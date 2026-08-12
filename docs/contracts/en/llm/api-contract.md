[한국어 (Korean)](../../ko/llm/api-contract.md)

> Contract revision: 2026-08-12.

# API Contract for LLM

> Execution guide for updating API, payload, import-path, and compatibility behavior.

## Read First

Read [../human/api-contract.md](../human/api-contract.md) first.

- The human-facing API contract is the canonical rule set.
- This file is an execution guide, not a replacement summary.

## Workflow

1. Identify whether the change touches public API, payload shape, import paths, package-level exports, or validation tooling.
2. Preserve canonical import paths unless the user explicitly requests a breaking migration.
3. Keep package-level public exports aligned with canonical module objects.
4. Describe `Result` as an independently shaped Python boundary exchange protocol, not as a Rust compatibility target.
5. When changing `Result`, keep the explicit `data` requirement, typed factories, tuple-like read behavior, and lack of raw reconstruction helpers aligned.
6. When public/debug payload shape changes, update tests before treating the change as complete.
7. Keep public payloads free of debug-only fields.
8. Keep debug payload safety behavior explicit: safe copies, `"<BLOCKED>"`, masking after capture, and no system collection for public-only paths.
9. Keep public tag values bounded, JSON-safe, and free of caller-owned object references.
10. Keep synchronous and async decorator behavior covered by executable tests and consumer typing checks.
11. If the supported Python version range changes, update `pyproject.toml`, CI workflow, and user docs together.
12. Run the local verification commands that are available in the current checkout.

## Test Expectations

API-sensitive changes should run:

```bash
pytest -q
python -m mypy
python -m ruff check .
python -m ruff format --check .
python scripts/check-docstring-contract.py
markdownlint-cli2 "**/*.md" "#node_modules"
python -m py_compile tbot223_base/__init__.py tbot223_base/result.py tbot223_base/exception_tracker.py
git diff --check
```

When CI is available, the optional Python compatibility workflow should be used before release-like checkpoints.

## Do Not

- Do not expose traceback, params, user input, local variables, or system information in public payloads.
- Do not retain unsupported caller-owned objects inside public tags.
- Do not introduce alternate public import paths without documenting them in the API contract.
- Do not change `ResultStatus` string values without documenting a breaking change.
- Do not update docs without matching behavior tests when payload behavior changes.
- Do not describe the `1.0.0a1` rebuild as a stable release or production guarantee.
