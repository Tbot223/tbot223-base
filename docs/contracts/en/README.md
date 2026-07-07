[한국어 (Korean)](../ko/README.md)

> Contract revision: 2026-06-23.

# Contract Docs

> Entry point for repository writing contracts.

## Contract Families

### Documentation Contract

- [human/documentation-contract.md](human/documentation-contract.md): Canonical contract for repository Markdown documents.
- [llm/documentation-contract.md](llm/documentation-contract.md): Execution guide for AI-assisted Markdown writing.

### Docstring Contract

- [human/docstring-contract.md](human/docstring-contract.md): Canonical contract for Python docstrings.
- [llm/docstring-contract.md](llm/docstring-contract.md): Execution guide for AI-assisted docstring writing.

### API Contract

- [human/api-contract.md](human/api-contract.md): Canonical contract for public import paths, `Result`, and `ExceptionTracker` payload shapes.
- [llm/api-contract.md](llm/api-contract.md): Execution guide for API, payload, compatibility, and validation updates.

## Recommended Use

- For README files, guides, references, release notes, and contract docs, start with the Documentation Contract.
- For Python docstrings, start with the Docstring Contract.
- For import paths, `Result`, exception payloads, or API compatibility, start with the API Contract.
- For AI-assisted writing, read the matching human contract first and the matching LLM execution guide second.

## Repository Decisions

- Scope includes README families, guide/reference/release documents, and contract docs.
- API contract scope includes canonical import paths, payload shapes, and validation expectations.
- Scope excludes TODO.md, code comments, and non-Markdown source files.
- English and Korean documents should keep matching paths when both exist.
- This repository uses a medium-strength documentation contract: the framework is standardized, but wording remains flexible.

## Path Policy

- This README is the contract entry point.
- Canonical contract files live under this lowercase path tree.
- Canonical document contracts live under this directory tree.
