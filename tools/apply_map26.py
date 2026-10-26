"""새 연도 강의자료 반영: 강의 키 <KEY>가 새 파일로 바뀐 뒤, 옛 쪽 번호를 새 쪽으로 옮긴다(guide/handoff/26년도_업데이트_절차.md).
입력: work/<SID>/upd26/<KEY>_map.json = {"map": {"옛쪽": 새쪽|null}, "lecfix": {"옛쪽": 새쪽}}  (담당 작업자가 25 ↔ 26 대조로 만든 것)
고치는 곳: tools/<sid>/annot.txt·tables.txt·pred.txt · 같은 과목의 다른 lec_*.txt (lec_<KEY>.txt는 작업자가 직접 고침)
- [[KEY:n]] → [[KEY:새쪽]] · 새쪽이 없으면(26에서 빠짐) [[KEY5:n]]
- annot 머리 lec=KEY:n(또는 n-m) → 새쪽(없으면 lecfix) · 둘 다 없으면 그대로 두고 경고
- tables 머리줄(#TBL)의 src= 칩도 같은 규칙
- annot에서 lec=KEY 블록의 A:/M:/N: 줄 · tables의 k=KEY 블록 · pred의 @KEY 블록 안 맨글 'p.n'(인용 칩 밖) → 'p.새쪽' · 없으면 '25 p.n'
- pred 머리줄 f=KEY:n → 새쪽(없으면 f=KEY5:n) · 그림빵(m=)의 f 쪽이 바뀌면 경고(m 상자를 figmask로 다시 보기)
- pred Q: 줄이 바뀌면(쪽 인용) 그 블록 머리에 oid=<옛 aid>를 붙임(예상문제 aid = Q 글자 — ✓·✗·★·넘버링 기록이 끊기지 않게 · 이미 oid가 있으면 그대로) (10-16 스킬 점검 ✗7)
- 'p.n 필기'·'필기(p.n)'(옛 판 필기 쪽) → '25 p.n …' 그대로(새 쪽엔 그 필기가 없음 — 10-26) · '25 p.n'·'25 <교수> p.n'은 그대로
주의: 블록 안 맨글 p.n 중 다른 강의 쪽·JB 참고 쪽·쪽 번호 없는 '필기 "…"'의 앞 쪽까지 옮겨질 수 있다 → 옮긴 뒤 담당 검토자가 확인(25 필기 인용 칩은 [[KEY5:n]] — 필기만인 줄 칩은 메인이 apply 전에 [[KEY5:n]]으로).
사용: .venv/bin/python tools/apply_map26.py <SID> <KEY> [--dry] [--old <옛 보조 키 — 기본 KEY5>] [--redo]
  --old: 같은 해 개정판처럼 옛 판이 <KEY>5가 아닐 때(예 첫 26판을 보조 키 <KEY>6으로 둔 경우 --old <KEY>6)
  --redo: 이미 옮긴 표시(.applied)를 .applied.<날짜>로 옮기고 새 map으로 다시(새 판이 또 올 때만 — map.json은 새 판 기준이어야 함)"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J
from pred_merge import slug as pslug   # 예상문제 aid = f'{SID}:P:{slug(Q)}'(build4·pred_merge와 같은 셈)

def main(sid, key, dry, old=None, redo=False):
    d = os.path.join(J.TOOLS, sid.lower()); m = json.load(open(J.work(sid, 'upd26', f'{key}_map.json'), encoding='utf-8'))
    mp = {int(k): v for k, v in m['map'].items()}; fix = {int(k): v for k, v in (m.get('lecfix') or {}).items()}
    done = J.work(sid, 'upd26', f'{key}.applied')
    if redo and os.path.exists(done) and not dry: import datetime; os.rename(done, done + '.' + datetime.date.today().strftime('%m%d'))
    if os.path.exists(done) and not dry: print(sid, key, '이미 옮김(두 번 옮기면 쪽이 어긋남 — 새 판이면 --redo) —', done); return
    old = old or key + '5'; st = {'cite': 0, 'cite5': 0, 'lec': 0, 'plain': 0, 'plain25': 0, 'note25': 0, 'f': 0, 'oid': 0, 'warn': []}
    def cite(mm):
        n = int(mm.group(1)); v = mp.get(n)
        if v: st['cite'] += 1; return f'[[{key}:{v}]]'
        st['cite5'] += 1; return f'[[{old}:{n}]]'
    def plain(s):
        parts = re.split(r'(\[\[[^\]]*\]\]|\{jb:[^}]*\})', s)
        for i in range(0, len(parts), 2):
            def rp(mm):
                pre = parts[i][:mm.start()]; post = parts[i][mm.end():]
                if re.search(r'(25|26)\s*$', pre[-4:]) or re.search(r'(?:25|26) [가-힣]{2,4} $', pre[-10:]): return mm.group(0)   # '25 p.n'·'26 p.n'·'25 변민수 p.n'은 그대로
                n = int(mm.group(2)); v = mp.get(n)
                if n not in mp: return mm.group(0)   # 이 강의 쪽 범위 밖(교과서·다른 자료 쪽) — 그대로
                if re.match(r'\s*필기', post) or pre.endswith('필기('): st['note25'] += 1; return f'25 {mm.group(0)}'   # 옛 판 필기 쪽(10-26 GERI PSY — 'p.n 필기'·'필기(p.n)')은 새 쪽엔 그 필기가 없음 → '25 p.n' 그대로
                if mm.group(4):   # 'p.n-m' 범위 — 두 끝을 다 옮김(10-09: 앞 끝만 옮겨 'p.79-79'가 되던 것)
                    e = int(mm.group(4)); ve = mp.get(e)
                    if v and ve: st['plain'] += 1; return f'{mm.group(1)}{v}{mm.group(3)}{ve}'
                    st['plain25'] += 1; return f'25 {mm.group(0)}'
                if v: st['plain'] += 1; return f'{mm.group(1)}{v}'
                st['plain25'] += 1; return f'25 {mm.group(1)}{n}'
            parts[i] = re.sub(r'(?<![0-9A-Za-z])(p\.\s?)(\d+)(?:([-~–])(\d+))?(?![0-9])', rp, parts[i])
        return ''.join(parts)
    CITE = re.compile(r'\[\[' + key + r':(\d+)\]\]')
    files = ['annot.txt', 'tables.txt', 'pred.txt'] + sorted(f for f in os.listdir(d) if f.startswith('lec_') and f != f'lec_{key}.txt')
    for f in files:
        p = os.path.join(d, f); L = open(p, encoding='utf-8').read().split('\n'); blk = False; hdr = None
        for i, l in enumerate(L):
            if f == 'annot.txt' and l.startswith('@'):
                mm = re.search(r'lec=' + key + r':(\d+)(?:-(\d+))?', l); blk = bool(mm)
                if mm:
                    n = int(mm.group(1)); v = mp.get(n) or fix.get(n)
                    if v and mm.group(2):   # lec=KEY:n-m 범위는 끝도 옮김(옮길 쪽이 없으면 앞 끝 + 길이 그대로)
                        e = int(mm.group(2)); ve = mp.get(e) or fix.get(e) or (v + e - n); v = f'{v}-{ve}'
                    if v: L[i] = l[:mm.start()] + f'lec={key}:{v}' + l[mm.end():]; st['lec'] += 1
                    else: st['warn'].append(f'{l[:40]} — lec 옮길 쪽 없음')
                continue
            if f == 'tables.txt' and l.startswith('#TBL'): blk = bool(re.search(r'k=\s*' + key + r'\b', l)); L[i] = CITE.sub(cite, l); continue   # 머리줄 src= 칩도
            if f == 'pred.txt' and l.startswith('@'):
                blk = re.sub(r'^@P ', '@', l)[1:].split('|')[0].strip() == key; hdr = i
                def fmv(mm):   # 머리줄 f=KEY:n(쉼표 여럿) — 새쪽, 없으면 옛 보조 키
                    def one(x):
                        q = re.fullmatch(r'(\s*)' + key + r':(\d+)(\s*)', x)
                        if not q: return x
                        v = mp.get(int(q.group(2))); st['f'] += 1
                        return f'{q.group(1)}{key}:{v}{q.group(3)}' if v else f'{q.group(1)}{old}:{q.group(2)}{q.group(3)}'
                    return mm.group(1) + ','.join(one(x) for x in mm.group(2).split(','))
                l2 = re.sub(r'(\|\s*f=)([^|]*)', fmv, l)
                if l2 != l and re.search(r'\|\s*m=', l): st['warn'].append(f'{l[:50]} — 그림빵 f 쪽이 바뀜: m 상자를 figmask 미리보기로 다시 확인')
                L[i] = l2; continue
            l2 = CITE.sub(cite, l)
            if blk and f in ('annot.txt', 'tables.txt', 'pred.txt') and not l2.startswith('@'): l2 = plain(l2)
            if f == 'pred.txt' and l.startswith('Q:') and l2 != l and hdr is not None and not re.search(r'\|\s*oid=', L[hdr]):
                L[hdr] = L[hdr].rstrip() + f' | oid={sid}:P:{pslug(l[2:].strip())}'; st['oid'] += 1   # Q 글자가 바뀌면 옛 aid로 기록 잇기
            L[i] = l2
        if not dry: open(p, 'w', encoding='utf-8').write('\n'.join(L))
    if not dry: open(done, 'w').write('1')
    print(sid, key, {k: v for k, v in st.items() if k != 'warn'}); [print('  ⚠', w) for w in st['warn']]

if __name__ == '__main__':
    av = sys.argv[1:]; old = None
    if '--old' in av: i = av.index('--old'); old = av[i + 1].upper(); del av[i:i + 2]
    a = [x for x in av if not x.startswith('--')]
    main(a[0].upper(), a[1].upper(), '--dry' in av, old, '--redo' in av)
