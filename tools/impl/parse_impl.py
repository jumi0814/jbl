import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json
BASE = J.JBX
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        t = rd(f'{BASE}IMPL_20{ed}/{i}.txt'); first = True
        for l in t.split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
SEC = re.compile(r'^\s*(20\d\d)\s*-\s*3Q\s*$')
CUE = re.compile(r'[?？]|시오|하시오|하라|쓰|고르|설명|나열|비교|서술|기술|채우|기입|무엇|어떠한|인가|은\?|는\?|미복원|복원 불충분|빈칸|요건|\(\s*\d\d|\(짤|\(탈|예상문제|NEW|★|\(\s*\)|\(\s*\d\s*\)')
def parse(ed, n):
    L = load(ed, n); blocks = []; cur = None; sec = '머리말'; last = 0
    for idx, (pg, l) in enumerate(L):
        s = l.strip()
        m = SEC.match(s)
        if m: sec = m.group(1) + '-3Q'; last = 0; cur = None; continue
        if s.startswith('<과거자료'): continue
        if sec == '머리말': continue
        mq = re.match(r'^(추\s*\d|\d{1,2})\s*[.．]\s*(\S.*)?$', s)
        if mq:
            num = mq.group(1).replace(' ', ''); near = s + ' ' + ' '.join(x[1] for x in L[idx + 1:idx + 5])
            isnum = num.isdigit(); ok = False
            if isnum:
                nn = int(num)
                if nn > last and CUE.search(near): ok = True
            else:
                if CUE.search(near): ok = True
            if ok:
                cur = {'ed': ed, 'sec': sec, 'prof': '', 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur)
                if isnum: last = nn
                continue
        if cur is not None: cur['lines'].append(l); cur['pg2'] = pg
    return blocks
if __name__ == '__main__':
    allb = {}
    for ed, n in (('25', 14), ('24', 15), ('23', 6)):
        b = parse(ed, n); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks')
        for x in b:
            txt = '\n'.join(x['lines']); stem = ' '.join(x['lines'][:2])[:58]
            print(f" {x['sec']:8}|{str(x['num']):>3}|p{x['pg']:<2}-{x['pg2']:<2}|{len(txt):5}|{'A' if '답' in txt else '-'}| {stem}")
    json.dump(allb, open(J.work('IMPL', 'jb_blocks.json'), 'w'), ensure_ascii=False)
