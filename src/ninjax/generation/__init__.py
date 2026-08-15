"""Generate GW and EM signals for binary neutron stars."""

from ninjax.generation.ejecta import (
    GEOM_MSUN_KM,
    binary_to_ejecta,
    dynamic_mass_KrFo,
    log10_disk_mass,
)
from ninjax.generation.em import em_lightcurve
from ninjax.generation.eos import (
    family_from_nep,
    family_from_table,
    lambda_of_mass,
    radius_of_mass,
    resolve_family,
    tov_mass,
)
from ninjax.generation.generate import generate_signals, sample_parameters
from ninjax.generation.gw import gw_polarizations, gw_strain, to_jim_params


__all__ = [
    "GEOM_MSUN_KM",
    "binary_to_ejecta",
    "dynamic_mass_KrFo",
    "em_lightcurve",
    "family_from_nep",
    "family_from_table",
    "generate_signals",
    "gw_polarizations",
    "gw_strain",
    "lambda_of_mass",
    "log10_disk_mass",
    "radius_of_mass",
    "resolve_family",
    "sample_parameters",
    "to_jim_params",
    "tov_mass",
]
