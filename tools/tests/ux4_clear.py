"""ux4 B1-3·B02 🧹 표시 지우기 2단계 — 1280×900 · 1180×820(터치) · 820×1180(터치)
CONS WHT 학습: 카드 4에 형광 2·내 빈칸 1, 카드 5에 형광 1 → 카드 4를 화면 가운데 → 🧹 → [이 탭](개수 4) → [이 카드](창은 열린 채, 대상 카드 4·개수 3·테두리)
→ [형광펜만] → 확인 → 카드 4 형광 0·카드 5 형광 1 · 다시 🧹 [이 탭] → [모두] → 탭 0 → ↶ 한 번에 복원(2) → 새로고침 뒤 유지 ·
0개 줄을 누르면 '이 탭에는 n개' 안내 · 정리표(표 화면)는 '이 행'이 대상 · 콘솔 오류 0 · 스크린샷 work/_tmp/ux4i_clear_<폭>.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
# 카드(블록 선택자) 안 n번째 글줄의 한 낱말 가운데 좌표 — 화면 가운데로 옮긴 뒤
PICK = """([sel,n])=>{const c=document.querySelector(sel);const L=[...c.querySelectorAll('li,p,td')].filter(l=>l.offsetParent&&!l.closest('details:not([open]),.noann,button')&&!l.querySelector('[data-rk],li,p')&&/[A-Za-z가-힣]{4}/.test(l.textContent));const li=L[n];li.scrollIntoView({block:'center'});
 const w=document.createTreeWalker(li,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){const m=/[A-Za-z가-힣]{4,}/.exec(x.nodeValue);if(m&&!x.parentElement.closest('button,.chip,.noann,[data-rk]')){const r=document.createRange();r.setStart(x,m.index+1);r.setEnd(x,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2,m[0]];}}return null;}"""
CNT = "(sel=>{const c=document.querySelector(sel);const g=t=>{const s=new Set();c.querySelectorAll('[data-rk='+t+']').forEach(e=>s.add(e.getAttribute('data-g')||e));return s.size;};return {h:g('h'),b:g('b')};})"
async def tapword(pg, sel, n):
    a = await pg.evaluate(PICK, [sel, n]); await pg.wait_for_timeout(120)
    a = await pg.evaluate(PICK, [sel, n]); await pg.mouse.click(a[0], a[1]); await pg.wait_for_timeout(150); return a[2]
async def run(b, tag, vp, touch):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
    dlg = []; pg.on('dialog', lambda d: (dlg.append(d.message), asyncio.ensure_future(d.accept())))
    await pg.goto(U + '#/'); await pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.tauto','false')")
    await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/learn'); await pg.wait_for_selector('#stage .tc', timeout=30000); await pg.wait_for_timeout(900)
    C4, C5 = '#t-WHT-3', '#t-WHT-4'
    await pg.keyboard.press('h'); await tapword(pg, C4, 0); await tapword(pg, C4, 1)
    await pg.keyboard.press('b'); await tapword(pg, C4, 2)
    await pg.keyboard.press('h'); await tapword(pg, C5, 0); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)
    c4 = await pg.evaluate(CNT + f"('{C4}')"); c5 = await pg.evaluate(CNT + f"('{C5}')")
    ok(c4 == {'h': 2, 'b': 1} and c5 == {'h': 1, 'b': 0}, f'{tag} 준비: 카드4 {c4} · 카드5 {c5}')
    # 카드 4를 화면 가운데로(카드 5의 표시는 화면 밖)
    await pg.evaluate(f"(()=>{{const c=document.querySelector('{C4}'),r=c.getBoundingClientRect();scrollTo(0,scrollY+r.top+Math.min(r.height,innerHeight)/2-innerHeight/2);}})()"); await pg.wait_for_timeout(400)
    await pg.evaluate("__h.Kit&&0"); await pg.evaluate("window.__h&&0")
    await pg.click('#k-clear'); await pg.wait_for_selector('#clearpop.on')
    await pg.click('#clearpop [data-csc=tab]'); await pg.wait_for_timeout(150)
    r = await pg.evaluate("[document.querySelector('#clearpop').classList.contains('on'),document.querySelector('#clearpop [data-ck=all] b').textContent,document.querySelector('#clearpop [data-csc=tab]').classList.contains('on')]")
    ok(r[0] and r[1] == '4' and r[2], f'{tag} [이 탭] → 창 열린 채 · 모두 4 {r}')
    await pg.click('#clearpop [data-csc=card]'); await pg.wait_for_timeout(150)
    r = await pg.evaluate(f"[document.querySelector('#clearpop').classList.contains('on'),document.querySelector('#clearpop [data-ck=all] b').textContent,document.querySelector('#clearpop [data-ck=hl] b').textContent,document.querySelector('{C4}').classList.contains('clrtgt'),document.querySelector('#clearpop .cpt').textContent,document.querySelector('#clearpop [data-csc=card]').getAttribute('aria-pressed')]")
    ok(r[0] and r[1] == '3' and r[2] == '2' and r[3] and r[5] == 'true', f'{tag} [이 카드] → 창 열린 채 · 대상 카드 4(테두리) · 모두 3 · 형광 2 {r}')
    await pg.screenshot(path=J.TMP + f'/ux4i_clear_{tag}.png')
    n0 = len(dlg); await pg.click('#clearpop [data-ck=hl]'); await pg.wait_for_timeout(300)
    c4 = await pg.evaluate(CNT + f"('{C4}')"); c5 = await pg.evaluate(CNT + f"('{C5}')")
    ok(len(dlg) == n0 + 1 and c4 == {'h': 0, 'b': 1} and c5 == {'h': 1, 'b': 0}, f'{tag} [형광펜만] → 확인 → 카드4 {c4} · 카드5 {c5} (확인창 {dlg[-1][:20] if dlg else ""})')
    ok(not await pg.evaluate("document.querySelector('#clearpop').classList.contains('on')") and await pg.evaluate("document.querySelectorAll('#stage .clrtgt').length") == 0, f'{tag} 지운 뒤 창 닫힘·테두리 없음')
    # 0개 줄 → 안내(창 유지)
    await pg.click('#k-clear'); await pg.wait_for_selector('#clearpop.on'); await pg.click('#clearpop [data-csc=card]'); await pg.wait_for_timeout(100)
    z = await pg.evaluate("document.querySelector('#clearpop [data-ck=hl]').classList.contains('z')")
    await pg.click('#clearpop [data-ck=hl]'); await pg.wait_for_timeout(200)
    t = await pg.evaluate("(document.querySelector('#toast')||{}).textContent||''")
    ok(z and '없어요' in t and '이 탭에는 1개' in t and await pg.evaluate("document.querySelector('#clearpop').classList.contains('on')"), f'{tag} 0개 줄 → 안내 "{t[:40]}" · 창 유지')
    await pg.click('#clearpop [data-csc=tab]'); await pg.wait_for_timeout(100); await pg.click('#clearpop [data-ck=all]'); await pg.wait_for_timeout(300)
    tot = await pg.evaluate("document.querySelectorAll('#stage [data-rk]').length")
    ok(tot == 0, f'{tag} [이 탭] [모두] → 탭 표시 {tot}')
    await pg.click('#k-undo'); await pg.wait_for_timeout(300)
    c4 = await pg.evaluate(CNT + f"('{C4}')"); c5 = await pg.evaluate(CNT + f"('{C5}')")
    ok(c4 == {'h': 0, 'b': 1} and c5 == {'h': 1, 'b': 0}, f'{tag} ↶ 한 번 → 모두 지우기 전으로 {c4} {c5}')
    await pg.reload(); await pg.wait_for_selector('#stage .tc', timeout=30000); await pg.wait_for_timeout(1200)
    c4 = await pg.evaluate(CNT + f"('{C4}')"); c5 = await pg.evaluate(CNT + f"('{C5}')")
    ok(c4 == {'h': 0, 'b': 1} and c5 == {'h': 1, 'b': 0}, f'{tag} 새로고침 뒤 유지 {c4} {c5}')
    # 표 화면: 정리표 행 = '이 행'
    await pg.goto('about:blank'); await pg.goto(U + '#/OMS1/DD1/sum'); await pg.wait_for_selector('#stage .msum', timeout=30000); await pg.wait_for_timeout(900)
    R = "#stage .msum table.mtx>tbody>tr[data-aid]"
    await pg.evaluate(f"document.querySelectorAll('{R}')[2].id='ux4row'")
    await pg.keyboard.press('h'); await tapword(pg, '#ux4row', 0); await pg.keyboard.press('Escape')
    await pg.click('#k-clear'); await pg.wait_for_selector('#clearpop.on'); await pg.wait_for_timeout(100)
    r = await pg.evaluate("[document.querySelector('#clearpop [data-csc=card]').textContent,document.querySelector('#clearpop [data-csc=card]').disabled,document.querySelector('#clearpop [data-ck=hl] b').textContent,document.querySelector('#ux4row').classList.contains('clrtgt')]")
    ok(r[0] == '이 행' and not r[1] and r[2] == '1' and r[3], f'{tag} 정리표: 대상 = 이 행 {r}')
    await pg.click('#clearpop [data-ck=hl]'); await pg.wait_for_timeout(300)
    ok(await pg.evaluate("document.querySelectorAll('#ux4row [data-rk]').length") == 0, f'{tag} 정리표 이 행 형광 지움')
    ok(not errs, f'{tag} 콘솔 오류 0 {errs[:3]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        try:
            for tag, vp, touch in [('1280', {'width': 1280, 'height': 900}, False), ('1180', {'width': 1180, 'height': 820}, True), ('820', {'width': 820, 'height': 1180}, True)]:
                await run(b, tag, vp, touch)
        finally:
            await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
