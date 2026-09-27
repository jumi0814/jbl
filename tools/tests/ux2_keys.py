"""2차 묶음 1 회귀: 새 단축키 배치(A02) — H·Shift+H·B(A 별칭)·E·N·Shift+N·T·D·F·C·G·/ · 한 장씩 S ★(B는 빈칸)·keyNotice · ? 도움말 키 표.
맥 1280×900 · 아이패드 세로 820×1180(터치)·가로 1180×820(터치). 스크린샷 work/_tmp/ux2_keys_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1200):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
BODY = "(c)=>document.body.classList.contains(c)"
async def a02(pg, tag):
    await open_(pg, '#/OMS1/DD1/learn')
    await pg.keyboard.press('b'); m1 = await pg.evaluate(BODY, 'mode-b'); await pg.keyboard.press('b'); m2 = await pg.evaluate(BODY, 'mode-b')
    ok(m1 and not m2, f'B → 빈칸 모드 켜기·끄기 ({m1},{m2})')
    await pg.keyboard.press('h'); h1 = await pg.evaluate(BODY, 'mode-h'); await pg.keyboard.press('h'); h2 = await pg.evaluate(BODY, 'mode-h')
    ok(h1 and not h2, f'H 두 번 → 켜졌다 꺼짐 ({h1},{h2})')
    await pg.keyboard.press('a'); a1 = await pg.evaluate(BODY, 'mode-b'); await pg.keyboard.press('Escape')
    ok(a1 and not await pg.evaluate(BODY, 'mode-b'), '옛 A 키도 빈칸 모드 · Esc 끄기')
    c0 = await pg.evaluate("[__h.Kit.color(),document.querySelector('#k-swc .swcur').style.background,document.querySelector('#k-swl .sw.sel').dataset.c]")
    await pg.keyboard.press('Shift+H'); await pg.wait_for_timeout(100)
    c1 = await pg.evaluate("[__h.Kit.color(),document.querySelector('#k-swc .swcur').style.background,document.querySelector('#k-swl .sw.sel').dataset.c]")
    toast = await pg.inner_text('#toast')
    ok(c0[0] == 'y' and c1[0] == 'g' and c1[1] != c0[1] and c1[2] == 'g' and '초록' in toast, f'Shift+H → 색 칩 {c0} → {c1} · 토스트 {toast!r}')
    await pg.keyboard.press('Shift+H'); await pg.keyboard.press('Shift+H'); await pg.keyboard.press('Shift+H'); await pg.keyboard.press('Shift+H')
    ok(await pg.evaluate("__h.Kit.color()") == 'y', 'Shift+H 다섯 번 → 한 바퀴(y→g→p→u→o→y)')
    # D: 지금 카드 ✓ / F: 접기 / C: 압축
    await pg.evaluate("(()=>{const c=document.querySelector('#t-DD1-2');window.scrollTo(0,c.getBoundingClientRect().top+scrollY-120)})()"); await pg.wait_for_timeout(1200)
    cur = await pg.evaluate("(()=>{const n=document.querySelector('#lmn').textContent;return n})()")
    await pg.keyboard.press('d'); await pg.wait_for_timeout(300)
    dn = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.done.OMS1')") or '{}')
    aid = await pg.evaluate(f"document.querySelector('#t-DD1-{int(cur)-1}').dataset.aid") if cur.isdigit() else None
    ok(cur.isdigit() and dn.get(aid) == 1, f'D → 지금 카드({cur}) ✓ 이해함 {list(dn)[:2]}')
    await pg.keyboard.press('d'); await pg.wait_for_timeout(300)
    c = await pg.evaluate("(()=>{const n=+document.querySelector('#lmn').textContent;const c=document.querySelector('#t-DD1-'+(n-1));return c?[n,c.classList.contains('open')]:null})()")
    await pg.keyboard.press('f'); await pg.wait_for_timeout(150)
    c2 = await pg.evaluate(f"document.querySelector('#t-DD1-{c[0]-1}').classList.contains('open')") if c else None
    ok(c and c[1] != c2, f'F → 지금 카드 접기/펼치기 {c} → {c2}')
    await pg.keyboard.press('c'); cd = await pg.evaluate("document.querySelector('#stage').classList.contains('cond')"); await pg.keyboard.press('c')
    ok(cd and not await pg.evaluate("document.querySelector('#stage').classList.contains('cond')"), 'C → 압축 보기 켜고 끄기')
    await pg.keyboard.press('/'); ok(await pg.evaluate("document.activeElement.id") == 'gsearch', '/ → 검색창')
    await pg.keyboard.press('Escape'); await pg.evaluate("document.activeElement.blur()")
    await pg.keyboard.press('t'); t1 = await pg.evaluate(BODY, 'kit-off'); await pg.keyboard.press('t')
    ok(t1 and not await pg.evaluate(BODY, 'kit-off'), 'T → 도구 막대 숨기기·다시')
    await pg.keyboard.press('g'); await pg.wait_for_timeout(400); ok('/_home/' in await pg.evaluate('location.hash'), 'G → 과목 홈')
    # E·N·Shift+N — 저장형 빈칸 3개(한 카드)
    await open_(pg, '#/OMS1/DD1/learn')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.fold.OMS1.DD1');localStorage.removeItem('jblhub.v1.done.OMS1')"); await open_(pg, '#/OMS1/DD1/learn')   # D(✓하면 접기)로 접힌 카드는 N 대상이 아님
    await pg.evaluate("""()=>{const B=document.querySelector('#t-DD1-3');const T=__h.Kit.textOf(B);const ws=[...new Set((T.match(/[A-Za-z가-힣]{3,}/g)||[]))].filter(w=>T.split(w).length===2).slice(0,3);
      const k='jblhub.v1.ann.OMS1';const a=JSON.parse(localStorage.getItem(k)||'{}');a[B.dataset.aid]=ws.map(x=>({t:'b',x,i:0}));localStorage.setItem(k,JSON.stringify(a));}""")
    await open_(pg, '#/OMS1/DD1/learn'); await pg.evaluate("document.querySelector('#t-DD1-3').scrollIntoView({block:'start'})"); await pg.wait_for_timeout(1000)
    NB = "[...new Set([...document.querySelectorAll('#t-DD1-3 [data-rk=b].show')].map(e=>e.dataset.g))].length"
    await pg.keyboard.press('n'); n1 = await pg.evaluate(NB); await pg.keyboard.press('n'); n2 = await pg.evaluate(NB)
    ok(n1 == 1 and n2 == 2, f'N → 가린 칸 하나씩 열기 ({n1},{n2})')
    await pg.keyboard.press('Shift+N'); ok(await pg.evaluate(NB) == 0, 'Shift+N → 이 카드 다시 가리기')
    await pg.keyboard.press('e'); e1 = await pg.evaluate("getComputedStyle(document.querySelector('#t-DD1-3 [data-rk=b]')).color")
    await pg.keyboard.press('e'); e2 = await pg.evaluate("getComputedStyle(document.querySelector('#t-DD1-3 [data-rk=b]')).color")
    ok(e1 != 'rgba(0, 0, 0, 0)' and e2 == 'rgba(0, 0, 0, 0)', f'E → 전부 열기·가리기 ({e1},{e2})')
    # 한 장씩: S = ★, B = 빈칸 모드(★ 그대로)
    await open_(pg, '#/OMS1/_jb/_jb'); await pg.evaluate("localStorage.removeItem('jblhub.v1.keyNotice')"); await pg.click('#fone'); await pg.wait_for_timeout(300)
    t = await pg.inner_text('#toast'); ok('★는 이제 S' in t, f'처음 한 번 안내 토스트 {t!r}')
    cid = await pg.evaluate("document.querySelector('#cards .qc.cur').dataset.id")
    BM = f"!!(JSON.parse(localStorage.getItem('jblhub.v1.mk.OMS1')||'{{}}').bm||{{}})['{cid}']"
    b0 = await pg.evaluate(BM); await pg.keyboard.press('s'); b1 = await pg.evaluate(BM)
    await pg.keyboard.press('b'); b2 = await pg.evaluate(BM); mb = await pg.evaluate(BODY, 'mode-b'); await pg.keyboard.press('Escape')
    ok(b1 != b0 and b2 == b1 and mb, f'한 장씩 S → ★ 토글({b0}→{b1}) · B는 ★ 그대로({b2})·빈칸 모드({mb})')
    okeys = await pg.evaluate("document.querySelector('.okeys').textContent+' | '+document.querySelector('#obm').title")
    ok('S ★' in okeys and '(S)' in okeys, f'풀이 막대 안내 {okeys!r}')
    await pg.click('#fone')
    await pg.keyboard.press('?'); ht = await pg.inner_text('#help')
    ok('빈칸 B' in ht and 'S ★' in ht and '한/영 상관없이' in ht and 'Shift+H' in ht, '? 도움말 키 표(B 빈칸·S ★·한/영·Shift+H)')
    await pg.screenshot(path=J.TMP + f'/ux2_keys_help_{tag}.png'); await pg.keyboard.press('Escape')
    titles = await pg.evaluate("['#k-h','#k-b','#k-eye'].map(x=>document.querySelector(x).title).join(' | ')")
    ok('(H)' in titles and '(B)' in titles and '(E)' in titles, f'도구 막대 제목 {titles[:80]}')
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    await a02(pg, tag)
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 820, 'height': 1180}, True, 'ipad')
        await run(b, {'width': 1180, 'height': 820}, True, 'ipadl')
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
