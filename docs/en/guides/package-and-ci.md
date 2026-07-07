[한국어 (Korean)](../../ko/guides/package-and-ci.md)

> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.0.1"`.

# Package and CI Guide

This guide explains the local `pyproject.toml` setup and the optional Python compatibility CI workflow.

## Local Editable Install

Use editable install when you want local imports to behave like an installed package while still editing the checkout.

```bash
python -m pip install -e ".[test]"
```

Then run the tests.

```bash
pytest -q
```

## What `pyproject.toml` Does

`pyproject.toml` is the standard package metadata entry point for modern Python tooling.

In this repository it defines:

- `setuptools` as the build backend.
- package metadata such as name, version, README, license, and `requires-python`.
- `typing-extensions` for Python versions older than 3.10.
- the optional `test` dependency group.
- package discovery for `tbot223_base`.
- inclusion of `py.typed` for type-aware tooling.
- pytest's default `tests` path.

## Optional Compatibility CI

The workflow at `.github/workflows/python-compatibility.yml` is manual-only. It runs when someone chooses it from the GitHub Actions UI.

The current matrix is:

- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13
- Python 3.14

Each job installs the package with test dependencies and runs:

```bash
pytest -q
```

## When To Run It

Run the optional compatibility workflow before release-like checkpoints, public API changes, payload contract changes, or Python support range changes.

For small local-only edits, `pytest -q` in the current checkout is usually enough.
