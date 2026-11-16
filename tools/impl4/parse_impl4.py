import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""IMPL4 JB 분해(11-16 Q4 JB 단계) — parse(ed, n) → 블록 [{'ed','sec','prof','num','pg','pg2','lines','lp','past'}]
판(ed): '25'·'24'·'23' = 4Q JB(work/jb/IMPL4_20YY — 판 해 = 파일 해 · 최신 시험 해 = 판 해 - 1)
구조(보고 work/IMPL4/jb/R_JB_IMPL4.md 1절) — 세 판 모두 **연도 칸형**(교수 머리 없음 · 2단 조판 — pdfium 글 순서 = 왼쪽 단 → 오른쪽 단):
  25판 = '2024-4Q'·'2023-4Q'·'2022-4Q' · 24판 = '2023-4Q'·'2022-4Q'·'2021-4Q'·'2020-4Q' · 23판 = '2022-4Q'·'2021-4Q'·'2020-4Q'
  23판 2022 칸 12-16번·2020 칸 7-14번 앞 머리 '[이젠 안들어오시는 교수님 범위]' → 블록 past=True(머리 줄은 문항 글이 아님 — 칸 머리처럼 뺌)
문항 = 칸 안 'N. …'(직전 번호 + 1 · 앞 블록이 답·참고·해설 줄 뒤이거나 '미복원'·'중복 복원' 자리 줄)
  · 'A~B. …' = 번호 범위 블록('13-14' · '4-5')
  · 답 줄 전에 'N+1. …'이 또 오면 같은 블록(번호 범위 'N-(N+1)' — 24·25판 2023 칸 '1. 고정성 … 2. 가철성 … (유사 문제로 같이 풀이)' 답 하나)
  · '추가) …' = 블록 '추가'(24·25판 2023 칸 끝 — 명훈 교수님 언급 문제)
해설·답 안의 'N.' 줄(25판 2024 칸 5번 답 '1. Fixture fracture'·'2.'·'3.')은 직전 번호 + 1이 아니라 문항 아님(RULES 0-1) — 걸리는 줄이 없어 NOTQ 표는 비어 있음"""
import re, json
BASE = J.JBX
def jbdir(ed): return f'{BASE}IMPL4_20{ed}'
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        t = rd(f'{jbdir(ed)}/{i}.txt'); first = True
        for l in t.split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue   # 쪽 번호(25판 1~12 · 24판 63~76 · 23판 33~44)
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
SEC = re.compile(r'^\s*(20\d\d)\s*-\s*4Q\s*$')                        # '2024-4Q'
PAST = re.compile(r'^\s*\[\s*이젠\s*안\s*들어오시는\s*교수님\s*범위\s*\]\s*$')   # 23판 '[이젠 안들어오시는 교수님 범위]'
QL = re.compile(r'^\s*(\d{1,2})\s*[.．]\s*(\S.*)?$')
RNG = re.compile(r'^\s*(\d{1,2})\s*~\s*(\d{1,2})\s*[.．]\s*(\S.*)?$')      # '13~14. …' · '4~5. 2번과 중복 복원'
ADD = re.compile(r'^\s*추가\s*\)')                                      # '추가) 명훈 교수님 언급 문제. …'
ANSZ = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$|^\s*해설\s*[:：)]?|^\s*(참고|참조)\s*[:：]')
SLOT = re.compile(r'미복원|중복\s*복원')   # 자리 줄(답 없이 다음 번호가 바로 옴)
NOTQ = set()   # 해설·답 안 번호 줄(직전 번호 + 1이라 문항처럼 보이는 것) — (판, 칸, 쪽, 줄 앞글) · 이 JB에는 없음
def notq(ed, sec, pg, s): return any(k[:3] == (ed, sec, pg) and s.startswith(k[3]) for k in NOTQ)
def parse(ed, n):
    L = load(ed, n); blocks = []; cur = None; sec = None; last = 0; inans = False; past = False
    def new(num, pg, l):
        b = {'ed': ed, 'sec': sec, 'prof': '', 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l], 'lp': [pg], 'past': past}
        blocks.append(b); return b
    for pg, l in L:
        s = l.strip()
        m = SEC.match(s)
        if m: sec = m.group(1); cur = None; last = 0; inans = False; past = False; continue
        if not sec: continue
        if PAST.match(s): past = True; cur = None; inans = False; continue
        slot = cur is not None and len([x for x in cur['lines'] if x.strip()]) <= 3 and bool(SLOT.search(' '.join(cur['lines'])))
        mr = RNG.match(s)
        if mr and int(mr.group(1)) == last + 1 and (cur is None or inans or slot):
            a, b = int(mr.group(1)), int(mr.group(2))
            cur = new(f'{a}-{b}', pg, l); inans = False; last = b; continue
        if ADD.match(s) and cur is not None and (inans or slot):
            cur = new('추가', pg, l); inans = False; continue
        mq = QL.match(s)
        if mq:
            nn = int(mq.group(1))
            if nn == last + 1 and not notq(ed, sec, pg, s):
                if cur is None or inans or slot:
                    cur = new(str(nn), pg, l); inans = False; last = nn; continue
                if not inans and cur['num'] == str(last) and not any(ANSZ.match(x) for x in cur['lines']):   # 답 전에 다음 번호 = 같이 푼 문항(번호 범위)
                    cur['num'] = f'{cur["num"]}-{nn}'; cur['lines'].append(l); cur['lp'].append(pg); cur['pg2'] = pg; last = nn; continue
        if cur is not None:
            cur['lines'].append(l); cur['lp'].append(pg); cur['pg2'] = pg
            if ANSZ.match(s): inans = True
    for x in blocks:   # 블록 끝의 빈 줄 정리(글자는 그대로)
        while len(x['lines']) > 1 and not x['lines'][-1].strip(): x['lines'].pop(); x['lp'].pop()
        x['pg2'] = x['lp'][-1]
    return blocks
NP = {'25': 12, '24': 14, '23': 12}
if __name__ == '__main__':
    for ed, n in NP.items():
        b = parse(ed, n)
        cnt = {}
        for x in b: cnt.setdefault(x['sec'], []).append(x['num'] + ('*' if x['past'] else ''))
        print(f'=== {ed}판: {len(b)} blocks')
        for s_, nums in cnt.items(): print(f'  {s_}: {len(nums)} {nums}')
        if '-v' in _sys.argv:
            for x in b: print(f"   {x['sec']}|{x['num']:>5}|p{x['pg']:<2}-{x['pg2']:<2}|{'P' if x['past'] else ' '}| {x['lines'][0][:60]}  …  {x['lines'][-1][:40]}")
