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
- [x] 1 자료 확인 · [x] 2 폴더·목록 · [x] 3 JB 분해 · [x] 4 자료 정독 · [x] 5 원고 · [ ] 6 빌드·검증 · [ ] 7 검토 2회차 · [ ] 8 확인·배포
- 이어서(사용자 10-03): [ ] 9 전 과목 최종 점검(맥_세션_시작 2·3·4·7 포함 — 7과목 정리본·JB·주석·정리표 + 허브 기능 전부) · [ ] 10 최종 배포·사이트 확인 · [ ] 11 최종본 전달

## 재개 메모 (10-03 — 마지막으로 한 일·다음 할 일)
- 강의 키: INT Introduction(26) · FUN Fundamentals of esthetic dentistry(26) · PLAN 심미수복에서의 진단 및 치료계획(26) · SPE Special Effects(25) · COL 색(안진수 25) · MAT 심미수복재료(25) · VEN Direct veneer, Indirect composite resin inlay(25) · 보조 키 INT5·FUN5·PLAN5(25판 — 슬라이드 동일, 필기는 26 파일에 합본). 쪽 이미지 폴더 E01i~E10i(tools/matx.py SRC).
- 4·5단계 끝: 강의별 작성자 7명(guide/handoff/ESTH_원고_BRIEF.md) → 원고 7개(카드 105 · 그림 285 · ⭐ 91 · 표 89) + work/ESTH/parts/{annot,tables,pred}_<키>.txt → `tools/merge_parts.py ESTH`로 tools/esth/annot·tables·pred(대조 61 · 비교표 50 · 예상 93). 작성자 보고 work/ESTH/parts/R_<키>.md.
- 빌드: ESTH build4 통과(⭐ 91/91 구조화 · 연결 누락 0 · 없는 문항 0) · check_lec 7강의 ✗ 0 · check_years 0 · check_eyears 0 · check_abbr 4개(TSR·APS·BFD·BPA — 모두 슬라이드 그림 속 글자).
- 등급: B = T21~T23(여인성) · C = T10·T11·T14·U01(서덕규 cervical, '23년도 시험범위 아님')·T17(증례, '출제되지 않을 것으로 예상'). T16은 PLAN p.25-29 증례와 같은 형식이라 A.
- 함께 한 일: 6과목 '맥에서 확인할 것' 146건(맞음 123·고침 16·판단 불가 7 — guide/handoff/review_final/M_<SID>.md) · trend.py·build4 '짤 비율 %' → '짤 j/n'(사용자 09-29) · build4 옛 문구 3개 · UNREC 범위 · OMS1 그림 판정(S20-4·'경사진') · tests 3개(ux3_home·ux4_nav·ux_u22)를 ESTH 준비 상태에 맞춤 · audit_design SUBJ에 ESTH.
- 진행 중(10-03): 7과목 전체 빌드·검증 `sh tools/build_all.sh`(로그 work/_tmp/build_all_1003a.log) · ESTH 독립 검토 1회차(검토자 7명 — guide/handoff/ESTH_검토_BRIEF.md, 보고 work/ESTH/parts/R2_<키>.md). 검토가 끝나면 merge_parts → ESTH build4 → check 4종 → 커밋·푸시 → 검토 2회차(새 문제가 안 나올 때까지) → 8단계.
- 사용자 확인 필요(모아 둘 것): R19 JB 답이 자료와 반대 · R06 opalescence 정의가 두 강의에서 다름 · Q16 근거(24년 porcelain 표)가 25 자료에 없음 · Q23·Q25·T12·T21~T23 근거 강의(2024 Laminate veneer·여인성 2024 RBR·서덕규 2021)가 materials에 없음 — 더 과거 자료를 받을지.
