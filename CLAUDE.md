# JBL — 3학년 3쿼터 시험 대비 시스템 (Claude Code 작업 지침)

이 저장소는 치의학대학원 3학년 3쿼터 7과목의 **JB(과거 기출) 기반 학습 사이트**다.
`docs/`가 GitHub Pages(공개 저장소, main 브랜치 /docs)로 공개되는 사이트이고, 사용자는 그 링크로 공부한다.
사용자가 "○○과 강의자료 작업해줘"라고 하면 아래 절차대로 팩을 만들고/갱신하고, 빌드·검증 후 **커밋·푸시까지** 한다.

## 폴더
| 경로 | 내용 | git |
|---|---|---|
| `docs/index.html` | 허브(모든 과목 공통, 도구·검색·백업 내장) | O |
| `docs/packs/<SID>.js`, `<SID>.img.<강의키>.js`, `<SID>.img.jb.js` | 과목 팩 | O |
| `tools/<sid>/` (oms1·cons·impl·anat·geri·pharm·esth) | 과목별 빌드 파이프라인. 모든 과목이 같은 스크립트, `subject.py`·`assemble.py`·`parse_<sid>.py`·원고만 다름 | O |
| `guide/` | 정리본 원칙·피드백기록·과목노트 — **작업 전 반드시 읽을 것** | O |
| `tools/SPEC.md` | 파이프라인 상세 스펙 — 작업 전 반드시 읽을 것 | O |
| `materials/<과목명>/` | 사용자가 넣는 강의자료(PDF 등) | X |
| `jb/` | JB 파일(`2025 3Q <과목> JB.pdf` 등 — 실제 PDF. `tools/jbx.py`가 `work/jb/<SID>_20xx/`에 N.txt·N.jpeg·manifest.json으로 풂. ZIP판도 처리) | X |
| `reference/` | 승인된 형식 예시(윤혜정 정리본 HTML, 지난 학기 HUB) | X |
| `work/` | 추출·OCR·중간 산출물 | X |

과목 코드: OMS1 구강악안면외과학1 · CONS 임상치과보존학 · IMPL 치과임플란트학 · ANAT 임상두경부해부학 · GERI 노인치과학 · PHARM 임상치과약물치료학 · ESTH 심미치과학

## 첫 세션에서 할 일 (한 번만)
1. `tools/*/` 스크립트에 하드코딩된 경로(`/home/claude/...`, `/mnt/user-data/outputs/...`, `/home/claude/tessdata`)를 저장소 기준 상대 경로로 바꾼다: 과목 작업 폴더 = `work/<SID>/`, JB 추출 = `work/jb/<SID>_20xx/`, 출력 = `docs/`(허브는 `docs/index.html`). 단일 파일판(`<과목>_JBL.html`)은 `work/`에 만들고 커밋하지 않는다.
2. 환경: 파이썬은 저장소의 가상환경 `.venv/`를 쓴다(`source .venv/bin/activate` 후 실행, 없으면 `/opt/homebrew/bin/python3.14 -m venv .venv && .venv/bin/pip install pymupdf pypdfium2 pillow playwright && .venv/bin/python -m playwright install chromium` — 스크립트가 Python 3.12+ 문법이라 시스템 3.11로는 안 됨). OCR은 Homebrew의 `tesseract`(kor 포함, `tesseract --list-langs`로 확인). 없으면 사용자 동의를 받고 설치.
3. 기존 OMS1·CONS 팩을 다시 빌드해 `docs/`와 결과가 같은지 확인.

## 과목 작업 절차 ("○○ 작업해줘")
1. `materials/<과목>/`과 `jb/`의 해당 과목 3개 판본(23·24·25판)을 확인. 강의자료는 **26년도 우선, 없으면 25년도**, 둘 다 없으면 사용자에게 말한다.
2. JB 분해: 판본 구조를 전부 읽고(연도 칸형 / 교수별 괄호형) `tools/<sid>/parse_<sid>.py` 작성 → 블록 수·번호 검증. 판본 간 같은 문제는 OTHER로 연결, 대조표에서 연결 안 된 블록 0.
3. 강의자료 읽기: `.venv/bin/python tools/matx.py <SID>` → `work/<SID>/mat/<파일>/`(t/ 텍스트층+PDF 주석 필기, o/ OCR — 텍스트층이 빈 쪽, i/ 쪽 이미지 폭 1100). 텍스트층 글자가 깨진 PDF는 전 쪽 OCR. 필기·그림·표는 i/ 이미지를 직접 본다. 필기의 '강조 페이지'·'시험문제' 메모를 찾는다. 정리본 키 ↔ 파일은 matx.py의 SRC 표 + subject.py LECMAP 폴더(쪽 이미지 `work/<SID>/lec/<폴더>`). **Mac의 한글 파일명은 NFD — unicodedata NFC로 정규화해서 비교.**
4. `subject.py`(과목 설정) → `lec_<키>.txt`(강의별 정리본) → `annot.txt`(문항별 대조) → `tables.txt` → `pred.txt` → `build4.py`.
   - 여러 강의를 병렬로 쓸 때: `tools/dump_review.py <SID>`로 문항·자료 안내를 만들고, 강의마다 원고는 `tools/<sid>/lec_<키>.txt`, 대조·표·예상은 `work/<SID>/parts/{annot,tables,pred}_<키>.txt`에 쓴 뒤 `tools/merge_parts.py <SID>`로 합친다(이번 전면 개편 방식: 강의별 작성 → 독립 검토자가 자료 대조·수정).
   - 원고 하나 점검: `tools/check_lec.py <SID> [키]`(문법·기출 ⭐ 연결·그림 쪽·쪽 범위 커버리지·밀도).
5. 검증(아래) → playwright로 과목 홈·JB·정리본·이미지·도구 동작 확인 → 커밋·푸시.

## 새 연도 강의자료(26년도 등)·새 강의·새 과목 — 스킬 `jbl-update`로 한 번에 완성본까지
- **`.claude/skills/jbl-update/SKILL.md`를 따른다**("26년도 자료 반영해 줘"·"○○ 정리본 만들어 줘"·`/jbl-update [SID…]`): 받기 → 연결 → 작성(처음부터 최종형 `RULES.md`) → 독립 검토 3회 → 화면 다듬기(🔑⚡·JB 해설·줄바꿈·표·예상·공부 전략) → 사용자 눈 QA(`QA.md`) → `sh tools/full_check.sh` → 배포·보고. 사용자 피드백을 받으면 RULES.md·QA.md에도 규칙을 더한다.

### (세부) 26년도 갱신 절차
- `guide/handoff/26년도_업데이트_절차.md` 그대로: 맥은 materials/에 PDF를 넣고 `sh tools/push_materials.sh [SID…]` 한 줄 → 클라우드에서 `sh tools/cloud_materials.sh` 뒤 대조·수정·검토·빌드·배포. 사용자 표시(형광펜·빈칸·메모·북마크·채점·중요)는 반드시 유지 — `guide/정리본_원칙.md` '사용자 표시 보존' 절.

## 절대 규칙
- **내용은 사용자가 준 강의자료와 JB에서만.** Claude 자체 지식 금지. 근거가 없으면 "근거 없음". 자료에 없는 약어·사실을 쓰지 않는다(예: 슬라이드에 없는 'ITP').
- **JB 문항은 하나도 빠짐없이.** 그림 문항은 잘리지 않게.
- **출제연도** = JB 괄호 연도(문항 첫머리 전체에서 찾기, `(24, 탈)`·`(14~)`·`(…,13,)` 변형 포함) ∪ 문항이 실린 연도 칸 ∪ 다른 연도 칸의 같은 문제. 실리지 않은 해를 붙이는 것은 절대 금지. 비슷하지만 다른 문항은 별개로 두고 '관련 문항' 링크만. 판(JB 파일) 연도는 표시하지 않는다.
- **JB 답안은 글자 불변**, 줄바꿈만 정리(나열은 한 줄에 한 항목, 문장 중간 끊김은 이어 붙임). 공백 제외 글자 비교로 검증.
- 그림 캡션은 필기에 설명이 있을 때만. 없으면 쪽 번호만.

## 정리본 형식 (사용자가 승인한 형식 — 구강외과1 기준)
강의별 정리본은 "쑥쑥 넘기며 틀을 잡고 → 다시 읽으며 디테일 → 이해·암기"용이다. **슬라이드·필기를 쪽 순서로 옮겨 적고 JB만 매치한 필사본 금지, 요약+JB 언급뿐인 얇은 정리본 금지. 필기는 보조(한 줄 ✍ 이해)이고 강의자료가 메인.** `reference/예시정리본_윤혜정_혈액질환.html`의 학습 페이지·전체정리표 수준을 기준으로 한다.

- 강의 첫 화면 '이 강의의 틀': `@MAP` 흐름 + 분류(`@G`)별 카드 목차 + ⭐ 많이 나온 순 + 출제 경향(짤/탈·형식·탈 성격·공부 전략).
- 카드 = 의미 단위 주제 하나. 머리: 번호 · 영문 제목 · 국문 부제 · 쪽 범위 · 한 줄 요지 · 태그.
- 본문 순서: `=` 🔑 핵심 한 줄 → `#` 소제목(정의/특징/치료처럼 의미 단위) → `-` 항목(한 줄에 사실 하나, 영어 뒤 한글 풀이, ①②③) → `|` 표(나란히 비교할 것) → `E:` ⭐ 시험포인트(몇 년에 어떻게, 함정) → `P:` 💬 교수님 강조 → `U:` ✍ 이해 → `F:` 그림(해당 내용 바로 아래, 캡션에 쉼표 금지) → `M:` ⚡ 암기 줄(카드당 보통 3~7줄 — 라벨·논리 순서, `.claude/skills/jbl-update/RULES.md` 6절).
- 강조: `{r:…}` 빨간 핵심어·수치(자동 빈칸 대상) / `==…==` 시험에 그대로 나온 문장 / `**…**` 용어 / `{u:…}` 25 대비 26 PPT 새·바뀐 내용(초록 NEW 26) / `{e:…}` 26 수업 강조·시험 예고(보라 26 강조 — 25에도 강조했으면 '(25년도에도 강조함)' · 강의 머리 `@UPD` 줄 = 강의 틀 제목 줄의 접힌 초록 알약 '25 → 26 바뀐 점 펼치기 ▸'(누르면 펼침)) / `{n:…}` 필기 구간(앞에만 ✍ — 뒤에 강의 내용이 이어지면 줄바꿈).
- 문법 전체와 예시는 `tools/SPEC.md`, 실제 원고는 `tools/oms1/lec_*.txt`, `tools/cons/lec_*.txt`.

## 페이지 구성 (바꾸지 말고 유지)
과목 홈(공부 순서 → 진행률 → 교수별 출제 경향·📌 공부 전략 → 강의 카드 → 2회 이상 출제) / 강의 탭(학습·정리표·비교표·기출·예상·플래시카드) / JB 문제(연도 배지 → 짤/탈 칩 → 📖 정리본 칩 → 대조 → 문제 → 답·해설·대조·주변부·다른 판본) / 비교표 / 기출 한눈표 / 기출 대장. 짤 = 이전 해에 한 번이라도 나온 문제, 탈 = 그 해 처음. 자료 시작 해는 '기준선'.

## 검증 (빌드 후 매번)
- 현 교수 기출 전부가 어느 카드의 ⭐ 시험포인트에 연결됨(누락 0), 정리본이 가리키는 문항 id가 실제 존재 — build4 출력 + `tools/check_lec.py <SID>`
- JB 원문 글자 불변, 대조표 연결 안 된 블록 0
- 출제연도: `tools/check_years.py`(문항·다른 판본 괄호의 해가 배지에 다 있는지 — 노인치과학 24·23판은 학번 +2), `tools/check_eyears.py`(⭐ 문구에 배지에 없는 해를 쓰지 않았는지)
- 자료에 없는 약어: `tools/check_abbr.py` — 걸린 약어는 쪽 이미지로 확인해 자료에 없으면 원래 용어로
- playwright: `tools/verify.py`(허브 홈에 모든 과목, 이미지 로딩, 형광펜·빈칸·실행취소·새로고침 후 복원, 콘솔 오류 0) + `tools/audit_design.py`(명암·긴 덩어리·가로 넘침) + `tools/tests/*.py`

## 사용자 피드백을 받았을 때 (매번 이 순서)
1. 피드백을 **원문 그대로** `guide/피드백기록.md`에 한 줄 추가하고, 규칙이 바뀌면 `guide/정리본_원칙.md`의 해당 항목을 고친다(예시도 갱신).
2. 어느 파일(원고 lec_*.txt / annot / tables / shell)을 어떻게 고칠지 먼저 한 문단으로 말하고 진행한다. 사용자는 대안을 여러 개 놓고 고르는 걸 선호한다 — 방향이 갈리면 2~3안을 제시.
3. 고친 뒤 빌드·검증·자기검토 체크리스트 → 결과를 사이트 기준으로 보고(어느 과목 어느 카드가 어떻게 바뀌었는지).
4. 같은 종류의 지적을 두 번 받지 않도록, 고친 규칙을 다른 과목 원고에도 적용해야 하는지 확인하고 사용자에게 묻는다.
5. **지시가 없어도** 스킬 `.claude/skills/jbl-update/`(RULES·QA·AGENTS·SKILL)를 최신 지시까지 갱신하고, 독립 담당에게 스킬 자기점검(스킬만으로 지금 품질이 나오는지·빠진 지시)을 시킨 뒤 고친다(사용자 10-07). 보고 끝에 "스킬에도 반영: …" 한 줄 — 절차는 SKILL.md '사용자 피드백을 받으면'.

## claude.ai 대화에서 작업한 결과를 받았을 때
- `JBL_HUB.zip`(허브): `JBL_HUB/JBL_HUB.html` → `docs/index.html`, `JBL_HUB/packs/*` → `docs/packs/`로 교체(README.md는 저장소 것 유지). 사용자가 직접 폴더를 바꿔도 된다.
- `JBL_master.zip`(도구·원고·지침): `.venv/bin/python tools/localize.py <zip>` → 출력된 CLAUDE.md·SPEC.md 차이 중 새 규칙만 손으로 합침 → 받은 과목을 재빌드해 `docs/`와 같은지 확인 → 커밋·푸시.
- `guide/정리본_원칙.md`·`guide/피드백기록.md`·`guide/과목노트_<SID>.md`는 다음 과목 작업 전에 반드시 읽는다(누적된 사용자 피드백).

## 클라우드 세션(원본 PDF가 없는 환경)에서 작업할 때
- 먼저 `guide/인수인계_클라우드.md`를 읽는다(A절 = 10-03 인계: 상태·자료 받기·남은 일·주의).
- 원본 PDF(`materials/`·`jb/`)와 `reference/`는 없다. `sh tools/cloud_setup.sh`로 환경을 준비하고, **`sh tools/cloud_materials.sh`로 작업용 추출본을 받는다**(origin `cloud-materials` 브랜치 → `work/`: 7과목 강의자료 쪽 이미지·텍스트·OCR, JB 3판본 추출, 강의 폴더 연결, ESTH 작업 조각 — 사용자가 2026-10-03에 "암호화 없이 그대로·7과목 전부"로 정해 올린 것. main에 합치지 않는다).
- 추출본을 받으면 원고·annot·build4 수정과 **전체 빌드 `sh tools/build_all.sh`**, 자료 대조(쪽 이미지 Read), check_lec·check_years·check_eyears·check_abbr를 클라우드에서 한다. 허브 코드(shell.html)만 고쳤으면 `sh tools/hub_all.sh`(= sync → `tools/rehub.py` → verify → audit → tests)도 된다.
- 맥에서만 되는 것: 새 PDF 추출(`tools/matx.py`·`tools/jbx.py` — pymupdf·tesseract·원본 필요)과 새 과목·새 연도 자료 반영 — `guide/handoff/로컬에서_할_일.md`에 적고 사용자에게 알린다.
- `work/`는 커밋되지 않는다 — `work/<SID>/parts`에서 고친 것은 `tools/merge_parts.py <SID>`로 `tools/<sid>/`에 합쳐야 남는다.
- 원본 자료를 더 올리는 것(원본 PDF·새 자료)은 사용자가 분명히 허락했을 때만.

## 커밋·푸시 정책
- 빌드·검증이 통과하면 `docs/`(와 바뀐 `tools/`)만 커밋하고 `git push`. 메시지 예: `CONS: 서덕규 26 강의자료 반영`.
- `materials/`·`jb/`·`reference/`·`work/`는 **절대 커밋하지 않는다**(.gitignore). 커밋 전 `git status`로 확인.
- 검증 실패 시 커밋하지 말고 사용자에게 무엇이 실패했는지 말한다.
- 푸시 후 Pages 반영까지 1~2분 걸린다고 안내.
