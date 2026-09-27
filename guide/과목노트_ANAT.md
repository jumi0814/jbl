# ANAT 임상두경부해부학 — 과목 노트 (완료 2026-09-25 · 전면 개편 2026-09-27)

## 자료 (materials/임상두경부해부학/ — 전부 원본 PDF, 쪽 이미지는 work/ANAT/mat/<파일>/i/)
| 키 | 강의 | 교수 | 연도 | 비고 |
|---|---|---|---|---|
| NECK | Neck dissection | 명훈 | 26 | 56쪽(OCR 42쪽). p.4~5에 교수님이 공개한 시험문제(level 경계 표) 그대로 · 보조 키 NK5 = 25 Neck dissection 67쪽(필기·경계 표 보충) |
| NV | 신경·혈관 해부학 | 권익재 | 26 | 45쪽(OCR 22쪽) + 25(47쪽, 보조 키 NV5 — JB 참고 쪽수는 25 기준) |
| LIP | 구순열·구개열·비 해부학 | 양훈주 | 26 | 28쪽(발생·병리해부·구개 근육). ⚠ 기출 대부분은 25 한정준(최진영 PPT, 56쪽, 슬라이드는 이미지 → OCR, 보조 키 LP5)의 keystone·framework·Kiesselbach·unilateral 10+4 → 두 자료를 한 정리본에 (25 전용 카드는 쪽 범위 100+로 '별도 파일') |
| MAND | Mandible | 서병무 | 25 | 83쪽, 21~25 필기 풍부 |
| PAR | Parotidectomy | 서미현 | 25 | 35쪽 |
| MAX | Maxilla | 서병무 | 25 | 109쪽 원본 PDF(그림·필기, OCR 61쪽)로 교체됨 — 예전 텍스트본(96슬라이드)은 폐기, 원본 쪽 기준으로 재작성. JB 참고 쪽수(24·23 자료)와 0~4쪽 어긋남 |
| TMJ | TMJ·SMAS | 박주영 | 25 | 47쪽 이미지 → OCR. p.1 시험 언급 쪽 6-7·15-17·39-40, p.46 QUIZ |

## 이번 개편 (커밋 7dd84a3, 2026-09-27)
- 정리본 카드 53 → 123(NECK 8→17 · NV 8→16 · LIP 10→18 · MAND 9→21 · PAR 6→19 · MAX 8→19 · TMJ 8→13), 그림(F:) 줄 49 → 232(그림 약 430장). 강의마다 작성 + 독립 검토(사실 대조·커버리지·원칙) 후 병합
- 문항 대조(annot.txt) 73문항 전부 작성: 강의자료 대조 A: 76 → 176줄, 판정(v=)·연결 강의(lec=) 재점검(T01·U09 ok→part, R14·U06 ok→part, Q04·R14·M03 연결 쪽 수정)
- 비교표 12 → 37, 예상문제 30 → 70
- 출제연도: JB 괄호 '(24. 23)'(마침표) 파싱 누락 수정 · 다른 판본 괄호로 확인된 해 추가
- 국문 부제의 연도 나열 제거(카드 aid가 바뀐 카드는 저장된 형광펜·빈칸이 복원 안 될 수 있음)
- 마무리 약어 점검(tools/check_abbr.py): 자료에 없는 약어를 원래 용어로 — TVP → tensor veli palatini, LLSAN·LLS(LIP) → 풀네임, END → Extended ND, EJV → external jugular v., JAMA → journal of the American Medical Association, MM(br.) → marginal mandibular, BFP(MAND) → buccal fat pad, SN mapping → Sentinel node mapping, XII·X → hypoglossal n.·vagus n. 자료에 있어 유지: LVP(LP5 p.31 슬라이드 제목) · LLC·ULC(LP5 p.48 그림) · STA·STV(TMJ p.40) · BFP(MAX p.8 그림) · LLS·OO·ION(MAX p.54 그림) · IOA(MAX p.85) · IVRO(MAND p.14 필기 'ivro') · LC(TMJ p.37 그림)

## JB 특이사항
- 구조: 연도 칸 안에 교수 소제목(2024/2023/2022 in 25판; 24판은 최진영 파트만 6쪽; 23판 2022~2020 + 명훈 2018·2017). 번호는 연도 칸마다 재시작, '추가복원 1·2', '2-1' 하위문항
- 정본 73: Q01~20(2024) / R01~14(2023) / S01~09+S11(2022) / T01~23 중 13(2021) / U03~24 중 12(2020) / M01~04(명훈 18·17). 판본 간 중복 61, 미연결 0
- tier B = 이종호(T01·T02·T03·U03·U05, 권익재 전임)·김성민(U23·U24, 파로티드 전임). 최진영·한정준 출제분은 양훈주(LIP)로 귀속, 이재현 방식과 동일
- 연도: Q02 (24,23,22,21,20) + 해설의 18·19 객관식 추가 / Q07 (24,22) + 해설 "23년 Le Fort 워딩" → 23 추가
- 미복원·근거 없음: S11(미복원), S07(FH plane 8±4 출처 불명), T02(권익재 PPT에 없음). 부분 일치 10(교과서·전임 교수 PPT 근거)
- COVER: 서병무·양훈주·박주영·서미현 20, 권익재 22, 이종호·김성민 19, 명훈 17

## 남은 것 (사용자 확인)
- 26년 시험 범위: 양훈주 26 자료에 없는 코(keystone·framework·Kiesselbach)는 25 한정준 자료로 유지 중
- 필기끼리 모순 — LIP: levator veli palatini와 hamulus(26 p.17 "걸려 있다" ↔ 25 p.24 "걸리는 건 아니다", 원고는 ⚠ + 슬라이드 따름) · MAND: parotid duct 개구(p.10 상악 1·2 대구치 ↔ p.7 하악, 원고는 p.10) · MAX p.12 ascending pharyngeal a. 출처 · NV p.27 mylohyoid br. 분지 위치(mental/mandibular foramen) · TMJ p.37 거리 '1.7cm(7mm)'/'0.7cm(7mm)'
- 판정 선택: MAX U13 v=ok(JB는 '측면그림', 슬라이드는 medial view — part로 할지) · T17을 NV·MAX 두 강의에 동시 연결해도 되는지(빌드 후 확인)
- NECK: 26 p.4 공개 시험문제를 ==형광==(시험에 나온 문장)으로 표시해도 되는지 · MRND Type 1 '제거: SCM·IJV'는 25 필기에서 추론
- 복원 불확실 문항: PAR Q17(p.20 vs p.27 그림) · NV Q20(상악/하악)·R12 · MAND T23·S03(그림 추측) — E:·annot에 ⚠
- 카드 제목(aid) 바뀐 카드(TMJ Skin Incisions·SMAS 등)는 기존 형광펜·빈칸이 복원 안 될 수 있음
