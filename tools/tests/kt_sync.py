"""U03 회귀: 두 창 동시 사용(채점·공부 시간 합산)·옛 mk 형식·무활동 시간 계상.
docs/index.html(J.HUB_URL)을 열고 스크린샷은 work/_tmp/"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime
from playwright.async_api import async_playwright
U = J.HUB_URL; NS = 'jblhub.v1.'
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def ls(pg, k): return json.loads(await pg.evaluate(f"localStorage.getItem('{NS}{k}')") or 'null')
def today(ms):
    d = datetime.datetime.fromtimestamp(ms / 1000); return d.strftime('%Y-%m-%d')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); errs = []
        A = await ctx.new_page(); Bp = await ctx.new_page()
        for pg in (A, Bp): pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await A.goto(U + '#/PHARM/_jb/'); await A.wait_for_timeout(800); await A.evaluate('localStorage.clear()')
        # ① 두 창 채점: A·B 모두 연 뒤 A에서 RX01 맞음, B에서 RX02 틀림
        await A.goto('about:blank'); await A.goto(U + '#/PHARM/_jb/'); await Bp.goto(U + '#/PHARM/_jb/'); await A.wait_for_timeout(1200); await Bp.wait_for_timeout(1200)
        await A.click('#c-RX01 [data-mk="ok"]'); await A.wait_for_timeout(300)
        ok(await Bp.evaluate("document.querySelector('#c-RX01').classList.contains('mk-ok')"), '다른 창의 맞음 표시가 B 화면에 바로 반영(storage 이벤트)')
        await Bp.click('#c-RX02 [data-mk="ng"]'); await Bp.wait_for_timeout(300)
        await A.reload(); await A.wait_for_timeout(1200)
        mk = await ls(A, 'mk.PHARM')
        ok(mk['ok'].get('RX01') == 1 and mk['ng'].get('RX02') == 1, f'새로고침 뒤 RX01 맞음·RX02 틀림 둘 다 남음 {mk}')
        ok(await A.evaluate("document.querySelector('#c-RX01').classList.contains('mk-ok')&&document.querySelector('#c-RX02').classList.contains('mk-ng')"), '화면 표시도 둘 다')
        # ③ 옛 형식 mk (bm 없음)·깨진 값
        for bad in ('{"ok":{},"ng":{}}', '{"ok":[],"ng":null,"bm":"x"}', '[]'):
            await A.evaluate(f"localStorage.setItem('{NS}mk.PHARM', {json.dumps(bad)})")
            await A.goto('about:blank'); await A.goto(U + '#/PHARM/_jb/'); await A.wait_for_timeout(1000)
            await A.click('#jbbar [data-qf="bm"]'); await A.click('#jbbar [data-qf=""]')
            await A.click('#c-RX03 [data-mk="bm"]'); await A.click('#c-RX03 [data-mk="ok"]'); await A.click('#c-RX04 [data-mk="ng"]')
            await A.click('#jbbar [data-qf="bm"]'); vis = await A.evaluate("[...document.querySelectorAll('#cards .qc:not(.hid)')].map(c=>c.dataset.id)")
            await A.click('#jbbar [data-qf="todo"]'); await A.click('#jbbar [data-qf="ng"]'); await A.click('#jbbar [data-qf=""]')
            await A.goto('about:blank'); await A.goto(U + '#/PHARM/RX/jb'); await A.wait_for_timeout(900)
            await A.click('#fone'); await A.keyboard.press('b'); await A.keyboard.press('o'); await A.keyboard.press('x')
            await A.goto('about:blank'); await A.goto(U + '#/PHARM/_home/'); await A.wait_for_timeout(700)
            ok(vis == ['RX03'] and not errs, f'옛·깨진 mk {bad} → ★ 필터·O/X·키보드 pageerror 0 ({vis}) {errs[:1]}')
        # 메모: 포커스 없는 창은 새 값을 불러오고, 입력 중인 창은 저장할 때 구분선으로 합침
        await A.goto('about:blank'); await A.goto(U + '#/PHARM/RX/learn'); await Bp.goto('about:blank'); await Bp.goto(U + '#/PHARM/RX/learn'); await A.wait_for_timeout(900); await Bp.wait_for_timeout(900)
        await A.keyboard.press('Shift+M'); await A.fill('#memota', '창A 메모'); await A.locator('#memota').blur(); await A.wait_for_timeout(200)
        ok(await Bp.evaluate("document.querySelector('#memota').value") == '창A 메모', '포커스 없는 창은 다른 창의 메모를 바로 불러옴')
        await Bp.keyboard.press('Shift+M'); await Bp.wait_for_timeout(100); await Bp.type('#memota', ' + 창B 입력 중')
        await A.fill('#memota', '창A 메모 수정'); await A.locator('#memota').blur(); await A.wait_for_timeout(200)
        await Bp.locator('#memota').blur(); await Bp.wait_for_timeout(200)
        mm = await ls(A, 'memo.PHARM.RX') or ''
        ok('창B 입력 중' in mm and '창A 메모 수정' in mm and '다른 창의 메모와 합침' in mm, f'입력 중 다른 창이 바꾼 메모는 구분선으로 합침: {mm!r}')
        # ④ 공부 시간: 가짜 시계 — 두 창 합산, 9분 무입력은 1분 20초 이하
        await b.close(); b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1280, 'height': 900})
        A = await ctx.new_page(); Bp = await ctx.new_page()
        for pg in (A, Bp): pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        t0 = int(datetime.datetime(2026, 9, 20, 10, 0, 0).timestamp() * 1000)
        for pg in (A, Bp): await pg.clock.install(time=t0 / 1000)
        await A.goto(U + '#/PHARM/_jb/'); await A.clock.run_for(1500); await A.evaluate('localStorage.clear()')
        await A.goto('about:blank'); await A.goto(U + '#/PHARM/_jb/'); await Bp.goto(U + '#/PHARM/RX/learn')
        for pg in (A, Bp): await pg.clock.run_for(1500)
        for pg in (A, Bp):
            for i in range(3):
                await pg.mouse.move(300 + i * 10, 400); await pg.clock.run_for(10000)
        await A.clock.run_for(1500); await Bp.clock.run_for(1500)
        tm = await ls(A, 'time') or {}; d = today(t0); s = (tm.get(d) or {}).get('PHARM', 0)
        ok(s >= 50000, f'두 창 공부 시간 합산: {s/1000:.0f}초 (각 창 약 30초 → 50초 이상)')
        await Bp.close()
        before = s
        await A.mouse.move(500, 500); await A.clock.run_for(1000)
        await A.clock.run_for(9 * 60 * 1000)
        tm = await ls(A, 'time') or {}; s2 = (tm.get(d) or {}).get('PHARM', 0)
        ok(s2 - before <= 80000, f'9분 무입력 → 늘어난 시간 {(s2-before)/1000:.0f}초 ≤ 80초')
        await A.mouse.move(520, 500); await A.clock.run_for(25000)
        tm = await ls(A, 'time') or {}; s3 = (tm.get(d) or {}).get('PHARM', 0)
        ok(0 < s3 - s2 <= 30000, f'다시 움직이면 이어서 잼: +{(s3-s2)/1000:.0f}초')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else 'FAIL'); _sys.exit(1 if fails else 0)
