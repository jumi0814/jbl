import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
"""OMS2 구강악안면외과학 2(4Q) — JB 23·24·25판 → 정식 문항(Q)·같은 문제의 다른 판본(other)·대조표(LEDGER) (2026-11-16 JB 단계 · work/OMS2/jb/R_JB_OMS2.md)
id = 강의 글자 + 번호(강의 안에서 최근 해 먼저 · jb_lock.json이 잠금 — 번호 당기기 금지):
  O Surgical Treatment of OSA(OSA) · P POPA(POPA) · F FACEGIDE(FG — 25 강의 안 함 · 참고) · E 악안면영역의 심미수술 I(AES — 26 양훈주 · 옛 최진영 심미수술 기출 참고)
  R Rhinoplasty 보형물(RHN — 옛 최진영 심미수술 · 26 AES에 없음 · 참고) · S 연조직이식(SOFT) · B 골조직이식(BONE) · T 조직공학(TE) · C 악교정수술의 합병증(CMP — 서병무 · 자료 대기)
  L Loading Protocol(LOAD — 한정준 · 2022 4Q 수업 · 지금은 3Q 범위 · 참고) · MMA(MMA — 25 새 강의)는 기출 없음
묶음 G = (id, 강의 키, tier, [(판, 칸, 번호) …]) — 첫 블록 = 정식(가장 최신 판·가장 최근 칸) · 나머지 = 같은 문제의 다른 판본(OTHER)
  · 같은 문제 = 판 사이 같은 문항(25판 괄호 연도 사슬 · 24판 '(짤)' · '1. 2023 1 번' 가리킴) + 다른 연도 칸의 같은 문제(문제 글·답이 같음 — 23판 2020 칸 S05·C01·C02·O08)
  · 비슷하지만 묻는 것·답이 다른 것은 별개(관련 문항 rel=는 다음 단계 — 짝 목록 보고 3절): O01·O02·O05 · S01·S07·S09 · S02·S08·S10 · B02·B03·B04 · T02·T03·T04 · C04·C05
  · 24판 박주영 2022 '2-2. 2023 2 번' = 2023 2번(STSG 선) 가리킴 → S02 · 그 아래 답·해설(피부 층)은 2-1의 것 → parse가 2-1 블록에 붙임(PTR_ANS_PREV) → S06 (11-16 JBV — 앞 담당은 2-1·2-2 둘 다 S06에 두었음)
  · 23판 심미수술 2020 '2. Rhinoplasty …'(답·참고가 1번 Mandibuloplasty 답을 잘못 복사) = 4번(표 답)과 같은 문제 → R01의 다른 판본
출제연도 = 블록 괄호 연도 ∪ 칸 해 ∪ 같은 문제 다른 판본(괄호·칸) — 두 해 한 칸('2022·2021')·'황순정' 칸은 칸 해를 쓰지 않음(괄호만)"""
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_oms2 as P, subject as S
BASE = J.JBX; SUB = 'OMS2'
NPAGES = P.NPAGES
LECMAP = S.LECMAP

# ---------- 1. JB blocks ----------
blocks = {}
for ed, n in NPAGES.items():
    out = []
    for x in P.parse(ed, n):
        x['text'] = '\n'.join(x['lines']).strip(); out.append(x)
    blocks[ed] = out
ANSRE = re.compile(r'^\s*\[답\]|^\s*답\s*[:：)]|^\s*답\s*$')   # '[답] osteoconduction'·'[답]: …'·'답:' — 23·24판은 '[답] 글'이 같은 줄
def stem_of(t):
    out = []
    for l in t.split('\n'):
        if ANSRE.match(l): break
        out.append(l)
    return ' '.join(out)
NOISE = re.compile(r'(반짤반탈|짤|탈|년도|년|~|’|\')')
def tag_years(text):
    """문항 첫머리(답 이전)의 연도 괄호 전부 — (24,21,20,19) · (2022, 2021) · (2021,2018) · (2019)…(2020) — (짤)·(탈)·(1 개 당 1 점…)·(유사복원)은 연도 아님"""
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
    """칸 해 — '2024-4Q · 최진영'·'최진영 POPA 2023' → 24·23 · 두 해 한 칸 '…2022·2021'·'박주영 황순정' → None(괄호 연도만)"""
    m = re.search(r'(20\d\d)(·20\d\d)?', sec or '')
    return int(m.group(1)) % 100 if m and not m.group(2) else None
def seclabel(sec): return f'{sec} 칸'

# ---------- 2. canonical questions ----------
# 강의별 담당 — 26 자료가 온 강의(AES) = 26 담당 · 나머지 = 25 담당(25 임시본 · RULES 14 b) · 자료 없는 키 = JB 칸 교수
LK_PROF = {'OSA': '최진영', 'MMA': '최진영', 'POPA': '최진영', 'FG': '최진영', 'AES': '양훈주', 'RHN': '최진영',
           'SOFT': '박주영', 'BONE': '박주영', 'TE': '박주영', 'CMP': '서병무', 'LOAD': '한정준'}
C24, C23, C22 = '2024-4Q · 최진영', '2023-4Q · 최진영', '2022-4Q · 최진영'
J24, J23, J22 = '2024-4Q · 박주영', '2023-4Q · 박주영', '2022-4Q · 박주영'
B24, B22 = '2024-4Q · 서병무', '2022-4Q · 서병무'
G = [
    # ---- O Surgical Treatment of OSA(최진영 · 25 251103 자료)
    ('O01', 'OSA', 'A', [('25', C24, '1')]),                                   # 수면무호흡의 정의 (24)
    ('O02', 'OSA', 'A', [('25', C24, '1(유사복원)')]),                          # (유사복원) 수면무호흡 진단기준 넘버링 (24) — 멘트 '최진영 9 문항'에 셈 · 관련 O01·O05
    ('O03', 'OSA', 'A', [('25', C24, '2'), ('24', '최진영 OSA 2021', '1'), ('23', '최진영 OSA 2021', '1')]),   # 방치 시 문제점 = OSA 치료해야 하는 이유 (24,21,20,19)
    ('O04', 'OSA', 'A', [('25', C24, '3'), ('24', '최진영 OSA 2023', '2'), ('24', '최진영 OSA 2021', '2'), ('23', '최진영 OSA 2021', '2')]),   # 수술적 치료 나열 (24,23,21)·(2021,2018)
    ('O05', 'OSA', 'A', [('25', C23, '9'), ('24', '최진영 OSA 2023', '3')]),   # OSA 증상 (23) — 25판 답 = 진단기준 / 24판 답 = Hypersomnolence 등(p.4)
    ('O06', 'OSA', 'A', [('25', C23, '10'), ('24', '최진영 OSA 2023', '1')]),  # MMA 적응증 (23)
    ('O07', 'OSA', 'A', [('25', C22, '14'), ('24', '최진영 OSA 2022', '1'), ('23', '최진영 OSA 2022', '1')]),   # surgical vs medical 고려 요소 표 (22)
    ('O08', 'OSA', 'A', [('25', C22, '15'), ('24', '최진영 OSA 2022', '2'), ('23', '최진영 OSA 2022', '2'), ('23', '최진영 OSA 2020', '2')]),   # phased surgical protocol (22,20)
    ('O09', 'OSA', 'A', [('23', '최진영 OSA 2020', '1')]),                     # UPPP 합병증 (2019) · rationale·indication (2020)
    ('O10', 'OSA', 'A', [('23', '최진영 OSA 2020', '3')]),                     # Fugita's classification (2018) — 2020 칸(보고 5절)
    # ---- P New Paradigm in the treatment of dentofacial deformity: POPA(최진영 · 25 251117 자료 · 21년 첫 강의)
    ('P01', 'POPA', 'A', [('25', C24, '4'), ('24', '최진영 POPA 2023', '1'), ('24', '최진영 POPA 2022', '1'), ('24', '최진영 POPA 2021', '1'),
                          ('23', '최진영 POPA 2022', '1'), ('23', '최진영 POPA 2021', '1')]),   # 전통적 턱교정수술 단점 (24,23,22,21)
    ('P02', 'POPA', 'A', [('25', C24, '5'), ('24', '최진영 POPA 2023', '2')]),   # 선수술 가능해진 이유(+장점) (24,23)
    ('P03', 'POPA', 'A', [('25', C24, '6'), ('24', '최진영 POPA 2023', '4')]),   # 환자중심적·생리적 이유 (24,23)
    ('P04', 'POPA', 'A', [('25', C23, '11'), ('24', '최진영 POPA 2023', '3'), ('24', '최진영 POPA 2021', '2'), ('23', '최진영 POPA 2021', '2')]),   # SFA concept (23,21)
    # ---- F FACEGIDE(최진영 · 21~24 강의 · 25 강의 안 함 — 25판 "문제는 참고용으로 남겨두었습니다")
    ('F01', 'FG', 'C', [('25', C24, '7'), ('24', '최진영 FACEGIDE 2023', '2')]),   # Class 2 CAD/CAM 모의수술·맞춤 고정판 장점 (24,23)
    ('F02', 'FG', 'C', [('25', C24, '8'), ('24', '최진영 FACEGIDE 2023', '3'), ('24', '최진영 FACEGIDE 2022·2021', '1'), ('23', '최진영 FACEGIDE 2022·2021', '1')]),   # CAD/CAM vs conventional 장점 (24,23,22,21)
    ('F03', 'FG', 'C', [('25', C23, '12'), ('24', '최진영 FACEGIDE 2023', '1')]),   # condylar sag (23)
    ('F04', 'FG', 'C', [('25', C23, '13'), ('24', '최진영 FACEGIDE 2022·2021', '2'), ('23', '최진영 FACEGIDE 2022·2021', '2')]),   # custom-made facial implant 차이 (23,22)·(2022)
    # ---- E 악안면영역의 심미수술 I(26 양훈주 261109 — Genioplasty·Mandibuloplasty·Malarplasty) ← 23판 '[참고: 악안면영역 심미수술 (21,22,23 년도 강의 안하심)]' 옛 최진영 기출
    ('E01', 'AES', 'C', [('23', '최진영 심미수술 2020', '1')]),   # Mandibuloplasty 합병증 (2020, 2013) — 26 AES p.20 '합병증' 목록
    ('E02', 'AES', 'C', [('23', '최진영 심미수술 2020', '3')]),   # Malarplasty 절개법·장점 (2020, 2019)
    # ---- R Rhinoplasty(옛 최진영 심미수술 — 26 AES 목차(p.2·40)에 없음)
    ('R01', 'RHN', 'C', [('23', '최진영 심미수술 2020', '4'), ('23', '최진영 심미수술 2020', '2')]),   # silicone vs goretex 장단점 — 2번 = 같은 문제(답 잘못 복사)
    # ---- S 연조직이식 — 피부/점막이식(박주영 · 25 251124 자료 — 25판이 '골조직이식 p.10·12'로 단 S04·S05 = 골조직이식 첫머리 '지난 시간 REVIEW QUIZ' · 연조직이식 p.32·33에 같은 슬라이드)
    ('S01', 'SOFT', 'A', [('25', J24, '3')]),                                  # 옳은 것 모두(생착·이종/동종·점막이식) (24)
    ('S02', 'SOFT', 'A', [('25', J24, '4'), ('24', '박주영 2023', '2'), ('24', '박주영 2022', '2-2'), ('23', '박주영 2022', '2-2')]),   # STSG·FTSG 나누는 선 (24,23,22) — 24판 2022 '2-2. 2023 2 번' 가리킴(11-16 JBV)
    ('S03', 'SOFT', 'A', [('25', J24, '5'), ('24', '박주영 2022', '3'), ('23', '박주영 2022', '3')]),     # tie-over dressing 이름·목적 (24,22)
    ('S04', 'SOFT', 'A', [('25', J23, '6'), ('24', '박주영 2023', '1')]),                                # 피부이식 생착기전 날짜별 (23)
    ('S05', 'SOFT', 'A', [('25', J22, '8'), ('24', '박주영 2022', '1'), ('23', '박주영 2022', '1'), ('23', '박주영 2020', '1')]),   # 수혜부 성공조건 (22) + 23판 2020 칸 같은 문제
    ('S06', 'SOFT', 'A', [('25', J22, '9'), ('24', '박주영 2022', '2-1'), ('23', '박주영 2022', '2-1')]),   # 피지샘·모근·땀샘 그림 객관식 (22) — 24판 2-1 블록에 그 아래 답·해설(parse PTR_ANS_PREV — 11-16 JBV)
    ('S07', 'SOFT', 'A', [('24', '박주영 2021', '1'), ('23', '박주영 2021', '1')]),   # 옳은 선지(생착 정의 · 틀린 선지 '3-5일이면 혈행 완성') (2021,2020)
    ('S08', 'SOFT', 'A', [('24', '박주영 2021', '4'), ('23', '박주영 2021', '4')]),   # 그림 주고 FTSG 부위 고르기 (2021,2020)
    ('S09', 'SOFT', 'B', [('23', '박주영 황순정', '1')]),   # 황순정 ★★★ 생착 정의·기전 (2018,2016,2013)
    ('S10', 'SOFT', 'B', [('23', '박주영 황순정', '2')]),   # 황순정 ★★★ 두께 분류 (2018,2016,2013)
    # ---- B 구강악안면골이식(박주영 · 25 251201 자료)
    ('B01', 'BONE', 'A', [('25', J24, '1'), ('24', '박주영 2023', '3')]),     # 구내 골 채취부위 그림 ①~④ (24,23)
    ('B02', 'BONE', 'A', [('25', J22, '10'), ('24', '박주영 2022', '4'), ('23', '박주영 2022', '4')]),   # 유리자가골 구외/구내 공여부 표 빈칸 (22)
    ('B03', 'BONE', 'A', [('24', '박주영 2021', '3'), ('23', '박주영 2021', '3')]),   # 구외/구내 공여부 중 가장 채취량 많은 곳 (2021,2019)
    ('B04', 'BONE', 'A', [('23', '박주영 2019', '1')]),                         # Intraoral donor site 중 가장 cortical bone 많은 곳 (2019 칸)
    # ---- T 구강악안면조직공학 및 조직공학을 이용한 골이식(박주영 · 25 251208 자료)
    ('T01', 'TE', 'A', [('25', J24, '2'), ('24', '박주영 2023', '4')]),       # osteoconduction 정의 고르기 (24,23)
    ('T02', 'TE', 'A', [('25', J23, '7'), ('24', '박주영 2023', '5')]),       # PRF 사진 — 이름·활용·효과 (23)
    ('T03', 'TE', 'A', [('24', '박주영 2021', '2'), ('23', '박주영 2021', '2')]),   # PRF 맞는 것 (2021,2020)
    ('T04', 'TE', 'A', [('23', '박주영 2019', '2')]),                         # PRP 특징 객관식(보기·답 미복원 — 해설만) (2019 칸)
    # ---- C Complications with Orthognathic Surgery(서병무 · 25 수업 12/15(예정) · 자료 없음)
    ('C01', 'CMP', 'A', [('25', B24, '1'), ('24', '서병무 합병증 2023', '1'), ('23', '서병무 합병증 2022', '3(추가복원)'), ('23', '서병무 합병증 2020', '1')]),   # 술 중 합병증 나열 (24,23) + 22 추가복원·2020
    ('C02', 'CMP', 'A', [('25', B24, '2'), ('24', '서병무 합병증 2023', '2'), ('24', '서병무 합병증 2022', '3'), ('23', '서병무 합병증 2022', '3'),
                         ('23', '서병무 합병증 2020', '2')]),   # routine aftermath 나열 (24,23,22) + 2020
    ('C03', 'CMP', 'A', [('25', B22, '3'), ('24', '서병무 합병증 2022', '1'), ('23', '서병무 합병증 2022', '1')]),   # 잘 손상되는 신경과 이유 (22)
    ('C04', 'CMP', 'A', [('25', B22, '4'), ('24', '서병무 합병증 2022', '2'), ('23', '서병무 합병증 2022', '2')]),   # 출혈 지속에도 골삭제를 빠르게 하는 이유 (22)
    ('C05', 'CMP', 'A', [('24', '서병무 합병증 2021', '1'), ('23', '서병무 합병증 2021', '1')]),   # 예상치 못한 출혈과 처치법 (2021 칸)
    # ---- L Loading Protocol(한정준 · 23판 '<IV> 한정준 교수님 Part' — 2022 4Q 수업 · 24판 멘트 '2023: … 6 문제는 pf.한정준 3Q 내용으로 생략')
    ('L01', 'LOAD', 'C', [('23', '한정준 Loading 2022', '1')]),   # Immediate occlusal loading 장점
    ('L02', 'LOAD', 'C', [('23', '한정준 Loading 2022', '2')]),   # 즉시하중 골유착·초기 안정성 요소
]
CANON = [(cid, *toks[0]) for cid, lk, tier, toks in G]
OTHER = {cid: toks[1:] for cid, lk, tier, toks in G if len(toks) > 1}
LK = {cid: lk for cid, lk, tier, toks in G}
TIER = {cid: tier for cid, lk, tier, toks in G}
CROPS = {}   # JB 그림 조각(tools/jbfig.py → jb_crops.json)은 다음 단계 JF — 그림 문항 표 = 보고 3절
FIG = {'B01', 'S02', 'S03', 'S06', 'S08', 'T02'}   # 시험에 그림·사진이 주어진 문항(S08은 JB에 답 표시 그림만 — 답 쪽) · O07·O08·O03 그림·표는 답·해설 쪽(그림 문항 아님)
def _short(t):
    for l in t.split('\n'):
        s = re.sub(r'^\s*\d{1,2}(?:-\d)?\s*[.．]\s*', '', l).strip()
        s = re.sub(r'^\s*(추가복원\s*[:：]?|\(유사복원\))\s*', '', s).strip()
        if s: return s
    return ''
Q = []
for cid, ed, sec, num in CANON:
    x = find(ed, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t)
    yrs = set(ty) | ({secyear(sec)} if secyear(sec) else set())
    for (e2, s2, n2) in OTHER.get(cid, []):
        x2 = find(e2, s2, n2); assert x2, (cid, e2, s2, n2)
        if secyear(s2): yrs.add(secyear(s2))
        yrs |= tag_years(x2['text'])[0]
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': TIER[cid], 'prof': '',
              'src': f'JB {ed}판 · {seclabel(sec)} {num}번', 'short': _short(t)[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True),
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
        s = P.rd(f'{BASE}{SUB}_20{ed}/{p}.txt'); t += '\n'.join(l for l in s.split('\n') if '무단인쇄' not in l and l.strip() and l.strip() != 'ㅗ') + '\n'
    return t.strip()
MENT = {'25': ment('25', [1]), '24': ment('24', [1]), '23': ment('23', [1, 2, 3])}   # 판 머리 멘트·수업 표 쪽(23판은 1~3쪽 — '21 년 이전' 학번별 코멘트·2023 수업 표)
if __name__ == '__main__':
    used = {}
    for cid, lk, tier, toks in G:
        for b in toks: used.setdefault('|'.join(b), []).append(cid)
    allk = [f"{ed}|{x['sec']}|{x['num']}" for ed in NPAGES for x in blocks[ed]]
    print('Q', len(Q), '· 블록', len(allk), '· 묶음 안 블록', len(used), '· 못 쓴 블록', [k for k in allk if k not in used], '· 없는 블록', [k for k in used if k not in allk])
    print('두 카드 이상에 든 블록', {k: v for k, v in used.items() if len(v) > 1})
    print('ids 겹침', [c for c in LK if [g[0] for g in G].count(c) > 1], '· 카드 수', len(G), len(set(LK)))
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [(r['ed'], r['sec'], r['num'], r['first'][:25]) for r in LEDGER if r['st'] == 'ref'])
    for ed in NPAGES: print(f' {ed}판', {s_: sum(1 for r in LEDGER if r['ed'] == ed and r['st'] == s_) for s_ in ('card', 'dup', 'ref')})
    if '-v' in sys.argv:
        for q in Q: print(f"{q['id']} {q['lk']:5} {q['tier']} {str(q['yrs']):26} {q['jbtag'][:34]:34} {q['short'][:44]}")
