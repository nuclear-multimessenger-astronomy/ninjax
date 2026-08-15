"""Driver turning a table of binary properties into GW and EM signals."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import jax
import jax.numpy as jnp
import numpy as np
import pandas as pd
from astropy import units
from astropy.cosmology import Planck18, z_at_value
from astropy.time import Time
from fiesta.utils import write_event_data
from jax import Array
from jaxtyping import Key
from jimgw.core.prior import Prior
from jimgw.core.single_event.transform_utils import Mc_eta_to_m1_m2, Mc_q_to_m1_m2

from ninjax.generation.ejecta import binary_to_ejecta
from ninjax.generation.em import em_lightcurve
from ninjax.generation.eos import EOSLike, resolve_family
from ninjax.generation.gw import gw_polarizations, gw_strain, to_jim_params


# astropy exports its realizations lazily, so Planck18 carries no usable static type
COSMOLOGY: Any = Planck18

REQUIRED_COLUMNS = (
    "luminosity_distance",
    "ra",
    "dec",
    "psi",
    "theta_jn",
    "phase",
    "geocent_time",
    "chi_1",
    "chi_2",
)


def sample_parameters(prior: Prior, n_samples: int, rng_key: Key) -> pd.DataFrame:
    """Draw ``n_samples`` from a jim prior into a table."""
    samples = prior.sample(rng_key, n_samples)
    return pd.DataFrame({name: np.asarray(v) for name, v in samples.items()})


def _to_table(
    source: pd.DataFrame | Prior, n_samples: int, rng_key: Key | None
) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        table = source.copy()
    elif rng_key is None:
        raise ValueError("rng_key is required when sampling from a prior")
    else:
        table = sample_parameters(source, n_samples, rng_key)

    if "mass_1" not in table:
        if "M_c" not in table:
            raise ValueError("need either mass_1/mass_2 or M_c with q or eta")
        M_c = jnp.asarray(table["M_c"].to_numpy())
        if "q" in table:
            mass_1, mass_2 = Mc_q_to_m1_m2(M_c, jnp.asarray(table["q"].to_numpy()))
        else:
            mass_1, mass_2 = Mc_eta_to_m1_m2(M_c, jnp.asarray(table["eta"].to_numpy()))
        table["mass_1"] = np.asarray(mass_1)
        table["mass_2"] = np.asarray(mass_2)

    missing = [name for name in REQUIRED_COLUMNS if name not in table]
    if missing:
        raise ValueError(f"table is missing required columns: {missing}")
    return table


def _redshift(params: Mapping[str, Any]) -> float:
    if "redshift" in params:
        return float(params["redshift"])
    distance = float(params["luminosity_distance"]) * units.Mpc
    return float(z_at_value(COSMOLOGY.luminosity_distance, distance))


def _flatten(obj: Mapping[str, Any], prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    for key, value in obj.items():
        if isinstance(value, Mapping):
            flat.update(_flatten(value, f"{prefix}{key}_"))
        else:
            flat[f"{prefix}{key}"] = np.asarray(value)
    return flat


def _write_record(
    outdir: Path, index: int, record: Mapping[str, Any], params: Mapping[str, Any]
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    if record.get("em"):
        mjd = Time(float(params["geocent_time"]), format="gps").mjd
        data = {
            filt: np.column_stack(
                [
                    mjd + np.asarray(lightcurve["time"]),
                    np.asarray(lightcurve["mag"]),
                    np.asarray(lightcurve.get("mag_err", 0.0))
                    * np.ones_like(lightcurve["mag"]),
                ]
            )
            for filt, lightcurve in record["em"].items()
        }
        write_event_data(str(outdir / f"{index}_em.dat"), data)

    if record.get("gw"):
        np.savez(outdir / f"{index}_gw.npz", **_flatten(record["gw"]))


def generate_signals(
    source: pd.DataFrame | Prior,
    eos: EOSLike,
    *,
    n_samples: int = 1,
    rng_key: Key | None = None,
    gw_mode: Literal["polarizations", "strain", "none"] = "polarizations",
    frequencies: Array | None = None,
    gw_kwargs: Mapping[str, Any] | None = None,
    em_model: Any = None,
    error_budget: float | None = None,
    detection_limit: float | None = None,
    alpha: float = 0.0,
    ratio_zeta: float = 0.15,
    outdir: str | os.PathLike[str] | None = None,
) -> list[dict[str, Any]]:
    """Generate GW and EM signals for every binary in ``source``.

    ``source`` is either a table of binary properties or a jim prior to sample.
    ``eos`` is a macroscopic table path, a dict of jester parameters, or a
    ready-made family. ``gw_kwargs`` is forwarded to :func:`gw_strain`, which
    needs at least ``duration`` and ``sampling_frequency``.
    """
    table = _to_table(source, n_samples, rng_key)
    family = resolve_family(eos)
    gw_opts = dict(gw_kwargs or {})
    base_key = jax.random.key(0) if rng_key is None else rng_key

    records = []
    for index, row in enumerate(table.to_dict(orient="records")):
        params: dict[str, Any] = dict(row)
        key = jax.random.fold_in(base_key, index)

        redshift = _redshift(params)
        params["redshift"] = redshift
        params.setdefault(
            "inclination_EM", min(params["theta_jn"], np.pi - params["theta_jn"])
        )
        params["mass_1_source"] = params["mass_1"] / (1 + redshift)
        params["mass_2_source"] = params["mass_2"] / (1 + redshift)
        params.update(
            binary_to_ejecta(
                params["mass_1_source"],
                params["mass_2_source"],
                family,
                alpha=params.get("alpha", alpha),
                ratio_zeta=params.get("ratio_zeta", ratio_zeta),
            )
        )

        trigger_time = float(gw_opts.get("trigger_time", params["geocent_time"]))
        params["t_c"] = float(params["geocent_time"]) - trigger_time

        record: dict[str, Any] = {"parameters": params}
        if gw_mode != "none":
            jim_params = to_jim_params(params)
            if gw_mode == "polarizations":
                if frequencies is None:
                    raise ValueError("gw_mode='polarizations' needs frequencies")
                record["gw"] = gw_polarizations(jim_params, frequencies)
            else:
                record["gw"] = gw_strain(
                    jim_params,
                    rng_key=key,
                    **{**gw_opts, "trigger_time": trigger_time},
                )

        if em_model is not None:
            record["em"] = em_lightcurve(
                params,
                em_model,
                error_budget=error_budget,
                detection_limit=detection_limit,
                rng_key=key,
            )

        if outdir is not None:
            _write_record(Path(outdir), index, record, params)
        records.append(record)

    return records
