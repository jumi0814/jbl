"""ux4 묶음 2 회귀 — 메뉴 두 단계(B2-1·B2-2)·서랍/M(B2-5)·전환 규칙과 스크롤 기억(B2-6). ux3_nav.py를 대신함.
B2-1 홈·달력(?s 포함)·검색 = 허브 메뉴(과목 7줄 · '이 과목' 없음) / #/CONS/… = 과목 메뉴('‹ 허브 홈' · 과목 머리 '보존' · 이 과목 7 · 강의 7 · 다른 과목 줄 0)
     · aria-current · ESTH 준비 중 · 백업 → 백업 창·복원 · 1분 타이머 = 글자만 · revInfo 과목당 1회 · 채점 → 허브 메뉴 '오늘 복습' 즉시
B2-2 1280 학습 첫 화면 카드 목차 ≥10줄 · 스크롤로 카드 7 → 목차 7번 .on · 기출 카드 = 노란 점 · 과목 바꾸기 → IMPL 과목 홈 + 메뉴 색 IMPL · 820 줄 ≥40px
B2-5 820 ☰ → 300px 서랍(상단 막대 위부터 · 뒤 스크롤 잠금) · 강의 줄 → 이동+닫힘 · Esc·배경 닫힘 · 1180↔820 회전 · 1280·1180 M → 숨김·#main 왼쪽 0·☰ · 다시 M → 복원
     · 설정 하나(navfold — 학습에서 숨기면 허브 홈도 숨김) · 집중 모드(V)가 M 상태를 바꾸지 않음
B2-6 '‹ 허브 홈'·뒤로가기 → 허브 메뉴 스크롤 복원 · 과목을 바꾸면 메뉴 맨 위 · JB 📖 칩 → 강의 → ↩ 알약 → JB(과목 메뉴 그대로) · 달력 ?s=CONS → 허브 메뉴
맥 1280×900 · 아이패드 가로 1180×820·세로 820×1180(터치). 스크린샷 work/_tmp/ux4i_nav_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
ESTH_READY = _os.path.exists(_os.path.join(J.DOCS, 'packs', 'ESTH.js'))   # 심미치과학 팩이 생기면 '준비 중' 대신 정상
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, wait=350):
    await pg.goto('about:blank'); await pg.goto(U + h)
    await pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')", timeout=30000); await pg.wait_for_timeout(wait)
NAV = """(()=>{const n=document.querySelector('#nav'),s=document.querySelector('#side'),r=s.getBoundingClientRect(),cs=getComputedStyle(s);
 return {mode:n.dataset.mode,nvs:n.querySelectorAll('.nvs').length,grid:n.querySelectorAll('.nvgrid .nvd').length,lec:n.querySelectorAll('.nvl').length,back:!!n.querySelector('.nvback'),
  sj:(n.querySelector('.nvsjn')||{}).textContent||'',cur:[...n.querySelectorAll('[aria-current]')].filter(e=>!e.closest('.nvswp')).map(e=>e.dataset.nv||e.dataset.d||e.dataset.nvsj||''),vis:cs.visibility,w:Math.round(r.width),
  dbtn:n.querySelectorAll('.dbtn').length,ovx:document.documentElement.scrollWidth-innerWidth}})()"""
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    print('==', tag); W = vp['width']; narrow = W <= 860
    tap = (lambda s: pg.tap(s)) if touch else (lambda s: pg.click(s))
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await open_(pg, '#/')
    # ---- B2-1 화면마다 메뉴 모드 · aria-current
    views = [('#/', 'hub', ['home']), ('#/_cal', 'hub', ['cal']), ('#/_cal?s=CONS', 'hub', ['cal']), ('#/?q=%ED%86%B5%EC%A6%9D', 'hub', []),
             ('#/CONS/_home/_home', 'subj', ['_home']), ('#/CONS/WHT/learn', 'subj', ['WHT']), ('#/CONS/WHT/sum', 'subj', ['WHT']), ('#/CONS/_jb/_jb', 'subj', ['_jb']), ('#/CONS/_marks/_marks', 'subj', ['_marks'])]
    for h, mode, cur in views:
        await open_(pg, h, 500); r = await pg.evaluate(NAV)
        if mode == 'hub': good = r['mode'] == 'hub' and r['nvs'] == 7 and r['grid'] == 0 and not r['back'] and r['lec'] == 0
        else: good = r['mode'] == 'subj' and r['nvs'] == 0 and r['grid'] == 8 and r['back'] and '보존' in r['sj'] and r['lec'] == 7 and r['dbtn'] == 15   # ux4f O13 과목 메뉴에 ★ 북마크 카드(_cbm) — 8칸·버튼 15
        shown = (r['vis'] == 'hidden') if narrow else (r['vis'] == 'visible' and r['w'] == 256) or (h.endswith('/sum') and W <= 1440)
        ok(good and shown and r['ovx'] <= 0, f'{tag} {h}: {mode} 메뉴 {r}')
        ok(r['cur'] == cur, f'{tag} {h}: aria-current {r["cur"]} = {cur}')
        if h in ('#/', '#/CONS/WHT/learn'): await pg.screenshot(path=J.TMP + f'/ux4i_nav_{tag}_{h.strip("#/").replace("/", "_") or "home"}.png')
    await open_(pg, '#/'); es = await pg.evaluate("(()=>{const e=document.querySelector('#nav .nvs[data-s=ESTH] .nvsb');return e?[e.getAttribute('aria-disabled'),e.textContent]:null})()")
    if ESTH_READY: ok(es and es[0] != 'true' and '준비 중' not in es[1], f'{tag} ESTH 준비됨(누를 수 있음) {es}')
    else: ok(es and es[0] == 'true' and '준비 중' in es[1], f'{tag} ESTH 준비 중 aria-disabled {es}')
    nums = await pg.evaluate("[...document.querySelectorAll('#nav .nvs:not(.off) .nvsb')].map(b=>[b.dataset.nvs,+b.querySelector('.r').textContent,(__h.PACKS[b.dataset.nvs].stats.main!=null?__h.PACKS[b.dataset.nvs].stats.main:__h.PACKS[b.dataset.nvs].stats.cards)])")
    ok(len(nums) == (7 if ESTH_READY else 6) and all(a == c for _, a, c in nums), f'{tag} 과목 줄 숫자 = 현 교수 기출 수 {nums}')
    txt = await pg.evaluate("document.querySelector('#nav').innerText")
    ok('%' not in txt and 'D-' not in txt and '시험' not in txt and '읽음' not in txt and '▸' not in txt, f"{tag} 허브 메뉴에 읽음 %·시험일·▸ 없음")
    # 과목 줄 → 과목 홈 + 과목 메뉴(서랍이면 먼저 열기)
    if narrow: await tap('#navbtn'); await pg.wait_for_timeout(300)
    await tap('#nav .nvsb[data-nvs="ANAT"]'); await pg.wait_for_timeout(800)
    r = await pg.evaluate(NAV)
    ok((await pg.evaluate('location.hash')).startswith('#/ANAT/_home') and r['mode'] == 'subj' and '두경부' in r['sj'], f'{tag} 과목 줄 1탭 → ANAT 과목 홈·과목 메뉴 {r["sj"]}')
    # ---- 백업 창 · 복원
    if narrow: await tap('#navbtn'); await pg.wait_for_timeout(300)
    await pg.evaluate("document.querySelector('#bkup').click()"); await pg.wait_for_timeout(250)
    ok(await pg.evaluate("document.querySelector('#bkpop').classList.contains('on') && !!document.querySelector('#bkpop #bksend') && !!document.querySelector('#bkpop #rstr')"), f'{tag} 백업 → 백업 창(보내기·받기·복원)')
    await pg.click('#rstr'); await pg.wait_for_selector('#rpop.on .rstore', timeout=8000)
    ok(not await pg.evaluate("document.querySelector('#bkpop').classList.contains('on')"), f'{tag} ↺ 복원 → 복원 창')
    await pg.keyboard.press('Escape')
    # ---- 1분 타이머 = 글자만 · revInfo 캐시 · 채점 → 오늘 복습
    await open_(pg, '#/CONS/_home/_home')
    L0 = await pg.evaluate("document.querySelector('#nav').innerHTML.length"); await pg.evaluate("__h.navBadges()"); L1 = await pg.evaluate("document.querySelector('#nav').innerHTML.length")
    ok(abs(L1 - L0) <= 4, f'{tag} 글자 갱신은 다시 그리지 않음 ({L0} → {L1})')
    await open_(pg, '#/'); n0 = await pg.evaluate("__h.rvcN()"); await pg.evaluate("__h.navRender()"); n1 = await pg.evaluate("__h.rvcN()")
    ok(0 < n0 <= (7 if ESTH_READY else 6) and n1 == n0, f'{tag} 허브 홈 revInfo = 과목당 1회({n0}) · 다시 그려도 0회 추가({n1 - n0})')
    await open_(pg, '#/CONS/_jb/_jb', 600)
    await pg.evaluate("(()=>{const c=document.querySelector('#cards .qc:not(.hid)');c.querySelector('.mk.ng,[data-mk=ng]').click();})()"); await pg.wait_for_timeout(600)
    await open_(pg, '#/')
    rv = await pg.evaluate("[(document.querySelector('#nav [data-nb=\"rv\"]')||{}).textContent,!document.querySelector('#nav [data-nv=rev]').hidden,Object.keys(__h.PACKS).reduce((a,s)=>a+__h.revInfo(s).due.size,0)]")
    ok(rv[2] >= 1 and rv[0] == str(rv[2]) and rv[1], f'{tag} ✗ 채점 → 허브 메뉴 오늘 복습 {rv}')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.mk.CONS')")
    # ---- B2-2 카드 목차 · 과목 바꾸기
    await open_(pg, '#/CONS/WHT/learn', 700)
    if narrow: await tap('#navbtn'); await pg.wait_for_timeout(350)
    t = await pg.evaluate("""(()=>{const sc=document.querySelector('#navsc'),q=sc.getBoundingClientRect(),L=[...sc.querySelectorAll('.nvtoc .scard2')];const P=__h.PACKS.CONS.lect.find(x=>x.k==='WHT');
      return {n:L.length,vis:L.filter(e=>{const r=e.getBoundingClientRect();return r.top>=q.top&&r.bottom<=q.bottom+1}).length,dots:L.filter(e=>e.querySelector('.x')).length,want:P.cards.filter(c=>c[3]).length,cards:P.cards.length,
       h:Math.round(L[0].getBoundingClientRect().height),lh:Math.round(sc.querySelector('.nvl').getBoundingClientRect().height),underCur:L[0].closest('.nvtoc').previousElementSibling.dataset.d}})()""")
    ok(t['n'] == t['cards'] and t['underCur'] == 'WHT', f'{tag} 지금 강의 바로 아래 카드 목차 {t["n"]}줄')
    ok(t['dots'] == t['want'] and t['dots'] > 0, f'{tag} 기출 카드 노란 점 {t["dots"]} = {t["want"]}')
    if W == 1280: ok(t['vis'] >= 10, f'{tag} 첫 화면에 카드 목차 {t["vis"]}줄 보임(≥10)')
    if touch: ok(t['lh'] >= 40 and t['h'] >= 36, f'{tag} 터치 줄 높이 강의 {t["lh"]} ≥40 · 목차 {t["h"]} ≥36')
    if narrow:
        await pg.screenshot(path=J.TMP + f'/ux4i_nav_{tag}_drawer.png'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
    await pg.evaluate("document.querySelector('#t-WHT-6').scrollIntoView({block:'start'});scrollBy(0,-90)"); await pg.wait_for_timeout(900)
    on = await pg.evaluate("[__h.LCUR,[...document.querySelectorAll('#nav .nvtoc .scard2.on')].map(e=>+e.dataset.lj)]")
    ok(on[0] == 6 and on[1] == [6], f'{tag} 스크롤로 카드 7 → 목차 7번 .on {on}')
    if narrow: await tap('#navbtn'); await pg.wait_for_timeout(350)
    vis = await pg.evaluate("(()=>{const e=document.querySelector('#nav .nvtoc .scard2.on'),q=document.querySelector('#navsc').getBoundingClientRect(),r=e.getBoundingClientRect();return r.top>=q.top-1&&r.bottom<=q.bottom+1})()")
    ok(vis, f'{tag} 메뉴 안에서 지금 카드가 보임')
    await tap('#nav .nvtoc .scard2[data-lj="2"]'); await pg.wait_for_timeout(900)
    r = await pg.evaluate("[__h.LCUR,document.body.classList.contains('navopen'),Math.round(document.querySelector('#t-WHT-2').getBoundingClientRect().top)]")
    ok(r[0] == 2 and not r[1] and 0 <= r[2] < 400, f'{tag} 목차 3번 누르면 그 카드로{"·서랍 닫힘" if narrow else ""} {r}')
    if narrow: await tap('#navbtn'); await pg.wait_for_timeout(350)
    await tap('#nav [data-nvsw]'); await pg.wait_for_timeout(200)
    sw = await pg.evaluate("(()=>{const p=document.querySelector('#nav .nvswp');return [!p.hidden,p.querySelectorAll('[data-nvsj]').length,(p.querySelector('.pi.on')||{}).dataset?.nvsj,document.querySelector('#nav [data-nvsw]').getAttribute('aria-expanded')]})()")
    ok(sw[0] and sw[1] == 7 and sw[2] == 'CONS' and sw[3] == 'true', f'{tag} [과목 바꾸기 ▾] → 7과목·지금 과목 눌림 {sw}')
    await pg.screenshot(path=J.TMP + f'/ux4i_nav_{tag}_switch.png')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(150)
    ok(await pg.evaluate("document.querySelector('#nav .nvswp').hidden"), f'{tag} Esc → 과목 바꾸기 닫힘')
    await tap('#nav [data-nvsw]'); await pg.wait_for_timeout(150); await tap('#nav [data-nvsj="IMPL"]'); await pg.wait_for_timeout(900)
    r = await pg.evaluate("[location.hash,document.querySelector('#nav').dataset.mode,(document.querySelector('#nav .nvsjn')||{}).textContent,getComputedStyle(document.querySelector('#nav')).getPropertyValue('--nc').trim().toLowerCase(),__h.sjColor('IMPL').toLowerCase(),document.querySelector('#navsc').scrollTop,document.body.classList.contains('navopen')]")
    ok(r[0].startswith('#/IMPL/_home') and r[1] == 'subj' and '임플란트' in r[2] and r[3] == r[4] and r[5] == 0 and not r[6], f'{tag} 과목 바꾸기 → IMPL 과목 홈 · 메뉴 색 IMPL · 맨 위 {r}')
    # ---- B2-6 허브 메뉴 스크롤 기억 · 뒤로가기 · ↩ 알약 · 달력 ?s
    await pg.set_viewport_size({'width': W, 'height': 420}); await open_(pg, '#/')
    if narrow: await tap('#navbtn'); await pg.wait_for_timeout(300)
    await pg.evaluate("document.querySelector('#navsc').scrollTop=120"); top0 = await pg.evaluate("document.querySelector('#navsc').scrollTop")
    await pg.evaluate("document.querySelector('#nav .nvsb[data-nvs=CONS]').click()"); await pg.wait_for_timeout(700)
    await pg.evaluate("document.querySelector('#nav .nvl[data-d=WHT]').click()"); await pg.wait_for_timeout(900)
    if narrow: await tap('#navbtn'); await pg.wait_for_timeout(300)
    await pg.evaluate("document.querySelector('#nav .nvback').click()"); await pg.wait_for_timeout(700)
    r = await pg.evaluate("[location.hash,document.querySelector('#nav').dataset.mode,document.querySelector('#navsc').scrollTop]")
    ok(top0 > 60 and r[0] in ('#/', '') and r[1] == 'hub' and abs(r[2] - top0) <= 2, f'{tag} ‹ 허브 홈 → 허브 메뉴·스크롤 복원 {top0} → {r}')
    await pg.evaluate("document.querySelector('#nav .nvsb[data-nvs=CONS]').click()"); await pg.wait_for_timeout(700)
    await pg.go_back(); await pg.wait_for_timeout(900)
    r = await pg.evaluate("[location.hash,document.querySelector('#nav').dataset.mode,document.querySelector('#navsc').scrollTop]")
    ok(r[1] == 'hub' and abs(r[2] - top0) <= 2, f'{tag} 뒤로가기 → 허브 메뉴·스크롤 복원 {r}')
    await pg.set_viewport_size(vp)
    await open_(pg, '#/OMS1/_jb/_jb', 800)
    g = await pg.evaluate("(()=>{const c=[...document.querySelectorAll('#cards .qc:not(.hid) [data-golec]')][0];if(!c)return null;const d=c.dataset.golec.split(':')[0];c.click();return d;})()"); await pg.wait_for_timeout(1200)
    r = await pg.evaluate("[location.hash,document.querySelector('#nav').dataset.mode,[...document.querySelectorAll('#nav [aria-current]')].filter(e=>!e.closest('.nvswp')).map(e=>e.dataset.d),document.querySelector('#retpill').classList.contains('on')]")
    ok(g and r[0].startswith('#/OMS1/' + g) and r[1] == 'subj' and r[2] == [g] and r[3], f'{tag} JB 📖 칩 → 강의({g}) · 과목 메뉴 그 강의 · ↩ 알약 {r}')
    await pg.evaluate("document.querySelector('#retpill').click()"); await pg.wait_for_timeout(1000)
    r = await pg.evaluate("[location.hash,document.querySelector('#nav').dataset.mode,[...document.querySelectorAll('#nav [aria-current]')].filter(e=>!e.closest('.nvswp')).map(e=>e.dataset.d)]")
    ok(r[0].startswith('#/OMS1/_jb') and r[1] == 'subj' and r[2] == ['_jb'], f'{tag} ↩ 알약 → OMS1 JB · 과목 메뉴 JB 문제 {r}')
    await open_(pg, '#/_cal?s=CONS'); r = await pg.evaluate("[document.querySelector('#nav').dataset.mode,document.querySelectorAll('#nav .nvs').length]")
    ok(r == ['hub', 7], f'{tag} 달력 ?s=CONS → 허브 메뉴 {r}')
    # ---- B2-5 서랍 / M
    if narrow:
        await open_(pg, '#/CONS/WHT/learn'); await tap('#navbtn'); await pg.wait_for_timeout(350)
        r = await pg.evaluate("(()=>{const s=document.querySelector('#side').getBoundingClientRect(),h=document.querySelector('#nav .nvdh');return [document.body.classList.contains('navopen'),Math.round(s.left),Math.round(s.width),Math.round(s.top),Math.round(s.bottom)-innerHeight,getComputedStyle(h).display,h.textContent.includes('임상치과보존학 메뉴'),document.documentElement.classList.contains('navlock'),getComputedStyle(document.querySelector('#navbg')).display,getComputedStyle(document.querySelector('#nav .nvhidew')).display]})()")
        ok(r[0] and r[1] == 0 and r[2] == 300 and r[3] == 0 and r[4] == 0 and r[5] == 'flex' and r[6] and r[7] and r[8] == 'block' and r[9] == 'none', f'{tag} ☰ → 300px 서랍(화면 위부터·머리 ● 보존 메뉴 ✕(ux4c 1회차 과목 메뉴는 과목 이름)·뒤 스크롤 잠금·가림막·M 없음) {r}')
        y0 = await pg.evaluate('scrollY'); await pg.mouse.wheel(0, 600); await pg.wait_for_timeout(250)
        ok(await pg.evaluate('scrollY') == y0, f'{tag} 서랍 열린 동안 뒤 화면 스크롤 안 됨')
        await tap('#nav .nvl[data-d="CRK"]'); await pg.wait_for_timeout(900)
        ok(await pg.evaluate("location.hash.indexOf('#/CONS/CRK')===0&&!document.body.classList.contains('navopen')&&!document.documentElement.classList.contains('navlock')"), f'{tag} 서랍 강의 줄 → 이동·닫힘·잠금 풀림')
        await tap('#navbtn'); await pg.wait_for_timeout(250); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(250)
        ok(not await pg.evaluate("document.body.classList.contains('navopen')"), f'{tag} Esc → 서랍 닫힘')
        await tap('#navbtn'); await pg.wait_for_timeout(250); await pg.click('#navbg', position={'x': W - 40, 'y': 500}); await pg.wait_for_timeout(250)
        ok(not await pg.evaluate("document.body.classList.contains('navopen')"), f'{tag} 가림막 → 서랍 닫힘')
        await tap('#navbtn'); await pg.wait_for_timeout(250); await tap('#nav .nvclose'); await pg.wait_for_timeout(250)
        ok(not await pg.evaluate("document.body.classList.contains('navopen')"), f'{tag} ✕ → 서랍 닫힘')
        # 회전 1180 ↔ 820
        await tap('#navbtn'); await pg.wait_for_timeout(250); await pg.set_viewport_size({'width': 1180, 'height': 820}); await pg.wait_for_timeout(500)
        r = await pg.evaluate("[document.body.classList.contains('navopen'),document.documentElement.classList.contains('navlock'),getComputedStyle(document.querySelector('#side')).visibility,Math.round(document.querySelector('#side').getBoundingClientRect().width),Math.round(document.querySelector('#main').getBoundingClientRect().left)]")
        ok(not r[0] and not r[1] and r[2] == 'visible' and r[3] == 256 and r[4] == 256, f'{tag} 서랍 연 채 가로로 → 서랍 닫힘·고정 메뉴 256 {r}')
        await pg.set_viewport_size(vp); await pg.wait_for_timeout(500)
        r = await pg.evaluate("[document.body.classList.contains('navopen'),getComputedStyle(document.querySelector('#side')).visibility,Math.round(document.querySelector('#main').getBoundingClientRect().left)]")
        ok(not r[0] and r[1] == 'hidden' and r[2] == 0, f'{tag} 다시 세로 → 서랍 닫힌 채 {r}')
    else:
        await open_(pg, '#/CONS/WHT/learn'); await pg.evaluate("['sidefold','navfold','navfoldHub','wideSide','focus'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))"); await open_(pg, '#/CONS/WHT/learn')
        await pg.evaluate("window.__lev=0;document.addEventListener('jbl:layout',()=>__lev++)")
        ST = "[document.body.classList.contains('sidefold'),Math.round(document.querySelector('#main').getBoundingClientRect().left),getComputedStyle(document.querySelector('#navbtn')).display,JSON.parse(localStorage.getItem('jblhub.v1.navfold')),__lev,document.querySelectorAll('#sideopen').length]"
        ok(await pg.evaluate("getComputedStyle(document.querySelector('#navbtn')).display") == 'none', f'{tag} 메뉴가 보일 때 상단 ☰ 없음')
        await pg.keyboard.press('Shift+M'); await pg.wait_for_timeout(500); r = await pg.evaluate(ST)
        ok(r[0] and r[1] == 0 and r[2] != 'none' and r[3] is True and r[4] == 1 and r[5] == 0, f'{tag} M → 메뉴 숨김·#main 왼쪽 0·☰ 보임·navfold·jbl:layout 1번·› 손잡이 없음 {r}')
        await pg.screenshot(path=J.TMP + f'/ux4i_nav_{tag}_fold.png')
        await pg.click('#gohome'); await pg.wait_for_timeout(700)
        ok(await pg.evaluate("document.body.classList.contains('sidefold')"), f'{tag} 학습에서 숨기면 허브 홈도 숨김(설정 하나)')
        await pg.click('#navbtn'); await pg.wait_for_timeout(500); r = await pg.evaluate(ST)
        ok(not r[0] and r[1] == 256 and r[3] is False, f'{tag} ☰ → 메뉴 다시 보임·#main 256 {r}')
        await open_(pg, '#/CONS/WHT/learn'); ok(not await pg.evaluate("document.body.classList.contains('sidefold')"), f'{tag} 과목에서도 보임')
        await pg.keyboard.press('Shift+M'); await pg.wait_for_timeout(400); await pg.keyboard.press('v'); await pg.wait_for_timeout(300); await pg.keyboard.press('v'); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("document.body.classList.contains('sidefold')&&!document.body.classList.contains('focus')"), f'{tag} 집중 모드(V) 켜고 꺼도 M 숨김 그대로')
        await pg.keyboard.press('Shift+M'); await pg.wait_for_timeout(400)
        ok(not await pg.evaluate("document.body.classList.contains('sidefold')"), f'{tag} M 다시 → 복원')
        await pg.evaluate("['sidefold','navfold','navfoldHub','wideSide','focus'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))")
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
