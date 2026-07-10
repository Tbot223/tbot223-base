[한국어 (Korean)](../../ko/guides/package-and-ci.md)

> Runtime baseline: package version 1.0.0rc1 (`tbot223_base.__version__ == "1.0.0rc1"`).

# Package and CI Guide

This guide explains the local `pyproject.toml` setup, the Python compatibility CI workflow, and the release-only publish workflow.

Release, CI, Docker, and repository maintenance commands live here instead of the root README so the public package README can stay focused on users.

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
- package metadata such as name, README, license, authors, classifiers, project URLs, and `requires-python`.
- dynamic package version loading from `tbot223_base.__version__`.
- the optional `test` dependency group.
- the optional `release` dependency group for build and metadata validation tools.
- the optional `dev` dependency group for test and release tooling together.
- package discovery for `tbot223_base`.
- inclusion of `py.typed` for type-aware tooling.
- pytest's default `tests` path.

## Local Release Tools

Install the reusable release tooling from the package extras.

```bash
python -m pip install -e ".[test,release]"
```

Then run the release readiness check.

```bash
scripts/check-release-readiness.sh v1.0.0rc1
```

Use strict release mode after the `v1.0.0rc1` tag exists locally and `origin/main` is available.

```bash
scripts/check-release-readiness.sh --strict-release v1.0.0rc1
```

Release gates accept stable `vMAJOR.MINOR.PATCH` tags and release-candidate `vMAJOR.MINOR.PATCHrcN` tags. After removing the leading `v`, the tag text must still exactly match `tbot223_base.__version__`.

The script runs metadata checks, Python compile checks, `pytest`, `actionlint`, `git diff --check`, temporary source/wheel builds, `twine check`, and distribution metadata assertions.

For host-only use, install the `actionlint` binary separately. The Docker check already includes it.

## Docker Checks

Use Docker when you want the same checks without depending on host Python tooling.

```bash
docker compose run --build --rm test
```

```bash
docker compose run --build --rm check
```

The `test` service runs only `pytest -q`. The `check` service runs `scripts/check-release-readiness.sh v1.0.0rc1` inside an image that installs the `test` and `release` dependency groups and includes `actionlint`.

## Compatibility CI

The workflow at `.github/workflows/python-compatibility.yml` runs on push, pull request, and manual dispatch.

It also supports `workflow_call` so the publish workflow can require the same compatibility matrix before uploading a package.

The current matrix is:

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

The compatibility workflow runs automatically for push and pull request events. Use manual dispatch before release-like checkpoints, public API changes, payload contract changes, or Python support range changes.

For small local-only edits, `pytest -q` in the current checkout is usually enough.

## Publish Workflow

The workflow at `.github/workflows/publish.yml` runs only when a GitHub Release is published.

Before uploading anything, it validates:

- the release has a tag.
- the tag uses stable `vMAJOR.MINOR.PATCH` or release-candidate `vMAJOR.MINOR.PATCHrcN` format, for example `v1.0.0rc1`.
- the tag points to a commit contained in `origin/main`.
- the tag version matches `tbot223_base.__version__` after removing the leading `v`.
- the Python compatibility matrix passes.
- source and wheel distributions build successfully.
- `twine check` accepts the generated distributions.

The publish job uses PyPI Trusted Publishing through GitHub OIDC. Configure the PyPI trusted publisher before publishing the first release.

Use these PyPI Trusted Publisher values:

- Repository owner: `Tbot223`
- Repository name: `tbot223-base`
- Workflow: `publish.yml`
- Environment name: `pypi`

## Release Checklist

For `1.0.0rc1`, the expected release tag is `v1.0.0rc1`.

Stable releases still use `vMAJOR.MINOR.PATCH`; release candidates use `vMAJOR.MINOR.PATCHrcN`. In both cases, use the exact package version with a leading `v`.

1. Merge or fast-forward the release commit onto `main`.
2. Confirm `tbot223_base.__version__` matches the intended release version.
3. Run the compatibility workflow manually if you want a pre-release signal before creating the GitHub Release.
4. Create the version tag on the `main` commit.
5. Run `scripts/check-release-readiness.sh --strict-release v1.0.0rc1` or `docker compose run --build --rm check --strict-release v1.0.0rc1`.
6. Publish a GitHub Release from that tag.

The publish workflow will stop before PyPI upload if the tag, branch ancestry, package version, tests, build, or metadata check does not match the release contract.
