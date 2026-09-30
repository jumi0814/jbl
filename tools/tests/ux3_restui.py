"""ux3 R1·R3 회귀 — 쉬는 시간 타이머 표시(참고 HUB 트래커 위젯·집중 모드)와 과목 색 한 가지. (ux4 묶음2: 메뉴 트래커·#tmr → 상단 시계 알약 #clock·팝오버 #tpop)
R1 ① 시계 팝오버 '⏱ 크게 보기 · 지금 구간': 공부 중 = 이번 집중 h:mm:ss(세션 f0·자동 T.f0 — 1초마다 흐름) · 쉬는 중 = 이번 휴식 m:ss
   ② ⏱ 크게 → #bigclock: 쉬는 중 = 큰 휴식 구간·휴식 색(.rest) · 공부 중 = '● 집중 중' 큰 집중 구간 · 작은 줄 오늘 공부·휴식·목표 %
   ③ 쉬는 중 시계 알약 #clock.rest — 금색 점 · 글자 '휴식 m:ss'(지금 휴식 구간, 흐름) · 숫자는 오늘 공부 합계 그대로 · 홈·과목·자동 휴식(무활동) 모두 같음
   ④ 홈 오늘 띠·달력 상태 카드·팝오버 머리·휴식 요약 줄의 휴식 = restStats() ⑤ 자동 휴식에서 돌아와 띠 10초 뒤 '☕ 휴식 n분으로 기록했어요 [📖 공부로 바꾸기]'
R3 팩 color = SJC = sjColor · 메뉴 점·홈 과목표 점·과목 홈 --hero1·--acc 같은 색 · 흰 글자 대비 ≥4.5
맥 1280×900 · 아이패드 세로 820×1180 · 가로 1180×820(터치). 스크린샷 work/_tmp/ux3p_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime, math, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
NOW = datetime.datetime(2026, 9, 24, 10, 0, 0); MIN = 60000
def fmtH(ms):
    m = int(math.floor(max(0, ms) / 60000)); return f'{m // 60}:{m % 60:02d}'   # ux4c 1회차 fmtH = 분 내림
async def boot(pg, h, ms=1500):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.clock.run_for(ms)
async def fresh(pg, h):
    await boot(pg, h); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await boot(pg, h)
async def lab(pg): return await pg.evaluate("document.querySelector('#clock .ckl').textContent")
async def st(pg): return await pg.evaluate("document.querySelector('#clock').dataset.st")
async def pop(pg):   # 팝오버를 열어(열려 있으면 그대로) 글자 — 알약·팝오버 누름은 측정 상태를 바꾸지 않음(TRKSEL)
    return await pg.evaluate("(()=>{const p=document.querySelector('#tpop');if(!p.classList.contains('on'))document.querySelector('#clock').click();return {seg:(p.querySelector('[data-tpt=seg]')||{}).textContent||'',rest:(p.querySelector('[data-tpt=rest]')||{}).textContent||'',rv:(p.querySelector('[data-tpt=rv]')||{}).textContent||'',rl:(p.querySelector('.trrl')||{}).textContent||'',rows:[...p.querySelectorAll('[data-tp]')].map(b=>b.dataset.tp)}})()")
async def popx(pg): await pg.evaluate("document.querySelector('#tpop').classList.remove('on')")
async def toast(pg): return await pg.evaluate("(t=>t&&getComputedStyle(t).display!=='none'?t.textContent:'')(document.querySelector('#toast'))")

async def part_view(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print(f'== {tag} {vp}')
    await pg.clock.install(time=NOW)
    await fresh(pg, '#/CONS/WHT/learn')
    # ① 세션 25분 → 지금 구간(집중)
    await pg.evaluate("__h.trStart()"); await pg.clock.run_for(25 * MIN + 5000)
    a = (await pop(pg))['seg']; await pg.clock.run_for(2000); a2 = (await pop(pg))['seg']
    ok(re.fullmatch(r'지금 구간 0:25:0\d', a) and a2 != a, f'세션 25분 → 팝오버 지금 구간 {a!r} → 2초 뒤 {a2!r}')
    ok((await pop(pg))['rows'][:3] == ['stop', 'rest', 'big'] and (await lab(pg)).startswith('세션 0:25'), f"알약 {await lab(pg)!r} · 팝오버 [■][☕][⏱ 크게]")
    await pg.screenshot(path=J.TMP + f'/ux3p_t_study_{tag}.png', clip={'x': 0, 'y': 0, 'width': vp['width'], 'height': 360})
    await pg.evaluate("document.querySelector('#tpop [data-tp=big]').click()"); await pg.clock.run_for(1100)
    bl, bt, bs = await pg.inner_text('#bcl'), await pg.inner_text('#bct'), await pg.inner_text('#bcs')
    ok(bl == '● 집중 중' and bt.startswith('0:25:') and '오늘 공부 0:25' in bs and '세션 0:25' in bs and '목표' in bs, f'⏱ 크게(공부 중) {bl!r} {bt!r} {bs!r}')
    await pg.evaluate("document.querySelector('[data-bigx]').click()"); await pg.clock.run_for(200)
    # ② ☕ 쉬기 4분
    await pg.evaluate("__h.trRest()"); await pg.clock.run_for(4 * MIN + 10000)
    R = await pg.evaluate("__h.restStats()")
    ck = await pg.evaluate("(c=>[c.classList.contains('rest'),c.querySelector('.ckl').textContent,getComputedStyle(c.querySelector('.ckd')).backgroundColor,c.querySelector('.ckt').textContent])(document.querySelector('#clock'))")
    ok(ck[0] and re.fullmatch(r'휴식 4:[0-2]\d', ck[1]) and ck[2] == 'rgb(183, 121, 31)' and ck[3].startswith('0:25:'), f'알약 휴식 — 금색 점·지금 휴식 구간·공부 합계 그대로 {ck}')
    await pg.clock.run_for(2000); ok((await lab(pg)) != ck[1], f'쉬는 동안 휴식 타이머가 흐름 {ck[1]!r} → {await lab(pg)!r}')
    P = await pop(pg)
    ok(P['rows'][:2] == ['resume', 'stop'] and P['seg'] == '' and re.fullmatch(r'지금 휴식 4:[0-2]\d', P['rest']) and P['rv'] == fmtH(R['ms']) and '오늘 휴식' in P['rl'] and '%' not in P['rl'],   # ux4d 집중 % 없음
       f'쉬는 중 팝오버 [▶ 다시 — 지금 휴식 m:ss][■] · 지금 구간 중복 없음(ux4c 2회차) · 오늘 휴식 = restStats {P}')
    await pg.screenshot(path=J.TMP + f'/ux3p_t_rest_{tag}.png', clip={'x': 0, 'y': 0, 'width': vp['width'], 'height': 360})
    await pg.evaluate("document.querySelector('#tpop [data-tp=big]').click()"); await pg.clock.run_for(1100)
    bl, bt, bs = await pg.inner_text('#bcl'), await pg.inner_text('#bct'), await pg.inner_text('#bcs')
    cls = await pg.evaluate("document.querySelector('#bigclock').className")
    ok(bl == '☕ 쉬는 중' and re.fullmatch(r'4:[0-2]\d', bt) and bs.startswith('오늘 휴식 0:04 · 공부 0:25') and 'rest' in cls, f'⏱ 크게(쉬는 중) {bl!r} {bt!r} {bs!r} {cls!r}')
    await pg.screenshot(path=J.TMP + f'/ux3p_t_big_{tag}.png')
    await pg.evaluate("document.querySelector('[data-bigx]').click()"); await pg.clock.run_for(200)
    # ③④ 홈 — 알약 글자 · 오늘 띠 휴식 = restStats
    await pg.evaluate("location.hash='#/'"); await pg.clock.run_for(1200)
    ok(re.fullmatch(r'휴식 4:\d\d', await lab(pg)) and await pg.evaluate("getComputedStyle(document.querySelector('#clock'),'::before').content") in ('none', 'normal'), f"홈 알약 {await lab(pg)!r} · 옛 앞말(::before) 없음")
    R = await pg.evaluate("__h.restStats()")
    bv = await pg.evaluate("(e=>e?e.textContent:'')(document.querySelector('#home .hband .trrv'))")
    ok(bv == fmtH(R['ms']), f'홈 오늘 띠 휴식 {bv!r} = restStats {fmtH(R["ms"])}')
    await pg.screenshot(path=J.TMP + f'/ux3p_t_home_{tag}.png', clip={'x': 0, 'y': 0, 'width': vp['width'], 'height': 320})
    await pg.evaluate("location.hash='#/_cal'"); await pg.clock.run_for(1200)
    cr = await pg.inner_text('#cc-rest'); R = await pg.evaluate("__h.restStats()"); P = await pop(pg); await popx(pg)
    ok(cr == fmtH(R['ms']) and P['rv'] == fmtH(R['ms']), f'달력 상태 카드 휴식 {cr!r} = 팝오버 {P["rv"]!r} = restStats')
    # ▶ 다시 → 집중 0부터 · ■ → 멈춤
    await pg.evaluate("location.hash='#/CONS/WHT/learn'"); await pg.clock.run_for(1000)
    await pg.evaluate("__h.trResume()"); await pg.clock.run_for(3000)
    a = (await pop(pg))['seg']; await popx(pg); ok(re.fullmatch(r'지금 구간 0:00:0\d', a), f'▶ 다시 → 집중 0부터 {a!r}')
    ok(not await pg.evaluate("document.querySelector('#clock').classList.contains('rest')"), '▶ 다시 → 알약 휴식 색 풀림')
    await pg.evaluate("__h.trStop()"); await pg.clock.run_for(1200)
    P = await pop(pg); await popx(pg)
    ok(await lab(pg) == '멈춤' and re.fullmatch(r'0:0[45]', P['rv']) and P['seg'] == '', f"■ 뒤 알약 {await lab(pg)!r} · 팝오버 휴식 {P['rv']!r}")
    # ⑤ 자동 측정 → 무활동 → 자동 휴식(같은 표시) → 돌아와 띠 → 기록 알림
    await fresh(pg, '#/CONS/WHT/learn')
    for i in range(21):
        await pg.mouse.move(300 + (i % 9) * 11, 420 + (i % 3)); await pg.clock.run_for(30000)
    fm = await pg.evaluate("__h.trFocusMs()")
    ok(await st(pg) == 'run' and await lab(pg) == '공부 중' and 10 * MIN <= fm < 11 * MIN, f'자동 측정 10분 → {await st(pg)} {await lab(pg)!r} · 지금 구간 {fm / MIN:.1f}분')
    await pg.clock.run_for(9 * MIN)
    ck = await pg.evaluate("(c=>[c.classList.contains('rest'),c.querySelector('.ckl').textContent])(document.querySelector('#clock'))")
    ok(await st(pg) == 'rest' and ck[0] and ck[1].startswith('휴식 '), f'무활동 → 자동 휴식 표시 {await st(pg)} {ck}')
    await pg.screenshot(path=J.TMP + f'/ux3p_t_auto_{tag}.png', clip={'x': 0, 'y': 0, 'width': vp['width'], 'height': 260})
    await pg.clock.run_for(15 * MIN); await pg.mouse.move(640, 500); await pg.clock.run_for(300)
    bd = await pg.evaluate("(b=>b.hidden?'':b.textContent)(document.querySelector('#idleband'))")
    ok('쉬었어요' in bd and '공부했어요' in bd, f'돌아와 입력 → 띠 {bd!r}')
    await pg.clock.run_for(10500); t = await toast(pg)
    ok(re.search(r'☕ 휴식 \d+분으로 기록했어요', t) and '공부로 바꾸기' in t, f'10초 뒤 기록 알림 {t!r}')
    ok(not await pg.evaluate("document.querySelector('#clock').classList.contains('rest')") and await lab(pg) in ('공부 중', '대기'), f'돌아온 뒤 알약 {await lab(pg)!r}')
    # R3 과목 색 한 가지
    await pg.evaluate("location.hash='#/'"); await pg.clock.run_for(1200)
    r = await pg.evaluate("""()=>{const hex=c=>'#'+c.match(/\\d+/g).slice(0,3).map(x=>(+x).toString(16).padStart(2,'0')).join('').toUpperCase(),bad=[];
      Object.keys(__h.PACKS).forEach(k=>{const c=__h.sjColor(k).toUpperCase();if(__h.PACKS[k].color.toUpperCase()!==c||(__h.SJC[k]||'').toUpperCase()!==c)bad.push(k+' pack/SJC');
       const n=document.querySelector(`#nav .nvs[data-s="${k}"] .nvdot`),h=document.querySelector(`#home .hsj[data-s="${k}"] .hdot`);
       if(!n||hex(getComputedStyle(n).backgroundColor)!==c)bad.push(k+' nav');if(!h||hex(getComputedStyle(h).backgroundColor)!==c)bad.push(k+' home');});return bad;}""")
    ok(not r, f'R3 팩 color = SJC = 메뉴 점 = 홈 과목표 점 {r}')
    for s in ['OMS1', 'PHARM']:
        await pg.evaluate(f"location.hash='#/{s}/_home'"); await pg.clock.run_for(900)
        h = await pg.evaluate("s=>[getComputedStyle(document.documentElement).getPropertyValue('--hero1').trim().toUpperCase(),getComputedStyle(document.documentElement).getPropertyValue('--acc').trim().toUpperCase(),__h.sjColor(s).toUpperCase()]", s)
        ok(h[0] == h[1] == h[2], f'R3 {s} 과목 홈 hero·--acc = sjColor {h}')
    if tag == 'mac':
        await pg.evaluate("location.hash='#/PHARM/_home'"); await pg.clock.run_for(900)
        await pg.screenshot(path=J.TMP + '/ux3p_t_hero_pharm.png', clip={'x': 0, 'y': 0, 'width': 1280, 'height': 400})
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), '가로 넘침 0')
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await part_view(b, {'width': 1280, 'height': 900}, False, 'mac')
        await part_view(b, {'width': 820, 'height': 1180}, True, 'ipp')
        await part_view(b, {'width': 1180, 'height': 820}, True, 'ipl')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
