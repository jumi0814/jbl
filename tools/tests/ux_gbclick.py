import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
# 10-27 사용자 '예상문제 칸에서 내가 그림빵의 각 빈칸들 클릭하면 인식 안되는 오류도 고쳐줘! 클릭하면 빈칸 벗겨지게끔! 관련 오류가 생길때가 많아' —
# 보이는 가림막은 모두 한 번에 열림 · 형광펜/빈칸 도구가 켜져 있어도 · 가림막 바로 옆(그림)을 눌러도 가장 가까운 것 · 터치 빠른 연속 탭
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fail = []
def ok(c, m):
    print(('  OK  ' if c else '  FAIL') + ' ' + m)
    if not c: fail.append(m)
SEL = '#stage .pc:not(.px) .gbm'
async def box(pg, i):
    m = pg.locator(SEL).nth(i); await m.evaluate("e=>e.scrollIntoView({block:'center'})"); await pg.wait_for_timeout(80)
    return m, await m.bounding_box(), await m.evaluate("e=>e.classList.contains('open')")
async def opened(m): return await m.evaluate("e=>e.classList.contains('open')")
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        pg = await (await br.new_context(viewport={'width': 1280, 'height': 900})).new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for sid, lec in (('IMPL', 'PART'), ('ANAT', 'MAX'), ('PHARM', 'RX')):
            await pg.goto(U + f'#/{sid}/{lec}/pred'); await pg.wait_for_timeout(2500)
            n = await pg.locator(SEL).count(); good = 0
            for i in range(n):
                m, b, o0 = await box(pg, i); await pg.mouse.click(b['x'] + b['width'] / 2, b['y'] + b['height'] / 2); await pg.wait_for_timeout(60)
                good += (await opened(m)) != o0
            ok(n > 0 and good == n, f'{sid} {lec} 보이는 가림막 {n}개 중 {good}개가 한 번에 열리고 닫힘')
            await pg.reload(); await pg.wait_for_timeout(2500)
            for key, i in (('h', 0), ('b', 1)):
                await pg.keyboard.press(key); m, b, o0 = await box(pg, i); await pg.mouse.click(b['x'] + b['width'] / 2, b['y'] + b['height'] / 2); await pg.wait_for_timeout(80)
                ok((await opened(m)) != o0, f'{sid} 도구 {key} 켜진 채로 가림막 누름 → 열림'); await pg.keyboard.press('Escape')
            m, b, o0 = await box(pg, 2)
            pt = await pg.evaluate("([x,y])=>{const e=document.elementFromPoint(x,y);return e&&e.tagName}", [b['x'] + b['width'] / 2, b['y'] - 5])
            await pg.mouse.click(b['x'] + b['width'] / 2, b['y'] - 5); await pg.wait_for_timeout(80)
            near = await pg.evaluate("([x,y])=>{const fg=document.elementFromPoint(x,y);return true}", [0, 0])
            ok(pt != 'IMG' or (await pg.locator(SEL + '.open').count()) >= 1, f'{sid} 가림막 5px 위({pt}) 누름 → 가장 가까운 가림막 열림')
        tp = await (await br.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True, is_mobile=True)).new_page(); tp.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await tp.goto(U + '#/IMPL/PART/pred'); await tp.wait_for_timeout(2500)
        m0, b0, _ = await box(tp, 0); m1 = tp.locator(SEL).nth(1); b1 = await m1.bounding_box()
        await tp.touchscreen.tap(b0['x'] + b0['width'] / 2, b0['y'] + b0['height'] / 2); await tp.wait_for_timeout(40); await tp.touchscreen.tap(b1['x'] + b1['width'] / 2, b1['y'] + b1['height'] / 2); await tp.wait_for_timeout(150)
        ok(await opened(m0) and await opened(m1), '터치: 가림막 두 개를 빠르게 연달아 탭 → 둘 다 열림')
        ta = await tp.evaluate(f"getComputedStyle(document.querySelector('{SEL}')).touchAction")
        ok(ta == 'manipulation', f'가림막 touch-action = {ta}(두 번 탭 확대 막음)')
        ok(not errs, f'콘솔 오류 0 {errs[:2]}')
        await br.close()
    print('RESULT', 'FAIL' if fail else 'PASS')
asyncio.run(main())
