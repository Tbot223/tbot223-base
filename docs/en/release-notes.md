[한국어 (Korean)](../ko/release-notes.md)

# Release Notes

## 0.0.1 / Current Dev Checkout

### Added

- `ResultStatus` with explicit `success`, `failure`, and `cancelled` states.
- `Result` tuple-like outcome container with `success=` tri-state shorthand.
- `ExceptionTracker` debug and public-safe exception payload paths.
- `ExceptionTrackerDecorator` for converting uncaught exceptions into failure `Result` objects.
- Minimal `pyproject.toml` packaging metadata for local package tooling.
- Canonical `tbot223_base.result` and `tbot223_base.exception_tracker` module paths.
- API contract docs for import paths, `Result`, and debug/public `ExceptionTracker` payload shapes.
- Optional manual Python compatibility CI for Python 3.9 through 3.14.

### Changed

- Debug exception context now stores only small safe copies and replaces heavy values with `"<BLOCKED>"`.
- Pre-release non-canonical module paths were removed in favor of canonical `tbot223_base.result` and `tbot223_base.exception_tracker`.
- `pyproject.toml` now defines the optional `test` dependency group and Python 3.9 typing fallback dependency.
- Documentation paths are being normalized around lowercase canonical paths under `docs/contracts`, `docs/en`, and `docs/ko`.

### Notes

- The repository keeps checkout-based usage documented while supporting local package tooling through `pyproject.toml`.
