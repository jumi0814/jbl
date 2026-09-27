import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import asyncio
from playwright.async_api import async_playwright
U=J.HUB_URL
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':1000}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto(U+'#/ANAT/MAND/learn'); await pg.wait_for_timeout(2500)
        await pg.evaluate("""()=>{const k='jblhub.v1.ann.ANAT';localStorage.setItem(k,'{}');const c2=document.querySelector('#t-MAND-2'),c3=document.querySelector('#t-MAND-3');const a={};
          a[c2.dataset.aid]=[{t:'h',x:'anterior to masseter / facial a.&v. cross inf. border',i:0,c:'g'}];
          a[c3.dataset.alt]=[{t:'b',x:'chorda tympani',i:0}];localStorage.setItem(k,JSON.stringify(a));}""")
        await pg.reload(); await pg.wait_for_timeout(2500)
        print('fuzzy', await pg.locator('#t-MAND-2 .rk-h').all_inner_texts())
        print('alt migrate', await pg.locator('#t-MAND-3 .rk-b').count(), 'old key left', await pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('jblhub.v1.ann.ANAT'))).some(k=>/:c\\d+$/.test(k))"))
        # done(이해함) 이관
        await pg.evaluate("""()=>{const c=document.querySelector('#t-MAND-0');const d={};d[c.dataset.alt]=1;localStorage.setItem('jblhub.v1.done.ANAT',JSON.stringify(d));}""")
        await pg.reload(); await pg.wait_for_timeout(2500); print('done migrate', await pg.evaluate("document.querySelector('#t-MAND-0').classList.contains('done')"), await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"MAND\"] small').textContent"))
        print('errs', errs); await b.close()
asyncio.run(main())
