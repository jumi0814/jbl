import re, html, os
import emph
CITE = re.compile(r'(\[\[[A-Z0-9]+:[^\]]+\]\]|\{jb:[^}]+\})')
def inline(s, ctx):
    out = []
    for tok in CITE.split(s):
        if tok.startswith('[['):
            k, p = tok[2:-2].split(':', 1)
            if not S.LECMAP.get(k, (None,))[0]: out.append(f'<button class="cite t" data-k="{k}" data-p="">{ctx["LECNAME"][k]} ‘{html.escape(p)}’</button>')
            else:
                if p.isdigit(): ctx['cited'].add((k, int(p)))
                out.append(f'<button class="cite" data-k="{k}" data-p="{p}">{ctx["LECNAME"][k]} p.{p}</button>')
        elif tok.startswith('{jb:'):
            i = tok[4:-1]; q = ctx['QMAP'].get(i)
            if q: out.append(f'<button class="xjb{" rep" if len(q["yrs"]) >= 2 else ""}" data-go="{i}" title="{html.escape(q["short"])}">기출 {"·".join("%02d" % y for y in q["yrs"])}</button>')
        else:
            t = emph.apply(html.escape(tok, quote=False), phrases=False, numbers=False)
            t = re.sub(r'\*\*(.+?)\*\*', r'<b class="term">\1</b>', t)
            t = re.sub(r'==(.+?)==', r'<span class="hl">\1</span>', t)
            t = re.sub(r'\{k:([^{}]+)\}', r'<span class="hk">\1</span>', t)
            t = t.replace('💡', '<b class="bulb">💡</b>').replace('⚠', '<b class="warn">⚠</b>')
            out.append(t)
    return ''.join(out)
def parse(path):
    lec = None; card = None; grp = ''
    for raw in open(path, encoding='utf-8'):
        line = raw.rstrip('\n')
        if not line.strip(): continue
        if line.startswith('#LEC'):
            p = [x.strip() for x in line[4:].split('|')]
            lec = {'k': p[0], 'title': p[1], 'prof': p[2], 'yr': p[3], 'file': p[4], 'pages': int(p[5]), 'notes': [], 'cards': [], 'map': ''}
        elif line.startswith('@MAP'): lec['map'] = line[4:].strip()
        elif line.startswith('@G'): grp = line[2:].strip()
        elif line.startswith('!'): lec['notes'].append(line[1:].strip())
        elif line.startswith('## '):
            p = [x.strip() for x in line[3:].split('|')]; jb = []; tag = ''
            for x in p[3:]:
                if x.startswith('jb='): jb = [j.strip() for j in x[3:].split(',') if j.strip()]
                else: tag = x
            card = {'en': p[0], 'ko': p[1], 'rng': p[2], 'tag': tag, 'jb': jb, 'gist': '', 'body': [], 'figs': [], 'grp': grp, 'recall': []}
            lec['cards'].append(card)
        elif line.startswith('> '): card['gist'] = line[2:].strip()
        elif line.startswith('= '): card['body'].append(('K', line[2:].strip()))
        elif line.startswith('# '): card['body'].append(('h', line[2:].strip()))
        elif line.startswith('|'):
            row = [c.strip() for c in line.strip().strip('|').split('|')]
            if card['body'] and card['body'][-1][0] == 'T': card['body'][-1][1].append(row)
            else: card['body'].append(('T', [row]))
        elif line.startswith('F:'):
            fl = []
            for part in line[2:].split(','):
                part = part.strip()
                if not part: continue
                pg, _, cap = part.partition('=')
                fk = None
                if ':' in pg: fk, pg = pg.split(':', 1); fk = fk.strip()
                fl.append((int(re.findall(r'\d+', pg)[0]), cap.strip(), fk))
            card['figs'] += [(p_, fk_) for p_, _, fk_ in fl]; card['body'].append(('F', fl))
        elif line.startswith('E:'):
            ids, _, txt = line[2:].partition('|'); card['body'].append(('E', ([i.strip() for i in ids.split(',') if i.strip()], txt.strip())))
        elif line.startswith('M:'): card['recall'].append(line[2:].strip())
        elif line[:2] in ('P:', 'U:'): card['body'].append((line[0], line[2:].strip()))
        elif line.startswith('- '): card['body'].append(('b', line[2:].strip()))
        else: raise ValueError(f'{path}: unknown line: ' + line[:60])
    return lec
import subject as S
ORDER = S.LEC_ORDER
def load_all():
    DIR = os.path.dirname(os.path.abspath(__file__))
    return [parse(f'{DIR}/lec_{k}.txt') for k in ORDER if os.path.exists(f'{DIR}/lec_{k}.txt')]
if __name__ == '__main__':
    for L in load_all():
        print(L['k'], 'cards', len(L['cards']), 'items', sum(1 for c in L['cards'] for b in c['body'] if b[0] == 'b'), 'tables', sum(1 for c in L['cards'] for b in c['body'] if b[0] == 'T'),
              'exam', sum(1 for c in L['cards'] for b in c['body'] if b[0] == 'E'), 'recall', sum(len(c['recall']) for c in L['cards']), 'figs', sum(len(c['figs']) for c in L['cards']))


# ---- v6 가독성: 긴 줄을 의미 단위로 자동 구조화 ----
CIRC = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮'
OPEN, CLOSE = '(（["“', ')）]"”'
def _depth_iter(s):
    d = 0; q = False
    for i, ch in enumerate(s):
        if ch in '"“”': q = not q if ch == '"' else (ch == '“')
        if ch in '(（[': d += 1
        elif ch in ')）]': d = max(0, d - 1)
        yield i, ch, d + (1 if q else 0)
def split_top(s, sep=' / '):
    out, last = [], 0; skip = -1
    for i, ch, d in _depth_iter(s):
        if i < skip: continue
        if d == 0 and s.startswith(sep, i):
            out.append(s[last:i].strip()); last = i + len(sep); skip = last
    out.append(s[last:].strip())
    return [x for x in out if x]
def _marks(s, pat):
    pos = []
    for i, ch, d in _depth_iter(s):
        if d: continue
        m = pat.match(s, i)
        if m and (i == 0 or s[i-1] in ' ·/(—:;,=' ):
            pos.append((i, m.group(1)))
    return pos
PAT_CIRC = re.compile('([' + CIRC + '])')
PAT_NUM = re.compile(r'(\d{1,2})[.)] (?=\S)')
PAT_ABC = re.compile(r'([A-H])\) (?=\S)')
def split_enum(s):
    for pat in (PAT_CIRC, PAT_NUM, PAT_ABC):
        pos = _marks(s, pat)
        if pat is PAT_NUM:  # 1. 2. 3. 순서가 맞는 것만
            seq, want = [], 1
            for p, g in pos:
                if int(g) == want: seq.append((p, g)); want += 1
            pos = seq
        if pat is PAT_ABC:
            seq, want = [], 'A'
            for p, g in pos:
                if g == want: seq.append((p, g)); want = chr(ord(want) + 1)
            pos = seq
        if len(pos) >= 3:
            idx = [p for p, _ in pos]
            raw_lead = s[:idx[0]]
            lead = raw_lead.strip().rstrip(':：—-=').strip()
            if raw_lead.count('==') % 2 == 1: lead = lead.replace('==', '').strip()
            if lead in ('', '=='): lead = ''
            items = [s[a:b].strip().rstrip('·/,;').strip() for a, b in zip(idx, idx[1:] + [len(s)])]
            return lead, _rebalance(items, raw_lead.count('==') % 2 == 1), pat is PAT_CIRC
            items = [s[a:b].strip().rstrip('·/,;').strip() for a, b in zip(idx, idx[1:] + [len(s)])]
            return lead, items, pat is PAT_CIRC
    return None
def split_lead(s):
    m = re.match(r'^([^:：=/]{2,46}?)\s*[:：]\s+(.+)$', s)
    if m and len(m.group(2)) > 60 and not re.search(r'https?$', m.group(1)): return m.group(1), m.group(2)
    return None
def segments(s, min_len=14):
    """길면 나눌 조각 목록, 아니면 None"""
    for sep, mn in ((' / ', min_len), ('; ', 20), (' · ', 22)):
        parts = split_top(s, sep)
        if len(parts) >= 2 and min(len(p) for p in parts) >= mn and (sep == ' / ' or len(s) > 110): return parts
    if len(s) > 190:  # 문장 단위
        parts = [p.strip() for p in re.split(r'(?<=[.다음함됨])\s+(?=[A-Z가-힣\d(①"“])', s) if p.strip()]
        if len(parts) >= 2 and parts[0] and len(parts[0]) < 25 and len(parts) >= 3: parts = [parts[0] + ' ' + parts[1]] + parts[2:]
        if len(parts) >= 2 and min(len(p) for p in parts) >= 25: return parts
        parts = split_top(s, '; ')
        if len(parts) >= 2 and min(len(p) for p in parts) >= 25: return parts
    if s.count('→') >= 5 and len(s) > 170:
        parts = [p.strip() for p in split_top(s, ' → ')]
        if len(parts) >= 5: return ['→'] + parts
    return None
def _rebalance(parts, hl0=False):
    """조각마다 ==…== 과 {r:…} 짝을 맞춤 — 형광이 걸친 조각은 조각 전체를 형광으로"""
    out = []; hl = hl0; rs = 0
    for p in parts:
        if p == '→': out.append(p); continue
        n = p.count('=='); piece_hl = hl or n > 0
        hl = hl ^ (n % 2 == 1)
        q = p.replace('==', '').strip()
        q = ('{r:' * rs) + q
        rs = max(0, q.count('{r:') - q.count('}'))
        q = q + ('}' * rs)
        out.append(('==' + q + '==') if piece_hl and q else q)
    return out
def render_block(v, ctx, depth=0):
    """본문 블록(🔑·⭐·💬·항목 공통): 앞머리 라벨 + 번호 목록/조각 목록"""
    e = split_enum(v)
    if e:
        lead, items, circ = e
        head = f'<div class="klead">{inline(lead, ctx)}</div>' if lead else ''
        return head + '<ol class="circ">' + ''.join(f'<li>{render_block(x, ctx, depth+1) if (depth == 0 and len(x) > 150) else inline(x, ctx)}</li>' for x in items) + '</ol>'
    top = split_top(v)
    if len(top) >= 2 and sum(1 for p in top if re.match(r'^[^:：/]{1,34}[:：]\s', p)) >= 2:
        def lab(p):
            m = re.match(r'^([^:：/]{1,34})[:：]\s+(.*)$', p)
            if not m: return inline(p, ctx)
            lb, rest = m.group(1), m.group(2)
            if lb.count('==') % 2 == 1: lb = lb.replace('==', ''); rest = '==' + rest
            if lb.count('{r:') > lb.count('}'): lb = lb + '}'; rest = '{r:' + rest
            return f'<b class="lbl">{inline(lb, ctx)}</b> ' + inline(rest, ctx)
        return '<ul class="klist lab">' + ''.join(f'<li>{lab(p)}</li>' for p in _rebalance(top)) + '</ul>'
    if len(v) > 90:
        sp = split_lead(v)
        if sp and depth == 0:
            lead, rest = sp; inner = segments(rest)
            if not inner:
                pr = split_top(rest)
                if len(pr) >= 4 and min(len(p) for p in pr) >= 4: inner = pr
            if inner:
                return f'<div class="klead">{inline(lead, ctx)}</div>' + _seg_html(inner, ctx, depth)
    parts = segments(v)
    if parts: return _seg_html(parts, ctx, depth)
    return inline(v, ctx)
def _seg_html(parts, ctx, depth):
    parts = _rebalance(parts)
    if parts[0] == '→':
        return '<ol class="steps">' + ''.join(f'<li>{inline(p, ctx)}</li>' for p in parts[1:]) + '</ol>'
    return '<ul class="klist">' + ''.join(f'<li>{render_block(p, ctx, depth+1) if (depth == 0 and len(p) > 150) else inline(p, ctx)}</li>' for p in parts) + '</ul>'
def render_key(v, ctx): return f'<div class="kb">{render_block(v, ctx)}</div>'
def render_item(v, ctx):
    body = render_block(v, ctx) if len(v) > 110 else inline(v, ctx)
    return f'<div class="li{" nolead" if body.startswith("<ol") or body.startswith("<ul") else ""}">{body}</div>'
def render_recall(x, ctx):
    rows = split_top(x)
    if len(rows) >= 2 and len(x) > 60 and min(len(r) for r in rows) >= 14: return ''.join(f'<li>{inline(r, ctx)}</li>' for r in rows)
    return f'<li>{inline(x, ctx)}</li>'
