"""10-08 사용자 '큰 구분점끼리 줄간격 조금 더 · 세부 넘버링은 조금 덜' 회귀: 줄간격 3층이 어디서나 같은 순서인지
  ⚡ 학습·📖 JB 카드 ⚡: 서로 다른 줄 > 같은 줄 조각 > 안쪽 번호·◦ 하위 · 🎯·대조: 항목 > 항목 안 조각·안쪽 목록
  + '자가골 채취: 구내 … / 구외 …'는 머리 아래 하위 목록(◦)으로(구외가 따로 떨어진 •가 아님)
  .venv/bin/python tools/tests/ux6_gap.py"""
import os as _os, sys, statistics as st; sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
W = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
GAPS = r"""(sel)=>{const o={};const add=(k,a,b)=>{const r=a.getBoundingClientRect(),s=b.getBoundingClientRect();if(!r.height||!s.height||Math.abs(s.left-r.left)>2)return;(o[k]=o[k]||[]).push(s.top-r.bottom);};
 document.querySelectorAll(sel).forEach(m=>{const ul=m.querySelector(':scope>ul');if(!ul)return;const L=[...ul.children];
  L.forEach((li,i)=>{const n=L[i+1];if(n)add(li.classList.contains('mg')&&n.classList.contains('mg')&&!n.classList.contains('mg0')?'same':'diff',li,n);
   li.querySelectorAll('li').forEach(x=>{const y=x.nextElementSibling;if(y&&y.tagName==='LI')add('sub',x,y);});});});
 const md=a=>a&&a.length?a.sort((x,y)=>x-y)[a.length>>1]:null;return {diff:md(o.diff),same:md(o.same),sub:md(o.sub),n:Object.fromEntries(Object.entries(o).map(([k,v])=>[k,v.length]))};}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}); E = []; pg.on('pageerror', lambda e: E.append(str(e)))
    for lec in ('OMS1/EXT', 'OMS1/DD2', 'CONS/ADH', 'GERI/SAL'):
        pg.goto(U + '#/' + lec + '/learn'); pg.wait_for_function(W, timeout=60000); pg.wait_for_timeout(900)
        g = pg.evaluate(GAPS, '#stage .c-mem')
        ok(g['diff'] is not None and g['sub'] is not None and g['diff'] > (g['same'] if g['same'] is not None else -1) and (g['same'] is None or g['same'] > g['sub']) and g['diff'] - g['sub'] >= 4,
           f'{lec} ⚡ 줄간격 층: 다른 줄 {g["diff"]} > 같은 줄 조각 {g["same"]} > 안쪽 {g["sub"]} ({g["n"]})')
    pg.goto(U + '#/OMS1/EXT/learn'); pg.wait_for_function(W, timeout=60000); pg.wait_for_timeout(900)
    r = pg.evaluate("""()=>{const li=[...document.querySelectorAll('#stage .c-mem li')].find(x=>/^구외/.test(x.textContent.trim()));if(!li)return null;
      return [li.parentElement.classList.contains('msub'), li.parentElement.closest('li').textContent.trim().slice(0,7)]}""")
    ok(bool(r) and r[0] and r[1].startswith('자가골 채취'), f'OMS1 EXT ⚡ 구외 = 자가골 채취 머리 아래 ◦ 하위 목록 ({r})')
    pg.goto(U + '#/OMS1/_jb/_jb'); pg.wait_for_function(W, timeout=60000); pg.wait_for_timeout(900)
    pg.evaluate("()=>{[...document.querySelectorAll('#stage .qc')].slice(0,30).forEach(c=>{const t=c.querySelector('[data-tog]');if(t)t.click();const d=c.querySelector('[data-deep]');if(d)d.click();c.querySelectorAll('details').forEach(x=>x.open=true);});}")
    pg.wait_for_timeout(900)
    g = pg.evaluate(GAPS, '#stage .ab.lk .lkey.lmem')
    ok(g['diff'] is not None and g['sub'] is not None and g['diff'] - g['sub'] >= 4, f'OMS1 JB 📖 카드 ⚡ 줄간격 층: 다른 줄 {g["diff"]} > 안쪽 {g["sub"]} ({g["n"]})')
    k = pg.evaluate("""()=>{const a=[],s=[];document.querySelectorAll('#stage .ab.key1>ul>li').forEach(li=>{const n=li.nextElementSibling;if(n){const r=li.getBoundingClientRect(),q=n.getBoundingClientRect();if(r.height&&q.height)a.push(q.top-r.bottom);}
      li.querySelectorAll('li').forEach(x=>{const y=x.nextElementSibling;if(y&&y.tagName==='LI'){const r=x.getBoundingClientRect(),q=y.getBoundingClientRect();if(r.height&&q.height&&Math.abs(q.left-r.left)<3)s.push(q.top-r.bottom);}});});
      const md=v=>v.length?v.sort((x,y)=>x-y)[v.length>>1]:null;return [md(a),md(s),a.length,s.length]}""")
    ok(k[0] is not None and (k[1] is None or k[0] > k[1]), f'OMS1 JB 🎯 요점 항목 {k[0]} > 안쪽 {k[1]} ({k[2]}·{k[3]})')
    ok(not E, f'콘솔 오류 0 ({E[:2]})')
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
