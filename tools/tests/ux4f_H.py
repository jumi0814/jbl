"""ux4f H 회귀 — 마지막 회차 새 오류(학습·표 관점, 클라우드 10-02)
H1 정리표 ★ 칸 연도 칩이 칸 밖(⚡ 열)으로 넘치지 않음 — 1180 터치(메뉴 자동 숨김)·1280 메뉴 펼침
H2 학습 탭 본문 표가 820에서 칸보다 넓지 않음(ANAT NECK·IMPL GRAFT)
H3 '이 강의의 틀' 카드 목차 제목·정리표 묶음 칩·전체정리표 칩에 말줄임(…·text-overflow) 없음 — 이름 그대로, 좁으면 줄바꿈
H4 과목 비교표 강의 칩 줄이 넘치면 오른쪽 흐림(.ovr) · 세로 휠로 가로 넘김
H5 플래시카드 ◀▶ 손가락 44px"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
def new(b, w, h, touch):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch)
    ctx.add_init_script("try{if(!localStorage.getItem('jblhub.v1.whatsNew.4'))localStorage.setItem('jblhub.v1.whatsNew.4','1')}catch(e){}")
    pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    return ctx, pg
def go(pg, h, w=900):
    pg.goto('about:blank'); pg.goto(U + '#' + h); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(w)
STAR = """(()=>[...document.querySelectorAll('#stage .msum td.mt .jbchip')].filter(e=>e.offsetParent).map(c=>{const td=c.closest('td').getBoundingClientRect(),r=c.getBoundingClientRect();return Math.round(r.right-td.right)}).filter(x=>x>1))()"""
ELL = """(sel)=>[...document.querySelectorAll(sel)].filter(e=>e.offsetParent).filter(e=>{const s=getComputedStyle(e);return e.textContent.includes('…')||(s.textOverflow==='ellipsis'&&e.scrollWidth>e.clientWidth+1)}).map(e=>e.textContent.trim().slice(0,30))"""
with sync_playwright() as p:
    b = p.chromium.launch()
    # H1
    for W, H, T, menu in [(1180, 820, True, False), (1280, 900, False, True)]:
        ctx, pg = new(b, W, H, T)
        for h_ in ['/CONS/WHT/sum', '/GERI/PSY/sum']:
            go(pg, h_)
            if menu and pg.evaluate("document.body.classList.contains('sidefold')"): pg.keyboard.press('Shift+M'); pg.wait_for_timeout(800)
            pg.evaluate("document.querySelectorAll('#stage .msum .mex:not(.mexo)').forEach(()=>0)"); r = pg.evaluate(STAR)
            ok(not r, f'H1 {W}{" 메뉴" if menu else ""} {h_} ★ 칸 칩 넘침 0 {r[:4]}')
        ok(not pg.errs, f'H1 {W} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # H2·H3·H5 (820)
    ctx, pg = new(b, 820, 1180, True)
    for h_ in ['/ANAT/NECK/learn', '/IMPL/GRAFT/learn']:
        go(pg, h_)
        r = pg.evaluate("[...document.querySelectorAll('#stage .tc .tscroll')].filter(s=>s.offsetParent).map(s=>[s.closest('.tc').id,s.scrollWidth,s.clientWidth]).filter(x=>x[1]>x[2]+1)")
        ok(not r, f'H2 820 {h_} 학습 표 넘침 0 {r[:3]}')
    for h_ in ['/PHARM/RX/learn', '/GERI/PAIN/learn', '/ANAT/MAND/learn']:
        go(pg, h_); r = pg.evaluate(ELL, '#stage .frame .outline .ot')
        ok(not r, f'H3 820 {h_} 틀 카드 목차 말줄임 0 {r[:3]}')
    for h_ in ['/GERI/PAIN/sum', '/IMPL/GRAFT/sum', '/PHARM/RX/sum', '/ANAT/NV/sum']:
        go(pg, h_); r = pg.evaluate(ELL, '#stage .msbar .tg, #stage .stchips .tg')
        ok(not r, f'H3 820 {h_} 묶음·전체정리표 칩 말줄임 0 {r[:3]}')
    go(pg, '/OMS1/DD1/flash')
    r = pg.evaluate("['#fprev','#fnext'].map(s=>{const e=document.querySelector(s);const q=e.getBoundingClientRect();return [Math.round(q.width),Math.round(q.height)]})")
    ok(all(x[0] >= 44 and x[1] >= 44 for x in r), f'H5 820 플래시카드 ◀▶ 44px {r}')
    ok(not pg.errs, f'820 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # H4
    ctx, pg = new(b, 1280, 900, False); go(pg, '/PHARM/_tbl/_tbl')
    r = pg.evaluate("(()=>{const s=document.querySelector('#stage .tbltoc .ttc');return [s.classList.contains('ovr'),s.scrollWidth>s.clientWidth]})()")
    ok(r[0] and r[1], f'H4 비교표 칩 줄 넘침 → 오른쪽 흐림 {r}')
    box = pg.evaluate("(()=>{const r=document.querySelector('#stage .tbltoc .ttc').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
    pg.mouse.move(box[0], box[1]); y0 = pg.evaluate("scrollY"); pg.mouse.wheel(0, 300); pg.wait_for_timeout(400)
    r = pg.evaluate("[document.querySelector('#stage .tbltoc .ttc').scrollLeft,scrollY]")
    ok(r[0] > 0 and r[1] == y0, f'H4 세로 휠 = 칩 줄 가로 넘김(페이지는 그대로) {r} {y0}')
    ok(not pg.errs, f'H4 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
