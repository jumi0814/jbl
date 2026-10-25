"""10-25 사용자 '툴바가 갑자기 중앙이 아닌 오른쪽에 뜰 때가 있는데 …', '답 펼치기를 누르면 가끔 위로 펼쳐지면서 스크롤해야하는데, 항상 화면 기준 그냥 아래쪽으로' 회귀.
① 아래 도구 막대(#kit) = 메뉴를 뺀 본문 폭의 가운데(1100·1440·2000, 집중 모드면 화면 가운데) · 폰은 화면 안
② 기출·예상 '답 모두 펼치기/접기'(#frev) — 보던 카드(화면 맨 위 카드)가 같은 화면 위치(±3px)에 그대로
③ 위에 붙는 탭 줄·거르기 막대가 불투명(반투명이면 뒤 카드 글자가 비침 — 사용자 사진 PHARM HM)"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
KX = "(()=>{const k=document.querySelector('#kit'),r=k.getBoundingClientRect(),sw=parseFloat(getComputedStyle(k).left)||0,W=document.documentElement.clientWidth;return [Math.round((r.left+r.right)/2-(sw+(W-sw)/2)),Math.round(r.left),Math.round(r.right),W]})()"
CARD = "i=>{const c=[...document.querySelectorAll('#stage .qc,#stage .pc')].filter(x=>x.offsetParent)[i];if(!c)return '';c.dataset.kf=String(i);return String(i)}"
TOP = "i=>{const c=document.querySelector('#stage [data-kf=\"'+i+'\"]');return c?Math.round(c.getBoundingClientRect().top):null}"
alpha = lambda c: float(re.findall(r'[\d.]+', c)[3]) if c.startswith('rgba') else 1.0
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (1100, 1440, 2000):
        pg = b.new_page(viewport={'width': w, 'height': 1000}); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto(J.HUB_URL + '#/PHARM/HM/jb'); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1200)
        k = pg.evaluate(KX); ok(abs(k[0]) <= 2 and k[2] <= k[3], f'{w} ① 도구 막대 본문 가운데 {k}')
        pg.evaluate("document.querySelector('.dfoc').click()"); pg.wait_for_timeout(500)
        k = pg.evaluate(KX); ok(abs(k[0]) <= 2, f'{w} ① 집중 모드 — 화면 가운데 {k}')
        pg.evaluate("document.querySelector('.dfoc').click()"); pg.wait_for_timeout(400)
        for tab in ('jb', 'pred'):
            if tab == 'pred': pg.goto(J.HUB_URL + '#/PHARM/HM/pred'); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1000)
            for i in (5, 9):
                cid = pg.evaluate(CARD, i)
                if not cid: continue
                pg.evaluate("i=>{const c=document.querySelector('#stage [data-kf=\"'+i+'\"]');scrollTo(0,c.getBoundingClientRect().top+scrollY-230)}", cid); pg.wait_for_timeout(500)
                t0 = pg.evaluate(TOP, cid); pg.click('#frev'); pg.wait_for_timeout(1700); t1 = pg.evaluate(TOP, cid)
                pg.click('#frev'); pg.wait_for_timeout(1700); t2 = pg.evaluate(TOP, cid)
                ok(t0 is not None and abs(t1 - t0) <= 3 and abs(t2 - t0) <= 3, f'{w} ② {tab} {i + 1}번째 카드 답 모두 펼치기·접기 뒤 같은 자리 {t0} → {t1} → {t2}')
        pg.goto(J.HUB_URL + '#/PHARM/HM/jb'); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(900); pg.evaluate("scrollTo(0,2500)"); pg.wait_for_timeout(500)
        bg = pg.evaluate("['#dtabs','#jbbar','#top'].map(s=>{const e=document.querySelector(s);return e?getComputedStyle(e).backgroundColor:'rgb(0,0,0)'})")
        ok(all(alpha(c) >= 0.999 for c in bg), f'{w} ③ 위에 붙는 막대 불투명 {bg}')
        pg.close()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(J.HUB_URL + '#/GERI/SAL/learn'); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1200)
    if pg.evaluate("document.body.classList.contains('kit-off')"): pg.evaluate("document.querySelector('[data-kitt]').click()"); pg.wait_for_timeout(500)
    k = pg.evaluate("(()=>{const e=document.querySelector('#kit');const r=e.getBoundingClientRect();if(!r.width)return null;const f=e.querySelector('button').getBoundingClientRect();return [Math.round(r.left),Math.round(r.right),innerWidth,Math.round(f.left)]})()")
    ok(k is not None and k[0] >= 0 and k[1] <= k[2] and k[3] >= 0, f'390 ① 도구 막대·첫 단추(형광펜) 화면 안 {k}')
    b.close()
ok(not errs, f'pageerror 0 {errs[:2]}')
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
sys.exit(1 if fails else 0)
