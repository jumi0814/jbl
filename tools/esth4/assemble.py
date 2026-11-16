import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
"""ESTH4 4Q 심미치과학 — JB 23·24·25판 → 정식 문항(Q)·같은 문제의 다른 판본(other)·대조표(LEDGER) (2026-11-16 JB 단계 · 보고 work/ESTH4/jb/R_JB_ESTH4.md)
id = 강의 글자 + 번호(강의 안에서 최근 해 먼저 · 같은 해는 JB 번호 순 · jb_lock.json이 잠금 — 번호 당기기 금지):
  C 심미수복재료–도재(CER — 조준호 · 22년까지 한중석) · R Resin bonded(RBR — 25 여인성 · 23·24 이재현 출제) · K CAD,CAM(CAD — 25 새 강의 윤형인 · 21 한중석 문항)
  D 디지털 기술의 활용(DIG — 최순영) · P 가철성 보철물(RPD — 곽재영) · G 심미적 치주치료(PER — 이용무) · S Esthetic smile(SMI — 백승학)
  L Laminate(LAM — 이창하 22년 · 올해 4Q 강의 없음 · tier C) · Z 25판 2024 칸 '미복원' 자리(build4가 숨김 — 기출 대장에만)
묶음 G = (id, 강의 키, tier, ['판|칸 해|번호' …]) — 첫 블록 = 정식(가장 최신 판 · 같은 판이면 가장 최근 해 칸 · 가리킴 줄 아닌 것), 나머지 = 같은 문제의 다른 판본(OTHER)
  · 같은 문제 = 문제 글·답이 같은 것 + JB가 같다고 적은 것(25판 괄호 연도 사슬 · 25판 가리킴 줄 '24년 n번'·'23년 n번' · 25판 2022 칸 6번 '21년)' 덧붙임)
  · 비슷하지만 묻는 것·답이 다른 것은 별개(관련 문항 rel=은 다음 단계 annot — 짝 목록은 보고 3절):
    C03 ↔ C05(All-ceramic 한계점 ★ ↔ 도재 완전 수복 장단점) · C06 ↔ C10·C11·C09(한중석 짤문항 변형 ↔ load to fracture·crack 종류·square of thickness) ·
    P03 ↔ P07(맥카트니 (1)(2)(3) ↔ McCartney 도해·적응증) · P05 ↔ P06(Stern ERA ★ ↔ Biloc and Plasta — 25판 해설 '그림을 주고 이름을 쓰는 형식으로 같았습니다') ·
    P08 ↔ P11(Combination clasp ↔ wrought wire 심미 이유) · G01 ↔ G14·G17·G04(Miller 분류) · G13 ↔ G15(probing depth ↔ 치은열구 깊이 일정) · G06 ↔ G11·G09(생물학적 폭경)
  · 합친 판단(보고 5절 확인): C08 = 2020 칸 3번 'Zirconia framework 위에 laminate veneer … 파절의 원인 5가지 이상'(답 7항목 글자 같음 · ★) · S01 = 2020 칸 4번 'Components of esthetic profile'(답 8항목 같음 · 25판 멘트 '매년 같은 짤 한 문제')
  · 출제연도 = 괄호(25판) ∪ 실린 칸 ∪ 다른 판본 같은 문제의 칸·괄호 — 판(파일) 해는 쓰지 않음"""
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_esth4 as P, subject as S
BASE = J.JBX; SUB = 'ESTH4'
NPAGES = P.NPAGES   # {'25': 16, '24': 18, '23': 15}
LECMAP = S.LECMAP

# ---------- 1. JB blocks ----------
blocks = {}
for ed, n in NPAGES.items():
    out = []
    for x in P.parse(ed, n):
        x['text'] = '\n'.join(x['lines']).strip(); out.append(x)
    blocks[ed] = out
BYKEY = {P.key(x): x for ed in blocks for x in blocks[ed]}
ANSRE = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$')
def stem_of(t):
    out = []
    for l in t.split('\n'):
        if ANSRE.match(l): break
        out.append(l)
    return ' '.join(out)
def tag_years(text):
    """문항 첫머리(답 이전)의 연도 괄호 전부 — 25판 (24,23) · (24,22,21) · (24,23,22,21) · (23,21) – 한중석 교수님 문항 · (짤)·(탈)·(변형)·(9점)·(T/F)는 연도 아님"""
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = re.sub(r'(반짤반탈|짤|탈|년|~)', ' ', g).replace('，', ',')
        if not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*[,、]\s*(20\d\d|\d\d)?)*\s*', g2): continue
        vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
        if not vs or not all(8 <= v <= 26 for v in vs): continue
        ys |= set(vs); raw.append('(' + re.sub(r'\s+', '', g) + ')')
    return ys, raw
def find(ed, sec, num):
    for x in blocks[ed]:
        if x['sec'] == sec and str(x['num']) == str(num): return x
    return None
def secyear(sec): m = re.match(r'(20\d\d)', sec or ''); return int(m.group(1)) % 100 if m else None

# ---------- 2. canonical questions ----------
LK_PROF = {'CER': '조준호', 'RBR': '여인성', 'CAD': '윤형인', 'DIG': '최순영', 'RPD': '곽재영', 'PER': '이용무', 'SMI': '백승학', 'LAM': '이창하'}   # 25 담당(26 자료 없음) — 출제 해 교수는 subject.YEAR_PROF
G = [
    # ---- C 심미수복재료–도재(CER · 25 조준호 · 23·24 조준호 · 21·22 한중석 '221111 New zirconia esthetic vs function vs longevity 1·2')
    ('C01', 'CER', 'A', ['25|2024|1']),                                     # Metal ceramic system의 한계 서술(9점)
    ('C02', 'CER', 'A', ['25|2024|2']),                                     # metal-ceramic margin 전치부 2개 이름·그리기(collar disappearing·collarless shoulder)
    ('C03', 'CER', 'A', ['25|2024|3']),                                     # ★ All-ceramic의 한계점(10점) — C05와 별개(묻는 것 = 한계만 · 괄호 연도 없음)
    ('C04', 'CER', 'A', ['25|2024|4']),                                     # Metal-ceramic 금속 구조 옳지 않은 것 모두
    ('C05', 'CER', 'A', ['25|2023|1', '24|2023|1', '24|2021|4', '23|2021|4']),   # 도재 완전 수복의 장단점 (23,21) — 2021 ★4 all ceramic crown의 장단점
    ('C06', 'CER', 'A', ['25|2023|2', '24|2023|2']),                        # (pf.한중석 짤문항 변형) O·I·R·F 줄임말 + load to fracture (23,21)
    ('C07', 'CER', 'A', ['25|2023|3', '24|2023|3', '24|2021|3', '23|2021|3']),   # 파절강도 a·b·c (23,21) – 한중석 교수님 문항
    ('C08', 'CER', 'A', ['25|2023|4', '24|2023|4', '25|2022|7', '24|2022|7', '23|2022|8', '23|2020|3']),   # Zirconia-porcelain veneer 파절 원인 5가지 (23,22) · 25판 2022 '23년 4번' · 2020 ★3(같은 답)
    ('C09', 'CER', 'A', ['25|2022|3', '24|2022|3', '23|2022|3']),           # 빈칸 — square of the thickness(2022)
    ('C10', 'CER', 'A', ['24|2021|1', '23|2021|1']),                        # Thickness → load to fracture(2021 ★)
    ('C11', 'CER', 'A', ['24|2021|2', '23|2021|2']),                        # ★ crack 종류 빈칸빵(2021)
    ('C12', 'CER', 'A', ['24|2021|5', '23|2021|5']),                        # ★ Hoop stress 정의와 임상적 의의(2021)
    # ---- R Resin bonded restoration(RBR · 25 여인성 · 23·24 이재현 출제)
    ('R01', 'RBR', 'A', ['25|2024|5', '25|2023|5', '24|2023|5']),           # ★ Wei YR 2016 1-retainer vs 2-retainer (24,23) · 25판 2023 '24년 5번'
    # ---- K CAD,CAM(CAD · 25 새 강의 윤형인 — 2021 한중석 문항 · 내용 = 25 CAD p.24 overmilling)
    ('K01', 'CAD', 'A', ['24|2021|6', '23|2021|6']),                        # CAD/CAM 보철물이 삭제량을 정확히 반영 못 하는 이유(milling bur → overmill)
    # ---- D 디지털 기술의 활용(DIG · 최순영)
    ('D01', 'DIG', 'A', ['25|2024|6']),                                     # 첫 번째 슬라이드 14문항 단답형(2024)
    ('D02', 'DIG', 'A', ['25|2023|6', '24|2023|6']),                        # 주어진 치아와 대칭인 그림(선지 미복원 · 답 2번 추정)
    ('D03', 'DIG', 'A', ['25|2023|7', '24|2023|7']),                        # CAD-CAM 사용 기계 순서(사진 보기) C-A-B
    # ---- P 가철성 보철물을 이용한 심미개선(RPD · 곽재영)
    ('P01', 'RPD', 'A', ['25|2024|7', '25|2023|9', '24|2023|10']),          # ★ 서베이어의 기능 (24,23) · 24판 2023 '(탈)' · 25판 2023 '24년 7번'
    ('P02', 'RPD', 'A', ['25|2024|8', '25|2022|8', '24|2022|8', '24|2021|8', '23|2022|9', '23|2021|8']),   # ★ 환자의 기대와 욕구 충족 (24,22,21) · 25판 2022 '24년 8번'
    ('P03', 'RPD', 'A', ['25|2024|9']),                                     # 맥카트니 클라스프 (1) 빈칸 (2) T/F (3) I bar 타입 — P07과 별개(꼴·답 다름)
    ('P04', 'RPD', 'A', ['25|2024|10', '25|2023|8', '25|2022|2', '24|2023|8', '24|2022|2', '24|2021|7', '23|2022|2', '23|2021|7']),   # ★ Staubi 1996 attachment 분류 (24,23,22,21)
    ('P05', 'RPD', 'A', ['25|2024|11']),                                    # ★ 그림 attachment system — Stern ERA(2024)
    ('P06', 'RPD', 'A', ['25|2023|10', '24|2023|9']),                       # 그림 attachment — Biloc and Plasta(2023)
    ('P07', 'RPD', 'A', ['25|2022|5', '24|2022|5', '24|2021|10', '23|2022|6', '23|2021|10']),   # McCartney clasp 도해·적응증(2022 · 2021 ★10)
    ('P08', 'RPD', 'A', ['25|2022|9', '24|2022|9', '23|2022|10']),          # Combination clasp 구성요소와 특징(2022)
    ('P09', 'RPD', 'A', ['24|2021|9', '23|2021|9']),                        # 사진 주고 이름 · 이전) Swiss McCollum att. 설명(2021)
    ('P10', 'RPD', 'A', ['23|2020|1']),                                     # ★ 클라스프 심미적 방법 열거 (짤)(2020)
    ('P11', 'RPD', 'A', ['23|2020|2']),                                     # ★ wrought wire가 심미적인 이유(2020)
    # ---- G 심미적 치주치료(PER · 이용무)
    ('G01', 'PER', 'A', ['25|2024|13']),                                    # 밀러 class1·2 나누는 기준 ( ) — mucogingival junction(2024)
    ('G02', 'PER', 'A', ['25|2024|14']),                                    # 구개면 이식편 채취 — 대구개동맥(2024 · 교과서 Ch37 p.576)
    ('G03', 'PER', 'A', ['25|2024|15']),                                    # 치관연장술 대신 ( ) — forced tooth eruption(2024 · 교과서 p.566)
    ('G04', 'PER', 'A', ['25|2023|11', '24|2023|11']),                      # Miller 3은 FCTG로 100% 회복 T/F(변형)(2023)
    ('G05', 'PER', 'A', ['25|2023|12', '24|2023|12', '24|2021|18', '23|2021|18']),   # 멜라닌 색소침착 재발 T/F (23,21)
    ('G06', 'PER', 'A', ['25|2023|13', '25|2022|4', '24|2023|13', '24|2022|4', '23|2022|5']),   # 치아와 정상 치은 도해·생물학적 폭경 (23,22) · 25판 2022 '23년 13번'
    ('G07', 'PER', 'A', ['25|2022|1', '24|2022|1', '24|2021|14', '23|2022|1', '23|2021|14']),   # 유리치은이식 후 creeping attachment (22,21)
    ('G08', 'PER', 'A', ['25|2022|6', '24|2022|6', '24|2021|15', '23|2022|7', '23|2021|15']),   # FGG가 FCTG보다 색조 심미적 T/F(2022) · 21년) 같은 문제(25판이 합침)
    ('G09', 'PER', 'A', ['25|2022|10', '24|2022|10', '24|2021|16', '23|2022|13', '23|2021|16']),   # finishing line이 biological width 침범 시 반응 2가지 (22,21) · 22 칸 'Biologic width 침범시 결과 2개'
    ('G10', 'PER', 'A', ['24|2021|11', '23|2021|11']),                      # ★ 변연치은은 각화치은으로 부착치은 T/F(2021)
    ('G11', 'PER', 'A', ['24|2021|12', '23|2021|12']),                      # ★ 생물학적 폭경은 치은열구 깊이 포함 T/F(2021)
    ('G12', 'PER', 'A', ['24|2021|17', '23|2021|17']),                      # ★ Tarnow ( )mm 이하 papilla(2021)
    ('G13', 'PER', 'A', ['24|2021|19', '23|2021|19']),                      # 한 치아 probing depth 다 같다 T/F(2021)
    ('G14', 'PER', 'A', ['24|2021|20', '23|2021|20']),                      # Miller Class III — ( ) 넘어가지 않음 → MGJ(2021)
    ('G15', 'PER', 'A', ['23|2020|5']),                                     # 치은열구 깊이 일정 — '잘못된 문제라고 시험시간에 말씀'(2020 · 답 없음)
    ('G16', 'PER', 'A', ['23|2020|6']),                                     # Crown lengthening 최종변연 — 3mm(2020)
    ('G17', 'PER', 'A', ['23|2020|7']),                                     # ★ Miller Class II 그림 맞추기(2020)
    ('G18', 'PER', 'A', ['23|2020|8']),                                     # 노출된 치근 덮는 술식 3개 이상(2020)
    # ---- S Esthetic smile(SMI · 백승학 — 25판 멘트 '매년 같은 짤 한 문제')
    ('S01', 'SMI', 'A', ['25|2024|18', '25|2023|14', '24|2023|14', '23|2020|4']),   # ★ Components of aesthetic smile 8가지 (24,23,22) · 2020 ★4 'Components of esthetic profile'(같은 답)
    # ---- L Laminate를 이용한 전치부 심미수복(LAM · 이창하 2022 출제 · 2023 4Q 강의 → 24·25 4Q 없음 · 24·25판에서 빠짐) — 참고
    ('L01', 'LAM', 'C', ['23|2022|4']),                                     # 그림의 기구 — depth guide bur
    ('L02', 'LAM', 'C', ['23|2022|11']),                                    # 라미네이트 절삭 분류 세 개(그림) — Butt joint·Palatal chamfer·Feather edge
    ('L03', 'LAM', 'C', ['23|2022|12']),                                    # PLV 금기증
    # ---- Z 미복원 자리(build4 _HIDE가 숨김 — 기출 대장 '미복원')
    ('Z01', '', 'A', ['25|2024|12']),
    ('Z02', '', 'A', ['25|2024|16-17']),
]
def _blk(b):
    x = BYKEY.get(b); assert x, b; return x
CANON = [(cid, _blk(bs[0])['ed'], _blk(bs[0])['sec'], _blk(bs[0])['num']) for cid, lk, tier, bs in G]
OTHER = {cid: [(_blk(b)['ed'], _blk(b)['sec'], _blk(b)['num']) for b in bs[1:]] for cid, lk, tier, bs in G if bs[1:]}
LK = {cid: lk for cid, lk, tier, bs in G}
TIER = {cid: tier for cid, lk, tier, bs in G}
CROPS = {}   # JB 그림 조각은 다음 단계(tools/jbfig.py → jb_crops.json — 보고 3절 그림 문항 표)
FIGRE = re.compile(r'그림|사진|도해|그리시오|빈칸빵')
TALRE = re.compile(r'\(\s*탈\s*\)|\(\s*\d\d\s*,\s*탈\s*\)')
Q = []
for cid, ed, sec, num in CANON:
    x = find(ed, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t)
    yrs = set(ty) | ({secyear(sec)} if secyear(sec) else set())
    for (e2, s2, n2) in OTHER.get(cid, []):
        x2 = find(e2, s2, n2); assert x2, (cid, e2, s2, n2)
        if secyear(s2): yrs.add(secyear(s2))
        yrs |= tag_years(x2['text'])[0]
    short = re.sub(r'^★?\s*\d{1,2}(\s*-\s*\d{1,2})?\s*[.．]?\s*★?\s*', '', t.split('\n')[0]).strip() or (t.split('\n') + [''])[1].strip()   # 25판 2024 칸 9번 '9. ' 다음 줄 '맥카트니 클라스프'
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': TIER[cid], 'prof': '',
              'src': f'JB {ed}판 · {sec} 칸 {num}번', 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True),
              'secy': secyear(sec), 'tal': bool(TALRE.search(stem_of(t))), 'pick': ''})

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
    q['fig'] = bool(FIGRE.search(stem_of(q['text'])))

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
MENT = {ed: ment(ed, [1, 2]) for ed in NPAGES}   # 판 머리 멘트·수업 표 = 1~2쪽(세 판 모두)
if __name__ == '__main__':
    used = {}
    for cid, lk, tier, bs in G:
        for b in bs: used.setdefault(b, []).append(cid)
    allk = [P.key(x) for ed in NPAGES for x in blocks[ed]]
    print('Q', len(Q), '· 블록', len(allk), '· 묶음 안 블록', len(used), '· 못 쓴 블록', [k for k in allk if k not in used], '· 없는 블록', [k for k in used if k not in allk])
    print('두 카드 이상에 든 블록', {k: v for k, v in used.items() if len(v) > 1})
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [(r['ed'], r['sec'], r['num']) for r in LEDGER if r['st'] == 'ref'])
    for q in Q: print(f"{q['id']} {q['tier']} {LK[q['id']]:4} {str(q['yrs']):22} {q['jbtag'][:22]:22} {'탈 ' if q['tal'] else ''}{'🖼 ' if q['fig'] else ''}{q['short'][:46]}")
