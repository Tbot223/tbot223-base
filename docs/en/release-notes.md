[한국어 (Korean)](../ko/release-notes.md)

# Release Notes

## 0.1.0 / Current Dev Checkout

### Added

- `ResultStatus` with explicit `success`, `failure`, and `cancelled` states.
- `Result` tuple-like outcome container with `success=` tri-state shorthand.
- `ExceptionTracker` debug and public-safe exception payload paths.
- `ExceptionTrackerDecorator` for converting uncaught exceptions into failure `Result` objects.
- Publish-ready `pyproject.toml` packaging metadata for local package tooling.
- Canonical `tbot223_base.result` and `tbot223_base.exception_tracker` module paths.
- API contract docs for import paths, `Result`, and debug/public `ExceptionTracker` payload shapes.
- Python compatibility CI for Python 3.10 through 3.14 on push, pull request, and manual dispatch.
- Release-only PyPI publish workflow gated by a `vMAJOR.MINOR.PATCH` tag, package version match, `main` branch ancestry, compatibility tests, build, and metadata checks.
- Reusable local release readiness script for tests, workflow linting, package builds, `twine check`, and distribution metadata assertions.
- Docker and Compose entry points for one-command test and release-readiness checks.
- English-first root README with a Korean companion README, design intent, audience fit, trade-offs, and quickstart examples.

### Changed

- Debug exception context now stores only small safe copies and replaces heavy values with `"<BLOCKED>"`.
- Pre-release non-canonical module paths were removed in favor of canonical `tbot223_base.result` and `tbot223_base.exception_tracker`.
- `pyproject.toml` now uses `tbot223_base.__version__` as the dynamic package version source and declares the optional `test` dependency group.
- `pyproject.toml` now declares optional `release` and `dev` dependency groups for repeatable local checks.
- Documentation paths are being normalized around lowercase canonical paths under `docs/contracts`, `docs/en`, and `docs/ko`.
- Compatibility CI can now be reused by release workflows through `workflow_call`.
- Getting Started and API contract docs now describe `Result` as an independently shaped Python boundary exchange protocol rather than a Rust compatibility target.
- Release, CI, Docker, and repository maintenance commands are kept in the package and CI guide instead of the public README.

### Notes

- The repository keeps checkout-based usage documented while supporting local package tooling through `pyproject.toml`.
