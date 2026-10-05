import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_anat as P, subject as S
BASE = J.JBX; SUB = 'ANAT'
NPAGES = {'25': 22, '24': 6, '23': 26}
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
        g2 = re.sub(r'(반짤반탈|짤 변형|짤|탈|년|NEW|’|\'|~|\.)', ' ', g).replace('，', ',')
        if not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*[,、\s]\s*(20\d\d|\d\d)?)*\s*', g2): continue   # (24. 23)처럼 마침표·공백 구분도 읽음
        vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
        if not vs or not all(8 <= v <= 26 for v in vs): continue
        ys |= set(vs); raw.append('(' + g.strip() + ')')
    return ys, raw
def find(ed, sec, num):
    for x in blocks[ed]:
        if x['sec'] == sec and str(x['num']) == str(num): return x
    return None
LK_PROF = {'NECK': '명훈', 'NV': '권익재', 'LIP': '양훈주', 'MAND': '서병무', 'PAR': '서미현', 'MAX': '서병무', 'TMJ': '박주영'}
CANON = [('Q%02d' % i, '25', '2024', str(i), 'A') for i in range(1, 21)] + \
        [('R%02d' % i, '25', '2023', str(i), 'A') for i in range(1, 13)] + [('R13', '25', '2023', '추가복원1', 'A'), ('R14', '25', '2023', '추가복원2', 'A')] + \
        [('S%02d' % i, '25', '2022', str(i), 'A') for i in range(1, 10)] + [('S11', '23', '2022', '11', 'A')] + \
        [('T01', '23', '2021', '1', 'B'), ('T02', '23', '2021', '2', 'B'), ('T03', '23', '2021', '3', 'B'), ('T06', '23', '2021', '6', 'A'), ('T13', '23', '2021', '13', 'A'),
         ('T14', '23', '2021', '14', 'A'), ('T15', '23', '2021', '15', 'A'), ('T16', '23', '2021', '16', 'A'), ('T17', '23', '2021', '17', 'A'), ('T20', '23', '2021', '20', 'A'),
         ('T21', '23', '2021', '21', 'A'), ('T22', '23', '2021', '22', 'A'), ('T23', '23', '2021', '23', 'A')] + \
        [('U03', '23', '2020', '3', 'B'), ('U05', '23', '2020', '5', 'B'), ('U06', '23', '2020', '6', 'A'), ('U07', '23', '2020', '7', 'A'), ('U09', '23', '2020', '9', 'A'),
         ('U11', '23', '2020', '11', 'A'), ('U12', '23', '2020', '12', 'A'), ('U13', '23', '2020', '13', 'A'), ('U14', '23', '2020', '14', 'A'), ('U15', '23', '2020', '15', 'A'),
         ('U23', '23', '2020', '23', 'B'), ('U24', '23', '2020', '24', 'B')] + \
        [('M01', '25', '2018', '1', 'A'), ('M02', '25', '2018', '2', 'A'), ('M03', '25', '2018', '3', 'A'), ('M04', '25', '2017', '4', 'A')]
OTHER = {'Q01': [('24', '2021', '5'), ('23', '2021', '5')],
         'Q02': [('24', '2023', '1'), ('24', '2022', '16'), ('24', '2021', '4'), ('23', '2022', '16'), ('23', '2021', '4'), ('23', '2020', '10')],
         'Q03': [('24', '2022', '19'), ('23', '2022', '19'), ('23', '2020', '8')],
         'Q04': [('24', '2023', '2')], 'Q07': [('23', '2022', '12'), ('23', '2022', '13')], 'Q09': [('23', '2020', '17')], 'Q11': [('23', '2022', '14')],
         'Q13': [('23', '2022', '3'), ('23', '2020', '22')], 'Q14': [('23', '2022', '1'), ('23', '2021', '11'), ('23', '2020', '19'), ('23', '2020', '20')],
         'Q15': [('23', '2022', '2'), ('23', '2021', '12'), ('23', '2020', '21')], 'Q19': [('23', '2022', '22'), ('23', '2022', '23')],
         'R01': [('24', '2023', '3')], 'R02': [('24', '2023', '4')], 'R05': [('23', '2022', '7'), ('23', '2022', '10')], 'R07': [('23', '2021', '8')],
         'R09': [('23', '2022', '21'), ('23', '2021', '9'), ('23', '2021', '10')],
         'S01': [('23', '2022', '4')], 'S02': [('23', '2022', '5'), ('23', '2022', '6')], 'S03': [('23', '2022', '8')], 'S04': [('23', '2022', '9')],
         'S05': [('24', '2022', '15'), ('23', '2022', '15')], 'S06': [('24', '2022', '17'), ('23', '2022', '17')], 'S07': [('24', '2022', '18'), ('23', '2022', '18')],
         'S08': [('23', '2022', '24')], 'S09': [('23', '2022', '20'), ('23', '2021', '7')],
         'T01': [('23', '2020', '1')], 'T03': [('23', '2020', '2'), ('23', '2020', '4')], 'T06': [('24', '2021', '6')], 'T13': [('23', '2020', '22')],
         'T14': [('23', '2021', '18')], 'T15': [('23', '2021', '19')], 'U13': [('23', '2020', '16')], 'U14': [('23', '2020', '18')],
         'M01': [('23', '2018', '1')], 'M02': [('23', '2018', '2')], 'M03': [('23', '2018', '3')], 'M04': [('23', '2017', '4')]}
CROPS = {}
Q = []
def secyear(sec): return int(sec) % 100
for cid, ed, sec, num, tier in CANON:
    x = find(ed, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t)
    short = re.sub(r'^\s*(추가복원\s*\d|\d{1,2}(-\d)?)\s*[.．)]\s*', '', t.split('\n')[0]).strip()
    yrs = set(ty) | {secyear(sec)}
    for (e2, s2, n2) in OTHER.get(cid, []):
        yrs.add(secyear(s2)); x2 = find(e2, s2, n2)
        if x2: yrs |= tag_years(x2['text'])[0]
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': tier, 'prof': x['prof'],
              'src': f'JB {ed}판 · {sec}년 칸 · {x["prof"]} {num}번', 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True),
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
        cur = {'v': '', 'yrs': [], 'yrsnote': '', 'lec': [], 'rel': '', 'pair': '', 'prof': '', 'A': [], 'M': [], 'N': [], 'K': []}; ANN[parts[0]] = cur
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
        if a['prof']: q['prof'] = a['prof']
    else:
        q.update({'v': 'na', 'yrsnote': '', 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': [], 'K': [], 'lk': '', 'xtra': []}); q['yrs'] = sorted(q['base'], reverse=True)
    if q['tier'] == 'A' and q['lk']: q['prof'] = LK_PROF.get(q['lk'], q['prof'])
    o = []
    for (e2, s2, n2) in OTHER.get(q['id'], []):
        x2 = find(e2, s2, n2)
        if x2: o.append({'ed': e2, 'sec': s2 + '년 칸', 'num': n2, 'pg': x2['pg'], 'pg2': x2['pg2'], 'text': x2['text']})
    q['other'] = o; q['lab24'] = ''; q['crops'] = CROPS.get(q['id'], {})
    q['fig'] = bool(re.search(r'그림|모식도|사진|아래와 같이|빈칸빵|가리키는|표시', ' '.join(q['text'].split('\n')[:3])))
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
        LEDGER.append({'ed': ed, 'sec': x['sec'] + '년', 'num': x['num'], 'pg': x['pg'], 'first': first, 'st': st, 'to': to})
def ment(ed, pages):
    t = ''
    for p in pages:
        s = P.rd(f'{BASE}{SUB}_20{ed}/{p}.txt'); t += '\n'.join(l for l in s.split('\n') if '무단인쇄' not in l and l.strip()) + '\n'
    return t.strip()
MENT = {'25': ment('25', [1]), '24': ment('24', [1]), '23': ment('23', [1])}
if __name__ == '__main__':
    print('Q', len(Q))
    for q in Q: print(q['id'], q['tier'], q['prof'], q['yrs'], q['jbtag'], q['short'][:36])
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [(r['ed'], r['sec'], r['num'], r['first'][:28]) for r in LEDGER if r['st'] == 'ref'])
