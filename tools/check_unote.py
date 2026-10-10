"""필기에 NEW 26 검사(10-10 사용자 '필기 아님!! 슬라이드 원문 내용에서 새로 추가된 걸 말하는거임 … 모든 새로 추가된 필기가 26강조/new 26이 되는게 절대 아냐!!')
{u:…} 안의 {n:…} · {n:…} 안의 {u:…} · U: 줄의 {u:} · {u:26 필기…} — lec_*.txt·annot·tables·pred
  .venv/bin/python tools/check_unote.py <SID> [--parts]   → 파일:줄 목록 + 끝줄 '<SID> 필기NEW26 n'(--parts면 work/<SID>/parts 조각도)"""
import os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import jblpaths as J
def u_on_note(ln):
    st, hit = [], (ln.startswith('U:') and '{u:' in ln) or bool(re.search(r'\{u:\s*(?:\d{2}\s)?필기', ln))
    for m in re.finditer(r'\{(\w+):|\{|\}', ln):
        if m.group(0) == '}':
            if st: st.pop()
            continue
        k = m.group(1) or '?'
        if (k == 'n' and 'u' in st) or (k == 'u' and 'n' in st): hit = True
        st.append(k)
    return hit
if __name__ == '__main__':
    a = sys.argv[1:]; S = a[0].upper(); D = os.path.join(J.TOOLS, S.lower()); n = 0
    fs = sorted(glob.glob(D + '/lec_*.txt')) + [os.path.join(D, x) for x in ('annot.txt', 'tables.txt', 'pred.txt')]
    if '--parts' in a: fs += sorted(glob.glob(J.work(S, 'parts') + '/*.txt'))
    for f in fs:
        if not os.path.exists(f): continue
        for i, ln in enumerate(open(f, encoding='utf-8'), 1):
            if u_on_note(ln): n += 1; print(f'  {os.path.relpath(f, J.ROOT)}:{i} {ln.strip()[:150]}')
    print(f'{S} 필기NEW26 {n}')
