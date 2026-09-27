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
        q['A'] = [A.cite_html(f'정리본 «{c_["ko"]}» 카드의 슬라이드 내용과 일치 — {etxt} {cites_}')]; q['v'] = 'ok' if q['v'] in ('', 'na') else q['v']

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
def go(i, txt, cls='link'): return f'<button class="{cls}" data-go="{i}">{txt}</button>'

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
    h = [f'<article data-aid="{aid(q["id"])}" class="qc {heat(n)} t{q["tier"]}" id="c-{q["id"]}" data-id="{q["id"]}" data-tier="{q["tier"]}" data-prof="{esc((q["prof"] or "").split("(")[0])}" data-lec="{q["lk"]}" data-n="{n}" data-y0="{q["yrs"][0] if n else 0}" data-v="{q["v"]}" data-idx="{idx}">',
         f'<div class="qhead">{yr_badge(q)}{st_chip(q)}<span class="chip pf">{esc(q["prof"] or "")}</span>{f'<span class="chip tier" title="{esc(TIERS.get(q["tier"], ""))}">참고 · {esc(TIERS.get(q["tier"], ""))[:22]}</span>' if q["tier"] != "A" else ""}{lecchip}<span class="chip v-{q["v"]}">{VNAME[q["v"]]}</span></div>',
         f'<div class="qtext">{reflow.render(qt, True)}</div>{figq}']
    if q['fig'] and not figq: h.append('<div class="small">🖼 그림 문항 — 그림은 ‘JB 원본’ 버튼에서 쪽 전체로 확인(원본 쪽에는 답도 함께 보임).</div>')
    h.append(f'<div class="qsub">{"".join(sub)}<span class="chip src">{esc(q["src"])}</span></div>')
    if q['yrsnote']: h.append(f'<div class="note">연도 표기 근거: {esc(q["yrsnote"])}</div>')
    if q.get('rel') and q['rel'] in QMAP: r = QMAP[q['rel']]; h.append(f'<div class="note">다른 해의 관련 문항(별개 출제): {go(r["id"], "·".join(YR(y) for y in r["yrs"]) + "년 · " + esc(r["short"]))}</div>')
    if q.get('pair') and q['pair'] in QMAP: h.append(f'<div class="note">같은 내용이 JB의 다른 연도 칸에도 실려 있음: {go(q["pair"], esc(QMAP[q["pair"]]["src"]))}</div>')
    jbb = ''.join(f'<button class="btn sm" data-jb="{q["ed"]}-{p}">JB 원본 {p}쪽</button>' for p in range(q['pg'], q['pg2'] + 1))
    h.append(f'<div class="acts"><button class="btn pri" data-tog="1">답·해설</button><button class="btn mk ok" data-mk="ok">맞음</button><button class="btn mk ng" data-mk="ng">틀림</button><button class="btn mk bm" data-mk="bm">★</button>{jbb}</div>')
    a = ['<div class="ans">', f'<section class="ab jbans"><h5>JB 답안 <small>글자는 원문 그대로 · 줄바꿈만 정리</small></h5><div class="lines">{reflow.render(at) if at.strip() else "<div class=ln>(JB에 답 표기가 따로 없음 — 위 원문 참조)</div>"}</div>{figa}</section>']
    if q['A']: a.append(f'<section class="ab chk v-{q["v"]}"><h5>🔎 강의자료 대조 <small>{VNAME[q["v"]]}</small></h5><ul>{"".join(f"<li>{x}</li>" for x in q["A"])}</ul>{"".join(f"<div class=note>{x}</div>" for x in q["N"])}</section>')
    elif q['tier'] == 'C':
        same = f' 같은 문제의 다른 수록본은 {go(q["same"], esc(QMAP[q["same"]]["short"]))}에서 강의자료와 대조했습니다.' if q.get('same') else ''
        a.append(f'<section class="ab chk v-na"><h5>🔎 강의자료 대조</h5><div class="small">받은 25·26년도 강의자료에는 이 교수님 파트에 대응하는 강의가 없어 대조하지 않았습니다(JB 원문만 수록).{same}</div></section>')
    if q['M']: a.append(f'<section class="ab more"><h5>🧭 주변부 확장 <small>같은·인접 슬라이드 — 변형 출제 대비</small></h5><ul>{"".join(f"<li>{x}</li>" for x in q["M"])}</ul></section>')
    if q['id'] in Q2CARD:
        k, j = Q2CARD[q['id']]; c_ = [L_ for L_ in LEC if L_['k'] == k][0]['cards'][j]
        key_ = next((v for t, v in c_['body'] if t == 'K'), '')
        rec_ = ''.join(lecparse.render_recall(x, ctx) for x in c_['recall'][:3])
        a.append(f'<section class="ab lk"><h5>📖 정리본 카드 <small>{esc(LECNAME[k])} · {esc(c_["ko"])}</small> <button class="chip lec" data-golec="{k}:{j}">카드로 이동 →</button></h5><div class="lkey"><div class="ct">🔑 핵심</div>{lecparse.render_key(key_, ctx) if key_ else esc(c_["gist"])}</div>{("<div class=ct style=margin-top:8px>⚡ 암기</div><ul class=lrec>" + rec_ + "</ul>") if rec_ else ""}</section>')
    if q['other']:
        o = ''.join(f'<div class="oh">JB {v["ed"]}판 · {esc(v["sec"])} {esc(v["num"])}번 <button class="btn sm" data-jb="{v["ed"]}-{v["pg"]}">원본 {v["pg"]}쪽</button></div><div class="lines box0">{reflow.render(v["text"], True)}</div>' for v in q['other'])
        a.append(f'<details class="oth"><summary>다른 연도 칸·다른 판본에 실린 같은 문제 {len(q["other"])}건 (원문 그대로)</summary>{o}</details>')
    a.append('</div>'); h.append(''.join(a)); h.append('</article>')
    return ''.join(h)

# ---- 주석(A/M/N) 안의 인용 쪽도 이미지 대상에 포함
for q in Q:
    for x in q['A'] + q['M'] + q['N']:
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
        out.append(f'<figure data-fig="{k2}-{p}"><span class="fb">슬라이드</span><img data-img="{k2}-{p}" alt=""><figcaption><b>{lab_}{p}</b>{nm}{(" · " + esc(cap)) if cap else ""}</figcaption></figure>')
    return '<div class="figs noann">' + ''.join(out) + '</div>'
def yl(yrs, full=False):
    """연도 라벨: 5개 초과면 앞 4개 + 나머지 수"""
    ys = ['%02d' % y for y in yrs]
    if full or len(ys) <= 5: return '·'.join(ys)
    return '·'.join(ys[:4]) + f' +{len(ys) - 4}'
def ychips(ids):
    return ''.join(f'<button class="jbchip{" rep" if len(QMAP[i]["yrs"]) >= 2 else ""}" data-go="{i}" title="{"·".join(YR(y) for y in QMAP[i]["yrs"])}">{("·".join(YR(y) for y in QMAP[i]["yrs"]) if len(QMAP[i]["yrs"]) <= 4 else "·".join(YR(y) for y in QMAP[i]["yrs"][:3]) + "…")}년{(" · " + str(len(QMAP[i]["yrs"])) + "회") if len(QMAP[i]["yrs"]) >= 2 else ""}</button>' for i in ids if i in QMAP)
def mini_table(rows):
    head = ''.join(f'<th>{lecparse.inline(c, ctx)}</th>' for c in rows[0])
    body = ''.join('<tr>' + ''.join((f'<th>{lecparse.inline(c, ctx)}</th>' if j == 0 else f'<td>{lecparse.inline(c, ctx)}</td>') for j, c in enumerate(r)) + '</tr>' for r in rows[1:])
    return f'<div class="tscroll"><table class="mini"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
def lec_card(L, j, c):
    k = L['k']; ids = [x for x in c['jb'] if x in QMAP]; mx = max([len(QMAP[x]['yrs']) for x in ids] or [0])
    m = re.fullmatch(r'(\d+)(?:-(\d+))?', c['rng']); lab = ''
    if m:
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        pl_ = getattr(S, 'PAGE_LABEL', {}).get(k, 'p.')
        lab = '별도 파일' if a > 100 else ('필기본' if a == 0 else ('%s%d' % (pl_, a) if a == b else '%s%d–%d' % (pl_, a, b)))
    kk = getattr(S, 'ALT_KEY', {}).get(k, k) if (m and int(m.group(1)) > 100) else k
    ys = sorted({y for x in ids for y in QMAP[x]['yrs']}, reverse=True)
    ych = f'<span class="chip yr n{min(mx,3)}" title="{"·".join(YR(y) for y in ys)}">기출 {yl(ys)}</span>' if ids else ''
    prof = any(b[0] == 'P' for b in c['body'])
    tg = ' · '.join(x for x in c['tag'].split(' · ') if not x.strip().startswith('기출'))
    tagc = f'<span class="chip tagc">{esc(tg)}</span>' if tg else ''
    h = [f'<article class="tc {heat(mx)} open" id="t-{k}-{j}" data-grp="{esc(c["grp"])}" data-aid="{card_aid(k, c)}" data-alt="{aid(k + ":c%d" % j)}"><div class="thead" data-ttog><span class="badge">{j+1}</span><div class="tt"><div class="en serif">{esc(c["en"])}</div><div class="ko">{esc(c["ko"])} <span class="pg">· {lab}</span></div><div class="one">{lecparse.inline(c["gist"], ctx)}</div><div class="tchips">{tagc}{ych}{"<span class=\'chip emc\'>💬 교수 강조</span>" if prof else ""}</div></div><button class="dn noann" data-done="1" title="이해함 표시">✓</button><span class="car">▶</span></div><div class="tbody">']
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
        if t == 'K': key = v; h.append(f'<div class="co c-key"><div class="ct">🔑 핵심</div>{lecparse.render_key(v, ctx)}</div>')
        elif t == 'h': h.append(f'<h4 class="sh">{lecparse.inline(v, ctx)}</h4>'); curb = {'h': v, 'items': []}; blocks.append(curb)
        elif t == 'b':
            h.append(lecparse.render_item(v, ctx))
            if curb is None: curb = {'h': '', 'items': []}; blocks.append(curb)
            curb['items'].append(v)
        elif t == 'T':
            h.append(mini_table(v))
            if curb is None: curb = {'h': '', 'items': []}; blocks.append(curb)
            for r in v[1:]: curb['items'].append('**' + r[0] + '** — ' + ' / '.join(x for x in r[1:] if x))
        elif t == 'F': h.append(figgrid(kk, v))
        elif t == 'E':
            exams.append(v); exbuf.append(v)
        elif t == 'P': h.append(f'<div class="co c-prof"><div class="ct">💬 교수님 강조</div>{lecparse.render_key(v, ctx)}</div>')
        elif t == 'U': h.append(f'<div class="und"><span class="ui">✍ 이해</span>{lecparse.render_block(v, ctx) if len(v) > 150 else lecparse.inline(v, ctx)}</div>')
    flush_ex()
    if c['recall']: h.append(f'<div class="co c-mem"><div class="ct">⚡ 암기 <small>빨간 글씨를 자동 빈칸으로 가리고 떠올리기</small></div><ul>{"".join(lecparse.render_recall(x, ctx) for x in c["recall"])}</ul></div>')
    h.append('</div></article>')
    thumb = ''
    if c['figs']:
        tp, tk = c['figs'][0]; tk = tk or kk
        thumb = f'<figure class="mth" data-fig="{tk}-{tp}"><img data-img="{tk}-{tp}" alt=""></figure>'
    det = ''.join(f'<div class="mblk">{("<b>" + lecparse.inline(bk["h"], ctx) + "</b>") if bk["h"] else ""}{"".join(f"<div class=ci>{lecparse.render_block(x, ctx) if len(x) > 110 else lecparse.inline(x, ctx)}</div>" for x in bk["items"][:6])}</div>' for bk in blocks if bk['items'])
    ex = ''.join(f'<div class="mex">{ychips(e[0])}<div>{lecparse.inline(e[1], ctx)}</div></div>' for e in exams) or '<span class="small">미출제</span>'
    mem = ''.join(f'<div class="ci">{lecparse.inline(x, ctx)}</div>' for x in c['recall']) or '<span class="small">—</span>'
    row = (f'<tr class="{heat(mx)}"><th><button class="link" data-scroll2="{k}:{j}"><span class="mn">{j+1}</span> <span class="serif men">{esc(c["en"])}</span></button><div class="mko">{esc(c["ko"])} <span class="pg">· {lab}</span></div>{thumb}</th>'
           f'<td><div class="mg">{lecparse.inline(c["gist"], ctx)}</div>{("<div class=mkey><b>🔑</b> " + lecparse.render_block(key, ctx) + "</div>") if key else ""}</td><td>{det}</td><td class="mt">{ex}</td><td class="mnote">{mem}</td></tr>')
    return ''.join(h), mx, ids, lab, row

lect = []
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
        outline.append(f'<button class="ol {heat(mx)}" data-scroll="t-{k}-{j}"><b>{j+1}</b><span class="ot">{esc(c["ko"])}</span><span class="og2">{lecparse.inline(c["gist"], ctx)}</span>{("<span class=oy>" + yl(ys) + "</span>") if ys else ""}</button>')
    jb_ids = sorted([q['id'] for q in Q if q['tier'] != 'C' and q['lk'] == k], key=lambda i: (-len(QMAP[i]['yrs']), -(QMAP[i]['yrs'][0] if QMAP[i]['yrs'] else 0)))
    flow = ''.join(f'<span class="fl">{lecparse.inline(x.strip(), ctx)}</span>' for x in L['map'].split('→')) if L['map'] else ''
    LQ = [q for q in Q if q['tier'] != 'C' and q['lk'] == k and q.get('st')]
    SM = trend.summarize(LQ); ttxt, tstrat = trend.tendency_text(SM, L['title'])
    tal_list = ''
    for q in sorted(LQ, key=lambda q: -q['st']['latest']['y']):
        a = q['st']['latest']
        if a['kind'] == '탈': tal_list += f'<li><button class="jbchip" data-go="{q["id"]}">{YR(a["y"])}</button> {esc(q["short"][:44])} <span class="small">— {a["tal"]}{" · 교수 강조" if a.get("emph") else ""} · {esc(q["st"]["fmt"])}</span></li>'
    trend_html = f'<div class="trend"><div class="frt2">출제 경향 <span class="small">— JB 자료에서 산출(짤 = 이전 해에 한 번이라도 나온 문제, 탈 = 그 해 처음)</span></div><div class="yrow">{trend.years_html(SM)}</div><div class="ttxt tlines">{"".join(f"<div>{x}</div>" for x in ttxt.split(" / "))}</div>{("<details class=tald><summary>탈 문항 목록 — 어디서 새로 냈나</summary><ul>" + tal_list + "</ul></details>") if tal_list else ""}<div class="tstr">📌 공부 전략: {tstrat}</div></div>'
    top_ids = sorted(jb_ids, key=lambda i: (QMAP[i]['tier'] != 'A', -len(QMAP[i]['yrs']), -(QMAP[i]['yrs'][0] if QMAP[i]['yrs'] else 0)))[:8]
    top = ''.join(f'<li>{ychips([i])} {esc(QMAP[i]["short"][:46])}{"…" if len(QMAP[i]["short"]) > 46 else ""}</li>' for i in top_ids)
    gp = '<div class="pills noann" id="grppills"><button class="tg on" data-grp="">전체</button>' + ''.join(f'<button class="tg" data-grp="{esc(g)}">{esc(g)}</button>' for g in grps) + '<span class="sp"></span><button class="tg" id="lcond" title="🔑 핵심·⭐ 시험포인트·⚡ 암기 줄만 남김">압축 보기</button><button class="btn sm" id="lopen">모두 펼치기</button><button class="btn sm" id="lclose">모두 접기</button></div>'
    head = (f'<section class="frame" data-aid="{aid(k + ":frame")}"><div class="frt">이 강의의 틀</div>{("<div class=flow>" + flow + "</div>") if flow else ""}{trend_html}<div class="fcols"><div class="outline noann">{"".join(outline)}</div>'
            f'<div class="ftop"><div class="ct">⭐ 많이 나온 순</div><ol>{top}</ol></div></div>{"".join(f"<p class=fnote>{lecparse.inline(n, ctx)}</p>" for n in L["notes"])}</section>{gp}')
    summ = f'<div class="pills noann"><span class="small">강의 전체를 한 표로 — 주제를 누르면 학습 탭의 그 카드로, 연도를 누르면 문제로 이동합니다. ⚡자동 빈칸(빨간 글씨)으로 가리고 복습할 수 있습니다.</span></div><div class="tblwrap wide" data-aid="{aid(k + ":sum")}"><div class="tscroll"><table class="mtx"><thead><tr><th style="width:15%">주제</th><th style="width:20%">한 줄 요지 · 🔑 핵심</th><th style="width:30%">세부 내용</th><th style="width:17%">⭐ 기출 — 이렇게 나왔다</th><th style="width:18%">⚡ 암기 줄</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></div>'
    mxl = max([len(QMAP[i]['yrs']) for i in jb_ids] or [0])
    recall = [{'t': c['en'], 'h': lecparse.inline(x, ctx)} for c in L['cards'] for x in c['recall']]
    lect.append({'k': k, 'title': L['title'], 'prof': L['prof'], 'yr': L['yr'], 'file': L['file'], 'nsec': len(L['cards']), 'aids': [[card_aid(k, c_), aid(k + ':c%d' % j_)] for j_, c_ in enumerate(L['cards'])], 'heat': heat(mxl), 'head': head, 'learn': ''.join(cards), 'sum': summ,
                 'jb': jb_ids, 'pred': [i for i, p in enumerate(PRED) if p['k'] == k], 'tbl': [], 'recall': recall, 'tline': trend.short_line(SM), 'tstrat': tstrat, 'hint': (lambda h_: (h_[:180] + '…') if len(h_) > 180 else h_)(next((n for n in L['notes'] if re.search(r'시험|강조|예고|공개|QUIZ|퀴즈|별표', n)), ''))})

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
        hh = [esc(c.strip()) for c in line[2:].split('|')]
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
TBL = []
for i, t in enumerate(tables):
    head = ''.join(f'<th>{c}</th>' for c in t['head'])
    body = ''.join('<tr>' + ''.join((f'<th>{lecparse.inline(c, ctx)}</th>' if j == 0 else f'<td>{cell(c)}</td>') for j, c in enumerate(r)) + '</tr>' for r in t['rows'])
    TBL.append({'k': t['k'], 'html': f'<div class="tblwrap" data-aid="{aid("T:" + slug(t["title"]))}" data-alt="{aid("T%d" % i)}"><div class="tbt serif">{esc(t["title"])}</div><div class="tscroll"><table class="cmp"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>{"".join(f"<div class=note>{n}</div>" for n in t["notes"])}<div class="pgrow"><span class="small">출처</span>{t["src"]}</div></div>'})
for L in lect: L['tbl'] = [i for i, t in enumerate(TBL) if t['k'] == L['k']]

# ---- 예상문제
preds = []
for i, p in enumerate(PRED):
    rel = ''
    if p['b'] and p['b'] in QMAP: r = QMAP[p['b']]; rel = f'<button class="jbchip" data-go="{r["id"]}">관련 기출 {"·".join(YR(y) for y in r["yrs"])}년 · {esc(r["short"])}</button>'
    preds.append({'k': p['k'], 'html': f'<article class="pc" data-ptype="{"v" if "짤" in p["t"] else "n"}" data-aid="{aid("P:" + slug(p.get("q_raw") or p["q"]))}" data-alt="{aid("P%d" % i)}"><div class="qhead"><span class="ybadge pr"><b>예상</b><i>{esc(p["t"])}</i></span><span class="chip pf">{esc(LECNAME[p["k"]])}</span>{rel}</div><div class="pq">{p["q"]}</div><div class="acts"><button class="btn pri" data-tog="1">답 보기</button></div><div class="ans"><section class="ab jbans"><h5>답 <small>강의자료 문장으로만 구성</small></h5><div class="pre2">{lecparse.render_block(p["a_raw"], ctx) if p.get("a_raw") else p["a"]}</div></section></div></article>'})

# ---- 기출 한눈표
def ans_core(q):
    _, at = split_qa(q); L = reflow.reflow(at); out = []
    for s in L:
        if re.match(r'^\s*(참고|해설)\s*[:：)]?', s): break
        out.append(s)
    return ''.join(f'<div class="ln{" li" if reflow.LISTM.match(s) else ""}">{esc(s)}</div>' for s in out[:14]) + ('<div class="ln small">… (이하 카드에서)</div>' if len(out) > 14 else '')
sumall = ['<div class="pills noann"><button class="tg" data-filt="rep">2회 이상만</button><span class="small">강의 순서 · 출제 많은 순 — 문제를 누르면 카드로 이동. ⚡자동 빈칸 ‘표의 내용’으로 답 열을 가리고 복습할 수 있습니다.</span></div>']
for n_, L in enumerate(LEC + [None]):
    k = L['k'] if L else ''
    rows = [q for q in Q if q['tier'] != 'C' and q['lk'] == k]
    if not rows: continue
    rows.sort(key=lambda q: (-len(q['yrs']), -(q['yrs'][0] if q['yrs'] else 0)))
    tr = ''.join(f'<tr class="{heat(len(q["yrs"]))}{" rep" if len(q["yrs"]) >= 2 else ""}"><th><span class="ybadge sm n{min(len(q["yrs"]),3)}"><b>{"·".join("%02d" % y for y in q["yrs"])}</b></span><div class="small">{esc(q["prof"])}</div></th><td class="qs">{go(q["id"], esc(q["short"]))}{("<div><span class='chip v-" + q["v"] + "'>" + VNAME[q["v"]] + "</span></div>") if q["v"] in ("diff", "part", "none") else ""}</td><td>{("<div class='note'>⚠ 아래 JB 답은 강의자료와 어긋납니다 — 문제를 눌러 ‘강의자료 대조’를 확인하세요.</div>") if q["v"] == "diff" else ""}<div class="lines">{ans_core(q)}</div></td></tr>' for q in rows)
    sumall.append(f'<div class="tblwrap" data-aid="{aid("SUM:" + (k if k else "none"))}" data-alt="{aid("SUM%d" % n_)}"><div class="tbt serif">{esc(L["title"] if L else "강의자료에 대응 쪽 없음")} <small>{len(rows)}문항</small></div><div class="tscroll"><table class="sum"><thead><tr><th style="width:86px">출제</th><th style="width:32%">문제</th><th>답 핵심 (JB 원문)</th></tr></thead><tbody>{tr}</tbody></table></div></div>')

# ---- JB 필터 막대 / 대장
import build2 as B
TIERS = S.TIERS
nt = {t: sum(1 for q in Q if q['tier'] == t) for t in 'ABC'}
profs = []
for q in Q:
    p_ = (q['prof'] or '').split('(')[0]
    if p_ and p_ not in profs: profs.append(p_)
jbbar = f"""<div class="bar noann" id="jbbar"><div class="brow">
<span class="qf"><button class="tg on" data-qf="">전체</button><button class="tg" data-qf="todo">안 푼 것</button><button class="tg" data-qf="ng">틀린 것</button><button class="tg" data-qf="bm">★ 북마크</button></span>
<select id="fn"><option value="0">출제 횟수 전체</option><option value="2">2회 이상</option><option value="3">3회 이상</option></select>
<select id="fsort"><option value="">JB 수록 순서</option><option value="n">출제 횟수 많은 순</option><option value="y">최근 출제 순</option><option value="r">셔플</option></select>
<input type="search" id="fq" placeholder="문제 검색"><button class="tg" id="fone">한 장씩 풀기</button><button class="tg" id="frev">답 모두 펼치기</button><button class="btn sm" id="fmore">상세 필터 ▾</button></div>
<div class="brow" id="jbmore" hidden><button class="tg on" data-tier="A">{TIERS['A']} {nt['A']}</button>{f'<button class="tg on" data-tier="B">{TIERS["B"]} {nt["B"]}</button>' if nt['B'] else ''}<button class="tg" data-tier="C">{TIERS['C']} {nt['C']}</button>
<label>교수 <select id="fprof"><option value="">전체</option>{''.join(f'<option>{esc(p_)}</option>' for p_ in profs)}</select></label>
<label>강의 <select id="flec"><option value="">전체</option>{''.join(f'<option value="{l["k"]}">{esc(l["title"])}</option>' for l in lect)}</select></label>
<label>대조 <select id="fver"><option value="">전체</option><option value="flag">불일치·부분 일치</option><option value="none">근거 없음</option></select></label></div>
<div class="prog" id="jbprog"></div></div>
<div class="onebar noann" id="onebar"><button class="btn" id="oprev">◀ 이전</button><span id="opos"></span><button class="btn" id="onext">다음 ▶</button><span class="small">O 맞음 · X 틀림 · B 북마크 · Space 답 · ←/→ 이동</span></div>"""
profS = {}
for q in Q:
    if q['tier'] == 'C' or not q.get('st') or not (q['prof'] or '').strip(): continue
    profS.setdefault((q['prof'] or '').split('(')[0], []).append(q)
prow = ''; pstrat = ''
for p_, qs in profS.items():
    SM = trend.summarize(qs); t_, st_ = trend.tendency_text(SM, p_, MENT_PROF.get(p_, ''))
    lecs = sorted({LECNAME.get(q['lk'], '') for q in qs if q['lk']})
    note = S.PROF_NOTE.get(p_, '')
    prow += f'<tr><th>{esc(p_)}<div class="small">{esc(" · ".join(lecs))}{("<br>" + esc(note)) if note else ""}</div></th><td><div class="yrow">{trend.years_html(SM)}</div></td><td><div class="tlines">{"".join(f"<div>{x}</div>" for x in t_.split(" / "))}</div></td></tr>'
    pstrat += f'<li><b>{esc(p_)}</b> — {st_}</li>'
trends_html = f'<div class="panel"><div class="bt">교수별 출제 경향 <span class="small">— JB 자료에서 산출. 짤 = 이전 해에 한 번이라도 나온 문제, 탈 = 그 해 처음 나온 문제. 자료가 시작되는 해는 ‘기준선’으로 표시</span></div><div class="tscroll"><table class="cmp trendtbl"><thead><tr><th style="width:15%">교수</th><th style="width:40%">연도별 문항 · 짤/탈</th><th>경향</th></tr></thead><tbody>{prow}</tbody></table></div><div class="small" style="margin-top:6px">{esc(MENT_ALL)}</div></div><div class="panel"><div class="bt">📌 이 과목 공부 전략</div><ul class="stratl">{pstrat}</ul></div>'
top = [{'id': q['id'], 'yrs': q['yrs'], 'short': q['short'], 'prof': q['prof'], 'lk': q['lk']} for q in sorted([q for q in Q if q['tier'] != 'C' and len(q['yrs']) >= 2], key=lambda q: (-len(q['yrs']), -q['yrs'][0]))]
ledger = B.view_led()

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
    for n in L['notes']:
        if re.search(r'시험|예고|강조|공개|keyword|키워드|별표|QUIZ|퀴즈', n): HINTS.append({'k': L['k'], 't': L['title'], 'h': lecparse.inline(n, ctx)})
pack = {'id': SID, 'title': TITLE, 'hints': HINTS, 'en': EN, 'color': COLOR, 'profs': PROFS, 'built': S.BUILT, 'stats': {'cards': len(Q), 'rep': sum(1 for q in Q if q['tier'] != 'C' and len(q['yrs']) >= 2)},
        'tiers': TIERS, 'top': top, 'trends': trends_html, 'imgalias': getattr(S, 'IMG_ALIAS', {}), 'lecname': LECNAME, 'cards': {q['id']: qcard(q, i) for i, q in enumerate(Q)}, 'order': [q['id'] for q in Q], 'preds': preds, 'tables': TBL, 'lect': lect, 'jbbar': jbbar, 'sumall': ''.join(sumall), 'ledger': ledger}
js = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
pack_js = 'JBLHUB.register(' + js(pack) + ');'
CH = {'jb': {'jb': IMG['jb']}}
for key, v in lecimg.items():
    ck = key.split('-')[0]; ck = getattr(S, 'IMG_ALIAS', {}).get(ck, ck)
    CH.setdefault(ck, {'lec': {}})['lec'][key] = v
img_files = {c: "JBLHUB.images('%s',%s,'%s');" % (SID, js(o), c) for c, o in CH.items()}
shell = open(DIR + '/shell.html', encoding='utf-8').read()
OUT = J.DOCS; os.makedirs(OUT + '/packs', exist_ok=True)
open(OUT + '/index.html', 'w', encoding='utf-8').write(shell.replace('<!--INLINE_PACKS-->', ''))
open(OUT + f'/packs/{SID}.js', 'w', encoding='utf-8').write(pack_js)
for f_ in os.listdir(OUT + '/packs'):
    if f_.startswith(SID + '.img'): os.remove(OUT + '/packs/' + f_)
for c, t in img_files.items(): open(OUT + f'/packs/{SID}.img.{c}.js', 'w', encoding='utf-8').write(t)
SINGLE = _os.path.join(J.WORK, f'{S.TITLE.replace(" ", "")}_JBL.html')   # 단일 파일판 — work/에만, 커밋 안 함
open(SINGLE, 'w', encoding='utf-8').write(shell.replace('<!--INLINE_PACKS-->', '<script>' + pack_js + '</script>\n' + ''.join('<script>' + t + '</script>\n' for t in img_files.values())))
# ---- 검증
inlec = {i for L in LEC for c in L['cards'] for i in (list(c['jb']) + [i_ for b in c['body'] if b[0] == 'E' for i_ in b[1][0]])}
print('⭐ 시험포인트로 다뤄지지 않은 연결 기출:', sorted({i for L in LEC for c in L['cards'] for i in c['jb']} - {i_ for L in LEC for c in L['cards'] for b in c['body'] if b[0] == 'E' for i_ in b[1][0]}))
print('정리본에 연결 안 된 현 교수·겹침 기출(미복원 제외):', [q['id'] for q in Q if q['tier'] != 'C' and q['id'] not in inlec and q['v'] != 'na'])
print('정리본이 가리키는 없는 문항:', sorted(i for i in inlec if i not in QMAP))
print('lecture images', len(lecimg), '| sizes MB:', {_os.path.relpath(f, J.ROOT): round(_os.path.getsize(f) / 1e6, 2) for f in [OUT + f'/packs/{SID}.js', SINGLE]}, '| img chunks MB', {c: round(len(t) / 1e6, 2) for c, t in img_files.items()})
