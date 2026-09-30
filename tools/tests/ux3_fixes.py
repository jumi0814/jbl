"""ux3 검증 수정 회귀(func F1~F10 · visual V01~V12 · flow V01~V12) — 트래커·달력 고치기·메뉴 숨김·메뉴 구성·색·대비.
가짜 시계(page.clock) 2026-09-29(화) 10:00 · 맥 1280×900 · 아이패드 세로 820×1180 · 가로 1180×820(터치 has_touch). 스크린샷 work/_tmp/ux3f_*.png
  .venv/bin/python tools/tests/ux3_fixes.py [부분 …]   # 부분 = trk cal mrg nav tbl"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime, math, itertools
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
NOW = datetime.datetime(2026, 9, 29, 10, 0, 0)
TODAY, YDAY = '2026-09-29', '2026-09-28'; MIN = 60000
MAC, PORT, LAND = {'width': 1280, 'height': 900}, {'width': 820, 'height': 1180}, {'width': 1180, 'height': 820}
async def ls(pg, k):
    v = await pg.evaluate(f"localStorage.getItem('jblhub.v1.{k}')"); return json.loads(v) if v else None
async def boot(pg, h, ms=1800):
    await pg.goto('about:blank'); await pg.goto(U + h, timeout=120000); await pg.clock.run_for(ms)
async def fresh(pg, h, extra=''):
    await boot(pg, h); await pg.evaluate("localStorage.clear();sessionStorage.clear();" + extra); await boot(pg, h)
async def st(pg): return await pg.evaluate("__h.trState()")
async def sub(pg, d, s): return await pg.evaluate(f"__h.tDay('{d}')['{s}']||0")
async def tot(pg, d): return await pg.evaluate(f"(o=>Object.values(o).reduce((a,b)=>a+b,0))(__h.tDay('{d}'))")
async def study(pg, n, step=30000, x=300):
    for i in range(n):
        await pg.mouse.move(x + (i % 9) * 11, 420 + (i % 3)); await pg.clock.run_for(50)
        if i < n - 1: await pg.clock.run_for(step - 50)
    return await pg.evaluate("__h.T.last")
async def wheel(pg, n, step=30000):
    for i in range(n):
        await pg.mouse.wheel(0, 120 if i % 2 else -120); await pg.clock.run_for(step)
async def toast(pg): return await pg.evaluate("(e=>e&&e.style.display!=='none'?e.textContent:'')(document.querySelector('#toast'))")
async def ctxpg(b, vp, touch=False):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.clock.install(time=NOW); return ctx, pg, errs

# ---------------- 트래커: V01·V02(flow V01) · F2 · flow V04 · flow V05 · flow V10 ----------------
async def part_trk(b):
    for vp, touch, tag in ((PORT, True, 'port'), (LAND, True, 'land'), (MAC, False, 'mac')):
        ctx, pg, errs = await ctxpg(b, vp, touch); print('== 트래커 버튼(V01·V02)', tag)
        await fresh(pg, '#/CONS/WHT/learn')
        ok(await st(pg) == 'wait', f'{tag} 처음 = ○ 자동 대기 ({await st(pg)})')
        tp = (lambda s: pg.tap(s)) if touch else (lambda s: pg.click(s))
        # ux4 묶음2: 상단 #tmr 대신 시계 알약(#clock) → 팝오버 줄(#tpop [data-tp]) — 알약을 누르는 입력은 상태를 바꾸지 않음(TRKSEL)
        await tp('#clock'); await pg.clock.run_for(300)
        ok(await st(pg) == 'wait', f'{tag} 대기에서 알약을 눌러도 측정이 저절로 시작되지 않음 ({await st(pg)})')
        await tp('#tpop [data-tp=start]'); await pg.clock.run_for(300)
        ok(await st(pg) == 'sess', f"{tag} 대기에서 알약 → [▶ 공부 시작] → 세션 (☕ 휴식 아님) ({await st(pg)} · {await pg.inner_text('#clock')!r})")
        await pg.screenshot(path=J.TMP + f'/ux3f_trk_tmr_{tag}.png', clip={'x': 0, 'y': 0, 'width': vp['width'], 'height': 70})
        await pg.evaluate("__h.trStop();localStorage.removeItem('jblhub.v1.tstate')"); await boot(pg, '#/CONS/WHT/learn')
        # 자동 휴식 중 알약 → [▶ 다시 공부] → 자동 측정(run) — 새 수동 휴식·■ 아님
        await study(pg, 6); await pg.clock.run_for(9 * MIN)
        ts = await ls(pg, 'tstate'); ok(ts and ts.get('ar') == 1, f'{tag} 무입력 9분 → 자동 휴식(ar)')
        await tp('#clock'); await pg.clock.run_for(200); await tp('#tpop [data-tp=resume]'); await pg.clock.run_for(300)
        ts = await ls(pg, 'tstate')
        ok(await st(pg) == 'run' and ts is None, f'{tag} 자동 휴식 중 알약 ▶ 다시 공부 → 자동 측정(run) · tstate 없음 ({await st(pg)} · {ts})')
        t = await toast(pg); ok('다시 공부' in t, f'{tag} 알림 {t[:40]!r}')
        ok(not errs, f'{tag} pageerror 0 {errs[:2]}')
        await ctx.close()
    # 홈 오늘 띠 ▶ (1180 터치)
    ctx, pg, errs = await ctxpg(b, LAND, True); await fresh(pg, '#/')
    await pg.tap('#home [data-trk=band] [data-trb=start]'); await pg.clock.run_for(300)
    ok(await st(pg) == 'sess', f'홈 오늘 띠 ▶ → 세션 ({await st(pg)})')
    ok(await pg.evaluate("!document.querySelector('#tmr')&&!document.querySelector('#home [data-trb=big]')"), 'ux4 묶음2 상단 #tmr 없음(시계 알약 하나) · 홈 ⏱ 크게 없음')
    await ctx.close()

    ctx, pg, errs = await ctxpg(b, LAND, True); print('== F2 ■ 멈춤 풀기 · flow V10 시계 안 되감김')
    await fresh(pg, '#/CONS/WHT/learn')
    await wheel(pg, 10)
    await pg.evaluate("__h.trStop()"); await pg.clock.run_for(300); c0 = await sub(pg, TODAY, 'CONS')
    ok(await st(pg) == 'end', '■ → 멈춤')
    t = await toast(pg); ok('20분' in t, f'■ 알림에 다시 재는 법 {t[-40:]!r}')
    await wheel(pg, 4); ok(await sub(pg, TODAY, 'CONS') == c0 and await st(pg) == 'end', '■ 뒤 곧바로 같은 문서 입력 2분 → 안 잼(멈춤 유지)')
    await pg.clock.fast_forward(2 * 60 * MIN); await boot(pg, '#/CONS/WHT/learn')
    ok(await st(pg) != 'end', f'■ 뒤 2시간 지나 같은 문서 다시 열기 → 멈춤 풀림 ({await st(pg)})')
    c1 = await sub(pg, TODAY, 'CONS'); await wheel(pg, 10); await pg.evaluate("dispatchEvent(new Event('pagehide'))")
    d = await sub(pg, TODAY, 'CONS') - c1; ok(abs(d - 5 * MIN) <= 40000, f'다시 연 뒤 5분 입력 → 보존 +{d / MIN:.1f}분 (5)')
    # 보이는 채 20분 넘게 입력 없음 → 다음 입력에 풀림
    await pg.evaluate("__h.trStop()"); await pg.clock.run_for(300); await pg.clock.fast_forward(25 * MIN)
    await pg.mouse.move(500, 500); await pg.clock.run_for(1500)
    ok(await st(pg) == 'run', f'■ 뒤 25분 입력 없다가 움직임 → 자동 측정 ({await st(pg)})')
    # 저절로 끝난 세션(닫힘 기본값) → 같은 문서 공부 자동 측정
    now = await pg.evaluate("Date.now()")
    await pg.evaluate("s=>{localStorage.setItem('jblhub.v1.tstate',JSON.stringify(s));dispatchEvent(new StorageEvent('storage',{key:'jblhub.v1.tstate'}))}", {'st': 'sess', 't0': now - 60 * MIN, 'seg': now - 50 * MIN, 'S': 'CONS', 'D': 'WHT', 'at': now - 50 * MIN, 'd': TODAY, 'own': 'dead', 'li': now - 50 * MIN, 'sum': 10 * MIN, 'rsum': 0, 'cls': now - 50 * MIN})
    await boot(pg, '#/CONS/WHT/learn', 1000)
    band = await pg.evaluate("(b=>b.hidden?'':b.textContent)(document.querySelector('#trband'))")
    ok('켜진 채 닫혔어요' in band, f'닫은(cls) 세션 → 질문 {band[:30]!r}')
    await pg.clock.run_for(61000); ok(await st(pg) not in ('end', 'sess'), f'1분 뒤 기본값 → 자동 대기 ({await st(pg)})')
    c2 = await sub(pg, TODAY, 'CONS'); await wheel(pg, 10); await pg.evaluate("dispatchEvent(new Event('pagehide'))")
    d = await sub(pg, TODAY, 'CONS') - c2; ok(abs(d - 5 * MIN) <= 40000, f'기본값 뒤 같은 문서 5분 → +{d / MIN:.1f}분 (■ 멈춤 아님)')
    # flow V04 화면만 숨긴 채(hid, cls 없음) 다시 열림 → 질문 없이 세션 이어감(화면 밖 50분 셈)
    now = await pg.evaluate("Date.now()"); await pg.evaluate("localStorage.removeItem('jblhub.v1.time')")
    await pg.evaluate("s=>{localStorage.setItem('jblhub.v1.tstate',JSON.stringify(s));dispatchEvent(new StorageEvent('storage',{key:'jblhub.v1.tstate'}))}", {'st': 'sess', 't0': now - 60 * MIN, 'seg': now - 50 * MIN, 'S': 'CONS', 'D': 'WHT', 'at': now - 50 * MIN, 'd': TODAY, 'own': 'dead', 'li': now - 55 * MIN, 'sum': 10 * MIN, 'rsum': 0, 'hid': now - 50 * MIN})
    await boot(pg, '#/CONS/WHT/learn', 1500); await pg.clock.run_for(1000)
    band = await pg.evaluate("(b=>b.hidden?'':b.textContent)(document.querySelector('#trband'))")
    ok(band == '' and await st(pg) == 'sess', f'flow V04 숨김만(다른 앱·탭 버림) → 질문 없이 세션 ({await st(pg)} · {band[:20]!r})')
    exp = await pg.evaluate("Date.now()") - (now - 50 * MIN)   # page.clock은 실제 시간도 흐름 — 느린 기계에서 50분 + 걸린 시간
    ok(abs(await sub(pg, TODAY, 'CONS') - exp) <= 30000, f'화면 밖 50분 세션에 들어감 ({await sub(pg, TODAY, "CONS") / MIN:.1f}분 · 기대 {exp / MIN:.1f})')
    await pg.evaluate("__h.trStop();localStorage.removeItem('jblhub.v1.tstate')"); await boot(pg, '#/CONS/WHT/learn')
    # flow V10 자동 휴식 시작 때 시계가 되감기지 않음
    await study(pg, 6); await pg.clock.run_for(5 * MIN); c3 = await pg.evaluate("__h.tDay(__h.CAL?'%s':'%s')" % (TODAY, TODAY))
    s3 = await tot(pg, TODAY); await pg.clock.run_for(4 * MIN)
    ok(await st(pg) == 'rest' and await tot(pg, TODAY) >= s3, f'flow V10 자동 휴식 시작 → 오늘 합계 {s3 / 1000:.0f}→{await tot(pg, TODAY) / 1000:.0f}초 (되감기 없음)')
    # flow V05 띠 10초 기본값 뒤 [📖 공부로 바꾸기] 알림
    await pg.clock.run_for(20 * MIN); await pg.mouse.move(700, 500); await pg.clock.run_for(300)
    r0 = await pg.evaluate("__h.restDay('%s')" % TODAY); s0 = await tot(pg, TODAY)
    await pg.clock.run_for(10500); t = await toast(pg)
    ok('휴식' in t and '기록했어요' in t and '공부로 바꾸기' in t, f'flow V05 기본값(쉬었어요) 뒤 알림 {t!r}')
    await pg.screenshot(path=J.TMP + '/ux3f_rest_toast_land.png')
    await pg.evaluate("document.querySelector('#toast .tact').click()"); await pg.clock.run_for(300)
    r1 = await pg.evaluate("__h.restDay('%s')" % TODAY); s1 = await tot(pg, TODAY)
    ok(r0 - r1 >= 20 * MIN and s1 - s0 >= 20 * MIN, f'[📖 공부로 바꾸기] → 휴식 −{(r0 - r1) / MIN:.0f}분 · 공부 +{(s1 - s0) / MIN:.0f}분')
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()

# ---------------- 달력 고치기: F1 되돌리기 · F3 빼기 상한 · F5 입력칸 키 · F10 주소 · flow V05 📖 ----------------
SEEDC = {'time': {YDAY: {'CONS': 60 * MIN}}, 'timed': {YDAY: {'CONS:WHT': 60 * MIN}}, 'tseg': {YDAY: [[14 * 3600, 15 * 3600, 'CONS', 'WHT', 'a']]}, 'tauto': False}
async def seedc(pg, extra=None):
    await boot(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    S = dict(SEEDC); S.update(extra or {})
    await pg.evaluate("S=>{for(const k in S)localStorage.setItem('jblhub.v1.'+k,JSON.stringify(S[k]))}", S)
    await boot(pg, '#/_cal/' + YDAY)
async def rows(pg): return await pg.evaluate("[...document.querySelectorAll('#calday .crow')].map(r=>r.textContent.replace(/\\s+/g,' ').trim())")
async def segsum(pg, d, S):
    return await pg.evaluate(f"__h.daySegs('{d}').filter(x=>x.f.charAt(0)!=='r'&&x.S==='{S}').reduce((a,x)=>a+(x.e-x.s)*1000,0)")
async def part_cal(b):
    for vp, touch, tag in ((PORT, True, 'port'), (MAC, False, 'mac')):
        ctx, pg, errs = await ctxpg(b, vp, touch); print('== F1 되돌리기', tag)
        await seedc(pg)
        base = await sub(pg, YDAY, 'CONS'); ok(base == 60 * MIN, f'{tag} 어제 보존 자동 60분')
        # + 시간 추가 30분 10:00 → 🗑 → 화면의 되돌리기 = 🗑의 것
        await pg.evaluate("document.querySelector('#cadd').open=true"); await pg.clock.run_for(100)
        await pg.select_option('#caS', 'CONS'); await pg.fill('#caT', '10:00'); await pg.fill('#caH', '0'); await pg.fill('#caM', '30')
        await pg.evaluate("document.querySelector('[data-cago=\"1\"]').click()"); await pg.clock.run_for(300)
        ok(await sub(pg, YDAY, 'CONS') == 90 * MIN, f'{tag} + 30분 → 90')
        i = await pg.evaluate("__h.CAL.rows.findIndex(r=>r.s===36000)")
        await pg.evaluate(f"document.querySelector('[data-crd=\"{i}\"]').click()"); await pg.clock.run_for(300)
        ok(await sub(pg, YDAY, 'CONS') == 60 * MIN, f'{tag} 🗑 → 60')
        t = await toast(pg); ok('지웠어요' in t, f'{tag} 화면의 알림 = 🗑 것 {t[:30]!r}')
        await pg.evaluate("document.querySelector('#toast .tact').click()"); await pg.clock.run_for(300)
        v = await sub(pg, YDAY, 'CONS'); ok(v == 90 * MIN, f'{tag} 되돌리기 → 추가한 뒤(90) ({v / MIN:.0f}) — 측정 60 아래로 안 떨어짐')
        ok(abs(await segsum(pg, YDAY, 'CONS') - v) < 1000, f'{tag} 구간 합 = 합계 (시간대 없음 줄 없음) {await rows(pg)}')
        await pg.screenshot(path=J.TMP + f'/ux3f_cal_undo_{tag}.png')
        # add → edit(60분) → 고친 기록에서 옛 '추가' ✕ = 막힘(뒤 고침 먼저)
        i = await pg.evaluate("__h.CAL.rows.findIndex(r=>r.s===36000)")
        g2 = await pg.evaluate(f"__h.editSeg('{YDAY}',{i},{{start:36000,end:39600}})"); await pg.clock.run_for(300)
        ok(await sub(pg, YDAY, 'CONS') == 120 * MIN, f'{tag} ✎ 60분으로 → 120')
        ga = await pg.evaluate("__h.tEdit().filter(e=>e.k==='add'&&!e.x).map(e=>e.p||e.i).pop()")
        ok(await pg.evaluate(f"__h.undoEdit('{ga}')") == -1 and await sub(pg, YDAY, 'CONS') == 120 * MIN, f'{tag} 뒤에 고친 구간이 있는 추가 되돌리기 → 거부(-1) · 합계 그대로')
        await pg.evaluate("location.hash='#/_time'"); await pg.clock.run_for(800)
        dis = await pg.evaluate(f"(()=>{{const b=[...document.querySelectorAll('.tehist button[disabled]')];return b.length}})()")
        ok(dis >= 1, f'{tag} 고친 기록 — 막힌 ✕는 흐리게(disabled) {dis}')
        ok(await pg.evaluate(f"__h.undoEdit('{g2}')") >= 1 and await pg.evaluate(f"__h.undoEdit('{ga}')") >= 1 and await sub(pg, YDAY, 'CONS') == 60 * MIN, f'{tag} 뒤 것부터 되돌리면 둘 다 → 60')
        ok(abs(await segsum(pg, YDAY, 'CONS') - 60 * MIN) < 1000, f'{tag} 구간 합 = 합계 60')
        ok(not errs, f'{tag} pageerror 0 {errs[:2]}')
        await ctx.close()
    ctx, pg, errs = await ctxpg(b, MAC); print('== F3 빼기 상한 · F5 · F10 · 📖')
    await seedc(pg, {'time': {YDAY: {'CONS': 60 * MIN}, TODAY: {'CONS': 20 * MIN}}})
    await boot(pg, '#/_cal')
    ok(await pg.evaluate("__h.ntsAmt('%s','CONS')" % TODAY) == 20 * MIN, '오늘 보존 시간대 없음 20분')
    await pg.evaluate("document.querySelector('[data-cnts=\"CONS\"]').click()"); await pg.clock.run_for(200)
    hint = await pg.inner_text('#calday .cedit'); ok('0:20까지' in hint, f'± 줄에 빼기 상한 안내 {hint[-20:]!r}')
    await pg.fill('#cntsm', '60'); await pg.evaluate("document.querySelector('[data-cntsgo=\"-1\"]').click()"); await pg.clock.run_for(200)
    t = await toast(pg); ok(await sub(pg, TODAY, 'CONS') == 0 and '0:20까지만' in t, f'− 60 → 20까지만 뺌 ({await sub(pg, TODAY, "CONS")}) {t!r}')
    e = (await ls(pg, 'tedit'))[-1]; ok(e['ms'] == -20 * MIN, f"tedit −20분만 ({e['ms'] / MIN})")
    await pg.evaluate("__h.addTime({d:'%s',S:'CONS',D:'',start:null,min:30})" % TODAY)
    ok(await sub(pg, TODAY, 'CONS') == 30 * MIN, f'뒤에 30분 더하면 30 (음수에 삼켜지지 않음) ({await sub(pg, TODAY, "CONS") / MIN:.0f})')
    # F5 시간 입력칸 안의 ←·t·m
    await boot(pg, '#/_cal/' + YDAY)
    await pg.keyboard.press('a'); await pg.clock.run_for(200); await pg.focus('#caT')
    s0 = await pg.evaluate("__h.CAL.sel")
    for k in ('ArrowLeft', 't', 'm'): await pg.keyboard.press(k); await pg.clock.run_for(100)
    r = await pg.evaluate("[__h.CAL.sel,document.querySelector('#cadd').open,document.activeElement&&document.activeElement.id,document.body.classList.contains('sidefold')]")
    ok(r[0] == s0 and r[1] and r[2] == 'caT' and not r[3], f'F5 시간 입력칸에서 ← t m → 날짜·폼·포커스·메뉴 그대로 {r}')
    # F10 주소
    await pg.evaluate("location.hash='#/_cal?s=CONS'"); await pg.clock.run_for(500)
    await pg.evaluate("location.hash='#/_cal/2026-08-03'"); await pg.clock.run_for(500)
    ok(await pg.evaluate("location.hash") == '#/_cal/2026-08-03' and await pg.evaluate("__h.CAL.s") == '', f"F10 ?s 없는 주소 → 과목 필터 없음 ({await pg.evaluate('location.hash')})")
    await pg.evaluate("location.hash='#/_cal/2099-01-01'"); await pg.clock.run_for(500)
    ok(await pg.evaluate("__h.CAL.sel") == TODAY, f"F10 먼 앞날 → 오늘 ({await pg.evaluate('__h.CAL.sel')})")
    # flow V05 달력 휴식 줄 📖
    await pg.evaluate("S=>{localStorage.setItem('jblhub.v1.trest',JSON.stringify(S.r));localStorage.setItem('jblhub.v1.tseg',JSON.stringify(S.s))}",
                      {'r': {YDAY: 30 * MIN}, 's': {YDAY: [[14 * 3600, 15 * 3600, 'CONS', 'WHT', 'a'], [15 * 3600, 15 * 3600 + 1800, '', '', 'ra']]}})
    await boot(pg, '#/_cal/' + YDAY)
    c0 = await sub(pg, YDAY, 'CONS'); i = await pg.evaluate("__h.CAL.rows.findIndex(r=>r.r)")
    ok(await pg.evaluate(f"!!document.querySelector('[data-crs=\"{i}\"]')"), '휴식 줄에 📖 버튼')
    await pg.evaluate(f"document.querySelector('[data-crs=\"{i}\"]').click()"); await pg.clock.run_for(300)
    ok(await sub(pg, YDAY, 'CONS') - c0 == 30 * MIN and await pg.evaluate("__h.restDay('%s')" % YDAY) == 0, f'📖 → 보존 +30 · 휴식 0 ({(await sub(pg, YDAY, "CONS") - c0) / MIN:.0f})')
    ok(await pg.evaluate("__h.tLec('%s')['CONS:WHT']" % YDAY) == 90 * MIN, '바로 앞 공부 구간의 강의(WHT)로')
    await pg.screenshot(path=J.TMP + '/ux3f_cal_reststudy_mac.png')
    await pg.evaluate("document.querySelector('#toast .tact').click()"); await pg.clock.run_for(300)
    ok(await sub(pg, YDAY, 'CONS') == c0 and await pg.evaluate("__h.restDay('%s')" % YDAY) == 30 * MIN, '되돌리기 → 휴식 30 · 공부 그대로')
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()

# ---------------- 메뉴: flow V02 옛 sidefold · F9·V10 정리표 숨김 · F8 · flow V12 · V04 강의 줄 · V09 서랍 카드 · V08 칩 · flow V08 · flow V09 · F7 · V03 · V11 · V12 ----------------
CONTRAST = r"""(sel)=>{const lum=c=>{const m=c.match(/[\d.]+/g).map(Number);const f=v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(m[0])+.7152*f(m[1])+.0722*f(m[2])};
 const bg=e=>{while(e){const c=getComputedStyle(e).backgroundColor;const m=c.match(/[\d.]+/g);if(m&&(m.length<4||+m[3]>0.5))return c;e=e.parentElement;}return 'rgb(255,255,255)'};
 return [...document.querySelectorAll(sel)].filter(e=>e.getClientRects().length&&e.textContent.trim()).map(e=>{const a=lum(getComputedStyle(e).color),b=lum(bg(e));return +(((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(2))})}"""
def lab(h):
    def lin(c):
        c /= 255; return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = [lin(int(h[i:i + 2], 16)) for i in (1, 3, 5)]
    X = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047; Y = r * 0.2126 + g * 0.7152 + b * 0.0722; Z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883
    f = lambda v: v ** (1 / 3) if v > 0.008856 else 7.787 * v + 16 / 116
    return 116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))
FOLD = "document.body.classList.contains('sidefold')"
async def part_nav(b):
    V2 = {'sidefold': True, 'ux2old': 1, 'time': {YDAY: {'CONS': 30 * MIN}}}
    for vp, touch, tag in ((MAC, False, 'mac'), (LAND, True, 'land')):
        ctx, pg, errs = await ctxpg(b, vp, touch); print('== 메뉴 숨김(flow V02·F9·V10·flow V12)', tag)
        await boot(pg, '#/'); await pg.evaluate("S=>{localStorage.clear();for(const k in S)localStorage.setItem('jblhub.v1.'+k,JSON.stringify(S[k]))}", V2); await boot(pg, '#/')
        r = await pg.evaluate(f"[{FOLD},Math.round(document.querySelector('#side').getBoundingClientRect().width)]")
        ok(not r[0] and r[1] > 200, f'{tag} flow V02 2차 판 sidefold:true → 🏠 오늘에서는 메뉴 보임 {r}')
        await pg.screenshot(path=J.TMP + f'/ux3f_nav_v2home_{tag}.png')
        await boot(pg, '#/CONS/WHT/learn'); ok(await pg.evaluate(FOLD), f'{tag} 문서 화면은 옛 설정대로 숨김(2차 판 뜻 — 과목 화면)')
        ok(await ls(pg, 'sidefold') is True, f'{tag} 옛 LS sidefold 값 그대로')
        # flow V12 처음 M = 알림 하나
        await pg.evaluate("sessionStorage.removeItem('jblhub.v1.toasts')"); await pg.keyboard.press('m'); await pg.clock.run_for(400)
        L = await pg.evaluate("JSON.parse(sessionStorage.getItem('jblhub.v1.toasts')||'[]').map(x=>x.t)")
        ok(len(L) == 1 and 'M은 이제 메뉴' in L[0] and '펼쳤어요' in L[0], f'{tag} flow V12 옛 사용자 첫 M → 알림 하나 {L}')
        ok(not await pg.evaluate(FOLD) and await ls(pg, 'navfold') is False and await ls(pg, 'sidefold') is True, f'{tag} M → 펼침 · 새 키 navfold=false · 옛 sidefold 그대로')
        # F9: 정리표(자동 숨김) → M 보임 → M 숨김 → 학습·홈은 보임
        await boot(pg, '#/CONS/WHT/sum'); f0 = await pg.evaluate(FOLD)
        ok(f0 == (vp['width'] <= 1440), f'{tag} 정리표 자동 숨김 {f0}')
        await pg.keyboard.press('m'); await pg.clock.run_for(500); ok(not await pg.evaluate(FOLD) and await ls(pg, 'wideSide') == 1, f'{tag} 정리표 M → 보임 · wideSide 1')
        await pg.keyboard.press('m'); await pg.clock.run_for(500); ok(await pg.evaluate(FOLD) and await ls(pg, 'wideSide') == 0, f'{tag} 정리표 M → 숨김 · wideSide 0')
        await pg.evaluate("location.hash='#/CONS/WHT/learn'"); await pg.clock.run_for(800); ok(not await pg.evaluate(FOLD), f'{tag} F9 학습으로 → 메뉴 보임(새지 않음)')
        await pg.evaluate("location.hash='#/'"); await pg.clock.run_for(800); ok(not await pg.evaluate(FOLD), f'{tag} F9 홈 → 메뉴 보임')
        # V10: 학습에서 숨김 → 정리표에서 보이게 → 학습 → 정리표 다시 = 보임
        await pg.evaluate("location.hash='#/CONS/WHT/learn'"); await pg.clock.run_for(800); await pg.keyboard.press('m'); await pg.clock.run_for(500)
        ok(await pg.evaluate(FOLD) and await ls(pg, 'navfold') is True, f'{tag} 학습 M → 숨김(navfold)')
        await pg.evaluate("location.hash='#/'"); await pg.clock.run_for(800); ok(await pg.evaluate(FOLD), f'{tag} ux4 묶음2(B13) 숨김 설정 하나 — 학습에서 숨기면 홈도 숨김')
        await pg.evaluate("location.hash='#/CONS/WHT/learn'"); await pg.clock.run_for(800)
        await pg.evaluate("location.hash='#/CONS/WHT/sum'"); await pg.clock.run_for(800); await pg.keyboard.press('m'); await pg.clock.run_for(500)
        ok(not await pg.evaluate(FOLD), f'{tag} 정리표 M → 보임')
        await pg.evaluate("location.hash='#/CONS/WHT/learn'"); await pg.clock.run_for(800); await pg.evaluate("location.hash='#/CONS/WHT/sum'"); await pg.clock.run_for(800)
        ok(not await pg.evaluate(FOLD), f'{tag} V10 정리표 다시 → 펼친 그대로')
        ok(not errs, f'{tag} pageerror 0 {errs[:2]}')
        await ctx.close()
    ctx, pg, errs = await ctxpg(b, PORT, True); print('== F8 · V09 · flow V09 (820)')
    await fresh(pg, '#/CONS/WHT/learn', "localStorage.setItem('jblhub.v1.keyNoticeM','1')")
    await pg.keyboard.press('v'); await pg.clock.run_for(300); await pg.keyboard.press('m'); await pg.clock.run_for(400)
    r = await pg.evaluate("document.body.className")
    ok('focus' not in r.split() and 'navopen' in r.split(), f'F8 820 집중 모드에서 M → 집중 끔 · 서랍 열림 ({r})')
    sc = await pg.evaluate("(d=>d?[getComputedStyle(d).display,d.querySelectorAll('.scard2').length,d.getBoundingClientRect().height]:null)(document.querySelector('#side .nvtoc'))")
    ok(sc and sc[0] != 'none' and sc[1] > 3 and sc[2] > 100, f'V09 서랍에도 지금 강의 카드 목차(ux4 묶음2 — 늘 펼침) {sc}')
    await pg.screenshot(path=J.TMP + '/ux3f_nav_drawer_port.png')
    await pg.tap('#side .scard2[data-lj="3"]'); await pg.clock.run_for(900)
    ok(not await pg.evaluate("document.body.classList.contains('navopen')") and await pg.evaluate("__h.LCUR") == 3, f"서랍 카드 누름 → 서랍 닫고 카드 4로 (LCUR {await pg.evaluate('__h.LCUR')})")
    await ctx.close()
    for vp, tag in ((PORT, 'port'), (LAND, 'land')):
        ctx, pg, errs = await ctxpg(b, vp, True)
        await fresh(pg, '#/CONS/WHT/learn', "localStorage.setItem('jblhub.v1.keyNoticeM','1');localStorage.setItem('jblhub.v1.lastBy',JSON.stringify({CONS:{s:'CONS',d:'WHT',t:'learn',at:1}}))"); 
        if vp['width'] <= 860: await pg.evaluate("document.querySelector('#navbtn').click()"); await pg.clock.run_for(400)
        SM = """(sels)=>sels.map(s=>{const e=[...document.querySelectorAll(s)].find(x=>x.getClientRects().length);if(!e)return [s,0,0];const r=e.getBoundingClientRect();return [s,Math.round(r.width),Math.round(r.height)]})"""
        sz = await pg.evaluate(SM, ['#side .nvl', '#side .nvd', '#side .nvback', '#side .nvsw', '#bkup', '#side .scard2'])   # ux4d 바닥 '도움말'(.nvq) 뺌 → 바닥 백업 버튼 높이로   # ux4 묶음2 과목 메뉴(줄 40 · 목차·과목 바꾸기·‹ 36 · 바닥 44)
        bad = [x for x in sz if x[2] < (40 if x[0].endswith('bkup') else 36 if x[0].endswith(('scard2', 'nvsw', 'nvback')) else 40)]
        ok(not bad, f'{tag} flow V09 손가락 크기 {sz} 모자람 {bad}')
        await pg.evaluate("location.hash='#/_cal'"); await pg.clock.run_for(800)
        await pg.evaluate("document.querySelector('#calmset').open=true;document.querySelector('#cadd')&&(document.querySelector('#cadd').open=true)"); await pg.clock.run_for(200)
        sz = await pg.evaluate(SM, ['.calset label.tauto', '[data-caq="0"]'])
        ok(all(x[2] >= 44 for x in sz), f'{tag} 달력 설정 줄·0으로 44px {sz}')
        await ctx.close()
    print('== V04 강의 줄 · V08 칩 · flow V08 · F7 · V03 · V11 · V12')
    for vp, tag in ((MAC, 'mac'), (LAND, 'land'), ({'width': 1000, 'height': 800}, 'w1000')):
        ctx, pg, errs = await ctxpg(b, vp, vp is LAND)
        await fresh(pg, '#/ANAT/LIP/learn', "localStorage.setItem('jblhub.v1.keyNoticeM','1')")
        r = await pg.evaluate("""(()=>{const L=[...document.querySelectorAll('#nav .nvl')],i=L.findIndex(x=>x.hasAttribute('aria-current')),toc=document.querySelector('#nav .nvtoc');
          return {n:L.length,i,tocAfterCur:!!(toc&&L[i]&&L[i].nextElementSibling===toc),nextAfterToc:!!(toc&&L[i+1]&&toc.nextElementSibling===L[i+1])}})()""")
        ok(r['n'] == 7 and r['tocAfterCur'] and (r['i'] == r['n'] - 1 or r['nextAfterToc']), f'{tag} V04·ux4 카드 목차는 지금 강의 줄 바로 아래 {r}')
        await pg.screenshot(path=J.TMP + f'/ux3f_nav_lecs_{tag}.png')
        clip = []
        for S in ('OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM'):
            await pg.evaluate(f"__h.openDoc('{S}','_home')"); await pg.clock.run_for(300)
            clip += await pg.evaluate("[...document.querySelectorAll('#nav .nvd .el,#nav .nvsjn')].filter(e=>e.getClientRects().length&&e.scrollWidth>e.clientWidth+1).map(e=>e.closest('[data-s]')?.dataset.s+':'+e.textContent)")
        ok(not clip, f'{tag} V08 문서 칩 글자 잘림 0 {clip[:4]}')
        await ctx.close()
    ctx, pg, errs = await ctxpg(b, LAND, True)
    await fresh(pg, '#/', "localStorage.setItem('jblhub.v1.keyNoticeM','1')")
    wk = await pg.inner_text('#nav [data-nb="wk"]'); ok(wk.startswith('이번 주 '), f"V12 메뉴 달력 줄 '{wk}'")
    # F7 다른 창이 재는 동안(storage time·timed) 메뉴 노드 그대로 · 배지 갱신
    await pg.evaluate("window.__nv=document.querySelector('#nav .nvs[data-s=OMS1]');window.__mut=0;new MutationObserver(m=>{m.forEach(x=>{if(x.type==='childList'&&x.target.id==='nav')__mut++})}).observe(document.querySelector('#nav'),{childList:true})")
    for i in range(3):
        await pg.evaluate("i=>{const o=JSON.parse(localStorage.getItem('jblhub.v1.time')||'{}');o['%s']={OMS1:(i+1)*20*60000};localStorage.setItem('jblhub.v1.time',JSON.stringify(o));dispatchEvent(new StorageEvent('storage',{key:'jblhub.v1.time'}))}" % TODAY, i)
        await pg.clock.run_for(25000)
    r = await pg.evaluate("[__mut,window.__nv===document.querySelector('#nav .nvs[data-s=OMS1]'),document.querySelector('#nav [data-nb=wk]').textContent]")
    ok(r[0] == 0 and r[1] and r[2] == '이번 주 1:00', f'F7 다른 창 기록(storage time) 3번 → 메뉴 다시 그림 0 · 노드 그대로 · 이번 주 글자 {r}')
    # V03 색 거리
    cols = await pg.evaluate("['OMS1','CONS','IMPL','ANAT','GERI','PHARM'].map(k=>__h.sjColor(k))")
    dm = min(math.dist(lab(a), lab(c)) for a, c in itertools.combinations(cols, 2))
    ok(dm >= 20, f'V03 과목 색 서로 ΔE 최소 {dm:.1f} ≥ 20 {cols}')
    nd = await pg.evaluate("[...document.querySelectorAll('#nav .nvs:not(.off) .nvdot')].map(e=>getComputedStyle(e).backgroundColor)")
    ok(len(set(nd)) == len(nd) >= 6, f'메뉴 과목 점 색 서로 다름 {len(set(nd))}/{len(nd)}')
    # V11 대비
    await pg.evaluate("location.hash='#/'"); await pg.clock.run_for(800)
    c1 = await pg.evaluate(CONTRAST, '#home .hwb.fut .hwl'); c3 = await pg.evaluate(CONTRAST, '#side .nvs.off .nvst2,#side .nvs.off .nvsn')
    await pg.evaluate("location.hash='#/_cal'"); await pg.clock.run_for(800)
    c2 = await pg.evaluate(CONTRAST, '#calg .cc.out .cn,#calg .cc.fut .cn')
    ok(c1 and min(c1) >= 3.5 and c2 and min(c2) >= 3.5 and (not c3 or min(c3) >= 4.5), f'V11 대비 — 앞날 요일 {min(c1 or [0])} · 다른 달·앞날 날짜 {min(c2 or [0])} · 준비 중 {min(c3 or [9])}')
    await pg.screenshot(path=J.TMP + '/ux3f_cal_land.png')
    await pg.evaluate("location.hash='#/_time'"); await pg.clock.run_for(800)
    lg = await pg.evaluate("[...document.querySelectorAll('#calbody .tvlg span span, #calbody .tvs .nm')].map(e=>e.textContent.trim()).filter(Boolean)")
    ok(not any('임상' in x or '학' == x[-1:] for x in lg), f'V12 통계 = 짧은 과목 이름 {lg[:6]}')
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()

# ---------------- 표(F4): 칸 넘침 0 · 1280 영문 낱말 중간 끊김 0 (문제였던 강의) ----------------
TSCAN = r"""()=>{const out=[];const cells=[...document.querySelectorAll('#stage table td, #stage table th')].filter(c=>c.offsetParent);
 for(const c of cells){const w=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);let t;while(t=w.nextNode()){const re=/[A-Za-z][A-Za-z\-]{3,}/g;let m;while(m=re.exec(t.nodeValue)){const r=document.createRange();r.setStart(t,m.index);r.setEnd(t,m.index+m[0].length);const rs=[...r.getClientRects()].filter(x=>x.width>0);
  if(rs.length>1&&Math.abs(rs[0].top-rs[rs.length-1].top)>4&&m[0].indexOf('-')<0&&!t.parentElement.closest('.lw.hy'))out.push('BRK:'+m[0]);}}
 if(c.scrollWidth>c.clientWidth+1)out.push('OVF:'+c.textContent.slice(0,20));}return out;}"""
async def part_tbl(b):
    # ux3 fix2 F4 — 세 폭 모두 낱말 중간 끊김 0('(' 앞·'→'·'/' 뒤 줄바꿈 자리 · 칸보다 긴 13자↑ 낱말은 .lw.hy 하이픈 — 끊김으로 안 셈) · 옛 검증에서 끊기던 강의 포함
    for vp, tag in ((MAC, 'mac'), (LAND, 'land'), (PORT, 'port')):
        ctx = await b.new_context(viewport=vp, has_touch=vp is not MAC); pg = await ctx.new_page(); print('== F4 표', tag)
        for sk in ('PHARM/DS/sum', 'IMPL/PRO/sum', 'CONS/INL/sum', 'CONS/FRC/sum', 'OMS1/LOAD/sum', 'IMPL/OSS/sum', 'ANAT/LIP/sum', 'CONS/CRK/tbl', 'GERI/BLE/sum', 'PHARM/CHR/sum', 'IMPL/HIS/sum', 'PHARM/HM/sum', 'GERI/PAIN/tbl', 'CONS/ADH/sum'):
            await pg.goto('about:blank'); await pg.goto(U + f'#/{sk}', timeout=120000)
            await pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#stage table')", timeout=90000); await pg.wait_for_timeout(1200)
            r = await pg.evaluate(TSCAN); ovf = [x for x in r if x.startswith('OVF')]; brk = [x for x in r if x.startswith('BRK')]
            ok(not ovf and not brk, f'{tag} {sk} 표 칸 넘침 {len(ovf)} · 낱말 끊김 {len(brk)} {r[:3]}')
        await pg.screenshot(path=J.TMP + f'/ux3f_tbl_{tag}.png'); await ctx.close()

# ---------------- F6 줄인 기록(세션 정리·휴식 지움·📖)은 tedit trim — 줄이기 전 백업을 합쳐도 되살아나지 않음 ----------------
SNAP = "(()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.indexOf('jblhub.v1.')===0)o[k]=localStorage.getItem(k);}return o;})()"
async def part_mrg(b):
    ctx, pg, errs = await ctxpg(b, MAC); print('== F6 줄인 기록 + 옛 백업 합치기')
    await fresh(pg, '#/CONS/WHT/learn', "localStorage.setItem('jblhub.v1.tauto','false');")
    t = await pg.evaluate("Date.now()")
    await pg.evaluate("t=>__h.tRec('CONS','WHT',t-40*60000,t-10*60000,'s')", t)
    snap = await pg.evaluate(SNAP); c0 = await sub(pg, TODAY, 'CONS')
    tm0 = await pg.evaluate("localStorage.getItem('jblhub.v1.time')")
    await pg.evaluate("t=>__h.tUnrec('CONS','WHT',t-30*60000,t-10*60000,'s')", t)   # '마지막 입력 때 멈춤' — 뒤 20분 되돌림
    c1 = await sub(pg, TODAY, 'CONS'); ok(c0 - c1 == 20 * MIN, f'세션 뒤 20분 되돌림 → 보존 −{(c0 - c1) / MIN:.0f}분')
    ok(await pg.evaluate("localStorage.getItem('jblhub.v1.time')") == tm0, 'time은 그대로(tedit trim에 −)')
    ok(await pg.evaluate("__h.tLec('%s')['CONS:WHT']" % TODAY) == 10 * MIN, 'tLec 강의도 −20')
    await pg.evaluate("d=>__h.mergeData(d)", snap)
    ok(await sub(pg, TODAY, 'CONS') == c1, f'되돌리기 전 백업 합치기 → 보존 그대로 {c1 / MIN:.0f}분 ({(await sub(pg, TODAY, "CONS")) / MIN:.0f})')
    # 휴식 30분 → 📖(tUnrec r) → 옛 백업 합치기 → 휴식 0 그대로
    await pg.evaluate("t=>__h.tRec('','',t-9*60000,t-60000,'ra')", t); snap2 = await pg.evaluate(SNAP)
    ok(await pg.evaluate("__h.restDay('%s')" % TODAY) == 8 * MIN, '휴식 8분')
    await pg.evaluate("t=>__h.tUnrec('','',t-9*60000,t-60000,'r')", t)
    ok(await pg.evaluate("__h.restDay('%s')" % TODAY) == 0, '휴식 되돌림 → 0')
    await pg.evaluate("d=>__h.mergeData(d)", snap2)
    rd = await pg.evaluate("__h.restDay('%s')" % TODAY); ok(rd == 0, f'옛 백업 합치기 → 휴식 0 그대로 ({rd})')
    # 있는 만큼만 뺌 — 기록보다 큰 되돌림이 음수로 남아 뒤 공부를 삼키지 않음
    await pg.evaluate("t=>__h.tUnrec('CONS','WHT',t-200*60000,t-100*60000,'s')", t)
    c2 = await sub(pg, TODAY, 'CONS'); ok(c2 == 0, f'기록(10분)보다 큰 되돌림 → 0 ({c2 / MIN:.0f})')
    await pg.evaluate("t=>__h.tRec('CONS','WHT',t-5*60000,t,'a')", t)
    ok(await sub(pg, TODAY, 'CONS') == 5 * MIN, f'뒤 공부 5분은 그대로 +5 ({(await sub(pg, TODAY, "CONS")) / MIN:.1f})')
    # 고친 기록(통계)에는 trim이 안 보임
    await boot(pg, '#/_time')
    h = await pg.evaluate("(e=>e?e.textContent:'')(document.querySelector('.tehist'))")
    ok('−' not in h, f"고친 기록에 자동 정리(trim) 없음 {h[:60]!r}")
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()

async def main():
    only = _sys.argv[1:]
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for nm, fn in (('trk', part_trk), ('cal', part_cal), ('mrg', part_mrg), ('nav', part_nav), ('tbl', part_tbl)):
            if not only or nm in only: await fn(b)
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
