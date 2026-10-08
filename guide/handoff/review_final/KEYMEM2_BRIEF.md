# 🔑 핵심·⚡ 암기 구조화 전면 개편(과목 하나 담당, 10-05 클라우드 · 2차)

사용자(10-05 원문): "강의자료 별 핵심 및 암기 정리에서 ⚡ 암기 * Total-etch = 도말층 다 제거 → enamel에 best * dentin엔 too aggressive · thick hybrid layer · deeply exposed collagen · leakage·biodegradation * Protocol: 인산 30-40% 15초(enamel → dentin) → primer rubbing 15초(wet bonding) → hydrophobic bonding → immediate 광중합 * 실패 원인: collagen 과건조 collapse · resin tag 부족 → 빈 공간 · 과노출 → MMP * Total-etch 장점 = micromechanical interlocking · smear layer removal · best approach for enamel * separated hydrophobic adhesive layer · sufficiently thick film · stress-absorbing 이거 보면 장점이 줄바꿈되어서 끊겨있고, 단점은 위에 가있고 단점이라고 표시도 안되어있고 일괄적으로 다 같은 기호로 시작하니까 가독성도 떨어지고, 암기라는게 일단 내용을 변형시키거나 너무 축약하지도 않는 선에서 깔끔하게 내가 구조화하고 이해하고 암기하기 쉽게 정리해야하는데 이건 그냥 단순히 나열이자나. 순서도 뒤죽박죽 중구난방에 구조화도 안되어있어서 한번에 읽히지도 않는!! 내가 지금 몇번씩 강의자료의 핵심과 암기란에 대해서 피드백을 주고 있는데, 더이상 안 줘도 되게끔 완벽하게! 면밀히 모든 과목 모든 강의자료의 핵심,암기탭을 검토해서, 가장 최적으로 효과적 효율적으로 구조화하고 정리한 형태가 될 수 있게끔 전면적으로 개선해줘!! 이때 내용을 줄이고 변형시키고 압축하라는게 절대 아니고, 너의 최적 판단 아래 핵심 및 암기하면 좋을 내용을 정리하는건데, 적절한 줄바꿈과 들여쓰기, 글머리기호 등을 사용해서 가장 최적으로 효과적 효율적으로 정리해달라는거야."

이전 지시(KEYMEM_BRIEF.md — 누락·짝·기출·강조 보강, 요약 탭이 되지 않게)는 그대로 유효. 이번은 **구조·순서·라벨**을 카드마다 다시 짠다.

## 대상
맡은 과목 `tools/<sid>/lec_*.txt`의 **모든 카드**의 `=` 🔑 핵심 줄과 `M:` ⚡ 암기 줄. 본문·표·E:·P:·U:는 근거로 읽기만(고치지 않음).

## 카드마다 이렇게 다시 짠다
1. **논리 순서로 다시 놓기**: 정의/개념 → 분류·종류 → 특징·기전 → 장점 → 단점·한계 → 적응증/금기 → 술식 순서(Protocol) → 실패·합병증 → 비교(vs) → 수치. (그 카드에 있는 것만. 본문 `#` 소제목 순서를 기본 뼈대로.)
2. **한 덩어리 = 한 `M:` 줄 + 라벨**: 같은 대상의 사실은 한 줄로 모으고 맨 앞에 라벨 `장점:`·`단점:`·`적응증:`·`금기:`·`술식 순서:`·`실패 원인:`·`특징:`·`정의:`·`분류:` 등(콜론 라벨 — 화면에서 굵은 머리). 라벨 없이 시작하는 줄이 앞 줄의 일부(예 '단점'인데 표시 없음)면 라벨을 붙여 제자리로.
   - 예(위 사용자 예, CONS Total-etch):
     - `M: 정의: Total-etch = 도말층 다 제거 → enamel에 best`
     - `M: 장점: ① micromechanical interlocking ② smear layer removal ③ best approach for enamel ④ separated hydrophobic adhesive layer ⑤ sufficiently thick film ⑥ stress-absorbing`
     - `M: 단점(dentin엔 too aggressive): ① thick hybrid layer ② deeply exposed collagen ③ leakage·biodegradation`
     - `M: 술식 순서: ① 인산 30-40% 15초(enamel → dentin) ② primer rubbing 15초(wet bonding) ③ hydrophobic bonding ④ immediate 광중합`
     - `M: 실패 원인: ① collagen 과건조 → collapse ② resin tag 부족 → 빈 공간 ③ 과노출 → MMP`
     - (10-07 정정 — 이 줄은 장점의 나머지 3개라 위 장점 줄에 ④⑤⑥으로 합침이 맞음: 자료의 한 목록은 ⚡에서도 한 라벨 아래 · RULES 6이 이김)
3. **글머리·들여쓰기 = 기호로**(렌더러가 바꿔 줌):
   - 개수·순서·나열 3개↑ → `라벨: ① … ② … ③ …` (머리 + 들여 쓴 번호 목록)
   - 서로 다른 사실 → ` / `(줄마다 한 줄) (라벨 줄 안에서는 그 라벨 아래 ◦ 하위 — 라벨과 무관한 사실은 따로 M:, 10-08)
   - 짝 비교 → `A: … / B: …` 또는 `A {r:…} ↔ B {r:…}` (공통 머리가 있으면 `머리: A … / B …` — 10-08 자가골 예, A·B 뒤 콜론 없이)
   - 한 대상 안의 짧은 나열(2개) → ` · `
   - 위계: `② 머리: ① … ② …`(바깥 번호 + 안쪽 번호)도 됨
   - `=`는 '정의·대응(약어=풀이, 기호=값)'일 때만, 한 줄에 하나.
4. **🔑(`=` 줄)**: 카드의 뼈대 한두 줄 — 무엇이고(정의) 시험에서 무엇이 갈리는지. 3개↑ 나열이면 `머리: ① … ② … ③ …`, 서로 다른 사실은 ` / `. 이미 좋은 🔑은 그대로.
5. **분량·내용**: 줄이거나 바꾸거나 압축하지 않음 — 원래 ⚡·🔑의 사실은 모두 남김(낱말을 다듬는 정도·라벨·조사·기호 추가는 됨). 같은 사실이 두 줄에 겹치면 하나로 합침(사실은 남김). 새 사실은 본문·표·E:·P:·U:에 있는 것만(빠진 기출·강조·짝이면 더함 — KEYMEM 규칙). Claude 지식·자료에 없는 약어 금지. (10-07 — 번호 항목 한 개의 낱말 길이는 FWBAL·RULES 6: 짧은 원문은 풀 워딩, 문장처럼 긴 원문은 원문 핵심어를 살린 압축. '압축 금지'는 사실을 빼지 말라는 뜻)
6. **⚡ 줄 수**: 카드당 보통 3~7줄. 줄 하나가 플래시카드 한 장 — 한 줄에 한 덩어리(라벨 하나).

## 플래시카드 기록
⚡ 줄을 합치거나 라벨을 붙이면 줄 글자가 바뀐다 — 메인이 빌드에서 '옛 줄 글자가 새 줄 안에 들어 있으면(기호·번호·공백 무시) 기록을 넘기는' 규칙을 넣으므로, **옛 줄의 낱말은 가능한 한 그대로 새 줄 안에** 두라(라벨·번호·기호만 덧붙임). 낱말을 바꾼 줄은 보고에 적음.

## 검사(고친 뒤 꼭)
- `.venv/bin/python tools/dump_breaks.py <SID> <키>` — 🔑·⚡ 화면 조각에 줄바꿈 오류 0(조사·'—'·'→'로 시작하는 조각, 찢긴 사실, 빈 조각, `{r:}` 짝 깨짐 없음).
- `.venv/bin/python tools/check_lec.py <SID>` ✗ 0 · `.venv/bin/python tools/check_abbr.py <SID>`(새 약어 0) · `.venv/bin/python tools/check_eyears.py` 0.
- 빌드·커밋·git stash·브라우저 금지. lec_*.txt 밖·다른 과목 수정 금지. 공용 scratchpad에 스크립트를 쓸 때는 `<SID>_` 접두어 파일명으로(다른 담당자와 겹치지 않게).

## 보고 `work/review_final2/KM2_<SID>.md`
카드마다 한 줄(⚡ 전→후 줄 수 · 라벨·순서 · 더한 사실 · 낱말 바꾼 줄) · 합계. 최종 답 5줄.
