import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
"""ANAT4 임상두경부해부학(4Q) — JB 23·24판 → 정식 문항(Q)·같은 문제의 다른 판본(other)·대조표(LEDGER) (2026-11-16 JB 단계 · work/ANAT4/jb/R_JB_ANAT4.md)
id(강의와 무관 — 강의 나누기를 바꿔도 id·기록 그대로 · jb_lock.json이 잠금, 번호 당기기 금지):
  B01~B23 = '[임상두경부해부학 4Q 문제 뱅크]' n번(24판 번호 — 1~21은 23판도 같은 번호·같은 문제 · 22 = 24판 '씹기 근육(저작근)들의 기시부위와 정지부위' · 23 = 24판에만, 그림 글)
  X22 = 23판 뱅크 22번 'Masseter muscle의 기시와 정지'(24판에서 22번 글이 '씹기 근육(저작근)들 …'로 바뀜 — 묻는 범위가 달라 별개 · 2022년 기출문제 1번 'Masseter m 의 기시 정지'가 이 문제)
  M01~M04 = 23판 끝 '명훈 교수님'(3Q Neck dissection) [2018년 복원] 1~3 · [2017년 복원] 1 — 3Q ANAT의 M01~M04와 같은 문항(같은 id 꼴)
묶음 G = (id, 강의 키, tier, [(판, 칸, 번호) …]) — 첫 블록 = 정식(가장 최신 판) · 나머지 = 같은 문제의 다른 판본(OTHER)
  · '[2022년 기출문제]'·'[2023년 기출문제]' 목록 문항 = 가리키는 뱅크 문항의 다른 판본(출제 연도 = 그 목록 해 — 판 안의 '실린 연도 칸')
  · 문항에 연도 괄호가 없음 → 목록에 없는 뱅크 문항은 출제 연도 없음(실리지 않은 해 금지 · 판 해를 연도로 쓰지 않음)"""
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_anat4 as P, subject as S
BASE = J.JBX; SUB = 'ANAT4'
NPAGES = P.NPAGES
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
NOISE = re.compile(r'(반짤반탈|짤 변형|짤|탈|년도|년|이전|이후|~|’|\')')
def tag_years(text):
    """문항 첫머리(답 이전)의 연도 괄호 전부 — 이 과목 JB는 문항에 연도 괄호가 없음(목록 해·복원 칸 해로만) · '(Bank 12 번 참고)'·'(9개)'·'(fossa)'는 연도 아님"""
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = NOISE.sub(' ', g).replace('，', ',').strip().strip(',').strip()
        if not re.fullmatch(r'(20\d\d|\d\d)(\s*[,、]\s*(20\d\d|\d\d))*', g2): continue
        vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
        if not vs or not all(8 <= v <= 26 for v in vs): continue
        ys |= set(vs); raw.append('(' + re.sub(r'\s+', '', g) + ')')
    return ys, raw
def find(ed, sec, num):
    for x in blocks[ed]:
        if x['sec'] == sec and str(x['num']) == str(num): return x
    return None
def secyear(sec):
    """실린 연도 칸 — '2022년 기출문제'·'2018년 복원 · 명훈' → 22·18 · '문제 뱅크' → None"""
    m = re.match(r'(20\d\d)년', sec or ''); return int(m.group(1)) % 100 if m else None
def seclabel(sec): return sec

# ---------- 2. canonical questions ----------
# 강의 연결 교수(LK_PROF — 26 담당 미정 · 25 수업 표 담당) · HN = 뱅크(출제 교수 근거 없음 — '' · subject.py YEAR_PROF '-')
LK_PROF = {'LL': '방강미', 'UL': '장미숙', 'SPL': '방강미', 'HN': '', 'MH': '명훈'}
BK = '문제 뱅크'; Y22 = '2022년 기출문제'; Y23 = '2023년 기출문제'; H18 = '2018년 복원 · 명훈'; H17 = '2017년 복원 · 명훈'
def bk(n, eds=('24', '23')): return [(e, BK, str(n)) for e in eds]
G = [
    # ---- HN 두경부 문제 뱅크(머리 및 목 해부학 7판 — JB [참고] 쪽) · tier A
    ('B01', 'HN', 'A', bk(1) + [('24', Y22, '3'), ('23', Y22, '3')]),   # 입 주위 근육의 종류와 기능(9개) [참고] 225~230 · 2022년 3번 'Bank 1 번'
    ('B02', 'HN', 'A', bk(2)),            # 씹기 근육 기시·정지·작용 표 [참고] 243-257 — 관련 X22·B22(둘 다 'Bank 2번 참고')
    ('B03', 'HN', 'A', bk(3)),            # 턱관절 구조물 9가지 [참고] 286-287 — 23판 '턱관절의 구조물 및 도해.' → 24판 '구조물들의 명칭을 나열하시오.'(이전 출제 꼴)
    ('B04', 'HN', 'A', bk(4)),            # Facial a.의 가지(특히 Facial part) [참고] 381
    ('B05', 'HN', 'A', bk(5)),            # Maxillary a. n.의 가지 [참고] 395·574
    ('B06', 'HN', 'A', bk(6) + [('24', Y23, '3')]),   # Pterygoid plexus 15개 [참고] 418 · 2023년 3번
    ('B07', 'HN', 'A', bk(7)),            # Trigeminal n.(maxillary·mandibular n.) 주행·분지 [참고] 574-576·594
    ('B08', 'HN', 'A', bk(8)),            # Facial n. 요약 표 [참고] 643
    ('B09', 'HN', 'A', bk(9) + [('24', Y23, '2')]),   # 머리 및 목의 부교감 신경 계통 [참고] 714-721 · 2023년 2번
    ('B10', 'HN', 'A', bk(10)),           # Salivary gland 위치·개구 부위 [참고] 484-488
    ('B11', 'HN', 'A', bk(11)),           # 낱개머리뼈 Mx·Mn·bony palate [참고] 108-124·94-107·126 — 23판은 '11-1) Bony palate의 구성 뼈' + 예전 족보 자료(13~15쪽)
    ('B12', 'HN', 'A', bk(12) + [('24', Y23, '1')]),  # Infratemporal region(fossa) 경계·내용물 [참고] 826-827 · 2023년 1번
    ('B13', 'HN', 'A', bk(13)),           # Carotid triangle 경계·내용물 [참고] 938
    ('B14', 'HN', 'A', bk(14) + [('24', Y22, '4'), ('23', Y22, '4')]),   # Submandibular triangle 경계·내용물 [참고] 903-904 · 2022년 4번 · 24판 '[참고] 25년도 수업시간에 출제 예고한 슬라이드'
    ('B15', 'HN', 'A', bk(15)),           # Radical neck dissection 절단·보존 구조물 [참고] 694('출처를 찾지 못해 과거 참고해설을 그대로') — 관련 M04(1)
    ('B16', 'HN', 'A', bk(16)),           # Posterior triangle of the neck 경계·내용물 [참고] 989-997
    ('B17', 'HN', 'A', bk(17)),           # 입천장 신경·혈관 [참고] 470
    ('B18', 'HN', 'A', bk(18)),           # 혀 신경(일반감각·미각·운동) [참고] 482
    ('B19', 'HN', 'A', bk(19)),           # Laryngotomy·tracheotomy 시술 부위·주의 구조물 [참조] 530-533
    ('B20', 'HN', 'A', bk(20) + [('24', Y22, '2'), ('23', Y22, '2')]),   # 눈알 근육 6개·지배신경 [참조] 549·555·620 · 2022년 2번
    ('B21', 'HN', 'A', bk(21) + [('24', Y22, '5'), ('23', Y22, '5')]),   # Pterygopalatine fossa 경계·내용물 [참조] 866~869 · 2022년 5번
    ('B22', 'HN', 'A', bk(22, ('24',))),  # 24판 22번 '씹기 근육(저작근)들의 기시부위와 정지부위'(-> Bank 2번 참고) — 23판 22번(Masseter)과 묻는 범위가 달라 별개(X22)
    ('B23', 'HN', 'A', bk(23, ('24',))),  # 24판 23번 '입꼬리를 위로 올릴 때 작용하는 근육들'(그림 글 — 노란 형광) — 관련 B01
    ('X22', 'HN', 'A', [('23', BK, '22'), ('24', Y22, '1'), ('23', Y22, '1')]),   # 23판 22번 'Masseter muscle의 기시와 정지'(Bank 2번 참고) · 2022년 1번 'Masseter m 의 기시 정지 (Bank 2 번 참고)'
    # ---- MH 3Q 명훈 Neck dissection(4Q 강의·교과서에 없음 — 기출 참고) · tier C
    ('M01', 'MH', 'C', [('23', H18, '1')]),   # 경부 level 2 구분 landmarks (230830 명훈 Neck dissection p.24)
    ('M02', 'MH', 'C', [('23', H18, '2')]),   # functional neck dissection이 radical에 비해 save하는 구조물 3
    ('M03', 'MH', 'C', [('23', H18, '3')]),   # spinal accessory nerve 손상 후유증(구강악안면외과학교과서 p441)
    ('M04', 'MH', 'C', [('23', H17, '1')]),   # (1) Radical neck dissection 시 보존 구조물(림프절) (2★) Neck resection 분류 도해(답 그림 — 24쪽) — 관련 B15
]
CANON = [(cid, *toks[0]) for cid, lk, tier, toks in G]
OTHER = {cid: toks[1:] for cid, lk, tier, toks in G if toks[1:]}
LK = {cid: lk for cid, lk, tier, toks in G}
TIER = {cid: tier for cid, lk, tier, toks in G}
CROPS = {}   # JB 그림 조각(tools/jbfig.py → jb_crops.json)은 다음 단계 JF — 그림 문항 표 = 보고 3절
FIG = set()  # 시험에 그림이 주어진 문항 없음(그림은 모두 답·해설 쪽 — B01·B03·B11·B13·B14·M04 · 24판 B14 '출제 예고 슬라이드' · 보고 3절)
Q = []
for cid, ed, sec, num in CANON:
    x = find(ed, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t)
    yrs = set(ty) | ({secyear(sec)} if secyear(sec) else set())
    for (e2, s2, n2) in OTHER.get(cid, []):
        x2 = find(e2, s2, n2); assert x2, (cid, e2, s2, n2)
        if secyear(s2): yrs.add(secyear(s2))
        yrs |= tag_years(x2['text'])[0]
    short = re.sub(r'^\s*\d{1,2}\s*[.．]\s*', '', t.split('\n')[0]).strip()
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': TIER[cid], 'prof': '',
              'src': f'JB {ed}판 · {seclabel(sec)} {num}번', 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True),
              'secy': secyear(sec), 'tal': bool(re.search(r'\(\s*탈\s*\)|\(\s*\d\d\s*,\s*탈\s*\)', stem_of(t))), 'pick': ''})

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
if os.path.exists(DIR + '/annot.txt'):
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
        lkp_ = a['lec'][0].split(':')[1] if a['lec'] and ':' in a['lec'][0] else ''
        q.update({'v': a['v'], 'yrsnote': a['yrsnote'], 'rel': a['rel'], 'pair': a['pair'], 'A': a['A'], 'M': a['M'], 'N': a['N'], 'K': a.get('K', []), 'lk': lk_ or LK[q['id']], 'lkp': int(lkp_) if lkp_.isdigit() else None})
        q['yrs'] = sorted(set(q['base']) | set(a['yrs']), reverse=True); q['xtra'] = sorted(set(a['yrs']) - set(q['base']), reverse=True)
    else:
        q.update({'v': 'na', 'yrsnote': '', 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': [], 'K': [], 'lk': LK[q['id']], 'xtra': []}); q['yrs'] = sorted(q['base'], reverse=True)
    q['prof'] = LK_PROF.get(q['lk'], '')
    o = []
    for (e2, s2, n2) in OTHER.get(q['id'], []):
        x2 = find(e2, s2, n2)
        if x2: o.append({'ed': e2, 'sec': s2, 'num': n2, 'pg': x2['pg'], 'pg2': x2['pg2'], 'text': x2['text']})
    q['other'] = o; q['lab24'] = ''; q['crops'] = CROPS.get(q['id'], {})
    q['fig'] = q['id'] in FIG

# 답 칸 시작(build4 split_qa는 '답'·'[답]' 줄만 답으로 봄 — 이 JB 뱅크는 답 머리 없이 문제 줄 바로 뒤가 답) = annot ans=와 같은 지시를 기본으로
#   (annot에 ans=를 적으면 그것이 이김 · 글자는 그대로 · 쉼표로 여러 머리 = 판마다 첫 답 줄 · 같은 꼴 OPATH ANS_DEFAULT)
ANS_DEFAULT = {'B01': '*입 주위의 근육은', 'B02': '근육 기시 정지 작용', 'B03': '- 턱관절의 구조물 9가지,Mandibular condyle', 'B04': '목부분',
               'B05': '[maxillary a.]', 'B06': '- 15개', 'B07': '*내용이 너무 많아', 'B08': '성분 기능 분포', 'B09': '1) Oculomotor', 'B10': '1) 이하선',
               'B11': '1) Maxilla,좌', 'B12': '[1] 경계', 'B13': '[1] 경계', 'B14': '[1] 경계', 'B15': '절단하거나 묶는 구조물', 'B16': '[1] 경계',
               'B17': 'Hard palate', 'B18': '부위 일반감각', 'B19': '1) 후두절개술', 'B20': 'Oculomotor nerve Trochlear,*Ocular movement', 'B21': '1] 경계',
               'B22': '[참조]', 'B23': 'Levator anguli oris m.', 'X22': 'Bank 2번 참고'}
for cid, v in ANS_DEFAULT.items():
    ANN.setdefault(cid, {}).setdefault('ans', v)

LECT = []; TABLES = []
# ---------- 5. predicted ----------
PRED = []; cur = None
for _pf, _fn in (('pred.txt', ''), ('final.txt', '1')):   # 10-29 사용자 '최종 N제라는 탭' — final.txt = 같은 문법(머리 fn=1)
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
        ls = [l for l in P.rd(f'{BASE}{SUB}_20{ed}/{p}.txt').split('\n') if '무단인쇄' not in l and l.strip()]
        if ls and re.fullmatch(r'\s*\d{1,3}\s*', ls[0]): ls = ls[1:]   # 쪽 번호 줄
        t += '\n'.join(ls) + '\n'
    return t.strip()
MENT = {'24': ment('24', [1]), '23': ment('23', [1])}   # 판 1쪽 = 학습부 멘트 + 수업 표(24판 = '2025 4Q JB' 25년 멘트 · 23판 = 23년 멘트)
if __name__ == '__main__':
    used = {}
    for cid, lk, tier, toks in G:
        for b in toks: used.setdefault('|'.join(b), []).append(cid)
    allk = [f"{ed}|{x['sec']}|{x['num']}" for ed in NPAGES for x in blocks[ed]]
    print('Q', len(Q), '· 블록', len(allk), '· 묶음 안 블록', len(used), '· 못 쓴 블록', [k for k in allk if k not in used], '· 없는 블록', [k for k in used if k not in allk])
    print('두 카드 이상에 든 블록', {k: v for k, v in used.items() if len(v) > 1})
    print('ids 겹침', [c for c in LK if list(LK).count(c) > 1], '· 카드 수', len(G), len(set(LK)))
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [(r['ed'], r['sec'], r['num'], r['first'][:25]) for r in LEDGER if r['st'] == 'ref'])
    for ed in NPAGES: print(f' {ed}판', {s_: sum(1 for r in LEDGER if r['ed'] == ed and r['st'] == s_) for s_ in ('card', 'dup', 'ref')})
    if '-v' in sys.argv:
        for q in Q: print(f"{q['id']} {q['lk']:4} {q['tier']} {str(q['yrs']):12} {len(q['other'])} {q['short'][:50]}")
