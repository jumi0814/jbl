# 4Q 남은 일 인계(11-27 — 사용자 "울트라코드가 아니라 엑스트라로 … 워크플로우 이어나갈 수 있게끔 … 인계")

이 폴더만 보면 다음 담당(같은 세션이든 새 세션이든)이 그대로 이어 갈 수 있게 정리함. 규칙·절차의 원본은 `.claude/skills/jbl-update/`(SKILL·RULES 14·AGENTS·QA) · 진행 기록 `guide/handoff/UPD_4Q_진행.md`.

## 1. 지금 상태(11-27 14:20 UTC)
| 과목 | 끝난 정리본(검토·QA까지) | 배포 | 남은 정리본 |
|---|---|---|---|
| OMS2 | AES(26) · CMP·FG·RHN·LOAD(강의 없는 키) | 2차 | 25 임시본 6: OSA MMA POPA SOFT BONE TE |
| CONS4 | IRR(26) · SFA(26) | 2차 | 25 임시본 6: SFB EMS TEMS REP VPT IMP |
| IMPL4 | AUG(26) · PAST | 2차 | 25 임시본 6: COMP EDEN SOFT PERI PROG SURG |
| GERI4 | SYS(26) · PER(26) | 2차 | 25 임시본 5: BIO DEN PRO OMF OSC |
| PHARM4 | DS(26) · ANX·XE · **SED = 자리 표시**(안전 분류기가 자동 작성을 막음 — 다시 시도하지 않음 · 끝 보고 '사용자 확인') | 2차 | 25 임시본 5: LA DI HOR PGX GER |
| RAD | TRL(26) · FRAC | 2차 | 25 임시본 18(묶음 2개 — 차례로) |
| ESTH4 | CER RBR CAD DIG RPD PER SMI(25 임시본 · 검토 3회·QA·고침·마지막 merge 끝) · LAM | **미배포**(3차에) | 없음 |
| HINS | 11강의 + EXT·OHL — 작성·검토 3회·QA 끝 · **QA 고침 4강의(PRAC HOS AIDS HSYS)만 남음**(5시간 한도) | **미배포** | 없음(QA 고침·마지막 merge만) |
| OPATH | — | JB만 | 25 임시본 15 + 강의 없는 키 5 |
| ANAT4 | — | JB만 | HN(교과서 '교') · LL·UL·SPL('안내') · MH(강의 없는 키) |
- 마지막 커밋(작업 브랜치 ux4-cloud-72p9dr): 이 인계 커밋 · main 배포본 = 2차(f5bbdcca 계열 — `git log origin/main -1`).
- 11-27 메인이 고친 것(커밋 4e813bd4 — 아직 main 아님): 연도 없는 문항 칩('수업 예고'·'연도 미상') · 필기 라벨 ✍ 겹침 · 옛 답이 새 답 안이면 📜 이전 답 아님 · 잘린 '(' · 정답 요지 첫 조각 · 인용 꼬리 '(빨간 글씨).' · 📖 ⚡ = 문항과 겹치는 ⚡ · '참고 기출만 있는 교수' 줄 · JBFIX CONS4 L05·L08·L20 · OMS2 C03·C05 · 기출 대장 16자 자르기(4Q build2 10개) · 기출 참고 카드 P: → '-' · PHARM4 TREND_NOTE 조영단 해 · GERI4 NOIMG PER 3. 8과목 빌드·scan_render 통과(HINS·ESTH4는 run 안에서 다시 빌드됨).
- tesseract(kor) 설치됨(jbfig용 — 새 컨테이너면 `apt-get install -y tesseract-ocr tesseract-ocr-kor`).

## 2. 진행률(11-27 · 무게 = 26 강의 3 · 25 임시본 1.5 · 강의 없는 키·안내 0.3 · 교과서 HN 3)
| 단계 | 몫 | 끝남 |
|---|---|---|
| JB 분해·검수(10과목) | 15 | 100% |
| 교수 프로필·TREND | 10 | 100% |
| 정리본(109강의 · 무게 151) | 50 | 36%(무게 54 — 끝 37강의 + SED 자리 표시) |
| JB 그림 조각(JF 150문항) | 3 | 0%(초안 조각만 — 검수 전) |
| QA 메인 몫(렌더러·JBFIX) | 2 | 거의 끝(남은 것 §6) |
| 예상문제 다듬기·최종 N제(10과목) | 15 | 0%(강의별 예상 초안은 정리본 단계에서 씀) |
| 배포·전 검사·끝 보고 | 5 | 30%(1·2차 배포) |
| **합계** | 100 | **약 46% 끝 · 약 54% 남음** |

## 3. 다음 순서(그대로 — 한 과목에 run 둘 금지 · 같은 과목 split·merge·빌드가 겹치지 않게)
1. **HINS 남은 QA 고침**(같은 세션이면): Workflow `{scriptPath: "/root/.claude/projects/-home-user-jbl/a0af02c5-0dbc-52ee-b82b-13be879fb1dd/workflows/scripts/q4-notes-wf_9b907993-044.js", resumeFromRunId: "wf_2159598a-5cb", args: args/hins_resume.json 내용 그대로}`(그 파일이 없으면 글자가 같은 사본 guide/handoff/wf4q/q4-notes.js) → 앞 담당은 캐시, QAfix 4 + 마지막 merge만 돎.
   - 새 세션이면(resume 안 됨): Agent 4명(강의마다) — 지시 = `work/review_final2/QA_HINS.md`의 그 강의 항목 + 끝난 QAFIX_HINS_*.md 꼴 그대로(work/HINS/parts·tools/hins/lec_<KEY>.txt만) → 메인이 `merge_parts HINS` → `tools/hins/build4.py` → check_lec·check_25only·link_audit HINS. (work/가 없으면 QA 고침은 건너뛰고 끝 보고 '남은 QA'에 적음 — tools/hins는 이미 QA 전 merge 상태.)
2. **전 검사·3차 배포**: `sh tools/full_check.sh`(도는 정리본 run이 없으면 JBL_FC_SKIP 없이) → 기준값(진행 파일 '4Q 2차 배포' 줄)과 견줌 → `git fetch origin main && git merge-base --is-ancestor FETCH_HEAD HEAD && git push origin HEAD:main` → 1~2분 뒤 실제 주소 확인(scratchpad livesite 꼴 — HINS·ESTH4 강의 탭·JB·그림 · 콘솔 오류 0 · 404 0). 3차 = HINS 13 · ESTH4 8 + 11-27 렌더러 손질.
3. **나란히 셋**(한도 대기가 없으면 셋, 있으면 둘):
   - OPATH 정리본: Workflow `{scriptPath: guide/handoff/wf4q/q4-notes2.js, args: args/opath.json}`
   - ANAT4 정리본: 같은 스크립트 + `args/anat4.json`(HN '교' · LL·UL·SPL '안내' · MH 강의 없는 키)
   - JB 그림 조각: Workflow `{scriptPath: guide/handoff/wf4q/q4-jf.js, args: args/jf.json}` — **단 jf.json small 줄에서 OPATH 항목을 빼고 돌림**(OPATH 정리본 run과 빌드가 겹침 — OPATH JF는 OPATH 정리본 뒤에 small=[OPATH], rad=[]로 한 번 더).
4. **25 임시본**(JF가 그 과목을 끝낸 뒤 · 과목 하나 = run 하나 · 나란히 2~3): `q4-notes2.js` + `args/t25_<sid>.json` — oms2 · pharm4 · geri4 · impl4 · cons4 · rad1 → **rad2는 rad1이 끝난 뒤**(같은 과목).
   - 과목 하나가 끝날 때마다: 그 과목 build4 → full_check(도는 과목은 `JBL_FC_SKIP="<SID…>"` + 그 과목 팩을 마지막 배포 커밋 것으로 되돌려 둔 채) → 배포(SKILL '중간 배포') · 진행 파일에 한 줄.
5. **예상문제 다듬기·최종 N제**(정리본이 다 끝난 과목부터 · 과목 하나씩): AGENTS P(강의 묶음) → `pred_merge`·`pred_check`·`link_audit`(△ 최근 해 예상 연결 0 — OMS2 CMP C01·C02 · RAD FRAC F01·F02 · AES △5 t=미출제 판단 포함)·`fmt_audit` → PA(독립 감사) → FN(교수마다) → FNV(다른 담당) → final.txt · `subject.py FINAL_NOTE`('직전 2년 기출 먼저') → 빌드·배포. 스크립트는 그때 q4-notes 꼴로 새로(지시문 = AGENTS P·PA·FN·FNV 블록 + RULES 14 c ⑥ · 담당 schema {done, summary}).
6. **끝**: 전 과목 full_check · legacy_restore(--rev 1차 배포 전 기준 — 진행 파일) · 최종 배포 · 끝 보고(§5 사용자 확인 목록 한 번에).

## 4. 돌릴 때 지킬 것
- run이 사용 한도·컨테이너 재시작으로 멈추면 **같은 scriptPath·같은 args로 resumeFromRunId**(앞 담당은 캐시). 스크립트 파일을 고치면 고친 담당부터 다시 돎 — 도는 run의 스크립트는 고치지 않음(새 run은 새 파일).
- 길게 돌릴 땐 send_later로 확인 예약(한도면 풀리는 시각 + 5분) — 사용자 11-17 '절대 멈추지 말고'. 단 사용자가 '시작하라'고 할 때까지는 아무것도 띄우지 않음(11-27).
- 커밋은 메인만(담당 금지) · work/·materials/·jb/·reference/ 커밋 금지 · main은 ancestor 확인 푸시로만 · 3Q(docs/3q) 손대지 않음.
- 정리본 run 안에서 메인 통합 담당(Q4_MAIN_BRIEF)이 split·merge·빌드를 함 — 그 과목을 메인이 따로 빌드·merge하지 않음.
- 25 임시본은 26 자료가 오면 전면(RULES 14 5) — 이번 일과 별개.

## 5. 끝 보고 '사용자 확인'에 모을 것(지금까지)
- PHARM4 SED 진정수면제 — 자동 작성이 안전 분류기에 다섯 번 막혀 자리 표시(기출 탭 38문항은 공부 가능) · 원하면 사용자가 정리할 쪽 목록 제공.
- ANAT4 나눔(무인): HN = 교과서 정리본 · LL·UL·SPL = 범위 안내 · MH = 강의 없는 키.
- 개인 연락처 쪽(쪽 그림 보류): OMS2 MMA 78 · OPATH ODT 1 · GERI4 SYS 50 · GERI4 PER 3(필기 속 면허 번호 언급 — 11-27 추가) — 공개해도 되는지.
- GERI4 SYS ⚡ 4줄(전임 류인철 JB 답 목록) QA 고침에서 지움 — RULES 14a(⚡ = 26 자료만) · 글은 ⭐·annot에 그대로 · 되살릴지.
- JB 판정: RAD 배지 연도·M05/M06 · OPATH I04 합침·O01 20·D01/D02 · OMS2 O10 20·E01/E02 등급 · ANAT4 24판 이름·X22/B22·'탈' 칩 · CONS4 SFB · PHARM4 LA05 2021 · HINS M08(진행 파일·R_JB 보고에 근거).
- 배포 기준값(check_abbr·table_audit·check_breaks_jb) — 진행 파일 '4Q 2차 배포' 줄.

## 6. 남은 메인 몫(작은 것 — 배포 전 틈에)
- 스크린샷 다시(QA 보고마다 — OMS2·GERI4·IMPL4·CONS4·RAD·PHARM4 `work/<SID>/main/HANDOFF_after.md`) · IMPL4 H8(겹 점 숨김 — 선택) · OMS2 AES 예상 △5(t=미출제 + b=기출 — P 단계 몫).
- OMS2 RHN R01·E02 답 표 그림 조각 = jf.json OMS2 항목에 넣어 둠 · CONS4 L08·EMS M01 = jf.json CONS4.
