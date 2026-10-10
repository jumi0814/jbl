"""넘버링 모듈 내보내기 (10-10) — tools/num/{num.js,docx.js} → docs/num/ 로 복사하고, docs/num 파일들의 해시를 허브 shell.html의 NUMV에 박는다(캐시 갱신).
  .venv/bin/python tools/num/build_num.py          # 복사 + NUMV → 그다음 sync_common + rehub(허브 다시 쓰기)까지
  .venv/bin/python tools/num/build_num.py --check  # docs/num이 tools/num과 같고 NUMV가 맞는지만(다르면 종료 코드 1)
기본 자료(seed)는 tools/num/build_seed.py(첨부 Word가 work/num/src에 있을 때만)."""
import os, sys, re, shutil, hashlib, subprocess
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
SRC = os.path.join(TOOLS, 'num'); OUT = os.path.join(ROOT, 'docs', 'num'); SHELL = os.path.join(TOOLS, 'cons', 'shell.html')
FILES = ['num.js', 'docx.js']
def ver():
    h = hashlib.md5()
    for f in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, f)
        if os.path.isfile(p) and f.endswith('.js'): h.update(f.encode()); h.update(open(p, 'rb').read())
    return h.hexdigest()[:8]
def main(check=False):
    os.makedirs(OUT, exist_ok=True); bad = []
    for f in FILES:
        a, b = os.path.join(SRC, f), os.path.join(OUT, f)
        if not os.path.exists(b) or open(a, 'rb').read() != open(b, 'rb').read():
            bad.append(f)
            if not check: shutil.copyfile(a, b)
    v = ver(); s = open(SHELL, encoding='utf-8').read(); m = re.search(r"const NUMV='([0-9a-f]{8}|dev)';", s)
    if not m: sys.exit('shell.html에 NUMV 줄이 없음')
    if m.group(1) != v:
        bad.append('NUMV')
        if not check: open(SHELL, 'w', encoding='utf-8').write(s[:m.start(1)] + v + s[m.end(1):])
    if check: print('build_num check:', 'OK' if not bad else 'DIFF ' + ', '.join(bad)); return not bad
    print(f'build_num: NUMV {v} · 바뀐 것 {", ".join(bad) or "없음"}')
    py = sys.executable
    subprocess.run([py, os.path.join(TOOLS, 'sync_common.py')], check=True)
    subprocess.run([py, os.path.join(TOOLS, 'rehub.py')], check=True)
    return True
if __name__ == '__main__':
    sys.exit(0 if main('--check' in sys.argv) else 1)
