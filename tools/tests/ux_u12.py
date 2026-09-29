"""U12 회귀: 도구 막대·터치 대상 크기 — 820×1180 터치에서 kit 한 줄·높이 ≤56, 견본 ≥28, .dn ≥40, 강의 칩 ≥32,
허브 홈·검색 화면에서 #kit 숨김, 1280에서는 견본 5개 나란히. 스크린샷 work/_tmp/ux_u12_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
SZ = '''(sel)=>{const e=[...document.querySelectorAll(sel)].find(x=>x.offsetParent||getComputedStyle(x).position==='fixed');if(!e)return null;const b=e.getBoundingClientRect();return [Math.round(b.width),Math.round(b.height)];}'''
async def open_(pg, h):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(1100)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        ctx = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True); pg = await ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await open_(pg, '#/OMS1/DD1/learn')
        k = await pg.evaluate(SZ, '#kit'); ok(k and k[1] <= 56, f'iPad 세로 kit 높이 ≤56 ({k})')
        ok(await pg.evaluate("document.querySelectorAll('#k-swl .sw').length===5 && getComputedStyle(document.querySelector('#k-swl')).display==='none'"), '860 이하: 견본 5개는 ▾ 팝오버 안')
        dn = await pg.evaluate(SZ, '#stage .dnend'); ok(dn and dn[1] >= 40, f'카드 끝 ✓ 다 봄 높이 ≥40 (ux4 B1-6 — 머리 ✓ 원 대신) ({dn})')
        kb = await pg.evaluate(SZ, '#kit button'); ok(kb and min(kb) >= 40, f'kit 버튼 ≥40 ({kb})')
        await pg.tap('#k-swc'); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("getComputedStyle(document.querySelector('#k-swl')).display!=='none'"), '▾ 누르면 견본 팝오버 열림')
        sw = await pg.evaluate(SZ, '#k-swl .sw'); ok(sw and min(sw) >= 28, f'견본 ≥28 ({sw})')
        await pg.screenshot(path=J.TMP + '/ux_u12_ipp_swpop.png')
        await pg.tap('#k-swl .sw[data-c="g"]'); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("getComputedStyle(document.querySelector('#k-swl')).display==='none' && document.querySelector('#k-h').classList.contains('on')"), '색 고르면 닫히고 형광펜 켜짐')
        await pg.keyboard.press('Escape')
        pb = await pg.evaluate("parseFloat(getComputedStyle(document.querySelector('#stage')).paddingBottom)")
        kh = await pg.evaluate("document.querySelector('#kit').offsetHeight")
        ok(pb >= kh + 24, f'#stage padding-bottom({pb}) ≥ kit 높이+24')
        await open_(pg, '#/OMS1/_jb/_jb')
        cl = await pg.evaluate(SZ, '#stage button.chip.lec'); ok(cl and cl[1] >= 32, f'강의 칩 높이 ≥32 ({cl})')
        await pg.screenshot(path=J.TMP + '/ux_u12_ipp_jb.png')
        await open_(pg, '')
        ok(await pg.evaluate("getComputedStyle(document.querySelector('#kit')).display==='none'"), '허브 홈에서 #kit 숨김')
        await pg.fill('#gsearch', '임플란트'); await pg.wait_for_timeout(600)
        ok(await pg.evaluate("getComputedStyle(document.querySelector('#kit')).display==='none'"), '검색 화면에서 #kit 숨김')
        await ctx.close()
        ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await open_(pg, '#/OMS1/DD1/learn')
        ok(await pg.evaluate("[...document.querySelectorAll('#k-swl .sw')].filter(x=>x.offsetParent).length===0 && !!document.querySelector('#k-swc').offsetParent"), '1280: 견본 5개도 ▾ 팝오버 안(ux4 B1-4 막대에 늘어놓지 않음)')
        k = await pg.evaluate(SZ, '#kit'); ok(k and k[1] <= 50, f'1280 kit 한 줄 ({k})')
        kx = await pg.evaluate("(()=>{const r=document.querySelector('#kit').getBoundingClientRect(),sw=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--sidew'))||0,W=document.documentElement.clientWidth;return Math.abs((r.left+r.right)/2-(sw+(W-sw)/2));})()"); ok(kx < 2, f'1280 kit 가운데(메뉴를 뺀 본문 폭 — ux4 B32) {kx}')
        await pg.screenshot(path=J.TMP + '/ux_u12_mac.png')
        ok(not errs, f'pageerror 0 ({errs[:2]})')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
