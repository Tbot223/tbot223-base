[한국어 (Korean)](../../ko/reference/exception-tracker.md)

> Runtime baseline: package version 1.0.0 (`tbot223_base.__version__ == "1.0.0"`).

# ExceptionTracker Reference

This reference covers `ExceptionTracker`, `ExceptionTrackerDecorator`, masking, and safe context capture.

For stability rules around debug/public payload shapes, see the [API contract](../../contracts/en/human/api-contract.md).

## Two Payload Paths

| Path | Methods | Intended use |
| --- | --- | --- |
| Debug-heavy | `get_exception_info()`, `get_exception_return()` | Internal diagnostics where traceback and context metadata are useful. |
| Public-safe | `get_public_exception_info()`, `get_public_exception_return()` | API responses, UI surfaces, or untrusted boundaries. |

The public-safe path does not collect traceback text, local variables, params, or system information.

## Public Tag Safety

Public tag keys are normalized to strings, and tag values are copied into a JSON-safe structure instead of retaining caller-owned references.

The public tag copy policy keeps exact built-in `None`, `bool`, `int`, finite `float`, and bounded `str` values. Plain `list` and `tuple` values become copied lists, and plain `dict` values become dictionaries with normalized string keys. Each collection keeps at most `CONTEXT_MAX_ITEMS` items and nesting is limited by `PUBLIC_TAG_MAX_DEPTH`. Unsupported, oversized, non-finite, cyclic, or too-deep values become `"<BLOCKED>"`.

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

Small primitives and primitive-only `list`/`tuple` values are copied. Top-level `dict` values are copied only when they fit the item limit. Deep, bytes-like, or custom object values are replaced with `"<BLOCKED>"` instead of metadata summaries.

## System Info

Debug payloads include system information for internal diagnostics. Environment variables are copied only when the key is a small string and the value is a small primitive or shallow tuple/list of small primitives; collection stops at `ENVIRONMENT_VARIABLE_MAX_COUNT` entries. Small environment values can still be sensitive, so mask `system_info` before exposing debug payloads outside a trusted boundary.

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

`ExceptionTrackerDecorator` wraps synchronous and coroutine functions and converts uncaught exceptions into failure `Result` objects. A synchronous function returns its original value or a failure `Result`; coroutine functions and awaitable results resolve to their original value or a failure `Result` when awaited.

Generator and async-generator iteration happens after the decorated call returns, so exceptions raised during later iteration are not converted by this decorator.
