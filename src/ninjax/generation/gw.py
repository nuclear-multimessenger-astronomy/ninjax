"""Gravitational-wave signals for a binary neutron star."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from jax import Array
from jaxtyping import Key
from jimgw.core.single_event.detector import GroundBased2G, get_detector_preset
from jimgw.core.single_event.transform_utils import m1_m2_to_Mc_eta
from jimgw.core.single_event.waveform import RippleIMRPhenomD_NRTidalv2


def to_jim_params(params: Mapping[str, Any]) -> dict[str, Any]:
    """Map table columns onto the names jim's tidal waveform and detectors expect."""
    M_c, eta = m1_m2_to_Mc_eta(params["mass_1"], params["mass_2"])
    return {
        "M_c": M_c,
        "eta": eta,
        "s1_z": params["chi_1"],
        "s2_z": params["chi_2"],
        "lambda_1": params["lambda_1"],
        "lambda_2": params["lambda_2"],
        "d_L": params["luminosity_distance"],
        "phase_c": params["phase"],
        # exact for the aligned-spin waveform used here
        "iota": params["theta_jn"],
        "ra": params["ra"],
        "dec": params["dec"],
        "psi": params["psi"],
        "t_c": params["t_c"],
    }


def _detector_instances(names: Sequence[str]) -> list[GroundBased2G]:
    preset = get_detector_preset()
    instances = []
    for name in names:
        entry = preset[name]
        instances.extend(entry if isinstance(entry, list) else [entry])
    return instances


def gw_polarizations(
    params: Mapping[str, Any],
    frequencies: Array,
    *,
    f_ref: float = 20.0,
) -> dict[str, Array]:
    """Plus and cross polarizations on a frequency grid, keyed ``"p"`` and ``"c"``."""
    waveform = RippleIMRPhenomD_NRTidalv2(f_ref=f_ref)
    return waveform(frequencies, params)


def gw_strain(
    params: Mapping[str, Any],
    *,
    detectors: Sequence[str] = ("H1", "L1", "V1"),
    duration: float,
    sampling_frequency: float,
    trigger_time: float,
    f_min: float = 20.0,
    f_max: float = 1024.0,
    f_ref: float = 20.0,
    psd_files: Mapping[str, str] | None = None,
    asd_files: Mapping[str, str] | None = None,
    zero_noise: bool = False,
    rng_key: Key | None = None,
) -> dict[str, dict[str, Any]]:
    """Project the waveform onto each detector and add coloured Gaussian noise.

    Without ``psd_files`` or ``asd_files`` jim downloads the GWTC-2 ASD, which
    needs network access and only covers H1, L1 and V1. Results are keyed by
    detector name, so ``"ET"`` expands to its three components.
    """
    waveform = RippleIMRPhenomD_NRTidalv2(f_ref=f_ref)

    signals = {}
    for ifo in _detector_instances(detectors):
        ifo.load_and_set_psd(
            psd_file=(psd_files or {}).get(ifo.name, ""),
            asd_file=(asd_files or {}).get(ifo.name, ""),
        )
        ifo.inject_signal(
            duration=duration,
            sampling_frequency=sampling_frequency,
            trigger_time=trigger_time,
            waveform_model=waveform,
            parameters=dict(params),
            f_min=f_min,
            f_max=f_max,
            zero_noise=zero_noise,
            rng_key=rng_key,
        )
        signals[ifo.name] = {
            "frequencies": ifo.sliced_frequencies,
            "strain": ifo.sliced_fd_data,
            "psd": ifo.sliced_psd,
            "optimal_snr": ifo.optimal_snr,
            "match_filtered_snr": ifo.match_filtered_snr,
        }
    return signals
