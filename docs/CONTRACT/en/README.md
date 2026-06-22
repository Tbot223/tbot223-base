[한국어 (Korean)](../ko/README.md)

> Contract revision: 2026-06-23.

# Contract Docs

> Entry point for repository writing contracts.

## Contract Families

### Documentation Contract

- [FOR_HUMAN/DOCUMENTATION_CONTRACT.md](FOR_HUMAN/DOCUMENTATION_CONTRACT.md): Canonical contract for repository Markdown documents.
- [FOR_LLM/DOCUMENTATION_CONTRACT.md](FOR_LLM/DOCUMENTATION_CONTRACT.md): Execution guide for AI-assisted Markdown writing.

### Docstring Contract

- [FOR_HUMAN/DOCSTRING_CONTRACT.md](FOR_HUMAN/DOCSTRING_CONTRACT.md): Canonical contract for Python docstrings.
- [FOR_LLM/DOCSTRING_CONTRACT.md](FOR_LLM/DOCSTRING_CONTRACT.md): Execution guide for AI-assisted docstring writing.

## Recommended Use

- For README files, guides, references, release notes, and contract docs, start with the Documentation Contract.
- For Python docstrings, start with the Docstring Contract.
- For AI-assisted writing, read the matching `FOR_HUMAN` file first and the matching `FOR_LLM` file second.

## Repository Decisions

- Scope includes README families, guide/reference/release documents, and contract docs.
- Scope excludes TODO.md, code comments, and non-Markdown source files.
- English and Korean documents should keep matching paths when both exist.
- This repository uses a medium-strength documentation contract: the framework is standardized, but wording remains flexible.

## Path Policy

- This README is the contract entry point.
- The legacy path [../../DOCSTRING_CONTRACT.md](../../DOCSTRING_CONTRACT.md) is kept as a compatibility note.
- Canonical document contracts live under this directory tree.
