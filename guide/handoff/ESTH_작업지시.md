# ESTH(심미치과학) 작업 지시 — 사용자 10-02 요청 원문 기준

> "심미치과학 강의자료 정리본과 jb문제를 다른 과목처럼 아주 최적으로 효과적 효율적으로 공부할 수 있는 형태로 각 강의자료(각 강의주제마다 가장 최신년도 강의자료 사용하면서) 정리본을 만들고 심미치과학 과목탭을 완성시켜줘. 이후 강의자료 정리본 및 jb 문제 등 해당 과목탭의 모든 것에서 빠진 내용,누락, 잘못된 내용, 효과적이지 않은 구조 등등 모든걸 면밀히 검토하면서 가장 최적으로 고쳐서 개선해주면서 심미치과학 또한 다른 과목탭과 비슷하게 최상의퀄리티로 완성될 수 있게끔 해줘!"

## 먼저 읽기
CLAUDE.md(절대 규칙·정리본 형식·검증) · guide/정리본_원칙.md · guide/피드백기록.md · tools/SPEC.md · 기준 원고 tools/oms1/lec_DD1.txt · tools/cons/lec_FRC.txt · guide/handoff/맥_세션_시작.md 5번의 '새 과목이라 함께 고칠 곳' 목록.

## 순서 (단계마다 검증 → 커밋·푸시, 진행은 한국어로 짧게 보고)
1. `materials/심미치과학/` 파일 목록 → 강의 주제별로 26년 자료(없으면 25년)를 고른 표를 보고. JB 3개 판본(23·24·25판) 확인.
2. `tools/esth/` 만들기(공통 파일은 tools/cons에서 복사, 과목별 subject.py·assemble.py·parse_esth.py 새로) · 6과목만 적힌 목록 전부에 ESTH 추가(맥_세션_시작.md 목록).
3. JB 분해: parse_esth.py → 블록 수·번호 검증, 판본 간 같은 문제 OTHER 연결, 대조표 연결 안 된 블록 0, 출제연도 규칙(괄호 연도 ∪ 실린 칸 ∪ 다른 칸 같은 문제 — 없는 해 금지), JB 답 글자 불변.
4. `.venv/bin/python tools/matx.py ESTH` → 강의자료 정독(텍스트층·OCR·쪽 이미지·필기의 '강조'·'시험문제' 메모).
5. 강의별 lec_<키>.txt — 승인 형식(구강외과1 기준: 이 강의의 틀 @MAP·@G·⭐ 많이 나온 순·출제 경향 / 카드 = 🔑 → 소제목 → 항목 → 표 → ⭐ → 💬 → ✍ → 그림 → ⚡). 필사본·얇은 정리본 금지. 자료에 없는 내용·약어 금지.
6. annot·tables·pred → build4 → check_lec·check_years·check_eyears·check_abbr → verify·audit·tests → 허브에서 '준비 중' 해제 확인, SJC.ESTH 색 지정.
7. **독립 검토 2회차**: 강의마다 ⭐ ↔ JB 답 대조, 빠진 내용·누락·잘못된 내용·효과적이지 않은 구조·빨강 과다를 자료와 대조해 고침(다른 과목과 같은 품질). 새 문제가 안 나올 때까지.
8. playwright로 과목 홈·JB·정리본·이미지·도구(형광펜·빈칸·공부 시간·북마크) 확인(1280·820 터치·1180 터치) → main 배포 → 사이트 확인.

## 멈췄다 이어 갈 때
git log 마지막 커밋과 이 문서 아래 진행 표시를 보고 이어서. 사용자 결정이 꼭 필요한 것만 2~3안으로 묻고, 그 외에는 멈추지 말고 진행.

## 진행 표시
- [x] 1 자료 확인 · [x] 2 폴더·목록 · [x] 3 JB 분해 · [ ] 4 자료 정독 · [ ] 5 원고 · [ ] 6 빌드·검증 · [ ] 7 검토 2회차 · [ ] 8 확인·배포
- 이어서(사용자 10-03): [ ] 9 전 과목 최종 점검(맥_세션_시작 2·3·4·7 포함 — 7과목 정리본·JB·주석·정리표 + 허브 기능 전부) · [ ] 10 최종 배포·사이트 확인 · [ ] 11 최종본 전달

## 재개 메모 (10-03 세션 — 마지막으로 한 일·다음 할 일)
- 강의 키(정함): INT Introduction(26 260911) · FUN Fundamentals of esthetic dentistry(26 260911) · PLAN 심미수복에서의 진단 및 치료계획(26 260918) · SPE Special Effects(25 250926) · COL 색(안진수, 25 251010) · MAT 심미수복재료(25 251017) · VEN Direct veneer, Indirect composite resin inlay(25 251024) · 보조 키(25판) INT5·FUN5·PLAN5. 쪽 이미지 폴더 E01i~E07i(본 키) · E08i~E10i(보조) — `tools/matx.py` SRC['ESTH'](커밋 전, 작업 폴더에만).
- 한 일: `tools/jbx.py ESTH`(work/jb/ESTH_2023·2024·2025) · `tools/matx.py ESTH`(work/ESTH/mat, lec 링크) · `tools/esth/parse_esth.py` 작성 — 25판 64·24판 60·23판 44블록(끝 대비표 '표' 포함), 블록 밖 줄은 멘트·표지·칸 제목뿐.
- 정본 설계(assemble.py에 쓸 것): 25판 2024 칸 Q01~Q28(미복원 범위 3-5 → Q03) · 2023 칸 비포인터 R03·R04·R05·R06·R07·R08·R09·R10(10-11)·R14(14-15)·R18·R19·R20·R22 · 2022 칸 S04·S12·S14 · 24판 2021 칸 T03·T08·T09·T10·T11·T12·T14·T15·T16·T17·T20·T21·T22·T23 · 23판 2020 칸 U01~U05 = 61장(미복원 11). 24판 2023 칸 두 번째 '4.'=4b(=R06), 2022 칸 두 번째 '6.'=6b(=R07). 2021 #6 치관 폭 = R07과 같은 문제로 연결(→ 23·22·21·20). Q06은 24판 2022 칸 괄호 (23,21,20)의 23 포함. 대비표 3개 = T15의 OTHER.
- 2·3단계 끝(10-03): tools/esth/ 공통 파일 복사 + subject.py·assemble.py(정본 61 · 판본 간 중복 107 · 미연결 0) · 6과목 목록에 ESTH(check_years·check_eyears·check_abbr·dump_review·aidlock_enrich·tests annot_text·card_text·aidlock_test, sync_common DST·SUBJ_ORDER) — legacy_base·tests/legacy_restore는 옛 허브에 ESTH가 없어 6과목 그대로. audit_design SUBJ·RED_REP와 shell SJC.ESTH(#2F7A3E 예정)는 원고가 생긴 뒤.
- 자동 이어가기: 예약 작업 `jbl-auto-resume`(매시간, 하트비트 work/_resume/heartbeat가 2시간 넘게 멈추면 /Users/jumisong/JBL에서 이어서). 작업 중에는 하트비트를 자주 갱신.
- 다음: 4단계 자료 정독 → 5단계 강의별 원고(lec_INT·FUN·PLAN·SPE·COL·MAT·VEN) + work/ESTH/parts/annot_·tables_·pred_<키>.txt → merge_parts → build4.
