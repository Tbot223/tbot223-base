[English](../../en/guides/package-and-ci.md)

> 런타임 기준: package version 1.0.0rc1 (`tbot223_base.__version__ == "1.0.0rc1"`).

# Package and CI Guide

이 가이드는 local `pyproject.toml` 설정, Python compatibility CI workflow, release-only publish workflow 사용법을 설명한다.

Release, CI, Docker, repository maintenance 명령은 공개 package README가 사용자 중심으로 유지되도록 root README가 아니라 이 문서에서 다룬다.

## Local editable 설치

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
- package name, README, license, authors, classifiers, project URLs, `requires-python` 같은 metadata.
- `tbot223_base.__version__`에서 package version을 읽는 dynamic version 설정.
- optional `test` dependency group.
- build와 metadata validation tool을 위한 optional `release` dependency group.
- test tool과 release tool을 함께 설치하는 optional `dev` dependency group.
- `tbot223_base` package discovery.
- type-aware tooling을 위한 `py.typed` 포함.
- pytest 기본 `tests` path.

## Local release 도구

재사용 가능한 release tooling은 package extra로 설치한다.

```bash
python -m pip install -e ".[test,release]"
```

그 다음 release readiness check를 실행한다.

```bash
scripts/check-release-readiness.sh v1.0.0rc1
```

`v1.0.0rc1` tag가 local에 있고 `origin/main`을 확인할 수 있는 상태에서는 strict release mode를 사용한다.

```bash
scripts/check-release-readiness.sh --strict-release v1.0.0rc1
```

Release gate는 stable `vMAJOR.MINOR.PATCH` tag와 release candidate `vMAJOR.MINOR.PATCHrcN` tag를 모두 허용한다. 앞의 `v`를 제거한 문자열은 여전히 `tbot223_base.__version__`과 정확히 같아야 한다.

이 script는 metadata check, Python compile check, `pytest`, `actionlint`, `git diff --check`, temporary source/wheel build, `twine check`, distribution metadata assertion을 실행한다.

Host-only로 사용할 때는 `actionlint` binary를 별도로 설치해야 한다. Docker check에는 이미 포함되어 있다.

## Docker 점검

Host Python tooling에 의존하지 않고 같은 check를 실행하고 싶으면 Docker를 사용한다.

```bash
docker compose run --build --rm test
```

```bash
docker compose run --build --rm check
```

`test` service는 `pytest -q`만 실행한다. `check` service는 `test`, `release` dependency group을 설치하고 `actionlint`를 포함한 image 안에서 `scripts/check-release-readiness.sh v1.0.0rc1`을 실행한다.

## Compatibility CI

`.github/workflows/python-compatibility.yml` workflow는 push, pull request, manual dispatch에서 실행된다.

또한 `workflow_call`을 지원하므로 publish workflow가 package upload 전에 같은 compatibility matrix를 요구할 수 있다.

현재 matrix는 다음과 같다.

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

Compatibility workflow는 push와 pull request에서 자동 실행된다. Release-like checkpoint, public API 변경, payload contract 변경, Python support range 변경 전에는 manual dispatch로도 실행하는 것이 좋다.

작은 local-only 변경은 현재 checkout에서 `pytest -q`만 실행해도 보통 충분하다.

## Publish workflow

`.github/workflows/publish.yml` workflow는 GitHub Release가 published 상태가 될 때만 실행된다.

Package를 upload하기 전에 다음을 검증한다.

- release에 tag가 있다.
- tag가 stable `vMAJOR.MINOR.PATCH` 또는 release candidate `vMAJOR.MINOR.PATCHrcN` 형식을 사용한다. 예: `v1.0.0rc1`.
- tag가 `origin/main`에 포함된 commit을 가리킨다.
- 앞의 `v`를 제거한 tag version이 `tbot223_base.__version__`과 일치한다.
- Python compatibility matrix가 통과한다.
- source distribution과 wheel distribution이 정상적으로 build된다.
- 생성된 distribution을 `twine check`가 통과시킨다.

Publish job은 GitHub OIDC 기반 PyPI Trusted Publishing을 사용한다. 첫 release를 publish하기 전에 PyPI trusted publisher를 설정해야 한다.

PyPI Trusted Publisher에는 다음 값을 사용한다.

- Repository owner: `Tbot223`
- Repository name: `tbot223-base`
- Workflow: `publish.yml`
- Environment name: `pypi`

## 릴리스 체크리스트

`1.0.0rc1`의 expected release tag는 `v1.0.0rc1`이다.

Stable release는 계속 `vMAJOR.MINOR.PATCH`를 사용하고, release candidate는 `vMAJOR.MINOR.PATCHrcN`를 사용한다. 두 경우 모두 package version 앞에 `v`만 붙인 exact tag를 사용한다.

1. Release commit을 `main`에 merge하거나 fast-forward한다.
2. `tbot223_base.__version__`이 의도한 release version과 일치하는지 확인한다.
3. GitHub Release를 만들기 전에 신호를 보고 싶으면 compatibility workflow를 manual dispatch로 실행한다.
4. `main` commit에 version tag를 만든다.
5. `scripts/check-release-readiness.sh --strict-release v1.0.0rc1` 또는 `docker compose run --build --rm check --strict-release v1.0.0rc1`을 실행한다.
6. 그 tag에서 GitHub Release를 publish한다.

Tag, branch ancestry, package version, tests, build, metadata check가 release contract와 맞지 않으면 publish workflow는 PyPI upload 전에 중단된다.
