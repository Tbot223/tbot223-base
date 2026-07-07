[English](../en/release-notes.md)

# 릴리스 노트

## 0.1.0 / Current Dev Checkout

### Added

- `success`, `failure`, `cancelled` 상태를 명시하는 `ResultStatus`.
- `success=` tri-state shorthand를 지원하는 tuple-like outcome container `Result`.
- Debug 예외 payload와 public-safe 예외 payload를 분리한 `ExceptionTracker`.
- uncaught exception을 failure `Result`로 변환하는 `ExceptionTrackerDecorator`.
- local package tooling을 위한 publish-ready `pyproject.toml` packaging metadata.
- Canonical `tbot223_base.result`, `tbot223_base.exception_tracker` module path.
- import path, `Result`, debug/public `ExceptionTracker` payload shape용 API 계약 문서.
- push, pull request, manual dispatch에서 Python 3.10부터 3.14까지 확인하는 Python compatibility CI.
- `vMAJOR.MINOR.PATCH` tag, package version match, `main` branch ancestry, compatibility tests, build, metadata check로 gate되는 release-only PyPI publish workflow.
- tests, workflow linting, package build, `twine check`, distribution metadata assertion을 반복 실행하는 local release readiness script.
- 한 줄 명령으로 test와 release-readiness check를 실행하는 Docker/Compose entry point.
- English-first root README와 Korean companion README, design intent, 맞는 사용자, 트레이드오프, quickstart 예시.

### Changed

- Debug exception context가 raw object reference 대신 작은 safe copy만 저장하고 무거운 값은 `"<BLOCKED>"`로 대체한다.
- Pre-release non-canonical module path는 제거하고 canonical `tbot223_base.result`, `tbot223_base.exception_tracker`만 사용한다.
- `pyproject.toml`이 `tbot223_base.__version__`을 dynamic package version source로 사용하고 optional `test` dependency group을 정의한다.
- 반복 가능한 local check를 위해 optional `release`, `dev` dependency group을 정의한다.
- 문서 경로를 `docs/contracts`, `docs/en`, `docs/ko` 아래 lowercase canonical path 중심으로 정리한다.
- Compatibility CI를 `workflow_call`로 release workflow에서 재사용할 수 있게 했다.
- Getting Started와 API contract 문서가 `Result`를 Rust compatibility target이 아니라 독립적으로 형성된 Python 경계 교환 프로토콜로 설명한다.
- Release, CI, Docker, repository maintenance 명령은 public README 대신 package and CI guide에서 다룬다.

### Notes

- 현재 repository 문서는 checkout 기반 사용을 유지하면서 `pyproject.toml`을 통한 local package tooling을 지원한다.
