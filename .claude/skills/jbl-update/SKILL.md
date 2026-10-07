---
name: jbl-update
description: 26년도(새 연도) 강의자료 반영 또는 새 강의·새 과목 정리본을 한 번에 '완성본'까지 — 자료 받기 → 작성 → 독립 검토 3회 → 화면 다듬기(🔑⚡·JB 해설·줄바꿈·표·예상문제·공부 전략) → 사용자 눈 QA → 빌드·전 검사 → 배포·보고. 사용자가 "26년도 자료 반영해 줘", "○○ 강의자료 새로 올렸어", "○○ 정리본 만들어 줘", "/jbl-update [SID…]"라고 할 때 쓴다.
---

# JBL 업데이트 — 한 번에 완성본까지

심미치과학(ESTH)은 정리본을 만든 뒤 사용자 지적 수십 번(필사본 반려 → 카드형 → 검토 3회 → 줄바꿈 3회 → 번호·들여쓰기 → 표 → JB 해설 5회 → 🔑⚡ 3회 …)을 거쳐 지금 모양이 됐다. 이 스킬은 그 **모든 회차를 처음부터 차례로 한 번에** 돌려, 사용자가 다시 지적하지 않아도 되는 완성본을 만든다.

## 먼저 읽기(매번)
1. `CLAUDE.md` · `.claude/skills/jbl-update/RULES.md`(**최종형** — 모든 담당이 처음부터 이 모양으로) · `QA.md`(사용자 눈 점검표) · `AGENTS.md`(담당 지시문 틀)
2. `guide/피드백기록.md` 맨 아래 20줄(최근 지시) · `guide/과목노트_<SID>.md` · `guide/정리본_원칙.md`
3. 사용자 메시지는 **원문 그대로** `guide/피드백기록.md`에 한 줄 추가(작업 중 새 지시가 와도 매번). 새 규칙이면 RULES.md·QA.md에도 넣는다(다음에 같은 지적이 없게).

## 진행 원칙
- 결정이 꼭 필요한 것만 2~3안으로 묻고(강의 신설·삭제·교수 변경, 자료가 서로 모순, 근거 자료 없음) 나머지는 멈추지 않는다. 묻는 동안 다른 강의는 계속.
- 단계마다 짧게 보고(한국어). "얼마나 남았어?"엔 단계·남은 담당 수로 분 단위 추정.
- 담당이 끝날 때마다 **그 담당 파일만** 커밋·푸시(작업 브랜치). docs/는 빌드가 끝난 뒤에만 커밋. `work/`·`materials/`·`jb/`·`reference/`는 절대 커밋하지 않는다.
- 오래 걸리는 명령(빌드·전 검사 40분)은 Bash `run_in_background`로. `cmd &`로 띄우지 않는다(호출이 끝나면 같이 죽음). 기다릴 땐 `until …; do sleep; done` 한 번.
- 병렬 담당 수: 단계당 강의 수만큼(보통 7) — 한 파일은 한 담당만 쓴다(아래 단계별 파일 나눔 지킴).

## A. 받기·환경
- 클라우드: `sh tools/cloud_setup.sh` → 새 추출본만 `git fetch origin cloud-materials && git archive origin/cloud-materials work/<SID>/mat | tar -x`(전체 `sh tools/cloud_materials.sh`는 work/<SID>/parts를 덮어씀 — 처음 한 번만). 원본 PDF 추출(matx·jbx)은 맥에서만 → 사용자에게 "맥에서 `git pull && sh tools/push_materials.sh <SID…>` 한 줄"을 안내하고 기다림(자세히 `guide/handoff/26년도_업데이트_절차.md`).
- 맥: `.venv` 확인 → `.venv/bin/python tools/matx.py <SID>`(새 PDF) · 새 JB면 `tools/jbx.py`.

## B. 자료 표 → 바로 진행
- `work/<SID>/mat/index.json`에서 새 파일 → 강의 주제마다 가장 최신 연도 파일을 고른 표(키 · 강의 · 교수 · 연도 · 파일 · 쪽 수 · 25 대비 변화 예상)를 사용자에게 보여 주고 **바로 이어서 진행**(신설·삭제·교수 변경만 질문).
- 모드: **갱신**(기존 강의 키, 사용자 표시 있음 → 보존 규칙 RULES 12) / **새 강의·새 과목**(표시 없음 → 구조를 자유롭게, 새 과목은 `guide/handoff/ESTH_작업지시.md` 2·3단계: tools/<sid>/ 만들기·parse_<sid>.py·JB 분해 검증·목록에 과목 추가).

## C. 연결(메인이 직접, 파이썬 몇 줄)
- `tools/matx.py` SRC에 새 폴더(예 `'C10i': '260922_'`) · `tools/<sid>/subject.py` LECMAP `<KEY>` = 26 파일, `<KEY>5` = 옛 25 · IMG_ALIAS `<KEY>5 → <KEY>` · `work/<SID>/lec/<폴더>` 링크 · 쪽 수가 바뀌면 FORCE_PAGES.
- `.venv/bin/python tools/dump_review.py <SID>` → questions.md·materials.md·qids.json(담당들이 읽음).
- 기준본 저장: `tools/annot_diff.py <SID> --save` · 강의마다 `tools/text_diff.py tools/<sid>/lec_<KEY>.txt --save` · `tools/text_diff.py tools/<sid>/tables.txt --save` · `pred.txt`도.

## D. 작성(강의마다 1명 병렬) — AGENTS.md B1(갱신) / B2(새 강의)
- 작성자가 **처음부터 RULES.md 최종형으로** 쓰게 하는 것이 전체 시간을 가장 줄인다(옛날엔 회차마다 고쳤던 것을 여기서 한 번에).
- 갱신: 담당이 다 끝나면 `tools/apply_map26.py <SID> <KEY>`(강의마다 한 번 — .applied) → 과목 강의가 다 옮겨진 뒤 `tools/split_parts.py <SID> --force`. apply_map26은 'JB 참고 p.N'·다른 강의 쪽·25 필기 쪽까지 옮기는 버릇 → C 검토에서 되돌림 확인. 다른 강의 파일이 바뀐 키를 가리키는 곳(맨글 p.N·F:·#TBL src)은 grep으로 손질.
- 새 강의: 담당이 parts에 씀 → `tools/merge_parts.py <SID>`.
- 첫 빌드: `.venv/bin/python tools/<sid>/build4.py` → 연결 누락·없는 문항 0 → `dump_review.py <SID>` 다시(검토자가 최신 화면 덤프를 보게).

## E. 독립 검토 3회(회차마다 다른 담당, 강의마다 1명 병렬) — AGENTS.md C
- 갱신 강의 담당 파일: 원고 + `work/<SID>/parts/{annot,tables,pred}_<KEY>.txt`(split_parts로 만든 것). 회차가 끝날 때마다 `merge_parts <SID>` → build4 → `dump_review` → 다음 회차.
- 1회차 역대조·⭐↔JB / 2회차 다른 각도·학습 효과·파일 간 일치 / 3회차 빨강·id·RULES 전 절. **3회차에서도 새 문제가 나오면 4회차**(새 문제 0까지).

## F. 화면 다듬기(지적받았던 회차를 미리) — AGENTS.md D1~D4
- 다듬기 전 전체 빌드 한 번(`sh tools/full_check.sh --no-ui`, run_in_background) → 화면 덤프 새로: `tools/dump_breaks2.py <SID>` · `tools/dump_jb.py <SID>` · `tools/scan_render.py <SID>`.
- 파일이 겹치지 않게 동시에: **D1 🔑⚡**(강의 묶음 둘 — lec `=`·`M:`) · **D3 JB 해설**(과목 하나 — annot) · **D4 표·예상**(과목 하나 — tables·pred). 그 뒤 **D2 줄바꿈·번호·들여쓰기**(강의 묶음 둘 — lec `-`·`=` 기호). 마지막에 메인이 **@TIP**(강의 박스 공부 전략 — `guide/handoff/TIP_BRIEF.md`) 손질.
- 갱신 강의만 대상이어도 D1·D2는 그 강의의 **모든 카드**(바뀐 줄만 고치면 앞뒤가 안 맞음).

## G. 빌드·전 검사·QA
1. `sh tools/full_check.sh`(run_in_background, 약 40분) → `work/_tmp/full_check.log` '== 요약'. 실패는 고치고 그 부분만 다시. 알려진 거짓 실패: file:// 표시 테스트는 JBL_HTTP=1로(full_check가 함), ux3_compat은 file://로.
2. 스크린샷: `JBL_HTTP=1 .venv/bin/python tools/qa_shots.py <SID> <바뀐 KEY들>` → `work/_tmp/qa_<SID>_<KEY>_{card,mem,jb}.png`를 Read로 직접 본다(사용자가 예로 든 모양이 있으면 그 카드도 — 예 Total-etch ⚡). 넓은 화면은 PIL로 잘라 확대.
3. **사용자 눈 QA**(과목 하나 1명, 고치지 않고 찾기만 — AGENTS.md E) → 걸린 것을 해당 단계 담당에게 다시 보내 고침 → 다시 1. QA에서 0이 될 때까지.
4. `tools/fc_carry.py <SID>` — 플래시카드 기록 이어짐 95%↑(끊긴 줄 목록 `work/_tmp/fc_carry_<SID>.md`는 보고에).

## H. 배포·보고
- `git add docs tools guide .claude` → 커밋(메시지 예 `CONS: 26년도 강의자료 반영(ADH·INL)`) → `git push origin <작업 브랜치>` → `git fetch origin main && git merge-base --is-ancestor origin/main HEAD && git push origin HEAD:main`. `git status`로 work/ 등이 빠졌는지.
- 보고(한국어, 사이트 기준): 사이트 반영 1~2분 안내 · 과목·강의마다 무엇이 바뀌었나(26 새 쪽·바뀐 수치·새 시험 예고 → 어느 카드) · 카드·⭐·표·예상 수 · 플래시카드 기록 이어짐 n/m · 사용자 확인 필요(자료 모순·근거 없음·판독 불가) · 다음에 할 일(맥 작업 등).
- `guide/과목노트_<SID>.md`에 이번 갱신 요지·남은 확인 사항 덧붙임.

## 사용자 피드백을 받으면(작업 중이든 끝난 뒤든)
1. 원문 그대로 `guide/피드백기록.md` → 2. 어느 파일을 어떻게 고칠지 한 문단(방향이 갈리면 2~3안) → 3. 고치고 빌드·검사·스크린샷 → 4. 같은 종류를 **모든 과목**에 적용할지 묻거나(작으면 바로) 적용 → 5. **RULES.md·QA.md에 새 규칙·점검 항목을 추가**(이 스킬이 다음 업데이트 때 저절로 반영하도록).
