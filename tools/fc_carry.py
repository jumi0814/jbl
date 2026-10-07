"""⚡ 암기 줄을 고친 뒤 플래시카드 기록(알아요·몰라요)이 얼마나 이어지는지 — 배포된 main 팩과 지금 docs 팩 비교(10-05).
  .venv/bin/python tools/fc_carry.py [SID…] [--ref <git 커밋 · 기본 origin/main>]
옛 ⚡ 줄 키가 새 팩에 그대로 있거나(같은 줄) 새 줄의 'ok'(넘겨받는 옛 키)에 있으면 '이어짐'. 끊긴 줄 목록은 work/_tmp/fc_carry_<SID>.md"""
import os, sys, re, json, html, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import jblpaths as J
args = sys.argv[1:]; ref = 'origin/main'
if '--ref' in args: i = args.index('--ref'); ref = args[i + 1]; del args[i:i + 2]
SIDS = [a.upper() for a in args] or ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
src = open(os.path.join(J.TOOLS, 'cons', 'build4.py'), encoding='utf-8').read()
i = src.index('def fchash'); j = src.index('\n', src.index('return', i)); exec(src[i:j])   # build4와 같은 키 함수
txt = lambda h: html.unescape(re.sub(r'<[^>]+>', '', h))
tot = [0, 0]
for S in SIDS:
    t = subprocess.run(['git', '-C', J.ROOT, 'show', f'{ref}:docs/packs/{S}.js'], capture_output=True, text=True).stdout
    if not t: print(S, f'{ref}에 팩 없음(새 과목)'); continue
    old = json.loads(t[t.index('{'):t.rindex('}') + 1]); new = J._load_js(os.path.join(J.DOCS, 'packs', S + '.js'))
    nk, ok = set(), set()
    for L in new['lect']:
        for r in L['recall']: nk.add('R:' + L['k'] + ':' + fchash(r['t'] + '|' + txt(r['h']))); ok.update(r.get('ok') or [])
    lost = []
    for L in old['lect']:
        for r in L['recall']:
            k = 'R:' + L['k'] + ':' + fchash(r['t'] + '|' + txt(r['h']))
            if k not in nk and k not in ok: lost.append((L['k'], r['t'], txt(r['h'])))
    n = sum(len(L['recall']) for L in old['lect']); tot[0] += n; tot[1] += n - len(lost)
    with open(os.path.join(J.TMP, f'fc_carry_{S}.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {S} 기록이 끊기는 옛 ⚡ 줄 {len(lost)}\n'); [f.write(f'- {k} · {t} · {h}\n') for k, t, h in lost]
    print(f'{S}: 옛 ⚡ {n} · 새 {sum(len(L["recall"]) for L in new["lect"])} · 기록 이어짐 {n - len(lost)} · 끊김 {len(lost)}')
print(f'합계: 기록 이어짐 {tot[1]}/{tot[0]}' + (f' ({100 * tot[1] // max(tot[0], 1)}%)' if tot[0] else ''))
