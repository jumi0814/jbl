# 전면 점검·개선(11-10) — 담당 공통 지시(모든 담당 지시문 맨 앞)

저장소 /home/user/jbl(또는 내 worktree). 파이썬 `.venv/bin/python`(worktree면 `ln -s /home/user/jbl/.venv .venv`). 보고는 한국어.
먼저 읽기: `CLAUDE.md`(쿼터 절·절대 규칙) · `guide/handoff/upg1110/PLAN.md`(승인된 계획 — 내 묶음 절) · 내 묶음의 점검 보고(`guide/handoff/upg1110/R_*.md` — 줄 번호는 커밋 b714aca8 기준이라 **함수 이름으로 grep**) · 허브를 고치면 `tools/SPEC.md` 해당 절과 `guide/정리본_원칙.md` 7-1·7-2b(디자인 v3 · 화면 연결).

## 절대 지킬 것
- **3Q 저장 이름 상수는 그대로**(tools/quarters.json 3q.ident — 바꾸면 3Q 기록이 안 보임) · 허브 코드에 저장 이름 글자를 새로 쓰지 않음 · 쿼터 정체성은 `QC.*`로만(전역 `T·QC·NS·LS·SYNC·XS·PACKS·CUR`을 지역 변수 이름으로 다시 선언하지 않음 — 11-04 사고).
- **사용자 기록(형광펜·빈칸·메모·채점·북마크·넘버링·공부 시간)은 지우지 않음** — 옮기거나 고쳐 써야 하면 먼저 `autoBak` · 지움 대신 표시 · 옛 판 코드가 읽어도 깨지지 않는 꼴.
- **새 기능을 넣지 않음**(사용자 11-10 "시험직전모드는 필요없어" — 고치는 일만). 계획에 없는 화면·단추를 만들지 않음. 화면 글은 쉬운 한국어, 기존 낱말 그대로(답 보기 → 해설 더 ▾ → 답 접기 ▲ · ⭐ 기출 / ★ 북마크).
- 새 CSS는 디자인 v3(shell.html 맨 끝 v3 묶음 뒤에 · 누르는 것 = 먹색 `--brand` · 의미 색 토큰 · 과목 색은 점·밑줄·선택 막대에만 · 새 단추/칩 꼴 금지 · 폰 누름 자리 ≥ 32px).
- Claude 지식으로 공부 내용을 만들지 않음(내용은 자료·JB에서만 — 이 작업은 코드·문서 고침).

## 허브(shell.html)를 고치는 담당
- 고치는 파일은 `tools/cons/shell.html` 하나(과목 폴더 사본은 `tools/sync_common.py`가 만듦 — 직접 고치지 않음). 줄이 매우 길어 Edit가 어려우면 파이썬으로 '글자 그대로 바꾸기 + `assert t.count(a)==1`'.
- 고친 뒤: `.venv/bin/python tools/sync_common.py` → `.venv/bin/python tools/rehub.py`(4Q docs/) → `.venv/bin/python tools/rehub.py --q 3q --stage`(3Q 스테이징 work/_tmp/hub3q — 3Q 테스트가 여는 곳).
- 테스트: 3Q 회귀 `JBL_HTTP=1 .venv/bin/python tools/tests/<이름>.py`(tools/tests 안은 저절로 3Q 스테이징) · 쿼터 범용 `.venv/bin/python tools/tests4/<이름>.py`(qsite가 4Q = 뿌리·3Q = 3q/ 두 허브를 한 주소로 띄움 — 내용이 필요한 시험은 3q/ 허브에서, 과목·강의·카드는 `__h.PACKS`에서 찾아 씀 — id를 박지 않음). 무거운 테스트는 하나씩(동시에 돌리면 시간에 민감한 것이 거짓 실패) · 전체 `ux_all`은 돌리지 않음(메인이 함).
- `tools/tests/` 기준 실패 37개(guide/handoff/UPD_4Q_진행.md 재개 메모)는 원래 실패 — 내 고침 뒤 **새로** 실패하는 것만 문제(고치기 전 결과와 견줌).
- 바뀐 동작은 `tools/SPEC.md`(해당 절에 '11-10' 한 줄)·코드 옆 주석(기존 꼴 `/* 11-10 … */`)에. 화면 규칙이 바뀌면 `guide/정리본_원칙.md`도.
- 넘버링은 `tools/num/num.js` → `.venv/bin/python tools/num/build_num.py`.

## 끝낼 때
- 보고 파일 `guide/handoff/upg1110/DONE_<묶음>.md`: 항목마다 '고침(어디·어떻게) / 안 함(왜)' · 돌린 테스트와 결과(고치기 전 대비) · 메인이 정할 것 · 남은 위험. 시작할 때 머리를 먼저 쓰고 항목 하나 끝날 때마다 덧붙여 저장(한도로 멈춰도 이어 가게).
- 메인 저장소에서 일하는 담당은 **커밋·푸시·git stash 금지**(메인이 함). worktree 담당은 자기 worktree 브랜치에 커밋만(푸시 금지) — 마지막 메시지에 브랜치·커밋 해시.
- 맡은 파일 밖은 고치지 않음(다른 담당이 동시에 일함 — 지시문에 적힌 파일만).
