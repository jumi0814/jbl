# ESTH/VEN 독립 검토 2회차 (10-03)
대상: `tools/esth/lec_VEN.txt` · `work/ESTH/parts/{annot,tables,pred}_VEN.txt`. 1회차 보고(R2_VEN.md) 17건을 자료와 다시 대조(전부 맞음) → 쪽 이미지 34장을 1쪽부터 역대조(자료 → 원고) · JB 25판 p.7 그림을 원본 PDF 6배로 다시 판독 · p.4 막대그래프 원본 내장 이미지(336×181px) 확인 · questions.md 9문항(Q23·Q25·T11·T12·T14·T21·T22·T23·U02) JB 답 낱말 대조 · build4 주 카드 선택 로직(Q2CARD)·⭐ 구조(exam_parts)·📣 문장 분리(split_note)를 원고에 직접 돌려 확인.

## 고친 것 (19건) — 카드/파일 · 무엇을 → 어떻게 · 근거
### 원고 lec_VEN.txt
1. **Q23의 주 카드가 엉뚱한 카드였음** · Rationale 카드(p.2-4) 머리에 `jb=Q23`이 있어 build4가 Q23의 📖 정리본 카드를 «왜 순측 법랑질을 수복하나»(🔑 Enamel = stiffness…)로 잡고 있었음(questions.md Q23 블록 맨 끝 줄로 확인) → 머리의 `jb=Q23` 삭제(짧은 ⭐ 줄은 유지). 이제 Q23 → «임상 과정 ① 두 계면 처리»(p.23, 전체 ⭐·PLV 층 ⚡). 짧은 ⭐도 실험 소제목 밑에서 '라미네이트 = 에나멜에 본딩' 항목 바로 아래로 옮기고 가리키는 카드 이름을 지금 이름으로.
2. **T14 짧은 ⭐ 추가**(p.8 카드, `jb=T11,T14`) · 21년 객관식(서덕규 퀴즈, 참고) "치경부 결손에 대해 옳지 않은 것" → 3 · 근거 = p.8 필기 "거의 파져서 오니까 와동형성 안해도 되지 않냐고 하는데, 표면 처리 해줘야 한다"·"표면 아무것도 안해도 되는건 아님" · ⚠ 같은 필기가 "삭제량 가지지 않아도 되지만"이라고도 해 preparation을 표면 전처치로 읽을 때만 JB 답과 맞음(annot_PLAN T14·PLAN p.25 짧은 ⭐와 같은 문구). T14 annot가 lec=VEN:8인데 VEN에 ⭐가 없어 📖 카드가 비던 것 해결.
3. **U02 짧은 ⭐ 추가**(p.12-13 증례 카드) · 20·18년 서술, JB 답 2) "전치부 파절의 경우, putty matrix index를 이용하여 enamel shade, body dentin shade, dentin shade의 resin으로 layering"이 p.13 파절 증례·p.9 Layering/PVS matrix와 같은 술식(BRIEF '다른 강의와 걸친 문항'). 주 카드는 PLAN 그대로(annot lec=PLAN — 시뮬레이션으로 확인). ⚠ JB 문항은 55세 / 이 증례는 10세 미만이라 PLV·전장관 나이가 아니어서 DCV.
4. **T12 ⭐ 두 줄 → 한 줄** · 1회차가 둘째 ⭐ 줄에 "근거와 함정"을 따로 두어 → 답 자리에 "근거는 서덕규 2021…"이 답처럼 렌더됐음 → 한 줄로 합쳐 답(10단계 번호 목록) → 근거(접힘) → ⚠ 함정 순으로 렌더(render_exam으로 확인).
5. **⭐ 꼬리 ' — ' 때문에 순서가 뒤집히던 것** · Q23 "⚠ 함정: … — JB 그림 메모"와 T21 "⚠ … — Laminate veneer도"는 ' — ' 뒤가 '설명'으로 분리돼 답 줄 옆에 먼저 붙었음 → ' · '로 바꿔 ⚠ 안에 둠. Q25의 "⚠ JB 해설:"(함정이 아닌데 ⚠) → JB 해설 인용은 근거 쪽, ⚠ 함정에는 retentive type 시멘트·임시접착용만.
6. **본문 {r:} 밀도 1.9% → 13.5%**(19개 → 150개) · 승인 원고 DD1 13.1%·같은 교수 ADH 18.3%인데 VEN 본문은 거의 전부 **굵게**라, ⚡ 자동 빈칸을 켜도 🔑·⚡만 가려지고 바로 아래 본문·표에 같은 답이 그대로 보였음 → 슬라이드 항목 용어·수치를 본문·표에서도 {r:}로(카드별 빨강 6~30%, check_lec 30% 경고 0).
7. DCV 장단점 카드(p.6-7) · "①~⑥ 한 줄 + 필기 풀이 한 줄"(160·139·170자) → 슬라이드 순서대로 한 줄에 하나 + 그 필기(① 보존적 / ② 당일 수복·인상채득·임시치아 생략 / ③ 기공료 / ④ 재료 비용 / ⑤ 에나멜 삭제 거의 없음 / ⑥ 대합치 wear) · 단점 4개도 같은 식.
8. Rationale 카드(p.4) · Relative crown flexibility 한 줄(234자, → 6단계라 번호 '단계'로 렌더됨 — 순서가 아닌데) → 2열 표(Intact·Proximal enamel 값 표기 없음 / 1.15 / 1.30 / 1.37 / 1.40 / 2.16). ⚡에 "Facial enamel 제거 시 최대 2.16". 분수는 원본 내장 이미지가 336×181px라 판독 불가 재확인.
9. p.3 "괄호 숫자·세라믹·composite" 한 줄(134자, 사실 3개) → 3줄.
10. DCV 임상 고려 카드(p.9) · "실제 증례(p.13) … 순측을 쌓음(필기 — 다음 카드)" → 다음 카드는 p.10-11 카드라 틀린 안내 + '순측'은 필기에 없는 말 → "p.13 증례 카드 — 왁스업 후 찍은 퍼티 인덱스로 palatal 쪽 plate를 먼저". ⚡ "prep·bonding" → "prep·에칭·본딩"(JB 보기 G 원문).
11. 증례 카드(p.13) · 술식 한 줄(142자) → ①②③ 3줄, 필기에 없는 "(순측)"·사진 해석 "순측 충전 → 완성"(T12 짧은 ⭐·⚡) → 필기 원문 "그 위에 라미네이트 비니어".
12. 간접 레진 인레이 단점(p.19) · 필기 "여러번 와야"·"비용 더 비싸" 두 줄이 빠져 있었음 → ①~④ 한 줄에 하나로 넣음. 장점 ④(156자) → 본문 + "④의 대비"(포세린 조정 어려움 ↔ 레진 기공 쉬움) 2줄. ⚡ 186자 한 줄 → 장점 3 / 단점 4 두 줄.
13. 계면 처리 카드(p.23) · 본문에 슬라이드 순서 자체(윗줄 Roughening → Silanization → Bonding / 아랫줄 Etching → Priming → Bonding)가 소제목·🔑에만 있었음 → 항목으로. 비교표 crown 열 '사이' 칸 "자료에 없음" → "T23 해설엔 없음 — adhesive type cement = Resin cement(T22·Q25 → 다음 카드)"(tables_VEN과 일치). ⚡에 JB T23 답(etchant · primer · adhesive).
14. Resin cement 카드(p.23) · `U:`(✍ 필기)에 필기가 아닌 강의계획 메모가 있었음 → 항목으로. **adhesive type vs retentive type 표 추가**(JB Q25·T22·T21 해설 — 시멘트: Resin cement ↔ Zinc phosphate·Polycarboxylate·Glass ionomer·Resin-modified glass ionomer / 수복물: Laminate veneer·Maryland bridge ↔ all ceramic·cast gold restoration·metal ceramic restoration, "지금 강의자료엔 없음" 명시) + ⚡ 1줄(T21 답 Maryland bridge가 ⚡에 없었음). 슬라이드 글자("Adhesive Cementation — Dual-cured resin cement — 충분한 광조사!")와 필기를 줄로 나눔.
15. Masking 카드(p.11) · 슬라이드에서 "B: opaque shade"만 파란 글씨인 것 추가. 증례 카드들(p.14·15·27·30·32)의 한 줄에 사실 2~3개 → 나눔(글자는 그대로).
16. `!` 머리말 · p.2 "올해는 세라믹 비중 줄이고 직접 composite veneer" 예고가 '수업 변화'라는 이름이라 📣 상자에 안 뜨고 접힌 출처 줄로 갔음 → '교수님 예고(p.2 필기 — 올해 바뀐 비중)'. JB 경향 한 문장 258자(audit_design 230자 덩어리) → 현 교수 3문항 / U02 겹침 / 근거 강의 없음 → p.23 / 참고 문항(T21~T23·T11·T14) 문장으로 나눔(가장 긴 📣 217자).
### annot_VEN.txt
17. T12 A · 사진 해석("파절 치아 → 퍼티 인덱스(palatal) → 순측 충전 → 완성" — 셋째 사진은 실제로 무엇인지 필기에 없음) → "사진 6장이 화살표 순서로 이 과정을 보여줌". T12 M에 U02(JB 답 2) 원문) 연결, T11 M에 같은 카드의 T14 연결.
### tables_VEN.txt
18. 'Indirect composite resin inlay' 표 · Contra-indication 행이 "이럴 때 레진 인레이(Indication)" 열에 들어가 뜻이 반대로 읽힘 → 행을 빼고 N: 메모로(상대 금기 필기 포함, [[VEN:17]]). 'Masking 층 순서' 표 · 머리 "치면 A → 바깥 E"(그림은 cervical·body·incisal 부위라 안→밖이 아님) → "그림 기호(필기: 이 순서로 씀)", B 행의 추정 칸 "Opacity" 삭제, D·E 행은 연결 근거 필기 쪽 표시.
19. 계면 처리 표에 adhesive / retentive type 분류 N: 추가({jb:T21}이 어느 표에도 없었음) · 삭제 기준 표 N:에 {jb:T14}.
- pred_VEN.txt: 14문항 답을 원고·슬라이드와 다시 대조 — 고칠 것 없음.

## 1회차 수정 재대조
- 17건 모두 자료와 맞음(T12 등급 A · p.9 필기 짝 · "전단력?" 원문 · JB 그림 메모 전문 · Pumiced enamel / Etched enamel · INT p.3 11주 여인성 "레진 접착성 보철물, 도재 라미네이트 비니어, 금속 도재 수복물" 이미지 확인). 다만 6번(T12 ⭐ 두 줄 나누기)은 렌더가 어색해 위 4번으로 다시 고침.

## 사용자 확인 필요 (3건)
1. p.30 필기 "3번과 컨택부위 …"의 '3번' 뜻(1회차와 같음 — 원고엔 빼고 정리).
2. p.3 표 괄호 파란 숫자가 Corresponding material의 값인지(1회차와 같음 — "같은 파란 글씨"로만 적음).
3. Q23·Q25·T12·U02의 원 근거 강의(2024 Laminate veneer p.27 · 2024 여인성 Resin Bonded Restoration · 서덕규 2021 전치부 심미수복)가 받은 자료에 없음 — 있으면 v=part → ok 대조 가능.

## 총괄에게
- 12:59 중간 저장 커밋(f3c857c)에 lec_VEN.txt는 이 2회차 수정본이 이미 들어감. annot_VEN·tables_VEN은 그 뒤에 고쳤으므로 `merge_parts.py ESTH` 다시 필요.
- **다른 6강의도 본문 {r:}가 드묾**(COL 4.5 · FUN 3.1 · INT 3.8 · MAT 2.2 · PLAN 3.8 · SPE 7.0% ↔ DD1 13.1 · ADH 18.3%) — 원고 안내의 "🔑·⚡와 겹치는 본문은 굵게"를 30% 초과 때가 아니라 일괄 적용한 결과. 자동 빈칸이 본문 답을 못 가림 → 같은 손질이 필요한지 판단 필요.
- U02가 VEN 카드에도 ⭐로 걸림(주 카드 PLAN 유지) · T14는 VEN p.8 주 카드 + PLAN p.25 짧은 ⭐.

## 평가
- **누락**: 34쪽 역대조 — 슬라이드 글자·표 칸·수치는 모두 있음. 빠져 있던 것은 p.19 필기 2줄("여러번 와야"·"비용 더 비싸")과 p.11 파란 글씨 강조뿐 → 추가. p.34(Q&A)만 제외.
- **정확도**: 수치·철자 오류 0(탄성계수·열팽창·인장강도 12칸, 블록 10종, 1 mm, 20초·1000, 치아 번호). 필기에 없는 말 2곳("순측"·사진 해석) → 원문으로. 자료 밖 약어 0(check_abbr VEN 0건).
- **⭐**: 9문항 11줄 — JB 답 낱말 일치(Q23 "Bonding resin – Luting composite – Bonding resin - Silane" · Q25 "Resin cement" · T12 "5번 D-F-E-G-H-B-J-A-I-C"+보기 10개 원문 · T23 "수복물 전, etchant, primer, adhesive" · T11 5 · T14 3 · T21·T22 1)), 연도는 questions.md '출제'와 같음(check_eyears 0건). 주 카드: Q23·T23 → 계면 처리 / Q25·T22·T21 → Resin cement / T12 → p.9 / T11·T14 → p.8.
- **구조**: 16카드 유지 · 항목 94 → 128 · 표 10 → 12 · ⭐ 10 → 11줄 · ⚡ 34 → 36. 120자 넘는 본문 항목 17 → 3(사진 목록·실험 설명·Alternative 줄). check_lec ✓(✗ 0 · 경고는 빠진 쪽 34뿐) · merge_parts --check 통과.
- **DD1 대비 밀도**: 34쪽에 카드 16 · 항목 128 · 표 12 · 그림 32(DD1 75쪽 19 · 75 · 4 · 40) — 본문 빨강 밀도도 이제 DD1 수준.
