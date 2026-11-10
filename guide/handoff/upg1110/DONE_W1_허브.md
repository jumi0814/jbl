# DONE_W1_허브 — 빈 과목·그림 다시 받기·이동(11-10 · 허브 담당)

맡은 파일: `tools/cons/shell.html` · `tools/tests4/q_stub.py`·`q_links.py`(새로) · `tools/SPEC.md` · `guide/정리본_원칙.md` · 이 보고.
(build4.py는 다른 담당 — 건드리지 않음 · 커밋·푸시·stash 안 함)

지시 = `guide/handoff/upg1110/agents/UPG_H1.md` · 점검 보고 = `R_NAV_이동·연동·빈과목.md`(A1~A24 · (b)1~8).

## 이어받음(11-10 둘째 담당)
앞 담당이 shell.html만 고치다 한도로 멈춤(커밋 983e9740 'WIP' · 기준 4127b1ce). `git diff 4127b1ce 983e9740 -- tools/cons/shell.html` 68곳을 항목별로 읽어 아래 목록을 실제 상태로 고침.
- 이어받을 때 shell.html 두 `<script>`를 메모리에서 컴파일 → 문법 오류 0(기준 커밋도 0).
- 과목 폴더 사본·docs/·3Q 스테이징은 이어받을 때 옛 판(sync_common·rehub 전).

## 진행(항목 하나 끝날 때마다 덧붙임)

- [ ] 고치기 전 회귀 기준 잡기(worktree 4127b1ce)
- [~] 1. 빈 과목(A11~A16 · (b)4·5) — **앞 담당 코드 다 들어감**(isStub·isWait·profOf·allStub·noData · resOk·homeResume·resumeTarget · 과목 표 '자료 대기' · 오늘 할 일 · actBtn · docHas/docOk → openDoc·sjKeepDoc·qjIndex·navSubj · 빈 화면 글 · lpn·머리·강의 카드 · Ctrl+K 비교표·그림빵 · WAIT 표시 막음 · 검색 색인 · #htop) · 남은 것 = 화면 확인 · WAIT 메모 키
- [~] 2. 그림(A1 · A18) — **앞 담당 코드 다 들어감**(needImages·imgLoad 다시 받기 · openImg 없는 쪽) · 남은 것 = 화면 확인
- [~] 3. ↩·자리(A2~A7 · A20 · A24 · (b)2 · (b)8 · A10 강의 카드) — **거의 다 들어감** · 남은 것 = 학습 거르기 되살린 뒤 카드 수·빈 묶음 맞춤 · 허브 화면(검색·달력·내 강의목록·넘버링)으로 갈 때 PL.lost 지움 · 화면 확인
- [~] 4. 주소(A8 · A9) — docOk·숨은 탭 알림 들어감 · 남은 것 = 도움말 '1~6'
- [~] 5. 키·터치(A21~A23) — 넘버링 편집 중 Ctrl+K만 들어감 · 남은 것 = SELECT · 답 바로 보기 36px
- [ ] 6. (b)3 · (b)7 확인
- [ ] 새 테스트 q_stub · q_links
- [ ] 회귀(고친 뒤)
- [ ] SPEC.md · 정리본_원칙.md
