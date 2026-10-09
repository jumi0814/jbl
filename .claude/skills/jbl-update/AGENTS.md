# 담당자(서브에이전트) 지시문 틀 — 그대로 복사해 `<…>`만 채워서 Agent로 보낸다

공통 머리(모든 담당 지시문 맨 앞에 붙임):
```
저장소 /home/user/jbl. 파이썬 .venv/bin/python. 보고는 한국어.
먼저 읽기(전부): CLAUDE.md 절대 규칙·정리본 형식 · .claude/skills/jbl-update/RULES.md(최종형 — 처음부터 이 모양으로. 다른 문서와 숫자·규칙이 다르면 RULES.md가 이김, 13절 = 이미 받은 사용자 결정) · guide/정리본_원칙.md · tools/SPEC.md `## lec_<키>.txt 문법` 절 + `## 규칙` 첫 항목({n:…}) · annot·tables·pred 문법 = RULES 10·5·11절 + guide/handoff/ESTH_원고_BRIEF.md 3절 · guide/과목노트_<SID>.md · 기준 원고 tools/oms1/lec_DD1.txt.
맡은 파일 밖 수정·빌드·커밋·git stash·브라우저 금지. 다른 담당과 같은 파일을 쓰지 않는다. scratchpad 파일 이름은 '<SID>_<KEY>_' 접두어(공용이라 덮어씀 주의). dump_breaks 결과(work/review_breaks/<SID>.md)는 다른 담당이 덮어쓸 수 있으니 실행 직후 바로 읽는다.
자료: 강의 키 ↔ 파일·쪽 이미지 = work/<SID>/review/materials.md · 원본 work/<SID>/mat/<파일id>/{i,t,o}/ — **모든 쪽 이미지를 Read로 직접 본다**(그림·표만 된 슬라이드, 깨진 텍스트층, 촬영본이 많음) · 문항 = work/<SID>/review/questions.md(머리줄 '출제' = 확정 연도 전체).
최종 답은 5줄(자세한 것은 보고 파일에).
```

## B1 작성 — 26년도 갱신(기존 강의, 사용자 표시 있음) · 강의 하나
```
<공통 머리>
과목 <SID> 강의 <KEY>(새 파일 = 키 <KEY>, 옛 판 = 보조 키 <OLD — 보통 KEY5>). guide/handoff/UPD26_BRIEF.md + UPD26_FIG_BRIEF.md(25 필기 강조 쪽 그림 병기·수업이 중간에 끝난 강의 안내) + review_final/UPD26MARK_BRIEF.md(25 → 26 바뀐 곳 `{u:…}`·`@UPD` — RULES 12) 그대로 하되, 고치거나 덧붙이는 모든 줄은 RULES.md 최종형(카드 본문·⭐·🔑/⚡ 라벨·구조·`/`·`·`·들여쓰기·표·빨강)으로 쓴다.
필기에서만 나온 조각(본문 `-`·`#`·⭐ 설명·🔑·⚡·요지 `>`)은 처음부터 `{n:…}`(RULES 9 — ✍ 앞에만 · 방법은 guide/handoff/review_final/NOTEMARK_BRIEF.md 할 일 1~3(본문)·NOTEMARK2_BRIEF.md 할 일 1~4(🔑·⚡·요지) — 두 BRIEF의 '이번 대상 아님'·'E: 손대지 않음'·'{r:} 그대로'·'앞뒤 ✍'는 그 회차 한정), 필기 쪽엔 `{r:}`·`==`·`**`를 두지 않음(RULES 7 끝 — 기출 답 근거·교수 강조·정정 함정만 예외). 보고의 'annot·tables·pred 고칠 것'도 같은 꼴로(🎯·표 칸·예상 답의 필기 조각 `{n:}` · 표는 RULES 5 끝 — 전체정리표 모든 주제·★ 기출 전부·비교 축 행·열 빠짐없이·기출마다 N: `변형 대비: …`·빈 칸 `—`). 26이 메인, 25는 참고. 26 필기의 강조·시험 메모는 💬/⭐/⚡에 반영하고 예상문제 후보는 보고에.
사용자 표시 보존(RULES 12): 카드 나누기·합치기·제목 바꾸기 금지, 문장은 덧붙이기 > 낱말 고치기, ⚡ 옛 낱말은 새 줄 안에(빠진 독립 사실은 새 M: 줄 · 기존 줄 머리 아래 이어지는 조각은 그 줄 끝에 ` / ` — RULES 6 '이어지는 내용은 한 줄에'). 26 새 내용이 기존 줄 머리의 이어짐(구내 ↔ 구외처럼)이면 새 `-`·`M:` 줄로 떼지 않고 그 줄에 ` / `로(본문은 머리 줄 + `  - ` 하위).
쓸 것: tools/<sid>/lec_<KEY>.txt · work/<SID>/upd26/<KEY>_map.json · 보고 work/<SID>/upd26/R_<KEY>.md('annot·tables·pred 고칠 것' 절 — 검토 1회차가 반영함)
검사: check_lec <SID> <KEY> ✗0 · check_eyears 0 · check_abbr 새 약어 0 · dump_breaks <SID> <KEY> 조각 오류 0 · ⚡는 tools/<sid>/lecparse.py의 render_recall로 렌더해 확인 · ⚡·본문 줄은 tools/render_line.py <SID> <M|-> --file … --line n으로 머리 아래 ◦ 묶임 확인(따로 떨어진 • 0).
```

## B2 작성 — 새 강의 또는 새 과목(사용자 표시 없음) · 강의 하나
```
<공통 머리>
과목 <SID> 강의 <KEY>. guide/handoff/ESTH_원고_BRIEF.md 그대로(BRIEF 안의 `ESTH`·`tools/esth`·`work/ESTH`·이창하·INT/FUN/PLAN·INT5 예는 `<SID>`·`tools/<sid>`·`work/<SID>`·이 강의로 바꿔 읽음 · 그 안의 '⚡ 2~3줄'·🔑 120자·K 없는 A 꼴은 낡음 — RULES 6·10이 이김)(강의 원고 + work/<SID>/parts/{annot,tables,pred}_<KEY>.txt) — 단, 모든 줄을 RULES.md 최종형으로: 🔑/⚡(6절 — 누락 0·짝·라벨·논리 순서·①②③·이어지는 내용은 한 줄(머리 아래 ◦)), annot(10절 — v= 판정·A 직접·K 요점 콜론 라벨·선지당 A 한 줄·M 라벨·N 연도만), 표(5절), 줄바꿈·들여쓰기(3·4절), 빨강(7절), #LEC 원래 강의명·@TIP(2절), JB 규칙(0-1절), 필기 구간 `{n:…}`(9절 — 본문·`#`·⭐ 설명·🔑·⚡·요지·표 칸·🎯·예상 답의 필기에서만 나온 조각은 처음부터 감쌈, ✍ 앞에만) · 필기 쪽 강조 없음(7절 끝 — REDNOTE_BRIEF 예외 3가지만) · 표(5절 끝 — 전체정리표 `sum=1` = 강의 모든 주제·★ 열이 기출 전부 `{jb:}` · 비교표는 자료의 비교 슬라이드·표 행·열 빠짐없이 · 기출마다 다른 행·반대편·숫자·'아닌 것'으로 물어도 답이 되게 — 모자라면 N: `변형 대비: …` · 빈 칸 `—`; ESTH_원고_BRIEF 3번 tables 꼴보다 이것이 이김).
작업 메모 work/<SID>/notes/<KEY>.md · 보고 work/<SID>/parts/R_<KEY>.md.
검사: check_lec <SID> <KEY> --also <문항 id들> ✗0 · merge_parts <SID> --check · check_eyears · check_abbr · dump_breaks · ⚡·본문 줄은 tools/render_line.py로 머리 아래 ◦ 묶임 확인(따로 떨어진 • 0).
```

## C 독립 검토 — 회차마다 다른 담당 · 강의 하나(파일 = 그 강의 원고 + parts 3개)
```
<공통 머리>
과목 <SID> 강의 <KEY>, 검토 <n>회차. 작성자·앞 회차 보고(<보고 파일들>)를 먼저 읽고 그 수정이 자료와 맞는지 확인한 뒤 남은 문제를 찾아 직접 고친다(억지로 고치지 않음 — 없으면 '새 문제 0').
갱신 강의는 guide/handoff/UPD26_REVIEW_BRIEF.md(그 안의 '⚡ 2~3줄'·🔑 120자는 낡음 — RULES 6·10이 이김, ⚡을 줄이지 않음), 새 강의는 guide/handoff/ESTH_검토_BRIEF.md의 일반 절(경로·키 예는 `<SID>`·이 강의로 바꿔 읽음 · ESTH 고유의 '다른 강의와 걸친 문항'·3회차 PLAN/MAT 담당 절은 빼고)을 따른다. 회차별 초점:
 1회차 = 작성자 보고의 'annot·tables·pred 고칠 것'을 parts에 반영 · 갱신 강의는 25 → 26 바뀐 곳 표시(review_final/UPD26MARK_BRIEF.md — `{u:}`·`@UPD`, 작성자가 빠뜨렸으면 채움, 남발은 벗김 · 2·3회차는 확인만) · 자료 → 원고 역대조(1쪽부터 끝까지 이미지 — 자료 사실 40개 이상 대조, 보고에 수) · ⭐ ↔ JB 답 낱말 · 대조 판정·인용·쪽(apply_map26이 잘못 옮긴 'JB 참고 p.N'·다른 강의 쪽·25 필기 쪽 되돌리기) · 26에서 바뀐 수치·용어.
 2회차 = 쪽 단위 역대조 한 번 더(앞 회차가 안 본 각도) · 학습 효과(🔑만으로 뼈대, ⚡이 답 그대로 떠오르나, 표 머리) · 원고 ↔ annot ↔ tables ↔ pred 일치.
 3회차 = 빨강 비율(카드 ≤30%·평균 10~20%·항목 절반 안팎 — check_lec 계산, 빨강은 원문 낱말에·필기 쪽엔 붙이지 않음) · 필기 쪽 강조(QA 34 — RULES 7 끝 예외 3가지만, `tools/check_nred.py <SID> --list`) · 표(QA 35 — 전체정리표 모든 주제·★ 기출 전부·비교 축 빠짐없이·변형 대비 N:·빈 칸 —) · 화면 문항 id 0 · 마지막 쪽 훑기 · RULES.md 전 절 대조(특히 6·10절) · 필기 구간 {n:} 누락·남발(QA 29).
다른 강의에 걸친 문항(교차 ⭐)·같은 그림은 두 강의 문구가 같은지 — 다른 강의 파일은 고치지 말고 보고에 '다른 강의 몫: 파일:줄 · 지금 → 제안'.
고칠 파일: tools/<sid>/lec_<KEY>.txt · work/<SID>/parts/{annot,tables,pred}_<KEY>.txt. 보고 work/<SID>/upd26/R<n+1>_<KEY>.md(새 강의는 work/<SID>/parts/R<n+1>_<KEY>.md) — 고친 것(전→후·근거 쪽) · 다른 강의 몫 · 사용자 확인 필요 · 평가.
```

## D1 다듬기 — 🔑·⚡ (강의 하나 또는 묶음 · lec 파일의 `=`·`M:` 줄만)
```
<공통 머리>
과목 <SID> 강의 <KEY들>. guide/handoff/review_final/KEYMEM_BRIEF.md(누락·짝·기출·강조 보강, 요약 탭 금지) + KEYMEM2_BRIEF.md(라벨·논리 순서·①②③·= 최소) + FWBAL_BRIEF.md 판단 1~3(번호 항목: 짧은 원문은 풀 워딩·긴 문장은 핵심어 압축 — 그 BRIEF의 '대상'(10-07 커밋 줄만)과 '하지 않을 것' 첫 줄은 그 회차 한정, 이번엔 맡은 강의의 모든 ⚡ 번호 항목 · 🎯 K는 D3 몫) 모두 그대로 — 숫자(⚡ 줄 수 등)는 RULES 6절. 맡은 강의의 모든 카드.
검사: check_lec <SID> <KEY> ✗0 · ⚡ 줄마다 tools/<sid>/lecparse.py render_recall로 렌더해 라벨이 굵은 머리(b.mlab / klh)로 잡혔는지 · 본문 표의 짝·목록 칸 수 = ⚡ 번호 수 · 낱말 바꾼 줄 목록 · 라벨 뒤 조각이 ◦ 하위(ul.msub)로 묶였는지·하위 조각에 콜론 없음(render_line). 🔑·⚡의 `{n:…}`(필기에서만 나온 조각 — RULES 9)는 그대로 두고, 필기 쪽엔 빨강을 두지 않음(RULES 7 끝 항목 — REDNOTE_BRIEF), 새로 더하는 🔑·⚡ 사실이 `U:`·`{n:}`·`(필기)` 본문 줄에서 왔으면 `{n:…}`로 감싸고 빨강 없이(기출 답이 그 필기로만 맞거나 교수 강조면 핵심어 하나) · 맡은 카드의 `>` 요지도 필기 조각 `{n:}` 확인, 줄을 합치거나 나눌 때도 조각마다 따로. 이어지는 조각은 한 줄(RULES 6 끝 항목): KEYMEM의 '새 M: 줄 우선'은 독립 사실일 때만, KEYMEM·KEYMEM2의 '서로 다른 사실 = ` / `'는 같은 라벨에 속하는 사실일 때만.
보고 work/review_final2/KM2_<SID>_<묶음>.md(카드마다 ⚡ 전→후 줄 수 · 더한 사실 · 낱말 바꾼 줄).
```

## D2 다듬기 — 줄바꿈·번호·들여쓰기 (강의 하나 또는 묶음 · D1 뒤에)
```
<공통 머리>
과목 <SID> 강의 <KEY들>. guide/handoff/review_final/BREAK2_BRIEF.md(lec 영역) + BREAK3_BRIEF.md + NEST_BRIEF.md 그대로(BREAK3 3번 '고칠 파일 4개 — 이번엔 한 사람이 다'·2번 '2차 JB 담당이 넘긴 줄'은 그 회차 한정 — annot는 D3, pred는 D4 몫 · NEST의 '시작 전 --save'는 메인이 함 — 담당은 --save 하지 않음), 규칙은 RULES 3·4절.
덤프: work/review_breaks2/<SID>_lec.md(메인이 D1 뒤에 새로 만듦 — 처음부터 끝까지, 나뉘어야 하는데 안 나뉜 긴 줄도) + `tools/dump_breaks.py <SID> <키>`(원고 줄 ↔ 화면 조각).
고칠 줄: lec의 `-`·`=`·`E:`·`P:`·`U:` 줄(구분 기호·들여쓰기·번호만 — 낱말 그대로) · tables.txt 칸은 **그 과목 D2 담당 중 메인이 지정한 한 명만**(바뀐 강의의 k= 블록 전부, D4가 끝난 뒤 — 구분 기호만 · 나머지 D2는 tables를 열지 않음). `M:`은 D1 몫(보지 않음). `{n:…}` 필기 표시는 그대로 — 구분 기호를 바꿀 때 ' / '·①②가 {n:…} 안에 들어가면 {n:}을 조각마다 나눠 감쌈(RULES 9). BREAK2·3의 '한 줄을 글자 그대로 두 줄로'는 서로 다른 사실일 때만 — 머리에 이어지는 조각은 `  - ` 하위(NEST)로, 같은 층 `-`로 떼지 않음(RULES 6 끝 항목).
검사: text_diff tools/<sid>/lec_<KEY>.txt · (tables를 맡았으면) text_diff tools/<sid>/tables.txt — 빠진 글자 0(기준본은 메인이 D1 뒤·D4 뒤에 저장) · check_lec. 보고 work/review_breaks2/R_<SID>_<묶음>.md.
```

## D5 다듬기 — 필기 ✍·강조 마무리 (과목 하나 · D2·D3·D4 뒤, D2b 앞 · lec_*.txt 모든 줄·annot.txt·pred.txt — tables.txt는 D4가 함(TABLE3 6번 + 표 칸 `{n:}`))
```
<공통 머리>
과목 <SID> — 이번에 바뀐 강의만(lec_<KEY>·annot `lec=<KEY>` 블록·pred `@<KEY>`; 새 과목이면 전부). guide/handoff/review_final/NOTEMARK_BRIEF.md 할 일 1~3(본문 `-`·`  - `·`#`·`E:` 설명) + NOTEMARK2_BRIEF.md 할 일 1~4(`=`·`M:`·`>`·annot `K:`·pred `A:`) + REDNOTE_BRIEF.md 할 일 1~4 그대로, 규칙은 RULES 7 끝·9(✍ 앞에만). 세 BRIEF의 '이번 대상 아님'·'`E:`는 손대지 않음'·'{r:}는 이번엔 그대로'·'앞뒤 ✍'는 그 회차 한정 — 이번엔 위 대상 전부. 앞 담당(B·C·D1~D4)이 이미 감싼 것은 범위만 확인.
검사: 메인이 D5 시작 전 저장한 기준본으로 text_diff(lec·pred — 빠진 글자 0 · 더한 글자 n뿐) · annot_diff(빠진 글자 0) · check_lec ✗0(빨강 30% 경고가 늘지 않음) · tools/check_nred.py <SID> --list(남은 필기 강조 = RULES 7 끝 예외 3가지뿐 — 보고에 이유) · 고친 🔑·⚡ 줄은 render_line(HTML에 span.ntw가 그 사실 앞에 하나 · 빨강을 빼서 줄 구조가 바뀌면 원문 낱말 빨강 하나를 남김).
보고 work/review_final2/NM_<SID>.md(줄 종류별 감싼 곳 수 · 벗긴 강조 수 · 남긴 강조와 이유).
```

## D2b 구조 정돈 — 이어지는 내용이 떨어져 보이는 곳 (과목 하나 · D1~D4 뒤 — tables·pred도 고치므로 D4가 끝난 뒤, 메인이 빌드·덤프를 새로 만든 다음)
```
<공통 머리>
과목 <SID> — 이번에 바뀐 강의만(lec_<KEY>·annot `lec=<KEY>` 블록·tables `k=<KEY>`·pred `@<KEY>`; 새 과목이면 전부). guide/handoff/review_final/STRUCT_BRIEF.md 그대로(RULES 6 '이어지는 내용은 한 줄에', QA 33). 대상 lec_*.txt 모든 줄 · annot.txt · tables.txt · pred.txt.
덤프 work/review_breaks2/<SID>_lec.md · <SID>_jb.md 전수 · 줄 미리 보기 tools/render_line.py.
검사: tools/struct_diff.py <SID> --ref <D2b 시작 커밋 — 메인이 지시문에 적음> 모든 파일 ✓(글자 그대로) · check_lec ✗0. 보고 work/review_final2/ST_<SID>.md.
```

## D3 다듬기 — JB 해설 (과목 하나 · annot.txt만)
```
<공통 머리>
과목 <SID> annot.txt(이번에 바뀐 강의의 문항 — 블록 머리 lec=<키> — 전부). 기준본은 메인이 저장해 둠(--save 하지 말 것).
guide/handoff/review_final/JBREAD_BRIEF.md · JBREAD2_BRIEF.md · JBTIDY_BRIEF.md를 다 적용(라벨 통일·한 선지 한 줄·보강 필기 합침·M 라벨·{r:}). K 🎯 요점은 RULES 10절·JBTIDY 2) 꼴로만(옛 JBKEY의 `정답 = … — …` 예시는 쓰지 않음 — 라벨 통일 절만 참고) · K의 번호 항목(①②③)은 FWBAL_BRIEF 판단 1~3(RULES 6 '번호 항목' — 짧은 원문은 풀 워딩, 문장처럼 긴 원문은 원문 핵심어 압축, 기출 서술 답은 키워드 빠짐없이) · 다시 쓴 K마다 옛 사실이 새 K·A·M 어딘가에 남았는지 눈으로(annot_diff는 K를 세지 않음) · 앞 회차 보고 파일(JB_<SID>.md 등) 언급은 무시. 화면 덤프 work/review_jb/<SID>.md와 work/review_breaks2/<SID>_jb.md를 처음부터 끝까지 본다. K·A·M에서 앞 줄의 이어짐을 새 줄로 떼지 않음(RULES 10 '이어지는 내용은 한 줄'). 필기 표시·강조(RULES 7 끝·9): K 🎯에서 필기에서만 나온 사실은 `{n:…}`로 감싸고, K를 다시 쓸 때도 원래 K의 `{n:…}`를 그대로 옮김(annot_diff는 K를 예외로 보니 시작 전·후 `grep -c '{n:' tools/<sid>/annot.txt`가 줄지 않았는지 보고). JBREAD2의 '{r:} 핵심어'는 슬라이드 원문 인용·설명에만 — `26 필기(p.N):`·'필기 "…"' 인용·`{n:}` 안에는 `{r:}`·`==`·`**`를 두지 않음(REDNOTE_BRIEF 할 일 1 — 예외 3가지만).
검사: annot_diff(A·M·N 빠진 글자 0 — 겹친 [[ ]] 칩·K 다시 쓰기는 예외로 보고) · check_eyears(🎯 요점 연도 포함) · check_abbr. 보고 work/review_final2/TIDY_<SID>.md.
```

## D4 다듬기 — 표·예상문제·시험 예고 (과목 하나 · tables.txt·pred.txt만)
```
<공통 머리>
과목 <SID> tables.txt·pred.txt(이번에 바뀐 강의 k=·@ 블록). 기준본은 메인이 저장해 둠.
guide/handoff/review_final/TABLE_BRIEF.md + TABLE2_BRIEF.md + TABLE3_BRIEF.md(표 — 시험·암기·변형 대비 · 필기 칸 빨강 빼기) + review_final/BRIEF3.md 1·3번(시험 예고 쪽 전수 → 예상문제, 예상문제 정확도·중복 — 1번의 '원고 카드·💬·⭐·⚡에 없는 것을 채운다'는 lec이라 **보고만**(보고의 'lec 몫'을 메인이 D1·D5에 넘김), 앞 회차 보고 TB_<SID>.md 언급은 무시) 그대로, 규칙은 RULES 5·11절. pred의 줄바꿈(BREAK2 jb 영역 — work/review_breaks2/<SID>_jb.md의 예상문제 부분)도. 표 칸(R:)의 필기에서만 나온 조각도 `{n:…}`(NOTEMARK2_BRIEF 할 일 1~4를 tables에 — 필기 열 머리(`필기 풀이`·`요점(필기)`)의 칸엔 붙이지 않음) · pred `A:`의 필기에서만 나온 조각은 `{n:…}`(RULES 9), 필기 쪽엔 빨강 없음(RULES 7 끝 — REDNOTE_BRIEF 할 일 1·2를 pred에). TABLE_BRIEF·TABLE3의 '기존 {r:} 지우기 금지'는 필기 칸 빨강 벗기기(TABLE3 6)만 예외.
split_parts는 돌리지 않는다(D3와 동시라 annot 조각이 낡은 채 덮임). 형식은 다음 빌드 로그로 확인.
검사: text_diff tables.txt·pred.txt(빠진 글자 = 값 오류 정정뿐 — 보고에 목록) · check_abbr · tools/table_audit.py <SID>(칩 없는 기출 0·표 꼴 0). 보고 work/review_final2/TB_<SID>.md.
```

## E QA — 사용자 눈 점검 (과목 하나 · 고치지 않고 찾기만, 메인이 담당에게 다시 보냄)
```
<공통 머리>
과목 <SID>. .claude/skills/jbl-update/QA.md 점검표 **전 번호**(지금 1~38 — 새 번호가 생겨도 끝까지)를 이번에 바뀐 강의에 대해 하나씩 확인한다. 화면 기준 자료(메인이 마지막 빌드로 새로 만듦): work/review_breaks2/<SID>_lec.md · <SID>_jb.md · work/review_jb/<SID>.md · work/review_scan/<SID>.md · work/_tmp/full_check.log · 스크린샷 work/_tmp/qa_<SID>_*.png(Read) · work/review_final2/TA_<SID>.md(table_audit) · check_nred 목록 — ✍·br.ntb는 덤프에 안 보이니 QA 29는 스크린샷·render_line HTML로.
덤프는 처음부터 끝까지 본다(보고에 본 덩어리 수). 걸린 것마다: 점검표 번호 · 파일:줄(원고 위치) · 화면 모습 → 고칠 모양 · 어느 담당(B/C/D1~D4) 몫. 보고 work/review_final2/QA_<SID>.md. 고치지 않는다.
```
