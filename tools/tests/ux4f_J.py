"""ux4f J 회귀 — 사용자 10-02 '집중모드에서 시간이 지날 때마다 집중모드의 상단바가 계속 꿈틀거리듯이 움직이는 오류, 집중모드에선 시간 클릭하면 바로 멈추거나 공부 재개할 수 없는 거'
J1 집중 모드 탭 줄(#dtabs) 높이·버튼 위치가 1초마다·공부 → 자리 비움 → 휴식으로 바뀌어도 그대로(한 가지)
J2 탭 줄 시계(.fclock)는 버튼 — 누르면 시계 창(■ 멈춤·☕ 쉬기·▶ 다시 공부), 창은 화면 안 · Esc로 닫으면 포커스가 탭 줄 시계로
J3 시계 창으로 쉬기 → 상태 휴식 · 다시 공부 → 공부(집중 모드는 그대로)"""
import os as _os, sys as _sys, datetime; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
W = "!!(window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni'))"
GEO = "(()=>{const t=document.querySelector('#dtabs');const r=t.getBoundingClientRect();return JSON.stringify([Math.round(r.height),[...t.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>Math.round(b.getBoundingClientRect().left))])})()"
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw, vh, touch in [(1280, 900, False), (820, 1180, True), (1180, 820, True)]:
        c = b.new_context(viewport={'width': vw, 'height': vh}, has_touch=touch); pg = c.new_page(); E = []
        pg.on('pageerror', lambda e: E.append(str(e)[:200]))
        pg.clock.install(time=datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0))
        def go(h):
            pg.goto('about:blank'); pg.goto(U + h); pg.clock.run_for(1500)
            for _ in range(150):
                if pg.evaluate(W): break
                pg.wait_for_timeout(100); pg.clock.run_for(100)
        go('#/'); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); go('#/CONS/WHT/learn')
        pg.keyboard.press('v'); pg.clock.run_for(800)
        ok(pg.evaluate("document.body.classList.contains('focus')"), f'{vw} V → 집중 모드')
        seen = {}; sts = set()
        for i in range(30):
            if i % 3 == 0: pg.mouse.move(400 + i, 500)
            pg.clock.run_for(1000); g = pg.evaluate(GEO); seen[g] = seen.get(g, 0) + 1; sts.add(pg.evaluate("document.querySelector('.fclock').dataset.st"))
        for i in range(12):
            pg.clock.run_for(60000); g = pg.evaluate(GEO); seen[g] = seen.get(g, 0) + 1; sts.add(pg.evaluate("document.querySelector('.fclock').dataset.st"))
        ok(len(seen) == 1 and 'rest' in sts, f'J1 {vw} 탭 줄 위치 한 가지(1초마다·상태 {sorted(sts)}) {len(seen)}')
        f = pg.evaluate("(f=>f&&[f.tagName,f.textContent.trim(),Math.round(f.getBoundingClientRect().height)])(document.querySelector('.fclock'))")
        ok(f and f[0] == 'BUTTON' and '휴식' in f[1] and f[2] >= (44 if touch else 30), f'J2 {vw} 탭 줄 시계 = 버튼 {f}')
        pg.click('.fclock'); pg.clock.run_for(300)
        r = pg.evaluate("(p=>{const q=p.getBoundingClientRect();return [p.classList.contains('on'),[...p.querySelectorAll('[data-tp]')].map(b=>b.textContent.trim()),q.left>=0&&q.right<=innerWidth&&q.top>=0]})(document.querySelector('#tpop'))")
        ok(r[0] and any('멈춤' in x for x in r[1]) and any('쉬기' in x for x in r[1]) and r[2], f'J2 {vw} 누르면 시계 창(화면 안) {r[1][:3]}')
        pg.keyboard.press('Escape'); pg.clock.run_for(200)
        ok(not pg.evaluate("document.querySelector('#tpop').classList.contains('on')") and pg.evaluate("document.activeElement&&document.activeElement.classList.contains('fclock')") and pg.evaluate("document.body.classList.contains('focus')"), f'J2 {vw} Esc = 창만 닫힘 · 포커스 탭 줄 시계 · 집중 그대로')
        pg.click('.fclock'); pg.clock.run_for(300)
        pg.evaluate("[...document.querySelectorAll('#tpop [data-tp]')].find(b=>/쉬기/.test(b.textContent)).click()"); pg.clock.run_for(1500)
        s1 = pg.evaluate("document.querySelector('.fclock').dataset.st")
        pg.click('.fclock'); pg.clock.run_for(300)
        lab = pg.evaluate("[...document.querySelectorAll('#tpop [data-tp]')].map(b=>b.textContent.trim())")
        pg.evaluate("(b=>b&&b.click())([...document.querySelectorAll('#tpop [data-tp]')].find(b=>/다시 공부|공부 시작/.test(b.textContent)))"); pg.clock.run_for(1500)
        s2 = pg.evaluate("document.querySelector('.fclock').dataset.st")
        ok(s1 == 'rest' and s2 in ('run', 'sess') and pg.evaluate("document.body.classList.contains('focus')"), f'J3 {vw} 쉬기 → {s1} · 다시 공부 → {s2} (창 {lab[:2]})')
        ok(not E, f'{vw} 콘솔 오류 없음 {E[:2]}')
        c.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
