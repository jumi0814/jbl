import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import asyncio
from playwright.async_api import async_playwright
U=J.HUB_URL
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1440,'height':1500}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto(U); await pg.wait_for_timeout(2500); print('home subjects', await pg.locator('.scard[data-s]').count())
        await pg.click('.scard[data-s="GERI"]'); await pg.wait_for_timeout(600); print('lcards', await pg.locator('.lcard').count()); await pg.screenshot(path=_os.path.join(J.TMP, 'a0.png'))
        await pg.click('#side .dbtn[data-d="_jb"]'); await pg.wait_for_timeout(400); print('jb visible', await pg.locator('#cards .qc:not(.hid)').count())
        await pg.click('#c-Y01 [data-tog]'); await pg.evaluate("document.getElementById('c-Y01').scrollIntoView()"); await pg.wait_for_timeout(300); await pg.screenshot(path=_os.path.join(J.TMP, 'a1.png'))
        await pg.click('#c-Y01 .cite >> nth=0'); await pg.wait_for_timeout(1500); print('modal', await pg.inner_text('#mtitle')); await pg.click('#mclose')
        await pg.click('#c-K01 [data-tog]'); await pg.click('#c-K01 .cite.t >> nth=0'); await pg.wait_for_timeout(400); print('text cite →', await pg.evaluate('location.hash'))
        for k in ['HARD','OHQ','ENDO','BLE','SAL','PAIN','PSY']:
            await pg.click(f'#side .dbtn[data-d="{k}"]'); await pg.wait_for_timeout(1500); print(k,'cards',await pg.locator('#stage .tc').count(),'figs',await pg.evaluate("[...document.querySelectorAll('#stage .figs img')].filter(i=>i.src.startsWith('data:')).length"),'/',await pg.locator('#stage .figs figure').count())
        await pg.click('#side .dbtn[data-d="PAIN"]'); await pg.wait_for_timeout(1500); print('LP5 figs', await pg.evaluate("[...document.querySelectorAll('#stage .figs img[data-img^=\"PN5\"]')].filter(i=>i.src.startsWith('data:')).length"))
        await pg.evaluate("document.getElementById('t-PAIN-4').scrollIntoView()"); await pg.wait_for_timeout(300); await pg.screenshot(path=_os.path.join(J.TMP, 'a2.png'))
        for t in ['sum','tbl','jb','pred','flash']:
            await pg.click(f'#dtabs button[data-t="{t}"]'); await pg.wait_for_timeout(300); print(t, len(await pg.inner_text('#stage')))
        await pg.click('#side .dbtn[data-d="_tbl"]'); await pg.wait_for_timeout(300); print('tables', await pg.locator('#stage .tblwrap').count())
        await pg.click('#side .dbtn[data-d="_led"]'); await pg.wait_for_timeout(300); print('ledger len', len(await pg.inner_text('#stage')))
        await pg.click('#side .dbtn[data-d="SAL"]'); await pg.wait_for_timeout(800); await pg.click('#k-auto'); await pg.check('input[value="red"]'); await pg.click('#ago'); await pg.wait_for_timeout(400); print('auto blanks', await pg.locator('#stage .rk-b').count()); await pg.keyboard.press('Control+z')
        print('errs', errs[:4]); await b.close()
asyncio.run(main())
