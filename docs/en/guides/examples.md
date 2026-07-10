[한국어 (Korean)](../../ko/guides/examples.md)

> Runtime baseline: package version 1.0.0rc1 (`tbot223_base.__version__ == "1.0.0rc1"`).

# Executable Examples

This guide lists the standalone example scripts under `examples/` and shows how to run each one from a source checkout.

## Prerequisites

- Run commands from the repository root.
- Use Python 3.10 or newer.
- No package install is required when running from this checkout; each script adds the repository root to `sys.path`.
- Result examples live under `examples/result/`; exception boundary examples live under `examples/exception_tracker/`.

## Scripts

| Script | Shows |
| --- | --- |
| `examples/result/result_status_flow.py` | `ResultStatus.SUCCESS`, `ResultStatus.FAILURE`, `ResultStatus.CANCELLED`, `unwrap_or()`, and `expect()`. |
| `examples/exception_tracker/public_exception_payload.py` | Public-safe exception payloads for API, UI, bot, or other untrusted boundaries. |
| `examples/exception_tracker/debug_exception_payload.py` | Masked debug payloads with location, context, traceback-frame count, and masked system information. |
| `examples/exception_tracker/decorator_boundary.py` | `ExceptionTrackerDecorator` converting uncaught function-boundary exceptions into failure `Result` objects. |
| `examples/exception_tracker/threaded_shared_tracker.py` | One shared `ExceptionTracker` instance used across `ThreadPoolExecutor` workers. |

## Run

```bash
python examples/result/result_status_flow.py
python examples/exception_tracker/public_exception_payload.py
python examples/exception_tracker/debug_exception_payload.py
python examples/exception_tracker/decorator_boundary.py
python examples/exception_tracker/threaded_shared_tracker.py
```

Some output includes generated IDs, timestamps, local file paths, or traceback locations, so exact text may differ between machines.

## Use as Starting Points

Copy the shape of the script that matches your boundary:

- Use `examples/result/result_status_flow.py` when a function should return an explicit outcome.
- Use `examples/exception_tracker/public_exception_payload.py` when the payload may leave a trusted process boundary.
- Use `examples/exception_tracker/debug_exception_payload.py` when internal diagnostics should stay rich but masked.
- Use `examples/exception_tracker/decorator_boundary.py` when a small function wrapper should convert uncaught exceptions to `Result` values.
- Use `examples/exception_tracker/threaded_shared_tracker.py` when a tracker instance is shared across thread workers.

## Verify

```bash
python -m py_compile examples/result/result_status_flow.py examples/exception_tracker/public_exception_payload.py examples/exception_tracker/debug_exception_payload.py examples/exception_tracker/decorator_boundary.py examples/exception_tracker/threaded_shared_tracker.py
```
