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
