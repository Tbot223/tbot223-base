[English](../../en/llm/api-contract.md)

> Contract revision: 2026-07-07.

# API Contract for LLM

> API, payload, import path, compatibility behavior를 수정할 때 따르는 실행 지시서.

## 먼저 읽을 것

먼저 [../human/api-contract.md](../human/api-contract.md)를 읽는다.

- 사람용 API 계약이 정본 규칙이다.
- 이 문서는 정본 요약이 아니라 실행용 보조 지시서다.

## 작업 절차

1. 변경이 public API, payload shape, import path, package-level export, validation tooling에 닿는지 확인한다.
2. 사용자가 breaking migration을 명시적으로 요청하지 않았다면 canonical import path를 유지한다.
3. Package-level public export를 canonical module object와 맞춘다.
4. `Result`는 Rust compatibility target이 아니라 독립적으로 형성된 Python 경계 교환 프로토콜로 설명한다.
5. public/debug payload shape가 바뀌면 완료로 보기 전에 테스트를 갱신한다.
6. public payload에는 debug-only field가 들어가지 않게 한다.
7. debug payload safety behavior를 명시적으로 유지한다: safe copy, `"<BLOCKED>"`, capture 이후 masking.
8. 지원 Python version range가 바뀌면 `pyproject.toml`, CI workflow, 사용자 문서를 함께 갱신한다.
9. 현재 checkout에서 가능한 local verification command를 실행한다.

## 테스트 기대값

API에 민감한 변경은 다음을 실행하는 것이 좋다.

```bash
pytest -q
python -m py_compile tbot223_base/__init__.py tbot223_base/result.py tbot223_base/exception_tracker.py
git diff --check
```

CI를 사용할 수 있으면 release-like checkpoint 전에 optional Python compatibility workflow를 실행한다.

## 하지 말 것

- Public payload에 traceback, params, user input, local variables, system information을 노출하지 않는다.
- API 계약에 문서화하지 않은 alternate public import path를 추가하지 않는다.
- Breaking change를 문서화하지 않고 `ResultStatus` string value를 바꾸지 않는다.
- Payload behavior를 바꾸면서 동작 테스트 없이 문서만 갱신하지 않는다.
