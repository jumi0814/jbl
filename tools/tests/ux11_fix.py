"""UX11 전체 점검(10-10) 고친 것 회귀 — 허브 이동·범위·검색 위치·휴대폰 배치.
- 아직 안 온 과목 주소(#/PHARM/XE/learn) = 팩이 도착하면 그 강의로(홈에 머물지 않음)
- 과목 범위 검색(#/?q=…&s=CONS)·내 강의목록(#/_bm?s=PHARM)을 새로 열어도 범위 유지
- 검색 결과 → 찾은 글자 자리(접힌 25→26 알약은 펼침 · 글자 표시 sxhit) · 알약 색 설명은 색인에서 뺌
- 휴대폰(390): 공부 순서 글이 눌리지 않음 · 허브 홈 넘버링 카드·예상 연도 칩·넘버링 불러오기 창이 화면 안 · '이어서' 알림은 창을 열면 닫힘
- 메뉴 카드 목록 배지 'NEW 26'·'26 강조' · pageerror 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        # ---- 데스크톱 ----
        ctx = await b.new_context(viewport={'width': 1366, 'height': 900}); pg = await ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        # 1) 늦게 오는 과목으로 가는 주소
        async def slow(route):
            await asyncio.sleep(4); await route.continue_()
        await pg.route('**/packs/PHARM.js*', slow)
        await pg.goto(U + '#/'); await pg.wait_for_timeout(1500)
        pre = await pg.evaluate("!!__h.PACKS.PHARM")
        await pg.evaluate("location.hash='#/PHARM/XE/learn'"); await pg.wait_for_timeout(300)
        mid = await pg.evaluate("location.hash")
        for _ in range(40):
            await pg.wait_for_timeout(250)
            if await pg.evaluate("!!__h.PACKS.PHARM && __h.CUR.s==='PHARM'"): break
        st = await pg.evaluate("({h:location.hash,s:__h.CUR.s,d:__h.CUR.d})")
        ok(not pre and st['s'] == 'PHARM' and st['d'] == 'XE', f"아직 안 온 과목 주소 → 도착하면 그 강의 (도착 전 {pre} · 잠깐 {mid} → {st})")
        await pg.unroute('**/packs/PHARM.js*')
        # 2) 범위 유지 — 새로 열기
        pg2 = await ctx.new_page(); pg2.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg2.goto(U + '#/?q=bleaching&s=CONS'); await pg2.wait_for_timeout(4000)
        sr = await pg2.evaluate("({h:location.hash,g:document.querySelectorAll('#home .sgrp').length,t:[...document.querySelectorAll('#home .sgt')].map(x=>x.textContent.slice(0,12))})")
        ok('s=CONS' in sr['h'] and sr['g'] == 1, f"과목 범위 검색을 새로 열어도 범위 유지 {sr}")
        await pg2.goto(U + '#/_bm?s=PHARM'); await pg2.reload(); await pg2.wait_for_timeout(4000)
        bm = await pg2.evaluate("({h:location.hash,on:(document.querySelector('.hbmtabs .tg.on')||{}).dataset?.hbt,subs:[...document.querySelectorAll('.hbmsub')].map(x=>x.dataset.hbs)})")
        ok('s=PHARM' in bm['h'] and bm['on'] == 'PHARM' and bm['subs'] == ['PHARM'], f"내 강의목록 과목 탭을 새로 열어도 유지 {bm}")
        # 3) 검색 결과 → 글자 자리
        await pg2.goto(U + '#/?q=tragus&s=ANAT'); await pg2.wait_for_timeout(4000)
        await pg2.click('#home .res'); await pg2.wait_for_timeout(1500)
        hit = await pg2.evaluate("""(()=>{const H=CSS.highlights&&CSS.highlights.get('sxhit');if(!H)return {hl:false};const r=[...H][0],R=r.getBoundingClientRect(),dt=r.startContainer.parentElement.closest('details');return {hl:true,txt:r.toString(),inView:R.top>=0&&R.bottom<=innerHeight,open:dt?dt.open:null}})()""")
        ok(hit.get('hl') and hit.get('txt', '').lower() == 'tragus' and hit.get('inView') and hit.get('open') in (None, True), f"검색 결과 → 찾은 글자 표시·화면 안·접힌 곳 펼침 {hit}")
        await pg2.goto(U + '#/?q=' + '초록 NEW 26 ='.replace(' ', '%20')); await pg2.wait_for_timeout(4000)
        lead = await pg2.evaluate("(document.querySelector('#home .lead')||{}).textContent||''")
        ok(lead.startswith('0건'), f"25→26 알약 색 설명은 검색 색인에 없음 ({lead[:20]})")
        # 4) 메뉴 카드 목록 배지
        await pg2.goto(U + '#/CONS/CRK/learn'); await pg2.wait_for_timeout(3000)
        lab = await pg2.evaluate("[...new Set([...document.querySelectorAll('#side .scard2 small')].map(x=>x.textContent))]")
        ok(lab and set(lab) <= {'NEW 26', '26 강조'}, f"메뉴 카드 목록 배지 = NEW 26 · 26 강조 {lab}")
        await ctx.close()
        # ---- 휴대폰 ----
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True); pg = await ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(U + '#/'); await pg.wait_for_timeout(3000)
        hn = await pg.evaluate("Math.max(...[...document.querySelectorAll('.hnums .hnumb')].map(x=>x.getBoundingClientRect().right))")
        ok(hn <= 390, f"휴대폰 허브 홈 넘버링 카드가 화면 안 (오른쪽 {hn:.0f})")
        for S in ('IMPL', 'GERI', 'CONS'):
            await pg.evaluate(f"location.hash='#/{S}/_home/_home'"); await pg.wait_for_timeout(1500)
            w = await pg.evaluate("Math.min(...[...document.querySelectorAll('#hguide ol.steps>li .stx')].map(x=>x.getBoundingClientRect().width))")
            r = await pg.evaluate("Math.max(0,...[...document.querySelectorAll('#hguide .act')].map(x=>x.getBoundingClientRect().right))")
            ok(w >= 200 and r <= 390, f"휴대폰 {S} 공부 순서 글 폭 {w:.0f}px · 버튼 오른쪽 {r:.0f}")
        await pg.evaluate("location.hash='#/GERI/SAL/pred'"); await pg.wait_for_timeout(1500)
        cr = await pg.evaluate("Math.max(0,...[...document.querySelectorAll('.pc .jbchip')].map(x=>x.getBoundingClientRect().right))")
        ok(cr <= 390, f"휴대폰 예상 '관련 기출' 칩이 화면 안 (오른쪽 {cr:.0f})")
        await pg.evaluate("location.hash='#/_num/PHARM'"); await pg.wait_for_timeout(3000)
        await pg.evaluate("__h.toast('마지막으로 보던 문제부터 이어서 보여 드려요',{level:'result',id:'nmresume',ms:20000})"); await pg.wait_for_timeout(300)
        t0 = await pg.evaluate("getComputedStyle(document.getElementById('toast')).display")
        await pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); await pg.wait_for_timeout(900)
        t1 = await pg.evaluate("getComputedStyle(document.getElementById('toast')).display")
        dw = await pg.evaluate("(()=>{const b=document.querySelector('.nm-dlg .bd');return b?{sw:b.scrollWidth,cw:b.clientWidth,r:Math.round(b.getBoundingClientRect().right)}:null})()")
        ok(dw and dw['sw'] <= dw['cw'] + 1 and dw['r'] <= 390, f"휴대폰 넘버링 불러오기 창 내용이 창 안 {dw}")
        ok(t0 != 'none' and t1 == 'none', f"'이어서' 알림은 창을 열면 닫힘 ({t0} → {t1})")
        await ctx.close(); await b.close()
        ok(not errs, f"pageerror 0 {errs[:3]}")
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')

asyncio.run(main())
