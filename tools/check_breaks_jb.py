"""10-05 JB 원문(문제·답·해설·다른 판본) 줄바꿈 점검 — 빌드된 팩에서 '이어져야 할 줄'(앞 줄이 문장부호 없이 끝나고 다음 줄이 이어지는 말)을 셈.
  .venv/bin/python tools/check_breaks_jb.py [SID…]  (표본 출력)"""
import sys, re, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'tools')); sys.path.insert(0, os.path.join(ROOT, 'tools', 'cons'))
import jblpaths as J, reflow
from bs4 import BeautifulSoup
SIDS = [a.upper() for a in sys.argv[1:]] or ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
cnt = collections.Counter(); ex = collections.defaultdict(list)
CONT_END = re.compile(r'(?:따라|따른|대한|위한|관한|의한|통해|통하여|하는|되는|있는|없는|같은|하여|하고|되어|하며|되며|이며|으며|에서|으로|에게|부터|까지|처럼|보다|에는|에도|지만|는데|이나|거나|및|[을를에의]|[,，])$')
for S in SIDS:
    P = J._load_js(os.path.join(ROOT, 'docs', 'packs', S + '.js'))
    for q, h in P['cards'].items():
        s = BeautifulSoup(h, 'html.parser')
        for box in s.select('.jbans .lines, .oth .lines, .qtext'):
            L = [re.sub(r'\s+', ' ', x.get_text(' ', strip=True)) for x in box.select('.ln')]
            for a, b in zip(L, L[1:]):
                if not a or not b or reflow.STARTER.match(b) or reflow.LABEL.match(b): continue
                if re.search(r'[.?!:：;)\]”"…]$', a): continue
                if CONT_END.search(a) or re.match(r'^[a-z「『(]', b): k = '이어질 줄'
                else: continue
                cnt[S] += 1
                if len(ex[S]) < 5: ex[S].append(f'{q}: …{a[-35:]!r} | {b[:35]!r}')
for S in SIDS: print(S, cnt[S]); [print('   ', x) for x in ex[S]]
print('합계', sum(cnt.values()))
