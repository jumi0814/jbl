import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_geri as P, subject as S
BASE = J.JBX; SUB = 'GERI'
NPAGES = {'25': 16, '24': 24, '23': 26}
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
def tag_years(text, ed='25', sec='2024'):
    ys, raw = set(), []
    secy = int(sec) % 100
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = re.sub(r'(반짤반탈|짤 변형|짤|탈|년도|년|NEW|’|\'|~|\.|번과 유사|유사|학번)', ' ', g).replace('，', ',')
        if not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*[,、\-]\s*(20\d\d|\d\d)?)*\s*', g2): continue
        vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
        if not vs or not all(5 <= v <= 26 for v in vs): continue
        if '-' in g2 and len(vs) == 2: vs = list(range(min(vs), max(vs) + 1))
        out = []
        for v in vs:
            if ed in ('24', '23'):
                out.append(v + 2 if v + 2 < secy else v)   # 학번 → 연도(+2); 자기 학번 이후면 연도 그대로
            else: out.append(v)
        ys |= set(out); raw.append('(' + g.strip() + ')')
    return ys, raw
def find(ed, sec, num, prof=None):
    for x in blocks[ed]:
        if x['sec'] == sec and str(x['num']) == str(num) and (prof is None or x['prof'] == prof): return x
    return None
LK_PROF = {'HARD': '유연지', 'OHQ': '한동헌', 'ENDO': '이우철', 'BLE': '금기연', 'SAL': '고홍섭', 'PAIN': '장지희', 'PSY': '변민수'}
def C(pfx, ed, sec, nums, tier='A', start=1, prof=None):
    return [(f'{pfx}{start + i:02d}', ed, sec, str(n), tier, prof) for i, n in enumerate(nums)]
CANON = [('Y01', '25', '2024', '1', 'A', '유연지')] + C('H', '25', '2024', range(1, 12), prof='한동헌') + C('E', '25', '2024', range(1, 6), prof='이우철') + [('K01', '25', '2024', '1', 'A', '금기연')] + \
        C('G', '25', '2024', range(1, 7), prof='고홍섭') + C('J', '25', '2024', range(1, 6), prof='장지희') + [('B01', '25', '2024', '1', 'A', '변민수')] + \
        C('E', '25', '2023', range(1, 5), start=7, prof='이우철') + C('G', '25', '2023', [1, 2], start=7, prof='고홍섭') + C('J', '25', '2023', [1, 2], start=6, prof='장지희') + C('B', '25', '2023', [1, 2], start=2, prof='변민수') + \
        C('E', '25', '2022', [1, 2], start=11, prof='이우철') + [('G09', '25', '2022', '1', 'A', '고홍섭')] + C('J', '25', '2022', [1, 2], start=8, prof='장지희') + [('B04', '25', '2022', '1', 'A', '변민수')] + \
        [('C01', '24', '2023', '1', 'B'), ('C02', '24', '2023', '2', 'B'), ('C03', '24', '2023', '4', 'B'), ('C04', '24', '2023', '5', 'B'), ('K02', '24', '2023', '12', 'A')] + \
        C('Y', '24', '2022', [2, 3, 4, 5], start=2) + [('C05', '24', '2022', '7', 'B'), ('C06', '24', '2022', '9', 'B'), ('C07', '24', '2022', '11', 'B'), ('C08', '24', '2022', '12', 'B')] + \
        [('C09', '24', '2021', '3', 'B'), ('C10', '24', '2021', '4', 'B'), ('C11', '24', '2021', '5', 'B'), ('E13', '24', '2021', '7', 'A'), ('G10', '24', '2021', '14', 'A'), ('J11', '24', '2021', '19', 'A'), ('J10', '24', '2021', '22', 'A')] + \
        C('P', '24', '2021', [23, 24, 25, 26]) + \
        [('C12', '23', '2021', '8', 'B'), ('C13', '23', '2020', '4', 'B'), ('C14', '23', '2020', '6', 'B'), ('C15', '23', '2020', '7', 'B'), ('J12', '23', '2020', '10', 'A'), ('J13', '23', '2020', '12', 'A'), ('J14', '23', '2020', '14', 'A'),
         ('G11', '23', '2020', '17', 'A'), ('G12', '23', '2020', '18', 'A'), ('Y06', '23', '2020', '23', 'A')]
OTHER = {'Y01': [('24', '2022', '1'), ('24', '2021', '1'), ('23', '2022', '23'), ('23', '2021', '25'), ('23', '2020', '22')], 'Y02': [('23', '2022', '24')], 'Y03': [('23', '2022', '25')],
         'Y04': [('24', '2021', '2'), ('23', '2022', '26'), ('23', '2021', '26'), ('23', '2020', '24')], 'Y05': [('24', '2022', '6'), ('23', '2022', '27'), ('23', '2022', '28')],
         'E01': [('24', '2023', '8')], 'E03': [('23', '2020', '3'), ('24', '2022', '13'), ('23', '2022', '1')], 'E07': [('24', '2023', '7'), ('23', '2020', '1')],
         'E08': [('24', '2023', '9'), ('24', '2021', '8'), ('23', '2021', '2')], 'E09': [('24', '2023', '10')],
         'E10': [('24', '2023', '11'), ('24', '2022', '16'), ('24', '2022', '17'), ('24', '2021', '9'), ('24', '2021', '10'), ('23', '2022', '4'), ('23', '2022', '5'), ('23', '2021', '3'), ('23', '2021', '4')],
         'E11': [('24', '2022', '14'), ('23', '2022', '2')], 'E12': [('24', '2022', '15'), ('23', '2022', '3')], 'E13': [('23', '2021', '1'), ('23', '2020', '2')],
         'K01': [('24', '2022', '18'), ('24', '2022', '19'), ('24', '2021', '11'), ('23', '2022', '21'), ('23', '2022', '22'), ('23', '2021', '24'), ('23', '2020', '21')], 'K02': [('24', '2023', '13')],
         'G01': [('24', '2023', '15'), ('24', '2022', '20'), ('24', '2021', '12'), ('24', '2021', '13'), ('23', '2022', '16'), ('23', '2021', '17'), ('23', '2021', '18'), ('23', '2020', '16')],
         'G02': [('24', '2023', '17'), ('24', '2022', '21'), ('23', '2022', '17')], 'G03': [('24', '2023', '18'), ('24', '2022', '23'), ('24', '2021', '17'), ('23', '2022', '19'), ('23', '2021', '22'), ('23', '2020', '19')],
         'G04': [('24', '2023', '19'), ('24', '2022', '24'), ('24', '2021', '18'), ('23', '2022', '20'), ('23', '2021', '23'), ('23', '2020', '15')], 'G05': [('23', '2020', '20')],
         'G07': [('24', '2023', '14')], 'G08': [('24', '2023', '16')], 'G09': [('24', '2022', '22'), ('24', '2021', '16'), ('23', '2022', '18'), ('23', '2021', '21')], 'G10': [('24', '2021', '15'), ('23', '2021', '19'), ('23', '2021', '20')],
         'J01': [('24', '2023', '20'), ('24', '2022', '27'), ('24', '2021', '20'), ('25', '2022', '3', '장지희'), ('23', '2022', '15'), ('23', '2021', '14'), ('23', '2020', '11')],
         'J04': [('24', '2021', '21'), ('23', '2021', '15')], 'J06': [('24', '2023', '21')], 'J07': [('24', '2023', '22')], 'J08': [('24', '2022', '25'), ('23', '2022', '13')],
         'J09': [('24', '2022', '26'), ('23', '2022', '14'), ('23', '2020', '13')], 'J10': [('23', '2021', '16')], 'J11': [('23', '2021', '13')],
         'B01': [('24', '2023', '25')], 'B02': [('24', '2023', '23')], 'B03': [('24', '2023', '24')], 'B04': [('24', '2022', '28'), ('23', '2022', '12')],
         'C02': [('24', '2023', '3'), ('24', '2022', '8'), ('23', '2022', '7')], 'C03': [('24', '2022', '10'), ('23', '2022', '9')], 'C04': [('24', '2023', '6'), ('24', '2021', '6')],
         'C05': [('23', '2022', '6')], 'C06': [('23', '2022', '8')], 'C07': [('23', '2022', '10')], 'C08': [('23', '2022', '11')], 'C09': [('23', '2021', '5')], 'C10': [('23', '2021', '6')], 'C11': [('23', '2021', '7'), ('23', '2020', '5')],
         'P01': [('23', '2021', '9'), ('23', '2020', '9')], 'P02': [('23', '2021', '10'), ('23', '2020', '8')], 'P03': [('23', '2021', '11')], 'P04': [('23', '2021', '12')]}
CROPS = {}
Q = []
def secyear(sec): return int(sec) % 100
CANON = [c if len(c) == 6 else c + (None,) for c in CANON]
for cid, ed, sec, num, tier, pf in CANON:
    x = find(ed, sec, num, pf); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t, ed, sec)
    short = re.sub(r'^\s*(\d{1,2}(-\d)?)\s*[.．)]\s*', '', t.split('\n')[0]).strip()
    yrs = set(ty) | {secyear(sec)}
    for o_ in OTHER.get(cid, []):
        e2, s2, n2 = o_[:3]; yrs.add(secyear(s2)); x2 = find(e2, s2, n2, o_[3] if len(o_) > 3 else None)
        if x2: yrs |= tag_years(x2['text'], e2, s2)[0]
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': tier, 'prof': x['prof'],
              'src': f'JB {ed}판 · {sec}년 칸 · {x["prof"]} {num}번', 'prof0': x['prof'], 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)) + (' (학습부 예상 — 선지 미복원)' if '(예상)' in short else ''), 'base': sorted(yrs, reverse=True),
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
        cur = {'v': '', 'yrs': [], 'yrsnote': '', 'lec': [], 'rel': '', 'pair': '', 'prof': '', 'A': [], 'M': [], 'N': []}; ANN[parts[0]] = cur
        for p in parts[1:]:
            k, _, v = p.partition('=')
            if k == 'yrs': cur['yrs'] = [int(y) for y in v.split(',') if y.strip()]
            elif k == 'lec': cur['lec'] = [v] if v else []
            else: cur[k] = v
    elif cur is not None and len(line) > 2 and line[1] == ':' and line[0] in 'AMN':
        collect(line); cur[line[0]].append(cite_html(line[2:].strip()))
for q in Q:
    a = ANN.get(q['id'])
    if a:
        lk_ = a['lec'][0].split(':')[0] if a['lec'] else ''; lk_ = getattr(S, 'IMG_ALIAS', {}).get(lk_, lk_)
        q.update({'v': a['v'], 'yrsnote': a['yrsnote'], 'rel': a['rel'], 'pair': a['pair'], 'A': a['A'], 'M': a['M'], 'N': a['N'], 'lk': lk_})
        q['yrs'] = sorted(set(q['base']) | set(a['yrs']), reverse=True); q['xtra'] = sorted(set(a['yrs']) - set(q['base']), reverse=True)
        if a['prof']: q['prof'] = a['prof']
    else:
        q.update({'v': 'na', 'yrsnote': '', 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': [], 'lk': '', 'xtra': []}); q['yrs'] = sorted(q['base'], reverse=True)
    pass  # GERI: JB에 교수 소제목이 명확하므로 원 교수 유지(전임 교수도 별도 행)
    o = []
    for o_ in OTHER.get(q['id'], []):
        e2, s2, n2 = o_[:3]; x2 = find(e2, s2, n2, o_[3] if len(o_) > 3 else None)
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
idmap = {(q['ed'], q['sec'], str(q['num']), q['prof0']): q['id'] for q in Q}
rev = {}
for cid, lst in OTHER.items():
    for o_ in lst:
        e2, s2, n2 = o_[:3]; x2 = find(e2, s2, n2, o_[3] if len(o_) > 3 else None)
        if x2: rev.setdefault((e2, s2, str(n2), x2['prof']), []).append(cid)
for ed in NPAGES:
    for x in blocks[ed]:
        key = (ed, x['sec'], str(x['num']), x['prof']); first = x['text'].split('\n')[0][:70]
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
