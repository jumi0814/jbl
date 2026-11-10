# DONE_빌드 — 11-10 전면 점검·개선 · 빌드 쪽(W1 build4 + W3 그림 파일 빌드)

담당: worktree 담당(빌드 쪽 — 앞 담당이 한도로 멈춰 두 번째 담당이 이어서) · 지시문 `guide/handoff/upg1110/agents/UPG_B.md` · 기준 커밋 b714aca8 · 브랜치 `worktree-agent-ae5c8cca242a40c1a`
맡은 파일: `tools/cons/build4.py`(+ sync 사본) · `tools/quarters.json`·`tools/quarters.py` · `tools/jblpaths.py` · `tools/verify.py` · `tools/check_links.py` · `tools/tests4/q_perf.py` · 새 `tools/tests4/q_imgbuild.py` · `tools/SPEC.md`(빌드 절) · 이 보고
건드리지 않은 것: `tools/cons/shell.html`(허브 담당) · `lecparse.py`·`trend.py`·`build2.py`·`assemble.py`(맡은 파일 밖 — 필요한 고침은 build4 안에서) · **`docs/`는 커밋하지 않음**(메인 결정 11-10 — 허브 담당과 부딪힘 · 다시 빌드한 4Q 빈 팩은 시험·비교에만)

## 진행(항목이 끝날 때마다 고침)
- [x] 읽기: BRIEF_공통 · PLAN · R_DESIGN §0·§3·§5 · R_NAV A10·A17·A19 · build4·jblpaths·quarters·new_subject·verify·check_links·q_perf
- [x] 앞 담당 작업분(f0e4f6c5) 확인 — 아래 표
- [ ] 1. D 검사(q_imgbuild) · 2. A 검사(4Q 빈 팩 10개 다시 빌드·비교) · 3. check_links · 4. verify · 5. q_perf · 6. B grep 보고 · 7. SPEC · 8. 전체 검사

## 앞 담당이 한 것 — 이어받을 때의 실제 상태(코드 읽기 + 읽기 전용 측정)
| 항목 | 코드 | 검사 |
|---|---|---|
| A 빈 과목 | 들어감(build4 `STUB`) | 안 됨 — worktree `docs/packs` 10개는 옛 팩 그대로 |
| B 라벨 | 들어감(build4 4곳) | 허브·테스트 grep 보고 안 씀 |
| C cite 쪽 | build4 들어감(`_cnum`) | `check_links.py` 손 안 댐 |
| D 그림 파일 | 들어감(quarters.json·quarters.py·jblpaths·build4 `IMGFILES`) | q_imgbuild를 한 번 돌린 흔적(시험 폴더가 남음 = FAIL 1개 이상 — 어느 줄인지 모름) |
| E 도구 | `q_imgbuild.py`만 씀 | `verify.py`·`check_links.py`·`q_perf.py` 손 안 댐 |
| SPEC·보고 | 안 씀 | — |

읽기 전용 측정(배포본 그대로):
- 3Q 팩에서 새 규칙에 걸릴 것 = GERI `[[OHQ:쪽]]` 1개 · PHARM JB 원본 쪽 `23q4-17~20` 4개 — 그 밖 0.
- 3Q 7과목 `data-img`(4,001개)·cite(15,805개) 키는 전부 묶음에 있음 → verify의 새 키 검사를 3Q에 걸어도 새 실패 없음.
- `check_links.py`는 `docs/packs`가 박혀 있어 `JBL_Q=3q`로는 3Q 팩(`docs/3q`)을 못 찾음.

(아래에 항목별 결과를 덧붙임)
