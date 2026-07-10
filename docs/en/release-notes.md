[한국어 (Korean)](../ko/release-notes.md)

# Release Notes

## 1.0.0 — 2026-07-10

`1.0.0` promotes the validated `1.0.0rc2` package to the first stable release. It introduces no runtime behavior changes from `1.0.0rc2`.

### Changed

- The package version and runtime/documentation baseline now target `1.0.0`.
- Package metadata now declares `Development Status :: 5 - Production/Stable`.
- Installation and release instructions now use the stable `1.0.0` package and `v1.0.0` tag, with GitHub's prerelease option disabled.

## 1.0.0rc2 — 2026-07-10

`1.0.0rc2` closes the remaining async, typing, and public-payload safety gaps found during the 1.0 release review. No public API removals are included.

### Added

- `ExceptionTrackerDecorator` now awaits coroutine functions and awaitable results inside the wrapper and converts their uncaught exceptions into failure `Result` objects while preserving successful async return values.
- Added an optional `type` dependency group, package-level mypy configuration, and a mypy gate in the Python 3.10-3.14 compatibility workflow and local release-readiness script.
- Release checks now install the built wheel in an isolated environment and verify imports, `Result`, public payload JSON serialization, and the packaged `py.typed` marker.
- Source distributions now include the bilingual docs, runnable examples, release script, full tests, and public consumer type-check fixture referenced by the repository metadata.

### Changed

- Public tag keys and values are now copied into a bounded JSON-safe shape. Unsupported, oversized, non-finite, cyclic, or too-deep values become `"<BLOCKED>"` without retaining caller-owned object references.
- `Result._make()` and `Result._replace()` keep runtime status normalization and subclass reconstruction while matching the generated `NamedTuple` typing surface.
- Strict local release mode now requires the release tag to point at `HEAD` and the working tree to be clean.
- The publish workflow now requires release-candidate tags to use the GitHub prerelease flag and stable tags not to use it.
- Installation docs now use an exact `1.0.0rc2` prerelease command while keeping the unqualified command for stable releases, and the Apache license notice now contains the final copyright text.

## 1.0.0rc1 — 2026-07-10

`1.0.0rc1` is the 1.0 API-stabilization release candidate. No public API removals are included in this release candidate.

### Changed

- `Result._make()` and `Result._replace()` now reconstruct values through `ResultStatus.normalize()` so reconstructed results keep the same normalized success/failure/cancelled invariant as direct construction.
- Debug-context safe-copy rules now block custom subclasses of scalar primitives such as `str`, `int`, and `float` instead of treating them as plain built-in scalars.
- Explicit `location.origin` masks now also affect the derived debug `Result.context` string, including partial origin masks that feed the formatted context.
- Unprintable exception text now falls back to `<unprintable ...>` while staying inside the failure `Result` / decorator boundary.
- Each debug payload now gets isolated per-call snapshots for `system_info.now` and copied `system_info.started_at`, and the docs/examples now document safe reuse of one tracker instance across threads.
- `ExceptionTracker.MASK_PRESETS` is now read-only so shared preset definitions cannot be mutated at runtime.
- Documentation now clarifies the public-safe payload path, when debug masking is still required for trusted-only payloads, and which security boundaries the caller still owns.
- Added executable `Result` and `ExceptionTracker` examples plus aligned English/Korean examples guides.
- Host-side release tooling now supports Python 3.10 through the `tomli` fallback when `tomllib` is unavailable.
- Release gates now accept exact-match stable tags (`vMAJOR.MINOR.PATCH`) and release-candidate tags (`vMAJOR.MINOR.PATCHrcN`), and the runtime/documentation baseline now targets `1.0.0rc1`.
- Release verification now covers Python 3.10-3.14 compatibility, the Docker release-check path, package build plus `twine check`, and workflow linting with `actionlint`.

## 0.1.0

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
- `Result` keeps `Result[T]` runtime subscription while avoiding a Python 3.10 `NamedTuple`/`Generic` import failure.
- Pre-release non-canonical module paths were removed in favor of canonical `tbot223_base.result` and `tbot223_base.exception_tracker`.
- `pyproject.toml` now uses `tbot223_base.__version__` as the dynamic package version source and declares the optional `test` dependency group.
- `pyproject.toml` now declares optional `release` and `dev` dependency groups for repeatable local checks.
- Documentation paths are being normalized around lowercase canonical paths under `docs/contracts`, `docs/en`, and `docs/ko`.
- Compatibility CI can now be reused by release workflows through `workflow_call`.
- Getting Started and API contract docs now describe `Result` as an independently shaped Python boundary exchange protocol rather than a Rust compatibility target.
- Release, CI, Docker, and repository maintenance commands are kept in the package and CI guide instead of the public README.

### Notes

- The repository keeps checkout-based usage documented while supporting local package tooling through `pyproject.toml`.
