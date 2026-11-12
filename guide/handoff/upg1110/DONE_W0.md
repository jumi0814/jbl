# DONE_W0 — 안전망(가벼운 판) · 11-10 시작 → 11-11 이어 감

지시문: `guide/handoff/upg1110/agents/UPG_T2_안전망.md`(가벼운 판 — 원래 `agents/UPG_T.md` 1~7 가운데 고른 것) · 계획 `PLAN.md` W0 · 설계 `R_DESIGN_설계.md` §4·§5 · `R_HISTORY…md` 4번.
앞 담당(worktree `worktree-agent-ac5912c51bbd11a94` — 273be7ec)이 한도로 멈춤 → 그 작업분(시험용 사이트 `qsite.build_fixture`·`q_ident` 린트·`q_crawl.py` 일부)은 메인 b607f618에 합쳐져 있음. 이 보고는 **메인 저장소 담당(11-11)**이 이어 쓴 것 — 커밋·푸시 안 함(메인이 함).
허브 코드(`tools/cons/shell.html`·`build4.py`·`num.js`)·`q_perf.py`는 건드리지 않음.

진행(항목 하나 끝날 때마다 고쳐 씀 — 한도로 멈춰도 여기서 이어 감):

- [x] 1 시험용 사이트(fixture) `qsite.build_fixture()` — 11-11 코드(4Q 그림 파일 방식)에서 확인(고칠 것 없음)
- [x] 2 `q_crawl.py` 마무리 — 전부 RESULT PASS(948화면 · 3분 32초) · 가로 넘침 재는 법 고침(아래 2)
- [x] 3 `q_pos.py`(자리 지킴이) — 새 파일 · 지금 코드 RESULT PASS(105경우 어긋남 0 · KNOWN 0 · 5분 35초)
- [x] 4 `tools/tests/STATUS.json`(35줄) · `ux_all.py`(STATUS 읽음) · `fmt_cases.py` 판정 줄 — 전체 `ux_all`은 안 돌림(메인)
- [x] (앞 담당 · b607f618) `q_ident` 린트 넓히기 — PASS 확인됨(메인)
- [x] 5 `full_check.sh` — `sh -n` 통과 · 바뀐 부분만 확인(전체는 메인)
- [x] 6 렉 묶음 전 기준 수치(`q_pos.py --perf` — 아래 표)

## 항목별 기록

### 1 시험용 사이트 — 됨(qsite 안 고침)
- `build_fixture()` 1.5초 · 뿌리 허브 `__h.NS==='jbl4q.v1.'` · 과목 팩 7개(OMS1·CONS·IMPL·ANAT·GERI·PHARM·ESTH) · 3Q 팩은 `imgf`가 없어 묶음 방식 그대로 → PHARM/HM 학습 그림 77개 가운데 화면에 올린 30개 모두 뜸(naturalWidth>0) · pageerror·console error·HTTP ≥400 0.
- 가장 큰 문서(PACKINFO·biggest): 학습·정리표·비교표·예상 = PHARM/HM · 기출 = ESTH/BOOK · 과목 JB·비교표·정리표 = PHARM · 과목 예상 = ESTH.

### 2 q_crawl — 됨(11-12 · `tools/tests4/q_crawl.py`)
- **지금 결과(전부): RESULT PASS · 948화면 · 3분 32초**(15분 안) — 화면 오류(pageerror)·콘솔 error·HTTP ≥400·요청 실패 0 · 글·속성 undefined/NaN/[object Object] 0 · 가로 넘침 0 · 빈 화면 0 · 그 주소가 그 화면으로 안 열림 0.

| 허브 | 1280×900 | 폰 393×852 |
|---|---|---|
| 뿌리(4Q — 빈 과목 10) | 46화면 · 10초 | 26화면 · 8초 |
| 3q/(3Q 7과목) | 411화면 · 82초 | 27화면 · 14초 |
| fixture(4Q 정체성 + 3Q 내용) | 411화면 · 84초 | 27화면 · 14초 |

- 훑는 것: 허브 화면 6개(`#/`·`_cal`·`_time`·`_bm`·`_num`·`_numr`) + 과목마다 메뉴에 있는 과목 문서 전부(_home·_jb·_pred·_final·_fig·_sum·_led·_tbl·_cbm·_marks) + 강의마다 모든 탭(`__h.docTabs`). 폰은 허브 화면 + 과목마다 과목 홈·JB 문제·가장 큰 강의 첫 탭(시간 — 폰 전부는 `JBL_CRAWL_VW=393`).
- **고친 것(검사기)**: ① 가로 넘침 — body·html이 `overflow-x:clip`이라 `documentElement.scrollWidth`는 넘쳐도 창 폭 그대로(앞 담당 검사는 늘 0 · 검사기 자체 검사가 FAIL로 드러냄) → **보이는 요소의 오른쪽 끝을 직접 잼**: 틀(#top·#nav·#hero·#dtabs·#stage / #home) 안 요소 가운데 오른쪽 끝 > 창 폭 + 1이고, 자르는/스크롤하는 조상(표 가로 스크롤 상자 등 `overflow-x ≠ visible`)·붙박이(`position:fixed`)·숨김(visibility·opacity 0)·안 그려지는 것(`checkVisibility()` 거짓 — 접힌 `<details>` 안 '25 → 26 바뀐 점' 알약 내용 등)·창 밖에서 시작하는 것(밀어 둔 서랍)이 아닌 것 = 넘침. ② 폰은 문서 2~3개만 ③ `JBL_CRAWL=lite`(과목 문서 + 가장 큰 강의 2개는 모든 탭 · 나머지는 첫 탭만 — 느려지면 쓸 것 · 지금은 전부가 3분 반이라 기본은 전부) · `quick`(과목마다 가장 큰 강의 하나 — 564화면 2분 45초).
- 검사기 자체 검사(한 번): 허브 홈에 일부러 넣은 'undefined' 글·`title="NaN분"`·창보다 300px 넓은 칸을 잡는지 → 잡음.
- **진짜 가로 넘침: 못 찾음**(1280 전부 · 폰은 위 범위). 처음 고친 직후 학습 탭마다 걸린 `span.gone26`·`button.ucj`는 접힌 details 안(화면에 안 그려짐)이라 거짓 경보 → `checkVisibility`로 뺌.
- 덤(11-12 한 번): 폰 393에서 fixture 모든 강의·탭 `JBL_CRAWL_VW=393 JBL_CRAWL_SITE=fx` → **411화면 RESULT PASS · 102초**(가로 넘침·오류 0). 폰도 기본으로 전부 돌리면 전체 약 6분 반(15분 안) — 기본을 바꿀지는 메인.
- 안 본 것: 답 펼친 상태·필터 건 상태 · 820/1180(아이패드 — audit_design이 봄) · 넘버링 화면 안쪽(허브 화면 `_num`·`_numr` 첫 화면만).

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

### 5 full_check.sh — 됨(11-12 · 전체는 안 돌림)
- '도구 문법' 묶음에 `tools/tests4/*.py`도(py_compile — 지금 0건).
- tests4 묶음: `for f in tools/tests4/q_*.py`가 새 `q_crawl`(약 4분)·`q_pos`(약 6분)도 돎(주석에 적음 — UI=1일 때 약 10분 더 걸림). 수치만 내는 `q_pos.py --perf`는 full_check에서 안 돎.
- 3q 묶음: 테스트 58개를 하나씩 `grep RESULT|FAIL`하던 for 문 → **`JBL_HTTP=1 ux_all.py <같은 58개 이름>`** 한 번(로그에 줄마다 ` ok `/`SKIP`/`known`/`FAIL` + 끝 `RESULT … · PASS n · SKIP n(…) · 알려진 실패 n`) + `ux3_compat`는 전처럼 file://(JBL_HTTP 없이)로 `ux_all.py ux3_compat` 한 줄. '== 요약'은 'FAIL' 글자를 세므로 PASS·SKIP·known뿐이면 3q 테스트에서 걸리는 줄 0(STATUS 기준).
- 확인: `sh -n tools/full_check.sh` 통과 · 58개 이름 모두 ux_all이 찾음(`--list` → 돌릴 것 54 · SKIP 4 = legacy_restore(local)·ux10_num5·ux11_fix·ux_u27(retired)) · `ux_all.py nb_numbering fmt_cases ux11_fix` 출력을 요약 정규식에 넣어 걸리는 줄 0 · ux3_compat 줄 = SKIP local(여기 git 7095e56 없음).
- 바뀌는 것(메인이 알 것): 3q full_check에서 전에 'FAIL'로 요약에 뜨던 legacy_restore·ux10_num5·ux11_fix·ux_u27(기준 실패)이 이제 SKIP 줄 · ux_all은 이름 순서(가나다)로 돎 · 테스트 하나가 3600초를 넘으면 실패.

## 끝 정리(11-12)
- 바꾼 파일: `tools/tests4/q_crawl.py`(가로 넘침 재는 법·폰 범위·lite) · 새 `tools/tests4/q_pos.py` · 새 `tools/tests/STATUS.json` · `tools/tests/ux_all.py` · `tools/tests/fmt_cases.py`(판정 줄 2곳) · `tools/full_check.sh` · 이 보고. `qsite.py`는 안 고침(시험용 사이트가 그대로 됨). 허브(`shell.html`)·`build4.py`·`num.js`·다른 테스트는 안 건드림. 커밋·푸시 안 함.
- 돌린 것과 결과: `q_crawl` 전부 PASS(948화면 3분 32초) · `q_pos` PASS(105경우 5분 35초 — 그 뒤 '검사기 자체 검사' 한 줄을 더했고 좁힌 실행(`JBL_POS_DOC=tbl JBL_POS_SC=tab,chip`)으로만 다시 확인) · `q_pos --perf` 38초 · `fmt_cases` PASS · `ux3_timer` PASS(231초) · bug? 3개 + ux2_jblock = 위 표 · `ux_all --list`·작은 묶음 · `sh -n full_check.sh`. 전체 `ux_all`·전체 `full_check`는 안 돌림(메인).
- **허브에서 찾은 버그: 없음**(q_pos 어긋남 0 · q_crawl 진짜 가로 넘침·오류 0 · bug? 3개는 모두 낡은 기대/3Q 내용).

### 메인이 정할 것
1. `ux_u18`(3Q 내용 — 해설 230자 덩어리 29개 + ANAT Q02)·`ux4e_names`·`ux4f_O`는 버그가 아님 → ① 지금처럼 bug?(돌리고 '알려진 실패')로 둘지 ② ux4e_names 93줄·ux4f_O 94줄을 한 줄씩 고쳐 STATUS에서 뺄지(각 5분 안 — 내 맡은 파일이 아니라 안 고침) ③ ux_u18은 3Q가 보관이라 계속 실패 → retired + 4Q annot에서 같은 검사(audit_design CHK) 0.
2. `ux2_jblock` 한 줄(`jblock.check`에 옮김 표 {id:id}) — 낡은 기대인지 `tools/jblock.py` 쪽인지 확인(브라우저 없는 6초 테스트).
3. local 10개는 이 컨테이너에서 다 SKIP — 기록 지킴이 4개(legacy_restore·legacy_restore_107·ux2_sum_mig·ux3_compat)는 **맥이나 전체 복제(git 7095e56·f2e99d3)에서만 돎** → 허브의 표시 복원 길을 고치는 묶음(W6·W7) 뒤에는 맥에서 한 번 돌려 달라고 사용자에게 부탁할지 / `git fetch --unshallow`가 되는지.
4. 글꼴 local 5개(ux2_learn·ux2_tables·ux3_tables·ux3_fixes·ux3_rest)는 맥에서 돌면 '진짜 실패'로 뜸 — 맥에서도 내용 때문에 실패하면 retired로 옮기기.
5. q_pos 범위를 넓힐지: 폰 393 · 허브 '이어서' · 답 펼친/필터 건 상태 · 스크롤 뒤 0.8초 안에 바로 떠나는 경우(지금은 자리 저장을 기다린 뒤 떠남). 렉 묶음(content-visibility·표 맞춤 미루기)이 건드리는 것이 '늦게 밀림'이라 1.5초 측정이 핵심 — 지금 범위로 충분하다고 봄.
6. q_crawl 폰을 기본으로 전부 돌릴지(+3분) · full_check(UI)가 q_crawl·q_pos로 약 10분 늘어나는 것.

### 남은 위험
- q_pos·q_crawl은 3Q 내용(fixture)에 기대어 가장 큰 문서를 고름 — 4Q 내용이 차면 `JBL_POS_SITE`/qsite 뿌리에서도 그대로 돌지만(과목·강의를 PACKS에서 찾음) 4Q 그림 파일 방식(`imgf`) 팩에서는 아직 한 번도 안 돌려 봄(그림 높이가 width/height 속성으로 잡혀 있으면 같음).
- STATUS의 retired 20개는 R_HISTORY 4번 분류표를 그대로 믿은 것(하나씩 다시 돌리지 않음) — 그 가운데 실제 버그가 숨어 있을 수는 있음(`ux_all.py --force <이름>`으로 다시 볼 수 있음). 'see'(대신 보는 테스트)는 이름·머리말로 고른 것이라 1:1로 같은 것을 지키지는 않음.
- q_pos의 ±2px은 한 번에 한 탭·부하 없는 상태 기준 — 다른 무거운 테스트와 함께 돌리면 100ms 측정이 흔들릴 수 있음(혼자 돌릴 것).
