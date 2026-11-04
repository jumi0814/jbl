"""4Q 판 25 전용 내용 검사(11-04 · RULES 14) — 4Q 과목 정리본(tools/<sid>/lec_*.txt)에 25 자료에만 있는 내용이
'📜 25 기출 근거' ⭐ 줄 밖에 남았는지 본다. 읽기만 함(파일·docs를 쓰지 않음).
사용: .venv/bin/python tools/check_25only.py <SID…> [--list] [--keys K1,K2]
      SID를 안 주면 tools/quarters.py의 4q 과목.  --list = 걸린 줄 전부(기본은 강의마다 5줄)

(a) ✗ 25 전용 표시가 📜 줄 밖에 있는 줄. 📜 줄 = `E: <JB id>[,<id>…] | <YY·YY>년 <형식> "<요지>" → <JB 답> — 📜 25 기출 근거: "<25 글>" [[<25 보조 키>:<쪽>]]`
    gone  '(… 26에서 빠짐)'·'26 자료에서 빠짐'(lecparse GONE26 · 4Q엔 📜 줄 안에서도 ✗ — 📜이 대신함)
    p25   '25 p.N'·'25 자료 p.N'
    chip  [[<25 보조 키>:N]] — 보조 키 = subject.py IMG_ALIAS 중 LECMAP 이름에 '25'가 있고 '26'이 없는 키(KEY5·CR5·NK5·PN5 …)
    fig   F: <25 보조 키>:N — 📜 줄 바로 아래 F: 줄만 됨(그 기출이 그 그림을 물을 때)
    note  '25 필기'
    old   '(25: 옛 값)'
    rng   카드 쪽 범위에 옛 판 쪽('25 p.n' · 100+n — build4 gone_state와 같은 판정)
    noid  📜 줄인데 E: 머리에 JB 문항 id가 없음
    · 정보(종료 코드 영향 없음): form = 📜 줄이 'YY년 … "요지" → 답 — 📜 …' 꼴이 아님(lecparse EXAM_RE — 구조화 ⭐로 안 그려짐)
(b) 정보 — 임시 강의(LECMAP 이름에 '25'만 = 25 자료 본문 · 폴더 None = 자료 대기(SKILL B 3b))와 @UPD '25 자료 임시' 머리 유무.
    임시 강의는 25가 본문이라 (a)를 보지 않음 · 25 본문인데 머리가 없거나, LECMAP이 26인데 머리가 남았으면 QA 99 ✗(RULES 14 b).
보지 않는 줄: #LEC(파일 설명)뿐. @MAP·@G·@UPD·!·@TIP·카드 줄은 봄(화면에 보임 — '!' 자료 설명은 '25 자료(보조 키 X5) = 기출 근거로만'처럼 쓰면 안 걸림 ·
    @UPD의 빠진 25 쪽은 수만 — 쪽 글·칩 없이).
문항 id가 실제로 있는지는 check_lec가 봄. (a)가 하나라도 있으면 종료 코드 1."""
import os, re, sys, ast, importlib.util
TOOLS = os.path.dirname(os.path.abspath(__file__))
MARK = '📜 25 기출 근거'
IDRE = re.compile(r'^[A-Za-z0-9_\-]+$')
P25 = re.compile(r'(?<![\w.])25\s*(?:자료\s*)?p\.\s*\d')
NOTE25 = re.compile(r'(?<![\w.])25\s*필기')
OLD25 = re.compile(r'\(25\s*:\s')
GONE_TXT = re.compile(r'26(?: 자료)?에서 빠[짐졌]')
HEAD_TMP = re.compile(r'^@UPD\s*25 자료 임시')
GONE26_FALLBACK = r'\(([^()]{0,200}?26(?: 자료)?에서 빠[짐졌][^()]{0,200}?)\)'
EXAM_FALLBACK = r'^(?P<yr>[\d·]+년(?:\s*이전)?(?:\s*\(?\d+회\)?)?)(?P<mid>[^"“”→]{0,40}?)(?P<q>["“][^"“”]+?["”](?:의 \'[^\']+\')?)(?P<qx>(?:\s*\([^()]*\)|\s[^"“”→()]{1,14})?)(?P<arr>\s*→\s*)(?P<rest>.+)$'

def lp_patterns(d):
    """그 과목 lecparse.py에서 GONE26·EXAM_RE 정규식 글자만 꺼냄(import하면 subject를 끌어오므로 ast로) — 못 찾으면 10-27 판 사본"""
    out = {'GONE26': GONE26_FALLBACK, 'EXAM_RE': EXAM_FALLBACK}
    try:
        tree = ast.parse(open(os.path.join(d, 'lecparse.py'), encoding='utf-8').read())
        for n in tree.body:
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in out:
                v = n.value
                if isinstance(v, ast.Call) and v.args and isinstance(v.args[0], ast.Constant) and isinstance(v.args[0].value, str):
                    out[n.targets[0].id] = v.args[0].value
    except (OSError, SyntaxError):
        pass
    return re.compile(out['GONE26']), re.compile(out['EXAM_RE'])

def load_subject(sid, d):
    spec = importlib.util.spec_from_file_location(f'_subj25_{sid}', os.path.join(d, 'subject.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def old_segs(rng, npages):
    """build4 gone_state와 같은 판정 — 카드 쪽 범위 조각 중 옛 판(25) 쪽 조각"""
    bad = []
    for sg in [x.strip() for x in re.split(r'[,·]', rng or '') if x.strip()]:
        if re.fullmatch(r'2\d\s*p\.\s*\d+(?:\s*[-–~]\s*\d+)?', sg): bad.append(sg); continue
        m = re.match(r'(\d+)', sg)
        if m and int(m.group(1)) > 100 and int(m.group(1)) > (npages or 0): bad.append(sg)
    return bad

def fig_keys(line):
    ks = []
    for part in line[2:].split(','):
        pg = part.strip().partition('=')[0]
        if ':' in pg: ks.append(pg.split(':', 1)[0].strip())
    return ks

def check_lec(path, key, S, a25, gone_re, exam_re):
    """→ (걸린 줄 [(줄 번호, [종류], 글자)], 📜 줄 수, 정보 줄 [(줄 번호, 종류, 글자)])"""
    hits, info, n_ok = [], [], 0
    alt = key in (getattr(S, 'ALT_KEY', None) or {})
    chip_re = re.compile(r'\[\[(?:' + '|'.join(map(re.escape, sorted(a25, key=len, reverse=True))) + r'):') if a25 else None
    npages, prev_ok = 0, False
    for ln, raw in enumerate(open(path, encoding='utf-8'), 1):
        line = raw.rstrip('\n')
        if not line.strip(): continue
        if line.startswith('#LEC'):
            p = [x.strip() for x in line[4:].split('|')]
            try: npages = int(p[5])
            except (IndexError, ValueError): npages = 0
            prev_ok = False; continue
        kinds = []
        is_e = line.startswith('E:')
        ok = False
        if is_e and MARK in line:
            ids, bar, txt = line[2:].partition('|')
            idl = [x.strip() for x in ids.split(',') if x.strip()]
            if bar and idl and all(IDRE.match(x) for x in idl):
                ok = True; n_ok += 1
                m = exam_re.match(txt.strip())
                rest = m.group('rest') if m else ''
                if not m or not (0 <= rest.find(' — ') < rest.find('📜')):
                    info.append((ln, 'form', line))
            else: kinds.append('noid')
        if gone_re.search(line) or GONE_TXT.search(line): kinds.append('gone')
        if not ok:
            if P25.search(line): kinds.append('p25')
            if chip_re and chip_re.search(line): kinds.append('chip')
            if NOTE25.search(line): kinds.append('note')
            if OLD25.search(line): kinds.append('old')
        if line.startswith('F:') and any(k in a25 for k in fig_keys(line)) and not prev_ok: kinds.append('fig')
        if line.startswith('## ') and not alt:
            p = [x.strip() for x in line[3:].split('|')]
            if len(p) > 2 and old_segs(p[2], npages): kinds.append('rng')
        if kinds: hits.append((ln, kinds, line))
        prev_ok = ok or (prev_ok and line.startswith('F:') and 'fig' not in kinds)
    return hits, n_ok, info

KINDS = ['gone', 'p25', 'chip', 'fig', 'note', 'old', 'rng', 'noid']

def main(sids, keys_only, full):
    bad_all = 0
    for sid in sids:
        d = os.path.join(TOOLS, sid.lower())
        if not os.path.exists(os.path.join(d, 'subject.py')): print(f'✗ {sid}: tools/{sid.lower()}/subject.py 없음'); bad_all += 1; continue
        S = load_subject(sid, d); gone_re, exam_re = lp_patterns(d)
        LM = getattr(S, 'LECMAP', {}); IA = getattr(S, 'IMG_ALIAS', {})
        lab = lambda k: str((LM.get(k) or ('', ''))[1])
        a25 = {a for a in IA if '25' in lab(a) and '26' not in lab(a)}
        tot = dict.fromkeys(KINDS, 0); nlines = nlec = nok = 0; prov = []
        for k in [k for k in S.LEC_ORDER if not keys_only or k in keys_only]:
            path = os.path.join(d, f'lec_{k}.txt')
            if not os.path.exists(path): continue
            folder = (LM.get(k) or (None, ''))[0]
            src = open(path, encoding='utf-8').read()
            head = any(HEAD_TMP.match(x) for x in src.split('\n'))
            pk = '자료 대기(LECMAP 폴더 None)' if folder is None else ('25 자료 본문(LECMAP 이름 ' + lab(k) + ')' if '25' in lab(k) and '26' not in lab(k) else '')
            if pk:
                prov.append((k, pk, head)); continue
            if head: prov.append((k, '', head))   # LECMAP은 26인데 임시 머리가 남음 — (a)도 봄
            hits, n_ok, info = check_lec(path, k, S, a25, gone_re, exam_re); nok += n_ok
            for ln, ks, _ in hits:
                for x in ks: tot[x] += 1
            if hits or info or n_ok:
                kc = {x: sum(x in ks for _, ks, _ in hits) for x in KINDS}
                print(f'{"✗" if hits else "✓"} {sid}/{k}: 25 전용 {len(hits)}줄 (' + ' · '.join(f'{x} {kc[x]}' for x in KINDS if kc[x]) + f') · 📜 줄 {n_ok}' + (f' · 꼴 정보 {len(info)}' if info else ''))
                for ln, ks, t in (hits if full else hits[:5]):
                    print(f'   ✗ lec_{k}.txt:{ln} [{",".join(ks)}] {t[:110]}')
                if not full and len(hits) > 5: print(f'   … {len(hits) - 5}줄 더(--list)')
                for ln, kd, t in (info if full else info[:3]): print(f'   · lec_{k}.txt:{ln} [{kd}] 📜 줄 꼴 — "YY년 <형식> \\"요지\\" → JB 답 — 📜 25 기출 근거: …" (구조화 ⭐) · {t[:80]}')
            else: print(f'✓ {sid}/{k}: 25 전용 0')
            nlines += len(hits); nlec += bool(hits)
        for k, pk, head in prov:
            if not pk: print(f'· {sid}/{k}: LECMAP은 26인데 @UPD \'25 자료 임시\' 머리가 남음 — 26 전면으로 다시 짰으면 그 줄을 지움(QA 99 · RULES 14 b)')
            elif pk.startswith('자료 대기'): print(f'· {sid}/{k}: 임시 강의 — {pk} · SKILL B 3b 꼴(#LEC \'자료 대기\') · (a) 안 봄')
            else: print(f'· {sid}/{k}: 임시 강의 — {pk} · @UPD \'25 자료 임시\' 머리 {"있음" if head else "없음(QA 99 ✗ — RULES 14 b)"} · (a) 안 봄')
        prov = [x for x in prov if x[1]]
        print(f'== {sid}: (a) 25 전용 줄 {nlines}(강의 {nlec}개 · ' + ' · '.join(f'{x} {tot[x]}' for x in KINDS if tot[x]) + f') · 📜 줄 {nok} · (b) 임시 강의 {len(prov)} · 25 보조 키 {",".join(sorted(a25)) or "없음"}')
        bad_all += nlines
    return bad_all

if __name__ == '__main__':
    a = sys.argv[1:]
    full = '--list' in a; a = [x for x in a if x != '--list']
    keys = set()
    if '--keys' in a: i = a.index('--keys'); keys = {x.strip() for x in a[i + 1].split(',') if x.strip()}; a = a[:i] + a[i + 2:]
    if a and a[0] in ('-h', '--help'): sys.exit(__doc__)
    sids = [x.upper() for x in a]
    if not sids:
        try:
            sys.path.insert(0, TOOLS); import quarters as Qr; sids = Qr.sids('4q')
        except Exception: sids = []
        if not sids: sys.exit(__doc__ + '\n(4q 과목이 아직 없음 — SID를 주세요)')
    sys.exit(1 if main(sids, keys, full) else 0)
