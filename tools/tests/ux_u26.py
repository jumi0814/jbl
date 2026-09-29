"""U26 회귀: 카드 머리 — 접기는 번호·영문 제목·▶만(요지 .one을 눌러도 열린 채, 형광펜 모드면 .one 단어가 칠해짐·새로고침 복원),
✓ → 사이드바 '읽음 n/m' 즉시 갱신 + 자동 접기·다음 카드가 탭 아래, 모두 접기 → 새로고침 → 열린 카드 0, 압축 보기 상태가 강의를 옮겨도 유지,
옛 done.<S> 기록 그대로 읽힘, 연도 칩 → 기출 탭 그 문항, '안 읽은 것만'. 820×1180 터치 · 1280×900."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1100):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
WORDXY = """(sel)=>{const e=document.querySelector(sel);e.scrollIntoView({block:'center'});const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){const m=/[A-Za-z가-힣]{3,}/.exec(x.nodeValue);if(m&&!x.parentElement.closest('button,.chip')){const r=document.createRange();r.setStart(x,m.index+1);r.setEnd(x,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2,m[0]];}}}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
        # 옛 done 기록
        aid0 = None
        await open_(pg, '#/OMS1/DD1/learn')
        aid0 = await pg.evaluate("document.querySelector('#t-DD1-0').dataset.aid")
        await pg.evaluate(f"localStorage.setItem('jblhub.v1.done.OMS1',JSON.stringify({{'{aid0}':1}}))")
        await open_(pg, '#/OMS1/DD1/learn')
        ok(await pg.evaluate("document.querySelector('#t-DD1-0').classList.contains('done')"), '옛 done.<S> 기록 → 카드 ✓')
        a = await pg.evaluate(WORDXY, '#t-DD1-2 .one'); await pg.touchscreen.tap(a[0], a[1]); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("document.querySelector('#t-DD1-2').classList.contains('open')"), '.one 탭 → 카드 열린 채')
        await pg.evaluate("document.querySelector('#k-h').click()")
        a = await pg.evaluate(WORDXY, '#t-DD1-2 .one'); await pg.touchscreen.tap(a[0], a[1]); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("!!document.querySelector('#t-DD1-2 .one [data-rk=h]') && document.querySelector('#t-DD1-2').classList.contains('open')"), f'형광펜 모드 .one 단어 칠함 ({a[2]})')
        await pg.evaluate("document.querySelector('#k-h').click()")
        await open_(pg, '#/OMS1/DD1/learn')
        ok(await pg.evaluate("!!document.querySelector('#t-DD1-2 .one [data-rk=h]')"), '새로고침 후 .one 형광펜 복원')
        # ✓ → 사이드바·자동 접기
        await pg.evaluate("document.querySelector('#t-DD1-3').scrollIntoView()")
        DN = "Object.keys(JSON.parse(localStorage.getItem('jblhub.v1.done.OMS1')||'{}')).length"
        s0 = await pg.evaluate(DN)
        await pg.evaluate("document.querySelector('#t-DD1-3 .dn').click()"); await pg.wait_for_timeout(900)
        s1 = await pg.evaluate(DN)
        ok(s1 == s0 + 1 and not await pg.evaluate("document.querySelector('#side .nvl[aria-current] small')") and '/' not in await pg.evaluate("document.querySelector('#side .nvl[aria-current]').textContent"), f'✓ → LS done 기록 {s0} → {s1} · 메뉴 강의 줄에는 읽음 n/N 없음(ux4 묶음2)')
        r = await pg.evaluate("(()=>{const c=document.querySelector('#t-DD1-3'),n=document.querySelector('#t-DD1-4');return [c.classList.contains('open'),Math.round(n.getBoundingClientRect().top-document.querySelector('#dtabs').getBoundingClientRect().bottom)]})()")
        ok(not r[0] and 0 <= r[1] <= 30, f'자동 접기·다음 카드가 탭 아래 {r}')
        await pg.screenshot(path=J.TMP + '/ux_u26_done_820.png')
        # 모두 접기 → 새로고침
        await pg.evaluate("document.querySelector('#lclose').click()"); await open_(pg, '#/OMS1/DD1/learn')
        ok(await pg.evaluate("document.querySelectorAll('#stage .tc.open').length") == 0, '모두 접기 → 새로고침 → 열린 카드 0')
        await pg.evaluate("document.querySelector('#lopen').click()")
        # 압축 보기 유지
        await pg.evaluate("document.querySelector('#lcond').click()"); await open_(pg, '#/OMS1/DD2/learn')
        ok(await pg.evaluate("document.querySelector('#stage').classList.contains('cond') && document.querySelector('#lmcond').classList.contains('on')"), '압축 보기 → 다른 강의에서도 유지')
        await pg.evaluate("document.querySelector('#lcond').click()")
        # 안 읽은 것만
        await open_(pg, '#/OMS1/DD1/learn'); await pg.evaluate("document.querySelector('[data-filt=unread]').click()"); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("getComputedStyle(document.querySelector('#t-DD1-0')).display==='none' && getComputedStyle(document.querySelector('#t-DD1-1')).display!=='none'"), '안 읽은 것만 → 읽은 카드 숨김')
        # 연도 칩
        await open_(pg, '#/OMS1/DD1/learn'); qid = await pg.evaluate("(()=>{const b=document.querySelector('#stage .tchips button.chip.yr');b.click();return b.dataset.go})()"); await pg.wait_for_timeout(900)
        ok(await pg.evaluate(f"location.hash.startsWith('#/OMS1/DD1/jb') && document.querySelector('#c-{qid}').getBoundingClientRect().top<400"), f'연도 칩 → 강의 기출 탭 {qid}')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
