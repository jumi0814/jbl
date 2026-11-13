# DONE_W6 — 렉(표 맞춤·그리기 뒤 일·팩 이어 받기·2단계 스위치) · 11-12 시작

지시문: `guide/handoff/upg1110/agents/UPG_H5_렉.md`(+ 11-12 덧붙임) · 설계 `R_DESIGN_설계.md` §4 · 측정 `R_AUDIT_1104_측정.md` #3·#10·#11·#17 · 고치기 전 기준 `DONE_W0.md` 6번 표.
맡은 파일: `tools/cons/shell.html` · `tools/SPEC.md` · 이 보고. 메인 저장소에서 혼자 일함 — **커밋·푸시·stash 안 함(메인이 함)**.
순서: 1번(표 맞춤) → 지킴이 → 2번(그리기 뒤 일) → 3번(팩 이어 받기) → 지킴이 → 4번(스위치 `LS 'cvh'` 기본 끔).
지킴이 = `tools/tests4/q_pos.py` 전체 + `tools/tests/ux_nav`·`ux_kitfrev`·`ux_marks`·`ux2_jbq`(JBL_HTTP=1 · 3Q 스테이징).

진행(항목 하나 끝날 때마다 고쳐 씀 — 한도로 멈춰도 여기서 이어 감):

- [x] 0 고치기 전 기준(이 컨테이너에서 다시 잼 — 아래 0번)
- [~] 1 표 맞춤(읽기/쓰기 나눔 · 보이는 표 먼저 · 기억) — **코드는 들어감(WIP 커밋 3d8ea709 = 메인이 함) · 검사 전**(11-13 컨테이너가 다시 시작돼 여기서 이어 감)
- [ ] 2 그리기 뒤 일(learnSpy 관찰자·navRender 읽기 → 자리 복원 다음 프레임)
- [ ] 3 팩 이어 받기(plEnd — 1.5초 입력 없음 + 화면 보임)
- [ ] 4 2단계 스위치 `cvh`(기본 끔)

## 항목별 기록

### 0 고치기 전 기준(11-12 · 이 컨테이너 · BUILD 007d154b · 하나씩 돌림)
수치 `q_pos.py --perf`(fixture 1280×900 · 한 번 잰 값 ±15%):

| 문서 | 처음 열기 ms | Layout 수 | Recalc 수 | Layout ms | Script ms | Task ms | 다시 열기 ms | Layout 수 | Task ms |
|---|---|---|---|---|---|---|---|---|---|
| 과목 비교표 PHARM/_tbl | 830 | 72 | 73 | 387 | 169 | 824 | 628 | 71 | 772 |
| 정리표 PHARM/HM | 665 | 14 | 17 | 254 | 255 | 640 | 229 | 10 | 208 |
| 학습 PHARM/HM | 553 | 14 | 15 | 289 | 140 | 611 | 356 | 14 | 351 |
| 과목 JB PHARM/_jb | 490 | 10 | 13 | 153 | 191 | 490 | 348 | 9 | 339 |
| 예상 PHARM/HM | 192 | 9 | 8 | 74 | 37 | 194 | 91 | 8 | 64 |

(DONE_W0 6번 표 — 같은 코드 · 다른 때: 733/507 · 505/153 · 420/241 · 402/349 · 153/72)

어디서 쓰는지(CDP 추적 — 강제 배치·스타일 계산마다 부른 함수):
- 과목 비교표: 첫 배치(자동 표 배치) 279ms 한 번 + **tblFit 안에서 표마다 스타일 계산 2.2ms + 배치 1.2ms × 63 = 215ms** + twStats 등 스크립트 · 다시 열어도 같은 길(기억 없음).
- 정리표: 첫 배치 165ms(stCard가 냄) + colFit 후보 높이 재기 4번 37ms · 다시 열면 colFit은 캐시(CF.cache는 원래 mount를 넘어 남음)라 196ms.
- 학습: 첫 배치 294ms 한 번(lmCount가 냄 — 누가 내든 한 번은 내야 함) · 나머지 강제 배치는 다 합쳐 40ms 안쪽 → 2번(그리기 뒤 일)은 얻을 것이 작음.

지킴이·회귀(고치기 전): q_pos PASS(105경우 · 347초) · ux_nav PASS · ux_kitfrev PASS · ux_marks PASS · **ux2_jbq FAIL 14(STATUS retired — 원래 실패)** · ux_align PASS · ux_fbar PASS · ux_v3phone PASS · ux2_load PASS · **ux2_tables FAIL(STATUS local — 맥 글꼴)** · **ux3_tables FAIL 1(STATUS local — `1280 펼침 IMPL/OSS table 높이 5623 ≤ 기본 5456`)** · q_crawl PASS(948화면) · q_perf PASS.
