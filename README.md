<p align="center">
  <img src="docs/_static/logo.png" alt="ninjax logo" width="300">
</p>

<h1 align="center">ninjax</h1>

<p align="center">
  <em>Joint multi-messenger parameter estimation in JAX</em>
</p>

<p align="center">
  <a href="https://github.com/nuclear-multimessenger-astronomy/ninjax/actions/workflows/ci.yml"><img src="https://github.com/nuclear-multimessenger-astronomy/ninjax/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://nuclear-multimessenger-astronomy.github.io/ninjax/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-blue" alt="Documentation"></a>
</p>

`ninjax` is a JAX reimplementation of [`nmma`](https://github.com/nuclear-multimessenger-astronomy/nmma).
It performs joint Bayesian inference over gravitational-wave, electromagnetic, and
nuclear equation-of-state data, combining a likelihood per messenger over one shared
set of parameters. Each messenger is handled by a dedicated JAX package, so `ninjax`
supplies the parameter conversions and the joint likelihood that tie them together.

> [!TIP]
> **The documentation is the best place to get started.**
> It covers installation, examples, and the API reference.
>
> **[Read the full documentation →](https://nuclear-multimessenger-astronomy.github.io/ninjax/)**

## What's in `ninjax`?

| Component | Description |
|---|---|
| **Gravitational waves** | Compact-binary inference via [`jim`](https://github.com/GW-JAX-Team/Jim) |
| **Electromagnetic** | Kilonova and afterglow light curves via [`fiesta`](https://github.com/nuclear-multimessenger-astronomy/fiestaEM) |
| **Equation of state** | Neutron-star EOS and TOV solutions via [`jester`](https://github.com/nuclear-multimessenger-astronomy/jester) |
| **Joint inference** | Parameter conversions and the combined likelihood across all three |

## Installation

Install the latest version by cloning the repository:

```bash
git clone https://github.com/nuclear-multimessenger-astronomy/ninjax
cd ninjax
uv sync
```

Extra dependencies can be installed as follows:
```bash
uv sync --extra dev    # For developers (run tests, build docs)
```

## Generating injections

Installing `ninjax` provides `ninjax-generate`, which turns a population of binary
neutron stars and an equation of state into the gravitational-wave and kilonova
signals they would produce. Tidal deformabilities, radii and ejecta masses are derived
from the equation of state, so only the binary parameters need to be supplied.

Binary parameters come from one of two places. Either a CSV table, one row per binary:

```bash
ninjax-generate --eos ALF2.dat --params-file binaries.csv --outdir injections
```

The table needs the columns `mass_1`, `mass_2` (or `M_c` with `q` or `eta`),
`luminosity_distance`, `ra`, `dec`, `psi`, `theta_jn`, `phase`, `geocent_time`,
`chi_1` and `chi_2`.

Or a prior to sample, written as a `[prior]` table in TOML using the same format as
`jim-run`:

```toml
# prior.toml
[prior]
mass_1              = { type = "uniform", min = 1.2, max = 1.6 }
mass_2              = { type = "uniform", min = 1.0, max = 1.2 }
luminosity_distance = { type = "power_law", min = 50.0, max = 200.0, alpha = 2.0 }
ra                  = { type = "uniform", min = 0.0, max = 6.283185307179586 }
dec                 = { type = "cosine" }
psi                 = { type = "uniform", min = 0.0, max = 3.141592653589793 }
theta_jn            = { type = "sine" }
phase               = { type = "uniform", min = 0.0, max = 6.283185307179586 }
geocent_time        = { type = "uniform", min = 1187008882.0, max = 1187008883.0 }
chi_1               = { type = "uniform", min = -0.05, max = 0.05 }
chi_2               = { type = "uniform", min = -0.05, max = 0.05 }
```

```bash
ninjax-generate --eos ALF2.dat --prior-file prior.toml --n-samples 100 \
                --outdir injections --seed 42
```

`--eos` accepts either a macroscopic table with columns `(R [km], M [M_sun], Lambda)`,
or a `.json`/`.toml` file of jester nuclear empirical parameters, in which case the TOV
equations are solved to build the family.

### Choosing the output

The gravitational-wave side produces waveform polarizations by default. Pass
`--gw.mode strain` to project the signal onto detectors and add coloured Gaussian
noise instead, or `--gw.mode none` to skip it:

```bash
ninjax-generate --eos ALF2.dat --params-file binaries.csv --outdir injections \
                --gw.mode strain --gw.detectors H1 L1 V1 \
                --gw.duration 64 --gw.sampling-frequency 2048
```

Without `--gw.psd-files` or `--gw.asd-files`, jim downloads the GWTC-2 ASD, which needs
network access and only covers H1, L1 and V1. When given, those files pair up with
`--gw.detectors` in order, so they cannot be combined with a name that stands for
several detectors at once (`ET` expands to `ET1`, `ET2` and `ET3`, and the results are
keyed by those names).

The electromagnetic side is off until a fiesta surrogate is named. Light curves are
noiseless unless `--em.error-budget` is set, and points fainter than
`--em.detection-limit` are recorded as non-detections:

```bash
ninjax-generate --eos ALF2.dat --params-file binaries.csv --outdir injections \
                --gw.mode none --fixed-params ejecta.json \
                --em.model-name Bu2025_MLP --em.filters ztfg ztfr \
                --em.error-budget 0.1 --em.detection-limit 22.0
```

Surrogate weights are downloaded from HuggingFace the first time a model is used,
unless `--em.model-dir` points at a local copy.

A kilonova surrogate needs ejecta parameters that neither the binary nor the equation
of state fixes, such as `v_ej_dyn` and `Ye_dyn`. Supply them as table columns, in the
prior, or as constants shared by every binary through `--fixed-params`:

```json
{"v_ej_dyn": 0.2, "Ye_dyn": 0.15, "v_ej_wind": 0.1, "Ye_wind": 0.3}
```

If any are missing, the command says which ones before doing any work.

### Output

```
injections/
├── parameters.csv   every input and derived parameter, one row per binary
├── 0_gw.npz         GW signal: polarizations, or strain and PSD per detector
└── 0_em.dat         photometry in fiesta's format, readable by load_event_data
```

Run `ninjax-generate --help` for the full list of options.

## For developers

All development guidelines - including how to run tests, contribute code, and write
documentation - are in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Citing

If you use `ninjax` in your work, please cite the relevant paper(s), including those
for `nmma`, `jim`, `fiesta`, and `jester`.

See [`CITATION.cff`](CITATION.cff) or the [citing page in the documentation](https://nuclear-multimessenger-astronomy.github.io/ninjax/citing.html)
for the full list of references.
