[한국어 (Korean)](../../ko/llm/api-contract.md)

> Contract revision: 2026-07-07.

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
5. When public/debug payload shape changes, update tests before treating the change as complete.
6. Keep public payloads free of debug-only fields.
7. Keep debug payload safety behavior explicit: safe copies, `"<BLOCKED>"`, and masking after capture.
8. If the supported Python version range changes, update `pyproject.toml`, CI workflow, and user docs together.
9. Run the local verification commands that are available in the current checkout.

## Test Expectations

API-sensitive changes should run:

```bash
pytest -q
python -m py_compile tbot223_base/__init__.py tbot223_base/result.py tbot223_base/exception_tracker.py
git diff --check
```

When CI is available, the optional Python compatibility workflow should be used before release-like checkpoints.

## Do Not

- Do not expose traceback, params, user input, local variables, or system information in public payloads.
- Do not introduce alternate public import paths without documenting them in the API contract.
- Do not change `ResultStatus` string values without documenting a breaking change.
- Do not update docs without matching behavior tests when payload behavior changes.
