먼저 /home/user/jbl/guide/handoff/upg1110/BRIEF_공통.md 를 끝까지 읽고 그대로 따른다(메인 저장소에서 일하는 '허브 담당').

묶음 **W1 허브 쪽** — 빈 과목·그림 다시 받기·이동. 점검 보고 = guide/handoff/upg1110/R_NAV_이동·연동·빈과목.md(A1~A24 · (b)1~8 · 'Deferred' 표) 전부 읽기. 맡은 파일: tools/cons/shell.html · tools/tests4/q_stub.py·q_links.py(새로) · tools/SPEC.md · guide/정리본_원칙.md · 보고 guide/handoff/upg1110/DONE_W1_허브.md. (build4.py는 다른 담당 — 건드리지 않음.)

할 일(R_NAV 번호):
1. 빈 과목(A11~A16 · (b)4·5): `isStub(p)` = `p.stub===true || (!((p.order||[]).length) && (p.lect||[]).every(L=>L.k==='WAIT'))`(build4가 곧 `pack.stub`을 냄 — 지금 팩엔 없으니 뒤 조건으로도 잡히게). 적용: homeResume·resumeTarget(시작하기·이어서가 대기 강의로 안 감 · 과목이 전부 빈 과목이면 지금의 qEmpty 안내) · 허브 과목 표 줄('자료 대기' — 0/0 대신) · 오늘 할 일 · actBtn('기출을 다 맞혔어요' → '자료 대기') · sjKeepDoc + openDoc(빈 과목·빈 문서면 _home) · JB/예상/비교표 빈 화면 글('조건에 맞는 문항이 없습니다'는 거르기가 켜졌을 때만 — 자료가 없으면 '아직 자료가 없어요') · lpn·과목 머리·강의 머리('- - 강의자료 대기'·끝에 ' · '·빈 h1 → 교수 '-'는 없는 것으로, en이 비면 과목 이름) · qjIndex·navSubj(0개 문서·WAIT 탭 항목 숨김 — 빈 과목은 과목 홈만) + Ctrl+K 강의 항목에 비교표·그림빵 탭도(있는 강의만) · WAIT 카드는 표시(✓·★·형광펜·빈칸) 못 하게 · 검색 색인에서 WAIT 강의 뺌 · #htop(2회 이상 출제)은 0개면 숨김.
2. 그림(A1): needImages 실패 → 1.5초 뒤 한 번 다시(캐시 피해서) → 또 실패면 imgWait[key] 지우고 script 제거·열린 그림 창 스피너 닫고 '그림을 받지 못했어요 [다시]' 알림(다음 호출은 다시 받음). A18: openImg에서 없는 쪽이면 1쪽 대신 알림(가장 가까운 있는 쪽을 열되 '그 쪽 원본이 없어 n쪽을 열었어요' — 쪽이 하나도 없으면 닫고 알림).
3. ↩·자리(A2~A7·A20·A24·(b)2·(b)8): retFrom에 y 저장·goRet가 {pos,y} · search()가 ↩ 스택을 지우지 않음(결과를 열 때만 정리) · '더 보기' 펼침을 SQ·history state에 기억(뒤로·sxDone 다시 그리기에도 유지) · marksGo·data-cbmgo·resClick(검색 결과 → 검색으로 돌아오는 ↩)·넘버링 화면에서 Ctrl+K로 갈 때 ↩ · 학습 탭 거르기(묶음 알약·only-*)를 fltRead/fltRestore에 · golec 카드가 없으면 '그 카드를 찾지 못해 강의 처음으로 왔어요' · 받는 중인 과목 깊은 링크는 주소를 #/로 바꾸지 않음 · PL.lost는 사용자가 다른 곳으로 가면 지움 · 아직 안 받은 과목 바꾸기 단추는 '불러오는 중' 알림. A10의 과목 홈 강의 카드: 본문을 눌러도 아래 '📖 정리본'과 같게 ↩ 생김(같은 곳으로 가는 같은 동작). 예상 카드의 관련 기출 칩이 JB로 건너가는 것은 그대로 둠.
4. 주소(A8·A9): openDoc에 `docOk(p,d)` — `_`로 시작하는 문서가 SUBJDOCS에 없거나 _final인데 N제 0·_fig인데 그림빵 0이면 _home + 기존 '없는 강의' 알림 꼴(sjKeepDoc도 같은 함수) · 도움말 '1~6 탭 바꾸기' → 실제(보이는 탭 순서 1~7) · 숨은 탭 주소로 오면 첫 탭으로 가며 한 줄 알림.
5. 키·터치(A21~A23): 한 글자 단축키는 SELECT에 초점일 때 끔 · 넘버링 편집 칸(#numv [contenteditable])에 초점이면 Ctrl/⌘+K 끔 · 검색 '답 바로 보기' 누름 자리 폰 36px.
6. (b)3 #jbpeek가 J/K·스크롤로 떠다니는지 3Q 스테이징에서 확인해 떠다니면 스크롤·이동 때 닫음. (b)7 폰 393 학습 탭 줄 흐림 표시 확인만(고칠 게 있으면 보고).
하지 않는 것: (b)1 iPad 기기 확인(보고에 '사용자 기기 확인' 한 줄) · A17·A19(build4·원고 — 다른 담당) · 표 맞춤·그림 파일(뒤 묶음).

테스트: 새 tools/tests4/q_stub.py(4Q 빈 과목 10개 — 과목 홈 글·시작하기·Ctrl+K 항목 수·과목 바꾸기·없는 주소·WAIT 카드 표시 불가 · 폰 393도) · 새 tools/tests4/q_links.py(3q/ 허브에서 PACKS로 찾아: 칩 종류마다 건너감 → ↩로 같은 자리(±2px) · 과목 홈으로 ↩ · 검색 '더 보기' → 결과 → 뒤로 · 검색 뒤 ↩ 스택 유지 · 내 표시·★ 카드·검색 결과 ↩ · 넘버링 Ctrl+K ↩ · 학습 거르기 유지 · 없는 `_` 주소 · needImages 실패 뒤 다시 받기(page.route로 한 번 abort)) · 회귀(고치기 전·후 견줌): ux_nav · ux26_links · ux_srchkeep · ux4_nav · ux2_load · ux_u30 · ux_kitfrev · ux_final · ux_gbclick · tests4 q_empty·q_ident·q_isolation·q_sync + tools/verify.py(`JBL_HTTP=1` 4Q · `JBL_Q=3q JBL_HTTP=1` 3Q 스테이징).
끝나면 마지막 메시지에: 항목별 고침/안 함 · 테스트 결과(전·후) · 메인이 정할 것.
