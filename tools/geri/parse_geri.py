import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json
BASE = J.JBX
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        t = rd(f'{BASE}GERI_20{ed}/{i}.txt'); first = True
        for l in t.split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
SEC25 = re.compile(r'^\s*(20\d\d)\s*-\s*3Q\s*$')
SEC24 = re.compile(r'^\s*<\s*(\d\d)\s*학번\s*기출\s*\(\s*(20\d\d)\s*년도\s*\)\s*>\s*$')
PROF = re.compile(r'^\s*\[\s*([가-힣]{2,3})\s*교수님\s*\]\s*$')
CUE = re.compile(r'[?？]|시오|하시오|하라|하여라|쓰기|쓰시|서술|설명|나열|비교|기술|채우|기입|빈칸|무엇|어떤|이유|차이|특징|구조|명칭|이름|기능|고르|골라|옳|맞는|중복|미복원|\(\s*\d\d|\(탈|\(짤|\[서술|\[단답|\[객|예상|정의|관련|키워드|객관식|서술형|단답형|확률|방법|얼마|고르시오|들어갈|증가|감소|틀린|아닌|질환|것은|것을|경우|사진|그림|\(\s*\)|적기|계획|치료|법 |상관|원인|요소|요인')
STRONG = re.compile(r'[?？]|시오|하시오|하라|하여라|쓰시|쓰기|고르|골라|옳|맞는|서술|설명|나열|중복|미복원|\[서술|\[단답|\[객|\(탈|\(\s*\d\d\s*[,)\-]|\(짤|객관식|빈칸|예상|유사복원|틀린|아닌|얼마|확률')
ANS = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$')
def parse(ed, n):
    L = load(ed, n); blocks = []; cur = None; sec = None; prof = ''; last = 0; inans = False
    for idx, (pg, l) in enumerate(L):
        s = l.strip()
        m = SEC25.match(s)
        if m: sec = m.group(1); last = 0; cur = None; inans = False; prof = ''; continue
        m = SEC24.match(s)
        if m: sec = m.group(2); last = 0; cur = None; inans = False; prof = ''; continue
        mp = PROF.match(s)
        if mp and sec: prof = mp.group(1); cur = None; inans = False; last = 0 if ed == '25' else last; continue
        if not sec: continue
        mq = re.match(r'^(\d{1,2})(-\d)?\s*[.．]\s*(\S.*)?$', s)
        if mq:
            base_ = mq.group(1); sub = mq.group(2) or ''; num = base_ + sub; nn = int(base_)
            nxt = [x[1] for x in L[idx + 1:idx + 5]]; near2 = s
            for x_ in nxt:
                if re.match(r'^\s*(\d{1,2}[.．)]|답|참고|해설)', x_.strip()): break
                near2 += ' ' + x_
            near = s + ' ' + ' '.join(x[1] for x in L[idx + 1:idx + 4])
            cue = ((STRONG.search(near2) if nn != last + 1 else CUE.search(near2)) if inans else CUE.search(near)) is not None
            ok = (nn > last or (sub and nn == last) or (nn == 1 and prof and ed == '25' and last == 0)) and cue
            if ok and sub and cur is not None and nn == last:  # 하위 문항(10-1, 3-1)은 상위 블록에 합침
                cur['lines'].append(l); cur['pg2'] = pg; inans = False; continue
            if ok:
                cur = {'ed': ed, 'sec': sec, 'prof': prof, 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur); inans = False
                if not sub: last = nn
                continue
        if cur is not None:
            cur['lines'].append(l); cur['pg2'] = pg
            if ANS.match(s): inans = True
    return blocks
if __name__ == '__main__':
    allb = {}
    for ed, n in (('25', 16), ('24', 24), ('23', 26)):
        b = parse(ed, n); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks')
        for x in b:
            txt = '\n'.join(x['lines']); stem = x['lines'][0][:46]
            print(f" {x['sec']:5}|{x['prof'][:3]:3}|{str(x['num']):>5}|p{x['pg']:<2}|{len(txt):5}| {stem}")
    json.dump(allb, open(J.work('GERI', 'jb_blocks.json'), 'w'), ensure_ascii=False)
