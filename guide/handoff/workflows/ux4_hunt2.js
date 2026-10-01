export const meta = {
  name: 'jbl-ux4-hunt2',
  description: '허브 4차 오류 전수 조사 2 — 6관점(3명씩) 조사 → 재현 검증 → 수정을 새 오류가 안 나올 때까지(최대 2회) → 최종 build_all',
  phases: [
    { title: 'Hunt', detail: '6관점 조사(라운드마다)' },
    { title: 'Confirm', detail: '오류마다 독립 재현' },
    { title: 'Fix', detail: '확인된 오류 수정' },
    { title: 'Checklist', detail: '사용자 지시사항 한 줄씩 대조' },
    { title: 'Final', detail: '남은 것 수정·build_all' },
  ],
}
const BUGS = {
  type: 'object',
  properties: { bugs: { type: 'array', items: { type: 'object', properties: {
    title: { type: 'string' }, screen: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] },
    repro: { type: 'string' }, expected: { type: 'string' }, actual: { type: 'string' }, evidence: { type: 'string' }, cause: { type: 'string' }, fix: { type: 'string' },
  }, required: ['title', 'screen', 'severity', 'repro', 'actual', 'fix'] } } },
  required: ['bugs'],
}
const VERDICT = { type: 'object', properties: { real: { type: 'boolean' }, severity: { type: 'string' }, note: { type: 'string' } }, required: ['real', 'note'] }
const DONE = {
  type: 'object',
  properties: { fixed: { type: 'array', items: { type: 'string' } }, not_fixed: { type: 'array', items: { type: 'string' } }, tests: { type: 'string' }, commit: { type: 'string' }, notes: { type: 'array', items: { type: 'string' } } },
  required: ['fixed', 'tests'],
}
const CHECK = {
  type: 'object',
  properties: { items: { type: 'array', items: { type: 'object', properties: {
    requirement: { type: 'string' }, status: { type: 'string', enum: ['done', 'partial', 'missing'] }, evidence: { type: 'string' }, fix: { type: 'string' },
  }, required: ['requirement', 'status', 'evidence'] } } },
  required: ['items'],
}
const MAIN = '/Users/jumisong/JBL'
const REQS = `사용자 지시사항(원문 — 최근 것부터): ⑤ "작업 계속해서 잘 해주는데 특히 내가 이전에 준 지시사항 … 을 모두 잘 수행하도록 하고 오류 또한 면밀히 빠짐없이 검토할 수 있게끔 … 효율적으로 오류 찾아서 개선해줘!" ④ "집중모드는 너무 좋지만 집중모드와 별개로 하이라이트, 빈칸빵 등의 도구창 토글 버튼은 따로 있었으면 좋겠고, 형광펜 및 빈칸빵 켜짐 이라는 안내탭은 없어도 될 것 같아. 그리고 암기에서 각각 모든 줄에 Ox이건 필요 없을 것 같아서 없애줘. 그리고 집중모드로 토글되면서 화면이 중앙에서 치우쳐진 상태가 되는 오류, 표시 지우기에 이 카드만 이 탭만 이게 클릭되더라도 안지워지는 오류 등등 크고 작은 오류들이 많은데 면밀히 검토하면서 홈페이지, 과목탭, 각 강의자료 정리본, 정리표 등 모든 것에서 모든 오류들을 찾고 최적으로 효과적 효율적으로 개선해줬으면 좋겠어. 더불어서 시험일 표시는 안해도 되고, 정리본 읽음, 퍼센트 이런건 필요 없어. 그냥 가장 최적으로 가독성 좋고 깔끔하게 허브 홈페이지 및 과목별 탭페이지를 정리해줬으면 좋겠어." ③ "내가 한 과목에 들어가면 메뉴탭이 허브 홈페이지의 메뉴탭이랑 달라지게, 해당 과목의 메뉴탭에 대한 메뉴탭으로 specify되게끔 해주고, 전반적으로 좀 난잡한데, 가독성 좋고 조금 더 깔끔하게 … 홈페이지, 과목별 페이지 및 메뉴탭 등등을 전면적 개선해줘!" ② "jbl 허브 메인 사이트에 왼쪽 메뉴탭이 있게끔 … 내가 공부하다가 멈추고 쉬면 쉬는시간 타이머도 함께 기능하게끔 hub html 참고해서 보완해주고." / "허브 html 참고해서 쉬는 시간도 측정되게끔, 내가 공부하다가 멈추면 쉬는시간 측정되게끔" ① (3차) "materials 폴더에 올린 공부시간 측정 hub html 참고해서 달력 및 공부시간 수정/추가/측정 … 기본 페이지에 왼쪽 탭 … 공부달력탭 포함 … 빈칸빵 기능도 하이라이트처럼 색상 선택 … 각 정리본 들어가서는 왼쪽의 메뉴탭을 m 누르면 토글 … 메뉴탭 없어지면 표가 자동으로 커졌으면 … 열 간격도 … 최적으로 … 한줄요지 핵심에서 핵심 상자 내용 줄바꿈도 적절히" (2차) "H누르면 하이라이트 토글, b 누르면 빈칸빵, v 누르면 메뉴탭 안 볼 수 있게끔 … 공부 시간 측정 및 요일별 공부시간 … 정리본의 가독성, 편의성, 적절한 줄바꿈 … 전체정리표 … 족보 문제만 보는 칸에서도 … 각종 기능들이 오류 없는지, 날라가는 데이터는 없는지"`
const BASE = `작업 위치: 본 저장소 ${MAIN} (main). JBL 허브 = 치의학대학원 3학년 3쿼터 시험 대비 학습 사이트(6과목, 곧 ESTH). 사용자는 아이패드(세로 820·가로 1180, 애플펜슬·손가락, 하드웨어 키보드 — 한글 입력 상태일 수 있음)와 맥(1280)에서 GitHub Pages로 공부하며 실제 저장 데이터(형광펜·빈칸·채점·공부 시간·메모)가 있다. 방금 4차 개편(허브/과목 두 단계 메뉴·상단 시계 하나·도구 막대 토글·오류 55건·시험일/읽음 %/모드 칩/⚡ ○✕ 제거·토큰·홈/과목/강의 화면 정리)이 main에 들어갔다 — 계획 work/ux4_plan.json, 최종 시안 work/_tmp/ux4_final/, 개편 전 오류 목록 work/ux4_bugs.json, 허브 문서 tools/SPEC.md, 원칙 guide/정리본_원칙.md 7-1, CLAUDE.md.
${REQS}
빌드된 사이트: file://${MAIN}/docs/index.html (코드 원본 tools/cons/shell.html·build4.py·lecparse.py → sync_common.py로 6과목 복사 · sh tools/build_all.sh = 빌드+verify+audit+ux_all 약 50분 · 한 과목만 빌드하면 stale). playwright: ${MAIN}/.venv/bin/python. 해시만 바꾸면 안 바뀔 수 있으니 about:blank → URL. localStorage 접두 jblhub.v1.`
const STYLE = `조사 방식(중요 — 앞 조사자들이 대화가 너무 길어져 API가 멈춰 실패했다): ① 스크린샷은 꼭 필요할 때만, clip이나 scale 0.5로 작게 찍고 Read는 문제 확인용으로만(조사 전체에서 12장 이하). ② 대부분은 playwright로 DOM을 재서 확인(요소 위치·크기·겹침·textContent·scrollWidth·getComputedStyle·콘솔 오류) — 한 스크립트에서 여러 화면·뷰포트를 한 번에 돌리고 결과를 JSON 한 줄로 출력. ③ 셸 명령 하나는 2분 안에 끝나게 나누고, 오래 걸리면 백그라운드로 돌리고 짧게 확인. ④ 도구 호출은 60번 이하로 끝내고 보고.`
const LENSES = [
  ['hub', '허브 홈·허브 메뉴·상단 막대(빵부스러기·검색·시계 알약과 팝오버 — 공부/쉬는 중 휴식 타이머/대기·▶/☕/■·⏱ 크게)·📅 공부 달력·통계·백업/복원·도움말·새 기능 안내'],
  ['subject', '과목 메뉴(‹ 허브 홈·과목 바꾸기·이 과목 문서·강의·카드 목차·스크롤 스파이·서랍·M)·과목 홈(순서·진행률·교수별 표·강의 카드·2회 이상)·과목 사이 이동·뒤로가기·새로고침 상태'],
  ['learn', '강의 학습 탭(틀·카드·🔑·⭐·⚡·그림 확대·✓ 다 봄)·미니바([카드 ▾][보기 ▾ — 복습·압축·가리기][✎ 도구][⤢ 집중])·도구 막대(형광펜·빈칸 5색·자동·되돌리기/다시·메모·전체 보기·🧹 지우기 2단계)·집중 모드 가운데 정렬·키(H·B·E·N·Q·R·V·T·M·J/K·1~6)'],
  ['tables', '정리표(요약/자세히·전체정리표·👁 열 가리기·필터·열 폭·메뉴 숨김 확장)·비교표·기출 한눈표·대장·예상문제·플래시카드'],
  ['jb', 'JB 문제(목록·한 장씩·답 1·2단계·O/X·★·필터·회차 요약·복습 대기열·압축 목록·인쇄)·🖍 내 표시 모아보기·검색 결과·연도 칩 미리보기'],
  ['touchdata', '아이패드 전용(820·1180 has_touch, 손가락 tap·펜슬 touchType stylus·드래그·길게 누르기·서랍·44px) 전 화면 + 데이터 안전(1차 7095e56·2차 0918775·3차 ea74f10 허브에서 쌓은 데이터를 같은 프로필로 새 허브에서 열었을 때 형광펜·빈칸·채점·시간·메모·설정 그대로, 자동 백업·복원·되돌리기, 저장 실패, 창 두 개)'],
]
const key = b => (b.screen + '|' + b.title).toLowerCase().replace(/\s+/g, ' ').slice(0, 90)
const seen = new Set(), confirmedAll = [], fixes = []
let dry = 0, round = 0
while (dry < 1 && round < 2) {
  round++
  phase('Hunt')
  const runLens = ([k, body]) => agent(`${BASE}

## 역할: 오류 조사자(${k}, ${round}회차) — 영역: ${body}
세 뷰포트(맥 1280x900 마우스 · 아이패드 세로 820x1180 · 가로 1180x820 has_touch)에서 실제 공부하듯 모든 버튼·키·흐름을 눌러 오류를 빠짐없이 찾는다: 동작 안 함·반대로 동작·화면 치우침/겹침/잘림/가로 넘침·새로고침·뒤로가기 뒤 상태 잃음·화면끼리 값 불일치·콘솔 오류·저장 안 됨/날아감·키 충돌(한글 입력 상태 포함)·사용자 지시사항과 어긋남(예: 시험일·읽음 %가 아직 보임, 모드 칩·⚡ ○✕가 남음, 과목 안에서 허브 메뉴가 보임, 쉬는 중 휴식 타이머가 안 보임, 도구 토글이 집중 모드와 묶임). 코드도 읽어 논리 오류를 찾는다. 파일은 고치지 말 것 — 스크린샷·스크립트는 work/_tmp/ux4h_${k}_${round}/.
이미 보고된 것(다시 보고하지 말 것): ${JSON.stringify([...seen]).slice(0, 6000)}
${STYLE}
각 오류: 제목, 화면, 심각도(high=공부 방해·데이터·오작동 / medium=불편·어긋남 / low=다듬기), 재현 절차, 기대, 실제, 근거(스크린샷·출력), 원인(코드 위치), 수정안. 새로 찾은 것만, 중요한 것부터 최대 20개. 없으면 빈 목록.`, { label: `hunt:${k}:${round}`, phase: 'Hunt', schema: BUGS, effort: 'high' })
  const w1 = await parallel(LENSES.slice(0, 3).map(l => () => runLens(l)))
  const w2 = await parallel(LENSES.slice(3).map(l => () => runLens(l)))
  let res = [...w1, ...w2]
  const failed = LENSES.filter((l, i) => !res[i])
  if (failed.length) {   // 실패한 조사자는 한 번 더(실패를 '오류 없음'으로 치지 않음)
    log(`실패한 조사자 ${failed.map(l => l[0]).join(',')} 다시`)
    const again = await parallel(failed.map(l => () => runLens(l)))
    failed.forEach((l, j) => { res[LENSES.indexOf(l)] = again[j] })
  }
  const found = res.filter(Boolean).flatMap(r => r.bugs || [])
  log(`${round}회차 조사자 성공 ${res.filter(Boolean).length}/6`)
  const fresh = found.filter(b => !seen.has(key(b)))
  fresh.forEach(b => seen.add(key(b)))
  log(`${round}회차: 새 오류 후보 ${fresh.length}건`)
  if (!fresh.length) { dry++; continue }
  phase('Confirm')
  const judged = await parallel(fresh.map((b, i) => () => agent(`${BASE}

## 역할: 재현 검증자 — 아래 오류 보고가 진짜인지 독립적으로 재현해 판정한다(파일은 고치지 말 것, 스크립트는 work/_tmp/ux4c_${round}_${i}/). 스크린샷은 최대 3장·작게, 도구 호출 25번 이하, 셸 명령은 2분 안에. 재현 절차를 그대로 따라 해 보고, 안 되면 비슷한 조건 2가지를 더 시도. 재현되면 real=true와 실제 심각도, 안 되면 real=false와 이유. 사용자 지시사항과 어긋나는 것(뺄 것이 남음 등)은 재현되면 real.
오류: ${JSON.stringify(b)}`, { label: `confirm:${round}:${i}`, phase: 'Confirm', schema: VERDICT, effort: 'medium' }).then(v => ({ b, v }))))
  const conf = judged.filter(x => x && x.v && x.v.real).map(x => ({ ...x.b, severity: x.v.severity || x.b.severity, verify: x.v.note }))
  log(`${round}회차: 확인 ${conf.length} / 후보 ${fresh.length}`)
  if (!conf.length) { dry++; continue }
  dry = 0
  confirmedAll.push(...conf)
  phase('Fix')
  const fx = await agent(`${BASE}

## 역할: 수정자(${round}회차) — 재현이 확인된 오류를 모두 고친다
오류(JSON): ${JSON.stringify(conf).slice(0, 50000)}
지킬 것: LS 키·형식 하위 호환, 원고 수정 금지, 카드 textContent 보존, 기능 유지(요청으로 뺀 것 제외). 고칠 때마다 playwright로 확인(스크린샷 work/_tmp/ux4f_*.png를 Read로), 회귀 테스트 추가·갱신, SPEC·도움말, 고친 단위로 git add tools && git commit(한국어, 끝에 "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"). docs/ 커밋·push 금지. 끝에 6과목 빌드 + 관련 테스트(마지막 회차가 아니면 build_all은 생략 가능 — 대신 verify.py·audit_design.py·관련 tests). 결과(JSON): 고친 것, 못 고친 것과 이유, 테스트, 커밋.`, { label: `fix:${round}`, phase: 'Fix', schema: DONE, effort: 'high' })
  fixes.push(fx)
}
const gaps = [{ requirement: '③④ 허브 홈·과목 페이지·메뉴를 가독성 좋고 깔끔하게(요소 수)', status: 'partial', evidence: '앞 대조: 허브 홈 1280 보이는 버튼·링크 21·글자 조각 85 — 최종 수정자(앞 실행)가 처리했는지 확인' }]
const chk = null
phase('Final')
const fin = await agent(`${BASE}

## 역할: 최종 수정자 — 지시사항 점검에서 done이 아닌 항목을 모두 채우고, 앞 회차에서 못 고친 오류를 마저 고친 뒤 전체 검증
지시사항 미충족(JSON): ${JSON.stringify(gaps).slice(0, 20000)}
앞 회차 못 고친 것: ${JSON.stringify(fixes.map(f => f && f.not_fixed)).slice(0, 8000)}
${STYLE}
고친 단위로 커밋(한국어, 끝에 Co-Authored-By 줄). 끝에 sh tools/build_all.sh(백그라운드로 돌리고 2분 이하 확인을 되풀이) RESULT PASS까지(실패하면 고치고 다시). 그리고 세 뷰포트에서 허브 홈·과목 홈·강의 학습·정리표·JB 한 장씩·달력을 찍어 Read로 최종 확인. 결과(JSON): 고친 것, 못 고친 것과 이유, 테스트 결과, 마지막 커밋, 사용자에게 알릴 것.`, { label: 'final', phase: 'Final', schema: DONE, effort: 'high' })
return { rounds: round, confirmed: confirmedAll.length, confirmedAll, fixes, checklist: chk, final: fin }
