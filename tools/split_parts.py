"""tools/<sid>/annot.txt·tables.txt·pred.txt → work/<SID>/parts/{annot,tables,pred}_<키>.txt 로 다시 나눈다(merge_parts.py의 반대).
여러 작업자가 강의별로 동시에 고칠 때, 커밋된 최신 내용에서 조각을 새로 만들어 시작하기 위한 것(work/는 커밋되지 않아 세션이 바뀌면 옛 조각이 남거나 없음).
- annot: 블록 머리 `lec=<키>:<쪽>`의 키(보조 키는 subject.IMG_ALIAS로 본 강의)로 나눔. lec=가 비었으면(미복원 등) 조각에 넣지 않음 — tools/<sid>/annot.txt에 그대로 남는다.
- tables: `k=<키>` · pred: `@<키>`
사용: .venv/bin/python tools/split_parts.py <SID> [--force]   (조각이 이미 있으면 --force 없이는 덮어쓰지 않음)"""
import os, sys, re, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J
from merge_parts import blocks, join

def main(sid, force):
    d = os.path.join(J.TOOLS, sid.lower()); pd = J.work(sid, 'parts'); os.makedirs(pd, exist_ok=True)
    sp = importlib.util.spec_from_file_location('subject_' + sid, os.path.join(d, 'subject.py')); S = importlib.util.module_from_spec(sp); sp.loader.exec_module(S)
    alias = getattr(S, 'IMG_ALIAS', {}); out = {}
    _, bl = blocks(open(os.path.join(d, 'annot.txt'), encoding='utf-8').read(), r'^@')
    for h, ls in bl:
        m = re.search(r'lec=([A-Z0-9]+)', h)
        if m: k = alias.get(m.group(1), m.group(1)); out.setdefault(('annot', k), []).append((h, ls))
    _, bl = blocks(open(os.path.join(d, 'tables.txt'), encoding='utf-8').read(), r'^#TBL')
    for h, ls in bl:
        m = re.search(r'k=\s*([A-Z0-9]+)', h)
        if m: out.setdefault(('tables', m.group(1)), []).append((h, ls))
    _, bl = blocks(open(os.path.join(d, 'pred.txt'), encoding='utf-8').read(), r'^@')
    for h, ls in bl:
        k = re.sub(r'^@P ', '@', h)[1:].split('|')[0].strip(); out.setdefault(('pred', k), []).append((re.sub(r'^@P ', '@', h), ls))
    n = 0
    for (kind, k), b in sorted(out.items()):
        p = os.path.join(pd, f'{kind}_{k}.txt')
        if os.path.exists(p) and not force: print(f'  있음(건너뜀 — --force로 덮어씀): {os.path.relpath(p, J.ROOT)}'); continue
        t = join([], b); t = t.replace('\n#TBL', '\n\n#TBL') if kind == 'tables' else t
        open(p, 'w', encoding='utf-8').write(t); n += 1; print(f'  {kind}_{k}.txt  {len(b)}블록')
    print(f'{sid}: 조각 {n}개 씀 → {os.path.relpath(pd, J.ROOT)}')

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    main(a[0].upper(), '--force' in a)
