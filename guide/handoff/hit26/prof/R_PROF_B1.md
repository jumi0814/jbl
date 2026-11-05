# R_PROF_B1 — 교수 프로필 담당 B1 보고 (11-05 · AGENTS PROF · 지시문 work/_tmp/agents/PROF_B1.md)

- 맡은 교수: 조영단 · 임영준 · 조준호 · 김성균 · 명훈 → `guide/prof/<이름>.md` 5개(형식 guide/prof/README.md 절 제목·순서 그대로 · NFC)
- 입력(이 컨테이너 바꿈): JB = `work/3q26/ref_<SID>.md`(3Q 배포본 카드 — data-yp 해별 교수) + `tools/<sid>/annot.txt` · 교수×해 = `tools/<sid>/subject.py` YEAR_PROF·YEAR_PROF_Q·PROF_NOTE·MENT_PROF·MENT_ALL·TREND_NOTE · 형식 = `work/_tmp/fmt26/<SID>.md`(fmt_audit) · 26 실제 = `guide/handoff/hit26/HIT_<SID>.md` + `tools/<sid>/r26.txt` · 지난 경향 = `guide/handoff/trend26/TREND_<SID>.md`(+ yearprof_R_<SID>.md) · 수업 신호 = 원고 `tools/<sid>/lec_*.txt`(`!`·`@UPD`·`P:`·`{e:}`)
- 교수 찾기(`grep -n '<이름>' tools/*/subject.py`): 조영단 = IMPL HIS · PHARM DS / 임영준 = IMPL BIO / 조준호 = IMPL PART / 김성균 = IMPL PRO / 명훈 = IMPL PATH · ANAT NECK · GERI SURG(26 새) — OMS1·CONS·ESTH·4Q 과목(subject.py 빈 틀)엔 없음
- 없는 입력: work/<SID>/review/questions.md(→ ref로 대신) · 4Q JB(work/jb 없음) · 4Q 과목표(UPD_4Q_진행 '받을 자료 1' — 아직)
- 대조 스크립트(scratchpad): ref 카드 data-yp × subject.py YEAR_PROF(·_Q) 해마다 대조 · ref 꼴·연도 × fmt_audit 2절 문항 표 대조

## 교수마다

### 조영단 — guide/prof/조영단.md (끝)
- 과목: IMPL HIS(23~26) · PHARM DS(20~24 · 26 3Q 범위 아님)
- 연도·교수 대조(ref data-yp × subject.py YEAR_PROF): IMPL 카드 9 · 출현 12 → YEAR_PROF HIS 일치 12/12 / PHARM 카드 31 · 출현 44 → YEAR_PROF DS 일치 42 · 근거 없음 2(2019 DS05·DS10 — YEAR_PROF 뺀 해 → 셈 밖) · 다른 교수로 잡힌 해 0
- 형식 칸 대조(fmt_audit): IMPL 1절 '조영단 23·24·25' 칸 = 이 파일 §2 3줄 같은 수 · 카드 9/9 형식·연도 일치(2절) / PHARM DS = 등급 C라 1절 표 밖 → 2절 문항 표 형식 열 31/31·연도 31/31 일치로 셈
- 26 3Q 절 = HIT_IMPL 1절 Z07~Z11 · 2절 '조영단 5 · 적중 5/5 · 상만 5/5 · 상+같은 꼴 3/5'와 같은 수 · PHARM 26 = 0(r26 PHARM에 조영단 0)
- 불확실 칸: §2 PHARM 2025 '기록 없음' · §2 PHARM T/F(20만)·빈칸(21만) · §4 횟수 1~2 줄 전부 · §5 IMPL p.43 · 26 빨간 상자 · PHARM 필기 해 미상 2줄 · §9 HM 2020 출제자(조영단 가능성 — 16출현 넣지 않음) · IMPL 22 문항 0 · 25 13번 미복원 · DS10·DS14

### 임영준 — guide/prof/임영준.md (끝)
- 과목: IMPL BIO(20~26 · 다른 과목 0)
- 연도·교수 대조: 카드 10 · 출현 19 → YEAR_PROF BIO 일치 9(23~25) · 근거 없음 10(20~22 — YEAR_PROF 뺀 해, ref 해별 교수 = 화면 q['prof'] 임영준) · 다른 교수로 잡힌 해 0 → 파일엔 20~22를 넣되 줄마다 'YEAR_PROF 뺀 해' 표시 · 합을 두 줄(20~26 · 23~26)로
- 형식 칸 대조(fmt_audit IMPL 1절 '임영준 25~20' 6칸) = §2 6줄 같은 수 · 2절 카드 10/10 형식·연도 일치
- 26 3Q 절 = HIT_IMPL 1절 Z01~Z03 · 2절 '임영준 3 · 적중 3/3 · 상만 3/3 · 상+같은 꼴 0/3' 같은 수
- 불확실 칸: §4 모든 줄(1~2문항) · §5 모든 줄(26 한 해 · 필기 해 미상) · §9 20~22 출제자 · T04 형식(단답 ⚑ vs 나열) · 24 미복원 4·5·9 교수 미상

### 조준호 — guide/prof/조준호.md (끝)
- 과목: IMPL PART(25·26 · 다른 과목 0)
- 연도·교수 대조: 카드 3 · 출현 3 → YEAR_PROF PART 2025 조준호 일치 3/3 · 같은 강의 23·24 = 이재현(YEAR_PROF — Q08·R11은 이 파일 셈 밖, '옛 교수 꼴' 참고 줄만)
- 형식 칸 대조: fmt_audit IMPL 1절 '조준호 25 단답 1 · 서술 2' = §2 같은 수 · 2절 P08·P09·P10 형식·연도 일치
- 26 3Q 절 = HIT_IMPL 1절 Z04~Z06 · 2절 '조준호 3 · 적중 3/3 · 상만 1/3' 같은 수
- 불확실 칸: 거의 전부(2년 6문항) — §3 2회 이상 축 · §4 모든 줄 · §5 부정 신호·26 강조 · §9 P08 복원 불충분 · P10 형식 의심 · 25 JB 답이 26 PPT 근거인 점

### 김성균 — guide/prof/김성균.md (끝)
- 과목: IMPL PRO(20~25 · 26은 r26 prof=김성균 — 수업 박지만 · 다른 과목 0)
- 연도·교수 대조: 카드 5 · 출현 9 → YEAR_PROF PRO 일치 4(2023 3 · 2025 1) · 근거 없음 5(20~22 — YEAR_PROF 뺀 해, 화면 q['prof'] 김성균) · 다른 교수로 잡힌 해 0 · 2024 출현 0
- 형식 칸 대조: fmt_audit IMPL 1절 '김성균 25·23·22·21·20' 5칸 = §2 같은 수 · 2절 카드 5/5 형식·연도 일치
- 26 3Q 절 = HIT_IMPL 1절 Z18 · 2절 '김성균 1 · 적중 1/1 · 상만 1/1' 같은 수
- 불확실 칸: 거의 전부(해마다 1~3문항) — §4 모든 줄 · §5 모든 줄 · §9 20~22 출제자 · 26 Z18 출제 교수(김성균/박지만) · 24 미복원 4·5 자리 · 형식 분류 차이(S03 서술 ↔ Z18 넘버링)

### 명훈 — guide/prof/명훈.md (끝)
- 과목: ANAT NECK(17·18) · IMPL PATH(23) · GERI SURG(26 새 · JB 0)
- 연도·교수 대조: ANAT 카드 4 · 출현 4 → YEAR_PROF NECK 일치 4/4 / IMPL 카드 1(R12) · 출현 1 → YEAR_PROF PATH 2023 일치 1/1 · 수업 공개 R13·R14(연도 없음 · kind=예고)는 셈 밖 / GERI YEAR_PROF·카드 0
- 형식 칸 대조: fmt_audit ANAT 1절 '명훈 18 단답 1·서술 2 · 17 단답 1' = §2 같은 수 · IMPL 1절 '명훈 23 객관식 1' = §2 · 2절 카드 5/5 형식·연도 일치
- 26 3Q 절 = HIT_IMPL '명훈 0' · HIT_ANAT 교수 4명(명훈 없음 — r26 머리) · HIT_GERI '한동헌·명훈 복원 0' 같은 수 · 7절 예상 수 = pred.txt 직접 셈(IMPL PATH 15블록 = 상 3·중 9·보관 3 · ANAT NECK 16 = 상 5·중 8·하 2·보관 1 · GERI SURG 14 = 상 1·중 8·하 5)
- 불확실 칸: §3 18 짤/탈(M04 같은 축?) · §4 모든 줄 · §5 부정 신호 · §9 IMPL 22·23 복원 한계 · R15 위치 · 공개 문항 출제 여부 · GERI 복원 대상 · ANAT '짤 경향' 멘트 ↔ 탈 3 · 형식 의심 2(M03·M04) · 24년 멘트 해 · 4Q 담당

## 끝 — 검사 요약
- 쓴 파일: guide/prof/조영단.md · 임영준.md · 조준호.md · 김성균.md · 명훈.md(이름 = subject.py PROF_LEC 글자 · NFC) + 이 보고. 다른 파일 수정·빌드·커밋 없음.
- 연도·교수 대조 합: 카드 63 · 출현 92(IMPL 28 카드 · 44 출현 / PHARM 31 · 44 / ANAT 4 · 4) → YEAR_PROF 일치 75(IMPL 29 · PHARM 42 · ANAT 4) · YEAR_PROF 뺀 해 17(IMPL BIO 20~22 10 · PRO 20~22 5 · PHARM DS 2019 2) · 다른 교수로 잡힌 해 0 · (+ 수업 공개 R13·R14 2 — 연도 없음, 셈 밖)
- 형식 칸: fmt_audit 1절 교수×연도 칸(IMPL 조영단 3 · 임영준 6 · 김성균 5 · 조준호 1 · 명훈 1 / ANAT 명훈 2) 모두 같은 수 · 2절 문항 표 63/63 카드 형식·연도 일치(IMPL 28 · PHARM 31 · ANAT 4)
- 26 3Q 절: HIT 표와 같은 수 — IMPL 임영준 3 · 조준호 3 · 조영단 5 · 김성균 1 · 명훈 0 / ANAT 명훈 0 / GERI 명훈 0(복원 없음) / PHARM 조영단 0(범위 아님)
