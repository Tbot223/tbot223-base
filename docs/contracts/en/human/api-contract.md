[한국어 (Korean)](../../ko/human/api-contract.md)

> Contract revision: 2026-07-07.

# API Contract

> Contract for public import paths, `Result`, and `ExceptionTracker` payload shapes.

## 1. Goal

- Define the pre-release public API around Python-conventional canonical module paths.
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

The `success=` input and `result.success` property SHOULD remain available as supported tri-state shorthand APIs until a documented breaking change removes them.

## 5. Exception Payload Contract

`ExceptionTracker` has two payload paths.

| Path | Methods | Boundary |
| --- | --- | --- |
| Debug-heavy | `get_exception_info()`, `get_exception_return()` | Trusted internal diagnostics. |
| Public-safe | `get_public_exception_info()`, `get_public_exception_return()` | API responses, UI surfaces, and untrusted boundaries. |

Debug payloads MUST include structured failure metadata, location information, copied safe context, chained causes, traceback data, and system information unless masked or unavailable.

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

## 7. Debug Safety Rules

Debug context capture MUST avoid retaining raw object references.

Small primitive values MAY be copied. Heavy, deep, unsupported, or custom object values MUST be replaced with `"<BLOCKED>"`.

Mask presets and explicit mask paths MUST be applied after context capture.

The default debug path SHOULD mask `input_context.local_variables`.

## 8. Validation Rules

Contract-sensitive API changes MUST include executable tests.

Tests SHOULD cover:

- Canonical import paths.
- Package-level public exports.
- `ResultStatus` normalization and `success=` shorthand behavior.
- Debug payload masking and safe context capture.
- Public payload minimal fields and absence of debug-only fields.
- Decorator conversion of uncaught exceptions into failure `Result` objects.

The optional Python compatibility CI SHOULD run the test suite across the declared Python version matrix before release-like checkpoints.

## 9. Final Checklist

- Did canonical imports keep working?
- Did package-level exports still return the same public objects?
- Did public payloads avoid debug-only fields?
- Did debug payload masking still apply after context capture?
- Did tests pin any changed payload shape?
- Did docs mention any intentional compatibility or breaking behavior?
