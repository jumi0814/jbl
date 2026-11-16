import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
"""RAD 임상영상치의학(4Q) — JB 23·24·25판 → 정식 문항(Q)·같은 문제의 다른 판본(other)·대조표(LEDGER) (2026-11-16 JB 단계 · work/RAD/jb/R_JB_RAD.md)
id = 강의 글자 + 번호(강의 안에서 최근 해 먼저 · jb_lock.json이 잠금 — 번호 당기기 금지):
  P 치주(PER) · J 정당화(JUS) · I 임플란트(IMP) · C CT·MRI(CTMR) · K 치아 주위 병소(PTL) · D DSR · F 프랙탈(FRAC — 25 자료 없음) · L Deep learning(DL)
  V 3차원(TDI) · R 치아와 관련 없는 투과성(TRL) · M 혼합성·불투과성(MIX) · H 두경부 영상해부학(HNA) · X 허경회 증례(HC1·HC2 …) · W 법규(LAW) · Z 25판 2024 칸 미복원 자리(숨김)
묶음 G = (id, 강의 키, tier, [블록 '판|칸|번호' …]) — 첫 블록 = 정식(가장 최신 판 · 가리킴 줄이 아닌 것), 나머지 = 같은 문제의 다른 판본(OTHER)
  · '21 치주질환, 골파괴, 방사선 관련 문제'(24·25판 2023 칸 묶음 머리) = 21-1·21-2·21-3 세 카드(P07·P03·P08)의 다른 판본
  · 판 사이 같은 문제 = 문제 글이 같거나 JB가 같은 문제라고 적은 것(괄호 연도 사슬 + 25판 2022 칸 '2024년 n번 문항' 가리킴 · 24판이 23판 2022 땡시 문항을 빼고 2023 칸 괄호에 (22)를 붙인 것)
  · 보기만 다시 복원된 같은 문제(P04 교합외상 · P06 악화 질환 · W02 …)는 한 카드(앞면 = 가장 최신 판 · 옛 꼴 = 이전 출제 꼴 — 사용자 10-24 결정 ①)
  · 비슷하지만 묻는 것·답이 다른 것은 별개(관련 문항 rel=은 다음 단계 annot — 짝 목록은 보고 3절)"""
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_rad as P, subject as S
BASE = J.JBX; SUB = 'RAD'
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
NOTYEAR = {'10', '11'}   # 2022 단답 11번(D02) '(10)의 측정은 최대화하고 (11)의 측정은 최소화' = 빈칸 번호(연도 아님)
def tag_years(text):
    """문항 첫머리(답 이전)의 연도 괄호 전부 — (20,21,24) · (20변형,21) · (12변형,21) · (13,14,20변형,21) · (23,24)"""
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        if g.strip() in NOTYEAR: continue
        g2 = re.sub(r'(반짤반탈|변형|짤|탈|년|~)', ' ', g).replace('，', ',')
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
def seclabel(sec): return f'{sec}년 칸' if re.fullmatch(r'20\d\d', sec) else f'{sec} 칸'

# ---------- 2. canonical questions ----------
# 강의별 담당(26 담당 · 26 자료가 없는 강의는 25 담당 — RULES 13 10-26 'LK_PROF = 26 담당')
LK_PROF = {'PER': '허민석', 'JUS': '강주희', 'IMP': '이삼선', 'CTMR': '강주희', 'PTL': '김조은', 'DSR': '이원진', 'FRAC': '이원진', 'DL': '이원진',
           'TRL': '조규동', 'MIX': '허민석', 'TDI': '이원진', 'GAI': '이원진', 'HNA': '허경회', 'HC1': '허경회', 'HC2': '허경회', 'HC3': '허경회',
           'HD1': '허경회', 'HD2': '허경회', 'HD3': '허경회', 'LAW': '허민석'}
H21 = ['25|2023|21', '24|2023|21']   # 묶음 머리 줄(세 카드 공통 다른 판본)
G = [
    # ---- P 치주질환의 영상진단(허민석)
    ('P01', 'PER', 'A', ['25|2024|6']),
    ('P02', 'PER', 'A', ['25|2024|7', '24|2021 객관식|7', '23|2021 객관식|7', '23|2020 객관식|11']),
    ('P03', 'PER', 'A', ['25|2024|8', '25|2023|21-2', '24|2023|21-2', '23|2022 객관식|3-2', '24|2021 객관식|9-2', '23|2021 객관식|9-2'] + H21),
    ('P04', 'PER', 'A', ['25|2024|10', '25|2022 객관식|2', '24|2022 객관식|2', '23|2022 객관식|2', '24|2021 객관식|8', '23|2021 객관식|8', '23|2020 객관식|19']),
    ('P05', 'PER', 'A', ['25|2024|11']),
    ('P06', 'PER', 'A', ['25|2024|11-1', '25|2022 객관식|3', '24|2022 객관식|3', '23|2022 객관식|6', '23|2020 객관식|25']),
    ('P07', 'PER', 'A', ['25|2023|21-1', '24|2023|21-1', '23|2022 객관식|3-1'] + H21),
    ('P08', 'PER', 'A', ['25|2023|21-3', '24|2023|21-3', '23|2022 객관식|5-1', '23|2020 객관식|13'] + H21),
    ('P09', 'PER', 'A', ['25|2023|22', '24|2023|22']),
    ('P10', 'PER', 'A', ['25|2023|23', '24|2023|23']),
    ('P11', 'PER', 'A', ['23|2022 객관식|4']),
    ('P12', 'PER', 'A', ['23|2022 객관식|5']),
    ('P13', 'PER', 'A', ['24|2021 객관식|9-1', '23|2021 객관식|9-1']),
    ('P14', 'PER', 'A', ['23|2020 T/F|3']),
    ('P15', 'PER', 'A', ['23|2020 T/F|7']),
    ('P16', 'PER', 'A', ['23|2020 객관식|9']),
    ('P17', 'PER', 'A', ['23|2020 객관식|10']),
    ('P18', 'PER', 'A', ['23|2020 객관식|12']),
    ('P19', 'PER', 'A', ['23|2020 객관식|14']),
    ('P20', 'PER', 'A', ['23|2020 객관식|17']),
    ('P21', 'PER', 'A', ['23|2020 객관식|18']),
    ('P22', 'PER', 'A', ['23|2020 객관식|20']),
    ('P23', 'PER', 'A', ['23|2020 객관식|21']),
    ('P24', 'PER', 'A', ['23|2020 객관식|22']),
    ('P25', 'PER', 'A', ['23|2020 객관식|23']),
    ('P26', 'PER', 'A', ['23|2020 객관식|24']),
    ('P27', 'PER', 'A', ['23|2020 땡시|6']),   # 치조백선 소실·하악골 뿌옇게 → 부갑상선기능항진증(JB 치주 해설 '전신질환과 치주질환' 표)
    # ---- J 영상검사의 정당화와 최적화(강주희)
    ('J01', 'JUS', 'A', ['25|2024|18']),
    ('J02', 'JUS', 'A', ['25|2023|1', '24|2023|1', '23|2021 단답형|21']),
    ('J03', 'JUS', 'A', ['25|2023|2', '24|2023|2', '23|2021 단답형|19']),
    ('J04', 'JUS', 'A', ['25|2022 객관식|1', '24|2022 객관식|1', '23|2022 객관식|1']),
    ('J05', 'JUS', 'A', ['24|2021 단답형|19', '23|2021 단답형|20']),
    # ---- I 임플란트방사선학(이삼선)
    ('I01', 'IMP', 'A', ['25|2024|1', '24|2021 T/F|5', '23|2021 T/F|5', '23|2020 T/F|1']),   # JB 괄호 (20,21,24) = nasopalatine canal T/F의 2024 복원
    ('I02', 'IMP', 'A', ['25|2024|2']),
    ('I03', 'IMP', 'A', ['25|2024|3', '25|2022 T/F|2', '24|2022 T/F|2', '23|2022 T/F|2', '24|2021 T/F|2', '23|2021 T/F|2', '23|2020 T/F|6']),
    ('I04', 'IMP', 'A', ['25|2024|4', '25|2022 T/F|1-3', '24|2022 T/F|1-3', '23|2022 T/F|1-3']),   # 23판 답 T → 24·25판 F
    ('I05', 'IMP', 'A', ['25|2023|18', '24|2023|18']),   # Parallel view(하악 임플란트 PA) — 강의 연결 불확실(JB 참고 = 교과서 338p 치주)
    ('I06', 'IMP', 'A', ['25|2022 T/F|1-1', '24|2022 T/F|1-1', '23|2022 T/F|1-1', '24|2021 T/F|1-1', '23|2021 T/F|1-1', '23|2020 T/F|4']),
    ('I07', 'IMP', 'A', ['25|2022 T/F|1-2', '24|2022 T/F|1-2', '23|2022 T/F|1-2', '24|2021 T/F|1-2', '23|2021 T/F|1-2']),
    ('I08', 'IMP', 'A', ['25|2022 T/F|3', '24|2022 T/F|3', '23|2022 T/F|3', '24|2021 T/F|6', '23|2021 T/F|6', '23|2020 T/F|5']),
    ('I09', 'IMP', 'A', ['24|2021 T/F|3', '23|2021 T/F|3']),
    ('I10', 'IMP', 'A', ['24|2021 T/F|4', '23|2021 T/F|4']),
    ('I11', 'IMP', 'A', ['23|2020 T/F|2']),
    ('I12', 'IMP', 'A', ['23|2020 T/F|8']),
    ('I13', 'IMP', 'A', ['23|2020 서술형|32']),
    ('I14', 'IMP', 'A', ['23|2020 서술형|33']),
    # ---- C CT 및 MRI의 임상적 이용(강주희)
    ('C01', 'CTMR', 'A', ['25|2023|3', '24|2023|3']),
    ('C02', 'CTMR', 'A', ['25|2023|6', '24|2023|6']),
    ('C03', 'CTMR', 'A', ['25|2022 단답형|9', '24|2022 단답형|9', '23|2022 단답형|13']),
    ('C04', 'CTMR', 'A', ['25|2022 단답형|9-1', '24|2022 단답형|9-1', '23|2022 단답형|13-1', '24|2021 땡시|27', '23|2021 땡시|27']),
    ('C05', 'CTMR', 'A', ['24|2021 단답형|20-1', '23|2021 단답형|22-1']),
    ('C06', 'CTMR', 'A', ['24|2021 단답형|20-2', '23|2021 단답형|22-2']),
    ('C07', 'CTMR', 'A', ['24|2021 단답형|21', '23|2021 단답형|23']),
    # ---- K 치아 주위 방사선투과성·불투과성 병소의 영상감별진단(김조은)
    ('K01', 'PTL', 'A', ['25|2023|7', '24|2023|7']),   # #74,75 proximal caries — 강의 연결 불확실(JB 참고 없음)
    ('K02', 'PTL', 'A', ['25|2023|8', '24|2023|8']),
    ('K03', 'PTL', 'A', ['25|2023|29', '24|2023|29']),
    ('K04', 'PTL', 'A', ['25|2023|30', '24|2023|30']),
    ('K05', 'PTL', 'A', ['25|2022 단답형|10', '24|2022 단답형|10', '23|2022 단답형|14']),
    ('K06', 'PTL', 'A', ['24|2022 땡시|5', '23|2022 땡시|9', '24|2021 땡시|11', '23|2021 땡시|11']),
    ('K07', 'PTL', 'A', ['24|2022 땡시|6', '23|2022 땡시|10', '24|2021 땡시|12', '23|2021 땡시|12']),
    ('K08', 'PTL', 'A', ['24|2022 땡시|7', '23|2022 땡시|11', '24|2021 땡시|10', '23|2021 땡시|10']),
    ('K09', 'PTL', 'A', ['24|2022 땡시|9', '23|2022 땡시|13']),
    ('K10', 'PTL', 'A', ['24|2022 땡시|13', '23|2022 땡시|17']),
    ('K11', 'PTL', 'C', ['24|2022 땡시|20', '23|2022 땡시|26']),   # '허민석교수님)' #14 I&D 뒤 촬영법 — 25 자료에 맞는 허민석 강의 없음 → 치근단 병소 강의에 참고(C)
    ('K12', 'PTL', 'A', ['24|2021 땡시|13', '23|2021 땡시|13']),
    ('K13', 'PTL', 'A', ['24|2021 땡시|14', '23|2021 땡시|14']),
    ('K14', 'PTL', 'A', ['24|2021 땡시|15', '23|2021 땡시|15']),
    ('K15', 'PTL', 'A', ['24|2021 땡시|16', '23|2021 땡시|16']),
    ('K16', 'PTL', 'A', ['24|2021 땡시|17', '23|2021 땡시|17']),
    ('K17', 'PTL', 'A', ['23|2020 땡시|1']),
    ('K18', 'PTL', 'A', ['23|2020 땡시|2']),
    ('K19', 'PTL', 'A', ['23|2020 땡시|3']),   # torus mandibularis — 25 자료 251016 p.30·57·58
    ('K20', 'PTL', 'A', ['23|2020 땡시|4']),
    ('K21', 'PTL', 'A', ['23|2020 땡시|5']),
    ('K22', 'PTL', 'A', ['23|2020 땡시|13']),
    ('K23', 'PTL', 'A', ['23|2020 땡시|14']),
    ('K24', 'PTL', 'A', ['23|2020 땡시|19']),
    # ---- D DSR(이원진)
    ('D01', 'DSR', 'A', ['25|2024|24', '25|2023|17', '24|2023|17', '23|2022 단답형|16', '23|2022 단답형|16-1', '24|2021 단답형|15-1', '23|2021 단답형|15-1', '23|2020 단답형|28']),
    ('D02', 'DSR', 'A', ['25|2022 단답형|11', '24|2022 단답형|11', '23|2022 단답형|15']),
    ('D03', 'DSR', 'A', ['24|2021 단답형|14-1', '23|2021 단답형|14-1', '23|2020 단답형|29']),
    ('D04', 'DSR', 'A', ['24|2021 단답형|14-2', '23|2021 단답형|14-2']),
    ('D05', 'DSR', 'A', ['24|2021 단답형|15-2', '23|2021 단답형|15-2']),
    # ---- F 프랙탈(이원진 — 옛 '디지털 방사선 영상의 응용' · 25 자료 없음)
    ('F01', 'FRAC', 'A', ['25|2024|25']),
    ('F02', 'FRAC', 'A', ['25|2024|25-1', '25|2023|33', '24|2023|33']),
    ('F03', 'FRAC', 'A', ['25|2022 단답형|12', '24|2022 단답형|12', '23|2022 단답형|17']),
    ('F04', 'FRAC', 'A', ['24|2021 단답형|16', '23|2021 단답형|16', '23|2020 단답형|27']),
    ('F05', 'FRAC', 'A', ['23|2020 단답형|31']),
    # ---- L Deep learning(이원진)
    ('L01', 'DL', 'A', ['25|2024|27']),
    # ---- V 3차원영상(이원진)
    ('V01', 'TDI', 'A', ['24|2021 단답형|17', '23|2021 단답형|17']),
    ('V02', 'TDI', 'A', ['24|2021 단답형|18', '23|2021 단답형|18', '23|2020 단답형|30']),
    # ---- R 치아와 관련 없는 방사선투과성 병소(26 조규동 · 22~25 강주희 · 21 허민석)
    ('R01', 'TRL', 'A', ['25|2024|31']),
    ('R02', 'TRL', 'A', ['25|2023|4', '24|2023|4']),
    ('R03', 'TRL', 'A', ['25|2023|5', '24|2023|5']),
    ('R04', 'TRL', 'A', ['25|2023|32', '24|2023|32']),
    ('R05', 'TRL', 'A', ['24|2022 땡시|8', '23|2022 땡시|12']),
    ('R06', 'TRL', 'A', ['24|2022 땡시|10', '23|2022 땡시|14']),
    ('R07', 'TRL', 'A', ['24|2022 땡시|11', '23|2022 땡시|15']),
    ('R08', 'TRL', 'A', ['24|2022 땡시|12', '23|2022 땡시|16']),
    ('R09', 'TRL', 'A', ['24|2022 땡시|16', '23|2022 땡시|20']),
    ('R10', 'TRL', 'A', ['24|2022 땡시|17', '23|2022 땡시|22']),
    ('R11', 'TRL', 'A', ['24|2021 땡시|18', '23|2021 땡시|18']),
    ('R12', 'TRL', 'A', ['24|2021 땡시|20', '23|2021 땡시|20']),
    ('R13', 'TRL', 'A', ['24|2021 땡시|21', '23|2021 땡시|21']),
    ('R14', 'TRL', 'A', ['24|2021 땡시|22', '23|2021 땡시|22']),
    ('R15', 'TRL', 'A', ['24|2021 땡시|23', '23|2021 땡시|23']),
    ('R16', 'TRL', 'A', ['24|2021 땡시|24', '23|2021 땡시|24']),
    ('R17', 'TRL', 'A', ['24|2021 땡시|25', '23|2021 땡시|25']),
    # ---- M 치아와 관련이 없는 혼합성/방사선불투과성 병소(허민석)
    ('M01', 'MIX', 'A', ['25|2023|19', '24|2023|19', '23|2022 땡시|21', '23|2022 땡시|21-1']),
    ('M02', 'MIX', 'A', ['25|2023|20', '24|2023|20', '23|2022 땡시|23']),
    ('M03', 'MIX', 'A', ['25|2023|31', '24|2023|31']),
    ('M04', 'MIX', 'A', ['24|2022 땡시|18', '23|2022 땡시|22+']),   # osteopetrosis — 23판은 22번 뒤 번호 없이 붙어 있던 것(parse UNNUM '22+' · 11-16 JBV) · 25 자료 251113 p.39
    ('M05', 'MIX', 'A', ['24|2022 땡시|19', '23|2022 땡시|24']),   # 44p 그림 — 23판 답 aneurysmal bone cyst → 24판 osteochondromatosis
    ('M06', 'MIX', 'A', ['23|2022 땡시|25']),
    ('M07', 'MIX', 'A', ['24|2021 땡시|19', '23|2021 땡시|19']),
    ('M08', 'MIX', 'A', ['23|2020 땡시|7']),
    ('M09', 'MIX', 'A', ['23|2020 땡시|17']),
    # ---- H 두경부 영상해부학 — CT 정상 구조물(허경회) · 증례 땡시(옛 '영상해부학' 케이스 — 25 증례 파일로 옮길지는 annot 단계)
    ('H01', 'HNA', 'A', ['25|2023|9', '24|2023|9', '23|2022 땡시|1', '24|2021 땡시|3', '23|2021 땡시|3', '23|2020 땡시|9']),
    ('H02', 'HNA', 'A', ['25|2023|10', '24|2023|10']),
    ('H03', 'HNA', 'A', ['25|2023|11', '24|2023|11']),
    ('H04', 'HNA', 'A', ['25|2023|12', '24|2023|12', '23|2022 땡시|2', '24|2021 땡시|4', '23|2021 땡시|4', '23|2020 땡시|11']),
    ('H05', 'HNA', 'A', ['25|2023|13', '24|2023|13', '23|2022 땡시|3', '24|2021 땡시|7', '23|2021 땡시|7']),
    ('H06', 'HNA', 'A', ['25|2023|14', '24|2023|14', '23|2022 땡시|4', '24|2021 땡시|6', '23|2021 땡시|6', '23|2020 땡시|15']),
    ('H07', 'HNA', 'A', ['25|2023|15', '24|2023|15']),
    ('H08', 'HNA', 'A', ['25|2023|16', '24|2023|16']),
    ('H09', 'HNA', 'A', ['24|2022 땡시|1', '23|2022 땡시|5', '24|2021 땡시|5', '23|2021 땡시|5']),
    ('H10', 'HNA', 'A', ['24|2022 땡시|2', '23|2022 땡시|6', '24|2021 땡시|8', '23|2021 땡시|8']),
    ('H11', 'HNA', 'A', ['24|2022 땡시|3', '23|2022 땡시|7', '24|2021 땡시|9', '23|2021 땡시|9']),
    ('H12', 'HNA', 'A', ['24|2022 땡시|4', '23|2022 땡시|8']),
    ('H13', 'HNA', 'A', ['24|2022 땡시|14', '23|2022 땡시|18']),
    ('H14', 'HNA', 'A', ['24|2022 땡시|15', '23|2022 땡시|19']),
    ('H15', 'HNA', 'A', ['24|2021 땡시|1', '23|2021 땡시|1']),
    ('H16', 'HNA', 'A', ['24|2021 땡시|2', '23|2021 땡시|2']),
    ('H17', 'HNA', 'A', ['24|2021 땡시|26', '23|2021 땡시|26']),
    ('H18', 'HNA', 'A', ['23|2020 땡시|8']),
    ('H19', 'HNA', 'A', ['23|2020 땡시|10']),
    ('H20', 'HNA', 'A', ['23|2020 땡시|12']),
    ('H21', 'HNA', 'A', ['23|2020 땡시|16']),
    ('H22', 'HNA', 'A', ['23|2020 땡시|18']),
    # ---- X 허경회 증례(25 파일마다 강의 — JB 참고 = 그 증례 파일)
    ('X01', 'HC1', 'A', ['25|2024|21']),
    ('X02', 'HC2', 'A', ['25|2024|22']),
    # ---- W 방사선안전관리법규 및 정도관리(허민석)
    ('W01', 'LAW', 'A', ['25|2024|5']),
    ('W02', 'LAW', 'A', ['25|2024|13', '25|2022 객관식|5', '24|2022 객관식|5', '23|2022 객관식|8', '24|2021 객관식|10', '23|2021 객관식|10']),
    ('W03', 'LAW', 'A', ['25|2024|14', '25|2022 객관식|6', '24|2022 객관식|6', '23|2022 객관식|9']),
    ('W04', 'LAW', 'A', ['25|2024|16']),
    ('W05', 'LAW', 'A', ['25|2024|16-1', '25|2022 객관식|7', '24|2022 객관식|7', '23|2022 객관식|11', '24|2021 객관식|11', '23|2021 객관식|11']),
    ('W06', 'LAW', 'A', ['25|2024|17', '25|2022 객관식|8', '24|2022 객관식|8', '23|2022 객관식|11-1', '24|2021 객관식|12', '23|2021 객관식|12']),
    ('W07', 'LAW', 'A', ['25|2024|20']),
    ('W08', 'LAW', 'A', ['25|2023|24', '24|2023|24']),
    ('W09', 'LAW', 'A', ['25|2023|25', '24|2023|25']),
    ('W10', 'LAW', 'A', ['25|2023|26', '24|2023|26']),
    ('W11', 'LAW', 'A', ['25|2023|27', '24|2023|27']),
    ('W12', 'LAW', 'A', ['25|2023|28', '24|2023|28', '23|2022 객관식|12-1']),
    ('W13', 'LAW', 'A', ['25|2022 객관식|4', '24|2022 객관식|4', '23|2022 객관식|7', '23|2020 객관식|26']),
    ('W14', 'LAW', 'A', ['23|2022 객관식|10']),
    ('W15', 'LAW', 'A', ['23|2022 객관식|10-1', '23|2020 객관식|16']),
    ('W16', 'LAW', 'A', ['23|2022 객관식|12']),
    ('W17', 'LAW', 'A', ['24|2021 객관식|13', '23|2021 객관식|13']),
    ('W18', 'LAW', 'A', ['23|2020 객관식|15']),
] + [('Z%02d' % n, '', 'A', [f'25|2024|{n}']) for n in (9, 12, 15, 19, 23, 26, 28, 29, 30)]   # 25판 2024 칸 미복원·중복복원 자리(build4가 숨김 — 기출 대장에만)
HIDE = {'Z19'}   # '19. 중복복원' — build4 미복원 규칙(_HIDE)에 안 걸려 hide=1을 넣어 줌(어느 문항의 중복인지 JB에 없음)
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
    yrs = set(ty) | ({secyear(sec)} if secyear(sec) else set())
    for (e2, s2, n2) in OTHER.get(cid, []):
        x2 = find(e2, s2, n2); assert x2, (cid, e2, s2, n2)
        if secyear(s2): yrs.add(secyear(s2))
        yrs |= tag_years(x2['text'])[0]
    short = re.sub(r'^\s*\d{1,2}(\s*-\s*\d{1,2})?\s*[.．]?\s*', '', t.split('\n')[0]).strip()
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
    q['fig'] = bool(re.search(r'사진|영상|그림|땡시', ' '.join(q['text'].split('\n')[:3]))) or q['sec'].endswith('땡시')
for cid in HIDE:   # 미복원 자리(중복복원) — annot에 hide=0을 적으면 그대로 보임
    ANN.setdefault(cid, {}).setdefault('hide', '1')

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
MENT = {'25': ment('25', [1, 2]), '24': ment('24', [1, 2]), '23': ment('23', [1, 2, 3])}   # 판 머리 멘트·수업 표 쪽
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
        for q in Q: print(f"{q['id']} {q['lk']:5} {q['tier']} {str(q['yrs']):30} {q['jbtag'][:34]:34} {q['short'][:44]}")
