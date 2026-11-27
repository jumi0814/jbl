export const meta = {
  name: 'q4-notes2',
  description: '4Q 정리본 — 과목마다 준비 → 강의별 작성(B2Q) → 독립 검토(26 강의 3회 · 25 임시본 2회 · 새 문제 있으면 확인) → 26 강의 F 다듬기 → QA → 고침',
  whenToUse: '4Q 과목 정리본 묶음(args.subjects — 과목마다 이번 강의 목록)',
  phases: [
    { title: 'Prep', detail: '통합 담당 — build4·split·dump_review' },
    { title: 'Write', detail: '강의마다 B2Q 작성 · 올해 강의 없는 키 한 담당' },
    { title: 'Review', detail: '강의마다 독립 검토 C(회차마다 다른 담당) + 회차 끝 merge' },
    { title: 'Polish', detail: '26 강의 F 한 담당(D1→D3→D4→D2→D5→D2b→@TIP)' },
    { title: 'QA', detail: '사용자 눈 QA(E) → 강의별 고침 → 마지막 merge' },
  ],
}

const H = `저장소 /home/user/jbl. 파이썬 .venv/bin/python(믿지 않는 파일을 읽는 파이썬은 -I). 보고는 한국어.
공통 머리 = .claude/skills/jbl-update/AGENTS.md 맨 위 '공통 머리' 블록 전체를 그대로 따른다(먼저 읽기 · 금지 · 자료 = 모든 쪽 이미지를 Read로 직접 · 26 표시 · 보고 파일은 머리 먼저·단계마다 덧붙임 · 예상 블록 · 자료 공개 · 끝내기 전 줄바꿈 검사 · 최종 답 5줄).
이 과목은 4Q — RULES 14 + guide/handoff/Q4_RULES_BRIEF.md 먼저(26이 본문 · 25 전용은 📜 ⭐ 줄만 · 25 임시본 머리). JB 단계 보고 work/<SID>/jb/R_JB_<SID>.md 2절(강의 표)·5절과 V_JB_<SID>.md(독립 검수)를 이 강의 몫만 읽음. 과목 출제 경향 = work/<SID>/pred26/TREND_<SID>.md(TREND 담당이 쓰는 중일 수 있음 — 있으면 이 강의 문단을 '이 강의의 틀' 출제 경향·공부 전략에, 없으면 questions.md로 쓰고 보고에 'TREND 없이 씀').
같은 시각에 같은 과목 다른 강의 담당이 돈다 — 맡은 파일만 고침 · build4·rehub·merge_parts·split_parts·sync_common·full_check·커밋·git stash·브라우저 금지(검사 명령은 됨: check_lec·check_25only·check_eyears·check_abbr·check_unote·dump_breaks·render_line·text_diff(비교만 — --save 금지)·pred_check --file).
보고 파일이 이미 있으면(앞 담당이 사용 한도로 멈춤) 그 보고와 파일 상태를 먼저 확인하고 남은 것만(보고는 지우지 않고 이어 씀).`
const HM = `저장소 /home/user/jbl. 파이썬 .venv/bin/python. 보고는 한국어. 지시문 = guide/handoff/Q4_MAIN_BRIEF.md(통합 담당 — 글 내용은 고치지 않음 · 그 '금지' 그대로). 최종 답 = schema(ok = 막힘 없음 · summary = 그 BRIEF '돌려줄 것' 꼴 전체).`
const MS = { type: 'object', properties: { ok: { type: 'boolean' }, summary: { type: 'string' } }, required: ['ok', 'summary'] }
const RS = { type: 'object', properties: { new_problems: { type: 'integer' }, summary: { type: 'string' } }, required: ['new_problems', 'summary'] }
const WS = { type: 'object', properties: { done: { type: 'boolean' }, summary: { type: 'string' } }, required: ['done', 'summary'] }
const V2T = `\n최종 답 = schema(done = 원고·parts 3개·보고를 다 쓰고 '끝내기 전 검사'까지 마쳤으면 true — 사용 한도·분량으로 다 못 썼으면 false(다음 담당이 보고를 보고 이어 감) · summary = 5줄).`
const QS = { type: 'object', properties: { fix_keys: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } }, required: ['fix_keys', 'summary'] }

async function must(p, what) { const r = await p; if (r == null) throw new Error(`${what}: 결과 없음(한도·오류) — resume`); return r }
async function all(thunks, what) { const rs = await parallel(thunks); if (rs.some(r => r == null)) throw new Error(`${what}: 담당 일부 실패 — resume`); return rs }
async function main(s, step, tag, extra, ph) {
  const r = await must(agent(`${HM}
과목 ${s.sid}(tools/${s.dir}/ · ${s.ko}). 단계 '${step}'. 보고 파일 work/${s.sid}/main/M_${tag}.md. 이번 묶음 강의 = ${s.lecs.map(L => L.key).concat(s.nomat || []).join(' ')}(나머지 강의는 자리 표시 그대로 — split·merge는 과목 전체라 상관없음 · 강의별 표는 이번 묶음 강의만).
${extra || ''}`, { label: `main:${s.sid}:${tag}`, phase: ph, model: 'sonnet', schema: MS }), `main ${s.sid} ${tag}`)
  if (!r.ok) throw new Error(`main ${s.sid} ${tag} 막힘: ${r.summary.slice(0, 400)}`)
  return r
}
const branch = (s, L) => L.br === '교' ? `(교과서) 강의자료 = 교과서(LECMAP ${L.key} 폴더 = 교과서 쪽 그림 · #LEC 4번째 칸 '교과서' · PAGE_LABEL·R_JB 2절 'PDF 쪽 = 책 쪽 + n' 대응표) — 이 강의는 JB 문제 뱅크 문항을 직접 가짐: 뱅크 문항마다 JB [참고] 쪽 + 교과서 해당 절을 직접 읽고 카드(교과서 순서·주제 단위 · 문항이 묻는 구조·경계·내용물·가지·지배신경 표는 RULES 5 비교표) · 쪽 칩 = PDF 쪽 · @UPD·{u:}·{e:}·25 임시본 머리 없음(SKILL D '참고 강의'·RULES 13 10-17 ESTH BOOK 꼴 참고 — 단 XREF가 아니라 문항을 직접 가짐) · 교과서 글은 원문 그대로(자체 지식 0) · F 단계가 없음 — 처음부터 RULES 6·3·4·7·9·10·5 최종형 + @TIP`
  : L.br === '안내' ? `(안내 — B2Q 대신 이 줄만 따름) JB 기출 0인 교과서 범위 강의: 정리본 대신 안내 카드 하나 — #LEC 줄 그대로 · '@MAP <강의 이름> — 교과서 범위 · JB 기출 0' · '@G ① 범위 안내' · 카드 '## Textbook scope | 교과서 범위 안내 | <첫 쪽>-<끝 쪽> | 범위' · '= ' 한 줄(JB 학습부 멘트 원문 근거 — 예 "실제 시험에는 두경부 위주로 출제"(24판 1쪽)) · '> 기출 0 — 이 범위는 교과서로' · '# 교과서 장·쪽' 아래 '-' 줄마다 장·절 제목(교과서 목차 쪽 원문) + 쪽 칩 [[${L.key}:<PDF 쪽>]] · M: 줄 없음 · annot·tables·pred 조각은 비운 채 · 검사 check_lec(자료 기준 항목 ✗는 보고에 까닭)`
  : L.br === '가'
  ? `(가) 26 있음 — LECMAP ${L.key} = 26 파일${L.aux ? ` · 25 같은 주제 = 보조 키 ${L.aux}(IMG_ALIAS ${L.aux} → ${L.key} · 25↔26 쪽 대조표 work/${s.sid}/upd26/${L.key}_cmp26.md 먼저 · 25 PPT·25 필기는 JB 기출 근거만 📜 ⭐ 줄)` : ' · 25에 같은 강의 파일 없음(25 이전에 없던 주제면 C안 `@UPD 26 새 강의 — …` · 옛 교수·옛 주제 기출은 26 근거 ⭐ 또는 ⚠ 근거 없음)'}`
  : `(나) 26 없음 — 25 임시본(LECMAP ${L.key} = 25 파일 · @UPD 첫 줄 정확히 '@UPD 25 자료 임시 — 26 수업 뒤 26 기준으로 다시(<25 파일 이름>)' · 이 강의는 F 단계가 없음 — 처음부터 RULES 6(🔑⚡)·3·4(줄바꿈)·7(빨강)·9(필기)·10(annot)·5(표) 최종형 + @TIP(guide/handoff/TIP_BRIEF.md)까지)`
const rmax = L => L.br === '가' ? 3 : ((L.br === 'nomat' || L.br === '안내') ? 1 : 2)
const cmax = L => L.br === '가' ? 2 : ((L.br === 'nomat' || L.br === '안내') ? 0 : 1)

async function subject(s) {
  const tag = (x) => `${s.sid}:${x}`
  await main(s, 'prep', 'prep', '', 'Prep')
  // ---- 작성
  const WL = s.lecs.filter(L => !L.written)   // 11-21 이미 쓴 강의(written)는 작성 건너뜀
  const wp = (L) => `${H}

과목 ${s.sid}(tools/${s.dir}/ · ${s.ko}) 강의 ${L.key} 작성. 지시문 = AGENTS.md 'B2Q 작성' 블록 + 그 안의 B2 블록(ESTH_원고_BRIEF — 경로·키는 이 과목으로 바꿔 읽음 · RULES 최종형이 이김) 그대로. 가지: ${branch(s, L)}.
지금 tools/${s.dir}/lec_${L.key}.txt = JB 단계 자리 표시(카드 하나 'Notes in progress') — 통째로 새로 씀(#LEC 키·교수·연도 칸 그대로 · 이름·파일 칸은 표지 기준으로 다듬어도 됨 · 자리 표시 카드는 없앰).
annot·tables·pred = work/${s.sid}/parts/{annot,tables,pred}_${L.key}.txt(메인이 split — 지금 비어 있음): 이 강의 문항(work/${s.sid}/review/questions.md의 '연결 강의 ${L.key}' 전부 — tier C 참고 기출 포함)마다 annot 블록을 RULES 10 꼴로 새로(머리 lec=${L.key}:<⭐ 카드 쪽> · K·A '정답 요지' = 카드 앞면(가장 최신 판) 답 기준) · 표 = RULES 5(전체정리표 sum=1 + 비교표) · 예상 = RULES 11 최종형(과목 예상 단계가 TREND로 다시 봄).
강의 메모(메인): ${L.note || '없음'}
작업 메모 work/${s.sid}/notes/${L.key}.md · 보고 work/${s.sid}/parts/R_${L.key}.md(맨 위 '줄바꿈: …' 한 줄 · 'annot·tables·pred 고칠 것'·'다른 강의 몫'·'개인 연락처 쪽'·'사용자 확인' 절).`
  const W = WL.map(L => () => agent(wp(L) + (s.v2 ? V2T : ''), s.v2 ? { label: `B2Q:${tag(L.key)}`, phase: 'Write', schema: WS } : { label: `B2Q:${tag(L.key)}`, phase: 'Write' }))
  if ((s.nomat || []).length && !s.nomat_written) W.push(() => agent(`${H}

과목 ${s.sid}(tools/${s.dir}/ · ${s.ko}) — 올해 4Q 강의·자료가 없는 키 ${s.nomat.join(' ')}(LECMAP 폴더 None · 보통 tier C 참고 기출 — RAD FRAC처럼 tier A면 ⭐가 꼭 있어야 함). 정리본은 쓰지 않고 키마다 tools/${s.dir}/lec_<KEY>.txt를 안내 카드 하나로(Q4_JB_BRIEF 2 '정리본은 쓰지 않음 — 안내 카드 하나'):
- #LEC 줄 그대로 · '@MAP <원래 주제> — 올해 4Q 강의·자료 없음 · JB 기출 n문항(참고)' · '@G ① 기출 참고' · 카드 '## Past exams only | 올해 강의 없음 — 기출로 공부 | 0 | 기출 참고 | jb=<그 키 문항 id 전부>' · '= <왜 강의가 없는지 — JB 학습부 멘트·수업 표 원문 근거 한 줄>' · '> 정리본 없음 — 기출 탭에서 JB 답·해설로 공부' · 문항마다 E: 줄(RULES 2 ⭐ 꼴 'YY·YY년 <형식> "<요지>" → <JB 답 원문>' · 근거 = JB 답·JB 해설뿐 — 강의자료 없음, 자체 지식 금지) · M: 줄 3~7(JB 답에서만 · RULES 6 라벨 꼴).
- 그 주제를 2026에 다른 쿼터에서 강의하면(PHARM4 ANX·XE = 3Q 사이트 임상치과약물치료학, OMS2 LOAD = 3Q 구강악안면외과학 1) '= ' 다음 줄 '- 2026엔 3Q 사이트 <과목> <강의>에서 공부(이 탭은 4Q JB 기출 참고)' 한 줄(내용은 옮기지 않음 · P:(💬 교수님 강조) 아님 — 11-27 QA IMPL4 H6).
- annot = work/${s.sid}/parts/annot_<KEY>.txt — 문항마다 RULES 10 꼴(v=na · K·A는 JB 답 원문 근거 · N 연도만) · tables·pred 조각은 비운 채.
검사: check_lec ${s.sid} <KEY> — 자료 기준 항목(쪽·그림·항목 수·밀도)은 자료가 없어 남을 수 있음: 남은 ✗·경고마다 보고에 까닭 · check_eyears · dump_breaks.
보고 work/${s.sid}/parts/R_NOMAT.md.`, { label: `NOMAT:${s.sid}`, phase: 'Write' }))
  const wr = await all(W, `작성 ${s.sid}`)
  if (s.v2) for (let t = 1; t <= 2; t++) {   // 11-21 작성 담당이 다 끝내지 못하고 답을 돌려준 경우(PHARM4 SED) — done=false면 이어 쓰게 다시
    const pend = WL.filter((L, i) => wr[i] && wr[i].done === false)
    if (!pend.length) break
    const rr = await all(pend.map(L => () => agent(wp(L) + V2T + `\n(이어서 ${t}회 — 앞 담당이 다 끝내지 못함: 보고·작업 메모·파일 상태를 먼저 보고 남은 것만 끝까지)`, { label: `B2Q+${t}:${tag(L.key)}`, phase: 'Write', schema: WS })), `작성 이어서 ${s.sid}`)
    pend.forEach((L, j) => { wr[WL.indexOf(L)] = rr[j] })
  }
  if (s.v2 && WL.some((L, i) => wr[i] && wr[i].done === false)) throw new Error(`작성 ${s.sid}: 덜 끝난 강의 ${WL.filter((L, i) => wr[i] && wr[i].done === false).map(L => L.key).join(' ')}`)
  log(`${s.sid} 작성 끝 ${wr.length}`)
  await main(s, 'merge', 'R1', `이번 회차 보고 = ${s.lecs.map(L => `work/${s.sid}/parts/R_${L.key}.md`).concat((s.nomat || []).length ? [`work/${s.sid}/parts/R_NOMAT.md`] : []).join(' · ')} → HANDOFF 파일 work/${s.sid}/main/HANDOFF_R1.md(검토 1회차가 읽음 — 작성 보고의 'annot·tables·pred 고칠 것'은 그 강의 1회차 담당이 직접 반영하니 옮겨 적지 않아도 됨 · '다른 강의 몫'만).`, 'Review')
  // ---- 검토 회차
  const units = s.lecs.slice().concat((s.nomat || []).length ? [{ key: 'NOMAT', br: 'nomat' }] : [])
  const last = {}, reps = {}
  units.forEach(L => { reps[L.key] = [L.key === 'NOMAT' ? `work/${s.sid}/parts/R_NOMAT.md` : `work/${s.sid}/parts/R_${L.key}.md`] })
  for (let n = 1; n <= 5; n++) {
    const todo = units.filter(L => n <= rmax(L) || (n <= rmax(L) + cmax(L) && (last[L.key] || 0) > 0))
    if (!todo.length) break
    const rs = await all(todo.map(L => () => {
      const out = L.key === 'NOMAT' ? `work/${s.sid}/parts/R2_NOMAT.md` : `work/${s.sid}/parts/R${n + 1}_${L.key}.md`
      const conf = n > rmax(L)
      const focus = L.key === 'NOMAT'
        ? `올해 강의 없는 키 ${s.nomat.join(' ')} 검토 — 안내 카드의 E:·M:·annot가 JB 답·해설 원문과 맞는지(문항마다 JB 원본 쪽 그림으로 · 자체 지식 0 · 연도·형식 · 빠진 문항 0 · '= '·P: 근거 원문) · 파일 tools/${s.dir}/lec_<KEY>.txt · work/${s.sid}/parts/annot_<KEY>.txt`
        : `과목 ${s.sid} 강의 ${L.key} 검토 ${conf ? `확인 회차(${n}회차 — 앞 회차가 고친 곳 + 같은 꼴을 강의 전체에서 · SKILL E 10-26 GERI PSY 선례)` : `${n}회차`}(독립 — 앞 담당과 다른 눈). 지시문 = AGENTS.md 'C 독립 검토' 블록 그대로(새 강의 = guide/handoff/ESTH_검토_BRIEF.md 일반 절 · 회차 초점 ${conf ? '확인' : n}회차${(L.br === '나' || L.br === '교') && n === 2 ? ' + 3회차 초점(빨강 비율·필기 쪽 강조·표·화면 id·RULES 전 절 — 25 임시본은 검토가 2회라 함께)' : ''} · '(4Q 과목 · 11-04)' 줄 · 끝내기 전 검사). 가지: ${branch(s, L)}.
고칠 파일: tools/${s.dir}/lec_${L.key}.txt · work/${s.sid}/parts/{annot,tables,pred}_${L.key}.txt.${n === 1 ? ' 1회차 = 작성 보고의 \'annot·tables·pred 고칠 것\' 반영 + 과목 출제 경향(TREND 파일이 생겼으면 그 강의 문단과 강의 틀 맞춤).' : ''}`
      return agent(`${H}

${focus}
먼저 읽기: 앞 보고 ${reps[L.key].join(' · ')} · 메인이 모은 다른 강의 몫 work/${s.sid}/main/HANDOFF_R${n}.md의 '${L.key}' 절(있으면 — 자료로 확인한 뒤 반영).
보고 ${out} — 맨 위 '새 문제 n'(새 문제 = 자료·JB와 틀린 사실 · 빠진 슬라이드 글/⭐/기출 · 잘못된 쪽 · 잘못된 표시({u:}/{e:}/{n:}/캡션)·25 전용 줄 · 줄바꿈 ✗ — 보강(덧붙임·pr 조정)은 세지 않음 · SKILL E) · '줄바꿈: …' 한 줄 · '다른 강의 몫' · '사용자 확인'.
최종 답 = schema(new_problems = 보고 맨 위 수 · summary = 5줄).`, { label: `C${n}:${tag(L.key)}`, phase: 'Review', schema: RS }).then(r => { if (r) reps[L.key].push(out); return r })
    }), `검토 ${n} ${s.sid}`)
    todo.forEach((L, i) => { last[L.key] = rs[i].new_problems })
    log(`${s.sid} 검토 ${n}회차: ${todo.map((L, i) => `${L.key} ${rs[i].new_problems}`).join(' · ')}`)
    await main(s, 'merge', `R${n + 1}`, `이번 회차 보고 = ${todo.map(L => reps[L.key][reps[L.key].length - 1]).join(' · ')} → HANDOFF 파일 work/${s.sid}/main/HANDOFF_R${n + 1}.md`, 'Review')
  }
  const left = units.filter(L => (last[L.key] || 0) > 0).map(L => `${L.key} ${last[L.key]}`)
  // ---- F (26 강의)
  const F = s.lecs.filter(L => L.br === '가')
  if (F.length) {
    await main(s, 'fprep', 'fprep', `F 담당 강의 = ${F.map(L => L.key).join(' ')}(기준본은 이 강의들 lec·parts 조각 모두).`, 'Polish')
    await all(F.map(L => () => agent(`${H}

과목 ${s.sid} 강의 ${L.key} — 지시문 = AGENTS.md 'F 한 담당' 블록 그대로(D1 → D3 → D4 → D2 → D5 → D2b → @TIP · 파일 = tools/${s.dir}/lec_${L.key}.txt + work/${s.sid}/parts/{annot,tables,pred}_${L.key}.txt(메인이 방금 merge·split · 기준본 저장함 — 다시 --save 하지 않음) · 화면 덤프 work/review_breaks2/${s.sid}_lec.md·${s.sid}_jb.md·work/review_jb/${s.sid}.md·work/review_final2/TA_${s.sid}.md(메인이 방금 만듦 — 이 강의 몫만)). 26 표시({u:}·{e:}·@UPD) 보존 · 4Q 끝내기 전 검사.
보고 work/review_final2/F_${s.sid}_${L.key}.md(단계마다 덧붙임).`, { label: `F:${tag(L.key)}`, phase: 'Polish' })), `F ${s.sid}`)
  }
  // ---- QA
  const QK = s.lecs.map(L => L.key).concat(s.nomat || [])
  await main(s, 'qaprep', 'qaprep', `qa_shots 강의 = ${s.lecs.map(L => L.key).join(' ')}.`, 'QA')
  const qa = await must(agent(`${H}

과목 ${s.sid} — 사용자 눈 QA. 지시문 = AGENTS.md 'E QA' 블록 그대로(.claude/skills/jbl-update/QA.md 점검표 전 번호 — 97~102 4Q 포함 · 끝 절 '스크린샷으로 꼭 볼 것'까지) · 대상 강의 = ${QK.join(' ')}(이번 묶음만) · 화면 기준 자료는 메인이 방금 만든 것(work/review_breaks2/${s.sid}_*.md · work/review_jb/${s.sid}.md · work/review_scan/${s.sid}.md · work/review_final2/TA_${s.sid}.md · 스크린샷 work/_tmp/qa_${s.sid}_*.png).
**메인 허락: 글자 그대로인 작은 것(구분 기호·줄 나눔·{n:}/{u:}/{e:}/{r:} 표시·라벨)은 직접 고침** — 파일 = 그 강의 tools/${s.dir}/lec_<KEY>.txt + work/${s.sid}/parts/{annot,tables,pred}_<KEY>.txt(메인이 방금 merge·split) · 고치기 전 \`tools/text_diff.py <파일> --save\`(그 파일 처음 고칠 때 한 번) · 끝에 빠진 글자 0. 낱말·사실·빠진 내용·구조 문제는 고치지 않고 보고에 강의별로(점검표 번호 · 파일:줄 · 화면 모습 → 고칠 모양 · 근거 쪽) — 메인이 그 강의 고침 담당에게 보냄. 허브·렌더러 몫은 보고만('메인 = 허브').
보고 work/review_final2/QA_${s.sid}.md. 최종 답 = schema(fix_keys = 고침 담당이 필요한 강의 키(낱말·사실·구조 문제가 남은 강의) · summary = 5줄).`, { label: `QA:${s.sid}`, phase: 'QA', schema: QS }), `QA ${s.sid}`)
  const fk = (qa.fix_keys || []).filter(k => QK.includes(k))
  if (fk.length) {
    await all(fk.map(k => () => agent(`${H}

과목 ${s.sid} 강의 ${k} — QA 고침. QA 보고 work/review_final2/QA_${s.sid}.md의 '${k}' 항목(낱말·사실·빠진 내용·구조)을 자료 쪽 이미지·JB 원본으로 하나씩 확인하고 맞는 것만 고침(아니면 보고에 까닭 — 억지로 고치지 않음). 파일 = tools/${s.dir}/lec_${k}.txt + work/${s.sid}/parts/{annot,tables,pred}_${k}.txt(QA가 직접 고친 것 위에 · 기준본 diff는 QA가 저장한 것 — 다시 --save 하지 않음). 규칙 = RULES 최종형 · 4Q 끝내기 전 검사.
보고 work/review_final2/QAFIX_${s.sid}_${k}.md(항목마다 고침/안 고침·까닭).`, { label: `QAfix:${tag(k)}`, phase: 'QA' })), `QA 고침 ${s.sid}`)
  }
  const fin = await main(s, 'merge', 'final', `이번 회차 보고 = work/review_final2/QA_${s.sid}.md${fk.length ? ' · ' + fk.map(k => `work/review_final2/QAFIX_${s.sid}_${k}.md`).join(' · ') : ''} → HANDOFF 파일 work/${s.sid}/main/HANDOFF_after.md(남은 것 — 메인이 배포 전에 봄). 마지막 단계라 split(5번)은 하지 않아도 됨.`, 'QA')
  return { sid: s.sid, lecs: QK, left_problems: left, qa: qa.summary, final: fin.summary }
}

const out = await pipeline(args.subjects, subject)
return out