"""회귀 전체 — tools/tests/*.py(이 파일 제외)를 차례로 돌려 하나라도 실패하면 종료 코드 1 (tools/build_all.sh가 빌드 실패로 봄)
실패 = 종료 코드 ≠ 0 · 출력에 'RESULT FAIL' · 'RESULT' 판정 줄이 없음(판정 없는 테스트는 테스트가 아님 — F7)
  .venv/bin/python tools/tests/ux_all.py [이름 …]   # 이름을 주면 그것만"""
import os, sys, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
PY = os.path.join(ROOT, '.venv', 'bin', 'python'); PY = PY if os.path.exists(PY) else sys.executable
only = sys.argv[1:]
tests = sorted(f for f in os.listdir(HERE) if f.endswith('.py') and f != 'ux_all.py' and (not only or f[:-3] in only or f in only))
bad = []
for f in tests:
    t0 = time.time(); r = subprocess.run([PY, os.path.join(HERE, f)], cwd=ROOT, capture_output=True, text=True, timeout=3600)
    out = (r.stdout or '') + (r.stderr or ''); res = [l for l in out.splitlines() if l.startswith('RESULT')]
    why = 'exit %d' % r.returncode if r.returncode else ('RESULT FAIL' if any('FAIL' in l for l in res) else ('판정 줄 없음' if not res else ''))   # RESULT SKIP = 인자가 필요한 1회용 검사
    print(f"{'FAIL' if why else ' ok '} {f:22s} {time.time() - t0:5.0f}s {res[-1] if res else ''} {why}", flush=True)
    if why:
        bad.append(f); print('\n'.join('      ' + l for l in out.splitlines() if 'FAIL' in l or 'Error' in l or 'Traceback' in l)[:3000])
print('RESULT', 'PASS' if not bad else f'FAIL {len(bad)}: ' + ', '.join(bad)); sys.exit(1 if bad else 0)
