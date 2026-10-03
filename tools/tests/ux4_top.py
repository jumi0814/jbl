"""ux4 묶음 2 회귀 — 상단 막대(B2-3)·공부 시계 알약(B2-4).
B2-3 밝은 상단 막대 52px(종이 바탕 · 선 하나 · 크롬 이모지 0 · 가로 넘침 0) · 빵부스러기 글자(홈 'JBL / 오늘' · 과목 홈 'JBL / 임상치과보존학' · 강의 'JBL / 임상치과보존학 / Tooth whitening' · JB · 달력 · 검색)
     · 'JBL' → 허브 홈 · 과목 이름 → 과목 홈 · 글자 대비 ≥4.5 · 과목 안 '/' → 검색 칸(‘보존에서 검색’) · 결과 = 그 과목만 → [전체로 넓히기] → 모든 과목 · 허브에서는 전체
B2-4 시계 알약 하나(#tmr·⏸ 자리 비움 칩·⤢·🏠 글자 없음 · 메뉴·홈에 트래커 ⏱ 없음) · 상태 점(대기 회색 · 공부 중 과목색 · 휴식 금색) + 오늘 h:mm:ss + '공부 중/휴식 m:ss/대기'
     · 쉬는 중 '휴식 m:ss'가 1초마다 흐름 · 알약을 눌러도 측정이 저절로 시작되지 않음 · 팝오버 [■ 멈춤][☕ 쉬기][⏱ 크게 보기][공부 달력][하루 목표·측정 설정] · 화면 안에 뜸
맥 1280×900 · 아이패드 가로 1180×820·세로 820×1180(터치). 스크린샷 work/_tmp/ux4i_top_*.png"""
import os as _os, sys as _sys, re; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, wait=350):
    await pg.goto('about:blank'); await pg.goto(U + h)
    await pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')", timeout=30000); await pg.wait_for_timeout(wait)
CRUMB = "[...document.querySelector('#crumb').children].filter(e=>!e.classList.contains('sl')).map(e=>e.textContent.trim()).join(' / ')"
LUM = """(c)=>{const m=c.match(/[\\d.]+/g).map(Number);const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(m[0])+.7152*f(m[1])+.0722*f(m[2]);}"""
CK = "(c=>({st:c.dataset.st,t:c.querySelector('.ckt').textContent,l:c.querySelector('.ckl').textContent,dot:getComputedStyle(c.querySelector('.ckd')).backgroundColor}))(document.querySelector('#clock'))"
def rgb(h): h = h.lstrip('#'); return 'rgb(%d, %d, %d)' % tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    print('==', tag); W = vp['width']; narrow = W <= 860
    tap = (lambda s: pg.tap(s)) if touch else (lambda s: pg.click(s))
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await open_(pg, '#/')
    # ---- B2-3 막대 모양 · 빵부스러기
    want = [('#/', 'JBL / 오늘'), ('#/CONS/_home/_home', 'JBL / 임상치과보존학'), ('#/CONS/WHT/learn', 'JBL / 임상치과보존학 / Tooth whitening'), ('#/CONS/_jb/_jb', 'JBL / 임상치과보존학 / JB 문제'),
            ('#/CONS/_sum/_sum', 'JBL / 임상치과보존학 / 기출 한눈표'), ('#/_cal', 'JBL / 공부 달력'), ('#/?q=%ED%86%B5%EC%A6%9D', 'JBL / 검색')]
    for h, w in want:
        await open_(pg, h); c = await pg.evaluate(CRUMB)
        t = await pg.evaluate(f"""(()=>{{const t=document.querySelector('#top'),r=t.getBoundingClientRect(),cs=getComputedStyle(t),L={LUM},cur=document.querySelector('#crumb .ccur'),fg=getComputedStyle(cur).color,sl=getComputedStyle(document.querySelector('#crumb #gohome')).color;
          const bg=cs.backgroundColor,cr=(a,b)=>{{const x=L(a),y=L(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}};
          return {{h:Math.round(r.height),bg,ovx:t.scrollWidth-t.clientWidth,emo:/\\p{{Extended_Pictographic}}/u.test(t.innerText.replace(/[☰✎★]/g,'')),c1:Math.round(cr(fg,bg)*10)/10,c2:Math.round(cr(sl,bg)*10)/10,cut:cur.scrollWidth>cur.clientWidth+1}}}})()""")
        ok(c == w, f'{tag} {h} 빵부스러기 {c!r} = {w!r}')
        ok(52 <= t['h'] <= 53 and t['bg'] == 'rgb(247, 245, 240)' and t['ovx'] <= 0 and not t['emo'] and t['c1'] >= 4.5 and t['c2'] >= 4.5, f'{tag} {h} 상단 막대 {t}')
        if h in ('#/', '#/CONS/WHT/learn'): await pg.screenshot(path=J.TMP + f'/ux4i_top_{tag}_{h.strip("#/").replace("/", "_") or "home"}.png', clip={'x': 0, 'y': 0, 'width': W, 'height': 60})
    ok(await pg.evaluate("!document.querySelector('#tmr,#idlechip,#focusb,#sideopen,#top .brand')"), f'{tag} 옛 #tmr·자리 비움 칩·⤢·🏠 글자·› 없음')
    await open_(pg, '#/CONS/WHT/learn'); await pg.evaluate("document.querySelector('#crumb .cbs').click()"); await pg.wait_for_timeout(700)
    ok((await pg.evaluate('location.hash')).startswith('#/CONS/_home'), f'{tag} 과목 이름 → 과목 홈')
    await tap('#gohome'); await pg.wait_for_timeout(700)
    ok(await pg.evaluate("location.hash") in ('#/', '') and await pg.evaluate("document.querySelector('#nav').dataset.mode") == 'hub', f"{tag} 'JBL' → 허브 홈·허브 메뉴")
    # ---- 검색 범위
    await open_(pg, '#/CONS/WHT/learn', 1500)
    await pg.keyboard.press('Slash'); await pg.wait_for_timeout(150)
    r = await pg.evaluate("[document.activeElement&&document.activeElement.id,document.querySelector('#gsearch').placeholder]")
    ok(r == ['gsearch', '과목 검색'], f"{tag} 과목 안 '/' → 검색 칸 '과목 검색' {r}")
    await pg.keyboard.type('통증'); await pg.wait_for_timeout(2500)
    r = await pg.evaluate("[location.hash,[...new Set([...document.querySelectorAll('#home .sres')].map(x=>x.dataset.s))],!!document.querySelector('#home [data-swide]'),document.querySelector('#nav').dataset.mode,document.querySelector('#gsearch').placeholder]")
    ok('&s=CONS' in r[0] and r[1] == ['CONS'] and r[2] and r[3] == 'subj' and r[4] == '과목 검색', f'{tag} 결과 = 보존만 · [전체로 넓히기] · 과목 메뉴(ux4c 2회차 navS) {r}')
    await pg.evaluate("document.querySelector('#home [data-swide]').click()"); await pg.wait_for_timeout(2500)
    r = await pg.evaluate("[location.hash,[...new Set([...document.querySelectorAll('#home .sres')].map(x=>x.dataset.s))].length,document.querySelector('#gsearch').placeholder]")
    ok('&s=' not in r[0] and r[1] >= 3 and r[2] == '전체 검색', f'{tag} 전체로 넓히기 → 여러 과목 {r}')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
    await open_(pg, '#/', 1500); await pg.keyboard.press('Slash'); await pg.keyboard.type('통증'); await pg.wait_for_timeout(2500)
    r = await pg.evaluate("[location.hash,[...new Set([...document.querySelectorAll('#home .sres')].map(x=>x.dataset.s))].length]")
    ok('&s=' not in r[0] and r[1] >= 3, f'{tag} 허브에서 검색 = 전체 {r}')
    # ---- B2-4 시계 알약
    await open_(pg, '#/'); ck = await pg.evaluate(CK)
    ok(ck['st'] in ('wait', 'off') and ck['l'] == '대기' and re.fullmatch(r'\d+:\d\d:\d\d', ck['t']) and ck['dot'] == 'rgb(185, 178, 166)', f'{tag} 허브 홈 알약 = 대기·회색 점 {ck}')
    ok(await pg.evaluate("!document.querySelector('#side [data-trb],#side [data-trk],#home [data-trb=big]')"), f'{tag} 메뉴 트래커·홈 ⏱ 크게 없음')
    await tap('#clock'); await pg.wait_for_timeout(250)
    ok(await pg.evaluate("document.querySelector('#clock').dataset.st") in ('wait', 'off'), f'{tag} 알약을 눌러도 측정이 저절로 시작되지 않음')
    p = await pg.evaluate("(()=>{const p=document.querySelector('#tpop'),r=p.getBoundingClientRect();return {on:p.classList.contains('on'),rows:[...p.querySelectorAll('[data-tp]')].map(b=>b.dataset.tp),l:Math.round(r.left),r:Math.round(r.right),t:Math.round(r.top),ck:Math.round(document.querySelector('#clock').getBoundingClientRect().bottom),txt:p.innerText}})()")
    ok(p['on'] and p['rows'] == ['start', 'big', 'cal', 'goal'] and p['l'] >= 0 and p['r'] <= W and p['t'] >= p['ck'], f'{tag} 대기 팝오버 [▶ 시작][⏱ 크게][달력][목표] · 화면 안 {p["rows"]} {p["l"]}~{p["r"]}')
    ok('오늘' in p['txt'] and '/ 4:00' in p['txt'] and '휴식' in p['txt'], f"{tag} 팝오버 머리 '오늘 h:mm / 목표 · 휴식' {p['txt'][:40]!r}")
    await pg.screenshot(path=J.TMP + f'/ux4i_top_{tag}_pop_wait.png')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(150)
    await open_(pg, '#/CONS/WHT/learn'); await pg.mouse.move(400, 500); await pg.mouse.move(420, 520); await pg.wait_for_timeout(1300)
    ck = await pg.evaluate(CK); col = await pg.evaluate("__h.sjColor('CONS')")
    ok(ck['st'] == 'run' and ck['l'].startswith('공부 ') and ck['dot'] == rgb(col), f'{tag} 과목에서 움직이면 공부 중·과목색 점 {ck} {col}')
    await tap('#clock'); await pg.wait_for_timeout(250)
    rows = await pg.evaluate("[...document.querySelectorAll('#tpop [data-tp]')].map(b=>b.dataset.tp)")
    ok(rows == ['stop', 'rest', 'big', 'cal', 'goal'], f'{tag} 공부 중 팝오버 [■ 멈춤][☕ 쉬기]… {rows}')
    await tap('#tpop [data-tp=rest]'); await pg.wait_for_timeout(1200)
    a = await pg.evaluate(CK); await pg.wait_for_timeout(2100); b2 = await pg.evaluate(CK)
    ok(a['st'] == 'rest' and a['dot'] == 'rgb(183, 121, 31)' and re.fullmatch(r'휴식 \d+:\d\d', a['l']) and b2['l'] != a['l'] and b2['t'] == a['t'], f'{tag} ☕ → 휴식 금색 점 · 휴식 타이머가 흐름({a["l"]} → {b2["l"]}) · 공부 합계는 멈춤')
    await tap('#clock'); await pg.wait_for_timeout(1300)
    r = await pg.evaluate("[[...document.querySelectorAll('#tpop [data-tp]')].map(b=>b.dataset.tp),(document.querySelector('#tpop [data-tpt=rest]')||{}).textContent]")
    ok(r[0] == ['resume', 'stop', 'big', 'cal', 'goal'] and r[1] and r[1].startswith('지금 휴식'), f'{tag} 쉬는 중 팝오버 [▶ 다시 공부 · 휴식 m:ss] {r}')
    await pg.screenshot(path=J.TMP + f'/ux4i_top_{tag}_pop_rest.png')
    await tap('#tpop [data-tp=big]'); await pg.wait_for_timeout(1200)
    r = await pg.evaluate("[document.querySelector('#bigclock').classList.contains('on'),document.querySelector('#bigclock').classList.contains('rest'),document.querySelector('#tpop').classList.contains('on')]")
    ok(r == [True, True, False], f'{tag} ⏱ 크게 보기 → 크게(휴식)·팝오버 닫힘 {r}')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
    await tap('#clock'); await pg.wait_for_timeout(200); await tap('#tpop [data-tp=resume]'); await pg.wait_for_timeout(500)
    ok((await pg.evaluate(CK))['st'] == 'run', f'{tag} ▶ 다시 공부 → 공부 중')
    await tap('#clock'); await pg.wait_for_timeout(200); await tap('#tpop [data-tp=stop]'); await pg.wait_for_timeout(400)
    ck = await pg.evaluate(CK); ok(ck['st'] == 'end' and ck['l'] == '멈춤' and ck['dot'] == 'rgb(185, 178, 166)', f'{tag} ■ 공부 멈춤 → 멈춤·회색 {ck}')
    await tap('#clock'); await pg.wait_for_timeout(200); await tap('#tpop [data-tp=goal]'); await pg.wait_for_timeout(800)
    ok(await pg.evaluate("location.hash.indexOf('#/_cal')===0&&!!document.querySelector('#calmset')&&document.querySelector('#calmset').open"), f'{tag} 하루 목표·측정 설정 → 📅 달력 측정 설정 펼침')
    await tap('#clock'); await pg.wait_for_timeout(200); await tap('#tpop [data-tp=start]'); await pg.wait_for_timeout(400)
    ck = await pg.evaluate(CK); ok(ck['st'] == 'sess' and ck['l'].startswith('세션 '), f'{tag} ▶ 공부 시작 → 세션 {ck}')
    await pg.evaluate("__h.trStop()"); await pg.wait_for_timeout(200)
    ok(not errs, f'{tag} 콘솔·페이지 오류 0 {errs[:3]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 1180, 'height': 820}, True, 'land')
        await run(b, {'width': 820, 'height': 1180}, True, 'port')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
