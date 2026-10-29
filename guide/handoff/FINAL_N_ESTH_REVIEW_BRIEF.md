# ESTH 최종 N제 독립 검수(10-29 밤 — 시험 오늘)

작성 기준 = `guide/handoff/FINAL_N_ESTH_BRIEF.md`(먼저 전부 읽기) · 검수 항목 = `guide/handoff/FINAL_N_REVIEW_BRIEF.md` '문항마다' 1~5 · '강의마다' 그대로(경로만 ESTH: 파일 `work/ESTH/final/final_<담당>.txt` · 쪽 이미지 `work/ESTH/review/materials.md` · 문항 `work/ESTH/review/questions.md`). 당신은 작성자가 아니다 — 작성 보고(R_<담당>.md)를 믿지 말고 쪽 이미지·원고·JB로 직접 확인한다. 사용자는 오늘 시험 직전 이 N제만 본다 → **틀린 답·정답 둘·애매한 선지 0이 최우선**, 그다음 짤 축 누락 0.

더 볼 것(ESTH):
- 100% 객관식 5지 · 안진수 COL 문항·슬라이드 0(이창하 색 Q13·P20 축은 @BOOK에 있어야 함 — BK 담당만).
- 해설 = PRED_EXPL1029_BRIEF 꼴: 줄마다 `번호 ○/× · 개념 이름 — 핵심 한 줄` · 틀린 선지 '→ 보기의 「…」가 틀림' · 개념 이름만 있는 줄·문장만 옮긴 줄 0 · ⚠ = '바른 것 vs 함정' · `🔑 개념:` ≤2줄 · 너무 길지 않게.
- 자료에 없는 말·약어·Claude 지식 0 · 보기·답 속 해 = 배지의 해만 · BOOK은 교과서 쪽 이미지에 있는 글만.
- 시간: 약 20분 — 고칠 것은 바로 고치고(같은 파일), 더할 것은 가치 높은 짤 축 누락만.

검사 `.venv/bin/python tools/pred_check.py ESTH --file <파일>` ✗0 · 다른 파일 수정·빌드·커밋 금지 · 보고 `work/ESTH/final/V_<담당>.md`(짧게: 고친 것 — 무엇을 왜·근거 쪽 · 더한 것 · 확인 필요) · 최종 답 4줄(검수 수·고친 수·더한 수·확인 필요).
