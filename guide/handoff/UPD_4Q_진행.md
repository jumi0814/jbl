# 4Q 진행 (11-04 시작)

사용자 원문·결정 = guide/피드백기록.md 11-04 · 계획(승인) = 아래 요약 · 내용 규칙 = .claude/skills/jbl-update/RULES.md 14절 · 담당 요약 guide/handoff/Q4_RULES_BRIEF.md

## 사용자 결정(11-04)
1. 주소: `jumi0814.github.io/jbl/` = 4Q · 3Q는 `/jbl/3q/` 보관 · 두 허브에 3Q⇄4Q 전환 · "용량커지거나 해서 렉 절대 안 생기게끔"
2. 26이 오면 25에만 있고 기출과 무관한 내용은 그냥 지움(표시도 함께)
3. 2026 3Q 실제 기출 = 4Q 분석 + 3Q 사이트에도 '2026 출제'로 추가
4. 4Q는 동기화·화면 설정만 이어받기(공부 시간·기록은 새로)

## 단계
- [x] P0 등록표 `tools/quarters.json`·`quarters.py` · `jblpaths`(J.Q·DOCS·HUB_DIR·docs_of·pack_path·sids)
- [x] P0 허브 정체성 `const QC=/*QCFG*/`(3Q = 원래 상수 · 4Q 따로) · NS 기반 정규식 · 4Q 첫 실행 가져오기(설정·토큰만) · 전환 링크(메뉴·홈) · 다른 쿼터 과목 주소 넘기기 · 빈 과목 달력 오류
- [x] P0 도구: build4(쿼터 docs·frozen 거부·fill_index·manifest) · rehub(--q·--stage·--site·아이콘) · sync_common·build_num(살아 있는 쿼터 전부) · jbx(4Q JB) · matx(materials/4Q) · cloud/push_materials · full_check(JBL_Q·tests4·check_25only) · 스크립트 SID 목록 → 등록표 · verify(과목 수)
- [x] P0 `tools/new_subject.py` — 시험 SID로 첫 build4 → 4Q 허브에 과목 뜸(q_empty) → 지움
- [x] P0 tests4: q_ident · q_isolation(한 브라우저 두 허브 — 3Q 기록 글자 그대로) · q_empty · q_perf(기준 perf_base.json)
- [x] P0 4Q 내용 규칙: RULES 14 · AGENTS B1Q·B2Q·PROF·HIT · QA 97~99 · SKILL '4Q 판' · 정리본_원칙 · guide/prof/README.md · Q4_RULES_BRIEF · check_25only
- [x] P0 3Q 회귀: 3q-final 기준(worktree) vs 새 허브 코드(3Q 정체성) — 155개: 기준 실패 37개와 같은 목록·같은 실패 줄(ux3_timer는 이제 통과 · ux3_tedit·ux3_fixes는 부하 때만 — 혼자 돌리면 기준과 같음) **단 ux_sync·ux_sync_all·ux_sync_num·ux_sync_real 4개가 새로 실패** → 원인: 정체성 블록 `const Q`가 syncPull의 지역 배열 `Q=[]`에 가려 `h.app!==Q.headApp`이 늘 참 → 받은 기록을 모두 버림(휴대폰이 첫 합치기·새로고침을 안 함) → 전역 이름을 `QC`로(34곳) · q_ident 린트 'QC로만' · 새 시험 tests4/q_sync(3Q·4Q 각각 두 기기 연결·첫 합치기·★ 합집합)
- [~] P0 허브 점검(담당 — work/_tmp/hub_audit_4q.md 20건) → 고침: Ctrl+K·과목 바꾸기 N제 없는 과목 · Ctrl+K·메뉴 이동 ↩ · JB 미리보기 '답 접기 ▲' · '예상 0' 탭 숨김 · Ctrl+K 영문 과목 코드 · 폰 학습 카드 표 글자 끊김 · 과목 홈 2회↑ 줄 0폭 · N제·경향 줄 말줄임 · JB 머리 '예상 n ▸' 먹색·32px · ☆ 대비 · 폰 탭 줄 60% · 글자 폭 잼 기억 · (메뉴 이동 ↩는 되돌림 — ux_nav '사이드바 이동에는 알약 없음'(10-22 같은 개편) · 화면 밖 카드 content-visibility는 되돌림 — 여는 시간 40~80%↓였지만 3프레임 뒤 카드 크기가 바뀌어 goEl·위치 복원·모두 펼치기가 1100px씩 어긋남(ux_nav·ux_kitfrev·ux_marks·ux2_jbq F05) → 긴 화면 속도는 따로: 위치 기능을 다 맞춘 가상 목록/c-v + 안정화 루프)
  - 다음(나중): 비교표·정리표 열 폭 맞춤을 보이는 표부터(PHARM 비교표 4배 CPU 3.7초 — 위치 복원과 함께 시험) · 4Q 그림 = 파일(webp)+URL(첫 그림 대기·메모리↓ — 넘버링 Word 내보내기는 fetch로) · 검색 결과 다 그리지 않기 · 콘텐츠 ★(4Q 원고 규칙 — 3Q 원고는 그대로)
- [x] P0 전환(11-04): `tools/cutover.py` — 3Q 108개 파일 이름 바꿈만 + 3Q index 한 줄(⇄ 4Q 링크) · 등록표 current=4q·3q docs/3q frozen · 4Q 빈 허브 docs/(탭 제목 'JBL 4Q' — 등록표 `title` · 3Q는 'JBL 허브' 그대로) · 확인: verify(docs/3q 7과목·docs 4Q 0과목) · tests4 · 실제 /jbl/ 배치 연기(⇄ 양쪽·다른 쿼터 과목 주소 → 3q/·3Q 기록 보임·설정 이어받음·그림·404 0) · 되돌릴 기준 = 태그 `3q-final`(= 전환 전 origin/main de02f90)
- [x] P0 배포(11-04 23:43 — main 6d8dda0 · 실제 https://jumi0814.github.io/jbl/ 연기 통과: 4Q 'JBL 4Q'·⇄ 양쪽·3Q 7과목·그림·다른 쿼터 과목 주소 → 3q/·404 0) · 태그 3q-final은 프록시가 태그 푸시를 막아 로컬에만 — 되돌릴 기준 = 커밋 de02f90(main 기록에 있음) · rehub도 JBL_UNFREEZE=1이면 보관 쿼터를 씀(P1용)
- [ ] P0 배포 뒤 기기 확인(사용자): iPad 홈 화면 앱 → 4Q 빈 허브(화면 설정 이어짐) · ⇄ 3학년 3쿼터 → 3Q 기록 그대로 · 동기화 켜져 있던 기기는 4Q에서도 켜짐(토큰만 — 4Q 기록은 새 Gist 'JBL 4Q 동기화')
- [ ] P1 2026 3Q 실제 기출 받기 → 과목·교수별 분석 · 적중 분석(HIT) · 교수 프로필(PROF) → 3Q 사이트 '2026 출제'(JBL_UNFREEZE=1 — 결정 3)
- [ ] P2 4Q 과목마다: new_subject → JB 분해 → TREND → 정리본(26 본문 / 없으면 25 임시) → annot·tables → 검토 → 예상·N제 → 검사 → 과목마다 중간 배포
- [ ] P3 26 강의가 나올 때마다 전면 갱신(25 무관 내용 지움) → 예상·N제 → 배포

## 받을 자료(사용자에게 보낸 순서)
1. 4Q 과목표(과목명·교수·강의 제목·주차 · 3Q와 이어지는 과목) 2. 2026 3Q 실제 기출 3. 4Q JB(판본 전부 · `20YY 4Q <과목> JB.pdf`) 4. 26 강의자료+필기 5. 25 강의자료+필기(26이 없는 강의 · 교과서) 6. 학기 중 새 26 강의

## 재개 메모
- 3Q 기준 회귀: scratchpad worktree base3q(3q-final) — `work/_tmp/base_ux_all.log` · 새 코드 회귀는 기준이 끝난 뒤 같은 명령(JBL_HTTP=1 ux_all)
- 3Q 기준(3q-final · 이 컨테이너 — work/ 없음)에서 155개 중 37개 이미 실패: ct · fakegist · fmt_cases · kt · legacy_restore · legacy_restore_107 · ux10_num5 · ux11_fix · ux2_auto · ux2_device · ux2_jblock · ux2_jbq · ux2_keys · ux2_learn · ux2_sum_mig · ux2_tables · ux3_compat · ux3_fixes · ux3_keybox · ux3_keylines · ux3_rest · ux3_restui · ux3_tables · ux3_timer · ux4_calm · ux4_nav · ux4_top · ux4c_fix1 · ux4e_names · ux4f_O · ux_u15 · ux_u17 · ux_u18 · ux_u19 · ux_u21 · ux_u27 · ux_u30 — 새 코드는 이 목록과 같아야 함(실패 줄도 견줌)
- 시험 사이트 미리 보기: `.venv/bin/python tools/rehub.py --site work/_tmp/qsite`(4q = 뿌리 · 3q = 3q/)
