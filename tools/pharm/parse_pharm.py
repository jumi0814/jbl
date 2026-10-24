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
            if ed == '26' and first and l.strip() == '임상치과약물치료학': continue   # 26판 쪽 머리(과목명 → 쪽 번호)
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
TOPIC = re.compile(r'^\s*[<\[]\s*(금연[^>\]]*|구강건조증[^>\]]*|보톡스|급성/만성통증[^>\]]*|지혈제[^>\]]*|살균제[^>\]]*|성호르몬[^>\]]*)\s*[>\]]\s*$')
TKEY = {'금연': 'RX', '구강건조': 'XE', '보톡스': 'BT', '통증': 'PN', '지혈': 'HM', '살균': 'DS', '성호르몬': 'SX', '항불안': 'AX'}
# 26판(2026 3Q JB): 주제 머리 '[1] 금연 요법 및 처방전'·'[4,5] 급성/만성통증 치료제'·'[7] 항불안제' · 연도 머리 '[2025 년 – pf.백정화]'(소문자 pf)
TOPIC26 = re.compile(r'^\s*\[\s*\d(?:\s*,\s*\d)*\s*\]\s*(금연.*|구강건조증.*|보톡스.*|급성/만성통증.*|지혈제.*|살균제.*|항불안제.*)$')
YEAR26 = re.compile(r'^\s*\[\s*(20\d\d)\s*년\s*[-–]\s*[Pp]f\.?\s*([가-힣]{2,3})\s*\]\s*$')
# 23 4Q JB(work/jb/PHARM_2023q4): '<항불안제>' + 10-25 '<구강건조증 치료제>'(XE — 3Q 같은 강의) · '<진정수면제>'(SD)·'<약물상호작용>'(DI)는 26 ANX와 겹치는 문항만(Q4KEEP) — 국소마취제·약물유전학·노인은 건너뜀
TOPICQ4 = re.compile(r'^\s*<\s*(항불안제|구강건조증 치료제|진정수면제|국소마취제|약물상호작용|치과약물유전학)\s*>\s*$')
TKEYQ4 = {'항불안제': 'AX', '구강건조증 치료제': 'XE', '진정수면제': 'SD', '약물상호작용': 'DI'}
# 10-25 결정 A13·A14(사용자 10-24 결정표): 진정수면제(서광석)·약물상호작용 중 26 ANX(김우진 항불안제) 정리본이 다루는 문항만 참고 기출로 — 나머지는 범위 밖(블록을 만들지 않음)
Q4KEEP = {'SD': {('2022', '1'), ('2022', '2'), ('2022', '3'), ('2022', '4'), ('2022', '10'), ('2021', '1'), ('2021', '2'), ('2021', '3'), ('2021', '5'),
                 ('2020', '1'), ('2020', '2'), ('2020', '5'), ('2020', '10'), ('2020', '12'), ('2020', '13'), ('2020', '16')},
          'DI': {('2022', '7'), ('2021', '1')}}
# 26판 소문항 중 따로 블록으로 떼는 것(제 괄호 연도가 머리 문항과 다르고 묻는 것도 다른 새 문항): 항불안제 2025-4 밑 '4-1. (T/F) …(21)' · 통증 2025-7 밑 '(2) … 마약유사진통제의 특성 …(25)'
#  · 10-25 통증 2025-3 밑 '(3-2) [과거 복원]'(통증 분류 빈칸 = PN09 꼴 — (3-1) 25년 복원 '삼차신경통과 ____'은 신경병성 질환명 = PN12 꼴 · 결정 B3/B4/B9/E5)
#  (지혈 2023-3의 3-1·3-2는 같은 문제의 두 복원이라 떼지 않음)
SUB26 = {('AX', '2025', '4-1'), ('PN', '2025', '7-2'), ('PN', '2025', '3-2')}
# 10-25 앞 문항 블록(답·해설 칸)에 삼켜진 다음 문항 → 따로 떼어 낸 블록(cut=True — assemble MAPCUT으로 직접 연결 · 자동 매칭·id 번호에 안 들어감)
#  키 (판, 주제, 칸, 머리 블록 번호) → (이 글로 시작하는 줄부터 떼기, 새 블록 번호) — 결정 A1/A2(DS 2021 4-1·4-2 Iodine) · A3/A4(PN 2021 8-1·8-2 증례) · A11(XE 2023 4번) · A12(HM 2020 15-1)
CUT = {('24', 'DS', '2021', '3'): ('4-1.', '4'), ('23', 'DS', '2021', '3'): ('4-1.', '4'),
       ('24', 'PN', '2021', '8'): ('8-1.', '8-1'), ('23', 'PN', '2021', '8'): ('8-1.', '8-1'),
       ('24', 'XE', '2023', '3'): ('4. 평상시와', '4'),
       ('23', 'HM', '2020', '15'): ('15-1.', '15-1')}
SUBL = re.compile(r'^\(?\s*(\d{1,2})\s*-\s*(\d)\s*\)?\s*[.．]?(?=\s|$)')   # '4-1.' · '(3-2)'
SUBP = re.compile(r'^\(\s*(\d)\s*\)\s*\S')   # '(2) …' — 머리 번호 + '-2'
YEAR = re.compile(r'^\s*[\[<]\s*(20\d\d)\s*년\s*(?:도)?\s*(?:[-–]\s*Pf\.?\s*([가-힣]{2,3})|([가-힣]{2,3})\s*교수님)?\s*[\]>]\s*$')
CUE = re.compile(r'[?？]|시오|하시오|하라|쓰기|쓰시|서술|설명|나열|비교|기술|채우|기입|빈칸|무엇|어떤|이유|차이|특징|기전|고르|골라|옳|맞는|틀린|아닌|중복|미복원|\(\s*\d\d|\(탈|\(짤|T/F|\(\s*\)|약은|약물|용어|효과|정의|경우|것은|것을|사용|치료|적응증|부작용|목적|복원|짤|표\s|보여주|이다\.|한다\.|should|because|used|rate|effect')
STRONG = re.compile(r'[?？]|시오|하시오|하라|쓰시|쓰기|고르|골라|옳|맞는|틀린|아닌|서술|설명|나열|중복|미복원|\[서술|\[단답|\(탈|\(\s*\d\d\s*[,)\-’\']|\(짤|T/F|\(\s*\)')
QEND = re.compile(r'[?？]|것은|시오')
ANS = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$')
def parse(ed, n):
    L = load(ed, n); blocks = []; cur = None; topic = None; sec = None; prof = ''; last = 0; inans = False
    for idx, (pg, l) in enumerate(L):
        s = l.strip()
        m = (TOPIC26 if ed == '26' else TOPICQ4 if ed == '23q4' else TOPIC).match(s)
        if m:
            t = m.group(1); topic = next((v for k, v in TKEY.items() if k in t), None); sec = None; cur = None; last = 0; inans = False; prof = ''
            if ed == '23q4': topic = TKEYQ4.get(t.strip(), 'SX')   # 4Q JB는 항불안제·구강건조증 + 진정수면제·약물상호작용(Q4KEEP 문항만)
            continue
        m = YEAR.match(s)
        if m and topic:
            nsec = m.group(1)
            if sec and int(nsec) > int(sec) and topic == 'HM': topic = 'BT'   # 24판: 지혈 뒤에 주제 헤더 없이 보톡스 <2023년>이 이어짐
            sec = nsec; prof = m.group(2) or m.group(3) or ''; last = 0; cur = None; inans = False; continue
        m = YEAR26.match(s) if ed == '26' else None
        if m and topic:
            sec = m.group(1); prof = m.group(2); last = 0; cur = None; inans = False; continue
        if not topic or not sec or topic == 'SX': continue
        if ed == '26' and cur is not None:
            ms = SUBL.match(s); mp = None if ms else SUBP.match(s)
            sk = f'{ms.group(1)}-{ms.group(2)}' if ms else (f"{str(cur['num']).split('-')[0]}-{mp.group(1)}" if mp else '')
            if sk and (topic, sec, sk) in SUB26 and sk != str(cur["num"]):   # 10-25 떼어 낸 소문항 안의 '(2) …' 답 줄은 다시 떼지 않음(PN 2025 (3-2) 답 '(2) somatic')
                cur = {'ed': ed, 'topic': topic, 'sec': sec, 'prof': prof, 'num': sk, 'pg': pg, 'pg2': pg, 'lines': [l], 'lp': [pg], 'sub': True}; blocks.append(cur); inans = False; continue
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
                cur = {'ed': ed, 'topic': topic, 'sec': sec, 'prof': prof, 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l], 'lp': [pg]}; blocks.append(cur); inans = False; last = nn; continue
            # 답안·해설 안에 삼켜진 다음 문항(직전 번호+1로 시작하고 문항형 문장으로 끝남) → 새 블록 (split=True: assemble이 기존 id 뒤에 번호를 붙임)
            if cur is not None and nn == last + 1:
                stem = [s]; hit_ans = False
                for _pg, x_ in L[idx + 1:idx + 21]:
                    xs = x_.strip()
                    if ANS.match(xs): hit_ans = True; break
                    if re.match(r'^\s*해설\s*[:：]', xs) or re.match(r'^\s*\d{1,2}\s*[.．)]', xs): break
                    stem.append(xs)
                # 문항형으로 끝나거나(? · 것은 · 시오), 명사로 끝나도 3줄 안에 곧바로 '답'이 오면 문항(예: 2021년 14번 "…검사의 종류, 기준, 산출방법")
                if QEND.search(" ".join(stem)) or (hit_ans and inans and len(stem) <= 3 and len("".join(stem)) >= 12):
                    cur = {'ed': ed, 'topic': topic, 'sec': sec, 'prof': prof, 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l], 'lp': [pg], 'split': True}; blocks.append(cur); inans = False; last = nn; continue
        if cur is not None:
            cur['lines'].append(l); cur['lp'].append(pg); cur['pg2'] = pg
            if ANS.match(s): inans = True
    out = []
    for x in blocks:   # 10-25 CUT — 삼켜진 다음 문항을 떼어 바로 뒤에 새 블록으로(글자·줄 순서 그대로)
        out.append(x); c_ = CUT.get((ed, x['topic'], x['sec'], str(x['num'])))
        if not c_: continue
        i_ = next((i for i, l in enumerate(x['lines']) if i and l.strip().startswith(c_[0])), None)
        assert i_ is not None, ('CUT 못 찾음', ed, x['topic'], x['sec'], x['num'], c_)
        y = {'ed': ed, 'topic': x['topic'], 'sec': x['sec'], 'prof': x['prof'], 'num': c_[1], 'pg': x['lp'][i_], 'pg2': x['lp'][-1], 'lines': x['lines'][i_:], 'lp': x['lp'][i_:], 'cut': True}
        x['lines'], x['lp'] = x['lines'][:i_], x['lp'][:i_]; x['pg2'] = x['lp'][-1]; out.append(y)
    if ed == '23q4': out = [x for x in out if x['topic'] not in Q4KEEP or (x['sec'], str(x['num'])) in Q4KEEP[x['topic']]]
    return out
if __name__ == '__main__':
    allb = {}
    for ed, n in (('25', 26), ('24', 40), ('23', 54), ('26', 26), ('23q4', 23)):
        b = parse(ed, n); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks')
        for x in b: print(f" {x['topic']}|{x['sec']}|{x['prof'][:3]:3}|{x['num']:>2}|p{x['pg']:<2}| {x['lines'][0][:48]}")
    json.dump(allb, open(J.work('PHARM', 'jb_blocks.json'), 'w'), ensure_ascii=False)
