.PHONY: init smoketest test typecheck docs

## Run once after cloning: rename all placeholders interactively.
init:
	@bash scripts/init.sh

## Verify the skeleton works end-to-end (install → test → typecheck).
smoketest:
	uv sync --extra dev
	uv run pytest
	uv run pyright

## Run the test suite.
test:
	uv run pytest -v tests/

## Run the type checker.
typecheck:
	uv run pyright

## Build the documentation locally.
docs:
	uv run sphinx-build -W --keep-going docs docs/_build/html
	@echo "Docs built → docs/_build/html/index.html"
