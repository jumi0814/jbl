"""출제 연도별 출제 교수 표(subject.py YEAR_PROF·YEAR_PROF_Q) 점검(10-16 — 사용자 '출제연도 기준의 교수님 이름')
빌드된 팩(docs/packs/<SID>.js)의 카드(data-lec·data-yrs·data-yp)와 맞춰 봄.
  .venv/bin/python tools/check_yearprof.py [SID…]
✗ = 고쳐야 함(종료 코드 1): YEAR_PROF 키가 강의에 없음 · YEAR_PROF_Q id가 문항에 없음 · 교수 글이 빈칸/문자열 아님 · 해가 숫자 아님
△ = 확인: 그 강의(문항)에 그 해 문항이 없음(오타·옮겨 간 키) · 표에 적힌 해인데 카드 data-yp가 다름(빌드 전 팩)"""
import os, sys, re, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J
SIDS = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
def load_subject(sid):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), sid.lower(), 'subject.py')
    sp = importlib.util.spec_from_file_location('subject_' + sid, p); m = importlib.util.module_from_spec(sp)
    sys.path.insert(0, os.path.dirname(p))
    try: sp.loader.exec_module(m)
    finally: sys.path.pop(0)
    return m
def y2(y): return y % 100
def audit(SID):
    S = load_subject(SID); P = J._load_js(os.path.join(J.DOCS, 'packs', SID + '.js'))
    YP, YQ = getattr(S, 'YEAR_PROF', {}) or {}, getattr(S, 'YEAR_PROF_Q', {}) or {}
    keys = {L['k'] for L in P['lect']}
    cards = {}
    for q, h in P['cards'].items():
        a = re.search(r'<article[^>]*>', h); A = a.group(0) if a else ''
        g = lambda k: (re.search(k + r'="([^"]*)"', A) or [None, ''])[1]
        yp = {}
        for t in re.split(r'\s+(?=\d{2}:)', g('data-yp').strip()):
            if ':' in t: yp[int(t.split(':', 1)[0])] = t.split(':', 1)[1].strip()
        cards[q] = {'lec': g('data-lec'), 'yrs': {int(y) for y in g('data-yrs').split() if y.isdigit()}, 'yp': yp}
    X, W = [], []
    def chk_val(where, y, p):
        if not isinstance(y, int): X.append(f'{where} 해 {y!r} — 숫자 아님')
        if not isinstance(p, str) or not p.strip(): X.append(f'{where} {y} — 교수 글 빈칸/문자열 아님 {p!r}')
    for k, d in YP.items():
        if k not in keys: X.append(f'YEAR_PROF[{k!r}] — 강의 키 없음(LECMAP·팩 강의 {len(keys)}개)'); continue
        qs = [c for c in cards.values() if c['lec'] == k]
        for y, p in (d or {}).items():
            chk_val(f'YEAR_PROF[{k}]', y, p)
            if isinstance(y, int) and not any(y2(y) in c['yrs'] for c in qs): W.append(f'YEAR_PROF[{k}] {y} — 이 강의에 그 해 문항 없음')
            elif isinstance(y, int) and isinstance(p, str):
                bad = [q for q, c in cards.items() if c['lec'] == k and y2(y) in c['yrs'] and q not in YQ and c['yp'] and c['yp'].get(y2(y)) != p.strip()]
                if bad: W.append(f'YEAR_PROF[{k}] {y} {p} — 카드 data-yp가 다름 {bad[:4]}(빌드 전 팩?)')
    for q, d in YQ.items():
        if q not in cards: X.append(f'YEAR_PROF_Q[{q!r}] — 문항 없음'); continue
        for y, p in (d or {}).items():
            chk_val(f'YEAR_PROF_Q[{q}]', y, p)
            if isinstance(y, int) and y2(y) not in cards[q]['yrs']: W.append(f'YEAR_PROF_Q[{q}] {y} — 이 문항 출제 연도에 없음({sorted(cards[q]["yrs"], reverse=True)})')
    return X, W, len(YP), len(YQ)
def main():
    tot = 0
    for SID in [s.upper() for s in sys.argv[1:]] or SIDS:
        X, W, nl, nq = audit(SID); tot += len(X)
        print(f'{SID}: ✗ {len(X)} · △ {len(W)} (강의 {nl} · 문항 예외 {nq})')
        for x in X: print('  ✗', x)
        for w in W[:12]: print('  △', w)
        if len(W) > 12: print(f'  △ … +{len(W) - 12}')
    print('RESULT', 'PASS' if not tot else f'FAIL {tot}'); return 1 if tot else 0
if __name__ == '__main__': sys.exit(main())
