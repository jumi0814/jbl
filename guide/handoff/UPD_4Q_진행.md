# 4Q 진행 (11-04 시작)

사용자 원문·결정 = guide/피드백기록.md 11-04 · 계획(승인) = 아래 요약 · 내용 규칙 = .claude/skills/jbl-update/RULES.md 14절 · 담당 요약 guide/handoff/Q4_RULES_BRIEF.md

## 사용자 결정(11-04)
1. 주소: `jumi0814.github.io/jbl/` = 4Q · 3Q는 `/jbl/3q/` 보관 · 두 허브에 3Q⇄4Q 전환 · "용량커지거나 해서 렉 절대 안 생기게끔"
2. 26이 오면 25에만 있고 기출과 무관한 내용은 그냥 지움(표시도 함께)
3. 2026 3Q 실제 기출 = 4Q 분석 + 3Q 사이트에도 '2026 출제'로 추가
4. 4Q는 동기화·화면 설정만 이어받기(공부 시간·기록은 새로)

## 단계
- [x] P0 등록표 `tools/quarters.json`·`quarters.py` · `jblpaths`(J.Q·DOCS·HUB_DIR·docs_of·pack_path·sids)
- [x] P0 허브 정체성 `const Q=/*QCFG*/`(3Q = 원래 상수 · 4Q 따로) · NS 기반 정규식 · 4Q 첫 실행 가져오기(설정·토큰만) · 전환 링크(메뉴·홈) · 다른 쿼터 과목 주소 넘기기 · 빈 과목 달력 오류
- [x] P0 도구: build4(쿼터 docs·frozen 거부·fill_index·manifest) · rehub(--q·--stage·--site·아이콘) · sync_common·build_num(살아 있는 쿼터 전부) · jbx(4Q JB) · matx(materials/4Q) · cloud/push_materials · full_check(JBL_Q·tests4·check_25only) · 스크립트 SID 목록 → 등록표 · verify(과목 수)
- [x] P0 `tools/new_subject.py` — 시험 SID로 첫 build4 → 4Q 허브에 과목 뜸(q_empty) → 지움
- [x] P0 tests4: q_ident · q_isolation(한 브라우저 두 허브 — 3Q 기록 글자 그대로) · q_empty · q_perf(기준 perf_base.json)
- [x] P0 4Q 내용 규칙: RULES 14 · AGENTS B1Q·B2Q·PROF·HIT · QA 97~99 · SKILL '4Q 판' · 정리본_원칙 · guide/prof/README.md · Q4_RULES_BRIEF · check_25only
- [ ] P0 3Q 회귀: 3q-final 기준(worktree) vs 새 허브 코드(3Q 정체성) — 같은 실패 목록이어야 함
- [ ] P0 허브 점검(담당) → 고칠 목록 → 공통 shell에서 고침
- [ ] P0 전환: `tools/cutover.py`(git mv docs → docs/3q · 등록표 current=4q·3q frozen·4q docs=docs · rehub) → 배포 → 기기 확인(사용자)
- [ ] P1 2026 3Q 실제 기출 받기 → 과목·교수별 분석 · 적중 분석(HIT) · 교수 프로필(PROF) → 3Q 사이트 '2026 출제'(JBL_UNFREEZE=1 — 결정 3)
- [ ] P2 4Q 과목마다: new_subject → JB 분해 → TREND → 정리본(26 본문 / 없으면 25 임시) → annot·tables → 검토 → 예상·N제 → 검사 → 과목마다 중간 배포
- [ ] P3 26 강의가 나올 때마다 전면 갱신(25 무관 내용 지움) → 예상·N제 → 배포

## 받을 자료(사용자에게 보낸 순서)
1. 4Q 과목표(과목명·교수·강의 제목·주차 · 3Q와 이어지는 과목) 2. 2026 3Q 실제 기출 3. 4Q JB(판본 전부 · `20YY 4Q <과목> JB.pdf`) 4. 26 강의자료+필기 5. 25 강의자료+필기(26이 없는 강의 · 교과서) 6. 학기 중 새 26 강의

## 재개 메모
- 3Q 기준 회귀: scratchpad worktree base3q(3q-final) — `work/_tmp/base_ux_all.log` · 새 코드 회귀는 기준이 끝난 뒤 같은 명령(JBL_HTTP=1 ux_all)
- 3Q 기준(3q-final)에서 이미 실패(환경·낡은 테스트): ct · fakegist(판정 줄 없음 — 도우미) · fmt_cases(판정 줄 없음) · kt · legacy_restore·legacy_restore_107(work/ 필요) · ux10_num5 · ux11_fix · ux2_auto · ux2_device … (끝나면 전체 목록)
- 시험 사이트 미리 보기: `.venv/bin/python tools/rehub.py --site work/_tmp/qsite`(4q = 뿌리 · 3q = 3q/)
