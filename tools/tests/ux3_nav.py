"""ux3 트랙1 묶음 G 회귀 — 전역 왼쪽 메뉴(#app 격자·navRender·sideToggle·서랍·revInfo 캐시).
모든 화면에 #side · aria-current · 과목 전환 1탭 · ▸ 펼침 저장(주소 그대로) · ESTH 준비 중 · ↪ 이어서 · 💾 → 백업 창·복원 ·
메뉴 숨기기(\\ · ‹ · ›) 새로고침 유지 + 'jbl:layout' 한 번 + #main +248 · 820 서랍(☰ · 도구 막대 숨김 · 강의 누르면 닫힘 · 과목 줄은 펼치기만) ·
1분 타이머 = 배지 글자만 · revInfo 과목당 1회 · 채점하면 🔁 배지 즉시. 맥 1280×900 + 아이패드 가로 1180×820·세로 820×1180(터치).
스크린샷 work/_tmp/ux3i_g_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, time
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, wait=300):
    await pg.goto('about:blank'); await pg.goto(U + h)
    await pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .nvs')", timeout=30000); await pg.wait_for_timeout(wait)
CURSEL = "[...document.querySelectorAll('#side [aria-current]')].map(e=>(e.dataset.nv||e.dataset.nvs||e.dataset.d||e.className))"
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    print('==', tag); W = vp['width']; narrow = W <= 860
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await open_(pg, '#/')
    # ---- G1·G2 모든 화면에 메뉴 · aria-current
    views = [('#/', 'home', 'home'), ('#/_time', 'cal', 'time'), ('#/?q=%EB%AF%B8%EB%B0%B1', None, 'search'), ('#/CONS/_home/_home', 'CONS', 'shome'),
             ('#/CONS/WHT/learn', 'WHT', 'learn'), ('#/CONS/WHT/sum', 'WHT', 'sum'), ('#/CONS/_jb/_jb', '_jb', 'jb'), ('#/CONS/_marks/_marks', 'marks', 'marks')]
    for h, want, nm in views:
        await open_(pg, h, 500)
        r = await pg.evaluate("(()=>{const s=document.querySelector('#side'),cs=getComputedStyle(s),B=document.body.classList;return {vis:cs.visibility,w:Math.round(s.getBoundingClientRect().width),fold:B.contains('sidefold'),open:document.querySelector('#sideopen')?getComputedStyle(document.querySelector('#sideopen')).display:'',nvs:document.querySelectorAll('#side .nvs').length,ovx:document.documentElement.scrollWidth-innerWidth}})()")
        cur = await pg.evaluate(CURSEL)
        if narrow: shown = r['nvs'] == 7 and r['vis'] == 'hidden'   # 서랍 닫힘
        elif r['fold']: shown = r['open'] == 'flex' and r['nvs'] == 7   # 정리표 자동 숨김 → › 손잡이
        else: shown = r['vis'] == 'visible' and r['w'] >= 230 and r['nvs'] == 7
        ok(shown and r['ovx'] <= 0, f'{tag} {nm}: 메뉴 {r}')
        if want: ok(want in cur, f'{tag} {nm}: aria-current {cur} ∋ {want}')
        else: ok(not cur, f'{tag} {nm}: 검색 화면은 aria-current 없음 {cur}')
        if nm in ('home', 'learn', 'sum') : await pg.screenshot(path=J.TMP + f'/ux3i_g_{tag}_{nm}.png')
    # ---- G3 과목 7줄 · ESTH · 과목 전환 1탭 · ▸ 펼침 저장
    await open_(pg, '#/CONS/WHT/learn')
    es = await pg.evaluate("(()=>{const e=document.querySelector('#side .nvs[data-s=ESTH] .nvsb');return e?[e.getAttribute('aria-disabled'),e.textContent]:null})()")
    ok(es and es[0] == 'true' and '준비 중' in es[1], f'{tag} ESTH 준비 중 aria-disabled {es}')
    if narrow: await pg.click('#navbtn'); await pg.wait_for_timeout(300)
    h0 = await pg.evaluate("location.hash"); await pg.click('#side .nvx[data-nvx="GERI"]'); await pg.wait_for_timeout(250)
    ok(await pg.evaluate("location.hash") == h0 and await pg.evaluate("!!document.querySelector('#side .nvs[data-s=GERI] .nvbody')"), f'{tag} ▸ → 펼침(주소 그대로)')
    await open_(pg, '#/CONS/WHT/learn')
    ok(await pg.evaluate("!!document.querySelector('#side .nvs[data-s=GERI].open .nvdocs') && JSON.parse(localStorage.getItem('jblhub.v1.navExp')).GERI===1"), f'{tag} 새로고침 뒤에도 GERI 펼침(LS navExp)')
    nd = await pg.evaluate("document.querySelectorAll('#side .dbtn').length"); ok(nd == 14, f"{tag} 지금 과목 문서 칩 7 + 강의 7만 .dbtn ({nd})")
    ok(await pg.evaluate("!document.querySelector('#sjsel')&&!document.querySelector('#side .hubhome')"), f'{tag} #sjsel·허브 홈 줄 없음')
    if narrow:
        await pg.click('#navbtn'); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[document.body.classList.contains('navopen'),getComputedStyle(document.querySelector('#kit')).visibility,getComputedStyle(document.querySelector('#navbg')).display,Math.round(document.querySelector('#side').getBoundingClientRect().width)]")
        ok(r[0] and r[1] == 'hidden' and r[2] == 'block' and 300 <= r[3] <= 322, f'{tag} ☰ → 서랍 열림 · 도구 막대 숨김 · 배경 {r}')
        await pg.screenshot(path=J.TMP + f'/ux3i_g_{tag}_drawer.png')
        await pg.click('#side .nvsb[data-nvs="ANAT"]'); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("document.body.classList.contains('navopen') && !!document.querySelector('#side .nvs[data-s=ANAT] .nvl') && location.hash.indexOf('CONS')>0"), f'{tag} 서랍에서 과목 줄 = 펼치기만(서랍 열림·주소 그대로)')
        await pg.click('#side .nvs[data-s=ANAT] .nvl >> nth=0'); await pg.wait_for_timeout(900)
        ok(await pg.evaluate("!document.body.classList.contains('navopen') && location.hash.indexOf('#/ANAT/')===0 && /\\/learn$/.test(location.hash)"), f'{tag} 서랍 강의 줄 → 이동·서랍 닫힘 ({await pg.evaluate("location.hash")})')
        await pg.click('#navbtn'); await pg.wait_for_timeout(250); await pg.click('#navbg', position={'x': W - 40, 'y': 400}); await pg.wait_for_timeout(250)
        ok(not await pg.evaluate("document.body.classList.contains('navopen')"), f'{tag} 배경 누르면 서랍 닫힘')
        await pg.keyboard.press('Backslash'); await pg.wait_for_timeout(250); ok(await pg.evaluate("document.body.classList.contains('navopen')"), f'{tag} \\ → 서랍'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
    else:
        await pg.click('#side .nvsb[data-nvs="ANAT"]'); await pg.wait_for_timeout(700)
        ok(await pg.evaluate("location.hash.indexOf('#/ANAT/_home')===0 && !!document.querySelector('#side .nvs[data-s=ANAT].cur .nvdocs')"), f'{tag} 과목 줄 1탭 → ANAT 과목 홈·펼침')
        # 메뉴 높이(과목 하나 펼침 · 과목 홈)
        await pg.evaluate("localStorage.removeItem('jblhub.v1.navExp');__h.navRender()")
        hh = await pg.evaluate("(()=>{const n=document.querySelector('#nav');return [...n.children].reduce((a,c)=>a+(c.id==='navsc'?c.scrollHeight:c.offsetHeight),0)})()")
        ok(W != 1280 or hh <= 900, f'{tag} 과목 하나 펼친 메뉴 전체 높이 {hh} ≤ 900')
        await pg.click('#side .nvd.dbtn[data-d="_jb"]'); await pg.wait_for_timeout(700)
        ok(await pg.evaluate("location.hash.indexOf('#/ANAT/_jb')===0"), f'{tag} 문서 칩 📝 JB → ANAT JB')
    # ---- G2 ↪ 이어서 · 🖍 내 표시 · 💾
    await open_(pg, '#/CONS/WHT/learn', 600); await pg.evaluate("document.querySelector('#t-WHT-6').scrollIntoView({block:'start'});scrollBy(0,-80)"); await pg.wait_for_timeout(1300)
    await open_(pg, '#/')
    if narrow: await pg.click('#navbtn'); await pg.wait_for_timeout(300)
    rs = await pg.evaluate("[...document.querySelectorAll('#side .nvrs')].map(e=>e.textContent)")
    ok(any('보존' in x and 'Tooth' in x or '미백' in x for x in rs) or any('보존' in x for x in rs), f'{tag} ↪ 이어서 줄 {rs}')
    await pg.click('#side .nvrs >> nth=0'); await pg.wait_for_timeout(1200)
    ok(await pg.evaluate("location.hash.indexOf('#/CONS/WHT/learn')===0 && scrollY>300"), f'{tag} ↪ 이어서 → 읽던 카드 위치 (y={await pg.evaluate("scrollY")})')
    await pg.evaluate("document.querySelector('#bkup').click()"); await pg.wait_for_timeout(200)
    ok(await pg.evaluate("document.querySelector('#bkpop').classList.contains('on') && !!document.querySelector('#bkpop #bksend') && !!document.querySelector('#bkpop #rstr')"), f'{tag} 💾 → 백업 창(보내기·받기·복원)')
    await pg.click('#rstr'); await pg.wait_for_selector('#rpop.on .rstore', timeout=8000)
    ok(not await pg.evaluate("document.querySelector('#bkpop').classList.contains('on')"), f'{tag} ↺ 복원 → 복원 창(백업 창 닫힘)')
    await pg.keyboard.press('Escape')
    # ---- G2 1분 타이머 = 배지 글자만
    await open_(pg, '#/CONS/_home/_home')
    L0 = await pg.evaluate("document.querySelector('#nav').innerHTML.length"); await pg.evaluate("__h.navBadges()"); L1 = await pg.evaluate("document.querySelector('#nav').innerHTML.length")
    ok(abs(L1 - L0) <= 4, f'{tag} 배지 갱신은 다시 그리지 않음 ({L0} → {L1})')
    # ---- G6 revInfo 과목당 1회 · 채점 → 🔁 배지 1초 안
    await open_(pg, '#/'); n0 = await pg.evaluate("__h.rvcN()"); await pg.evaluate("__h.navRender()"); n1 = await pg.evaluate("__h.rvcN()")
    ok(0 < n0 <= 6 and n1 == n0, f'{tag} 허브 홈을 그려도 revInfo 계산 = 과목당 1회({n0}) · 다시 그려도 0회 추가({n1 - n0})')
    await open_(pg, '#/CONS/_jb/_jb', 600)
    await pg.evaluate("(()=>{const c=document.querySelector('#cards .qc:not(.hid)');c.querySelector('.mk.ng,[data-mk=ng]').click();})()"); await pg.wait_for_timeout(700)
    rv = await pg.evaluate("[(document.querySelector('#side [data-nb=\"rv.CONS\"]')||{}).textContent,(document.querySelector('#side [data-nb=\"rv\"]')||{}).textContent,__h.revInfo('CONS').due.size]")
    ok(rv[2] >= 1 and rv[0] == '🔁' + str(rv[2]) and rv[1] == str(rv[2]), f'{tag} ✗ 채점 → 메뉴 🔁 배지 즉시 {rv}')
    # ---- G5 메뉴 숨기기
    if not narrow:
        await open_(pg, '#/CONS/WHT/learn'); await pg.evaluate("['sidefold','wideSide','focus'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))"); await open_(pg, '#/CONS/WHT/learn')
        await pg.evaluate("window.__lev=0;document.addEventListener('jbl:layout',()=>__lev++)")
        m0 = await pg.evaluate("document.querySelector('#main').getBoundingClientRect().width")
        await pg.keyboard.press('Backslash'); await pg.wait_for_timeout(500)
        r = await pg.evaluate("[document.body.classList.contains('sidefold'),Math.round(document.querySelector('#main').getBoundingClientRect().width),__lev,getComputedStyle(document.querySelector('#sideopen')).display,getComputedStyle(document.querySelector('#navbtn')).display,JSON.parse(localStorage.getItem('jblhub.v1.sidefold'))]")
        ok(r[0] and r[1] - m0 == (248 if W >= 1024 else 232) and r[2] == 1 and r[3] == 'flex' and r[4] != 'none' and r[5] is True, f'{tag} \\ → 메뉴 숨김 · #main {m0}→{r[1]} · jbl:layout {r[2]}회 · › {r[3]} · ☰ {r[4]}')
        await open_(pg, '#/CONS/WHT/learn'); ok(await pg.evaluate("document.body.classList.contains('sidefold')"), f'{tag} 새로고침 뒤에도 숨김')
        await pg.screenshot(path=J.TMP + f'/ux3i_g_{tag}_fold.png')
        await pg.click('#sideopen'); await pg.wait_for_timeout(450)
        ok(not await pg.evaluate("document.body.classList.contains('sidefold')"), f'{tag} › → 펼침')
        await pg.click('#side .nvhead [data-nvfold]'); await pg.wait_for_timeout(450); ok(await pg.evaluate("document.body.classList.contains('sidefold')"), f'{tag} 메뉴 머리 ‹ → 숨김')
        await pg.click('#navbtn'); await pg.wait_for_timeout(450); ok(not await pg.evaluate("document.body.classList.contains('sidefold')"), f'{tag} 상단 ☰ → 펼침')
        # 집중 모드에서 펼치기 = 집중 모드 끔
        await pg.keyboard.press('v'); await pg.wait_for_timeout(300); await pg.evaluate("__h.sideToggle()"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("!document.body.classList.contains('focus')&&!document.body.classList.contains('sidefold')&&getComputedStyle(document.querySelector('#side')).display!=='none'"), f'{tag} 집중 모드 중 메뉴 펼치기 → 집중 모드 끔')
        # 정리표 자동 숨김(≤1440) · › → wideSide
        await open_(pg, '#/CONS/WHT/sum', 700)
        ok(await pg.evaluate("document.body.classList.contains('sidefold')") == (W <= 1440), f'{tag} 정리표 1440 이하 자동 숨김')
        await pg.click('#sideopen'); await pg.wait_for_timeout(450)
        ok(await pg.evaluate("localStorage.getItem('jblhub.v1.wideSide')") == '1', f'{tag} 정리표에서 › → wideSide=1')
        await pg.evaluate("['sidefold','wideSide'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))")
    ok(not errs, f'{tag} 콘솔·페이지 오류 0 {errs[:3]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 1180, 'height': 820}, True, 'land')
        await run(b, {'width': 820, 'height': 1180}, True, 'port')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
