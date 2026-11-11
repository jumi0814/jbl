"""11-04 분기 정체성 — ① 3Q 값이 3Q 허브 원래 상수와 글자까지 같음(3q-final의 shell 상수) ② 4Q 값은 모두 다름 ③ 등록표 검사
④ 허브 코드(shell·num.js)에 저장 이름 글자가 주석 밖에 남지 않음(모두 Q에서) ⑤ 미리 보기 사이트의 두 허브가 각자 Q를 받음
⑥ (11-10 W0) 전역 이름을 가리는 선언 0 — 허브 전역 QC·NS·NSR·LS·SYNC·XS·PACKS·CUR·SUBJECTS를 const/let/var·함수 인자·구조 분해·함수 이름·catch로 다시 선언하면 ✗
   (11-04 사고: 정체성 `const Q`가 syncPull의 지역 배열 `Q=[]`에 가려 받은 기록을 모두 버림) · `T`(공부 시계)는 지역 이름으로 쓰는 곳이 여럿이라
   'T를 다시 선언한 범위 안에서 전역 T의 필드(T.t0·T.inp …)를 읽으면' ✗ · 린트 자체 검사(나쁜 예를 잡는지)도 같이.
   JBL_LINT_ONLY=1 이면 브라우저 없이 ①~④·⑥만."""
import re, json
from qsite import *
OLD3 = {'ns': 'jblhub.v1.', 'syncKey': 'jblsync', 'gist': 'JBL 허브', 'headApp': 'jblhub-sync', 'bakApp': 'jblhub', 'filePre': 'JBL허브_',
        'idb': {'bak': 'jblhub-bak', 'sync': 'jblsync', 'lsq': 'jblhub-lsq', 'xs': 'jblhub-xs'}, 'bc': {'t': 'jblhub', 'xs': 'jblhub-xs'}, 'lock': 'jblsync'}
ok(QS.QS['3q']['ident'] == OLD3, '① 3Q 정체성 = 3Q 허브 원래 상수(바꾸면 3Q 기록이 안 보임)')
flat = lambda d: [x for v in d.values() for x in (v.values() if isinstance(v, dict) else [v])]
for q in QS.QS:
    if q != '3q': ok(not set(flat(QS.QS[q]['ident'])) & set(flat(OLD3)), f'② {q} 정체성 값이 3Q와 하나도 안 겹침')
e = QS.check(); ok(not e, f'③ 등록표 검사 {e[:3]}')
strip = lambda t: re.sub(r'/\*.*?\*/', '', re.sub(r'(?m)^\s*//.*$', '', t), flags=re.S)
for f in ('cons/shell.html', 'num/num.js'):
    t = strip(open(os.path.join(TOOLS, f), encoding='utf-8').read())
    lit = sorted(set(re.findall(r"['\"`](jbl(?:hub|sync|4q)[^'\"`\s]*|JBL 허브 동기화[^'\"`]*|JBL허브_[^'\"`]*)['\"`]", t)) - {'jblhub.probe', 'jblsyncst'})
    ok(not lit, f'④ {f}: 주석 밖 저장 이름 글자 0 {lit[:5]}')
    sh = re.findall(r'(?<![\w$.])Q\.(ns|syncKey|gist|headApp|bakApp|filePre|idb|bc|lock|id|label|subjects|colors|links|importFrom|others)\b', t)
    ok(not sh, f'④ {f}: 정체성은 QC로만(Q는 동기화 등 지역 배열 이름과 겹침 — 11-04 syncPull Q.headApp → 받은 기록 모두 버림) {sh[:5]}')

# ---- ⑥ 전역 이름을 가리는 선언(11-10 W0) — 작은 JS 토큰 분석기(주석·문자열·정규식·템플릿 글은 건너뜀 · `${…}` 안은 코드로 읽음)
GLOB = ['QC', 'NS', 'NSR', 'LS', 'SYNC', 'XS', 'PACKS', 'CUR', 'SUBJECTS']   # 다시 선언하면 바로 ✗
SOFT = 'T'                                                                    # 다시 선언한 범위 안에서 전역 필드를 읽으면 ✗
# 허용(이름을 바꾸면 여기서 뺌) — (파일, 이름, 그 선언 바로 뒤 글 머리): 까닭
ALLOW = {('num/num.js', 'NS', "='xmlns:w="): 'Word(.docx) XML 이름 공간 글 — 그 함수는 허브 저장 이름 공간(NS)을 읽지 않음(넘버링은 H.st로만 저장)'}
_TOK = re.compile(r'''(?P<ws>\s+)|(?P<lc>//[^\n]*)|(?P<bc>/\*.*?\*/)|(?P<s>'(?:\\.|[^'\\\n])*'|"(?:\\.|[^"\\\n])*")|(?P<n>0[xX][0-9a-fA-F]+|\d+\.?\d*(?:[eE][+-]?\d+)?n?|\.\d+)|(?P<id>[A-Za-z_$ -￿][\w$ -￿]*)|(?P<p>=>|\.\.\.|===|!==|==|!=|<=|>=|&&=|\|\|=|\?\?=|&&|\|\||\?\?|\?\.|\+\+|--|\*\*=|\*\*|<<=|>>>=|>>=|<<|>>>|>>|[-+*/%&|^]=|[{}()\[\];,.<>+\-*/%&|^!~?:=@#\\])''', re.S)
_REKW = {'return', 'typeof', 'case', 'in', 'of', 'void', 'delete', 'throw', 'new', 'else', 'do', 'instanceof', 'yield', 'await'}
def js_tokens(src):
    """[(종류 id|p|n|s, 글, 자리)] — 템플릿 `…${식}…` = s ( 식 ) … 로 풀어 괄호 짝이 맞게"""
    out = []; i = 0; n = len(src); tpl = []   # tpl = `${` 안 중괄호 깊이 스택
    def template(i):   # i = 템플릿 글 안(여는 ` 다음 또는 식을 닫은 } 다음) → 코드로 돌아갈 자리
        while i < n:
            c = src[i]
            if c == '\\': i += 2; continue
            if c == '`': return i + 1
            if c == '$' and src[i + 1:i + 2] == '{': out.append(('p', '(', i)); tpl.append(0); return i + 2
            i += 1
        raise ValueError('템플릿 글이 안 닫힘')
    while i < n:
        c = src[i]
        if c == '`': out.append(('s', '`', i)); i = template(i + 1); continue
        if c == '}' and tpl and tpl[-1] == 0: tpl.pop(); out.append(('p', ')', i)); i = template(i + 1); continue
        if c == '/' and src[i + 1:i + 2] not in ('/', '*'):
            pv = next((x for x in reversed(out)), None)
            if pv is None or (pv[0] == 'id' and pv[1] in _REKW) or (pv[0] == 'p' and pv[1] not in (')', ']', '}')):
                j = i + 1; cls = False; good = False
                while j < n and src[j] != '\n':
                    d = src[j]
                    if d == '\\': j += 2; continue
                    if d == '[': cls = True
                    elif d == ']': cls = False
                    elif d == '/' and not cls: good = True; break
                    j += 1
                if good:
                    j += 1
                    while j < n and (src[j].isalpha()): j += 1
                    out.append(('s', '/', i)); i = j; continue
        m = _TOK.match(src, i)
        if not m: raise ValueError(f'읽지 못한 글자 {src[i:i + 20]!r} @{i}')
        k = m.lastgroup; i = m.end()
        if k in ('ws', 'lc', 'bc'): continue
        v = m.group(0)
        if tpl and k == 'p':
            if v == '{': tpl[-1] += 1
            elif v == '}': tpl[-1] -= 1
        out.append((k, v if k != 's' else "'", m.start()))
    if tpl: raise ValueError('템플릿 식이 안 닫힘')
    return out
_OPEN = {'(': ')', '[': ']', '{': '}'}; _CTRL = {'if', 'for', 'while', 'switch', 'with', 'return', 'typeof', 'await', 'function', 'new', 'in', 'of', 'do', 'else', 'void', 'delete', 'throw', 'yield', 'case'}
_STMT = {'const', 'let', 'var', 'return', 'if', 'for', 'while', 'do', 'switch', 'try', 'throw', 'break', 'continue', 'class'}
def js_bindings(tk):
    """토큰 → (선언 [(이름, 종류, 토큰 번호, 중괄호 깊이, 범위 (lo, hi) 토큰 번호)], 짝 표)"""
    mt = {}; st = []; depth = [0] * len(tk); encl = [-1] * len(tk); bs = []; d = 0
    for i, (k, v, _) in enumerate(tk):
        encl[i] = bs[-1] if bs else -1
        if k == 'p' and v in _OPEN:
            st.append(i)
            if v == '{': depth[i] = d; d += 1; bs.append(i); continue
        elif k == 'p' and v in (')', ']', '}'):
            if not st or _OPEN[tk[st[-1]][1]] != v: raise ValueError(f'괄호 짝이 안 맞음 @{tk[i][2]}')
            mt[st[-1]] = i; mt[i] = st.pop()
            if v == '}': d -= 1; bs.pop(); encl[i] = bs[-1] if bs else -1
        depth[i] = d
    if st: raise ValueError(f'안 닫힌 괄호 @{tk[st[-1]][2]}')
    P = lambda i, v: 0 <= i < len(tk) and tk[i][0] == 'p' and tk[i][1] == v
    I = lambda i: 0 <= i < len(tk) and tk[i][0] == 'id'
    def items(lo, hi):   # (lo, hi) 사이를 깊이 0 쉼표로 나눔
        a = lo; i = lo; out = []
        while i < hi:
            if tk[i][0] == 'p' and tk[i][1] in _OPEN: i = mt[i] + 1; continue
            if P(i, ','): out.append((a, i)); a = i + 1
            i += 1
        if a < hi: out.append((a, hi))
        return out
    def target(a, b, names):   # 묶는 자리 하나: [...]이름 | {무늬} | [무늬] (뒤의 = 기본값은 버림)
        if a < b and P(a, '...'): a += 1
        if a >= b: return
        if I(a): names.append((tk[a][1], a))
        elif P(a, '{'):
            for x, y in items(a + 1, mt[a]):
                if P(x, '...'): target(x, y, names); continue
                j = x; colon = -1
                while j < y:
                    if tk[j][0] == 'p' and tk[j][1] in _OPEN: j = mt[j] + 1; continue
                    if P(j, '='): break
                    if P(j, ':'): colon = j; break
                    j += 1
                target(colon + 1 if colon >= 0 else x, y, names)
        elif P(a, '['):
            for x, y in items(a + 1, mt[a]): target(x, y, names)
    def expr_end(j, hi=None):   # 식의 끝(깊이 0의 , ; 닫는 괄호 · 다음 문장 머리)
        hi = len(tk) if hi is None else hi
        while j < hi:
            k, v, _ = tk[j]
            if k == 'p' and v in _OPEN: j = mt[j] + 1; continue
            if k == 'p' and v in (',', ';', ')', ']', '}'): return j
            if k == 'id' and v in _STMT and not P(j - 1, '.'): return j
            j += 1
        return j
    out = []
    def scope_block(i):   # 그 토큰을 감싼 { … } (없으면 파일 전체)
        b = encl[i]; return (b, mt[b]) if b >= 0 else (0, len(tk) - 1)
    def params(op, kind, body_from):   # ( … ) 인자 + 본문 범위
        names = []
        for x, y in items(op + 1, mt[op]): target(x, y, names)
        b = body_from
        hi = mt[b] if P(b, '{') else expr_end(b) - 1
        for nm, at in names: out.append((nm, kind, at, depth[at], (op, hi)))
    for i, (k, v, _) in enumerate(tk):
        if k == 'id' and v in ('const', 'let', 'var') and not P(i - 1, '.') and not P(i + 1, ':') and not P(i + 1, '='):
            j = i + 1
            while j < len(tk):
                names = []
                if I(j): names.append((tk[j][1], j)); j += 1
                elif P(j, '{') or P(j, '['): target(j, mt[j] + 1, names); j = mt[j] + 1
                else: break
                for nm, at in names: out.append((nm, v, at, depth[i], scope_block(i)))
                if P(j, '='): j = expr_end(j + 1)
                if P(j, ','): j += 1; continue
                break
        elif k == 'id' and v == 'function' and not P(i - 1, '.'):
            j = i + 1
            if P(j, '*'): j += 1
            if I(j):
                if not (P(i - 1, '=') or P(i - 1, '(') or P(i - 1, ',') or P(i - 1, ':')): out.append((tk[j][1], 'function', j, depth[i], scope_block(i)))   # 함수 선언 이름(식 안의 이름은 밖에 안 보임)
                j += 1
            if P(j, '('): params(j, '인자', mt[j] + 1)
        elif k == 'id' and v == 'class' and I(i + 1) and not P(i - 1, '.'): out.append((tk[i + 1][1], 'class', i + 1, depth[i], scope_block(i)))
        elif k == 'id' and v == 'catch' and P(i + 1, '(') and P(mt[i + 1] + 1, '{'): params(i + 1, 'catch', mt[i + 1] + 1)
        elif k == 'p' and v == '=>':
            if I(i - 1): b = i + 1; hi = mt[b] if P(b, '{') else expr_end(b) - 1; out.append((tk[i - 1][1], '인자', i - 1, depth[i - 1], (i - 1, hi)))
            elif P(i - 1, ')'): params(mt[i - 1], '인자', i + 1)
        elif k == 'p' and v == ')' and P(i + 1, '{') and I(mt[i] - 1) and tk[mt[i] - 1][1] not in _CTRL and tk[mt[i] - 1][1] != 'catch' and not (I(mt[i] - 2) and tk[mt[i] - 2][1] == 'function'):
            params(mt[i], '인자', i + 1)   # 메서드 줄임꼴 이름(…){…}
    return out, mt
def js_of(path):
    t = open(path, encoding='utf-8').read()
    if path.endswith('.html'): return [(m.start(1), m.group(1)) for m in re.finditer(r'<script(?:\s[^>]*)?>(.*?)</script>', t, re.S)], t
    return [(0, t)], t
def shadow_lint(src, glob=GLOB, soft=SOFT, allow=(), own=True, gfields=None):
    """src(JS 한 덩이) → (['✗ 글', …], 정보) · allow = [(이름, 선언 뒤 글 머리)]
    own = 전역을 선언하는 코드 자신(허브 shell — 이름마다 가장 바깥 선언 하나가 전역) · False(num.js 등 딴 파일) = 어떤 선언이든 가림 · gfields = 전역 T의 필드(딴 파일은 허브에서 받아 씀)"""
    tk = js_tokens(src); B, mt = js_bindings(tk); bad = []
    top = {}   # 이름 → 가장 바깥(중괄호 깊이가 가장 얕은 const/let/var/function) 선언 = 전역 선언 자신
    for nm, kind, at, dep, sc in B:
        if kind != '인자' and kind != 'catch' and (nm not in top or dep < top[nm][0]): top[nm] = (dep, at)
    isg = lambda nm, at: own and nm in top and top[nm][1] == at   # 전역 선언 자신
    line = lambda at: src.count('\n', 0, tk[at][2]) + 1
    ctx = lambda at: re.sub(r'\s+', ' ', src[max(0, tk[at][2] - 30):tk[at][2] + 50])
    for nm, kind, at, dep, sc in B:
        if nm in glob and not isg(nm, at):
            after = re.sub(r'\s+', '', src[tk[at][2] + len(nm):tk[at][2] + len(nm) + 40])
            if any(nm == a and after.startswith(h) for a, h in allow): continue
            bad.append(f'{line(at)}줄 {kind} {nm} — 전역 {nm}를 가림 «{ctx(at)}»')
    # T: 다시 선언한 범위들 · 그 밖에서 읽은 T.<필드> = 전역 필드
    S = [(sc, at) for nm, kind, at, dep, sc in B if nm == soft and not isg(nm, at)]
    use = [i for i in range(len(tk) - 2) if tk[i] [:2] == ('id', soft) and tk[i + 1][0] == 'p' and tk[i + 1][1] in ('.', '?.') and tk[i + 2][0] == 'id' and not (i and tk[i - 1][0] == 'p' and tk[i - 1][1] in ('.', '?.'))]
    inside = lambda i: next((at for (lo, hi), at in S if lo <= i <= hi), None)
    gf = {tk[i + 2][1] for i in use if inside(i) is None} if own else set(gfields or [])
    if own and soft in top:   # 전역 T={…}의 키도
        a = top[soft][1]
        if a + 2 < len(tk) and tk[a + 1][1] == '=' and tk[a + 2][1] == '{':
            j = a + 3; hi = mt[a + 2]
            while j < hi:
                if tk[j][0] == 'p' and tk[j][1] in _OPEN: j = mt[j] + 1; continue
                if tk[j][0] == 'id' and tk[j + 1][1] in (':', ',', '}', '(') and tk[j - 1][1] in ('{', ','): gf.add(tk[j][1])
                j += 1
    for i in use:
        at = inside(i)
        if at is not None and tk[i + 2][1] in gf: bad.append(f'{line(i)}줄 {soft}.{tk[i + 2][1]} — {line(at)}줄에서 {soft}를 다시 선언한 범위 안에서 전역 {soft}의 필드를 읽음 «{ctx(i)}»')
    return bad, {'tokens': len(tk), 'decls': len(B), 'soft': len(S), 'softat': sorted(line(at) for sc, at in S), 'gf': sorted(gf), 'top': {nm: line(top[nm][1]) for nm in glob + [soft] if own and nm in top}}
# 린트 자체 검사 — 나쁜 예는 잡고 멀쩡한 예는 안 잡음
_SELF = [("const QC={ns:'a'},NS=QC.ns;function f(){const Q=[];return Q.length+NS.length;}", 0),
         ("const NS='a';function f(){const NS='b';return NS;}", 1), ("const LS={};const g=(a,LS)=>a;", 1), ("let CUR={};function f({CUR}){return CUR;}", 1),
         ("const XS={};for(const [k,XS] of []){}", 1), ("var SYNC={};try{}catch(SYNC){}", 1), ("const PACKS={};function h(){function PACKS(){}}", 1),
         ("const QC=1;const f=x=>{let a=1,QC=2;return a+QC;};", 1), ("const S=`a${(()=>{const NS=1;return NS;})()}b`;const NS=2;", 1),
         ("const SUBJECTS=[];const o={m(SUBJECTS){return 1;}};", 1), ("const NS=1;const r=/[/'\"`]/.test('x')?{NS:1}:{a:NS};const o={NS,LS:2};o.NS=3;", 0),
         ("const T={t0:0,inp:0};function a(){const T=[1,2];return T.length+T.map(x=>x).length;}function b(){return T.t0;}", 0),
         ("const T={t0:0,inp:0};function a(q){const T=q.split(' ');return T.inp;}", 1), ("const T={t0:0};T.last=1;const f=(T,i)=>T.last+i;", 1),
         ("const T={t0:0};function a(){const T=(k,v)=>k+v;return T('a','b');}function c(){return T.t0;}", 0)]
sb = [(s, n, len(shadow_lint(s)[0])) for s, n in _SELF]
ok(all((g > 0) == (n > 0) for s, n, g in sb), f'⑥ 린트 자체 검사 {len(_SELF)}개(나쁜 예는 잡고 멀쩡한 예는 안 잡음) {[s[:50] for s, n, g in sb if (g > 0) != (n > 0)][:3]}')
GF = set()
for f in ('cons/shell.html', 'num/num.js'):
    try:
        parts, whole = js_of(os.path.join(TOOLS, f)); bad = []; info = []; own = f.endswith('shell.html')
        if own: parts = [max(parts, key=lambda x: len(x[1]))]   # 허브 본 코드(가장 긴 script) — 머리의 짧은 script는 따로 도는 조각
        for off, src in parts:
            b, st = shadow_lint(src, allow=[(a[1], a[2]) for a in ALLOW if a[0] == f], own=own, gfields=GF); l0 = whole.count('\n', 0, off)
            if own:
                GF |= set(st['gf']); miss = [g for g in GLOB + [SOFT] if g not in st['top']]
                ok(not miss and len(GF) >= 10, f'⑥ {f}: 전역 선언을 찾음 {({k: v + l0 for k, v in st["top"].items()})} · 전역 {SOFT} 필드 {len(GF)}개 {miss}')
            bad += [re.sub(r'^(\d+)줄', lambda m: f'{int(m.group(1)) + l0}줄', re.sub(r'— (\d+)줄에서', lambda m: f'— {int(m.group(1)) + l0}줄에서', x)) for x in b]; info.append(st)
        ok(not bad, f'⑥ {f}: 전역 이름({"·".join(GLOB)})을 가리는 선언 0 · {SOFT}를 다시 선언한 범위 {sum(x["soft"] for x in info)}곳{[n + whole.count(chr(10), 0, parts[0][0]) for x in info for n in x["softat"]]}에서 전역 {SOFT} 필드 읽기 0 (토큰 {sum(x["tokens"] for x in info)} · 선언 {sum(x["decls"] for x in info)})')
        for x in bad[:20]: print('       ✗ ' + x[:260])
    except ValueError as ex:
        ok(False, f'⑥ {f}: 코드를 읽지 못함(린트 분석기) — {ex}')
if os.environ.get('JBL_LINT_ONLY'): done()
from playwright.sync_api import sync_playwright
rel = build(); base = serve()
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on('pageerror', lambda x: errs.append(str(x)[:200]))
    for q, r in rel.items():
        pg.goto(url(base, r)); pg.wait_for_timeout(2500)
        got = pg.evaluate('JSON.stringify({id:__h.Q.id,ns:__h.NS,sync:__h.Q.syncKey,sj:__h.Q.subjects.map(x=>x[0]),title:document.title,kick:(document.querySelector(".hkick")||{}).textContent||""})')
        g = json.loads(got)
        ok(g['id'] == q and g['ns'] == QS.QS[q]['ident']['ns'] and g['sync'] == QS.QS[q]['ident']['syncKey'], f'⑤ {q} 허브가 자기 정체성 {g["id"]} {g["ns"]}')
        ok(g['sj'] == QS.sids(q), f'⑤ {q} 과목 = 등록표 {g["sj"]}')
        ok(QS.QS[q]['label'] in g['kick'] and all(QS.QS[o]['label'] in g['kick'] for o in QS.QS[q].get('links', [])), f'⑤ {q} 홈 머리: 쿼터 이름·전환 링크 «{g["kick"][:60]}»')
    ok(not errs, f'콘솔 오류 0 {errs[:2]}')
    br.close()
done()
