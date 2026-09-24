# 강의 쪽별 텍스트층(<키>t/) + OCR(<키>o/) 합쳐 보기 — work/CONS/ 기준
import re,os,sys,json
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jblpaths as J
def dec(s):
    hi=sum(1 for c in s if 0xA0<=ord(c)<=0xFF)
    if hi>=max(2,len(s.strip())*0.4):
        return ''.join(chr(0x120-ord(c)) if 0xA0<=ord(c)<=0xFF else c for c in s)
    return s
def clean_lines(t):
    out=[]
    for l in t.split('\n'):
        l=dec(l).strip()
        l=re.sub(r'\s+',' ',l)
        if len(re.findall(r'[A-Za-z0-9가-힣]',l))<2: continue
        out.append(l)
    return out
def page(k,i):
    tl=clean_lines(open(f'{k}t/{i}.txt').read()) if os.path.exists(f'{k}t/{i}.txt') else []
    oc=clean_lines(open(f'{k}o/{i}.txt').read()) if os.path.exists(f'{k}o/{i}.txt') else []
    has_ko=sum(len(re.findall(r'[가-힣]',l)) for l in tl)>15
    tl_join=' '.join(tl).lower()
    keep=[]
    for l in oc:
        asc=len(re.findall(r'[A-Za-z0-9]',l)); ko=len(re.findall(r'[가-힣]',l))
        if ko>asc*0.6:
            if has_ko: continue
            keep.append('~'+l); continue
        if asc<4: continue
        toks=l.split(); good=[t for t in toks if re.fullmatch(r"[A-Za-z][A-Za-z\-'/,.():;%]{2,}",t)]
        if len(good)<2 and not re.search(r'\d',l): continue
        if len(good)<max(1,len(toks)*0.5): continue
        # skip if already in text layer
        key=re.sub(r'[^a-z0-9]','',l.lower())[:25]
        if key and key in re.sub(r'[^a-z0-9]','',tl_join): continue
        keep.append(l)
    return tl,keep
if __name__=='__main__':
    os.chdir(J.work('CONS'))
    k=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3])
    for i in range(a,b+1):
        tl,oc=page(k,i)
        print(f'[p{i}] S: '+' / '.join(oc)[:420])
        if tl: print('   N: '+' / '.join(tl)[:800])
