[한국어 (Korean)](../../ko/reference/result.md)

> Runtime baseline: package version 1.0.0rc2 (`tbot223_base.__version__ == "1.0.0rc2"`).

# Result Reference

This reference covers `ResultStatus`, `Result`, and `ResultUnwrapException`.

## ResultStatus

`ResultStatus` is a string enum with three states.

| Value | Meaning |
| --- | --- |
| `ResultStatus.SUCCESS` | The operation completed successfully. |
| `ResultStatus.FAILURE` | The operation failed. |
| `ResultStatus.CANCELLED` | The operation was cancelled or not executed. |

`ResultStatus.normalize()` accepts a `ResultStatus`, tri-state shorthand values (`bool` or `None`), or a valid status string.

## Result

`Result[T]` is an immutable tuple-like container with these fields.

| Field | Type | Meaning |
| --- | --- | --- |
| `status` | `ResultStatus` | The normalized operation state. |
| `error` | `Optional[str]` | Human-readable error text. |
| `context` | `Optional[str]` | Operation context. |
| `data` | `T` | Payload returned by the operation. |

The `success=` constructor argument is supported as tri-state shorthand. New code should prefer `status=ResultStatus...` when it needs the explicit enum form.

Use `Result[T]` when the payload type is known. `unwrap()` and `expect()` return `T`, and `unwrap_or(default)` returns either `T` or the default value type.

## Import Path

Import `Result`, `ResultStatus`, and `ResultUnwrapException` from `tbot223_base.result`.

## Predicates

- `result.success`: tri-state shorthand property returning `True`, `False`, or `None`.
- `result.is_success`: `True` only for `ResultStatus.SUCCESS`.
- `result.is_failure`: `True` only for `ResultStatus.FAILURE`.
- `result.is_cancelled`: `True` only for `ResultStatus.CANCELLED`.

## Unwrap Helpers

- `unwrap()`: returns `T` for success; raises `ResultUnwrapException` otherwise.
- `expect(msg="")`: returns `T` for success; raises with a custom message otherwise.
- `unwrap_or(default)`: returns `T` for success; otherwise returns `default`.

## Example

```python
from tbot223_base.result import Result, ResultStatus

result: Result[dict[str, str]] = Result(ResultStatus.FAILURE, "not found", "LoadProfile", None)

if result.is_failure:
    fallback = result.unwrap_or({"name": "anonymous"})
    print(fallback)
```
