"""ux3 트랙1 묶음 L 회귀 — 표 자동 확장·열 폭.
L1 메뉴 숨김/펼침 → .msum 폭 ±248 · col 합 100% · 행 필터·묶음 필터 뒤 col 그대로 · 요약↔자세히 다시 맞춤
L2 정리표 colFit — 7강의 × 1280(숨김·펼침)·1180: 맞춘 높이 ≤ 기본값(CSS 기본 열 폭 — 기본 폭에서 칸이 넘치면 ×1.02까지) · 가로 넘침 0 · 칸 넘침(th·td scrollWidth) 0
L3 820 세로 = 2단 카드(38%|62%) — 1단 카드보다 25%↑ 낮음 · 카드 안 가로 넘침 0 · 👁 칸 이름 누르면 가림
L4 비교표 820 PHARM RX 최소 열 ≥ 90px 또는 카드형 · 1180 PHARM DS 최대 행 높이 ≤ 220px · 전체정리표 넘침은 .ovx 스크롤 안에서만
결과 표 work/_tmp/ux3l_tables.json · 스크린샷 work/_tmp/ux3i_l_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []; OUT = {}
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, wait=900):
    await pg.goto('about:blank'); await pg.goto(U + h)
    await pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .nvs')&&(location.hash.length<3||document.querySelector('#stage .msum,#stage .tblwrap,#stage .qc'))", timeout=30000); await pg.wait_for_timeout(wait)
LECS = [('CONS', 'WHT'), ('ANAT', 'LIP'), ('OMS1', 'DD1'), ('IMPL', 'OSS'), ('GERI', 'SAL'), ('PHARM', 'DS'), ('CONS', 'ADH')]
M = """(()=>{const t=document.querySelector('#stage .msum table.mtx'),w=document.querySelector('#stage .msum');const cols=[...t.querySelectorAll('colgroup>col')].map(c=>parseFloat(c.style.width)||0);
 return {H:Math.round(t.getBoundingClientRect().height),W:Math.round(w.getBoundingClientRect().width),disp:getComputedStyle(t).display,cfw:t.dataset.cfw||'',sum:cols.reduce((a,b)=>a+b,0),
  over:document.documentElement.scrollWidth-innerWidth,cov:[...t.querySelectorAll('tbody tr:not(.grow)>th,tbody tr:not(.grow)>td')].filter(c=>c.scrollWidth>c.clientWidth+1).length,tover:Math.round(t.getBoundingClientRect().width-t.closest('.tscroll').clientWidth)}})()"""
DEF = "(()=>{const t=document.querySelector('#stage .msum table.mtx');const k=t.dataset.cfw;__h.cfApply(t,null);const h=Math.round(t.getBoundingClientRect().height);window.__dcov=[...t.querySelectorAll('tbody tr:not(.grow)>th,tbody tr:not(.grow)>td')].filter(c=>c.scrollWidth>c.clientWidth+1).length;__h.cfApply(t,k?k.split(',').map(Number):null);return h})()"
async def dflt(pg):   # 기본 열 폭 높이 · 기본 폭에서 칸 넘침이 있으면(주제 열 < 영문 낱말) 하한을 지킨 colFit이 기본보다 2%까지 높아도 됨
    d = await pg.evaluate(DEF); dc = await pg.evaluate("window.__dcov"); return d, dc
def le(r, d, dc): return r['cov'] == 0 and (r['H'] <= d or (dc > 0 and r['H'] <= d * 1.02))
async def run(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    # ---- L2 1280 숨김(정리표 자동 숨김) · 펼침
    for s, k in LECS:
        await open_(pg, f'#/{s}/{k}/sum', 1200); r = await pg.evaluate(M); d, dc = await dflt(pg)
        OUT[f'1280fold {s}/{k}'] = dict(r, default=d)
        ok(r['disp'] == 'table' and le(r, d, dc) and (not r['cfw'] or abs(r['sum'] - 100) < 0.6) and r['over'] <= 0 and r['tover'] <= 1, f'1280 숨김 {s}/{k} 높이 {r["H"]} ≤ 기본 {d}{"(넘침 " + str(dc) + ")" if dc else ""} 칸넘침 {r["cov"]} ({round((1 - r["H"] / d) * 100, 1)}%↓) 열 {r["cfw"]} 폭 {r["W"]}')
    await open_(pg, '#/CONS/WHT/sum', 1200); r0 = await pg.evaluate(M)
    await pg.evaluate("window.__lev=0;document.addEventListener('jbl:layout',()=>__lev++)")
    await pg.click('#sideopen'); await pg.wait_for_timeout(250); w250 = await pg.evaluate("Math.round(document.querySelector('#stage .msum').getBoundingClientRect().width)"); await pg.wait_for_timeout(500); r1 = await pg.evaluate(M)
    ok(abs((r0['W'] - w250) - 248) <= 10 and abs(r1['sum'] - 100) < 0.6 and r1['disp'] == 'table', f'L1 › 펼침 → 250ms 안에 .msum {r0["W"]} → {w250} · 열 {r1["cfw"]} 합 {r1["sum"]}')
    await pg.keyboard.press('Backslash'); await pg.wait_for_timeout(700); r2 = await pg.evaluate(M)
    ok(r2['W'] == r0['W'] and r2['cfw'] == r0['cfw'], f'L1 \\ 다시 숨김 → 폭·열 처음과 같음 {r2["W"]} {r2["cfw"]}')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.sidefold');localStorage.setItem('jblhub.v1.wideSide','1')")
    for s, k in LECS:
        await open_(pg, f'#/{s}/{k}/sum', 1200); r = await pg.evaluate(M); d, dc = await dflt(pg)
        OUT[f'1280open {s}/{k}'] = dict(r, default=d)
        ok(le(r, d, dc) and r['over'] <= 0 and r['tover'] <= 1, f'1280 펼침 {s}/{k} {r["disp"]} 높이 {r["H"]} ≤ 기본 {d}{"(넘침 " + str(dc) + ")" if dc else ""} 칸넘침 {r["cov"]} 열 {r["cfw"]} 폭 {r["W"]}')
    await pg.screenshot(path=J.TMP + '/ux3i_l_1280_open.png')
    # 필터 뒤 col 그대로 · 요약↔자세히 다시 맞춤
    await open_(pg, '#/CONS/WHT/sum', 1200); c0 = (await pg.evaluate(M))['cfw']
    for sel in ['[data-mfilt="hit"]', '[data-mfilt="rep2"]', '[data-mfilt=""]']:
        await pg.click('#msbar ' + sel); await pg.wait_for_timeout(350)
    await pg.click('#msbar [data-mgrp]:not([data-mgrp=""])'); await pg.wait_for_timeout(350); await pg.click('#msbar [data-mgrp=""]'); await pg.wait_for_timeout(350)
    c1 = (await pg.evaluate(M))['cfw']; ok(c1 == c0, f'L1 행 필터·묶음 필터 뒤 열 폭 그대로 {c0} → {c1}')
    n0 = await pg.evaluate("__h.CF.n"); await pg.click('#msbar [data-mdense="f"]'); await pg.wait_for_timeout(700); rf = await pg.evaluate(M); df, dfc = await dflt(pg); n1 = await pg.evaluate("__h.CF.n")
    ok(n1 == n0 + 1 and le(rf, df, dfc), f'L1 자세히 → 다시 맞춤({n1 - n0}회) {rf["cfw"]} 높이 {rf["H"]} ≤ {df}')
    OUT['1280 full CONS/WHT'] = dict(rf, default=df)
    await pg.click('#msbar [data-mdense="s"]'); await pg.wait_for_timeout(500)
    ok(not errs, f'오류 0 {errs[:2]}'); await ctx.close()
    # ---- 1180 가로
    ctx = await b.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True); pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    for s, k in LECS[:4]:
        await open_(pg, f'#/{s}/{k}/sum', 1200); r = await pg.evaluate(M); d, dc = await dflt(pg)
        OUT[f'1180 {s}/{k}'] = dict(r, default=d)
        ok(le(r, d, dc) and r['over'] <= 0, f'1180 {s}/{k} {r["disp"]} 높이 {r["H"]} ≤ {d}{"(넘침 " + str(dc) + ")" if dc else ""} 칸넘침 {r["cov"]} 열 {r["cfw"]}')
    await pg.screenshot(path=J.TMP + '/ux3i_l_1180_sum.png')
    await open_(pg, '#/PHARM/DS/tbl', 1200)
    mh = await pg.evaluate("Math.max(...[...document.querySelectorAll('#stage table.cmp tbody tr')].map(r=>r.getBoundingClientRect().height))")
    OUT['1180 PHARM/DS tbl maxrow'] = mh
    ok(mh <= 220, f'L4 1180 PHARM DS 비교표 최대 행 높이 {round(mh)} ≤ 220')
    await pg.screenshot(path=J.TMP + '/ux3i_l_1180_pharm_ds.png'); await ctx.close()
    # ---- 820 세로: 2단 카드 · 비교표
    ctx = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True); pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    ONE = "(()=>{let s=document.getElementById('__one');if(!s){s=document.createElement('style');s.id='__one';s.textContent='.msum table.mtx tbody tr:not(.grow)>*{float:none!important;margin-left:0!important;width:auto!important;border-left:0!important;padding-left:0!important}';document.head.appendChild(s);}else s.remove();return Math.round(document.querySelector('#stage .msum table.mtx').getBoundingClientRect().height)})()"
    for s, k in LECS[:4]:
        await open_(pg, f'#/{s}/{k}/sum', 1200)
        r = await pg.evaluate("(()=>{const t=document.querySelector('#stage .msum table.mtx'),tr=t.querySelector('tbody tr:not(.grow)');const th=tr.querySelector('th'),md=tr.querySelector('td.md');let ov=0;t.querySelectorAll('tbody tr:not(.grow)').forEach(r=>{if(r.scrollWidth>r.clientWidth+1)ov++;});return {H:Math.round(t.getBoundingClientRect().height),disp:getComputedStyle(tr).display,fl:getComputedStyle(th).float,thw:Math.round(th.getBoundingClientRect().width/tr.getBoundingClientRect().width*100),mdl:Math.round(md.getBoundingClientRect().left-tr.getBoundingClientRect().left),ov}})()")
        h1 = await pg.evaluate(ONE); await pg.evaluate(ONE)
        OUT[f'820 {s}/{k}'] = dict(r, one=h1)
        ok(r['disp'] == 'flow-root' and r['fl'] == 'left' and 34 <= r['thw'] <= 40 and r['ov'] == 0 and r['H'] <= h1 * 0.75, f'L3 820 {s}/{k} 2단 카드 {r["H"]} ≤ 1단 {h1}×0.75 ({round((1 - r["H"] / h1) * 100)}%↓) 주제 폭 {r["thw"]}% 넘침 {r["ov"]}')
        if k == 'WHT': await pg.screenshot(path=J.TMP + '/ux3i_l_820_card2.png')
    # 👁 칸 이름 = 그 칸 가리기
    await open_(pg, '#/CONS/WHT/sum', 1200)
    await pg.evaluate("(()=>{const td=document.querySelector('#stage .msum tbody tr:not(.grow) td.mnote');td.scrollIntoView({block:'center'});})()"); await pg.wait_for_timeout(300)
    xy = await pg.evaluate("(()=>{const r=document.querySelector('#stage .msum tbody tr:not(.grow) td.mnote').getBoundingClientRect();return [r.left+20,r.top+12]})()")
    await pg.touchscreen.tap(xy[0], xy[1]); await pg.wait_for_timeout(400)
    ok(await pg.evaluate("document.querySelectorAll('#stage .msum td.cov[data-col=mem]').length>3"), 'L3 820 칸 이름(⚡ 암기 👁) 누르면 모든 주제에서 가림')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.cover.CONS.WHT/sum')")
    # L4 820 PHARM RX 비교표
    await open_(pg, '#/PHARM/RX/tbl', 1200)
    rx = await pg.evaluate("[...document.querySelectorAll('#stage .tblwrap')].map(w=>{const t=w.querySelector('table');if(!t)return null;const card=w.classList.contains('stcard');const c=[...t.querySelectorAll('colgroup>col')].map(x=>x.getBoundingClientRect().width).filter(x=>x>0);const r=t.tBodies[0]&&t.tBodies[0].rows[0];const cw=r?[...r.cells].map(x=>x.getBoundingClientRect().width):[];return {card,min:Math.round(Math.min(...(cw.length?cw:[999]))),n:cw.length}}).filter(Boolean)")
    OUT['820 PHARM/RX tbl'] = rx
    ok(all(x['card'] or x['min'] >= 90 for x in rx), f'L4 820 PHARM RX 비교표 최소 열 ≥ 90px 또는 카드형 {rx}')
    await pg.screenshot(path=J.TMP + '/ux3i_l_820_pharm_rx.png')
    # 전체정리표 넘침은 .ovx 안에서만(모든 과목 · 820)
    bad = []; nst = 0
    for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
        for k in (await pg.evaluate(f"__h.PACKS.{s}.lect.filter(L=>(L.sumt||[]).length).map(L=>L.k)")):
            await open_(pg, f'#/{s}/{k}/sum', 600); await pg.evaluate("document.querySelector('#sumtop [data-sttab=all]')&&document.querySelector('#sumtop [data-sttab=all]').click()"); await pg.wait_for_timeout(400)
            r = await pg.evaluate("[...document.querySelectorAll('#sumtop .tblwrap.stbl:not(.stoff)')].map(w=>{const x=w.querySelector('.tscroll')||w,t=w.querySelector('table');return {ovx:x.classList.contains('ovx'),card:w.classList.contains('stcard'),o:t.getBoundingClientRect().width-x.clientWidth,pg:document.documentElement.scrollWidth-innerWidth}})")
            nst += len(r)
            for x in r:
                if x['pg'] > 0 or (x['o'] > 2 and not x['ovx']): bad.append((s, k, x))
            await pg.evaluate("localStorage.removeItem('jblhub.v1.sumtop.'+__h.CUR.s+'.'+__h.CUR.d)")
    ok(not bad and nst >= 20, f'L4 820 전체정리표 {nst}개 — 넘침은 .ovx 안에서만 {bad[:3]}')
    ok(not errs, f'오류 0 {errs[:2]}'); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); await run(b); await b.close()
    json.dump(OUT, open(J.TMP + '/ux3l_tables.json', 'w'), ensure_ascii=False, indent=1)
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
