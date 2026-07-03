[한국어 (Korean)](../../ko/llm/docstring-contract.md)

> Contract revision: 2026-06-23.

# Docstring Contract for LLM

> This document is not a human-facing contract; it is an execution guide the LLM follows directly when generating docstrings.

## Read First

Before reading this file, you MUST first read [../human/docstring-contract.md](../human/docstring-contract.md).

- The human-facing document is the canonical contract.
- This document does not summarize or replace the canonical one.
- If a conflict arises while writing, the human-facing canonical document wins.

## Goal

- Write docstrings with the current runtime behavior of the code as the priority.
- Keep the Markdown-heavy format, assuming the Markdown-rendering IDE hover/peek as the primary consumer.
- Extract `Constraint` only from validation logic in the code.
- Write `Example` as a context-complete runnable example that includes real imports, instantiation, and helper function definitions.

## Reading Procedure

1. First, read [../human/docstring-contract.md](../human/docstring-contract.md) to the end.
2. Understand the rendering target, scope, section structure, and expression rules.
3. Then read this document and confirm what to extract from the actual code.
4. If a conflict arises while writing, fall back to the human-facing canonical document.

## Priority

1. The actual behavior of the code.
2. The current function signature and return shape.
3. The scope, section structure, and expression rules of the human-facing canonical contract.
4. The extraction rules and checklists of this document.
5. Stylistic polish and decoration.

Runtime truth takes priority over format. When evidence is insufficient, do not force sections to be filled.

## Workflow

1. Read the function signature.
2. First decide whether this function is a public API, an important internal, or a trivial helper.
3. In the function body, find input validation, guard clauses, failure returns, exception-raising points, auto-correction, and side effects.
4. Based on the evidence, write `Arguments`, `Callable Signature`, `Enum`, `Constraint`, `Returns`, `Raises`, `Note`, `Warning`, and `Example` only as much as needed.
5. Always include `Arguments` and `Returns` in a full docstring.
6. Add `Enum` only when there are real limited choices and the meaning branches.
7. If you include `Example`, include real imports, real class names, real function names, instantiation, and any required helper function definitions.

## Scope Decision Rules

- Treat a public API as a full docstring by default.
- Treat an important internal method as a full-docstring candidate if any of the following:
  - The validation logic is non-obvious.
  - A callback, function list, or dependency injection is a core input.
  - It has side effects, process control, or security risk.
  - It is an extension point maintainers reference often.
- A trivial private helper, a simple adapter, or an obvious one-liner wrapper may use only a one-line summary or be omitted.

## Constraint Extraction Rules

### Core principle

- `Constraint` reflects only validation logic present in the code.
- Comments, intent, future plans, and TODOs are not evidence for `Constraint`.
- Fallback or auto-correction is not a rejection condition, so it usually goes in `Note`.
- Not only `raise` but also failure paths such as `return Result(False, ...)` count as constraint evidence.
- Do not create free-form constraints outside the allowed patterns.

### Code patterns accepted as evidence

- `if not isinstance(...)`
- `if len(data) == 0`
- `if value not in (...)`
- `if workers > len(data) and not override`
- `if chunk_size is not None and chunk_size < 0`
- `raise ValueError(...)`, `raise TypeError(...)`, `raise KeyError(...)`
- `return Result(False, ...)` or an equivalent failure return

### Allowed patterns

| Pattern | Template |
|---------|----------|
| TYPE | `` `{param}` MUST be `{type}`. `` |
| NON-EMPTY | `` `{param}` MUST be a non-empty `{type}`. `` |
| ELEMENT | `` Each element of `{param}` MUST be `{shape}`. `` |
| CHOICE | `` `{param}` MUST be one of `{values}`. `` |
| RELATION | `` `{param}` MUST satisfy `{expr}`. `` |
| UNLESS | `` `{param}` MUST satisfy `{expr}` unless `{guard}` is `{value}`. `` |
| IF-THEN | `` If `{condition}`, `{param}` MUST satisfy `{expr}`. `` |
| MUTUAL | `` `{paramA}` and `{paramB}` MUST NOT both be `{value}`. `` |

### Formal pattern mapping examples

| Code shape | docstring pattern |
| --- | --- |
| `if not isinstance(data, str):` | `data` MUST be `str`. |
| `if algorithm not in ['md5', 'sha1', 'sha256', 'sha512']:` | `algorithm` MUST be one of `'md5', 'sha1', 'sha256', 'sha512'`. |
| `if workers > len(data) and not override:` | `workers` MUST satisfy `<= len(data)` unless `override` is `True`. |
| `if chunk_size is not None and chunk_size < 0:` | If `chunk_size` is not `None`, `chunk_size` MUST satisfy `>= 0`. |
| `if code < 0 or code > 255:` | `code` MUST satisfy `>= 0 and <= 255`. |

### Prohibitions

- Do not supplement constraints from common sense that are not in the code.
- Do not pre-write constraints that merely seem useful in the future.
- Do not create an Enum from a plain type annotation alone.
- Do not write behavior that the implementation auto-corrects as if it were a failure constraint.
- Do not omit the real call meaning just because the type hint is `Callable[..., Any]`.

## Raises Extraction Rules

- Write in `Raises` only the exceptions the function actually raises.
- Use direct raise points such as `raise ValueError(...)` or `raise ResultUnwrapException(...)` as evidence.
- Paths that express failure as `return Result(False, ...)` go in `Constraint`/`Returns`, not `Raises`.
- Even if an internal function it calls may raise, do not infer it when the current function does not handle it explicitly.
- Wrap the exception type in backticks and state the trigger condition.

## Example Rules

- Use real import paths and real class names.
- Write it as immediately runnable, including instance creation, helper function definitions, and minimal input data inside the example.
- For multi-line statements, use the doctest continuation prompt `...`. This `...` marks input continuation, not omitted code.
- Show expected output as a result line or as a `# value` comment.
- Omission placeholders such as `...`, `func1`, `val1`, or an undefined `app_core` are prohibited.
- For functions with large side effects, show only a minimal call example, and write the risk in `Warning`.
- You may omit the Example when realistic setup would be excessive or the destructive side effects are large enough that a runnable Example would mislead.

## Special Form Extraction Rules

Special forms map onto existing sections instead of adding new ones.

- When you see `async def` or `await`, write the `await` result type in `Returns`. Move concurrency and cancellation behavior into `Note` or `Warning`, and do not add an async-only section.
- When the body has a `yield`, treat it as a generator and write `Iterator[...]` / `Generator[...]` and what it yields in `Returns`. Do not add a separate Yields section.
- For `*args` and `**kwargs`, write `*args` and `**kwargs` as-is in the `Arguments` Name and the element type in Type.
- For `@property`, set `Arguments` to `None` and treat only `Returns` as required. Do not invent a `Constraint` without code evidence on a property. Treat a setter as a method with one value argument.
- When you see `__enter__` / `__exit__` or `@contextmanager`, write the `with` binding value in `Returns`, release guarantees and leak risks in `Warning`, and setup/teardown in `Note`.
- For a `NamedTuple` or `@dataclass`, document the fields once in the class docstring using the `Arguments` table form.

## Per-Section Checklist

### Arguments

- Write only the arguments in the signature.
- When there is a default, keep the `Default: \`value\`.` form.

### Callable Signature

- Add it only when a callable is a core argument.
- When you can describe the actual call shape, be more specific than `Callable[..., Any]`.

### Enum

- Add it only when the choices are actually limited.
- Declare the value type first with a `type:` row.

### Constraint

- Write only validation that has code evidence.
- Use only the allowed formal patterns.
- Do not add a single line of validation that is not in the code.

### Returns

- Write the actual return type of the current function.
- When it returns a `Result`, also write what `data` contains based on the current code.

### Raises

- Write it only when an actual `raise` statement exists.
- Do not write `Result` failure returns in `Raises`.

### Note

- Write supplementary information such as fallback, auto-computation, lazy loading, and caching behavior.
- Do not hide input-rejection conditions in `Note`.

### Warning

- Write it only when there is abnormal termination, process replacement, security risk, a pickling constraint, or a side effect.

### Example

- Re-check whether the import is missing.
- Re-check whether instantiation is missing.
- Check that you did not omit a needed helper function definition.
- Check that no `...` or undefined identifier remains.

## Before You Output

- Did you first decide whether this function is a full-docstring target?
- Did you leave the human-provided code and signature unchanged?
- Did `Constraint` come only from actual if statements, raises, and failure returns?
- Did `Raises` come only from actual `raise` statements?
- Does `Enum` reflect real limited choices?
- Is `Example` runnable without placeholders?
- Does `Returns` match the current implementation?
- Even when the format is sparse, did you avoid filling in fabricated content?
- Is the full-docstring floor a one-line summary + `Arguments` + `Returns`, and did you add a runnable `Example` for public APIs?
- Did you handle special forms such as async, generators, `@property`, context managers, and `NamedTuple` with the existing-section mapping rules?

## Paste Prompt

```text
First read docs/contracts/en/human/docstring-contract.md to learn the contract, then
use docs/contracts/en/llm/docstring-contract.md as the working instruction to write the docstring for the code I just gave you.
Keep the Markdown-heavy format but assume the Markdown-rendering IDE hover/peek as the primary consumer,
treat public APIs and important internal methods as full-docstring targets,
analyze the code's if statements, raises, and failure returns to write Constraint only with the allowed formal patterns,
add Enum only when there are real limited choices,
and write Example in runnable form including real imports, instantiation, and helper function definitions.
Never add constraints not in the code or placeholder examples.
```
