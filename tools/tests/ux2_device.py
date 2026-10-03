"""C10 회귀: 기기 옮기기와 공부 시간 합산
기기 A(맥)·B(아이패드)에 같은 날 60분·40분 → A 백업을 B에 합치면 B 오늘 합계 1:40, B의 time 원본 40분 그대로 · 같은 A 백업을 두 번 합쳐도 1:40 ·
백업 파일에 dev {id,name} · navigator.share 모의 성공 → lastBackup 갱신, 취소(reject) → 그대로 · 공유가 안 되면 내려받기 + [받았어요] → 갱신 ·
표시가 바뀐 지 3일 넘게 백업이 없으면 과목을 열 때 노란 띠(하루 한 번·✕) · 허브 홈 '이 기기(…) 마지막 보내기 …'·기기 옮기기 창 '다른 기기(맥)와 합친 때'.
맥 1280×900 + 아이패드 세로 820×1180 · 가로 1180×820. 스크린샷 work/_tmp/ux2i_c10_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
TODAY = J.study_today().isoformat()
SUM = f"Math.round(Object.values(__h.tDay('{TODAY}')).reduce((a,b)=>a+b,0)/60000)"
async def ctx_dev(b, vp, touch, did, name, mins, init=''):
    ctx = await b.new_context(viewport=vp, has_touch=touch, accept_downloads=True)
    if init: await ctx.add_init_script(init)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
    await pg.goto(U + '#/'); await pg.wait_for_selector('.hsj[data-s="OMS1"]')
    await pg.evaluate("([id,nm,d,m])=>{localStorage.clear();const ns='jblhub.v1.';localStorage.setItem(ns+'devId',JSON.stringify(id));localStorage.setItem(ns+'devName',JSON.stringify(nm));localStorage.setItem(ns+'time',JSON.stringify({[d]:{OMS1:m*60000}}));localStorage.setItem(ns+'timed',JSON.stringify({[d]:{'OMS1:DD1':m*60000}}));}", [did, name, TODAY, mins])
    await pg.evaluate("__h.bkClear()"); await pg.reload(); await pg.wait_for_selector('.hsj[data-s="OMS1"]')
    return ctx, pg, errs
async def merge(pg, f):
    await pg.evaluate("window.__mark=1;document.querySelector('#rfile').dataset.how='merge'"); await pg.set_input_files('#rfile', f)
    await pg.wait_for_function("!window.__mark", timeout=8000); await pg.wait_for_function("window.__h&&document.querySelector('.hsj[data-s]')", timeout=8000); await pg.wait_for_timeout(300)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ca, A, ea = await ctx_dev(b, {'width': 1280, 'height': 900}, False, 'devA', '맥', 60)
        cb, B, eb = await ctx_dev(b, {'width': 820, 'height': 1180}, True, 'devB', '아이패드', 40)
        j = json.loads(await A.evaluate("JSON.stringify(__h.bakFile())")); f = J.TMP + '/ux2_devA.json'; json.dump(j, open(f, 'w'))
        ok(j.get('dev', {}).get('id') == 'devA' and j['dev']['name'] == '맥', f"백업 파일 dev {j.get('dev')}")
        await merge(B, f)
        tb = json.loads(await B.evaluate("localStorage.getItem('jblhub.v1.time')")); s1 = await B.evaluate(SUM)
        ok(s1 == 100 and tb[TODAY]['OMS1'] == 40 * 60000, f'B 오늘 합계 {s1}분(1:40) · B time 원본 {tb[TODAY]["OMS1"] / 60000:.0f}분 그대로')
        td = json.loads(await B.evaluate("localStorage.getItem('jblhub.v1.timeDev')")); ok(td.get('devA', {}).get('name') == '맥', f"timeDev {list(td)}")
        await merge(B, f); ok(await B.evaluate(SUM) == 100, '같은 백업을 두 번 합쳐도 1:40')
        ok(await B.evaluate("Math.round(Object.values(__h.T.dlog['" + TODAY + "']||{}).reduce((a,b)=>a+b,0)/60000)") == 40, '강의별 원본(timed)도 그대로')
        await B.keyboard.press('Escape'); await B.evaluate("document.querySelector('#bkup').click()"); await B.wait_for_selector('#bkpop.on'); t = await B.inner_text('#bkpop')
        ok('이 기기(아이패드)' in t and '다른 기기(맥)와 합친 때' in t, f'기기 옮기기 창 {t[:90]!r}')
        await B.screenshot(path=J.TMP + '/ux2i_c10_pop_ipp.png'); await B.keyboard.press('Escape')
        await B.evaluate("document.querySelector('#bkup').click()")
        hp = await B.evaluate("document.querySelector('#home .bkp').textContent")   # ux3 H5 접힌 💾 더보기 안; ok('이 기기(아이패드) 마지막 보내기 없음' in hp, f'허브 홈 백업 패널 {hp[:60]!r}')
        # 공유 모의
        for tag, init, want in [('share-ok', "navigator.canShare=()=>true;navigator.share=()=>Promise.resolve();", True), ('share-cancel', "navigator.canShare=()=>true;navigator.share=()=>Promise.reject(new DOMException('abort','AbortError'));", False)]:
            cx, P, ep = await ctx_dev(b, {'width': 1180, 'height': 820}, True, 'devC', '아이패드', 10, init)
            await P.evaluate("document.querySelector('#bkup').click()"); await P.click('#bksend'); await P.wait_for_timeout(500)
            lb = await P.evaluate("localStorage.getItem('jblhub.v1.lastBackup')")
            ok((lb is not None) == want, f'{tag}: lastBackup {"갱신" if lb else "그대로"}')
            if want: await P.screenshot(path=J.TMP + '/ux2i_c10_share_ipl.png')
            ok(not ep, f'{tag} pageerror 0 {ep[:2]}'); await cx.close()
        # 내려받기 + [받았어요]
        await A.evaluate("document.querySelector('#bkup').click()"); await A.wait_for_selector('#bkpop.on')
        async with A.expect_download() as dl: await A.click('#bksend')
        d = await dl.value; ok(d.suggested_filename.startswith('JBL허브_맥_'), f'내려받기 {d.suggested_filename}')
        ok(await A.evaluate("localStorage.getItem('jblhub.v1.lastBackup')") is None, '내려받기만으로는 lastBackup 그대로')
        await A.click('#bkpop [data-bkgot]'); await A.wait_for_timeout(200); ok(await A.evaluate("localStorage.getItem('jblhub.v1.lastBackup')") is not None, '[받았어요] → lastBackup 갱신')
        await A.screenshot(path=J.TMP + '/ux2i_c10_pop_mac.png')
        # 노란 띠
        await A.evaluate("(()=>{const ns='jblhub.v1.';localStorage.setItem(ns+'lastBackup',String(Date.now()-5*864e5-3600e3));localStorage.setItem(ns+'annAt.OMS1',String(Date.now()-4*864e5));localStorage.removeItem(ns+'bkNagDay');})()")
        await A.goto('about:blank'); await A.goto(U + '#/OMS1/DD1/learn'); await A.wait_for_selector('#bkband', timeout=5000)
        t = await A.inner_text('#bkband'); ok('마지막 백업 5일 전' in t and '보내기' in t, f'노란 띠 {t!r}')
        await A.screenshot(path=J.TMP + '/ux2i_c10_band_mac.png')
        await A.click('#bkband [data-bkx]'); ok(await A.locator('#bkband').count() == 0, '✕로 닫힘')
        await A.goto('about:blank'); await A.goto(U + '#/CONS/_home'); await A.wait_for_timeout(1200); ok(await A.locator('#bkband').count() == 0, '하루 한 번')
        ok(not ea and not eb, f'pageerror 0 {ea[:2]} {eb[:2]}')
        await ca.close(); await cb.close(); await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
