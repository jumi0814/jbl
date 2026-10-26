"""기기 동기화 회귀 공통 — 가짜 GitHub Gist API(page.route) + 두 창 도우미. ux_sync_all.py·ux_sync_real.py가 씀(ux_sync.py·ux_sync_num.py는 같은 내용을 안에 둠).
목록 since·updated_at·내용 없는 목록·POST·PATCH(파일 지움 null)·DELETE·토큰 검사 — 실제 GitHub과 같은 꼴.
10-26 실제처럼(REAL): 1MB(바이트) 넘는 파일은 잘라 주고 truncated·raw_url(gist.githubusercontent.com — 따로 받음) · 크기만큼 늦게 응답 · FAIL[묶음] = 그 묶음 받기를 n번 502로 · gist_all(기기) = 그 기기 모든 묶음"""
import json, datetime, base64, gzip
TOK = 'ghp_TESTTOKEN0123456789abcdefABCDEF'; NS = 'jblhub.v1.'
G = {}; CLK = [0]; LOG = []; REAL = [False]; FAIL = {}; FAILTAG = ['ph']; RAW = []
CORS = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Authorization, Content-Type, Accept', 'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS', 'Content-Type': 'application/json'}
def now_iso():
    CLK[0] += 1; return (datetime.datetime(2026, 10, 25) + datetime.timedelta(seconds=CLK[0])).strftime('%Y-%m-%dT%H:%M:%SZ')
async def raw(route):   # 잘린 파일 따로 받기(실제 gist.githubusercontent.com — CORS 열림)
    gid, name = route.request.url.split('/raw/', 1)[0].rsplit('/', 1)[1], route.request.url.split('/raw/', 1)[1]
    RAW.append(name)
    if gid not in G or name not in G[gid]['files']: return await route.fulfill(status=404, headers=CORS, body='')
    await route.fulfill(status=200, headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'text/plain; charset=utf-8'}, body=G[gid]['files'][name])
async def gh(route, tag=''):
    rq = route.request; m = rq.method; path = rq.url.split('api.github.com', 1)[1]
    if m == 'OPTIONS': return await route.fulfill(status=204, headers=CORS)
    LOG.append((m, path.split('?')[0], len(rq.post_data or ''), tag))
    if REAL[0]:
        import asyncio as _a; await _a.sleep(min(2.5, 0.05 + len(rq.post_data or '') / 2e6))
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
    if m == 'GET':
        d = G[gid]['description']
        for g, n in list(FAIL.items()):
            if n > 0 and (' · %s · ' % g) in d and tag in FAILTAG: FAIL[g] = n - 1; return await route.fulfill(status=502, headers=CORS, body='{"message":"Server Error"}')
        def one(k, v):
            if REAL[0] and len(v.encode('utf-8')) > 1000000: return {'content': v.encode('utf-8')[:1000000].decode('utf-8', 'ignore'), 'truncated': True, 'raw_url': 'https://gist.githubusercontent.com/u/%s/raw/%s' % (gid, k)}
            return {'content': v, 'truncated': False, 'raw_url': 'https://gist.githubusercontent.com/u/%s/raw/%s' % (gid, k)}
        body = json.dumps({'id': gid, 'updated_at': G[gid]['updated_at'], 'files': {k: one(k, v) for k, v in G[gid]['files'].items()}})
        if REAL[0]:
            import asyncio as _a; await _a.sleep(min(2.5, 0.05 + len(body) / 4e6))
        return await route.fulfill(status=200, headers=CORS, body=body)
    if m == 'PATCH':
        b = json.loads(rq.post_data)
        if 'description' in b: G[gid]['description'] = b['description']
        for k, v in b.get('files', {}).items():
            if v is None: G[gid]['files'].pop(k, None)
            else: G[gid]['files'][k] = v['content']
        G[gid]['updated_at'] = now_iso()
        return await route.fulfill(status=200, headers=CORS, body=json.dumps({'id': gid}))
    if m == 'DELETE': G.pop(gid, None); return await route.fulfill(status=204, headers=CORS)
    await route.fulfill(status=400, headers=CORS, body='{}')
def gist_data(dev, g):   # 그 기기·묶음 Gist 내용(NS 붙은 키 → 값 글)
    for v in G.values():
        if (' · %s · %s · ' % (dev, g)) not in v['description']: continue
        try:
            h = json.loads(v['files']['head.json']); txt = ''.join(v['files']['data.%d.part' % i] for i in range(h['n']))
            return json.loads(gzip.decompress(base64.b64decode(txt)).decode('utf-8') if h.get('enc') == 'gz64' else txt)
        except Exception as e: return {'__err': str(e)}
    return {}
def gist_all(dev):   # 그 기기의 모든 묶음을 합친 것(v3 = 넘버링은 N<과목><조각> 묶음)
    o = {}
    for v in G.values():
        if (' · %s · ' % dev) not in v['description']: continue
        g = v['description'].split(' · ')[2]; o.update(gist_data(dev, g))
    return o
async def getv(pg, k): return await pg.evaluate("k=>{const v=JBLSYNC.get(k);try{return v==null?null:JSON.parse(v)}catch(e){return v}}", k)
async def settle(pg, ms=400):
    for _ in range(80):
        await pg.wait_for_timeout(150)
        try:
            if not await pg.evaluate("JBLSYNC.busy()"): break
        except Exception: pass
    await pg.wait_for_timeout(ms)
async def tick(pg, o='{}'): await pg.evaluate(f"JBLSYNC.tick({o})"); await settle(pg)
async def poll(pg, js, sec):   # js가 참이 될 때까지 최대 sec초 — 걸린 초(못 되면 None)
    for i in range(int(sec * 2)):
        try:
            if await pg.evaluate(js): return i / 2
        except Exception: pass
        await pg.wait_for_timeout(500)
    return None
async def two(p, U):   # 컴퓨터(1280) · 아이폰(393 터치) 두 창 — 저장소 비우고 허브 홈
    dc = await p.chromium.launch(); b = dc
    d = await b.new_context(viewport={'width': 1280, 'height': 900})
    m = await b.new_context(viewport={'width': 393, 'height': 852}, is_mobile=True, has_touch=True, user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')
    await d.route('https://api.github.com/**', lambda r: gh(r, 'dk')); await m.route('https://api.github.com/**', lambda r: gh(r, 'ph'))
    for c in (d, m): await c.route('https://gist.githubusercontent.com/**', raw)
    dk = await d.new_page(); ph = await m.new_page()
    for pg in (dk, ph):
        await pg.goto(U + '#/'); await pg.wait_for_timeout(1500); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(1500)
    return b, dk, ph
async def connect(dk, ph):   # 컴퓨터 = 기준(토큰) → 휴대폰 = 연결 코드 → 양쪽 기기 id
    await dk.evaluate(f"JBLSYNC.connect('{TOK}')"); await settle(dk)
    code = await dk.evaluate("JBLSYNC.code()")
    try:
        async with ph.expect_navigation(timeout=20000, wait_until='load'): await ph.evaluate(f"JBLSYNC.connect('{code}')")
    except Exception: pass
    await ph.wait_for_timeout(3500); await settle(ph)
    return [await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.devId'))") for pg in (dk, ph)]
