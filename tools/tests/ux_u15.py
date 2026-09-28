"""U15 회귀: JB 필터 막대 공통화(과목 JB·강의 기출 탭) · 위에 붙는 압축 막대 · 연도/짤탈/교수 필터 · 검색 범위(띄어쓰기 무시) · 풀이 상태 저장.
맥 1280×900 · 아이패드 세로 820×1180(터치). 스크린샷 work/_tmp/ux_u15_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1200):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
VIS = "[...document.querySelectorAll('#cards .qc:not(.hid)')]"
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    # 강의 기출 탭: 공통 막대
    await open_(pg, '#/PHARM/RX/jb')
    r = await pg.evaluate("(()=>({qf:document.querySelectorAll('#jbbar [data-qf]:not([hidden])').length,prog:!!document.querySelector('#jbprog .pline'),flec:!!document.querySelector('#flec'),sort:document.querySelector('#fsort').value,hstat:document.querySelector('#hstat').textContent}))()")
    ok(r['qf'] == 4 and r['prog'] and not r['flec'] and r['sort'] == 'n', f'강의 기출 탭: 안 푼 것/틀린 것/★·진행률, 강의 필터 숨김, 기본 출제 횟수 순 {r}')
    ok(r['hstat'].startswith('✓0 ✗0'), f"강의 헤더 '✓ ✗' 칩 ({r['hstat']})")
    await pg.screenshot(path=J.TMP + f'/ux_u15_lectab_{tag}.png')
    # PHARM _jb: 20000px 스크롤해도 첫 줄 보임
    await open_(pg, '#/PHARM/_jb/_jb')
    await pg.screenshot(path=J.TMP + f'/ux_u15_top_{tag}.png')
    await pg.evaluate("scrollTo(0,20000)"); await pg.wait_for_timeout(500)
    r = await pg.evaluate("(()=>{const b=document.querySelector('#jbbar .b1').getBoundingClientRect(),t=document.querySelector('#top').getBoundingClientRect();return {top:Math.round(b.top),tb:Math.round(t.bottom),mini:document.querySelector('#jbbar').classList.contains('mini'),vis:b.bottom>0&&b.top<innerHeight,y:scrollY}})()")
    ok(r['vis'] and r['mini'] and r['top'] >= r['tb'] and r['y'] > 15000, f'20000px 스크롤 후 필터 첫 줄 보임·압축 {r}')
    h = await pg.evaluate("document.querySelector('#jbbar').offsetHeight")
    ok(h <= (130 if tag == 'ipad' else 80), f'압축 막대 높이 {h}px')
    await pg.screenshot(path=J.TMP + f'/ux_u15_scrolled_{tag}.png')
    await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(300)
    # 검색: 'warfarin과' 문제만 = 6건
    await pg.fill('#fq', 'warfarin과'); await pg.wait_for_timeout(400)
    n = await pg.evaluate(f"{VIS}.length"); t = await pg.inner_text('#fqn')
    ok(n == 6 and t == '6건', f"'warfarin과' 문제만 {n}건 ({t})")
    await pg.evaluate("document.querySelector('#jbbar [data-qs=\"qa\"]').click()"); await pg.wait_for_timeout(200)
    n2 = await pg.evaluate(f"{VIS}.length"); ok(n2 >= n, f'문제+답 범위 {n2}건 ≥ {n}')
    await pg.evaluate("document.querySelector('#jbbar [data-qs=\"q\"]').click()"); await pg.fill('#fq', ''); await pg.wait_for_timeout(300)
    # 연도 2024
    await pg.select_option('#fyr', '24'); await pg.wait_for_timeout(300)
    r = await pg.evaluate(f"(()=>{{const v={VIS};return {{n:v.length,bad:v.filter(c=>(' '+c.dataset.yrs+' ').indexOf(' 24 ')<0).length,all:[...document.querySelectorAll('#cards .qc')].filter(c=>c.dataset.tier!=='C'&&(' '+c.dataset.yrs+' ').indexOf(' 24 ')>=0).length,sort:document.querySelector('#fsort').value}}}})()")
    ok(r['n'] > 0 and r['bad'] == 0 and r['n'] == r['all'] and r['sort'] == '', f'2024 → data-yrs에 24가 있는 카드만, 정렬 JB 수록 순서 {r}')
    # 짤/탈
    await pg.evaluate("document.querySelector('#jbbar [data-stf=\"tt\"]').click()"); await pg.wait_for_timeout(200)
    r = await pg.evaluate(f"(()=>{{const v={VIS};return {{n:v.length,bad:v.filter(c=>c.dataset.st!=='tt').length}}}})()")
    ok(r['n'] > 0 and r['bad'] == 0, f'2024 + 탈 {r}')
    # 교수
    prof = await pg.evaluate("(()=>{const o=document.querySelectorAll('#fprof option');return o.length>1?o[1].value:''})()")
    await pg.evaluate("document.querySelector('#jbbar [data-stf=\"tt\"]').click()"); await pg.select_option('#fyr', ''); await pg.select_option('#fprof', prof); await pg.wait_for_timeout(300)
    r = await pg.evaluate(f"(()=>{{const v={VIS};return {{n:v.length,bad:v.filter(c=>c.dataset.prof!=={json.dumps(prof)}).length}}}})()")
    ok(r['n'] > 0 and r['bad'] == 0, f'교수 필터 {prof} {r}')
    # 상태 저장: 다른 문서 다녀오기
    await pg.select_option('#fyr', '23'); await pg.evaluate("document.querySelector('#jbbar [data-stf=\"jj\"]').click()"); await pg.fill('#fq', 'NSAID'); await pg.wait_for_timeout(300)
    await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"_home\"]').click()"); await pg.wait_for_timeout(400)
    await pg.evaluate("document.querySelector('#side .dbtn[data-d=\"_jb\"]').click()"); await pg.wait_for_timeout(600)
    r = await pg.evaluate("(()=>({yr:document.querySelector('#fyr').value,st:(document.querySelector('#jbbar [data-stf].on')||{}).dataset?.stf,q:document.querySelector('#fq').value,prof:document.querySelector('#fprof').value}))()")
    ok(r == {'yr': '23', 'st': 'jj', 'q': 'NSAID', 'prof': prof}, f'필터 상태 유지(U08 저장값) {r}')
    await pg.evaluate("document.querySelector('#jbbar [data-stf=\"jj\"]').click()"); await pg.fill('#fq', ''); await pg.select_option('#fyr', ''); await pg.select_option('#fprof', '')
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), '가로 넘침 없음')
    # OMS1: 강의 필터·tier 참고
    await open_(pg, '#/OMS1/_jb/_jb')
    await pg.evaluate("document.querySelector('#fmore').click()"); await pg.wait_for_timeout(200)
    await pg.screenshot(path=J.TMP + f'/ux_u15_oms1more_{tag}.png')
    ok(await pg.evaluate("!!document.querySelector('#flec') && document.querySelectorAll('#jbmore [data-tier]').length===3"), 'OMS1 상세 필터: 강의·등급 3')
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 820, 'height': 1180}, True, 'ipad')
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
