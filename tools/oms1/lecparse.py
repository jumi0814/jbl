import re, html, os
import emph
CITE = re.compile(r'(\[\[[A-Z0-9]+:[^\]]+\]\]|\{jb:[^}]+\})')
SRCN = re.compile(r'\((\d{2}\s)?필기\)')
SRCH = re.compile(r'^필기:\s')
SRCP = re.compile(r'^슬라이드\s(\d{1,3})((?:\s흐름|\s표시)?):\s')
_WBR_SPLIT = re.compile(r'(<[^>]*>)'); _WBR_DOT = re.compile(r'(&#?[A-Za-z0-9]+;|[^\s·<>&])·(?![\s·])'); _WBR_SDOT = re.compile(r' ·(?= )'); _WBR_D0 = re.compile(r'^·(?![\s·])')
_WBR_PAR = re.compile(r'(?<=[A-Za-z0-9])\((?=[A-Za-z])'); _WBR_ARR = re.compile(r'(?<=[A-Za-z])→(?=[A-Za-z])'); _WBR_LONG = re.compile(r'(?<![A-Za-z0-9&#_\-])([A-Za-z]{13,})(?![A-Za-z0-9;_\-]|<span class="nwd">[A-Za-z])'); _WBR_SL = re.compile(r'(?<=[A-Za-z][A-Za-z0-9])/(?=[A-Za-z][A-Za-z0-9])')
def _wbr(t):
    """ux2 fixB VIS04 — 띄어 쓰지 않은 'A·B·C' 가운뎃점 뒤에 줄바꿈 자리(<wbr>)를 넣어 좁은 칸에서 영어 낱말이 글자 중간(Lambdo|id)에서 끊기지 않게. 글자(textContent)·표시 위치 불변 — 태그 밖 글자에만
    ux3 fix V07 — 가운뎃점이 줄 머리로 가지 않게('전방 / ·일차구개'): 앞 글자와 '·'를 끊지 않는 조각(.nwd)으로 묶음 · ' · '는 ' ·'를 묶어 줄은 '· ' 뒤에서만 바뀜"""
    if '·' not in t and '(' not in t and '→' not in t and '/' not in t and not _WBR_LONG.search(t): return t
    P = _WBR_SPLIT.split(t)
    def one(i, p):
        if p.startswith('<'): return p
        if '·' in p: p = _WBR_D0.sub('·<wbr>', _WBR_SDOT.sub('<span class="nwd"> ·</span>', _WBR_DOT.sub(r'<span class="nwd">\1·</span><wbr>', p)))   # 태그 바로 뒤 '·'(앞 글자가 태그 안)는 옛 규칙대로 뒤에 <wbr>만
        # ux3 fix2 F4 — 붙여 쓴 영문 조각 'parachlorophenol(Endotine)'·'incisal→middle→cervical'·'A/B'가 좁은 칸에서 글자 중간(hypochl|orite)에서 끊기지 않게 '(' 앞·'→'/'/' 뒤에 줄바꿈 자리
        p = _WBR_PAR.sub('<wbr>(', p); p = _WBR_ARR.sub('→<wbr>', p); p = _WBR_SL.sub('/<wbr>', p)
        if i and p.startswith('(') and len(p) > 1 and p[1].isascii() and p[1].isalpha() and P[i - 1].startswith('</'): p = '<wbr>' + p   # '<b>H2O2</b>(oxygenating)'
        p = _WBR_LONG.sub(r'<span class="lw" lang="en">\1</span>', p)   # ux3 fix2 F4 13자↑ 영문 낱말 — 칸보다 길 때만(shell lwFit → .hy) 하이픈 줄바꿈 mechano-|transduction
        return p
    return ''.join(one(i, p) for i, p in enumerate(P))
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
def inline(s, ctx, first=True):
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
            if q: out.append(f'<button class="xjb{" rep" if len(q["yrs"]) >= 2 else ""}" data-go="{i}" title="{html.escape(q["short"])}">기출 {"·".join("%02d" % y for y in q["yrs"]) or "연도 미상"}</button>')
        else:
            t = emph.apply(html.escape(tok, quote=False), phrases=False, numbers=False, kcls=kc)
            t = re.sub(r'\*\*(.+?)\*\*', r'<b class="term">\1</b>', t)
            t = re.sub(r'==(.+?)==', r'<span class="hl">\1</span>', t)
            t = re.sub(r'\{k:([^{}]+)\}', r'<span class="hk">\1</span>', t)
            t = t.replace('💡', '<b class="bulb">💡</b>').replace('⚠', '<b class="warn">⚠</b>')
            if '\ue010' in t or '\ue012' in t:   # ux2 E03 작은 표를 펼친 줄의 열 이름(표시 글자에 안 드는 .noann)·숨긴 칸(.csx)
                t = re.sub('\ue010([^\ue011]*)\ue011', r'<span class="clab noann">\1 </span>', t).replace('\ue012', '<span class="csx">').replace('\ue013', '</span>')
            out.append(_wbr(_srcmeta(t, first and ti == 0)))
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
        if pat is PAT_CIRC:  # ux2 F10 원문자가 이어진 것(①②③)·바로 앞이 조/항/호/숫자인 것(12조 ②)은 나누는 자리가 아님
            pos = [(p, g) for p, g in pos if not (s[p + 1:p + 2] and s[p + 1] in CIRC) and not (p and s[p - 1] in CIRC) and not re.search(r'[조항호\d]\s*$', s[:p])]
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
            if pat is PAT_CIRC and any(len(x) <= 3 and all(c in CIRC or c in ' .,·/;' for c in x) for x in items): continue   # ux2 F10 원문자만 남는 조각이 생기면 나누지 않음
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
_IP = [None]   # ux3 트랙3 N1 — key_lines가 도는 동안만 조각 렌더를 바꾸는 갈고리(평소에는 inline 그대로)
def _ip(p, ctx, li=False): return _IP[0](p, ctx, li) if _IP[0] else inline(p, ctx)
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
def _gridc(cls, n):
    """ux2 fixB VIS06 격자 단 수 고정 — --c(넓은 화면)·--cn(아이패드 세로 ≤860): n이 단 수 이하면 n단, 아니면 나누어떨어지는 가장 큰 단, 없으면 마지막 줄이 가장 많이 차는 단(하나만 남는 줄을 피함). 넓은 칸(cgw)은 3단(세로 2단)·40자↑(cg2)는 2단까지. 칸이 좁으면 CSS가 단 수만 줄임"""
    if 'cgrid' not in cls: return ''
    def best(mx):
        if n <= mx: return n
        for c in range(mx, 1, -1):
            if n % c == 0: return c
        return max(range(mx, 1, -1), key=lambda c: ((n % c) / c, c))
    mx = 2 if 'cg2' in cls else (3 if 'cgw' in cls else 4)
    return f' style="--c:{best(mx)};--cn:{best(min(mx, 3))}"'
def _list_html(parts, ctx, depth, tag='ul', cls='klist', fmt=None):
    """조각 목록 → 목록 HTML. fmt(p) = li 안 HTML(기본: 길면 한 단계 더 구조화). 안쪽이 목록 하나뿐인 조각은 li에 목록만 들지 않게:
       klist·circ면 바깥 목록에 항목으로 풀어 넣고, steps·kflow면 바깥 목록을 잠시 닫고 그 블록을 둠"""
    parts, flags = _hl_flags(parts)
    if cls == 'klist' and _is_flow(parts): cls = 'kflow'
    if cls == 'circ' and len(parts) >= 2:   # ux2 D09 짧은 번호 나열(중앙값 22자 이하)은 격자(번호 그대로) — fixB VIS06: 칸 폭은 가장 긴 항목 기준(24자↑ 넓은 칸 · 40자↑ 2단까지) · → 흐름은 가로 한 줄 흐름
        ls = sorted(len(_plain(p).strip()) for p in parts); med = ls[len(ls) // 2]
        if med <= 22 and sum('→' in _plain(p) for p in parts) >= max(1, len(parts) - 1): cls = 'circ cflow'
        elif med <= 22: cls = 'circ cgrid' if ls[-1] <= 24 else ('circ cgrid cgw' if ls[-1] <= 40 else 'circ cgrid cgw cg2')
        elif med <= 34 and len(parts) >= 4 and ls[-1] <= 60: cls = 'circ cgrid cgw' + (' cg2' if ls[-1] > 40 else '')
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
        segs.append(('li', _ip(p, ctx, True) if (cls.split()[0] in ('klist', 'circ') and not any(x in cls for x in ('kflow', 'cgrid', 'cflow'))) else inline(p, ctx), f))
    out, run = [], []
    def flush():
        if not run: return
        allf = all(f for _, f in run)
        c2 = cls + (' hlblock' if allf else (' hlsome' if any(f for _, f in run) else ''))
        lis = []
        for k, (h, f) in enumerate(run):
            lc = '' if (allf or not f) else (' class="hlb hlb0"' if (k == 0 or not run[k - 1][1]) else ' class="hlb"')
            lis.append(f'<li{lc}>{h}</li>')
        out.append(f'<{tag} class="{c2}"{_gridc(c2, len(run))}>' + ''.join(lis) + f'</{tag}>'); run.clear()
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
            return f'<b class="lbl">{inline(lb, ctx)}</b> ' + _ip(rest, ctx)
        parts = _lab_merge(_rebalance(top))
        ls_ = sorted(_L(x) for x in parts)
        fl = _is_flow(parts) and not (_IP[0] and ls_[len(ls_) // 2] > 22)   # ux3 N1 🔑 상자·칸에서는 라벨 사실마다 줄(K2) — 짧은 나열(중앙값 22자 이하, ux2 D09)은 가로 흐름 그대로
        return _list_html(parts, ctx, depth, 'ul', 'kflow lab' if fl else 'klist lab', fmt=lab)
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
    return _ip(v, ctx)
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
# ---- ux3 트랙3 N1·N2 🔑 핵심 상자·정리표 🔑 칸·한 줄 요지 줄 나누기 (key_lines) ----
# 원고 글자는 그대로 — 새로 나누는 자리의 구분자(' · ',' / ',' — ',' → ',' + ')는 <span class="ksep">로 DOM에 남김(줄이 바뀌는 곳에서만 CSS로 숨김 .kh).
# 그래서 표시 단위(aid) textContent가 옛 렌더(render_block)와 글자까지 같다 — 다르면 옛 렌더를 그대로 씀(KL[2] 되돌림 수).
# 규칙: K1 최상위 ' / '(50자 초과 · 12자 이하 수치 나열 제외) → 줄 / K5 최상위 ' — ' 뒤 16자↑ → 둘째 줄 .ksub / K2 ' · ' 사실 중 'X = …'·'X: …'
# (라벨 26자 이하·괄호 없음) 2개↑ → 라벨 사실마다 줄(b.lbl) / 'X: 긴 내용' → 머리 줄(.klh) + 나머지 / K4 ' → ' 4단계↑·70자 초과 → 단계 흐름(.ksi)
# / K6 90자 초과 · ' + ' 조각 모두 12자↑ · 괄호 부연 → '+ ' 앞에서 줄 / K3 56자 초과 · ' · ' 사실 3개↑ → 사실 단위 흐름(.kfi, 24자 이하는 nowrap)
# · 8자 미만 짧은 줄은 앞 줄에 붙임 · 한 상자 7줄까지(넘으면 그 단계는 나누지 않음 — 넘치는 🔑은 key_split이 이미 .krest로 내림)
KFN = 24   # 이 글자 수 이하 사실·단계는 중간에서 끊지 않음(nowrap 덩어리) — 계획 32자에서 정리표 🔑 칸(약 240px) 폭에 맞춰 24자로
KL = [0, 0, 0]   # 상자 수 · 새 구조 · 글자가 달라 옛 렌더로 되돌린 수(빌드 로그·check_lec)
def _ks(sep, cls='kh'): return f'<span class="ksep {cls}">{html.escape(sep, quote=False)}</span>'
def _sp(s, sep):
    """최상위(괄호·{…}·따옴표 밖) sep 자리로 나눔 — 조각을 sep로 다시 이으면 s와 글자까지 같음"""
    out, last, skip = [], 0, -1
    for i, ch, d in _depth_iter(s):
        if i < skip: continue
        if d == 0 and s.startswith(sep, i): out.append(s[last:i]); last = i + len(sep); skip = last
    out.append(s[last:]); return out
def _bal(parts):
    """조각마다 ==…==·**…** 짝을 맞춤(경계에서 닫고 다음 조각에서 다시 엶 — 글자는 그대로, 표시만)"""
    out, hl, bd = [], False, False
    for p in parts:
        q = ('**' if bd else '') + ('==' if hl else '') + p
        hl ^= p.count('==') % 2 == 1; bd ^= p.count('**') % 2 == 1
        q = q + ('==' if hl else '') + ('**' if bd else '')
        out.append(q.replace('====', ''))
    return out
def _L(p): return len(_plain(CITE.sub('', p)).strip())
LBLK = re.compile(r'^(\s*)([^=:：()（）{}\[\]*"“”/·]{1,26}?)(\s=\s|[:：]\s)(\S.*)$', re.S)
def _lab(p):
    m = LBLK.match(p)
    if not m or '==' in m.group(2) or not m.group(2).strip(): return None
    return m
def _labh(p, ctx, first):
    m = _lab(p)
    if not m: return inline(p, ctx, first)
    return inline(m.group(1), ctx, first) + '<b class="lbl">' + inline(m.group(2), ctx, False) + '</b>' + inline(m.group(3) + m.group(4), ctx, False)
def _numlist(parts): return all(_L(x) <= 12 for x in parts) and sum(bool(re.search(r'\d', _plain(x))) for x in parts) >= len(parts) - 1
def _lines(items):
    """[(html, 길이)…] → 8자 미만은 앞 줄에 붙인 줄 목록(html만) · items의 html은 앞 구분자(숨김 .kh)를 이미 품고 있음 — 붙일 때는 구분자를 보이게"""
    out = []
    for h, n in items:
        if out and n < 8: out[-1] = [out[-1][0] + h.replace('class="ksep kh"', 'class="ksep kj"', 1), out[-1][1] + n]
        else: out.append([h, n])
    return [h for h, _ in out]
def _div(lines, cls='kl'): return ''.join(f'<div class="{cls}">{h}</div>' for h in lines)
def _kp(p, ctx, first=True, lvl=0, li=False):
    """한 조각(옛 렌더라면 inline 한 덩어리) → 줄 나눈 HTML. 줄이 없으면 inline 그대로 · li = 옛 렌더의 목록 한 줄(라벨 'X = …'은 굵게)"""
    n = _L(p)
    m = _lab(p) if li else None
    if m and _L(m.group(4)) >= 2:
        return inline(m.group(1), ctx, first) + '<b class="lbl">' + inline(m.group(2), ctx, False) + '</b>' + inline(m.group(3), ctx, False) + _kp(m.group(4), ctx, False, 1)
    if n <= 40: return inline(p, ctx, first)
    # K1 ' / '
    if lvl == 0 and n > 50:
        ps = _sp(p, ' / ')
        if len(ps) >= 2 and not _numlist(ps) and all(x.strip() for x in ps):
            ps = _bal(ps); its = [((_ks(' / ') if i else '') + _kp(x, ctx, first and not i, 1), _L(x)) for i, x in enumerate(ps)]
            ls = _lines(its)
            if 2 <= len(ls) <= 7: return _div(ls)
    # K5 ' — ' 뒤 16자↑ → 둘째 줄
    ps = _sp(p, ' — ')
    if len(ps) >= 2 and all(x.strip() for x in ps[:2]):
        head, tail = ps[0], ' — '.join(ps[1:])
        if _L(tail) >= 16 and _L(head) >= 4:
            head, tail = _bal([head, tail])
            return _kp(head, ctx, first, lvl + 1) + '<div class="ksub">' + _ks(' — ') + _kp(tail, ctx, False, lvl + 1) + '</div>'
    # K2 라벨 사실마다 줄
    ps = _sp(p, ' · ')
    if len(ps) >= 2 and all(x.strip() for x in ps):
        bp = _bal(ps); labs = [bool(_lab(x)) for x in bp]
        if sum(labs) >= 2:
            groups = []
            for i, x in enumerate(bp):
                if labs[i] or not groups: groups.append([i])
                else: groups[-1].append(i)
            if 2 <= len(groups) <= 7:
                lines = []
                for gi, g in enumerate(groups):
                    h = ''
                    for k, i in enumerate(g):
                        sep = '' if i == 0 else (_ks(' · ') if k == 0 else _ks(' · ', 'kj'))
                        h += sep + (_labh(bp[i], ctx, first and i == 0) if labs[i] else _kf(bp[i], ctx, first and i == 0))
                    lines.append(h)
                return _div(lines)
    # 'X: 긴 내용' → 머리 줄 + 나머지
    m = re.match(r'^([^:：=/(){}\[\]"“”·]{2,30}?[:：])(\s)(.+)$', p, re.S)
    if m and n > 70 and _L(m.group(3)) > 50 and m.group(1).count('==') % 2 == 0 and m.group(1).count('**') % 2 == 0:
        rest = _kp(m.group(3), ctx, False, lvl + 1)
        if rest.startswith('<div') or 'class="kfi' in rest or 'class="ksi' in rest:
            return '<div class="kl klh">' + inline(m.group(1), ctx, first) + _ks(m.group(2), 'kj') + '</div>' + ('<div class="kl">' + rest + '</div>' if not rest.startswith('<div') else rest)
    # K4 ' → ' 단계 흐름
    ps = _sp(p, ' → ')
    if (len(ps) >= 4 and n > 70 or len(ps) == 3 and n > 80) and all(x.strip() for x in ps):
        bp = _bal(ps)
        return '<span class="kst">' + ''.join(f'<span class="ksi{" kfn" if _L(x) <= KFN else ""}">' + (_ks(' → ', 'ka') if i else '') + inline(x, ctx, first and not i) + '</span>' for i, x in enumerate(bp)) + '</span>'
    # K6 ' + ' 부연 묶음
    ps = _sp(p, ' + ')
    if n > 90 and len(ps) >= 2 and all(_L(x) >= 12 for x in ps) and any(re.search(r'[(（]', x) for x in ps) and len(ps) <= 7:
        bp = _bal(ps)
        return _div([(_ks(' + ', 'kp') if i else '') + _kp(x, ctx, first and not i, lvl + 1) for i, x in enumerate(bp)])
    # K3 ' · ' 사실 흐름
    ps = _sp(p, ' · ')
    if n > 56 and len(ps) >= 3 and all(x.strip() for x in ps):
        return _flow(_bal(ps), ' · ', ctx, first)
    # K3b 띄어 쓰지 않은 'A·B·C·D' 나열(80자 초과, 4개↑) → 항목 흐름(라벨 'X = '가 있으면 라벨 굵게 + 흐름)
    if n > 80:
        m = _lab(p); body = m.group(4) if m else p
        ps = _sp(body, '·')
        if len(ps) >= 4 and all(x.strip() and not x.startswith(' ') and not x.endswith(' ') for x in ps):
            h = _flow(_bal(ps), '·', ctx, first and not m)
            return (inline(m.group(1), ctx, first) + '<b class="lbl">' + inline(m.group(2), ctx, False) + '</b>' + inline(m.group(3), ctx, False) + h) if m else h
    return inline(p, ctx, first)
def _kf(p, ctx, first):
    """라벨 줄에 붙는 라벨 없는 사실 — inline"""
    return inline(p, ctx, first)
def _flow(bp, sep, ctx, first):
    """K3 사실 흐름 — 사실마다 .kfi(24자 이하는 끊지 않는 덩어리). ux3 fix V06: 14자 미만 조각이 '→'로 시작하거나 앞 사실이 라벨 없는 '→' 흐름이면
    앞 사실에 붙임('Common carotid → internal(뇌) · external(얼굴)'이 한 사실) — 구분자는 그대로(글자 불변)"""
    groups = []
    for i, x in enumerate(bp):
        if groups and _L(x) < 14:
            prev = bp[groups[-1][-1]]
            if _plain(x).strip().startswith('→') or ('→' in _plain(prev) and not _lab(prev) and not _lab(x)):
                groups[-1].append(i); continue
        groups.append([i])
    out = ''
    for g in groups:
        n = sum(_L(bp[i]) for i in g) + 3 * (len(g) - 1)
        out += f'<span class="kfi{" kfn" if n <= KFN else ""}">' + ''.join(inline(bp[i], ctx, first and not i) + (_ks(sep, 'kfs') if i < len(bp) - 1 else '') for i in g) + '</span>'
    return '<span class="kfw">' + out + '</span>'
def _txt(h): return html.unescape(re.sub(r'<[^>]+>', '', h))
def key_lines(v, ctx):
    """🔑 상자·정리표 🔑 칸 본문(ux3 N1) — 옛 render_block과 같은 틀(번호·라벨·' / ' 목록)에 조각마다 K1~K6. 글자가 옛 렌더와 다르면 옛 렌더"""
    old = render_block(v, ctx); KL[0] += 1
    _IP[0] = lambda p, c, li=False: _kp(p, c, True, 0, li)
    try: new = render_block(v, ctx)
    except Exception: new = None
    finally: _IP[0] = None
    if new is None or _txt(new) != _txt(old): KL[2] += 1; return old
    if new != old: KL[1] += 1
    return new
def render_keybox(v, ctx): return f'<div class="kb">{key_lines(v, ctx)}</div>'
GK = [0, 0]   # 요지 수 · 단계 흐름(K4)을 쓴 요지 수(빌드 로그)
def _gsteps(p, ctx, first=True):
    """ux3 fix flow V07 요지의 ' → ' 흐름 — 3단계↑·40자 초과면 단계마다 .ksi(24자 이하는 끊지 않는 덩어리 · 줄머리 '→ ') — 좁은 정리표 🔑 칸에서 단계 경계로 줄이 바뀜"""
    ps = _sp(p, ' → ')
    if len(ps) >= 3 and _L(p) > 40 and all(x.strip() for x in ps):
        bp = _bal(ps); GK[1] += 1
        return '<span class="kst">' + ''.join(f'<span class="ksi{" kfn" if _L(x) <= KFN else ""}">' + (_ks(' → ', 'ka') if i else '') + inline(x, ctx, first and not i) + '</span>' for i, x in enumerate(bp)) + '</span>'
    return inline(p, ctx, first)
def gist_html(g, ctx):
    """한 줄 요지(ux3 N3) — 첫 최상위 ' — ' 뒤가 16자↑면 둘째 줄 .ksub(구분자는 .ksep로 남김 — 글자 불변) · 긴 '→' 흐름은 단계 단위(flow V07)"""
    GK[0] += 1; ref = _txt(inline(g, ctx)); k0 = GK[1]
    ps = _sp(g, ' — ')
    if len(ps) >= 2 and ps[0].strip():
        head, tail = ps[0], ' — '.join(ps[1:])
        if _L(tail) >= 16:
            head, tail = _bal([head, tail]); h = _gsteps(head, ctx) + '<span class="ksub">' + _ks(' — ') + _gsteps(tail, ctx, False) + '</span>'
            if _txt(h) == ref: return h
            h = inline(head, ctx) + '<span class="ksub">' + _ks(' — ') + inline(tail, ctx, False) + '</span>'; GK[1] = k0
            if _txt(h) == ref: return h
    h = _gsteps(g, ctx)
    if _txt(h) == ref: return h
    GK[1] = k0; return inline(g, ctx)
def line_units(h):
    """ux3 N5 점검용 — 렌더 HTML을 '화면에서 한 덩어리로 흐르는 글자' 단위로 나눔(블록 div·li·목록 경계, 흐름 항목 .kfi·.ksi·.ksub 시작에서 끊음 · 숨긴 구분자 .kh 글자는 뺌 · 가로 흐름 목록 kflow·sflow·cflow의 li는 이어짐)"""
    from html.parser import HTMLParser
    BLK = {'div', 'ul', 'ol', 'li', 'h4'}
    class U(HTMLParser):
        def __init__(s): super().__init__(); s.units = []; s.cur = ''; s.st = []; s.hide = 0
        def flush(s):
            t = re.sub(r'\s+', ' ', s.cur).strip()
            if t: s.units.append(t)
            s.cur = ''
        def handle_starttag(s, tag, a):
            c = dict(a).get('class', '') or ''
            inflow = tag == 'li' and any(x in ('kflow', 'sflow', 'cflow') for st in s.st for x in st[1].split())
            if (tag in BLK and not inflow) or (tag == 'span' and re.search(r'\b(kfi|ksi|ksub)\b', c)): s.flush()
            hid = tag == 'span' and 'ksep' in c.split() and 'kh' in c.split()
            if hid: s.hide += 1
            if tag not in ('wbr', 'br', 'img'): s.st.append((tag, c, hid))
        def handle_endtag(s, tag):
            while s.st:
                t, c, hid = s.st.pop()
                if hid: s.hide -= 1
                if t == tag: break
            if tag in BLK: s.flush()
        def handle_data(s, d):
            if not s.hide: s.cur += d
    u = U(); u.feed(h); u.flush(); return u.units
