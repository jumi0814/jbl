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
def slug(*xs):
    t = '|'.join(xs); base = re.sub(r'[^a-z0-9가-힣]+', '', t.lower())[:24]
    return base + '_' + _hl.md5(t.encode('utf-8')).hexdigest()[:6]
def card_aid(k, c): return aid(k + ':' + slug(c['en'], c['ko']))
heat = lambda n: 'h2' if n >= 2 else ('h1' if n == 1 else 'h0')
ctx = {'QMAP': QMAP, 'YR': YR, 'LECNAME': LECNAME, 'cited': set()}
LEC = lecparse.load_all()
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
    if L0: q['short'] = re.sub(r'^\s*\d{1,3}(-\d)?\s?[.)]?\s*', '', L0[0]).strip()[:78]
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
for i, lst in cand.items():
    q = QMAP.get(i); pl = PROF_LEC.get((q['prof'] or '').split('(')[0], []) if q else []
    lst.sort(key=lambda x: (x[1] not in pl, x[0]))
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
    if a['kind'] == '짤': return f'<span class="chip jj" title="{YR(a["from"])}년에도 출제된 문제">짤 · {YR(a["from"])}년에도 출제</span>'
    if a['kind'] == '탈': return f'<span class="chip tt" title="이 해에 처음 출제 — {"같은 카드에서 이전 기출이 있음(변형)" if a["tal"] == "변형" else "이전 기출이 없던 카드(새 영역)"}{", 교수 강조 쪽" if a.get("emph") else ""}">탈 · 첫 출제 · {"변형" if a["tal"] == "변형" else "새 영역"}{" · 💬" if a.get("emph") else ""}</span>'
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
def astruct(s, lvl=0):
    s = s.strip()
    if lvl > 5 or len(s) <= 190:
        if len(s) > 150 and lvl == 0: return lecparse.render_block(s, ctx)
        return _lbl(s) or lecparse.inline(s, ctx)
    sub = lambda ps: _ul([astruct(x, lvl + 1) for x in lecparse._rebalance(ps)])
    blk = lambda ps: ''.join(f'<div class="kp">{astruct(x, lvl + 1)}</div>' for x in lecparse._rebalance(ps))   # 문장·대시·쉼표로 나눈 조각은 점 없이 줄로
    # 1) 문장('. ' — p. 같은 약어 제외)
    pos = [(i, 1) for i in _d0(s, '. ') if not re.search(r'(?:\bp|\bvs|\be\.g|\bcf|\bFig|\bNo|\bex|\bi\.e)$', s[max(0, i - 4):i])]
    ps = _cut(s, pos, 'L')
    if len(ps) >= 2 and min(len(x) for x in ps) >= 8: return blk(ps)
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
    gs = [g for g in _groups(s) if g[1] - g[0] > 80]
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
    return f'<div class="agree">✓ 정리본 «{esc(ko)}» 일치</div>' + (f'<div class="aex"><span class="ui">⭐</span><div class="kb">{astruct(etxt) if len(etxt) > 190 else lecparse.render_block(etxt, ctx)}</div></div>' if etxt else '') + f'<div class="cites">{cites}</div>'
def struct_item(x):
    """대조(A)·주변부(M)·메모(N) 항목(HTML): 150자를 넘거나 ' / '가 3개 이상이면 astruct로 점 목록화하고 인용 칩은 끝의 .cites 줄로 모음"""
    plain = html.unescape(re.sub(r'<[^>]+>', '', CITE_BTN.sub('', x)))
    if len(plain) <= 150 and plain.count(' / ') < 3: return x
    cites = CITE_BTN.findall(x); body = CITE_BTN.sub(' ', x); keep = []
    def ph(m): keep.append(m.group(0)); return f'\ue000{len(keep) - 1}\ue001'
    body = re.sub(r'<b class="(?:warn|bulb)">[^<]*</b>', ph, body)
    if '<' in body: return x
    raw = re.sub(r'\s+', ' ', html.unescape(body)).strip()
    r = astruct(raw) if len(raw) > 190 else lecparse.render_block(raw, ctx)
    r = re.sub('\ue000(\\d+)\ue001', lambda m: keep[int(m.group(1))], r)
    return r + (f'<div class="cites">{" ".join(cites)}</div>' if cites else '')
def qcard(q, idx):
    qt, at = split_qa(q); n = len(q['yrs'])
    figq = ''.join(f'<img class="fig" loading="lazy" src="{IMG["crop"][k]}" alt="JB 그림">' for k in q['crops'].get('q', []))
    figa = ''.join(f'<img class="fig" loading="lazy" src="{IMG["crop"][k]}" alt="JB 그림(답)">' for k in q['crops'].get('a', []))
    lecchip = ''
    if q['id'] in Q2CARD:
        k, j = Q2CARD[q['id']]; lecchip = f'<button class="chip lec" data-golec="{k}:{j}">📖 {esc(LECNAME[k])} 정리본</button>'
    sub = []
    sub.append(f'<span class="chip jb">JB 괄호 {esc(q["jbtag"])}</span>' if q['jbtag'] else '<span class="chip jbn">JB 괄호 없음</span>')
    if q.get('xtra'): sub.append(f'<span class="chip cmp">괄호에 없던 {"·".join(YR(y) for y in q["xtra"])}년 추가</span>')
    if q['tal']: sub.append('<span class="chip ol">JB 표기 (탈)</span>')
    if q.get('pick'): sub.append(f'<span class="chip pk">⭐ {esc(q["pick"])}</span>')
    if q.get('lab24'): sub.append(f'<span class="chip ol" title="JB 24판이 2023년 시험 문항에 붙인 표기">24판 표기(23년 시험): {esc(q["lab24"])}</span>')
    h = [f'<article data-aid="{aid(q["id"])}" class="qc {heat(n)} t{q["tier"]}" id="c-{q["id"]}" data-id="{q["id"]}" data-tier="{q["tier"]}" data-prof="{esc((q["prof"] or "").split("(")[0])}" data-lec="{q["lk"]}" data-n="{n}" data-y0="{q["yrs"][0] if n else 0}" data-yrs="{" ".join("%02d" % y for y in q["yrs"])}" data-st="{st_kind(q)}" data-v="{q["v"]}" data-idx="{idx}">',
         f'<div class="qhead">{yr_badge(q)}{st_chip(q)}<span class="chip pf">{esc(q["prof"] or "")}</span>{f'<span class="chip tier" title="{esc(TIERS.get(q["tier"], ""))}">참고 · {esc(TIERS.get(q["tier"], ""))[:22]}</span>' if q["tier"] != "A" else ""}{lecchip}{vchip(q["v"])}</div>',
         f'<div class="qtext">{reflow.render(qt, True)}</div>{figq}']
    if q['fig'] and not figq: h.append('<div class="small">🖼 그림 문항 — 그림은 ‘JB 원본’ 버튼에서 쪽 전체로 확인(원본 쪽에는 답도 함께 보임).</div>')
    h.append(f'<div class="qsub">{"".join(sub)}<span class="chip src">{esc(q["src"])}</span></div>')
    if q['yrsnote']: h.append(f'<div class="note">연도 표기 근거: {esc(q["yrsnote"])}</div>')
    if q.get('rel') and q['rel'] in QMAP: r = QMAP[q['rel']]; h.append(f'<div class="note">다른 해의 관련 문항(별개 출제): {go(r["id"], "·".join(YR(y) for y in r["yrs"]) + "년 · " + esc(r["short"]))}</div>')
    if q.get('pair') and q['pair'] in QMAP: h.append(f'<div class="note">같은 내용이 JB의 다른 연도 칸에도 실려 있음: {go(q["pair"], esc(QMAP[q["pair"]]["src"]))}</div>')
    jbb = ''.join(f'<button class="btn sm" data-jb="{q["ed"]}-{p}">JB 원본 {p}쪽</button>' for p in range(q['pg'], q['pg2'] + 1))
    h.append(f'<div class="acts"><button class="btn pri" data-tog="1">답·해설</button><button class="btn mk ok" data-mk="ok">맞음</button><button class="btn mk ng" data-mk="ng">틀림</button><button class="btn mk bm" data-mk="bm">★</button>{jbb}</div>')
    ansh = reflow.render(at, ans=True) if at.strip() else "<div class=ln>(JB에 답 표기가 따로 없음 — 위 원문 참조)</div>"
    exbtn = '<button class="btn sm exmore noann" data-exmore="1">해설 전체 보기 ▾</button>' if 'class="exw clamp"' in ansh else ''
    a = ['<div class="ans">', f'<section class="ab jbans"><h5>JB 답안 <small>글자는 원문 그대로 · 줄바꿈만 정리</small></h5><div class="lines">{ansh}</div>{exbtn}{figa}</section>']
    if q['A']: a.append(f'<section class="ab chk v-{q["v"]}"><h5>🔎 강의자료 대조 <small>{VNAME[q["v"]]}</small></h5><ul>{"".join((f"<li class=\"auto\">{auto_item(*x)}</li>" if q.get("auto") else f"<li>{struct_item(x)}</li>") for x in q["A"])}</ul>{"".join(f"<div class=note>{struct_item(x)}</div>" for x in q["N"])}</section>')
    elif q['tier'] == 'C':
        same = f' 같은 문제의 다른 수록본은 {go(q["same"], esc(QMAP[q["same"]]["short"]))}에서 강의자료와 대조했습니다.' if q.get('same') else ''
        a.append(f'<section class="ab chk v-na"><h5>🔎 강의자료 대조</h5><div class="small">받은 25·26년도 강의자료에는 이 교수님 파트에 대응하는 강의가 없어 대조하지 않았습니다(JB 원문만 수록).{same}</div></section>')
    if q['M']: a.append(f'<section class="ab more"><h5>🧭 주변부 확장 <small>같은·인접 슬라이드 — 변형 출제 대비</small></h5><ul>{"".join(f"<li>{struct_item(x)}</li>" for x in q["M"])}</ul></section>')
    if q['id'] in Q2CARD:
        k, j = Q2CARD[q['id']]; c_ = [L_ for L_ in LEC if L_['k'] == k][0]['cards'][j]
        key_ = next((v for t, v in c_['body'] if t == 'K'), '')
        m1_ = (' <span class="lkm">⚡ ' + lecparse.inline(c_['recall'][0], ctx) + '</span>') if c_['recall'] else ''
        rec_ = ''.join(lecparse.render_recall(x, ctx) for x in c_['recall'])
        a.append(f'<details class="ab lk"><summary><span class="lkt">📖 «{esc(c_["ko"])}»</span>{m1_}<button class="chip lec" data-golec="{k}:{j}">카드로 이동 →</button></summary><div class="lkey"><div class="ct">🔑 핵심 <small>{esc(LECNAME[k])}</small></div>{lecparse.render_key(key_, ctx) if key_ else esc(c_["gist"])}</div>{("<div class=ct style=margin-top:8px>⚡ 암기</div><ul class=lrec>" + rec_ + "</ul>") if rec_ else ""}</details>')
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
        items = ''.join(f'<li>{lecparse.inline(x.strip(), ctx)}</li>' for x in rest.split(' / ') if x.strip())
        return f'<div class="{cls}">{tag}<div class="lead">{lecparse.inline(lead + " " + tags, ctx)}</div><ol class="sub">{items}</ol></div>'
    return f'<div class="{cls}">{tag}{lecparse.inline(text, ctx)}</div>'
def figgrid(kk, fl):
    out = []
    for p, cap, fk in fl:
        k2 = fk or kk; ctx['cited'].add((k2, p)); lab_ = getattr(S, 'PAGE_LABEL', {}).get(k2, 'p.')
        nm = (' <i>' + esc(LECNAME.get(k2, k2).split('(')[-1].rstrip(')')) + '</i>') if fk else ''
        out.append(f'<figure data-fig="{k2}-{p}"><img data-img="{k2}-{p}" alt=""><figcaption><b>{lab_}{p}</b>{nm}{(" · " + esc(cap)) if cap else ""}</figcaption></figure>')
    return '<div class="figs noann">' + ''.join(out) + '</div>'
def yl(yrs, full=False):
    """연도 라벨: 5개 초과면 앞 4개 + 나머지 수"""
    ys = ['%02d' % y for y in yrs]
    if full or len(ys) <= 5: return '·'.join(ys)
    return '·'.join(ys[:4]) + f' +{len(ys) - 4}'
def ylab(yrs):
    """연도 표기 통일(U24): '24·23·21 (3회)' — 4개 초과는 앞 4개 + '+n'"""
    ys = ['%02d' % y for y in yrs]
    return ('·'.join(ys[:4]) + (f' +{len(ys) - 4}' if len(ys) > 4 else '')) + (f' ({len(ys)}회)' if len(ys) >= 2 else '')
def ychips(ids):
    return ''.join(f'<button class="jbchip{" rep" if len(QMAP[i]["yrs"]) >= 2 else ""}" data-go="{i}" title="{"·".join(YR(y) for y in QMAP[i]["yrs"])}년">{ylab(QMAP[i]["yrs"])}</button>' for i in ids if i in QMAP)
def short_clean(t):
    """문항 요약 끝의 JB 괄호 연도 '(21,22,24)'·'(24, 탈)' 떼기 — 연도는 칩에 있음"""
    return re.sub(r'\s*\([^()]*\b\d{2}\b[^()]*\)\s*\.?\s*$', '', t).strip() or t
def mini_table(rows):
    head = ''.join(f'<th>{lecparse.inline(c, ctx)}</th>' for c in rows[0])
    body = ''.join('<tr>' + ''.join((f'<th>{lecparse.inline(c, ctx)}</th>' if j == 0 else f'<td>{lecparse.inline(c, ctx)}</td>') for j, c in enumerate(r)) + '</tr>' for r in rows[1:])
    return f'<div class="tscroll"><table class="mini"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
def mkey_html(key):
    """정리표 🔑: 라벨을 첫 줄(앞머리·첫 항목) 안에 인라인으로 — '🔑' 혼자 한 줄에 서지 않게"""
    r = lecparse.render_block(key, ctx); lb = '<b class="mkl">🔑</b> '
    m = re.match(r'^(<div class="klead">|<(?:ul|ol) class="[^"]*"><li(?: class="[^"]*")?>)', r)
    return (r[:m.end()] + lb + r[m.end():]) if m else lb + r
def lec_card(L, j, c):
    k = L['k']; ids = [x for x in c['jb'] if x in QMAP]; mx = max([len(QMAP[x]['yrs']) for x in ids] or [0])
    m = re.fullmatch(r'(\d+)(?:-(\d+))?', c['rng']); lab = ''
    if m:
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        pl_ = getattr(S, 'PAGE_LABEL', {}).get(k, 'p.')
        lab = '별도 파일' if a > 100 else ('필기본' if a == 0 else ('%s%d' % (pl_, a) if a == b else '%s%d–%d' % (pl_, a, b)))
    kk = getattr(S, 'ALT_KEY', {}).get(k, k) if (m and int(m.group(1)) > 100) else k
    ys = sorted({y for x in ids for y in QMAP[x]['yrs']}, reverse=True)
    ych = f'<button class="chip yr n{min(mx,3)}" data-go="{ids[0]}"{(" data-gos=" + chr(34) + " ".join(ids) + chr(34)) if len(ids) > 1 else ""} title="{"·".join(YR(y) for y in ys)} — 누르면 기출 문제로">기출 {ylab(ys)}</button>' if ids else ''
    prof = any(b[0] == 'P' for b in c['body'])
    tg = ' · '.join(x for x in c['tag'].split(' · ') if not x.strip().startswith('기출'))
    tagc = f'<span class="chip tagc">{esc(tg)}</span>' if tg else ''
    h = [f'<article class="tc {heat(mx)} open" id="t-{k}-{j}" data-grp="{esc(c["grp"])}" data-aid="{AIDS[(k, j)]}" data-alt="{card_alt(k, j)}"><div class="thead"><span class="badge" data-ttog>{j+1}</span><div class="tt" data-aid="{AIDS[(k, j)]}~h"><div class="en serif" data-ttog>{esc(c["en"])}</div><div class="ko">{esc(c["ko"])} <span class="pg">· {lab}</span></div><div class="one">{lecparse.inline(c["gist"], ctx)}</div><div class="tchips">{tagc}{ych}{"<span class=\'chip emc\'>💬 교수 강조</span>" if prof else ""}</div></div><button class="dn noann" data-done="1" title="이해함 표시">✓</button><button class="car noann" data-ttog title="접기/펼치기" aria-label="접기/펼치기">▶</button></div><div class="tbody">']
    blocks = []; curb = None; key = ''; exams = []; exbuf = []
    def flush_ex():
        if not exbuf: return
        if len(exbuf) == 1:
            v = exbuf[0]; h.append(f'<div class="co c-exam"><div class="ct">⭐ 시험포인트 <span class="ey">{ychips(v[0])}</span></div>{lecparse.render_key(v[1], ctx)}</div>')
        else:
            h.append('<div class="co c-exam"><div class="ct">⭐ 시험포인트 <small>이 카드에서 나온 문제 ' + str(len(exbuf)) + '개</small></div><ul class="exlist">' + ''.join(f'<li><span class="ey">{ychips(v[0])}</span> {lecparse.render_block(v[1], ctx) if len(v[1]) > 150 else lecparse.inline(v[1], ctx)}</li>' for v in exbuf) + '</ul></div>')
        exbuf.clear()
    for t, v in c['body']:
        if t != 'E': flush_ex()
        if t == 'K':
            ks = lecparse.key_split(v)
            if len(v) > 180: KEYLONG[k] = KEYLONG.get(k, 0) + 1
            if ks:   # 🔑이 길면 첫 조각만 상자에 — 나머지는 상자 밖 본문·정리표 세부 칸으로
                key = ks[0]; h.append(f'<div class="co c-key"><div class="ct">🔑 핵심</div>{lecparse.render_key(ks[0], ctx)}</div>' + lecparse.render_key_rest(ks[1], ctx))
                curb = {'h': '', 'items': list(ks[1])}; blocks.append(curb)
            else: key = v; h.append(f'<div class="co c-key"><div class="ct">🔑 핵심</div>{lecparse.render_key(v, ctx)}</div>')
        elif t == 'h': h.append(f'<h4 class="sh">{lecparse.inline(v, ctx)}</h4>'); curb = {'h': v, 'items': []}; blocks.append(curb)
        elif t == 'b':
            h.append(lecparse.render_item(v, ctx))
            if curb is None: curb = {'h': '', 'items': []}; blocks.append(curb)
            curb['items'].append(v)
        elif t == 'T':
            h.append(mini_table(v))
            if curb is None: curb = {'h': '', 'items': []}; blocks.append(curb)
            for r in v[1:]:
                r0 = r[0].replace('**', '').strip(); rest_ = ' / '.join(x for x in r[1:] if x)
                curb['items'].append(('**' + r0 + '** — ' + rest_) if r0 else rest_)
        elif t == 'F': h.append(figgrid(kk, v))
        elif t == 'E':
            exams.append(v); exbuf.append(v)
        elif t == 'P': h.append(f'<div class="co c-prof"><div class="ct">💬 교수님 강조</div>{lecparse.render_key(v, ctx)}</div>')
        elif t == 'U': h.append(f'<div class="und"><span class="ui">✍ 이해</span>{lecparse.render_block(v, ctx) if len(v) > 150 else lecparse.inline(v, ctx)}</div>')
    flush_ex()
    if c['recall']:   # 안내문은 강의의 첫 ⚡ 블록에만(U27 — 카드마다 반복하지 않음)
        tip = '' if MEMTIP.get(k) else ' <small>빨간 글씨를 자동 빈칸으로 가리고 떠올리기</small>'; MEMTIP[k] = 1
        h.append(f'<div class="co c-mem"><div class="ct">⚡ 암기{tip}</div><ul>{"".join(lecparse.render_recall(x, ctx) for x in c["recall"])}</ul></div>')
    h.append('</div></article>')
    thumb = ''
    if c['figs']:
        tp, tk = c['figs'][0]; tk = tk or kk
        thumb = f'<figure class="mth" data-fig="{tk}-{tp}"><img data-img="{tk}-{tp}" alt=""></figure>'
    more2 = lambda bk: f'<button class="link more2 noann" data-scroll2="{k}:{j}">+{len(bk["items"]) - 6} 더 보기(카드로)</button>' if len(bk['items']) > 6 else ''
    det = ''.join(f'<div class="mblk">{("<b>" + lecparse.inline(bk["h"], ctx) + "</b>") if bk["h"] else ""}{"".join(f"<div class=ci>{lecparse.render_block(x, ctx) if len(x) > 110 else lecparse.inline(x, ctx)}</div>" for x in bk["items"][:6])}{more2(bk)}</div>' for bk in blocks if bk['items'])
    ex = ''.join(f'<div class="mex">{ychips(e[0])}<div>{lecparse.inline(e[1], ctx)}</div></div>' for e in exams) or '<span class="small">미출제</span>'
    mem = ''.join(f'<div class="ci">{lecparse.inline(x, ctx)}</div>' for x in c['recall']) or '<span class="small">—</span>'
    row = (f'<tr class="{heat(mx)}"><th><button class="link" data-scroll2="{k}:{j}"><span class="mn">{j+1}</span> <span class="serif men">{esc(c["en"])}</span></button><div class="mko">{esc(c["ko"])} <span class="pg">· {lab}</span></div>{thumb}</th>'
           f'<td data-h="한 줄 요지 · 🔑 핵심"><div class="mg">{lecparse.inline(c["gist"], ctx)}</div>{("<div class=mkey>" + mkey_html(key) + "</div>") if key else ""}</td><td data-h="세부 내용">{det}</td><td class="mt" data-h="⭐ 기출 — 이렇게 나왔다">{ex}</td><td class="mnote" data-h="⚡ 암기 줄">{mem}</td></tr>')
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
prow = ''; psum = ''; SUSE = {}
for p_, qs in profS.items():
    SM = PSM[p_]; t_ = ' / '.join(PPARTS[p_][0])
    lecs = sorted({LECNAME.get(q['lk'], '') for q in qs if q['lk']})
    note = S.PROF_NOTE.get(p_, '')
    prow += f'<tr><th>{esc(p_)}<div class="small">{esc(" · ".join(lecs))}{("<br>" + esc(note)) if note else ""}</div></th><td><div class="yrow">{trend.years_html(SM)}</div></td><td><div class="tlines">{"".join(f"<div>{x}</div>" for x in t_.split(" / "))}</div></td></tr>'
    if p_ not in PCUR: continue
    tags = [t for t in (strat_tag(x) for x in PPARTS[p_][1] if x not in SCOMMON) if t]
    for x in PPARTS[p_][1]:
        if x not in SCOMMON: SUSE.setdefault(x, []).append(p_)
    psum += f'<li title="{esc(t_)}"><span class="tsl">{esc(trend.prof_line(p_, SM))}</span>{(" <span class=tk>· " + esc(" · ".join(tags)) + "</span>") if tags else ""}</li>'
# 📌 전략: 모든 교수에 공통인 항목은 '공통:' 한 줄, 나머지 항목도 문장은 한 번만 쓰고 해당 교수를 뒤에
strat_html = (f'<div class="tc0"><b>공통:</b> {" · ".join(SCOMMON)}</div>' if SCOMMON else '') + (('<div class="tsx">' + ''.join(f'<span>{esc(x)} <i>{esc("·".join(ps))}</i></span>' for x, ps in SUSE.items()) + '</div>') if SUSE else '')
PRATIO = [r_ for r_ in (trend.latest_ratio(PSM[p_]) for p_ in PCUR) if r_ is not None]
trends_html = (f'<div class="panel ptrend"><div class="bt">교수별 출제 경향 · 📌 공부 전략 <span class="small">— JB 자료에서 산출(짤 = 이전 해에 한 번이라도 나온 문제, 탈 = 그 해 처음)</span></div><ul class="tsum">{psum}</ul>'
               + (f'<div class="tstrat"><div class="tsh">📌 공부 전략</div>{strat_html}</div>' if strat_html else '')
               + f'<details class="trd"><summary>연도별 문항 수·짤/탈 세부 보기{(" · 예전 담당 " + esc("·".join(POLD))) if POLD else ""}</summary><div class="tscroll"><table class="cmp trendtbl"><thead><tr><th style="width:15%">교수</th><th style="width:40%">연도별 문항 · 짤/탈</th><th>경향</th></tr></thead><tbody>{prow}</tbody></table></div><div class="small" style="margin-top:6px">{esc(MENT_ALL)}</div></details></div>')
top = [{'id': q['id'], 'yrs': q['yrs'], 'short': short_clean(q['short']), 'prof': q['prof'], 'lk': q['lk']} for q in sorted([q for q in Q if q['tier'] != 'C' and len(q['yrs']) >= 2], key=lambda q: (-len(q['yrs']), -q['yrs'][0]))]
lect = []; KEYLONG = {}; MEMTIP = {}
for L in LEC:
    k = L['k']; cards = []; rows = []; grps = []; curg = None; outline = []
    for j, c in enumerate(L['cards']):
        ch, mx, ids, lab, row = lec_card(L, j, c)
        if c['grp'] != curg:
            curg = c['grp']; grps.append(curg)
            cards.append(f'<h3 class="gdiv" data-grp="{esc(curg)}"><span>{esc(curg)}</span></h3>'); outline.append(f'<div class="og">{esc(curg)}</div>')
            rows.append(f'<tr class="grow"><td colspan="5">{esc(curg)}</td></tr>')
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
                  + (f'<div class="small">이 강의 기출만으로 본 전략: {tstrat}</div>' if strat_ != tstrat else '') + f'</details><div class="tstr">📌 공부 전략{(" (" + esc(pk_) + ")") if strat_ != tstrat else ""}: {strat_}</div>')
    top_ids = sorted(jb_ids, key=lambda i: (QMAP[i]['tier'] != 'A', -len(QMAP[i]['yrs']), -(QMAP[i]['yrs'][0] if QMAP[i]['yrs'] else 0)))[:8]
    ltop = ''.join(f'<li{" class=tmore" if n_ >= 5 else ""}>{ychips([i])} <span class="tq">{esc(short_clean(QMAP[i]["short"]))}</span></li>' for n_, i in enumerate(top_ids))
    NH = [x for n in L['notes'] for x in split_note(n) if HINT_RE.search(x)]; NO = [x for n in L['notes'] for x in split_note(n) if not HINT_RE.search(x)]
    hint_html = f'<div class="co c-prof fhint"><div class="ct">📣 교수님 예고·강조</div>{"".join(f"<div class=fh>{lecparse.inline(x, ctx)}</div>" for x in NH)}</div>' if NH else ''
    gp = '<div class="pills noann" id="grppills"><button class="tg on" data-grp="">전체</button>' + ''.join(f'<button class="tg" data-grp="{esc(g)}">{esc(g)}</button>' for g in grps) + '<span class="sp"></span><button class="tg" data-filt="unread" title="✓ 읽음 표시한 카드 숨기기">안 읽은 것만</button><button class="tg" id="lautofold" title="✓(이해함)을 누르면 그 카드를 접고 다음 카드로">✓하면 접기</button><button class="tg" id="lcond" title="🔑 핵심·⭐ 시험포인트·⚡ 암기 줄만 남김">압축 보기</button><button class="btn sm" id="lopen">모두 펼치기</button><button class="btn sm" id="lclose">모두 접기</button></div>'
    head = (f'<section class="frame" data-aid="{aid(k + ":frame")}"><div class="frt">이 강의의 틀</div><div class="fsrc" data-fsrc="1" title="눌러서 전체 보기">출처 {esc(L["file"])}{"".join(f" · {lecparse.inline(x, ctx)}" for x in NO)}</div>{("<div class=flow>" + flow + "</div>") if flow else ""}{hint_html}{trend_html}<div class="fcols"><div class="outline noann">{"".join(outline)}</div>'
            f'<div class="ftop"><div class="ct">⭐ 많이 나온 순{(" <button class=\'btn sm tmorebtn noann\' data-tmore=1>더 보기 (+" + str(len(top_ids) - 5) + ")</button>") if len(top_ids) > 5 else ""}</div><ol>{ltop}</ol></div></div></section>{gp}')
    summ = f'<div class="pills noann"><span class="small">강의 전체를 한 표로 — 주제를 누르면 학습 탭의 그 카드로, 연도를 누르면 문제로 이동합니다. ⚡자동 빈칸(빨간 글씨)으로 가리고 복습할 수 있습니다.</span></div><div class="tblwrap wide" data-aid="{aid(k + ":sum")}"><div class="tscroll"><table class="mtx"><thead><tr><th style="width:14%">주제</th><th style="width:24%">한 줄 요지 · 🔑 핵심</th><th style="width:30%">세부 내용</th><th style="width:16%">⭐ 기출 — 이렇게 나왔다</th><th style="width:16%">⚡ 암기 줄</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></div>'
    mxl = max([len(QMAP[i]['yrs']) for i in jb_ids] or [0])
    recall = [{'t': c['en'], 'h': lecparse.inline(x, ctx)} for c in L['cards'] for x in c['recall']]
    lcards = [[AIDS[(k, j_)], j_ + 1, c_['ko'], len({x for x in c_['jb'] if x in QMAP} | {x for b_ in c_['body'] if b_[0] == 'E' for x in b_[1][0] if x in QMAP})] for j_, c_ in enumerate(L['cards'])]   # 미니바·사이드바 카드 목록 [aid, 번호, 국문 제목, 기출 수]
    lect.append({'k': k, 'title': L['title'], 'cards': lcards, 'prof': L['prof'], 'yr': L['yr'], 'file': L['file'], 'nsec': len(L['cards']), 'aids': [[AIDS[(k, j_)]] + card_alt(k, j_).split(' ') for j_, c_ in enumerate(L['cards'])], 'heat': heat(mxl), 'head': head, 'learn': ''.join(cards), 'sum': summ,
                 'oldTitles': {o['aid']: ' · '.join(x for x in (o.get('en', ''), o.get('ko', '')) if x) for o in LOCK.get(k, []) if o.get('aid') and o['aid'] not in {AIDS[(k, j_)] for j_ in range(len(L['cards']))}},
                 'jb': jb_ids, 'pred': [i for i, p in enumerate(PRED) if p['k'] == k], 'tbl': [], 'recall': recall, 'tline': trend.short_line(SM), 'tstrat': tstrat, 'hint': (lambda h_: (h_[:180] + '…') if len(h_) > 180 else h_)(' '.join(x for n in L['notes'] for x in split_note(n) if HINT_RE.search(x)))})

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
    parts = [x.strip() for x in c.split(' / ') if x.strip()]
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
    body = ''.join('<tr>' + ''.join((f'<th>{lecparse.inline(c, ctx)}</th>' if j == 0 else f'<td>{cell(c)}</td>') for j, c in enumerate(r)) + '</tr>' for r in t['rows'])
    TBL.append({'k': t['k'], 'html': merge_cites(f'<div class="tblwrap" data-aid="{aid("T:" + slug(t["title"]))}" data-alt="{aid("T%d" % i)}"><div class="tbt serif">{esc(t["title"])}</div><div class="tscroll"><table class="cmp"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>{"".join(f"<div class=note>{n}</div>" for n in t["notes"])}<div class="pgrow"><span class="small">출처</span>{t["src"]}</div></div>')})
for L in lect: L['tbl'] = [i for i, t in enumerate(TBL) if t['k'] == L['k']]

# ---- 예상문제
preds = []
for i, p in enumerate(PRED):
    rel = ''
    if p['b'] and p['b'] in QMAP: r = QMAP[p['b']]; rel = f'<button class="jbchip" data-go="{r["id"]}">관련 기출 {"·".join(YR(y) for y in r["yrs"])}년 · {esc(r["short"])}</button>'
    preds.append({'k': p['k'], 'html': f'<article class="pc" data-ptype="{"v" if "짤" in p["t"] else "n"}" data-aid="{aid("P:" + slug(p.get("q_raw") or p["q"]))}" data-alt="{aid("P%d" % i)}"><div class="qhead"><span class="ybadge pr"><b>예상</b><i>{esc(p["t"])}</i></span><span class="chip pf">{esc(LECNAME[p["k"]])}</span>{rel}</div><div class="pq">{p["q"]}</div><div class="acts"><button class="btn pri" data-tog="1">답 보기</button></div><div class="ans"><section class="ab jbans"><h5>답 <small>강의자료 문장으로만 구성</small></h5><div class="pre2">{lecparse.render_block(p["a_raw"], ctx) if p.get("a_raw") else p["a"]}</div></section></div></article>'})

# ---- 기출 한눈표
CIRC_N = '①②③④⑤⑥⑦⑧⑨'
WRONG_Q = re.compile(r'옳지\s*않은|틀린\s*것|잘못된|바르지\s*않은')
ANS_NUM = re.compile(r'^\s*(?:\[답\]|답)\s*[:：)]?\s*((?:[1-9①-⑨]\s*(?:\)|번)?\s*(?:[,，·/]|및|와|과)?\s*)+)\.?\s*$')
def pick_choices(q, core):
    """한눈표: 답이 보기 번호뿐이면 문제 원문에서 그 번호의 보기 줄(글자 그대로)을 찾음 → (라벨, [줄…]) / 못 찾으면 (라벨, None) / 번호 답이 아니면 None"""
    if not core: return None
    m = ANS_NUM.match(core[0])
    if not m: return None
    nums = []
    for x in re.findall(r'[1-9①-⑨]', m.group(1)):
        n = CIRC_N.index(x) + 1 if x in CIRC_N else int(x)
        if n not in nums: nums.append(n)
    qt, _ = split_qa(q); L = reflow.reflow(qt)
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
    h = ''.join(f'<div class="ln{" li" if reflow.LISTM.match(s) else ""}">{esc(s)}</div>' for s in out[:14]) + ('<div class="ln small">… (이하 카드에서)</div>' if len(out) > 14 else '')
    pk = pick_choices(q, out)
    if pk:
        lab, lines = pk
        if lines: h += ''.join(f'<div class="ln pick"><b>{lab}</b> {esc(x)}</div>' for x in lines)
        else:
            qt, _ = split_qa(q); QL = reflow.reflow(qt)[1:]; ch = [x for x in QL if reflow.LISTM.match(x)] or QL
            if ch: h += f'<details class="pickd noann"><summary>▸ 보기 펼치기</summary>{"".join(f"<div class=ln>{esc(x)}</div>" for x in ch)}</details>'
    return h
def ybadge_sum(q):
    ys = ['%02d' % y for y in q['yrs']]
    lab_ = '·'.join(ys) if len(ys) <= 4 else '·'.join(ys[:3]) + f' +{len(ys) - 3}'
    return f'<span class="ybadge sm n{min(len(ys),3)}" title="{" · ".join(YR(y) for y in q["yrs"])}"><b>{lab_}</b></span>'
sumall = ['<div class="pills noann"><button class="tg" data-filt="rep">2회 이상만</button><span class="small">강의 순서 · 출제 많은 순 — 문제를 누르면 카드로 이동. ⚡자동 빈칸 ‘표의 내용’으로 답 열을 가리고 복습할 수 있습니다.</span></div>']
for n_, L in enumerate(LEC + [None]):
    k = L['k'] if L else ''
    rows = [q for q in Q if q['tier'] != 'C' and q['lk'] == k]
    if not rows: continue
    rows.sort(key=lambda q: (-len(q['yrs']), -(q['yrs'][0] if q['yrs'] else 0)))
    tr = ''.join(f'<tr class="{heat(len(q["yrs"]))}{" rep" if len(q["yrs"]) >= 2 else ""}"><th>{ybadge_sum(q)}<div class="small">{esc(q["prof"])}</div></th><td class="qs">{go(q["id"], esc(q["short"]), src="sum")}{("<div><span class='chip v-" + q["v"] + "'>" + VNAME[q["v"]] + "</span></div>") if q["v"] in ("diff", "part", "none") else ""}</td><td>{("<div class='note'>⚠ 아래 JB 답은 강의자료와 어긋납니다 — 문제를 눌러 ‘강의자료 대조’를 확인하세요.</div>") if q["v"] == "diff" else ""}<div class="lines">{ans_core(q)}</div></td></tr>' for q in rows)
    sumall.append(f'<div class="tblwrap" data-aid="{aid("SUM:" + (k if k else "none"))}" data-alt="{aid("SUM%d" % n_)}"><div class="tbt serif">{esc(L["title"] if L else "강의자료에 대응 쪽 없음")} <small>{len(rows)}문항</small></div><div class="tscroll"><table class="sum"><thead><tr><th style="width:96px">출제</th><th style="width:32%">문제</th><th>답 핵심 (JB 원문)</th></tr></thead><tbody>{tr}</tbody></table></div></div>')

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
    if avg_r is not None and avg_r >= 0.6 and top:
        guide.insert(0, {'b': f'⭐ 2회 이상 {len(top)}문항', 't': f'한눈표로 답부터 — 교수별 최근 해 짤 비율 평균 {round(avg_r * 100)}%(짤 = 이전 해에도 나온 문제)', 'act': 'sumrep'})
print('공부 순서 1단계:', guide[0]['b'], '| 교수별 최근 짤 비율', [round(r_ * 100) for r_ in PRATIO])

# ---- 이미지(인용·썸네일 쪽 추가)
def b64(im, q):
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
lecimg = {}; PREV = J.prev_images(SID)   # 강의 원본 이미지가 없으면 지금 docs/에 올라가 있는 이미지를 그대로 씀
for (k, p) in sorted(ctx['cited'] | {(k_, p_) for k_, r_ in S.FORCE_PAGES.items() for p_ in r_}):
    f = S.lec_img_path(k, p)
    if not f or not os.path.exists(f):
        if f and f'{k}-{p}' in PREV: lecimg[f'{k}-{p}'] = PREV[f'{k}-{p}']
        continue
    im = Image.open(f).convert('RGB'); w, hh = im.size; im = im.resize((740, int(hh * 740 / w))); lecimg[f'{k}-{p}'] = b64(im, 38)

HINTS = []
for L in LEC:
    hs = [x for n in L['notes'] for x in split_note(n) if HINT_RE.search(x)]
    if hs: HINTS.append({'k': L['k'], 't': L['title'], 'h': lecparse.inline(' '.join(hs), ctx)})
pack = {'id': SID, 'title': TITLE, 'hints': HINTS, 'en': EN, 'color': COLOR, 'profs': PROFS, 'built': S.BUILT, 'stats': {'cards': len(Q), 'main': sum(1 for q in Q if q['tier'] != 'C'), 'ref': sum(1 for q in Q if q['tier'] == 'C'), 'rep': sum(1 for q in Q if q['tier'] != 'C' and len(q['yrs']) >= 2)}, 'refids': [q['id'] for q in Q if q['tier'] == 'C'],
        'tiers': TIERS, 'top': top, 'trends': trends_html, 'guide': guide, 'pstrat': PSTRAT, 'imgalias': getattr(S, 'IMG_ALIAS', {}), 'lecname': LECNAME, 'cards': {q['id']: qcard(q, i) for i, q in enumerate(Q)}, 'order': [q['id'] for q in Q], 'preds': preds, 'tables': TBL, 'lect': lect, 'jbprofs': profs, 'jbyears': sorted({y for q in Q for y in q['yrs']}, reverse=True), 'tcount': nt, 'sumall': ''.join(sumall), 'ledger': ledger}
js = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
pack_js = 'JBLHUB.register(' + js(pack) + ');'
CH = {'jb': {'jb': IMG['jb']}}
for key, v in lecimg.items():
    ck = key.split('-')[0]; ck = getattr(S, 'IMG_ALIAS', {}).get(ck, ck)
    CH.setdefault(ck, {'lec': {}})['lec'][key] = v
img_files = {c: "JBLHUB.images('%s',%s,'%s');" % (SID, js(o), c) for c, o in CH.items()}
shell = open(DIR + '/shell.html', encoding='utf-8').read()
OUT = J.DOCS; os.makedirs(OUT + '/packs', exist_ok=True)
open(OUT + f'/packs/{SID}.js', 'w', encoding='utf-8').write(pack_js)
# 허브가 불러올 팩 = docs/packs에 실제로 있는 <SID>.js (없는 과목은 '자료 대기' 카드 — 404 방지)
READY = [x for x in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH'] if os.path.exists(OUT + f'/packs/{x}.js')]
open(OUT + '/index.html', 'w', encoding='utf-8').write(shell.replace('<!--INLINE_PACKS-->', '').replace('null/*READY*/', js(READY)))
for f_ in os.listdir(OUT + '/packs'):
    if f_.startswith(SID + '.img'): os.remove(OUT + '/packs/' + f_)
for c, t in img_files.items(): open(OUT + f'/packs/{SID}.img.{c}.js', 'w', encoding='utf-8').write(t)
SINGLE = _os.path.join(J.WORK, f'{S.TITLE.replace(" ", "")}_JBL.html')   # 단일 파일판 — work/에만, 커밋 안 함
open(SINGLE, 'w', encoding='utf-8').write(shell.replace('null/*READY*/', '[]').replace('<!--INLINE_PACKS-->', '<script>' + pack_js + '</script>\n' + ''.join('<script>' + t + '</script>\n' for t in img_files.values())))
# ---- 검증
inlec = {i for L in LEC for c in L['cards'] for i in (list(c['jb']) + [i_ for b in c['body'] if b[0] == 'E' for i_ in b[1][0]])}
print('⭐ 시험포인트로 다뤄지지 않은 연결 기출:', sorted({i for L in LEC for c in L['cards'] for i in c['jb']} - {i_ for L in LEC for c in L['cards'] for b in c['body'] if b[0] == 'E' for i_ in b[1][0]}))
print('정리본에 연결 안 된 현 교수·겹침 기출(미복원 제외):', [q['id'] for q in Q if q['tier'] != 'C' and q['id'] not in inlec and q['v'] != 'na'])
print('정리본이 가리키는 없는 문항:', sorted(i for i in inlec if i not in QMAP))
print('lecture images', len(lecimg), '| sizes MB:', {_os.path.relpath(f, J.ROOT): round(_os.path.getsize(f) / 1e6, 2) for f in [OUT + f'/packs/{SID}.js', SINGLE]}, '| img chunks MB', {c: round(len(t) / 1e6, 2) for c, t in img_files.items()})
