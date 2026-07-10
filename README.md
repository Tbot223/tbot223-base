[한국어 (Korean)](README.ko.md)

> Runtime baseline: package version 1.0.0 (`tbot223_base.__version__ == "1.0.0"`).

# tbot223-base

`tbot223-base` is a small Python base package for exchanging operation results and safe exception payloads across function and module boundaries.

It provides two core pieces:

- `Result` and `ResultStatus` for explicit `success`, `failure`, and `cancelled` outcomes.
- `ExceptionTracker` for separating internal debug diagnostics from public-safe error payloads.

## Design Intent

`tbot223-base` was shaped by Python boundary-handling needs, not by an attempt to reproduce another language's API.

Rust's `Result` can be a useful comparison point for readers, but it is not the source model or compatibility target for this package. Here, `Result` is a Python-style exchange protocol: a small value shape that lets functions pass status, data, context, and error text without guessing how the caller wants to handle the outcome.

`ExceptionTracker` exists for safe error handling at boundaries. It does not make errors disappear; it keeps rich internal diagnostics available while producing a smaller public payload that avoids traceback, local variable, system, or raw exception leakage.

## Who This Is For

This package fits codebases that want:

- a stable result shape for function, service, worker, or module boundaries.
- a lightweight way to return success, failure, and cancellation without inventing a new dictionary shape in each layer.
- public-safe error payloads for APIs, UI surfaces, bot responses, or other untrusted boundaries.
- debug diagnostics that can stay richer than public responses.
- a small typed utility package rather than a framework.

It is especially useful when an operation result is part of the interface between components, not just a local implementation detail.

## Trade-offs

`Result` makes outcomes explicit, but that also means callers and callees must agree to pass and inspect a structured value. For very small scripts or code where normal exceptions are already the clearest control flow, this can be unnecessary ceremony.

`ExceptionTracker` intentionally separates public and debug payloads. That is safer for public boundaries, but it also means public responses will not contain raw exception messages, traceback frames, local variables, or system information unless you explicitly provide safe public text.

This package is not:

- a Rust-compatible `Result` implementation.
- a pattern-matching or monadic result framework.
- a logging, tracing, metrics, or observability system.
- a replacement for Python exceptions inside purely local control flow.

## Installation

```bash
python -m pip install "tbot223-base==1.0.0"
```

For the latest stable release without pinning a version, use `python -m pip install tbot223-base`.

For local development from a source checkout:

```bash
python -m pip install -e ".[test,type]"
```

## Quickstart

Create and inspect a result.

```python
from tbot223_base.result import Result, ResultStatus

result: Result[dict[str, int]] = Result(
    status=ResultStatus.SUCCESS,
    error=None,
    context="FetchProfile",
    data={"user_id": 1},
)

if result.is_success:
    print(result.unwrap())
```

Return a public-safe exception payload.

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

User-facing docs:

- [English docs](docs/en/README.md)
- [Korean docs](docs/ko/README.md)
- [Getting Started](docs/en/guides/getting-started.md)
- [Executable examples](docs/en/guides/examples.md)
- [Result reference](docs/en/reference/result.md)
- [ExceptionTracker reference](docs/en/reference/exception-tracker.md)
- [API contract](docs/contracts/en/human/api-contract.md)

Repository maintenance docs:

- [Package and CI guide](docs/en/guides/package-and-ci.md)
- [Release notes](docs/en/release-notes.md)
