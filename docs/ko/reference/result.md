[English](../../en/reference/result.md)

> 런타임 기준: `1.0.0a1` 기반 미배포 working tree. 이번 수정은 기존 release tag에 포함되지 않는다.

# Result 레퍼런스

이 alpha 레퍼런스는 `ResultStatus`, `Result`, `ResultUnwrapException`을 설명한다.

## ResultStatus

`ResultStatus`는 `SUCCESS`, `FAILURE`, `CANCELLED` 세 값을 가진 string enum이다. `ResultStatus.normalize()`는 enum, tri-state shorthand(`True`, `False`, `None`), 유효한 status string을 받는다.

## Result Shape

`Result[T]`는 `(status, error, context, data)` 순서의 immutable tuple-like value다. Indexing, unpacking, structural pattern matching, tuple equality를 유지한다.

| Field | Type | Meaning |
| --- | --- | --- |
| `status` | `ResultStatus` | 정규화된 outcome 상태. |
| `error` | `Optional[str]` | 사람이 읽을 수 있는 error text. |
| `context` | `Optional[str]` | operation context. |
| `data` | `T` | 모든 상태에서 필요한 payload. |

`data`는 의도적으로 `None`인 경우에도 반드시 제공해야 한다. Result가 payload type을 조용히 바꾸지 않도록 `_make()`, `_replace()`는 public API가 아니며 제공하지 않는다.

## 생성

새 코드에서는 typed factory를 우선 사용한다.

```python
from tbot223_base.result import Result

success = Result.ok({"name": "Ada"}, context="LoadProfile")
failure = Result.failure(None, error="not found", context="LoadProfile")
cancelled = Result.cancelled(None, context="LoadProfile")
```

정규화된 status form이 필요하면 explicit construction도 사용할 수 있다.

```python
from tbot223_base.result import Result, ResultStatus

result: Result[int] = Result(ResultStatus.SUCCESS, None, "Compute", 42)
```

`success=` input과 `result.success` property는 이 alpha 동안 tri-state shorthand로 유지한다. `result.success`는 `True`, `False`, `None`을 반환하고 `is_success`, `is_failure`, `is_cancelled`는 boolean predicate다.

## Unwrap helper

- `unwrap()`은 success일 때만 `T`를 반환한다.
- `expect(msg="")`는 success일 때만 `T`를 반환하고 실패 시 `msg`를 기록한다.
- `unwrap_or(default)`는 success일 때 `T`, 그 외에는 전달한 default를 반환한다.

`unwrap()`과 `expect()`는 non-success result에서 `ResultUnwrapException`을 raise한다. 고정된 메시지는 저장된 `error`, `context`, `data`를 stringification하지 않으며 원본 값은 exception attribute로 남는다.

## Import 경로

`Result`, `ResultStatus`, `ResultUnwrapException`은 `tbot223_base.result`에서 import한다.

## 복사와 정적 타입

Payload가 해당 연산을 지원하면 `copy.copy`, `copy.deepcopy`, 표준 pickle 왕복은 result field를 유지한다. 얕은 복사는 payload를 공유하고 깊은 복사는 payload도 복사한다. 복원 과정도 명시적 data를 요구하며 `_make`, `_replace`를 다시 제공하지 않는다.

고정 tuple 타입은 음수 index를 포함한 literal indexing과 unpacking에서 각 field 타입을 유지한다. 동적 index와 slice에는 일반 tuple typing 규칙을 적용한다. Container는 immutable이며 payload 자체의 mutability는 바뀌지 않는다.
