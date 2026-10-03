import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_esth as P, subject as S
BASE = J.JBX; SUB = 'ESTH'
NPAGES = P.NPAGES
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
    """문항 첫머리(답 이전)의 연도 괄호 전부 — (24,23,22) · (21,20,18) · 줄이 끊긴 '(24,23,22,\\n21)'도(stem_of가 이어 붙임)"""
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = re.sub(r'(반짤반탈|짤 변형|짤|탈|년|’|\'|~)', ' ', g).replace('，', ',')
        if not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*[,、]\s*(20\d\d|\d\d)?)*\s*', g2): continue
        vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
        if not vs or not all(8 <= v <= 26 for v in vs): continue
        ys |= set(vs); raw.append('(' + re.sub(r'\s+', '', g) + ')')
    return ys, raw
def find(ed, sec, num):
    for x in blocks[ed]:
        if x['sec'] == sec and str(x['num']) == str(num): return x
    return None
# 강의별 교수 (annot lec= 의 강의키로 정함)
LK_PROF = {'INT': '이창하', 'FUN': '이창하', 'PLAN': '이창하', 'SPE': '이창하', 'MAT': '이창하', 'VEN': '이창하', 'COL': '안진수'}
# 정본 문항: (id, 판, 칸, 번호) — 25판이 기준, 25판에 없는 2021 칸은 24판, 2020 칸은 23판
C24 = ['1', '2', '3-5', '6', '7', '8', '9'] + [str(i) for i in range(10, 29)]
CANON = [('Q%02d' % int(n.split('-')[0]), '25', '2024-3Q', n) for n in C24] + \
        [('R%02d' % int(n.split('-')[0]), '25', '2023-3Q', n) for n in ['3', '4', '5', '6', '7', '8', '9', '10-11', '14-15', '18', '19', '20', '22']] + \
        [('S%02d' % int(n), '25', '2022-3Q', n) for n in ['4', '12', '14']] + \
        [('T%02d' % int(n), '24', '2021-3Q', n) for n in ['3', '8', '9', '10', '11', '12', '14', '15', '16', '17', '20', '21', '22', '23']] + \
        [('U%02d' % i, '23', '2020-3Q', str(i)) for i in range(1, 6)]
# 같은 문제의 다른 수록(판, 칸, 번호) — 연도 합산과 '다른 판본' 표시에 사용 (25판 칸 안의 '2024 1번' 같은 가리킴 줄 포함)
OTHER = {
    'Q01': [('25', '2023-3Q', '1'), ('25', '2022-3Q', '1'), ('24', '2023-3Q', '1'), ('24', '2022-3Q', '1'), ('23', '2022-3Q', '1')],
    'Q02': [('25', '2023-3Q', '2'), ('25', '2022-3Q', '2'), ('24', '2023-3Q', '2'), ('24', '2022-3Q', '2'), ('24', '2021-3Q', '1'), ('23', '2022-3Q', '2'), ('23', '2021-3Q', '1')],
    'Q06': [('25', '2022-3Q', '5'), ('24', '2022-3Q', '6'), ('24', '2021-3Q', '5'), ('23', '2021-3Q', '5')],
    'Q08': [('25', '2022-3Q', '6'), ('24', '2022-3Q', '5'), ('23', '2022-3Q', '5')],
    'Q10': [('25', '2022-3Q', '9'), ('24', '2022-3Q', '8'), ('24', '2021-3Q', '7'), ('23', '2022-3Q', '8'), ('23', '2021-3Q', '7')],
    'Q12': [('25', '2023-3Q', '12'), ('24', '2023-3Q', '12')],
    'Q15': [('25', '2023-3Q', '13'), ('25', '2022-3Q', '10'), ('24', '2023-3Q', '13'), ('24', '2022-3Q', '9'), ('23', '2022-3Q', '9')],
    'Q16': [('25', '2022-3Q', '11'), ('24', '2022-3Q', '10'), ('23', '2022-3Q', '10')],
    'Q17': [('24', '2021-3Q', '13'), ('23', '2021-3Q', '13')],
    'Q18': [('25', '2023-3Q', '16'), ('24', '2023-3Q', '16')],
    'Q19': [('25', '2023-3Q', '17'), ('25', '2022-3Q', '13'), ('24', '2023-3Q', '17'), ('24', '2022-3Q', '11'), ('23', '2022-3Q', '11')],
    'Q26': [('25', '2023-3Q', '21'), ('25', '2022-3Q', '15'), ('24', '2023-3Q', '21'), ('24', '2022-3Q', '13'), ('24', '2021-3Q', '18'), ('23', '2022-3Q', '13'), ('23', '2021-3Q', '18')],
    'Q28': [('25', '2023-3Q', '23'), ('25', '2022-3Q', '16'), ('24', '2023-3Q', '23'), ('24', '2022-3Q', '15'), ('23', '2022-3Q', '15')],
    'R03': [('24', '2023-3Q', '3')],
    'R04': [('25', '2022-3Q', '3'), ('24', '2023-3Q', '4'), ('24', '2022-3Q', '3'), ('24', '2021-3Q', '2'), ('23', '2022-3Q', '3'), ('23', '2021-3Q', '2')],
    'R06': [('24', '2023-3Q', '4b')],
    'R07': [('25', '2022-3Q', '7'), ('24', '2023-3Q', '7'), ('24', '2022-3Q', '6b'), ('24', '2021-3Q', '6'), ('23', '2022-3Q', '6'), ('23', '2021-3Q', '6')],
    'R08': [('24', '2023-3Q', '8')],
    'R09': [('25', '2022-3Q', '8'), ('24', '2023-3Q', '9'), ('24', '2022-3Q', '7'), ('23', '2022-3Q', '7')],
    'R10': [('24', '2023-3Q', '10-11')],
    'R14': [('24', '2023-3Q', '14-15')],
    'R18': [('24', '2023-3Q', '18')],
    'R19': [('24', '2023-3Q', '19')],
    'R20': [('24', '2023-3Q', '20')],
    'R22': [('24', '2023-3Q', '22')],
    'S04': [('24', '2022-3Q', '4'), ('24', '2021-3Q', '4'), ('23', '2022-3Q', '4'), ('23', '2021-3Q', '4')],
    'S12': [('24', '2022-3Q', '12'), ('23', '2022-3Q', '12')],
    'S14': [('24', '2022-3Q', '14'), ('24', '2021-3Q', '19'), ('23', '2022-3Q', '14'), ('23', '2021-3Q', '19')],
    'T15': [('23', '2021-3Q', '15'), ('25', '부록', '표'), ('24', '부록', '표'), ('23', '부록', '표')],
}
for n in ['3', '8', '9', '10', '11', '12', '14', '16', '17', '20', '21', '22', '23']:
    OTHER['T%02d' % int(n)] = [('23', '2021-3Q', n)]
# 등급: A 현 강의(기본) · B 전임 여인성 Resin-bonded restoration · C 서덕규 Successful cervical restoration(JB: '23년도 시험범위 아닙니다')
TIER = {'T21': 'B', 'T22': 'B', 'T23': 'B', 'T10': 'C', 'T11': 'C', 'T14': 'C', 'T16': 'C', 'U01': 'C'}
PROF_FIX = {'T21': '여인성', 'T22': '여인성', 'T23': '여인성', 'T10': '서덕규', 'T11': '서덕규', 'T14': '서덕규', 'T16': '서덕규', 'U01': '서덕규'}
# JB 쪽 이미지에서 잘라 넣는 그림(25판, 쪽 이미지 폭 924 기준 좌표) — 모두 답·해설 쪽 그림
CROP_BOX = {'Q23_a': ('25', 7, (476, 696, 880, 934)), 'Q26_a': ('25', 8, (474, 310, 866, 670)), 'Q28_a': ('25', 9, (474, 106, 872, 336))}
CROPS = {'Q23': {'a': ['Q23_a']}, 'Q26': {'a': ['Q26_a']}, 'Q28': {'a': ['Q28_a']}}
Q = []
def secyear(sec): return int(sec[2:4]) if re.match(r'20\d\d-3Q', sec) else None
for cid, ed, sec, num in CANON:
    x = find(ed, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t)
    short = re.sub(r'^★?\s*\d{1,2}(\s*-\s*\d{1,2})?\s*[.．]\s*', '', t.split('\n')[0]).strip()
    yrs = set(ty) | {secyear(sec)}
    for (e2, s2, n2) in OTHER.get(cid, []):
        x2 = find(e2, s2, n2); assert x2, (cid, e2, s2, n2)
        if secyear(s2): yrs.add(secyear(s2))
        yrs |= tag_years(x2['text'])[0]
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': TIER.get(cid, 'A'), 'prof': '',
              'src': f'JB {ed}판 · {sec} {num}번', 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True),
              'secy': secyear(sec), 'tal': bool(re.search(r'탈★|\(\s*탈\s*\)', stem_of(t))), 'pick': ''})

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
        cur = {'v': '', 'yrs': [], 'yrsnote': '', 'lec': [], 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': []}; ANN[parts[0]] = cur
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
    else:
        q.update({'v': 'na', 'yrsnote': '', 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': [], 'lk': '', 'xtra': []}); q['yrs'] = sorted(q['base'], reverse=True)
    q['prof'] = PROF_FIX.get(q['id']) or LK_PROF.get(q['lk'], '')
    o = []
    for (e2, s2, n2) in OTHER.get(q['id'], []):
        x2 = find(e2, s2, n2)
        if x2: o.append({'ed': e2, 'sec': s2, 'num': n2, 'pg': x2['pg'], 'pg2': x2['pg2'], 'text': x2['text']})
    q['other'] = o; q['lab24'] = ''; q['crops'] = CROPS.get(q['id'], {})
    q['fig'] = bool(re.search(r'사진|그림', ' '.join(q['text'].split('\n')[:3])))

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
for k, (ed, pg, box) in CROP_BOX.items():
    f = f'{BASE}{SUB}_20{ed}/{pg}.jpeg'
    if os.path.exists(f): IMG['crop'][k] = b64(Image.open(f).convert('RGB').crop(box), 85)
for k, v in J.prev_crops(SUB, CROPS).items(): IMG['crop'].setdefault(k, v)
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
MENT = {'25': ment('25', [1]), '24': ment('24', [1]), '23': ment('23', [1, 2])}
if __name__ == '__main__':
    print('Q', len(Q), '미복원', sum(1 for q in Q if re.fullmatch(r'\d+(-\d+)?\.\s*미복원', q['text'].strip())))
    for q in Q: print(f"{q['id']} {q['tier']} {str(q['yrs']):26} {q['jbtag']:24} {q['short'][:44]}")
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [(r['ed'], r['sec'], r['num'], r['first'][:25]) for r in LEDGER if r['st'] == 'ref'])
