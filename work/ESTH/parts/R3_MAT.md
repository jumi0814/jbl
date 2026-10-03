# ESTH/MAT 독립 검토 2회차 (10-03)

대상: `tools/esth/lec_MAT.txt` · `work/ESTH/parts/{annot,tables,pred}_MAT.txt`. 방법: ① 쪽 이미지 1~35쪽을 처음부터 넘기며 자료 → 원고 방향으로 역대조(p.10 시편 사진·p.19 주사기·p.20~22 shade wheel·p.30은 원본 PDF를 3~8배로 확대) ② 담당 6문항 JB 답을 questions.md와 낱말 단위 비교 ③ 처음 보는 학생 눈으로 🔑·⚡·표 머리·긴 줄 ④ 원고 ↔ annot ↔ tables ↔ pred 수치·쪽 대조 ⑤ 1회차 수정 11건 재대조.

## 1회차 수정 재대조
- R2_MAT의 11건 전부 자료와 맞음(디스크 순서 = 가운데 두 개 Z350 Dentin·Body / 끝·두 번째 Bulk-fill · JB 해설 원문 인용 · Point 4·Premisa 이름표 · p.24 Light-cure GI 묶음 이름 · p.6 흐름도 11갈래 · tables 층 표 p.10/p.16 분리). 되돌린 것 없음.
- 표 칸(직접 55 · 간접 30 · 적용 와동 9 · special enamel 3 · 제품 20×6 · Z350XT 36 shade · shade wheel 9)도 다시 봄 — 오류 0.

## 고친 것 (17건)
1. **Q18 JB 카드가 엉뚱한 정리본 카드로 연결되던 것** — lec `Opacity vs Translucency` 카드 머리의 `jb=Q18`을 뺌(짧은 ⭐ 줄은 그대로). build4 Q2CARD는 같은 강의 안에서 'jb= 머리에 그 문항이 있는 첫 카드'를 고르므로, p.10 카드(짧은 ⭐)가 p.12 주 카드보다 앞이라 Q18 문제 카드의 📖 정리본·🔑·⚡이 «불투명한 dentin vs 투명한 enamel»(Microhybrid·Bulk-fill 4 mm)로 나오고 있었음(questions.md Q18 블록에서 확인). 고친 뒤 모의 계산: Q18 → «특수 enamel shade 3묶음과 약자»(🔑 약자 목록 · ⚡ XL·OA). 근거: tools/esth/build4.py 64~77행.
2. **영어 뒤 한글 풀이가 거의 없던 것**(승인 형식 '영어 뒤 한글 풀이' — DD1·ADH는 줄마다 있음) — 번역만 붙임(사실 추가 없음): 성질 7 · 판단 요소 6(p.4) / Patient Factors 표 16칸(p.5) / 흐름도 Direct·Indirect·High caries activity·Stress-bearing·Non-stress-bearing + 풀이 한 줄(p.6) / 직접 11·간접 10 Property 이름(p.7·9 — O/X 칸은 손대지 않음) / Opacity·Translucency 머리(p.10) / special enamel 특징 풀이 한 줄(p.12) / Hue and chroma·Translucency, white hue, opalescence(p.16) / Vittra ①②·Streamlined inventory(p.17·18) / high caries risk·base/liner·deciduous 풀이 한 줄(p.24). tables_MAT 직접·간접 표 21줄에도 같은 풀이.
3. **Patient Factors 표 머리** '필요한 것' → '✓ 항목 — 고려·필요한 것' — 1번 'Well-distribution of occlusal loads'는 '필요한 재료'가 아니라 슬라이드의 ✓ 항목. 근거 p.5.
4. **간접수복재 카드** — '직접 표와 다른 줄'(Fluoride release·Esthetics·Short setting time이 빠지고 Cariostatic·Bonding to tooth substance가 들어감, 나머지 8줄 같은 이름) 한 줄 추가 + tables N. 근거 p.7·9(두 표 줄 이름 대조).
5. **Opacity 카드 디스크 필기** — 146자 한 줄에 사실 3개 → 3줄로 나눔, 디스크 나열에 '(왼쪽부터)'. 근거 p.10.
6. **Thickness 카드 ⚡ 추가** — Q27 JB 답 두 쌍 그대로 'Thickness, Saturation(이창하) / Reflectance, Thickness(안진수 — 색 강의)'. 기존 ⚡은 슬라이드 문장뿐이라 시험 답 꼴로 떠올리기 어려웠음. 근거 Q27.
7. **p.6 ⭐(별표)** — 1회차가 '숨은 ⭐'로 사용자 확인에만 적은 것: 텍스트층의 AppleColorEmoji 글리프(쪽 왼쪽 위 [x 31, y −3~10])로, 숨긴 글자가 아니라 MuPDF가 색 이모지를 못 그려 쪽 이미지에만 안 보이는 것(일반 PDF 보기에서는 보임 — FUN p.19와 같은 자리, FUN 원고는 이미 '쪽 머리에 ⭐ 표시'로 반영). → `!` 교수님 강조 줄 끝 + 흐름도 카드 `P:` 한 줄 + 태그 '별표 쪽'으로 중립 반영(무엇을 강조한 것인지 설명 필기는 없다고 적음).
8. **Shade Reference 카드** — 끊겨 있던 줄 "… 상자 표시 / Z350의 shade를 보면(필기)" 정리: 상자(A2D·A2B·A2E + Clear) = 오른쪽 사진의 주사기 4개(라벨 A2 셋 + C 하나)와 같은 조합, 주사기 색 = 표 머리 색 순서. 근거 p.19 사진 확대.
9. **Shade wheel 둘레 글자**(1회차·작성자 '흐려 판독 불가') — 원본 그림을 4~8배 확대해 읽음: Dentin cure time 1.5mm 40 seconds / Body curetime 2.00mm 20 seconds / Enamel curetime 2.0mm 20 seconds → lec 한 줄 + tables 층 표 N. 근거 p.22(p.20도 같은 글자).
10. **Applicable Range 카드** — porcelain 안내 줄(166자, 사실 2개 + 필기) → 2줄.
11. **증례 카드(p.25)** — 'E shade·D shade·T' 읽는 법 한 줄(p.13 Premisa 줄의 세 묶음 Enamel shade·Dentin shade·Translucent shade와 같은 머리글자, D shade가 A2-O) · 사진 11장 순서(술전 → 러버댐 → 술후) · '같은 이유' 줄 121자 → 필기 인용 한 줄.
12. **Customized shade guide(p.30)** — 사진 9장 과정 한 줄(기성 guide → 틀에 레진 → 손잡이에 shade 이름 → 나란히 비교). 필기 "채워넣어 손잡이 달아서"와 같은 내용.
13. **그림 캡션** — F: 줄 전부 쪽 번호뿐이던 것 → 필기에 설명이 있는 21쪽에만 필기 문구로 캡션(쉼표 없음). 글자뿐인 소표지 p.26은 그림에서 뺌(쪽 범위 26-29는 유지).
14. **Q18 판정 근거 보강(슬라이드 글자)** — 'OA = opaque → dentin 쪽'이 필기뿐이었음 → p.16 슬라이드 "Composite for dentin (Hue and chroma / O or Dentin)" · "Composite for enamel (… / Generic or Opalescent)"와 p.25 'D shade A2-O'를 제품 카드 ⭐ · dentin/enamel 카드 한 줄 · annot Q18 M · tables special enamel N · pred 답에 추가.
15. **annot Q27 N 쪽 번호** — "'251010_안진수pf_색 p.80-83'은 COL p.82-83" → JB가 가리키는 파일이 지금 COL 파일 그대로라 p.80~83 네 장(Translucency and Opacity)이고 'Reflectance · Thickness'는 그중 p.82·83. COL p.80·81 문장(Opacity·Translucency·Transparency 정의 / Trnasmittance·Contrast ratio — 슬라이드 철자 그대로)을 주변부 M:으로 추가. 근거 COL 쪽 이미지 80~83.
16. **annot Q17 N** — "2021 칸 13번에 같은 문제" → "다른 판본 2021 칸 13번(괄호 (21,20))"(지금 판 2021 칸이 아님 — questions.md '다른 판본' 2건).
17. **tables·pred 맞춤** — 층 표에 증례 줄(p.25 D shade A2-O / E shade) · pred Q17 짤 변형에 p.25 증례(universal shade만 → 너무 투명 → opaque shade)를 묶음(문항 수 14 유지: 짤 변형 7 · 교수 강조 2 · 미출제 5).

## 사용자 확인 필요 (4건)
1. **shade wheel 둘레 글자 판독** — 그림 원본이 559×476이라 확대해도 흐림. Dentin 1.5mm 40 seconds · Body 2.00mm 20 seconds · Enamel 2.0mm 20 seconds는 p.22에서 읽힘. Translucent(2.0mm 20 seconds로 보임)와 'Translucent*' 각주는 확신할 수 없어 쓰지 않음. 원고의 "가장 불투명한 Dentin만 더 얇게·더 오래"는 이 수치를 비교한 말.
2. **p.6 ⭐의 뜻** — 누가 왜 붙였는지 설명 필기 없음(교수 강조인지 필기자 표시인지 불명). 중립으로만 적음.
3. **한글 풀이 용어** — 번역일 뿐이지만 표기 선택 확인: Low thermal diffusivity = 낮은 열확산 · Radiopacity greater than or equal to enamel = 방사선 불투과성 ≥ 법랑질 · Isolation = 격리·방습 · In vivo performance = 실제 임상 성적.
4. 1회차에서 이어지는 것(변동 없음): Q16 근거 자료 없음(24년도 p.17) · p.6 분홍 글씨 = 약점이라는 해석 · Q18 XL 논란(답 3), 4) 유지).

## 총괄에게 (내 파일 밖 — 고치지 않음)
- 1번과 같은 연결 문제가 다른 강의에도 있을 수 있음. 같은 강의의 여러 카드에 걸린 문항과 지금 Q2CARD가 고르는 카드(1부터 센 번호): INT Q01 → 2 · R04 → 5 / FUN Q06 → 11 · Q11 → 3 · R07 → 10 · T08 → 1 · T09 → 3 · U04 → 1 / COL Q13 → 7 · Q20 → 15 · S14 → 5 / SPE R19 → 7 · S12 → 9 · T15 → 9 / PLAN R20 → 3 · U02 → 13 / VEN Q23 → 1 · T12 → 5. 주 카드가 맞는지 확인 필요(짧은 ⭐ 카드가 주 카드보다 앞이면 그 카드 머리의 jb=에서 id를 빼면 됨).
- `tools/esth/annot.txt`·`tables.txt`·`pred.txt`는 건드리지 않음 — parts 합치기 필요.

## 평가
- **누락**: 자료 → 원고 역대조에서 빠진 슬라이드 글자·표 칸 0. 새로 채운 것은 그림 속 글자 2곳(p.19 주사기, p.22 cure time)과 사진 설명 2줄(p.25·30), p.6 별표. 원고에 없는 필기는 머리말 성격 두 줄뿐(p.3 "재료를 고를 때 어떻게 골라야 하나" → 그림 캡션으로, p.10 "직접 수복할 때 컴포짓 뭘 고를까?" → 넣지 않음).
- **정확도**: 틀린 사실·수치·철자 0. 쪽 번호 오류 1(annot Q27 N) · 판본 표기 1(annot Q17 N).
- **⭐**: 6문항 10줄 — 연도·형식·보기·JB 답 낱말 일치(Q15 1) glass ionomer · Q16 3) castable ceramic · Q17 3번 dentin-body-enamel shade · Q18 3), 4) · Q19 3) Hybrid composite · Q27 두 교수 답 전문). JB 해설 오기 2곳 ⚠ 유지. 문제는 내용이 아니라 연결(1번)이었음.
- **구조**: 카드 16장·분류 6 그대로(나누거나 합칠 곳 없음). 한글 풀이·캡션·긴 줄 분리로 읽기 쉬움 보완.
- **DD1 대비**: 35쪽에 카드 16 · 항목 101 · 표 19 · ⭐ 10 · 그림 31 · ⚡ 36(DD1 75쪽: 19 · 75 · 4 · 19 · 40).
- **검사**: `check_lec.py ESTH MAT --also Q15,Q16,Q17,Q18,Q19,Q27` ✓(✗ 0, 경고 = 빠진 쪽 1·35뿐) · `merge_parts.py ESTH --check` 통과 · `check_eyears.py ESTH` 0건 · `check_abbr.py` MAT는 APS·BPA(p.17 그림 글자)뿐, 새 약어 0 · 표 열 수 일치 · lecparse로 688줄 렌더 오류 없음. 빌드·커밋 안 함.
