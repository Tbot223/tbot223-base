[English](../../en/guides/package-and-ci.md)

> Runtime baseline: current `dev` branch checkout with `tbot223_base.__version__ == "0.0.1"`.

# Package and CI Guide

이 가이드는 local `pyproject.toml` 설정과 optional Python compatibility CI workflow 사용법을 설명한다.

## Local Editable Install

Checkout을 수정하면서도 import는 설치된 package처럼 동작하게 보고 싶을 때 editable install을 쓴다.

```bash
python -m pip install -e ".[test]"
```

그 다음 테스트를 실행한다.

```bash
pytest -q
```

## `pyproject.toml` 역할

`pyproject.toml`은 modern Python tooling이 읽는 표준 package metadata entry point다.

이 repository에서는 다음을 정의한다.

- build backend로 `setuptools` 사용.
- package name, version, README, license, `requires-python` 같은 metadata.
- Python 3.10보다 낮은 버전을 위한 `typing-extensions`.
- optional `test` dependency group.
- `tbot223_base` package discovery.
- type-aware tooling을 위한 `py.typed` 포함.
- pytest 기본 `tests` path.

## Optional Compatibility CI

`.github/workflows/python-compatibility.yml` workflow는 manual-only다. GitHub Actions UI에서 사용자가 선택했을 때 실행된다.

현재 matrix는 다음과 같다.

- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13
- Python 3.14

각 job은 package와 test dependency를 설치한 뒤 다음을 실행한다.

```bash
pytest -q
```

## 언제 실행할까

Release-like checkpoint, public API 변경, payload contract 변경, Python support range 변경 전에는 optional compatibility workflow를 실행하는 것이 좋다.

작은 local-only 변경은 현재 checkout에서 `pytest -q`만 실행해도 보통 충분하다.
