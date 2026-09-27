import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':1000}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto(J.HUB_URL + '#/OMS1/DD1/learn'); await pg.wait_for_timeout(1200)
        li=pg.locator('#t-DD1-3 .tbody .li >> nth=1'); await li.evaluate("e=>e.scrollIntoView({block:'center'})"); await pg.wait_for_timeout(150)
        bx=await li.bounding_box(); x,y=bx['x']+120,bx['y']+14
        await pg.keyboard.press('h'); await pg.mouse.click(x,y); await pg.wait_for_timeout(150); print('hl', await pg.locator('#stage .rk-h').all_inner_texts())
        await pg.keyboard.press('a'); await pg.mouse.move(x+150,y); await pg.mouse.down(); await pg.mouse.move(x+330,y); await pg.mouse.up(); await pg.wait_for_timeout(150); print('blank', await pg.locator('#stage .rk-b').all_inner_texts())
        await pg.keyboard.press('Escape'); await pg.click('#k-auto'); await pg.check('input[value="red"]'); await pg.click('#ago'); await pg.wait_for_timeout(400); print('auto red blanks', await pg.locator('#stage .rk-b').count())
        await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(200); print('undo →', await pg.locator('#stage .rk-b').count())
        await pg.reload(); await pg.wait_for_timeout(1200); print('reload: hl', await pg.locator('#stage .rk-h').count(), 'blank', await pg.locator('#stage .rk-b').count())
        # JB 카드 안에서도 표시가 유지되고, 강의 탭의 같은 카드에서도 보이는지
        await pg.click('#side .dbtn[data-d="_jb"]'); await pg.wait_for_timeout(300); await pg.click('#c-Q01 [data-tog]')
        l2=pg.locator('#c-Q01 .jbans .ln.li >> nth=1'); await l2.evaluate("e=>e.scrollIntoView({block:'center'})"); b2=await l2.bounding_box()
        await pg.keyboard.press('a'); await pg.mouse.click(b2['x']+60,b2['y']+10); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(150)
        await pg.click('#side .dbtn[data-d="DD1"]'); await pg.click('#dtabs button[data-t="jb"]'); await pg.wait_for_timeout(300)
        print('같은 문항 카드의 빈칸이 강의 탭에도 표시:', await pg.locator('#c-Q01 .rk-b').count())
        print('errs', errs[:3]); await b.close()
asyncio.run(main())
