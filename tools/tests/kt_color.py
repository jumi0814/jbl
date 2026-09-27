"""U04 회귀: 파랑 형광펜이 빈칸(.rk-b)으로 둔갑하지 않고, 주황이 회색으로 칠해지지 않는다. 옛 파랑 기록 {t:'h',c:'b'} 이관.
docs/index.html(J.HUB_URL)을 열고 스크린샷은 work/_tmp/ux_kt_color.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; KEY = 'jblhub.v1.ann.CONS'
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(1200)
LINES = "#stage .tc .tbody li, #stage .tc .tbody div.li:not(.nolead)"   # 본문 한 줄 = 목록 li 또는 항목 div.li(원고 구조와 무관)
async def tap(pg, sel_nth):
    b = await pg.evaluate("""(n)=>{const LINES='""" + LINES + """';const L=[...document.querySelectorAll(LINES)].filter(e=>e.offsetParent&&!e.closest('.noann,.c-exam')&&e.textContent.trim().length>20);const c=L[n];c.scrollIntoView({block:'center'});
      const w=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);let t,m;while(t=w.nextNode()){if(t.parentElement.closest('[data-rk],.noann,button'))continue;if(m=/[A-Za-z가-힣]{3,}/.exec(t.nodeValue))break;}const r=document.createRange();r.setStart(t,m.index+1);r.setEnd(t,m.index+2);const b=r.getBoundingClientRect();return {x:b.left+b.width/2,y:b.top+b.height/2};}""", sel_nth)
    await pg.mouse.click(b['x'], b['y']); await pg.wait_for_timeout(150)
STYLE = "(el)=>{const s=getComputedStyle(el);return [s.color,s.backgroundColor]}"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await open_(pg, '#/CONS/CRK/learn'); await pg.evaluate('localStorage.clear()'); await open_(pg, '#/CONS/CRK/learn')
        await pg.click('#k-sw .sw[data-c="u"]'); await tap(pg, 0)
        el = pg.locator('#stage .rk-h.rk-u').first; c, bg = await el.evaluate(STYLE)
        ok(c not in ('rgba(0, 0, 0, 0)', 'transparent') and bg == 'rgb(201, 221, 247)', f'파랑 형광펜: 글자색 {c} · 배경 {bg} (#C9DDF7)')
        ok(await pg.locator('#stage .rk-b').count() == 0, '파랑으로 칠해도 빈칸(.rk-b)이 생기지 않음')
        await pg.click('#k-sw .sw[data-c="o"]'); await tap(pg, 1)
        c2, bg2 = await pg.locator('#stage .rk-h.rk-o').first.evaluate(STYLE)
        ok(bg2 == 'rgb(255, 201, 140)', f'주황 형광펜 배경 {bg2} = rgb(255,201,140)')
        await pg.screenshot(path=J.TMP + '/ux_kt_color.png')
        a = json.loads(await pg.evaluate(f"localStorage.getItem('{KEY}')"))
        ok(any(o.get('c') == 'u' for L in a.values() for o in L), "새 기록의 파랑 키 = 'u'")
        # 옛 기록 {t:'h',c:'b'} + 빈칸 {t:'b'} 넣고 새로고침
        aid = await pg.evaluate("document.querySelector('#stage .tc').dataset.aid")
        words = await pg.evaluate("(()=>{const B=document.querySelector('#stage .tc'),T=__h.Kit.textOf(B);const W=[...B.querySelectorAll('.tbody div.li,.tbody li')].flatMap(e=>e.textContent.split(/[^A-Za-z]+/));return [...new Set(W)].filter(w=>w.length>=4&&T.split(w).length===2).slice(0,2)})()")   # 카드 안에 한 번만 나오는 영어 낱말(문맥 없는 옛 기록은 후보가 하나일 때만 복원)
        await pg.evaluate("([k,aid,w])=>{const a={};a[aid]=[{t:'h',x:w[0],i:0,c:'b'},{t:'b',x:w[1],i:0}];localStorage.setItem(k,JSON.stringify(a));localStorage.removeItem('jblhub.v1.autobak.i');localStorage.removeItem('jblhub.v1.autobak.pi');for(const i of ['p0','p1','p2',0,1,2,3,4])localStorage.removeItem('jblhub.v1.autobak.'+i);}", [KEY, aid, words])
        await open_(pg, '#/CONS/CRK/learn')
        a = json.loads(await pg.evaluate(f"localStorage.getItem('{KEY}')"))
        ok([o.get('c') for o in a[aid] if o['t'] == 'h'] == ['u'], f"옛 파랑 {{c:'b'}} → c:'u'로 이관 {a[aid]}")
        bak = await pg.evaluate("(()=>{for(const i of ['p0','p1','p2',0,1,2,3,4]){const v=localStorage.getItem('jblhub.v1.autobak.'+i);if(v){const j=JSON.parse(v);if(j.why)return j.why;}}return ''})()")
        ok(bak == '파랑 색 키 이관', f'이관 전 자동 백업 남김 ({bak})')
        c3, bg3 = await pg.locator('#stage .rk-h.rk-u').first.evaluate(STYLE)
        ok(bg3 == 'rgb(201, 221, 247)' and c3 != 'rgba(0, 0, 0, 0)', f'옛 파랑 기록이 파랑으로 보임 ({c3}, {bg3})')
        cb = await pg.locator('#stage .rk-b').first.evaluate(STYLE)
        ok(await pg.locator('#stage .rk-b').count() >= 1 and cb[0] == 'rgba(0, 0, 0, 0)', f'빈칸(t:b)은 그대로 빈칸 ({cb})')
        # 모아보기 견본 색
        await open_(pg, '#/CONS/_marks/')
        cols = await pg.evaluate("[...document.querySelectorAll('#stage .mk:not(.b)')].map(e=>getComputedStyle(e).backgroundColor)")
        ok('rgb(201, 221, 247)' in cols, f'모아보기 파랑 견본 {cols}')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else 'FAIL'); _sys.exit(1 if fails else 0)
