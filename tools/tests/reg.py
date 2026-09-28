import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import asyncio
from playwright.async_api import async_playwright
fail=[]
def ok(c,msg):
    print(('  OK  ' if c else '  FAIL')+' '+msg)
    if not c: fail.append(msg)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':1000}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto(J.HUB_URL + '#/OMS1/DD1/learn'); await pg.wait_for_timeout(1200)
        li=pg.locator('#t-DD1-3 .tbody .li >> nth=1'); await li.evaluate("e=>e.scrollIntoView({block:'center'})"); await pg.wait_for_timeout(150)
        bx=await li.bounding_box(); x,y=bx['x']+120,bx['y']+14
        await pg.keyboard.press('h'); await pg.mouse.click(x,y); await pg.wait_for_timeout(150); ok(await pg.locator('#stage .rk-h').count()>=1, f"형광 {await pg.locator('#stage .rk-h').all_inner_texts()}")
        await pg.keyboard.press('a'); await pg.mouse.move(x+150,y); await pg.mouse.down(); await pg.mouse.move(x+330,y); await pg.mouse.up(); await pg.wait_for_timeout(150); ok(await pg.locator('#stage .rk-b').count()>=1, f"빈칸 {await pg.locator('#stage .rk-b').all_inner_texts()}")
        await pg.keyboard.press('Escape'); await pg.click('#k-auto'); await pg.check('input[value="red"]'); await pg.click('#ago'); await pg.wait_for_timeout(400); nb=await pg.locator('#stage .rk-b').count(); ok(nb>1, f'자동 빈칸 {nb}')
        await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(200); ok(await pg.locator('#stage .rk-b').count()<nb, '자동 빈칸 되돌리기')
        await pg.reload(); await pg.wait_for_timeout(1200); ok(await pg.locator('#stage .rk-h').count()>=1 and await pg.locator('#stage .rk-b').count()>=1, '새로고침 후 복원')
        # JB 카드 안에서도 표시가 유지되고, 강의 탭의 같은 카드에서도 보이는지
        await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"_jb\"]').click()"); await pg.wait_for_selector('#c-Q01 [data-tog]'); await pg.click('#c-Q01 [data-tog]'); await pg.wait_for_selector('#c-Q01 .jbans .ln.li >> nth=1', state='visible')   # ux3: 조건 대기(부하 중 300ms 고정 대기가 모자라 가끔 실패)
        l2=pg.locator('#c-Q01 .jbans .ln.li >> nth=1'); await l2.evaluate("e=>e.scrollIntoView({block:'center'})"); b2=await l2.bounding_box()
        for _ in range(20):   # ux3: 답 펼침·막대가 자리 잡을 때까지(자리가 두 번 같을 때) — 부하 중 그 사이 누르면 ✓ 맞음 버튼을 눌러 가끔 실패
            await pg.wait_for_timeout(100); nb2=await l2.bounding_box()
            if nb2==b2: break
            b2=nb2
        await pg.keyboard.press('a'); await pg.mouse.click(b2['x']+60,b2['y']+10); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(150)
        await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"DD1\"]').click()"); await pg.click('#dtabs button[data-t="jb"]')
        try: await pg.wait_for_function("document.querySelectorAll('#c-Q01 .rk-b').length>0", timeout=5000)
        except Exception: pass
        ok(await pg.locator('#c-Q01 .rk-b').count()>=1, '같은 문항 카드의 빈칸이 강의 탭에도 표시')
        ok(not errs, f'콘솔 오류 0 {errs[:3]}'); await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fail else f'FAIL {len(fail)}'); _sys.exit(1 if fail else 0)
