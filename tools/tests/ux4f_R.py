"""ux4f R 회귀 — 10-03 허브 점검(HUB_MARK·HUB_TIME·HUB_JB)에서 고친 것
R1 H·B를 켜도 카드 머리 ▣ 칩이 자리를 지킴(visibility) — 본문 세로 위치 그대로
R2 ⏱ 크게를 연 채 V·H·2를 눌러도 뒤 화면이 바뀌지 않음(Esc로 닫힘)
R3 820 세로 학습 탭 ⋯ 보기 메뉴가 화면 안(왼쪽 0 이상)
R4 카드 머리 연도 칩을 다시 누르면 미리보기가 닫힘 · 연도 없는 문항 칩 = '연도 미상'(빈 버튼 없음)
R5 머리 칩의 문항 묶음 ⊇ 그 카드 ⭐의 문항"""
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
    pg = ctx.new_page(); pg.errs = []; pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); return ctx, pg
def go(pg, h, w=1200):
    pg.goto('about:blank'); pg.goto(U + '#' + h); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(w)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = new(b, 1280, 900, False)
    # ---------- R1 ----------
    go(pg, '/CONS/WHT/learn')
    pg.keyboard.press('q'); pg.wait_for_timeout(500)   # 가리기 보기 → 빨간 낱말이 가려져 카드 머리에 ▣ 칩
    pg.evaluate("(()=>{const c=[...document.querySelectorAll('#stage .tc')].find(c=>c.querySelector('.qzchip'));if(c){c.id='r1c';c.scrollIntoView({block:'center'});}})()"); pg.wait_for_timeout(300)
    G = "(c=>c?[!!c.querySelector('.qzchip'),Math.round((c.querySelector('.tbody')||c).getBoundingClientRect().top),(c.querySelector('.qzchip')||{style:{}}).style.visibility||'']:null)(document.querySelector('#r1c'))"
    r0 = pg.evaluate(G); pg.keyboard.press('h'); pg.wait_for_timeout(300); r1 = pg.evaluate(G)
    ok(r0 and r0[0] and r1[0] and r1[2] == 'hidden' and abs(r1[1] - r0[1]) <= 1, f'R1 H 켬 → ▣ 칩 자리 그대로(숨김) · 본문 위치 {r0} → {r1}')
    pg.keyboard.press('h'); pg.wait_for_timeout(200); r2 = pg.evaluate(G)
    ok(r2 and r2[2] == '', f'R1 H 끔 → ▣ 칩 다시 보임 {r2}')
    pg.keyboard.press('q'); pg.wait_for_timeout(200)
    # ---------- R2 ----------
    go(pg, '/OMS1/DD1/learn')
    opened = pg.evaluate("(()=>{const b=document.querySelector('[data-bigopen],[data-big],#ckbig');if(b){b.click();return 1;}if(window.__h&&__h.bigOpen){__h.bigOpen();return 2;}return 0;})()"); pg.wait_for_timeout(400)
    if not pg.evaluate("!!document.querySelector('#bigclock.on')"):
        pg.evaluate("document.querySelector('#clock')&&document.querySelector('#clock').click()"); pg.wait_for_timeout(300)
        pg.evaluate("(()=>{const b=[...document.querySelectorAll('button')].find(x=>/크게/.test(x.textContent)&&x.offsetParent);if(b)b.click();})()"); pg.wait_for_timeout(400)
    big = pg.evaluate("!!document.querySelector('#bigclock.on')")
    h0 = pg.evaluate("location.hash")
    for k in ('v', 'h', '2'): pg.keyboard.press(k); pg.wait_for_timeout(150)
    st = pg.evaluate("[document.body.classList.contains('focus'),document.body.classList.contains('mode-h'),location.hash]")
    ok(big and st == [False, False, h0], f'R2 ⏱ 크게 열린 채 V·H·2 → 뒤 화면 그대로 {big} {st}')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(not pg.evaluate("!!document.querySelector('#bigclock.on')"), 'R2 Esc → ⏱ 크게 닫힘')
    # ---------- R4 ----------
    go(pg, '/PHARM/RX/learn', 1500)
    c = pg.evaluate("(()=>{const b=document.querySelector('#stage .tchips .chip.yr[data-go]');if(!b)return null;b.id='r4c';b.scrollIntoView({block:'center'});const r=b.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];})()")
    pg.wait_for_timeout(300); pg.mouse.click(c[0], c[1]); pg.wait_for_timeout(400)
    o1 = pg.evaluate("!!document.querySelector('#jbpeek.on')")
    c = pg.evaluate("(b=>{const r=b.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})(document.querySelector('#r4c'))")
    pg.mouse.click(c[0], c[1]); pg.wait_for_timeout(400)
    ok(o1 and not pg.evaluate("!!document.querySelector('#jbpeek.on')"), f'R4 머리 연도 칩 → 미리보기 열림 {o1} · 다시 누름 → 닫힘')
    # ---------- R5 ----------
    bad = []
    for s, k in [('PHARM', 'RX'), ('ANAT', 'MAND'), ('PHARM', 'BT'), ('OMS1', 'DD1')]:
        go(pg, f'/{s}/{k}/learn', 1200)
        bad += pg.evaluate("""(s=>[...document.querySelectorAll('#stage .tc')].map(c=>{const h=c.querySelector('.tchips .chip.yr[data-go]');const hs=new Set(h?[h.dataset.go,...(h.dataset.gos||'').split(' ')].filter(Boolean):[]);const es=[...c.querySelectorAll('.c-exam [data-go]')].map(x=>x.dataset.go).filter(x=>!hs.has(x));return es.length?s+':'+c.id+':'+es.join(','):null}).filter(Boolean))""", f'{s}/{k}')
        bad += pg.evaluate("""(s=>[...document.querySelectorAll('#stage .jbchip,#stage .chip.yr,#stage .xjb')].filter(b=>!b.textContent.trim()).map(b=>s+':빈칩:'+b.dataset.go))""", f'{s}/{k}')
    go(pg, '/CONS/INL/learn', 1200)
    bad += pg.evaluate("[...document.querySelectorAll('#stage .jbchip,#stage .chip.yr,#stage .xjb')].filter(b=>!b.textContent.trim()).map(b=>'CONS/INL:빈칩:'+b.dataset.go)")
    ok(not bad, f'R5 머리 칩 ⊇ ⭐ 문항 · 빈 칩 없음 {bad[:4]}')
    ok(not pg.errs, f'1280 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # ---------- R3 ----------
    ctx, pg = new(b, 820, 1180, True); out = []
    for s, k in [('OMS1', 'REP'), ('ESTH', 'MAT'), ('OMS1', 'DD3')]:
        go(pg, f'/{s}/{k}/learn', 1200)
        r = pg.evaluate("(()=>{const d=document.querySelector('#stage details.pmore');if(!d)return null;d.scrollIntoView({block:'center'});d.open=true;return 1;})()"); pg.wait_for_timeout(300)
        if r: out.append((s + k, pg.evaluate("(m=>m?Math.round(m.getBoundingClientRect().left):null)(document.querySelector('#stage details.pmore[open] .pmenu'))"), pg.evaluate("(m=>m?Math.round(m.getBoundingClientRect().right):null)(document.querySelector('#stage details.pmore[open] .pmenu'))")))
    ok(all(x[1] is not None and x[1] >= 0 and x[2] <= 820 for x in out), f'R3 820 ⋯ 메뉴 화면 안 {out}')
    ok(not pg.errs, f'820 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
