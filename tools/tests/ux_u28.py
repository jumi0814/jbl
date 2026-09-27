"""U28 회귀: 플래시카드 — 빈칸 3개↑ 카드에서 첫 빈칸을 누르면 그것만 열림(카드는 앞면), 카드 다른 곳 = 뒤집기,
몰라요 2장 → 새로고침 → '몰라요만' = 2장, 820 터치 스와이프로 넘김, 탭을 옮겼다 와도 위치 유지, 암기 줄 ' / '는 줄(li)로."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1000):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
        await open_(pg, '#/OMS1/DD1/flash')
        # 빈칸 3개 이상인 카드 찾기
        n = 0
        for _ in range(80):
            n = await pg.evaluate("document.querySelectorAll('#fcard .fcb').length")
            if n >= 3: break
            await pg.evaluate("document.querySelector('#fnext').click()")
        ok(n >= 3, f'빈칸 {n}개 카드')
        await pg.evaluate("document.querySelector('#fcard .fcb').click()"); await pg.wait_for_timeout(150)
        r = await pg.evaluate("[document.querySelectorAll('#fcard .fcb.show').length, document.querySelector('#fcard').classList.contains('back')]")
        ok(r == [1, False], f'첫 빈칸만 열림 {r}')
        await pg.evaluate("document.querySelector('#fcard .side').click()"); await pg.wait_for_timeout(150)
        ok(await pg.evaluate("document.querySelector('#fcard').classList.contains('back')"), '카드 다른 곳 → 뒤집기')
        ok(await pg.evaluate("document.querySelectorAll('#fc ul.fcl li').length>=1"), '암기 줄 li')
        # 몰라요 2장
        await open_(pg, '#/OMS1/DD1/flash')
        k1 = await pg.evaluate("document.querySelector('.fcpos').textContent")
        await pg.click('#fx'); await pg.wait_for_timeout(150); await pg.click('#fx'); await pg.wait_for_timeout(150)
        await open_(pg, '#/OMS1/DD1/flash'); await pg.click('[data-fst="x"]'); await pg.wait_for_timeout(200)
        t = await pg.inner_text('.fcpos')
        ok(t.strip().endswith('/ 2'), f'몰라요 2 → 새로고침 → 몰라요만 ({t})')
        await pg.click('[data-fst="x"]'); await pg.wait_for_timeout(150)
        # 스와이프
        p0 = await pg.inner_text('.fcpos')
        box = await pg.evaluate("(()=>{const r=document.querySelector('#fcard').getBoundingClientRect();return [r.left+r.width*0.8,r.top+r.height/2]})()")
        cdp = await ctx.new_cdp_session(pg)
        async def touch(t, x, y): await cdp.send('Input.dispatchTouchEvent', {'type': t, 'touchPoints': [{'x': x, 'y': y}] if t != 'touchEnd' else []})
        await touch('touchStart', box[0], box[1])
        for k in range(1, 6): await touch('touchMove', box[0] - k * 40, box[1] + 2)
        await touch('touchEnd', 0, 0); await pg.wait_for_timeout(300)
        p1 = await pg.inner_text('.fcpos')
        ok(p0 != p1, f'스와이프 → 다음 ({p0} → {p1})')
        # 탭 이동 후 위치 유지
        await pg.evaluate("document.querySelector('#fnext').click();document.querySelector('#fnext').click()"); p2 = await pg.inner_text('.fcpos')
        await pg.evaluate("document.querySelector('#dtabs [data-t=learn]').click()"); await pg.wait_for_timeout(500)
        await pg.evaluate("document.querySelector('#dtabs [data-t=flash]').click()"); await pg.wait_for_timeout(500)
        p3 = await pg.inner_text('.fcpos')
        ok(p2 == p3, f'탭 옮겼다 와도 위치 유지 ({p2} = {p3})')
        await pg.screenshot(path=J.TMP + '/ux_u28_flash_820.png')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
