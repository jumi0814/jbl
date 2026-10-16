# R_CONS — FMT26 문항 형식 재판정 반영 + 25년 기출 ↔ 예상문제 연결 점검 (10-16 · CONS 담당)

- 브리프: guide/handoff/FMT26_BRIEF.md · 쓴 파일: tools/cons/pred.txt 하나(빌드·커밋·브라우저 없음)
- 읽은 것: CLAUDE.md 절대 규칙 · RULES.md 11절 · PRED26_BRIEF 2절 · 과목노트_CONS · work/_tmp/fmt26/CONS.md · trend26/TREND_CONS.md · link_audit.md CONS 절 · review/questions.md(Q30~Q68 전부) · review/materials.md · tools/cons/pred.txt
- 진행: (작업하며 아래 절을 하나씩 덧붙임)

## 1. 형식 대조 — fmt26(고친 판정) ↔ TREND_CONS 서술 ↔ 활성 예상문제 꼴(고치기 전)
| 교수 · 강의 | fmt26 2023~2025 (서술·단답·객관·T/F·빈칸) | TREND_CONS 서술 | 판정 | 활성 예상(전) 꼴 |
|---|---|---|---|---|
| 이인복 · WHT | 25: 3·1·0·1·0 / 24: 2·1·0·0·0 / 23: 1·1·0·1·0 | 서술·n가지 + T/F 5 묶음(23·25, Q06·Q30) + 24 빈칸(Q02), 객관식 0 | 일치(fmt '단답' = n가지 쓰기 · Q02 24 빈칸은 옛 서술 발문 글로 세어 서술) | 18: T/F 묶음 3(5개 2 · 3개 1) · 빈칸 1 · 그림 1 · 그림빵 1 · 서술 12 · 객관식 0 → **꼴 맞음(손대지 않음)** |
| 서덕규 · CRK·DHS | 25: 3·3·30·0·0 / 24: 1·0·0·0·0 / 23: 2·0·0·0·0 | 25년 37블록 **전부 객관식 5지**('옳은 것' 11 · '아닌 것' 8 · 증례 2) · 24 전 2축 서술 | 일치(남은 서술 3 = Q07·Q08(옛 서술 발문 글에 25 병합)·Q46(추가 복원, 보기 없음) · 단답 3 = Q41·Q54 미복원 · Q56 같은 줄 보기 번호 없음 → 실제는 모두 객관식) | **어긋남**: CRK 18 중 객관식 7(39%) · DHS 17 중 객관식 5(29%) — 25년 100% 객관식인데 서술이 다수 |
| 김선영 · INL·ANT | 25: 1·1·0·0·0 / 24: 0·2·0·0·0 / 23: 0·2·0·0·0 | 100% 예고 쪽 서술 나열(n가지) | 일치(fmt '단답' = 'n가지 쓰시오' 나열 — 객관·T/F·빈칸 0은 같음) | INL 6 · ANT 5 전부 서술 나열 → **맞음** |
| 이창하 · ADH | 25: Q14 객관 · Q67 객관 · Q68 단답 / 24: Q14·Q17_1 객관 · Q15 빈칸 · Q18 서술 / 23: Q14 객관 · Q16·Q17 단답 · Q19 서술 | ADH = 5지 '옳은 것'(Q14 3년 연속 · Q17_1 · Q67) + p.19 표 단답 + 목록 서술 | 일치 | **어긋남(부분)**: ADH 16 중 객관식 1(Q14 축)뿐 — 25 Q67(self-etch·universal '옳은 것')·Q68(p.19 표) 축에 객관식 없음 |
| 이창하 · FRC | 25: Q20·Q22 서술 / 24: Q20·Q21 서술 / 23: Q20·Q22 서술 · Q25 단답 | 목록 서술·단답 · 객관식 22 1회(Q23) | 일치 | FRC 17: 서술·단답 위주 + 객관식 1(Q26 축) → **맞음** |

- 고칠 곳: CRK·DHS(서술 → 5지 객관식, 26 예고 3축·핵심 정의 등은 서술 짝 유지 — TREND 2-6 "예고 세 축은 넘버링 서술로도 한 번씩") · ADH(Q67·Q68 축 5지 '옳은 것' 새 문항). WHT T/F 묶음은 이미 있음(블록 #6 'T/F 5개(틀리면 감점)' b=Q30,Q06 · #13 T/F 5 · #7 T/F 3).

## 2. Q68(사용자 예시) 연결 재확인 — 이상 없음
- docs/packs/CONS.js(현재 빌드) 기준: ADH 기출 탭(L.jb)에 Q68 있음 · 정리본 ⭐ 2곳(lec_ADH 카드 'Functional Monomers · 10-MDP ★' 머리 jb= + `E: Q68` 줄 237) · 정리표 2 · 비교표 2(tables.txt 527-528 'R: 4-META … {jb:Q68}') · 예상문제 b=Q68 2개(10-MDP 기능·결합 / p.19 표 full name 단답).
- 이번에 더함: Q68 축의 이창하 객관식 꼴 '옳은 것' 1개(아래 4절 N3) — 23 단답(Q17) → 24 객관식(Q17_1)으로 바꿔 낸 이창하 꼴과 같은 방식.

## 3. 고친 블록(개선 — Q·A 다시 씀, oid = 지금 aid · 모두 pred_before에 있는 aid)
쪽 근거는 모두 쪽 이미지 Read로 확인(work/CONS/lec/C09i·C03i·C02i·C08i·C11i).
| 강의 | 전(Q 첫머리) | 후 | 정답 근거 쪽 | oid |
|---|---|---|---|---|
| CRK | Cracked tooth와 VRF의 차이를 … 비교하시오(서술) | 5지 '옳지 않은 것' — 예후를 바꾼 보기 ⑤ | CRK p.61 Summary · p.18·20·13·34 | CONS:P:crackedtooth와verticalroo_5808f4 |
| CRK | 5가지 분류 중 예후가 Hopeless인 두 가지…(서술) | 5지 '짝으로 옳지 않은 것'(분류 – 치료 흐름·예후) ⑤ VRF | p.60 Clinical Treatment · p.61 · p.20 · p.38 | CONS:P:5가지분류중예후가hopeless인두가지와치료_ababf0 |
| CRK | Craze line과 cracked tooth를 … 구별하시오(서술) | 5지 '옳은 것' ③ | p.16 · p.18 · 26 필기 p.42·45 · p.60 | CONS:P:crazeline과crackedtooth를범_c0282d |
| CRK | AAE 표에서 VRF의 Location… 쓰시오(단답) | 5지 '옳지 않은 것' ⑤ Symptoms(= Fractured cusp 칸) | p.13 AAE 표 · p.20 | CONS:P:aae분류표에서verticalrootfrac_7c8220 |
| CRK | band 대신 crown을 권하는 이유…(서술) | 5지 '옳지 않은 것' ⑤ "f/u 더 필요하면 band"(Temp Cr의 반대) | p.58·59 · 26 필기 p.57·59 | CONS:P:crackedtooth의치료로band대신cr_de7467 |
| CRK | Fractured cusp의 원인 3가지와 …(서술) | 5지 '옳은 것' ② margin 위치 | p.31·32(26 새) · p.17 · p.16 · p.60-61 | CONS:P:fracturedcusp의원인3가지와치료계획_78cc37 |
| CRK | 교수님 연구 증상·방향 분포를 쓰고…(서술) | 5지 '옳은 것' ③ M-D 40.2·B-L 40.2·복합 19.6 | p.25 · p.28 | CONS:P:교수님연구에서crackedtooth의증상분포_7385cf |
| CRK | (객관식 — 25 JB 멘트 "올해는 객관식") Longitudinal tooth fracture의 분류… | 발문 앞 메모 글만 뺌(보기·답 그대로) | — | CONS:P:객관식25jb멘트올해는객관식longitudi_d66d1a |
| DHS | 중합수축응력과 접착력의 크기 관계…(서술) | 5지 '옳은 것' ③ 계면파괴 | DHS p.80(26 새) | CONS:P:레진수복시중합수축응력과접착력의크기관계에따라생_e5aa68 |
| DHS | SDF의 성분별 효과와 주의점(서술) | 5지 '옳지 않은 것' ⑤ chemical burn 없음 | p.96·97(26 새) | CONS:P:sdfsilverdiaminefluoride_75a9aa |
| DHS | My Clinical tips 4가지를 쓰시오 | **증례 객관식 A~E**(25 증례 꼴 — p.89 미백 후 시림 환자 + p.95 tips) 정답 D | p.89 · p.95(26 새) · 25 JB 39번 해설 e) | CONS:P:서덕규교수님의지각과민치아myclinicalt_bdbf00 |
| DHS | home care '기본 중의 기본'·치약 RDA 비교(서술) | 5지 '옳은 것' ③ 저연마 ↔ plaque 제거력 균형 | p.100·101 · DH5 p.25 필기(RDA 200↑ / 50-80) | (원래 oid 그대로) CONS:P:지각과민환자의homecare에서교수님이기본중_d4ffd8 |
| DHS | 비우식성 병소 3가지를 원인과 함께…(서술) | 5지 '옳지 않은 것' ⑤ 모양만 보고 단정 | p.74-77(26 필기 p.77 혼재) | CONS:P:치경부노출로시린치아의원인이되는비우식성병소3가_b45844 |
- 머리 필드는 그대로(t에 '교수 형식(객관식)'만 덧붙임 · pr·b·why 그대로). 원래 A의 {u:}(26 새)·{n:}(필기) 표시는 옮겨 유지.
- 서술로 남긴 서덕규 문항(짝 객관식이 따로 있음): CRK 정의(영문)·검사법(26 예고 ①)·cracked tooth 특징 3(26 예고 ③)·분류 5 + 의미(26 예고 ②) / DHS flow 방향 쓰기·tubule 수치(26에서 빠짐)·정의·Robin 3·시린 원인 5·K nitrate·oxalate 기전(26에서 빠짐)·Class V 원칙(하) — TREND 2-6 "26 형식 예고 없음 → 예고 축은 넘버링 서술로도 한 번씩".
- 결과 꼴(활성): CRK 19 = 객관식 15('옳은 것' 7 · '옳지 않은 것' 7 · 증례 1) + 서술 4 · DHS 18 = 객관식 11('옳은 것' 4 · '옳지 않은 것' 5 · 고르기 1 · 증례 1) + 서술 7 · ADH 18 = 객관식 3 + 서술·단답 15.

## 4. 25년 기출 ↔ 예상 연결(link_audit △ 5 → 0 예정) · b= 더한 것 · 새 문항
| 25 문항 | 처리 | 블록 |
|---|---|---|
| Q55 병리생리(세관액 움직임) | 같은 축(p.91 hydrodynamic) 기존 블록 b=에 더함 | DHS 'Hydrodynamic theory에 따라 … 흐름 방향' b=Q08 → Q08,Q55 · 'inward flow 묶은 것'(객관식) b=Q08 → Q08,Q55 |
| Q54(미복원 '약제 문항') · Q56 치약 성분(potassium nitrate) · Q58 NovaMin 기전 | 같은 축 기존 블록 'Potassium nitrate와 oxalate 기전'은 b가 이미 3개(Q57·Q63·Q64) → **새 문항 N1** | DHS N1 |
| Q45 '씹을 때 머리까지 아프다'(답 불확실 ②?) | 같은 축(증상·통증 기전) 기존 객관식 없음 → **새 문항 N2** | CRK N2 |
| (형식) Q67 self-etch·universal '옳은 것' | 축 연결은 있었으나(b=Q67 서술 5개) 객관식 꼴 없음 → **새 문항 N4** | ADH N4 |
| (형식) Q68 p.19 표 | 축 연결 있음(2개) · 객관식 꼴 없음 → **새 문항 N3** | ADH N3 |

새 문항(모두 t=짤 변형 · 교수 형식(객관식) · 보기 5):
- **N1 DHS 상** b=Q54,Q56,Q58 — "약제와 기전의 짝으로 옳은 것" 정답 ② potassium & oxalates(potassium = nerve desensitization · oxalate = tubule occlusion) — DHS p.92 26 필기 · WHT 슬라이드 115 26 필기(fluoride·potassium nitrate) · 오답 근거 DH5 p.20·21·22·24(26에서 빠짐이라 A에 표시). why "25 약제 축 최다 · 26 p.92 필기 기전".
- **N2 CRK 중** b=Q45,Q35 — "머리위에까지 찌릿 … 씹었다 뗄 때 아파요 — 이 통증에 대한 설명으로 옳은 것" 정답 ③(벌어졌다 오므라듦 · fluid movement 또는 innervation 자극 추정) — CR5 p.46 25 Q&A 필기(26에서 빠짐) · CRK p.24·25·29. t에 '26에서 빠짐(Q&A) · JB 대비'. 답 불확실 문항 축이라 상이 아닌 중.
- **N3 ADH 상** b=Q68,Q16,Q15 — "Functional Monomers 표(p.19)에 대한 설명으로 옳은 것" 정답 ② PENTA full name — 오답: 4-META phosphate ○ / GPDM phosphate ✗ / MDP·HEMA에 다른 단량체 full name(Q68 JB 해설·예시 답안). 26 필기 p.19 강조 {e:}(25년도에도 강조함).
- **N4 ADH 상** b=Q67 — "다음 중 옳은 것"(Q67 선지 뒤집기: smear layer 제거 여부 · selective enamel etch 15 sec · total-etch 60 sec × · universal mode · thick hybrid layer는 total-etch 단점) 정답 ② — ADH p.31·27·26·12·33·30·25.

## 5. 그 밖에
- WHT 't=미출제'인데 25 Q30 ②(10% CP at-home = safe·efficient)가 이미 물은 내용 2블록 → t만 '짤 변형'으로(Q·A 그대로): 'Night guard vital bleaching의 장점과 단점'(장점 Safest, efficient method = Q30 ② 근거 슬라이드 81) · '10% carbamide peroxide는 몇 %의 H2O2 … 결론 슬라이드'(슬라이드 182 = Q30 ② 근거).
- link_audit '△ t 미출제인데 b=' 나머지 5는 같은 축 다른 항목이라 그대로: WHT 슬라이드 21 표(Q30 ③ 이웃 쪽) · INL 와동형성 원리 5(Q12는 같은 p.43의 cusp coverage) · ANT Class 4 layering(Q66 해설이 인용한 쪽) · ADH Self-etch 특성 목록 p.30(Q67은 protocol 선지) · FRC favorable vs unfavorable(22 Q24 답 ④ 한 항목).
- 26에서 빠진 내용 표시: 25 쪽만 근거인 활성 블록은 'K nitrate·oxalate 기전'(이미 '26에서 빠짐 · JB 대비') 하나 · 새 N2도 표시함. 답이 26 자료와 다른 블록은 이번에 본 블록 중 없음(WHT T/F 5 묶음 답도 슬라이드 134·16·26·182·130 원문으로 다시 확인).
- 보관(x=1) 0 · 지운 블록 0(블록 116 → 120).

## 6. 검사
- `.venv/bin/python tools/pred_check.py CONS` → ✗ 0 · △ 0 (WHT 18 · CRK 19 · DHS 18 · INL 6 · ANT 5 · ADH 18 · FRC 17 활성)
- `tools/check_abbr.py CONS` → 11개(작업 전과 같은 목록 — 새 약어 0) · `tools/check_eyears.py CONS` → 0건(이 도구는 lec E:·annot K:만 봄 → pred why·t 연도는 따로 스크립트로 b 배지와 대조: 이번에 쓴 why·t는 모두 배지 안의 해)
- link_audit '예상 = 기출' 유사도(0.86) 미리 계산 — 새·고친 문항 최고 0.68(✗ 없음). link_audit·사이트 반영은 메인 빌드 뒤.

## 7. 사용자 확인 필요
- 서덕규 26 형식: 26 필기에 '객관식' 예고 없음(TREND 8-1) — 객관식 위주로 바꾸되 26 예고 3축·핵심 정의는 서술 짝을 남김. 26이 다시 서술로 돌아가면 서술 짝으로 대비.
- N2(Q45 축)는 JB 답 자체가 불확실(②?) — 근거는 25 Q&A 필기(26에서 빠짐)뿐.
- Q41('special enamel' 미복원)은 축을 알 수 없어 기존 b(craze vs cracked)만 둠 — 새 문항 없음.
- 객관식으로 바꾼 서술 블록에 붙어 있던 ✓·✗·★ 기록은 oid로 이어지지만, 이제 객관식 문제에 붙어 보임.

## 최종 답(5줄)
- 형식 대조: fmt26 판정과 TREND_CONS는 네 교수 모두 일치(서덕규 25 = 실제 전부 객관식 — fmt 표의 서술 3·단답 3은 옛 발문 병합·미복원·번호 없는 보기 탓) · 어긋난 곳은 예상문제 꼴 — CRK 객관식 7/18 · DHS 5/17 · ADH 1/16.
- 개선 13(oid 이어짐): CRK 서술 7 → 5지 객관식('옳은/옳지 않은' 반반) + 발문 메모 정리 1 · DHS 서술 5 → 5지 4 + 증례 1 → CRK 객관식 15/19 · DHS 11/18(26 예고 3축·정의 등 서술 짝은 남김).
- 25 연결: Q55 → 기존 hydrodynamic 2블록 b= · Q54·Q56·Q58 → 새 N1(DHS 상, 약제–기전 짝) · Q45 → 새 N2(CRK 중, 26에서 빠진 25 Q&A — JB 대비) · ADH 새 N3(Q68 p.19 표 객관식, 상)·N4(Q67 뒤집기, 상).
- Q68 연결 이상 없음(기출 탭·⭐ 2·정리표·비교표·예상 b= 2 → 3) · WHT T/F 5 묶음(감점식) 이미 있음 · WHT t '미출제' 2 → '짤 변형' · 보관 0 · 지운 블록 0.
- 검사: pred_check ✗0 △0 · check_abbr 새 약어 0 · check_eyears 0(pred why·t 연도는 별도 대조 — 이상 없음) · 빌드·커밋 안 함.
