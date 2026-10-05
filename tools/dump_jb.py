"""10-05 JB 해설 화면 덤프 — 빌드된 팩의 JB 카드마다 문제 · JB 답 줄 · 🔎 대조(꼬리표·위치·❝인용 줄·설명·[근거]) · 🧭 주변부(소절 ## · 항목) · [메모]를
  화면에 보이는 줄 그대로 적음(검토용). .venv/bin/python tools/dump_jb.py <SID> → work/review_jb/<SID>.md"""
import os, sys, re
from bs4 import BeautifulSoup, NavigableString, Tag
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools')); import jblpaths as J
SID = sys.argv[1].upper(); P = J._load_js(os.path.join(ROOT, 'docs', 'packs', SID + '.js'))
BLK = {'div', 'li', 'ul', 'ol', 'blockquote', 'p', 'section', 'details', 'table', 'tr', 'h5', 'summary'}
def T(el): return re.sub(r'\s+', ' ', el.get_text(' ', strip=True)).strip()
def isblk(c): return isinstance(c, Tag) and c.name in BLK
def walk(el, d, out):
    buf = []
    def flush():
        t = re.sub(r'\s+', ' ', ''.join(buf)).strip()
        if t: out.append('  ' * d + t)
        buf.clear()
    for c in el.children:
        if isinstance(c, NavigableString): buf.append(str(c)); continue
        if not isinstance(c, Tag): continue
        cl = c.get('class') or []
        if c.name in ('h5', 'summary') or 'amgh' in cl:
            if 'amgh' in cl: flush(); out.append('  ' * d + '## ' + T(c))
            continue
        if not isblk(c): buf.append((f'[{T(c)}] ' if 'vtag' in cl else T(c) + ' ')); continue
        flush()
        if 'cites' in cl: out.append('  ' * d + '[근거] ' + T(c)); continue
        if c.name == 'blockquote': [out.append('  ' * (d + 1) + '❝ ' + T(q)) for q in c.find_all(class_='ql')] or out.append('  ' * (d + 1) + '❝ ' + T(c)); continue
        if c.name == 'table': out.append('  ' * d + '[표] ' + ' | '.join(T(r) for r in c.find_all('tr'))); continue
        if 'note' in cl: out.append('  ' * d + '[메모] ' + T(c)); continue
        pre = '• ' if c.name == 'li' else ''
        if pre and not any(isblk(x) for x in c.children): out.append('  ' * d + pre + T(c)); continue
        if pre: sub = []; walk(c, d + 1, sub); out.append('  ' * d + '•' + (sub[0].strip() if sub else '')); out.extend(sub[1:]); continue
        walk(c, d + (1 if c.name in ('ul', 'ol') else 0), out)
    flush()
os.makedirs(os.path.join(ROOT, 'work', 'review_jb'), exist_ok=True)
fo = open(os.path.join(ROOT, 'work', 'review_jb', SID + '.md'), 'w', encoding='utf-8')
for qid, h in P['cards'].items():
    s = BeautifulSoup(h, 'html.parser'); a = s.find('article')
    fo.write(f'\n\n==================== {qid} ====================\n')
    q = s.find(class_='qtext'); fo.write('문제: ' + (T(q) if q else '') + '\n')
    ja = s.find(class_='jbans')
    if ja: fo.write('[JB 답]\n' + '\n'.join('  ' + T(l) for l in ja.find_all(class_='ln')) + '\n')
    for sec, nm in (('chk', '🔎 대조'), ('more', '🧭 주변부')):
        e = s.find(class_=lambda c: c and 'ab' in c.split() and sec in c.split()) if False else s.select_one(f'.ab.{sec}')
        if not e: continue
        out = []; walk(e, 1, out); fo.write(f'[{nm}]\n' + '\n'.join(out) + '\n')
fo.close(); print(SID, len(P['cards']), '문항 →', f'work/review_jb/{SID}.md')
