import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import asyncio, json
from playwright.async_api import async_playwright
U=J.HUB_URL
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1280,'height':1000}); pg=await ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto(U+'#/ANAT/MAND/learn'); await pg.wait_for_timeout(2500)
        await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(2500)
        card=pg.locator('#t-MAND-1'); await card.evaluate("e=>e.scrollIntoView({block:'start'})"); await pg.wait_for_timeout(200)
        # 1) 어절 클릭: 'including angle' 근처 빨간 글자 클릭
        k=pg.locator('#t-MAND-1 .c-key .k >> nth=0'); kb=await k.bounding_box(); print('target', await k.inner_text())
        await pg.keyboard.press('h'); await pg.mouse.click(kb['x']+5,kb['y']+kb['height']/2); await pg.wait_for_timeout(150)
        print('1 click word →', await pg.locator('#stage .rk-h').all_inner_texts())
        # 2) 같은 곳 다시 클릭 → 지움
        await pg.mouse.click(kb['x']+5,kb['y']+kb['height']/2); await pg.wait_for_timeout(150); print('2 toggle off →', await pg.locator('#stage .rk-h').count())
        # 3) 드래그로 여러 어절(요소 경계 포함) → 빈칸 한 묶음
        li=pg.locator('#t-MAND-1 .tbody :is(li,.li) >> nth=1'); lb=await li.bounding_box()
        await pg.keyboard.press('a'); await pg.mouse.move(lb['x']+30,lb['y']+lb['height']/2); await pg.mouse.down(); await pg.mouse.move(lb['x']+200,lb['y']+lb['height']/2,steps=6)
        print('3a preview spans', await pg.locator('#stage [data-pre]').count())
        await pg.mouse.move(lb['x']+380,lb['y']+lb['height']/2,steps=4); await pg.mouse.up(); await pg.wait_for_timeout(150)
        g=await pg.evaluate("[...new Set([...document.querySelectorAll('#stage .rk-b')].map(e=>e.dataset.g))]")
        print('3b blank spans', await pg.locator('#stage .rk-b').count(), 'groups', len(g), 'text', await pg.evaluate("[...document.querySelectorAll('#stage .rk-b')].map(e=>e.textContent).join('')"))
        # 4) 도구 끄고 빈칸 한 조각 클릭 → 묶음 전체 열림
        await pg.keyboard.press('Escape'); await pg.locator('#stage .rk-b >> nth=0').click(); await pg.wait_for_timeout(100)
        print('4 reveal all in group', await pg.locator('#stage .rk-b.show').count(), '/', await pg.locator('#stage .rk-b').count())
        # 5) 형광 드래그 다른 카드 + undo/redo
        li2=pg.locator('#t-MAND-2 .tbody :is(li,.li) >> nth=0'); await li2.evaluate("e=>e.scrollIntoView({block:'center'})"); b2=await li2.bounding_box()
        await pg.keyboard.press('h'); await pg.mouse.move(b2['x']+20,b2['y']+10); await pg.mouse.down(); await pg.mouse.move(b2['x']+260,b2['y']+10,steps=5); await pg.mouse.up(); await pg.wait_for_timeout(150)
        n_h=await pg.locator('#stage .rk-h').count(); await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(100); n_u=await pg.locator('#stage .rk-h').count(); await pg.keyboard.press('Control+Shift+z'); await pg.wait_for_timeout(100); n_r=await pg.locator('#stage .rk-h').count()
        print('5 hl', n_h, 'undo', n_u, 'redo', n_r)
        ann=await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.ann.ANAT'))"); print('stored', json.dumps(ann,ensure_ascii=False)[:400])
        # 6) 새로고침 후 복원
        await pg.reload(); await pg.wait_for_timeout(2500); print('6 reload hl', await pg.locator('#stage .rk-h').count(), 'blank', await pg.locator('#stage .rk-b').count(), 'groups', await pg.evaluate("new Set([...document.querySelectorAll('#stage .rk-b')].map(e=>e.dataset.g)).size"))
        # 7) 느슨한 복원: 저장 텍스트에 ' / ' 구분자가 들어간 옛 기록 흉내
        await pg.evaluate("""()=>{const k='jblhub.v1.ann.ANAT';const a=JSON.parse(localStorage.getItem(k));const aid=document.querySelector('#t-MAND-3').dataset.aid;a[aid]=[{t:'h',x:'anterior to masseter / facial a.&v. cross inf. border',i:0,c:'g'}];localStorage.setItem(k,JSON.stringify(a));}""")
        await pg.reload(); await pg.wait_for_timeout(2500); print('7 fuzzy restore in card3', await pg.locator('#t-MAND-3 .rk-h').all_inner_texts())
        # 8) 옛 aid(data-alt) 기록 이관
        await pg.evaluate("""()=>{const k='jblhub.v1.ann.ANAT';const a=JSON.parse(localStorage.getItem(k));const el=document.querySelector('#t-MAND-4');a[el.dataset.alt]=[{t:'b',x:'Wharton',i:0}];localStorage.setItem(k,JSON.stringify(a));}""")
        await pg.reload(); await pg.wait_for_timeout(2500); print('8 alt migrate', await pg.locator('#t-MAND-4 .rk-b').count(), await pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('jblhub.v1.ann.ANAT'))).some(k=>k.endsWith(':c3'))"))
        # 9) 모달
        f=pg.locator('#t-MAND-1 figure >> nth=0'); await f.scroll_into_view_if_needed(); await f.click(); await pg.wait_for_timeout(900)
        print('9 modal on', await pg.evaluate("document.getElementById('imgmodal').classList.contains('on')"))
        ib=await pg.locator('#mimg').bounding_box(); await pg.mouse.click(ib['x']+ib['width']*0.3, ib['y']+ib['height']*0.3); await pg.wait_for_timeout(300)
        print('  zoom', await pg.evaluate("document.getElementById('mimg').style.width"))
        await pg.mouse.click(ib['x']+ib['width']*0.3, ib['y']+ib['height']*0.3); await pg.wait_for_timeout(200); print('  unzoom', await pg.evaluate("document.getElementById('mimg').style.width||'fit'"))
        await pg.mouse.click(8, 500); await pg.wait_for_timeout(200); print('  backdrop close →', await pg.evaluate("document.getElementById('imgmodal').classList.contains('on')"))
        # 10) 공부시간 자동
        await pg.mouse.move(300,300); await pg.mouse.move(310,320); await pg.wait_for_timeout(2300); print('10 clock', await pg.inner_text('#clock'), await pg.inner_text('#tmr'))
        await pg.click('#clock'); await pg.wait_for_timeout(200); print('   tpop', (await pg.inner_text('#tpop'))[:80].replace('\n',' | '))
        await pg.mouse.click(600,600); await pg.wait_for_timeout(100)
        # 11) 모아보기
        await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"_marks\"]').click()"); await pg.wait_for_timeout(600); print('11 marks', await pg.locator('.mk-row').count(), await pg.locator('.mk').count())
        await pg.locator('.mk-row .res >> nth=0').click(); await pg.wait_for_timeout(800); print('   jump', await pg.evaluate('location.hash'))
        # 12) 복원 팝업·도움말
        await pg.click('#rstr'); await pg.wait_for_timeout(150); print('12 rpop', await pg.locator('#rpop.on').count(), 'snaps', await pg.locator('#rpop [data-snap]').count())
        await pg.keyboard.press('Escape'); await pg.keyboard.press('?'); await pg.wait_for_timeout(100); print('   help', await pg.locator('#help.on').count()); await pg.keyboard.press('Escape')
        # 13) 홈 이어서 보기
        await pg.click('#gohome'); await pg.wait_for_timeout(300); print('13 resume', await pg.locator('.resume .res').count(), 'bkp', await pg.locator('.bkp').count())
        print('errs', errs[:5]); await b.close()
asyncio.run(main())
