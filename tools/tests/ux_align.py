"""10-24 정렬 회귀(사용자 '같은 줄 안에 일렬이 아니라 위아래 삐뚤빼뚤 … 박스나 동그라미 안 단어·태그가 위아래로 쏠림'):
가로 flex 줄 안 항목(키 60px 미만)의 세로 중심 차이 3px 이상 = 0 · 배경/테가 있는 작은 알약(≤34px) 안 글자의 위·아래 여백 차이 2.5px 이상 = 0
(여러 줄로 감기는 ⭐ 시험포인트 줄 .exrow는 위 맞춤이 맞아 제외 · 표 칸은 위 맞춤이라 제외). 1440·820·393."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
JS = r"""()=>{
const vis=e=>{const r=e.getBoundingClientRect();return r.width>2&&r.height>2&&getComputedStyle(e).visibility!=='hidden'};
const nm=e=>e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+(typeof e.className==='string'&&e.className.trim()?'.'+e.className.trim().split(/\s+/).slice(0,3).join('.'):'');
const rows=[];
// 1) 한 줄 안 항목 중심 어긋남: flex 줄(가로)인 컨테이너의 자식 — 같은 줄(top 겹침)끼리 중심 차이
document.querySelectorAll('#stage *, #top *, #dtabs *, #home *').forEach(c=>{const cs=getComputedStyle(c);if(!/flex/.test(cs.display)||cs.flexDirection.startsWith('column')||!vis(c))return;
 const K=[...c.children].filter(vis).map(k=>{const r=k.getBoundingClientRect();return {k,t:r.top,b:r.bottom,m:(r.top+r.bottom)/2,h:r.height}});if(K.length<2)return;
 const lines=[];K.forEach(x=>{let L=lines.find(l=>x.t<l.b-2&&x.b>l.t+2);if(!L){L={t:x.t,b:x.b,it:[]};lines.push(L)}L.it.push(x);L.t=Math.min(L.t,x.t);L.b=Math.max(L.b,x.b)});
 lines.forEach(L=>{if(L.it.length<2)return;const ms=L.it.map(x=>x.m),d=Math.max(...ms)-Math.min(...ms);if(d>=3&&L.it.every(x=>x.h<60))rows.push(['ROW',Math.round(d*10)/10,nm(c),cs.alignItems,L.it.map(x=>nm(x.k)+':'+Math.round(x.m-L.t)+'/'+Math.round(x.h)).join(' ')])});});
// 2) 알약 안 글자 쏠림: 배경·테가 있는 작은 요소의 글자 영역 위/아래 여백 차이
const pills=[];document.querySelectorAll('#stage *, #top *, #dtabs *, #home *, #kit *').forEach(e=>{if(!vis(e))return;const r=e.getBoundingClientRect();if(r.height>44||r.height<14)return;const cs=getComputedStyle(e);
 const bg=cs.backgroundColor!=='rgba(0, 0, 0, 0)'||parseFloat(cs.borderTopWidth)>0||cs.boxShadow!=='none';if(!bg)return;
 const tn=[...e.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim());if(!tn.length)return;const rg=document.createRange();rg.selectNodeContents(tn[0]);const q=[...rg.getClientRects()].filter(x=>x.height>0);if(!q.length)return;const qr=q[0];
 const up=qr.top-r.top,dn=r.bottom-qr.bottom,d=up-dn;if(Math.abs(d)>=2.5)pills.push(['PILL',Math.round(d*10)/10,nm(e),e.textContent.trim().slice(0,12),Math.round(r.height),cs.lineHeight,cs.display,cs.paddingTop+'/'+cs.paddingBottom])});
return {rows:rows.filter(r=>!/exrow/.test(r[2])),pills:pills.filter(p=>/^(span|button|summary|a|b)/.test(p[2])&&p[4]<=34)};}"""
H = ['#/IMPL/PART/learn', '#/IMPL/PART/jb', '#/IMPL/PART/pred', '#/IMPL/PART/fig', '#/IMPL/_jb/_jb', '#/IMPL/_fig/_fig', '#/PHARM/_home/_home', '#/ESTH/MAT/learn', '#/']
fails = []
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w in (1440, 820, 393):
            pg = await b.new_page(viewport={'width': w, 'height': 900}, is_mobile=w < 600, has_touch=w < 600)
            for h in H:
                await pg.goto('about:blank'); await pg.goto(J.HUB_URL + h); await pg.wait_for_timeout(1300)
                r = await pg.evaluate(JS); bad = r['rows'] + r['pills']
                print(('  OK   ' if not bad else '  FAIL ') + f'{w} {h} 어긋남 {len(bad)}', json.dumps(bad[:2], ensure_ascii=False)[:300])
                if bad: fails.append((w, h))
            await pg.close()
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
