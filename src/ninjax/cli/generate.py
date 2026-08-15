"""``ninjax-generate``: build GW and EM signals for a population of binaries."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any, Literal, NoReturn

import pandas as pd
import tyro
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


# Columns generate_signals derives itself, so a surrogate may ask for them even
# though the input table does not supply them.
DERIVED_COLUMNS = frozenset(
    {
        "redshift",
        "inclination_EM",
        "mass_1_source",
        "mass_2_source",
        "lambda_1",
        "lambda_2",
        "radius_1",
        "radius_2",
        "compactness_1",
        "compactness_2",
        "log10_mej_dyn",
        "log10_mej_wind",
        "log10_mej",
        "log10_mdisk",
        "t_c",
    }
)


class BaseConfig(BaseModel):
    """Shared validation policy for every config section."""

    model_config = ConfigDict(extra="forbid", validate_default=True)


class GWConfig(BaseConfig):
    """Gravitational-wave output."""

    mode: Literal["polarizations", "strain", "none"] = Field(
        default="polarizations",
        description="Waveform polarizations, detector strain, or no GW output.",
    )
    f_min: float = Field(default=20.0, description="Lower frequency bound in Hz.")
    f_max: float = Field(default=1024.0, description="Upper frequency bound in Hz.")
    delta_f: float = Field(
        default=0.25, description="Frequency spacing in Hz, used by mode=polarizations."
    )
    f_ref: float = Field(
        default=20.0, description="Waveform reference frequency in Hz."
    )
    detectors: tuple[str, ...] = Field(
        default=("H1", "L1", "V1"), description="Detector names, used by mode=strain."
    )
    duration: float = Field(default=128.0, description="Segment duration in seconds.")
    sampling_frequency: float = Field(
        default=2048.0,
        description="Sampling frequency in Hz for the injected segment.",
    )
    psd_files: tuple[Path, ...] | None = Field(
        default=None, description="One PSD file per detector, in the same order."
    )
    asd_files: tuple[Path, ...] | None = Field(
        default=None, description="One ASD file per detector, in the same order."
    )
    zero_noise: bool = Field(
        default=False, description="Inject the signal without adding detector noise."
    )

    @model_validator(mode="after")
    def _check_grid(self) -> GWConfig:
        if self.f_max <= self.f_min:
            raise ValueError(f"f-max ({self.f_max}) must exceed f-min ({self.f_min})")
        if self.delta_f <= 0:
            raise ValueError(f"delta-f must be positive, got {self.delta_f}")
        for name, files in (
            ("psd-files", self.psd_files),
            ("asd-files", self.asd_files),
        ):
            if files is not None and len(files) != len(self.detectors):
                raise ValueError(
                    f"{name} has {len(files)} entries but there are "
                    f"{len(self.detectors)} detectors"
                )
        return self


class EMConfig(BaseConfig):
    """Electromagnetic output, disabled unless a surrogate is named."""

    model_name: str | None = Field(
        default=None, description="fiesta surrogate to run, for example Bu2025_MLP."
    )
    model_type: Literal[
        "BullaFlux",
        "BullaLightcurveModel",
        "LightcurveModel",
        "FluxModel",
        "AfterglowFlux",
    ] = Field(
        default="BullaFlux",
        description="fiesta surrogate class to load the model with.",
    )
    filters: tuple[str, ...] = Field(
        default=("ztfg", "ztfr"), description="Photometric filters to predict."
    )
    model_dir: Path | None = Field(
        default=None,
        description="Directory holding the surrogate weights. "
        "Omit to download them from HuggingFace on first use.",
    )
    error_budget: float | None = Field(
        default=None,
        description="Gaussian scatter in magnitudes. Omit for a noiseless light curve.",
    )
    detection_limit: float | None = Field(
        default=None,
        description="Limiting magnitude. Fainter points are recorded as "
        "non-detections with infinite error.",
    )


class GenerateConfig(BaseConfig):
    """Generate gravitational-wave and kilonova signals for binary neutron stars.

    Binary parameters come either from a table (--params-file) or by sampling a
    jim prior (--prior-file). Tidal deformabilities, radii and ejecta masses are
    derived from the equation of state given by --eos.
    """

    eos: Path = Field(
        description="Equation of state. A .json or .toml file is read as jester "
        "nuclear empirical parameters; anything else as a macroscopic table with "
        "columns (R [km], M [M_sun], Lambda)."
    )
    outdir: Path = Field(description="Directory to write the generated signals into.")
    params_file: Path | None = Field(
        default=None, description="CSV table of binary parameters, one row per binary."
    )
    prior_file: Path | None = Field(
        default=None,
        description="TOML file with a [prior] table to sample, as used by jim-run.",
    )
    n_samples: int = Field(
        default=1, description="Number of binaries to draw, used with --prior-file."
    )
    seed: int = Field(default=0, description="Random seed for sampling and for noise.")
    fixed_params: Path | None = Field(
        default=None,
        description="JSON or TOML file of constant values applied to every binary, "
        "for parameters the prior or table does not supply.",
    )
    alpha: float = Field(
        default=0.0, description="Offset added to the dynamical ejecta mass."
    )
    ratio_zeta: float = Field(
        default=0.15,
        description="Fraction of the remnant disk that becomes wind ejecta.",
    )
    gw: GWConfig = Field(
        default_factory=lambda: GWConfig(), description="Gravitational-wave output."
    )
    em: EMConfig = Field(
        default_factory=lambda: EMConfig(), description="Electromagnetic output."
    )

    @model_validator(mode="after")
    def _check_inputs(self) -> GenerateConfig:
        if (self.params_file is None) == (self.prior_file is None):
            raise ValueError("set exactly one of --params-file or --prior-file")
        for path in (self.eos, self.params_file, self.prior_file, self.fixed_params):
            if path is not None and not path.exists():
                raise ValueError(f"file not found: {path}")
        return self


def fail(message: str) -> NoReturn:
    """Exit with a message instead of a traceback."""
    raise SystemExit(f"ninjax-generate: {message}")


def load_mapping(path: Path) -> dict[str, Any]:
    """Read a JSON or TOML file into a dict."""
    if path.suffix == ".toml":
        with path.open("rb") as stream:
            return tomllib.load(stream)
    with path.open() as stream:
        return json.load(stream)


def build_prior(path: Path) -> Any:
    """Build a jim prior from the ``[prior]`` table of a TOML file."""
    # jimgw.cli is private, but it already parses this exact format for jim-run.
    from jimgw.cli._config import PriorConfig
    from jimgw.cli._prior import build_prior as jim_build_prior

    spec = load_mapping(path).get("prior")
    if spec is None:
        fail(f"{path} has no [prior] table")
    return jim_build_prior(PriorConfig.model_validate(spec))


def build_table(config: GenerateConfig) -> pd.DataFrame:
    """Read or sample the binary parameters, then apply any fixed values."""
    import jax

    from ninjax.generation import sample_parameters

    if config.params_file is not None:
        table = pd.read_csv(config.params_file)
    elif config.prior_file is not None:
        prior = build_prior(config.prior_file)
        table = sample_parameters(prior, config.n_samples, jax.random.key(config.seed))
    else:
        raise ValueError("set exactly one of --params-file or --prior-file")

    if config.fixed_params is not None:
        for name, value in load_mapping(config.fixed_params).items():
            table[name] = value
    return table


def build_em_model(config: EMConfig) -> Any:
    """Load the named fiesta surrogate."""
    from fiesta.inference import lightcurve_model

    model_class = getattr(lightcurve_model, config.model_type)
    return model_class(
        config.model_name,
        filters=list(config.filters),
        directory=None if config.model_dir is None else str(config.model_dir),
    )


def check_em_parameters(model: Any, table: pd.DataFrame) -> None:
    """Fail early when the surrogate needs parameters nothing supplies."""
    missing = [
        name
        for name in model.parameter_names
        if name not in table.columns and name not in DERIVED_COLUMNS
    ]
    if missing:
        fail(
            f"surrogate {model.name} needs parameters that are not in the table "
            f"and are not derived: {missing}. Supply them with --fixed-params, "
            "as table columns, or in the prior."
        )


def gw_kwargs(config: GWConfig) -> dict[str, Any]:
    """Translate the GW section into keyword arguments for ``gw_strain``."""

    def paired(files: tuple[Path, ...] | None) -> dict[str, str] | None:
        if files is None:
            return None
        return {
            name: str(path) for name, path in zip(config.detectors, files, strict=True)
        }

    return {
        "detectors": list(config.detectors),
        "duration": config.duration,
        "sampling_frequency": config.sampling_frequency,
        "f_min": config.f_min,
        "f_max": config.f_max,
        "f_ref": config.f_ref,
        "zero_noise": config.zero_noise,
        "psd_files": paired(config.psd_files),
        "asd_files": paired(config.asd_files),
    }


def write_parameters(records: list[dict[str, Any]], outdir: Path) -> Path:
    """Write every derived parameter for every binary to ``parameters.csv``."""
    import numpy as np

    rows = [
        {name: np.asarray(value).item() for name, value in record["parameters"].items()}
        for record in records
    ]
    path = outdir / "parameters.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def main() -> None:
    # tyro renders errors from the nested sections itself, but a failure in the
    # top-level model escapes as a raw traceback unless caught here.
    try:
        config = tyro.cli(GenerateConfig)
    except ValidationError as error:
        fail(
            "; ".join(
                item["msg"].removeprefix("Value error, ") for item in error.errors()
            )
        )

    # jimgw raises at import time when float64 is off, so this has to come first.
    import jax

    jax.config.update("jax_enable_x64", True)

    import jax.numpy as jnp

    from ninjax.generation import generate_signals

    table = build_table(config)

    em_model = None
    if config.em.model_name is not None:
        em_model = build_em_model(config.em)
        check_em_parameters(em_model, table)

    frequencies = None
    if config.gw.mode == "polarizations":
        frequencies = jnp.arange(config.gw.f_min, config.gw.f_max, config.gw.delta_f)

    eos = config.eos
    config.outdir.mkdir(parents=True, exist_ok=True)
    records = generate_signals(
        table,
        load_mapping(eos) if eos.suffix in (".json", ".toml") else eos,
        rng_key=jax.random.key(config.seed),
        gw_mode=config.gw.mode,
        frequencies=frequencies,
        gw_kwargs=gw_kwargs(config.gw),
        em_model=em_model,
        error_budget=config.em.error_budget,
        detection_limit=config.em.detection_limit,
        alpha=config.alpha,
        ratio_zeta=config.ratio_zeta,
        outdir=config.outdir,
    )

    write_parameters(records, config.outdir)
    print(f"Wrote {len(records)} injection(s) to {config.outdir}")
