# Q4 MAIN — 통합 담당(메인 몫 실행 · 과목 하나 · 11-16)

Workflow 안에서 메인이 하던 '회차 사이 일'(SKILL D·E·F·G의 메인 줄)을 대신한다. **글을 쓰지 않는다**(원고·annot·tables·pred의 내용 수정 금지 — 단 아래 '다른 강의 몫 옮기기'의 글자 그대로 옮김만). 같은 과목의 다른 담당이 돌고 있지 않을 때만 불림(회차 사이).
명령은 저장소 /home/user/jbl에서 · 파이썬 `.venv/bin/python` · 오래 걸리는 것은 그대로 기다림(1~5분). 보고는 한국어 · 보고 파일 `work/<SID>/main/M_<단계>.md`(머리 먼저 · 단계마다 덧붙임) · 최종 답 = 아래 '돌려줄 것' 꼴.

## 단계(지시문이 고른 하나)
### prep — 작성 전
1. `.venv/bin/python tools/<sid>/build4.py > work/_tmp/b_<sid>_m.log 2>&1` → 끝 3줄(연결 안 된·없는 문항·⭐ 연결 안 된 현 교수 기출) 보고.
2. `.venv/bin/python tools/split_parts.py <SID> --force` → `.venv/bin/python tools/merge_parts.py <SID> --check` '검사 통과'.
3. `.venv/bin/python tools/dump_review.py <SID>` → `work/<SID>/review/{questions,materials}.md`·qids.json. materials.md에서 강의마다 쪽 이미지 폴더가 있는지('폴더 없음' 0 — 있으면 R_JB 2절의 링크 줄로 `ln -sfn` 다시).
4. 강의마다 문항 id 목록(questions.md의 lk)을 보고에 표로(작성 담당 지시문에 메인이 넣음).

### merge — 회차 뒤(작성·검토 C·F 담당이 parts·lec를 고친 뒤)
1. 이번 회차 보고들(지시문이 준 경로)의 '다른 강의 몫'·'annot·tables·pred 고칠 것'을 모아 `work/<SID>/main/HANDOFF_<다음 회차>.md`에 강의별로 정리(파일:줄 · 지금 → 제안 · 근거 쪽) — **고치지 않고 옮겨 적기만**(다음 회차 그 강의 담당이 반영).
2. `.venv/bin/python tools/merge_parts.py <SID>` — '낡은 조각'(✗)이 나오면 멈추지 말고 원인(tools/<sid>/annot·tables·pred를 누가 고쳤나 — `git diff --stat tools/<sid>/`)을 보고에 적고 `--stale-ok` 쓰지 않음 → 돌려줄 것에 'merge 막힘'.
3. build4 → 끝 3줄 · 'JB id 잠금'·'예상문제(S3):' 줄 · 오류가 나면 traceback 끝 20줄.
4. 검사(모두 돌리고 숫자만 보고 · 고치지 않음): `tools/check_lec.py <SID>`(강의별 ✗·경고 수) · `tools/check_years.py <SID>` · `tools/check_eyears.py <SID>` · `tools/check_abbr.py <SID>` · `tools/check_unote.py <SID>` · `tools/check_yearprof.py <SID>` · `tools/check_25only.py <SID>` · `tools/link_audit.py <SID>`(✗·△ 줄) · `tools/pred_check.py <SID>` · `tools/check_nred.py <SID>`.
5. `.venv/bin/python tools/dump_review.py <SID>` 다시 · `.venv/bin/python tools/split_parts.py <SID> --force`(merge가 tools를 바꿨으니 조각을 새로 — 다음 회차가 씀) → `merge_parts <SID> --check` 통과.

### fprep — F(다듬기) 앞
merge 1~5 + `tools/dump_breaks2.py <SID>` · `tools/dump_jb.py <SID>` · `tools/scan_render.py <SID>` · `tools/table_audit.py <SID> --md work/review_final2/TA_<SID>.md` · `JBL_FRONT_ONLY=1 .venv/bin/python tools/<sid>/build4.py`(front_auto.json) → **기준본 저장**: 강의마다 `tools/text_diff.py tools/<sid>/lec_<KEY>.txt --save` · `tools/text_diff.py work/<SID>/parts/annot_<KEY>.txt --save`(tables·pred 조각도 있으면).

### qaprep — QA 앞
merge 1~5 + `dump_breaks2`·`dump_jb`·`scan_render`·`table_audit`(위와 같음) · `JBL_HTTP=1 .venv/bin/python tools/qa_shots.py <SID> <KEY들>` → 만든 png 목록 · 기준본 저장(fprep과 같은 파일).

## 금지
글 내용 수정 · 공통 파일(tools/cons/* · tools/<sid>/ 안 공통 사본) · 다른 과목 · rehub·sync_common·full_check·build_all · 커밋·git stash · `--stale-ok`.

## 돌려줄 것(최종 답 — 이 꼴 그대로, 길어도 됨)
```
단계 <prep|merge|fprep|qaprep> · 빌드 <ok|오류>
연결: 연결 안 된 [] · 없는 문항 [] · ⭐ 연결 안 된 현 교수 기출 n개(id …)
강의별: <KEY> check_lec ✗a 경고b · 25only c · link ✗d △e  (강의마다 한 줄)
과목: years n · eyears n · abbr n · unote n · yearprof n · pred_check ✗n · nred n
다음 회차 넘길 것: work/<SID>/main/HANDOFF_<회차>.md(강의별 건수)
막힘: (없으면 '없음')
```
