"""C01 회귀: 저장 실패를 확실히 알리고 다시 쓰기 — localStorage를 더미로 한도까지 채운 뒤 형광펜 1개 → 빨간 띠 '⚠ 저장되지 않았어요'([지금 백업 파일 받기][공간 정리]) ·
LS.get은 큐의 값을 먼저(메모리 = 최신) · 백업 파일(dumpAll)에 저장 못 한 표시가 들어 있음 · 더미를 지우면 30초 안에 ann에 쓰이고 띠가 닫힘('저장됐어요') · 새로고침 뒤 표시 1개 ·
옛 자동 백업 사본(localStorage autobak.*)이 있으면 그것부터 지우고 곧바로 저장.
맥 1280×900(전 과정) + 아이패드 세로 820×1180 · 가로 1180×820(띠 모양·버튼). 스크린샷 work/_tmp/ux2i_c01_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, time
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
PICK = '''(n=>{const lis=[...document.querySelectorAll('#stage [data-aid] li')].filter(l=>l.offsetParent&&!l.closest('details:not([open])')&&!l.querySelector('[data-rk]')&&/[A-Za-z가-힣]{3}/.test(l.textContent));const li=lis[n];li.scrollIntoView({block:'center'});const w=document.createTreeWalker(li,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){const m=/[A-Za-z가-힣]{3,}/.exec(x.nodeValue);if(m&&!x.parentElement.closest('button,.chip,.noann,[data-rk]')){const r=document.createRange();r.setStart(x,m.index+1);r.setEnd(x,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2,m[0]];}}})'''
FILL = """()=>{for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(/^jblhub\\.v1\\.autobak/.test(k))localStorage.removeItem(k);}
 let n=0;const big='x'.repeat(200000);for(let i=0;i<200;i++){try{localStorage.setItem('zz.dummy'+i,big);n++;}catch(e){break;}}
 const sm='y'.repeat(2000);for(let i=0;i<5000;i++){try{localStorage.setItem('zz.dsm'+i,sm);n++;}catch(e){break;}}
 const t='z'.repeat(50);for(let i=0;i<5000;i++){try{localStorage.setItem('zz.dt'+i,t);n++;}catch(e){break;}}return n;}"""
UNFILL = "()=>{for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(k.indexOf('zz.')===0)localStorage.removeItem(k);}}"
ANN = "(()=>{const v=localStorage.getItem('jblhub.v1.ann.OMS1');if(!v)return 0;const a=JSON.parse(v);let n=0;for(const k in a)n+=a[k].length;return n;})()"
async def run(b, vp, touch, tag, full):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept()); print('==', tag)
    await pg.goto(U + '#/OMS1/DD1/learn'); await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3")
    await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3"); await pg.wait_for_timeout(500)
    n = await pg.evaluate(FILL); print('       더미', n, '개로 채움')
    await pg.keyboard.press('h'); a = await pg.evaluate(PICK + '(0)'); await pg.mouse.click(a[0], a[1]); await pg.wait_for_timeout(200)
    ok(await pg.locator('#stage [data-rk=h]').count() == 1, f'형광펜 칠함 ("{a[2]}")')
    await pg.wait_for_selector('#lserr', timeout=3000)
    txt = await pg.inner_text('#lserr'); ok('저장되지 않았어요' in txt and '지금 백업 파일 받기' in txt and '공간 정리' in txt, f'오류 띠 {txt!r}')
    await pg.keyboard.press('Escape'); await pg.screenshot(path=J.TMP + f'/ux2i_c01_band_{tag}.png')
    ok(await pg.evaluate(ANN) == 0, 'localStorage ann에는 아직 없음(한도)')
    ok(await pg.evaluate("__h.Kit.all&&Object.values(__h.Kit.all()).flat().length") == 1 and await pg.evaluate("(()=>{const d=__h.dumpAll();const a=JSON.parse(d['jblhub.v1.ann.OMS1']||'{}');return Object.values(a).flat().length})()") == 1, '메모리·백업 파일(dumpAll)에는 표시 1개')
    # 띠는 하나만(연달아 실패해도)
    await pg.keyboard.press('h'); a2 = await pg.evaluate(PICK + '(2)'); await pg.mouse.click(a2[0], a2[1]); await pg.wait_for_timeout(150); await pg.click('#k-undo'); await pg.wait_for_timeout(150)
    ok(await pg.locator('#toasterr .terr').count() == 1, f"띠는 하나 ({await pg.locator('#toasterr .terr').count()})")
    await pg.keyboard.press('Escape')
    if not full:
        await pg.evaluate(UNFILL); await pg.evaluate("__h.lsFlush()")
        ok(await pg.locator('#lserr').count() == 0 and await pg.evaluate(ANN) == 1, '더미를 지우고 다시 쓰면 띠 닫힘·ann 1')
        ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close(); return
    await pg.evaluate(UNFILL); t0 = time.time()
    await pg.wait_for_function("document.querySelector('#lserr')===null&&(()=>{const v=localStorage.getItem('jblhub.v1.ann.OMS1');return !!v&&Object.values(JSON.parse(v)).flat().length===1})()", timeout=36000, polling=500)
    ok(True, f'더미를 지우면 {time.time() - t0:.0f}초 뒤 ann에 기록 · 띠 닫힘')
    ok('저장됐어요' in (await pg.evaluate("sessionStorage.getItem('jblhub.v1.toasts')") or ''), "'저장됐어요' 알림")
    await pg.reload(); await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3"); await pg.wait_for_timeout(600)
    ok(await pg.locator('#stage [data-rk=h]').count() == 1, f"새로고침 뒤 표시 {await pg.locator('#stage [data-rk=h]').count()}개")
    # 옛 자동 백업 사본이 있으면 그것부터 지우고 곧바로 저장
    await pg.evaluate(FILL); await pg.evaluate("(()=>{for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(k.indexOf('zz.dummy')===0){localStorage.removeItem(k);break;}}localStorage.setItem('jblhub.v1.autobak.3',JSON.stringify({at:1000,data:{x:'q'.repeat(190000)}}));localStorage.setItem('jblhub.v1.autobak.p1',JSON.stringify({at:900,why:'원고 갱신 전',data:{}}));})()")
    await pg.evaluate("(()=>{let i=0;try{for(;i<400;i++)localStorage.setItem('zz.fill'+i,'w'.repeat(1000));}catch(e){}try{for(i=0;i<3000;i++)localStorage.setItem('zz.f2'+i,'w'.repeat(5));}catch(e){}})()")
    await pg.keyboard.press('h'); a = await pg.evaluate(PICK + '(3)'); await pg.mouse.click(a[0], a[1]); await pg.wait_for_timeout(200)
    ok(await pg.locator('#lserr').count() == 0 and await pg.evaluate(ANN) == 2, '옛 자동 백업 사본을 지우고 곧바로 저장(띠 없음)')
    ok(await pg.evaluate("localStorage.getItem('jblhub.v1.autobak.3')") is None, '옛 주기 사본이 지워짐')
    await pg.evaluate(UNFILL)
    order = await pg.evaluate("(()=>{localStorage.setItem('jblhub.v1.autobak.3',JSON.stringify({at:3000,data:{}}));localStorage.setItem('jblhub.v1.autobak.1',JSON.stringify({at:2000,data:{}}));localStorage.setItem('jblhub.v1.autobak.p1',JSON.stringify({at:900,why:'원고 갱신 전',data:{}}));const o=__h.lsBakSlots().map(k=>k.slice(10));['autobak.3','autobak.1','autobak.p1'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k));return o;})()")
    ok(order == ['autobak.1', 'autobak.3', 'autobak.p1'], f'지우는 순서 = 오래된 주기 칸부터, 보호 칸은 마지막 {order}')
    # 도움말 — 마지막 자동 백업 시각
    await pg.evaluate("__h.autoBak(true,'시험')"); await pg.keyboard.press('Escape'); await pg.keyboard.press('?'); await pg.wait_for_timeout(150)
    ok((await pg.inner_text('#hbakat')).startswith('오늘'), f"도움말 '마지막 성공' {await pg.inner_text('#hbakat')!r}")
    await pg.keyboard.press('Escape')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()
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
