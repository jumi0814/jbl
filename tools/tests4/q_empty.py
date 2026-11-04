"""11-04 과목이 아직 없는(또는 적은) 쿼터 허브 — 홈·달력·통계·내 강의목록·내 넘버링·넘버링 복습·검색·백업 창·도움말이 오류 없이 열림 (컴퓨터·폰)
과목이 생기면 그 과목 홈도 같이 열어 봄(자료 대기 과목 포함)"""
from qsite import *
from playwright.sync_api import sync_playwright
rel = build(); base = serve()
Q4 = [q for q in QS.QS if q != '3q']
with sync_playwright() as p:
    br = p.chromium.launch()
    for vw, mob in (({'width': 1280, 'height': 900}, False), ({'width': 393, 'height': 852}, True)):
        ctx = br.new_context(viewport=vw, is_mobile=mob, has_touch=mob); ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, body='{}'))
        for q in Q4:
            pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda x: errs.append(str(x)[:200])); pg.on('dialog', lambda d: d.dismiss())
            U = url(base, rel[q]); pg.goto(U); pg.wait_for_timeout(3000)
            seen = []
            for h in ['#/', '#/_cal', '#/_time', '#/_bm', '#/_num', '#/_numr'] + [f'#/{s}/_home' for s in QS.sids(q)]:
                pg.goto(U + h); pg.wait_for_timeout(1500); seen.append(h)
                ok(pg.evaluate("document.querySelector('#home,#stage')!=null && document.body.innerText.length>20"), f'{q} {vw["width"]}px {h} 화면이 그려짐')
            pg.goto(U + '#/'); pg.wait_for_timeout(1200)
            pg.evaluate("(()=>{const b=document.querySelector('#bkup');if(b)b.click();})()"); pg.wait_for_timeout(1200)
            ok(pg.evaluate("!!document.querySelector('.bkp,#bkpanel,.panel')"), f'{q} {vw["width"]}px 백업·동기화 창')
            pg.keyboard.press('Escape'); pg.evaluate("(()=>{const s=document.querySelector('#gsearch');if(s){s.focus();s.value='치아';s.dispatchEvent(new Event('input',{bubbles:true}));}})()"); pg.wait_for_timeout(1500)
            sw = pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
            ok(sw, f'{q} {vw["width"]}px 가로 넘침 없음')
            ok(not errs, f'{q} {vw["width"]}px 콘솔 오류 0 {errs[:3]}')
            pg.close()
        ctx.close()
    br.close()
done()
