import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json
BASE = J.JBX
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        t = rd(f'{BASE}CONS_20{ed}/{i}.txt'); first = True
        for l in t.split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
PROF = re.compile(r'^\[(\d)\]\s*(\S+?)\s*교수님\s*$')
SPLIT_SUB = {'25': {'17-1'}, '26': {'4-1', '14-1', '45-2', '17-1'}}   # 별도 카드로 분리할 하위 문항
# ---- 26판(2026 3Q JB, 학습부 26년 편집): 앞쪽 '2025-3Q'(25년 시험 복원 — [교수 교수님] 머리, 번호 1~48, 15 → 18로 건너뜀)
#      + 뒷부분 '[과거 기출 — 25 년도와 명확히 중복되지 않은 문항]'([n] 교수 + '- 강의 -' 머리, 번호는 25판 번호 그대로).
#      번호가 앞·뒤에서 겹치므로 뒷부분 블록은 key 'P<번호>'(find·대조표 키) — 화면 번호(num)는 JB 그대로.
#      문항 시작 줄은 아래 순서표의 '다음 번호'일 때만(보기 '1. …'·해설 '1) …'을 문항으로 잘못 끊지 않게).
#      '추가 복원:'(21·34 해설 끝 — 번호 없이 덧붙인 25년 문항 복원)은 별도 블록 '21+'·'34+'(문항 하나도 빠짐없이 — 별개 문항으로).
ORDER26 = {'front': ['1', '2', '3', '4', '4-1', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '14-1', '15', '18', '19', '20', '21', '21+', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '34+', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '45-2', '46', '47', '48'],
           'back': ['2', '5', '9', '11', '12', '13', '15', '16', '17', '17-1', '18', '19', '21', '23', '24', '25', '26', '27', '28', '29']}
PROF26 = re.compile(r'^\[(\S+?)\s*교수님\]\s*$')
CUE26 = re.compile(r'[?？]|시오|하기|서술|쓰시|쓰세|고르|나열|설명|약자|목적|이유|방법|요소|기준|고려|빈칸|채우|T/F|문제|\(\s*(?:20)?\d\d[^)]*\)|과거|옳은|틀린|아닌|어떻게|가능성|성분')
def load26(n):
    """26판 쪽 머리 '임상치과보존학' + 쪽 번호 줄을 뺌(그 외는 load와 같음)"""
    lines = []
    for i in range(1, n + 1):
        t = rd(f'{BASE}CONS_2026/{i}.txt'); k = 0
        for l in t.split('\n'):
            if '무단인쇄' in l: continue
            if k == 0 and l.strip() == '임상치과보존학': k = 1; continue
            if k == 1 and re.fullmatch(r'\s*\d{1,3}\s*', l): k = 2; continue
            if l.strip(): k = 2
            lines.append((i, l.rstrip()))
    return lines
def parse26(n):
    L = load26(n); blocks = []; cur = None; prof = ''; lec = ''; sec = '머리말'; hold = []
    part = None; order = []; nxt = 0
    def start(num, pg, l, sub_merge=False):
        nonlocal cur, hold, nxt
        nxt += 1
        if sub_merge and cur is not None: cur['lines'].append(l); cur['pg2'] = pg; return
        cur = {'ed': '26', 'sec': sec, 'prof': prof, 'num': num, 'pg': pg, 'pg2': pg, 'lines': hold + [l]}
        if part == 'back': cur['key'] = 'P' + num
        hold = []; blocks.append(cur)
    for idx, (pg, l) in enumerate(L):
        s = l.strip()
        if s == '2025-3Q' and part is None: part = 'front'; order = ORDER26['front']; nxt = 0; sec = '2025-3Q'; continue
        if s.startswith('[과거 기출'): part = 'back'; order = ORDER26['back']; nxt = 0; cur = None; prof = ''; lec = ''; sec = '과거 기출'; continue
        if part == 'back' and s == '중복되지 않은 문항]' and cur is None and not prof: continue
        if part is None: continue
        mp = PROF26.match(s) if part == 'front' else PROF.match(s)
        if mp:
            prof = mp.group(1) if part == 'front' else mp.group(2); cur = None; lec = ''
            sec = f'2025-3Q · {prof}' if part == 'front' else f'과거 기출 · {prof}'; continue
        if part == 'back' and cur is None and not lec and re.match(r'^-\s*.+\s*[-–]\s*$', s):
            lec = s.strip('-–— ').strip(); sec = f'과거 기출 · {prof} · {lec}'; continue
        if part == 'back' and cur is None and not lec and re.match(r'^-\s*.+$', s) and idx + 1 < len(L) and re.match(r'^.+\s*[-–]\s*$', L[idx + 1][1]):
            lec = (s.strip('-– ') + ' ' + L[idx + 1][1].strip().strip('-– ')).strip(); sec = f'과거 기출 · {prof} · {lec}'; continue
        if part == 'back' and lec and cur is None and re.match(r'^.+\s*[-–]\s*$', s) and sec.endswith(s.strip('-– ').strip()): continue
        if re.match(r'^(20\d\d\s*년\s*교수님\s*(강조|pick).*)$', s): hold.append(s); continue
        want = order[nxt] if nxt < len(order) else None
        if want and want.endswith('+'):
            if s.startswith('추가 복원:'): start(want, pg, l); continue
        elif want:
            m = re.match(r'^(\d{1,2})(-\d)?\s*[.．]\s*(\S.*)?$', s)
            if m and f'{m.group(1)}{m.group(2) or ""}' == want:
                near = s + ' ' + ' '.join(x[1] for x in L[idx + 1:idx + 3])   # 답 안의 '2. …' 나열을 문항으로 끊지 않게(기존 parse의 cue + 26판 객관식 발문 낱말)
                if cur is None or CUE26.search(near):
                    start(want, pg, l, sub_merge=('-' in want and want not in SPLIT_SUB['26'])); continue
        if s.startswith('* 수고하셨습니다'): cur = None; continue
        if cur is not None: cur['lines'].append(l); cur['pg2'] = pg
    return blocks
def parse(ed, n):
    if ed == '26': return parse26(n)
    L = load(ed, n); blocks = []; cur = None; prof = ''; lec = ''; sec = '머리말'; hold = []
    started = False; exp = 1
    for idx, (pg, l) in enumerate(L):
        s = l.strip()
        mp = PROF.match(s)
        if mp: prof = mp.group(2); started = True; cur = None; lec = ''; continue
        if s.startswith('[손호현'): prof = '손호현'; sec = '손호현 기출(참고)'; started = True; cur = None; lec = ''; continue
        if started and re.match(r'^-\s*.+\s*[-–]\s*$', s) and cur is None and not lec:
            lec = s.strip('-–— ').strip(); sec = f'{prof} · {lec}'; continue
        if started and re.match(r'^-\s*.+$', s) and cur is None and not lec and idx + 1 < len(L) and re.match(r'^.+\s*[-–]\s*$', L[idx + 1][1]):
            lec = (s.strip('-– ') + ' ' + L[idx + 1][1].strip().strip('-– ')).strip(); sec = f'{prof} · {lec}'; continue
        if lec and cur is None and re.match(r'^.+\s*[-–]\s*$', s) and sec.endswith(s.strip('-– ').strip()): continue
        if re.match(r'^(20\d\d\s*년\s*교수님\s*(강조|pick).*)$', s): hold.append(s); continue
        m = re.match(r'^(\d{1,2})(-\d)?(?:\([^)]*\))?\s*[.．]\s*(\S.*)?$', s)
        if m and started:
            base = int(m.group(1)); sub = m.group(2) or ''; num = f'{base}{sub}'
            near = s + ' ' + ' '.join(x[1] for x in L[idx + 1:idx + 3])
            cue = bool(re.search(r'[?？]|시오|하기|서술|쓰시|쓰세|고르|나열|설명|약자|목적|이유|방법|요소|기준|고려|빈칸|채우|T/F|문제|\(\s*(?:20)?\d\d[^)]*\)|과거', near))
            ok = ((not sub and base == exp) or (sub and base == exp - 1)) and (cur is None or cue)
            if ok:
                if sub and num not in SPLIT_SUB.get(ed, set()) and cur is not None:
                    cur['lines'].append(l); cur['pg2'] = pg; continue
                cur = {'ed': ed, 'sec': sec, 'prof': prof, 'num': num, 'pg': pg, 'pg2': pg, 'lines': hold + [l]}
                hold = []; blocks.append(cur)
                if not sub: exp = base + 1
                continue
        if s.startswith('* 수고하셨습니다'): cur = None; continue
        if cur is not None: cur['lines'].append(l); cur['pg2'] = pg
    return blocks
if __name__ == '__main__':
    allb = {}
    for ed, n in (('26', 33), ('25', 14), ('24', 16), ('23', 12)):
        b = parse(ed, n); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks')
        for x in b:
            txt = '\n'.join(x['lines']); stem = ' '.join(x['lines'][:2])[:60]
            print(f" {x['sec'][:22]:22}|{x['prof'][:3]:3}|{str(x['num']):>4}|p{x['pg']:<2}-{x['pg2']:<2}|{len(txt):5}|{'A' if re.search(r'답', txt) else '-'}| {stem}")
    json.dump(allb, open(J.work('CONS', 'jb_blocks.json'), 'w'), ensure_ascii=False)
