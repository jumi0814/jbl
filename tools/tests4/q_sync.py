"""11-04 쿼터마다 기기 동기화가 실제로 됨 — 컴퓨터 연결(그 쿼터 이름의 Gist) → 휴대폰이 연결 코드로 붙음 → 첫 합치기 뒤 새로고침 →
★ 카드 = 둘의 합집합 · 휴대폰이 컴퓨터 메모를 받음. 3Q·4Q 미리 보기 사이트 각각 따로 띄운 두 창(같은 쿼터끼리)으로.
(11-04 정체성 블록 Q가 syncPull 지역 배열 Q에 가려 받은 기록을 모두 버리던 것 — q_isolation은 '분리'만 봐서 못 잡음 → 이 시험)
GitHub API는 가짜(page.route — 목록·내용·POST·PATCH · 네트워크에 나가지 않음)."""
import json, datetime
from qsite import *
from playwright.sync_api import sync_playwright
TOK = 'ghp_TESTTOKEN0123456789abcdefABCDEF'
rel = build(); base = serve()
for q, r in rel.items():
    U = url(base, r); I = QS.QS[q]['ident']; N = I['ns']; G = {}; CLK = [0]; SJ = (QS.sids(q) or ['X'])[0]
    def now_iso():
        CLK[0] += 1; return (datetime.datetime(2026, 11, 4) + datetime.timedelta(seconds=CLK[0])).strftime('%Y-%m-%dT%H:%M:%SZ')
    def gh(route):
        rq = route.request; m = rq.method; path = rq.url.split('api.github.com', 1)[1]
        H = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Authorization, Content-Type, Accept', 'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS', 'Content-Type': 'application/json'}
        if m == 'OPTIONS': return route.fulfill(status=204, headers=H)
        if (rq.headers.get('authorization') or '') != 'Bearer ' + TOK: return route.fulfill(status=401, headers=H, body='{"message":"Bad credentials"}')
        if m == 'GET' and path.startswith('/gists?'):
            qq = dict(x.split('=', 1) for x in path.split('?', 1)[1].split('&')); since = qq.get('since', '').replace('%3A', ':')
            L = [{'id': k, 'description': v['description'], 'updated_at': v['updated_at'], 'files': {f: {'filename': f, 'size': len(c)} for f, c in v['files'].items()}} for k, v in G.items() if not since or v['updated_at'] >= since]
            L.sort(key=lambda x: x['updated_at'], reverse=True); pp = int(qq.get('per_page', 30)); pg = int(qq.get('page', 1))
            return route.fulfill(status=200, headers=H, body=json.dumps(L[(pg - 1) * pp: pg * pp]))
        if m == 'POST' and path == '/gists':
            b = json.loads(rq.post_data); gid = 'g%d' % (len(G) + 1)
            G[gid] = {'description': b['description'], 'files': {k: v['content'] for k, v in b['files'].items() if v}, 'updated_at': now_iso()}
            return route.fulfill(status=201, headers=H, body=json.dumps({'id': gid}))
        gid = path.split('/')[2].split('?')[0] if path.startswith('/gists/') else ''
        if gid not in G: return route.fulfill(status=404, headers=H, body='{}')
        if m == 'GET': return route.fulfill(status=200, headers=H, body=json.dumps({'id': gid, 'updated_at': G[gid]['updated_at'], 'files': {k: {'content': v, 'truncated': False, 'raw_url': ''} for k, v in G[gid]['files'].items()}}))
        if m == 'PATCH':
            b = json.loads(rq.post_data)
            if 'description' in b: G[gid]['description'] = b['description']
            for k, v in b.get('files', {}).items():
                if v is None: G[gid]['files'].pop(k, None)
                else: G[gid]['files'][k] = v['content']
            G[gid]['updated_at'] = now_iso(); return route.fulfill(status=200, headers=H, body=json.dumps({'id': gid}))
        if m == 'DELETE': G.pop(gid, None); return route.fulfill(status=204, headers=H)
        route.fulfill(status=400, headers=H, body='{}')
    def settle(pg, ms=400):
        for _ in range(80):
            pg.wait_for_timeout(150)
            try:
                if not pg.evaluate("JBLSYNC.busy()"): break
            except Exception: pass
        pg.wait_for_timeout(ms)
    with sync_playwright() as p:
        br = p.chromium.launch(); errs = []
        dc = br.new_context(viewport={'width': 1280, 'height': 900}); pc = br.new_context(viewport={'width': 393, 'height': 852}, is_mobile=True, has_touch=True)
        for c in (dc, pc): c.route('https://api.github.com/**', gh)
        dk = dc.new_page(); ph = pc.new_page()
        for pg in (dk, ph):
            pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.goto(U + '#/'); pg.wait_for_timeout(1500); pg.evaluate("localStorage.clear();sessionStorage.clear()")
        S = lambda pg, k, v: pg.evaluate("([k,v])=>localStorage.setItem(k,v)", [N + k, json.dumps(v)])
        S(dk, f'cbm.{SJ}', {'A1': 1000, 'A2': 1000}); S(dk, f'memo.{SJ}.L', '컴퓨터 메모'); S(ph, f'cbm.{SJ}', {'A3': 1000})
        for pg in (dk, ph): pg.reload(); pg.wait_for_timeout(2000)
        dk.evaluate(f"JBLSYNC.connect('{TOK}')"); settle(dk)
        ds = [v['description'] for v in G.values()]
        ok(len(G) >= 2 and all(d.startswith(I['gist'] + ' 동기화 v3 · ') for d in ds), f'{q} ① 컴퓨터 연결 — Gist {len(G)}개 · 설명 머리 «{I["gist"]} 동기화 v3» {ds[:2]}')
        code = dk.evaluate("JBLSYNC.code()")
        try:
            with ph.expect_navigation(timeout=30000, wait_until='load'): ph.evaluate(f"JBLSYNC.connect('{code}')")
            nav = True
        except Exception: nav = False
        ok(nav, f'{q} ② 휴대폰 연결 → 첫 합치기 뒤 새로고침')
        ph.wait_for_timeout(2500); settle(ph)
        G2 = lambda pg, k: pg.evaluate("k=>{const v=JBLSYNC.get(k);try{return v==null?null:JSON.parse(v)}catch(e){return v}}", k)
        cb = G2(ph, f'cbm.{SJ}') or {}; mm = G2(ph, f'memo.{SJ}.L')
        ok(set(cb) == {'A1', 'A2', 'A3'}, f'{q} ② 휴대폰 ★ 카드 = 컴퓨터 + 제 것 {sorted(cb)}')
        ok(isinstance(mm, str) and '컴퓨터 메모' in mm, f'{q} ② 휴대폰이 컴퓨터 메모를 받음 {mm!r}')
        dk.evaluate("JBLSYNC.tick({})"); settle(dk)
        cd = G2(dk, f'cbm.{SJ}') or {}
        ok(set(cd) == {'A1', 'A2', 'A3'}, f'{q} ③ 컴퓨터도 휴대폰 ★를 받음 {sorted(cd)}')
        ok(not errs, f'{q} 콘솔 오류 0 {errs[:2]}')
        br.close()
done()
