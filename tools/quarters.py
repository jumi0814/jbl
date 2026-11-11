"""분기 등록표 읽기·검사 — tools/quarters.json (11-04 4Q 계획).
분기(3q·4q)마다 docs 폴더·허브 이름·저장 정체성(localStorage 이름 공간·동기화·IndexedDB·BroadcastChannel·잠금·백업 이름),
과목(SID)마다 분기·이름·짧은 이름·색·JB 파일 이름·강의자료 폴더 이름.
분기의 "img": "files"(11-10 — 4q) = 그 분기 과목의 그림을 파일로(<docs>/packs/img/<SID>/<키>.<h8>.webp|jpg + 팩 imgf — build4·tools/jblpaths.py img_*) · 키가 없으면(3q) 묶음 방식(<SID>.img.<강의>.js) 그대로.
같은 주소(jumi0814.github.io)의 두 허브가 서로의 기록을 건드리지 않게 — 정체성 값은 분기마다 모두 달라야 함(check).
  python tools/quarters.py current            # 지금 분기
  python tools/quarters.py sids [q]           # 그 분기 과목(공백으로)
  python tools/quarters.py docs [q]           # 그 분기 docs 폴더(저장소 기준)
  python tools/quarters.py img [q]            # 그 분기 그림 방식(files = 파일 · chunks = 묶음)
  python tools/quarters.py check              # 등록표 검사(어기면 종료 코드 1)"""
import os, re, sys, json
TOOLS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(TOOLS)
REG = json.load(open(os.path.join(TOOLS, 'quarters.json'), encoding='utf-8'))
QS = REG['quarters']; SUBJ = REG['subjects']

def current(): return REG['current']
def info(q): return QS[q]
def sids(q=None):
    q = q or current(); return [s for s, v in SUBJ.items() if v['q'] == q]
def all_sids(): return list(SUBJ)
def quarter_of(sid):
    v = SUBJ.get(sid)
    if not v: raise KeyError(f'{sid}: tools/quarters.json subjects에 없는 과목 — tools/new_subject.py로 등록')
    return v['q']
def docs_dir(q): return os.path.join(ROOT, QS[q]['docs'])
def stage_dir(q): return os.path.join(ROOT, QS[q].get('stage') or os.path.join('work', '_tmp', 'hub' + q))
def frozen(q): return bool(QS[q].get('frozen'))
def img_mode(q): return QS[q].get('img') or 'chunks'   # 11-10 그림 방식 — 'files'(그림 파일 + 팩 imgf) · 'chunks'(묶음 — 키 없음)
def cutover_dir(q, base=None): return os.path.join(base or os.path.join(ROOT, 'docs'), os.path.relpath(REG['cutover'][q], 'docs'))
def live(): return [q for q in QS if not frozen(q)]

def published(d):
    D = os.path.join(ROOT, 'docs'); d = os.path.abspath(d); return d == D or d.startswith(D + os.sep)
def qcfg(q, docs=None, layout=None):
    """허브(shell.html)의 const Q — 그 분기의 정체성·과목표·다른 분기 링크(상대 주소)
    layout = {분기: 폴더}(미리 보기 사이트) — 없으면 등록표 docs이고 사이트(docs/ 아래)에 없는 분기로는 링크를 걸지 않음(전환 전 스테이징)"""
    I = QS[q]; L = layout or {k: docs_dir(k) for k in QS}; me = docs or L[q]; sub = sids(q)
    links = []
    for o in I.get('links', []):
        if layout is None and not (published(L[o]) and published(me)): continue
        url = os.path.relpath(L[o], me).replace(os.sep, '/')
        links.append({'id': o, 'label': QS[o]['label'], 'url': ('' if url == '.' else url.rstrip('/') + '/'), 'sids': sids(o)})
    imp = I.get('importFrom')
    return dict(I['ident'], id=q, label=I['label'], title=I.get('title', 'JBL 허브'),   # 탭 제목(11-04 — 3Q는 원래 'JBL 허브' 그대로 · ux_u22)
                subjects=[[s, SUBJ[s]['ko'], SUBJ[s]['short']] for s in sub],
                colors={s: SUBJ[s]['color'] for s in sub},
                links=links,
                bcAll=REG.get('bcAll') or '',   # 11-10 T3 쿼터 공용 시계 채널(모든 쿼터가 같은 값 — 정체성 아님)
                importFrom=({'ns': QS[imp]['ident']['ns'], 'syncKey': QS[imp]['ident']['syncKey'], 'label': QS[imp]['label']} if imp else None),
                others=[{'ns': QS[o]['ident']['ns'], 'syncKey': QS[o]['ident']['syncKey'], 'label': QS[o]['label']} for o in QS if o != q])

_js = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
def fill_index(shell, q, READY, PV, PSZ, BUILD, docs=None, inline=None, jsf=_js, layout=None):
    """shell.html → 그 분기 index.html(build4·rehub 공통 — 두 곳이 같은 글을 내야 rehub --check가 맞음)"""
    t = shell
    if inline is not None: t = t.replace('<!--INLINE_PACKS-->', inline)
    t = t.replace('<!--INLINE_PACKS-->', '').replace('null/*READY*/', jsf(READY)).replace('null/*PV*/', jsf(PV)).replace('null/*PSZ*/', jsf(PSZ)).replace("'dev'/*BUILD*/", jsf(BUILD))
    t = t.replace('null/*QCFG*/', _js(qcfg(q, docs, layout)))
    t = re.sub(r'<title>[^<]*</title>', '<title>JBL 허브 · ' + QS[q]['label'] + '</title>', t, count=1)
    return t

def manifest(q):
    return json.dumps({'name': 'JBL 허브', 'short_name': 'JBL 허브', 'start_url': './', 'scope': './', 'display': 'standalone', 'lang': 'ko', 'background_color': '#F7F4EF', 'theme_color': '#FFFFFF',
                       'icons': [{'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png'}]}, ensure_ascii=False, indent=1).encode('utf-8')

def icon_png(n):
    """홈 화면 앱 아이콘(build4 C11과 같은 그림 — 먹 바탕 · JBL · 노란 띠)"""
    import io
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('RGB', (n, n), '#111827'); d = ImageDraw.Draw(im)
    d.rounded_rectangle([int(n * .16), int(n * .60), int(n * .84), int(n * .74)], radius=max(2, n // 28), fill='#FFE58A')
    try: f = ImageFont.load_default(size=int(n * .30))
    except TypeError: f = ImageFont.load_default()
    d.text((n / 2, n * .42), 'JBL', fill='#FFFFFF', font=f, anchor='mm')
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True); return b.getvalue()

def check():
    err = []
    if current() not in QS: err.append(f'current {current()} 없음')
    for s, v in SUBJ.items():
        if not re.fullmatch(r'[A-Z][A-Z0-9]{1,7}', s): err.append(f'{s}: SID는 대문자로 시작하는 영숫자 2~8자')
        if s in ('T', 'M') or s.startswith('N'): err.append(f'{s}: 동기화 묶음 이름(T·M·N…)과 헷갈림')
        if v['q'] not in QS: err.append(f'{s}: 분기 {v["q"]} 없음')
        for k in ('ko', 'short', 'color', 'jb', 'mat'):
            if not v.get(k): err.append(f'{s}: {k} 비어 있음')
    for s in SUBJ:   # 넘버링 동기화 조각 = N<SID><0-7> — 같은 쿼터(한 허브의 SYNC_SJ)의 다른 SID + 숫자 하나와 겹치면 안 됨(11-05: 쿼터가 다르면 허브·동기화가 따로라 괜찮음 — 4Q CONS4 ↔ 3Q CONS)
        for t in SUBJ:
            if t != s and SUBJ[t]['q'] == SUBJ[s]['q'] and re.fullmatch(re.escape(s) + r'[0-7]', t): err.append(f'{t}: {s}+숫자와 동기화 조각 이름이 겹침')
    seen = {}
    for q, I in QS.items():
        for k, v in I['ident'].items():
            for x in (v.values() if isinstance(v, dict) else [v]):
                if x in seen and seen[x] != q: err.append(f'{q}.{k} = {x!r} — 분기 {seen[x]}와 같음(기록이 섞임)')
                seen.setdefault(x, q)
        for o in I.get('links', []) + ([I['importFrom']] if I.get('importFrom') else []):
            if o not in QS: err.append(f'{q}: 링크·가져오기 분기 {o} 없음')
        if I.get('img') not in (None, 'files'): err.append(f'{q}.img = {I.get("img")!r} — "files"이거나 키가 없어야 함(없음 = 묶음 방식)')
        if I.get('img') and I.get('frozen'): err.append(f'{q}: 보관(frozen) 분기는 그림 방식을 바꾸지 않음(배포된 묶음 그대로 — img 키를 빼기)')
    ns = [I['ident']['ns'] for I in QS.values()]
    for a in ns:
        for b in ns:
            if a != b and b.startswith(a): err.append(f'이름 공간 {b!r}가 {a!r}로 시작함(접두가 겹침)')
    gs = [I['ident']['gist'] for I in QS.values()]
    for a in gs:
        for b in gs:
            if a != b and b.startswith(a + ' '): err.append(f'Gist 머리 {b!r}가 {a!r} 다음 공백으로 시작함')
    docs = [QS[q]['docs'] for q in QS]
    if len(set(docs)) != len(docs): err.append('분기 docs 폴더가 겹침')
    if REG.get('bcAll') and REG['bcAll'] in seen: err.append(f"bcAll = {REG['bcAll']!r} — 분기 {seen[REG['bcAll']]}의 정체성 값과 같음(공용 채널은 달라야 함)")   # 11-10 T3
    return err

if __name__ == '__main__':
    a = sys.argv[1:] or ['check']
    if a[0] == 'current': print(current())
    elif a[0] == 'sids': print(' '.join(sids(a[1] if len(a) > 1 else None)))
    elif a[0] == 'docs': print(QS[a[1] if len(a) > 1 else current()]['docs'])
    elif a[0] == 'live': print(' '.join(live()))
    elif a[0] == 'img': print(img_mode(a[1] if len(a) > 1 else current()))
    elif a[0] == 'check':
        e = check(); print('\n'.join('  ✗ ' + x for x in e) or 'quarters check: OK'); sys.exit(1 if e else 0)
    else: sys.exit(__doc__)
