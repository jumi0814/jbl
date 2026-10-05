import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import os
import re, json, html, sys, os, datetime, zipfile, io, base64
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import assemble as A
import reflow, lecparse, subject as S
from PIL import Image
SID, TITLE, EN, COLOR, PROFS = S.SID, S.TITLE, S.EN, S.COLOR, S.PROFS
esc = lambda s: html.escape(str(s), quote=True)
Q = A.Q; QMAP = {q['id']: q for q in Q}; PRED = A.PRED; IMG = A.IMG
YR = lambda y: '20%02d' % y
LECNAME = {k: v[1] for k, v in A.LECMAP.items()}
VNAME = {'ok': '강의자료와 일치', 'part': '부분 일치·부분 근거', 'diff': '⚠ 강의자료와 불일치', 'none': '강의자료에 근거 없음', 'na': '대응 강의자료 없음'}
aid = lambda x: f'{SID}:{x}'
import hashlib as _hl
UNREC = re.compile(r'^\d+(\s*-\s*\d+)?\s*[.)]\s*미복원\s*$')   # ux2 fixB VIS14 문제 전체가 '미복원'인 문항(풀 수 없음) · ESTH '3-5. 미복원'처럼 번호 범위도
PICKLAB = {'틀린 보기': '정답 · 틀린 설명'}   # ux2 fixB VIS07 부정 발문('틀린 것을 고르시오')의 답 = 정답(틀린 설명) — 초록 강조와 같은 말로
def cut_hint(h, n=130):
    """ux2 fixB VIS12 강의 카드 💬 한 줄 — n자 안에서 ' · '·문장 끝·닫는 따옴표 뒤(따옴표 짝이 맞는 자리)에서 자르고 ' …'(따옴표 한가운데서 끊지 않음)"""
    if len(h) <= n: return h
    best = -1
    for m in re.finditer(r' · |[.!]\s|["”]\s', h[:n + 1]):
        e = m.start() if m.group(0) == ' · ' else m.start() + 1
        if e >= 40 and h[:e].count('"') % 2 == 0 and h[:e].count('“') == h[:e].count('”'): best = e
    if best < 0:
        best = h.rfind(' ', 0, n)
        if best < 40: best = n
        while h[:best].count('"') % 2: best = h.rfind('"', 0, best)
    return h[:best].rstrip(' ·,') + ' …'
def slug(*xs):
    t = '|'.join(xs); base = re.sub(r'[^a-z0-9가-힣]+', '', t.lower())[:24]
    return base + '_' + _hl.md5(t.encode('utf-8')).hexdigest()[:6]
def card_aid(k, c): return aid(k + ':' + slug(c['en'], c['ko']))
heat = lambda n: 'h2' if n >= 2 else ('h1' if n == 1 else 'h0')
ctx = {'QMAP': QMAP, 'YR': YR, 'LECNAME': LECNAME, 'cited': set()}
LEC = lecparse.load_all()
# ux4e 사용자 '과목명·강의자료 이름은 줄이지 말고 원래 그대로' — 화면에 보이는 강의 이름 = 정리본 원고의 강의 제목(L['title']) 그대로. LECNAME(LECMAP 짧은 이름)은 두고 화면에는 쓰지 않음
LECT = {L_['k']: L_['title'] for L_ in LEC}
lname = lambda k: LECT.get(k) or LECT.get(getattr(S, 'IMG_ALIAS', {}).get(k, '')) or re.sub(r'\s*\([^)]*\)\s*$', '', LECNAME.get(k, k)) or k
# ---- 머리말(! 줄) 문장 나누기(U24): 괄호·따옴표 밖의 '. '에서 — 교수님 예고·강조 문장만 📣로
HINT_RE = re.compile(r'시험|강조|예고|공개|QUIZ|퀴즈|별표|중요(?!성)|keyword|키워드')
def split_note(n):
    out, last = [], 0
    for i, ch, d in lecparse._depth_iter(n):
        if d == 0 and ch == '.' and n[i + 1:i + 2] == ' ' and not re.search(r'(?:\bp|\bvs|\be\.g|\bcf|\bFig|\bNo|\bex|\bi\.e)$', n[max(0, i - 4):i]):
            out.append(n[last:i + 1].strip()); last = i + 2
    out.append(n[last:].strip())
    return [x for x in out if x]
# ---- 카드 aid 고정(tools/aidlock.py · aid_lock.json): 원고를 다시 써도 옛 카드의 표시·✓가 새 카드로 이어지게
import aidlock
LOCK_P = os.path.join(DIR, 'aid_lock.json'); LOCK = aidlock.load(LOCK_P); AIDS, ALTS, _lk_log = {}, {}, []
for L_ in LEC:
    _a, _al, LOCK[L_['k']], _st = aidlock.assign(L_['k'], L_['cards'], LOCK.get(L_['k'], []), lambda j, c, k=L_['k']: card_aid(k, c))
    for j_ in range(len(L_['cards'])): AIDS[(L_['k'], j_)] = _a[j_]; ALTS[(L_['k'], j_)] = _al[j_]
    _lk_log.append(f"{L_['k']} 유지 {_st['keep']}·이관 {_st['moved']}·신규 {_st['new']}")
aidlock.save(LOCK_P, LOCK)
print('카드 aid 잠금:', ' / '.join(_lk_log))
def card_alt(k, j): return ' '.join([aid(k + ':c%d' % j)] + [a for a in ALTS[(k, j)] if a != aid(k + ':c%d' % j)])

for q in Q:
    L0 = reflow.reflow(q['text'])
    if L0: q['stem'] = re.sub(r'^\s*\d{1,3}(-\d)?\s?[.)]?\s*', '', L0[0]).strip(); q['short'] = q['stem'][:78]
# ---- 문항 → 강의 카드 위치
PROF_LEC = S.PROF_LEC
cand = {}
for L in LEC:
    for j, c in enumerate(L['cards']):
        for i in c['jb']: cand.setdefault(i, []).append((0, L['k'], j))
        for b_ in c['body']:
            if b_[0] == 'E':
                for i in b_[1][0]: cand.setdefault(i, []).append((1, L['k'], j))
Q2CARD = {}
def _cpages(k_, j_):
    """카드 쪽 범위('17-22' · '5·7' · '5, 7-9') → 쪽 집합"""
    out = set()
    for a_, b_ in re.findall(r'(\d+)(?:\s*[-~–]\s*(\d+))?', [L_ for L_ in LEC if L_['k'] == k_][0]['cards'][j_].get('rng', '') or ''):
        out |= set(range(int(a_), int(b_ or a_) + 1))
    return out
for i, lst in cand.items():
    q = QMAP.get(i); pl = PROF_LEC.get((q['prof'] or '').split('(')[0], []) if q else []
    own = getattr(S, 'IMG_ALIAS', {}).get(q['lk'], q['lk']) if q and q.get('lk') else ''   # annot lec=의 주 강의(보조 키는 본 강의로) — 같은 교수의 앞 강의에 짧은 ⭐만 있어도 주 강의 카드로(ESTH R19·S12 → SPE · T12 → VEN, 10-03)
    pg_ = q.get('lkp') if q else None   # annot lec=<키>:<쪽>의 쪽(assemble이 넘겨줄 때만 — ESTH) → 주 강의 안에서 그 쪽을 담은 카드가 주 카드(보조 카드 머리 jb=를 지우지 않아도 됨)
    lst.sort(key=lambda x: (x[1] != own, x[1] not in pl, bool(pg_) and x[1] == own and pg_ not in _cpages(x[1], x[2]), x[0]))
    Q2CARD[i] = (lst[0][1], lst[0][2])
for q in Q:
    if q['id'] in Q2CARD: q['lk'] = Q2CARD[q['id']][0]
    # 주석이 없는 문항: 연결된 정리본 카드의 ⭐ 시험포인트 줄을 대조 근거로 자동 채움(슬라이드 인용 포함)
    if q['id'] in Q2CARD and not q['A'] and not q['N'] and not q['M']:
        k_, j_ = Q2CARD[q['id']]; c_ = [L_ for L_ in LEC if L_['k'] == k_][0]['cards'][j_]
        etxt = next((t_ for kind_, v_ in c_['body'] if kind_ == 'E' for ids_, t_ in [v_] if q['id'] in ids_), '')
        pg_ = c_['figs'][0][0] if c_['figs'] else re.findall(r'\d+', c_.get('rng', '') or '0')[0]
        cites_ = ' '.join(f'[[{fk_ or k_}:{p_}]]' for p_, fk_ in c_['figs'][:3]) or f'[[{k_}:{pg_}]]'
        q['A'] = [(c_['ko'], etxt, A.cite_html(cites_))]
        q['auto'] = 1; q['v'] = 'ok' if q['v'] in ('', 'na') else q['v']

import trend
COVER = S.COVER
trend.analyze(Q, Q2CARD, LEC, COVER)
MENT_PROF = S.MENT_PROF
MENT_ALL = S.MENT_ALL
def st_chip(q):
    st = q.get('st')
    if not st or (q.get('v') == 'na' and not q.get('lk')): return ''
    a = st['latest']
    if a['kind'] == '짤': return f'<span class="chip jj" title="짤 — {YR(a["from"])}년에도 출제된 문제">짤</span>'   # 연도는 배지에 이미 있음(V06)
    if a['kind'] == '탈': return f'<span class="chip tt" title="탈 — 이 해에 처음 출제 · {"같은 카드에서 이전 기출이 있음(변형)" if a["tal"] == "변형" else "이전 기출이 없던 카드(새 영역)"}{", 교수 강조 쪽" if a.get("emph") else ""}">탈 · {"변형" if a["tal"] == "변형" else "새 영역"}{" · 💬" if a.get("emph") else ""}</span>'
    return f'<span class="chip base">{YR(a["y"])}년 — 기준선(이전 자료 없음)</span>'
def st_kind(q):
    """짤/탈 필터용: 최근 출제 해의 판정 — jj 짤 · tt 탈 · base 기준선 · '' 판정 없음"""
    st = q.get('st')
    if not st or (q.get('v') == 'na' and not q.get('lk')): return ''
    return {'짤': 'jj', '탈': 'tt'}.get(st['latest']['kind'], 'base')
def vchip(v):
    """카드 머리 대조 칩: 일치는 작은 '✓ 대조' 점 칩, 부분 일치·불일치만 글자 그대로, 근거 없음·자료 없음은 짧게(전체 뜻은 title)"""
    short = {'ok': '✓ 대조', 'none': '근거 없음', 'na': '자료 없음'}.get(v)
    return f'<span class="chip v-{v}{" vsm" if short else ""}" title="{VNAME[v]}">{short or VNAME[v]}</span>'
def split_qa(q):
    qs, as_, mode = [], [], 'q'
    for l in q['text'].split('\n'):
        if re.match(r'^\s*(유사복원\)|추가복원\)|\*?비슷한 복원|복원 원문)', l) or (q['id'] == 'Q23' and re.match(r'^\s*\(\d\)\s', l)): mode = 'q'
        if reflow.LABEL.match(l) and '참고' not in l.split(':')[0] and mode == 'q' and re.match(r'^\s*(\[답\]|답)', l): mode = 'a'
        (qs if mode == 'q' else as_).append(l)
    return '\n'.join(qs), '\n'.join(as_)
def yr_badge(q, big=True):
    ys = q['yrs']; n = len(ys)
    if not n: return '<span class="ybadge n0">연도 표기 없음</span>'
    lab_ = " · ".join(YR(y) for y in ys) if (big and n <= 6) else (" · ".join(YR(y) for y in ys[:4]) + (f" … {YR(ys[-1])}" if n > 4 else ""))
    return f'<span class="ybadge n{min(n,3)}" title="{" · ".join(YR(y) for y in ys)}"><b>{lab_}</b><i>{n}회 출제</i></span>'
def go(i, txt, cls='link', src=''): return f'<button class="{cls}" data-go="{i}"{f" data-src=\"{src}\"" if src else ""}>{txt}</button>'

CITE_BTN = re.compile(r'<button class="cite[^"]*" data-k="[^"]*" data-p="[^"]*">.*?</button>')
# ---- 대조·주변부 자동 구조화(U18): 긴 줄을 문장 → ' — ' → 나열(' / '·' · '·'; ') → 괄호·따옴표 안 나열 → ', ' 순으로 나눔. 글자는 그대로(나눈 자리의 구분자만 빠짐)
def _d0(s, sep):
    """깊이 0(괄호·따옴표 밖)에서 sep이 시작하는 자리"""
    return [i for i, ch, d in lecparse._depth_iter(s) if d == 0 and s.startswith(sep, i)]
def _cut(s, pos, keep):
    """pos 자리에서 자름 — keep='L'이면 구분자 첫 글자를 왼쪽에, 'R'이면 오른쪽 조각 첫머리에, ''이면 버림(길이 n)"""
    out, last = [], 0
    for i, n in pos:
        if keep == 'L': out.append(s[last:i + 1]); last = i + 1
        elif keep == 'R': out.append(s[last:i]); last = i + 1
        else: out.append(s[last:i]); last = i + n
    out.append(s[last:]); return [x.strip() for x in out if x.strip()]
def _groups(s):
    out, prev, a = [], 0, None
    for i, ch, d in lecparse._depth_iter(s):
        if prev == 0 and d > 0: a = i
        if prev > 0 and d == 0 and a is not None: out.append((a, i)); a = None
        prev = d
    return out
def _lbl(x):
    m = re.match(r'^([^:：()"“”/]{2,40}[:：])\s+(.+)$', x)
    return f'<b class="lbl">{lecparse.inline(m.group(1), ctx)}</b> {lecparse.inline(m.group(2), ctx)}' if m else None
def _ul(items, cls='klist'): return f'<ul class="{cls}">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'
def _pmerge(ps):
    """10-05 문장부호만 남은 조각('.'·')'·'/')은 앞 조각 끝에 붙임 — 화면에 '.' 한 줄이 따로 생기던 것"""
    out = []
    for x in ps:
        if out and re.fullmatch(r'\s*[.,;:)\]/·]+\s*', x): out[-1] = out[-1].rstrip() + x.strip()
        else: out.append(x)
    return out
def astruct(s, lvl=0):
    s = s.strip()
    if lvl > 5 or len(s) <= 190:
        if (len(s) > 150 or lecparse._facts(lecparse.split_top(s, ' / '))) and lvl == 0: return lecparse.render_block(s, ctx)   # 10-04 짧아도 ' / ' 사실 조각이면 줄마다
        return _lbl(s) or lecparse.inline(s, ctx)
    sub = lambda ps: _ul([astruct(x, lvl + 1) for x in _pmerge(lecparse._rebalance(ps))])
    blk = lambda ps: ''.join(f'<div class="kp">{astruct(x, lvl + 1)}</div>' for x in _pmerge(lecparse._rebalance(ps)))   # 문장·대시·쉼표로 나눈 조각은 점 없이 줄로
    # 1) 문장('. ' — p. 같은 약어 제외)
    pos = [(i, 1) for i in _d0(s, '. ') if not lecparse.ABBR.search(s[max(0, i - 8):i + 1])]   # 10-04 해부 약어(n. a. lig. proc. …)·번호(1.)·Perio. 뒤에서 문장을 자르지 않음
    ps = _cut(s, pos, 'L')
    if len(ps) >= 2 and min(len(x) for x in ps) >= 8: return blk(ps)
    # 1-2) 10-04 사용자 줄바꿈 전수(2차): 최상위 ' / '가 있으면 대시보다 먼저 — 'A — 설명 / B — 설명'이 대시에서 찢겨 'A' · '설명 / B' · '설명'으로 보이던 것
    ps = lecparse.split_top(s, ' / ')
    if len(ps) >= 2 and min(len(x) for x in ps) >= 12:
        m = re.match(r'^(.{4,80}?[:：])\s+(.+)$', ps[0])
        if m and not re.search(r'[()"“”]', m.group(1)): return f'<div class="klead">{lecparse.inline(m.group(1), ctx)}</div>' + blk([m.group(2)] + ps[1:])
        return blk(ps)
    # 2) ' — ' (대시는 뒤 조각 첫머리에)
    ps = _cut(s, [(i + 1, 1) for i in _d0(s, ' — ')], 'R')
    if len(ps) >= 2 and min(len(x) for x in ps) >= 10: return blk(ps)
    # 3) 나열
    e_ = lecparse.split_enum(s)
    if e_:
        ld, its, _c = e_
        return (f'<div class="klead">{lecparse.inline(ld, ctx)}</div>' if ld else '') + _ul([astruct(x, lvl + 1) for x in its], 'circ' if _c else 'klist')
    for sep, mn in ((' / ', 2), (' · ', 3), ('; ', 2), (' → ', 3)):
        ps = lecparse.split_top(s, sep)
        if len(ps) >= mn:
            m = re.match(r'^(.{4,80}?[:：])\s+(.+)$', ps[0])
            if m and not re.search(r'[()"“”]', m.group(1)): return f'<div class="klead">{lecparse.inline(m.group(1), ctx)}</div>' + sub([m.group(2)] + ps[1:])
            return sub(ps)
    # 4) 괄호·따옴표 안 나열 펼치기 — 가장 긴 묶음
    best = None
    for a_, b_ in _groups(s):
        inner = s[a_ + 1:b_]
        cand = []
        e_ = lecparse.split_enum(inner)
        if e_ and not e_[0]: cand.append(e_[1])
        for sep, mn in ((' / ', 3), (' · ', 4), ('; ', 3), (', ', 5)):
            its = lecparse.split_top(inner, sep)
            if len(its) >= mn: cand.append(its); break
        if cand and (best is None or b_ - a_ > best[1] - best[0]): best = (a_, b_, cand[0])
    if best:
        a_, b_, its = best; head = s[:a_ + 1].strip(); tail = s[b_ + 1:].strip()
        m = re.match(r'^(.{3,80}? — )(.+)$', its[0])
        if m: head += m.group(1).rstrip(); its = [m.group(2)] + its[1:]
        its[-1] = its[-1] + s[b_]
        pp = lecparse._rebalance([head] + its + ([tail] if tail else []))
        h_ = f'<div class="klead">{astruct(pp[0], lvl + 1) if len(pp[0]) > 190 else lecparse.inline(pp[0], ctx)}</div>' + _ul([astruct(x, lvl + 1) for x in pp[1:1 + len(its)]])
        return h_ + (f'<div class="ktail">{astruct(pp[-1], lvl + 1)}</div>' if tail else '')
    # 4b) 가장 긴 괄호·따옴표 묶음 안으로 들어가 다시 나눔(앞머리·꼬리는 따로 줄)
    gs = [g for g in _groups(s) if g[1] - g[0] > 80 and not re.match(r'^\s*(?:은|는|이|가|을|를|과|와|의|로|으로|에|에서|라고|이라고|란|도|만)(?:\s|$)', s[g[1] + 1:])]   # 10-05 인용·괄호 뒤가 조사로 이어지면 그 묶음에서 자르지 않음(" 한 글자 줄·조사로 시작하는 줄)
    if gs:
        a_, b_ = max(gs, key=lambda g: g[1] - g[0]); head = s[:a_ + 1].strip(); inner = s[a_ + 1:b_ + 1]; tail = s[b_ + 1:].strip()
        return (f'<div class="klead">{astruct(head, lvl + 1)}</div>' if head else '') + f'<div class="kin">{astruct(inner, lvl + 1)}</div>' + (f'<div class="ktail">{astruct(tail, lvl + 1)}</div>' if tail else '')
    # 5) ', ' 로 140자 안팎씩
    ps = _cut(s, [(i, 1) for i in _d0(s, ', ')], 'L')
    if len(ps) >= 2:
        out, cur = [], ''
        for x in ps:
            if cur and len(cur) + len(x) > 140: out.append(cur); cur = x
            else: cur = (cur + ' ' + x).strip()
        out.append(cur)
        if len(out) >= 2: return blk(out)
    return lecparse.inline(s, ctx)
def auto_item(ko, etxt, cites):
    """annot가 없는 문항: '✓ 정리본 «카드» 일치' 한 줄 + ⭐ 시험포인트 원문(구조화) + 인용 칩 3개까지"""
    return f'<div class="agree">✓ 정리본 «{esc(ko)}» 일치</div>' + (f'<div class="aex"><span class="ui">⭐</span><div class="kb">{astruct(etxt) if len(etxt) > 190 else lecparse.render_block(etxt, ctx)}</div></div>' if etxt else '') + cite_row(CITE_BTN.findall(cites))
def _inl_html(x):
    """글자 + 인용 버튼·⚠💡 HTML에서 글자 조각에만 원고 표기({r:}·==·**) 렌더 — 10-05 해설 강조 표시"""
    ps = re.split(r'(<button class="cite[^"]*"[^>]*>.*?</button>|<b class="(?:warn|bulb)">[^<]*</b>)', x)
    return ''.join(t if (i % 2) else lecparse.inline(html.unescape(t), ctx) for i, t in enumerate(ps))
def struct_item(x):
    """대조(A)·주변부(M)·메모(N) 항목(HTML): 150자를 넘거나 ' / '가 3개 이상이면 astruct로 점 목록화하고 인용 칩은 끝의 .cites 줄로 모음"""
    plain = html.unescape(re.sub(r'<[^>]+>', '', CITE_BTN.sub('', x)))
    if len(plain) <= 150 and plain.count(' / ') < 3: return _inl_html(x) if re.search(r'\{r:|==|\*\*', plain) else x
    cites = list(dict.fromkeys(CITE_BTN.findall(x))); body = CITE_BTN.sub(' ', x); keep = []   # 문장마다 같은 쪽을 인용한 원고 — .cites 줄에는 한 번만
    def ph(m): keep.append(m.group(0)); return f'\ue000{len(keep) - 1}\ue001'
    body = re.sub(r'<b class="(?:warn|bulb)">[^<]*</b>', ph, body)
    if '<' in body: return x
    raw = re.sub(r'\s+', ' ', html.unescape(body)).strip()
    r = astruct(raw) if len(raw) > 190 else lecparse.render_block(raw, ctx)
    r = re.sub('\ue000(\\d+)\ue001', lambda m: keep[int(m.group(1))], r)
    return r + (f'<div class="cites">{" ".join(cites)}</div>' if cites else '')
def _top_lis(h):
    """ux2 F09: h가 목록 하나(<ul class="klist">…</ul>)뿐이면 맨 위 li들의 안쪽 HTML, 아니면 None"""
    m = re.match(r'^<ul class="klist(?: lab)?">(.*)</ul>$', h, flags=re.S)
    if not m: return None
    body = m.group(1); out = []; depth = 0; start = last = 0
    for t in re.finditer(r'<(/?)(ul|ol|li)\b[^>]*>', body):
        if not t.group(1):
            if t.group(2) == 'li' and depth == 0:
                if body[last:t.start()].strip(): return None
                start = t.end()
            depth += 1
        else:
            depth -= 1
            if depth < 0: return None
            if t.group(2) == 'li' and depth == 0: out.append(body[start:t.start()]); last = t.end()
    return out if out and not depth and not body[last:].strip() else None
def item_lis(x):
    """대조·주변부 한 항목 → li 안쪽 HTML 목록: 구조화 결과가 '점 목록 하나 + 인용 줄'뿐이면 바깥 li를 풀어 항목을 형제 li로(빈 글머리 없음 — ux2 F09), 인용 줄은 마지막 li 끝에"""
    r = struct_item(x)
    m = re.match(r'^(<ul class="klist(?: lab)?">.*</ul>)(<div class="cites">(?:(?!</ul>).)*</div>)?$', r, flags=re.S)
    its = _top_lis(m.group(1)) if m else None
    if its: its[-1] += m.group(2) or ''; return its
    return [r]
# ---- 10-05 사용자 'jb문제 란에서 가독성을 전면적으로 … 인용이나 근거, 필기파트가 중구난방 … 슬라이드 원문 보는 버튼도 … 너무 크게' — 대조·주변부 항목 모양(글자 그대로, 배치만):
#  A 줄 = [판정 꼬리표] 위치 → 슬라이드 인용 상자(" … " 안 ' / ' = 한 줄씩) → 설명 줄 → 작은 근거 줄(📄 강의명 쪽 쪽 — 강의명은 한 번) · M 줄 = 라벨로 📄 같은·인접 슬라이드 / ✍ 필기 / 🔁 변형 대비·함정 / 그 밖 소절에 모음
VWORD = re.compile(r'일치|불일치|부분|근거 없음|보강|보충|정답|오답|다른 점|대응|정정|틀림|옳음|불가|보류|×|○')
def _vcls(v):
    if re.search(r'불일치|×|오답|다른 점|근거 없음|정정|틀림', v): return 'vd'
    if '부분' in v: return 'vp'
    if re.search(r'일치|○|정답|대응|옳음', v): return 'vk'
    return 'vi'
def _pdepth(t):
    d = 0
    for ch in t:
        if ch == '(': d += 1
        elif ch == ')': d = max(0, d - 1)
    return d
def _qspan(s):
    """처음 나오는 큰따옴표 묶음 (여는 자리, 닫는 자리)"""
    for i, ch in enumerate(s):
        if ch in '"“' and _pdepth(s[:i]) > 0: return None   # 10-05 괄호 안 인용은 상자로 떼지 않음(문장 속 덧말) — '1)'처럼 짝 없는 닫는 괄호는 세지 않음
        if ch in '"“':
            j = s.find('"' if ch == '"' else '”', i + 1)
            return (i, j) if j > i else None
    return None
CITE_ONE = re.compile(r'<button class="(cite[^"]*)" data-k="([^"]*)" data-p="([^"]*)">(.*?)</button>')
def cite_row(cites):
    """인용 칩 → 작은 근거 줄: 같은 강의는 이름 한 번 + 쪽 링크들(버튼 = 쪽 글자, data-k·data-p 그대로)"""
    if not cites: return ''
    gs = []
    for c in cites:
        m = CITE_ONE.match(c)
        if not m: gs.append(('', [c])); continue
        cls, k, p_, t = m.groups(); mm = re.match(r'^(.*?)\s*((?:슬라이드|p\.)\s?[\d–\-·,~ ]+)$', t)
        nm, pg = (mm.group(1).strip(), mm.group(2)) if mm else ('', t)
        m3 = None if mm else re.match(r'^(.*?)\s*‘(.+)’$', t)
        if m3: nm, pg = m3.group(1).strip(), (('p.' + m3.group(2)) if re.fullmatch(r'[\d–\-·,~ ]+', m3.group(2)) else m3.group(2))   # 쪽 이미지가 없는 강의 인용 ‘4’ → p.4
        b_ = f'<button class="{cls} cz" data-k="{k}" data-p="{p_}" title="{esc(t)}">{pg}</button>'
        if gs and gs[-1][0] == nm and nm: gs[-1][1].append(b_)
        else: gs.append((nm, [b_]))
    return '<div class="cites cz">' + ''.join(f'<span class="cg">{f"<span class=czk>{nm}</span>" if nm else ""}{"".join(bs)}</span>' for nm, bs in gs) + '</div>'
def _qhtml(qt):
    if '\u2029' in qt: return ''.join(_qhtml(x) for x in qt.split('\u2029'))
    tl = re.search(r'["”][.,;:)\]]*$', qt); tl = tl.group(0) if tl else qt[-1]
    o, c_ = qt[0], tl; inner = qt[1:len(qt) - len(tl)].strip()
    ps = lecparse._rebalance(lecparse.split_top(inner, ' / ')) if ' / ' in inner else [inner]
    ps = [x for x in ps if x.strip()] or ['']
    ps[0] = o + ps[0]; ps[-1] = ps[-1] + c_
    return ''.join(f'<div class="ql">{_lbl(x) if (len(ps) > 1 and _lbl(x)) else lecparse.inline(x, ctx)}</div>' for x in ps)
PGTOK = re.compile(r'\s*(?:—\s*)?\(?(?:pp?\.\s?\d+[a-z]?(?:\s?[-~–,·]\s?\d+)*|슬라이드\s?\d+(?:\s?[-~–,·]\s?\d+)*)\)?(?=$|[\s:：,)\]—])')
def _nopg(s):
    """10-05 사용자 '선지마다 설명 앞에 어디 몇쪽 내용인지 나와있는건 없애고, 근거란에만 표시' — 항목 머리(위치·라벨)의 쪽 표기를 뺌(근거 줄이 있을 때만 부름)"""
    t = PGTOK.sub(' ', s)
    t = re.sub(r'\(\s*\)', '', t); t = re.sub(r'\s{2,}', ' ', t); t = re.sub(r'\s+([:：,)])', r'\1', t)
    return re.sub(r'^[\s—·,:：]+|[\s—·,]+$', '', t)
def _nopg_head(raw):
    """머리 라벨('5-1) ×(24): p.13 …', 'p.6: …', '26 필기(p.6) …')의 쪽 표기만 뺌 — 본문 글은 그대로"""
    m = re.match(r'^([^"“:：]{0,60}?[:：])(\s*)(.*)$', raw)
    if m:
        lab = _nopg(m.group(1)[:-1]); rest = re.sub(r'^\(?(?:pp?\.\s?\d+[a-z]?(?:\s?[-~–,·]\s?\d+)*)\)?\s+', '', m.group(3))
        return (lab + m.group(1)[-1] + ' ' + _nopg_pre(rest)) if lab else _nopg_pre(rest)
    return _nopg_pre(re.sub(r'^\(?(?:pp?\.\s?\d+[a-z]?(?:\s?[-~–,·]\s?\d+)*)\)?[\s:：]+', '', raw))
def _nopg_pre(t):
    """첫 인용 앞 40자 안의 머리('25 p.6 필기 "…', '26 필기 — p.7 "…')에서 쪽 표기만 뺌"""
    i = min([k for k in (t.find('"'), t.find('“')) if k >= 0] or [-1])
    if 0 < i <= 40 and PGTOK.search(t[:i]): return _nopg(t[:i]) + ' ' + t[i:]
    return t
QPART = re.compile(r'(?:은|는|이|가|을|를|에|의|로|도|와|과|면|고|며|서|게|인|한|된|던|할|될)$')
def aitem_lis(x, kind='A'):
    """대조(A)·주변부(M) 한 줄(HTML: 글자 + 인용 버튼 + ⚠💡) → li 안쪽 HTML 목록"""
    cites = list(dict.fromkeys(CITE_BTN.findall(x))); body = CITE_BTN.sub(' ', x)
    keep = []
    def ph(m): keep.append(m.group(0)); return f'{len(keep) - 1}'
    body = re.sub(r'<b class="(?:warn|bulb)">[^<]*</b>', ph, body)
    if '<' in body: return item_lis(x)
    raw = re.sub(r'\s+([.,;)])', r'\1', re.sub(r'\s+', ' ', html.unescape(body))).strip()   # 인용 칩을 뺀 자리의 ' .' 꼬리
    back = lambda h_: re.sub('(\\d+)', lambda m: keep[int(m.group(1))], h_)
    tag = ''
    m = re.match(r'^(.{1,24}?)\s+—\s+(.+)$', raw)
    if kind == 'A' and m and VWORD.search(m.group(1)) and not re.search(r'["“\[]', m.group(1)) and m.group(1).count('(') == m.group(1).count(')'):
        tag = f'<span class="vtag {_vcls(m.group(1))}">{back(esc(m.group(1)))}</span>'; raw = m.group(2)   # 10-05 ⚠ 자리표시(\ue000n\ue001)가 꼬리표에 그대로 보이던 것(사용자 사진 '⊠0⊠ 치료법은 부분')
    if cites: raw = _nopg_head(raw)
    qs = _qspan(raw); cr = cite_row(cites)
    if qs and re.match(r'^(?:은|는|이|가|을|를|과|와|의|로|으로|에|에서|라고|이라고|이란|란|도|만|처럼|보다|이며|이고|이다|라는|이라는)(?:\s|[,.)]|$)', raw[qs[1] + 1:].lstrip()): qs = None   # 10-05 인용 뒤가 조사로 이어지면 문장 속 인용 — 상자로 떼지 않음
    pre_ = raw[:qs[0]].strip() if qs else ''
    if qs and qs[0] <= 80 and qs[1] - qs[0] >= 40 and re.fullmatch(r'[^"“]{0,80}?[:：]?', pre_) and not QPART.search(pre_.rstrip(':：')):   # 10-05 사용자 '"기억해줬으면 좋겠다" 이건 왜 굳이 줄바꿈하고 상자에' — 40자 이상 인용이 머리·라벨 바로 뒤에 올 때만 상자(짧은 인용·문장 속 인용은 같은 줄)
        loc = raw[:qs[0]].strip(); qt = raw[qs[0]:qs[1] + 1]; aft = raw[qs[1] + 1:].strip()
        mp = re.match(r'^[.,;:)\]]+', aft)
        if mp: qt += mp.group(0); aft = aft[mp.end():].strip()   # 인용 뒤 마침표만 남으면 인용 끝에(따로 '.' 한 줄이 생기던 것)
        aft = re.sub(r'^[/—,·]\s+', '', aft)
        while True:   # 10-05 통일: 바로 이어지는 인용(" / "…")은 같은 상자에 한 줄 더
            m4 = re.match(r'^(?:/\s*)?(["“])', aft)
            if not m4: break
            q2 = _qspan(aft[m4.start(1):])
            if not q2: break
            j_ = m4.start(1) + q2[1] + 1; mp2 = re.match(r'^[.,;:)\]]+', aft[j_:]); j2 = j_ + (mp2.end() if mp2 else 0)
            if re.match(r'^\s*(?:은|는|이|가|을|를|과|와|의|로|으로|에|라고|란|도)(?:\s|$)', aft[j2:]): break
            qt += '\u2029' + aft[m4.start(1):j2]; aft = re.sub(r'^[/—,·]\s+', '', aft[j2:].strip())   # 다음 사실 앞 구분자 ' / '는 줄 머리에 남기지 않음
        loc = loc.rstrip(':：').strip()
        hd = tag + (f'<span class="aloc">{lecparse.inline(loc, ctx)}</span>' if loc else '')
        ah = ''
        if aft: ah = f'<div class="acm">{astruct(aft) if len(aft) > 190 else (lecparse.render_block(aft, ctx) if (len(aft) > 150 or lecparse._facts(lecparse.split_top(aft, " / "))) else lecparse.inline(aft, ctx))}</div>'
        qh_ = _qhtml(qt)
        if hd: qh_ = qh_.replace('<div class="ql">', f'<div class="ql"><span class="ahd in">{hd}</span> ', 1)   # 10-05 사용자 '하나의 선지에 대한 설명인데 너무 많은 칸' — 머리 라벨은 인용 상자 첫 줄 안에(따로 한 줄 쓰지 않음)
        return [back(f'<blockquote class="aq">{qh_}</blockquote>' + ah) + cr]
    rest = html.escape(raw, quote=False)
    rest = re.sub('(\\d+)', lambda m: keep[int(m.group(1))], rest)
    lis = item_lis(rest) if raw else ['']
    if tag:
        if lis[0].startswith('<'): lis[0] = f'<div class="ahd">{tag}</div>' + lis[0]
        else: lis[0] = f'<span class="ahd in">{tag}</span> ' + lis[0]
    m2 = re.match(r'^([^:<"“”]{1,40}?:)(\s)', lis[0])
    if m2: lis[0] = f'<b class="lbl">{m2.group(1)}</b>' + lis[0][len(m2.group(1)):]
    lis[-1] += cr
    return lis
def note_html(x):
    """N(연도·판본 메모) — 인용 칩은 끝의 작은 근거 줄로"""
    cites = list(dict.fromkeys(CITE_BTN.findall(x)))
    if not cites: return struct_item(x)
    body = re.sub(r'\s+([.,·)])', r'\1', re.sub(r'\s{2,}', ' ', CITE_BTN.sub(' ', x))).strip()
    return struct_item(body) + cite_row(cites)
MKIND = (('s', '📄 같은·인접 슬라이드'), ('n', '✍ 필기'), ('v', '🔁 변형 대비·함정'), ('e', '📌 그 밖'))
def _mkind(lab):
    if '필기' in lab: return 'n'
    if re.search(r'변형|함정|주의|혼동|헷갈|비교|구별', lab): return 'v'
    if re.search(r'슬라이드|p\.\s?\d|쪽|앞|뒤|같은|표|그림|Table|Fig', lab): return 's'
    return 'e'
def mgroups(M):
    """주변부 줄 → 종류별 소절(라벨 없는 줄은 앞 줄 종류를 이음 — 이어지는 말)"""
    G = {k: [] for k, _ in MKIND}; prev = 'e'
    for x in M:
        pl = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', CITE_BTN.sub('', x)))).strip()
        m = re.match(r'^([^:]{1,60}?)[:：]\s', pl)
        if m and (m.group(1).lstrip()[:1] in '"“' or (m.group(1).count('"') % 2) or m.group(1).count('“') != m.group(1).count('”')): m = None   # 따옴표로 시작하거나 따옴표 짝이 안 맞는 앞부분은 라벨 아님(인용 뒤 콜론)
        k = _mkind(m.group(1)) if m else prev
        G[k].append(x); prev = k
    used = [(k, t) for k, t in MKIND if G[k]]
    if len(used) == 1 and used[0][0] == 'e': return '<ul>' + ''.join(f'<li>{y}</li>' for x in G['e'] for y in aitem_lis(x, 'M')) + '</ul>'
    return ''.join(f'<div class="amg amg-{k}"><div class="amgh noann">{t}</div><ul>' + ''.join(f'<li>{y}</li>' for x in G[k] for y in aitem_lis(x, 'M')) + '</ul></div>' for k, t in used)
ANS_REFONLY = re.compile(r'\(?\s*(?:해설|해답|아래|위)?\s*(?:참조|참고)\s*\)?\s*\.?')
def ans_head(q):
    """JB 답 핵심 줄(참고·해설 앞) — (줄 목록, 라벨 뗀 핵심 글)"""
    _, at = split_qa(q); out = []
    for s_ in reflow.reflow(at):
        if re.match(r'^\s*(참고|해설)\s*[:：)]?', s_): break
        out.append(s_)
    return out, re.sub(r'^\s*(?:\[답\]|답)\s*[:：)]?\s*', '', ' '.join(out)).strip()
def first_sent(t):
    """괄호·따옴표 밖 첫 '. '까지(없으면 전체)"""
    for i, ch, d in lecparse._depth_iter(t):
        if d == 0 and ch == '.' and t[i + 1:i + 2] == ' ' and i > 8 and not re.search(r'(?:\bp|\bvs|\be\.g|\bcf|\bFig|\bNo|\bex|\bi\.e)$', t[max(0, i - 4):i]): return t[:i + 1]
    return t
def src_short(q):
    """ux2 F04 출처 한 줄: 'JB 25판 · 2024년 칸 · 처방전과 금연요법 1번' → '2024년 칸 1번'(판 연도는 표시하지 않음 — 전체는 title)"""
    s_ = re.sub(r'^\s*JB\s*\d{2}\s*판\s*·?\s*', '', q['src'] or '').strip()
    m = re.match(r'^(\d{4}년 칸)\s*·\s*.*?(\d+번)\s*$', s_)
    return f'{m.group(1)} {m.group(2)}' if m else s_
def qcard(q, idx):
    qt, at = split_qa(q); n = len(q['yrs'])
    figq = ''.join(f'<img class="fig" loading="lazy" src="{IMG["crop"][k]}" alt="JB 그림">' for k in q['crops'].get('q', []))
    figa = ''.join(f'<img class="fig" loading="lazy" src="{IMG["crop"][k]}" alt="JB 그림(답)">' for k in q['crops'].get('a', []))
    lecchip = ''
    if q['id'] in Q2CARD:
        k, j = Q2CARD[q['id']]; lecchip = f'<button class="chip lec" data-golec="{k}:{j}">{esc(lname(k))} 정리본 →</button>'   # ux4 B3-6 문항 머리 12px 메타의 과목색 글자 링크(크롬 이모지 없음)
    # 출처·연도 근거(ux2 F04) — 카드 앞면은 [연도 배지][짤/탈][교수][📖] + 문제만. 출처 줄·연도 표기 근거·관련 문항은 답 절 끝 details '출처·연도 근거'로 보임
    # (DOM 자리는 문제 바로 뒤 그대로 — 글자 순서가 같아 형광펜 위치 불변. 화면 순서만 CSS order로 답 뒤). 판 연도는 표시하지 않음(CLAUDE.md) — 전체 출처는 title
    prov = [f'출처: {esc(src_short(q))}' if q['src'] else '', f'JB 괄호 {esc(q["jbtag"])}' if q['jbtag'] else 'JB 괄호 없음']
    if q['tal']: prov.append('JB 표기 (탈)')
    if q.get('lab24'): prov.append(f'JB 표기(2023년 시험): {esc(q["lab24"])}')
    sub = []
    if q.get('xtra'): sub.append(f'<span class="chip cmp">괄호에 없던 {"·".join(YR(y) for y in q["xtra"])}년 추가</span>')
    if q.get('pick'): sub.append(f'<span class="chip pk">⭐ {esc(q["pick"])}</span>')
    # 정답 보기(ux2 F01): 답이 보기 번호뿐이면 문제의 그 보기 줄에 data-ans(ok | 부정 발문이면 wrong) — 답을 펼쳤을 때만 강조(CSS) · 답 칸 .ans0 아래 '정답 보기 …' 한 줄(원문 부분 문자열·noann)
    head_, core_ = ans_head(q); pk = pick_choices(q, head_); at_h = reflow.render(at, ans=True) if at.strip() else ''
    qh = reflow.render(qt, True, choices=True)
    pick_ln = ''
    if pk and pk[1]:
        lab, lines = pk; dv = 'wrong' if lab == '틀린 보기' else 'ok'
        for x in lines: qh = re.sub(r'(<div class="ln li[^"]*")(>' + re.escape(esc(x)) + '</div>)', r'\1 data-ans="' + dv + r'"\2', qh, count=1)
        pick_ln = ''   # 10-05 사용자 'jb 미리보기 및 jb 답안에 정답 보기 3) … 정답보기는 없애도 될 것 같아' — 답 칸의 '정답 보기 …' 줄은 없앰(문제 보기 줄 강조 data-ans는 그대로)
    h = [f'<article data-aid="{aid(q["id"])}" class="qc {heat(n)} t{q["tier"]}" id="c-{q["id"]}" data-id="{q["id"]}" data-tier="{q["tier"]}" data-prof="{esc((q["prof"] or "").split("(")[0])}" data-lec="{q["lk"]}" data-n="{n}" data-y0="{q["yrs"][0] if n else 0}" data-yrs="{" ".join("%02d" % y for y in q["yrs"])}" data-st="{st_kind(q)}" data-v="{q["v"]}" data-idx="{idx}"{' data-unrec="1"' if UNREC.match(qt.strip()) else ''}>',
         f'<div class="qhead">{yr_badge(q)}{st_chip(q)}{f'<span class="chip pf">{esc(q["prof"])}</span>' if (q["prof"] or "").strip() else ''}{'<span class="chip unrec noann" title="JB에 문제가 복원되지 않음 — 안 푼 것·한 장씩 회차에서 뺌">미복원</span>' if UNREC.match(qt.strip()) else ''}{f'<span class="chip tier" title="{esc(TIERS.get(q["tier"], ""))}">참고 · {esc(TIERS.get(q["tier"], ""))[:22]}</span>' if q["tier"] != "A" else ""}{lecchip}{vchip(q["v"])}</div>',
         f'<div class="qtext">{qh}</div>{figq}']
    if q['fig'] and not figq: h.append('<div class="small">🖼 그림 문항 — 그림은 ‘JB 원본’ 버튼에서 쪽 전체로 확인(원본 쪽에는 답도 함께 보임).</div>')
    sd = [f'<div class="qsub"><span class="prov noann" title="{esc(q["src"] or "")}">{" · ".join(x for x in prov if x)}</span>{"".join(sub)}</div>']
    if q['yrsnote']: sd.append(f'<div class="note">연도 표기 근거: {esc(q["yrsnote"])}</div>')
    if q.get('rel') and q['rel'] in QMAP: r = QMAP[q['rel']]; sd.append(f'<div class="note">다른 해의 관련 문항(별개 출제): {go(r["id"], "·".join(YR(y) for y in r["yrs"]) + "년 · " + esc(r["short"]))}</div>')
    if q.get('pair') and q['pair'] in QMAP: sd.append(f'<div class="note">같은 내용이 JB의 다른 연도 칸에도 실려 있음: {go(q["pair"], esc(QMAP[q["pair"]]["src"]))}</div>')
    h.append(f'<details class="srcd"><summary class="noann">출처·연도 근거</summary>{"".join(sd)}</details>')
    jbb = ''.join(f'<button class="btn sm" data-jb="{q["ed"]}-{p}">JB 원본 {p}쪽</button>' for p in range(q['pg'], q['pg2'] + 1))
    deep = bool(q['A'] or q['M'] or q['N'] or q['other'] or 'class="exw' in at_h or q['tier'] == 'C')
    h.append(f'<div class="acts"><button class="btn pri" data-tog="1">답·해설</button>{"<button class=\"btn deepb noann\" data-deep=\"1\"><span class=\"d1\">자세히 ▾ <small>해설·대조·주변부</small></span><span class=\"d2\">간단히 ▴</span></button>" if deep else ""}<button class="btn mk ok" data-mk="ok">✓ 맞음</button><button class="btn mk ng" data-mk="ng">✗ 틀림</button><button class="btn mk bm" data-mk="bm">★</button>{jbb}</div>')
    ansh = reflow.render(at, ans=True) if at.strip() else "<div class=ln>(JB에 답 표기가 따로 없음 — 위 원문 참조)</div>"
    if pick_ln:
        ansh, n_ = re.subn(r'(<div class="ln lab lab-a ans0">.*?</div>)', lambda m_: m_.group(1) + pick_ln, ansh, count=1)
        if not n_: ansh = pick_ln + ansh
    exbtn = '<button class="btn sm exmore noann" data-exmore="1">해설 전체 보기 ▾</button>' if 'class="exw clamp"' in ansh else ''
    # 답 두 단계(ux2 F02): 1단계(.open) = JB 답 핵심(.ans0·정답 보기) + 대조 첫 항목의 '정답 …' 한 줄 + 📖 ⚡ 첫 줄 · 2단계(.open.deep) = 해설 전체·대조·주변부·다른 판본
    # 답 핵심이 비었거나 '해설 참조'뿐이면(excore) 1단계에도 해설(접힌 채)을 보임. 대조·주변부는 details(머리 = noann summary, 원래 h5는 글자 보존용으로 숨김)
    excore = not core_ or bool(ANS_REFONLY.fullmatch(core_))
    a = ['<div class="ans">', f'<section class="ab jbans{" excore" if excore else ""}"><h5>JB 답안 <small>글자는 원문 그대로 · 줄바꿈만 정리</small></h5><div class="lines">{ansh}</div>{exbtn}{figa}</section>']
    if q.get('K'):   # 10-05 사용자 'jb 문제들만 봐도 진짜 이해하고 암기할 수 있게' — annot 'K:' = 🎯 요점(왜 이 답인지·외울 축 — 강의자료 근거) · 1단계(답·해설)부터 보임
        a.append('<section class="ab key1"><h5 class="noann">🎯 요점 <small>왜 이 답인지 · 외울 것</small></h5><ul>' + ''.join(f'<li>{y}</li>' for x in q['K'] for y in aitem_lis(x, 'M')) + '</ul></section>')
    a1 = ''
    if q['A'] and not q.get('auto'):
        pl = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', CITE_BTN.sub('', q['A'][0])))).strip()
        if pl.startswith('정답'): a1 = f'<div class="a1k noann"><b>정답</b> {esc(first_sent(lecparse._plain(pl[2:].strip())))}</div>'   # 10-05 annot {r:} 표기가 정답 요지 줄에 그대로 보이던 것
    if a1: a.append(f'<div class="a1 noann">{a1}</div>')
    if q['A']:
        hd_ = f'🔎 강의자료 대조 <small>{VNAME[q["v"]]}</small>'
        lis_ = ''.join((f'<li class="auto">{auto_item(*x)}</li>' if q.get('auto') else ''.join(f'<li>{y}</li>' for y in aitem_lis(x, 'A'))) for x in q['A'])
        a.append(f'<details class="ab chk v-{q["v"]}"><summary class="noann">{hd_}</summary><h5>{hd_}</h5><ul>{lis_}</ul>{"".join(f"<div class='note{" yr" if re.match(r'^\s*연도', html.unescape(re.sub(r'<[^>]+>', '', x))) else ""}'>{note_html(x)}</div>" for x in q["N"])}</details>')
    elif q['tier'] == 'C':
        same = f' 같은 문제의 다른 수록본은 {go(q["same"], esc(QMAP[q["same"]]["short"]))}에서 강의자료와 대조했습니다.' if q.get('same') else ''
        a.append(f'<section class="ab chk v-na"><h5>🔎 강의자료 대조</h5><div class="small">받은 25·26년도 강의자료에는 이 교수님 파트에 대응하는 강의가 없어 대조하지 않았습니다(JB 원문만 수록).{same}</div></section>')
    if q['M']:
        hd_ = '🧭 주변부 확장 <small>같은·인접 슬라이드 — 변형 출제 대비</small>'
        a.append(f'<details class="ab more"><summary class="noann">{hd_}</summary><h5>{hd_}</h5>{mgroups(q["M"])}</details>')
    if q['id'] in Q2CARD:
        k, j = Q2CARD[q['id']]; c_ = [L_ for L_ in LEC if L_['k'] == k][0]['cards'][j]
        key_ = next((v for t, v in c_['body'] if t == 'K'), '')
        m1_ = (' <span class="lkm">⚡ ' + lecparse.inline(c_['recall'][0], ctx) + '</span>') if c_['recall'] else ''
        rec_ = ''.join(lecparse.render_recall(x, ctx) for x in c_['recall'])
        a.append(f'<details class="ab lk"><summary><span class="lkt">📖 «{esc(c_["ko"])}»</span>{m1_}<button class="chip lec" data-golec="{k}:{j}">카드로 이동 →</button></summary><div class="lkey"><div class="ct">🔑 핵심 <small>{esc(lname(k))}</small></div>{lecparse.render_keybox(key_, ctx) if key_ else esc(c_["gist"])}</div>{("<div class=\"lkey lmem\"><div class=\"ct\">⚡ 암기</div><ul class=\"lrec\">" + rec_ + "</ul></div>") if rec_ else ""}</details>')
    a.append('<div class="acts acts2 noann"><button class="btn sm mk ok" data-mk="ok">✓ 맞음</button><button class="btn sm mk ng" data-mk="ng">✗ 틀림</button><button class="btn sm mk bm" data-mk="bm">★</button><button class="btn sm" data-fold="1">답 접기 ▲</button></div>')
    if q['other']:
        o = ''.join(f'<div class="oh">JB {v["ed"]}판 · {esc(v["sec"])} {esc(v["num"])}번 <button class="btn sm" data-jb="{v["ed"]}-{v["pg"]}">원본 {v["pg"]}쪽</button></div><div class="lines box0">{reflow.render(v["text"], True)}</div>' for v in q['other'])
        a.append(f'<details class="oth"><summary>다른 연도 칸·다른 판본에 실린 같은 문제 {len(q["other"])}건 (원문 그대로)</summary>{o}</details>')
    a.append('</div>'); h.append(''.join(a)); h.append('</article>')
    return ''.join(h)

# ---- 주석(A/M/N) 안의 인용 쪽도 이미지 대상에 포함
for q in Q:
    for x in [y if isinstance(y, str) else y[2] for y in q['A']] + q['M'] + q['N']:
        for m in re.finditer(r'data-k="([A-Z0-9]+)" data-p="(\d+)"', x): ctx['cited'].add((m.group(1), int(m.group(2))))

def bullet(kind, text):
    tested = '{jb:' in text
    cls = 'li' + (' tested' if tested else '') + (' near' if kind == 'n' else '')
    tag = '<span class="ntag">주변</span>' if (kind == 'n' and not tested) else ''
    if ' :: ' in text:
        lead, rest = text.split(' :: ', 1)
        tags = ''.join(re.findall(r'\{jb:[^}]+\}', rest)); rest = re.sub(r'\s*\{jb:[^}]+\}', '', rest)
        items = ''.join(f'<li>{lecparse.inline(x.strip(), ctx)}</li>' for x in lecparse._rebalance(lecparse.split_top(rest, ' / ')) if x.strip())
        return f'<div class="{cls}">{tag}<div class="lead">{lecparse.inline(lead + " " + tags, ctx)}</div><ol class="sub">{items}</ol></div>'
    return f'<div class="{cls}">{tag}{lecparse.inline(text, ctx)}</div>'
_DIMS = {}; _PREVI = []
def img_dims(key):
    """ux2 D10 강의 쪽 이미지의 표시 크기(폭 740 기준 높이) — 원본 쪽 이미지 머리만 읽음, 없으면 지금 docs/의 이미지"""
    if key in _DIMS: return _DIMS[key]
    k_, p_ = key.rsplit('-', 1); f = S.lec_img_path(k_, int(p_)); wh = None
    try:
        if f and os.path.exists(f): wh = Image.open(f).size
        else:
            if not _PREVI: _PREVI.append(J.prev_images(SID))
            v = _PREVI[0].get(key)
            if v: wh = Image.open(io.BytesIO(base64.b64decode(v.split(',', 1)[1]))).size
    except Exception: wh = None
    _DIMS[key] = (740, round(wh[1] * 740 / wh[0])) if wh and wh[0] else None
    return _DIMS[key]
def figgrid(kk, fl):
    """카드 그림 — ux2 D10: 1장 .one(넓게)·2장 .two(반씩)·3장↑ 격자 · img에 width·height(자리 미리 잡기)·lazy · data-n(그림 숨김 칩 '🖼 n')"""
    out = []
    for p, cap, fk in fl:
        k2 = fk or kk; ctx['cited'].add((k2, p)); lab_ = getattr(S, 'PAGE_LABEL', {}).get(k2, 'p.')
        nm = (' <i>' + esc(LECNAME.get(k2, k2).split('(')[-1].rstrip(')')) + '</i>') if fk else ''
        wh = img_dims(f'{k2}-{p}'); wa = f' width="{wh[0]}" height="{wh[1]}"' if wh else ''
        out.append(f'<figure data-fig="{k2}-{p}"><img data-img="{k2}-{p}" alt=""{wa} loading="lazy" decoding="async"><figcaption><b>{lab_}{p}</b>{nm}{(" · " + esc(cap)) if cap else ""}</figcaption></figure>')
    n = len(out); cl = ' one' if n == 1 else (' two' if n == 2 else '')
    return f'<button class="figchip noann" data-figopen="1" data-n="{n}" aria-label="그림 {n}장 보기"></button><div class="figs noann{cl}" data-n="{n}">' + ''.join(out) + '</div>'
def yl(yrs, full=False):
    """연도 라벨: 5개 초과면 앞 4개 + 나머지 수"""
    ys = ['%02d' % y for y in yrs]
    if full or len(ys) <= 5: return '·'.join(ys)
    return '·'.join(ys[:4]) + f' +{len(ys) - 4}'
def ylab(yrs):
    """연도 표기 통일(U24): '24·23·21 (3회)' — 4개 초과는 앞 4개 + '+n'"""
    if not yrs: return '연도 미상'   # 10-03 허브 점검: 연도 없는 문항 칩이 빈 버튼이던 것
    ys = ['%02d' % y for y in yrs]
    return ('·'.join(ys[:4]) + (f' +{len(ys) - 4}' if len(ys) > 4 else '')) + (f' ({len(ys)}회)' if len(ys) >= 2 else '')
def hlab(ids, yrs):
    """카드 머리·정리표 행 기출 칩 글자 — 문항이 둘 이상이면 문항 수를 앞에(10-04 사용자 '다수 문제 있는 경우엔 관련 출제문제 갯수를 써놓든 해서 … 클릭하지 않더라도 알 수 있게끔')"""
    if len(ids) < 2: return '기출 ' + ylab(yrs)
    ys = ['%02d' % y for y in yrs]
    return f'기출 <b class="hqn">{len(ids)}문항</b> · ' + (('·'.join(ys[:4]) + (f' +{len(ys) - 4}' if len(ys) > 4 else '')) if ys else '연도 미상')
def ychips(ids):
    return ''.join(f'<button class="jbchip{" rep" if len(QMAP[i]["yrs"]) >= 2 else ""}" data-go="{i}" title="{("·".join(YR(y) for y in QMAP[i]["yrs"]) + "년") if QMAP[i]["yrs"] else "연도 미상"}">{ylab(QMAP[i]["yrs"])}</button>' for i in ids if i in QMAP)
GENERIC_Q = re.compile(r'^(?:다음|중|옳은|옳지|않은|틀린|바른|것|것을|것은|고르시오|고르세요|적기|적으시오|쓰시오|설명하시오|서술하시오|설명|T/?F|문제|[\s.,?!·()~0-9])*$')
def q_gist(t):
    """ux2 D11 문제 요지 — (탈)·(짤)·(복원 원문)·(24,23,22)·'지문을 읽고 물음에 답하시오.'를 위치와 상관없이 떼고 60자 어절 경계로 · 일반 발문만 남으면 ''"""
    t = lecparse._plain(t or '')
    t = re.sub(r'\((?:탈|짤|복원 원문)[^)]*\)', ' ', t)
    t = re.sub(r'\(\s*\d{2}(?:\s*[,·~]\s*\d{0,2})*(?:\s*,\s*[탈짤])?\s*\)?', ' ', t)
    t = t.replace('지문을 읽고 물음에 답하시오.', ' ')
    t = re.sub(r'\s+', ' ', t).strip(' ,·')
    if GENERIC_Q.match(t): return ''
    if len(t) > 60: t = (t[:60].rsplit(' ', 1)[0] if ' ' in t[:60] else t[:60]).rstrip(' ,·(') + '…'
    return t
YRPAR = re.compile(r'\s*\(\s*\d{2}\s*[’′\']?(?:\s*[,·~]\s*\d{2}\s*[’′\']?)*(?:\s*[,·]\s*[탈짤])?\s*[,·]?\s*\)')
def short_clean(t):
    """문항 요약의 JB 괄호 연도 '(21,22,24)'·'(20’, 19’)'·'(24, 탈)' 떼기(어디에 있든) — 연도는 칩에 있음 · 끝의 옛 형식 괄호도"""
    t2 = YRPAR.sub('', t)
    t2 = re.sub(r'\s*\([^()]*\b\d{2}\b[^()]*\)\s*\.?\s*$', '', t2).strip()
    t2 = YRCUT.sub('', t2).strip()   # 4차 최종: 78자 자르기에 걸려 닫히지 않은 끝 괄호 연도 '(24,23' · '(2' · '(' 떼기
    return t2 or t
YRCUT = re.compile(r'\s*\(\s*(?:\d{1,2}\s*[’′\']?(?:\s*[,·~]\s*(?:\d{1,2}\s*[’′\']?|[탈짤])?)*)?\s*$')
def short_top(q):
    """4차 최종: 과목 홈 '2회 이상 출제' 줄 — 첫 줄 전체에서 괄호 연도를 먼저 떼고 78자(넘치면 …)"""
    t = short_clean(q.get('stem') or q['short']); cut = len(t) > 78
    if cut: t = t[:77].rstrip()
    i = t.rfind('(')
    if i > t.rfind(')') and len(t[:i].rstrip()) >= 12: t, cut = t[:i].rstrip(), False   # 닫히지 않은 괄호(잘림·다음 줄로 이어짐) 앞에서 끊기
    return t + ('…' if cut else '')
SUMQ_STEM = re.compile(r'다음\s*(?:설명|글|그림|표|증례)')
def sum_q(q):
    """ux2 E10 한눈표 문제 칸: 발문(번호·JB 괄호 연도 뗌) + 발문이 '다음 설명·글·그림·표·증례'이거나 목록 줄이 1개뿐이면 본문 줄을 160자까지(넘치면 '…▸'로 그 자리 펼침)"""
    qt, _ = split_qa(q); L = reflow.reflow(qt, True)
    if not L: return esc(q['short']), ''
    stem = short_clean(re.sub(r'^\s*\d{1,3}(-\d)?\s?[.)]?\s*', '', L[0]).strip()) or q['short']
    body = [x for x in L[1:] if x.strip()]
    nl = sum(1 for x in body if reflow.LISTM.match(x))
    if not body or not (SUMQ_STEM.search(stem) or nl == 1): return esc(stem[:120] + ('…' if len(stem) > 120 else '')), ''
    bt = YRPAR.sub('', ' '.join(body)).strip()
    if len(bt) <= 160: return esc(stem), f'<div class="qbody">{esc(bt)}</div>'
    cut = bt[:160].rsplit(' ', 1)[0] if ' ' in bt[:160] else bt[:160]
    return esc(stem), f'<div class="qbody">{esc(cut)}<span class="qrest">{esc(bt[len(cut):])}</span><button class="qmore noann" data-qmore="1" aria-label="본문 더 보기"></button></div>'
def mini_table(rows, cls='mini'):
    head = ''.join(f'<th>{lecparse.inline(c, ctx)}</th>' for c in rows[0])
    body = ''.join('<tr>' + ''.join((f'<th>{lecparse.inline(c, ctx)}</th>' if j == 0 else f'<td>{lecparse.inline(c, ctx)}</td>') for j, c in enumerate(r)) + '</tr>' for r in rows[1:])
    return f'<div class="tscroll"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
SYM_RE = re.compile(r'[○×✓✗△◎OX✔\-—\s]+')
DASH = ('', '—', '-', '–')
LB0, LB1, HX0, HX1 = '\ue010', '\ue011', '\ue012', '\ue013'   # lecparse.inline: 열 이름 표(.clab.noann — 표시 글자에 안 듦) · 숨김(.csx — 글자는 DOM에)
def t_items(v):
    """ux2 E03 카드 안 작은 표 → 정리표 세부 칸 항목. 값 열이 3개↑면 표 그대로(('TBL', v)) · ○/× 기호표는 ○ 열 이름만 보임('— Intrinsic ○ · Extrinsic ○' — ×·— 칸은 숨김)
    · 값 열이 2개면 칸마다 열 이름 · 1개면 그대로. 칸 글자와 ' / ' 이음은 옛 빌드와 같게 두고 열 이름은 .noann(표시 위치 불변 — E01 이관)"""
    hd = [re.sub(r'\*\*|\{r:|\}|==', '', x).strip() for x in v[0]]; nv = len(v[0]) - 1
    vals = [c.strip() for r in v[1:] for c in r[1:] if c.strip() not in DASH]
    sym = bool(vals) and all(SYM_RE.fullmatch(c) for c in vals)
    if nv >= 3: return [('TBL', v)]
    out = []
    for r in v[1:]:
        r0 = r[0].replace('**', '').strip()
        toks = ' '.join(re.findall(r'\{jb:[^}]+\}|\[\[[^\]]+\]\]', r0))   # 기출·인용 버튼은 굵게 밖으로(굵게 짝이 끊기지 않게)
        r0 = re.sub(r'\s*(\{jb:[^}]+\}|\[\[[^\]]+\]\])', '', r0).strip()
        cs = []
        for i_, x in enumerate(r):
            if not i_ or not x: continue
            h_ = hd[i_] if (i_ < len(hd) and (sym or nv >= 2)) else ''
            c = (LB0 + h_ + LB1 if h_ else '') + x
            if x.strip() in DASH or (sym and x.strip() in ('×', '✗', 'X')): c = HX0 + c + HX1
            cs.append(c)
        rest_ = ' / '.join(cs)
        out.append(('**' + r0 + '**' + (' ' + toks if toks else '') + ' — ' + rest_) if r0 else ((toks + ' ' if toks else '') + rest_))
    return out
def red_terms(x, kc):
    """ux2 E02 요약 줄 — 항목(또는 작은 표)의 {r:} 중 카드 시험 핵심(.k, .k2 아님)만"""
    txt = ' '.join(c for r in x[1] for c in r) if isinstance(x, tuple) else x
    return [m.strip() for m in re.findall(r'\{r:([^{}]+)\}', txt) if m.strip() and kc(m) == 'k']
def mkey_html(key):
    """정리표 🔑: 라벨을 첫 줄(앞머리·첫 항목) 안에 인라인으로 — '🔑' 혼자 한 줄에 서지 않게"""
    r = lecparse.key_lines(key, ctx); lb = '<b class="mkl">🔑</b> '   # ux3 N3 — 🔑 상자와 같은 줄 나누기(key_lines)
    m = re.match(r'^(<div class="klead">|<div class="kl(?: klh)?">|<(?:ul|ol) class="[^"]*"><li(?: class="[^"]*")?>)', r)
    return (r[:m.end()] + lb + r[m.end():]) if m else lb + r
def pg_label(k, rng, npages):
    """ux2 D08 카드 쪽 범위 — '1-3·12'·'17-18,23' 여러 조각도 'p.1–3·12'로. 100 넘는 조각은 별도 파일(ALT_KEY 강의거나 강의 쪽수보다 클 때), 0은 필기본
    → (표시, 첫 조각 시작 쪽 | None)"""
    pl_ = getattr(S, 'PAGE_LABEL', {}).get(k, 'p.'); nums, spec, first = [], [], None
    for sg in [x.strip() for x in re.split(r'[,·]', rng or '') if x.strip()]:
        m = re.fullmatch(r'(\d+)(?:\s*[-–~]\s*(\d+))?', sg)
        if not m: continue
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if first is None: first = a
        if a > 100 and (k in getattr(S, 'ALT_KEY', {}) or a > (npages or 0)):
            if '별도 파일' not in spec: spec.append('별도 파일')
        elif a == 0:
            if '필기본' not in spec: spec.append('필기본')
        else: nums.append(str(a) if a == b else f'{a}–{b}')
    return ' · '.join(([pl_ + '·'.join(nums)] if nums else []) + spec), first
def fchash(t):
    """허브 fcHash와 같은 값(djb2 · UTF-16 단위 · 36진) — ⚡ 줄 → 플래시카드 기록 키 R:<강의>:<해시>"""
    h = 5381; b = t.encode('utf-16-le')
    for i in range(0, len(b), 2): h = (h * 33 + (b[i] | (b[i + 1] << 8))) & 0xFFFFFFFF
    d = '0123456789abcdefghijklmnopqrstuvwxyz'; o = ''
    while True:
        h, r = divmod(h, 36); o = d[r] + o
        if not h: return o
def txt_of(h_): return html.unescape(re.sub(r'<[^>]+>', '', h_))
def fcnorm(t): return re.sub(r'[\s/·•,;:|]+', '', t)
FCPREV = {}
try:
    _pp = J._load_js(os.path.join(J.DOCS, 'packs', SID + '.js'))
    for _L in _pp.get('lect', []):
        for _r in _L.get('recall') or []:
            _tc = txt_of(_r['h']); _k = 'R:' + _L['k'] + ':' + fchash(_r['t'] + '|' + _tc)
            FCPREV.setdefault((_L['k'], fcnorm(_r['t'] + '|' + _tc)), []).extend([_k] + list(_r.get('ok') or []))
except Exception as _e: print('FCPREV 없음', _e)
EXN = [0, 0]
def lec_card(L, j, c):
    k = L['k']; ids = [x for x in c['jb'] if x in QMAP]; mx = max([len(QMAP[x]['yrs']) for x in ids] or [0])
    ctx['RED'] = lecparse.red_set([v for t_, v in c['body'] if t_ == 'K'] + [v[1] for t_, v in c['body'] if t_ == 'E'] + list(c['recall']))   # ux2 D06 카드의 시험 핵심 빨강
    lab, first = pg_label(k, c['rng'], L.get('pages'))
    kk = getattr(S, 'ALT_KEY', {}).get(k, k) if (first is not None and first > 100 and k in getattr(S, 'ALT_KEY', {})) else k
    ys = sorted({y for x in ids for y in QMAP[x]['yrs']}, reverse=True)
    eids = [x for t_, v in c['body'] if t_ == 'E' for x in v[0] if x in QMAP]; allq = list(dict.fromkeys(ids + eids))
    dn = min(3, max([len(QMAP[x]['yrs']) for x in allq] or [0]))   # ux2 D02 data-n = 최대 출제 횟수(3 = 3회 이상)
    hq = allq; hys = sorted({y for x in hq for y in QMAP[x]['yrs']}, reverse=True); hmx = max([len(QMAP[x]['yrs']) for x in hq] or [0])   # 10-03 허브 점검: 머리 칩 = 연결 문항 ∪ 이 카드 ⭐의 문항(⭐ 개수·미리보기와 같은 묶음)
    ych = f'<button class="chip yr n{min(hmx,3)}" data-go="{hq[0]}"{(" data-gos=" + chr(34) + " ".join(hq) + chr(34)) if len(hq) > 1 else ""} title="{(str(len(hq)) + "문항 · ") if len(hq) > 1 else ""}{"·".join(YR(y) for y in hys) or "연도 미상"} — 누르면 JB 미리보기{"(한꺼번에)" if len(hq) > 1 else ""}">{hlab(hq, hys)}</button>' if hq else ''
    nex = sum(1 for t_, _ in c['body'] if t_ == 'E')
    exj = f'<button class="chip exj noann" data-exjump="1" aria-label="이 카드의 ⭐ 시험포인트로">⭐ {len(allq) or nex} ↓</button>' if nex else ''   # ux2 D05
    prof = any(b[0] == 'P' for b in c['body'])
    tg = ' · '.join(x for x in c['tag'].split(' · ') if not x.strip().startswith('기출'))
    tagc = f'<span class="chip tagc">{esc(tg)}</span>' if tg else ''
    h = [f'<article class="tc {heat(mx)} open" id="t-{k}-{j}" data-n="{dn}" data-grp="{esc(c["grp"])}" data-aid="{AIDS[(k, j)]}" data-alt="{card_alt(k, j)}"><div class="thead"><span class="badge" data-ttog>{j+1}</span><div class="tt" data-aid="{AIDS[(k, j)]}~h"><div class="en serif" data-ttog>{esc(c["en"])}</div><div class="ko">{esc(c["ko"])}{(" <span class=" + chr(34) + "pg" + chr(34) + ">· " + lab + "</span>") if lab else ""}</div><div class="one">{lecparse.gist_html(c["gist"], ctx)}</div><div class="tchips">{tagc}{ych}{exj}{"<span class=\'chip emc\'>💬 교수 강조</span>" if prof else ""}</div></div><button class="dn noann" data-done="1" title="이해함 표시">✓</button><button class="car noann" data-ttog title="접기/펼치기" aria-label="접기/펼치기">▶</button></div><div class="tbody">']
    blocks = []; curb = None; key = ''; exams = []; exbuf = []; prevb = None
    def exhtml(v):
        r_ = lecparse.render_exam(v, ctx)
        return r_
    def flush_ex():
        if not exbuf: return
        if len(exbuf) == 1:
            v = exbuf[0]; r_ = exhtml(v[1])
            h.append(f'<div class="co c-exam"><div class="ct">⭐ 시험포인트 <span class="ey">{ychips(v[0])}</span></div>{("<div class=" + chr(34) + "kb kbx" + chr(34) + ">" + r_ + "</div>") if r_ else lecparse.render_key(v[1], ctx)}</div>')
        else:
            def exli(v):
                r_ = exhtml(v[1])
                return f'<li class="exrow"><span class="ey">{ychips(v[0])}</span> {r_}</li>' if r_ else f'<li><span class="ey">{ychips(v[0])}</span> {lecparse.render_block(v[1], ctx) if len(v[1]) > 150 else lecparse.inline(v[1], ctx)}</li>'
            h.append('<div class="co c-exam"><div class="ct">⭐ 시험포인트 <small>이 카드에서 나온 문제 ' + str(len(exbuf)) + '개</small></div><ul class="exlist">' + ''.join(exli(v) for v in exbuf) + '</ul></div>')
        exbuf.clear()
    for t, v in c['body']:
        if t != 'E': flush_ex()
        if t not in ('b', 'b2'): prevb = None
        if t == 'K':
            ks = lecparse.key_split(v)
            if len(v) > 180: KEYLONG[k] = KEYLONG.get(k, 0) + 1
            if ks:   # 🔑이 길면 첫 조각만 상자에 — 나머지는 상자 밖 본문·정리표 세부 칸으로
                key = ks[0]; h.append(f'<div class="co c-key"><div class="ct">🔑 핵심</div>{lecparse.render_keybox(ks[0], ctx)}</div>' + lecparse.render_key_rest(ks[1], ctx))
                curb = {'h': '', 'items': list(ks[1])}; blocks.append(curb)
            else: key = v; h.append(f'<div class="co c-key"><div class="ct">🔑 핵심</div>{lecparse.render_keybox(v, ctx)}</div>')
        elif t == 'h': h.append(f'<h4 class="sh">{lecparse.inline(v, ctx)}</h4>'); curb = {'h': v, 'items': []}; blocks.append(curb)
        elif t == 'b':
            st_ = None; C_ = lecparse.CIRC; v0 = v.lstrip()[:1]
            if prevb is not None and v0 and v0 in C_ and h and h[-1].startswith('<div class="li nolead'):   # ux2 D09 앞 줄이 ⑤로 끝나고 이 줄이 ⑥으로 시작 → 한 목록처럼(ol start=6) — fixB N1: 앞 줄이 실제로 번호 목록(ol)으로 그려졌을 때만(① ② 한 줄씩 쓴 나열은 끝까지 같은 모양)
                lc = [ch for ch in prevb if ch in C_]
                if lc and C_.index(v0) == C_.index(lc[-1]) + 1 and C_.index(lc[-1]) >= 1: st_ = C_.index(v0) + 1
            h.append(lecparse.render_item(v, ctx, cont=st_)); prevb = v
            if curb is None: curb = {'h': '', 'items': []}; blocks.append(curb)
            curb['items'].append(v)
        elif t == 'b2':   # 10-05 하위 항목(원고 '  - ') — 바로 위 항목 아래 들여 쓴 줄
            h.append(re.sub(r'^<div class="li', '<div class="li l2', lecparse.render_item(v, ctx), count=1))
            if curb is None: curb = {'h': '', 'items': []}; blocks.append(curb)
            curb['items'].append(v)
        elif t == 'T':
            h.append(mini_table(v))
            if curb is None: curb = {'h': '', 'items': []}; blocks.append(curb)
            curb['items'] += t_items(v)
        elif t == 'F': h.append(figgrid(kk, v))
        elif t == 'E':
            exams.append(v); exbuf.append(v)
        elif t == 'P': h.append(f'<div class="co c-prof"><div class="ct">💬 교수님 강조</div>{lecparse.render_key(v, ctx)}</div>')
        elif t == 'U': h.append(f'<div class="und"><span class="ui">✍ 이해</span>{lecparse.render_block(v, ctx) if (len(v) > 150 or lecparse._facts(lecparse.split_top(v, " / "))) else lecparse.inline(v, ctx)}</div>')
    flush_ex()
    if c['recall']:   # 안내문은 강의의 첫 ⚡ 블록에만(U27 — 카드마다 반복하지 않음)
        tip = '' if MEMTIP.get(k) else ' <small>빨간 글씨를 자동 빈칸으로 가리고 떠올리기</small>'; MEMTIP[k] = 1
        def mli(x):   # ux2 D03 ⚡ 줄마다 플래시카드와 같은 키(data-fk — 복습 정렬·플래시카드 기록 호환) · ux4 B1-5 줄 끝 ○✕는 없앰(카드 단위 알아요/몰라요·플래시카드는 그대로)
            r_ = lecparse.render_recall(x, ctx); fk = 'R:' + k + ':' + fchash(c['en'] + '|' + txt_of(r_))
            nli = r_.count('<li>')   # ux2 fixB flow V08(B안): ' / '로 나뉜 한 줄 = 한 판정(키 하나) — 여러 li를 한 묶음(.mg)으로 보이고 ○✕는 끝 줄에 하나
            if nli > 1:
                parts = r_.split('<li>'); r_ = parts[0] + ''.join(f'<li data-fk="{fk}" class="mg{" mg0" if j == 0 else (" mgz" if j == nli - 1 else "")}">' + t for j, t in enumerate(parts[1:]))
            else:
                r_ = r_.replace('<li>', f'<li data-fk="{fk}">')
            return r_
        h.append(f'<div class="co c-mem"><div class="ct">⚡ 암기{tip}<button class="memqz noann" data-memqz="1" aria-label="가리기"></button></div><ul>{"".join(mli(x) for x in c["recall"])}</ul></div>')
    h.append('<div class="rvj noann"><button data-rv="o" aria-label="알아요"></button><button data-rv="x" aria-label="몰라요"></button></div></div></article>')
    thumb = ''
    if c['figs']:
        tp, tk = c['figs'][0]; tk = tk or kk
        thumb = f'<figure class="mth" data-fig="{tk}-{tp}"><img data-img="{tk}-{tp}" alt=""></figure>'
    # (옛 빌드 글자 '미출제'·머리 라벨은 .tho(숨김)로 같은 자리에 남김 — 옛 표시 위치 불변, 보이는 새 라벨은 .noann)
    # ---- 정리표 행(ux2 E01~E06): 주제(제목·연도 칩·미출제) · 🔑 요지·핵심 · 세부(요약 줄 .sline(noann) + 전체 .mfull) · ★ 시험(문항마다 연도 칩 + 문제 → 답) · ⚡ 암기
    kc = lecparse._kcls(ctx['RED'])
    def ci_html(x):
        if isinstance(x, tuple): return f'<div class="ci cit">{mini_table(x[1], "mini sm")}</div>'
        n_ = len(re.sub('\ue010[^\ue011]*\ue011|[\ue012\ue013]', '', x))   # 열 이름 표는 길이에서 뺌(옛 빌드와 같은 렌더 — 표시 위치 불변)
        return f'<div class="ci">{lecparse.render_block(x, ctx) if n_ > 110 else lecparse.inline(x, ctx)}</div>'
    more2 = lambda bk: f'<button class="link more2 noann" data-scroll2="{k}:{j}">+{len(bk["items"]) - 6} 더 보기(카드로)</button>' if len(bk['items']) > 6 else ''
    bks = [bk for bk in blocks if bk['items']]; nit = sum(len(bk['items']) for bk in bks)
    det = ''.join(f'<div class="mblk">{("<b>" + lecparse.inline(bk["h"], ctx) + "</b>") if bk["h"] else ""}{"".join(ci_html(x) for x in bk["items"][:6])}{more2(bk)}</div>' for bk in bks)
    sl, used, cut = [], 0, 0
    for bk in bks:   # 요약 줄 = 소제목마다 '소제목: 시험 핵심어·수치' (블록 4개·300자까지, 핵심어가 없으면 첫 항목 앞 50자)
        ts = list(dict.fromkeys(t_ for x in bk['items'] if not isinstance(x, tuple) for t_ in red_terms(x, kc))) or list(dict.fromkeys(t_ for x in bk['items'] if isinstance(x, tuple) for t_ in red_terms(x, kc)))   # 10-05 소제목 아래 표가 다른 소제목 행까지 담으면(Indications 행이 든 표가 Contraindications 아래) 요약 줄이 섞이던 것 — 줄 항목의 핵심어 먼저, 없을 때만 표
        if ts: body = '·'.join('{r:' + t_ + '}' for t_ in ts)
        else:
            f0 = next((x for x in bk['items'] if not isinstance(x, tuple)), '')
            f0 = re.sub(r'\s+', ' ', lecparse._plain(re.sub(r'\[\[[^\]]*\]\]|\ue010[^\ue011]*\ue011|[\ue012\ue013]', '', f0))).strip()
            f1 = f0[:50]
            if len(f0) > 50 and ' ' in f1.strip(): f1 = f1.rsplit(' ', 1)[0].rstrip(' ·,;:—-(')   # ux2 fixB VIS03 낱말 경계에서 자름(bra… → 낱말 끝 …)
            body = (f1 + ('…' if len(f0) > len(f1) else '')).replace('{', '(').replace('}', ')') if f0 else ''
        hh = lecparse._plain(bk['h'] or '')
        ln = len(hh) + len(lecparse._plain(body))
        if len(sl) >= 4 or (sl and used + ln > 300): cut += 1; continue
        used += ln; sl.append(f'<div class="sl">{("<b>" + lecparse.inline(bk["h"], ctx) + "</b>" + (": " if body else "")) if bk["h"] else ""}{lecparse.inline(body, ctx) if body else ""}</div>')
    dbtn = (f'<button class="mdmore noann" data-mdmore="1"><span class="l1">{("+" + str(cut) + "줄") if cut else "세부"} ▸</span><span class="l2">세부 {nit}줄 ▸</span><span class="l3">접기 ▴</span></button>') if det else ''
    sav = list(lecparse.EXAM_N)
    def mex(e):
        ch = ychips(e[0]); r_ = lecparse.render_exam(e[1], ctx)
        if not r_:
            m = re.match(r'^(\d{2}(?:\s*[·,~]\s*\d{2})*년(?:\s*이전)?(?:\s*\d+회)?\s*)', e[1])
            r_ = (f'<span class="ex-yr">{esc(m.group(1))}</span>' + lecparse.inline(e[1][m.end():], ctx)) if (m and ch) else lecparse.inline(e[1], ctx)
        return f'<div class="mex"><div class="mexb"><span class="mexi">{ch}{r_}</span></div></div>'
    ex = ''.join(mex(e) for e in exams); lecparse.EXAM_N[:] = sav
    if len(exams) > 3:   # 요약에서는 3문항까지 — 나머지는 '+n문항 ▸'(전체 모드·표시가 든 문항은 늘 보임)
        ex = ex.replace('<div class="mex">', '<div class="mex mexx">'); ex = ex.replace('<div class="mex mexx">', '<div class="mex">', 3) + f'<button class="mexmore noann" data-mexmore="1"><span class="l1">+{len(exams) - 3}문항 ▸</span><span class="l3">접기 ▴</span></button>'
    mem = ''.join(f'<div class="ci">{lecparse.inline(x, ctx)}</div>' for x in c['recall']) or '<span class="small">—</span>'
    ralt = ' '.join(x + '~s' for x in card_alt(k, j).split(' '))   # ux2 E01 정리표 행 = 표시 단위(카드 aid~s) · 옛 카드 aid도 ~s로 이어받음
    ych2 = f'<button class="chip yr n{min(dn,3)}" data-go="{allq[0]}"{(" data-gos=" + chr(34) + " ".join(allq) + chr(34)) if len(allq) > 1 else ""} title="{"·".join(YR(y) for y in sorted({y for x in allq for y in QMAP[x]["yrs"]}, reverse=True))} — 누르면 JB 문제로">{hlab(allq, sorted({y for x in allq for y in QMAP[x]["yrs"]}, reverse=True))}</button>' if allq else '<span class="m0">미출제</span>'
    exc = f'<td class="mt" data-col="ex" data-h="★ 시험">{ex}</td><td class="mnote" data-col="mem" data-h="⚡ 암기">{mem}</td>' if exams else f'<td class="mnote mw" colspan="2" data-col="mem" data-h="⚡ 암기"><span class="tho">미출제</span>{mem}</td>'
    row = (f'<tr class="{heat(dn)}" id="m-{k}-{j}" data-aid="{AIDS[(k, j)]}~s" data-alt="{ralt}" data-grp="{esc(c["grp"])}" data-n="{dn}"><th data-col="topic"><div class="mtw"><button class="link" data-scroll2="{k}:{j}"><span class="mn">{j+1}</span> <span class="serif men" lang="en">{esc(c["en"])}</span></button><div class="mko">{lecparse._wbr(esc(c["ko"]))}{(" <span class=" + chr(34) + "pg" + chr(34) + ">· " + lab + "</span>") if lab else ""}</div><div class="mych noann">{ych2}</div>{thumb}</div></th>'
           f'<td class="mk" data-col="key" data-h="🔑 요지·핵심"><div class="mg">{lecparse.gist_html(c["gist"], ctx)}</div>{("<div class=mkey>" + mkey_html(key) + "</div>") if key else ""}</td><td class="md" data-col="det" data-h="세부">{("<div class=" + chr(34) + "sline noann" + chr(34) + ">" + "".join(sl) + "</div>") if sl else ""}<div class="mfull">{det}</div>{dbtn}</td>{exc}</tr>')
    ctx['RED'] = None
    return ''.join(h), mx, ids, lab, row

profS = {}
for q in Q:
    if q['tier'] == 'C' or not q.get('st') or not (q['prof'] or '').strip(): continue
    profS.setdefault((q['prof'] or '').split('(')[0], []).append(q)
# 교수별 요약(U21): 한 줄 요약 · 📌 전략(여러 교수에 공통인 항목은 '공통:'으로 한 번만, 교수별로는 다른 부분만) · 연도별 칸은 접힘
PSM = {p_: trend.summarize(qs) for p_, qs in profS.items()}
PPARTS = {p_: trend.tendency_parts(PSM[p_], p_, MENT_PROF.get(p_, '')) for p_ in profS}
# 최근 2개 시험 해에 한 문항도 없는 교수(예전 담당)는 요약·전략에서 빼고 세부(접힘)에만
_ymax = max((y for q in Q for y in q['yrs']), default=0)
PCUR = [p_ for p_ in profS if max((y for q in profS[p_] for y in q['yrs']), default=0) >= _ymax - 1] or list(profS)
POLD = [p_ for p_ in profS if p_ not in PCUR]
_sl = [PPARTS[p_][1] for p_ in PCUR]
SCOMMON = [x for x in _sl[0] if all(x in l_ for l_ in _sl[1:])] if len(_sl) >= 2 else []
PSTRAT = {p_: ' · '.join(PPARTS[p_][1]) for p_ in profS}   # 강의 틀의 📌 한 줄(그 강의 교수 것 전체)
def strat_tag(x):
    """전략 항목 → 교수 줄의 짧은 꼬리표(형식·탈 성격) — 판정(완짤형 등)은 요약 줄에 이미 있음"""
    if x.startswith('기출이 걸린 카드'): return '탈=변형'
    if x.startswith('아직 안 나온 카드'): return '탈=새 영역'
    if x.startswith('💬'): return '💬 강조 카드'
    m = re.match(r'^(서술형|객관식|빈칸|T/F|단답형):', x)
    return m.group(1) if m else ''
prow = ''; psum = ''; trow = ''; SUSE = {}
for p_, qs in profS.items():
    SM = PSM[p_]; t_ = ' / '.join(PPARTS[p_][0])
    lecs = sorted({lname(q['lk']) for q in qs if q['lk']})
    note = S.PROF_NOTE.get(p_, '')
    prow += f'<tr><th>{esc(p_)}<div class="small">{esc(" · ".join(lecs))}{("<br>" + esc(note)) if note else ""}</div></th><td><div class="yrow">{trend.years_html(SM)}</div></td><td><div class="tlines">{"".join(f"<div>{x}</div>" for x in t_.split(" / "))}</div></td></tr>'
    if p_ not in PCUR: continue
    tags = [t for t in (strat_tag(x) for x in PPARTS[p_][1] if x not in SCOMMON) if t]
    for x in PPARTS[p_][1]:
        if x not in SCOMMON: SUSE.setdefault(x, []).append(p_)
    psum += f'<li title="{esc(t_)}"><span class="tsl">{esc(trend.prof_line(p_, SM))}</span>{(" <span class=tk>· " + esc(" · ".join(tags)) + "</span>") if tags else ""}</li>'
    # ux4 B3-3 경향 표 한 행(교수 | 최근 해 | 짤/탈 | 유형 | 짤 비율 | 탈의 성격·형식) — 탈 성격은 전략 항목 전체에서(공통 항목 포함), 형식은 최근 해 최다
    _nat = [t.replace('탈=', '') for t in dict.fromkeys(strat_tag(x) for x in PPARTS[p_][1]) if t and t not in ('서술형', '객관식', '빈칸', 'T/F', '단답형')]
    _pc = trend.prof_cells(SM); _fm = max(_pc[4].split(' · '), key=lambda z: int(z.rsplit(' ', 1)[-1]) if z.rsplit(' ', 1)[-1].isdigit() else 0).rsplit(' ', 1)[0] if _pc[4] and _pc[4] != '—' else ''
    trow += f'<tr class="tsl" title="{esc(trend.prof_line(p_, SM))}"><th>{esc(p_)}</th><td class="n">{_pc[0]}</td><td class="n">{_pc[1]}</td><td>{_pc[2]}</td><td class="n">{_pc[3]}</td><td>{esc(" · ".join(_nat + ([_fm] if _fm else [])))}</td></tr>'
    if getattr(S, 'TREND_NOTE', {}).get(p_): trow += f'<tr class="tnote"><td colspan="6"><small>※ {esc(S.TREND_NOTE[p_])}</small></td></tr>'   # ux4f 맥 인계 10-03 — 강의 연결만으로 그 교수에 들어간 문항 등 집계 주석(subject.py PROF_NOTE)
# 📌 전략: 모든 교수에 공통인 항목은 '공통:' 한 줄, 나머지 항목도 문장은 한 번만 쓰고 해당 교수를 뒤에
def strat_list(items, top=4):
    """📌 전략 목록(V05) — 한 줄에 전략 하나(본문 글자) + 교수 꼬리표(작은 회색). 위 top개만, 나머지는 '+N 더 보기'"""
    li = lambda x, ps: f'<li><span class="sx">{x}</span>{(" <i>" + esc("·".join(ps)) + "</i>") if ps else ""}</li>'
    h = '<ul class="tsl2">' + ''.join(li(x, ps) for x, ps in items[:top]) + '</ul>'
    if len(items) > top: h += f'<details class="smore"><summary>+{len(items) - top} 더 보기</summary><ul class="tsl2">' + ''.join(li(x, ps) for x, ps in items[top:]) + '</ul></details>'
    return h
_sitems = [(x, ['공통']) for x in SCOMMON] + [(esc(x), ps) for x, ps in sorted(SUSE.items(), key=lambda kv: -len(kv[1]))]
strat_html = strat_list(_sitems) if _sitems else ''
PRATIO = [r_ for r_ in (trend.latest_ratio(PSM[p_]) for p_ in PCUR) if r_ is not None]
trends_html = (f'<section class="ptrend sh4"><h2 class="hh">교수별 출제 경향 <small>짤 = 이전 해에 한 번이라도 나온 문제 · 탈 = 그 해 처음</small></h2><div class="tscroll"><table class="ttab"><thead><tr><th>교수</th><th>최근 해</th><th>짤 / 탈</th><th>유형</th><th>짤 / 문항</th><th>탈의 성격 · 형식</th></tr></thead><tbody>{trow}</tbody></table></div>'   # ux4 B3-3 문장 목록 → 표(행 = 최근 2개 시험 해에 문항이 있는 교수)
               + (f'<div class="tstrat"><div class="tsh">📌 공부 전략</div>{strat_html}</div>' if strat_html else '')
               + f'<details class="trd"><summary>연도별 문항 수·짤/탈 세부 보기{(" · 예전 담당 " + esc("·".join(POLD))) if POLD else ""}</summary><div class="tscroll"><table class="cmp trendtbl"><thead><tr><th style="width:15%">교수</th><th style="width:40%">연도별 문항 · 짤/탈</th><th>경향</th></tr></thead><tbody>{prow}</tbody></table></div><div class="small" style="margin-top:6px">{esc(MENT_ALL)}</div></details></section>')
top = [{'id': q['id'], 'yrs': q['yrs'], 'short': short_top(q), 'prof': q['prof'], 'lk': q['lk']} for q in sorted([q for q in Q if q['tier'] != 'C' and len(q['yrs']) >= 2], key=lambda q: (-len(q['yrs']), -q['yrs'][0]))]
lect = []; KEYLONG = {}; MEMTIP = {}
def fsrc_short(f):
    """강의 틀 첫 줄(V11) — '26년도 슬라이드 · 75쪽'처럼 짧게. 파일 이름·자료 안내는 눌러서 펼침"""
    m = re.search(r'\((\d{2})년도[^,)]*,\s*(\d+)\s*쪽', f or '')
    return f'{m.group(1)}년도 강의자료 · {m.group(2)}쪽 ▸' if m else '출처 ▸'
for L in LEC:
    k = L['k']; cards = []; rows = []; grps = []; curg = None; outline = []
    for j, c in enumerate(L['cards']):
        ch, mx, ids, lab, row = lec_card(L, j, c)
        if c['grp'] != curg:
            curg = c['grp']; grps.append(curg)
            cards.append(f'<h3 class="gdiv" data-grp="{esc(curg)}"><span>{esc(curg)}</span></h3>'); outline.append(f'<div class="og">{esc(curg)}</div>')
            rows.append(f'<tr class="grow" data-grp="{esc(curg)}"><td colspan="5">{esc(curg)}</td></tr>')
        cards.append(ch); rows.append(row)
        ys = sorted({y for x in ids for y in QMAP[x]['yrs']}, reverse=True)
        outline.append(f'<button class="ol {heat(mx)}" data-scroll="t-{k}-{j}" title="{esc(c["gist"])}"><b>{j+1}</b><span class="ot">{esc(re.sub(r"\s*\((?:\d{2}[·,~\s]*)+\)\s*$", "", c["ko"]) or c["ko"])}</span><span class="og2">{lecparse.inline(c["gist"], ctx)}</span>{("<span class=oy><i>기출</i> " + ylab(ys) + "</span>") if ys else ""}</button>')
    jb_ids = sorted([q['id'] for q in Q if q['tier'] != 'C' and q['lk'] == k], key=lambda i: (-len(QMAP[i]['yrs']), -(QMAP[i]['yrs'][0] if QMAP[i]['yrs'] else 0)))
    flow = ''.join(f'<span class="fl">{lecparse.inline(x.strip(), ctx)}</span>' for x in L['map'].split('→')) if L['map'] else ''
    LQ = [q for q in Q if q['tier'] != 'C' and q['lk'] == k and q.get('st')]
    SM = trend.summarize(LQ); ttxt, tstrat = trend.tendency_text(SM, L['title'])
    tal_list = ''
    for q in sorted(LQ, key=lambda q: -q['st']['latest']['y']):
        a = q['st']['latest']
        if a['kind'] == '탈': tal_list += f'<li><button class="jbchip" data-go="{q["id"]}">{YR(a["y"])}</button> {esc(q["short"][:44])} <span class="small">— {a["tal"]}{" · 교수 강조" if a.get("emph") else ""} · {esc(q["st"]["fmt"])}</span></li>'
    pk_ = re.split(r'[(·,/]', L['prof'])[0].strip()
    strat_ = PSTRAT.get(pk_) or tstrat
    trend_html = (f'<details class="trend"><summary><b>출제 경향</b> <span class="tsl">{esc(trend.short_line(SM))}</span></summary><div class="small tnote">JB 자료에서 산출 — 짤 = 이전 해에 한 번이라도 나온 문제, 탈 = 그 해 처음</div><div class="yrow">{trend.years_html(SM)}</div><div class="ttxt tlines">{"".join(f"<div>{x}</div>" for x in ttxt.split(" / "))}</div>{("<details class=tald><summary>탈 문항 목록 — 어디서 새로 냈나</summary><ul>" + tal_list + "</ul></details>") if tal_list else ""}'
                  + (f'<div class="small">이 강의 기출만으로 본 전략: {tstrat}</div>' if strat_ != tstrat else '') + f'</details><div class="tstr"><div class="tsh">📌 공부 전략{(" (" + esc(pk_) + ")") if strat_ != tstrat else ""}</div>{strat_list([(x.strip(), []) for x in strat_.split(" · ") if x.strip()], 3)}</div>')
    top_ids = sorted(jb_ids, key=lambda i: (QMAP[i]['tier'] != 'A', -len(QMAP[i]['yrs']), -(QMAP[i]['yrs'][0] if QMAP[i]['yrs'] else 0)))[:8]
    def ltop_li(n_, i):   # ux2 D11 '연결 카드 국문 제목 — 문제 요지' · 줄 = 그 카드로(data-cj) · 연도 칩 = JB
        cj = next((j_ for j_, c_ in enumerate(L['cards']) if Q2CARD.get(i) == (k, j_)), None)
        if cj is None: cj = next((j_ for j_, c_ in enumerate(L['cards']) if i in c_['jb'] or any(b_[0] == 'E' and i in b_[1][0] for b_ in c_['body'])), None)
        et = None
        if cj is not None:
            et = next((lecparse.exam_q(b_[1][1]) for b_ in L['cards'][cj]['body'] if b_[0] == 'E' and i in b_[1][0]), None)
        g = q_gist(et or QMAP[i]['short'])
        if not g and not et: g = q_gist(short_clean(QMAP[i]['short']))
        ti = (re.sub(r'\s*\((?:\d{2}[·,~\s]*)+\)\s*$', '', L['cards'][cj]['ko']) or L['cards'][cj]['ko']) if cj is not None else ''
        body = (f'<b>{esc(ti)}</b>' + (f' — {esc(g)}' if g else '')) if ti else esc(g or short_clean(QMAP[i]['short']))
        return f'<li{" class=tmore" if n_ >= 5 else ""}{(" data-cj=" + chr(34) + str(cj) + chr(34)) if cj is not None else ""}>{ychips([i])} <span class="tq">{body}</span></li>'
    ltop = ''.join(ltop_li(n_, i) for n_, i in enumerate(top_ids))
    NH = [x for n in L['notes'] for x in split_note(n) if HINT_RE.search(x)]; NO = [x for n in L['notes'] for x in split_note(n) if not HINT_RE.search(x)]
    hint_html = f'<div class="co c-prof fhint"><div class="ct">📣 교수님 예고·강조</div>{"".join(f"<div class=fh>{lecparse.inline(x, ctx)}</div>" for x in NH)}</div>' if NH else ''
    gp = '<div class="pills noann" id="grppills"><button class="tg on" data-grp="">전체</button>' + ''.join(f'<button class="tg" data-grp="{esc(g)}">{esc(g)}</button>' for g in grps) + '<span class="sp"></span><span class="rvsort" title="복습 보기 정렬"><button class="tg on" data-rvs="">강의 순</button><button class="tg" data-rvs="n">기출 많은 순</button><button class="tg" data-rvs="x">몰라요·✓ 안 한 것 먼저</button></span><span class="rvleg">카드 [알아요○][몰라요✕] → ‘몰라요·✓ 안 한 것 먼저’ 정렬 · ✓ = 다 봄 · 🔁 오늘 복습은 JB 채점 기준</span><button class="tg" data-filt="unread" title="✓ 다 봄 표시한 카드 숨기기">안 본 카드만</button><button class="tg" data-filt="jb" title="⭐ 기출이 걸린 카드만">⭐ 기출 카드만</button><button class="tg" data-filt="rep2" title="2회 이상 나온 기출이 걸린 카드만">2회↑만</button><button class="tg" data-filt="mine" title="내 형광펜·빈칸이 있는 카드만">내 표시만</button><details class="pmore"><summary class="tg" title="보기 설정 — ✓하면 접기 · 압축 보기 · 모두 펼치기/접기">⋯</summary><div class="pmenu"><button class="tg" id="lautofold" title="✓(이해함)을 누르면 그 카드를 접고 다음 카드로">✓하면 접기</button><button class="tg" id="lcond" title="🔑 핵심·⭐ 시험포인트·⚡ 암기 줄만 남김">압축 보기</button><button class="tg" id="lexfirst" title="⭐ 시험포인트를 🔑 핵심 바로 뒤에 (모든 강의)">⭐ 먼저</button><div class="pseg" title="빨간 글씨 — 시험 핵심만(🔑·⭐·⚡에도 나오는 것) · 전부"><b>빨강</b><button class="tg" data-redm="core">시험 핵심만</button><button class="tg" data-redm="all">전부</button></div><div class="pseg" title="카드 그림 (I로 바꾸기)"><b>그림</b><button class="tg" data-figm="big">크게</button><button class="tg" data-figm="small">작게</button><button class="tg" data-figm="hide">숨김</button></div><button class="btn sm" id="lopen">모두 펼치기</button><button class="btn sm" id="lclose">모두 접기</button><span class="fsz" title="글자 크기(모든 과목·화면 공통)"><button class="btn sm" id="fsdn" title="글자 작게">A−</button><b id="fsv">100%</b><button class="btn sm" id="fsup" title="글자 크게">A+</button></span></div></details></div>'
    head = (f'<section class="frame" data-aid="{aid(k + ":frame")}" data-k="{k}"><div class="frt">이 강의의 틀<button class="frtog noann" data-frtog="1" title="이 강의의 틀 접기/펼치기 (강의마다 기억)"></button></div><div class="fsrc" data-fsrc="1" title="눌러서 출처 전체 보기"><span class="fs0">{fsrc_short(L["file"])}</span><span class="fs1"> — 출처 {esc(L["file"])}{"".join(f" · {lecparse.inline(x, ctx)}" for x in NO)}</span></div>{("<div class=flow>" + flow + "</div>") if flow else ""}{hint_html}{trend_html}<div class="fcols"><div class="outline noann">{"".join(outline)}</div>'
            f'<div class="ftop"><div class="ct">⭐ 많이 나온 순{(" <button class=\'btn sm tmorebtn noann\' data-tmore=1>더 보기 (+" + str(len(top_ids) - 5) + ")</button>") if len(top_ids) > 5 else ""}</div><ol>{ltop}</ol></div></div></section>{gp}')
    mgp = ''.join(f'<button class="tg" data-mgrp="{esc(g)}" title="{esc(g)}">{esc(g)}</button>' for g in grps)
    summ = (f'<div class="pills noann msbar" id="msbar"><span class="pseg"><span class="pglab">보기</span><button class="tg" data-mdense="s" title="세부를 소제목마다 한 줄(시험 핵심어)로">요약</button><button class="tg" data-mdense="f" title="세부 내용 전부">자세히</button></span>'
            f'<span class="pseg"><span class="pglab">주제</span><button class="tg" data-mfilt="">모든 주제</button><button class="tg" data-mfilt="hit" title="기출이 나온 주제만">기출 나온 주제</button><button class="tg" data-mfilt="rep2" title="2회 이상 나온 기출이 걸린 주제만">2회↑만</button></span>'
            f'<span class="pseg mgrp"><button class="tg on" data-mgrp="">모든 묶음</button>{mgp}</span><span class="small mshelp">주제를 누르면 학습 카드로 · 연도 칩은 기출 문제로 · <span class="mshw">열 머리 👁 = 그 열 가리고 떠올리기</span><span class="mshn">칸 이름(🔑 요지·★ 시험·⚡ 암기…)의 👁를 누르면 그 칸을 모든 주제에서 가리기</span> · J/K 다음/이전 행</span></div>'
            f'<div class="tblwrap wide msum" data-aid="{aid(k + ":sumt")}" data-alt="{aid(k + ":sum")}"><div class="tscroll"><table class="mtx"><colgroup><col class="c1"><col class="c2"><col class="c3"><col class="c4"><col class="c5"></colgroup><thead><tr><th data-col="topic">주제</th>{"".join(f'<th data-col="{c_}"><span class="thn noann">{n_}</span><span class="tho">{o_}</span></th>' for c_, n_, o_ in (("key", "🔑 요지·핵심", "한 줄 요지 · 🔑 핵심"), ("det", "세부", "세부 내용"), ("ex", "★ 시험", "⭐ 기출 — 이렇게 나왔다"), ("mem", "⚡ 암기", "⚡ 암기 줄")))}</tr></thead><tbody>{"".join(rows)}</tbody></table></div></div>')
    mxl = max([len(QMAP[i]['yrs']) for i in jb_ids] or [0])
    recall = [{'t': c['en'], 'h': lecparse.render_recall(x, ctx)} for c in L['cards'] for x in c['recall']]   # 플래시카드: ' / ' 줄은 <li>로(U28)
    for r_ in recall:   # 10-04 ⚡ 줄 구분 기호(/ ·)·띄어쓰기만 바뀌어도 플래시카드 기록(알아요·몰라요)이 이어지게 — 지난 팩의 같은 줄(기호·공백 뺀 글자가 같음) 키를 ok로 넘김(허브가 옮김)
        tc_ = txt_of(r_['h']); nk_ = 'R:' + L['k'] + ':' + fchash(r_['t'] + '|' + tc_); old_ = FCPREV.get((L['k'], fcnorm(r_['t'] + '|' + tc_)), [])
        ok_ = [o for o in dict.fromkeys(old_) if o != nk_]
        if ok_: r_['ok'] = ok_[:6]
    lcards = [[AIDS[(k, j_)], j_ + 1, c_['ko'], len({x for x in c_['jb'] if x in QMAP} | {x for b_ in c_['body'] if b_[0] == 'E' for x in b_[1][0] if x in QMAP})] for j_, c_ in enumerate(L['cards'])]   # 미니바·사이드바 카드 목록 [aid, 번호, 국문 제목, 기출 수]
    lect.append({'k': k, 'title': L['title'], 'cards': lcards, 'prof': L['prof'], 'yr': L['yr'], 'file': L['file'], 'nsec': len(L['cards']), 'aids': [[AIDS[(k, j_)]] + card_alt(k, j_).split(' ') for j_, c_ in enumerate(L['cards'])], 'heat': heat(mxl), 'hot': mxl >= 3, 'head': head, 'learn': ''.join(cards), 'sum': summ,
                 'oldTitles': {o['aid']: ' · '.join(x for x in (o.get('en', ''), o.get('ko', '')) if x) for o in LOCK.get(k, []) if o.get('aid') and o['aid'] not in {AIDS[(k, j_)] for j_ in range(len(L['cards']))}},
                 'jb': jb_ids, 'pred': [i for i, p in enumerate(PRED) if p['k'] == k], 'tbl': [], 'recall': recall, 'tline': trend.short_line(SM), 'tstrat': tstrat, 'tip': ' · '.join(L.get('tip') or []), 'hint': cut_hint(' '.join(x for n in L['notes'] for x in split_note(n) if HINT_RE.search(x)))})

print('⭐ 시험포인트 구조화(ux2 D04):', f'{lecparse.EXAM_N[0]}/{lecparse.EXAM_N[1]}줄')
print('🔑 줄 나누기(ux3 N1 key_lines):', f'상자·칸 {lecparse.KL[0]} · 새 구조 {lecparse.KL[1]} · 글자가 달라 옛 렌더로 되돌림 {lecparse.KL[2]}')
if lecparse.KL[2]: print('  ⚠ key_lines 되돌림이 있음 — tools/check_lec.py로 확인')
print('요지 → 흐름(ux3 fix flow V07 gist_html):', f'요지 {lecparse.GK[0]} · 단계 흐름 {lecparse.GK[1]}')
print('🔑 180자 초과 카드(상자 밖으로 나눔 대상):', ' · '.join(f'{L_["k"]} {KEYLONG.get(L_["k"], 0)}' for L_ in LEC))
# ---- 비교표(칸 안의 ' / ' 나열을 줄 단위로)
tables = []; cur = None
for line in open(DIR + '/tables.txt', encoding='utf-8'):
    line = line.rstrip('\n')
    if line.startswith('#TBL'):
        p = [x.strip() for x in line[4:].split('|')]; cur = {'title': p[0], 'k': '', 'src': '', 'head': [], 'rows': [], 'notes': []}
        for x in p[1:]:
            if x.startswith('k='): cur['k'] = x[2:]
            elif x.startswith('src='): cur['src'] = lecparse.inline(x[4:], ctx)
            elif x.replace(' ', '') == 'sum=1': cur['sum'] = 1   # ux2 E05 의미 축 전체정리표 → 정리표 탭 맨 위(비교표에는 싣지 않음)
        tables.append(cur)
    elif line.startswith('H:') and cur:
        hh = [lecparse.inline(c.strip(), ctx) for c in line[2:].split('|')]
        while hh and not hh[-1]: hh.pop()
        cur['head'] = hh
    elif line.startswith('R:') and cur:
        rr = [c.strip() for c in line[2:].split('|')]
        while len(rr) > len(cur['head']) and not rr[-1]: rr.pop()
        cur['rows'].append(rr)
    elif line.startswith('N:') and cur: cur['notes'].append(lecparse.inline(line[2:].strip(), ctx))
def cell(c):
    if c.strip() == '해당 없음': return '<span class="na" title="해당 없음">해당 없음</span>'   # ux2 fixB VIS13 빈 칸 표기 통일 — 글자(textContent)는 그대로, 화면은 '—'(CSS)
    parts = lecparse._rebalance(lecparse.split_top(c, ' / '))   # 괄호·{r:…} 안의 ' / '는 나누지 않고, 조각을 넘는 표시는 짝을 맞춤
    if len(parts) <= 1: return lecparse.inline(c, ctx)
    return ''.join(f'<div class="ci">{lecparse.inline(x, ctx)}</div>' for x in parts)
CITE1 = re.compile(r'<button class="cite" data-k="([A-Z0-9]+)" data-p="(\d+)">([^<]*?) p\.\d+</button>')
def merge_cites(h):
    """같은 강의의 연속 인용 칩(사이에 공백·쉼표·가운뎃점만)을 하나로: '강의 p.17–21'(이어진 쪽) · 'p.17·19·21'"""
    def run(m):
        cs = CITE1.findall(m.group(0))
        if len({k for k, _, _ in cs}) != 1: return m.group(0)
        ps = [int(p_) for _, p_, _ in cs]
        lab = f'{ps[0]}–{ps[-1]}' if ps == list(range(ps[0], ps[0] + len(ps))) else '·'.join(map(str, ps))
        return f'<button class="cite" data-k="{cs[0][0]}" data-p="{ps[0]}" data-pp="{",".join(map(str, ps))}">{cs[0][2]} p.{lab}</button>'
    return re.sub(r'(?:<button class="cite" data-k="([A-Z0-9]+)" data-p="\d+">[^<]*?</button>)(?:[\s,·]*<button class="cite" data-k="\1" data-p="\d+">[^<]*?</button>)+', run, h)
TBL = []
for i, t in enumerate(tables):
    head = ''.join(f'<th>{c}</th>' for c in t['head'])
    sm_ = t.get('sum'); nc_ = max([len(r) for r in t['rows']] + [len(t['head'])])
    body = ''.join('<tr>' + ''.join((f'<th>{lecparse.inline(c, ctx)}</th>' if j == 0 else f'<td{" class=keycell" if sm_ and j == nc_ - 1 else ""}>{cell(c)}</td>') for j, c in enumerate(r)) + '</tr>' for r in t['rows'])
    nj_ = len(set(re.findall(r'\{jb:([^}]+)\}', ' '.join(c for r in t['rows'] for c in r))) & set(QMAP))   # ux2 E09 표 안 기출 연결 수
    TBL.append({'k': t['k'], 'nj': nj_, **({'sum': 1} if sm_ else {}), 'html': merge_cites(f'<div class="tblwrap{" stbl" if sm_ else ""}" data-aid="{aid("T:" + slug(t["title"]))}" data-alt="{aid("T%d" % i)}" data-nj="{nj_}"><div class="tbt serif">{esc(t["title"])}</div><div class="tscroll"><table class="cmp{" stbl" if sm_ else ""}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>{"".join(f"<div class=note>{n}</div>" for n in t["notes"])}<div class="pgrow"><span class="small">출처</span>{t["src"]}</div></div>')})
for L in lect: L['tbl'] = [i for i, t in enumerate(TBL) if t['k'] == L['k'] and not t.get('sum')]; L['sumt'] = [i for i, t in enumerate(TBL) if t['k'] == L['k'] and t.get('sum')]

# ---- 예상문제
preds = []
CIRC_ALL = '①②③④⑤⑥⑦⑧⑨⑩'
def pq_lines(h):
    """ux2 F10 예상문제 보기(①~⑩, 차례대로·앞이 공백인 것) 앞에서 줄바꿈 — 발문 .ln.q1 + 보기 .ln.li. 글자 그대로(나눈 자리의 공백은 앞 줄 끝에 남음) · 인용 버튼 안 글자는 건너뜀"""
    pos, want, inb = [], 0, 0
    for m in re.finditer(r'<[^>]+>|[①-⑩]', h):
        t = m.group(0)
        if t.startswith('<'): inb += 1 if re.match(r'<button\b', t) else (-1 if t == '</button>' else 0); continue
        if inb or want >= len(CIRC_ALL) or t != CIRC_ALL[want] or (m.start() and h[m.start() - 1] not in ' \n'): continue
        pos.append(m.start()); want += 1
    if len(pos) < 2: return h
    parts = [h[:pos[0]]] + [h[a:b] for a, b in zip(pos, pos[1:] + [len(h)])]
    return (f'<div class="ln q1">{parts[0]}</div>' if parts[0].strip() else '') + ''.join(f'<div class="ln li">{x}</div>' for x in parts[1:])
for i, p in enumerate(PRED):
    rel = ''
    if p['b'] and p['b'] in QMAP: r = QMAP[p['b']]; rel = f'<button class="jbchip" data-go="{r["id"]}">관련 기출 {"·".join(YR(y) for y in r["yrs"])}년 · {esc(r["short"])}</button>'
    preds.append({'k': p['k'], 'html': f'<article class="pc" data-ptype="{"v" if "짤" in p["t"] else "n"}" data-aid="{aid("P:" + slug(p.get("q_raw") or p["q"]))}" data-id="P:{aid("P:" + slug(p.get("q_raw") or p["q"]))}" data-alt="{aid("P%d" % i)}"><div class="qhead"><span class="ybadge pr"><b>예상</b><i>{esc(p["t"])}</i></span><span class="chip pf">{esc(LECNAME[p["k"]])}</span>{rel}</div><div class="pq">{pq_lines(p["q"])}</div><div class="acts"><button class="btn pri" data-tog="1">답 보기</button><button class="btn mk ok" data-mk="ok">✓ 맞음</button><button class="btn mk ng" data-mk="ng">✗ 틀림</button><button class="btn mk bm" data-mk="bm">★</button></div><div class="ans"><section class="ab jbans"><h5>답 <small>강의자료 문장으로만 구성</small></h5><div class="pre2">{lecparse.render_block(p["a_raw"], ctx) if p.get("a_raw") else p["a"]}</div></section></div></article>'})

# ---- 기출 한눈표
CIRC_N = '①②③④⑤⑥⑦⑧⑨'
WRONG_Q = re.compile(r'옳지\s*않은|틀린\s*것|잘못된|바르지\s*않은')
ANS_NUM = re.compile(r'^\s*(?:\[답\]|답)\s*[:：)]?\s*((?:[1-9①-⑨]\s*(?:\)|번)?\s*(?:[,，·/]|및|와|과)?\s*)+)\.?\s*$')
ANS_NUM_VAL = re.compile(r'^\s*(?:\[답\]|답)\s*[:：)]?\s*([1-9])\s*\)\s+[0-9]+(?:\.[0-9]+)?\s*\.?\s*$')
def pick_choices(q, core):
    """한눈표: 답이 보기 번호뿐이면 문제 원문에서 그 번호의 보기 줄(글자 그대로)을 찾음 → (라벨, [줄…]) / 못 찾으면 (라벨, None) / 번호 답이 아니면 None"""
    if not core: return None
    m = ANS_NUM.match(core[0])
    if not m: return None
    m1 = ANS_NUM_VAL.match(core[0])   # "답: 5) 2" = 5번 보기(내용이 숫자 2) — 뒤 숫자는 보기 번호가 아님(10-03 최종 점검 GERI C01·C04)
    nums = []
    for x in ([m1.group(1)] if m1 else re.findall(r'[1-9①-⑨]', m.group(1))):
        n = CIRC_N.index(x) + 1 if x in CIRC_N else int(x)
        if n not in nums: nums.append(n)
    qt, _ = split_qa(q); L = reflow.reflow(qt, True)
    stem, rest = (L[0] if L else ''), L[1:]
    lab = '틀린 보기' if WRONG_Q.search(' '.join(L[:2])) else '정답 보기'
    def mk(n):
        c = CIRC_N[n - 1] if n <= len(CIRC_N) else '@'
        return rf'(?:{n}\s?\)|\(\s?{n}\s?\)|{c})'
    out = []
    for n in nums:
        hit = None
        for l in rest:                                   # 줄 첫머리 보기
            if re.match(r'^\s*' + mk(n), l): hit = l.strip(); break
        if hit is None:                                  # 한 줄에 보기 여러 개
            for l in [stem] + rest:
                mm = re.search(r'(?:^|\s)(' + mk(n) + r'.*?)(?=\s' + mk(n + 1) + r'|$)', l)
                if mm and (l is not stem or mm.start(1) > 0): hit = mm.group(1).strip(); break
        if hit is None:
            for l in rest:
                if re.match(rf'^\s*{n}\s?\.\s', l): hit = l.strip(); break
        if hit is None: return (lab, None)
        nx = re.search(r'\s' + mk(n + 1) + r'\s?\S', hit)
        if nx and nx.start() > 2: hit = hit[:nx.start()].strip()
        out.append(hit)
    return (lab, out)
def ans_core(q):
    _, at = split_qa(q); L = reflow.reflow(at); out = []
    for s in L:
        if re.match(r'^\s*(참고|해설)\s*[:：)]?', s): break
        out.append(s)
    def lab_(s):   # ux2 E10 '답 :'·'답:'·'[답]' 라벨은 글자 그대로 .alab(작은 회색)
        m = re.match(r'^(\s*(?:\[답\]|답)\s*[:：)]?\s*)(.*)$', s)
        return (f'<span class="alab">{esc(m.group(1))}</span>{esc(m.group(2))}') if m and m.group(2).strip() else esc(s)
    TOK = lambda s: [x for x in re.split(r'\s{2,}|\t|\s\|\s', s.strip()) if x]
    tab = [s for s in out if len(TOK(s)) >= 3 and all(len(x) <= 14 for x in TOK(s))]
    if len(tab) >= 3:   # 표 모양 답(짧은 토막 3칸↑ 줄이 3줄↑) — 첫 3줄만 글자 그대로 격자로
        h = ''.join(f'<div class="ln tabl">{esc(s)}</div>' for s in out[:3]) + (f'<div class="ln small">… (이하 {len(out) - 3}줄 카드에서)</div>' if len(out) > 3 else '')
    else:
        h = ''.join(f'<div class="ln{" li" if reflow.LISTM.match(s) else ""}">{lab_(s)}</div>' for s in out[:14]) + ('<div class="ln small">… (이하 카드에서)</div>' if len(out) > 14 else '')
    core_ = re.sub(r'^\s*(?:\[답\]|답)\s*[:：)]?\s*', '', ' '.join(out)).strip()
    if not core_ or re.fullmatch(r'\(?\s*(?:해설|해답|아래|위)?\s*(?:참조|참고)\s*\)?\s*\.?', core_):   # 답 핵심이 '해설 참조'뿐 → 해설 첫 줄부터 6줄(원문 그대로) · 해설도 없으면 연결 카드 ⚡ 첫 줄
        i0 = next((i for i, x in enumerate(L) if re.match(r'^\s*해설\s*[:：)]?', x)), None)
        ex_ = []
        if i0 is not None:
            first = re.sub(r'^\s*해설\s*[:：)]?\s*', '', L[i0]).strip(); ex_ = ([first] if first else []) + L[i0 + 1:]
        if ex_: h += '<div class="ln exl"><span class="alab">해설</span></div>' + ''.join(f'<div class="ln">{esc(x)}</div>' for x in ex_[:6]) + (f'<div class="ln small">… (이하 {len(ex_) - 6}줄 카드에서)</div>' if len(ex_) > 6 else '')
        elif q['id'] in Q2CARD:
            k_, j_ = Q2CARD[q['id']]; c_ = next(L_ for L_ in LEC if L_['k'] == k_)['cards'][j_]
            if c_['recall']: h += f'<div class="ln exl"><span class="alab">📖</span> {lecparse.inline(c_["recall"][0], ctx)}</div>'
        if not core_ and '<div class="ln exl">' not in h: h += '<div class="ln small">(JB에 답 표기 없음 — 문제를 눌러 원문으로)</div>'
    pk = pick_choices(q, out)
    if pk:
        lab, lines = pk
        if lines: h += ''.join(f'<div class="ln pick"><b>{PICKLAB.get(lab, lab)}</b> {esc(x)}</div>' for x in lines)
        else:
            qt, _ = split_qa(q); QL = reflow.reflow(qt, True)[1:]; ch = [x for x in QL if reflow.LISTM.match(x)] or QL
            if ch: h += f'<details class="pickd noann"><summary>▸ 보기 펼치기</summary>{"".join(f"<div class=ln>{esc(x)}</div>" for x in ch)}</details>'
    return h
def ybadge_sum(q):
    ys = ['%02d' % y for y in q['yrs']]
    lab_ = '·'.join(ys) if len(ys) <= 4 else '·'.join(ys[:3]) + f' +{len(ys) - 3}'
    return f'<span class="ybadge sm n{min(len(ys),3)}" title="{" · ".join(YR(y) for y in q["yrs"])}"><b>{lab_}</b></span>'
SUMCHIPS = []
sumall = ['']   # ux2 E11 공부 막대는 아래에서(강의 칩이 필요)
sname_ = lambda L: L['title']   # ux4e 원래 강의 제목 그대로
for n_, L in enumerate(LEC + [None]):
    k = L['k'] if L else ''
    rows = [q for q in Q if q['tier'] != 'C' and q['lk'] == k]
    if not rows: continue
    rows.sort(key=lambda q: (-len(q['yrs']), -(q['yrs'][0] if q['yrs'] else 0)))
    def srow(q):
        st_, bd_ = sum_q(q)
        lk_ = (f'<button class="chip lec sumlk noann" data-golec="{Q2CARD[q["id"]][0]}:{Q2CARD[q["id"]][1]}" aria-label="정리본 카드로"></button>') if q['id'] in Q2CARD else ''
        vc_ = f"<div><span class='chip v-{q['v']}'>{VNAME[q['v']]}</span></div>" if q['v'] in ('diff', 'part', 'none') else ''
        nt_ = "<div class='note'>⚠ 아래 JB 답은 강의자료와 어긋납니다 — 문제를 눌러 ‘강의자료 대조’를 확인하세요.</div>" if q['v'] == 'diff' else ''
        return (f'<tr class="{heat(len(q["yrs"]))}{" rep" if len(q["yrs"]) >= 2 else ""}" data-id="{q["id"]}"><th data-col="yr">{ybadge_sum(q)}<div class="small">{esc(q["prof"])}</div><span class="smk noann"><i class="mdot"></i><button data-smk="ok" aria-label="맞음"></button><button data-smk="ng" aria-label="틀림"></button><button data-smk="bm" aria-label="북마크"></button></span></th>'
                f'<td class="qs" data-col="q">{go(q["id"], st_, cls="link sq", src="sum")}{bd_}{lk_}{vc_}</td><td data-col="ans">{nt_}<div class="lines">{ans_core(q)}</div></td></tr>')
    tr = ''.join(srow(q) for q in rows)
    sid_ = 'sm-' + (k if k else 'none'); SUMCHIPS.append((sid_, (sname_(L) if L else '대응 쪽 없음'), len(rows)))
    sumall.append(f'<div class="tblwrap" id="{sid_}" data-aid="{aid("SUM:" + (k if k else "none"))}" data-alt="{aid("SUM%d" % n_)}"><div class="tbt serif">{esc(L["title"] if L else "강의자료에 대응 쪽 없음")} <small>{len(rows)}문항</small></div><div class="tscroll"><table class="sum"><thead><tr><th style="width:96px" data-col="yr">출제</th><th style="width:32%" data-col="q">문제</th><th data-col="ans">답 핵심 (JB 원문)</th></tr></thead><tbody>{tr}</tbody></table></div></div>')
sumall[0] = ('<div class="sumbar noann" id="sumbar"><div class="sbr"><span class="sbl">' + ''.join(f'<button class="tg" data-sgo="{a_}">{esc(n_)} <b>{c_}</b></button>' for a_, n_, c_ in SUMCHIPS) + '</span></div>'
             '<div class="sbr"><button class="tg" data-filt="rep">2회↑만</button><button class="tg" data-sf="ng">✗ 틀린 것만</button><button class="tg" data-sf="todo">안 푼 것만</button><button class="tg" data-sumhide="1" title="답 칸을 가리고 떠올리기 — 칸을 누르면 그 칸만 열림(저장 안 함)">답 가리기</button>'
             '<span class="small sleg"><i class="lg2"></i>2회↑ <i class="lg1"></i>1회 · <i class="mdot ok"></i>맞음 <i class="mdot ng"></i>틀림 <i class="mdot"></i>안 푼 것 · 문제를 누르면 JB · 📖 정리본 카드</span></div></div>')

# ---- JB 필터 막대 / 대장
import build2 as B
TIERS = S.TIERS
nt = {t: sum(1 for q in Q if q['tier'] == t) for t in 'ABC'}
profs = []
for q in Q:
    p_ = (q['prof'] or '').split('(')[0]
    if p_ and p_ not in profs: profs.append(p_)
# JB 필터 막대는 허브(shell.html jbBar)가 pack.jbprofs·jbyears·tcount로 그림 — 과목 JB 문제와 강의 기출 탭이 같이 씀
ledger = B.view_led()
ledger = re.sub(r'(?<!<div class="tscroll">)(<table class="cmp">.*?</table>)', r'<div class="tscroll">\1</div>', ledger, flags=re.S)   # 기출 대장 표는 가로 스크롤 상자 안에(F6 — 페이지 전체가 옆으로 밀리지 않게)
ledger = re.sub(r'<th>20(\d{2})</th>', r'<th title="20\1">\1</th>', ledger).replace('<table class="cmp">', '<table class="cmp led">')   # ux2 E12 연도 머리 두 자리 · 첫 열(교수) 고정은 허브 tblFit(.ovx)
# 과목 홈 공부 순서(U21): subject.py의 GUIDE(선택) — [(굵은 제목, 설명, 실행 버튼 키)]. 없으면 자동 규칙(JB 통계만):
#   교수별 최근 해 짤 비율 평균 ≥ 60%면 1단계 = '⭐ 2회 이상 n문항 · 한눈표로 답부터'. 실행 키: resume(이어서 학습)·todo(안 푼 것)·rep(2회 이상만 풀기)·sumrep(한눈표 2회 이상)
GUIDE = getattr(S, 'GUIDE', None)
if GUIDE: guide = [{'b': g[0], 't': g[1], 'act': g[2] if len(g) > 2 else ''} for g in GUIDE]
else:
    guide = [{'b': '강의 정리본 → 학습', 't': '‘이 강의의 틀’로 흐름 → 카드마다 🔑 → 세부 → ⭐ 시험포인트', 'act': 'resume'},
             {'b': '강의 → 기출', 't': '그 강의 기출을 한 장씩 풀고 맞음/틀림 — 📖 칩으로 정리본과 오가기', 'act': 'todo'},
             {'b': '강의 → 플래시카드·⚡자동 빈칸', 't': '암기 줄을 가리고 떠올리기', 'act': ''},
             {'b': '과목 → JB 문제', 't': '출제 횟수 순으로 풀고 틀린 것만 다시 · 비교표 · 예상문제로 마무리', 'act': 'rep'}]
    avg_r = sum(PRATIO) / len(PRATIO) if PRATIO else None
    _JN = [(PSM[p_][ys_[0]]['jjal'], PSM[p_][ys_[0]]['jjal'] + PSM[p_][ys_[0]]['tal']) for p_ in PCUR for ys_ in [[y for y, d in PSM[p_].items() if not d['base']]] if ys_]   # 사용자 09-29 '퍼센트 필요 없어' — 교수별 최근 해 짤 수/문항 수 합
    if avg_r is not None and avg_r >= 0.6 and top:
        guide.insert(0, {'b': f'⭐ 2회 이상 {len(top)}문항', 't': f'한눈표로 답부터 — 교수별 최근 해 짤 {sum(j for j, _ in _JN)}/{sum(n for _, n in _JN)}문항(짤 = 이전 해에도 나온 문제)', 'act': 'sumrep'})
print('공부 순서 1단계:', guide[0]['b'], '| 교수별 최근 짤 비율', [round(r_ * 100) for r_ in PRATIO])

# ---- 이미지(인용·썸네일 쪽 추가)
def b64(im, q):
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
# 10-04 사용자 '피피티 사진 … 화질이 너무 깨져서 내용이 안 보이는데 … 틀과 크기는 그대로 유지하면서 화질만 개선 … 렉이 먹는다던가 파일이 너무 무거워져서 … 없게끔'
#   강의 쪽 그림 = 원본 쪽 이미지 폭(1100) 그대로 WebP q72(예전 740px JPEG q38 — 글자 뭉개짐) · 한 장 평균 32KB → 47KB · 화면 크기는 CSS(폭 100%·max-height)라 그대로 · 지연 로딩(imgSet) 그대로 · JB 원본 그림은 그대로
LECW, LECQ = 1100, 72
def webp64(im):
    b = io.BytesIO(); im.save(b, 'WEBP', quality=LECQ, method=6); return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
lecimg = {}; PREV = J.prev_images(SID)   # 강의 원본 이미지가 없으면 지금 docs/에 올라가 있는 이미지를 그대로 씀
for (k, p) in sorted(ctx['cited'] | {(k_, p_) for k_, r_ in S.FORCE_PAGES.items() for p_ in r_}):
    f = S.lec_img_path(k, p)
    if not f or not os.path.exists(f):
        if f and f'{k}-{p}' in PREV: lecimg[f'{k}-{p}'] = PREV[f'{k}-{p}']
        continue
    im = Image.open(f).convert('RGB'); w, hh = im.size
    if w > LECW: im = im.resize((LECW, int(hh * LECW / w)), Image.LANCZOS)
    lecimg[f'{k}-{p}'] = webp64(im)

HINTS = []
for L in LEC:
    hs = [x for n in L['notes'] for x in split_note(n) if HINT_RE.search(x)]
    if hs: HINTS.append({'k': L['k'], 't': L['title'], 'h': lecparse.inline(' '.join(hs), ctx)})
pack = {'id': SID, 'title': TITLE, 'hints': HINTS, 'en': EN, 'color': COLOR, 'profs': PROFS, 'built': S.BUILT, 'stats': {'cards': len(Q), 'main': sum(1 for q in Q if q['tier'] != 'C'), 'ref': sum(1 for q in Q if q['tier'] == 'C'), 'rep': sum(1 for q in Q if q['tier'] != 'C' and len(q['yrs']) >= 2)}, 'refids': [q['id'] for q in Q if q['tier'] == 'C'],
        'tiers': TIERS, 'top': top, 'trends': trends_html, 'guide': guide, 'pstrat': PSTRAT, 'imgalias': getattr(S, 'IMG_ALIAS', {}), 'lecname': LECNAME, 'cards': {q['id']: qcard(q, i) for i, q in enumerate(Q)}, 'order': [q['id'] for q in Q], 'preds': preds, 'tables': TBL, 'lect': lect, 'jbprofs': profs, 'jbyears': sorted({y for q in Q for y in q['yrs']}, reverse=True), 'tcount': nt, 'sumall': ''.join(sumall), 'ledger': ledger}
# JB 문항 id 잠금(C09, tools/jblock.py) — 새 id만 잠금에 추가 · 팩에 이번 해시(jbhash, verify가 비교)와 옮김 표(jbmove·jbmovev, 허브가 기록을 옮김)
import jblock as _JL
_QH = {q['id']: _JL.qhash(split_qa(q)[0]) for q in Q}
_jlock, _jmove, _jadd = _JL.update(SID, _QH)
pack['jbhash'] = _QH
if _jmove: pack['jbmove'] = _jmove; pack['jbmovev'] = _hl.md5(json.dumps(_jmove, sort_keys=True).encode('utf-8')).hexdigest()[:8]
_jerr = _JL.check(SID, _QH, _jlock, _jmove)
print('JB id 잠금:', len(_jlock), '| 새로 잠금', len(_jadd), '| 옮김 표', len(_jmove), ('| ⚠ ' + ' · '.join(_jerr[:5]) + ' → ' + _JL.need_msg(SID)) if _jerr else '')
SYMPUA = {'\uf0b0': '°', '\uf0b1': '±', '\uf0b4': '×', '\uf0ae': '→', '\uf0ac': '←', '\uf0b3': '≥', '\uf0a3': '≤'}   # 10-05 PDF Symbol 글꼴의 사용 영역 글자(JB OMS1 Q44 '7\uf0b0' = 7°) → 원래 기호(화면 □ 깨짐)
js = lambda o: re.sub('[\uf0a3\uf0ac\uf0ae\uf0b0\uf0b1\uf0b3\uf0b4]', lambda m: SYMPUA[m.group(0)], json.dumps(o, ensure_ascii=False)).replace('</', '<\\/')
import hashlib as _hl
_h8 = lambda t: _hl.md5(t.encode('utf-8')).hexdigest()[:8]
shell = open(DIR + '/shell.html', encoding='utf-8').read()
BUILD = _h8(shell)   # 허브 코드 판 — index(HUB_BUILD)와 모든 팩(p.build)에 같이 박음(F5: 배포 중 옛 index·새 팩 섞임 감지)
pack['build'] = BUILD
CH = {}   # JB 원본 쪽 이미지는 판본별 청크(<SID>.img.jb23/jb24/jb25.js) — 누른 판본 것만 받음(U29, 재압축 없음)
for key_, v_ in IMG['jb'].items(): CH.setdefault('jb' + key_.split('-')[0], {'jb': {}})['jb'][key_] = v_
for key, v in lecimg.items():
    ck = key.split('-')[0]; ck = getattr(S, 'IMG_ALIAS', {}).get(ck, ck)
    CH.setdefault(ck, {'lec': {}})['lec'][key] = v
img_files = {c: "JBLHUB.images('%s',%s,'%s');" % (SID, js(o), c) for c, o in CH.items()}
pack['imgv'] = {c: _h8(t) for c, t in img_files.items()}   # 이미지 청크 캐시 무효화(?v=)
# 옛 허브(배포본) 표시 기준선 — 옛 표시가 남은 과목만 허브가 받아 표시에 문맥(p·s·v)을 붙임(F1, tools/legacy_base.py)
LXF = os.path.join(DIR, 'legacy_txt.json'); lx_js = None
if os.path.exists(LXF):
    _lx = json.load(open(LXF, encoding='utf-8'))
    lx_js = "JBLHUB.legacy('%s',%s,%s);" % (SID, js(_lx['txt']), js(_lx.get('rev', '')))
    pack['lx'] = _h8(lx_js)
# 옛 허브(JBLHUB.build 없음)가 이 팩을 받으면 새 index로 바꿔 엶(?v= 붙여 캐시 우회) — 같은 판을 이미 붙였으면 그냥 등록
pack_js = ("window.JBLHUB&&!JBLHUB.build&&location.search.indexOf('v=%s')<0&&/^https?:/.test(location.protocol)&&location.replace(location.pathname+'?v=%s'+location.hash);"   # 중괄호 없는 한 줄(팩 파서는 첫 '{'부터 읽음)
           "JBLHUB.register(%s);") % (BUILD, BUILD, js(pack))
OUT = J.DOCS; os.makedirs(OUT + '/packs', exist_ok=True)
open(OUT + f'/packs/{SID}.js', 'w', encoding='utf-8').write(pack_js)
# 허브가 불러올 팩 = docs/packs에 실제로 있는 <SID>.js (없는 과목은 '자료 대기' 카드 — 404 방지) · 팩마다 내용 지문(?v=)
READY = [x for x in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH'] if os.path.exists(OUT + f'/packs/{x}.js')]
PV = {x: _h8(open(OUT + f'/packs/{x}.js', encoding='utf-8').read()) for x in READY}
PSZ = {x: round(sum(os.path.getsize(os.path.join(OUT, 'packs', f)) for f in os.listdir(os.path.join(OUT, 'packs')) if f == x + '.js') / 1e6, 1) for x in READY}   # ux2 fixB flow V11 첫 방문 진행 표시(MB)
open(OUT + '/index.html', 'w', encoding='utf-8').write(shell.replace('<!--INLINE_PACKS-->', '').replace('null/*READY*/', js(READY)).replace('null/*PV*/', js(PV)).replace('null/*PSZ*/', js(PSZ)).replace("'dev'/*BUILD*/", js(BUILD)))
# 홈 화면 앱(C11) — docs/manifest.webmanifest·icon-192.png·icon-512.png (내용이 바뀐 때만 씀 · 모든 과목 빌드가 같은 것을 냄)
def _icon(n):
    from PIL import ImageDraw, ImageFont
    im = Image.new('RGB', (n, n), '#0F4B4A'); d = ImageDraw.Draw(im)
    d.rounded_rectangle([int(n * .16), int(n * .60), int(n * .84), int(n * .74)], radius=max(2, n // 28), fill='#FFE58A')
    try: f = ImageFont.load_default(size=int(n * .30))
    except TypeError: f = ImageFont.load_default()
    d.text((n / 2, n * .42), 'JBL', fill='#FFFFFF', font=f, anchor='mm')
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True); return b.getvalue()
_man = json.dumps({'name': 'JBL 허브', 'short_name': 'JBL 허브', 'start_url': './', 'scope': './', 'display': 'standalone', 'lang': 'ko', 'background_color': '#F6F4EF', 'theme_color': '#0F4B4A',
                   'icons': [{'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png'}]}, ensure_ascii=False, indent=1).encode('utf-8')
for _fn, _b in [('manifest.webmanifest', _man), ('icon-192.png', _icon(192)), ('icon-512.png', _icon(512))]:
    _p = os.path.join(OUT, _fn)
    if not os.path.exists(_p) or open(_p, 'rb').read() != _b: open(_p, 'wb').write(_b)
for f_ in os.listdir(OUT + '/packs'):
    if f_.startswith(SID + '.img') or f_ == SID + '.lx.js': os.remove(OUT + '/packs/' + f_)
for c, t in img_files.items(): open(OUT + f'/packs/{SID}.img.{c}.js', 'w', encoding='utf-8').write(t)
if lx_js: open(OUT + f'/packs/{SID}.lx.js', 'w', encoding='utf-8').write(lx_js)
# 호환: 옛 index가 찾는 <SID>.img.jb.js — 판본별 청크(jb23·24·25)를 받아 옛 허브가 기다리는 'jb' 한 묶음으로 넘김
_jbc = sorted(c for c in img_files if c.startswith('jb'))
if _jbc:
    open(OUT + f'/packs/{SID}.img.jb.js', 'w', encoding='utf-8').write(
        "(function(){var H=window.JBLHUB,o=H.images,N=%s,acc={jb:{},lec:{}},n=0;H.images=function(i,x,c){if(i==='%s'&&N.indexOf(c)>=0){for(var k in (x.jb||{}))acc.jb[k]=x.jb[k];if(++n===N.length){H.images=o;o.call(H,i,acc,'jb');}return;}return o.apply(H,arguments);};"
        "N.forEach(function(c){var s=document.createElement('script');s.src='packs/%s.img.'+c+'.js';document.head.appendChild(s);});})();" % (js(_jbc), SID, SID))
SINGLE = _os.path.join(J.WORK, f'{S.TITLE.replace(" ", "")}_JBL.html')   # 단일 파일판 — work/에만, 커밋 안 함
open(SINGLE, 'w', encoding='utf-8').write(shell.replace('null/*READY*/', '[]').replace("'dev'/*BUILD*/", js(BUILD)).replace('<!--INLINE_PACKS-->', '<script>' + pack_js + '</script>\n' + ''.join('<script>' + t + '</script>\n' for t in img_files.values())))
# ---- 검증
inlec = {i for L in LEC for c in L['cards'] for i in (list(c['jb']) + [i_ for b in c['body'] if b[0] == 'E' for i_ in b[1][0]])}
print('⭐ 시험포인트로 다뤄지지 않은 연결 기출:', sorted({i for L in LEC for c in L['cards'] for i in c['jb']} - {i_ for L in LEC for c in L['cards'] for b in c['body'] if b[0] == 'E' for i_ in b[1][0]}))
print('정리본에 연결 안 된 현 교수·겹침 기출(미복원 제외):', [q['id'] for q in Q if q['tier'] != 'C' and q['id'] not in inlec and q['v'] != 'na'])
print('정리본이 가리키는 없는 문항:', sorted(i for i in inlec if i not in QMAP))
print('lecture images', len(lecimg), '| sizes MB:', {_os.path.relpath(f, J.ROOT): round(_os.path.getsize(f) / 1e6, 2) for f in [OUT + f'/packs/{SID}.js', SINGLE]}, '| img chunks MB', {c: round(len(t) / 1e6, 2) for c, t in img_files.items()})
