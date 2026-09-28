"""ux3 트랙3 묶음 N3·N4 화면 회귀: 🔑 상자·정리표 🔑 칸·요지 줄 나누기
학습 탭 🔑 = 줄(.kl)·흐름(.kfi·.ksi)·둘째 줄(.ksub) · 숨긴 구분자(.ksep.kh)는 화면에 없음 · 압축(C)·⚡ 복습(R) = 한 줄 흐름(구분자 보임) ·
정리표 요약 모드 🔑 칸 = 줄로 나뉨(옛 '한 줄 흐름' 아님) · 요지(.mg·카드 머리 .one) ' — ' 둘째 줄 · 🔑 안에 걸친 표시가 숨긴 구분자에 갇히지 않음(rkshow) ·
가로 넘침 없음 · 콘솔 오류 0. 맥 1280×900 · 아이패드 세로 820×1180·가로 1180×820(터치). 스크린샷 work/_tmp/ux3i_kb_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1400):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
KB = """(t)=>{const k=[...document.querySelectorAll('#stage .c-key')].find(e=>e.textContent.includes(t));if(!k)return null;k.closest('.tc').classList.add('open');k.scrollIntoView({block:'center'});
 const ls=[...k.querySelectorAll('.kl,.ksub')].filter(e=>e.getClientRects().length);const tops=new Set(ls.map(e=>Math.round(e.getBoundingClientRect().top)));
 const kh=[...k.querySelectorAll('.ksep.kh')];return {lines:ls.length,rows:tops.size,disp:ls.length?getComputedStyle(ls[0]).display:'',khShown:kh.filter(e=>e.getClientRects().length).length,kh:kh.length}}"""
async def run(pg, tag, W):
    await open_(pg, '#/ANAT/LIP/learn'); await pg.evaluate("['cond','review','focus','sidefold','wideSide'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))"); await open_(pg, '#/ANAT/LIP/learn')
    r = await pg.evaluate(KB, '인중 = philtrum')
    ok(r and r['lines'] == 2 and r['rows'] == 2 and r['disp'] == 'block' and r['kh'] >= 1 and r['khShown'] == 0, f'{tag} 학습 🔑 라벨 줄 2줄 · 숨긴 구분자 안 보임 {r}')
    el = await pg.evaluate_handle("[...document.querySelectorAll('#stage .c-key')].find(e=>e.textContent.includes('인중 = philtrum'))")
    await el.as_element().screenshot(path=J.TMP + f'/ux3i_kb_learn_{tag}.png')
    one = await pg.evaluate("(()=>{const o=[...document.querySelectorAll('#stage .thead .one')].find(e=>e.querySelector('.ksub'));if(!o)return null;const s=o.querySelector('.ksub');return [getComputedStyle(s).display,o.querySelector('.ksep.kh').getClientRects().length]})()")
    ok(one and one[0] == 'block' and one[1] == 0, f'{tag} 카드 머리 요지 둘째 줄(.ksub block · 구분자 숨김) {one}')
    await pg.keyboard.press('c'); await pg.wait_for_timeout(300); c = await pg.evaluate(KB, '인중 = philtrum'); await pg.keyboard.press('c'); await pg.wait_for_timeout(200)
    ok(c and c['disp'] == 'inline' and c['khShown'] == c['kh'], f'{tag} 압축(C) = 한 줄 흐름 · 구분자 보임 {c}')
    await pg.keyboard.press('r'); await pg.wait_for_timeout(500); rv = await pg.evaluate(KB, '인중 = philtrum')
    await pg.screenshot(path=J.TMP + f'/ux3i_kb_review_{tag}.png'); await pg.keyboard.press('r'); await pg.wait_for_timeout(300)
    ok(rv and rv['disp'] == 'inline' and rv['khShown'] == rv['kh'], f'{tag} ⚡ 복습(R) = 한 줄 흐름 · 구분자 보임 {rv}')
    # 표시가 숨긴 구분자에 걸쳐도 보임(rkshow) — '인중 = philtrum(column·dimple) · 입술' 걸친 형광펜
    await pg.evaluate("""()=>{const k=[...document.querySelectorAll('#stage .c-key')].find(e=>e.textContent.includes('인중 = philtrum'));const B=k.closest('[data-aid]');const T=__h.Kit.textOf(B);const x='dimple) · 입술';
      const A=JSON.parse(localStorage.getItem('jblhub.v1.ann.ANAT')||'{}');const a=T.indexOf(x);A[B.dataset.aid]=[{t:'h',x,i:0,p:T.slice(Math.max(0,a-12),a),s:T.slice(a+x.length,a+x.length+12),v:__h.Kit.fnv(T),c:'y'}];localStorage.setItem('jblhub.v1.ann.ANAT',JSON.stringify(A));}""")
    await open_(pg, '#/ANAT/LIP/learn')
    hs = await pg.evaluate("(()=>{const k=[...document.querySelectorAll('#stage .c-key')].find(e=>e.textContent.includes('인중 = philtrum'));const m=[...k.querySelectorAll('[data-rk]')];return [m.map(e=>e.textContent).join(''),m.every(e=>e.getClientRects().length>0)]})()")
    ok(hs[0] == 'dimple) · 입술' and hs[1], f'{tag} 구분자에 걸친 표시 전부 보임 {hs}')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.ann.ANAT')")
    # 정리표 요약 모드 — 🔑 칸 줄로 나뉨 · 요지 둘째 줄
    for h, t in [('#/GERI/ENDO/sum', 'Negotiation = Do 100'), ('#/CONS/CRK/sum', 'Bite pain 51%')]:
        await open_(pg, h, 1600)
        s = await pg.evaluate("""(t)=>{const cs=[...document.querySelectorAll('#stage .msum td.mk .mkey')].filter(e=>e.offsetParent);const k=t?cs.find(e=>e.textContent.includes(t)):cs.find(e=>e.querySelector('.kl,li'));if(!k)return null;k.scrollIntoView({block:'center'});
          const ls=[...k.querySelectorAll('.kl,li')].filter(e=>e.getClientRects().length);const tops=new Set(ls.map(e=>Math.round(e.getBoundingClientRect().top)));
          const mg=[...document.querySelectorAll('#stage .msum .mg')].find(e=>e.querySelector('.ksub')&&e.offsetParent);return {n:ls.length,rows:tops.size,d:ls.length?getComputedStyle(ls[0]).display:'',mg:mg?getComputedStyle(mg.querySelector('.ksub')).display:null,cards:cs.length}}""", t)
        ok(s and s['n'] >= 2 and s['rows'] >= 2 and s['d'] in ('block', 'list-item') and s['mg'] == 'block', f'{tag} {h} 요약 모드 🔑 칸 {s}')
        await pg.screenshot(path=J.TMP + f'/ux3i_kb_sum_{h.split("/")[1]}_{tag}.png')
        ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{tag} {h} 가로 넘침 없음')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for tag, vp, touch in [('mac', {'width': 1280, 'height': 900}, False), ('820', {'width': 820, 'height': 1180}, True), ('1180', {'width': 1180, 'height': 820}, True)]:
            ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
            await run(pg, tag, vp['width']); ok(not errs, f'{tag} 콘솔 오류 0 {errs[:2]}'); await ctx.close()
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
