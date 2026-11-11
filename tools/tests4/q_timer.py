"""11-10 W4 공부 시간 — 잠든 시간 자동 빼기(T1)·시계 뒤로(T2)·쿼터 공용 시계 채널(T3)·tedit 자동 줄임 한 줄(T4)·4Q 2차 가져오기 qimport2(T5)·닫힘 표시 cls(T6).
가짜 시계(page.clock — ux3_timer와 같은 방식 · fast_forward = 기기가 잠든 채 시간이 한 번에 흐름 · run_for = 깨어 있는 채 1초 틱이 다 돎) · 시간대 Asia/Seoul(하루 경계 06:00).
4Q 뿌리와 3q/ 허브 둘 다(qsite — 한 주소) · 과목은 등록표·__h.PACKS에서 찾음(id를 박지 않음)."""
import json, datetime
from qsite import *
from playwright.sync_api import sync_playwright
KST = datetime.timezone(datetime.timedelta(hours=9)); MIN = 60000; HR = 60 * MIN
def T(*a): return datetime.datetime(*a, tzinfo=KST)
rel = build(); base = serve()

def mk(b, when):
    ctx = b.new_context(viewport={'width': 1280, 'height': 900}, timezone_id='Asia/Seoul', locale='ko-KR'); ctx.clock.install(time=when)
    pg = ctx.new_page(); pg._errs = []; pg.on('pageerror', lambda e: pg._errs.append(str(e)[:200])); return ctx, pg
def boot(pg, u, ms=1500):
    pg.goto('about:blank'); pg.goto(u); pg.clock.run_for(ms)
    for _ in range(150):
        if pg.evaluate("!!(window.__h&&__h.plStat&&__h.plStat().pend===0)"): break
        pg.wait_for_timeout(100); pg.clock.run_for(100)

with sync_playwright() as p:
    b = p.chromium.launch()
    for q, r in rel.items():
        U = url(base, r); N = QS.QS[q]['ident']['ns']; SJ = (QS.sids(q) or [''])[0]; HOME = U + '#/'; DOC = U + (f'#/{SJ}/_home' if SJ else '#/')
        print(f'== {q} ({U})')
        def ls(pg, k):
            v = pg.evaluate("k=>localStorage.getItem(k)", N + k); return json.loads(v) if v else None
        def tot(pg, d=''):   # 공부 합계(ms) = time + tedit(되돌린 것·휴식 몫 빼고) — d 없으면 모든 날
            return pg.evaluate("""([N,d])=>{const J=k=>{try{return JSON.parse(localStorage.getItem(N+k)||'null')}catch(e){return null}},t=J('time')||{};let v=0;
              for(const k in t)if(!d||k===d)for(const s in t[k])v+=+t[k][s]||0;(J('tedit')||[]).forEach(e=>{if(e&&!e.x&&e.f!=='r'&&(!d||e.d===d))v+=+e.ms||0});return v}""", [N, d])
        def band(pg): return pg.evaluate("(b=>b.hidden?'':b.dataset.k+'|'+b.textContent)(document.querySelector('#trband'))")
        def st(pg): return pg.evaluate("__h.trState()")
        def fresh(b_, when, extra='', u=None):
            ctx, pg = mk(b_, when); boot(pg, u or HOME); pg.evaluate("([N,x])=>{localStorage.clear();sessionStorage.clear();localStorage.setItem(N+'tauto','false');if(x)eval(x)}", [N, extra]); boot(pg, u or HOME); return ctx, pg

        # ---- T1 ① ▶ 뒤 100분 잠듦 → 묻지 않고 마지막 입력 +1분에서 끝 · 알림 + 되돌리기
        ctx, pg = fresh(b, T(2026, 11, 10, 10, 0, 0))
        pg.evaluate("S=>__h.trStart({S,D:''})", SJ); pg.clock.run_for(5000)
        ok(st(pg) == 'sess', '▶ 공부 시작 → 세션')
        pg.clock.fast_forward(100 * MIN); pg.clock.run_for(2000)
        v = tot(pg); bd = band(pg)
        ok(st(pg) not in ('sess', 'rest', 'end') and ls(pg, 'tstate') is None, f'100분 잠듦 → 세션 끝(묻지 않음) · 상태 {st(pg)}')
        ok(abs(v - MIN) <= 2000, f'100분 잠듦 → 공부 +{v / 1000:.0f}초 (마지막 입력 +1분 = 60)')
        ok(bd.startswith('slept|') and '잠든 1시간 39분은 공부 시간에서 뺐어요' in bd and '되돌리기' in bd, f'알림 띠 {bd!r}')
        ok('12시간' not in (pg.inner_text('#toast') or '') and '세션 끝' not in (pg.evaluate("(e=>e.style.display==='none'?'':e.textContent)(document.querySelector('#toast'))")), '알림은 띠 하나(세션 끝 알림 없음)')
        pg.screenshot(path=os.path.join(ROOT, 'work', '_tmp', f'q_timer_slept_{q}.png'))
        # 다음 입력 뒤에도 30초는 남음 → 그 뒤 닫힘은 아래 ③에서 · 여기선 입력 10초 뒤에도 남아 있는지
        pg.mouse.move(400, 300); pg.mouse.click(400, 300); pg.clock.run_for(10000)
        ok(band(pg).startswith('slept|'), '입력 10초 뒤에도 알림 남음')
        pg.evaluate("__h.trStart()"); pg.clock.run_for(1000)
        ok(band(pg).startswith('slept|'), '▶ 다시 시작해도 알림 남음'); pg.evaluate("__h.trStop()"); pg.clock.run_for(500)
        v0 = tot(pg)
        pg.evaluate("document.querySelector('#trband [data-trq=slback]').click()"); pg.clock.run_for(4000)   # 앞의 '세션 끝' 알림(3초) 뒤에 되돌림 알림
        v1 = tot(pg); te = [e for e in (ls(pg, 'tedit') or []) if e.get('k') == 'add' and not e.get('x')]
        ok(abs((v1 - v0) - (99 * MIN + 5000)) <= 3000 and len(te) == 1 and te[0]['S'] == (SJ or '기타'), f'[되돌리기] → +{(v1 - v0) / MIN:.2f}분 다시 넣음(99.08) · tedit add {len(te)}줄 · 과목 {te and te[0]["S"]}')
        ok(band(pg) == '' and ls(pg, 'tstate.slp') is None, '되돌린 뒤 알림 닫힘')
        tt = pg.evaluate("(e=>e.style.display==='none'?'':e.textContent)(document.querySelector('#toast'))"); ok('다시 넣었어요' in tt and '되돌리기' in tt, f'되돌림 알림 {tt[:50]!r}')
        pg.evaluate("document.querySelector('#toast .tact').click()"); pg.clock.run_for(500)
        ok(abs(tot(pg) - v0) <= 1000, f'되돌림의 [되돌리기](있던 시간 고침 되돌리기 길) → 다시 빠짐 ({(tot(pg) - v0) / 1000:.0f}초)')
        ok(not pg._errs, f'pageerror 0 ({pg._errs[:2]})'); ctx.close()

        # ---- T1 ② 30분 잠듦 → 전부 셈(화면이 잠긴 채 책으로 공부)
        ctx, pg = fresh(b, T(2026, 11, 10, 10, 0, 0))
        pg.evaluate("S=>__h.trStart({S,D:''})", SJ); pg.clock.run_for(5000)
        pg.clock.fast_forward(30 * MIN); pg.clock.run_for(25000)
        v = tot(pg); ok(st(pg) == 'sess' and abs(v - (30 * MIN + 30000)) <= 22000 and band(pg) == '', f'30분 잠듦 → 전부 셈 +{v / MIN:.2f}분 · 세션 그대로 · 알림 없음({band(pg)!r})')
        # 이어서 깨어 있는 채 입력만 없음 → 90분에 되묻기 띠(지금 그대로)
        pg.clock.run_for(60 * MIN)
        ok(band(pg).startswith('ask|') and '입력이 없어요' in band(pg), f'깨어 있는 채 무입력 90분 → 되묻기 띠 그대로 {band(pg)[:30]!r}')
        ok(not pg._errs, f'pageerror 0 ({pg._errs[:2]})'); ctx.close()

        # ---- T1 ③ 8시간 잠듦(탭이 버려졌다 다시 열림 = 시작 때 길) · 06:00 경계 · 이미 기록한 몫 되돌림 · 시계 숫자
        NOW = T(2026, 11, 10, 10, 0, 0); now = int(NOW.timestamp() * 1000); D0, D1 = '2026-11-09', '2026-11-10'
        seed = {'st': 'sess', 't0': now - 8 * HR - 20 * MIN, 'seg': now - 8 * HR, 'f0': now - 8 * HR - 20 * MIN, 'S': SJ, 'D': '', 'at': now - 8 * HR, 'd': D0, 'own': 'deadwin', 'li': now - 8 * HR - 20 * MIN, 'sum': 20 * MIN, 'rsum': 0, 'hid': now - 8 * HR}
        ctx, pg = fresh(b, NOW)
        num = pg.evaluate("""([N,s,d,S])=>{localStorage.setItem(N+'tstate',JSON.stringify(s));localStorage.setItem(N+'time',JSON.stringify({[d]:{[S||'기타']:20*60000}}));
          __h.T.tk=s.at;__h.T.inp=0;__h.sessFlush();return [__h.trSessTxt(),JSON.parse(localStorage.getItem(N+'tstate')).at,__h.tDay(d)]}""", [N, seed, D0, SJ])
        ok(num[1] == seed['at'] and sum(num[2].values()) <= 21 * MIN + 1000, f'잠든 간격은 sessFlush가 기록하지 않음 · 그날 합계(진행 중 몫 포함) {sum(num[2].values()) / MIN:.1f}분 ≤ 21 · 세션 시계 {num[0]}(부풀지 않음)')
        boot(pg, HOME)
        bd = band(pg); v = tot(pg)
        ok(ls(pg, 'tstate') is None and bd.startswith('slept|') and '잠든 8시간 19분' in bd, f'다시 열림(시작 때) → 질문 대신 자동으로 빼고 알림 {bd[:40]!r}')
        ok(abs(v - MIN) <= 1000, f'8시간 잠듦 → 합계 {v / MIN:.2f}분 (20분 기록 중 마지막 입력 +1분만 = 1.00)')
        boot(pg, HOME); ok(band(pg).startswith('slept|'), '새로고침해도 알림 남음(기기 전용 tstate.slp)')
        pg.evaluate("document.querySelector('#trband [data-trq=slback]').click()"); pg.clock.run_for(500)
        te = [e for e in (ls(pg, 'tedit') or []) if e.get('k') == 'add' and not e.get('x')]; byd = {e['d']: e['ms'] for e in te}
        ok(set(byd) == {D0, D1} and abs(byd[D0] - (4 * HR + 19 * MIN)) <= 1000 and abs(byd[D1] - 4 * HR) <= 20000 and len({e.get('p') for e in te}) == 1,
           f'되돌리기 → 06:00에서 두 날로 나눔 {D0} {byd.get(D0, 0) / MIN:.1f}분(259) · {D1} {byd.get(D1, 0) / MIN:.1f}분(240) · 한 묶음')
        sg = ls(pg, 'tseg') or {}; m0 = [x for x in sg.get(D0, []) if x[4] == 'm']; m1 = [x for x in sg.get(D1, []) if x[4] == 'm']
        ok(len(m0) == 1 and len(m1) == 1 and m0[0][1] == 86400 and m1[0][0] == 0, f"구간 'm' 날마다 하나 — {D0} {m0} · {D1} {m1}")
        ok(abs(tot(pg) - (MIN + 8 * HR + 19 * MIN)) <= 21000, f'되돌린 뒤 합계 {tot(pg) / MIN:.1f}분 (500)')
        # 알림은 다음 입력 30초 뒤 닫힘 — 새 알림으로
        ok(not pg._errs, f'pageerror 0 ({pg._errs[:2]})'); ctx.close()

        # ---- T1 ④ 자정·06:00을 낀 잠듦(23:00 ▶ → 07:00) · 알림은 다음 입력 30초 뒤 닫힘
        ctx, pg = fresh(b, T(2026, 11, 9, 23, 0, 0))
        pg.evaluate("S=>__h.trStart({S,D:''})", SJ); pg.clock.run_for(5000)
        pg.clock.fast_forward(8 * HR); pg.clock.run_for(2000)
        bd = band(pg); ok(bd.startswith('slept|') and '잠든 7시간 59분' in bd and abs(tot(pg, D0) - MIN) <= 2000 and tot(pg, D1) == 0, f'23:00 ▶ → 07:00 → {D0} {tot(pg, D0) / 1000:.0f}초(60) · {D1} {tot(pg, D1) / 1000:.0f}초(0) · {bd[:36]!r}')
        pg.mouse.move(400, 300); pg.mouse.click(400, 300); pg.clock.run_for(20000); a20 = band(pg); pg.clock.run_for(15000)
        ok(a20.startswith('slept|') and band(pg) == '' and ls(pg, 'tstate.slp') is None, f'다음 입력 뒤 20초엔 남고 35초엔 닫힘 ({a20[:8]!r} → {band(pg)!r})')
        ok(not pg._errs, f'pageerror 0 ({pg._errs[:2]})'); ctx.close()

        # ---- T1 ⑤ 되묻기 끔 → 지금 그대로(12시간 상한)
        ctx, pg = fresh(b, T(2026, 11, 10, 10, 0, 0), "localStorage.setItem(N+'sessAsk','0')")
        pg.evaluate("S=>__h.trStart({S,D:''})", SJ); pg.clock.run_for(1000)
        pg.clock.fast_forward(12 * HR + 5 * MIN); pg.clock.run_for(2000)
        v = tot(pg); ok(st(pg) not in ('sess', 'rest', 'end') and abs(v - 12 * HR) <= 5000 and not band(pg).startswith('slept|'), f'되묻기 끔 · 12시간 5분 잠듦 → 12시간 상한 +{v / HR:.3f}시간 · 잠든 시간 알림 없음')
        ok(not pg._errs, f'pageerror 0 ({pg._errs[:2]})'); ctx.close()

        # ---- T2 시계 뒤로(세션) — 기준을 지금으로 다시 잡고 계속 잼
        ctx, pg = fresh(b, T(2026, 11, 10, 10, 0, 0))
        pg.evaluate("S=>__h.trStart({S,D:''})", SJ); pg.clock.run_for(30000); v0 = tot(pg)
        pg.clock.set_system_time(T(2026, 11, 10, 9, 0, 0)); pg.clock.run_for(65000)
        ts = ls(pg, 'tstate'); nw = pg.evaluate("Date.now()"); v = tot(pg)
        ok(ts and ts['st'] == 'sess' and ts['seg'] <= nw and ts['t0'] <= nw and v - v0 >= 40000, f'세션 중 시계 1시간 뒤로 → 65초 동안 +{(v - v0) / 1000:.0f}초(≥40 — 옛: 0) · seg·t0 ≤ 지금')
        ok(not band(pg).startswith('slept|'), '시계 뒤로는 잠든 시간이 아님'); ok(not pg._errs, f'pageerror 0 ({pg._errs[:2]})'); ctx.close()
        # 자동 측정
        if SJ:
            ctx, pg = fresh(b, T(2026, 11, 10, 10, 0, 0), "localStorage.setItem(N+'tauto','true')", DOC)
            for i in range(3): pg.mouse.move(400 + i * 9, 400); pg.mouse.wheel(0, 2); pg.mouse.click(600, 12); pg.clock.run_for(5000)
            if st(pg) == 'run':
                pg.evaluate("dispatchEvent(new Event('pagehide'))"); v0 = tot(pg)
                pg.clock.set_system_time(T(2026, 11, 10, 9, 0, 0))
                for i in range(6): pg.mouse.move(420 + i * 9, 420); pg.mouse.wheel(0, 2); pg.clock.run_for(10000)
                pg.evaluate("dispatchEvent(new Event('pagehide'))"); v = tot(pg)
                ok(v - v0 >= 40000, f'자동 측정 중 시계 1시간 뒤로 → 60초 동안 +{(v - v0) / 1000:.0f}초(≥40 — 옛: 0)')
            else: print(f'  --   {q}: 과목 화면에서 자동 측정이 안 돎(상태 {st(pg)}) — 자동 측정 시계 뒤로는 건너뜀')
            ok(not pg._errs, f'pageerror 0 ({pg._errs[:2]})'); ctx.close()

        # ---- T6 닫힘 표시(cls)가 남은 세션 — 다른 창이 이어받으면 지움 → 그 창이 버려졌다 다시 열려도 '켜진 채 닫힌 세션'을 묻지 않음
        NOW = T(2026, 11, 10, 10, 0, 0); now = int(NOW.timestamp() * 1000)
        ctx, pg = fresh(b, NOW)
        seed = {'st': 'sess', 't0': now - 10 * MIN, 'seg': now - 1000, 'f0': now - 10 * MIN, 'S': SJ, 'D': '', 'at': now - 1000, 'd': D1, 'own': '', 'cls': now - 1000, 'li': now - 1000, 'sum': 10 * MIN, 'rsum': 0}
        pg.evaluate("([N,s])=>{localStorage.setItem(N+'tstate',JSON.stringify(s));__h.sessFlush()}", [N, seed]); pg.clock.run_for(3000)
        ts = ls(pg, 'tstate'); ok(ts and ts['st'] == 'sess' and ts.get('own') and 'cls' not in ts, f"이어받은 뒤 cls 없음 (own {bool(ts and ts.get('own'))} · cls {'cls' in (ts or {})})")
        # 이어받은 창이 화면만 숨겨진 채 버려졌다(pagehide 없음) 5분 뒤 다시 열림
        nw = pg.evaluate("Date.now()"); ts.update({'hid': nw, 'at': nw, 'li': nw, 'own': 'deadwin'})
        pg.evaluate("([N,s])=>{addEventListener('pagehide',()=>localStorage.setItem(N+'tstate',JSON.stringify(s)))}", [N, ts])   # 버려진 탭 = pagehide 없이 사라짐 — 허브의 닫힘 처리(own ''·cls) 뒤에 '숨겨진 채' 상태로 덮어 흉내
        pg.goto('about:blank'); pg.clock.fast_forward(5 * MIN)
        pg.evaluate("0"); pg.goto(HOME); pg.clock.run_for(1500)
        ts2 = ls(pg, 'tstate'); ok(ts2 and ts2['st'] == 'sess' and not band(pg).startswith('closed|'), f'다시 열림 → 세션 이어짐 · 닫힘 질문 없음 ({band(pg)[:20]!r})')
        ok(not pg._errs, f'pageerror 0 ({pg._errs[:2]})'); ctx.close()

        # ---- T4 자동 줄임(tUnrec)은 (기기·날·과목·문서·종류) 한 줄에 누적 · 합치기 = 같은 id면 나중 것 · 옛 줄은 그대로
        ctx, pg = fresh(b, T(2026, 11, 10, 10, 0, 0))
        r = pg.evaluate("""([N,S,now])=>{const S2=S||'기타',old={i:'oldtrim1',at:now-9e5,d:__h.day(),S:S2,D:'',ms:-5000,k:'trim',g:null,x:0};localStorage.setItem(N+'tedit',JSON.stringify([old]));
          __h.tRec(S2,'',now-30*60000,now,'a');for(let i=0;i<5;i++)__h.tUnrec(S2,'',now-(i+1)*60000,now-(i+1)*60000+10000,'a');
          __h.tRec('','',now-3600000,now-3000000,'r');for(let i=0;i<3;i++)__h.tUnrec('','',now-3600000+i*60000,now-3600000+i*60000+20000,'r');
          const L=JSON.parse(localStorage.getItem(N+'tedit'));const a=L.filter(e=>e.k==='trim'&&e.i!=='oldtrim1'&&e.f!=='r'),rr=L.filter(e=>e.f==='r');
          const C=x=>JSON.parse(JSON.stringify(x)),mine=a[0],A=[Object.assign({},mine,{ms:-99000,at:mine.at+5})],B=[Object.assign({},mine,{ms:-1000,at:mine.at-5})];
          return {n:L.length,a:a.map(e=>e.ms),r:rr.map(e=>e.ms),old:L.find(e=>e.i==='oldtrim1'),id:mine.i,m1:__h.teMerge(C(L),A).L.find(e=>e.i===mine.i).ms,m2:__h.teMerge(C(L),B).L.find(e=>e.i===mine.i).ms,m3:__h.teMerge(C(B),C(L)).L.find(e=>e.i===mine.i).ms,dev:__h.devMine().id}}""", [N, SJ, int(T(2026, 11, 10, 10, 0, 0).timestamp() * 1000)])
        ok(r['a'] == [-50000] and r['r'] == [-60000] and r['n'] == 3, f"줄임 5번 → 공부 한 줄 {r['a']} · 휴식 3번 → 한 줄 {r['r']} · tedit 모두 {r['n']}줄(옛 1 + 새 2)")
        ok(r['old'] and r['old']['ms'] == -5000 and not r['old'].get('x'), '옛 줄임 줄은 그대로 읽음')
        ok(r['dev'] in r['id'] and r['m1'] == -99000 and r['m2'] == -50000 and r['m3'] == -50000, f"합치기: 같은 id면 나중 at이 이김 (받은 것이 나중 {r['m1']} · 받은 것이 옛 {r['m2']} · 뒤집어도 {r['m3']}) · id에 기기 {r['id']}")
        ok(not pg._errs, f'pageerror 0 ({pg._errs[:2]})'); ctx.close()

    # ---- T5 4Q 2차 가져오기(qimport2) — 1차 표시가 이미 있는 기기도 한 번 더 · 4Q에 없는 설정만 · 기록 키는 절대 아님
    cur = QS.current(); src = QS.QS[cur].get('importFrom')
    if src:
        N4 = QS.QS[cur]['ident']['ns']; N3 = QS.QS[src]['ident']['ns']; U4 = url(base, rel[cur])
        ctx, pg = mk(b, T(2026, 11, 10, 10, 0, 0)); boot(pg, U4 + '#/')
        pg.evaluate("""([A,B])=>{localStorage.clear();const S=(k,v)=>localStorage.setItem(k,JSON.stringify(v));
          S(B+'tauto',false);S(B+'tgoal',300);S(B+'sessAsk',120);S(B+'jbauto',false);S(B+'jbautoNg',true);S(B+'jbhidePrev',false);S(B+'ascope','lec');S(B+'cond',true);S(B+'autofold',false);S(B+'exfirst',true);S(B+'qzscope','x');
          S(B+'time',{'2026-10-01':{OMS1:3600000}});S(B+'tedit',[{i:'a',d:'2026-10-01',ms:1}]);S(B+'tgoalDay',{'2026-10-01':100});S(B+'tstate',{st:'end'});S(B+'ann.OMS1',{a:1});
          S(A+'qimport',{at:1,n:0,tok:0});S(A+'tgoal',200);}""", [N4, N3])
        boot(pg, U4 + '#/')
        g = lambda k: (lambda v: json.loads(v) if v is not None else None)(pg.evaluate("k=>localStorage.getItem(k)", N4 + k))
        got = {k: g(k) for k in ('tauto', 'sessAsk', 'jbauto', 'jbautoNg', 'jbhidePrev', 'ascope', 'cond', 'autofold', 'exfirst', 'qzscope')}
        ok(got == {'tauto': False, 'sessAsk': 120, 'jbauto': False, 'jbautoNg': True, 'jbhidePrev': False, 'ascope': 'lec', 'cond': True, 'autofold': False, 'exfirst': True, 'qzscope': 'x'}, f'2차 가져오기 — 시계·자동 넘김 설정 {got}')
        ok(g('tgoal') == 200, f"4Q에 이미 있는 값은 그대로 (tgoal {g('tgoal')})")
        ok(all(g(k) is None for k in ('time', 'tedit', 'tgoalDay', 'tstate', 'ann.OMS1')), '기록 키(time·tedit·tgoalDay·tstate·ann)는 가져오지 않음')
        f2 = g('qimport2'); ok(isinstance(f2, dict) and f2.get('n') == 10, f'qimport2 표시 {f2}')
        ok(pg.evaluate("__h.T.auto") is False, '가져온 값이 바로 쓰임(자동 측정 꺼짐)')
        pg.evaluate("([A,B])=>{localStorage.setItem(B+'sessAsk','60');localStorage.removeItem(A+'sessAsk')}", [N4, N3]); boot(pg, U4 + '#/')
        ok(g('sessAsk') is None, '한 번만(표시가 있으면 다시 가져오지 않음)')
        ok(pg.evaluate("([B])=>JSON.parse(localStorage.getItem(B+'time'))['2026-10-01'].OMS1", [N3]) == 3600000, '3Q 기록은 그대로')
        ok(not pg._errs, f'pageerror 0 ({pg._errs[:2]})'); ctx.close()

    # ---- T3 쿼터 공용 시계 채널 — 다른 쿼터 창이 수동 세션 중이면 이쪽 자동 측정은 쉼 · 끝나면 다시 · 수동 ▶는 그대로
    qs = list(rel)
    for q in qs:
        o = [x for x in qs if x != q][0]; SJ = (QS.sids(q) or [''])[0]
        if not SJ: continue
        Uq = url(base, rel[q]); Uo = url(base, rel[o]); Nq = QS.QS[q]['ident']['ns']; No = QS.QS[o]['ident']['ns']
        ctx, pg = mk(b, T(2026, 11, 10, 10, 0, 0)); boot(pg, Uq + '#/')
        pg.evaluate("([A,B])=>{localStorage.clear();localStorage.setItem(A+'tauto','true');localStorage.setItem(B+'tauto','false')}", [Nq, No])
        boot(pg, Uq + f'#/{SJ}/_home'); po = ctx.new_page(); boot(po, Uo + '#/')
        def inp(n=3):
            pg.bring_to_front()
            for i in range(n): pg.mouse.move(400 + i * 9, 400); pg.mouse.wheel(0, 2); pg.mouse.click(600, 12); pg.clock.run_for(2000)
        inp(); s0 = pg.evaluate("__h.trState()")
        if s0 != 'run': print(f'  --   {q}: 과목 화면에서 자동 측정이 안 돎(상태 {s0}) — 건너뜀'); ctx.close(); continue
        po.evaluate("__h.trStart()"); pg.clock.run_for(7000); pg.wait_for_timeout(300)
        s1 = pg.evaluate("__h.trState()"); inp(2); s2 = pg.evaluate("__h.trState()")
        ok(s1 == 'other' and s2 == 'other', f'{o} 창이 ▶ 세션 중 → {q} 자동 측정 쉼(다른 창에서 측정 중) · 입력해도 그대로 ({s0} → {s1} → {s2})')
        pg.evaluate("__h.trStart()"); pg.clock.run_for(1000); ok(pg.evaluate("__h.trState()") == 'sess', f'{q} 수동 ▶는 그대로 시작됨'); pg.evaluate("__h.trStop()"); pg.evaluate("__h.trDo('autoon')"); pg.clock.run_for(500)
        po.evaluate("__h.trStop()"); pg.clock.run_for(16000); pg.wait_for_timeout(300); inp(2); s3 = pg.evaluate("__h.trState()")
        ok(s3 == 'run', f'{o} 세션이 끝나면 {q} 자동 측정 다시 ({s3})')
        ok(not pg._errs and not getattr(po, '_errs', []), f'pageerror 0 ({pg._errs[:2]})'); ctx.close()
    b.close()
done()
