"""B11 회귀: 알림 대기열·등급·위치 — 연달아 부르면 하나씩 차례로(동시에 1개) · result 6초 + [보기] · error는 7초 뒤에도 남고 ✕로 닫힘 ·
화면 아래 도구 막대 위(탭 줄과 겹치지 않음, 팝업이 열려 있으면 팝업 아래) · 최근 알림 20개(sessionStorage) → [복원] 창 '최근 알림' · 옛 toast(글, ms) 그대로.
맥 1280×900 + 아이패드 세로 820×1180 + 가로 1180×820. 스크린샷 work/_tmp/ux2i_b11_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, time
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
VIS = "(()=>{const e=document.querySelector('#toast');return e&&getComputedStyle(e).display!=='none'?e.querySelector('span').textContent:''})()"
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await pg.goto(U + '#/OMS1/DD1/learn'); await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3"); await pg.wait_for_timeout(800)
    await pg.evaluate("sessionStorage.clear()")
    await pg.wait_for_function("getComputedStyle(document.querySelector('#toast')).display==='none'", timeout=8000)
    # 차례로 하나씩
    await pg.evaluate("__h.toast('알림 A',{level:'result'});__h.toast('알림 B',{level:'result'});__h.toast('알림 C')")
    seen, multi, t0 = [], False, time.time()
    while time.time() - t0 < 12:
        v = await pg.evaluate(VIS); n = await pg.evaluate("document.querySelectorAll('#toast span').length")
        multi = multi or n > 1
        if v and (not seen or seen[-1] != v): seen.append(v)
        if seen[-1:] == ['알림 C'] and not v: break
        await pg.wait_for_timeout(50)
    ok(seen[:3] == ['알림 A', '알림 B', '알림 C'] and not multi, f'세 번 연달아 → 차례로 {seen} · 동시에 1개')
    # result [보기]
    await pg.evaluate("window.__acted=0;__h.toast('결과 알림',{level:'result',action:{label:'보기',fn:()=>{window.__acted=1}}})")
    await pg.wait_for_function("document.querySelector('#toast .tact')", timeout=3000)
    await pg.screenshot(path=J.TMP + f'/ux2i_b11_result_{tag}.png')
    tb = await pg.evaluate("document.querySelector('#toast').getBoundingClientRect().toJSON()"); db = await pg.evaluate("document.querySelector('#dtabs').getBoundingClientRect().toJSON()")
    kb = await pg.evaluate("document.querySelector('#kit').getBoundingClientRect().toJSON()")
    ov = lambda a, c: not (a['bottom'] <= c['top'] or c['bottom'] <= a['top'] or a['right'] <= c['left'] or c['right'] <= a['left'])
    ok(not ov(tb, db) and tb['bottom'] <= kb['top'] + 1, f"토스트가 탭 줄과 안 겹치고 도구 막대 위 (토스트 {tb['top']:.0f}~{tb['bottom']:.0f} · 탭 {db['top']:.0f}~{db['bottom']:.0f} · 도구 {kb['top']:.0f})")
    await pg.click('#toast .tact'); ok(await pg.evaluate("window.__acted") == 1 and await pg.evaluate(VIS) == '', 'result [보기] 누르면 동작 · 닫힘')
    # error — 7초 뒤에도 남음 · ✕
    await pg.evaluate("__h.toast('저장 실패 예시',{level:'error'})")
    await pg.wait_for_timeout(7200)
    ok(await pg.evaluate("document.querySelectorAll('#toasterr .terr').length") == 1 and await pg.is_visible('#toasterr .terr'), 'error는 7초 뒤에도 남아 있음')
    await pg.screenshot(path=J.TMP + f'/ux2i_b11_error_{tag}.png')
    await pg.click('#toasterr .tx'); ok(await pg.evaluate("document.querySelectorAll('#toasterr .terr').length") == 0, 'error ✕로 닫힘')
    # 옛 toast(글, ms) · 팝업이 열려 있으면 팝업 아래
    await pg.click('#clock'); await pg.wait_for_timeout(200)
    await pg.evaluate("__h.toast('팝업 중 알림',1500)"); await pg.wait_for_function("document.querySelector('#toast span')&&document.querySelector('#toast span').textContent==='팝업 중 알림'", timeout=4000)
    pb = await pg.evaluate("document.querySelector('#tpop').getBoundingClientRect().bottom"); tt = await pg.evaluate("document.querySelector('#toast').getBoundingClientRect().top")
    ok(tt >= pb, f'팝업이 열려 있으면 팝업 아래 (팝업 {pb:.0f} · 토스트 {tt:.0f})')
    await pg.keyboard.press('Escape')
    # 최근 알림
    await pg.evaluate("document.querySelector('#bkup').click()"); await pg.click('#rstr'); await pg.wait_for_timeout(200)
    lg = await pg.evaluate("(()=>{const d=document.querySelector('#rpop .rlog');return d?d.textContent:''})()")
    ok('최근 알림' in lg and '저장 실패 예시' in lg and '알림 A' in lg, f"복원 창 '최근 알림' ({lg[:40]!r})")
    n = await pg.evaluate("JSON.parse(sessionStorage.getItem('jblhub.v1.toasts')).length"); ok(n <= 20, f'sessionStorage 최근 알림 {n}개 (≤20)')
    await pg.keyboard.press('Escape')
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
