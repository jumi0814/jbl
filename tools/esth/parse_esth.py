import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
# ESTH 심미치과학 JB(23·24·25판) → 문항 블록. 구조 = 연도 칸형('2024-3Q' 칸 아래 번호 문항, 문항 첫머리 괄호 연도)
# 판본별 특이점(전문 확인 2026-10-03):
#  - 미복원은 '3-5. 미복원'처럼 번호 범위로도 적힘 → 범위 하나 = 블록 하나(num '3-5')
#  - 24판 2023 칸에 '4.'가 두 번(두 번째 = 25판 2023 칸 6번 용어 문제), 2022 칸에 '6.'이 두 번(두 번째 = 치관 폭/길이 비율) → 두 번째는 num '4b'·'6b'
#  - 해설 안의 번호 줄(25판 2024 칸 11번 해설의 '3. Tooth axis' … '12. Incisal edge configuration' · '13. Lower lipline', 23번 해설 '1.~6.')은 문항이 아님
#  - 각 판 끝의 'Wider space를 좁게 보이게 …' 대비표(JB 해설이 'JB맨뒤에 표로 정리'라고 가리킴)는 블록 num '표'(칸 '부록')
import re, json
BASE = J.JBX
NPAGES = {'25': 16, '24': 21, '23': 20}
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        t = rd(f'{BASE}ESTH_20{ed}/{i}.txt'); first = True
        for l in t.split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
SEC = re.compile(r'^\s*(20\d\d)\s*-\s*3Q\s*$')
QRE = re.compile(r'^★?\s*(\d{1,2})(?:\s*-\s*(\d{1,2}))?\s*[.．]\s*(\S.*)?$')
NOTQ = {'3. Tooth axis', '4. Zenith of the gingiva contour', '5. Balance of gingival levels', '6. level of interdental contact',
        '12. Incisal edge configuration', '13. Lower lipline'}
DUP = {('24', '2023-3Q', 4): '4b', ('24', '2022-3Q', 6): '6b'}   # 같은 번호가 두 번 — 두 번째 문항의 num
TABLE = re.compile(r'^(\*\s*아래는 예전부터|Wider space를 좁게 보이게)')
def parse(ed, n=None):
    L = load(ed, n or NPAGES[ed]); blocks = []; cur = None; sec = '머리말'; last = 0; seen = set()
    for idx, (pg, l) in enumerate(L):
        s = l.strip()
        m = SEC.match(s)
        if m: sec = m.group(1) + '-3Q'; last = 0; cur = None; seen = set(); continue
        if sec == '머리말': continue
        if TABLE.match(s) and not (cur and cur['num'] == '표'):
            cur = {'ed': ed, 'sec': '부록', 'prof': '', 'num': '표', 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur); sec = '부록'; continue
        if s.startswith('수고하셨습니다'): cur = None; continue
        mq = QRE.match(s)
        if mq and sec != '부록' and s not in NOTQ:
            a = int(mq.group(1)); b = int(mq.group(2)) if mq.group(2) else None
            num = None
            if a > last and a <= last + 6: num = f'{a}-{b}' if b else str(a)
            elif a == last and (ed, sec, a) in DUP and (ed, sec, a) not in seen: num = DUP[(ed, sec, a)]; seen.add((ed, sec, a))
            if num:
                cur = {'ed': ed, 'sec': sec, 'prof': '', 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur)
                last = b or a
                continue
        if cur is not None: cur['lines'].append(l); cur['pg2'] = pg
    for x in blocks:   # 끝의 빈 줄 정리
        while x['lines'] and not x['lines'][-1].strip(): x['lines'].pop()
    return blocks
if __name__ == '__main__':
    allb = {}
    for ed in ('25', '24', '23'):
        b = parse(ed); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks')
        for x in b:
            txt = '\n'.join(x['lines']); stem = ' '.join(x['lines'][:2])[:62]
            print(f" {x['sec']:8}|{str(x['num']):>5}|p{x['pg']:<2}-{x['pg2']:<2}|{len(txt):5}|{'A' if '답' in txt else '-'}| {stem}")
    json.dump(allb, open(J.work('ESTH', 'jb_blocks.json'), 'w'), ensure_ascii=False)
