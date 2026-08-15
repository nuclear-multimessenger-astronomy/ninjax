[![CI](https://github.com/nuclear-multimessenger-astronomy/ninjax/actions/workflows/ci.yml/badge.svg)](https://github.com/nuclear-multimessenger-astronomy/ninjax/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://nuclear-multimessenger-astronomy.github.io/ninjax/)

# ninjax

*Joint multi-messenger parameter estimation in JAX*

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

## For developers

All development guidelines - including how to run tests, contribute code, and write
documentation - are in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Citing

If you use `ninjax` in your work, please cite the relevant paper(s), including those
for `nmma`, `jim`, `fiesta`, and `jester`.

See [`CITATION.cff`](CITATION.cff) or the [citing page in the documentation](https://nuclear-multimessenger-astronomy.github.io/ninjax/citing.html)
for the full list of references.
