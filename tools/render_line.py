"""원고 한 줄이 화면에서 어떤 구조(머리·목록·하위 목록)로 보이는지 — 빌드 없이(10-08 구조 정돈 담당용).
  .venv/bin/python tools/render_line.py <SID> <M|-|=|K> "<원고 줄(머리 기호 뺀 내용)>"
  .venv/bin/python tools/render_line.py <SID> <M|-|=|K> --file tools/<sid>/lec_<키>.txt --line <줄 번호>
→ 들여쓰기 outline(• 바깥 줄 · ◦ 하위 · ① 번호)과 HTML 한 줄"""
import os, sys, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
a = sys.argv[1:]; S, kind = a[0].lower(), a[1]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), S)); import lecparse as LP
if '--file' in a:
    f = a[a.index('--file') + 1]; n = int(a[a.index('--line') + 1]); v = open(f, encoding='utf-8').read().split('\n')[n - 1]
    v = re.sub(r'^(?:[A-Z]:|=|-)\s?', '', v)
else: v = a[2]
class Q(dict):
    def __missing__(self, k): return {}
ctx = {'RED': set(), 'LECNAME': Q(), 'QMAP': Q(), 'cited': set()}
h = {'M': lambda: '<ul>' + LP.render_recall(v, ctx) + '</ul>', '-': lambda: LP.render_item(v, ctx), '=': lambda: LP.render_keybox(v, ctx), 'K': lambda: LP.render_block(v, ctx)}[kind]()
def outline(h):
    out, d = [], 0
    for m in re.finditer(r'<(/?)(\w+)\b([^>]*)>|([^<]+)', h):
        if m.group(4):
            t = html.unescape(m.group(4))
            if t.strip(): out[-1:] = [(out[-1] if out else '') + t] if out and not out[-1].endswith('\n') else out[-1:] + [t]
            continue
        tag, close, attr = m.group(2), m.group(1), m.group(3)
        if tag not in ('ul', 'ol', 'li', 'div'): continue
        if tag in ('ul', 'ol'): d += -1 if close else 1
        elif not close and (tag == 'li' or 'klead' in attr or 'class="kl' in attr):
            if out and not out[-1].endswith('\n'): out[-1] += '\n'
            out.append('  ' * max(0, d - 1) + ('◦ ' if d >= 2 else '• '))
    return ''.join(out)
print(outline(h)); print('HTML:', h[:600])
