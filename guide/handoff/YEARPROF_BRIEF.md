# YEARPROF — 출제 연도별 출제 교수 (10-16)

사용자(10-16 원문): "jb 및 넘버링 파트에서 출제 연도 및 교수님 태그를 달 때 출제연도 기준의 교수님 이름을 적었으면 좋겠어! 강의자료는 같더라도 출제 교수님이 다르면 그걸 알 수 있게! 그리고 문제 옆에 출제연도는 가장 최신순(25,23,22) 이렇게, 및 교수님 태그가 볼드체였으면 좋겠어 지금은 잘 안 보여."

## 지금 문제
문항의 교수(q['prof'])는 대부분 **강의 연결(assemble.py LK_PROF — 그 강의 지금 담당)**에서 옴 → 옛 교수가 낸 해의 문항도 지금 교수 이름으로 보임(예: ANAT LIP 20~25년 문항이 26 담당 '양훈주' — 실제 출제는 한정준·최진영 · PHARM 22년 구강건조증은 백정화 출제인데 XE = 이윤실).

## 할 일(과목 하나 · 파일 = tools/<sid>/subject.py 하나만 — 맨 끝에 덧붙임)
```python
# 10-16 출제 연도별 출제 교수(그 해 그 강의 문항을 낸 교수) — 근거: <요지> (guide/handoff/YEARPROF_BRIEF.md)
YEAR_PROF = {'<강의 키>': {2025: '교수', 2024: '교수', …}, …}       # 강의 단위(그 해 그 강의 = 한 교수)
YEAR_PROF_Q = {'<문항 id>': {2022: '교수'}, …}                     # 예외(같은 해 같은 강의인데 문항마다 교수가 다를 때·강의 연결과 다른 교수 문항)
```
- 그 강의 문항의 출제 연도(work/<SID>/review/questions.md 머리줄 '출제')에 나오는 **모든 해**를 확인. 근거가 있는 해만 적음(모르면 빼기 — 빈 해는 지금 교수(q['prof'])로 보임). **추측 금지.**
- 근거(강한 순): ① JB 판본 원문의 교수 머리(work/jb/<SID>_20xx/N.txt — '○○○ 교수님'·교수별 칸·괄호) — 그 판이 다루는 시험 해(26판 = 2025년 시험 · 25판 = 2024 · 24판 = 2023 · 23판 = 2022 · 그보다 옛 해는 그 판 안의 연도 칸/괄호의 교수 표기) ② JB 학습부 멘트·수업 표(26판 p.2 등) ③ subject.py PROF_NOTE·TREND_NOTE ④ guide/handoff/trend26/TREND_<SID>.md(교수 변경 강의의 '옛 교수 기출' 분석) ⑤ guide/과목노트_<SID>.md.
- GERI는 assemble OTHER에 판마다 교수가 있음(('26','2025','4','장지희')) — 그것도 근거. GERI 학번 판(24·23판): 'NN학번' 멘트·칸 = 시험 해 NN+2(check_years '학번?' 규칙과 같음 — RULES 0-1 · 틀리면 교수 태그가 2년씩 밀림).
- 바뀜 멘트에 옛 교수 이름이 있으면('○○ 교수님에서 △△ 교수님으로') 바뀌기 바로 전 해는 그 옛 이름(그보다 옛 해는 근거가 있을 때만 — 없으면 빼거나 '이전 교수').
- 기존 문항이 다른 강의로 옮겨 가면 YEAR_PROF[옛 키]의 해들을 YEAR_PROF[새 키]로(문항 단위면 YEAR_PROF_Q — build4 yp_of는 q['lk']로 찾음).
- 교수 이름 글자는 지금 사이트에서 쓰는 꼴 그대로(subject.py PROFS·PROF_LEC과 같은 글자).

## 검사·보고
- `.venv/bin/python -c "import sys;sys.path[:0]=['tools/<sid>','tools'];import subject as S;print(len(S.YEAR_PROF), len(getattr(S,'YEAR_PROF_Q',{})))"` 가 오류 없이.
- `.venv/bin/python tools/check_yearprof.py <SID>` 0(YEAR_PROF 키 ∉ LECMAP · 그 강의에 문항이 없는 해 · YEAR_PROF_Q의 없는 문항 id).
- 보고 `work/_tmp/yearprof/R_<SID>.md`: 강의마다 연도 → 교수 표 · 각 칸 근거(판·쪽·글 인용) · 근거 없어 뺀 해 · 사용자 확인 필요. 최종 답 5줄. 빌드·커밋 금지.
