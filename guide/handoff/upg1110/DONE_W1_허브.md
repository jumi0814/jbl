# DONE_W1_허브 — 빈 과목·그림 다시 받기·이동(11-10 · 허브 담당)

맡은 파일: `tools/cons/shell.html` · `tools/tests4/q_stub.py`·`q_links.py`(새로) · `tools/SPEC.md` · `guide/정리본_원칙.md` · 이 보고.
(build4.py는 다른 담당 — 건드리지 않음 · 커밋·푸시·stash 안 함)

지시 = `guide/handoff/upg1110/agents/UPG_H1.md` · 점검 보고 = `R_NAV_이동·연동·빈과목.md`(A1~A24 · (b)1~8).

## 이어받음(11-10 둘째 담당)
앞 담당이 shell.html만 고치다 한도로 멈춤(커밋 983e9740 'WIP' · 기준 4127b1ce). `git diff 4127b1ce 983e9740 -- tools/cons/shell.html` 68곳을 항목별로 읽어 아래 목록을 실제 상태로 고침.
- 이어받을 때 shell.html 두 `<script>`를 메모리에서 컴파일 → 문법 오류 0(기준 커밋도 0).
- 과목 폴더 사본·docs/·3Q 스테이징은 이어받을 때 옛 판(sync_common·rehub 전).

## 진행(항목 하나 끝날 때마다 덧붙임)

- [~] 고치기 전 회귀 기준 잡기 — scratchpad `base_w1`(worktree 4127b1ce · 자체 3Q 스테이징)에서 하나씩 도는 중
- [~] 1. 빈 과목(A11~A16 · (b)4·5) — **코드 끝**(앞 담당: isStub·isWait·profOf·allStub·noData · resOk·homeResume·resumeTarget · 과목 표 '자료 대기' · 오늘 할 일 · actBtn · docHas/docOk → openDoc·sjKeepDoc·qjIndex·navSubj · 빈 화면 글 · lpn·머리·강의 카드 · Ctrl+K 비교표·그림빵 · WAIT 표시 막음 · 검색 색인 · #htop / 이어서: WAIT에서 M(메모)도 막음) · 남은 것 = 화면 확인(q_stub)
- [~] 2. 그림(A1 · A18) — **코드 끝**(앞 담당: needImages·imgLoad 다시 받기 · openImg 없는 쪽) · 남은 것 = 화면 확인(q_links F)
- [~] 3. ↩·자리(A2~A7 · A20 · A24 · (b)2 · (b)8 · A10 강의 카드) — **코드 끝**(이어서: 학습 거르기를 되살린 뒤 `gdivEmpty`·`lmCount` · 검색·달력·내 강의목록·넘버링으로 갈 때도 `PL.lost` 지움) · 남은 것 = 화면 확인(q_links A~D)
- [~] 4. 주소(A8 · A9) — **코드 끝**(이어서: 도움말 '1~6' → '1~7 탭 바꾸기(보이는 탭 순서대로)' · 키 정규식 1-7) · 남은 것 = 화면 확인(q_links E)
- [~] 5. 키·터치(A21~A23) — **코드 끝**(이어서: SELECT `isKbSelect` · '답 바로 보기' 폰 36px) · 남은 것 = 화면 확인(q_links G)
- [ ] 6. (b)3 · (b)7 확인
- [~] 새 테스트 q_stub · q_links — 파일 씀 · 아직 안 돌림
- [ ] 회귀(고친 뒤)
- [x] SPEC.md(끝에 '11-10 W1' 절 + 쿼터 절 테스트 줄 + 키 표 1~7) · 정리본_원칙.md 7-2b(↩ 규칙 3줄 + '11-10 빈 과목·없는 화면' 묶음)
- [x] sync_common(17개 사본 동일) → rehub 4Q(docs/ BUILD 13a9c87a) → rehub --q 3q --stage — 한 번 돌림(끝에 다시)
