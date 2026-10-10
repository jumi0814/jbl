"""구조만 바꿨는지 검사(10-08 사용자 '내용은 절대 건드리지 말고 구조만 정돈') — 원고(lec_*.txt·annot.txt·tables.txt·pred.txt)의 글자를
기준본(git, 기본 HEAD)과 비교한다. 띄어쓰기·구분 기호(' / '·' · '·' — '·•·①~⑳·콜론)·줄 머리(M: · - · = · K: …)·줄 나눔·조각 순서는 무시하고,
나머지 글자 수(글자마다 개수)가 하나라도 다르면 ✗ — 낱말을 바꾸거나 빼거나 더한 것.
  .venv/bin/python tools/struct_diff.py <SID> [--ref <커밋>]   → 파일마다 ✓/✗ · ✗이면 늘어난·줄어든 글자와 바뀐 줄 몇 개"""
import os, sys, re, subprocess, collections, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import jblpaths as J
a = sys.argv[1:]; ref = 'HEAD'
if '--ref' in a: i = a.index('--ref'); ref = a[i + 1]; del a[i:i + 2]
S = a[0].upper(); sid = S.lower(); D = os.path.join(J.TOOLS, sid)
PRE = re.compile(r'^\s*(?:[A-Z]{1,2}\d?:|=|-|#{1,3}|@[A-Z]+)\s?')
STRUCT = re.compile(r'[\s/·•①-⑳:：—]+')   # '—'(D2가 ' — ' → ' / '로 바꾸는 구분 기호 — 10-10)
def norm(t): return STRUCT.sub('', ''.join(PRE.sub('', l) for l in t.split('\n')))
bad = 0
for f in sorted(os.listdir(D)):
    if not (f.startswith('lec_') and f.endswith('.txt') or f in ('annot.txt', 'tables.txt', 'pred.txt')): continue
    new = open(os.path.join(D, f), encoding='utf-8').read()
    old = subprocess.run(['git', '-C', J.ROOT, 'show', f'{ref}:tools/{sid}/{f}'], capture_output=True, text=True).stdout
    if old == new: continue
    A, B = collections.Counter(norm(old)), collections.Counter(norm(new))
    ch = sum(1 for x, y in zip(old.split('\n'), new.split('\n')) if x != y)
    TK = lambda t: collections.Counter(re.findall(r'[^\s/·•①-⑳:：]+', ''.join(PRE.sub(' ', l) + ' ' for l in t.split('\n'))))
    if A == B:
        ta, tb = TK(old), TK(new)
        if ta != tb: print(f'⚠ {f}: 글자는 그대로지만 띄어쓰기가 바뀐 낱말 — 늘어남 {list((tb - ta).elements())[:6]} · 줄어듦 {list((ta - tb).elements())[:6]}'); continue
        print(f'✓ {f}: 글자 그대로(구조만) · 바뀐 줄 약 {ch}'); continue
    bad += 1; plus, minus = B - A, A - B
    print(f'✗ {f}: 늘어난 글자 {dict(plus.most_common(12))} · 줄어든 글자 {dict(minus.most_common(12))}')
    ol, nl = old.split('\n'), new.split('\n')
    for g in [x for x in difflib.unified_diff(ol, nl, lineterm='', n=0) if x[:1] in '+-' and x[:3] not in ('+++', '---')][:8]: print('   ', g[:220])
print(f'{S}: 내용 글자가 바뀐 파일 {bad}')
sys.exit(1 if bad else 0)
