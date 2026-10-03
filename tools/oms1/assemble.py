import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json, io, base64, os, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import parse_jb

BASE = J.JBX
NPAGES = {'25': 16, '24': 20, '23': 28}
LEC = J.work('OMS1', 'lec') + '/'
import subject as _S
LECMAP = _S.LECMAP

# ---------- 1. JB blocks ----------
blocks = {}
for ed, n in NPAGES.items():
    b = parse_jb.parse(ed, n)
    out = []
    for x in b:
        x['text'] = '\n'.join(x['lines']).strip()
        x['pg2'] = x.get('pg2', x['pg'])
        # 24판 2020: 답 목록 일부가 문항으로 잘못 분리된 것 병합
        if out and x['sec'] == '서병무 DD 2020' and re.match(r'^\s*\d\.\s*(Developmental origin|Trauma|Tumors)', x['text']):
            out[-1]['text'] += '\n' + x['text']; out[-1]['pg2'] = x['pg2']; out[-1]['merged'] = True; continue
        out.append(x)
    blocks[ed] = out
# 23판 2020 섹션: 1번 뒤에 2~4번이 묶여 분리되지 않음 → 표시용 라벨
for x in blocks['23']:
    if x['sec'] == '서병무 DD 2020' and x.get('merged'):
        x['num'] = '1~4'

ANSRE = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$')
def stem_of(t):
    out = []
    for l in t.split('\n'):
        if ANSRE.match(l): break
        out.append(l)
    return ' '.join(out)
def sec_year(sec):
    m = re.match(r'(20\d\d)-3Q', sec) or re.search(r'(20\d\d)$', sec)
    return int(m.group(1)) % 100 if m else None
def tag_years(text):
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = re.sub(r'(반짤반탈|짤 변형|짤|탈|년|NEW|’|\'|~|\.)', ' ', g).replace('，', ',')   # (2019, 탈)·(24. 23) 같은 변형도 읽음
        if not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*[,、\s]\s*(20\d\d|\d\d)?)*\s*', g2): continue
        vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
        if not vs or not all(8 <= v <= 26 for v in vs): continue
        ys |= set(vs); raw.append('(' + g.strip() + ')')
    return ys, raw

def find(ed, sec, num):
    for x in blocks[ed]:
        if x['sec'] == sec and str(x['num']) == str(num):
            return x
    return None

# ---------- 2. canonical questions ----------
OTHER = {  # canonical -> [(ed, sec, num)]
 'Q01': [('24','2023-3Q',2)], 'Q03': [('24','서병무 DD 2021',7),('23','서병무 DD 2021',7)],
 'Q04': [('24','2022-3Q',1),('23','2022-3Q',1)], 'Q06': [('24','2023-3Q',3),('24','서병무 DD 2021',6),('23','서병무 DD 2021',6)],
 'Q07': [('24','2023-3Q',4)], 'Q08': [('24','2023-3Q',6)], 'Q12': [('24','2022-3Q','추가'),('23','2022-3Q','추가')],
 'Q13': [('24','서병무 DD 2020',6),('23','서병무 DD 2020',6)], 'Q14': [('24','2023-3Q',7),('24','서병무 DD 2021',1),('23','서병무 DD 2021',1)],
 'Q15': [('24','서병무 DD 2021',8),('23','서병무 DD 2021',8)], 'Q16': [('24','2022-3Q',9),('23','2022-3Q',9)],
 'Q17': [('24','2023-3Q',19)], 'Q22': [('24','2022-3Q',19),('23','2022-3Q',19)],
 'Q24': [('24','2023-3Q',10),('24','2022-3Q',13),('23','2022-3Q',13)], 'Q25': [('24','2023-3Q',1)], 'Q26': [('24','2023-3Q',4)],
 'Q27': [('24','2023-3Q',5)], 'Q28': [('24','2023-3Q',8)], 'Q29': [('24','2023-3Q',9),('24','2022-3Q',10),('23','2022-3Q',10)],
 'Q30': [('24','2023-3Q',14)], 'Q31': [('24','2023-3Q',18)], 'Q32': [('24','2023-3Q',17)], 'Q33': [('24','2023-3Q',12)],
 'Q34': [('24','2023-3Q',13)], 'Q35': [('24','2023-3Q',15)], 'Q36': [('24','2023-3Q',16)], 'Q37': [('24','2023-3Q',11)],
 'Q38': [('24','2022-3Q',3),('23','2022-3Q',3)], 'Q39': [('24','2022-3Q',2),('23','2022-3Q',2),('24','서병무 DD 2020',2)],
 'Q40': [('24','2022-3Q',4),('23','2022-3Q',4)], 'Q41': [('24','2022-3Q',5),('23','2022-3Q',5)],
 'Q42': [('24','2022-3Q',7),('23','2022-3Q',7)], 'Q43': [('24','2022-3Q',8),('23','2022-3Q',8)],
 'Q44': [('24','2022-3Q',6),('23','2022-3Q',6)], 'Q45': [('24','2022-3Q',12),('23','2022-3Q',12)],
 'Q46': [('24','2022-3Q',15),('23','2022-3Q',15)], 'Q47': [('24','2022-3Q',16),('23','2022-3Q',16)],
 'Q48': [('24','2022-3Q',18),('23','2022-3Q',18)], 'Q49': [('24','2022-3Q',14),('23','2022-3Q',14)],
 'S21-2': [('23','서병무 DD 2021',2)], 'S21-3': [('23','서병무 DD 2021',3)], 'S21-4': [('23','서병무 DD 2021',4)],
 'S21-5': [('23','서병무 DD 2021',5)], 'S21-9': [('23','서병무 DD 2021',9)], 'S20-1': [('23','서병무 DD 2020','1~4')],
 'S20-3': [('23','서병무 DD 2020','1~4')], 'S20-4': [('23','서병무 DD 2020','1~4')], 'S20-5': [('23','서병무 DD 2020',5)],
 'S20-7': [('23','서병무 DD 2020',7)], 'S20-8': [('23','서병무 DD 2020',8)],
 'J1': [('23','정필훈 기출',1)], 'J2': [('23','정필훈 기출',3)], 'J3': [('23','정필훈 기출',8)], 'J4': [('23','정필훈 기출',10),('23','정필훈 기출',2)],
 'J5': [('23','정필훈 기출',18)], 'J6': [('23','정필훈 기출',20)], 'J7': [('23','정필훈 기출',21)], 'J8': [('23','정필훈 기출',23)],
}
CROPS = {'Q35': {'q': ['Q35_q']}, 'J3': {'q': ['J3_q']}, 'J4': {'a': ['J4_a1', 'J4_a2']}, 'J6': {'q': ['J6_q']}, 'J7': {'q': ['J7_q']}}

used = set()
Q = []
def add(cid, ed, x, tier, prof, label):
    used.add((ed, x['sec'], str(x['num'])))
    t = x['text']
    head = ' '.join(t.split('\n')[:3])
    ty, raw = tag_years(t)
    sy = sec_year(x['sec'])
    base = set(ty) | ({sy} if sy else set())
    short = re.sub(r'^\s*\d{1,3}(-\d)?\.?\s*', '', t.split('\n')[0]).strip()
    Q.append({'id': cid, 'ed': ed, 'sec': x['sec'], 'num': x['num'], 'pg': x['pg'], 'pg2': x['pg2'], 'text': t,
              'tier': tier, 'prof': prof, 'src': label, 'short': short[:52], 'jbtag': ' '.join(raw),
              'base': sorted(base, reverse=True), 'secy': sy, 'tal': bool(re.search(r'\(탈\)', head))})

for x in blocks['25']:
    add('Q%02d' % x['num'], '25', x, 'A', x['prof'], f"JB 25판 · {x['sec']} {x['num']}번")
for num in (2, 3, 4, 5, 9):
    add(f'S21-{num}', '24', find('24', '서병무 DD 2021', num), 'A', '서병무', f'JB 24판 · 서병무 DD 2021 {num}번')
for num in (1, 3, 4, 5, 7, 8):
    add(f'S20-{num}', '24', find('24', '서병무 DD 2020', num), 'A', '서병무', f'JB 24판 · 서병무 DD 2020 {num}번')
for num in range(1, 9):
    add(f'J{num}', '24', find('24', '정필훈 기출', num), 'B', '정필훈', f'JB 24판 · 정필훈 기출 {num}번')
ci = 0
for x in blocks['23']:
    if x['sec'].startswith('서병무 임플란트') or x['sec'] == '정필훈 기출':
        ci += 1
        prof = '정필훈' if x['sec'] == '정필훈 기출' else '서병무(임플란트·13~21)'
        add(f'C{ci:02d}', '23', x, 'C', prof, f"JB 23판 · {x['sec']} {x['num']}번")
# J ↔ C 연결
JC = {'J1': 1, 'J2': 3, 'J3': 8, 'J4': 10, 'J5': 18, 'J6': 20, 'J7': 21, 'J8': 23}
for q in Q:
    if q['tier'] == 'C' and q['sec'] == '정필훈 기출':
        for j, n in JC.items():
            if str(q['num']) == str(n): q['same'] = j
for cid, lst in OTHER.items():
    for (ed, sec, num) in lst: used.add((ed, sec, str(num)))

# ---------- 3. annotations ----------
import emph
EMPH = emph.apply
def cite_html(s, em=False):
    toks = re.split(r'(\[\[[A-Z0-9]+:[^\]]+\]\])', s)
    s = ''.join(t if t.startswith('[[') else (EMPH(html.escape(t, quote=False)) if (em and EMPH) else html.escape(t, quote=False)) for t in toks)
    def rep(m):
        k, p = m.group(1), m.group(2)
        name = LECMAP[k][1]
        if k == 'DD3':
            return f'<button class="cite t" data-k="DD3" data-p="">{name} ‘{p}’</button>'
        return f'<button class="cite" data-k="{k}" data-p="{p}">{name} p.{p}</button>'
    s = re.sub(r'\[\[([A-Z0-9]+):([^\]]+)\]\]', rep, s)
    s = s.replace('⚠', '<b class="warn">⚠</b>').replace('💡', '<b class="bulb">💡</b>')
    return s

cited = set()
def collect(s):
    for m in re.finditer(r'\[\[([A-Z0-9]+):([^\]]+)\]\]', s):
        k, p = m.group(1), m.group(2)
        if k != 'DD3' and p.isdigit(): cited.add((k, int(p)))

ANN = {}
cur = None
for line in open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'annot.txt'), encoding='utf-8'):
    line = line.rstrip('\n')
    if line.startswith('@'):
        parts = [p.strip() for p in line[1:].split('|')]
        cur = {'v': '', 'yrs': [], 'yrsnote': '', 'lec': [], 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': []}
        ANN[parts[0]] = cur
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
        q.update({'v': a['v'], 'yrsnote': a['yrsnote'], 'rel': a['rel'], 'pair': a['pair'],
                  'A': a['A'], 'M': a['M'], 'N': a['N'], 'lk': a['lec'][0].split(':')[0] if a['lec'] else ''})
        q['yrs'] = sorted(set(q['base']) | set(a['yrs']), reverse=True)
        q['xtra'] = sorted(set(a['yrs']) - set(q['base']), reverse=True)
    else:
        q.update({'v': 'na', 'yrsnote': '', 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': [], 'lk': '', 'xtra': []})
        q['yrs'] = sorted(q['base'], reverse=True)
    o = []
    for (ed, sec, num) in OTHER.get(q['id'], []):
        x = find(ed, sec, num)
        if x: o.append({'ed': ed, 'sec': sec, 'num': x['num'], 'pg': x['pg'], 'pg2': x['pg2'], 'text': x['text']})
    q['other'] = o
    lab = ''
    for v in o:
        if v['ed'] == '24' and v['sec'] == '2023-3Q':
            m = re.search(r'\(((?:서술형|객관식|단답형)[^)]*|모두 고르시오[^)]*)\)', ' '.join(v['text'].split('\n')[:3]))
            if m: lab = m.group(1)
    q['lab24'] = lab
    q['crops'] = CROPS.get(q['id'], {})
    q['fig'] = bool(re.search(r'그림|(?<!경)사진|도해', ' '.join(q['text'].split('\n')[:4]))) and q['id'] not in ('S20-4',)   # S20-4 = '방사선 사진 종류'를 묻는 글 문항(그림 없음 — 10-03 맥 확인)

# ---------- 4. lectures ----------
LECT = []
for fn in ('lectures1.txt', 'lectures2.txt'):
    lec = None; sec = None
    if not _os.path.exists(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), fn)): continue
    for line in open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), fn), encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('#LEC'):
            p = [x.strip() for x in line[4:].split('|')]
            lec = {'k': p[0], 'title': p[1], 'prof': p[2], 'yr': p[3], 'file': p[4], 'pages': int(p[5]), 'notes': [], 'secs': []}
            LECT.append(lec)
        elif line.startswith('!') and lec:
            lec['notes'].append(cite_html(line[1:].strip()))
        elif line.startswith('§') and lec:
            p = [x.strip() for x in line[1:].split('|')]
            jb = []
            for x in p[2:]:
                if x.startswith('jb='): jb = [j.strip() for j in x[3:].split(',') if j.strip()]
            sec = {'rng': p[0], 'title': p[1], 'jb': jb, 'items': []}
            lec['secs'].append(sec)
        elif line.startswith('- ') and sec is not None:
            t = line[2:].strip(); em = t.startswith('* ')
            if em: t = t[2:]
            sec['items'].append({'em': em, 'h': cite_html(t, True)})
# 쪽 범위 누락 검사
cov_report = []
for lec in LECT:
    if not lec['pages']: continue
    have = set()
    for s in lec['secs']:
        m = re.fullmatch(r'(\d+)(?:-(\d+))?', s['rng'])
        if m:
            a = int(m.group(1)); b = int(m.group(2) or a)
            if b <= lec['pages']: have |= set(range(a, b + 1))
    miss = [p for p in range(1, lec['pages'] + 1) if p not in have]
    cov_report.append((lec['k'], lec['pages'], miss))

# ---------- 4b. tables ----------
TABLES = []
curt = None
for line in open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'tables.txt'), encoding='utf-8'):
    line = line.rstrip('\n')
    if line.startswith('#TBL'):
        p = [x.strip() for x in line[4:].split('|')]
        curt = {'title': p[0], 'k': '', 'src': '', 'head': [], 'rows': [], 'notes': []}
        for x in p[1:]:
            if x.startswith('k='): curt['k'] = x[2:]
            elif x.startswith('src='): collect(x); curt['src'] = cite_html(x[4:])
        TABLES.append(curt)
    elif line.startswith('H:') and curt: curt['head'] = [html.escape(c.strip()) for c in line[2:].split('|')]
    elif line.startswith('R:') and curt: curt['rows'].append([cite_html(c.strip(), True) for c in line[2:].split('|')])
    elif line.startswith('N:') and curt: collect(line); curt['notes'].append(cite_html(line[2:].strip(), True))

# ---------- 5. predicted ----------
PRED = []
cur = None
for line in open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'pred.txt'), encoding='utf-8'):
    line = line.rstrip('\n')
    if line.startswith('@P'):
        p = [x.strip() for x in line[2:].split('|')]
        cur = {'k': p[0], 't': '', 'b': '', 'q': '', 'a': ''}
        for x in p[1:]:
            k, _, v = x.partition('='); cur[k] = v
        PRED.append(cur)
    elif line.startswith('Q:') and cur: cur['q'] = cite_html(line[2:].strip()); cur['q_raw'] = line[2:].strip()
    elif line.startswith('A:') and cur: collect(line); cur['a'] = cite_html(line[2:].strip()); cur['a_raw'] = line[2:].strip()

# ---------- 6. images ----------
def b64(im, q):
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
IMG = {'jb': {}, 'lec': {}, 'crop': {}}
for ed, n in NPAGES.items():
    man = json.load(open(f'{BASE}OMS1_20{ed}/manifest.json'))
    vis = {p['page_number'] for p in man['pages'] if p.get('has_visual_content')}
    for i in range(1, n + 1):
        if not os.path.exists(f'{BASE}OMS1_20{ed}/{i}.jpeg'):   # JB 쪽 이미지가 없는 환경(클라우드 세션) — 지금 docs/packs의 쪽 이미지를 그대로(tools/jblpaths.prev_jb_pages)
            IMG['jb'][f'{ed}-{i}'] = J.prev_jb_pages('OMS1')[f'{ed}-{i}']; continue
        im = Image.open(f'{BASE}OMS1_20{ed}/{i}.jpeg').convert('RGB')
        if i in vis: IMG['jb'][f'{ed}-{i}'] = b64(im, 50)
        else: IMG['jb'][f'{ed}-{i}'] = b64(im.convert('L').resize((860, int(im.size[1]*860/im.size[0]))), 32)
emph = {'DX': [17, 23, 27, 32, 41, 42], 'LOAD': [7, 9, 16, 18], 'REP': [2, 5, 6]}
for k, ps in emph.items():
    for p in ps: cited.add((k, p))
for p in range(1, 46): cited.add(('DX', p))
for (k, p) in sorted(cited):
    d = LECMAP[k][0]
    f = f'{LEC}{d}i/{p}.jpg'
    if not os.path.exists(f): continue
    im = Image.open(f).convert('RGB'); w, h = im.size
    im = im.resize((780, int(h * 780 / w)))
    IMG['lec'][f'{k}-{p}'] = b64(im, 40)
CROP_DIR = J.work('OMS1', 'crops')
for f in (sorted(_os.listdir(CROP_DIR)) if _os.path.isdir(CROP_DIR) else []):
    im = Image.open(_os.path.join(CROP_DIR, f)).convert('RGB')
    if f.startswith('Q35'): im = im.crop((0, 0, im.size[0], im.size[1] - 8))
    IMG['crop'][f[:-4]] = b64(im, 85)
for k, v in J.prev_crops('OMS1', CROPS).items(): IMG['crop'].setdefault(k, v)

# ---------- 7. ledger ----------
LEDGER = []
idmap = {(q['ed'], q['sec'], str(q['num'])): q['id'] for q in Q}
rev = {}
for cid, lst in OTHER.items():
    for (ed, sec, num) in lst: rev.setdefault((ed, sec, str(num)), []).append(cid)
for ed in ('25', '24', '23'):
    for x in blocks[ed]:
        key = (ed, x['sec'], str(x['num']))
        first = x['text'].split('\n')[0][:70]
        if '미복원' in first and len(x['text']) < 20: st, to = 'lost', []
        elif key in idmap: st, to = 'card', [idmap[key]]
        elif key in rev: st, to = 'dup', rev[key]
        else: st, to = 'ref', []
        LEDGER.append({'ed': ed, 'sec': x['sec'], 'num': x['num'], 'pg': x['pg'], 'first': first, 'st': st, 'to': to})
# 교차참조 전용 블록(본문 없이 "(2024. 7번)" 식) 연결
XREF = {('24', '서병무 DD 2021', '1'): ['Q14'], ('24', '서병무 DD 2021', '6'): ['Q06'], ('24', '서병무 DD 2021', '8'): ['Q15'],
        ('24', '서병무 DD 2020', '2'): ['Q39'], ('24', '서병무 DD 2021', '7'): ['Q03'], ('24', '서병무 DD 2020', '6'): ['Q13']}
for r in LEDGER:
    k = (r['ed'], r['sec'], str(r['num']))
    if k in XREF: r['st'] = 'dup'; r['to'] = XREF[k]
def ment(ed, pages):
    t = ''
    for p in pages:
        s = parse_jb.rd(f'{BASE}OMS1_20{ed}/{p}.txt')
        s = '\n'.join(l for l in s.split('\n') if '무단인쇄' not in l and l.strip())
        t += s + '\n'
    return t.strip()
MENT = {'25': ment('25', [1, 2]), '24': ment('24', [1, 2]), '23': ment('23', [1, 2])}

