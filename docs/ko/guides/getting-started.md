[English](../../en/guides/getting-started.md)

> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.0.1"`.

# Getting Started

이 가이드는 repository checkout 또는 editable install 상태에서 `tbot223-base`를 import해 쓰는 가장 작은 흐름을 보여준다.

## 전제 조건

- Python을 사용할 수 있어야 한다.
- repository checkout이 `PYTHONPATH`에 있거나, 현재 작업 디렉터리가 repository root이거나, checkout이 editable mode로 설치되어 있어야 한다.
- 현재 repository는 local package tooling용 최소 `pyproject.toml` packaging metadata를 정의한다.

## Import 경로

새 코드는 canonical module path를 사용한다.

- `tbot223_base.result`
- `tbot223_base.exception_tracker`

## Result 기본 사용

```python
from tbot223_base.result import Result, ResultStatus

result: Result[dict[str, str]] = Result(
    status=ResultStatus.SUCCESS,
    error=None,
    context="LoadConfig",
    data={"mode": "dev"},
)

if result.is_success:
    print(result.unwrap())
```

명시적인 status 처리가 필요하면 `ResultStatus.SUCCESS`, `ResultStatus.FAILURE`, `ResultStatus.CANCELLED`를 사용한다. `success=` 생성자 인자는 tri-state shorthand로도 지원된다.

## Public 예외 payload

```python
from tbot223_base.exception_tracker import ExceptionTracker

tracker = ExceptionTracker()

try:
    1 / 0
except Exception as error:
    result = tracker.get_public_exception_return(
        error,
        error_code="DIVIDE_BY_ZERO",
        public_message="The calculation could not be completed.",
        public_context="Calculator.Divide",
        tags={"layer": "service"},
        retryable=False,
    )
    print(result.data)
```

API 응답, UI, 외부 경계처럼 raw exception detail을 노출하면 안 되는 곳에서는 public 경로를 사용한다.

## Debug 예외 payload

```python
from tbot223_base.exception_tracker import ExceptionTracker

tracker = ExceptionTracker()

try:
    1 / 0
except Exception as error:
    result = tracker.get_exception_info(
        error,
        mask_presets=("private", "traceback", "system_info"),
    )
    print(result.error)
```

Debug 경로는 traceback과 context metadata를 포함할 수 있다. Context 값은 작고 안전할 때만 복사되며, 무거운 값은 `"<BLOCKED>"`로 대체된다.

## 확인

```bash
pytest
```
