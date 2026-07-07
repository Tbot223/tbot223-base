[English](../../en/human/api-contract.md)

> Contract revision: 2026-07-07.

# API Contract

> public import path, `Result`, `ExceptionTracker` payload shape에 적용하는 계약이다.

## 1. 목표

- pre-release public API를 Python 관례에 맞는 canonical module path 중심으로 정의한다.
- debug/public 예외 payload를 우연히 만들어진 dict가 아니라 명시적 계약으로 다룬다.
- 내부 진단 정보와 외부 노출용 error payload의 안전 경계를 유지한다.
- API나 payload 동작이 바뀔 때 실행 가능한 테스트도 함께 맞춘다.

## 2. 적용 범위

이 계약은 다음에 적용한다.

- `tbot223_base` 아래 canonical import path.
- `ResultStatus`, `Result`, `ResultUnwrapException`.
- `ExceptionTracker`, `ExceptionTrackerDecorator`, 그리고 반환되는 debug/public payload 구조.
- API 계약을 검증하는 테스트와 CI job.

이 계약은 다음에는 적용하지 않는다.

- public API로 import하지 않는 private helper 이름.
- 테스트가 명시적으로 고정하지 않은 내부 error string의 정확한 문구.
- 표현만 바뀌는 문서 문장.

## 3. Public Import 경로

Public code는 다음 canonical path를 MUST 사용한다.

- `tbot223_base.result`
- `tbot223_base.exception_tracker`

`tbot223_base.__init__`의 package-level export는 주요 public API object를 SHOULD 노출한다.

## 4. Result 계약

`Result`는 다음 field를 가진 immutable tuple-like outcome container로 MUST 유지된다.

| Field | Meaning |
| --- | --- |
| `status` | 정규화된 `ResultStatus`. |
| `error` | 선택적 human-readable error text. |
| `context` | 선택적 operation context. |
| `data` | operation payload. |

`ResultStatus`는 `success`, `failure`, `cancelled` string value를 MUST 유지한다.

`success=` 입력과 `result.success` property는 문서화된 breaking change로 제거되기 전까지 지원되는 tri-state shorthand API로 SHOULD 유지한다.

## 5. Exception Payload 계약

`ExceptionTracker`는 두 payload path를 가진다.

| Path | Methods | Boundary |
| --- | --- | --- |
| Debug-heavy | `get_exception_info()`, `get_exception_return()` | trusted internal diagnostics. |
| Public-safe | `get_public_exception_info()`, `get_public_exception_return()` | API response, UI surface, untrusted boundary. |

Debug payload는 mask되었거나 수집할 수 없는 경우를 제외하고 structured failure metadata, location information, copied safe context, chained causes, traceback data, system information을 MUST 포함한다.

Public payload는 lightweight하게 유지해야 하며 traceback text, traceback frames, local variables, params, user input, system information을 MUST NOT 포함한다.

## 6. Public Payload Shape

Public payload는 다음 top-level shape를 MUST 사용한다.

| Key | Meaning |
| --- | --- |
| `id` | payload unique identifier. |
| `status` | failure status string. |
| `success` | `False`. |
| `timestamp` | UTC timestamp string. |
| `error` | public `code`와 `message`. |
| `tags` | string key를 가진 public metadata. |
| `retryable` | 선택적 retry hint. |

Caller가 안전한 `public_message`를 명시적으로 넘기지 않는 한 raw exception message는 public payload에 MUST NOT 노출한다.

## 7. Debug Safety Rules

Debug context capture는 raw object reference를 보존하지 않아야 한다.

작은 primitive 값은 복사할 수 있다. 무겁거나, 깊거나, 지원하지 않거나, custom object인 값은 `"<BLOCKED>"`로 MUST 대체한다.

Mask preset과 명시적 mask path는 context capture 이후에 MUST 적용한다.

기본 debug path는 `input_context.local_variables`를 SHOULD mask한다.

## 8. Validation Rules

계약에 영향을 주는 API 변경은 실행 가능한 테스트를 MUST 포함한다.

테스트는 다음을 SHOULD 확인한다.

- Canonical import path.
- Package-level public export.
- `ResultStatus` normalization과 `success=` shorthand behavior.
- Debug payload masking과 safe context capture.
- Public payload의 최소 field와 debug-only field 부재.
- Decorator가 uncaught exception을 failure `Result`로 변환하는 동작.

Optional Python compatibility CI는 release-like checkpoint 전에 선언된 Python version matrix에서 test suite를 SHOULD 실행한다.

## 9. 최종 체크리스트

- Canonical import가 계속 동작하는가?
- Package-level export가 같은 public object를 반환하는가?
- Public payload에 debug-only field가 없는가?
- Debug payload masking이 context capture 이후 적용되는가?
- 바뀐 payload shape를 테스트가 고정하는가?
- 의도적인 compatibility 또는 breaking behavior가 문서에 적혀 있는가?
