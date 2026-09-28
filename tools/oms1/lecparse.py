import re, html, os
import emph
CITE = re.compile(r'(\[\[[A-Z0-9]+:[^\]]+\]\]|\{jb:[^}]+\})')
SRCN = re.compile(r'\((\d{2}\s)?필기\)')
SRCH = re.compile(r'^필기:\s')
SRCP = re.compile(r'^슬라이드\s(\d{1,3})((?:\s흐름|\s표시)?):\s')
def _srcmeta(t, first):
    """ux2 D07 출처 메타를 가볍게 — 글자는 그대로 두고 감싸기만(.srcn = ✍ 아이콘·.srcp = 회색 'p.NN' 칩, 원문 글자는 안쪽 .srt — CSS display:none, textContent·표시·검색 그대로)"""
    t = SRCN.sub(lambda m: f'<span class="srcn" title="{(m.group(1) or "").strip() + " " if m.group(1) else ""}필기"><span class="srt">{m.group(0)}</span></span>', t)
    if first:
        t = SRCH.sub(lambda m: f'<span class="srcn srch" title="필기"><span class="srt">{m.group(0)}</span></span>', t, count=1)
        t = SRCP.sub(lambda m: f'<span class="srcp" data-p="{m.group(1)}" title="슬라이드 {m.group(1)}{m.group(2)}"><span class="srt">{m.group(0)}</span></span>', t, count=1)
    return t
def _rnorm(x): return re.sub(r'\s+', '', html.unescape(re.sub(r'==|\*\*|<[^>]+>', '', x))).lower()
def red_set(texts):
    """ux2 D06 — 카드의 🔑·⭐·⚡ 원고에 든 {r:…} 글자 집합(소문자·공백 제거)"""
    return {_rnorm(m) for t in texts for m in re.findall(r'\{r:([^{}]+)\}', t) if _rnorm(m)}
def _kcls(core):
    """본문 {r:}가 카드 핵심 집합과 서로 포함 관계면 'k'(빨강), 아니면 'k k2'(굵은 검정 — 원칙 7-1 안). 한 글자는 같을 때만"""
    def f(x):
        n = _rnorm(x)
        if not n: return 'k'
        for c in core:
            if n == c or (min(len(n), len(c)) >= 2 and (n in c or c in n)): return 'k'
        return 'k k2'
    return f
def inline(s, ctx):
    out = []; core = ctx.get('RED'); kc = _kcls(core) if core is not None else None
    for ti, tok in enumerate(CITE.split(s)):
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
            t = emph.apply(html.escape(tok, quote=False), phrases=False, numbers=False, kcls=kc)
            t = re.sub(r'\*\*(.+?)\*\*', r'<b class="term">\1</b>', t)
            t = re.sub(r'==(.+?)==', r'<span class="hl">\1</span>', t)
            t = re.sub(r'\{k:([^{}]+)\}', r'<span class="hk">\1</span>', t)
            t = t.replace('💡', '<b class="bulb">💡</b>').replace('⚠', '<b class="warn">⚠</b>')
            if '\ue010' in t or '\ue012' in t:   # ux2 E03 작은 표를 펼친 줄의 열 이름(표시 글자에 안 드는 .noann)·숨긴 칸(.csx)
                t = re.sub('\ue010([^\ue011]*)\ue011', r'<span class="clab noann">\1 </span>', t).replace('\ue012', '<span class="csx">').replace('\ue013', '</span>')
            out.append(_srcmeta(t, ti == 0))
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
        if ch in '(（[{': d += 1                 # {r:…}·{k:…} 안에서도 나누지 않음(예: {r:0.04 · 0.70})
        elif ch in ')）]}': d = max(0, d - 1)
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
            lead = raw_lead.strip().rstrip(':：—-').strip()
            if lead.endswith('=') and not lead.endswith('=='): lead = lead.rstrip('=').strip()   # 끝의 '=' 기호만 떼고 ==형광== 닫힘은 살림
            if lead.count('==') % 2 == 1: lead = lead.replace('==', '').strip()
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
    out = []; hl = hl0; rs = 0; bd = False
    for p in parts:
        if p == '→': out.append(p); continue
        n = p.count('=='); piece_hl = hl or n > 0
        hl = hl ^ (n % 2 == 1)
        nb = p.count('**'); was_bd = bd                          # **굵게**가 조각을 넘으면 조각마다 짝을 맞춤
        bd = bd ^ (nb % 2 == 1)
        q = p.replace('==', '').strip()
        if was_bd and nb % 2 == 1: q = '**' + q                  # 앞 조각에서 열린 굵게를 이 조각에서 닫음
        elif not was_bd and nb % 2 == 1: q = q + '**'           # 이 조각에서 열고 다음 조각으로 넘어감
        elif was_bd and nb == 0: q = '**' + q + '**'            # 조각 전체가 굵게 안
        q = ('{r:' * rs) + q
        rs = max(0, q.count('{r:') - q.count('}'))
        q = q + ('}' * rs)
        if piece_hl and q:                                      # 형광으로 감쌀 때 기출·인용 버튼 표시는 밖으로(짝이 끊기지 않게)
            toks = ' '.join(CITE.findall(q)); core = CITE.sub('', q).strip()
            q = ('==' + core + '==' if core else '') + (' ' + toks if toks else '')
        out.append(q)
    return out
# ---- U23: 짧은 나열은 가로 흐름(ul.kflow) · 여러 조각에 걸친 ==기출 문장==은 형광 블록(hlblock) · 목록만 든 li 없애기
LBL = re.compile(r'^([^:：/]{1,34})[:：]\s+(.*)$')
def _plain(p): return re.sub(r'\{jb:[^}]*\}|\{r:|\{k:|==|\*\*|\}', '', p)
def _is_flow(parts):
    """가로 흐름(ul.kflow): 4조각↑ 중앙값 24자 미만 · ux2 D09 2~3조각은 합 100자 이하이거나 3조각 중앙값 22자 이하"""
    if len(parts) < 2: return False
    ls = sorted(len(_plain(p).strip()) for p in parts)
    if len(parts) >= 4: return ls[len(ls) // 2] < 24
    return sum(ls) <= 100 or (len(parts) == 3 and ls[1] <= 22)
def _hl_flags(parts):
    """조각마다 ==…== 로 통째 감싸였는지 → 연속 3조각↑ 또는 (2조각↑·합 120자 초과)인 구간은 형광 블록: == 를 떼고 flag"""
    full = [p.startswith('==') and p.endswith('==') and p.count('==') == 2 and len(p) > 4 for p in parts]
    flags = [False] * len(parts); i = 0
    while i < len(parts):
        if not full[i]: i += 1; continue
        j = i
        while j < len(parts) and full[j]: j += 1
        if j - i >= 3 or (j - i >= 2 and sum(len(_plain(parts[k])) for k in range(i, j)) > 120):
            for k in range(i, j): flags[k] = True
        i = j
    return [p[2:-2] if f else p for p, f in zip(parts, flags)], flags
def _single_list(h):
    """h가 목록 하나뿐(앞머리 없음)이면 (태그, 클래스, 안쪽 li들) — 아니면 None"""
    m = re.fullmatch(r'<(ul|ol) class="([^"]*)">(.*)</\1>', h, flags=re.S)
    if not m or len(re.findall(r'<(?:ul|ol)\b', h)) != 1: return None
    return m.group(1), m.group(2), m.group(3)
def _list_html(parts, ctx, depth, tag='ul', cls='klist', fmt=None):
    """조각 목록 → 목록 HTML. fmt(p) = li 안 HTML(기본: 길면 한 단계 더 구조화). 안쪽이 목록 하나뿐인 조각은 li에 목록만 들지 않게:
       klist·circ면 바깥 목록에 항목으로 풀어 넣고, steps·kflow면 바깥 목록을 잠시 닫고 그 블록을 둠"""
    parts, flags = _hl_flags(parts)
    if cls == 'klist' and _is_flow(parts): cls = 'kflow'
    if cls == 'circ' and len(parts) >= 2:   # ux2 D09 짧은 번호 나열(중앙값 22자 이하)은 2~4단 격자(번호 그대로)
        ls = sorted(len(_plain(p).strip()) for p in parts)
        if ls[len(ls) // 2] <= 22: cls = 'circ cgrid'
        elif ls[len(ls) // 2] <= 34 and len(parts) >= 4 and ls[-1] <= 60: cls = 'circ cgrid cgw'   # 조금 긴 짧은 나열(중앙값 34자 이하)은 넓은 칸 격자
    segs = []   # ('li', html, flag) | ('blk', html)
    for p, f in zip(parts, flags):
        if fmt: segs.append(('li', fmt(p), f)); continue
        if depth == 0 and len(p) > 150:
            inner = render_block(p, ctx, depth + 1); sl = _single_list(inner)
            if sl:
                t_, c_, body = sl
                if c_.split()[0] in ('klist', 'circ') and 'kflow' not in c_:
                    for li in re.findall(r'<li(?: class="[^"]*")?>(.*?)</li>', body, flags=re.S): segs.append(('li', li, f))
                else: segs.append(('blk', inner))
                continue
            segs.append(('li', inner, f)); continue
        segs.append(('li', inline(p, ctx), f))
    out, run = [], []
    def flush():
        if not run: return
        allf = all(f for _, f in run)
        c2 = cls + (' hlblock' if allf else (' hlsome' if any(f for _, f in run) else ''))
        lis = []
        for k, (h, f) in enumerate(run):
            lc = '' if (allf or not f) else (' class="hlb hlb0"' if (k == 0 or not run[k - 1][1]) else ' class="hlb"')
            lis.append(f'<li{lc}>{h}</li>')
        out.append(f'<{tag} class="{c2}">' + ''.join(lis) + f'</{tag}>'); run.clear()
    for sg in segs:
        if sg[0] == 'blk': flush(); out.append(sg[1])
        else: run.append((sg[1], sg[2]))
    flush()
    return ''.join(out)
def _lab_merge(top):
    """라벨 목록: 라벨 없는 조각은 앞 라벨 항목에 ' / '로 합침"""
    out = []
    for p in top:
        if out and not LBL.match(p) and LBL.match(out[-1]): out[-1] = out[-1] + ' / ' + p
        else: out.append(p)
    return out
def render_block(v, ctx, depth=0):
    """본문 블록(🔑·⭐·💬·항목 공통): 앞머리 라벨 + 번호 목록/조각 목록"""
    e = split_enum(v)
    if e:
        lead, items, circ = e
        head = f'<div class="klead">{inline(lead, ctx)}</div>' if lead else ''
        return head + _list_html(items, ctx, depth, 'ol', 'circ')
    top = split_top(v)
    if len(top) >= 2 and sum(1 for p in top if LBL.match(p)) >= 2:
        def lab(p):
            m = LBL.match(p)
            if not m: return inline(p, ctx)
            lb, rest = m.group(1), m.group(2)
            if lb.count('==') % 2 == 1: lb = lb.replace('==', ''); rest = '==' + rest
            if lb.count('{r:') > lb.count('}'): lb = lb + '}'; rest = '{r:' + rest
            if lb.count('**') % 2 == 1: lb = lb.replace('**', ''); rest = '**' + rest
            return f'<b class="lbl">{inline(lb, ctx)}</b> ' + inline(rest, ctx)
        parts = _lab_merge(_rebalance(top))
        return _list_html(parts, ctx, depth, 'ul', 'kflow lab' if _is_flow(parts) else 'klist lab', fmt=lab)
    if len(v) > 90:
        sp = split_lead(v)
        if sp and depth <= 1:
            lead, rest = sp; inner = segments(rest)
            if not inner:
                pr = split_top(rest)
                if len(pr) >= 4 and min(len(p) for p in pr) >= 4: inner = pr
            if inner:
                return f'<div class="klead">{inline(lead, ctx)}</div>' + _seg_html(inner, ctx, depth, rest)
    parts = segments(v)
    if parts: return _seg_html(parts, ctx, depth, v)
    return inline(v, ctx)
def _seg_html(parts, ctx, depth, raw=None):
    parts = _rebalance(parts)
    if parts[0] == '→':
        ls = sorted(len(_plain(p).strip()) for p in parts[1:])   # ux2 D09 짧은 단계(중앙값 22자 이하)는 한 줄 흐름(→)
        return _list_html(parts[1:], ctx, depth, 'ol', 'steps sflow' if ls and ls[len(ls) // 2] <= 22 else 'steps', fmt=lambda p: inline(p, ctx))   # 단계도 기출 문장(==) 3개↑ 연속이면 한 묶음(hlb) — U23
    if depth >= 1 and raw is not None and _is_flow(parts): return inline(raw, ctx)   # 안쪽 짧은 나열은 원문 줄 그대로(li 안에 목록만 들지 않게)
    return _list_html(parts, ctx, depth)
def key_split(v):
    """🔑 핵심이 길면(최상위 항목 4개 초과 또는 180자 초과) 첫 조각만 상자에 두고 나머지는 상자 밖 본문으로 — (상자 원문, [나머지 원문…]) | None"""
    e = split_enum(v); pieces = None
    if e:
        lead, items, _c = e
        if len(items) >= 2: pieces = [((lead + ' ') if lead else '') + items[0]] + items[1:]
    else:
        top = split_top(v)
        if len(top) >= 2 and sum(1 for p in top if LBL.match(p)) >= 2: pieces = _lab_merge(_rebalance(top))
        elif len(v) > 90 and split_lead(v):
            lead, rest = split_lead(v); inner = segments(rest)
            if not inner:
                pr = split_top(rest)
                if len(pr) >= 4 and min(len(p) for p in pr) >= 4: inner = pr
            if inner and inner[0] != '→':
                inner = _rebalance(inner); pieces = [lead + ': ' + inner[0]] + inner[1:]
        if pieces is None:
            ps = segments(v)
            if ps and ps[0] != '→': pieces = _rebalance(ps)
    if not pieces or len(pieces) < 2: return None
    if not (len(pieces) > 4 or len(v) > 180): return None
    return pieces[0], pieces[1:]
def render_key_rest(pieces, ctx):
    """상자 밖으로 내린 🔑 조각: '라벨: 내용'은 소제목(h4.sh) + 항목, 나머지는 항목 — ux2 D01 div.krest로 감쌈(압축 보기에서도 보임)"""
    return '<div class="krest">' + _key_rest(pieces, ctx) + '</div>'
def _key_rest(pieces, ctx):
    out = []
    for p in pieces:
        m = LBL.match(p)
        if m and not re.search(r'[(\[“"]', m.group(1)) and m.group(1).count('==') % 2 == 0 and m.group(1).count('{r:') == m.group(1).count('}'):
            out.append(f'<h4 class="sh">{inline(m.group(1), ctx)}</h4>' + render_item(m.group(2), ctx))
        else: out.append(render_item(p, ctx))
    return ''.join(out)
def render_key(v, ctx): return f'<div class="kb">{render_block(v, ctx)}</div>'
def _ncirc(v):
    e = split_enum(v)
    return len(e[1]) if (e and e[2]) else 0
def render_item(v, ctx, cont=None):
    """항목 한 줄 — 110자 초과 또는 ux2 D09 원문자 번호 3개↑(길이 무관)면 구조화. cont = 앞 줄 번호에 이어지는 시작 번호(⑤ 다음 ⑥ → 6)"""
    if cont:
        pos = _marks(v, PAT_CIRC)
        if pos and pos[0][0] == 0:
            idx = [p for p, _ in pos]
            items = _rebalance([v[a:b].strip().rstrip('·/,;').strip() for a, b in zip(idx, idx[1:] + [len(v)])])
            body = _list_html(items, ctx, 0, 'ol', 'circ').replace('<ol class="circ', f'<ol start="{cont}" class="circ', 1)
            return f'<div class="li nolead cont">{body}</div>'
    body = render_block(v, ctx) if (len(v) > 110 or _ncirc(v) >= 3) else inline(v, ctx)
    return f'<div class="li{" nolead" if body.startswith("<ol") or body.startswith("<ul") else ""}">{body}</div>'
def render_recall(x, ctx):
    rows = split_top(x)
    if len(rows) >= 2 and len(x) > 60 and min(len(r) for r in rows) >= 14: return ''.join(f'<li>{inline(r, ctx)}</li>' for r in rows)
    return f'<li>{inline(x, ctx)}</li>'
# ---- ux2 D04 ⭐ 시험포인트 구조화: '<연도>년 <n회>(…) <형식> "<문제>" → <답> — <근거> ⚠ 함정: …' 한 줄을 나눔(글자는 그대로 — 감싸기만)
EXAM_RE = re.compile(r'^(?P<yr>[\d·]+년(?:\s*이전)?(?:\s*\d+회)?)(?P<mid>[^"“”→]{0,40}?)(?P<q>["“][^"“”]+?["”](?:의 \'[^\']+\')?)(?P<qx>(?:\s*\([^()]*\)|\s[^"“”→()]{1,14})?)(?P<arr>\s*→\s*)(?P<rest>.+)$')
EXAM_FMT = re.compile(r'(?:서술형?|빈칸|객관식|단답형?|T/F|그림)(?:\s?(?:단답|빈칸|서술))?')
EXAM_SRC = re.compile(r'자료|p\.|JB 해설|JB 답|슬라이드|필기|원문|강의록')
def _mk_ok(x):
    """조각 안에서 원고 표기 짝이 맞는지(==·**·{r:…}·{k:…}) — 안 맞으면 구조화하지 않음"""
    if x.count('==') % 2 or x.count('**') % 2: return False
    y = re.sub(r'\{(?:r|k|jb):[^{}]*\}', '', x)
    return '{r:' not in y and '{k:' not in y and '{jb:' not in y
def _d0pos(s, pat, start=0):
    """깊이 0(괄호·따옴표·{…} 밖)에서 pat(문자열)이 시작하는 첫 자리 ≥ start"""
    for i, ch, d in _depth_iter(s):
        if i >= start and d == 0 and s.startswith(pat, i): return i
    return -1
def exam_parts(v):
    """E: 줄 → dict(yr, mid, q, arr, a, tail=[(kind, 글자)…]) | None. kind = 'src'(근거·대조 — 접음) · 'more'(— 뒤 설명) · 'trap'(⚠ 함정)"""
    m = EXAM_RE.match(v)
    if not m: return None
    rest = m.group('rest'); cuts = [x for x in (_d0pos(rest, ' — '), _d0pos(rest, ' ⚠'), _d0pos(rest, '⚠')) if x > 0]
    cut = min(cuts) if cuts else len(rest); a = rest[:cut]; tail = []; i = cut
    while i < len(rest):
        seg = rest[i:]
        if seg.lstrip().startswith('⚠'):
            j = _d0pos(rest, ' — ', i + 1); j = len(rest) if j < 0 else j; kind = 'trap'
        else:
            js = [x for x in (_d0pos(rest, ' ⚠', i + 3), _d0pos(rest, '⚠', i + 3)) if x > 0]; j = min(js) if js else len(rest)
            kind = 'src' if EXAM_SRC.search(rest[i:j]) else 'more'
        tail.append((kind, rest[i:j])); i = j
    d = {'yr': m.group('yr'), 'mid': m.group('mid'), 'q': m.group('q'), 'qx': m.group('qx') or '', 'arr': m.group('arr'), 'a': a, 'tail': tail}
    if not all(_mk_ok(x) for x in [d['mid'], d['q'], d['qx'], d['a']] + [t for _, t in tail]) or not a.strip(): return None
    return d
def exam_q(v):
    """E: 줄의 문제 요지(따옴표 안 글자, 원고 표기 뗌) | None"""
    d = exam_parts(v)
    if not d: 
        m = re.search(r'["“]([^"”]{4,}?)["”]', v)
        return _plain(m.group(1)).strip() if m else None
    return _plain(re.sub(r'^["“]|["”](?:의 \'[^\']+\')?$', '', d['q'])).strip()
EXAM_N = [0, 0]   # 구조화 적용 수 / 전체 ⭐ 줄 수(빌드 로그)
def render_exam(v, ctx):
    """⭐ 한 줄 → 구조화 HTML(연도 머리 .ex-yr는 CSS로 숨김 · 형식 칩 .exf · 문제 .ex-q · → 답 .ex-a · ⚠ 함정 .ex-trap 다음 줄 · 근거 .ex-src 접힘(머리 줄 끝 '근거 ▸')) | None(옛 줄 — 지금 렌더)"""
    EXAM_N[1] += 1
    d = exam_parts(v)
    if not d: return None
    EXAM_N[0] += 1
    mid = ('<span class="exmid">' + inline(d['mid'], ctx) + '</span>') if d['mid'].strip() else html.escape(d['mid'], quote=False)
    mid = EXAM_FMT.sub(lambda m: f'<span class="exf">{m.group(0)}</span>', mid, count=1)
    mid = re.sub(r'\([^)]*\)', lambda m: f'<span class="exp">{m.group(0)}</span>', mid)
    a = d["a"]; ah = render_block(a, ctx) if len(a) > 170 else inline(a, ctx)   # 답이 아주 길 때만 목록으로(줄 수 늘지 않게)
    blk = ah.startswith('<') and re.match(r'<(?:div|ul|ol)\b', ah)
    head = f'<div class="exh"><span class="ex-yr">{html.escape(d["yr"], quote=False)}</span>{mid}<span class="ex-q">{inline(d["q"], ctx)}</span>{('<span class="exp">' + inline(d["qx"], ctx) + '</span>') if d["qx"] else ''}<span class="ex-arr">{html.escape(d["arr"], quote=False)}</span>' + ('' if blk else f'<span class="ex-a">{ah}</span>')
    more = ''.join(f'<span class="ex-more">{inline(t, ctx)}</span>' for k, t in d['tail'] if k == 'more' and not blk)
    srcb = '<button class="exsrcb noann" data-exsrc="1" aria-label="근거 보기"></button>' if any(k == 'src' for k, _ in d['tail']) else ''
    out = [head + more + srcb + '</div>']
    if blk: out.append(f'<div class="ex-a ex-ab">{ah}</div>' + ''.join(f'<div class="ex-more">{inline(t, ctx)}</div>' for k, t in d['tail'] if k == 'more'))
    for k, t in d['tail']:
        if k == 'trap': out.append(f'<div class="ex-trap">{inline(t.strip(), ctx)}</div>')
        elif k == 'src': out.append(f'<div class="ex-src">{inline(t.strip(), ctx)}</div>')   # 기본 접힘 — 머리 줄 끝 '근거 ▸'(.exsrcb)로 펼침
    return '<div class="exs">' + ''.join(out) + '</div>'
