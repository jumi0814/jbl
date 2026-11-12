"""회귀 전체 — tools/tests/*.py(이 파일 제외)를 차례로 돌려 진짜 실패가 하나라도 있으면 종료 코드 1 (tools/build_all.sh가 빌드 실패로 봄)
실패 = 종료 코드 ≠ 0 · 출력에 'RESULT FAIL' · 'RESULT' 판정 줄이 없음(판정 없는 테스트는 테스트가 아님 — F7)
11-12 W0: 기준 실패 정리표 tools/tests/STATUS.json을 읽음(분류·이유는 그 파일 머리)
  helper  = 테스트가 아님 → 목록에서 뺌
  retired = 낡음 → 돌리지 않고 SKIP 줄(대신 보는 테스트 = see)
  local   = need(path:·glob:·grep:<파일>::<글자>·git:<커밋>·os:darwin — '|' = 어느 하나)가 없으면 SKIP · 있으면 돌리고, 실패하면 진짜 실패(기록 지킴이 legacy_restore 등)
  bug?    = 돌림 · 실패해도 '알려진 실패'(종료 코드에 안 셈) · 통과하면 '(STATUS에서 빼도 됨)'
  → 진짜 실패 = STATUS에 없는 테스트의 실패 + need가 다 있는 local의 실패. 끝 줄 = RESULT PASS|FAIL · PASS n · SKIP n(이유별) · 알려진 실패 n
  (알려진 실패·SKIP 줄에는 'FAIL' 글자를 쓰지 않음 — full_check.sh 요약이 'FAIL'을 셈)
  .venv/bin/python tools/tests/ux_all.py [이름 …]   # 이름을 주면 그것만(STATUS는 그대로 따름)
  … --force [이름 …]    # STATUS를 무시하고 그대로 돌림(분류를 다시 볼 때)   … --list = 돌리지 않고 분류만"""
import os, sys, subprocess, time, json, glob, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
PY = os.path.join(ROOT, '.venv', 'bin', 'python'); PY = PY if os.path.exists(PY) else sys.executable
FORCE = '--force' in sys.argv; LIST = '--list' in sys.argv; only = [a for a in sys.argv[1:] if not a.startswith('--')]
try: STATUS = {k: v for k, v in json.load(open(os.path.join(HERE, 'STATUS.json'), encoding='utf-8')).items() if k != '_'}
except FileNotFoundError: STATUS = {}
INFO = re.compile(r'lost rate|LOST_GONE [0-9]')   # 통과해도 보여 줄 정보 줄(legacy_restore)
def has(n):
    """need 한 칸('|' = 어느 하나) → 있는지"""
    for a in n.split('|'):
        k, _, v = a.strip().partition(':')
        if k == 'path' and os.path.exists(os.path.join(ROOT, v)): return True
        if k == 'glob' and glob.glob(os.path.join(ROOT, v)): return True
        if k == 'grep':   # grep:<파일>::<글자> — 그 파일이 있고 그 글자가 들어 있음(같은 이름의 다른 쿼터 파일과 가림)
            p, _, s = v.partition('::'); p = os.path.join(ROOT, p)
            if os.path.exists(p) and s in open(p, encoding='utf-8', errors='replace').read(): return True
        if k == 'os' and sys.platform == v: return True
        if k == 'git' and subprocess.run(['git', 'cat-file', '-e', v + '^{commit}'], cwd=ROOT, capture_output=True).returncode == 0: return True
    return False
def helper(f): return STATUS.get(f[:-3], {}).get('st') == 'helper'
tests = sorted(f for f in os.listdir(HERE) if f.endswith('.py') and f != 'ux_all.py' and (FORCE or not helper(f)) and (not only or f[:-3] in only or f in only))
npass = 0; bad = []; known = []; skip = {}
for f in tests:
    n = f[:-3]; st = {} if FORCE else STATUS.get(n, {}); kind = st.get('st'); why0 = st.get('why', ''); see = st.get('see', '')
    miss = [x for x in st.get('need', []) if not has(x)] if kind == 'local' else []
    if kind == 'retired' or miss:
        r = 'retired(낡음)' if kind == 'retired' else 'local(여기 없는 것: ' + ' · '.join(miss) + ')'; skip.setdefault(kind, []).append(n)
        print(f"SKIP {f:22s}       {r} — {why0[:110]}{' → 대신 ' + see if see else ''}".replace('FAIL', '실패'), flush=True); continue
    if LIST: print(f" run {f:22s}       {kind or ''}"); continue
    t0 = time.time()
    try:
        r = subprocess.run([PY, os.path.join(HERE, f)], cwd=ROOT, capture_output=True, text=True, timeout=3600); out = (r.stdout or '') + (r.stderr or ''); rc = r.returncode
    except subprocess.TimeoutExpired as e:
        out = ((e.stdout or b'').decode('utf-8', 'replace') if isinstance(e.stdout, bytes) else (e.stdout or '')) + '\nTimeout 3600s'; rc = 124
    res = [l for l in out.splitlines() if l.startswith('RESULT')]
    why = 'exit %d' % rc if rc else ('RESULT FAIL' if any('FAIL' in l for l in res) else ('판정 줄 없음' if not res else ''))   # RESULT SKIP = 인자가 필요한 1회용 검사
    dt = time.time() - t0; info = ' '.join(l.strip() for l in out.splitlines() if INFO.search(l) and 'FAIL' not in l)[:200]
    if why and kind == 'bug?':
        known.append(n); print(f"known {f:21s} {dt:5.0f}s 알려진 실패(STATUS bug?) {(res[-1] if res else why).replace('FAIL', '실패')} — {why0[:140]}".replace('FAIL', '실패'), flush=True); continue
    print(f"{'FAIL' if why else ' ok '} {f:22s} {dt:5.0f}s {res[-1] if res else ''} {why}{' ' + info if info else ''}{' (STATUS ' + kind + '인데 통과 — 그 줄을 빼도 됨)' if kind == 'bug?' and not why else ''}", flush=True)
    if why:
        bad.append(n); print('\n'.join('      ' + l for l in out.splitlines() if 'FAIL' in l or 'Error' in l or 'Traceback' in l)[:3000])
    else: npass += 1
ns = sum(len(v) for v in skip.values())
tail = f"PASS {npass} · SKIP {ns}" + (f"({' · '.join(f'{k} {len(v)}' for k, v in skip.items())})" if ns else '') + (f" · 알려진 실패 {len(known)}({', '.join(known)})" if known else '')
if LIST: print('분류만(돌리지 않음) — ' + tail.replace('PASS 0 · ', '')); sys.exit(0)
print('RESULT', ('PASS' if not bad else f'FAIL {len(bad)}: ' + ', '.join(bad)) + ' · ' + tail); sys.exit(1 if bad else 0)
