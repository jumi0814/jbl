# 담당자(서브에이전트) 지시문 틀 — 그대로 복사해 `<…>`만 채워서 Agent로 보낸다

공통 머리(모든 담당 지시문 맨 앞에 붙임):
```
저장소 /home/user/jbl. 파이썬 .venv/bin/python. 보고는 한국어.
먼저 읽기(전부): CLAUDE.md 절대 규칙·정리본 형식 · .claude/skills/jbl-update/RULES.md(최종형 — 처음부터 이 모양으로) · guide/정리본_원칙.md · tools/SPEC.md lec·annot·tables·pred 문법 절 · guide/과목노트_<SID>.md · 기준 원고 tools/oms1/lec_DD1.txt.
맡은 파일 밖 수정·빌드·커밋·git stash·브라우저 금지. 다른 담당과 같은 파일을 쓰지 않는다. scratchpad 파일 이름은 '<SID>_<KEY>_' 접두어(공용이라 덮어씀 주의). dump_breaks 결과(work/review_breaks/<SID>.md)는 다른 담당이 덮어쓸 수 있으니 실행 직후 바로 읽는다.
자료: 강의 키 ↔ 파일·쪽 이미지 = work/<SID>/review/materials.md · 원본 work/<SID>/mat/<파일id>/{i,t,o}/ (그림·표·필기 쪽은 i/ 이미지를 Read로 직접 본다) · 문항 = work/<SID>/review/questions.md(머리줄 '출제' = 확정 연도).
최종 답은 5줄(자세한 것은 보고 파일에).
```

## B1 작성 — 26년도 갱신(기존 강의, 사용자 표시 있음) · 강의 하나
```
<공통 머리>
과목 <SID> 강의 <KEY>(26 파일 = 키 <KEY>, 25 = 보조 키 <KEY>5). guide/handoff/UPD26_BRIEF.md 그대로 하되, 고치거나 덧붙이는 모든 줄은 RULES.md 최종형(카드 본문·⭐·🔑/⚡ 라벨·구조·`/`·`·`·들여쓰기·표·빨강·그림 F: 25 필기 병기 규칙·@TIP 갱신)으로 쓴다.
26이 메인, 25는 참고. 26 필기의 강조·시험 메모는 💬/⭐/⚡/예상문제 후보까지 보고에.
사용자 표시 보존(RULES 12): 카드 나누기·합치기·제목 바꾸기 금지, 문장은 덧붙이기 > 낱말 고치기, ⚡ 옛 낱말은 새 줄 안에.
쓸 것: tools/<sid>/lec_<KEY>.txt · work/<SID>/upd26/<KEY>_map.json · 보고 work/<SID>/upd26/R_<KEY>.md
검사: check_lec <SID> <KEY> ✗0 · check_eyears 0 · check_abbr 새 약어 0 · dump_breaks <SID> <KEY> 조각 오류 0 · ⚡는 lecparse.render_recall로 렌더해 확인.
```

## B2 작성 — 새 강의 또는 새 과목(사용자 표시 없음) · 강의 하나
```
<공통 머리>
과목 <SID> 강의 <KEY>. guide/handoff/ESTH_원고_BRIEF.md 그대로(강의 원고 + work/<SID>/parts/{annot,tables,pred}_<KEY>.txt) — 단, 모든 줄을 RULES.md 최종형으로: 🔑/⚡(6절 — 누락 0·짝·라벨·논리 순서·①②③), annot(10절 — K 요점 콜론 라벨, 선지당 A 한 줄, M 라벨, N 연도만), 표(5절), 줄바꿈·들여쓰기(3·4절), 빨강 10~20%(7절), @TIP(2절).
모든 쪽 이미지를 직접 본다(그림만 된 슬라이드가 많음). 작업 메모 work/<SID>/notes/<KEY>.md · 보고 work/<SID>/parts/R_<KEY>.md.
검사: check_lec <SID> <KEY> --also <문항 id들> ✗0 · merge_parts <SID> --check · check_eyears · check_abbr · dump_breaks.
```

## C 독립 검토 — 회차마다 다른 담당 · 강의 하나(파일 = 그 강의 원고 + parts 3개)
```
<공통 머리>
과목 <SID> 강의 <KEY>, 검토 <n>회차. 작성자·앞 회차 보고(<보고 파일들>)를 먼저 읽고 그 수정이 자료와 맞는지 확인한 뒤 남은 문제를 찾아 직접 고친다(억지로 고치지 않음 — 없으면 '새 문제 0').
갱신 강의는 guide/handoff/UPD26_REVIEW_BRIEF.md, 새 강의는 guide/handoff/ESTH_검토_BRIEF.md의 해당 회차 절을 따른다. 회차별 초점:
 1회차 = 자료 → 원고 역대조(1쪽부터 끝까지 이미지) · ⭐ ↔ JB 답 낱말 · 대조 판정·인용·쪽 · 26에서 바뀐 수치·용어.
 2회차 = 쪽 단위 역대조 한 번 더(앞 회차가 안 본 각도) · 학습 효과(🔑만으로 뼈대, ⚡이 답 그대로 떠오르나, 표 머리) · 원고 ↔ annot ↔ tables ↔ pred 일치.
 3회차 = 빨강 비율(카드 ≤30%·평균 10~20%) · 화면 문항 id 0 · 마지막 쪽 훑기 · RULES.md 전 절 대조(특히 6·10절).
고칠 파일: tools/<sid>/lec_<KEY>.txt · work/<SID>/parts/{annot,tables,pred}_<KEY>.txt. 보고 work/<SID>/upd26/R<n+1>_<KEY>.md(새 강의는 work/<SID>/parts/R<n+1>_<KEY>.md) — 고친 것(전→후·근거 쪽) · 사용자 확인 필요 · 평가.
```

## D1 다듬기 — 🔑·⚡ (강의 묶음 하나 · lec 파일의 `=`·`M:` 줄만)
```
<공통 머리>
과목 <SID> 강의 <KEY들>. guide/handoff/review_final/KEYMEM_BRIEF.md(누락·짝·기출·강조 보강, 요약 탭 금지) + KEYMEM2_BRIEF.md(라벨·논리 순서·①②③·= 최소) 둘 다 그대로. 바꾼 강의·카드만이 아니라 맡은 강의의 모든 카드.
보고 work/review_final2/KM2_<SID>_<묶음>.md(카드마다 ⚡ 전→후 줄 수 · 더한 사실 · 낱말 바꾼 줄).
```

## D2 다듬기 — 줄바꿈·번호·들여쓰기 (강의 묶음 하나 · lec 파일의 `-`·`=` 줄 구분 기호만 — D1 뒤에)
```
<공통 머리>
과목 <SID> 강의 <KEY들>. guide/handoff/review_final/BREAK2_BRIEF.md(lec 영역) + NEST_BRIEF.md 그대로. dump_breaks <SID> <키>를 처음부터 끝까지 읽고 RULES 3·4절대로 — 구분 기호·들여쓰기·번호만(낱말 그대로). text_diff로 빠진 글자 0.
보고 work/review_breaks2/R_<SID>_<묶음>.md.
```

## D3 다듬기 — JB 해설 (과목 하나 · annot.txt만)
```
<공통 머리>
과목 <SID> annot.txt(이번에 바뀐 강의의 문항 — 블록 머리 lec=<키> — 전부). 시작 전 `tools/annot_diff.py <SID> --save`는 메인이 해 둠(하지 말 것).
guide/handoff/review_final/JBREAD_BRIEF.md · JBREAD2_BRIEF.md · JBKEY_BRIEF.md · JBTIDY_BRIEF.md를 차례로 다 적용(K 요점·라벨 통일·한 선지 한 줄·보강 필기 합침·`=` 최소). 화면 덤프 work/review_jb/<SID>.md를 처음부터 끝까지 본다.
검사: annot_diff(A·M·N 빠진 글자 0 — 겹친 [[ ]] 칩·K 다시 쓰기는 예외로 보고) · check_eyears · check_abbr. 보고 work/review_final2/TIDY_<SID>.md.
```

## D4 다듬기 — 표·예상문제·시험 예고 (과목 하나 · tables.txt·pred.txt만)
```
<공통 머리>
과목 <SID> tables.txt·pred.txt(이번에 바뀐 강의 k=·@ 블록). 시작 전 text_diff --save는 메인이 해 둠.
guide/handoff/review_final/TABLE_BRIEF.md + TABLE2_BRIEF.md(표) + review_final/BRIEF3.md 1·3번(시험 예고 쪽 전수 → 예상문제, 예상문제 정확도·중복) 그대로. RULES 5·11절.
검사: text_diff(빠진 글자 = 값 오류 정정뿐) · check_abbr · split_parts <SID> --force 뒤 merge_parts --check. 보고 work/review_final2/TB_<SID>.md.
```

## E QA — 사용자 눈 점검 (과목 하나 · 고치지 않고 찾기만, 메인이 담당에게 다시 보냄)
```
<공통 머리>
과목 <SID>. .claude/skills/jbl-update/QA.md 점검표 1~26번을 이번에 바뀐 강의에 대해 하나씩 확인한다. 화면 기준 자료: work/review_breaks2/<SID>.md(`tools/dump_breaks2.py <SID>`) · work/review_jb/<SID>.md(`tools/dump_jb.py <SID>`) · work/review_scan/<SID>.md(`tools/scan_render.py <SID>`) · 스크린샷(메인이 work/_tmp/qa_<SID>_*.png로 둠 — Read).
걸린 것마다: 점검표 번호 · 파일:줄(원고 위치) · 화면 모습 → 고칠 모양 · 어느 담당(B/C/D1~D4) 몫. 보고 work/review_final2/QA_<SID>.md. 고치지 않는다.
```
