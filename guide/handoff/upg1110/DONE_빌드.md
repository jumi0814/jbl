# DONE_빌드 — 11-10 전면 점검·개선 · 빌드 쪽(W1 build4 + W3 그림 파일 빌드)

담당: worktree 담당(빌드 쪽 — 앞 담당이 한도로 멈춰 두 번째 담당이 이어서) · 지시문 `guide/handoff/upg1110/agents/UPG_B.md` · 기준 커밋 b714aca8 · 브랜치 `worktree-agent-ae5c8cca242a40c1a`
맡은 파일: `tools/cons/build4.py`(+ sync 사본) · `tools/quarters.json`·`tools/quarters.py` · `tools/jblpaths.py` · `tools/verify.py` · `tools/check_links.py` · `tools/tests4/q_perf.py` · 새 `tools/tests4/q_imgbuild.py` · `tools/SPEC.md`(빌드 절) · 이 보고
건드리지 않은 것: `tools/cons/shell.html`(허브 담당) · `lecparse.py`·`trend.py`·`build2.py`·`assemble.py`(맡은 파일 밖 — 필요한 고침은 build4 안에서) · **`docs/`는 커밋하지 않음**(메인 결정 11-10 — 허브 담당과 부딪힘 · 다시 빌드한 4Q 빈 팩은 시험·비교에만)

## 진행(항목이 끝날 때마다 고침)
- [x] 읽기: BRIEF_공통 · PLAN · R_DESIGN §0·§3·§5 · R_NAV A10·A17·A19 · build4·jblpaths·quarters·new_subject·verify·check_links·q_perf
- [x] 앞 담당 작업분(f0e4f6c5) 확인 — 아래 표
- [x] 1. D 검사(q_imgbuild PASS 39줄 · JB 원본 쪽 길 포함 · 3Q 방식 출력 = 기준 커밋과 글자까지 같음)
- [x] 2. A 검사(4Q 빈 팩 10개 다시 빌드 — 바뀐 키 = stub·imgf·trends·ledger·lect.head/tline/tstrat뿐 · rehub --check OK · q_empty PASS)
- [x] 3. check_links(쿼터 자리 · ✗ 3종 · 보관 분기 알려진 것 5 — 4Q PASS · 3Q PASS + 알려진 것 5)
- [x] 4. verify(1a 그림 파일·키 · 3절 빈 과목 건너뜀 — 4Q PASS · 진짜 3Q 폴더 PASS)
- [x] 5. q_perf(파일 방식 예산 — PASS)
- [x] 7. SPEC(빌드 절 — '공통 코드 동기화' 절 뒤 새 절 + 작업 순서 5번 한 줄) → sync_common
- [ ] 6. B grep 보고 · 8. 전체 검사

## 앞 담당이 한 것 — 이어받을 때의 실제 상태(코드 읽기 + 읽기 전용 측정)
| 항목 | 코드 | 검사 |
|---|---|---|
| A 빈 과목 | 들어감(build4 `STUB`) | 안 됨 — worktree `docs/packs` 10개는 옛 팩 그대로 |
| B 라벨 | 들어감(build4 4곳) | 허브·테스트 grep 보고 안 씀 |
| C cite 쪽 | build4 들어감(`_cnum`) | `check_links.py` 손 안 댐 |
| D 그림 파일 | 들어감(quarters.json·quarters.py·jblpaths·build4 `IMGFILES`) | q_imgbuild를 한 번 돌린 흔적(시험 폴더가 남음 = FAIL 1개 이상 — 어느 줄인지 모름) |
| E 도구 | `q_imgbuild.py`만 씀 | `verify.py`·`check_links.py`·`q_perf.py` 손 안 댐 |
| SPEC·보고 | 안 씀 | — |

읽기 전용 측정(배포본 그대로):
- 3Q 팩에서 새 규칙에 걸릴 것 = GERI `[[OHQ:쪽]]` 1개 · PHARM JB 원본 쪽 `23q4-17~20` 4개 — 그 밖 0.
- 3Q 7과목 `data-img`(4,001개)·cite(15,805개) 키는 전부 묶음에 있음 → verify의 새 키 검사를 3Q에 걸어도 새 실패 없음.
- `check_links.py`는 `docs/packs`가 박혀 있어 `JBL_Q=3q`로는 3Q 팩(`docs/3q`)을 못 찾음.

(아래에 항목별 결과를 덧붙임)

## D. 그림 파일(W3) — 코드는 앞 담당 · 검사는 이번에
- **고침(코드 — 앞 담당 f0e4f6c5)**: `tools/quarters.json` `4q.img="files"` · `tools/quarters.py` `img_mode(q)`·`quarters.py img [q]`·check(값은 "files"뿐 · 보관 분기에 img 금지) · `tools/jblpaths.py` `img_mode·img_dir·img_name·img_url·prev_imgf·prev_img_path·img_bytes` + `prev_images`·`prev_jb_pages`가 파일 방식이면 지난 목록(imgf)의 파일을 같은 꼴(dataURI)로 · `tools/cons/build4.py` `IMGFILES` 가지(강의 쪽 `_lec_file` · JB 원본 쪽 · imgf · img_lock · 한 세대 남김 · `img_dims`는 잠금의 원본 크기 → 지난 파일 머리).
- **이번에 고친 것**: `tools/tests4/q_imgbuild.py`만 — build4·jblpaths는 고칠 것이 없었음.
  - 지난 실패 1줄(② 다시 빌드 = 팩 글자 그대로)의 원인 = 시험 원고의 두 카드가 너무 비슷해 `tools/aidlock.py`가 둘째 빌드부터 서로를 옛 이름(alt)으로 붙임(그림과 무관 · 원래 동작) → 시험 원고의 두 카드를 서로 다른 글로. 실패 줄에 다른 키가 보이게 `dk()`.
  - **④b JB 원본 쪽 길 추가**(앞 담당 시험에는 없어 JB 가지가 한 번도 안 돌았음): 사본 안 가짜 JB 2쪽(`work/jb/TST9_2026` — 진짜 work/jb는 안 씀) → `jb26-1.<h8>.jpg`·`jb26-2.<h8>.jpg`(assemble이 만든 JPEG 그대로 — 그림 쪽 색 924폭 · 글 쪽 회색 860폭)·`imgf.jb`·대장 단추 키와 같음·img_lock `[원본 md5|꼴, h8]` · 다시 빌드 = 팩·파일·잠금 그대로 · 쪽 그림 없이(클라우드) 다시 빌드 = 그대로 · 단일 파일판에 들어 있음 · 스위치 끄면 `TST9.img.jb26.js`(같은 바이트) + 호환 `TST9.img.jb.js`.
- **결과**: `tools/tests4/q_imgbuild.py` **PASS(39줄)** — ① 파일 3개·imgf·img_lock·HTML 폭·높이 ② 다시 빌드 = 파일(수정 시각까지)·팩 글자 그대로 ③ 그림 하나 바꿈 = 그 파일만 새 해시 + 옛 파일 한 세대 → 다음 빌드 때 지움 ④ 원본 없이 = 그대로 ④b JB ⑤ 스위치 끔 = 묶음·imgv(바이트 = 파일 방식 파일 · 두 방식 팩은 imgf·imgv 말고 같음) ⑥ TST9 지움(진짜 등록표·tools/에는 생긴 적 없음 — 도구 사본 `work/_tmp/q_imgbuild/repo`에서 돎 · 브라우저·work/jb 없이 약 5초).
- **3Q 방식이 안 바뀐 증거**(한 번 비교 — scratch): 스위치 끈 시험 과목(강의 그림 3장 + JB 원본 2쪽)을 **기준 커밋 b714aca8의 build4·jblpaths·quarters**와 지금 것으로 각각 빌드 → `index.html`·`TST9.js`·`TST9.img.IMG.js`·`TST9.img.jb26.js`·`TST9.img.jb.js`·아이콘·manifest **8개 파일이 글자까지 같음**. 코드로도: build4의 새 가지는 전부 `if IMGFILES`(= `J.img_mode(SID) == 'files'` — 3q는 키가 없어 False) 뒤 · `PREV = {} if IMGFILES else J.prev_images(SID)` · `JBIMG = IMG['jb']`(파일 방식일 때만 바꿈) · 묶음 쓰기 `for c, t in ({} if IMGFILES else img_files)` · jblpaths의 `prev_images`·`prev_jb_pages`는 첫 줄 `img_mode == 'files'`일 때만 새 길.

## A. 빈 과목(W1 · A17) — 코드는 앞 담당 · 검사는 이번에
- **고침(build4 — 앞 담당)**: `STUB = (not Q) and 강의 키 == ['WAIT']`(tools/new_subject.py 빈 틀 그대로일 때만) → `pack['stub'] = True`(실제 강의·JB가 들어오면 키 자체가 없음) · 과목 홈 '교수별 출제 경향' 절 `trends = ''` · 강의 틀에서 출제 경향(`details.trend`)·'📌 공부 전략 기출은 전부 풀되 …'(`.tstr`)·빈 '⭐ 많이 나온 순'(`.ftop`) 뺌 · `lect[0].tline`·`tstrat` = '' · 기출 대장 = 한 줄 안내('이 과목은 JB를 받는 대로 기출 대장(수록 대조표·연도 규칙·JB 원본 쪽)이 채워집니다.' — '카드 0개 = .'·빈 표 없음). '2회 이상 출제'는 원래 `top = []`(허브가 숨김 — 허브 몫).
- **검사(이번)**: 4Q 10과목 `tools/<sid>/build4.py` 전부 rc=0 → 커밋된 옛 팩과 JSON 비교: **10과목 모두 바뀐 키가 `stub`(True)·`imgf`({'lec':{},'jb':{}})·`trends`·`ledger` + `lect[0].head`·`tline`·`tstrat`뿐** · 팩 머리 줄·`build`·`imgv`({}) 그대로 · `docs/packs/img/`·묶음 파일 0 · `tools/` 곁다리 파일 변화 0(img_lock은 그림이 없으면 안 생김) → `tools/rehub.py --check` OK · `tools/tests4/q_empty.py` PASS 38줄(고치기 전 38줄 PASS와 같음) · 지금 허브로 OMS2 홈·WAIT 학습·대장·JB를 열어 글 확인(오류 0 · undefined/NaN 0 — 강의 틀에 경향·전략 없음, 대장 한 줄).
- **안 함(허브 몫 — 지금 허브에서 아직 보이는 빈 과목 글)**: 과목 홈 '기출을 다 맞혔어요'·'시작: 강의자료 대기 →'·강의 카드 '강의자료 대기 -' · JB 화면 '조건에 맞는 문항이 없습니다' · 공부 순서(`guide` — 이어서·안 푼 것 단추)는 build4에서 그대로(허브 `isStub`가 읽음 — 메인 확인).
- **docs는 커밋하지 않음**(메인 결정) — 메인이 합친 뒤 메인 저장소에서 10과목 build4 → rehub.

## C. cite 쪽 번호(A19) · 없는 JB 원본 쪽(A18) — build4는 앞 담당 · check_links는 이번에
- **고침(build4 — 앞 담당)**: 팩을 다 만든 뒤 한 번에 `_cnum` — `<button class="cite…" data-k data-p>`의 쪽이 비어 있지도(쪽 그림 폴더가 없는 강의의 글 인용 `cite t` — 그대로) 아스키 숫자도 아니면 칩을 만들지 않고 원고 글자 `[[키:쪽]]` 그대로 + 빌드 출력 '⚠ 쪽이 숫자가 아닌 인용'. lecparse.inline·assemble.cite_html·annot·pred 어느 길로 만든 칩이든 걸림(허용하던 꼴 = 숫자 하나 `data-p="12"` + 묶은 범위 `data-pp="12,13"`뿐 — 코드 확인: lecparse `_inline0`·build4 `CITE1`).
- **고침(이번 — `tools/check_links.py`)**:
  - 팩 자리 = `J.docs_of(SID)`(전에는 `docs/packs`가 박혀 있어 전환 뒤 `JBL_Q=3q`로는 파일을 못 찾고 죽었음 — full_check 3Q의 check_links 줄이 그동안 비어 있었을 것).
  - 새 ✗: **숫자 아닌 쪽**(`data-p`·`data-pp`) · **팩에 없는 JB 원본 쪽 단추**(`data-jb` — 팩 전체 글: 카드·대장·예상… ↔ 묶음 `<SID>.img.jb<판>.js`의 jb 키 또는 `imgf.jb`) · **없는 그림 파일**(imgf에 적혔는데 `packs/img/<SID>/…` 파일이 없음). 그림 있는지 = 묶음 ∪ imgf(파일이 실제 있는 것만). ①(쪽 이미지 없는 인용)도 팩 전체 글에서(3Q 기준 0 그대로).
  - **보관(frozen) 분기의 알려진 것**(메인 결정): 도구 안 `KNOWN = {'GERI': {'cite OHQ:쪽'}, 'PHARM': {'jb 23q4-17'…'jb 23q4-20'}}` — 보관 분기 과목에서만 적용 · '알려진 것 n(보관 분기 — FAIL 아님)'으로 따로 셈 · 목록에 없는 새 ✗는 FAIL · 다시 빌드해 사라지면 'KNOWN에서 뺄 것'으로 알려 줌. 종료 코드 = ✗가 있으면 1(전에는 늘 0).
- **결과**: 4Q `tools/check_links.py` → 10과목 전부 0 · RESULT PASS · `JBL_Q=3q tools/check_links.py` → 7과목 ✗ 0 · **알려진 것 5**(GERI `lect OHQ head → OHQ:쪽` 1 · PHARM `ledger → JB 원본 23q4-17~20` 4) · RESULT PASS. 거꾸로 시험(시험 폴더 팩에 숫자 아닌 쪽·없는 JB 쪽·없는 파일·그림 없는 쪽을 심음) → 4개 모두 ✗ · FAIL 4 · 종료 코드 1.
- build4 쪽 시험: q_imgbuild ①에 `[[IMG:쪽]]` 줄 — 칩 없이 글자 그대로 + 경고 출력 + 숫자 쪽은 칩(PASS).
- **3Q**: C는 스위치 뒤가 아님(메인 결정 = 그대로) — 3Q를 다시 빌드하는 날 GERI OHQ 머리말 칩 1개가 글자로 바뀜(그 밖 3Q 7과목 팩에 숫자 아닌 쪽 0 — 배포본 전수 확인).

## E. 도구 — verify · q_perf · q_imgbuild(이번에)
- **`tools/verify.py`**
  - 새 **1a절**: 팩에 `imgf`가 있으면 목록의 파일이 다 있음(`packs/img/<SID>/…`)·이름의 h8 = 파일 md5 앞 8자·PIL 디코드(+ 목록에 없는 '지난 세대 파일 n개'는 알림만) · **모든 팩**(묶음 방식 포함): 본문 그림 `img[data-img]`·인용 칩 쪽(`data-k`-`data-p`·`data-pp` 숫자)이 그림 파일 목록이나 그림 묶음에 있음(imgalias 반영 — 팩 전체 글에서).
  - **3절 도구 시험**: 강의가 있는 첫 과목에서(자료 대기 과목 = 팩 `stub` 또는 옛 팩 '문항 0 + 강의 WAIT뿐') · 전부 자료 대기면 알림 한 줄 뒤 404·콘솔 오류만 보고 끝. **고치기 전에는 4Q에서 3절이 죽었음**(WAIT 카드에 칠할 줄이 없어 `scrollIntoView` TypeError → Traceback · rc=1 — full_check의 verify 줄에 RESULT가 안 나오던 상태).
  - 결과: `JBL_HTTP=1 tools/verify.py`(4Q · 다시 빌드한 팩) **PASS — OK 123줄**(고치기 전: OK 101줄 뒤 Traceback) · `JBL_Q=3q JBL_HUB_DIR=docs/3q JBL_HTTP=1 tools/verify.py`(진짜 3Q 폴더) **PASS — OK 288줄**(1a: 7과목 본문 그림·인용 쪽 410~645개 전부 묶음에 있음 · 3절은 OMS1에서 그대로 돎). 거꾸로 시험(시험 사본의 팩에 없는 파일·이름 지문이 다른 파일·목록에 없는 키를 심음) → 'FAIL 그림 파일 … 없음 1 · 깨짐 1 · 지난 세대 파일 1개' · 'FAIL 본문 그림·인용 칩 쪽 … 없음 3'.
- **`tools/tests4/q_perf.py`**: 그 쿼터가 파일 방식(`QS.img_mode(q) == 'files'`)이면 묶음 예산(9.5MB) 대신 `packs/img/<SID>/*` **파일 하나 ≤ 400KB**(넘으면 실패 — 과목마다 '장수·합·가장 큰 파일' 한 줄) + '모두 n장·합' 알림 · 파일 방식 쿼터에 그림 묶음(`<SID>.img.*.js`)이 남아 있으면 실패 · `packs/img/` 폴더는 팩 크기 검사에서 건너뜀. 결과: **PASS**(4Q 그림 0장 · 시간 18개 모두 기준 안 — 3q.home 0.55s/기준 0.57 · 4q.home 0.33s/기준 0.22 등). 거꾸로 시험(500KB 가짜 파일·남은 묶음) → FAIL 2줄.
- **`tools/tests4/q_imgbuild.py`**(새 — D 절): PASS 40줄(인용 쪽 줄 포함). full_check의 `tools/tests4/q_*.py` 돌림에 저절로 들어감(브라우저 없음 · 약 5초 · 진짜 등록표·tools/를 건드리지 않음).

## SPEC.md(빌드 절만)
- '한 과목 작업 순서' 5번에 한 줄(파일 방식 쿼터의 출력) + '공통 코드 동기화·전 과목 빌드' 절 **바로 뒤**에 새 절 **'그림 파일 방식 · 빈 과목 · 라벨 통일 · 인용 쪽 (2026-11-10 …)'**(스위치·주소·팩 imgf·잠금·한 세대 남김·원본 없이 다시 빌드·그대로인 것·빈 과목·라벨·인용 쪽·검사). 문서 끝(쿼터 절)은 건드리지 않음 — 허브 담당이 끝에 덧붙여도 안 겹치게. `tools/sync_common.py`로 사본 17개 같음.
