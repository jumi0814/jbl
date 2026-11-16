import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""GERI4 JB 분해(11-16 Q4 JB 단계) — parse(ed, n) → 블록 [{'ed','sec','prof','num','pg','pg2','lines','lp'}]
판(ed): '25'·'24'·'23' = 4Q JB(work/jb/GERI4_20YY — 판 해 = 파일 해 · 최신 시험 해 = 판 해 - 1)
구조(보고 work/GERI4/jb/R_JB_GERI4.md 1절):
  25판 = 연도 칸 '2024-4Q'·'2023-4Q'·'2022-4Q' + 교수 머리 '[이재일 pf]'·'[김성민pf]'(번호는 칸 안에서 교수가 바뀌어도 이어짐)
  24판·23판 = 연도 칸 '<23년도 기출>'… + 교수 머리 '<조영단 pf>' + 맨 뒤 '<과거 외과 모음>'(교수 '<김성민pf>'·'<명훈pf>'마다 번호 새로 — sec '외과모음·김성민'·'외과모음·명훈')
문항 = 칸 안 'N. …'·'★2. …'·'★ 1. …'(직전 번호 + 1 · 앞 문항의 답·참고·해설 줄 뒤이거나 앞 블록이 '미복원'·'n번 중복복원'·'21년도 n번과 동일' 같은 자리 줄) · 'N-1.'(24판 2023 칸 21-1 · 22·21 칸 14-1 · 23판 22 칸 14-1·17-1 · 21 칸 14-1 = 따로 블록 'N-1')
해설·답 안의 번호 줄(RULES 0-1) = NOTQ · JB 번호 건너뜀 = GAP(23판 2020 칸 7 → 9 — 8번 없음)"""
import re, json
BASE = J.JBX
def jbdir(ed): return f'{BASE}GERI4_20{ed}'
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        t = rd(f'{jbdir(ed)}/{i}.txt'); first = True
        for l in t.split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue   # 쪽 번호(25판 1~18 · 24판 77~96 · 23판 115~133)
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
SEC25 = re.compile(r'^\s*(20\d\d)\s*-\s*4Q\s*$')                     # 25판 '2024-4Q'
SEC24 = re.compile(r'^\s*<\s*(\d\d)\s*년도\s*기출\s*>\s*$')          # 24·23판 '<23년도 기출>'
OLD = re.compile(r'^\s*<\s*과거\s*외과\s*모음\s*>\s*$')               # 24·23판 '<과거 외과 모음>'
PROF = re.compile(r'^\s*[\[<]\s*([가-힣]{2,3})\s*pf\s*[\]>]\s*$')    # '[이재일 pf]'·'[김성민pf]'·'<조영단 pf>'·'<명훈pf>'
QL = re.compile(r'^★?\s*(\d{1,2})\s*[.．]\s*(\S.*)?$')
SUBL = re.compile(r'^★?\s*(\d{1,2})\s*-\s*(\d)\s*[.．]\s*\S')
ANSZ = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$|^\s*해설\s*[:：)]?|^\s*(참고|참조)\s*[:：]')
SLOT = re.compile(r'미복원|중복\s*복원|복원\s*오류|번과\s*동일')   # 자리 줄(답 없이 다음 번호가 바로 옴)
# 해설·답 안의 번호 줄(직전 번호 + 1이라 문항처럼 보이는 것 — RULES 0-1) — (판, 칸, 쪽, 줄 앞글)
NOTQ = {('24', '2021', 12, '4. 동맥 경화'), ('23', '2021', 9, '4. 동맥 경화'),   # 21 칸 류인철 3번 '치주인대 노화시 특징 10개' 답 '1. 인대의 주섬유 … 10. 치근면 근처 상피잔사 감소'의 4번
        ('24', '외과모음·김성민', 17, '2. 비언어적인'), ('23', '외과모음·김성민', 16, '2. 비언어적인')}   # 외과 모음 김성민 1번 답 '<노화에 따른 인지기능의 변화> 1. … 2. 비언어적인 … 3. 경험으로'의 2번
GAP = {('23', '2020', 9)}   # 23판 20 칸: 7(류인철 오연성 폐렴) 다음이 9(곽재영 교합고경) — 8번 없음(쪽 그림 p.14·15 확인)
def notq(ed, sec, pg, s): return any(k[:3] == (ed, sec, pg) and s.startswith(k[3]) for k in NOTQ)
def parse(ed, n):
    L = load(ed, n); blocks = []; cur = None; sec = None; prof = ''; last = 0; inans = False; old = False
    for idx, (pg, l) in enumerate(L):
        s = l.strip()
        m = SEC25.match(s) if ed == '25' else SEC24.match(s)
        if m:
            sec = m.group(1) if ed == '25' else '20' + m.group(1); old = False; prof = ''; cur = None; last = 0; inans = False; continue
        if ed != '25' and OLD.match(s): sec = '외과모음'; old = True; prof = ''; cur = None; last = 0; inans = False; continue
        mp = PROF.match(s)
        if mp and sec:
            prof = mp.group(1); cur = None; inans = False
            if old: sec = f'외과모음·{prof}'; last = 0   # 외과 모음은 교수마다 번호 새로
            continue
        if not sec: continue
        slot = cur is not None and len([x for x in cur['lines'] if x.strip()]) <= 3 and bool(SLOT.search(' '.join(cur['lines'])))
        ms = SUBL.match(s)
        if ms and cur is not None and (inans or slot):
            a, b = int(ms.group(1)), ms.group(2)
            if a == last:   # 'N-1.' = 따로 블록(앞 번호의 딸린 문항 · 해설에 붙인 옛 판 문항)
                cur = {'ed': ed, 'sec': sec, 'prof': prof, 'num': f'{a}-{b}', 'pg': pg, 'pg2': pg, 'lines': [l], 'lp': [pg], 'sub': True}
                blocks.append(cur); inans = False; continue
        mq = QL.match(s)
        if mq and not SUBL.match(s):
            nn = int(mq.group(1))
            okn = nn == last + 1 or (ed, sec, nn) in GAP
            if okn and (cur is None or inans or slot) and not notq(ed, sec, pg, s):
                cur = {'ed': ed, 'sec': sec, 'prof': prof, 'num': str(nn), 'pg': pg, 'pg2': pg, 'lines': [l], 'lp': [pg]}
                blocks.append(cur); inans = False; last = nn; continue
        if cur is not None:
            cur['lines'].append(l); cur['lp'].append(pg); cur['pg2'] = pg
            if ANSZ.match(s): inans = True
    for x in blocks:   # 블록 끝의 빈 줄 정리(글자는 그대로)
        while len(x['lines']) > 1 and not x['lines'][-1].strip(): x['lines'].pop(); x['lp'].pop()
        x['pg2'] = x['lp'][-1]
    return blocks
NP = {'25': 18, '24': 20, '23': 19}
if __name__ == '__main__':
    allb = {}
    for ed, n in NP.items():
        b = parse(ed, n); allb[ed] = b
        cnt = {}
        for x in b: cnt.setdefault(x['sec'], []).append(x['num'])
        print(f'=== {ed}판: {len(b)} blocks')
        for s_, nums in cnt.items(): print(f'  {s_}: {len(nums)} {nums}')
        if '-v' in _sys.argv:
            for x in b: print(f"   {x['sec']}|{x['prof'][:3]:3}|{x['num']:>4}|p{x['pg']:<2}-{x['pg2']:<2}| {x['lines'][0][:60]}")
