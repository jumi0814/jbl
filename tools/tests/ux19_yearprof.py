"""UX19 출제 연도별 출제 교수 태그(10-16 사용자 "jb 및 넘버링 파트에서 출제 연도 및 교수님 태그를 달 때 출제연도 기준의 교수님 이름 … 강의자료는 같더라도 출제 교수님이 다르면 그걸 알 수 있게 … 출제연도는 가장 최신순(25,23,22) … 교수님 태그가 볼드체")
+ 같은 날 "교수님 바뀐 경우에엔 과목자료 기출문제에서 교수님 끼리 필터링" · "기출문제 자체에는 이전 교수님 족보 문제도"
- JB 카드 교수 칩: 굵게 · 해마다 다르면 '교수 25 · 교수 24·22'(최근 해 먼저 · data-yp 순서) — ANAT Q03(한정준 25 · 최진영 ~24)
- 교수 바뀐 강의(ANAT LIP) 기출 탭 교수 선택지 = 그 강의 카드 data-profs 전부 · 교수+연도 = 그 해 그 교수(data-yp)
- PHARM ANX(교수 바뀐 새 강의) 기출 탭 = 참고 기출 24가 기본으로 보임
- 과목 홈 '2회 이상 출제' 교수 = 굵게(출제 연도 기준)
- 넘버링 꼬리표 = 연도 최근 먼저 + 굵은 교수 · 해마다 다르면 묶음 · 복습 카드 교수 태그 굵게
- pageerror 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CLEAR = "(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0||k.indexOf('jblhub.v1.jbst')===0)localStorage.removeItem(k);})()"
def go(pg, h, w=2200):
    pg.goto('about:blank'); pg.goto(U + h); pg.wait_for_timeout(w)
def import_all(pg, sj):
    pg.evaluate(f"location.hash='#/_num/{sj}'"); pg.wait_for_timeout(3000)
    pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); pg.wait_for_timeout(700)
    pg.select_option('[data-if=src]', 'jb'); pg.select_option('[data-if=ty]', ''); pg.wait_for_timeout(300)
    pg.click('[data-ib=all]'); pg.wait_for_timeout(500); pg.click('[data-cf2=ok]'); pg.wait_for_timeout(1500); pg.click('.nm-ov [data-x]'); pg.wait_for_timeout(700)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1300, 'height': 900}); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    go(pg, '#/', 1500); pg.evaluate(CLEAR)
    # ---- JB 카드 칩
    go(pg, '#/ANAT/_jb', 2500)
    c = pg.evaluate("""(()=>{const a=document.querySelector('#c-Q03');if(!a)return null;const ch=a.querySelector('.qhead .chip.pf'),B=ch?[...ch.querySelectorAll('b')]:[];
      const yp=(a.dataset.yp||'').split(/\\s+(?=\\d{2}:)/).map(t=>t.split(':')[1]);return {n:B.length,names:B.map(x=>x.textContent),fw:B[0]?+getComputedStyle(B[0]).fontWeight:0,yp:[...new Set(yp)],prof:a.dataset.prof,yrs:a.dataset.yrs,txt:ch?ch.textContent:''}})()""")
    ok(bool(c) and c['n'] == 2 and [x for i, x in enumerate(c['names']) if x not in c['names'][:i]] == c['yp'] and c['names'][0] == c['prof'] and c['fw'] >= 700, f"ANAT Q03 교수 칩 = 굵은 교수 2명 · 최근 출제 해 교수 먼저(data-yp 순서) {c}")
    ok(bool(c) and '25' in c['txt'] and c['txt'].index(c['names'][0]) < c['txt'].index(c['names'][1]), f"칩 글 = '교수 연도 · 교수 연도'(최근 해 먼저) {c and c['txt']!r}")
    nb = pg.evaluate("[...document.querySelectorAll('#cards .qc .qhead .chip.pf')].filter(x=>x.offsetParent&&!x.querySelector('b')).length")
    ok(nb == 0, f"모든 JB 카드 교수 칩이 굵음(<b> 없는 칩 {nb})")
    # 교수+연도 거르기 = 그 해 그 교수
    opts = pg.evaluate("[...document.querySelectorAll('#fprof option')].map(o=>o.value)")
    ok('최진영' in opts and '한정준' in opts, f"ANAT JB 교수 선택지에 옛 출제 교수(최진영·한정준) {opts}")
    pg.select_option('#fprof', '최진영'); pg.wait_for_timeout(300)
    yo = pg.evaluate("[...document.querySelectorAll('#fyr option')].map(o=>o.value)")
    if '24' in yo:
        pg.select_option('#fyr', '24'); pg.wait_for_timeout(400)
        r = pg.evaluate("(()=>{const v=[...document.querySelectorAll('#cards .qc')].filter(c=>c.offsetParent!==null);return {n:v.length,bad:v.filter(c=>!(' '+(c.dataset.yp||'')+' ').includes(' 24:최진영 ')).map(c=>c.dataset.id).slice(0,5)}})()")
        ok(r['n'] > 0 and not r['bad'], f"교수 최진영 + 24년 = 그 해 최진영 출제만 {r}")
        pg.select_option('#fyr', '')
    pg.select_option('#fprof', ''); pg.wait_for_timeout(200)
    # ---- 교수 바뀐 강의 기출 탭(ANAT LIP)
    go(pg, '#/ANAT/LIP/jb', 2500)
    r = pg.evaluate("""(()=>{const o=[...document.querySelectorAll('#fprof option')].map(o=>o.value).filter(Boolean),c=[...document.querySelectorAll('#cards .qc')];const P=new Set();c.forEach(x=>(x.dataset.profs||'').split('|').forEach(p=>p&&P.add(p)));return {o,need:[...P],vis:!!document.querySelector('#fprof')&&document.querySelector('#fprof').offsetParent!==null}})()""")
    ok(r['vis'] and set(r['need']) <= set(r['o']) and len(r['o']) >= 2, f"ANAT LIP 기출 탭 교수 선택지 = 카드 출제 교수 전부 {r}")
    # ---- PHARM ANX 참고 기출 기본 보임
    go(pg, '#/PHARM/ANX/jb', 2500)
    r = pg.evaluate("(()=>{const v=[...document.querySelectorAll('#cards .qc')].filter(c=>c.offsetParent!==null);return {n:v.length,C:v.filter(c=>c.dataset.tier==='C').length,ref:[...document.querySelectorAll('#fprof option')].some(o=>/참고 기출/.test(o.textContent))}})()")
    ok(r['n'] >= 20 and r['C'] == r['n'], f"PHARM ANX 기출 탭 = 참고 기출이 기본으로 보임 {r}")
    # ---- 과목 홈 2회 이상 출제
    go(pg, '#/ANAT/_home', 2500)
    r = pg.evaluate("(()=>{const L=[...document.querySelectorAll('#htop .toplist li .p')];return {n:L.length,b:L.filter(x=>x.querySelector('b')).length,multi:L.filter(x=>x.querySelectorAll('b').length>1).length}})()")
    ok(r['n'] > 0 and r['b'] == r['n'], f"과목 홈 '2회 이상 출제' 교수 굵게 {r}")
    # ---- 넘버링
    import_all(pg, 'ANAT')
    r = pg.evaluate("""(()=>{const T=[...document.querySelectorAll('.nm-it .nm-qt')];let bad=[],multi=0;for(const t of T){const ys=[...t.querySelectorAll('.y')].map(e=>e.textContent).join('·').split('·').filter(Boolean).map(Number);for(let i=1;i<ys.length;i++)if(ys[i]>ys[i-1])bad.push(t.textContent);if(t.querySelectorAll('.p').length>1)multi++;}
      const p0=T.map(t=>t.querySelector('.p')).find(Boolean);return {n:T.length,bad:bad.slice(0,3),multi,fw:p0?+getComputedStyle(p0).fontWeight:0}})()""")
    ok(r['n'] > 50 and not r['bad'] and r['fw'] >= 700, f"넘버링 꼬리표 = 연도 최근 먼저 · 굵은 교수 {r}")
    ok(r['multi'] > 0, f"해마다 출제 교수가 다르면 묶음(ANAT LIP 등) {r['multi']}")
    q = pg.evaluate("""(()=>{const h=JBLNUM._H().PACKS.ANAT.cards.Q03||'',m=/data-aid="([^"]+)"/.exec(h);if(!m)return '';const a=document.querySelector('.nm-it[data-id="'+CSS.escape('jb:'+m[1])+'"]'),t=a&&a.querySelector('.nm-qt');return t?t.textContent:''})()""")
    ok(q.startswith('25') and '한정준' in q and q.index('한정준') < q.index('최진영'), f"ANAT Q03 꼬리표 '25 한정준 · 24·22·20 최진영' {q!r}")
    # 복습 카드
    pg.evaluate("location.hash='#/_numr/ANAT'"); pg.wait_for_timeout(2500)
    if pg.query_selector('.nm-rvw [data-rview=card]'):
        pg.click('.nm-rvw [data-rview=card]'); pg.wait_for_timeout(800)
        r = pg.evaluate("(()=>{const t=document.querySelector('.nm-card .nm-tag.pf, .nm-cpos .nm-tag.pf');const bb=t&&t.querySelector('b');return {t:!!t,b:!!bb,fw:bb?+getComputedStyle(bb).fontWeight:0}})()")
        ok(r['t'] and r['b'] and r['fw'] >= 700, f"복습 카드 교수 태그 굵게 {r}")
    else: ok(False, '넘버링 복습 카드 보기 단추 없음')
    ok(not errs, f"pageerror 0 {errs[:3]}")
    pg.evaluate(CLEAR); b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
