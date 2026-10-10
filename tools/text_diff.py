"""원고 파일 전후 글자 비교(10-05 표·주석 정리) — 파일 전체의 글자 다중집합(공백·구분자·표 기호 제외)을 견줌. 빠진 글자 0이어야 함.
  .venv/bin/python tools/text_diff.py <파일> --save   → work/_before/<파일 경로> 에 저장
  .venv/bin/python tools/text_diff.py <파일>          → 빠진 글자(✗)·더한 글자"""
import os, sys, re, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
f = os.path.abspath(sys.argv[1]); rel = os.path.relpath(f, ROOT); bak = os.path.join(ROOT, 'work', '_before', rel)
if '--save' in sys.argv:
    os.makedirs(os.path.dirname(bak), exist_ok=True); open(bak, 'w', encoding='utf-8').write(open(f, encoding='utf-8').read()); print('saved', bak); sys.exit()
SEP = re.compile(r'[\s/:：;·,—–\-=→"“”\'‘’.()|#*{}\[\]]')
def cnt(t): return collections.Counter(SEP.sub('', re.sub(r'(?m)^[A-Z]{1,3}:\s*|\{r:|\{jb:|\{[nue]:', '', t)))
a, b = cnt(open(bak, encoding='utf-8').read()), cnt(open(f, encoding='utf-8').read())
lost, add = a - b, b - a
print('빠진 글자', sum(lost.values()), ''.join(sorted(lost.elements()))[:300])
print('더한 글자', sum(add.values()), ''.join(sorted(add.elements()))[:300])
print('RESULT', 'PASS' if not lost else 'FAIL')
