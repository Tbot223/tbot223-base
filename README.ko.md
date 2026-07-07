[English](README.md)

> 런타임 기준: package version 0.1.0 (`tbot223_base.__version__ == "0.1.0"`).

# tbot223-base

`tbot223-base`는 Python 코드에서 함수와 모듈 경계를 오가는 연산 결과와 안전한 예외 payload를 일관된 형식으로 전달하기 위한 작은 기반 패키지다.

핵심은 두 가지다.

- `Result`와 `ResultStatus`로 `success`, `failure`, `cancelled` 결과를 명시적으로 표현한다.
- `ExceptionTracker`로 내부 디버깅용 진단 정보와 외부 노출용 public-safe error payload를 분리한다.

## 설계 의도

`tbot223-base`의 설계는 다른 언어의 API를 재현하려는 시도보다, Python 코드의 경계에서 결과를 안정적으로 주고받으려는 필요에서 출발했다.

Rust의 `Result`는 독자가 비교할 수 있는 기준일 수 있지만, 이 패키지의 원형이나 호환 목표는 아니다. 여기서 `Result`는 Python 스타일의 교환 프로토콜이다. 함수가 결과 상태, data, context, error text를 안정적으로 전달하게 해주는 작은 값의 형태이며, caller가 결과를 어떻게 처리할지 추측하지 않게 만든다.

`ExceptionTracker`는 경계에서 안전한 에러 처리를 하기 위해 존재한다. 에러를 숨기거나 무조건 터뜨리는 대신, 내부 진단 정보는 풍부하게 유지하고 외부에는 traceback, local variable, system 정보, raw exception이 새지 않는 작은 public payload를 만든다.

## 맞는 사용자

이 패키지는 다음을 원하는 코드베이스에 잘 맞는다.

- 함수, service, worker, module 경계에서 사용할 안정적인 result shape.
- 계층마다 새로운 dict 형태를 만들지 않고 success, failure, cancellation을 반환하는 가벼운 방식.
- API, UI, bot response, 외부 경계에 노출해도 안전한 error payload.
- Public response보다 풍부하게 유지되는 내부 debug diagnostics.
- Framework가 아니라 작고 typed된 utility package.

특히 operation result가 단순한 local implementation detail이 아니라 component 사이의 interface 일부일 때 유용하다.

## 트레이드오프

`Result`는 outcome을 명시적으로 만든다. 대신 caller와 callee가 structured value를 주고받고 확인하는 방식에 합의해야 한다. 아주 작은 script나 일반 exception 흐름이 이미 가장 명확한 코드에서는 불필요한 형식이 될 수 있다.

`ExceptionTracker`는 public payload와 debug payload를 의도적으로 분리한다. Public boundary에서는 더 안전하지만, 명시적으로 안전한 public text를 넘기지 않는 한 public response에는 raw exception message, traceback frame, local variable, system information이 들어가지 않는다.

이 패키지는 다음이 아니다.

- Rust-compatible `Result` 구현체.
- Pattern matching 또는 monadic result framework.
- Logging, tracing, metrics, observability system.
- 순수 local control flow 안에서 Python exception을 대체하는 도구.

## 설치

```bash
python -m pip install tbot223-base
```

Source checkout에서 local development를 할 때는 다음처럼 설치한다.

```bash
python -m pip install -e ".[test]"
```

## 빠른 시작

Result를 만들고 확인한다.

```python
from tbot223_base.result import Result, ResultStatus

result: Result[dict[str, int]] = Result(
    status=ResultStatus.SUCCESS,
    error=None,
    context="FetchProfile",
    data={"user_id": 1},
)

if result.is_success:
    print(result.unwrap())
```

Public-safe exception payload를 반환한다.

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
        retryable=False,
    )
    print(result.data)
```

## 문서

사용자 문서:

- [한국어 문서](docs/ko/README.md)
- [English docs](docs/en/README.md)
- [Getting Started](docs/ko/guides/getting-started.md)
- [Result reference](docs/ko/reference/result.md)
- [ExceptionTracker reference](docs/ko/reference/exception-tracker.md)
- [API 계약](docs/contracts/ko/human/api-contract.md)

Repository 관리 문서:

- [Package and CI guide](docs/ko/guides/package-and-ci.md)
- [릴리스 노트](docs/ko/release-notes.md)
