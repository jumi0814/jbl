export const meta = {
  name: 'jbl-ux4-final',
  description: '허브 4차 마무리 — 원래 이름 그대로·끊긴 작업 마무리·% 정리 → 확인된 오류 118건 재검(3명) → 남은 것 수정 → 최종 build_all',
  phases: [
    { title: 'Names', detail: '이름 원래대로·끊긴 작업·%' },
    { title: 'Recheck', detail: '118건 재현 재검' },
    { title: 'Fix', detail: '남은 오류 수정' },
    { title: 'Final', detail: 'build_all·세 뷰포트 확인' },
  ],
}
const DONE = {
  type: 'object',
  properties: { fixed: { type: 'array', items: { type: 'string' } }, not_fixed: { type: 'array', items: { type: 'string' } }, tests: { type: 'string' }, commit: { type: 'string' }, notes: { type: 'array', items: { type: 'string' } } },
  required: ['fixed', 'tests'],
}
const RECHECK = {
  type: 'object',
  properties: { still: { type: 'array', items: { type: 'object', properties: {
    n: { type: 'integer' }, title: { type: 'string' }, severity: { type: 'string' }, now: { type: 'string' }, fix: { type: 'string' },
  }, required: ['n', 'title', 'now'] } }, ok_count: { type: 'integer' }, notes: { type: 'string' } },
  required: ['still', 'ok_count'],
}
const MAIN = '/Users/jumisong/JBL'
const STYLE = `작업 방식(중요 — API가 불안정해 긴 대화가 자주 끊긴다): 스크린샷은 꼭 필요할 때만 clip·scale 0.5로 작게(전체 12장 이하), 대부분은 playwright로 DOM을 재서 확인(위치·크기·겹침·textContent·scrollWidth·콘솔 오류 — 한 스크립트에서 여러 화면·뷰포트를 돌리고 결과를 JSON 한 줄로). 셸 명령 하나는 2분 안에 끝나게 나누고, 오래 걸리는 것(build_all 약 50분)은 nohup 백그라운드로 돌리고 로그를 짧게 확인. 도구 호출은 80번 이하.`
const BASE = `작업 위치: 본 저장소 ${MAIN} (main). JBL 허브 = 치의학대학원 3학년 3쿼터 시험 대비 학습 사이트(6과목, 곧 ESTH). 사용자는 아이패드(세로 820·가로 1180, 펜슬·손가락, 하드웨어 키보드 — 한글 입력 상태일 수 있음)와 맥(1280)에서 GitHub Pages로 공부하며 실제 저장 데이터가 있다. 4차 개편(허브/과목 두 단계 메뉴·상단 시계 하나·도구 막대 토글·집중 모드 가운데·지우기 2단계·시험일/읽음 %/모드 칩/⚡ ○✕ 제거·calm 화면 정리)과 오류 조사 2회(확인 118건, 수정 58건 커밋) 뒤다. 계획 work/ux4_plan.json, 확인된 오류 전체 work/ux4_confirmed.json(n·title·screen·severity·repro·expected·actual·cause·fix·verify — 재현 스크립트는 work/_tmp/ux4c_<회차>_<i>/, 1회차 i=0..59 → n=i+1, 2회차 i=0..59 중 58건 → n=61..118), 허브 문서 tools/SPEC.md, 원칙 guide/정리본_원칙.md 7-1·7-5, CLAUDE.md.
코드 원본 tools/cons/{shell.html, build4.py, lecparse.py, trend.py} → .venv/bin/python tools/sync_common.py 로 6과목 복사 · 6과목 빌드 = 각 tools/<sid>/build4.py(한 과목만 빌드하면 stale) · 전체 = sh tools/build_all.sh(빌드+verify+audit+ux_all 80여 개). playwright ${MAIN}/.venv/bin/python, 사이트 file://${MAIN}/docs/index.html(about:blank → URL, LS 접두 jblhub.v1.).
지킬 것: LS 키·형식 하위 호환(새 키·이관만), 원고(lec_*.txt·annot·tables·pred) 수정 금지, 카드 textContent 보존(legacy_restore 통과), 기능 유지. 고친 단위로 git add tools && git commit(한국어, 끝에 "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"), docs/ 커밋·push 금지(오케스트레이터가 배포).
${STYLE}`
phase('Names')
const names = await agent(`${BASE}

## 역할: 마무리 구현자
① 끊긴 작업 마무리: git status에 커밋 안 된 변경(tools/cons/shell.html 등 6과목 사본·SPEC·tests ux3_fixes·ux3_rest·ux3_restui·ux4c_fix1 수정, 새 tests/ux4d_fix.py)이 있다 — 앞 '최종 수정자'가 네트워크 오류로 끊기기 전에 하던 것. git diff로 무엇을 하던 중인지 파악해 완성하거나(맞으면), 틀린 부분은 고쳐 커밋.
② 사용자 요청(원문, 10-01): "과목명 및 강의자료 이름 등은 너 마음대로 줄이지 말고 원래 그대로로 바꿔줘." → 과목명은 SUBJECTS의 원래 이름(구강악안면외과학 1·임상치과보존학·치과임플란트학·임상두경부해부학·노인치과학·임상치과약물치료학·심미치과학)으로, 강의 이름은 팩의 원래 강의 제목 그대로(지금 sjShort·짧은 이름·sname 등으로 줄인 것 전부) — 허브 메뉴 과목 줄·과목 메뉴 머리·과목 바꾸기·강의 목록·빵부스러기·허브 홈(이어서·오늘 할 일·최근·과목 표·이번 주)·과목 홈·달력(범례·과목 막대·날 패널·기록 줄·+ 시간 추가 select)·통계·검색 결과·시계 팝오버·내 표시·JB 칩·도움말·새 기능 안내 등 화면에 보이는 모든 곳. 자리가 좁으면 말줄임(…)·약칭 대신 줄바꿈(2~3줄)으로 — 메뉴 폭·표 칸은 줄바꿈이 자연스럽게(keep-all, 줄간격). 카드 목차의 카드 제목도 가능하면 말줄임 대신 2줄까지. 짧은 이름 데이터(SUBJECTS 셋째 값)는 지우지 말고 쓰지만 않게(나중 대비).
③ % 정리(사용자: "정리본 읽음, 퍼센트 이런건 필요 없어" — 허브 홈·과목 화면 정리 맥락): 허브 홈·과목 화면·메뉴·시계 알약/팝오버·⏱ 크게에서 % 글자를 빼고 시간(1:59 / 4:00)·개수로만. 달력 달성 고리도 % 대신 '1:59 / 4:00'. 집중 %(휴식 비율)는 빼고 휴식 시간만.
각 변경을 세 뷰포트에서 확인(텍스트 검사: 화면 innerText에 약칭·'…'로 끝나는 과목/강의 이름 0, '%' 0 — 정리표·원고 내용 속 %는 제외), 회귀 테스트 추가(tools/tests/ux4e_names.py), SPEC·도움말 갱신, 커밋. 6과목 빌드 + verify.py + 관련 테스트.
결과(JSON): 한 것, 못 한 것과 이유, 테스트, 마지막 커밋.`, { label: 'names', phase: 'Names', schema: DONE, effort: 'high' })
phase('Recheck')
const RANGES = [[1, 40], [41, 80], [81, 118]]
const rc = await parallel(RANGES.map(([a, b]) => () => agent(`${BASE}

## 역할: 재검자 — work/ux4_confirmed.json의 n=${a}~${b} 오류가 지금 빌드(docs/)에서 정말 고쳐졌는지 하나씩 재현해 확인(파일은 고치지 말 것 — 스크립트는 work/_tmp/ux4r_${a}/). 각 항목의 repro를 따라 하고(있으면 work/_tmp/ux4c_*/ 재현 스크립트 재사용), 여전히 재현되거나 절반만 고쳐진 것만 still에 적는다(now = 지금 상태 한 줄, fix = 수정안). 이름을 원래대로 바꾼 변경(마무리 구현자 보고: ${JSON.stringify(names).slice(0, 1500)})과 충돌하는 옛 기대(짧은 이름)는 무시. ok_count = 고쳐진 것 수.`, { label: `recheck:${a}-${b}`, phase: 'Recheck', schema: RECHECK, effort: 'medium' })))
const still = rc.filter(Boolean).flatMap(r => r.still || [])
log(`재검: 남은 오류 ${still.length}건 · 고쳐진 것 ${rc.filter(Boolean).reduce((s, r) => s + (r.ok_count || 0), 0)} · 재검자 성공 ${rc.filter(Boolean).length}/3`)
phase('Fix')
let fix = null
if (still.length) fix = await agent(`${BASE}

## 역할: 수정자 — 재검에서 아직 남은 오류를 모두 고친다
남은 오류(JSON — n은 work/ux4_confirmed.json 번호, 원래 repro·cause는 그 파일에서): ${JSON.stringify(still).slice(0, 40000)}
고칠 때마다 확인·회귀 테스트(tools/tests/ux4e_fix.py)·SPEC·커밋. 6과목 빌드 + verify.py + 관련 테스트. 결과(JSON): 고친 것(n별), 못 고친 것과 이유, 테스트, 커밋.`, { label: 'fix', phase: 'Fix', schema: DONE, effort: 'high' })
phase('Final')
const fin = await agent(`${BASE}

## 역할: 최종 검증자 — 전체 검증을 통과시키고 눈으로 최종 확인
1) nohup sh tools/build_all.sh > work/_tmp/ux4_final_ball.log 2>&1 & 로 돌리고 짧게 확인하며 기다린다. 실패하면 원인을 고치고(커밋) 다시 — RESULT PASS·EXIT 0까지. 2) 세 뷰포트에서 허브 홈·허브 메뉴·과목 홈(과목 메뉴)·강의 학습(도구 켬/끔·집중 모드)·정리표·JB 한 장씩·공부 달력을 한 장씩 작게 찍어 Read로 확인: 과목·강의 이름이 원래 그대로인지, 시험일·읽음·%·모드 칩·⚡ ○✕가 없는지, 겹침·가로 넘침이 없는지. 문제는 고치고 다시 build_all. 3) 도움말과 SPEC이 지금 동작과 맞는지.
앞 보고: ${JSON.stringify({ names, still: still.length, fix }).slice(0, 6000)}
결과(JSON): 고친 것, 못 고친 것과 이유, 테스트 결과(build_all 로그 경로·통과 수), 마지막 커밋, 사용자에게 알릴 것.`, { label: 'final', phase: 'Final', schema: DONE, effort: 'high' })
return { names, rc, still, fix, fin }
