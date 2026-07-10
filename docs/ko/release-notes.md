[English](../en/release-notes.md)

# 릴리스 노트

## 1.0.0 — 2026-07-10

`1.0.0`은 검증을 마친 `1.0.0rc2` package를 첫 stable release로 승격한다. `1.0.0rc2` 대비 runtime behavior 변경은 없다.

### Changed

- Package version과 runtime/documentation baseline을 `1.0.0`으로 맞췄다.
- Package metadata가 `Development Status :: 5 - Production/Stable`을 선언한다.
- 설치 및 release 안내가 stable `1.0.0` package와 `v1.0.0` tag를 사용하고 GitHub prerelease option을 끄도록 정리됐다.

## 1.0.0rc2 — 2026-07-10

`1.0.0rc2`는 1.0 release review에서 발견한 async, typing, public payload safety gap을 마무리한다. Public API 제거는 없다.

### Added

- `ExceptionTrackerDecorator`가 이제 wrapper 안에서 coroutine function과 awaitable result를 await하고, 성공한 async return value는 유지하면서 uncaught exception을 failure `Result`로 변환한다.
- Optional `type` dependency group, package-level mypy configuration, Python 3.10-3.14 compatibility workflow와 local release-readiness script의 mypy gate를 추가했다.
- Release check가 built wheel을 격리 환경에 설치한 뒤 import, `Result`, public payload JSON serialization, packaged `py.typed` marker를 검증한다.
- Source distribution에 bilingual docs, runnable example, release script, 전체 test, repository metadata가 참조하는 public consumer type-check fixture를 포함한다.

### Changed

- Public tag key와 value를 bounded JSON-safe shape로 복사한다. 지원하지 않거나, 너무 크거나, non-finite이거나, 순환하거나, 너무 깊은 값은 caller-owned object reference를 보존하지 않고 `"<BLOCKED>"`로 바뀐다.
- `Result._make()`와 `Result._replace()`가 runtime status normalization과 subclass reconstruction을 유지하면서 generated `NamedTuple` typing surface와 일치하도록 정리했다.
- Strict local release mode는 release tag가 `HEAD`를 가리키고 working tree가 clean한 상태를 요구한다.
- Publish workflow는 release-candidate tag에 GitHub prerelease flag를 요구하고 stable tag에는 그 flag를 허용하지 않는다.
- 설치 문서는 exact `1.0.0rc2` prerelease 명령을 사용하고 unqualified command는 stable release용으로 유지하며, Apache license notice도 최종 copyright text로 정리했다.

## 1.0.0rc1 — 2026-07-10

`1.0.0rc1`은 1.0 API 안정화를 위한 release candidate다. 이번 release candidate에는 public API 제거가 없다.

### Changed

- `Result._make()`와 `Result._replace()`가 이제 `ResultStatus.normalize()`를 거쳐 값을 다시 구성하므로, 재구성된 result도 직접 생성한 경우와 같은 success/failure/cancelled 정규화 불변식을 유지한다.
- Debug context safe-copy 규칙이 이제 `str`, `int`, `float` 같은 scalar primitive의 custom subclass를 일반 built-in scalar로 취급하지 않고 차단한다.
- 명시적인 `location.origin` mask는 이제 formatting에 사용되는 파생 debug `Result.context` 문자열에도 반영되며, 부분 origin mask도 같은 규칙을 따른다.
- 출력할 수 없는 exception text는 이제 failure `Result` / decorator boundary 밖으로 새지 않고 `<unprintable ...>` fallback으로 처리된다.
- 각 debug payload는 이제 `system_info.now`와 복사된 `system_info.started_at`에 대해 호출별로 분리된 snapshot을 가지며, 문서와 예시는 하나의 tracker instance를 여러 thread에서 안전하게 재사용하는 방법을 설명한다.
- `ExceptionTracker.MASK_PRESETS`를 read-only로 바꿔 shared preset definition이 runtime에 변경되지 않도록 했다.
- 문서는 public-safe payload 경로를 언제 써야 하는지, trusted-only debug payload에도 여전히 어떤 masking이 필요한지, 그리고 어떤 보안 경계를 caller가 직접 책임져야 하는지를 더 명확히 설명한다.
- 실행 가능한 `Result` / `ExceptionTracker` 예시와 이에 맞춘 영문/국문 examples guide를 추가했다.
- Host-side release tooling은 `tomllib`가 없는 경우 `tomli` fallback을 사용해 Python 3.10도 지원한다.
- Release gate는 이제 exact-match stable tag(`vMAJOR.MINOR.PATCH`)와 release candidate tag(`vMAJOR.MINOR.PATCHrcN`)를 모두 허용하며, runtime/documentation baseline도 `1.0.0rc1`로 맞췄다.
- Release 검증 범위는 이제 Python 3.10-3.14 compatibility, Docker release check 경로, package build + `twine check`, `actionlint` 기반 workflow linting까지 포함한다.

## 0.1.0

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
- `Result`가 `Result[T]` runtime subscription을 유지하면서 Python 3.10의 `NamedTuple`/`Generic` import 실패를 피하도록 정리했다.
- Pre-release non-canonical module path는 제거하고 canonical `tbot223_base.result`, `tbot223_base.exception_tracker`만 사용한다.
- `pyproject.toml`이 `tbot223_base.__version__`을 dynamic package version source로 사용하고 optional `test` dependency group을 정의한다.
- 반복 가능한 local check를 위해 optional `release`, `dev` dependency group을 정의한다.
- 문서 경로를 `docs/contracts`, `docs/en`, `docs/ko` 아래 lowercase canonical path 중심으로 정리한다.
- Compatibility CI를 `workflow_call`로 release workflow에서 재사용할 수 있게 했다.
- Getting Started와 API contract 문서가 `Result`를 Rust compatibility target이 아니라 독립적으로 형성된 Python 경계 교환 프로토콜로 설명한다.
- Release, CI, Docker, repository maintenance 명령은 public README 대신 package and CI guide에서 다룬다.

### Notes

- 현재 repository 문서는 checkout 기반 사용을 유지하면서 `pyproject.toml`을 통한 local package tooling을 지원한다.
