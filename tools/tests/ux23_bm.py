"""UX23 ★ 모아보기(10-21 사용자 "예상문제에 대해서도 별표 표시가 있는데 별표끼리 모아볼 수 있는 태그가 기출탭처럼 있어야지! 그리고내 넘버링으로 가져올 때 별표 분류할 수 있는 (또는 별표 표시가 보이게끔)했으면 좋겠어!")
- 예상 탭 막대 '★' = ★ 표시한 예상문제만(다시 누르면 전체) · 카드의 ★ 버튼과 같은 기록(mk.<과목>.bm['P:<aid>'])
- 내 넘버링 '기존 문제 불러오기': ★ 표시한 JB 기출·예상문제에 ★ 칩 · '★ 표시한 것만' 거르기
- 가져온 문제 머리에 ★(JBL에서 ★면) · ★ 기록은 읽기만(바꾸지 않음) · pageerror 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CLEAR = "(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0||k==='jblhub.v1.mk.ESTH')localStorage.removeItem(k);})()"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1300, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(J.HUB_URL + '#/'); pg.wait_for_timeout(2500); pg.evaluate(CLEAR)
    keys = pg.evaluate("""(()=>{const P=__h.PACKS.ESTH,pr=P.preds.filter(x=>!x.x&&x.k==='INT').slice(0,2).map(x=>'P:'+x.aid),jb=Object.keys(P.cards).find(k=>/data-lec="INT"/.test(P.cards[k].slice(0,900)));
      const bm={};pr.concat([jb]).forEach(k=>bm[k]=Date.now());localStorage.setItem('jblhub.v1.mk.ESTH',JSON.stringify({ok:{},ng:{},bm}));return pr.concat([jb]);})()""")
    ok(len(keys) == 3, f"★ 3개 심음(예상 2 · JB 1) {keys}")
    pg.reload(); pg.wait_for_timeout(2500); pg.evaluate("location.hash='#/ESTH/INT/pred'"); pg.wait_for_timeout(2500)
    has = pg.evaluate("!!document.querySelector('#ppills [data-pf=bm]')"); ok(has, "예상 탭 막대에 ★ 거르기")
    n0 = pg.evaluate("[...document.querySelectorAll('#stage .pc:not(.px)')].filter(c=>c.offsetParent).length")
    pg.click('#ppills [data-pf=bm]'); pg.wait_for_timeout(500)
    vis = pg.evaluate("[...document.querySelectorAll('#stage .pc')].filter(c=>c.offsetParent).map(c=>c.dataset.id)")
    ok(sorted(vis) == sorted(keys[:2]), f"★ 누르면 ★ 예상문제만 {len(vis)}/{n0} {vis}")
    pg.click('#ppills [data-pf=bm]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("[...document.querySelectorAll('#stage .pc:not(.px)')].filter(c=>c.offsetParent).length") == n0, "다시 누르면 전체")
    pg.evaluate("location.hash='#/_num/ESTH'"); pg.wait_for_timeout(3000)
    pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); pg.wait_for_timeout(800)
    pg.select_option('[data-if=ty]', ''); pg.wait_for_timeout(300)
    chips = pg.evaluate("document.querySelectorAll('.nm-irow .nm-chip.bm').length"); ok(chips == 3, f"불러오기 목록 ★ 칩 {chips}")
    pg.select_option('[data-if=bm]', '1'); pg.wait_for_timeout(400)
    rows = pg.evaluate("[...document.querySelectorAll('.nm-irow')].length"); ok(rows == 3, f"'★ 표시한 것만' = {rows}문제")
    pg.click('[data-ib=flt]'); pg.wait_for_timeout(600)
    if pg.query_selector('[data-cf2=ok]'): pg.click('[data-cf2=ok]')
    pg.wait_for_timeout(1500); pg.click('.nm-ov [data-x]'); pg.wait_for_timeout(800)
    st = pg.evaluate("[document.querySelectorAll('.nm-it').length,document.querySelectorAll('.nm-it .nm-bm').length]")
    ok(st[0] == 3 and st[1] == 3, f"가져온 {st[0]}문제 머리 ★ {st[1]}")
    mk = pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('jblhub.v1.mk.ESTH')).bm).length"); ok(mk == 3, "★ 기록은 그대로(읽기만)")
    ok(not errs, f"pageerror 0 {errs[:3]}")
    pg.evaluate(CLEAR); b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
