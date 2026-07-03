[한국어 (Korean)](../ko/release-notes.md)

# Release Notes

## 0.0.1 / Current Dev Checkout

### Added

- `ResultStatus` with explicit `success`, `failure`, and `cancelled` states.
- `Result` tuple-like outcome container with legacy `success=` compatibility.
- `ExceptionTracker` debug and public-safe exception payload paths.
- `ExceptionTrackerDecorator` for converting uncaught exceptions into failure `Result` objects.

### Changed

- Debug exception context now stores bounded snapshots instead of raw object references.
- Documentation paths are being normalized around lowercase canonical paths under `docs/contracts`, `docs/en`, and `docs/ko`.

### Notes

- The repository currently documents checkout-based usage rather than package installation metadata.
