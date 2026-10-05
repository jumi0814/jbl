"""ux4f P 회귀 — 사용자 10-03 요청 3가지
P1 'h로 하이라이트 킨 상태에서 t를 누르면 도구창만 사라지면 되는데' — H → T: 막대만 숨김 · 형광펜 모드 그대로 · 숨긴 채 칠해짐 · 알림
P2 '카드마다 젤 아래쪽에 다 봄 표시는 필요없고 북마크' — 카드 끝 ☆ 북마크(다 봄 버튼 없음) · LS cbm.<S> · D 키 · 새로고침 유지 ·
   강의 [보기 ▾] → ★ 북마크 카드만 · 과목 메뉴 '★ 북마크 카드'(#/<S>/_cbm — 강의 순서, 그림 그려짐) · 과목 홈 '북마크 카드 n장' · 백업 합치기 = 합집합 · 옛 done.<S> 그대로
P3 '강의자료화면이 자꾸 미세하게 간헐적으로 왼쪽 오른쪽으로 작게 움직이는' — 스크롤·시계 갱신 중 탭 줄·미니바·본문 가로 위치 변화 0(1280·820 터치·1180 터치)"""
import os as _os, sys as _sys, json; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
def new(b, w, h, touch):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch)
    ctx.add_init_script("try{if(!localStorage.getItem('jblhub.v1.whatsNew.4'))localStorage.setItem('jblhub.v1.whatsNew.4','1')}catch(e){}")
    pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    return ctx, pg
def go(pg, h, w=1000):
    pg.goto('about:blank'); pg.goto(U + '#' + h); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(w)
GEO = """(()=>{const r=s=>{const e=document.querySelector(s);if(!e||!e.offsetParent)return '-';const q=e.getBoundingClientRect();return Math.round(q.left*10)/10+':'+Math.round(q.width*10)/10};
 return ['#crumb .ccur','#gsearch','#clock','#dtabs','#lmini','#lmview','#dfocus','#stage'].map(r).join(' ')+' '+(document.documentElement.scrollWidth-innerWidth)})()"""
with sync_playwright() as p:
    b = p.chromium.launch(ignore_default_args=['--hide-scrollbars'])
    for W, H, T in [(1280, 900, False), (820, 1180, True), (1180, 820, True)]:
        ctx, pg = new(b, W, H, T); go(pg, '/'); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1');localStorage.setItem('jblhub.v1.done.ESTH',JSON.stringify({'x':1}))")
        # ---------- P1 ----------
        go(pg, '/ESTH/FUN/learn')
        pg.keyboard.press('h'); pg.wait_for_timeout(150); pg.keyboard.press('t'); pg.wait_for_timeout(300)
        r = pg.evaluate("[__h.Kit.mode(),document.body.classList.contains('mode-h'),document.body.classList.contains('kit-off'),getComputedStyle(document.querySelector('#kit')).display,document.querySelector('#toast').textContent]")
        ok(r[0] == 'h' and r[1] and r[2] and r[3] == 'none' and '켜진 채' in r[4], f'P1 {W} H → T = 막대만 숨김 · 형광펜 그대로 · 알림 {r[:4]} {r[4][:30]!r}')
        n0 = pg.evaluate("document.querySelectorAll('#stage [data-rk]').length")
        pt = pg.evaluate("(()=>{const e=[...document.querySelectorAll('#stage .tc .tbody li')].filter(l=>l.offsetParent&&l.textContent.length>30&&!l.querySelector('button,.chip,a,[data-rk]'))[3];e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return [r.left+24,r.top+10]})()")
        pg.wait_for_timeout(300); (pg.touchscreen.tap if T else pg.mouse.click)(pt[0], pt[1]); pg.wait_for_timeout(400)
        ok(pg.evaluate("document.querySelectorAll('#stage [data-rk]').length") > n0, f'P1 {W} 막대를 숨긴 채 칠해짐')
        pg.keyboard.press('h'); pg.wait_for_timeout(150); pg.keyboard.press('t'); pg.wait_for_timeout(200)
        ok(pg.evaluate("[__h.Kit.mode(),document.body.classList.contains('kit-off')]") == [None, False], f'P1 {W} H로 끄고 T로 막대 다시')
        # ---------- P2 ----------
        r = pg.evaluate("[document.querySelectorAll('#stage .tc>.cbend').length,document.querySelectorAll('#stage .tc').length,document.querySelectorAll('#stage .dnend').length]")
        ok(r[0] > 0 and r[0] == r[1] and r[2] == 0, f'P2 {W} 카드마다 끝 ☆ 북마크 · 다 봄 버튼 없음 {r}')
        bh = pg.evaluate("Math.round(document.querySelector('#stage .tc>.cbend').getBoundingClientRect().height)")
        ok(bh >= (44 if T else 28), f'P2 {W} 북마크 버튼 높이 {bh}')
        aids = []
        for i in (1, 4):
            pg.evaluate(f"document.querySelectorAll('#stage .tc')[{i}].querySelector(':scope>.cbend').scrollIntoView({{block:'center'}})"); pg.wait_for_timeout(250)
            box = pg.evaluate(f"(e=>{{const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}})(document.querySelectorAll('#stage .tc')[{i}].querySelector(':scope>.cbend'))")
            h0 = pg.evaluate("location.hash"); (pg.touchscreen.tap if T else pg.mouse.click)(box[0], box[1]); pg.wait_for_timeout(350)
            aids.append(pg.evaluate(f"document.querySelectorAll('#stage .tc')[{i}].dataset.aid"))
        L = pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.cbm.ESTH')||'{}')")
        ok(set(L) == set(aids) and pg.evaluate("document.querySelectorAll('#stage .tc.cbm').length") == 2 and pg.evaluate("location.hash") == h0, f'P2 {W} 두 카드 ★ → cbm.ESTH {len(L)} · 화면 그대로')
        pg.evaluate("document.querySelectorAll('#stage .tc')[6].scrollIntoView({block:'start'})"); pg.wait_for_timeout(600)
        c6 = pg.evaluate("__h.curCard?(__h.curCard()||{}).dataset.aid:null")
        pg.keyboard.press('d'); pg.wait_for_timeout(300)
        L = pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.cbm.ESTH')||'{}')")
        ok(len(L) == 3 and (c6 is None or c6 in L), f'P2 {W} D = 지금 카드 북마크 {len(L)}')
        pg.evaluate("document.querySelector('#lmview').click()"); pg.wait_for_timeout(250); pg.evaluate("document.querySelector('#lmcbm').click()"); pg.wait_for_timeout(500)
        pg.evaluate("document.querySelector('#stage .hlbar [data-hlf=bm]').click()"); pg.wait_for_timeout(300)   # 10-05 강조 카드 보기(⭐ 기출 ∪ ★ 북마크) → 토글 ★ 북마크만
        r = pg.evaluate("[[...document.querySelectorAll('#stage .tc')].filter(c=>c.offsetParent).length,document.querySelector('#lmview').textContent,document.querySelector('#stage').classList.contains('cbmonly')]")
        ok(r[0] == 3 and '★' in r[1] and r[2], f'P2 {W} [보기 ▾] → ★ 북마크 카드만 {r}')
        pg.reload(); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1000)
        ok(pg.evaluate("document.querySelectorAll('#stage .tc.cbm').length") == 3 and not pg.evaluate("document.querySelector('#stage').classList.contains('cbmonly')"), f'P2 {W} 새로고침 → ★ 3장 그대로(보기는 전체로)')
        go(pg, '/ESTH/_cbm', 2500)
        r = pg.evaluate("[document.querySelectorAll('#stage .tc').length,document.querySelectorAll('#stage h3.cbmh').length,document.querySelector('#stage h2').textContent,document.querySelectorAll('#stage .tc img[src]').length,document.querySelectorAll('#stage .tc img[data-img]').length,(document.querySelector('#nav .nvd[data-d=_cbm]')||{}).textContent]")
        ok(r[0] == 3 and r[1] == 1 and '3장' in r[2] and r[4] > 0 and '북마크 카드' in (r[5] or ''), f'P2 {W} 과목 ★ 북마크 카드 모아 보기 {r}')
        pg.evaluate("__h.fillAll()"); pg.wait_for_timeout(1500)
        r2 = pg.evaluate("[document.querySelectorAll('#stage .tc img[src]').length,document.querySelectorAll('#stage .tc img[data-img]').length]")
        ok(r2[0] == r2[1], f'P2 {W} 모아 보기 그림이 그려짐 {r2}')
        pg.evaluate("document.querySelector('#stage [data-cbmgo]').click()"); pg.wait_for_timeout(800)
        ok(pg.evaluate("location.hash").startswith('#/ESTH/FUN/learn'), f'P2 {W} 강의로 → 그 강의 학습')
        go(pg, '/ESTH/_home/_home')
        ok('북마크 카드 3장' in pg.evaluate("(document.querySelector('#hlec .cbmrow')||{}).textContent||''"), f'P2 {W} 과목 홈 ★ 북마크 카드 3장 줄')
        ok(pg.evaluate("localStorage.getItem('jblhub.v1.done.ESTH')") == '{"x":1}', f'P2 {W} 옛 다 봄 기록(done.ESTH) 그대로')
        n = pg.evaluate("__h.mergeData({'jblhub.v1.cbm.ESTH':JSON.stringify({'ESTH:X:y':5})}).n")
        ok(len(pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.cbm.ESTH'))")) == 4, f'P2 {W} 백업 합치기 = 합집합 {n}')
        # ---------- P3 ----------
        for route, foc in (('/ESTH/COL/learn', False), ('/ESTH/VEN/learn', True)):
            go(pg, route, 1500)
            if foc: pg.keyboard.press('v'); pg.wait_for_timeout(700)
            pg.mouse.move(500, 500); pg.wait_for_timeout(300); seen = set()
            for i in range(60):
                if i % 15 == 0: pg.mouse.move(500 + i, 500)
                if i in (15, 30): pg.mouse.wheel(0, 1500)
                if i == 45: pg.mouse.wheel(0, -1000)
                seen.add(pg.evaluate(GEO)); pg.wait_for_timeout(100)
            ok(len(seen) == 1, f'P3 {W} {route}{" 집중" if foc else ""} 스크롤·시계 갱신 중 가로 위치 한 가지 ({len(seen)}) {sorted(seen)[:2]}')
        ok(not pg.errs, f'{W} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
