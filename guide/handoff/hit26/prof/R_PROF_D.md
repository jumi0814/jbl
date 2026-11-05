# R_PROF_D — 교수 프로필 담당 D (11-05)

> 맡은 교수: 이창하 · 안진수 · 서덕규 · 이인복 · 김선영 · 손호현 (과목 CONS · ESTH — `grep -n '<이름>' tools/*/subject.py` 결과 이 두 과목뿐 · tools/cons4·esth4 subject.py는 비어 있음 · 4Q JB 없음)
> 쓴 파일: guide/prof/<이름>.md 6개(NFC) + 이 보고. 다른 파일 수정·빌드·커밋·stash 0.
> 입력: work/3q26/ref_CONS.md·ref_ESTH.md(3Q 배포본 JB 카드 — data-yp 해별 교수·data-fmt 꼴·jj/tt) · tools/cons·esth/subject.py(YEAR_PROF·YEAR_PROF_Q·PROF_LEC·MENT_PROF·MENT_ALL·PROF_NOTE·TREND_NOTE·FINAL_NOTE) · tools/cons·esth/annot.txt(미복원·합친 문항·st=·rel=) · work/_tmp/fmt26/CONS.md·ESTH.md(fmt_audit) · guide/handoff/hit26/HIT_ESTH.md(5절 프로필 몫)·tools/esth/r26.txt · guide/handoff/trend26/TREND_CONS.md·TREND_ESTH.md·yearprof_R_CONS.md·yearprof_R_ESTH.md.
> 대조 방법: ref 카드의 (문항, 해) 쌍마다 data-yp 교수 ↔ subject.py YEAR_PROF_Q·YEAR_PROF 값(스크립트 scratchpad yp_check.py) — '일치' / '표에 없는 해(강의 연결 교수로 채움)' / '불일치'. 형식 칸 = fmt_audit 교수 × 연도 표와 같은 수인지. 26 3Q 절 = HIT_ESTH 표 줄 수.

## 1. 이창하 — guide/prof/이창하.md
- 범위: CONS ADH(23~25)·FRC(22~25) + ESTH INT·FUN·PLAN·SPE·MAT·VEN·(COL 카드 Q13·P20 — YEAR_PROF_Q) 22~25 + 2026 3Q ESTH 1~25번. FRC 11~21 '이전 교수'(Q26~Q29)는 안 셈.
- 대조(연도·교수): ref data-yp (문항, 해) **91쌍 — YEAR_PROF·YEAR_PROF_Q와 일치 91 · 강의 연결로 채운 해 0 · 불일치 0**(CONS 23 · ESTH 68).
- 형식 칸: fmt_audit 이창하 행 8칸(CONS 22·23·24·25 · ESTH 22·23·24·25) 모두 같은 수(CONS 5·7·6·5 · ESTH 15·14·18·21).
- 26 3Q 절: HIT_ESTH 5절 이창하 25줄 = r26 prof=이창하 25줄 = 프로필 6절 25줄 ✓ · 7절 = HIT 2절 합계(23/23 · 2/2 · 상 22/25 · N제 23/25+△2) 그대로. CONS 2026 = 복원 없음.
- 짤/탈 셈: 같은 id에 앞선 해가 있으면 짤(사이트 기준) + 괄호로 JB '변형' 표기·annot rel/st 축 기준 — 22~25 같은 id 49/91 · 축 55/91.
- 불확실 칸: ESTH Q27(24 교수 불확실 — 수에 넣고 탈 꼴 셈에선 따로) · Q13·P20(강의 COL · 교수 이창하) · P11↔Q11 같은 축 여부 · 미복원 번호(분모) · FRC 11~21 교수 미상 · Z20 쪽·Z11 등 복원 불확실 · CONS 2026 없음 · 1~2문항 칸(탈 꼴 '필기' 1 · '같은 쪽 다른 줄' 1).
- 입력과 어긋난 곳(보고만): TREND_ESTH(10-15)는 Q13·P20을 안진수로 셌으나 지금 YEAR_PROF_Q는 이창하 → 이 프로필은 YEAR_PROF_Q 따름(ESTH 24 18 · 25 21 — TREND 16 · 19와 다름).

## 2. 안진수 — guide/prof/안진수.md
- 범위: ESTH COL 23~25(YEAR_PROF) + 2026 3Q 안진수 1~3번.
- 대조(연도·교수): ref data-yp (문항, 해) **9쌍 — YEAR_PROF와 일치 9 · 채운 해 0 · 불일치 0**. COL '-' 해 13쌍(Q26 4 · Q28 2 · S14 4 · T20 3)은 안 셈.
- 형식 칸: fmt_audit 안진수 23·24·25 행 = 프로필과 같은 수(3·3·3). fmt_audit 안진수 22·21·20·18 행(Q26·Q28 6쌍)은 YEAR_PROF '-' 해 → 프로필에 없음(2절·9절 1에 적음).
- 26 3Q 절: HIT_ESTH 5절 안진수 3줄 = r26 prof=안진수 3줄 = 프로필 6절 3줄 ✓ · 7절 = HIT 3/3 · 상 3/3 · N제 범위 밖.
- 불확실 칸: 18~22 교수 근거 없음 · 24 안진수 문항(Q20 vs 시험지 자리 Q27) · SPD 강조 해 표기 · 탈 3개 모두 1문항 칸.

## 3. 서덕규 — guide/prof/서덕규.md
- 범위: CONS CRK·DHS 2013~2025(16 Q07 = 손원준 뺌) + ESTH 2018·2020·2021(C등급 6 id 포함). 2026 = CONS 복원 없음 · ESTH 담당 아님.
- 대조(연도·교수): ref data-yp (문항, 해) **93쌍 — YEAR_PROF와 일치 87(CONS 44 · ESTH 43) · 강의 연결로 채운 해 6(Q07 21·20 · Q08 21·20·18·17 — yearprof_R_CONS 2절 '근거 없어 뺀 해') · 불일치 0**.
- 형식 칸: fmt_audit 서덕규 행 CONS 11칸(13·14·17~25) · ESTH 3칸(18·20·21 — C 제외) 모두 같은 수(CONS 34·1·2·2·2·2·1·2·2·1·1 · ESTH 3·16·13). C 11쌍은 근거 칸에 따로.
- fmt_audit와 JB 원문이 어긋남(보고): Q07(넘버링)·Q08(객관식)이 카드 하나 꼴로 모든 해에 같게 셈 — JB 문제 줄의 해별 꼴(Q07 서술 → 나열 → 서술 → 객관 · Q08 나열 → 보기 → 서술 → 쓰기 → 고르기 → 객관)을 2절 아래에 적음 · 25 단답 3·서술 1·넘버링 1은 보기 미복원·추가 복원 + Q07 → JB·예고로는 34 전부 객관식.
- 26 3Q 절: 복원 없음(CONS) · 해당 없음(ESTH) — HIT 표 0줄 = 프로필 0줄.
- 불확실 칸: 채운 해 6쌍 · ESTH 18 근거 약함 · ESTH 19 기록 0(20 탈 판정) · 25 같은 문항 다른 복원(31~34) · C등급 · 26 형식 예고 없음 · 25 이전 탈 2.

## 4. 이인복 — guide/prof/이인복.md
- 범위: CONS WHT 2010~2025.
- 대조(연도·교수): ref data-yp (문항, 해) **30쌍 — YEAR_PROF와 일치 16(25·24·23·22·20) · 강의 연결로 채운 해 14(21·18~10 — yearprof_R_CONS 2절) · 불일치 0**.
- 형식 칸: fmt_audit 이인복 행 15칸(10~18·20~25) 모두 같은 수(합 30 = 서술 15 · 빈칸 11 · T/F 2 · 단답 2).
- fmt_audit와 JB·팩이 어긋남(보고): Q02를 fmt_audit는 '빈칸'(모든 해) · 팩 data-fmt는 '서술' · JB 문제 줄은 '24만 빈칸빵, 나머지 그림 그리고 설명' → 표 칸은 fmt_audit, JB 기준(서술 25 · 빈칸 1)은 표 아래 줄.
- 26 3Q 절: 복원 없음(HIT 0줄 = 프로필 0줄).
- 불확실 칸: 채운 해 14쌍 · 꼴 셈 세 갈래 · Q02 2010 그림 불명 · Q31 답 복원 메모 · 탈 꼴 T/F 2 · Q&A 1(1~2문항 칸).

## 5. 김선영 — guide/prof/김선영.md
- 범위: CONS INL·ANT 2020~2025(Q12 연도 미상 제외).
- 대조(연도·교수): ref data-yp (문항, 해) **12쌍 — YEAR_PROF와 일치 7 · 강의 연결로 채운 해 5(INL·ANT 21·20) · 불일치 0**.
- 형식 칸: fmt_audit 김선영 행 6칸(20~25) 모두 같은 수(3·2·1·2·2·2 — 서술 8 · 단답 4).
- fmt_audit '의심'(Q09·Q10 단답 기본값) ↔ JB '서술 나열 100%'(TREND_CONS 3-1) → 표 칸 fmt_audit, JB 기준은 표 아래 줄.
- 26 3Q 절: 복원 없음.
- 불확실 칸: 채운 해 5쌍 · 20 첫 기록 3의 탈 판정(23판 '21 년' 멘트 '나머지는 짤족'과 엇갈림 — 새로 찾은 것) · fmt 단답 4 · Q12 연도 미상 · 26판 Q11 강조 표시 · ANT 26 자료 없음 · 해마다 분모 1~3.

## 6. 손호현 — guide/prof/손호현.md
- 범위: CONS C01·C02(C등급 · 강의 연결 없음) 2010~2016.
- 대조(연도·교수): ref data-yp (문항, 해) **8쌍 — YEAR_PROF_Q와 일치 8 · 채운 해 0 · 불일치 0**.
- 형식 칸: fmt_audit 집계 밖(C등급 — fmt26 CONS 2절 'C·집계 제외') → 팩 data-fmt(es)·JB 문제 줄로 채움(서술 8 · 그림 그리기 5).
- 26 3Q 절: 해당 없음(16 뒤 출제 없음).
- 불확실 칸: 전부(2 id · 8회) · C01 참고 줄 = 김선영 17년 강의 파일 · 12·13 기록 없음.

## 합계 · 검사
- 연도·교수 대조: (문항, 해) 243쌍 — YEAR_PROF·YEAR_PROF_Q와 일치 218 · 강의 연결로 채운 해 25(서덕규 6 · 이인복 14 · 김선영 5) · 불일치 0. (이창하 91 · 안진수 9 · 서덕규 93 · 이인복 30 · 김선영 12 · 손호현 8)
- 형식 칸: fmt_audit 교수 × 연도 칸과 모두 같은 수(이창하 8칸 · 안진수 3칸 · 서덕규 14칸 · 이인복 15칸 · 김선영 6칸) — 손호현은 fmt_audit 집계 밖(C등급). fmt_audit와 JB 원문 꼴이 어긋나는 곳(서덕규 Q07·Q08 해별 꼴 · 이인복 Q02 빈칸 · 김선영 단답 의심 · 안진수 '-' 해 6쌍)은 표 아래 줄·9절에.
- 26 3Q 절: HIT_ESTH 이창하 25줄 · 안진수 3줄 = r26 prof 줄 수 = 프로필 6절 줄 수. CONS 2026 복원 없음 → 서덕규·이인복·김선영 6·7절 '복원 없음' · 손호현 '해당 없음'.
- 모든 줄 근거: 스크립트로 근거 표시(문항 id·§·TREND/HIT/ref/annot/subject.py 등) 없는 줄 0까지 고침.
- git 상태(알림): 메인 커밋 37be795f·aae13f42가 작업 중이던 guide/prof/이창하·안진수·서덕규·이인복.md를 함께 담음 → 그 뒤 근거 표기 보강으로 이창하·안진수·서덕규 3개가 다시 수정됨(M) · 김선영·손호현은 아직 커밋 안 됨(??). 이 담당은 커밋하지 않음.
