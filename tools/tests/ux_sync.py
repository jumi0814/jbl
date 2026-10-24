"""10-24 기기 자동 동기화 v2 회귀(사용자 '모바일·컴퓨터 넘버링·★ 카드·★ 문제 연동 · 합칠 땐 컴퓨터 기준' + '꼭 데이터가 날라가지 않게 · 실시간 · 가장 최근 기록 · 덮어씌우지 않고 누락 없게').
GitHub Gist API를 가짜 서버(page.route — 목록 since·updated_at·내용 없는 목록·PATCH/POST)로 흉내 내고 컴퓨터(1280)·휴대폰(393 터치) 두 창:
 ① 컴퓨터 연결 = 기준 · 과목별 Gist ② 휴대폰 연결 = 컴퓨터 기준 첫 합치기(★ 카드 합집합 · 넘버링 = 컴퓨터 것 · 메모 둘 다 · 휴대폰 플래시카드 유지 · 공부 시간 기기별 · 합치기 전 자동 백업)
 ③ 컴퓨터가 휴대폰 기록을 새로고침 없이 반영 ④ 화면 메모리의 옛 채점이 새로 받은 ★ 문제를 덮지 않음(JB 카드 ★ 누른 뒤에도 둘 다)
 ⑤ 지운 ★ 전파 ⑥ 두 기기가 같은 때 고친 ★ 카드 = 둘 다 남음 ⑦ 같은 넘버링 문제를 둘 다 고침 = 더 최근 것
 ⑧ 바뀐 과목 묶음만 보냄 · 바뀐 게 없으면 목록 1번만(내용 받기 0) ⑨ 토큰이 백업·Gist에 없음 ⑩ 틀린 토큰 ⑪ 끊으면 더는 안 보냄 · 페이지 오류 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []; TOK = 'ghp_TESTTOKEN0123456789abcdefABCDEF'; NS = 'jblhub.v1.'
G = {}; CLK = [0]; LOG = []   # 가짜 Gist {id: {description, files, updated_at}} · 서버 시계 · 요청 기록
def now_iso():
    CLK[0] += 1; return (datetime.datetime(2026, 10, 24) + datetime.timedelta(seconds=CLK[0])).strftime('%Y-%m-%dT%H:%M:%SZ')
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CORS = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Authorization, Content-Type, Accept', 'Access-Control-Allow-Methods': 'GET, POST, PATCH, OPTIONS', 'Content-Type': 'application/json'}
async def gh(route):
    rq = route.request; m = rq.method; path = rq.url.split('api.github.com', 1)[1]
    if m == 'OPTIONS': return await route.fulfill(status=204, headers=CORS)
    LOG.append((m, path.split('?')[0], len(rq.post_data or '')))
    if (rq.headers.get('authorization') or '') != 'Bearer ' + TOK: return await route.fulfill(status=401, headers=CORS, body='{"message":"Bad credentials"}')
    if m == 'GET' and path.startswith('/gists?'):
        q = dict(x.split('=', 1) for x in path.split('?', 1)[1].split('&')); since = q.get('since', '').replace('%3A', ':')
        L = [{'id': k, 'description': v['description'], 'updated_at': v['updated_at'], 'files': {f: {'filename': f, 'size': len(c)} for f, c in v['files'].items()}} for k, v in G.items() if not since or v['updated_at'] >= since]
        L.sort(key=lambda x: x['updated_at'], reverse=True); pp = int(q.get('per_page', 30)); pg = int(q.get('page', 1))
        return await route.fulfill(status=200, headers=CORS, body=json.dumps(L[(pg - 1) * pp: pg * pp]))
    if m == 'POST' and path == '/gists':
        b = json.loads(rq.post_data); gid = 'g%d' % (len(G) + 1)
        G[gid] = {'description': b['description'], 'files': {k: v['content'] for k, v in b['files'].items() if v}, 'updated_at': now_iso()}
        return await route.fulfill(status=201, headers=CORS, body=json.dumps({'id': gid}))
    gid = path.split('/')[2].split('?')[0] if path.startswith('/gists/') else ''
    if gid not in G: return await route.fulfill(status=404, headers=CORS, body='{}')
    if m == 'GET': return await route.fulfill(status=200, headers=CORS, body=json.dumps({'id': gid, 'updated_at': G[gid]['updated_at'], 'files': {k: {'content': v, 'truncated': False, 'raw_url': ''} for k, v in G[gid]['files'].items()}}))
    if m == 'PATCH':
        b = json.loads(rq.post_data)
        if 'description' in b: G[gid]['description'] = b['description']
        for k, v in b.get('files', {}).items():
            if v is None: G[gid]['files'].pop(k, None)
            else: G[gid]['files'][k] = v['content']
        G[gid]['updated_at'] = now_iso()
        return await route.fulfill(status=200, headers=CORS, body=json.dumps({'id': gid}))
    await route.fulfill(status=400, headers=CORS, body='{}')
async def setv(pg, k, v): await pg.evaluate("([k,v])=>localStorage.setItem(k,v)", [NS + k, v if isinstance(v, str) else json.dumps(v)])
async def getv(pg, k): return await pg.evaluate("k=>{const v=JBLSYNC.get(k);try{return v==null?null:JSON.parse(v)}catch(e){return v}}", k)
async def settle(pg, ms=400):
    for _ in range(80):
        await pg.wait_for_timeout(150)
        try:
            if not await pg.evaluate("JBLSYNC.busy()"): break
        except Exception: pass
    await pg.wait_for_timeout(ms)
async def tick(pg, o='{}'): await pg.evaluate(f"JBLSYNC.tick({o})"); await settle(pg)
async def idb_whys(pg):
    return await pg.evaluate("""()=>new Promise(r=>{const q=indexedDB.open('jblhub-bak');q.onsuccess=()=>{try{const t=q.result.transaction('meta','readonly').objectStore('meta').getAll();t.onsuccess=()=>r(t.result.map(x=>x.why||''));t.onerror=()=>r([]);}catch(e){r([])}};q.onerror=()=>r([]);})""")
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
        T0 = {'2026-10-24': {'IMPL|PART': 600000}}
        await setv(dk, 'cbm.IMPL', {'A1': 1000, 'A2': 1000}); await setv(dk, 'num.i.IMPL.n1', {'u': 1000, 's': '컴퓨터 스토리'}); await setv(dk, 'lbm.CONS', {'X': 1000})
        await setv(dk, 'memo.IMPL.PART', json.dumps('컴퓨터 메모')); await setv(dk, 'time', T0)
        await setv(ph, 'cbm.IMPL', {'A3': 1000}); await setv(ph, 'num.i.IMPL.n1', {'u': 5000, 's': '휴대폰 스토리(더 최근)'}); await setv(ph, 'memo.IMPL.PART', json.dumps('휴대폰 메모')); await setv(ph, 'fc.IMPL', {'k1': {'s': 'o', 't': 1}})
        for pg in (dk, ph): await pg.reload(); await pg.wait_for_timeout(1500)
        dev_d = await dk.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.devId'))")
        # ① 컴퓨터 연결
        await dk.evaluate(f"JBLSYNC.connect('{TOK}')"); await settle(dk)
        descs = sorted(v['description'] for v in G.values())
        ok(any(' · IMPL · ' in d and d.endswith(' · 기준') for d in descs) and any(' · CONS · ' in d for d in descs) and any(' · T · ' in d for d in descs), f'① 컴퓨터 = 기준 · 과목별 Gist(IMPL·CONS·T) {len(G)}개')
        # ② 휴대폰 연결 — 컴퓨터 기준 첫 합치기(새로고침 1번)
        code = await dk.evaluate("JBLSYNC.code()")
        async with ph.expect_navigation(timeout=20000, wait_until='load'): await ph.evaluate(f"JBLSYNC.connect('{code}')")
        await ph.wait_for_timeout(2000); await settle(ph)
        cb = await getv(ph, 'cbm.IMPL'); ni = await getv(ph, 'num.i.IMPL.n1'); mm = await getv(ph, 'memo.IMPL.PART')
        ok(cb is not None and set(cb) == {'A1', 'A2', 'A3'}, f'② ★ 카드 = 컴퓨터 + 휴대폰에만 있던 것 {cb}')
        ok(ni is not None and ni.get('s') == '컴퓨터 스토리', f'② 넘버링 = 컴퓨터 기준 {ni}')
        ok(isinstance(mm, str) and '컴퓨터 메모' in mm and '휴대폰 메모' in mm, f'② 메모 = 둘 다 남음 {mm!r}')
        ok((await getv(ph, 'fc.IMPL') or {}).get('k1'), '② 휴대폰 플래시카드 그대로')
        ok((await getv(ph, 'lbm.CONS') or {}).get('X') == 1000, '② 다른 과목(CONS) 북마크도 받음')
        td = await getv(ph, 'timeDev') or {}
        ok(dev_d in td and td[dev_d].get('time', {}).get('2026-10-24'), f'② 컴퓨터 공부 시간 = 기기별로 받음 {list(td)}')
        ok('동기화 반영 전' in await idb_whys(ph), '② 첫 합치기 전 자동 백업(동기화 반영 전)')
        # ③ 컴퓨터가 휴대폰 기록을 새로고침 없이
        await dk.goto(U + '#/IMPL/PART/jb'); await dk.wait_for_timeout(1500); await settle(dk); await dk.evaluate("window.__keep=1")
        await tick(dk)
        cb = await getv(dk, 'cbm.IMPL'); ok(cb is not None and set(cb) == {'A1', 'A2', 'A3'}, f'③ 컴퓨터에도 휴대폰 ★ 카드 {cb}')
        ok(await dk.evaluate("window.__keep===1"), '③ 새로고침 없이 반영(실시간)')
        # ④ 화면 메모리의 옛 채점이 새로 받은 ★ 문제를 덮지 않음
        ids = await dk.evaluate("[...document.querySelectorAll('#stage .qc[data-id]')].map(e=>e.dataset.id).slice(0,2)")
        mk = await getv(ph, 'mk.IMPL') or {}; mk.setdefault('ok', {}); mk.setdefault('ng', {}); mk.setdefault('bm', {}); mk['bm'][ids[1]] = 1
        await setv(ph, 'mk.IMPL', mk); await tick(ph, '{pull:false,force:true}')
        await tick(dk)
        await dk.click(f'#stage .qc[data-id="{ids[0]}"] .btn.mk.bm'); await dk.wait_for_timeout(300)
        bm = (await getv(dk, 'mk.IMPL') or {}).get('bm', {})
        ok(ids[0] in bm and ids[1] in bm, f'④ 컴퓨터 ★ 누른 뒤에도 휴대폰 ★ 문제 남음 {list(bm)}')
        await tick(dk, '{pull:false,force:true}'); await tick(ph)
        bm = (await getv(ph, 'mk.IMPL') or {}).get('bm', {})
        ok(ids[0] in bm and ids[1] in bm, f'④ 휴대폰에도 둘 다 {list(bm)}')
        # ⑤ 지운 ★ 전파
        await setv(ph, 'cbm.IMPL', {'A2': 1000, 'A3': 1000}); await tick(ph, '{pull:false,force:true}'); await tick(dk)
        cb = await getv(dk, 'cbm.IMPL'); ok(cb is not None and set(cb) == {'A2', 'A3'}, f'⑤ 휴대폰에서 지운 ★가 컴퓨터에서도 지워짐 {cb}')
        await tick(dk, '{pull:false,force:true}'); await tick(ph)
        cb = await getv(ph, 'cbm.IMPL'); ok(cb is not None and set(cb) == {'A2', 'A3'}, f'⑤ 휴대폰에서 지운 ★ 안 살아남 {cb}')
        # ⑥ 같은 때 고친 ★ 카드 = 둘 다
        await setv(dk, 'cbm.IMPL', {'A2': 1000, 'A3': 1000, 'A7': 1}); await setv(ph, 'cbm.IMPL', {'A2': 1000, 'A3': 1000, 'A8': 1})
        await tick(dk, '{pull:false,force:true}'); await tick(ph, '{force:true}'); await tick(dk); await tick(dk, '{pull:false,force:true}'); await tick(ph)
        c1 = set(await getv(dk, 'cbm.IMPL') or {}); c2 = set(await getv(ph, 'cbm.IMPL') or {})
        ok({'A7', 'A8'} <= c1 and {'A7', 'A8'} <= c2, f'⑥ 같은 때 고친 ★ 둘 다 남음 컴퓨터 {sorted(c1)} 휴대폰 {sorted(c2)}')
        # ⑦ 같은 넘버링 문제를 둘 다 고침 → 더 최근 것
        await setv(dk, 'num.i.IMPL.n1', {'u': 9000, 's': '컴퓨터 수정'}); await setv(ph, 'num.i.IMPL.n1', {'u': 9500, 's': '휴대폰 수정(더 최근)'})
        await dk.reload(); await ph.reload(); await dk.wait_for_timeout(1500); await ph.wait_for_timeout(1500); await settle(dk); await settle(ph)
        await tick(dk, '{pull:false,force:true}'); await tick(ph, '{force:true}'); await tick(dk); await tick(dk, '{pull:false,force:true}'); await tick(ph)
        a = (await getv(dk, 'num.i.IMPL.n1') or {}).get('s'); c = (await getv(ph, 'num.i.IMPL.n1') or {}).get('s')
        ok(a == c == '휴대폰 수정(더 최근)', f'⑦ 넘버링 = 가장 최근 수정 컴퓨터 {a!r} 휴대폰 {c!r}')
        # ⑧ 바뀐 과목만 · 바뀐 게 없으면 목록만
        await tick(dk, '{pull:false,force:true}'); await tick(ph); LOG.clear()
        await setv(dk, 'cbm.IMPL', {'A2': 1000, 'A3': 1000, 'A7': 1, 'A8': 1, 'A9': 1}); await tick(dk, '{pull:false}')
        pat = [x for x in LOG if x[0] == 'PATCH']; ok(len(pat) == 1, f'⑧ 바뀐 묶음(IMPL)만 보냄 PATCH {len(pat)}')
        await tick(ph, '{push:false}'); LOG.clear(); await tick(ph, '{push:false}')
        ok([x[0] for x in LOG] == ['GET'] and LOG[0][1] == '/gists', f'⑧ 바뀐 게 없으면 목록 1번만 {LOG}')
        ok('A9' in (await getv(ph, 'cbm.IMPL') or {}), '⑧ 바뀐 묶음은 받음')
        # ⑨ 토큰 없음
        dump = await dk.evaluate("JBLSYNC.backup()"); ok(TOK not in dump and 'jblsync' not in dump, '⑨ 백업 파일에 토큰 없음')
        ok(all(TOK not in v['description'] and all(TOK not in c for c in v['files'].values()) for v in G.values()), '⑨ Gist에 토큰 없음')
        # ⑩ 틀린 토큰
        e3 = await b.new_context(viewport={'width': 1280, 'height': 900}); await e3.route('https://api.github.com/**', gh); x = await e3.new_page(); x.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await x.goto(U + '#/'); await x.wait_for_timeout(1000); await x.evaluate("JBLSYNC.connect('ghp_WRONGTOKEN0123456789abcdefXYZ')"); await x.wait_for_timeout(800)
        ok(await x.evaluate("JBLSYNC.state()===null"), '⑩ 틀린 토큰 = 연결 안 됨')
        # 💾 창
        await dk.evaluate("JBLSYNC.box()"); await dk.wait_for_timeout(300); t = await dk.inner_text('#syncbox')
        ok('켜짐' in t and '아이폰' in t, f'💾 창 동기화 칸 {t[:100]!r}'); await dk.screenshot(path=J.TMP + '/ux_sync_desk.png')
        # ⑪ 끊기
        dk.on('dialog', lambda d: asyncio.ensure_future(d.accept())); await dk.click('#syncoff'); await dk.wait_for_timeout(300); LOG.clear()
        await setv(dk, 'cbm.IMPL', {'Z': 1}); await dk.evaluate("JBLSYNC.tick({})"); await dk.wait_for_timeout(500)
        ok(await dk.evaluate("JBLSYNC.state()===null") and not LOG, f'⑪ 끊으면 더는 안 보냄 {LOG}')
        ok(not errs, f'페이지 오류 0 {errs[:3]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
