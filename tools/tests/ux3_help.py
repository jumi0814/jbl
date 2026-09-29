"""ux3 묶음 P2 회귀: 도움말(?) '⌨ 모든 단축키' 한 표(모든 화면 키 — M 메뉴·Shift+M 메모·Shift+B 빈칸 색·\\·달력 ←→·T·A 포함) ·
'M = 메모' 문구 없음 · 옛 상단 [백업][복원]·'사이드바' 문구 없음 · 모든 [도움말 ▸]/data-wnh 링크가 실제 도움말 줄로 감 ·
새 기능 안내(whatsNew, LS whatsNew.3): 기록 없는 새 기기 = 안 뜸 · 1차 기기(ux2old) = 7줄 한 번 · 2차 판을 기록 없이 처음 열었던 기기(ux2old=0)도
3차를 처음 열 때 기록이 있으면 뜸(ux3old) · [알겠어요] → 다시 안 뜸 · 도움말 상자 가로 넘침 0.
맥 1280×900 · 아이패드 세로 820×1180(터치)·가로 1180×820(터치). 스크린샷 work/_tmp/ux3i_help_*.png"""
import os as _os, sys as _sys, re; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1300):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
LSK = lambda k: f"JSON.parse(localStorage.getItem('jblhub.v1.{k}')||'null')"
async def run(pg, tag, vp):
    # ---- 도움말 한 표
    await open_(pg, '#/')   # 새 컨텍스트 = 기록 없는 새 기기의 첫 열기
    ok(not await pg.evaluate("document.querySelector('#wnew')") and await pg.evaluate(LSK('ux3old')) == 0, '새 기기(기록 없음) → 새 기능 안내 없음 · ux3old=0')
    await pg.evaluate("localStorage.clear()"); await open_(pg, '#/CONS/WHT/learn')
    await pg.evaluate("document.querySelector('#helpb').click()"); await pg.wait_for_timeout(300)
    ht = await pg.inner_text('#help')
    kt = await pg.evaluate("(()=>{const s=document.querySelector('#help .hkt');return s?[...s.querySelectorAll('.hkg')].map(g=>[g.querySelector('.hkn').textContent,[...g.querySelectorAll('li')].map(l=>[l.querySelector('kbd').textContent,l.querySelector('span').textContent])]):null})()")
    ok(kt and len(kt) >= 8, f'⌨ 모든 단축키 묶음 {len(kt or [])}개')
    keys = {n: {k for k, _ in L} for n, L in (kt or [])}
    allk = set().union(*keys.values()) if keys else set()
    need = ['?', '/', 'Esc', 'M', 'Shift+M', 'V', 'T', 'H', 'Shift+H', 'B', 'Shift+B', 'E', 'N', 'Shift+N', '1~6', 'G', 'Q', 'J / K', 'D', 'F', 'C', 'R', 'I', 'Space', 'O / X', 'S', '← / →', 'Shift+← / →', 'A']
    miss = [k for k in need if k not in allk]
    ok(not miss, f'모든 화면 키가 한 표에 {miss}')
    cal = keys.get('📅 공부 달력', set())
    ok({'← / →', 'Shift+← / →', 'T', 'A'} <= cal, f'📅 달력 키 ←→·Shift+←→·T·A {sorted(cal)}')
    mrow = [t for n, L in (kt or []) for k, t in L if k == 'M']
    ok(mrow and '메뉴' in mrow[0] and '\\' in mrow[0], f'M = 왼쪽 메뉴(\\ 별칭) {mrow}')
    ok(not re.search(r'(?<!Shift\+)(?<!Shift\+\s)\bM\s*[=:·]?\s*메모', ht), "도움말에 'M 메모' 문구 없음(메모는 Shift+M)")
    ok('[백업]' not in ht and '[복원]' not in ht and '사이드바' not in ht, "옛 상단 [백업][복원]·'사이드바' 문구 없음")
    ths = await pg.evaluate("[...document.querySelectorAll('#help tbody th')].map(t=>t.textContent.trim())")
    ok(len(ths) == len(set(ths)), f'도움말 줄 이름 중복 0 ({len(ths)}줄)')
    ok(sum(1 for t in ths if 'M' in t.split() or t.endswith(' M')) == 1, f"M을 설명하는 줄은 하나('왼쪽 메뉴 M') {[t for t in ths if t.endswith(' M')]}")
    bad = await pg.evaluate("(()=>{const names=new Set([...document.querySelectorAll('#help tbody th')].map(t=>t.textContent.trim()).concat([...document.querySelectorAll('#help [data-hn]')].map(x=>x.dataset.hn)));return [...document.querySelectorAll('#help [data-wnh]')].map(b=>b.dataset.wnh).filter(n=>!names.has(n))})()")
    ok(not bad, f'도움말 안 링크가 모두 실제 줄로 {bad}')
    ov = await pg.evaluate("(()=>{const b=document.querySelector('#help .hbox');return [b.scrollWidth-b.clientWidth,[...b.querySelectorAll('.hkt li')].filter(l=>l.scrollWidth>l.clientWidth+1).length]})()")
    ok(ov[0] <= 0 and ov[1] == 0, f'도움말 상자·단축키 칸 가로 넘침 0 {ov}')
    await pg.screenshot(path=J.TMP + f'/ux3i_help_keys_{tag}.png')
    await pg.evaluate("document.querySelector('#help [data-wnh=\"⌨ 모든 단축키\"]').click()"); await pg.wait_for_timeout(250)
    ok(await pg.evaluate("document.querySelector('#help .hkt').classList.contains('flash')"), "'⌨ 모든 단축키' 링크 → 단축키 표로(flash)")
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(150)
    ok(not await pg.evaluate("document.querySelector('#help').classList.contains('on')"), 'Esc로 도움말 닫힘')
    # ---- 1차 기기: 기록이 있는 채로 3차 판을 처음 연다
    await pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.mk.OMS1',JSON.stringify({ok:{Q01:1},ng:{},bm:{},log:{}}))"); await open_(pg, '#/')
    await pg.wait_for_function("window.__h&&__h.plStat().pend===0", timeout=30000)
    w = await pg.evaluate("(()=>{const w=document.querySelector('#wnew');if(!w)return null;const r=w.getBoundingClientRect(),b=document.querySelector('.hband');return {n:w.querySelectorAll('li').length,t:w.textContent,top:Math.round(r.top),h:Math.round(r.height),band:b?Math.round(b.getBoundingClientRect().top):-1,ov:w.scrollWidth-w.clientWidth}})()")
    ok(w and w['n'] == 7, f"1차 기기 → '✨ 이번 업데이트' 7줄 {w and w['n']}")
    ok(w and all(x in w['t'] for x in ['왼쪽 메뉴', '오늘', '공부 달력', '세션', '빈칸 색', '표 폭', '🔑']), '3차 핵심(메뉴·오늘·달력·세션·빈칸 색·표 폭·🔑) 모두')
    ok(w and 'Shift+M' in w['t'] and w['ov'] <= 0, f"M 줄에 '메모는 Shift+M' · 가로 넘침 0")
    ok(w and w['h'] <= (360 if vp['width'] <= 860 else 300), f"안내 카드 높이 {w and w['h']}px(홈을 너무 밀지 않게)")
    await pg.screenshot(path=J.TMP + f'/ux3i_help_wnew_{tag}.png')
    links = await pg.evaluate("[...document.querySelectorAll('#wnew [data-wnh]')].map(b=>b.dataset.wnh)")
    for n in links:
        await pg.evaluate("n=>{document.querySelectorAll('#help .flash').forEach(x=>x.classList.remove('flash'));document.querySelector('#wnew [data-wnh=\"'+n+'\"]').click()}", n); await pg.wait_for_timeout(200)
        r = await pg.evaluate("[document.querySelector('#help').classList.contains('on'),((document.querySelector('#help tr.flash th')||{}).textContent||'')||((document.querySelector('#help .hkt.flash')||{}).dataset||{}).hn||'']")
        ok(r[0] and r[1] == n, f'[도움말 ▸] {n} → 그 줄 {r}')
        await pg.evaluate("document.querySelector('#helpx').click()"); await pg.wait_for_timeout(100)
    await open_(pg, '#/')
    ok(await pg.evaluate("!!document.querySelector('#wnew')"), '[알겠어요] 전에는 다시 열어도 보임')
    await pg.evaluate("document.querySelector('#wnew [data-wnx]').click()"); await pg.wait_for_timeout(200)
    ok(not await pg.evaluate("document.querySelector('#wnew')") and await pg.evaluate(LSK('whatsNew.3')) == 1, '[알겠어요] → 사라짐 · LS whatsNew.3=1')
    await open_(pg, '#/')
    ok(not await pg.evaluate("document.querySelector('#wnew')"), '새로고침 뒤에도 안 뜸(한 번)')
    # ---- 2차 판을 기록 없이 처음 열었던 기기(ux2old=0) + 그 뒤 쌓인 기록 → 3차 처음 열 때 안내
    await pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.ux2old','0');localStorage.setItem('jblhub.v1.time',JSON.stringify({'2026-09-20':{CONS:600000}}));localStorage.setItem('jblhub.v1.whatsNew.2','1')"); await open_(pg, '#/')
    ok(await pg.evaluate("!!document.querySelector('#wnew')") and await pg.evaluate(LSK('ux3old')) == 1, '2차 시작 기기(ux2old=0)도 기록이 있으면 3차 안내 · ux3old=1')
    await pg.evaluate("localStorage.clear()"); await open_(pg, '#/')
    await pg.evaluate("localStorage.setItem('jblhub.v1.time',JSON.stringify({'2026-09-20':{CONS:600000}}))"); await open_(pg, '#/')
    ok(not await pg.evaluate("document.querySelector('#wnew')"), '3차 판에서 새로 시작한 기기(ux3old=0)는 기록이 생겨도 안 뜸')
    ms = await pg.evaluate("(()=>{try{return __h&&__h.mskip?__h.mskip('ux3old'):null}catch(e){return null}})()")
    if ms is not None: ok(ms, 'ux3old는 기기 전용(MSKIP)')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for tag, vp, touch in [('mac', {'width': 1280, 'height': 900}, False), ('820', {'width': 820, 'height': 1180}, True), ('1180', {'width': 1180, 'height': 820}, True)]:
            ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
            await run(pg, tag, vp); ok(not errs, f'{tag} 콘솔 오류 0 {errs[:2]}'); await ctx.close()
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
