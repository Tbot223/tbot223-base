[한국어 (Korean)](../../ko/human/api-contract.md)

> Contract revision: 2026-09-09 (unreleased boundary fixes).

# API Contract

> Contract for public import paths, `Result`, and `ExceptionTracker` payload shapes.

## 1. Goal

- Define the rebuilding alpha public API around Python-conventional canonical module paths.
- Define `Result` as an independently shaped Python boundary exchange protocol, not as a Rust compatibility target.
- Treat debug and public exception payloads as explicit contracts, not incidental dictionaries.
- Preserve the safety boundary between internal diagnostics and public-facing error payloads.
- Keep executable tests aligned with the contract whenever API or payload behavior changes.

## 2. Scope

This contract applies to:

- Canonical import paths under `tbot223_base`.
- `ResultStatus`, `Result`, and `ResultUnwrapException`.
- `ExceptionTracker`, `ExceptionTrackerDecorator`, and returned debug/public payload structures.
- Tests and CI jobs that validate the API contract.

This contract does not apply to:

- Private helper names that are not imported as public API.
- Exact wording of internal error strings unless tests explicitly pin them.
- Presentation-only documentation wording.

## 3. Public Import Paths

Public code MUST use these canonical paths:

- `tbot223_base.result`
- `tbot223_base.exception_tracker`

Package-level exports in `tbot223_base.__init__` SHOULD expose the primary public API objects.

## 4. Result Contract

`Result` MUST remain an immutable tuple-like outcome container with these fields:

| Field | Meaning |
| --- | --- |
| `status` | Normalized `ResultStatus`. |
| `error` | Optional human-readable error text. |
| `context` | Optional operation context. |
| `data` | Operation payload. |

`ResultStatus` MUST keep the string values `success`, `failure`, and `cancelled`.

`Result.data` MUST be supplied for every result state, including an intentional `None`. `Result.ok(data)`, `Result.failure(data, ...)`, and `Result.cancelled(data, ...)` are the preferred typed construction APIs. `Result` MUST retain tuple-like read behavior, but raw `_make()` and `_replace()` reconstruction helpers MUST NOT be exposed.

`Result` MUST be documented as a boundary exchange shape for Python code. If Rust's `Result` is mentioned, it MUST be treated only as a comparison point, not as the source model or compatibility target.

The `success=` input and `result.success` property SHOULD remain available as supported tri-state shorthand APIs until a documented breaking change removes them.

Standard copy/deepcopy and pickle reconstruction MUST retain the validated result fields when the payload supports them. Literal tuple indexing and unpacking MUST preserve field types.

## 5. Exception Payload Contract

`ExceptionTracker` has two payload paths.

| Path | Methods | Boundary |
| --- | --- | --- |
| Debug-heavy | `get_exception_info()`, `get_exception_return()` | Trusted internal diagnostics. |
| Public-safe | `get_public_exception_info()`, `get_public_exception_return()` | API responses, UI surfaces, and untrusted boundaries. |

Debug payloads MUST include structured failure metadata, location information, copied safe context, chained causes, traceback data, and system information unless masked or unavailable. One shared system snapshot MUST be collected lazily on the first debug-heavy call and reused thereafter; public-safe methods and location lookup MUST NOT collect it.

Public payloads MUST remain lightweight and MUST NOT include traceback text, traceback frames, local variables, params, user input, or system information.

## 6. Public Payload Shape

The public payload MUST use this top-level shape:

| Key | Meaning |
| --- | --- |
| `id` | Unique payload identifier. |
| `status` | Failure status string. |
| `success` | `False`. |
| `timestamp` | UTC timestamp string. |
| `error` | Public `code` and `message`. |
| `tags` | Public metadata with string keys. |
| `retryable` | Optional retry hint. |

Raw exception messages MUST NOT be exposed through the public payload unless the caller explicitly passes a safe `public_message`.

Public tag keys MUST be normalized to bounded strings. Public tag values MUST be copied into a bounded JSON-safe shape without retaining caller-owned object references. Unsupported, oversized, non-finite, cyclic, or too-deep values MUST be replaced with `"<BLOCKED>"`.

`ExceptionTrackerDecorator` MUST convert uncaught exceptions from synchronous functions, coroutine functions, and awaited results into failure `Result` objects. Exceptions raised during later generator or async-generator iteration are outside this decorator contract.

For automatic wrapping, awaitable-returning callables MUST expose the possibility of an immediate `Result` in their static return type. `wrap_awaitable()` MUST always return a coroutine and convert failures from both the deferred function call and its await. Cancellation and other `BaseException` subclasses MUST propagate.

Public integers MUST have at most 512 magnitude bits. String error codes and all normalized tag keys MUST have at most 200 characters. Unsupported keys MUST be dropped; oversized tag values MUST be blocked; invalid or oversized error codes MUST use the default code. Public tag copying MUST share a 256-value traversal budget across nested values and repeated references. Collections that cannot complete within the budget MUST become `"<BLOCKED>"`.

Final public field types MUST match the concrete payload: identifiers and messages are strings, status is `Literal["failure"]`, success is `Literal[False]`, and only retryable is nullable.

## 7. Debug Safety Rules

Debug context capture MUST avoid retaining raw object references. Mapping keys MUST be exact built-in `str` values; custom `str` subclasses MUST NOT be copied by identity.

Small primitive values MAY be copied. Heavy, deep, unsupported, or custom object values MUST be replaced with `"<BLOCKED>"`.

Mask presets and explicit mask paths MUST be applied after context capture.

The default debug path SHOULD mask `input_context.local_variables`.

Mask presets MUST NOT be documented as a guarantee that debug payloads are safe for public exposure. External responses MUST use the public path. If debug capture or masking fails, the fallback MUST contain only `tracker_failure=True` and a fixed generic message in its data dictionary, without original exceptions, input, or traceback. Fallback paths MUST NOT depend on writing to stdout or stderr.

## 8. Validation Rules

Contract-sensitive API changes MUST include executable tests.

Tests SHOULD cover:

- Canonical import paths.
- Package-level public exports.
- `ResultStatus` normalization, required `data`, typed factories, and rejected raw reconstruction helpers.
- Debug payload masking and safe context capture.
- Public payload minimal fields and absence of debug-only fields.
- Public tag JSON serialization and absence of caller-owned object references.
- Decorator conversion of synchronous and async uncaught exceptions into failure `Result` objects.
- Lazy debug system collection, deterministic public docstrings, and rejected invalid consumer typing.

The Python compatibility CI SHOULD run the test suite and package type check across the declared Python version matrix on push, pull request, manual dispatch, and before release-like checkpoints.

The negative consumer type gate MUST verify the expected diagnostic at every annotated line, not merely a nonzero mypy exit status. The source distribution MUST include the scripts and configurations needed by its non-strict readiness check. Strict release mode MUST reject a source archive without Git metadata.

## 9. Final Checklist

- Did canonical imports keep working?
- Did package-level exports still return the same public objects?
- Did public payloads avoid debug-only fields?
- Did debug payload masking still apply after context capture?
- Did tests pin any changed payload shape?
- Did docs mention any intentional compatibility or breaking behavior?
