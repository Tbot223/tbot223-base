[English](../en/README.md)

> 런타임 기준: package version 1.0.0 (`tbot223_base.__version__ == "1.0.0"`).

# tbot223-base 문서

`Result`, `ResultStatus`, `ExceptionTracker`를 사용하는 한국어 문서다.

## 시작하기

- [Root README](../../README.ko.md): 프로젝트 개요, 설계 의도, 맞는 사용자, 트레이드오프, 빠른 시작.
- [Getting Started](guides/getting-started.md): checkout 또는 editable install 기준 import와 핵심 API 사용법.
- [실행 가능한 예시](guides/examples.md): `examples/` 아래의 standalone script로 `Result`와 `ExceptionTracker` 흐름 실행.
- [Package and CI Guide](guides/package-and-ci.md): `pyproject.toml`, editable install, compatibility CI, release publishing 사용법.

## 레퍼런스

- [Result 레퍼런스](reference/result.md): 상태 모델, `success=` shorthand, unwrap 계열 helper.
- [ExceptionTracker 레퍼런스](reference/exception-tracker.md): debug payload, public payload, masking, safe context capture 정책.

## 릴리스 노트

- [릴리스 노트](release-notes.md)

## 계약 문서

- [문서 작성 계약](../contracts/README.md)
- [API 계약](../contracts/ko/human/api-contract.md)
