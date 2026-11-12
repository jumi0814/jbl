# DONE_W0 — 안전망(가벼운 판) · 11-10 시작 → 11-11 이어 감

지시문: `guide/handoff/upg1110/agents/UPG_T2_안전망.md`(가벼운 판 — 원래 `agents/UPG_T.md` 1~7 가운데 고른 것) · 계획 `PLAN.md` W0 · 설계 `R_DESIGN_설계.md` §4·§5 · `R_HISTORY…md` 4번.
앞 담당(worktree `worktree-agent-ac5912c51bbd11a94` — 273be7ec)이 한도로 멈춤 → 그 작업분(시험용 사이트 `qsite.build_fixture`·`q_ident` 린트·`q_crawl.py` 일부)은 메인 b607f618에 합쳐져 있음. 이 보고는 **메인 저장소 담당(11-11)**이 이어 쓴 것 — 커밋·푸시 안 함(메인이 함).
허브 코드(`tools/cons/shell.html`·`build4.py`·`num.js`)·`q_perf.py`는 건드리지 않음.

진행(항목 하나 끝날 때마다 고쳐 씀 — 한도로 멈춰도 여기서 이어 감):

- [x] 1 시험용 사이트(fixture) `qsite.build_fixture()` — 11-11 코드(4Q 그림 파일 방식)에서 확인(고칠 것 없음)
- [~] 2 `q_crawl.py` 마무리 — 가로 넘침 재는 법 고치는 중(아래 2 · 순서: 3 → 4 → 2 → 5)
- [x] 3 `q_pos.py`(자리 지킴이) — 새 파일 · 지금 코드 RESULT PASS(105경우 어긋남 0 · KNOWN 0 · 5분 35초)
- [x] 4 `tools/tests/STATUS.json`(35줄) · `ux_all.py`(STATUS 읽음) · `fmt_cases.py` 판정 줄 — 전체 `ux_all`은 안 돌림(메인)
- [x] (앞 담당 · b607f618) `q_ident` 린트 넓히기 — PASS 확인됨(메인)
- [ ] 5 `full_check.sh`
- [x] 6 렉 묶음 전 기준 수치(`q_pos.py --perf` — 아래 표)

## 항목별 기록

### 1 시험용 사이트 — 됨(qsite 안 고침)
- `build_fixture()` 1.5초 · 뿌리 허브 `__h.NS==='jbl4q.v1.'` · 과목 팩 7개(OMS1·CONS·IMPL·ANAT·GERI·PHARM·ESTH) · 3Q 팩은 `imgf`가 없어 묶음 방식 그대로 → PHARM/HM 학습 그림 77개 가운데 화면에 올린 30개 모두 뜸(naturalWidth>0) · pageerror·console error·HTTP ≥400 0.
- 가장 큰 문서(PACKINFO·biggest): 학습·정리표·비교표·예상 = PHARM/HM · 기출 = ESTH/BOOK · 과목 JB·비교표·정리표 = PHARM · 과목 예상 = ESTH.

### 2 q_crawl — 진행 중(11-12)
- quick(과목마다 과목 문서 + 가장 큰 강의 하나) 564화면 3분 7초: 오류·undefined/NaN·빈 화면 0 · 그 화면으로 안 열림 0.
- **찾은 것(검사기 쪽)**: body·html이 `overflow-x:clip`이라 `documentElement.scrollWidth`는 넘쳐도 창 폭 그대로 → 앞 담당의 '가로 넘침' 검사는 늘 0(검사기 자체 검사가 그걸 잡아 FAIL) → 보이는 요소의 오른쪽 끝을 직접 재는 식으로 바꿈. 지금은 학습 탭에서 거짓 경보(`span.gone26`·`button.ucj` — 접힌/밀어 둔 요소로 보임 · 확인 뒤 예외 처리 남음).

### 3 q_pos.py(자리 지킴이) — 새 파일 `tools/tests4/q_pos.py` · 11-12 RESULT PASS
- 자리: 시험용 사이트(fixture — 4Q 정체성 + 3Q 내용 · `JBL_POS_SITE=3q`면 3q/ 허브) 1280×900. 문서 7개는 `__h.PACKS`에서 가장 큰 것(`qsite.biggest`): 학습·정리표·비교표·예상 = PHARM/HM · 기출 = ESTH/BOOK · 과목 JB = PHARM/_jb · 과목 비교표 = PHARM/_tbl.
- 깊이 3곳(카드 목록의 처음·가운데·끝 카드를 기준선 30px 아래에 둠) × 경우 5개: ① 탭 전환 뒤 돌아옴(강의 = 다른 탭 단추 눌렀다 다시 · 과목 문서 = 메뉴 '과목 홈' 갔다 메뉴로 다시) ② 뒤로(과목 홈으로 갔다 `history.back`) ②' 앞으로(뒤로 갔다 `forward`) ③ 새로고침 ④ 칩(`.jbchip[data-go]`·`[data-golec]`·`[data-go]` — 학습·정리표는 미리보기 → 'JB에서 풀기')으로 건너갔다 ↩ 알약.
- 판정: 떠나기 전 기준 카드(`data-aid`)의 화면 높이와 돌아와 그려진 뒤(`CUR`가 그 문서 + #stage 채워짐) **100ms·1.5초** 두 번 잰 높이가 ±2px · 주소도 같음. 한 깊이에서 다섯 경우는 처음 잡은 높이와 견줌(조금씩 밀리는 것도 쌓여서 잡힘) — 어긋나면 다음 경우는 다시 자리 잡음.
- 검사기 자체 검사: 일부러 37px 밀면 '어긋남'으로 잡는지(한 번).
- **지금 결과: 7문서 × 3깊이 × 5경우 = 105경우 모두 ±1px 안(가장 큰 차 +0.9px — 학습 아래, 문서 높이 85420 ↔ 85421 소수점) · SKIP 0 · KNOWN(이미 있는 버그) 0 · 화면 오류 0 · 5분 35초**(10분 안).
- 이미 있는 버그: **못 찾음**(이 범위에서는). `KNOWN = {}` 표는 남겨 둠 — `(문서, 경우, 깊이|'*'): '이유'`를 적으면 그 경우는 'KNOWN' 줄로만 보이고 RESULT에 안 셈(KNOWN인데 통과하면 알려 줌).
- 안 본 것(범위 밖 — 메인이 정할 것): 폰 393 · 허브 '이어서'(원래 지시문 3번에 있던 것 — 가벼운 판에서 빠짐) · 답을 펼친 상태·필터를 건 상태·형광펜 켠 상태 · 스크롤 뒤 0.8초 안에 바로 떠나는 경우(지금은 1.1초 기다림 — 자리 저장 `posNow`가 스크롤 0.8초 뒤).
- 쓰는 법: `.venv/bin/python tools/tests4/q_pos.py` · 좁혀서 `JBL_POS_DOC=learn,_tbl JBL_POS_SC=tab,back,fwd,reload,chip` · 렉 묶음 스위치를 켠 뒤에도 그대로 돌려 PASS여야 함(R_DESIGN §4 'ship only if … q_pos pass').

### 6 렉 묶음 전 기준 수치 — `.venv/bin/python tools/tests4/q_pos.py --perf`(판정 없음 · 38초)
11-12 · 이 컨테이너 · fixture · 1280×900 · CPU 그대로(느리게 안 함) · 팩 7개 다 받은 뒤 허브 홈 → 그 문서. '여는 시간' = 주소 바꿈 → 그려짐 + 2프레임 · Layout·Task = 그 뒤 1.6초까지(표 맞춤·자리 맞춤 포함 — CDP `Performance.getMetrics`). 한 번 잰 값(±10%쯤 흔들림).

| 문서 | 크기(글자) | 처음 열기 ms | Layout 수 | Recalc 수 | Layout ms | Script ms | Task ms | 다시 열기 ms | Layout 수 | Task ms | JS 힙 MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 과목 비교표 PHARM/_tbl | 259991 | 733 | 72 | 73 | 328 | 152 | 714 | 507 | 71 | 505 | 134 |
| 정리표 PHARM/HM | 226415 | 505 | 14 | 17 | 168 | 206 | 484 | 153 | 10 | 136 | 145 |
| 학습 PHARM/HM | 269524 | 420 | 14 | 15 | 273 | 40 | 439 | 241 | 14 | 244 | 144 |
| 과목 JB PHARM/_jb | 2369374 | 402 | 10 | 13 | 119 | 148 | 393 | 349 | 9 | 337 | 147 |
| 예상 PHARM/HM | 93012 | 153 | 9 | 8 | 60 | 26 | 152 | 72 | 8 | 50 | 145 |

- 읽는 법: 과목 비교표만 Layout 수가 72(표 64개마다 한 번씩 강제 배치 — R_DESIGN §4 (a) '표마다 강제 배치 하나'와 맞음 · 다시 열어도 71 = 기억 없음) → 렉 묶음 (a)가 줄일 값. 정리표는 다시 열면 14 → 10.
- `q_perf2.py`·`perf2_base.json`(기준 저장·1.5배 넘으면 ✗·CPU 4배)은 안 만듦(지시문 6 '하지 않아도 됨').

### 4 STATUS.json · ux_all.py · fmt_cases — 됨(11-12)
- **`tools/tests/STATUS.json`** 35줄(머리 `_` = 읽는 법) — 기준 실패 37개 가운데 2개는 빠짐: `fmt_cases`(판정 줄 고쳐 통과) · `ux3_timer`(11-12 혼자 돌려 RESULT PASS · 104줄 · 231초 — 정리표에 안 넣음).

| st | 수 | 테스트 | ux_all이 하는 일 |
|---|---|---|---|
| helper | 1 | fakegist | 목록에서 뺌 |
| retired | 20 | kt · ux10_num5 · ux11_fix · ux2_auto · ux2_device · ux2_jbq · ux2_keys · ux3_keybox · ux3_keylines · ux3_restui · ux4_calm · ux4_nav · ux4_top · ux4c_fix1 · ux_u15 · ux_u17 · ux_u19 · ux_u21 · ux_u27 · ux_u30 | 돌리지 않고 SKIP 줄(이유 + '대신 보는 테스트') · 파일은 그대로 |
| local | 10 | ct(3Q 단일 파일판) · legacy_restore(git f2e99d3) · legacy_restore_107(git 7095e56) · ux2_sum_mig(git 7095e56) · ux3_compat(git 7095e56·0918775 / work/_legacy) · ux2_learn · ux2_tables · ux3_tables · ux3_fixes · ux3_rest(맥 — 글꼴·시계) | `need`가 다 있으면 돌림(실패 = 진짜 실패) · 없으면 SKIP(없는 것을 적음). 이 컨테이너 = 10개 다 SKIP(얕은 복제 — 7095e56·f2e99d3 없음 · 0918775는 있음 · work/_legacy 없음 · 리눅스) |
| bug? | 4 | ux_u18 · ux4e_names · ux4f_O · ux2_jblock | 돌림 · 실패해도 '알려진 실패'(종료 코드에 안 셈) · 통과하면 '빼도 됨' |

- 분류 근거 = R_HISTORY 4번 표 + UPD_4Q_진행 재개 메모(하나씩 다시 돌리지 않음). (i)+(ii)가 겹친 것: ux_u21 = retired(10-22 순서) · ux2_learn = local(맥 글꼴 — 맥에서도 실패하면 retired로 옮기기) · ux2_jblock = 돌려 보니 한 줄 실패라 bug?로.
- `need` 꼴: `path:<경로>` · `glob:<패턴>` · `grep:<파일>::<글자>` · `git:<커밋>` · `os:darwin` — 한 칸 안의 `|` = 어느 하나. (ct: 지금 `work/임상치과보존학_JBL.html`은 4Q CONS4 빈 과목 것이라 이름만으로는 못 가림 → `grep:…::"id": "CONS"`.)
- **`tools/tests/ux_all.py`**: STATUS를 읽음 · 줄 머리 ` ok `/`FAIL`/`SKIP`/`known` · 끝 줄 `RESULT PASS|FAIL n: … · PASS n · SKIP n(retired a · local b) · 알려진 실패 n(이름)` · 종료 코드 1 = STATUS에 없는 실패 + need가 다 있는 local의 실패 · SKIP·알려진 실패 줄에는 'FAIL' 글자를 안 씀(full_check 요약이 'FAIL'을 셈) · `--list`(돌리지 않고 분류만) · `--force`(STATUS 무시 — 분류 다시 볼 때) · 통과 줄에 `lost rate|LOST_GONE n` 정보도 붙임(legacy_restore — full_check가 보던 것) · 한 테스트 3600초 넘으면 실패로.
- 확인: `ux_all.py --list` → SKIP 30(retired 20 · local 10) · 돌릴 것 125(fakegist 빠짐) · `ux_all.py fmt_cases fakegist ux2_jblock kt legacy_restore ux_u19 card_text annot_text` → `RESULT PASS · PASS 3 · SKIP 3(retired 2 · local 1) · 알려진 실패 1(ux2_jblock)` 종료 0 · `ux_all.py ct`(need 고치기 전) → 진짜 FAIL로 종료 1(실패 길 확인).
- **`tools/tests/fmt_cases.py`**: 끝 줄 `fmt_cases RESULT PASS` → `RESULT PASS (fmt_cases)`(R_HISTORY 4번 '(h) 줄 머리가 RESULT가 아님') — 지금 RESULT PASS. full_check의 `fmt_cases $(… grep RESULT)` 줄은 그대로 읽힘.

#### 'bug?' — 11-12 한 번씩 돌린 결과(JBL_HTTP=1 · 3Q 스테이징 BUILD 007d154b)
| 테스트 | 결과 | 실패 줄 | 판단 |
|---|---|---|---|
| ux_u18 | FAIL 14(7줄 × 화면 2) · 51초 | `.ab.chk·.ab.more 230자 덩어리` OMS1 2/2265 · CONS 2/2312 · IMPL 5/1711 · ANAT 2/3128 · GERI 5/2696 · PHARM 13/3555(ESTH 0) + `ANAT Q02 대조 첫 항목 = 점 목록` 아님 | **허브 버그 아님 — 3Q 내용(annot 인용 덩어리 29개/15,667)**. 3Q 팩은 보관이라 그대로 · 같은 검사(audit_design CHK)를 4Q annot에서 0으로 지키면 됨. 3Q에서는 계속 실패하므로 retired로 옮길지 = 메인 |
| ux4e_names | FAIL 6(한 가지 × 화면 3 × 강의 2) · 126줄 통과 · 66초 | `메뉴 강의 줄 원래 제목 ['이인복 - Tooth whitening', …]` | **버그 아님 — 낡은 기대**: 메뉴 강의 줄이 '교수 - 제목'(`lpn`)이라 `full in nl`(제목과 글자 같음)이 거짓. 이름 잘림·% 재발은 **없음**(빵부스러기 제목·과목 이름·% 줄 모두 통과). 93줄을 '끝이 같은지'로 고치면 통과할 것(내 파일 아님 — 안 고침) |
| ux4f_O | FAIL 1(O3) · 30줄 통과 · 71초 | `O3 구멍 난 형광펜 위 빈칸 겹치기 … (빈칸→형광펜 [] · 빈칸 잃음 [])` | **버그 아님 — 낡은 글 가정**: 그 줄 '③ Chemicals (catalyst, booster, activator) …'에서 낱말 `booster,`의 끝 쉼표는 빈칸에 안 들어감(빈칸 = 12~29) → 첫 조건 `set(range(*WD[3])) <= B2`만 거짓. 지키려는 것(원래 빈칸 글자 그대로 · 형광펜은 새 빈칸 자리만 빠짐 `H2 == H1 - B2`)은 참(값을 찍어 확인). O1(가린 칸 형광펜)은 HTTP에서 통과 |
| ux2_jblock(덤) | FAIL 1 · 6초(브라우저 없음) | `옮김 표 {id:id}(확인만)이면 통과` — `jblock.check('PHARM', 바꾼 jbhash, lock, {qid: qid}) != []` | 미확인(낡은 기대인지 `tools/jblock.py` 쪽인지) — 메인 |
