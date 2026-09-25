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
