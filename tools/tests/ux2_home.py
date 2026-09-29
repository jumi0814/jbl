"""B06·B07·B10 회귀: 허브 홈 '오늘' 띠(ux4: 시험일 D-day·시험순·하루 분량은 화면에서 뺌 — 값은 보존) / 오늘 복습 대기열(라이트너 — mk.log만 읽음) /
작은 표시(hero ✓✗ 0이면 숨김·강의 미니바 '틀 · 19장'·#gohome button·서랍 '🏠 허브 홈').
맥 1280×900 + 아이패드 세로 820×1180 + 가로 1180×820. 스크린샷 work/_tmp/ux2i_b0*_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime, math, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, cond="window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#home,#stage')"):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_function(cond, timeout=30000); await pg.wait_for_timeout(300)
DAY = 864e5
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await open_(pg, '#/')
    # ---- B06 → ux4 B1-6: 시험일·시험순·하루 분량은 화면에서 뺌(LS exam.<S>·homeSort는 지우지 않고 그대로 · 로직에도 안 씀)
    d3 = (datetime.date.today() + datetime.timedelta(days=3)).isoformat()
    await pg.evaluate(f"localStorage.setItem('jblhub.v1.exam.PHARM',JSON.stringify('{d3}'));localStorage.setItem('jblhub.v1.homeSort',JSON.stringify('exam'))"); await open_(pg, '#/')
    bt = await pg.inner_text('#home .hband'); ok(not re.search(r'D-\d', bt) and '시험' not in bt, f'시험일이 있어도 띠에 D-n·시험 없음 ({bt!r})')
    r = await pg.evaluate("[document.querySelectorAll('#home .dday,#home [data-exed],#home [data-hsort],#home [data-exfocus],#home input[data-exam]').length,document.querySelector('#home .hsj[data-s]').dataset.s,document.querySelector('#home .hsjh').innerText]")
    ok(r[0] == 0 and r[1] == 'OMS1' and '시험' not in r[2] and '읽음' not in r[2], f'과목 표: 시험 칸·✎·기본/시험순 없음 · 순서 기본(OMS1 먼저) · 머리 {r[2]!r}')
    await pg.screenshot(path=J.TMP + f'/ux2i_b06_home_{tag}.png')
    await open_(pg, '#/PHARM/_home')
    ok(await pg.evaluate("!document.querySelector('#stage .exline')") and '하루' not in await pg.inner_text('#stage'), '과목 홈 하루 분량(시험일) 줄 없음')
    ok(await pg.evaluate("[JSON.parse(localStorage.getItem('jblhub.v1.exam.PHARM')),JSON.parse(localStorage.getItem('jblhub.v1.homeSort'))]") == [d3, 'exam'], 'LS exam.PHARM·homeSort 값 그대로')
    await pg.screenshot(path=J.TMP + f'/ux2i_b06_subj_{tag}.png')
    # ---- B07 오늘 복습
    ids = await pg.evaluate("__h.PACKS.PHARM.order.filter(id=>(__h.PACKS.PHARM.refids||[]).indexOf(id)<0).slice(0,4)")
    now = await pg.evaluate("Date.now()")
    mk = {'ok': {ids[0]: 1, ids[1]: 1, ids[2]: 1, ids[3]: 1}, 'ng': {}, 'bm': {},
          'log': {ids[0]: [{'r': 'ng', 't': now - 2 * DAY}, {'r': 'ok', 't': now - 1 * DAY}],                 # 틀림→맞음(어제) → 오늘 복습
                  ids[1]: [{'r': 'ng', 't': now - 10 * DAY}, {'r': 'ok', 't': now - 6 * DAY}, {'r': 'ok', 't': now - 4 * DAY}],   # →맞음 2번(4일 전) → +3일 = 복습
                  ids[2]: [{'r': 'ok', 't': now - 3 * DAY}],                                                  # 맞음만 → 뺌
                  ids[3]: [{'r': 'ng', 't': now - 2 * 60e3}, {'r': 'ok', 't': now - 60e3}]}}              # 오늘 맞음 → 내일 (몇 분 전 — 자정 직후에 돌려도 '오늘')
    raw = json.dumps(mk)
    await pg.evaluate("r=>localStorage.setItem('jblhub.v1.mk.PHARM',r)", raw)
    R = await pg.evaluate("(()=>{const r=__h.revInfo('PHARM');return [[...r.due].sort(),[...r.ever].sort()]})()")
    ok(R[0] == sorted(ids[:2]) and R[1] == sorted([ids[0], ids[1], ids[3]]), f'복습 = {ids[0]}·{ids[1]} (맞음만인 {ids[2]} 빠짐, 오늘 맞힌 {ids[3]}은 내일) {R}')
    await open_(pg, '#/')
    rb = await pg.evaluate("(()=>{const b=document.querySelector('#home .htodo [data-todo=rev][data-ts=PHARM]');return [b?b.textContent:'',!!document.querySelector('#home .hsj [data-revgo]')]})()")
    ok('복습 2문항' in rb[0] and not rb[1], f'허브 오늘 할 일 복습 줄 {rb[0]!r} · 과목 표 🔁 열 없음(ux4 B3-2 — 복습은 오늘 할 일·메뉴 오늘 복습)')   # ux3 H3·H4
    await open_(pg, '#/PHARM/_home')
    g1 = await pg.evaluate("document.querySelector('#hguide ol.steps li').textContent")
    ok('오늘 복습 2문항' in g1, f'과목 홈 공부 순서 첫 줄 {g1[:40]!r}')
    await open_(pg, '#/PHARM/_jb/_jb')
    qf = await pg.evaluate("[...document.querySelectorAll('#jbbar [data-qf=due],#jbbar [data-qf=ever]')].map(b=>b.textContent)")
    ok(qf == ['🔁 복습 2', '한 번이라도 틀림 3'], f'JB 필터 칩 {qf}')
    await pg.evaluate("document.querySelector('#jbbar [data-qf=due]').click()"); await pg.wait_for_timeout(200)
    vis = await pg.evaluate("[...document.querySelectorAll('#cards .qc')].filter(c=>!c.classList.contains('hid')).map(c=>c.dataset.id).sort()")
    ok(vis == sorted(ids[:2]), f'🔁 복습 필터 → {vis}')
    await pg.evaluate("document.querySelector('#jbbar [data-qf=ever]').click()"); await pg.wait_for_timeout(200)
    vis = await pg.evaluate("[...document.querySelectorAll('#cards .qc')].filter(c=>!c.classList.contains('hid')).length"); ok(vis == 3, f'한 번이라도 틀림 → {vis}')
    t3 = await pg.evaluate("(document.querySelector('#c-%s .chip.rec')||{}).title||''" % ids[3])
    ok('다음 복습' in t3, f'기록 칩 title {t3!r}')
    await pg.screenshot(path=J.TMP + f'/ux2i_b07_jb_{tag}.png')
    await open_(pg, '#/')
    await pg.evaluate("document.querySelector('#home .htodo [data-todo=rev][data-ts=PHARM]').click()"); await pg.wait_for_timeout(800)
    st = await pg.evaluate("[location.hash,document.body.classList.contains('jbone'),[...document.querySelectorAll('#cards .qc')].filter(c=>!c.classList.contains('hid')).length,(document.querySelector('#opos')||{}).textContent]")
    ok(st[0].startswith('#/PHARM/_jb') and st[1] and st[2] == 2 and st[3] == '1/2', f'오늘 할 일 복습 줄 → JB 복습 필터 + 한 장씩 {st}')
    await pg.screenshot(path=J.TMP + f'/ux2i_b07_one_{tag}.png')
    ok(await pg.evaluate("localStorage.getItem('jblhub.v1.mk.PHARM')") == raw, 'mk 원본 바이트 그대로(읽기만)')
    # ---- B10 작은 표시
    await open_(pg, '#/OMS1/DD1/learn')
    lmn = await pg.inner_text('#lmn'); lmc = await pg.inner_text('#lmcur')
    ok('–' not in lmc and '틀' in lmn, f'강의를 열면 미니바 {lmc!r}')
    ok(await pg.evaluate("getComputedStyle(document.querySelector('#hstat')).display") == 'none', 'hero ✓·✗ 둘 다 0 → display:none')
    await pg.evaluate("document.querySelector('#t-DD1-0').scrollIntoView({block:'start'})"); await pg.wait_for_timeout(600)
    lmc2 = await pg.inner_text('#lmcur'); ok(lmc2.startswith('카드 1/'), f'첫 카드가 기준선을 넘으면 {lmc2!r}')
    await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(600)
    ok('틀' in await pg.inner_text('#lmn'), f"다시 맨 위 → {await pg.inner_text('#lmcur')!r}")
    await pg.screenshot(path=J.TMP + f'/ux2i_b10_lmini_{tag}.png', clip={'x': 0, 'y': 0, 'width': vp['width'], 'height': 200})
    ok(await pg.evaluate("document.querySelector('#gohome').tagName") == 'BUTTON', '#gohome = BUTTON')
    if vp['width'] <= 860:
        await pg.click('#navbtn'); await pg.wait_for_timeout(300)
        hh = pg.locator('#side .nvback[data-nv="home"]'); ok(await hh.is_visible(), "서랍 과목 메뉴 맨 위 '‹ 허브 홈' (ux4 묶음2)")
        await pg.screenshot(path=J.TMP + f'/ux2i_b10_drawer_{tag}.png')
        await hh.click(); await pg.wait_for_timeout(500)
    else:
        ok(await pg.locator('#side .nvback[data-nv="home"]').is_visible(), "넓은 화면 과목 메뉴 '‹ 허브 홈' 늘 보임(ux4 묶음2)")
        await pg.click('#gohome'); await pg.wait_for_timeout(500)
    ok(await pg.evaluate("!!document.querySelector('#home .hub .hsj')&&!document.querySelector('#home').hidden"), '→ 허브 홈')
    await pg.evaluate("localStorage.setItem('jblhub.v1.mk.OMS1',JSON.stringify({ok:{},ng:{},bm:{}}))")
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), '가로 넘침 0')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 820, 'height': 1180}, True, 'ipp')
        await run(b, {'width': 1180, 'height': 820}, True, 'ipl')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
