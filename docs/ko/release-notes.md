[English](../en/release-notes.md)

# 릴리스 노트

## 0.0.1 / Current Dev Checkout

### Added

- `success`, `failure`, `cancelled` 상태를 명시하는 `ResultStatus`.
- Legacy `success=` 호환성을 유지하는 tuple-like outcome container `Result`.
- Debug 예외 payload와 public-safe 예외 payload를 분리한 `ExceptionTracker`.
- uncaught exception을 failure `Result`로 변환하는 `ExceptionTrackerDecorator`.

### Changed

- Debug exception context가 raw object reference 대신 작은 safe copy만 저장하고 무거운 값은 `"<BLOCKED>"`로 대체한다.
- 문서 경로를 `docs/contracts`, `docs/en`, `docs/ko` 아래 lowercase canonical path 중심으로 정리한다.

### Notes

- 현재 repository 문서는 package installation metadata 대신 checkout 기반 사용을 기준으로 한다.
