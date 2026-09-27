"""U25 회귀: 정리표·비교표 판형 — 820에서 정리표(table.mtx)는 카드형(머리 숨김·칸 라벨), 비교표 최소 열 ≥ 80px 또는 가로 스크롤·페이지 가로 넘침 0,
1280 정리표 2500px 스크롤 후 머리(thead)가 탭 바로 아래, 세부 칸 6개 초과는 '+N 더 보기(카드로)'(조용한 누락 0), 'Osseointegration' 단어 중간 끊김 없음."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=800):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
WORD = """(w)=>{const out=[];const tw=document.createTreeWalker(document.querySelector('#stage'),NodeFilter.SHOW_TEXT);let n;while(n=tw.nextNode()){let i=n.nodeValue.indexOf(w);while(i>=0){if(n.parentElement.offsetParent){const r=document.createRange();r.setStart(n,i);r.setEnd(n,i+w.length);const rs=[...r.getClientRects()].filter(x=>x.width>0);const tops=new Set(rs.map(x=>Math.round(x.top)));out.push(tops.size);}i=n.nodeValue.indexOf(w,i+1);}}return out;}"""
async def main():
    for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
        P = (lambda t__: json.loads(t__[t__.index('JBLHUB.register(')+16:-2]))(open(J.DOCS + f'/packs/{s}.js', encoding='utf-8').read())
        bad = sum(1 for L in P['lect'] for blk in re.findall(r'<div class="mblk">(.*?)</div>(?=<div class="mblk">|</td>)', L['sum'], flags=re.S) if blk.count('<div class=ci>') > 6)
        n2 = sum(L['sum'].count('more2') for L in P['lect'])
        ok(bad == 0, f'{s} 정리표 세부 칸 7개↑ 그대로 둔 블록 0 · 더 보기 버튼 {n2}')
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
            await open_(pg, f'#/{s}/_tbl')
            r = await pg.evaluate("""()=>({page:document.documentElement.scrollWidth>innerWidth+1,bad:[...document.querySelectorAll('#stage .tblwrap')].filter(w=>{const t=w.querySelector('.tscroll');const mn=Math.min(...[...w.querySelectorAll('thead th')].map(th=>th.getBoundingClientRect().width));return mn<80&&!(t.scrollWidth>t.clientWidth+2);}).length})""")
            ok(not r['page'] and not r['bad'], f'{s} 820 비교표: 페이지 가로 넘침 {r["page"]} · 좁은 열(스크롤 없음) {r["bad"]}')
        await open_(pg, '#/IMPL/OSS/sum')
        r = await pg.evaluate("""()=>{const t=document.querySelector('table.mtx');const td=t.querySelector('tbody td[data-h]');return {thead:getComputedStyle(t.querySelector('thead')).display,label:getComputedStyle(td,'::before').content,page:document.documentElement.scrollWidth>innerWidth+1}}""")
        ok(r['thead'] == 'none' and '요지' in r['label'] and not r['page'], f'820 정리표 카드형 {r}')
        await pg.screenshot(path=J.TMP + '/ux_u25_sum_820.png')
        ws = []
        for h in ['#/IMPL/_tbl', '#/IMPL/OSS/sum', '#/IMPL/OSS/learn', '#/IMPL/_sum']:
            await open_(pg, h); ws += await pg.evaluate(WORD, 'Osseointegration')
        ok(ws and max(ws) == 1, f"'Osseointegration' {len(ws)}곳 모두 한 줄 (줄 수 {sorted(set(ws))})")
        ctx2 = await b.new_context(viewport={'width': 1280, 'height': 900}); pg2 = await ctx2.new_page()
        await open_(pg2, '#/OMS1/DD1/sum', 1000); await pg2.evaluate('window.scrollTo(0,2500)'); await pg2.wait_for_timeout(400)
        g = await pg2.evaluate("(()=>{const th=document.querySelector('table.mtx thead th').getBoundingClientRect();const d=document.querySelector('#dtabs').getBoundingClientRect();return [Math.round(th.top),Math.round(d.bottom)]})()")
        ok(abs(g[0] - g[1]) <= 2, f'1280 정리표 2500px 스크롤 후 머리 top {g[0]} = 탭 아래 {g[1]}')
        await pg2.screenshot(path=J.TMP + '/ux_u25_sum_1280.png')
        await open_(pg2, '#/OMS1/DD1/sum'); n = await pg2.evaluate("document.querySelectorAll('#stage .more2').length")
        if n:
            await pg2.click('#stage .more2'); await pg2.wait_for_timeout(800)
            ok(await pg2.evaluate("location.hash.includes('/learn')"), '+N 더 보기(카드로) → 학습 탭 카드')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
