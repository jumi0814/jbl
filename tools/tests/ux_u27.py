"""U27 회귀: 색 체계 — 카드 머리(.thead)의 채움 색은 과목색·흰색뿐(ANAT·GERI 전 강의), ⚡ 안내문은 강의당 1번, 그림 '슬라이드' 배지 없음,
연도·기출 칩은 흰 바탕. 채운 빨강·13px 미만 대비는 tools/audit_design.py(RED FILL · SMALL LOW CONTRAST)."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
JS = """()=>{const acc=getComputedStyle(document.documentElement).getPropertyValue('--acc').trim();const d=document.createElement('i');d.style.color=acc;document.body.appendChild(d);const A=getComputedStyle(d).color;d.remove();
const bad=new Set();document.querySelectorAll('#stage .thead, #stage .thead *').forEach(e=>{if(!e.offsetParent)return;const b=getComputedStyle(e).backgroundColor;if(b==='rgba(0, 0, 0, 0)'||b==='rgb(255, 255, 255)'||b===A)return;bad.add(e.className+':'+b);});
return {bad:[...bad].slice(0,4),tips:document.querySelectorAll('#stage .c-mem .ct small').length,fb:document.querySelectorAll('#stage .figs .fb').length,
 chips:[...document.querySelectorAll('#stage .jbchip,#stage .chip.yr')].filter(e=>e.offsetParent&&getComputedStyle(e).backgroundColor!=='rgb(255, 255, 255)').length}}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for s in ['ANAT', 'GERI', 'OMS1']:
            P = json.loads(open(J.DOCS + f'/packs/{s}.js', encoding='utf-8').read()[len('JBLHUB.register('):-2])
            for L in P['lect']:
                await pg.goto('about:blank'); await pg.goto(U + f'#/{s}/{L["k"]}/learn'); await pg.wait_for_timeout(450)
                r = await pg.evaluate(JS)
                if r['bad'] or r['tips'] > 1 or r['fb'] or r['chips']: ok(False, f'{s}/{L["k"]} {r}')
            ok(True, f'{s} 강의 {len(P["lect"])}개 — 카드 머리 채움·⚡ 안내문·슬라이드 배지·칩 바탕 검사')
        await pg.goto('about:blank'); await pg.goto(U + '#/GERI/SAL/learn'); await pg.wait_for_timeout(600)
        await pg.evaluate("document.querySelector('#t-SAL-1').scrollIntoView()"); await pg.screenshot(path=J.TMP + '/ux_u27_geri.png')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
