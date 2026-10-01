export const meta = {
  name: 'jbl-ux3-impl',
  description: '허브 3차 구현 — 세 트랙 동시(1: 메뉴·레이아웃 G→표 열 폭 L / 2: 측정·세션 I→공부 달력 J / 3: M·빈칸 색 K→🔑 줄바꿈 N) → 병합 → 오늘 대시보드 H → 통합 P → 검증 3 → 수정',
  phases: [
    { title: 'Tracks', detail: 'G→L ∥ I→J ∥ K→N' },
    { title: 'Merge', detail: 'ux3t·ux3k → main' },
    { title: 'Home', detail: '묶음 H 오늘 대시보드' },
    { title: 'Integrate', detail: '묶음 P 도움말·SPEC·새 기능 안내·호환' },
    { title: 'Verify', detail: '기능·데이터 / 화면 / 공부 흐름' },
    { title: 'Fix', detail: '검증 결과 수정' },
  ],
}
const DONE = {
  type: 'object',
  properties: {
    implemented: { type: 'array', items: { type: 'string' } }, skipped: { type: 'array', items: { type: 'string' } },
    tests: { type: 'string' }, commit: { type: 'string' }, notes: { type: 'array', items: { type: 'string' } },
  },
  required: ['implemented', 'tests'],
}
const ISSUES = {
  type: 'object',
  properties: { issues: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] }, problem: { type: 'string' }, evidence: { type: 'string' }, proposal: { type: 'string' },
  }, required: ['id', 'severity', 'problem', 'proposal'] } } },
  required: ['issues'],
}
const MAIN = '/Users/jumisong/JBL', WT = '/Users/jumisong/JBL-ux3t', WK = '/Users/jumisong/JBL-ux3k'
const REQ = `사용자 요청(원문): "materials 폴더에 올린 공부시간 측정 hub html 참고해서 달력 및 공부시간 수정/추가/측정할 수 있게끔 해줘. 그리고 기본 페이지에 왼쪽 탭을 만들고, 너가 생각하는 가장 최적의 효과적 효율적 구성으로 공부달력탭 포함해서 jbl 메인 화면 및 왼쪽 메뉴탭 구성을 해줘. 지금의 각 과목탭 나열되어있는 구조를 전면 개선해줘. 그리고 빈칸빵 기능도 하이라이트처럼 색상 선택할 수 있게끔 해주면 좋겠어. 그리고 각 정리본 들어가서는 왼쪽의 메뉴탭을 m 누르면 토글되게끔, 안 보이게끔 하는 기능 추가해주고, 그러면 각 강의자료 정리본의 정리표 간격도 커지겠지? 지금 너무 열간 간격이 너무 좁아서 어쩔 수 없지만 특정 열에 많은 내용이 들어가면서 한 행이 너무 길어지는 등의 현상이 있거든. 메뉴탭 없어지면 표가 자동으로 커졌으면 좋겠고, 열 간격도 너가 가장 적절히 조절해서 가장 최적으로 효과적으로 표를 볼 수 있었으면 좋겠어. 이때 한줄요지 핵심에서 핵심 상자 내용 줄바꿈도 적절히 해주고! 지금 줄바꿈이 거의 안되어있어서 읽기 너무 어려워! 위 지시사항 및 그 외적으로도 개선점 및 오류 없는지, 너가 최적으로 판단해서 알아서 가장 최고의 내게 최적의 jbl 을 만들어주면 돼"`
const BASE = (root) => `JBL 허브 = 치의학대학원 3학년 3쿼터 시험 대비 학습 사이트(6과목 정리본·JB 기출, 곧 ESTH 추가). 사용자는 아이패드(세로 820·가로 1180, 애플펜슬·손가락, 하드웨어 키보드 — 한글 입력 상태일 수 있음)와 맥(1280)에서 GitHub Pages로 공부한다. 1차 배포본(7095e56) 사용자 데이터(형광펜·빈칸·채점·공부 시간·메모)가 있고 2차 개선(묶음 1~6·검증 수정)까지 main에 커밋돼 있다.
${REQ}
설계·계획: work/ux3_plan.json — decisions(결정 0~14)·wireframes·batches(묶음 G·H·I·J·K·L·N·P, 항목마다 what·acceptance·files)·data_compat. 반드시 decisions·data_compat·내 묶음 항목을 전부 읽고 그대로 구현(더 나은 방법이 확실하면 notes에 이유를 남기고 조정). 오케스트레이터 결정: 결정 14의 선택지 — (A) 허브 홈 과목 영역은 한눈표(1024↑)·카드(좁은 폭) 자동 전환만, [카드로 보기] 전환 버튼은 두지 않음 / (B) ■ 종료 뒤 자동 측정은 '새 문서를 열 때' 다시 켬 / (C) 날짜 경계 4시·직접 넣는 할 일은 이번에 안 함. 결정 13의 트랙 경계와 달리, 이번 실행의 트랙은 아래 역할에 적힌 대로다.
참고 HUB: materials/HUB.html(renderToday·openAddSession·buildTrackerWidget·fmRender) — 필요하면 playwright로 열어 본다.
파이썬 ${root}/.venv/bin/python, playwright 설치됨. 코드 원본은 ${root}/tools/cons/{shell.html, build4.py, lecparse.py, emph.py, reflow.py, trend.py} — 고친 뒤 .venv/bin/python tools/sync_common.py 로 6과목 폴더에 복사. 빌드·검증 한 번에: sh tools/build_all.sh (6과목 빌드 → verify → audit_design → tests/ux_all.py — 약 40분). 개발 중에는 6과목 빌드(sync_common.py --build 대신 각 build4.py) 뒤 관련 테스트만 돌리고, 묶음 끝에 build_all로 전체 확인. 한 과목만 다시 빌드하면 허브·팩 판이 어긋나 stale 모드 — 테스트 전 6과목 모두 빌드. 허브 동작 문서: tools/SPEC.md(v1~). 원칙: guide/정리본_원칙.md 7-1(색 절제·대비·줄간격), CLAUDE.md.
지킬 것: ① localStorage 키·형식 하위 호환(새 키 추가·이관만, 삭제·덮어쓰기·형식 변경 금지 — 이관 전 autoBak/migBak). ② 원고(tools/<sid>/lec_*.txt·annot.txt·tables.txt·pred.txt)는 고치지 않는다. ③ 렌더를 바꿔도 카드 textContent 보존(새 구분은 DOM에 남기고 CSS로 숨김) — 표시 위치 잃음 증가 0(tools/tests/legacy_restore.py, --rev 7095e56 포함 통과 유지). ④ CLAUDE.md '페이지 구성'의 과목 홈·강의 탭·JB 문제 내부 구성은 유지. ⑤ 항목마다 수용 기준을 playwright로 직접 확인하고 스크린샷(${root}/work/_tmp/ux3i_*.png)을 Read로 본다(맥 1280x900 + 아이패드 세로 820x1180 + 가로 1180x820, 터치는 has_touch). ⑥ 새 동작마다 tools/tests/에 회귀 테스트 추가·갱신(ux_all이 tests/*.py 자동 실행). ⑦ tools/SPEC.md와 도움말(? 표)에 새 동작을 적는다(내 묶음 이름의 새 소절로 — 병합 충돌 줄이기). ⑧ 항목 단위로 git add tools && git commit(메시지 한국어, 항목 id로 시작, 끝에 "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"). docs/는 커밋하지 말 것. push 금지. ⑨ 기계가 CPU 8·메모리 8GB이고 세 구현자가 동시에 브라우저 테스트를 돌린다 — 브라우저는 쓰고 바로 닫고, 시간 초과로 보이는 실패는 한 번 더 돌려 확인, 기다림은 조건 대기로.`
const TRACK = {
  1: { root: MAIN, name: '트랙 1(본 저장소 main)', batches: ['묶음 G', '묶음 L'],
    scope: `G0(하던 작업 마무리·피드백 기록)는 오케스트레이터가 끝냄 — 2차 수정까지 0918775로 커밋·배포, 피드백 기록 완료. 맡는 것: 묶음 G(전역 왼쪽 메뉴·#app 레이아웃·navRender·sideToggle·서랍·revInfo 캐시)와 묶음 L(표 자동 확장·colFit 열 폭·아이패드 세로 2단 카드·칸 공통 CSS). 새 CSS는 shell.html <style> 끝의 새 블록 '/* ux3 트랙1 — G·L */'에, 새 JS는 '// ux3 트랙1' 구역에. 동시 작업: 트랙 2(${WT}, 브랜치 ux3t)가 측정·세션·달력(묶음 I·J: T·tFlush·tBtn·tDay·tLec·tGoal·tPopHTML·timeView·parseHash의 _time/_cal·mergeData 시간 분기)을, 트랙 3(${WK}, 브랜치 ux3k)이 M 키·빈칸 색(묶음 K: keydown의 M·Shift+M·Shift+B 줄·Kit 빈칸·빈칸 CSS)과 🔑 줄바꿈(묶음 N: lecparse key_lines·build4 mkey_html·🔑 CSS)을 고친다 — 그 영역은 건드리지 말 것. 메뉴 머리 ⓪의 트래커는 트랙 2가 만들 함수 trkUI(where)를 쓴다: (typeof trkUI==='function' ? trkUI('nav') : 지금 #tmr 상태를 보여 주는 간단한 대체)로 호출해 두면 병합 뒤 자동으로 새 트래커가 나온다. M 키 바인딩은 트랙 3 몫 — 트랙 1은 지금 \\\\ 키가 부르는 사이드바 토글 함수 이름을 sideToggle()로 유지·정리해 두면 트랙 3이 M을 거기에 연결한다. 표가 폭 변화를 알 수 있게 레이아웃 전환이 끝나면 window에 CustomEvent 'jbl:layout'을 보낸다. 허브 홈(home()) 개편은 병합 뒤 묶음 H에서 하니 여기서는 home()을 새 #app 격자 안에 들어가게만.` },
  2: { root: WT, name: '트랙 2(worktree ux3t)', batches: ['묶음 I', '묶음 J'],
    scope: `작업 위치: git worktree ${WT}(브랜치 ux3t) — 모든 셸 명령은 'cd ${WT} && …'로, 파일 읽기·수정은 ${WT}/… 절대 경로로만. ${MAIN}(main)과 ${WK}는 다른 구현자가 동시에 작업 중이니 절대 고치지 말 것(git 명령도 ${WT}에서만). work/의 하위 폴더는 공유(심볼릭 링크) — 거기에 쓰지 말고 스크린샷·임시 파일은 ${WT}/work/_tmp/에. 맡는 것: 묶음 I(측정 상태 기계 tstate·세션 벽시계·안전장치·자정 분할·trest·tseg·tedit 편집 원장·날짜별 목표·백업 합치기·트래커 UI 공통 조각 trkUI(where) — where = 'nav'(메뉴 머리 한 줄)·'top'(상단 #tmr)·'pop'(시계 팝업)·'band'(홈 오늘 띠)·'card'(달력 상태 카드)로 HTML을 돌려주고 버튼 위임은 전역 한 곳)와 묶음 J(📅 공부 달력 #/_cal·#/_time 통계 별칭·월 달력·선택한 날 패널·+ 시간 추가·✎ 수정·🗑 삭제·⏱ 크게 #bigclock). 새 CSS는 '/* ux3 트랙2 — I·J */' 블록에, 새 JS는 '// ux3 트랙2' 구역에. 메뉴·레이아웃(트랙 1)·M 키·빈칸·🔑(트랙 3)·home() 본문(병합 뒤 묶음 H)은 건드리지 말 것 — 달력으로 가는 링크는 지금 있는 📊 공부 기록 링크·시계 팝업을 #/_cal로 바꾸는 정도만.` },
  3: { root: WK, name: '트랙 3(worktree ux3k)', batches: ['묶음 K', '묶음 N'],
    scope: `작업 위치: git worktree ${WK}(브랜치 ux3k) — 모든 셸 명령은 'cd ${WK} && …'로, 파일 읽기·수정은 ${WK}/… 절대 경로로만. ${MAIN}(main)과 ${WT}는 다른 구현자가 동시에 작업 중이니 절대 고치지 말 것(git 명령도 ${WK}에서만). work/의 하위 폴더는 공유 — 거기에 쓰지 말고 스크린샷·임시 파일은 ${WK}/work/_tmp/에. 맡는 것: 묶음 K(M = 메뉴 숨기기 — 지금 \\\\ 키가 부르는 사이드바 토글 함수를 그대로 부름(트랙 1이 이름을 sideToggle로 정리 중 — 둘 다 동작하게 지금 함수 이름을 확인해 호출), Shift+M = 메모, 처음 한 번 알림 keyNoticeM, 빈칸 5색 BCOL·저장 c 필드·도구 막대 견본·Shift+B·라벨 blabel·색 기억 bcol·hcol·자동 빈칸 창·내 표시 모아보기 빈칸 색)와 묶음 N(lecparse.key_lines 🔑 규칙 K1~K7·ksep 글자 불변·정리표 🔑 칸·한 줄 요지 .ksub·🔑 CSS·check_lec 글자 동일 검사 — 원고는 고치지 않음). 새 CSS는 '/* ux3 트랙3 — K·N */' 블록에, 새 JS는 '// ux3 트랙3' 구역에. 메뉴·레이아웃·표 열 폭(트랙 1)·측정·달력(트랙 2)·home()은 건드리지 말 것.` },
}
phase('Tracks')
const runTrack = async (t) => {
  const T = TRACK[t], out = []
  for (const b of T.batches) {
    const r = await agent(`${BASE(T.root)}

## 역할: 구현자 — ${T.name}, work/ux3_plan.json의 '${b} …'(batches 중 name이 '${b}'로 시작하는 것) 전 항목
${T.scope}
먼저 cd ${T.root} && git log --oneline -8 · git status로 상태를 보고(중간에 끊긴 작업이 있으면 이어서 완성) 그 위에서 작업한다.
앞 묶음 보고: ${JSON.stringify(out).slice(0, 5000)}
끝나면 sh tools/build_all.sh 가 RESULT PASS인지 확인(실패하면 고치고 다시). 결과(JSON): 구현한 항목, 건너뛴 항목과 이유, 테스트 결과, 마지막 커밋, 병합자·다음 묶음·검증자에게 넘길 메모(바꾼 함수·새 LS 키·새 CSS 블록 위치·다른 트랙과 맞물리는 계약).`, { label: `ux3:${b}`, phase: 'Tracks', schema: DONE, effort: 'high' })
    out.push({ batch: b, ...(r || { implemented: [], tests: 'agent failed' }) })
  }
  return out
}
const [t1, t2, t3] = await Promise.all([runTrack(1), runTrack(2), runTrack(3)])
phase('Merge')
const merge = await agent(`작업 위치: 본 저장소 ${MAIN} (main). ${BASE(MAIN)}
## 역할: 병합자 — 브랜치 ux3t(worktree ${WT}, 트랙 2: 묶음 I·J)와 ux3k(worktree ${WK}, 트랙 3: 묶음 K·N)를 main(트랙 1: 묶음 G·L)에 병합
1) 세 작업 트리 모두 docs/ 외 미커밋 변경이 없는지 확인(있으면 그 트랙 보고를 보고 알맞게 그 작업 트리에서 커밋).
2) cd ${MAIN} && git merge --no-ff ux3t -m "병합: 트랙 2(묶음 I 측정·세션·J 공부 달력)" → 충돌 해결 → git merge --no-ff ux3k -m "병합: 트랙 3(묶음 K M 키·빈칸 색·N 🔑 줄바꿈)" → 충돌 해결. 두 쪽 기능을 모두 살린다. tools/cons/shell.html·tools/SPEC.md·build4.py·lecparse.py를 먼저 해결하고 다른 과목 사본은 sync_common.py로 맞춘다. keydown·도움말 표·SPEC은 모든 키·설명을 넣고 겹치면 보고. 테스트 파일은 모두 유지. 계약 확인: 메뉴 머리 ⓪·상단이 트랙 2의 trkUI(where)를 실제로 쓰는지, M 키가 트랙 1의 sideToggle을 부르는지, 표가 'jbl:layout' 이벤트로 다시 맞춰지는지, 백업·복원(dumpAll·mergeData·MSKIP)에 세 트랙의 새 LS 키가 다 들어가는지 — 빠진 것은 고친다.
3) 병합 뒤 sh tools/build_all.sh 가 RESULT PASS가 될 때까지 고친다.
트랙 1 보고: ${JSON.stringify(t1).slice(0, 8000)}
트랙 2 보고: ${JSON.stringify(t2).slice(0, 8000)}
트랙 3 보고: ${JSON.stringify(t3).slice(0, 8000)}
결과(JSON): 해결한 충돌(파일·내용), 병합 후 고친 것, 테스트 결과, 병합 커밋.`, { label: 'ux3:merge', phase: 'Merge', schema: DONE, effort: 'high' })
phase('Home')
const home = await agent(`작업 위치: 본 저장소 ${MAIN} (main). ${BASE(MAIN)}

## 역할: 구현자 — work/ux3_plan.json의 '묶음 H …'(허브 홈 '오늘' 대시보드) 전 항목
세 트랙이 병합돼 있다(전역 메뉴 #app·navRender, 측정 trkUI·tDay·tGoal·달력 #/_cal, M·빈칸 색·🔑 줄바꿈, 표 colFit). 그 위에서 home()을 오늘 대시보드로 다시 쓴다. todayTasks()는 홈·메뉴 배지·시계 팝업이 함께 쓰게.
먼저 git log --oneline -15 · git status. 앞 보고: ${JSON.stringify({ t1, t2, t3, merge }).slice(0, 14000)}
끝나면 sh tools/build_all.sh RESULT PASS. 결과(JSON): 구현한 항목, 건너뛴 항목과 이유, 테스트 결과, 마지막 커밋, 메모.`, { label: 'ux3:묶음 H', phase: 'Home', schema: DONE, effort: 'high' })
phase('Integrate')
const integ = await agent(`작업 위치: 본 저장소 ${MAIN} (main). ${BASE(MAIN)}

## 역할: 통합자 — work/ux3_plan.json의 '묶음 P …' 중 P2(도움말·SPEC·새 기능 안내 whatsNew)·P3(6과목 재빌드·내용 검증: tools/check_lec.py 6과목 ✗ 0, check_years·check_eyears·check_abbr 새로 걸린 것 0)·P4(playwright 전체 회귀·세 뷰포트 화면 확인)·P5(1차 사용자 데이터 호환: 7095e56 허브에서 쌓은 데이터 → 새 허브에서 공부 시간 합계·형광펜·빈칸·채점·시험일·설정 그대로, legacy_restore --rev 7095e56 통과). P1(트랙 합치기)은 이미 끝남, P6의 push는 하지 말 것(오케스트레이터가 배포). 도움말(?)의 단축키 표는 모든 화면 키를 한 표로(M 메뉴·Shift+M 메모·Shift+B 빈칸 색 포함), '새 기능 안내'(whatsNew)는 1차 사용자에게 한 번 — 3차 핵심(왼쪽 메뉴·오늘 화면·공부 달력·세션 측정·M·빈칸 색·표 폭·🔑 줄바꿈)을 5~7줄로.
앞 보고: ${JSON.stringify({ merge, home }).slice(0, 10000)}
끝나면 sh tools/build_all.sh RESULT PASS. 결과(JSON): 한 것, 못 한 것과 이유, 테스트 결과, 마지막 커밋, 메모.`, { label: 'ux3:묶음 P', phase: 'Integrate', schema: DONE, effort: 'high' })
const impl = [...t1, ...t2, ...t3, { batch: 'merge', ...(merge || {}) }, { batch: '묶음 H', ...(home || {}) }, { batch: '묶음 P', ...(integ || {}) }]
phase('Verify')
const V = [
  ['func', `기능·데이터: 새 메뉴(모든 화면·아코디언·이어서·배지·서랍)·M/Shift+M/\\\\·Shift+B·빈칸 5색(저장·복원·되돌리기·다른 창 동기화·옛 회색 빈칸 그대로)·측정(자동·세션 ▶/☕/■·무활동 되묻기·창 닫았다 열기·자정 분할·창 두 개)·달력(추가·수정·삭제·되돌리기·날짜별 목표·통계 탭·#/_time 옛 링크)·tedit·tseg 백업 합치기(같은 백업 두 번 합쳐도 합계 불변·빼기 보존)·표 colFit(메뉴 숨김·표시 시 다시 맞춤·필터 뒤 흔들림 없음)·🔑 줄바꿈 뒤 형광펜·빈칸 위치 그대로. 1차 배포본(7095e56)·2차(수정 전 커밋 228ae8d 무렵) 데이터를 쌓은 프로필로 새 허브를 열어 합계·표시·채점·시험일이 그대로인지. 콘솔 오류 0.`],
  ['visual', `화면: 세 뷰포트 × (허브 홈 오늘 대시보드·왼쪽 메뉴(펼침/접힘/서랍)·공부 달력(달력·날짜 패널·추가/수정 창·크게 보기)·통계·과목 홈·학습 탭 🔑 상자와 한 줄 요지·정리표(메뉴 보임/숨김 폭 비교, 요약/전체, 전체정리표)·비교표·한눈표·JB·빈칸 5색) 스크린샷(work/_tmp/ux3v_*.png)을 Read로 직접 본다. 🔑·요지 줄바꿈이 읽기 쉬운지(너무 잘게 쪼개지거나 여전히 한 덩어리인 곳), 표 열 폭이 행 높이를 줄였는지(메뉴 숨김 전후 행 높이 비교 수치), 메뉴·홈이 헷갈리지 않는지, 원칙 7-1(색 절제·명암·겹침·가로 넘침).`],
  ['flow', `공부 흐름(아이패드 세로·가로, 손가락·펜슬): ① 1차·2차 사용자가 업데이트 후 처음 열 때(새 기능 안내·M 알림·이관 토스트가 과하거나 겹치지 않는지), ② 아침에 허브 열기 → 오늘 할 일 → ▶ 공부 시작 → 강의 학습(메뉴 M으로 숨기고 정리표 보기) → ☕ 쉬기 → 다시 → JB 한 장씩 → ■ 종료 → 달력에서 오늘 기록 확인·잘못 잰 시간 ✎ 고치기·빠진 시간 + 추가, ③ 과목 7개 사이 이동이 메뉴에서 몇 번 누름인지, ④ 뒤로가기·새로고침·탭 전환 뒤 메뉴 펼침·보기 상태 유지, ⑤ 터치 목표 44px·도움말이 새 기능을 다 설명하는지.`],
]
const ver = await parallel(V.map(([k, body]) => () => agent(`작업 위치: 본 저장소 ${MAIN} (main). ${BASE(MAIN)}

## 역할: 검증자(${k}) — 방금 구현된 3차 개선을 회의적으로 검증. 파일(tools/·docs/)은 고치지 말 것(스크린샷·임시 파일은 work/_tmp/에만). 문제마다 재현 절차·스크린샷 경로·코드 위치·구체적 수정안. 공부 방해·오류·데이터 위험 우선, 이슈는 중요한 것부터 최대 25개.
구현 보고: ${JSON.stringify(impl).slice(0, 16000)}
${body}`, { label: `ux3v:${k}`, phase: 'Verify', schema: ISSUES, effort: 'high' })))
phase('Fix')
const vi = ver.filter(Boolean).flatMap((v, i) => (v.issues || []).map(x => ({ lens: V[i][0], ...x })))
log(`검증 이슈 ${vi.length}건 (high ${vi.filter(x => x.severity === 'high').length})`)
let fix = null
if (vi.length) fix = await agent(`작업 위치: 본 저장소 ${MAIN} (main). ${BASE(MAIN)}

## 역할: 검증에서 나온 문제 수정
이슈(JSON): ${JSON.stringify(vi).slice(0, 60000)}
high·medium은 모두, low는 가능하면(중복은 합쳐서). 고칠 때마다 playwright로 확인(스크린샷 work/_tmp/ux3f_*.png를 Read로)·회귀 테스트 추가·SPEC·도움말 갱신·고친 단위로 커밋. 끝에 sh tools/build_all.sh RESULT PASS까지, 그리고 세 뷰포트에서 허브 홈·메뉴·달력·학습·정리표·JB를 한 번씩 찍어 눈으로 최종 확인. 결과(JSON): 고친 것(이슈 id별 한 줄), 못 고친 것과 이유, 테스트 결과, 마지막 커밋, 사용자 확인이 필요한 것(notes).`, { label: 'ux3:fix', phase: 'Fix', schema: DONE, effort: 'high' })
return { impl, issues: vi, fix }
