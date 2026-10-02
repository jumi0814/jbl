"""ux4f O 회귀 — 클라우드 10-02 코드 재검토로 찾은 오류
O1 가린 칸(👁)에 칠해 둔 형광펜: 다른 칸 칠하기 → ⌘Z(다시 그림) → 같은 줄 다시 칠하기 뒤에도 저장에 남고, 새로고침·칸 열기 뒤 보임(전에는 다시 그릴 때 가린 칸 표시를 그리지 않아 다음 저장에서 사라짐)
O2 집중 모드 탭 줄 시계: 정리표에서 눌러도 탭이 바뀌지 않고 시계 창이 화면 안에 열림(전에는 학습 탭으로 가고 창이 화면 밖)
O3 구멍 난 형광펜(가운데 빈칸) 위에 빈칸을 겹쳐 칠해도 원래 빈칸 글자가 형광펜으로 바뀌지 않음
O5 덮어쓰기 알림의 [↶ 되돌리기]는 그 동작만 — 그 뒤 다른 표시를 했으면 엉뚱한 것을 되돌리지 않음
O6 과목 홈 '안 푼 것 n →'이 풀던 한 장씩 회차를 묻지 않고 지우지 않음(취소하면 회차 그대로)
O7 전에 M으로 메뉴를 쓰던 사용자가 M을 먼저 눌러도 '이제 Shift+M' 알림 한 번
O8 다른 기기 합산 시작 전 날짜의 빈 과목('') 기록도 '기타'"""
import os as _os, sys as _sys, json; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
def new(b, w, h, touch):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch)
    ctx.add_init_script("try{if(!localStorage.getItem('jblhub.v1.whatsNew.4'))localStorage.setItem('jblhub.v1.whatsNew.4','1')}catch(e){}")
    pg = ctx.new_page(); pg.errs = []; pg.dlg = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    return ctx, pg
def go(pg, h, w=900):
    pg.goto('about:blank'); pg.goto(U + '#' + h); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(w)
# 칸(td) 안 첫 글자들 [i, j) 화면 좌표 — 드래그용
XY = """([sel,i,j])=>{const c=document.querySelector(sel);if(!c)return null;const w=document.createTreeWalker(c,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement.closest('.noann,.coveye,button')?2:1});const at=k=>{w.currentNode=c;let n;while(n=w.nextNode()){if(k<n.nodeValue.length)return [n,k];k-=n.nodeValue.length;}return null;};
 const A=at(i),Z=at(j-1);if(!A||!Z)return null;const r=document.createRange();r.setStart(A[0],A[1]);r.setEnd(A[0],A[1]+1);const a=r.getClientRects()[0];r.setStart(Z[0],Z[1]);r.setEnd(Z[0],Z[1]+1);const z=r.getClientRects()[0];
 let t='';w.currentNode=c;let n;while(n=w.nextNode())t+=n.nodeValue;return a&&z?[a.left+1,a.top+a.height/2,z.right-1,z.top+z.height/2,t.slice(i,j)]:null}"""
def drag(pg, p):
    pg.mouse.move(p[0], p[1]); pg.mouse.down(); pg.mouse.move(p[2], p[3], steps=8); pg.mouse.up(); pg.wait_for_timeout(450)
ANN = "(aid)=>(JSON.parse(localStorage.getItem('jblhub.v1.ann.CONS')||'{}')[aid]||[]).map(o=>o.x)"
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------- O1 ----------
    ctx, pg = new(b, 1280, 900, False); go(pg, '/'); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); go(pg, '/CONS/_tbl')
    row = pg.evaluate("""(()=>{const t=document.querySelector('#tb-2 table')||document.querySelector('#stage table');const L=[...t.tBodies[0].rows].filter(r=>r.cells.length>=3&&r.cells[1].tagName==='TD'&&r.cells[1].textContent.trim().length>=8&&r.cells[2].textContent.trim().length>=8);const r=L[1]||L[0];r.cells[1].id='o1a';r.cells[2].id='o1b';r.id='o1r';r.scrollIntoView({block:'center'});t.id=t.id||'o1t';return [t.closest('[data-aid]').dataset.aid,t.id,[...t.tBodies[0].rows].indexOf(r)]})()""")
    aid = row[0]; pg.wait_for_timeout(400); pg.keyboard.press('h'); pg.wait_for_timeout(200)
    pa = pg.evaluate(XY, ['#o1a', 0, 4]); drag(pg, pa)
    x0 = pg.evaluate(ANN, aid)
    ok(len(x0) == 1, f'O1 가릴 칸에 형광펜 1개 {x0} ({pa and pa[4]!r})')
    pg.evaluate("(id=>{const t=document.getElementById(id);t.tHead.rows[0].cells[1].querySelector('.coveye').click()})", row[1]); pg.wait_for_timeout(400)
    ok(pg.evaluate("document.querySelector('#o1a').matches('.cov:not(.covo)')"), 'O1 그 열 가림(👁)')
    pg.evaluate("document.querySelector('#o1b').scrollIntoView({block:'center'})"); pg.wait_for_timeout(200)
    pb = pg.evaluate(XY, ['#o1b', 0, 4]); drag(pg, pb)
    pg.keyboard.press('Control+z'); pg.wait_for_timeout(500)
    drawn = pg.evaluate("document.querySelectorAll('#o1a [data-rk]').length")
    pb = pg.evaluate(XY, ['#o1b', 0, 4]); drag(pg, pb)
    x1 = pg.evaluate(ANN, aid)
    ok(drawn >= 1 and x0 and x0[0] in x1 and len(x1) == 2, f'O1 ⌘Z 뒤 같은 줄 다시 칠해도 가린 칸 표시 그대로 저장 {x1} (다시 그림 {drawn})')
    pg.wait_for_timeout(700); pg.reload(); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(900)
    pg.evaluate("([aid,i])=>{const B=[...document.querySelectorAll('#stage [data-aid]')].find(e=>e.dataset.aid===aid);const t=B.querySelector('table');t.tHead.rows[0].cells[1].querySelector('.coveye').click();t.tBodies[0].rows[i].scrollIntoView({block:'center'})}", [aid, row[2]]); pg.wait_for_timeout(500)
    r = pg.evaluate("([aid,i])=>{const B=[...document.querySelectorAll('#stage [data-aid]')].find(e=>e.dataset.aid===aid);const c=B.querySelector('table').tBodies[0].rows[i];return [c.cells[1].matches('.cov:not(.covo)'),[...c.cells[1].querySelectorAll('[data-rk]')].map(e=>e.textContent).join('')]}", [aid, row[2]])
    ok(not r[0] and x0 and r[1] == x0[0], f'O1 새로고침 → 칸 열기 → 형광펜 보임 {r}')
    ok(not pg.errs, f'O1 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # ---------- O2 ----------
    for W, H, T in [(1280, 900, False), (820, 1180, True), (1180, 820, True)]:
        ctx, pg = new(b, W, H, T); go(pg, '/CONS/WHT/sum'); pg.keyboard.press('v'); pg.wait_for_timeout(600)
        h0 = pg.evaluate("location.hash"); fc = pg.evaluate("(f=>f&&[Math.round(f.getBoundingClientRect().height),!!f.closest('#dtabs')])([...document.querySelectorAll('.fclock')].find(x=>x.offsetParent))")
        if T: pg.tap('.fclock')
        else: pg.click('.fclock')
        pg.wait_for_timeout(400)
        r = pg.evaluate("(p=>{const q=p.getBoundingClientRect();return [location.hash,p.classList.contains('on'),q.left>=0&&q.right<=innerWidth&&q.top>=0&&q.bottom<=innerHeight,document.body.classList.contains('focus')]})(document.querySelector('#tpop'))")
        ok(r[0] == h0 and r[1] and r[2] and r[3], f'O2 {W} 집중 모드 정리표 시계 누름 = 탭 그대로·창 화면 안 {h0} → {r}')
        ok(fc and fc[0] >= (44 if T else 30), f'O2 {W} 탭 줄 시계 누름 자리 {fc}')
        ok(not pg.errs, f'O2 {W} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # ---------- O3·O5 (학습 카드) ----------
    ctx, pg = new(b, 1280, 900, False); go(pg, '/'); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); go(pg, '/CONS/WHT/learn')
    li = pg.evaluate("""(()=>{const L=[...document.querySelectorAll('#stage .tc .tbody li')].filter(l=>l.offsetParent&&!l.querySelector('[data-rk],b,i,span,a')&&l.textContent.trim().length>=70&&l.textContent.trim().split(/\s+/).length>=10&&l.textContent===l.textContent.trimStart());const l=L[3]||L[0];l.id='o3';l.scrollIntoView({block:'center'});return l.textContent.trim().slice(0,40)})()""")
    pg.wait_for_timeout(300)
    def marks():
        return pg.evaluate("[...document.querySelectorAll('#o3 [data-rk]')].map(e=>e.dataset.rk+':'+e.textContent)")
    aid3 = pg.evaluate("document.querySelector('#o3').closest('[data-aid]').dataset.aid")
    full = pg.evaluate("document.querySelector('#o3').textContent")
    CH = """()=>{const o={h:[],b:[]};let p=0;const w=document.createTreeWalker(document.querySelector('#o3'),NodeFilter.SHOW_TEXT,null);let n;while(n=w.nextNode()){const r=n.parentElement.closest('[data-rk]');for(let j=0;j<n.nodeValue.length;j++)if(r)o[r.dataset.rk].push(p+j);p+=n.nodeValue.length;}return o}"""
    import re as _re
    WD = [m.span() for m in _re.finditer(r'\S+', full)]   # 낱말 [시작, 끝) — 끌기는 낱말 단위로 붙음
    pg.keyboard.press('h'); pg.wait_for_timeout(150); drag(pg, pg.evaluate(XY, ['#o3', 0, WD[8][1]]))
    pg.keyboard.press('b'); pg.wait_for_timeout(150); drag(pg, pg.evaluate(XY, ['#o3', WD[2][0], WD[3][1]]))   # 두 낱말 빈칸
    c0 = pg.evaluate(CH); H0, B0 = sorted(c0['h']), sorted(c0['b'])
    # 저장본을 '한 묶음 형광펜 안에 빈칸' 모양으로(옛 기록·다른 기기 기록에서 생기는 구멍 난 형광펜) — 빈칸을 먼저 복원하게 순서도 바꿈
    ok3 = 'no marks'
    if H0 and B0 and H0[0] < B0[0] and H0[-1] > B0[-1]:
        hx0, hx1, bx = full[H0[0]:B0[0]], full[B0[-1] + 1:H0[-1] + 1], full[B0[0]:B0[-1] + 1]
        ok3 = pg.evaluate("""([aid,a,z,bx,big])=>{const k='jblhub.v1.ann.CONS',A=JSON.parse(localStorage.getItem(k)||'{}'),L=A[aid]||[];const h0=L.find(o=>o.t==='h'&&o.x===a),h1=L.find(o=>o.t==='h'&&o.x===z),bl=L.find(o=>o.t==='b'&&o.x===bx);if(!h0||!h1||!bl)return JSON.stringify(L.map(o=>o.t+':'+o.x));
          A[aid]=[bl,Object.assign({},h0,{x:big,s:h1.s})].concat(L.filter(o=>o!==h0&&o!==h1&&o!==bl));localStorage.setItem(k,JSON.stringify(A));return 'ok'}""", [aid3, hx0, hx1, bx, full[H0[0]:H0[-1] + 1]])
    pg.wait_for_timeout(300); pg.reload(); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(900)
    pg.evaluate("([aid,t])=>{const B=[...document.querySelectorAll('[data-aid]')].find(e=>e.dataset.aid===aid);const l=[...B.querySelectorAll('.tbody li')].find(x=>x.textContent===t);l.id='o3';l.scrollIntoView({block:'center'})}", [aid3, full]); pg.wait_for_timeout(300)
    hole = pg.evaluate("[new Set([...document.querySelectorAll('#o3 [data-rk=h]')].map(e=>e.dataset.g)).size,document.querySelectorAll('#o3 [data-rk=h]').length]")
    c1 = pg.evaluate(CH); H1, B1 = set(c1['h']), set(c1['b'])
    pg.keyboard.press('b'); pg.wait_for_timeout(150); drag(pg, pg.evaluate(XY, ['#o3', WD[1][0] + 1, WD[2][1] - 1]))   # 빈칸 앞 낱말 ~ 빈칸 첫 낱말(빈칸 둘째 낱말은 남아야 함 — 옛 코드는 형광펜 뒤 조각이 이 낱말을 덮음)
    c2 = pg.evaluate(CH); H2, B2 = set(c2['h']), set(c2['b'])
    ok(ok3 == 'ok' and hole == [1, 2] and H1 == set(H0) and B1 == set(B0), f'O3 준비: 구멍 난 형광펜 한 묶음 {ok3} {hole}')
    ok(set(range(*WD[3])) <= B2 and B1 <= B2 and not (H2 & B1) and H2 == H1 - B2, f'O3 구멍 난 형광펜 위 빈칸 겹치기 — 원래 빈칸 글자는 빈칸 그대로·형광펜은 새 빈칸 자리만 빠짐 (빈칸→형광펜 {sorted(H2 & B1)[:6]} · 빈칸 잃음 {sorted(B1 - B2)[:6]})')
    def marks():
        return pg.evaluate("[...document.querySelectorAll('#o3 [data-rk]')].map(e=>e.dataset.rk+':'+e.textContent)")
    # O5 덮어쓰기 알림 [↶ 되돌리기] 뒤 다른 표시 → 알림 버튼이 그 뒤 표시를 되돌리지 않음
    pg.keyboard.press('h'); pg.wait_for_timeout(150); drag(pg, pg.evaluate(XY, ['#o3', 12, 20]))   # 빈칸 덮어씀 → 알림
    tb = pg.evaluate("(()=>{const b=[...document.querySelectorAll('#toast button')].find(x=>/되돌리기/.test(x.textContent));if(b)b.id='o5b';return !!b})()")
    n_before = pg.evaluate("__h.Kit.undoN()")
    li2 = pg.evaluate("""(()=>{const L=[...document.querySelectorAll('#stage .tc .tbody li')].filter(l=>l.offsetParent&&l.id!=='o3'&&!l.querySelector('[data-rk],b,i,span,a')&&l.textContent.trim().length>=20);const l=L[5]||L[0];l.id='o5';l.scrollIntoView({block:'center'});return 1})()""")
    pg.wait_for_timeout(300); drag(pg, pg.evaluate(XY, ['#o5', 0, 6]))
    has5 = pg.evaluate("document.querySelectorAll('#o5 [data-rk]').length")
    if tb and pg.evaluate("!!document.querySelector('#o5b')"):
        pg.evaluate("document.querySelector('#o5b').click()"); pg.wait_for_timeout(400)
        r = pg.evaluate("[document.querySelectorAll('#o5 [data-rk]').length,document.querySelector('#toast').textContent]")
        ok(has5 and r[0] == has5 and '그 뒤에' in r[1], f'O5 옛 알림 [↶ 되돌리기] = 그 뒤 표시는 그대로·안내 {has5} {r}')
    else:
        ok(tb and not pg.evaluate("!!document.querySelector('#o5b')"), f'O5 새 표시 뒤 옛 되돌리기 버튼은 남지 않음(또는 안내) {tb}')
    ok(n_before >= 3, f'O5 실행 취소 단계 {n_before}')
    ok(not pg.errs, f'O3·O5 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # ---------- O6 ----------
    ctx, pg = new(b, 1280, 900, False); go(pg, '/'); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); go(pg, '/CONS/_jb')
    pg.evaluate("document.querySelector('#fone').click()"); pg.wait_for_timeout(600)
    s0 = pg.evaluate("(s=>s&&s.ids?s.ids.length:0)(__h.JB.sess)")
    pg.evaluate("__h.JB.cur=1;__h.JB.show&&__h.JB.show();__h.JB.save&&__h.JB.save()"); pg.wait_for_timeout(300)
    go(pg, '/CONS/_home/_home')
    dl = []
    pg.once('dialog', lambda d: (dl.append(d.message), d.dismiss()))
    has = pg.evaluate("(()=>{const b=document.querySelector('[data-jbf=\"todo\"]');if(b){b.click();return true}return false})()"); pg.wait_for_timeout(700)
    s1 = pg.evaluate("(s=>s&&s.ids?s.ids.length:0)(__h.JB.sess)")
    ok(has and s0 > 0 and dl and '새 회차' in dl[0] and s1 == s0, f'O6 안 푼 것 → 풀던 회차 확인(취소 = 그대로) {has} {s0} {s1} {dl[:1]}')
    ok(not pg.errs, f'O6 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # ---------- O7·O8 ----------
    ctx, pg = new(b, 1280, 900, False); go(pg, '/')
    pg.evaluate("""localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1');localStorage.setItem('jblhub.v1.ux2old','1');
      localStorage.setItem('jblhub.v1.devId',JSON.stringify('me'));localStorage.setItem('jblhub.v1.timeDev',JSON.stringify({other:{time:{'2026-01-05':{'':600000,'CONS':60000}},cut:'2026-02-01'}}))""")
    go(pg, '/CONS/WHT/learn')
    pg.evaluate("sessionStorage.removeItem('jblhub.v1.toasts')"); pg.keyboard.press('m'); pg.wait_for_timeout(400)
    T = pg.evaluate("JSON.parse(sessionStorage.getItem('jblhub.v1.toasts')||'[]').map(x=>x.t)")
    ok(pg.evaluate("document.querySelector('#memo').classList.contains('on')") and sum('이제 Shift+M' in t for t in T) == 1 and pg.evaluate("localStorage.getItem('jblhub.v1.keyNoticeM2')") == '1', f'O7 옛 사용자 M 먼저 = 메모 + 알림 한 번 {T[:2]}')
    pg.keyboard.press('Escape'); pg.evaluate("document.activeElement&&document.activeElement.blur()"); pg.keyboard.press('Shift+M'); pg.wait_for_timeout(300)
    T = pg.evaluate("JSON.parse(sessionStorage.getItem('jblhub.v1.toasts')||'[]').map(x=>x.t)")
    ok(sum('이제 Shift+M' in t for t in T) == 1, f'O7 그 뒤 Shift+M은 알림 다시 안 함 {T[:3]}')
    d = pg.evaluate("__h.tDay('2026-01-05')")
    ok(d == {'기타': 600000, 'CONS': 60000}, f"O8 다른 기기 합산 시작 전 날 빈 과목 = 기타 {d}")
    ok(not pg.errs, f'O7·O8 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
