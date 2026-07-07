[한국어 (Korean)](../../ko/human/docstring-contract.md)

> Contract revision: 2026-06-23.

# Docstring Contract

> Markdown-first docstring format contract for the tbot223-base project.
> The primary consumer is the Markdown-rendering IDE hover/peek; `help()` and `pydoc` are treated as secondary compatibility targets.

## 1. Rendering Target

- Docstrings in this repository are optimized for IDE displays that parse Markdown.
- `###` headers, Markdown tables, and blockquotes are used to improve readability in IDE hover/peek.
- They must not break completely in `help()`, `pydoc`, or plain-text output, but those are not the primary optimization target.
- More important than the format choice is describing the current runtime behavior of the code accurately.

## 2. Scope and Strength

- Public APIs MUST follow the full format of this contract.
- An important internal method SHOULD follow the full format if it meets any of the following:
  - Input validation or constraints are non-obvious.
  - The call shape matters, as with callbacks, strategy functions, or dependency injection.
  - It has side effects, process control, security risk, or external system integration.
  - It is an external extension point or behavior maintainers reference often.
- Trivial private helpers, obvious one-liner wrappers, internal adapters, and simple getters/setters may use only a one-line summary or omit the docstring.
- Not every method in the same class needs to be documented at the same density.

## 3. Overall Structure

Every full docstring starts with a one-line summary, and the following sections use `###` headers.

```text
"""
One-line summary.

### Arguments
[arguments table or `None`]
### Returns
[return description]
### Example
[runnable example when included]
"""
```

### Minimum Compliant Form

The structural floor of a full docstring is the one-line summary, `Arguments`, and `Returns`. Add other sections only when there is supporting evidence.

```python
def unwrap_or(self, default: _DefaultT) -> Union[_DataT, _DefaultT]:
    """
    Return the contained `data` if successful; otherwise return `default`.

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(R)** | `default` | `_DefaultT` | Fallback value used when the result is not successful. |

    ### Returns
    `Union[_DataT, _DefaultT]` — The stored payload if successful, otherwise `default`.
    """
```

- To go below this, treat the function as a trivial helper per Section 2 and keep only the one-line summary or omit the docstring.
- Public APIs and important internal methods SHOULD add a runnable `Example` here. See 9.1 for the full example.

## 4. Section List and Conditions

| Section | Required | Condition |
|---------|----------|-----------|
| One-line summary | Always | The first line of every docstring. |
| Arguments | Always | Write `None` when there are no arguments. |
| Callable Signature | Conditional | When a callable, callback, function list, or protocol is a core input. |
| Enum | Conditional | Only when the real choices are limited and the meaning branches by value. Do not create it from a plain `Optional[...]` or a broad type annotation alone. |
| Constraint | Conditional | Only when actual validation logic exists in the code. |
| Returns | Always | Write the return type and its meaning per the current implementation. |
| Raises | Conditional | Only when the function intentionally raises an exception. Do not list paths that return failures as a `Result`. |
| Note | Optional | When supplementary explanation is needed, such as fallback, auto-computation, caching, or lazy loading. |
| Warning | Optional | When there are side effects, abnormal termination, security risk, process replacement, or pickling constraints. |
| Example | Recommended | Public APIs and important internal methods SHOULD include one. When included, it MUST be a context-complete runnable example. |

## 5. Section Order

### Basic form

```text
Arguments -> Returns -> Example
```

### Extended form

```text
Arguments -> Callable Signature -> Enum -> Constraint -> Returns -> Raises -> Note -> Warning -> Example
```

### Risk-emphasis variant

When the Warning must be read first, swap the order of Note and Warning.

```text
Arguments -> Callable Signature -> Enum -> Constraint -> Returns -> Raises -> Warning -> Note -> Example
```

## 6. Expression Standard

### 6.1 Sentence ending

- Every Description, Note, and Warning sentence ends with a period (`.`).
- The one-line summary also ends with a period.

### 6.2 Default notation

```text
Default: `value`.
```

- Standardize on `Default: \`value\`.` instead of `Default is ...`.
- Wrap `None`, `True`, `False`, numbers, and strings in backticks.

### 6.3 Type notation

- The Type column follows `typing` notation. Examples: `Optional[int]`, `Union[str, Path]`, `List[str]`.
- Specify inner generic parameters as far as practical.
- Wrap single types in backticks too. Examples: `str`, `int`, `bool`.

### 6.4 Reference notation

- Within a docstring, argument names are always wrapped in backticks. Examples: `workers`, `timeout`.
- Class, function, and return-type references are also wrapped in backticks. Examples: `ThreadPoolExecutor`, `Result`.
- Literal values are wrapped in backticks too. Examples: `True`, `False`, `None`, `'sha256'`, `0`.

### 6.5 Condition notation

- Operators and conditional expressions are wrapped in backticks. Examples: `> 0`, `>= 0 and <= 255`.
- Prefer explicit conditional expressions over natural language where possible.

## 7. Section Formats

### 7.1 One-line summary

```python
"""
Execute tasks concurrently with `ThreadPoolExecutor`.
"""
```

- Write in English, start with a base-form verb, and keep it concise.
- Wrap key class or function names in backticks.
- Leave a blank line after the summary.

### 7.2 Tag legend

Write it once, only at the top of the class `__init__` docstring.

```text
- **(R)** = Required argument
- **(O)** = Optional argument (has a default value)
- **(D)** = Dependency Injection (advanced usage)
```

### 7.3 Arguments

Write in Markdown table form.

```markdown
### Arguments
| Tag | Name | Type | Description |
|-----|------|------|-------------|
| **(R)** | `name` | `str` | User name. |
| **(O)** | `count` | `int` | Number of items. Default: `10`. |
| **(D)** | `manager` | `Optional[Manager]` | Manager instance. Default: built-in `Manager`. |
```

Tag meanings:

- **(R)** — Required. A mandatory argument with no default.
- **(O)** — Optional. An optional argument with a default.
- **(D)** — Dependency Injection. An injected argument for testing and extension.

When there are no arguments, write it as below.

```markdown
### Arguments
None
```

### 7.4 Callable Signature

Describe the exact call shape of a callable argument in a blockquote.

```markdown
### Callable Signature
> `data` element: `Tuple[Callable[..., Any], Dict[str, Any]]`
> - `Callable[..., Any]` — Any function accepting keyword arguments.
> - `Dict[str, Any]` — Keyword arguments passed via `func(**kwargs)`.
```

- State the parameter name and full type on the first line.
- Explain each type element in sub-bullets.
- When you can describe the actual call shape, be more specific than `Callable[..., Any]`.

### 7.5 Enum

Specify an argument with limited choices using a blockquote + table.
Declare the value type first with a `type:` row.

```markdown
### Enum
> `algorithm` — type: `str`
> | Value | Description |
> |-------|-------------|
> | `'md5'` | Uses the MD5 algorithm. |
> | `'sha1'` | Uses the SHA-1 algorithm. |
> | `'sha256'` | Uses the SHA-256 algorithm. |
> | `'sha512'` | Uses the SHA-512 algorithm. |
```

- Add it only when the real choices are limited and the meaning branches.
- Do not create an Enum section from a broad type annotation alone, such as `Optional[int]` or `Union[str, int]`.

### 7.6 Constraint

Describe validity constraints with a blockquote + bullet list.
Sentences use only the allowed patterns below.

| Pattern | Template | Example |
|---------|----------|---------|
| TYPE | `` `{param}` MUST be `{type}`. `` | `` `data` MUST be `str`. `` |
| NON-EMPTY | `` `{param}` MUST be a non-empty `{type}`. `` | `` `tasks` MUST be a non-empty `list`. `` |
| ELEMENT | `` Each element of `{param}` MUST be `{shape}`. `` | `` Each element of `data` MUST be `Tuple[Callable, Dict]`. `` |
| CHOICE | `` `{param}` MUST be one of `{values}`. `` | `` `algorithm` MUST be one of `'md5', 'sha1', 'sha256', 'sha512'`. `` |
| RELATION | `` `{param}` MUST satisfy `{expr}`. `` | `` `code` MUST satisfy `>= 0 and <= 255`. `` |
| UNLESS | `` `{param}` MUST satisfy `{expr}` unless `{guard}` is `{value}`. `` | `` `workers` MUST satisfy `<= len(data)` unless `override` is `True`. `` |
| IF-THEN | `` If `{condition}`, `{param}` MUST satisfy `{expr}`. `` | `` If `chunk_size` is not `None`, `chunk_size` MUST satisfy `>= 0`. `` |
| MUTUAL | `` `{paramA}` and `{paramB}` MUST NOT both be `{value}`. `` | `` `a` and `b` MUST NOT both be `None`. `` |

```markdown
### Constraint
> - `data` MUST be a non-empty `list`.
> - Each element of `data` MUST be `Tuple[Callable, Dict]`.
> - `workers` MUST satisfy `> 0`.
> - `workers` MUST satisfy `<= len(data)` unless `override` is `True`.
> - If `chunk_size` is not `None`, `chunk_size` MUST satisfy `>= 0`.
```

- Write it only when actual validation exists in the code.
- Do not supplement constraints from common sense that are not in the code.
- Write compound range conditions with the RELATION pattern. Example: `` `code` MUST satisfy `>= 0 and <= 255`. ``

### 7.7 Returns

```markdown
### Returns
`Result` — Contains the validated value in `data`.
```

- Wrap the type in backticks.
- After the em dash (`—`), add a description based on the current implementation.
- When returning a `Result`, state what `data` contains when possible.

### 7.8 Raises

Write it in a blockquote only when the function intentionally raises an exception.

```markdown
### Raises
> - `ResultUnwrapException` — Raised when `success` is not `True`.
```

- Write it only when an actual `raise` statement exists.
- Wrap the exception type in backticks, and after the em dash (`—`), describe the condition.
- Explain paths that return failures as a `Result` with `Constraint`/`Returns`, not `Raises`.

### 7.9 Note

Write supplementary explanations in a blockquote.

```markdown
### Note
> Worker count defaults to `os.cpu_count()` when `workers` is `None`.
```

### 7.10 Warning

Write cautions in a blockquote.

```markdown
### Warning
> This method does **not** return under normal circumstances.
```

When there is a security-related caution, separate it as a `**Security:**` block at the very top inside Warning.

```markdown
### Warning
> **Security:**
> - Input is not sanitized. Do not pass untrusted user input directly.
> - Pickle deserialization can execute arbitrary code.
>
> General warnings here.
```

### 7.11 Example

Write the Example in `>>>` REPL form.

```markdown
### Example
>>> from tbot223_base.result import Result
>>> result = Result(success=True, error=None, context="Demo", data={"key": "value"})
>>> print(result.success)  # True
>>> print(result.data["key"])  # value
```

- Use real import paths and real class and function names.
- Include the required instance creation, helper function definitions, and minimal input data.
- For multi-line statements, use the doctest continuation prompt `...`. This `...` marks input continuation, not omitted code.
- Show expected output as a result line or as a `# value` comment.
- Do not use omission placeholders such as `...`, `foo`, `bar`, or an undefined `app_core`.
- The example exists to show the format and usage flow; output may vary by environment, so it does not guarantee passing as an automated doctest.
- For methods with large side effects, show only a minimal call example, and explain the risk first in `Warning`.
- You may omit the Example when realistic setup would be excessive or the destructive side effects are large enough that a runnable example would mislead.

## 8. Rule Summary

1. A full docstring always includes the one-line summary, Arguments, and Returns.
2. Public APIs and important internal methods SHOULD include a runnable Example.
3. If you include an Example, write it in context-complete runnable form.
4. Add Callable Signature, Enum, and Constraint only when there is evidence.
5. Use Enum only when there are real limited choices and meaning branches.
6. Constraint uses only the allowed formal patterns.
7. Write the Tag legend once, only in the class `__init__`.
8. Standardize defaults in the `Default: \`value\`.` form.
9. Trivial private helpers and obvious adapters may use only a one-line summary or be omitted.
10. List Raises only when an actual `raise` statement exists; do not list `Result` failure returns.

## 9. Full Example Docstrings

### 9.1 Basic form example

A basic form based on the real `Result.unwrap_or` in `tbot223_base`.

```python
def unwrap_or(self, default: _DefaultT) -> Union[_DataT, _DefaultT]:
    """
    Return the contained `data` if successful; otherwise return `default`.

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(R)** | `default` | `_DefaultT` | Fallback value used when the result is not successful. |

    ### Returns
    `Union[_DataT, _DefaultT]` — The stored payload if successful, otherwise `default`.

    ### Example
    >>> from tbot223_base.result import Result
    >>> result = Result(success=False, error="Not Found", context="FetchData", data=None)
    >>> print(result.unwrap_or({"key": "default"}))  # {'key': 'default'}
    """
```

### 9.2 Enum + Warning + Note example

An example based on the real `ExceptionTracker.get_exception_info` in `tbot223_base`. `mask_presets` is a real limited choice set, so Enum is used. Invalid input is ignored rather than rejected, so it is described in Note instead of Constraint.

```python
def get_exception_info(
    self,
    error: Exception,
    user_input: object = None,
    params: ExceptionParams = ((), {}),
    mask_presets: MaskPresetsInput = ("default",),
    mask_paths: MaskPathsInput = (),
) -> Result:
    """
    Build structured exception information.

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(R)** | `error` | `Exception` | The exception object to describe. |
    | **(O)** | `user_input` | `object` | User input context. Small safe values are copied; heavy values are blocked. Default: `None`. |
    | **(O)** | `params` | `ExceptionParams` | Additional call context `(args, kwargs)`. Small safe values are copied; heavy values are blocked. Default: `((), {})`. |
    | **(O)** | `mask_presets` | `MaskPresetsInput` | Named mask presets. Default: `("default",)`. |
    | **(O)** | `mask_paths` | `MaskPathsInput` | Extra paths to mask. Default: `()`. |

    ### Enum
    > `mask_presets` — type: `str`
    > | Value | Description |
    > |-------|-------------|
    > | `'default'` | Masks `input_context.local_variables`. |
    > | `'private'` | Masks user input, params, and local variables. |
    > | `'user_input'` | Masks `input_context.user_input`. |
    > | `'params'` | Masks `input_context.params` and local variables. |
    > | `'traceback'` | Masks `causes`, `traceback`, and `traceback_frames`. |
    > | `'system_info'` | Masks `system_info`. |

    ### Returns
    `Result` — Contains the structured error information in `data`.

    ### Warning
    > **Security:**
    > - `user_input`, `params`, and `local_variables` never store raw object references.
    > - Heavy or unsupported context values are replaced with `"<BLOCKED>"` rather than summarized with metadata.
    > - Small copied context values, `traceback`, and `system_info` may still contain sensitive data.
    > - Environment variables inside `system_info` are copied only when they are small primitives or shallow tuple/list values with small primitive items.
    > - Apply `mask_presets=("private", "traceback", "system_info")` before exposing error information outside a trusted boundary.

    ### Note
    > Context capture preserves small primitives and primitive-only `list`/`tuple` values; `dict` values are copied only at the top level.
    > Unknown preset names and invalid mask paths are ignored rather than rejected.

    ### Example
    >>> from tbot223_base.exception_tracker import ExceptionTracker
    >>> tracker = ExceptionTracker()
    >>> try:
    ...     1 / 0
    ... except ZeroDivisionError as error:
    ...     result = tracker.get_exception_info(error, mask_presets=("private", "traceback"))
    >>> print(result.success)  # True
    """
```

### 9.3 Constraint + Raises example

An example based on the real `Result.unwrap` in `tbot223_base`. When `success` is not `True`, it actually raises `ResultUnwrapException`, so Constraint and Raises are written together.

```python
def unwrap(self) -> _DataT:
    """
    Return the contained `data` when the result represents success.

    ### Arguments
    None

    ### Constraint
    > - `self.status` MUST be `ResultStatus.SUCCESS`.

    ### Returns
    `_DataT` — The stored payload.

    ### Raises
    > - `ResultUnwrapException` — Raised when `status` is not `ResultStatus.SUCCESS`.

    ### Example
    >>> from tbot223_base.result import Result
    >>> result = Result(success=True, error=None, context="FetchData", data=42)
    >>> print(result.unwrap())  # 42
    """
```

**Illustrative examples.** The next two examples (9.4, 9.5) exist to show the format. This base package has no dependency-injection argument or callable-list API, so they assume shapes likely used in the companion package (`tbot223_core`). When writing real docstrings, use the actual import paths and identifiers of the target code.

### 9.4 Class `__init__` and Tag legend example (illustrative)

Write the Tag legend once at the top of the class `__init__` docstring. Use `(D)` for dependency-injection arguments.

```python
class TaskRunner:
    def __init__(self, retries: int = 3, manager: Optional[Manager] = None) -> None:
        """
        Initialize a task runner.

        - **(R)** = Required argument
        - **(O)** = Optional argument (has a default value)
        - **(D)** = Dependency Injection (advanced usage)

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(O)** | `retries` | `int` | Retry attempts per task. Default: `3`. |
        | **(D)** | `manager` | `Optional[Manager]` | Injected manager for tests or extension. Default: built-in `Manager`. |

        ### Returns
        `None` — Initializes the runner and resolves the injected `manager`.
        """
```

### 9.5 Callable Signature example (illustrative)

```python
def thread_pool_executor(
    self,
    data: List[Tuple[Callable[..., Any], Dict[str, Any]]],
    workers: Optional[int] = None,
    override: bool = False,
    timeout: Optional[float] = None,
) -> Result:
    """
    Execute tasks concurrently with `ThreadPoolExecutor`.

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(R)** | `data` | `List[Tuple[Callable[..., Any], Dict[str, Any]]]` | A list of `(callable, kwargs_dict)` tuples. |
    | **(O)** | `workers` | `Optional[int]` | Number of worker threads. Default: `None`. |
    | **(O)** | `override` | `bool` | Allow workers to exceed task count. Default: `False`. |
    | **(O)** | `timeout` | `Optional[float]` | Max wait time per task in seconds. Default: `None`. |

    ### Callable Signature
    > `data` element: `Tuple[Callable[..., Any], Dict[str, Any]]`
    > - `Callable[..., Any]` — Any function accepting keyword arguments.
    > - `Dict[str, Any]` — Keyword arguments passed via `func(**kwargs)`.

    ### Constraint
    > - `data` MUST be a non-empty `list`.
    > - Each element of `data` MUST be `Tuple[Callable, Dict]`.
    > - `workers` MUST satisfy `> 0`.
    > - `workers` MUST satisfy `<= len(data)` unless `override` is `True`.
    > - If `timeout` is not `None`, `timeout` MUST satisfy `> 0.1`.

    ### Returns
    `Result` — Contains an ordered `List[Result]` of task results in `data`.

    ### Example
    >>> from tbot223_core import AppCore
    >>> def add(a: int, b: int) -> int:
    ...     return a + b
    >>> app_core = AppCore(is_logging_enabled=False)
    >>> data = [(add, {"a": 1, "b": 2}), (add, {"a": 3, "b": 4})]
    >>> result = app_core.thread_pool_executor(data, workers=2, timeout=1.0)
    >>> print([res.data for res in result.data])  # [3, 7]
    """
```

## 10. Special Forms

Most special forms reuse existing sections instead of adding new ones. The table below lists only the per-form delta.
`Result` is a generic tuple-like container, so the dataclass / NamedTuple row is grounded in real field documentation, while the async, generator, and context manager rows are for format illustration because the base package has no such code.

| Form | Key rule |
|------|----------|
| `async def` / coroutine | Keep the one-line summary in base-verb form. In `Returns`, describe the type and meaning produced when `await`ed. Put concurrency, cancellation, and async side effects in `Note` or `Warning`, and do not add an async-only section. |
| Generator / iterator | In `Returns`, write the `Iterator[...]` or `Generator[...]` type and what it yields. Note lazy evaluation or single-pass consumption in `Note`, and do not add a separate Yields section. |
| `*args` / `**kwargs` | Write the `Arguments` Name as `*args` or `**kwargs` as-is, and put each element type in Type. Tag is usually **(O)**. |
| `@property` | Set `Arguments` to `None`. Write the summary as a value-returning verb form, and only `Returns` is required. Treat a setter as a method taking one value argument. Do not invent a `Constraint` without code evidence on a property. |
| Context manager | Name the managed resource in the summary. In `Returns`, write the value bound in the `with` block; put setup and teardown in `Note`, and resource-release guarantees or leak risks in `Warning`. |
| dataclass / NamedTuple | Document the fields once in the class docstring using the `Arguments` table form. Methods follow the usual rules. |

### `*args` / `**kwargs` Example

```markdown
### Arguments
| Tag | Name | Type | Description |
|-----|------|------|-------------|
| **(O)** | `*args` | `int` | Values to sum. |
| **(O)** | `**kwargs` | `str` | Named options forwarded to the handler. |
```

### Generator `Returns` Example

```markdown
### Returns
`Iterator[int]` — Yields each parsed line number in order.
```

### dataclass / NamedTuple Field Example

A class-level field table based on the real generic `Result` tuple-like field names and types in `tbot223_base`.

```markdown
### Arguments
| Tag | Name | Type | Description |
|-----|------|------|-------------|
| **(R)** | `status` | `ResultStatus` | Overall operation state. |
| **(R)** | `error` | `Optional[str]` | Error label when not successful. |
| **(R)** | `context` | `Optional[str]` | Call-site context label. |
| **(R)** | `data` | `_DataT` | Payload carried on the result. |
```
