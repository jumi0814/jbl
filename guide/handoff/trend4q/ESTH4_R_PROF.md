# R_ESTH4 — ESTH4(4Q 심미치과학) 교수 프로필 담당 보고(11-16)

맡은 범위: guide/prof/ 조준호(이어 씀) · 여인성(새로) · 윤형인(새로) · 최순영(새로) · 백승학(새로) · 이창하(이어 씀 — LAM tier C) · 한중석(새로 — ESTH4 CER·CAD + IMPL4 PAST 줄) · 이재현(새로 — 옛 출제 RBR) · (이용무·곽재영 = GERI4 담당 — 쓰지 않음)
입력: work/ESTH4/review/questions.md(머리 '출제') · tools/esth4/subject.py YEAR_PROF·MENT_PROF·PROF_NOTE · fmt_audit ESTH4(11-16 분류기 고친 뒤 다시 돌림) · work/ESTH4/jb/R_JB_ESTH4.md·V_JB_ESTH4.md · IMPL4(한중석) tools/impl4/subject.py·work/IMPL4/review/questions.md·fmt_audit IMPL4 · 기존 프로필 조준호·이창하 · HIT(3Q) — 조준호 HIT_IMPL · 이창하 HIT_ESTH

단계:
1. 입력 확인(questions.md·qids.json 신선도 · fmt_audit 다시)
2. 교수별 문항 표(출제 연도 기준 YEAR_PROF) — 대조 수
3. 파일 쓰기: 조준호 → 여인성 → 윤형인 → 최순영 → 백승학 → 이창하 → 한중석 → 이재현
4. 검사(연도·교수 대조 · 형식 = fmt_audit 표)

## 진행
- [x] 1 입력 확인(11-16 23:49~51): ESTH4·IMPL4 questions.md가 팩(23:46)보다 낡음 → `dump_review.py ESTH4`(50)·`IMPL4`(42) 다시 · 3Q ESTH(61)·IMPL(41)도(review 없음/낡음) · `fmt_audit.py ESTH4` PASS(문항 47 · 의심 14 — 고친 fmt_of 그대로 S01·C07·C12 등 ⚑) · `fmt_audit.py IMPL4` PASS · `JBL_Q=3q fmt_audit.py ESTH IMPL` PASS(여인성·이재현 3Q 줄)
- [x] 2 교수별 (문항, 해) 대조 — scratchpad ESTH4_PROF_chk.py(qids.json yrs × subject.py YEAR_PROF·YEAR_PROF_Q — 칸 없으면 카드 교수):
  - 조준호 11 = ESTH4 8(C01~C04 24 · C05~C08 23) + IMPL 3Q 3(P08~P10 25) (+ 26 3Q r26 Z04~Z06 3 — 기존 프로필) · C08 20 = '이전 교수'(셈 밖)
  - 한중석 14 = ESTH4 9(C05·C06·C07·C10·C11·C12·K01 21 + C08·C09 22 — C06 21은 25판 괄호뿐) + IMPL4 5(X01·X02 22·20 · X04 20 — PAST는 YEAR_PROF 칸 없음 → 카드 교수 대체 · V_JB_IMPL4 'QPROF 대체' 근거)
  - 이재현 5 = ESTH4 R01 24·23 + IMPL 3Q Q08 24·23 · R11 23
  - 최순영 3 = D01 24 · D02 23 · D03 23 / 백승학 3 = S01 24·23·22(S01 20 = '-' 셈 밖 — fmt_audit는 data-prof 대체로 백승학 20에 셈)
  - 이창하 ESTH4 3 = L01~L03 22(tier C) (3Q ESTH 68 · CONS 23은 기존 그대로 — qids 68 같음)
  - 여인성 6 = 3Q ESTH T21~T23 21·20(YEAR_PROF_Q) · ESTH4 0 / 윤형인 0
- [x] 3-1 조준호(이어 씀) 끝: 머리 11-16 줄 · 1절 ESTH4 줄(+4Q 줄 갱신 꼬리) · 2절 ESTH4 3줄+합 · 3절 ESTH4 짤/탈 · 4절 ESTH4 3줄 · 5절 ESTH4 멘트·25 신호 · 8절 ESTH4 묶음 · 9절 6~11 — 6·7절(IMPL 26 3Q)은 그대로
- [x] 3-2 여인성(새로) 끝: 3Q ESTH T21~T23 21·20(6 · fmt_audit 3Q 객관 2·빈칸 1 ×2 같음) · ESTH4 0 · 6·7절 '없음' · 불확실 5
- [x] 3-3 윤형인(새로) 끝: JB 기출 없음 · 1절 + 25판 멘트 원문만 · K01은 한중석 쪽
- [x] 3-4 최순영(새로) 끝: D01 24 · D02·D03 23 = fmt_audit 23 객관1·단답1 / 24 단답1 같음 · 탈 3/3 · 불확실 5
- [x] 3-5 백승학(새로) 끝: S01 22·23·24(3 · fmt_audit 단답 ⚑ — 20 칸은 fmt_audit가 백승학에 셈 · YEAR_PROF '-'라 뺌) · 짤 3/3 · TREND_NOTE '직전 2년 기출 먼저' 문구 제안 · 불확실 5
- [x] 3-6 이창하(이어 씀) 끝: 머리 11-16 줄(54 id · 94회) · 1절 ESTH4 줄 + 4Q 줄 갱신 꼬리 · 2절 ESTH4 2022 줄(fmt_audit 2절 L01 단답·L02 넘버링·L03 서술 같음) · 3절 · 4절 2줄 · 5절 · 8절 · 9절 9~10 — 6·7절 그대로
- [x] 3-7 한중석(새로) 끝: ESTH4 9(21 7 + 22 2 — fmt_audit '한중석 22 빈칸1·넘버링1 / 21 빈칸1·단답4·서술2' 같음) + IMPL4 PAST 5(fmt_audit 2절 X01·X02 단답 · X04 서술 같음) = 14 · 불확실 9
- [x] 3-8 이재현(새로) 끝: IMPL 3Q Q08 24·23 · R11 23(fmt_audit 3Q '이재현 24 단답1 · 23 단답2' 같음) + ESTH4 R01 24·23(fmt_audit '이재현 24·23 단답 1' 같음) = 5 · 불확실 5
- [x] 4 검사(11-17 00시대):
  - 연도·교수 대조(questions.md 머리 '출제' × YEAR_PROF·YEAR_PROF_Q — scratchpad ESTH4_PROF_chk.py) **113쌍 = 프로필 수와 같음**: 조준호 11(ESTH4 8 + IMPL 3) · 한중석 14(ESTH4 9 + IMPL4 5 — PAST는 YEAR_PROF 칸 없음 → 카드 교수 대체 표시) · 이재현 5 · 최순영 3 · 백승학 3 · 이창하 71(ESTH 68 = 기존 프로필 수 그대로 + ESTH4 3) · 여인성 6 · 윤형인 0
  - 형식 칸 = fmt_audit 표: ESTH4 1절 조준호 24·23 · 한중석 22·21 · 이재현 24·23 · 최순영 24·23 · 백승학 24·23·22 행 일치 · 2절 L01~L03(이창하)·IMPL4 2절 X01·X02·X04(한중석) 일치 · 3Q ESTH 여인성 21·20 · 3Q IMPL 이재현 24·23 일치 · **어긋남 1**: fmt_audit '백승학 20 단답 1'(S01 20 칸 — YEAR_PROF SMI 2020 '-'인데 data-prof 대체) → 프로필은 셈 밖으로 두고 적음
  - 26 3Q 실제 절: 조준호(IMPL Z04~Z06 3)·이창하(ESTH Z01~Z25) 그대로(HIT 표와 같음 — 손대지 않음) · 새 프로필 6개 = '없음'
  - 답 글 검사: 새로 쓴 줄에 JB 답 낱말 0(answer 낱말 grep — 'load to fracture' 2곳은 '두께 ↑ → 파절 하중'으로 바꿈 · 조준호 11-05 줄의 scan body·pick-up은 옛 줄이라 그대로)
  - 파일 이름 NFC ✓ · 더하기만(조준호·이창하 옛 줄 지운 것 0 — 이창하 1절 4Q 줄은 꼬리에 '(11-16 갱신: …)'만)
  - 참고: 메인이 진행 커밋 4e79798f에 여인성·윤형인·최순영·조준호(그 시점 판)를 이미 넣음 → 그 뒤 고친 것(미커밋) = 조준호 1줄('load to fracture' → '두께 ↑ → 파절 하중') · 이창하(이 담당 수정분 전체) · 새 파일 백승학·한중석·이재현

## 결과 요약
| 교수 | 파일 | 대조 수(문항×해) | 불확실 칸 |
|---|---|---|---|
| 조준호 | 이어 씀(+ESTH4) | 11(ESTH4 8 + IMPL 3) | ESTH4 2해 8문항뿐 · C06·C07 형식 ⚑ · C03↔C05 축 · 24 탈 쪽이 손본 쪽인지 · IMPL4 R02 셈 밖 · CER 2020 이전 교수 |
| 여인성 | 새로 | 6(3Q ESTH T21~T23 21·20) | 2020 출제 쿼터(3Q/4Q) · 22~24 3Q 문항 0 · 4Q RBR 기출 0 · 표본 3축 |
| 윤형인 | 새로(JB 기출 없음) | 0 | 2025 시험 JB 미수령 · 26 담당 미정 |
| 최순영 | 새로 | 3 | 3문항 모두 · 23 첫해인지 · '반탈' 멘트 ↔ 탈 2/2 · D02 선지 미복원 |
| 백승학 | 새로 | 3(S01 22·23·24 · 20 '-' 셈 밖) | S01 22 = 괄호뿐 · 2024 미복원 16-17 자리 · 형식 fmt 단답 ⚑(원문 넘버링) |
| 이창하 | 이어 씀(+ESTH4 LAM) | 71(ESTH 68 그대로 + ESTH4 3) | ESTH4 2022 3문항뿐(tier C) · 23 4Q 수업 뒤 문항 0 |
| 한중석 | 새로(ESTH4 CER·CAD + IMPL4 PAST) | 14(ESTH4 9 + IMPL4 5) | 2021 칸 서덕규 강의 섞임 가능 · CER 2020 이전 교수 · C06 21 괄호 · ★ 4/6 ↔ 사이트 탈 · IMPL4 PAST 교수 대체 · 형식 ⚑ 3 · K01 연결 |
| 이재현 | 새로(IMPL 3Q PART + ESTH4 RBR) | 5 | 23 ESTH4 강의명 ↔ R01 주제 · IMPL 24 미복원 9 · '반탈' ↔ 탈 · 표본 5 |

## 메인에게(넣을 것·확인)
1. TREND_NOTE 문구(c ⑥ 6 — 짤 교수): `TREND_NOTE['백승학'] = '직전 2년 기출 먼저 — 24·23 같은 한 문제(Components of aesthetic smile 8가지 · 넘버링 꼴) · 25 필기 "시험문제 넘버링 한문제"'` · 조준호(ESTH4 짤 4/8 · 축 5/8)는 '직전 2년 기출 먼저(24 C01~C04 · 23 C05~C08)' 줄 권함(guide/prof/조준호.md §8 ESTH4).
2. fmt_of(11-16 고친 뒤)에도 ⚑ 남음: S01(원문 넘버링) · C07(빈칸) · C12(서술) · C06(줄임말+빈칸) · IMPL4 X01·X02(원문 나열 — fmt_audit 의심 목록엔 안 뜸).
3. fmt_audit가 YEAR_PROF '-' 해를 data-prof로 대체해 셈(S01 20 → 백승학 · P10·P11 20 → 곽재영) — 프로필은 YEAR_PROF대로 뺌.
4. 사용자 확인 새 것 없음(JB 단계 5절 그대로 — K01 연결 · C08·S01 2020 합침 · RPD·SMI 2022 교수 근거 약함).
