[한국어 (Korean)](../../ko/guides/package-and-ci.md)

> Runtime baseline: unreleased working tree based on `1.0.0a1`; these fixes are not part of the existing release tag.

# Package and CI Guide

This guide covers the rebuilding alpha's local package tools, compatibility workflow, and prerelease-only publish gate. It does not authorize publication; read [Rebuilding](../rebuilding.md) first.

## Local Development

```bash
python -m pip install -e ".[test,type,lint,release]"
npm ci
pytest -q
python -m mypy
python scripts/check-rejected-types.py
python -m ruff check .
python -m ruff format --check .
python scripts/check-docstring-contract.py
npx --no-install markdownlint-cli2 "**/*.md" "#node_modules"
```

The package has no runtime dependencies. The `test`, `type`, `lint`, and `release` extras support local verification. Ruff and Markdownlint are development-only and are not part of the Python package.

## Release Readiness

Run the complete local gate with the exact alpha tag text.

```bash
scripts/check-release-readiness.sh v1.0.0a1
```

Strict mode additionally requires the tag to point at `HEAD`, a clean worktree, and a locally available `origin/main`.

```bash
scripts/check-release-readiness.sh --strict-release v1.0.0a1
```

Accepted tags are stable `vMAJOR.MINOR.PATCH`, alpha `vMAJOR.MINOR.PATCHaN`, and release-candidate `vMAJOR.MINOR.PATCHrcN`. Their text after the leading `v` must exactly match `tbot223_base.__version__`.

The script runs Python compile checks, pytest plus deterministic docstring doctests, AST docstring-contract validation, positive and negative mypy checks, Ruff linting and format checks, Markdownlint, actionlint, diff whitespace checks, source/wheel build, `twine check`, distribution inspection, and isolated-wheel smoke tests.

## Docker Checks

```bash
docker compose run --build --rm test
docker compose run --build --rm check
```

The `check` image installs `actionlint`, Ruff, and the development-only Markdownlint CLI, then runs the complete `v1.0.0a1` readiness check.

## Compatibility CI

`.github/workflows/python-compatibility.yml` runs on push, pull request, manual dispatch, and reusable-workflow invocation for Python 3.10 through 3.14. It validates pytest, public consumer typing, each annotated invalid consumer line and expected mypy error code, Ruff linting and formatting, the docstring contract, and Markdownlint. Ubuntu runs Python 3.10–3.14; Windows and macOS additionally run Python 3.12. A separate required workflow job runs actionlint.

## Publish Workflow

`.github/workflows/publish.yml` starts only when a GitHub Release is published. It requires a version-matching tag on `main`, the compatibility workflow, build and wheel checks, and PyPI Trusted Publishing.

Alpha and release-candidate tags must use GitHub's prerelease option. Stable tags must not. `1.0.0a1` remains a rebuilding alpha: do not create a release or publish a distribution until the project explicitly approves that step.

## Source Archive Verification

The sdist includes Python validation scripts, Node manifests and lockfile, Markdownlint configuration, and workflow files. After installing the documented development tools and running `npm ci`, its non-strict readiness script can run without Git metadata. Strict mode requires a real Git checkout, the matching tag, and a clean worktree; a source archive cannot establish release provenance.
