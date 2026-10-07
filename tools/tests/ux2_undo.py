"""C06 회귀: 실행 취소 — 무엇을 되돌렸는지 알리기
학습 탭에서 형광펜 1개 → 기출 탭으로 → ⌘Z → 토스트 '↶ 되돌림: 형광펜 1개 (… 학습)' + [그 화면으로](누르면 학습 탭) · ⌘⇧Z 다시 · 새로고침 뒤에도 ⌘Z ·
80단계 스택 JSON 길이 합 ≤ 예전(단계마다 ANN 전체)의 1/10 · 다른 창이 같은 aid를 바꾸면 그 aid 항목만 무효(다른 aid 항목은 남음).
맥 1280×900 + 아이패드 세로 820×1180 · 가로 1180×820. 스크린샷 work/_tmp/ux2i_c06_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
PICK = '''(n=>{const lis=[...document.querySelectorAll('#stage .tc [data-aid] li,#stage .tc li')].filter(l=>l.offsetParent&&!l.closest('details:not([open])')&&!l.querySelector('[data-rk]')&&/[A-Za-z가-힣]{3}/.test(l.textContent));const li=lis[n];li.scrollIntoView({block:'center'});const w=document.createTreeWalker(li,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){const m=/[A-Za-z가-힣]{3,}/.exec(x.nodeValue);if(m&&!x.parentElement.closest('button,.chip,.noann,[data-rk]')){const r=document.createRange();r.setStart(x,m.index+1);r.setEnd(x,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2,m[0],li.closest('[data-aid]').dataset.aid];}}})'''
HN = "document.querySelectorAll('#stage [data-rk=h]').length"
async def toast_with(pg, sub, timeout=6000):
    await pg.wait_for_function(f"(()=>{{const e=document.querySelector('#toast');return e&&getComputedStyle(e).display!=='none'&&e.textContent.includes({json.dumps(sub)});}})()", timeout=timeout)
    return await pg.inner_text('#toast')
async def run(b, vp, touch, tag, full):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept()); print('==', tag)
    await pg.goto(U + '#/OMS1/DD1/learn'); await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3")
    await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await pg.reload(); await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3"); await pg.wait_for_timeout(400)
    await pg.keyboard.press('h'); a = await pg.evaluate(PICK + '(1)'); await pg.mouse.click(a[0], a[1]); await pg.wait_for_timeout(150); await pg.keyboard.press('Escape')
    ok(await pg.evaluate(HN) == 1, f'학습 탭 형광펜 1개 ("{a[2]}")')
    await pg.click('#dtabs button[data-t="jb"]'); await pg.wait_for_function("location.hash.indexOf('/jb')>0"); await pg.wait_for_timeout(300)
    await pg.keyboard.press('Meta+z')
    t = await toast_with(pg, '되돌림'); ok('형광펜 1개' in t and '학습' in t and '그 화면으로' in t, f'토스트 {t!r}')
    await pg.screenshot(path=J.TMP + f'/ux2i_c06_toast_{tag}.png')
    ann = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')") or '{}'); ok(not any(ann.values()), '기록에서 빠짐')
    await pg.click('#toast .tact'); await pg.wait_for_function("location.hash.indexOf('/learn')>0"); await pg.wait_for_timeout(300)
    ok(True, '[그 화면으로] → 학습 탭')
    await pg.keyboard.press('Meta+Shift+z'); t = await toast_with(pg, '다시 실행'); ok(await pg.evaluate(HN) == 1 and '형광펜 1개' in t and '그 화면으로' not in t, f'다시 실행 → 복귀·같은 화면이면 버튼 없음 {t!r}')
    await pg.reload(); await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3"); await pg.wait_for_timeout(500)
    ok(await pg.evaluate("__h.Kit.undoN()") >= 1, f"새로고침 뒤 되돌릴 수 있는 단계 {await pg.evaluate('__h.Kit.undoN()')}")
    await pg.keyboard.press('Meta+z'); await pg.wait_for_timeout(250); ok(await pg.evaluate(HN) == 0, '새로고침 뒤 ⌘Z 동작')
    if full:
        # 80단계 스택 크기 — 큰 ANN(다른 카드 표시 400개)을 깔고 같은 낱말을 80번 칠하고 지움
        seed = await pg.evaluate("""(()=>{const aids=[...document.querySelectorAll('#stage .tc')].map(e=>e.dataset.aid);const A={};aids.slice(8).forEach((aid,j)=>{A[aid]=[];for(let i=0;i<Math.ceil(400/Math.max(1,aids.length-8));i++)A[aid].push({t:'h',x:'없는낱말'+j+'_'+i,i:0,c:'y',p:'앞문맥앞문맥앞문맥',s:'뒤문맥뒤문맥뒤문맥',v:'abc123',lost:1});});localStorage.setItem('jblhub.v1.ann.OMS1',JSON.stringify(A));return JSON.stringify(A).length;})()""")
        await pg.evaluate("sessionStorage.clear()"); await pg.reload(); await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3"); await pg.wait_for_timeout(500)
        await pg.keyboard.press('h'); a = await pg.evaluate(PICK + '(1)'); await pg.wait_for_timeout(100)
        await pg.evaluate("([x,y])=>{for(let i=0;i<80;i++){const el=document.elementFromPoint(x,y);el.dispatchEvent(new MouseEvent('mousedown',{clientX:x,clientY:y,button:0,bubbles:true}));document.dispatchEvent(new MouseEvent('mouseup',{clientX:x,clientY:y,button:0,bubbles:true}));}}", [a[0], a[1]])
        await pg.wait_for_timeout(100); await pg.keyboard.press('Escape')
        n = await pg.evaluate("__h.Kit.undoN()"); by = await pg.evaluate("__h.Kit.stackBytes()"); full_ = await pg.evaluate("JSON.stringify(__h.Kit.all()).length")
        ok(n == min(80, 50) and by * 10 <= full_ * 80,   # 10-05 되돌리기 최대 50단계(UMAX)
           f'80단계 스택 {by:,}자 ≤ 예전 {full_ * 80:,}자의 1/10 (ANN {seed:,}자)')
        # 다른 창이 그 aid를 바꾸면 그 항목만 무효
        await pg.keyboard.press('h'); b2 = await pg.evaluate(PICK + '(4)'); await pg.mouse.click(b2[0], b2[1]); await pg.wait_for_timeout(150); await pg.keyboard.press('Escape')
        n1 = await pg.evaluate("__h.Kit.undoN()")
        pg2 = await ctx.new_page(); await pg2.goto(U + '#/'); await pg2.wait_for_timeout(600)
        await pg2.evaluate("aid=>{const A=JSON.parse(localStorage.getItem('jblhub.v1.ann.OMS1'));A[aid]=[];localStorage.setItem('jblhub.v1.ann.OMS1',JSON.stringify(A));}", a[3])
        await pg.wait_for_timeout(500); n2 = await pg.evaluate("__h.Kit.undoN()")
        ok(a[3] != b2[3] and n2 == 1 and n1 == 50, f'다른 창이 바꾼 aid 항목만 무효 ({n1} → {n2})')
        await pg.keyboard.press('Meta+z'); await pg.wait_for_timeout(200); ok(await pg.evaluate(f"!document.querySelector('[data-aid=\"{b2[3]}\"] [data-rk=h]')"), '남은 항목은 되돌릴 수 있음')
        await pg2.close()
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac', True)
        await run(b, {'width': 820, 'height': 1180}, True, 'ipp', False)
        await run(b, {'width': 1180, 'height': 820}, True, 'ipl', False)
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
