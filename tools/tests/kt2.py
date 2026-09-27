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
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':1000}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto(U+'#/ANAT/MAND/learn'); await pg.wait_for_timeout(2500)
        # 고정 글자 대신 카드에서 고름: 카드 2 = 블록 안에 한 번만 나오는 세 어절(' / '를 끼워 옛 기록 흉내), 카드 3 = 한 번만 나오는 영어 낱말(옛 aid 키로)
        fx=await pg.evaluate("""()=>{const k='jblhub.v1.ann.ANAT';localStorage.setItem(k,'{}');const c2=document.querySelector('#t-MAND-2'),c3=document.querySelector('#t-MAND-3');
          const T2=__h.Kit.textOf(c2),T3=__h.Kit.textOf(c3);let ph=null;for(const li of c2.querySelectorAll('.tbody :is(li,.li)')){const w=li.textContent.trim().split(/\\s+/).filter(x=>/[A-Za-z가-힣]{2}/.test(x));for(let i=0;i+2<w.length&&!ph;i++){const p=w.slice(i,i+3).join(' ');if(T2.split(p).length===2)ph=[w[i],w[i+1]+' '+w[i+2]];}if(ph)break;}
          const w3=(T3.match(/[A-Za-z]{5,}/g)||[]).find(x=>T3.split(x).length===2);if(!ph||!w3||!c3.dataset.alt)return null;const a={};
          a[c2.dataset.aid]=[{t:'h',x:ph[0]+' / '+ph[1],i:0,c:'g'}];a[c3.dataset.alt.split(' ')[0]]=[{t:'b',x:w3,i:0}];localStorage.setItem(k,JSON.stringify(a));return [ph[0],w3,c3.dataset.alt.split(' ')[0]];}""")
        ok(fx is not None, f'픽스처 {fx}')
        await pg.reload(); await pg.wait_for_timeout(2500)
        r=await pg.locator('#t-MAND-2 .rk-h').all_inner_texts(); ok(bool(fx) and len(r)>=1 and fx[0] in ''.join(r), f'느슨한 복원 {r}')
        ok(await pg.locator('#t-MAND-3 .rk-b').count()>=1 and bool(fx) and not await pg.evaluate("(k)=>k in JSON.parse(localStorage.getItem('jblhub.v1.ann.ANAT'))", fx[2] if fx else ''), '옛 aid 표시 이관(옛 키 없어짐)')
        # done(이해함) 이관
        await pg.evaluate("""()=>{const c=document.querySelector('#t-MAND-0');const d={};d[c.dataset.alt]=1;localStorage.setItem('jblhub.v1.done.ANAT',JSON.stringify(d));}""")
        await pg.reload(); await pg.wait_for_timeout(2500); ok(await pg.evaluate("document.querySelector('#t-MAND-0').classList.contains('done')"), '이해함 ✓ 옛 aid → 새 카드 이관')
        ok(not errs, f'콘솔 오류 0 {errs[:3]}'); await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fail else f'FAIL {len(fail)}'); _sys.exit(1 if fail else 0)
