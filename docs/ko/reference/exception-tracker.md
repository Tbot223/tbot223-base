[English](../../en/reference/exception-tracker.md)

> 런타임 기준: `1.0.0a1` 기반 미배포 working tree. 이번 수정은 기존 release tag에 포함되지 않는다.

# ExceptionTracker 레퍼런스

이 문서는 `ExceptionTracker`, `ExceptionTrackerDecorator`, masking, safe context capture 정책을 설명한다.

Debug/public payload shape의 안정성 규칙은 [API 계약](../../contracts/ko/human/api-contract.md)을 기준으로 본다.

## 두 가지 payload 경로

| Path | Methods | Intended use |
| --- | --- | --- |
| Debug-heavy | `get_exception_info()`, `get_exception_return()` | traceback과 context metadata가 필요한 내부 진단. |
| Public-safe | `get_public_exception_info()`, `get_public_exception_return()` | API 응답, UI, untrusted boundary. |

Public-safe 경로는 traceback text, local variables, params, system information을 수집하지 않는다. Tracker를 생성하거나 `get_exception_location()`을 호출해도 deferred system snapshot은 수집하지 않는다.

## Public tag safety

Public tag key는 string으로 정규화하고, value는 caller-owned reference를 보존하지 않도록 JSON-safe structure로 복사한다.

Public tag copy 정책은 exact built-in `None`, `bool`, `int`, finite `float`, bounded `str` 값을 유지한다. Tag value, 정규화할 key, error code의 정수는 절댓값 기준 `PUBLIC_MAX_INTEGER_BITS`(512) bit까지만 허용한다. 초과한 정수 value는 `"<BLOCKED>"`, 초과·미지원 key는 제거, 초과한 error code는 기본 code로 처리한다. 문자열 error code와 정규화된 모든 key는 200자로 제한한다. Plain `list`와 `tuple`은 복사된 list가 되고, plain `dict`는 정규화된 string key를 가진 dictionary가 된다. Collection마다 `CONTEXT_MAX_ITEMS`개까지 유지하며 nesting은 `PUBLIC_TAG_MAX_DEPTH`로 제한한다. 지원하지 않거나, 너무 크거나, non-finite이거나, 순환하거나, 너무 깊은 값은 `"<BLOCKED>"`로 대체한다.

전체 tags mapping이 반복 참조를 포함해 `PUBLIC_TAG_MAX_NODES`(256)의 value 방문 예산을 공유한다. 남은 예산 안에 복사를 마칠 수 없는 collection은 `"<BLOCKED>"`가 되며 이후 value도 차단될 수 있다. 작은 tag의 기존 shape는 유지한다. 이는 순회 예산이며 caller가 명시한 public message·context의 byte 제한은 아니다.

최종 public field의 `id`, `timestamp`, `error.code`, `error.message`는 non-optional이다. `status`는 literal `"failure"`, `success`는 literal `False`이며 `retryable`만 nullable이다.

## Import 경로

`ExceptionTracker`, `ExceptionTrackerDecorator`는 `tbot223_base.exception_tracker`에서 import한다.

## Debug context capture

Debug 경로는 `user_input`, `params.args`, `params.kwargs`, origin frame의 `local_variables`를 raw object reference가 아니라 안전한 복사본으로 저장한다.

기본 안전 제한값:

| Constant | Value |
| --- | --- |
| `CONTEXT_MAX_VALUE_LENGTH` | `200` |
| `CONTEXT_MAX_ITEMS` | `20` |
| `PUBLIC_TAG_MAX_DEPTH` | `3` |
| `PUBLIC_MAX_INTEGER_BITS` | `512` |
| `PUBLIC_TAG_MAX_NODES` | `256` |

작은 primitive와 primitive-only `list`/`tuple` 값만 복사한다. Top-level `dict` 값은 item 제한을 만족할 때만 복사한다. 깊은 nested 값, bytes-like 값, custom object는 metadata로 요약하지 않고 `"<BLOCKED>"`로 대체한다.

## System info

Debug payload는 첫 debug-heavy 호출에서 system snapshot 하나를 lazy 수집하고 이후 각 payload에 복사한다. `started_at`과 `now` 모두 추가 system collection을 일으키지 않는다. 환경변수는 key가 작은 문자열이고 value가 작은 primitive 또는 작은 primitive만 담은 얕은 tuple/list일 때만 복사하며, `ENVIRONMENT_VARIABLE_MAX_COUNT`개에서 수집을 멈춘다. 작은 환경변수 값도 민감할 수 있다. Mask된 debug payload도 내부 진단용이며 외부 응답에는 public method를 사용한다.

## Thread concurrency

`ExceptionTracker` instance는 여러 thread 호출에서 재사용할 수 있도록 설계한다. Debug payload는 호출마다 새로 생성하며, startup system information도 reference를 공유하지 않고 각 payload에 복사해서 넣는다.

반환되는 payload dictionary는 여전히 mutable하다. Caller가 반환 payload를 수정하거나 여러 thread에 공유한다면 자체 synchronization을 제공해야 한다. `Result` container 자체는 immutable이지만, `Result.data`에는 mutable user payload가 들어갈 수 있다.

이 보장은 thread 중심이다. Multiprocessing 동작이나 process 간 shared-state 보장을 새로 추가하지 않는다.

## Mask preset

| Preset | Effect |
| --- | --- |
| `default` | `input_context.local_variables`를 mask한다. |
| `private` | user input, params, local variables를 mask한다. |
| `user_input` | `input_context.user_input`을 mask한다. |
| `params` | params와 local variables를 mask한다. |
| `traceback` | causes, traceback text, traceback frames를 mask한다. |
| `system_info` | system information을 mask한다. |

명시적 `mask_paths`로 `"location.origin"` 같은 dot path나 `("error", "message")` 같은 tuple path도 mask할 수 있다. Debug `Result.context`가 `location.origin`에서 파생될 때도 같은 masking 결과가 반영된다.

Mask preset은 지정 field를 선택적으로 가릴 뿐 모든 비밀을 제거하지 않는다. 특히 `("private", "traceback", "system_info")` 조합에도 원본 오류 메시지와 source location이 남는다.

Debug 수집이나 masking이 실패하면 `data`에는 `{"tracker_failure": True, "message": <고정 일반 메시지>}`만 남는다. 원본 예외, traceback, 입력 데이터는 포함하지 않는다. Fallback 경로는 stdout·stderr에 출력하지 않는다. Caller는 `result.data.get("tracker_failure") is True`로 tracker 자체 실패를 구분할 수 있다.

## Public example

```python
from tbot223_base.exception_tracker import ExceptionTracker

tracker = ExceptionTracker()

try:
    1 / 0
except Exception as error:
    result = tracker.get_public_exception_return(
        error,
        error_code="DIVIDE_BY_ZERO",
        public_message="The calculation could not be completed.",
        tags={"layer": "service"},
        retryable=False,
    )
```

## Decorator

`ExceptionTrackerDecorator`는 synchronous function과 coroutine function을 자동으로 감싼다. Awaitable을 반환하는 callable의 정적 반환 타입은 `Awaitable[T | Result[object]] | Result[object]`다. 동기 factory는 awaitable 생성 전에 실패할 수 있기 때문이다. 기존 자동 경로의 runtime 동작은 유지하지만 caller는 await 전에 union을 좁혀야 한다.

모든 호출에서 coroutine을 반환해야 한다면 coroutine function과 동기 awaitable factory에 `@decorator.wrap_awaitable`을 사용한다. 이 wrapper는 await할 때 원래 함수를 호출하고, factory 호출 중 실패와 await 중 실패를 모두 failure result로 변환한다. Cancellation과 다른 `BaseException` subclass는 전파한다.

```python
import asyncio
from typing import Awaitable
from tbot223_base import ExceptionTrackerDecorator


@ExceptionTrackerDecorator().wrap_awaitable
def factory() -> Awaitable[int]:
    raise ValueError("before creating awaitable")


result = asyncio.run(factory())
assert result.is_failure
```

Decorator의 실패 결과는 내부 진단 데이터이며 masking만으로 public-safe해지지 않는다.

Generator와 async generator의 iteration은 decorated call이 반환된 뒤 실행되므로, 이후 iteration 중 발생한 exception은 이 decorator가 변환하지 않는다.
