---
name: jbl-update
description: 26년도(새 연도) 강의자료 반영 또는 새 강의·새 과목 정리본을 한 번에 '완성본'까지 — 자료 받기 → 연결 → 작성(처음부터 최종형) → 독립 검토(바뀐 양만큼 1~3회) → 화면 다듬기(🔑⚡·JB 해설·줄바꿈·번호·표·예상문제·공부 전략) → 사용자 눈 QA → 빌드·전 검사 → 배포·보고. 사용자가 "26년도 자료 반영해 줘", "○○ 강의자료 새로 올렸어", "○○ 정리본 만들어 줘", "2027 JB 넣었어"(새 JB 판본 통합) · "교수별 예상문제 다시"(예상문제 전면 개선) · "/jbl-update [SID…]"라고 할 때 쓴다.
---

# JBL 업데이트 — 한 번에 완성본까지

심미치과학(ESTH)은 정리본을 만든 뒤 사용자 지적 수십 번(필사본 반려 → 카드형 → 검토 3회 → 줄바꿈 3회 → 번호·들여쓰기 → 표 → JB 해설 5회 → 🔑⚡ 3회 …)을 거쳐 지금 모양이 됐다. 이 스킬은 그 **모든 회차를 처음부터 차례로 한 번에** 돌려, 사용자가 다시 지적하지 않아도 되는 완성본을 만든다.

## 먼저 읽기(매번)
1. `CLAUDE.md` · `.claude/skills/jbl-update/RULES.md`(**최종형** — 문서끼리 다르면 이 파일이 이김, 13절 = 이미 받은 결정) · `QA.md`(사용자 눈 점검표) · `AGENTS.md`(담당 지시문 틀)
2. `guide/피드백기록.md` 맨 아래 20줄과 '10-15 (26 JB 7개 …)' 블록 전체(1~9번 — 새 연도 묶음의 기준) · `guide/과목노트_<SID>.md` · `guide/정리본_원칙.md` · 클라우드면 `guide/인수인계_클라우드.md` A-2(자료 받기)·A-4(주의)만(A-3 '남은 일'은 10-03에 끝남 · A-2의 'annot·tables·pred는 tools/에서 직접'·A-4의 'build_all 1~2시간'보다 이 스킬의 D·E(parts)·F(직접)·G(full_check)가 이김) · 이어 가는 중이면 `guide/handoff/UPD_<MMDD>_진행.md`
3. 사용자 메시지는 **원문 그대로** `guide/피드백기록.md`에 한 줄(작업 중 새 지시가 와도 매번). 새 규칙이면 RULES.md·QA.md에도(다음에 같은 지적이 없게), 새 결정이면 RULES 13절에.

## 진행 원칙
- **묻는 것**: RULES 13절에 없는 새 결정만(강의 신설·삭제·교수 변경, pptx만 온 자료, 자료끼리 모순). B단계 직후 **한 번에 묶어**(2~3안씩) 묻고 답을 기다리는 동안 다른 강의를 진행. 답은 피드백기록·RULES 13에.
- **무인·자율 지시**(사용자 10-15 "확인을 기다리지 말고 … 위험하거나 복구할 수 없는 변경은 강행하지 말 것"): 묻지 않고 가장 보수적인 안(기존 유지·별개 문항·보관 x=1)으로 진행 · 결정은 진행 파일 '결정' 절과 RULES 13에 '(무인 결정 — 사용자가 다르게 원하면 바꿈)' · 보고의 '사용자 확인'에 모음(위 '묻는 것'보다 이 줄이 이김).
- **단계별 배포**(사용자 10-15 7번 — 자료·JB → 예상문제 → 허브 기능 → 저장 공간): 단계마다 full_check → 배포. 배포 전 `git rev-parse origin/main`을 진행 파일에 적음(되돌릴 기준 · legacy_restore `--rev`). 검증 안 된 것은 작업 브랜치 WIP 커밋만(main 금지).
- 단계마다 짧게 보고(한국어). "얼마나 남았어?"엔 단계·남은 담당 수로 분 단위 추정(작성·검토 회차 각 15~25분, 전 검사 40분).
- **진행 파일** `guide/handoff/UPD_<MMDD>_진행.md`: 단계 체크(A~H) + 재개 메모(마지막 커밋·진행 중 담당·parts 상태·다음 할 일)를 단계 끝마다 갱신·커밋. 토큰·시간 한도로 멈춰도 새 세션이 이 파일부터 읽고 이어 감. 긴 작업(D~G)을 시작할 때 `send_later`(약 5시간 뒤 · 메시지 '진행 파일 guide/handoff/UPD_<MMDD>_진행.md 읽고 이어서')로 재개를 예약하고, 끝나면 그 예약을 지운다(사용자 10-02·03·04 '리셋되면 바로 이어서').
- **담당이 사용 한도(429)로 멈추면**(10-09 두 번): ⓐ 채운 지시문은 띄우기 전에 `work/_tmp/agents/<담당 이름>.md`에 저장하고, 진행 파일 '진행 중 담당'에 이름·지시문 경로·기준본 저장 시각을 적음 ⓑ 한도 메시지의 풀리는 시각 + 5분에 `send_later`(메시지 '진행 파일 guide/handoff/UPD_<MMDD>_진행.md 읽고 멈춘 담당 <이름들> 다시 띄우기' — 5시간 예약과 별개, 울리면 지움) ⓒ 다시 띄울 때 같은 지시문 + 한 줄 '앞 담당이 한도로 멈춤 — 보고 파일과 text_diff·annot_diff(기준본 그대로 — 다시 --save 하지 않음)로 이미 한 것을 확인하고 남은 것만'.
- 담당이 끝날 때마다 **그 담당 파일만** 커밋·푸시(작업 브랜치). parts(work/)는 커밋되지 않으니 회차 끝 `merge_parts` 뒤 `tools/<sid>/annot·tables·pred` 커밋. docs/는 빌드가 끝난 뒤에만. `work/`·`materials/`·`jb/`·`reference/`는 절대 커밋하지 않는다.
- 오래 걸리는 명령은 Bash `run_in_background`로(`cmd &` 금지 — 호출이 끝나면 같이 죽음). 기다릴 땐 `until …; do sleep; done` 한 번.
- **parts ↔ tools는 한 방향만**(10-10 — `merge_parts`는 parts 폴더의 **모든 강의 조각**으로 tools/<sid>/annot·tables·pred를 덮음 → tools를 직접 고친 뒤 돌리면 끝난 수정(NEW 26·필기 표시·표)이 소리 없이 되돌아가고 빌드·검사는 통과함): 한 과목 안에서 parts 담당(D 새 강의·E·F ≤5 모드)과 tools 직접 담당(F 표준 D1~D2b·B3 표시·QA 직접 수정)을 동시에 돌리지 않는다. tools를 직접 고친 뒤에는 그 과목 parts가 낡음 → parts를 다시 쓰기 전 반드시 `split_parts <SID> --force`. merge_parts 직전: 마지막 split 때 커밋(진행 파일에 적어 둠) 뒤로 `git log --oneline <그 커밋>..HEAD -- tools/<sid>/annot.txt tools/<sid>/tables.txt tools/<sid>/pred.txt`가 비었는지(아니면 merge 금지 — 고친 조각만 손으로 옮기거나 다시 split). 도구도 막음: split_parts가 `work/<SID>/parts/.stamp`(그때 tools 3파일 sha1)를 쓰고 merge_parts(·--check)는 지금 tools가 다르거나 .stamp가 없으면 ✗ '낡은 조각'으로 멈춤(`--stale-ok`는 알고 덮을 때만). 10-10 기준 7과목 모두 parts 낡음(.stamp 없음 — 다음 parts 작업 전 split_parts --force).
- 허브 코드 담당을 worktree로 여럿 띄우면(10-15 S1c·S3·S4) 같은 파일(num.js·shell.html·build4)을 고치는 담당은 차례로 합침: 먼저 끝난 것을 합쳐 full_check → 다음 것은 그 위에 `git merge`(충돌 = 두 쪽 다 살림 · NUMV는 build_num이 다시 씀) → full_check. worktree 담당이 메인 데이터를 빌려 빌드했으면 그 파일은 커밋하지 않게(빌린 목록 파일).
- 한 파일은 한 담당만. 담당 수: 바뀐 강의 ≤3이면 D1·D2도 강의마다 1명, 그보다 많으면 강의 묶음 2개(3~4강의씩).

## A. 받기·환경
- 클라우드: `sh tools/cloud_setup.sh` → 새 추출본만 `git fetch origin cloud-materials && git archive FETCH_HEAD work/<SID>/mat work/jb | tar -x`(cloud_materials.sh와 같은 방식). 전체 `sh tools/cloud_materials.sh`는 첫 세션에만(그 안의 `work/<SID>/parts`는 **낡은 9~10월 조각** — 쓰기 전 반드시 `split_parts <SID> --force`).
- **JB PDF가 대화 첨부로 오면**(10-15): `jb/20YY 3Q <과목> JB.pdf`로 복사(커밋 금지 — 업로드 경로는 진행 파일에) → `.venv/bin/pip install pymupdf pypdfium2` · `apt-get install -y tesseract-ocr tesseract-ocr-kor`(jbfig·figmask에 필요 — cloud_setup.sh는 안 깖) → `.venv/bin/python -I tools/jbx.py <SID>`(→ work/jb/<SID>_20YY). 다른 쿼터 JB(4Q 등 — jbx는 '3Q'만 잡음)는 jbx의 extract 함수로 `work/jb/<SID>_20YYq4`에 풀고, 그 과목 parse·assemble에 판 '<YY>q4'(그 주제만)·tier C로(PHARM 23q4 선례).
- 강의자료 원본 추출(matx)은 맥에서만 → 사용자에게 "맥 터미널에서 `git pull && sh tools/push_materials.sh <SID…>` 한 줄"을 안내(새 JB 판본·새 과목이면 jbx 추출본 work/jb/<SID>_20xx도 함께 올라감 — 자세히 `guide/handoff/26년도_업데이트_절차.md`).
- 맥 세션이면 `.venv` 확인 → `.venv/bin/python tools/matx.py <SID>` · 새 JB면 `tools/jbx.py`.

## B. 자료 표·모드 판정 → 바로 진행
- `work/<SID>/mat/index.json`의 새 파일 → 강의 주제마다 가장 최신 연도 파일 표(키 · 강의(원래 이름) · 교수 · 연도 · 파일 · 쪽 수 · 형식 PDF/pptx/촬영본 · 25 대비 변화 예상)를 보여 주고 **바로 이어서 진행**.
- **차등 갱신(사용자 10-15 — 가장 먼저 판단)**: "동일 교수·경미한 PPT 변경: 기존 정리본의 반영 상태를 확인하고 실제 변경된 부분만 필요시 수정 … 불필요한 전체 재작성은 하지 말 것" · "동일 교수·유사 강의지만 유의미한 변경: 기존 정리본을 유지하면서 추가·변경·삭제된 부분만 선별적으로 보완 … 25년도에만 존재하지만 과거 JB 대비에 필요한 내용은 `26 자료에서 빠짐 · JB 짤 대비용`" · "교수 변경 또는 강의 전면 개편: 26년도 강의자료를 기준으로 정리본을 새로 구성 … 교수만 변경되고 내용이 상당히 유사하다면 … 불필요한 재작성을 피할 것". → 작성 담당이 먼저 25↔26 쪽 대조표(<KEY>_cmp26.md)를 만들고, 같은 쪽 = 쪽 번호만 · 바뀐/새 쪽·26 강조만 원고에 반영 → 검토·다듬기는 아래 등급표대로. **작성 담당이 원고 쪽 번호도 26으로 옮긴다**(apply_map26은 lec_<KEY>를 안 옮김 — 10-15 MAX·PART에서 메인이 따로 옮김).
- **차등 등급표**(cmp 대조표로 판정 · 경계 10%는 10-16 무인 결정 — RULES 13):

  | 등급 | 판정 | 작성 | 검토 | 다듬기(F) |
  |---|---|---|---|---|
  | 경미 | 같은 교수 · 바뀐+새 쪽 ≤10% · 새 주제 없음 | B1(바뀐 줄만) | AGENTS **C0** 마무리 1회 | 바뀐 카드만 D1·D2·D5 |
  | 유의미 | 같은 교수 · 바뀐+새 쪽 >10% 또는 새 주제 | B1 | E 2회(새 문제 0까지) | 바뀐·새 카드 |
  | 전면 | 교수 변경 + 내용 다름 · 슬라이드 재구성 | B2(26 구조로 새로 — RULES 12 '전면') | E 3회 | F 전 단계(모든 카드) |
- **새 연도 묶음 순서**(10-15에 실제로 지킨 것 — 이 순서를 바꾸면 기록이 끊기거나 parts가 낡음): ① 맨 처음 과목마다 `tools/pred_dump.py <SID>`(배포본 팩 기준 예상문제 aid → work/<SID>/pred26/pred_before.* — 어떤 변경보다 먼저) ② JB 담당(AGENTS **J**) ∥ 자료 작성(B1/B2) ③ **그 과목 JB 담당이 끝난 뒤** apply_map26 ④ JB 담당은 tools/annot·tables·lec를 직접 고침 → `split_parts --force` 뒤 검토(C/C0) ⑤ JB 그림 조각(AGENTS **JF**) → G·H 배포 ⑥ TREND(AGENTS **T**) → PRED 조각(AGENTS **P**) → `pred_merge` → `pred_check` → G·H 배포(pred_merge 뒤에도 parts 낡음) ⑦ 허브 기능(worktree 담당) → G·H 배포 ⑧ 저장 공간 등 → 배포. BRIEF = guide/handoff/JB26_BRIEF.md · PRED26_BRIEF.md · S3_BRIEF.md.
- **새 JB 판본**(다음 해 JB)이 왔으면 강의 갱신과 별도로 과목마다 담당 1명 — RULES 0-1 '새 판본' · guide/handoff/JB26_BRIEF.md. 그 과목 갱신 중 강의 몫은 work/<SID>/jb26/E_<KEY>.md로 받아 갱신 검토 담당이 넣음. 새 문항 그림은 tools/jbfig.py → 검수(RULES 0-1 'JB 그림 조각').
- **예상문제는 정리본과 따로 — 전체 강의**(사용자 10-15 "정리본 수정과 예상문제 개선은 독립적으로 … 정리본을 수정하지 않는 강의까지 포함해 전체 강의를 대상으로"): 새 JB·새 자료를 반영한 뒤 과목마다 TREND 담당 1명 → 강의 묶음마다 PRED 담당(조각 파일) → pred_merge → 빌드 — RULES 11 · PRED26_BRIEF.
- 강의마다 **모드 판정**:
  1. **갱신**(LECMAP의 그 키가 아직 25 파일 — 사용자 표시 있음): 새 26 = `<KEY>`, 옛 25 = `<KEY>5`. 보존 규칙 RULES 12.
  2. **이미 반영됨**(LECMAP 폴더의 SRC 앞머리가 그 26 파일 — 예 CONS ADH·INL은 10-03에 반영): 같은 파일이면 "이미 반영됨"이라고 한 줄 알리고 그 강의는 F(다듬기)만. 새 개정판(같은 해 다른 파일)이면 지금 26판을 보조 키 `<KEY>6`으로(LECMAP·IMG_ALIAS) 옮기고 새 판 = `<KEY>` → D에서 `apply_map26 <SID> <KEY> --old <KEY>6 --redo`. 시작 전 옛 `work/<SID>/upd26/`를 `upd26_<옛날짜>/`로 옮김(옛 보고를 이번 것으로 착각하지 않게). 단 원고에 `@UPD`가 없으면(9월에 26 본문 + 25 보조로 처음 쓴 강의 등 — subject.py IMG_ALIAS에 `<KEY>5`가 있는 강의) F 전에 25 ↔ 26 바뀐 곳 표시: AGENTS.md **B3**(`review_final/UPD26MARK_BRIEF.md` 끝 절 — apply_map26 돌리지 않음 · 과목 하나 1명 · annot·tables·pred는 tools 직접 → 끝나면 그 과목 parts 낡음 — 다음 parts 작업 전 `split_parts --force`). 확인: `grep -L '^@UPD' tools/<sid>/lec_<KEY>.txt`(IMG_ALIAS 값인 키마다).
  3. **새 강의**(같은 과목에 새 주제): subject.py에 키 추가(C단계) — 사용자 표시 없음, 구조 자유. 25 이전에 없던 주제(JB에 그 강의 기출 없음)면 원고 첫 @UPD를 정확히 `@UPD 26 새 강의 — 25에 없던 주제(…)`로(과목 홈 'NEW 26 강의' 칩 — RULES 13 C안 · 줄마다 `{u:}` 없음 · 26 수업 강조·시험 예고는 `{e:}`). 25 파일만 없는 강의(JB에 기출 있음)는 새 강의 아님.
  4. **새 과목**: ① 맥에서 `tools/matx.py`·`tools/jbx.py`의 SUBJ와 matx SRC에 과목을 넣어 커밋(맥 세션 또는 사용자에게 한 줄) ② `guide/handoff/ESTH_작업지시.md` 2·3단계 — `tools/<sid>/` 만들기(공통 파일은 tools/cons에서 — sync_common DST에 추가), subject.py·assemble.py·parse_<sid>.py 새로, JB 분해 검증(RULES 0-1) ③ 과목 목록이 박힌 곳 전부에 새 SID: `grep -rln "'PHARM'" tools`(full_check.sh·fc_carry·rehub SIDS·verify·build4 READY·shell.html SUBJECTS/SJC/SJS·push_materials·check_*·check_links·cloud_materials(설명 글)·scan_render·dump_review·audit_design SUBJ·legacy_base·aidlock_enrich·sync_common DST) + 과목 수를 가정한 tests 확인 ④ SJC 과목 색 지정(audit_design 명암).
  5. **새 JB 판본**(work/jb/<SID>_2026 등): tools/<sid>/parse_<sid>.py에 판본 구조를 더해 블록 수·번호 검증(RULES 0-1) → 판본 사이 같은 문제 OTHER 연결(대조표에서 연결 안 된 블록 0) → jb_lock.json으로 옛 id 유지·새 id만 더함 → build4 → check_years → 새 기출을 E(검토)에서 ⭐·annot에 연결(현 교수 누락 0).
- 표가 비어 있으면(새 파일 없음) "새 파일이 없다 — 맥에서 push_materials가 끝났는지"를 묻고 멈춘다.

## C. 연결(메인이 직접)
- `tools/matx.py` SRC에 새 폴더(예 `'C10i': '260922_'`) · `tools/<sid>/subject.py` LECMAP `<KEY>`(새 파일)·`<KEY>5`(옛 25)·IMG_ALIAS `<KEY>5 → <KEY>` · 쪽 수가 바뀌면 FORCE_PAGES · 새 강의·새 과목은 LEC_ORDER·PROF_LEC·PROF_ORDER·COVER·TIERS(·TREND_NOTE)와 assemble.py의 문항 → 강의 연결 · assemble.py `LK_PROF`에 새 키(빠지면 그 강의 문항의 교수가 빈칸 — ESTH·IMPL·ANAT·GERI) · PHARM은 `TOPIC_LK`도 · **기존 문항이 새 강의로 옮겨 가면** split_parts 직후 그 @블록을 옛 강의 조각(`parts/annot_<옛키>.txt`)에서 지우고 새 강의 조각에만 둔다(같은 id가 두 조각에 있으면 merge_parts는 파일 이름 순으로 나중 것이 이김) · 강의 수를 가정한 테스트를 새 수로: `grep -rn "== 7" tools/tests | grep -i "lec\|ks\|nvl"`(ux4f_C PHARM·ux4_nav CONS — ux3_fixes ANAT는 `grep -n "ANAT/LIP\|'ANAT'" tools/tests/ux3_fixes.py`로 따로). 교수가 바뀐 강의는 RULES 13(ACU 선례) — PROF_LEC은 그대로(JB 출제 교수), PROF_NOTE에 26 담당 한 줄.
- 쪽 이미지 링크(클라우드엔 pymupdf가 없어 손으로): `ln -sfn ../mat/<파일id>/i work/<SID>/lec/<폴더>`(OMS1은 LECMAP `L13` ↔ 링크 `L13i`) → dump_review 뒤 `materials.md`에서 그 키가 새 파일id로 나오는지('폴더 없음'이면 링크 실패 — 빠뜨리면 build4가 docs/packs의 옛 그림을 써서 26 쪽에 25 그림이 붙어도 통과함).
- 새 과목은 팩이 없어 dump_review·check_lec·merge_parts가 안 됨 → JB 분해·assemble 뒤 강의 원고 스텁(`#LEC` 줄 + 빈 카드 하나)으로 첫 build4 → docs/packs/<SID>.js 생성(아직 검증된 적 없는 경로 — 실패하면 build4 오류를 보고 READY·LEC_ORDER부터 확인, 결과를 과목노트에).
- `.venv/bin/python tools/dump_review.py <SID>` → questions.md(머리줄 '출제' = 확정 연도 전체)·materials.md·qids.json.
- (보고용) 26 반영 전 원고 사본: `mkdir -p work/<SID>/upd26 && cp tools/<sid>/lec_<KEY>.txt work/<SID>/upd26/<KEY>_before.txt` · apply_map26 전 `cp tools/<sid>/{annot,tables,pred}.txt work/<SID>/upd26/pre_apply/`(E 1회차가 잘못 옮긴 쪽을 견줌).

## D. 작성(강의마다 1명 병렬) — AGENTS.md B1(갱신) / B2(새 강의)
- 작성자가 **처음부터 RULES.md 최종형으로** 쓰게 하는 것이 전체 시간을 가장 줄인다.
- 갱신: **그 과목 작성자 전원(과 그 과목 JB 담당)이 끝난 뒤** 강의마다 `tools/apply_map26.py <SID> <KEY>`(예상문제: Q 줄이 바뀌면 머리에 oid=<옛 aid>를 스스로 붙이고 f=도 옮김 · 그림빵 f 쪽이 바뀌면 경고 → figmask 미리보기로 m= 다시, 못 하면 x=1 — 10-16)(다른 lec 파일도 고치므로 동시에 돌리지 않음 — 한 번만, .applied) → `tools/split_parts.py <SID> --force` → `tools/merge_parts.py <SID> --check`가 '검사 통과'인지 확인하고 담당을 보냄. apply_map26은 'JB 참고 p.N'·다른 강의 쪽·25 필기 쪽까지 옮기는 버릇 → E 1회차가 되돌림 확인. 다른 강의 파일이 바뀐 키를 가리키는 곳(맨글 p.N·F:·#TBL src)은 grep으로 손질.
- 새 강의: 먼저 `split_parts <SID> --force`(낡은 조각 덮기) → `merge_parts <SID> --check` 통과 확인 → 담당이 parts에 씀 → `tools/merge_parts.py <SID>`.
- 갱신 강의는 25 → 26 바뀐 곳 표시를 작성 단계부터(RULES 12 · `review_final/UPD26MARK_BRIEF.md` — `{u:}` 초록 NEW 26 = 슬라이드 원문 새·바뀐 내용 · `{e:}` 보라 26 강조 = 26 수업 강조·시험 예고(25에도 강조면 `(25년도에도 강조함)`) · 필기엔 `{u:}` 없음 · `@UPD`(강의 틀 제목 줄의 접힌 초록 알약) · 사용자 10-09) · 이미 26으로 쓴 강의(map.json 없음)는 B3.
- 첫 빌드: `.venv/bin/python tools/<sid>/build4.py` → 연결 누락·없는 문항 0 → `dump_review.py <SID>` 다시.

## E. 독립 검토(등급표 — 전면 3회 · 유의미 2회 · 경미 C0 1회 · 회차마다 다른 담당, 강의마다 1명 병렬) — AGENTS.md C
- 담당 파일: 원고 + `work/<SID>/parts/{annot,tables,pred}_<KEY>.txt`. 1회차가 작성자 보고의 'annot·tables·pred 고칠 것'을 parts에 반영.
- 회차 끝마다 메인: 보고서의 '다른 강의 몫'(교차 ⭐·같은 그림 문구)을 모아 그 강의 다음 회차 담당에게 넘김(또는 직접 — 그때도 `work/<SID>/parts/` 조각에. tools/<sid>/annot·tables·pred를 고치면 다음 merge_parts가 블록째 덮음) → `merge_parts <SID>` → `tools/<sid>/annot·tables·pred` 커밋 → build4 → `dump_review` → 다음 회차.
- 1회차 역대조·⭐↔JB / 2회차 다른 각도·학습 효과·파일 간 일치 / 3회차 빨강·id·RULES 전 절. **3회차에도 새 문제가 나오면 4회차**(새 문제 0까지).

## F. 화면 다듬기(지적받았던 회차를 미리) — AGENTS.md D1~D4
- **F부터는 `tools/<sid>/` 파일을 직접 고친다**(parts는 낡음 — 다시 쓰려면 반드시 `split_parts --force` 뒤).
- 시작 전 메인: 빌드(`sh tools/full_check.sh --no-ui`, run_in_background) → 화면 덤프 `tools/dump_breaks2.py <SID>`(→ `work/review_breaks2/<SID>_lec.md`·`_jb.md`) · `tools/dump_jb.py <SID>`(→ `work/review_jb/<SID>.md`) · `tools/scan_render.py <SID>` · `tools/table_audit.py <SID> --md work/review_final2/TA_<SID>.md`(D4가 읽음) → **기준본 다시 저장**: `tools/annot_diff.py <SID> --save` · 강의마다 `tools/text_diff.py tools/<sid>/lec_<KEY>.txt --save` · `text_diff tools/<sid>/tables.txt --save` · `pred.txt --save`.
- 동시에(파일이 안 겹침): **D1 🔑⚡**(lec `=`·`M:`) · **D3 JB 해설**(과목 하나 — annot) · **D4 표·예상**(과목 하나 — tables·pred, pred 줄바꿈 포함).
- D1이 끝나면 메인이 build4 + `dump_breaks2 <SID>` 다시 + 강의마다 `text_diff tools/<sid>/lec_<KEY>.txt --save`(D1 뒤 기준본) → **D2 줄바꿈·번호·들여쓰기**(lec `-`·`=`·`E:`·`P:`·`U:` 줄 + tables.txt 칸의 구분 기호 — D4가 끝난 뒤 메인이 `text_diff tools/<sid>/tables.txt --save` 하고 그 과목 D2 담당 **한 명만** tables 차례).
- D2·D3·D4가 끝나면 메인이 build4 + `dump_breaks2 <SID>` 다시 → 기준본 다시 저장(lec마다·pred `text_diff --save` · `annot_diff --save`) → **D5 필기 ✍·강조 마무리**(과목 하나 — lec 모든 줄·annot·pred, tables는 D4가 함(TABLE3 6번 필기 칸 빨강 + NOTEMARK2 표 칸 `{n:}`) · `NOTEMARK_BRIEF`+`NOTEMARK2_BRIEF`+`REDNOTE_BRIEF` · RULES 7 끝·9 · QA 29·34) → 커밋 → build4 + `dump_breaks2 <SID>` 다시(D5의 ✍ 줄바꿈·빨강 변화 반영) → **D2b 구조 정돈**(`--ref` = 그 커밋)(과목 하나 — 위아래로 이어지는 내용이 떨어진 • 로 보이는 곳·엉뚱한 머리 아래 묶인 곳, `STRUCT_BRIEF.md`·RULES 6 '이어지는 내용은 한 줄에' · 검사 `tools/struct_diff.py` ✓).
- **강의가 적거나(≤5) 사용 한도가 걱정되면**(10-09 — 한도로 담당 5명이 두 번 멈춤): 강의마다 F 담당 1명(지시문 = AGENTS.md 'F 한 담당' — parts 검사는 text_diff, struct_diff·annot_diff는 tools/만 읽으니 구조 검사는 메인이 merge 뒤 `struct_diff <SID> --ref <F 시작 커밋>`)이 D1 → D3 → D4 → D2 → D5 → D2b → @TIP을 차례로(그 강의 lec + `work/<SID>/parts/{annot,tables,pred}_<KEY>.txt` — 같은 과목 다른 강의와 파일이 안 겹침, split은 E 때 것 그대로) · 메인은 시작 전 lec·parts `text_diff --save`, 끝나면 `merge_parts` → 빌드. 한도로 멈추면 같은 지시문으로 다시 띄움(손댄 곳은 기준본 diff로 이어 감).
- 마지막에 메인이 `@TIP`(강의 박스 공부 전략 — `guide/handoff/TIP_BRIEF.md`)을 바뀐 강의마다 다시 씀(B1이 쓴 것은 덮어써도 됨).
- D1·D2를 그 강의의 **모든 카드**에 하는 것은 '전면' 강의만 — 경미·유의미는 🆕 26 바뀜 칩 카드와 새 기출 카드만(등급표).

## G. 빌드·전 검사·QA
1. `sh tools/full_check.sh`(run_in_background, 약 40분) → 요약 = `work/_tmp/full_check.log` 끝 '== 요약'(= `work/_tmp/full_check.fail` — check_years/eyears/abbr/numbering/breaks_jb·fc_carry 95% 미만도 잡힘). **10-16 배포 기준값**(이 수보다 늘면 새 문제 — 갱신을 시작할 때 진행 파일에 다시 적음): check_years GERI 11(전부 '학번?' — +2 하면 배지에 있음) · PHARM 1(RX39 '관련 문항' 글 속 (24,23) — 거짓 양성) · check_abbr OMS1 6·CONS 11·IMPL 7·ANAT 6·GERI 8·PHARM 22·ESTH 7(확인된 그림 속 글자) · check_numbering 합계 5(선지 번호 인용) · check_nred OMS1 18·CONS 73·IMPL 94·ANAT 73·GERI 34·PHARM 29·ESTH 61 · pred_check 7과목 ✗0(사라진 옛 문항 0) · 빌드 impl '되돌림 2' · check_lec '@UPD없음' 0(10-10 — 25·26 둘 다 있는 강의는 모두 @UPD) · '필기NEW26' 0(check_unote — lec·annot·tables·pred · 10-10 '필기 아님!!') · 테스트 ux7_u26(NEW 26·26 강조 화면) PASS. 표시 보존: 갱신 전 `git rev-parse origin/main`을 진행 파일에 적어 두고, 원고·예상문제를 크게 고친 과목은 `tools/legacy_base.py --rev <갱신 전 origin/main>` → `JBL_HTTP=1 tools/tests/legacy_restore.py --rev <그 판>`(10-16 `--rev 807ef93` = LOST_GONE 3.9% · 모두 '위치 잃음' 보관) 결과와 함께 위치 잃음 수를 보고. 알려진 거짓 실패: file:// 표시 테스트는 JBL_HTTP=1로(full_check가 함), ux3_compat은 file://로.
2. 스크린샷: `JBL_HTTP=1 .venv/bin/python tools/qa_shots.py <SID> <바뀐 KEY들>` → `work/_tmp/qa_<SID>_<KEY>_{card,mem,jb}.png`를 Read로 직접 본다(⭐가 가장 많은 카드 1장뿐 — 26 새 내용 카드·강의 틀(초록 알약을 눌러 펼친 채)·26 강조 카드·카드 목록 메뉴('카드 n/m ▾' 펼침 — lpopOpen())·과목 홈 강의 카드(NEW 26 강의 칩)·사용자가 예로 든 카드·정리표/비교표 탭·플래시카드는 playwright로 `#/<SID>/<KEY>/learn`에서 그 카드 `scrollIntoView` 뒤 따로 찍음). 넓은 화면은 PIL로 잘라 확대.
3. **사용자 눈 QA**(과목 하나 1명, 찾기만 — AGENTS.md E · 사용 한도가 걱정되면 '글자 그대로인 작은 표시·구조 문제는 직접 고침'을 허락해 반려 회차를 줄임(10-09) — 그때도 낱말·사실 문제와 허브·렌더러 몫은 보고만) → 걸린 것을 해당 단계 담당에게 다시 보냄(보내기 전 그 담당 검사의 기준본 `text_diff --save`·`annot_diff --save`를 다시 저장) → 고친 과목만 `tools/<sid>/build4.py` + 해당 검사 → QA 0이 될 때까지 → 마지막에 full_check 한 번.
4. `tools/fc_carry.py <SID>` — 플래시카드 기록 이어짐 95%↑(끊긴 줄 `work/_tmp/fc_carry_<SID>.md`는 보고에).

## H. 배포·보고
- 큰 갱신이면 배포 전에 사용자에게 한 줄: "💾 백업 창 → [백업 파일 보내기]로 백업 하나 받아 두면 어느 기기에서든 되돌릴 수 있어요"(표시 보존 이중 안전).
- `git add docs tools guide .claude` → 커밋(메시지 예 `CONS: 26년도 강의자료 반영(ADH·INL)`) → `git push origin <작업 브랜치>` → `git fetch origin main && git merge-base --is-ancestor origin/main HEAD && git push origin HEAD:main`. 확인이 실패하면(main이 앞섬) `git merge origin/main`(docs 충돌이면 다시 빌드) 뒤 다시. `git status`로 work/ 등이 빠졌는지.
- 보고(한국어, 사이트 기준): 사이트 반영 1~2분 · 과목·강의마다 무엇이 바뀌었나(26 새 쪽·바뀐 수치·새 시험 예고 → 어느 카드) · 카드·⭐·표·예상 수 · JB 새 문항 수(과목별)·그림 조각 수 · 예상문제 활성/보관·상/중/하·그림빵·oid 수(build4 '예상문제(S3):' 줄) · 플래시카드 기록 이어짐 n/m · 표시 위치 잃음(legacy_restore) · 사용자 확인 필요(자료 모순·근거 없음·판독 불가) · 다음에 할 일(맥 작업 등).
- `guide/과목노트_<SID>.md`에 이번 갱신 요지·남은 확인 사항, 진행 파일에 완료 표시.

## 사용자 피드백을 받으면(작업 중이든 끝난 뒤든 — 사용자 10-07: "별다른 지시사항 없어도 스킬파일을 가장 최신의 지시사항까지 모조리 다 업데이트")
JB·강의자료 정리본·🔑⚡·표·예상문제·화면 모양에 대한 피드백은 **지시가 없어도 매번** 고친 뒤 이 스킬까지 갱신한다:
1. 원문 그대로 `guide/피드백기록.md` → 2. 어느 파일을 어떻게 고칠지 한 문단(방향이 갈리면 2~3안) → 3. 고치고 빌드·검사·스크린샷 → 4. 같은 종류를 **모든 과목**에 적용(작으면 바로, 크면 묻기).
5. **스킬 갱신(빠뜨리지 않음 — QA 새 번호는 늘 끝에 붙임)**: RULES.md(새 규칙 — ✗/✓ 예는 사용자 원문 그대로) · QA.md(새 점검 항목 — 확인 방법까지) · RULES 13(새 결정) · AGENTS.md(그 규칙을 지켜야 할 담당 지시문) · 이번에 쓴 BRIEF가 있으면 `guide/handoff/review_final/`에 두고 AGENTS·SKILL에서 가리킴 · 새 검사 스크립트·테스트는 `tools/full_check.sh`에.
6. **스킬 자기점검**(커밋 전): 독립 담당 1명에게 "피드백기록.md 전체(특히 이번 것)와 지금 가장 최신 정리본(이번에 고친 강의)을 보고 — 이 스킬(RULES·QA·AGENTS·SKILL)만 따라 새 강의를 만들면 지금 품질이 나오는가, 빠진 지시·모순·틀린 경로는 없는가"를 보고만 하게 하고(`work/_tmp/skill_audit<n>.md` — 앞 회차 파일을 덮지 않게 다음 번호), 걸린 것을 고친다.
7. 사용자 보고 끝에 한 줄: "스킬에도 반영: RULES n절·QA n번 …".
