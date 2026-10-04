"""10-04 사용자 요청 회귀:
① 북마크 카드 모아보기(#/<S>/_cbm) 위 강의별 탭 — 전체 + 강의마다 · 누르면 그 강의만 · 새로고침 뒤 고른 탭 유지(LS cbmtab.<S>) · 북마크 1강의뿐이면 탭 없음
② ■ 멈춤 = 손으로 ▶ 할 때까지 그대로(입력·새 문서·25분 뒤·다시 열기 모두 안 잼) · 3분 넘게 움직이면 띠로 한 번 알림 · 띠 [▶ 공부 시작] = 세션
③ 자동 측정 켬 + ☕ 쉬기(손) → 10초 뒤 스크롤·클릭 = 공부로(자동 측정에서 쉬었으면 run, 세션에서 쉬었으면 sess) · Esc·마우스 움직임만은 아님 · 자동 측정 끔이면 그대로 쉼
  .venv/bin/python tools/tests/ux4g_A.py"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
NOW = datetime.datetime(2026, 10, 5, 10, 0, 0); MIN = 60000
async def boot(pg, h, ms=1800):
    await pg.goto('about:blank'); await pg.goto(U + h, timeout=120000); await pg.clock.run_for(ms)
    for _ in range(150):
        if await pg.evaluate("!!(window.__h&&__h.plStat&&__h.plStat().pend===0)"): break
        await pg.wait_for_timeout(100); await pg.clock.run_for(100)
async def fresh(pg, h):
    await boot(pg, h); await pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); await boot(pg, h)
async def st(pg): return await pg.evaluate("__h.trState()")
async def wheel(pg, n, step=30000):
    for i in range(n):
        await pg.mouse.move(400 + i % 7, 420); await pg.mouse.wheel(0, 120 if i % 2 else -120); await pg.clock.run_for(step)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        # ---------- ① 북마크 카드 강의 탭 ----------
        ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.clock.install(time=NOW)
        await fresh(pg, '#/OMS1/_home')
        # 강의 두 개에서 카드 하나씩 북마크(카드 끝 버튼)
        lects = await pg.evaluate("[...document.querySelectorAll('#hlec .lcard[data-d], #hlec [data-d]')].map(e=>e.dataset.d).filter((v,i,a)=>v&&!v.startsWith('_')&&a.indexOf(v)===i).slice(0,2)")
        ok(len(lects) == 2, f'강의 두 개 {lects}')
        for k in lects:
            await boot(pg, f'#/OMS1/{k}/learn')
            await pg.evaluate("document.querySelector('#stage .tc .cbend').click()"); await pg.clock.run_for(300)
        await boot(pg, '#/OMS1/_cbm')
        tabs = await pg.evaluate("[...document.querySelectorAll('#stage .cbmtabs [data-cbtab]')].map(b=>b.dataset.cbtab)")
        ok(tabs == [''] + lects, f'탭 = 전체 + 북마크 강의 {tabs}')
        vis = "[...document.querySelectorAll('#stage .cbmsec')].filter(x=>!x.hidden).map(x=>x.dataset.cbk)"
        ok(await pg.evaluate(vis) == lects, '처음 = 전체')
        await pg.click(f'#stage .cbmtabs [data-cbtab="{lects[1]}"]'); await pg.clock.run_for(300)
        ok(await pg.evaluate(vis) == [lects[1]], f'{lects[1]} 탭 → 그 강의만')
        ok(await pg.evaluate(f"document.querySelector('#stage .cbmtabs [data-cbtab=\"{lects[1]}\"]').getAttribute('aria-selected')") == 'true', 'aria-selected')
        await boot(pg, '#/OMS1/_cbm')
        ok(await pg.evaluate(vis) == [lects[1]], '새로고침 뒤 고른 탭 유지')
        await pg.click('#stage .cbmtabs [data-cbtab=""]'); await pg.clock.run_for(300)
        ok(await pg.evaluate(vis) == lects, '전체 탭 → 모두')
        await pg.screenshot(path=J.TMP + '/ux4g_cbm.png')
        # 한 강의 북마크를 모두 빼면 탭 없음 · 저장된 탭이 없는 강의면 전체
        await pg.click(f'#stage .cbmtabs [data-cbtab="{lects[0]}"]'); await pg.clock.run_for(200)
        await boot(pg, f'#/OMS1/{lects[0]}/learn'); await pg.evaluate("document.querySelector('#stage .tc.cbm .cbend').click()"); await pg.clock.run_for(300)
        await boot(pg, '#/OMS1/_cbm')
        ok(await pg.evaluate("!document.querySelector('#stage .cbmtabs')") and await pg.evaluate(vis) == [lects[1]], '북마크 강의 하나뿐 → 탭 없음 · 그 강의 보임')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await ctx.close()

        # ---------- ② ■ 멈춤 ----------
        ctx = await b.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.clock.install(time=NOW)
        await fresh(pg, '#/CONS/WHT/learn')
        await wheel(pg, 4); ok(await st(pg) == 'run', '자동 측정 중')
        await pg.evaluate("__h.trStop()"); await pg.clock.run_for(300); ok(await st(pg) == 'end', '■ → 멈춤')
        t0 = await pg.evaluate("__h.tDay('2026-10-05').CONS||0")
        await wheel(pg, 2, 2000); await pg.mouse.click(600, 500); await pg.clock.run_for(1000)
        ok(await st(pg) == 'end', '■ 뒤 스크롤·클릭 → 멈춤 그대로')
        await pg.evaluate("location.hash='#/CONS/_jb'"); await pg.clock.run_for(1500); await wheel(pg, 2, 2000)
        ok(await st(pg) == 'end', '■ 뒤 다른 문서 열고 움직임 → 멈춤 그대로')
        await pg.clock.fast_forward(25 * MIN); await wheel(pg, 1, 1000)
        ok(await st(pg) == 'end', '■ 뒤 25분 지나 움직임 → 멈춤 그대로')
        await boot(pg, '#/CONS/WHT/learn'); await wheel(pg, 1, 1000)
        ok(await st(pg) == 'end', '■ 뒤 다시 열기 → 멈춤 그대로')
        await wheel(pg, 8, 30000)
        band = await pg.evaluate("(b=>b.hidden?'':b.textContent)(document.querySelector('#trband'))")
        ok('멈춤 중' in band, f'3분 넘게 움직임 → 띠 알림 {band[:30]!r}')
        t1 = await pg.evaluate("__h.tDay('2026-10-05').CONS||0"); ok(t1 == t0, f'멈춤 중 공부 시간 그대로 (+{(t1 - t0) / 1000:.0f}초)')
        await pg.tap('#trband [data-trq=start]'); await pg.clock.run_for(300)
        ok(await st(pg) == 'sess', f'띠 [▶ 공부 시작] → 세션 ({await st(pg)})')
        ok(await pg.evaluate("document.querySelector('#trband').hidden"), '띠 닫힘')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await ctx.close()

        # ---------- ③ ☕ 쉬기 뒤 움직이면 공부 ----------
        ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.clock.install(time=NOW)
        await fresh(pg, '#/CONS/WHT/learn')
        await wheel(pg, 4); ok(await st(pg) == 'run', '자동 측정 중')
        await pg.evaluate("__h.trRest()"); await pg.clock.run_for(300); ok(await st(pg) == 'rest', '☕ 쉬기 → 쉬는 중')
        await pg.mouse.wheel(0, 100); await pg.clock.run_for(500)
        ok(await st(pg) == 'rest', '쉬기 누르고 10초 안 스크롤 → 쉬는 중 그대로')
        await pg.clock.run_for(2 * MIN); await pg.keyboard.press('Escape'); await pg.mouse.move(700, 300); await pg.clock.run_for(500)
        ok(await st(pg) == 'rest', 'Esc·마우스 움직임만 → 쉬는 중 그대로')
        await pg.mouse.move(600, 500); await pg.mouse.wheel(0, 120); await pg.clock.run_for(1000)
        ok(await st(pg) == 'run', f'2분 쉬고 스크롤 → 자동 측정 ({await st(pg)})')
        r = await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.trest')||'{}')")
        ok(json.dumps(r).count('2026-10-05') >= 1, f'쉰 2분은 휴식 기록 {str(r)[:80]}')
        # 세션에서 쉬기 → 클릭 → 세션
        await pg.evaluate("__h.trStart()"); await pg.clock.run_for(MIN); await pg.evaluate("__h.trRest()"); await pg.clock.run_for(MIN)
        await pg.mouse.click(640, 500); await pg.clock.run_for(500)
        ok(await st(pg) == 'sess', f'세션에서 쉬고 클릭 → 세션 ({await st(pg)})')
        # 자동 측정 끔 → 쉬는 중 그대로
        await pg.evaluate("__h.trStop();__h.T.auto=false;localStorage.setItem('jblhub.v1.tauto','false')"); await pg.evaluate("__h.trStart()"); await pg.clock.run_for(MIN)
        await pg.evaluate("__h.trRest()"); await pg.clock.run_for(MIN); await pg.mouse.wheel(0, 120); await pg.clock.run_for(500)
        ok(await st(pg) == 'rest', f'자동 측정 끔 → 스크롤해도 쉬는 중 ({await st(pg)})')
        # ---------- ③-2 카드 머리 기출 칩: 문항 둘 이상이면 'n문항' ----------
        await boot(pg, '#/OMS1/DD1/learn')
        r = await pg.evaluate("[...document.querySelectorAll('#stage .tc .tchips .chip.yr')].map(b=>[(b.dataset.gos||'').split(' ').filter(Boolean).length||1,b.textContent.trim()])")
        multi = [x for x in r if x[0] > 1]; single = [x for x in r if x[0] == 1]
        ok(multi and all(f'{n}문항' in t for n, t in multi), f'여러 문항 칩에 문항 수 {multi[:3]}')
        ok(all('문항' not in t for _, t in single), f'한 문항 칩은 그대로 {single[:3]}')
        # ---------- ④ 메모 칸 밖 누르면 입력 끝 → M = 메모 토글 (터치·마우스) ----------
        for touch in (False, True):
            c4 = await b.new_context(viewport={'width': 1180, 'height': 820}, has_touch=touch); q = await c4.new_page(); e4 = []
            q.on('pageerror', lambda e: e4.append(str(e)[:200])); await q.clock.install(time=NOW)
            await fresh(q, '#/CONS/WHT/learn'); tg = 'touch' if touch else 'mouse'
            await q.keyboard.press('m'); await q.clock.run_for(300)
            ok(await q.evaluate("document.querySelector('#memo').classList.contains('on')"), f'{tg} M → 메모 열림')
            await q.click('#memota'); await q.keyboard.type('abc m'); await q.clock.run_for(500)
            ok(await q.evaluate("document.querySelector('#memota').value") == 'abc m', f'{tg} 메모 쓰는 중 m = 글자')
            if touch: await q.tap('#stage .tc .tbody')
            else: await q.mouse.click(500, 500)
            await q.clock.run_for(400)
            ok(await q.evaluate("document.activeElement!==document.querySelector('#memota')"), f'{tg} 본문 누름 → 메모 입력 끝')
            await q.keyboard.press('m'); await q.clock.run_for(300)
            ok(await q.evaluate("document.querySelector('#memota').value") == 'abc m' and not await q.evaluate("document.querySelector('#memo').classList.contains('on')"), f'{tg} 그 뒤 M → 메모 닫힘(글자 안 들어감)')
            ok(json.loads(await q.evaluate("localStorage.getItem('jblhub.v1.memo.CONS.WHT')") or '""') == 'abc m', f'{tg} 메모 저장됨')
            ok(not e4, f'{tg} pageerror 0 {e4[:2]}')
            await c4.close()
        # ---------- ⑤ 시계 알약 = 마지막으로 공부 시작한 때부터(세션도) ----------
        await pg.evaluate("__h.trStop();__h.T.auto=true;localStorage.setItem('jblhub.v1.tauto','true')")
        await pg.evaluate("__h.trStart()"); await pg.clock.run_for(10 * MIN)
        await pg.evaluate("__h.trRest()"); await pg.clock.run_for(5 * MIN); await pg.evaluate("__h.trResume()"); await pg.clock.run_for(2 * MIN + 5000)
        lab = await pg.inner_text('#clock .ckl')
        ok(lab.startswith('공부 2:0'), f'세션 10분 → 쉬기 5분 → 다시 2분: 알약 {lab!r} (공부 2:0x — 세션 합계 12분 아님)')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
