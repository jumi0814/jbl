"""화면 줄바꿈 전수 덤프 2판(10-04 사용자 '정리본과 jb 등 모든 곳에서 줄바꿈 오류 전수조사') — 빌드된 팩(docs/packs/<SID>.js)의 HTML에서
목록·조각으로 나뉘어 보이는 모든 덩어리(ul/ol 목록 · .kp 조각 줄 · 🔑 .kl/.ksi 줄 · .klead 머리)를 찾아 화면 그대로 조각을 적는다.
정리본 학습(learn)·정리표(sum)·강의 비교표(tbl)·JB 카드(대조·해설·답·주변부)·예상문제·과목 비교표·기출 한눈표 전부.
  .venv/bin/python tools/dump_breaks2.py <SID>   → work/review_breaks2/<SID>_lec.md(정리본 학습·정리표·강의 비교표) · <SID>_jb.md(JB·예상·과목 비교표·한눈표)  (⚑ = 의심 표시가 붙은 덩어리 먼저)"""
import os, sys, re, json
from bs4 import BeautifulSoup, NavigableString
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools')); import jblpaths as J
SID = sys.argv[1].upper()
P = J._load_js(os.path.join(ROOT, 'docs', 'packs', SID + '.js'))
SKIPC = {'noann', 'cite', 'jbchip', 'xjb', 'figchip', 'ey', 'ych', 'clab'}
def txt(el):
    for k in el.find_all(class_='kh') if hasattr(el, 'find_all') else []: k.replace_with(' ')
    return re.sub(r'\s+', ' ', el.get_text(' ', strip=True)).strip()
def flags(pieces):
    f = []
    for i, p in enumerate(pieces):
        q = p.lstrip('• ').strip()
        if not q: continue
        if re.match(r'^(—|–|-|→|·|,|\)|\]|”|’|은 |는 |이 |가 |을 |를 |로 |으로 |의 |에 |와 |과 |및 |또는 )', q): f.append(f'조각 {i+1}이 이어지는 말로 시작')
        if i and re.match(r'^[a-z][a-z]+ [a-z]', q) and not re.search(r'[.:)!?]$', pieces[i-1].strip()): f.append(f'조각 {i+1}이 앞 조각 문장 중간(소문자로 이어짐)')
        if q.count('(') != q.count(')'): f.append(f'조각 {i+1} 괄호 짝 안 맞음')
        if q.count('"') % 2 or q.count('“') != q.count('”'): f.append(f'조각 {i+1} 따옴표 짝 안 맞음')
        if len(q) <= 3 and not re.match(r'^[①-⑳\d]', q): f.append(f'조각 {i+1}이 너무 짧음({q!r})')
        if i + 1 < len(pieces) and re.search(r'(각각|및|또는|와|과|의|에서|으로|로|을|를|이|가|은|는|—|→|,)$', q): f.append(f'조각 {i+1}이 이어질 말로 끝남')
    return f
out_f, out_n = [], []
def scan(html, where):
    if not html or not isinstance(html, str): return
    soup = BeautifulSoup(html, 'html.parser')
    seen = set()
    # 1) 목록 ul/ol (가장 바깥 목록만 — 안쪽은 들여쓰기로)
    for L in soup.find_all(['ul', 'ol']):
        if L.find_parent(['ul', 'ol']) or id(L) in seen: continue
        if set(L.get('class') or []) & {'hlist', 'steps', 'tqs'}: pass
        lis = L.find_all('li', recursive=False)
        if len(lis) < 2: continue
        lead = L.find_previous_sibling(class_='klead')
        pieces = []
        def walk(ul, d):
            for li in ul.find_all('li', recursive=False):
                sub = li.find(['ul', 'ol'])
                if sub:
                    own = ''.join(str(c) for c in li.children if c is not sub)
                    pieces.append(('  ' * d) + '• ' + txt(BeautifulSoup(own, 'html.parser')))
                    walk(sub, d + 1)
                else:
                    kps = li.find_all(class_=['klead', 'kp', 'kl'], recursive=False)
                    if kps:
                        rest = ''.join(str(c) for c in li.children if c not in kps and not (getattr(c, 'get', None) and 'cites' in (c.get('class') or [])))
                        if txt(BeautifulSoup(rest, 'html.parser')): pieces.append(('  ' * d) + '• ' + txt(BeautifulSoup(rest, 'html.parser')))
                        for k in kps: pieces.append(('  ' * d) + ('• [머리] ' if 'klead' in (k.get('class') or []) else '  ‣ ') + txt(k))
                    else: pieces.append(('  ' * d) + '• ' + txt(li))
        walk(L, 0)
        ctx = where(L)
        blk = ([f'[머리] {txt(lead)}'] if lead else []) + pieces
        (out_f if flags([p.strip() for p in pieces]) else out_n).append((ctx, blk, flags([p.strip() for p in pieces])))
    # 2) 조각 줄(.kp)·🔑 줄(.kl)·단계(.ksi) — 같은 부모 아래 둘 이상
    for cls in ('kp', 'kl', 'ksi', 'ksub'):
        parents = {}
        for e in soup.find_all(class_=cls):
            parents.setdefault(id(e.parent), (e.parent, []))[1].append(e)
        for _, (par, es) in parents.items():
            if len(es) < 2 and cls != 'ksub': continue
            if cls == 'ksub':   # 요지 둘째 줄 — 첫 줄(ksub 앞 글자 전부) + 둘째 줄
                head = ''.join(str(c) for c in par.children if not (getattr(c, 'get', None) and 'ksub' in (c.get('class') or [])))
                pieces = ['• ' + txt(BeautifulSoup(head, 'html.parser'))] + ['• ' + txt(e) for e in es]
            else: pieces = ['• ' + txt(e) for e in es if txt(e)]
            if len(pieces) < 2: continue
            fl = flags([p for p in pieces])
            (out_f if fl else out_n).append((where(par), pieces, fl))
def lec_where(L, kind):
    def w(el):
        art = el.find_parent('article')
        if art is not None:
            t = art.find(class_='en'); return f'{L["k"]} {kind} · 카드 「{txt(t) if t else art.get("id")}」'
        tr = el.find_parent('tr')
        if tr is not None:
            th = tr.find('th'); return f'{L["k"]} {kind} · 행 「{txt(th)[:60] if th else ""}」'
        h = el.find_previous(['h2', 'h3']); return f'{L["k"]} {kind} · {txt(h)[:60] if h else ""}'
    return w
for L in P['lect']:
    for kind in ('learn', 'sum', 'tbl'):
        scan(L.get(kind), lec_where(L, {'learn': '학습', 'sum': '정리표', 'tbl': '비교표'}[kind]))
for qid, h in P['cards'].items():
    def w(el, qid=qid):
        sec = el.find_parent(class_=re.compile(r'^(ans|qa|ann|agree|aex|qn|qbody|peri|other)'))
        c = (sec.get('class') or [''])[0] if sec is not None else ''
        return f'JB {qid} · {c}'
    scan(h, w)
for i, pr in enumerate(P.get('preds') or []):
    scan(pr.get('html'), lambda el, i=i: f'예상문제 {i+1}')
scan(P.get('tables') if isinstance(P.get('tables'), str) else None, lambda el: '과목 비교표')
if isinstance(P.get('tables'), list):
    for t in P['tables']: scan(t.get('html') if isinstance(t, dict) else t, lambda el: '과목 비교표')
scan(P.get('sumall'), lambda el: '기출 한눈표')
os.makedirs(os.path.join(ROOT, 'work', 'review_breaks2'), exist_ok=True)
for part, test in (('lec', lambda c: not (c.startswith('JB ') or c.startswith('예상문제') or c in ('과목 비교표', '기출 한눈표'))), ('jb', lambda c: c.startswith('JB ') or c.startswith('예상문제') or c in ('과목 비교표', '기출 한눈표'))):
    F = [x for x in out_f if test(x[0])]; N = [x for x in out_n if test(x[0])]
    p = os.path.join(ROOT, 'work', 'review_breaks2', f'{SID}_{part}.md')
    with open(p, 'w', encoding='utf-8') as f:
        f.write(f'# {SID} 화면 줄바꿈 전수 덤프 2판 ({part}) — 덩어리 {len(F) + len(N)} (⚑ 의심 {len(F)})\n\n## ⚑ 의심 표시가 붙은 덩어리\n')
        for ctx, blk, fl in F: f.write(f'\n### {ctx}\n⚑ ' + ' · '.join(dict.fromkeys(fl)) + '\n' + '\n'.join('    ' + b for b in blk) + '\n')
        f.write('\n## 나머지 덩어리(의심 표시 없음 — 그래도 전부 읽어 볼 것)\n')
        for ctx, blk, fl in N: f.write(f'\n### {ctx}\n' + '\n'.join('    ' + b for b in blk) + '\n')
print(SID, '덩어리', len(out_f) + len(out_n), '⚑', len(out_f), '→', p)
