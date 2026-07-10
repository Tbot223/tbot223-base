[English](../../en/guides/examples.md)

> 런타임 기준: package version 1.0.0rc1 (`tbot223_base.__version__ == "1.0.0rc1"`).

# 실행 가능한 예시

이 가이드는 `examples/` 아래의 독립 실행 예시 스크립트와 source checkout에서 실행하는 방법을 정리한다.

## 전제 조건

- Repository root에서 명령을 실행한다.
- Python 3.10 이상을 사용한다.
- 이 checkout에서 실행할 때는 package install이 필요 없다. 각 script가 repository root를 `sys.path`에 추가한다.
- Result 예시는 `examples/result/` 아래에 두고, exception boundary 예시는 `examples/exception_tracker/` 아래에 둔다.

## 스크립트

| Script | 보여주는 내용 |
| --- | --- |
| `examples/result/result_status_flow.py` | `ResultStatus.SUCCESS`, `ResultStatus.FAILURE`, `ResultStatus.CANCELLED`, `unwrap_or()`, `expect()`. |
| `examples/exception_tracker/public_exception_payload.py` | API, UI, bot response 같은 untrusted boundary에 내보낼 public-safe exception payload. |
| `examples/exception_tracker/debug_exception_payload.py` | Location, context, traceback-frame count, masked system information을 포함하는 masked debug payload. |
| `examples/exception_tracker/decorator_boundary.py` | `ExceptionTrackerDecorator`가 function boundary의 uncaught exception을 failure `Result`로 바꾸는 흐름. |
| `examples/exception_tracker/threaded_shared_tracker.py` | 하나의 `ExceptionTracker` instance를 여러 `ThreadPoolExecutor` worker에서 공유하는 흐름. |

## 실행

```bash
python examples/result/result_status_flow.py
python examples/exception_tracker/public_exception_payload.py
python examples/exception_tracker/debug_exception_payload.py
python examples/exception_tracker/decorator_boundary.py
python examples/exception_tracker/threaded_shared_tracker.py
```

일부 출력에는 생성된 ID, timestamp, local file path, traceback location이 포함되므로 machine마다 정확한 문자열은 달라질 수 있다.

## 시작점으로 사용하기

필요한 boundary에 맞는 script 형태를 가져가면 된다.

- 명시적인 outcome을 반환하는 함수가 필요하면 `examples/result/result_status_flow.py`를 참고한다.
- Trusted process boundary 밖으로 나갈 payload가 필요하면 `examples/exception_tracker/public_exception_payload.py`를 참고한다.
- 내부 진단 정보는 풍부하게 유지하되 masking이 필요하면 `examples/exception_tracker/debug_exception_payload.py`를 참고한다.
- 작은 function wrapper에서 uncaught exception을 `Result` 값으로 바꾸고 싶으면 `examples/exception_tracker/decorator_boundary.py`를 참고한다.
- 여러 thread worker에서 하나의 tracker instance를 공유해야 하면 `examples/exception_tracker/threaded_shared_tracker.py`를 참고한다.

## 확인

```bash
python -m py_compile examples/result/result_status_flow.py examples/exception_tracker/public_exception_payload.py examples/exception_tracker/debug_exception_payload.py examples/exception_tracker/decorator_boundary.py examples/exception_tracker/threaded_shared_tracker.py
```
