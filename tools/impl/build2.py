import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import re, json, html, sys, os
import os
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import assemble as A
import subject as S
esc = lambda s: html.escape(str(s), quote=True)
Q, LECT, PRED, TABLES, LEDGER, MENT, IMG, LECMAP = A.Q, A.LECT, A.PRED, A.TABLES, A.LEDGER, A.MENT, A.IMG, A.LECMAP
QMAP = {q['id']: q for q in Q}
YR = lambda y: '20%02d' % y
VNAME = {'ok': '강의자료와 일치', 'part': '부분 일치·부분 근거', 'diff': '⚠ 강의자료와 불일치', 'none': '강의자료에 근거 없음', 'na': '대응 강의자료 없음'}
LECTITLE = {l['k']: l['title'] for l in LECT}
ANSRE = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$|^\s*\[답\]')

def split_text(q):
    qs, as_, mode = [], [], 'q'
    for l in q['text'].split('\n'):
        if re.match(r'^\s*(유사복원\)|추가복원\)|\*?비슷한 복원|복원 원문)', l) or (q['id'] == 'Q23' and re.match(r'^\s*\(\d\)\s', l)): mode = 'q'
        if ANSRE.match(l): mode = 'a'
        (qs if mode == 'q' else as_).append(l)
    return '\n'.join(qs), '\n'.join(as_)

def heat(n): return 'h2' if n >= 2 else ('h1' if n == 1 else 'h0')
def yr_chips(q):
    ys = q['yrs']; n = len(ys); h = ''
    if n: h += f'<span class="chip yr n{min(n,3)}">{" · ".join(YR(y) for y in ys)}년 출제 ({n}회)</span>'
    h += f'<span class="chip jb">JB 괄호 {esc(q["jbtag"])}</span>' if q['jbtag'] else '<span class="chip jbn">JB 괄호 없음</span>'
    if q.get('xtra'): h += f'<span class="chip cmp">괄호에 없던 {"·".join(YR(y) for y in q["xtra"])}년 추가</span>'
    if q['tal']: h += '<span class="chip ol">JB 표기 (탈)</span>'
    if q.get('lab24'): h += f'<span class="chip ol">{esc(q["lab24"])}</span>'
    return h
def jb_btns(ed, a, b): return ''.join(f'<button class="btn sm" data-jb="{ed}-{p}">JB 원본 {p}쪽</button>' for p in range(a, b + 1))
def golink(i, txt): return f'<button class="link" data-go="{i}">{txt}</button>'

def qcard(q, idx):
    qt, at = split_text(q); n = len(q['yrs'])
    figq = ''.join(f'<img class="fig" loading="lazy" src="{IMG["crop"][k]}" alt="JB 그림">' for k in q['crops'].get('q', []))
    figa = ''.join(f'<img class="fig" loading="lazy" src="{IMG["crop"][k]}" alt="JB 그림(답)">' for k in q['crops'].get('a', []))
    h = [f'<article class="qc {heat(n)} t{q["tier"]}" id="c-{q["id"]}" data-id="{q["id"]}" data-tier="{q["tier"]}" data-prof="{esc((q["prof"] or "").split("(")[0])}" data-lec="{q["lk"]}" data-n="{n}" data-y0="{q["yrs"][0] if n else 0}" data-v="{q["v"]}" data-idx="{idx}">']
    h.append(f'<div class="meta">{yr_chips(q)}<span class="chip">{esc(q["prof"] or "")}</span><span class="chip v-{q["v"]}">{VNAME[q["v"]]}</span><span class="chip src">{esc(q["src"])}</span></div>')
    h.append(f'<div class="qtext">{esc(qt)}</div>{figq}')
    if q['fig'] and not figq: h.append('<div class="small">🖼 그림 문항 — 그림은 ‘JB 원본’ 버튼에서 쪽 전체로 확인(원본 쪽에는 답도 함께 보임).</div>')
    if q['yrsnote']: h.append(f'<div class="note">연도 표기 근거: {esc(q["yrsnote"])}</div>')
    if q.get('rel') and q['rel'] in QMAP: r = QMAP[q['rel']]; h.append(f'<div class="note">다른 해의 관련 문항(별개 출제): {golink(r["id"], "·".join(YR(y) for y in r["yrs"]) + "년 · " + esc(r["short"]))}</div>')
    if q.get('pair') and q['pair'] in QMAP: h.append(f'<div class="note">같은 내용이 JB의 다른 연도 칸에도 실려 있음: {golink(q["pair"], esc(QMAP[q["pair"]]["src"]))}</div>')
    h.append(f'<div class="acts"><button class="btn pri" data-tog="1">답·해설</button><button class="btn mk ok" data-mk="ok">맞음</button><button class="btn mk ng" data-mk="ng">틀림</button><button class="btn mk bm" data-mk="bm">★</button>{jb_btns(q["ed"], q["pg"], q["pg2"])}</div>')
    a = ['<div class="ans">']
    a.append(f'<div class="box jbans"><div class="bt">JB 답·해설·참고 <span class="small">(원문 그대로)</span></div><div class="pre">{esc(at) if at else "(JB에 답 표기가 따로 없음 — 위 원문 참조)"}</div>{figa}</div>')
    if q['A']:
        a.append(f'<div class="box chk v-{q["v"]}"><div class="bt">🔎 강의자료 대조 — {VNAME[q["v"]]}</div><ul>{"".join(f"<li>{x}</li>" for x in q["A"])}</ul>{"".join(f"<div class=note>{x}</div>" for x in q["N"])}</div>')
    elif q['tier'] == 'C':
        same = f' 같은 문제의 다른 수록본은 {golink(q["same"], esc(QMAP[q["same"]]["short"]))}에서 강의자료와 대조했습니다.' if q.get('same') else ''
        a.append(f'<div class="box chk v-na"><div class="bt">🔎 강의자료 대조</div><div class="small">받은 25·26년도 강의자료에는 이 교수님 파트에 대응하는 강의가 없어 대조하지 않았습니다(JB 원문만 수록).{same}</div></div>')
    if q['M']: a.append(f'<div class="box more"><div class="bt">🧭 주변부 확장 — 같은·인접 슬라이드의 내용</div><ul>{"".join(f"<li>{x}</li>" for x in q["M"])}</ul></div>')
    if q['other']:
        o = ''.join(f'<div class="oh">JB {v["ed"]}판 · {esc(v["sec"])} {esc(v["num"])}번 <button class="btn sm" data-jb="{v["ed"]}-{v["pg"]}">원본 {v["pg"]}쪽</button></div><div class="pre">{esc(v["text"])}</div>' for v in q['other'])
        a.append(f'<details class="oth"><summary>다른 연도 칸·다른 판본에 실린 같은 문제 {len(q["other"])}건 (원문 그대로)</summary>{o}</details>')
    a.append('</div>'); h.append(''.join(a)); h.append('</article>')
    return ''.join(h)

def view_jb():
    profs = []
    for q in Q:
        p = (q['prof'] or '').split('(')[0]
        if p and p not in profs: profs.append(p)
    cnt = {t: sum(1 for q in Q if q['tier'] == t) for t in 'ABC'}
    bar = f'''<div class="bar" id="jbbar"><button class="tg on" data-tier="A">현 교수 기출 {cnt["A"]}</button><button class="tg on" data-tier="B">정필훈 중 서병무 내용과 겹침 {cnt["B"]}</button><button class="tg" data-tier="C">참고용 과거 교수 {cnt["C"]}</button>
<label>교수 <select id="fprof"><option value="">전체</option>{"".join(f"<option>{esc(p)}</option>" for p in profs)}</select></label>
<label>강의 <select id="flec"><option value="">전체</option>{"".join(f'<option value="{l["k"]}">{esc(l["title"])}</option>' for l in LECT)}</select></label>
<label>출제 <select id="fn"><option value="0">전체</option><option value="2">2회 이상</option><option value="3">3회 이상</option></select></label>
<label>대조 <select id="fver"><option value="">전체</option><option value="flag">불일치·부분 일치</option><option value="none">근거 없음</option></select></label>
<label>내 표시 <select id="fmine"><option value="">전체</option><option value="todo">안 푼 것</option><option value="ng">틀림</option><option value="bm">★</option></select></label>
<label>정렬 <select id="fsort"><option value="">JB 수록 순서</option><option value="n">출제 횟수 많은 순</option><option value="y">최근 출제 순</option><option value="r">셔플</option></select></label>
<input type="search" id="fq" placeholder="문제 검색">
<button class="tg" id="fone">한 장씩 풀기</button><button class="tg" id="frev">답 모두 펼치기</button><span class="cnt" id="jbcnt"></span></div>
<div class="onebar" id="onebar"><button class="btn" id="oprev">◀ 이전</button><span id="opos"></span><button class="btn" id="onext">다음 ▶</button></div>'''
    return bar + '<div class="cards" id="cards">' + ''.join(qcard(q, i) for i, q in enumerate(Q)) + '</div><div class="panel" id="jbempty" style="display:none">조건에 맞는 문항이 없습니다.</div>'

def sec_label(lec, s):
    m = re.fullmatch(r'(\d+)(?:-(\d+))?', s['rng'])
    if not m: return s['rng'], []
    a = int(m.group(1)); b = int(m.group(2) or a)
    if a > 100: return '별도 파일', [('REP2', p - 100) for p in range(a, b + 1)]
    if a == 0: return '필기본', []
    return ('p.%d' % a) if a == b else ('p.%d–%d' % (a, b)), [(lec['k'], p) for p in range(a, b + 1)]
def view_lec():
    h = ['<div class="pills" id="lecpills">' + ''.join(f'<button class="tg{" on" if i == 0 else ""}" data-lec="{l["k"]}">{esc(l["title"])}</button>' for i, l in enumerate(LECT)) + '<button class="btn sm" id="lopen">모두 펼치기</button><button class="btn sm" id="lclose">모두 접기</button></div>']
    for i, lec in enumerate(LECT):
        h.append(f'<div class="lecwrap{" on" if i == 0 else ""}" data-k="{lec["k"]}"><div class="lhead"><div class="en serif">{esc(lec["title"])}</div><div class="ko">{esc(lec["prof"])} 교수님 · 출처 {esc(lec["file"])}</div>{"".join(f"<p>{n}</p>" for n in lec["notes"])}</div>')
        for j, s in enumerate(lec['secs']):
            ids = [x for x in s['jb'] if x in QMAP]; mx = max([len(QMAP[x]['yrs']) for x in ids] or [0])
            lab, pgs = sec_label(lec, s)
            pg = ''.join(f'<button class="cite" data-k="{k}" data-p="{p}">p.{p}</button>' for k, p in pgs if f'{k}-{p}' in IMG['lec'])
            norm = [it for it in s['items'] if not it['em']]; emp = [it for it in s['items'] if it['em']]
            ychips = ''
            if ids:
                ys = sorted({y for x in ids for y in QMAP[x]['yrs']}, reverse=True)
                ychips = f'<span class="chip yr n{min(mx,3)}">기출 {len(ids)}문항 · {"·".join(YR(y)[2:] for y in ys)}년</span>'
            h.append(f'<article class="tc {heat(mx)}" id="t-{lec["k"]}-{j}"><div class="thead" data-ttog="1"><span class="badge">{lab}</span><div class="tt"><div class="en serif">{esc(s["title"])}</div><div class="tchips">{ychips}{"<span class=chip\x20emc>💬 교수 강조</span>" if emp else ""}</div></div><span class="car">▶</span></div><div class="tbody">')
            if emp: h.append(f'<div class="box prof"><div class="bt">💬 교수님 강조</div><ul>{"".join(f"<li>{it["h"]}</li>" for it in emp)}</ul></div>')
            if norm: h.append(f'<ul class="pts">{"".join(f"<li>{it["h"]}</li>" for it in norm)}</ul>')
            if ids:
                li = ''.join(f'<li><button class="jbchip{" rep" if len(QMAP[x]["yrs"]) >= 2 else ""}" data-go="{x}">{"·".join(YR(y) for y in QMAP[x]["yrs"])}년</button> {esc(QMAP[x]["short"])}</li>' for x in ids)
                h.append(f'<div class="box exam"><div class="bt">⭐ 여기서 나온 기출 <span class="small">(눌러서 문제·해설로 이동)</span></div><ul>{li}</ul></div>')
            if pg: h.append(f'<div class="pgrow"><span class="small">슬라이드 원본</span>{pg}</div>')
            h.append('</div></article>')
        h.append('</div>')
    return ''.join(h)

def view_sum():
    h = ['<div class="panel"><div class="bt">기출 한눈표</div><div class="small">현 교수 기출과 정필훈 중 겹치는 문제를 강의 순서대로 한 표에 모았습니다. ‘답 핵심’은 JB 답 원문의 앞부분입니다. HUB의 자동 빈칸(표) 기능으로 답 열을 가리고 복습할 수 있습니다.</div></div>']
    order = [l['k'] for l in LECT] + ['']
    for k in order:
        rows = [q for q in Q if q['tier'] != 'C' and q['lk'] == k]
        if not rows: continue
        rows.sort(key=lambda q: (-len(q['yrs']), -(q['yrs'][0] if q['yrs'] else 0)))
        title = LECTITLE.get(k, '강의자료에 대응 쪽 없음')
        tr = ''
        for q in rows:
            qt, at = split_text(q)
            at = re.sub(r'^\s*\[?답\]?\s*[:：)]?\s*', '', at.strip())
            at = re.split(r'\n\s*(참고|해설)\s*[:：)]', at)[0]
            at = ' / '.join(x.strip() for x in at.split('\n') if x.strip())[:260]
            n = len(q['yrs'])
            tr += f'<tr class="{heat(n)}"><th><span class="chip yr n{min(n,3)}">{"·".join(YR(y)[2:] for y in q["yrs"])}</span></th><td class="qs">{golink(q["id"], esc(q["short"]))}</td><td>{esc(at)}</td></tr>'
        h.append(f'<div class="tblwrap"><div class="tbt serif">{esc(title)}</div><table class="sum"><thead><tr><th style="width:74px">출제연도</th><th style="width:34%">문제</th><th>답 핵심 (JB 원문)</th></tr></thead><tbody>{tr}</tbody></table></div>')
    return ''.join(h)

def view_tbl():
    h = ['<div class="pills" id="tblpills"><button class="tg on" data-tk="">전체</button>' + ''.join(f'<button class="tg" data-tk="{l["k"]}">{esc(l["title"])}</button>' for l in LECT if any(t['k'] == l['k'] for t in TABLES)) + '</div>']
    for t in TABLES:
        head = ''.join(f'<th>{c}</th>' for c in t['head'])
        body = ''.join('<tr>' + ''.join((f'<th>{c}</th>' if i == 0 else f'<td>{c}</td>') for i, c in enumerate(r)) + '</tr>' for r in t['rows'])
        h.append(f'<div class="tblwrap" data-k="{t["k"]}"><div class="tbt serif">{esc(t["title"])}</div><div class="tscroll"><table class="cmp"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>{"".join(f"<div class=note>{n}</div>" for n in t["notes"])}<div class="pgrow"><span class="small">출처</span>{t["src"]}</div></div>')
    return ''.join(h)

def view_pred():
    ks = []
    for p in PRED:
        if p['k'] not in ks: ks.append(p['k'])
    h = ['<div class="panel"><div class="bt">예상문제 %d개</div><div class="small">실제 기출이 아닙니다. 문제와 답은 모두 받은 강의자료의 문장에서만 만들었고, 근거 유형(짤 변형 / 미출제 / 교수 강조)과 출처 쪽을 붙였습니다.</div></div>' % len(PRED),
         '<div class="pills" id="predpills"><button class="tg on" data-pk="">전체</button>' + ''.join(f'<button class="tg" data-pk="{k}">{esc(LECTITLE.get(k, k))}</button>' for k in ks) + '<button class="btn sm" id="popen">답 모두 펼치기</button></div>']
    for i, p in enumerate(PRED):
        rel = ''
        if p['b'] and p['b'] in QMAP: r = QMAP[p['b']]; rel = f'<button class="jbchip" data-go="{r["id"]}">관련 기출 {"·".join(YR(y) for y in r["yrs"])}년 · {esc(r["short"])}</button>'
        h.append(f'<article class="pc" data-k="{p["k"]}"><div class="meta"><span class="chip cmp">예상</span><span class="chip">{esc(LECMAP[p["k"]][1])}</span><span class="chip n1">{esc(p["t"])}</span>{rel}</div><div class="pq">{p["q"]}</div><div class="acts"><button class="btn pri" data-tog="1">답 보기</button></div><div class="ans"><div class="box jbans"><div class="pre2">{p["a"]}</div></div></div></article>')
    return ''.join(h)

def view_led():
    A_ = [q for q in Q if q['tier'] == 'A']
    seen = set(); rep = []
    for q in sorted([q for q in Q if q['tier'] != 'C' and len(q['yrs']) >= 2], key=lambda q: (-len(q['yrs']), -q['yrs'][0])):
        if q.get('pair') in seen: continue
        seen.add(q['id']); rep.append(q)
    profs = S.PROF_ORDER; yrs = sorted({y for q in Q if q['tier'] != 'C' for y in q['yrs']}, reverse=True)[:8]
    h = [f'<div class="panel"><div class="bt">수록 현황</div><div>카드 <b>{len(Q)}</b>개 = 현 교수 기출 {len(A_)} + {S.TIERS['B']} {sum(1 for q in Q if q["tier"]=="B")} + {S.TIERS['C']} {sum(1 for q in Q if q["tier"]=="C")}. 아래 대조표의 모든 JB 블록은 ‘카드’ 또는 ‘중복(같은 문제의 다른 수록본)’으로 연결되어 있고, ‘미복원’은 JB 원문 표기 그대로입니다.</div></div>',
         '<div class="panel"><div class="bt">연도 표기 규칙</div><div class="small">① 문제 옆 괄호의 연도를 모두 넣습니다. ② 괄호에 빠져 있어도 그 문항이 실린 <b>연도 칸</b>은 반드시 넣습니다. ③ 다른 연도 칸에 같은 문제가 또 있으면 그 연도도 더합니다. ④ 실리지 않은 해는 절대 붙이지 않습니다. ⑤ 2025년 시험 문항은 아직 없습니다 — 받은 JB 중 가장 최신본(25판)이 2025년 시험 전에 만들어졌기 때문입니다.</div></div>']
    t = ''.join(f'<tr><th>{p}</th>' + ''.join(f'<td>{sum(1 for q in A_ if q["prof"]==p and y in q["yrs"]) or ""}</td>' for y in yrs) + f'<td>{sum(1 for q in A_ if q["prof"]==p and len(q["yrs"])>=2)}</td></tr>' for p in profs)
    h.append(f'<div class="tblwrap"><div class="tbt serif">교수별 × 출제연도 문항 수</div><table class="cmp"><thead><tr><th>교수</th>{"".join(f"<th>{YR(y)}</th>" for y in yrs)}<th>2회 이상 반복</th></tr></thead><tbody>{t}</tbody></table></div>')
    t = ''.join(f'<tr><th>{" · ".join(YR(y) for y in q["yrs"])}</th><td>{len(q["yrs"])}회</td><td>{esc(q["prof"])}</td><td>{golink(q["id"], esc(q["short"]))}</td><td>{esc(q["jbtag"] or "없음")}</td></tr>' for q in rep)
    h.append(f'<div class="tblwrap"><div class="tbt serif">반복 출제 문항 {len(rep)}개</div><table class="cmp"><thead><tr><th>출제연도</th><th>횟수</th><th>교수</th><th>문항</th><th>JB 괄호</th></tr></thead><tbody>{t}</tbody></table></div>')
    for ed in A.NPAGES:
        R = [r for r in LEDGER if r['ed'] == ed]
        def st(r):
            if r['st'] == 'card': return '카드 ' + golink(r['to'][0], '열기')
            if r['st'] == 'dup': return '중복 → ' + ', '.join(golink(x, esc(QMAP[x]['short'][:16])) for x in r['to'])
            return 'JB에 미복원으로 표기' if r['st'] == 'lost' else '원본 쪽 참조'
        t = ''.join(f'<tr><td>{esc(r["sec"])}</td><td>{esc(r["num"])}</td><td><button class="link" data-jb="{ed}-{r["pg"]}">{r["pg"]}</button></td><td>{esc(r["first"])}</td><td>{st(r)}</td></tr>' for r in R)
        h.append(f'<details class="tblwrap"><summary class="tbt serif">JB {ed}판 대조표 — 블록 {len(R)}개</summary><table class="cmp"><thead><tr><th>연도 칸</th><th>번호</th><th>쪽</th><th>첫 줄</th><th>처리</th></tr></thead><tbody>{t}</tbody></table></details>')
    h.append('<details class="tblwrap"><summary class="tbt serif">학습부 멘트 원문</summary>' + ''.join(f'<div class="oh">JB {e}판</div><div class="pre">{esc(MENT[e])}</div>' for e in A.NPAGES) + '</details>')
    h.append('<div class="panel"><div class="bt">JB 원본 쪽</div><div class="small">그림·밑줄·굵은 글씨까지 원본 그대로 확인하는 용도입니다.</div>' + ''.join(f'<div class="oh">JB {e}판</div><div class="pggrid">' + ''.join(f'<button class="btn sm" data-jb="{e}-{p}">{p}</button>' for p in range(1, n + 1)) + '</div>' for e, n in A.NPAGES.items()) + '</div>')
    return ''.join(h)

if __name__ == '__main__':
    VIEWS = [('lec', '📖 강의 정리', view_lec), ('jb', '📝 JB 문제', view_jb), ('sum', '🗂 기출 한눈표', view_sum), ('tbl', '📊 비교표', view_tbl), ('pred', '✍️ 예상문제', view_pred), ('led', '📚 기출 대장·원본', view_led)]
    nav = ''.join(f'<button data-t="{k}" class="{"on" if i == 0 else ""}">{n}<span class="kbd">{i+1}</span></button>' for i, (k, n, _) in enumerate(VIEWS))
    secs = ''.join(f'<section class="view{" on" if i == 0 else ""}" id="v-{k}">{f()}</section>' for i, (k, n, f) in enumerate(VIEWS))
    stats = f'<span class="hchip">기출 {len(Q)}문항</span><span class="hchip">2회 이상 {sum(1 for q in Q if q["tier"]!="C" and len(q["yrs"])>=2)}</span><span class="hchip">강의 {len(LECT)}개 정리</span><span class="hchip">비교표 {len(TABLES)}</span><span class="hchip">예상 {len(PRED)}</span>'
    tpl = open(DIR + '/template2.html', encoding='utf-8').read()
    imgjs = 'const IMG=' + json.dumps({'jb': IMG['jb'], 'lec': IMG['lec']}, ensure_ascii=False).replace('</', '<\\/') + ';const LECNAME=' + json.dumps({k: v[1] for k, v in LECMAP.items()}, ensure_ascii=False) + ';const NPAGES={"25":16,"24":20,"23":28};'
    out = tpl.replace('<!--NAV-->', nav).replace('<!--STATS-->', stats).replace('<!--VIEWS-->', secs).replace('/*__IMG__*/', imgjs)
    open(J.work('IMPL', 'build2_view.html'), 'w', encoding='utf-8').write(out)
    txt = re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]+>', '', out, flags=re.S)
    print('size MB', round(len(out.encode()) / 1e6, 2), '| visible text chars', len(txt), '| cards', len(Q), '| tables', len(TABLES))
