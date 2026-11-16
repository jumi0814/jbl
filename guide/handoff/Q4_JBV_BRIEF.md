# Q4 JBV — 4Q 과목 JB 독립 검수(과목 하나 · 11-16 · Q4_JB 담당과 다른 담당)

앞 담당(Q4_JB)이 세운 그 과목 JB를 **믿지 않고** JB 원본 쪽과 하나하나 맞대어, 틀린 것을 직접 고친다(억지로 고치지 않음 — 없으면 '새 문제 0'). CLAUDE.md 절대 규칙: **JB 문항은 하나도 빠짐없이 · 출제연도 = 괄호 ∪ 실린 칸 ∪ 다른 판·칸의 같은 문제(실리지 않은 해 금지 · 판 해 금지) · JB 답 글자 불변**.

## 먼저 읽기
`guide/handoff/Q4_JB_BRIEF.md`(앞 담당이 한 일) · 앞 담당 보고 `work/<SID>/jb/R_JB_<SID>.md` · RULES 0·0-1·13 · `tools/SPEC.md` 'JB 문항 id 잠금(C09)'·'JB 결정 반영'(jb_move · front= · rel= · subq= · hide=) · `tools/<sid>/{parse_<sid>.py,assemble.py,subject.py}`.

## 볼 것(판마다 1쪽부터 끝까지 — 글 `N.txt`와 쪽 그림 `N.jpeg`를 둘 다)
1. **빠짐**: 쪽마다 문항 번호를 세어 `parse_<sid>.py` `__main__` 블록 목록과 맞댐 — 빠진 블록·두 문항이 한 블록으로 붙음·한 문항이 둘로 쪼개짐·해설/머리말 번호를 문항으로 셈·소문항(4-1 등)·미복원 문항(번호만 있는 것도 문항 — v=na).
2. **같은 문제 묶기(OTHER)**: 다른 판·다른 해 칸의 같은 문제가 따로 정식 문항으로 남음(→ 하나로) / 답·조건이 다른 문제를 하나로 묶음(→ 떼어 냄 · 짝은 보고에 `rel=` 후보).
3. **출제연도**: 문항마다 배지 해 = 괄호 연도(문항 첫머리 전체 · `(24, 탈)`·`(14~)`·`(…,13,)`) ∪ 실린 칸 해 ∪ 묶인 다른 판·칸 해 — 더하거나 빠진 해 · 판 해가 섞임 · `tools/check_years.py <SID>`.
4. **답·문제 글자**: 정식 문항 글이 원본과 같은지(공백 제외) · 깨진 기호(보고에 쪽·글자 — 공통 build4 SYMPUA는 메인 몫) · 그림·표가 글로 잘못 옮겨짐.
5. **강의·교수·tier**: 문항 → 강의 키 연결(그 판 칸 머리·수업 표·주제) · YEAR_PROF(그 해 출제 교수 — 판 교수 머리·칸 메모·수업 표·멘트에 근거가 있는지 · 추측이면 지우고 '-') · tier(현 교수 기출 A · 참고 C) · 올해 강의 없는 주제 처리.
6. **강의 표**: `subject.py` LECMAP 키 ↔ `work/<SID>/mat/index.json` 파일(26이 있으면 26이 본문 · 같은 주제 25 = 보조 키) · `work/<SID>/lec/<폴더>` 링크가 맞는 파일로 가는지(`ls -l`) · 강의 이름·교수 = 표지.
7. **앞면**: `JBL_FRONT_ONLY=1 .venv/bin/python tools/<sid>/build4.py` → `work/<SID>/front_auto.json` — 가장 최신 판 사본이 다른 문제를 고르지 않았는지(asim·qsame 낮은 것부터).

## 고치는 법
- `parse_<sid>.py`·`assemble.py`·`subject.py`만(정식 id는 jb_lock.json이 잠금 — **번호 당기기·재사용 금지** · 합치기 = 남는 카드 OTHER로 옮기고 `jb_move.json` {없어진: 남는} · 새 문항 = lock에 없는 새 번호 · SPEC 'JB 결정 반영').
- 고친 뒤 `.venv/bin/python tools/<sid>/build4.py > work/_tmp/b_<sid>_jbv.log 2>&1` → '연결 안 된'·'없는 문항' `[]` · jblock.lock_errors 이 과목 0 · `tools/dump_review.py <SID>` · `tools/check_years.py <SID>` 0 · `tools/check_yearprof.py <SID>` 0 · `tools/fmt_audit.py <SID>`.
- 금지: Q4_JB_BRIEF '금지'와 같음(공통 파일·다른 과목·matx·rehub·커밋·브라우저·annot/tables/pred).

## 보고 `work/<SID>/jb/V_JB_<SID>.md`(맨 위 '새 문제 n' — 빠짐·묶기·연도·글자·연결·교수·앞면 꼴별 수 · 고친 것 전→후 · 판마다 '센 번호 = 블록' 대조 수 · 사용자 확인) — 최종 답 5줄.
