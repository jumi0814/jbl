import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""PHARM4 JB 분해(11-16 Q4 JB 단계) — parse(ed, n) → 블록 [{'ed','topic','sec','prof','num','pg','pg2','lines','lp'}]
판(ed): '25'·'24'·'23' = 4Q JB(work/jb/PHARM4_20YY — 판 해 = 파일 해 · 최신 시험 해 = 판 해 - 1)
        '25q3'·'24q3'·'23q3' = 3Q JB(work/jb/PHARM_20YY)의 <살균제와 소독제> 칸(26부터 4Q 강의 — 사용자 11-16 메모 ①)
        + 23q3의 [성호르몬과 길항제] 칸(23까지 3Q 강의 → 24부터 4Q — 3Q 사이트는 '4Q로 이전되어 제외'로 안 실음 → 이 과목에)
구조 = 강의 머리 '<항불안제>'·'[성호르몬과 길항제]' + 연도 칸 '[2024 년 - Pf. 이윤실]'·'<2022년>'·'[2023년- (예정)]'·'<2022년 조영단 교수님>'
문항 = 칸 안 'N. …'(직전 번호 + 1 · 앞 문항의 답·해설·참고 줄 뒤 · 앞 문항이 'n번 중복' 가리킴이면 바로) · 'N-1.'(DS 2021 Iodine 4-1·4-2 = 블록 '4' 하나 — 3Q 분해와 같게) · 'N-M.'(앞 번호의 딸린 문항 — 23q3 성호르몬 2020 '9-1.' = 블록 '9-1')
해설 안 번호 줄(RULES 0-1) = NOTQ · 판 머리 표기 잘못 = SECFIX(보고 work/PHARM4/jb/R_JB_PHARM4.md 1절)"""
import re, json
BASE = J.JBX
DIRS = {'25': 'PHARM4_2025', '24': 'PHARM4_2024', '23': 'PHARM4_2023', '25q3': 'PHARM_2025', '24q3': 'PHARM_2024', '23q3': 'PHARM_2023'}
def jbdir(ed): return f'{BASE}{DIRS[ed]}'
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        t = rd(f'{jbdir(ed)}/{i}.txt'); first = True
        for l in t.split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue   # 쪽 번호
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
TOPICS = {'항불안제': 'AX', '구강건조증 치료제': 'XE', '진정수면제': 'SD', '국소마취제': 'LA', '약물상호작용': 'DI', '성호르몬과 길항제': 'SX',
          '치과약물유전학': 'PG', '노인 및 임산부/수유부의 약물치료': 'GR', '살균제와 소독제': 'DS',
          '금연 요법 및 처방전': '-', '보톡스': '-', '급성/만성통증 치료제': '-', '지혈제와 수렴제': '-'}   # '-' = 3Q JB의 다른 강의(이 과목 아님)
TOPIC = re.compile(r'^\s*[<\[]\s*(' + '|'.join(re.escape(k) for k in TOPICS) + r')\s*[>\]]\s*$')
Q3KEEP = {'25q3': {'DS'}, '24q3': {'DS'}, '23q3': {'DS', 'SX'}}   # 3Q JB에서 가져오는 강의 칸(3Q 24·25판 <구강건조증 치료제>는 3Q 강의라 뺌)
YEAR = re.compile(r'^\s*[\[<]\s*(20\d\d)\s*년\s*(?:도)?\s*(이전)?\s*(?:\(예정\))?\s*(?:[-–]\s*(?:Pf\.?\s*([가-힣]{2,3})|\(예정\)))?\s*(?:([가-힣]{2,3})\s*교수님)?\s*[\]>]\s*$')
# 판 머리 연도 표기 잘못 — (판, 강의, 머리 쪽): 바른 해
#  23판 <치과약물유전학> p.26 '[2021년 – Pf. 백정화]' = 2022 칸(같은 판 p.27에 진짜 '[2021년 – Pf. 백정화]'가 또 있음 · 24판 p.25 '[2022년 – Pf. 백정화]'·25판 p.20 '[2022년 – Pf. 백정화]'에 같은 문항 4개·3개 · 해설 참고 파일 221201_백정화 = 2022 수업)
SECFIX = {('23', 'PG', 26): '2022'}
QL = re.compile(r'^(\d{1,2})\s*[.．]\s*(\S.*)?$')
SUBL = re.compile(r'^(\d{1,2})\s*-\s*(\d)\s*[.．]\s*\S')
ANSZ = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$|^\s*해설\s*[:：)]?|^\s*참고\s*[:：]')
# 해설·답 안의 번호 줄(직전 번호 + 1이라 문항처럼 보이는 것 — RULES 0-1) — (판, 강의, 칸, 번호 줄 쪽, 줄 앞글)
NOTQ = {('25', 'LA', '2024', 10, '5. ➢Mepivacaine'), ('24', 'LA', '2023', 11, '5. ➢Mepivacaine'),   # 국소마취제 4번 해설 '1. procaine … 5. ➢Mepivacaine, Prilocaine (구매가 어려움)'
        ('24', 'SX', '2021', 17, '2. Increased hematocrit'), ('23q3', 'SX', '2021', 47, '2. Increased hematocrit')}   # 성호르몬 2021 1번 해설 'adverse effects of testosterone 1. Acne … 2. Increased hematocrit'
def notq(ed, topic, sec, pg, s): return any(k[:4] == (ed, topic, sec, pg) and s.startswith(k[4]) for k in NOTQ)
# 칸 머리와 1번 사이에 놓인 '여러 문항 공통 보기'(11-16 독립 검수 V_JB_PHARM4 — 그 전엔 버려져 카드에 보기가 없었음)
#  약물상호작용 2022 칸 '<1-10번 문제를 위한 복원된 보기>' + 약물 쌍 6줄(25판 p.13 · 24판 p.21 · 23판 p.21 — 굵은 글 = 문제 글) → 그 칸 블록마다 문제 글 뒤·첫 '답' 줄 앞에 원문 그대로
#  (25판 진정수면제 2024 칸 머리 아래 '* 기본적으로 <보기> 여러개가 주어지고 …'는 학습부 설명(보통 글)이라 넣지 않음 — 보고 V_JB_PHARM4)
SHARED_PRE = {('25', 'DI', '2022'), ('24', 'DI', '2022'), ('23', 'DI', '2022')}
def parse(ed, n):
    L = load(ed, n); blocks = []; cur = None; topic = None; sec = None; prof = ''; hdr = ''; last = 0; inans = False; pre = {}
    keep = Q3KEEP.get(ed)
    for idx, (pg, l) in enumerate(L):
        s = l.strip()
        m = TOPIC.match(s)
        if m:
            topic = TOPICS[m.group(1)]; sec = None; cur = None; last = 0; inans = False; prof = ''; hdr = ''
            if topic == '-' or (keep is not None and topic not in keep) or (keep is None and topic == 'DS'): topic = None
            continue
        m = YEAR.match(s)
        if m and topic:
            sec = 'pre' if m.group(2) else SECFIX.get((ed, topic, pg), m.group(1)); prof = m.group(3) or m.group(4) or ''; hdr = s
            cur = None; last = 0; inans = False; continue
        if not topic or not sec or sec == 'pre': continue
        ms = SUBL.match(s)
        if ms and cur is not None and inans:
            a, b = int(ms.group(1)), ms.group(2)
            if a == last + 1:   # 'N-1.'로 시작하는 묶음 = 블록 N(3Q 분해 CUT과 같은 블록)
                cur = {'ed': ed, 'topic': topic, 'sec': sec, 'prof': prof, 'hdr': hdr, 'num': str(a), 'pg': pg, 'pg2': pg, 'lines': [l], 'lp': [pg], 'grp': True}
                blocks.append(cur); inans = False; last = a; continue
            if a == last and not cur.get('grp'):   # 앞 문항의 딸린 문항(23q3 SX 2020 '9-1.')
                cur = {'ed': ed, 'topic': topic, 'sec': sec, 'prof': prof, 'hdr': hdr, 'num': f'{a}-{b}', 'pg': pg, 'pg2': pg, 'lines': [l], 'lp': [pg], 'sub': True}
                blocks.append(cur); inans = False; continue
        mq = QL.match(s)
        if mq:
            nn = int(mq.group(1))
            ptr = cur is not None and re.search(r'중복', cur['lines'][0]) and len(cur['lines']) <= 2
            if nn == last + 1 and (cur is None or inans or ptr) and not notq(ed, topic, sec, pg, s):
                cur = {'ed': ed, 'topic': topic, 'sec': sec, 'prof': prof, 'hdr': hdr, 'num': str(nn), 'pg': pg, 'pg2': pg, 'lines': [l], 'lp': [pg]}
                blocks.append(cur); inans = False; last = nn; continue
        if cur is not None:
            cur['lines'].append(l); cur['lp'].append(pg); cur['pg2'] = pg
            if ANSZ.match(s): inans = True
        elif s and (ed, topic, sec) in SHARED_PRE: pre.setdefault((topic, sec), []).append((pg, l))   # 칸 머리 ~ 1번 사이 공통 보기
    for x in blocks:   # 블록 끝의 빈 줄 정리(글자는 그대로)
        while len(x['lines']) > 1 and not x['lines'][-1].strip(): x['lines'].pop(); x['lp'].pop()
        x['pg2'] = x['lp'][-1]
        pl = pre.get((x['topic'], x['sec']))
        if pl:   # 공통 보기를 문제 글 뒤(첫 '답' 줄 앞)에 — 글자 그대로 · 줄마다 앞에 강제 줄바꿈 표시 U+2063(reflow.HARD — 보기 쌍 6줄이 한 줄로 이어지지 않게 · 화면·qhash·글자 비교에서 빠짐 · SPEC JBFIX 꼴)
            i = next((k for k, l in enumerate(x['lines']) if ANSZ.match(l.strip())), len(x['lines']))
            x['lines'][i:i] = ['⁣' + l.strip() for _, l in pl]; x['lp'][i:i] = [p for p, _ in pl]; x['pre'] = len(pl)
    return blocks
NP = {'25': 23, '24': 30, '23': 32, '25q3': 26, '24q3': 40, '23q3': 54}
if __name__ == '__main__':
    allb = {}
    for ed, n in NP.items():
        b = parse(ed, n); allb[ed] = b
        cnt = {}
        for x in b: cnt.setdefault((x['topic'], x['sec']), []).append(x['num'])
        print(f'=== {ed}판: {len(b)} blocks')
        for (t, s_), nums in cnt.items(): print(f'  {t} {s_}: {len(nums)} {nums}')
        if '-v' in _sys.argv:
            for x in b: print(f"   {x['topic']}|{x['sec']}|{x['prof'][:3]:3}|{x['num']:>4}|p{x['pg']:<2}| {x['lines'][0][:60]}")
