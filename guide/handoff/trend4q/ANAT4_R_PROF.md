# R_ANAT4 — ANAT4(임상두경부해부학 · 4Q) 교수 프로필 담당 보고 (11-16)

맡은 파일: guide/prof/방강미.md · guide/prof/장미숙.md · guide/prof/이승표.md · guide/prof/박영석.md (모두 새로 · 명훈 = IMPL4 담당이라 쓰지 않음)
단계: ① 지시·형식 읽기(AGENTS 공통 머리·PROF · guide/prof/README.md · RULES 14 · Q4_RULES_BRIEF) ② ANAT4 subject.py(YEAR_PROF·PROF_LEC·MENT)·questions.md·fmt_audit·R_JB/V_JB 읽기 ③ 다른 4Q 과목에 같은 교수가 있는지 grep ④ 교수마다 파일 작성(방강미 → 장미숙 → 이승표 → 박영석) ⑤ 대조 수·불확실 칸 기록

## 진행
- ① 읽음: AGENTS 공통 머리·PROF · guide/prof/README.md · RULES 14(a~d · c ⑥) · Q4_RULES_BRIEF · 예시 프로필 송영하·구영(11-16 새로 꼴) · 과목노트_ANAT4.
- ② ANAT4 팩(11-16 23:46)이 questions.md(23:29)보다 새것 → `dump_review.py ANAT4` 다시(28 문항) · `fmt_audit.py ANAT4` 다시(문항 8 · 단답 3 · 넘버링 1 · 서술 4 · 의심 1 B06 — 출제 교수 칸 전부 '?' = 교수 미상) · subject.py YEAR_PROF HN {2023:'-', 2022:'-'} · R_JB/V_JB 읽음 · JB 1쪽 쪽 그림 두 장(24판 1.jpeg · 23판 1.jpeg) 직접 봄 — 수업 표 14줄 = subject.py PROF_NOTE·PROF_LEC와 같음.
- ③ grep: 장미숙·이승표·박영석 = ANAT4에만 · 방강미 = ANAT4 + OMS1(3Q — DX 2022 Q46·Q47 · LOAD 2022 Q48(카드 교수 · YEAR_PROF LOAD 2022 칸 없음)) → 방강미 파일에 OMS1 줄도 씀(PROF '그 교수가 낸 모든 과목·쿼터'). OMS1 형식 = `JBL_Q=3q fmt_audit.py OMS1`(scratchpad) 방강미 22 객 2 · 단 1 · 3Q 팩 data-yp '22:방강미' 3장. HIT 6과목에 네 이름 없음.
- ④-1 방강미.md 새로 씀(11-16): 1절 ANAT4(25 수업 5강 — JB 기출 교수 근거 없음(뱅크)) + OMS1(3Q DX·LOAD 22) · 2절 OMS1 22 객 2·단 1(fmt_audit) · ANAT4 0 · 멘트 원문(ANAT4 25년·23년 · OMS1 25년·23년) · 3절 기준선 3/3 · 축이 한정준에게 이어짐 2 · 5절 B14 '25년도 수업시간에 출제 예고' — 교수 불확실 · 6·7 없음 · 9절 동명 · Q48 교수 엇갈림.
- ④-2 장미숙.md 새로 씀: 1절 ANAT4(25 UL 1강 · 23 수업 4강 — JB 기출 교수 근거 없음(뱅크)) · 2~4절 0 · 멘트 원문 23년·25년 · 5절 B14 예고 교수 불확실 · 6·7 없음 · 9절 B12 ↔ 23 5강 이름 같음(세지 않음 — 근거 아님).
- ④-3 이승표.md 새로 씀: 1절 ANAT4(25 7강 Neck 예정 — JB 기출 교수 근거 없음(뱅크) · 23 Neck 칸 빈칸) · 2~4절 0 · 멘트 원문 · 5절 B14 예고는 이 교수 수업 '(예정)' 때 만든 JB → 이 교수 근거 아님 · 6·7 없음.
- ④-4 박영석.md 새로 씀: 1절 ANAT4(23 수업 Splanchnology·Face · 25 표에 없음 · PROF_LEC []) · 2~4절 0 · 멘트 원문 · 6·7 없음 · 9절 26 담당 모름.

## 대조 수(교수마다)
| 교수 | 대조한 것 | 수 | 결과 |
|---|---|---|---|
| 공통(ANAT4) | questions.md '출제' 있는 카드(22: B01·B14·B20·B21·X22 · 23: B06·B09·B12) ↔ YEAR_PROF HN {2023:'-', 2022:'-'} ↔ questions.md 교수 칸(빈칸 · '교수 미상') ↔ fmt_audit 출제 교수 '?' | 8 | 8/8 교수 미상 → 네 교수 셀 문항 0 |
| 공통(ANAT4) | 수업 표 쪽 그림(24판 1.jpeg 7줄 · 23판 1.jpeg 7줄) ↔ subject.py PROF_LEC·PROF_NOTE | 14 | 14/14 같음(방강미 25 5 · 장미숙 25 1 + 23 4 · 이승표 25 1 · 박영석 23 2 · 23 Neck 빈칸 1) |
| 방강미(OMS1) | questions.md '방강미 \| 출제 22'(Q46·Q47·Q48) ↔ OMS1 YEAR_PROF(DX 2022 '방강미' — Q46·Q47 · LOAD 2022 칸 없음 — Q48) ↔ 3Q 팩 data-yp '22:방강미' | 3 | 2 확정 · 1(Q48) 불확실(교수 근거 엇갈림 — yearprof_R_OMS1 3절 1 · 한정준.md 9절) |
| 방강미(OMS1) | 형식 = `JBL_Q=3q fmt_audit.py OMS1` 방강미 22 ↔ 3Q 팩 data-fmt | 3 | 객 2(Q46·Q47 mc) · 단 1(Q48 sh) 같음 · TREND_OMS1은 Q48 '서술(넘버링)' — 표는 fmt_audit 따름 |
| 방강미 | HIT 6과목(guide/handoff/hit26) 이름 검색 · HIT_OMS1 DX 26 교수 | 1 | 0건 · 26 DX = 한정준(Z14·Z15·Z17) → 6·7절 없음 |
| 장미숙·이승표·박영석 | 다른 과목 subject.py·JB 추출(work/jb)·review 검색 | 3 | ANAT4 밖 0 |

## 불확실 칸
- 방강미: 2절 OMS1 22 행(3문항뿐) · 3절 기준선 3/3(짤/탈 판정 없음) · 4절 세 줄 모두(1문항씩) · 5절 B14 예고 교수 · 9절 1(OMS1·ANAT4 같은 사람인지) · 9절 2(Q48 출제 교수).
- 장미숙·이승표·박영석: 2~4절 0(JB 기출 교수 근거 없음(뱅크)) — 칸 자체가 없음 · 5절 B14 예고 교수(장미숙 불확실 · 이승표 근거 아님 · 박영석 무관) · 26 담당 미정.
- 메인 확인 후보(고치지 않음): ① OMS1 Q48 2022 교수(OMS1 YEAR_PROF LOAD 2022 — 기존 A안 그대로) ② ANAT4 방강미 = OMS1 방강미 같은 사람인지(이름만 같음) ③ 24판 B14 '25년도 수업시간에 출제 예고' 강의·교수.
- 쓴 파일: guide/prof/방강미.md · guide/prof/장미숙.md · guide/prof/이승표.md · guide/prof/박영석.md (NFC 이름 확인 · ★☆ 0) · 다른 파일 수정 0(dump_review ANAT4 출력 = work/ANAT4/review 재생성 — 메인 지시) · 빌드·커밋 없음.

상태: 끝(11-16).
