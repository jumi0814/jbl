# Q4 JB — 4Q 새 과목 JB 분해 + 강의 연결(과목 하나 · 11-16)

사용자 11-16: "4큐 자료 올렸어 … jb 및 강의자료 작업 가장 최적으로 효과적으로 … 퀄리티 절대 놓치지 않으면서" · "임상치과약물치료학의 조영단의 살균제와 소독제가 25년도까진 3큐 파트였는데 올해 4큐 파트로 바뀐 점 참고" · "4큐 이윤실의 불안제가 이미 3큐에서 시험 본 강의자료라는 점 참고".
이 단계 = 그 과목의 **JB 문항 전부 + 강의 틀(키·파일·교수·연도별 출제 교수)** 을 세워 첫 빌드까지. 정리본 본문(lec 카드)·annot(JB 해설)·tables·pred는 다음 단계(B2Q 작성 담당)가 함.

## 먼저 읽기
CLAUDE.md 절대 규칙(출제연도·JB 빠짐없이·답 글자 불변) · `.claude/skills/jbl-update/RULES.md` 0·0-1·13·14절 · `tools/SPEC.md` 'JB 문항 id 잠금(C09)'·'JB 결정 반영'(front= 자동 = 가장 최신 판) 항목 · `guide/handoff/JB26_BRIEF.md`(판본 통합 요령 — 이 과목은 기존 판이 없는 **새 과목**: 모든 판이 새로) · `guide/handoff/YEARPROF_BRIEF.md` · 본보기 코드: `tools/esth/parse_esth.py`(연도 칸형)·`tools/cons/parse_cons.py`(교수별 괄호형)·`tools/esth/assemble.py`·`tools/pharm/assemble.py`(TOPIC_LK·다른 쿼터 판 '23q4')·`tools/<3Q 같은 과목>/subject.py`(필드 뜻 — tools/cons/subject.py 주석) · `guide/과목노트_<SID>.md`(빈 틀이면 이번에 채움).

## 자료
- JB: `work/jb/<SID>_20YY/`(N.txt pdfium 글 · N.jpeg 쪽 그림 폭 924 · manifest.json) — 판 = 파일 해(예 2025판 = 2025년에 만든 JB · **그 안의 최신 시험 해는 머리 멘트로 확인** — 보통 판 해 - 1). 판마다 **모든 쪽을 글과 그림 둘 다** 본다(표·칸·괄호 연도·교수 칸 머리·미복원·그림 문항).
- 강의자료: `work/<SID>/mat/index.json`(파일·쪽 수) · `work/<SID>/mat/<파일id>/{i,t,o}/` — 파일 이름 앞 날짜 = 수업 날(25 = 251103… · 26 = 261103…). 이 단계에서는 **표지·목차·첫 몇 쪽만**(강의 제목·교수 확인 — 본문 정독은 작성 담당).
- 과목 틀: `tools/<sid>/`(new_subject.py 빈 틀 — subject.py·assemble.py·parse_<sid>.py·lec_WAIT.txt).

## 할 일(차례대로 · 보고 파일 `work/<SID>/jb/R_JB_<SID>.md`에 단계마다 덧붙여 저장 — 멈춰도 다음 담당이 이어 감)
1. **판 전부 읽기** → 보고 1절: 판마다 구조(연도 칸형/교수별/강의별)·머리 멘트 원문 요지(교수 변경·올해 안 한 강의·미복원·'3Q 내용으로 생략')·수업 표(강의·날짜·교수)·판마다 문항 블록 수.
2. **강의 표**(보고 2절 — 메인이 matx SRC·과목노트에 옮김): 키(영문 대문자 2~5자 · 과목 안에서 겹치지 않게 · 3Q 같은 과목 키와 같아도 됨)마다 강의 이름(원래 제목)·26 담당 교수·파일:
   - 26 파일이 있으면 `<KEY>` = 26 파일 · 같은 주제 25 파일 = `<KEY>5`(IMG_ALIAS `<KEY>5 → <KEY>` · 25가 여러 파일이면 `<KEY>5`·`<KEY>5B` …) · 26이 25 두 강의를 하나로 합쳤으면 둘 다 그 키의 25 보조 키.
   - 26이 없으면 `<KEY>` = 25 파일(25 임시본 — RULES 14 b · LECMAP 이름 끝 '(25)').
   - 강의 순서 LEC_ORDER = 26 수업 차례(26이 없는 주는 25 차례).
   - **JB에만 있고 올해 강의·자료가 없는 주제**(멘트 '올해는 강의하지 않으셨습니다'·'참고용' 등): 그 내용이 지금 강의에 있으면 그 강의에 tier C(참고)로 · 없으면 따로 키(LECMAP 폴더 `None` · 이름 '<원래 제목> — 올해 강의 없음(기출 참고)') — 문항은 하나도 빼지 않음. 정리본은 쓰지 않음(작성 담당이 '자료 없음' 안내 카드 하나).
   - 교과서·참고 자료뿐인 과목(ANAT4)은 SKILL '참고 강의'(XREF_LECS·FIG_ONLY_LECS · RULES 13 10-17 ESTH BOOK) 꼴을 보고 강의를 어떻게 나눌지 2~3안 + 고른 안(무인 — 가장 보수적인 안)을 보고에.
   - 쪽 이미지 링크: `mkdir -p work/<SID>/lec && ln -sfn ../mat/<파일id>/i work/<SID>/lec/<폴더>`(폴더 이름 = 키 + 'i' 등 · 3Q 과목 꼴) — 보고에 `'<폴더>': '<파일 이름 앞머리>'` 줄(matx SRC — **tools/matx.py는 메인이 고침**).
3. **parse_<sid>.py**: 판마다 블록 분해(`parse(ed, n)` → 블록 [{'ed','sec','prof','num','pg','pg2','lines'}] — 본보기 꼴) · `__main__`에 판마다 블록 수·번호 목록 출력 · 머리말·해설 안 번호 줄은 문항 아님(RULES 0-1) · 블록 수 = 1절에서 센 수.
4. **assemble.py**: NPAGES(판 → 쪽 수) · 정식 문항(CANON)·같은 문제의 다른 판 블록 = OTHER(판 사이 같은 문제는 하나로 · 비슷하지만 답·조건이 다른 문제는 별개 + annot `rel=`은 다음 단계 — 보고에 짝 목록) · 문항마다 강의 키(LK/TOPIC_LK)·tier(A 현 교수 기출 · B · C 참고 — 3Q 과목 꼴)·LK_PROF · 대조표(LEDGER)에서 **연결 안 된 블록 0** · id = 새 과목 꼴(예 강의마다 글자 + 번호 — 한번 정하면 jb_lock.json이 잠금 · 번호 당기기 금지).
   - **출제연도**(CLAUDE.md 절대 규칙): 괄호 연도(문항 첫머리 전체 · `(24, 탈)`·`(14~)`·`(…,13,)` 변형) ∪ 실린 연도 칸 ∪ 다른 판·칸의 같은 문제 — 실리지 않은 해 금지 · 판 해를 출제연도로 쓰지 않음.
   - **답 글자 불변**(공백 제외 비교) — 줄바꿈 정리만(build4가 함).
5. **subject.py**: SID·TITLE·EN·COLOR(그대로)·PROFS · LECMAP·LEC_ORDER·IMG_ALIAS·FORCE_PAGES · PROF_LEC·PROF_ORDER·COVER·TIERS·PROF_NOTE·MENT_PROF·MENT_ALL(멘트 원문 인용 `"…"(25판)` 꼴) · **YEAR_PROF**(강의 → {출제 해: 그 해 출제 교수} — 판 교수 머리·칸 메모·수업 표·멘트 근거만, 추측 금지 · YEARPROF_BRIEF)·YEAR_PROF_Q · NOIMG_PAGES(교수님 본인 연락처 쪽만 — RULES 8 · 보고 '개인 연락처 쪽'). 3Q 같은 과목 subject.py의 필드 꼴 그대로.
6. **강의 원고 자리**: 강의마다 `tools/<sid>/lec_<KEY>.txt` 빈 틀 — `#LEC <KEY> | <강의 이름> | <교수> | <25|26> | <파일 이름> | <쪽 수>` + `@MAP 작성 중` + `@G ① 작성 중` + 카드 하나(`## Notes in progress | 정리본 작성 중 | 1 | 자리 표시` · `= 이 강의 정리본은 작성 중이에요 — 기출 탭부터 보세요.`) — 3Q 과목 #LEC 줄 꼴 그대로(tools/pharm/lec_*.txt 머리) · `lec_WAIT.txt`는 지움(`git rm` 아님 — 파일만 지움 · 메인이 커밋).
7. **빌드·검사**: `.venv/bin/python tools/<sid>/build4.py > work/_tmp/b_<sid>_jb.log 2>&1` → 끝의 '연결 안 된'·'없는 문항' `[]` · 'JB id 잠금: n | 새로 잠금 k'(k = 문항 수) · `python -c "import sys;sys.path.insert(0,'tools');import jblock;print(jblock.lock_errors('docs'))"` 이 과목 0 · `.venv/bin/python tools/dump_review.py <SID>`(→ work/<SID>/review/questions.md) · `tools/check_years.py <SID>` 0 · `tools/check_yearprof.py <SID>` 0 · `tools/fmt_audit.py <SID>`(형식 판정 — 원문과 어긋나면 보고) · `JBL_FRONT_ONLY=1 .venv/bin/python tools/<sid>/build4.py` → `work/<SID>/front_auto.json`(앞면 = 가장 최신 판 · 답이 바뀐 카드 수 보고). '⭐ 정리본에 연결 안 된 현 교수 기출'은 이 단계에서 다 나옴(정리본이 아직 없음 — 정상).
8. **그림 문항 표**(보고 3절 — 다음 단계 JF가 조각): id · 판-쪽 · 그림이 문제 쪽/답 쪽 · 번호·화살표·빈칸.

## 쓸 파일 · 금지
- 쓸 것: `tools/<sid>/{parse_<sid>.py, assemble.py, subject.py, lec_*.txt}` · build4가 쓰는 `tools/<sid>/{jb_lock.json, jb_move.json, aid_lock.json, img_lock.json}`·`docs/packs/<SID>.js`·`docs/packs/img/<SID>/` · `work/<SID>/…` · `guide/과목노트_<SID>.md`.
- 금지: 공통 파일(tools/cons/* · tools/<sid>/ 안의 build4·lecparse·reflow·trend·emph·build2·shell 사본 · tools/matx.py·jbx.py·quarters.*) · 다른 과목 파일 · build4 외 빌드(rehub·sync_common·full_check·build_all) · 커밋·git stash · 브라우저 · annot·tables·pred(다음 단계).
- 막히면 판단 근거를 보고에 적고 가장 보수적인 쪽(문항 별개로 둠·빼지 않음).

## 보고(`work/<SID>/jb/R_JB_<SID>.md` — 끝나면 최종 답 5줄)
1절 판 구조·멘트 · 2절 강의 표(키·이름·교수·26/25 파일·쪽·보조 키·matx SRC 줄·링크 확인) + 교수 표(교수 · 강의 · 출제 해 · 26 담당 여부) · 3절 문항 표(판마다 블록 수 = 정식 a + 같은 문제 b + 머리말 c · 강의별 문항 수·tier · 연도 분포 · 그림 문항) · 4절 검사 결과(위 7) · 5절 사용자 확인(판독 불가·애매한 연결·올해 강의 없음 주제·교과서 강의 나누기 안).
