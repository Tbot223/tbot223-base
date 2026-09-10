[English](../../en/human/api-contract.md)

> Contract revision: 2026-09-09 (unreleased boundary fixes).

# API Contract

> public import path, `Result`, `ExceptionTracker` payload shape에 적용하는 계약이다.

## 1. 목표

- 재정비 alpha public API를 Python 관례에 맞는 canonical module path 중심으로 정의한다.
- `Result`를 Rust compatibility target이 아니라 독립적으로 형성된 Python 경계 교환 프로토콜로 정의한다.
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

`Result.data`는 의도적인 `None`을 포함해 모든 result 상태에서 반드시 제공해야 한다. `Result.ok(data)`, `Result.failure(data, ...)`, `Result.cancelled(data, ...)`가 권장 typed construction API다. `Result`는 tuple-like read behavior를 유지하지만 raw `_make()`, `_replace()` reconstruction helper를 노출해서는 안 된다.

`Result`는 Python 코드의 경계에서 쓰는 exchange shape로 문서화해야 한다. Rust의 `Result`를 언급할 때는 비교 기준으로만 다뤄야 하며, 원형이나 compatibility target으로 설명해서는 안 된다.

`success=` 입력과 `result.success` property는 문서화된 breaking change로 제거되기 전까지 지원되는 tri-state shorthand API로 SHOULD 유지한다.

Payload가 연산을 지원하면 표준 copy/deepcopy와 pickle 복원은 검증된 result field를 MUST 유지한다. Literal tuple indexing과 unpacking은 각 field 타입을 MUST 유지한다.

## 5. Exception Payload 계약

`ExceptionTracker`는 두 payload path를 가진다.

| Path | Methods | Boundary |
| --- | --- | --- |
| Debug-heavy | `get_exception_info()`, `get_exception_return()` | trusted internal diagnostics. |
| Public-safe | `get_public_exception_info()`, `get_public_exception_return()` | API response, UI surface, untrusted boundary. |

Debug payload는 mask되었거나 수집할 수 없는 경우를 제외하고 structured failure metadata, location information, copied safe context, chained causes, traceback data, system information을 MUST 포함한다. Shared system snapshot 하나는 첫 debug-heavy 호출에서 lazy 수집하고 이후 재사용해야 하며 public-safe method와 location lookup은 이를 수집해서는 안 된다.

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

Public tag key는 bounded string으로 MUST 정규화한다. Public tag value는 caller-owned object reference를 보존하지 않는 bounded JSON-safe shape로 MUST 복사한다. 지원하지 않거나, 너무 크거나, non-finite이거나, 순환하거나, 너무 깊은 값은 `"<BLOCKED>"`로 MUST 대체한다.

`ExceptionTrackerDecorator`는 synchronous function, coroutine function, awaited result에서 발생한 uncaught exception을 failure `Result`로 MUST 변환한다. 이후 generator 또는 async-generator iteration 중 발생한 exception은 이 decorator 계약의 범위 밖이다.

자동 wrapper는 awaitable을 반환하는 callable이 즉시 `Result`를 반환할 가능성을 정적 반환 타입에 MUST 표시한다. `wrap_awaitable()`은 항상 coroutine을 반환하고 지연된 함수 호출과 await 양쪽의 실패를 MUST 변환한다. Cancellation과 다른 `BaseException` subclass는 MUST 전파한다.

Public 정수는 절댓값 기준 512 bit까지만 MUST 허용한다. 문자열 error code와 정규화된 모든 tag key는 200자 이하로 MUST 제한한다. 미지원 key는 제거하고, 초과한 tag value는 차단하고, 잘못되거나 초과한 error code는 기본 code로 MUST 대체한다. Public tag 복사는 nested value와 반복 참조 전체에 256-value 순회 예산을 MUST 공유하며, 남은 예산으로 완성하지 못하는 collection은 `"<BLOCKED>"`로 MUST 대체한다.

최종 public field 타입은 실제 payload에 MUST 일치한다. 식별자와 메시지는 string, status는 `Literal["failure"]`, success는 `Literal[False]`이며 retryable만 nullable이다.

## 7. Debug Safety Rules

Debug context capture는 raw object reference를 보존하지 않아야 한다. Mapping key는 exact built-in `str`이어야 하며 custom `str` subclass를 identity로 복사해서는 안 된다.

작은 primitive 값은 복사할 수 있다. 무겁거나, 깊거나, 지원하지 않거나, custom object인 값은 `"<BLOCKED>"`로 MUST 대체한다.

Mask preset과 명시적 mask path는 context capture 이후에 MUST 적용한다.

기본 debug path는 `input_context.local_variables`를 SHOULD mask한다.

Mask preset을 debug payload 전체의 public 노출 안전성 보장으로 설명해서는 안 된다. 외부 응답은 public 경로를 MUST 사용한다. Debug 수집 또는 masking이 실패하면 fallback data dictionary에는 `tracker_failure=True`와 고정 일반 메시지만 MUST 포함하며 원본 예외, 입력, traceback은 제외한다. Fallback은 stdout·stderr 쓰기에 의존해서는 안 된다.

## 8. Validation Rules

계약에 영향을 주는 API 변경은 실행 가능한 테스트를 MUST 포함한다.

테스트는 다음을 SHOULD 확인한다.

- Canonical import path.
- Package-level public export.
- `ResultStatus` normalization, 필수 `data`, typed factory, 거부되는 raw reconstruction helper.
- Debug payload masking과 safe context capture.
- Public payload의 최소 field와 debug-only field 부재.
- Public tag JSON serialization과 caller-owned object reference 부재.
- Decorator가 synchronous/async uncaught exception을 failure `Result`로 변환하는 동작.
- Lazy debug system collection, deterministic public docstring, 거부되는 invalid consumer typing.

Python compatibility CI는 push, pull request, manual dispatch, release-like checkpoint 전에 선언된 Python version matrix에서 test suite와 package type check를 SHOULD 실행한다.

음성 consumer type gate는 mypy 종료 코드만 확인하지 않고 주석으로 지정한 각 line의 예상 diagnostic을 MUST 검증한다. Source distribution은 non-strict readiness에 필요한 script와 설정을 MUST 포함한다. Strict release mode는 Git metadata가 없는 source archive를 MUST 거부한다.

## 9. 최종 체크리스트

- Canonical import가 계속 동작하는가?
- Package-level export가 같은 public object를 반환하는가?
- Public payload에 debug-only field가 없는가?
- Debug payload masking이 context capture 이후 적용되는가?
- 바뀐 payload shape를 테스트가 고정하는가?
- 의도적인 compatibility 또는 breaking behavior가 문서에 적혀 있는가?
