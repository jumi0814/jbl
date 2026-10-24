import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_cons as P, subject as S
BASE = J.JBX; SUB = 'CONS'
NPAGES = {'26': 33, '25': 14, '24': 16, '23': 12}
LECMAP = S.LECMAP

# ---------- 1. JB blocks ----------
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
    """문항 첫머리(답 이전)의 연도 괄호 전부. (24, 탈) / (14~) / (21,20,19,18,17,15,14,13,) 도 처리"""
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = re.sub(r'(반짤반탈|짤|탈|년|~)', ' ', g).replace('，', ',')
        if not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*[,、]\s*(20\d\d|\d\d)?)*\s*', g2): continue
        vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
        if not vs or not all(8 <= v <= 26 for v in vs): continue
        ys |= set(vs); raw.append('(' + g.strip() + ')')
    return ys, raw
def find(ed, num):
    for x in blocks[ed]:
        if str(x.get('key', x['num'])) == str(num): return x   # 26판 뒷부분(과거 기출)은 key 'P<번호>' — 앞쪽 번호와 겹쳐서
    return None

# ---------- 2. canonical questions ----------
# 25판 문항 ↔ 24판 ↔ 23판 (같은 문제의 다른 수록본)
OTHER = {'Q01': [('24', 1), ('23', 1)], 'Q02': [('24', 2), ('23', 2)], 'Q04': [('24', 3), ('23', 3)], 'Q05': [('24', 4), ('23', 4)],
         'Q06': [('24', 5)], 'Q07': [('24', 6), ('23', 14)], 'Q08': [('24', 7), ('23', 15)], 'Q09': [('24', 8), ('23', 16)],
         'Q10': [('24', 10), ('23', 18)], 'Q11': [('24', 11), ('23', 19)], 'Q12': [('24', 9), ('23', 17)], 'Q13': [('24', 12), ('23', 20)],
         'Q14': [('24', 13)], 'Q16': [('24', 15)], 'Q17': [('24', 14)], 'Q19': [('24', 16)], 'Q20': [('24', 20), ('23', 8)],
         'Q22': [('24', 18), ('23', 6)], 'Q23': [('24', 17), ('23', 5)], 'Q24': [('24', 19), ('23', 7)], 'Q25': [('24', 21), ('23', 9)],
         'Q26': [('24', 22), ('23', 10)], 'Q27': [('24', 23), ('23', 11)], 'Q28': [('24', 24), ('23', 12)], 'Q29': [('24', 25), ('23', 13)],
         'C01': [('23', 21)], 'C02': [('23', 22)]}
# 26판(2026 3Q JB) — 앞쪽 '2025-3Q'에서 연도가 병합된 기존 문항 + 뒷부분 '과거 기출'(key P<번호>) → 기존 id의 다른 판본(맨 앞에)
OTHER26 = {'Q01': ['1'], 'Q03': ['2'], 'Q04': ['3'], 'Q06': ['4-1'], 'Q07': ['7'], 'Q08': ['40', '41'], 'Q10': ['42'], 'Q14': ['45', '45-2'],
           'Q22': ['47'], 'Q20': ['48'],
           'Q39': ['14-1'], 'Q43': ['20'],   # 10-25 결정 B2-2·B2-1: 같은 25년 문항의 다른 복원 → 합침(옛 Q40 14-1번 → Q39 · 옛 Q44 20번 → Q43 — JB 20번 해설 '19 번 복원이 더 정확') · jb_move.json
           'Q02': ['P2'], 'Q05': ['P5'], 'Q09': ['P9'], 'Q11': ['P11'], 'Q12': ['P12'], 'Q13': ['P13'], 'Q15': ['P15'], 'Q16': ['P16'],
           'Q17': ['P17'], 'Q17_1': ['P17-1'], 'Q18': ['P18'], 'Q19': ['P19'], 'Q21': ['P21'], 'Q23': ['P23'], 'Q24': ['P24'],
           'Q25': ['P25'], 'Q26': ['P26'], 'Q27': ['P27'], 'Q28': ['P28'], 'Q29': ['P29']}
for _c, _l in OTHER26.items(): OTHER[_c] = [('26', n_) for n_ in _l] + OTHER.get(_c, [])
# 26판 새 문항(25년 시험 — 이전 판에 없던 복원) → 새 id Q30~(jb_lock에 없는 번호, 26판 번호 순) · 놓을 자리 = 같은 강의 묶음의 기존 마지막 문항 뒤
NEW26 = [('Q30', '4'), ('Q31', '5'),
         ('Q32', '6'), ('Q33', '8'), ('Q34', '9'), ('Q35', '10'), ('Q36', '11'), ('Q37', '12'), ('Q38', '13'), ('Q39', '14'),
         ('Q41', '15'), ('Q42', '18'), ('Q43', '19'), ('Q45', '21'), ('Q46', '21+'), ('Q47', '22'), ('Q48', '23'), ('Q49', '24'),
         ('Q50', '25'), ('Q51', '26'), ('Q52', '27'), ('Q53', '28'), ('Q54', '29'), ('Q55', '30'), ('Q56', '31'), ('Q57', '32'), ('Q58', '33'),
         ('Q59', '34'), ('Q60', '34+'), ('Q61', '35'), ('Q62', '36'), ('Q63', '37'), ('Q64', '38'), ('Q65', '39'),
         ('Q66', '43'),
         ('Q67', '44'), ('Q68', '46')]
NEW26_AFTER = {'이인복': 'Q06', '서덕규': 'Q08', '김선영': 'Q13', '이창하': 'Q19'}
CROPS = {}
Q = []
def add(cid, ed, x, tier, prof, label, secy=None):
    t = x['text']; head = ' '.join(t.split('\n')[:3])
    ty, raw = tag_years(t)
    short = re.sub(r'^\s*(20\d\d\s*년\s*교수님\s*(강조|pick)[^\n]*\n)?', '', t).split('\n')[0]
    short = re.sub(r'^\s*\d{1,2}(-\d)?(\([^)]*\))?\s*[.．]?\s*', '', short).strip()
    Q.append({'id': cid, 'ed': ed, 'sec': x['sec'], 'num': x['num'], 'pg': x['pg'], 'pg2': x['pg2'], 'text': t,
              'tier': tier, 'prof': prof, 'src': label, 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)),
              'base': sorted(ty | ({secy} if secy else set()), reverse=True), 'secy': secy, 'tal': bool(re.search(r'\(\s*\d\d\s*,\s*탈\s*\)|\(탈\)', head)) or (ed == '26' and '[탈]' in stem_of(t)),
              'pick': '\n'.join(l for l in t.split('\n')[:2] if re.match(r'^\s*20\d\d\s*년\s*교수님', l)).strip()})
for x in blocks['25']:
    cid = 'Q%02d' % int(x['num']) if '-' not in str(x['num']) else 'Q' + str(x['num']).replace('-', '_').zfill(4)
    add(cid, '25', x, 'A', x['prof'], f"JB 25판 · {x['prof']} {x['num']}번")
for cid, num in NEW26:   # 26판 앞쪽 = '2025-3Q' 칸(25년 출제 문항만 — 26판 머리 멘트) → 칸 연도 25(괄호가 없는 11·26·30·38·추가 복원도)
    x = find('26', num); lab = f"{num[:-1]}번 뒤 추가 복원" if num.endswith('+') else f"{num}번"
    add(cid, '26', x, 'A', x['prof'], f"JB 26판 · 2025년 칸 · {x['prof']} {lab}", secy=25)
    _new = Q.pop(); _at = max(i for i, q_ in enumerate(Q) if q_['id'] == NEW26_AFTER[x['prof']] or (q_['ed'] == '26' and q_['prof'] == x['prof']))
    Q.insert(_at + 1, _new)
for i, num in enumerate((26, 27), 1):
    x = find('24', num); add(f'C{i:02d}', '24', x, 'C', '손호현', f'JB 24판 · 손호현 기출 {num}번')

# ---------- 3. annotations ----------
import emph
EMPH = emph.apply
def cite_html(s, em=False):
    toks = re.split(r'(\[\[[A-Z0-9]+:[^\]]+\]\])', s)
    s = ''.join(t if t.startswith('[[') else (EMPH(html.escape(t, quote=False)) if (em and EMPH) else html.escape(t, quote=False)) for t in toks)
    def rep(m):
        k, p = m.group(1), m.group(2); name = LECMAP[k][1]
        if not LECMAP[k][0]: return f'<button class="cite t" data-k="{k}" data-p="">{name} ‘{p}’</button>'
        return f'<button class="cite" data-k="{k}" data-p="{p}">{name} {"슬라이드" if k == "WHT" else "p."}{p}</button>'
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
    oy = set()   # 출제연도 ∪ 다른 판본 같은 문제의 괄호(26판에서 25년 시험에 '명확히 같은' 문항으로 연도 병합 → 25)
    for (ed, num) in OTHER.get(q['id'], []):
        x = find(ed, num)
        if x:
            oy |= tag_years(x['text'])[0]
            if ed == '26' and not q['pick']: q['pick'] = '\n'.join(l for l in x['text'].split('\n')[:2] if re.match(r'^\s*20\d\d\s*년\s*교수님', l)).strip()   # 26판 뒷부분 '2025 년 교수님 강조'(11번에 새로)
    q['base'] = sorted(set(q['base']) | oy, reverse=True)
    a = ANN.get(q['id'])
    if a:
        q.update({'v': a['v'], 'yrsnote': a['yrsnote'], 'rel': a['rel'], 'pair': a['pair'], 'A': a['A'], 'M': a['M'], 'N': a['N'], 'K': a.get('K', []), 'lk': a['lec'][0].split(':')[0] if a['lec'] else ''})
        q['yrs'] = sorted(set(q['base']) | set(a['yrs']), reverse=True); q['xtra'] = sorted(set(a['yrs']) - set(q['base']), reverse=True)
    else:
        q.update({'v': 'na', 'yrsnote': '', 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': [], 'K': [], 'lk': '', 'xtra': []}); q['yrs'] = sorted(q['base'], reverse=True)
    o = []
    for (ed, num) in OTHER.get(q['id'], []):
        x = find(ed, num)
        if x: o.append({'ed': ed, 'sec': x['sec'], 'num': x['num'], 'pg': x['pg'], 'pg2': x['pg2'], 'text': x['text']})
    q['other'] = o; q['lab24'] = ''; q['crops'] = CROPS.get(q['id'], {})
    q['fig'] = bool(re.search(r'사진|도해', ' '.join(q['text'].split('\n')[:4])))

LECT = []; TABLES = []
# ---------- 5. predicted ----------
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
# ---------- 6. images ----------
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
# ---------- 7. ledger ----------
LEDGER = []
idmap = {(q['ed'], str(q['num'])): q['id'] for q in Q}   # 정식 문항은 26판 앞쪽 블록뿐(뒷부분 key P…는 모두 다른 판본)
rev = {}
for cid, lst in OTHER.items():
    for (ed, num) in lst: rev.setdefault((ed, str(num)), []).append(cid)
for ed in NPAGES:
    for x in blocks[ed]:
        key = (ed, str(x.get('key', x['num']))); first = re.sub(r'^\s*20\d\d\s*년\s*교수님[^\n]*\n', '', x['text']).split('\n')[0][:70]
        if key in idmap: st, to = 'card', [idmap[key]]
        elif key in rev: st, to = 'dup', rev[key]
        else: st, to = 'ref', []
        LEDGER.append({'ed': ed, 'sec': x['sec'], 'num': x['num'], 'pg': x['pg'], 'first': first, 'st': st, 'to': to})
def ment(ed, pages):
    t = ''
    for p in pages:
        s = P.rd(f'{BASE}{SUB}_20{ed}/{p}.txt'); t += '\n'.join(l for l in s.split('\n') if '무단인쇄' not in l and l.strip()) + '\n'
    return t.strip()
MENT = {'26': ment('26', [1, 2]), '25': ment('25', [1, 2]), '24': ment('24', [1, 2, 3]), '23': ment('23', [1, 2])}
if __name__ == '__main__':
    print('Q', len(Q), [(q['id'], q['prof'], q['yrs'], q['jbtag'], q['tal']) for q in Q])
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [ (r['ed'], r['num'], r['first'][:20]) for r in LEDGER if r['st'] == 'ref'])
