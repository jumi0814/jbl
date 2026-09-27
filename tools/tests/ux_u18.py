"""U18 회귀: 대조·주변부 자동 구조화 — ANAT Q02 대조 첫 항목이 점 목록, .ab.chk·.ab.more 230자 덩어리 0(전 과목, audit_design의 CHK와 같음),
인용 칩은 .cites 줄. annot 글자 불변은 tools/tests/annot_text.py. 스크린샷 work/_tmp/ux_u18_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
src = open(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), 'audit_design.py'), encoding='utf-8').read()
CHK = src[src.index('CHK=r"""') + 8:src.index('"""', src.index('CHK=r"""') + 8)]
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
        await pg.goto('about:blank'); await pg.goto(U + f'#/{s}/_jb/_jb'); await pg.wait_for_timeout(1400)
        r = await pg.evaluate(CHK); ok(r['n'] == 0, f"{s}: .ab.chk·.ab.more 230자 덩어리 {r['n']}/{r['all']} {r['longs'][:2]}")
    await pg.goto('about:blank'); await pg.goto(U + '#/ANAT/_jb/_jb'); await pg.wait_for_timeout(1400)
    r = await pg.evaluate("(()=>{const li=document.querySelector('#c-Q02 .ab.chk>ul>li');return {ul:!!li.querySelector('ul.klist'),n:Math.max(0,...[...li.querySelectorAll('ul.klist')].map(u=>u.children.length)),cites:li.querySelectorAll(':scope>.cites .cite').length}})()")
    ok(r['ul'] and r['n'] >= 2 and r['cites'] >= 1, f'ANAT Q02 대조 첫 항목 = 점 목록(인용 속 \' / \' 나열 → 항목 2개↑ — 항목 수는 원고 따라) {r}')
    for s, q in [('ANAT', 'Q02'), ('GERI', 'J01'), ('IMPL', 'Q13'), ('PHARM', 'DS25')]:
        await pg.goto('about:blank'); await pg.goto(U + f'#/{s}/_jb/_jb'); await pg.wait_for_timeout(1300)
        await pg.evaluate(f"(()=>{{const c=document.querySelector('#c-{q}');c.classList.add('open');const e=c.querySelector('.ab.chk');const cs=getComputedStyle(document.documentElement);scrollTo(0,e.getBoundingClientRect().top+scrollY-parseFloat(cs.getPropertyValue('--toph'))-parseFloat(cs.getPropertyValue('--tabh'))-20)}})()")
        await pg.wait_for_timeout(300); await pg.screenshot(path=J.TMP + f'/ux_u18_{s}_{q}_{tag}.png')
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), '가로 넘침 없음')
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 820, 'height': 1180}, True, 'ipad')
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
