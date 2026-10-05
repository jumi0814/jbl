"""10-04 사용자 '허브 홈에서 공부달력과 내 표시 사이에 내 북마크 라는 탭 … 과목별로 내가 북마크 표시한 강의자료 … 전체 한번에 또는 과목별로 … 과목홈 강의자료 공부전략까지 표시된 그 형식 그대로'
허브 메뉴 순서(공부 달력 → 내 북마크 → … 내 표시) · #/_bm 전체·과목 탭 · 과목 홈 강의 카드 틀(.lcard·📌 공부 전략) · 새로고침 뒤 탭 유지 · ☆로 빼면 바로 빠짐 · 카드 → 강의 · 뒤로 → 내 북마크 (1280·820)
  .venv/bin/python tools/tests/ux4g_C.py"""
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
        pg.goto(U); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1');localStorage.setItem('jblhub.v1.lbm.PHARM',JSON.stringify({XE:1,ACU:2}));localStorage.setItem('jblhub.v1.lbm.CONS',JSON.stringify({INL:3}))")
        pg.goto('about:blank'); pg.goto(U + '#/'); pg.wait_for_timeout(3500)
        nav = pg.evaluate("[...document.querySelectorAll('#nav [data-nv]')].map(b=>b.dataset.nv)")
        ok(nav.index('cal') < nav.index('bm') < nav.index('marks'), f'{tag} 메뉴: 공부 달력 → 내 북마크 → 내 표시 {nav}')
        ok(pg.evaluate("document.querySelector('#nav [data-nv=bm] [data-nb=bma]').textContent") == '3', f'{tag} 메뉴 숫자 3')
        pg.evaluate("document.querySelector('#nav [data-nv=bm]').click()"); pg.wait_for_timeout(1500)
        ok(len(pg.evaluate(CARDS)) > 20, f'{tag} (10-05) 기본 = 과목별 모든 강의 {len(pg.evaluate(CARDS))}')
        pg.evaluate("document.querySelector('#home [data-hbf=bm]').click()"); pg.wait_for_timeout(800)   # 10-05 ★ 북마크 거르기
        ok(pg.evaluate("location.hash") == '#/_bm' and pg.evaluate(CARDS) == ['CONS:INL', 'PHARM:XE', 'PHARM:ACU'], f'{tag} 전체 = 과목·강의 순서 {pg.evaluate(CARDS)}')
        ok(pg.evaluate("[...document.querySelectorAll('#home [data-hbt]')].map(b=>b.dataset.hbt)") == ['', 'CONS', 'PHARM'], f'{tag} 탭 전체·과목')
        ok(pg.evaluate("document.querySelectorAll('#home #hlec .lgrid .lcw .lcard .ltip').length") == 3, f'{tag} 과목 홈 카드 틀 + 📌 공부 전략')
        pg.evaluate("document.querySelector('#home [data-hbt=PHARM]').click()"); pg.wait_for_timeout(500)
        ok(pg.evaluate(CARDS) == ['PHARM:XE', 'PHARM:ACU'] and pg.evaluate("location.hash") == '#/_bm?s=PHARM', f'{tag} 약물 탭 → 그 과목만')
        pg.reload(); pg.wait_for_timeout(3000)
        ok(pg.evaluate(CARDS) == ['PHARM:XE', 'PHARM:ACU'], f'{tag} 새로고침 뒤 탭 유지')
        pg.evaluate("document.querySelector('#home [data-lbm=\"PHARM|ACU\"]').click()"); pg.wait_for_timeout(500)
        ok(pg.evaluate(CARDS) == ['PHARM:XE'] and pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.lbm.PHARM'))") == {'XE': 1}, f'{tag} ☆로 빼면 바로 빠짐')
        pg.evaluate("document.querySelector('#home [data-hbt=\"\"]').click()"); pg.wait_for_timeout(400)
        pg.evaluate("document.querySelector('#home .lcard[data-hbs=CONS]').click()"); pg.wait_for_timeout(2500)
        ok(pg.evaluate("location.hash") == '#/CONS/INL/learn', f'{tag} 카드 → 강의 학습 {pg.evaluate("location.hash")}')
        pg.go_back(); pg.wait_for_timeout(1500)
        ok(pg.evaluate("location.hash") == '#/_bm' and len(pg.evaluate(CARDS)) == 2, f'{tag} 뒤로 → 내 북마크')
        ok(pg.evaluate("document.documentElement.scrollWidth-innerWidth") <= 0, f'{tag} 가로 넘침 없음')
        ok(not errs, f'{tag} pageerror 0 {errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
