# JBL 과목 팩 제작 스펙 (구강악안면외과학1 → 임상치과보존학에서 확정)

## 폴더 구조 (과목당 한 폴더 — 모든 과목이 같은 스크립트를 쓰고 `subject.py`·`assemble.py`·`parse_<과목>.py`만 다름)
- claude.ai 대화에서 받은 `JBL_master.zip` 반영: `python tools/localize.py <zip>` (경로 변환 + guide/·.claude/commands/ 복사, CLAUDE.md·SPEC.md는 차이만 출력)
- 공통: `tools/jblpaths.py`(저장소 기준 경로 — 스크립트는 여기서만 경로를 얻음) · `tools/jbx.py`(JB PDF → `work/jb/<SID>_20xx/`) · `tools/verify.py`(playwright 허브 검증)
- 경로: 과목 작업 폴더 `work/<SID>/`(jb_blocks.json·강의 쪽 이미지 `lec/`·OCR) · JB 추출 `work/jb/<SID>_20xx/` · 출력 `docs/`(허브 `docs/index.html` + `docs/packs/`) · 단일 파일판 `work/<과목>_JBL.html`(커밋 안 함)
- 파이썬은 3.12 이상(저장소 `.venv/`, f-string 문법 때문에 3.11 불가)
- `subject.py` 과목 설정 — SID·제목·색·교수, LECMAP(강의키 → 이미지 폴더·표시명), LEC_ORDER, PROF_LEC, COVER(기준선 연도), TIERS, MENT_PROF/MENT_ALL(학습부 멘트), PAGE_LABEL, IMG_ALIAS
- `parse_<과목>.py` JB(23·24·25판 ZIP 텍스트) → 문항 블록 (`jb_blocks.json`). JB 구조가 과목마다 달라 여기만 새로 씀
- `assemble.py` 문항 정규화·연도 괄호 파싱·OTHER(판본 간 같은 문제)·주석 병합·JB 쪽 이미지·대장·멘트·예상문제 파싱
- `reflow.py` JB 원문 줄바꿈 정리(글자 불변) · `emph.py` 빨간 핵심어 · `lecparse.py` 정리본 원고 파서 · `trend.py` 짤/탈·형식·전략
- `build2.py` 기출 대장 렌더러 · `build4.py` 팩 조립(정리본·비교표·예상·경향) + 허브·단일 파일판 출력 ← 실행 진입점
- `shell.html` 허브 템플릿(모든 과목 공통) · `annot.txt` 문항 주석 · `lec_<키>.txt` 정리본 원고 · `tables.txt` 비교표 · `pred.txt` 예상문제

## 한 과목 작업 순서
1. `python tools/jbx.py <SID>`로 JB 3판본을 `work/jb/<SID>_20xx/`에 풀고(N.txt + N.jpeg + manifest.json — 텍스트는 pdfium, 쪽 이미지는 폭 924) 전문을 읽어 구조(연도 칸형 / 교수별 괄호형)를 파악 → `parse_<과목>.py` 작성, 블록 수·번호 검증
2. 강의자료: `pymupdf`로 쪽 텍스트·이미지(폭 1100), 텍스트가 부족하면 `tesseract -l kor+eng` OCR. 6슬라이드 핸드아웃은 셀 단위로 잘라 슬라이드 번호로(보존학 WHT). 강의실 촬영본은 슬라이드 사진 영역만 OCR. 텍스트만 온 파일은 그대로 필기본(그림 없음)
3. `subject.py` 채우기 → `assemble.py`의 OTHER·tier·연도 규칙 조정 → `annot.txt`(문항마다 v= / lec= / A: M: N:, 출처 [[키:쪽]])
4. `lec_<키>.txt` 7개 내외(형식은 아래) → `tables.txt`·`pred.txt` → `python3 build4.py` → 검증 출력(연결 누락 0, 없는 문항 0) → playwright로 화면·도구·이미지 확인
5. 출력: `docs/index.html`(허브) + `docs/packs/<SID>.js` + `docs/packs/<SID>.img.<강의>.js`, 단일 파일판 `work/<과목>_JBL.html` → `python tools/verify.py`
   - 강의 쪽 이미지 원본(`work/<SID>/lec/`)이 없으면 지금 `docs/packs/`에 있는 같은 쪽 이미지를 그대로 씀(재빌드해도 그림이 빠지지 않음)

## 공통 코드 동기화·전 과목 빌드 (tools/sync_common.py · tools/build_all.sh)
- 공통 생성 코드(shell.html·build4.py·lecparse.py·trend.py·reflow.py·emph.py·template2.html)는 **tools/cons/에서만 고친다**. SPEC.md는 tools/SPEC.md가 원본
- `.venv/bin/python tools/sync_common.py` — cons → oms1·impl·anat·geri·pharm 복사(SPEC.md 사본 포함) · `--check` 사본끼리 다르면 종료 코드 1 · `--build` 복사 후 6과목 build4 → verify.py → audit_design.py
- `tools/build_all.sh` = `sync_common.py --build --all`(tests/ux_all.py가 있으면 그것까지)
- build2.py는 과목마다 마지막 출력 줄(`J.work('<SID>', 'build2_view.html')`)이 달라 복사하지 않는다 — 고칠 때는 과목별로
- 과목별로 달라야 하는 설정은 subject.py의 선택 항목(`getattr(S, '이름', 기본값)`)으로 — 없으면 기존 동작
- 기준선: work/는 메인 저장소와 공유되어 강의 이미지·강의 이름이 바뀔 수 있으므로, 코드 변경 전후 비교는 "지금 work/로 HEAD 코드를 빌드한 docs/"를 기준으로 한다(빌드는 결정적 — 같은 입력이면 같은 출력)

## lec_<키>.txt 문법
```
#LEC 키 | 제목 | 교수 | 연도 | 파일 설명 | 쪽수
! 머리말(자료 출처·강조 쪽·주의)
@MAP 흐름 → 흐름 → 흐름
@G ① 분류 이름
## 영문 제목 | 국문 부제 | 쪽범위 | 태그 | jb=Q01,Q02
> 한 줄 요지
= 🔑 핵심 한 줄  ({r:빨강} ==형광(시험에 나온 문장)== **굵게**)
# 소제목                                 - 항목 (① ② ③, 영어 뒤 한글 풀이)
| 표 머리 | ... |   | 행 | ... |
E: Q01,Q02 | ⭐ 시험포인트 — 몇 년에 어떻게, 함정 (한 줄에 하나)
P: 💬 교수님 강조      U: ✍ 이해(필기 한 줄)
F: 19=캡션, 20=캡션, 21   (캡션 안에 쉼표 금지; 보조 자료의 쪽은 `DH5:13=캡션`처럼 키를 앞에 — subject.py의 LECMAP에 보조 키와 IMG_ALIAS를 등록)
M: ⚡ 암기 줄({r:} 포함)
```

## 규칙
- 답·해설·정리본은 강의자료와 JB에서만. 근거 없으면 "근거 없음". 자료에 없는 약어·사실 금지. 그림 캡션은 필기에 설명이 있을 때만
- 출제연도 = 괄호 ∪ 문항이 실린 연도 칸 ∪ 다른 연도 칸의 같은 문제. 괄호 파싱은 `(24, 탈)` `(14~)` `(…,13,)` 변형 처리. 실리지 않은 해 금지
- JB 답안 글자 불변(줄바꿈만 정리). 강의자료 26 > 25, 둘 다 있으면 26 본문 + 25 그림/보조 키
- 검증: 현 교수 기출 전부 ⭐ 시험포인트 연결, 문항 id 존재, 이미지 로딩, 형광펜·빈칸·실행취소·새로고침 복원

## 렌더링 규칙 (v6, lecparse.render_block — render_key / render_item / render_recall가 호출)
- `split_top(s, ' / ')`: 괄호 밖의 ' / '에서만 분리. 조각 최소 길이 14자 미만이면 분리하지 않음
- `split_circ`: 괄호 밖 ①②③…이 3개 이상이면 (앞머리, 항목들)로 분리 → `<ol class="circ">`
- 🔑(=)·⭐(E:)·💬(P:)는 render_key, 항목(-)은 render_item(80자 초과 시만 ① 분리, 120자 초과·3조각 이상일 때만 ' / ' 분리), ⚡(M:)는 render_recall
- 연속된 E: 줄은 한 `.c-exam` 블록 안의 `<ul class="exlist">`로 합침
- CSS는 shell.html 끝의 `/* ===== v5 가독성·디자인 통일 ===== */` 블록이 이전 규칙을 덮어씀 — 디자인 변경은 이 블록에서

- v6: render_block = split_enum(①·1.·A)) → 라벨 목록('라벨: 내용 / 라벨: 내용') → split_lead+segments → segments(' / ', '; ', ' · ', 문장, '→' 5단계↑는 번호 단계). _rebalance로 ==·{r:} 짝 맞춤. 예상문제 답(a_raw)·정리표 세부·✍ 이해·⭐ 목록에도 적용. CSS는 shell.html의 'v6 가독성' 블록
- 디자인 감사: tools/audit_design.py(명암 대비 3.0 미만·230자 넘는 덩어리·가로 넘침) — 빌드 후 매번 실행

## 허브 도구 v2 (2026-09-26, shell.html)
- 형광펜·빈칸(Kit): 저장 단위 = 카드(data-aid). 기록 {t,x,i,c}. 탭 = 어절(공백·/·()·,;:·→=| 경계, 끝 문장부호 정리), 드래그 = 어절 단위로 넓힌 한 묶음(data-g) — 조각이 여러 개여도 한 번에 열림/지움. 마우스=누른 채 끌기, 펜=바로 끌기, 손가락=0.28초 길게 누른 뒤 끌기(짧은 스와이프는 스크롤). 칠한 곳을 다시 누르면 지움, 다른 색이면 색만 변경. 좌표→글자 위치는 직접 판정(hit)
- 복원: 정확 일치 → 공백·구분기호 무시 느슨한 일치. 카드 aid는 내용 기반(강의키:slug(en,ko)), 옛 index aid는 data-alt로 자동 이관(표시·'이해함' 모두)
- 다른 창 동기화: storage 이벤트로 같은 과목 표시를 다시 읽음
- 공부 시간: 자동 측정(기본 켬, 과목을 연 동안만) · 8분 무활동/다른 창이면 멈춤 · 과목·강의별 기록(time, timed) · 시계 누르면 오늘·7일 팝업
- 그림: 바깥 누르면 닫힘, 그림 누르면 그 자리 확대/맞추기, 드래그 이동, Ctrl+휠, ←/→·스와이프, 아래로 쓸어 닫기, +/- 키
- 안전: 5분마다 자동 백업(최근 5개, autobak.*) · 복원 = 합치기(기본)/덮어쓰기/자동 백업 시점 · navigator.storage.persist · 홈에 백업 경과일 알림
- 편의: 이어서 보기(과목별 마지막 위치), 🖍 내 표시 모아보기(_marks), ? 도움말
- 테스트: tools/tests/kt*.py(도구), reg.py·ct.py(회귀), audit_design.py(디자인) — 모두 docs/index.html(J.HUB_URL)을 열고 스크린샷은 work/_tmp/
