"""ux3 묶음 I5·I7 회귀: tedit 편집 원장 — add/del/undo 뒤 time·timed·tadj 바이트 동일·합계 기대값 · 옛 tadj가 있는 날 합계 = time+tadj+tedit ·
통계 탭 '시간 고치기'·옛 tadj ✕ = tedit 상쇄(옛 값 그대로) · 합치기 회귀('구간 삭제(tedit −30분) 뒤 삭제 전 백업 합치기 → 삭제 반영 그대로', '빼기 뒤 옛 백업 합치기', 두 번 합쳐도 같음) ·
다른 기기 백업 = tseg·trest는 timeDev[id]로(달력에 💻 읽기 전용), tedit는 로컬 원장에 한 번만 · 되돌리기·교체(studyPlan)도 tedit 합집합 · tstate는 합치지 않음.
가짜 시계 2026-09-29(화) 10:00 · 맥 1280×900"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
NOW = datetime.datetime(2026, 9, 29, 10, 0, 0)
D1, D2, D3 = '2026-09-28', '2026-09-27', '2026-09-20'; MIN = 60000
async def ls(pg, k):
    v = await pg.evaluate(f"localStorage.getItem('jblhub.v1.{k}')"); return json.loads(v) if v else None
async def raw(pg, k): return await pg.evaluate(f"localStorage.getItem('jblhub.v1.{k}')")
async def boot(pg, h, ms=1500):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.clock.run_for(ms)
async def sub(pg, d, s): return await pg.evaluate(f"__h.tDay('{d}')['{s}']||0")
async def tot(pg, d): return await pg.evaluate(f"(o=>Object.values(o).reduce((a,b)=>a+b,0))(__h.tDay('{d}'))")
SEED = {'time': {D1: {'CONS': 40 * MIN, 'OMS1': 20 * MIN}, D2: {'CONS': 10 * MIN}, D3: {'ANAT': 30 * MIN}},
        'timed': {D1: {'CONS:WHT': 40 * MIN}},
        'tadj': {D3: {'ANAT': -10 * MIN}, D2: {'CONS': 15 * MIN}},
        'tseg': {D1: [[9 * 3600, 9 * 3600 + 1800, 'CONS', 'WHT', 'a'], [11 * 3600, 11 * 3600 + 600, 'CONS', 'WHT', 'a'], [20 * 3600, 20 * 3600 + 1200, 'OMS1', '', 'a']]}}
async def seed(pg):
    await boot(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    await pg.evaluate("S=>{for(const k in S)localStorage.setItem('jblhub.v1.'+k,JSON.stringify(S[k]));localStorage.setItem('jblhub.v1.tauto','false')}", SEED)
    await boot(pg, '#/')

async def part(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== I5 tedit')
    await pg.clock.install(time=NOW)
    await seed(pg)
    R0 = {k: await raw(pg, k) for k in ('time', 'timed', 'tadj')}
    ok(await tot(pg, D3) == 20 * MIN and await tot(pg, D2) == 25 * MIN, f'옛 tadj 합계 = time + tadj ({await tot(pg, D3) / MIN:.0f}·{await tot(pg, D2) / MIN:.0f}분)')
    # add 60 → +3600000
    c0 = await sub(pg, D2, 'CONS')
    g = await pg.evaluate(f"__h.addTime({{d:'{D2}',S:'CONS',D:'WHT',start:8*3600,min:60}})")
    ok(await sub(pg, D2, 'CONS') - c0 == 3600000, f'addTime 60분 → tDay 보존 +{(await sub(pg, D2, "CONS") - c0) / MIN:.0f}분')
    ok(await pg.evaluate(f"__h.tLec('{D2}')['CONS:WHT']") == 60 * MIN, 'tLec 강의 +60분(tedit D 항목)')
    ok(all([await raw(pg, k) == R0[k] for k in R0]), 'time·timed·tadj JSON 바이트 그대로')
    ok(await tot(pg, D2) == 10 * MIN + 15 * MIN + 60 * MIN, f'옛 tadj가 있는 날 합계 = time+tadj+tedit ({await tot(pg, D2) / MIN:.0f}분)')
    e = (await ls(pg, 'tedit'))[-1]; ok(list(e.keys())[:9] == ['i', 'at', 'd', 'S', 'D', 'ms', 'k', 'g', 'x'] and len(e['i']) == 8 and e['k'] == 'add' and e['g'] == [28800, 32400], f'tedit 항목 형식 {list(e.keys())}')
    # del (달력 🗑) → 원래대로 · undo → 다시 +60
    await boot(pg, '#/_cal/' + D2)
    i8 = await pg.evaluate("__h.dayRows('%s').findIndex(r=>r.s===8*3600)" % D2)
    gd = await pg.evaluate(f"__h.delSeg('{D2}',{i8})"); await pg.clock.run_for(200)
    ok(await sub(pg, D2, 'CONS') == c0, f'🗑 → 원래대로 ({await sub(pg, D2, "CONS") / MIN:.0f}분)')
    ok(await pg.evaluate(f"__h.undoEdit('{gd}')") >= 1 and await sub(pg, D2, 'CONS') - c0 == 3600000, 'del 되돌리기 → 다시 +60분')
    ok(all([await raw(pg, k) == R0[k] for k in R0]), 'time·timed·tadj 바이트 그대로(del·undo 뒤)')
    ok(await pg.evaluate(f"__h.undoEdit('{g}')") == 1 and await sub(pg, D2, 'CONS') == c0 and await pg.evaluate("__h.dayRows('%s').length" % D2) == 0, 'add 되돌리기 → 원래대로 · 구간도 숨김')
    # 통계 '시간 고치기' −30(빼기) → tedit · tadj 그대로 · 옛 tadj ✕ = 상쇄
    await boot(pg, '#/_time')
    await pg.evaluate("document.querySelector('#home details.tvadj').open=true")
    await pg.fill('#tvad', D1); await pg.select_option('#tvas', 'CONS'); await pg.fill('#tvam', '30')
    bak_before = await pg.evaluate("JSON.stringify(__h.dumpAll())")
    await pg.evaluate("document.querySelector('#home [data-tvadj=\"-1\"]').click()"); await pg.clock.run_for(200)
    ok(await sub(pg, D1, 'CONS') == 10 * MIN and await raw(pg, 'tadj') == R0['tadj'], f'시간 고치기 −30분 → 보존 {await sub(pg, D1, "CONS") / MIN:.0f}분 · tadj 그대로')
    await pg.evaluate(f"document.querySelector('#home [data-tvadx=\"{D3}|ANAT\"]').click()"); await pg.clock.run_for(200)
    ok(await tot(pg, D3) == 30 * MIN and await raw(pg, 'tadj') == R0['tadj'], f'옛 tadj ✕ → 상쇄(합계 {await tot(pg, D3) / MIN:.0f}분) · 옛 값 그대로')
    ok('취소함' in await pg.inner_text('#home .tehist'), "고친 기록에 '취소함'")
    # 합치기 회귀: 빼기 뒤 옛 백업 합치기 → 빼기 그대로 · 두 번 합쳐도 같음
    for i in range(2):
        await pg.evaluate("d=>__h.mergeData(JSON.parse(d))", bak_before)
        ok(await sub(pg, D1, 'CONS') == 10 * MIN and await tot(pg, D3) == 30 * MIN, f'빼기 뒤 옛 백업 합치기 {i + 1}번 → 보존 {await sub(pg, D1, "CONS") / MIN:.0f}분 그대로')
    # 구간 삭제(tedit −30분) 뒤 삭제 전 백업 합치기
    await boot(pg, '#/_cal/' + D1)
    bak2 = await pg.evaluate("JSON.stringify(__h.dumpAll())"); t0 = await tot(pg, D1)
    i9 = await pg.evaluate("__h.dayRows('%s').findIndex(r=>r.s===20*3600)" % D1)   # 구강외과1 20:00–20:20
    await pg.evaluate(f"__h.delSeg('{D1}',{i9})"); await pg.clock.run_for(200)
    t1 = await tot(pg, D1); ok(t0 - t1 == 20 * MIN, f'구간 삭제 → −{(t0 - t1) / MIN:.0f}분')
    for i in range(2):
        await pg.evaluate("d=>__h.mergeData(JSON.parse(d))", bak2)
        ok(await tot(pg, D1) == t1, f'삭제 전 백업 합치기 {i + 1}번 → 합계 삭제 반영 그대로 ({await tot(pg, D1) / MIN:.0f}분)')
    await boot(pg, '#/_cal/' + D1)
    ok(not any(r['s'] == 20 * 3600 for r in await pg.evaluate("__h.dayRows('%s')" % D1)), '합친 뒤에도 지운 구간(x가 이김) 숨김')
    # 다른 기기의 삭제·추가가 들어오면(백업의 tedit) 한 번만
    other = json.loads(bak2); oe = json.loads(other.get('jblhub.v1.tedit', '[]'))
    oe.append({'i': 'zzzz0001', 'at': 1, 'd': D3, 'S': 'ANAT', 'D': '', 'ms': 5 * MIN, 'k': 'add', 'g': None, 'x': 0})
    other['jblhub.v1.tedit'] = json.dumps(oe); other['jblhub.v1.tstate'] = json.dumps({'st': 'sess', 't0': 1, 'seg': 1, 'S': 'OMS1', 'D': '', 'at': 1, 'd': D1, 'own': 'x', 'li': 1, 'sum': 0, 'rsum': 0})
    a3 = await tot(pg, D3)
    for i in range(2): await pg.evaluate("d=>__h.mergeData(d)", other)
    ok(await tot(pg, D3) - a3 == 5 * MIN, f'백업의 새 tedit 항목 → 두 번 합쳐도 +5분 한 번 ({(await tot(pg, D3) - a3) / MIN:.0f})')
    ok(await ls(pg, 'tstate') is None, 'tstate는 합치지 않음(기기 전용)')
    # 다른 기기(dev) 백업: tseg·trest는 timeDev[id]로, tedit는 로컬 원장
    dv = {'jblhub.v1.time': json.dumps({D1: {'PHARM': 25 * MIN}}), 'jblhub.v1.tseg': json.dumps({D1: [[15 * 3600, 15 * 3600 + 1500, 'PHARM', '', 'a']]}),
          'jblhub.v1.trest': json.dumps({D1: 7 * MIN}), 'jblhub.v1.tedit': json.dumps([{'i': 'dev00001', 'at': 2, 'd': D1, 'S': 'PHARM', 'D': '', 'ms': 10 * MIN, 'k': 'add', 'g': None, 'x': 0}])}
    p0 = await sub(pg, D1, 'PHARM')
    for i in range(2): await pg.evaluate("d=>__h.mergeData(d,{dev:{id:'devB',name:'아이패드',cut:''}})", dv)
    td = await ls(pg, 'timeDev'); e = td.get('devB', {})
    ok(e.get('tseg', {}).get(D1) and e.get('trest', {}).get(D1) == 7 * MIN, f"기기 백업 → timeDev.devB에 tseg·trest {list(e)}")
    ok(await ls(pg, 'tseg') and not any(q[2] == 'PHARM' for q in (await ls(pg, 'tseg')).get(D1, [])), '이 기기 tseg에는 섞지 않음')
    await boot(pg, '#/_cal/' + D1)
    ok(await sub(pg, D1, 'PHARM') - p0 == 35 * MIN, f'기기 시간 25 + tedit 10 = +{(await sub(pg, D1, "PHARM") - p0) / MIN:.0f}분(두 번 합쳐도 한 번)')
    rows = await pg.evaluate("[...document.querySelectorAll('#calday .crow.dv')].map(r=>r.textContent)")
    ok(len(rows) == 1 and '💻' in rows[0] and '아이패드' in rows[0] and await pg.evaluate("document.querySelectorAll('#calday .crow.dv [data-crd]').length") == 0, f'💻 다른 기기 구간 = 읽기 전용 줄 {rows}')
    ok(await pg.evaluate("document.querySelectorAll('#calday .cbk.dv').length") == 1, '24시간 띠에 기기 구간(점선)')
    # 되돌리기·교체(studyPlan) — tedit 합집합
    P = await pg.evaluate("d=>{const p=__h.studyPlan(d,null);return Object.keys(p.set)}", {'jblhub.v1.tedit': json.dumps([{'i': 'plan0001', 'at': 3, 'd': D3, 'S': 'ANAT', 'D': '', 'ms': MIN, 'k': 'set', 'g': None, 'x': 0}])})
    ok('jblhub.v1.tedit' in P, f'studyPlan(교체·되돌리기)도 tedit 합집합 {P}')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await part(b)
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
