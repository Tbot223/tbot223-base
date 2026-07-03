[English](../../en/guides/getting-started.md)

> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.0.1"`.

# Getting Started

이 가이드는 repository checkout 상태에서 `tbot223-base`를 바로 import해 쓰는 가장 작은 흐름을 보여준다.

## 전제 조건

- Python을 사용할 수 있어야 한다.
- repository checkout이 `PYTHONPATH`에 있거나 현재 작업 디렉터리가 repository root여야 한다.
- 현재 repository에는 packaging metadata가 없으므로 `pip install` 기반 설치를 단정하지 않는다.

## Result 기본 사용

```python
from tbot223_base.tbot223_Result import Result, ResultStatus

result = Result(
    status=ResultStatus.SUCCESS,
    error=None,
    context="LoadConfig",
    data={"mode": "dev"},
)

if result.is_success:
    print(result.unwrap())
```

새 코드는 `ResultStatus.SUCCESS`, `ResultStatus.FAILURE`, `ResultStatus.CANCELLED`를 우선 사용한다. Legacy `success=` 생성자 인자는 호환성을 위해 유지된다.

## Public 예외 payload

```python
from tbot223_base.tbot223_Exception import ExceptionTracker

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
from tbot223_base.tbot223_Exception import ExceptionTracker

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

Debug 경로는 traceback과 context metadata를 포함할 수 있다. Context 값은 raw object reference가 아니라 제한된 snapshot으로 저장된다.

## 확인

```bash
pytest
```
