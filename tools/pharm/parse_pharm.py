import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json
BASE = J.JBX
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        t = rd(f'{BASE}PHARM_20{ed}/{i}.txt'); first = True
        for l in t.split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
TOPIC = re.compile(r'^\s*[<\[]\s*(금연[^>\]]*|구강건조증[^>\]]*|보톡스|급성/만성통증[^>\]]*|지혈제[^>\]]*|살균제[^>\]]*|성호르몬[^>\]]*)\s*[>\]]\s*$')
TKEY = {'금연': 'RX', '구강건조': 'XE', '보톡스': 'BT', '통증': 'PN', '지혈': 'HM', '살균': 'DS', '성호르몬': 'SX'}
YEAR = re.compile(r'^\s*[\[<]\s*(20\d\d)\s*년\s*(?:도)?\s*(?:[-–]\s*Pf\.?\s*([가-힣]{2,3})|([가-힣]{2,3})\s*교수님)?\s*[\]>]\s*$')
CUE = re.compile(r'[?？]|시오|하시오|하라|쓰기|쓰시|서술|설명|나열|비교|기술|채우|기입|빈칸|무엇|어떤|이유|차이|특징|기전|고르|골라|옳|맞는|틀린|아닌|중복|미복원|\(\s*\d\d|\(탈|\(짤|T/F|\(\s*\)|약은|약물|용어|효과|정의|경우|것은|것을|사용|치료|적응증|부작용|목적|복원|짤|표\s|보여주|이다\.|한다\.|should|because|used|rate|effect')
STRONG = re.compile(r'[?？]|시오|하시오|하라|쓰시|쓰기|고르|골라|옳|맞는|틀린|아닌|서술|설명|나열|중복|미복원|\[서술|\[단답|\(탈|\(\s*\d\d\s*[,)\-’\']|\(짤|T/F|\(\s*\)')
QEND = re.compile(r'[?？]|것은|시오')
ANS = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$')
def parse(ed, n):
    L = load(ed, n); blocks = []; cur = None; topic = None; sec = None; prof = ''; last = 0; inans = False
    for idx, (pg, l) in enumerate(L):
        s = l.strip()
        m = TOPIC.match(s)
        if m:
            t = m.group(1); topic = next((v for k, v in TKEY.items() if k in t), None); sec = None; cur = None; last = 0; inans = False; prof = ''; continue
        m = YEAR.match(s)
        if m and topic:
            nsec = m.group(1)
            if sec and int(nsec) > int(sec) and topic == 'HM': topic = 'BT'   # 24판: 지혈 뒤에 주제 헤더 없이 보톡스 <2023년>이 이어짐
            sec = nsec; prof = m.group(2) or m.group(3) or ''; last = 0; cur = None; inans = False; continue
        if not topic or not sec or topic == 'SX': continue
        mq = re.match(r'^(\d{1,2})\s*[.．]\s*(\S.*)?$', s)
        if mq:
            nn = int(mq.group(1)); num = mq.group(1)
            nxt = [x[1] for x in L[idx + 1:idx + 5]]; near2 = s
            for x_ in nxt:
                if re.match(r'^\s*(\d{1,2}[.．)]|답|참고|해설)', x_.strip()): break
                near2 += ' ' + x_
            near = s + ' ' + ' '.join(x[1] for x in L[idx + 1:idx + 7])
            cue = ((STRONG.search(near2) if nn != last + 1 else CUE.search(near2)) if inans else CUE.search(near)) is not None
            can_start = cur is None or inans or re.search(r'중복', cur['lines'][0]) or nn == 1
            if nn > last and cue and can_start:
                cur = {'ed': ed, 'topic': topic, 'sec': sec, 'prof': prof, 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur); inans = False; last = nn; continue
            # 답안·해설 안에 삼켜진 다음 문항(직전 번호+1로 시작하고 문항형 문장으로 끝남) → 새 블록 (split=True: assemble이 기존 id 뒤에 번호를 붙임)
            if cur is not None and nn == last + 1:
                stem = [s]
                for _pg, x_ in L[idx + 1:idx + 21]:
                    xs = x_.strip()
                    if ANS.match(xs) or re.match(r'^\s*해설\s*[:：]', xs) or re.match(r'^\s*\d{1,2}\s*[.．)]', xs): break
                    stem.append(xs)
                if QEND.search(' '.join(stem)):
                    cur = {'ed': ed, 'topic': topic, 'sec': sec, 'prof': prof, 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l], 'split': True}; blocks.append(cur); inans = False; last = nn; continue
        if cur is not None:
            cur['lines'].append(l); cur['pg2'] = pg
            if ANS.match(s): inans = True
    return blocks
if __name__ == '__main__':
    allb = {}
    for ed, n in (('25', 26), ('24', 40), ('23', 54)):
        b = parse(ed, n); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks')
        for x in b: print(f" {x['topic']}|{x['sec']}|{x['prof'][:3]:3}|{x['num']:>2}|p{x['pg']:<2}| {x['lines'][0][:48]}")
    json.dump(allb, open(J.work('PHARM', 'jb_blocks.json'), 'w'), ensure_ascii=False)
