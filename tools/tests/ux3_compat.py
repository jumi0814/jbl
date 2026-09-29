"""ux3 묶음 P5 회귀: 옛 판(1차 7095e56 · 2차 0918775 배포본) 데이터 ↔ 새 허브 호환.
정방향 — 옛 허브로 쌓은 형식의 데이터(time·timed·tadj·timeDev·devCut·mk 채점·done·memo·exam.<S>·homeSort·sidefold·tgoal·idleMin·hlabel·tauto·lastBy)를
  옛 허브로 한 번 열어(옛 허브가 쓴 그대로를 기준선으로) 새 허브로 열면: 지난 날짜 합계 tDay·tLec = 옛 계산(2차는 옛 허브의 tDay·tLec을 직접 부름,
  1차는 time·timed 그대로) · 오늘 시계 글자 같음 · 그 키들의 저장 JSON 불변 · (ux4) 시험일·시험순은 화면에 없고 값만 보존.
역방향 — 새 허브에서 만든 tedit(시간 추가)·tseg·trest·tgoalDay·색 빈칸(c)을 옛 허브로 열면: 콘솔 오류 0 · 2차 합계 = 새 합계 − tedit 몫 ·
  색 빈칸은 옛 허브에 빈칸으로 그려짐 · 옛 허브를 거친 뒤에도 새 키·c 필드 그대로.
백업 — 새 허브 dumpAll → 빈 프로필 mergeData(기기 모드) → 지난 날짜 합계 = 보낸 기기의 (time+tadj+tedit), 두 번 합쳐도 같음.
형광펜·빈칸 위치는 legacy_restore.py --rev 7095e56(ux_all의 legacy_restore_107)이 따로 본다. 맥 1280×900. 결과 work/_tmp/ux3_compat.json"""
import os as _os, sys as _sys, json, datetime; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import legacy_base as LB
import asyncio
from playwright.async_api import async_playwright
NEWU = J.HUB_URL; fails = []; REP = {}
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
MIN = 60000
today = datetime.date.today()
D = lambda n: (today - datetime.timedelta(days=n)).isoformat()
D1, D2, D3, T0 = D(3), D(2), D(10), today.isoformat()
def old2_docs():
    d = LB.old_docs('0918775', None); ix = _os.path.join(d, 'index.html'); h = open(ix, encoding='utf-8').read()
    if 'window.__h={tDay,' not in h:   # 이 복사본(work/_legacy)에만 — 옛 합계 함수를 그대로 부르려고
        h = h.replace('window.__h={openDoc,', 'window.__h={tDay,tLec,openDoc,', 1); open(ix, 'w', encoding='utf-8').write(h)
    return d
OLD1 = 'file://' + _os.path.join(LB.old_docs('7095e56', None), 'index.html')
OLD2 = 'file://' + _os.path.join(old2_docs(), 'index.html')
BLANK = _os.path.join(J.TMP, 'ux3_compat_blank.html'); open(BLANK, 'w').write('<!doctype html><title>blank</title>')
BLANKU = 'file://' + BLANK
V1 = {'time': {D1: {'OMS1': 60 * MIN, 'CONS': 20 * MIN}, D2: {'IMPL': 30 * MIN}, D3: {'ANAT': 10 * MIN}, T0: {'CONS': 15 * MIN}},
      'timed': {D1: {'OMS1:DD1': 50 * MIN, 'OMS1:_jb': 10 * MIN, 'CONS:WHT': 20 * MIN}, D2: {'IMPL:OSS': 30 * MIN}, T0: {'CONS:WHT': 15 * MIN}},
      'tauto': False, 'memo.CONS': {'WHT': '1차 메모'},
      'mk.OMS1': {'ok': {'Q01': 1}, 'ng': {'Q02': 1}, 'bm': {'Q03': 1}, 'log': {}},
      'lastBy': {'CONS': {'s': 'CONS', 'd': 'WHT', 't': 'learn', 'at': 1}}}
V2 = dict(V1, **{'tadj': {D1: {'OMS1': -5 * MIN}, D2: {'CONS': 7 * MIN}}, 'tgoal': 300, 'idleMin': 15, 'exam.CONS': (today + datetime.timedelta(days=9)).isoformat(),
                 'homeSort': 'exam', 'sidefold': True, 'hlabel': {'y': '기출'}, 'devId': 'devA', 'devName': '맥', 'devCut': D(30),
                 'timeDev': {'devB': {'name': '아이패드', 'cut': D(30), 'time': {D1: {'CONS': 25 * MIN}}, 'timed': {D1: {'CONS:WHT': 25 * MIN}}}}})
KEEP = ['time', 'timed', 'tadj', 'timeDev', 'tauto', 'memo.CONS', 'exam.CONS', 'homeSort', 'sidefold', 'tgoal', 'idleMin', 'hlabel', 'devId', 'devCut', 'lastBy']
SEED = "S=>{localStorage.clear();for(const k in S)localStorage.setItem('jblhub.v1.'+k,JSON.stringify(S[k]))}"
SNAP = "()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.startsWith('jblhub.v1.'))o[k.slice(10)]=localStorage.getItem(k)}return o}"
SUM = lambda o: sum((o or {}).values())
async def page(ctx, errs):
    pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None); return pg
async def go(pg, u, w=2500):
    await pg.goto('about:blank'); await pg.goto(u); await pg.wait_for_timeout(w)
async def newhub(pg, h='#/'):
    await go(pg, NEWU + h, 400); await pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0", timeout=60000); await pg.wait_for_timeout(600)
async def forward(b, tag, seed, oldu):
    print(f'-- 정방향 {tag}')
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); errs_old, errs_new = [], []
    pg = await page(ctx, errs_old)
    await go(pg, BLANKU, 100); await pg.evaluate(SEED, seed)
    await go(pg, oldu + '#/'); clk_old = await pg.inner_text('#clock')
    old = None
    if tag == '2차':
        old = await pg.evaluate("D=>D.map(d=>[__h.tDay(d),__h.tLec(d)])", [D1, D2, D3])
    await go(pg, BLANKU, 200); base = await pg.evaluate(SNAP)
    ok(not errs_old, f'{tag} 옛 허브 콘솔 오류 0 {errs_old[:2]}')
    pg2 = await page(ctx, errs_new); await pg.close()
    await newhub(pg2)
    new = await pg2.evaluate("D=>D.map(d=>[__h.tDay(d),__h.tLec(d)])", [D1, D2, D3])
    clk_new = await pg2.inner_text('#clock')
    if old is None:   # 1차 = time·timed 그대로(tadj·timeDev 없음)
        tm, td = json.loads(base['time']), json.loads(base['timed'])
        old = [[tm.get(d, {}), td.get(d, {})] for d in [D1, D2, D3]]
    diff = [(d, SUM(o[0]), SUM(n[0])) for d, o, n in zip([D1, D2, D3], old, new) if SUM(o[0]) != SUM(n[0]) or o[0] != n[0]]
    ok(not diff, f'{tag} 지난 날짜 과목별 합계 tDay 같음 {[(d, SUM(o[0]) / MIN) for d, o in zip([D1, D2, D3], old)]} 차이 {diff}')
    dl = [d for d, o, n in zip([D1, D2, D3], old, new) if o[1] != n[1]]
    ok(not dl, f'{tag} 강의별 tLec 같음 {dl}')
    ok(clk_old[:5] == clk_new[:5], f'{tag} 오늘 시계 {clk_old} → {clk_new}')
    if tag == '2차':
        band = await pg2.evaluate("(document.querySelector('.hband')||{}).textContent||''")
        nav = await pg2.evaluate("(document.querySelector('#nav .nvs[data-s=CONS] .nvdd')||{}).textContent||''")
        ok('D-9' not in band and not nav, f'{tag} ux4 B1-6 시험일(exam.CONS)은 화면에 없음 — 띠·메뉴 D-n 없음 ({nav!r})')
        ok(await pg2.evaluate("__h.tDay&&typeof __h.tDay==='function'") and await pg2.evaluate("document.querySelector('[data-hsort=exam],[data-hsort2=exam]:not(:is(.nvsort *))')===null"), f'{tag} ux4 시험순 버튼 없음(homeSort 값은 아래 저장 JSON 불변 검사로)')
    await pg2.close(); pg3 = await page(ctx, errs_new); await go(pg3, BLANKU, 100); after = await pg3.evaluate(SNAP)
    ch = [k for k in KEEP if k in base and k != 'time' and k != 'timed' and after.get(k) != base[k]]
    tpast = lambda s, k: {d: v for d, v in json.loads(s.get(k, '{}')).items() if d != T0}
    ch += [k for k in ['time', 'timed'] if tpast(after, k) != tpast(base, k)]
    ok(not ch, f'{tag} 옛 키 저장 JSON 불변(지난 날짜 time·timed 포함) {ch}')
    mk0, mk1 = json.loads(base['mk.OMS1']), json.loads(after.get('mk.OMS1', '{}'))
    ok(all(set(mk0[k]) <= set(mk1.get(k, {})) for k in ['ok', 'ng', 'bm']), f'{tag} 채점 ok·ng·★ 그대로 {[(k, list(mk1.get(k, {}))) for k in ["ok", "ng", "bm"]]}')
    ok(not errs_new, f'{tag} 새 허브 콘솔 오류 0 {errs_new[:2]}')
    REP[f'forward_{tag}'] = {'old': [SUM(o[0]) / MIN for o in old], 'new': [SUM(n[0]) / MIN for n in new], 'clock': [clk_old, clk_new]}
    await pg3.close(); return ctx
async def reverse(b, ctx):
    print('-- 역방향(새 데이터 → 옛 허브) · 백업 기기 모드')
    errs = []; pg = await page(ctx, errs)
    await newhub(pg, '#/OMS1/DD1/learn'); await pg.wait_for_selector('#t-DD1-2', timeout=30000)
    # 새 허브에서 만든 새 형식: 시간 추가(tedit·tseg) · 휴식(trest) · 날짜 목표 · 색 빈칸(c:'g')
    g = await pg.evaluate(f"__h.addTime({{d:'{D2}',S:'CONS',D:'WHT',start:9*3600,min:20}})")
    await pg.evaluate(f"(()=>{{const k='jblhub.v1.';const r=JSON.parse(localStorage.getItem(k+'trest')||'{{}}');r['{D2}']=(r['{D2}']||0)+{8 * MIN};localStorage.setItem(k+'trest',JSON.stringify(r));const t=JSON.parse(localStorage.getItem(k+'tgoalDay')||'{{}}');t['{D2}']=180;localStorage.setItem(k+'tgoalDay',JSON.stringify(t))}})()")
    bw = await pg.evaluate("""()=>{const B=document.querySelector('#t-DD1-2');const s=__h.Kit.textOf(B);const m=s.match(/[가-힣]{3,}/g)||[];const w=m.find(x=>s.split(x).length===2);if(!w)return null;
      const a=s.indexOf(w),b=a+w.length,C=12;const A=JSON.parse(localStorage.getItem('jblhub.v1.ann.OMS1')||'{}');(A[B.dataset.aid]=A[B.dataset.aid]||[]).push({t:'b',x:w,i:0,p:s.slice(Math.max(0,a-C),a),s:s.slice(b,b+C),v:__h.Kit.fnv(s),c:'g'});
      localStorage.setItem('jblhub.v1.ann.OMS1',JSON.stringify(A));return [B.dataset.aid,w]}""")
    await newhub(pg, '#/OMS1/DD1/learn'); await pg.wait_for_selector('#t-DD1-2', timeout=30000); await pg.wait_for_timeout(400)
    rk = await pg.evaluate("w=>{const e=[...document.querySelectorAll('#t-DD1-2 [data-rk=b]')].find(x=>x.textContent===w);return e?[e.dataset.bc||'',e.className]:null}", bw[1])
    ok(rk and rk[0] == 'g', f'새 허브: 색 빈칸(초록) 그려짐 {bw} {rk}')
    new = await pg.evaluate("D=>D.map(d=>__h.tDay(d))", [D1, D2, D3])
    te = await pg.evaluate(f"(JSON.parse(localStorage.getItem('jblhub.v1.tedit')||'[]')).filter(e=>!e.x&&e.d==='{D2}').reduce((a,e)=>a+e.ms,0)")
    ok(te == 20 * MIN and g, f'시간 추가 20분 → tedit({te / MIN:.0f}분)')
    await go(pg, BLANKU, 150); s0 = await pg.evaluate(SNAP); dump = None
    # 옛 2차 허브
    e2 = []; p2 = await page(ctx, e2); await go(p2, OLD2 + '#/')
    o2 = await p2.evaluate("D=>D.map(d=>__h.tDay(d))", [D1, D2, D3])
    await p2.evaluate("__h.openDoc('OMS1','DD1','learn')"); await p2.wait_for_timeout(1200)
    r2 = await p2.evaluate("w=>[...document.querySelectorAll('[data-rk=b]')].some(x=>x.textContent===w)", bw[1])
    ok(not e2, f'2차 허브 — 새 데이터로 열어도 콘솔 오류 0 {e2[:2]}')
    exp = [dict(n) for n in new]; exp[1]['CONS'] = exp[1].get('CONS', 0) - te
    exp = [{k: v for k, v in e.items() if v} for e in exp]
    ok(o2 == exp, f'2차 합계 = 새 합계 − tedit 몫 (D2 새 {SUM(new[1]) / MIN:.0f}분 → 2차 {SUM(o2[1]) / MIN:.0f}분, 차 {te / MIN:.0f}분)')
    ok(r2, f'2차 허브: 색 빈칸이 빈칸으로 보임({bw[1]})')
    await p2.close()
    # 옛 1차 허브
    e1 = []; p1 = await page(ctx, e1); await go(p1, OLD1 + '#/')
    await p1.evaluate("__h.openDoc('OMS1','DD1','learn')"); await p1.wait_for_timeout(1500)
    r1 = await p1.evaluate("w=>[...document.querySelectorAll('[data-rk=b]')].some(x=>x.textContent===w)", bw[1])
    ok(not e1, f'1차 허브 — 새 데이터로 열어도 콘솔 오류 0 {e1[:2]}')
    ok(r1, f'1차 허브: 색 빈칸이 빈칸(회색)으로 보임({bw[1]})')
    await go(p1, BLANKU, 150); s1 = await p1.evaluate(SNAP); await p1.close()
    lost = [k for k in ['tedit', 'tseg', 'trest', 'tgoalDay'] if s1.get(k) != s0.get(k)]
    a0 = json.loads(s0['ann.OMS1']).get(bw[0], []); a1 = json.loads(s1.get('ann.OMS1', '{}')).get(bw[0], [])
    c_ok = any(o.get('x') == bw[1] and o.get('c') == 'g' for o in a1)
    ok(not lost and c_ok, f'옛 허브를 거친 뒤에도 새 키·빈칸 c 필드 그대로 (바뀐 키 {lost} · c {c_ok})')
    # 다시 새 허브 → 합계 그대로
    pg = await page(ctx, errs); await newhub(pg)
    back = await pg.evaluate("D=>D.map(d=>__h.tDay(d))", [D1, D2, D3])
    ok(back == new, '옛 허브를 거쳐 새 허브로 돌아와도 합계 같음')
    dump = await pg.evaluate("__h.dumpAll()")
    exp_dev = await pg.evaluate("D=>D.map(d=>{const o={};const add=(k,v)=>{if(v)o[k]=(o[k]||0)+v};const L=JSON.parse(localStorage.getItem('jblhub.v1.time')||'{}')[d]||{},A=JSON.parse(localStorage.getItem('jblhub.v1.tadj')||'{}')[d]||{};for(const k in L)add(k,L[k]);for(const k in A)add(k,A[k]);JSON.parse(localStorage.getItem('jblhub.v1.tedit')||'[]').filter(e=>!e.x&&e.d===d).forEach(e=>add(e.S,e.ms));for(const k in o)if(!(o[k]>0))delete o[k];return o})", [D1, D2, D3])
    ok(not errs, f'새 허브 콘솔 오류 0 {errs[:2]}')
    await pg.close()
    # 백업 → 다른 기기(빈 프로필) 합치기(기기 모드)
    ctx2 = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True); e3 = []; q = await page(ctx2, e3)
    await newhub(q); await q.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.tauto','false')"); await newhub(q)
    for i in range(2): await q.evaluate("d=>__h.mergeData(d,{dev:{id:'devA',name:'맥',cut:''}})", dump)
    await newhub(q)
    got = await q.evaluate("D=>D.map(d=>__h.tDay(d))", [D1, D2, D3])
    ok(got == exp_dev, f'백업 → 다른 기기(기기 모드) 합계 = 보낸 기기 time+tadj+tedit (두 번 합쳐도) {[SUM(x) / MIN for x in got]} vs {[SUM(x) / MIN for x in exp_dev]}')
    await q.evaluate("__h.openDoc('OMS1','DD1','learn')"); await q.wait_for_timeout(1500)
    rk2 = await q.evaluate("w=>{const e=[...document.querySelectorAll('#t-DD1-2 [data-rk=b]')].find(x=>x.textContent===w);return e?e.dataset.bc||'':null}", bw[1])
    ok(rk2 == 'g', f'다른 기기에서도 색 빈칸 초록 {rk2}')
    ok(not e3, f'다른 기기 콘솔 오류 0 {e3[:2]}')
    REP['reverse'] = {'new': [SUM(x) / MIN for x in new], 'old2': [SUM(x) / MIN for x in o2], 'tedit_min': te / MIN, 'dev': [SUM(x) / MIN for x in got]}
    await ctx2.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        try:
            c1 = await forward(b, '1차', V1, OLD1); await c1.close()
            c2 = await forward(b, '2차', V2, OLD2)
            await reverse(b, c2); await c2.close()
        finally:
            await b.close()
    json.dump(REP, open(_os.path.join(J.TMP, 'ux3_compat.json'), 'w'), ensure_ascii=False, indent=1)
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
