export const meta = {
  name: 'q4-jf',
  description: '4Q JB 그림 조각 검수(AGENTS JF) — 그림 문항마다 조각을 보고 상자를 고쳐 jb_crops.json · 과목은 차례로(같은 json을 둘이 쓰지 않게) · RAD는 묶음 4개',
  phases: [{ title: 'JF', detail: '두 줄 — 작은 과목 차례로 · RAD 묶음 차례로' }],
}
// args = guide/handoff/wf4q/args/jf.json ({small: [job…], rad: [job…]}) · job = {sid, dir, ids, part?, note?}
// 같은 과목 json(tools/<sid>/jb_crops.json)을 두 담당이 동시에 쓰지 않게 줄마다 차례로 — 두 줄(small · rad)만 나란히.
// HINS·ESTH4는 그 과목 정리본 run이 끝난 뒤(빌드가 겹치지 않게) small 줄 끝에 넣음.
const H = `저장소 /home/user/jbl. 파이썬 .venv/bin/python. 보고는 한국어. 공통 머리 = .claude/skills/jbl-update/AGENTS.md 맨 위 '공통 머리' 블록(먼저 읽기 · 금지). 지시문 = AGENTS.md 'JF JB 그림 조각 검수' 블록 + RULES.md 0-1 'JB 그림 조각' 줄 + tools/SPEC.md 'JB 그림 조각' 절 + tools/jbfig.py 맨 위 설명 그대로.
4Q 과목(docs/packs/<SID>.js · 그림 파일 방식 — build4가 조각도 docs/packs/img/<SID>/에 씀). JB 쪽 그림 = work/jb/<SID>_20<판>/<쪽>.jpeg(924폭 — 상자 좌표는 이 픽셀). tesseract(kor) 필요 — 없으면 apt-get install -y tesseract-ocr tesseract-ocr-kor.
같은 시각에 다른 과목 JF 담당·다른 과목 정리본 담당이 돈다 — 맡은 과목의 tools/<sid>/jb_crops.json만 고침(맡은 id 줄만 — 다른 id 줄은 그대로) · 빌드는 tools/<sid>/build4.py만 · annot·lec·subject·assemble·shell·rehub·sync_common·full_check·커밋·git stash 금지.
절차: ① \`.venv/bin/python tools/jbfig.py <SID> --ids <맡은 id> --dump\`(맡은 id 줄만 json에 씀 · 검수용 work/_tmp/jbfig/<SID>/<id>_q1.jpg·_a1.jpg… · 상자를 그린 쪽 work/_tmp/jbfig/<SID>/pages/<판>-<쪽>.jpg) ② 문항마다 조각·상자 그린 쪽·원래 쪽 그림을 한 장씩 Read — 문제 그림(q)이 빠짐·잘림·남의 문항 그림·답 글자 섞임이 없는지 · 그림 속 라벨이 곧 답이면 그 그림은 a(답 쪽)에만 · 문제는 그림을 말하는데 JB에 그림이 없으면 "nofig": "absent" · 그림 문항이 아니면(글만으로 풀림) "nofig": "text" · 고친 상자·확인한 문항은 문항 항목에 "fix": true + "note" 한 줄(무엇을 봤는지 — 그림 속 글자·답 추측 금지) ③ 고친 뒤 같은 명령 다시(fix 항목은 그대로 두고 조각만 다시 그림) → 조각 다시 Read ④ \`.venv/bin/python tools/<sid>/build4.py\` → 맡은 id 카드에 '쪽 전체로 확인' 안내 0(검사: \`.venv/bin/python -c "import re,sys;t=open('docs/packs/<SID>.js',encoding='utf-8').read().replace(chr(92)+chr(34),chr(34));ids=sys.argv[1].split(',');print([i for i in ids if (lambda m:m and '쪽 전체로 확인' in t[m.end():t.find('</article>',m.end())])(re.search(r'data-id=\\"'+i+r'\\"',t))])" <맡은 id>\` = [] ) · 문제 조각(q)에 답 글자 0.
보고 work/_tmp/jbfig/REPORT_<SID><묶음>.md(맨 위 '맡은 id n · 조각 붙음 n · absent n · text n · 남음 n' 한 줄 → 문항마다 한 줄 결정). 보고 파일이 이미 있으면(앞 담당이 한도로 멈춤) 그 보고와 json의 fix 상태를 먼저 보고 남은 id만.
최종 답 = schema(done = 맡은 id 전부 결정·빌드·검사까지 마침 · remaining = 못 끝낸 id · summary = 5줄).`
const S = { type: 'object', properties: { done: { type: 'boolean' }, remaining: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } }, required: ['done', 'remaining', 'summary'] }
const job = (j) => `${H}

과목 ${j.sid}(tools/${j.dir}/) · 맡은 id ${j.ids.length}개: ${j.ids.join(',')}${j.part ? ` · RAD 묶음 ${j.part}/4(앞 묶음 담당이 같은 json의 다른 id를 이미 고쳤음 — 그 줄은 건드리지 않음)` : ''}.
${j.note || ''}`
async function run1(j) {
  let r = await agent(job(j), { label: `JF:${j.sid}${j.part ? ':' + j.part : ''}`, phase: 'JF', schema: S })
  if (r && !r.done && r.remaining && r.remaining.length) {
    r = await agent(job({ ...j, ids: r.remaining, note: `(앞 담당이 다 못 끝냄 — 남은 id만 · 보고 파일 이어 씀) ${j.note || ''}` }), { label: `JF:${j.sid}${j.part ? ':' + j.part : ''}:2`, phase: 'JF', schema: S })
  }
  return { sid: j.sid, part: j.part || 0, r }
}
async function lane(jobs) { const out = []; for (const j of jobs) out.push(await run1(j)); return out }
const A = args.small, R = args.rad
const res = await parallel([() => lane(A), () => lane(R)])
const flat = res.flat().filter(Boolean)
const bad = flat.filter(x => !x.r || !x.r.done)
log(`JF 끝: ${flat.length}묶음 · 덜 됨 ${bad.length}`)
return flat.map(x => ({ sid: x.sid, part: x.part, done: x.r ? x.r.done : null, remaining: x.r ? x.r.remaining : null, summary: x.r ? x.r.summary.slice(0, 600) : '결과 없음(한도·오류 — resume)' }))
