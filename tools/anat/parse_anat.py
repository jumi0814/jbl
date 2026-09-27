import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json
BASE = J.JBX
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        t = rd(f'{BASE}ANAT_20{ed}/{i}.txt'); first = True
        for l in t.split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
SEC = re.compile(r'^\s*\[?\s*(20\d\d)\s*(?:-\s*3Q|년\s*복원|년|\])?\s*\]?\s*$')
PROF = re.compile(r'^\s*\[?\s*([가-힣]{2,3})\s*교수님\s*\]?\s*$')
CUE = re.compile(r'[?？]|시오|하시오|하라|하여라|쓰기|쓰시|서술|설명|나열|비교|기술|채우|기입|빈칸|무엇|어떤|이유|차이|특징|구조|명칭|이름|위치|기능|분지|경계|골라|고르|옳|맞는|중복|미복원|\(\s*\d\d|\(탈|\(짤|\[서술|\[단답|\[객|추가복원|정의|관련|키워드|객관식|서술형|단답형')
STRONG = re.compile(r'[?？]|시오|하시오|하라|하여라|쓰시|쓰기|적기|골라|고르|옳|맞는|서술하|설명하|나열|열거|중복|미복원|추가복원|\[서술|\[단답|\[객|\(탈\)|\(\s*\d\d\s*[,)]|\(짤|절개법|접근법|객관식|서술형|단답형|빈칸빵|넘버링|임상양상|해부학적 특징|그림 주고|그림을 보고|경계쓰고|키워드')
ANS = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$')
def parse(ed, n):
    L = load(ed, n); blocks = []; cur = None; sec = '머리말'; prof = ''; last = 0; inans = False
    for idx, (pg, l) in enumerate(L):
        s = l.strip()
        m = SEC.match(s)
        if m and len(s) < 16: sec = m.group(1); last = 0; cur = None; inans = False; continue
        mp = PROF.match(s)
        if mp and sec != '머리말': prof = mp.group(1); cur = None; inans = False; continue
        if sec == '머리말': continue
        mq = re.match(r'^(추가복원\s*\d|\d{1,2})(-\d)?\s*([.．)])\s*(\S.*)?$', s)
        if mq and (mq.group(3) != ')' or mq.group(2)):
            base_ = mq.group(1).replace(' ', ''); sub = mq.group(2) or ''; num = base_ + sub
            near = s + ' ' + ' '.join(x[1] for x in L[idx + 1:idx + 4])
            nxt = [x[1] for x in L[idx + 1:idx + 3]]; near2 = s
            for x_ in nxt:
                if re.match(r'^\s*(\d{1,2}[.．)]|답|참고|해설)', x_.strip()): break
                near2 += ' ' + x_
            if base_.isdigit():
                nn = int(base_); cue = (STRONG.search(near2) if inans else CUE.search(near)) is not None
                ok = (nn > last or (sub and nn == last)) and cue
                if ok and sub and cur is not None and nn == last:  # 하위 문항은 상위 블록에 합침
                    cur['lines'].append(l); cur['pg2'] = pg; continue
            else: ok = True; nn = last
            if ok:
                cur = {'ed': ed, 'sec': sec, 'prof': prof, 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur); inans = False
                if base_.isdigit() and not sub: last = nn
                continue
        if cur is not None:
            cur['lines'].append(l); cur['pg2'] = pg
            if ANS.match(s): inans = True
    return blocks
if __name__ == '__main__':
    allb = {}
    for ed, n in (('25', 22), ('24', 6), ('23', 26)):
        b = parse(ed, n); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks')
        for x in b:
            txt = '\n'.join(x['lines']); stem = x['lines'][0][:50]
            print(f" {x['sec']:5}|{x['prof'][:3]:3}|{str(x['num']):>7}|p{x['pg']:<2}-{x['pg2']:<2}|{len(txt):5}| {stem}")
    json.dump(allb, open(J.work('ANAT', 'jb_blocks.json'), 'w'), ensure_ascii=False)
