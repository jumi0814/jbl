import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import asyncio
from playwright.async_api import async_playwright
U=J.HUB_URL
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1440,'height':1500}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto(U); await pg.wait_for_timeout(2500)
        print('home active', await pg.locator('.scard[data-s]').count())
        await pg.click('.scard[data-s="CONS"]'); await pg.wait_for_timeout(600); print('hash', await pg.evaluate('location.hash'), 'lcards', await pg.locator('.lcard').count())
        await pg.screenshot(path=_os.path.join(J.TMP, 'k0.png'))
        await pg.click('#side .dbtn[data-d="_jb"]'); await pg.wait_for_timeout(400); print('jb visible', await pg.locator('#cards .qc:not(.hid)').count())
        await pg.click('#c-Q08 [data-tog]'); await pg.evaluate("document.getElementById('c-Q08').scrollIntoView()"); await pg.wait_for_timeout(300); await pg.screenshot(path=_os.path.join(J.TMP, 'k1.png'))
        await pg.click('#c-Q08 .cite >> nth=0'); await pg.wait_for_timeout(1500); print('modal', await pg.inner_text('#mtitle')); await pg.click('#mclose')
        await pg.click('#c-Q08 [data-jb] >> nth=0'); await pg.wait_for_timeout(1500); print('jb modal', await pg.inner_text('#mtitle')); await pg.click('#mclose')
        await pg.click('#side .dbtn[data-d="WHT"]'); await pg.wait_for_timeout(2500); print('WHT cards', await pg.locator('#stage .tc').count(), 'figs loaded', await pg.evaluate("[...document.querySelectorAll('#stage .figs img')].filter(i=>i.src.startsWith('data:')).length"))
        await pg.evaluate("document.getElementById('t-WHT-4').scrollIntoView()"); await pg.wait_for_timeout(300); await pg.screenshot(path=_os.path.join(J.TMP, 'k2.png'))
        for k in ['CRK','DHS','INL','ANT','ADH','FRC']:
            await pg.click(f'#side .dbtn[data-d="{k}"]'); await pg.wait_for_timeout(1500); print(k,'cards',await pg.locator('#stage .tc').count(),'figs',await pg.evaluate("[...document.querySelectorAll('#stage .figs img')].filter(i=>i.src.startsWith('data:')).length"),'/',await pg.locator('#stage .figs figure').count())
        await pg.click('#side .dbtn[data-d="_jb"]'); await pg.wait_for_timeout(300); await pg.click('#c-Q09 [data-tog]'); (await pg.click('#c-Q09 .cite.t >> nth=0')) if await pg.locator('#c-Q09 .cite.t').count() else print('text cite: 이 문항에 텍스트 인용 없음(건너뜀)'); await pg.wait_for_timeout(300); print('text cite →', await pg.evaluate('location.hash')); await pg.click('#side .dbtn[data-d="INL"]'); await pg.wait_for_timeout(300)
        for t in ['sum','tbl','jb','pred','flash']:
            await pg.click(f'#dtabs button[data-t="{t}"]'); await pg.wait_for_timeout(300); print(t, len(await pg.inner_text('#stage')))
        await pg.click('#side .dbtn[data-d="_tbl"]'); await pg.wait_for_timeout(300); print('tables', await pg.locator('#stage .tblwrap').count())
        await pg.click('#side .dbtn[data-d="_led"]'); await pg.wait_for_timeout(300); print('ledger len', len(await pg.inner_text('#stage')))
        # 도구
        await pg.click('#side .dbtn[data-d="ADH"]'); await pg.wait_for_timeout(800); await pg.click('#k-auto'); await pg.check('input[value="red"]'); await pg.click('#ago'); await pg.wait_for_timeout(400); print('auto blanks', await pg.locator('#stage .rk-b').count()); await pg.keyboard.press('Control+z')
        await pg.click('.scard, #gohome'); await pg.wait_for_timeout(400); print('home both', await pg.locator('.scard[data-s]').count())
        print('errs', errs[:4])
        p2=await b.new_page(); e2=[]; p2.on('pageerror',lambda e:e2.append(str(e)[:150])); await p2.goto('file://' + _os.path.join(J.WORK, '임상치과보존학_JBL.html') + '#/CONS/FRC/learn'); await p2.wait_for_timeout(2500); print('single-file FRC figs', await p2.evaluate("[...document.querySelectorAll('#stage .figs img')].filter(i=>i.src.startsWith('data:')).length"), e2[:2])
        await b.close()
asyncio.run(main())
