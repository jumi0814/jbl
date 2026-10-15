"""예상문제(pred.txt) 문법·필드 검사 — guide/handoff/PRED26_BRIEF.md 2-3·2-4절
사용: .venv/bin/python tools/pred_check.py <SID> [--keys K1,K2] [--loose]
✗ = 고쳐야 함(종료 코드 1) · △ = 확인 권장. --loose = pr 없는 블록 허용(개선 전 파일 점검용)."""
import os, sys, re, json, importlib.util, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J
CIRC = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮'
def subject(sid):
    p = os.path.join(J.TOOLS, sid.lower(), 'subject.py')
    sp = importlib.util.spec_from_file_location('subject_' + sid, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def blocks(sid):
    out = []; cur = None
    for n, line in enumerate(open(os.path.join(J.TOOLS, sid.lower(), 'pred.txt'), encoding='utf-8'), 1):
        line = line.rstrip('\n')
        if line.startswith('@'):
            p = [x.strip() for x in (line[3:] if line.startswith('@P ') else line[1:]).split('|')]
            cur = {'k': p[0], 'n': n, 'f': {}, 'q': '', 'a': '', 'raw': line}
            for x in p[1:]:
                k, _, v = x.partition('='); cur['f'][k.strip()] = v.strip()
            out.append(cur)
        elif cur and line.startswith('Q:'): cur['q'] = line[2:].strip()
        elif cur and line.startswith('A:'): cur['a'] = line[2:].strip()
        elif cur and line.strip() and not line.startswith('#'): cur.setdefault('extra', []).append((n, line[:40]))
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('sid'); ap.add_argument('--keys'); ap.add_argument('--loose', action='store_true'); a = ap.parse_args()
    sid = a.sid.upper(); S = subject(sid); keys = set(a.keys.split(',')) if a.keys else None
    qids = set(json.load(open(J.work(sid, 'review', 'qids.json'), encoding='utf-8')).get('q', {}).keys()) if os.path.exists(J.work(sid, 'review', 'qids.json')) else set()
    if not qids:
        try: qids = set(json.load(open(J.work(sid, 'review', 'qids.json'), encoding='utf-8')).keys())
        except Exception: qids = set()
    pb = J.work(sid, 'pred26', 'pred_before.json'); old = {r['aid'] for r in json.load(open(pb, encoding='utf-8'))} if os.path.exists(pb) else set()
    B = blocks(sid); bad = warn = 0; seen_oid = {}; seen_q = {}; stat = {}
    def X(b, m):
        nonlocal bad; bad += 1; print(f'✗ {b["k"]} 줄 {b["n"]}: {m}')
    def W(b, m):
        nonlocal warn; warn += 1; print(f'△ {b["k"]} 줄 {b["n"]}: {m}')
    for b in B:
        if keys and b['k'] not in keys: continue
        f = b['f']; st = stat.setdefault(b['k'], {'활성': 0, '보관': 0, '상': 0, '중': 0, '하': 0, '그림빵': 0, '그림': 0})
        if b['k'] not in S.LECMAP and b['k'] not in getattr(S, 'LEC_ORDER', []): X(b, f'강의 키 {b["k"]} 없음')
        if not b['q']: X(b, 'Q: 없음')
        if not b['a']: X(b, 'A: 없음')
        for n, t in b.get('extra', []): W(b, f'Q:/A: 밖 줄 {n} "{t}" — 화면에 안 나옴')
        arch = f.get('x') == '1'; st['보관' if arch else '활성'] += 1
        pr = f.get('pr', '')
        if pr and pr not in ('상', '중', '하'): X(b, f'pr={pr} (상·중·하만)')
        if not pr and not arch and not a.loose: X(b, 'pr= 없음')
        if pr and not arch: st[pr] += 1
        why = f.get('why', '')
        if not why and not arch and not a.loose: X(b, 'why= 없음')
        if len(why) > 60: W(b, f'why {len(why)}자 — 짧게(≤40)')
        for i in [x for x in re.split(r'[,\s]+', f.get('b', '')) if x]:
            if qids and i not in qids: X(b, f'b={i}: 없는 문항 id')
        if f.get('oid'):
            if old and f['oid'] not in old: X(b, f'oid={f["oid"]}: pred_before에 없는 aid')
            if f['oid'] in seen_oid: X(b, f'oid 중복(줄 {seen_oid[f["oid"]]})')
            seen_oid[f['oid']] = b['n']
        for fp in [x for x in f.get('f', '').split(',') if x.strip()]:
            m = re.fullmatch(r'\s*([A-Z0-9]+):(\d+)\s*', fp)
            if not m: X(b, f'f={fp}: <KEY>:<쪽> 꼴'); continue
            k, p = m.group(1), int(m.group(2)); d = S.LECMAP.get(k, (None,))[0]
            if not d or not os.path.exists(os.path.join(J.work(sid, 'lec'), d, f'{p}.jpg')): X(b, f'f={fp}: 쪽 이미지 없음')
            st['그림'] += 1
        if 'm' in f or '그림빵' in f.get('t', ''):
            st['그림빵'] += 1
            if not f.get('f'): X(b, '그림빵인데 f= 없음')
            boxes = [x for x in f.get('m', '').split(';') if x.strip()]
            if not boxes: X(b, '그림빵인데 m= 없음')
            for bx in boxes:
                try:
                    v = [float(t) for t in bx.split(',')]
                    if len(v) != 4 or not all(0 <= t <= 100 for t in v) or v[0] >= v[2] or v[1] >= v[3]: X(b, f'm 상자 {bx} 범위')
                except ValueError: X(b, f'm 상자 {bx} 숫자 아님')
            na = sum(1 for c in CIRC if c in b['a'])
            if boxes and na != len(boxes): W(b, f'상자 {len(boxes)}개 · 답 번호 {na}개')
        qk = re.sub(r'\s+', '', b['q'])[:60]
        if qk and qk in seen_q and not arch: W(b, f'같은 문제 글(줄 {seen_q[qk]})')
        seen_q.setdefault(qk, b['n'])
    for k, s in stat.items(): print(f'  {k}: ' + ' · '.join(f'{a_} {v}' for a_, v in s.items()))
    print(f'✗ {bad} · △ {warn}'); return 1 if bad else 0
if __name__ == '__main__': sys.exit(main())
