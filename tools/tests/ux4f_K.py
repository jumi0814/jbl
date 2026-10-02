"""ux4f K 회귀 — 사용자 10-02 '자동측정을 껐다 켰는데 자동측정 기능이 갑자기 안되는 오류' · '단축어 shift m이 메뉴탭, m은 메모장'
K1 ■ 멈춤 뒤 측정 설정에서 자동 측정을 껐다 켜면 멈춤이 풀려 같은 강의에서 움직이면 다시 잼(전에는 '멈춤'에 그대로)
K2 ■ 멈춤 뒤 시계 창 '↻ 자동 측정 다시' 한 번 = 곧바로 잼 · 자동 측정 꺼짐이면 '↻ 자동 측정 켜기'
K3 단축키: M = 메모 · Shift+M = 메뉴 숨기기/보이기(한글 입력 'ㅡ'+Shift도) · 허브에서 M은 안내만"""
import os as _os, sys as _sys, datetime; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
W = "!!(window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni'))"
td = datetime.date.today().isoformat()
with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(viewport={'width': 1280, 'height': 900}); pg = c.new_page(); E = []
    pg.on('pageerror', lambda e: E.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept())
    pg.clock.install(time=datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0))
    def go(h, hard=True):
        if hard: pg.goto('about:blank'); pg.goto(U + h)
        else: pg.evaluate(f"location.hash='{h}'")
        pg.clock.run_for(1500)
        for _ in range(150):
            if pg.evaluate(W): break
            pg.wait_for_timeout(100); pg.clock.run_for(100)
    st = lambda: pg.evaluate("__h.trState()")
    def move(n=4):
        for i in range(n): pg.mouse.move(300 + i * 20, 420 + i); pg.clock.run_for(20000)
    def pop(rx):
        pg.evaluate("document.querySelector('#clock').click()"); pg.clock.run_for(300)
        return pg.evaluate(f"(b=>b?(b.click(),b.textContent.trim()):null)([...document.querySelectorAll('#tpop [data-tp]')].find(b=>/{rx}/.test(b.textContent)))")
    go('#/'); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); go('#/CONS/WHT/learn')
    move(3); ok(st() == 'run', f'K0 강의에서 움직이면 자동 측정 {st()}')
    pop('멈춤'); pg.clock.run_for(500); ok(st() == 'end', f'K1 ■ 멈춤 → {st()}')
    go('#/_cal/' + td, False); pg.evaluate("document.querySelector('#calmset').open=true"); pg.clock.run_for(300)
    pg.click('input[data-cset=tauto]'); pg.clock.run_for(400); s_off = st(); pg.click('input[data-cset=tauto]'); pg.clock.run_for(400); s_on = st()
    go('#/CONS/WHT/learn', False); move(4)
    ok(s_off == 'off' and s_on == 'wait' and st() == 'run', f'K1 껐다 켜기 {s_off} → {s_on} → 강의에서 움직이면 {st()}')
    pop('멈춤'); pg.clock.run_for(500)
    lab = pop('자동 측정 다시'); pg.clock.run_for(500); move(1)
    ok(lab and st() == 'run', f'K2 멈춤 → 시계 창 [{lab}] → {st()}')
    pg.evaluate("localStorage.setItem('jblhub.v1.tauto','false')"); go('#/CONS/WHT/learn'); move(1)
    lab2 = pop('자동 측정 켜기'); pg.clock.run_for(500); move(2)
    ok(st() == 'off' or (lab2 and st() == 'run'), f'K2 꺼짐 → [{lab2}] → {st()}')
    # K3 단축키
    go('#/CONS/WHT/learn'); pg.keyboard.press('Escape')
    pg.keyboard.press('m'); pg.clock.run_for(300)
    m1 = pg.evaluate("[document.querySelector('#memo').classList.contains('on'),document.activeElement&&document.activeElement.id,document.body.classList.contains('sidefold')]")
    pg.keyboard.press('Escape'); pg.clock.run_for(300)
    f0 = pg.evaluate("document.body.classList.contains('sidefold')")
    pg.evaluate("document.body.focus()"); pg.keyboard.press('Shift+M'); pg.clock.run_for(500); f1 = pg.evaluate("document.body.classList.contains('sidefold')")
    pg.evaluate("document.dispatchEvent(new KeyboardEvent('keydown',{key:'ㅡ',code:'KeyM',shiftKey:true,bubbles:true}))"); pg.clock.run_for(500); f2 = pg.evaluate("document.body.classList.contains('sidefold')")
    ok(m1[0] and m1[1] == 'memota' and m1[2] == f0, f'K3 M → 메모(메뉴 그대로) {m1}')
    ok(f1 != f0 and f2 == f0, f'K3 Shift+M → 메뉴 {f0}→{f1} · 한글 ㅡ+Shift → {f2}')
    go('#/'); pg.evaluate("sessionStorage.removeItem('jblhub.v1.toasts')"); pg.keyboard.press('m'); pg.clock.run_for(300)
    ok(not pg.evaluate("document.querySelector('#memo').classList.contains('on')") and '메모' in pg.evaluate("document.querySelector('#toast').textContent"), 'K3 허브에서 M = 안내만(메모 창 안 열림)')
    ok(not E, f'콘솔 오류 없음 {E[:2]}')
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
