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

## 10-09 26 갱신 2차 — PAR(26 권익재 새 PPT · 25 서미현 Parotidectomy 참고)
- 교수·슬라이드 구성이 바뀐 강의: 26 = 본문, 25 = [[PAR5:n]] 참고 · JB(서미현 출제) 판정 v=는 25 근거 기준(RULES 13 끝 — LIP 선례) · PROF_LEC 그대로, PROF_NOTE에 26 담당 한 줄.
- 26 새 카드 3장(Vessels·Temporal·Salivary 등) 덧붙임 → 카드 22장(19장 초과 — 합치기 금지라 그대로) · 예상문제 18개(옛 문항 지우지 않음 — RULES 13 끝).
- 25 → 26 바뀐 곳 표시({u:} ~120 · @UPD 7줄 — 교수 변경·새 쪽 21·바뀐 쪽 8·빠진 25 쪽 26) · MAND도 표시(@UPD 5).
- Stensen's duct 개구 위치 세 표현 병기(25 필기 '제1·2 대구치' · 26 p.3 'around upper 2nd molar'·p.5 '상악 제2 대구치 부근' · JB '제2대구치 맞은편') — PAR·MAND 같은 문구.
- 남은 확인: 🔑 7장의 뒷조각이 상자 밖 보통 줄로(렌더러 key_rest) · R07 JB 답 'Length: 5 cm'만 큰 단답 상자 · 26 필기 p.26 한 줄(뜻 애매해 안 넣음).
- 10-10 25→26 표시: NV 같은 슬라이드(25 p.7·35 복제 쪽만 빠짐) · NECK 26 새 쪽 3(p.4·5 공개 시험문제 정답 표·p.6 landmark 13) · LIP 새 PPT(25 한정준·최진영 56쪽 → 26 양훈주 28쪽) 주제 단위 — 새 주제 8·바뀐 값 2(palatoglossus·palatopharyngeus)·빠진 25 주제 13 회색(일측성 10+4·CP 4항목·LVP 40%·코 전부 = 기출 근거). 확인 필요: NECK 26 강조 3(25에도 있음 — NEW 26 안 붙임).
- 10-10 표시 규칙 바뀜(사용자 '26년도 강조와 26년도 피피티에 새로 추가된 내용 표시는 확실히 구분'·'필기 아님!! 슬라이드 원문'): 위에 적힌 '26 교수 강조·시험 예고 → NEW 26'은 옛 방식 — 지금은 `{e:}` 26 강조(강의별 수 work/<SID>/upd26/EMP_<KEY>.md) · NEW 26 = 슬라이드 원문 새·바뀐 내용만 · 필기에 NEW 26 없음(RULES 12·13 · `tools/check_unote.py`).


## 10-16 26판 JB(2025년 시험) 통합
- 새 문항 11(P04 NV · P05~P08·P10 LIP · P12 MAX · P14~P16 PAR · P20 TMJ) · MAX 26 자료(107쪽 — 25와 같은 슬라이드, 쪽 1~2 당겨짐 · 26 필기 강조 {e:} 12 · P12 = 26 p.12 그림 표지 9). 확인 필요: P05 JB 답 (2),(5) vs 26 p.12 표 (2),(4) · P20 '신경과 가지' 답에 가지 없음 · P16 '5개' 묻는데 답 4 · P04 JB 답과 슬라이드 핵심 landmark 다름 · 26판 17~20번 교수 머리 없음 → 박주영으로 · 26 형광펜 11쪽을 26 강조로 볼지.
- 자세한 보고: work/ANAT/jb26/R_JB26.md(클라우드 work — 세션 끝나면 사라짐)

## 10-19 TMJ(박주영 TMJ·SMAS) 26 자료 반영 — 경미
- 26 = 261014_박주영_TMJ,SMAS(43쪽 · 폴더 A14i · 키 TMJ) · 25 = 251027(47쪽 · A09i · 보조 키 TMJ5 · IMG_ALIAS TMJ5→TMJ).
- 바뀐 슬라이드 0 · 새 쪽 3(p.41 Gap arthroplasty 영상 링크만 새 슬라이드 `{u:}` · p.23·31 = 다음 쪽 앞 단계) · 25에만 6쪽(p.9 경첩/활주 · p.10-11 윤활관절 미세 해부 · p.36-38 측두분지 위치·safe zone) → 회색 '26에서 빠짐 · JB 짤 대비용' + 25 그림(TMJ5) · 26 수업은 p.36(Triad)에서 끝(26 학습부 "여기부터는 수업을 안 하셨어요") · 26 필기에 시험·강조 메모 없음({e:} 0).
- 25 p.7 A~G 구조 목록은 슬라이드가 아니라 25 학습부 필기였음(26 같은 슬라이드엔 화살표만) → 표 머리·'(25 학습부 답)' 출처.
- Q14 대조 ok → part(정답 5) synovial membrane 근거가 25 p.10-11에만 — 26 자료엔 'membrane' 없음 · 1)~4)는 26 p.24-27 소거법).
- 그림빵: p.7은 25 그림(26 학습부 상자가 답 7개를 보여 줌) · p.13·17·36 상자 다시(17·36은 26 학습부 상자도 가림) · 새 p.30(CN7 5 branch)·p.20(SMAS 5층) → TMJ 예상 활성 15 · 그림빵 6.
- 사용자 확인: 26 시험 범위가 p.36까지인지(p.37~43 26 수업에서 안 다룸) · 26 필기에만 있는 표 새 행(후두부 감각 = great occipital nerve).


## 10-25 JB 전수 검토 결정 반영(사용자 10-24 결정표 — guide/handoff/jb_audit_1024)
- V01 새 카드(18·19 Unilateral cleft lip 객관식 — JB 해설 문장, Q02 배지 19·18 뺌) · U21 새 카드(2021·2020 SMAS 객관식, Q15 −21·20) · R07→Q16 합침(이하선관 25·24·23·21) · 2020 17번→P12 · 22-2 분해(→T13) · U09 MAND · T17 MAX(prof 서병무) · U06 ans= · P20·P16 보충(P16 다섯째는 mastoid process '후보') · R13·R14 출처 '추가복원' · S11 숨김 · front=26 Q03·Q13·Q14·Q15·Q16·Q18·Q19·R02. 남은 확인: 24판 원본 잘림 여부(로컬에서_할_일).
- 사용자 표시 이관: tools/anat/jb_move.json(합친 id → 남는 id · 숨긴 id → '' · 앞면 바뀐 id → 자기 id).
- 10-27 26 구강악안면외과학1 실제 출제(학생 복원 — work/upload_1027_oms1) 꼴로 예상문제 더함(guide/handoff/PRED_OMS26_BRIEF.md · 보고 work/ANAT/pred26/R_OMS26_ANAT.md) · 기존 예상 그대로 · why 첫머리 '26 구강외과 꼴:' · subject.py TREND_NOTE 교수 한 줄.
