> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.0.1"`.

# tbot223-base

`tbot223-base`는 Python 코드에서 연산 결과와 예외 정보를 일관된 형식으로 전달하기 위한 작은 기반 모듈이다.

핵심은 두 가지다.

- `Result`와 `ResultStatus`로 성공, 실패, 취소 상태를 명시적으로 표현한다.
- `ExceptionTracker`로 내부 디버깅용 예외 정보와 외부 노출용 public error payload를 분리한다.

## Documents

- [Documentation home](docs/README.md)
- [Korean docs](docs/ko/README.md)
- [English docs](docs/en/README.md)
- [Contract docs](docs/contracts/README.md)
- [Package and CI guide](docs/ko/guides/package-and-ci.md)

## Quick Example

```python
from tbot223_base.result import Result, ResultStatus

result: Result[dict[str, int]] = Result(
    status=ResultStatus.SUCCESS,
    error=None,
    context="FetchProfile",
    data={"user_id": 1},
)

if result.is_success:
    print(result.data)
```

## Development Check

```bash
python -m pip install -e ".[test]"
```

```bash
pytest
```

현재 테스트는 `Result` 상태 모델, unwrap 계열 동작, `ExceptionTracker` debug/public 분리, decorator 기반 실패 반환을 확인한다. GitHub Actions의 optional compatibility workflow는 Python 3.9부터 3.14까지 같은 테스트를 실행한다.
