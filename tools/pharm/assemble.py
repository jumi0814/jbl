import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_pharm as P, subject as S
BASE = J.JBX; SUB = 'PHARM'
NPAGES = {'26': 26, '25': 26, '24': 40, '23': 54, '23q4': 5}   # 26판 = 2026 3Q JB(2025년 시험까지 · 10-15 통합) · 23q4 = 2023 4Q JB 1~5쪽(멘트 + <항불안제>만 — 26 3Q 새 강의 ANX의 참고 기출)
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
            if ed in ('24', '23') and ('’' not in g and "'" not in g):
                out.append(v + 2 if v + 2 < secy else v)   # 학번 → 연도(+2)
            else: out.append(v)
        ys |= set(out); raw.append('(' + g.strip() + ')')
    return ys, raw

def secyear(sec): return int(sec) % 100
LK_PROF = {'RX': '백정화', 'XE': '이윤실', 'BT': '김우진', 'ACU': '우경미', 'CHR': '우경미', 'HM': '우경미', 'DS': '조영단', 'ANX': '김우진'}   # ANX = 26 3Q 새 강의(김우진) — JB 기출은 4Q 이윤실·류현모(tier C)
TOPIC_LK = {'RX': 'RX', 'XE': 'XE', 'BT': 'BT', 'PN': 'CHR', 'HM': 'HM', 'DS': 'DS', 'AX': 'ANX'}
TOPIC_PROF = {'RX': '백정화', 'XE': '이윤실', 'BT': '김우진', 'PN': '우경미', 'HM': '우경미', 'DS': '조영단', 'AX': '이윤실'}
import difflib
DUP = re.compile(r'(20\d\d)\s*년?\s*(\d{1,2})\s*번\s*(?:문항\s*)?중복|^\s*\d{1,2}\s*[.．]\s*(\d{1,2})\s*번\s*문항\s*중복')
def sig(t):
    ls = [l for l in stem_of(t).split('\n') if re.sub(r'^\s*\d{1,2}\s*[.．]\s*', '', l).strip()]
    s0 = (ls[0] + ' ' + (ls[1] if len(ls) > 1 and len(re.sub(r'^\s*\d{1,2}\s*[.．]\s*', '', ls[0]).strip()) < 12 else '')) if ls else ''
    s0 = re.sub(r'^\s*\d{1,2}\s*[.．]\s*', '', s0); s0 = re.sub(r'\([^)]*\)', '', s0)
    s0 = re.sub(r'[^0-9A-Za-z가-힣]', '', s0).lower()
    return s0[:70]
def find(ed, topic, sec, num):
    for x in blocks[ed]:
        if x['topic'] == topic and x['sec'] == sec and str(x['num']) == str(num): return x
    return None
CANON, OTHER, ptr = [], {}, {}
counter = {}
# 1차: 원래 블록 / 2차: 답안에서 분리된 블록(split) — 분리 블록의 새 id는 기존 번호 뒤에 붙어 기존 id(채점·표시 키)가 바뀌지 않음
for ed, x in [(e, x) for e in ('25', '24', '23') for x in blocks[e] if not x.get('split')] + [(e, x) for e in ('25', '24', '23') for x in blocks[e] if x.get('split')]:
    if True:
        key = (ed, x['topic'], x['sec'], x['num']); t = '\n'.join(x['lines'])
        m = DUP.search(t.split('\n')[0] + ' ' + (t.split('\n')[1] if '\n' in t else ''))
        if m:
            tsec = m.group(1) or x['sec']; tnum = m.group(2) or m.group(3)
            tgt = find(ed, x['topic'], tsec, tnum)
            cid = ptr.get((ed, x['topic'], tsec, str(tnum))) if tgt else None
            if cid: OTHER.setdefault(cid, []).append((ed, x['topic'], x['sec'], x['num'])); ptr[key] = cid; continue
        s = sig(t)
        best, bscore = None, 0
        for c in CANON:
            if c[1] != x['topic']: continue
            r = difflib.SequenceMatcher(None, s, c[5]).ratio()
            if r > bscore: best, bscore = c, r
        if best and ((bscore >= 0.72 and len(s) >= 8) or (bscore >= 0.99 and len(s) >= 4)):
            OTHER.setdefault(best[0], []).append((ed, x['topic'], x['sec'], x['num'])); ptr[key] = best[0]; continue
        n = counter.get(x['topic'], 0) + 1; counter[x['topic']] = n
        cid = f'{x["topic"]}{n:02d}'; CANON.append((cid, x['topic'], ed, x['sec'], x['num'], s)); ptr[key] = cid
# 분리 블록 카드는 id는 뒤에 붙었지만 목록 순서는 삼켰던 문항(같은 판·칸의 직전 번호) 바로 뒤로
for c in [c for c in CANON if (find(c[2], c[1], c[3], c[4]) or {}).get('split')]:
    prev = ptr.get((c[2], c[1], c[3], str(int(c[4]) - 1)))
    if prev and prev != c[0]:
        CANON.remove(c); CANON.insert(next(i for i, c2 in enumerate(CANON) if c2[0] == prev) + 1, c)
# ---- 26판(2026 3Q JB — 2025년 시험까지) · 23 4Q JB(<항불안제>만): 블록마다 직접 정한 연결(10-15) ----
# 값: 기존 id = 그 문항의 다른 판본(OTHER)에 덧붙임(목록이면 여러 문항에) · ('NEW', 새 id) = 새 정식 문항(표시 원문 = 이 블록, id는 jb_lock에 없는 새 번호)
#     'LOST' = 'N. 중복복원'(번호만 — 어느 문항과 겹치는지 표기 없음 → 대조표 '미복원 표기', 카드 없음)
# 판단 근거(같은 문제/별개)는 work/PHARM/jb26/R_JB26.md 3절 — 같은 질문·같은 답이면 연결, 보기·답이 다르면 별개(annot rel=)
MAP26 = {
    ('RX', '2025', '1'): ('NEW', 'RX37'), ('RX', '2025', '2'): ('NEW', 'RX38'), ('RX', '2025', '3'): ('NEW', 'RX39'), ('RX', '2025', '4'): ('NEW', 'RX40'),
    ('RX', '2025', '5'): ('NEW', 'RX41'), ('RX', '2025', '6'): 'RX09', ('RX', '2025', '7'): ('NEW', 'RX42'),
    ('RX', '2024', '1'): 'RX01', ('RX', '2024', '2'): 'RX02', ('RX', '2024', '3'): 'RX03', ('RX', '2024', '4'): 'RX04',
    ('RX', '2023', '1'): 'RX05', ('RX', '2023', '2'): 'RX02', ('RX', '2023', '3'): 'RX06', ('RX', '2023', '4'): 'RX03',
    ('XE', '2025', '1'): ('NEW', 'XE22'), ('XE', '2025', '2'): ('NEW', 'XE23'), ('XE', '2025', '3'): 'XE02', ('XE', '2025', '4'): ('NEW', 'XE24'), ('XE', '2025', '5'): ('NEW', 'XE25'),
    ('XE', '2025', '6'): ('NEW', 'XE26'), ('XE', '2025', '7'): 'XE16', ('XE', '2025', '8'): 'XE04', ('XE', '2025', '9'): 'XE17',
    ('XE', '2024', '1'): 'XE01', ('XE', '2024', '2'): 'XE02', ('XE', '2024', '3'): 'XE03',
    ('XE', '2023', '1'): 'XE04', ('XE', '2023', '2'): 'XE05', ('XE', '2023', '3'): 'XE03', ('XE', '2023', '4'): 'XE06', ('XE', '2023', '5'): 'XE07',
    ('BT', '2025', '1'): 'BT01', ('BT', '2025', '2'): 'BT08', ('BT', '2025', '3'): 'BT02', ('BT', '2025', '4'): 'BT03', ('BT', '2025', '5'): ('NEW', 'BT20'),
    ('BT', '2025', '6'): 'BT05', ('BT', '2025', '7'): 'BT06', ('BT', '2025', '8'): 'LOST', ('BT', '2025', '9'): 'BT09', ('BT', '2025', '10'): 'BT07',
    ('BT', '2024', '1'): 'BT01', ('BT', '2024', '2'): 'BT02', ('BT', '2024', '3'): 'BT03', ('BT', '2024', '4'): 'BT04', ('BT', '2024', '5'): 'BT05',
    ('BT', '2023', '1'): 'BT01', ('BT', '2023', '2'): 'BT04', ('BT', '2023', '3'): 'BT06', ('BT', '2023', '4'): 'BT07', ('BT', '2023', '5'): 'BT02', ('BT', '2023', '6'): 'BT03', ('BT', '2023', '7'): 'BT08',
    ('PN', '2025', '1'): ['PN05', 'PN06', 'PN07'], ('PN', '2025', '2'): 'LOST', ('PN', '2025', '3'): 'PN09', ('PN', '2025', '4'): 'PN03', ('PN', '2025', '5'): 'LOST',
    ('PN', '2025', '6'): 'PN04', ('PN', '2025', '7'): 'PN08', ('PN', '2025', '7-2'): ('NEW', 'PN27'),
    ('PN', '2024', '1'): 'PN01', ('PN', '2024', '2'): 'PN02', ('PN', '2024', '3'): 'PN03', ('PN', '2024', '4'): 'PN04', ('PN', '2024', '5'): 'PN05', ('PN', '2024', '6'): 'PN06', ('PN', '2024', '7'): 'PN07', ('PN', '2024', '8'): 'PN08',
    ('PN', '2023', '1'): 'PN01', ('PN', '2023', '2'): 'PN09', ('PN', '2023', '3'): 'PN02', ('PN', '2023', '4'): 'PN03', ('PN', '2023', '5'): 'PN04', ('PN', '2023', '6'): 'PN10',
    ('HM', '2025', '1'): ('NEW', 'HM26'), ('HM', '2025', '2'): ('NEW', 'HM27'), ('HM', '2025', '3'): ('NEW', 'HM28'), ('HM', '2025', '4'): 'HM02', ('HM', '2025', '5'): 'HM03',
    ('HM', '2024', '1'): 'HM01', ('HM', '2024', '2'): 'HM02', ('HM', '2024', '3'): 'HM03', ('HM', '2024', '4'): 'HM04',
    ('HM', '2023', '1'): 'HM05', ('HM', '2023', '2'): 'HM04', ('HM', '2023', '3'): 'HM06', ('HM', '2023', '4'): 'HM03',
    ('AX', '2025', '1'): ('NEW', 'AX01'), ('AX', '2025', '2'): ('NEW', 'AX02'), ('AX', '2025', '3'): ('NEW', 'AX03'), ('AX', '2025', '4'): ('NEW', 'AX04'), ('AX', '2025', '4-1'): ('NEW', 'AX05'),
    ('AX', '2025', '5'): ('NEW', 'AX06'), ('AX', '2025', '6'): ('NEW', 'AX07'),
    ('AX', '2024', '1'): ('NEW', 'AX08'), ('AX', '2024', '2'): 'AX01', ('AX', '2024', '3'): 'AX02', ('AX', '2024', '4'): ('NEW', 'AX09'), ('AX', '2024', '5'): ('NEW', 'AX10'), ('AX', '2024', '6'): ('NEW', 'AX11'),
    ('AX', '2023', '1'): 'AX06', ('AX', '2023', '2'): ('NEW', 'AX12'),
}
MAPQ4 = {
    ('AX', '2022', '1'): ('NEW', 'AX13'), ('AX', '2022', '2'): ('NEW', 'AX14'), ('AX', '2022', '3'): ('NEW', 'AX15'), ('AX', '2022', '4'): ('NEW', 'AX16'), ('AX', '2022', '5'): ('NEW', 'AX17'),
    ('AX', '2021', '1'): 'AX05', ('AX', '2021', '2'): ('NEW', 'AX18'), ('AX', '2021', '3'): 'AX12', ('AX', '2021', '4'): 'AX03',
    ('AX', '2020', '1'): ('NEW', 'AX19'), ('AX', '2020', '2'): ('NEW', 'AX20'), ('AX', '2020', '3'): ('NEW', 'AX21'), ('AX', '2020', '4'): 'AX12', ('AX', '2020', '5'): ('NEW', 'AX22'),
    ('AX', '2020', '6'): 'AX03', ('AX', '2020', '7'): ('NEW', 'AX23'), ('AX', '2020', '8'): 'AX05', ('AX', '2020', '9'): ('NEW', 'AX24'),
}
LOST = set(); NEW26 = []
for ed_, M_ in (('26', MAP26), ('23q4', MAPQ4)):
    assert len(M_) == len(blocks[ed_]), (ed_, len(M_), len(blocks[ed_]))
    for x in blocks[ed_]:
        k_ = (x['topic'], x['sec'], str(x['num'])); v_ = M_[k_]; key = (ed_, x['topic'], x['sec'], x['num'])   # KeyError = 연결 안 정한 블록
        if v_ == 'LOST': LOST.add(key); continue
        if isinstance(v_, tuple):
            cid = v_[1]; assert all(c[0] != cid for c in CANON), cid   # 새 id = 10-15 처음 빌드 때 jb_lock.json에 없던 새 번호(기존 id 재사용 금지 — 이후 빌드에선 잠금에 이 id·해시가 있음)
            CANON.append((cid, x['topic'], ed_, x['sec'], x['num'], sig(x['text']))); ptr[key] = cid; NEW26.append(cid); continue
        for cid in ([v_] if isinstance(v_, str) else v_):
            assert any(c[0] == cid for c in CANON), cid
            OTHER.setdefault(cid, []).append(key)
        ptr[key] = v_ if isinstance(v_, str) else v_[0]
# 목록 순서: 26판 2025 칸 새 문항은 그 주제 첫 기존 카드 앞(JB 26판 순서) · 통증 2025-7 (2)는 같은 증례 PN08 바로 뒤 · 항불안제(AX)는 맨 끝(새 강의 ANX)
_new = [c for c in CANON if c[0] in NEW26]; CANON[:] = [c for c in CANON if c[0] not in NEW26]
for c in _new:
    if c[1] == 'AX': CANON.append(c); continue
    if c[0] == 'PN27': CANON.insert(next(i for i, c2 in enumerate(CANON) if c2[0] == 'PN08') + 1, c); continue
    _at = next(i for i, c2 in enumerate(CANON) if c2[1] == c[1] and c2[0] not in NEW26)
    CANON.insert(_at, c)
FIGQ = {'RX42'}   # 문제 쪽에 표(그림)가 있는 26판 새 문항 — 'JB 원본에서 그림 확인' 안내(그림 붙이기는 다음 단계)
FIGNO = {'PN27'}   # 낱말 속 '사진'(마약유사진통제)이 그림 단서로 잘못 잡힌 새 문항
Q = []
CROPS = {}
for cid, topic, ed, sec, num, _s in CANON:
    tier, pf = ('C' if topic == 'AX' else 'A'), None   # AX = 4Q 항불안제(이윤실·류현모 출제) — 참고(⭐ 연결 의무 없음)
    x = find(ed, topic, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t, ed, sec)
    short = next((re.sub(r'^\s*(\d{1,2}(-\d)?)\s*[.．)]\s*', '', l).strip() for l in t.split('\n') if re.sub(r'^\s*(\d{1,2}(-\d)?)\s*[.．)]\s*', '', l).strip()), '')
    yrs = set(ty) | ({secyear(sec)} if not (x.get('sub') and ty) else set())   # 26판 소문항(4-1 등)은 제 괄호 연도만(머리 문항 칸 해를 붙이지 않음)
    for o_ in OTHER.get(cid, []):
        e2, tp2, s2, n2 = o_; x2 = find(e2, tp2, s2, n2); t2 = tag_years(x2['text'], e2, s2)[0] if x2 else set()
        if not (x2 and x2.get('sub') and t2): yrs.add(secyear(s2))
        yrs |= t2
    lname_ = S.LECMAP[TOPIC_LK[topic]][1].split("(")[0]
    if ed == '23q4': src = f'JB 23판 · {sec}년 칸 · 4Q JB {lname_} {num}번'   # 23 4Q JB(판 연도는 화면에 쓰지 않음 — src_short가 '2022년 칸 1번'만)
    elif '-' in str(num): src = f'JB {ed}판 · {sec}년 칸 · {lname_} {str(num).split("-")[0]}번 소문항({num})'
    else: src = f'JB {ed}판 · {sec}년 칸 · {lname_} {num}번'
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': tier, 'prof': x['prof'] or TOPIC_PROF[topic],
              'src': src, 'prof0': x['prof'] or TOPIC_PROF[topic], 'topic': topic, 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)) + (' (학습부 예상 — 선지 미복원)' if '(예상)' in short else ''), 'base': sorted(yrs, reverse=True),
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
    if not q['lk']: q['lk'] = TOPIC_LK[q['topic']]
    if q['prof0'] == '백정화' and q['topic'] == 'XE': pass  # 22년 구강건조증은 백정화 출제 — 교수 유지
    o = []
    for o_ in OTHER.get(q['id'], []):
        e2, tp2, s2, n2 = o_; x2 = find(e2, tp2, s2, n2)
        if x2: o.append({'ed': e2, 'sec': s2 + '년 칸', 'num': n2, 'pg': x2['pg'], 'pg2': x2['pg2'], 'text': x2['text']})
    q['other'] = o; q['lab24'] = ''; q['crops'] = CROPS.get(q['id'], {})
    q['fig'] = bool(re.search(r'그림|모식도|사진|아래와 같이|빈칸빵|가리키는|표시', ' '.join(q['text'].split('\n')[:3]))) and q['id'] not in FIGNO or q['id'] in FIGQ
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
idmap = {(q['ed'], q['sec'], str(q['num']), q['topic']): q['id'] for q in Q}
rev = {}
for cid, lst in OTHER.items():
    for o_ in lst:
        e2, tp2, s2, n2 = o_; rev.setdefault((e2, s2, str(n2), tp2), []).append(cid)
for ed in NPAGES:
    for x in blocks[ed]:
        key = (ed, x['sec'], str(x['num']), x['topic']); first = x['text'].split('\n')[0][:70]
        if key in idmap: st, to = 'card', [idmap[key]]
        elif key in rev: st, to = 'dup', rev[key]
        elif (ed, x['topic'], x['sec'], x['num']) in LOST: st, to = 'lost', []   # 26판 'N. 중복복원'(번호만)
        else: st, to = 'ref', []
        LEDGER.append({'ed': ed, 'sec': x['sec'] + '년', 'num': x['num'], 'pg': x['pg'], 'first': first, 'st': st, 'to': to})
def ment(ed, pages):
    t = ''
    for p in pages:
        s = P.rd(f'{BASE}{SUB}_20{ed}/{p}.txt'); t += '\n'.join(l for l in s.split('\n') if '무단인쇄' not in l and l.strip()) + '\n'
    return t.strip()
MENT = {'26': ment('26', [1]), '25': ment('25', [1]), '24': ment('24', [1]), '23': ment('23', [1]), '23q4': ment('23q4', [1])}   # 26판 1쪽 = 26 멘트·수업 표 · 23q4 1쪽 = 23 4Q 멘트(항불안제 이윤실·류현모)
if __name__ == '__main__':
    print('Q', len(Q))
    for q in Q: print(q['id'], q['tier'], q['prof'], q['yrs'], q['jbtag'], q['short'][:36])
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'lost', 'ref')}, [(r['ed'], r['sec'], r['num'], r['first'][:28]) for r in LEDGER if r['st'] == 'ref'])
    for e_ in ('26', '23q4'): print(f'{e_}판 블록', {s_: sum(1 for r in LEDGER if r['ed'] == e_ and r['st'] == s_) for s_ in ('card', 'dup', 'lost', 'ref')})
    print('새 문항', len(NEW26), NEW26)
