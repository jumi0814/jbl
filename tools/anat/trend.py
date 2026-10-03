import re, html
esc = lambda s: html.escape(str(s), quote=True)
YR = lambda y: '20%02d' % y
def fmt_of(q):
    """문제 형식: JB 24판 라벨 → 문두 단서 순으로 판정"""
    lab = (q.get('lab24') or '')
    stem = ' '.join(q['text'].split('\n')[:4])
    src = lab + ' ' + stem
    if re.search(r'T/F|\(T\)|\(F\)|옳으면 T', src): return 'T/F'
    if re.search(r'빈칸|괄호|\(\s*\)|\(\d\.\s*\)', src) and '고르' not in src: return '빈칸'
    if re.search(r'객관식|고르(시오|세요|라)|모두 골라|맞는 것|옳은 것|아닌 것|틀린 것', src): return '객관식'
    if re.search(r'단답|쓰시오|쓰세요|쓰고|약자|무엇|몇|시기는|각도', src) and not re.search(r'서술|설명|나열|기술|장단점|이유', src): return '단답형'
    if re.search(r'서술|설명|나열|기술|장단점|이유|과정|목적|한계|단점|장점|특징|종류', src): return '서술형'
    return '단답형'
def jb_mark(q):
    src = (q.get('lab24') or '') + ' ' + ' '.join(q['text'].split('\n')[:4])
    if '반짤반탈' in src: return '반짤반탈'
    if re.search(r'\(탈\)|형 탈|\s탈\b|탈,', src): return '탈'
    if re.search(r'\(짤\)|형 짤|\s짤\b|짤,', src): return '짤'
    return ''
def analyze(Q, Q2CARD, LEC, PROF_COVER):
    """PROF_COVER: {교수: 자료가 커버하는 가장 이른 시험연도} — 그 해의 문항은 짤/탈 판정 불가(기준선)"""
    by_card = {}
    for q in Q:
        if q['tier'] == 'C': continue
        c = Q2CARD.get(q['id'])
        if c: by_card.setdefault(c, []).append(q)
    cardP = {(L['k'], j): any(b[0] == 'P' for b in c['body']) for L in LEC for j, c in enumerate(L['cards'])}
    for q in Q:
        if q['tier'] == 'C' or not q['yrs']: q['st'] = None; continue
        prof = (q['prof'] or '').split('(')[0]; base = PROF_COVER.get(prof, 0)
        app = []
        for y in sorted(q['yrs']):
            if y <= base: app.append({'y': y, 'kind': '기준선'}); continue
            if any(y2 < y for y2 in q['yrs']): app.append({'y': y, 'kind': '짤', 'from': max(y2 for y2 in q['yrs'] if y2 < y)}); continue
            c = Q2CARD.get(q['id']); prior = False
            if c:
                for q2 in by_card.get(c, []):
                    if q2 is not q and any(y2 < y for y2 in q2['yrs']): prior = True
            app.append({'y': y, 'kind': '탈', 'tal': '변형' if prior else '새영역', 'emph': bool(c and cardP.get(c))})
        q['st'] = {'fmt': fmt_of(q), 'mark': jb_mark(q), 'app': app, 'latest': app[-1]}
    return
def summarize(qs, prof=None):
    """문항 목록 → 연도별 짤/탈·형식 집계"""
    years = {}
    for q in qs:
        if not q.get('st'): continue
        for a in q['st']['app']:
            d = years.setdefault(a['y'], {'n': 0, 'jjal': 0, 'tal': 0, 'base': 0, 'var': 0, 'new': 0, 'emph': 0, 'fmt': {}})
            d['n'] += 1
            if a['kind'] == '짤': d['jjal'] += 1
            elif a['kind'] == '탈':
                d['tal'] += 1; d['var' if a['tal'] == '변형' else 'new'] += 1
                if a.get('emph'): d['emph'] += 1
            else: d['base'] += 1
            if a['y'] == q['st']['latest']['y']: d['fmt'][q['st']['fmt']] = d['fmt'].get(q['st']['fmt'], 0) + 1
    return dict(sorted(years.items(), reverse=True))
def ratio_word(r):
    if r is None: return '판정 불가'
    return '완짤형' if r >= 0.6 else ('반짤반탈' if r >= 0.3 else '탈형')
def fmt_str(fm):
    if not fm: return '—'
    tot = sum(fm.values()); return ' · '.join(f'{k} {v}' for k, v in sorted(fm.items(), key=lambda x: -x[1]))
def years_html(S, limit=6):
    if not S: return '<span class="small">기출 없음</span>'
    cells = []; items = list(S.items()); older = items[limit:]; items = items[:limit]
    for y, d in items:
        if d['base']: cells.append(f'<span class="ycell base"><b>{YR(y)}</b> {d["n"]}문항 <i>(기준선 — 이전 자료 없음)</i></span>'); continue
        judged = d['jjal'] + d['tal']
        tl = f' (변형 {d["var"]} · 새 영역 {d["new"]})' if d['tal'] else ''
        cells.append(f'<span class="ycell"><b>{YR(y)}</b> {d["n"]}문항 · 짤 <b class="cj">{d["jjal"]}</b> / 탈 <b class="ct">{d["tal"]}</b>{tl}</span>')
    if older:
        on = sum(d['n'] for _, d in older); oj = sum(d['jjal'] for _, d in older); ot = sum(d['tal'] for _, d in older)
        rng_ = YR(older[-1][0]) if older[-1][0] == older[0][0] else f'{YR(older[-1][0])}~{YR(older[0][0])}'
        cells.append(f'<span class="ycell base"><b>{rng_}</b> {on}문항 · 짤 {oj} / 탈 {ot}{" (기준선 포함)" if any(d["base"] for _, d in older) else ""}</span>')
    return ''.join(cells)
def tendency_text(S, name, ment='', short=False):
    """데이터에서 규칙으로 뽑는 경향 문장 + 공부 전략(' · '로 이은 문자열). 항목 목록이 필요하면 tendency_parts"""
    parts, strat = tendency_parts(S, name, ment)
    return (' / '.join(parts), ' · '.join(strat))
def latest_ratio(S):
    """최근 판정 가능한 해의 짤 비율(표본 3 미만이면 판정 가능한 해 합산) — 판정 불가면 None"""
    ys = [y for y, d in S.items() if not d['base']]
    if not ys: return None
    L = S[ys[0]]; nL = L['jjal'] + L['tal']
    if nL >= 3 or len(ys) == 1: return L['jjal'] / nL if nL else None
    n = sum(S[y]['jjal'] + S[y]['tal'] for y in ys)
    return sum(S[y]['jjal'] for y in ys) / n if n else None
def prof_line(name, S):
    """과목 홈 교수별 요약 한 줄: '서병무 · 최근 2024 16문항 짤 11/탈 5 → 완짤형' (JB 통계만 · % 없음)"""
    ys = [y for y, d in S.items() if not d['base']]
    if not S: return f'{name} · 기출 없음'
    if not ys:
        y = next(iter(S)); return f'{name} · {YR(y)} {S[y]["n"]}문항 (기준선 — 짤/탈 판정 불가)'
    y = ys[0]; d = S[y]; r = latest_ratio(S)
    return f'{name} · 최근 {YR(y)} {d["n"]}문항 짤 {d["jjal"]}/탈 {d["tal"]}{pooled(S)} → {ratio_word(r)}'   # % 없음(사용자 09-29)
def pooled(S):
    """ux4 B20 최근 해 표본이 3 미만이라 판정 가능한 해를 합산했으면 그 사실과 합산 수를 드러냄(최근 해 숫자와 판정이 반대로 읽히지 않게) — 아니면 ''"""
    ys = [y for y, d in S.items() if not d['base']]
    if len(ys) < 2: return ''
    L = S[ys[0]]
    if L['jjal'] + L['tal'] >= 3: return ''
    j = sum(S[y]['jjal'] for y in ys); n = j + sum(S[y]['tal'] for y in ys)
    return f' · 표본이 적어 누적 짤 {j}/{n}'
def tendency_parts(S, name, ment=''):
    """(경향 문장 목록, 공부 전략 항목 목록)"""
    ys = [y for y, d in S.items() if not d['base']]
    if not ys:
        return (['자료가 커버하는 첫 해의 기출만 있어 짤/탈을 판정할 수 없음(그 해 문항은 "기준선")'], ['기출은 전부 풀되 정리본 전체를 훑을 것 — 이 문항들이 다음 해의 짤 후보'])
    latest = ys[0]; L = S[latest]; nL = L['jjal'] + L['tal']
    rL = L['jjal'] / nL if nL else None
    tot_j = sum(S[y]['jjal'] for y in ys); tot_t = sum(S[y]['tal'] for y in ys); n = tot_j + tot_t
    r = rL if (nL >= 3 or len(ys) == 1) else (tot_j / n if n else None)
    traj = ' → '.join(f'{YR(y)[2:]}년 짤 {S[y]["jjal"]}/{S[y]["jjal"]+S[y]["tal"]}' for y in sorted(ys)[-5:] if S[y]['jjal'] + S[y]['tal'])   # 사용자 09-29 '퍼센트 필요 없어' — 해마다 짤 수/판정 문항 수
    var = sum(S[y]['var'] for y in ys); new = sum(S[y]['new'] for y in ys); emph = sum(S[y]['emph'] for y in ys)
    rising = len(ys) >= 2 and all((S[a]['jjal']/(S[a]['jjal']+S[a]['tal']) if S[a]['jjal']+S[a]['tal'] else 0) <= (S[b]['jjal']/(S[b]['jjal']+S[b]['tal']) if S[b]['jjal']+S[b]['tal'] else 0) for a, b in zip(sorted(ys), sorted(ys)[1:]))
    word = ratio_word(r)
    if nL >= 3 or len(ys) == 1: parts = [f'최근 {YR(latest)}년 {L["n"]}문항 = 짤 {L["jjal"]} · 탈 {L["tal"]} → <b>{word}</b>']
    else: parts = [f'최근 {YR(latest)}년은 {L["n"]}문항(짤 {L["jjal"]} · 탈 {L["tal"]})으로 표본이 적어 판정 가능한 해를 합산: 짤 {tot_j}/{n} → <b>{word}</b>']
    if len(ys) > 1: parts.append('짤 추이 ' + traj + (' — 기출이 쌓이면서 짤이 늘어나는 중' if rising and rL and rL >= 0.5 and nL >= 3 else ''))
    if tot_t:
        lv, ln_ = L['var'], L['new']
        if L['tal'] >= 2:
            if lv > ln_: parts.append(f'{YR(latest)}년 탈 {L["tal"]}문항 = <b>이미 나온 카드에서 다른 항목을 묻는 변형</b> {lv} · 새 영역 {ln_} (누적 변형 {var} · 새 영역 {new})')
            elif ln_ > lv: parts.append(f'{YR(latest)}년 탈 {L["tal"]}문항 = <b>아직 안 나온 카드에서 새로</b> {ln_} · 변형 {lv} (누적 변형 {var} · 새 영역 {new})')
            else: parts.append(f'{YR(latest)}년 탈 {L["tal"]}문항 = 변형 {lv} · 새 영역 {ln_} (누적 변형 {var} · 새 영역 {new})')
        else:
            if var > new: parts.append(f'누적 탈 {tot_t}문항은 대부분 <b>이미 나온 카드에서 다른 항목을 묻는 변형</b>(변형 {var} · 새 영역 {new})')
            elif new > var: parts.append(f'누적 탈 {tot_t}문항은 <b>아직 안 나온 카드에서 새로</b> 내는 쪽(새 영역 {new} · 변형 {var})')
            else: parts.append(f'누적 탈 {tot_t}문항은 변형·새 영역 반반({var}:{new})')
        le = L['emph']
        if L['tal'] >= 2 and le >= L['tal'] * 0.5: parts.append(f'{YR(latest)}년 탈 중 {le}문항이 <b>교수 강조 쪽</b>에서 출제')
        elif emph and emph >= tot_t * 0.5: parts.append(f'누적 탈 중 {emph}문항이 <b>교수 강조 쪽</b>에서 출제')
    parts.append('형식 ' + fmt_str(L['fmt']))
    strat = []
    if r is not None and r >= 0.6: strat.append('JB 문항을 답까지 그대로 쓸 수 있게 외우는 것이 1순위')
    elif r is not None and r >= 0.3: strat.append('기출은 답까지 외우고, 같은 카드의 다른 항목(‘주변’·⚡ 암기 줄)까지 넓게')
    else: strat.append('기출 암기만으로는 부족 — 정리본을 처음부터 끝까지 읽고 카드별 🔑·⚡를 모두 챙길 것')
    uv, un = (L['var'], L['new']) if L['tal'] >= 2 else (var, new)
    if tot_t and uv > un: strat.append('기출이 걸린 카드는 항목 전체를 통째로(같은 슬라이드에서 다른 것을 물음)')
    if tot_t and un >= uv: strat.append('아직 안 나온 카드도 버리지 말 것')
    ue = L['emph'] if L['tal'] >= 2 else emph
    if ue and tot_t and ue >= (L['tal'] if L['tal'] >= 2 else tot_t) * 0.5: strat.append('💬 교수 강조 카드를 먼저')
    fm = L['fmt']
    if fm:
        top = max(fm, key=fm.get)
        strat.append({'서술형': '서술형: 항목 수와 번호(①②③)를 정확히 — 암기 줄을 소리 내어 나열', '객관식': '객관식: 절대/상대·이상/이하 같은 대비 쌍이 함정 — 비교표로', '빈칸': '빈칸: 정의 문장을 통째로 — 용어↔정의 양방향', 'T/F': 'T/F: 한 문제에 여러 카드가 섞임 — 수치·조건(mm, 주, %)을 정확히', '단답형': '단답형: 수치·시기·이름을 즉답 — ⚡ 암기 줄 반복'}[top])
    if ment: parts.append('학습부 멘트 — ' + ment)
    return (parts, strat)
def short_line(S):
    ys = [y for y, d in S.items() if not d['base']]
    if not S: return '기출 없음'
    if not ys:
        y = next(iter(S)); return f'{YR(y)}년 {S[y]["n"]}문항 (기준선)'
    y = ys[0]; d = S[y]
    return f'{YR(y)}년 {d["n"]}문항 · 짤 {d["jjal"]} / 탈 {d["tal"]}{pooled(S)} → {ratio_word(latest_ratio(S))} · {fmt_str(d["fmt"])}'   # ux4 B20 교수 줄과 같은 판정 규칙(latest_ratio)
def prof_cells(S):
    """ux4 B3-3 과목 홈 교수별 출제 경향 표 한 행 — (최근 해 'YYYY · n문항', '짤 / 탈', 판정, 짤 / 문항(합산이면 '표본이 적어 누적 짤 j/n'), 최근 해 형식) · prof_line과 같은 판정 규칙(latest_ratio)"""
    if not S: return ('기출 없음', '—', '—', '—', '')
    ys = [y for y, d in S.items() if not d['base']]
    if not ys:
        y = next(iter(S)); return (f'{YR(y)} · {S[y]["n"]}문항', '기준선', '판정 불가', '—', fmt_str(S[y]['fmt']))
    y = ys[0]; d = S[y]; r = latest_ratio(S); pl = pooled(S)
    return (f'{YR(y)} · {d["n"]}문항', f'{d["jjal"]} / {d["tal"]}', ratio_word(r), (f'{d["jjal"]}/{d["jjal"] + d["tal"]}' if d['jjal'] + d['tal'] else '—') + (f' <small>{pl[3:]}</small>' if pl else ''), fmt_str(d['fmt']))   # 짤 / 문항(% 없음 — 사용자 09-29)

