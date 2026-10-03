import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import asyncio, json
from playwright.async_api import async_playwright
U=J.HUB_URL
fail=[]
def ok(c,msg):
    print(('  OK  ' if c else '  FAIL')+' '+msg)
    if not c: fail.append(msg)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1280,'height':1000}); pg=await ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto(U+'#/ANAT/MAND/learn'); await pg.wait_for_timeout(2500)
        await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(2500)
        # 0) 한글 입력 상태의 키(e.key='ㅗ', e.code='KeyH') — 키 이름은 e.code로(A01)
        r0=await pg.evaluate("""()=>{const k=(key,code)=>document.body.dispatchEvent(new KeyboardEvent('keydown',{key,code,bubbles:true,cancelable:true}));const B=document.body.classList;
          k('ㅗ','KeyH');const h=B.contains('mode-h');k('ㅗ','KeyH');const h2=B.contains('mode-h');k('ㅠ','KeyB');const b=B.contains('mode-b');k('Escape','Escape');return [h,h2,b,B.contains('mode-b')];}""")
        ok(r0==[True,False,True,False], f'0 한글 입력 상태 ㅗ(KeyH) 형광펜 켜기·끄기 · ㅠ(KeyB) 빈칸 · Esc 끄기 {r0}')
        card=pg.locator('#t-MAND-1'); await card.evaluate("e=>e.scrollIntoView({block:'start'})"); await pg.wait_for_timeout(200)
        # 1) 어절 클릭: 'including angle' 근처 빨간 글자 클릭
        k=pg.locator('#t-MAND-1 .c-key .k >> nth=0'); kb=await k.bounding_box(); print('target', await k.inner_text())
        await pg.keyboard.press('h'); await pg.mouse.click(kb['x']+5,kb['y']+kb['height']/2); await pg.wait_for_timeout(150)
        t1=await pg.locator('#stage .rk-h').all_inner_texts(); ok(len(t1)>=1, f'1 누르면 어절 형광 {t1}')
        # 2) 같은 곳 다시 클릭 → 지움
        await pg.mouse.click(kb['x']+5,kb['y']+kb['height']/2); await pg.wait_for_timeout(150); ok(await pg.locator('#stage .rk-h').count()==0, '2 같은 곳 다시 누르면 지움')
        # 3) 드래그로 여러 어절(요소 경계 포함) → 빈칸 한 묶음
        li=pg.locator('#t-MAND-1 .tbody :is(li,.li) >> nth=1'); lb=await li.bounding_box()
        await pg.keyboard.press('a'); await pg.mouse.move(lb['x']+30,lb['y']+lb['height']/2); await pg.mouse.down(); await pg.mouse.move(lb['x']+200,lb['y']+lb['height']/2,steps=6)
        ok(await pg.locator('#stage [data-pre]').count()>0, '3a 끄는 동안 미리보기')
        await pg.mouse.move(lb['x']+380,lb['y']+lb['height']/2,steps=4); await pg.mouse.up(); await pg.wait_for_timeout(150)
        g=await pg.evaluate("[...new Set([...document.querySelectorAll('#stage .rk-b')].map(e=>e.dataset.g))]")
        ok(await pg.locator('#stage .rk-b').count()>=1 and len(g)==1, f'3b 드래그 빈칸 = 한 묶음 (조각 {await pg.locator("#stage .rk-b").count()}, 묶음 {len(g)})')
        # 4) 도구 끄고 빈칸 한 조각 클릭 → 묶음 전체 열림
        await pg.keyboard.press('Escape'); await pg.locator('#stage .rk-b >> nth=0').click(); await pg.wait_for_timeout(100)
        ok(await pg.locator('#stage .rk-b.show').count()==await pg.locator('#stage .rk-b').count()>0, '4 빈칸 한 조각 누르면 묶음 전체 열림')
        # 5) 형광 드래그 다른 카드 + undo/redo
        li2=pg.locator('#t-MAND-2 .tbody :is(li,.li) >> nth=0'); await li2.evaluate("e=>e.scrollIntoView({block:'center'})"); b2=await li2.bounding_box()
        await pg.keyboard.press('h'); await pg.mouse.move(b2['x']+20,b2['y']+10); await pg.mouse.down(); await pg.mouse.move(b2['x']+260,b2['y']+10,steps=5); await pg.mouse.up(); await pg.wait_for_timeout(150)
        n_h=await pg.locator('#stage .rk-h').count(); await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(100); n_u=await pg.locator('#stage .rk-h').count(); await pg.keyboard.press('Control+Shift+z'); await pg.wait_for_timeout(100); n_r=await pg.locator('#stage .rk-h').count()
        ok(n_h>=1 and n_u<n_h and n_r==n_h, f'5 형광 드래그 {n_h} · 되돌리기 {n_u} · 다시 {n_r}')
        ann=await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.ann.ANAT'))")
        ok(all(('p' in o and 's' in o and 'v' in o) for L in ann.values() for o in L), '5b 새 표시는 문맥(p·s)·블록 지문(v)과 함께 저장(F1)')
        # 6) 새로고침 후 복원
        await pg.reload(); await pg.wait_for_timeout(2500); ok(await pg.locator('#stage .rk-h').count()>=1 and await pg.locator('#stage .rk-b').count()>=1 and await pg.evaluate("new Set([...document.querySelectorAll('#stage .rk-b')].map(e=>e.dataset.g)).size")==1, '6 새로고침 후 형광·빈칸 묶음 복원')
        # 7) 느슨한 복원: 옛 기록처럼 어절 사이에 ' / '가 낀 글자(문맥 없음) — 카드 3에서 블록 안에 한 번만 나오는 세 어절을 골라 흉내(고정 글자 대신)
        fx=await pg.evaluate("""()=>{const B=document.querySelector('#t-MAND-3');const T=__h.Kit.textOf(B);const lis=[...B.querySelectorAll('.tbody :is(li,.li)')];
          for(const li of lis){const w=li.textContent.trim().split(/\\s+/).filter(x=>/[A-Za-z가-힣]{2}/.test(x));for(let k=0;k+2<w.length;k++){const ph=w.slice(k,k+3).join(' ');if(T.split(ph).length===2)return [B.dataset.aid,w[k],w[k+1]+' '+w[k+2]];}}return null;}""")
        ok(fx is not None, f'7a 고정 글자 대신 카드에서 고른 글자 {fx}')
        if fx:
            await pg.evaluate("""(f)=>{const k='jblhub.v1.ann.ANAT';const a=JSON.parse(localStorage.getItem(k));a[f[0]]=[{t:'h',x:f[1]+' / '+f[2],i:0,c:'g'}];localStorage.setItem(k,JSON.stringify(a));}""", fx)
            await pg.reload(); await pg.wait_for_timeout(2500); r7=await pg.locator('#t-MAND-3 .rk-h').all_inner_texts()
            ok(len(r7)>=1 and fx[1] in ''.join(r7), f'7 느슨한 복원(구분 기호 무시) → {r7}')
        # 8) 옛 aid(data-alt) 기록 이관 — 카드 4에서 한 번만 나오는 어절
        f8=await pg.evaluate("""()=>{const B=document.querySelector('#t-MAND-4');if(!B||!B.dataset.alt)return null;const T=__h.Kit.textOf(B);const w=(T.match(/[A-Za-z]{5,}/g)||[]).find(x=>T.split(x).length===2);return w?[B.dataset.alt.split(' ')[0],w,B.dataset.aid]:null;}""")
        ok(f8 is not None, f'8a 옛 aid·고른 글자 {f8}')
        if f8:
            await pg.evaluate("""(f)=>{const k='jblhub.v1.ann.ANAT';const a=JSON.parse(localStorage.getItem(k));a[f[0]]=[{t:'b',x:f[1],i:0}];localStorage.setItem(k,JSON.stringify(a));}""", f8)
            await pg.reload(); await pg.wait_for_timeout(2500)
            ok(await pg.locator('#t-MAND-4 .rk-b').count()>=1 and not await pg.evaluate("(f)=>f[0] in JSON.parse(localStorage.getItem('jblhub.v1.ann.ANAT'))", f8), '8 옛 aid 표시 → 새 카드로 이관')
        # 9) 모달
        f=pg.locator('#t-MAND-1 figure >> nth=0'); await f.scroll_into_view_if_needed(); await f.click(); await pg.wait_for_timeout(900)
        ok(await pg.evaluate("document.getElementById('imgmodal').classList.contains('on')"), '9 그림 누르면 확대창')
        ib=await pg.locator('#mimg').bounding_box(); await pg.mouse.click(ib['x']+ib['width']*0.3, ib['y']+ib['height']*0.3); await pg.wait_for_timeout(300)
        ok(bool(await pg.evaluate("document.getElementById('mimg').style.width")), '9b 그림 누르면 확대')
        await pg.mouse.click(ib['x']+ib['width']*0.3, ib['y']+ib['height']*0.3); await pg.wait_for_timeout(200); ok(await pg.evaluate("document.getElementById('mimg').style.width||'fit'")=='fit', '9c 다시 누르면 맞춤')
        await pg.mouse.click(8, 500); await pg.wait_for_timeout(200); ok(not await pg.evaluate("document.getElementById('imgmodal').classList.contains('on')"), '9d 바깥 누르면 닫힘')
        # 10) 공부시간 자동
        await pg.mouse.move(300,300); await pg.mouse.wheel(0, 1); await pg.mouse.move(310,320); await pg.mouse.wheel(0, 1); await pg.wait_for_timeout(2300); ok(bool((await pg.inner_text('#clock')).strip()), f"10 공부 시계 알약 {await pg.inner_text('#clock')}")
        await pg.click('#clock'); await pg.wait_for_timeout(200); print('   tpop', (await pg.inner_text('#tpop'))[:80].replace('\n',' | '))
        await pg.mouse.click(600,600); await pg.wait_for_timeout(100)
        # 11) 모아보기
        await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"_marks\"]').click()"); await pg.wait_for_timeout(600); ok(await pg.locator('.mk-row').count()>=1, f"11 모아보기 줄 {await pg.locator('.mk-row').count()}")
        await pg.locator('.mk-row .res >> nth=0').click(); await pg.wait_for_timeout(800); ok('_marks' not in await pg.evaluate('location.hash'), f"11b 칩 → 그 자리 {await pg.evaluate('location.hash')}")
        # 12) 복원 팝업·도움말
        await pg.evaluate("document.querySelector('#bkup').click()"); await pg.click('#rstr'); await pg.wait_for_timeout(150); ok(await pg.locator('#rpop.on').count()==1, f"12 복원 창 (자동 백업 {await pg.locator('#rpop [data-snap]').count()})")
        await pg.keyboard.press('Escape'); await pg.keyboard.press('?'); await pg.wait_for_timeout(100); ok(await pg.locator('#help.on').count()==1, '12b 도움말(?)'); await pg.keyboard.press('Escape')
        # 13) 홈 이어서 보기
        await pg.click('#gohome'); await pg.wait_for_timeout(300); ok(await pg.locator('.resume .res').count()>=1, '13 홈 이어서 보기')
        ok(not errs, f'콘솔 오류 0 {errs[:3]}'); await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fail else f'FAIL {len(fail)}'); _sys.exit(1 if fail else 0)
