"""10-05 사용자 '동그라미 123~ 에 또 새로 동그라미 123~으로 넘버링하고 들여쓰기도 없어서 헷갈리는' — 렌더된 화면에서 같은 단계(같은 목록·같은 카드의 형제 줄)에 원문자 번호가 ①로 다시 시작하는 곳을 셈.
  .venv/bin/python tools/check_numbering.py [SID…] → 요약 + work/review_scan/NUM_<SID>.md"""
import os, sys, re
from bs4 import BeautifulSoup
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'tools')); import jblpaths as J
C = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮'
SIDS = [a.upper() for a in sys.argv[1:]] or ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
def lead(t):
    t = t.strip(); return C.index(t[0]) if t and t[0] in C else None
def sibruns(par, kids, where, out):
    seq = [(lead(re.sub(r'\s+', ' ', k.get_text(' ', strip=True))), k) for k in kids]
    prev = None
    for n, k in seq:
        if n is None: continue
        if prev is not None and n == 0 and prev >= 1: out.append((where, re.sub(r'\s+', ' ', k.get_text(' ', strip=True))[:90]))
        prev = n
tot = 0
for S in SIDS:
    P = J._load_js(os.path.join(ROOT, 'docs', 'packs', S + '.js')); out = []
    def scan(h, where):
        if not isinstance(h, str) or not h: return
        s = BeautifulSoup(h, 'html.parser')
        for L in s.find_all(['ul', 'ol']): sibruns(L, L.find_all('li', recursive=False), where, out)
        for tb in s.find_all(class_='tbody'):
            grp = []
            for c in tb.find_all(recursive=False):
                cl = c.get('class') or []
                if c.name == 'div' and 'li' in cl and 'l2' not in cl: grp.append(c)
                elif c.name == 'div' and 'li' in cl and 'l2' in cl: continue
                else: sibruns(tb, grp, where, out); grp = []
            sibruns(tb, grp, where, out)
        for ab in s.select('.ab'): sibruns(ab, ab.find_all(['div', 'li'], recursive=False), where, out)
    for L in P['lect']: scan(L.get('learn'), f'{L["k"]}/학습')
    for q, h in P['cards'].items(): scan(h, f'JB {q}')
    open(os.path.join(ROOT, 'work', 'review_scan', f'NUM_{S}.md'), 'w', encoding='utf-8').write('\n'.join(f'- {w} · {t}' for w, t in out))
    print(S, len(out)); [print('   ', w, '·', t) for w, t in out[:6]]; tot += len(out)
print('합계', tot)
