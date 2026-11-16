import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""RAD 임상영상치의학(4Q) JB 분해 — 23·24·25판(2026-11-16 · 판마다 전 쪽 글·그림 확인).
구조 = 연도 칸형(칸 안 번호 문항 · 문항 첫머리 괄호 연도) — 판마다 칸:
  25판(30쪽): 1~2쪽 멘트·수업 표 → '[2024]'(2024 시험) · '[2023]' · '2022-3,4Q'(<T/F 문제> · <객관식 문제> · <단답형 문제>)
  24판(48쪽): 1~2쪽 멘트·수업 표 → '2023-3,4Q' · '2022-3,4Q'(<T/F>·<객관식>·<단답형>) · '[2022 4Q 땡시 기출 복원]' · '2021 3,4Q'(<T/F>·<객관식>·<단답형>) · '[2021 4Q 땡시 기출 복원]'
  23판(58쪽): 1~3쪽 멘트·수업 표 → '[2022년 기출]'(<T/F>·<객관식>·<단답형>) · '[2022 4Q 땡시 기출 복원]' · '[2021년 기출]'(…) · '[2021 4Q 땡시 기출 복원]' · '[2020년 기출]'(<T/F>·<객관식>·<단답형>·<서술형>) · '[2020 4Q 땡시 기출 복원]'
칸 이름(sec) = '2024'·'2023'(번호 하나로 이어지는 칸) · '<해> T/F'·'<해> 객관식'·'<해> 단답형'·'<해> 서술형'(2022 칸은 <객관식>에서 번호가 1로 다시 시작) · '<해> 땡시'.
문항 시작 줄 = 아래 순서표 ORDER의 '다음 번호'일 때만(보기 '1. …'·해설 '1. …'·'22 학습부: …'를 문항으로 끊지 않게 — RULES 0-1).
  · '21 치주질환, 골파괴, 방사선 관련 문제'(24판 2023 칸 · 25판 2023 칸 — 점 없는 묶음 머리) = 블록 num '21'(머리 줄 하나 — assemble이 21-1·21-2·21-3 카드의 다른 판본으로)
  · '<방사선상 특징>'은 해설 안 글(칸 머리 아님)
  · 23판 2022 땡시 22번 뒤 번호 없는 osteopetrosis 문항 = 블록 num '22+'(UNNUM — 11-16 JBV 독립 검수)
  · 23판 2022 객관식 3-2의 보기 '4. 등각촬영법에서 …'는 다음 번호 '4'와 같아 NOTQ로 뺌 · 23판 2020 땡시 12번 안 '2. Masseter m.'은 해설 줄(순서표가 거름)"""
import re, json
BASE = J.JBX
NPAGES = {'25': 30, '24': 48, '23': 58}
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n=None):
    lines = []
    for i in range(1, (n or NPAGES[ed]) + 1):
        first = True
        for l in rd(f'{BASE}RAD_20{ed}/{i}.txt').split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue   # 쪽 번호 줄(25판 1~30 · 24판 127~174 · 23판 167~224)
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
def _r(a, b): return [str(i) for i in range(a, b + 1)]
SUBS = {'<T/F 문제>': 'T/F', '<객관식 문제>': '객관식', '<단답형 문제>': '단답형', '<서술형 문제>': '서술형'}
YEARHEAD = {   # 판 → {머리 줄: 칸 해(+ '땡시')}
    '25': {'[2024]': '2024', '[2023]': '2023', '2022-3,4Q': '2022'},
    '24': {'2023-3,4Q': '2023', '2022-3,4Q': '2022', '[2022 4Q 땡시 기출 복원]': '2022 땡시', '2021 3,4Q': '2021', '[2021 4Q 땡시 기출 복원]': '2021 땡시'},
    '23': {'[2022년 기출]': '2022', '[2022 4Q 땡시 기출 복원]': '2022 땡시', '[2021년 기출]': '2021', '[2021 4Q 땡시 기출 복원]': '2021 땡시',
           '[2020년 기출]': '2020', '[2020 4Q 땡시 기출 복원]': '2020 땡시'},
}
# 칸마다 문항 번호 차례(판 전 쪽을 읽고 센 것 — '21H' = 점 없는 묶음 머리 '21 …')
ORDER = {
    '25': {'2024': _r(1, 11) + ['11-1'] + _r(12, 16) + ['16-1'] + _r(17, 25) + ['25-1'] + _r(26, 31),
           '2023': _r(1, 20) + ['21H', '21-1', '21-2', '21-3'] + _r(22, 33),
           '2022 T/F': ['1-1', '1-2', '1-3', '2', '3'], '2022 객관식': _r(1, 8), '2022 단답형': ['9', '9-1', '10', '11', '12']},
    '24': {'2023': _r(1, 20) + ['21H', '21-1', '21-2', '21-3'] + _r(22, 33),
           '2022 T/F': ['1-1', '1-2', '1-3', '2', '3'], '2022 객관식': _r(1, 8), '2022 단답형': ['9', '9-1', '10', '11', '12'], '2022 땡시': _r(1, 20),
           '2021 T/F': ['1-1', '1-2'] + _r(2, 6), '2021 객관식': ['7', '8', '9-1', '9-2', '10', '11', '12', '13'],
           '2021 단답형': ['14-1', '14-2', '15-1', '15-2', '16', '17', '18', '19', '20-1', '20-2', '21'], '2021 땡시': _r(1, 27)},
    '23': {'2022 T/F': ['1-1', '1-2', '1-3', '2', '3'],
           '2022 객관식': ['1', '2', '3-1', '3-2', '4', '5', '5-1', '6', '7', '8', '9', '10', '10-1', '11', '11-1', '12', '12-1'],
           '2022 단답형': ['13', '13-1', '14', '15', '16', '16-1', '17'], '2022 땡시': _r(1, 21) + ['21-1', '22', '22+'] + _r(23, 26),
           '2021 T/F': ['1-1', '1-2'] + _r(2, 6), '2021 객관식': ['7', '8', '9-1', '9-2', '10', '11', '12', '13'],
           '2021 단답형': ['14-1', '14-2', '15-1', '15-2', '16', '17', '18', '19', '20', '21', '22-1', '22-2', '23'], '2021 땡시': _r(1, 27),
           '2020 T/F': _r(1, 8), '2020 객관식': _r(9, 26), '2020 단답형': _r(27, 31), '2020 서술형': ['32', '33'], '2020 땡시': _r(1, 19)},
}
NOTQ = {('23', '2022 객관식', '4. 등각촬영법에서 골파괴 높이를 관찰할 수 없다.')}   # 3-2 보기(다음 문항 번호 4와 같음)
# 번호 없는 문항(11-16 JBV 독립 검수): 판|칸|가짜 번호 → 그 문항 첫 줄 앞머리 — CONS '21+' 꼴(번호 뒤 '+' = 그 번호 블록 뒤에 번호 없이 붙은 다른 문항)
#  · 23판 p.22 2022 땡시 22번(허민석 양성·악성) 해설·참고 뒤 굵은 글씨 '하악골이 전반적으로 균일하게 방사선불투과상이 증가 … 답: osteopetrosis'
#    = 24판 2022 땡시 18번(M04)의 23판 사본(24판이 번호를 붙임) — 22번 블록에 붙어 있던 것을 뗌
UNNUM = {('23', '2022 땡시', '22+'): '하악골이 전반적으로 균일하게 방사선불투과상이'}
QRE = re.compile(r'^(\d{1,2})(?:\s*-\s*(\d{1,2}))?\s*[.．]\s*(\S.*)?$')
HRE = re.compile(r'^(\d{1,2})\s+(\S.*)$')
def parse(ed, n=None):
    L = load(ed, n); blocks = []; cur = None; year = None; sec = '머리말'; order = []; k = 0
    for pg, l in L:
        s = l.strip()
        if s in YEARHEAD[ed]:
            year = YEARHEAD[ed][s]; sec = year; cur = None; order = ORDER[ed].get(sec, []); k = 0; continue
        if year and s in SUBS and '땡시' not in year:
            sec = f'{year} {SUBS[s]}'; cur = None; order = ORDER[ed][sec]; k = 0; continue
        if sec == '머리말': continue
        nxt = order[k] if k < len(order) else None
        if nxt and (ed, sec, s) not in NOTQ:
            num = None
            if (ed, sec, nxt) in UNNUM:
                if s.startswith(UNNUM[(ed, sec, nxt)]): num = nxt
            elif nxt.endswith('H'):
                m = HRE.match(s)
                if m and m.group(1) == nxt[:-1]: num = nxt[:-1]
            else:
                m = QRE.match(s)
                if m and (m.group(1) + (f'-{m.group(2)}' if m.group(2) else '')) == nxt: num = nxt
            if num:
                cur = {'ed': ed, 'sec': sec, 'prof': '', 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur); k += 1
                continue
        if cur is not None: cur['lines'].append(l); cur['pg2'] = pg if l.strip() else cur['pg2']
    for x in blocks:
        while x['lines'] and not x['lines'][-1].strip(): x['lines'].pop()
    return blocks
def missing(ed):
    """순서표에 있는데 못 찾은 번호(0이어야 함)"""
    got = {}
    for x in parse(ed): got.setdefault(x['sec'], []).append(x['num'])
    return {s: [o.rstrip('H') for o in order if o.rstrip('H') not in got.get(s, [])] for s, order in ORDER[ed].items() if [o for o in order if o.rstrip('H') not in got.get(s, [])]}
if __name__ == '__main__':
    allb = {}
    for ed in ('25', '24', '23'):
        b = parse(ed); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks · 못 찾은 번호 {missing(ed)}')
        for s in ORDER[ed]: print(f'   {s}: {len([x for x in b if x["sec"] == s])} ' + ' '.join(x['num'] for x in b if x['sec'] == s))
        if '-v' in _sys.argv:
            for x in b:
                txt = '\n'.join(x['lines']); stem = ' '.join(x['lines'][:2])[:62]
                print(f" {x['sec']:12}|{str(x['num']):>5}|p{x['pg']:<2}-{x['pg2']:<2}|{len(txt):5}|{'A' if '답' in txt else '-'}| {stem}")
    _os.makedirs(J.work('RAD'), exist_ok=True)
    json.dump(allb, open(J.work('RAD', 'jb_blocks.json'), 'w'), ensure_ascii=False)
