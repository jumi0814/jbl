"""ux3 트랙3 묶음 K1 회귀: M = 메뉴 숨기기/보이기(한글 입력 상태 흉내 key='ㅡ' code='KeyM' 포함 · \\ 별칭 · 860 이하는 서랍) · Shift+M = 메모 ·
메모 입력칸 안의 m은 글자 · 집중 모드(V) 중 M = 집중 모드 끄고 메뉴 · 1차 사용자 처음 한 번 알림(LS keyNoticeM) · #k-memo title.
맥 1280×900 · 아이패드 세로 820×1180(터치)·가로 1180×820(터치). 스크린샷 work/_tmp/ux3i_keys_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1300):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
KM = "document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'ㅡ',code:'KeyM',shiftKey:true,bubbles:true,cancelable:true}))"   # 한글 입력 상태의 M
ST = "(()=>{const B=document.body.classList;return {fold:B.contains('sidefold'),nav:B.contains('navopen'),focus:B.contains('focus'),memo:document.querySelector('#memo').classList.contains('on')}})()"
async def run(pg, tag, vp):
    await open_(pg, '#/CONS/WHT/learn'); await pg.evaluate("['sidefold','navfold','navfoldHub','wideSide','focus','keyNoticeM','ux2old'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))"); await open_(pg, '#/CONS/WHT/learn')
    narrow = vp['width'] <= 860
    s0 = await pg.evaluate(ST); await pg.evaluate(KM); await pg.wait_for_timeout(250); s1 = await pg.evaluate(ST)
    if narrow: ok(not s0['nav'] and s1['nav'], f'{tag} M(한글 ㅡ/KeyM) → 서랍 열림 {s0} → {s1}')
    else: ok(not s0['fold'] and s1['fold'], f'{tag} M(한글 ㅡ/KeyM) → 메뉴 숨김 {s0} → {s1}')
    await pg.screenshot(path=J.TMP + f'/ux3i_keys_m_{tag}.png')
    if narrow: await pg.keyboard.press('Escape')
    else:
        await pg.keyboard.press('Shift+M'); await pg.wait_for_timeout(250); s2 = await pg.evaluate(ST); ok(not s2['fold'], f'{tag} M 다시 → 메뉴 보임 {s2}')
        await pg.keyboard.press('Backslash'); await pg.wait_for_timeout(200); s3 = await pg.evaluate(ST); await pg.keyboard.press('Backslash'); await pg.wait_for_timeout(200)
        ok(s3['fold'] and not (await pg.evaluate(ST))['fold'], f'{tag} \\ = 같은 토글(별칭)')
    await pg.wait_for_timeout(200)
    f0 = await pg.evaluate(ST); await pg.keyboard.press('m'); await pg.wait_for_timeout(250); f1 = await pg.evaluate(ST)
    ok(f1['memo'] and f1['fold'] == f0['fold'] and f1['nav'] == f0['nav'], f'{tag} Shift+M → 메모 창(메뉴 그대로) {f1}')
    await pg.wait_for_timeout(150); await pg.keyboard.type('mm'); await pg.wait_for_timeout(150)
    v = await pg.evaluate("document.querySelector('#memota').value"); f2 = await pg.evaluate(ST)
    ok(v.endswith('mm') and f2['fold'] == f0['fold'] and f2['nav'] == f0['nav'], f'{tag} 메모 입력칸 안의 m = 글자({v[-4:]!r}) · 메뉴 그대로')
    await pg.evaluate("document.querySelector('#memota').value='';document.querySelector('#memota').dispatchEvent(new Event('input'));document.querySelector('#memox').click();document.activeElement.blur()"); await pg.wait_for_timeout(400)
    ok('(M)' in await pg.evaluate("document.querySelector('#k-memo').title"), f'{tag} 📝 제목 = M')   # ux4f 10-02 M = 메모
    if not narrow:   # 집중 모드 중 M → 집중 모드 끄고 메뉴 보임
        await pg.keyboard.press('v'); await pg.wait_for_timeout(250); a = await pg.evaluate(ST); await pg.keyboard.press('Shift+M'); await pg.wait_for_timeout(300); b = await pg.evaluate(ST)
        ok(a['focus'] and not b['focus'] and not b['fold'], f'{tag} 집중 모드(V) 중 M → 집중 모드 꺼짐·메뉴 보임 {a} → {b}')
    # 1차 사용자 처음 한 번 알림
    await pg.evaluate("localStorage.setItem('jblhub.v1.ux2old','1');localStorage.removeItem('jblhub.v1.keyNoticeM');localStorage.removeItem('jblhub.v1.keyNoticeM2');localStorage.removeItem('jblhub.v1.focus')"); await open_(pg, '#/CONS/WHT/learn')
    await pg.evaluate("sessionStorage.removeItem('jblhub.v1.toasts')")   # 알림 기록(최근 20개)
    await pg.keyboard.press('Shift+M'); await pg.wait_for_timeout(200)
    if narrow: await pg.keyboard.press('Escape')
    else: await pg.keyboard.press('Shift+M')
    await pg.wait_for_timeout(200); T = await pg.evaluate("JSON.parse(sessionStorage.getItem('jblhub.v1.toasts')||'[]').map(x=>x.t)")
    n = sum('이제 Shift+M' in t for t in T)   # ux4f 10-02 바꾼 키 알림(keyNoticeM2)
    ok(n == 1 and await pg.evaluate("localStorage.getItem('jblhub.v1.keyNoticeM2')") == '1', f'{tag} 1차 사용자 처음 한 번 알림 {n}번 {T}')
    try: await pg.wait_for_function("t=>(document.querySelector('#toast').textContent||'').includes(t)", arg='이제 Shift+M', timeout=6000); shown = True
    except Exception: shown = False
    ok(shown, f'{tag} 알림이 화면에 뜸')
    await pg.evaluate("['sidefold','navfold','navfoldHub','wideSide','ux2old','keyNoticeM','keyNoticeM2'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for tag, vp, touch in [('mac', {'width': 1280, 'height': 900}, False), ('820', {'width': 820, 'height': 1180}, True), ('1180', {'width': 1180, 'height': 820}, True)]:
            ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
            await run(pg, tag, vp); ok(not errs, f'{tag} 콘솔 오류 0 {errs[:2]}'); await ctx.close()
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
