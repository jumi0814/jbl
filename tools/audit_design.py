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
/* U27: 채운 빨강 배경(글자 있는 요소) · 13px 미만 글자 대비 4.5 미만 */
const redfill=[],small=[];const seenR=new Set(),seenS=new Set();
document.querySelectorAll('#stage *, #home *, #side *, #hero *').forEach(el=>{if(!el.offsetParent)return;const own=[...el.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim()).length;if(!own)return;const cs=getComputedStyle(el);
 const c=rgb(cs.backgroundColor);if(c&&c.a>0.5&&c.r>=150&&c.g<=90&&c.b<=90){const k=el.tagName+'.'+el.className;if(!seenR.has(k)){seenR.add(k);redfill.push(k.slice(0,50));}}
 if(parseFloat(cs.fontSize)<13){const fg=rgb(cs.color),bg=bgOf(el);if(fg&&bg&&fg.a>0.3){const L1=lum(fg),L2=lum(bg),cr=(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);if(cr<4.5){const k=el.tagName+'.'+el.className;if(!seenS.has(k)){seenS.add(k);small.push([k.slice(0,50),el.textContent.trim().slice(0,30),cr.toFixed(2)]);}}}}});
const longs=[];
document.querySelectorAll('#stage .li, #stage .klist li, #stage .co > div, #stage .exlist li, #stage ol.circ li, #stage .ab li, #stage td').forEach(el=>{
 if(!el.offsetParent)return; const t=el.innerText.trim(); if(t.length>230 && !el.querySelector('li')) longs.push(t.slice(0,90)+' …['+t.length+']');
});
const ov=document.documentElement.scrollWidth>document.documentElement.clientWidth;
return {bad,longs:longs.slice(0,40),nlong:longs.length,ov,redfill,small};
}"""
CHK=r"""()=>{const cs=[...document.querySelectorAll('#cards .qc')];const was=cs.map(c=>c.classList.contains('open'));cs.forEach(c=>c.classList.add('open'));const longs=[];let all=0;
 /* 덩어리 = 그 요소가 직접 가진 글(안의 목록·블록·인용 칩 줄은 따로 셈) */
 const leaf=el=>{const c=el.cloneNode(true);c.querySelectorAll('ul,ol,div,.cites,button').forEach(x=>x.remove());return c.textContent.replace(/\s+/g,' ').trim();};
 document.querySelectorAll('#cards .ab.chk li, #cards .ab.chk div, #cards .ab.more li, #cards .ab.more div').forEach(el=>{if(!el.offsetParent)return;all++;const t=leaf(el);if(t.length>230)longs.push(el.closest('.qc').dataset.id+' '+t.slice(0,80)+' …['+t.length+']');});
 cs.forEach((c,i)=>c.classList.toggle('open',was[i]));return {n:longs.length,all,longs:longs.slice(0,20)};}"""
OVERLAP=r"""()=>{const bad=[];document.querySelectorAll('#stage .ln.li, #stage .mtx .ci, #stage .li').forEach(el=>{if(!el.offsetParent)return;const b=getComputedStyle(el,'::before');if(b.content==='none'||b.display==='none'||b.content==='normal'||b.position!=='absolute')return;
 const cs=getComputedStyle(el);const pad=parseFloat(cs.paddingLeft)+(parseFloat(cs.textIndent)||0);const L=parseFloat(b.left)||0,W=parseFloat(b.width)||0;if(L+W>pad-1)bad.push(el.className+': '+el.textContent.trim().slice(0,20));});return bad.slice(0,3);}"""
TEAL=r"""(sid)=>{if(sid==='OMS1'||sid==='PHARM')return [];const T=['rgb(14, 72, 70)','rgb(23, 63, 61)','rgb(225, 238, 235)','rgb(195, 218, 213)','rgb(186, 215, 210)','rgb(10, 51, 50)'];const bad=new Set();
 document.querySelectorAll('#stage *, #hero, #hero *, #side *').forEach(el=>{if(!el.offsetParent&&el.id!=='hero')return;const cs=getComputedStyle(el);for(const v of [cs.color,cs.backgroundColor,cs.borderTopColor,cs.borderLeftColor,cs.backgroundImage])if(T.some(t=>v.indexOf(t)>=0))bad.add(el.tagName+'.'+String(el.className).slice(0,30));});return [...bad].slice(0,5);}"""
async def ipad_sweep(b):
    """아이패드 세로(820×1180)·가로(1180×820): 모든 과목 문서·강의 학습/정리표 — 페이지 가로 밀림 · 목록 점이 첫 글자를 가림 · 과목색이 아닌 청록(OMS1·PHARM 밖)"""
    bad=[]
    for vw,vh in [(820,1180),(1180,820)]:
        pg=await (await b.new_context(viewport={'width':vw,'height':vh},has_touch=vw<1000)).new_page()
        for s,ls in SUBJ.items():
            for d in ['_home','_jb','_sum','_tbl','_pred','_led']+[f'{k}/learn' for k in ls]+[f'{k}/sum' for k in ls]:
                await pg.goto('about:blank'); await pg.goto(f'{U}#/{s}/{d}'); await pg.wait_for_timeout(500)
                if d=='_jb': await pg.evaluate("document.querySelector('#frev')&&document.querySelector('#frev').click()"); await pg.wait_for_timeout(200)
                ov=await pg.evaluate('document.documentElement.scrollWidth-innerWidth')
                if ov>1: bad.append(f'OVERFLOW {vw} {s}/{d} {ov}px')
                o=await pg.evaluate(OVERLAP)
                if o: bad.append(f'OVERLAP {vw} {s}/{d} {o}')
                if vw==820:
                    t=await pg.evaluate(TEAL, s)
                    if t: bad.append(f'TEAL {s}/{d} {t}')
        await pg.close()
    return bad
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':1000}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:150]))
        allbad={}; totlong=0; longs=[]; RED={}; SMALL={}
        def acc(r, where):
            for x in r.get('redfill', []): RED.setdefault(x, where)
            for x in r.get('small', []): SMALL.setdefault(x[0], (x[1], x[2], where))
        await pg.goto(U); await pg.wait_for_timeout(2000)
        r=await pg.evaluate(JS); acc(r,'hub')
        for x in r['bad']: allbad.setdefault(x[0],(x[1],x[2],'hub'))
        for s,ls in SUBJ.items():
            await pg.goto('about:blank'); await pg.goto(f'{U}#/{s}/_home'); await pg.wait_for_timeout(2400)
            for view in ['_home','_jb','_sum','_tbl','_pred','_led']:
                await pg.evaluate('d=>document.querySelector(`#side .dbtn[data-d="${d}"]`)?.click()', view); await pg.wait_for_timeout(700)
                if view=='_jb':
                    # 대조·주변부 덩어리 검사 — 모든 카드의 답을 펼쳐 .ab.chk li·.ab.chk .note·.ab.more li
                    rc=await pg.evaluate(CHK); totlong+=rc['n']; longs+=[s+'/_jb/chk: '+t for t in rc['longs']]; print('  CHUNK',s,'.ab.chk/.ab.more 230자 넘는 덩어리',rc['n'],'/',rc['all'])
                    await pg.evaluate("document.querySelectorAll('#cards [data-tog]').forEach((b,i)=>{if(i<8)b.click()})"); await pg.wait_for_timeout(300)
                r=await pg.evaluate(JS); acc(r, s+view)
                for x in r['bad']: allbad.setdefault(x[0],(x[1],x[2],s+view))
                totlong+=r['nlong']; longs+= [s+view+': '+t for t in r['longs'][:3]]
                if r['ov']: print('OVERFLOW',s,view); errs.append(f'OVERFLOW 1280 {s}/{view}')
            for k in ls:
                await pg.evaluate('d=>document.querySelector(`#side .dbtn[data-d="${d}"]`)?.click()', k); await pg.wait_for_timeout(900)
                for t in ['learn','sum','tbl','jb','pred','flash']:
                    await pg.evaluate('d=>document.querySelector(`#dtabs button[data-t="${d}"]`)?.click()', t); await pg.wait_for_timeout(350)
                    r=await pg.evaluate(JS); acc(r, f'{s}/{k}/{t}')
                    for x in r['bad']: allbad.setdefault(x[0],(x[1],x[2],f'{s}/{k}/{t}'))
                    totlong+=r['nlong']; longs+= [f'{s}/{k}/{t}: '+x for x in r['longs']]
                    if r['ov']: print('OVERFLOW',s,k,t); errs.append(f'OVERFLOW 1280 {s}/{k}/{t}')
        print('RED FILL', len(RED))
        for k,v in RED.items(): print(' ',k,'|',v)
        print('SMALL LOW CONTRAST(<13px, <4.5)', len(SMALL))
        for k,v in SMALL.items(): print(' ',k,'|',v)
        print('LOW CONTRAST', len(allbad))
        for k,v in allbad.items(): print(' ',k,'|',v)
        print('LONG', totlong)
        json.dump(longs,open(_os.path.join(J.TMP, 'longs.json'),'w'),ensure_ascii=False,indent=0)
        for x in longs[:60]: print(' ',x[:170])
        IP=await ipad_sweep(b)
        print('IPAD SWEEP (가로 밀림·점 겹침·청록)', len(IP))
        for x in IP[:40]: print(' ',x)
        print('errs',errs[:3]); await b.close()
        return not IP and not errs
ok_=asyncio.run(main())
print('RESULT', 'PASS' if ok_ else 'FAIL'); sys.exit(0 if ok_ else 1)
