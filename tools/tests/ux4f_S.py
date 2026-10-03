"""ux4f S 회귀 — 10-04 허브 점검 2차 NAV(오류 5 + 개선) · QUIZ(오류 3)
N1 검색 결과 → 뒤로 → ✕ 닫기/Esc = '검색 전 화면'(방금 본 결과 문서가 아니라)
N2 학습 탭 인쇄 전(beforeprint · print 미디어) 늦게 넣는 카드 그림을 모두 채움
N3 390 폰: 빵부스러기 한 줄(한 글자 폭으로 눌리지 않음) · 상단 막대 낮음 · 도구 막대 화면 안 · 과목 JB·비교표 가로 넘침 0
N4 [틀 ▾]·[보기 ▾] 열면 포커스가 목록 안 · ↓ 이동 · Esc = 닫고 버튼으로
N5 200% 확대(640×450·590×410) 탭이 미니바 밑에 깔리지 않음
개선 검색 띄어쓰기 무시('국소 마취' = '국소마취') · 본문으로 건너뛰기(첫 Tab)
Q1 저장한 빈칸 위 가리기(Q) = 두 겹으로 가리지 않음(한 번 누르면 보임)
Q2 플래시카드에서 E는 안내만 · 전체 보기는 탭을 옮기면 꺼짐
Q3 가리기 중 H로 가린 칸을 누르면 칠하지 않고 안내"""
import os as _os, sys as _sys, json; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
TOAST = "(document.querySelector('#toast')||{}).textContent||''"
def new(b, w, h, touch):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch)
    ctx.add_init_script("try{if(!localStorage.getItem('jblhub.v1.whatsNew.4'))localStorage.setItem('jblhub.v1.whatsNew.4','1')}catch(e){}")
    pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    return ctx, pg
def go(pg, h, w=1000):
    pg.goto('about:blank'); pg.goto(U + '#' + h); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(w)
def nres(pg): return pg.evaluate("document.querySelectorAll('#home .sres').length")
def srch(pg, q):
    pg.fill('#gsearch', q); pg.wait_for_function("document.querySelector('#home .sres')&&!document.querySelector('#home .sxw')", timeout=60000); pg.wait_for_timeout(400)
with sync_playwright() as p:
    b = p.chromium.launch(ignore_default_args=['--hide-scrollbars'])
    # ---------- 1280 마우스: N1 · 띄어쓰기 · N2 · N4 · 건너뛰기 · Q1~Q3 ----------
    ctx, pg = new(b, 1280, 900, False)
    for start, want in (('/PHARM/RX/learn', '#/PHARM/RX/learn'), ('/', '#/')):
        for how in ('x', 'esc'):
            go(pg, start); srch(pg, '처방')
            pg.evaluate("[...document.querySelectorAll('#home .sres')].find(r=>r.dataset.d!=='RX'&&r.dataset.d[0]!=='_').click()"); pg.wait_for_timeout(1200)
            h1 = pg.evaluate("location.hash"); pg.go_back(); pg.wait_for_timeout(1200)
            back = pg.evaluate("location.hash").startswith('#/?q=')
            if how == 'x': pg.click('#sclose')
            else: pg.focus('#gsearch'); pg.keyboard.press('Escape')
            pg.wait_for_timeout(1200); h2 = pg.evaluate("location.hash")
            ok(back and (h2 == want or h2.startswith(want + '/') or (want == '#/' and h2 in ('#/', ''))) and h2 != h1, f'N1 {start} 결과({h1}) → 뒤로 → {how} = 검색 전 화면 {h2}')
    go(pg, '/'); srch(pg, '국소마취'); n0 = nres(pg); lead0 = pg.inner_text('#home .lead')
    srch(pg, '국소 마취'); n1 = nres(pg); lead1 = pg.inner_text('#home .lead')
    mk = pg.evaluate("[...document.querySelectorAll('#home .sres mark')].slice(0,40).map(m=>m.textContent.replace(/\\s/g,'')).every(t=>t==='국소마취')")
    ok(n0 > 0 and lead1.split('건')[0] >= lead0.split('건')[0] and n1 > 0 and mk, f"검색 띄어쓰기 무시 '국소마취' {lead0.split('—')[0]} · '국소 마취' {lead1.split('—')[0]} · <mark> 원문 위치 {mk}")
    srch(pg, '처방'); ok(pg.inner_text('#home .lead').split('건')[0].strip().isdigit(), "공백 없는 검색은 그대로")
    pg.keyboard.press('Escape'); pg.wait_for_timeout(500)
    # N2
    go(pg, '/ESTH/FUN/learn', 1500)
    r0 = pg.evaluate("[document.querySelectorAll('#stage .tc .figs img').length,[...document.querySelectorAll('#stage .tc .figs img')].filter(i=>!i.getAttribute('src')).length]")
    pg.evaluate("dispatchEvent(new Event('beforeprint'))"); pg.wait_for_timeout(300)
    r1 = pg.evaluate("[...document.querySelectorAll('#stage .tc .figs img')].filter(i=>!i.getAttribute('src')).length")
    pg.evaluate("dispatchEvent(new Event('afterprint'))")
    ok(r0[0] > 10 and r0[1] > 0 and r1 == 0, f'N2 beforeprint → 카드 그림 모두 채움 (그림 {r0[0]} · 빈 {r0[1]} → {r1})')
    go(pg, '/OMS1/DD1/learn', 1500); e0 = pg.evaluate("[...document.querySelectorAll('#stage .tc .figs img')].filter(i=>!i.getAttribute('src')).length")
    pg.emulate_media(media='print'); pg.wait_for_timeout(400)
    e1 = pg.evaluate("[...document.querySelectorAll('#stage .tc .figs img')].filter(i=>!i.getAttribute('src')).length")
    bm = pg.evaluate("[...document.querySelectorAll('#stage .cbend')].filter(e=>e.offsetParent).length")
    pg.emulate_media(media='screen'); pg.wait_for_timeout(200)
    ok(e0 > 0 and e1 == 0 and bm == 0, f'N2 print 미디어 → 그림 채움 ({e0} → {e1}) · ☆ 북마크 인쇄 안 함 {bm}')
    # N4
    for trig, pop, item in (('#lmcur', '#lpop', '.lpi'), ('#lmview', '#lvpop', '.pi')):
        go(pg, '/ESTH/FUN/learn', 1200); pg.focus(trig); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
        a1 = pg.evaluate(f"[document.querySelector('{pop}').classList.contains('on'),!!document.activeElement.closest('{pop}'),document.activeElement.matches('{item}')]")
        i1 = pg.evaluate(f"[...document.querySelectorAll('{pop} {item}')].indexOf(document.activeElement)")
        pg.keyboard.press('ArrowDown'); pg.wait_for_timeout(100)
        i2 = pg.evaluate(f"[...document.querySelectorAll('{pop} {item}')].indexOf(document.activeElement)")
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        a3 = pg.evaluate(f"[document.querySelector('{pop}').classList.contains('on'),document.activeElement.id]")
        ok(a1 == [True, True, True] and i2 != i1 and i2 >= 0 and a3 == [False, trig[1:]], f'N4 {trig} Enter → 목록 안 포커스 {a1} · ↓ {i1}→{i2} · Esc 닫고 버튼으로 {a3}')
    go(pg, '/ESTH/FUN/learn', 1200); pg.click('#lmcur'); pg.wait_for_timeout(300); pg.keyboard.press('ArrowDown'); pg.keyboard.press('Enter'); pg.wait_for_timeout(900)
    ok(pg.evaluate("[document.querySelector('#lpop').classList.contains('on'),document.activeElement.id]") == [False, 'lmcur'], 'N4 카드 고르면 닫히고 포커스는 [틀 ▾]')
    # 건너뛰기
    go(pg, '/ESTH/FUN/learn', 1000); pg.evaluate("document.activeElement&&document.activeElement.blur()"); pg.keyboard.press('Tab')
    s1 = pg.evaluate("[document.activeElement.id,Math.round(document.activeElement.getBoundingClientRect().width)]")
    pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    s2 = pg.evaluate("document.activeElement.id"); pg.keyboard.press('Tab'); s3 = pg.evaluate("!!document.activeElement.closest('#stage')")
    hid = pg.evaluate("(()=>{document.activeElement.blur();return Math.round(document.querySelector('#skipb').getBoundingClientRect().width)})()")
    ok(s1[0] == 'skipb' and s1[1] > 60 and s2 == 'stage' and s3 and hid <= 1, f'본문으로 건너뛰기 첫 Tab {s1} → Enter {s2} → 다음 Tab 본문 {s3} · 평소 숨김 {hid}')
    # Q1 — 저장 빈칸 위 가리기
    go(pg, '/OMS1/DD1/learn', 1200)
    aid = pg.evaluate("""(()=>{const c=[...document.querySelectorAll('#stage .tc')].find(c=>[...c.querySelectorAll('.k')].filter(k=>k.closest('[data-aid]')===c&&!k.closest('.noann,button')).length>=4);
      const ks=[...c.querySelectorAll('.k')].filter(k=>k.closest('[data-aid]')===c&&!k.closest('.noann,button')).slice(0,2),cnt={};const A={};A[c.dataset.aid]=ks.map(k=>{const x=k.textContent.trim();cnt[x]=(cnt[x]||0)+1;return {t:'b',x,i:cnt[x]-1};});
      localStorage.setItem('jblhub.v1.ann.OMS1',JSON.stringify(A));return c.dataset.aid})()""")
    go(pg, '/OMS1/DD1/learn', 600); pg.evaluate("aid=>__h.openDoc('OMS1','DD1','learn',aid)", aid); pg.wait_for_timeout(700)
    pg.keyboard.press('q'); pg.wait_for_timeout(400)
    r = pg.evaluate("aid=>{const c=document.querySelector('#stage .tc[data-aid=\"'+aid+'\"]');return [__h.QZ.on,c.querySelectorAll('[data-rk=b]').length,[...c.querySelectorAll('.k.qzk')].filter(k=>k.closest('[data-rk=b]')||k.querySelector('[data-rk=b]')).length,c.querySelectorAll('.k.qzk').length]}", aid)
    ok(r[0] and r[1] > 0 and r[2] == 0 and r[3] > 0, f'Q1 저장 빈칸 안 빨간 글씨는 가리기 대상 아님 (Q {r[0]} · 빈칸 {r[1]} · 겹침 {r[2]} · 가린 칸 {r[3]})')
    pg.evaluate("aid=>document.querySelector('#stage .tc[data-aid=\"'+aid+'\"] [data-rk=b]').scrollIntoView({block:'center'})", aid); pg.wait_for_timeout(300)
    bx = pg.evaluate("aid=>{const e=document.querySelector('#stage .tc[data-aid=\"'+aid+'\"] [data-rk=b]');const q=e.getBoundingClientRect();return [q.left+Math.min(8,q.width/2),q.top+q.height/2]}", aid)
    pg.mouse.click(bx[0], bx[1]); pg.wait_for_timeout(300)
    r = pg.evaluate("aid=>{const e=document.querySelector('#stage .tc[data-aid=\"'+aid+'\"] [data-rk=b]');return [e.classList.contains('show'),[...e.querySelectorAll('.k')].map(k=>getComputedStyle(k).color).join()]}", aid)
    ok(r[0] and 'rgba(0, 0, 0, 0)' not in r[1], f'Q1 한 번 누르면 빈칸 글자가 보임 {r}')
    # Q3 — 가리기 중 H로 가린 칸
    a0 = pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')")
    k = pg.evaluate("aid=>{const k=document.querySelector('#stage .tc[data-aid=\"'+aid+'\"] .k.qzk:not(.show)');if(!k)return null;k.scrollIntoView({block:'center'});const q=k.getBoundingClientRect();return [q.left+q.width/2,q.top+q.height/2]}", aid)
    pg.wait_for_timeout(200); pg.keyboard.press('h'); pg.wait_for_timeout(200)
    if k:
        k = pg.evaluate("aid=>{const k=document.querySelector('#stage .tc[data-aid=\"'+aid+'\"] .k.qzk:not(.show)');const q=k.getBoundingClientRect();return [q.left+q.width/2,q.top+q.height/2]}", aid)
        pg.mouse.click(k[0], k[1]); pg.wait_for_timeout(400)
    a1 = pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')"); t3 = pg.evaluate(TOAST)
    A0, A1 = json.loads(a0 or '{}'), json.loads(a1 or '{}')
    ok(k and A0 == A1 and '가린 칸' in t3, f'Q3 H 모드로 가린 칸 누름 → 저장 안 함 · 안내 {t3[:30]!r} {A0 if A0 != A1 else ""} {A1 if A0 != A1 else ""}')
    pg.keyboard.press('h'); pg.keyboard.press('q'); pg.wait_for_timeout(200)
    # Q2 — 플래시카드 E
    go(pg, '/OMS1/DD1/flash', 1000); pg.keyboard.press('e'); pg.wait_for_timeout(300)
    r = pg.evaluate("[document.body.classList.contains('rk-reveal')," + TOAST + "]")
    ok(not r[0] and '플래시카드' in r[1], f'Q2 플래시카드 E = 전체 보기 안 켬 · 안내 {r[1][:30]!r}')
    go(pg, '/OMS1/DD1/learn', 800); sh0 = pg.evaluate("document.querySelectorAll('#stage [data-rk=b].show').length"); pg.keyboard.press('e'); pg.wait_for_timeout(200); on1 = pg.evaluate("document.body.classList.contains('rk-reveal')")
    pg.keyboard.press('2'); pg.wait_for_timeout(600); pg.keyboard.press('1'); pg.wait_for_timeout(600)
    r = pg.evaluate("[document.body.classList.contains('rk-reveal'),document.querySelector('#k-eye').classList.contains('on'),document.querySelectorAll('#stage [data-rk=b].show').length]")
    ok(on1 and r == [False, False, sh0], f'Q2 학습 E 켬 {on1} → 탭을 옮겼다 오면 전체 보기 꺼짐 {r}')
    pg.evaluate("localStorage.removeItem('jblhub.v1.ann.OMS1')")
    ok(not pg.errs, f'1280 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # ---------- 390 폰: N3 ----------
    ctx, pg = new(b, 390, 844, True)
    for route in ('/ESTH/FUN/learn', '/ESTH/_home/_home', '/', '/PHARM/_jb', '/ESTH/FUN/tbl', '/CONS/_tbl', '/PHARM/_tbl'):
        go(pg, route, 1200)
        r = pg.evaluate("""[Math.round(document.querySelector('#top').getBoundingClientRect().height),Math.round(document.querySelector('#crumb').getBoundingClientRect().width),Math.round((document.querySelector('#crumb .ccur')||{getBoundingClientRect:()=>({height:0})}).getBoundingClientRect().height),
          document.documentElement.scrollWidth-innerWidth,(()=>{const k=document.querySelector('#kit');if(!k||!k.offsetParent)return 0;return [...k.querySelectorAll('button')].filter(e=>e.offsetParent&&(e.getBoundingClientRect().right>innerWidth+1||e.getBoundingClientRect().left<-1)).length})()]""")
        ok(r[0] <= 100 and r[1] >= 300 and r[2] <= 30 and r[3] <= 0 and r[4] == 0, f'N3 390 {route} 상단 {r[0]}px · 빵부스러기 폭 {r[1]} · 지금 이름 높이 {r[2]} · 가로 넘침 {r[3]} · 도구 막대 밖 버튼 {r[4]}')
    ok(not pg.errs, f'390 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # ---------- 200% 확대: N5 ----------
    for W, H, T in ((640, 450, False), (590, 410, True)):
        ctx, pg = new(b, W, H, T); go(pg, '/ESTH/FUN/learn', 1200)
        r = pg.evaluate("[...document.querySelectorAll('#dtabs button[data-t]')].map(t=>{const q=t.getBoundingClientRect(),e=document.elementFromPoint(q.left+q.width/2,q.top+q.height/2);return [t.dataset.t,!!e&&t.contains(e)&&q.right<=innerWidth]})")
        ov = pg.evaluate("document.documentElement.scrollWidth-innerWidth")
        ok(len(r) == 6 and all(x[1] for x in r) and ov <= 0, f'N5 {W}×{H} 탭 6개 모두 누를 수 있음 {[x[0] for x in r if not x[1]]} · 넘침 {ov}')
        lm = pg.evaluate("(()=>{const q=document.querySelector('#lmcur').getBoundingClientRect(),e=document.elementFromPoint(q.left+q.width/2,q.top+q.height/2);return !!e&&!!e.closest('#lmcur')})()")
        ok(lm, f'N5 {W} [틀 ▾] 그대로 누를 수 있음')
        ok(not pg.errs, f'{W} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
