"""ux3 묶음 I 회귀: 측정 상태 기계(tstate)·세션 벽시계·안전장치·자정 분할·trest·tseg·창 두 개·트래커 조각(trkUI).
가짜 시계(page.clock — 컨텍스트 공용)로 2026-09-24(목) 10:00 기준. 맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치).
스크린샷 work/_tmp/ux3i_timer_*.png"""
import re, os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
NOW = datetime.datetime(2026, 9, 24, 10, 0, 0)
TODAY = '2026-09-24'; MIN = 60000
async def ls(pg, k):
    v = await pg.evaluate(f"localStorage.getItem('jblhub.v1.{k}')"); return json.loads(v) if v else None
async def boot(pg, h, ms=1800):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.clock.run_for(ms)
    for _ in range(150):   # 팩(과목 자료) 도착까지 — 느린 컴퓨터(클라우드)에서는 1.8초 안에 다 못 받음(가짜 시계와 별개로 실제 읽기 시간)
        if await pg.evaluate("!!(window.__h&&__h.plStat&&__h.plStat().pend===0)"): break
        await pg.wait_for_timeout(100); await pg.clock.run_for(100)
TE = "(d)=>(JSON.parse(localStorage.getItem('jblhub.v1.tedit')||'[]')).filter(e=>e&&!e.x&&e.f!=='r'&&(!d||e.d===d)).reduce((a,e)=>a+(+e.ms||0),0)"   # ux3 fix2 F6 줄인 몫 = tedit trim
async def tsum(pg, d=TODAY):
    return sum(((await ls(pg, 'time')) or {}).get(d, {}).values()) + await pg.evaluate(f"({TE})('{d}')")
async def tall(pg): return sum(sum(v.values()) for v in ((await ls(pg, 'time')) or {}).values()) + await pg.evaluate(f"({TE})('')")
async def st(pg): return await pg.evaluate("document.querySelector('#clock').dataset.st")   # ux4 묶음2 시계 알약
async def tp(pg, a):   # 알약 → 팝오버 줄(start·rest·resume·stop·big) — 옛 #tmr 누르기·길게 누르기 대신
    await pg.evaluate("a=>{const p=document.querySelector('#tpop');if(!p.classList.contains('on'))document.querySelector('#clock').click();document.querySelector('#tpop [data-tp='+a+']').click()}", a)
async def fresh(pg, h, extra=''):
    await boot(pg, h); await pg.evaluate("localStorage.clear();sessionStorage.clear();" + extra); await boot(pg, h)

async def part_states(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== I1·I3 상태 전이·휴식·멈춤', tag)
    await pg.clock.install(time=NOW)
    await fresh(pg, '#/OMS1/DD1/learn', "localStorage.setItem('jblhub.v1.tauto','false');")
    ok(await st(pg) == 'off', f"자동 꺼짐 → ○ 상태 off ({await pg.evaluate("document.querySelector('#clock').dataset.lab")!r})")
    await tp(pg, 'start'); await pg.clock.run_for(300)
    t = await pg.evaluate("document.querySelector('#clock').dataset.lab"); ok(await st(pg) == 'sess' and '공부 0:00' in t, f"▶ 공부 시작 → 알약 '공부 0:00'(10-04 이번 집중) ({t!r})")
    ts = await ls(pg, 'tstate'); ok(ts and ts['st'] == 'sess' and ts['S'] == 'OMS1' and ts['D'] == 'DD1', f"tstate 세션 귀속 = 지금 문서 {ts and (ts['S'], ts['D'])}")
    await pg.clock.run_for(10 * MIN)   # 입력 없이 10분 — 세션은 벽시계
    s0 = await tsum(pg); ok(abs(s0 - 10 * MIN) <= 21000, f'세션 10분(입력 없음) → time +{s0 / MIN:.2f}분')
    ok(re.search(r'공부 (9|10):\d\d', await pg.evaluate("document.querySelector('#clock').dataset.lab")), f"알약 이번 집중 m:ss {await pg.evaluate("document.querySelector('#clock').dataset.lab")!r}")   # ux4f A8 fmtH 내림(h:mm:ss 알약과 같은 기준) — 10분 ±1초는 0:09 또는 0:10
    await pg.screenshot(path=J.TMP + f'/ux3i_timer_sess_{tag}.png', clip={'x': 0, 'y': 0, 'width': vp['width'], 'height': 60})
    # ☕ 쉬기 — 5분 동안 time 그대로, trest +5분
    await tp(pg, 'rest'); await pg.clock.run_for(300)
    ok(await st(pg) == 'rest', f"☕ → 쉬는 중 ({await pg.evaluate("document.querySelector('#clock').dataset.lab")!r})")
    a0 = await tsum(pg); await pg.clock.run_for(5 * MIN); a1 = await tsum(pg)
    ok(a1 - a0 <= 1000, f'쉬는 동안 time 증가 {(a1 - a0) / 1000:.0f}초 (0)')
    tr = ((await ls(pg, 'trest')) or {}).get(TODAY, 0); ok(abs(tr - 5 * MIN) <= 21000, f'trest[오늘] = {tr / 1000:.0f}초 (300±20 — 20초마다 기록)')
    await pg.evaluate("dispatchEvent(new Event('pagehide'))")
    tr = ((await ls(pg, 'trest')) or {}).get(TODAY, 0); ok(abs(tr - 5 * MIN - 300) <= 1000, f'닫을 때 기록 → trest = {tr / 1000:.1f}초 (300±1)')
    # 새로고침 → 휴식 유지, 휴식 시계 이어감
    await boot(pg, '#/OMS1/DD1/learn', 1500)
    t = await pg.evaluate("document.querySelector('#clock').dataset.lab"); import re as _re; ok(await st(pg) == 'rest' and _re.search(r'휴식 5:[0-5]\d', t), f"새로고침 → 휴식 유지·휴식 시계 이어감 ({t!r})")   # 5분 + 새로고침 몇 초(부하에 따라 달라짐)
    ok(await pg.evaluate("document.querySelector('#trband').hidden"), '새로고침(2분 안) → 닫힘 질문 없음')
    # ▶ 다시 → 세션
    await tp(pg, 'resume'); await pg.clock.run_for(300)
    ok(await st(pg) == 'sess', f"▶ → 세션 재개 ({await pg.evaluate("document.querySelector('#clock').dataset.lab")!r})")
    await pg.clock.run_for(2 * MIN)
    # ■ 종료 — 알약 → [■ 세션 끝내기]
    await tp(pg, 'stop'); await pg.clock.run_for(300)
    ok(await st(pg) == 'end', f"■ 세션 끝내기 → 멈춤 ({await pg.evaluate("document.querySelector('#clock').dataset.lab")!r})")
    tt = await pg.inner_text('#toast'); ok('세션 끝' in tt and '공부' in tt and '휴식' in tt, f'종료 알림 {tt[:60]!r}')
    # 같은 문서에서 스크롤·움직여도 time 0 (자동 측정 켬)
    await pg.evaluate("localStorage.setItem('jblhub.v1.tauto','true');__h.T.auto=true")
    e0 = await tsum(pg)
    for i in range(6): await pg.mouse.wheel(0, 200); await pg.mouse.move(300 + i * 5, 400); await pg.mouse.wheel(0, 1); await pg.clock.run_for(20000)
    await pg.evaluate("dispatchEvent(new Event('pagehide'))"); e1 = await tsum(pg)
    ok(e1 - e0 == 0 and await st(pg) == 'end', f'■ 뒤 같은 문서 2분 입력 → time +{(e1 - e0) / 1000:.0f}초 (0) · 멈춤 유지')
    # (10-04 사용자 '멈춤 표시를 했을 땐 … 수동으로 공부 시작이라고 누르기 전까진 자동으로 공부 전환이 되면 안되는') 새 문서를 열어도 멈춤 그대로
    await pg.evaluate("location.hash='#/OMS1/_home'"); await pg.clock.run_for(1500)
    for i in range(3): await pg.mouse.move(400 + i * 7, 420); await pg.mouse.wheel(0, 1); await pg.clock.run_for(1000)
    ok(await st(pg) == 'end', f"새 문서 열기 → 멈춤 그대로 ({await pg.evaluate("document.querySelector('#clock').dataset.lab")!r})")
    await pg.evaluate("__h.trDo('autoon')"); await pg.mouse.wheel(0, 1); await pg.clock.run_for(1000)
    ok(await st(pg) == 'run', f"↻ 자동 측정 다시 → 자동 측정 ({await pg.evaluate("document.querySelector('#clock').dataset.lab")!r})")
    # 측정 중 → 알약 ☕(from auto) → ▶ → 자동 측정으로
    await tp(pg, 'rest'); await pg.clock.run_for(300)
    ok(await st(pg) == 'rest' and (await ls(pg, 'tstate'))['from'] == 'auto', '측정 중 → ☕ (자동에서 쉬기)')
    await tp(pg, 'resume'); await pg.clock.run_for(300)
    ok(await st(pg) == 'run' and await ls(pg, 'tstate') is None, f"▶ → 자동 측정으로 돌아감 ({await st(pg)})")
    # 트래커 조각(홈 띠·달력 카드)과 시계 알약·팝오버가 같은 상태 — 한 곳에서 ☕ → 1초 안에 모두
    await pg.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=\"trkt\">'+__h.trkUI('band')+__h.trkUI('card')+'</div>')")
    await pg.click('#clock'); await pg.clock.run_for(300)
    sts = await pg.evaluate("[...document.querySelectorAll('[data-trk] .trs')].map(e=>e.className.split('trs-')[1])")
    ok(len(sts) >= 2 and set(sts) == {'run'} and await st(pg) == 'run' and await pg.evaluate("[...document.querySelectorAll('#tpop [data-tp]')].map(b=>b.dataset.tp).slice(0,2).join()") == 'stop,rest', f'띠·카드 조각·알약·팝오버 = 측정 중 {sts}')
    ok(await pg.evaluate("!document.querySelector('#nav [data-trk],#tmr')"), 'ux4 묶음2 메뉴 트래커·#tmr 없음(시계 알약 하나)')
    await pg.screenshot(path=J.TMP + f'/ux3i_timer_pop_{tag}.png')
    await pg.evaluate("document.querySelector('#trkt [data-trk=band] [data-trb=rest]').click()"); await pg.clock.run_for(1000)
    sts = await pg.evaluate("[...document.querySelectorAll('[data-trk] .trs')].map(e=>e.className.split('trs-')[1])")
    ok(await st(pg) == 'rest' and set(sts) == {'rest'} and await pg.evaluate("document.querySelector('#clock').classList.contains('rest')"), f'띠 조각 ☕ → 1초 안에 알약·조각 모두 쉬는 중 {sts}')
    ok(await pg.evaluate("[...document.querySelectorAll('#tpop [data-tp]')].map(b=>b.dataset.tp).slice(0,2).join()") == 'resume,stop', '열린 팝오버도 바로 [▶ 다시][■]')
    await pg.evaluate("document.querySelector('#tpop [data-tp=stop]').click()"); await pg.clock.run_for(300)
    ok(await st(pg) == 'end', '팝업 ■ → 멈춤')
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), '가로 넘침 0')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def part_safety(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== I2 세션 안전장치')
    await pg.clock.install(time=NOW)
    await fresh(pg, '#/CONS/_home', "localStorage.setItem('jblhub.v1.tauto','false');")
    await pg.evaluate("__h.trStart()"); await pg.clock.run_for(1000)
    t0 = await tsum(pg)
    await pg.clock.run_for(30 * MIN)
    ok(abs((await tsum(pg)) - t0 - 30 * MIN) <= 21000, f'세션 30분·무입력 → time +{((await tsum(pg)) - t0) / MIN:.2f}분')
    ok(await pg.evaluate("document.querySelector('#trband').hidden"), '30분엔 되묻기 없음(기본 90분)')
    await pg.clock.run_for(61 * MIN)
    band = await pg.evaluate("(b=>b.hidden?'':b.textContent)(document.querySelector('#trband'))")
    ok('입력이 없어요' in band and '마지막 입력' in band, f'90분 무입력 → 띠 {band!r}')
    await pg.screenshot(path=J.TMP + '/ux3i_timer_ask_mac.png')
    await pg.evaluate("document.querySelector('#trband [data-trq=stopli]').click()"); await pg.clock.run_for(500)
    d = (await tsum(pg)) - t0
    ok(abs(d - MIN) <= 2000 and await st(pg) not in ('end', 'sess', 'rest'), f'[마지막 입력 때 멈춤] → 초과분 빠짐 · time +{d / 1000:.0f}초 (시작 +1분)')
    seg = ((await ls(pg, 'tseg')) or {}).get(TODAY, [])
    ss = sum(q[1] - q[0] for q in seg if q[4].startswith('s'))
    ok(abs(ss - 60) <= 2, f'세션 구간(tseg) 합 {ss}초 = 60초')
    # 30분 더 무응답 → 자동으로 마지막 입력 +1분에 끝냄
    await pg.evaluate("__h.trStart()"); await pg.clock.run_for(1000); t1 = await tsum(pg)
    await pg.clock.run_for(121 * MIN)
    d = (await tsum(pg)) - t1
    ok(await st(pg) not in ('end', 'sess', 'rest') and abs(d - MIN) <= 2000, f'되묻기 30분 무응답 → 자동 종료 · time +{d / 1000:.0f}초')
    # 세션 되묻기 끔 → 12시간 상한
    await pg.evaluate("localStorage.setItem('jblhub.v1.sessAsk','0')")
    await pg.evaluate("__h.trStart()"); await pg.clock.run_for(1000); t2 = await tall(pg)
    await pg.clock.fast_forward(12 * 60 * MIN + 5 * MIN); await pg.clock.run_for(2000)   # 기기가 잠든 채 12시간(타이머가 한 번에 몰려 옴)
    d = await tall(pg) - t2
    ok(await st(pg) not in ('end', 'sess', 'rest') and abs(d - 12 * 60 * MIN) <= 5000, f'되묻기 끔 → 12시간 상한에서 끝냄 · +{d / 3600000:.3f}시간')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def part_closed(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== I2 켜진 채 닫힌 세션')
    await pg.clock.install(time=NOW)
    await fresh(pg, '#/', "localStorage.setItem('jblhub.v1.tauto','false');")
    now = await pg.evaluate("Date.now()")
    for how in ('cend', 'cnow'):
        seed = {'st': 'sess', 't0': now - 60 * MIN, 'seg': now - 50 * MIN, 'S': 'CONS', 'D': '', 'at': now - 50 * MIN, 'd': TODAY, 'own': 'deadwin', 'li': now - 50 * MIN, 'sum': 10 * MIN, 'rsum': 0}
        await pg.evaluate("s=>{localStorage.setItem('jblhub.v1.tstate',JSON.stringify(s));localStorage.removeItem('jblhub.v1.time')}", seed)
        await boot(pg, '#/', 1500)
        band = await pg.evaluate("(b=>b.hidden?'':b.textContent)(document.querySelector('#trband'))")
        ok('켜진 채 닫혔어요' in band and '09:10' in band, f'다시 열기 → 질문 {band!r}')
        if how == 'cend':
            await pg.screenshot(path=J.TMP + '/ux3i_timer_closed_mac.png')
            await pg.evaluate("document.querySelector('#trband [data-trq=cend]').click()"); await pg.clock.run_for(500)
            ok(await tsum(pg) == 0 and await st(pg) not in ('end', 'sess', 'rest'), f'[마지막 기록 때 끝난 것으로(기본)] → 더하지 않음 ({await tsum(pg)}) · 자동 대기(F2 — ■ 멈춤 아님)')
        else:
            await pg.evaluate("document.querySelector('#trband [data-trq=cnow]').click()"); await pg.clock.run_for(500)
            ok(abs(await tsum(pg) - 50 * MIN) <= 10000 and await st(pg) == 'sess', f'[지금까지로] → +{(await tsum(pg)) / MIN:.1f}분 · 세션 계속')
    # 기본값은 1분 뒤 저절로
    await pg.evaluate("__h.trStop();localStorage.removeItem('jblhub.v1.time')"); await pg.clock.run_for(300)
    now2 = await pg.evaluate("Date.now()")
    await pg.evaluate("s=>localStorage.setItem('jblhub.v1.tstate',JSON.stringify(s))", {'st': 'sess', 't0': now2 - 30 * MIN, 'seg': now2 - 20 * MIN, 'S': 'CONS', 'D': '', 'at': now2 - 20 * MIN, 'd': TODAY, 'own': 'x', 'li': now2 - 20 * MIN, 'sum': 10 * MIN, 'rsum': 0})
    await boot(pg, '#/', 1000); await pg.clock.run_for(61000)
    ok(await st(pg) not in ('end', 'sess', 'rest') and (await tsum(pg)) == 0 and await pg.evaluate("document.querySelector('#trband').hidden"), '답이 없으면 1분 뒤 기본값(마지막 기록 때) · 자동 대기(F2)')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def part_midnight(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== I3 자정 분할 · I4 tseg')
    await pg.clock.install(time=datetime.datetime(2026, 9, 23, 23, 50, 0))
    await fresh(pg, '#/OMS1/DD1/learn', "localStorage.setItem('jblhub.v1.tauto','false');")
    await pg.evaluate("__h.trStart()")
    await pg.clock.run_for(30 * MIN); await pg.evaluate("dispatchEvent(new Event('pagehide'))")
    tm = (await ls(pg, 'time')) or {}; y = sum(tm.get('2026-09-23', {}).values()); t = sum(tm.get('2026-09-24', {}).values())
    ok(abs(y - 10 * MIN) <= 6000 and abs(y + t - 30 * MIN) <= 2000, f'세션 23:50→00:20 → 어제 {y / MIN:.1f}분 · 오늘 {t / MIN:.1f}분 (≈10·20)')
    sg = (await ls(pg, 'tseg')) or {}
    ok(sg.get('2026-09-23') and sg['2026-09-23'][-1][1] == 86400 and sg.get('2026-09-24') and sg['2026-09-24'][0][0] == 0, f"tseg 자정에서 나뉨 {sg.get('2026-09-23', [])[-1:]} {sg.get('2026-09-24', [])[:1]}")
    # 자동 측정도 한 번의 flush가 자정을 넘으면 나눔 — tRec 직접
    await pg.evaluate("__h.trStop()"); await pg.evaluate("localStorage.removeItem('jblhub.v1.time');localStorage.removeItem('jblhub.v1.tseg')")
    n = await pg.evaluate("(()=>{const b=new Date(2026,8,24,0,0,0).getTime();return __h.tRec('CONS','WHT',b-10*60000,b+20*60000,'a')})()")
    tm = (await ls(pg, 'time')) or {}; td = (await ls(pg, 'timed')) or {}
    ok(tm.get('2026-09-23', {}).get('CONS') == 10 * MIN and tm.get('2026-09-24', {}).get('CONS') == 20 * MIN and td.get('2026-09-23', {}).get('CONS:WHT') == 10 * MIN, f"tRec(23:50~00:20) → 어제 10분·오늘 20분 {tm}")
    # I4 자동 측정 10분 → tseg 한 구간
    await pg.clock.run_for(2 * 3600 * 1000)
    await pg.evaluate("localStorage.setItem('jblhub.v1.tauto','true');localStorage.removeItem('jblhub.v1.tstate');localStorage.removeItem('jblhub.v1.tseg')")
    await boot(pg, '#/OMS1/DD1/learn', 1000)
    for i in range(20): await pg.mouse.move(300 + (i % 9) * 11, 420); await pg.mouse.wheel(0, 1); await pg.clock.run_for(30000)
    await pg.evaluate("dispatchEvent(new Event('pagehide'))")
    L = [q for q in ((await ls(pg, 'tseg')) or {}).get(TODAY, []) if q[4] == 'a']
    ok(len(L) == 1 and abs((L[0][1] - L[0][0]) - 600) <= 20 and L[0][2] == 'OMS1' and L[0][3] == 'DD1', f'자동 10분 → tseg 한 구간 {L}')
    s1 = await pg.evaluate(f"(o=>Object.values(o).reduce((a,b)=>a+b,0))(__h.tDay('{TODAY}'))")
    await pg.evaluate("localStorage.removeItem('jblhub.v1.tseg')"); await boot(pg, '#/OMS1/DD1/learn', 800)
    s2 = await pg.evaluate(f"(o=>Object.values(o).reduce((a,b)=>a+b,0))(__h.tDay('{TODAY}'))")
    ok(abs(s1 - s2) <= 1000, f'tseg를 지워도 tDay 합계 같음 ({s1} / {s2})')
    await pg.evaluate("localStorage.setItem('jblhub.v1.tseg',JSON.stringify({'2026-03-26':[[0,60,'OMS1','','a']],'2026-03-28':[[0,60,'OMS1','','a']]}))")
    await boot(pg, '#/', 800); sg = (await ls(pg, 'tseg')) or {}
    ok('2026-03-26' not in sg and '2026-03-28' in sg, f'180일 넘은 tseg는 부팅 때 버림 {sorted(sg)}')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def part_two(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); A = await ctx.new_page(); B = await ctx.new_page(); errs = []
    for pg in (A, B): pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    print('== I8 창 두 개')
    await A.clock.install(time=NOW)
    await fresh(A, '#/PHARM/_home', "localStorage.setItem('jblhub.v1.tauto','false');")
    await boot(A, '#/PHARM/_home'); await boot(B, '#/CONS/_home')
    await A.evaluate("__h.trStart()"); await A.clock.run_for(1000)
    ok(await st(B) == 'sess', f"A에서 ▶ → B도 1초 안에 세션 ({await B.evaluate("document.querySelector('#clock').dataset.lab")!r})")
    for i in range(12):   # 10초마다 번갈아 입력 — 2분(기록 창이 옮겨 다녀도 한 번씩만)
        pg = (A, B)[i % 2]; await pg.mouse.move(300 + i * 7, 400); await pg.mouse.wheel(0, 1); await asyncio.sleep(0.1); await A.clock.run_for(10000)
    for q in (A, B): await q.evaluate("dispatchEvent(new Event('pagehide'))")
    s = sum(sum(v.values()) for v in ((await ls(A, 'time')) or {}).values())
    ok(115000 <= s <= 125000, f'두 창 번갈아 2분 세션 → time +{s / 1000:.0f}초 (겹침 없음)')
    await B.evaluate("__h.trRest()"); await B.clock.run_for(1000)
    ok(await st(A) == 'rest', f"B에서 ☕ → A도 쉬는 중 ({await A.evaluate("document.querySelector('#clock').dataset.lab")!r})")
    await A.evaluate("__h.trStop()"); await A.clock.run_for(1000)
    ok(await st(B) == 'end', 'A에서 ■ → B도 멈춤')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await part_states(b, {'width': 1280, 'height': 900}, False, 'mac')
        await part_states(b, {'width': 820, 'height': 1180}, True, 'ipp')
        await part_states(b, {'width': 1180, 'height': 820}, True, 'ipl')
        await part_safety(b)
        await part_closed(b)
        await part_midnight(b)
        await part_two(b)
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
