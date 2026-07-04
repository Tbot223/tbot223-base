[한국어 (Korean)](../../ko/guides/getting-started.md)

> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.0.1"`.

# Getting Started

This guide shows the smallest useful path for importing `tbot223-base` from a repository checkout.

## Prerequisites

- Python is available in the environment.
- The repository checkout is on `PYTHONPATH` or the current working directory is the repository root.
- The current repository does not define packaging metadata, so this guide does not assume `pip install`.

## Result Basics

```python
from tbot223_base.tbot223_Result import Result, ResultStatus

result: Result[dict[str, str]] = Result(
    status=ResultStatus.SUCCESS,
    error=None,
    context="LoadConfig",
    data={"mode": "dev"},
)

if result.is_success:
    print(result.unwrap())
```

Use `ResultStatus.SUCCESS`, `ResultStatus.FAILURE`, and `ResultStatus.CANCELLED` for new code. The legacy `success=` constructor argument is still supported for compatibility.

## Public Exception Payload

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
        public_context="Calculator.Divide",
        tags={"layer": "service"},
        retryable=False,
    )
    print(result.data)
```

Use the public path for API responses, UI surfaces, or any boundary where raw exception details should not be exposed.

## Debug Exception Payload

```python
from tbot223_base.tbot223_Exception import ExceptionTracker

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
