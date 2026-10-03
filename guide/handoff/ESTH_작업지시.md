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

## 재개 메모 추가 (10-03 오후 — 사용 한도로 멈춤, 여기서 이어서)
- **상태**: 7과목 빌드 통과 · verify PASS · audit PASS(로그 work/_tmp/build_all_1003b.log) · tests/ux_all 진행 중이었음(ux3_rest까지 ok). 실패 3개 원인: ux2_load(과목 수 6 가정 → NP로 고침) · ux2_learn(EXT 기준 480→472·5000→5100 — 고침) · **ux2_keys 타임아웃(Page.click 30초) — 아직 원인 미확인, 단독으로 다시 돌려 볼 것**.
- **docs는 아직 커밋 안 함**(작업 폴더 /Users/jumisong/JBL/.claude/worktrees/materials-aesthetics-jb-folders-d4ae36 에 빌드본이 있음 — 다른 곳에서 이어 가면 `sh tools/build_all.sh`로 다시 빌드). tools·guide는 커밋·푸시함.
- **ESTH 검토 2회차**: INT(20건)·COL(18건)·MAT(17건) 끝 — 보고 work/ESTH/parts/R3_<키>.md. FUN·PLAN·SPE·VEN은 진행 중이었음(R3 파일이 없으면 그 강의 2회차를 다시 돌릴 것 — guide/handoff/ESTH_검토_BRIEF.md '2회차'). 끝나면: `tools/merge_parts.py ESTH` → `tools/sync_common.py` → esth build4 → check_lec·check_years·check_eyears·check_abbr → verify → 3회차(새 문제 0이 될 때까지).
- **빌드 규칙 바꿈(tools/cons/build4.py Q2CARD)**: annot `lec=<키>:<쪽>`의 주 강의 → 그 쪽을 담은 카드가 주 카드(ESTH assemble가 q['lkp']로 넘김). 그래서 검토자들이 📖 연결을 맞추려고 보조 카드 머리에서 뺀 `jb=`를 **되살릴 것**(카드 머리 기출 칩용): INT 카드4(R04) · PLAN 54Y/M 카드(U02)·p.17 카드(T12) · COL Light·Human Vision 카드(Q13) · MAT p.10 Opacity 카드(Q18) — R2/R3 보고서에 적힌 곳. 되살린 뒤 빌드해 questions.md '연결 강의'와 📖 카드가 annot 쪽과 맞는지 확인. MAT R3 보고서에 '다른 강의에서 확인할 문항 18개' 목록 있음.
- **강의 이름**: #LEC 제목을 강의자료 원래 이름으로 고침(PLAN·SPE·COL·MAT) — 다시 빌드해야 화면에 반영.
- **새 사용자 요청(10-03)**: "강의자료화면이 자꾸 미세하게 간헐적으로 왼쪽 오른쪽으로 작게 움직이는 흔들리는 오류" — 아직 손 못 댐. 재현(1280·820·1180, 학습 탭에서 가만히 두거나 스크롤·시계 1초 갱신·도구 막대 켜기) → shell.html 수정(공통은 tools/cons에서만, sync_common) → 회귀 테스트 추가.
- **그다음**: 6 빌드·검증 마무리 → 커밋(docs 포함)·푸시 → 7 검토 회차 마무리 → 8 세 화면 확인·배포 → 9 전 과목 최종 점검(guide/handoff/맥_세션_시작.md 7번 — 맥 확인 146건은 끝: review_final/M_<SID>.md, 판단 불가 7건·제안 43건은 사용자 확인 목록으로) → 10 배포 → 11 최종본(JBL_HUB.zip은 work/에).
- (추가) PLAN 검토 2회차도 끝(21건 — work/ESTH/parts/R3_PLAN.md). 남은 2회차: FUN·SPE·VEN(R3 파일 유무로 확인). PLAN R3 보고: INT·VEN·FUN·COL `!` 머리말에 내부 문항 id가 든 📣 문장 9개 — 내용 설명으로 바꿀 것.
- (추가) VEN 검토 2회차도 끝(19건 — R3_VEN.md): Q23 주 카드 = p.23 · T14·U02 짧은 ⭐ 추가 · 본문 {r:} 1.9% → 13.5%(자동 빈칸이 본문 답을 못 가리던 것). **다른 6강의도 본문 {r:}가 2~7%** — DD1 수준(약 10~14%)으로 올릴지 3회차에서 판단·손질(핵심어·수치만, 카드당 30% 이하). 남은 2회차: FUN·SPE. merge_parts를 다시 돌릴 것(annot_VEN·tables_VEN이 커밋 뒤에 바뀜).
