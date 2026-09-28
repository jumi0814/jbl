"""C07 회귀: JB 회차 고정과 풀이 상태 보존
PHARM _jb '안 푼 것' + 강의 필터 → 한 장씩 4문항 채점(✓✗✓✗) → '5/N' · 새로고침해도 '5/N'(안 푼 것 필터를 다시 계산하지 않음)·요약 ✓2 ✗2 ·
같은 컨텍스트 새 탭 #/PHARM/_jb/_jb → 한 장씩·필터·위치 복원(LS) · 과목 홈·허브 카드 '↪ 이어서 풀기: … 한 장씩 5/N' · 회차 중 필터를 바꾸면 '새 회차를 시작할까요?'(취소 = 그대로) ·
'필터 다시 적용 ↻' 알약 · 8일 지난 LS jbst는 무시.
맥 1280×900(전 과정) + 아이패드 세로 820×1180 · 가로 1180×820(알약·이어서 풀기 모양). 스크린샷 work/_tmp/ux2i_c07_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def jb(pg, h='#/PHARM/_jb'):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_function("document.querySelectorAll('#cards .qc').length>10"); await pg.wait_for_timeout(400)
async def setup(pg):
    await jb(pg); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await jb(pg)
    lec = await pg.evaluate("(()=>{const c={};document.querySelectorAll('#cards .qc').forEach(q=>{if(q.dataset.tier!=='C')c[q.dataset.lec]=(c[q.dataset.lec]||0)+1;});return Object.entries(c).sort((a,b)=>b[1]-a[1])[0][0]})()")
    await pg.evaluate("document.querySelector('#fmore').click()"); await pg.select_option('#flec', lec); await pg.click('#jbbar [data-qf="todo"]'); await pg.wait_for_timeout(200)
    await pg.click('#fone'); await pg.wait_for_timeout(300)
    return lec
POS = "document.querySelector('#opos').textContent"
async def run(b, vp, touch, tag, full):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []; D = {'acc': True, 'msg': []}
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    async def on_dialog(d):
        D['msg'].append(d.message)
        await (d.accept() if D['acc'] else d.dismiss())
    pg.on('dialog', on_dialog); print('==', tag)
    lec = await setup(pg); n0 = await pg.evaluate("__h.JB.vis.length")
    for k in ['o', 'x', 'ArrowRight', 'o', 'x', 'ArrowRight']:   # ux2 F07 ✗는 답을 펼치고 머묾 → →로 넘김
        await pg.keyboard.press(k); await pg.wait_for_timeout(450)
    p1 = await pg.evaluate(POS); ok(p1 == f'5/{n0}', f'4문항 채점 뒤 {p1} (N={n0})')
    await pg.screenshot(path=J.TMP + f'/ux2i_c07_one_{tag}.png')
    await pg.reload(); await pg.wait_for_function("document.querySelectorAll('#cards .qc').length>10"); await pg.wait_for_timeout(500)
    p2 = await pg.evaluate(POS); ok(p2 == f'5/{n0}', f'새로고침 뒤 {p2} 유지')
    sm = await pg.evaluate("__h.JB.sumHTML().replace(/<[^>]+>/g,'')"); ok(f'이번 회차 {n0}문항' in sm and '✓ 2' in sm and '✗ 2' in sm, f'요약 {sm[:60]!r}')
    ok(await pg.locator('#jbre').count() == 1, "'필터 다시 적용 ↻' 알약")
    if full:
        # 새 탭(같은 컨텍스트) — LS로 복원
        pg2 = await ctx.new_page(); await pg2.goto(U + '#/PHARM/_jb/_jb'); await pg2.wait_for_function("document.querySelectorAll('#cards .qc').length>10"); await pg2.wait_for_timeout(500)
        ok(await pg2.evaluate(POS) == f'5/{n0}' and await pg2.evaluate("document.querySelector('#fone').classList.contains('on')") and await pg2.evaluate("document.querySelector('#flec').value") == lec,
           f"새 탭 → 한 장씩·강의 필터·위치 {await pg2.evaluate(POS)}")
        await pg2.close()
        # 과목 홈·허브 카드 '이어서 풀기'
        await pg.goto('about:blank'); await pg.goto(U + '#/PHARM/_home'); await pg.wait_for_selector('#stage [data-jbres]'); t = await pg.inner_text('#stage [data-jbres]')
        ok('이어서 풀기' in t and '안 푼 것' in t and f'5/{n0}' in t, f'과목 홈 {t!r}')
        await pg.goto('about:blank'); await pg.goto(U + '#/'); await pg.wait_for_selector('.scard[data-s="PHARM"] [data-jbres]'); t = await pg.inner_text('.scard[data-s="PHARM"] [data-jbres]'); ok(f'5/{n0}' in t, f'허브 카드 {t!r}')
        await pg.click('.scard[data-s="PHARM"] [data-jbres]'); await pg.wait_for_function("location.hash.indexOf('_jb')>0"); await pg.wait_for_timeout(500)
        ok(await pg.evaluate(POS) == f'5/{n0}', '누르면 그 회차·그 문항으로')
        # 회차 중 필터 바꾸기 → 확인(취소 = 그대로)
        D['acc'] = False; await pg.click('#jbbar [data-qf=""]'); await pg.wait_for_timeout(300)
        ok(any('새 회차를 시작할까요' in m for m in D['msg']) and await pg.evaluate(POS) == f'5/{n0}' and await pg.evaluate("document.querySelector('#jbbar [data-qf=\"todo\"]').classList.contains('on')"), '필터를 바꾸면 확인 · 취소하면 그대로')
        D['acc'] = True; await pg.click('#jbbar [data-qf=""]'); await pg.wait_for_timeout(300)
        n1 = await pg.evaluate("__h.JB.vis.length"); ok(await pg.evaluate(POS) == f'1/{n1}' and n1 >= n0, f'확인 → 새 회차 {await pg.evaluate(POS)}')
        # 8일 지난 LS
        await pg.evaluate("(()=>{const k='jblhub.v1.jbst.PHARM._jb';const v=JSON.parse(localStorage.getItem(k));v.at=Date.now()-8*864e5;localStorage.setItem(k,JSON.stringify(v));})()")
        pg3 = await ctx.new_page(); await pg3.goto(U + '#/PHARM/_jb/_jb'); await pg3.wait_for_function("document.querySelectorAll('#cards .qc').length>10"); await pg3.wait_for_timeout(400)
        ok(not await pg3.evaluate("document.querySelector('#fone').classList.contains('on')"), '8일 지난 LS jbst는 무시')
        await pg3.close()
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
