"""10-04 사용자 '하이라이트모드에서 빈 공간을 클릭하면 해당 단어를 클릭하지 않았는데도 위 아래 행의 첫글자가 하이라이트되는 오류'
형광펜 모드: ① 줄 끝 오른쪽 빈 곳 ② 두 줄 사이 틈 ③ 항목 왼쪽 들여쓰기 빈 곳 → 칠하지 않음 · ④ 낱말 위 → 그 낱말만 칠함 (마우스 1280 · 손가락 820)
+ 시계 창: ■ 멈춤 줄에 색 칠함(.on) 없음
  .venv/bin/python tools/tests/ux4g_B.py"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import datetime
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
W = "!!(window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#stage .tc .tbody'))"
GEO = """(()=>{const c=[...document.querySelectorAll('#stage .tc .tbody .li')].find(e=>{const r=e.getBoundingClientRect();return r.top>120&&r.bottom<innerHeight-100&&e.textContent.length>60&&!e.querySelector('ol,ul')});
 if(!c)return null;const rg=document.createRange();rg.selectNodeContents(c);const rs=[...rg.getClientRects()].filter(r=>r.width>4);const R=c.getBoundingClientRect(),f=rs[0],l=rs[rs.length-1];
 const t=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);let n,w=null;while(n=t.nextNode()){const m=/[A-Za-z가-힣]{3,}/.exec(n.nodeValue);if(m){const r2=document.createRange();r2.setStart(n,m.index);r2.setEnd(n,m.index+m[0].length);const b=r2.getBoundingClientRect();w=[b.left+b.width/2,b.top+b.height/2,m[0]];break;}}
 const nx=c.parentElement.querySelector('.li~.li')||c.nextElementSibling;const nr=nx&&nx.getBoundingClientRect();
 return {endx:Math.min(R.right-4,l.right+40),endy:l.top+l.height/2,lastw:l.right-l.left,gapy:nr?(R.bottom+nr.top)/2:null,gapx:f.left+20,leftx:Math.max(R.left-14,2),lefty:f.top+f.height/2,w,txt:c.textContent.slice(0,40)}})()"""
N = "document.querySelectorAll('#stage [data-rk]').length"
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw, vh, touch in ((1280, 900, False), (820, 1180, True)):
        ctx = b.new_context(viewport={'width': vw, 'height': vh}, has_touch=touch); pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.clock.install(time=datetime.datetime(2026, 10, 5, 10, 0, 0))
        pg.goto(U); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); pg.goto('about:blank'); pg.goto(U + '#/PHARM/XE/learn'); pg.clock.run_for(2000)
        for _ in range(150):
            if pg.evaluate(W): break
            pg.wait_for_timeout(100); pg.clock.run_for(100)
        pg.evaluate("(e=>e&&e.scrollIntoView({block:'center'}))([...document.querySelectorAll('#stage .tc .tbody .li')].find(e=>e.textContent.length>60&&!e.querySelector('ol,ul')))"); pg.clock.run_for(1500)
        pg.keyboard.press('h'); pg.clock.run_for(300)
        g = pg.evaluate(GEO); tag = 'touch' if touch else 'mouse'
        ok(g is not None and g['w'], f'{tag} 시험 줄 {g and g["txt"]!r}')
        tap = (lambda x, y: pg.touchscreen.tap(x, y)) if touch else (lambda x, y: pg.mouse.click(x, y))
        n0 = pg.evaluate(N)
        for nm, (x, y) in (('줄 끝 오른쪽 빈 곳', (g['endx'], g['endy'])), ('줄 사이 틈', (g['gapx'], g['gapy'])), ('왼쪽 들여쓰기 빈 곳', (g['leftx'], g['lefty']))):
            if y is None: continue
            tap(x, y); pg.clock.run_for(400); n1 = pg.evaluate(N)
            ok(n1 == n0, f'{tag} {nm} 누름 → 칠하지 않음 (표시 {n0}→{n1})'); n0 = n1
        tap(g['w'][0], g['w'][1]); pg.clock.run_for(400)
        got = pg.evaluate("[...document.querySelectorAll('#stage [data-rk]')].map(e=>e.textContent).join('|')")
        ok(g['w'][2] in got, f"{tag} 낱말 '{g['w'][2]}' 누름 → 그 낱말 칠함 ({got[:40]!r})")
        pg.keyboard.press('h'); pg.clock.run_for(200)
        pg.evaluate("__h.trStart()"); pg.clock.run_for(2000); pg.evaluate("document.querySelector('#clock').click()"); pg.clock.run_for(300)
        on = pg.evaluate("[...document.querySelectorAll('#tpop [data-tp].on')].map(b=>b.dataset.tp)")
        ok('stop' not in on, f'{tag} 시계 창 ■ 멈춤 색칠 없음 (색칠된 줄 {on})')
        # 압축 보기(C)에서 카드 제목·▶ 누르면 그 카드 전체 내용 · 다시 누르면 접힘 · 압축 끄면 풂
        pg.keyboard.press('Escape'); pg.clock.run_for(200)
        pg.evaluate("document.querySelector('#tpop').classList.remove('on');document.activeElement&&document.activeElement.blur()"); pg.mouse.click(5, 300); pg.keyboard.press('c'); pg.clock.run_for(500)
        cid = pg.evaluate("(c=>c&&c.id)([...document.querySelectorAll('#stage .tc.open')].find(c=>{const r=c.getBoundingClientRect();return r.bottom>80&&r.top<innerHeight-120&&c.querySelector('.thead .en[data-ttog]')}))")
        vis = f"(c=>[...c.querySelectorAll('.tbody .li')].filter(e=>e.offsetParent).length)(document.getElementById('{cid}'))"
        n0 = pg.evaluate(vis)
        ok(pg.evaluate("document.querySelector('#stage').classList.contains('cond')") and cid, f'{tag} 압축 보기 켬 ({cid}) 보이는 항목 {n0}')
        pg.evaluate(f"document.querySelector('#{cid} .thead .en[data-ttog]').click()"); pg.clock.run_for(400)
        n1 = pg.evaluate(vis); full = pg.evaluate(f"document.getElementById('{cid}').classList.contains('cfull')")
        ok(full and n1 > n0, f'{tag} 압축 중 제목 누름 → 그 카드 전체 내용 (항목 {n0}→{n1})')
        pg.evaluate(f"document.querySelector('#{cid} .car[data-ttog]').click()"); pg.clock.run_for(400)
        ok(not pg.evaluate(f"document.getElementById('{cid}').classList.contains('open')") and not pg.evaluate(f"document.getElementById('{cid}').classList.contains('cfull')"), f'{tag} 다시 누름 → 접힘')
        pg.evaluate(f"document.querySelector('#{cid} .car[data-ttog]').click()"); pg.clock.run_for(300)
        ok(pg.evaluate(vis) == n1 and pg.evaluate(f"document.getElementById('{cid}').classList.contains('cfull')"), f'{tag} 접힌 카드 펼침 → 바로 전체 내용 ({pg.evaluate(vis)})')
        pg.evaluate(f"document.querySelector('#{cid} .car[data-ttog]').click()"); pg.clock.run_for(300)
        pg.keyboard.press('c'); pg.clock.run_for(400)
        ok(not pg.evaluate("document.querySelectorAll('#stage .tc.cfull').length"), f'{tag} 압축 끄면 전체 내용 표시 풂')
        ok(not errs, f'{tag} pageerror 0 {errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
