import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import asyncio
from playwright.async_api import async_playwright
U=J.HUB_URL
JS="""async ([x1,y1,x2,y2,hold,tt])=>{const tgt=document.elementFromPoint(x1,y1);const mk=(x,y)=>new Touch(Object.assign({identifier:1,target:tgt,clientX:x,clientY:y},tt?{touchType:tt}:{}));
 const ev=(type,x,y)=>{const t=mk(x,y);const e=new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true});tgt.dispatchEvent(e);return e.defaultPrevented;};
 ev('touchstart',x1,y1);await new Promise(r=>setTimeout(r,hold));let pv=false;for(let i=1;i<=5;i++){pv=ev('touchmove',x1+(x2-x1)*i/5,y1+(y2-y1)*i/5)||pv;}
 const pre=document.querySelectorAll('[data-pre]').length;const endp=ev('touchend',x2,y2);return {pv,pre,endp};}"""
# 이 Chromium의 Touch는 touchType을 받지 않음 → 같은 처리 함수를 부르도록 touches[0].touchType='stylus'를 가진 합성 이벤트(Event + defineProperty)로 흉내
JSP="""async ([x1,y1,x2,y2,hold,tt])=>{const tgt=document.elementFromPoint(x1,y1);const pt=(x,y)=>({identifier:1,target:tgt,clientX:x,clientY:y,touchType:tt});
 const ev=(type,x,y)=>{const e=new Event(type,{bubbles:true,cancelable:true});const t=pt(x,y);Object.defineProperty(e,'touches',{value:type==='touchend'?[]:[t]});Object.defineProperty(e,'changedTouches',{value:[t]});tgt.dispatchEvent(e);return e.defaultPrevented;};
 ev('touchstart',x1,y1);await new Promise(r=>setTimeout(r,hold));let pv=false;if(x2!==x1||y2!==y1)for(let i=1;i<=5;i++){pv=ev('touchmove',x1+(x2-x1)*i/5,y1+(y2-y1)*i/5)||pv;}
 const endp=ev('touchend',x2,y2);return {pv,endp};}"""
fail=[]
def ok(c,msg):
    print(('  OK  ' if c else '  FAIL')+' '+msg)
    if not c: fail.append(msg)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':820,'height':1180},has_touch=True); pg=await ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto(U+'#/ANAT/NECK/learn'); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.removeItem('jblhub.v1.ann.ANAT')"); await pg.reload(); await pg.wait_for_timeout(2500)
        # 픽스처: 첫 카드 본문에서 글이 긴 줄 두 개(원고 구조와 무관 — 항목 div.li든 목록 li든)
        n=await pg.evaluate("""()=>{const L=[...document.querySelectorAll('#stage .tc.open .tbody li, #stage .tc.open .tbody div.li:not(.nolead)')].filter(e=>e.offsetParent&&!e.closest('.noann,.c-exam')&&e.textContent.trim().length>=40&&e.getBoundingClientRect().width>=420);
          L.slice(0,2).forEach((e,i)=>e.setAttribute('data-kt3',i));return L.length;}""")
        ok(n>=2, f'픽스처: 글이 긴 본문 줄 {n}개')
        li=pg.locator('[data-kt3="0"]'); await li.evaluate("e=>e.scrollIntoView({block:'center'})"); bb=await li.bounding_box()
        await pg.keyboard.press('h')
        r=await pg.evaluate(JS,[bb['x']+20,bb['y']+12,bb['x']+300,bb['y']+12,350]); t_=await pg.locator('#stage .rk-h').all_inner_texts(); ok(r['pv'] and len(t_)>=1, f'길게 누른 뒤 끌기 = 형광 {t_}')
        r=await pg.evaluate(JS,[bb['x']+20,bb['y']+40,bb['x']+20,bb['y']+300,50]); ok(not r['pv'] and await pg.locator('#stage .rk-h').count()==len(t_), '그냥 쓸면 스크롤(표시 안 늘어남)')
        # tap
        li2=pg.locator('[data-kt3="1"]'); await li2.evaluate("e=>e.scrollIntoView({block:'center'})"); b2=await li2.bounding_box()
        w=await pg.evaluate("""()=>{const e=document.querySelector('[data-kt3="1"]');const tw=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let t;while(t=tw.nextNode()){if(t.parentElement.closest('.noann,button'))continue;const m=/[A-Za-z가-힣]{4,}/.exec(t.nodeValue);if(!m)continue;
          const r=document.createRange();r.setStart(t,m.index+1);r.setEnd(t,m.index+2);const b=r.getBoundingClientRect();return {x:b.left+b.width/2,y:b.top+b.height/2,w:m[0]};}return null;}""")   # 줄 첫 4자 이상 낱말 가운데
        r=await pg.evaluate(JS,[w['x'],w['y'],w['x'],w['y'],60]); t2=await pg.locator('#stage .rk-h').all_inner_texts(); ok(len(t2)>len(t_) and any(w['w'] in x for x in t2), f"짧게 톡 = 어절 형광 ({w['w']}) {t2}")
        # A07: 길게 누른 뒤 그대로 떼기 = 누르기(tapAt) — 두 번이면 칠했다 지움(전에는 두 번째도 또 칠함) · 짧은 톡 두 번도 0
        NM="document.querySelectorAll('#stage [data-rk]').length"
        await pg.evaluate("localStorage.removeItem('jblhub.v1.ann.ANAT')"); await pg.reload(); await pg.wait_for_timeout(2500)
        await pg.evaluate("""()=>{const L=[...document.querySelectorAll('#stage .tc.open .tbody li, #stage .tc.open .tbody div.li:not(.nolead)')].filter(e=>e.offsetParent&&!e.closest('.noann,.c-exam')&&e.textContent.trim().length>=40&&e.getBoundingClientRect().width>=420);L.slice(0,3).forEach((e,i)=>e.setAttribute('data-kt3',i));}""")
        WORD="""(n)=>{const e=document.querySelector('[data-kt3="'+n+'"]');e.scrollIntoView({block:'center'});const tw=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let t;while(t=tw.nextNode()){if(t.parentElement.closest('.noann,button'))continue;const m=/[A-Za-z가-힣]{4,}/.exec(t.nodeValue);if(!m)continue;
          const r=document.createRange();r.setStart(t,m.index+1);r.setEnd(t,m.index+2);const b=r.getBoundingClientRect();return [b.left+b.width/2,b.top+b.height/2];}return null;}"""
        await pg.keyboard.press('h'); w=await pg.evaluate(WORD,0)
        await pg.evaluate(JS,[w[0],w[1],w[0],w[1],400]); n1=await pg.evaluate(NM); await pg.evaluate(JS,[w[0],w[1],w[0],w[1],400]); n2=await pg.evaluate(NM)
        ok(n1>=1 and n2==0, f'길게 누르기(0.4초) 두 번 → 칠했다 지움 ({n1}→{n2})')
        await pg.evaluate(JS,[w[0],w[1],w[0],w[1],60]); m1=await pg.evaluate(NM); await pg.evaluate(JS,[w[0],w[1],w[0],w[1],60]); m2=await pg.evaluate(NM)
        ok(m1>=1 and m2==0, f'짧은 톡 두 번 → 0 (기존 동작 {m1}→{m2})')
        await pg.keyboard.press('Escape')
        # 펜슬로 바로 칠하기(penDirect — 터치 기기 기본 켬): 모드 없이 펜슬로 끌면 형광펜 1 · 펜슬로 그 자리를 톡 치면 지움 · 손가락은 스크롤
        sup=await pg.evaluate("(()=>{try{return new Touch({identifier:1,target:document.body,clientX:1,clientY:1,touchType:'stylus'}).touchType}catch(e){return String(e)}})()")
        ok(await pg.evaluate("__h.Kit.pen()"), f'터치 기기에서 펜슬로 바로 칠하기 기본 켬 (Touch.touchType 지원: {sup})')
        li=pg.locator('[data-kt3="2"]'); await li.evaluate("e=>e.scrollIntoView({block:'center'})"); b3=await li.bounding_box()
        TJ = JS if sup=='stylus' else JSP
        if True:
            await pg.evaluate(TJ,[b3['x']+20,b3['y']+12,b3['x']+260,b3['y']+12,30,'stylus']); p1=await pg.evaluate("document.querySelectorAll('#stage [data-rk=h]').length")
            ann=await pg.evaluate("Object.values(JSON.parse(localStorage.getItem('jblhub.v1.ann.ANAT')||'{}')).flat().length")
            ok(p1>=1 and ann==1 and not await pg.evaluate("document.body.classList.contains('mode-h')"), f'모드 없이 펜슬로 끌기 → 형광펜 표시 1 (조각 {p1}, 기록 {ann})')
            xy=await pg.evaluate("(()=>{const r=document.querySelector('#stage [data-rk=h]').getBoundingClientRect();return [r.left+Math.min(8,r.width/2),r.top+r.height/2]})()")
            await pg.evaluate(TJ,[xy[0],xy[1],xy[0],xy[1],30,'stylus'])
            ok(await pg.evaluate("document.querySelectorAll('#stage [data-rk]').length")==0, '펜슬로 칠한 곳 톡 → 지움')
            r=await pg.evaluate(TJ,[b3['x']+20,b3['y']+12,b3['x']+260,b3['y']+12,30,'direct'])
            ok(await pg.evaluate("document.querySelectorAll('#stage [data-rk]').length")==0 and not r['pv'], '손가락(direct)으로 끌면 칠하지 않음(스크롤)')
            await pg.evaluate("localStorage.setItem('jblhub.v1.penDirect','false')")
            await pg.evaluate(TJ,[b3['x']+20,b3['y']+12,b3['x']+260,b3['y']+12,30,'stylus'])
            ok(await pg.evaluate("document.querySelectorAll('#stage [data-rk]').length")==0, '설정을 끄면 펜슬도 모드 없이는 칠하지 않음')
            await pg.evaluate("localStorage.removeItem('jblhub.v1.penDirect')")
        ok(not errs, f'콘솔 오류 0 {errs[:3]}'); await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fail else f'FAIL {len(fail)}'); _sys.exit(1 if fail else 0)
