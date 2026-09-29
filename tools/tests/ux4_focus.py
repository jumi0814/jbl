"""ux4 B1-2·B01 집중 모드 가운데 정렬 — 1280×900 · 1180×820(터치) · 820×1180(터치)
학습·정리표·예상·JB·기출 한눈표에서 V → 첫 본문 단위(.tc·.tblwrap·.pc·.qc)의 좌우 여백 차 ≤2px · 도구 막대 중심 = 화면 가운데 ±2 ·
상단 막대·메뉴·hero 숨김, 탭 줄이 맨 위(top 0) · [집중 끝]·Esc·V로 나가짐 · 1280 M 숨김(sidefold)에서도 같음 · #fpill 없음 ·
B03 읽던 자리: 카드 중간을 보다가 V 켜고 끄기 → 같은 카드·거리(±40px) · 콘솔 오류 0 · 스크린샷 work/_tmp/ux4i_focus_<폭>_<화면>.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
VIEWS = [('learn', '#/CONS/WHT/learn', '#stage .tc'), ('sum', '#/CONS/WHT/sum', '#stage .msum'), ('pred', '#/CONS/WHT/pred', '#stage .pc'), ('jb', '#/CONS/_jb/_jb', '#cards .qc'), ('sumall', '#/CONS/_sum/_sum', '#stage table')]
M = """(sel=>{const el=[...document.querySelectorAll(sel)].find(e=>e.offsetParent&&e.getBoundingClientRect().height>0);const W=document.documentElement.clientWidth;const r=el.getBoundingClientRect();const k=document.querySelector('#kit'),kr=k.getBoundingClientRect();
 const t=document.querySelector('#top'),d=document.querySelector('#dtabs');return {l:Math.round(r.left),r:Math.round(W-r.right),kc:Math.round((kr.left+kr.right)/2),W,top:getComputedStyle(t).display,hero:getComputedStyle(document.querySelector('#hero')).display,
 side:getComputedStyle(document.querySelector('#side')).display,dt:d.offsetParent?Math.round(d.getBoundingClientRect().top):null,fo:document.body.classList.contains('focus'),fp:document.querySelectorAll('#fpill').length}})"""
UNIT = {'learn': '#stage .tc', 'sum': '#stage .tblwrap', 'pred': '#stage .pc', 'jb': '#cards .qc', 'sumall': '#stage .tblwrap'}
KV = "document.dispatchEvent(new KeyboardEvent('keydown',{key:'ㅍ',code:'KeyV',bubbles:true}))"
async def run(b, tag, vp, touch):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
    await pg.goto(U + '#/'); await pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.tauto','false')")
    for fold in ([False, True] if vp['width'] > 860 else [False]):
        await pg.evaluate(f"localStorage.setItem('jblhub.v1.navfold',{'true' if fold else 'false'});localStorage.setItem('jblhub.v1.wideSide',1);localStorage.setItem('jblhub.v1.focus','false')")
        for name, h, sel in VIEWS:
            await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_selector(sel, timeout=30000); await pg.wait_for_timeout(700)
            await pg.evaluate("scrollTo(0,300)"); await pg.wait_for_timeout(200)
            await pg.evaluate(KV); await pg.wait_for_timeout(600)
            r = await pg.evaluate(M, UNIT[name]); ft = f'{tag}{"·M숨김" if fold else ""} {name}'
            ok(r['fo'] and abs(r['l'] - r['r']) <= 2, f'{ft}: 집중 모드 본문 좌우 여백 {r["l"]}/{r["r"]}')
            ok(abs(r['kc'] - r['W'] / 2) <= 2, f'{ft}: 도구 막대 가운데 {r["kc"]} (화면 {r["W"] / 2})')
            ok(r['top'] == 'none' and r['hero'] == 'none' and r['dt'] == 0 and r['fp'] == 0, f'{ft}: 상단 막대·hero 숨김·탭 줄 맨 위 {r["top"]} {r["hero"]} dt={r["dt"]} fpill={r["fp"]}')
            if not fold: await pg.screenshot(path=J.TMP + f'/ux4i_focus_{tag}_{name}.png')
            # 나가기: 이름 차례로 [집중 끝] · Esc · V
            how = {'learn': 'btn', 'sum': 'esc', 'pred': 'v', 'jb': 'btn', 'sumall': 'esc'}[name]
            if how == 'btn':
                bsel = await pg.evaluate("(()=>{const b=[...document.querySelectorAll('.dfoc')].find(x=>x.offsetParent);b.id=b.id||'ux4fb';return [b.id,b.textContent]})()")
                ok(bsel[1] == '집중 끝', f'{ft}: 집중 버튼 글자 = 집중 끝 ({bsel[1]})')
                await (pg.tap('#' + bsel[0]) if touch else pg.click('#' + bsel[0]))
            elif how == 'esc': await pg.keyboard.press('Escape')
            else: await pg.evaluate(KV)
            await pg.wait_for_timeout(500); r2 = await pg.evaluate(M, UNIT[name])
            ok(not r2['fo'] and r2['top'] != 'none', f'{ft}: {how}로 집중 끝 → 상단 막대 다시 {r2["top"]}')
            if fold and vp['width'] > 860:
                ok(abs(r2['l'] - r2['r']) <= 2 or name in ('sum', 'sumall'), f'{ft}: M 숨김(집중 아님) 본문 좌우 여백 {r2["l"]}/{r2["r"]}')
    # B03 읽던 자리 — 카드 7 중간을 보다가 V 켜고 끄기
    await pg.evaluate("localStorage.setItem('jblhub.v1.navfold','false')")
    await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/learn'); await pg.wait_for_selector('#stage .tc', timeout=30000); await pg.wait_for_timeout(800)
    P = "(()=>{const c=document.querySelector('#t-WHT-6');const d=document.querySelector('#dtabs').getBoundingClientRect();return Math.round(c.getBoundingClientRect().top-d.bottom)})()"
    await pg.evaluate("(()=>{const c=document.querySelector('#t-WHT-6');c.classList.add('open');const d=document.querySelector('#dtabs').getBoundingClientRect();scrollTo(0,scrollY+c.getBoundingClientRect().top-d.bottom-12+400)})()"); await pg.wait_for_timeout(600)
    a0 = await pg.evaluate(P); await pg.evaluate(KV); await pg.wait_for_timeout(1500); a1 = await pg.evaluate(P); await pg.evaluate(KV); await pg.wait_for_timeout(1500); a2 = await pg.evaluate(P)
    ok(abs(a1 - a0) <= 40 and abs(a2 - a0) <= 40, f'{tag} B03 V 켜고 끄기 뒤 읽던 자리 {a0} → {a1} → {a2}')
    ok(not errs, f'{tag} 콘솔 오류 0 {errs[:3]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        try:
            for tag, vp, touch in [('1280', {'width': 1280, 'height': 900}, False), ('1180', {'width': 1180, 'height': 820}, True), ('820', {'width': 820, 'height': 1180}, True)]:
                await run(b, tag, vp, touch)
        finally:
            await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
