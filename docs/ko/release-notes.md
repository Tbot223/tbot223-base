[English](../en/release-notes.md)

# 릴리스 노트

## 1.0.0a1 — lint 기준

`1.0.0a1`은 `1.0.0a0` 이후 재정비 alpha를 이어간다. 새 runtime API나 stable compatibility 보장을 추가하지 않는다.

### 추가

- 저장소가 Python 3.10 기준의 Ruff 설정과 baseline correctness/import sorting 규칙(`E4`, `E7`, `E9`, `F`, `I`)을 직접 관리한다.
- Ruff는 development-only `lint` extra로 제공하고 compatibility CI, Docker check, release readiness에서 실행한다.

### 변경

- Package code, test, example, helper script의 import ordering과 Ruff formatter 출력을 같은 기준으로 맞췄다.
- Developer/release 문서에 Ruff lint와 format check를 추가했다.

## 1.0.0a0 — 재정비

`1.0.0a0`는 패키지를 alpha 재정비로 다시 시작한다. 이전 공개 릴리스와 tag는 철회했으며, 이 문서는 그것들을 유효한 릴리스 이력으로 보존하지 않는다. 이유와 현재 범위는 [재정비 문서](rebuilding.md)를 참고한다.

### Alpha 상태

이 버전은 GitHub prerelease이며 production release가 아니다. 안정 의존성으로 도입하거나 호환성 지원을 기대하면 안 된다. 재정비 기간에는 public API, payload shape, release 절차가 바뀔 수 있다.

### 복구한 계약

- failure와 cancellation을 포함한 모든 outcome에서 `Result.data`를 필수로 한다. 의도적으로 payload가 없을 때는 명시적 `None`을 계속 허용한다.
- `Result.ok()`, `Result.failure()`, `Result.cancelled()`가 권장 typed 생성 경로이며, tuple-like unpacking, indexing, comparison은 유지한다.
- Raw `Result._make()`, `_replace()` reconstruction helper는 제공하지 않는다.
- 실패한 `unwrap()`와 `expect()`는 raw value를 `ResultUnwrapException` attribute에만 보관한다. 예외 메시지는 저장된 data, error, context를 formatting하지 않는다.
- `ExceptionTracker`는 첫 debug-heavy 호출에서 shared system snapshot 하나만 lazy 수집한다. public-only method와 location lookup은 이를 수집하지 않는다.
- Debug context copy는 exact built-in `str` key만 허용한다. 없는 error-code mapping은 `data=None`인 일반 failure result로 반환하고 emergency output을 내보내지 않는다.

### 품질 게이트

- Public docstring은 구조 검사와 deterministic doctest로 검증한다.
- Type gate는 유효한 `Result` 생성을 통과시키고 data 생략, 잘못된 payload type, 제거된 raw helper 사용을 거부한다.
- CI는 Python 3.10–3.14를 대상으로 pytest, mypy, Ruff lint/format, Markdownlint, actionlint, package check를 실행한다.
- release-ready package는 sdist/wheel build, `twine check`, isolated wheel smoke test를 통과했다.

### 보류한 작업

Public payload `TypedDict` 확정, exception chaining 정책, public tag 전역 budget, immutable supply-chain pinning, SBOM/provenance artifact, stable compatibility 보장은 후속 작업이다. 이 alpha는 이들을 약속하지 않는다.
