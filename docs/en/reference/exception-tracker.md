[한국어 (Korean)](../../ko/reference/exception-tracker.md)

> Runtime baseline: unreleased working tree based on `1.0.0a1`; these fixes are not part of the existing release tag.

# ExceptionTracker Reference

This reference covers `ExceptionTracker`, `ExceptionTrackerDecorator`, masking, and safe context capture.

For stability rules around debug/public payload shapes, see the [API contract](../../contracts/en/human/api-contract.md).

## Two Payload Paths

| Path | Methods | Intended use |
| --- | --- | --- |
| Debug-heavy | `get_exception_info()`, `get_exception_return()` | Internal diagnostics where traceback and context metadata are useful. |
| Public-safe | `get_public_exception_info()`, `get_public_exception_return()` | API responses, UI surfaces, or untrusted boundaries. |

The public-safe path does not collect traceback text, local variables, params, or system information. Constructing a tracker and calling `get_exception_location()` also leave the deferred system snapshot untouched.

## Public Tag Safety

Public tag keys are normalized to strings, and tag values are copied into a JSON-safe structure instead of retaining caller-owned references.

The public tag copy policy keeps exact built-in `None`, `bool`, `int`, finite `float`, and bounded `str` values. Integers in tag values, normalized keys, and error codes have at most `PUBLIC_MAX_INTEGER_BITS` (512) magnitude bits. Oversized integer values become `"<BLOCKED>"`, unsupported or oversized keys are dropped, and oversized error codes use the default code. String error codes and all normalized keys are limited to 200 characters. Plain `list` and `tuple` values become copied lists, and plain `dict` values become dictionaries with normalized string keys. Each collection keeps at most `CONTEXT_MAX_ITEMS` items and nesting is limited by `PUBLIC_TAG_MAX_DEPTH`. Unsupported, oversized, non-finite, cyclic, or too-deep values become `"<BLOCKED>"`.

Tag copying shares `PUBLIC_TAG_MAX_NODES` (256) value visits across the entire tags mapping, including repeated references. A collection that cannot be completed within the remaining budget becomes `"<BLOCKED>"`; later values may also be blocked. Small tags retain their existing shape. This is a traversal budget, not a byte limit on caller-supplied public messages or context.

Final public fields `id`, `timestamp`, `error.code`, and `error.message` are non-optional. `status` is the literal `"failure"`, `success` is the literal `False`, and only `retryable` is nullable.

## Import Path

Import `ExceptionTracker` and `ExceptionTrackerDecorator` from `tbot223_base.exception_tracker`.

## Debug Context Capture

The debug path stores `user_input`, `params.args`, `params.kwargs`, and origin-frame `local_variables` as safe copies rather than raw object references.

Default safety limits:

| Constant | Value |
| --- | --- |
| `CONTEXT_MAX_VALUE_LENGTH` | `200` |
| `CONTEXT_MAX_ITEMS` | `20` |
| `PUBLIC_TAG_MAX_DEPTH` | `3` |
| `PUBLIC_MAX_INTEGER_BITS` | `512` |
| `PUBLIC_TAG_MAX_NODES` | `256` |

Small primitives and primitive-only `list`/`tuple` values are copied. Top-level `dict` values are copied only when they fit the item limit. Deep, bytes-like, or custom object values are replaced with `"<BLOCKED>"` instead of metadata summaries.

## System Info

Debug payloads collect one system snapshot lazily on the first debug-heavy call, then copy it into each payload; neither `started_at` nor `now` triggers another system collection. Environment variables are copied only when the key is a small string and the value is a small primitive or shallow tuple/list of small primitives; collection stops at `ENVIRONMENT_VARIABLE_MAX_COUNT` entries. Small environment values can still be sensitive. Debug payloads remain internal diagnostics even when masked; use the public methods for external responses.

## Thread Concurrency

`ExceptionTracker` instances are intended to be reusable across concurrent thread calls. Debug payloads are created fresh per call, and startup system information is copied into each payload rather than shared by reference.

Returned payload dictionaries remain mutable. If callers mutate or share returned payloads across threads, they should provide their own synchronization. `Result` is immutable as a container, but `Result.data` can still contain mutable user payloads.

This guarantee is thread-focused. It does not add multiprocessing behavior or cross-process shared-state guarantees.

## Mask Presets

| Preset | Effect |
| --- | --- |
| `default` | Masks `input_context.local_variables`. |
| `private` | Masks user input, params, and local variables. |
| `user_input` | Masks `input_context.user_input`. |
| `params` | Masks params and local variables. |
| `traceback` | Masks causes, traceback text, and traceback frames. |
| `system_info` | Masks system information. |

Explicit `mask_paths` can also mask dot paths such as `"location.origin"` or tuple paths such as `("error", "message")`. When a debug `Result.context` string is derived from `location.origin`, the masked origin is reflected there as well.

Mask presets select fields; they do not remove every occurrence of a secret. In particular, `("private", "traceback", "system_info")` leaves raw error messages and source locations.

If debug capture or masking fails, the result contains only `{"tracker_failure": True, "message": <fixed generic message>}` in `data`; no original exception, traceback, or input data is included. Fallback paths do not write to stdout or stderr. Callers can distinguish tracker failure with `result.data.get("tracker_failure") is True`.

## Public Example

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

`ExceptionTrackerDecorator` automatically wraps synchronous and coroutine functions. For an awaitable-returning callable its static return type is `Awaitable[T | Result[object]] | Result[object]`: a synchronous factory can fail before it produces an awaitable. Existing automatic runtime behavior is preserved, but callers must narrow that union before awaiting.

Use `@decorator.wrap_awaitable` for coroutine functions or synchronous awaitable factories when every call must return a coroutine. This wrapper defers the original call until awaited and converts both factory-call failures and await failures into a failure result. Cancellation and other `BaseException` subclasses propagate.

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

Decorator failure results are debug diagnostics. Masking them does not make them public-safe.

Generator and async-generator iteration happens after the decorated call returns, so exceptions raised during later iteration are not converted by this decorator.
