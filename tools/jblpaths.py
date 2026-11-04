"""저장소 기준 경로 — 모든 과목 파이프라인 공통.
과목 작업 폴더 = work/<SID>/ · JB 추출 = work/jb/<SID>_20xx/ (tools/jbx.py) · 출력 = 그 과목 분기의 docs 폴더(tools/quarters.json — 허브 <docs>/index.html, 팩 <docs>/packs/)
11-04 분기(3q·4q): Q = $JBL_Q 또는(tools/tests에서 돌면 3q · 그 밖은 등록표 current) · DOCS = $JBL_DOCS 또는 그 분기 docs ·
  HUB_DIR(테스트가 여는 허브) = $JBL_HUB_DIR 또는(분기가 frozen이고 스테이징이 있으면 그 스테이징 — rehub.py --q 3q --stage) DOCS · docs_of(sid) = 그 과목 분기의 docs"""
import os, re, sys, json
TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
WORK = os.path.join(ROOT, 'work')
if TOOLS not in sys.path: sys.path.insert(0, TOOLS)
import quarters as QS
def _q0():
    a = os.path.abspath(sys.argv[0]) if sys.argv and sys.argv[0] else ''
    return '3q' if os.sep + os.path.join('tools', 'tests') + os.sep in a else QS.current()   # 3Q 회귀(tools/tests)는 3Q 허브를 봄 — 4Q 테스트는 tools/tests4
Q = os.environ.get('JBL_Q') or _q0()
DOCS = os.path.abspath(os.environ['JBL_DOCS']) if os.environ.get('JBL_DOCS') else QS.docs_dir(Q)
HUB_DIR = os.path.abspath(os.environ['JBL_HUB_DIR']) if os.environ.get('JBL_HUB_DIR') else (QS.stage_dir(Q) if QS.frozen(Q) and os.path.exists(os.path.join(QS.stage_dir(Q), 'index.html')) else DOCS)
def docs_of(sid):
    """그 과목 팩이 들어가는 docs 폴더(과목 분기 기준 · $JBL_DOCS가 있으면 그것)"""
    return os.path.abspath(os.environ['JBL_DOCS']) if os.environ.get('JBL_DOCS') else QS.docs_dir(QS.quarter_of(sid))
def pack_path(sid, f=None): return os.path.join(docs_of(sid), 'packs', f or sid + '.js')
def sids(q=None): return QS.sids(q or Q)
JBX = os.path.join(WORK, 'jb') + '/'          # f'{JBX}{SID}_20{ed}/{i}.txt'
HUB_URL = 'file://' + os.path.join(HUB_DIR, 'index.html')   # 테스트·감사 스크립트가 여는 허브
if os.environ.get('JBL_HTTP'):   # 10-03 허브 점검: file://은 Chromium이 화면을 옮길 때 가끔 다른 localStorage를 보여 표시·북마크 테스트가 이유 없이 실패 → JBL_HTTP=1이면 docs/를 로컬 http로(포트 = JBL_HTTP 값이 숫자면 그 값)
    import threading, http.server, functools, socketserver
    _port = int(os.environ['JBL_HTTP']) if os.environ['JBL_HTTP'].isdigit() and int(os.environ['JBL_HTTP']) > 1 else 0
    class _Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    _srv = socketserver.ThreadingTCPServer(('127.0.0.1', _port), functools.partial(_Q, directory=HUB_DIR)); _srv.daemon_threads = True
    threading.Thread(target=_srv.serve_forever, daemon=True).start()
    HUB_URL = f'http://127.0.0.1:{_srv.server_address[1]}/index.html'
TMP = os.path.join(WORK, '_tmp'); os.makedirs(TMP, exist_ok=True)   # 스크린샷 등 임시 파일
def work(sid, *p):
    d = os.path.join(WORK, sid); os.makedirs(d, exist_ok=True)
    return os.path.join(d, *p)
def _load_js(path):
    t = open(path, encoding='utf-8').read()
    return json.loads(t[t.index('{'):t.rindex('}') + 1])
def prev_images(sid):
    """지금 docs/packs/에 올라가 있는 <SID>.img.*.js의 강의 이미지 {키-쪽: dataURI}.
    강의자료 원본(materials/, work/)이 없는 환경에서 재빌드해도 이미지가 빠지지 않게 하는 대체용."""
    out = {}; d = os.path.join(docs_of(sid), 'packs')
    if not os.path.isdir(d): return out
    for f in os.listdir(d):
        if f.startswith(sid + '.img.') and f.endswith('.js') and not f.startswith(sid + '.img.jb'):   # JB 원본 청크(jb·jb23·jb24·jb25)는 제외
            out.update(_load_js(os.path.join(d, f)).get('lec', {}))
    return out
def prev_crops(sid, crops):
    """지금 docs/packs/<SID>.js 문항 카드에 박힌 JB 그림 조각 {조각키: dataURI} (crops 폴더가 없을 때 대체용)."""
    p = pack_path(sid)
    if not os.path.exists(p): return {}
    cards = _load_js(p).get('cards', {}); out = {}
    for cid, kinds in crops.items():
        h = cards.get(cid, '')
        for kind, alt in (('q', 'JB 그림'), ('a', 'JB 그림(답)')):
            srcs = re.findall(r'<img class="fig" loading="lazy" src="([^"]+)" alt="%s">' % re.escape(alt), h)
            for k, s in zip(kinds.get(kind, []), srcs): out[k] = s
    return out
def prev_jb(sid):
    """지금 docs/packs/<SID>.img.jb.js의 JB 원본 쪽 이미지 {판-쪽: dataURI} — 같은 JB PDF를 다시 렌더해 파일만 바뀌는 것을 막는 용도."""
    p = pack_path(sid, sid + '.img.jb.js')
    return _load_js(p).get('jb', {}) if os.path.exists(p) else {}

_PJ = {}
def prev_jb_pages(sid):
    """지금 docs/packs/<SID>.img.jb23·jb24·jb25.js에 든 JB 원본 쪽 이미지 {판-쪽: dataURI}.
    JB 쪽 이미지 파일(work/jb/<SID>_20xx/N.jpeg)이 없는 환경(클라우드 세션 — 텍스트만 풀어 둠)에서 assemble.py가 그대로 다시 쓰는 대체용."""
    if sid not in _PJ:
        out = {}; d = os.path.join(docs_of(sid), 'packs')
        for f in (sorted(os.listdir(d)) if os.path.isdir(d) else []):
            if re.fullmatch(re.escape(sid) + r'\.img\.jb\d+\.js', f): out.update(_load_js(os.path.join(d, f)).get('jb', {}))
        _PJ[sid] = out
    return _PJ[sid]

def study_today():
    """허브의 '오늘'(공부 날) — 아침 6시 경계(DCUT 2026-10-03부터, shell.html day()와 같은 규칙). 새벽 0~6시 실행에도 테스트가 허브와 같은 날을 씀"""
    import datetime as _dt
    now = _dt.datetime.now(); k = (now - _dt.timedelta(hours=6)).date()
    return k if k.isoformat() >= '2026-10-03' else now.date()
