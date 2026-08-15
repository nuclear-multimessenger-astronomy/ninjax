"""Neutron star families from jester parameters or from a tabulated EOS."""

from __future__ import annotations

import os

import jax.numpy as jnp
import numpy as np
from jax import Array
from jax.typing import ArrayLike
from jesterTOV import utils as jester_utils
from jesterTOV.eos.metamodel import MetaModel_with_CSE_EOS_model
from jesterTOV.tov.data_classes import FamilyData
from jesterTOV.tov.gr import GRTOVSolver


EOSLike = str | os.PathLike[str] | dict[str, float] | FamilyData


def family_from_nep(
    params: dict[str, float],
    *,
    nb_CSE: int = 8,
    ndat_metamodel: int = 100,
    ndat_CSE: int = 100,
    ndat: int = 100,
    min_nsat: float = 2.0,
) -> FamilyData:
    """Solve the TOV equations for a metamodel+CSE EOS.

    Expects the nuclear empirical parameters ``E_sat, K_sat, Q_sat, Z_sat, E_sym,
    L_sym, K_sym, Q_sym, Z_sym`` plus ``nbreak``, ``n_CSE_{i}_u`` and ``cs2_CSE_{i}``.
    """
    model = MetaModel_with_CSE_EOS_model(
        nb_CSE=nb_CSE,
        ndat_metamodel=ndat_metamodel,
        ndat_CSE=ndat_CSE,
    )
    eos_data = model.construct_eos(params)
    return GRTOVSolver().construct_family(eos_data, ndat, min_nsat)


def family_from_table(path: str | os.PathLike[str], *, ndat: int = 100) -> FamilyData:
    """Load a macroscopic EOS table with columns ``(R [km], M [M_sun], Lambda)``.

    Follows nmma's ``--eos-file`` convention. The unstable branch above the maximum
    mass is dropped and the result is regridded onto a uniform mass axis, so the
    output matches what :func:`family_from_nep` produces.
    """
    radii, masses, lambdas = np.loadtxt(path, usecols=(0, 1, 2)).T
    _, masses, radii, lambdas = jester_utils.limit_by_MTOV(
        jnp.zeros_like(masses),
        jnp.asarray(masses),
        jnp.asarray(radii),
        jnp.asarray(lambdas),
    )
    mass_grid = jnp.linspace(jnp.min(masses), jnp.max(masses), ndat)
    return FamilyData(
        log10pcs=jnp.full((ndat,), jnp.nan),
        masses=mass_grid,
        radii=jnp.interp(mass_grid, masses, radii),
        lambdas=jnp.interp(mass_grid, masses, lambdas),
    )


def resolve_family(eos: EOSLike) -> FamilyData:
    """Build a :class:`FamilyData` from a table path, a parameter dict, or itself."""
    if isinstance(eos, FamilyData):
        return eos
    if isinstance(eos, dict):
        return family_from_nep(eos)
    return family_from_table(eos)


def lambda_of_mass(family: FamilyData, mass: ArrayLike) -> Array:
    """Tidal deformability at a given mass, zero above the maximum mass."""
    log_lambda = jnp.interp(
        mass, family.masses, jnp.log(family.lambdas), left=-jnp.inf, right=-jnp.inf
    )
    return jnp.exp(log_lambda)


def radius_of_mass(family: FamilyData, mass: ArrayLike) -> Array:
    """Radius in km at a given mass, zero above the maximum mass."""
    return jnp.interp(mass, family.masses, family.radii, left=0.0, right=0.0)


def tov_mass(family: FamilyData) -> Array:
    """Maximum non-rotating mass in solar masses."""
    return jnp.max(family.masses)
