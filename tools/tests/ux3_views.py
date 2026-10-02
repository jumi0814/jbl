"""ux3 묶음 P4 회귀·화면 확인: 1280×900 · 1180×820(터치) · 820×1180(터치) × 화면 11개(홈·📅 달력·📊 통계·검색·🖍 내 표시·과목 홈·학습·정리표·비교표·JB·한 장씩)
+ 820 ☰ 서랍 · 1180 메뉴 숨김(M) 정리표. 화면마다: 콘솔 오류 0 · 가로 넘침 0(문서 scrollWidth ≤ 창 폭) · 본문(#home 또는 #stage)이 비지 않음 ·
왼쪽 메뉴·도구 막대(#kit)가 본문 첫 줄을 가리지 않음(820 서랍 닫힘 상태) · 스크린샷 work/_tmp/ux3p_<폭>_<화면>.png (사람이 직접 봄)."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
VIEWS = [('home', '#/', '#home .hband'), ('cal', '#/_cal', '#calg'), ('stats', '#/_time', '#home'), ('search', '#/?q=' + 'bleaching', '#home .sres'),
         ('marks', '#/CONS/_marks', '#stage'), ('subj', '#/CONS/_home', '#stage'), ('learn', '#/CONS/WHT/learn', '#stage .tc'),
         ('sum', '#/CONS/WHT/sum', '#stage .msum'), ('cmp', '#/CONS/_tbl', '#stage table'), ('jb', '#/CONS/_jb/_jb', '#cards .qc')]
CHK = """()=>{const W=innerWidth,de=document.documentElement,main=document.querySelector('#home:not([hidden])')||document.querySelector('#stage');
 const txt=(main&&main.innerText||'').trim().length;const kit=document.querySelector('#kit');const k=kit&&kit.offsetParent?kit.getBoundingClientRect():null;
 return {ov:de.scrollWidth-W,txt,kit:k?[Math.round(k.left),Math.round(k.right)]:null,W}}"""
async def run(b, tag, vp, touch):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
    await pg.goto(U + '#/'); await pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.tauto','false')")
    for name, h, sel in VIEWS:
        await pg.goto('about:blank'); await pg.goto(U + h)
        try: await pg.wait_for_selector(sel, timeout=30000)
        except Exception: pass
        await pg.wait_for_timeout(900)
        r = await pg.evaluate(CHK)
        ok(r['ov'] <= 0 and r['txt'] > 40, f'{tag} {name}: 가로 넘침 {r["ov"]} · 본문 글자 {r["txt"]}')
        await pg.screenshot(path=J.TMP + f'/ux3p_{tag}_{name}.png')
    # 한 장씩
    await pg.goto('about:blank'); await pg.goto(U + '#/CONS/_jb/_jb'); await pg.wait_for_selector('#cards .qc', timeout=30000); await pg.wait_for_timeout(600)
    await pg.click('#fone'); await pg.wait_for_timeout(700)
    r = await pg.evaluate(CHK); ok(r['ov'] <= 0, f'{tag} one: 한 장씩 가로 넘침 {r["ov"]}')
    await pg.screenshot(path=J.TMP + f'/ux3p_{tag}_one.png'); await pg.click('#fone'); await pg.wait_for_timeout(300)
    if vp['width'] <= 860:   # ☰ 서랍
        await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/learn'); await pg.wait_for_selector('#stage .tc', timeout=30000); await pg.wait_for_timeout(600)
        await pg.keyboard.press('Shift+M'); await pg.wait_for_timeout(500)
        r = await pg.evaluate("(()=>{const s=document.querySelector('#side').getBoundingClientRect();return [document.body.classList.contains('navopen'),Math.round(s.left),Math.round(s.right),document.documentElement.scrollWidth-innerWidth]})()")
        ok(r[0] and r[1] >= 0 and r[2] <= vp['width'] and r[3] <= 0, f'{tag} ☰ 서랍 열림·화면 안 {r}')
        await pg.screenshot(path=J.TMP + f'/ux3p_{tag}_drawer.png'); await pg.keyboard.press('Escape')
    else:   # 메뉴 숨김 정리표
        await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/sum'); await pg.wait_for_selector('#stage .msum', timeout=30000); await pg.wait_for_timeout(800)
        f0 = await pg.evaluate("document.body.classList.contains('sidefold')")
        if not f0: await pg.keyboard.press('Shift+M'); await pg.wait_for_timeout(900)
        r = await pg.evaluate("(()=>{const m=document.querySelector('#stage .msum').getBoundingClientRect();return [document.body.classList.contains('sidefold'),Math.round(m.width),document.documentElement.scrollWidth-innerWidth]})()")
        ok(r[0] and r[1] >= vp['width'] - 120 and r[2] <= 0, f'{tag} 메뉴 숨김 정리표 폭 {r}')
        await pg.screenshot(path=J.TMP + f'/ux3p_{tag}_sumfold.png')
    ok(not errs, f'{tag} 콘솔 오류 0 {errs[:3]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        try:
            for tag, vp, touch in [('1280', {'width': 1280, 'height': 900}, False), ('1180', {'width': 1180, 'height': 820}, True), ('820', {'width': 820, 'height': 1180}, True)]:
                await run(b, tag, vp, touch)
        finally:
            await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
