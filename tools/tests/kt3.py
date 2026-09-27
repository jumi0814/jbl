import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import asyncio
from playwright.async_api import async_playwright
U=J.HUB_URL
JS="""async ([x1,y1,x2,y2,hold])=>{const tgt=document.elementFromPoint(x1,y1);const mk=(x,y)=>new Touch({identifier:1,target:tgt,clientX:x,clientY:y});
 const ev=(type,x,y)=>{const t=mk(x,y);const e=new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true});tgt.dispatchEvent(e);return e.defaultPrevented;};
 ev('touchstart',x1,y1);await new Promise(r=>setTimeout(r,hold));let pv=false;for(let i=1;i<=5;i++){pv=ev('touchmove',x1+(x2-x1)*i/5,y1+(y2-y1)*i/5)||pv;}
 const pre=document.querySelectorAll('[data-pre]').length;const endp=ev('touchend',x2,y2);return {pv,pre,endp};}"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':820,'height':1180},has_touch=True); pg=await ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto(U+'#/ANAT/NECK/learn'); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.removeItem('jblhub.v1.ann.ANAT')"); await pg.reload(); await pg.wait_for_timeout(2500)
        li=pg.locator('#t-NECK-0 .c-key li >> nth=0'); await li.evaluate("e=>e.scrollIntoView({block:'center'})"); bb=await li.bounding_box()
        await pg.keyboard.press('h')
        r=await pg.evaluate(JS,[bb['x']+20,bb['y']+12,bb['x']+300,bb['y']+12,350]); print('long-press drag', r, await pg.locator('#stage .rk-h').all_inner_texts())
        r=await pg.evaluate(JS,[bb['x']+20,bb['y']+40,bb['x']+20,bb['y']+300,50]); print('quick swipe (scroll)', r, 'hl count', await pg.locator('#stage .rk-h').count())
        # tap
        li2=pg.locator('#t-NECK-0 .c-key li >> nth=1'); b2=await li2.bounding_box()
        r=await pg.evaluate(JS,[b2['x']+30,b2['y']+12,b2['x']+30,b2['y']+12,60]); print('tap', r, await pg.locator('#stage .rk-h').all_inner_texts())
        print('errs', errs); await b.close()
asyncio.run(main())
