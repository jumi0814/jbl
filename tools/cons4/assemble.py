import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
"""CONS4 임상치과보존학(4Q) — JB 23·24·25판 → 정식 문항(Q)·같은 문제의 다른 판본(other)·대조표(LEDGER) (2026-11-16 JB 단계 · work/CONS4/jb/R_JB_CONS4.md)
id = JB 교수 칸 글자 + 번호(25판 차례 · jb_lock.json이 잠금 — 번호 당기기 금지):
  M 유연지 Endodontic Microsurgery(EMS) · L 이우철 요인 1·2(SFA·SFB — 26 'Part1'만 와서 강의 둘로 나눔, 글자는 이우철 칸 하나) · T 금기연 TEMS · R 치아재식술 및 치아이식술(REP)
  V 손원준 생활치수치료(VPT) · I 손원준 근관치료 관점에서 본 임플란트 프로토콜(IMP)
묶음 G = (id, 강의 키, tier, [블록 '판|칸|번호' …]) — 첫 블록 = 정식(가장 최신 판 = 25판), 나머지 = 같은 문제의 다른 판본(OTHER)
  · 판 사이 같은 문제 = 문제 글이 같고 괄호 연도가 이어지는 것(24판 유연지 21·22번처럼 괄호 없던 것은 25판 '(출제년도 미상)'으로 같은 글)
  · 보기만 다시 복원된 같은 문제(L18 23판 8번 4지선다 '답: 없음' → 24·25판 5지선다)·답이 바뀐 같은 문제(M07 '4)' → '4,6' · L17 '3?' → '1, 3?' · R01 '1,3' → '3')는 한 카드(앞면 = 25판 · 사용자 10-24 결정 ①)
  · 비슷하지만 묻는 것·답이 다른 것은 별개 — L06·L07(25판 12·12-1 '같은 문제로 보이는데, 복원이 정확하지 않아' · 답 4? / 1?) · I03·I04(39·39-1) · M06·M07(6 서술 '짤로 복원' · 6-1 객관식) — rel=은 다음 단계 annot(짝 목록 보고 3절)"""
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_cons4 as P, subject as S
BASE = J.JBX; SUB = 'CONS4'
NPAGES = P.NPAGES
LECMAP = S.LECMAP

# ---------- 1. JB blocks ----------
blocks = {}
for ed, n in NPAGES.items():
    out = []
    for x in P.parse(ed, n):
        x['text'] = '\n'.join(x['lines']).strip(); out.append(x)
    blocks[ed] = out
ANSRE = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$|^\s*교과서\s*답\s*[:：]')
def stem_of(t):
    out = []
    for l in t.split('\n'):
        if ANSRE.match(l): break
        out.append(l)
    return ' '.join(out)
def tag_years(text):
    """문항 첫머리(답 이전)의 연도 괄호 전부 — (24 탈) · (24 짤) · (23,21) · (24,23,22,21,20) · (20,16,14,11) — '(출제년도 미상)'·'(복원미흡)'·'(46 번 치아 …)'·'(1)'은 연도 아님"""
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = re.sub(r'(반짤반탈|변형|짤|탈|년|~)', ' ', g).replace('，', ',')
        if not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*[,、]\s*(20\d\d|\d\d)?)*\s*', g2): continue
        vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
        if not vs or not all(8 <= v <= 26 for v in vs): continue
        ys |= set(vs); raw.append('(' + re.sub(r'\s+', ' ', g).strip() + ')')
    return ys, raw
def find(ed, sec, num):
    for x in blocks[ed]:
        if x['sec'] == sec and str(x['num']) == str(num): return x
    return None
SECLAB = {'유연지': '유연지 교수님', '이우철': '이우철 교수님', '금기연 TEMS': '금기연 교수님(TEMS)', '금기연 재식': '금기연 교수님(치아재식술 및 치아이식술)',
          '손원준': '손원준 교수님', '연도 미상': '기출년도 모르는 문제', '금기연 참고': '[참고] 금기연 교수님'}
def seclabel(sec): return SECLAB.get(sec, sec)

# ---------- 2. canonical questions ----------
# 강의별 담당(26 담당 · 26 자료가 없는 강의는 25 담당 — RULES 13 10-26 'LK_PROF = 26 담당')
LK_PROF = {'IRR': '손원준', 'SFA': '이우철', 'SFB': '이우철', 'EMS': '유연지', 'TEMS': '금기연', 'REP': '금기연', 'VPT': '손원준', 'IMP': '손원준'}
G = [
    # ---- M 유연지 — Endodontic Microsurgery(EMS · 25 임시)
    ('M01', 'EMS', 'A', ['25|유연지|1']),                                   # 핸드피스 그림(문제 쪽) — 기구 특징·용도·장점
    ('M02', 'EMS', 'A', ['25|유연지|2']),                                   # 과정 7단계
    ('M03', 'EMS', 'A', ['25|유연지|3', '24|유연지|20']),                   # Conventional vs micro 차이(표)
    ('M04', 'EMS', 'A', ['25|유연지|4', '24|유연지|21']),                   # 하악 구치부 flap · 수직 incision
    ('M05', 'EMS', 'A', ['25|유연지|5', '24|유연지|22']),                   # 치주 좋고 보철물 → Oschebein-Lubke flap
    ('M06', 'EMS', 'A', ['25|유연지|6']),                                   # Flap 형성 시 주의사항(서술 '24 짤' — M07과 별개 · rel)
    ('M07', 'EMS', 'A', ['25|유연지|6-1', '24|유연지|23', '23|연도 미상|20']),   # flap 디자인 틀린 것(23판 답 4) → 24·25판 4, 6)
    # ---- L 이우철 — 요인 Part1(SFA · 26) / 요인 2(SFB · 25 임시)
    ('L01', 'SFA', 'A', ['25|이우철|7', '24|이우철|3', '23|이우철|3']),     # 성공의 임상적 기준
    ('L02', 'SFA', 'A', ['25|이우철|8']),                                   # 성공·실패 요소 중 해부학적 구조 3가지(26 p.42 '해부학적 구조(석회화, 근관의 형태와 수, 치아 경사도 등)')
    ('L03', 'SFA', 'A', ['25|이우철|9', '24|이우철|12', '23|이우철|12']),   # 방사선학적 성공 3가지
    ('L04', 'SFA', 'A', ['25|이우철|10', '24|이우철|10', '23|이우철|10']),  # 조직학적 성공
    ('L05', 'SFA', 'A', ['25|이우철|11', '24|이우철|11', '23|이우철|11']),  # 방사선학적 실패 기준(교과서 답·PPT 답 — ans=교과서 답)
    ('L06', 'SFA', 'A', ['25|이우철|12', '24|이우철|5', '23|이우철|5']),    # 옳은 것(재치료 성공률·금관·온도·나이·전신질환) 답 4?
    ('L07', 'SFA', 'A', ['25|이우철|12-1', '24|이우철|5-1', '23|이우철|5-2']),   # 맞는 것(같은 축 다른 복원) 답 1? — L06과 별개 · rel
    ('L08', 'SFA', 'A', ['25|이우철|13']),                                  # 사진 → Incomplete healing(scar)(사진 임의로 가져옴)
    ('L09', 'SFB', 'A', ['25|이우철|14']),                                  # VRF 옳은 것(25 요인 2 VRF)
    ('L10', 'SFA', 'A', ['25|이우철|15']),                                  # MTA one step apexification 장점
    ('L11', 'SFA', 'A', ['25|이우철|16']),                                  # overfilling 객관식(복원미흡 — 답 ?)
    ('L12', 'SFA', 'A', ['25|이우철|17', '24|이우철|16', '23|이우철|16']),  # MTA 임상적 적용
    ('L13', 'SFA', 'A', ['25|이우철|18', '24|이우철|1', '23|이우철|1']),    # MTA 적용 방법 3가지(23판 답 없음)
    ('L14', 'SFA', 'A', ['25|이우철|19', '24|이우철|2', '23|이우철|2']),    # 근관치료용 MTA 제품 3가지 이상
    ('L15', 'SFA', 'A', ['25|이우철|20', '24|이우철|17']),                  # #11 증례 → 3개월 간격 팔로업(periapical scar)
    ('L16', 'SFA', 'A', ['25|이우철|21', '24|이우철|6', '23|이우철|6']),    # periapical scar 진단명
    ('L17', 'SFA', 'A', ['25|이우철|22', '24|이우철|7', '23|이우철|7']),    # 옳지 않은 것(나이·외과적) 23·24판 3? → 25판 1, 3?
    ('L18', 'SFA', 'A', ['25|이우철|23', '24|이우철|8', '23|이우철|8']),    # 외과적 치근단 수술 필요 환자(23판 4지 '없음' → 24·25판 5지 '5?')
    ('L19', 'SFB', 'A', ['25|이우철|24', '24|이우철|9', '23|이우철|9']),    # 사진 → apico 실패(isthmus 처리 실패)
    ('L20', 'SFA', 'A', ['25|이우철|25', '24|이우철|13', '23|이우철|13']),  # 투과성 병소·증상 없음 → 3m r/c(복원미흡)
    ('L21', 'SFB', 'A', ['25|이우철|26', '24|이우철|4', '23|이우철|4']),    # POOR PAST 8가지
    ('L22', 'SFB', 'A', ['25|이우철|27', '24|이우철|14', '23|이우철|14']),  # #46 치근단 수술 후 병소 → MB·ML isthmus
    ('L23', 'SFB', 'A', ['25|이우철|28', '24|이우철|19']),                  # C canal 모식도(semi-colon 68%)
    ('L24', 'SFB', 'A', ['25|이우철|29', '24|이우철|15', '23|이우철|15']),  # 한국인 C-shaped incidence 33%
    ('L25', 'SFB', 'A', ['25|이우철|30', '24|이우철|18']),                  # 상악 제2대구치 근관 형태 종단면(답 = 슬라이드 그림)
    # ---- T 금기연 — TEMS(25 임시)
    ('T01', 'TEMS', 'A', ['25|금기연 TEMS|31', '24|금기연 TEMS|24', '23|금기연 참고|28']),   # Traditional·Micro·TEMS 비교 표
    ('T02', 'TEMS', 'A', ['25|금기연 TEMS|32', '24|금기연 TEMS|25', '23|금기연 참고|29']),   # CARP transplantation 장점·한계
    # ---- R 치아재식술 및 치아이식술(REP · 25 금기연 — 2023 손원준 출제)
    ('R01', 'REP', 'A', ['25|금기연 재식|33', '24|손원준|30']),             # 자가치아이식술 틀린 것(24판 1,3 → 25판 3)
    # ---- V 손원준 — 생활치수치료(VPT · 25 임시)
    ('V01', 'VPT', 'A', ['25|손원준|34']),                                  # 그림 → MTA VPT 과정
    ('V02', 'VPT', 'A', ['25|손원준|35']),                                  # Dycal·MTA 한계
    ('V03', 'VPT', 'A', ['25|손원준|36']),                                  # 천공 옳은 것(JB 참고 = 교과서 p.456-459 · 강의 연결 불확실 — 손원준 칸 VPT 문항 바로 뒤)
    # ---- I 손원준 — 근관치료 관점에서 본 임플란트 프로토콜(IMP · 25 임시)
    ('I01', 'IMP', 'A', ['25|손원준|37']),                                  # 상악 중절치 apex buccal · 즉시 임플란트
    ('I02', 'IMP', 'A', ['25|손원준|38', '24|손원준|26', '23|손원준|17']),  # endodontic surgery evolutionary event
    ('I03', 'IMP', 'A', ['25|손원준|39', '24|손원준|27', '23|손원준|18']),  # Implant vs RCT 성공률 비교 못 하는 이유
    ('I04', 'IMP', 'A', ['25|손원준|39-1', '24|손원준|27-1', '23|손원준|19']),   # survival rate 단순 비교 문제(사진) — I03과 별개 · rel
    ('I05', 'IMP', 'A', ['25|손원준|40', '24|손원준|28']),                  # slow vs rapid extrusion
    ('I06', 'IMP', 'A', ['25|손원준|41', '24|손원준|29']),                  # orthodontic extrusion 장점
    ('I07', 'IMP', 'A', ['25|손원준|42', '24|손원준|31', '23|연도 미상|21']),   # 엔도 실패 단일치아 임플란트 고려사항
]
ANSAT = {'L05': '교과서 답'}   # 답 칸이 '교과서 답:'으로 시작(build4 split_qa는 '답'으로 시작하는 줄만 봄) — annot ans=와 같은 지시(annot에 ans=를 적으면 그것이 이김)
def _key(b): ed, sec, num = b.split('|'); return ed, sec, num
CANON = [(cid, *_key(bs[0])) for cid, lk, tier, bs in G]
OTHER = {cid: [_key(b) for b in bs[1:]] for cid, lk, tier, bs in G if bs[1:]}
LK = {cid: lk for cid, lk, tier, bs in G}
TIER = {cid: tier for cid, lk, tier, bs in G}
CROPS = {}
Q = []
for cid, ed, sec, num in CANON:
    x = find(ed, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t)
    yrs = set(ty)
    for (e2, s2, n2) in OTHER.get(cid, []):
        x2 = find(e2, s2, n2); assert x2, (cid, e2, s2, n2)
        yrs |= tag_years(x2['text'])[0]
    short = re.sub(r'^\s*\d{1,2}(\s*-\s*\d{1,2})?\s*[.．]?\s*', '', t.split('\n')[0]).strip()
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': TIER[cid], 'prof': '',
              'src': f'JB {ed}판 · {seclabel(sec)} {num}번', 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True),
              'secy': None, 'tal': bool(re.search(r'\(\s*탈\s*\)|\(\s*\d\d\s*[, ]\s*탈\s*\)', stem_of(t))), 'pick': ''})

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
    q['fig'] = bool(re.search(r'사진|그림|모식도|도해', ' '.join(q['text'].split('\n')[:4])))
for cid, v in ANSAT.items():   # 답 칸 시작 줄(annot에 ans=가 있으면 그대로)
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
        s = P.rd(f'{BASE}{SUB}_20{ed}/{p}.txt'); t += '\n'.join(l for l in s.split('\n') if '무단인쇄' not in l and l.strip()) + '\n'
    return t.strip()
MENT = {'25': ment('25', [1]), '24': ment('24', [1]), '23': ment('23', [1])}   # 판 머리 멘트·수업 표 쪽(p.1)
if __name__ == '__main__':
    used = {}
    for cid, lk, tier, bs in G:
        for b in bs: used.setdefault(b, []).append(cid)
    allk = [f"{ed}|{x['sec']}|{x['num']}" for ed in NPAGES for x in blocks[ed]]
    print('Q', len(Q), '· 블록', len(allk), '· 묶음 안 블록', len(used), '· 못 쓴 블록', [k for k in allk if k not in used], '· 없는 블록', [k for k in used if k not in allk])
    print('두 카드 이상에 든 블록', {k: v for k, v in used.items() if len(v) > 1})
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [(r['ed'], r['sec'], r['num'], r['first'][:25]) for r in LEDGER if r['st'] == 'ref'])
    for ed in NPAGES: print(f' {ed}판', {s_: sum(1 for r in LEDGER if r['ed'] == ed and r['st'] == s_) for s_ in ('card', 'dup', 'ref')})
    if '-v' in sys.argv:
        for q in Q: print(f"{q['id']} {q['lk']:5} {q['tier']} {str(q['yrs']):24} {q['jbtag'][:30]:30} tal={int(q['tal'])} fig={int(q['fig'])} {q['short'][:44]}")
