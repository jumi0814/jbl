먼저 guide/handoff/upg1110/BRIEF_공통.md 를 끝까지 읽고 그대로 따른다. 너는 **메인 저장소 담당**(/home/user/jbl — 커밋·푸시·git stash 금지 · 지금 다른 담당은 없음).

묶음 **W0 안전망(가벼운 판) — 이어 가기**. 앞 담당이 사용 한도로 멈췄고, 그 작업분(시험용 사이트 `qsite.build_fixture`·`q_ident` 린트·`q_crawl.py` 일부)은 이미 메인에 합쳐져 있다(커밋 b607f618 — `q_ident` PASS 확인됨). 원래 지시문 = guide/handoff/upg1110/agents/UPG_T.md(1~7번) — 그중 **아래 것만** 한다. 보고 `guide/handoff/upg1110/DONE_W0.md`(체크 목록이 있음 — 항목 하나 끝날 때마다 고쳐 씀).
읽기: tools/tests4/qsite.py·q_crawl.py·q_links.py(쓰는 법 참고) · guide/handoff/upg1110/R_DESIGN_설계.md §4·§5 · R_HISTORY…md 4번(기준 실패 37개 분류) · guide/handoff/UPD_4Q_진행.md(기준 실패 목록) · tools/tests/ux_all.py · tools/full_check.sh.
맡은 파일: tools/tests4/qsite.py·q_crawl.py·새 q_pos.py · tools/tests/ux_all.py·새 tools/tests/STATUS.json·tools/tests/fmt_cases.py(판정 줄만) · tools/full_check.sh · DONE_W0.md. **tools/cons/shell.html·build4.py·num.js는 건드리지 않음**(버그를 찾으면 고치지 말고 보고).

할 일(이 순서 · 사용량을 아낌 — 큰 탐색 금지, 필요한 함수만 grep):
1. **시험용 사이트 확인**: `build_fixture()`가 지금 코드(11-11 — 4Q 그림 파일 방식 `quarters.json 4q.img=files`·팩 `imgf`가 생긴 뒤)에서도 되는지 — 4Q 정체성(`__h.NS==='jbl4q.v1.'`)으로 3Q 7과목 내용이 열리고 그림(묶음 방식 3Q 팩)이 뜨고 콘솔 오류 0. 안 되면 qsite만 고침.
2. **q_crawl.py 마무리**: 3q/ 허브·fixture·4Q 뿌리(빈 과목 10)에서 과목마다 모든 문서 + 강의마다 모든 탭 → pageerror·console error·HTTP ≥400 0 · 글에 undefined/NaN/[object Object] 0 · 가로 넘침 0 · 빈 #stage 0(1280 · 폰 393은 과목마다 문서 2~3개만 — 시간 줄이기). 전체 15분 안에 끝나게(느리면 강의 탭은 과목마다 가장 큰 강의 2개 + 나머지는 학습 탭만).
3. **q_pos.py(자리 지킴이 — 다음 묶음 '렉'의 안전판 · 가장 중요)**: fixture 또는 3q/ 허브에서 가장 긴 학습·정리표·비교표·기출·예상·과목 JB·과목 비교표 문서의 깊이 3곳(위·가운데·아래)마다 ① 탭 전환 뒤 돌아옴 ② 브라우저 뒤로/앞으로 ③ 새로고침 ④ 칩으로 건너갔다 ↩ → 같은 카드(`data-aid`/id)가 같은 화면 위치(±2px)인지, 100ms와 1.5초 뒤 두 번 잼. **지금 코드에서 통과해야 함** — 지금 실패하는 경우는 '이미 있는 버그'로 목록에(테스트에서는 KNOWN으로 표시해 RESULT PASS가 되게 하고 DONE에 재현 적음). 10분 안에 끝나게.
4. **STATUS.json**: 기준 실패 37개를 **하나씩 다시 돌리지 않고** R_HISTORY 4번 분류표와 UPD_4Q_진행.md 목록으로 `tools/tests/STATUS.json` `{"<테스트>": {"st": "local|retired|helper|bug?", "why": "한 줄", "see": "대신 보는 테스트"}}` · ux_all.py: helper(fakegist 등)는 목록에서 뺌 · local은 필요한 것(work/jb·옛 커밋·work/_legacy 등)이 없으면 SKIP · retired는 돌리지 않고 SKIP 줄(파일은 옮기지 않음 — 기록 지킴이 legacy_restore·legacy_restore_107·ux2_sum_mig·ux3_compat은 retired가 아니라 local) · 끝 요약 = PASS n · SKIP n(이유별) · FAIL 목록(STATUS에 없는 실패만 진짜 실패 — 종료 코드 1). 'bug?'로 의심되는 3개(ux_u18·ux4e_names·ux4f_O)만 한 번씩 돌려 지금 결과를 why에. fmt_cases 판정 줄은 분류표에 고칠 곳이 적혀 있을 때만.
5. **full_check.sh**: tests4 루프가 새 q_crawl·q_pos도 돌고, 3q일 때 ux_all 요약이 STATUS 기준(PASS·SKIP만이면 통과)으로 읽히게. 전체 full_check는 돌리지 않음(메인이 함) — `sh -n`과 바뀐 부분만 확인.
6. (시간이 남을 때만) q_perf2 — 하지 않아도 됨. 대신 DONE에 '렉 묶음 전 기준 수치'로 fixture에서 과목 비교표·정리표·학습(가장 큰 것) 여는 시간(ms)과 LayoutCount를 한 번 재서 표로 적음(CDP Performance.getMetrics — 스크립트는 scratchpad가 아니라 q_pos.py 안의 `--perf` 옵션으로 남겨도 됨).

끝나면 마지막 메시지(짧게): 새 테스트마다 지금 결과·걸린 시간 · STATUS 분류 표(수) · 'bug?' 3개 결과 · q_pos가 찾은 이미 있는 버그 · 메인이 정할 것.
