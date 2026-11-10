먼저 /home/user/jbl/guide/handoff/upg1110/BRIEF_공통.md 를 끝까지 읽고 그대로 따른다(메인 저장소에서 일하는 '허브 담당' — 커밋 금지).

묶음 **W4 공부 시간**. 읽기: guide/handoff/upg1110/R_DESIGN_설계.md §0(T1 줄)·§1 W1 표·**§2 전체(설계 — 그대로 따르되 아래 '사용자 선택'이 이김)** · R_DATA…md A1~A5·(b)1 · tools/SPEC.md 공부 시간 절 · guide/피드백기록.md에서 시계 관련 줄(10-02~10-07 — 하루 경계 06:00·수동 ▶ 세션·자동 측정·되묻기·휴식의 뜻) · tools/tests/ux3_timer.py·ux3_rest.py·ux5_sess.py·ux3_tedit.py·ux3_fixes.py(시계 부분)·ux4g_A.py.
맡은 파일: tools/cons/shell.html · tools/quarters.json·tools/quarters.py(쿼터 공용 시계 채널 이름을 qcfg로 내는 것만) · 새 tools/tests4/q_timer.py · tools/tests/ux3_timer.py(의도적으로 바뀐 기대값만 — 무엇을 왜 바꿨는지 보고) · tools/SPEC.md · 보고 guide/handoff/upg1110/DONE_W4.md.

**사용자 선택(11-10)**: "자동으로 빼고 알림" — 잠든 구간은 묻지 않고 자동으로 빼고, 다시 열면 알림 하나 + 되돌리기.
- 잠듦 판정: 틱 사이 간격 g = now − max(tstate.at, T.tk) ≥ 90초(틱마다 T.tk 기록 · tstate.at은 지금도 ≤20초마다 씀).
- 수동 세션(st==='sess')에서 깨어났을 때, li = 마지막 입력, idle = now − li, A = 되묻기 기준(sessAskMin — 기본 90분):
  - idle < A → 지금처럼 전부 셈(화면이 잠긴 채 책으로 공부).
  - idle ≥ A (A > 0) → **묻지 않고** 세션을 li + 1분에서 끝냄(간격을 먼저 기록하지 않음 — sessFlush가 li+1분까지만) → 알림 띠/토스트 "잠든 n시간 n분은 공부 시간에서 뺐어요 [되돌리기]" — 되돌리기 = 뺀 구간을 그 세션 과목·문서에 다시 넣음(달력 '+ 시간 추가'가 쓰는 길로 — tedit에 한 줄 · 하루 경계 06:00으로 나눔) · 알림은 다음 입력 뒤에도 30초는 남고 달력 그날 줄에서도 되돌릴 수 있으면 더 좋음(있던 '시간 고침' 되돌리기 길을 씀).
  - 깨어 있는 채 입력만 없는 경우(g < 90초)는 지금 그대로(A에서 되묻기 띠 → 30분 뒤 li+1분에 끝).
  - A = 0(되묻기 끔)은 지금 그대로(12시간 상한 — ux3_timer 125줄 기대 유지).
- 12시간 상한 검사보다 먼저 판정(trTick) · 시작 때(boot — 켜진 채 닫힌 세션 질문 자리)도 idle ≥ A면 같은 자동 길(질문 대신) · 보이게 될 때(visibilitychange·pageshow) 바로 trTick · 시계 숫자(sessLiveFor·trSessMs·trFocusMs)도 같은 잣대로 잘라 부푼 숫자가 잠깐도 안 보이게.
그 밖: T2 시계가 뒤로 가면(now < T.t0 − 2초 · ts.seg > now + 2초) 기준을 지금으로 다시 잡음 · T6 trTake에서 ts.cls 지움 · T4 tedit: 자동 줄임(tUnrec — trAutoRest·restBack)이 줄마다 쌓이지 않게 (기기·날·과목·문서·종류)로 정해진 id 한 줄에 ms 누적(teMerge는 같은 id면 나중 at이 이김 — 옛 줄은 그대로 두고 읽음) · T3 3Q·4Q 시계 겹침: 쿼터 공용 BroadcastChannel(이름은 등록표 맨 위 한 값 → qcfg — 3Q 정체성 값은 안 바꿈) — 다른 쿼터 창이 측정 중이면 이쪽 자동 측정은 쉼(수동 ▶는 사용자가 누른 것이라 그대로 · 3Q 허브는 index를 다시 만들 때부터 적용) · T5 4Q 첫 실행 2차 가져오기 `qimport2`(이미 1차 표시가 있는 기기도 한 번 더): tauto·tgoal·sessAsk·jbauto·jbautoNg·jbhidePrev·ascope·sumhide·cond·autofold·exfirst·qz 설정 키(코드에서 실제 키 이름 확인) — 4Q에 값이 없을 때만, 기록 키는 절대 아님.
테스트: 새 tools/tests4/q_timer.py(가짜 시계 — ux3_timer가 쓰는 방식 재사용: ▶ 뒤 100분 잠듦(idle ≥ A → 자동 빼기 + 알림 + 되돌리기로 복구) · 30분 잠듦(전부 셈) · 8시간 잠듦 · 자정·06:00 경계를 낀 잠듦 · 되묻기 끔 12시간 · 시계 뒤로 · cls 남은 세션 · 4Q 뿌리와 3q/ 허브 둘 다) · 회귀(전·후 견줌): ux3_timer · ux3_rest · ux3_fixes · ux3_tedit · ux5_sess · ux4g_A · ux3_restui · kt_sync · ux_sync(T 묶음) · tests4 q_isolation·q_sync.
끝나면 마지막 메시지에: 항목별 고침/안 함 · 테스트 전·후 · 화면 글(알림 문구) · 메인이 정할 것.
