"""U02 회귀: 위치를 잃은 표시(원고가 바뀌어 글자를 못 찾는 형광펜·빈칸)는 어떤 편집에도 버려지지 않는다.
docs/index.html(J.HUB_URL)을 열고 스크린샷은 work/_tmp/ux_kt_orphan*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; KEY = 'jblhub.v1.ann.CONS'; GHOST = '이문장은원고수정으로사라진문장'
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(1200)
async def ann(pg): return json.loads(await pg.evaluate(f"localStorage.getItem('{KEY}')") or '{}')
async def tap_word(pg, aid, nth=-1):
    b = await pg.evaluate("""([aid,nth])=>{const B=document.querySelector('[data-aid="'+aid+'"]');const L=[...B.querySelectorAll('.tbody li,.tbody p')].filter(e=>e.offsetParent&&e.textContent.trim().length>20);const c=L[nth<0?L.length+nth:nth];c.scrollIntoView({block:'center'});
      const w=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);let t;while(t=w.nextNode()){if(t.nodeValue.trim().length>5)break;}const r=document.createRange();r.setStart(t,1);r.setEnd(t,2);const b=r.getBoundingClientRect();return {x:b.left+b.width/2,y:b.top+b.height/2};}""", [aid, nth])
    await pg.mouse.click(b['x'], b['y']); await pg.wait_for_timeout(150)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await open_(pg, '#/CONS/CRK/learn'); await pg.evaluate('localStorage.clear()')
        aid = await pg.evaluate("document.querySelector('#stage .tc').dataset.aid")
        await pg.evaluate("([k,aid,x])=>{const a={};a[aid]=[{t:'h',x,i:0,c:'y'}];localStorage.setItem(k,JSON.stringify(a));}", [KEY, aid, GHOST])
        await open_(pg, '#/CONS/CRK/learn')
        a = await ann(pg); g = [o for o in a.get(aid, []) if o['x'] == GHOST]
        ok(bool(g) and g[0].get('lost') == 1, '복원 때 못 찾은 표시 → lost:1로 남음')
        ok(await pg.evaluate("!document.querySelector('#k-lost').hidden && document.querySelector('#k-lost b').textContent==='1'"), "도구 막대 '⚠ 위치 잃음 1' 배지")
        await pg.screenshot(path=J.TMP + '/ux_kt_orphan_badge.png')
        # 같은 카드에 새 표시 → 지우기 → 색 바꾸기 → 🧹 → 되돌리기
        await pg.click('#k-h'); await tap_word(pg, aid)
        a = await ann(pg); ok(any(o['x'] == GHOST for o in a.get(aid, [])) and len(a[aid]) == 2, '새 표시를 칠해도 잃은 표시 유지 (orphan_kept_after_edit=true)')
        await tap_word(pg, aid)
        a = await ann(pg); ok([o['x'] for o in a.get(aid, [])] == [GHOST], '칠한 곳을 다시 눌러 지워도 잃은 표시 유지')
        await tap_word(pg, aid); await pg.click('#k-sw .sw[data-c="g"]'); await tap_word(pg, aid)
        a = await ann(pg); ok(any(o['x'] == GHOST for o in a.get(aid, [])) and any(o.get('c') == 'g' for o in a.get(aid, [])), '색 바꾸기 뒤에도 유지')
        await pg.keyboard.press('Escape'); await pg.click('#k-clear'); await pg.wait_for_timeout(200)
        a = await ann(pg); ok([o['x'] for o in a.get(aid, [])] == [GHOST], '🧹 화면 지우기 뒤에도 잃은 표시만 남음')
        await pg.click('#k-undo'); await pg.wait_for_timeout(200)
        a = await ann(pg); ok(any(o['x'] == GHOST for o in a.get(aid, [])) and len(a.get(aid, [])) == 2, '되돌리기 → 칠한 것 복귀 + 잃은 표시 유지')
        # 배지 → 모아보기의 위치 잃음 절
        await pg.click('#k-lost'); await pg.wait_for_timeout(500)
        ok(await pg.evaluate(f"location.hash.indexOf('_marks')>0 && !!document.querySelector('#mk-lost') && document.querySelector('#mk-lost').textContent.includes('{GHOST}')"), '배지 누르면 🖍 모아보기 ⚠ 위치 잃음 절')
        await pg.screenshot(path=J.TMP + '/ux_kt_orphan_marks.png')
        # 글자가 다시 생기면 lost 해제: 잃은 표시의 x를 실제 있는 어절로 바꿈
        await open_(pg, '#/CONS/CRK/learn')
        real = await pg.evaluate("([aid])=>{const B=document.querySelector('[data-aid=\"'+aid+'\"]');return B.querySelector('.tbody li').textContent.trim().split(/\\s+/).find(w=>w.length>=4)}", [aid])
        await pg.evaluate("([k,aid,x,r])=>{const a=JSON.parse(localStorage.getItem(k));a[aid].forEach(o=>{if(o.x===x)o.x=r;});localStorage.setItem(k,JSON.stringify(a));}", [KEY, aid, GHOST, real])
        await open_(pg, '#/CONS/CRK/learn')
        a = await ann(pg); ok(all(not o.get('lost') for o in a.get(aid, [])), f'글자를 다시 찾으면 lost 해제 ({real})')
        ok(await pg.evaluate("document.querySelector('#k-lost').hidden"), '잃은 표시 0개면 배지 숨김')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else 'FAIL'); _sys.exit(1 if fails else 0)
