"""annot.txt 구조 정리 전후 글자 비교(10-05 JB 가독성) — 문항(@Q) 단위로 공백·구분자를 뺀 글자 다중집합을 견줌.
  .venv/bin/python tools/annot_diff.py <SID> --save   → work/<SID>/annot_before.txt 에 지금 원고 저장
  .venv/bin/python tools/annot_diff.py <SID>          → 저장본과 비교: 빠진 글자(✗ — 0이어야 함) · 더한 글자(라벨 등 — 확인용)"""
import os, sys, re, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SID = sys.argv[1].upper(); src = os.path.join(ROOT, 'tools', SID.lower(), 'annot.txt'); bak = os.path.join(ROOT, 'work', SID, 'annot_before.txt')
if '--save' in sys.argv:
    open(bak, 'w', encoding='utf-8').write(open(src, encoding='utf-8').read()); print('saved', bak); sys.exit()
SEP = re.compile(r'[\s/:：;·,—–\-=→"“”\'‘’.(){}*]')   # 강조 표기({r:}·**)를 빼도 빠진 글자로 안 잡힘(10-09 D5)
def blocks(t):
    out, cur = {}, None
    for ln in t.splitlines():
        m = re.match(r'^@(\S+)', ln)
        if m: cur = m.group(1); out[cur] = collections.Counter(); continue
        if cur is None: continue
        if ln.startswith('K:'): continue   # K 🎯는 다시 쓰기 허용 — A·M·N만 셈(10-05) · K는 눈으로
        ln = re.sub(r'^[AMN]:\s*|\{r:|\{n:|\{u:|\{e:|\{jb:', '', ln)
        out[cur].update(SEP.sub('', ln))
    return out
A, B = blocks(open(bak, encoding='utf-8').read()), blocks(open(src, encoding='utf-8').read())
bad = 0
for q in A:
    a, b = A[q], B.get(q, collections.Counter())
    lost, add = a - b, b - a
    if lost: bad += 1; print(f'✗ {q} 빠진 글자: {"".join(sorted(lost.elements()))[:200]}')
    if add: print(f'  {q} 더한 글자: {"".join(sorted(add.elements()))[:120]}')
for q in B:
    if q not in A: print(f'✗ {q} 새 문항 블록(원래 없음)'); bad += 1
print('RESULT', 'PASS' if not bad else f'FAIL {bad}')
