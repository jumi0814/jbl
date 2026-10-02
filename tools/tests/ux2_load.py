"""B08·B09 회귀: 첫 화면 불러오기(뼈대·진행 막대·요청한 과목 먼저·실패 [다시]) / 검색 색인 나눠 만들기(첫 입력 긴 작업 < 200ms, CPU×4)·종류 칩(&k=)·JB '답 바로 보기'.
docs/를 로컬 http 서버로 열고 page.route로 팩마다 1초씩 늦추거나 404를 낸다. 맥 1280×900 + 아이패드 세로 820×1180 + 가로 1180×820. 스크린샷 work/_tmp/ux2i_b0*_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, threading, http.server, socketserver, time, re
from playwright.async_api import async_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def serve(d):
    class Q(http.server.SimpleHTTPRequestHandler):
        def __init__(s, *a, **k): super().__init__(*a, directory=d, **k)
        def log_message(s, *a): pass
    class S(socketserver.ThreadingTCPServer): allow_reuse_address = True; daemon_threads = True
    srv = S(('127.0.0.1', 0), Q); threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv
PACK = re.compile(r'/packs/([A-Z0-9]+)\.js(\?|$)')

async def run(b, base, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    # ---- B08-a 팩마다 1초 늦춤 → 0.3초에 뼈대·진행 막대
    async def slow(route):
        await asyncio.sleep(1.0); await route.continue_()
    await pg.route(PACK, slow)
    t0 = time.time(); await pg.goto(base + '/index.html#/', wait_until='commit'); await pg.wait_for_timeout(300)
    st = await pg.evaluate("(()=>{const b=document.querySelector('#plbox');return b&&b.offsetParent?b.textContent:''})()")
    ok('과목 자료 불러오는 중' in st and '0/6' in st, f'0.3초: 뼈대 + 진행 막대 {st[:60]!r}')
    await pg.screenshot(path=J.TMP + f'/ux2i_b08_skel_{tag}.png')
    await pg.wait_for_function("window.__h&&__h.plStat().pend===0", timeout=20000)
    ok(await pg.evaluate("document.querySelectorAll('#home .hsj[data-s]').length") == 6 and not await pg.evaluate("document.querySelector('#home .plc')"), '모두 도착 → 과목 표 6행·불러오는 중 칩 없음')
    # ---- B08-b 딥링크는 그 과목 팩만 기다림
    await pg.goto('about:blank'); t0 = time.time(); await pg.goto(base + '/index.html#/OMS1/DD1/learn', wait_until='commit')
    await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3", timeout=20000); dt = time.time() - t0
    n = await pg.evaluate("Object.keys(__h.PACKS).length")
    ok(dt < 3.0 and n <= 2, f'#/OMS1/DD1/learn → {dt:.1f}초에 학습 탭 · 그때 불러온 팩 {n}개(다른 팩을 기다리지 않음)')
    await pg.screenshot(path=J.TMP + f'/ux2i_b08_deep_{tag}.png')
    await pg.wait_for_function("__h.plStat().pend===0", timeout=30000)
    ok(await pg.evaluate("Object.keys(__h.PACKS).length") == 6, '나머지는 차례로 도착')
    await pg.unroute(PACK, slow)
    # ---- B08-c 404 → 실패 안내 → [다시]
    hits = {'n': 0}
    async def f404(route):
        hits['n'] += 1
        if hits['n'] == 1: await route.fulfill(status=404, body='nope')
        else: await route.continue_()
    await pg.route(re.compile(r'/packs/PHARM\.js'), f404)
    await pg.goto('about:blank'); await pg.goto(base + '/index.html#/')
    await pg.wait_for_function("document.querySelector('#packbar .plbad')", timeout=15000)
    t = await pg.inner_text('#packbar'); ok('PHARM' in t and '실패' in t and '다시' in t, f'팩 404 → 실패 안내 {t!r}')
    ok('불러오기 실패' in await pg.inner_text('#home .hsj.off[data-off=PHARM]'), '허브 과목 표에도 ⚠ 불러오기 실패')
    await pg.screenshot(path=J.TMP + f'/ux2i_b08_fail_{tag}.png')
    await pg.click('#packbar [data-plretry=PHARM]')
    await pg.wait_for_function("__h.PACKS.PHARM&&document.querySelector('#home .hsj[data-s=PHARM]')", timeout=15000)
    ok(await pg.evaluate("document.querySelector('#packbar').hidden"), '[다시] → 성공 · 안내 사라짐 · 카드 채워짐')
    await pg.unroute(re.compile(r'/packs/PHARM\.js'), f404)
    # ---- B09 검색: 첫 입력 긴 작업(CPU×4) · 종류 칩 · 답 바로 보기
    cdp = await ctx.new_cdp_session(pg)
    await pg.goto('about:blank'); await pg.goto(base + '/index.html#/'); await pg.wait_for_function("__h.plStat().pend===0", timeout=20000)
    await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    await pg.evaluate("window.__LT=[];new PerformanceObserver(l=>l.getEntries().forEach(e=>__LT.push(Math.round(e.duration)))).observe({entryTypes:['longtask']})")
    ready0 = await pg.evaluate("__h.sxProg().ready")
    await pg.click('#gsearch'); await pg.keyboard.type('warfarin', delay=60)
    await pg.wait_for_function("document.querySelector('#home .skinds')", timeout=20000); await pg.wait_for_timeout(400)
    lt = await pg.evaluate("__LT"); mx = max(lt or [0])
    ok(mx < 200, f'첫 입력(색인 {"끝남" if ready0 else "만드는 중"}) 긴 작업 최대 {mx}ms < 200ms ({len(lt)}개)')
    await pg.wait_for_function("__h.sxProg().ready", timeout=60000)
    lt = await pg.evaluate("__LT"); ok(max(lt or [0]) < 200, f'색인 만드는 동안 긴 작업 최대 {max(lt or [0])}ms')
    await pg.evaluate("new Promise(r=>setTimeout(()=>{const t=performance.now();while(performance.now()-t<90);setTimeout(r,50);},0))"); await pg.wait_for_timeout(200)
    ok(len(await pg.evaluate("__LT")) > len(lt), '대조: 일부러 만든 긴 작업은 관측됨(관측기 동작)')
    await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 1})
    await pg.wait_for_timeout(300)
    chips = await pg.evaluate("[...document.querySelectorAll('#home .skinds [data-sk]')].map(b=>b.textContent)")
    ok(len(chips) == 5 and chips[0].startswith('전체') and not await pg.evaluate("document.querySelector('#home .sxw')"), f'종류 칩 {chips}')
    nall = int(chips[0].split()[-1]); njb = int([c for c in chips if c.startswith('JB')][0].split()[-1])
    await pg.evaluate("document.querySelector('#home [data-sk=jb]').click()"); await pg.wait_for_timeout(300)
    tl = await pg.evaluate("[...document.querySelectorAll('#home .sres .stl b')].map(b=>b.textContent)")
    ok(len(tl) == njb and all(x.startswith('JB ') or ' · JB ' in x for x in tl) and (await pg.evaluate('location.hash')).endswith('&k=jb'), f'JB 칩 → JB 결과만 {len(tl)}건 · 해시 &k=jb {tl[:2]}')   # ux4f 결과 줄 머리에 과목 코드 없음(사용자 10-01 코드·줄임 대신 원래 이름) — 줄이 \'JB …\'로 시작
    await pg.screenshot(path=J.TMP + f'/ux2i_b09_jb_{tag}.png')
    await pg.reload(); await pg.wait_for_function("document.querySelector('#home .skinds [data-sk=jb].on')&&__h.sxProg().ready", timeout=30000); await pg.wait_for_timeout(300)
    tl2 = await pg.evaluate("document.querySelectorAll('#home .sres').length")
    ok(tl2 == njb, f'새로고침해도 JB 칩 유지 ({tl2})')
    await pg.evaluate("document.querySelector('#home [data-sk=\"\"]').click()"); await pg.wait_for_timeout(200)
    ok(await pg.evaluate("document.querySelectorAll('#home .sres').length") == nall and not (await pg.evaluate('location.hash')).count('&k='), '전체 칩 → 모두 · &k 없음')
    await pg.evaluate("document.querySelector('#home [data-sk=jb]').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('#home .sres .sans').click()"); await pg.wait_for_timeout(900)
    st = await pg.evaluate("[location.hash,!!document.querySelector('#cards .qc.open')]")
    ok('/_jb' in st[0] and st[1], f"'답 바로 보기' → JB 카드 답 펼침 {st}")
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), '가로 넘침 0')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def main():
    srv = serve(J.DOCS); base = f'http://127.0.0.1:{srv.server_address[1]}'
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, base, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, base, {'width': 820, 'height': 1180}, True, 'ipp')
        await run(b, base, {'width': 1180, 'height': 820}, True, 'ipl')
        await b.close()
    srv.shutdown()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
