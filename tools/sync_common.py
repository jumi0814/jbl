"""공통 생성 코드 동기화 — 수정은 tools/cons/에서만 하고 이 스크립트로 다른 과목 폴더에 복사한다.
  .venv/bin/python tools/sync_common.py            # cons → oms1·impl·anat·geri·pharm 복사
  .venv/bin/python tools/sync_common.py --check    # 사본끼리 다르면 실패(종료 코드 1)
  .venv/bin/python tools/sync_common.py --build    # 복사 후 6과목 build4 → verify → audit_design (tools/build_all.sh와 같음)
build2.py는 과목마다 마지막 출력 줄이 달라 복사하지 않는다(고칠 때는 과목별로)."""
import os, sys, shutil, hashlib, subprocess
TOOLS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(TOOLS)
SRC = 'cons'
DST = ['oms1', 'impl', 'anat', 'geri', 'pharm']
COMMON = ['shell.html', 'build4.py', 'lecparse.py', 'trend.py', 'reflow.py', 'emph.py', 'template2.html', 'SPEC.md']
SUBJ_ORDER = ['oms1', 'cons', 'impl', 'anat', 'geri', 'pharm']
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
def check():
    bad = []
    for f in COMMON:
        src = os.path.join(TOOLS, 'SPEC.md') if f == 'SPEC.md' else os.path.join(TOOLS, SRC, f)
        h0 = md5(src)
        for d in [SRC] + DST:
            p = os.path.join(TOOLS, d, f)
            if not os.path.exists(p) or md5(p) != h0: bad.append(f'{d}/{f}')
    print('sync check:', 'OK — 6개 사본 동일' if not bad else 'DIFF ' + ', '.join(bad))
    return not bad
def sync():
    shutil.copyfile(os.path.join(TOOLS, 'SPEC.md'), os.path.join(TOOLS, SRC, 'SPEC.md'))
    for d in DST:
        for f in COMMON:
            shutil.copyfile(os.path.join(TOOLS, SRC, f), os.path.join(TOOLS, d, f))
    print('synced', len(COMMON), 'files →', ', '.join(DST))
def build(extra=()):
    py = os.path.join(ROOT, '.venv', 'bin', 'python'); py = py if os.path.exists(py) else sys.executable
    for s in SUBJ_ORDER:
        print(f'== build {s}', flush=True)
        r = subprocess.run([py, os.path.join(TOOLS, s, 'build4.py')], cwd=ROOT)
        if r.returncode: print('BUILD FAIL', s); return False
    for t in ['verify.py', 'audit_design.py'] + list(extra):
        print(f'== {t}', flush=True)
        r = subprocess.run([py, os.path.join(TOOLS, t)], cwd=ROOT)
        if r.returncode: print('FAIL', t); return False
    return True
if __name__ == '__main__':
    a = sys.argv[1:]
    if '--check' in a: sys.exit(0 if check() else 1)
    sync(); ok = check()
    if '--build' in a: ok = build(['tests/ux_all.py'] if '--all' in a and os.path.exists(os.path.join(TOOLS, 'tests', 'ux_all.py')) else []) and ok
    sys.exit(0 if ok else 1)
