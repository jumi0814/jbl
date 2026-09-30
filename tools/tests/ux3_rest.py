"""ux3 J9 회귀: 공부하다 멈추면 쉬는 시간 자동 측정(참고 HUB 휴식) — LS restAuto(기본 켬)·restMax(기본 90분).
가짜 시계(page.clock — 컨텍스트 공용)로 2026-09-24(목) 10:00 기준.
무활동 → 휴식(시작 = 마지막 입력) · 돌아오면 띠 [☕ 쉬었어요](기본 10초)/[📖 공부했어요] · 상한 90분 · ■ 뒤 휴식 아님 · 자정 분할 · 화면 숨김 ·
restAuto 끔 = 옛 띠 · 창 두 개 · 새로고침은 휴식 아님 · 닫았다 다시 열기(≤ restMax 이어 감 / 넘으면 빼기) · 달력 휴식 줄·빗금·카드 = trest.
맥 1280×900 + 아이패드 세로 820×1180 + 가로 1180×820(터치) 표시 확인. 스크린샷 work/_tmp/ux3i_rest_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime, math, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
NOW = datetime.datetime(2026, 9, 24, 10, 0, 0)
TODAY = '2026-09-24'; MIN = 60000
def fmtH(ms):
    m = int(math.floor(max(0, ms) / 60000)); return f'{m // 60}:{m % 60:02d}'   # ux4c 1회차 fmtH = 분 내림
async def ls(pg, k):
    v = await pg.evaluate(f"localStorage.getItem('jblhub.v1.{k}')"); return json.loads(v) if v else None
async def boot(pg, h, ms=1800):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.clock.run_for(ms)
async def fresh(pg, h, extra=''):
    await boot(pg, h); await pg.evaluate("localStorage.clear();sessionStorage.clear();" + extra); await boot(pg, h)
# ux3 fix2 F6 — 줄이는 기록은 tedit(k:'trim', 휴식은 f:'r')에 − 로 남음: 기록된 합 = time + tedit(공부) · trest + tedit(휴식)
TE = "(d,r)=>(JSON.parse(localStorage.getItem('jblhub.v1.tedit')||'[]')).filter(e=>e&&!e.x&&e.d===d&&((e.f==='r')===r)).reduce((a,e)=>a+(+e.ms||0),0)"
async def tsum(pg, d=TODAY): return sum(((await ls(pg, 'time')) or {}).get(d, {}).values()) + await pg.evaluate(f"({TE})('{d}',false)")
async def rest(pg, d=TODAY): return ((await ls(pg, 'trest')) or {}).get(d, 0) + await pg.evaluate(f"({TE})('{d}',true)")
async def st(pg): return await pg.evaluate("document.querySelector('#clock').dataset.st")   # ux4 묶음2 시계 알약
async def band(pg): return await pg.evaluate("(b=>b.hidden?'':b.textContent)(document.querySelector('#idleband'))")
async def study(pg, n, step=30000, x=300):
    """n번 입력(step 간격) — 마지막 입력 뒤 멈춤 · 돌려줌: 마지막 입력 시각(ms)"""
    for i in range(n):
        await pg.mouse.move(x + (i % 9) * 11, 420 + (i % 3)); await pg.clock.run_for(50)
        if i < n - 1: await pg.clock.run_for(step - 50)
    return await pg.evaluate("__h.T.last")
HIDE = "Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))"
SHOW = "delete document.hidden;document.dispatchEvent(new Event('visibilitychange'))"

async def part_idle(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== J9 무활동 → 휴식 · 되묻기 · 상한 · ■')
    await pg.clock.install(time=NOW)
    await fresh(pg, '#/OMS1/DD1/learn')
    ok(await pg.evaluate("__h.restOn()") and await pg.evaluate("__h.restMaxMin()") == 90, 'restAuto 기본 켬 · restMax 기본 90분')
    # 10분 공부(30초마다 입력) → 무입력 8분 넘으면 휴식(시작 = 마지막 입력)
    t0 = await pg.evaluate("Date.now()")
    li = await study(pg, 21)
    await pg.clock.run_for(8 * MIN + 2000)
    ts = await ls(pg, 'tstate')
    ok(await st(pg) == 'rest' and ts and ts.get('ar') == 1 and ts.get('r0') == li + MIN, f"무입력 8분 → ☕ 쉬는 중·ar·r0 = 마지막 입력 + 1분(flow V10 — 미리 센 1분은 공부) ({await pg.inner_text('#clock .ckl')!r} r0-li={ts and ts.get('r0') - li})")
    ok(re.search(r'휴식 7:0\d', await pg.inner_text('#clock .ckl')), f"알약 휴식 시계 = 마지막 입력 1분 뒤부터 ({await pg.inner_text('#clock .ckl')!r})")
    ok(abs(await tsum(pg) - 11 * MIN) <= 1000, f'공부 = 11분(flow V10 마지막 입력 뒤 1분은 공부 그대로 — 시계 안 되감김) — time {await tsum(pg) / 1000:.0f}초')
    await pg.screenshot(path=J.TMP + '/ux3i_rest_tmr_mac.png', clip={'x': 0, 'y': 0, 'width': 1280, 'height': 60})
    # 마지막 입력에서 28분 뒤 입력 → 띠(기본 쉬었어요) → 10초 무응답
    await pg.clock.run_for(28 * MIN - 8 * MIN - 2000 - 50)
    await pg.mouse.move(600, 500); await pg.clock.run_for(300)
    bt = await band(pg); ok('쉬었어요' in bt and '공부했어요' in bt and '27분' in bt, f'돌아와 입력 → 띠 {bt!r}')
    await pg.screenshot(path=J.TMP + '/ux3i_rest_band_mac.png')
    ok(await st(pg) == 'run', f'입력 → 휴식 끝·자동 측정 다시 ({await st(pg)})')
    await pg.clock.run_for(10500)
    ok(await band(pg) == '', '10초 무응답 → 띠 닫힘(쉬었어요로 확정)')
    r = await rest(pg); ok(abs(r - 27 * MIN) <= MIN, f'trest[오늘] = {r / MIN:.2f}분 (27±1)')
    segs = [q for q in ((await ls(pg, 'tseg')) or {}).get(TODAY, []) if str(q[4]).startswith('r')]
    ok(len(segs) == 1 and segs[0][4] == 'ra', f'tseg 휴식 구간 1개(ra) {segs}')
    tm = await tsum(pg); ok(abs(tm - 11 * MIN) <= 1500, f'time은 11분만 ({tm / 1000:.0f}초)')
    # [📖 공부했어요] → 휴식에서 빼고 공부로
    await pg.evaluate("__h.trStop()"); await pg.evaluate("localStorage.removeItem('jblhub.v1.tstate')"); await pg.clock.run_for(300)
    await pg.evaluate("location.hash='#/OMS1/DD2/learn'"); await pg.clock.run_for(800)
    li = await study(pg, 5, x=320); await pg.clock.run_for(9 * MIN); r0 = await rest(pg); tm0 = await tsum(pg)   # 휴식이 시작된 뒤(공부 몫 다 기록)
    r0 -= 8 * MIN - 50   # 이미 기록된 휴식(마지막 입력 1분 뒤부터) — 옮기면 이것까지 빠짐
    await pg.clock.run_for(19 * MIN - 50); await pg.mouse.move(610, 500); await pg.clock.run_for(300)
    ok('공부했어요' in await band(pg), '두 번째 휴식 → 띠')
    await pg.evaluate("document.querySelector('#idleband [data-rb=study]').click()"); await pg.clock.run_for(300)
    r1 = await rest(pg); tm1 = await tsum(pg)
    ok(abs(r1 - r0) <= 21000 and abs((tm1 - tm0) - 27 * MIN) <= 2000, f'[공부했어요] → trest +{(r1 - r0) / 1000:.0f}초 (0) · time +{(tm1 - tm0) / MIN:.2f}분 (27)')
    segs = [q for q in ((await ls(pg, 'tseg')) or {}).get(TODAY, []) if str(q[4]).startswith('r')]
    ok(len(segs) == 1, f'옮긴 휴식 구간은 tseg에서 빠짐 (휴식 구간 {len(segs)})')
    tdd = ((await ls(pg, 'timed')) or {}).get(TODAY, {}).get('OMS1:DD2', 0)
    ok(tdd >= 27 * MIN, f'공부로 옮긴 시간은 멈춘 강의(DD2)에 ({tdd / MIN:.1f}분)')
    # 무입력 3시간 → 휴식은 상한 90분까지
    li = await study(pg, 3, x=340); r0 = await rest(pg)
    await pg.clock.run_for(9 * MIN); await pg.clock.fast_forward(171 * MIN); await pg.clock.run_for(2000)
    r1 = await rest(pg)
    ok(abs((r1 - r0) - 90 * MIN) <= 2000 and await st(pg) != 'rest' and await ls(pg, 'tstate') is None, f'무입력 3시간 → trest +{(r1 - r0) / MIN:.2f}분 (상한 90) · 자동 대기 ({await st(pg)})')
    await pg.mouse.move(640, 500); await pg.clock.run_for(300)
    ok(await band(pg) == '' and await st(pg) == 'run', '상한 뒤 돌아오면 띠 없이 자동 측정')
    # restMax 30분
    await pg.evaluate("localStorage.setItem('jblhub.v1.restMax','30')")
    await study(pg, 3, x=360); r0 = await rest(pg); await pg.clock.run_for(60 * MIN)
    ok(abs((await rest(pg) - r0) - 30 * MIN) <= 2000, f'restMax 30 → 휴식 +{(await rest(pg) - r0) / MIN:.1f}분')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.restMax')")
    # ■ 종료 뒤 30분 → 휴식 0
    await study(pg, 3, x=380); await pg.evaluate("__h.trStop()"); await pg.clock.run_for(300); r0 = await rest(pg)
    await pg.clock.run_for(30 * MIN)
    ok(await rest(pg) == r0 and await st(pg) == 'end', f'■ 종료 뒤 30분 → trest +{(await rest(pg) - r0) / 1000:.0f}초 (0) · 멈춤')
    # ■ 자동 휴식 중 → 그 시각에 휴식 끝
    await pg.evaluate("location.hash='#/OMS1/DD1/learn'"); await pg.clock.run_for(800)
    await study(pg, 3, x=400); await pg.clock.run_for(12 * MIN); r0 = await rest(pg)
    ok(await st(pg) == 'rest', '다시 무활동 → 휴식')
    await pg.evaluate("__h.trStop()"); r0 = await rest(pg); await pg.clock.run_for(20 * MIN)
    ok(await rest(pg) == r0 and await st(pg) == 'end', f'■ → 휴식 끝(그 뒤 +{(await rest(pg) - r0) / 1000:.0f}초)')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def part_hide(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== J9 화면 숨김 · 자정 · restAuto 끔 · 새로고침 · 닫았다 열기')
    await pg.clock.install(time=datetime.datetime(2026, 9, 23, 23, 40, 0))
    await fresh(pg, '#/CONS/_home')
    await study(pg, 21)   # 23:40~23:50 공부
    await pg.evaluate(HIDE); await pg.clock.run_for(1000)
    ts = await ls(pg, 'tstate'); ok(ts and ts.get('ar') == 1 and ts.get('why') == 'hide', f"화면 숨김 → 자동 휴식 {ts and ts.get('why')}")
    await pg.clock.run_for(30 * MIN - 1000); await pg.evaluate(SHOW); await pg.clock.run_for(300)
    bt = await band(pg); ok('쉬었어요' in bt and '30분' in bt, f'00:20 화면 돌아옴 → 띠 {bt!r}')
    await pg.clock.run_for(10500)
    y = await rest(pg, '2026-09-23'); t = await rest(pg, '2026-09-24')
    ok(abs(y - 10 * MIN) <= 5000 and abs(t - 20 * MIN) <= 5000, f'23:50 휴식 → 00:20 복귀 → 어제 {y / MIN:.1f}분 · 오늘 {t / MIN:.1f}분 (10·20)')
    ok(await st(pg) == 'run', f'화면 돌아옴 → 자동 측정 다시 ({await st(pg)})')
    # 화면 숨김 15분 → 휴식 15분
    await study(pg, 3, x=330); r0 = await rest(pg, TODAY)
    await pg.evaluate(HIDE); await pg.clock.run_for(15 * MIN); await pg.evaluate(SHOW); await pg.clock.run_for(10800)
    ok(abs(await rest(pg, TODAY) - r0 - 15 * MIN) <= 2000, f'숨김 15분 → 휴식 +{(await rest(pg, TODAY) - r0) / MIN:.2f}분')
    # 숨김 30초(탭 잠깐 바꿈) → 휴식 아님
    await study(pg, 2, x=350); r0 = await rest(pg, TODAY)
    await pg.evaluate(HIDE); await pg.clock.run_for(30000); await pg.evaluate(SHOW); await pg.clock.run_for(500)
    ok(await rest(pg, TODAY) == r0 and await band(pg) == '', f'숨김 30초 → 휴식 0·띠 없음 (+{(await rest(pg, TODAY) - r0) / 1000:.0f}초)')
    # 새로고침 → 휴식 아님(자동 측정 중 새로고침)
    await study(pg, 3, x=360); r0 = await rest(pg, TODAY)
    await boot(pg, '#/CONS/_home', 1500)
    ok(await ls(pg, 'tstate') is None and await st(pg) != 'rest' and await rest(pg, TODAY) == r0, f'새로고침 → 쉬는 중 아님 ({await st(pg)})')
    # 닫았다 20분 뒤 다시 열기 → 공백 = 휴식 · 2시간 뒤 → 넣지 않음
    for gap, want in ((20, 20), (120, 0)):
        await study(pg, 3, x=380); r0 = await rest(pg, TODAY)
        await pg.evaluate(HIDE); await pg.evaluate("dispatchEvent(new Event('pagehide'))")
        await pg.goto('about:blank'); await pg.clock.run_for(gap * MIN)
        await pg.goto(U + '#/CONS/_home'); await pg.clock.run_for(1500)
        await pg.mouse.move(700, 450); await pg.clock.run_for(10800)
        d = await rest(pg, TODAY) - r0
        ok(abs(d - want * MIN) <= 15000, f'닫고 {gap}분 뒤 다시 열기 → 휴식 +{d / MIN:.1f}분 ({want})')
    # restAuto 끔 → 자동 휴식 0 · 옛 띠
    await pg.evaluate("localStorage.setItem('jblhub.v1.restAuto','false')")
    await study(pg, 3, x=400); r0 = await rest(pg, TODAY)
    await pg.clock.run_for(12 * MIN); ok(await ls(pg, 'tstate') is None and await st(pg) != 'rest', 'restAuto 끔 → 무활동이어도 쉬는 중 아님')
    await pg.mouse.move(720, 450); await pg.clock.run_for(300)
    bt = await band(pg); ok('입력이 없었어요' in bt and await rest(pg, TODAY) == r0, f'restAuto 끔 → 옛 띠 {bt!r} · 휴식 0')
    await pg.evaluate("document.querySelector('#idleband [data-ib=no]').click()")
    await pg.evaluate(HIDE); await pg.clock.run_for(10 * MIN); await pg.evaluate(SHOW); await pg.clock.run_for(500)
    ok(await rest(pg, TODAY) == r0, 'restAuto 끔 → 화면 숨김 10분도 휴식 0')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.restAuto')")
    # ☕ 수동 휴식도 한 번 상한(restMax) — 자동에서 쉬기
    await study(pg, 3, x=420); await pg.evaluate("__h.trRest()"); await pg.clock.run_for(300); r0 = await rest(pg, TODAY)
    await pg.evaluate("localStorage.setItem('jblhub.v1.restMax','30')"); await pg.clock.run_for(45 * MIN)
    ok(abs((await rest(pg, TODAY) - r0) - 30 * MIN) <= 2000 and await st(pg) != 'rest', f'☕ 수동 휴식 45분 → 상한 30분에 멈춤 (+{(await rest(pg, TODAY) - r0) / MIN:.1f}분 · {await st(pg)})')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def part_two(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); A = await ctx.new_page(); B = await ctx.new_page(); errs = []
    for q in (A, B): q.on('pageerror', lambda e: errs.append(str(e)[:200]))
    print('== J9 창 두 개')
    await A.clock.install(time=NOW)
    await boot(A, '#/OMS1/_home'); await A.evaluate("localStorage.clear()")
    await boot(A, '#/OMS1/_home'); await boot(B, '#/CONS/_home')
    await study(A, 10)
    await A.clock.run_for(12 * MIN)
    ok(await st(A) == 'rest' and await st(B) == 'rest', f'A 무활동 → A·B 모두 쉬는 중 ({await st(A)}·{await st(B)})')
    r0 = await rest(A)
    await B.mouse.move(500, 500); await asyncio.sleep(0.1); await A.clock.run_for(1000)
    ok(await st(A) != 'rest' and await st(B) == 'run', f'B에서 공부 시작 → A 휴식 끝 ({await st(A)}·{await st(B)})')
    r1 = await rest(A)
    for i in range(20): await B.mouse.move(500 + i, 520); await asyncio.sleep(0.02); await A.clock.run_for(30000)   # B 10분 공부
    r2 = await rest(A)
    ok(r1 - r0 < 2 * MIN and r2 == r1, f'휴식은 B 시작 시각에 끝(그 뒤 +{(r2 - r1) / 1000:.0f}초)')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def part_view(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== J9 표시', tag)
    await pg.clock.install(time=NOW)
    await fresh(pg, '#/PHARM/RX/learn')
    await study(pg, 21); await pg.clock.run_for(20 * MIN)   # 10분 공부 → 휴식 진행 중(20분)
    # 달력: 상태 카드 휴식 = trest + 진행 · 요약 · 오늘 패널 휴식 줄·빗금
    await pg.evaluate("location.hash='#/_cal'"); await pg.clock.run_for(1500)
    ok(await st(pg) == 'rest', '달력으로 가도(입력 없이) 쉬는 중')
    exp = await pg.evaluate("__h.restStats().ms")
    cr = await pg.inner_text('#cc-rest'); ok(cr == fmtH(exp), f'상태 카드 휴식 {cr} = trest[오늘]+진행 {fmtH(exp)}')
    rs = await pg.inner_text('#cc-rs'); ok('집중' in rs and '1회' in rs, f'휴식 카드 요약 {rs!r}')
    ok(await pg.evaluate("document.querySelectorAll('#calday .cband .cbk.r').length") >= 1, '24시간 띠에 휴식(빗금) 블록')
    rows = await pg.evaluate("[...document.querySelectorAll('#calday .crow.r')].map(r=>r.textContent)")
    ok(len(rows) == 1 and '휴식' in rows[0], f'기록 목록 ☕ 휴식 줄 {rows}')
    await pg.screenshot(path=J.TMP + f'/ux3i_rest_cal_{tag}.png')
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), '가로 넘침 0(달력)')
    # 측정 설정: 켬/상한
    await pg.evaluate("document.querySelector('#calmset').open=true"); await pg.clock.run_for(100)
    ok(await pg.evaluate("document.querySelector('[data-cset=restAuto]').checked") and await pg.evaluate("document.querySelector('[data-cset=restMax]').value") == '90', '측정 설정: 쉬는 시간 재기 켬 · 상한 90분')
    await pg.select_option('[data-cset=restMax]', '60'); ok(await ls(pg, 'restMax') == 60, '상한 60 → LS restMax=60')
    await pg.select_option('[data-cset=restMax]', '90')
    # ⏱ 크게: 쉬는 중 · 집중 %
    await pg.evaluate("__h.bigOpen()"); await pg.clock.run_for(1100)
    ok(await pg.inner_text('#bcl') == '☕ 쉬는 중' and '집중' in await pg.inner_text('#bcs'), f"⏱ 크게 {await pg.inner_text('#bcl')!r} · {await pg.inner_text('#bcs')!r}")
    await pg.screenshot(path=J.TMP + f'/ux3i_rest_big_{tag}.png')
    await pg.keyboard.press('Escape'); await pg.clock.run_for(300)   # Esc도 입력 → 휴식 끝
    # 홈 오늘 띠 조각(band) 짧게 '휴식 h:mm' · 시계 팝업 휴식 줄
    await pg.clock.run_for(10500)
    await pg.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=\"trkt\">'+__h.trkUI('band')+'</div>')")
    t = await pg.inner_text('#trkt'); ok(re.search(r'휴식 0:(19|2\d)', t), f'오늘 띠 조각 {t!r} (휴식은 마지막 입력 1분 뒤부터 — flow V10)')
    await pg.click('#clock'); await pg.clock.run_for(300)
    pl = await pg.evaluate("(e=>e?e.textContent:'')(document.querySelector('#tpop .trrl'))")
    ok('휴식' in pl and '집중' in pl and '가장 긴 휴식' in pl, f'시계 팝업 휴식 줄 {pl!r}')
    ok(await pg.evaluate("!document.querySelector('#tpop #trestc,#tpop select')||!!document.querySelector('#tpop #trsj')"), 'ux4 묶음2 시계 팝오버에는 설정 없음(📅 달력 측정 설정)')
    await pg.screenshot(path=J.TMP + f'/ux3i_rest_pop_{tag}.png')
    # 측정 설정(달력)에서 끄기 → 휴식 없음
    await pg.evaluate("document.querySelector('#tpop [data-tp=goal]').click()"); await pg.clock.run_for(600)
    await pg.evaluate("(c=>{c.checked=false;c.dispatchEvent(new Event('change',{bubbles:true}))})(document.querySelector('[data-cset=restAuto]'))")
    ok(await ls(pg, 'restAuto') is False, '측정 설정에서 끄면 LS restAuto=false')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.restAuto')")
    # 휴식 중 띠 화면(아이패드 폭 — 띠 넘침)
    await pg.evaluate("location.hash='#/PHARM/RX/learn'"); await pg.clock.run_for(800)
    await study(pg, 3); await pg.clock.run_for(12 * MIN); await pg.mouse.move(400, 300); await pg.clock.run_for(300)
    bw = await pg.evaluate("(b=>{const r=b.getBoundingClientRect();return [r.left,r.right,innerWidth,b.hidden]})(document.querySelector('#idleband'))")
    ok(not bw[3] and bw[0] >= 0 and bw[1] <= bw[2], f'되묻기 띠 화면 안 {bw}')
    await pg.screenshot(path=J.TMP + f'/ux3i_rest_band_{tag}.png')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await part_idle(b)
        await part_hide(b)
        await part_two(b)
        await part_view(b, {'width': 1280, 'height': 900}, False, 'mac')
        await part_view(b, {'width': 820, 'height': 1180}, True, 'ipp')
        await part_view(b, {'width': 1180, 'height': 820}, True, 'ipl')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
