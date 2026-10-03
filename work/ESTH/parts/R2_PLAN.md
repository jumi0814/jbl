# ESTH/PLAN 독립 검토 (10-03)
검토 범위: 26 자료 45쪽 이미지 전부 + 텍스트층 · 25판(PLAN5) 45쪽 텍스트층·이미지 차이 비교(25에만 있는 줄/표시 0 — 확인) · 담당 문항 R20·U02·T16(A)·T10·T14·U01·T17(C) + T12 짧은 ⭐ · JB 원본 쪽(23판 p.17 · 24판 p.17) · 다른 강의 자료 전체 검색(putty·layering·5급·erosion·bevel 등).

## 고친 것 (20건)
### tools/esth/lec_PLAN.txt
1. `!` JB 경향 2줄 → 다시 씀. 원래 "현 교수 문항은 R20 하나"였고, T16은 '참고 C'에 들어 있어 지금 등급(T16·U02·T12 = A, T10·T14·U01·T17 = C)과 맞지 않았음. 이제 A 문항(R20·U02·T16·T12 주 VEN)과 C 문항을 따로 적고, U02·T16의 JB 답 중 자료에 없는 부분도 밝힘. 근거: assemble.py TIER, questions.md.
2. 9단계 카드 🔑에 R20 답이 없었음 → `Diagnostic phase(mock-up·provisionalization)`를 넣음(p.8).
3. 9단계 도표 화살표 3곳을 p.8 이미지로 다시 그려 보고 고침.
   - "3 Treatment plan → 4 Initial therapy"를 다음 둘로 고침: 3 Consultation(머리글) → 4·5 / 3 Treatment plan and options → 5 Diagnostic mock-up.
   - "4 → 5" 화살표는 도표에 없어서 지움. 실제로 있는 건 5 Provisionalization → 6.
   - 7↔8 사이 화살표를 Work Authorization Form · (Master cast) → Master cast · 8 Restoration → 7 Restoration · Presentation of progress → 9로 나눠 적음.
4. 9단계 카드에 p.7 필기 U:를 넣음: "치아 하나면 이렇게까지 안 해도 되지만 6전치·하악까지 전체 심미 치료할 때 systemic 접근 필요".
5. 첫 카드: "④ Esthetic Rehabilitation ⑤ Treatment Outcome"이 한 줄에 사실 두 개 → 두 줄로 나눔. 제목만 있는 간지 F: 2와, p.9와 목록이 같은 F: 10은 지움.
6. Know the patient에 p.11 필기 "캐릭터가 독특하신 환자분들은 대기실에 앉아있는 것만 봐도 알 수 있다"를 넣고, p.8 1단계 필기와 이어 놓음.
7. Inform patient에 p.13 필기 머리말 "환자에게 잘 알려주고 설득하고 협상해야 함"을 넣음(원래 빠져 있었음).
8. Diagnostic wax-up 카드 머리에서 `jb=T12`를 지움. build4는 강의 순서대로 처음 나온 jb= 카드를 주 카드로 고르기 때문에(정렬이 안정적) T12의 📖 정리본 칩이 VEN이 아니라 PLAN으로 가고 있었음(questions.md '연결 강의 PLAN'). 짧은 ⭐(E:)는 그대로 둠.
9. p.21 위 도식의 파란 **APR** 부위가 빠져 있어 넣음. 그림 속 글자이고, APR·APT 풀이는 자료에 없다고 밝힘.
10. 심미 차트 표(p.24를 크게 보며 확인)에서 빠진 주소·전화(집·직장·핸드폰) 칸을 채움.
11. 54Y/M 카드:
    - 머리 `jb=`에서 U02를 지움(위와 같은 이유로 U02 주 카드가 Case 2가 아니라 54Y/M로 잡히던 것을 바로잡음).
    - 태그를 '치경부 결손 문항 참고' → 'erosion 원인·치료계획'으로 바꿈.
    - 🔑에 원인(산성 물질이나 음식 / 마모·교모라면 구치부)을 넣음.
    - **T16 ⭐를 A 문항용으로 다시 씀**: JB 답 전문 → 이 강의로 쓰는 틀(원인 p.25 → 옵션 3개 장단점 p.26-28 → 2번 선택·술식 p.29) → ⚠ 자료에 없는 항목(하악 lingual·위산 역류·의과적 refer)과 JB 근거 쪽(서덕규 p.5).
12. Case 1:
    - p.32 "현재 파노라마"는 해석이 들어간 말 → "파노라마(필기 없음)"으로 고침.
    - T17 ⭐에 '심미적 문제' 찾는 기준으로 p.7 심미 추가 PI 7항목을 연결함.
    - JB 해설 인용의 라벨을 '함정' → '참고'로 바꾸고 원문 그대로 적음.
13. Case 2 U02 ⭐의 ⚠: 원래 "shade layering·putty index는 자료에 없음"이었으나, Direct veneer 강의에 관련 필기가 있음 → `[[VEN:9]]` "PVS custom matrix from the wax-up model" · `[[VEN:11]]` "cervical shade, body shade, translucent한 enamel shade 순으로"를 넣음. 자료에 없는 것은 '상아질 변색 → full veneer crown'과 '큰 힘 주의'뿐.

### work/ESTH/parts/annot_PLAN.txt
14. **T14: none → part, lec=VEN:8.** VEN p.8 필기에 정답 3)의 이유가 있음(이미지로 확인): "5급 와동 수복시에도 말했을 것. 거의 파져서 오니까 와동형성 안해도 되지 않냐고 하는데, 표면 처리 해줘야 한다" · "표면 아무것도 안해도 되는건 아님". 나머지 보기 1·2·4·5는 근거 없음 그대로.
15. U02:
    - M:의 p.28 Disadvantage에서 빠진 "Intentional root canal treatment"를 채움.
    - VEN p.9(putty index), p.11(shade 순서), p.13(10세 미만 외상 환자는 간접 수복 나이가 아님 — 나이에 따른 선택)을 주변부로 넣음.
    - A: '자료에 없는 부분'을 위 내용에 맞게 고침.
16. T16:
    - "옵션(2번 선택)이 JB의 '보존적 수복 치료'에 해당"은 틀림 → 보존적인 것은 옵션 3 필기 "보존적으로 치료하는 것"(p.28)이라고 고침.
    - M:에 VEN p.14 erosive·abrasive 증례(직접 수복 vs 라미네이트를 고르는 근거)를 넣음.
    - N:의 내부 메모 "R_PLAN.md에 A 상향 검토 권고"를 지우고 A 근거 문장으로 바꿈.
17. T10:
    - N:의 내부 메모 "등급 C 유지 권고(R_PLAN.md)"를 지움. 사이트에 그대로 보이는 칸이라서.
    - "22~24년 시험에 안 나옴"은 확인할 수 없는 말 → "22년 이후 칸에는 다시 실리지 않음"으로 고침(JB 전 판을 검색해 확인).
    - M:에 FUN p.16(abrasion → gingival level apical 이동)과 VEN p.14 관련 필기를 넣음.
18. U01:
    - N:의 내부 메모를 지움.
    - M:에 관련 원칙만 넣음: VEN p.17 Posterior Indirect Composite Resin 금기 "Impossible isolation & moisture control" + 필기 "bleeding, moisture control 안되면…", INT p.4 "5급은 … 심미적인 고려가 필요함".
    - bevel 판단 자체는 자료에 없어서 v=none 유지.

### work/ESTH/parts/tables_PLAN.txt · pred_PLAN.txt
19. 비교표 1개를 더함: "Present illness — 차트 7칸 · 일반 PI · 심미 추가 PI"(p.4·6·7, 심미 차트 p.24 메모 포함). 7개 → 8개.
20. 예상문제:
    - 어색한 문구 "composite mock-up으로 결정하거나 하는 것"을 "Composite mock-up 아래에 제시된 항목 4가지"로 바꿈.
    - 미출제 1문항(Systemic Patient Management 5 + Communication 2, p.3)을 더함. 13개 → 14개.

검사:
- `check_lec.py ESTH PLAN --also …`: ✓ (✗ 0 · 경고 0)
- `merge_parts.py ESTH --check`: 통과
- 내 parts 약어 검사: 0
- E: 9줄 모두 exam_parts로 나뉨을 확인. U02·T16·T10·T12 JB 답은 공백을 빼고 글자를 비교해 원문과 같음.
- ⭐ 연도는 questions.md '출제'와 손으로 대조해 일치(R20 23 · U02 20·18 · T16/T10 21·20·18 · T17 21 · T12 21·20).

## 사용자 확인 필요 (6건)
1. T14(C)의 연결 강의를 PLAN에서 VEN으로 바꿈(lec=VEN:8). 근거가 VEN p.8 필기에 있기 때문. VEN 원고의 p.8 카드에 T14 짧은 ⭐를 둘지는 VEN 검토자나 총괄이 정할 일(C라서 필수 아님).
2. check_abbr에서 `APR` 1건이 걸림. p.21 그림 속 글자라 그대로 두었고, 풀이는 쓰지 않음.
3. p.28 옵션 3: 슬라이드 Disadvantage에는 "Intentional root canal treatment"가 있는데, 26 필기는 "현실성은 없지만 근관치료 없이". 원고는 슬라이드를 기준으로 하고 ⚠로 차이를 적어 둠.
4. p.38 26 필기 "치근파절 중에 가장 예후가 안 좋은 것이 치근부의 파절이다"는 뜻이 모호해 원문 그대로 둠.
5. U02·T16 JB 답의 근거는 서덕규 2021 강의(211008 전치부 심미수복 p.2 · 211001 successful cervical restoration p.5)인데 받은 자료에 없음. 그 자료를 주면 ⚠ 부분을 근거로 채울 수 있음.
6. check_eyears.py·check_years.py는 팩을 빌드해야 돌릴 수 있음 → 총괄이 merge·build 뒤에 실행해야 함(손 대조는 일치).

## 평가
- **누락**:
  - 슬라이드 항목·표·그림은 모두 들어 있었음.
  - 빠진 것: 필기 3줄(p.7 6전치 systemic, p.11 대기실, p.13 설득·협상), 도식 라벨 1개(APR), 차트 칸 1개(주소·전화). 모두 채움.
  - 25판에만 있는 내용은 없음(텍스트·이미지로 확인).
- **정확도**:
  - 사실이 틀린 곳: p.8 화살표 3곳(고침).
  - 해석이 들어간 곳: p.32 '현재', T16 annot의 '보존적=옵션 2'(고침).
  - 나머지 수치·철자·인용(23mm · 1-2mm · 4년 · 10년 · 1 – 2 wks · reposioning/Extration 원문 철자)은 쪽 이미지와 같음.
- **⭐**:
  - A 문항 R20·U02·T16·T12는 모두 연결됨.
  - 주 카드 연결이 잘못 잡히던 2건(T12 → PLAN, U02 → 54Y/M)은 jb= 정리로 바로잡음(빌드 뒤 '연결 강의'로 확인 필요).
  - T16은 A용 서술 답 틀로 강화함.
- **구조**: 카드 14장의 의미 단위가 적절함(틀 3 · 초진 관리 2 · 진단 단계 4 · 증례 5). 비교할 것은 모두 표로 되어 있음(본문 표 10 + 비교표 8). 🔑은 120자 안쪽, 빨강 30% 경고 없음, 필기 문단 없음.
- **DD1 대비 밀도**: DD1은 카드 19 · 항목 75 · 표 4 · 그림 40 · 75쪽, PLAN은 카드 14 · 항목 104 · 표 10 · 그림 41 · 45쪽. 쪽당 밀도는 DD1 이상이고, 형식(요지 → 🔑 → 소제목 → 항목·표 → ⭐ → 그림 → ⚡)도 같음.
