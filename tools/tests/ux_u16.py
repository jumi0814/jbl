"""U16 회귀: JB 진행률 분모 = 현 교수 기출(stats.main). OMS1 = 68(+참고 42 따로), PHARM = 전체 그대로(참고 없음), 기출 대장에 '0' 등급 생략.
맥 1280×900 · 아이패드 세로 820×1180. 스크린샷 work/_tmp/ux_u16_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1100):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    await pg.evaluate("localStorage.setItem('jblhub.v1.mk.OMS1', JSON.stringify({ok:{Q01:1,Q02:1},ng:{Q03:1},bm:{}}))")
    st = await pg.evaluate("(()=>{const s=[...document.querySelectorAll('.scard')];return 0})()")
    await open_(pg, '#/')
    hub = await pg.evaluate("document.querySelector('.scard[data-s=\"OMS1\"]').innerText")
    ok('기출 68문항' in hub and '참고 42' in hub and '기출 68 — 맞음 2 · 틀림 1 · 안 푼 것 65' in hub, '허브 카드 OMS1 분모 68 · 참고 42')
    ph = await pg.evaluate("document.querySelector('.scard[data-s=\"PHARM\"]').innerText")
    ok('기출 156문항' in ph and '참고' not in ph, 'PHARM 허브 카드 156 · 참고 없음')
    await pg.screenshot(path=J.TMP + f'/ux_u16_hub_{tag}.png')
    await open_(pg, '#/OMS1/_home/_home')
    t = await pg.evaluate("document.querySelector('#stage .panel .pline').innerText")
    ok('현 교수 기출 68문항' in t and '안 푼 것 65' in t and '참고 42 숨김' in t, f'과목 홈 진행률 ({t[:80]})')
    await pg.screenshot(path=J.TMP + f'/ux_u16_home_{tag}.png')
    await open_(pg, '#/OMS1/_jb/_jb')
    t = await pg.inner_text('#jbprog')
    ok('현 교수 기출 68문항' in t and '참고 42 숨김' in t, f'JB 진행 줄 68 · 참고 42 ({t[:90]})')
    await pg.evaluate("document.querySelector('#jbprog [data-reftog]').click()"); await pg.wait_for_timeout(300)
    t = await pg.inner_text('#jbprog'); n = await pg.evaluate("document.querySelectorAll('#cards .qc[data-tier=C]:not(.hid)').length")
    ok('참고 42 보이는 중' in t and n == 42 and '현 교수 기출 68문항' in t, f'[보이기] → 참고 카드 42 보임, 분모 그대로 ({t[:90]})')
    cid = await pg.evaluate("document.querySelector('#cards .qc[data-tier=C]').dataset.id")
    await pg.evaluate(f"document.querySelector('#c-{cid} [data-mk=ok]').click()"); await pg.wait_for_timeout(200)
    t = await pg.inner_text('#jbprog')
    ok('맞음 1' in t.split('참고')[1] and '맞음 2' in t.split('참고')[0], f'참고 카드 채점은 참고 칩에 따로 ({t[:120]})')
    await pg.screenshot(path=J.TMP + f'/ux_u16_jb_{tag}.png')
    await open_(pg, '#/PHARM/_jb/_jb')
    t = await pg.inner_text('#jbprog'); ok('기출 156문항' in t and '참고' not in t, f'PHARM JB 진행 줄 156 ({t[:60]})')
    for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
        await open_(pg, f'#/{s}/_led/_led', 700)
        t = await pg.evaluate("document.querySelector('#stage .panel').innerText")
        ok(not re.search(r'\s0(\.|\s|$)', t.split('.')[0] + '.'), f'{s} 기출 대장 0 등급 생략 ({t[:70]})')
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 820, 'height': 1180}, True, 'ipad')
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
