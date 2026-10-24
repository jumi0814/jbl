"""10-24 기기 자동 동기화 회귀(사용자 '모바일에서 볼 때랑 컴퓨터에서 볼 때랑 넘버링 내역, 별표 카드, 별표 문제 등등이 다 연동 · 지금 데이터를 합칠 땐 컴퓨터 기준').
GitHub Gist API를 가짜 서버(page.route)로 흉내 내고 컴퓨터(1280)·휴대폰(393 터치) 두 창으로:
 ① 컴퓨터가 토큰으로 연결 → Gist 만들고 기기 파일 보냄 ② 휴대폰이 연결 코드로 연결 → 컴퓨터 기록을 받아 합침(★ 카드 합집합 · 넘버링 문제 = 컴퓨터 것 · 휴대폰에만 있던 ★ 유지)
 ③ 컴퓨터가 휴대폰 파일을 받아 합침 ④ 휴대폰에서 ★ 하나를 지우면 컴퓨터에서도 지워짐 ⑤ 컴퓨터에서 넘버링을 고치면 휴대폰에 들어감
 ⑥ 토큰은 백업 파일·Gist 파일에 들어가지 않음 ⑦ 틀린 토큰 = 오류 알림만(페이지 오류 0) ⑧ 공부 중(입력 뒤)에 받은 변경은 바로 덮지 않고 [지금 반영] 알림."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []; TOK = 'ghp_TESTTOKEN0123456789abcdefABCDEF'; NS = 'jblhub.v1.'
G = {}   # 가짜 Gist 저장소 id → {description, files{name: content}}
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CORS = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Authorization, Content-Type, Accept', 'Access-Control-Allow-Methods': 'GET, POST, PATCH, OPTIONS', 'Content-Type': 'application/json'}
async def gh(route):
    rq = route.request; m = rq.method; path = rq.url.split('api.github.com', 1)[1]
    if m == 'OPTIONS': return await route.fulfill(status=204, headers=CORS)
    if (rq.headers.get('authorization') or '') != 'Bearer ' + TOK: return await route.fulfill(status=401, headers=CORS, body='{"message":"Bad credentials"}')
    if m == 'GET' and path.startswith('/gists?'): return await route.fulfill(status=200, headers=CORS, body=json.dumps([{'id': k, 'description': v['description']} for k, v in G.items()]))
    if m == 'POST' and path == '/gists':
        b = json.loads(rq.post_data); gid = 'g%d' % (len(G) + 1); G[gid] = {'description': b['description'], 'files': {k: v['content'] for k, v in b['files'].items()}}
        return await route.fulfill(status=201, headers=CORS, body=json.dumps({'id': gid}))
    gid = path.split('/')[2] if path.startswith('/gists/') else ''
    if gid not in G: return await route.fulfill(status=404, headers=CORS, body='{}')
    if m == 'GET': return await route.fulfill(status=200, headers=CORS, body=json.dumps({'id': gid, 'files': {k: {'content': v, 'truncated': False, 'raw_url': ''} for k, v in G[gid]['files'].items()}}))
    if m == 'PATCH':
        for k, v in json.loads(rq.post_data)['files'].items():
            if v is None: G[gid]['files'].pop(k, None)
            else: G[gid]['files'][k] = v['content']
        return await route.fulfill(status=200, headers=CORS, body=json.dumps({'id': gid}))
    await route.fulfill(status=400, headers=CORS, body='{}')
async def setv(pg, k, v): await pg.evaluate("([k,v])=>localStorage.setItem(k,v)", [NS + k, json.dumps(v)])
async def getv(pg, k): return await pg.evaluate("k=>{const v=JBLSYNC.get(k);return v==null?null:JSON.parse(v)}", k)
async def settle(pg, ms=1500):
    for _ in range(40):
        await pg.wait_for_timeout(250)
        try:
            if not await pg.evaluate("window.JBLSYNC&&JBLSYNC.busy()"): break
        except Exception: pass
    await pg.wait_for_timeout(ms)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        dc = await b.new_context(viewport={'width': 1280, 'height': 900}); pc = await b.new_context(viewport={'width': 393, 'height': 852}, is_mobile=True, has_touch=True,
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')
        for c in (dc, pc): await c.route('https://api.github.com/**', gh)
        dk = await dc.new_page(); ph = await pc.new_page(); errs = []
        for pg in (dk, ph): pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for pg in (dk, ph):
            await pg.goto(U + '#/'); await pg.wait_for_timeout(800); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
        await setv(dk, 'cbm.IMPL', {'A1': 1000, 'A2': 1000}); await setv(dk, 'num.i.IMPL.n1', {'u': 1000, 's': '컴퓨터 스토리'}); await setv(dk, 'lbm.IMPL', {'PART': 1000})
        await setv(ph, 'cbm.IMPL', {'A3': 1000}); await setv(ph, 'num.i.IMPL.n1', {'u': 5000, 's': '휴대폰 스토리(더 최근)'})
        for pg in (dk, ph): await pg.reload(); await pg.wait_for_timeout(1500)
        # ① 컴퓨터 연결
        await dk.evaluate(f"JBLSYNC.connect('{TOK}')"); await settle(dk)
        files = list(G.get('g1', {}).get('files', {}))
        ok(len(G) == 1 and any(f.endswith('.json') and f.startswith('dev-') for f in files), f'① 컴퓨터 연결 → Gist 만들고 기기 파일 보냄 {files}')
        ok(await dk.evaluate("JBLSYNC.state().primary===true"), '① 컴퓨터 = 기준 기기')
        # ② 휴대폰 연결(연결 코드)
        code = await dk.evaluate("JBLSYNC.code()")
        async with ph.expect_navigation(timeout=15000): await ph.evaluate(f"JBLSYNC.connect('{code}')")
        await settle(ph)
        cb = await getv(ph, 'cbm.IMPL'); ni = await getv(ph, 'num.i.IMPL.n1')
        ok(cb is not None and set(cb) == {'A1', 'A2', 'A3'}, f'② 휴대폰 ★ 카드 = 컴퓨터 것 + 휴대폰에만 있던 것 {cb}')
        ok(ni is not None and ni.get('s') == '컴퓨터 스토리', f'② 넘버링 문제는 컴퓨터 기준 {ni}')
        ok((await getv(ph, 'lbm.IMPL') or {}).get('PART') == 1000, '② 강의 북마크도 받음')
        ok(await ph.evaluate("JBLSYNC.state().primary===false"), '② 휴대폰 = 기준 아님')
        # ③ 컴퓨터가 휴대폰 파일 받기(지금 동기화 = 바로 반영 → 새로고침)
        async with dk.expect_navigation(timeout=15000): await dk.evaluate("JBLSYNC.tick({now:true})")
        await settle(dk)
        cb = await getv(dk, 'cbm.IMPL'); ok(cb is not None and set(cb) == {'A1', 'A2', 'A3'}, f'③ 컴퓨터에도 휴대폰 ★ 카드 {cb}')
        # ④ 휴대폰에서 ★ A1 지움 → 컴퓨터에서도 지워짐
        await ph.evaluate("JBLSYNC.tick({now:true})"); await settle(ph, 500)
        await setv(ph, 'cbm.IMPL', {'A2': 1000, 'A3': 1000}); await ph.evaluate("JBLSYNC.tick({pull:false})"); await settle(ph, 500)
        async with dk.expect_navigation(timeout=15000): await dk.evaluate("JBLSYNC.tick({now:true})")
        await settle(dk)
        cb = await getv(dk, 'cbm.IMPL'); ok(cb is not None and set(cb) == {'A2', 'A3'}, f'④ 휴대폰에서 지운 ★가 컴퓨터에서도 지워짐 {cb}')
        # ⑤ 컴퓨터에서 넘버링 고침 → 휴대폰
        await setv(dk, 'num.i.IMPL.n1', {'u': 9000, 's': '컴퓨터에서 고침'}); await dk.evaluate("JBLSYNC.tick({pull:false})"); await settle(dk, 500)
        async with ph.expect_navigation(timeout=15000): await ph.evaluate("JBLSYNC.tick({now:true})")
        await settle(ph)
        ni = await getv(ph, 'num.i.IMPL.n1'); ok(ni is not None and ni.get('s') == '컴퓨터에서 고침', f'⑤ 컴퓨터 넘버링 수정이 휴대폰에 {ni}')
        cb = await getv(ph, 'cbm.IMPL'); ok(cb is not None and set(cb) == {'A2', 'A3'}, f'⑤ 휴대폰 ★ 그대로(지운 A1 안 살아남) {cb}')
        # ⑥ 토큰이 백업·Gist에 없음
        dump = await dk.evaluate("JBLSYNC.backup()")
        ok(TOK not in dump and 'jblsync' not in dump, '⑥ 백업 파일에 토큰 없음')
        ok(all(TOK not in v for v in G['g1']['files'].values()), '⑥ Gist 파일에 토큰 없음(조각은 gzip — 머리 파일 검사)')
        # ⑧ 공부 중(입력 뒤)에 받은 변경 = 알림만
        await setv(ph, 'cbm.IMPL', {'A2': 1000, 'A3': 1000, 'A9': 1}); await ph.evaluate("JBLSYNC.tick({pull:false})"); await settle(ph, 500)
        await dk.mouse.click(600, 400); await dk.wait_for_timeout(200)
        await dk.evaluate("JBLSYNC.vis(Date.now()-60000);JBLSYNC.tick({})"); await settle(dk, 500)
        cb = await getv(dk, 'cbm.IMPL'); pend = await dk.evaluate("JBLSYNC.pend()")
        ok(cb is not None and 'A9' not in cb and pend, f'⑧ 공부 중엔 바로 덮지 않고 대기 {cb} pend={pend}')
        async with dk.expect_navigation(timeout=15000): await dk.evaluate("JBLSYNC.applyNow()")
        await settle(dk)
        cb = await getv(dk, 'cbm.IMPL'); ok(cb is not None and 'A9' in cb, f'⑧ [지금 반영] 뒤 들어옴 {cb}')
        # 💾 창 UI
        await dk.evaluate("JBLSYNC.box()"); await dk.wait_for_timeout(300)
        t = await dk.inner_text('#syncbox'); ok('켜짐' in t and '아이폰' in t, f'💾 창 동기화 칸 {t[:120]!r}')
        await dk.screenshot(path=J.TMP + '/ux_sync_desk.png')
        # ⑦ 틀린 토큰
        e3 = await b.new_context(viewport={'width': 1280, 'height': 900}); await e3.route('https://api.github.com/**', gh); x = await e3.new_page(); x.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await x.goto(U + '#/'); await x.wait_for_timeout(1000); await x.evaluate("JBLSYNC.connect('ghp_WRONGTOKEN0123456789abcdefXYZ')"); await x.wait_for_timeout(800)
        ok(await x.evaluate("JBLSYNC.state()===null"), '⑦ 틀린 토큰 = 연결 안 됨')
        ok(not errs, f'페이지 오류 0 {errs[:3]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
