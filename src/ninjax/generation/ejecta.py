"""Ejecta parameters from binary masses and a neutron star family.

Ports the BNS fitting formulas used by nmma's ``BNSEjectaFitting``.
"""

from __future__ import annotations

from typing import Any

import jax.numpy as jnp
from jax import Array
from jax.typing import ArrayLike
from jesterTOV.tov.data_classes import FamilyData

from ninjax.generation.eos import lambda_of_mass, radius_of_mass, tov_mass


GEOM_MSUN_KM = 1.476625038050125
"""Geometrised solar mass in km."""


def dynamic_mass_KrFo(
    mass_1: ArrayLike,
    mass_2: ArrayLike,
    compactness_1: ArrayLike,
    compactness_2: ArrayLike,
    a: float = -9.3335,
    b: float = 114.17,
    c: float = -337.56,
    n: float = 1.5465,
) -> Array:
    r"""Dynamical ejecta mass in solar masses, from arXiv:2002.07728.

    .. math::
        m_{\rm dyn} = 10^{-3} \sum_{i \neq j} m_i
        \left( \frac{a}{C_i} + b \left(\frac{m_j}{m_i}\right)^n + c\, C_i \right)
    """
    mdyn = mass_1 * (
        a / compactness_1 + b * jnp.power(mass_2 / mass_1, n) + c * compactness_1
    )
    mdyn += mass_2 * (
        a / compactness_2 + b * jnp.power(mass_1 / mass_2, n) + c * compactness_2
    )
    return jnp.maximum(0.0, 1e-3 * mdyn)


def log10_disk_mass(
    total_mass: ArrayLike,
    mass_ratio: ArrayLike,
    mtov: ArrayLike,
    r16_geom: ArrayLike,
    a0: float = -1.725,
    delta_a: float = -2.337,
    b0: float = -0.564,
    delta_b: float = -0.437,
    c: float = 0.958,
    d: float = 0.057,
    beta: float = 5.879,
    q_trans: float = 0.886,
) -> Array:
    r"""Base-10 log of the remnant disk mass, from arXiv:2205.08513 Eq. (22).

    The threshold mass follows arXiv:1908.05442. ``r16_geom`` is :math:`R_{1.6}`
    in geometrised solar masses, i.e. the radius in km divided by
    :data:`GEOM_MSUN_KM`.
    """
    threshold_mass = (-3.606 * mtov / r16_geom + 2.38) * mtov
    xi = 0.5 * jnp.tanh(beta * (mass_ratio - q_trans))
    a = a0 + delta_a * xi
    b = b0 + delta_b * xi

    log10_mdisk = a * (1 + b * jnp.tanh((c - total_mass / threshold_mass) / d))
    return jnp.maximum(-3.0, log10_mdisk)


def binary_to_ejecta(
    mass_1_source: ArrayLike,
    mass_2_source: ArrayLike,
    family: FamilyData,
    *,
    alpha: float = 0.0,
    ratio_zeta: float = 0.15,
) -> dict[str, Any]:
    """Tidal, radius and ejecta parameters for one binary.

    ``alpha`` offsets the dynamical ejecta and ``ratio_zeta`` is the fraction of
    the disk that becomes wind ejecta; both are free parameters in nmma.
    """
    lambda_1 = lambda_of_mass(family, mass_1_source)
    lambda_2 = lambda_of_mass(family, mass_2_source)
    radius_1 = radius_of_mass(family, mass_1_source)
    radius_2 = radius_of_mass(family, mass_2_source)

    compactness_1 = mass_1_source * GEOM_MSUN_KM / radius_1
    compactness_2 = mass_2_source * GEOM_MSUN_KM / radius_2

    mdyn = dynamic_mass_KrFo(mass_1_source, mass_2_source, compactness_1, compactness_2)
    log10_mdisk = log10_disk_mass(
        mass_1_source + mass_2_source,
        mass_2_source / mass_1_source,
        tov_mass(family),
        radius_of_mass(family, 1.6) / GEOM_MSUN_KM,
    )

    log10_mej_dyn = jnp.log10(mdyn + alpha)
    log10_mej_wind = jnp.log10(ratio_zeta) + log10_mdisk

    return {
        "lambda_1": lambda_1,
        "lambda_2": lambda_2,
        "radius_1": radius_1,
        "radius_2": radius_2,
        "compactness_1": compactness_1,
        "compactness_2": compactness_2,
        "log10_mej_dyn": log10_mej_dyn,
        "log10_mej_wind": log10_mej_wind,
        "log10_mej": jnp.log10(10**log10_mej_dyn + 10**log10_mej_wind),
        "log10_mdisk": log10_mdisk,
    }
