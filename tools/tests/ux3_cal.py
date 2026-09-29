"""ux3 묶음 J 회귀: 📅 공부 달력(#/_cal) — 라우트·옛 #/_time(통계 탭)·칸 합계 = tDay·시험 칩·✎·●·달 넘김 선택 유지·날짜별 목표·
+ 시간 추가(겹침 [겹친 만큼 빼고])·✎ 과목 바꾸기·🗑 지우기(새로고침·다른 창에서 되살아나지 않음)·되돌리기·옛 날짜 '시간대 없음'·시험일 지정·키(←→·Shift·T·A)·
1초 갱신 동안 격자 DOM 불변·⏱ 크게(Esc·숨김 동안 콜백 0)·세 폭 가로 넘침 0.
가짜 시계 2026-09-29(화) 10:00. 스크린샷 work/_tmp/ux3j_{1280,1180,820}.png · ux3i_cal_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime, math
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
NOW = datetime.datetime(2026, 9, 29, 10, 0, 0)
D = lambda i: (NOW - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
MIN = 60000
def fmtH(ms):
    m = int(math.floor(max(0, ms) / 60000 + 0.5)); return f'{m // 60}:{m % 60:02d}'
async def ls(pg, k):
    v = await pg.evaluate(f"localStorage.getItem('jblhub.v1.{k}')"); return json.loads(v) if v else None
async def raw(pg, k): return await pg.evaluate(f"localStorage.getItem('jblhub.v1.{k}')")
async def boot(pg, h, ms=1800):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.clock.run_for(ms)
async def dsum(pg, d): return await pg.evaluate(f"(o=>Object.values(o).reduce((a,b)=>a+b,0))(__h.tDay('{d}'))")
async def dsub(pg, d, s): return await pg.evaluate(f"__h.tDay('{d}')['{s}']||0")
async def cell(pg, d): return await pg.evaluate(f"(c=>c?c.querySelector('.cv').textContent:null)(document.querySelector('#calg [data-cd=\"{d}\"]'))")

def seed(lec):
    """9/1~9/29: OMS1·CONS 분 단위(time·timed) · 9/28은 시간대(tseg)도: CONS 09:00–09:10 자동 · CONS 13:00–14:00 자동 · 휴식 14:00–14:15 · 옛 tadj 9/10 CONS +20분"""
    time, timed = {}, {}
    for i in range(29):
        d = D(i); o = {'OMS1': (20 + (i * 17) % 200) * MIN, 'CONS': ((i * 29) % 150) * MIN}
        if i == 0: o = {'OMS1': 30 * MIN}
        o = {k: v for k, v in o.items() if v}; time[d] = o
        timed[d] = {k + ':' + lec[k][i % len(lec[k])]: v for k, v in o.items()}
    d28 = D(1); c = lec['CONS'][0]
    time[d28] = {'CONS': 70 * MIN}; timed[d28] = {'CONS:' + c: 70 * MIN}
    tseg = {d28: [[9 * 3600, 9 * 3600 + 600, 'CONS', c, 'a'], [13 * 3600, 14 * 3600, 'CONS', c, 'a'], [14 * 3600, 14 * 3600 + 900, '', '', 'r']]}
    trest = {d28: 15 * MIN}
    tadj = {D(19): {'CONS': 20 * MIN}}
    return time, timed, tseg, trest, tadj

async def setup(pg):
    await boot(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    lec = await pg.evaluate("Object.fromEntries(['OMS1','CONS'].map(s=>[s,__h.PACKS[s].lect.map(L=>L.k)]))")
    time, timed, tseg, trest, tadj = seed(lec)
    await pg.evaluate("""([a,b,c,d,e])=>{const N='jblhub.v1.';localStorage.setItem(N+'time',JSON.stringify(a));localStorage.setItem(N+'timed',JSON.stringify(b));localStorage.setItem(N+'tseg',JSON.stringify(c));
      localStorage.setItem(N+'trest',JSON.stringify(d));localStorage.setItem(N+'tadj',JSON.stringify(e));localStorage.setItem(N+'tauto','false');localStorage.setItem(N+'exam.CONS',JSON.stringify('2026-10-01'));}""", [time, timed, tseg, trest, tadj])
    return lec, time

async def part_main(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== J 달력', tag)
    await pg.clock.install(time=NOW)
    lec, time = await setup(pg)
    await boot(pg, '#/_cal')
    ok(await pg.evaluate("location.hash") == '#/_cal' and await pg.locator('#calg .cc').count() == 35, f"#/_cal 월 달력 5주 {await pg.locator('#calg .cc').count()}칸")
    # J3 칸 h:mm = tDay
    bad = []
    for i in range(29):
        d = D(i); v = await dsum(pg, d); exp = fmtH(v) if v >= 30000 else ''; got = await cell(pg, d)
        if got != exp: bad.append((d, got, exp))
    ok(not bad, f'9월 칸 h:mm = tDay 29일 ({bad[:3]})')
    ok(await cell(pg, D(19)) == fmtH(sum(time[D(19)].values()) + 20 * MIN), f'옛 tadj가 있는 날도 칸 = time + tadj ({await cell(pg, D(19))})')
    ok(await pg.evaluate("!document.querySelector('#calg .cx')"), 'ux4 B1-6 시험일(LS exam.CONS 10/1)이 있어도 달력에 시험 칩 없음')
    ok(await pg.evaluate("document.querySelector('#calg .cc.today').dataset.cd") == D(0) and await pg.evaluate("document.querySelector('#calg .cc.sel').dataset.cd") == D(0), '오늘 테두리·선택 = 오늘')
    goal = 240 * MIN
    exp_dots = sorted([D(i) for i in range(29) if await dsum(pg, D(i)) >= goal])
    got_dots = await pg.evaluate("[...document.querySelectorAll('#calg .cc .cg')].map(e=>e.closest('.cc').dataset.cd).sort()")
    ok(got_dots == exp_dots, f'달성 ● = 합계 ≥ 4:00인 날 {len(got_dots)}/{len(exp_dots)}')
    ok(await pg.evaluate("document.querySelector('#calg [data-cd=\"2026-09-30\"]').classList.contains('fut')"), '미래 칸 흐림(fut)')
    # J2 카드 = tDay·trest
    ok(await pg.inner_text('#cc-td') == '00:30:00', f"오늘 공부 카드 {await pg.inner_text('#cc-td')}")
    sm = await pg.inner_text('#calsum'); ok(sm.startswith('9월 ') and '공부한 날 29' in sm, f'월 요약 {sm!r}')
    await pg.screenshot(path=J.TMP + f'/ux3j_{vp["width"]}.png', full_page=True)
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), '가로 넘침 0(달력)')
    # 1초 갱신 동안 격자 DOM 불변
    await pg.evaluate("window.__mo=0;new MutationObserver(r=>{window.__mo+=r.length}).observe(document.querySelector('#calg'),{childList:true,subtree:true,attributes:true})")
    t1 = await pg.inner_text('#cc-td'); await pg.evaluate("__h.trStart()"); await pg.clock.run_for(5000); t2 = await pg.inner_text('#cc-td')
    ok(await pg.evaluate("window.__mo") == 0 and t1 != t2, f'1초 갱신(오늘 공부 {t1}→{t2}) 동안 격자 변화 {await pg.evaluate("window.__mo")}')
    ok(await pg.evaluate("document.querySelector('.ccard.cst [data-trk] .trs').className.includes('trs-sess')"), '상태 카드 = 세션')
    await pg.evaluate("__h.trStop()"); await pg.clock.run_for(300)
    # ‹ › 선택 유지 · 이번 달
    await pg.evaluate("document.querySelector('[data-calm=\"-1\"]').click()"); await pg.clock.run_for(100)
    ok('8월' in await pg.inner_text('.calym') and '9/29' in await pg.inner_text('#calday .cdh'), f"‹ → 8월 · 선택(9/29) 유지 {await pg.inner_text('.calym')}")
    await pg.evaluate("document.querySelector('[data-calm=\"1\"]').click()"); await pg.clock.run_for(100)
    ok(await pg.evaluate("document.querySelector('#calg .cc.sel').dataset.cd") == D(0), '› → 9월 · 선택 칸 그대로')
    # 옛 날짜(시간대 없음)
    await pg.evaluate(f"document.querySelector('#calg [data-cd=\"{D(19)}\"]').click()"); await pg.clock.run_for(100)
    rows = await pg.evaluate("[...document.querySelectorAll('#calday .crow')].map(r=>[r.classList.contains('nts'),r.querySelector('.cdur').textContent])")
    ok(rows and all(r[0] for r in rows) and sum(int(r[1].split(':')[0]) * 60 + int(r[1].split(':')[1]) for r in rows) * MIN == await dsum(pg, D(19)), f"tseg 없는 날 = '시간대 없음' 줄만 · 합 맞음 {rows}")
    # #/_cal/2026-09-28 → 그 날 선택
    await boot(pg, '#/_cal/' + D(1), 1200)
    ok('9/28(월)' in await pg.inner_text('#calday .cdh') and await pg.evaluate("document.querySelector('#calg .cc.sel').dataset.cd") == D(1), '#/_cal/2026-09-28 → 그 날 선택')
    band = await pg.evaluate("document.querySelectorAll('#calday .cband .cbk').length"); ok(band == 3, f'24시간 띠 구간 3(공부 2 + 휴식 1) {band}')
    rows = await pg.evaluate("[...document.querySelectorAll('#calday .crow:not(.nts)')].map(r=>r.querySelector('.ctm').textContent+' '+r.querySelector('.cdur').textContent)")
    ok(rows == ['09:00–09:10 0:10', '13:00–14:00 1:00', '14:00–14:15 0:15'], f'기록 목록 시간순 {rows}')
    await pg.screenshot(path=J.TMP + f'/ux3i_cal_day_{tag}.png', full_page=True)
    # 블록 → 그 줄로
    await pg.evaluate("document.querySelector('#calday .cbk[data-crow=\"1\"]').click()"); await pg.clock.run_for(100)
    ok(await pg.evaluate("document.querySelector('#cr-1').classList.contains('flash')"), '띠 블록을 누르면 그 줄 강조')
    # J5 + 시간 추가 — 겹침 [겹친 만큼 빼고] → +50분
    t0, td0 = await raw(pg, 'time'), await raw(pg, 'timed'); s0 = await dsub(pg, D(1), 'CONS')
    await pg.evaluate("document.querySelector('#cadd').open=true"); await pg.clock.run_for(100)
    await pg.select_option('#caS', 'CONS'); await pg.fill('#caT', '09:00'); await pg.fill('#caH', '1'); await pg.fill('#caM', '0')
    await pg.evaluate("document.querySelector('[data-cago=\"1\"]').click()"); await pg.clock.run_for(100)
    w = await pg.evaluate("(w=>w.hidden?'':w.textContent)(document.querySelector('#cawarn'))")
    ok('이미' in w and '0:10' in w, f'겹침 경고 {w!r}')
    await pg.screenshot(path=J.TMP + f'/ux3i_cal_overlap_{tag}.png', full_page=True)
    await pg.evaluate("document.querySelector('#cawarn [data-cago=\"cut\"]').click()"); await pg.clock.run_for(200)
    s1 = await dsub(pg, D(1), 'CONS'); ok(s1 - s0 == 50 * MIN, f'[겹친 만큼 빼고] → 보존 +{(s1 - s0) / MIN:.0f}분 (50)')
    ok(await raw(pg, 'time') == t0 and await raw(pg, 'timed') == td0, 'time·timed 바이트 그대로')
    await pg.evaluate("document.querySelector('#toast .tact').click()"); await pg.clock.run_for(200)
    ok(await dsub(pg, D(1), 'CONS') == s0, '알림 [되돌리기] → 원래대로')
    # 어제 +1시간 30분(시간대 없이)
    await pg.evaluate("document.querySelector('#cadd').open=true"); await pg.fill('#caT', ''); await pg.fill('#caH', '1'); await pg.fill('#caM', '30')
    c0 = await cell(pg, D(1)); await pg.evaluate("document.querySelector('[data-cago=\"1\"]').click()"); await pg.clock.run_for(200)
    ok(await cell(pg, D(1)) == fmtH(await dsum(pg, D(1))) and await dsum(pg, D(1)) == 70 * MIN + 90 * MIN, f'어제 +1:30 → 칸 {c0} → {await cell(pg, D(1))}')
    ok(await pg.evaluate(f"!!document.querySelector('#calg [data-cd=\"{D(1)}\"] .ce')"), '고친 날 ✎')
    ok(await raw(pg, 'time') == t0 and await raw(pg, 'timed') == td0, 'time·timed 바이트 그대로(추가 뒤)')
    # 거부: 미래·0분·24시간 초과
    await pg.evaluate("document.querySelector('#cadd').open=true"); await pg.fill('#caH', '0'); await pg.fill('#caM', '0')
    await pg.evaluate("document.querySelector('[data-cago=\"1\"]').click()"); await pg.clock.run_for(100)
    ok('0분' in await pg.inner_text('#cawarn'), '0분 거부')
    await pg.fill('#caH', '23'); await pg.fill('#caM', '0'); await pg.evaluate("document.querySelector('[data-cago=\"1\"]').click()"); await pg.clock.run_for(100)
    ok('24시간' in await pg.inner_text('#cawarn'), '하루 24시간 초과 거부')
    # J6 ✎ 과목 바꾸기 보존 → 해부: 보존 −, 해부 +, 하루 합계 그대로
    tot0, cs, an = await dsum(pg, D(1)), await dsub(pg, D(1), 'CONS'), await dsub(pg, D(1), 'ANAT')
    i13 = await pg.evaluate("[...document.querySelectorAll('#calday .crow')].findIndex(r=>r.querySelector('.ctm').textContent.startsWith('13:00'))")
    await pg.evaluate(f"document.querySelectorAll('#calday .crow')[{i13}].querySelector('[data-cre]').click()"); await pg.clock.run_for(100)
    await pg.select_option('#ceS', 'ANAT'); await pg.evaluate("document.querySelector('[data-cesave]').click()"); await pg.clock.run_for(200)
    tot1, cs1, an1 = await dsum(pg, D(1)), await dsub(pg, D(1), 'CONS'), await dsub(pg, D(1), 'ANAT')
    ok(tot1 == tot0 and cs - cs1 == 60 * MIN and an1 - an == 60 * MIN, f'✎ 보존→해부 = 보존 −{(cs - cs1) / MIN:.0f} · 해부 +{(an1 - an) / MIN:.0f} · 합계 그대로')
    rows = await pg.evaluate("[...document.querySelectorAll('#calday .crow:not(.nts)')].map(r=>r.querySelector('.ctm').textContent+' '+r.querySelector('.csj').textContent)")
    ok(any(r.startswith('13:00–14:00') and '두경부해부' in r for r in rows), f'목록에 고친 구간 {rows}')
    ok(await raw(pg, 'time') == t0 and await raw(pg, 'timed') == td0, 'time·timed 바이트 그대로(고친 뒤)')
    # 🗑 지우기 → 새로고침·다른 창에서 되살아나지 않음 → 되돌리기
    i9 = await pg.evaluate("[...document.querySelectorAll('#calday .crow')].findIndex(r=>r.querySelector('.ctm').textContent.startsWith('09:00'))")
    a0 = await dsum(pg, D(1))
    await pg.evaluate(f"document.querySelectorAll('#calday .crow')[{i9}].querySelector('[data-crd]').click()"); await pg.clock.run_for(200)
    for _ in range(40):   # 앞 알림(결과 알림은 3초 이상)이 지나갈 때까지
        tt = await pg.inner_text('#toast')
        if '지웠어요' in tt: break
        await pg.clock.run_for(500)
    ok('지웠어요' in tt and await pg.locator('#toast .tact').count() == 1, f'🗑 → 확인창 없이 · 알림 [되돌리기] {tt!r}')
    a1 = await dsum(pg, D(1)); ok(a0 - a1 == 10 * MIN, f'🗑 → 합계 −{(a0 - a1) / MIN:.0f}분')
    await boot(pg, '#/_cal/' + D(1), 1200); ok(await dsum(pg, D(1)) == a1 and not any(r.startswith('09:00') for r in await pg.evaluate("[...document.querySelectorAll('#calday .crow .ctm')].map(e=>e.textContent)")), '새로고침 → 지운 구간 되살아나지 않음')
    p2 = await ctx.new_page(); await p2.goto(U + '#/_cal/' + D(1)); await pg.clock.run_for(1200)
    ok(await p2.evaluate(f"(o=>Object.values(o).reduce((a,b)=>a+b,0))(__h.tDay('{D(1)}'))") == a1, '다른 창 → 지운 채')
    await p2.close()
    g = await pg.evaluate("__h.tEdit().filter(e=>e.k==='del'&&!e.x).map(e=>e.p||e.i)[0]")
    await pg.evaluate(f"__h.undoEdit('{g}')"); await boot(pg, '#/_cal/' + D(1), 1200)
    ok(await dsum(pg, D(1)) == a0 and any(r.startswith('09:00') for r in await pg.evaluate("[...document.querySelectorAll('#calday .crow .ctm')].map(e=>e.textContent)")), '되돌리기 → 합계·구간 다시')
    # I6 날짜별 목표 — 어제만 2:00
    await pg.select_option(f'#calday select[data-cgoal="{D(1)}"]', '120'); await pg.clock.run_for(200)
    ok(await pg.evaluate(f"__h.tGoal('{D(1)}')") == 120 and await pg.evaluate(f"__h.tGoal('{D(0)}')") == 240, '어제 목표 2:00 · 오늘은 기본 4:00')
    f = await pg.evaluate(f"+document.querySelector('#calg [data-cd=\"{D(1)}\"]').style.getPropertyValue('--f')")
    ok(abs(f - min(1, (await dsum(pg, D(1))) / (120 * MIN))) < 0.002 and await pg.evaluate(f"!!document.querySelector('#calg [data-cd=\"{D(1)}\"] .cg')"), f'어제 칸 채움·● 기준 = 2:00 (--f {f})')
    ok(await pg.evaluate(f"document.querySelector('#calg [data-cd=\"{D(1)}\"] .cn').classList.contains('gd')"), '따로 정한 목표 = 날짜 밑줄')
    # ux4 B1-6 앞날: 목표만 · '이 날을 시험일로'·시험 칩 없음 · LS exam.CONS는 그대로
    await pg.evaluate("document.querySelector('#calg [data-cd=\"2026-09-30\"]').click()"); await pg.clock.run_for(100)
    ok(await pg.locator('#calday #cadd').count() == 0 and await pg.locator('#calday select[data-cexs],#calday .cdex').count() == 0, '앞날 = 추가 없음 · 시험일 고르기 없음')
    ok(await ls(pg, 'exam.CONS') == '2026-10-01' and '시험' not in await pg.inner_text('#calday'), 'LS exam.CONS 보존 · 그 날 칸에 시험 글자 없음')
    # 키: ← → · Shift+← · T · A
    await boot(pg, '#/_cal', 1200); await pg.mouse.click(5, 300)
    await pg.keyboard.press('ArrowLeft'); await pg.clock.run_for(100)
    ok(await pg.evaluate("__h.CAL.sel") == D(1), f'← → 어제 {await pg.evaluate("__h.CAL.sel")}')
    await pg.keyboard.press('Shift+ArrowLeft'); await pg.clock.run_for(100); ok('8월' in await pg.inner_text('.calym'), 'Shift+← → 지난달')
    await pg.keyboard.press('t'); await pg.clock.run_for(100); ok(await pg.evaluate("__h.CAL.sel") == D(0) and '9월' in await pg.inner_text('.calym'), 'T → 오늘')
    await pg.keyboard.press('a'); await pg.clock.run_for(100); ok(await pg.evaluate("document.querySelector('#cadd').open"), 'A → 선택한 날 + 시간 추가 열림')
    # J1 옛 #/_time = 통계 탭 · 뒤로가기
    await boot(pg, '#/_cal', 1000); await pg.evaluate("location.hash='#/_time'"); await pg.clock.run_for(500)
    ok(await pg.evaluate("document.querySelector('[data-caltab=\"stats\"]').classList.contains('on')") and await pg.locator('#home .tvb').count() == 7, '#/_time → 📊 통계 탭(주 막대 7)')
    await pg.go_back(); await pg.clock.run_for(500)
    ok(await pg.evaluate("location.hash") == '#/_cal' and await pg.locator('#calg').count() == 1, f"뒤로가기 → 달력 {await pg.evaluate('location.hash')}")
    # J7 ⏱ 크게
    await pg.evaluate("document.querySelector('.ccard.cst [data-trb=big]').click()"); await pg.clock.run_for(100)
    ok(await pg.evaluate("document.querySelector('#bigclock').classList.contains('on')"), '⏱ 크게 열림')
    await pg.evaluate("__h.trStart()"); b1 = await pg.inner_text('#bct'); await pg.clock.run_for(1100); b2 = await pg.inner_text('#bct')
    ok(b1 != b2, f'1초마다 숫자 바뀜 {b1}→{b2}')
    await pg.screenshot(path=J.TMP + f'/ux3i_cal_big_{tag}.png')
    await pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))")
    n0 = await pg.evaluate("__h.BIG.n"); await pg.clock.run_for(5000); n1 = await pg.evaluate("__h.BIG.n")
    ok(n1 == n0, f'숨김 동안 콜백 {n1 - n0}')
    await pg.evaluate("delete document.hidden;document.dispatchEvent(new Event('visibilitychange'))"); await pg.clock.run_for(1100)
    ok(await pg.evaluate("__h.BIG.n") > n1, '다시 보이면 이어서')
    await pg.keyboard.press('Escape'); await pg.clock.run_for(100)
    ok(not await pg.evaluate("document.querySelector('#bigclock').classList.contains('on')"), 'Esc → 닫힘')
    await pg.evaluate("__h.trStop()")
    # 넘침 — 선택한 날·통계
    await boot(pg, '#/_cal/' + D(1), 1200); await pg.evaluate("document.querySelector('#cadd').open=true")
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), '가로 넘침 0(선택한 날·추가 폼)')
    await pg.screenshot(path=J.TMP + f'/ux3i_cal_{vp["width"]}.png', full_page=True)
    await boot(pg, '#/_time', 1200); ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), '가로 넘침 0(통계)')
    await pg.evaluate("scrollTo(0,document.body.scrollHeight)"); await pg.screenshot(path=J.TMP + f'/ux3i_cal_stats_{tag}.png')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await part_main(b, {'width': 1280, 'height': 900}, False, 'mac')
        await part_main(b, {'width': 1180, 'height': 820}, True, 'ipl')
        await part_main(b, {'width': 820, 'height': 1180}, True, 'ipp')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
