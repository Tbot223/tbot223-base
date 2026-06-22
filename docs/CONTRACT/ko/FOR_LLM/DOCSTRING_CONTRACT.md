[English](../../en/FOR_LLM/DOCSTRING_CONTRACT.md)

> Contract revision: 2026-06-23.

# Docstring Contract for LLM

> 이 문서는 사람이 읽는 계약서가 아니라, LLM이 docstring 생성 작업을 수행할 때 직접 따라야 하는 실행 지시서다.

## 먼저 할 일

이 문서를 읽기 전에 반드시 [../FOR_HUMAN/DOCSTRING_CONTRACT.md](../FOR_HUMAN/DOCSTRING_CONTRACT.md)를 먼저 읽는다.

- `FOR_HUMAN` 문서는 규약의 정본이다.
- 이 문서는 정본을 요약 대체하지 않는다.
- 작성 중 충돌이 생기면 사람용 정본이 우선이다.

## 목표

- 현재 코드의 런타임 동작을 우선으로 docstring을 작성한다.
- Markdown-heavy 형식은 유지하되, Markdown을 렌더링하는 IDE hover/peek를 1차 소비자로 가정한다.
- `Constraint`는 코드의 검증 로직에서만 추출한다.
- `Example`은 실제 import, 인스턴스화, 보조 함수 정의까지 포함한 context-complete runnable 예제로 작성한다.

## 읽기 절차

1. 먼저 [../FOR_HUMAN/DOCSTRING_CONTRACT.md](../FOR_HUMAN/DOCSTRING_CONTRACT.md)를 끝까지 읽는다.
2. 렌더링 대상, 적용 범위, 섹션 구조, 표현 규칙을 이해한다.
3. 그 다음 이 문서를 읽고, 실제 코드에서 무엇을 추출해야 하는지 확인한다.
4. 작성 중 충돌이 생기면 사람용 정본 기준으로 되돌린다.

## 우선순위

1. 코드의 실제 동작.
2. 현재 함수 시그니처와 반환 방식.
3. 사람용 정본 계약서의 적용 범위, 섹션 구조, 표현 규칙.
4. 이 문서의 추출 규칙과 체크리스트.
5. 문체의 완성도와 장식.

형식보다 런타임 진실이 우선이다. 근거가 부족하면 섹션을 억지로 채우지 않는다.

## 작업 절차

1. 함수 시그니처를 읽는다.
2. 이 함수가 공개 API인지, 중요한 internal인지, trivial helper인지 먼저 판단한다.
3. 함수 본문에서 입력 검증, 가드 절, 실패 반환, 예외 발생 지점, 자동 보정, side effect를 찾는다.
4. 근거를 바탕으로 `Arguments`, `Callable Signature`, `Enum`, `Constraint`, `Returns`, `Raises`, `Note`, `Warning`, `Example`을 필요한 만큼만 작성한다.
5. `Arguments`와 `Returns`는 full docstring에서는 항상 넣는다.
6. `Enum`은 실제 제한된 선택지와 의미 분기가 있을 때만 넣는다.
7. `Example`을 넣는다면 실제 import, 실제 클래스명, 실제 함수명, 인스턴스화, 필요한 보조 함수 정의까지 포함한다.

## 적용 범위 판단 규칙

- 공개 API는 full docstring을 기본값으로 본다.
- 중요한 internal 메서드는 다음 중 하나면 full docstring 후보로 본다.
  - 검증 로직이 비명백하다.
  - 콜백, 함수 리스트, 의존성 주입이 핵심 입력이다.
  - side effect, 프로세스 제어, 보안 위험이 있다.
  - 유지보수자가 자주 참고해야 하는 확장 지점이다.
- trivial private helper, 단순 adapter, 자명한 one-liner wrapper는 한 줄 요약만 쓰거나 생략할 수 있다.

## Constraint 추출 규칙

### 핵심 원칙

- `Constraint`는 코드에 있는 검증 로직만 반영한다.
- 주석, 의도, 미래 계획, TODO는 `Constraint` 근거가 아니다.
- fallback이나 자동 보정은 거절 조건이 아니므로 보통 `Note`로 간다.
- `raise`뿐 아니라 `return Result(False, ...)` 같은 실패 경로도 제약 근거로 본다.
- 허용 패턴 밖의 자유 서술 제약은 만들지 않는다.

### 근거로 인정할 코드 패턴

- `if not isinstance(...)`
- `if len(data) == 0`
- `if value not in (...)`
- `if workers > len(data) and not override`
- `if chunk_size is not None and chunk_size < 0`
- `raise ValueError(...)`, `raise TypeError(...)`, `raise KeyError(...)`
- `return Result(False, ...)` 또는 이에 준하는 실패 반환

### 허용 패턴

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

### 정형 패턴 매핑 예시

| 코드 형태 | docstring 패턴 |
| --- | --- |
| `if not isinstance(data, str):` | `data` MUST be `str`. |
| `if algorithm not in ['md5', 'sha1', 'sha256', 'sha512']:` | `algorithm` MUST be one of `'md5', 'sha1', 'sha256', 'sha512'`. |
| `if workers > len(data) and not override:` | `workers` MUST satisfy `<= len(data)` unless `override` is `True`. |
| `if chunk_size is not None and chunk_size < 0:` | If `chunk_size` is not `None`, `chunk_size` MUST satisfy `>= 0`. |
| `if code < 0 or code > 255:` | `code` MUST satisfy `>= 0 and <= 255`. |

### 금지 사항

- 코드에 없는 제약을 상식으로 보충하지 않는다.
- 미래에 필요해 보이는 제약을 미리 적지 않는다.
- 단순 타입 표기만 보고 Enum을 만들지 않는다.
- 내부 구현이 자동 보정하는 동작을 실패 제약처럼 쓰지 않는다.
- `Callable[..., Any]`라는 타입 힌트만 보고 실제 호출 의미를 생략하지 않는다.

## Raises 추출 규칙

- `Raises`는 함수가 실제로 `raise` 하는 예외만 적는다.
- `raise ValueError(...)`, `raise ResultUnwrapException(...)`처럼 직접 raise 하는 지점을 근거로 본다.
- 실패를 `return Result(False, ...)`로 표현하는 경로는 `Raises`가 아니라 `Constraint`/`Returns`로 적는다.
- 호출하는 내부 함수가 raise 할 수 있어도, 현재 함수가 명시적으로 다루지 않으면 추정해서 적지 않는다.
- 예외 타입은 백틱으로 감싸고 발생 조건을 함께 적는다.

## Example 작성 규칙

- 실제 import 경로와 실제 클래스명을 사용한다.
- 예제 안의 인스턴스 생성, 보조 함수 정의, 최소 입력 데이터까지 포함해 바로 실행 가능한 형태로 쓴다.
- 여러 줄 문장의 연속 행은 doctest 연속 프롬프트 `...`을 쓴다. 이 `...`은 입력 연속 표시이며 코드 생략 표시가 아니다.
- 기대 출력은 결과 줄로 보여주거나 `# value`처럼 주석으로 표기한다.
- 코드 생략용 `...`, `func1`, `val1`, 미정의 `app_core` 같은 placeholder는 금지한다.
- 부작용이 큰 함수는 최소 호출 예제만 보여주고, 위험성은 `Warning`에 적는다.
- 현실적으로 과도한 setup이 필요하거나 파괴적 부작용이 커서 runnable Example이 오히려 오해를 부르면 Example을 생략할 수 있다.

## 특수 형태 추출 규칙

특수 형태는 새 섹션을 만들지 않고 기존 섹션에 매핑한다.

- `async def`나 `await`가 보이면, `Returns`에 `await` 결과 타입을 적는다. 동시성·취소 동작은 `Note`나 `Warning`으로 보내고 async 전용 섹션은 만들지 않는다.
- 함수 본문에 `yield`가 있으면 제너레이터로 보고, `Returns`에 `Iterator[...]` / `Generator[...]`와 산출 의미를 적는다. 별도 Yields 섹션은 만들지 않는다.
- `*args`, `**kwargs`는 `Arguments` 테이블의 Name에 `*args`, `**kwargs` 그대로 적고 Type에 요소 타입을 적는다.
- `@property`는 `Arguments`를 `None`으로 두고 `Returns`만 필수로 본다. property에 코드 근거 없는 `Constraint`를 만들지 않는다. setter는 값 인자 1개 메서드로 본다.
- `__enter__` / `__exit__`나 `@contextmanager`가 보이면, `Returns`에 `with` 바인딩 값을 적고 해제 보장·누수 위험은 `Warning`, 셋업/티어다운은 `Note`로 적는다.
- `NamedTuple`이나 `@dataclass`는 필드를 클래스 docstring에 `Arguments` 테이블 형식으로 한 번 정리한다.

## 섹션별 체크리스트

### Arguments

- 시그니처에 있는 인자만 적는다.
- 기본값이 있으면 `Default: \`value\`.` 형태를 유지한다.

### Callable Signature

- 콜러블이 핵심 인자일 때만 넣는다.
- 실제 호출 형태를 설명할 수 있으면 `Callable[..., Any]`보다 구체적으로 쓴다.

### Enum

- 실제 선택지가 제한될 때만 넣는다.
- 값 타입을 `type:` 행으로 먼저 선언한다.

### Constraint

- 코드 근거가 있는 검증만 적는다.
- 허용된 정형 패턴만 사용한다.
- 코드에 없는 검증은 한 줄도 추가하지 않는다.

### Returns

- 현재 함수의 실제 반환 타입을 적는다.
- `Result`를 반환하면 `data`에 무엇이 담기는지도 현재 코드 기준으로 적는다.

### Raises

- 실제 `raise` 문이 있을 때만 적는다.
- `Result` 실패 반환은 `Raises`에 적지 않는다.

### Note

- fallback, 자동 계산, lazy loading, 캐시 동작 같은 보충 정보를 적는다.
- 입력 거절 조건을 `Note`에 숨기지 않는다.

### Warning

- 비정상 종료, 프로세스 교체, 보안 리스크, pickling 제약, side effect가 있을 때만 적는다.

### Example

- import가 빠졌는지 다시 본다.
- 인스턴스화가 빠졌는지 다시 본다.
- 보조 함수 정의가 필요한데 빠뜨리지 않았는지 본다.
- `...`나 미정의 식별자가 남아 있지 않은지 점검한다.

## 출력 전에 확인할 것

- 이 함수가 full docstring 대상인지 먼저 판단했는가.
- 사람이 준 코드와 시그니처를 바꾸지 않았는가.
- `Constraint`가 실제 if 문, raise, 실패 반환에서만 나왔는가.
- `Raises`가 실제 `raise` 문에서만 나왔는가.
- `Enum`이 실제 제한된 선택지를 반영하는가.
- `Example`이 placeholder 없이 runnable한가.
- `Returns`가 현재 구현과 맞는가.
- 형식이 부족하더라도 허구의 내용을 채우지 않았는가.
- full docstring 바닥은 한 줄 요약 + `Arguments` + `Returns`이고, 공개 API에는 runnable `Example`을 더했는가.
- async, 제너레이터, `@property`, 컨텍스트 매니저, `NamedTuple` 같은 특수 형태를 기존 섹션 매핑 규칙대로 처리했는가.

## 붙여넣기용 프롬프트

```text
먼저 docs/CONTRACT/ko/FOR_HUMAN/DOCSTRING_CONTRACT.md를 읽고 규약을 익힌 뒤,
docs/CONTRACT/ko/FOR_LLM/DOCSTRING_CONTRACT.md를 작업 지시서로 사용해서 방금 준 코드의 docstring을 작성해줘.
Markdown-heavy 형식은 유지하되 Markdown을 렌더링하는 IDE hover/peek를 1차 소비자로 가정하고,
공개 API와 중요한 internal 메서드는 full docstring 대상으로 보고,
Constraint는 코드의 if문, raise, 실패 반환 로직을 분석해서 허용된 정형 패턴으로만 작성하고,
Enum은 실제 제한된 선택지가 있을 때만 넣고,
Example은 실제 import, 인스턴스화, 보조 함수 정의까지 포함한 runnable 형태로 작성해줘.
코드에 없는 제약과 placeholder 예시는 절대 추가하지 마.
```
