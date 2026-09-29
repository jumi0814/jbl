"""ux4 B1-4·B1-5·B1-6 요청으로 뺀 것 — 1280×900 · 1180×820(터치) · 820×1180(터치)
B1-6 LS exam.CONS='2026-10-20'·homeSort='exam'·done.CONS를 미리 넣어도 허브 홈·과목 홈·강의·달력 화면 글자(innerText)에 '시험일'·'D-'·'시험순'·'읽음'·'n%' 0건,
     값은 그대로 · 카드 끝 '✓ 다 봄' → LS done.CONS에 aid 기록(머리 ✓ 원은 숨김) · 과목 표 순서 = 기본
B1-5 CONS WHT 학습·R 복습 보기에서 .mj 0개·⚡ 줄 바탕 없음 · ⚡ '가리기'로 .c-mem.memhide 토글 · 플래시카드 채점·LS fc.CONS(R: 키) 전후 그대로
B1-4 H → 버튼 눌림만('켜짐' 글자·칩·안내 없음) · ▾ 색 팝오버 5색 → 다음 형광 색 · 콘솔 오류 0"""
import os as _os, sys as _sys, re; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
BAD = re.compile(r'시험일|D-\d|D-day|시험순|읽음')
PCT = re.compile(r'\d+\s?%')
TXT = "(()=>{const a=[...document.querySelectorAll('#home:not([hidden]),#hero,#dtabs,#stage,#nav')].filter(e=>e.offsetParent||e.id==='nav').map(e=>e.innerText).join('\\n');return a})()"
# 진행 막대 % 글자가 있던 크롬(메뉴 과목 줄·오늘 띠·과목 표·강의 바로가기·강의 카드·다음 할 일·미니바·달력 그 날 머리) — 본문(원고)의 %는 제외
PTX = "(()=>[...document.querySelectorAll('#nav .nvs,#home .hband,#home .hsj,#stage .ljump,#stage .lcard,#stage #nextp,#lmini,#home .cdh')].filter(e=>e.offsetParent).map(e=>e.innerText).join('\\n'))()"
async def run(b, tag, vp, touch):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
    await pg.goto(U + '#/'); await pg.evaluate("""localStorage.clear();const S=(k,v)=>localStorage.setItem('jblhub.v1.'+k,JSON.stringify(v));S('tauto',false);S('exam.CONS','2026-10-20');S('exam.PHARM','2026-10-05');S('homeSort','exam');S('whatsNew.3',1);
      S('fc.CONS',{'R:WHT:zzz':{s:'x',t:1},'V:abc':{s:'o',t:2}});""")
    keep0 = await pg.evaluate("['exam.CONS','exam.PHARM','homeSort','fc.CONS'].map(k=>localStorage.getItem('jblhub.v1.'+k))")
    for name, h, sel in [('home', '#/', '#home .hsj'), ('subj', '#/CONS/_home/_home', '#stage .lcard'), ('learn', '#/CONS/WHT/learn', '#stage .tc'), ('cal', '#/_cal', '#calg')]:
        await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_selector(sel, timeout=30000); await pg.wait_for_timeout(900)
        if name == 'cal':
            await pg.evaluate("document.querySelector('#calg [data-cd]').click()"); await pg.wait_for_timeout(300)
        t = await pg.evaluate(TXT); hits = sorted(set(m.group(0) for m in BAD.finditer(t)) | set(m.group(0) for m in PCT.finditer(await pg.evaluate(PTX))))
        ok(not hits, f'{tag} {name}: 시험일·D-·시험순·읽음·진행 % 글자 0 {hits[:6]} {[t[max(0,m.start()-20):m.end()+10] for m in BAD.finditer(t)][:2]}')
        if name == 'home':
            o = await pg.evaluate("[...document.querySelectorAll('#home .hsj[data-s]')].map(e=>e.dataset.s)")
            ok(o[:3] == ['OMS1', 'CONS', 'IMPL'], f'{tag} 과목 표 순서 = 기본(시험순 없음) {o[:3]}')
            await pg.screenshot(path=J.TMP + f'/ux4i_home_{tag}.png')
    ok(await pg.evaluate("['exam.CONS','exam.PHARM','homeSort','fc.CONS'].map(k=>localStorage.getItem('jblhub.v1.'+k))") == keep0, f'{tag} LS exam.·homeSort·fc 값 그대로')
    # ✓ 다 봄
    await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/learn'); await pg.wait_for_selector('#stage .tc', timeout=30000); await pg.wait_for_timeout(700)
    r = await pg.evaluate("(()=>{const c=document.querySelector('#t-WHT-1');const h=c.querySelector('.thead .dn'),e=c.querySelector('.dnend');e.scrollIntoView({block:'center'});return [getComputedStyle(h).display,!!e.offsetParent,e.textContent,c.dataset.aid]})()")
    await (pg.tap('#t-WHT-1 .dnend') if touch else pg.click('#t-WHT-1 .dnend')); await pg.wait_for_timeout(200)
    dn = await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.done.CONS')||'{}')")
    ok(r[0] == 'none' and r[1] and r[2] == '✓ 다 봄' and dn.get(r[3]) == 1 and await pg.evaluate("document.querySelector('#t-WHT-1').classList.contains('done')"), f'{tag} 카드 끝 ✓ 다 봄 → LS done.CONS[{r[3]}] (머리 ✓ 숨김) {r[:3]}')
    await (pg.tap('#t-WHT-1 .dnend') if touch else pg.click('#t-WHT-1 .dnend')); await pg.wait_for_timeout(200)
    ok(r[3] not in await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.done.CONS')||'{}')"), f'{tag} 다시 누르면 취소')
    # B1-5 ⚡ ○✕ 없음
    m = await pg.evaluate("(()=>{const L=[...document.querySelectorAll('#stage .c-mem li')];return [document.querySelectorAll('#stage .mj,#stage [data-mj]').length,L.length,L.filter(li=>{const b=getComputedStyle(li).backgroundColor;return b!=='rgba(0, 0, 0, 0)'&&b!=='transparent'}).length]})()")
    ok(m[0] == 0 and m[1] > 0 and m[2] == 0, f'{tag} 학습: .mj 0 · ⚡ 줄 {m[1]}개 바탕색 {m[2]}')
    q = await pg.evaluate("(()=>{const b=document.querySelector('#stage .c-mem [data-memqz]');b.scrollIntoView({block:'center'});b.id='ux4mq';return getComputedStyle(b).borderStyle})()")
    await (pg.tap('#ux4mq') if touch else pg.click('#ux4mq')); await pg.wait_for_timeout(150)
    on = await pg.evaluate("document.querySelector('#ux4mq').closest('.c-mem').classList.contains('memhide')")
    await (pg.tap('#ux4mq') if touch else pg.click('#ux4mq')); await pg.wait_for_timeout(150)
    off = not await pg.evaluate("document.querySelector('#ux4mq').closest('.c-mem').classList.contains('memhide')")
    ok(on and off and q == 'none', f'{tag} ⚡ 가리기(글자 링크) → memhide 켜고 끔 {on} {off} 테두리 {q}')
    await pg.keyboard.press('r'); await pg.wait_for_timeout(500)
    m = await pg.evaluate("[document.querySelector('#stage').classList.contains('review'),document.querySelectorAll('#stage .mj').length,[...document.querySelectorAll('#stage .tc .rvj button')].filter(b=>b.offsetParent).length]")
    ok(m[0] and m[1] == 0 and m[2] > 0, f'{tag} R 복습 보기: .mj 0 · 카드 단위 알아요/몰라요는 그대로 {m}')
    await pg.keyboard.press('r'); await pg.wait_for_timeout(300)
    # 플래시카드 채점 → fc 기록(R: 키 보존)
    await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/flash'); await pg.wait_for_selector('#fc', timeout=30000); await pg.wait_for_timeout(700)
    await pg.keyboard.press('Space'); await pg.wait_for_timeout(200); await pg.keyboard.press('o'); await pg.wait_for_timeout(300)
    fc = await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.fc.CONS')||'{}')")
    ok(fc.get('R:WHT:zzz') == {'s': 'x', 't': 1} and fc.get('V:abc') == {'s': 'o', 't': 2} and len(fc) >= 3, f'{tag} 플래시카드 채점 기록 늘고 옛 R:·V: 키 그대로 ({len(fc)}개)')
    # B1-4 H → 눌림만 · ▾ 색
    await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/learn'); await pg.wait_for_selector('#stage .tc', timeout=30000); await pg.wait_for_timeout(700)
    await pg.keyboard.press('h'); await pg.wait_for_timeout(300)
    r = await pg.evaluate("[document.querySelector('#k-h').classList.contains('on'),document.body.innerText.indexOf('켜짐'),document.querySelectorAll('.modechip,#modechip').length,getComputedStyle(document.querySelector('#stage .tc')).outlineStyle]")
    ok(r[0] and r[1] < 0 and r[2] == 0 and r[3] != 'dashed', f'{tag} H → 형광펜 버튼 눌림만(켜짐 글자 {r[1]} · 칩 {r[2]} · 점선 {r[3]})')
    await (pg.tap('#k-swc') if touch else pg.click('#k-swc')); await pg.wait_for_timeout(200)
    n5 = await pg.evaluate("[...document.querySelectorAll('#k-swl .sw')].filter(x=>x.offsetParent).length")
    await (pg.tap('#k-swl .sw[data-c=p]') if touch else pg.click('#k-swl .sw[data-c=p]')); await pg.wait_for_timeout(200)
    xy = await pg.evaluate("(()=>{const li=[...document.querySelectorAll('#t-WHT-2 li')].find(l=>l.offsetParent&&/[A-Za-z가-힣]{4}/.test(l.textContent));li.scrollIntoView({block:'center'});const w=document.createTreeWalker(li,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){const m=/[A-Za-z가-힣]{4,}/.exec(x.nodeValue);if(m&&!x.parentElement.closest('button,.noann')){const r=document.createRange();r.setStart(x,m.index+1);r.setEnd(x,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2];}}})()")
    await pg.mouse.click(xy[0], xy[1]); await pg.wait_for_timeout(200)
    ok(n5 == 5 and await pg.evaluate("document.querySelectorAll('#stage .rk-h.rk-p').length") >= 1, f'{tag} ▾ 색 팝오버 {n5}색 → 분홍 형광')
    await pg.keyboard.press('Escape')
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
