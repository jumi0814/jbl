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
SPLIT_SUB = {'25': {'17-1'}}   # 별도 카드로 분리할 하위 문항
def parse(ed, n):
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
    for ed, n in (('25', 14), ('24', 16), ('23', 12)):
        b = parse(ed, n); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks')
        for x in b:
            txt = '\n'.join(x['lines']); stem = ' '.join(x['lines'][:2])[:60]
            print(f" {x['sec'][:22]:22}|{x['prof'][:3]:3}|{str(x['num']):>4}|p{x['pg']:<2}-{x['pg2']:<2}|{len(txt):5}|{'A' if re.search(r'답', txt) else '-'}| {stem}")
    json.dump(allb, open(J.work('CONS', 'jb_blocks.json'), 'w'), ensure_ascii=False)
