# ⚡ 암기·🎯 요점의 번호 항목 = 슬라이드 원문 풀 워딩(과목 하나 담당, 10-07)

> ⚠ 10-07 사용자 정정 — 긴 문장까지 다 풀면 '복붙'이라 안 됨: **FWBAL_BRIEF.md와 RULES 6이 이김**(짧은 원문만 풀 워딩, 긴 문장은 핵심어 압축).

사용자(10-07 원문): "* 얼굴 평가 * ① Soft tissue * ② Skeletal·dental * ③ static·functioning * ④ Growth·aging 암기 정리에선 넘버링처럼 서술형으로 나오는 항목들을 너가 단어를 압축해서 나열해놓는데, 이런 넘버링 항목들은 피피티 원어 압축하지 말고 써놨으면 좋겠어! 번역된 한국어가 함께 있는건 상관없지만, 위처럼 단어들을 생략하고 축약하는 것보다는 아래처럼 피피티 넘버링 원어가 압축 없이 그대로 나열되었으면 좋겠어. ① Soft tissue ② Skeletal and dental structures ③ Interrelationship between static and functioning positions ④ Growth and aging process 나머지는 그대로! 오로지 넘버링된 내용들에 한해서 압축버전 말고 풀 워딩을 써주는걸로 모든 강의자료 정리본 및 jb의 암기 정리 에서 다 바꿔줘! 너가 최적으로 판단해서 뭔가 서술형 넘버링 나올만한 내용들에 대해서만 풀워딩으로 바꿔주고 다른건 다 너무 좋으니까 그것만 바꿔줘!"

## 대상
- 맡은 과목 `tools/<sid>/lec_*.txt`의 `M:` ⚡ 줄(📖 JB 카드의 ⚡도 이 줄) — 그리고 `tools/<sid>/annot.txt`의 `K:` 🎯 요점 중 `외울 것:`·`답의 뼈대`처럼 ①②③ 나열인 줄.
- **①②③(또는 1. 2. 3.) 번호 항목만.** 그 항목이 **서술형(나열·n가지·단계)으로 나올 만한 것**이면 각 항목을 **슬라이드(또는 JB 답) 원문 그대로 풀 워딩**으로: 사용자 예 ✗ `① Soft tissue ② Skeletal·dental ③ static·functioning ④ Growth·aging` → ✓ `① Soft tissue ② Skeletal and dental structures ③ Interrelationship between static and functioning positions ④ Growth and aging process`.
- 원문 확인: 같은 카드 본문 `-` 줄·표(대개 원문이 있음) → 없거나 의심되면 쪽 이미지 `work/<SID>/mat/<파일>/i/<쪽>.jpg`(Read)·텍스트층 `t/<쪽>.txt`. JB 서술 답이 있는 나열이면 JB 답 원문(`work/<SID>/review/questions.md`)과도 맞춤.
- 한국어 풀이는 원문 뒤 괄호로 붙어 있으면 그대로 둬도 됨(예 `① Soft tissue(연조직)`). 한국어 슬라이드면 슬라이드 한국어 원문 그대로.

## 하지 않을 것
- 번호 항목이 아닌 줄·조각(정의 `A = B`, 짝 `A / B`, 수치, ` · ` 짧은 나열)은 그대로 — "나머지는 그대로!"
- 원래 원문이 짧은 낱말인 항목(슬라이드도 'Hue · Value · Chroma'처럼 낱말)은 그대로. 이미 원문 그대로인 줄도 그대로.
- 원문에 없는 말 넣기·약어 금지(자료에 있는 말만). 항목 순서·개수·라벨·`{r:}`(빨강은 원문 핵심어 쪽으로 옮겨 유지)·카드 순서 바꾸지 않음.
- 플래시카드: 줄 글자가 바뀌면 기록이 넘어가는지 빌드가 비슷함으로 판단 — 라벨·번호·다른 항목은 그대로 두어 비슷함을 지킨다. 바꾼 줄 목록을 보고에.

## 검사
- `.venv/bin/python tools/check_lec.py <SID>` ✗ 0 · `.venv/bin/python tools/check_abbr.py <SID>` 새 약어 0 · ⚡는 `tools/<sid>/lecparse.py`의 render_recall로 렌더해 번호 목록이 그대로 나뉘는지(원문자 앞 낱말이 '항·조·호'·숫자로 끝나면 `, `).
- annot를 고치면 `.venv/bin/python tools/annot_diff.py <SID>`(기준본은 메인이 저장 — --save 하지 말 것)로 A·M·N 빠진 글자 0.
- 빌드·커밋·git stash·브라우저 금지. 맡은 과목의 lec_*.txt·annot.txt 밖 수정 금지. scratchpad 파일 이름은 `<SID>_FW_` 접두어.

## 보고 `work/review_final2/FW_<SID>.md`
바꾼 줄마다: 파일:줄 · 전 → 후 · 원문 근거(쪽). 끝에 건수(⚡ n · 🎯 n). 최종 답 5줄.
