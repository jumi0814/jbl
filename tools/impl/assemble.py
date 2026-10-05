import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_impl as P, subject as S
BASE = J.JBX; SUB = 'IMPL'
NPAGES = {'25': 14, '24': 15, '23': 6}
LECMAP = S.LECMAP

blocks = {}
for ed, n in NPAGES.items():
    out = []
    for x in P.parse(ed, n):
        x['text'] = '\n'.join(x['lines']).strip(); out.append(x)
    blocks[ed] = out
ANSRE = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$')
def stem_of(t):
    out = []
    for l in t.split('\n'):
        if ANSRE.match(l): break
        out.append(l)
    return ' '.join(out)
def tag_years(text):
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = re.sub(r'(반짤반탈|짤 변형|짤|탈|년|NEW|’|\'|~)', ' ', g).replace('，', ',')
        if not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*[,、]\s*(20\d\d|\d\d)?)*\s*', g2): continue
        vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
        if not vs or not all(8 <= v <= 26 for v in vs): continue
        ys |= set(vs); raw.append('(' + g.strip() + ')')
    return ys, raw
def find(ed, sec, num):
    for x in blocks[ed]:
        if x['sec'] == sec and str(x['num']) == str(num): return x
    return None
# 강의별 교수
LK_PROF = {'HIS': '조영단', 'OSS': '한정준', 'PATH': '명훈', 'BIO': '임영준', 'PRO': '김성균', 'PART': '조준호', 'GRAFT': '윤필영'}
# 정본 문항: (id, ed, sec, num)
CANON = [('Q%02d' % i, '25', '2024-3Q', str(i)) for i in range(1, 19)] + \
        [('R%02d' % i, '25', '2023-3Q', str(i)) for i in range(1, 13) if i != 5] + [('R13', '25', '2023-3Q', '추1'), ('R14', '25', '2023-3Q', '추2')] + \
        [('S01', '25', '2022-3Q', '1'), ('S03', '25', '2022-3Q', '3')] + \
        [('T01', '24', '2021-3Q', '1'), ('T02', '24', '2021-3Q', '2'), ('T04', '24', '2021-3Q', '4'), ('R15', '24', '2023-3Q', '15')] + \
        [('U09', '23', '2020-3Q', '9'), ('U10', '23', '2020-3Q', '10')]
# 같은 문제의 다른 수록(판, 칸, 번호) — 연도 합산과 '다른 판본' 표시에 사용
OTHER = {'Q01': [('24', '2023-3Q', '17'), ('24', '2022-3Q', '11'), ('23', '2022-3Q', '11')],
         'Q02': [('25', '2022-3Q', '5'), ('24', '2023-3Q', '18'), ('24', '2022-3Q', '12'), ('23', '2022-3Q', '12')],
         'Q03': [('24', '2023-3Q', '19')],
         'Q06': [('25', '2023-3Q', '5'), ('24', '2023-3Q', '6'), ('24', '2022-3Q', '6'), ('23', '2022-3Q', '6'), ('23', '2020-3Q', '8')],
         'Q07': [('25', '2022-3Q', '2'), ('24', '2022-3Q', '7'), ('24', '2021-3Q', '3'), ('23', '2022-3Q', '7'), ('23', '2021-3Q', '3')],
         'Q08': [('24', '2023-3Q', '14')], 'Q11': [('24', '2023-3Q', '2')], 'Q17': [('24', '2023-3Q', '8')],
         'R01': [('24', '2023-3Q', '1')], 'R02': [('24', '2023-3Q', '3')], 'R03': [('24', '2023-3Q', '4')], 'R04': [('24', '2023-3Q', '5')],
         'R06': [('24', '2023-3Q', '7')], 'R07': [('24', '2023-3Q', '9')], 'R08': [('24', '2023-3Q', '10')],
         'R09': [('25', '2022-3Q', '4'), ('24', '2023-3Q', '11'), ('24', '2022-3Q', '9'), ('23', '2022-3Q', '9')],
         'R10': [('24', '2023-3Q', '12')], 'R11': [('24', '2023-3Q', '13')], 'R12': [('24', '2023-3Q', '16')],
         'R13': [('24', '2023-3Q', '추1')], 'R14': [('24', '2023-3Q', '추2')],
         'S01': [('24', '2022-3Q', '5'), ('23', '2022-3Q', '5')],
         'S03': [('24', '2022-3Q', '8'), ('24', '2021-3Q', '5'), ('23', '2022-3Q', '8'), ('23', '2021-3Q', '5')],
         'T01': [('23', '2021-3Q', '1')], 'T02': [('23', '2021-3Q', '2')], 'T04': [('23', '2021-3Q', '4')]}
CROPS = {}
Q = []
def secyear(sec): return int(sec[2:4])
for cid, ed, sec, num in CANON:
    x = find(ed, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t)
    short = re.sub(r'^\s*(추\s*\d|\d{1,2})\s*[.．]\s*', '', t.split('\n')[0]).strip()
    yrs = set(ty) | {secyear(sec)}
    for (e2, s2, n2) in OTHER.get(cid, []):
        yrs.add(secyear(s2)); x2 = find(e2, s2, n2)
        if x2: yrs |= tag_years(x2['text'])[0]
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': 'A', 'prof': '',
              'src': f'JB {ed}판 · {sec} {num}번', 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True),
              'secy': secyear(sec), 'tal': bool(re.search(r'\(\s*탈\s*\)', stem_of(t))), 'pick': ''})

import emph
EMPH = emph.apply
def cite_html(s, em=False):
    toks = re.split(r'(\[\[[A-Z0-9]+:[^\]]+\]\])', s)
    s = ''.join(t if t.startswith('[[') else (EMPH(html.escape(t, quote=False)) if (em and EMPH) else html.escape(t, quote=False)) for t in toks)
    def rep(m):
        k, p = m.group(1), m.group(2); name = LECMAP[k][1]
        if not LECMAP[k][0]: return f'<button class="cite t" data-k="{k}" data-p="">{name} ‘{p}’</button>'
        return f'<button class="cite" data-k="{k}" data-p="{p}">{name} p.{p}</button>'
    s = re.sub(r'\[\[([A-Z0-9]+):([^\]]+)\]\]', rep, s)
    return s.replace('⚠', '<b class="warn">⚠</b>').replace('💡', '<b class="bulb">💡</b>')
cited = set()
def collect(s):
    for m in re.finditer(r'\[\[([A-Z0-9]+):([^\]]+)\]\]', s):
        k, p = m.group(1), m.group(2)
        if LECMAP.get(k, (None,))[0] and p.isdigit(): cited.add((k, int(p)))
ANN = {}; cur = None
for line in open(DIR + '/annot.txt', encoding='utf-8'):
    line = line.rstrip('\n')
    if line.startswith('@'):
        parts = [p.strip() for p in line[1:].split('|')]
        cur = {'v': '', 'yrs': [], 'yrsnote': '', 'lec': [], 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': [], 'K': []}; ANN[parts[0]] = cur
        for p in parts[1:]:
            k, _, v = p.partition('=')
            if k == 'yrs': cur['yrs'] = [int(y) for y in v.split(',') if y.strip()]
            elif k == 'lec': cur['lec'] = [v] if v else []
            else: cur[k] = v
    elif cur is not None and len(line) > 2 and line[1] == ':' and line[0] in 'AMNK':
        collect(line); cur[line[0]].append(cite_html(line[2:].strip()))
for q in Q:
    a = ANN.get(q['id'])
    if a:
        lk_ = a['lec'][0].split(':')[0] if a['lec'] else ''; lk_ = getattr(S, 'IMG_ALIAS', {}).get(lk_, lk_)
        q.update({'v': a['v'], 'yrsnote': a['yrsnote'], 'rel': a['rel'], 'pair': a['pair'], 'A': a['A'], 'M': a['M'], 'N': a['N'], 'K': a.get('K', []), 'lk': lk_})
        q['yrs'] = sorted(set(q['base']) | set(a['yrs']), reverse=True); q['xtra'] = sorted(set(a['yrs']) - set(q['base']), reverse=True)
    else:
        q.update({'v': 'na', 'yrsnote': '', 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': [], 'K': [], 'lk': '', 'xtra': []}); q['yrs'] = sorted(q['base'], reverse=True)
    q['prof'] = LK_PROF.get(q['lk'], '')
    o = []
    for (e2, s2, n2) in OTHER.get(q['id'], []):
        x2 = find(e2, s2, n2)
        if x2: o.append({'ed': e2, 'sec': s2, 'num': n2, 'pg': x2['pg'], 'pg2': x2['pg2'], 'text': x2['text']})
    q['other'] = o; q['lab24'] = ''; q['crops'] = CROPS.get(q['id'], {})
    q['fig'] = bool(re.search(r'그림|모식도|아래와 같이|아래 빈칸', ' '.join(q['text'].split('\n')[:3])))

LECT = []; TABLES = []
PRED = []; cur = None
for line in open(DIR + '/pred.txt', encoding='utf-8'):
    line = line.rstrip('\n')
    if line.startswith('@'):
        p = [x.strip() for x in (line[3:] if line.startswith('@P ') else line[1:]).split('|')]
        cur = {'k': p[0], 't': '', 'b': '', 'q': '', 'a': ''}
        for x in p[1:]:
            k, _, v = x.partition('='); cur[k] = v
        PRED.append(cur)
    elif line.startswith('Q:') and cur: cur['q'] = cite_html(line[2:].strip()); cur['q_raw'] = line[2:].strip()
    elif line.startswith('A:') and cur: collect(line); cur['a'] = cite_html(line[2:].strip()); cur['a_raw'] = line[2:].strip()
def b64(im, q):
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
IMG = {'jb': {}, 'lec': {}, 'crop': {}}
for ed, n in NPAGES.items():
    man = json.load(open(f'{BASE}{SUB}_20{ed}/manifest.json'))
    vis = {p['page_number'] for p in man['pages'] if p.get('has_visual_content')}
    for i in range(1, n + 1):
        if not os.path.exists(f'{BASE}{SUB}_20{ed}/{i}.jpeg'):   # JB 쪽 이미지가 없는 환경(클라우드 세션) — 지금 docs/packs의 쪽 이미지를 그대로(tools/jblpaths.prev_jb_pages)
            IMG['jb'][f'{ed}-{i}'] = J.prev_jb_pages(SUB)[f'{ed}-{i}']; continue
        im = Image.open(f'{BASE}{SUB}_20{ed}/{i}.jpeg').convert('RGB')
        if i in vis: IMG['jb'][f'{ed}-{i}'] = b64(im, 50)
        else: IMG['jb'][f'{ed}-{i}'] = b64(im.convert('L').resize((860, int(im.size[1] * 860 / im.size[0]))), 32)
LEDGER = []
idmap = {(q['ed'], q['sec'], str(q['num'])): q['id'] for q in Q}
rev = {}
for cid, lst in OTHER.items():
    for (e2, s2, n2) in lst: rev.setdefault((e2, s2, str(n2)), []).append(cid)
for ed in NPAGES:
    for x in blocks[ed]:
        key = (ed, x['sec'], str(x['num'])); first = x['text'].split('\n')[0][:70]
        if key in idmap: st, to = 'card', [idmap[key]]
        elif key in rev: st, to = 'dup', rev[key]
        else: st, to = 'ref', []
        LEDGER.append({'ed': ed, 'sec': x['sec'], 'num': x['num'], 'pg': x['pg'], 'first': first, 'st': st, 'to': to})
def ment(ed, pages):
    t = ''
    for p in pages:
        s = P.rd(f'{BASE}{SUB}_20{ed}/{p}.txt'); t += '\n'.join(l for l in s.split('\n') if '무단인쇄' not in l and l.strip()) + '\n'
    return t.strip()
MENT = {'25': ment('25', [1]), '24': ment('24', [1]), '23': ment('23', [1])}
if __name__ == '__main__':
    print('Q', len(Q)); 
    for q in Q: print(q['id'], q['yrs'], q['jbtag'], q['short'][:40])
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [(r['ed'], r['sec'], r['num'], r['first'][:25]) for r in LEDGER if r['st'] == 'ref'])
