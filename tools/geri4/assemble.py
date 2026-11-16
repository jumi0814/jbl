import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
"""GERI4 노인치과학(4Q) — JB 23·24·25판 → 정식 문항(Q)·같은 문제의 다른 판본(other)·대조표(LEDGER) (2026-11-16 JB 단계 · work/GERI4/jb/R_JB_GERI4.md)
id = 강의 글자 + 번호(강의 안에서 최근 해 먼저 · jb_lock.json이 잠금 — 번호 당기기 금지):
  B 노화의 생물학(BIO 이재일) · S 전신질환과 치주질환(SYS 조영단) · L 같은 강의 전임 류인철 출제(SYS · tier B) · P 노인환자의 치주치료(PER 이용무)
  D 노인 무치악 환자의 보철 치료(DEN 임영준) · R 노인환자의 보철치료(PRO 곽재영) · M 노인성 외과 질환(OMF 명훈 — 과거 외과 모음) · C 노인환자의 외과적 치료시 고려사항(OSC 김성민)
  Z 미복원·'중복복원'(무엇의 중복인지 없음)·'복원 오류' 자리(build4가 숨김 — 기출 대장에만)
묶음 G = (id, 강의 키, tier, [블록 '판|칸|번호' …]) — 첫 블록 = 정식(가장 최신 판 · 같은 판이면 가장 최근 칸 · 가리킴 줄이 아닌 것), 나머지 = 같은 문제의 다른 판본(OTHER)
  · 판 사이 같은 문제 = 문제 글이 같거나 JB가 같은 문제라고 적은 것(괄호 연도 사슬 '(24-21,19)'·'(24-22)' · '8번 중복복원' · '21년도 n번과 동일' · 25판이 외과 모음을 빼며 칸 문항에 넘긴 것)
  · 비슷하지만 묻는 것·답이 다른 것은 별개(관련 문항 rel=은 다음 단계 annot — 짝 목록은 보고 3절): T/F 묶음(P07) ↔ 낱문항 T/F(P11·P13·P14·P15) · high·low VD(R05) ↔ 교합고경 높을 때(R06) ↔ VD 높을 때(D04) …"""
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_geri4 as P, subject as S
BASE = J.JBX; SUB = 'GERI4'
NPAGES = dict(P.NP)   # 판 → 쪽 수 {'25': 18, '24': 20, '23': 19}
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
NOISE = r"(\d\d\s*강조\w*|반짤반탈|짤|탈|객관식|객|단답형|단답|서술형|서술|T\s*/\s*F|TF|교과서 문장|이\s*전|년도|년|’|‘|'|`|~)"   # '25강조'·'25 강조'·'25강조idfd' = 2025 수업 강조(출제 해 아님 — 통째로 뺌) · '이 전' = 줄바꿈으로 갈린 '이전'(25판 25번 '(24-21, 이\n전)')
def tag_years(text):
    """문항 첫머리(답 이전)의 연도 괄호 전부 — (24 탈) · (객, 24 탈) · (24탈, 단답) · (22,24) · (24-21,19) · (24-21, 이전) · (24-22, 25강조) · (23-19) · (17)
    'a-b' = 범위(25판 — 24판 괄호 + 칸 해를 이은 것: (24-21,19) = 24·23·22·21·19) · '이전' = 해 없음 · 'NN강조' = 수업 강조(뺌) · (5점)·(T/F)·( ) = 연도 아님"""
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = re.sub(NOISE, ' ', g).replace('，', ',').strip(' ,')   # '(객, 24 탈)' → '24'
        if not re.search(r'\d', g2) or not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*-\s*(20\d\d|\d\d))?(\s*,\s*((20\d\d|\d\d)(\s*-\s*(20\d\d|\d\d))?)?)*\s*,?\s*', g2): continue
        vs = set()
        for tok in g2.split(','):
            nums = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', tok)]
            if len(nums) == 2: vs |= set(range(min(nums), max(nums) + 1))
            else: vs |= set(nums)
        if not vs or not all(9 <= v <= 26 for v in vs): continue
        ys |= vs; raw.append('(' + g.strip() + ')')
    return ys, raw
def secyear(sec): m = re.fullmatch(r'(20\d\d)', sec or ''); return int(m.group(1)) % 100 if m else None
def seclabel(sec, prof=''):
    if secyear(sec): return f'{sec}년 칸 · {prof}' if prof else f'{sec}년 칸'
    return f'과거 외과 모음 · {sec.split("·")[-1]}'
BMAP = {}
for ed in NPAGES:
    for x in blocks[ed]:
        k_ = (ed, x['sec'], str(x['num'])); assert k_ not in BMAP, k_; BMAP[k_] = x
def find(ed, sec, num):
    return BMAP.get((ed, str(sec), str(num)))

# ---------- 2. canonical questions ----------
# 강의별 담당(26 담당 · 26 자료가 없는 강의는 25 담당 — RULES 13 10-26 'LK_PROF = 26 담당')
LK_PROF = {'SYS': '조영단', 'PER': '이용무', 'BIO': '이재일', 'DEN': '임영준', 'PRO': '곽재영', 'OMF': '명훈', 'OSC': '김성민'}
QPROF = {f'L{i:02d}': '류인철' for i in range(1, 5)}   # 전임 교수 문항(강의 연결 교수와 다름 — 3Q GERI 조현재 꼴)
KC, KM = '외과모음·김성민', '외과모음·명훈'
G = [
    # ---- B 노화의 생물학(이재일) — 25판 2024 칸만("작년에 처음 출제되어서 1개년 기출밖에 없습니다")
    ('B01', 'BIO', 'A', ['25|2024|1']), ('B02', 'BIO', 'A', ['25|2024|2']), ('B03', 'BIO', 'A', ['25|2024|3']), ('B04', 'BIO', 'A', ['25|2024|4']),
    ('B05', 'BIO', 'A', ['25|2024|5']), ('B06', 'BIO', 'A', ['25|2024|6']), ('B07', 'BIO', 'A', ['25|2024|8']), ('B08', 'BIO', 'A', ['25|2024|10']),
    # ---- S 전신질환과 치주질환(조영단 — 22년부터)
    ('S01', 'SYS', 'A', ['25|2024|11']),
    ('S02', 'SYS', 'A', ['25|2024|13', '24|2022|3', '23|2022|3']),   # Epigenetics '(22,24)' — 24·23판 2022 칸 3번
    ('S03', 'SYS', 'A', ['25|2024|14']),
    ('S04', 'SYS', 'A', ['25|2023|1', '24|2023|3']), ('S05', 'SYS', 'A', ['25|2023|2', '24|2023|4']), ('S06', 'SYS', 'A', ['25|2023|3', '24|2023|5']),
    ('S07', 'SYS', 'A', ['25|2022|1', '24|2022|1', '23|2022|1']), ('S08', 'SYS', 'A', ['25|2022|2', '24|2022|2', '23|2022|2']),
    # ---- L 같은 강의 전임 류인철(21·20 칸 '<류인철 pf>') — tier B
    ('L01', 'SYS', 'B', ['24|2021|1', '23|2021|1']), ('L02', 'SYS', 'B', ['24|2021|2', '23|2021|2']),   # L02 경화상아질 — JB 해설 "답안은 3Q 범위에 해당합니다"(3Q GERI HARD)
    ('L03', 'SYS', 'B', ['24|2021|3', '23|2021|3']), ('L04', 'SYS', 'B', ['23|2020|7']),
    # ---- P 노인환자의 치주치료(이용무)
    ('P01', 'PER', 'A', ['25|2024|15']), ('P02', 'PER', 'A', ['25|2024|17']), ('P03', 'PER', 'A', ['25|2024|18']), ('P04', 'PER', 'A', ['25|2024|19']), ('P05', 'PER', 'A', ['25|2024|20']),
    ('P06', 'PER', 'A', ['25|2024|21', '24|2023|11', '24|2022|12', '24|2021|11', '23|2022|12', '23|2021|11', '23|2020|6']),   # 전반적 주의사항 '(24-21,19)' · 23판 20 칸 '<류인철 pf> 6. 21년도 11번과 동일'(보고 5절)
    ('P07', 'PER', 'A', ['25|2023|4', '24|2023|6']),   # T/F 6문장 묶음(보기 끝 괄호 (23,22)·(23-19))
    ('P08', 'PER', 'A', ['25|2022|3', '24|2022|4', '23|2022|4', '24|2021|8', '23|2021|8']),   # 골융합 임플란트 성공률 (22,21,20,19)
    ('P09', 'PER', 'A', ['25|2022|4', '24|2022|5', '23|2022|5']), ('P10', 'PER', 'A', ['25|2022|5', '24|2022|6', '23|2022|6']),
    ('P11', 'PER', 'A', ['25|2022|6', '24|2022|8', '23|2022|8', '24|2021|4', '23|2021|4', '23|2020|2']),   # 20대 이후 치은염·치주염 유병율 · 20 칸 '21년도 4번과 동일'
    ('P12', 'PER', 'A', ['25|2022|7', '24|2022|9', '23|2022|9', '23|2020|1']),   # 백악질 두께 감소 · 20 칸 1번 '(중복: 나이에 따라 치아 맹출하면서 백악질이 줄어든다)'
    ('P13', 'PER', 'A', ['24|2023|8', '24|2023|9', '24|2022|7', '23|2022|7', '24|2021|6', '23|2021|6', '23|2020|4']),   # 노화 > 흡연 위험요소(낱문항) · '9. 8번 중복복원' · 20 칸 '21년도 6번과 동일'
    ('P14', 'PER', 'A', ['24|2023|10', '24|2022|10', '23|2022|10']), ('P15', 'PER', 'A', ['24|2022|11', '23|2022|11', '24|2021|7', '23|2021|7']),
    ('P16', 'PER', 'A', ['24|2021|5', '23|2021|5', '23|2020|3']),   # 결합조직 섬유성분 · 20 칸 '21년도 5번과 동일'
    ('P17', 'PER', 'A', ['24|2021|10', '23|2021|10']), ('P18', 'PER', 'A', ['23|2020|5']),
    # ---- D 노인 무치악 환자의 보철 치료(임영준)
    ('D01', 'DEN', 'A', ['25|2024|22']), ('D02', 'DEN', 'A', ['25|2024|24']),
    ('D03', 'DEN', 'A', ['25|2022|8', '24|2022|16', '23|2022|16']),
    ('D04', 'DEN', 'A', ['25|2022|9', '24|2022|17', '23|2022|17', '24|2021|14', '23|2021|14']),   # VD 높을 때 (22,21)
    ('D05', 'DEN', 'A', ['24|2021|15', '23|2021|15']), ('D06', 'DEN', 'A', ['23|2020|14']),
    # ---- R 노인환자의 보철치료(곽재영)
    ('R01', 'PRO', 'A', ['25|2024|25', '24|2023|16', '24|2022|14', '23|2022|14']),   # Willis gauge 설명(·도해·목적) '(24-21, 이전)'
    ('R02', 'PRO', 'A', ['25|2024|26', '24|2022|14-1', '23|2022|14-1', '24|2021|12', '23|2021|12', '23|2020|11']),   # Willis gauge 측정부위·방법·목적 · 20 칸 '21년도 12번과 동일'
    ('R03', 'PRO', 'A', ['25|2024|27', '24|2023|17', '24|2022|15', '23|2022|15', '23|2020|10']),   # VD 측정(확인) 방법 5가지
    ('R04', 'PRO', 'A', ['25|2024|28']),
    ('R05', 'PRO', 'A', ['25|2023|5', '24|2023|15']),   # high VD와 low VD (23,20)
    ('R06', 'PRO', 'A', ['24|2021|14-1', '23|2021|14-1', '23|2022|17-1', '23|2020|9']),   # 교합고경 높을 때 (20) — 21·22 칸 임영준 해설 "아래에 곽재영 교수님 문제를 가져왔습니다"
    ('R07', 'PRO', 'A', ['23|2020|12']), ('R08', 'PRO', 'A', ['23|2020|13']),
    # ---- M 노인성 외과 질환(명훈) — 24·23판 과거 외과 모음(25판에서 뺌 — 멘트 "명훈 교수님께서 4년간 문제 출제하시지 않으시고")
    ('M01', 'OMF', 'A', ['24|' + KM + '|1', '23|' + KM + '|1']), ('M02', 'OMF', 'A', ['24|' + KM + '|2', '23|' + KM + '|2']), ('M03', 'OMF', 'A', ['24|' + KM + '|3', '23|' + KM + '|3']),
    ('M04', 'OMF', 'A', ['24|' + KM + '|4', '23|' + KM + '|4']), ('M05', 'OMF', 'A', ['24|' + KM + '|5', '23|' + KM + '|5']), ('M06', 'OMF', 'A', ['24|' + KM + '|6', '23|' + KM + '|6']),
    # ---- C 노인환자의 외과적 치료시 고려사항(김성민)
    ('C01', 'OSC', 'A', ['25|2024|29', '24|2023|21-1', '24|2022|19', '23|2022|19']),   # 신장 투석 환자 발치·즉시 임플란트 '(24-22)'(65세·신장이식 예정 ← 78세 — 이전 출제 꼴)
    ('C02', 'OSC', 'A', ['25|2024|30', '24|2023|22', '24|2022|18', '23|2022|18', '24|2021|17', '23|2021|17', '23|2020|15', '24|' + KC + '|3', '23|' + KC + '|3']),   # 공존이환(Comorbidity) — 괄호 사슬 (21,18,17,14,12,11) · 25판이 외과 모음을 빼며 칸 문항으로 넘김
    ('C03', 'OSC', 'A', ['25|2023|6', '24|2023|21', '24|2021|16', '23|2021|16', '24|' + KC + '|2', '23|' + KC + '|2']),   # 노인의 신장 변화 (23,21,18,17,14,11)
    ('C04', 'OSC', 'A', ['24|' + KC + '|1', '23|' + KC + '|1']),   # 뇌세포 및 신경화학적 변화 (17) — 25판 멘트 "김성민 교수님께서 17년도에만 출제하신 1문제"
    # ---- Z 미복원·자리(build4 숨김 — 기출 대장 '미복원')
    ('Z01', 'BIO', 'A', ['25|2024|7']), ('Z02', 'BIO', 'A', ['25|2024|9']), ('Z03', 'SYS', 'A', ['25|2024|12']), ('Z04', 'PER', 'A', ['25|2024|16']), ('Z05', 'DEN', 'A', ['25|2024|23']),
    ('Z06', 'SYS', 'A', ['24|2023|1']), ('Z07', 'SYS', 'A', ['24|2023|2']), ('Z08', 'PER', 'A', ['24|2023|7']), ('Z09', 'PER', 'A', ['24|2023|12']), ('Z10', 'PER', 'A', ['24|2023|13']),
    ('Z11', 'PER', 'A', ['24|2023|14']), ('Z12', 'PRO', 'A', ['24|2023|18']), ('Z13', 'PRO', 'A', ['24|2023|19']), ('Z14', 'PRO', 'A', ['24|2023|20']),
    ('Z15', 'PRO', 'A', ['24|2022|13', '23|2022|13']),   # '13. 복원 오류'
    ('Z16', 'PER', 'A', ['24|2021|9', '23|2021|9']),     # '9. 중복복원'(무엇의 중복인지 없음)
    ('Z17', 'PRO', 'A', ['24|2021|13', '23|2021|13']),   # '13. 중복 복원'(〃)
]
HIDE = {'Z15', 'Z16', 'Z17'}   # '복원 오류'·'중복복원' — build4 미복원 규칙(_HIDE)에 안 걸려 hide=1을 넣어 줌(어느 문항의 중복인지 JB에 없음)
FIGQ = {'R01', 'D05'}   # 그림 문항(R01 Willis gauge 도해 — 25판 p.9 답 쪽 사진 · D05 Top five critical areas 슬라이드 빈칸 — 24판 p.15·23판 p.12 답 쪽 그림) — 그림 조각은 다음 단계(보고 3절)
def _key(b): ed, sec, num = b.split('|'); return ed, sec, num
CANON = [(cid, *_key(bs[0])) for cid, lk, tier, bs in G]
OTHER = {cid: [_key(b) for b in bs[1:]] for cid, lk, tier, bs in G if bs[1:]}
LK = {cid: lk for cid, lk, tier, bs in G}
TIER = {cid: tier for cid, lk, tier, bs in G}
_used = {}
for cid, lk, tier, bs in G:
    for b in bs:
        k_ = _key(b); assert k_ in BMAP, ('없는 블록', cid, b); assert k_ not in _used, ('두 번 쓴 블록', cid, b, _used[k_]); _used[k_] = cid
assert len({c for c, *_ in CANON}) == len(CANON), '같은 id 두 번'
def blk_years(ed, sec, x):
    """블록 하나의 출제 해 = 괄호 해 ∪ 실린 칸 해 — 딸린 블록 'N-1'에 제 괄호가 있으면(24판 22 칸 14-1 '(21,20)' · 21 칸 14-1 '(20)' — 해설에 붙인 옛 JB 문항) 제 괄호 해만"""
    ty = tag_years(x['text'])[0]
    if x.get('sub') and ty: return set(ty)
    return set(ty) | ({secyear(sec)} if secyear(sec) else set())
CROPS = {}
Q = []
for cid, ed, sec, num in CANON:
    x = find(ed, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t)
    yrs = blk_years(ed, sec, x)
    for (e2, s2, n2) in OTHER.get(cid, []):
        yrs |= blk_years(e2, s2, find(e2, s2, n2))
    short = re.sub(r'^★?\s*\d{1,2}(\s*-\s*\d{1,2})?\s*[.．]?\s*', '', t.split('\n')[0]).strip()
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': TIER[cid], 'prof': QPROF.get(cid, LK_PROF[LK[cid]]),
              'src': f'JB {ed}판 · {seclabel(sec, x["prof"])} {num}번', 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True),
              'secy': secyear(sec), 'tal': bool(re.search(r'\([^()]*\d\d\s*탈[^()]*\)|\(\s*탈[^()]*\)', stem_of(t))), 'pick': ''})

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
        q.update({'v': a['v'], 'yrsnote': a['yrsnote'], 'rel': a['rel'], 'pair': a['pair'], 'A': a['A'], 'M': a['M'], 'N': a['N'], 'K': a.get('K', []), 'lk': lk_ or LK[q['id']]})
        q['yrs'] = sorted(set(q['base']) | set(a['yrs']), reverse=True); q['xtra'] = sorted(set(a['yrs']) - set(q['base']), reverse=True)
        if a.get('prof'): q['prof'] = a['prof']
    else:
        q.update({'v': 'na', 'yrsnote': '', 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': [], 'K': [], 'lk': LK[q['id']], 'xtra': []}); q['yrs'] = sorted(q['base'], reverse=True)
    o = []
    for (e2, s2, n2) in OTHER.get(q['id'], []):
        x2 = find(e2, s2, n2); o.append({'ed': e2, 'sec': s2, 'num': n2, 'pg': x2['pg'], 'pg2': x2['pg2'], 'text': x2['text']})
    q['other'] = o; q['lab24'] = ''; q['crops'] = CROPS.get(q['id'], {})
    q['fig'] = q['id'] in FIGQ
for cid in HIDE:   # 자리 줄(복원 오류·중복복원) — annot에 hide=0을 적으면 그대로 보임
    ANN.setdefault(cid, {}).setdefault('hide', '1')

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
    dj = P.jbdir(ed)
    man = json.load(open(f'{dj}/manifest.json'))
    vis = {p['page_number'] for p in man['pages'] if p.get('has_visual_content')}
    for i in range(1, n + 1):
        if not os.path.exists(f'{dj}/{i}.jpeg'):   # JB 쪽 이미지가 없는 환경(클라우드 세션) — 지금 docs/packs의 쪽 이미지를 그대로(tools/jblpaths.prev_jb_pages)
            IMG['jb'][f'{ed}-{i}'] = J.prev_jb_pages(SUB)[f'{ed}-{i}']; continue
        im = Image.open(f'{dj}/{i}.jpeg').convert('RGB')
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
        LEDGER.append({'ed': ed, 'sec': (x['sec'] + '년') if secyear(x['sec']) else x['sec'], 'num': x['num'], 'pg': x['pg'], 'first': first, 'st': st, 'to': to})
def ment(ed, pages):
    t = ''
    for p in pages:
        s = P.rd(f'{P.jbdir(ed)}/{p}.txt'); t += '\n'.join(l for l in s.split('\n') if '무단인쇄' not in l and l.strip()) + '\n'
    return t.strip()
MENT = {ed: ment(ed, [1, 2]) for ed in NPAGES}   # 판 머리 멘트(p.1) + 수업 표(p.2)
if __name__ == '__main__':
    print('Q', len(Q), '블록', sum(len(b) for b in blocks.values()), '숨김 자리 Z', sum(1 for q in Q if q['id'].startswith('Z')))
    for q in Q: print(q['id'], q['tier'], q['lk'], q['prof'], q['yrs'], q['jbtag'], '|', q['short'][:40], '| other', len(q['other']))
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [(r['ed'], r['sec'], r['num'], r['first'][:28]) for r in LEDGER if r['st'] == 'ref'])
    for e_ in NPAGES: print(f'{e_}판 블록', len(blocks[e_]), {s_: sum(1 for r in LEDGER if r['ed'] == e_ and r['st'] == s_) for s_ in ('card', 'dup', 'ref')})
