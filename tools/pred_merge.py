"""예상문제 조각 합치기: work/<SID>/pred26/pred_<묶음>.txt(맡은 강의 블록 전부를 새로 쓴 것) → tools/<sid>/pred.txt
- 조각에 든 강의 키의 블록을 pred.txt에서 모두 빼고, 그 키의 첫 블록 자리에 조각 블록을 넣음(다른 강의 블록·순서는 그대로)
- 안전: 조각에 없는 옛 aid(oid로도 안 이어지고 Q 글자도 같지 않은 것)가 있으면 멈춤 — 기존 문항은 지우지 않고 x=1로 보관해야 함(PRED26_BRIEF 2-1)
사용: .venv/bin/python tools/pred_merge.py <SID> <조각 파일…> [--dry]"""
import os, sys, re, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J
def split(text):
    """[(키, 블록 글)] — 블록 = '@' 줄부터 다음 '@' 줄 앞까지(앞의 머리 글은 키 None)"""
    out = []; cur_k = None; buf = []
    for line in text.split('\n'):
        if line.startswith('@'):
            if buf: out.append((cur_k, '\n'.join(buf)))
            h = line[3:] if line.startswith('@P ') else line[1:]
            cur_k = h.split('|')[0].strip(); buf = [line]
        else: buf.append(line)
    if buf: out.append((cur_k, '\n'.join(buf)))
    return out
def slug(*xs):
    t = '|'.join(xs); base = re.sub(r'[^a-z0-9가-힣]+', '', t.lower())[:24]
    return base + '_' + hashlib.md5(t.encode('utf-8')).hexdigest()[:6]
def aids(sid, blocks, new=False):
    s = set()
    for k, b in blocks:
        if k is None: continue
        q = next((l[2:].strip() for l in b.split('\n') if l.startswith('Q:')), '')
        m = re.search(r'\|\s*oid=([^|\n]+)', b.split('\n')[0])
        if m: s.add(m.group(1).strip())   # oid가 있으면 화면 aid = oid(build4 pred_aid) — Q 글자를 또 고쳐도 기록은 oid로 이어짐(10-27b)
        else: s.add(f'{sid}:P:{slug(q)}')
        if new: s.add(f'{sid}:P:{slug(q)}')
    return s
def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]; dry = '--dry' in sys.argv
    sid = a[0].upper(); P = os.path.join(J.TOOLS, sid.lower(), 'pred.txt')
    base = split(open(P, encoding='utf-8').read())
    parts = [split(open(f, encoding='utf-8').read().strip('\n')) for f in a[1:]]
    keys = {}
    for i, pb in enumerate(parts):
        for k, _ in pb:
            if k is None: continue
            if k in keys and keys[k] != i: raise SystemExit(f'✗ 강의 {k}가 두 조각에 있음')
            keys[k] = i
    old = aids(sid, [(k, b) for k, b in base if k in keys]); new = aids(sid, [x for pb in parts for x in pb], True)
    lost = sorted(old - new)
    if lost: raise SystemExit('✗ 조각에서 사라진 옛 문항(지우지 말고 x=1로): ' + ', '.join(lost[:20]) + (' …' if len(lost) > 20 else ''))
    out = []; placed = set()
    for k, b in base:
        if k in keys:
            if k not in placed:
                placed.add(k); out += [bb for kk, bb in parts[keys[k]] if kk == k]
            continue
        out.append(b)
    for k, i in keys.items():
        if k not in placed: out += [bb for kk, bb in parts[i] if kk == k]   # pred.txt에 없던 새 강의(예 PHARM ANX) — 끝에
    txt = '\n'.join(x.rstrip('\n') for x in out).rstrip('\n') + '\n'
    n0 = sum(1 for k, _ in base if k); n1 = txt.count('\n@')+ (1 if txt.startswith('@') else 0)
    print(f'{sid}: 블록 {n0} → {n1} · 바꾼 강의 {sorted(keys)} · 옛 문항 보존 ✓({len(old)})')
    if not dry: open(P, 'w', encoding='utf-8').write(txt)
if __name__ == '__main__': main()
