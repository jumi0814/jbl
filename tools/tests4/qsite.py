"""tests4 공통 — 전환 뒤 모양의 미리 보기 사이트(4q = 뿌리, 3q = 3q/ — tools/rehub.py --site)를 만들고 한 주소(origin)로 띄움.
두 허브가 같은 localStorage·IndexedDB를 쓰는 실제 상황 그대로(jumi0814.github.io/jbl/ 와 /jbl/3q/).
11-10 W0 시험용 사이트(fixture) build_fixture() — 지금 쿼터 정체성(4Q 저장 이름)으로 3Q 팩을 띄움: 4Q 코드 길(저장 이름·첫 실행 가져오기·동기화)을 진짜 내용으로 시험.
  등록표 파일은 안 바꿈(부르는 동안만 quarters.sids를 덮어씀) · 자리 work/_tmp/fx(뿌리 = 4Q 정체성 + 3Q 7과목 · 3q/ = 3Q 허브 그대로 — ⇄ 링크가 살아 있음)
  과목·강의·카드는 박지 말고 __h.PACKS에서 찾아 씀(아래 PACKINFO) — 4Q 내용이 차면 같은 테스트가 qsite 뿌리에서 그대로 돎."""
import os, sys, subprocess, threading, functools, http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import quarters as QS
SITE = os.path.join(ROOT, 'work', '_tmp', 'qsite')
FX = os.path.join(ROOT, 'work', '_tmp', 'fx')
PY = os.path.join(ROOT, '.venv', 'bin', 'python')
def build():
    r = subprocess.run([PY if os.path.exists(PY) else sys.executable, os.path.join(TOOLS, 'rehub.py'), '--site', SITE], capture_output=True, text=True)
    if r.returncode: sys.exit('rehub --site 실패\n' + r.stdout + r.stderr)
    return {q: os.path.relpath(QS.cutover_dir(q, SITE), SITE).replace(os.sep, '/').strip('.').strip('/') for q in QS.QS}
def build_fixture(stubs=False, out=None):
    """시험용 사이트 — out(기본 work/_tmp/fx) 뿌리에 '지금 쿼터 정체성 + 내용 쿼터(보관 3Q) 팩' 허브, 그 아래 <3q>/에 3Q 허브 그대로.
    stubs=True면 지금 쿼터의 진짜 과목 팩(자료 대기 빈 과목 등)도 3Q 과목 뒤에 같이 실음(빈 과목 ↔ 내용 있는 과목 사이 이동 시험용).
    돌려주는 값 = {'dir','ident': 지금 쿼터 id,'content': 내용 쿼터 id,'rel': {쿼터: 사이트 안 상대 폴더},'sids': 뿌리 허브의 과목 목록}"""
    http_ = os.environ.pop('JBL_HTTP', None)   # rehub → jblpaths가 JBL_HTTP=1이면 서버를 하나 더 띄움 — 여기선 필요 없음
    try: import rehub
    finally:
        if http_ is not None: os.environ['JBL_HTTP'] = http_
    fx = os.path.abspath(out or FX); cur = QS.current()
    src = next((q for q in QS.QS if q != cur and QS.frozen(q) and QS.sids(q)), None)   # 내용이 있는 보관 쿼터(3q)
    if not src: sys.exit('build_fixture: 내용이 있는 보관 쿼터가 없음')
    L = {q: (fx if q == cur else os.path.join(fx, q)) for q in QS.QS}
    s_src = QS.sids(src); s_cur = QS.sids(cur) if stubs else []; real = QS.sids
    def fake(q=None):   # 이 호출 동안만: 지금 쿼터의 과목 = 내용 쿼터 과목(+ 진짜 과목) · 내용 쿼터로 넘길 과목은 없음(뿌리가 다 가짐)
        q = q or QS.current(); return list(s_src) + list(s_cur) if q == cur else [] if q == src else real(q)
    os.makedirs(os.path.join(fx, 'packs'), exist_ok=True)
    if stubs:   # 지금 쿼터 진짜 팩 — rehub.one은 src(내용 쿼터)에 없는 과목을 건너뛰므로 먼저 BUILD를 박아 넣어 둠
        import hashlib
        B = hashlib.md5(open(os.path.join(TOOLS, 'cons', 'shell.html'), encoding='utf-8').read().encode('utf-8')).hexdigest()[:8]
        for s in s_cur:
            f0 = os.path.join(QS.docs_dir(cur), 'packs', s + '.js')
            if os.path.exists(f0): open(os.path.join(fx, 'packs', s + '.js'), 'w', encoding='utf-8').write(rehub.restamp(open(f0, encoding='utf-8').read(), B, s))
    else:   # 지난번 stubs=True로 남은 팩 치움
        for s in QS.sids(cur):
            f = os.path.join(fx, 'packs', s + '.js')
            if os.path.exists(f): os.remove(f)
    QS.sids = fake
    try: B, bad, READY = rehub.one(cur, out=fx, src=QS.docs_dir(src), layout=L)
    finally: QS.sids = real
    n = os.path.join(fx, 'num'); n0 = os.path.join(QS.docs_dir(cur), 'num')   # 넘버링 모듈은 지금 쿼터 것(보관 쿼터 사본은 얼어 있음)
    if os.path.islink(n) and os.readlink(n) != n0 and os.path.isdir(n0): os.remove(n); os.symlink(n0, n)
    rehub.one(src, out=L[src], src=QS.docs_dir(src), layout=L)   # 3q/ = 3Q 허브 그대로(같은 주소에서 두 정체성)
    return {'dir': fx, 'ident': cur, 'content': src, 'rel': {q: os.path.relpath(L[q], fx).replace(os.sep, '/').strip('.').strip('/') for q in L}, 'sids': READY}
class _H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve(d=None):
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(_H, directory=d or SITE)); srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f'http://127.0.0.1:{srv.server_address[1]}/'
def url(base, rel): return base + (rel + '/' if rel else '') + 'index.html'
# ---- 허브에서 과목·강의·문서를 찾는 공통 JS(11-10 — id를 박지 않음)
READYJS = "()=>!!(window.__h&&__h.PACKS&&document.querySelector('.hkick,#stage'))"
PACKSJS = "n=>!!(window.__h&&__h.PACKS&&Object.keys(__h.PACKS).length>=n)"
PACKINFO = """()=>{const len=x=>x==null?0:(typeof x==='string'?x.length:JSON.stringify(x).length),o={};
 for(const s of Object.keys(__h.PACKS)){const p=__h.PACKS[s],T=p.tables||[],P=p.preds||[],C=p.cards||{},sum=(a,f)=>(a||[]).reduce((n,i)=>n+len(f(i)),0);
  o[s]={order:(p.order||[]).length,size:{_jb:sum(p.order,i=>C[i]),_tbl:sum(T.filter(x=>!x.sum),x=>x.html),_pred:sum(P,x=>x.html),_sum:len(p.sumall),_led:len(p.ledger)},
   lect:(p.lect||[]).map(L=>({k:L.k,tabs:__h.docTabs(p,L.k).map(t=>t[0]),size:{learn:len(L.learn),sum:len(L.sum),tbl:sum(L.tbl,i=>(T[i]||{}).html),jb:sum(L.jb,i=>C[i]),pred:sum(L.pred,i=>(P[i]||{}).html)}}))};}
 return o;}"""   # 과목마다 {order: JB 문항 수, size: 과목 문서 크기(글자), lect: [{k, tabs: 그 강의에 있는 탭, size: 탭 크기}]} — '가장 긴 문서' 고르기용
NAVDOCS = "()=>[...document.querySelectorAll('#nav .nvd[data-d]')].map(b=>b.dataset.d)"   # 지금 과목 메뉴에 있는 과목 문서(_home·_jb·… — 없는 문서는 메뉴에 없음)
def biggest(info, tab):
    """PACKINFO 결과에서 그 탭(learn·sum·tbl·jb·pred) 또는 과목 문서(_jb·_tbl·_pred·_sum)가 가장 큰 (과목, 문서, 탭, 크기) — 없으면 None"""
    best = None
    for s, v in info.items():
        if tab[0] == '_':
            c = (v['size'].get(tab, 0), s, tab, tab)
        else:
            c = max(((L['size'].get(tab, 0), s, L['k'], tab) for L in v['lect'] if tab in L['tabs']), default=None)
        if c and c[0] > 0 and (best is None or c[0] > best[0]): best = c
    return best and (best[1], best[2], best[3], best[0])
def wait_hub(pg, n=1, timeout=120000):
    """허브가 뜨고 과목 팩 n개 이상을 받을 때까지(빈 쿼터면 n=0)"""
    pg.wait_for_function(READYJS, timeout=timeout)
    if n: pg.wait_for_function(PACKSJS, arg=n, timeout=timeout)
fail = []
def ok(c, m):
    print(('  OK  ' if c else '  FAIL') + ' ' + m)
    if not c: fail.append(m)
def done():
    print('RESULT', 'FAIL' if fail else 'PASS'); sys.exit(1 if fail else 0)

def filesite(rel, sid='IMPL', q='3q'):
    """11-11 W3 '한 과목을 그림 파일 방식으로 바꾼 사본' — q 허브(rel[q])의 사본 <q>f/를 만들고 그 안에서 과목 sid만 파일 방식으로:
    그림 묶음(<SID>.img.*.js)을 풀어 packs/img/<SID>/<키>.<h8>.webp(강의 쪽) · jb<판>-<쪽>.<h8>.jpg(JB 원본 쪽) 파일로 쓰고(build4 주소 규칙 — DONE_빌드.md),
    팩 사본에 imgf = {lec:{키:h8}, jb:{키:h8}}를 넣고 imgv를 비움 · 그 과목의 묶음 파일은 사본에 두지 않음(허브가 묶음을 찾으면 404로 드러남).
    다른 과목은 묶음 방식 그대로(링크) → 두 방식이 한 허브에서 함께 돎 · 저장 정체성은 q 그대로(그림 길만 시험) · 넘버링 모듈은 지금 것(docs/num — 보관 분기의 옛 num.js가 아니라).
    돌려주는 값 = (사본의 상대 자리, imgf)"""
    import re, json, base64, hashlib, shutil
    src = os.path.join(SITE, rel[q]) if rel[q] else SITE; fr = (rel[q] or 'root') + 'f'; dst = os.path.join(SITE, fr)
    P0 = os.path.join(src, 'packs'); P = os.path.join(dst, 'packs'); os.makedirs(P, exist_ok=True)
    shutil.copyfile(os.path.join(src, 'index.html'), os.path.join(dst, 'index.html'))
    def link(a, b):
        a = os.path.realpath(a)
        if os.path.islink(b):
            if os.readlink(b) == a: return
            os.remove(b)
        elif os.path.lexists(b): return
        os.symlink(a, b)
    for f in ('icon-192.png', 'icon-512.png', 'manifest.webmanifest'):
        if os.path.exists(os.path.join(src, f)): link(os.path.join(src, f), os.path.join(dst, f))
    link(os.path.join(QS.docs_dir(QS.current()), 'num'), os.path.join(dst, 'num'))
    chunks = sorted(f for f in os.listdir(P0) if f.startswith(sid + '.img.') and f.endswith('.js'))
    for f in os.listdir(P0):
        b = os.path.join(P, f)
        if f in chunks or f == 'img':
            if os.path.islink(b): os.remove(b)
            continue
        if f == sid + '.js': continue
        link(os.path.join(P0, f), b)
    D = os.path.join(P, 'img', sid); stamp = os.path.join(D, '_stamp.json')
    sig = [[f, os.path.getsize(os.path.realpath(os.path.join(P0, f))), int(os.path.getmtime(os.path.realpath(os.path.join(P0, f))))] for f in chunks]
    old = json.load(open(stamp, encoding='utf-8')) if os.path.exists(stamp) else {}
    if old.get('sig') == sig and all(os.path.exists(os.path.join(D, n)) for n in old.get('files', [])[:5]): imgf = old['imgf']
    else:
        shutil.rmtree(D, ignore_errors=True); os.makedirs(D); imgf = {'lec': {}, 'jb': {}}; files = []
        for f in chunks:
            if f == sid + '.img.jb.js': continue   # 호환용 모음(판별 묶음을 다시 부름) — 그림 없음
            t = open(os.path.join(P0, f), encoding='utf-8').read(); o = json.loads(t[t.index('{'):t.rindex('}') + 1])
            for kind in ('lec', 'jb'):
                for k, v in (o.get(kind) or {}).items():
                    b = base64.b64decode(v.split(',', 1)[1]); h = hashlib.md5(b).hexdigest()[:8]
                    n = ('jb' if kind == 'jb' else '') + k + '.' + h + ('.jpg' if kind == 'jb' else '.webp')
                    open(os.path.join(D, n), 'wb').write(b); imgf[kind][k] = h; files.append(n)
        json.dump({'sig': sig, 'imgf': imgf, 'files': files}, open(stamp, 'w', encoding='utf-8'))
    t = open(os.path.join(P0, sid + '.js'), encoding='utf-8').read(); m = re.findall(r'"imgv": \{[^{}]*\}', t)
    if len(m) != 1: sys.exit(f'{sid}.js에서 imgv를 못 찾음({len(m)})')
    open(os.path.join(P, sid + '.js'), 'w', encoding='utf-8').write(t.replace(m[0], '"imgv": {}, "imgf": ' + json.dumps(imgf, ensure_ascii=False)))
    return fr, imgf
