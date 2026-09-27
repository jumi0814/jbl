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
        await pg.goto(U); await pg.wait_for_timeout(2500); ok(await pg.locator('.scard[data-s]').count()>=6, '허브 과목 카드')
        await pg.click('.scard[data-s="GERI"]'); await pg.wait_for_timeout(600); ok(await pg.locator('.lcard').count()>=5, 'GERI 강의 카드'); await pg.screenshot(path=_os.path.join(J.TMP, 'a0.png'))
        await pg.click('#side .dbtn[data-d="_jb"]'); await pg.wait_for_timeout(400); ok(await pg.locator('#cards .qc:not(.hid)').count()>10, 'JB 카드 보임')
        await pg.click('#c-Y01 [data-tog]'); await pg.evaluate("document.getElementById('c-Y01').scrollIntoView()"); await pg.wait_for_timeout(300); await pg.screenshot(path=_os.path.join(J.TMP, 'a1.png'))
        await pg.click('#c-Y01 .cite >> nth=0'); await pg.wait_for_timeout(1500); ok(bool(await pg.inner_text('#mtitle')), '인용 그림 확대창'); await pg.click('#mclose')
        await pg.click('#c-K01 [data-tog]'); (await pg.click('#c-K01 .cite.t >> nth=0')) if await pg.locator('#c-K01 .cite.t').count() else print('text cite: 이 문항에 텍스트 인용 없음(건너뜀)'); await pg.wait_for_timeout(400); print('text cite →', await pg.evaluate('location.hash'))
        for k in ['HARD','OHQ','ENDO','BLE','SAL','PAIN','PSY']:
            await pg.click(f'#side .dbtn[data-d="{k}"]'); await pg.wait_for_timeout(1500); nf=await pg.evaluate("[...document.querySelectorAll('#stage .figs img')].filter(i=>i.src.startsWith('data:')).length"); ok(await pg.locator('#stage .tc').count()>0 and nf==await pg.locator('#stage .figs figure').count(), f"{k} 카드·그림 {nf}/{await pg.locator('#stage .figs figure').count()}")
        await pg.click('#side .dbtn[data-d="PAIN"]'); await pg.wait_for_timeout(1500); ok(True, 'PAIN 열림')
        await pg.evaluate("document.getElementById('t-PAIN-4').scrollIntoView()"); await pg.wait_for_timeout(300); await pg.screenshot(path=_os.path.join(J.TMP, 'a2.png'))
        for t in ['sum','tbl','jb','pred','flash']:
            await pg.click(f'#dtabs button[data-t="{t}"]'); await pg.wait_for_timeout(300); ok(len(await pg.inner_text('#stage'))>50, f'탭 {t} 내용')
        await pg.click('#side .dbtn[data-d="_tbl"]'); await pg.wait_for_timeout(300); ok(await pg.locator('#stage .tblwrap').count()>0, '비교표')
        await pg.click('#side .dbtn[data-d="_led"]'); await pg.wait_for_timeout(300); ok(len(await pg.inner_text('#stage'))>200, '기출 대장')
        await pg.click('#side .dbtn[data-d="SAL"]'); await pg.wait_for_timeout(800); await pg.click('#k-auto'); await pg.check('input[value="red"]'); await pg.click('#ago'); await pg.wait_for_timeout(400); ok(await pg.locator('#stage .rk-b').count()>0, '자동 빈칸'); await pg.keyboard.press('Control+z')
        ok(not errs, f'콘솔 오류 0 {errs[:3]}'); await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fail else f'FAIL {len(fail)}'); _sys.exit(1 if fail else 0)
