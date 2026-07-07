[English](../en/release-notes.md)

# 릴리스 노트

## 0.0.1 / Current Dev Checkout

### Added

- `success`, `failure`, `cancelled` 상태를 명시하는 `ResultStatus`.
- `success=` tri-state shorthand를 지원하는 tuple-like outcome container `Result`.
- Debug 예외 payload와 public-safe 예외 payload를 분리한 `ExceptionTracker`.
- uncaught exception을 failure `Result`로 변환하는 `ExceptionTrackerDecorator`.
- local package tooling을 위한 최소 `pyproject.toml` packaging metadata.
- Canonical `tbot223_base.result`, `tbot223_base.exception_tracker` module path.
- import path, `Result`, debug/public `ExceptionTracker` payload shape용 API 계약 문서.
- Python 3.9부터 3.14까지 확인하는 optional manual Python compatibility CI.

### Changed

- Debug exception context가 raw object reference 대신 작은 safe copy만 저장하고 무거운 값은 `"<BLOCKED>"`로 대체한다.
- Pre-release non-canonical module path는 제거하고 canonical `tbot223_base.result`, `tbot223_base.exception_tracker`만 사용한다.
- `pyproject.toml`이 optional `test` dependency group과 Python 3.9 typing fallback dependency를 정의한다.
- 문서 경로를 `docs/contracts`, `docs/en`, `docs/ko` 아래 lowercase canonical path 중심으로 정리한다.

### Notes

- 현재 repository 문서는 checkout 기반 사용을 유지하면서 `pyproject.toml`을 통한 local package tooling을 지원한다.
