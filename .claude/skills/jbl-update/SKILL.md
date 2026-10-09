---
name: jbl-update
description: 26년도(새 연도) 강의자료 반영 또는 새 강의·새 과목 정리본을 한 번에 '완성본'까지 — 자료 받기 → 연결 → 작성(처음부터 최종형) → 독립 검토 3회 → 화면 다듬기(🔑⚡·JB 해설·줄바꿈·번호·표·예상문제·공부 전략) → 사용자 눈 QA → 빌드·전 검사 → 배포·보고. 사용자가 "26년도 자료 반영해 줘", "○○ 강의자료 새로 올렸어", "○○ 정리본 만들어 줘", "/jbl-update [SID…]"라고 할 때 쓴다.
---

# JBL 업데이트 — 한 번에 완성본까지

심미치과학(ESTH)은 정리본을 만든 뒤 사용자 지적 수십 번(필사본 반려 → 카드형 → 검토 3회 → 줄바꿈 3회 → 번호·들여쓰기 → 표 → JB 해설 5회 → 🔑⚡ 3회 …)을 거쳐 지금 모양이 됐다. 이 스킬은 그 **모든 회차를 처음부터 차례로 한 번에** 돌려, 사용자가 다시 지적하지 않아도 되는 완성본을 만든다.

## 먼저 읽기(매번)
1. `CLAUDE.md` · `.claude/skills/jbl-update/RULES.md`(**최종형** — 문서끼리 다르면 이 파일이 이김, 13절 = 이미 받은 결정) · `QA.md`(사용자 눈 점검표) · `AGENTS.md`(담당 지시문 틀)
2. `guide/피드백기록.md` 맨 아래 20줄 · `guide/과목노트_<SID>.md` · `guide/정리본_원칙.md` · 클라우드면 `guide/인수인계_클라우드.md` A-2(자료 받기)·A-4(주의)만(A-3 '남은 일'은 10-03에 끝남 · A-2의 'annot·tables·pred는 tools/에서 직접'·A-4의 'build_all 1~2시간'보다 이 스킬의 D·E(parts)·F(직접)·G(full_check)가 이김) · 이어 가는 중이면 `guide/handoff/UPD_<MMDD>_진행.md`
3. 사용자 메시지는 **원문 그대로** `guide/피드백기록.md`에 한 줄(작업 중 새 지시가 와도 매번). 새 규칙이면 RULES.md·QA.md에도(다음에 같은 지적이 없게), 새 결정이면 RULES 13절에.

## 진행 원칙
- **묻는 것**: RULES 13절에 없는 새 결정만(강의 신설·삭제·교수 변경, pptx만 온 자료, 자료끼리 모순). B단계 직후 **한 번에 묶어**(2~3안씩) 묻고 답을 기다리는 동안 다른 강의를 진행. 답은 피드백기록·RULES 13에.
- 단계마다 짧게 보고(한국어). "얼마나 남았어?"엔 단계·남은 담당 수로 분 단위 추정(작성·검토 회차 각 15~25분, 전 검사 40분).
- **진행 파일** `guide/handoff/UPD_<MMDD>_진행.md`: 단계 체크(A~H) + 재개 메모(마지막 커밋·진행 중 담당·parts 상태·다음 할 일)를 단계 끝마다 갱신·커밋. 토큰·시간 한도로 멈춰도 새 세션이 이 파일부터 읽고 이어 감. 긴 작업(D~G)을 시작할 때 `send_later`(약 5시간 뒤 · 메시지 '진행 파일 guide/handoff/UPD_<MMDD>_진행.md 읽고 이어서')로 재개를 예약하고, 끝나면 그 예약을 지운다(사용자 10-02·03·04 '리셋되면 바로 이어서').
- 담당이 끝날 때마다 **그 담당 파일만** 커밋·푸시(작업 브랜치). parts(work/)는 커밋되지 않으니 회차 끝 `merge_parts` 뒤 `tools/<sid>/annot·tables·pred` 커밋. docs/는 빌드가 끝난 뒤에만. `work/`·`materials/`·`jb/`·`reference/`는 절대 커밋하지 않는다.
- 오래 걸리는 명령은 Bash `run_in_background`로(`cmd &` 금지 — 호출이 끝나면 같이 죽음). 기다릴 땐 `until …; do sleep; done` 한 번.
- 한 파일은 한 담당만. 담당 수: 바뀐 강의 ≤3이면 D1·D2도 강의마다 1명, 그보다 많으면 강의 묶음 2개(3~4강의씩).

## A. 받기·환경
- 클라우드: `sh tools/cloud_setup.sh` → 새 추출본만 `git fetch origin cloud-materials && git archive FETCH_HEAD work/<SID>/mat work/jb | tar -x`(cloud_materials.sh와 같은 방식). 전체 `sh tools/cloud_materials.sh`는 첫 세션에만(그 안의 `work/<SID>/parts`는 **낡은 9~10월 조각** — 쓰기 전 반드시 `split_parts <SID> --force`).
- 원본 추출(matx·jbx)은 맥에서만 → 사용자에게 "맥 터미널에서 `git pull && sh tools/push_materials.sh <SID…>` 한 줄"을 안내(새 JB 판본·새 과목이면 jbx 추출본 work/jb/<SID>_20xx도 함께 올라감 — 자세히 `guide/handoff/26년도_업데이트_절차.md`).
- 맥 세션이면 `.venv` 확인 → `.venv/bin/python tools/matx.py <SID>` · 새 JB면 `tools/jbx.py`.

## B. 자료 표·모드 판정 → 바로 진행
- `work/<SID>/mat/index.json`의 새 파일 → 강의 주제마다 가장 최신 연도 파일 표(키 · 강의(원래 이름) · 교수 · 연도 · 파일 · 쪽 수 · 형식 PDF/pptx/촬영본 · 25 대비 변화 예상)를 보여 주고 **바로 이어서 진행**.
- 강의마다 **모드 판정**:
  1. **갱신**(LECMAP의 그 키가 아직 25 파일 — 사용자 표시 있음): 새 26 = `<KEY>`, 옛 25 = `<KEY>5`. 보존 규칙 RULES 12.
  2. **이미 반영됨**(LECMAP 폴더의 SRC 앞머리가 그 26 파일 — 예 CONS ADH·INL은 10-03에 반영): 같은 파일이면 "이미 반영됨"이라고 한 줄 알리고 그 강의는 F(다듬기)만. 새 개정판(같은 해 다른 파일)이면 지금 26판을 보조 키 `<KEY>6`으로(LECMAP·IMG_ALIAS) 옮기고 새 판 = `<KEY>` → D에서 `apply_map26 <SID> <KEY> --old <KEY>6 --redo`. 시작 전 옛 `work/<SID>/upd26/`를 `upd26_<옛날짜>/`로 옮김(옛 보고를 이번 것으로 착각하지 않게).
  3. **새 강의**(같은 과목에 새 주제): subject.py에 키 추가(C단계) — 사용자 표시 없음, 구조 자유.
  4. **새 과목**: ① 맥에서 `tools/matx.py`·`tools/jbx.py`의 SUBJ와 matx SRC에 과목을 넣어 커밋(맥 세션 또는 사용자에게 한 줄) ② `guide/handoff/ESTH_작업지시.md` 2·3단계 — `tools/<sid>/` 만들기(공통 파일은 tools/cons에서 — sync_common DST에 추가), subject.py·assemble.py·parse_<sid>.py 새로, JB 분해 검증(RULES 0-1) ③ 과목 목록이 박힌 곳 전부에 새 SID: `grep -rln "'PHARM'" tools`(full_check.sh·fc_carry·rehub SIDS·verify·build4 READY·shell.html SUBJECTS/SJC/SJS·push_materials·check_*·scan_render·dump_review·audit_design SUBJ·legacy_base·aidlock_enrich·sync_common DST) + 과목 수를 가정한 tests 확인 ④ SJC 과목 색 지정(audit_design 명암).
- 표가 비어 있으면(새 파일 없음) "새 파일이 없다 — 맥에서 push_materials가 끝났는지"를 묻고 멈춘다.

## C. 연결(메인이 직접)
- `tools/matx.py` SRC에 새 폴더(예 `'C10i': '260922_'`) · `tools/<sid>/subject.py` LECMAP `<KEY>`(새 파일)·`<KEY>5`(옛 25)·IMG_ALIAS `<KEY>5 → <KEY>` · 쪽 수가 바뀌면 FORCE_PAGES · 새 강의·새 과목은 LEC_ORDER·PROF_LEC·PROF_ORDER·COVER·TIERS(·TREND_NOTE)와 assemble.py의 문항 → 강의 연결 · assemble.py `LK_PROF`에 새 키(빠지면 그 강의 문항의 교수가 빈칸 — ESTH·IMPL·ANAT·GERI) · PHARM은 `TOPIC_LK`도 · **기존 문항이 새 강의로 옮겨 가면** split_parts 직후 그 @블록을 옛 강의 조각(`parts/annot_<옛키>.txt`)에서 지우고 새 강의 조각에만 둔다(같은 id가 두 조각에 있으면 merge_parts는 파일 이름 순으로 나중 것이 이김) · 강의 수를 가정한 테스트를 새 수로: `grep -rn "== 7" tools/tests | grep -i "lec\|ks\|nvl"`(ux4f_C PHARM·ux4_nav CONS·ux3_fixes ANAT). 교수가 바뀐 강의는 RULES 13(ACU 선례) — PROF_LEC은 그대로(JB 출제 교수), PROF_NOTE에 26 담당 한 줄.
- 쪽 이미지 링크(클라우드엔 pymupdf가 없어 손으로): `ln -sfn ../mat/<파일id>/i work/<SID>/lec/<폴더>`(OMS1은 LECMAP `L13` ↔ 링크 `L13i`) → dump_review 뒤 `materials.md`에서 그 키가 새 파일id로 나오는지('폴더 없음'이면 링크 실패 — 빠뜨리면 build4가 docs/packs의 옛 그림을 써서 26 쪽에 25 그림이 붙어도 통과함).
- 새 과목은 팩이 없어 dump_review·check_lec·merge_parts가 안 됨 → JB 분해·assemble 뒤 강의 원고 스텁(`#LEC` 줄 + 빈 카드 하나)으로 첫 build4 → docs/packs/<SID>.js 생성(아직 검증된 적 없는 경로 — 실패하면 build4 오류를 보고 READY·LEC_ORDER부터 확인, 결과를 과목노트에).
- `.venv/bin/python tools/dump_review.py <SID>` → questions.md(머리줄 '출제' = 확정 연도 전체)·materials.md·qids.json.
- (보고용) 26 반영 전 원고 사본: `mkdir -p work/<SID>/upd26 && cp tools/<sid>/lec_<KEY>.txt work/<SID>/upd26/<KEY>_before.txt` · apply_map26 전 `cp tools/<sid>/{annot,tables,pred}.txt work/<SID>/upd26/pre_apply/`(E 1회차가 잘못 옮긴 쪽을 견줌).

## D. 작성(강의마다 1명 병렬) — AGENTS.md B1(갱신) / B2(새 강의)
- 작성자가 **처음부터 RULES.md 최종형으로** 쓰게 하는 것이 전체 시간을 가장 줄인다.
- 갱신: **그 과목 작성자 전원이 끝난 뒤** 강의마다 `tools/apply_map26.py <SID> <KEY>`(다른 lec 파일도 고치므로 동시에 돌리지 않음 — 한 번만, .applied) → `tools/split_parts.py <SID> --force` → `tools/merge_parts.py <SID> --check`가 '검사 통과'인지 확인하고 담당을 보냄. apply_map26은 'JB 참고 p.N'·다른 강의 쪽·25 필기 쪽까지 옮기는 버릇 → E 1회차가 되돌림 확인. 다른 강의 파일이 바뀐 키를 가리키는 곳(맨글 p.N·F:·#TBL src)은 grep으로 손질.
- 새 강의: 먼저 `split_parts <SID> --force`(낡은 조각 덮기) → `merge_parts <SID> --check` 통과 확인 → 담당이 parts에 씀 → `tools/merge_parts.py <SID>`.
- 갱신 강의는 25 → 26 바뀐 곳 표시를 작성 단계부터(RULES 12 · `review_final/UPD26MARK_BRIEF.md` — `{u:}` 초록 NEW 26 · `@UPD` 상자 · 사용자 10-09).
- 첫 빌드: `.venv/bin/python tools/<sid>/build4.py` → 연결 누락·없는 문항 0 → `dump_review.py <SID>` 다시.

## E. 독립 검토 3회(회차마다 다른 담당, 강의마다 1명 병렬) — AGENTS.md C
- 담당 파일: 원고 + `work/<SID>/parts/{annot,tables,pred}_<KEY>.txt`. 1회차가 작성자 보고의 'annot·tables·pred 고칠 것'을 parts에 반영.
- 회차 끝마다 메인: 보고서의 '다른 강의 몫'(교차 ⭐·같은 그림 문구)을 모아 그 강의 다음 회차 담당에게 넘김(또는 직접 — 그때도 `work/<SID>/parts/` 조각에. tools/<sid>/annot·tables·pred를 고치면 다음 merge_parts가 블록째 덮음) → `merge_parts <SID>` → `tools/<sid>/annot·tables·pred` 커밋 → build4 → `dump_review` → 다음 회차.
- 1회차 역대조·⭐↔JB / 2회차 다른 각도·학습 효과·파일 간 일치 / 3회차 빨강·id·RULES 전 절. **3회차에도 새 문제가 나오면 4회차**(새 문제 0까지).

## F. 화면 다듬기(지적받았던 회차를 미리) — AGENTS.md D1~D4
- **F부터는 `tools/<sid>/` 파일을 직접 고친다**(parts는 낡음 — 다시 쓰려면 반드시 `split_parts --force` 뒤).
- 시작 전 메인: 빌드(`sh tools/full_check.sh --no-ui`, run_in_background) → 화면 덤프 `tools/dump_breaks2.py <SID>`(→ `work/review_breaks2/<SID>_lec.md`·`_jb.md`) · `tools/dump_jb.py <SID>`(→ `work/review_jb/<SID>.md`) · `tools/scan_render.py <SID>` · `tools/table_audit.py <SID> --md work/review_final2/TA_<SID>.md`(D4가 읽음) → **기준본 다시 저장**: `tools/annot_diff.py <SID> --save` · 강의마다 `tools/text_diff.py tools/<sid>/lec_<KEY>.txt --save` · `text_diff tools/<sid>/tables.txt --save` · `pred.txt --save`.
- 동시에(파일이 안 겹침): **D1 🔑⚡**(lec `=`·`M:`) · **D3 JB 해설**(과목 하나 — annot) · **D4 표·예상**(과목 하나 — tables·pred, pred 줄바꿈 포함).
- D1이 끝나면 메인이 build4 + `dump_breaks2 <SID>` 다시 + 강의마다 `text_diff tools/<sid>/lec_<KEY>.txt --save`(D1 뒤 기준본) → **D2 줄바꿈·번호·들여쓰기**(lec `-`·`=`·`E:`·`P:`·`U:` 줄 + tables.txt 칸의 구분 기호 — D4가 끝난 뒤 메인이 `text_diff tools/<sid>/tables.txt --save` 하고 그 과목 D2 담당 **한 명만** tables 차례).
- D2·D3·D4가 끝나면 메인이 build4 + `dump_breaks2 <SID>` 다시 → 기준본 다시 저장(lec마다·pred `text_diff --save` · `annot_diff --save`) → **D5 필기 ✍·강조 마무리**(과목 하나 — lec 모든 줄·annot·pred, tables는 D4가 함(TABLE3 6번 필기 칸 빨강 + NOTEMARK2 표 칸 `{n:}`) · `NOTEMARK_BRIEF`+`NOTEMARK2_BRIEF`+`REDNOTE_BRIEF` · RULES 7 끝·9 · QA 29·34) → 커밋 → build4 + `dump_breaks2 <SID>` 다시(D5의 ✍ 줄바꿈·빨강 변화 반영) → **D2b 구조 정돈**(`--ref` = 그 커밋)(과목 하나 — 위아래로 이어지는 내용이 떨어진 • 로 보이는 곳·엉뚱한 머리 아래 묶인 곳, `STRUCT_BRIEF.md`·RULES 6 '이어지는 내용은 한 줄에' · 검사 `tools/struct_diff.py` ✓).
- **강의가 적거나(≤5) 사용 한도가 걱정되면**(10-09 — 한도로 담당 5명이 두 번 멈춤): 강의마다 F 담당 1명이 D1 → D3 → D4 → D2 → D5 → D2b → @TIP을 차례로(그 강의 lec + `work/<SID>/parts/{annot,tables,pred}_<KEY>.txt` — 같은 과목 다른 강의와 파일이 안 겹침, split은 E 때 것 그대로) · 메인은 시작 전 lec·parts `text_diff --save`, 끝나면 `merge_parts` → 빌드. 한도로 멈추면 같은 지시문으로 다시 띄움(손댄 곳은 기준본 diff로 이어 감).
- 마지막에 메인이 `@TIP`(강의 박스 공부 전략 — `guide/handoff/TIP_BRIEF.md`)을 바뀐 강의마다 다시 씀(B1이 쓴 것은 덮어써도 됨).
- 갱신 강의만 대상이어도 D1·D2는 그 강의의 **모든 카드**.

## G. 빌드·전 검사·QA
1. `sh tools/full_check.sh`(run_in_background, 약 40분) → 요약 = `work/_tmp/full_check.log` 끝 '== 요약'(= `work/_tmp/full_check.fail` — check_years/eyears/abbr/numbering/breaks_jb·fc_carry 95% 미만도 잡힘). **10-09 배포 기준값**(이 수보다 늘면 새 문제 — 갱신을 시작할 때 진행 파일에 다시 적음): check_years GERI 11(전부 '학번?' — +2 하면 배지에 있음) · check_abbr OMS1 5·CONS 11·IMPL 8·ANAT 8·GERI 7·PHARM 22·ESTH 6(확인된 그림 속 글자) · check_numbering ESTH 4(선지 번호 인용) · check_nred OMS1 18·CONS 75·IMPL 94·ANAT 72·GERI 34·PHARM 28·ESTH 60 · 빌드 impl '되돌림 2'. 표시 보존: 갱신 전 `git rev-parse origin/main`을 진행 파일에 적어 두고, 원고를 크게 고친 과목은 `tools/tests/legacy_restore.py`(옛 고정 판 기준) 결과와 함께 위치 잃음 수를 보고. 알려진 거짓 실패: file:// 표시 테스트는 JBL_HTTP=1로(full_check가 함), ux3_compat은 file://로.
2. 스크린샷: `JBL_HTTP=1 .venv/bin/python tools/qa_shots.py <SID> <바뀐 KEY들>` → `work/_tmp/qa_<SID>_<KEY>_{card,mem,jb}.png`를 Read로 직접 본다(⭐가 가장 많은 카드 1장뿐 — 26 새 내용 카드·사용자가 예로 든 카드·정리표/비교표 탭·플래시카드는 playwright로 `#/<SID>/<KEY>/learn`에서 그 카드 `scrollIntoView` 뒤 따로 찍음). 넓은 화면은 PIL로 잘라 확대.
3. **사용자 눈 QA**(과목 하나 1명, 찾기만 — AGENTS.md E · 사용 한도가 걱정되면 '글자 그대로인 작은 표시·구조 문제는 직접 고침'을 허락해 반려 회차를 줄임(10-09) — 그때도 낱말·사실 문제와 허브·렌더러 몫은 보고만) → 걸린 것을 해당 단계 담당에게 다시 보냄(보내기 전 그 담당 검사의 기준본 `text_diff --save`·`annot_diff --save`를 다시 저장) → 고친 과목만 `tools/<sid>/build4.py` + 해당 검사 → QA 0이 될 때까지 → 마지막에 full_check 한 번.
4. `tools/fc_carry.py <SID>` — 플래시카드 기록 이어짐 95%↑(끊긴 줄 `work/_tmp/fc_carry_<SID>.md`는 보고에).

## H. 배포·보고
- 큰 갱신이면 배포 전에 사용자에게 한 줄: "💾 백업 창 → [백업 파일 보내기]로 백업 하나 받아 두면 어느 기기에서든 되돌릴 수 있어요"(표시 보존 이중 안전).
- `git add docs tools guide .claude` → 커밋(메시지 예 `CONS: 26년도 강의자료 반영(ADH·INL)`) → `git push origin <작업 브랜치>` → `git fetch origin main && git merge-base --is-ancestor origin/main HEAD && git push origin HEAD:main`. 확인이 실패하면(main이 앞섬) `git merge origin/main`(docs 충돌이면 다시 빌드) 뒤 다시. `git status`로 work/ 등이 빠졌는지.
- 보고(한국어, 사이트 기준): 사이트 반영 1~2분 · 과목·강의마다 무엇이 바뀌었나(26 새 쪽·바뀐 수치·새 시험 예고 → 어느 카드) · 카드·⭐·표·예상 수 · 플래시카드 기록 이어짐 n/m · 사용자 확인 필요(자료 모순·근거 없음·판독 불가) · 다음에 할 일(맥 작업 등).
- `guide/과목노트_<SID>.md`에 이번 갱신 요지·남은 확인 사항, 진행 파일에 완료 표시.

## 사용자 피드백을 받으면(작업 중이든 끝난 뒤든 — 사용자 10-07: "별다른 지시사항 없어도 스킬파일을 가장 최신의 지시사항까지 모조리 다 업데이트")
JB·강의자료 정리본·🔑⚡·표·예상문제·화면 모양에 대한 피드백은 **지시가 없어도 매번** 고친 뒤 이 스킬까지 갱신한다:
1. 원문 그대로 `guide/피드백기록.md` → 2. 어느 파일을 어떻게 고칠지 한 문단(방향이 갈리면 2~3안) → 3. 고치고 빌드·검사·스크린샷 → 4. 같은 종류를 **모든 과목**에 적용(작으면 바로, 크면 묻기).
5. **스킬 갱신(빠뜨리지 않음 — QA 새 번호는 늘 끝에 붙임)**: RULES.md(새 규칙 — ✗/✓ 예는 사용자 원문 그대로) · QA.md(새 점검 항목 — 확인 방법까지) · RULES 13(새 결정) · AGENTS.md(그 규칙을 지켜야 할 담당 지시문) · 이번에 쓴 BRIEF가 있으면 `guide/handoff/review_final/`에 두고 AGENTS·SKILL에서 가리킴 · 새 검사 스크립트·테스트는 `tools/full_check.sh`에.
6. **스킬 자기점검**(커밋 전): 독립 담당 1명에게 "피드백기록.md 전체(특히 이번 것)와 지금 가장 최신 정리본(이번에 고친 강의)을 보고 — 이 스킬(RULES·QA·AGENTS·SKILL)만 따라 새 강의를 만들면 지금 품질이 나오는가, 빠진 지시·모순·틀린 경로는 없는가"를 보고만 하게 하고(`work/_tmp/skill_audit.md`), 걸린 것을 고친다.
7. 사용자 보고 끝에 한 줄: "스킬에도 반영: RULES n절·QA n번 …".
