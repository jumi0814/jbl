import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""CONS4 임상치과보존학(4Q) JB 분해 — 23·24·25판(2026-11-16 · 판마다 전 쪽 글·그림 확인 · work/CONS4/jb/R_JB_CONS4.md 1절).
구조 = 교수별 괄호형(멘트 "기존 JB 가 연도별이 아닌 교수님별로 정리") — 판 안에서 번호가 교수 칸을 넘어 이어짐 · 출제연도 = 문항 머리 괄호.
  25판(18쪽 · 쪽 번호 1~18): p.1 멘트·수업 표 → [1] 유연지(1~6, 6-1) · [2] 이우철(7~30, 12-1) · [3] 금기연 TEMS(31·32) · [3’] 금기연 치아재식술 및 치아이식술(33 — 손원준 2023 문제) · [4] 손원준(34~42, 39-1)
  24판(16쪽 · 쪽 번호 47~62 · p.16 빈 쪽): p.1 멘트·수업 표 → [1] 이우철(1~19, 5-1) · [2] 유연지(20~23) · [3] 금기연 TEMS(24·25) · [4] 손원준 임플란트·재식(26~31, 27-1)
  23판(12쪽 · 쪽 번호 2·22~32 — 큰 JB의 4Q 부분 · p.12 빈 쪽): p.1 멘트·수업 표 → [1] 이우철(1~16, 5-2) · [2] 손원준(17~19) · [6] 기출년도 모르는 문제(20·21) · [참고] 금기연 TEMS(28·29 — 22~27 번호 없음)
칸 이름(sec) = 교수 칸('유연지'·'이우철'·'금기연 TEMS'·'금기연 재식'·'손원준'·'연도 미상'·'금기연 참고') · prof = 칸 머리 교수.
문항 시작 줄 = 칸 순서표 ORDER의 '다음 번호'일 때만(답 속 '1. Flap … 3. Curettage' 같은 나열·해설 번호 줄을 문항으로 끊지 않게 — RULES 0-1) ·
칸 머리 뒤 부제·칸 메모('복원된 문제가 없어 손원준 교수님의 2023년도 문제를 남겨두었습니다')는 블록에 넣지 않음(멘트 — subject.py PROF_NOTE)."""
import re, json
BASE = J.JBX
NPAGES = {'25': 18, '24': 16, '23': 12}
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n=None):
    lines = []
    for i in range(1, (n or NPAGES[ed]) + 1):
        first = True
        for l in rd(f'{BASE}CONS4_20{ed}/{i}.txt').split('\n'):
            if '무단인쇄' in l: continue
            if l.strip() == '임상치과보존학': continue   # 23판 쪽 머리(p.2~) · 표지 제목
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue   # 쪽 번호 줄
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
def _r(a, b): return [str(i) for i in range(a, b + 1)]
# 칸 머리 줄 → (칸 이름, 교수)
SECRE = [(re.compile(r'^\[\d\]\s*유연지 교수님$'), '유연지', '유연지'),
         (re.compile(r'^\[\d\]\s*이우철 교수님$'), '이우철', '이우철'),
         (re.compile(r'^\[3\]\s*금기연 교수님$'), '금기연 TEMS', '금기연'), (re.compile(r'^\[3[’\']\]\s*금기연 교수님$'), '금기연 재식', '금기연'),
         (re.compile(r'^\[참고\]\s*금기연 교수님$'), '금기연 참고', '금기연'),
         (re.compile(r'^\[\d\]\s*손원준 교수님$'), '손원준', '손원준'),
         (re.compile(r'^\[6\]\s*기출년도 모르는 문제'), '연도 미상', '')]
# 칸마다 문항 번호 차례(판 전 쪽을 읽고 센 것)
ORDER = {
    '25': {'유연지': _r(1, 6) + ['6-1'], '이우철': _r(7, 12) + ['12-1'] + _r(13, 30), '금기연 TEMS': ['31', '32'], '금기연 재식': ['33'],
           '손원준': _r(34, 39) + ['39-1'] + _r(40, 42)},
    '24': {'이우철': _r(1, 5) + ['5-1'] + _r(6, 19), '유연지': _r(20, 23), '금기연 TEMS': ['24', '25'], '손원준': ['26', '27', '27-1'] + _r(28, 31)},
    '23': {'이우철': _r(1, 5) + ['5-2'] + _r(6, 16), '손원준': _r(17, 19), '연도 미상': ['20', '21'], '금기연 참고': ['28', '29']},
}
NOTQ = {('25', '유연지', '3. Curettage')}   # 2번 답(과정 1~7)의 셋째 줄 — 다음 문항 번호 3과 같음
QRE = re.compile(r'^(\d{1,2})(?:\s*-\s*(\d{1,2}))?\s*[.．]\s*(\S.*)?$')
def parse(ed, n=None):
    L = load(ed, n); blocks = []; cur = None; sec = '머리말'; prof = ''; order = []; k = 0
    for pg, l in L:
        s = l.strip()
        hit = next(((nm, pf) for rx, nm, pf in SECRE if rx.match(s)), None)
        if hit:
            sec, prof = hit; cur = None; order = ORDER[ed][sec]; k = 0; continue
        if sec == '머리말': continue
        nxt = order[k] if k < len(order) else None
        if nxt and (ed, sec, s) not in NOTQ:
            m = QRE.match(s)
            if m and (m.group(1) + (f'-{m.group(2)}' if m.group(2) else '')) == nxt:
                cur = {'ed': ed, 'sec': sec, 'prof': prof, 'num': nxt, 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur); k += 1
                continue
        if cur is not None: cur['lines'].append(l); cur['pg2'] = pg if l.strip() else cur['pg2']
    for x in blocks:
        while x['lines'] and not x['lines'][-1].strip(): x['lines'].pop()
    return blocks
def missing(ed):
    """순서표에 있는데 못 찾은 번호(0이어야 함)"""
    got = {}
    for x in parse(ed): got.setdefault(x['sec'], []).append(x['num'])
    return {s: [o for o in order if o not in got.get(s, [])] for s, order in ORDER[ed].items() if [o for o in order if o not in got.get(s, [])]}
if __name__ == '__main__':
    allb = {}
    for ed in ('25', '24', '23'):
        b = parse(ed); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks · 못 찾은 번호 {missing(ed)}')
        for s in ORDER[ed]: print(f'   {s}: {len([x for x in b if x["sec"] == s])} ' + ' '.join(x['num'] for x in b if x['sec'] == s))
        if '-v' in _sys.argv:
            for x in b:
                txt = '\n'.join(x['lines']); stem = ' '.join(x['lines'][:2])[:62]
                print(f" {x['sec']:8}|{str(x['num']):>5}|p{x['pg']:<2}-{x['pg2']:<2}|{len(txt):5}|{'A' if '답' in txt else '-'}| {stem}")
    _os.makedirs(J.work('CONS4'), exist_ok=True)
    json.dump(allb, open(J.work('CONS4', 'jb_blocks.json'), 'w'), ensure_ascii=False)
