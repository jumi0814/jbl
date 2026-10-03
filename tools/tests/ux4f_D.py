"""ux4f D 회귀 — 오류 재검 2회차 범위 D(n 61~90: 허브·시계·검색·과목 홈·과목 메뉴·강의 학습 보기/키) 중 이번에 고친 것.
(61~85는 ux4c 2회차에서 고쳐 tools/tests/ux4c_fix2.py가 확인 — 여기서는 86~90)
86 정리표 탭 Q = 이 화면의 빨간 핵심어 가리기 · 학습 탭에서 켠 '이 카드' 가리기가 정리표에 0칸으로 남지 않음 · 그 뒤 Esc에 '가리기 보기를 껐어요' 없음
87 🧹 지우기 창이 열린 채 E·Q·C·R·J → 창이 먼저 닫힘
88 [보기 ▾] 창을 Esc·바깥·항목으로 닫으면 #lmview aria-expanded='false'
89 그림 확대 창이 열린 채 뒤로 = 창만 닫고 강의에 남음(자리 그대로) · [닫기]로 닫은 뒤 뒤로 = 앞 화면(과목 홈)
90 도움말: 'D 지금 카드 ✓ 다 봄' · 카드 머리 '⭐ n ↓' 문구 없음
맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)"""
import re, os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def new(b, w, h, touch=False):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch); pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    pg.on('dialog', lambda d: d.accept())
    pg.goto('about:blank'); pg.goto(U + '#/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1');localStorage.setItem('jblhub.v1.tauto','false')")
    return ctx, pg
def go(pg, h, wait=600):
    pg.goto('about:blank'); pg.goto(U + h)
    pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')", timeout=60000); pg.wait_for_timeout(wait)
def key(pg, k, code=None, shift=False):
    pg.evaluate("([k,c,s])=>document.dispatchEvent(new KeyboardEvent('keydown',{key:k,code:c,shiftKey:s,bubbles:true}))", [k, code or '', shift]); pg.wait_for_timeout(300)
TOASTS = "(JSON.parse(sessionStorage.getItem('jblhub.v1.toasts')||'[]')).map(x=>x&&(x.t||x[1]||'')).join(' | ')"
QS = "[__h.QZ.on,__h.QZ.scope,document.querySelectorAll('#stage .k.qzk').length,document.querySelectorAll('#stage .k.qzk:not(.show)').length]"
VP = [('mac', 1280, 900, False), ('port', 820, 1180, True), ('land', 1180, 820, True)]

def quiz_sum(b):
    print('== 86 정리표 탭 Q')
    for tag, w, h, t in VP:
        ctx, pg = new(b, w, h, t)
        go(pg, '#/CONS/WHT/learn', 800)
        pg.evaluate("__h.goCard(3)"); pg.wait_for_timeout(500)
        key(pg, 'ㅂ', 'KeyQ'); a = pg.evaluate(QS)
        n_sum = pg.evaluate("[...document.querySelectorAll('#dtabs button[data-t]')].findIndex(x=>x.dataset.t==='sum')+1")
        key(pg, str(n_sum), 'Digit' + str(n_sum)); pg.wait_for_timeout(500)
        s0 = pg.evaluate("[location.hash]+''"); c = pg.evaluate(QS)
        ok(a[0] and a[1] == 'card' and a[2] > 0 and s0.endswith('/sum') and not c[0] and c[2] == 0, f'{tag} 학습 탭 이 카드 가리기 {a} → 정리표로 오면 가리기 꺼짐 {c}')
        key(pg, 'Escape', 'Escape')
        ok('가리기 보기를 껐어요' not in pg.evaluate(TOASTS), f'{tag} 정리표에서 Esc → 보이지 않던 가리기를 껐다는 알림 없음')
        key(pg, 'ㅂ', 'KeyQ'); d = pg.evaluate(QS); tx = pg.evaluate(TOASTS)
        ok(d[0] and d[2] > 0 and d[3] == d[2] and re.search('가리기 보기 — (이 행|이 표|이 화면)', tx) and '없어요' not in tx, f'{tag} 정리표 Q → 이 행(못 찾으면 이 표·이 화면) 빨간 핵심어 {d[2]}개 가림 {d}')   # E 합침: 정리표의 '이 카드' = 화면 위쪽 행(qzUnit)
        ok(pg.evaluate("localStorage.getItem('jblhub.v1.qzscope')") in (None, '"card"'), f'{tag} 저장된 범위는 그대로')
        key(pg, 'ㅂ', 'KeyQ'); e = pg.evaluate(QS)
        ok(not e[0] and e[2] == 0, f'{tag} 정리표 Q 다시 → 끔 {e}')
        if tag == 'mac':
            go(pg, '#/CONS/WHT/sum', 800); key(pg, 'ㅂ', 'KeyQ'); f = pg.evaluate(QS)
            ok(f[0] and f[2] > 0, f'{tag} 정리표를 바로 열고 Q → 가림 {f}')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

def clear_keys(b):
    print('== 87 🧹 창 + 보기 키 · 88 [보기 ▾] aria-expanded')
    for tag, w, h, t in VP:
        ctx, pg = new(b, w, h, t)
        go(pg, '#/CONS/WHT/learn', 800)
        for k, code in [('ㄷ', 'KeyE'), ('ㅂ', 'KeyQ'), ('ㅊ', 'KeyC'), ('ㄱ', 'KeyR'), ('ㅓ', 'KeyJ')]:
            pg.evaluate("document.querySelector('#k-clear').click()"); pg.wait_for_timeout(200)
            o = pg.evaluate("document.querySelector('#clearpop').classList.contains('on')")
            key(pg, k, code)
            c = pg.evaluate("[document.querySelector('#clearpop').classList.contains('on'),document.querySelectorAll('#stage .clrtgt').length]")
            ok(o and c == [False, 0], f'{tag} 🧹 창 열린 채 {code[-1]} → 창 닫힘 {o} → {c}')
            key(pg, k, code)   # 보기 되돌림
        AE = "document.querySelector('#lmview').getAttribute('aria-expanded')"
        for how in ['esc', 'out', 'item']:
            pg.evaluate("window.scrollTo(0,400)"); pg.wait_for_timeout(300)
            pg.evaluate("document.querySelector('#lmview').click()"); pg.wait_for_timeout(200)
            o = [pg.evaluate("document.querySelector('#lvpop').classList.contains('on')"), pg.evaluate(AE)]
            if how == 'esc': key(pg, 'Escape', 'Escape')
            elif how == 'out': pg.mouse.click(w // 2, h - 160); pg.wait_for_timeout(250)
            else: pg.evaluate("document.querySelector('#lmcond').click()"); pg.wait_for_timeout(300)
            c = [pg.evaluate("document.querySelector('#lvpop').classList.contains('on')"), pg.evaluate(AE)]
            ok(o == [True, 'true'] and c == [False, 'false'], f'{tag} [보기 ▾] {how}로 닫음 → aria-expanded false {o} → {c}')
            if how == 'item': pg.evaluate("document.querySelector('#lmview').click()"); pg.wait_for_timeout(150); pg.evaluate("document.querySelector('#lmall').click()"); pg.wait_for_timeout(300)
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

def modal_back(b):
    print('== 89 그림 확대 + 뒤로')
    for tag, w, h, t in VP:
        ctx, pg = new(b, w, h, t)
        go(pg, '#/CONS/_home/_home', 600)
        pg.evaluate("__h.openDoc('CONS','WHT','learn')"); pg.wait_for_timeout(900)
        OPEN = "(()=>{const f=document.querySelector('#stage figure[data-fig],#stage img.fig');f.scrollIntoView({block:'center'});f.click();})()"
        pg.evaluate(OPEN); pg.wait_for_timeout(800)
        y0 = pg.evaluate("[document.querySelector('#imgmodal').classList.contains('on'),Math.round(scrollY)]")
        pg.go_back(); pg.wait_for_timeout(800)
        r = pg.evaluate("[document.querySelector('#imgmodal').classList.contains('on'),document.body.classList.contains('modal-on'),location.hash,Math.round(scrollY)]")
        ok(y0[0] and not r[0] and not r[1] and r[2].startswith('#/CONS/WHT/learn') and abs(r[3] - y0[1]) < 40, f'{tag} 확대 창 → 뒤로 = 창만 닫힘·강의 그 자리 {y0} → {r}')
        pg.evaluate(OPEN); pg.wait_for_timeout(800)
        pg.evaluate("document.querySelector('#mnext').click()"); pg.wait_for_timeout(500)
        key(pg, 'Escape', 'Escape'); pg.wait_for_timeout(500)
        r2 = pg.evaluate("[document.querySelector('#imgmodal').classList.contains('on'),location.hash]")
        ok(not r2[0] and r2[1].startswith('#/CONS/WHT/learn'), f'{tag} 다음 그림 뒤 Esc → 닫힘·강의 그대로 {r2}')
        pg.go_back(); pg.wait_for_timeout(1000)
        r3 = pg.evaluate("location.hash")
        ok(r3.startswith('#/CONS/_home'), f'{tag} 닫은 뒤 뒤로 한 번 = 과목 홈(빈 항목 없음) {r3}')
        pg.go_forward(); pg.wait_for_timeout(1000)
        r4 = pg.evaluate("[location.hash,document.querySelector('#imgmodal').classList.contains('on')]")
        ok(r4[0].startswith('#/CONS/WHT/learn') and not r4[1], f'{tag} 앞으로 → 강의 {r4}')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

def help_text(b):
    print('== 90 도움말 문구')
    ctx, pg = new(b, 1280, 900)
    go(pg, '#/CONS/WHT/learn', 600)
    tx = pg.evaluate("document.querySelector('#help').textContent")
    ok('지금 카드 ★ 북마크' in tx and '✓ 이해함 ·' not in tx.split('학습 탭')[-1][:200], "도움말 'D 지금 카드 ★ 북마크'(사용자 10-03 다 봄 → 북마크)")
    ok('⭐ n ↓' not in tx, "도움말에 숨긴 '⭐ n ↓' 문구 없음")
    ok(pg.evaluate("[...document.querySelectorAll('#stage [data-cbm]')].some(x=>x.offsetParent&&x.textContent.includes('북마크'))"), "카드 끝 버튼 이름 '☆ 북마크'")
    ok(not pg.errs, f'오류 0 {pg.errs[:3]}')
    ctx.close()

if __name__ == '__main__':
    only = _sys.argv[1:]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for f in [quiz_sum, clear_keys, modal_back, help_text]:
            if not only or f.__name__ in only: f(b)
        b.close()
    print(f'\nRESULT {"PASS" if not fails else "FAIL"} {len(fails)}')
    for m in fails: print('  ' + m)
    _sys.exit(1 if fails else 0)
