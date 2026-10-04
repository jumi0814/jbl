"""정리본 원고 줄이 화면에서 어디서 끊기는지(자동 줄바꿈·목록 나눔) 덤프 — 줄바꿈 검토용(10-04 사용자 '줄바꿈이 이상한 곳 전수').
  .venv/bin/python tools/dump_breaks.py <SID> [강의키]   → work/review_breaks/<SID>.md
화면 규칙 그대로(build4와 같은 함수): '-' = render_item · '=' = key_split(🔑 + 나머지) · 'U:' 150자↑ render_block · 'P:' render_key · 'E:' render_exam.
나뉘는 줄만 적음: 원고 줄(파일:줄) → 화면 조각(한 줄에 하나, 들여쓰기 = 목록 깊이)."""
import os, sys, re, html, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SID = sys.argv[1].upper(); ONLY = sys.argv[2] if len(sys.argv) > 2 else None
D = os.path.join(ROOT, 'tools', SID.lower()); sys.path.insert(0, D); os.chdir(D)
import lecparse
ctx = {'RED': None, 'LECNAME': collections.defaultdict(lambda: '강의'), 'QMAP': {}, 'cited': set()}
def text(h):
    h = re.sub(r'<span class="ksep[^"]*">([^<]*)</span>', r'\n\1 ', h)
    h = re.sub(r'<(li|br)[^>]*>', '\n• ', h)
    h = re.sub(r'<(div|p)[^>]*class="(kl|kr|kh|khead|klead|lead)[^"]*"[^>]*>', '\n', h)
    h = re.sub(r'<[^>]+>', '', h)
    return [x.strip() for x in html.unescape(h).split('\n') if x.strip()]
out = [f'# {SID} 화면 줄바꿈 덤프 (나뉘는 줄만)\n']
n = 0; LONG = []
for f in sorted(os.listdir(D)):
    if not (f.startswith('lec_') and f.endswith('.txt')): continue
    k = f[4:-4]
    if ONLY and k != ONLY: continue
    lines = open(f, encoding='utf-8').read().split('\n')
    out.append(f'\n## {f}\n')
    for i, ln in enumerate(lines, 1):
        t = ln[:2]
        try:
            if ln.startswith('- '): v = ln[2:]; h = lecparse.render_item(v, ctx)
            elif ln.startswith('= '): v = ln[2:]; ks = lecparse.key_split(v); h = (lecparse.render_keybox(ks[0], ctx) + '<br>' + lecparse.render_key_rest(ks[1], ctx)) if ks and ks[1] else (lecparse.render_keybox(ks[0], ctx) if ks else lecparse.render_key(v, ctx))
            elif ln.startswith('U: '): v = ln[3:]; h = lecparse.render_block(v, ctx) if len(v) > 150 else lecparse.inline(v, ctx)
            elif ln.startswith('P: '): v = ln[3:]; h = lecparse.render_key(v, ctx)
            else: continue
        except Exception as e:
            out.append(f'- {f}:{i} ⚠ 렌더 오류 {e}'); continue
        ps = text(h)
        if len(ps) < 2:
            if ps and len(ps[0]) > 170: LONG.append(f'- {f}:{i} ({len(ps[0])}자 한 덩어리) `{ln[:160]}…`')
            continue
        n += 1
        out.append(f'### {f}:{i}\n원고: `{ln}`\n화면:\n' + '\n'.join('    ' + p for p in ps) + '\n')
out.append('\n## 나뉘지 않은 긴 줄(170자↑ 한 덩어리 — 읽기 어려우면 / 로 나눌 자리 검토)\n' + ('\n'.join(LONG) or '없음'))
os.makedirs(os.path.join(ROOT, 'work', 'review_breaks'), exist_ok=True)
p = os.path.join(ROOT, 'work', 'review_breaks', f'{SID}.md'); open(p, 'w', encoding='utf-8').write('\n'.join(out))
print(SID, '나뉘는 줄', n, '→', p)
