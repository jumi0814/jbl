"""공통 생성 코드 동기화 — 수정은 tools/cons/에서만 하고 이 스크립트로 다른 과목 폴더에 복사한다.
  .venv/bin/python tools/sync_common.py            # cons → 등록표의 다른 과목 폴더 전부 복사
  .venv/bin/python tools/sync_common.py --check    # 사본끼리 다르면 실패(종료 코드 1)
  .venv/bin/python tools/sync_common.py --build    # 복사 후 7과목 build4 → verify → audit_design (tools/build_all.sh와 같음)
  .venv/bin/python tools/sync_common.py --rehub --all   # 원본(work/jb)이 없는 환경: 복사 후 허브만 다시(tools/rehub.py) → verify → audit_design → tests (tools/hub_all.sh와 같음)
build2.py는 과목마다 마지막 출력 줄이 달라 복사하지 않는다(고칠 때는 과목별로)."""
import os, sys, shutil, hashlib, subprocess
TOOLS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(TOOLS)
SRC = 'cons'   # 공통 코드 원본(3Q 과목 폴더지만 그대로 — 모든 과목 폴더가 같은 사본)
sys.path.insert(0, TOOLS); import quarters as QS   # 11-04 과목 = 등록표(tools/quarters.json)에서 tools/<sid>/ 폴더가 있는 것 전부(쿼터 상관없이 같은 사본)
SUBJ_ORDER = [s.lower() for s in QS.all_sids() if os.path.isdir(os.path.join(TOOLS, s.lower()))]
DST = [d for d in SUBJ_ORDER if d != SRC]
BUILD_ORDER = [s.lower() for q in QS.live() for s in QS.sids(q) if os.path.isdir(os.path.join(TOOLS, s.lower()))]   # 빌드는 보관(frozen) 아닌 쿼터 과목만
COMMON = ['shell.html', 'build4.py', 'lecparse.py', 'trend.py', 'reflow.py', 'emph.py', 'template2.html', 'SPEC.md']
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
def check():
    bad = []
    for f in COMMON:
        src = os.path.join(TOOLS, 'SPEC.md') if f == 'SPEC.md' else os.path.join(TOOLS, SRC, f)
        h0 = md5(src)
        for d in [SRC] + DST:
            p = os.path.join(TOOLS, d, f)
            if not os.path.exists(p) or md5(p) != h0: bad.append(f'{d}/{f}')
    print('sync check:', f'OK — {len(DST) + 1}개 사본 동일' if not bad else 'DIFF ' + ', '.join(bad))
    return not bad
def sync():
    shutil.copyfile(os.path.join(TOOLS, 'SPEC.md'), os.path.join(TOOLS, SRC, 'SPEC.md'))
    for d in DST:
        for f in COMMON:
            shutil.copyfile(os.path.join(TOOLS, SRC, f), os.path.join(TOOLS, d, f))
    print('synced', len(COMMON), 'files →', ', '.join(DST))
def build(extra=(), rehub=False):
    py = os.path.join(ROOT, '.venv', 'bin', 'python'); py = py if os.path.exists(py) else sys.executable
    if rehub:   # 원본(work/jb)이 없는 환경 — 팩은 그대로 두고 허브만 다시(tools/rehub.py)
        print('== rehub', flush=True)
        if subprocess.run([py, os.path.join(TOOLS, 'rehub.py')], cwd=ROOT).returncode: print('REHUB FAIL'); return False
    for s in ([] if rehub else BUILD_ORDER):
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
    if '--build' in a or '--rehub' in a: ok = build(['tests/ux_all.py'] if '--all' in a and os.path.exists(os.path.join(TOOLS, 'tests', 'ux_all.py')) else [], rehub='--rehub' in a) and ok
    sys.exit(0 if ok else 1)
