"""A09 회귀: 🖍 내 표시 모아보기 v2 — 표시마다 그 표시가 든 줄(li·td·p·.ln, ≤160자)·칠한 부분만 <mark> · 색 필터 칩(LS mkcol) ·
빈칸 줄은 가린 채(누르면 열림) · 색 라벨(LS hlabel, 기본 노랑=기출·분홍=헷갈림·초록=암기 완료 — 견본 우클릭/길게 누르기) · 허브 홈 '🖍 전 과목 내 표시'.
맥 1280×900 + 아이패드 세로 820×1180 + 가로 1180×820. 스크린샷 work/_tmp/ux2i_a09_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1200):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
WORDS = """(n)=>{const L=[...document.querySelectorAll('#stage .tc.open .tbody li,#stage .tc.open .tbody div.li')].filter(e=>e.offsetParent&&!e.closest('.noann,.c-exam')&&e.textContent.trim().length>=30&&!e.querySelector('li,div.li'));
  const out=[];for(const e of L){const tw=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let t;while(t=tw.nextNode()){if(t.parentElement.closest('.noann,button,.chip,.k'))continue;const m=/[A-Za-z가-힣]{4,}/.exec(t.nodeValue);if(!m)continue;out.push(e);break;}if(out.length>=n)break;}
  out.forEach((e,i)=>e.setAttribute('data-a09',i));return out.length;}"""
PT = """(i)=>{const e=document.querySelector('[data-a09="'+i+'"]');e.scrollIntoView({block:'center'});const tw=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let t;while(t=tw.nextNode()){if(t.parentElement.closest('.noann,button,.chip,.k'))continue;const m=/[A-Za-z가-힣]{4,}/.exec(t.nodeValue);if(!m)continue;
  const r=document.createRange();r.setStart(t,m.index+1);r.setEnd(t,m.index+2);const b=r.getBoundingClientRect();return [b.left+b.width/2,b.top+b.height/2];}return null;}"""
VIS = "[...document.querySelectorAll('#stage .mk-line')].filter(e=>e.offsetParent).length"
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await open_(pg, '#/OMS1/DD1/learn'); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await open_(pg, '#/OMS1/DD1/learn', 1500)
    ok(await pg.evaluate(WORDS, 4) == 4, '픽스처: 본문 줄 4개')
    clk = (lambda x, y: pg.touchscreen.tap(x, y)) if touch else (lambda x, y: pg.mouse.click(x, y))
    await pg.keyboard.press('h')
    for i, c in enumerate(['y', 'y', 'p']):
        await pg.evaluate(f"__h.Kit.setColor('{c}')"); xy = await pg.evaluate(PT, i); await clk(xy[0], xy[1]); await pg.wait_for_timeout(150)
    await pg.keyboard.press('Escape'); await pg.keyboard.press('b'); xy = await pg.evaluate(PT, 3); await clk(xy[0], xy[1]); await pg.wait_for_timeout(150); await pg.keyboard.press('Escape')
    ann = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')") or '{}'); nm = sum(len(v) for v in ann.values())
    ok(nm == 4, f'노랑 2·분홍 1·빈칸 1 칠함 ({nm})')
    await open_(pg, '#/OMS1/_marks/_marks', 1300)
    L = await pg.evaluate("[...document.querySelectorAll('#stage .mk-line')].map(e=>({c:e.dataset.c,m:e.querySelectorAll('mark').length,len:e.textContent.replace('↗','').length}))")
    hl = [x for x in L if x['c'] != 'b']
    ok(len(hl) == 3 and sum(x['m'] for x in hl) == 3 and all(x['len'] <= 162 for x in L), f'형광펜 줄 3개·mark 3개·160자 이내 {[(x["c"], x["len"]) for x in L]}')
    ok(await pg.evaluate("[...document.querySelectorAll('#stage .mk-line')].every(e=>{const m=e.querySelector('mark');return m&&e.textContent.replace('↗','').trim().length>m.textContent.trim().length+5})"), '줄마다 표시 앞뒤 문장 맥락이 함께 보임')
    ok(await pg.evaluate("[...document.querySelectorAll('#stage .mk-line[data-c=y] mark')].every(m=>getComputedStyle(m).backgroundColor==='rgb(255, 229, 138)')"), '노랑 표시만 노랑 <mark>')
    await pg.screenshot(path=J.TMP + f'/ux2i_a09_marks_{tag}.png')
    await pg.evaluate("document.querySelector('#stage .mkf[data-mkcol=p]').click()"); await pg.wait_for_timeout(150)
    v = await pg.evaluate(VIS); ok(v == 1 and await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.mkcol'))") == 'p', f'분홍 필터 → 1줄 ({v})')
    await pg.screenshot(path=J.TMP + f'/ux2i_a09_pink_{tag}.png')
    await pg.reload(); await pg.wait_for_timeout(1300)
    v = await pg.evaluate(VIS); ok(v == 1, f'새로고침 뒤에도 분홍 필터 유지 ({v})')
    await pg.evaluate("document.querySelector('#stage .mkf[data-mkcol=b]').click()"); await pg.wait_for_timeout(150)
    bl = pg.locator('#stage .mk-line[data-c=b] mark.mk-bl').first
    c0 = await bl.evaluate("e=>getComputedStyle(e).color"); await bl.click(); c1 = await bl.evaluate("e=>getComputedStyle(e).color")
    ok(await pg.evaluate(VIS) == 1 and c0 == 'rgba(0, 0, 0, 0)' and c1 != c0, f'빈칸 필터 1줄 · 가려져 있고 누르면 열림 ({c0} → {c1})')
    await pg.evaluate("document.querySelector('#stage .mkf[data-mkcol=\"\"]').click()"); await pg.wait_for_timeout(100)
    ok(await pg.evaluate(VIS) == 4, '전체 → 4줄')
    ok('기출' in await pg.inner_text('#stage .mkf[data-mkcol=y]') and '헷갈림' in await pg.inner_text('#stage .mkf[data-mkcol=p]'), '모아보기 칩에 기본 라벨(노랑 기출·분홍 헷갈림)')
    # ↗ → 그 자리로
    await pg.evaluate("document.querySelector('#stage .mk-line[data-c=p] button.mkgo').click()"); await pg.wait_for_timeout(700)
    ok((await pg.evaluate('location.hash')).startswith('#/OMS1/DD1/') and await pg.evaluate("!!document.querySelector('#stage .mkflash')"), '↗ → 정리본의 그 표시로 가서 깜빡임')
    # 색 라벨: 견본 우클릭(맥)/0.5초 길게 누르기(아이패드) → prompt → 저장 · 길게 누른 뒤의 click은 색을 고르지 않음
    await open_(pg, '#/OMS1/DD1/learn', 1300)
    pg.once('dialog', lambda d: asyncio.ensure_future(d.accept('시험 직전')))
    c_before = await pg.evaluate("__h.Kit.color()")
    if touch:
        await pg.evaluate("document.querySelector('#k-swc').click()"); await pg.wait_for_timeout(100)
        await pg.evaluate("document.querySelector('#k-swl .sw[data-c=u]').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerType:'touch',button:0}))")
        await pg.wait_for_timeout(700)
        await pg.evaluate("document.querySelector('#k-swl .sw[data-c=u]').dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerType:'touch'}))")
        await pg.evaluate("document.querySelector('#k-swl .sw[data-c=u]').click()")
        ok(await pg.evaluate("__h.Kit.color()") == c_before and not await pg.evaluate("document.body.classList.contains('mode-h')"), '길게 누른 뒤의 누르기는 색·모드를 바꾸지 않음')
    else:
        await pg.click('#k-swl .sw[data-c=u]', button='right')
    await pg.wait_for_timeout(300)
    lab = await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.hlabel')||'null')")
    ok(bool(lab) and lab.get('u') == '시험 직전' and lab.get('y') == '기출', f'견본 {"길게 누르기" if touch else "우클릭"} → 라벨 저장 {lab}')
    await pg.reload(); await pg.wait_for_timeout(1300)
    ok('시험 직전' in await pg.evaluate("document.querySelector('#k-swl .sw[data-c=u]').title"), '새로고침 뒤 견본 title에 라벨')
    await open_(pg, '#/OMS1/_marks/_marks', 1200)
    ok('시험 직전' in await pg.inner_text('#stage .mkf[data-mkcol=u]'), '모아보기 칩에 바꾼 라벨')
    # 허브 홈 '🖍 전 과목 내 표시'
    await open_(pg, '#/', 1200)
    t = await pg.inner_text('#home .mkall'); ok('전 과목 내 표시' in t and '🖍 3 · ▣ 1' in t, f'허브 홈 전 과목 내 표시 ({t[:120]!r})')
    await pg.evaluate("document.querySelector('#home .mkall').scrollIntoView({block:'center'})"); await pg.screenshot(path=J.TMP + f'/ux2i_a09_home_{tag}.png')
    await pg.evaluate("document.querySelector('#home [data-mks=OMS1]').click()"); await pg.wait_for_timeout(900)
    ok((await pg.evaluate('location.hash')).startswith('#/OMS1/_marks') and await pg.evaluate(VIS) == 4, '→ 그 과목 모아보기')
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), '가로 넘침 0')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 820, 'height': 1180}, True, 'ipp')
        await run(b, {'width': 1180, 'height': 820}, True, 'ipl')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
