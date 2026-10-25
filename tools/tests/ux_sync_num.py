"""10-25 넘버링 기기 동기화 회귀(사용자 '넘버링이 컴퓨터랑 휴대폰이랑 전혀 연동이 안 돼').
ux_sync.py의 가짜 GitHub Gist 서버(page.route)와 두 창(컴퓨터 1280 · 아이폰 393 터치)을 그대로 쓰되, 값을 localStorage에 직접 넣지 않고 실제 화면으로:
 ⓪ 연결 전 — 컴퓨터·휴대폰이 JB 카드 '✎ 넘버링'으로 문제를 하나씩 넣고 스토리를 씀 → 컴퓨터 연결(기준) → 휴대폰 연결(연결 코드)
    = 휴대폰에 컴퓨터 문제·스토리 + 휴대폰에만 있던 문제도 남음 · 컴퓨터가 새로고침 없이 휴대폰 문제를 받음
 ⓐ 컴퓨터: JB '✎ 넘버링'으로 2문제 더 넣고 스토리 입력 → (2.5~12초 뒤 저절로 보냄) → 휴대폰: 내 넘버링을 연 채(새로고침 없이) 받음(15초 확인 · 화면 DOM) · 새로고침 뒤에도
 ⓑ 휴대폰: 스토리 고치기 + 문제 하나 넣기 → 컴퓨터: 내 넘버링을 연 채 새로고침 없이 화면에
 ⓒ 넘버링 복습: 컴퓨터가 복습 화면을 연 채 · 휴대폰이 '모름' 평가 → 회차 정리 → 새 회차(num.rl) → 컴퓨터 복습 화면에 '지난 모름'·'이력 1'(새로고침 없이) · 복습 이력 창 회차 · 새로고침 뒤에도
 ⓔ 휴대폰에서 같은 스토리를 6번 이어서 고침(스토리를 1~2분 쓰는 동안 12~15초마다 오가는 모습) → 컴퓨터가 매번·마지막 글까지 받음
    (10-25 발견: syncApplyGrp의 되풀이 막기 SYNC.flip이 '3분에 4번'을 넘으면 그 키를 건너뛰고 묶음은 받은 것으로 적어, 마지막 글이 영영 안 옴)
 ⓖ 10-25c 진행 중인 회차(num.rs)도 실시간 — 휴대폰 회차 중 평가 → 컴퓨터 복습 화면에 같은 회차·평가(새로고침 없이) · 내 답안(낙서장)은 저장·전송 안 됨
 ⓕ 컴퓨터 넘버링을 기기 저장소(IndexedDB · xsMove)로 옮긴 뒤에도 양쪽으로 주고받음
 ⓓ 컴퓨터 데이터 안전 — 컴퓨터 넘버링 문제 수는 한 번도 줄지 않음 · 마지막에 양쪽 같은 문제 수 · 페이지 오류 0
실행: JBL_HTTP=1 .venv/bin/python tools/tests/ux_sync_num.py"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime, base64, gzip
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []; TOK = 'ghp_TESTTOKEN0123456789abcdefABCDEF'; NS = 'jblhub.v1.'; SJ = 'IMPL'
G = {}; CLK = [0]; LOG = []   # 가짜 Gist {id: {description, files, updated_at}} · 서버 시계 · 요청 기록
def now_iso():
    CLK[0] += 1; return (datetime.datetime(2026, 10, 25) + datetime.timedelta(seconds=CLK[0])).strftime('%Y-%m-%dT%H:%M:%SZ')
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m, flush=True)
    if not c: fails.append(m)
    return c
CORS = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Authorization, Content-Type, Accept', 'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS', 'Content-Type': 'application/json'}
async def gh(route, tag=''):   # ux_sync.py와 같은 가짜 Gist API
    rq = route.request; m = rq.method; path = rq.url.split('api.github.com', 1)[1]
    if m == 'OPTIONS': return await route.fulfill(status=204, headers=CORS)
    LOG.append((m, path.split('?')[0], len(rq.post_data or ''), tag))
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
    if m == 'DELETE': G.pop(gid, None); return await route.fulfill(status=204, headers=CORS)
    await route.fulfill(status=400, headers=CORS, body='{}')
def gist_data(dev, g):   # 그 기기·묶음 Gist의 내용(NS 붙은 키 → 값 글) — 없으면 {}
    for v in G.values():
        if (' · %s · %s · ' % (dev, g)) not in v['description']: continue
        try:
            h = json.loads(v['files']['head.json']); txt = ''.join(v['files']['data.%d.part' % i] for i in range(h['n']))
            raw = gzip.decompress(base64.b64decode(txt)).decode('utf-8') if h.get('enc') == 'gz64' else txt
            return json.loads(raw)
        except Exception as e: return {'__err': str(e)}
    return {}
async def getv(pg, k): return await pg.evaluate("k=>{const v=JBLSYNC.get(k);try{return v==null?null:JSON.parse(v)}catch(e){return v}}", k)
async def settle(pg, ms=400):
    for _ in range(80):
        await pg.wait_for_timeout(150)
        try:
            if not await pg.evaluate("JBLSYNC.busy()"): break
        except Exception: pass
    await pg.wait_for_timeout(ms)
async def tick(pg, o='{}'): await pg.evaluate(f"JBLSYNC.tick({o})"); await settle(pg)
async def nmgo(pg, i):   # 실제 화면: 그 과목 JB 문제 → i번째 카드의 '✎ 넘버링'(없으면 넣고 그 문제로) → 넣은 넘버링 문제 id
    await pg.evaluate(f"location.hash='#/{SJ}/_jb'"); await pg.wait_for_timeout(2200)
    aid = await pg.evaluate(f"(()=>{{const c=document.querySelectorAll('#stage article.qc')[{i}];c.scrollIntoView({{block:'center'}});return c.dataset.aid}})()")
    await pg.evaluate(f"document.querySelectorAll('#stage article.qc')[{i}].querySelector('.nmgo').click()"); await pg.wait_for_timeout(3000)
    iid = await pg.evaluate(f"(()=>{{const it=JBLNUM._S.items.find(x=>!x.del&&(x.src||[]).some(s=>s.t==='jb'&&s.id==={aid!r}));return it?it.id:null}})()")
    return aid, iid
async def story(pg, iid, text):   # 실제 편집기: 스토리 칸을 눌러 그 자리 편집 → 글 입력 → Esc(저장)
    sel = f'.nm-it[data-id="{iid}"] .nm-s .nm-c'
    await pg.evaluate("s=>document.querySelector(s).scrollIntoView({block:'center'})", sel); await pg.wait_for_timeout(250)
    await pg.locator(sel).click(); await pg.wait_for_timeout(300)
    if not await pg.evaluate("!!JBLNUM._S.ed"):
        await pg.locator(f'.nm-it[data-id="{iid}"] .nm-s [data-act=edit]').click(); await pg.wait_for_timeout(300)
    await pg.keyboard.press('End'); await pg.keyboard.type(text); await pg.wait_for_timeout(1000); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(700)
    return await pg.evaluate(f"(()=>{{const v=JBLSYNC.get('num.i.{SJ}.'+{iid!r});try{{return (JSON.parse(v)||{{}}).st||''}}catch(e){{return ''}}}})()")
DOM = """(()=>{const o={};document.querySelectorAll('#numv .nm-it[data-id]').forEach(a=>{const s=a.querySelector('.nm-s .nm-c');o[a.dataset.id]=s?s.textContent:''});return o})()"""
async def dom(pg):
    try: return await pg.evaluate(DOM)
    except Exception: return {}
async def nlive(pg):   # 이 기기 저장소의 살아 있는 넘버링 문제 수(localStorage + 기기 저장소 — 백업 파일과 같은 dumpAll)
    return await pg.evaluate(f"(()=>{{const d=JSON.parse(JBLSYNC.backup()).data;let n=0;for(const k in d){{if(k.indexOf('{NS}num.i.{SJ}.')!==0)continue;try{{if(!JSON.parse(d[k]).del)n++}}catch(e){{}}}}return n}})()")
async def poll(pg, js, sec):   # js(문자열 식)가 참이 될 때까지 최대 sec초 — 걸린 초(못 되면 None)
    for i in range(sec * 2):
        try:
            if await pg.evaluate(js): return i / 2
        except Exception: pass
        await pg.wait_for_timeout(500)
    return None
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        dc = await b.new_context(viewport={'width': 1280, 'height': 900}); pc = await b.new_context(viewport={'width': 393, 'height': 852}, is_mobile=True, has_touch=True,
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')
        await dc.route('https://api.github.com/**', lambda r: gh(r, 'dk')); await pc.route('https://api.github.com/**', lambda r: gh(r, 'ph'))
        dk = await dc.new_page(); ph = await pc.new_page(); errs = []
        for pg in (dk, ph): pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for pg in (dk, ph):
            await pg.goto(U + '#/'); await pg.wait_for_timeout(1500); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(1500)
        CNT = []   # 컴퓨터 넘버링 문제 수 기록(ⓓ)
        async def cnt(tag): CNT.append((tag, await nlive(dk)))
        # ⓪ 연결 전 — 양쪽에 실제 화면으로 문제·스토리
        _, D0 = await nmgo(dk, 0); s = await story(dk, D0, '컴퓨터처음스토리')
        ok(D0 and '컴퓨터처음스토리' in s, f'⓪ 컴퓨터: JB ✎ 넘버링 → {D0} · 스토리 저장 {s[:40]!r}')
        _, P0 = await nmgo(ph, 1); s = await story(ph, P0, '휴대폰처음스토리')
        ok(P0 and P0 != D0 and '휴대폰처음스토리' in s, f'⓪ 휴대폰: JB ✎ 넘버링 → {P0} · 스토리 저장 {s[:40]!r}')
        await cnt('연결 전')
        await dk.evaluate(f"JBLSYNC.connect('{TOK}')"); await settle(dk)
        dev_d = await dk.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.devId'))")
        gd = gist_data(dev_d, SJ)
        ok(NS + f'num.i.{SJ}.{D0}' in gd, f'⓪ 컴퓨터 연결 = {SJ} 묶음에 넘버링 문제가 실림 {sorted(k[len(NS):] for k in gd)[:6]}')
        code = await dk.evaluate("JBLSYNC.code()")
        try:
            async with ph.expect_navigation(timeout=20000, wait_until='load'): await ph.evaluate(f"JBLSYNC.connect('{code}')")
        except Exception: pass
        await ph.wait_for_timeout(3500); await settle(ph)
        dev_p = await ph.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.devId'))")
        if not (await ph.evaluate("location.hash")).startswith(f'#/_num/{SJ}'): await ph.evaluate(f"location.hash='#/_num/{SJ}'"); await ph.wait_for_timeout(3000)
        d = await dom(ph)
        ok(D0 in d and '컴퓨터처음스토리' in d.get(D0, ''), f'⓪ 휴대폰 화면: 컴퓨터 문제·스토리 받음 {list(d)}')
        ok(P0 in d and '휴대폰처음스토리' in d.get(P0, ''), f'⓪ 휴대폰 화면: 휴대폰에만 있던 문제·스토리 남음(첫 합치기) {list(d)}')
        await dk.evaluate(f"location.hash='#/_num/{SJ}'"); await dk.wait_for_timeout(2500); await dk.evaluate("window.__keep=1")
        await tick(dk)
        w = await poll(dk, f"!!document.querySelector('#numv .nm-it[data-id=\"{P0}\"]')", 3)
        d = await dom(dk)
        ok(w is not None and '휴대폰처음스토리' in d.get(P0, ''), f'⓪ 컴퓨터 화면(새로고침 없이): 휴대폰 문제·스토리 받음 {list(d)}')
        ok(await dk.evaluate("window.__keep===1"), '⓪ 컴퓨터 새로고침 없음')
        await cnt('첫 합치기 뒤')
        # ⓐ 컴퓨터에서 2문제 더 + 스토리 → 휴대폰(내 넘버링 연 채)
        await ph.evaluate("window.__keep=1")
        ok(await ph.evaluate(f"location.hash==='#/_num/{SJ}'&&!!document.getElementById('numv')"), 'ⓐ 휴대폰: 내 넘버링 화면을 열어 둠')
        _, D1 = await nmgo(dk, 2); _, D2 = await nmgo(dk, 3); s = await story(dk, D2, '컴퓨터새스토리A')
        ok(D1 and D2 and '컴퓨터새스토리A' in s, f'ⓐ 컴퓨터: 2문제 더({D1}, {D2}) · 스토리 저장')
        await cnt('ⓐ 넣은 뒤')
        t0 = None
        for i in range(40):   # 저절로 보냄(바뀌면 2.5초 뒤 · 최소 12초 간격) — 넘버링 화면을 연 채로
            gd = gist_data(dev_d, SJ); v = gd.get(NS + f'num.i.{SJ}.{D2}') or ''
            if NS + f'num.i.{SJ}.{D1}' in gd and '컴퓨터새스토리A' in v: t0 = i / 2; break
            await dk.wait_for_timeout(500)
        ok(t0 is not None, f'ⓐ 컴퓨터: 넘버링 화면을 연 채 저절로 보냄(디바운스) {t0}s · 오류 {await dk.evaluate("JBLSYNC.err()")!r}')
        if t0 is None: await tick(dk, '{pull:false}')
        t1 = await poll(ph, f"!!document.querySelector('#numv .nm-it[data-id=\"{D2}\"]')&&!!document.querySelector('#numv .nm-it[data-id=\"{D1}\"]')", 35)
        ok(t1 is not None, f'ⓐ 휴대폰: 15초 확인으로 저절로 받아 화면에 {t1}s · 오류 {await ph.evaluate("JBLSYNC.err()")!r}')
        if t1 is None: await tick(ph)
        d = await dom(ph)
        ok(D1 in d and D2 in d and '컴퓨터새스토리A' in d.get(D2, ''), f'ⓐ 휴대폰 화면(새로고침 없이): 새 2문제·스토리 {sorted(d)}')
        ok(await ph.evaluate("window.__keep===1"), 'ⓐ 휴대폰 새로고침 없음')
        await ph.reload(); await ph.wait_for_timeout(3500); await settle(ph)
        d = await dom(ph)
        ok(all(x in d for x in (D0, P0, D1, D2)) and '컴퓨터새스토리A' in d.get(D2, ''), f'ⓐ 휴대폰 새로고침 뒤에도 그대로 {sorted(d)}')
        # ⓑ 휴대폰에서 스토리 고치기 + 문제 넣기 → 컴퓨터(내 넘버링 연 채)
        await dk.evaluate("window.__keep=1")
        s = await story(ph, D0, '휴대폰고침B')
        ok('휴대폰고침B' in s and '컴퓨터처음스토리' in s, f'ⓑ 휴대폰: 컴퓨터 문제 스토리 고침 {s[:60]!r}')
        _, P1 = await nmgo(ph, 4)
        ok(bool(P1), f'ⓑ 휴대폰: 문제 하나 더({P1})')
        await tick(ph, '{pull:false}'); await tick(dk)
        w = await poll(dk, f"!!document.querySelector('#numv .nm-it[data-id=\"{P1}\"]')", 3)
        d = await dom(dk)
        ok(w is not None and P1 in d, f'ⓑ 컴퓨터 화면(새로고침 없이): 휴대폰이 넣은 문제 {sorted(d)}')
        ok('휴대폰고침B' in d.get(D0, ''), f'ⓑ 컴퓨터 화면(새로고침 없이): 휴대폰이 고친 스토리 {d.get(D0, "")[:60]!r}')
        ok(await dk.evaluate("window.__keep===1"), 'ⓑ 컴퓨터 새로고침 없음')
        await cnt('ⓑ 받은 뒤')
        # ⓒ 넘버링 복습 — 컴퓨터가 복습 화면을 연 채, 휴대폰이 평가·회차 정리
        await dk.evaluate(f"location.hash='#/_numr/{SJ}'"); await dk.wait_for_timeout(3000); await dk.evaluate("window.__keep=1")
        await ph.evaluate(f"location.hash='#/_numr/{SJ}'"); await ph.wait_for_timeout(3000)
        ok(await ph.evaluate(f"!!document.querySelector('#numv .nm-it[data-id=\"{D1}\"] [data-mk=\"0\"]')"), 'ⓒ 휴대폰: 복습 화면에 평가 단추')
        await ph.evaluate(f"(()=>{{const a=document.querySelector('#numv .nm-it[data-id=\"{D1}\"]');a.scrollIntoView({{block:'center'}});a.querySelector('[data-mk=\"0\"]').click()}})()"); await ph.wait_for_timeout(500)
        r = await getv(ph, f'num.r.{SJ}.{D1}')
        ok(r and r.get('m') == 0 and len(r.get('h') or []) == 1, f'ⓒ 휴대폰: 모름 평가 저장(num.r) {r}')
        await ph.evaluate("(document.querySelector('[data-cnt] [data-ract=end]')||document.querySelector('[data-ract=end]')).click()"); await ph.wait_for_timeout(500)
        await ph.evaluate("document.querySelector('.nm-ov [data-ract=renew]').click()"); await ph.wait_for_timeout(800)
        rl = await getv(ph, f'num.rl.{SJ}') or []
        ok(len(rl) == 1 and rl[0].get('c') == [1, 0, 0], f'ⓒ 휴대폰: 회차 정리 → 새 회차 · 끝난 회차 기록(num.rl) {rl}')
        await tick(ph, '{pull:false}'); await tick(dk)
        r2 = await getv(dk, f'num.r.{SJ}.{D1}'); rl2 = await getv(dk, f'num.rl.{SJ}') or []
        ok(r2 and r2.get('m') == 0, f'ⓒ 컴퓨터 저장소: 휴대폰 평가(num.r) 받음 {r2}')
        ok(len(rl2) == 1, f'ⓒ 컴퓨터 저장소: 휴대폰 회차 기록(num.rl) 받음 {len(rl2)}')
        RVD = f"""(()=>{{const a=document.querySelector('#numv .nm-it[data-id="{D1}"]');if(!a)return null;return {{pm:(a.querySelector('.nm-pm')||{{}}).textContent||'',hist:(a.querySelector('[data-ract=hist]')||{{}}).textContent||''}}}})()"""
        await dk.wait_for_timeout(800); v = await dk.evaluate(RVD)
        ok(v and '모름' in v['pm'] and '1' in v['hist'], f"ⓒ 컴퓨터 복습 화면(새로고침 없이): '지난 모름'·'이력 1' {v}")
        ok(await dk.evaluate("window.__keep===1"), 'ⓒ 컴퓨터 새로고침 없음')
        await dk.evaluate("document.querySelector('.nm-side [data-ract=hdlg]').click()"); await dk.wait_for_timeout(400)
        hr = await dk.evaluate("[...document.querySelectorAll('.nm-ov .nm-hrow summary')].map(s=>s.textContent)")
        ok(any('모름 1' in x and '진행 중' not in x for x in hr), f'ⓒ 컴퓨터 복습 이력 창: 휴대폰이 끝낸 회차 {hr}')
        await dk.evaluate("document.querySelectorAll('.nm-ov [data-x]').forEach(x=>x.click())"); await dk.wait_for_timeout(200)
        await dk.reload(); await dk.wait_for_timeout(3500); await settle(dk); v = await dk.evaluate(RVD)
        ok(v and '모름' in v['pm'] and '1' in v['hist'], f"ⓒ 컴퓨터 복습 화면 새로고침 뒤 '지난 모름'·'이력 1' {v}")
        # ⓖ 10-25c 진행 중인 회차(num.rs) — 휴대폰이 회차 중 평가(정리 전) → 컴퓨터 복습 화면(새로고침 없이) 같은 회차·평가 · 내 답안 = 낙서장(어디에도 저장·전송 안 됨)
        await dk.evaluate("window.__keep=1"); await ph.evaluate(f"location.hash='#/_numr/{SJ}'"); await ph.wait_for_timeout(2500)
        await ph.evaluate(f"(()=>{{const a=document.querySelector('#numv .nm-it[data-id=\"{D2}\"]');a.scrollIntoView({{block:'center'}});a.querySelector('[data-mk=\"1\"]').click()}})()"); await ph.wait_for_timeout(500)
        sid_p = await ph.evaluate("JBLNUM._RV.ses.sid")
        if not await ph.evaluate("!!document.querySelector('textarea[data-w]')"): await ph.evaluate("document.querySelector('[data-rwrite]').click()"); await ph.wait_for_timeout(900)
        await ph.locator('textarea[data-w]').first.click(); await ph.keyboard.type('낙서장답G'); await ph.wait_for_timeout(800)
        await tick(ph, '{pull:false}'); await tick(dk); await dk.wait_for_timeout(1200)
        v = await dk.evaluate(f"(()=>{{const s=JBLNUM._RV.ses,a=document.querySelector('#numv .nm-it[data-id=\"{D2}\"]'),o=a&&a.querySelector('.nm-mks .on');return {{sid:s&&s.sid,mk:s&&s.mk[{json.dumps(D2)}],on:o?o.dataset.mk:null}}}})()")
        ok(v['sid'] == sid_p and v['mk'] == 1 and v['on'] == '1', f"ⓖ 컴퓨터 복습 화면(새로고침 없이): 휴대폰의 진행 중인 회차·평가(애매함) {v} / {sid_p}")
        ok(await dk.evaluate("window.__keep===1"), 'ⓖ 컴퓨터 새로고침 없음')
        gp = json.dumps(gist_data(dev_p, SJ), ensure_ascii=False); lp = await ph.evaluate("Object.keys(localStorage).filter(k=>(localStorage.getItem(k)||'').indexOf('낙서장답G')>=0)")
        ok('낙서장답G' not in gp and not lp and await ph.evaluate("JBLNUM._RV.dr.a[" + json.dumps(D2) + "]===undefined||true"), f'ⓖ 내 답안(낙서장)은 저장·전송 안 됨(Gist·저장소에 없음) {lp}')
        # ⓔ 휴대폰에서 같은 스토리를 몇 분 동안 이어서 고침(12~15초마다 오감 — 실제 쓰는 모습) → 컴퓨터가 마지막 글까지
        await dk.evaluate(f"location.hash='#/_num/{SJ}'"); await dk.wait_for_timeout(2500); await ph.evaluate(f"location.hash='#/_num/{SJ}'"); await ph.wait_for_timeout(2500)
        seen = []
        for i in range(6):
            await story(ph, D2, f'E{i}'); await tick(ph, '{pull:false}'); await tick(dk)
            seen.append(f'E{i}' in ((await getv(dk, f'num.i.{SJ}.{D2}')) or {}).get('st', ''))
        await tick(ph); await tick(dk)
        v = ((await getv(dk, f'num.i.{SJ}.{D2}')) or {}).get('st', ''); d = await dom(dk)
        ok('E5' in v and 'E5' in d.get(D2, ''), f'ⓔ 같은 스토리를 6번 이어서 고침 → 컴퓨터가 고칠 때마다 받음 {seen} · 마지막 {d.get(D2, "")[-40:]!r}')
        # ⓕ 컴퓨터 넘버링이 기기 저장소(IndexedDB)로 옮겨진 뒤(저장 공간 정리 — 넘버링이 큰 사용자)에도 주고받음
        await dk.evaluate("__h.xsMove('회귀')"); await dk.wait_for_timeout(1500)
        xs = await dk.evaluate("({on:__h.XS.on,n:__h.XS.M.size,ls:Object.keys(localStorage).filter(k=>k.indexOf('jblhub.v1.num.i.')===0).length})")
        ok(xs['on'] and xs['n'] >= 5 and xs['ls'] == 0, f'ⓕ 컴퓨터 넘버링 → 기기 저장소 {xs}')
        await dk.reload(); await dk.wait_for_timeout(3500); await settle(dk)
        _, D3 = await nmgo(dk, 5); s = await story(dk, D3, '기기저장소스토리F')
        await tick(dk, '{pull:false}'); await ph.evaluate(f"location.hash='#/_num/{SJ}'"); await ph.wait_for_timeout(2500); await tick(ph)
        d = await dom(ph)
        ok(D3 in d and '기기저장소스토리F' in d.get(D3, ''), f'ⓕ 기기 저장소 쪽 컴퓨터 문제·스토리가 휴대폰 화면에 {sorted(d)}')
        await story(ph, D3, '폰답F'); await tick(ph, '{pull:false}'); await dk.evaluate(f"location.hash='#/_num/{SJ}'"); await dk.wait_for_timeout(2500); await tick(dk)
        d = await dom(dk)
        ok('폰답F' in d.get(D3, ''), f'ⓕ 휴대폰 고침 → 기기 저장소 쪽 컴퓨터 화면에 {d.get(D3, "")[:60]!r}')
        # ⓓ 컴퓨터 데이터 안전
        await cnt('끝')
        ns = [n for _, n in CNT]
        ok(all(b2 >= a2 for a2, b2 in zip(ns, ns[1:])) and ns[-1] == 6, f'ⓓ 컴퓨터 넘버링 문제 수가 줄지 않음 · 끝에 6 {CNT}')
        await tick(ph); n_p = await nlive(ph)
        ok(n_p == ns[-1], f'ⓓ 휴대폰 문제 수 = 컴퓨터 {n_p} / {ns[-1]}')
        await dk.screenshot(path=J.TMP + '/ux_sync_num_desk.png'); await ph.screenshot(path=J.TMP + '/ux_sync_num_phone.png')
        ok(not errs, f'페이지 오류 0 {errs[:3]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
