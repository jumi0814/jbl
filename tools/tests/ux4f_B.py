"""ux4f 범위 B 회귀 — 강의 학습 탭·도구 막대·미니바 오류 재검(n 23~34).
23 막대를 숨기면(T·✕) 형광펜·빈칸 모드 끔 · 견본 창 닫힘 · 숨긴 채 누르면 표시 없음
24 [카드 ▾]·[보기 ▾] 창이 화면(도구 막대 위) 안 — 낮은 창·창 높이를 줄여도
25 C(압축) 뒤 지금 카드 그대로 · J = 다음 카드(J×3·J×6·사이드바에서 고른 카드)
26 / → Esc → 검색칸에서 나옴(글자를 친 뒤에도) · 집중 모드 상단 막대 다시 숨음
27 🧹 이 카드 테두리 → Esc·T로 닫아도 없음
28 맨 위(틀)에서 K → 그대로 · 카드 1에서 K → 틀
29 [카드 ▾] 창이 버튼 아래(집중 모드·보통)
30 세로 820 서랍이 열린 채 V → 서랍 닫고 집중
31 복습 보기 필터·정렬·알림·도움말에 옛 '읽음'·'[⚡ 복습](R)' 말 없음
32 [보기 ▾] 겹친 보기는 버튼에 모두 · 복습 중 '가리기'를 눌러도 가리기가 꺼지지 않음
33 되돌리기 알림 뒤 다음 동작 알림이 곧바로
34 🧹 창 좌우 여백 12px 이상
맥 1280×900(·1280×760) · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)"""
import os as _os, sys as _sys, time; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def new(b, w, h, touch=False):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch); pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    pg.on('dialog', lambda d: d.accept())
    pg.goto('about:blank'); pg.goto(U + '#/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')")
    return ctx, pg
def go(pg, h, wait=1200):
    pg.goto('about:blank'); pg.goto(U + h)
    pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')", timeout=60000); pg.wait_for_timeout(wait)
GEO = "(()=>{const line=innerHeight*.3;let j=-1;for(const c of document.querySelectorAll('#stage .tc')){if(c.offsetParent===null)continue;if(c.getBoundingClientRect().top<=line)j=+c.id.split('-').pop();else break}return j})()"
R4 = "(e=>{const r=e.getBoundingClientRect();return [r.left,r.top,r.right,r.bottom].map(Math.round)})"
VPS = [('mac', 1280, 900, False), ('land', 1180, 820, True), ('port', 820, 1180, True)]

def kit(b):
    print('== 23·27·34 도구 막대')
    for tag, w, h, t in VPS:
        ctx, pg = new(b, w, h, t); go(pg, '#/CONS/WHT/learn')
        # 23 빈칸 모드 + 견본 창 → T 두 번
        pg.keyboard.press('b'); pg.wait_for_timeout(100)
        pg.evaluate("['#k-sw','#k-bsw'].forEach(q=>{const e=document.querySelector(q);if(e)e.classList.add('open')})")
        pg.keyboard.press('t'); pg.wait_for_timeout(150)
        r = pg.evaluate("[__h.Kit.mode(),document.body.classList.contains('mode-b'),document.body.classList.contains('kit-off'),document.querySelectorAll('#k-sw.open,#k-bsw.open').length]")
        ok(r == [None, False, True, 0], f'{tag} B → T: 빈칸 모드 꺼짐 · 견본 창 닫힘 {r}')
        pg.keyboard.press('t'); pg.wait_for_timeout(150)
        r = pg.evaluate("[document.body.classList.contains('kit-off'),document.querySelector('#k-b').getAttribute('aria-pressed'),document.querySelectorAll('#k-sw.open,#k-bsw.open').length]")
        ok(r == [False, 'false', 0], f'{tag} 다시 T → 막대 보임 · 빈칸 버튼 안 눌림 · 견본 창 닫힌 채 {r}')
        # 23 막대 ✕로 숨겨도 같음
        pg.keyboard.press('h'); pg.wait_for_timeout(100); pg.click('#k-hide'); pg.wait_for_timeout(200)
        n0 = pg.evaluate("document.querySelectorAll('#stage .rk-h,#stage .rk-b').length")
        li = pg.evaluate("(()=>{const e=document.querySelectorAll('#stage .tc .tbody :is(li,.li)')[2];e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return [r.left+20,r.top+8]})()")
        pg.wait_for_timeout(200); (pg.touchscreen.tap if t else pg.mouse.click)(li[0], li[1]); pg.wait_for_timeout(300)
        ok(pg.evaluate("__h.Kit.mode()") is None and pg.evaluate("document.querySelectorAll('#stage .rk-h,#stage .rk-b').length") == n0, f'{tag} H → 막대 ✕ → 모드 꺼짐 · 눌러도 표시 없음')
        pg.keyboard.press('t'); pg.wait_for_timeout(200)
        # 27 🧹 이 카드 → T
        pg.evaluate("document.querySelectorAll('#stage .tc')[3].scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
        pg.click('#k-clear'); pg.wait_for_timeout(200); pg.click('#clearpop [data-csc=card]'); pg.wait_for_timeout(150)
        # 34 🧹 창 여백
        r = pg.evaluate(R4 + "(document.querySelector('#clearpop'))")
        ok(r[0] >= 12 and r[2] <= w - 12, f'{tag} 🧹 창 좌우 여백 12px 이상 {r} / {w}')
        a = pg.evaluate("document.querySelectorAll('#stage .clrtgt').length"); pg.keyboard.press('t'); pg.wait_for_timeout(200)
        ok(a == 1 and pg.evaluate("document.querySelectorAll('#stage .clrtgt').length") == 0 and not pg.evaluate("document.querySelector('#clearpop').classList.contains('on')"), f'{tag} 🧹 이 카드 테두리 → T → 창·테두리 없음')
        pg.keyboard.press('t'); pg.wait_for_timeout(200)
        pg.click('#k-clear'); pg.wait_for_timeout(200); pg.click('#clearpop [data-csc=card]'); pg.wait_for_timeout(150); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.querySelectorAll('#stage .clrtgt').length") == 0, f'{tag} 🧹 이 카드 테두리 → Esc → 없음')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()
    ctx, pg = new(b, 700, 1000); go(pg, '#/CONS/WHT/learn'); pg.click('#k-clear'); pg.wait_for_timeout(300)
    r = pg.evaluate(R4 + "(document.querySelector('#clearpop'))")
    ok(r[0] >= 12 and r[2] <= 700 - 12, f'700 🧹 창 좌우 여백 {r}')
    ctx.close()

def pops(b):
    print('== 24·29 [카드 ▾]·[보기 ▾] 창 자리')
    for tag, w, h, t in VPS + [('mac760', 1280, 760, False)]:
        ctx, pg = new(b, w, h, t); go(pg, '#/CONS/WHT/learn'); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(400)
        for focus in (False, True):
            if focus: pg.keyboard.press('v'); pg.wait_for_timeout(500)
            f = '집중 ' if focus else ''
            pg.click('#lmcur'); pg.wait_for_timeout(300); pg.evaluate("document.querySelector('#lpop').scrollTop=1e5"); pg.wait_for_timeout(150)
            r = pg.evaluate("(()=>{const p=document.querySelector('#lpop').getBoundingClientRect(),L=[...document.querySelectorAll('#lpop .lpi')].pop().getBoundingClientRect(),k=document.querySelector('#kit'),kt=k.offsetParent?k.getBoundingClientRect().top:innerHeight,b=document.querySelector('#lmcur').getBoundingClientRect();return [Math.round(L.bottom),Math.round(p.bottom),Math.round(kt),Math.round(p.left),Math.round(p.right),Math.round(b.left),Math.round(b.right),Math.round(p.top-b.bottom),innerWidth]})()")
            ok(r[0] <= r[2] and r[1] <= r[2], f'{tag} {f}[카드 ▾] 끝까지 굴리면 마지막 카드가 도구 막대 위 {r[:3]}')
            ok(r[3] >= 8 and r[4] <= r[8] - 8 and r[3] < r[6] and r[4] > r[5] and 0 <= r[7] <= 12, f'{tag} {f}[카드 ▾] 창이 버튼 바로 아래(겹침·화면 안) {r[3:]}')
            pg.click('#lmcur'); pg.wait_for_timeout(150)
            pg.click('#lmview'); pg.wait_for_timeout(200)
            r = pg.evaluate("[Math.round(document.querySelector('#lvpop').getBoundingClientRect().bottom),Math.round(document.querySelector('#lvpop').getBoundingClientRect().right),Math.round(document.querySelector('#lmview').getBoundingClientRect().right),innerHeight]")
            ok(r[0] <= r[3] and abs(r[1] - r[2]) <= 2, f'{tag} {f}[보기 ▾] 창이 화면 안 · 버튼 오른쪽 끝에 맞춤 {r}')
            pg.click('#lmview'); pg.wait_for_timeout(150)
        pg.keyboard.press('v'); pg.wait_for_timeout(400)
        if tag == 'mac760':   # 창 높이를 줄여도
            pg.click('#lmcur'); pg.wait_for_timeout(200); pg.set_viewport_size({'width': w, 'height': 600}); pg.wait_for_timeout(500)
            pg.evaluate("document.querySelector('#lpop').scrollTop=1e5"); pg.wait_for_timeout(150)
            r = pg.evaluate("[Math.round([...document.querySelectorAll('#lpop .lpi')].pop().getBoundingClientRect().bottom),innerHeight]")
            ok(r[0] <= r[1], f'{tag} [카드 ▾] 열린 채 창 높이 600 → 마지막 카드 화면 안 {r}')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

def nav(b):
    print('== 25·28·30 J/K·C·서랍')
    for tag, w, h, t in VPS:
        ctx, pg = new(b, w, h, t)
        for nj in (3, 6):
            go(pg, '#/CONS/WHT/learn'); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(600)   # 읽던 자리 복원 대신 맨 위에서
            for i in range(nj): pg.keyboard.press('j'); pg.wait_for_timeout(350)
            pg.wait_for_timeout(900); c0 = pg.evaluate("__h.LCUR")
            pg.keyboard.press('c'); pg.wait_for_timeout(2200)
            r = pg.evaluate(f"[__h.LCUR,{GEO},document.querySelector('#lmcur').textContent]")
            ok(c0 == nj - 1 and r[0] == r[1] == c0 and f'카드 {c0 + 1}/' in r[2], f'{tag} J×{nj} → C: 지금 카드·표시 그대로 {c0} {r}')
            pg.keyboard.press('j'); pg.wait_for_timeout(900)
            ok(pg.evaluate("__h.LCUR") == c0 + 1, f'{tag} J×{nj} → C → J = 다음 카드 {pg.evaluate("__h.LCUR")}')
            pg.keyboard.press('c'); pg.wait_for_timeout(1500)   # 압축은 LS에 남으므로 되돌림
        if w > 860:   # 사이드바 카드 15 → C
            go(pg, '#/CONS/WHT/learn')
            pg.evaluate("[...document.querySelectorAll('#side .scard2')][14].click()"); pg.wait_for_timeout(1500)
            pg.keyboard.press('c'); pg.wait_for_timeout(2200)
            r = pg.evaluate(f"[__h.LCUR,{GEO}]")
            ok(r == [14, 14], f'{tag} 사이드바 카드 15 → C → 그대로 {r}')
            pg.keyboard.press('j'); pg.wait_for_timeout(900)
            ok(pg.evaluate("__h.LCUR") == 15, f'{tag} 이어서 J = 카드 16 {pg.evaluate("__h.LCUR")}')
            pg.keyboard.press('c'); pg.wait_for_timeout(1500)
        # 28 틀에서 K
        for s in (['CONS', 'WHT'] if tag != 'land' else ['PHARM', 'HM'],):
            go(pg, f'#/{s[0]}/{s[1]}/learn', 1500); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(500)
            pg.keyboard.press('k'); pg.wait_for_timeout(900)
            ok(pg.evaluate("scrollY") < 5 and pg.evaluate("__h.LCUR") == -1, f'{tag} {s[0]} 맨 위(틀)에서 K → 그대로')
            for k in 'jjkk': pg.keyboard.press(k); pg.wait_for_timeout(800)
            pg.keyboard.press('k'); pg.wait_for_timeout(1200)
            ok(pg.evaluate("__h.LCUR") == -1, f'{tag} {s[0]} J J K K K → 틀 {pg.evaluate("__h.LCUR")}')
        if w <= 860:
            go(pg, '#/CONS/WHT/learn')
            pg.keyboard.press('m'); pg.wait_for_timeout(300); pg.keyboard.press('v'); pg.wait_for_timeout(500)
            r = pg.evaluate("[document.body.classList.contains('navopen'),document.body.classList.contains('focus'),document.documentElement.classList.contains('navlock')]")
            ok(r == [False, True, False], f'{tag} 서랍이 열린 채 V → 서랍 닫고 집중 · 스크롤 잠금 풀림 {r}')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

def keys(b):
    print('== 26 / 뒤 Esc')
    for tag, w, h, t in VPS:
        ctx, pg = new(b, w, h, t); go(pg, '#/CONS/WHT/learn')
        pg.keyboard.press('Slash'); pg.wait_for_timeout(150); pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        l0 = pg.evaluate("__h.LCUR"); pg.keyboard.press('j'); pg.wait_for_timeout(800)
        r = pg.evaluate("[document.activeElement.id,document.querySelector('#gsearch').value,__h.LCUR]")
        ok(r[0] != 'gsearch' and r[1] == '' and r[2] != l0, f'{tag} / → Esc → J = 다음 카드 {r}')
        pg.keyboard.press('v'); pg.wait_for_timeout(500)
        pg.keyboard.press('Slash'); pg.keyboard.type('abc'); pg.wait_for_timeout(400); pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
        r = pg.evaluate("[document.activeElement.id,document.querySelector('#gsearch').value,document.body.classList.contains('topshow'),document.body.classList.contains('focus'),location.hash]")
        ok(r[0] != 'gsearch' and r[1] == '' and r[2] is False and r[3] and r[4].endswith('/learn'), f'{tag} 집중 / abc → Esc → 칸에서 나옴 · 상단 막대 숨음 {r}')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

def view(b):
    print('== 31·32·33 복습 보기 말·[보기 ▾]·알림')
    for tag, w, h, t in [('mac', 1280, 900, False), ('port', 820, 1180, True)]:
        ctx, pg = new(b, w, h, t); go(pg, '#/CONS/WHT/learn')
        pg.keyboard.press('r'); pg.wait_for_timeout(500)
        r = pg.evaluate("[[...document.querySelectorAll('#grppills')].map(e=>e.innerText+' '+[...e.querySelectorAll('[title]')].map(x=>x.title).join(' ')).join(''),document.querySelector('#toast').textContent,document.querySelector('#help').innerText||document.querySelector('#help').textContent]")
        ok('읽' not in r[0] and '안 본 카드만' in r[0] and '몰라요·✓ 안 한 것 먼저' in r[0], f'{tag} 복습 필터·정렬에 읽음 말 없음')
        ok('[⚡ 복습](R)' not in r[1] and '[보기 ▾]' in r[1], f'{tag} R 알림 = [보기 ▾] {r[1]!r}')
        ok('안 읽은' not in r[2] and '[⚡ 복습](R)' not in r[2] and '이해함' not in r[2], f'{tag} 도움말에 옛 말 없음')
        pg.keyboard.press('r'); pg.wait_for_timeout(400)
        st = []
        for x in ['lmcond', 'lmrev', 'lmqz', 'lmqz', 'lmrev', 'lmall']:
            pg.click('#lmview'); pg.wait_for_timeout(150); pg.click('#' + x); pg.wait_for_timeout(500)
            st.append(pg.evaluate("[document.querySelector('#stage').className.split(' ').filter(c=>['cond','review','quiz'].includes(c)).join(' '),document.querySelector('#lmview').textContent,[...document.querySelectorAll('#lvpop .pi.on')].map(e=>e.id).join(',')]"))
        ok(st[1][1] == '복습·압축' and st[1][2] == 'lmcond,lmrev', f'{tag} 압축 → 복습: 버튼 복습·압축 · 메뉴 표시 같음 {st[1]}')
        ok('quiz' in st[2][0] and st[2][1] == '복습·압축·가리기', f'{tag} 복습 중 가리기 → 가리기 그대로 켜짐 {st[2]}')
        ok('quiz' not in st[3][0] and st[3][1] == '복습·압축', f'{tag} 가리기 다시 → 꺼짐 {st[3]}')
        ok(st[4] == ['cond', '압축', 'lmcond'] and st[5][1] == '보기', f'{tag} 복습 끔 → 압축 · 전체 → 보기 {st[4]} {st[5]}')
        pg.click('#lmview'); pg.click('#lmrev'); pg.wait_for_timeout(300); pg.keyboard.press('q'); pg.wait_for_timeout(300)
        ok(pg.evaluate("document.querySelector('#stage').classList.contains('quiz')"), f'{tag} 복습 중 Q → 가린 채(꺼지지 않음)')
        pg.click('#lmview'); pg.click('#lmrev'); pg.wait_for_timeout(300)
        ok(pg.evaluate("document.querySelector('#stage').classList.contains('quiz')") and pg.evaluate("document.querySelector('#lmview').textContent") == '가리기', f'{tag} 넘겨받은 가리기는 복습을 꺼도 남음')
        pg.keyboard.press('q'); pg.wait_for_timeout(200)
        # 미니바가 넘치지 않음(겹친 이름)
        pg.click('#lmview'); pg.click('#lmcond'); pg.wait_for_timeout(300); pg.click('#lmview'); pg.click('#lmrev'); pg.wait_for_timeout(300); pg.keyboard.press('q'); pg.wait_for_timeout(300)
        for fm in (False, True):
            if fm: pg.keyboard.press('v'); pg.wait_for_timeout(500)
            r = pg.evaluate("(()=>{const m=document.querySelector('#lmini'),b=document.querySelector('#lmview').getBoundingClientRect();return [m.scrollWidth<=m.clientWidth+1,Math.round(b.right),innerWidth,Math.round(b.height)]})()")
            ok(r[0] and r[1] <= r[2] and r[3] <= 48, f'{tag} {"집중 " if fm else ""}겹친 이름 버튼이 미니바 안 {r}')
        if True: pg.keyboard.press('v'); pg.wait_for_timeout(400)
        pg.click('#lmview'); pg.click('#lmall'); pg.wait_for_timeout(300)
        # 33 되돌리기 알림 뒤 다음 알림
        pg.keyboard.press('h')
        pg.evaluate("document.querySelector('#t-WHT-3 .tbody :is(li,.li)').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
        lis = pg.evaluate("[...document.querySelectorAll('#t-WHT-3 .tbody :is(li,.li)')].slice(0,3).map(e=>{const r=e.getBoundingClientRect();return [r.left+15,r.top+8]})")
        for x, y in lis:
            pg.mouse.move(x, y); pg.mouse.down(); pg.mouse.move(x + 200, y, steps=5); pg.mouse.up(); pg.wait_for_timeout(250)
        n = pg.evaluate("document.querySelectorAll('#stage .rk-h').length")
        pg.keyboard.press('Escape'); pg.wait_for_timeout(3200)
        pg.keyboard.press('Control+z'); pg.wait_for_timeout(250)
        u = pg.evaluate("document.querySelector('#toast').textContent")
        for i in range(3): pg.keyboard.press('Control+z'); pg.wait_for_timeout(60)
        pg.keyboard.press('Shift+N'); t0 = time.time(); seen = None
        while time.time() - t0 < 2.5:
            if '다시 가렸' in pg.evaluate("document.querySelector('#toast').style.display==='block'?document.querySelector('#toast').textContent:''"): seen = time.time() - t0; break
            pg.wait_for_timeout(50)
        ok(n > 0 and '되돌림' in u and seen is not None and seen < 1.0, f'{tag} ⌘Z×4 → Shift+N 알림이 곧바로 {n} {u[:20]!r} {seen}')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

with sync_playwright() as p:
    b = p.chromium.launch()
    for f in (kit, pops, nav, keys, view):
        try: f(b)
        except Exception as e: ok(False, f'{f.__name__} 예외 {str(e)[:300]}')
    b.close()
print('RESULT', 'PASS' if not fails else 'FAIL', len(fails))
_sys.exit(1 if fails else 0)
