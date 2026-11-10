# DONE_빌드 — 11-10 전면 점검·개선 · 빌드 쪽(W1 build4 + W3 그림 파일 빌드)

담당: worktree 담당(빌드 쪽 — 앞 담당이 한도로 멈춰 두 번째 담당이 이어서) · 지시문 `guide/handoff/upg1110/agents/UPG_B.md` · 기준 커밋 b714aca8 · 브랜치 `worktree-agent-ae5c8cca242a40c1a`
맡은 파일: `tools/cons/build4.py`(+ sync 사본) · `tools/quarters.json`·`tools/quarters.py` · `tools/jblpaths.py` · `tools/verify.py` · `tools/check_links.py` · `tools/tests4/q_perf.py` · 새 `tools/tests4/q_imgbuild.py` · `tools/SPEC.md`(빌드 절) · 이 보고
건드리지 않은 것: `tools/cons/shell.html`(허브 담당) · `lecparse.py`·`trend.py`·`build2.py`·`assemble.py`(맡은 파일 밖 — 필요한 고침은 build4 안에서) · **`docs/`는 커밋하지 않음**(메인 결정 11-10 — 허브 담당과 부딪힘 · 다시 빌드한 4Q 빈 팩은 시험·비교에만)

## 진행(항목이 끝날 때마다 고침)
- [x] 읽기: BRIEF_공통 · PLAN · R_DESIGN §0·§3·§5 · R_NAV A10·A17·A19 · build4·jblpaths·quarters·new_subject·verify·check_links·q_perf
- [x] 앞 담당 작업분(f0e4f6c5) 확인 — 아래 표
- [x] 1. D 검사(q_imgbuild PASS 39줄 · JB 원본 쪽 길 포함 · 3Q 방식 출력 = 기준 커밋과 글자까지 같음)
- [ ] 2. A 검사(4Q 빈 팩 10개 다시 빌드·비교) · 3. check_links · 4. verify · 5. q_perf · 6. B grep 보고 · 7. SPEC · 8. 전체 검사

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
