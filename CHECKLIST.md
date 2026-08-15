# New Package Checklist

Steps to follow every time you start a new package from this template.

---

## 1. Initialize the template

```bash
make init
```

Renames all `package_name` / `YOUR_ORG` / `YOUR_NAME` placeholders in one pass. Run this before doing anything else.

---

## 2. Smoke-test the skeleton

```bash
make smoketest
```

Installs the package, runs tests, and type-checks. Everything should pass before you write a line of actual code.

---

## 3. Fill in the blanks

- [ ] `pyproject.toml` — add runtime `dependencies`
- [ ] `pyproject.toml` — update `keywords` and `classifiers`
- [ ] `README.md` — write the tagline and feature table
- [ ] `CITATION.cff` — add DOI / paper details once published
- [ ] `docs/conf.py` — verify `project`, `author`, `release` fields
- [ ] `docs/index.rst` — flesh out the landing page
- [ ] `docs/_static/` — replace the placeholder SVG logos
- [ ] `LICENSE` — confirm the year is current
- [ ] `.python-version` — pin to the Python version you'll develop against

---

## 4. GitHub repository setup

- [ ] Enable **GitHub Pages** (Settings → Pages → Source: GitHub Actions)
- [ ] Mark repo as a **template** if you want to reuse it again (Settings → Template repository)
- [ ] Add repository secrets if needed:
  - `CODECOV_TOKEN` — for coverage reporting
  - `ANTHROPIC_API_KEY` — for Claude Code review workflow
- [ ] Update `.github/CODEOWNERS` with your GitHub username (if `make init` didn't already)

---

## 5. Pre-commit hooks

```bash
uv run pre-commit install
uv run pre-commit run --all-files   # verify clean on first run
```

---

## 6. First real commit

```bash
git add -A
git commit -m "chore: initialize from package-template"
git push -u origin main
```

Check that CI goes green before adding any substantive code.

---

## 7. Ongoing

- Write tests *before* (or alongside) new features — see `CONTRIBUTING.md`.
- Keep `CITATION.cff` updated when papers are published.
- Bump the version in `pyproject.toml` and `src/<package>/__init__.py` before each release.
