[한국어 (Korean)](../../ko/reference/result.md)

> Runtime baseline: unreleased working tree based on `1.0.0a1`; these fixes are not part of the existing release tag.

# Result Reference

This alpha reference covers `ResultStatus`, `Result`, and `ResultUnwrapException`.

## ResultStatus

`ResultStatus` is a string enum with three values: `SUCCESS`, `FAILURE`, and `CANCELLED`. `ResultStatus.normalize()` accepts the enum, a tri-state shorthand (`True`, `False`, or `None`), or a valid status string.

## Result Shape

`Result[T]` is an immutable tuple-like value in this order: `(status, error, context, data)`. It preserves indexing, unpacking, structural pattern matching, and tuple equality.

| Field | Type | Meaning |
| --- | --- | --- |
| `status` | `ResultStatus` | Normalized outcome state. |
| `error` | `Optional[str]` | Human-readable error text. |
| `context` | `Optional[str]` | Operation context. |
| `data` | `T` | Required payload for every state. |

`data` must always be provided, including a deliberate `None` payload. `_make()` and `_replace()` are not public API and are unavailable so a result cannot silently change its payload type.

## Construction

Prefer typed factories for new code.

```python
from tbot223_base.result import Result

success = Result.ok({"name": "Ada"}, context="LoadProfile")
failure = Result.failure(None, error="not found", context="LoadProfile")
cancelled = Result.cancelled(None, context="LoadProfile")
```

Explicit construction is also supported when a caller needs the normalized status form.

```python
from tbot223_base.result import Result, ResultStatus

result: Result[int] = Result(ResultStatus.SUCCESS, None, "Compute", 42)
```

The `success=` input and `result.success` property remain tri-state shorthand during this alpha. `result.success` returns `True`, `False`, or `None`; `is_success`, `is_failure`, and `is_cancelled` are boolean predicates.

## Unwrap Helpers

- `unwrap()` returns `T` only for success.
- `expect(msg="")` returns `T` only for success and records `msg` when it fails.
- `unwrap_or(default)` returns `T` for success or the given default otherwise.

`unwrap()` and `expect()` raise `ResultUnwrapException` for non-success results. Its fixed message never stringifies stored `error`, `context`, or `data`; those original values remain available as exception attributes.

## Import Path

Import `Result`, `ResultStatus`, and `ResultUnwrapException` from `tbot223_base.result`.

## Copying and Static Types

`copy.copy`, `copy.deepcopy`, and standard pickle round trips preserve the result fields when the payload supports those operations. Shallow copies share the payload; deep copies copy it. Reconstruction still requires explicit data and does not restore `_make` or `_replace`.

The fixed tuple type preserves field types through literal indexing (including negative indexes) and unpacking. Dynamic indexes and slices have normal tuple typing. The container is immutable; payload mutability is unchanged.
