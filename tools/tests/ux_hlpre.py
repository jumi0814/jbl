import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
# 10-27 사용자 '하이라이트 칠 때 해당 색이 반영되게끔, 지금은 색 무관하게 드래그하면 노란색으로 표시되었다가 마지막에 색이 바뀌는데' — 끄는 동안 미리 보기 = 고른 형광펜 색(빈칸은 고른 빈칸 색)
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fail = []
def ok(c, m):
    print(('  OK  ' if c else '  FAIL') + ' ' + m)
    if not c: fail.append(m)
HL = {'y': 'rgb(255, 229, 138)', 'g': 'rgb(189, 235, 196)', 'p': 'rgb(255, 207, 223)', 'u': 'rgb(201, 221, 247)', 'o': 'rgb(255, 201, 140)'}
BK = {'n': 'rgb(230, 226, 220)', 'u': 'rgb(214, 228, 245)', 'v': 'rgb(226, 218, 242)'}
async def drag(pg, li, check):
    await li.evaluate("e=>e.scrollIntoView({block:'center'})"); await pg.wait_for_timeout(150); b = await li.bounding_box()
    await pg.mouse.move(b['x'] + 20, b['y'] + b['height'] / 2); await pg.mouse.down(); await pg.mouse.move(b['x'] + 240, b['y'] + b['height'] / 2, steps=6)
    mid = await pg.evaluate("[...document.querySelectorAll('#stage [data-pre]')].map(e=>getComputedStyle(e).backgroundColor)")
    await pg.mouse.up(); await pg.wait_for_timeout(150); return mid
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await (await br.new_context(viewport={'width': 1280, 'height': 1000})).new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for sid, lec in (('CONS', 'ADH'), ('PHARM', 'HM')):
            await pg.goto(U + f'#/{sid}/{lec}/learn'); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(2500)
            lis = pg.locator(f'#t-{lec}-1 .tbody :is(li,.li)'); n = await lis.count()
            await pg.keyboard.press('h')
            for i, c in enumerate(['g', 'p', 'y']):
                await pg.evaluate(f"__h.Kit.setColor('{c}')"); mid = await drag(pg, lis.nth(min(i, n - 1) if n else 0), c)
                fin = await pg.evaluate("[...document.querySelectorAll('#stage .rk-h')].map(e=>e.dataset.c)")
                ok(bool(mid) and all(x == HL[c] for x in mid), f'{sid} 형광펜 {c}: 끄는 동안 {set(mid)} = {HL[c]}')
                ok(c in fin, f'{sid} 형광펜 {c}: 놓은 뒤 같은 색 {sorted(set(fin))}')
            await pg.keyboard.press('Escape'); await pg.keyboard.press('b')
            for j, c in enumerate(('u', 'n')):
                await pg.evaluate(f"__h.Kit.setBColor('{c}')"); mid = await drag(pg, lis.nth(min(3 + j, n - 1)) if n else lis.first, c)
                ok(bool(mid) and all(x == BK[c] for x in mid), f'{sid} 빈칸 {c}: 끄는 동안 {set(mid)} = {BK[c]}')
            await pg.keyboard.press('Escape')
        ok(not errs, f'콘솔 오류 0 {errs[:2]}')
        await br.close()
    print('RESULT', 'FAIL' if fail else 'PASS')
asyncio.run(main())
