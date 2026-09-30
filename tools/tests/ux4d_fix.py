"""ux4d 회귀 — 4차 개편 마무리(앞 회차에서 남은 것).
허브: 왼쪽 메뉴 바닥에 '도움말' 중복 없음(도움말은 상단 ? 하나)
JB: 미니 막대(스크롤 내림) 820·1180에서 '지금 n/N'이 [답 펼치기]를 덮지 않고 가로 넘침 없음(1240 이하 정렬 칸 숨김)
    · 📖 칩 → ↩ 돌아가기 뒤 펼친 답·지금 문항 그대로
도구: 🧹 표시 지우기 창이 화면 오른쪽에 붙지 않음(8px 여백)
정리표: 한 번도 안 누른 전체정리표는 1180 → 820으로 돌리면 접힘
맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
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
R = "e=>{if(!e||!e.offsetParent)return null;const r=e.getBoundingClientRect();return [Math.round(r.left),Math.round(r.right)]}"
with sync_playwright() as p:
    b = p.chromium.launch()
    # 허브 메뉴 바닥
    ctx, pg = new(b, 1280, 900); go(pg, '#/')
    ft = pg.evaluate("[...document.querySelectorAll('#side .nvfoot button')].filter(x=>x.offsetParent).map(x=>x.textContent.trim())")
    ok('도움말' not in ft and any('백업' in x for x in ft), f'허브 메뉴 바닥에 도움말 중복 없음 {ft}')
    ok(pg.evaluate("!!document.querySelector('#helpb')&&document.querySelector('#helpb').offsetParent!==null"), '상단 ? 도움말은 그대로')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    for w, h in [(820, 1180), (1180, 820), (1280, 900)]:
        ctx, pg = new(b, w, h, touch=w < 1280); go(pg, '#/OMS1/_jb/_jb')
        pg.evaluate("scrollTo(0,2500)"); pg.wait_for_timeout(700)
        m = pg.evaluate("(R=>{const bar=document.querySelector('#jbbar'),b1=bar.querySelector('.b1');return {mini:bar.classList.contains('mini'),sw:b1.scrollWidth-b1.clientWidth,rev:R(document.querySelector('#frev')),now:R(document.querySelector('#fnow'))}})(" + R + ")")
        ov = m['rev'] and m['now'] and m['now'][0] < m['rev'][1]
        ok(m['mini'] and m['sw'] <= 1 and not ov, f'{w} 미니 막대 넘침·겹침 없음 {m}')
        ok(not pg.errs, f'{w} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # ↩ 돌아가기 뒤 펼친 답 유지
    for w, h, t in [(1280, 900, False), (820, 1180, True)]:
        ctx, pg = new(b, w, h, touch=t); go(pg, '#/CONS/_jb/_jb')
        pg.evaluate("document.querySelector('#cards .qc[data-id=Q10]').scrollIntoView({block:'start'})"); pg.wait_for_timeout(600)
        pg.evaluate("(()=>{const c=document.querySelector('#cards .qc[data-id=Q10]');c.classList.add('open')})()"); pg.wait_for_timeout(300)
        pg.evaluate("document.querySelector('#cards .qc[data-id=Q10] .chip.lec').click()"); pg.wait_for_timeout(1500)
        pill = pg.evaluate("(document.querySelector('#retpill')||{}).textContent")
        pg.evaluate("document.querySelector('#retpill').click()"); pg.wait_for_timeout(1500)
        r = pg.evaluate("(()=>{const c=document.querySelector('#cards .qc[data-id=Q10]');return {h:location.hash,open:!!c&&c.classList.contains('open'),top:c&&Math.round(c.getBoundingClientRect().top)}})()")
        ok('돌아가기' in (pill or '') and r['h'].startswith('#/CONS/_jb') and r['open'], f'{w} 📖 → ↩ 돌아가기 뒤 Q10 답 펼친 채 {pill} {r}')
        ok(not pg.errs, f'{w} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # 🧹 창 오른쪽 여백
    for w, h in [(820, 1180), (700, 1000)]:
        ctx, pg = new(b, w, h, touch=True); go(pg, '#/CONS/WHT/learn')
        pg.evaluate("document.querySelector('#k-clear').click()"); pg.wait_for_timeout(500)
        c = pg.evaluate("(()=>{const p=document.querySelector('#clearpop');if(!p.classList.contains('on'))return null;const r=p.getBoundingClientRect();return [Math.round(r.left),Math.round(r.right),innerWidth]})()")
        ok(c and c[0] >= 8 and c[1] <= c[2] - 8, f'{w} 🧹 창 좌우 8px 여백 {c}')
        ctx.close()
    # 전체정리표 돌리기
    ctx, pg = new(b, 1180, 820, touch=True); go(pg, '#/CONS/WHT/sum')
    a = pg.evaluate("(document.querySelector('#sumtop')||{}).className")
    pg.set_viewport_size({'width': 820, 'height': 1180}); pg.wait_for_timeout(700)
    c = pg.evaluate("(document.querySelector('#sumtop')||{}).className")
    ok(a is not None and 'stclosed' not in a and 'stclosed' in (c or ''), f'안 누른 전체정리표 1180→820 접힘 {a} → {c}')
    pg.evaluate("document.querySelector('#sumtop [data-sttab=\"0\"]').click()"); pg.wait_for_timeout(300)
    pg.set_viewport_size({'width': 1180, 'height': 820}); pg.wait_for_timeout(300); pg.set_viewport_size({'width': 820, 'height': 1180}); pg.wait_for_timeout(500)
    d = pg.evaluate("document.querySelector('#sumtop').className")
    ok('stclosed' not in d, f'한 번 펼친 전체정리표는 돌려도 그대로 {d}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
