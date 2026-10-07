"""ux4f C 회귀 — 오류 재검 범위 C(n 35~60: 정리표·플래시·예상·비교표·한눈표·기출 대장·JB 문제·검색·형광펜).
정리표: 가린 칸 가운데 탭 = 그 칸만(35) · 카드형 비교표도 칸 이름 탭으로 열 가림(38) · 모두 펼치기 ↔ 모두 접기(44) · 돌리면 요약/자세히 막대 자리도(45)
플래시: 긴 카드에서 ◀ n/N ▶ 줄이 알아요/몰라요에 덮이지 않음(36)
예상: J/K 카드 머리가 필터 줄 아래·K 뒤로(37) · 필터 뒤 강의 머리 숨김·수(41) · 약물 예상 강의 순서 = 메뉴(43)
한눈표·비교표: 붙는 막대 한 줄 칩·범례는 막대 밖(39) · 2회↑만 새로고침 뒤 칩 수(40) · 기출 대장 열 머리 붙음(42)
JB: 미니 막대 넘침 없음(48) · 회차 밖 문항으로 가면 회차·필터·위치 그대로(46) · 회차 중 검색은 Enter에 한 번(47) · 한 장씩 아래 막대에 ✎ 도구·집중 중복 없음(50)
    · 목록 Space = 카드 버튼과 같은 열기↔가리기(54) · 미리보기 채점 채움 없음·다시 누르면 지움(53)
검색: 과목 한정 '전체로 넓히기' 작은 글자(51) · ⚡ 안내 글이 조각에 없음(52)
도구: 형광펜이 빈칸을 덮으면 알림·겹치지 않은 조각은 남김(56) · ⚡ 창 바깥 탭 닫힘(57) · 손가락 대상 44px(58) · 빈칸 글자 선택 막음(59)
그 밖: [카드 ▾] 목록 화면 안(55) · 돌아가기 알약 조사 없음(60)
맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def new(b, w, h, touch=False):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch); pg = ctx.new_page(); pg.errs = []; pg.dlg = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    def dl(d):
        pg.dlg.append(d.message[:30]); d.accept()
    pg.on('dialog', dl)
    pg.goto('about:blank'); pg.goto(U + '#/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1');localStorage.setItem('jblhub.v1.tauto','false')")
    return ctx, pg
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
def go(pg, h, wait=700):
    pg.goto('about:blank'); pg.goto(U + h)
    pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(wait)
def reload(pg, wait=800):
    pg.reload(); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(wait)

def tables(b):
    print('== 정리표·비교표 가리기')
    ctx, pg = new(b, 820, 1180, True); go(pg, '#/CONS/WHT/sum')
    el = pg.evaluate("""(()=>{const c=[...document.querySelectorAll('#stage .msum table.mtx td[data-col]')].find(x=>x.offsetParent&&getComputedStyle(x.closest('table')).display!=='table');if(!c)return null;c.scrollIntoView({block:'center'});const r=c.getBoundingClientRect();return [r.left+10,r.top+8,c.dataset.col]})()""")
    ok(el is not None, '820 정리표 카드형')
    if el:
        pg.touchscreen.tap(el[0], el[1]); pg.wait_for_timeout(300)
        n = pg.evaluate(f"document.querySelectorAll('#stage .msum td.cov[data-col=\"{el[2]}\"]').length")
        c = pg.evaluate(f"""(()=>{{const c=[...document.querySelectorAll('#stage .msum td.cov[data-col="{el[2]}"]')][2];c.scrollIntoView({{block:'center'}});const r=c.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}})()""")
        pg.touchscreen.tap(c[0], c[1]); pg.wait_for_timeout(300)
        r = pg.evaluate("[document.querySelectorAll('#stage .msum td.cov').length,document.querySelectorAll('#stage .msum td.covo').length]")
        ok(n > 3 and r == [n, 1], f'35 칸 이름 탭 → 열 가림 {n} · 가린 칸 가운데 탭 → 그 칸만 열림 {r}')
    # 44
    pg.evaluate("document.querySelector('#sumtop [data-sttab=all]').click()"); pg.wait_for_timeout(200)
    t1 = pg.evaluate("document.querySelector('#sumtop [data-sttab=all]').textContent")
    pg.evaluate("document.querySelector('#sumtop [data-sttab=all]').click()"); pg.wait_for_timeout(200)
    t2 = pg.evaluate("document.querySelector('#sumtop [data-sttab=all]').textContent")
    ok(t1 == '모두 접기' and t2 == '모두 펼치기', f'44 전체정리표 모두 펼치기 ↔ 모두 접기 {t1}/{t2}')
    # 38 카드형 비교표
    go(pg, '#/PHARM/XE/tbl', 1300)
    r = pg.evaluate("[...document.querySelectorAll('#stage table.cmp')].filter(t=>t.offsetParent).map(t=>getComputedStyle(t).display==='table'?!!(t.querySelector('thead .coveye')&&t.querySelector('thead .coveye').getBoundingClientRect().width>0):'card')")
    ok(r and all(x is True or x == 'card' for x in r), f'38 강의 비교표 820: 표는 👁 보임 · 카드형은 칸 이름 탭 {r}')
    for u in ['#/PHARM/_tbl']:
        go(pg, u, 1300)
        r = pg.evaluate("""(()=>{const t=[...document.querySelectorAll('#stage table.cmp')].find(x=>x.offsetParent&&getComputedStyle(x).display!=='table');if(!t)return null;const c=[...t.querySelectorAll('td[data-col]')][1];c.scrollIntoView({block:'center'});const r=c.getBoundingClientRect();window._t=t;return [r.left+10,r.top+8]})()""")
        ok(r is not None, f'38 {u} 820 카드형 비교표 있음')
        if not r: continue
        pg.wait_for_timeout(300)
        pg.touchscreen.tap(r[0], r[1]); pg.wait_for_timeout(300)
        n = pg.evaluate("_t.querySelectorAll('td.cov').length")
        c = pg.evaluate("(()=>{const c=[..._t.querySelectorAll('td.cov')][1]||_t.querySelector('td.cov');c.scrollIntoView({block:'center'});const r=c.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()") if n else None
        if c: pg.touchscreen.tap(c[0], c[1]); pg.wait_for_timeout(300)
        r2 = pg.evaluate("[_t.querySelectorAll('td.cov').length,_t.querySelectorAll('td.covo').length]")
        ok(n >= 2 and r2 == [n, 1], f'38 {u} 칸 이름 탭 → 열 가림 {n} · 가운데 탭 → 그 칸만 {r2}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # 45 돌리기
    ctx, pg = new(b, 1180, 820, True); go(pg, '#/CONS/WHT/sum')
    F = "(()=>{const mb=document.querySelector('#stage #msbar'),tp=document.querySelector('#stage #sumtop');return !!(mb.compareDocumentPosition(tp)&4)})()"
    a = pg.evaluate(F)
    pg.set_viewport_size({'width': 820, 'height': 1180}); pg.wait_for_timeout(900); c = pg.evaluate(F)
    pg.set_viewport_size({'width': 1180, 'height': 820}); pg.wait_for_timeout(900); d = pg.evaluate(F)
    ok(a is False and c is True and d is False, f'45 요약/자세히 막대 자리 1180 뒤 → 820 맨 위 → 1180 뒤 {a},{c},{d}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()

def flash(b):
    print('== 플래시카드')
    for w, h, t in [(1180, 820, True), (1280, 900, False)]:
        ctx, pg = new(b, w, h, t); go(pg, '#/OMS1/DD1/flash'); bad = []; n = pg.evaluate("document.querySelectorAll('#fc').length")
        for i in range(84):
            r = pg.evaluate("(()=>{const a=document.querySelector('.fcctl'),j=document.querySelector('.fcjudge');if(!a||!j)return null;const A=a.getBoundingClientRect(),B=j.getBoundingClientRect(),p=document.querySelector('#fprev').getBoundingClientRect();const e=document.elementFromPoint(p.left+p.width/2,p.top+p.height/2);return [Math.round(A.bottom),Math.round(B.top),e&&e.id,Math.round(A.bottom)<=innerHeight]})()")
            if not r: break
            if r[0] > r[1] + 1 or r[2] != 'fprev' or not r[3]: bad.append((i, r))
            pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(25)
        ok(n == 1 and not bad, f'36 {w} 모든 카드에서 ◀ ▶ 줄이 화면 안·판정 줄 위·누를 수 있음 {bad[:2]}')
        ok(not pg.errs, f'{w} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()

def pred(b):
    print('== 예상문제')
    for w, h, t, u in [(1280, 900, False, '#/CONS/_pred'), (820, 1180, True, '#/CONS/_pred'), (1180, 820, True, '#/CONS/WHT/pred')]:
        ctx, pg = new(b, w, h, t); go(pg, u); out = []
        for k in 'jjjkk':
            pg.keyboard.press(k); pg.wait_for_timeout(450)
            out.append(pg.evaluate("(()=>{const L=[...document.querySelectorAll('#stage .pc')];const c=document.querySelector('#stage .pc.rcur');const pp=document.querySelector('#ppills').getBoundingClientRect();return [L.indexOf(c),c?Math.round(c.getBoundingClientRect().top-pp.bottom):-99]})()"))
        ok([x[0] for x in out] == [0, 1, 2, 1, 0] and all(x[1] >= 0 for x in out), f'37 {w} {u} J J J K K 순서·카드 머리가 필터 줄 아래 {out}')
        ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/_pred')
    pg.click('#ppills [data-ptype=n]'); pg.wait_for_timeout(300)
    r = pg.evaluate("[...document.querySelectorAll('#stage h3.pgh')].map(h=>{let n=0,e=h.nextElementSibling;while(e&&!e.matches('h3.pgh')){if(e.matches('.pc')&&getComputedStyle(e).display!=='none')n++;e=e.nextElementSibling;}return [h.hidden,n,(h.querySelector('.pgn')||{}).textContent]})")
    ok(all((x[0] == (x[1] == 0)) and (x[1] == 0 or x[2].startswith(f'· {x[1]} /') or x[2] == f'· {x[1]}문항') for x in r), f'41 미출제 필터 뒤 강의 머리 수 = 보이는 문항 {r[:3]}')
    pg.click('#ppills [data-pf=ng]'); pg.wait_for_timeout(700)
    r = pg.evaluate("[document.querySelectorAll('#stage h3.pgh:not([hidden])').length,!!document.querySelector('#predempty')]")
    ok(r == [0, True], f'41 틀린 것(0) → 강의 머리 모두 숨김·안내 {r}')
    go(pg, '#/PHARM/_pred')
    hs = pg.evaluate("[...document.querySelectorAll('#stage h3.pgh')].map(h=>h.textContent)")
    lec = pg.evaluate("__h.PACKS.PHARM.lect.map(L=>L.k)")
    ks = pg.evaluate("(()=>{const P=__h.PACKS.PHARM;return [...document.querySelectorAll('#stage h3.pgh')].map(h=>{const t=h.firstChild.textContent.trim();const L=P.lect.find(L=>t.startsWith((L.title||'').slice(0,6)));return L&&L.k;})})()")
    ok(ks == [k for k in lec if k in ks] and len(ks) == 7 and None not in ks, f'43 약물 예상 강의 순서 = 메뉴 순서 {ks} / {lec}')
    first = pg.evaluate("(()=>{const h=document.querySelector('#stage h3.pgh');let e=h.nextElementSibling;return e&&e.matches('.pc')})()")
    ok(first, '43 강의 머리 바로 아래 그 강의 문항')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()

def sumtbl(b):
    print('== 한눈표·비교표·기출 대장')
    for w, h, t in [(820, 1180, True), (1180, 820, True), (1280, 900, False)]:
        ctx, pg = new(b, w, h, t)
        for u, sel, lim in [('#/CONS/_sum', '#sumbar', 120), ('#/CONS/_tbl', '#tbltoc', 70)]:
            go(pg, u); pg.evaluate("scrollTo(0,1500)"); pg.wait_for_timeout(400)
            r = pg.evaluate(f"(()=>{{const e=document.querySelector('{sel}');const r=e.getBoundingClientRect();const L=e.querySelector('.sbl,.ttc');return [Math.round(r.height),getComputedStyle(e).position,!!e.querySelector('.sleg'),L.scrollWidth>L.clientWidth?'scroll':'fit',[...L.querySelectorAll('.tg')].every(b=>b.scrollWidth<=b.clientWidth+1)]}})()")
            ok(r[0] <= lim and r[1] == 'sticky' and not r[2] and r[4], f'39 {w} {u} 붙는 막대 높이 {r[0]} ≤ {lim} · 범례 밖 · 칩 이름 안 잘림 {r}')
        go(pg, '#/CONS/_sum')
        ok(pg.evaluate("!!document.querySelector('#stage .sleg.slego')&&document.querySelector('#stage .sleg').offsetParent!==null"), f'39 {w} 한눈표 범례는 막대 아래에 그대로 보임')
        # 42 기출 대장
        go(pg, '#/CONS/_led')
        pg.evaluate("""(()=>{document.querySelectorAll('#stage details').forEach(d=>d.open=true)})()"""); pg.wait_for_timeout(500)
        pg.evaluate("""(()=>{const t=[...document.querySelectorAll('#stage table.led')].sort((a,b)=>b.offsetHeight-a.offsetHeight)[0];const r=t.getBoundingClientRect();scrollTo(0,scrollY+r.top+r.height/2-300)})()"""); pg.wait_for_timeout(400)
        r = pg.evaluate("""(()=>{const t=[...document.querySelectorAll('#stage table.led')].sort((a,b)=>b.offsetHeight-a.offsetHeight)[0];const h=t.querySelector('thead th');return [Math.round(h.getBoundingClientRect().top),Math.round(t.getBoundingClientRect().top),t.offsetHeight]})()""")
        ok(r[2] > 800 and r[1] < -300 and 40 <= r[0] <= 170, f'42 {w} 기출 대장 긴 표 가운데서 열 머리가 위 막대 아래에 붙음 {r}')
        ok(not pg.errs, f'{w} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/_sum')
    CH = "[...document.querySelectorAll('#sumbar [data-sgo] b')].map(x=>x.textContent).join(',')"
    a = pg.evaluate(CH); pg.click('#stage [data-filt=rep]'); pg.wait_for_timeout(300); b2 = pg.evaluate(CH)
    reload(pg); c = pg.evaluate(CH)
    ok(a != b2 and b2 == c, f'40 2회↑만 새로고침 뒤 칩 수 그대로 {a} → {b2} → {c}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()

def jb(b):
    print('== JB 문제')
    ctx, pg = new(b, 1180, 820, True); go(pg, '#/CONS/_jb')
    pg.evaluate("(()=>{const s=document.querySelector('#fyr');s.value=[...s.options].find(o=>/24/.test(o.value)).value;s.dispatchEvent(new Event('change',{bubbles:true}))})()"); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelector('#fone').click()"); pg.wait_for_timeout(400)
    ST = "[document.querySelector('#opos').textContent,__h.JB.sess.ids&&__h.JB.sess.ids.length,__h.JB.F.yr,(__h.JB.vis[__h.JB.cur]||{dataset:{}}).dataset.id,document.querySelector('#fyr').value]"
    s0 = pg.evaluate(ST); out = pg.evaluate("__h.JB.sess.ids.indexOf('Q07')<0")
    pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(300)
    pg.evaluate("__h.revealCard(document.querySelector('#cards .qc[data-id=\"Q07\"]'))"); pg.wait_for_timeout(400)
    s1 = pg.evaluate(ST); vis = pg.evaluate("getComputedStyle(document.querySelector('#cards .qc[data-id=\"Q07\"]')).display!=='none'")
    pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(300); s2 = pg.evaluate(ST)
    pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(300); s3 = pg.evaluate(ST)
    reload(pg); s4 = pg.evaluate(ST)
    ok(out and s1[0] == '회차 밖' and s1[3] == 'Q07' and vis and s1[1] == 12 and s1[2] == '24', f'46 회차 밖 Q07 → 그 카드만(회차·연도 그대로) {s0} → {s1}')
    ok(s2[:3] == ['2/12', 12, '24'] and s3[0] == '3/12' and s4[0] == '3/12' and s4[4] == '24', f'46 ▶ → 회차 자리로·새로고침 뒤 위치·연도 그대로 {s2} {s3} {s4}')
    if not pg.evaluate("!!document.querySelector('#fq').offsetParent"): pg.evaluate("document.querySelector('#fexp').click()"); pg.wait_for_timeout(200)
    ok(pg.evaluate("!!document.querySelector('#fq').offsetParent"), '47 검색 칸 보임')
    pg.dlg.clear(); pg.focus('#fq'); pg.keyboard.type('re', delay=40); pg.wait_for_timeout(3300); pg.keyboard.type('s', delay=40); pg.wait_for_timeout(300)
    t1 = [len(pg.dlg), pg.evaluate(ST)]
    pg.keyboard.press('Enter'); pg.wait_for_timeout(400); t2 = [len(pg.dlg), pg.evaluate(ST)]
    ok(t1[0] == 0 and t1[1][1] == 12 and t2[0] == 1 and t2[1][1] != 12, f'47 회차 중 검색: 글자마다 확인창·새 회차 없음 → Enter에 한 번 {t1} {t2}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    for w, h, t in [(820, 1180, True), (1280, 900, False)]:
        ctx, pg = new(b, w, h, t); go(pg, '#/CONS/_jb'); pg.evaluate("document.querySelector('#fone').click()"); pg.wait_for_timeout(300); pg.keyboard.press('v'); pg.wait_for_timeout(500)
        r = pg.evaluate("[document.body.classList.contains('focus'),[...document.querySelectorAll('[data-kitt],.dfoc')].filter(x=>x.offsetParent).length,[...document.querySelectorAll('#onebar .otool button')].filter(x=>x.offsetParent).map(x=>x.textContent).join('')]")
        ok(r[0] and r[1] == 2 and r[2] == '🖍▣', f'50 {w} 한 장씩+집중: ✎ 도구·집중 버튼은 한 벌 · 아래 막대엔 🖍 ▣만 {r}')
        pg.keyboard.press('t'); pg.wait_for_timeout(200); pg.evaluate("document.querySelector('#okh').click()"); pg.wait_for_timeout(200)
        r = pg.evaluate("[document.body.classList.contains('kit-off'),document.body.classList.contains('mode-h'),getComputedStyle(document.querySelector('#kit')).display]")
        ok(r[0] is False and r[1] and r[2] != 'none', f'50 {w} 막대를 숨긴 채 🖍 → 막대도 보임 {r}')
        ok(not pg.errs, f'{w} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    for w, h, t in [(820, 1180, True), (1180, 820, True), (1280, 900, False)]:
        ctx, pg = new(b, w, h, t); go(pg, '#/OMS1/_jb/_jb'); pg.evaluate("scrollTo(0,2500)"); pg.wait_for_timeout(700)
        r = pg.evaluate("(()=>{const bar=document.querySelector('#jbbar'),b1=bar.querySelector('.b1');const R=e=>e&&e.offsetParent?e.getBoundingClientRect():null;const a=R(document.querySelector('#frev')),n=R(document.querySelector('#fnow'));return [bar.classList.contains('mini'),b1.scrollWidth-b1.clientWidth,!!(a&&n&&n.left<a.right)]})()")
        ok(r[0] and r[1] <= 1 and not r[2], f'48 {w} JB 미니 막대 가로 넘침·[답 펼치기] 가림 없음 {r}')
        ctx.close()
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/_jb')
    pg.keyboard.press('j'); pg.wait_for_timeout(300)
    LB = "(()=>{const c=document.querySelector('#cards .qc[data-id=Q01]');return [c.classList.contains('open'),c.classList.contains('deep'),c.querySelector('.acts:not(.acts2) [data-tog]').textContent]})()"
    seq = []
    for i in range(3): pg.keyboard.press(' '); pg.wait_for_timeout(250); seq.append(pg.evaluate(LB))
    for i in range(3): pg.evaluate("document.querySelector('#cards .qc[data-id=Q01] .acts:not(.acts2) [data-tog]').click()"); pg.wait_for_timeout(250); seq.append(pg.evaluate(LB))
    want = [[True, False, '답 가리기 ▲'], [False, False]] * 3
    ok(all(s[:len(w_)] == w_ for s, w_ in zip(seq, want)) and seq[1][2] == seq[3][2] and '가리기' not in seq[1][2], f'54 목록: Space·카드 버튼 모두 열기 ↔ 가리기(글자 = 다음 동작) {seq}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()

def peek_search(b):
    print('== 미리보기·검색·돌아가기')
    ctx, pg = new(b, 1180, 820, True); go(pg, '#/CONS/CRK/learn')
    pg.evaluate("(()=>{const c=document.querySelector('#stage .c-exam .jbchip[data-go]');c.scrollIntoView({block:'center'});c.click()})()"); pg.wait_for_timeout(300)
    F = "(()=>{const b=document.querySelector('#jbpeek [data-jpmk=ok]');return [b.classList.contains('on'),getComputedStyle(b).backgroundColor]})()"
    pg.click('#jbpeek [data-jpmk=ok]'); pg.wait_for_timeout(200); a = pg.evaluate(F)
    pg.click('#jbpeek [data-jpmk=ok]'); pg.wait_for_timeout(200); c = pg.evaluate(F)
    ok(a[0] and a[1] in ('rgb(255, 255, 255)', 'rgba(0, 0, 0, 0)') or (a[0] and 'rgb(240, 245, 240)' != a[1]), f'53 미리보기 ✓ 맞음 켜짐 = 채움 없음 {a}')
    ok(not c[0], f'53 다시 누르면 기록 지움 {c}')
    # 60
    pg.evaluate("(()=>{const c=document.querySelector('#jbpeek [data-jpgo]');c.click()})()"); pg.wait_for_timeout(1200)
    pill = pg.evaluate("(document.querySelector('#retpill')||{}).textContent||''")
    ok(pill.startswith('↩ 돌아가기 · ') and '로 돌아가기' not in pill, f'60 돌아가기 알약 조사 없음 {pill!r}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    for w, h, t in [(820, 1180, True), (1280, 900, False)]:
        ctx, pg = new(b, w, h, t); go(pg, '#/CONS/_jb')
        pg.keyboard.press('/'); pg.wait_for_timeout(200); pg.keyboard.type('bleaching'); pg.keyboard.press('Enter'); pg.wait_for_timeout(2500)
        r = pg.evaluate("(()=>{const s=document.querySelector('.shead h2 .swide'),h=document.querySelector('.shead h2');return s&&[parseFloat(getComputedStyle(s).fontSize),parseFloat(getComputedStyle(h).fontSize)]})()")
        ok(r and r[0] <= 15 and r[0] < r[1], f'51 {w} 전체로 넓히기 링크 작은 글자 {r}')
        ok(pg.evaluate("document.querySelector('#home').innerText.length>200&&!document.querySelector('#home').innerText.includes('빨간 글씨를 자동 빈칸으로')"), f'52 {w} 검색 조각에 ⚡ 안내 글 없음')
        ok(not pg.errs, f'{w} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()

def tools_(b):
    print('== 도구(형광펜·빈칸·창·터치)')
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/WHT/learn')
    # 56 빈칸 위로 형광펜
    r = pg.evaluate("""(()=>{const K=__h.Kit;const B=[...document.querySelectorAll('#stage .tc li')].find(x=>x.offsetParent&&x.textContent.length>50&&!x.querySelector('[data-rk],img'));window._B=B;return B&&B.textContent.length})()""")
    ok(r and r > 40, f'56 대상 블록 {r}')
    s = pg.evaluate("""(()=>{const K=__h.Kit;if(!K.applyRange)return 'noapi';})()""")
    # 화면 조작(선택 → 모드 적용)으로: 빈칸 모드에서 낱말 하나, 형광펜 모드에서 그 줄 앞부터 빈칸 뒤까지
    def sel(a, z):
        pts = pg.evaluate(f"""(()=>{{const B=_B;const w=document.createTreeWalker(B,NodeFilter.SHOW_TEXT);let n,p=0;const at=(o)=>{{const w=document.createTreeWalker(B,NodeFilter.SHOW_TEXT);let n,p=0;while(n=w.nextNode()){{const L=n.nodeValue.length;if(p+L>o){{const r=document.createRange();r.setStart(n,o-p);r.setEnd(n,o-p+1);return r.getBoundingClientRect();}}p+=L;}}}};const A=at({a}),Z=at({z}-1);return [A.left+1,A.top+A.height/2,Z.right-1,Z.top+Z.height/2]}})()""")
        pg.mouse.move(pts[0], pts[1]); pg.mouse.down(); pg.mouse.move((pts[0]+pts[2])/2, (pts[1]+pts[3])/2, steps=4); pg.mouse.move(pts[2], pts[3], steps=4); pg.mouse.up(); pg.wait_for_timeout(300)
    pg.evaluate("_B.scrollIntoView({block:'center'})"); T0 = pg.evaluate("_B.textContent")   # 10-07 내용이 바뀌어도 되게 — 글자는 이 블록에서 계산
    pg.keyboard.press('b'); pg.wait_for_timeout(150); sel(10, 26)
    nb = pg.evaluate("_B.querySelectorAll('[data-rk=b]').length")
    pg.keyboard.press('b'); pg.keyboard.press('h'); pg.wait_for_timeout(150); sel(0, 13)
    r = pg.evaluate("[_B.querySelectorAll('[data-rk=b]').length,_B.querySelectorAll('[data-rk=h]').length,(_B.querySelector('[data-rk=b]')||{}).textContent,document.querySelector('#toast').innerText]")
    ok(nb >= 1 and r[0] >= 1 and r[1] >= 1 and '덮어썼어요' in r[3] and len((r[2] or '').strip()) >= 2, f'56 빈칸 일부를 형광펜으로 덮으면 알림 · 겹치지 않은 빈칸 조각은 남음 {nb} → {r}')
    pg.keyboard.press('h'); pg.wait_for_timeout(100)
    reload(pg)
    r2 = pg.evaluate("(()=>{const B=[...document.querySelectorAll('#stage .tc li')].find(x=>x.textContent.startsWith(%s));return B?[B.querySelectorAll('[data-rk=b]').length,B.querySelectorAll('[data-rk=h]').length,(B.querySelector('[data-rk=b]')||{}).textContent]:null})()" % __import__("json").dumps(T0[:25]))
    ok(r2 and r2[0] == r[0] and r2[1] == r[1] and r2[2] == r[2], f'56 새로고침 뒤에도 남은 빈칸 조각·형광펜 그대로 {r2}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    for w, h in [(1180, 820), (820, 1180)]:
        ctx, pg = new(b, w, h, True); go(pg, '#/CONS/WHT/learn')
        pg.click('#lmcur'); pg.wait_for_timeout(300)
        r = pg.evaluate("(()=>{const p=document.querySelector('#lpop');p.scrollTop=1e5;const L=[...p.querySelectorAll('.lpi')];const l=L[L.length-1].getBoundingClientRect();return [Math.round(p.getBoundingClientRect().bottom),Math.round(l.bottom),innerHeight]})()")
        ok(r[0] <= r[2] and r[1] <= r[2], f'55 {w} [카드 ▾] 목록 끝 카드가 화면 안 {r}')
        pg.click('#lmcur'); pg.wait_for_timeout(200)
        pg.click('#k-auto'); pg.wait_for_timeout(200)
        on = pg.evaluate("document.querySelector('#autopop').classList.contains('on')")
        pg.touchscreen.tap(w // 2 + 100, 140); pg.wait_for_timeout(250)
        ok(on and not pg.evaluate("document.querySelector('#autopop').classList.contains('on')"), f'57 {w} ⚡ 창 바깥 탭 → 닫힘')
        m = pg.evaluate("""(()=>{const R=s=>[...document.querySelectorAll(s)].filter(x=>x.offsetParent).map(x=>{const r=x.getBoundingClientRect();return [s,Math.round(r.width),Math.round(r.height)]});return [].concat(R('#dtabs .dfoc'),R('#k-swc'),R('#k-bswc'),R('#stage details>summary:not(.tg)'))})()""")
        small = [x for x in m if x[2] < 44 or (x[0] != '#stage details>summary:not(.tg)' and x[1] < 44)]
        ok(len(m) >= 4 and not small, f'58 {w} 손가락 대상 44px 이상 {small or len(m)}')
        us = pg.evaluate("(()=>{const s=document.createElement('span');s.className='rk-b';document.querySelector('#stage .tc').appendChild(s);const v=getComputedStyle(s).userSelect||getComputedStyle(s).webkitUserSelect;s.remove();return v})()")
        ok(us == 'none', f'59 {w} 터치 기기 빈칸 글자 선택 막음 {us}')
        ok(not pg.errs, f'{w} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()

with sync_playwright() as p:
    b = p.chromium.launch()
    for f in (tables, flash, pred, sumtbl, jb, peek_search, tools_):
        if len(_sys.argv) > 1 and f.__name__ not in _sys.argv[1:]: continue
        try: f(b)
        except Exception as e: ok(False, f'{f.__name__} 예외 {str(e)[:300]}')
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
