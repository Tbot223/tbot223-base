[English](../../en/reference/exception-tracker.md)

> 런타임 기준: package version 1.0.0 (`tbot223_base.__version__ == "1.0.0"`).

# ExceptionTracker 레퍼런스

이 문서는 `ExceptionTracker`, `ExceptionTrackerDecorator`, masking, safe context capture 정책을 설명한다.

Debug/public payload shape의 안정성 규칙은 [API 계약](../../contracts/ko/human/api-contract.md)을 기준으로 본다.

## 두 가지 payload 경로

| Path | Methods | Intended use |
| --- | --- | --- |
| Debug-heavy | `get_exception_info()`, `get_exception_return()` | traceback과 context metadata가 필요한 내부 진단. |
| Public-safe | `get_public_exception_info()`, `get_public_exception_return()` | API 응답, UI, untrusted boundary. |

Public-safe 경로는 traceback text, local variables, params, system information을 수집하지 않는다.

## Public tag safety

Public tag key는 string으로 정규화하고, value는 caller-owned reference를 보존하지 않도록 JSON-safe structure로 복사한다.

Public tag copy 정책은 exact built-in `None`, `bool`, `int`, finite `float`, bounded `str` 값을 유지한다. Plain `list`와 `tuple`은 복사된 list가 되고, plain `dict`는 정규화된 string key를 가진 dictionary가 된다. Collection마다 `CONTEXT_MAX_ITEMS`개까지 유지하며 nesting은 `PUBLIC_TAG_MAX_DEPTH`로 제한한다. 지원하지 않거나, 너무 크거나, non-finite이거나, 순환하거나, 너무 깊은 값은 `"<BLOCKED>"`로 대체한다.

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

작은 primitive와 primitive-only `list`/`tuple` 값만 복사한다. Top-level `dict` 값은 item 제한을 만족할 때만 복사한다. 깊은 nested 값, bytes-like 값, custom object는 metadata로 요약하지 않고 `"<BLOCKED>"`로 대체한다.

## System info

Debug payload는 내부 진단용 system information을 포함한다. 환경변수는 key가 작은 문자열이고 value가 작은 primitive 또는 작은 primitive만 담은 얕은 tuple/list일 때만 복사하며, `ENVIRONMENT_VARIABLE_MAX_COUNT`개에서 수집을 멈춘다. 작은 환경변수 값도 민감할 수 있으므로 trusted boundary 밖으로 debug payload를 보낼 때는 `system_info`를 mask해야 한다.

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

`ExceptionTrackerDecorator`는 synchronous function과 coroutine function을 감싸고 uncaught exception을 failure `Result`로 변환한다. Synchronous function은 원래 value 또는 failure `Result`를 반환하고, coroutine function과 awaitable result는 await했을 때 원래 value 또는 failure `Result`로 resolve된다.

Generator와 async generator의 iteration은 decorated call이 반환된 뒤 실행되므로, 이후 iteration 중 발생한 exception은 이 decorator가 변환하지 않는다.
