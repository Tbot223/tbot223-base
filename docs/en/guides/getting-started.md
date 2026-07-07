[한국어 (Korean)](../../ko/guides/getting-started.md)

> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.1.0"`.

# Getting Started

This guide shows the smallest useful path for importing `tbot223-base` from a repository checkout or editable install.

## Design Intent

`tbot223-base` was shaped by Python boundary-handling needs, not by an attempt to reproduce another language's API. Rust's `Result` can be a useful comparison point, but it is not the source model or compatibility target for this package.

Its `Result` type is a Python-style exchange protocol for passing status, data, context, and error text between functions.

`ExceptionTracker` is for safe error handling at boundaries. Use it when you want internal diagnostics without exposing traceback, local variables, system information, or raw exception details through public payloads.

## Prerequisites

- Python is available in the environment.
- The repository checkout is on `PYTHONPATH`, the current working directory is the repository root, or the checkout is installed in editable mode.
- The repository defines `pyproject.toml` packaging metadata for local package tooling.

## Import Paths

Use the canonical module paths for new code:

- `tbot223_base.result`
- `tbot223_base.exception_tracker`

## Result Basics

```python
from tbot223_base.result import Result, ResultStatus

result: Result[dict[str, str]] = Result(
    status=ResultStatus.SUCCESS,
    error=None,
    context="LoadConfig",
    data={"mode": "dev"},
)

if result.is_success:
    print(result.unwrap())
```

Use `ResultStatus.SUCCESS`, `ResultStatus.FAILURE`, and `ResultStatus.CANCELLED` for explicit status handling. The `success=` constructor argument is also supported as tri-state shorthand.

## Public Exception Payload

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
        public_context="Calculator.Divide",
        tags={"layer": "service"},
        retryable=False,
    )
    print(result.data)
```

Use the public path for API responses, UI surfaces, or any boundary where raw exception details should not be exposed.

## Debug Exception Payload

```python
from tbot223_base.exception_tracker import ExceptionTracker

tracker = ExceptionTracker()

try:
    1 / 0
except Exception as error:
    result = tracker.get_exception_info(
        error,
        mask_presets=("private", "traceback", "system_info"),
    )
    print(result.error)
```

The debug path can include traceback and context metadata. Context values are copied only when small and safe; heavy values are replaced with `"<BLOCKED>"`.

## Verify

```bash
pytest
```
