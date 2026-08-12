[한국어 (Korean)](../ko/release-notes.md)

# Release Notes

## 1.0.0a1 — lint baseline

`1.0.0a1` continues the rebuilding alpha after `1.0.0a0`. It does not add a new runtime API or stable compatibility promise.

### Added

- The repository now owns a Ruff configuration targeting Python 3.10 with baseline correctness rules and import sorting (`E4`, `E7`, `E9`, `F`, and `I`).
- Ruff is available through the development-only `lint` extra and runs in compatibility CI, Docker checks, and release readiness.

### Changed

- Package code, tests, examples, and helper scripts now follow the same import ordering and Ruff formatter output.
- Developer and release documentation now includes Ruff linting and format checks.

## 1.0.0a0 — rebuilding

`1.0.0a0` restarts the package as an alpha rebuild. Earlier public releases and tags were withdrawn; this file intentionally does not preserve them as valid release history. See [Rebuilding](rebuilding.md) for the rationale and current scope.

### Alpha status

This is a GitHub prerelease, not a production release. Do not adopt it as a stable dependency or expect compatibility support. Public APIs, payload shapes, and release procedures may change during rebuilding.

### Restored contracts

- `Result.data` is required for every outcome, including failure and cancellation. Explicit `None` remains valid.
- `Result.ok()`, `Result.failure()`, and `Result.cancelled()` provide the preferred typed construction path while tuple-like unpacking, indexing, and comparison remain available.
- Raw `Result._make()` and `_replace()` reconstruction helpers are unavailable.
- Failed `unwrap()` and `expect()` calls retain raw values only on `ResultUnwrapException` attributes; their exception message does not format stored data, error, or context.
- `ExceptionTracker` collects one shared system snapshot lazily on the first debug-heavy call. Public-only methods and location lookup do not collect it.
- Debug context copies accept only exact built-in `str` keys. A missing error-code mapping returns a normal failure result with `data=None` and no emergency output.

### Quality gates

- Public docstrings are checked structurally and through deterministic doctests.
- The type gate accepts valid `Result` construction and rejects omitted data, invalid payload types, and removed raw helpers.
- CI covers Python 3.10–3.14 and runs pytest, mypy, Ruff linting and formatting, Markdownlint, actionlint, and package checks.
- The release-ready package passed sdist/wheel build, `twine check`, and an isolated wheel smoke test.

### Deferred work

Public payload `TypedDict` finalization, exception chaining policy, a public-tag global budget, immutable supply-chain pinning, SBOM/provenance artifacts, and stable compatibility guarantees remain follow-up work. They are not promised by this alpha.
