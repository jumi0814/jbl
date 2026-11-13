"""11-11 W5 저장 공간·형광펜 — ① 다른 쿼터 기록이 큰 상태(D3 — 저장 공간 창·허브 홈 경고의 '다른 쿼터(○쿼터) 기록 n MB — ○Q 허브에서 정리하기' 글·링크 · 누르면 그 허브 + 공간 정리 창)
② 밀린 쓰기(저장 실패 대기열)는 15일 뒤에도 남음(옛: 14일 넘으면 버림) · 띠에 밀린 개수·가장 오래된 날 ③ 다른 쿼터 백업 파일을 넣으면 안내(D4)
④ 형광펜 위치 찾기(B1 — 블록 글이 바뀌었고 후보가 하나뿐이면 문맥이 맞을 때만 · 12자 이상은 그대로) ⑤ ★ 카드 수 = 지금 있는 카드만 · 원고 갱신 이관이 ★ 카드 북마크·회독 수도(B3).
4Q 뿌리와 3q/ 허브 둘 다(qsite — 한 주소 = 저장 한도를 같이 씀) · 과목·카드는 등록표·__h.PACKS에서 찾음(id를 박지 않음)."""
import json, re
from qsite import *
from playwright.sync_api import sync_playwright
rel = build(); base = serve()
FULL = "try{const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){let f='';try{f=sessionStorage.getItem('q_full')||'';}catch(e){}if(f&&this===localStorage&&f.split('|').some(x=>String(k).indexOf(x)>=0))throw new DOMException('quota','QuotaExceededError');return o.call(this,k,v);};}catch(e){}"   # sessionStorage q_full = 'memo.|ann.'처럼 — 그 글자가 든 키 쓰기만 자리 없음으로(저장 실패 대기열 길 · 창마다 따로)

def wait(pg, js, n=100, ms=100):
    for _ in range(n):
        try:
            if pg.evaluate(js): return True
        except Exception: pass
        pg.wait_for_timeout(ms)
    return False

with sync_playwright() as p:
    b = p.chromium.launch()
    for q, r in rel.items():
        oq = [x for x in QS.QS if x != q][0]; I = QS.QS[q]['ident']; IO = QS.QS[oq]['ident']; N = I['ns']; NO = IO['ns']
        U = url(base, r); UO = url(base, rel[oq]); SJ = (QS.sids(q) or [''])[0]
        ko = re.sub(r'^\d+학년\s*', '', QS.QS[oq]['label']); sh = ko.replace('쿼터', 'Q')
        print(f'== {q} ({U}) · 다른 쿼터 {ko}')
        ctx = b.new_context(viewport={'width': 1280, 'height': 900}, accept_downloads=True); ctx.add_init_script(FULL)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        def boot(u, ms=1500): pg.goto('about:blank'); pg.goto(u); pg.wait_for_timeout(ms)
        boot(U + '#/'); pg.evaluate("localStorage.clear();sessionStorage.clear()")

        # ---- ① 다른 쿼터 기록이 큼(한도 100만 자로 재 둠 · 다른 쿼터 80만 자)
        pg.evaluate("([N,NO])=>{localStorage.setItem(N+'lscap','1000000');localStorage.setItem(NO+'ann.BIG',JSON.stringify('가'.repeat(100)+'x'.repeat(800000)));}", [N, NO])
        boot(U + '#/')
        w = pg.evaluate("(e=>e?[e.textContent,(e.querySelector('a')||{}).href||'']:['',''])(document.querySelector('#storewarn .storewarn'))")
        ok(f'다른 쿼터({ko}) 기록' in w[0] and f'{sh} 허브에서 정리하기' in w[0] and w[1] == UO.replace('index.html', '') + '#/_clean', f'{q} ① 허브 홈 경고 {w[0][:90]!r} → {w[1]}')
        pg.evaluate("document.querySelector('#storewarn [data-openrst]').click()"); pg.wait_for_timeout(1500)
        t = pg.evaluate("(e=>e?[e.textContent,e.querySelector('a').getAttribute('href')]:['',''])(document.querySelector('#rpop .oqline'))")
        ok(re.search(rf'다른 쿼터\({ko}\) 기록 [\d.]+(MB|KB) — {sh} 허브에서 정리하기', t[0] or '') is not None and t[1].endswith('#/_clean'), f'{q} ① 저장 공간 창 {t[0]!r} ({t[1]})')
        pg.screenshot(path=os.path.join(ROOT, 'work', '_tmp', f'q_store_oq_{q}.png'))
        pg.evaluate("document.querySelector('#rpop .oqline a').click()")
        try: pg.wait_for_function("location.hash==='#/'&&!!((document.querySelector('#rpop.on #rclean')||{}).open)", timeout=12000)   # 11-13 고정 2.5초 대기 → 조건 대기(전체 검사 묶음 안에서 한 번 늦어 거짓 실패)
        except Exception: pass
        pg.wait_for_timeout(300)
        there = pg.evaluate("[location.href,!!((document.querySelector('#rpop.on #rclean')||{}).open)]")
        ok(there[0].startswith(UO.replace('index.html', '')) and there[0].endswith('#/') and there[1], f'{q} ① 링크 → {ko} 허브 + 공간 정리 창 열림 {there}')
        boot(U + '#/'); pg.evaluate("([N,NO])=>{localStorage.removeItem(NO+'ann.BIG');localStorage.removeItem(N+'lscap');}", [N, NO])

        # ---- ② 밀린 쓰기: 15일 전에 밀린 줄이 다시 열어도 남음(자리 없음 → 띠에 개수·가장 오래된 날 · 자리 생기면 저장)
        OLD = 15 * 86400000
        pg.evaluate("sessionStorage.setItem('q_full','memo.')"); boot(U + '#/')
        pg.evaluate("""([db,at])=>new Promise(res=>{const r=indexedDB.open(db,1);r.onupgradeneeded=()=>{const d=r.result;if(!d.objectStoreNames.contains('q'))d.createObjectStore('q',{keyPath:'k'});};
          r.onsuccess=()=>{const tx=r.result.transaction(['q'],'readwrite');tx.objectStore('q').put({k:'memo.X.L',v:JSON.stringify('밀린 메모'),at});tx.oncomplete=()=>{r.result.close();res(1);};};})""", [I['idb']['lsq'], pg.evaluate("Date.now()") - OLD])
        boot(U + '#/', 2500)
        band = pg.evaluate("(e=>e?e.textContent:'')(document.querySelector('#lserr'))"); od = pg.evaluate("a=>new Date(a).toLocaleDateString('ko-KR',{month:'long',day:'numeric'})", pg.evaluate("Date.now()") - OLD)
        ok('기록 1건을 이 기기에 임시 보관 중' in band and f'가장 오래된 것 {od}' in band and pg.evaluate("__h.LSQ.get('memo.X.L')") == json.dumps('밀린 메모', ensure_ascii=False), f'{q} ② 15일 전에 밀린 줄이 남아 있음(옛: 버림) · 띠 {band[:70]!r}')
        boot(U + '#/', 2500); row = pg.evaluate("""db=>new Promise(res=>{const r=indexedDB.open(db,1);r.onsuccess=()=>{const g=r.result.transaction(['q']).objectStore('q').getAll();g.onsuccess=()=>{r.result.close();res(g.result);};};})""", I['idb']['lsq'])
        ok(len(row) == 1 and abs(pg.evaluate("Date.now()") - row[0]['at'] - OLD) < 120000, f'{q} ② 한 번 더 열어도 그대로 · 처음 밀린 때 유지({len(row)}줄)')
        pg.evaluate("sessionStorage.removeItem('q_full')"); boot(U + '#/', 2500)
        ok(pg.evaluate("k=>localStorage.getItem(k)", N + 'memo.X.L') == json.dumps('밀린 메모', ensure_ascii=False) and pg.evaluate("__h.LSQ.size") == 0, f'{q} ② 자리가 생기면 저장됨')

        # ---- ②b (b)2 꽉 찬 동안 밀린 형광펜·채점이 다른 창의 새 값을 덮지 않음(합쳐 씀) · 다른 창이 안 썼으면 지금처럼 덮어씀(지운 표시가 되살아나지 않음)
        m = lambda x: {'t': 'h', 'x': x, 'i': 0}; KA = N + 'ann.ZZ'; KM = N + 'mk.ZZ'
        pg.evaluate("([a,b,v,w])=>{localStorage.setItem(a,JSON.stringify(v));localStorage.setItem(b,JSON.stringify(w));}", [KA, KM, {'c1': [m('하나'), m('지울것')]}, {'ok': {'Q1': 1}, 'ng': {}, 'bm': {}}])
        pg.evaluate("sessionStorage.setItem('q_full','ann.|mk.')")
        pg.evaluate("([v,w])=>{__h.LS.set('ann.ZZ',v);__h.LS.set('mk.ZZ',w);}", [{'c1': [m('하나'), m('둘')]}, {'ok': {'Q1': 1, 'Q2': 1}, 'ng': {}, 'bm': {}}]); pg.wait_for_timeout(300)
        ok(pg.evaluate("__h.LSQ.has('ann.ZZ')&&__h.LSQ.has('mk.ZZ')") and '지울것' in pg.evaluate("k=>localStorage.getItem(k)", KA), f'{q} ②b 자리 없음 → 형광펜·채점이 대기열에(저장소엔 옛 값)')
        pg2 = ctx.new_page(); pg2.goto(U + '#/'); pg2.wait_for_timeout(800)   # 다른 창(자리 있음)이 그사이 새 값을 씀
        pg2.evaluate("([a,b,v,w])=>{localStorage.setItem(a,JSON.stringify(v));localStorage.setItem(b,JSON.stringify(w));}", [KA, KM, {'c1': [m('하나'), m('지울것'), m('셋')], 'c2': [m('넷')]}, {'ok': {'Q1': 1, 'Q3': 1}, 'ng': {}, 'bm': {}}]); pg2.close()
        pg.evaluate("sessionStorage.removeItem('q_full')"); pg.evaluate("__h.lsFlush()"); pg.wait_for_timeout(300)
        A = json.loads(pg.evaluate("k=>localStorage.getItem(k)", KA)); M = json.loads(pg.evaluate("k=>localStorage.getItem(k)", KM)); xs = sorted(o['x'] for o in A.get('c1', []))
        ok({'하나', '둘', '셋'} <= set(xs) and [o['x'] for o in A.get('c2', [])] == ['넷'] and pg.evaluate("__h.LSQ.size") == 0, f'{q} ②b 다른 창이 쓴 표시(셋·넷)와 밀린 표시(둘)가 다 남음(옛: 밀린 값이 덮어 셋·넷이 사라짐) {xs} · c2 {len(A.get("c2", []))}')
        ok(set(M.get('ok', {})) == {'Q1', 'Q2', 'Q3'}, f"{q} ②b 채점도 합쳐 씀 {sorted(M.get('ok', {}))}")
        pg.evaluate("sessionStorage.setItem('q_full','ann.')"); pg.evaluate("v=>__h.LS.set('ann.ZZ',v)", {'c1': [m('하나')]}); pg.wait_for_timeout(200)
        pg.evaluate("sessionStorage.removeItem('q_full')"); pg.evaluate("__h.lsFlush()"); pg.wait_for_timeout(200)
        A = json.loads(pg.evaluate("k=>localStorage.getItem(k)", KA)); ok([o['x'] for o in A.get('c1', [])] == ['하나'] and 'c2' not in A, f'{q} ②b 다른 창이 안 썼으면 밀린 값 그대로(이 창에서 지운 표시가 되살아나지 않음) {A}')
        pg.evaluate("([a,b])=>{localStorage.removeItem(a);localStorage.removeItem(b);}", [KA, KM])

        # ---- ③ 다른 쿼터 백업 파일 → 안내(넣지 않음)
        boot(U + '#/')
        bad = {'app': IO['bakApp'], 'v': 2, 'at': '2026-11-01T00:00:00Z', 'dev': {}, 'data': {NO + 'mk.ZZ': '{"ok":{"Q09":1}}'}}
        pg.evaluate("t=>__h.fileRestore(t,'merge')", json.dumps(bad)); pg.wait_for_timeout(800)
        tt = pg.evaluate("(e=>e?e.textContent:'')(document.querySelector('#bakq'))")   # 오류 띠(#toasterr 안 id bakq)
        ok(f'{ko} 백업 파일이에요 — {sh} 허브(⇄)에서 넣어 주세요' in tt and f'⇄ {sh} 허브로' in tt and pg.evaluate("([a,b])=>localStorage.getItem(a)==null&&localStorage.getItem(b)==null", [N + 'mk.ZZ', NO + 'mk.ZZ']), f'{q} ③ 안내 {tt[:60]!r} · 기록은 안 들어감')
        pg.evaluate("t=>__h.fileRestore(t,'merge')", json.dumps({'app': 'zzz', 'data': {}})); pg.wait_for_timeout(600)
        ok('백업 파일을 읽지 못했어요' in pg.evaluate("document.querySelector('#toasterr').textContent"), f'{q} ③ 모르는 파일은 있던 글 그대로')

        # ---- ④ B1 형광펜 위치 찾기
        R = lambda t, o: pg.evaluate("([t,o])=>{const r=__h.Kit.resolve(t,o);return r?[r[0],t.slice(r[0],r[1])]:null}", [t, o])
        NEW = '치아 우식은 법랑질에서 시작한다. 치수 괴사 뒤에는 치근단 병소가 방사선 사진에서 보인다. 끝.'
        o = {'x': '치근단 병소', 'i': 0, 'p': '처치 전에 반드시 ', 's': '의 크기를 잰다', 'v': 'zz-other'}
        ok(R(NEW, o) is None, f'{q} ④ 블록 글이 바뀜 + 문장이 빠지고 같은 낱말이 다른 곳에 한 번 → 붙이지 않음(위치 잃음 · 옛: 조용히 옮겨 붙음)')
        o2 = dict(o, p='치수 괴사 뒤에는 ', s='가 방사선 사진에서'); r2 = R(NEW, o2)
        ok(r2 and r2[1] == '치근단 병소', f'{q} ④ 블록 글이 바뀌어도 앞뒤 문맥이 맞으면 붙음 {r2}')
        o3 = dict(o, x='치근단 병소가 방사선 사진에서 보인다'); r3 = R(NEW, o3)
        ok(r3 and r3[1] == o3['x'], f'{q} ④ 12자 이상은 지금처럼(후보 하나면 붙음) {r3}')
        o4 = {k: v for k, v in o.items() if k != 'v'}; r4 = R(NEW, o4)
        ok(r4 and r4[1] == '치근단 병소', f'{q} ④ 블록 지문이 없는 옛 표시는 지금처럼 {r4}')
        o5 = {'x': '병소', 'i': 0, 'p': None, 's': None}; o5.pop('p'); o5.pop('s')
        ok((R(NEW, o5) or [0, ''])[1] == '병소', f'{q} ④ 문맥 없는 옛 표시 = 후보가 하나면 그 자리(그대로)')

        # ---- ⑤ B3 ★ 카드 수 = 지금 있는 카드만 · 이관이 ★ 카드 북마크·회독 수도
        boot(U + f'#/{SJ}/_home'); wait(pg, f"!!(window.__h&&__h.PACKS['{SJ}'])")
        card = pg.evaluate("""S=>{const p=__h.PACKS[S];if(!p||!p.lect)return null;for(const L of p.lect){const m=/<article[^>]*class="[^"]*\\btc\\b[^"]*"[^>]*data-aid="([^"]+)"/.exec(L.learn||'')||/<article[^>]*data-aid="([^"]+)"[^>]*class="[^"]*\\btc\\b/.exec(L.learn||'');if(m)return [L.k,m[1]];}return null}""", SJ)
        if not card: print(f'  --   {q} ⑤ 카드가 있는 강의가 아직 없음(빈 과목) — 건너뜀')
        else:
            K0, A0 = card
            pg.evaluate("([N,S,a])=>localStorage.setItem(N+'cbm.'+S,JSON.stringify({[a]:1000,[S+':없어진강의:c1']:2000,[S+':없어진강의:c2']:3000}))", [N, SJ, A0])
            n = pg.evaluate("S=>[__h.cbmN(S),Object.keys(JSON.parse(localStorage.getItem(QCNS+'cbm.'+S))).length]".replace('QCNS', json.dumps(N)), SJ)
            stub = pg.evaluate("S=>__h.isStub(__h.PACKS[S])", SJ)
            ok(n == ([3, 3] if stub else [1, 3]), f'{q} ⑤ ★ 카드 수 = 지금 있는 카드만 {n[0]}(기록은 {n[1]}개 그대로 — 옛: 3)' + (' · 빈 과목(자료 대기)은 기록 수 그대로' if stub else ''))
            # 원고 갱신: 그 카드가 옛 aid(S:옛강의:c9)를 이어받음 → ★ 북마크·회독 수가 새 카드·새 강의 키로
            boot(U + f'#/{SJ}/{K0}', 2500)
            res = pg.evaluate("""([N,S,K,A])=>{const p=__h.PACKS[S],L=p.lect.find(x=>x.k===K),old=S+':옛강의:c9';L.learn=L.learn.replace('data-aid="'+A+'"','data-aid="'+A+'" data-alt="'+old+'"');
              localStorage.setItem(N+'cbm.'+S,JSON.stringify({[old]:1234,[S+':없어진강의:c1']:2000}));localStorage.setItem(N+'lrd.'+S,JSON.stringify({'옛강의':{n:3,at:5},'없어진강의':{n:1,at:6}}));
              delete __h.AIDX[S];delete __h.AMIG[S];__h.migrateAids(S);return [JSON.parse(localStorage.getItem(N+'cbm.'+S)),JSON.parse(localStorage.getItem(N+'lrd.'+S)),__h.lecAlias(S)]}""", [N, SJ, K0, A0])
            ok(res[0].get(A0) == 1234 and f'{SJ}:옛강의:c9' not in res[0] and res[0].get(f'{SJ}:없어진강의:c1') == 2000, f'{q} ⑤ ★ 카드 북마크가 새 카드로(표시한 때 그대로 · 이을 곳 없는 것은 그대로 둠) {res[0]}')
            ok(res[1].get(K0, {}).get('n') == 3 and '옛강의' not in res[1] and res[1].get('없어진강의', {}).get('n') == 1, f'{q} ⑤ 회독 수가 새 강의 키로 {res[1]} · 강의 키 이음 {res[2]}')
        ok(not errs, f'{q} 콘솔 오류 0 {errs[:2]}'); ctx.close()
    b.close()
done()
