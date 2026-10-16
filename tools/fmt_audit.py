"""문항 형식 점검표 — trend.fmt_of(빌드가 '교수별 출제 경향·형식'에 쓰는 분류기)가 문항마다 무엇으로 판정했는지 한눈에 보고, 판정이 수상한 문항을 이유와 함께 뽑는다(정보용 — 고치지 않음 · exit 0, 과목 이름이 틀릴 때만 2).
사용: .venv/bin/python tools/fmt_audit.py [SID…] [--md PATH]
  SID 기본 = OMS1 CONS IMPL ANAT GERI PHARM ESTH
  --md 기본 = work/_tmp/fmt<YY>/<SID>.md (YY = 팩의 가장 최근 시험연도 + 1, 예 26)
       PATH에 '{SID}'가 있으면 과목마다 바꿔 넣음 · 폴더(이미 있거나 '/'로 끝남)면 <PATH>/<SID>.md · 과목 하나면 그 파일 · 여러 과목 + 파일 하나면 한 파일에 이어 씀
입력: 문항 글(text·lab24)은 build4와 같게 tools/<sid>/assemble.py의 Q(빌드가 fmt_of에 넘기는 그 dict) — 불러오기에 실패하면 팩 카드(.qtext + 답 section.ab.jbans)로 재구성.
      강의·출제연도·연도별 출제 교수·등급은 지금 팩 docs/packs/<SID>.js의 <article data-lec·data-yrs·data-yp·data-prof·data-tier>.
집계 대상 = build4 trend.analyze와 같음(등급 C 제외 · 출제연도 있는 문항). 표의 칸 = 문항이 실린 해마다 1(사이트 경향표는 문항의 최근 해에만 형식을 셈 — 아래 머리말에 적음).
출력: ① 교수 × 시험연도 × 형식 표(교수 = 그 해 출제 교수 data-yp, 없으면 data-prof · 연도 최근 순) ② 문항 → 강의 · 형식 · 연도 · 출제 교수 ③ 의심 목록(이유 — 다른 형식일 가능성) ④ 참고(추정에 기댄 판정 — 의심 수에 안 셈)
      화면: 의심 문항 한 줄씩('  ? ') · 과목마다 '<SID>: 문항 n · 형식 {..} · 의심 k' · 끝에 RESULT PASS"""
import os, re, sys, io, html, contextlib, importlib.util, traceback
TOOLS = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TOOLS)
import jblpaths as J

SIDS = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
FMTS = ['객관식', 'T/F', '빈칸', '단답형', '서술형']   # fmt_of가 돌려주는 값(이 밖의 값이 나오면 뒤에 덧붙임)
SUBDIRS = {os.path.join(TOOLS, s.lower()) for s in SIDS}

# ---------- 불러오기 ----------
def load_trend(sid):
    """그 과목 build4가 쓰는 tools/<sid>/trend.py(7과목 같은 사본)"""
    p = os.path.join(TOOLS, sid.lower(), 'trend.py')
    sp = importlib.util.spec_from_file_location(f'_fmt_trend_{sid}', p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m

def _clear_subject_modules():
    """과목마다 같은 이름(assemble·subject·emph·parse_*…)이라 앞 과목 모듈을 비움(jbfig.load_assemble과 같은 방식)"""
    for k, m in list(sys.modules.items()):
        f = getattr(m, '__file__', None)
        if f and os.path.dirname(os.path.abspath(f)) in SUBDIRS: del sys.modules[k]

def load_assemble(sid):
    """build4처럼 tools/<sid>/assemble.py를 불러 Q(문항 dict 목록)를 돌려줌 · 실패하면 (None, 오류 한 줄)"""
    d = os.path.join(TOOLS, sid.lower()); _clear_subject_modules(); old = list(sys.path); sys.path.insert(0, d); buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            import assemble as A
        return A.Q, ''
    except (Exception, SystemExit) as e:   # 정보 도구라 멈추지 않음 → 팩 글로
        return None, f'{type(e).__name__}: {str(e)[:160]}'
    finally:
        sys.path[:] = old; _clear_subject_modules()   # assemble이 스스로 넣는 tools/<sid>도 빼고 다음 과목으로

def _attrs(card_html):
    m = re.search(r'<article\b[^>]*>', card_html)
    return {k: html.unescape(v) for k, v in re.findall(r'(data-[\w-]+)="([^"]*)"', m.group(0))} if m else {}

def year_profs(a):
    """data-yp '25:교수 24:교수(…)' → {25: '교수', …} (공백 뒤 'NN:'에서 나눔) · 없으면 data-prof"""
    out = {}
    for part in re.split(r'\s+(?=\d\d:)', (a.get('data-yp') or '').strip()):
        y, _, p = part.partition(':')
        if y.isdigit() and p.strip(): out[int(y)] = p.strip()
    return out

NOANS = 'JB에 답 표기가 따로 없음'
def pack_parts(card_html):
    """팩 카드 → (문제 줄, JB 답 줄) — 답 줄은 section.ab.jbans의 .lines(머리 h5 빼고 · '답:' 라벨 그대로)"""
    from bs4 import BeautifulSoup
    s = BeautifulSoup(card_html, 'html.parser')
    qt = s.select_one('.qtext'); ab = s.select_one('section.ab.jbans')
    ql = [x.get_text(' ', strip=True) for x in qt.select('.ln')] if qt else []
    if qt and not ql: ql = [l for l in qt.get_text('\n').split('\n') if l.strip()]
    box = ab.select_one('.lines') if ab else None
    al = [x.get_text(' ', strip=True) for x in box.select('.ln')] if box else []
    return [l for l in ql if l], [l for l in al if l and NOANS not in l]

def pack_text(card_html, T):
    """팩 카드 → fmt_of 입력 text(문제 줄 + JB 답 · 답 첫 줄에 '답:' 표시가 없으면 붙임) — assemble을 못 불러올 때만"""
    ql, al = pack_parts(card_html)
    if al and not T.ANS.match(al[0]): al = ['답: ' + al[0]] + al[1:]
    return '\n'.join(ql + al)

def load(sid, T):
    pp = os.path.join(J.DOCS, 'packs', f'{sid}.js')
    P = J._load_js(pp); C = P.get('cards', {}); LN = P.get('lecname', {}) or {}
    Q, err = load_assemble(sid); src = 'assemble'
    QM = {q['id']: q for q in (Q or [])}
    rows, notes = [], []
    if Q is None: src = 'pack'; notes.append(f'assemble 불러오기 실패({err}) → 팩 카드 글(.qtext + JB 답)로 재구성')
    miss = [i for i in C if Q is not None and i not in QM]
    if miss: notes.append(f'팩에만 있는 문항 {len(miss)}개(팩 글로 재구성): {" ".join(miss[:12])}')
    extra = [i for i in QM if i not in C]
    if extra: notes.append(f'assemble에만 있는 문항 {len(extra)}개(팩에 없음 — 빌드 전?): {" ".join(extra[:12])}')
    for cid, h in C.items():
        a = _attrs(h); q0 = QM.get(cid)
        q = {'id': cid, 'text': q0['text'], 'lab24': q0.get('lab24') or ''} if q0 else {'id': cid, 'text': pack_text(h, T), 'lab24': ''}
        yrs = sorted({int(y) for y in (a.get('data-yrs') or '').split() if y.isdigit()}, reverse=True)
        yp = year_profs(a); prof = (a.get('data-prof') or (q0 or {}).get('prof') or '').strip()
        rows.append({'id': cid, 'q': q, 'from': 'assemble' if q0 else 'pack', 'tier': a.get('data-tier') or (q0 or {}).get('tier', ''),
                     'lec': a.get('data-lec') or '', 'lecname': LN.get(a.get('data-lec') or '', ''), 'yrs': yrs,
                     'yp': {y: yp.get(y) or prof or '?' for y in yrs}, 'prof': prof, 'pans': pack_parts(h)[1]})
    return P, rows, src, notes

# ---------- 의심 판정 ----------
CUE_CHOICE = re.compile(r'옳은\s*것|옳지\s*않은|아닌\s*것|틀린\s*것|T\s*/\s*F|O\s*/\s*X')
CUE_BLANK = re.compile(r'빈칸|괄호')
INLINE_CH = re.compile(r'(?:^|\s)\(?[1-5][.)]\s?')
LOOSE_CH = re.compile(r'^\s*(?:[①-⑩]|\*?\(?[1-9][.)](?!\d)|\(?[a-eA-E][.)]|[ㄱ-ㅎ]\s*[.)\-:]|[가나다라마]\s*[.)])')   # 보기 줄(느슨히 — 'ㄱ-'·'가)'·'*1)'도)
LABEL = re.compile(r'[\[(]\s*(?:서술형|단답형|객관식|객)\s*[\])]')
TF_EXPL = re.compile(r'T/F|(?<![A-Za-z])TF(?![A-Za-z])|O\s*/\s*X|\(T\)|\(F\)|옳으면 T')
SHORT_CUE = re.compile(r'단답|쓰시오|쓰세요|쓰고|약자|무엇|몇|시기는|각도')
LONG_CUE = re.compile(r'서술|설명|나열|기술|장단점|이유|과정|목적|한계|단점|장점|특징|종류|비교')
UNREC = re.compile(r'미복원|복원\s*(?:불충분|미흡|안\s*됨)')

def suspects(T, q, fmt, pans=()):
    """fmt_of 결과와 문제 부분 단서가 어긋나는 것(휴리스틱) → (의심 이유, 참고 이유)
    의심 = 다른 형식일 가능성이 큰 것 · 참고 = 판정은 맞을 듯하나 추정에 기댄 것(의심 수에 안 셈)"""
    L = T.q_lines(q); qp = ' '.join(L); lab = q.get('lab24') or ''; src4 = lab + ' ' + ' '.join(L[:4]); allq = lab + ' ' + qp
    body = re.sub(r'^\s*(?:추\s*)?\d+(?:-\d+)?\s*[.)]\s*', '', qp)
    ch = [l for l in L[1:] if T.CHOICE.match(l)]; loose = [l for l in L[1:] if LOOSE_CH.match(l)]
    inline = len(INLINE_CH.findall(body)); circ = len(re.findall(r'[①②③④⑤]', qp))
    labeled = bool(LABEL.search(src4))
    R, S = [], []
    if UNREC.search(qp) and len(re.sub(r'\(.*?\)|[\s\d.\-]', '', body)) <= 12:
        R.append(f'미복원 문항 — 형식을 알 수 없는데 {fmt}로 셈')
    elif fmt in ('단답형', '서술형') and not labeled:
        if len(ch) >= 3: R.append(f'보기 줄 {len(ch)}개인데 {fmt}')
        m = CUE_CHOICE.search(qp)
        if m: R.append(f"'{m.group(0)}' 있는데 {fmt}")
        m = CUE_BLANK.search(qp)
        if m and '고르' not in qp: R.append(f"'{m.group(0)}' 단서 있는데 {fmt}")
        if fmt == '단답형' and '?' not in qp and not re.search(r'주관식', ' '.join(L[:4])) and not SHORT_CUE.search(allq):
            R.append('형식 단서 없음(물음표·쓰시오 없음) — 기본값 단답형')
        if fmt == '서술형' and not SHORT_CUE.search(allq) and not LONG_CUE.search(allq):
            R.append('형식 단서 없음 — 서술형 근거 불명')
    if fmt == '객관식' and not ch and not loose and inline < 3 and circ < 3:
        R.append('객관식인데 번호 붙은 보기 줄 없음' + (' (보기 미복원 표기)' if re.search(r'보기\s*미복원|선지', qp) else ''))
    if fmt == '빈칸' and not re.search(r'빈칸|괄호|\(\s*\)|\(\s*\d\s*\)|\[\s*\d\s*\]|@|\(\s*(?:[ㄱ-ㅎ]|[A-E])\s*\)|_{2,}', allq):
        S.append('빈칸 표시(빈칸·괄호·( 1 )·@) 없이 빈칸 — 글자 A·B 빈칸으로 추정')
    if fmt == 'T/F' and not TF_EXPL.search(src4):
        S.append('명시 T/F 없음 — 평서문 한 문장이라 T/F로 추정')
    if pans and len(L) == len([l for l in q['text'].split('\n') if l.strip()]):
        R.append('답 표시(답:·[답]·답))를 못 찾아 JB 답까지 문제 부분으로 봄')
    return R, S

# ---------- 출력 ----------
def fmt_keys(cnt):
    return FMTS + sorted(k for k in cnt if k not in FMTS)

def yy(y): return f'{y:02d}'

def short(t, n=46):
    t = re.sub(r'\s+', ' ', t).strip(); return t if len(t) <= n else t[:n - 1] + '…'

def md_cell(t): return str(t).replace('|', '\\|').replace('\n', ' ')

def prof_str(yp):
    ps = list(dict.fromkeys(yp.values()))
    if len(ps) <= 1: return ps[0] if ps else '—'
    return ' · '.join(f'{yy(y)} {p}' for y, p in yp.items())

def audit(sid):
    T = load_trend(sid); P, rows, src, notes = load(sid, T)
    for r in rows: r['fmt'] = T.fmt_of(r['q'])
    live = [r for r in rows if r['tier'] != 'C' and r['yrs']]
    cnt = {}; tab = {}
    for r in live:
        cnt[r['fmt']] = cnt.get(r['fmt'], 0) + 1
        for y, p in r['yp'].items():
            d = tab.setdefault(p, {}).setdefault(y, {}); d[r['fmt']] = d.get(r['fmt'], 0) + 1
    for r in live: r['why'], r['soft'] = suspects(T, r['q'], r['fmt'], r['pans']); r['qp'] = ' '.join(T.q_lines(r['q']))
    sus = [r for r in live if r['why']]; soft = [r for r in live if r['soft'] and not r['why']]
    latest = max([y for r in rows for y in r['yrs']] or [0])
    return {'sid': sid, 'title': P.get('title') or sid, 'rows': rows, 'live': live, 'cnt': cnt, 'tab': tab, 'sus': sus, 'soft': soft, 'src': src, 'notes': notes, 'latest': latest}

def to_md(R):
    sid, rows, live, tab, sus = R['sid'], R['rows'], R['live'], R['tab'], R['sus']
    K = fmt_keys(R['cnt']); out = []
    nC = sum(1 for r in rows if r['tier'] == 'C'); nN = sum(1 for r in rows if r['tier'] != 'C' and not r['yrs'])
    out.append(f'# {sid} 문항 형식 점검 — {R["title"]}\n')
    out.append(f'- 분류기 `tools/{sid.lower()}/trend.py` fmt_of · 문항 글 = {"assemble Q(빌드와 같음)" if R["src"] == "assemble" else "팩 카드 재구성"} · 강의·연도·교수 = `docs/packs/{sid}.js`')
    out.append(f'- 집계 문항 {len(live)} (전체 카드 {len(rows)} · 등급 C {nC} · 출제연도 없음 {nN} 제외 — build4 trend.analyze와 같음)')
    out.append(f'- 형식: {" · ".join(f"{k} {R["cnt"][k]}" for k in K if R["cnt"].get(k))} · 의심 {len(sus)} · 참고 {len(R["soft"])}')
    out.append('- 표 칸 = 그 해 시험에 실린 문항 수(한 문항이 여러 해에 나오면 해마다 셈) · 사이트 경향표(trend.summarize)는 문항의 최근 해에만 형식을 셈')
    for n in R['notes']: out.append(f'- ⚠ {n}')
    out.append('\n## 1. 교수 × 시험연도 × 형식\n')
    out.append('| 교수 | 연도 | ' + ' | '.join(K) + ' | 계 |'); out.append('|---|---|' + '---:|' * (len(K) + 1))
    order = sorted(tab, key=lambda p: (-max(tab[p]), -sum(sum(d.values()) for d in tab[p].values()), p))
    for p in order:
        for j, y in enumerate(sorted(tab[p], reverse=True)):
            d = tab[p][y]
            out.append(f'| {md_cell(p) if j == 0 else ""} | {yy(y)} | ' + ' | '.join(str(d.get(k, '')) for k in K) + f' | {sum(d.values())} |')
    yt = {}
    for p in tab:
        for y, d in tab[p].items():
            for k, v in d.items(): yt.setdefault(y, {}).setdefault(k, 0); yt[y][k] += v
    out.append('\n연도 합계\n'); out.append('| 연도 | ' + ' | '.join(K) + ' | 계 |'); out.append('|---|' + '---:|' * (len(K) + 1))
    for y in sorted(yt, reverse=True):
        out.append(f'| {yy(y)} | ' + ' | '.join(str(yt[y].get(k, '')) for k in K) + f' | {sum(yt[y].values())} |')
    out.append('\n## 2. 문항 → 강의 · 형식 · 연도 · 출제 교수\n')
    out.append('| 문항 | 강의 | 형식 | 연도 | 출제 교수 | 문제 첫머리 |'); out.append('|---|---|---|---|---|---|')
    for r in rows:
        L = r['q']['text'].split('\n'); first = next((l for l in L if l.strip()), '')
        tag = '' if (r['tier'] != 'C' and r['yrs']) else (' (C·집계 제외)' if r['tier'] == 'C' else ' (연도 없음·집계 제외)')
        lec = f"{r['lec']} {r['lecname']}".strip() or '—'
        out.append(f"| {r['id']}{tag}{' ⚑' if r.get('why') else ''} | {md_cell(lec)} | {r['fmt']} | {' '.join(yy(y) for y in r['yrs']) or '—'} | {md_cell(prof_str(r['yp']) if r['yrs'] else (r['prof'] or '—'))} | {md_cell(short(first))} |")
    out.append(f'\n## 3. 의심 {len(sus)}\n')
    if not sus: out.append('없음')
    else:
        out.append('| 문항 | 형식 | 이유 | 문제 부분(답 앞) |'); out.append('|---|---|---|---|')
        for r in sus:
            out.append(f"| {r['id']} | {r['fmt']} | {md_cell(' / '.join(r['why']))} | {md_cell(short(r['qp'], 120))} |")
    soft = R['soft']
    out.append(f'\n## 4. 참고 — 추정에 기댄 판정 {len(soft)} (의심 수에 안 셈)\n')
    if not soft: out.append('없음')
    else:
        out.append('| 문항 | 형식 | 근거 | 문제 부분(답 앞) |'); out.append('|---|---|---|---|')
        for r in soft:
            out.append(f"| {r['id']} | {r['fmt']} | {md_cell(' / '.join(r['soft']))} | {md_cell(short(r['qp'], 120))} |")
    return '\n'.join(out) + '\n'

def md_path(arg, sid, latest):
    if not arg: return os.path.join(J.TMP, f'fmt{latest + 1:02d}', f'{sid}.md')
    if '{SID}' in arg: return arg.replace('{SID}', sid)
    if arg.endswith('/') or os.path.isdir(arg): return os.path.join(arg, f'{sid}.md')
    return arg

def main(argv):
    md = None; sids = []
    it = iter(argv)
    for a in it:
        if a == '--md': md = next(it, None)
        elif a.startswith('--md='): md = a[5:]
        elif a in ('-h', '--help'): print(__doc__); return 0
        else: sids.append(a.upper())
    sids = sids or SIDS
    bad = [s for s in sids if s not in SIDS]
    if bad: print(f'알 수 없는 과목 {bad} — {" ".join(SIDS)}'); return 2
    written = set(); lines = []
    for sid in sids:
        try: R = audit(sid)
        except Exception as e:
            print(f'{sid}: 점검 실패 {type(e).__name__}: {e}'); traceback.print_exc(limit=2); continue
        p = md_path(md, sid, R['latest']); os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        with open(p, 'a' if p in written else 'w', encoding='utf-8') as f: f.write(('\n\n' if p in written else '') + to_md(R))
        written.add(p)
        for n in R['notes']: print(f'  ⚠ {sid} {n}')
        for r in R['sus']: print(f"  ? {sid} {r['id']} [{r['fmt']}] {' / '.join(r['why'])} — {short(r['qp'], 70)}")
        K = fmt_keys(R['cnt'])
        lines.append(f"{sid}: 문항 {len(R['live'])} · 형식 {{{', '.join(f'{k} {R['cnt'][k]}' for k in K if R['cnt'].get(k))}}} · 의심 {len(R['sus'])}" + (f" (참고 {len(R['soft'])})" if R['soft'] else ''))
    for l in lines: print(l)
    for p in sorted(written): ap = os.path.abspath(p); print('  md →', os.path.relpath(ap, J.ROOT) if ap.startswith(J.ROOT + os.sep) else ap)
    print('RESULT PASS')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
