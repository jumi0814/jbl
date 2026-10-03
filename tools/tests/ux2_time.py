"""B01~B05 회귀(무활동 되묻기·창 여러 개는 LS restAuto=false — 쉬는 시간 자동 측정을 끈 옛 흐름, 켠 흐름은 ux3_rest): 공부 시간 — 📊 공부 기록 화면(#/_time — ux3부터 📅 공부 달력의 [📊 통계] 탭)·시계 팝업·허브 홈 시간 표·측정 표시(되감기 없음·자리 비움)·무활동 되묻기·창 여러 개.
가짜 시계(page.clock)로 2026-09-24(목) 기준 14일치 합성 기록(time·timed, 3과목)을 넣고 확인한다.
맥 1280×900 + 아이패드 세로 820×1180 + 가로 1180×820. 스크린샷 work/_tmp/ux2i_b0*_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime, math
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
NOW = datetime.datetime(2026, 9, 24, 10, 0, 0)          # 목요일 — 이번 주 = 9/21(월)~9/27(일)
D = lambda i: (NOW - datetime.timedelta(days=i)).strftime('%Y-%m-%d')   # i일 전
def fmtH(ms):
    m = int(math.floor(max(0, ms) / 60000)); return f'{m // 60}:{m % 60:02d}'   # ux4c 1회차 fmtH = 분 내림
MIN = 60000
async def ls(pg, k):
    v = await pg.evaluate(f"localStorage.getItem('jblhub.v1.{k}')"); return json.loads(v) if v else None
async def boot(pg, h, ms=1800):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.clock.run_for(ms)
    for _ in range(150):   # 팩(과목 자료) 도착까지 — 느린 컴퓨터(클라우드)에서는 1.8초 안에 다 못 받음(가짜 시계와 별개로 실제 읽기 시간)
        if await pg.evaluate("!!(window.__h&&__h.plStat&&__h.plStat().pend===0)"): break
        await pg.wait_for_timeout(100); await pg.clock.run_for(100)

def synth(lec):
    """14일(오늘 포함) × OMS1·CONS·PHARM · 분 단위 · 강의별(timed)은 과목 시간을 강의 키에 나눠 담고 비학습 화면(_home)도 조금"""
    time, timed = {}, {}
    for i in range(14):
        d = D(i); o = {'OMS1': (10 + (i * 7) % 50) * MIN, 'CONS': ((i * 13) % 40) * MIN}
        if i % 3 == 0: o['PHARM'] = 30 * MIN
        o = {k: v for k, v in o.items() if v}; time[d] = o; td = {}
        for s, v in o.items():
            ks = lec[s]; a = ks[i % len(ks)]; b = ks[(i + 1) % len(ks)]
            td[s + ':' + a] = v * 2 // 3; td[s + ':' + b] = v - v * 2 // 3 - MIN if v > 2 * MIN else v - v * 2 // 3
            if v > 2 * MIN: td[s + ':_home'] = MIN
        timed[d] = td
    return time, timed

async def part_view(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== B01·B02', tag)
    await pg.clock.install(time=NOW)
    await boot(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    lec = await pg.evaluate("Object.fromEntries(['OMS1','CONS','PHARM'].map(s=>[s,__h.PACKS[s].lect.map(L=>L.k)]))")
    time, timed = synth(lec)
    time[D(0)]['GERI'] = 20000                      # 20초 — 목록에서 숨김(1분 미만)
    await pg.evaluate("([a,b])=>{localStorage.setItem('jblhub.v1.time',JSON.stringify(a));localStorage.setItem('jblhub.v1.timed',JSON.stringify(b));localStorage.setItem('jblhub.v1.tauto','false');}", [time, timed])
    raw_time = await pg.evaluate("localStorage.getItem('jblhub.v1.time')")
    day_sum = lambda d: sum(time.get(d, {}).values())
    # ---- B01 공부 기록 화면
    await boot(pg, '#/_time')
    ds = await pg.evaluate("[...document.querySelectorAll('#home .tvb')].map(b=>b.dataset.tvd)")
    wk = [(NOW - datetime.timedelta(days=3) + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    ok(ds == wk, f'막대 7개 월~일 순서 {ds[:2]}…{ds[-1:]}')
    tot = sum(day_sum(d) for d in wk)
    sm = await pg.inner_text('#tvsum'); ok(f'이번 주 {fmtH(tot)}' in sm, f'이번 주 합계 {fmtH(tot)} ({sm[:60]!r})')
    ems = await pg.evaluate("[...document.querySelectorAll('#home .tvb')].map(b=>(b.querySelector('em')||{}).textContent||'')")
    exp = [fmtH(day_sum(d)) if day_sum(d) >= 30000 else '' for d in wk]
    ok(ems == exp, f'막대 위 h:mm = 날마다 합 {ems} vs {exp}')
    ok(await pg.evaluate("document.querySelectorAll('#home .tvb.today').length===1&&document.querySelector('#home .tvb.today').dataset.tvd") == D(0), '오늘 막대 테두리 하나')
    ok(await pg.evaluate("!!document.querySelector('#home .tvplot .goal')&&getComputedStyle(document.querySelector('#home .tvplot .goal')).borderTopStyle==='dashed'"), '목표선 점선')
    ok(await pg.evaluate("document.querySelectorAll('#home .hmg .hm').length") == 84, '12주 잔디 84칸')
    await pg.screenshot(path=J.TMP + f'/ux2i_b01_week_{tag}.png')
    await pg.evaluate("document.querySelector('#home [data-tvd=\"%s\"]').click()" % D(1)); await pg.clock.run_for(100)
    t = await pg.inner_text('#tvday'); ok(fmtH(day_sum(D(1))) in t and '과목 홈' not in t, f'막대 누르면 그날 목록(비학습 화면 없음) {t[:50]!r}')
    # 강의 상위 10 (전체)
    acc = {}
    for d, o in timed.items():
        for k, v in o.items():
            if not k.endswith(':_home') and v >= 30000: acc[k] = acc.get(k, 0) + v
    top = [fmtH(v) for k, v in sorted(acc.items(), key=lambda x: -x[1])[:10]]
    got = await pg.evaluate("[...document.querySelectorAll('#home .tvlec tbody tr')].map(r=>r.querySelector('td.t').textContent)")
    ok(got == top, f'강의 상위 10 정렬 {got[:4]} vs {top[:4]}')
    # ◀ 지난주
    await pg.evaluate("document.querySelector('#home [data-tvw=\"-1\"]').click()"); await pg.clock.run_for(100)
    pw = [(NOW - datetime.timedelta(days=10) + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    ptot = sum(day_sum(d) for d in pw); sm = await pg.inner_text('#tvsum')
    ok(f'이 주 {fmtH(ptot)}' in sm and await pg.evaluate("[...document.querySelectorAll('#home .tvb')].map(b=>b.dataset.tvd)") == pw, f'◀ 지난주 합 {fmtH(ptot)} ({sm[:40]!r})')
    await pg.evaluate("document.querySelector('#home [data-tvw=\"0\"]').click()"); await pg.clock.run_for(100)
    # 시간 고치기 +30분 (9/23)
    d1 = D(1); before = await pg.evaluate("document.querySelector('#home [data-tvd=\"%s\"] em').textContent" % d1)
    await pg.evaluate("document.querySelector('#home details.tvadj').open=true")
    await pg.fill('#tvad', d1); await pg.select_option('#tvas', 'CONS'); await pg.fill('#tvam', '30')
    await pg.evaluate("document.querySelector('#home [data-tvadj=\"1\"]').click()"); await pg.clock.run_for(100)
    after = await pg.evaluate("document.querySelector('#home [data-tvd=\"%s\"] em').textContent" % d1)
    ok(after == fmtH(day_sum(d1) + 30 * MIN) and before == fmtH(day_sum(d1)), f'tadj +30분 → 그날 막대 {before} → {after}')
    ok(await pg.evaluate("localStorage.getItem('jblhub.v1.time')") == raw_time, 'time 키 값은 그대로')
    te = await ls(pg, 'tedit') or []   # ux3 I5: 손 고침은 tadj 대신 tedit(추가 전용 원장)
    ok(len(te) == 1 and te[0]['d'] == d1 and te[0]['S'] == 'CONS' and te[0]['ms'] == 30 * MIN and te[0]['k'] == 'set' and await ls(pg, 'tadj') is None, f'고친 시간 = tedit 한 항목 · tadj 쓰지 않음 {te}')
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), '가로 넘침 0')
    await pg.evaluate("scrollTo(0,document.body.scrollHeight)"); await pg.screenshot(path=J.TMP + f'/ux2i_b01_bottom_{tag}.png')
    # ---- B02 시계 팝업·허브 홈 시간 표
    await boot(pg, '#/')
    await pg.click('#clock'); await pg.clock.run_for(200)
    rows = await pg.evaluate("[...document.querySelectorAll('#tpop [data-tp]')].map(b=>b.dataset.tp)")   # ux4 묶음2: 시계 팝오버 = 버튼 줄(주 막대·과목별은 📅 달력·📊 통계)
    ok(rows[-3:] == ['big', 'cal', 'goal'] and '/ 4:00' in await pg.inner_text('#tpop .ph'), f'팝오버 [⏱ 크게][달력][목표] · 머리 오늘/목표 {rows}')
    pt = await pg.inner_text('#tpop')
    ok('0분' not in pt and '노인' not in pt and '과목 홈' not in pt, f'팝업: 0분·1분 미만 과목·비학습 줄 없음')
    await pg.screenshot(path=J.TMP + f'/ux2i_b02_pop_{tag}.png')
    await pg.keyboard.press('Escape')
    await boot(pg, '#/_time')   # ux3 H1 '최근 공부 시간' 표는 허브 홈 → 📅 달력 [📊 통계] 탭
    ht = await pg.inner_text('#home .htime')
    first = await pg.evaluate("document.querySelector('#home .htime tbody tr th').textContent")
    ok(first == '9/24(목)' and '0분' not in ht, f'통계 탭 최근 공부 시간 첫 행 = 최신 날짜 {first} · 0분 없음')
    ok(await pg.evaluate("document.querySelectorAll('#home .htime tbody tr').length") <= 7, '표 7행 이하')
    await boot(pg, '#/')
    bt = await pg.inner_text('#home .hband'); wk = await pg.inner_text('#home .hweek')
    ok('오늘' in bt and '이번 주' in wk, f"허브 홈 '오늘' 띠·이번 주 {bt[:30]!r}")
    await pg.evaluate("document.querySelector('#home .hband [data-tvgo2]').click()"); await pg.clock.run_for(300)
    ok(await pg.evaluate("location.hash") == '#/_cal', "'오늘' 띠 → #/_cal(📅 공부 달력)")
    await pg.go_back(); await pg.clock.run_for(300); ok(await pg.evaluate("!!document.querySelector('#home .hub .hsj')"), '뒤로 → 허브 홈')
    await boot(pg, '#/PHARM/_home')
    ok('이 과목 달력' in await pg.inner_text('#hprog') and await pg.evaluate("!!document.querySelector('#hprog h2 [data-tvgo2]')"), '과목 홈 진행률 절 제목 오른쪽에 이 과목 달력 링크(ux3 H6 · ux4 B3-3 크롬 이모지 없음)')
    await pg.evaluate("document.querySelector('#hprog [data-tvgo2]').click()"); await pg.clock.run_for(300)
    ok(await pg.evaluate("location.hash") == '#/_cal?s=PHARM', '과목 홈 → #/_cal?s=PHARM(과목 필터)')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def part_clock(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== B03·B04 측정 표시·무활동')
    await pg.clock.install(time=NOW)
    await boot(pg, '#/OMS1/DD1/learn'); await pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.restAuto','false')"); await boot(pg, '#/OMS1/DD1/learn', 1200)   # ux3 J9: 옛 되묻기 띠(무활동 → [공부했어요][빼기])는 '쉬는 시간 재기'를 끈 때의 흐름 — 새 흐름은 tests/ux3_rest.py
    clk = lambda: pg.inner_text('#clock .ckt')   # ux4 묶음2 알약의 오늘 합계(h:mm:ss)
    sec = lambda t: (lambda a: int(a[0]) * 3600 + int(a[1]) * 60 + int(a[2]))(t.strip().split(':'))
    await pg.mouse.move(400, 400); await pg.mouse.wheel(0, 1)
    for i in range(3):
        await pg.clock.run_for(10000)
        if i < 2: await pg.mouse.move(410 + i * 10, 400); await pg.mouse.wheel(0, 1)   # 0·10·20초에 입력 → 마지막 입력 20초
    t30 = await clk(); ok(29 <= sec(t30) <= 30 and await pg.evaluate("document.querySelector('#clock').dataset.st") == 'run', f"30초 → {t30} · ● 측정 중")
    seq = [sec(await clk())]
    for _ in range(270):   # 무활동 4분 30초 — 1초마다 읽어 되감기지 않음
        await pg.clock.run_for(1000); seq.append(sec(await clk()))
    ok(seq[-1] <= 20 + 60 and (await pg.inner_text('#clock .ckl')).startswith('자리 비움'), f"5분 무활동 → {await clk()} (마지막 입력 20초 + 1분 이내) · 알약 '{await pg.inner_text('#clock .ckl')}'")
    for _ in range(240):
        await pg.clock.run_for(1000); seq.append(sec(await clk()))
    ok(all(a <= b for a, b in zip(seq, seq[1:])), f'9분 동안 1초마다 읽은 값이 줄지 않음 ({seq[0]}→{seq[-1]})')
    ok(await pg.evaluate("document.querySelector('#clock').dataset.st") != 'run', '기준(8분) 넘으면 멈춤')
    await pg.screenshot(path=J.TMP + '/ux2i_b03_idle_mac.png', clip={'x': 0, 'y': 0, 'width': 1280, 'height': 60})
    # B04: 입력이 없은 지 12분 → 입력 → 띠 → [공부했어요]
    await pg.clock.run_for(12 * MIN - 540000 + 20000)   # 마지막 입력(20초)에서 12분 뒤로
    tm0 = sum((await ls(pg, 'time') or {}).get('2026-09-24', {}).values())
    await pg.mouse.move(500, 500); await pg.mouse.wheel(0, 1); await pg.clock.run_for(300)
    band = await pg.evaluate("(()=>{const b=document.querySelector('#idleband');return b.hidden?'':b.textContent})()")
    ok('입력이 없었어요' in band and '공부했어요' in band, f'12분 무활동 뒤 입력 → 띠 {band!r}')
    await pg.screenshot(path=J.TMP + '/ux2i_b04_band_mac.png')
    await pg.evaluate("document.querySelector('#idleband [data-ib=add]').click()"); await pg.clock.run_for(200)
    tm1 = sum((await ls(pg, 'time') or {}).get('2026-09-24', {}).values())
    ok(abs((tm1 - tm0) - 12 * MIN) <= MIN + 1000, f'[공부했어요] → time +{(tm1 - tm0) / MIN:.1f}분 (12분 ±1)')
    # [빼기]·10초 경과 → 변화 없음
    for how in ('no', 'wait'):
        await pg.clock.run_for(9 * MIN); await pg.clock.run_for(3 * MIN)
        a0 = sum((await ls(pg, 'time') or {}).get('2026-09-24', {}).values())
        await pg.mouse.move(520 if how == 'no' else 540, 500); await pg.mouse.wheel(0, 1); await pg.clock.run_for(300)
        vis = await pg.evaluate("!document.querySelector('#idleband').hidden")
        if how == 'no': await pg.evaluate("document.querySelector('#idleband [data-ib=no]').click()")
        else: await pg.clock.run_for(10500)
        await pg.clock.run_for(200); a1 = sum((await ls(pg, 'time') or {}).get('2026-09-24', {}).values())
        ok(vis and a1 - a0 <= 1000 and await pg.evaluate("document.querySelector('#idleband').hidden"), f"{'[빼기]' if how == 'no' else '10초 경과'} → 띠 닫힘·변화 없음 (+{(a1 - a0) / 1000:.0f}초)")
    # idleMin=15 → 12분에는 멈추지 않음
    await pg.evaluate("localStorage.setItem('jblhub.v1.idleMin','15')")
    await pg.mouse.move(560, 500); await pg.mouse.wheel(0, 1); await pg.clock.run_for(12 * MIN)
    ok(await pg.evaluate("document.querySelector('#clock').dataset.st") == 'run', 'idleMin 15 → 12분 무활동에도 측정 중')
    await pg.mouse.move(580, 500); await pg.mouse.wheel(0, 1); await pg.clock.run_for(300)
    ok(await pg.evaluate("document.querySelector('#idleband').hidden"), 'idleMin 15 → 12분 뒤 입력해도 띠 없음')
    # 시계 팝업의 무활동 기준 선택
    ok(await pg.evaluate("document.querySelector('#clock').tagName==='BUTTON'&&document.querySelector('#clock').getAttribute('aria-label').includes('공부 시계')"), '#clock = button · aria-label')
    await pg.click('#clock'); await pg.clock.run_for(200); await pg.click('#tpop [data-tp=goal]'); await pg.clock.run_for(500)   # ux4 묶음2: 측정 설정은 📅 달력
    ok(await pg.evaluate("document.querySelector('#calmset select[data-cset=idleMin]').value") == '15', '달력 측정 설정 무활동 기준 = 15분')
    await pg.select_option('#calmset select[data-cset=idleMin]', '5'); ok(await ls(pg, 'idleMin') == 5, '5분 고르면 LS idleMin=5')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def part_multi(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); A = await ctx.new_page(); B = await ctx.new_page(); errs = []
    for pg in (A, B): pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    print('== B05 창 여러 개')
    await A.clock.install(time=NOW)   # 컨텍스트 공용 시계
    await boot(A, '#/PHARM/RX/learn'); await A.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.restAuto','false')")
    await boot(A, '#/PHARM/RX/learn'); await boot(B, '#/PHARM/RX/learn')
    for i in range(12):          # 10초마다 번갈아 입력 — 2분
        pg = (A, B)[i % 2]; await pg.mouse.move(300 + i * 7, 400); await pg.mouse.wheel(0, 1); await asyncio.sleep(0.15)
        await A.clock.run_for(10000)   # page.clock은 컨텍스트 공용 — 한 번만 돌림
    for q in (A, B): await q.evaluate("dispatchEvent(new Event('pagehide'))")
    s = sum((await ls(A, 'time') or {}).get('2026-09-24', {}).values())
    ok(110000 <= s <= 130000, f'두 창 번갈아 2분 → time +{s / 1000:.0f}초 (겹쳐 잡힌 시간 ≤ 10초)')
    st = await A.evaluate("document.querySelector('#clock').textContent"); ok('다른 창' in st, f"다른 창 버튼 '{st}'")
    await B.mouse.move(700, 400); await B.mouse.wheel(0, 1); await B.clock.run_for(1000)
    # ux2 fixA V07·V10: 화면에 보이는 채 blur(Split View 옆 앱) = 무활동과 같게 — 30초에 멈추지 않음
    await B.evaluate("dispatchEvent(new Event('blur'))"); await B.clock.run_for(31000)
    ok(await B.evaluate("document.querySelector('#clock').dataset.st") == 'run', 'blur(화면에 보임) 31초 → 계속 잼(무활동 규칙)')
    await B.evaluate("dispatchEvent(new Event('focus'))"); await B.mouse.move(710, 400); await B.mouse.wheel(0, 1); await B.clock.run_for(1000)
    # 옛 방식(LS blurIdle=false): 30초 뒤 멈춤 → focus → 다시
    await B.evaluate("localStorage.setItem('jblhub.v1.blurIdle','false')")
    await B.evaluate("dispatchEvent(new Event('blur'))"); await B.clock.run_for(31000)
    ok(await B.evaluate("document.querySelector('#clock').dataset.st") != 'run', 'blurIdle 끔 → blur 31초 → 측정 멈춤')
    await B.evaluate("dispatchEvent(new Event('focus'))"); await B.clock.run_for(1000)
    ok(await B.evaluate("document.querySelector('#clock').dataset.st") == 'run', 'focus → 다시 잼')
    await B.evaluate("localStorage.removeItem('jblhub.v1.blurIdle')")
    # Split View: blur 뒤 12분 입력 없음 → 무활동 기준(8분)에 멈춤 → 돌아와 입력하면 [공부했어요 +n분]
    await B.mouse.move(720, 400); await B.mouse.wheel(0, 1); await B.clock.run_for(1000)
    await B.evaluate("dispatchEvent(new Event('blur'))"); await B.clock.run_for(12 * MIN)
    ok(await B.evaluate("document.querySelector('#clock').dataset.st") != 'run', 'blur 12분 → 무활동 기준에서 멈춤')
    await B.evaluate("dispatchEvent(new Event('focus'))"); await B.mouse.move(730, 400); await B.mouse.wheel(0, 1); await B.clock.run_for(300)
    band = await B.evaluate("(()=>{const b=document.querySelector('#idleband');return b.hidden?'':b.textContent})()")
    ok('공부했어요 +11분' in band, f'Split View 돌아옴 → 띠 {band!r}')
    await B.evaluate("document.querySelector('#idleband [data-ib=no]').click()"); await B.clock.run_for(200)
    await B.screenshot(path=J.TMP + '/ux2f_v07_split.png', clip={'x': 0, 'y': 0, 'width': 1280, 'height': 60})
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def part_twoidle(b):
    """ux2 fixA V02: 창 A 무활동(기준 넘어 멈춤) → 창 B가 30분 잼 → A로 돌아와도 B가 잰 시간은 되묻지 않음(띠 ≤ B 시작 전 공백)"""
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); A = await ctx.new_page(); B = await ctx.new_page(); errs = []
    for pg in (A, B): pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    print('== V02 창 두 개 무활동 뒤 다른 창')
    await A.clock.install(time=NOW)
    await boot(A, '#/OMS1/_home'); await A.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.restAuto','false')")
    await boot(A, '#/OMS1/_home'); await boot(B, '#/CONS/_home')
    await A.mouse.move(300, 400); await A.mouse.wheel(0, 1); await A.clock.run_for(1000)
    for i in range(10): await A.mouse.move(310 + i, 400); await A.mouse.wheel(0, 1); await A.clock.run_for(30000)   # A 5분 공부
    await A.clock.run_for(10 * MIN)   # 둘 다 10분 입력 없음 → A 멈춤(idleGap)
    ok(await A.evaluate("document.querySelector('#clock').dataset.st") != 'run', 'A 10분 무활동 → 멈춤')
    for i in range(60): await B.mouse.move(300 + (i % 20), 420); await B.mouse.wheel(0, 1); await asyncio.sleep(0.02); await A.clock.run_for(30000)   # B 30분
    await A.mouse.move(500, 500); await A.mouse.wheel(0, 1); await asyncio.sleep(0.1); await A.clock.run_for(300)
    band = await A.evaluate("(()=>{const b=document.querySelector('#idleband');return b.hidden?'':b.textContent})()")
    import re as _re
    m = _re.search(r'공부했어요 \+(\d+)분', band); add = int(m.group(1)) if m else 0
    ok(add <= 11, f'A로 돌아옴 → 띠 +{add}분 ≤ B 시작 전 공백(약 9분) ({band!r})')
    if m: await A.evaluate("document.querySelector('#idleband [data-ib=add]').click()"); await A.clock.run_for(200)
    for q in (A, B): await q.evaluate("dispatchEvent(new Event('pagehide'))")
    tm = (await ls(A, 'time') or {}).get('2026-09-24', {}); tot = sum(tm.values())
    ok(tot <= 47 * MIN, f"합계 {tot / MIN:.0f}분 ≤ 실제 흐른 약 46분 ({ {k: round(v / MIN) for k, v in tm.items()} })")
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await part_view(b, {'width': 1280, 'height': 900}, False, 'mac')
        await part_view(b, {'width': 820, 'height': 1180}, True, 'ipp')
        await part_view(b, {'width': 1180, 'height': 820}, True, 'ipl')
        await part_clock(b)
        await part_multi(b)
        await part_twoidle(b)
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
