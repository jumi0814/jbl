import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
# 10-27 사용자 '검색칸에서 타이핑하다가 지우고 결국 빈칸인 상태일 때 자동 나가지는게 아니라 계속 유지되어서 내가 바로 타이핑하면 검색창에서 타이핑이 되게끔'
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fail = []
def ok(c, m):
    print(('  OK  ' if c else '  FAIL') + ' ' + m)
    if not c: fail.append(m)
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        for vw in ({'width': 1280, 'height': 900}, {'width': 390, 'height': 844}):
            pg = await (await br.new_context(viewport=vw)).new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto(U + '#/CONS/ADH/learn'); await pg.wait_for_timeout(2500)
            await pg.click('#gsearch'); await pg.keyboard.type('adhesion', delay=30); await pg.wait_for_timeout(900)
            ok(await pg.evaluate("location.hash.startsWith('#/?q=')"), f'{vw["width"]} 검색 결과 화면')
            for _ in range(8): await pg.keyboard.press('Backspace'); await pg.wait_for_timeout(40)
            await pg.wait_for_timeout(500)
            st = await pg.evaluate("({act:document.activeElement&&document.activeElement.id,val:document.querySelector('#gsearch').value,emp:!!document.querySelector('#home .srchempty'),hash:location.hash})")
            ok(st['act'] == 'gsearch' and st['val'] == '' and st['emp'], f'{vw["width"]} 글자를 다 지워도 검색칸 그대로(포커스 {st["act"]} · 안내 {st["emp"]})')
            await pg.keyboard.type('hybrid', delay=30); await pg.wait_for_timeout(900)
            st2 = await pg.evaluate("({act:document.activeElement&&document.activeElement.id,val:document.querySelector('#gsearch').value,res:document.querySelectorAll('#home .res').length})")
            ok(st2['act'] == 'gsearch' and st2['val'] == 'hybrid' and st2['res'] > 0, f'{vw["width"]} 바로 다시 치면 검색칸에 입력·결과 {st2["res"]}')
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(600)
            ok(await pg.evaluate("location.hash.startsWith('#/CONS/ADH')"), f'{vw["width"]} Esc = 검색 전 화면으로')
            await pg.click('#gsearch'); await pg.keyboard.type('ab', delay=30); await pg.wait_for_timeout(800)
            for _ in range(2): await pg.keyboard.press('Backspace')
            await pg.wait_for_timeout(300); await pg.click('#home #sclose') if await pg.locator('#home #sclose').count() else None; await pg.wait_for_timeout(600)
            ok(await pg.evaluate("location.hash.startsWith('#/CONS/ADH')"), f'{vw["width"]} 빈 검색 화면의 ✕ 닫기 = 검색 전 화면으로')
        ok(not errs, f'콘솔 오류 0 {errs[:2]}')
        await br.close()
    print('RESULT', 'FAIL' if fail else 'PASS')
asyncio.run(main())
