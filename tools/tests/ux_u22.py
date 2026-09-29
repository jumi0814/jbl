"""U22 회귀: 허브 홈 과목 카드 행동 버튼(이어서 = lastBy 위치 · 안 푼 기출 = _jb 안 푼 것)·두 줄 진행, 사이드바 과목 전환 select,
document.title(강의명 · 과목 — JBL / JBL 허브), READY(없는 팩 불러오지 않음 — 콘솔 오류 0), 압축 hero(1180×820 학습 본문 시작 y ≤ 170)."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1000):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append('console ' + m.text[:120]) if m.type == 'error' else None)
        await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await open_(pg, '#/')
        ok(await pg.title() == 'JBL 허브', f'허브 제목 ({await pg.title()})')
        ok(await pg.evaluate("document.querySelectorAll('.hsj.off').length") == 1 and '자료 준비 중' in await pg.inner_text('.hsj.off[data-off=ESTH]'), 'ESTH 자료 대기 행')
        ok(await pg.evaluate("document.querySelectorAll('.hsj[data-s] .pbar').length") == 6, '과목 표 진행 막대 하나(기출 — ux4 B1-6 읽음 막대 없음) × 6')
        await open_(pg, '#/OMS1/DD2/learn', 1300)
        ok('DD' in await pg.title() or 'Dentofacial' in await pg.title(), f'강의 제목 ({await pg.title()})')
        await pg.evaluate("window.scrollTo(0,3000)"); await pg.wait_for_timeout(1200)
        await open_(pg, '#/')
        t = await pg.get_attribute('.hsj[data-s="OMS1"] .go-resume', 'title')
        ok('이어서' in t, f'허브 과목 표 ↪ 이어서 버튼 ({t})')
        await pg.click('.hsj[data-s="OMS1"] .go-resume'); await pg.wait_for_timeout(1300)
        ok(await pg.evaluate("location.hash.startsWith('#/OMS1/DD2/learn') && scrollY>1500"), f'이어서 → DD2 학습 읽던 곳 (y={await pg.evaluate("scrollY")})')
        await open_(pg, '#/'); await pg.click('#home .htodo [data-todo=jb]'); await pg.wait_for_timeout(900)   # ux3 H3 ✅ 오늘 할 일 ③(최근 과목 OMS1)
        ok(await pg.evaluate("location.hash.startsWith('#/OMS1/_jb') && document.querySelector('#jbbar [data-qf=\"todo\"]').classList.contains('on')"), '안 푼 기출 → _jb 안 푼 것')
        await pg.click('#side [data-nvsw]'); await pg.wait_for_timeout(200); await pg.click('#side [data-nvsj="GERI"]'); await pg.wait_for_timeout(900)
        ok(await pg.evaluate("location.hash.startsWith('#/GERI/_home')"), '과목 메뉴 [과목 바꾸기 ▾] → GERI 홈 (ux4 묶음2)')
        ok(not errs, f'콘솔·페이지 오류 0 {errs[:3]}')
        ctx2 = await b.new_context(viewport={'width': 1180, 'height': 820}); pg2 = await ctx2.new_page()
        for h in ['#/OMS1/DD1/learn', '#/PHARM/HM/learn', '#/GERI/_jb/_jb']:
            await open_(pg2, h)
            y = await pg2.evaluate("Math.round(document.querySelector('#stage').firstElementChild.getBoundingClientRect().top)")
            ok(y <= 170 or '_jb' in h and y <= 175, f'1180×820 {h} 본문 시작 y={y}')
        await pg2.screenshot(path=J.TMP + '/ux_u22_jb_1180.png')
        ctx3 = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True); pg3 = await ctx3.new_page()
        await open_(pg3, '#/OMS1/DD1/learn'); await pg3.click('#navbtn'); await pg3.wait_for_timeout(400)
        ok(await pg3.evaluate("document.querySelectorAll('#side [data-nvsj]').length===7 && document.querySelectorAll('#side .nvl').length===__h.PACKS.OMS1.lect.length && document.querySelector('#side .nvsw').getBoundingClientRect().width>60"), '820 서랍 = 과목 메뉴(강의 줄 · 과목 바꾸기 7과목)')
        await pg3.screenshot(path=J.TMP + '/ux_u22_drawer_820.png')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
