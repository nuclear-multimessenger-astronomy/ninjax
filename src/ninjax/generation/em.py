"""Electromagnetic light curves from a fiesta surrogate."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import jax
import jax.numpy as jnp
from jax import Array
from jaxtyping import Key


def em_lightcurve(
    params: Mapping[str, Any],
    model: Any,
    *,
    error_budget: float | None = None,
    detection_limit: float | None = None,
    rng_key: Key | None = None,
) -> dict[str, dict[str, Array]]:
    """Apparent AB magnitudes per filter from a fiesta surrogate.

    Returns the noiseless curve unless ``error_budget`` is given, in which case
    Gaussian scatter of that width is added. Points fainter than
    ``detection_limit`` are returned at the limit with an infinite error, which is
    how fiesta's ``EMLikelihood`` marks a non-detection.
    """
    times, mags = model.predict(dict(params))

    if error_budget is None:
        return {filt: {"time": times, "mag": mag} for filt, mag in mags.items()}

    key = jax.random.key(0) if rng_key is None else rng_key

    lightcurves = {}
    for filt, mag in mags.items():
        key, subkey = jax.random.split(key)
        mag = mag + error_budget * jax.random.normal(subkey, mag.shape)
        mag_err = jnp.full(mag.shape, error_budget)

        if detection_limit is not None:
            missed = mag > detection_limit
            mag = jnp.where(missed, detection_limit, mag)
            mag_err = jnp.where(missed, jnp.inf, mag_err)

        lightcurves[filt] = {"time": times, "mag": mag, "mag_err": mag_err}
    return lightcurves
