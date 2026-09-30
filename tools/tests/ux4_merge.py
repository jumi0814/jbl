"""ux4 묶음 1 × 묶음 2 병합 계약 — 1280×900 · 1180×820(터치) · 820×1180(터치)
두 묶음이 겹치는 곳만 본다(각 묶음 자체는 ux4_kit·ux4_focus·ux4_clear·ux4_remove·ux4_bugs / ux4_nav·ux4_top).
① 과목 학습: 과목 메뉴(#nav[data-mode=subj]) · 빵부스러기 과목(.cbs) · [✎ 도구]·[⤢ 집중]이 탭 줄에 하나씩 · 도구 막대 가운데 = 메뉴를 뺀 본문 가운데
② V(집중): #top·#side 숨김 · 탭 줄 top 0 · .fclock = 알약 글자(오늘 합계 · 상태) · 쉬는 중이면 '☕ 휴식 m:ss · 공부 h:mm:ss'이고 1초마다 흐름
③ 집중 중 / = 상단 막대가 잠깐 내려오고 검색칸 placeholder = '<과목>에서 검색' · blur면 다시 숨김
④ 집중 중 M = 집중 끔 + 메뉴(>860 펼침 · ≤860 서랍 + html.navlock) · 집중 끝 뒤 과목 메뉴 그대로
⑤ T = 도구 막대 토글(LS kitoff) — 집중·메뉴 숨김과 따로 · 허브 홈(허브 메뉴)에서는 T 무시
⑥ 한 탭 문서(JB): 평소 hero 오른쪽 .dhk [✎ 도구][⤢ 집중] · 집중이면 #dtabs.dsolo(문서 이름 + 버튼) · 알약을 누르면 팝오버(#tpop [data-tp])
콘솔 오류 0 · 스크린샷 work/_tmp/ux4i_merge_<폭>_<장면>.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
KEY = lambda k, code: f"document.dispatchEvent(new KeyboardEvent('keydown',{{key:'{k}',code:'{code}',bubbles:true}}))"
KV, KM, KT = KEY('ㅍ', 'KeyV'), KEY('ㅡ', 'KeyM'), KEY('ㅅ', 'KeyT')
ST = """(()=>{const q=s=>document.querySelector(s),vis=e=>!!e&&e.offsetParent!==null&&getComputedStyle(e).display!=='none'&&e.getBoundingClientRect().width>0;
 const B=document.body.classList,k=q('#kit'),kr=k.getBoundingClientRect(),dt=q('#dtabs'),sw=parseFloat(getComputedStyle(document.body).getPropertyValue('--sidew'))||0,W=document.documentElement.clientWidth;
 const fc=[...document.querySelectorAll('.fclock')].find(vis),c=q('#clock');
 return {mode:q('#nav').dataset.mode,cbs:!!q('#crumb .cbs'),fo:B.contains('focus'),kitoff:B.contains('kit-off'),top:getComputedStyle(q('#top')).display,side:vis(q('#side'))&&q('#side').getBoundingClientRect().right>4,
  dt:vis(dt)?Math.round(dt.getBoundingClientRect().top):null,kv:getComputedStyle(k).display!=='none'&&getComputedStyle(k).visibility!=='hidden'&&kr.width>0,kc:Math.round((kr.left+kr.right)/2),bc:Math.round(sw+(W-sw)/2),W,sw,
  kitt:[...document.querySelectorAll('[data-kitt]')].filter(vis).length,dfoc:[...document.querySelectorAll('.dfoc')].filter(vis).length,
  fc:fc?fc.textContent:null,ckt:(c.querySelector('.ckt')||{}).textContent,ckl:(c.querySelector('.ckl')||{}).textContent,st:c.dataset.st,
  navopen:B.contains('navopen'),lock:document.documentElement.classList.contains('navlock'),fold:B.contains('sidefold'),
  solo:vis(q('#dtabs.dsolo'))?q('#dtabs .dtone')&&q('#dtabs .dtone').textContent:null,dhk:[...document.querySelectorAll('.hero .dhk button')].filter(vis).length,
  ph:q('#gsearch').placeholder,lsKit:localStorage.getItem('jblhub.v1.kitoff')}})()"""
async def run(b, tag, vp, touch):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
    nar = vp['width'] <= 860
    await pg.goto(U + '#/'); await pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.tauto','false');localStorage.setItem('jblhub.v1.whatsNew.4',1)")
    shot = lambda n: pg.screenshot(path=J.TMP + f'/ux4i_merge_{tag}_{n}.png')
    # ① 과목 학습
    await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/learn'); await pg.wait_for_selector('#stage .tc', timeout=30000); await pg.wait_for_timeout(800)
    await pg.evaluate("scrollTo(0,400)"); await pg.wait_for_timeout(300)
    r = await pg.evaluate(ST)
    ok(r['mode'] == 'subj' and r['cbs'] and r['top'] != 'none', f'{tag} ① 과목 메뉴·빵부스러기 과목 {r["mode"]} {r["cbs"]}')
    ok(r['kitt'] == 1 and r['dfoc'] == 1, f'{tag} ① 탭 줄 [✎ 도구] {r["kitt"]} · [⤢ 집중] {r["dfoc"]} 하나씩')
    ok(r['kv'] and abs(r['kc'] - r['bc']) <= 2, f'{tag} ① 도구 막대 가운데 {r["kc"]} = 본문 가운데 {r["bc"]} (메뉴 {r["sw"]})')
    await shot('learn')
    # ② V → 집중 · 시계 따라감
    await pg.evaluate(KV); await pg.wait_for_timeout(700); r = await pg.evaluate(ST)
    ok(r['fo'] and r['top'] == 'none' and not r['side'] and r['dt'] == 0, f'{tag} ② 집중: 상단·메뉴 숨김·탭 줄 top {r["dt"]}')
    ok(r['fc'] is not None and r['ckt'] in r['fc'], f'{tag} ② .fclock = 알약 오늘 합계 ({r["fc"]!r} ⊃ {r["ckt"]!r})')
    ok(r['kv'] and abs(r['kc'] - r['W'] / 2) <= 2, f'{tag} ② 집중 중 도구 막대 화면 가운데 {r["kc"]}/{r["W"] / 2}')
    await pg.evaluate("__h.trStart()"); await pg.wait_for_timeout(1200); await pg.evaluate("__h.trRest()"); await pg.wait_for_timeout(1300)
    f1 = await pg.evaluate(ST); await pg.wait_for_timeout(2200); f2 = await pg.evaluate(ST)
    ok(f1['st'] == 'rest' and (f1['fc'] or '').startswith('☕ 휴식 ') and ' · 공부 ' in (f1['fc'] or ''), f'{tag} ② 쉬는 중 .fclock {f1["fc"]!r}')
    ok(f1['fc'] != f2['fc'] and re.search(r'휴식 \d+:\d\d', f2['fc'] or ''), f'{tag} ② 휴식 m:ss가 흐름 {f1["fc"]!r} → {f2["fc"]!r}')
    await shot('focus_rest')
    await pg.evaluate("__h.trStop()"); await pg.wait_for_timeout(300)
    # ③ 집중 중 / 검색
    await pg.evaluate(KEY('/', 'Slash')); await pg.wait_for_timeout(400); r = await pg.evaluate(ST)
    ok(r['fo'] and r['top'] != 'none' and r['ph'] == '과목 검색' and r['ph'] != '전체 검색', f'{tag} ③ 집중 중 / → 상단 막대·과목 안 검색 {r["top"]} {r["ph"]!r}')
    ok(await pg.evaluate("document.activeElement&&document.activeElement.id==='gsearch'"), f'{tag} ③ 검색칸 포커스')
    await shot('focus_search')
    await pg.evaluate("document.activeElement.blur()"); await pg.wait_for_timeout(300); r = await pg.evaluate(ST)
    ok(r['fo'] and r['top'] == 'none', f'{tag} ③ blur → 상단 막대 다시 숨김 {r["top"]}')
    # ④ 집중 중 M
    await pg.evaluate(KM); await pg.wait_for_timeout(700); r = await pg.evaluate(ST)
    if nar: ok(not r['fo'] and r['navopen'] and r['lock'] and r['mode'] == 'subj', f'{tag} ④ 집중 중 M → 집중 끔 + 서랍(과목 메뉴)·navlock {r["navopen"]} {r["lock"]}')
    else: ok(not r['fo'] and r['side'] and not r['fold'] and r['mode'] == 'subj', f'{tag} ④ 집중 중 M → 집중 끔 + 메뉴 펼침 {r["side"]} fold={r["fold"]}')
    await shot('focus_M')
    if nar:
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400); r = await pg.evaluate(ST)
        ok(not r['navopen'] and not r['lock'], f'{tag} ④ Esc → 서랍 닫힘·잠금 풀림')
    # ⑤ T 토글 — 집중과 따로 · 허브 홈에서는 무시
    await pg.evaluate(KT); await pg.wait_for_timeout(300); r = await pg.evaluate(ST)
    ok(r['kitoff'] and not r['kv'] and r['lsKit'] == 'true' and not r['fo'], f'{tag} ⑤ T → 도구 막대 끔(LS kitoff) {r["lsKit"]}')
    await pg.evaluate(KV); await pg.wait_for_timeout(600); r = await pg.evaluate(ST)
    ok(r['fo'] and r['kitoff'] and not r['kv'], f'{tag} ⑤ 집중을 켜도 도구 막대 꺼진 채')
    await pg.evaluate(KT); await pg.wait_for_timeout(300); r = await pg.evaluate(ST)
    ok(r['fo'] and not r['kitoff'] and r['kv'], f'{tag} ⑤ 집중 중 T → 도구 막대 켬(집중 그대로)')
    await pg.evaluate(KV); await pg.wait_for_timeout(500)
    await pg.goto(U + '#/'); await pg.wait_for_timeout(900)
    r0 = await pg.evaluate(ST); await pg.evaluate(KT); await pg.wait_for_timeout(300); r = await pg.evaluate(ST)
    ok(r['mode'] == 'hub' and r['kitoff'] == r0['kitoff'] and not r['kv'], f'{tag} ⑤ 허브 홈(허브 메뉴)에서 T 무시 {r["mode"]}')
    # ⑥ 한 탭 문서 JB
    await pg.goto('about:blank'); await pg.goto(U + '#/CONS/_jb/_jb'); await pg.wait_for_selector('#cards .qc', timeout=30000); await pg.wait_for_timeout(800)
    r = await pg.evaluate(ST)
    ok(r['mode'] == 'subj' and r['dhk'] == 2 and r['solo'] is None, f'{tag} ⑥ JB 평소: hero .dhk 버튼 {r["dhk"]} · dsolo 숨김')
    await pg.evaluate(KV); await pg.wait_for_timeout(700); r = await pg.evaluate(ST)
    ok(r['fo'] and r['solo'] and 'JB' in r['solo'] and r['dt'] == 0 and r['fc'] is not None, f'{tag} ⑥ JB 집중: #dtabs.dsolo {r["solo"]!r} top {r["dt"]} · 시계 {r["fc"]!r}')
    await shot('jb_focus')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
    await (pg.tap('#clock') if touch else pg.click('#clock')); await pg.wait_for_timeout(400)
    tp = await pg.evaluate("[document.querySelector('#tpop').classList.contains('on')||getComputedStyle(document.querySelector('#tpop')).display!=='none',[...document.querySelectorAll('#tpop [data-tp]')].map(b=>b.dataset.tp)]")
    ok(tp[0] and 'start' in tp[1] and 'big' in tp[1], f'{tag} ⑥ 알약 → 팝오버 {tp}')
    await shot('jb_clock')
    ok(not errs, f'{tag} 콘솔 오류 0 {errs[:3]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        try:
            for tag, vp, t in [('1280', {'width': 1280, 'height': 900}, False), ('1180', {'width': 1180, 'height': 820}, True), ('820', {'width': 820, 'height': 1180}, True)]:
                await run(b, tag, vp, t)
        finally: await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
