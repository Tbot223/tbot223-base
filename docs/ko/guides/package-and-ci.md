[English](../../en/guides/package-and-ci.md)

> 런타임 기준: `1.0.0a1` 기반 미배포 working tree. 이번 수정은 기존 release tag에 포함되지 않는다.

# Package and CI Guide

이 가이드는 재정비 alpha의 local package 도구, compatibility workflow, prerelease-only publish gate를 설명한다. 공개를 승인하는 문서가 아니므로 먼저 [재정비 문서](../rebuilding.md)를 읽는다.

## 로컬 개발

```bash
python -m pip install -e ".[test,type,lint,release]"
npm ci
pytest -q
python -m mypy
python scripts/check-rejected-types.py
python -m ruff check .
python -m ruff format --check .
python scripts/check-docstring-contract.py
npx --no-install markdownlint-cli2 "**/*.md" "#node_modules"
```

Package에는 runtime dependency가 없다. `test`, `type`, `lint`, `release` extra는 local verification용이다. Ruff와 Markdownlint는 development-only이며 Python package에 포함되지 않는다.

## Release readiness

정확한 alpha tag text로 complete local gate를 실행한다.

```bash
scripts/check-release-readiness.sh v1.0.0a1
```

Strict mode는 tag가 `HEAD`를 가리키고 worktree가 clean하며 local `origin/main`을 확인할 수 있어야 한다.

```bash
scripts/check-release-readiness.sh --strict-release v1.0.0a1
```

허용 tag는 stable `vMAJOR.MINOR.PATCH`, alpha `vMAJOR.MINOR.PATCHaN`, release-candidate `vMAJOR.MINOR.PATCHrcN`이다. 앞의 `v`를 뺀 문자열은 `tbot223_base.__version__`과 정확히 같아야 한다.

Script는 Python compile check, pytest와 deterministic docstring doctest, AST docstring-contract validation, positive/negative mypy check, Ruff lint/format check, Markdownlint, actionlint, diff whitespace check, source/wheel build, `twine check`, distribution inspection, isolated-wheel smoke test를 실행한다.

## Docker check

```bash
docker compose run --build --rm test
docker compose run --build --rm check
```

`check` image는 `actionlint`, Ruff, development-only Markdownlint CLI를 설치하고 완전한 `v1.0.0a1` readiness check를 실행한다.

## Compatibility CI

`.github/workflows/python-compatibility.yml`은 Python 3.10부터 3.14에서 push, pull request, manual dispatch, reusable-workflow invocation마다 실행한다. Pytest, public consumer typing, 각 주석으로 지정한 잘못된 consumer line과 예상 mypy error code, Ruff lint/format, docstring contract, Markdownlint를 검증한다.

## Publish workflow

`.github/workflows/publish.yml`은 GitHub Release가 published일 때만 시작한다. Version과 일치하는 `main` tag, compatibility workflow, build/wheel check, PyPI Trusted Publishing을 요구한다.

Alpha와 release-candidate tag는 GitHub prerelease option을 켜야 한다. Stable tag는 끄고 publish한다. `1.0.0a1`은 재정비 alpha이므로 프로젝트가 명시적으로 승인하기 전에는 release를 만들거나 distribution을 publish하지 않는다.

## Source archive 검증

Ubuntu에서는 Python 3.10–3.14를 검증하고 Windows와 macOS에서는 Python 3.12도 검증한다. 별도 필수 workflow job이 actionlint를 실행한다.

sdist에는 Python 검증 script, Node manifest·lockfile, Markdownlint 설정과 workflow 파일이 포함된다. 명시된 개발 도구를 설치하고 `npm ci`를 실행하면 Git metadata 없이 non-strict readiness script를 실행할 수 있다. Strict mode는 실제 Git checkout, 일치하는 tag, 깨끗한 worktree를 요구하며 source archive만으로 릴리스 출처를 확인하지 않는다.
