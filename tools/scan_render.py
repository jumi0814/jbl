"""10-05 화면 렌더 결함 스캐너 — 빌드된 팩(docs/packs/<SID>.js)의 모든 HTML(정리본 학습·정리표·비교표·JB 카드·예상·과목 비교표·한눈표)에서
  글자 깨짐(사용 영역 자리표시 \\ue000~\\uf8ff·U+FFFD) · 원고 표기 누출({r: {jb: [[ ** ==) · 홀로 남은 문장부호 줄 · 빈 항목 · 인용 상자 따옴표 짝 · 괄호 짝(블록 단위) 을 찾음
  .venv/bin/python tools/scan_render.py [SID…]   → 요약 + work/review_scan/<SID>.md(자리·글자)"""
import os, sys, re, collections
from bs4 import BeautifulSoup
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools')); import jblpaths as J
SIDS = [a.upper() for a in sys.argv[1:]] or ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
PUA = re.compile(r'[-�]')
LEAK = re.compile(r'\{r:|\{n:|\{u:|\{e:|\ue030|\ue031|\ue032|\ue033|\ue034|\ue035|\ue036|\ue037|\ue038|\ue039|\{jb:|\[\[|\*\*|(?<![=<>!])==(?!=)')
BLK = ['li', 'div', 'td', 'th', 'blockquote', 'p']
os.makedirs(os.path.join(ROOT, 'work', 'review_scan'), exist_ok=True)
tot = 0
for SID in SIDS:
    P = J._load_js(os.path.join(ROOT, 'docs', 'packs', SID + '.js')); out = collections.defaultdict(list)
    def scan(h, where):
        if not h or not isinstance(h, str): return
        if PUA.search(h): out['깨진 글자'].append((where, PUA.findall(h)[:5], re.sub(r'<[^>]+>', '', h[max(0, PUA.search(h).start() - 80):PUA.search(h).start() + 40])))
        soup = BeautifulSoup(h, 'html.parser')
        for el in soup.find_all(BLK):
            if el.find_parent(class_=re.compile(r'^(lines|box0|qtext)$')) or 'ln' in (el.get('class') or []): continue   # JB 원문 줄은 글자 불변 — 제외
            own = ''.join(t for t in el.find_all(string=True, recursive=False)).strip()
            full = re.sub(r'\s+', ' ', el.get_text(' ', strip=True))
            if not el.find(BLK) and LEAK.search(full) and 'noann' not in ' '.join(el.get('class') or []): out['표기 누출'].append((where, LEAK.search(full).group(0), full[:120]))
            if re.fullmatch(r'[.,;:)\]·/]+', full) and not el.find(BLK): out['홀로 남은 부호'].append((where, own, str(el.parent)[:160] if el.parent else ''))
            if el.name == 'li' and not full: out['빈 항목'].append((where, '', str(el)[:100]))
            if el.name == 'blockquote' and 'aq' in (el.get('class') or []):
                if full.count('"') % 2 or full.count('“') != full.count('”'): out['인용 따옴표 짝'].append((where, '', full[:140]))
            if not el.find(BLK) and full.count('(') != full.count(')') and len(full) < 400 and not full.endswith('…') and not re.search(r'\d\)|[a-z가-힣]\)\s', full): out['괄호 짝(블록)'].append((where, '', full[:140]))
    for L in P['lect']:
        for kind in ('learn', 'sum', 'tbl'): scan(L.get(kind), f'{L["k"]}/{kind}')
    for qid, h in P['cards'].items(): scan(h, f'JB {qid}')
    for i, pr in enumerate(P.get('preds') or []): scan(pr.get('html'), f'예상 {i+1}')
    for t in (P.get('tables') or []): scan(t.get('html') if isinstance(t, dict) else t, '과목 비교표')
    scan(P.get('sumall'), '한눈표')
    with open(os.path.join(ROOT, 'work', 'review_scan', SID + '.md'), 'w', encoding='utf-8') as f:
        for k, L in out.items():
            f.write(f'\n## {k} {len(L)}\n'); [f.write(f'- {w} · {a} · {c}\n') for w, a, c in L]
    print(SID, ' · '.join(f'{k} {len(v)}' for k, v in out.items()) or '결함 0'); tot += sum(len(v) for k, v in out.items() if k in ('깨진 글자', '표기 누출', '홀로 남은 부호', '빈 항목'))
print('RESULT', 'PASS' if not tot else f'FAIL {tot}')
