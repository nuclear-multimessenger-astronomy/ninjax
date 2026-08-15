# CLAUDE.md

This file provides guidance to Claude Code when working with the documentation in this repository.

## Style

When writing long-form documentation, use full sentences and not a list of bullet points with short sentences. Make it easy to read and clear for new users.

## Building Documentation

```bash
# Build documentation locally
uv run sphinx-build docs docs/_build/html

# Build with auto-reload
uv run sphinx-autobuild docs docs/_build/html
# Then visit http://127.0.0.1:8000

# Strict mode (same as CI/CD - fails on warnings)
uv run sphinx-build -W --keep-going docs docs/_build/html
```

**Always test in strict mode before committing** — CI/CD will fail if there are any warnings.

## Documentation Architecture

```
docs/
├── index.rst                 # Main entry point
├── conf.py                   # Sphinx configuration
├── api/                      # API reference (.rst files, auto-generated from docstrings)
├── developer_guide/          # Developer documentation
├── examples/                 # Jupyter notebook examples
├── _static/                  # CSS, logos, assets
└── _templates/               # Sphinx templates
```

## Sphinx Configuration Notes

- **HTML Theme**: `sphinx_book_theme`
- **Custom CSS**: `_static/style.css`
- **Logo**: `_static/logo_light.svg` (light mode), `_static/logo_dark.svg` (dark mode)
- **Favicon**: `_static/icon.svg`

## Math in Docstrings

Always use reStructuredText math formatting:

```python
def my_function(x: float) -> float:
    r"""Compute something.

    The formula is :math:`f(x) = x^2`.

    For display math:

    .. math::
        f(x) = x^2

    Args:
        x: Input value
    """
```

## Common Pitfalls

- Use raw strings `r"""` for docstrings with LaTeX
- Use `.. autosummary::` with `:toctree: _autosummary/` for API reference pages, not `.. automodule::`
- Every warning is an error in CI (`-W` flag)
