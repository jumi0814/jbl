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
CHK=r"""()=>{const cs=[...document.querySelectorAll('#cards .qc')];const was=cs.map(c=>c.className);const dw=[...document.querySelectorAll('#cards details')].map(d=>[d,d.open]);cs.forEach(c=>c.classList.add('open','deep'));document.querySelectorAll('#cards details.ab').forEach(d=>d.open=true);const longs=[];let all=0;
 /* 덩어리 = 그 요소가 직접 가진 글(안의 목록·블록·인용 칩 줄은 따로 셈) */
 const leaf=el=>{const c=el.cloneNode(true);c.querySelectorAll('ul,ol,div,.cites,button').forEach(x=>x.remove());return c.textContent.replace(/\s+/g,' ').trim();};
 document.querySelectorAll('#cards .ab.chk li, #cards .ab.chk div, #cards .ab.more li, #cards .ab.more div').forEach(el=>{if(!el.offsetParent)return;all++;const t=leaf(el);if(t.length>230)longs.push(el.closest('.qc').dataset.id+' '+t.slice(0,80)+' …['+t.length+']');});
 /* ux2 F09 EMPTY BULLET — 답을 모두 펼친 뒤(2단계) 글머리가 보이는 li인데 앞에 글 없이 첫 자식이 목록(ul/ol) = 빈 점 한 줄 · raw = CSS 안전망을 빼고 구조만 센 것(참고) */
 let eb=0,raw=0;const ebx=[];document.querySelectorAll('#cards .ans li').forEach(li=>{if(!li.offsetParent)return;const f=[...li.childNodes].find(n=>n.nodeType===1||(n.nodeType===3&&n.textContent.trim()));if(!f||f.nodeType!==1||!/^(UL|OL)$/.test(f.tagName))return;if(f.classList.contains('kflow'))return;raw++;const cs_=getComputedStyle(li);if(cs_.display==='list-item'&&cs_.listStyleType!=='none'){eb++;if(ebx.length<5)ebx.push(li.closest('.qc').dataset.id);}});
 cs.forEach((c,i)=>c.className=was[i]);dw.forEach(([d,o])=>d.open=o);return {n:longs.length,all,longs:longs.slice(0,20),eb,raw,ebx};}"""
OVERLAP=r"""()=>{const bad=[];document.querySelectorAll('#stage .ln.li, #stage .mtx .ci, #stage .li').forEach(el=>{if(!el.offsetParent)return;const b=getComputedStyle(el,'::before');if(b.content==='none'||b.display==='none'||b.content==='normal'||b.position!=='absolute')return;
 const cs=getComputedStyle(el);const pad=parseFloat(cs.paddingLeft)+(parseFloat(cs.textIndent)||0);const L=parseFloat(b.left)||0,W=parseFloat(b.width)||0;if(L+W>pad-1)bad.push(el.className+': '+el.textContent.trim().slice(0,20));});return bad.slice(0,3);}"""
TEAL=r"""(sid)=>{if(sid==='OMS1'||sid==='PHARM')return [];const T=['rgb(14, 72, 70)','rgb(23, 63, 61)','rgb(225, 238, 235)','rgb(195, 218, 213)','rgb(186, 215, 210)','rgb(10, 51, 50)'];const bad=new Set();
 document.querySelectorAll('#stage *, #hero, #hero *, #side *').forEach(el=>{if(!el.offsetParent&&el.id!=='hero')return;const cs=getComputedStyle(el);for(const v of [cs.color,cs.backgroundColor,cs.borderTopColor,cs.borderLeftColor,cs.backgroundImage])if(T.some(t=>v.indexOf(t)>=0))bad.add(el.tagName+'.'+String(el.className).slice(0,30));});return [...bad].slice(0,5);}"""
REDJS=r"""()=>{const isRed=el=>{const c=(getComputedStyle(el).color.match(/\d+/g)||[0,0,0]).map(Number);return c[0]>=150&&c[1]<=90&&c[2]<=90;};let tot=0,red=0;
 document.querySelectorAll('#stage .tc').forEach(c=>{const w=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){const p=n.parentElement;if(!p||!p.offsetParent||p.closest('button,.noann,.chip'))continue;const L=n.nodeValue.replace(/\s/g,'').length;if(!L)continue;tot+=L;if(isRed(p))red+=L;}});
 const it=[...document.querySelectorAll('#stage .tc .tbody .li')].filter(e=>e.offsetParent),ri=it.filter(e=>[...e.querySelectorAll('.k')].some(k=>k.offsetParent&&isRed(k))).length;
 return {chars:tot?Math.round(red/tot*1000)/10:0,items:it.length?Math.round(ri/it.length*1000)/10:0,spans:document.querySelectorAll('#stage .tc .k').length,red:[...document.querySelectorAll('#stage .tc .k')].filter(isRed).length};}"""
RED_REP=[('OMS1','EXT'),('GERI','PAIN'),('PHARM','HM'),('ANAT','MAND'),('CONS','WHT'),('IMPL','GRAFT')]
async def red_share(b):
    """ux2 D06 RED SHARE — 대표 6개 강의 학습 탭(1280): 빨간 글자 비율(보이는 카드 글자 중 빨강) · 빨강이 든 항목(.li) 비율 · 빨간 span/전체 .k (목표 글자 ≤10%·항목 ≤45% — 보고용, 판정에는 안 씀)"""
    pg=await b.new_page(viewport={'width':1280,'height':900}); out=[]
    for s,k in RED_REP:
        await pg.goto('about:blank'); await pg.goto(f'{U}#/{s}/{k}/learn'); await pg.wait_for_timeout(700)
        r=await pg.evaluate(REDJS); out.append((s,k,r))
    await pg.close(); return out
async def sum_rows(b):
    """ux2 E02 정리표(요약 모드, 1280·사이드바 자동 접힘) 행 높이 400px 넘는 행 — 경고(판정에는 안 씀)"""
    pg=await b.new_page(viewport={'width':1280,'height':900}); out=[]
    for s,ls in SUBJ.items():
        for k in ls:
            await pg.goto('about:blank'); await pg.goto(f'{U}#/{s}/{k}/sum'); await pg.wait_for_timeout(400)
            r=await pg.evaluate("[...document.querySelectorAll('#stage .msum table.mtx>tbody>tr[data-aid]')].filter(r=>r.offsetHeight>400).map(r=>r.id+' '+r.offsetHeight)")
            out+= [f'{s}/{k} {x}' for x in r]
    await pg.close(); return out
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
                if d=='_led':   # ux2 E12 기출 대장 — 문서 가로 넘침 정확히 0
                    ov2=await pg.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
                    if ov2: bad.append(f'OVERFLOW(led) {vw} {s}/{d} {ov2}px')
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
        allbad={}; totlong=0; longs=[]; RED={}; SMALL={}; EMPTY={}
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
                    EMPTY[s]=rc['eb']; print('  EMPTY BULLET',s,rc['eb'],'(구조만',rc['raw'],')',rc['ebx'])
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
        print('EMPTY BULLET (답 모두 펼침 뒤 빈 글머리 — 0이어야 함)', sum(EMPTY.values()), EMPTY)
        if sum(EMPTY.values()): errs.append(f'EMPTY BULLET {EMPTY}')
        print('RED FILL', len(RED))
        for k,v in RED.items(): print(' ',k,'|',v)
        print('SMALL LOW CONTRAST(<13px, <4.5)', len(SMALL))
        for k,v in SMALL.items(): print(' ',k,'|',v)
        print('LOW CONTRAST', len(allbad))
        for k,v in allbad.items(): print(' ',k,'|',v)
        print('LONG', totlong)
        json.dump(longs,open(_os.path.join(J.TMP, 'longs.json'),'w'),ensure_ascii=False,indent=0)
        for x in longs[:60]: print(' ',x[:170])
        TR=await sum_rows(b)
        print('SUM ROW (정리표 요약 모드 행 높이 > 400px — 경고)', len(TR))
        for x in TR[:20]: print(' ',x)
        RS=await red_share(b)
        print('RED SHARE (빨간 글자 % · 빨강이 든 항목 % · 빨간 span/전체 .k — 목표 ≤10% · ≤45%)')
        for s_,k_,r_ in RS: print(f"  {s_}/{k_}: 글자 {r_['chars']}% · 항목 {r_['items']}% · span {r_['red']}/{r_['spans']}{'' if r_['chars']<=10 and r_['items']<=45 else '  (목표 초과)'}")
        IP=await ipad_sweep(b)
        print('IPAD SWEEP (가로 밀림·점 겹침·청록)', len(IP))
        for x in IP[:40]: print(' ',x)
        print('errs',errs[:3]); await b.close()
        return not IP and not errs
ok_=asyncio.run(main())
print('RESULT', 'PASS' if ok_ else 'FAIL'); sys.exit(0 if ok_ else 1)
