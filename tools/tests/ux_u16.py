"""U16 회귀: JB 진행률 분모 = 현 교수 기출(stats.main). OMS1 = main(+참고 ref 따로), PHARM = 전체 그대로(참고 없음), 기출 대장에 '0' 등급 생략.
문항 수는 팩(PACKS.<S>.stats)에서 읽음 — 원고·JB 분해가 바뀌어도 고정 숫자에 묶이지 않게.
맥 1280×900 · 아이패드 세로 820×1180. 스크린샷 work/_tmp/ux_u16_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1100):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    await pg.evaluate("localStorage.setItem('jblhub.v1.mk.OMS1', JSON.stringify({ok:{Q01:1,Q02:1},ng:{Q03:1},bm:{}}))")
    await open_(pg, '#/')
    ST = await pg.evaluate("({O:__h.PACKS.OMS1.stats,P:__h.PACKS.PHARM.stats})"); M, R, PM = ST['O']['main'], ST['O']['ref'], ST['P']['main']
    ok(R > 0 and ST['P']['ref'] == 0 and ST['P']['cards'] == PM, f'픽스처: OMS1 현 교수 {M}·참고 {R} / PHARM {PM}(참고 0)')
    hub = await pg.evaluate("(()=>{const r=document.querySelector('.hsj[data-s=\"OMS1\"]');return r.querySelector('.hcj').title+' | '+r.innerText})()")   # ux3 H4 과목 표 기출 칸 title
    r_ng = await pg.evaluate("document.querySelector('.hsj[data-s=\"OMS1\"] .hcng').textContent")
    ok(f'현 교수 기출 {M}문항' in hub and f'참고 {R}' in hub and '맞음 2 · 틀림 1' in hub and f'안 푼 것 {M - 3}' in hub and f'3 / {M}' in hub and r_ng == '1', f'허브 과목 표 OMS1 푼 것 3 / 분모 {M} · 틀림 1 · 참고 {R}(title) ({hub[:90]!r})')   # ux4 B3-2 '기출 푼 것 n / 전체' + 틀림 열
    ph = await pg.evaluate("document.querySelector('.hsj[data-s=\"PHARM\"] .hcj').title")
    ok(f'기출 {PM}문항' in ph and '참고' not in ph and '현 교수' not in ph, f'PHARM 허브 과목 표 {PM} · 참고 없음 ({ph!r})')
    await pg.screenshot(path=J.TMP + f'/ux_u16_hub_{tag}.png')
    await open_(pg, '#/OMS1/_home/_home')
    t = await pg.evaluate("document.querySelector('#hprog').innerText")
    ok(f'현 교수 기출 {M}문항' in t and f'안 푼 것 {M - 3}' in t and f'JB에서 참고 {R} 보기' in t, f'과목 홈 진행률(ux4 B3-3 — 참고는 절 제목 오른쪽 링크) ({t[:80]})')
    await pg.screenshot(path=J.TMP + f'/ux_u16_home_{tag}.png')
    await open_(pg, '#/OMS1/_jb/_jb')
    t = await pg.inner_text('#jbprog')
    ok(f'현 교수 기출 {M}문항' in t and f'참고 {R} 숨김' in t, f'JB 진행 줄 {M} · 참고 {R} ({t[:90]})')
    await pg.evaluate("document.querySelector('#jbprog [data-reftog]').click()"); await pg.wait_for_timeout(300)
    t = await pg.inner_text('#jbprog'); n = await pg.evaluate("document.querySelectorAll('#cards .qc[data-tier=C]:not(.hid)').length")
    ok(f'참고 {R} 보이는 중' in t and n == R and f'현 교수 기출 {M}문항' in t, f'[보이기] → 참고 카드 {R} 보임, 분모 그대로 ({t[:90]})')
    cid = await pg.evaluate("document.querySelector('#cards .qc[data-tier=C]').dataset.id")
    await pg.evaluate(f"document.querySelector('#c-{cid} [data-mk=ok]').click()"); await pg.wait_for_timeout(200)
    t = await pg.inner_text('#jbprog')
    ok('맞음 1' in t.split('참고')[1] and '맞음 2' in t.split('참고')[0], f'참고 카드 채점은 참고 칩에 따로 ({t[:120]})')
    await pg.screenshot(path=J.TMP + f'/ux_u16_jb_{tag}.png')
    await open_(pg, '#/PHARM/_jb/_jb')
    t = await pg.inner_text('#jbprog'); ok(f'기출 {PM}문항' in t and '참고' not in t, f'PHARM JB 진행 줄 {PM} ({t[:60]})')
    for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
        await open_(pg, f'#/{s}/_led/_led', 700)
        t = await pg.evaluate("document.querySelector('#stage .panel').innerText")
        ok(not re.search(r'\s0(\.|\s|$)', t.split('.')[0] + '.'), f'{s} 기출 대장 0 등급 생략 ({t[:70]})')
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
