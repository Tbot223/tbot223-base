[한국어 (Korean)](../../ko/reference/exception-tracker.md)

> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.0.1"`.

# ExceptionTracker Reference

This reference covers `ExceptionTracker`, `ExceptionTrackerDecorator`, masking, and bounded context snapshots.

## Two Payload Paths

| Path | Methods | Intended use |
| --- | --- | --- |
| Debug-heavy | `get_exception_info()`, `get_exception_return()` | Internal diagnostics where traceback and context metadata are useful. |
| Public-safe | `get_public_exception_info()`, `get_public_exception_return()` | API responses, UI surfaces, or untrusted boundaries. |

The public-safe path does not collect traceback text, local variables, params, or system information.

## Debug Context Snapshot

The debug path stores `user_input`, `params.args`, `params.kwargs`, and origin-frame `local_variables` as bounded snapshots rather than raw object references.

Default snapshot limits:

| Constant | Value |
| --- | --- |
| `CONTEXT_MAX_REPR_LENGTH` | `200` |
| `CONTEXT_MAX_ITEMS` | `20` |
| `CONTEXT_MAX_DEPTH` | `2` |

Small primitives are kept directly. Long strings, bytes-like values, collections, and custom objects are summarized with metadata such as `type`, `length`, `preview`, `repr`, `shape`, and `truncated`.

## Mask Presets

| Preset | Effect |
| --- | --- |
| `default` | Masks `input_context.local_variables`. |
| `private` | Masks user input, params, and local variables. |
| `user_input` | Masks `input_context.user_input`. |
| `params` | Masks params and local variables. |
| `traceback` | Masks causes, traceback text, and traceback frames. |
| `system_info` | Masks system information. |

Explicit `mask_paths` can also mask dot paths such as `"location.origin"` or tuple paths such as `("error", "message")`.

## Public Example

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

`ExceptionTrackerDecorator` wraps a callable and converts uncaught exceptions into failure `Result` objects. It preserves the original return type on success and returns `Result` on failure.
