import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
"""IMPL4 치과임플란트학(4Q) — JB 23·24·25판 → 정식 문항(Q)·같은 문제의 다른 판본(other)·대조표(LEDGER) (2026-11-16 JB 단계 · work/IMPL4/jb/R_JB_IMPL4.md)
id = 강의 글자 + 번호(강의 안에서 최근 해 먼저 · jb_lock.json이 잠금 — 번호 당기기 금지):
  A 위축된 상악 구치부 증강(AUG 명훈 — 26) · C 임플란트 식립의 합병증과 대책(COMP 서미현) · E 완전 무치악 환자의 보철수복(EDEN 김명주)
  S Soft tissue management(SOFT 김성태 ← 구영) · P Peri-implantitis(PERI 구기태) · R 임플란트의 보철적 예후(PROG 박지만) · G Implant surgery(SURG 설양조)
  X 이젠 안 들어오시는 교수님 범위(PAST — 23판 '[이젠 안들어오시는 교수님 범위]' 중 지금 강의에 같은 내용이 없는 것 · tier C)
  Z 미복원 자리(25판 2024 칸 7·11·12·16 — build4가 숨김, 기출 대장에만 · 강의는 바로 앞 문항의 강의 — 추정 아님, 자리만)
묶음 G = (id, 강의 키, tier, [블록 '판|칸|번호' …]) — 첫 블록 = 정식(가장 최신 판 · 같은 판이면 가장 최근 칸), 나머지 = 같은 문제의 다른 판본(OTHER)
  · 판 사이 같은 문제 = 문제 글이 같거나(괄호만 다름) JB가 같은 문제라고 적은 것(25판 '중복 문항은 모두 삭제' 뒤 괄호 '(23’,24’)'·'(22’,23’,24’)'로 합친 것 · '4~5. 2번과 중복 복원')
  · 비슷하지만 묻는 것·답이 다른 것은 별개(관련 문항 rel=은 다음 단계 annot — 짝 목록은 보고 3절):
    C01 항응고제 4가지(22~24) ↔ C07 주의할 약물(=항응고제, 20 · 21년도 답) · C01 ↔ C04 NOAC · R01 기계적 합병증(24) ↔ R03 고정성·가철성 기계적 합병증(23) ↔ R04 합병증의 종류(20)
    G01 tap·lance·Lindemann 3개(24 — 괄호 22’,23’) ↔ G05 Lindemann 하나(23·22·20·18) · G03 countersink · P06 biological problem ↔ P07 local factor ↔ P05 기여 요인
    E03 최소 개수 표 빈칸 ↔ E06 OD vs fixed 표 · E01 ↔ E02(25판 해설 '24년 2번 문항과 중복 복원의 가능성') · C03 mucositis 빈칸(서미현) ↔ P01 mucositis 차이(구기태)"""
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_impl4 as P, subject as S
BASE = J.JBX; SUB = 'IMPL4'
NPAGES = dict(P.NP)   # 판 → 쪽 수 {'25': 12, '24': 14, '23': 12}
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
NOISE = r"(반짤반탈|짤|탈|년도|년|’|‘|'|`|~)"
def tag_years(text):
    """문항 첫머리(답 이전)의 연도 괄호 전부 — (탈)은 해 없음 · (22’,23’,24’) · (23’, 24’) · (22,20,19) · (22,19, 18) · (20’, \\n19’)(stem_of가 이어 붙임) · (22')
    연도 아닌 괄호 = (사진 임의 복원) · (유사 문제로 같이 풀이) · (7점) · (★★★★★) · (NEW) · (최소개수 …) · (복원 원문 문장: …) · (10문제였는데 …)"""
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = re.sub(NOISE, ' ', g).replace('，', ',').strip(' ,')
        if not re.search(r'\d', g2) or not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*,\s*(20\d\d|\d\d)?)*\s*,?\s*', g2): continue
        vs = {int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)}
        if not vs or not all(9 <= v <= 26 for v in vs): continue
        ys |= vs; raw.append('(' + g.strip() + ')')
    return ys, raw
def secyear(sec): m = re.fullmatch(r'(20\d\d)', sec or ''); return int(m.group(1)) % 100 if m else None
def seclabel(sec, past=False): return f'{sec}년 칸' + (' · 이젠 안들어오시는 교수님 범위' if past else '')
BMAP = {}
for ed in NPAGES:
    for x in blocks[ed]:
        k_ = (ed, x['sec'], str(x['num'])); assert k_ not in BMAP, k_; BMAP[k_] = x
def find(ed, sec, num):
    return BMAP.get((ed, str(sec), str(num)))

# ---------- 2. canonical questions ----------
# 강의별 담당(26 담당 · 26 자료가 없는 강의는 25 담당 — RULES 13 10-26 'LK_PROF = 26 담당') · PAST는 문항마다 QPROF
LK_PROF = {'AUG': '명훈', 'COMP': '서미현', 'EDEN': '김명주', 'SOFT': '김성태', 'PERI': '구기태', 'PROG': '박지만', 'SURG': '설양조', 'PAST': ''}
QPROF = {'P06': '허성주', 'P07': '허성주', 'R04': '허성주', 'A02': '이종호', 'A03': '이종호',   # tier C(이젠 안들어오시는 교수님 범위 · 참고 파일 교수) — 같은 내용이 있는 지금 강의에 lk
         'X01': '한중석', 'X02': '한중석', 'X03': '허성주', 'X04': '한중석', 'X05': '이종호', 'X06': '권호범'}
G = [
    # ---- A 위축된 상악 구치부 증강(명훈 — 26) · 명훈 JB 문항은 수업 중 알려 준 문제 하나(출제 아님 — kind=예고) + 이종호 자가골 채취 2문항(26 p.40-45 Block bone graft 'Symphysis·Ramus' — tier C)
    ('A01', 'AUG', 'A', ['25|2023|추가', '24|2023|추가']),   # "추가) 명훈 교수님 언급 문제. Alveolar ridge atrophy의 극복 방안" — 24년 멘트 "문제 하나를 알려주셔 23JB 끝부분에 실었으나 3Q 때에도 출제 하지 않으셨습니다"
    ('A02', 'AUG', 'C', ['23|2020|11']), ('A03', 'AUG', 'C', ['23|2020|12']),   # 자가골 채취 부위·장단점 · 하악지 골 채취 시 주의사항(참고 211102_이종호_인공치 식립과 뼈이식)
    # ---- C 임플란트 식립의 합병증과 대책(서미현)
    ('C01', 'COMP', 'A', ['25|2024|8', '24|2023|13', '24|2022|1', '23|2022|1']),   # 항응고제 4가지 이상 '(23’,24’)' — 25판이 2023 칸 13번을 지우고 합침 · 2022 칸 1번 같은 글
    ('C02', 'COMP', 'A', ['25|2024|9', '24|2023|12']),   # 상악동 천공 사진 처치법 '(23’, 24’)'
    ('C03', 'COMP', 'A', ['25|2024|10']),   # peri-implant mucositis 빈칸(탈) — 참고 251111_서미현 p.48
    ('C04', 'COMP', 'A', ['25|2023|8', '24|2023|10']),   # NOAC 예시
    ('C05', 'COMP', 'A', ['25|2022|1', '24|2022|2', '23|2022|2', '24|2022|4-5', '23|2022|4-5', '24|2020|1', '23|2020|1']),   # 수술 도중 합병증 (22,20,19) · '4~5. 2번과 중복 복원' · 2020 칸 1번 (20’,19’)
    ('C06', 'COMP', 'A', ['24|2021|7', '23|2021|7']),   # 견치 부위 동맥(sublingual artery)
    ('C07', 'COMP', 'A', ['24|2020|2', '23|2020|2']),   # 주의할 약물(=항응고제 4가지 이상) — '(21년도 답)' Coumadin·Pradaxa·Xarelto·Eliquis(C01과 답이 달라 별개)
    # ---- E 완전 무치악 환자의 보철수복(김명주)
    ('E01', 'EDEN', 'A', ['25|2024|1']), ('E02', 'EDEN', 'A', ['25|2024|2']),   # 둘 다 (탈) — E01 해설 "24년 2번 문항과 중복 복원의 가능성"(별개로 둠)
    ('E03', 'EDEN', 'A', ['25|2024|3', '24|2023|5', '24|2021|6', '23|2021|6']),   # 최소 개수 표 빈칸 '(22’,23’,24’)' · 24판 2023 칸 '(21’, 22’)' · 2021 칸 6번(같은 표 사진)
    ('E04', 'EDEN', 'A', ['25|2024|4', '24|2023|11', '24|2022|11', '23|2022|11']),   # 고정성보다 가철성 적응증 '(22’,23’,24’)'
    ('E05', 'EDEN', 'A', ['25|2023|6', '24|2023|7']),   # 옳은 선지(복원 불충분 — 답 '1?')
    ('E06', 'EDEN', 'A', ['25|2022|4', '24|2022|10', '23|2022|10']),   # od vs fixed prosthesis 표
    # ---- S Soft tissue management(김성태 ← 구영 — 이 강의 기출은 구영 교수님 출제)
    ('S01', 'SOFT', 'A', ['25|2023|5', '24|2023|6', '24|2020|3', '23|2020|3']),   # Clinical rationale of peri-implant attached soft tissue(23 · 2020 칸 3번)
    ('S02', 'SOFT', 'A', ['25|2023|7', '24|2023|9']),   # 치주조직의 구분을 그리고 설명(복원 불충분 — 해설 그림)
    ('S03', 'SOFT', 'A', ['25|2022|2', '24|2022|3', '23|2022|3', '24|2021|1', '23|2021|1']),   # 정상 치아 vs 임플란트 주변 조직 차이 (22,21,19)
    # ---- P Peri-implantitis(구기태)
    ('P01', 'PERI', 'A', ['25|2024|13']), ('P02', 'PERI', 'A', ['25|2024|14', '24|2022|9', '23|2022|9']),   # P02 임상적 지표 '(22’,24’)' = 2022 칸 9번 '5년지났고 base data 없을 때 … 임상적 기준'(같은 답)
    ('P03', 'PERI', 'A', ['25|2024|15']),   # 그림 빈칸 Transmucosal(탈)
    ('P04', 'PERI', 'A', ['24|2021|2', '23|2021|2']),   # 진단 방법 5가지 중 2개 빈칸 (21,19) — 참고 191203_이용무 · "22’ 학습부: 올해는 이 내용을 구기태 교수님께서 다루셨습니다"
    ('P05', 'PERI', 'A', ['24|2021|3', '23|2021|3', '24|2020|4', '23|2020|4']),   # 기여 요인 (21,20) · 2020 칸 '(NEW)'
    ('P06', 'PERI', 'C', ['24|2021|5', '23|2021|5', '24|2020|5', '23|2020|5']),   # (★★★★★) biological problem(local, systemic) (21,20,19) — 참고 '(20’ 필기) 201208_허성주'(tier C · 주제 = 구기태 기여 요인)
    ('P07', 'PERI', 'C', ['23|2022|16']),   # local factor 7개 — '[이젠 안들어오시는 교수님 범위]' 허성주(P06과 같은 표 답 · 묻는 것이 달라 별개)
    # ---- R 임플란트의 보철적 예후(박지만)
    ('R01', 'PROG', 'A', ['25|2024|5']),   # 보철물 기계적 합병증 원인·해결·예방(참고 241203_박지만 p.9-15)
    ('R02', 'PROG', 'A', ['25|2024|6']),   # 나사풀림(탈) — JB 해설 '조준호 교수님 수업 … 박지만 교수님의 강의자료에서도 해당되는 내용을 찾을 수 없습니다'(강의 연결 확인 필요 — 보고 5절)
    ('R03', 'PROG', 'A', ['25|2023|1-2', '24|2023|1-2']),   # 고정성·가철성 보철물 기계적 합병증(1·2번 같이 풀이)
    ('R04', 'PROG', 'C', ['23|2020|10']),   # (★★★★★) 임플란트 합병증의 종류 — '[이젠 …]' 참고 201208_허성주 p.4 · 같은 6가지 목록이 24·25판 2023 칸 1-2번 해설 '박지만 교수님 수업 … Types of complication'
    # ---- G Implant surgery(설양조)
    ('G01', 'SURG', 'A', ['25|2024|17']),   # tap·lance·Lindemann 이름과 목적 '(22’,23’,24’)'(25판이 2023·2022 칸 Lindemann 문항을 지우고 괄호로 합침 — 묻는 기구가 달라 G05와 별개)
    ('G02', 'SURG', 'A', ['25|2024|18']),   # stability 그래프 빈칸(탈)
    ('G03', 'SURG', 'A', ['25|2023|3', '24|2023|3']),   # countersink drill
    ('G04', 'SURG', 'A', ['25|2023|4', '24|2023|4', '24|2022|7', '23|2022|7']),   # anatomic limitation 상악·하악
    ('G05', 'SURG', 'A', ['24|2023|8', '24|2022|8', '23|2022|8', '24|2020|6', '23|2020|6']),   # Lindemann drill 이름·용도 (22',20',18') · (22,20, 18) · (20’, 18’)
    ('G06', 'SURG', 'A', ['25|2022|3', '24|2022|6', '23|2022|6', '24|2021|4', '23|2021|4']),   # Pilot drill 용도 (22,19, 18) · (19, 18)
    # ---- X 이젠 안 들어오시는 교수님 범위(23판만 · 24판부터 뺌) — 지금 강의에 같은 내용 없음(11-16 글층·OCR 검색 — 작성 담당이 다시 볼 것)
    ('X01', 'PAST', 'C', ['23|2022|12', '23|2020|9']),   # Single implant 고려사항(한중석 211012 p.21)
    ('X02', 'PAST', 'C', ['23|2022|13-14', '23|2020|8']),   # 보철물의 고정 방식 및 적응증(한중석 p.15)
    ('X03', 'PAST', 'C', ['23|2022|15']),   # Long-term implant survival 10-16 years 수치(허성주 221206 장기적 예후를 고려한 보철치료)
    ('X04', 'PAST', 'C', ['23|2020|7']),   # (NEW) 임플란트 지대주의 종류(한중석 p.9)
    ('X05', 'PAST', 'C', ['23|2020|13']),   # 2가지 bone healing(이종호 210928 골이식 생리 및 원리)
    ('X06', 'PAST', 'C', ['23|2020|14']),   # 권호범 교수님 논문 빈칸빵(10문제 중 9개 복원)
    # ---- Z 미복원 자리(build4 숨김 — 기출 대장 '미복원' · 강의 = 바로 앞 문항의 강의)
    ('Z01', 'PROG', 'A', ['25|2024|7']), ('Z02', 'COMP', 'A', ['25|2024|11']), ('Z03', 'COMP', 'A', ['25|2024|12']), ('Z04', 'PERI', 'A', ['25|2024|16']),
]
KIND = {'A01': '예고'}   # 수업 중 알려 준 문제(출제 아님 — 배지 '수업 예고 문항' · 출제 연도·집계에서 뺌 · 3Q IMPL R13·R14 꼴) — annot에 kind=를 적으면 그것이 이김
HIDE = set()   # 자리 줄은 모두 'N. 미복원'(build4 미복원 규칙이 숨김) · '4~5. 2번과 중복 복원'은 C05의 다른 판본
FIGQ = {'C02', 'E03', 'E06', 'S02', 'P03', 'G01', 'G02', 'G03', 'G05'}   # 그림·표 문항(보고 3절 — 그림 조각은 다음 단계 JF)
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
assert all(LK[c] in LECMAP for c in LK), '없는 강의 키'
def blk_years(ed, sec, x):
    """블록 하나의 출제 해 = 괄호 해 ∪ 실린 칸 해"""
    return set(tag_years(x['text'])[0]) | ({secyear(sec)} if secyear(sec) else set())
CROPS = {}
Q = []
for cid, ed, sec, num in CANON:
    x = find(ed, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t)
    yrs = blk_years(ed, sec, x)
    for (e2, s2, n2) in OTHER.get(cid, []):
        yrs |= blk_years(e2, s2, find(e2, s2, n2))
    short = re.sub(r'^\s*(\d{1,2}(\s*[-~]\s*\d{1,2})?\s*[.．]|추가\s*\))\s*', '', t.split('\n')[0]).strip()
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': TIER[cid], 'prof': QPROF.get(cid, LK_PROF[LK[cid]]),
              'src': f'JB {ed}판 · {seclabel(sec, x.get("past"))} {num}번', 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True),
              'secy': secyear(sec), 'tal': bool(re.search(r'\(\s*탈\s*\)', stem_of(t))), 'pick': ''})

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
for cid in HIDE:   # 자리 줄 숨김 강제(annot에 hide=0을 적으면 그대로 보임)
    ANN.setdefault(cid, {}).setdefault('hide', '1')
for cid, k_ in KIND.items():   # kind=예고(출제 아님) — annot에 kind=를 적으면 그것이 이김(build4 _ax가 ANN을 읽음)
    ANN.setdefault(cid, {}).setdefault('kind', k_)

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
MENT = {ed: ment(ed, [1]) for ed in NPAGES}   # 판 머리 멘트 + 수업 표(셋 다 p.1)
if __name__ == '__main__':
    print('Q', len(Q), '블록', sum(len(b) for b in blocks.values()), '숨김 자리 Z', sum(1 for q in Q if q['id'].startswith('Z')))
    for q in Q: print(q['id'], q['tier'], q['lk'], q['prof'], q['yrs'], q['jbtag'], '|', q['short'][:40], '| other', len(q['other']))
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [(r['ed'], r['sec'], r['num'], r['first'][:28]) for r in LEDGER if r['st'] == 'ref'])
    for e_ in NPAGES: print(f'{e_}판 블록', len(blocks[e_]), {s_: sum(1 for r in LEDGER if r['ed'] == e_ and r['st'] == s_) for s_ in ('card', 'dup', 'ref')})
