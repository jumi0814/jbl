import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_pharm4 as P, subject as S
BASE = J.JBX; SUB = 'PHARM4'
# 판 → 쪽 수 · 25·24·23 = 4Q JB(work/jb/PHARM4_20YY) · 25q3·24q3·23q3 = 3Q JB(work/jb/PHARM_20YY)의 <살균제와 소독제>·(23q3) [성호르몬과 길항제] 칸(11-16 Q4 JB 단계 — 사용자 메모 ①·보고 work/PHARM4/jb/R_JB_PHARM4.md)
NPAGES = {'25': 23, '24': 30, '23': 32, '25q3': 26, '24q3': 40, '23q3': 54}
LECMAP = S.LECMAP

# ---------- 1. JB blocks ----------
blocks = {}
for ed, n in NPAGES.items():
    out = []
    for x in P.parse(ed, n):
        x['text'] = '\n'.join(x['lines']).strip(); out.append(x)
    blocks[ed] = out
# 3Q 판은 이 과목 칸이 든 쪽만 원본 쪽 그림으로(1쪽 = 판 머리 멘트 · 3Q 다른 강의 쪽은 싣지 않음)
JBPAGES = {ed: (sorted({1} | {p for x in blocks[ed] for p in x['lp']}) if ed.endswith('q3') else list(range(1, n + 1))) for ed, n in NPAGES.items()}
ANSRE = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$')
def stem_of(t):
    out = []
    for l in t.split('\n'):
        if ANSRE.match(l): break
        out.append(l)
    return ' '.join(out)
NOISE = r"(반짤반탈|짤 변형|완짤|짤|탈|년도|년|NEW|new|이전|이후|과거|’|‘|'|`|~|\.|번과 유사|유사|학번|추가|기출|출제|복원|최근|연속|회)"
def tag_years(text, ed='25', sec='2024'):
    """문항 첫머리(답 이전)의 연도 괄호 전부 — (24,23) · (24,과거) · (21’ 20’, 19’) · (20’, 19’, 18’, 16’ 이전) · (2021년 6번 문항) · (2019 1 번 문항)
    3Q 23·24판(23q3·24q3)은 '’'가 없는 두 자리 = 학번(+2 — 3Q 23판 1쪽 "과거 문제 옆의 숫자는 ‘가 붙은 경우 년도, 없으면 학번" · tools/pharm/assemble.py tag_years와 같게)"""
    ys, raw = set(), []
    secy = int(sec) % 100
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        mq_ = re.fullmatch(r'\s*(20\d\d)\s*년?\s*\d{1,2}(?:\s*-\s*\d)?\s*번\s*문항(?:\s*중복)?\s*', g)   # '(2021년 6번 문항)'·'(2019 1 번 문항)' = 그 해 출제(네 자리 연도)
        if mq_: ys.add(int(mq_.group(1)) % 100); raw.append('(' + g.strip() + ')'); continue
        g2 = re.sub(NOISE, ' ', g).replace('，', ',')
        if not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*[,、\-\s]\s*(20\d\d|\d\d)?)*\s*', g2): continue
        vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
        if not vs or not all(5 <= v <= 26 for v in vs): continue
        if '-' in g2 and len(vs) == 2: vs = list(range(min(vs), max(vs) + 1))
        out = []
        for v in vs:
            if ed in ('24q3', '23q3') and ('’' not in g and "'" not in g): out.append(v + 2 if v + 2 < secy else v)
            else: out.append(v)
        ys |= set(out); raw.append('(' + g.strip() + ')')
    return ys, raw
def secyear(sec): return int(sec) % 100

# ---------- 2. canonical questions ----------
# 강의 = 26 4Q 수업(subject.LEC_ORDER) · 문항 id = JB 칸 글자(AX·SD·LA·DI·SX·PG·GR·XE·DS) + 번호(11-16 처음 정함 — jb_lock.json이 잠금 · 번호 당기기 금지)
TOPIC_LK = {'DS': 'DS', 'SD': 'SED', 'LA': 'LA', 'DI': 'DI', 'SX': 'HOR', 'PG': 'PGX', 'GR': 'GER', 'AX': 'ANX', 'XE': 'XE'}
LK_PROF = {'DS': '조영단', 'SED': '서광석', 'LA': '김우진', 'DI': '이윤실', 'HOR': '노상호', 'PGX': '백정화', 'GER': '백정화', 'ANX': '이윤실', 'XE': '이윤실'}   # 강의 연결 교수(26 담당 · 26 자료가 아직 없는 강의는 25 담당) — 출제 해 교수는 subject.YEAR_PROF
TOPIC_NAME = {'DS': '살균제와 소독제', 'SD': '진정수면제', 'LA': '국소마취제', 'DI': '약물상호작용', 'SX': '성호르몬과 길항제', 'PG': '치과약물유전학', 'GR': '노인 및 임산부/수유부의 약물치료', 'AX': '항불안제', 'XE': '구강건조증 치료제'}   # JB 칸 이름(출처 줄)
TIER_C = {'AX', 'XE'}   # 참고(⭐ 연결 의무 없음): 항불안제 = 2026은 3Q에서 강의·시험(메모 ②) · 구강건조증 = 2024부터 3Q(23 4Q JB에만)
# 같은 문제 묶음 — (id, [판:칸-번호 …]) · 첫 블록 = 정식 원문(가장 최신 판 · 같은 판이면 가장 최근 칸 — DS는 3Q 사이트 DS01~DS31 묶음·원문 그대로) · 나머지 = 다른 판본(OTHER)
# 묶는 기준(보고 3절): ① 글자가 같은(오타·띄어쓰기만 다른) 문제 ② JB가 같은 문제라고 적음(최신 판 괄호 '(24,23)'·'(24,과거)'에 든 해의 칸 문항 · 'n번 중복'·'중복 복원' · '(2021년 6번 문항)') ③ 3Q 사이트가 이미 한 카드로 묶은 23 4Q JB 블록(tools/pharm/assemble.py MAPQ4 — 같은 결정 유지)
#   그 밖에 묻는 것·답이 비슷하기만 한 문항은 별개(관련 문항 rel=은 다음 단계 annot — 짝 목록 보고 3절)
GROUPS = [
    # --- DS 살균제와 소독제(3Q JB 25q3·24q3·23q3 — 3Q 사이트 PHARM DS01~DS31과 같은 묶음·순서)
    ('DS01', ['25q3:2024-1', '25q3:2023-3', '24q3:2023-3']), ('DS02', ['25q3:2024-2', '25q3:2023-4', '24q3:2023-4']),
    ('DS03', ['25q3:2024-3', '25q3:2023-1', '24q3:2023-1']), ('DS04', ['25q3:2024-4', '25q3:2023-2', '24q3:2023-2']),
    ('DS31', ['24q3:2021-5', '23q3:2021-5']), ('DS05', ['25q3:2024-5', '24q3:2021-1', '23q3:2021-1', '23q3:2020-14']),
    ('DS06', ['25q3:2023-5', '24q3:2023-5']), ('DS07', ['25q3:2022-1', '24q3:2022-1', '23q3:2022-1']), ('DS08', ['25q3:2022-2', '24q3:2022-2', '23q3:2022-2']),
    ('DS09', ['25q3:2022-3', '24q3:2022-3', '23q3:2022-3']), ('DS10', ['25q3:2022-4', '24q3:2022-4', '23q3:2022-4']), ('DS11', ['25q3:2022-5', '24q3:2022-5', '23q3:2022-5']),
    ('DS12', ['25q3:2022-6', '24q3:2022-6', '23q3:2022-6']), ('DS13', ['25q3:2022-7', '24q3:2022-7', '24q3:2022-8', '23q3:2022-7', '23q3:2022-8']),
    ('DS14', ['25q3:2022-8', '24q3:2022-9', '23q3:2022-9']), ('DS30', ['25q3:2022-9', '24q3:2022-10', '23q3:2022-10']),
    ('DS15', ['24q3:2021-2', '23q3:2021-2']), ('DS16', ['24q3:2021-3', '23q3:2021-3', '23q3:2020-1']), ('DS17', ['24q3:2021-6', '23q3:2021-6']),
    ('DS18', ['24q3:2021-7', '23q3:2021-7', '23q3:2020-4']), ('DS19', ['24q3:2021-8', '23q3:2021-8', '23q3:2020-7']), ('DS20', ['24q3:2021-9', '23q3:2021-9', '23q3:2020-8']),
    ('DS21', ['23q3:2020-2', '24q3:2021-4', '23q3:2021-4']), ('DS22', ['23q3:2020-3']), ('DS23', ['23q3:2020-5']), ('DS24', ['23q3:2020-6']),
    ('DS25', ['23q3:2020-9']), ('DS26', ['23q3:2020-10']), ('DS27', ['23q3:2020-11']), ('DS28', ['23q3:2020-12']), ('DS29', ['23q3:2020-13']),
    # --- SD 진정수면제(서광석)
    ('SD01', ['25:2024-1']), ('SD02', ['25:2024-2', '24:2022-7', '23:2022-7', '24:2023-3']),   # (24,23,22) — 24판 2023 칸 3번 '서맥 발생이 빈발한다'가 25판에서 이 괄호로 합쳐짐(25판 2023 칸에서 빠진 셋 = TCE·진통·서맥)
    ('SD03', ['25:2024-3']), ('SD04', ['25:2024-4', '24:2023-1']), ('SD05', ['25:2024-5']), ('SD06', ['25:2024-6', '24:2023-6']), ('SD07', ['25:2024-7']),
    ('SD08', ['25:2023-1', '24:2023-2']), ('SD09', ['25:2023-2', '24:2023-4']), ('SD10', ['25:2023-3', '24:2023-5']), ('SD11', ['25:2023-4', '24:2023-7']),
    ('SD12', ['25:2022-1', '24:2022-1', '23:2022-1']), ('SD13', ['25:2022-2', '24:2022-2', '23:2022-2', '24:2021-1', '23:2021-1']),   # 21-1 Triazolam 과잉반응 억제 = flumazenil(3Q AX26)
    ('SD14', ['25:2022-3', '24:2022-3', '23:2022-3', '23:2020-1', '23:2020-16']),   # 2020 1·16 주사 시 통증(3Q AX27)
    ('SD15', ['25:2022-4', '24:2022-4', '23:2022-4']), ('SD16', ['25:2022-5', '24:2022-5', '23:2022-5']), ('SD17', ['25:2022-6', '24:2022-6', '23:2022-6']),
    ('SD18', ['25:2022-7', '24:2022-8', '23:2022-8']), ('SD19', ['25:2022-8', '24:2022-9', '23:2022-9']), ('SD20', ['25:2022-9', '24:2022-10', '23:2022-10']),
    ('SD21', ['24:2021-2', '23:2021-2', '23:2020-10']),   # 우유 같은 흰색(3Q AX29)
    ('SD22', ['24:2021-3', '23:2021-3']), ('SD23', ['24:2021-4', '23:2021-4']), ('SD24', ['24:2021-5', '23:2021-5', '23:2020-13']),   # 선행성 기억상실(3Q AX31)
    ('SD25', ['24:2021-6', '23:2021-6']), ('SD26', ['24:2021-7', '23:2021-7']),
    ('SD27', ['23:2020-2']), ('SD28', ['23:2020-3']), ('SD29', ['23:2020-4']), ('SD30', ['23:2020-5']), ('SD31', ['23:2020-6']), ('SD32', ['23:2020-7']),
    ('SD33', ['23:2020-8']), ('SD34', ['23:2020-9']), ('SD35', ['23:2020-11']), ('SD36', ['23:2020-12']), ('SD37', ['23:2020-14']), ('SD38', ['23:2020-15']),
    # --- LA 국소마취제
    ('LA01', ['25:2024-1', '24:2023-1']), ('LA02', ['25:2024-2', '24:2023-2']), ('LA03', ['25:2024-3', '24:2023-3']), ('LA04', ['25:2024-4', '24:2023-4']),   # LA04 답 25판 4) · 24판 3)
    ('LA05', ['25:2023-1', '24:2023-5', '24:2021-3', '23:2021-3', '23:2020-6']),   # 1:200,000 소아·성인 계산 — 21-3 '(복원이 불량하여 유사한 문제를 가져왔습니다.)'·20-6 '(중복복원)' 글 같음
    ('LA06', ['25:2023-2', '24:2023-6']),   # 답 25판 4.4, 13.9 · 24판 6.7, 8.3
    ('LA07', ['25:2022-1', '24:2022-1', '23:2022-1']), ('LA08', ['25:2022-2', '24:2022-2', '23:2022-2']), ('LA09', ['25:2022-3', '24:2022-3', '23:2022-3', '23:2020-8']),
    ('LA10', ['25:2022-4', '24:2022-4', '23:2022-4']), ('LA11', ['25:2022-5', '24:2022-5', '23:2022-5']),
    ('LA12', ['24:2021-1', '23:2021-1']), ('LA13', ['24:2021-2', '23:2021-2', '23:2020-7']),
    ('LA14', ['23:2020-1']), ('LA15', ['23:2020-2']), ('LA16', ['23:2020-3']), ('LA17', ['23:2020-4']), ('LA18', ['23:2020-5']),
    # --- DI 약물상호작용
    ('DI01', ['25:2024-1']), ('DI02', ['25:2024-2']), ('DI03', ['25:2023-1', '24:2023-1']),
] + [(f'DI{3 + i:02d}', [f'25:2022-{i}', f'24:2022-{i}', f'23:2022-{i}']) for i in range(1, 11)] + [(f'DI{13 + i:02d}', [f'24:2021-{i}', f'23:2021-{i}']) for i in range(1, 7)] + [
    # --- SX 성호르몬과 길항제(노상호) — 23q3 = 3Q 23판 [성호르몬과 길항제]
    ('SX01', ['25:2024-1', '24:2023-1', '24:2021-5', '23q3:2021-5', '23q3:2020-2']), ('SX02', ['25:2024-2', '24:2023-2', '23q3:2020-16']),
    ('SX03', ['25:2024-3', '24:2023-3', '24:2021-14', '23q3:2021-14', '23q3:2020-18']), ('SX04', ['25:2024-4', '24:2023-4', '23q3:2020-3']),
    ('SX05', ['25:2024-5', '24:2023-5', '24:2021-12', '23q3:2021-12', '23q3:2020-9']),
    ('SX06', ['25:2024-6', '24:2022-3', '24:2021-7', '23q3:2022-3', '23q3:2021-7', '23q3:2020-7']),
    ('SX07', ['25:2024-7', '24:2022-6', '24:2021-15', '23q3:2022-6', '23q3:2021-15', '23q3:2020-13']),
    ('SX08', ['25:2024-8', '24:2021-3', '23q3:2021-3', '23q3:2020-14']),
    ('SX09', ['25:2024-9', '24:2021-8', '23q3:2021-8', '23q3:2020-11']),   # '(24,과거)' — 21·20 '호르몬을 이용한 피임제의 작동원리'
    ('SX10', ['25:2023-1', '24:2023-6', '24:2021-2', '23q3:2021-2', '23q3:2020-5']),
    ('SX11', ['25:2023-2', '24:2023-7', '24:2022-2', '24:2021-4', '23q3:2022-2', '23q3:2021-4', '23q3:2020-1']),
    ('SX12', ['25:2022-1', '24:2022-1', '24:2021-6', '23q3:2022-1', '23q3:2021-6', '23q3:2020-6']),
    ('SX13', ['25:2022-2', '24:2022-4', '23q3:2022-4', '23q3:2020-12']), ('SX14', ['25:2022-3', '24:2022-5', '23q3:2022-5', '23q3:2020-10']),
    ('SX15', ['24:2021-1', '23q3:2021-1']), ('SX16', ['24:2021-9', '23q3:2021-9']), ('SX17', ['24:2021-10', '23q3:2021-10', '23q3:2020-15']),
    ('SX18', ['24:2021-11', '23q3:2021-11']), ('SX19', ['24:2021-13', '23q3:2021-13', '23q3:2020-8']),
    ('SX20', ['23q3:2020-4']), ('SX21', ['23q3:2020-9-1']), ('SX22', ['23q3:2020-17']),
    # --- PG 치과약물유전학(백정화) — 23판 p.26 첫 칸 '[2021년 …]' = 2022(parse SECFIX)
    ('PG01', ['25:2024-1', '25:2022-1', '24:2023-1', '24:2022-1', '24:2021-1', '23:2022-1', '23:2021-1']),
    ('PG02', ['25:2024-2', '24:2022-2', '23:2022-2']),   # (24,23) — 24판·23판은 2022 칸 'carbamazepine - induced SJS 유전자?'
    ('PG03', ['25:2024-3']), ('PG04', ['25:2024-4']), ('PG05', ['25:2024-5']), ('PG06', ['25:2023-1', '24:2023-2']), ('PG07', ['25:2023-2', '24:2023-3']),
    ('PG08', ['25:2022-2', '24:2022-3', '23:2022-3']), ('PG09', ['25:2022-3', '24:2022-4', '23:2022-4']),
    # --- GR 노인 및 임산부/수유부의 약물치료(백정화)
    ('GR01', ['25:2024-1']), ('GR02', ['25:2024-2']), ('GR03', ['25:2024-3', '24:2023-3', '24:2022-3', '24:2021-5', '23:2022-3', '23:2021-5']),
    ('GR04', ['25:2024-4', '24:2023-4', '24:2022-4', '23:2022-4']),   # (24,22) — 24판 2023 칸 4번 '태아에게 안전하고 임신말기에 …(12개 보기)'도 같은 문제(25판 2023 칸에서 빠짐)
    ('GR05', ['25:2023-1', '24:2023-1']), ('GR06', ['25:2023-2', '24:2023-2']),
    ('GR07', ['25:2022-1', '24:2022-1', '23:2022-1']), ('GR08', ['25:2022-2', '24:2022-2', '23:2022-2']), ('GR09', ['25:2022-3', '24:2022-5', '23:2022-5']),
    ('GR10', ['24:2021-1', '23:2021-1']), ('GR11', ['24:2021-2', '23:2021-2']), ('GR12', ['24:2021-3', '23:2021-3']), ('GR13', ['24:2021-4', '23:2021-4']), ('GR14', ['24:2021-6', '23:2021-6']),
    # --- AX 항불안제(참고 C — 2026은 3Q)
    ('AX01', ['25:2024-1']), ('AX02', ['25:2024-2']), ('AX03', ['25:2024-3', '24:2023-1']), ('AX04', ['25:2024-4', '24:2023-2']),
    ('AX05', ['25:2024-5', '24:2023-3']),   # Buspirone 옳지 않은 것 (24,23) — 24판 2023 칸 3번(복원 선지 다름 · 답 2)
    ('AX06', ['25:2024-6']), ('AX07', ['25:2023-1', '24:2023-5']),
    ('AX08', ['25:2023-2', '24:2023-6', '24:2021-3', '23:2021-3', '23:2020-4']),   # 제2상 포합(3Q AX12)
    ('AX09', ['25:2021-1', '24:2021-1', '23:2021-1', '23:2020-8']),   # BZ1 T/F(3Q AX05)
    ('AX10', ['25:2021-2', '24:2021-2', '23:2021-2']), ('AX11', ['25:2021-3', '24:2021-4', '23:2021-4', '23:2020-6']),   # BZD 외 항불안(3Q AX03)
    ('AX12', ['24:2023-4']), ('AX13', ['24:2022-1', '23:2022-1']), ('AX14', ['24:2022-2', '23:2022-2']), ('AX15', ['24:2022-3', '23:2022-3']),
    ('AX16', ['24:2022-4', '23:2022-4']), ('AX17', ['24:2022-5', '23:2022-5']),
    ('AX18', ['23:2020-1']), ('AX19', ['23:2020-2']), ('AX20', ['23:2020-3']), ('AX21', ['23:2020-5']), ('AX22', ['23:2020-7']), ('AX23', ['23:2020-9']),
    # --- XE 구강건조증 치료제(참고 C — 23 4Q JB만 · 2024부터 3Q)
    ('XE01', ['23:2022-1', '23:2022-3']), ('XE02', ['23:2022-2', '23:2022-5']),   # JB '1 번과 중복 복원으로 추정'·'2 번 문제와 중복 복원으로 예상'(3Q XE08·XE09)
    ('XE03', ['23:2022-4']), ('XE04', ['23:2022-6']), ('XE05', ['23:2022-7']), ('XE06', ['23:2021-1']), ('XE07', ['23:2021-2']), ('XE08', ['23:2021-3']),
    ('XE09', ['23:2021-4', '23:2020-5']), ('XE10', ['23:2021-5', '23:2020-2']), ('XE11', ['23:2021-6']), ('XE12', ['23:2021-7', '23:2020-1']),   # 3Q XE15·XE03·XE17
    ('XE13', ['23:2021-8']), ('XE14', ['23:2021-9']), ('XE15', ['23:2020-3']), ('XE16', ['23:2020-4']), ('XE17', ['23:2020-6']),
]
def _ref(s):
    ed, _, r = s.partition(':'); sec, _, num = r.partition('-'); return ed, sec, num
BMAP = {}
for ed in NPAGES:
    for x in blocks[ed]:
        k_ = (ed, x['sec'], str(x['num']), x['topic']); assert k_ not in BMAP, k_; BMAP[k_] = x
def find(ed, sec, num, topic=None):
    c = [x for (e, s, n, t), x in BMAP.items() if (e, s, n) == (ed, str(sec), str(num)) and (topic is None or t == topic)]
    return c[0] if len(c) == 1 else None
OTHER = {}; CANON = []; _seen = set()
for cid, refs in GROUPS:
    tp = re.match(r'[A-Z]+', cid).group(0)
    xs = []
    for r in refs:
        k_ = _ref(r) + (tp,); assert k_ in BMAP, ('없는 블록', cid, r); assert k_ not in _seen, ('두 번 쓴 블록', cid, r); _seen.add(k_); xs.append(k_)
    CANON.append((cid, xs[0])); OTHER[cid] = xs[1:]
assert len({c for c, _ in CANON}) == len(CANON), '같은 id 두 번'
LOST = set()
CROPS = {}
FIGQ = {'LA12', 'XE09'}   # 문제 쪽에 그림·표가 있는 문항(LA12 = 보기 1)~4) 구조식 그림 · XE09 = 2020 칸 5번 빈 표 그림) — 그림 조각은 다음 단계(보고 3절 그림 표)
Q = []
for cid, k0 in CANON:
    ed, sec, num, tp = k0; x = BMAP[k0]
    tier = 'C' if tp in TIER_C else 'A'; lk = TOPIC_LK[tp]
    t = x['text']; ty, raw = tag_years(t, ed, sec)
    short = next((re.sub(r'^\s*(\d{1,2}(-\d)?)\s*[.．)]\s*', '', l).strip() for l in t.split('\n') if re.sub(r'^\s*(\d{1,2}(-\d)?)\s*[.．)]\s*', '', l).strip()), '')
    yrs = set(ty) | ({secyear(sec)} if not (x.get('sub') and ty) else set())   # 딸린 문항(23q3 성호르몬 2020 '9-1. … (19’, 18’, 16’ 이전)')은 제 괄호 해만 — 칸 해를 붙이지 않음(3Q 26판 소문항과 같은 규칙)
    for o_ in OTHER[cid]:
        x2 = BMAP[o_]; t2 = tag_years(x2['text'], o_[0], o_[1])[0]
        if not (x2.get('sub') and t2): yrs.add(secyear(o_[1]))
        yrs |= t2
    if ed.endswith('q3'): src = f'JB {ed}판 · {sec}년 칸 · 3Q JB {TOPIC_NAME[tp]} {num}번'   # 3Q JB(살균제와 소독제·23 성호르몬) — 3Q 사이트 '23q4판' 꼴의 거울
    else: src = f'JB {ed}판 · {sec}년 칸 · {TOPIC_NAME[tp]} {num}번'
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': tier, 'prof': LK_PROF[lk], 'src': src,
              'topic': tp, 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True), 'secy': secyear(sec),
              'tal': bool(re.search(r'\(\s*탈\s*\)', stem_of(t))), 'pick': '', 'hdr': x.get('hdr', '')})

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
    o = []
    for o_ in OTHER.get(q['id'], []):
        x2 = BMAP[o_]; o.append({'ed': o_[0], 'sec': o_[1], 'num': o_[2], 'pg': x2['pg'], 'pg2': x2['pg2'], 'text': x2['text']})
    q['other'] = o; q['lab24'] = ''; q['crops'] = CROPS.get(q['id'], {})
    q['fig'] = q['id'] in FIGQ

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
    for i in JBPAGES[ed]:
        if not os.path.exists(f'{dj}/{i}.jpeg'):   # JB 쪽 이미지가 없는 환경(클라우드 세션) — 지금 docs/packs의 쪽 이미지를 그대로(tools/jblpaths.prev_jb_pages)
            IMG['jb'][f'{ed}-{i}'] = J.prev_jb_pages(SUB)[f'{ed}-{i}']; continue
        im = Image.open(f'{dj}/{i}.jpeg').convert('RGB')
        if i in vis: IMG['jb'][f'{ed}-{i}'] = b64(im, 50)
        else: IMG['jb'][f'{ed}-{i}'] = b64(im.convert('L').resize((860, int(im.size[1] * 860 / im.size[0]))), 32)
# ---------- 7. ledger ----------
LEDGER = []
idmap = {(q['ed'], q['sec'], str(q['num']), q['topic']): q['id'] for q in Q}
rev = {}
for cid, lst in OTHER.items():
    for (e2, s2, n2, t2) in lst: rev.setdefault((e2, s2, str(n2), t2), []).append(cid)
for ed in NPAGES:
    for x in blocks[ed]:
        key = (ed, x['sec'], str(x['num']), x['topic']); first = x['text'].split('\n')[0][:70]
        if key in idmap: st, to = 'card', [idmap[key]]
        elif key in rev: st, to = 'dup', rev[key]
        else: st, to = 'ref', []
        LEDGER.append({'ed': ed, 'sec': x['sec'] + '년', 'num': x['num'], 'pg': x['pg'], 'first': first, 'st': st, 'to': to})
def ment(ed, pages):
    t = ''
    for p in pages:
        s = P.rd(f'{P.jbdir(ed)}/{p}.txt'); t += '\n'.join(l for l in s.split('\n') if '무단인쇄' not in l and l.strip()) + '\n'
    return t.strip()
MENT = {ed: ment(ed, [1]) for ed in NPAGES}   # 판 머리 멘트 = 그 판 1쪽(3Q 판도 3Q JB 1쪽 — 메모 ①)
if __name__ == '__main__':
    print('Q', len(Q), '블록', sum(len(b) for b in blocks.values()))
    for q in Q: print(q['id'], q['tier'], q['prof'], q['yrs'], q['jbtag'], q['short'][:36])
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [(r['ed'], r['sec'], r['num'], r['first'][:28]) for r in LEDGER if r['st'] == 'ref'])
    for e_ in NPAGES: print(f'{e_}판 블록', len(blocks[e_]), {s_: sum(1 for r in LEDGER if r['ed'] == e_ and r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, '쪽 그림', len(JBPAGES[e_]))
