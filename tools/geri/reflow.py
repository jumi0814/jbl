import re, html, unicodedata
STARTER = re.compile(r'^\s*(?:\d{1,2}\s?[\).]\s?\S|\d{1,2}-\d\.|\(\s?\d{1,2}\s?\)|[①-⑳㉠-㉭]|[-•·▶▷→※*✓◆■□○●]\s?\S?|[가-하]\.\s|[a-zA-Z][\).]\s|\[답\]|답\s*[:：)]|답\s*$|해설\s*[:：)]|해설\s*$|참고\s*[:：)]|참고\s*$|유사복원|추가복원|복원 원문|\*?\s?비슷한 복원|<[^>]+>|\(T/F\)|장점\s*[:：]?\s*$|단점\s*[:：]?\s*$|cf[\.\)]|ex[\.\)]|Q\d|\[[^\]]+\]\s*$|\[[^\]]+\]\s)')
LABEL = re.compile(r'^\s*(\[답\]|답\s*[:：)]?|해설\s*[:：)]?|참고\s*[:：)]?)(.*)$')
LISTM = re.compile(r'^\s*(?:\d{1,2}\s?[\).]|\(\s?\d{1,2}\s?\)|[①-⑳㉠-㉭]|[-•·▶▷→※*✓◆■□○●]|[가-하]\.|[a-zA-Z][\).])\s?')
def width(s): return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)
def reflow(text):
    raw = [l.rstrip() for l in text.split('\n')]
    lines = [l for l in raw if l.strip()]
    if not lines: return []
    ws = sorted(width(l) for l in lines)
    W = ws[int(len(ws) * 0.9)] if len(ws) >= 6 else max(ws)
    W = max(W, 30)
    out = []; prev_full = False; prev_raw = ''
    for l in lines:
        s = l.strip()
        single = len(s) == 1 and '가' <= s <= '힣'
        if out and single and len(prev_raw.strip()) == 1 and '가' <= prev_raw.strip() <= '힣':
            out[-1] += s                                   # 세로로 끊긴 표 머리("장"/"점") → 붙임
        elif out and not STARTER.match(s) and (prev_full or prev_raw.rstrip().endswith((',', '，'))) and not prev_raw.rstrip().endswith((':', '：')):
            out[-1] += ' ' + s                             # 단 폭 때문에 끊긴 줄 → 이어 붙임
        else:
            out.append(s)
        prev_full = width(l) >= W * 0.74
        prev_raw = l
    return out
def same_chars(a, b): return re.sub(r'\s+', '', a) == re.sub(r'\s+', '', b)
def render(text, first_bold=False):
    """논리 줄 단위 HTML. 글자는 원문 그대로, 라벨(답·해설·참고)만 굵게."""
    L = reflow(text); assert same_chars(text, '\n'.join(L)), 'reflow changed characters'
    h = []
    for i, s in enumerate(L):
        m = LABEL.match(s)
        if first_bold and i == 0:
            h.append(f'<div class="ln q1">{html.escape(s)}</div>')
        elif m:
            lab, rest = m.group(1), m.group(2)
            kind = 'a' if '답' in lab else ('e' if '해설' in lab else 'r')
            h.append(f'<div class="ln lab lab-{kind}"><b>{html.escape(lab)}</b>{html.escape(rest)}</div>')
        elif LISTM.match(s): h.append(f'<div class="ln li">{html.escape(s)}</div>')
        elif re.match(r'^(장점|단점)\s*[:：]?\s*$|^<[^>]+>$|^\[[^\]]+\]\s*$', s): h.append(f'<div class="ln hd">{html.escape(s)}</div>')
        else: h.append(f'<div class="ln{" q1" if (first_bold and i == 0) else ""}">{html.escape(s)}</div>')
    return ''.join(h)
if __name__ == '__main__':
    import json
    b = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jb_blocks.json')))
    bad = 0; n = 0; before = after = 0
    for ed in b:
        for q in b[ed]:
            t = '\n'.join(q['lines']); L = reflow(t); n += 1
            before += len([x for x in t.split('\n') if x.strip()]); after += len(L)
            if not same_chars(t, '\n'.join(L)): bad += 1
    print('blocks', n, 'char-mismatch', bad, '| lines', before, '→', after)
    for q in b['25']:
        if q['num'] in (4, 32, 22):
            print('-----', q['num']); print('\n'.join(reflow('\n'.join(q['lines']))))
