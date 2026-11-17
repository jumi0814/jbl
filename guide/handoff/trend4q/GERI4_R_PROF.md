# R_GERI4 — GERI4(노인치과학 4Q) 교수 프로필 담당 보고 (11-16)

맡은 범위: guide/prof/{이용무(새로 — GERI4 PER 26 · ESTH4 PER 25 · IMPL4 PROF_LEC 줄)·곽재영(새로 — GERI4 PRO · ESTH4 RPD)·임영준(이어)·김성민(새로)·류인철(새로 — 전임 tier B)}.md · 보고 이 파일. (조영단·이재일·명훈은 쓰지 않음)
단계: 0 입력 준비(dump_review GERI4·ESTH4·IMPL4 낡았으면 · fmt_audit GERI4·ESTH4·IMPL4 · R_JB/V_JB 읽기 · JB 원문 멘트) → 1 이용무 → 2 곽재영 → 3 임영준(이어) → 4 김성민 → 5 류인철 → 6 검사(대조 수·불확실) → 끝.

## 진행
- [x] 0 입력: questions.md·qids.json이 팩(23:16~23:17)보다 낡아 `dump_review.py` GERI4(62)·ESTH4(50)·IMPL4(42) 다시 · `fmt_audit.py` 셋 → scratchpad GERI4PROF_fmt_{GERI4,ESTH4,IMPL4}.md(11-16 분류기 · PASS · GERI4 의심 10 · ESTH4 14 · IMPL4 4) · ANAT(3Q 김성민 칸)은 guide 밖 work/_tmp/fmt26/ANAT.md 46행 '김성민 20 서 2' + `JBL_Q=3q` 셈 · R_JB_GERI4·V_JB_GERI4·R_JB_ESTH4 읽음 · JB 원문(work/jb/GERI4_2023·ESTH4_2023~2025) 멘트·해설 원문 대조 · 강의자료 글층 grep(GERI4 PER5·PER·DEN·PRO · ESTH4 PER·RPD) · 26 GERI4 PER 필기 = 25와 다른 쪽 21장 차이 영역을 잘라 한 장으로 봄(scratchpad GERI4PROF_per26_0.jpg — '시험' 글 0) · ESTH4 PER p.1(필기 해 색)·p.26(멜라닌 '*****시험') 쪽 이미지 확인.
- 셈 규칙: 교수 = 팩 data-yp(YEAR_PROF·YEAR_PROF_Q — 빠진 해 = '-' 근거 없음 · 셈 밖) · 짤/탈 = trend.analyze(괄호에 더 이른 해 = 짤 · COVER 이하 첫 해 = 기준선) — scratchpad GERI4PROF_cnt.py.
- fmt_audit 1절 교수 칸 ≠ YEAR_PROF(1절은 빠진 해를 카드 교수로 채움): GERI4 이용무 19 4 · 곽재영 19 1 · 임영준 19 1 · 류인철 19 3(모두 '-') · ESTH4 곽재영 20 2(P10·P11 RPD 2020 '-') · IMPL4 이용무 21 1(PERI 2021 '-') → 프로필은 YEAR_PROF 해만.
- [x] 1 이용무(새로) — guide/prof/이용무.md · 대조: GERI4 PER 카드-해 35 = YEAR_PROF PER 20~24(data-yp) 35/35 · fmt_audit GERI4 1절 이용무 24~20 = 6·4·10·8·7(같음 · 19 4는 '-' 셈 밖) · ESTH4 PER 23 = YEAR_PROF PER 20~24 23/23 · fmt_audit ESTH4 이용무 3·3·4·9·4(같음) · IMPL4 1 = YEAR_PROF_Q P04 {2019} 1/1(fmt_audit 21 1은 '-' 셈 밖) · 짤/탈 = trend.analyze 규칙 스크립트 셈 · 멘트 원문 = work/jb 글과 대조.
  - 불확실 칸: §3 ESTH4 ★(옛 칸 짤)·23년 멘트 '전부 2회 이상' ↔ 카드 탈 · GERI4 P07·P08 괄호 해 · 20 칸 '21년도 n번과 동일' · P06 2020 교수 · §4 1~2개 칸 전부 · §5 신호 전부(1/1) · P17 출처 · ESTH4 쪽 = JB 참고 파일 쪽 · 2025 JB 없음 · 26 ESTH4 담당.
- [x] 2 곽재영(새로) — guide/prof/곽재영.md · 대조: GERI4 PRO 카드-해 19 = YEAR_PROF PRO 20~24 19/19 · fmt_audit GERI4 곽재영 24~20 = 4·4·3·2·6(같음 · 19 1 '-' 셈 밖) · ESTH4 RPD 16 = YEAR_PROF RPD 21~24 16/16 · fmt_audit ESTH4 곽재영 5·3·4·4(같음 · 20 2 = P10·P11 '-' 셈 밖) · 쪽 = JB 참고 + 25 덱 글 검색(PRO p.4·7·14·18~21 · RPD p.3·7·9·13·18·20-29).
  - 불확실 칸: R01 21·R02 22·23 범위 괄호만 · R06 출제 교수(D04와 같은 내용) · §4 1~2개 칸 전부 · §5 신호 전부 · ESTH4 2020 '-'·2022 근거 약함 · 2025 JB 없음 · 26 담당.
- [x] 3 임영준(이어 씀) — guide/prof/임영준.md 머리·1·2·3·4·5·8·9절에 GERI4 줄(모두 '(11-16 GERI4)' 꼬리 · 6·7절 = 3Q IMPL 그대로) · 대조: GERI4 DEN 카드-해 7 = YEAR_PROF DEN 20·21·22·24 7/7 · fmt_audit GERI4 임영준 24·22·21·20 = 2·2·2·1(같음 · 19 1 '-' 셈 밖) · git diff '-' 줄 = 머리 1 · 1절 4Q 줄 1(둘 다 꼬리만 더함 — 옛 글 그대로) · 기존 IMPL 수 손대지 않음.
  - 불확실 칸: GERI4 칸 전부(7문항) · 23 칸 문항 없음 이유 · D04 출제 교수 · D01~D04 형식(목록) · 26 담당 · 2025 JB 없음.
- [x] 4 김성민(새로) — guide/prof/김성민.md · 대조: GERI4 OSC 카드-해 20 = YEAR_PROF OSC(24·23·22·21·20·18·17·14·12·11) 20/20 · fmt_audit GERI4 1절 김성민 24~11 = 2·3·2·2·1·2·3·2·1·2(같음) · ANAT(3Q) 4 = YEAR_PROF_Q U23·U24 {2020·2019} 4/4 · fmt26/ANAT.md 46행 '김성민 20 서 2'(19는 그 표에 없음 — JBL_Q=3q 셈 2) · 25 자료 1쪽 원문 = work/GERI4/mat/251218_…/t/1.txt 글 그대로.
  - 불확실 칸: §3 11~18 괄호 해(연도/학번) · §4 탈 1(1문항) · §5 예고 적중 수 · 2025 출제 · ANAT 칸 전부 · 26 담당 · OSC 쪽(슬라이드 없음).
- [x] 5 류인철(새로) — guide/prof/류인철.md · 대조: GERI4 카드-해 6 = YEAR_PROF SYS 21·20 5(L01~L04) + YEAR_PROF_Q P06 {2020} 1 = 6/6 · fmt_audit GERI4 1절 류인철 21·20 = 3·3(같음 · 19 3 '-' 셈 밖) · 26 SYS·PER 덱 글 검색(L01 축 = SYS 당뇨·심혈관 쪽 · L03 축 = PER p.9 · L04 낱말 없음).
  - 불확실 칸: 전부(6문항) · P06 2020 교수 · 19 괄호 의존 짤 · 쪽 근거 없음(강의 자료 없음) · L02 3Q 범위.
- [x] 6 검사 — 5파일 모두 '## 1.'~'## 9.' 9절 · NFC(파일 이름·글) · 답 사실 글 훑어 뺌(곽재영 attachment 이름 3개 · 김성민 C01 해설 요일 줄 — 답 내용이라 지움) · 6·7절: 새 4파일 '없음(3Q 출제 없음)' · 임영준 6·7절(26 3Q IMPL — HIT_IMPL 표와 같은 수) 손대지 않음 · 임영준 git diff '-' 2줄(머리·1절 4Q 줄 — 꼬리만 더함).

## 끝 — 교수마다 대조 수 · 불확실 칸
| 교수 | 파일 | 대조(카드-해 = YEAR_PROF·YEAR_PROF_Q) | 형식 근거 | 불확실 칸 |
|---|---|---|---|---|
| 이용무 | guide/prof/이용무.md(새로) | GERI4 PER 35/35 · ESTH4 PER 23/23 · IMPL4 PERI 1/1(P04 2019) = 59 | fmt_audit GERI4·ESTH4·IMPL4 1절(19·21 '-' 칸 셈 밖) | ESTH4 ★ 옛 칸 짤·23년 멘트 '전부 2회 이상' ↔ 카드 탈 · GERI4 P07·P08 괄호 해 · 20 칸 '21년도 n번과 동일' · P06 2020 교수 · P17 출처 · ESTH4 쪽 = 참고 파일 쪽 · §4·§5 1~2개 칸 · 2025 JB 없음 · 26 ESTH4 담당 |
| 곽재영 | guide/prof/곽재영.md(새로) | GERI4 PRO 19/19 · ESTH4 RPD 16/16 = 35 | fmt_audit GERI4·ESTH4 1절(GERI4 19 · ESTH4 20 '-' 셈 밖) | R01 21·R02 22·23 범위 괄호만 · R06 출제 교수(D04와 같은 내용) · ESTH4 2020 '-'·2022 근거 약함 · R07·R08 쪽 · §4·§5 1~2개 칸 · 26 담당 · 2025 JB 없음 |
| 임영준 | guide/prof/임영준.md(이어 — GERI4 줄) | GERI4 DEN 7/7(IMPL 22 그대로 → 합 29) | fmt_audit GERI4 1절(19 '-' 셈 밖) | GERI4 칸 전부(7문항) · 23 칸 문항 없음 이유 · D04 출제 교수 · D01~D04 형식(목록) · 26 담당 |
| 김성민 | guide/prof/김성민.md(새로) | GERI4 OSC 20/20(20~24 10 + 괄호 해 10) · ANAT(3Q) U23·U24 4/4 = 24 | fmt_audit GERI4 1절 · fmt26/ANAT.md 46행 | 11~18 괄호 해(연도/학번) · 탈 1 · 예고 적중 수 · 2025 출제(25 수업 2문항) · ANAT 전부 · OSC 쪽(슬라이드 없음) · 26 담당 |
| 류인철 | guide/prof/류인철.md(새로) | GERI4 SYS 5 + P06 2020 1 = 6/6 | fmt_audit GERI4 1절(19 '-' 셈 밖) | 전부(6문항) · P06 2020 교수(V_JB ② A/B/C) · 19 괄호 의존 짤 · 쪽 근거 없음 · L02 3Q 범위 |
- 메인 확인 거리: ① guide/prof/조영단.md 9절 12 = "GERI4 SYS … GERI4 담당이 1~5·8절에 이어 씀"인데 이번 지시는 조영단 = PHARM4 담당 → GERI4 SYS 줄은 이 담당이 쓰지 않음(누가 쓸지 정해야 함) ② TREND_NOTE 문구(c ⑥ 6 — 각 프로필 8절): 이용무(GERI4 '직전 2년 기출 먼저 — 23에 22 문항 4개 그대로 · P06 6년 연속') · 곽재영(GERI4 '24에 23 문항 3개 그대로(Willis·VD)' · ESTH4 '24에 23 문항 2개 그대로') · 임영준(GERI4 '24 D01·D02 · 22 D03·D04 · 24 탈은 바로 옆 짝 개념') · 김성민('24에 23 문항 2개 그대로 · 25 수업에 같은 2문항') ③ ESTH4 ★('21년도까지 두 번 이상 출제') · 23년 멘트('전부 2회 이상') = 카드 기준 탈인 G10·G11·G12(21)·G06(22)·P08(22)이 JB로는 짤 → ESTH4 사이트 짤/탈 판정·TREND에 영향(ESTH4 담당 몫) ④ GERI4 22 수업 '안 다룸'(22학습부 해설) → 22 R01·R03 출제 2/2 — c ⑥ 2 사례 1 ⑤ fmt_of 몫: IMPL4 P04 객관식 ↔ 원문 '빈칸빵' · GERI4 D01~D04·R05·R06·R08 단답 ↔ 목록 · ESTH4 P01·P02·P04·G18 단답 ↔ 목록 ⑥ fmt_audit 1절은 YEAR_PROF '-' 해를 카드 교수로 채움(GERI4 19 · ESTH4 RPD 20 · IMPL4 PERI 21) — 프로필은 YEAR_PROF 해만.
- 쓴 파일: guide/prof/{이용무,곽재영,김성민,류인철}.md(새) · guide/prof/임영준.md(꼬리만 더함) · 이 보고. scratchpad: GERI4PROF_{cnt,q,diffcrop}.py · GERI4PROF_fmt_{GERI4,ESTH4,IMPL4}.md · GERI4PROF_per26_0.jpg · GERI4PROF_임영준_before.md. 빌드·커밋 안 함.

상태: 끝(0~6 완료 · 11-16).
