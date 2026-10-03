"""aid_lock.json 옛 항목에 단어 집합(tok)을 채운다 — 원고를 전면 재작성해 문장 해시(sig)가 거의 안 겹칠 때도
옛 카드(사용자가 표시를 남긴 카드)와 새 카드를 내용으로 맞출 수 있게 (tools/aidlock.py가 tok이 있으면 단어 Jaccard를 씀).
사용: .venv/bin/python tools/aidlock_enrich.py <git 커밋(옛 원고)> [SID ...]
옛 커밋의 tools/<sid>/lec_*.txt를 임시 폴더에 꺼내 lecparse로 읽고, 옛 카드의 aid(= card_aid 규칙)로 잠금 항목을 찾아 tok을 넣는다."""
import os, sys, re, json, subprocess, tempfile, importlib, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J, aidlock

def main(rev, sids):
    for sid in sids:
        d = os.path.join(J.TOOLS, sid.lower()); lp = os.path.join(d, 'aid_lock.json')
        if not os.path.exists(lp): print(sid, '잠금 없음'); continue
        lock = json.load(open(lp, encoding='utf-8'))
        tmp = tempfile.mkdtemp(prefix='oldlec_')
        names = subprocess.run(['git', '-C', J.ROOT, 'ls-tree', '--name-only', rev, f'tools/{sid.lower()}/'], capture_output=True, text=True).stdout.split()
        for n in names:
            if re.search(r'/(lec_[A-Z0-9]+\.txt|subject\.py|lecparse\.py|emph\.py)$', n):
                open(os.path.join(tmp, os.path.basename(n)), 'wb').write(subprocess.run(['git', '-C', J.ROOT, 'show', f'{rev}:{n}'], capture_output=True).stdout)
        sys.path.insert(0, tmp)
        for m in ('subject', 'lecparse', 'emph'): sys.modules.pop(m, None)
        try:
            LP = importlib.import_module('lecparse')
            ORDER = [f[4:-4] for f in os.listdir(tmp) if f.startswith('lec_')]
            n_set = 0
            for k in ORDER:
                L = LP.parse(os.path.join(tmp, f'lec_{k}.txt'))
                old = {(o['en'], o['ko']): o for o in lock.get(k, [])}
                for c in L['cards']:
                    o = old.get((c['en'], c['ko']))
                    if o is not None and not o.get('tok'):
                        o['tok'] = sorted(aidlock.tokens(c)); n_set += 1
            aidlock.save(lp, lock); print(f'{sid}: 옛 카드 {n_set}개에 단어 집합 추가')
        finally:
            sys.path.remove(tmp); shutil.rmtree(tmp, ignore_errors=True)
            for m in ('subject', 'lecparse', 'emph'): sys.modules.pop(m, None)

if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1], [a.upper() for a in sys.argv[2:]] or ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH'])
