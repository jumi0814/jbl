"""11-11 W5 백업·넘버링 기록 — ① 기출 번호 옮김(jbMove)이 넘버링 문제의 JB 연결도 따라감(C1 — src[].id·ref.id · 같은 새 번호 문제가 이미 있으면 둘 다 둠)
② 되돌리기/교체 창 '넘버링도 이 시점으로'(D1 — 선택 칸 켬/끔 · 미리 보기 수) ③ 동기화 충돌로 밀린 판(old) 목록 + [되살리기](D2 — 지금 것을 old로 보내고 바꿈 · 백업 파일에도).
4Q 뿌리와 3q/ 허브 둘 다(qsite — 한 주소) · 과목은 등록표·__h.PACKS에서 찾음(id를 박지 않음)."""
import json
from qsite import *
from playwright.sync_api import sync_playwright
rel = build(); base = serve()

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
        U = url(base, r); N = QS.QS[q]['ident']['ns']; SJ = (QS.sids(q) or [''])[0]; S2 = (QS.sids(q) + [''])[1]
        print(f'== {q} ({U})')
        ctx = b.new_context(viewport={'width': 1280, 'height': 900}); pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto(U + '#/'); pg.wait_for_timeout(1200); pg.evaluate("localStorage.clear();sessionStorage.clear()")
        pg.goto('about:blank'); pg.goto(U + f'#/{SJ}/_home'); ok(wait(pg, f"!!(window.__h&&__h.PACKS['{SJ}'])"), f'{q} 과목 팩 도착({SJ})')
        pg.evaluate("__h.xsReady()"); pg.wait_for_timeout(300)
        G = lambda k: pg.evaluate("k=>{const v=__h.stGet(k);try{return v==null?null:JSON.parse(v)}catch(e){return v}}", k)
        P = lambda k, v: pg.evaluate("([k,v])=>__h.stSet(k,JSON.stringify(v))", [k, v])
        def item(sub, iid, src, u, **kw):
            it = {'id': iid, 's': sub, 'kind': src[0]['t'] if src else 'user', 'lec': '', 'q': '문제 ' + iid, 'a': '답', 'st': '', 'note': '', 'tags': [], 'yrs': [], 'src': src, 'ref': ({'t': src[0]['t'], 's': src[0]['s'], 'id': src[0]['id']} if src else None), 'done': False, 'o': 1, 'c': u, 'u': u, 'del': False, 'rv': [], 'rvok': False, 'prev': None, 'pm': None}
            it.update(kw); P(f'num.i.{sub}.{iid}', it); return it

        # ---- ① C1 기출 번호 옮김 → 넘버링 문제의 JB 연결
        jb = lambda i: {'t': 'jb', 's': SJ, 'id': f'{SJ}:{i}', 'lec': '', 'yrs': [2024], 'lab': ''}
        item(SJ, f'jb:{SJ}:ZZ1', [jb('ZZ1')], 1000)                                   # 옛 번호 ZZ1 → ZZ2로 옮겨질 문제
        item(SJ, 'u_new', [jb('ZZ2')], 2000)                                           # 옮기기 전에 새 번호 카드에서 만든 문제(더 최근)
        item(SJ, f'jb:{SJ}:ZZ3', [jb('ZZ3'), {'t': 'pred', 's': SJ, 'id': f'{SJ}:ZZ3'}], 3000)   # ZZ3 → ZZ4(부딪힘 없음) · 예상문제 출처는 그대로
        item(SJ, 'u_keep', [jb('ZZ9')], 4000)                                          # 옮김 표에 없는 문제
        if S2: item(S2, 'other', [{'t': 'jb', 's': S2, 'id': f'{S2}:ZZ1', 'yrs': []}], 5000)   # 다른 과목 — 같은 번호여도 그대로
        P(f'num.r.{SJ}.jb:{SJ}:ZZ1', {'id': f'jb:{SJ}:ZZ1', 'h': [{'t': 900, 'm': 2, 's': 'sA'}], 'w': [], 'm': 2, 'd': 900, 'u': 900})
        before = {k: pg.evaluate("k=>__h.stGet(k)", k) for k in pg.evaluate("__h.stKeys('num.')")}
        pg.evaluate(f"(S=>{{const p=__h.PACKS[S];p.jbmove={{ZZ1:'ZZ2',ZZ3:'ZZ4'}};p.jbmovev='t1';delete __h.MIGP['n'+S];__h.migNum(S);}})('{SJ}')")
        ok(wait(pg, f"localStorage.getItem('{N}jbmovedN.{SJ}.t1')==='1'"), f'{q} ① 넘버링 몫 한 번 표시(jbmovedN.{SJ}.t1)')
        a = G(f'num.i.{SJ}.jb:{SJ}:ZZ1'); nw = G(f'num.i.{SJ}.u_new'); c = G(f'num.i.{SJ}.jb:{SJ}:ZZ3'); kp = G(f'num.i.{SJ}.u_keep')
        ok(a and a['src'][0]['id'] == f'{SJ}:ZZ2' and a['ref']['id'] == f'{SJ}:ZZ2' and a['id'] == f'jb:{SJ}:ZZ1' and a['u'] == 1000, f"{q} ① src·ref가 새 번호로(문제 id·u 그대로) {a and (a['src'][0]['id'], a['ref']['id'], a['id'], a['u'])}")
        ok(c and c['src'][0]['id'] == f'{SJ}:ZZ4' and c['src'][1]['id'] == f'{SJ}:ZZ3' and c['ref']['id'] == f'{SJ}:ZZ4' and 'dj' not in c, f"{q} ① 예상문제 출처는 그대로 · 부딪힘 없으면 표시 없음 {c and [x['id'] for x in c['src']]}")
        ok(nw and nw.get('dj', {}).get('id') == f'jb:{SJ}:ZZ1' and 'dj' not in a and not a['del'] and not nw['del'], f"{q} ① 같은 새 번호 문제가 이미 있음 → 둘 다 둠 · 더 최근(u) 쪽에 표시 dj {nw and nw.get('dj')}")
        ok(json.dumps(kp, sort_keys=True) == json.dumps(json.loads(before[f'num.i.{SJ}.u_keep']), sort_keys=True) and (not S2 or pg.evaluate("k=>__h.stGet(k)", f'num.i.{S2}.other') == before[f'num.i.{S2}.other']), f'{q} ① 옮김 표에 없는 문제·다른 과목은 그대로')
        ok(pg.evaluate("k=>__h.stGet(k)", f'num.r.{SJ}.jb:{SJ}:ZZ1') == before[f'num.r.{SJ}.jb:{SJ}:ZZ1'] and len(pg.evaluate("__h.stKeys('num.i.')")) == len([k for k in before if k.startswith('num.i.')]), f'{q} ① 복습 기록·문제 수 그대로(지운 것 0)')
        bl = pg.evaluate("__h.bkList().then(L=>L.map(x=>x.why||x.r||''))")
        ok(any('이관' in str(x) for x in bl), f'{q} ① 옮기기 전 자동 백업 {bl[:3]}')
        ok(pg.evaluate(f"__h.jbMoveNum('{SJ}')") is False, f'{q} ① 두 번째는 아무것도 안 함(한 번만)')
        # ---- ② D1 '넘버링도 이 시점으로' — 넘버링을 고친 뒤 자동 백업 시점으로 되돌리기(선택 칸 끔 = 넘버링 그대로 · 켬 = 넘버링도)
        msgs = []; pg.on('dialog', lambda d: (msgs.append(d.message), d.accept()))
        def boot(u, ms=1500):
            pg.goto('about:blank'); pg.goto(u); pg.wait_for_timeout(ms); wait(pg, "!!(window.__h&&__h.xsReady)"); pg.evaluate("__h.xsReady()"); pg.wait_for_timeout(200)
        boot(U + '#/'); pg.evaluate("(async()=>{for(const k of __h.stKeys('num.'))localStorage.removeItem(k);})()")
        pg.evaluate("N=>{for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(k.indexOf(N+'num.')===0)localStorage.removeItem(k);}}", N)
        L = lambda k, v: pg.evaluate("([k,v])=>localStorage.setItem(k,JSON.stringify(v))", [N + k, v])
        item(SJ, 'A', [], 1000, q='A 옛 글'); item(SJ, 'B', [], 1000, q='B 글')
        P(f'num.r.{SJ}.A', {'id': 'A', 'h': [{'t': 900, 'm': 0, 's': 's1'}], 'w': [], 'm': 0, 'd': 900, 'u': 900}); L(f'exam.{SJ}', {'d': '2026-12-01'}); L(f'cbm.{SJ}', {'X': 1})
        pg.evaluate("__h.autoBak(true,'시험 시점')"); pg.wait_for_timeout(1500)
        def later():
            item(SJ, 'A', [], 5000, q='A 새 글'); pg.evaluate("k=>localStorage.removeItem(k)", N + f'num.i.{SJ}.B'); item(SJ, 'C', [], 6000, q='C 새 문제')
            P(f'num.r.{SJ}.A', {'id': 'A', 'h': [{'t': 900, 'm': 0, 's': 's1'}, {'t': 7000, 'm': 2, 's': 's2'}], 'w': [], 'm': 2, 'd': 7000, 'u': 7000}); L(f'exam.{SJ}', {'d': '2026-12-20'}); L(f'cbm.{SJ}', {'X': 1, 'Y': 2})
        def state(): return [(G(f'num.i.{SJ}.A') or {}).get('q'), G(f'num.i.{SJ}.B') is not None, G(f'num.i.{SJ}.C') is not None, len((G(f'num.r.{SJ}.A') or {}).get('h', [])), (G(f'exam.{SJ}') or {}).get('d'), sorted(G(f'cbm.{SJ}') or {})]
        def snap(num):
            boot(U + '#/'); pg.evaluate("__h.openRestore()"); wait(pg, "!!document.querySelector('#rpop [data-snap]')")
            sid = pg.evaluate("__h.bkList().then(L=>(L.find(x=>x.why==='시험 시점')||{}).id)")
            if num: pg.check('#rnum')
            del msgs[:]
            try:
                with pg.expect_navigation(timeout=15000): pg.evaluate("id=>{document.querySelector('#rpop [data-snap=\"'+id+'\"]').click()}", sid)
            except Exception: pass
            pg.wait_for_timeout(1500); wait(pg, "!!(window.__h&&__h.xsReady)"); pg.evaluate("__h.xsReady()"); pg.wait_for_timeout(300)
        later(); ok(state() == ['A 새 글', False, True, 2, '2026-12-20', ['X', 'Y']], f'{q} ② 고친 뒤 상태 {state()}')
        boot(U + '#/'); pg.evaluate("__h.openRestore()"); wait(pg, "!!document.querySelector('#rpop #rnum')")
        lab = pg.evaluate("document.querySelector('#rnum').closest('label').textContent"); ok('넘버링도 이 시점으로' in lab and pg.evaluate("document.querySelector('#rnum').checked") is False, f'{q} ② 복원 창 선택 칸(기본 끔) {lab[:40]!r}')
        pg.screenshot(path=os.path.join(ROOT, 'work', '_tmp', f'q_backup_rnum_{q}.png'))
        snap(False)
        ok(state() == ['A 새 글', False, True, 2, '2026-12-20', ['X']] and any('넘버링은 지금 그대로' in m for m in msgs), f'{q} ② 선택 칸 끔 → 표시만 되돌아가고 넘버링·시험 날짜는 그대로 {state()}')
        later(); tb = pg.evaluate("Date.now()"); snap(True)
        pv = next((m for m in msgs if '넘버링도 이 시점으로' in m), '')
        ok('이 시점 뒤에 고친 문제 1개가 그때 글로 돌아가고' in pv and '뒤에 새로 만든 1개가 사라지고' in pv and '뒤에 지운 1개가 다시 생깁니다' in pv, f'{q} ② 미리 보기 수(문제마다 u) {pv[pv.find("넘버링도"):][:110]!r}')
        ok(state() == ['A 옛 글', True, False, 1, '2026-12-01', ['X']], f'{q} ② 선택 칸 켬 → 넘버링 문제·복습 기록·시험 날짜도 그 시점으로 {state()}')
        bk = pg.evaluate("(async S=>{const L=await __h.bkList();const m=L.filter(x=>x.why==='되돌리기 전').sort((a,b)=>b.at-a.at)[0];if(!m)return null;const r=await __h.bkLoad(m.id);return Object.keys(r.data).filter(k=>k.indexOf('num.i.'+S+'.C')>=0).length})(%s)" % json.dumps(SJ))
        ok(bk == 1, f'{q} ② 되돌리기 전 상태(새 문제 C 포함)는 자동 백업에 남음 {bk}')

        # ---- ②b 11-11 메인 결정 5: 되돌린 넘버링 문제는 u = 지금 → 다른 기기에 더 최근 판(되돌리기 1분 전에 고친 것)이 있어도 동기화에서 되돌린 판이 이김(옛: u 1000 < 그 판 → 조용히 원래대로)
        kA = f'num.i.{SJ}.A'; a = G(kA); bb = G(f'num.i.{SJ}.B')
        ok(a and a['q'] == 'A 옛 글' and a['u'] >= tb and a['c'] == 1000 and bb and bb['u'] >= tb, f"{q} ②b 되돌린 문제·다시 생긴 문제의 u = 지금(만든 때 c는 그대로) {a and (a['u'] >= tb, a['c'])}")
        loc = json.dumps(a, ensure_ascii=False); rem = json.dumps(dict(a, q='A 다른 기기 글', u=tb - 60000), ensure_ascii=False); bas = json.dumps(dict(a, q='A 새 글', u=5000), ensure_ascii=False)
        m1 = pg.evaluate("([k,b,l,r])=>__h.syncMerge3(k,b,l,r)", [kA, bas, loc, rem]); m2 = pg.evaluate("([k,b,l,r])=>__h.syncMerge3(k,b,l,r)", [kA, bas, rem, loc])
        ok(m1 and json.loads(m1)['q'] == 'A 옛 글' and m2 and json.loads(m2)['q'] == 'A 옛 글', f"{q} ②b 되돌린 뒤 동기화해도 되돌린 판 유지(둘 다 바뀜 = 3방향 — 이 기기·그 기기 어느 쪽에서 합쳐도) {m1 and json.loads(m1)['q']!r}·{m2 and json.loads(m2)['q']!r}")
        old1 = json.dumps(dict(a, u=1000), ensure_ascii=False); m0 = pg.evaluate("([k,b,l,r])=>__h.syncMerge3(k,b,l,r)", [kA, bas, old1, rem])
        ok(m0 and json.loads(m0)['q'] == 'A 다른 기기 글', f"{q} ②b (견줌) u를 안 올린 옛 동작이면 다른 기기 판이 이겼음 {m0 and json.loads(m0)['q']!r}")
        ok(pg.evaluate("([x,l])=>__h.xsWin(x,l)", [loc, rem]) == 'x', f'{q} ②b 다른 창이 옛 판을 써도 되돌린 판 유지(xsWin)')
        rr = G(f'num.r.{SJ}.A'); ok(rr and 'u' in rr and rr['u'] == 900, f"{q} ②b 복습 기록은 백업 것 그대로(u 안 올림) {rr and rr.get('u')}")

        # ---- ③ D2 동기화로 밀린 판 목록 + [되살리기] · 30일·200줄 정리 · 백업 파일
        old_v = json.dumps(dict(G(f'num.i.{SJ}.A'), q='<p>A <b>밀린</b> 글</p>', u=500), ensure_ascii=False); key = f'num.i.{SJ}.A'
        pg.evaluate("([k,v])=>__h.xsOld([{k,v,why:'다른 기기 동기화로 바뀌기 전',dev:'아이패드'}])", [key, old_v]); pg.wait_for_timeout(300)
        boot(U + '#/'); pg.evaluate("__h.openRestore()"); ok(wait(pg, "!!document.querySelector('#rpop #rold')"), f'{q} ③ 복원 창에 밀린 판 목록')
        row = pg.evaluate("[document.querySelector('#rold summary').textContent,document.querySelector('#rold .row').textContent]")
        ok('밀린 넘버링 판 1개' in row[0] and 'A 밀린 글' in row[1] and '아이패드' in row[1] and '되살리기' in row[1], f'{q} ③ 목록 = 문제 제목·때·기기 {row}')
        pg.evaluate("document.querySelector('#rold').open=true"); pg.screenshot(path=os.path.join(ROOT, 'work', '_tmp', f'q_backup_old_{q}.png'))
        t0 = pg.evaluate("Date.now()"); pg.evaluate("document.querySelector('#rold [data-oldre]').click()"); wait(pg, "k=>false", 1); pg.wait_for_timeout(2000)
        a = G(key); olds = pg.evaluate("__h.xsOldLoad()")
        ok(a and '밀린' in a['q'] and a['u'] >= t0, f"{q} ③ [되살리기] → 그 판으로 바뀜 · u = 지금(다시 밀리지 않게) {a and a['q']}")
        ok(len(olds) == 1 and 'A 옛 글' in olds[0]['v'] and olds[0]['why'] == '되살리기 전', f"{q} ③ 지금 있던 것은 밀린 판으로 감(지운 것 0) {[(o['why'], o.get('dev')) for o in olds]}")
        ok(pg.evaluate("(document.querySelector('#rold summary')||{}).textContent||''").find('1개') >= 0, f'{q} ③ 목록 다시 그림')
        bf = pg.evaluate("__h.bakFile().old||[]"); ok(len(bf) == 1 and bf[0]['k'] == key and 'id' not in bf[0], f'{q} ③ 백업 파일에 밀린 판 포함({len(bf)}줄)')
        n1 = pg.evaluate("([k,v])=>__h.xsOldIn([{k,v,at:1794000000000,why:'다른 기기에서 지워짐',dev:'맥'}])", [key, old_v]); n2 = pg.evaluate("([k,v])=>__h.xsOldIn([{k,v,at:1794000000000,why:'다른 기기에서 지워짐',dev:'맥'}])", [key, old_v])
        ok(n1 == 1 and n2 == 0, f'{q} ③ 백업 파일의 밀린 판을 받음(같은 줄은 한 번만) {n1}·{n2}')
        pg.evaluate("([k,v])=>__h.xsOld([{k,v,at:Date.now()-40*864e5,why:'오래됨'}].concat(Array.from({length:205},(_, i)=>({k:k+'.z'+i,v,why:'많음'}))),true)", [key, old_v]); pg.wait_for_timeout(500)
        olds = pg.evaluate("__h.xsOldLoad()"); ok(len(olds) == 200 and not any(o['why'] == '오래됨' for o in olds), f'{q} ③ 30일·200줄 넘으면 정리({len(olds)}줄 · 오래된 것 {sum(1 for o in olds if o["why"] == "오래됨")})')
        # ---- ④ F1 넘버링 화면을 떠날 때 열린 '새 문제' 창의 글 = 초안으로 남김(다시 열면 이어 쓰기) · F2 Word 파일 이름 날짜 = 허브 day()
        NEWNUM = 'draftKeep' in open(os.path.join(SITE, r, 'num', 'num.js'), encoding='utf-8').read()   # 3Q 허브(보관)는 넘버링 모듈도 옛 것(docs/3q/num) — 새 num.js 시험은 건너뜀
        if not NEWNUM:
            print(f'  --   {q} ④⑤ 이 허브의 넘버링 모듈은 보관된 옛 판 — 새 num.js 시험(F1·C2 화면)은 건너뜀'); ok(not errs, f'{q} 콘솔 오류 0 {errs[:2]}'); ctx.close(); continue
        boot(U + f'#/_num/{SJ}', 2500); ok(wait(pg, "!!document.querySelector('#numv [data-act=new]')"), f'{q} ④ 내 넘버링 열림')
        pg.click('#numv [data-act=new]'); pg.wait_for_timeout(400); pg.click('.nm-ov [data-rich=q]'); pg.keyboard.type('쓰다 만 문제 3가지를 쓰시오.'); pg.fill('.nm-ov [data-nf=yrs]', '25'); pg.fill('.nm-ov [data-nf=note]', '참고')
        n_items = len(pg.evaluate("__h.stKeys('num.i.')"))
        pg.evaluate("location.hash='#/'"); pg.wait_for_timeout(1200)
        d = pg.evaluate("k=>JSON.parse(localStorage.getItem(k)||'null')", N + 'num.draft')
        ok(d and '쓰다 만 문제' in d['q'] and d['yrs'] == '25' and d['note'] == '참고' and len(pg.evaluate("__h.stKeys('num.i.')")) == n_items, f"{q} ④ 떠날 때 초안으로 남김(옛: 묻지 않고 버림) {d and d['q'][:30]!r}")
        pg.evaluate(f"location.hash='#/_num/{SJ}'"); wait(pg, "!!document.querySelector('#numv [data-act=new]')"); pg.wait_for_timeout(600); pg.click('#numv [data-act=new]'); pg.wait_for_timeout(500)
        back = pg.evaluate("(o=>o?[o.querySelector('[data-rich=q]').textContent,o.querySelector('[data-nf=yrs]').value,o.querySelector('[data-nf=note]').value,o.querySelector('[data-nf-msg]').textContent]:null)(document.querySelector('.nm-ov'))")
        ok(back and '쓰다 만 문제 3가지' in back[0] and back[1] == '25' and back[2] == '참고' and '이어서 열었어요' in back[3], f'{q} ④ 다시 열면 이어 쓰기 {back}')
        pg.click('.nm-ov [data-nfsave]'); pg.wait_for_timeout(600)
        ok(pg.evaluate("k=>JSON.parse(localStorage.getItem(k)||'null')", N + 'num.draft') is None and len(pg.evaluate("__h.stKeys('num.i.')")) == n_items + 1, f'{q} ④ 저장하면 초안 지움 · 문제 +1')
        pg.click('#numv [data-act=new]'); pg.wait_for_timeout(400)
        ok(pg.evaluate("document.querySelector('.nm-ov [data-rich=q]').textContent.trim()") == '', f'{q} ④ 그다음 새 문제 창은 빈 칸')
        pg.evaluate("document.querySelector('.nm-ov [data-x]').click()"); pg.wait_for_timeout(300)
        # ---- ⑤ C2 실제 화면: 넘버링 복습에서 평가 → 같은 것을 다시 눌러 지움 = 지움 표시 {t,s,x:1}(줄을 빼지 않음) → 다른 평가
        boot(U + f'#/_numr/{SJ}', 2500); ok(wait(pg, "!!document.querySelector('#numv [data-mk]')"), f'{q} ⑤ 넘버링 복습 열림')
        rid = pg.evaluate("(b=>{const a=b.closest('[data-id]');b.click();return a.dataset.id})(document.querySelector('#numv [data-mk=\"0\"]'))"); pg.wait_for_timeout(500)
        sid = (G(f'num.rs.{SJ}') or {}).get('sid'); r1 = G(f'num.r.{SJ}.{rid}') or {}
        ok(sid and [e for e in r1.get('h', []) if e.get('s') == sid] and r1.get('m') == 0, f"{q} ⑤ 모름 평가 → 이 회차 줄 {[e for e in r1.get('h', []) if e.get('s') == sid]}")
        pg.evaluate("id=>document.querySelector('#numv [data-id=\"'+CSS.escape(id)+'\"] [data-mk=\"0\"]').click()", rid); pg.wait_for_timeout(500)
        r2 = G(f'num.r.{SJ}.{rid}') or {}; cur = [e for e in r2.get('h', []) if e.get('s') == sid]; lv = [e for e in r2.get('h', []) if not e.get('x')]
        ok(len(cur) == 1 and cur[0].get('x') == 1 and 'm' not in cur[0] and r2.get('m') == (lv[-1]['m'] if lv else None) and len(r2['h']) == len(r1['h']), f"{q} ⑤ 다시 눌러 지움 → 지움 표시(줄 수 그대로 {len(r2.get('h', []))}) · 최근 평가 = 그 앞 회차 것 {r2.get('m')}")
        ui = pg.evaluate("id=>{const a=document.querySelector('#numv [data-id=\"'+CSS.escape(id)+'\"]');return [a.classList.contains('mk0'),[...a.querySelectorAll('[data-mk].on')].length,(a.querySelector('.nm-rf [data-ract=hist]')||{}).textContent||'']}", rid)
        ok(ui[0] is False and ui[1] == 0 and ui[2].strip() == ('이력' + (' ' + str(len(lv)) if lv else '')), f'{q} ⑤ 화면: 평가 꺼짐 · 이력 수는 지움 표시를 안 셈 {ui}')
        pg.evaluate("id=>document.querySelector('#numv [data-id=\"'+CSS.escape(id)+'\"] [data-mk=\"2\"]').click()", rid); pg.wait_for_timeout(500)
        r3 = G(f'num.r.{SJ}.{rid}') or {}; cur = [e for e in r3.get('h', []) if e.get('s') == sid]
        ok(len(cur) == 1 and cur[0].get('m') == 2 and not cur[0].get('x') and r3.get('m') == 2 and len(r3['h']) == len(r1['h']), f"{q} ⑤ 다시 평가(암기 완료) → 그 회차 한 줄 {cur}")
        ok(not errs, f'{q} 콘솔 오류 0 {errs[:2]}'); ctx.close()
    b.close()
done()
