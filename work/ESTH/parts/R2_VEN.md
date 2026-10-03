# ESTH/VEN 독립 검토 (10-03)
대상: `tools/esth/lec_VEN.txt` · `work/ESTH/parts/{annot,tables,pred}_VEN.txt` — 원본 34쪽 이미지 전부 직접 확인(p.4 막대그래프는 원본 PDF를 6배로 렌더해 재확인), JB 25판 p.7-8 이미지(Q23 그림 메모)·questions.md 7문항 대조.

## 고친 것 (17건)
### 원고 lec_VEN.txt
1. `!` JB 경향 · T12를 "전임 교수 것"이라고 적었던 것 → **등급 A(현 교수) 문항**으로 바로잡음(questions.md `tier A | 이창하`, subject.py TIERS A = 서덕규 퀴즈에서 이어진 문항). 현 교수 문항 3개(Q23·Q25·T12)와 참고 문항(T11 C · T21~T23 B)을 나눠 적음. 근거: questions.md T12 머리줄.
2. `!` JB 경향 · 레진 접착성 보철물·도재 라미네이트 비니어가 지금 강의계획상 11주 여인성 강의(기말 범위)라는 점 추가 — Introduction(26) p.3 강의계획 이미지로 확인.
3. `!` 수업 진행 · p.1 필기("3Q 마지막 수업!", 4Q 안내, "4Q와 좀 겹치는 - 실제 임상 케이스 몇 개")가 빠져 있었음 → 추가.
4. DCV 장단점 카드 · ⑥ Premature wear of the opposing dentition 설명 → "⚠ 함정: 문구만 보면 단점 같지만 슬라이드 Advantages 목록"으로 고침(객관식 함정 대비, p.5 Porcelain 단점 Wear properties와 연결). 근거 p.6·p.5.
5. Clinical Considerations 카드 · 필기 짝이 어긋나 있었음: ① Single shade에 붙인 "유니버셜한 셰이드는 어색" 필기는 원래 ⑤ Translucency 줄("…어색해 보일 수 있으므로 incisal에 투명한 셰이드로 해야 함") → ① = "색 고려", ⑤ = 필기 원문. ③에 빠진 "특히" 복원. 근거 p.9 필기 6줄.
6. T12 ⭐ · "⚠ 순서:"(⚠는 함정·불일치 표시인데 순서 나열에 씀) + 보기 문구를 줄여 적었던 것 → JB 보기 원문으로 10단계(D. Wax up → … → C. Finishing과 polishing, 렌더러가 번호 단계로 보여줌) + 별도 ⭐ 줄에 근거(서덕규 2021 p.2 없음 · p.9 = D→F · p.13 palatal 먼저)와 ⚠ 함정(G는 F·E 뒤 · A→I→C).
7. Materials 카드 · "열을 가해 좀 더 (강도가) 높아질 수 있게"(해석 삽입) → 필기 원문 "좀 더 전단력? 높아질 수 있게 함" 인용. 🔑의 "(추가 중합)" 삭제, 대신 p.18 Improved mechanical properties — Additional polymerization: heat, pressure, light 연결 항목 추가.
8. Clinical Procedures 카드(⭐ 5줄·소제목 4·표 하나에 다 몰려 있었음) → **두 카드로 나눔**: ① Surface Treatment — 수복물 내면 Roughening→Silanization→Bonding / 치아 Etching→Priming→Bonding / 계면 비교표(jb=Q23,T23) ② Adhesive Cementation — Dual-cured resin cement·충분한 광조사(jb=Q25,T22,T21). 카드마다 🔑·요지·⚡ 새로(⚡ +2: "에칭 불가→sandblasting·film thickness·box 코너 얇은 한 층", "adhesive = Resin cement / retentive = Zinc phosphate·Polycarboxylate·GI·RMGI(JB 해설)"), p.19 "레진시멘트 등 고려 필요" 연결, 💬는 카드별로(①"주의해야 할 것 한두가지" ②"붙이고 나서 광조사 충분히").
9. F: 23 캡션 "수복물과 치아 두 계면 처리 후 Adhesive Cementation"은 필기 설명이 아님 → 쪽 번호만(원칙 5-9).
10. Q23 ⭐ · JB 그림 메모 말줄임(…) → 원문 전문("중요한 것은, 5번 silane의 사용 (ex. 포세린 프라이머) 사용하지 않으면 치면-bonding은 잘 붙지만 Resin cement와 laminate는 잘 안붙게 됩니다") — JB 25판 p.7 그림 확대 판독.
11. PLV ⚡ "Etched enamel →" → JB 해설 1번 원문 "Pumiced enamel / Etched enamel →".
12. Dual-cured 🔑가 한 덩어리 80자 초과 → ' / '로 나눔(check_lec 80자 덩어리 0).
### annot_VEN.txt
13. T12 A · "H·B·J 흐름과 맞음"(단정) → "같은 방향 — 단 단계 이름·순서는 슬라이드에 명시 없음"으로 완화(p.13 필기·사진엔 palatal plate 먼저만 있음).
14. Q23 M · JB 그림 메모 원문 인용. T23 A · 인용 안에 괄호를 넣은 '수복물 전(처리)' → JB 답 '수복물 전'과 해설 '수복물 전처리'를 구분.
15. Q23·Q25·T21·T22·T23 N · 근거 주제가 지금 강의계획 11주 여인성 강의(기말 범위) `[[INT:3]]` 추가.
### tables_VEN.txt
16. 계면 비교표 crown 열 머리 출처를 "JB T23·T22·Q25 해설"로(시멘트 칸은 T22·Q25 해설 내용) · DCV vs PLV 대합치 칸을 "슬라이드 Advantages 목록의 …"로.
### pred_VEN.txt
17. 교수 예고("전부 객관식 · 넘버링·단답형 안 나옴 · 함정 주의")와 맞지 않게 대부분 "쓰시오"였던 것 → 13→14문항, 9문항을 객관식(옳은/옳지 않은 것)으로 재작성. 함정형 보기: DCV 장점 ⑥ Premature wear · Heavy occlusal force = 상대 금기 · Increased tooth preparation = 단점 · Translucency – incisal edges · 자가중합이어도 광조사 필수. 미출제 Rationale(탄성계수 Enamel 80 ≫ Dentin 14) 1문항 추가. 유형: 짤 변형 5 · 교수 강조 2 · 미출제 7.

## 사용자 확인 필요 (6건)
1. p.3 표의 괄호 파란 숫자(60-70 · 8-14 · 25-40 / 10-20 · 25-68 · 40-60)를 Corresponding material(Feldspathic ceramics / Hybrid composites)의 값으로 읽을지 — 슬라이드에 명시 없음(필기 "세라믹 탄성계수·열팽창계수가 에나멜에 근접, composite 열팽창계수 좀 커서"와는 맞음). 원고는 "같은 파란 글씨"라고만 둠.
2. p.4 막대그래프 Facial enamel 아래 분수 3개 — 원본 PDF 고배율 렌더로도 판독 불가(값 1.15·1.40·2.16만 적음).
3. p.30 필기 "3번과 컨택부위 해부학적 외형 형태 맞춰주기 많이 힘들 수 있다"의 '3번'이 무엇인지 불명 → 원고엔 '3번' 없이 정리.
4. Q23·Q25·T12의 원 근거 강의(2024 이창하 Laminate veneer p.27 · 2024 여인성 Resin Bonded Restoration p.6-7 · 2021 서덕규 전치부 심미수복 p.2)가 받은 자료에 없음 — 있으면 대조해 v=part → ok 가능.
5. questions.md(빌드 전 덤프)에 T12 '연결 강의 PLAN'으로 나옴 — annot는 lec=VEN:9, 주 ⭐도 VEN(PLAN p.17은 짧은 ⭐). 빌드 후 T12가 VEN 카드로 연결되는지 총괄 확인.
6. T11(cervical restoration 퀴즈) 등급 C 유지 권고 — 이 강의·ESTH 자료에 selective etching·finishing·polishing 근거 없음(v=none).

## 평가
- **누락**: 34쪽 전부 이미지 대조 — 슬라이드 항목·표·그림은 모두 들어가 있었음. 빠진 것은 p.1 필기(4Q 안내) 하나 → 추가. p.34(Q&A)만 제외.
- **정확도**: 사실·수치·철자 오류 없음(탄성계수·열팽창·인장강도 6칸, 블록 10종 제조사, 1 mm, 1000 mW/cm², 치아 번호 모두 확인). 필기 짝 어긋남 1(p.9), 해석 삽입 2("(강도가)"·"(추가 중합)"), 필기 아닌 캡션 1 → 고침. 자료 밖 약어 0(check_abbr VEN 0건).
- **⭐**: 7문항 전부 연결, 연도(Q23·Q25 = 24 / T11·T12·T21·T22·T23 = 21·20)·JB 답 원문·나열 전부 일치. T12 등급 표기 오류 수정, T12 ⭐ 10단계 원문화.
- **구조**: 15 → 16카드(임상 과정을 계면 처리 / resin cement 두 카드로). 🔑 모두 짧은 한 줄, 소제목 의미 단위, 비교는 표(본문 표 10 + 비교표 8), ⚡ 34. check_lec ✓(✗ 0 · 빨강 30% 초과 0 · 🔑 80자 덩어리 0 · 빠진 쪽 34만), merge_parts --check 통과.
- **DD1 대비 밀도**: 34쪽에 카드 16 · 항목 94 · 표 10 · 그림 32 (DD1 75쪽 19 · 75 · 4 · 40) — 쪽당 밀도는 DD1 이상. 증례(p.24-32)는 수업대로 판단 이유 위주로 짧게 묶여 있어 적절.
