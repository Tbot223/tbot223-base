[English](../en/rebuilding.md)

> 런타임 기준: package version `1.0.0a0` (`tbot223_base.__version__ == "1.0.0a0"`).

# `tbot223-base` 재정비

`tbot223-base`는 `1.0.0a0`부터 다시 시작한다. 이전 공개 버전과 release tag는 패키지가 안정적인 타입·안전성 보장을 내세웠지만 런타임 구현이 이를 완전히 강제하지 못했기 때문에 철회했다.

## 의미

- 현재는 production-ready release가 아닌 alpha 재정비 단계다.
- Public API, payload shape, release 절차는 migration 지원 없이 바뀔 수 있다.
- 아직 package name을 안정 의존성으로 설치하지 말고 source checkout에서 개발한다.
- Git commit 이력은 맥락을 위해 남기지만, 이전 릴리스 주장이 계속 유효하다는 뜻은 아니다.

## 현재 보장

- `Result`는 immutable tuple-like 형태를 유지하면서 모든 상태에서 명시적인 `data`를 요구한다.
- `Result.ok()`, `Result.failure()`, `Result.cancelled()`가 권장 typed factory이며 raw `_make()`, `_replace()` reconstruction은 제공하지 않는다.
- 실패한 `unwrap()` 또는 `expect()`는 raw value를 예외 메시지로 formatting하지 않고 `ResultUnwrapException` attribute에만 보관한다.
- Public exception 경로는 traceback, local context, system information을 수집하지 않는다. Debug system snapshot은 첫 debug-heavy 호출에서만 시작한다.
- Debug context copy는 exact built-in string key만 허용하며 custom `str` key object를 보존하지 않는다.

## 재정비 원칙

1. 런타임 동작, static type, 문서, 예제가 같은 계약을 설명하게 한다.
2. 선택한 boundary path에 필요한 데이터만 수집한다.
3. 깨진 불변식을 감추는 compatibility shim보다 작고 명시적인 인터페이스를 우선한다.
4. 안전성 또는 typing 주장을 새로 하면 반드시 regression test와 gate를 추가한다.

## 공개 릴리스 전 필수 게이트

- Unit test, deterministic public docstring doctest, AST 기반 docstring-contract check가 통과한다.
- Mypy가 지원하는 public usage는 통과시키고 의도적으로 잘못된 `Result` usage는 거부한다.
- Markdownlint, actionlint, package build, `twine check`, isolated-wheel smoke check가 통과한다.
- Python 3.10부터 3.14 compatibility CI가 통과한다.
- `v1.0.0a0` 같은 GitHub prerelease tag가 package version과 정확히 일치하고, 공개를 고려하기 전에 strict release readiness를 통과한다.

## 보류한 작업

이번 alpha 재정비는 final public payload `TypedDict`, suppressed exception context 정책, public tag 전역 budget, immutable supply-chain pinning, SBOM/provenance artifact, stable release compatibility를 아직 보장하지 않는다. 이 항목들은 숨은 동작이 아니라 별도 후속 결정으로 남긴다.
