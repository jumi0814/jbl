import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import asyncio
from playwright.async_api import async_playwright
U=J.HUB_URL
fail=[]
def ok(c,msg):
    print(('  OK  ' if c else '  FAIL')+' '+msg)
    if not c: fail.append(msg)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1440,'height':1500}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto(U); await pg.wait_for_timeout(2500)
        ok(await pg.locator('.scard[data-s]').count()>=6, '허브 과목 카드')
        await pg.click('.scard[data-s="CONS"]'); await pg.wait_for_timeout(600); ok(await pg.locator('.lcard').count()>=5, f"CONS 강의 카드 {await pg.locator('.lcard').count()}")
        await pg.screenshot(path=_os.path.join(J.TMP, 'k0.png'))
        await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"_jb\"]').click()"); await pg.wait_for_timeout(400); ok(await pg.locator('#cards .qc:not(.hid)').count()>10, 'JB 카드 보임')
        await pg.click('#c-Q08 [data-tog]'); await pg.evaluate("document.getElementById('c-Q08').scrollIntoView()"); await pg.wait_for_timeout(300); await pg.screenshot(path=_os.path.join(J.TMP, 'k1.png'))
        await pg.click('#c-Q08 .cite >> nth=0'); await pg.wait_for_timeout(1500); ok(bool(await pg.inner_text('#mtitle')), '인용 그림 확대창'); await pg.click('#mclose')
        await pg.click('#c-Q08 [data-jb] >> nth=0'); await pg.wait_for_timeout(1500); ok('JB' in await pg.inner_text('#mtitle') or bool(await pg.inner_text('#mtitle')), 'JB 원본 쪽 창'); await pg.click('#mclose')
        await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"WHT\"]').click()"); await pg.wait_for_timeout(2500); ok(await pg.locator('#stage .tc').count()>3 and await pg.evaluate("[...document.querySelectorAll('#stage .figs img')].filter(i=>i.src.startsWith('data:')).length")>0, 'WHT 카드·그림')
        await pg.evaluate("document.getElementById('t-WHT-4').scrollIntoView()"); await pg.wait_for_timeout(300); await pg.screenshot(path=_os.path.join(J.TMP, 'k2.png'))
        for k in ['CRK','DHS','INL','ANT','ADH','FRC']:
            await pg.evaluate("d=>document.querySelector('#side .dbtn[data-d=\"'+d+'\"]').click()", k); await pg.wait_for_timeout(1500); nf=await pg.evaluate("[...document.querySelectorAll('#stage .figs img')].filter(i=>i.src.startsWith('data:')).length"); ok(await pg.locator('#stage .tc').count()>0 and nf==await pg.locator('#stage .figs figure').count(), f"{k} 카드·그림 {nf}/{await pg.locator('#stage .figs figure').count()}")
        await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"_jb\"]').click()"); await pg.wait_for_timeout(300); await pg.click('#c-Q09 [data-tog]'); (await pg.click('#c-Q09 .cite.t >> nth=0')) if await pg.locator('#c-Q09 .cite.t').count() else print('text cite: 이 문항에 텍스트 인용 없음(건너뜀)'); await pg.wait_for_timeout(300); print('text cite →', await pg.evaluate('location.hash')); await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"INL\"]').click()"); await pg.wait_for_timeout(300)
        for t in ['sum','tbl','jb','pred','flash']:
            await pg.click(f'#dtabs button[data-t="{t}"]'); await pg.wait_for_timeout(300); ok(len(await pg.inner_text('#stage'))>50, f'탭 {t} 내용')
        await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"_tbl\"]').click()"); await pg.wait_for_timeout(300); ok(await pg.locator('#stage .tblwrap').count()>0, '비교표')
        await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"_led\"]').click()"); await pg.wait_for_timeout(300); ok(len(await pg.inner_text('#stage'))>200, '기출 대장')
        # 도구
        await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"ADH\"]').click()"); await pg.wait_for_timeout(800); await pg.click('#k-auto'); await pg.check('input[value="red"]'); await pg.click('#ago'); await pg.wait_for_timeout(400); ok(await pg.locator('#stage .rk-b').count()>0, '자동 빈칸'); await pg.keyboard.press('Control+z')
        await pg.click('.scard, #gohome'); await pg.wait_for_timeout(400); ok(await pg.locator('.scard[data-s]').count()>=6, '홈으로')
        ok(not errs, f'콘솔 오류 0 {errs[:3]}')
        p2=await b.new_page(); e2=[]; p2.on('pageerror',lambda e:e2.append(str(e)[:150])); await p2.goto('file://' + _os.path.join(J.WORK, '임상치과보존학_JBL.html') + '#/CONS/FRC/learn'); await p2.wait_for_timeout(2500); ok(await p2.evaluate("[...document.querySelectorAll('#stage .figs img')].filter(i=>i.src.startsWith('data:')).length")>0 and not e2, f'단일 파일판 그림 {e2[:2]}')
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fail else f'FAIL {len(fail)}'); _sys.exit(1 if fail else 0)
