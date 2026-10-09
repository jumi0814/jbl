> 새 연도 자료·새 강의·새 과목 정리본은 `.claude/skills/jbl-update/SKILL.md`를 따른다(이 명령은 10-02 판 — RULES.md·QA.md가 없다).

$ARGUMENTS 과목의 JBL 팩을 만들거나 갱신한다.

1. `CLAUDE.md`, `guide/정리본_원칙.md`, `tools/SPEC.md`를 먼저 전부 읽는다. 기준 원고 `tools/oms1/lec_DD1.txt`와 `tools/cons/lec_FRC.txt`를 열어 형식·밀도를 확인한다.
2. `materials/$ARGUMENTS/`의 강의자료 목록을 보여주고, 강의마다 26/25년도 중 무엇을 쓸지, 빠진 강의가 있는지 먼저 나에게 보고한다. 빠진 게 있으면 진행 전에 묻는다.
3. 절차대로 진행한다: JB 분해·검증 → 강의자료 정독(OCR 포함) → subject.py → annot.txt → 강의별 lec 원고 → tables.txt → pred.txt → 빌드.
4. 강의 원고를 하나 끝낼 때마다 `guide/정리본_원칙.md` 8번 체크리스트로 자기검토하고 결과를 짧게 보고한다.
5. 빌드 로그(연결 누락·없는 문항), playwright 검증 결과를 보여준 뒤 이상이 없으면 `docs/`와 바뀐 `tools/`만 커밋·푸시한다. `git status`로 materials/jb/reference/work가 빠진 것을 확인한다.
6. 마지막에: 강의별 카드 수·그림 수·⭐ 연결 수, 확인이 필요한 점(자료 부족·JB와 슬라이드 불일치), 사이트 반영 안내를 보고한다.
