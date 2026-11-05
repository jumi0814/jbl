import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_pharm4 as P, subject as S
BASE = J.JBX; SUB = 'PHARM4'
NPAGES = {}   # JB 판본 {'26': 쪽수, '25': …} — parse_pharm4.py를 쓴 뒤 채움
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
# (새 과목 — JB 분해 뒤 채움) OTHER = {id: [(판, 번호), …]} 같은 문제의 다른 판본 · 문항 = add(id, 판, 블록, tier, 교수, 출처 글) · 판본마다 for x in blocks[판]: add(…)
#   본보기: tools/cons/assemble.py 2절(새 판 문항 NEW26·놓을 자리) · tools/esth/assemble.py(연도 칸형) — 판본 사이 같은 문제는 OTHER로(대조표 연결 안 된 블록 0)
OTHER = {}
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

# ---------- 3. annotations ----------
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
for _pf, _fn in (('pred.txt', ''), ('final.txt', '1')):   # 10-29 사용자 '최종 N제라는 탭' — final.txt = 같은 문법(머리 fn=1 · build4가 강의 예상 목록에서 빼고 과목 '🎯 최종 N제' 탭에)
  if not os.path.exists(DIR + '/' + _pf): continue
  for line in open(DIR + '/' + _pf, encoding='utf-8'):
    line = line.rstrip('\n')
    if line.startswith('@'):
        p = [x.strip() for x in (line[3:] if line.startswith('@P ') else line[1:]).split('|')]
        cur = {'k': p[0], 't': '', 'b': '', 'q': '', 'a': ''}
        for x in p[1:]:
            k, _, v = x.partition('='); cur[k] = v
        if _fn: cur['fn'] = _fn
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
idmap = {(q['ed'], str(q['num'])): q['id'] for q in Q}   
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
MENT = {ed: ment(ed, [1]) for ed in NPAGES}   # JB 판 머리 멘트 쪽 — 판마다 맞게
if __name__ == '__main__':
    print('Q', len(Q), [(q['id'], q['prof'], q['yrs'], q['jbtag'], q['tal']) for q in Q])
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [ (r['ed'], r['num'], r['first'][:20]) for r in LEDGER if r['st'] == 'ref'])
