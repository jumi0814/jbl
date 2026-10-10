import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); import jblpaths as J  # tools/localize.py
import asyncio, json, sys
from playwright.async_api import async_playwright
U=J.HUB_URL
SUBJ={'GERI':['HARD','OHQ','ENDO','BLE','SAL','PAIN','PSY'],'OMS1':['DD1','DD2','DD3','DX','EXT','LOAD','REP'],'CONS':['WHT','CRK','DHS','INL','ANT','ADH','FRC'],'IMPL':['HIS','OSS','PATH','BIO','PRO','PART','GRAFT'],'ANAT':['NECK','NV','LIP','MAND','PAR','MAX','TMJ'],'PHARM':['RX','XE','BT','ACU','CHR','HM','DS']}
if _os.path.exists(_os.path.join(J.DOCS,'packs','ESTH.js')): SUBJ['ESTH']=['INT','FUN','PLAN','SPE','COL','MAT','VEN']   # 심미치과학(10-03) — 팩이 생긴 뒤부터 감사
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
TEAL=r"""(sid)=>{if(sid==='OMS1')return [];   /* ux3 R3 약물치료 과목 색이 자두색이 되어 청록 예외는 구강외과1만 */const T=['rgb(14, 72, 70)','rgb(23, 63, 61)','rgb(225, 238, 235)','rgb(195, 218, 213)','rgb(186, 215, 210)','rgb(10, 51, 50)'];const bad=new Set();
 document.querySelectorAll('#stage *, #hero, #hero *, #side *').forEach(el=>{if(!el.offsetParent&&el.id!=='hero')return;const cs=getComputedStyle(el);for(const v of [cs.color,cs.backgroundColor,cs.borderTopColor,cs.borderLeftColor,cs.backgroundImage])if(T.some(t=>v.indexOf(t)>=0))bad.add(el.tagName+'.'+String(el.className).slice(0,30));});return [...bad].slice(0,5);}"""
REDJS=r"""()=>{const isRed=el=>{const c=(getComputedStyle(el).color.match(/\d+/g)||[0,0,0]).map(Number);return c[0]>=150&&c[1]<=90&&c[2]<=90;};let tot=0,red=0;
 document.querySelectorAll('#stage .tc').forEach(c=>{const w=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){const p=n.parentElement;if(!p||!p.offsetParent||p.closest('button,.noann,.chip'))continue;const L=n.nodeValue.replace(/\s/g,'').length;if(!L)continue;tot+=L;if(isRed(p))red+=L;}});
 const it=[...document.querySelectorAll('#stage .tc .tbody .li')].filter(e=>e.offsetParent),ri=it.filter(e=>[...e.querySelectorAll('.k')].some(k=>k.offsetParent&&isRed(k))).length;
 return {chars:tot?Math.round(red/tot*1000)/10:0,items:it.length?Math.round(ri/it.length*1000)/10:0,spans:document.querySelectorAll('#stage .tc .k').length,red:[...document.querySelectorAll('#stage .tc .k')].filter(isRed).length};}"""
RED_REP=[('OMS1','EXT'),('GERI','PAIN'),('PHARM','HM'),('ANAT','MAND'),('CONS','WHT'),('IMPL','GRAFT')]
if 'ESTH' in SUBJ: RED_REP.append(('ESTH','FUN'))
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
# ---- ux2 fixB 화면 검사(VIS01·VIS02·VIS04·VIS05·VIS08·V12) ----
PARTIAL=r"""()=>{/* 줄임(overflow:hidden) 칸의 아래 끝에 걸쳐 반쯤 잘린 줄 — 정리표 ★·⚡·세부 */const bad=[];
 document.querySelectorAll('#stage .msum td.mt .mexb, #stage .msum td.mt .ex-q, #stage .msum td.mt .ex-a, #stage .msum td.mt .ex-ab, #stage .msum td.mnote .ci, #stage .msum td.md .sline').forEach(el=>{if(!el.offsetParent)return;const cs=getComputedStyle(el);if(cs.overflow!=='hidden'&&cs.overflowY!=='hidden')return;const b=el.getBoundingClientRect();if(!b.height)return;
  const r=document.createRange();r.selectNodeContents(el);const cut=[...r.getClientRects()].some(x=>x.height>4&&x.width>2&&x.top<b.bottom-2&&x.bottom>b.bottom+2);if(cut)bad.push((el.closest('tr')||{}).id+' '+el.className);});return bad;}"""
STOPEN=r"""()=>{const f=document.querySelector('#sumtop');if(!f)return -1;f.querySelectorAll('.stbl.stoff').forEach(t=>t.classList.remove('stoff'));return f.querySelectorAll('.stbl').length;}"""
STOV=r"""()=>[...document.querySelectorAll('#sumtop .tblwrap.stbl')].filter(w=>{const x=w.querySelector('.tscroll')||w,t=w.querySelector('table');return t&&t.scrollWidth>x.clientWidth+1;}).map(w=>(w.querySelector('.tbt')||w).textContent.slice(0,30)+' +'+(w.querySelector('table').scrollWidth-(w.querySelector('.tscroll')||w).clientWidth))"""
DBL=r"""()=>{/* 칸 점(::before)이 보이는데 첫 자식이 목록(ul/ol) = 점 두 개 */const bad=[];document.querySelectorAll('#stage .ci').forEach(el=>{if(!el.offsetParent)return;const b=getComputedStyle(el,'::before');if(b.display==='none'||b.content==='none'||b.content==='normal')return;const f=el.firstElementChild;if(f&&/^(UL|OL)$/.test(f.tagName)&&!el.firstChild.textContent.trim().length)bad.push(el.textContent.trim().slice(0,30));});return bad.slice(0,5);}"""
MIDW=r"""()=>{/* 영어 낱말이 글자 사이에서 줄바꿈(Lambdo|id) — 보이는 표·카드 글자 */let n=0;const ex=[];const w=document.createTreeWalker(document.querySelector('#stage'),NodeFilter.SHOW_TEXT);let t;const r=document.createRange();
 while(t=w.nextNode()){const v=t.nodeValue;if(!/[A-Za-z]{2}/.test(v)||!t.parentElement||!t.parentElement.offsetParent)continue;r.selectNodeContents(t);if(r.getClientRects().length<2)continue;let prev=null;
  for(let i=0;i<v.length;i++){r.setStart(t,i);r.setEnd(t,i+1);const b=r.getClientRects()[0];if(!b)continue;if(prev&&b.top>prev.top+4&&/[A-Za-z]/.test(prev.ch)&&/[A-Za-z]/.test(v[i])){n++;if(ex.length<3)ex.push(v.slice(Math.max(0,i-8),i)+'|'+v.slice(i,i+6));}prev={top:b.top,ch:v[i]};}}return {n,ex};}"""
SMALLT=r"""()=>[...document.querySelectorAll('button,[role=button],summary,select')].filter(e=>{if(!e.offsetParent||e.closest('#help,.pop:not(.on)'))return false;const r=e.getBoundingClientRect();return r.width>0&&(r.height<40||r.width<40);}).length"""
REDC=r"""()=>{const isRed=el=>{const c=(getComputedStyle(el).color.match(/\d+/g)||[0,0,0]).map(Number);return c[0]>=150&&c[1]<=90&&c[2]<=90;};let T=0,R=0;const hi=[];
 document.querySelectorAll('#stage .tc').forEach(c=>{let tot=0,red=0;const w=document.createTreeWalker(c.querySelector('.tbody')||c,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){const p=n.parentElement;if(!p||!p.offsetParent||p.closest('button,.noann,.chip,figure,.figs,.c-exam'))continue;const L=n.nodeValue.replace(/\s/g,'').length;if(!L)continue;tot+=L;if(p.closest('.k:not(.k2)')&&isRed(p))red+=L;}
  T+=tot;R+=red;if(tot>80&&red/tot>0.30)hi.push(((c.querySelector('.thead .en')||c).textContent.trim().slice(0,34))+' '+Math.round(red/tot*100)+'%');});return {avg:T?Math.round(R/T*1000)/10:0,hi};}"""
async def fixb_sweep(b):
    """정리표 반쯤 잘린 줄(터치 1180·1366 · 맥 1280) = 판정 · 820 전체정리표 가로 넘침 = 판정 · 점 두 개 = 판정 · 영어 낱말 중간 끊김·40px 미만 누름 자리·빨강 비율(원고) = 보고"""
    bad=[]; rep=[]
    for vw,vh,tch in [(1180,820,True),(1366,1024,True),(1280,900,False),(820,1180,True)]:
        pg=await (await b.new_context(viewport={'width':vw,'height':vh},has_touch=tch)).new_page(); mid=0; mex=[]
        for s,ls in SUBJ.items():
            for k in ls:
                await pg.goto('about:blank'); await pg.goto(f'{U}#/{s}/{k}/sum'); await pg.wait_for_timeout(450)
                if vw!=820:
                    pl=await pg.evaluate(PARTIAL)
                    if pl: bad.append(f'PARTIAL LINE {vw}{"t" if tch else ""} {s}/{k} {len(pl)} {pl[:2]}')
                if vw==820:
                    n=await pg.evaluate(STOPEN)
                    if n>0:
                        await pg.wait_for_timeout(350); ov=await pg.evaluate(STOV)
                        if ov: bad.append(f'SUMTOP OVERFLOW 820 {s}/{k} {ov}')
                d=await pg.evaluate(DBL)
                if d: bad.append(f'DOUBLE BULLET {vw} {s}/{k} {d}')
                if vw in (1180,1280):
                    m=await pg.evaluate(MIDW); mid+=m['n']; mex+=[f'{s}/{k} {x}' for x in m['ex']][:1]
        if vw in (1180,1280): rep.append(f'MIDWORD {vw} 정리표 영어 낱말 중간 줄바꿈 {mid} {mex[:4]}')
        if vw==820:
            for h in ['#/','#/OMS1/_home','#/OMS1/DD1/learn','#/OMS1/DD1/sum','#/OMS1/_sum','#/OMS1/_jb/_jb']:
                await pg.goto('about:blank'); await pg.goto(U+h); await pg.wait_for_timeout(600)
                rep.append(f'TOUCH<40 820 {h} {await pg.evaluate(SMALLT)}')
        await pg.close()
    pg=await b.new_page(viewport={'width':1280,'height':900}); hi=[]; avg=[]
    for s,ls in SUBJ.items():
        for k in ls:
            await pg.goto('about:blank'); await pg.goto(f'{U}#/{s}/{k}/learn'); await pg.wait_for_timeout(500)
            r=await pg.evaluate(REDC); avg.append((r['avg'],f'{s}/{k}')); hi+=[f'{s}/{k} {x}' for x in r['hi']]
    await pg.close()
    avg.sort(reverse=True); rep.append(f"RED RATIO 강의 평균 20% 초과 {[f'{n} {a}%' for a,n in avg if a>20]} · 카드 30% 초과 {len(hi)} {hi[:12]} (원고 — 보고만)")
    return bad, rep
async def ipad_sweep(b):
    """아이패드 세로(820×1180)·가로(1180×820): 모든 과목 문서·강의 학습/정리표 — 페이지 가로 밀림 · 목록 점이 첫 글자를 가림 · 과목색이 아닌 청록(OMS1 밖)"""
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
# ---- ux3 트랙3 K·N 화면 검사 ----
KEYCH=r"""()=>{/* 🔑 상자(.c-key .kb)·정리표 🔑 칸(.mkey)의 '한 덩어리로 흐르는 글자'(가장 가까운 block·list-item·inline-block 조상 단위, 보이는 글자만) 중 150자·80자 넘는 수 */
 let n150=0,n80=0;const blk=el=>{while(el){const d=getComputedStyle(el).display;if(d!=='inline'&&d!=='contents')return el;el=el.parentElement;}return null;};
 document.querySelectorAll('#stage .c-key .kb, #stage .mkey').forEach(R=>{const M=new Map();const w=document.createTreeWalker(R,NodeFilter.SHOW_TEXT);let t;while(t=w.nextNode()){const p=t.parentElement;if(!p||!p.getClientRects().length)continue;const b=blk(p);M.set(b,(M.get(b)||'')+t.nodeValue);}
  M.forEach(v=>{const L=v.replace(/\s+/g,' ').trim().length;if(L>150)n150++;if(L>80)n80++;});});return [n150,n80];}"""
BLANKCR=r"""()=>{/* 빈칸 5색 가린 상태 밑줄 대 바탕 대비(3.0↑) · 인쇄는 따로 */const lum=c=>{const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2]);};const rgb=s=>(s.match(/\d+(\.\d+)?/g)||[]).slice(0,3).map(Number);
 const box=document.querySelector('#stage')||document.body,o={};for(const c of ['n','u','g','p','v']){const e=document.createElement('span');e.className='rk-b'+(c!=='n'?' rkb-'+c:'');e.textContent='가나';box.appendChild(e);const cs=getComputedStyle(e);const a=lum(rgb(cs.backgroundColor)),b=lum(rgb(cs.borderBottomColor));o[c]=Math.round((Math.max(a,b)+0.05)/(Math.min(a,b)+0.05)*100)/100;e.remove();}return o;}"""
KEYCH_BASE=(3,954)   # 옛 렌더(0918775 docs) 1280 학습+정리표 42강의: 150자↑ 3 · 80자↑ 954 — 새 렌더 150자↑는 30% 이하(≤0)여야
async def ux3_checks(b):
    """ux3 N4 🔑 긴 덩어리(1280 학습·정리표 전 강의) · K2 빈칸 5색 밑줄 대비 · 인쇄 에뮬레이션 색 없음"""
    bad=[]; rep=[]; pg=await b.new_page(viewport={'width':1280,'height':900}); t150=t80=0
    for s,ls in SUBJ.items():
        for k in ls:
            for t in ('learn','sum'):
                await pg.goto('about:blank'); await pg.goto(f'{U}#/{s}/{k}/{t}'); await pg.wait_for_timeout(350)
                r=await pg.evaluate(KEYCH); t150+=r[0]; t80+=r[1]
    rep.append(f'KEYCHUNK 🔑 상자·정리표 칸 한 덩어리 150자↑ {KEYCH_BASE[0]} → {t150} · 80자↑ {KEYCH_BASE[1]} → {t80} (옛 → 새)')
    # ux3 fix flow V07 — 정리표 '🔑 요지·핵심' 칸(요지 .mg + 🔑 .mkey)만, 폭별(1280 표 · 820 2단 카드) 80자↑ 덩어리(보고만)
    for vw in (1280, 820):
        p2 = await b.new_page(viewport={'width': vw, 'height': 900}); n80 = n50 = 0
        for s, ls in SUBJ.items():
            for k in ls:
                await p2.goto('about:blank'); await p2.goto(f'{U}#/{s}/{k}/sum'); await p2.wait_for_timeout(350)
                r = await p2.evaluate(KEYCH.replace("'#stage .c-key .kb, #stage .mkey'", "'#stage .msum td.mk'").replace('if(L>150)n150++;if(L>80)n80++;', 'if(L>80)n150++;if(L>50)n80++;'))
                n80 += r[0]; n50 += r[1]
        await p2.close(); rep.append(f'KEYCHUNK 정리표 🔑 요지·핵심 칸만 {vw}: 80자↑ {n80} · 50자↑ {n50}')
    if t150>KEYCH_BASE[0]*0.3: bad.append(f'KEYCHUNK 150자↑ {t150} (옛 {KEYCH_BASE[0]}의 30% 넘음)')
    cr=await pg.evaluate(BLANKCR); rep.append(f'BLANKCR 빈칸 밑줄 대비 {cr}')
    if any(v<3.0 for v in cr.values()): bad.append(f'BLANKCR 대비 3.0 미만 {cr}')
    await pg.emulate_media(media='print'); pr=await pg.evaluate("(()=>{const box=document.querySelector('#stage');const o=[];for(const c of ['n','u','g','p','v']){const e=document.createElement('span');e.className='rk-b'+(c!=='n'?' rkb-'+c:'');e.textContent='가';box.appendChild(e);o.push(getComputedStyle(e).backgroundColor);e.remove();}return o})()"); await pg.emulate_media(media='screen')
    if any(x!='rgba(0, 0, 0, 0)' for x in pr): bad.append(f'BLANK PRINT 인쇄에 빈칸 바탕색 {pr}')
    await pg.close(); return bad, rep
# ---- ux3 R3 과목 색 한 가지 — 팩 color(subject.py) = SJC = sjColor · 메뉴 점·홈 과목표 점·이어서·과목 홈 hero·--acc·통계·달력 과목 점이 모두 그 색 · hero 흰 글자·종이 바탕 대비 ≥4.5 ----
SJCOL=r"""()=>{const H=window.__h,P=H.PACKS,ids=Object.keys(P),bad=[];const hex=c=>{const m=(c||'').match(/\d+/g);return m?'#'+m.slice(0,3).map(x=>(+x).toString(16).padStart(2,'0')).join('').toUpperCase():'';};
 const SJC=H.SJC||{};ids.forEach(k=>{const a=(P[k].color||'').toUpperCase(),b=(SJC[k]||'').toUpperCase(),c=(H.sjColor(k)||'').toUpperCase();if(!(a&&a===b&&b===c))bad.push(`${k} 팩 ${a} · SJC ${b} · sjColor ${c}`);});
 const want=new Set(ids.map(k=>H.sjColor(k).toUpperCase()));Object.keys(SJC).forEach(k=>want.add(SJC[k].toUpperCase()));want.add('#9A9288');
 const pick=(sel,prop,key)=>document.querySelectorAll(sel).forEach(e=>{if(!e.getClientRects().length)return;const v=hex(getComputedStyle(e)[prop]);const s=key?key(e):'';if(s&&v!==H.sjColor(s).toUpperCase())bad.push(`${sel} ${s} ${v}≠${H.sjColor(s)}`);else if(!s&&v&&!want.has(v))bad.push(`${sel} 과목 색이 아님 ${v}`);});
 pick('#nav .nvs .nvdot','backgroundColor',e=>e.closest('.nvs').dataset.s);pick('#home .hsj .hdot','backgroundColor',e=>{const h=e.closest('.hsj');return h.dataset.s||h.dataset.off;});
 pick('#nav .nvrs .nvdot','backgroundColor',e=>e.closest('.nvrs').dataset.s);pick('.sjdot','backgroundColor',null);return bad;}"""
async def subj_color(b):
    """ux3 R3 과목 색 한 가지 — 허브 홈·통계·달력·과목 홈(hero·--acc)을 1280으로 열어 같은 과목이 화면마다 같은 색인지, hero 흰 글자·종이 바탕 대비 ≥4.5"""
    bad=[]; pg=await b.new_page(viewport={'width':1280,'height':900})
    await pg.goto('about:blank'); await pg.goto(U+'#/'); await pg.wait_for_timeout(1500)
    ids=await pg.evaluate("Object.keys(__h.PACKS)")
    await pg.evaluate("ids=>{const d=new Date(),t=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'),o={};o[t]={};ids.forEach((k,i)=>o[t][k]=(i+1)*6e5);localStorage.setItem('jblhub.v1.time',JSON.stringify(o));}", ids)
    for h in ['#/','#/_time','#/_cal']:
        await pg.goto('about:blank'); await pg.goto(U+h); await pg.wait_for_timeout(1200)
        bad+=[f'{h} {x}' for x in await pg.evaluate(SJCOL)]
    for s in ids:
        await pg.goto('about:blank'); await pg.goto(f'{U}#/{s}/_home'); await pg.wait_for_timeout(900)
        r=await pg.evaluate("""s=>{const c=__h.sjColor(s).toUpperCase(),cs=getComputedStyle(document.documentElement),h1=cs.getPropertyValue('--hero1').trim().toUpperCase(),ac=cs.getPropertyValue('--acc').trim().toUpperCase();
          const lin=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)},L=h=>{const n=parseInt(h.slice(1),16);return 0.2126*lin(n>>16&255)+0.7152*lin(n>>8&255)+0.0722*lin(n&255)},cr=(a,b)=>{const x=L(a),y=L(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
          return {c,h1,ac,w:cr(c,'#FFFFFF'),p:cr(c,'#F1EDE5')};}""", s)
        if not (r['h1']==r['c']==r['ac']): bad.append(f'{s} 과목 홈 --hero1 {r["h1"]} · --acc {r["ac"]} ≠ {r["c"]}')
        if r['w']<4.5 or r['p']<4.5: bad.append(f'{s} {r["c"]} 대비 흰 글자 {r["w"]:.2f} · 종이 {r["p"]:.2f} (<4.5)')
        bad+=[f'{s}/_home {x}' for x in await pg.evaluate(SJCOL)]
    await pg.close(); return bad
CALM=r"""()=>{const vis=e=>{const r=e.getBoundingClientRect();if(r.width<1||r.height<1||r.bottom<0||r.top>innerHeight)return false;const s=getComputedStyle(e);return s.visibility!=='hidden'&&s.display!=='none'&&+s.opacity>0.05};
 const fs=new Set(),odd=new Set();for(const e of document.querySelectorAll('#home *,#hero *,#dtabs *,#stage *')){if(!vis(e))continue;if(![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))continue;if(e.closest('.tc .tbody,.qc .qtext,.qc .ans,table'))continue;if(e.closest('details:not([open])')&&!e.closest('summary'))continue;const f=getComputedStyle(e).fontSize;fs.add(f);if(Math.abs(parseFloat(f)*2-Math.round(parseFloat(f)*2))>0.01)odd.add(f+' '+e.tagName+'.'+String(e.className).slice(0,30));}
 const OK=/[🔑⭐💬✍⚡📌⚠☕▶✎★]/u,emo=[];document.querySelectorAll('#top,#nav,#dtabs,#hero,#lvpop,#home h1,#home h2,#stage h2.hh,#stage .frt,#home .btn,#stage #jbbar,#stage .acts').forEach(r=>{if(!vis(r))return;const t=r.innerText||'';(t.match(/\p{Extended_Pictographic}/gu)||[]).forEach(c=>{if(!OK.test(c))emo.push(c+' '+(r.id||r.className||r.tagName));});});
 return {fs:[...fs].sort((a,b)=>parseFloat(a)-parseFloat(b)),odd:[...odd].slice(0,8),emo};}"""
async def calm_checks(b):
    """ux4 B3-1 최종 시안 글자 6단계·크롬 이모지 — 1280 첫 화면(허브 홈·과목 홈·강의 학습·JB)의 본문 밖(머리·탭·절 제목·버튼) 글자 크기 종류 ≤7/6/6/7, 0.5px 단위가 아닌 크기 0, 크롬(상단·메뉴·탭·머리·절 제목·버튼) 이모지 0(정리본 표지 🔑⭐💬✍⚡📌⚠·☕·재생 ▶ 제외 — 시안의 [▶ 시작][☕ 쉬기] · 시안의 글자 기호 [✎ 도구]·JB 별표 ★도 제외)"""
    bad=[]; rep=[]; pg=await b.new_page(viewport={'width':1280,'height':900})
    for h,lim in [('#/',7),('#/CONS/_home/_home',6),('#/CONS/WHT/learn',6),('#/CONS/_jb/_jb',7),('#/PHARM/_home/_home',6),('#/OMS1/DD1/learn',6)]:
        await pg.goto('about:blank'); await pg.goto(U+h); await pg.wait_for_timeout(1500)
        r=await pg.evaluate(CALM); rep.append(f'{h} 글자 크기 {len(r["fs"])}종 {" ".join(r["fs"])}')
        if len(r['fs'])>lim: bad.append(f'{h} 글자 크기 {len(r["fs"])}종 > {lim}: {r["fs"]}')
        if r['odd']: bad.append(f'{h} 0.5px 단위 아닌 크기 {r["odd"]}')
        if r['emo']: bad.append(f'{h} 크롬 이모지 {r["emo"][:8]}')
    await pg.close(); return bad, rep
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
        FB,FR=await fixb_sweep(b)
        print('FIXB SWEEP (반쯤 잘린 줄·820 전체정리표 넘침·점 두 개 — 0이어야 함)', len(FB))
        for x in FB[:40]: print(' ',x)
        for x in FR: print('  (보고)',x)
        UB,UR=await ux3_checks(b)
        print('UX3 K·N (🔑 긴 덩어리·빈칸 대비·인쇄 — 판정)', len(UB))
        for x in UB: print(' ',x)
        for x in UR: print('  (보고)',x)
        IP=await ipad_sweep(b)
        print('IPAD SWEEP (가로 밀림·점 겹침·청록)', len(IP))
        for x in IP[:40]: print(' ',x)
        CB,CR=await calm_checks(b)
        print('CALM (ux4 B3-1 글자 6단계·크롬 이모지 — 0이어야 함)', len(CB))
        for x in CR: print('  (보고)',x)
        for x in CB: print(' ',x)
        SC=await subj_color(b)
        print('SUBJ COLOR (과목 색 한 가지 — 0이어야 함)', len(SC))
        for x in SC[:20]: print(' ',x)
        print('errs',errs[:3]); await b.close()
        return not IP and not errs and not FB and not UB and not SC and not CB
ok_=asyncio.run(main())
print('RESULT', 'PASS' if ok_ else 'FAIL'); sys.exit(0 if ok_ else 1)
