"""U31 회귀: 학습 탭 끝 '다음 할 일' — DD1 맨 끝 패널: 기출 풀기(→ 강의 기출 탭·안 푼 것 필터)·플래시카드·다음 강의(DD2 학습),
읽음 안 한 카드 n개 → 첫 미읽음 카드, 마지막 강의는 '과목 홈으로', 기출·정리표 탭 끝 '📖 학습으로 돌아가기 · 다음 강의'."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1000):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for vp, touch, tag in [({'width': 1280, 'height': 900}, False, '1280'), ({'width': 820, 'height': 1180}, True, '820')]:
            ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
            await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
            await open_(pg, '#/OMS1/DD1/learn')
            ok(await pg.evaluate("(()=>{const n=document.querySelector('#stage #nextp');return !!n&&n===document.querySelector('#stage').lastElementChild})()"), '학습 맨 끝 다음 할 일 패널')
            await pg.evaluate("document.querySelector('#nextp').scrollIntoView()"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=J.TMP + f'/ux_u31_next_{tag}.png')
            await pg.click('#nextp [data-nx="jb"]'); await pg.wait_for_timeout(900)
            ok(await pg.evaluate("location.hash.startsWith('#/OMS1/DD1/jb') && document.querySelector('#jbbar [data-qf=todo]').classList.contains('on')"), '기출 풀기 → 강의 기출 탭·안 푼 것')
            ok(await pg.evaluate("!!document.querySelector('#stage .nextl [data-nx=learn]')"), '기출 탭 끝 학습으로 돌아가기 줄')
            await open_(pg, '#/OMS1/DD1/learn'); await pg.click('#nextp [data-nx="flash"]'); await pg.wait_for_timeout(700)
            ok(await pg.evaluate("location.hash.startsWith('#/OMS1/DD1/flash') && !!document.querySelector('#fcard')"), '플래시카드로')
            await open_(pg, '#/OMS1/DD1/learn'); await pg.click('#nextp [data-nx="next"]'); await pg.wait_for_timeout(700)
            ok(await pg.evaluate("location.hash.startsWith('#/OMS1/DD2/learn')"), '다음 강의 → DD2 학습')
            await open_(pg, '#/OMS1/DD1/learn'); await pg.evaluate("document.querySelector('#t-DD1-0 .dnend').click()"); await pg.wait_for_timeout(700)
            ok(await pg.evaluate("!document.querySelector('#nextp [data-nx=unread]')&&!/읽음/.test(document.querySelector('#nextp').innerText)"), 'ux4 B1-6 다음 할 일에 읽음 수·안 읽은 카드 링크 없음')
            await open_(pg, '#/OMS1/REP/learn')
            ok(await pg.evaluate("!!document.querySelector('#nextp [data-nx=home]') && !document.querySelector('#nextp [data-nx=next]')"), '마지막 강의 → 과목 홈으로')
            await open_(pg, '#/OMS1/DD1/sum')
            ok(await pg.evaluate("!!document.querySelector('#stage .nextl [data-nx=next]')"), '정리표 끝 다음 강의 줄')
            ok(not errs, f'pageerror 0 {errs[:2]}')
            await ctx.close()
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
