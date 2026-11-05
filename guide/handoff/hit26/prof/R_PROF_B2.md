# R_PROF_B2 — 교수 프로필 4명(백정화 · 이윤실 · 김우진 · 우경미) 보고 (11-05)

- 지시: work/_tmp/agents/PROF_B2.md · AGENTS 'PROF' 절 · guide/prof/README.md(절 제목·순서 그대로) · CLAUDE.md 절대 규칙.
- 교수 찾기 `grep -n '<이름>' tools/*/subject.py` → 넷 모두 **tools/pharm/subject.py에만** 있음(PROF_LEC·YEAR_PROF·MENT_PROF·PROF_NOTE). tools/pharm4/subject.py는 빈 틀(PROF_LEC {}) — 4Q 담당 근거 없음.
- 입력: work/3q26/ref_PHARM.md(JB 카드 205 · data-yp) · tools/pharm/annot.txt(lec= 쪽 · rel=) · tools/pharm/subject.py(YEAR_PROF·YEAR_PROF_Q·PROF_LEC·MENT_PROF·MENT_ALL·PROF_NOTE — TREND_NOTE 없음) · work/_tmp/fmt26/PHARM.md(형식) · guide/handoff/hit26/HIT_PHARM.md·R_PHARM.md + tools/pharm/r26.txt(26 3Q 55문항) · guide/handoff/trend26/TREND_PHARM.md·yearprof_R_PHARM.md·PHARM_R_JB26.md · tools/pharm/lec_*.txt(`!`·`@UPD` 수업 신호) · tools/pharm/jb_crops.json(그림 문항).
- 쓴 것: guide/prof/백정화.md · 이윤실.md · 김우진.md · 우경미.md(NFC) + 이 보고. 그 밖 파일 수정·빌드·커밋·git stash 없음. 계산 스크립트는 scratchpad.
- 공통 검사(교수마다 아래에 수):
  - 연도·교수: ref 카드 205의 (문항, 해) 쌍마다 data-yp ↔ subject.py YEAR_PROF_Q → YEAR_PROF 대조 — 전체 일치 292 · 어긋남 0 · YEAR_PROF에 없는 해(화면 q['prof'] 대체) 60.
  - 형식: fmt_audit 1절(교수 × 연도) 합계 = 이 프로필 2절 강의별 합(3Q·tier A) — 넷 모두 해마다 같음. ANX(4Q)·약물상호작용은 fmt_audit 2절 문항별 형식으로 셈(1절은 C 등급 빼서).
  - ref 꼴 코드 ↔ fmt_audit 다른 문항 2: HM03(ref es · fmt_audit 넘버링) · HM06(ref tf · fmt_audit 빈칸) → 프로필은 fmt_audit 따름.
  - 26 3Q 실제: r26 머리줄(prof·fmt·st·jb) 교수·강의별 수 = HIT 1절 표 줄 수.

## 백정화 — guide/prof/백정화.md
- 과목: PHARM만(RX 19·21~25 · XE 22 · 약물상호작용 22 AX37). 26 3Q 실제 7.
- 연도·교수 대조: (문항, 해) 39쌍 = YEAR_PROF 일치 37 · 어긋남 0 · 근거 없는 해 2(RX36 18·15). 카드 30.
- 형식 대조: fmt_audit 1절 백정화 25·24·23·22·21·19·18·15 합 = 2절 강의별 합(22 = RX 객3·단2 + XE 객2·단3 = 객5·단5 ✓). AX37은 2절(빈칸).
- 26 3Q 실제 대조: r26 백정화 7(객 6·서 1 · 짤 3·변형 4·탈 0) = HIT 1절 표 7줄 · 2절 합계 · 상만 5/7 = HIT 표(Z01~05 상 · Z24·Z33 중) ✓.
- 불확실 칸: 2절 22 약물상호작용(1문항) · 18·15(근거 없는 해) · §5 25 강조 → 26 3/3(3곳) · §8 '4Q 새 강의 첫해'(22 한 해) · RX 19·21 쿼터.
- 지난 자료와 다른 점: TREND 7-1은 25를 객 5·단 1·서 1(RX38 객관식)로 셈 — 프로필은 fmt_audit(RX38 단답) 따름.

## 이윤실 — guide/prof/이윤실.md
- 과목: PHARM만(XE 20·21·23·24·25 · RX 20 · 항불안제 20·21·23~25(4Q) · 약물상호작용 21 AX36). 26 3Q 실제 8(XE).
- 연도·교수 대조: (문항, 해) 89쌍 = YEAR_PROF·YEAR_PROF_Q 일치 82 · 어긋남 0 · 근거 없는 해 7(XE06 16 · RX16 16·15 · RX24 17·16 · AX11 18 · AX12 17). 카드 61.
- 형식 대조: fmt_audit 1절 이윤실 25·24·23·21·20·17·16·15 = 2절 XE·RX 합(20 = RX 19 + XE 6 = 객1·TF12·빈7·단3·넘1·서1 ✓). 항불안제·약물상호작용(C 등급)은 fmt_audit 2절 문항별로 셈(23~25 항불안제 객 11·단 4·빈 1·서 1).
- 26 3Q 실제 대조: r26 이윤실 8(객 4·단 4 · 짤 3·변형 5·탈 0) = HIT 1절 표 8줄 · 상만 8/8 = HIT 2절.
- 불확실 칸: 2절 약물상호작용 21(1) · 그림(XE15 1) · 18·17·16·15(근거 없는 해) · §5 25 강조 2/3(3곳) · p.31 '나오지 않는 곳' · §8 다른 교수 축(근거 2) · 4Q 항불안제 쪽(김우진 26 PPT 쪽으로만 매겨짐).
- 지난 자료와 다른 점: TREND 6-1의 '넘버링 1·보기 고르는 주관식 2'(항불안제) ↔ fmt_audit은 AX03 단답·AX06 단답·AX07 객관식 — 프로필 2절은 fmt_audit 따름(보기 고르기는 글로만 적음).

## 김우진 — guide/prof/김우진.md
- 과목: PHARM만(BT 21~25 · 26 3Q 실제 BT·ACU·CHR·ANX 34). 4Q 근거 없음(tools/pharm4 빈 틀).
- 연도·교수 대조: (문항, 해) 45쌍 = YEAR_PROF 일치 35 · 어긋남 0 · 근거 없는 해 10(BT01·05·06·14·15·16·17·18·19 20 · BT19 19). 카드 16(그중 근거 없는 해뿐인 카드 2 — BT18·BT19).
- 형식 대조: fmt_audit 1절 김우진 25(객 9)·24(5)·23(7)·22(6)·21(객 7·TF 1)·20(객 7·TF 2)·19(TF 1) = 2절 ✓.
- 26 3Q 실제 대조: r26 김우진 34(BT 8 · ACU 11 · CHR 7 · ANX 8 · 객 19·단 15 · 짤 1·변형 16·탈 17) = HIT 1절 표 34줄 · 적중 30 = 짤 축 17 + 탈 자리 13 · 놓침 3 · 불가 1 · 상만 13/34 = HIT 2절 ✓.
- HIT 4절 '프로필 몫' 문구와 다른 수(r26·HIT 1절 표로 다시 셈): BT 짤·변형 '6/8' → 5/8 · 새 강의 탈 '15/26' → 14/26 · 탈 출처 합 16 → 17(Z37 같은 쪽 다른 칸 빠짐) · Z22(ANX p.11)·Z55(ANX p.15)는 annot lec= 기준 4Q 기출 카드(AX37 · AX11·AX19)가 있는 쪽이라 '같은 쪽 다른 칸'으로 셈(HIT는 '미출제 쪽') · 수업 신호 HIT '3/5'(BT·ACU·CHR) → 이 파일 ANX 포함 9/12.
- 불확실 칸: 2절 20·19(근거 없는 해) · §4 '26 바뀐 쪽·새 상자' 4 · §5 ANX p.40 ② ↔ Z23 · 26 단답의 문장 빈칸 꼴(복원 글 판정) · 25 BT '중복복원' 8번.

## 우경미 — guide/prof/우경미.md
- 과목: PHARM만(ACU·CHR 21~25 · HM 21~25 · 26 3Q 실제 HM 6 · 22 국소마취제 첫 강의 — JB 문항 없음). 4Q 근거 없음.
- 연도·교수 대조: (문항, 해) 115쌍 = YEAR_PROF 일치 76 · 어긋남 0 · 근거 없는 해 39(ACU·CHR 20 · HM 20·19·18·17·16). 카드 53(YEAR_PROF 확정 해 있는 카드 38 · 근거 없는 해뿐 15 — PN16~26 · HM19~24).
- 형식 대조: fmt_audit 1절 우경미 25(13)·24(12)·23(10)·22(17)·21(24)·20(32)·19~16 = 2절 ACU+CHR+HM 합 ✓(25 객4·빈5·단1·넘1·서2 등 해마다 같음).
- 26 3Q 실제 대조: r26 우경미 6(HM · 객 3·서 3 · 짤 1·변형 4·탈 1) = HIT 1절 표 6줄 · 적중 5/6 · 상만 4/6 = HIT 2절 ✓.
- 불확실 칸: 2절 25·24 ACU(2문항) · 20·19~16(근거 없는 해 — HM 20은 조영단일 수도: 23판 '21년' 멘트) · 국소마취제(문항 없음) · §5 강조 ↔ 출제 주제 판정 · PN05~07 논문(슬라이드 밖).
- 지난 자료와 다른 점: ref 꼴 HM03 es · HM06 tf ↔ fmt_audit 넘버링·빈칸(프로필은 fmt_audit) · TREND 9-1 'HM 22 탈 1(HM03)'은 지금 카드(HM11 합침 — assemble MERGE)로는 HM03 20 출제가 있어 짤(카드 기준 22 탈 = HM02뿐).

## 마무리 검사
- 쓴 파일: guide/prof/백정화.md · 이윤실.md · 김우진.md · 우경미.md — 파일 이름 NFC(아래 확인) · README 형식 절 9개 제목·순서 그대로.
- 연도·교수 대조 합: 백정화 37+2 · 이윤실 82+7 · 김우진 35+10 · 우경미 76+39 = 확정 230 · 근거 없는 해 58 · 어긋남 0(ref 전체 292·60 중 넷 몫).
- 26 3Q 실제 합: 7 + 8 + 34 + 6 = 55 = r26 문항 수 = HIT 1절 표 줄 수.
