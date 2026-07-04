[English](../../en/reference/result.md)

> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.0.1"`.

# Result 레퍼런스

이 문서는 `ResultStatus`, `Result`, `ResultUnwrapException`을 설명한다.

## ResultStatus

`ResultStatus`는 세 가지 상태를 가진 string enum이다.

| Value | Meaning |
| --- | --- |
| `ResultStatus.SUCCESS` | 작업이 성공했다. |
| `ResultStatus.FAILURE` | 작업이 실패했다. |
| `ResultStatus.CANCELLED` | 작업이 취소되었거나 실행되지 않았다. |

`ResultStatus.normalize()`는 `ResultStatus`, legacy `bool`, `None`, 유효한 status string을 받는다.

## Result

`Result[T]`는 immutable tuple-like container이며 다음 필드를 가진다.

| Field | Type | Meaning |
| --- | --- | --- |
| `status` | `ResultStatus` | 정규화된 작업 상태. |
| `error` | `Optional[str]` | 사람이 읽을 수 있는 에러 텍스트. |
| `context` | `Optional[str]` | 작업 맥락. |
| `data` | `T` | 작업이 반환한 payload. |

Legacy `success=` 생성자 인자는 계속 지원된다. 새 코드는 `status=ResultStatus...`를 우선 사용한다.

Payload 타입을 알고 있다면 `Result[T]`를 사용한다. `unwrap()`과 `expect()`는 `T`를 반환하고, `unwrap_or(default)`는 `T` 또는 default 값 타입을 반환한다.

## Predicate

- `result.success`: legacy tri-state 호환 property이며 `True`, `False`, `None`을 반환한다.
- `result.is_success`: `ResultStatus.SUCCESS`일 때만 `True`.
- `result.is_failure`: `ResultStatus.FAILURE`일 때만 `True`.
- `result.is_cancelled`: `ResultStatus.CANCELLED`일 때만 `True`.

## Unwrap helper

- `unwrap()`: 성공이면 `T`를 반환하고, 아니면 `ResultUnwrapException`을 raise한다.
- `expect(msg="")`: 성공이면 `T`를 반환하고, 아니면 custom message로 raise한다.
- `unwrap_or(default)`: 성공이면 `T`, 아니면 `default`를 반환한다.

## Example

```python
from tbot223_base.tbot223_Result import Result, ResultStatus

result: Result[dict[str, str]] = Result(ResultStatus.FAILURE, "not found", "LoadProfile", None)

if result.is_failure:
    fallback = result.unwrap_or({"name": "anonymous"})
    print(fallback)
```
