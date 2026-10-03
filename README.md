# JBL 작업용 추출본 (cloud-materials 브랜치) — 2026-10-03

사용자(jumi0814)가 10-03에 "암호화 없이 그대로 · 7과목 전부"로 정해 올린, **클라우드 세션 작업용 추출본**이다. main(사이트·도구)과는 따로 둔다 — main에 합치지 않는다.

- `work/jb/<SID>_2023|2024|2025/` JB 3판본 추출(N.txt 글 · N.jpeg 쪽 이미지 · manifest.json) — 7과목
- `work/<SID>/mat/<파일id>/` 강의자료 추출: `t/` 텍스트층(+필기 주석) · `o/` OCR · `i/` 쪽 이미지(폭 1100) · `index.json`
- `work/<SID>/lec/<폴더>` → `../mat/<파일id>/i` 연결(정리본 키 폴더 — subject.py LECMAP)
- `work/<SID>/parts/`·`review/`·`notes/` 강의별 작업 조각(대조·비교표·예상문제)·검토 보고·작업 메모
- 원본 PDF(materials/·jb/)는 올리지 않았다(맥에만).

쓰는 법(저장소 main 체크아웃에서): `sh tools/cloud_materials.sh` → 저장소의 `work/` 아래로 풀림(.gitignore라 커밋되지 않음).
