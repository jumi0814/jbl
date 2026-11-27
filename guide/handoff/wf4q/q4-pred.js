export const meta = {
  name: 'q4-pred',
  description: '4Q 예상문제 다듬기 — 과목마다 기준본 → 강의 묶음 P(TREND·교수 프로필·RULES 14 c⑥·빠진 문제 찾기) → 합치기·검사 → 독립 감사 PA → 합치기·검사·빌드 (최종 N제 없음 — 사용자 11-27)',
  whenToUse: '그 과목 정리본(작성·검토·QA)이 모두 끝난 뒤 — 같은 과목 정리본 run과 겹치지 않게',
  phases: [
    { title: 'Prep', detail: '통합 담당 — pred_dump 기준본 · dump_review · fmt_audit · link_audit · 묶음 조각(pred_slice)' },
    { title: 'P', detail: '강의 묶음마다 예상 판정(유지·개선 oid=·보관 x=1)·빠진 문제 찾기' },
    { title: 'Merge', detail: 'pred_merge · pred_check · build4 · link_audit · fmt_audit · check_lec · scan_render · PA 조각' },
    { title: 'PA', detail: '묶음마다 다른 담당이 독립 감사(상 전부 + 바뀐 답 쪽 이미지 대조)' },
    { title: 'Final', detail: 'pred_merge · 검사 · build4' },
  ],
}
// args = {subjects: [{sid, dir, ko, groups: [[KEY…], …], note?}]} · 과목은 차례로 pipeline(과목끼리 나란히) · 한 과목 안 P·PA 묶음은 나란히(조각 파일이 다름)
const H = `저장소 /home/user/jbl. 파이썬 .venv/bin/python(믿지 않는 파일을 읽는 파이썬은 -I). 보고는 한국어.
공통 머리 = .claude/skills/jbl-update/AGENTS.md 맨 위 '공통 머리' 블록 전체를 그대로 따른다(먼저 읽기 · 금지 · 자료 = 쪽 이미지를 Read로 직접 · 끝내기 전 줄바꿈 검사 · 최종 답 5줄).
이 과목은 4Q — RULES 14(특히 c ①~⑥ · ⑥ 1~8 '2026 3Q 적중 분석에서 배운 것') + guide/handoff/Q4_RULES_BRIEF.md 6절을 먼저. 교수 경향 = work/<SID>/pred26/TREND_<SID>.md(없으면 guide/handoff/trend4q/TREND_<SID>.md) · 교수 프로필 guide/prof/<교수>.md · 그 교수 3Q 적중 보고 guide/handoff/hit26/HIT_<3Q 과목>.md(프로필 '26 3Q 실제 출제' 절로 과목을 찾음 · 없으면 '참고 — 불확실').
사용자 11-27: "최종 n제는 나중에 내가 만들라는 과목만 … 예상문제 만드는거에 가장 최선으로" — 이 run은 예상문제만(최종 N제·final.txt 손대지 않음) · 정리본·annot·tables는 고치지 않음(고칠 것이 보이면 보고 '정리본 몫' 절에만).
같은 시각에 같은 과목 다른 묶음 담당이 돈다 — 맡은 조각 파일만 고침 · tools/<sid>/pred.txt 직접 수정·build4·rehub·merge_parts·split_parts·pred_merge(--dry 말고)·sync_common·full_check·커밋·git stash 금지(검사 명령은 됨).
보고 파일이 이미 있으면(앞 담당이 한도로 멈춤) 그 보고와 조각 상태를 먼저 확인하고 남은 것만(보고는 지우지 않고 이어 씀).
최종 답 = schema(done = 맡은 강의 블록 전부 판정·고침·끝내기 전 검사까지 마쳤으면 true — 한도·분량으로 다 못 했으면 false(다음 담당이 보고를 보고 이어 감) · summary = 5줄).`
const HM = `저장소 /home/user/jbl. 파이썬 .venv/bin/python. 보고는 한국어. 너는 예상문제 단계 통합 담당 — 글 내용(문제·답)은 고치지 않음 · 명령을 돌리고 결과를 그대로 적음 · 커밋·rehub·sync_common·full_check·split_parts·merge_parts 금지(정리본 parts는 이 단계와 무관 — 예상은 tools/<sid>/pred.txt에 pred_merge로).
최종 답 = schema(ok = 막힘 없음(검사 ✗0) · summary = 단계·명령마다 결과 한 줄 + 남은 △ 목록).`
const MS = { type: 'object', properties: { ok: { type: 'boolean' }, summary: { type: 'string' } }, required: ['ok', 'summary'] }
const WS = { type: 'object', properties: { done: { type: 'boolean' }, summary: { type: 'string' } }, required: ['done', 'summary'] }
async function main(s, step, body, ph) {
  const r = await agent(`${HM}
과목 ${s.sid}(tools/${s.dir}/ · ${s.ko}). 단계 '${step}'. 보고 파일 work/${s.sid}/pred26/M_${step}.md(머리 먼저 · 명령마다 덧붙임).
묶음: ${s.groups.map((g, i) => `P${i + 1} = ${g.join(' ')}`).join(' · ')}.
${body}`, { label: `main:${s.sid}:${step}`, phase: ph, model: 'sonnet', schema: MS })
  if (r == null) throw new Error(`main ${s.sid} ${step}: 결과 없음(한도·오류) — resume`)
  if (!r.ok) throw new Error(`main ${s.sid} ${step} 막힘: ${r.summary.slice(0, 500)}`)
  return r
}
async function worker(prompt, label, ph) {
  let r = await agent(prompt, { label, phase: ph, schema: WS })
  if (r && !r.done) r = await agent(prompt + `\n(앞 담당이 다 못 끝냄 — 보고 파일과 조각 상태를 보고 남은 블록만 · 보고 이어 씀)`, { label: label + ':2', phase: ph, schema: WS })
  if (r && !r.done) r = await agent(prompt + `\n(앞 담당 둘이 다 못 끝냄 — 보고 파일과 조각 상태를 보고 남은 블록만 · 보고 이어 씀)`, { label: label + ':3', phase: ph, schema: WS })
  if (r == null || !r.done) throw new Error(`${label}: 다 못 끝냄 — resume`)
  return r
}
async function subject(s) {
  const G = s.groups.map((g, i) => ({ n: i + 1, keys: g }))
  await main(s, 'prep', `할 일(차례로):
1. 지금 기준본 보관: work/${s.sid}/pred26/pred_before.json·.md가 있으면 pred_before_old_<그 파일 수정 날짜>.*로 이름 바꿈 → \`.venv/bin/python tools/pred_dump.py ${s.sid}\`(지금 docs/packs/${s.sid}.js 예상 = 사용자 ✓·✗·★ 키 aid 기준본 — 담당이 문제를 고쳐 쓰면 oid=<이 aid>).
2. \`.venv/bin/python tools/dump_review.py ${s.sid}\`(questions.md·qids.json 새로) · \`.venv/bin/python tools/fmt_audit.py ${s.sid} > work/${s.sid}/pred26/fmt_before.md\` · \`.venv/bin/python tools/link_audit.py ${s.sid} > work/${s.sid}/pred26/link_before.md 2>&1\` · \`.venv/bin/python tools/pred_check.py ${s.sid} > work/${s.sid}/pred26/check_before.md 2>&1\`.
3. 묶음마다 \`.venv/bin/python tools/pred_slice.py ${s.sid} P<n> <그 묶음 키들>\` → work/${s.sid}/pred26/P<n>.txt(지금 블록 그대로 — 담당이 이 파일을 고침). 블록 0인 키도 묶음에 그대로(담당이 새로 씀).
4. 보고: 묶음마다 블록 수(상·중·하·x=1) · link_before의 '최근 해 예상 연결 없음' 문항 id(묶음별) · check_before ✗·△ 수.
${s.note ? '과목 메모: ' + s.note : ''}`, 'Prep')
  const pP = (g) => `${H}

과목 ${s.sid}(tools/${s.dir}/ · ${s.ko}) 예상문제 P — 강의 ${g.keys.join(' ')}. 지시문 = .claude/skills/jbl-update/AGENTS.md 'P 예상문제' 블록 전체(4Q 줄·11-10 '읽기'·'끝내기 전 검사' 포함) 그대로.
고칠 파일 = work/${s.sid}/pred26/P${g.n}.txt(통합 담당이 pred_slice로 만든 지금 블록 — 정리본 단계 담당이 쓴 초안 · 이 파일 안에서 블록마다 유지/개선(oid=<pred_before aid>)/보관(x=1 · why에 사유)을 정하고 빠진 문제를 더함 · 지우지 않음). 기준 aid = work/${s.sid}/pred26/pred_before.{md,json}. 최근 해 연결 없는 문항 = work/${s.sid}/pred26/link_before.md(맡은 강의 몫은 b=로 건 예상 ≥1) · 형식 표 = work/${s.sid}/pred26/fmt_before.md.
강의 원고(읽기만) tools/${s.dir}/lec_<KEY>.txt · 쪽 이미지 work/${s.sid}/lec/<폴더>/<쪽>.jpg(subject.py LECMAP) — 답 근거는 쪽 이미지로 확인(답 = 슬라이드 글 · 필기는 RULES 11 K1~K3만). 25 임시본 강의(원고 @UPD '25 자료 임시')는 25 쪽이 본문 — 26에서 빠짐 표시 없음. 강의 없는 키(LECMAP 폴더 None)는 JB 짤 변형만(b= · 답 = JB 답 원문 근거).
${s.note ? '과목 메모: ' + s.note + '\n' : ''}보고 work/${s.sid}/pred26/R_P${g.n}.md(맨 위 '읽음: …' · '줄바꿈: 블록 n개 다 봄 · 고친 줄 m · ★ 0' 두 줄 → 강의마다 유지·개선·보관·새(상/중/하)·그림·그림빵 수 · 상 근거 꼴 · 빠진 문제 찾기 '본 쪽 n/N · 후보 k · 넣음 m · 뺀 이유' · '정리본 몫'·'사용자 확인' 절).
끝내기 전: \`.venv/bin/python tools/pred_check.py ${s.sid} --file work/${s.sid}/pred26/P${g.n}.txt\` ✗0 · \`.venv/bin/python tools/pred_merge.py ${s.sid} work/${s.sid}/pred26/P${g.n}.txt --dry\` 통과 · check_abbr·check_eyears(맡은 강의) · \`grep -n '[★☆]' work/${s.sid}/pred26/P${g.n}.txt\` 0.`
  await Promise.all(G.map(g => worker(pP(g), `P:${s.sid}:P${g.n}`, 'P')))
  await main(s, 'merge1', `할 일(차례로):
1. \`.venv/bin/python tools/pred_merge.py ${s.sid} ${G.map(g => `work/${s.sid}/pred26/P${g.n}.txt`).join(' ')} --dry\` → 통과면 --dry 없이. 멈추면(옛 aid 빠짐 등) 그 메시지와 어느 조각·블록인지 적고 ok=false(고치지 않음).
2. \`.venv/bin/python tools/pred_check.py ${s.sid}\` ✗0 · \`.venv/bin/python tools/${s.dir}/build4.py\` 오류 0 · \`.venv/bin/python tools/link_audit.py ${s.sid}\`(✗0 · △ '최근 해 예상 연결 없음' 0 — 남으면 id) · \`.venv/bin/python tools/fmt_audit.py ${s.sid}\`(예상 형식 = 교수 꼴 — 어긋남 목록) · \`.venv/bin/python tools/check_lec.py ${s.sid}\`(pred ★ 경고 0) · \`.venv/bin/python tools/scan_render.py ${s.sid}\`(결함 목록) · \`.venv/bin/python tools/check_eyears.py\` 중 이 과목 줄 0.
3. PA 조각: 묶음마다 \`.venv/bin/python tools/pred_slice.py ${s.sid} PA<n> <그 묶음 키들>\` → work/${s.sid}/pred26/PA<n>.txt.
4. 보고: 묶음마다 블록 수 전 → 후(상·중·하·x=1·새) · 위 검사 결과 · 남은 △.`, 'Merge')
  const pA = (g) => `${H}

과목 ${s.sid}(tools/${s.dir}/ · ${s.ko}) 예상 독립 감사 PA — 강의 ${g.keys.join(' ')}. 지시문 = AGENTS.md 'PA 예상 독립 감사' 블록 전체(4Q 줄 포함 — 상 = 근거 기준 · 옛 1회 기출이 중·하로 남았으면 올림 · 25 전용은 그 기출 짤 변형만) + guide/handoff/PRED_AUDIT1027B_BRIEF.md(기준 커밋·사본 이름은 이번 것으로: 기준본 = work/${s.sid}/pred26/pred_before.md · 이번 P 보고 = work/${s.sid}/pred26/R_P${g.n}.md — 믿지 말고 직접 대조).
고칠 파일 = work/${s.sid}/pred26/PA${g.n}.txt(P 단계 뒤 지금 블록). 상 전부 + P 단계에서 바뀌거나 새로 든 문항의 답을 쪽 이미지로 대조 · 정답이 하나로 갈리는지 · 틀린 선지가 슬라이드 글로 분명히 틀린지 · 형식 = 그 교수 기출 꼴 · why 첫머리 근거 꼴 · 답에 내부 문항 id 0 · 줄바꿈(RULES 11 첫 두 줄) · 지우지 않음(x=1).
${s.note ? '과목 메모: ' + s.note + '\n' : ''}보고 work/${s.sid}/pred26/A_P${g.n}.md(맨 위 '읽음: …' · '줄바꿈: 블록 n개 다 봄 · 고친 줄 m · ★ 0' → 대조한 문항 수 · 고친 것(전 → 후) · 올림/낮춤 · 사용자 확인).
끝내기 전: \`.venv/bin/python tools/pred_check.py ${s.sid} --file work/${s.sid}/pred26/PA${g.n}.txt\` ✗0 · \`.venv/bin/python tools/pred_merge.py ${s.sid} work/${s.sid}/pred26/PA${g.n}.txt --dry\` 통과 · check_abbr · check_eyears · ★ 0.`
  await Promise.all(G.map(g => worker(pA(g), `PA:${s.sid}:P${g.n}`, 'PA')))
  const fin = await main(s, 'final', `할 일(차례로):
1. \`.venv/bin/python tools/pred_merge.py ${s.sid} ${G.map(g => `work/${s.sid}/pred26/PA${g.n}.txt`).join(' ')} --dry\` → 통과면 --dry 없이(멈추면 ok=false · 메시지 그대로).
2. merge1의 2번 검사 전부 다시 + \`.venv/bin/python tools/pred_dump.py ${s.sid}\`를 하지 말 것(기준본은 그대로 둠 — 다음 배포 뒤 메인이 새로).
3. 보고: 과목 예상 전 → 후(활성·상·중·하·x=1·새 · 강의별) · 검사 결과 · 남은 △ · 감사 보고 '사용자 확인' 모음.`, 'Final')
  return { sid: s.sid, summary: fin.summary.slice(0, 1500) }
}
const out = await pipeline(args.subjects, s => subject(s))
log(`예상 끝: ${out.filter(Boolean).map(x => x.sid).join(' · ')}`)
return out
