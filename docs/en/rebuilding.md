[한국어 (Korean)](../ko/rebuilding.md)

> Runtime baseline: unreleased working tree based on `1.0.0a1`; these fixes are not part of the existing release tag.

# Rebuilding `tbot223-base`

`tbot223-base` continues its rebuilding alpha at `1.0.0a1`. Earlier public versions and release tags were withdrawn because the package presented stable type and safety guarantees that were not fully enforced by the runtime implementation.

## What This Means

- This is an alpha rebuild, not a production-ready release.
- Public API, payload shape, and release procedures may change without migration support.
- Develop from a source checkout; do not treat the package name as an installable stable dependency yet.
- Git commit history is retained for context, but it is not a statement that earlier release claims remain valid.

## Current Guarantees

- `Result` stays immutable and tuple-like, while every result state requires explicit `data`.
- `Result.ok()`, `Result.failure()`, and `Result.cancelled()` are the preferred typed factories; raw `_make()` and `_replace()` reconstruction are unavailable.
- A failed `unwrap()` or `expect()` keeps raw values on `ResultUnwrapException` attributes without formatting them into the exception message.
- Public exception paths do not collect traceback, local context, or system information. Debug system snapshots begin only on the first debug-heavy call.
- Debug context copies accept exact built-in string keys only and do not retain custom `str` key objects.

The unreleased boundary fixes add Result copy/pickle support and precise tuple typing, bounded public integers and a global tag traversal budget, concrete public field types, fail-closed debug fallback, and an explicit `wrap_awaitable()` decorator path. See the references and unreleased notes for migration details.

## Rebuilding Principles

1. Make runtime behavior, static types, documentation, and examples describe the same contract.
2. Collect only the data required by the selected boundary path.
3. Prefer a small explicit interface over compatibility shims that hide an invalid invariant.
4. Add a regression test and a gate whenever a safety or typing claim is introduced.

## Required Gates Before a Public Release

- Unit tests, deterministic public docstring doctests, and the AST-based docstring-contract check pass.
- Mypy accepts supported public usage and rejects intentionally invalid `Result` usage.
- Ruff linting and formatting, Markdownlint, actionlint, package build, `twine check`, and isolated-wheel smoke checks pass.
- Python 3.10 through 3.14 compatibility CI passes.
- A GitHub prerelease tag such as `v1.0.0a1` exactly matches the package version and passes strict release readiness before any publication is considered.

## Deferred Work

The alpha rebuild does not yet promise a stable long-term payload schema or a policy for suppressed exception context, immutable supply-chain pinning, SBOM/provenance artifacts, or stable release compatibility. These remain follow-up decisions, not hidden behavior guarantees.
