[English](../en/README.md)

> Contract revision: 2026-06-23.

# Contract Docs

> 저장소 문서 작성 계약의 진입점이다.

## 계약 종류

### 일반 문서 계약

- [human/documentation-contract.md](human/documentation-contract.md): 저장소 Markdown 문서용 정본 계약이다.
- [llm/documentation-contract.md](llm/documentation-contract.md): AI가 일반 문서를 작성하거나 수정할 때 따르는 실행 지시서다.

### 독스트링 계약

- [human/docstring-contract.md](human/docstring-contract.md): Python docstring용 정본 계약이다.
- [llm/docstring-contract.md](llm/docstring-contract.md): AI가 docstring을 작성하거나 수정할 때 따르는 실행 지시서다.

## 권장 사용 방식

- README, 가이드, 레퍼런스, 릴리스 노트, 계약 문서를 다룰 때는 일반 문서 계약부터 본다.
- Python docstring을 다룰 때는 독스트링 계약부터 본다.
- AI 작업에서는 해당 종류의 사람용 계약을 먼저 읽고 LLM 실행 지시서를 나중에 작업 지시서로 준다.

## 저장소 결정 사항

- 적용 범위는 README 계열, 가이드/레퍼런스/릴리스 문서, 계약 문서다.
- TODO.md, 코드 주석, 비-Markdown 소스 파일은 범위에서 제외한다.
- en/ko 문서가 모두 있을 때는 경로를 맞춘다.
- 이 저장소의 일반 문서 계약은 중간 강도다. 프레임은 맞추되 문장 자체는 유연하게 둔다.

## 경로 정책

- 이 README를 계약 진입점으로 사용한다.
- 정본 계약 문서는 이 lowercase path tree 아래에 둔다.
- 실제 계약 문서는 이 디렉토리 트리 아래를 기준으로 본다.
