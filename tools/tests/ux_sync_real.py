"""10-26 사용자 '내 컴퓨터에선 넘버링이 임상두경부해부학 등등 넘버링 다 추가해놓은게 왜!! 모바일에선 안 뜨냐고 … 넘버링 페이지 모든걸 연동해달라니까' 회귀.
깨끗한 새 창이 아니라 실제로 쓰던 그대로를 흉내 냄(fakegist REAL — 실제 GitHub처럼 1MB 넘는 파일은 잘려 오고 raw_url로 따로 · 크기만큼 늦은 응답):
 ① 연결 전부터 컴퓨터에 많이 — ANAT 160문제(그림 붙인 문제 23개 ≈ 2MB)·OMS1 145·IMPL 40 + 복습 기록 + ★ · 넘버링은 기기 저장소(IndexedDB)로 옮긴 뒤 새로고침
 ② 휴대폰 = 압축 풀기(DecompressionStream)가 없는 브라우저 흉내 · 휴대폰에만 있던 문제 1 · 컴퓨터 ANAT 넘버링 한 조각(NANAT3)은 처음 3번 받기 실패(502)
    → 연결 코드로 연결 · 한 조각이 막혀도 나머지는 바로 옴 · 넘버링 화면 띠 '아직 안 왔어요' · 동기화 창 '못 받음' → 잠시 뒤 다 옴
    → 휴대폰 '내 넘버링'(#/_num/ANAT) 화면에 161문제(그림까지) · OMS1 145 · IMPL 40 · 띠 사라짐 · 동기화 창 '✓ 다 받음'
 ③ 컴퓨터도 휴대폰 문제를 받음 · 압축 못 하는 휴대폰이 보낸 묶음(한글 글 — 조각이 1MB 아래)도 컴퓨터가 읽음
 ④ 실시간: 컴퓨터 ANAT 문제 스토리를 실제 편집기로 고침 → 보내는 양은 그 조각만(ANAT 넘버링 전체의 1/3 미만) → 휴대폰 화면(새로고침 없이)에
 ⑤ 같은 휴대폰의 다른 화면(홈 화면 앱처럼 저장소 따로 · 연결 안 함) → 넘버링 화면 띠 '이 화면은 기기 동기화가 꺼져 있어요' · 칩 '동기화 꺼짐'
 ⑥ 옛 판(v2 — git 6b634ffa 허브) 기기와 섞여도 안전: 옛 판은 새 판 묶음(v3)을 건너뛰고 제 넘버링을 지우지 않음 · 새 판은 옛 판이 보낸 넘버링(과목 묶음 안)을 받음
    → 옛 판 기기를 새 판으로 새로고침하면 컴퓨터 넘버링을 다 받고 제 것도 그대로 · 컴퓨터도 그 기기 것을 그대로
 ⑦ 컴퓨터 넘버링 수는 한 번도 줄지 않음 · 진단 복사에 토큰 없음 · 페이지 오류 0
실행: JBL_HTTP=1 .venv/bin/python tools/tests/ux_sync_real.py"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import jblpaths as J, asyncio, json, re, subprocess
from playwright.async_api import async_playwright
import fakegist as FG
from fakegist import gist_all, settle, tick, poll, NS, TOK, gh, raw
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m, flush=True)
    if not c: fails.append(m)
    return c
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
NOZ = "Object.defineProperty(window,'CompressionStream',{value:undefined,configurable:true,writable:true});Object.defineProperty(window,'DecompressionStream',{value:undefined,configurable:true,writable:true});"
CNT = "sj=>__h.stKeys('num.i.'+sj+'.').filter(k=>{const v=__h.stGet(k);return v&&v.indexOf('\"del\":1')<0&&v.indexOf('\"del\":true')<0}).length"
SEED = """([sj,n,every,kb,base])=>{const b=JSON.parse(base),A='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',rnd=m=>{let s='';for(let i=0;i<m;i++)s+=A[Math.random()*64|0];return s;},t0=Date.now()-3*864e5;
  for(let i=0;i<n;i++){const id='r'+sj+i,st='<p>'+sj+' 스토리 '+i+' — 머리글자 따기 '+'가나다라마바사아자차'.repeat(6)+'</p>'+(every&&i%every===0?'<p><img src="data:image/webp;base64,'+rnd(kb*1024)+'" width="640"></p>':'');
   __h.stSet('num.i.'+sj+'.'+id,JSON.stringify(Object.assign({},b,{id,k:'user',src:[],o:i,u:t0+i*1000,st,done:i%3===0})));
   if(i%10===0)__h.stSet('num.r.'+sj+'.'+id,JSON.stringify({id,h:[{t:t0+i*1000+5,s:'ses'+i,m:i%3}],w:[],u:t0+i*1000+5,m:i%3,d:t0+i*1000+5}));}
  return n;}"""
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
async def boot(pg, h='#/'):
    await pg.goto(U + h); await pg.wait_for_function(WAIT, timeout=90000); await pg.wait_for_timeout(1200)
async def numgo(pg, sj):
    await pg.evaluate(f"location.hash='#/_num/{sj}'"); await pg.wait_for_function("!!document.querySelector('#numv .nm-info')&&window.JBLNUM&&JBLNUM._S&&JBLNUM._S.sj", timeout=60000); await pg.wait_for_timeout(1500)
async def nmgo(pg, sj, i=0):   # 실제 화면: 그 과목 JB i번째 카드 '✎ 넘버링' → 넣은 넘버링 문제 id
    await pg.evaluate(f"location.hash='#/{sj}/_jb'"); await pg.wait_for_function(WAIT + "&&document.querySelector('#stage article.qc .nmgo')", timeout=60000); await pg.wait_for_timeout(800)
    aid = await pg.evaluate(f"(()=>{{const c=document.querySelectorAll('#stage article.qc')[{i}];c.scrollIntoView({{block:'center'}});c.querySelector('.nmgo').click();return c.dataset.aid}})()"); await pg.wait_for_timeout(3000)
    return await pg.evaluate(f"(()=>{{const it=JBLNUM._S.items.find(x=>!x.del&&(x.src||[]).some(s=>s.t==='jb'&&s.id==={aid!r}));return it?it.id:null}})()")
async def story(pg, sj, iid, text):   # 실제 편집기로 스토리 고침(ux_sync_num.py와 같음)
    sel = f'.nm-it[data-id="{iid}"] .nm-s .nm-c'
    await pg.evaluate("s=>document.querySelector(s).scrollIntoView({block:'center'})", sel); await pg.wait_for_timeout(300)
    await pg.locator(sel).click(); await pg.wait_for_timeout(300)
    if not await pg.evaluate("!!JBLNUM._S.ed"):
        await pg.locator(f'.nm-it[data-id="{iid}"] .nm-s [data-act=edit]').click(); await pg.wait_for_timeout(300)
    await pg.keyboard.press('End'); await pg.keyboard.type(text); await pg.wait_for_timeout(900); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(700)
    return await pg.evaluate(f"(()=>{{try{{return (JSON.parse(__h.stGet('num.i.{sj}.'+{iid!r}))||{{}}).st||''}}catch(e){{return ''}}}})()")
OLD = {}; OLDREV = '6b634ffa'   # 옛 판 = 10-25c 배포(동기화 v2) — HEAD로 하면 v3를 커밋한 뒤엔 새 판끼리 비교가 됨
def old_file(rel):
    if rel not in OLD: OLD[rel] = subprocess.run(['git', 'show', OLDREV + ':docs/' + rel], capture_output=True, cwd=J.ROOT).stdout
    return OLD[rel]
OLDRE = re.compile(r'^http://127\.0\.0\.1:\d+/(index\.html|num/num\.js|packs/[A-Z0-9]+\.js)(\?.*)?$')
async def old_route(route):   # 옛 판(git 6b634ffa) 허브·넘버링 모듈·과목 팩 — 같은 주소(같은 저장소)
    rel = OLDRE.match(route.request.url).group(1)
    await route.fulfill(status=200, headers={'Content-Type': ('text/html' if rel.endswith('.html') else 'application/javascript') + '; charset=utf-8', 'Cache-Control': 'no-store'}, body=old_file(rel))
async def main():
    if not U.startswith('http'): print('JBL_HTTP=1 로 실행해 주세요'); _sys.exit(2)
    FG.REAL[0] = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        dc = await b.new_context(viewport={'width': 1280, 'height': 900})
        pc = await b.new_context(viewport={'width': 393, 'height': 852}, is_mobile=True, has_touch=True, user_agent=UA); await pc.add_init_script(NOZ)
        for c, t in ((dc, 'dk'), (pc, 'ph')):
            await c.route('https://api.github.com/**', (lambda t: (lambda r: gh(r, t)))(t)); await c.route('https://gist.githubusercontent.com/**', raw)
        dk = await dc.new_page(); ph = await pc.new_page()
        for pg in (dk, ph): pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for pg in (dk, ph): await boot(pg); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await boot(pg)
        DC = []
        async def dcnt(tag): DC.append((tag, {s: await dk.evaluate(CNT, s) for s in ('ANAT', 'OMS1', 'IMPL')}))
        # ① 컴퓨터 — 실제 화면으로 하나 넣고 그 꼴로 많이 · 기기 저장소로 옮김 · 새로고침
        iid = await nmgo(dk, 'ANAT'); base = await dk.evaluate(f"__h.stGet('num.i.ANAT.'+{iid!r})")
        ok(bool(iid and base), f'① 컴퓨터: ANAT JB ✎ 넘버링으로 실제 문제 하나({iid}) — 이 꼴로 많이')
        n = [await dk.evaluate(SEED, ['ANAT', 160, 7, 80, base]), await dk.evaluate(SEED, ['OMS1', 145, 0, 0, base]), await dk.evaluate(SEED, ['IMPL', 40, 0, 0, base])]
        await dk.evaluate("(()=>{const m={ok:{},ng:{},bm:{'T01':{t:Date.now()},'T02':{t:Date.now()}}};__h.stSet('mk.ANAT',JSON.stringify(m));})()")
        await dk.evaluate("(()=>{__h.stSet('hlabel',JSON.stringify({y:'기출 표시',g:'암기'}));__h.stSet('tgoal','240');})()")   # 형광펜 색 이름·하루 목표도(10-26 '모든 기록')
        mv = await dk.evaluate("__h.xsMove('회귀').then(r=>r)"); await dk.wait_for_timeout(1500)
        await dk.reload(); await dk.wait_for_function(WAIT, timeout=90000); await dk.wait_for_timeout(1200); xs = await dk.evaluate("__h.xsReady().then(s=>s)")   # 주소가 같으면 goto는 새로고침이 아님
        await dcnt('연결 전')
        ok(mv and mv.get('ok') is not False and xs.get('on') and DC[-1][1]['ANAT'] == 161 and DC[-1][1]['OMS1'] == 145, f'① 컴퓨터 연결 전: 넘버링 {DC[-1][1]} · 기기 저장소(IndexedDB) {xs} · 옮기기 {mv}')
        sz = len(''.join(await dk.evaluate("__h.stKeys('num.i.ANAT.').map(k=>__h.stGet(k))")))
        ok(sz > 1800000, f'① ANAT 넘버링 글 {sz/1e6:.1f}MB(그림 포함)')
        # ② 휴대폰 — 자기 문제 하나 · 컴퓨터 연결(기준) → 휴대폰 연결 코드
        await ph.evaluate(SEED.replace("const id='r'+sj+i", "const id='p'+sj+i"), ['ANAT', 1, 0, 0, base])
        ok(await ph.evaluate("typeof DecompressionStream==='undefined'&&typeof CompressionStream==='undefined'"), '② 휴대폰: 압축·압축 풀기 없는 브라우저 흉내')
        await dk.evaluate(f"JBLSYNC.connect('{TOK}')"); await settle(dk, 1500)
        dev_d = await dk.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.devId'))")
        ga = gist_all(dev_d); groups = sorted({v['description'].split(' · ')[2] for v in FG.G.values() if (' · %s · ' % dev_d) in v['description']})
        ok(sum(1 for k in ga if k.startswith(NS + 'num.i.ANAT.')) == 161 and any(g.startswith('NANAT') for g in groups), f'② 컴퓨터가 보낸 묶음 {groups[:12]}… · ANAT 넘버링 161 실림')
        big = max(len(json.dumps(v['files'])) for v in FG.G.values() if (' · %s · NANAT' % dev_d) in v['description'])
        ok(big < sz / 3, f'② ANAT 넘버링은 조각마다 작게(가장 큰 조각 {big/1e6:.2f}MB · 전체 {sz/1e6:.1f}MB)')
        await dcnt('컴퓨터 연결 뒤')
        FG.FAIL['NANAT3'] = 3
        code = await dk.evaluate("JBLSYNC.code()")
        try:
            async with ph.expect_navigation(timeout=30000, wait_until='load'): await ph.evaluate(f"JBLSYNC.connect('{code}')")
        except Exception: pass
        await ph.wait_for_function(WAIT, timeout=90000); await settle(ph, 1500)
        await numgo(ph, 'ANAT')
        c1 = await ph.evaluate(CNT, 'ANAT'); st = await ph.evaluate("JBLSYNC.status()")
        ban = await ph.evaluate("(()=>{const b=document.querySelector('#numv [data-syncban]');return b&&!b.hidden?b.textContent:''})()")
        ok(0 < c1 < 162 and FG.FAIL['NANAT3'] < 3, f'② 휴대폰: 막힌 조각(NANAT3)만 빼고 먼저 옴 ANAT {c1}/162 · 실패 남은 횟수 {FG.FAIL["NANAT3"]} · 못 받음 {st.get("fails")} · 오류 {st.get("err")!r}')
        ok('아직 이 화면에 안 왔어요' in ban, f'② 휴대폰 넘버링 화면 띠: {ban[:80]!r}')
        await ph.evaluate("JBLSYNC.box()"); await ph.wait_for_timeout(500)
        bx = await ph.evaluate("(document.querySelector('#syncbox')||{}).textContent||''")
        ok('못 받음' in bx and '아직 이 화면에 안 온 문제' in bx, f'② 동기화 창에 못 받은 묶음·덜 온 수가 보임 {re.sub(chr(10), " ", bx)[:200]!r}')
        await ph.evaluate("document.querySelector('#bkclose')&&document.querySelector('#bkclose').click()")
        t = await poll(ph, f"(()=>{{const f={CNT};return f('ANAT')===162&&f('OMS1')===145&&f('IMPL')===40}})()", 120)
        ok(t is not None, f'② 잠시 뒤(실패한 조각만 다시) 휴대폰에 다 옴 — {t}s · ANAT {await ph.evaluate(CNT, "ANAT")} OMS1 {await ph.evaluate(CNT, "OMS1")} IMPL {await ph.evaluate(CNT, "IMPL")}')
        t = await poll(ph, "document.querySelectorAll('#numv .nm-it[data-id]').length>=162", 30)
        dn = await ph.evaluate("document.querySelectorAll('#numv .nm-it[data-id]').length")
        ok(t is not None, f'② 휴대폰 내 넘버링 ANAT 화면(새로고침 없이)에 {dn}문제')
        hv = await ph.evaluate("[JBLSYNC.get('hlabel'),JBLSYNC.get('tgoal'),JBLSYNC.get('mk.ANAT')]")
        ok(hv[0] and '기출 표시' in hv[0] and hv[1] == '240' and hv[2] and 'T01' in hv[2], f'② 형광펜 색 이름·하루 목표·★(mk)도 옴 {[str(x)[:40] for x in hv]}')
        im = await ph.evaluate("(()=>{const a=document.querySelector('#numv .nm-it[data-id=\"rANAT7\"]');return a?a.querySelectorAll('img[src^=\"data:image/webp\"]').length:-1})()")
        ok(im >= 1, f'② 그림 붙인 문제(rANAT7)의 그림도 옴 {im}')
        ban = await ph.evaluate("(()=>{const b=document.querySelector('#numv [data-syncban]');return b&&!b.hidden?b.textContent:''})()")
        ok(not ban, f'② 다 온 뒤 띠 사라짐 {ban[:60]!r}')
        await ph.evaluate("JBLSYNC.box()"); await ph.wait_for_timeout(500)
        bx = await ph.evaluate("(document.querySelector('#syncbox')||{}).textContent||''")
        ok('✓ 다 받음' in bx and '못 받음' not in bx, f'② 동기화 창 ✓ 다 받음 {re.sub(chr(10), " ", bx)[:160]!r}')
        await ph.evaluate("document.querySelector('#bkclose')&&document.querySelector('#bkclose').click()")
        chip = await ph.evaluate("(()=>{const c=document.querySelector('#numv .nm-sync');return c?[c.className,c.textContent]:null})()")
        ok(chip and 'on' in chip[0] and '동기화' in chip[1], f'② 넘버링 화면 칩 {chip}')
        # ③ 컴퓨터도 휴대폰 문제(압축 없이 보낸 묶음)를 받음
        await tick(dk, '{tnow:true}')
        t = await poll(dk, "!!__h.stGet('num.i.ANAT.pANAT0')", 40)
        ok(t is not None, f'③ 컴퓨터가 휴대폰에만 있던 문제를 받음(압축 못 하는 브라우저가 보낸 묶음) {t}s')
        await dcnt('휴대폰 연결 뒤')
        # ④ 실시간 — 컴퓨터 실제 편집기 → 휴대폰 화면
        await numgo(dk, 'ANAT'); await dk.evaluate("window.__keep=1"); await ph.evaluate("window.__keep=1")
        L0 = len(FG.LOG); s = await story(dk, 'ANAT', 'rANAT5', '실시간고침XYZ')
        ok('실시간고침XYZ' in s, '④ 컴퓨터: ANAT rANAT5 스토리를 편집기로 고침')
        t = await poll(ph, "(()=>{const a=document.querySelector('#numv .nm-it[data-id=\"rANAT5\"] .nm-s .nm-c');return a&&a.textContent.indexOf('실시간고침XYZ')>=0})()", 60)
        ok(t is not None, f'④ 휴대폰 화면(새로고침 없이)에 고친 스토리 {t}s')
        pt = [x for x in FG.LOG[L0:] if x[3] == 'dk' and x[0] in ('PATCH', 'POST')]
        ok(pt and max(x[2] for x in pt) < sz / 3, f'④ 보낸 양 = 그 조각만 {[round(x[2]/1e3) for x in pt]}KB (ANAT 넘버링 전체 {sz/1e6:.1f}MB)')
        ok(await dk.evaluate("window.__keep===1") and await ph.evaluate("window.__keep===1"), '④ 두 화면 모두 새로고침 없음')
        # ⑤ 같은 휴대폰의 다른 화면(저장소 따로 · 연결 안 함)
        hc = await b.new_context(viewport={'width': 393, 'height': 852}, is_mobile=True, has_touch=True, user_agent=UA)
        await hc.route('https://api.github.com/**', lambda r: gh(r, 'hs'))
        hs = await hc.new_page(); hs.on('pageerror', lambda e: errs.append(str(e)[:200])); await boot(hs); await numgo(hs, 'ANAT')
        ban = await hs.evaluate("(()=>{const b=document.querySelector('#numv [data-syncban]');return b&&!b.hidden?b.textContent:''})()")
        chip = await hs.evaluate("(()=>{const c=document.querySelector('#numv .nm-sync');return c?c.textContent:''})()")
        ok('이 화면은 기기 동기화가 꺼져 있어요' in ban and '홈 화면 아이콘' in ban, f'⑤ 연결 안 한 다른 화면: 넘버링 띠 안내 {ban[:70]!r}')
        ok('동기화 꺼짐' in chip, f'⑤ 칩 {chip!r}')
        await hs.evaluate("document.querySelector('#numv [data-syncban] [data-bkpop]').click()"); await hs.wait_for_timeout(500)
        ok(await hs.evaluate("!!document.querySelector('#bkpop.on #synctok')"), '⑤ [연결하기] = 동기화 연결 칸이 열림')
        await hc.close()
        # ⑥ 옛 판(v2) 기기와 섞임 → 새 판으로
        oc = await b.new_context(viewport={'width': 820, 'height': 1180}, is_mobile=True, has_touch=True, user_agent=UA.replace('iPhone; CPU iPhone OS', 'iPad; CPU OS'))
        await oc.route('https://api.github.com/**', lambda r: gh(r, 'od')); await oc.route('https://gist.githubusercontent.com/**', raw); await oc.route(OLDRE, old_route)
        od = await oc.new_page(); od.on('pageerror', lambda e: errs.append('옛 판: ' + str(e)[:200]))
        await boot(od); await od.evaluate("localStorage.clear();sessionStorage.clear()"); await boot(od)
        ov = await od.evaluate("typeof window.syncGrp==='function'?'?':(document.documentElement.outerHTML.indexOf('SYNC_V=3')<0?'v2':'v3')")
        await od.evaluate(SEED.replace("const id='r'+sj+i", "const id='o'+sj+i"), ['IMPL', 3, 0, 0, base])
        try:
            async with od.expect_navigation(timeout=8000, wait_until='load'): await od.evaluate(f"JBLSYNC.connect('{code}')")
        except Exception: pass
        await od.wait_for_function(WAIT, timeout=90000); await settle(od, 1500); await tick(od, '{force:true}')
        oc1 = await od.evaluate(CNT, 'IMPL')
        ok(ov == 'v2' and oc1 == 3, f'⑥ 옛 판({ov}) 기기: 연결해도 제 넘버링 그대로(새 판 묶음은 건너뜀 — 지우지 않음) IMPL {oc1}')
        await tick(dk, '{tnow:true}')
        t = await poll(dk, "!!__h.stGet('num.i.IMPL.oIMPL0')&&!!__h.stGet('num.i.IMPL.oIMPL2')", 40)
        ok(t is not None, f'⑥ 새 판 컴퓨터가 옛 판 기기의 넘버링(과목 묶음 안 v2)을 받음 {t}s')
        await oc.unroute(OLDRE, old_route); await od.reload(); await od.wait_for_function(WAIT, timeout=90000); await od.wait_for_timeout(1200); await settle(od, 1000); await tick(od, '{tnow:true}')
        t = await poll(od, f"(()=>{{const f={CNT};return f('ANAT')===162&&f('OMS1')===145&&f('IMPL')===43}})()", 120)
        ok(t is not None, f'⑥ 새 판으로 새로고침한 그 기기: 컴퓨터 넘버링 다 받고 제 것도 그대로 {t}s · ANAT {await od.evaluate(CNT, "ANAT")} IMPL {await od.evaluate(CNT, "IMPL")}')
        await tick(dk, '{tnow:true}'); await tick(ph, '{tnow:true}'); await tick(dk, '{tnow:true}')
        await dcnt('옛 판 기기 섞인 뒤')
        ok(DC[-1][1]['IMPL'] == 43 and DC[-1][1]['ANAT'] == 162, f'⑥ 컴퓨터: 옛 판에서 온 문제도 새 판 뒤에 그대로 {DC[-1][1]}')
        # ⑦
        prev = None; dec = []
        for tag, c in DC:
            if prev and any(c[s] < prev[s] for s in c): dec.append(tag)
            prev = c
        ok(not dec, f'⑦ 컴퓨터 넘버링 수는 줄지 않음 {DC}')
        dg = await ph.evaluate("(()=>{let t='';const w=navigator.clipboard.writeText;navigator.clipboard.writeText=v=>{t=v;return Promise.resolve();};JBLSYNC.box();document.querySelector('#syncdiag').click();navigator.clipboard.writeText=w;return t})()")
        await ph.wait_for_timeout(300)
        ok(dg and 'JBL 동기화 진단' in dg and TOK not in dg and 'ghp_' not in dg, f'⑦ 진단 복사(토큰 없음) {dg[:120]!r}')
        ok(not errs, f'⑦ 페이지 오류 0 {errs[:3]}')
        await ph.screenshot(path=J.TMP + '/ux_sync_real_phone.png')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
