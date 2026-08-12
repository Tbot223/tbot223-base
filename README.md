[한국어 (Korean)](README.ko.md)

> **Rebuilding status — `1.0.0a1`:** This repository is being rebuilt before any public release. It is not recommended for production use, and API, payload, and release guarantees may change without compatibility support. Read [Rebuilding](docs/en/rebuilding.md) before adopting it.
> Runtime baseline: package version `1.0.0a1` (`tbot223_base.__version__ == "1.0.0a1"`).

# tbot223-base

`tbot223-base` is a small Python base package for exchanging operation results and safe exception payloads across function and module boundaries.

It provides two core pieces:

- `Result` and `ResultStatus` for explicit `success`, `failure`, and `cancelled` outcomes.
- `ExceptionTracker` for separating internal debug diagnostics from public-safe error payloads.

## Design Intent

`tbot223-base` is shaped by Python boundary-handling needs, not an attempt to reproduce another language's API. `Result` is a Python-style exchange protocol: a small value shape that lets functions pass status, data, context, and error text without guessing how the caller wants to handle the outcome.

`ExceptionTracker` keeps rich internal diagnostics available while producing a smaller public payload that avoids traceback, local-variable, system-information, and raw-exception leakage.

## Current Status

The prior release line was withdrawn because its type and safety contracts were ahead of their implementation. The current alpha rebuild makes `Result.data` required, removes raw reconstruction helpers, defers debug system collection, and validates documentation as executable contract material. The detailed rationale, current guarantees, and next gates are in [Rebuilding](docs/en/rebuilding.md).

## Who This Is For

This package is for codebases that want a small typed result shape at function, service, worker, or module boundaries, and public-safe error payloads for APIs, UI surfaces, bot responses, or other untrusted boundaries.

It is not a logging, tracing, metrics, observability, pattern-matching, or monadic-result framework. It also does not replace ordinary Python exceptions inside purely local control flow.

## Local Development

`1.0.0a1` is not a public install target. Work from a source checkout instead.

```bash
python -m pip install -e ".[test,type,lint]"
pytest -q
python -m ruff check .
python -m ruff format --check .
```

## Quickstart

Create and inspect a successful result.

```python
from tbot223_base.result import Result

result = Result.ok({"user_id": 1}, context="FetchProfile")

if result.is_success:
    print(result.unwrap())
```

Return a public-safe exception payload. This path does not collect debug system information.

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
        retryable=False,
    )
    print(result.data)
```

## Documentation

- [Rebuilding status](docs/en/rebuilding.md)
- [English docs](docs/en/README.md)
- [Korean docs](docs/ko/README.md)
- [Result reference](docs/en/reference/result.md)
- [ExceptionTracker reference](docs/en/reference/exception-tracker.md)
- [Package and CI guide](docs/en/guides/package-and-ci.md)
- [API contract](docs/contracts/en/human/api-contract.md)
