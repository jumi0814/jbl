"""비교표·전체정리표 빠짐 점검(10-09 사용자 '정리표 비교표, 전체정리표 … 빠진거, 누락, 오류 등등 없는지') — 빌드 없이 원고만 읽음.
강의마다: ① 정리본 카드(주제)가 전체정리표(sum=1) 어느 행에도 안 걸리는 것(카드 제목·국문 부제 낱말로 대략) ② 그 강의 기출(카드 jb=·E: id)이
   전체정리표 ★ 칸·비교표 어디에도 {jb:} 칩으로 없는 것 ③ 표 꼴(R: 칸 수 > H: 칸 수 · 빈 칸 · 열 8개↑) ④ 표에 쓴 {jb:} id가 없는 문항.
  .venv/bin/python tools/table_audit.py <SID> [--md work/review_final2/TA_<SID>.md]"""
import os, sys, re, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import jblpaths as J
a = sys.argv[1:]; S = a[0].upper(); sid = S.lower(); out = None
if '--md' in a: out = a[a.index('--md') + 1]
sys.path.insert(0, os.path.join(J.TOOLS, sid)); import lecparse as LP
LEC = LP.load_all()
QJ = {}
qf = os.path.join(J.WORK, S, 'review', 'qids.json')   # tools/dump_review.py가 만듦(문항 id → 강의 lk·tier·v)
if os.path.exists(qf): QJ = json.load(open(qf, encoding='utf-8')).get('q', {})
qids = set(QJ)
T = []; cur = None
for n, l in enumerate(open(os.path.join(J.TOOLS, sid, 'tables.txt'), encoding='utf-8'), 1):
    l = l.rstrip('\n')
    if l.startswith('#TBL'):
        p = [x.strip() for x in l[4:].split('|')]
        cur = {'title': p[0], 'k': next((x[2:] for x in p if x.startswith('k=')), ''), 'sum': any(x.replace(' ', '') == 'sum=1' for x in p), 'H': [], 'R': [], 'N': [], 'line': n}; T.append(cur)
    elif cur and l.startswith('H:'): cur['H'] = [c.strip() for c in l[2:].split('|')]
    elif cur and l.startswith('R:'): cur['R'].append((n, [c.strip() for c in l[2:].split('|')]))
    elif cur and l.startswith('N:'): cur['N'].append(l[2:].strip())
norm = lambda t: re.sub(r'[\s·/()\-—:,.]+', '', LP._plain(t)).lower()
lines = [f'# {S} 비교표·전체정리표 빠짐 점검(table_audit)\n']
tot = collections.Counter()
for L in LEC:
    k = L['k']; tabs = [t for t in T if t['k'] == k]; sums = [t for t in tabs if t['sum']]
    alltxt = ' '.join(c for t in tabs for _, r in t['R'] for c in r) + ' ' + ' '.join(x for t in tabs for x in t['N'])
    sumtxt = norm(' '.join(c for t in sums for _, r in t['R'] for c in r))
    jbs = collections.OrderedDict()
    for c in L['cards']:
        for i in c['jb'] + [i for b in c['body'] if b[0] == 'E' for i in b[1][0]]: jbs.setdefault(i, c['ko'] or c['en'])
    for i, q in QJ.items():
        if q.get('lk') == k and q.get('tier') != 'C' and q.get('v') != 'na': jbs.setdefault(i, '(카드 미연결)')
    intab = set(re.findall(r'\{jb:([^}]+)\}', alltxt))
    miss_jb = [(i, t) for i, t in jbs.items() if i not in intab]
    miss_card = []
    for c in L['cards']:
        keys = [w for w in re.split(r'[\s·/()\-—:,.]+', LP._plain(c['en'] + ' ' + c['ko'])) if len(w) >= 3]
        hit = sum(1 for w in keys if norm(w) and norm(w) in sumtxt)
        if keys and hit == 0: miss_card.append(f"{c['en']} · {c['ko']}")
    shape = []
    for t in tabs:
        h = len(t['H'])
        if h > 7: shape.append(f"「{t['title'][:40]}」 열 {h}개(7개 넘음)")
        for n, r in t['R']:
            if h and len(r) > h: shape.append(f"tables.txt:{n} 칸 {len(r)} > 머리 {h}")
            if any(not c for c in r[1:]): shape.append(f"tables.txt:{n} 빈 칸")
    bad_id = sorted({i for i in intab if qids and i not in qids})
    tot.update(jb=len(miss_jb), card=len(miss_card), shape=len(shape), badid=len(bad_id))
    lines.append(f"## {k} — 비교표 {len(tabs) - len(sums)} · 전체정리표 {len(sums)} · 카드 {len(L['cards'])} · 기출 {len(jbs)}")
    if not sums: lines.append('- ⚠ 전체정리표(sum=1) 없음')
    lines.append(f"- 표에 {{jb:}} 칩이 없는 기출 {len(miss_jb)}: " + (' · '.join(f'{i}({t[:18]})' for i, t in miss_jb) or '없음'))
    lines.append(f"- 전체정리표 행에 안 걸리는 카드(대략) {len(miss_card)}: " + (' / '.join(miss_card) or '없음'))
    if shape: lines.append('- 표 꼴: ' + ' · '.join(shape))
    if bad_id: lines.append('- ✗ 없는 문항 id: ' + ' '.join(bad_id))
    lines.append('')
lines.append(f"합계: 칩 없는 기출 {tot['jb']} · 안 걸리는 카드 {tot['card']} · 표 꼴 {tot['shape']} · 없는 id {tot['badid']}")
txt = '\n'.join(lines)
if out: os.makedirs(os.path.dirname(out), exist_ok=True); open(out, 'w', encoding='utf-8').write(txt + '\n')
print(txt if not out else lines[-1])
