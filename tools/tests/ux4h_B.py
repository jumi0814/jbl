"""10-05 사용자 '✍ 이해 여기 뒤에 있는 단어를 하이라이트 및 빈칸빵 하려고할 때 해당 ✍ 이해요게 같은 단어로 인식해서 같이 하이라이트' — ✍ 이해 꼬리표 바로 뒤 첫 낱말만 칠해지는지(형광펜·빈칸)
  + JB 미리보기 답에 해설 함께(10-05)   .venv/bin/python tools/tests/ux4h_B.py"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(U); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); pg.goto('about:blank'); pg.goto(U + '#/PHARM/RX/learn'); pg.wait_for_timeout(3500)
    for mode, key in (('형광펜', 'h'), ('빈칸', 'b')):
        pg.evaluate("document.querySelector('.und').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
        r = pg.evaluate("(()=>{const u=document.querySelector('.und'),l=u.querySelector('.ui');const w=document.createTreeWalker(u,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){if(!l.contains(n)&&n.nodeValue.trim())break;}const rg=document.createRange();rg.setStart(n,0);rg.setEnd(n,1);const b=rg.getBoundingClientRect();return [b.x+2,b.y+b.height/2,n.nodeValue.trim().split(/\\s/)[0]];})()")
        pg.keyboard.press(key); pg.wait_for_timeout(200); pg.mouse.click(r[0], r[1]); pg.wait_for_timeout(400); pg.keyboard.press(key); pg.wait_for_timeout(200)
        t = pg.evaluate("(()=>{const u=document.querySelector('.und');return [...u.querySelectorAll('[data-rk],mark,.hl-u,.rk-h,.rk-b')].map(x=>x.textContent).join('|');})()")
        ok(t and '이해' not in t and '✍' not in t, f'{mode}: ✍ 이해 뒤 첫 낱말만 {t!r} (낱말 {r[2]!r})')
        pg.keyboard.press("Control+z"); pg.wait_for_timeout(300)
    pg.goto(U + '#/PHARM/RX/learn'); pg.wait_for_timeout(2500)
    pg.evaluate("document.querySelector('.c-exam .jbchip[data-go]').click()"); pg.wait_for_timeout(600)
    pg.evaluate("(()=>{const b=document.querySelector('#jbpeek .jpshow, #jbpeek [data-jpshow]');if(b)b.click();})()"); pg.wait_for_timeout(500)
    a = pg.evaluate("(()=>{const p=document.querySelector('#jbpeek');return p?p.innerText:'';})()")
    ok('해설' in a or '참고' not in a, f'JB 미리보기 답 보기 — 해설 함께 {a[:80]!r}')
    ok(not errs, f'pageerror 0 {errs[:2]}'); b.close()
print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
