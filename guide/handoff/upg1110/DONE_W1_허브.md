# DONE_W1_허브 — 빈 과목·그림 다시 받기·이동(11-10 · 허브 담당)

맡은 파일: `tools/cons/shell.html` · `tools/tests4/q_stub.py`·`q_links.py`(새로) · `tools/SPEC.md` · `guide/정리본_원칙.md` · 이 보고.
(build4.py는 다른 담당 — 건드리지 않음 · 커밋·푸시·stash 안 함)

지시 = `guide/handoff/upg1110/agents/UPG_H1.md` · 점검 보고 = `R_NAV_이동·연동·빈과목.md`(A1~A24 · (b)1~8).

## 이어받음(11-10 둘째 담당)
앞 담당이 shell.html만 고치다 한도로 멈춤(커밋 983e9740 'WIP' · 기준 4127b1ce). `git diff 4127b1ce 983e9740 -- tools/cons/shell.html` 68곳을 항목별로 읽어 아래 목록을 실제 상태로 고침.
- 이어받을 때 shell.html 두 `<script>`를 메모리에서 컴파일 → 문법 오류 0(기준 커밋도 0).
- 과목 폴더 사본·docs/·3Q 스테이징은 이어받을 때 옛 판(sync_common·rehub 전).

## 진행(항목 하나 끝날 때마다 덧붙임)

- [x] 고치기 전 회귀 기준 — scratchpad `base_w1`(worktree 4127b1ce · 자체 3Q 스테이징) · 결과 `out_base/`
- [x] 1. 빈 과목(A11~A16 · (b)4·5) — **코드 끝**(앞 담당: isStub·isWait·profOf·allStub·noData · resOk·homeResume·resumeTarget · 과목 표 '자료 대기' · 오늘 할 일 · actBtn · docHas/docOk → openDoc·sjKeepDoc·qjIndex·navSubj · 빈 화면 글 · lpn·머리·강의 카드 · Ctrl+K 비교표·그림빵 · WAIT 표시 막음 · 검색 색인 · #htop / 이어서: WAIT에서 M(메모)도 막음)  · 화면 확인 = q_stub PASS
- [x] 2. 그림(A1 · A18) — **코드 끝**(앞 담당: needImages·imgLoad 다시 받기 · openImg 없는 쪽)  · 화면 확인 = q_links F PASS
- [x] 3. ↩·자리(A2~A7 · A20 · A24 · (b)2 · (b)8 · A10 강의 카드) — **코드 끝**(이어서: 학습 거르기를 되살린 뒤 `gdivEmpty`·`lmCount` · 검색·달력·내 강의목록·넘버링으로 갈 때도 `PL.lost` 지움)  · 화면 확인 = q_links A~D PASS
- [x] 4. 주소(A8 · A9) — **코드 끝**(이어서: 도움말 '1~6' → '1~7 탭 바꾸기(보이는 탭 순서대로)' · 키 정규식 1-7)  · 화면 확인 = q_links E PASS
- [x] 5. 키·터치(A21~A23) — **코드 끝**(이어서: SELECT `isKbSelect` · '답 바로 보기' 폰 36px)  · 화면 확인 = q_links G PASS
- [x] 6. (b)3 · (b)7 확인 — 아래 셋째 담당 절
- [x] 새 테스트 q_stub · q_links — 둘 다 RESULT PASS
- [x] 회귀(고친 뒤) — 아래 표
- [x] SPEC.md(끝에 '11-10 W1' 절 + 쿼터 절 테스트 줄 + 키 표 1~7) · 정리본_원칙.md 7-2b(↩ 규칙 3줄 + '11-10 빈 과목·없는 화면' 묶음)
- [x] sync_common(17개 사본 동일) → rehub 4Q(docs/ BUILD 13a9c87a) → rehub --q 3q --stage — 한 번 돌림(끝에 다시)

## 이어받음(11-10 셋째 담당 — 검사만)
기준 = 커밋 da991510(작업분 전부) · 고치기 전 = 4127b1ce(scratchpad `base_w1` worktree).
- [x] 📖 상자 칩 줄바꿈 CSS — 이미 shell.html v3 묶음 뒤에 있음(`details.ab.lk>summary .chip.lec{max-width:100%;white-space:normal;…}`) → 건너뜀
- [x] sync_common(17개 사본 동일) → rehub 4Q(BUILD c4d45d44 · 바꾼 파일 없음) → rehub --q 3q --stage(같음)
- [x] `tools/tests4/q_links.py` **RESULT PASS**(3분 · FAIL 0 — 둘째 담당이 적은 'route handler · hidden-tab pick · numbering edit box'는 da991510에 이미 고쳐져 있음)
- [x] `tools/tests4/q_stub.py` **RESULT PASS**(49초 · FAIL 0)
- [x] 6. (b)3 `#jbpeek` — **떠다니지 않음(고칠 것 없음)**. 3Q 스테이징 1280 · PHARM RX 학습 탭에서 기출 칩 → 미리보기: 휠 300px 뒤에도 칩 바로 아래(틈 0px — 문서에 붙어 같이 움직이고 `peekSync`가 scroll·keyup·click 때 다시 맞춤) · J/K로 카드를 옮기면 닫힘 · 칩이 화면 밖으로 나가면 닫힘 · 콘솔 오류 0.
- [x] 6. (b)7 폰 393 학습 탭 줄 흐림 — **탭 줄 흐림은 됨**(PHARM RX 탭 8개: 줄 224px에 내용 588px → `.dtrow.ovr` 붙고 오른쪽 28px 흐림 · 끝까지 밀면 흐림 꺼짐). 4Q는 지금 10과목이 모두 빈 과목이라 강의 탭 줄이 없어 볼 것 없음.
  - **보고(고치지 않음 — 메인이 정할 것)**: 같은 줄 오른쪽 도구 묶음(`.lmini`)에서 `#lmcur` 글 '틀 · 21장'(71px)이 38px 단추에 눌려 옆 '보기 ▾' 위로 겹쳐 보임(393·360 둘 다 · **고치기 전 4127b1ce도 똑같음** — W1 탓 아님 · 11-04 '⑥ 폰 강의 탭 줄' 규칙 `max-width:40%` 안에서 단추가 `min-width:38px`까지 줄어서). 단추에 `flex:none`을 주면 글은 안 겹치지만 묶음이 224px이 되어 ✎ 도구가 반쯤·⤢ 집중이 화면 밖으로 밀림(옆으로 밀어야 보임) → 디자인 선택이라 안 고침. 안: ① 폰에서 `#lmcur`를 숫자만(예 '21') ② 묶음 40% → 넓히고 탭 줄을 줄임 ③ `flex:none` + 묶음에도 흐림. 화면 = scratchpad `w1c/b7_new.png`.
- [x] 회귀(고친 뒤 · 하나씩 · 셋째 담당이 shell을 고친 것은 없음 — 검사한 것 = 커밋 da991510 그대로)

## 최종 상태(11-10)

### 항목별
| 항목 | 상태 |
|---|---|
| 1. 빈 과목(A11~A16 · (b)4·5) | 고침 — q_stub PASS(4Q 빈 과목 10개 · 폰 393 포함) |
| 2. 그림(A1 · A18) | 고침 — q_links F PASS(한 번 실패 = 저절로 다시 · 두 번 = 알림 [다시] · 없는 쪽 = 가까운 쪽 + 알림) |
| 3. ↩·자리(A2~A7 · A10 · A20 · A24 · (b)2 · (b)8) | 고침 — q_links A~D PASS(같은 자리 ±2px) |
| 4. 주소(A8 · A9) | 고침 — q_links E PASS |
| 5. 키·터치(A21~A23) | 고침 — q_links G PASS |
| 6. (b)3 #jbpeek | 확인 — 떠다니지 않음(고칠 것 없음) |
| 6. (b)7 폰 탭 줄 흐림 | 확인 — 흐림 됨 · 옆 도구 묶음 글 겹침은 보고만(원래 있던 것) |
| 📖 상자 칩 줄바꿈 CSS | 이미 들어 있음 |
| (b)1 iPad 홈 화면 앱 | **안 함 — 사용자 기기 확인**(홈 화면 앱에서 가장자리 쓸어 뒤로가 되는지 · ↩ 알약이 검색·내 표시·북마크 카드에서 뜨는지) |
| A17 · A19 | 안 함(build4·원고 — 다른 담당) |

### 테스트(고치기 전 4127b1ce → 고친 뒤 da991510)
| 테스트 | 전 | 후 |
|---|---|---|
| tests4/q_stub(새) | — | PASS |
| tests4/q_links(새) | — | PASS |
| ux_nav | PASS 64 | PASS 64 |
| ux26_links | PASS 20 | PASS 20 |
| ux_srchkeep | PASS 11 | PASS 11 |
| ux4_nav | FAIL 15(원래 실패 목록) | FAIL 15 — 실패 줄 같음 |
| ux2_load | PASS 51 | PASS 51 |
| ux_u30 | FAIL 2(원래 실패 목록) | FAIL 2 — 실패 줄 같음 |
| ux_kitfrev | PASS 23 | PASS 23 |
| ux_final | PASS 20 | PASS 20 |
| ux_gbclick | PASS 15 | PASS 15 |
| ux_marks | (기준 안 돌림) | PASS 22 |
| ux_align | PASS 27 | PASS 27 |
| ux_v3phone | PASS 57 | PASS 57 |
| q_empty | PASS 38 | PASS 38 |
| q_ident | PASS 14 | PASS 14 |
| q_isolation | PASS 17 | PASS 17 |
| q_sync | PASS 12 | PASS 12 |
| verify.py 3Q 스테이징(`JBL_Q=3q JBL_HTTP=1`) | PASS 281 | PASS 281 |
| verify.py 4Q(`JBL_HTTP=1`) | **죽음**(rc 1 · 123줄 형광펜 — 빈 과목 카드에 고를 글이 없음) | **죽음**(rc 1 · 109줄 — 빈 과목은 메뉴에 `_led`가 없음 = 이번에 일부러 숨김) |
| ux3_help | PASS 84 | **FAIL 3 — 테스트 기대값이 옛 글**(27줄 `need`의 `'1~6'` · 도움말은 지시 4번대로 '1~7') |

결과 파일: scratchpad `w1c/reg/*.log`(뒤) · `out_base/*.txt`(앞).

### 메인이 정할 것
1. **`tools/tests/ux3_help.py` 27줄 `'1~6'` → `'1~7'`** — 맡은 파일 밖이라 안 고침(이 한 글자만 바꾸면 PASS로 돌아옴 · 다른 실패 줄 없음).
2. **`tools/verify.py`가 4Q에서 죽음** — 4Q 10과목이 모두 빈 과목인 동안은 고치기 전에도 죽었음(죽는 줄만 123 → 109로 앞당겨짐). 빈 과목(`__h.PACKS[s].stub` 또는 order 0)은 과목별 검사를 건너뛰게 해야 4Q 검증이 끝까지 감. 맡은 파일 밖이라 안 고침. 4Q 허브 자체는 q_stub·q_empty로 확인됨.
3. **폰 학습 탭 줄 오른쪽 도구 묶음 글 겹침**(위 6번 (b)7 보고 — 원래 있던 것 · 안 ①~③ 가운데 고르기).
4. (b)1 iPad 홈 화면 앱 — 사용자 기기 확인.

### 남은 위험
- q_links·q_stub의 4Q 쪽은 빈 과목만 봄 — 4Q에 실제 강의가 들어오면(26 자료) q_links를 4Q 허브에서도 한 번 돌릴 것(지금은 3q/ 허브에서만).
- 커밋·푸시 안 함(메인이 함) · docs/·사본은 da991510과 같음(rehub '바꾼 파일 없음').
