"""U13 회귀: 강의 안 위치 — 탭 줄 미니바 '카드 n/N ▾'(IntersectionObserver 30% 선)·▾ 목록(누르면 그 카드가 탭 아래)·압축·↑ 틀·J/K,
넓은 화면 사이드바 카드 목록(스크롤 스파이 굵게), 820 세로에서 미니바가 탭 줄 안·가로 넘침 0, 학습 탭에서만.
맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820. 스크린샷 work/_tmp/ux_u13_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1300):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
SCROLLTO = """(sel)=>{const e=document.querySelector(sel);const cs=getComputedStyle(document.documentElement);const off=parseFloat(cs.getPropertyValue('--toph'))+parseFloat(cs.getPropertyValue('--tabh'))+12;scrollTo(0,e.getBoundingClientRect().top+scrollY-off);}"""
TOL = 56   # ux4 B3-5 카드 안쪽 여백 32(시안) + 테두리 — 제목이 탭 줄 바로 아래(옛 기준 40은 안쪽 12일 때)
UNDERTAB = """(sel)=>{const e=document.querySelector(sel),d=document.querySelector('#dtabs').getBoundingClientRect();const r=e.getBoundingClientRect();return Math.round(r.top-d.bottom);}"""
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    await open_(pg, '#/OMS1/DD1/learn')
    N = await pg.evaluate("document.querySelectorAll('#stage .tc').length")
    await pg.evaluate(SCROLLTO, '#t-DD1-11'); await pg.wait_for_timeout(700)
    t = await pg.inner_text('#lmcur')
    ok(t.startswith(f'카드 12/{N}'), f'카드 12로 스크롤 → 미니바 ({t})')
    if vp['width'] > 860:
        on = await pg.evaluate("(document.querySelector('#side .scard2.on')||{}).dataset?.lj")
        ok(on == '11', f'사이드바 카드 목록 스크롤 스파이 굵게 (lj={on})')
    await pg.screenshot(path=J.TMP + f'/ux_u13_card12_{tag}.png')
    # ▾ → 3번
    await pg.evaluate("document.querySelector('#lmcur').click()"); await pg.wait_for_timeout(300)
    ok(await pg.evaluate("document.querySelector('#lpop').classList.contains('on') && document.querySelector('#lpop .lpi.on').dataset.lj==='11'"), '▾ 목록 열림·지금 카드 강조')
    await pg.screenshot(path=J.TMP + f'/ux_u13_pop_{tag}.png')
    await pg.evaluate("document.querySelector('#lpop .lpi[data-lj=\"2\"]').click()"); await pg.wait_for_timeout(1600)
    d = await pg.evaluate(UNDERTAB, '#t-DD1-2 .thead')
    ok(0 <= d <= TOL and await pg.inner_text('#lmn') == '3', f'3번 → 카드 3 제목이 탭 바로 아래 (거리 {d}px, 미니바 {await pg.inner_text("#lmn")})')
    # J/K
    if not touch:
        await pg.keyboard.press('j'); await pg.wait_for_timeout(1500)
        d = await pg.evaluate(UNDERTAB, '#t-DD1-3 .thead'); ok(0 <= d <= TOL and await pg.inner_text('#lmn') == '4', f'J → 카드 4 ({d}px)')
        await pg.keyboard.press('k'); await pg.keyboard.press('k'); await pg.wait_for_timeout(1500)
        d = await pg.evaluate(UNDERTAB, '#t-DD1-1 .thead'); ok(0 <= d <= TOL and await pg.inner_text('#lmn') == '2', f'K K → 카드 2 ({d}px)')
        await pg.wait_for_timeout(1500); y0 = await pg.evaluate('scrollY')
        await pg.focus('#gsearch'); await pg.keyboard.press('j'); await pg.wait_for_timeout(150)
        r = await pg.evaluate("[scrollY, document.querySelector('#gsearch').value]")
        ok(abs(r[0] - y0) <= 2 and r[1] == 'j', f'입력칸 포커스 때 J 무시(스크롤 그대로·글자 입력) {y0}→{r}')
        await pg.evaluate("document.activeElement.blur();document.querySelector('#gsearch').value=''")
    # 압축·↑ 틀
    await pg.evaluate("document.querySelector('#lmcond').click()"); await pg.wait_for_timeout(200)
    ok(await pg.evaluate("document.querySelector('#stage').classList.contains('cond') && document.querySelector('#lcond').classList.contains('on') && document.querySelector('#lmcond').classList.contains('on')"), '미니바 압축 = 압축 보기(두 버튼 함께)')
    await pg.evaluate("document.querySelector('#lmcond').click()")
    await pg.evaluate("document.querySelector('#lmcur').click()"); await pg.wait_for_timeout(300)   # ux4 B3-4 ↑ 틀 = [카드 ▾] 목록 첫 줄 '이 강의의 틀'
    ok(await pg.evaluate("document.querySelector('#lpop .lpi:first-child').id==='lmup'"), '카드 ▾ 첫 줄 = 이 강의의 틀')
    await pg.evaluate("document.querySelector('#lmup').click()"); await pg.wait_for_timeout(1500)
    d = await pg.evaluate(UNDERTAB, '#stage .frame'); ok(0 <= d <= 40 and not await pg.evaluate("document.querySelector('#lpop').classList.contains('on')"), f'이 강의의 틀 → 틀로 · 목록 닫힘 ({d}px)')
    # 820 세로: 미니바가 탭 줄 안, 가로 넘침 0
    r = await pg.evaluate("(()=>{const m=document.querySelector('#lmini').getBoundingClientRect(),d=document.querySelector('#dtabs').getBoundingClientRect();return {inrow:m.top>=d.top-1&&m.bottom<=d.bottom+1&&m.right<=d.right+1&&m.left>=d.left,sw:document.documentElement.scrollWidth,iw:innerWidth,oneline:d.height<70}})()")
    ok(r['inrow'] and r['sw'] <= r['iw'] and r['oneline'], f'미니바가 탭 줄 안 · 가로 넘침 0 {r}')
    # 다른 탭에서는 없음
    await pg.evaluate("document.querySelector('#dtabs button[data-t=\"sum\"]').click()"); await pg.wait_for_timeout(500)
    ok(not await pg.evaluate("!!document.querySelector('#lmini')"), '정리표 탭에는 미니바 없음')
    if vp['width'] > 860:
        await pg.evaluate("document.querySelector('#side .scard2[data-lj=\"5\"]').click()"); await pg.wait_for_timeout(700)   # ux2 E08 정리표 탭에서는 그 행으로(학습 탭으로 안 넘어감)
        ok((await pg.evaluate('location.hash')).startswith('#/OMS1/DD1/sum') and await pg.evaluate("document.querySelector('#m-DD1-5').classList.contains('rcur')"), '사이드바 카드 6(정리표 탭) → 정리표 그 행')
        await pg.evaluate("document.querySelector('#dtabs button[data-t=\"jb\"]').click()"); await pg.wait_for_timeout(500)
        await pg.evaluate("document.querySelector('#side .scard2[data-lj=\"5\"]').click()"); await pg.wait_for_timeout(1600)
        ok((await pg.evaluate('location.hash')).startswith('#/OMS1/DD1/learn') and 0 <= await pg.evaluate(UNDERTAB, '#t-DD1-5 .thead') <= TOL, '사이드바 카드 6(다른 탭에서) → 학습 탭 그 카드')
        await pg.screenshot(path=J.TMP + f'/ux_u13_side_{tag}.png')
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 820, 'height': 1180}, True, 'ipad')
        await run(b, {'width': 1180, 'height': 820}, True, 'ipadl')
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
