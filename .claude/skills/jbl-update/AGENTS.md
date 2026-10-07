# 담당자(서브에이전트) 지시문 틀 — 그대로 복사해 `<…>`만 채워서 Agent로 보낸다

공통 머리(모든 담당 지시문 맨 앞에 붙임):
```
저장소 /home/user/jbl. 파이썬 .venv/bin/python. 보고는 한국어.
먼저 읽기(전부): CLAUDE.md 절대 규칙·정리본 형식 · .claude/skills/jbl-update/RULES.md(최종형 — 처음부터 이 모양으로. 다른 문서와 숫자·규칙이 다르면 RULES.md가 이김, 13절 = 이미 받은 사용자 결정) · guide/정리본_원칙.md · tools/SPEC.md `## lec_<키>.txt 문법` 절 · annot·tables·pred 문법 = RULES 10·5·11절 + guide/handoff/ESTH_원고_BRIEF.md 3절 · guide/과목노트_<SID>.md · 기준 원고 tools/oms1/lec_DD1.txt.
맡은 파일 밖 수정·빌드·커밋·git stash·브라우저 금지. 다른 담당과 같은 파일을 쓰지 않는다. scratchpad 파일 이름은 '<SID>_<KEY>_' 접두어(공용이라 덮어씀 주의). dump_breaks 결과(work/review_breaks/<SID>.md)는 다른 담당이 덮어쓸 수 있으니 실행 직후 바로 읽는다.
자료: 강의 키 ↔ 파일·쪽 이미지 = work/<SID>/review/materials.md · 원본 work/<SID>/mat/<파일id>/{i,t,o}/ — **모든 쪽 이미지를 Read로 직접 본다**(그림·표만 된 슬라이드, 깨진 텍스트층, 촬영본이 많음) · 문항 = work/<SID>/review/questions.md(머리줄 '출제' = 확정 연도 전체).
최종 답은 5줄(자세한 것은 보고 파일에).
```

## B1 작성 — 26년도 갱신(기존 강의, 사용자 표시 있음) · 강의 하나
```
<공통 머리>
과목 <SID> 강의 <KEY>(새 파일 = 키 <KEY>, 옛 판 = 보조 키 <OLD — 보통 KEY5>). guide/handoff/UPD26_BRIEF.md + UPD26_FIG_BRIEF.md(25 필기 강조 쪽 그림 병기·수업이 중간에 끝난 강의 안내) 그대로 하되, 고치거나 덧붙이는 모든 줄은 RULES.md 최종형(카드 본문·⭐·🔑/⚡ 라벨·구조·`/`·`·`·들여쓰기·표·빨강)으로 쓴다.
필기에서 온 본문 조각은 처음부터 `{n:…}`(RULES 9 — guide/handoff/review_final/NOTEMARK_BRIEF.md). 26이 메인, 25는 참고. 26 필기의 강조·시험 메모는 💬/⭐/⚡에 반영하고 예상문제 후보는 보고에.
사용자 표시 보존(RULES 12): 카드 나누기·합치기·제목 바꾸기 금지, 문장은 덧붙이기 > 낱말 고치기, ⚡ 옛 낱말은 새 줄 안에(빠진 정보는 새 M: 줄).
쓸 것: tools/<sid>/lec_<KEY>.txt · work/<SID>/upd26/<KEY>_map.json · 보고 work/<SID>/upd26/R_<KEY>.md('annot·tables·pred 고칠 것' 절 — 검토 1회차가 반영함)
검사: check_lec <SID> <KEY> ✗0 · check_eyears 0 · check_abbr 새 약어 0 · dump_breaks <SID> <KEY> 조각 오류 0 · ⚡는 tools/<sid>/lecparse.py의 render_recall로 렌더해 확인.
```

## B2 작성 — 새 강의 또는 새 과목(사용자 표시 없음) · 강의 하나
```
<공통 머리>
과목 <SID> 강의 <KEY>. guide/handoff/ESTH_원고_BRIEF.md 그대로(그 안의 '⚡ 2~3줄'·🔑 120자·K 없는 A 꼴은 낡음 — RULES 6·10이 이김)(강의 원고 + work/<SID>/parts/{annot,tables,pred}_<KEY>.txt) — 단, 모든 줄을 RULES.md 최종형으로: 🔑/⚡(6절 — 누락 0·짝·라벨·논리 순서·①②③), annot(10절 — v= 판정·A 직접·K 요점 콜론 라벨·선지당 A 한 줄·M 라벨·N 연도만), 표(5절), 줄바꿈·들여쓰기(3·4절), 빨강(7절), #LEC 원래 강의명·@TIP(2절), JB 규칙(0-1절), 필기 구간 `{n:…}`(9절 — 필기에서 온 본문 조각은 처음부터 감쌈).
작업 메모 work/<SID>/notes/<KEY>.md · 보고 work/<SID>/parts/R_<KEY>.md.
검사: check_lec <SID> <KEY> --also <문항 id들> ✗0 · merge_parts <SID> --check · check_eyears · check_abbr · dump_breaks.
```

## C 독립 검토 — 회차마다 다른 담당 · 강의 하나(파일 = 그 강의 원고 + parts 3개)
```
<공통 머리>
과목 <SID> 강의 <KEY>, 검토 <n>회차. 작성자·앞 회차 보고(<보고 파일들>)를 먼저 읽고 그 수정이 자료와 맞는지 확인한 뒤 남은 문제를 찾아 직접 고친다(억지로 고치지 않음 — 없으면 '새 문제 0').
갱신 강의는 guide/handoff/UPD26_REVIEW_BRIEF.md(그 안의 '⚡ 2~3줄'·🔑 120자는 낡음 — RULES 6·10이 이김, ⚡을 줄이지 않음), 새 강의는 guide/handoff/ESTH_검토_BRIEF.md의 일반 절(ESTH 고유의 '다른 강의와 걸친 문항'·3회차 PLAN/MAT 담당 절은 빼고)을 따른다. 회차별 초점:
 1회차 = 작성자 보고의 'annot·tables·pred 고칠 것'을 parts에 반영 · 자료 → 원고 역대조(1쪽부터 끝까지 이미지 — 자료 사실 40개 이상 대조, 보고에 수) · ⭐ ↔ JB 답 낱말 · 대조 판정·인용·쪽(apply_map26이 잘못 옮긴 'JB 참고 p.N'·다른 강의 쪽·25 필기 쪽 되돌리기) · 26에서 바뀐 수치·용어.
 2회차 = 쪽 단위 역대조 한 번 더(앞 회차가 안 본 각도) · 학습 효과(🔑만으로 뼈대, ⚡이 답 그대로 떠오르나, 표 머리) · 원고 ↔ annot ↔ tables ↔ pred 일치.
 3회차 = 빨강 비율(카드 ≤30%·평균 10~20%·항목 절반 이상) · 화면 문항 id 0 · 마지막 쪽 훑기 · RULES.md 전 절 대조(특히 6·10절) · 필기 구간 {n:} 누락·남발(QA 29).
다른 강의에 걸친 문항(교차 ⭐)·같은 그림은 두 강의 문구가 같은지 — 다른 강의 파일은 고치지 말고 보고에 '다른 강의 몫: 파일:줄 · 지금 → 제안'.
고칠 파일: tools/<sid>/lec_<KEY>.txt · work/<SID>/parts/{annot,tables,pred}_<KEY>.txt. 보고 work/<SID>/upd26/R<n+1>_<KEY>.md(새 강의는 work/<SID>/parts/R<n+1>_<KEY>.md) — 고친 것(전→후·근거 쪽) · 다른 강의 몫 · 사용자 확인 필요 · 평가.
```

## D1 다듬기 — 🔑·⚡ (강의 하나 또는 묶음 · lec 파일의 `=`·`M:` 줄만)
```
<공통 머리>
과목 <SID> 강의 <KEY들>. guide/handoff/review_final/KEYMEM_BRIEF.md(누락·짝·기출·강조 보강, 요약 탭 금지) + KEYMEM2_BRIEF.md(라벨·논리 순서·①②③·= 최소) + FWBAL_BRIEF.md(번호 항목: 짧은 원문은 풀 워딩·긴 문장은 핵심어 압축 — 🎯 요점 포함) 모두 그대로 — 숫자(⚡ 줄 수 등)는 RULES 6절. 맡은 강의의 모든 카드.
검사: check_lec <SID> <KEY> ✗0 · ⚡ 줄마다 tools/<sid>/lecparse.py render_recall로 렌더해 라벨이 굵은 머리(b.mlab / klh)로 잡혔는지 · 본문 표의 짝·목록 칸 수 = ⚡ 번호 수 · 낱말 바꾼 줄 목록.
보고 work/review_final2/KM2_<SID>_<묶음>.md(카드마다 ⚡ 전→후 줄 수 · 더한 사실 · 낱말 바꾼 줄).
```

## D2 다듬기 — 줄바꿈·번호·들여쓰기 (강의 하나 또는 묶음 · D1 뒤에)
```
<공통 머리>
과목 <SID> 강의 <KEY들>. guide/handoff/review_final/BREAK2_BRIEF.md(lec 영역) + BREAK3_BRIEF.md + NEST_BRIEF.md 그대로, 규칙은 RULES 3·4절.
덤프: work/review_breaks2/<SID>_lec.md(메인이 D1 뒤에 새로 만듦 — 처음부터 끝까지, 나뉘어야 하는데 안 나뉜 긴 줄도) + `tools/dump_breaks.py <SID> <키>`(원고 줄 ↔ 화면 조각).
고칠 줄: lec의 `-`·`=`·`E:`·`P:`·`U:` 줄(구분 기호·들여쓰기·번호만 — 낱말 그대로) · tables.txt 칸(그 강의 k= 블록, D4 뒤 — 구분 기호만). `M:`은 D1 몫(보지 않음). `{n:…}` 필기 표시는 그대로 — 구분 기호를 바꿀 때 ' / '·①②가 {n:…} 안에 들어가면 {n:}을 조각마다 나눠 감쌈(RULES 9).
검사: text_diff tools/<sid>/lec_<KEY>.txt(빠진 글자 0) · check_lec. 보고 work/review_breaks2/R_<SID>_<묶음>.md.
```

## D3 다듬기 — JB 해설 (과목 하나 · annot.txt만)
```
<공통 머리>
과목 <SID> annot.txt(이번에 바뀐 강의의 문항 — 블록 머리 lec=<키> — 전부). 기준본은 메인이 저장해 둠(--save 하지 말 것).
guide/handoff/review_final/JBREAD_BRIEF.md · JBREAD2_BRIEF.md · JBTIDY_BRIEF.md를 다 적용(라벨 통일·한 선지 한 줄·보강 필기 합침·M 라벨·{r:}). K 🎯 요점은 RULES 10절·JBTIDY 2) 꼴로만(옛 JBKEY의 `정답 = … — …` 예시는 쓰지 않음 — 라벨 통일 절만 참고). 화면 덤프 work/review_jb/<SID>.md와 work/review_breaks2/<SID>_jb.md를 처음부터 끝까지 본다.
검사: annot_diff(A·M·N 빠진 글자 0 — 겹친 [[ ]] 칩·K 다시 쓰기는 예외로 보고) · check_eyears(🎯 요점 연도 포함) · check_abbr. 보고 work/review_final2/TIDY_<SID>.md.
```

## D4 다듬기 — 표·예상문제·시험 예고 (과목 하나 · tables.txt·pred.txt만)
```
<공통 머리>
과목 <SID> tables.txt·pred.txt(이번에 바뀐 강의 k=·@ 블록). 기준본은 메인이 저장해 둠.
guide/handoff/review_final/TABLE_BRIEF.md + TABLE2_BRIEF.md(표) + review_final/BRIEF3.md 1·3번(시험 예고 쪽 전수 → 예상문제, 예상문제 정확도·중복) 그대로, 규칙은 RULES 5·11절. pred의 줄바꿈(BREAK2 jb 영역 — work/review_breaks2/<SID>_jb.md의 예상문제 부분)도.
split_parts는 돌리지 않는다(D3와 동시라 annot 조각이 낡은 채 덮임). 형식은 다음 빌드 로그로 확인.
검사: text_diff tables.txt·pred.txt(빠진 글자 = 값 오류 정정뿐 — 보고에 목록) · check_abbr. 보고 work/review_final2/TB_<SID>.md.
```

## E QA — 사용자 눈 점검 (과목 하나 · 고치지 않고 찾기만, 메인이 담당에게 다시 보냄)
```
<공통 머리>
과목 <SID>. .claude/skills/jbl-update/QA.md 점검표 **전 번호**(지금 1~31 — 새 번호가 생겨도 끝까지)를 이번에 바뀐 강의에 대해 하나씩 확인한다. 화면 기준 자료(메인이 마지막 빌드로 새로 만듦): work/review_breaks2/<SID>_lec.md · <SID>_jb.md · work/review_jb/<SID>.md · work/review_scan/<SID>.md · work/_tmp/full_check.log · 스크린샷 work/_tmp/qa_<SID>_*.png(Read).
덤프는 처음부터 끝까지 본다(보고에 본 덩어리 수). 걸린 것마다: 점검표 번호 · 파일:줄(원고 위치) · 화면 모습 → 고칠 모양 · 어느 담당(B/C/D1~D4) 몫. 보고 work/review_final2/QA_<SID>.md. 고치지 않는다.
```
