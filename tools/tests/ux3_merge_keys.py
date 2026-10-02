"""ux3 병합 회귀: 세 트랙의 새 LS 키가 백업(dumpAll)에 들어가고, 빈 기기에 합치기(mergeData)하면 돌아오며, 기기 전용 키(tstate)는 건너뜀.
트랙1 navExp·navSec · 트랙2 tseg·tedit·trest·tgoalDay·sessAsk·calTab·restAuto·restMax(+tstate 기기 전용) · 트랙3 bcol·hcol·blabel·keyNoticeM
+ 계약: M(한글 ㅡ 포함) → sideToggle(body.sidefold) → 'jbl:layout' 이벤트 1번 · 상단 시계 알약 #clock[data-st](ux4 묶음2 — 메뉴 트래커 없음) · 맥 1280×900"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
NEW = {'navExp': {'CONS': 1}, 'navSec': {'res': 1},
       'tseg': {'2026-09-28': [[36000, 37800, 'CONS', 'WHT', 'a']]}, 'tedit': [{'i': 'abcd1234', 'at': 1, 'd': '2026-09-28', 'S': 'CONS', 'D': 'WHT', 'ms': 600000, 'k': 'add', 'g': [40000, 40600], 'x': 0}],
       'trest': {'2026-09-28': 300000}, 'tgoalDay': {'2026-09-28': 300}, 'sessAsk': 90, 'calTab': 'cal', 'restAuto': True, 'restMax': 60,
       'bcol': 'g', 'hcol': 'p', 'blabel': {'g': '수치'}, 'keyNoticeM': 1}
DEV = {'tstate': {'st': 'end', 'd': '2026-09-28'}}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        try:
            ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto(U + '#/'); await pg.wait_for_function("window.__h&&__h.dumpAll", timeout=30000)
            await pg.evaluate("S=>{localStorage.clear();for(const k in S)localStorage.setItem('jblhub.v1.'+k,JSON.stringify(S[k]));localStorage.setItem('jblhub.v1.tauto','false')}", {**NEW, **DEV})
            d = await pg.evaluate("__h.dumpAll()")
            miss = [k for k in list(NEW) + list(DEV) if 'jblhub.v1.' + k not in d]
            ok(not miss, f'백업(dumpAll)에 새 키 전부 {miss}')
            await pg.evaluate("localStorage.clear()")
            r = await pg.evaluate("d=>__h.mergeData(d)", d)
            got = await pg.evaluate("K=>K.map(k=>[k,localStorage.getItem('jblhub.v1.'+k)])", list(NEW) + list(DEV))
            bad = [k for k, v in got if k in NEW and (v is None or json.loads(v) != NEW[k])]
            ok(not bad, f'빈 기기에 합치기 → 새 키 그대로 {bad} (skip {r.get("skip")})')
            ok(dict(got)['tstate'] is None, 'tstate(측정 상태)는 기기 전용 — 합치지 않음')
            # 계약: M → sideToggle → jbl:layout
            await pg.evaluate("localStorage.clear()"); await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/sum')
            await pg.wait_for_selector('#stage .msum', timeout=30000); await pg.wait_for_timeout(400)
            ok(await pg.evaluate("!document.querySelector('#nav [data-trk]')&&!!document.querySelector('#top #clock[data-st] .ckl')"), "ux4 묶음2 계약: 메뉴에 트래커 없음 · 측정 상태는 상단 시계 알약(#clock[data-st])")
            await pg.evaluate("window.__lay=0;document.addEventListener('jbl:layout',()=>__lay++)")
            f0 = await pg.evaluate("document.body.classList.contains('sidefold')")   # 정리표는 SIDEAUTO로 접혀 시작할 수 있음
            w0 = await pg.evaluate("document.querySelector('#stage .msum').getBoundingClientRect().width")
            await pg.keyboard.press('Shift+M'); await pg.wait_for_function("__lay>=1", timeout=5000); await pg.wait_for_timeout(300)
            w1 = await pg.evaluate("document.querySelector('#stage .msum').getBoundingClientRect().width")
            f1 = await pg.evaluate("document.body.classList.contains('sidefold')")
            ok(f1 != f0 and abs(w1 - w0) > 200 and (w1 > w0) == f1, f'M → 메뉴 {"숨김" if f1 else "보임"}(sidefold {f0}→{f1}) · jbl:layout · 표 폭 {w0:.0f}→{w1:.0f}')
            await pg.evaluate("document.dispatchEvent(new KeyboardEvent('keydown',{key:'ㅡ',code:'KeyM',shiftKey:true,bubbles:true}))"); await pg.wait_for_function("__lay>=2", timeout=5000)
            ok(await pg.evaluate("document.body.classList.contains('sidefold')") == f0, '한글 입력 상태 M(ㅡ, KeyM) → 처음 상태로')
            ok(not errs, f'pageerror 0 {errs[:2]}')
            await ctx.close()
        finally:
            await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
    _sys.exit(1 if fails else 0)
asyncio.run(main())
