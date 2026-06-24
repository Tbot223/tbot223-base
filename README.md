> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.0.1"`.

# tbot223-base

`tbot223-base`는 연산 결과와 예외 정보를 일관된 형식으로 전달하기 위한 기초 Python 모듈 저장소다.

이 저장소는 두 가지 축에 집중한다. 하나는 `Result`와 `ResultStatus`를 통한 상태 전달이고, 다른 하나는 `ExceptionTracker`를 통한 예외 정보 수집과 표준화된 실패 반환이다.

## 대상과 목적

- 여러 계층에서 동일한 성공/실패/취소 상태 모델을 공유하려는 코드베이스
- 내부 디버깅용 예외 payload와 외부 노출용 경량 예외 payload를 분리하려는 서비스 경계
- 공통 반환 규약과 예외 처리 규약을 작은 기반 모듈로 유지하려는 프로젝트

## 핵심 구성

- [`tbot223_base/tbot223_Result.py`](tbot223_base/tbot223_Result.py): `ResultStatus`, `Result`, `ResultUnwrapException`을 제공한다.
- [`tbot223_base/tbot223_Exception.py`](tbot223_base/tbot223_Exception.py): `ExceptionTracker`, `ExceptionTrackerDecorator`, 내부 debug payload, 외부 public payload 구성을 제공한다.
- [`tbot223_base/__init__.py`](tbot223_base/__init__.py): 현재 패키지 버전 `0.0.1`을 노출한다.

## 상태 모델

`Result`의 정식 상태 표면은 `status`다. `ResultStatus.SUCCESS`, `ResultStatus.FAILURE`, `ResultStatus.CANCELLED`를 사용해 연산 상태를 명시적으로 전달한다.

호환성을 위해 `Result(success=...)`와 `result.success`도 여전히 지원한다. 새 코드는 `status`와 `result.is_success` 계열 프로퍼티를 우선 사용하는 편이 자연스럽다.

```python
from tbot223_base.tbot223_Result import Result, ResultStatus

result = Result(
    status=ResultStatus.SUCCESS,
    error=None,
    context="FetchProfile",
    data={"user_id": 1},
)

if result.is_success:
    print(result.data)
```

## 예외 처리 모델

`ExceptionTracker`는 같은 예외를 두 가지 목적에 맞게 다룬다.

- `get_exception_info()` / `get_exception_return()`: traceback, local variables, system info까지 포함할 수 있는 내부 debug 경로
- `get_public_exception_info()` / `get_public_exception_return()`: 외부 응답에 노출할 수 있도록 경량화한 public 경로

이 구분 덕분에 내부 진단 정보와 외부 노출 정보를 같은 구조에 억지로 섞지 않아도 된다.

```python
from tbot223_base.tbot223_Exception import ExceptionTracker

tracker = ExceptionTracker()

try:
    1 / 0
except Exception as error:
    public_result = tracker.get_public_exception_return(
        error,
        error_code="DIVIDE_BY_ZERO",
        public_message="The calculation could not be completed.",
        public_context="Calculator.Divide",
        tags={"layer": "service"},
        retryable=False,
    )
    print(public_result.data)
```

## 테스트

이 저장소의 현재 테스트 스위트는 `pytest` 기준으로 작성되어 있다.

```bash
pytest
```

테스트는 `Result` 상태 모델, unwrap 계열 동작, `ExceptionTracker`의 debug/public 분리, decorator 기반 실패 반환을 확인한다.

## 추가 문서

- [docs/CONTRACT/README.md](docs/CONTRACT/README.md): 저장소 문서 계약 진입점
- [docs/CONTRACT/ko/FOR_HUMAN/DOCUMENTATION_CONTRACT.md](docs/CONTRACT/ko/FOR_HUMAN/DOCUMENTATION_CONTRACT.md): 현재 README가 따른 일반 문서 계약
- [docs/DOCSTRING_CONTRACT.md](docs/DOCSTRING_CONTRACT.md): docstring 계약의 호환성 안내 경로
