"""v3 폰 회귀(10-24 디자인 v3): 폰(393×852)에서 위에 붙는 영역 — 사용자 '폰 화면의 상단 절반을 위 탭으로 가리고 있는 오류'.
내린 뒤: 앱바(#top) 화면 밖 · 위에 붙은 것 아래 끝 ≤ 60px(탭 한 줄 — JB 화면은 거르기 작은 막대 한 줄 ≤ 90px) · 숨김↔보임 되풀이 없음 ·
조금 올리면 앱바가 다시 · 지금 탭이 탭 줄 안에 보임 · 데스크톱(1280)은 앱바를 숨기지 않음 · 콘솔 오류 0."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
COVER = """()=>{let mx=0,who='';for(const e of document.querySelectorAll('body *')){const cs=getComputedStyle(e);if(cs.position!=='sticky'&&cs.position!=='fixed')continue;if(e.closest('#kit,#side,#navbg,.pop,#retpill,.onebar,#bigclock,#toast'))continue;
 const r=e.getBoundingClientRect();if(r.width<200||r.height<4||r.top>4||r.bottom<=0||cs.visibility==='hidden'||cs.display==='none')continue;if(r.bottom>mx){mx=r.bottom;who=(e.id||e.className||e.tagName).toString().slice(0,40);}}
 const t=document.querySelector('#top').getBoundingClientRect();return {mx:Math.round(mx),who,top:Math.round(t.bottom),cls:document.body.className};}"""
TABVIS = """()=>{const on=document.querySelector('#dtabs .dtrow button.on'),row=document.querySelector('#dtabs .dtrow');if(!on||!row)return null;const a=on.getBoundingClientRect(),b=row.getBoundingClientRect();return a.left>=b.left-1&&a.right<=b.right+1;}"""
async def scroll(pg, dy, steps=12):
    for _ in range(steps):
        await pg.evaluate(f'window.scrollBy(0,{dy // steps})'); await pg.wait_for_timeout(40)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        ctx = await b.new_context(viewport={'width': 393, 'height': 852}, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.on('console', lambda m: errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
        for h, lim in [('#/GERI/OHQ/pred', 60), ('#/GERI/OHQ/learn', 60), ('#/GERI/OHQ/jb', 90), ('#/GERI/_jb/_jb', 90), ('#/OMS1/DD1/learn', 60), ('#/PHARM/HM/sum', 60), ('#/CONS/WHT/flash', 60)]:
            await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(1500)
            tv = await pg.evaluate(TABVIS)
            if tv is not None: ok(tv, f'{h} 지금 탭이 탭 줄 안에 보임')
            await scroll(pg, 1200); await pg.wait_for_timeout(300)
            await pg.evaluate("()=>{window.__flip=0;new MutationObserver(()=>window.__flip++).observe(document.body,{attributes:true,attributeFilter:['class']});}")
            await pg.wait_for_timeout(900)
            r = await pg.evaluate(COVER); fl = await pg.evaluate('window.__flip')
            ok(r['top'] <= 0, f'{h} 내린 뒤 앱바 숨김 (#top 아래 끝 {r["top"]})')
            ok(r['mx'] <= lim, f'{h} 내린 뒤 위에 붙은 영역 {r["mx"]}px ≤ {lim} ({r["who"]})')
            ok(fl <= 1, f'{h} 숨김↔보임 되풀이 없음 (몸 class 바뀜 {fl}번)')
            await scroll(pg, -120, 6); await pg.wait_for_timeout(500)
            r2 = await pg.evaluate(COVER)
            ok(r2['top'] >= 40, f'{h} 조금 올리면 앱바가 다시 (#top 아래 끝 {r2["top"]})')
        await ctx.close()
        pg = await b.new_page(viewport={'width': 1280, 'height': 900}); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(U + '#/GERI/OHQ/learn'); await pg.wait_for_timeout(1500); await scroll(pg, 1500); await pg.wait_for_timeout(600)
        r = await pg.evaluate(COVER)
        ok(r['top'] >= 40 and 'hdrhide' not in r['cls'], f'1280 앱바는 숨지 않음 (#top 아래 끝 {r["top"]})')
        ok(not errs, f'콘솔·페이지 오류 없음 {errs[:3]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
asyncio.run(main())
