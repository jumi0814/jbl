export const meta = {
  name: 'q4-queue',
  description: '4Q 남은 일 차례로(사용자 11-28 "순차적으로 … 토큰 최적 · 퀄리티 유지") — 과목마다 25 임시본 정리본(q4-notes2) → 그 과목 예상(q4-pred) · 끝에 JB 그림 조각(q4-jf)',
  whenToUse: '한 줄로 차례 실행(동시 담당 = 이 run의 상한 하나) — 멈추면 같은 args로 resume(끝난 단계는 캐시)',
  phases: [{ title: 'Queue', detail: 'steps 차례로 — 하위 workflow 하나씩' }],
}
// args = {steps: [{label, kind: 'notes'|'pred'|'jf', args}]} · 하위 스크립트는 고치지 않음(도는 run과 같은 파일 — 글자를 바꾸면 캐시가 깨짐)
const BASE = '/home/user/jbl/guide/handoff/wf4q/'
const REF = { notes: 'q4-notes2.js', pred: 'q4-pred.js', jf: 'q4-jf.js' }
const out = []
for (const st of args.steps) {
  log(`시작: ${st.label}`)
  const r = await workflow({ scriptPath: BASE + REF[st.kind] }, st.args)
  const bad = Array.isArray(r) && r.some(x => x == null)
  out.push({ label: st.label, done: !bad })
  if (bad) throw new Error(`${st.label}: 하위 run 일부 실패(한도·오류) — 이 queue를 같은 args로 resume`)
  log(`끝: ${st.label}`)
}
return out
