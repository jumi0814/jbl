"""ux4f I 회귀 — 사용자 10-02 요청 두 가지
I1 '과목 없이 공부한 내역은 시간 수정이 안되는 오류' — 과목 칸이 빈('') 옛 기록·기타 기록도 달력에서 '기타'로 보이고 ✎ 고치기·± 고치기가 됨(엉뚱한 과목으로 옮겨지지 않음)
I2 '각 과목별 페이지에서 각 강의본을 북마크' — 과목 홈 강의 카드 ☆/★ · '★ 북마크' 줄 · 강의 바로가기·과목 메뉴 ★ · 강의 머리 [☆ 북마크] · 새로고침 유지(LS lbm.<S>) · 백업 합치기 = 합집합"""
import os as _os, sys as _sys, json, datetime; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
td = datetime.date.today().isoformat()
def go(pg, h, w=800):
    pg.goto('about:blank'); pg.goto(U + h); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(w)
with sync_playwright() as p:
    b = p.chromium.launch()
    for W, H, T in [(1280, 900, False), (820, 1180, True)]:
        ctx = b.new_context(viewport={'width': W, 'height': H}, has_touch=T); pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept())
        # ---------- I1 ----------
        pg.goto(U + '#/')
        pg.evaluate(f"""(()=>{{localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1');
          localStorage.setItem('jblhub.v1.time',JSON.stringify({{'{td}':{{'':1800000,'기타':600000}}}}));
          localStorage.setItem('jblhub.v1.tseg',JSON.stringify({{'{td}':[[32400,34200,'','','a']]}}));}})()""")
        go(pg, '#/_cal/' + td)
        rows = pg.evaluate("[...document.querySelectorAll('.crows .crow')].map(r=>r.textContent.trim())")
        ok(rows and '기타' in rows[0] and pg.evaluate(f"__h.tDay('{td}')") == {'기타': 2400000}, f'I1 {W} 과목 칸 빈 기록 = 기타 줄 {rows} {pg.evaluate(f"__h.tDay(\'{td}\')")}')
        pg.evaluate("document.querySelector('[data-cre=\"0\"]').click()"); pg.wait_for_timeout(300)
        sv = pg.evaluate("document.querySelector('#ceS').value")
        pg.fill('#ceB', '09:15'); pg.evaluate("document.querySelector('[data-cesave=\"0\"]').click()"); pg.wait_for_timeout(500)
        dd = pg.evaluate(f"__h.tDay('{td}')")
        ok(sv == '기타' and dd == {'기타': 1500000}, f'I1 {W} ✎ 끝 09:15 → 기타 0:25(다른 과목으로 안 옮김) form={sv} {dd}')
        nb = pg.query_selector('[data-cnts]')
        ok(nb is not None, f'I1 {W} 시간대 없음 줄 ± 있음')
        if nb:
            nb.click(); pg.wait_for_timeout(300); pg.fill('#cntsm', '5'); pg.evaluate("document.querySelector('[data-cntsgo=\"-1\"]').click()"); pg.wait_for_timeout(500)
            d2 = pg.evaluate(f"__h.tDay('{td}')"); tt = pg.evaluate("document.querySelector('#toast').textContent")
            ok(d2 == {'기타': 1200000} and '기타' in tt, f'I1 {W} ± −5분 → 기타 0:20 {d2} {tt!r}')
        # ---------- I2 ----------
        go(pg, '#/CONS/_home/_home')
        pg.evaluate("document.querySelector('#hlec').scrollIntoView()")
        n0 = pg.evaluate("document.querySelectorAll('#hlec .lcw .lbm').length")
        pg.evaluate("document.querySelectorAll('#hlec .lbm')[1].click()"); pg.wait_for_timeout(300)
        h0 = pg.evaluate("location.hash")
        r = pg.evaluate("[document.querySelectorAll('#hlec .lcw.bm').length,(document.querySelector('#hlec .lbmrow')||{}).textContent||'',[...document.querySelectorAll('#nav .nvl.bm')].length,JSON.parse(localStorage.getItem('jblhub.v1.lbm.CONS')||'{}'),document.querySelectorAll('#stage .chip.ljc.bm i.bmk').length]")
        ok(n0 == 7 and h0.startswith('#/CONS/_home') and r[0] == 1 and 'Diagnosis and treatment of the cracked tooth' in r[1] and r[2] == 1 and list(r[3]) == ['CRK'] and r[4] >= 1, f'I2 {W} ☆ 누르면 북마크(카드·★ 줄·메뉴·바로가기) — 강의로 가지 않음 {n0} {h0} {r[:3]} {r[3]} {r[4]}')
        bh = pg.evaluate("Math.round(document.querySelector('#hlec .lbm').getBoundingClientRect().height)")
        ok(bh >= (44 if T else 40), f'I2 {W} ☆ 누름 자리 {bh}px')
        go(pg, '#/CONS/CRK/learn')
        hb = pg.evaluate("(b=>b&&[b.textContent,b.getAttribute('aria-pressed')])(document.querySelector('#hero .hbm'))")
        ok(hb and hb[0].startswith('★') and hb[1] == 'true', f'I2 {W} 새로고침·강의 머리 ★ 북마크 {hb}')
        pg.evaluate("document.querySelector('#hero .hbm').click()"); pg.wait_for_timeout(300)
        ok(pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.lbm.CONS')||'{}')") == {} and not pg.evaluate("document.querySelector('#nav .nvl.bm')"), f'I2 {W} 강의 머리에서 빼기 → 메뉴 ★도 사라짐')
        # 백업 합치기 = 합집합
        pg.evaluate("localStorage.setItem('jblhub.v1.lbm.CONS',JSON.stringify({INL:1}))")
        n = pg.evaluate("__h.mergeData?__h.mergeData({'jblhub.v1.lbm.CONS':JSON.stringify({ADH:2})}).n:-1")
        if n != -1:
            ok(set(pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.lbm.CONS'))")) == {'INL', 'ADH'}, f'I2 {W} 백업 합치기 = 합집합 {n}')
        ok(not errs, f'{W} 콘솔 오류 없음 {errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
