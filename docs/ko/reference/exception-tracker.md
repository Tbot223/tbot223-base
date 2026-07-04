[English](../../en/reference/exception-tracker.md)

> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.0.1"`.

# ExceptionTracker 레퍼런스

이 문서는 `ExceptionTracker`, `ExceptionTrackerDecorator`, masking, safe context capture 정책을 설명한다.

## 두 가지 payload 경로

| Path | Methods | Intended use |
| --- | --- | --- |
| Debug-heavy | `get_exception_info()`, `get_exception_return()` | traceback과 context metadata가 필요한 내부 진단. |
| Public-safe | `get_public_exception_info()`, `get_public_exception_return()` | API 응답, UI, untrusted boundary. |

Public-safe 경로는 traceback text, local variables, params, system information을 수집하지 않는다.

## Debug context capture

Debug 경로는 `user_input`, `params.args`, `params.kwargs`, origin frame의 `local_variables`를 raw object reference가 아니라 안전한 복사본으로 저장한다.

기본 context 제한값:

| Constant | Value |
| --- | --- |
| `CONTEXT_MAX_VALUE_LENGTH` | `200` |
| `CONTEXT_MAX_ITEMS` | `20` |

작은 primitive와 primitive-only `list`/`tuple` 값만 복사한다. Top-level `dict` 값은 item 제한을 만족할 때만 복사한다. 깊은 nested 값, bytes-like 값, custom object는 metadata로 요약하지 않고 `"<BLOCKED>"`로 대체한다.

## System info

Debug payload는 내부 진단용 system information을 포함한다. 환경변수는 key가 작은 문자열이고 value가 작은 primitive 또는 작은 primitive만 담은 얕은 tuple/list일 때만 복사하며, `ENVIRONMENT_VARIABLE_MAX_COUNT`개에서 수집을 멈춘다. 작은 환경변수 값도 민감할 수 있으므로 trusted boundary 밖으로 debug payload를 보낼 때는 `system_info`를 mask해야 한다.

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
