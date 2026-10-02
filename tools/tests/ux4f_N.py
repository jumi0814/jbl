"""ux4f N 회귀 — 새 오류 찾기 2회차(집중 모드·키·도구) 8건
N1 [카드 ▾]·[보기 ▾]·시계 창이 열린 채 V(집중)·Shift+M(메뉴)·회전 → 창 닫힘(옛 자리·화면 밖에 남지 않음)
N2 [카드 ▾]가 열린 채 M → 목록이 닫히고 메모가 보임
N3 과목 홈 ☆ 처음 누른 뒤 같은 자리 = 그 ☆ 그대로(★ 줄이 생겨도 밀리지 않음)
N4 집중 모드 탭 줄 가로 넘침 0(820·1180·1280) · '플래시카드' 탭이 다른 것에 가리지 않음
N5 820 서랍이 열린 채 H·Q·M 등 = 서랍 먼저 닫힘
N6 포인터로 누른 체크박스에 포커스가 남은 채 Space = 설정 그대로
N7 Q 뒤 J/K로 옮기고 곧바로 새로고침 = 그 카드
N8 아이패드 [카드 ▾]·[보기 ▾] 44px"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
W = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
def new(b, w, h, t):
    c = b.new_context(viewport={'width': w, 'height': h}, has_touch=t); c.add_init_script("try{if(!localStorage.getItem('jblhub.v1.whatsNew.4'))localStorage.setItem('jblhub.v1.whatsNew.4','1')}catch(e){}")
    pg = c.new_page(); pg.errs = []; pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); return c, pg
def go(pg, h, w=800):
    pg.goto('about:blank'); pg.goto(U + '#' + h); pg.wait_for_function(W, timeout=60000); pg.wait_for_timeout(w)
KEY = lambda k, c, s=False: f"document.dispatchEvent(new KeyboardEvent('keydown',{{key:'{k}',code:'{c}',shiftKey:{str(s).lower()},bubbles:true}}))"
ON = "(q=>{const e=document.querySelector(q);return !!(e&&e.classList.contains('on'))})"
with sync_playwright() as p:
    b = p.chromium.launch()
    for W_, H_, T in [(1280, 900, False), (1180, 820, True), (820, 1180, True)]:
        c, pg = new(b, W_, H_, T); go(pg, '/CONS/WHT/learn'); pg.evaluate("scrollTo(0,900)"); pg.wait_for_timeout(300)
        # N1
        for btn, pop in [('#lmcur', '#lpop'), ('#lmview', '#lvpop')]:
            pg.click(btn); pg.wait_for_timeout(250); a = pg.evaluate(ON + f"('{pop}')")
            pg.evaluate(KEY('ㅍ', 'KeyV')); pg.wait_for_timeout(400); z = pg.evaluate(ON + f"('{pop}')"); ex = pg.evaluate(f"document.querySelector('{btn}').getAttribute('aria-expanded')")
            ok(a and not z and ex != 'true', f'N1 {W_} {btn} 연 채 V → 창 닫힘 {a}->{z} aria {ex}')
            pg.evaluate(KEY('ㅍ', 'KeyV')); pg.wait_for_timeout(400)
        pg.click('#lmcur'); pg.wait_for_timeout(250); pg.set_viewport_size({'width': H_, 'height': W_}); pg.wait_for_timeout(500)
        ok(not pg.evaluate(ON + "('#lpop')"), f'N1 {W_} [카드 ▾] 연 채 회전 → 닫힘'); pg.set_viewport_size({'width': W_, 'height': H_}); pg.wait_for_timeout(500)
        # N2
        pg.click('#lmcur'); pg.wait_for_timeout(250); pg.evaluate(KEY('ㅡ', 'KeyM')); pg.wait_for_timeout(300)
        r = pg.evaluate("(()=>{const m=document.querySelector('#memo');const q=m.getBoundingClientRect();const e=document.elementFromPoint(q.left+q.width/2,q.top+q.height/2);return [m.classList.contains('on'),!!(e&&e.closest('#memo')),document.querySelector('#lpop').classList.contains('on')]})()")
        ok(r[0] and r[1] and not r[2], f'N2 {W_} [카드 ▾] 연 채 M → 메모가 위·목록 닫힘 {r}')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        # N4
        pg.evaluate(KEY('ㅍ', 'KeyV')); pg.wait_for_timeout(500)
        r = pg.evaluate("(()=>{const t=document.querySelector('#dtabs');const f=[...t.querySelectorAll('button[data-t]')].pop();const q=f.getBoundingClientRect();const e=document.elementFromPoint(q.right-6,q.top+q.height/2);return [t.scrollWidth-t.clientWidth,!!(e&&e.closest('button[data-t]')===f),f.textContent.trim()]})()")
        ok(r[0] <= 0 and r[1], f'N4 {W_} 집중 탭 줄 넘침 {r[0]} · 마지막 탭 보임 {r}')
        pg.evaluate(KEY('ㅍ', 'KeyV')); pg.wait_for_timeout(400)
        # N8
        if T:
            h = pg.evaluate("[...['#lmcur','#lmview']].map(q=>Math.round(document.querySelector(q).getBoundingClientRect().height))"); ok(min(h) >= 44, f'N8 {W_} [카드 ▾]·[보기 ▾] {h}')
        # N6
        pg.click('#k-auto'); pg.wait_for_timeout(300)
        if pg.evaluate("!!document.querySelector('#pendir')&&!!document.querySelector('#pendir').offsetParent"):
            pg.click('#pendir'); pg.wait_for_timeout(300); v0 = pg.evaluate("localStorage.getItem('jblhub.v1.penDirect')")
            pg.keyboard.press(' '); pg.wait_for_timeout(300); v1 = pg.evaluate("localStorage.getItem('jblhub.v1.penDirect')")
            ok(v0 == v1, f'N6 {W_} 누른 체크박스 + Space → 설정 그대로 {v0} {v1}')
        pg.keyboard.press('Escape')
        # N7
        go(pg, '/CONS/WHT/learn'); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(300)
        for k in 'jjjjjj': pg.evaluate(KEY('ㅓ', 'KeyJ')); pg.wait_for_timeout(450)
        pg.evaluate(KEY('ㅂ', 'KeyQ')); pg.wait_for_timeout(450)
        for k in 'kk': pg.evaluate(KEY('ㅏ', 'KeyK')); pg.wait_for_timeout(450)
        lab = pg.evaluate("document.querySelector('#lmcur').textContent"); pg.reload(); pg.wait_for_function(W, timeout=60000); pg.wait_for_timeout(1200)
        lab2 = pg.evaluate("document.querySelector('#lmcur').textContent")
        ok(lab == lab2, f'N7 {W_} Q 뒤 J/K → 새로고침 같은 카드 {lab} {lab2}')
        ok(not pg.errs, f'{W_} 콘솔 오류 없음 {pg.errs[:2]}'); c.close()
    # N3·N5 (820 터치)
    c, pg = new(b, 820, 1180, True); go(pg, '/CONS/_home/_home')
    pg.evaluate("document.querySelector('#hlec').scrollIntoView()"); pg.wait_for_timeout(300)
    q = pg.evaluate("(b=>{const r=b.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})(document.querySelectorAll('#hlec .lbm')[2])")
    pg.mouse.click(q[0], q[1]); pg.wait_for_timeout(400)
    e = pg.evaluate(f"(e=>e&&e.closest('.lbm')?e.closest('.lbm').dataset.lbm:null)(document.elementFromPoint({q[0]},{q[1]}))")
    pg.mouse.click(q[0], q[1]); pg.wait_for_timeout(400)
    ok(e and pg.evaluate("location.hash").startswith('#/CONS/_home') and pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.lbm.CONS')||'{}')") == {}, f'N3 ☆ 두 번 같은 자리 = 켰다 끔(강의로 가지 않음) {e}')
    go(pg, '/CONS/WHT/learn')
    for k, code in [('ㅗ', 'KeyH'), ('ㅂ', 'KeyQ'), ('ㅡ', 'KeyM')]:
        pg.evaluate("document.querySelector('#navbtn').click()"); pg.wait_for_timeout(400)
        pg.evaluate(KEY(k, code)); pg.wait_for_timeout(400)
        ok(not pg.evaluate("document.body.classList.contains('navopen')"), f'N5 서랍 열린 채 {code} → 서랍 닫힘')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(not pg.errs, f'N3·N5 콘솔 오류 없음 {pg.errs[:2]}'); c.close(); b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
