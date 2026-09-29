"""ux4 B1-1·B05 도구 막대 토글 [✎ 도구] — 집중 모드와 따로(LS kitoff 하나) · 1280×900 · 1180×820(터치) · 820×1180(터치)
강의 학습: [✎ 도구] → #kit 숨김·aria-pressed=false·LS kitoff=true → 다시 → 보임 · T(한글 입력 e.code=KeyT, key 'ㅅ')도 같음 ·
V로 집중 모드를 켜고 꺼도 #kit 표시가 그대로(켜짐·꺼짐 둘 다) · 막대의 ✕ = 도구 끔 · 새로고침 뒤 유지 · JB 한 장씩(집중 모드 포함)에서도 같은 버튼 ·
#kitshow·#k-min·#fpill·#modechip 요소 0 · 정리표·예상·JB 머리에도 [✎ 도구] · 콘솔 오류 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
ST = """(()=>{const k=document.querySelector('#kit'),b=[...document.querySelectorAll('[data-kitt]')].find(x=>x.offsetParent);return {kit:!!(k&&getComputedStyle(k).display!=='none'&&getComputedStyle(k).visibility!=='hidden'&&k.getBoundingClientRect().height>0),btn:b?b.getAttribute('aria-pressed'):null,ls:localStorage.getItem('jblhub.v1.kitoff'),focus:document.body.classList.contains('focus')}})()"""
KT = "document.dispatchEvent(new KeyboardEvent('keydown',{key:'ㅅ',code:'KeyT',bubbles:true}))"
KV = "document.dispatchEvent(new KeyboardEvent('keydown',{key:'ㅍ',code:'KeyV',bubbles:true}))"
async def clickkit(pg, touch):
    sel = await pg.evaluate("(()=>{const b=[...document.querySelectorAll('[data-kitt]')].find(x=>x.offsetParent);if(!b)return null;b.id=b.id||'ux4kt';return '#'+b.id})()")
    if touch: await pg.tap(sel)
    else: await pg.click(sel)
    await pg.wait_for_timeout(200)
async def run(b, tag, vp, touch):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
    await pg.goto(U + '#/'); await pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.tauto','false')")
    await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/learn'); await pg.wait_for_selector('#stage .tc', timeout=30000); await pg.wait_for_timeout(800)
    n = await pg.evaluate("['#kitshow','#k-min','#fpill','#modechip'].map(s=>document.querySelectorAll(s).length).reduce((a,b)=>a+b,0)")
    ok(n == 0, f'{tag} #kitshow·#k-min·#fpill·#modechip 요소 {n}')
    s0 = await pg.evaluate(ST); ok(s0['kit'] and s0['btn'] == 'true' and s0['ls'] is None, f'{tag} 처음: 도구 막대 보임·버튼 눌림 {s0}')
    await clickkit(pg, touch); s1 = await pg.evaluate(ST)
    ok(not s1['kit'] and s1['btn'] == 'false' and s1['ls'] == 'true', f'{tag} [✎ 도구] → 숨김·aria-pressed false·LS kitoff true {s1}')
    await pg.screenshot(path=J.TMP + f'/ux4i_kit_off_{tag}.png')
    await clickkit(pg, touch); s2 = await pg.evaluate(ST); ok(s2['kit'] and s2['btn'] == 'true' and s2['ls'] == 'false', f'{tag} 다시 → 보임 {s2}')
    await pg.evaluate(KT); await pg.wait_for_timeout(150); s3 = await pg.evaluate(ST); await pg.evaluate(KT); await pg.wait_for_timeout(150); s4 = await pg.evaluate(ST)
    ok(not s3['kit'] and s4['kit'], f'{tag} T(ㅅ·KeyT) → 숨김 → 보임 {s3["kit"]}/{s4["kit"]}')
    # 집중 모드와 따로
    await pg.evaluate(KV); await pg.wait_for_timeout(400); f1 = await pg.evaluate(ST)
    ok(f1['focus'] and f1['kit'], f'{tag} V(ㅍ) 집중 모드 켜도 도구 막대 그대로(보임) {f1}')
    await clickkit(pg, touch); f2 = await pg.evaluate(ST); ok(f2['focus'] and not f2['kit'] and f2['ls'] == 'true', f'{tag} 집중 모드 안에서 [✎ 도구] → 한 번에 숨김 {f2}')
    await pg.evaluate(KV); await pg.wait_for_timeout(400); f3 = await pg.evaluate(ST); ok(not f3['focus'] and not f3['kit'], f'{tag} 집중 끝 → 도구 막대 숨김 그대로 {f3}')
    await pg.reload(); await pg.wait_for_selector('#stage .tc', timeout=30000); await pg.wait_for_timeout(800); r1 = await pg.evaluate(ST)
    ok(not r1['kit'] and r1['btn'] == 'false', f'{tag} 새로고침 뒤 숨김 유지 {r1}')
    await clickkit(pg, touch); await pg.click('#k-hide') if not touch else await pg.tap('#k-hide'); await pg.wait_for_timeout(200); r2 = await pg.evaluate(ST)
    ok(not r2['kit'] and r2['btn'] == 'false' and r2['ls'] == 'true', f'{tag} 막대의 ✕ = 도구 끔(같은 상태) {r2}')
    await clickkit(pg, touch)
    # 다른 탭·문서 머리에도 같은 버튼
    for h, sel in [('#/CONS/WHT/sum', '#stage .msum'), ('#/CONS/WHT/pred', '#stage .pc'), ('#/CONS/_jb/_jb', '#cards .qc'), ('#/CONS/_sum/_sum', '#stage table')]:
        await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_selector(sel, timeout=30000); await pg.wait_for_timeout(600)
        a = await pg.evaluate(ST); await clickkit(pg, touch); b_ = await pg.evaluate(ST); await clickkit(pg, touch); c = await pg.evaluate(ST)
        ok(a['btn'] == 'true' and a['kit'] and not b_['kit'] and c['kit'], f'{tag} {h} 머리 [✎ 도구] 켜고 끔 {a["btn"]} {b_["kit"]} {c["kit"]}')
    # JB 한 장씩 × 집중 모드
    await pg.goto('about:blank'); await pg.goto(U + '#/CONS/_jb/_jb'); await pg.wait_for_selector('#cards .qc', timeout=30000); await pg.wait_for_timeout(600)
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(500)
    o1 = await pg.evaluate(ST); await clickkit(pg, touch); o2 = await pg.evaluate(ST); await clickkit(pg, touch); o3 = await pg.evaluate(ST)
    ok(o1['kit'] and o1['btn'] == 'true' and not o2['kit'] and o3['kit'], f'{tag} 한 장씩: 같은 [✎ 도구]로 켜고 끔 {o1["kit"]}/{o2["kit"]}/{o3["kit"]}')
    await pg.evaluate(KV); await pg.wait_for_timeout(400); o4 = await pg.evaluate(ST)
    await pg.screenshot(path=J.TMP + f'/ux4i_kit_jbone_focus_{tag}.png')
    ok(o4['focus'] and o4['kit'] and o4['btn'] == 'true', f'{tag} 한 장씩 × 집중 모드: 도구 막대·버튼 그대로 보임 {o4}')
    await clickkit(pg, touch); o5 = await pg.evaluate(ST); await clickkit(pg, touch); o6 = await pg.evaluate(ST)
    ok(not o5['kit'] and o6['kit'], f'{tag} 한 장씩 × 집중 모드에서도 켜고 끔 {o5["kit"]}/{o6["kit"]}')
    await pg.evaluate(KV); await pg.wait_for_timeout(300)
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
