"""11-04 분기 정체성 — ① 3Q 값이 3Q 허브 원래 상수와 글자까지 같음(3q-final의 shell 상수) ② 4Q 값은 모두 다름 ③ 등록표 검사
④ 허브 코드(shell·num.js)에 저장 이름 글자가 주석 밖에 남지 않음(모두 Q에서) ⑤ 미리 보기 사이트의 두 허브가 각자 Q를 받음"""
import re, json
from qsite import *
from playwright.sync_api import sync_playwright
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
