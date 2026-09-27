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
def render(text, first_bold=False, ans=False):
    """논리 줄 단위 HTML. 글자는 원문 그대로, 라벨(답·해설·참고)만 굵게.
    ans=True(JB 답안 칸): 첫 '답' 라벨 줄에 .ans0(크게·흰 칸), 첫 '해설' 라벨부터 끝까지를 .exw로 감싸고
    해설이 6줄 또는 400자를 넘으면 .exw.clamp(허브가 높이를 줄이고 '해설 전체 보기'를 붙임)"""
    L = reflow(text); assert same_chars(text, '\n'.join(L)), 'reflow changed characters'
    h = []; a0 = None; ex_at = None
    for i, s in enumerate(L):
        m = LABEL.match(s)
        if first_bold and i == 0:
            h.append(f'<div class="ln q1">{html.escape(s)}</div>')
        elif m:
            lab, rest = m.group(1), m.group(2)
            kind = 'a' if '답' in lab else ('e' if '해설' in lab else 'r')
            extra = ''
            if ans and kind == 'a' and a0 is None: a0 = i; extra = ' ans0'
            if ans and kind == 'e' and ex_at is None: ex_at = i
            h.append(f'<div class="ln lab lab-{kind}{extra}"><b>{html.escape(lab)}</b>{html.escape(rest)}</div>')
        elif LISTM.match(s): h.append(f'<div class="ln li">{html.escape(s)}</div>')
        elif re.match(r'^(장점|단점)\s*[:：]?\s*$|^<[^>]+>$|^\[[^\]]+\]\s*$', s): h.append(f'<div class="ln hd">{html.escape(s)}</div>')
        else: h.append(f'<div class="ln{" q1" if (first_bold and i == 0) else ""}">{html.escape(s)}</div>')
    if ans and ex_at is not None and (a0 is None or ex_at > a0):
        long_ = len(L) - ex_at > 6 or sum(len(x) for x in L[ex_at:]) > 400
        h = h[:ex_at] + [f'<div class="exw{" clamp" if long_ else ""}">'] + h[ex_at:] + ['</div>']
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
