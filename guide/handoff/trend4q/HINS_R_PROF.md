# R_HINS — HINS(의료전달체계와 건강보험 4Q) 교수 프로필 담당 보고 (11-16)

맡은 범위(이 파일만 씀): guide/prof/{송영하(새로)·한동헌(이어 씀 — GERI 3Q 줄 그대로 + HINS 4Q 줄)·김현덕(새로 — 옛 출제)·조현재(새로 — 옛 출제 · GERI OHQ 20~23 + HINS INF 19)}.md · 보고 이 파일.
쓰지 않음: 다른 교수 파일(읽기만) · '외래교수'·'이전 교수' = 프로필 없음(아는 교수 파일 9절에 한 줄).
단계: 0 입력 준비(dump_review·fmt_audit 다시 · R_JB/V_JB · questions.md · subject.py YEAR_PROF · RULES 14 c ⑥ · Q4_RULES_BRIEF) → 1 송영하 → 2 한동헌(이어) → 3 김현덕 → 4 조현재 → 5 검사(대조 수 · 불확실 칸) → 끝.

## 진행
- [x] 0-a 팩(docs/packs/HINS.js 23:17)이 review(15:03)보다 새것 → `dump_review.py HINS` 다시(157 문항) · `fmt_audit.py HINS` 다시(11-16 분류기 → work/_tmp/fmt25/HINS.md · 집계 144 · 객 61·T/F 1·빈 52·단 27·서 3 · 의심 12 · 참고 1).
- [x] 0-b 읽음: AGENTS 공통 머리·PROF · guide/prof/README.md · RULES 14 c ⑥ · Q4_RULES_BRIEF · R_JB_HINS·V_JB_HINS · subject.py(YEAR_PROF·YEAR_PROF_Q·PROF_NOTE·MENT_PROF·MENT_ALL) · JB 멘트 원문(work/jb/HINS_2023/1·2.txt · HINS_2024/1.txt · HINS_2025/1·2.txt) · 25 송영하·한동헌 PDF 글층 필기([주석] — 시험·예시·강조) · 기존 guide/prof/한동헌.md · GERI(3Q) 조현재 칸: work/GERI/review/qids.json·annot C01~C16 · TREND_GERI 0·3-3절 · `JBL_Q=3q fmt_audit.py GERI --md <scratchpad>/HINS_PROF_fmtGERI.md`(조현재 행 = fmt26/GERI.md와 같음 — 덮어쓰지 않음).
- [x] 0-c 셈(scratchpad HINS_PROF_q.py · _show.py · _marks2.py): qids.json 카드-해 246 → 출제 연도 기준 교수(YEAR_PROF·YEAR_PROF_Q) = 한동헌 85 · 김현덕 85 · 송영하 39 · 외래교수 28 · '-' 5 · 이전 교수 3 · 조현재 1. fmt25 1절과 대조: 송영하 24 12·23 13·22 13(+X05 C 1 = 14) ✓ · 한동헌 24 15·23 13·22 18·21 16·20 23 ✓ · 김현덕 21 34·20 42(+OHL C 3 = 45)·19 4·18 2 ✓ · 조현재 19 1 ✓. **어긋남 1**: fmt25 1절 '한동헌 18 2·14 1·12 1·10 1'(5회) = YEAR_PROF '-'(근거 없음) — fmt_audit가 강의 교수로 채움 → 프로필 셈에서 뺌(한동헌 9절).
- 발견: 송영하 25 PPT '예시 문제' 슬라이드 8문항(의료법 2 · 보건의료기본법 2 · 지역보건법 2 · 국민건강증진법 2 — MED p.3 Slide 10 · BLAW p.2·p.4·p.6 Slide 21) = JB 8카드(M06·M04·L05·L06·L07·L01·L02·L03 — 22~24 10회) → 8/8 출제.
- [x] 1 송영하(새로) — guide/prof/송영하.md · HINS 34카드(A 33 · C X05) 39회 · 대조: 카드-해 39 = YEAR_PROF(HSYS·INS·MED·BLAW 22~24 · PRAC 23) + YEAR_PROF_Q X05 39/39 · 형식 = fmt25/HINS 1절 송영하 행(24 객8·빈2·단2 · 23 객11·빈2 · 22 객9·빈1·단2·서1) + 2절 X05 객 · JB '(탈)' 표기 23 11/12 · 24 8/8 = 사이트 탈 같음 · 6·7절 '없음(3Q 출제 없음)'.
  - 불확실 칸: 22 단답·서술 판정 4(S07·I09·L07 · 22 칸 멘트 '주관식 3') · 24 M01·L02 단답 판정 · I03 23 꼴 · I09 복원 미흡 · X05 귀속 · 22 PRAC 강의 여부 · 26 자료 없음 → 25 필기·예시 문제 적중 미상. 9절에 '외래교수' 한 줄.
- [x] 2 한동헌(이어 씀) — guide/prof/한동헌.md · 머리 '11-16(HINS 더함)' · 1절 HINS 줄 + GERI4 줄 꼬리 '(11-16 갱신: GERI4 담당 아님)' · 2절 HINS 6행 + 꼴·원문 어긋남·발문·강의 비중·멘트 원문·25 필기 · 3절 HINS 사이트 셈·JB 표기 대조·21 짤 풀·직전 해·짤 꼴·2회 축·옛 담당(조현재) · 4절 표 HINS 6행(탈 23) + 셈·22 이후 8/10·오답 꼴 · 5절 수업 안 함 → 출제 · 25 필기 · 8절 HINS 5줄 · 9절 HINS 5줄 · GERI 3Q 줄·6·7절 그대로(git diff '-' 줄 = 머리·GERI4 줄 2개뿐 — 둘 다 옛 글 앞에 그대로 두고 꼬리만 더함).
  - 대조: HINS 카드-해 85 = YEAR_PROF(BEM·INF·AIDS·QUA 20~24 · HOS 22~24) 85/85 · fmt25/HINS 1절 한동헌 20~24 행 = 2절 HINS 행 같음(18·14·12·10 5회는 '-'라 뺌) · JB '(탈)' 23 4 · 24 1 = 사이트 탈 같음.
  - 불확실 칸: 20 꼴(단답·서술 11 중 9 '(객)') · 단답 5카드 · 20 문항이 이후 0인 까닭 · 25 필기 적중 미상 · '반짤반탈' 표기 3 · 수업 안 함 → 출제(2해만).
- [x] 3 김현덕(새로) — guide/prof/김현덕.md · HINS 67카드(A 64 · C OHL 3) 85회(18~21) · 대조: 카드-해 85 = YEAR_PROF(HSYS·INS·MED·BLAW 20·21 · HSYS·MED 19 · MED 18 · OHL 20) 85/85 · 형식 = fmt25/HINS 1절 김현덕 행(21 빈26·단5·객2·T/F1 · 20 A 42 + 2절 OHL 빈 3 · 19 빈3·단1 · 18 단2) · 짤/탈 = 김현덕 COVER 20 기준(사이트 배지는 송영하 COVER 22라 '기준선' — 9절에 적음) · 9절에 '이전 교수' 한 줄 · 6·7절 '없음(3Q 출제 없음)'.
  - 불확실 칸: 18·19(괄호로만 · 복원 적음) · M08 (18,14,11) 학습부 추정 · 사이트 배지와 짤/탈 셈 다름 · fmt 의심 7 · 21 멘트 '객관식 짤족' 어긋남 · 김현덕 2021 파일 없음 → 4절 쪽은 JB 참고 쪽 번호로만 · 탈 꼴 나누기는 내 판단.
- [x] 4 조현재(새로) — guide/prof/조현재.md · GERI OHQ 15카드 18회(20~23 · tier B) + HINS F05 1회(19) · 대조: GERI 카드-해 18 = GERI YEAR_PROF OHQ 20~23 '조현재' 18/18 · HINS 1 = YEAR_PROF INF 2019 1/1 · 형식 = `JBL_Q=3q fmt_audit.py GERI`(scratchpad HINS_PROF_fmtGERI.md — 11-16 분류기 · fmt26/GERI.md 조현재 행과 같은 수: 23 객4 · 22 객6 · 21 객4 · 20 객3·빈1) + fmt25/HINS F05 단답 · GERI annot v= ok 5·part 3·none 7 · 6·7절 '없음(2026 3Q 출제 없음 — 26 OHQ = 한동헌)'.
  - 불확실 칸: HINS 전부(1문항 · 2019 칸 없음) · 19 조현재 범위 · GERI 3Q JB 원문 없음(멘트는 subject.py 주석·annot N으로만) · C02·C16 선지 미복원 · 탈 꼴 나누기는 내 판단.
- [x] 5 검사 — 대조 합: HINS 카드-해 246 중 이 담당 셈 210(송영하 39 · 한동헌 85 · 김현덕 85 · 조현재 1) = YEAR_PROF·YEAR_PROF_Q 210/210 · 나머지 36 = 외래교수 28(송영하 9절 한 줄) · '-' 5(한동헌 9절) · 이전 교수 3(김현덕 9절 한 줄) · GERI 조현재 18/18 · 형식 칸 = fmt25/HINS 1·2절 행 그대로(어긋남 = 한동헌 '-' 5회 — fmt_audit가 강의 교수로 채움 → 뺌) · JB '(탈)' 표기 = 사이트 탈(송영하 23 11/12·24 8/8 · 한동헌 23 4·24 1) · 4파일 모두 '## 1.'~'## 9.' · NFC · 한동헌 git diff '-' 줄 2(머리·GERI4 줄 — 옛 글 그대로 두고 꼬리만 더함) · 6·7절(GERI 3Q) 손대지 않음.

## 끝 — 교수마다 대조 수 · 불확실 칸
| 교수 | 파일 | 대조(카드-해 = YEAR_PROF) | 형식 근거 | 불확실 칸 |
|---|---|---|---|---|
| 송영하 | guide/prof/송영하.md(새로) | HINS 39/39(A 38 · C X05 1) | fmt25/HINS 1·2절 | 22 단답·서술 판정 4(22 칸 멘트 '주관식 3') · 24 M01·L02 단답 판정 · I03 23 꼴 · I09 복원 미흡 · X05 귀속 · 22 PRAC 강의 여부 · 25 필기·예시 문제 적중 미상(26판 JB 없음) |
| 한동헌 | guide/prof/한동헌.md(이어 — GERI 3Q 줄·6·7절 그대로) | HINS 85/85(+ '-' 5회 뺌) · GERI 줄 그대로 | fmt25/HINS 1·2절 | 20 꼴(단답·서술 11 중 9 '(객)') · 단답 5카드 · 20 문항이 이후 0인 까닭 · 수업 안 함 → 출제(2해) · 25 필기 적중 미상 · '반짤반탈' 3 |
| 김현덕 | guide/prof/김현덕.md(새로 — 옛 출제) | HINS 85/85(A 82 · C OHL 3) | fmt25/HINS 1·2절 | 18·19 괄호로만 · M08 (18,14,11) 추정 · 사이트 배지(송영하 COVER 22)와 셈 다름 · fmt 의심 7 · 21 멘트 '객관식 짤족' 어긋남 · 김현덕 2021 파일 없음 |
| 조현재 | guide/prof/조현재.md(새로 — 옛 출제) | GERI 18/18 + HINS 1/1 | JBL_Q=3q fmt_audit GERI(scratchpad) · fmt25/HINS | HINS 전부(1문항) · 19 범위 · GERI 3Q JB 원문 없음 · C02·C16 선지 미복원 |
- 프로필 없음: '외래교수'(송영하.md 9절 한 줄) · '이전 교수'(김현덕.md 9절 한 줄) · '-'(HINS 한동헌 강의 18·14·12·10 — 한동헌.md 9절).
- 메인 확인 거리: ① 송영하 25 PPT '예시 문제' 8문항이 22~24에 8/8 출제(10회) — TREND·예상에서 '예시 슬라이드 보기·발문 바꾼 판'을 송영하 상 근거로(송영하.md 4·5·8절) ② fmt_audit가 YEAR_PROF '-' 해를 강의 교수로 채움(HINS 한동헌 18·14·12·10 5회) — trend 집계에도 같은지 메인 확인 ③ 김현덕 문항 카드 배지 '기준선'은 강의 교수(송영하) COVER 22 기준 — 출제 연도 기준(김현덕 COVER 20)이면 21 짤 12/탈 22(김현덕.md 3절) ④ HINS 20 '(객)' 표기 9문항이 단답·서술로 판정됨(fmt_of — 한동헌.md 2절).
- 쓴 파일: guide/prof/{송영하,김현덕,조현재}.md(새) · guide/prof/한동헌.md(꼬리만 더함) · 이 보고. 다시 만든 것: work/HINS/review/*(dump_review) · work/_tmp/fmt25/HINS.md(fmt_audit). scratchpad: HINS_PROF_{q,show,marks,marks2,stem,hdh}.py · HINS_PROF_rows.json · HINS_PROF_fmtGERI.md.
