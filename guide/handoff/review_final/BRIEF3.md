# 내용 최종 점검 2차 — 과목 하나 담당 (10-04 클라우드)

사용자(10-04): "정말 최종최종 강의자료 정리본 및 족보 based jbl 프로그램 … 공부 자료면에서의 정리, 정리표 및 비교표로의 정리, 핵심 암기, 필기 강조된 파트, 시험문제 출제한다고 한 파트, 예상문제, 26년도 되면서 추가된 강의자료, jb문제 등 모든 면에서 누락이나 오류 없이 가장 최적으로 효과적, 효율적으로 공부할 수 있는 형태인지 면밀히 검토 … 개선점들 모조리 다 고쳐서".
1차 점검(guide/handoff/review_final/BRIEF2.md — 강의별 원고 역대조·⭐↔JB)은 끝났다. **2차는 '공부 도구' 쪽: 정리표·비교표·예상문제·⚡ 암기·강조/시험 예고 쪽의 반영**을 과목 전체로 본다.

## 먼저 읽기
`CLAUDE.md` 절대 규칙·정리본 형식 · `guide/정리본_원칙.md`(사용자 표시 보존 포함) · `tools/SPEC.md`의 lec·tables·pred 문법 절 · `guide/과목노트_<SID>.md` · 1차 보고 `work/review_final2/R_<SID>_*.md`(이미 고친 것)

## 대상(맡은 과목 `<SID>`, 이것만 고친다)
- 원고 `tools/<sid>/lec_*.txt` · 비교표 `tools/<sid>/tables.txt` · 예상문제 `tools/<sid>/pred.txt` (annot.txt는 보고만)
- 원본: `work/<SID>/mat/…/{i,t,o}` (키 ↔ 파일 `work/<SID>/review/materials.md`), 문항 `work/<SID>/review/questions.md`

## 볼 것
1. **시험 예고·강조 쪽 전수**: 원고 `!` 머리말·📣 칸·필기의 '시험'·'강조'·'중요'·★ 쪽 목록을 만들고, 쪽마다 ① 원고 카드에 내용 ② 💬(P:) 또는 ⭐ 줄 ③ ⚡ 암기 줄 ④ 예상문제(pred)가 있는지. 없는 것을 채운다(pred는 강의자료 문장으로만, 답 정확히).
2. **정리표(sum)·비교표(tables)**: 표 칸이 원고·슬라이드와 같은가(수치·용어·순서), 카드에 있는 '나란히 비교할 것'(A vs B, 종류별 특징, 분류)이 표로 없으면 표를 덧붙임, 표 머리·행 이름이 한눈에 읽히는가, 26년도 반영 강의(DX·EXT·INL·ADH·GRAFT·PRO·MAND·ACU)의 표 쪽 번호·내용이 26과 맞는가.
3. **예상문제**: 문제·답이 원고·슬라이드와 맞는가(틀린 답 0), 기출 짤 변형·미출제 강조·교수 예고가 고르게 있는가, 같은 문제 중복 제거, 26 새 내용 반영.
4. **⚡ 암기(M:)**: 모든 카드에 2~3줄, 시험 답을 떠올리게 {r:} 빈칸, 카드 본문과 수치·용어가 같은가.
5. **JB ↔ 정리본**: 2회 이상 출제 문항이 정리표·비교표에도 보이는가({jb:ID} 칩), ⭐ 문구가 JB 답과 어긋나지 않는가(샘플 점검).
- 사용자 표시 보존: 카드 나누기·합치기·제목 바꾸기 금지, 문장은 덧붙이기 > 낱말 고치기 > 지우기. 표·예상문제는 덧붙이기 위주.
- 자료에 없는 사실 금지 · 화면에 문항 id 글자 금지(칩 {jb:ID}는 가능) · 판(JB 파일) 연도 표시 금지.

## 검사(✗ 0)
`.venv/bin/python tools/check_lec.py <SID>` · `.venv/bin/python tools/check_eyears.py` · `.venv/bin/python tools/check_abbr.py <SID>` · `.venv/bin/python tools/split_parts.py <SID> --force` 다음 `.venv/bin/python tools/merge_parts.py <SID> --check`(tables·pred 형식 확인용 — 확인 뒤 parts는 지워도 됨) · 빌드·커밋 금지.

## 보고 `work/review_final2/R3_<SID>.md`
고친 것(파일·위치·무엇·근거 쪽) · 덧붙인 표·예상문제 수 · 사용자 확인 필요(자료로 못 정함) · 평가. 최종 답 5줄.
