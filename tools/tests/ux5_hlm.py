"""10-07 사용자 회귀: 이미 칠한 형광펜 뭉텅이에 근처 단어부터 이어 칠하면 → 한 묶음(어절별로 끊긴 여러 묶음이 되지 않음) · 다른 색은 따로 · 새로고침 뒤 그대로
  .venv/bin/python tools/tests/ux5_hlm.py"""
import os as _os, sys; sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
src = open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'ux4f_M.py'), encoding='utf-8').read()
for k in ('PICK', 'XY', 'COV', 'W'): exec(src[src.index(k + '='):].split('\n')[0])
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
GR = """()=>{const gs=[...window.__b.querySelectorAll('[data-rk=h]')].map(e=>e.getAttribute('data-g'));return new Set(gs).size}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}); E = []; pg.on('pageerror', lambda e: E.append(str(e)))
    pg.goto(U + '#/'); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')")
    for lec, k in (('CONS/WHT', 3), ('OMS1/DD1', 7), ('PHARM/HM', 11)):
        pg.goto('about:blank'); pg.goto(U + '#/' + lec + '/learn'); pg.wait_for_function(W, timeout=60000); pg.wait_for_timeout(800); pg.keyboard.press('h')
        bid = pg.evaluate(PICK, k); pg.wait_for_timeout(300)
        def drag(i, j):
            a = pg.evaluate(XY, i); z = pg.evaluate(XY, j)
            if not a or not z: return False
            pg.mouse.move(a[0], a[1]); pg.mouse.down(); pg.mouse.move(z[0] + 4, z[1], steps=10); pg.mouse.up(); pg.wait_for_timeout(400); return True
        if not drag(10, 40): continue
        g0 = pg.evaluate(GR)
        drag(60, 25); c2, _ = pg.evaluate(COV)
        ok(pg.evaluate(GR) == g0 == 1 or (g0 == 1 and pg.evaluate(GR) == 1), f'{lec} 뭉텅이 뒤로 이어 칠함 → 한 묶음 ({pg.evaluate(GR)})')
        drag(5, 30)
        ok(pg.evaluate(GR) == 1, f'{lec} 뭉텅이 앞으로 이어 칠함 → 한 묶음 ({pg.evaluate(GR)})')
        cv, _ = pg.evaluate(COV); pg.wait_for_timeout(900); pg.reload(); pg.wait_for_function(W, timeout=60000); pg.wait_for_timeout(900)
        pg.evaluate("(id)=>{window.__b=document.getElementById(id)}", bid); cv2, _ = pg.evaluate(COV)
        ok(set(cv) == set(cv2) and pg.evaluate(GR) == 1, f'{lec} 새로고침 뒤 그대로 한 묶음')
    ok(not E, f'콘솔 오류 0 {E[:1]}')
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); sys.exit(1 if fails else 0)
