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
- [x] (11-05) 4Q 과목 10개 등록(new_subject — SID OMS2·CONS4·IMPL4·ANAT4·HINS·GERI4·PHARM4·RAD·OPATH·ESTH4 · 이어지는 과목 = 3Q 색 그대로 · 등록표 검사 'SID+숫자'는 같은 쿼터끼리만) · 빈 팩 빌드(허브에 10과목 '강의자료 대기') · jbx = jb·mat·정식 이름 어느 것이든
- [~] (11-05) P1 받음: 복원 엑셀 6개(1 OMS1·3 ANAT·4 GERI·5 PHARM·6 IMPL·7 ESTH — 2 CONS 없음) → work/3q26(이름·출석번호 뺌) · 과목 담당 6명(guide/handoff/R26_BRIEF.md — tools/<sid>/r26.txt · work/<SID>/hit26/HIT_<SID>.md) · OMS1 예상 판정 = 10-27 전 판(work/3q26/oms1_pred_before1027.txt)
  - [x] 6과목 담당 끝(11-05): r26 = OMS1 25 · ANAT 19 · GERI 18 · PHARM 55 · IMPL 18 · ESTH 28 = 163문항(짤 61·변형 66·탈 36) · 우리 예상이 덮음 149/163 · 상만 109/163 · ESTH N제 이창하 23/25 → 보고 guide/handoff/hit26/ · 배운 것 RULES 14 c ⑥ · '2026 출제' 넣는 법 RULES 13(11-05 무인) · 이름 검사 0(엑셀 이름 열 대조 — 거짓 일치 '…이다 빈칸' 2)
  - [x] (11-05) 교수 프로필 27명 guide/prof/(README 9절 · 연도·교수 대조 어긋남 0 · 담당 보고 guide/handoff/hit26/prof/) — 담당 5명(PROF_A 한정준·서병무·서미현·윤필영·양훈주·박주영·권익재 · B1 조영단·임영준·조준호·김성균·명훈 · B2 백정화·이윤실·김우진·우경미 · C 이우철·금기연·고홍섭·장지희·박지은·한동헌 · D 이창하·안진수·서덕규·이인복·김선영·손호현) — 지시문 work/_tmp/agents/PROF_*.md · 입력 work/3q26/ref_<SID>.md(해별 교수·꼴 포함)·work/_tmp/fmt26
  - **막힘**: 3Q 팩을 다시 빌드하려면 3Q 26판 JB 추출본(work/jb/<SID>_2026)이 필요 — 10-15 클라우드에서만 풀고 cloud-materials에 안 올림 → 사용자에게 26판 JB 7개 다시 요청(4Q JB와 함께) · 받으면: jbx → build4에 r26(2026 출제) 넣기(짤 = 기존 카드 연도 26 + '2026 복원' 판 · 앞면은 JB 판 그대로 / 탈 = 새 카드 Z01…) → JBL_UNFREEZE=1 빌드 → 3Q 회귀 → docs/3q 배포
- [ ] P1 2026 3Q 실제 기출 받기 → 과목·교수별 분석 · 적중 분석(HIT) · 교수 프로필(PROF) → 3Q 사이트 '2026 출제'(JBL_UNFREEZE=1 — 결정 3)
- [ ] P2 4Q 과목마다: new_subject → JB 분해 → TREND → 정리본(26 본문 / 없으면 25 임시) → annot·tables → 검토 → 예상·N제 → 검사 → 과목마다 중간 배포
- [ ] P3 26 강의가 나올 때마다 전면 갱신(25 무관 내용 지움) → 예상·N제 → 배포

## P2 4Q 내용 작업(11-16 — 사용자 '4큐 자료 올렸어 … 순서 및 동시작업 구조를 잘 체계화해서 퀄리티 절대 놓치지 않으면서 … 중간중간 깃허브에도 푸시')
- 받은 것(cloud-materials b7da4228·5a3e1c4f·bcd24516): 10과목 강의자료 약 100파일(26 = OMS2 1·CONS4 2·IMPL4 1·GERI4 2·PHARM4 2·RAD 1 · 나머지 25) · 4Q JB 23·24·25판(ANAT4는 23·24판 · 25판 = 2024년 시험까지 — 2025년 4Q 시험이 든 26판은 아직 없음) · ANAT4 자료 = 교과서 2권(1081·458쪽).
- 사용자 참고: ① PHARM4 조영단 '살균제와 소독제'(3Q PHARM DS) = 25까지 3Q · 26부터 4Q → PHARM4 DS 강의(26 PPT 261105) + 기출 = 3Q PHARM JB 23·24·25판 DS 칸(4Q JB엔 없음 — 판 이름 '<YY>q3') ② 4Q JB의 이윤실 '항불안제' = 2026엔 3Q에서 강의·시험(3Q 사이트 PHARM ANX) → PHARM4에선 문항은 빼지 않고 참고(올해 4Q 범위 아님) 키로만.
- 갱신 전 기준 main = 6b98a604(legacy_restore·fc_carry 비교 — 4Q는 첫 배포라 표시 없음).
- **순서·동시 작업 구조**(동시 담당 2 — 이 컨테이너 CPU 4 · 사용 한도):
  1. **JB 단계**(지금 — Workflow): 과목마다 Q4_JB(guide/handoff/Q4_JB_BRIEF.md — 분해·강의 표·연도별 출제 교수·첫 빌드) → Q4_JBV(Q4_JBV_BRIEF.md — 독립 검수·직접 고침) · 10과목 파이프라인 → 메인: matx SRC·과목노트·빌드·커밋·푸시(작업 브랜치).
  2. **교수 프로필**(PROF — 4Q JB로 새 교수·이어 쓰는 교수) — 3과 나란히.
  3. **과목마다 정리본**(과목 하나씩 Workflow): B2Q 작성(강의마다 · parts) → 메인 몫 담당(merge·build·dump) → 검토 C 1·2·3회차(새 문제 0까지) → F 다듬기(강의마다 F 한 담당) → QA(E) → full_check → **과목마다 배포**.
  4. **예상·N제**(과목마다): T(TREND) → P(강의 묶음) → PA 감사 → FN → FNV → 배포.
  - 과목 차례(무인 결정 — 다르게 원하면 바꿈): 26 자료가 있고 강의 수가 적은 과목부터 — ESTH4·IMPL4·OMS2·GERI4·PHARM4 → CONS4 → HINS → OPATH → RAD → ANAT4(교과서 — 나누기 안 확정 뒤).
- [ ] 1 JB 단계 · [ ] 2 프로필 · [ ] 3 정리본(과목별) · [ ] 4 예상·N제(과목별)
- **JB 단계 결과(11-16 23:40 UTC)**: 10과목 Q4_JB 끝 · 독립 검수 7과목 끝(RAD 2·PHARM4 1(10장)·HINS 1·OPATH 2(I04→I02 합침·D02)·ANAT4 1(18장 줄바꿈)·CONS4 0·OMS2 1(S06↔S02 가리킴 줄) — 보고 work/<SID>/jb/V_JB_<SID>.md) · GERI4·IMPL4·ESTH4 검수는 한도로 멈췄다가 이어 도는 중(Workflow wcvyuwrm4 = wf_872883a8-df5 resume) · 커밋 6fffdf92(WIP).
  - 메인 몫 한 것: matx SRC 10과목(R_JB 2절 줄 · 링크 대조 OK · PHARM4 DS5i = 3Q 자료라 SRC에 없음) · 과목 전용 깨진 글자 `subject.py SYMPUA`(build4가 더함 — HINS U+F02D·📫 → ☞ · OPATH U+100093 → □ · '؀리성' → 박리성 · SPEC JBFIX 절) · check_years 알려진 예외 `KNOWN`(RAD D02 빈칸 번호 (10)·(11)) · 형식 분류기: trend.q_lines가 ans=(답 머리 없는 답 칸 시작)를 앎 + '고르기' — build4가 q['ansat'] · fmt_audit도(ANAT4 의심 3→1 · CONS4 L05 객관식 → 단답형) · 과목노트 HINS·OPATH·ANAT4 보정 · **정리본 작성 중 자리 표시 강의**(카드 하나 'Notes in progress') = lecparse `wip` → check_lec '작성 중 · 검사 안 함' · link_audit ⭐·표·칩·예상 연결 건너뜀(기출 탭 빠짐은 그대로) — JB 먼저 배포용.
  - 사용자 확인으로 모음(무인 — 보수 쪽 그대로): RAD 비슷한 옛 문항 붙은 블록의 칸 해 배지 8장 · M05/M06 합칠지 · FRAC 이름 꼴 · PHARM4 LA05 2021('유사한 문제')·괄호에만 있는 해(SX01·SX05 22 · PG02 23)·3Q JB에만 있는 2023 4Q 구강건조증 칸 · HINS M08 (18,14,11)(해설 속 옛 JB 인용) · OPATH I04 합침·O01 20(21 오타?)·D01/D02 합칠지 · ANAT4 판 키 24(파일 '2024_2025' — 내용은 2025년 JB)·X22/B22·2023 '탈' 칩 · CONS4 이우철 26 = Part1뿐(SFB = 25 요인 2 임시본) · OMS2 O10 20(그 해 출제 아닐 수 있음)·E01·E02 tier C → B?
- **4Q 1차 배포 = JB 먼저(11-17)**: 갱신 전 main = 6b98a604 · full_check(4Q) 통과 — check_lec ✗0(자리 표시 강의 '작성 중 · 검사 안 함') · check_years 0 · link_audit ✗0(⭐ 검사는 작성 중 강의 건너뜀) · check_links 0(PHARM4 3Q JB 판 쪽 목록 = JBPAGES만 — build2) · verify PASS(자동 빈칸·한눈표 답 핵심은 정리본 쓴 강의에서) · tests4 q_* 전부 PASS · **4Q 기준값(첫 배포)**: check_breaks_jb 47(ANAT4 19·ESTH4 24 = 검수 담당이 일부러 한 줄씩 뗀 나열 · OPATH 3·PHARM4 1 = JB 해설 다듬기(D3)에서 볼 것) · fmt_audit 의심 RAD 74·PHARM4 25·OPATH 19·ESTH4 14·HINS 12·GERI4 10·OMS2 7·CONS4 5·IMPL4 4·ANAT4 1(정보) · fc_carry 0/0(옛 ⚡ 없음 — full_check가 실패로 세지 않게 고침) · 허브: 작성 중 강의는 '시작하기'가 기출 탭으로(resumeTarget).
- **재개 메모(11-17 00:00 UTC)**: 4Q 1차 배포(JB 먼저) = main 8b505400(실제 주소 확인 — PHARM4 DS 기출 31장 · 콘솔 오류 0 · 404 0) · 사용자 11-17 '모든 결정 권한 … 꼭 필요한 것만 마지막 순간에' → 무인 결정 그대로 · 도는 Workflow: ① PROF→TREND 6과목(OMS2·PHARM4·CONS4·HINS·OPATH·RAD — wkmexcg1z = wf_21e80431-dd1) ② PROF→TREND 4과목(GERI4·IMPL4·ESTH4·ANAT4 — wh1szd35r = wf_2a36553b-960 · PROF 모두 먼저) ③ **정리본 1묶음 = 26 강의 9**(OMS2 AES · PHARM4 DS·SED · GERI4 SYS·PER · IMPL4 AUG · CONS4 IRR·SFA · RAD TRL) + 올해 강의 없는 키(OMS2 CMP·FG·RHN·LOAD · PHARM4 ANX·XE · IMPL4 PAST · RAD FRAC) — wkap9tifp = wf_9b907993-044(과목마다: 통합 prep → 작성 → 검토 3회(+확인 2) → F → QA → 고침 → merge · 통합 담당 = guide/handoff/Q4_MAIN_BRIEF.md). 끝나면: TREND '메인 몫'을 subject.py에 · TREND를 guide/handoff/trend4q/로 복사 · 정리본 1묶음 full_check → 2차 배포 → 다음 묶음(25 임시본 — 과목 하나씩).
- **순서 다시 정함(11-16 23:40 — 무인 결정 · 사용 한도 = 5시간에 무거운 담당 약 20명)**:
  1. JB 단계 끝 → **4Q 1차 배포 = JB 먼저**(정리본 자리 표시 '작성 중 — 기출 탭부터' · 10과목 JB·연도·교수·앞면 · full_check 통과 뒤).
  2. 과목마다 PROF(그 과목 교수 프로필 — 교수 하나 = 파일 하나 · 여러 과목 교수는 한 과목 담당만) → T(TREND) — Q4_RULES_BRIEF 6 순서(TREND → 정리본).
  3. 정리본(과목 하나씩 Workflow · 26 자료 강의 먼저): **26 강의(가)** = 작성 → 검토 3회(+확인 최대 2) → F → QA → 배포 · **25 임시본(나)** = 작성 → 검토 2회(+확인 1) — F·QA는 26이 와서 전면으로 다시 쓸 때(임시본은 1~5주 안에 26으로 다시 씀 — 한도를 26 최종본·JB 해설에 모음 · JB 해설(annot)은 26 때 그대로 이어 씀) · 올해 강의 없는 키 = 과목마다 한 담당(안내 카드 하나 + ⭐ + annot).
  4. 예상·N제(과목마다 P → PA → FN → FNV).

## 전면 점검·개선(11-10 시작 — 사용자 '자료를 주기 전에 … 모든 방면에서 … 업데이트' · 계획·보고 guide/handoff/upg1110/)
- 방법: 허브 = tools/cons/shell.html **한 번에 한 담당**(긴 줄이라 합치기 충돌) → sync_common → rehub → 3Q 스테이징 회귀(JBL_Q=3q · rehub --q 3q --stage) + tests4 → 묶음마다 커밋·배포 · shell을 안 건드리는 일(build4·테스트 도구·스킬 문서)은 나란히
- [x] (11-12 가벼운 판 · 보고 DONE_W0.md — q_pos 105경우 PASS · q_crawl 948화면 PASS · STATUS.json 35줄(helper 1·retired 20·local 10·bug? 4) · 렉 전 기준 수치 · 전체 ux_all·full_check는 끝에 메인이) W0 안전망: tests4/qsite 시험용 사이트(4Q 정체성 + 3Q 팩) · tools/tests/STATUS.json(기준 실패 37 정리) · q_ident 린트 넓히기 · 성능 기준
- [x] (11-10 배포 1 — main c37b69a8) W1 빈 과목(isStub·build4 stub)·그림 다시 받기(needImages)·이동(↩ y·검색·없는 화면 주소·라벨 통일) → 배포 1
- [x] (11-11 배포 4와 함께 · 보고 DONE_W2.md — 메인 몫: TREND·P·FN 지시문에 HIT_<3Q 과목> 채우기 · subject.py TREND_NOTE '직전 2년 기출 먼저' · 사용자 확인 12건은 끝 보고) W2 4Q 규칙·스킬(적중 분석 후보 20여 줄 → RULES 14 c ⑥ · 상 비율 충돌 · AGENTS T·P·FN·PA·Q4_RULES_BRIEF · 옛 배치 · check_lec ★·줄바꿈)
- [x] (11-11 배포 4 · 보고 DONE_W3_허브.md·DONE_빌드.md — 허브 imgUrl 한 곳 · 파일 다시 받기·자리 표시 · 묶음(3Q) 비움 + fetch · 넘버링 그림 lecFill·lecWait) W3 4Q 그림 파일(build4 imgf·img_lock · 허브 그림 주소 한 곳 · 묶음 방식 메모리 비움) → 배포 2
- [x] (11-11 배포 2 · 보고 DONE_W4.md — 남은 다듬기 2개는 W5 담당 0번: 잠든 시간 알림은 ✕·되돌리기까지 남김 · 되돌리기 = 세션도 이어 감) W4 공부 시간(잠든 시간 자동 빼기 + 되돌리기 · 시계 뒤로 · cls · tedit 누적 · 쿼터 공용 채널 · qimport2) → 배포 3
- [x] (11-11 배포 3 · 보고 DONE_W5.md — 메인 결정: 넘버링을 되돌리면 u를 지금으로(되돌린 판이 동기화에서 이기게 — W3 허브 담당 0번) · dj 표시는 데이터만 · 3Q 허브는 끝에 한 번) W5 기록(저장 공간 안내·밀린 쓰기 · 넘버링 되돌리기·old 저장소 · 복습 채점 동기화 · 403/429 · jbMove → 넘버링 · pick 문맥 · ★ 수) → 배포 4
- [x] W6 렉(11-13 — 1 표 맞춤 줄 TWQ·2 그리기 뒤 일·3 팩 이어 받기 됨 · **2단계 content-visibility는 안 함**(따로 한 묶음 — 사용자에게 물음) · 과목 비교표 처음 830 → 493ms·다시 628 → 298ms · 보고 upg1110/DONE_W6.md) · 원래 계획: (표 맞춤 읽기/쓰기 분리·보이는 표 먼저·기억 · 그리기 뒤 일 미루기 · 2단계 높이 기억 + content-visibility는 스위치 뒤) → 배포 5
- [x] W7 디자인 남은 것 + 색·위계·여백 리뉴얼 v3.3(11-13 — 배포 6 = 2f583654 · 보고 upg1110/DONE_W7.md · 전체 회귀에서 걸린 교수 이름 굵기·정리본 칩 44px은 되돌림)
- [x] 끝: 3Q 보관 허브 다시 냄(`JBL_UNFREEZE=1 rehub.py --q 3q` + 3q/num · 진짜 폴더 verify·넘버링·동기화·기록 테스트 PASS) · 전체 ux_all PASS 121·SKIP 30·알려진 실패 1(ux_u18)
- [ ] 끝: JBL_UNFREEZE=1 rehub --q 3q(3Q 허브에도) · 전체 ux_all · 보고(내가 정한 것·기기 확인 부탁)
- **재개 메모(11-10 12:40 UTC)**: 담당 넷이 사용량 한도로 멈춤(11:00 UTC 풀림 · 사용자 "초기화되었습니다 … 계속 진행") → 작업분 WIP 커밋(메인 5e5fc213 문서·983e9740 shell(배포 금지 — 사본·docs 미반영 · 고치기 전 기준 4127b1ce) · worktree 브랜치 빌드 f0e4f6c5 `.claude/worktrees/agent-ae5c8cca242a40c1a` · 테스트 273be7ec `.claude/worktrees/agent-ac5912c51bbd11a94` · 패치 보관 guide/handoff/upg1110/wip/) → **한 번에 담당 둘까지**: ① 허브 W1 이어서 + 빌드 이어서(지금) ② 테스트(W0) 이어서 + 문서(W2) 이어서(남음: QA·AGENTS·Q4_RULES_BRIEF·묵은 줄·사용자 확인 목록) ③ 그 뒤 허브 묶음 하나씩(UPG_H2~H6). 담당이 멈추면 새 담당에게 같은 지시문 + '앞 담당이 한도로 멈춤 — 보고·diff로 확인하고 남은 것만'(worktree 담당은 isolation 없이 그 worktree 경로에서 일하게).
- **재개 메모 2(11-10 23:20 UTC)**: 두 번째 한도(16:00 UTC 풀림) · 사용자 "위 플랜 그대로 하되 추가적으로 디자인 … 색 배치 및 조화 … 리뉴얼 … 쭉 작업" → W7 = 디자인 리뉴얼로 넓힘(지시문 UPG_H6 끝 '넓힘') · **담당은 한 번에 하나**(허브 줄기) + 합치기·검사·배포는 메인이 직접 · 빌드 쪽 끝(브랜치 worktree-agent-ae5c8cca242a40c1a 0bd243fa — 패치 wip/B_빌드.patch · W1 허브 끝나면 합침 → sync_common → 4Q 10과목 build4 → rehub → verify·check_links·q_imgbuild) · W1 허브 = 코드 끝·검사 중(셋째 담당) · 테스트 안전망은 가벼운 것만(worktree agent-ac5912c51bbd11a94 273be7ec — 시험용 사이트·린트·q_crawl 일부) · 순서: W1 배포 → W4 → W5 → W3 허브 → W2 남은 문서 → W6 → W7
- 새 기능 없음(사용자 '시험직전모드는 필요없어') · 자료가 먼저 오면 내용 작업이 먼저(허브 묶음은 나란히)

## 받을 자료(사용자에게 보낸 순서)
1. 4Q 과목표(과목명·교수·강의 제목·주차 · 3Q와 이어지는 과목) 2. 2026 3Q 실제 기출 3. 4Q JB(판본 전부 · `20YY 4Q <과목> JB.pdf`) 4. 26 강의자료+필기 5. 25 강의자료+필기(26이 없는 강의 · 교과서) 6. 학기 중 새 26 강의

- **재개 메모 5(11-11 10:55 UTC)**: 배포 4(W3 허브 + W2 문서) 끝 · 다음 = W0 가벼운 안전망(worktree 브랜치 worktree-agent-ac5912c51bbd11a94 273be7ec를 합쳐 이어서 — q_pos가 W6의 안전판) → W6 렉(agents/UPG_H5_렉.md) → W7 디자인·색 리뉴얼(agents/UPG_H6_디자인.md) → 3Q 허브 다시 내기(JBL_UNFREEZE=1 rehub --q 3q + num) · ux_all 전체 · 끝 보고 · 담당은 한 번에 하나.

- **재개 메모 6(11-12 23:55 UTC)**: W0 끝 · 다음 = W6 렉 담당(agents/UPG_H5_렉.md — 단계마다 지킴이) → 검사·배포 5 → W7 디자인·색 리뉴얼 → 배포 6 → 3Q 허브 다시 내기 · ux_all 전체 · 끝 보고.

## 재개 메모
- 3Q 기준 회귀: scratchpad worktree base3q(3q-final) — `work/_tmp/base_ux_all.log` · 새 코드 회귀는 기준이 끝난 뒤 같은 명령(JBL_HTTP=1 ux_all)
- 3Q 기준(3q-final · 이 컨테이너 — work/ 없음)에서 155개 중 37개 이미 실패: ct · fakegist · fmt_cases · kt · legacy_restore · legacy_restore_107 · ux10_num5 · ux11_fix · ux2_auto · ux2_device · ux2_jblock · ux2_jbq · ux2_keys · ux2_learn · ux2_sum_mig · ux2_tables · ux3_compat · ux3_fixes · ux3_keybox · ux3_keylines · ux3_rest · ux3_restui · ux3_tables · ux3_timer · ux4_calm · ux4_nav · ux4_top · ux4c_fix1 · ux4e_names · ux4f_O · ux_u15 · ux_u17 · ux_u18 · ux_u19 · ux_u21 · ux_u27 · ux_u30 — 새 코드는 이 목록과 같아야 함(실패 줄도 견줌)
- 시험 사이트 미리 보기: `.venv/bin/python tools/rehub.py --site work/_tmp/qsite`(4q = 뿌리 · 3q = 3q/)
- **재개 메모 7(11-13 06:20 UTC)**: W6 끝·배포 5 · 다음 = W7 디자인·색 리뉴얼 담당 하나(agents/UPG_H6_디자인.md + 11-13 덧붙임 — v3_palette FAIL 1 `.lbm` · audit_design 4Q에서 죽음도 같이) → 검사(q_pos·q_crawl·3Q 스테이징 full_check) → 배포 6 → `JBL_UNFREEZE=1 rehub.py --q 3q`(+ 3Q num) · 전체 ux_all(3Q 스테이징 — STATUS) · full_check · 끝 보고(사용자 확인 목록 DONE_W2 12건 + W0·W6 결정 + 기기 확인 + 2단계 할지).
- **재개 메모 8(11-13 11:40 UTC)**: W7 담당은 고침·문서를 끝내고 마지막 보고 줄 앞에서 한도로 멈춤 → 메인이 검사(다시 띄우지 않음): sync·rehub·build_num `--check` OK · v3_palette PASS · 4Q full_check 통과 · q_pos '예상 ③ 새로고침' 흔들림 = 전부터 있던 것(렉 고침 전 3/12 · W6 4/12 · W7 2/12 → q_pos `BLIP` KNOWN) · 색 모으기 스크립트 `tools/design/snap_*.py` · 스킬 AGENTS H·QA 70에 v3.3. 3Q full_check가 도는 중에 컨테이너가 다시 시작돼 **남은 것만 다시**: `work/_tmp/end_w7.out`(rehub --stage → q_sync·q_timer → 전체 ux_all(STATUS) → audit_design 3Q · 끝 줄 END_DONE) → 결과를 DONE_W7 '메인 검사'의 '3Q 회귀'에 적기 → 커밋 → **배포 6** → 연기 확인 → 전·후 화면을 사용자에게 → `JBL_UNFREEZE=1 rehub.py --q 3q`(+ 3q/num) → `JBL_Q=3q JBL_HUB_DIR=docs/3q tools/verify.py` → 배포 7 → 끝 보고(사용자 확인 목록 = DONE_W2 12줄 + W0·W6·W7 '정할 것' + 기기 확인).
- **재개 메모 9(11-13 14:40 UTC)**: 전면 점검 W0~W7 + 끝 단계 모두 끝(배포 7 = 3Q 반영). 남은 것 = 사용자 답을 기다리는 것뿐: ① 3Q 26판 JB 7개 + 보존 복원 xlsx → 3Q '2026 출제'(task 11) ② 4Q JB·강의자료 → 내용 작업(스킬 jbl-update 4Q 판) ③ 끝 보고의 '확인 부탁' 목록(DONE_W2 12줄 · 2단계 렉(content-visibility) 할지 · 그림빵 가림막 · 집중 모드 합계 숨김 · 820 긴 제목 · 새로고침 직후 흔들림 고칠지 · 기기 확인).
