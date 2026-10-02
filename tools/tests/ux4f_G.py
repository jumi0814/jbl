"""ux4f G 회귀 — 마지막 회차 새 오류(허브·과목 홈 관점, 클라우드 10-02)
G1 과목 홈 공부 순서: '오늘 복습' 줄이 있어도 단계 번호는 1부터
G2 과목 홈(공부 순서·교수별 출제 경향 표)에 % 글자 없음 — 짤 수/문항 수로
G3 아이패드 손가락 대상 44px — 공부 순서 링크·강의 바로가기·진행률 버튼·서랍 머리·카드 목차·통계 ◀▶·검색 탭
G4 백업 창 '이 기기 이름' Esc = 저장하고 창 닫기 · 상태 줄 바로 새 이름
G5 아이패드 세로 상단 막대 높이 = 52 하나(강의 제목 길이와 상관없이) · 검색칸 120px 그대로 · 강의 제목은 전체
G6 과목 홈 '↪ 최근 읽던 곳' 시각 = 허브 홈과 같은 표기(atLab — '10. 2. 오전' 같은 로캘 표기 없음)"""
import os as _os, sys as _sys, re, json, datetime; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
td = datetime.date.today().isoformat()
def new(b, w, h, touch, seed=None):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch)
    ctx.add_init_script("try{if(!localStorage.getItem('jblhub.v1.whatsNew.4'))localStorage.setItem('jblhub.v1.whatsNew.4','1')}catch(e){}")
    pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    pg.on('dialog', lambda d: d.accept())
    return ctx, pg
def go(pg, h, w=700):
    pg.goto('about:blank'); pg.goto(U + '#' + h); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(w)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = new(b, 820, 1180, True)
    # 틀린 기출 하나(오늘 복습 줄이 생기게) — JB 화면에서 첫 문항 ✗
    go(pg, '/CONS/_jb')
    pg.locator('#cards .qc button', has_text='✗ 틀림').first.click(); pg.wait_for_timeout(400)
    # 틀린 날을 이틀 전으로(오늘 복습 대상이 되게) — mk.CONS 형식은 그대로, 날짜 값만 앞당김
    pg.evaluate("(()=>{const k='jblhub.v1.mk.CONS';const m=JSON.parse(localStorage.getItem(k)||'{}');const old=Date.now()-2*864e5;const sh=o=>{if(o&&typeof o==='object')for(const i in o){if(typeof o[i]==='number'&&o[i]>1e12)o[i]=old;else if(Array.isArray(o[i]))o[i]=o[i].map(v=>typeof v==='number'&&v>1e12?old:(v&&typeof v==='object'?(sh(v),v):v));else if(o[i]&&typeof o[i]==='object')sh(o[i]);}};sh(m);localStorage.setItem(k,JSON.stringify(m));})()")
    go(pg, '/CONS/WHT/learn'); pg.evaluate("window.scrollTo(0,1500)"); pg.wait_for_timeout(1500)
    go(pg, '/CONS/_home/_home')
    # G1
    r = pg.evaluate("""(()=>{const L=[...document.querySelectorAll('#hguide ol.steps>li')];return L.map(li=>getComputedStyle(li,'::before').content)})()""")
    rv = pg.evaluate("!!document.querySelector('#hguide li.rvli')")
    nums = [x.strip('"') for x in r if x.strip('"') != '·']
    ok(rv, f'G1 오늘 복습 줄 있음(시드) {rv} {r[:3]}')
    n1 = pg.evaluate("(()=>{const li=[...document.querySelectorAll('#hguide ol.steps>li:not(.rvli)')][0];const s=getComputedStyle(li);return s.counterIncrement+' | '+getComputedStyle(document.querySelector('#hguide li.rvli')||li).counterIncrement})()")
    ok(not rv or n1.split(' | ')[1].startswith('none'), f'G1 복습 줄은 번호를 세지 않음 {n1}')
    # G2
    tx = pg.evaluate("[...document.querySelectorAll('#hguide, section.ptrend table.ttab')].map(e=>e.innerText+' '+[...e.querySelectorAll('[title]')].map(x=>x.title).join(' ')).join(' ')")
    ok('%' not in tx and '짤 / 문항' in tx and re.search(r'\d+/\d+', tx), f'G2 과목 홈 % 없음·개수 {re.findall(r".{12}%.{0,4}", tx)[:3]}')
    # G6
    rs = pg.evaluate("(document.querySelector('#hprog .go-resume')||{}).textContent||''")
    ok(rs and not re.search(r'오전|오후|\d+\. \d+\.', rs), f'G6 최근 읽던 곳 시각 표기 {rs[-30:]!r}')
    # G3
    Q = """(s)=>[...document.querySelectorAll(s)].filter(e=>e.offsetParent).slice(0,4).map(e=>Math.round(e.getBoundingClientRect().height))"""
    for s in ['#hguide .b3lk', '.chip.ljc', '.b3btn']:
        h = pg.evaluate(Q, s); ok(h and min(h) >= 44, f'G3 820 과목 홈 {s} {h}')
    pg.evaluate("document.querySelector('#navbtn').click()"); pg.wait_for_timeout(400)
    for s in ['#nav .nvback', '#nav .nvsw']:
        h = pg.evaluate(Q, s); ok(h and min(h) >= 44, f'G3 820 서랍 {s} {h}')
    go(pg, '/CONS/WHT/learn'); pg.evaluate("document.querySelector('#navbtn').click()"); pg.wait_for_timeout(400)
    h = pg.evaluate(Q, '#nav .nvtoc .scard2'); ok(h and min(h) >= 44, f'G3 820 카드 목차 {h}')
    go(pg, '/_time')
    for s in ['[data-tvw]', '#tvgoal']:
        h = pg.evaluate(Q, s); ok(h and min(h) >= 44, f'G3 820 통계 {s} {h}')
    # G5
    hs = {}
    for h_ in ['/CONS/WHT/learn', '/CONS/DHS/learn', '/CONS/ADH/learn', '/OMS1/DD1/learn', '/CONS/_home/_home', '/CONS/_jb/_jb']:
        go(pg, h_, 400)
        r = pg.evaluate("[document.querySelector('#top').offsetHeight,document.querySelector('#gsearch').offsetWidth,(document.querySelector('#crumb .ccur')||{}).textContent,(()=>{const e=document.querySelector('#crumb .ccur'),t=document.querySelector('#top').getBoundingClientRect(),r=e.getBoundingClientRect();return r.bottom<=t.bottom+1&&r.top>=t.top-1})()]")
        hs[h_] = r
    ok(all(v[0] == 52 and v[1] == 120 and v[3] for v in hs.values()), f'G5 820 상단 막대 52·검색칸 120·제목 막대 안 {[(k, v[0], v[1]) for k, v in hs.items()]}')
    ok(hs['/CONS/DHS/learn'][2] == 'Dentin hypersensitivity — 시린 치아, 제대로 진단하고 효과적으로 진료하기', f'G5 강의 제목 전체 {hs["/CONS/DHS/learn"][2]!r}')
    ok(not pg.errs, f'820 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # G4 백업 창 기기 이름 Esc
    for W, H, T in [(1280, 900, False), (820, 1180, True)]:
        ctx, pg = new(b, W, H, T); go(pg, '/')
        if T: pg.evaluate("document.querySelector('#navbtn').click()"); pg.wait_for_timeout(400)
        pg.evaluate("document.querySelector('#bkup').click()"); pg.wait_for_timeout(300)
        pg.click('#devname'); pg.fill('#devname', '내 맥북'); pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
        r = pg.evaluate("[document.querySelector('#bkpop').classList.contains('on'),JSON.parse(localStorage.getItem('jblhub.v1.devName')||'null'),document.activeElement&&document.activeElement.id]")
        ok(not r[0] and r[1] == '내 맥북' and r[2] != 'devname', f'G4 {W} 기기 이름 Esc = 저장·창 닫힘 {r}')
        pg.evaluate("document.querySelector('#bkup').click()"); pg.wait_for_timeout(300)
        pg.fill('#devname', '공부 아이패드'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
        st = pg.evaluate("document.querySelector('#bkst').textContent")
        ok('공부 아이패드' in st, f'G4 {W} Enter 뒤 상태 줄 새 이름 {st[:40]!r}')
        ok(not pg.errs, f'G4 {W} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
