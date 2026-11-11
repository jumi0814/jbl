# DONE_W0 — 안전망(가벼운 판) · 11-10 시작 → 11-11 이어 감

지시문: `guide/handoff/upg1110/agents/UPG_T2_안전망.md`(가벼운 판 — 원래 `agents/UPG_T.md` 1~7 가운데 고른 것) · 계획 `PLAN.md` W0 · 설계 `R_DESIGN_설계.md` §4·§5 · `R_HISTORY…md` 4번.
앞 담당(worktree `worktree-agent-ac5912c51bbd11a94` — 273be7ec)이 한도로 멈춤 → 그 작업분(시험용 사이트 `qsite.build_fixture`·`q_ident` 린트·`q_crawl.py` 일부)은 메인 b607f618에 합쳐져 있음. 이 보고는 **메인 저장소 담당(11-11)**이 이어 쓴 것 — 커밋·푸시 안 함(메인이 함).
허브 코드(`tools/cons/shell.html`·`build4.py`·`num.js`)·`q_perf.py`는 건드리지 않음.

진행(항목 하나 끝날 때마다 고쳐 씀 — 한도로 멈춰도 여기서 이어 감):

- [ ] 1 시험용 사이트(fixture) `qsite.build_fixture()` — 11-11 코드(4Q 그림 파일 방식)에서 확인
- [ ] 2 `q_crawl.py` 마무리
- [ ] 3 `q_pos.py`(자리 지킴이)
- [ ] 4 `tools/tests/STATUS.json` · `ux_all.py`
- [x] (앞 담당 · b607f618) `q_ident` 린트 넓히기 — PASS 확인됨(메인)
- [ ] 5 `full_check.sh`
- [ ] 6 렉 묶음 전 기준 수치(`q_pos.py --perf`)

## 항목별 기록
