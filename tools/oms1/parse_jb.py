import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json
BASE=J.JBX
def rd(p): return open(p,'rb').read().decode('utf-8','replace').replace('\r','').replace('\x02','')
def load(ed,n):
    lines=[]
    for i in range(1,n+1):
        t=rd(f'{BASE}OMS1_20{ed}/{i}.txt')
        L=t.split('\n'); first=True
        for l in L:
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*',l): first=False; continue
            if l.strip(): first=False
            lines.append((i,l.rstrip()))
    return lines
SEC=[(r'^\s*(20\d\d)\s*-\s*3Q\s*$','exam'),(r'^\[\s*Dentofacial deformity\s*\]\s*(2021)?\s*$','sbm'),(r'^\s*(2021|2020)\s*$','year'),
     (r'^<\s*정필훈','jph'),(r'^<\s*서병무 교수님 임플란트','sbmimp'),(r'^\[\s*(Treatment planning for implant|즉시임플란트|Implant and the growth factor)\s*\]','sub'),
     (r'^\[추가복원된 탈문항\]','extra')]
ANS=re.compile(r'^\s*\[?답\]?\s*[:：)]?|^\s*답\s*$')
def parse(ed,n):
    L=load(ed,n); blocks=[]; cur=None; sec='머리말'; prof=''; exp=1; seen_ans=True
    cand=[]
    for idx,(pg,l) in enumerate(L):
        m=re.match(r'^\s*(\d{1,2})\s*\.?\s+(\S.*)$',l) or re.match(r'^\s*(\d{1,2})\.(\S.*)$',l)
        if m: cand.append((idx,int(m.group(1))))
    candset={i:n_ for i,n_ in cand}
    def has_answer_before_next(idx,num):
        # look ahead until a line that is candidate with num+1 or a section header
        for j in range(idx+1,min(len(L),idx+400)):
            t=L[j][1]
            if ANS.match(t): return True
            if any(re.match(p,t) for p,_ in SEC) or re.match(r'^\[(.+?)\s*교수님\]\s*$',t): return False
            if j in candset and candset[j]==num+1 and j-idx>1:
                # next question reached without answer
                return False
        return False
    for idx,(pg,l) in enumerate(L):
        hit=None
        for p,kind in SEC:
            mm=re.match(p,l)
            if mm: hit=(kind,mm)
        mp=re.match(r'^\[(.+?)\s*교수님\]\s*$',l)
        if hit:
            kind,mm=hit
            if kind=='exam': sec=mm.group(1)+'-3Q'; exp=1 if ed!='25' else exp
            elif kind=='sbm': sec='서병무 DD 2021'; exp=1
            elif kind=='year':
                if sec.startswith('서병무 임플란트'): sec=sec+' '+mm.group(1) if mm.group(1) not in sec else sec
                else: sec='서병무 DD '+mm.group(1)
                exp=1
            elif kind=='jph': sec='정필훈 기출'; exp=1
            elif kind=='sbmimp': sec='서병무 임플란트(13-21)'; exp=1
            elif kind=='sub': sec='서병무 임플란트: '+mm.group(1); exp=1
            elif kind=='extra': 
                cur={'ed':ed,'sec':sec,'prof':prof,'num':'추가','pg':pg,'lines':[l]}; blocks.append(cur); continue
            cur=None; continue
        if mp and ed=='25': prof=mp.group(1); cur=None; continue
        if idx in candset and sec!='머리말':
            num=candset[idx]
            near=' '.join(x[1] for x in L[idx:idx+3])
            cross=bool(re.search(r'\(20\d\d\.?\s*\d+\s*번\)',near)) or ('미복원' in l)
            ans_near=any(ANS.match(x[1]) for x in L[idx+1:idx+7])
            qlike=bool(re.search(r'[?？]|시오|하라|은\?|는\?|쓰|고르|설명|나열|서술|기술|이름|문제|\(20|\[객|\[주|★|\(서술형|\(객관식|\(단답형|목적|종류|리스트|모양|갯수|의미',near))
            ok = cross or ans_near or num>=9 or (qlike and has_answer_before_next(idx,num))
            if (num==exp or (cross and num in (exp,exp-1))) and ok:
                cur={'ed':ed,'sec':sec,'prof':prof,'num':num,'pg':pg,'lines':[l]}; blocks.append(cur); exp=num+1; continue
        if cur is not None: cur['lines'].append(l); cur['pg2']=pg
    return blocks
# ---- 26판(2026 3Q JB — 2025년 시험까지): 쪽 머리 '구강악안면외과학 1' + 쪽 번호 줄 · 연도 칸 '20NN-3Q' · '[○○○ 교수님]' · 문항 = 'N. …'(점 있는 번호)
# 2025-3Q 칸은 1번부터 차례(N = 앞 번호+1), 2024·2023·2022 칸은 25판 번호 그대로(25 칸으로 옮긴 문항은 빠져 번호가 띔 → 앞 번호보다 큰 번호만)
# 머리말(1~2쪽 멘트·'[24 년도 JB 구성] 1. 23 년도 기출 …'·수업 표)과 해설 안 번호 줄('1. 두경부영역에 …' — 앞 번호보다 작음)은 문항 아님(RULES 0-1)
def load26(n):
    lines=[]
    for i in range(1,n+1):
        L=rd(f'{BASE}OMS1_2026/{i}.txt').split('\n'); k=0
        if k<len(L) and L[k].strip()=='구강악안면외과학 1': k+=1
        if k<len(L) and re.fullmatch(r'\s*\d{1,3}\s*',L[k]): k+=1
        for l in L[k:]:
            if '무단인쇄' in l: continue
            lines.append((i,l.rstrip()))
    return lines
def parse26(n=16):
    blocks=[]; cur=None; sec='머리말'; prof=''; last=0
    for pg,l in load26(n):
        m=re.match(r'^\s*(20\d\d)-3Q\s*$',l)
        if m: sec=m.group(1)+'-3Q'; prof=''; last=0; cur=None; continue
        if sec=='머리말': continue
        mp=re.match(r'^\[(.+?)\s*교수님\]\s*$',l)
        if mp: prof=mp.group(1); cur=None; continue
        mq=re.match(r'^\s*(\d{1,2})\.\s*(\S.*)$',l)
        if mq:
            num=int(mq.group(1))
            if (num==last+1) if sec=='2025-3Q' else (num>last):
                cur={'ed':'26','sec':sec,'prof':prof,'num':num,'pg':pg,'lines':[l]}; blocks.append(cur); last=num; continue
        if cur is not None: cur['lines'].append(l); cur['pg2']=pg
    return blocks
_parse_old=parse
def parse(ed,n):
    return parse26(n) if ed=='26' else _parse_old(ed,n)
if __name__=='__main__':
    allb={}
    for ed,n in (('25',16),('24',20),('23',28),('26',16)):
        b=parse(ed,n); allb[ed]=b
        print(f'=== {ed}판: {len(b)} blocks')
        for x in b:
            txt='\n'.join(x['lines']); stem=' '.join(x['lines'][:2])[:58]
            print(f" {x['sec'][:14]:14}|{x['prof'][:3]:3}|{str(x['num']):>3}|p{x['pg']:<2}|{len(txt):5}|{'A' if re.search(r'답',txt) else '-'}| {stem}")
    json.dump(allb,open(J.work('OMS1', 'jb_blocks.json'), 'w'),ensure_ascii=False)
