"""강의별 작업 결과(work/<SID>/parts/)를 과목 파일에 합친다 — 여러 작업자가 한 과목의 annot/tables/pred를 동시에 고칠 때 충돌을 막는 용도.
- parts/annot_<키>.txt : @문항 블록들 → tools/<sid>/annot.txt 의 같은 id 블록을 통째로 교체(없던 id는 끝에 추가)
- parts/tables_<키>.txt: #TBL 블록들 → tables.txt 에서 k=<키> 블록을 전부 빼고 그 자리에 넣음
- parts/pred_<키>.txt  : @<키> 블록들 → pred.txt 에서 @<키> 블록을 전부 빼고 그 자리에 넣음
사용: .venv/bin/python tools/merge_parts.py <SID> [--check] [--stale-ok]   (--check: 형식 검사만)
낡은 조각 막기(10-10): split_parts가 parts/.stamp에 그때 tools/<sid>/annot·tables·pred의 sha1을 적고, merge(·--check)는 지금 tools 파일이
그와 다르면(= split 뒤 누가 tools를 직접 고침 — 합치면 그 수정이 소리 없이 되돌아감) 멈춘다. split_parts <SID> --force 뒤 다시(또는 알고 덮을 때만 --stale-ok).
merge가 끝나면 .stamp를 새 tools 파일로 갱신."""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J

def blocks(text, head):
    """head 정규식으로 시작하는 블록 목록 [(머리줄, [줄…])] + 첫 블록 앞 머리말"""
    pre, out, cur = [], [], None
    for l in text.split('\n'):
        if re.match(head, l): cur = (l, []); out.append(cur)
        elif cur is None: pre.append(l)
        else: cur[1].append(l)
    return pre, out
def join(pre, bl):
    s = '\n'.join(pre).rstrip('\n')
    parts = [s] if s else []
    for h, ls in bl:
        while ls and not ls[-1].strip(): ls = ls[:-1]
        parts.append('\n'.join([h] + ls))
    return '\n'.join(parts).rstrip('\n') + '\n'

def check_part(kind, text, sid, key, qids):
    errs = []
    for i, l in enumerate(text.split('\n'), 1):
        if not l.strip(): continue
        if kind == 'annot':
            if l.startswith('@'):
                cid = l[1:].split('|')[0].strip()
                if cid not in qids: errs.append(f'{i}: 없는 문항 {cid}')
                for f in l.split('|')[1:]:
                    k_, _, v = f.strip().partition('=')
                    if k_ not in ('v', 'yrs', 'yrsnote', 'lec', 'rel', 'pair'): errs.append(f'{i}: 모르는 필드 {k_}')
                    if k_ == 'v' and v not in ('ok', 'part', 'diff', 'none', 'na'): errs.append(f'{i}: v={v}')
            elif not re.match(r'^[AMNK]:', l): errs.append(f'{i}: 알 수 없는 줄 {l[:40]}')   # K: = 🎯 요점(10-05)
        elif kind == 'tables':
            if l.startswith('#TBL'):
                if f'k={key}' not in l.replace(' ', ''): errs.append(f'{i}: k={key} 아님')
            elif not re.match(r'^[HRN]:', l): errs.append(f'{i}: 알 수 없는 줄 {l[:40]}')
        elif kind == 'pred':
            if l.startswith('@'):
                if re.sub(r'^@P ', '@', l)[1:].split('|')[0].strip() != key: errs.append(f'{i}: @{key} 아님')
                m = re.search(r'b=([^|\s]*)', l)
                if m and m.group(1) and m.group(1) not in qids: errs.append(f'{i}: b={m.group(1)} 없는 문항')
            elif not re.match(r'^[QA]:', l): errs.append(f'{i}: 알 수 없는 줄 {l[:40]}')
        for m in re.finditer(r'\{jb:([^}]+)\}', l):
            if m.group(1) not in qids: errs.append(f'{i}: {{jb:{m.group(1)}}} 없는 문항')
    return errs

STAMP_FILES = ('annot.txt', 'tables.txt', 'pred.txt')
def stamp_now(d):
    import hashlib
    return {f: hashlib.sha1(open(os.path.join(d, f), 'rb').read()).hexdigest() for f in STAMP_FILES if os.path.exists(os.path.join(d, f))}
def write_stamp(sid):
    d = os.path.join(J.TOOLS, sid.lower()); pd = J.work(sid, 'parts'); os.makedirs(pd, exist_ok=True)
    json.dump(stamp_now(d), open(os.path.join(pd, '.stamp'), 'w'), indent=0)
def stale(sid):
    """낡은 조각이면 이유 문자열, 아니면 ''"""
    d = os.path.join(J.TOOLS, sid.lower()); sp = os.path.join(J.work(sid, 'parts'), '.stamp')
    if not os.path.exists(sp): return '.stamp 없음(split_parts 전 조각 — cloud_materials의 옛 조각일 수 있음)'
    old = json.load(open(sp)); now = stamp_now(d)
    ch = [f for f in STAMP_FILES if old.get(f) != now.get(f)]
    return ('split 뒤 tools/%s/%s가 바뀜' % (sid.lower(), '·'.join(ch))) if ch else ''

def main(sid, only_check, stale_ok=False):
    d = os.path.join(J.TOOLS, sid.lower()); pd = J.work(sid, 'parts')
    if not os.path.isdir(pd): print('parts 없음'); return 0
    why = stale(sid)
    if why and not stale_ok:
        print(f'✗ 낡은 조각 — {why}. 합치면 tools에서 직접 고친 것이 되돌아감 → .venv/bin/python tools/split_parts.py {sid} --force 뒤 다시(알고 덮을 때만 --stale-ok)')
        return 1
    qids = set(json.load(open(J.work(sid, 'review', 'qids.json'), encoding='utf-8'))['q'])
    bad = 0; files = sorted(os.listdir(pd))
    for f in files:
        m = re.match(r'(annot|tables|pred)_([A-Z0-9]+)\.txt$', f)
        if not m: continue
        e = check_part(m.group(1), open(os.path.join(pd, f), encoding='utf-8').read(), sid, m.group(2), qids)
        if e: bad += 1; print(f'✗ {f}:', *e[:10], sep='\n   ')
    if only_check or bad: print('검사', '통과' if not bad else f'실패 {bad}'); return bad
    # annot
    ap = os.path.join(d, 'annot.txt'); pre, bl = blocks(open(ap, encoding='utf-8').read(), r'^@')
    pos = {h[1:].split('|')[0].strip(): i for i, (h, _) in enumerate(bl)}; n = 0
    for f in files:
        if not f.startswith('annot_'): continue
        _, nb = blocks(open(os.path.join(pd, f), encoding='utf-8').read(), r'^@')
        for h, ls in nb:
            cid = h[1:].split('|')[0].strip(); n += 1
            if cid in pos: bl[pos[cid]] = (h, ls)
            else: pos[cid] = len(bl); bl.append((h, ls))
    open(ap, 'w', encoding='utf-8').write(join(pre, bl)); print(f'annot: {n}개 블록 반영')
    # tables / pred
    for kind, head, keyof in (('tables', r'^#TBL', lambda h: (re.search(r'k=\s*([A-Z0-9]+)', h) or [None, None])[1]),
                              ('pred', r'^@', lambda h: re.sub(r'^@P ', '@', h)[1:].split('|')[0].strip())):
        tp = os.path.join(d, kind + '.txt'); pre, bl = blocks(open(tp, encoding='utf-8').read(), head); n = 0
        for f in files:
            m = re.match(kind + r'_([A-Z0-9]+)\.txt$', f)
            if not m: continue
            key = m.group(1); _, nb = blocks(open(os.path.join(pd, f), encoding='utf-8').read(), head)
            if kind == 'pred' and any(h.startswith('@P ') for h, _ in bl):   # 이 과목 pred.txt가 '@P 키' 형식이면 맞춤(OMS1 assemble은 '@P'만 읽음)
                nb = [(re.sub(r'^@(?!P )', '@P ', h), ls) for h, ls in nb]
            idx = [i for i, (h, _) in enumerate(bl) if keyof(h) == key]
            at = idx[0] if idx else len(bl)
            bl = [b for i, b in enumerate(bl) if i not in set(idx)]
            at -= sum(1 for i in idx if i < at)
            bl[at:at] = nb; n += len(nb)
        open(tp, 'w', encoding='utf-8').write(join(pre, bl).replace('\n#TBL', '\n\n#TBL') if kind == 'tables' else join(pre, bl)); print(f'{kind}: {n}개 블록 반영')
    write_stamp(sid)
    return 0

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    sys.exit(1 if main(a[0].upper(), '--check' in a, '--stale-ok' in a) else 0)
