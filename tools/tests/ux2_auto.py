"""C03·C04 회귀: 자동 빈칸 규칙·긴 빈칸·옛 자동 빈칸 정리 · 🧹 지우기 메뉴·⚡ 창 문구
C03 '이 탭 전체' 저장형 → ann 증가 < 2KB·규칙 autoRule.<S>['DD1/learn']·새로고침 뒤 빈칸 수 같음 · '이 카드' 저장형 → a:1 기록 ·
    긴 빈칸(40자↑)은 {x:앞 24자, xl, xh}로 저장·해시로 복원 · 옛 형식(카드마다 .k 글자 그대로 3개↑) → 공간 정리 [→ 규칙으로 바꾸기] = 규칙 1개·그 기록만 빠지고 형광펜은 남음
C04 형광펜 2 + 자동 빈칸(a:1)에서 '자동 빈칸만' → 형광펜 2개 남음 · '이 카드' 범위는 다른 카드를 안 바꿈 · 확인창에 개수 · 지우기 전 자동 백업 ·
    ⚡ 창 미리 보기('이 카드의 빨간 글씨 n개'/'이 탭 전체 n개')·[이 탭의 자동 빈칸 지우기] · 창·title에 '보이는 화면' 0개
맥 1280×900(전 과정) + 아이패드 세로 820×1180 · 가로 1180×820(⚡ 창·🧹 메뉴 모양). 스크린샷 work/_tmp/ux2i_c03_*.png·ux2i_c04_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []; K = 'jblhub.v1.'
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
ANN = "(()=>{const v=localStorage.getItem('jblhub.v1.ann.OMS1');return v?JSON.parse(v):{}})()"
NB = "document.querySelectorAll('#stage [data-rk=b]').length"
async def openL(pg, h='#/OMS1/DD1/learn'):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3"); await pg.wait_for_timeout(500)
async def card_with_k(pg, need=3):
    for _ in range(20):
        n = await pg.evaluate("(()=>{const c=__h.curCard();return c?c.querySelectorAll('.k').length:0})()")
        if n >= need: return await pg.evaluate("__h.curCard().dataset.aid")
        await pg.keyboard.press('j'); await pg.wait_for_timeout(250)
    return None
async def shots(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await openL(pg); await pg.evaluate("localStorage.clear()"); await openL(pg); await card_with_k(pg)
    await pg.click('#k-auto'); await pg.check('input[value="red"]'); await pg.select_option('#asc', 'card'); await pg.wait_for_timeout(100)
    t = await pg.inner_text('#aprev'); ok(t.startswith('이 카드의 빨간 글씨') and '개를 빈칸으로 저장' in t, f'⚡ 미리 보기(이 카드) {t!r}')
    await pg.screenshot(path=J.TMP + f'/ux2i_c03_autopop_{tag}.png'); await pg.keyboard.press('Escape')
    await pg.click('#k-clear'); await pg.wait_for_selector('#clearpop.on'); await pg.screenshot(path=J.TMP + f'/ux2i_c04_menu_{tag}.png')
    ok(await pg.locator('#clearpop .crow').count() == 4, '🧹 메뉴 4줄'); await pg.keyboard.press('Escape')
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()
async def main_flow(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []; dlg = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    async def on_dialog(d): dlg.append(d.message); await d.accept()
    pg.on('dialog', on_dialog); print('== C03·C04 맥')
    await openL(pg); await pg.evaluate("localStorage.clear()"); await pg.evaluate("__h.bkClear()"); await openL(pg)
    # ---- C03 이 탭 전체 = 규칙
    a0 = len(await pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')||''"))
    await pg.click('#k-auto'); await pg.check('input[value="red"]'); await pg.select_option('#asc', 'all'); await pg.wait_for_timeout(100)
    t = await pg.inner_text('#aprev'); ok(t.startswith('이 탭 전체의 빨간 글씨') and '규칙' in t, f'⚡ 미리 보기(이 탭) {t!r}')
    await pg.click('#ago'); await pg.wait_for_timeout(300)
    n1 = await pg.evaluate(NB); a1 = len(await pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')||''"))
    rule = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.autoRule.OMS1')") or '{}')
    ok(n1 > 50 and a1 - a0 < 2048 and 'DD1/learn' in rule, f'이 탭 전체 빈칸 {n1}개 · ann 증가 {a1 - a0}자 (<2KB) · 규칙 {list(rule)}')
    await pg.evaluate("document.querySelector('#stage [data-rk=b]').click()"); await pg.wait_for_timeout(100)
    await openL(pg); n2 = await pg.evaluate(NB); ok(n2 == n1, f'새로고침 뒤 빈칸 수 같음 {n1} → {n2}')
    ok(await pg.evaluate("document.querySelectorAll('#stage [data-rk=b].show').length") == 1, '연 빈칸 1개(sessionStorage) 유지')
    # ⚡ [이 탭의 자동 빈칸 지우기]
    await pg.click('#k-auto'); await pg.wait_for_timeout(100); t = await pg.inner_text('#aclr'); ok(t.endswith(str(n1)), f'[이 탭의 자동 빈칸 지우기] 개수 {t!r}')
    await pg.click('#aclr'); await pg.wait_for_timeout(300)
    ok(await pg.evaluate(NB) == 0 and 'DD1/learn' not in json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.autoRule.OMS1')") or '{}'), '이 탭의 자동 빈칸 지우기 → 규칙 삭제·빈칸 0')
    ok(any('자동 빈칸 ' + str(n1) + '개' in m for m in dlg), f'확인창에 개수 {dlg[-1][:60] if dlg else ""!r}')
    await pg.keyboard.press('Meta+z'); await pg.wait_for_timeout(300); ok(await pg.evaluate(NB) == n1, '↶ 되돌리기로 규칙 복귀')
    await pg.keyboard.press('Meta+z'); await pg.wait_for_timeout(300); ok(await pg.evaluate(NB) == 0, '한 번 더 ↶ → 규칙 적용 전')
    # ---- C04 형광펜 2 + 이 카드 자동 빈칸(a:1) → '자동 빈칸만'
    aid = await card_with_k(pg, 3); ok(aid is not None, f'빨간 글씨 3개↑ 카드 {aid}')
    words = await pg.evaluate("aid=>{const B=document.querySelector('[data-aid=\"'+aid+'\"]');const T=__h.Kit.textOf(B);const W=[...B.querySelectorAll('.tbody li,.tbody div.li')].flatMap(e=>[...e.childNodes].filter(n=>n.nodeType===3).flatMap(n=>n.nodeValue.split(/[^A-Za-z가-힣]+/)));return [...new Set(W)].filter(w=>w.length>=3&&T.split(w).length===2).slice(0,2)}", aid)
    other = await pg.evaluate("aid=>{const cs=[...document.querySelectorAll('#stage .tc')];const i=cs.findIndex(c=>c.dataset.aid===aid);return cs[i+1].dataset.aid}", aid)
    await pg.evaluate("([aid,w,o])=>{const A=JSON.parse(localStorage.getItem('jblhub.v1.ann.OMS1')||'{}');A[aid]=w.map(x=>({t:'h',x,i:0,c:'y'}));A[o]=[{t:'h',x:'@@없는글자',i:0,c:'g',lost:1}];localStorage.setItem('jblhub.v1.ann.OMS1',JSON.stringify(A));}", [aid, words, other])
    await openL(pg); await pg.evaluate("aid=>__h.openDoc('OMS1','DD1','learn',aid)", aid); await pg.wait_for_timeout(500)
    cur = await pg.evaluate("__h.curCard()&&__h.curCard().dataset.aid"); ok(cur == aid, f'지금 카드 = {cur}')
    await pg.click('#k-auto'); await pg.check('input[value="red"]'); await pg.select_option('#asc', 'card'); await pg.click('#ago'); await pg.wait_for_timeout(300)
    A = await pg.evaluate(ANN); na = len([o for o in A.get(aid, []) if o.get('a') == 1]); nh = len([o for o in A.get(aid, []) if o['t'] == 'h'])
    ok(na >= 3 and nh == 2, f'이 카드 저장형 → a:1 기록 {na}개 · 형광펜 {nh}개')
    await pg.click('#k-clear'); await pg.wait_for_selector('#clearpop.on')
    row = await pg.inner_text('#clearpop [data-ck=auto]'); ok(str(na) in row, f'🧹 자동 빈칸만 개수 {row!r}')
    await pg.click('#clearpop [data-ck=auto]'); await pg.wait_for_timeout(300)
    A = await pg.evaluate(ANN); ok([o['t'] for o in A.get(aid, [])] == ['h', 'h'] and A.get(other, [{}])[0].get('lost') == 1, f"'자동 빈칸만' → 형광펜 2개 남음 · 다른 카드 잃은 표시 그대로")
    ok(any(f'자동 빈칸 {na}개' in m for m in dlg), '확인창에 개수')
    await pg.wait_for_timeout(300); L = await pg.evaluate("__h.bkList()"); ok(any(x['why'] == '표시 지우기 전' for x in L), "지우기 전 자동 백업('표시 지우기 전')")
    # 이 카드 '모두' → 다른 카드 표시는 그대로
    await pg.evaluate("([aid,o])=>{const A=JSON.parse(localStorage.getItem('jblhub.v1.ann.OMS1'));A[o]=(A[o]||[]);localStorage.setItem('jblhub.v1.ann.OMS1',JSON.stringify(A));}", [aid, other])
    ow = await pg.evaluate("o=>{const B=document.querySelector('[data-aid=\"'+o+'\"]');const T=__h.Kit.textOf(B);const W=T.split(/[^A-Za-z가-힣]+/);return W.filter(w=>w.length>=3&&T.split(w).length===2)[0]}", other)
    await pg.evaluate("([o,w])=>{const A=JSON.parse(localStorage.getItem('jblhub.v1.ann.OMS1'));A[o].push({t:'h',x:w,i:0,c:'p'});localStorage.setItem('jblhub.v1.ann.OMS1',JSON.stringify(A));}", [other, ow])
    await openL(pg); await pg.evaluate("aid=>__h.openDoc('OMS1','DD1','learn',aid)", aid); await pg.wait_for_timeout(500)
    await pg.click('#k-clear'); await pg.wait_for_selector('#clearpop.on'); await pg.click('#clearpop [data-csc=card]'); await pg.click('#clearpop [data-ck=all]'); await pg.wait_for_timeout(300)
    A = await pg.evaluate(ANN); ok(not A.get(aid) and len(A.get(other, [])) == 2, f"'이 카드' 모두 → 이 카드 0 · 다른 카드 {len(A.get(other, []))}개 그대로")
    # 긴 빈칸 — 압축 기록으로 복원
    await openL(pg); info = await pg.evaluate("""(()=>{const td=[...document.querySelectorAll('#stage .tc tbody td')].find(t=>t.textContent.trim().length>=40&&t.closest('[data-aid]'));const B=td.closest('[data-aid]');const T=__h.Kit.textOf(B);const x=td.textContent.trim();return [B.dataset.aid,x,T.split(x).length-1,__h.Kit.fnv(x)]})()""")
    await pg.evaluate("([aid,x,h])=>{localStorage.setItem('jblhub.v1.ann.OMS1',JSON.stringify({[aid]:[{t:'b',x:x.slice(0,24),xl:x.length,xh:h,i:0}]}));}", [info[0], info[1], info[3]])
    await openL(pg); got = await pg.evaluate("aid=>[...document.querySelectorAll('[data-aid=\"'+aid+'\"] [data-rk=b]')].map(e=>e.textContent).join('')", info[0])
    rec = (await pg.evaluate(ANN))[info[0]][0]
    ok(got == info[1] and len(rec['x']) == 24 and rec['xl'] == len(info[1]), f'긴 빈칸 {len(info[1])}자 → 압축 기록으로 복원·다시 저장해도 압축 (x {len(rec["x"])}자)')
    await pg.keyboard.press('b'); await pg.evaluate("aid=>{const e=document.querySelector('[data-aid=\"'+aid+'\"] [data-rk=b]');const r=e.getBoundingClientRect();e.scrollIntoView({block:'center'});}", info[0])
    # ---- 옛 형식 자동 빈칸 → 규칙
    await pg.keyboard.press('Escape'); await pg.evaluate("localStorage.removeItem('jblhub.v1.ann.OMS1');localStorage.removeItem('jblhub.v1.autoRule.OMS1')"); await openL(pg)
    seed = await pg.evaluate("""(()=>{const A={};let n=0;let hw=null;document.querySelectorAll('#stage .tc').forEach(c=>{const ks=[...c.querySelectorAll('.k')].filter(k=>k.closest('[data-aid]')===c&&!k.closest('.noann,button'));if(ks.length<3)return;const cnt={};A[c.dataset.aid]=ks.map(k=>{const x=k.textContent.trim();cnt[x]=(cnt[x]||0)+1;n++;return {t:'b',x,i:cnt[x]-1};});});
      const c0=[...document.querySelectorAll('#stage .tc')].find(c=>A[c.dataset.aid]);const T=__h.Kit.textOf(c0);hw=T.split(/[^A-Za-z]+/).filter(w=>w.length>=5&&T.split(w).length===2)[0];A[c0.dataset.aid].push({t:'h',x:hw,i:0,c:'y'});
      localStorage.setItem('jblhub.v1.ann.OMS1',JSON.stringify(A));return [n,c0.dataset.aid,hw];})()""")
    await openL(pg); await pg.click('#rstr'); await pg.wait_for_selector('#rpop #rclean'); await pg.evaluate("document.querySelector('#rclean').open=true"); await pg.wait_for_selector('#oldauto [data-clean]', timeout=5000)
    lab = await pg.inner_text('#oldauto'); ok(f'{seed[0]}개' in lab and '규칙 1개' in lab, f'공간 정리 미리 보기 {lab!r} (심은 {seed[0]}개)')
    await pg.screenshot(path=J.TMP + '/ux2i_c03_clean.png')
    await pg.click('#oldauto [data-clean]'); await pg.wait_for_timeout(500)
    A = await pg.evaluate(ANN); R = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.autoRule.OMS1')") or '{}')
    left_b = sum(1 for L in A.values() for o in L if o['t'] == 'b')
    ok(list(R) == ['DD1/learn'] and left_b == 0 and [o['x'] for o in A.get(seed[1], [])] == [seed[2]], f'규칙 {list(R)} · 남은 빈칸 기록 {left_b} · 형광펜 남음')
    ok(await pg.evaluate(NB) >= seed[0], f"빈칸은 그대로 보임 ({await pg.evaluate(NB)} ≥ {seed[0]})")
    await pg.wait_for_timeout(300); L = await pg.evaluate("__h.bkList()"); ok(any(x['why'] == '자동 빈칸 정리 전' for x in L), "정리 전 자동 백업('자동 빈칸 정리 전')")
    # '보이는 화면' 문자열 0
    await pg.keyboard.press('Escape'); await pg.click('#k-auto')
    ok(await pg.evaluate("document.documentElement.outerHTML.split('보이는 화면').length-1") == 0, "창·title에 '보이는 화면' 0개")
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await main_flow(b)
        await shots(b, {'width': 1280, 'height': 900}, False, 'mac')
        await shots(b, {'width': 820, 'height': 1180}, True, 'ipp')
        await shots(b, {'width': 1180, 'height': 820}, True, 'ipl')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
