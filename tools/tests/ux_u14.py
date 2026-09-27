"""U14 회귀: 한 장씩 풀기 아래 고정 풀이 막대([◀][답][✗][✓][★][▶] n/N) · ✓/✗/O/X = 설정 + 자동 넘김(jbauto) · MK.log 기록 칩 '✗2 ✓1'
· 스와이프 넘기기 · 목록 모드 답 끝 채점 줄(.acts2)·답 접기 · 마지막 다음 회차 요약 · 답 토글 문구 · '답 모두 펼치기' 뒤 개별 닫기 · 옛 mk 형식.
맥 1280×900 · 아이패드 세로 820×1180(터치). 스크린샷 work/_tmp/ux_u14_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1300):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
JS = lambda x: f"document.querySelector('{x}').click()"
CUR = "document.querySelector('#cards .qc.cur')?.dataset.id"
MKS = "JSON.parse(localStorage.getItem('jblhub.v1.mk.PHARM')||'{}')"
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    # 옛 mk 형식(log 없음·bm 없음)
    await pg.evaluate("localStorage.setItem('jblhub.v1.mk.PHARM', JSON.stringify({ok:{RX03:1},ng:{}}))")
    await open_(pg, '#/PHARM/_jb/_jb')
    await pg.evaluate(JS('#fone')); await pg.wait_for_timeout(300)
    id0 = await pg.evaluate(CUR)
    await pg.evaluate(JS('#otog')); await pg.wait_for_timeout(150)
    ok(await pg.inner_text('#otog') == '답 가리기 ▲' and await pg.evaluate("document.querySelector('#cards .qc.cur [data-tog]').textContent") == '답 가리기 ▲', '답 토글 문구 → 답 가리기 ▲')
    await pg.evaluate("scrollBy(0,600)"); await pg.wait_for_timeout(300)
    r = await pg.evaluate("(()=>{const b=document.querySelector('#onebar').getBoundingClientRect(),k=document.querySelector('#kit').getBoundingClientRect();const bs=[...document.querySelectorAll('#onebar .ob')].map(x=>{const r=x.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]});return {bottom:Math.round(b.bottom),ih:innerHeight,pos:getComputedStyle(document.querySelector('#onebar')).position,kitAbove:k.bottom<=b.top,bs}})()")
    ok(r['pos'] == 'fixed' and abs(r['bottom'] - r['ih']) <= 1 and r['kitAbove'], f"답 펼치고 스크롤해도 풀이 막대가 화면 아래·도구 막대는 그 위 {r['bottom']}/{r['ih']}")
    ok(all(w >= 56 and h >= 48 for w, h in r['bs']), f"막대 버튼 48×56 이상 {r['bs']}")
    await pg.screenshot(path=J.TMP + f'/ux_u14_bar_{tag}.png')
    # ✓ → ok 설정 + 0.25초 뒤 다음
    await pg.evaluate(JS('#ook')); await pg.wait_for_timeout(100)
    m = await pg.evaluate(MKS); same = await pg.evaluate(CUR)
    await pg.wait_for_timeout(350); nxt = await pg.evaluate(CUR)
    ok(m['ok'].get(id0) == 1 and same == id0 and nxt != id0, f'✓ → mk.ok[{id0}] 설정, 0.25초 뒤 다음 카드({nxt})')
    ok(isinstance(m.get('log', {}).get(id0), list) and m['log'][id0][-1]['r'] == 'ok' and m['ok'].get('RX03') == 1, f"MK.log 추가·옛 기록 유지 {m.get('log',{}).get(id0)}")
    # 이미 맞음인 카드에서 O → 맞음 유지
    await pg.evaluate(JS('#oprev')); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('#oauto').click()"); await pg.wait_for_timeout(100)
    ok(await pg.evaluate("localStorage.getItem('jblhub.v1.jbauto')") == 'false', '자동 넘김 끄기 저장(jbauto)')
    await pg.keyboard.press('o'); await pg.wait_for_timeout(350)
    m = await pg.evaluate(MKS)
    ok(m['ok'].get(id0) == 1 and await pg.evaluate(CUR) == id0 and len(m['log'][id0]) == 2, 'O를 다시 눌러도 맞음 유지(설정)·자동 넘김 꺼져 제자리')
    await pg.keyboard.press('x'); await pg.wait_for_timeout(100); await pg.keyboard.press('x'); await pg.wait_for_timeout(100)
    m = await pg.evaluate(MKS); chip = await pg.evaluate(f"document.querySelector('#c-{id0} .qhead .chip.rec')?.textContent")
    ok(m['ng'].get(id0) == 1 and not m['ok'].get(id0) and chip == '✗2 ✓2', f"X 두 번 → 틀림 유지 · 기록 칩 {chip}")
    await pg.evaluate("document.querySelector('#oauto').click()")
    # 스와이프(터치)·키
    if touch:
        c0 = await pg.evaluate(CUR)
        box = await pg.evaluate("(()=>{const r=document.querySelector('#cards .qc.cur .qtext').getBoundingClientRect();return [r.left+r.width/2,r.top+Math.min(r.height/2,60)]})()")
        cdp = await ctx.new_cdp_session(pg)
        async def swipe(x0, y0, x1):
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x0, 'y': y0}]})
            for i in range(1, 6): await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x0 + (x1 - x0) * i / 5, 'y': y0}]}); await pg.wait_for_timeout(16)
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        await swipe(box[0] + 150, box[1], box[0] - 150); await pg.wait_for_timeout(300)
        c1 = await pg.evaluate(CUR); ok(c1 != c0, f'왼쪽 스와이프 → 다음 ({c0}→{c1})')
        await pg.evaluate("document.querySelector('#k-h').click()"); await pg.wait_for_timeout(100)
        await swipe(box[0] - 150, box[1] + 30, box[0] + 150); await pg.wait_for_timeout(300)
        ok(await pg.evaluate(CUR) == c1, '형광펜 모드에서는 스와이프 무시')
        await pg.evaluate("document.querySelector('#k-h').click()")
    # 마지막 다음 = 요약
    n = await pg.evaluate("JSON.parse(document.querySelector('#opos').textContent.split('/')[1])")
    await pg.evaluate(f"(()=>{{for(let i=0;i<{n}+2;i++)document.querySelector('#onext').click()}})()")
    await pg.evaluate("(()=>{let g=0;while(document.querySelector('#opos').textContent!=='요약'&&g++<400)document.querySelector('#onext').click();})()"); await pg.wait_for_timeout(300)
    r = await pg.evaluate("(()=>{const s=document.querySelector('#onesum');return s&&!s.hidden?s.innerText:''})()")
    ok('이번 회차 156문항' in r and '✗ 1' in r and '틀린 것만 다시' in r, f"마지막 다음 = 회차 요약 ({r[:60]})")
    await pg.screenshot(path=J.TMP + f'/ux_u14_sum_{tag}.png')
    await pg.evaluate("document.querySelector('[data-onesum=\"ng\"]').click()"); await pg.wait_for_timeout(300)
    ok(await pg.inner_text('#opos') == '1/1' and await pg.evaluate(CUR) == id0, f"틀린 것만 다시 → {await pg.inner_text('#opos')}")
    await pg.evaluate("document.querySelector('#jbbar [data-qf=\"\"]').click()"); await pg.evaluate(JS('#fone')); await pg.wait_for_timeout(200)
    ok(not await pg.evaluate("document.body.classList.contains('jbone')"), '한 장씩 끄면 풀이 막대 사라짐')
    # 목록 모드: 답 끝 채점 줄·답 접기
    await pg.evaluate("document.querySelector('#c-RX05 [data-tog]').click()"); await pg.wait_for_timeout(150)
    await pg.evaluate("document.querySelector('#c-RX05 .acts2 [data-mk=\"ok\"]').click()"); await pg.wait_for_timeout(100)
    ok((await pg.evaluate(MKS))['ok'].get('RX05') == 1, '목록 모드 답 끝 [✓ 맞음]')
    await pg.evaluate("document.querySelector('#c-RX05 .acts2 [data-fold]').click()"); await pg.wait_for_timeout(500)
    r = await pg.evaluate("(()=>{const c=document.querySelector('#c-RX05');const t=c.getBoundingClientRect().top;return [c.classList.contains('open'),Math.round(t)]})()")
    ok(not r[0] and 0 < r[1] < 300, f'답 접기 → 닫히고 카드 머리로 {r}')
    # 답 모두 펼치기 뒤 개별 닫기
    await pg.evaluate(JS('#frev')); await pg.wait_for_timeout(150)
    await pg.evaluate("document.querySelector('#c-RX02 [data-tog]').click()"); await pg.wait_for_timeout(100)
    r = await pg.evaluate("[document.querySelector('#c-RX02').classList.contains('open'),getComputedStyle(document.querySelector('#c-RX02 .ans')).display,document.querySelector('#c-RX03').classList.contains('open')]")
    ok(r == [False, 'none', True], f"답 모두 펼치기 상태에서 개별 카드 닫기 {r}")
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), '가로 넘침 없음')
    hint = await pg.evaluate("getComputedStyle(document.querySelector('.okeys')).display")
    ok((hint == 'none') == touch, f'키 안내 문구는 마우스 기기만 ({hint})')
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
