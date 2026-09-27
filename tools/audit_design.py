import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); import jblpaths as J  # tools/localize.py
import asyncio, json, sys
from playwright.async_api import async_playwright
U=J.HUB_URL
SUBJ={'GERI':['HARD','OHQ','ENDO','BLE','SAL','PAIN','PSY'],'OMS1':['DD1','DD2','DD3','DX','EXT','LOAD','REP'],'CONS':['WHT','CRK','DHS','INL','ANT','ADH','FRC'],'IMPL':['HIS','OSS','PATH','BIO','PRO','PART','GRAFT'],'ANAT':['NECK','NV','LIP','MAND','PAR','MAX','TMJ'],'PHARM':['RX','XE','BT','ACU','CHR','HM','DS']}
JS=r"""()=>{
function rgb(s){const m=s.match(/rgba?\(([^)]+)\)/);if(!m)return null;const p=m[1].split(',').map(x=>parseFloat(x));return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1};}
function lum(c){const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b);}
function bgOf(el){while(el){const cs=getComputedStyle(el);if(cs.backgroundImage&&cs.backgroundImage!=='none')return null;const c=rgb(cs.backgroundColor);if(c&&c.a>0.5)return c;el=el.parentElement;}return {r:246,g:244,b:239,a:1};}
const bad=[];const seen=new Set();
document.querySelectorAll('#stage *, #hub *, #subj *').forEach(el=>{
 if(!el.offsetParent&&getComputedStyle(el).position!=='fixed')return;
 const own=[...el.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim().length>1).map(n=>n.textContent.trim()).join(' ');
 if(!own)return;
 const cs=getComputedStyle(el); const fg=rgb(cs.color); if(!fg||fg.a<0.3)return;
 const bg=bgOf(el); if(!bg)return; const L1=lum(fg),L2=lum(bg); const cr=(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
 if(cr<3.0){const k=el.tagName+'.'+el.className; if(!seen.has(k)){seen.add(k);bad.push([k.slice(0,50),own.slice(0,40),cr.toFixed(2)]);}}
});
const longs=[];
document.querySelectorAll('#stage .li, #stage .klist li, #stage .co > div, #stage .exlist li, #stage ol.circ li, #stage .ab li, #stage td').forEach(el=>{
 if(!el.offsetParent)return; const t=el.innerText.trim(); if(t.length>230 && !el.querySelector('li')) longs.push(t.slice(0,90)+' …['+t.length+']');
});
const ov=document.documentElement.scrollWidth>document.documentElement.clientWidth;
return {bad,longs:longs.slice(0,40),nlong:longs.length,ov};
}"""
CHK=r"""()=>{const cs=[...document.querySelectorAll('#cards .qc')];const was=cs.map(c=>c.classList.contains('open'));cs.forEach(c=>c.classList.add('open'));const longs=[];let all=0;
 /* 덩어리 = 그 요소가 직접 가진 글(안의 목록·블록·인용 칩 줄은 따로 셈) */
 const leaf=el=>{const c=el.cloneNode(true);c.querySelectorAll('ul,ol,div,.cites,button').forEach(x=>x.remove());return c.textContent.replace(/\s+/g,' ').trim();};
 document.querySelectorAll('#cards .ab.chk li, #cards .ab.chk div, #cards .ab.more li, #cards .ab.more div').forEach(el=>{if(!el.offsetParent)return;all++;const t=leaf(el);if(t.length>230)longs.push(el.closest('.qc').dataset.id+' '+t.slice(0,80)+' …['+t.length+']');});
 cs.forEach((c,i)=>c.classList.toggle('open',was[i]));return {n:longs.length,all,longs:longs.slice(0,20)};}"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':1000}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:150]))
        allbad={}; totlong=0; longs=[]
        await pg.goto(U); await pg.wait_for_timeout(2000)
        r=await pg.evaluate(JS); 
        for x in r['bad']: allbad.setdefault(x[0],(x[1],x[2],'hub'))
        for s,ls in SUBJ.items():
            await pg.goto('about:blank'); await pg.goto(f'{U}#/{s}/_home'); await pg.wait_for_timeout(2400)
            for view in ['_home','_jb','_sum','_tbl','_pred','_led']:
                await pg.evaluate('d=>document.querySelector(`#side .dbtn[data-d="${d}"]`)?.click()', view); await pg.wait_for_timeout(700)
                if view=='_jb':
                    # 대조·주변부 덩어리 검사 — 모든 카드의 답을 펼쳐 .ab.chk li·.ab.chk .note·.ab.more li
                    rc=await pg.evaluate(CHK); totlong+=rc['n']; longs+=[s+'/_jb/chk: '+t for t in rc['longs']]; print('  CHUNK',s,'.ab.chk/.ab.more 230자 넘는 덩어리',rc['n'],'/',rc['all'])
                    await pg.evaluate("document.querySelectorAll('#cards [data-tog]').forEach((b,i)=>{if(i<8)b.click()})"); await pg.wait_for_timeout(300)
                r=await pg.evaluate(JS)
                for x in r['bad']: allbad.setdefault(x[0],(x[1],x[2],s+view))
                totlong+=r['nlong']; longs+= [s+view+': '+t for t in r['longs'][:3]]
                if r['ov']: print('OVERFLOW',s,view)
            for k in ls:
                await pg.evaluate('d=>document.querySelector(`#side .dbtn[data-d="${d}"]`)?.click()', k); await pg.wait_for_timeout(900)
                for t in ['learn','sum','tbl','jb','pred','flash']:
                    await pg.evaluate('d=>document.querySelector(`#dtabs button[data-t="${d}"]`)?.click()', t); await pg.wait_for_timeout(350)
                    r=await pg.evaluate(JS)
                    for x in r['bad']: allbad.setdefault(x[0],(x[1],x[2],f'{s}/{k}/{t}'))
                    totlong+=r['nlong']; longs+= [f'{s}/{k}/{t}: '+x for x in r['longs']]
                    if r['ov']: print('OVERFLOW',s,k,t)
        print('LOW CONTRAST', len(allbad))
        for k,v in allbad.items(): print(' ',k,'|',v)
        print('LONG', totlong)
        json.dump(longs,open(_os.path.join(J.TMP, 'longs.json'),'w'),ensure_ascii=False,indent=0)
        for x in longs[:60]: print(' ',x[:170])
        print('errs',errs[:3]); await b.close()
asyncio.run(main())
