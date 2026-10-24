"""10-24 JB 전수 대조(사용자 '각 과목 jb 문제 누락 없는지 … 객관식 넘버링 서술형 단답형 등등 다 모조리 검토해서 빠진 문제, 교수님, 표기 등등') — 찾기만(고치지 않음).
  .venv/bin/python tools/jb_cover.py <SID> [--md work/_tmp/jbaudit/<SID>_auto.md]
① 분해 블록 ↔ 사이트 출처: 판본마다 parse_<sid>.parse가 낸 블록(판·칸·번호) 중 어느 카드의 '출처·다른 판본'(JB <판>판 · <칸> <번호>번)에도 없는 것
   → 가장 비슷한 카드(문제 글 앞부분 difflib 비율)와 함께 — 0.8↑ = 이미 합쳐진 같은 문제일 수 있음 · 그 아래 = 빠졌을 수 있음
② 원문 줄 ↔ 블록: 쪽 글(N.txt)에서 '번호로 시작하고 묻는 말(?·쓰시오·고르시오·서술·설명·무엇·옳은·틀린·기술·나열·쓰라·답하시오)'이 있는 줄이 어떤 블록 글에도 없으면(분해기가 놓친 문제)
③ 교수: 카드 data-profs 중 누구도 그 카드가 가리키는 블록의 칸 이름·글·그 쪽 머리(교수님)에 없으면(표기 확인용 — 칸 이름에 교수가 없는 판형은 많이 걸림)
④ 그림 쪽: manifest has_visual_content 쪽에 걸친 블록인데 카드에 그림(img.fig)이 없으면
⑤ 같은 판 안 같은 (칸, 번호)가 두 번 이상 · 블록 번호 건너뜀(칸 안에서 1,2,4 …)"""
import os, sys, re, json, difflib, importlib.util, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools')); import jblpaths as J
SID = sys.argv[1].upper(); sid = SID.lower(); MD = None
if '--md' in sys.argv: MD = sys.argv[sys.argv.index('--md') + 1]
TD = os.path.join(ROOT, 'tools', sid); sys.path.insert(0, TD); os.chdir(TD)
src = open(os.path.join(TD, 'assemble.py'), encoding='utf-8').read()
pname = 'parse_jb' if os.path.exists(os.path.join(TD, 'parse_jb.py')) else 'parse_' + sid
PM = __import__(pname)
m = re.search(r'^NPAGES\s*=\s*(\{[^}]*\})', src, re.M)
NP = eval(m.group(1)) if m else dict(PM.NPAGES)
P = J._load_js(os.path.join(ROOT, 'docs', 'packs', SID + '.js'))
norm = lambda t: re.sub(r'[\s ·•\-–—_:;,.()\[\]{}<>「」"\'“”‘’?!~/]+', '', t or '').lower()
TAG = re.compile(r'<[^>]+>')
def untag(h): return re.sub(r'\s+', ' ', TAG.sub(' ', h)).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').strip()
# 사이트 카드: 출처들·문제 글·교수·그림
cards = {}
for cid, h in P['cards'].items():
    refs = set((e, s.strip(), n) for e, s, n in re.findall(r'JB (\d\d(?:q4)?)판 · ([^"<]*?) (\S+?)번', h))
    q = re.search(r'<div class="qtext">(.*?)</div></div>', h, re.S)
    profs = (re.search(r'data-profs="([^"]*)"', h) or re.search(r'data-prof="([^"]*)"', h))
    cards[cid] = {'refs': refs, 'q': untag(q.group(1)) if q else '', 'all': untag(h), 'profs': [x for x in (profs.group(1) if profs else '').split('|') if x], 'fig': 'class="fig' in h or 'img class="fig' in h or '<img' in h}
REFS = collections.defaultdict(list)
for cid, c in cards.items():
    for r in c['refs']: REFS[r].append(cid)
def stemkey(t):
    t = re.sub(r'^\s*\(?\d{1,3}\s*[\.\)]?\s*', '', t.split('\n')[0] if len(norm(t.split('\n')[0])) >= 12 else t)
    return norm(t)[:45]
ALLN = {cid: norm(c['all']) for cid, c in cards.items()}
def owners(ed, x):
    """이 블록을 담은 카드: ① 출처 표기(같은 판·번호 + 칸 이름이 서로 포함) ② 블록 문제 글 앞 45자(정규화)가 카드 글에 그대로"""
    sn = norm(str(x['sec'])); out = set()
    for r, cs in REFS.items():
        if r[0] == ed and r[2] == str(x['num']) and (sn in norm(r[1]) or norm(r[1]) in sn): out.update(cs)
    k = stemkey(x['text'])
    if len(k) >= 10: out.update(cid for cid, a in ALLN.items() if k in a)
    return sorted(out)
def best(text):
    t = norm(text)[:120]; out = []
    for cid, c in cards.items():
        r = difflib.SequenceMatcher(None, t, norm(c['q'])[:120]).ratio()
        r2 = 1.0 if t[:40] and t[:40] in norm(c['all']) else 0
        out.append((max(r, r2), cid))
    out.sort(reverse=True); return out[:2]
QW = re.compile(r'\?|쓰시오|고르시오|서술|설명하|무엇|옳은|틀린|기술하|나열|쓰라|답하시오|고르면|아닌 것|맞는 것|적으시오|그리시오|이름은|종류|차이')
rep = [f'# {SID} JB 자동 대조 — 판본 {", ".join(f"{e}판 {n}쪽" for e, n in NP.items())} · 사이트 카드 {len(cards)}개\n']
tot = collections.Counter()
for ed, n in NP.items():
    try: B = PM.parse(ed, n)
    except Exception as e: rep.append(f'\n## {ed}판 — 분해 실패: {e}\n'); continue
    for x in B: x['text'] = '\n'.join(x['lines']).strip()
    man = {}
    try: man = {p['page_number']: p.get('has_visual_content') for p in json.load(open(os.path.join(J.JBX, f'{SID}_20{ed}', 'manifest.json'), encoding='utf-8'))['pages']}
    except Exception: pass
    rep.append(f'\n## {ed}판 — 블록 {len(B)}개\n')
    # ① 출처에 없는 블록
    miss = []
    for x in B:
        x['cids'] = owners(ed, x)
        if not x['cids']: miss.append(x)
    tot['unref'] += len(miss)
    rep.append(f'### ① 사이트 출처에 없는 블록 {len(miss)}개\n')
    for x in miss:
        b = best(x['text']); stem = re.sub(r'\s+', ' ', x['text'])[:150]
        tag = '합쳐졌을 수 있음' if b[0][0] >= 0.8 else ('비슷한 카드 있음' if b[0][0] >= 0.55 else '빠졌을 수 있음')
        rep.append(f'- [{tag}] {ed}판 {x["sec"]} {x["num"]}번 (p.{x["pg"]}) — {stem}\n  - 가장 비슷: {b[0][1]} ({b[0][0]:.2f}) · {b[1][1]} ({b[1][0]:.2f})')
    # ② 원문 줄이 블록에 없음
    allb = norm(' '.join(x['text'] for x in B)); lost = []
    for pg in range(1, n + 1):
        try: t = open(os.path.join(J.JBX, f'{SID}_20{ed}', f'{pg}.txt'), 'rb').read().decode('utf-8', 'replace')
        except Exception: continue
        for l in t.split('\n'):
            if re.match(r'^\s*(\d{1,3})\s*[\.\)]\s*\S', l) and QW.search(l) and len(norm(l)) >= 8 and norm(l) not in allb:
                lost.append((pg, l.strip()[:150]))
    tot['lost'] += len(lost)
    rep.append(f'### ② 원문에 있는데 어느 블록에도 없는 문제 줄 {len(lost)}개\n')
    rep += [f'- p.{pg}: {l}' for pg, l in lost]
    # ③ 교수 · ④ 그림 · ⑤ 중복·번호
    pf, fg = [], []
    for x in B:
        for cid in x.get('cids', []):
            c = cards[cid]; ctx = str(x['sec']) + ' ' + x['text']
            if c['profs'] and not any(p and p in ctx for p in c['profs']): pf.append(f'- {cid} 교수 {"·".join(c["profs"])} ↔ {ed}판 칸 「{x["sec"]}」 {x["num"]}번')
            pgs = range(int(x['pg']), int(x.get('pg2', x['pg'])) + 1)
            if any(man.get(p) for p in pgs) and not c['fig'] and ed == max(NP, key=lambda e: e.replace('q4', '')): fg.append(f'- {cid} ← {ed}판 {x["sec"]} {x["num"]}번 p.{x["pg"]} (그림 쪽인데 카드에 그림 없음 — 글만 있는 쪽일 수 있음)')
    rep.append(f'### ③ 교수 표기 확인 {len(pf)}개(칸 이름·글에 카드 교수 이름이 없음 — 판형 때문일 수 있음)\n'); rep += pf[:60] + ([f'- … 외 {len(pf) - 60}개'] if len(pf) > 60 else [])
    rep.append(f'### ④ 그림 쪽 블록인데 카드 그림 없음 {len(fg)}개\n'); rep += fg
    cnt = collections.Counter((str(x['sec']), str(x['num'])) for x in B); dup = [k for k, v in cnt.items() if v > 1]
    gaps = []
    for sec in dict.fromkeys(str(x['sec']) for x in B):
        nums = [int(x['num']) for x in B if str(x['sec']) == sec and re.fullmatch(r'\d+', str(x['num']))]
        if nums:
            exp = set(range(min(nums), max(nums) + 1)); g = sorted(exp - set(nums))
            if g: gaps.append(f'- 칸 「{sec}」 번호 빠짐 {g} (있는 번호 {min(nums)}~{max(nums)})')
    rep.append(f'### ⑤ 같은 칸·번호 중복 {len(dup)}개 · 번호 건너뜀 {len(gaps)}칸\n'); rep += [f'- 중복 「{s}」 {n_}번' for s, n_ in dup] + gaps
    tot['gap'] += len(gaps); tot['dup'] += len(dup); tot['prof'] += len(pf); tot['fig'] += len(fg)
rep.insert(1, f'요약: 출처 없는 블록 {tot["unref"]} · 블록 밖 문제 줄 {tot["lost"]} · 번호 건너뜀 {tot["gap"]}칸 · 중복 {tot["dup"]} · 교수 확인 {tot["prof"]} · 그림 확인 {tot["fig"]}\n')
txt = '\n'.join(rep)
if MD:
    os.makedirs(os.path.dirname(os.path.join(ROOT, MD)), exist_ok=True); open(os.path.join(ROOT, MD), 'w', encoding='utf-8').write(txt)
print(rep[1].strip())
