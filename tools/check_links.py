"""10-05 기능 연동 검사 — 빌드된 팩에서
  ① 인용 칩(cite data-k·data-p·data-pp)이 가리키는 쪽 이미지가 이미지 청크에 있는지(imgalias 반영)
  ② JB 카드 '📖 정리본' 칩(data-golec K:j)이 실제 카드를 가리키고 그 카드 ⭐/jb=에 이 문항이 있는지
  ③ 정리본·표·예상의 기출 칩(data-go / {jb:})이 있는 문항인지
  .venv/bin/python tools/check_links.py [SID…]"""
import os, sys, re, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools')); import jblpaths as J
SIDS = [a.upper() for a in sys.argv[1:]] or ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
bad_all = 0
for SID in SIDS:
    P = J._load_js(os.path.join(ROOT, 'docs', 'packs', SID + '.js')); have = set()
    for f in [x for x in glob.glob(os.path.join(ROOT, 'docs', 'packs', SID + '.img.*.js')) if not re.search(r'\.img\.jb\d*\.js$', x)]:
        t = open(f, encoding='utf-8').read(); i = t.index('{'); j = t.rindex('}')
        try: o = json.loads(t[i:j + 1]); have |= set((o.get('lec') or {}).keys())
        except Exception as e: print('  ? 청크 읽기 실패', f, e)
    alias = P.get('imgalias') or {}
    htmls = [(f'{L["k"]}/{k}', L.get(k) or '') for L in P['lect'] for k in ('learn', 'sum', 'tbl')] + [(f'JB {q}', h) for q, h in P['cards'].items()] + [(f'예상 {i}', p.get('html', '')) for i, p in enumerate(P.get('preds') or [])] + [('비교표', t.get('html', '') if isinstance(t, dict) else t) for t in P.get('tables') or []] + [('한눈표', P.get('sumall') or '')]
    miss, gobad, lecbad = [], [], []
    def img_ok(k, p):
        for kk in [k] + ([alias[k]] if isinstance(alias.get(k), str) else list(alias.get(k) or [])):
            if f'{kk}-{p}' in have: return True
        return any(x.endswith(f'-{p}') and x.split('-')[0] in (alias.get(k) if isinstance(alias.get(k), list) else [alias.get(k)]) for x in have)
    for w, h in htmls:
        if not isinstance(h, str): continue
        for m in re.finditer(r'<button class="cite[^"]*" data-k="([^"]*)" data-p="([^"]*)"(?: data-pp="([^"]*)")?', h):
            k, p, pp = m.groups()
            for pg in (pp.split(',') if pp else [p]):
                if pg and pg.isdigit() and not img_ok(k, pg): miss.append(f'{w} → {k}:{pg}')
        for m in re.finditer(r'data-go="([^"]+)"', h):
            if m.group(1) not in P['cards']: gobad.append(f'{w} → {m.group(1)}')
    lmap = {L['k']: L for L in P['lect']}
    for q, h in P['cards'].items():
        for m in re.finditer(r'data-golec="([A-Z0-9]+):(\d+)"', h):
            L = lmap.get(m.group(1))
            if not L: lecbad.append(f'JB {q} → 없는 강의 {m.group(1)}'); continue
            arts = re.findall(r'<article class="tc[^"]*" id="t-%s-(\d+)"' % m.group(1), L['learn'])
            if m.group(2) not in arts: lecbad.append(f'JB {q} → 없는 카드 {m.group(1)}:{m.group(2)}'); continue
            seg = L['learn'][L['learn'].index(f'id="t-{m.group(1)}-{m.group(2)}"'):]
            seg = seg[:seg.find('<article', 10) if seg.find('<article', 10) > 0 else len(seg)]
            if f'data-go="{q}"' not in seg: lecbad.append(f'JB {q} → 카드 {m.group(1)}:{m.group(2)}에 이 문항 칩 없음')
    n = len(miss) + len(gobad) + len(lecbad); bad_all += n
    print(f'{SID}: 쪽 이미지 없는 인용 {len(miss)} · 없는 문항 칩 {len(gobad)} · 📖 연결 어긋남 {len(lecbad)}')
    for x in (miss[:8] + gobad[:8] + lecbad[:12]): print('   ', x)
print('RESULT', 'PASS' if not bad_all else f'FAIL {bad_all}')
