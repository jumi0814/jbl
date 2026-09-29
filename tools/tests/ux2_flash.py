"""C08 회귀: 플래시카드 기출 판정 = JB 채점
옛 fc.OMS1 {'J:Q35':{s:'x',t}} → 과목을 열면 mk.ng.Q35·log 1건(how:'fc')·fc 원본 남음 · 두 번 열어도(fcMerged를 지워도) log 중복 없음 ·
플래시카드에서 Q01 몰라요 → JB '틀린 것' 필터에 Q01 · JB에서 맞음으로 매긴 문항은 플래시카드 '알아요'로 보임(상태·'몰라요만'은 mk에서) · 암기 카드는 fc 그대로.
맥 1280×900 + 아이패드 세로 820×1180 · 가로 1180×820. 스크린샷 work/_tmp/ux2i_c08_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
MK = "JSON.parse(localStorage.getItem('jblhub.v1.mk.OMS1')||'{}')"
async def go(pg, h):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_function("document.querySelector('#stage') && document.querySelector('#stage').children.length>0"); await pg.wait_for_timeout(500)
async def run(b, vp, touch, tag, full):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: asyncio.ensure_future(d.accept())); print('==', tag)
    await pg.goto(U + '#/'); await pg.wait_for_selector('.hsj[data-s="OMS1"]'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    await pg.goto(U + '#/'); await pg.wait_for_selector('.hsj[data-s="OMS1"]')
    lec, q1 = await pg.evaluate("(()=>{const p=__h.PACKS.OMS1;const L=p.lect.find(L=>L.jb.length>=3);return [L.k,L.jb]})()")
    qa, qb, qc = q1[0], q1[1], q1[2]
    if full:
        await pg.evaluate("q=>localStorage.setItem('jblhub.v1.fc.OMS1',JSON.stringify({['J:'+q]:{s:'x',t:1700000000000},'R:x:abc':{s:'o',t:1700000000001}}))", qc)
        await go(pg, '#/OMS1/_home'); m = await pg.evaluate(MK)
        L = m.get('log', {}).get(qc, [])
        ok(m.get('ng', {}).get(qc) == 1 and len(L) == 1 and L[0].get('how') == 'fc', f"옛 fc J:{qc} → mk.ng·log 1건 {L}")
        fc = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.fc.OMS1')")); ok(f'J:{qc}' in fc and 'R:x:abc' in fc, 'fc 원본 남음')
        await pg.evaluate("localStorage.removeItem('jblhub.v1.fcMerged.OMS1')"); await go(pg, '#/OMS1/_home')
        ok(len((await pg.evaluate(MK)).get('log', {}).get(qc, [])) == 1, '두 번 열어도 log 중복 없음')
        await pg.wait_for_timeout(300); ok(any(x['cat'] == 'upd' for x in await pg.evaluate("__h.bkList()")), "합치기 전 자동 백업(원고 갱신·이관 전 — ux2 fixA V04)")
    # 플래시카드에서 몰라요 → JB 틀린 것
    await go(pg, f'#/OMS1/{lec}/flash'); await pg.click('#fc [data-fk="기출"]'); await pg.wait_for_timeout(150)
    await pg.evaluate("q=>{const F=__h.Flash;const j=F.deck.findIndex(c=>c.key==='J:'+q);F.i=j;F.draw();}", qa)
    await pg.click('#fx'); await pg.wait_for_timeout(200)
    m = await pg.evaluate(MK); ok(m.get('ng', {}).get(qa) == 1 and m['log'][qa][-1].get('how') == 'fc', f'플래시카드 몰라요 → mk.ng.{qa} · how:fc')
    ok(f'J:{qa}' not in json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.fc.OMS1')") or '{}') or full, '기출 카드는 fc에 새로 쓰지 않음')
    # JB에서 맞음 → 플래시카드 알아요
    await go(pg, f'#/OMS1/_jb'); await pg.evaluate(f"document.querySelector('#c-{qb} [data-mk=\"ok\"]').click()"); await pg.wait_for_timeout(150)
    await pg.click('#jbbar [data-qf="ng"]'); await pg.wait_for_timeout(200)
    ok(await pg.evaluate(f"!document.querySelector('#c-{qa}').classList.contains('hid')"), f"JB '틀린 것' 필터에 {qa}")
    await go(pg, f'#/OMS1/{lec}/flash'); await pg.click('#fc [data-fk="기출"]'); await pg.wait_for_timeout(150)
    await pg.evaluate("q=>{const F=__h.Flash;const j=F.deck.findIndex(c=>c.key==='J:'+q);F.i=j;F.draw();}", qb)
    ok('알아요' in await pg.inner_text('#fcard .side'), f"JB 맞음 → 플래시카드 '알아요' ({await pg.inner_text('#fcard .side')!r})")
    t = await pg.inner_text('#fc [data-fst="x"]'); ok(t.strip().endswith('1' if not full else '2'), f"'몰라요만' 수 = mk 틀림 {t!r}")
    await pg.screenshot(path=J.TMP + f'/ux2i_c08_flash_{tag}.png')
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac', True)
        await run(b, {'width': 820, 'height': 1180}, True, 'ipp', False)
        await run(b, {'width': 1180, 'height': 820}, True, 'ipl', False)
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
