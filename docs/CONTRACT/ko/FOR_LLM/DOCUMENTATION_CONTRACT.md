[English](../../en/FOR_LLM/DOCUMENTATION_CONTRACT.md)

> Contract revision: 2026-06-23.

# Documentation Contract for LLM

> Python docstring이 아닌 저장소 Markdown 문서를 작성하거나 수정할 때 따르는 실행 지시서.

## 먼저 읽을 것

반드시 [../FOR_HUMAN/DOCUMENTATION_CONTRACT.md](../FOR_HUMAN/DOCUMENTATION_CONTRACT.md)를 먼저 읽는다.

- 사람용 문서가 정본이다.
- 이 문서는 실행용 보조 지시서다.
- 사람용 정본과 충돌하면 사람용 정본이 우선이다.

## 목표

- 모든 문서를 똑같이 만들지 않고도 전체 스타일을 통일한다.
- 문서 유형을 유지한다.
- 대응하는 en/ko 문서가 있으면 파일 경로를 맞춘다.
- TODO.md는 이 계약 범위에서 제외한다.
- 기본 Markdown 방언은 GitHub Flavored Markdown으로 본다.
- README, Guide, Reference는 런타임 기준 정보를, Contract는 `Contract revision` 또는 `Last updated`를 상단 메타에 둔다.

## 작업 절차

1. 현재 문서가 README, Guide, Reference, Release Notes, Contract 중 무엇인지 먼저 판별한다.
2. 대상 독자와 언어를 확인한다.
3. README, Guide, Reference라면 저장소에서 검증 가능한 런타임 기준 정보를 먼저 확인한다.
4. Contract라면 저장소에서 확인 가능한 revision 날짜나 명시적 revision 라벨을 먼저 확인한다.
5. 상단 메타 블록을 `언어 링크 -> 기준 정보 -> 제목` 순서로 둔다. 대응 언어 문서가 없으면 `기준 정보 -> 제목`으로 시작할 수 있다.
6. 문서 상단에서 이 파일의 목적이 드러나게 만든다.
7. 그 문서 유형의 기본형을 적용한다.
8. GitHub에서 자연스럽게 렌더링되는 구조를 우선한다.
9. 내부 링크는 상대 경로로 유지한다.
10. 이중 언어 쌍이 있으면 경로와 파일명을 맞춘다.

## 문서 유형 판단 기준

### README

- 진입점 문서다.
- 방향 제시와 안내가 완전한 설명보다 중요하다.
- 더 깊은 문서로 연결해야 한다.

### Guide

- 작업, 마이그레이션, 설정, 워크스루 흐름이 있다.
- 순서, 전환, 단계 구분이 중요하다.
- 독자가 한 상태에서 다른 상태로 가도록 도와야 한다.

### Reference

- 찾아보는 문서다.
- 구조적이고 모호함이 적어야 한다.
- Example은 동작 해설이 필요할 때만 넣는다.

### Release Notes

- 버전 단위 변경 보고다.
- 변경 종류별로 묶는다.
- 사실 중심으로 유지한다.
- 버전 히스토리 자체가 기준 정보이므로 런타임 기준이나 revision 표기를 따로 요구하지 않는다.

### Contract

- 규칙 문서다.
- 범위와 규범 문장이 중요하다.
- 패키지 버전보다 문서 정책 revision을 우선 표시한다.
- 필요할 때 MUST, SHOULD, MAY를 쓴다.

## 추출 규칙

- 저장소에서 확인 가능한 사실만 유지한다.
- 명령어, 버전, 마이그레이션 보장, 테스트 결과를 지어내지 않는다.
- README, Guide, Reference에서 정확한 릴리스 버전을 검증할 수 없으면 `current dev branch 기준`, `main branch HEAD 기준`처럼 검증 가능한 임시 기준을 쓰고, 추정 버전을 만들지 않는다.
- Contract 문서에는 패키지 버전을 추정해서 쓰지 않는다. 저장소에서 확인 가능한 revision 날짜나 명시적 revision 라벨만 사용한다.
- 문서를 다른 유형으로 조용히 바꾸지 않는다.
- README 문체를 계약 문서나 레퍼런스에 복사하지 않는다.
- 새로 작성하거나 수정한 구간에 현재 저장소의 `.markdownlint.jsonc` 기준에서 피할 수 있는 경고를 만들지 않는다.
- 파일에 기존 markdownlint 경고가 있으면, 현재 저장소의 `.markdownlint.jsonc` 기준에서 비용이 낮은 항목은 가능하면 함께 줄인다.
- 저장소 설정에서 비활성화된 구조 규칙은 억지로 맞추려고 문서 구조를 뒤집지 않는다.
- TODO 성격 문장, 초안 메모, 잡담성 표현을 최종 결과에 남기지 않는다.

## 이중 언어 규칙

- 대응 언어 파일이 있으면 경로와 파일명은 맞춘다.
- 섹션 순서는 달라도 되지만 범위는 어긋나지 않게 유지한다.
- 상단 근처에 언어 전환 링크를 둔다.
- en/ko 쌍 중 하나를 갱신하면 기준 정보 표기도 함께 점검한다.

## 마무리 전 확인

- README, Guide, Reference라면 상단에 런타임 기준 정보가 있는가?
- Contract라면 상단에 `Contract revision` 또는 `Last updated`가 있는가?
- 기준 정보가 저장소에서 검증 가능한 사실인가?
- 첫 블록에서 이 문서의 용도가 보이는가?
- 구조가 문서 유형에 맞는가?
- GitHub에서 자연스럽게 렌더링되는가?
- 헤더 깊이가 과도하지 않은가?
- 코드 블록에 언어 태그가 있는가?
- 링크가 상대 경로인가?
- 현재 저장소의 `.markdownlint.jsonc` 기준에서 새 경고를 추가하지 않았는가?
- 초안 전용 문장을 제거했는가?

## 붙여넣기용 프롬프트

```text
먼저 docs/CONTRACT/ko/FOR_HUMAN/DOCUMENTATION_CONTRACT.md를 읽고,
그 다음 docs/CONTRACT/ko/FOR_LLM/DOCUMENTATION_CONTRACT.md를 실행 지시서로 사용해서
방금 준 Markdown 문서를 작성하거나 수정해줘.
문서 유형을 유지하고, 저장소에서 확인 가능한 사실만 남기고,
README, Guide, Reference라면 상단 메타를 언어 링크 -> 기준 정보 -> 제목 순서로 두고,
Contract라면 패키지 버전 대신 Contract revision 또는 Last updated를 두고,
GitHub Flavored Markdown과 GitHub 렌더링을 기준으로 맞추고,
대응하는 이중 언어 파일이 있으면 경로를 맞추고,
정확한 릴리스 버전을 모르면 추정하지 말고 검증 가능한 임시 기준으로 쓰고,
현재 저장소의 .markdownlint.jsonc 기준에서 새 경고는 만들지 말고,
최종 결과에는 TODO 성격 문장이나 초안 메모를 남기지 마.
```
