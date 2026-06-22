[English](../../en/FOR_HUMAN/DOCSTRING_CONTRACT.md)

> Contract revision: 2026-06-23.

# Docstring Contract

> tbot223-base 프로젝트의 Markdown-first docstring 양식 계약.
> 1차 소비자는 Markdown을 렌더링하는 IDE hover/peek이며, `help()`와 `pydoc`은 2차 호환 대상으로 둔다.

## 1. 렌더링 대상

- 이 저장소의 docstring은 Markdown을 파싱하는 IDE 표시에 최적화한다.
- `###` 헤더, Markdown 표, blockquote를 쓰는 이유는 IDE hover/peek에서 가독성을 높이기 위해서다.
- `help()`, `pydoc`, 단순 텍스트 출력에서도 완전히 깨지지 않아야 하지만, 1차 최적화 대상은 아니다.
- 형식 선택보다 중요한 것은 현재 코드의 런타임 동작을 정확히 설명하는 것이다.

## 2. 적용 범위와 강도

- 공개 API는 이 계약의 전체 형식을 MUST 따른다.
- 중요한 internal 메서드는 다음 중 하나에 해당하면 전체 형식을 SHOULD 따른다.
  - 입력 검증이나 제약이 비명백하다.
  - 콜백, 전략 함수, 의존성 주입처럼 호출 형태 설명이 중요하다.
  - 부작용, 프로세스 제어, 보안 위험, 외부 시스템 연동이 있다.
  - 외부 확장 지점이거나 유지보수자가 자주 참고해야 하는 동작이다.
- 단순 private helper, 자명한 one-liner wrapper, 내부 adapter, 단순 getter/setter는 한 줄 요약만 쓰거나 docstring을 생략할 수 있다.
- 같은 클래스 안에서도 모든 메서드를 같은 밀도로 문서화할 필요는 없다.

## 3. 전체 구조

모든 full docstring은 한 줄 요약으로 시작하며, 이후 섹션은 `###` 헤더를 사용한다.

```text
"""
한 줄 요약.

### Arguments
[arguments table or `None`]
### Returns
[return description]
### Example
[runnable example when included]
"""
```

### 최소 준수 양식

full docstring의 구조적 바닥은 한 줄 요약, `Arguments`, `Returns` 세 가지다. 다른 섹션은 근거가 있을 때만 추가한다.

```python
def unwrap_or(self, default: Any) -> Any:
    """
    Return the contained `data` if successful; otherwise return `default`.

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(R)** | `default` | `Any` | Fallback value used when the result is not successful. |

    ### Returns
    `Any` — The stored payload if successful, otherwise `default`.
    """
```

- 이보다 더 줄이려면 2장 기준으로 trivial helper로 보고 한 줄 요약만 남기거나 docstring을 생략한다.
- 공개 API와 중요한 internal 메서드는 여기에 runnable `Example`을 SHOULD 더한다. 전체 예시는 9.1을 참고한다.

## 4. 섹션 목록과 적용 조건

| 섹션 | 필수 여부 | 적용 조건 |
|------|-----------|-----------|
| 한 줄 요약 | 항상 | 모든 docstring의 첫 줄. |
| Arguments | 항상 | 인자가 없으면 `None`으로 표기. |
| Callable Signature | 조건부 | 콜러블, 콜백, 함수 리스트, 프로토콜이 핵심 입력일 때. |
| Enum | 조건부 | 실제 선택지가 제한되고 값에 따라 의미 분기가 있을 때만. 단순 `Optional[...]` 또는 넓은 타입 표기만으로는 만들지 않는다. |
| Constraint | 조건부 | 코드에 실제 검증 로직이 있을 때만. |
| Returns | 항상 | 반환 타입과 현재 구현 기준 의미를 적는다. |
| Raises | 조건부 | 함수가 의도적으로 예외를 raise 할 때만. 실패를 `Result`로 반환하는 경로는 적지 않는다. |
| Note | 선택 | fallback, 자동 계산, 캐시, lazy loading 같은 보충 설명이 필요할 때. |
| Warning | 선택 | 부작용, 비정상 종료, 보안 위험, 프로세스 교체, pickling 제약이 있을 때. |
| Example | 권장 | 공개 API와 중요한 internal 메서드는 SHOULD 포함한다. 포함할 경우 context-complete runnable 예시여야 한다. |

## 5. 섹션 순서

### 기본형

```text
Arguments -> Returns -> Example
```

### 확장형

```text
Arguments -> Callable Signature -> Enum -> Constraint -> Returns -> Raises -> Note -> Warning -> Example
```

### 위험성 강조 변형

Warning을 먼저 읽어야 하는 경우 Note와 Warning의 순서를 바꾼다.

```text
Arguments -> Callable Signature -> Enum -> Constraint -> Returns -> Raises -> Warning -> Note -> Example
```

## 6. 표현 표준

### 6.1 문장 종결

- 모든 Description, Note, Warning 문장은 마침표(`.`)로 끝낸다.
- 한 줄 요약도 마침표로 끝낸다.

### 6.2 기본값 표기

```text
Default: `value`.
```

- `Default is ...` 대신 `Default: \`value\`.`로 통일한다.
- `None`, `True`, `False`, 숫자, 문자열 모두 백틱으로 감싼다.

### 6.3 타입 표기

- Type 칼럼은 `typing` 표기를 따른다. 예: `Optional[int]`, `Union[str, Path]`, `List[str]`.
- 제네릭 내부 파라미터까지 가능한 범위에서 명시한다.
- 단일 타입도 백틱으로 감싼다. 예: `str`, `int`, `bool`.

### 6.4 참조 표기

- docstring 내에서 인자 이름은 항상 백틱으로 감싼다. 예: `workers`, `timeout`.
- 클래스, 함수, 반환 타입 참조도 백틱으로 감싼다. 예: `ThreadPoolExecutor`, `Result`.
- 리터럴 값도 백틱으로 감싼다. 예: `True`, `False`, `None`, `'sha256'`, `0`.

### 6.5 조건 표기

- 연산자와 조건식은 백틱으로 감싼다. 예: `> 0`, `>= 0 and <= 255`.
- 가능한 한 자연어보다 명시적 조건식을 사용한다.

## 7. 각 섹션의 양식

### 7.1 한 줄 요약

```python
"""
Execute tasks concurrently with `ThreadPoolExecutor`.
"""
```

- 영어, 동사 원형으로 시작하고 간결하게 쓴다.
- 주요 클래스나 함수명은 백틱으로 감싼다.
- 요약 뒤에는 빈 줄을 둔다.

### 7.2 Tag 범례

클래스 `__init__` docstring 상단에만 한 번 기재한다.

```text
- **(R)** = Required argument
- **(O)** = Optional argument (has a default value)
- **(D)** = Dependency Injection (advanced usage)
```

### 7.3 Arguments

Markdown 테이블 형식으로 작성한다.

```markdown
### Arguments
| Tag | Name | Type | Description |
|-----|------|------|-------------|
| **(R)** | `name` | `str` | User name. |
| **(O)** | `count` | `int` | Number of items. Default: `10`. |
| **(D)** | `manager` | `Optional[Manager]` | Manager instance. Default: built-in `Manager`. |
```

Tag 의미:

- **(R)** — Required. 기본값이 없는 필수 인자.
- **(O)** — Optional. 기본값이 있는 선택 인자.
- **(D)** — Dependency Injection. 테스트와 확장을 위한 주입 인자.

인자가 없을 때는 아래처럼 적는다.

```markdown
### Arguments
None
```

### 7.4 Callable Signature

콜러블 인자의 정확한 호출 형태를 blockquote로 기술한다.

```markdown
### Callable Signature
> `data` element: `Tuple[Callable[..., Any], Dict[str, Any]]`
> - `Callable[..., Any]` — Any function accepting keyword arguments.
> - `Dict[str, Any]` — Keyword arguments passed via `func(**kwargs)`.
```

- 첫 줄에 파라미터명과 전체 타입을 적는다.
- 하위 bullet에서 각 타입 요소를 설명한다.
- 실제 호출 형태를 설명할 수 있으면 `Callable[..., Any]`보다 구체적으로 적는다.

### 7.5 Enum

선택지가 제한된 인자를 blockquote + 테이블로 명시한다.
값 타입을 `type:` 행으로 먼저 선언한다.

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

- 실제 선택지가 제한되고 의미 분기가 있을 때만 넣는다.
- 단순 `Optional[int]`, `Union[str, int]` 같은 넓은 타입 표기만으로는 Enum 섹션을 만들지 않는다.

### 7.6 Constraint

유효성 제약은 blockquote + bullet list로 기술한다.
문장은 아래 허용 패턴만 사용한다.

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

- 코드에 실제 유효성 검증이 있을 때만 적는다.
- 코드에 없는 제약은 상식으로 보충하지 않는다.
- 복합 범위 조건은 RELATION 패턴으로 적는다. 예: `` `code` MUST satisfy `>= 0 and <= 255`. ``

### 7.7 Returns

```markdown
### Returns
`Result` — Contains the validated value in `data`.
```

- 타입을 백틱으로 감싼다.
- em dash(`—`) 뒤에 현재 구현 기준 설명을 붙인다.
- `Result`를 반환하면 `data`에 무엇이 담기는지 가능하면 적는다.

### 7.8 Raises

함수가 의도적으로 예외를 raise 할 때만 blockquote로 작성한다.

```markdown
### Raises
> - `ResultUnwrapException` — Raised when `success` is not `True`.
```

- 실제 `raise` 문이 있을 때만 적는다.
- 예외 타입은 백틱으로 감싸고, em dash(`—`) 뒤에 발생 조건을 적는다.
- 실패를 `Result`로 반환하는 경로는 `Raises`가 아니라 `Constraint`/`Returns`로 설명한다.

### 7.9 Note

보충 설명은 blockquote로 작성한다.

```markdown
### Note
> Worker count defaults to `os.cpu_count()` when `workers` is `None`.
```

### 7.10 Warning

주의 사항은 blockquote로 작성한다.

```markdown
### Warning
> This method does **not** return under normal circumstances.
```

보안 관련 주의 사항이 있으면 Warning 내부 최상단에 `**Security:**` 블록으로 구분한다.

```markdown
### Warning
> **Security:**
> - Input is not sanitized. Do not pass untrusted user input directly.
> - Pickle deserialization can execute arbitrary code.
>
> General warnings here.
```

### 7.11 Example

Example은 `>>>` REPL 형식으로 작성한다.

```markdown
### Example
>>> from tbot223_base.tbot223_Result import Result
>>> result = Result(success=True, error=None, context="Demo", data={"key": "value"})
>>> print(result.success)  # True
>>> print(result.data["key"])  # value
```

- 실제 import 경로와 실제 클래스명, 함수명을 사용한다.
- 필요한 인스턴스 생성, 보조 함수 정의, 최소 입력 데이터를 함께 적는다.
- 여러 줄 문장의 연속 행은 doctest 연속 프롬프트 `...`을 사용한다. 이 `...`은 코드 생략 표시가 아니라 입력 연속 표시다.
- 기대 출력은 결과 줄로 보여주거나 `# value`처럼 주석으로 표기한다.
- 코드 생략용 `...`, `foo`, `bar`, 미정의 `app_core` 같은 placeholder는 쓰지 않는다.
- 예시는 양식과 사용 흐름을 보여주기 위한 것이며, 환경에 따라 출력이 달라질 수 있어 자동 doctest 통과를 보장하지는 않는다.
- 부작용이 큰 메서드는 최소 호출 예시만 보여주고, 위험성은 `Warning`에서 먼저 설명한다.
- 현실적으로 과도한 setup이 필요하거나 파괴적 부작용이 커서 실행 예시가 오히려 오해를 부르면 Example을 생략할 수 있다.

## 8. 규칙 요약

1. full docstring은 한 줄 요약, Arguments, Returns를 항상 포함한다.
2. 공개 API와 중요한 internal 메서드는 runnable Example을 SHOULD 포함한다.
3. Example을 넣는다면 context-complete runnable 형태로 쓴다.
4. Callable Signature, Enum, Constraint는 근거가 있을 때만 추가한다.
5. Enum은 실제 제한된 선택지와 의미 분기가 있을 때만 쓴다.
6. Constraint는 허용된 정형 패턴만 사용한다.
7. Tag 범례는 클래스 `__init__`에만 한 번 기재한다.
8. 기본값은 `Default: \`value\`.` 형식으로 통일한다.
9. trivial private helper와 자명한 adapter는 한 줄 요약만 쓰거나 생략할 수 있다.
10. Raises는 실제 `raise` 문이 있을 때만 적고, `Result` 실패 반환은 적지 않는다.

## 9. 전체 예시 Docstring

### 9.1 기본형 예시

`tbot223_base`의 실제 `Result.unwrap_or`를 기준으로 한 기본형이다.

```python
def unwrap_or(self, default: Any) -> Any:
    """
    Return the contained `data` if successful; otherwise return `default`.

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(R)** | `default` | `Any` | Fallback value used when the result is not successful. |

    ### Returns
    `Any` — The stored payload if successful, otherwise `default`.

    ### Example
    >>> from tbot223_base.tbot223_Result import Result
    >>> result = Result(success=False, error="Not Found", context="FetchData", data=None)
    >>> print(result.unwrap_or({"key": "default"}))  # {'key': 'default'}
    """
```

### 9.2 Enum + Warning + Note 예시

`tbot223_base`의 실제 `ExceptionTracker.get_exception_info`를 기준으로 한 예시다. `mask_presets`가 실제 제한된 선택지이므로 Enum을 쓴다. 잘못된 입력을 거절하지 않고 무시하므로 Constraint 대신 Note로 적는다.

```python
def get_exception_info(
    self,
    error: Exception,
    mask_presets: Any = ("default",),
    mask_paths: Any = (),
) -> Result:
    """
    Build structured exception information.

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(R)** | `error` | `Exception` | The exception object to describe. |
    | **(O)** | `mask_presets` | `Any` | Named mask presets. Default: `("default",)`. |
    | **(O)** | `mask_paths` | `Any` | Extra paths to mask. Default: `()`. |

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
    > - `user_input`, `params`, `local_variables`, `traceback`, and `system_info` may contain sensitive data.
    > - Apply `mask_presets=("private", "traceback", "system_info")` before exposing error information outside a trusted boundary.

    ### Note
    > Unknown preset names and invalid mask paths are ignored rather than rejected.

    ### Example
    >>> from tbot223_base.tbot223_Exception import ExceptionTracker
    >>> tracker = ExceptionTracker()
    >>> try:
    ...     1 / 0
    ... except ZeroDivisionError as error:
    ...     result = tracker.get_exception_info(error, mask_presets=("private", "traceback"))
    >>> print(result.success)  # True
    """
```

### 9.3 Constraint + Raises 예시

`tbot223_base`의 실제 `Result.unwrap`을 기준으로 한 예시다. `success`가 `True`가 아니면 실제로 `ResultUnwrapException`을 raise 하므로 Constraint와 Raises를 함께 적는다.

```python
def unwrap(self) -> Any:
    """
    Return the contained `data` when the result represents success.

    ### Arguments
    None

    ### Constraint
    > - `self.success` MUST be `True`.

    ### Returns
    `Any` — The stored payload.

    ### Raises
    > - `ResultUnwrapException` — Raised when `success` is not `True`.

    ### Example
    >>> from tbot223_base.tbot223_Result import Result
    >>> result = Result(success=True, error=None, context="FetchData", data=42)
    >>> print(result.unwrap())  # 42
    """
```

**양식 설명용 예시.** 다음 두 예시(9.4, 9.5)는 양식을 보여주기 위한 것이다. 이 베이스 패키지에는 의존성 주입 인자나 콜러블 리스트 API가 없어, 동반 패키지(`tbot223_core`)에서 쓰일 법한 형태를 가정한다. 실제 작성 시에는 대상 코드의 실제 import 경로와 식별자를 쓴다.

### 9.4 클래스 `__init__`과 Tag 범례 예시 (양식 설명용)

Tag 범례는 클래스 `__init__` docstring 상단에 한 번만 기재한다. `(D)`는 의존성 주입 인자에 쓴다.

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

### 9.5 Callable Signature 예시 (양식 설명용)

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

## 10. 특수 형태 처리

대부분의 특수 형태는 새 섹션을 만들지 않고 기존 섹션을 재사용한다. 아래는 형태별 델타만 정리한 것이다.
`Result`는 실제 `NamedTuple`이므로 dataclass / NamedTuple 행은 실제 코드 기준이며, async, 제너레이터, 컨텍스트 매니저 행은 베이스 패키지에 해당 코드가 없어 양식 설명용이다.

| 형태 | 핵심 규칙 |
|------|-----------|
| `async def` / 코루틴 | 한 줄 요약은 동사 원형을 유지한다. `Returns`에 `await` 시 산출되는 타입과 의미를 적는다. 동시성, 취소, 비동기 side effect는 `Note`나 `Warning`에 적고, async 전용 섹션은 만들지 않는다. |
| 제너레이터 / 이터레이터 | `Returns`에 `Iterator[...]` 또는 `Generator[...]` 타입과 산출 의미를 적는다. lazy 평가나 1회 소비 같은 특성은 `Note`로 보충하고, 별도 Yields 섹션은 두지 않는다. |
| `*args` / `**kwargs` | `Arguments` 테이블의 Name을 `*args`, `**kwargs`로 그대로 적고 Type에는 각 요소 타입을 적는다. Tag는 보통 **(O)**로 둔다. |
| `@property` | `Arguments`는 `None`으로 둔다. 한 줄 요약은 값을 반환하는 동사형으로 쓰고 `Returns`만 필수다. setter는 값 인자 1개를 받는 메서드로 본다. property에는 코드 근거 없는 `Constraint`를 만들지 않는다. |
| 컨텍스트 매니저 | 한 줄 요약에 관리 대상 리소스를 적는다. `Returns`에는 `with` 블록에 바인딩되는 값을 적고, 셋업과 티어다운은 `Note`, 리소스 해제 보장이나 누수 위험은 `Warning`에 적는다. |
| dataclass / NamedTuple | 필드는 클래스 docstring에 `Arguments` 테이블 형식으로 한 번 정리한다. 메서드는 평소 규칙을 그대로 따른다. |

### `*args` / `**kwargs` 표기 예시

```markdown
### Arguments
| Tag | Name | Type | Description |
|-----|------|------|-------------|
| **(O)** | `*args` | `int` | Values to sum. |
| **(O)** | `**kwargs` | `str` | Named options forwarded to the handler. |
```

### 제너레이터 `Returns` 표기 예시

```markdown
### Returns
`Iterator[int]` — Yields each parsed line number in order.
```

### dataclass / NamedTuple 필드 표기 예시

`tbot223_base`의 실제 `Result`(`NamedTuple`) 필드 이름과 타입을 기준으로 한 클래스 레벨 필드 표다.

```markdown
### Arguments
| Tag | Name | Type | Description |
|-----|------|------|-------------|
| **(R)** | `success` | `bool` | Whether the operation succeeded. |
| **(R)** | `error` | `Optional[str]` | Error label when not successful. |
| **(R)** | `context` | `str` | Call-site context label. |
| **(R)** | `data` | `Any` | Payload carried on the result. |
```
