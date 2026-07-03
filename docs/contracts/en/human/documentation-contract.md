[한국어 (Korean)](../../ko/human/documentation-contract.md)

> Contract revision: 2026-06-23.

# Documentation Contract

> Markdown writing contract for repository documents other than Python docstrings.

## 1. Goal

- Unify document style across README files, guides, references, release notes, and contract docs.
- Make each document's purpose obvious near the top.
- Make README, Guide, and Reference docs declare their runtime/version basis, and make Contract docs declare their document-policy revision, near the top.
- Keep English and Korean file structure aligned without forcing identical wording.
- Standardize the framework, not every sentence.
- Use GitHub Flavored Markdown as the baseline writing format.

## 2. Scope

This contract applies to:

- Root and language-specific README files.
- Long-form docs under docs/en and docs/ko.
- Contract docs under docs/contracts.
- Markdown documents only.

This contract does not apply to:

- TODO.md.
- Code comments.
- Source files or example scripts.
- Python docstrings, which follow the separate docstring contract.

## 3. Contract Strength

This is a medium-strength contract.

- Every document MUST have one primary document type.
- Every document MUST state its scope or purpose near the top.
- Every document SHOULD follow the template for its type.
- Exact heading names and exact sentence shape do not need to be identical across files.

## 4. Shared Rules

- README, Guide, and Reference docs MUST declare a runtime/version basis in the top metadata block.
- Contract docs MUST declare a `Contract revision` or `Last updated` in the top metadata block.
- Treat a Contract doc as recording a document-policy revision, not as an appendix to a package version.
- Release Notes are exempt from the basis requirement because the version history itself serves as the basis.
- The default top metadata order is `language switch link -> version basis -> title`.
- If no sibling language file exists, the file MAY start with `version basis -> title`.
- State scope, summary, or reader intent within the first 10 lines.
- Keep one dominant mode per document. Do not let a single file drift between README, guide, release note, and reference without clear section boundaries.
- Prefer shallow heading depth. Add deeper nesting only when it improves navigation.
- Use prose for explanation, lists for enumeration, and tables for fixed-structure comparisons.
- Write for correct GitHub rendering first, using GitHub Flavored Markdown as the default baseline.
- Use language tags on fenced code blocks whenever possible.
- Keep internal links relative.
- If an equivalent document exists in another language, add a language switch link near the top.
- The version basis may be written as a natural sentence, short banner, or blockquote when it stays clear.
- If the exact release version cannot be verified, use a verifiable temporary basis such as `current dev branch` or `main branch HEAD`, and do not invent a release number.
- For a Contract doc, use only a repository-verifiable date or an explicit revision label as the revision, and do not infer it from a package version.
- New or edited documents SHOULD not introduce avoidable markdownlint warnings.
- When touching an existing file, reduce low-cost markdownlint warnings when practical.
- If structural rules are already disabled in the repository config, do not force the document structure to match default markdownlint rules.
- Remove drafting notes, TODO-style text, and chatty filler before finalizing.

## 5. Bilingual Policy

- If both English and Korean files exist, the path and filename MUST match across languages.
- Section order and wording MAY differ by language.
- Information coverage SHOULD remain equivalent.
- Do not mix both languages through the main body except for language switch links, proper names, or unavoidable technical terms.

## 6. Document Types

### README

Use for orientation and entry-point documents.

Required elements:

- Version basis.
- Title.
- Short summary.
- Reader fit, purpose, or project framing.
- Links to deeper docs.

Common order:

```text
Language link (optional) -> Version basis -> Title -> Summary -> Fit/Purpose -> Core sections -> Further docs/links
```

Tone:

- Explanatory.
- Direct.
- Friendly but not promotional.

### Guide

Use for migration, walkthrough, setup, or task-oriented documents.

Required elements:

- Version basis.
- Title.
- Short summary.
- Starting state or prerequisites when relevant.
- Ordered flow, staged sections, or clearly progressive structure.
- Expected result, verification point, or next action when relevant.

Common order:

```text
Language link (optional) -> Version basis -> Title -> Summary -> Prerequisites/Context -> Steps or staged sections -> Verification/Next action
```

Tone:

- Procedural.
- Action-oriented.
- Explicit about transitions and consequences.

### Reference

Use for API overviews, structured feature descriptions, and lookup-style material.

Required elements:

- Version basis.
- Title.
- Scope statement.
- Navigable structure.
- Structured fields, tables, or repeatable section blocks when useful.

Common order:

```text
Language link (optional) -> Version basis -> Title -> Scope -> Navigation/TOC (optional) -> Feature blocks -> Notes/Examples when needed
```

Tone:

- Compressed.
- Precise.
- Low on narrative unless it helps interpretation.

### Release Notes

Use for version history and change reporting.

Required elements:

- Title.
- Version/date grouping.
- Change categories that match the content.

Common order:

```text
Title -> Version blocks -> Change categories
```

Tone:

- Factual.
- Brief.
- No tutorial drift.

### Contract

Use for repository rules, writing contracts, and normative standards.

Required elements:

- Contract revision or last updated.
- Purpose.
- Scope.
- Rules.
- Checklist, workflow, or companion document guidance.

Common order:

```text
Language link (optional) -> Contract revision -> Title -> Purpose -> Scope -> Rules -> Workflow/Checklist -> Companion docs
```

Tone:

- Normative.
- Clear.
- Use MUST, SHOULD, and MAY when the distinction matters.

## 7. Consistency Rules

- Make the document type visible from the opening block and first major heading choices.
- Do not use README tone for release notes.
- Do not use release-note grouping for guides.
- Do not turn references into long narrative essays unless the file explicitly mixes modes by section.
- Keep terminology stable within a file. If a term changes, explain the rename or migration explicitly.
- When updating one language in a bilingual pair, review whether the sibling file also needs structural and version-basis alignment.

## 8. Final Checklist

- Is the document type obvious near the top?
- If this is a README, Guide, or Reference, is the runtime/version basis present in the top metadata?
- If this is a Contract, is the contract revision or last updated present in the top metadata?
- Is the basis grounded in verifiable repository facts?
- Does the opener explain what the file is for?
- Does the structure match the file's type?
- Does the Markdown render cleanly on GitHub?
- Are internal links relative and language-local where possible?
- Are code blocks tagged?
- Did you avoid introducing new markdownlint warnings?
- Did you remove TODO-style or draft-only text?
- If a paired language file exists, does the path still match?
