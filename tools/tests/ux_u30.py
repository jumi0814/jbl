"""U30 회귀: 전체 검색 — 'fontanel' 스니펫에 버튼 글자(맞음·틀림·★) 없음·블록 사이 ' · '(낱말 붙음 없음), 결과 제목에 카드 번호/JB 번호,
지금 과목 먼저·과목별 20건 + 더 보기, 검색창을 비우거나 Esc·✕ 닫기 → 원래 강의·스크롤 위치, 결과 클릭 → 그 카드(revealCard)."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1100):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for vp, touch, tag in [({'width': 1280, 'height': 900}, False, '1280'), ({'width': 820, 'height': 1180}, True, '820')]:
            ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
            await open_(pg, '#/OMS1/DD1/learn'); await pg.evaluate("window.scrollTo(0,4000)"); await pg.wait_for_timeout(900)
            y0 = await pg.evaluate("scrollY")
            await pg.fill('#gsearch', 'fontanel'); await pg.wait_for_timeout(900)
            r = await pg.evaluate("""()=>{const rs=[...document.querySelectorAll('#home .sres')];return {n:rs.length,titles:rs.slice(0,6).map(x=>x.querySelector('.stl').innerText),sn:rs.map(x=>x.querySelector('.ssn').innerText).join(' || '),first:(document.querySelector('#home .sgt')||{}).innerText,more:document.querySelectorAll('#home [data-smore]').length}}""")
            ok(r['n'] > 0 and not any(w in r['sn'] for w in ['맞음틀림', '틀림★', '답·해설']), f'스니펫에 버튼 글자 없음 ({r["n"]}건)')
            ok(all(('카드 ' in t) or ('JB ' in t) or ('비교표' in t) or ('예상' in t) or ('틀' in t) for t in r['titles']), f'제목에 카드/JB 번호 {r["titles"][:3]}')
            ok('구강악안면외과학' in (r['first'] or ''), f'지금 과목 먼저 ({r["first"]})')
            await pg.screenshot(path=J.TMP + f'/ux_u30_search_{tag}.png')
            await pg.fill('#gsearch', ''); await pg.wait_for_timeout(1300)
            r2 = await pg.evaluate("[location.hash, Math.round(scrollY)]")
            ok(r2[0].startswith('#/OMS1/DD1/learn') and abs(r2[1] - y0) < 60, f'검색창 비움 → 원래 강의·위치 {r2} (전 y={y0})')
            await pg.fill('#gsearch', 'fontanel'); await pg.wait_for_timeout(900); await pg.press('#gsearch', 'Escape'); await pg.wait_for_timeout(1300)
            r3 = await pg.evaluate("[location.hash, Math.round(scrollY)]")
            ok(r3[0].startswith('#/OMS1/DD1/learn') and abs(r3[1] - y0) < 60, f'Esc → 원래 위치 {r3}')
            await pg.fill('#gsearch', 'fontanel'); await pg.wait_for_timeout(900); await pg.click('#sclose'); await pg.wait_for_timeout(1300)
            ok(await pg.evaluate("location.hash.startsWith('#/OMS1/DD1/learn')"), '✕ 닫기 → 원래 강의')
            await pg.fill('#gsearch', 'fontanel'); await pg.wait_for_timeout(900)
            aid = await pg.evaluate("(()=>{const r=[...document.querySelectorAll('#home .sres')].find(x=>x.dataset.d==='_jb');r.click();return r.dataset.aid})()"); await pg.wait_for_timeout(1300)
            ok(await pg.evaluate(f"(()=>{{const c=[...document.querySelectorAll('#stage [data-aid]')].find(x=>x.dataset.aid==='{aid}');return !!c&&c.getBoundingClientRect().top<innerHeight}})()"), '결과 클릭 → 그 JB 카드가 화면에')
            await pg.fill('#gsearch', '치아'); await pg.wait_for_timeout(1200)
            n = await pg.evaluate("[document.querySelectorAll('#home .sres').length, document.querySelectorAll('#home [data-smore]').length]")
            ok(n[0] > 40 and n[1] > 0, f'많으면 과목별 20건 + 더 보기 {n}')
            ok(not errs, f'pageerror 0 {errs[:2]}')
            await ctx.close()
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
