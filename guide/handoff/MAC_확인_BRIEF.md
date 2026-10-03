# '맥에서 확인할 것' 처리 안내 — 과목 하나를 맡은 작업자용 (2026-10-03)

배경: 10-02 클라우드 '정리본 최종 검토'(guide/handoff/review_final/R_<SID>_<KEY>.md)는 강의자료 원본이 없어 자료를 봐야 판단할 수 있는 것을 각 보고서의 `## 맥에서 확인할 것` 절에 남겼다(6과목 146건). 이 맥에는 원본이 있으니 하나씩 쪽 이미지로 확인하고 원고를 고친다.

저장소 = 이 안내 파일이 있는 저장소의 루트. 파이썬 `.venv/bin/python`. 보고는 한국어.

## 먼저 읽기
- `CLAUDE.md` '절대 규칙'·'정리본 형식' · `guide/정리본_원칙.md` 2·5·7-1·7-4절 · `guide/과목노트_<SID>.md`
- 원고 문법: `tools/SPEC.md` 31~64행

## 할 일 (맡은 과목의 R_<SID>_*.md 전부)
1. 각 보고서의 `## 맥에서 확인할 것` 항목마다:
   - 가리키는 쪽의 이미지를 Read 도구로 직접 본다 — 쪽 이미지 = `work/<SID>/lec/<폴더>/<쪽>.jpg`(폴더 = `tools/<sid>/subject.py`의 LECMAP[키][0]) 또는 `work/<SID>/mat/<파일id>/i/<쪽>.jpg`(파일 ↔ 키는 `work/<SID>/review/materials.md`). 텍스트층·OCR은 `work/<SID>/mat/<파일id>/t|o/<쪽>.txt`.
   - JB 원문이 필요하면 `work/jb/<SID>_2025|2024|2023/<쪽>.txt|.jpeg`.
   - 판정: **맞음(그대로)** / **고침**(원고가 자료와 다름 — 자료 원문대로 최소 수정) / **판단 불가**(필기 판독 불가 등 — 이유).
2. 고칠 때: `tools/<sid>/lec_*.txt`(필요하면 같은 과목의 annot.txt·tables.txt·pred.txt)에서 **최소 수정**(사용자의 형광펜·빈칸이 글자 위치에 붙어 있음 — 카드 나누기·합치기·대량 재작성 금지). 자료에 없는 사실·약어는 쓰지 않는다. JB 답 원문은 바꾸지 않는다.
3. 같은 보고서의 `## 제안` 절은 손대지 말고, 자료를 보고 판단에 도움이 되는 사실만 메모(사용자가 결정).
4. 다 고친 뒤 `.venv/bin/python tools/check_lec.py <SID>` → ✗ 0 · `.venv/bin/python tools/check_eyears.py <SID>`.
5. 빌드(build4)·docs 수정·git 커밋은 하지 않는다. 다른 과목 파일은 고치지 않는다.

## 보고
`guide/handoff/review_final/M_<SID>.md`:
```
# <SID> 맥 확인 결과 (10-03)
| 보고서 | 항목 | 판정 | 근거(쪽·자료 원문) | 고친 곳(파일:줄 요지) |
## 제안 절 메모(자료로 확인한 사실만)
## check_lec·check_eyears 결과
```
최종 답은 3줄(맞음 n · 고침 n · 판단 불가 n · check_lec 결과).
