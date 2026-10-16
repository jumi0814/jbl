# JB26 — 2026 3Q JB(26판) 통합 · 담당 = 과목 하나

사용자(10-15): "새 26년도 JB를 빠짐없이 통합하고 기존 JB의 원문·원래 답안·출제 이력은 보존. 관련 강의와 연결하면서 연도·교수·출제 형식 및 26년도 기준 답안과의 차이를 해설에서 구분." · "기존 JB 해설·참조가 오래된 25년도 정리본에 의존하거나 최신 자료와 충돌한다면 필요한 부분을 갱신. 과거 JB 원문은 임의로 변경하지 말 것."
26판 = 2025년 시험까지 담은 새 JB(학습부가 2026년에 만든 판). 25년 시험 새 문항 + 이전 문항(연도 병합·답 보강).

## 먼저 읽기
CLAUDE.md 절대 규칙 · .claude/skills/jbl-update/RULES.md 0·0-1·9·10·12절(최종형 — 문서끼리 다르면 RULES가 이김) · tools/SPEC.md 'JB 문항 id 잠금(C09)' 항목 · guide/과목노트_<SID>.md · 그 과목 tools/<sid>/parse_*.py·assemble.py·subject.py(지금 판본 처리 방식).

## 자료
- 26판: `work/jb/<SID>_2026/N.txt`(pdfium 텍스트 — 기존 판과 같은 변환) · `N.jpeg`(쪽 이미지, 폭 924) · manifest.json. 원본 `jb/2026 3Q <과목> JB.pdf`(pymupdf로 글자 위치·그림 상자 확인 가능 — `.venv/bin/python -I`).
- 기존 판: `work/jb/<SID>_2023~2025/`. 지금 사이트 문항 = `work/<SID>/review/questions.md`(id·연도·연결 강의·화면 글자) · `qids.json`.
- 강의자료: `work/<SID>/review/materials.md`(키 ↔ 쪽 이미지 폴더) · 쪽 이미지 `work/<SID>/lec/<폴더>/<쪽>.jpg`(Read로 직접 봄).

## 할 일(차례대로 — 보고 파일에 단계마다 덧붙여 저장)
1. **26판 전 쪽 읽기**: 머리 멘트(26년 학습부 코멘트·교수 변경·수업 표), 구조(연도 칸 / 교수별 / '25년 출제' 앞쪽 + 나머지 등), 문항 수·미복원.
2. **parse**: `parse_<sid>.py`에 26판 분해를 더한다. 기존 판(23·24·25) 분해 결과는 **한 블록도 바뀌지 않게**(고치기 전후 `__main__` 출력 diff로 확인 — 보고에 '기존 판 블록 동일 ✓'). 26판 머리말·해설 안 번호 줄은 문항 아님(RULES 0-1).
3. **assemble**: `NPAGES`(또는 그 과목 판 목록)에 `'26'`. 26판 블록 하나하나를
   - (a) 기존 정식 문항과 **같은 문제** → 그 id의 `OTHER`에 26판 블록 추가(그 과목 OTHER 꼴 그대로). 기존 정식 문항의 표시 원문(ed·text)은 **바꾸지 않음**(jb_lock 해시 — 바꾸면 사용자 채점·북마크·플래시카드가 끊김).
   - (b) **새 문항**(25년 시험 새 문제, 이전 판에 없던 복원) → 새 정식 문항. id = 그 과목 id 꼴을 따르되 `tools/<sid>/jb_lock.json`에 없는 새 번호(기존 id 재사용·번호 당기기 금지). 표시 원문 = 26판. tier·교수·강의 연결(LK_PROF·lec)도.
   - (c) 비슷하지만 답·조건이 다른 문항 = 별개 + 관련 문항 링크(annot `rel=`).
   - 대조표(LEDGER)에서 연결 안 된 26판 블록 0(`__main__`/빌드 출력으로 확인).
   - 26판에서 기존 문항 답이 보강·수정됐으면 화면 '다른 판본'에 그대로 보이고, 차이는 annot 그 문항 블록 끝 `N: 26판: …`(한 줄 — 무엇이 달라졌나). 기존 A·K·M 줄은 빼지 않음.
   - `MENT`에 `'26'`(26판 머리 쪽) · `subject.py`: `MENT_PROF`·`MENT_ALL`에 26 멘트 원문 인용(`"…"(26년)` — 기존 꼴) · `PROF_NOTE`에 26 교수 변경(26판 수업 표·멘트 근거) · `YEAR_PROF`에 25년 칸(판 교수 머리·수업 표·멘트 — guide/handoff/YEARPROF_BRIEF.md · 교수 바뀐 강의는 옛 해도 확인) · 새 교수면 `PROF_LEC`·`PROF_ORDER`·`COVER`·`TIERS`. 강의 키는 바꾸지 않음.
4. **출제연도**(RULES 0): 새 문항 = 괄호·칸 연도 그대로(실리지 않은 해 금지). 26판에서 연도가 병합된 기존 문항은 다른 판본 괄호로 배지에 25가 붙음(자동). `.venv/bin/python tools/check_years.py <SID>` — 새로 생긴 경고 0(기준값: GERI 11은 학번 판 — 늘지 않게).
5. **annot.txt**: 새 문항마다 블록(RULES 10 최종형 — `@id | v=ok|part|diff|none|na | lec=<키>:<쪽>` · K 1~3줄 · A 선지(근거) 하나에 한 줄 · M · N). 근거 = **26 강의자료 쪽 이미지**(없으면 25 보조 키 `<KEY>5`). 26 자료와 JB 답이 다르면 ⚠ 둘 다(RULES 9·13). 미복원 = v=na · K 없음. 기존 문항의 해설이 26 자료와 충돌하거나 25 자료에만 기대면 그 블록에 A/M 줄을 **덧붙여** 26 근거를 병기(지우지 않음).
6. **정리본 ⭐**(lec_*.txt): 새 문항(tier A·B)마다 주 카드(annot lec 쪽을 담은 카드)에 `E:` 줄(RULES 9 꼴 — `E: <id> | 25년 <형식> "<요지>" → <JB 답 원문 용어 전부> — p.<쪽> …`) + 카드 머리 `jb=`에 id 덧붙임 · 전체정리표(`tables.txt` `sum=1`) ★ 열에 `{jb:<id>}`. 기존 문항이 25년에도 나왔으면 그 문항의 `E:` 줄 연도 머리에 25를 더함(배지와 같게 — `tools/check_eyears.py <SID>` 0). 강의 `!` 머리말의 JB 출제 경향(짤 n/m·형식·반복 해)과 `@TIP`의 개수·연도는 25년 시험을 반영해 **낱말 최소 수정**. RULES 12(사용자 표시 보존): 카드 나누기·합치기·제목 바꾸기 금지, 덧붙이기 > 낱말 고치기.
   - **지금 26 자료로 갱신 중인 강의**(지시문의 '갱신 중 강의' — 다른 담당이 그 lec 파일을 씀): 그 lec 파일과 그 강의 annot 블록은 건드리지 않는다. 그 강의에 들어갈 새 문항 annot 블록 초안·`E:` 줄·`jb=`·`!` 수정은 `work/<SID>/jb26/E_<KEY>.md`에 그대로 붙여 넣을 꼴로 적는다(쪽 번호는 **26 자료 쪽** — LECMAP의 그 키는 이미 26 폴더). 메인이 갱신 담당 뒤에 넣는다.
7. **그림 문항**: 26판 새 문항·기존 문항 중 그림·사진·표·도식이 있는 것 목록(판-쪽, 문항 id, 그림이 문제 쪽인지 답 쪽인지, 번호·화살표·빈칸 여부)을 보고에 표로 — 그림 붙이기는 다음 단계(S1c)가 함. 지금 사이트에서 '🖼 그림 문항 — JB 원본 버튼에서…'로만 보이는 기존 문항도 함께 적는다.
8. **빌드·검사**: `.venv/bin/python tools/<sid>/build4.py > work/_tmp/b_<sid>_jb26.log 2>&1`(1~3분) → 끝의 '⭐ … 다뤄지지 않은'·'연결 안 된'·'없는 문항' 모두 `[]` · 'JB id 잠금: n | 새로 잠금 k'(k = 새 문항 수) → `python -c "import sys;sys.path.insert(0,'tools');import jblock;print(jblock.lock_errors('docs'))"`에 이 과목 오류 0 → `tools/check_years.py <SID>` · `tools/check_eyears.py <SID>` · `tools/check_lec.py <SID>` ✗0 · `tools/check_abbr.py <SID>` 새 약어 0 · `tools/link_audit.py <SID>` ✗0(강의 없음·기출 탭 빠짐·⭐ 없음) · `tools/check_yearprof.py <SID>` 0 · 새 문항 형식 = trend.fmt_of 판정(`tools/fmt_audit.py <SID>`)과 문제 원문 꼴 대조(어긋나면 보고 'fmt_of 몫') → `tools/dump_review.py <SID>`(questions.md에 새 문항이 보이는지).

## 쓸 파일 · 금지
- 쓸 것: `tools/<sid>/{parse_*.py, assemble.py, subject.py, annot.txt, tables.txt, lec_*.txt(갱신 중 강의 제외)}` · `work/<SID>/jb26/`(보고 `R_JB26.md`, 갱신 중 강의 몫 `E_<KEY>.md`).
- 금지: 공통 파일(tools/cons/build4.py·shell.html·lecparse.py·reflow·trend·emph — tools/<sid>/ 안의 같은 이름 복사본도) 수정 · build4 외 빌드(build_all·rehub·sync_common·full_check) · 커밋·git stash · 다른 과목 파일 · pred.txt(예상문제는 다음 단계) · 브라우저.
- 막히면(구조가 애매) 판단 근거를 보고에 적고 가장 보수적인 쪽(기존 유지·별개 문항)으로.

## 보고(work/<SID>/jb26/R_JB26.md)
26판 구조 요약 · 26판 블록 n = 기존 연결 a + 새 문항 b(문항마다 id · 연도 · 출제 교수(YEAR_PROF) · fmt_of 형식 · 강의) + 머리말 c · 기존 판 블록 동일 ✓ · 25년 시험 형식 요약(서술/단답/객관/T·F/빈칸/그림 개수 · 짤/탈 — 26판 멘트) · 26 교수 변경 · annot 새 블록 수 · ⭐ 더한 수 · 그림 문항 표 · 검사 결과 · 사용자 확인 필요(판독 불가·애매).
최종 답은 5줄.
