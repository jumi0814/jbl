"""tests4 공통 — 전환 뒤 모양의 미리 보기 사이트(4q = 뿌리, 3q = 3q/ — tools/rehub.py --site)를 만들고 한 주소(origin)로 띄움.
두 허브가 같은 localStorage·IndexedDB를 쓰는 실제 상황 그대로(jumi0814.github.io/jbl/ 와 /jbl/3q/)."""
import os, sys, subprocess, threading, functools, http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import quarters as QS
SITE = os.path.join(ROOT, 'work', '_tmp', 'qsite')
PY = os.path.join(ROOT, '.venv', 'bin', 'python')
def build():
    r = subprocess.run([PY if os.path.exists(PY) else sys.executable, os.path.join(TOOLS, 'rehub.py'), '--site', SITE], capture_output=True, text=True)
    if r.returncode: sys.exit('rehub --site 실패\n' + r.stdout + r.stderr)
    return {q: os.path.relpath(QS.cutover_dir(q, SITE), SITE).replace(os.sep, '/').strip('.').strip('/') for q in QS.QS}
class _H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve():
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(_H, directory=SITE)); srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f'http://127.0.0.1:{srv.server_address[1]}/'
def url(base, rel): return base + (rel + '/' if rel else '') + 'index.html'
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
