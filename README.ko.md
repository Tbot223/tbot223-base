[English](README.md)

> **재정비 상태 — `1.0.0a1`:** 이 저장소는 공개 릴리스 전에 다시 정비 중이다. production 사용을 권장하지 않으며 API, payload, 릴리스 보장은 호환성 지원 없이 바뀔 수 있다. 도입 전 [재정비 문서](docs/ko/rebuilding.md)를 읽어야 한다.
> 런타임 기준: package version `1.0.0a1` (`tbot223_base.__version__ == "1.0.0a1"`).

# tbot223-base

`tbot223-base`는 Python 코드에서 함수와 모듈 경계를 오가는 연산 결과와 안전한 예외 payload를 일관된 형식으로 전달하기 위한 작은 기반 패키지다.

핵심은 두 가지다.

- `Result`와 `ResultStatus`로 `success`, `failure`, `cancelled` 결과를 명시적으로 표현한다.
- `ExceptionTracker`로 내부 디버깅용 진단 정보와 외부 노출용 public-safe error payload를 분리한다.

## 설계 의도

`tbot223-base`는 다른 언어 API를 재현하려는 목적이 아니라 Python 코드 경계에서 결과를 안정적으로 주고받으려는 필요에서 출발했다. `Result`는 status, data, context, error text를 전달해 caller가 결과 처리 방식을 추측하지 않게 하는 Python 스타일의 작은 교환 프로토콜이다.

`ExceptionTracker`는 내부 진단 정보는 풍부하게 유지하면서 외부에는 traceback, local variable, system information, raw exception이 새지 않는 작은 public payload를 만든다.

## 현재 상태

이전 릴리스 라인은 타입과 안전성 계약이 실제 구현보다 앞서 있어 철회했다. 현재 알파 재정비에서는 `Result.data`를 필수로 만들고 raw reconstruction helper를 제거하며 debug system collection을 지연하고 문서를 실행 가능한 계약으로 검증한다. 이유, 현재 보장, 다음 게이트는 [재정비 문서](docs/ko/rebuilding.md)에 정리한다.

## 맞는 사용자

이 패키지는 함수, service, worker, module 경계에서 작은 typed result shape가 필요하고 API, UI, bot response, 기타 untrusted boundary에 노출할 public-safe error payload가 필요한 코드베이스를 위한 것이다.

Logging, tracing, metrics, observability, pattern matching, monadic result framework이 아니며 순수 local control flow에서 일반 Python exception을 대체하지도 않는다.

## 로컬 개발

`1.0.0a1`는 공개 설치 대상이 아니다. source checkout에서 작업한다.

```bash
python -m pip install -e ".[test,type,lint]"
pytest -q
python -m ruff check .
python -m ruff format --check .
```

## 빠른 시작

성공 result를 만들고 확인한다.

```python
from tbot223_base.result import Result

result = Result.ok({"user_id": 1}, context="FetchProfile")

if result.is_success:
    print(result.unwrap())
```

Public-safe exception payload를 반환한다. 이 경로는 debug system information을 수집하지 않는다.

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

- [재정비 상태](docs/ko/rebuilding.md)
- [한국어 문서](docs/ko/README.md)
- [English docs](docs/en/README.md)
- [Result 레퍼런스](docs/ko/reference/result.md)
- [ExceptionTracker 레퍼런스](docs/ko/reference/exception-tracker.md)
- [Package and CI guide](docs/ko/guides/package-and-ci.md)
- [API 계약](docs/contracts/ko/human/api-contract.md)
