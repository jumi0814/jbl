"""새 연도 강의자료 반영: 강의 키 <KEY>가 새 파일로 바뀐 뒤, 옛 쪽 번호를 새 쪽으로 옮긴다(guide/handoff/26년도_업데이트_절차.md).
입력: work/<SID>/upd26/<KEY>_map.json = {"map": {"옛쪽": 새쪽|null}, "lecfix": {"옛쪽": 새쪽}}  (담당 작업자가 25 ↔ 26 대조로 만든 것)
고치는 곳: tools/<sid>/annot.txt·tables.txt·pred.txt · 같은 과목의 다른 lec_*.txt (lec_<KEY>.txt는 작업자가 직접 고침)
- [[KEY:n]] → [[KEY:새쪽]] · 새쪽이 없으면(26에서 빠짐) [[KEY5:n]]
- annot 머리 lec=KEY:n(또는 n-m) → 새쪽(없으면 lecfix) · 둘 다 없으면 그대로 두고 경고
- annot에서 lec=KEY 블록의 A:/M:/N: 줄 · tables의 k=KEY 블록 · pred의 @KEY 블록 안 맨글 'p.n'(인용 칩 밖) → 'p.새쪽' · 없으면 '25 p.n'
사용: .venv/bin/python tools/apply_map26.py <SID> <KEY> [--dry]"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J

def main(sid, key, dry):
    d = os.path.join(J.TOOLS, sid.lower()); m = json.load(open(J.work(sid, 'upd26', f'{key}_map.json'), encoding='utf-8'))
    mp = {int(k): v for k, v in m['map'].items()}; fix = {int(k): v for k, v in (m.get('lecfix') or {}).items()}
    old = key + '5'; st = {'cite': 0, 'cite5': 0, 'lec': 0, 'plain': 0, 'plain25': 0, 'warn': []}
    def cite(mm):
        n = int(mm.group(1)); v = mp.get(n)
        if v: st['cite'] += 1; return f'[[{key}:{v}]]'
        st['cite5'] += 1; return f'[[{old}:{n}]]'
    def plain(s):
        parts = re.split(r'(\[\[[^\]]*\]\]|\{jb:[^}]*\})', s)
        for i in range(0, len(parts), 2):
            def rp(mm):
                if re.search(r'(25|26)\s*$', parts[i][:mm.start()][-4:]): return mm.group(0)   # '25 p.n'·'26 p.n'은 그대로
                n = int(mm.group(2)); v = mp.get(n)
                if v: st['plain'] += 1; return f'{mm.group(1)}{v}'
                st['plain25'] += 1; return f'25 {mm.group(1)}{n}'
            parts[i] = re.sub(r'(?<![0-9A-Za-z])(p\.\s?)(\d+)(?![0-9])', rp, parts[i])
        return ''.join(parts)
    CITE = re.compile(r'\[\[' + key + r':(\d+)\]\]')
    files = ['annot.txt', 'tables.txt', 'pred.txt'] + sorted(f for f in os.listdir(d) if f.startswith('lec_') and f != f'lec_{key}.txt')
    for f in files:
        p = os.path.join(d, f); L = open(p, encoding='utf-8').read().split('\n'); blk = False
        for i, l in enumerate(L):
            if f == 'annot.txt' and l.startswith('@'):
                mm = re.search(r'lec=' + key + r':(\d+)(?:-(\d+))?', l); blk = bool(mm)
                if mm:
                    n = int(mm.group(1)); v = mp.get(n) or fix.get(n)
                    if v: L[i] = l[:mm.start()] + f'lec={key}:{v}' + l[mm.end():]; st['lec'] += 1
                    else: st['warn'].append(f'{l[:40]} — lec 옮길 쪽 없음')
                continue
            if f == 'tables.txt' and l.startswith('#TBL'): blk = bool(re.search(r'k=\s*' + key + r'\b', l)); continue
            if f == 'pred.txt' and l.startswith('@'): blk = re.sub(r'^@P ', '@', l)[1:].split('|')[0].strip() == key; continue
            l2 = CITE.sub(cite, l)
            if blk and f in ('annot.txt', 'tables.txt', 'pred.txt') and not l2.startswith('@'): l2 = plain(l2)
            L[i] = l2
        if not dry: open(p, 'w', encoding='utf-8').write('\n'.join(L))
    print(sid, key, {k: v for k, v in st.items() if k != 'warn'}); [print('  ⚠', w) for w in st['warn']]

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    main(a[0].upper(), a[1].upper(), '--dry' in sys.argv)
