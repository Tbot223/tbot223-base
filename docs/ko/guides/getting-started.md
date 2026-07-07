[English](../../en/guides/getting-started.md)

> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.1.0"`.

# Getting Started

이 가이드는 repository checkout 또는 editable install 상태에서 `tbot223-base`를 import해 쓰는 가장 작은 흐름을 보여준다.

## 설계 의도

`tbot223-base`의 설계는 다른 언어의 API를 재현하려는 시도보다, Python 코드의 경계에서 결과를 안정적으로 주고받으려는 필요에서 출발했다. Rust의 `Result`는 독자가 비교할 수 있는 기준일 수 있지만, 이 패키지의 원형이나 호환 목표는 아니다.

여기서 `Result`는 함수 사이에서 status, data, context, error text를 안정적으로 주고받기 위한 Python 스타일의 교환 프로토콜이다.

`ExceptionTracker`는 경계에서 안전하게 에러를 다루기 위한 도구다. Public payload에 traceback, local variable, system information, raw exception detail을 노출하지 않으면서 내부 진단 정보를 유지하고 싶을 때 사용한다.

## 전제 조건

- Python을 사용할 수 있어야 한다.
- repository checkout이 `PYTHONPATH`에 있거나, 현재 작업 디렉터리가 repository root이거나, checkout이 editable mode로 설치되어 있어야 한다.
- 현재 repository는 local package tooling용 `pyproject.toml` packaging metadata를 정의한다.

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
