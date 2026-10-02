"""ux4f F 회귀 — 마지막 회차 새 오류(클라우드 10-02)
F1 펜슬 톡(모드 없음)으로 형광펜을 지우면 알림 + [↶ 되돌리기](말없이 지워지던 것) — 되돌리면 표시가 돌아옴
F2 아이패드를 돌려도(1180↔820) 읽던 JB 문항·학습 블록이 같은 자리(한 번 돌릴 때마다 두 문항씩 뒤로 밀리던 것)
F3 손가락 대상 44px — JB 참고 [보이기]·📖 강의 칩·내 표시 ↗·기출 대장 쪽 번호
F4 빈칸 모드에서 형광펜을 누르면 빈칸으로 + 알림 하나(덮어씀 알림이 겹쳐 두 번 뜨던 것)"""
import os as _os, sys as _sys, re; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
JSP = open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'kt3.py'), encoding='utf-8').read().split('JSP="""')[1].split('"""')[0]
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
def new(b, w, h, touch):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch)
    ctx.add_init_script("try{if(!localStorage.getItem('jblhub.v1.whatsNew.4'))localStorage.setItem('jblhub.v1.whatsNew.4','1')}catch(e){}")
    pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    pg.on('dialog', lambda d: d.accept())
    return ctx, pg
def go(pg, h, w=700):
    pg.goto('about:blank'); pg.goto(U + '#' + h); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(w)
TOAST = "(document.querySelector('#toast').style.display==='block'?document.querySelector('#toast').textContent:'')"
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------- F1 펜슬 톡 지우기 ----------
    print('== F1 펜슬 톡')
    ctx, pg = new(b, 820, 1180, True)
    go(pg, '/CONS/_jb')
    # 마우스 대신 Kit API 없이: H 모드에서 손가락 길게 눌러 끌기로 칠함
    pg.keyboard.press('h'); pg.wait_for_timeout(200)
    xy = pg.evaluate("(()=>{const c=document.querySelector('#cards .qc .qtext');c.scrollIntoView({block:'center'});const w=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){if(n.nodeValue.trim().length>12)break;}const r=document.createRange();r.setStart(n,0);r.setEnd(n,10);const q=r.getBoundingClientRect();return [q.left+2,q.top+q.height/2,q.right-2,c.closest('.qc').id]})()")
    pg.wait_for_timeout(300)
    pg.evaluate(JSP, [xy[0], xy[1], xy[2], xy[1], 30, 'stylus']); pg.wait_for_timeout(400)
    pg.keyboard.press('h'); pg.wait_for_timeout(300)
    q = xy[3]; n0 = pg.evaluate(f"document.querySelectorAll('#{q} [data-rk=h]').length")
    ok(n0 >= 1 and pg.evaluate("__h.Kit.mode()") in (None, ''), f'F1 펜슬로 칠함 {n0} · 모드 꺼짐')
    m = pg.evaluate(f"(()=>{{const m=document.querySelector('#{q} [data-rk=h]');const r=m.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}})()")
    pg.evaluate(JSP, [m[0], m[1], m[0], m[1], 30, 'stylus']); pg.wait_for_timeout(400)
    n1 = pg.evaluate(f"document.querySelectorAll('#{q} [data-rk=h]').length"); t = pg.evaluate(TOAST)
    ok(n1 == 0 and '지웠어요' in t and '되돌리기' in t, f'F1 펜슬 톡 = 지움 + 알림·되돌리기 {n0}→{n1} {t!r}')
    pg.evaluate("document.querySelector('#toast .tact').click()"); pg.wait_for_timeout(400)
    n2 = pg.evaluate(f"document.querySelectorAll('#{q} [data-rk=h]').length")
    ok(n2 == n0, f'F1 알림 [↶ 되돌리기] = 표시가 돌아옴 {n2}')
    ok(not pg.errs, f'F1 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # ---------- F2 회전 ----------
    print('== F2 회전')
    AT = """(sel)=>{const y=300;const L=[...document.querySelectorAll(sel)].filter(e=>e.offsetParent);const M=L.filter(e=>{const r=e.getBoundingClientRect();return r.top<=y&&r.bottom>y});const c=M[M.length-1];return c?(c.id||c.dataset.aid):null}"""
    for h_, sel, start in [('/CONS/_jb', '#stage .qc', "document.querySelector('#c-Q15').scrollIntoView({block:'start'});window.scrollBy(0,-200)"),
                           ('/OMS1/_jb', '#stage .qc', "document.querySelector('#c-Q20').scrollIntoView({block:'start'});window.scrollBy(0,-200)"),
                           ('/CONS/WHT/learn', '#stage [data-aid]', "document.querySelector('#t-WHT-4').scrollIntoView({block:'start'});window.scrollBy(0,-200)")]:
        ctx, pg = new(b, 820, 1180, True); go(pg, h_)
        pg.evaluate(start); pg.mouse.wheel(0, 10); pg.wait_for_timeout(1200)
        a0 = pg.evaluate(AT, sel); seq = [a0]
        for i in range(2):
            pg.set_viewport_size({'width': 1180, 'height': 820}); pg.wait_for_timeout(1200); seq.append(pg.evaluate(AT, sel))
            pg.set_viewport_size({'width': 820, 'height': 1180}); pg.wait_for_timeout(1200); seq.append(pg.evaluate(AT, sel))
        ok(a0 and seq[-1] == a0 and seq[2] == a0, f'F2 {h_} 돌려도 같은 자리 {seq}')
        ok(not pg.errs, f'F2 {h_} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # ---------- F3 손가락 44px ----------
    print('== F3 손가락 대상')
    Q = """(s)=>[...document.querySelectorAll(s)].filter(e=>e.offsetParent).slice(0,3).map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]})"""
    for W, H in [(820, 1180), (1180, 820)]:
        ctx, pg = new(b, W, H, True)
        for h_, sels in [('/CONS/_jb', ['.chip.refc .link', '.qc .qhead .chip.lec']), ('/CONS/_led', ['.pggrid .btn.sm'])]:
            go(pg, h_)
            for s in sels:
                r = pg.evaluate(Q, s)
                ok(r and all(x[1] >= 44 and x[0] >= 44 for x in r), f'F3 {W} {h_} {s} 44px 이상 {r}')
        ctx.close()
    # ---------- F4 빈칸 모드 형광펜 → 빈칸, 알림 하나 ----------
    print('== F4 형광펜 → 빈칸 알림 하나')
    ctx, pg = new(b, 1280, 900, False); go(pg, '/CONS/WHT/learn')
    li = pg.evaluate("(()=>{const e=document.querySelector('#t-WHT-3 .tbody :is(li,.li)');e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return [r.left+15,r.top+8]})()")
    pg.wait_for_timeout(300); pg.keyboard.press('h')
    pg.mouse.move(li[0], li[1]); pg.mouse.down(); pg.mouse.move(li[0] + 120, li[1], steps=5); pg.mouse.up(); pg.wait_for_timeout(3500)
    pg.keyboard.press('b'); pg.wait_for_timeout(200)
    pg.evaluate("(()=>{const m=document.querySelector('#t-WHT-3 [data-rk=h]');const r=m.getBoundingClientRect();window.__xy=[r.left+r.width/2,r.top+r.height/2]})()")
    xy = pg.evaluate("window.__xy"); pg.mouse.click(xy[0], xy[1]); pg.wait_for_timeout(300)
    t1 = pg.evaluate(TOAST); pg.wait_for_timeout(2600); t2 = pg.evaluate(TOAST)
    c = pg.evaluate("[document.querySelectorAll('#t-WHT-3 [data-rk=h]').length,document.querySelectorAll('#t-WHT-3 [data-rk=b]').length]")
    ok(c[0] == 0 and c[1] >= 1 and '빈칸으로 바꿨어요' in t1 and '덮어썼어요' not in t1 + t2, f'F4 형광펜 → 빈칸 · 알림 하나 {c} {t1!r} {t2!r}')
    ok(not pg.errs, f'F4 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
