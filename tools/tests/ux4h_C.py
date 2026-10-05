"""10-05 사용자 '1회독 표시를 추가 … 한번 보면 1회독부터 숫자 올릴 수 있게끔! 내 북마크에선 각 과목별로 모든 강의자료들이 보이고, 회독 표시 및 북마크 표시를 토글하면 해당 내역만'
  과목 홈 카드 '회독 +' → 1회독 → 2회독 · 오른쪽 클릭 −1 · LS lrd.<S> · 강의 머리 버튼 동기 · 내 북마크 [모든 강의][★][📖] 토글   .venv/bin/python tools/tests/ux4h_C.py"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CARDS = "[...document.querySelectorAll('#home .lcard')].map(c=>c.dataset.hbs+':'+c.dataset.d)"
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, touch in ((1280, 900, False), (820, 1180, True)):
        ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch); pg = ctx.new_page(); errs = []; tag = str(w)
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto(U); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); pg.goto('about:blank'); pg.goto(U + '#/PHARM/_home'); pg.wait_for_timeout(3500)
        btn = "document.querySelector('#hlec [data-lrd=\"PHARM|XE\"]')"
        ok(pg.evaluate(btn + ".textContent") == '회독 +', f'{tag} 처음 = 회독 +')
        h0 = pg.evaluate("location.hash"); pg.evaluate(btn + ".click()"); pg.wait_for_timeout(300)
        ok(pg.evaluate(btn + ".textContent") == '1회독' and pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.lrd.PHARM'))['XE'].n") == 1, f'{tag} 누르면 1회독(LS lrd)')
        ok(pg.evaluate("location.hash") == h0 and pg.evaluate("!!document.querySelector('#hlec')"), f'{tag} 회독 버튼은 강의로 이동하지 않음')
        pg.evaluate(btn + ".click()"); pg.wait_for_timeout(300); ok(pg.evaluate(btn + ".textContent") == '2회독', f'{tag} 다시 → 2회독')
        pg.evaluate(btn + ".dispatchEvent(new MouseEvent('contextmenu',{bubbles:true,cancelable:true}))"); pg.wait_for_timeout(300)
        ok(pg.evaluate(btn + ".textContent") == '1회독', f'{tag} 오른쪽 클릭 → 1회독')
        pg.evaluate("document.querySelector('#hlec [data-lbm=\"PHARM|ACU\"]').click()"); pg.wait_for_timeout(300)
        pg.goto(U + '#/PHARM/XE/learn'); pg.wait_for_timeout(2500)
        ok(pg.evaluate("document.querySelector('#hero [data-lrd]').textContent") == '1회독', f'{tag} 강의 머리에도 1회독')
        pg.goto(U + '#/_bm'); pg.wait_for_timeout(2500)
        n_all = len(pg.evaluate(CARDS)); ok(n_all > 30, f'{tag} 내 북마크 기본 = 모든 강의 {n_all}')
        pg.evaluate("document.querySelector('#home [data-hbf=rd]').click()"); pg.wait_for_timeout(600)
        ok(pg.evaluate(CARDS) == ['PHARM:XE'], f'{tag} 📖 회독만 {pg.evaluate(CARDS)}')
        pg.evaluate("document.querySelector('#home [data-hbf=bm]').click()"); pg.wait_for_timeout(600)
        ok(pg.evaluate(CARDS) == ['PHARM:ACU'], f'{tag} ★ 북마크만 {pg.evaluate(CARDS)}')
        pg.reload(); pg.wait_for_timeout(3000); ok(pg.evaluate(CARDS) == ['PHARM:ACU'], f'{tag} 새로고침 뒤 거르기 유지')
        pg.evaluate("document.querySelector('#home [data-hbf=\"\"]').click()"); pg.wait_for_timeout(600); ok(len(pg.evaluate(CARDS)) == n_all, f'{tag} 모든 강의로')
        ok(pg.evaluate("document.documentElement.scrollWidth-innerWidth") <= 0, f'{tag} 가로 넘침 없음')
        ok(not errs, f'{tag} pageerror 0 {errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
