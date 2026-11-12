먼저 /home/user/jbl/guide/handoff/upg1110/BRIEF_공통.md 를 끝까지 읽고 그대로 따른다(메인 저장소에서 일하는 '허브 담당' — 커밋 금지).

묶음 **W6 렉**. 읽기: guide/handoff/upg1110/R_DESIGN_설계.md §0('Table lag' 줄)·**§4 전체(설계 — 그대로)** · R_AUDIT_1104_측정.md #3·#10·#11·#17 · guide/handoff/UPD_4Q_진행.md 'P0 허브 점검' 줄(content-visibility를 되돌린 까닭) · shell.html의 tblMount·tblFit·twApply·twStats·twSolve·colFit·cfStats·learnSpy·setLCur·lmCount·navRender·navAfter·jbMini·mount·openDoc(복원 자리)·goEl·probePos·keepAt·keepCard·plEnd.
맡은 파일: tools/cons/shell.html · tools/SPEC.md(q_perf2는 만들지 않음 — 수치는 `tools/tests4/q_pos.py --perf`로 재고, 고치기 전 기준 표는 guide/handoff/upg1110/DONE_W0.md 6번에 있음) · 보고 guide/handoff/upg1110/DONE_W6.md.
할 일(자리 복원이 한 픽셀도 달라지면 안 됨 — tools/tests4/q_pos.py·tools/tests/ux_nav·ux_kitfrev·ux_marks·ux2_jbq가 지킴이):
1. 표 맞춤: twApply를 재기(읽기만)와 적용(쓰기만)으로 나눠 tblFit가 모든 읽기 → 모든 쓰기(표마다 강제 레이아웃 1번씩 하던 것) · 복원 자리(openDoc이 아는 목표) 위와 그 화면의 표는 바로, 나머지는 한가할 때 8개씩(IntersectionObserver 1500px 여유로 다가오면 먼저) · goEl로 건너뛰면 남은 줄을 먼저 비움 · 늦게 맞춘 표가 화면 위쪽이면 keepAt로 자리 유지 · twSolve 결과를 (팩 판 PV·문서·표 순번·폭 묶음·글자 크기·보기 모드)로 Map에 기억(다시 열면 재지 않음) · colFit의 CF 기억도 mount를 넘어 유지.
2. 그리기 뒤 일: learnSpy의 관찰자 만들기·navRender의 scrollIntoView 등 '읽기'를 자리 복원 다음 프레임으로(Kit.restore는 그대로 동기).
3. 팩 이어 받기: plEnd에서 다음 팩은 1.5초 입력이 없고 화면이 보일 때 시작(지금 보는 과목이 먼저 — 깊은 링크·검색·Ctrl+K가 필요로 하면 바로).
4. 2단계(스위치 `LS 'cvh'` 기본 끔 — 통과하면 메인이 켬): 문서를 처음 열 때 전부 레이아웃한 뒤 카드 높이를 (문서·탭·폭 묶음·보기 상태)로 기기 전용 기억 → 다음부터 그 높이를 contain-intrinsic-size로 주고 content-visibility:auto · 모두 펼치기·압축·인쇄·찾기 같은 한꺼번에 일은 끄고 → 하고 → 다시 재고 켬 · 높이가 달라질 수 있는 일(답 펼침·형광펜·글자 크기) 뒤 그 카드만 다시 잼. 스위치를 켠 채 지킴이 5개가 전부 통과할 때만 '켜도 됨'으로 보고(하나라도 실패면 끈 채 두고 실패 줄 보고).
측정(전·후 — `q_pos.py --perf` · 전 = DONE_W0.md 6번 표): 과목 비교표·정리표·학습·과목 JB·예상 여는 시간·LayoutCount · 두 번째 열기 · CPU 4배 · 목표: 표 탭 0.6~1.2초 → 0.3초 안팎, 두 번째 열기는 재기 0.
회귀(전·후): q_pos · ux_nav · ux_kitfrev · ux_marks · ux2_jbq · ux2_tables · ux3_tables · ux_align · ux_fbar · ux_v3phone · ux2_load · tests4 q_crawl·q_perf.
끝나면 마지막 메시지에: 전·후 수치 표 · 스위치 켜도 되는지 · 메인이 정할 것.


(11-12 덧붙임) 지금은 다른 담당이 없다 — 메인 저장소에서 혼자 일함. 사용 한도로 멈출 수 있으니 DONE_W6.md를 항목 하나 끝날 때마다 갱신하고, 1번(표 맞춤) → 회귀 → 2번 → 3번 → 회귀 → 4번(스위치) 순서로 **단계마다 지킴이(q_pos 전체 + ux_nav·ux_kitfrev·ux_marks·ux2_jbq)를 돌려 통과를 확인한 뒤 다음 단계**로. 단계 하나가 지킴이를 깨고 30분 안에 못 고치면 그 단계만 되돌리고 보고(앞 단계 성과는 지킴). 3Q 회귀는 `JBL_HTTP=1 .venv/bin/python tools/tests/<이름>.py`(먼저 `rehub.py --q 3q --stage`) · 긴 테스트는 `timeout` 붙여서.
