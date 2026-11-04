"""11-04 두 허브 분리 — 한 브라우저(같은 주소)에서 3Q 기록을 심고 4Q를 열어 쓰고·백업·'바꾸기' 복원·기기 저장소 옮기기를 해도
3Q 기록(jblhub.v1.* · jblsync · 3Q IndexedDB)은 글자 하나 안 바뀜 · 4Q는 화면 설정·동기화 토큰만 한 번 가져옴(Gist id·바탕 값·기기 id 안 가져옴)
· 서로의 동기화 Gist 설명을 무시 · 3Q 백업 파일은 4Q에 안 들어감 · 다른 쿼터 과목 주소는 그 쿼터 허브로
GitHub API는 가짜 401로 막음(진짜 토큰 없음 · 네트워크에 나가지 않음)."""
import json
from qsite import *
from playwright.sync_api import sync_playwright
rel = build(); base = serve(); U3 = url(base, rel['3q']); U4 = url(base, rel['4q'])
N3, N4 = QS.QS['3q']['ident']['ns'], QS.QS['4q']['ident']['ns']; K3, K4 = QS.QS['3q']['ident']['syncKey'], QS.QS['4q']['ident']['syncKey']
SNAP = "(p=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(p.some(x=>k===x||k.indexOf(x)===0))o[k]=localStorage.getItem(k);}return o;})"
DBS = "(async()=>indexedDB.databases?(await indexedDB.databases()).map(d=>d.name).sort():[])()"
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(viewport={'width': 1280, 'height': 900}); errs = []
    ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, content_type='application/json', body='{"message":"Bad credentials"}'))
    def page():
        pg = ctx.new_page(); pg.on('pageerror', lambda x: errs.append(str(x)[:200])); pg.on('dialog', lambda d: d.accept()); return pg
    # 1) 3Q — 기록 심기
    pg = page(); pg.goto(U3); pg.wait_for_timeout(3500)
    pg.evaluate("(N=>{const S=(k,v)=>localStorage.setItem(N+k,JSON.stringify(v));S('mk.CONS',{ok:{Q01:1},ng:{},bm:{}});S('ann.CONS.WHT',{h:[[0,5,'y']]});S('hcol','#ffd400');S('fontScale',1.1);S('num.cfg',{lay:'w'});S('devName','맥북');S('memo.CONS',{t:'3Q 메모'});"
                "localStorage.setItem('" + K3 + "',JSON.stringify({tok:'ghp_TEST3Q',primary:true,gg3:{T:'gist3q',M:'gist3m'},gs3:{T:'x'},base:{DEVX:{g:{},k:{a:1}}},seen3:'2026-11-01T00:00:00Z'}));})", N3)
    pg.evaluate("__h.autoBak&&__h.autoBak(true,'시험 3Q')"); pg.wait_for_timeout(1500)
    dev3 = pg.evaluate(f"localStorage.getItem('{N3}devId')")
    pg.close()
    probe = page(); probe.goto(U3.replace('index.html', 'manifest.webmanifest'))   # 허브를 열지 않고(쓰기 없이) 같은 주소의 저장소만 봄
    S3 = probe.evaluate(SNAP, [N3, K3]); D3 = probe.evaluate(DBS)
    ok(len(S3) >= 8 and N3 + 'mk.CONS' in S3, f'3Q 기록 심음 — 키 {len(S3)}개 · DB {D3}')
    # 2) 4Q — 처음 열기(가져오기)
    pg = page(); pg.goto(U4); pg.wait_for_timeout(4000)
    g = pg.evaluate("(([N,K])=>{const g=k=>localStorage.getItem(N+k);return {imp:g('qimport'),hcol:g('hcol'),fs:g('fontScale'),cfg:g('num.cfg'),dn:g('devName'),mk:g('mk.CONS'),ann:g('ann.CONS.WHT'),memo:g('memo.CONS'),dev:g('devId'),sync:localStorage.getItem(K)};})", [N4, K4])
    ok(bool(g['imp']), f'4Q 첫 실행 가져오기 표시 {g["imp"]}')
    ok(g['hcol'] == S3[N3 + 'hcol'] and g['fs'] == S3[N3 + 'fontScale'] and g['cfg'] == S3[N3 + 'num.cfg'] and g['dn'] == S3[N3 + 'devName'], '화면 설정(형광펜 색·글자 크기·넘버링 설정·기기 이름) 이어받음')
    ok(g['mk'] is None and g['ann'] is None and g['memo'] is None, '채점·형광펜·메모는 안 가져옴(4Q 새로)')
    sy = json.loads(g['sync'] or 'null') or {}
    ok(sy.get('tok') == 'ghp_TEST3Q', '동기화 토큰 이어받음')
    ok('gist3q' not in (g['sync'] or '') and 'gist3m' not in (g['sync'] or '') and 'DEVX' not in (g['sync'] or ''), f'3Q Gist id·바탕 값은 안 가져옴 {(g["sync"] or "")[:120]}')
    ok(not g['dev'] or g['dev'] != dev3, f'기기 id는 따로 {g["dev"]} ≠ {dev3}')
    # 3) 4Q에서 이것저것 — 쓰기·자동 백업·'바꾸기' 복원·옮기기·3Q 백업 넣기
    pg.evaluate(f"localStorage.setItem('{N4}memo.X','\"4Q 메모\"')")
    pg.evaluate("__h.autoBak&&__h.autoBak(true,'시험 4Q')"); pg.wait_for_timeout(1500)
    pg.evaluate("(async()=>{const j=__h.bakFile();await __h.fileRestore(JSON.stringify(j),'replace');})()"); pg.wait_for_timeout(2500)
    pg.evaluate("(async()=>{try{await __h.xsMove();}catch(e){}})()"); pg.wait_for_timeout(1500)
    bad = {'app': 'jblhub', 'v': 2, 'at': '2026-11-01T00:00:00Z', 'dev': {}, 'data': {N3 + 'mk.ESTH': '{"ok":{"Q09":1}}', N3 + 'hcol': '"#000000"'}}
    pg.evaluate("t=>__h.fileRestore(t,'merge')", json.dumps(bad)); pg.wait_for_timeout(1500)
    w = pg.evaluate(f"[localStorage.getItem('{N4}mk.ESTH'),localStorage.getItem('{N3}mk.ESTH')]")
    ok(w == [None, None], f'3Q 백업 파일은 4Q에 안 들어감 {w}')
    d3 = 'JBL 허브 동기화 v3 · abc12 · T · 맥 · 기준'
    r4 = pg.evaluate("d=>[__h.syncDescP(d),__h.syncDescP(__h.syncDesc({id:'zz9',name:'맥'},'T',true))]", d3)
    ok(r4[0] is None and r4[1] and r4[1].get('g') == 'T', f'4Q 동기화는 3Q Gist 설명을 무시 · 제 것은 읽음 {r4}')
    D4 = pg.evaluate(DBS)
    pg.close()
    # 4) 3Q 기록 그대로인가
    probe2 = page(); probe2.goto(U3.replace('index.html', 'manifest.webmanifest'))
    S3b = probe2.evaluate(SNAP, [N3, K3])
    diff = sorted(k for k in set(S3) | set(S3b) if S3.get(k) != S3b.get(k))
    ok(not diff, f'4Q를 쓰고 난 뒤 3Q 기록(jblhub.v1.*·jblsync) 글자 그대로 — 다른 키 {diff[:6]}')
    new_db = sorted(set(D4) - set(D3)); ok(all(x.startswith('jbl4q') for x in new_db), f'4Q가 만든 IndexedDB = 4Q 이름만 {new_db}')
    ok(set(D3) <= set(D4), '3Q IndexedDB 그대로 남음')
    k4 = probe2.evaluate(SNAP, [N4, K4]); ok(all(k.startswith(N4) or k == K4 for k in k4), f'4Q 키는 4Q 이름 공간에만 ({len(k4)}개)')
    probe2.close()
    # 5) 3Q 허브에서 — 기록 보이고, 4Q Gist 설명은 무시
    pg = page(); pg.goto(U3); pg.wait_for_timeout(3500)
    r3 = pg.evaluate("d=>[__h.syncDescP(d), JSON.parse(localStorage.getItem(__h.NS+'mk.CONS')||'null')]", 'JBL 4Q 동기화 v3 · abc12 · T · 맥')
    ok(r3[0] is None and r3[1] and r3[1]['ok'].get('Q01') == 1, f'3Q 허브: 채점 기록 그대로 · 4Q Gist 무시 {r3}')
    pg.close()
    # 6) 다른 쿼터 과목 주소 → 그 쿼터로
    if QS.sids('3q'):
        s0 = QS.sids('3q')[1 if len(QS.sids('3q')) > 1 else 0]
        pg = page(); pg.goto(U4 + f'#/{s0}/_home'); pg.wait_for_timeout(4000)
        ok(('/' + rel['3q'] + '/') in pg.url and (f'#/{s0}/_home') in pg.url, f'4Q에서 #/{s0}/… → 3Q 허브로 {pg.url[-40:]}')
        pg.goto(U4 + f'#/_num/{s0}'); pg.wait_for_timeout(3000)
        ok(('/' + rel['3q'] + '/') in pg.url, f'4Q에서 #/_num/{s0} → 3Q 허브로')
        pg.close()
    ok(not [e for e in errs if 'Bad credentials' not in e], f'콘솔 오류 0 {errs[:3]}')
    br.close()
done()
