import re, html, unicodedata
STARTER = re.compile(r'^\s*(?:\d{1,2}\s?[\).]\s?\S|\d{1,2}-\d\.|\(\s?\d{1,2}\s?\)|[①-⑳㉠-㉭]|[-•·▶▷→※*✓◆■□○●]\s?\S?|[가-하]\.\s|[a-zA-Z][\).]\s|\[답\]|답\s*[:：)]|답\s*$|해설\s*[:：)]|해설\s*$|참고\s*[:：)]|참고\s*$|유사복원|추가복원|복원 원문|\*?\s?비슷한 복원|<[^>]+>|\(T/F\)|장점\s*[:：]?\s*$|단점\s*[:：]?\s*$|cf[\.\)]|ex[\.\)]|Q\d|\[[^\]]+\]\s*$|\[[^\]]+\]\s)')
LABEL = re.compile(r'^\s*(\[답\]|답\s*[:：)]?|해설\s*[:：)]?|참고\s*[:：)]?)(.*)$')
LISTM = re.compile(r'^\s*(?:\d{1,2}\s?[\).]|\(\s?\d{1,2}\s?\)|[①-⑳㉠-㉭]|[-•·▶▷→※*✓◆■□○●]|[가-하]\.|[a-zA-Z][\).])\s?')
NUMM = re.compile(r'^\s*(?:\d{1,2}\s?[\).]|\(\s?\d{1,2}\s?\)|[①-⑳]|[가-하]\.)')   # 번호 단계
BULM = re.compile(r'^\s*[-•·▶▷→※*✓◆■□○●]')                                         # 그 아래 세부 항목
def width(s): return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)
CHOICE = re.compile(r'^\s*(?:\d{1,2}(?:\s?[~-]\s?\d{1,2})?\s?\)|\(\s?\d{1,2}\s?\)|[①-⑳])')   # 보기 번호 줄(n) · n~m) · (n) · 원문자)
def stray(prev, s, W):
    """ux2 F12 문제 보기 줄 중간 끊김: 앞 줄이 보기(번호로 시작)이고 마침표·물음표로 끝나지 않았는데, 이 줄은 보기 번호·라벨로 시작하지 않는 짧은 줄 → 앞 보기에 붙일 줄
    (0.2ml 같은 소수로 시작하는 줄은 번호 줄이 아님). verify.py가 같은 규칙으로 남은 줄을 셈"""
    if not CHOICE.match(prev) or re.search(r'[.?？。:：]\s*$', prev): return False
    if CHOICE.match(s) or LABEL.match(s) or (STARTER.match(s) and not re.match(r'^\s*\d+\.\d', s)): return False
    return len(s) <= 40 and width(s) <= W * 0.6
TROW = re.compile(r'^[A-Za-z][A-Za-z0-9 /+()\-]*$')   # 영문 표 행(한글·문장 부호 없음)
def is_thead(s):
    """ux2 fixB VIS10 영문 표 머리 줄: 대문자로 시작하는 낱말 3개↑·문장 부호 없음(예: 'Fused suture Name Description')"""
    w = s.split()
    return len(w) >= 3 and sum(1 for x in w if x[:1].isupper()) >= 3 and not re.search(r'[.,:;?!]', s)
def reflow(text, choices=False):
    raw = [l.rstrip() for l in text.split('\n')]
    lines = [l for l in raw if l.strip()]
    if not lines: return []
    ws = sorted(width(l) for l in lines)
    W = ws[int(len(ws) * 0.9)] if len(ws) >= 6 else max(ws)
    W = max(W, 30)
    out = []; prev_full = False; prev_raw = ''; tbl = False
    for l in lines:
        s = l.strip()
        single = len(s) == 1 and '가' <= s <= '힣'
        if tbl and (STARTER.match(s) or LABEL.match(s) or not TROW.match(s)): tbl = False
        if tbl and out:   # ux2 fixB VIS10 영문 표 블록: 소문자 한 낱말 줄(skull) = 앞 칸의 끝 · 앞 행이 3낱말 미만이면 아직 한 행 · 그 밖에 대문자로 시작하면 새 행(앞 줄이 넓어도 붙이지 않음)
            if re.fullmatch(r'[a-z]+', s) or len(out[-1].split()) < 3: out[-1] += ' ' + s
            else: out.append(s)
            prev_full = False; prev_raw = l; continue
        if TROW.match(s) and is_thead(s): tbl = True; out.append(s); prev_full = False; prev_raw = l; continue
        nm_ = re.match(r'^(\d{1,2})([.)])\s', s); inl_ = re.findall(r'(?:^|[\s,，:])(\d{1,2})([.)])\s', out[-1]) if out else []
        if out and nm_ and len(inl_) >= 2 and inl_[-1][1] == nm_.group(2) and int(nm_.group(1)) == int(inl_[-1][0]) + 1 and re.search(r'[,，]\s*$', out[-1]):
            out[-1] += ' ' + s                             # 10-05 사용자 '1. 면허종류, 2. 번호, 3. 분량, 4. 용법,' | '5. 용량, 6. 사용기간' — 한 줄 나열(앞 줄에 번호 둘 이상 + 쉼표로 끝남)이 다음 번호에서 끊긴 것 → 이어 붙임
        elif out and not STARTER.match(s) and not LABEL.match(s) and not re.match(r'^\s*(?:<[^>]+>|\[[^\]]+\])\s*$', out[-1]) and not re.search(r'[.?!:：;)\]”"…]\s*$', out[-1]) and (
                re.search(r'(?:[을를에의및]|하고|하며|하여|되어|이며|이고|에서|으로|에게|부터|까지|처럼|보다|에는|에도|으며|지만|는데|[,，]|\b(?:and|or|of|the|to|a|an|in|with|for|by|from|at|on|as|that|which|is|are))\s*$', out[-1]) or (re.match(r'^[a-z(]', s) and not re.match(r'^(?:e\.g|i\.e|cf|ex)\b', s)) or width(out[-1]) >= W * 0.6):
            out[-1] += ' ' + s                             # 10-05 문장 중간 끊김: 앞 줄이 문장부호로 끝나지 않고(조사·접속어·쉼표로 끝나거나 넓은 줄) 다음 줄이 번호·라벨·글머리가 아니면(소문자·여는 괄호로 시작하면 특히) → 이어 붙임
        elif out and out[-1].count('(') > out[-1].count(')') and s.count(')') > s.count('(') and not NUMM.match(s) and not LABEL.match(s) and width(s) <= W:
            out[-1] += ' ' + s                             # 10-05 JB 가독성: 괄호가 열린 채 끊긴 줄('… (necrosis' | '-> degradation products)') → 이어 붙임(글자 그대로)
        elif out and single and len(prev_raw.strip()) == 1 and '가' <= prev_raw.strip() <= '힣':
            out[-1] += s                                   # 세로로 끊긴 표 머리("장"/"점") → 붙임
        elif out and not STARTER.match(s) and (prev_full or prev_raw.rstrip().endswith((',', '，'))) and not prev_raw.rstrip().endswith((':', '：')):
            out[-1] += ' ' + s                             # 단 폭 때문에 끊긴 줄 → 이어 붙임
        elif choices and out and stray(out[-1], s, W):
            out[-1] += ' ' + s                             # ux2 F12 보기 줄 중간 끊김 → 앞 보기에
        else:
            out.append(s)
        prev_full = width(l) >= W * 0.74
        prev_raw = l
    return out
def same_chars(a, b): return re.sub(r'\s+', '', a) == re.sub(r'\s+', '', b)
SRCREF = re.compile(r'\d{4,6}[_\s]|pf[_ ]|_p\.?\s?\d|\bp\.?\s?\d|\d+\s?pg\b|PPT|ppt|강의자료|교과서|슬라이드|핸드아웃|\.pdf')
def render(text, first_bold=False, ans=False, choices=False):
    """논리 줄 단위 HTML. 글자는 원문 그대로, 라벨(답·해설·참고)만 굵게.
    ans=True(JB 답안 칸): 첫 '답' 라벨 줄에 .ans0(크게·흰 칸), 첫 '해설' 라벨부터 끝까지를 .exw로 감싸고
    해설이 6줄 또는 400자를 넘으면 .exw.clamp(허브가 높이를 줄이고 '해설 전체 보기'를 붙임)"""
    L = reflow(text, choices); assert same_chars(text, '\n'.join(L)), 'reflow changed characters'
    h = []; a0 = None; ex_at = None; innum = False; insrc = False   # 번호 단계 아래 '-'·'·' 줄은 .sub(들여쓰기) — 클래스만, 글자 불변(V04)
    for i, s in enumerate(L):
        m = LABEL.match(s); was_src = insrc; insrc = False
        if first_bold and i == 0:
            h.append(f'<div class="ln q1">{html.escape(s)}</div>')
        elif m:
            lab, rest = m.group(1), m.group(2)
            kind = 'a' if '답' in lab else ('e' if '해설' in lab else 'r')
            extra = ''
            if ans and kind == 'a' and a0 is None: a0 = i; extra = ' ans0' if rest.strip() else ' lab0'   # 값 없는 '답:'은 빈 흰 칸 대신 라벨만
            if ans and kind == 'e' and ex_at is None: ex_at = i
            srcl = kind == 'r' and (not rest.strip() or bool(SRCREF.search(rest))); insrc = srcl and not rest.strip()
            if srcl: extra += ' lab-src'   # 10-05 사용자 'jb원문 해설에 달려있는 출처 표시란은 아예 없애줘' — 출처뿐인 '참고:' 줄은 화면에서 숨김(글자는 그대로 · 내용이 있는 참고 줄은 보임)
            h.append(f'<div class="ln lab lab-{kind}{extra}"><b>{html.escape(lab)}</b>{html.escape(rest)}</div>'); innum = False
            continue
        elif was_src and SRCREF.search(s) and len(s) < 160: h.append(f'<div class="ln lab-src">{html.escape(s)}</div>'); insrc = True; continue
        elif LISTM.match(s):
            if NUMM.match(s): cls = ' num'; innum = True
            elif innum and BULM.match(s): cls = ' sub'
            else: cls = ''; innum = False
            h.append(f'<div class="ln li{cls}">{html.escape(s)}</div>')
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
