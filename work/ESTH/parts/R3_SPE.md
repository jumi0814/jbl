# ESTH/SPE 독립 검토 — 2회차 (10-03)
검토 범위: 쪽 이미지 24쪽 전부를 1쪽부터 다시 넘기며 자료 → 원고 방향으로 대조(p.8·12·23은 원본 PDF를 2.6배로 다시 뽑아 확인) · t/ 필기 전부 · JB 원본(25판 7·12·13·14·15쪽, 23판 1·13쪽) · Fundamentals 26 p.19·21·24·26·27 · ⭐ 줄을 `lecparse.exam_parts`로 나눠 "화면에 보이는 부분 / 접히는 부분"까지 확인. 고친 파일: `tools/esth/lec_SPE.txt` · `work/ESTH/parts/{annot,tables,pred}_SPE.txt`.

## 1회차(R2) 수정 17건 재대조
자료와 맞음 14건. 덜 된 곳 3건(아래 1·5·7번에서 고침):
- R2-9 "p.8 화살표는 확실한 것만" → 초록 화살표 2개가 빠져 있었음.
- R2-1 반대 짝 표로 바꾸면서 `Lengthening of incisal edge`가 Incisal edge 행으로 옮겨짐(슬라이드는 1) contact의 하위 항목 — tables_SPE와도 달랐음).
- R2-5 S12 주 ⭐의 보기 2)·4)가 JB 원문과 글자가 달랐음.

## 고친 것 (17건) — 카드/파일 · 무엇을 → 어떻게 · 근거
1. **Wider 카드 · S12 주 ⭐** — 보기 2) "…이동 → 넓어보임" · 4) "…근심이동 시 좁아보임"이 JB 원문("이동시킬 경우, 치아가 넓어보임" · "근심이동 시 치아가 좁아보임")과 달랐고, 보기 5개 해설이 접히는 '근거' 한 덩어리(504자)에 묻혀 있었음 → **'22년 객관식 보기 5개' 표**(보기 JB 원문 · ○/× · 자료 근거)로 빼고 ⭐는 답 + 근거 + 함정만. 근거 JB 25판 13쪽, p.4·11·15·18, FUN p.26.
2. **Staining 카드 · R19 ⭐** — 결론("보기 1)만 복원 … 시험에서는 자료대로 판단")이 ⚠ 뒤 ' — ' 때문에 접히는 '근거'(.ex-src) 쪽으로 들어가 있었음(렌더 코드 기준) → ⚠ 줄에 결론을 넣고(FUN ⭐ 문구 "JB 답과 자료가 어긋남 … 실제 정답은 확인 불가"와 맞춤) 근거 나열은 뒤로. JB 해설 인용도 원문 "어둡게(진하게)"로.
3. **Wider 카드 · T15 Staining·Arrangement ⭐** — 한 줄이라 렌더에서 `<Arrangement>`가 'Less prominent wider teeth'의 하위 항목처럼 나옴 → Staining ⭐(Staining 절 아래) · Arrangement ⭐(Arrangement 절 아래) 둘로(JB 글자 그대로). ⚠ 306자 → 122자(슬라이드 문장 재인용 삭제 — 바로 위 본문에 있음).
4. **Wider·Narrower 카드 본문** — 한 줄에 ✓ 2~3개(120~173자)라 목록으로 안 나뉘던 것 → 한 줄에 문장 하나 + 한글 풀이(labial ridge = 순측 융선 · developmental grooves = 발육구 · labially and incisally = 순측·절단 쪽 — JB 22년 보기의 한글 용어와 이어지게). 필기도 한 줄에 사실 하나로. 슬라이드 표기대로 `Place`/`Rotate` 대문자, p.15 `slight concavity…`는 ✓ 없는 이어 쓴 줄, `4) Others`.
5. **Narrower 카드 · Wider ↔ Narrower 한눈에 표** — `Lengthening of incisal edge`를 Contact 행으로 되돌림(p.18 1)의 하위 항목), Contact 행에 `mesial and distal surface more convex` 추가, 행 이름에 슬라이드 번호 1)~4).
6. **Narrower 카드 · ⚠ JB 표 차이** — 574자 한 줄(①~④) → 소제목 + 3줄. Wider 쪽 차이는 Wider 카드 ⭐ ⚠와 겹쳐 안내 한 줄로 줄임(카드 사이 중복 제거).
7. **Treatment Sequence 카드(p.7-8)** — 빠진 화살표 2개 추가(1 `Tentative diagnosis and treatment planning` → 3 `Treatment plan and options` · 3 Consultation–4 Initial therapy–5 Diagnostic phase를 잇는 초록 선), 276자 한 줄 → 9줄(렌더가 ' · '에서 "Diagnostic wax-up → 3의 …"로 잘못 쪼개던 것도 해결), Shade documentation이 1·2·7·8단계에 있음 명시. 이 강의 고유 내용(환영 적용 3단계 · 💬 initial therapy)을 9단계 표 앞으로.
8. **🔑** — Wider·Narrower: 렌더가 "Horizontal avoid ·" / "Vertical incorporate → contact … · 양쪽 1/3 darker ·" / "linguoversion"으로 어색하게 끊김 → `Shaping: … / Staining: … / Arrangement: …` 라벨 줄(서술 답의 뼈대). 카드 1: '그 사이를 메우는 것'(슬라이드 그림 해석) → 필기 정의 "마음대로 안 될 때 … 마지막 단계에서 조정".
9. **⚡** — Wider 3 → 4줄(T15 서술 답 순서 그대로: 원칙 · 1)2) · 3)4) · Staining/Arrangement — 빠져 있던 Rounded incisal edge·incisal notch·reduction in the reflective surface·slight concavity 추가, 첫 줄은 JB 카드 미리보기에 쓰여 짧게). Narrower에 Lengthening·Widening·horizontal lines, Shorter/Longer는 Shaping / Staining / Arrangement로 나누고 `converge gingivally`·`reopen incisal embrasure` 추가.
10. **Surface Characterization 카드** — Fundamentals p.26 연결 2줄 → Horizontal ↔ Vertical 표(슬라이드 · 필기) + 26 필기 "역이용: 옆으로 넓은 치아는 수직선을 강조하면 좁아 보이고, 수직으로 긴 치아는 수평선을 강조하면 짧아 보일 수 있다"(이 강의 Wider·Longer의 원리 — 원고에 없었음). teflon tape 137자 → 뜻 · 좋은 점 · 주의 3줄.
11. **Review 카드(p.12)** — '✓ … ✓ …' 한 줄 3개 → ①~⑤ / ①~⑥(자동 목록 · FUN 원고와 같은 꼴), '기억해 둘 것' + 💬를 앞으로(🔑와 같은 순서).
12. **Transition Line Angle 카드(p.23)** — #21/#11 비교 168자 → 표, 긴 줄 5개를 사실 단위로 나눔, 소제목 '충전 전에' → '진단 단계·왁스업·목업에서 거의 다'(필기 결론), 빠졌던 "filling 할 때부터 고려 — 미세하게 조작해서 filling하는게 쉽지 않으므로" 추가.
13. **내부 문항 id 노출** — 원고 본문·머리말·소제목에 S12·R19·T15·Q21이 글자로 보였음(승인 원고 DD1·FRC 본문에는 없음) → '22년 12번'식으로, Q21 ⭐에는 `{jb:S12}`·`{jb:R19}` 칩. annot·tables도 같이('FUN Q11'·'part'·'SPE' 같은 내부 표기 포함).
14. **! JB 경향** — "이창하 교수가 … 처음 강의"(JB에 없는 말) → 23판 학습부 멘트대로 "서덕규 교수가 맡았던 부분을 이창하 교수가 새로운 자료로 강의".
15. **pred** — Wider/Narrower contact 문제(T15 답·1번 문제와 겹침) → 교수 강조 p.12 "기억해둬야 할것들" 4가지로 교체(짤 변형 6 · 미출제 6 · 교수 강조 3 = 15문).
16. **F: 19** 캡션 추가(필기 "어두운 색을 cervical, 밝은 색을 수평적으로").
17. Narrower `Widening of the reflective surface – make the tooth appear wider`에 ==형광==(JB 표에 대소문자만 다르게 있음 — 같은 카드의 Flat/flat과 같은 기준).

검사: `check_lec.py ESTH SPE --also R19,S12,Q21,T15` ✓(오류 0 · 경고 0 — 카드 12 · 항목 131 · 표 12 · ⭐ 11 · 그림 21 · 암기 35 · 쪽 1~24, 🔑 80자 넘는 줄 2 → 1) · `check_abbr.py ESTH` SPE 0 · `check_eyears.py ESTH` 0 · `merge_parts.py ESTH --check` 통과 · ⭐ 11줄 모두 구조화 렌더(연도 = 배지: T15 21·20·18 / S12 22 / R19 23 / Q21 24). 빌드·브라우저 확인은 하지 않음(총괄 몫) — 렌더는 lecparse 함수로만 확인.

## 사용자 확인 필요 (4건)
1. **R19** — 1회차와 같음: JB 답 1)은 자료(SPE p.11·19, FUN p.19·27)와 반대, 보기 1)만 복원 → v=diff · ⚠ 유지.
2. **p.23 필기 "#21 distal line angle 보통보다 상당히 distal 쪽으로 위치시킴 - 넓어진걸 상쇄"** — p.13 필기(line angle을 안으로 모으면 좁아 보임)·p.23 위쪽 필기(#11은 distal로 옮겨 좁아 보이게)와 방향이 반대로 읽힘. 받아쓰기 문제인지 자료로는 알 수 없어 원문 그대로 두고 해석을 붙이지 않음.
3. **Q21 v=part · T15 v=part** — 1회차 판단 유지(바꾸려면 annot 머리줄 v만).
4. **p.8 초록 선** — 3 Consultation · 4 Initial therapy · 5 Diagnostic phase 세 곳 모두 화살촉이 있어 방향을 정할 수 없음 → SPE는 "세 단계 제목을 이음"으로만 씀.

## 총괄에게
- `tools/esth/lec_SPE.txt`는 12:59 중간 저장 커밋(f3c857c)에 이 2회차 수정본이 이미 들어가 있음(내가 커밋한 것 아님 — HEAD와 작업본 차이 0). parts 3개는 `merge_parts.py ESTH`로 합쳐야 반영.
- PLAN 원고 68행은 같은 초록 선을 "3 Consultation → 4 Initial therapy와 5 Diagnostic phase로"라고 방향을 정해 씀 — 위 4번과 맞출지 결정 필요(PLAN은 고치지 않음).
- 다른 강의에도 내부 문항 id가 화면 글자로 나옴(예: lec_FUN 6행 "Q06 24·23·22·21·20", annot_VEN 7줄 · FUN 5줄 · COL 4줄) — 과목 공통으로 정리할지.
- T15 주 ⭐(Shaping) 답 목록: 머리 줄 끝에 ' /'가 남고 "2) Rounded incisal edge, incisal notch" 아래가 'pleasing effect: incisal diastema…'로 쪼개짐 — 원고가 아니라 `render_block` 자동 구조화 결과(JB 글자를 지키려 원고는 그대로 둠).
- questions.md 기준 R19·S12는 이미 SPE 카드로 연결됨(build4 Q2CARD가 annot lec 우선) — FUN 카드 머리의 `jb=R19`·`jb=S12`는 그대로 둬도 됨.

## 평가
- 누락: 슬라이드 글자·표 칸·수치는 1회차 뒤 거의 완전. 2회차에서 찾은 빠진 것 = p.8 화살표 2개, p.23 필기 한 구절, FUN p.26 필기 한 문장(역이용), ⚡의 T15 답 항목 4개.
- 정확도: 사실 오류 0. 글자가 원문과 달랐던 곳 = S12 보기 2)·4), JB 멘트 '처음', 반대 짝 표의 Lengthening 행 위치.
- ⭐: 4문항 11줄 — 답은 JB 원문 낱말 그대로, 답·⚠ 줄에 결론이 오도록 정리. 22·23·24년이 같은 유형이라 보기 단위 판정표를 둠.
- 구조: 카드 12장 · @G 4 · @MAP 8단계 유지. 가장 많이 나온 Wider 카드가 "원칙 → 1) → 2) → 3) → 4) → Staining → Arrangement" 순서로 한 줄씩 읽히고, 🔑·⚡이 서술 답 뼈대(Shaping/Staining/Arrangement)와 같은 꼴.
- DD1 대비 밀도: 24쪽에 항목 131 · 표 12 · 그림 21 · 암기 35(DD1 75쪽 · 항목 75) — 줄 길이도 DD1 수준으로 맞춤. 새 문제는 위 17건이 전부이고, 나머지(카드 1·2·3·6 본문, 비교표 6개, 예상문제 14개, 대조 4문항의 인용·쪽·판정)는 다시 대조해 고칠 것 없음.
