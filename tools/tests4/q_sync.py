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
    U = url(base, r); I = QS.QS[q]['ident']; N = I['ns']; G = {}; CLK = [0]; CNT = [0]; MODE = ['']; LOG = []; SJ = (QS.sids(q) or ['X'])[0]
    def now_iso():
        CLK[0] += 1; return (datetime.datetime(2026, 11, 4) + datetime.timedelta(seconds=CLK[0])).strftime('%Y-%m-%dT%H:%M:%SZ')
    def gh(route, tag=''):
        rq = route.request; m = rq.method; path = rq.url.split('api.github.com', 1)[1]
        H = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Authorization, Content-Type, Accept', 'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS', 'Content-Type': 'application/json'}
        if m == 'OPTIONS': return route.fulfill(status=204, headers=H)
        if (rq.headers.get('authorization') or '') != 'Bearer ' + TOK: return route.fulfill(status=401, headers=H, body='{"message":"Bad credentials"}')
        LOG.append((tag, m, path.split('?')[0]))
        if MODE[0] and MODE[0].split(':')[0] == tag:   # 11-11 E3 403 두 가지 — perm 토큰 권한 없음(한도 남음) · limit 요청 한도(남은 0 + 풀리는 시각)
            lim = MODE[0].endswith('limit'); X = dict(H, **{'Access-Control-Expose-Headers': 'Retry-After, X-RateLimit-Remaining, X-RateLimit-Reset', 'X-RateLimit-Remaining': '0' if lim else '4990', 'X-RateLimit-Reset': str(int(datetime.datetime.now().timestamp()) + 600)})
            return route.fulfill(status=403, headers=X, body=json.dumps({'message': 'API rate limit exceeded for user ID 1.' if lim else 'Resource not accessible by personal access token'}))
        if m == 'GET' and path.startswith('/gists?'):
            qq = dict(x.split('=', 1) for x in path.split('?', 1)[1].split('&')); since = qq.get('since', '').replace('%3A', ':')
            L = [{'id': k, 'description': v['description'], 'updated_at': v['updated_at'], 'files': {f: {'filename': f, 'size': len(c)} for f, c in v['files'].items()}} for k, v in G.items() if not since or v['updated_at'] >= since]
            L.sort(key=lambda x: x['updated_at'], reverse=True); pp = int(qq.get('per_page', 30)); pg = int(qq.get('page', 1))
            return route.fulfill(status=200, headers=H, body=json.dumps(L[(pg - 1) * pp: pg * pp]))
        if m == 'POST' or (m == 'PATCH' and ' · T · ' not in G.get(path.split('/')[2].split('?')[0], {}).get('description', ' · T · ')): CNT[0] += 1   # 쓰기 요청 수(공부 시간 묶음 T는 빼고)
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
        dc.route('https://api.github.com/**', lambda r_: gh(r_, 'dk')); pc.route('https://api.github.com/**', lambda r_: gh(r_, 'ph'))
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
        # ---- 11-11 C2 넘버링 복습 평가(num.r)의 지움·바꿈이 두 기기에서 같음 — 회차(s)마다 가장 최근 t · 지움 표시 {t,s,x:1}
        RK = f'num.r.{SJ}.X1'; T0 = 1794000000000
        def put(pg, v): pg.evaluate("([k,v])=>localStorage.setItem(k,JSON.stringify(v))", [N + RK, v])
        def both(force=True):
            for _ in range(2):
                for pg in (dk, ph): pg.evaluate("f=>JBLSYNC.tick(f?{force:true}:{})", force); settle(pg, 250)
        live = lambda r: [(e.get('s'), e.get('m')) for e in (r or {}).get('h', []) if not e.get('x')]
        put(dk, {'id': 'X1', 'h': [{'t': T0, 'm': 0, 's': 'sA'}], 'w': [], 'm': 0, 'd': T0, 'u': T0}); both()
        ok(live(G2(ph, RK)) == [('sA', 0)], f'{q} ④ 복습 평가(모름)가 휴대폰으로 {G2(ph, RK)}')
        put(ph, {'id': 'X1', 'h': [{'t': T0 + 1000, 's': 'sA', 'x': 1}], 'w': [], 'u': T0 + 1000}); both()   # 휴대폰에서 같은 평가를 다시 눌러 지움(새 판 markSet이 쓰는 꼴)
        rd, rp = G2(dk, RK), G2(ph, RK)
        ok(live(rd) == [] and live(rp) == [] and rd.get('m') is None and rp.get('m') is None, f'{q} ④ 지운 평가가 두 기기에서 지워진 채(옛: 컴퓨터 사본이 되살림) 컴퓨터 {rd.get("h")} m={rd.get("m")} · 휴대폰 {rp.get("h")}')
        put(dk, {'id': 'X1', 'h': rd['h'] + [{'t': T0 + 2000, 'm': 2, 's': 'sB'}], 'w': [], 'm': 2, 'd': T0 + 2000, 'u': T0 + 2000}); both()
        rp = G2(ph, RK); put(ph, {'id': 'X1', 'h': [e for e in rp['h'] if e.get('s') != 'sB'] + [{'t': T0 + 3000, 'm': 1, 's': 'sB'}], 'w': [], 'm': 1, 'd': T0 + 3000, 'u': T0 + 3000}); both()   # 휴대폰에서 같은 회차 평가를 바꿈
        rd, rp = G2(dk, RK), G2(ph, RK)
        ok(live(rd) == [('sB', 1)] and live(rp) == [('sB', 1)] and rd.get('m') == 1 and rp.get('m') == 1 and len(rd['h']) == 2, f'{q} ④ 바꾼 평가 = 회차마다 한 줄(옛: 두 줄 다 남음) 컴퓨터 {rd.get("h")} · 휴대폰 {rp.get("h")}')
        # 옛 판 기기가 섞임(지움 표시를 모름): ㉠ 옛 판의 합집합 결과(옛 평가 + 지움 표시 · m 없음) ㉡ 화면 메모리의 옛 판으로 덮어씀(지움 표시 없이 옛 평가만) → 새 판 기기의 기록이 깨지지 않고 지운 것이 되살아나지 않음
        put(ph, {'id': 'X1', 'h': [{'t': T0, 'm': 0, 's': 'sA'}, {'t': T0 + 1000, 's': 'sA', 'x': 1}, {'t': T0 + 2000, 'm': 2, 's': 'sB'}, {'t': T0 + 3000, 'm': 1, 's': 'sB'}], 'w': [], 'd': T0 + 3000, 'u': T0 + 4000}); both()
        rd = G2(dk, RK); ok(live(rd) == [('sB', 1)] and rd.get('m') == 1 and len(rd['h']) == 2, f'{q} ⑤ 옛 판의 합집합(옛 줄 + 지움 표시)을 받아도 컴퓨터는 그대로 {rd.get("h")} m={rd.get("m")}')
        put(ph, {'id': 'X1', 'h': [{'t': T0, 'm': 0, 's': 'sA'}], 'w': [], 'm': 0, 'd': T0, 'u': T0 + 5000}); both()
        rd = G2(dk, RK); ok(live(rd) == [('sB', 1)] and rd.get('m') == 1, f'{q} ⑤ 옛 판이 옛 평가만 다시 써도 컴퓨터에서 지운 것이 되살아나지 않음 {rd.get("h")}')
        both(False); n0 = CNT[0]; both(False); both(False); ok(CNT[0] == n0, f'{q} ⑤ 그 뒤 두 기기가 번갈아 올리지 않음(쓰기 요청 +{CNT[0] - n0})')
        # 옛 판이 지움 표시 줄을 읽어도 깨지지 않는 꼴인지: m이 없는 줄(옛 판 화면 = '—' · 최근 평가·지난 평가에 안 걸림) · t·s는 그대로
        ok(all(('t' in e and 's' in e and 'm' not in e) for e in rd['h'] if e.get('x')), f'{q} ⑤ 지움 표시 줄 = {{t,s,x}}(m 없음)')
        # ---- 11-11 E3 GitHub 403: 토큰 권한 없음 = 되풀이하지 않음(다시 연결·[지금 동기화] 때만) · 요청 한도 = 풀리는 때까지 쉼
        cnt = lambda tag: len([x for x in LOG if x[0] == tag])
        MODE[0] = 'dk:perm'; dk.evaluate("JBLSYNC.tick({})"); settle(dk); e = dk.evaluate("JBLSYNC.err()")
        ok('Gist 권한이 없어요' in e and '한도' not in e, f'{q} ⑥ 403(한도 남음) = 토큰 권한 없음 {e!r}')
        n1 = cnt('dk')
        for _ in range(4): dk.evaluate("JBLSYNC.tick({})"); settle(dk, 100)
        dk.wait_for_timeout(1500); ok(cnt('dk') == n1, f'{q} ⑥ 권한 없음은 되풀이 0(요청 +{cnt("dk") - n1})')
        MODE[0] = ''; dk.evaluate("JBLSYNC.tick({tnow:true})"); settle(dk); ok(dk.evaluate("JBLSYNC.err()") == '' and cnt('dk') > n1, f'{q} ⑥ [지금 동기화]로는 다시 해 봄 → 풀림 {dk.evaluate("JBLSYNC.err()")!r}')
        dk.evaluate("JBLSYNC.tick({})"); settle(dk, 100); ok(dk.evaluate("JBLSYNC.err()") == '', f'{q} ⑥ 그 뒤 보통 동기화')
        MODE[0] = 'ph:limit'; ph.evaluate("JBLSYNC.tick({})"); settle(ph); e = ph.evaluate("JBLSYNC.err()"); n2 = cnt('ph')
        import re as _re
        ok('요청 한도' in e and _re.search(r'\d\d:\d\d쯤 다시', e) is not None and '권한' not in e, f'{q} ⑥ 403(남은 0) = 요청 한도 + 언제 다시 {e!r}')
        MODE[0] = ''
        for _ in range(3): ph.evaluate("JBLSYNC.tick({})"); settle(ph, 100)
        ok(cnt('ph') == n2, f'{q} ⑥ 한도가 풀리는 때까지 쉼(요청 +{cnt("ph") - n2} · 옛: 1분마다 다시)')
        ok(not errs, f'{q} 콘솔 오류 0 {errs[:2]}')
        br.close()
done()
