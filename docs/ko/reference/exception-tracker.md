[English](../../en/reference/exception-tracker.md)

> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.0.1"`.

# ExceptionTracker 레퍼런스

이 문서는 `ExceptionTracker`, `ExceptionTrackerDecorator`, masking, bounded context snapshot 정책을 설명한다.

## 두 가지 payload 경로

| Path | Methods | Intended use |
| --- | --- | --- |
| Debug-heavy | `get_exception_info()`, `get_exception_return()` | traceback과 context metadata가 필요한 내부 진단. |
| Public-safe | `get_public_exception_info()`, `get_public_exception_return()` | API 응답, UI, untrusted boundary. |

Public-safe 경로는 traceback text, local variables, params, system information을 수집하지 않는다.

## Debug context snapshot

Debug 경로는 `user_input`, `params.args`, `params.kwargs`, origin frame의 `local_variables`를 raw object reference가 아니라 제한된 snapshot으로 저장한다.

기본 snapshot 제한값:

| Constant | Value |
| --- | --- |
| `CONTEXT_MAX_REPR_LENGTH` | `200` |
| `CONTEXT_MAX_ITEMS` | `20` |
| `CONTEXT_MAX_DEPTH` | `2` |

작은 primitive는 직접 보존한다. 긴 문자열, bytes-like 값, collection, custom object는 `type`, `length`, `preview`, `repr`, `shape`, `truncated` 같은 metadata로 요약한다.

## Mask preset

| Preset | Effect |
| --- | --- |
| `default` | `input_context.local_variables`를 mask한다. |
| `private` | user input, params, local variables를 mask한다. |
| `user_input` | `input_context.user_input`을 mask한다. |
| `params` | params와 local variables를 mask한다. |
| `traceback` | causes, traceback text, traceback frames를 mask한다. |
| `system_info` | system information을 mask한다. |

명시적 `mask_paths`로 `"location.origin"` 같은 dot path나 `("error", "message")` 같은 tuple path도 mask할 수 있다.

## Public example

```python
from tbot223_base.tbot223_Exception import ExceptionTracker

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

`ExceptionTrackerDecorator`는 callable을 감싸고 uncaught exception을 failure `Result`로 변환한다. 성공 시에는 원래 반환 타입을 유지하고, 실패 시에는 `Result`를 반환한다.
