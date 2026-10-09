"""필기 쪽 강조 점검(10-09 사용자 '필기파트 … 강조 표시는 최대한 없애고 강의자료 원문 위주로' · RULES 7 끝 · QA 34) — 빌드 없이 원고만.
{n:…} 안 · U: 줄 · '필기:'/'NN 필기(p.N):' 라벨 M 줄의 {r:}·==·**를 센다(P: 💬 줄 제외). 예외(기출 근거·교수 강조·정정 함정)가 있어 0이 목표는 아님
→ 지난 배포보다 늘지 않는지 · --list 목록을 눈으로.
  .venv/bin/python tools/check_nred.py <SID> [--list]"""
import os, sys, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import jblpaths as J
a = sys.argv[1:]; S = a[0].upper(); sid = S.lower(); LIST = '--list' in a
EMPH = re.compile(r'\{r:|==|\*\*')
def nspans(s):
    out, i = [], 0
    while (j := s.find('{n:', i)) >= 0:
        d, k = 0, j + 3
        while k < len(s) and not (s[k] == '}' and d == 0):
            d += (s[k] == '{') - (s[k] == '}'); k += 1
        out.append(s[j + 3:k]); i = k + 1
    return out
hits = []
fs = sorted(glob.glob(os.path.join(J.TOOLS, sid, 'lec_*.txt'))) + [os.path.join(J.TOOLS, sid, x) for x in ('tables.txt', 'annot.txt', 'pred.txt')]
for f in fs:
    if not os.path.exists(f): continue
    for n, l in enumerate(open(f, encoding='utf-8'), 1):
        l = l.rstrip('\n')
        if l.startswith('P:'): continue
        segs = [x for x in nspans(l) if EMPH.search(x)]
        if l.startswith('U:') and EMPH.search(l): segs.append(l[2:])
        if re.match(r'^M:\s*(?:\d{2}\s)?필기(?:\s?\([^)]*\))?\s*:', l) and EMPH.search(l): segs.append(l[2:])
        hits += [f'{os.path.basename(f)}:{n} {x[:80]}' for x in segs]
if LIST: print('\n'.join(hits))
print(f'{S} 필기 쪽 강조 {len(hits)}')
