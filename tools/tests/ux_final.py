import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
# 10-29 사용자 '임상치과 보존학 과목에서 최종 N제라는 탭을 만들어서 … 이것만 보고 들어가면 탈 대비를 완벽히' — 과목 '🎯 최종 N제'(tools/<sid>/final.txt · fn)
#   메뉴·과목 홈 단계·강의 예상 탭 안내 · N제 머리(수·강의 칩) · 카드 = 예상 카드 꼴(N제 배지·답 보기·✓✗★) · 강의 예상·과목 예상에는 안 섞임 · JB 카드 '🎯 N제 n ▸' · N제 없는 과목은 메뉴 없음
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fail = []
def ok(c, m):
    print(('  OK  ' if c else '  FAIL') + ' ' + m)
    if not c: fail.append(m)
def pack(sid):
    t = open(_os.path.join(J.DOCS, 'packs', sid + '.js'), encoding='utf-8').read(); return json.loads(t[t.index('{'):t.rindex('}') + 1])
async def main():
    P = pack('CONS'); FN = [x for x in P['preds'] if x.get('fn') and not x.get('x')]
    if not FN: print('  (N제 없음 — 건너뜀)'); print('RESULT PASS'); return
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await (await br.new_context(viewport={'width': 1280, 'height': 900})).new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(U + '#/CONS/_home'); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(2500)
        ok(await pg.locator('[data-d="_final"]').count() >= 1, '과목 메뉴에 🎯 최종 N제')
        ok(await pg.locator('#stage .finli [data-gofinl]').count() == 1, '과목 홈 공부 순서에 최종 N제 단계')
        await pg.click('#stage .finli [data-gofinl]'); await pg.wait_for_timeout(1500)
        n = await pg.locator('#stage .pc').count(); ok(n == len(FN), f'N제 탭 카드 {n} = 팩 {len(FN)}')
        ok(await pg.locator('#stage .pc:not([data-fn])').count() == 0, 'N제 탭엔 N제만')
        ok((await pg.locator('#stage .pc .ybadge b').first.inner_text()).strip() == 'N제', '카드 배지 N제')
        ok(await pg.locator('#stage .finhd').count() == 1 and str(len(FN)) in await pg.locator('#stage .finhd .finh1').inner_text(), 'N제 머리 문항 수')
        ok(await pg.locator('#ppills [data-ptype="n"]').inner_text() == '탈 대비', '거르기 이름 탈 대비')
        ks = sorted({x['k'] for x in FN}); k0 = ks[0]; nk = sum(1 for x in FN if x['k'] == k0)
        await pg.click(f'#stage .finby [data-finl="{k0}"]'); await pg.wait_for_timeout(300)
        vis = await pg.evaluate("[...document.querySelectorAll('#stage .pc')].filter(c=>!c.classList.contains('plh')&&getComputedStyle(c).display!=='none').length")
        ok(vis == nk, f'강의 칩 {k0} → {vis} = {nk}')
        await pg.click(f'#stage .finby [data-finl="{k0}"]'); await pg.wait_for_timeout(300)
        c0 = pg.locator('#stage .pc').first; await c0.locator('[data-tog]').click(); await pg.wait_for_timeout(200)
        ok(await c0.locator('.ans').evaluate("e=>getComputedStyle(e).display!=='none'"), '답 보기 열림')
        await c0.locator('[data-mk="ok"]').click(); await pg.wait_for_timeout(300)
        aid = await c0.get_attribute('data-aid'); mk = await pg.evaluate("JSON.stringify(Object.keys(localStorage).filter(k=>/mk/.test(k)).map(k=>localStorage.getItem(k)).join(''))")
        ok(aid and ':F:' in aid and aid in mk, f'✓ 맞음 기록 = N제 aid({aid and aid[:24]})')
        await pg.goto(U + f'#/CONS/{k0}/pred'); await pg.wait_for_timeout(2000)
        ok(await pg.locator('#stage .pc[data-fn]').count() == 0, f'{k0} 예상 탭엔 N제 없음')
        ok(await pg.locator('#stage .finlk [data-gofinl]').count() == 1, f'{k0} 예상 탭 위 N제 안내')
        await pg.click('#stage .finlk [data-gofinl]'); await pg.wait_for_timeout(1500)
        ok(await pg.evaluate("(document.querySelector('#plec')||{}).value") == k0, f'안내 → N제 탭이 {k0}로 걸러져 열림')
        await pg.goto(U + '#/CONS/_pred/_pred'); await pg.wait_for_timeout(2000)
        ok(await pg.locator('#stage .pc[data-fn]').count() == 0, '과목 예상문제엔 N제 없음')
        await pg.goto(U + '#/CONS/_jb'); await pg.wait_for_timeout(2500); ch = pg.locator('#stage [data-gofin]')
        if await ch.count():
            await ch.first.scroll_into_view_if_needed(); await ch.first.click(); await pg.wait_for_timeout(1500)
            ok('_final' in await pg.evaluate('location.hash'), 'JB 카드 🎯 N제 칩 → N제 탭')
        await pg.goto(U + '#/ESTH/_home'); await pg.wait_for_timeout(2500)
        ok(await pg.locator('[data-d="_final"]').count() >= 1, 'ESTH(10-29 심미치과학 N제)도 메뉴에 🎯 최종 N제')
        await pg.goto(U + '#/ANAT/_home'); await pg.wait_for_timeout(2500)
        ok(await pg.locator('[data-d="_final"]').count() == 0, 'N제 없는 과목은 메뉴 없음')
        ok(not errs, f'콘솔 오류 0 {errs[:2]}')
        await br.close()
    print('RESULT', 'FAIL' if fail else 'PASS')
asyncio.run(main())
