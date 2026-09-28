"""두 트랙 병합(묶음 2·3 × 4·5) 상호작용 회귀 — 맥 1280×900 + 아이패드 세로 820×1180 · 가로 1180×820
① 규칙 자동 빈칸(C03 .rk-b[data-auto])은 '내 표시'(D01 .has-rk·'내 표시만' 필터)로 치지 않음 — 형광펜을 넣은 카드만 .has-rk
② 자동 빈칸 대상은 D06 두 단계를 따름: 규칙 red = .k2(본문 굵은 핵심어) 밖 · red2 = .k 전부 · 옛 자동 빈칸 정리(공간 정리)는 red2 규칙
③ 미니바 = '카드 n/N'(#lmpre·#lmn·#lmsuf 안 #lmN) — 맨 위는 '틀 · N장', J 뒤 '카드 1/N'(N = 보이는 카드)
④ sumMig: 플래그 sumMig.<S>가 있어도 옛 '<S>:<K>:sum' 표시가 남아 있으면 행으로 옮김 · 합치기(mergeData)는 sumMig 플래그를 가져오지 않음
⑤ 백업 dumpAll에 트랙 B 새 키(review·figmode·cover.*·sumdense) 포함 · 페이지 오류 0. 스크린샷 work/_tmp/ux2i_merge_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; NS = 'jblhub.v1.'; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def openL(pg, h='#/OMS1/DD1/learn'):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3", timeout=20000)
    await pg.wait_for_function("document.querySelector('#lmn')", timeout=10000)
async def flow(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await openL(pg); await pg.evaluate("localStorage.clear()"); await openL(pg)
    # ③ 미니바
    await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(300)
    t0 = (await pg.inner_text('#lmcur')).strip()
    ok(await pg.locator('#lmcur #lmpre').count() == 1 and await pg.locator('#lmcur #lmsuf #lmN').count() == 1, '미니바 구조 #lmpre·#lmn·#lmsuf>#lmN')
    ok(t0.startswith('틀'), f'맨 위 미니바 {t0!r} (틀 · N장)')
    await pg.keyboard.press('j'); await pg.wait_for_function("/^카드\\s*1\\s*\\//.test(document.querySelector('#lmcur').textContent.trim())", timeout=5000)
    t1 = (await pg.inner_text('#lmcur')).strip(); nvis = await pg.evaluate("[...document.querySelectorAll('#stage .tc')].filter(c=>c.offsetParent!==null).length")
    ok(t1.replace(' ', '').startswith('카드1/' + str(nvis)), f'J 뒤 미니바 {t1!r} (보이는 카드 {nvis})')
    # ① 규칙 빈칸은 내 표시가 아님
    await pg.evaluate("([ns])=>{localStorage.setItem(ns+'autoRule.OMS1',JSON.stringify({'DD1/learn':{kind:'red',scope:'all',one:false,at:Date.now()}}));}", [NS])
    await openL(pg)
    nr = await pg.evaluate("document.querySelectorAll('#stage .rk-b[data-auto]').length")
    nk2 = await pg.evaluate("document.querySelectorAll('#stage .k.k2 .rk-b[data-auto]').length")
    nhas = await pg.evaluate("document.querySelectorAll('#stage .has-rk').length")
    ok(nr > 20, f'규칙 빈칸 {nr}개 그려짐')
    ok(nk2 == 0, f'규칙 red는 .k2(본문 굵은 핵심어) 밖만 ({nk2})')
    ok(nhas == 0, f'규칙 빈칸만 있을 때 .has-rk 0 ({nhas})')
    await pg.evaluate("document.querySelector('#stage').classList.add('cond')"); await pg.wait_for_timeout(100)
    nshow = await pg.evaluate("[...document.querySelectorAll('#stage.cond .tbody .li')].filter(l=>getComputedStyle(l).boxShadow.includes('inset')).length")
    ok(nshow == 0, f'압축 보기에서 규칙 빈칸 줄에 노란 선 0 ({nshow})')
    await pg.evaluate("document.querySelector('#stage').classList.remove('cond')")
    # 형광펜 하나 → 그 카드만 .has-rk
    c = await pg.evaluate("""(()=>{const c=[...document.querySelectorAll('#stage .tc')].find(c=>{const T=__h.Kit.textOf(c);return T.split(/[^A-Za-z]+/).some(w=>w.length>=6&&T.split(w).length===2);});const T=__h.Kit.textOf(c);
      return [c.dataset.aid,T.split(/[^A-Za-z]+/).filter(w=>w.length>=6&&T.split(w).length===2)[0]];})()""")
    await pg.evaluate("([ns,aid,w])=>{localStorage.setItem(ns+'ann.OMS1',JSON.stringify({[aid]:[{t:'h',x:w,i:0,c:'y'}]}));}", [NS, c[0], c[1]])
    await openL(pg)
    flagged = await pg.evaluate("[...document.querySelectorAll('#stage .tc.has-rk')].map(c=>c.dataset.aid)")
    ok(flagged == [c[0]], f'형광펜 1개 → .has-rk 카드 {flagged} == [{c[0]}]')
    # ② red2 = .k 전부
    await pg.evaluate("([ns])=>{localStorage.setItem(ns+'autoRule.OMS1',JSON.stringify({'DD1/learn':{kind:'red2',scope:'all',one:false,at:Date.now()}}));}", [NS])
    await openL(pg)
    nr2 = await pg.evaluate("document.querySelectorAll('#stage .rk-b[data-auto]').length"); k2all = await pg.evaluate("document.querySelectorAll('#stage .tc .k.k2').length")
    ok(nr2 >= nr and (k2all == 0 or nr2 > nr), f'규칙 red2 빈칸 {nr2} ≥ red {nr} (.k2 {k2all}개 포함)')
    await pg.screenshot(path=J.TMP + f'/ux2i_merge_rule_{tag}.png')
    # ⑤ dumpAll에 트랙 B 새 키
    await pg.evaluate("([ns])=>{localStorage.setItem(ns+'review','true');localStorage.setItem(ns+'figmode','\"small\"');localStorage.setItem(ns+'cover.OMS1.DD1/sum','{}');localStorage.setItem(ns+'sumdense','\"f\"');}", [NS])
    ks = await pg.evaluate("Object.keys(__h.dumpAll())")
    ok(all(NS + k in ks for k in ['review', 'figmode', 'cover.OMS1.DD1/sum', 'sumdense']), '백업 dumpAll에 review·figmode·cover.*·sumdense')
    await pg.evaluate("([ns])=>{['review','figmode','cover.OMS1.DD1/sum','sumdense'].forEach(k=>localStorage.removeItem(ns+k));}", [NS])
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()
async def summig(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('== sumMig 다시 옮김·합치기')
    await pg.goto(U + '#/'); await pg.wait_for_function('window.__h&&__h.PACKS.CONS', timeout=20000); await pg.evaluate("localStorage.clear()")
    # 새 정리표 글자에서 한 행에만 한 번 나오는 낱말 → 옛 표 전체 키로 넣음(플래그는 이미 1)
    w = await pg.evaluate("""(()=>{const d=document.createElement('div');d.style.display='none';d.innerHTML=__h.PACKS.CONS.lect.find(L=>L.k==='WHT').sum;document.body.appendChild(d);
      const W=[...d.querySelectorAll('[data-alt]')].find(e=>e.dataset.alt.split(' ').includes('CONS:WHT:sum'));const T=__h.Kit.textOf(W)||'';
      let v='';const SK=__h.Kit.skipSel,tw=document.createTreeWalker(W,NodeFilter.SHOW_TEXT);let n;while(n=tw.nextNode()){const p=n.parentElement;if(!p||p.closest(SK))continue;v+=n.nodeValue;}
      const ws=v.split(/[^A-Za-z]+/).filter(x=>x.length>=7&&v.split(x).length===2);d.remove();return ws[0]||null;})()""")
    ok(bool(w), f'옛 표 글자에서 한 번만 나오는 낱말 {w!r}')
    await pg.evaluate("([ns,w])=>{localStorage.setItem(ns+'sumMig.CONS','1');localStorage.setItem(ns+'ann.CONS',JSON.stringify({'CONS:WHT:sum':[{t:'h',x:w,i:0,c:'y'}]}));}", [NS, w])
    await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/sum'); await pg.wait_for_function("document.querySelector('#stage table.mtx')", timeout=20000)
    await pg.wait_for_function(f"!Object.keys(JSON.parse(localStorage.getItem('{NS}ann.CONS')||'{{}}')).includes('CONS:WHT:sum')", timeout=8000)
    a = json.loads(await pg.evaluate(f"localStorage.getItem('{NS}ann.CONS')"))
    ok(any(k.endswith('~s') and any(o.get('x') == w for o in L) for k, L in a.items()), f'플래그가 있어도 옛 :sum 표시 → 행 aid로 옮김 {list(a)}')
    drawn = await pg.evaluate("[...document.querySelectorAll('#stage tr[data-aid] [data-rk]')].map(e=>e.textContent).join('')")
    ok(w in drawn, '옮긴 표시가 정리표 행에 칠해짐')
    await pg.evaluate(f"localStorage.removeItem('{NS}sumMig.GERI')")
    await pg.evaluate(f"__h.mergeData({{'{NS}sumMig.GERI':'1','{NS}review':'true'}})")
    ok(await pg.evaluate(f"localStorage.getItem('{NS}sumMig.GERI')") is None, '합치기는 sumMig 플래그를 가져오지 않음')
    ok(await pg.evaluate(f"localStorage.getItem('{NS}review')") == 'true', '합치기는 다른 새 키(review)는 가져옴')
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await flow(b, {'width': 1280, 'height': 900}, False, 'mac')
        await flow(b, {'width': 820, 'height': 1180}, True, 'ipad_p')
        await flow(b, {'width': 1180, 'height': 820}, True, 'ipad_l')
        await summig(b)
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
    _sys.exit(1 if fails else 0)
asyncio.run(main())
