"""ux4c 1회차 회귀 — 4차 개편 뒤 오류 찾기에서 재현된 것(허브·과목 홈·강의 학습).
허브: 공부하다 허브(홈·달력)로 나와 쉬면 ☕ 휴식(알약·띠) · 홈 '이번 주'·과목 표 시간이 머리와 같은 값 · 키보드 포커스 버튼 Enter/Space
     · 알약 폭 고정(쉬는 중 검색칸이 흔들리지 않음) · 좁은 폭 서랍 포커스(inert·Esc → ☰) · 버튼 이름 통일(■ 멈춤 · ▶ 다시 공부)
     · ⏱ 크게(상태 글자 한 번 · 휴식 m:ss · 1분 전 집중 % 없음) · 달력 오늘 공부 앞 0 없음 · 복원 창 자리 · 맥에 '홈 화면에 추가' 없음 · 바닥 '백업' 한 번
과목: 서랍 머리 '임상치과보존학 메뉴'(ux4e 정식 이름) · 틀린 것 0이면 [틀린 것 다시] 꺼짐 · 바로가기 필터는 한 번만(메뉴 'JB 문제'는 전체) · 비교표 수(머리 = 메뉴 = 화면)
     · 2회 이상 펼침 기억(뒤로 와도) · 과목 홈 새로고침 스크롤 · 'JB에서 참고 n 보기 →' · 강의 바로가기 간격 · 창을 바로 닫아도 읽던 자리 · IMPL 메뉴 강의 이름 두 줄
학습: T로 막대를 숨기면 펜 모드 끔 · [카드 ▾] 목록이 화면 안·버튼 아래 · C 뒤 지금 카드 · 틀·카드 1에서 K · / 뒤 Esc · 🧹 창 Esc 뒤 테두리 없음 · ⚡ 창 바깥 닫힘 · 서랍+V
그 밖: 예상 J/K(필터 줄 아래·첫 문항까지)·필터 뒤 강의 머리 · 한눈표 2회↑ 새로고침 칩 수 · 전체정리표 모두 접기 · 가린 칸 가운데 탭 · 검색 머리 작은 링크
맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)"""
import os as _os, sys as _sys, re; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def new(b, w, h, touch=False, clock=False):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch); pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    pg.on('dialog', lambda d: d.accept())
    if clock: import datetime as _dt; pg.clock.install(time=_dt.datetime.now().replace(hour=10, minute=0, second=0, microsecond=0))   # ux4d: 오늘 10시에 고정(자정 가까이 돌리면 오늘·이번 주가 두 날로 갈림)
    pg.goto('about:blank'); pg.goto(U + '#/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')")
    return ctx, pg
def go(pg, h, wait=500):
    pg.goto('about:blank'); pg.goto(U + h)
    pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')", timeout=60000); pg.wait_for_timeout(wait)
def mv(pg, i=0):
    pg.mouse.move(300 + i % 7, 300 + i % 5); pg.mouse.move(310, 320 + i % 3)
CK = "(c=>({st:c.dataset.st,t:c.querySelector('.ckt').textContent,l:c.querySelector('.ckl').textContent}))(document.querySelector('#clock'))"

def hub_rest(b):
    print('== 허브로 나와 쉬기(가짜 시계)')
    for tag, w, h, t, how in [('mac', 1280, 900, False, 'menu'), ('port', 820, 1180, True, 'cal')]:
        ctx, pg = new(b, w, h, t, clock=True)
        go(pg, '#/CONS/WHT/learn', 1500)
        for i in range(10): mv(pg, i); pg.clock.run_for(60000)
        mv(pg); pg.wait_for_timeout(200)
        ok(pg.evaluate(CK)['st'] == 'run', f'{tag} 강의에서 10분 → 공부 중')
        if how == 'menu': pg.evaluate("document.querySelector('#gohome').click()")
        else: pg.evaluate("location.hash='#/_cal'")
        pg.wait_for_timeout(400)
        ok(pg.evaluate(CK)['st'] == 'wait', f'{tag} 허브로 나오면 대기 {pg.evaluate(CK)}')
        for i in range(22): pg.clock.run_for(60000)
        pg.wait_for_timeout(200); c = pg.evaluate(CK)
        ok(c['st'] == 'rest' and c['l'].startswith('휴식 2'), f'{tag} 허브에서 22분 입력 없음 → 알약 휴식 {c}')
        ts = pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.tstate')||'null')")
        ok(ts and ts.get('why') == 'hub' and ts.get('S') == 'CONS' and ts.get('D') == 'WHT', f'{tag} tstate why hub · 떠난 강의로 귀속 {ts and [ts.get("why"), ts.get("S"), ts.get("D")]}')
        mv(pg); pg.clock.run_for(2000); pg.wait_for_timeout(300)
        ok(pg.evaluate(CK)['st'] == 'rest', f'{tag} 허브에서 움직여도 휴식 이어짐(ux4c 2회차)')
        pg.evaluate("__h.openDoc('CONS','WHT','learn')"); pg.wait_for_timeout(300)
        r = pg.evaluate("[!document.querySelector('#idleband').hidden,document.querySelector('#idleband').dataset.k,document.querySelector('#idleband').innerText,+Object.values(JSON.parse(localStorage.getItem('jblhub.v1.trest')||'{}'))[0]||0]")
        ok(r[0] and r[1] == 'rest' and '쉬었어요' in r[2] and r[3] >= 20 * 60000, f'{tag} 과목 문서를 열면 [☕ 쉬었어요][📖 공부했어요] 띠 · trest {r[3] // 60000}분')
        # 허브를 쓰는 동안(입력이 계속)은 휴식이 시작되지 않음
        go(pg, '#/CONS/WHT/learn', 800)
        for i in range(3): mv(pg, i); pg.clock.run_for(60000)
        pg.evaluate("document.querySelector('#gohome').click()"); pg.wait_for_timeout(300)
        for i in range(5): mv(pg, i); pg.clock.run_for(40000)
        ok(pg.evaluate(CK)['st'] == 'wait', f'{tag} 허브를 쓰는 동안(40초마다 입력)은 휴식 아님 {pg.evaluate(CK)}')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

def hub_home(b):
    print('== 허브 홈 숫자·키보드·알약·서랍·버튼 이름')
    ctx, pg = new(b, 1280, 900, clock=True)
    go(pg, '#/', 800)
    pg.click('#clock'); pg.wait_for_timeout(150); pg.click('#tpop [data-tp=start]'); pg.wait_for_timeout(200)
    for i in range(36): mv(pg, i); pg.clock.run_for(55000)
    pg.evaluate("document.querySelector('#home [data-trb=stop]').click()"); pg.wait_for_timeout(200); pg.clock.run_for(31000); pg.wait_for_timeout(200)
    r = pg.evaluate("[document.querySelector('#home [data-hb=td]').textContent,document.querySelector('#home [data-hw=tot]').textContent,(document.querySelector('#home .hwb.today .hwv')||{}).textContent]")
    ok(r[0] == r[1] == r[2] and r[0] != '0:00', f'머리 오늘 = 이번 주 합계 = 오늘 막대 {r}')
    ctx.close()
    for tag, w, h, t in [('mac', 1280, 900, False), ('port', 820, 1180, True)]:
        ctx, pg = new(b, w, h, t)
        go(pg, '#/', 800)
        # 키보드 Enter·Space
        pg.focus('#clock'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.querySelector('#tpop').classList.contains('on')"), f'{tag} #clock 포커스 + Enter → 팝오버')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        if w > 860:
            pg.evaluate("[...document.querySelectorAll('#nav .ni')].find(b=>/공부 달력/.test(b.textContent)).focus()"); pg.keyboard.press('Space'); pg.wait_for_timeout(500)
            ok(pg.evaluate("location.hash").startswith('#/_cal'), f'{tag} 메뉴 공부 달력 포커스 + Space → 달력')
            go(pg, '#/', 500)
        pg.evaluate("document.querySelector('#home .hrbig').focus()"); pg.keyboard.press('Enter'); pg.wait_for_timeout(700)
        ok(pg.evaluate("location.hash").startswith('#/CONS') or pg.evaluate("location.hash").startswith('#/OMS1'), f'{tag} 계속하기 카드 포커스 + Enter → 과목 {pg.evaluate("location.hash")}')
        # 마우스로 누른 뒤 남은 포커스는 Enter로 다시 눌리지 않음
        go(pg, '#/', 500)
        pg.click('#clock'); pg.wait_for_timeout(150); pg.click('#clock'); pg.wait_for_timeout(150)
        pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
        ok(not pg.evaluate("document.querySelector('#tpop').classList.contains('on')"), f'{tag} 포인터로 누른 뒤 Enter는 그 버튼을 다시 누르지 않음')
        # 알약 폭 고정
        def box(): return pg.evaluate("[document.querySelector('#clock').getBoundingClientRect().width,document.querySelector('#gsearch').getBoundingClientRect().left]")
        b0 = box(); pg.click('#clock'); pg.wait_for_timeout(100); pg.click('#tpop [data-tp=start]'); pg.wait_for_timeout(300); b1 = box()
        pg.click('#clock'); pg.wait_for_timeout(100); pg.click('#tpop [data-tp=rest]'); pg.wait_for_timeout(300)
        L = []
        for i in range(8): L.append(box()); pg.wait_for_timeout(1000)
        ws = [x[0] for x in L] + [b0[0], b1[0]]; ls = [x[1] for x in L] + [b0[1], b1[1]]
        ok(max(ws) - min(ws) <= 1 and max(ls) - min(ls) <= 1, f'{tag} 알약 폭·검색칸 자리 고정(대기·세션·휴식 8초) 폭 {min(ws):.1f}~{max(ws):.1f} · 검색 {min(ls):.1f}~{max(ls):.1f}')
        # 버튼 이름 통일 · ⏱ 크게
        pg.click('#clock'); pg.wait_for_timeout(100); pg.click('#tpop [data-tp=big]'); pg.wait_for_timeout(1200)
        r = pg.evaluate("[document.querySelector('#bigclock').innerText,document.querySelector('#bct').textContent]")
        ok(r[0].count('쉬는 중') == 1 and re.match(r'^\d+:\d\d$', r[1]) and '집중' not in r[0] and '%' not in r[0] and '다시 공부' in r[0] and '멈춤' in r[0] and '종료' not in r[0],
           f'{tag} ⏱ 크게(휴식): 제목 한 번 · {r[1]} m:ss · % 없음 · [▶ 다시 공부][■ 멈춤] ({r[0][:90]!r})')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        go(pg, '#/_cal', 700)
        r = pg.evaluate("[document.querySelector('#cc-td').textContent,document.querySelector('.ccard.cst').innerText]")
        ok(not r[0].startswith('00') and re.match(r'^\d:\d\d:\d\d$', r[0]) and '종료' not in r[1] and '멈춤' in r[1], f'{tag} 달력 오늘 공부 {r[0]} · 측정 카드 {r[1][:40]!r}')
        pg.evaluate("__h.trStop&&__h.trStop()"); pg.wait_for_timeout(200)
        go(pg, '#/', 500)
        # 바닥 문구 · 과목 표 머리
        r = pg.evaluate("[document.querySelector('#home .hbk summary').textContent,document.querySelector('#home .hsjh span').textContent]")
        ok(r[0].count('백업') == 1 and '기기 옮기기' in r[0] and r[1] == '', f'{tag} 바닥 한 줄 {r[0]!r} · 표 첫 머리 빈칸')
        if w <= 860:
            pg.click('#navbtn'); pg.wait_for_timeout(350)
            r = pg.evaluate("[!!document.activeElement.closest('#nav'),document.querySelector('#main').inert,document.querySelector('#top').inert]")
            ok(r == [True, True, True], f'{tag} 서랍 열면 포커스가 서랍 안 · 뒤 화면 inert {r}')
            seq = []
            for i in range(20): pg.keyboard.press('Tab'); seq.append(pg.evaluate("(a=>a.closest('#side')?'S':a===document.body?'B':'X')(document.activeElement)"))
            ok('X' not in seq, f'{tag} Tab 20번이 서랍 밖(뒤 화면)으로 새지 않음 {"".join(seq)} (B = 브라우저 주소창으로 한 바퀴)')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
            r = pg.evaluate("[document.activeElement.id,document.querySelector('#main').inert,document.body.classList.contains('navopen')]")
            ok(r == ['navbtn', False, False], f'{tag} Esc → 닫힘 · 포커스 ☰ · inert 풀림 {r}')
            go(pg, '#/CONS/_home/_home', 500); pg.click('#navbtn'); pg.wait_for_timeout(300)
            hd = pg.evaluate("document.querySelector('#nav .nvbrand').textContent.trim()")
            ok(hd == '임상치과보존학 메뉴', f'{tag} 과목 안 서랍 머리 {hd!r}')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        else:
            # 복원 창 자리 · 맥 '홈 화면에 추가' 없음
            pg.click('#bkup'); pg.wait_for_timeout(300); a = pg.evaluate("(r=>[r.left,r.bottom])(document.querySelector('#bkpop').getBoundingClientRect())")
            pg.click('#rstr'); pg.wait_for_timeout(600); r = pg.evaluate("(r=>[r.left,r.bottom])(document.querySelector('#rpop').getBoundingClientRect())")
            ok(abs(r[0] - a[0]) < 20 and abs(r[1] - a[1]) < 20, f'{tag} 복원 창이 백업 창 자리에 {a} → {r}')
            t2 = pg.evaluate("(document.querySelector('#rstp')||{}).textContent||''")
            ok('홈 화면' not in t2, f'{tag} 맥 복원 창에 홈 화면 추가 안내 없음 {t2!r}')
            pg.keyboard.press('Escape')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

def subject(b):
    print('== 과목 홈')
    for tag, w, h, t in [('mac', 1280, 900, False), ('port', 820, 1180, True)]:
        ctx, pg = new(b, w, h, t)
        go(pg, '#/CONS/_home/_home', 700)
        r = pg.evaluate("[document.querySelector('#hprog [data-jbf=ng]').disabled,document.querySelector('#hprog [data-jbf=todo]').disabled,document.querySelector('#hprog [data-reftog]')&&document.querySelector('#hprog [data-reftog]').textContent]")
        ok(r[0] is True and r[1] is False, f'{tag} 틀린 것 0 → [틀린 것 다시] 꺼짐 · [안 푼 것 풀기] 켜짐 {r[:2]}')
        # 바로가기 필터는 한 번만
        pg.click('#hprog [data-jbf=todo]'); pg.wait_for_timeout(600)
        ok(pg.evaluate("__h.JB.F.mine") == 'todo', f'{tag} 안 푼 것 풀기 → JB 안 푼 것')
        pg.evaluate("document.querySelector('#crumb .cbs').click()"); pg.wait_for_timeout(500)
        if w <= 860: pg.click('#navbtn'); pg.wait_for_timeout(300)
        pg.evaluate("document.querySelector('#nav .nvd[data-d=_jb]').click()"); pg.wait_for_timeout(700)
        r = pg.evaluate("[__h.JB.F.mine,__h.JB.F.n,__h.JB.vis.length,+(document.querySelector('#nav .nvd[data-d=_jb] .r')||{textContent:0}).textContent]")
        ok(r[0] == '' and r[1] == 0 and r[2] == r[3] and r[2] > 0, f'{tag} 메뉴 JB 문제 → 필터 풀림 · 목록 {r[2]} = 메뉴 {r[3]}')
        go(pg, '#/CONS/_home/_home', 500)
        rep = pg.query_selector('#hguide [data-jbn]') or pg.query_selector('#htop [data-jbn]')
        rep.click(); pg.wait_for_timeout(700)
        n2 = pg.evaluate("__h.JB.vis.length")
        go(pg, '#/CONS/_home/_home', 500)
        pg.evaluate("document.querySelector('#hero [data-hgo=_jb]').click()"); pg.wait_for_timeout(700)
        r = pg.evaluate("[__h.JB.F.n,__h.JB.one,__h.JB.vis.length]")
        ok(r[0] == 0 and r[1] is False and r[2] > n2, f'{tag} 2회 이상({n2}) 뒤 머리 기출 링크 → 전체 {r}')
        # 비교표 수
        go(pg, '#/CONS/_home/_home', 500)
        a = pg.evaluate("+document.querySelector('#hero [data-hgo=_tbl]').textContent.replace(/\\D/g,'')")
        bnav = pg.evaluate("+(document.querySelector('#nav .nvd[data-d=_tbl] .r')||{textContent:0}).textContent")
        go(pg, '#/CONS/_tbl/_tbl', 800); c = pg.evaluate("document.querySelectorAll('#stage table.cmp').length")
        ok(a == bnav == c, f'{tag} 비교표 머리 {a} = 메뉴 {bnav} = 화면 {c}')
        # 2회 이상 펼침 → 문항 → 뒤로
        go(pg, '#/CONS/_home/_home', 600)
        if pg.query_selector('#htop [data-topmore]'):
            pg.click('#htop [data-topmore]'); pg.wait_for_timeout(200)
            pg.evaluate("document.querySelector('#htop li.tmr').scrollIntoView({block:'center'})"); pg.wait_for_timeout(1200)
            y0 = pg.evaluate("scrollY"); pg.evaluate("document.querySelector('#htop li.tmr .q').click()"); pg.wait_for_timeout(900)
            pg.go_back(); pg.wait_for_timeout(1800)
            r = pg.evaluate("[document.querySelector('#htop').classList.contains('all'),scrollY]")
            ok(r[0] and abs(r[1] - y0) < 40, f'{tag} 펼친 2회 이상 → 문항 → 뒤로: 펼친 그대로 · y {y0} → {r[1]}')
        # 새로고침 스크롤
        go(pg, '#/CONS/_home/_home', 600); pg.evaluate("scrollTo(0,900)"); pg.wait_for_timeout(1300)
        pg.reload(); pg.wait_for_function("window.__h&&__h.plStat().pend===0", timeout=60000); pg.wait_for_timeout(1800)
        y = pg.evaluate("scrollY"); ok(abs(y - 900) < 40, f'{tag} 과목 홈 새로고침 → 같은 위치 {y}')
        if w <= 860:
            r = pg.evaluate("(()=>{const o=document.querySelector('#hguide ol').getBoundingClientRect(),l=document.querySelector('#stage .ljump').getBoundingClientRect();return l.top-o.bottom})()")
            ok(r >= 8, f'{tag} 강의 바로가기가 공부 순서와 떨어짐 {r:.0f}px')
        # 창을 바로 닫아도 읽던 자리
        go(pg, '#/CONS/DHS/learn', 1500); pg.evaluate("scrollTo(0,3000)"); pg.wait_for_timeout(250)
        pg.goto('about:blank'); pg.goto(U + '#/'); pg.wait_for_timeout(500)
        aid = pg.evaluate("(JSON.parse(localStorage.getItem('jblhub.v1.lastBy')||'{}').CONS||{}).aid||''")
        ok(aid and not aid.endswith(':frame'), f'{tag} 스크롤 0.25초 뒤 바로 떠나도 읽던 자리 저장 {aid}')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()
    ctx, pg = new(b, 1280, 900)
    go(pg, '#/OMS1/_home/_home', 500)
    t = pg.evaluate("document.querySelector('#hprog [data-reftog]').textContent")
    ok(t.startswith('JB에서 참고') and t.endswith('→'), f'참고 링크 글자 {t!r}')
    for w in (1280, 1180):
        pg.set_viewport_size({'width': w, 'height': 820}); go(pg, '#/IMPL/_home/_home', 500)
        cut = pg.evaluate("[...document.querySelectorAll('#nav .nvl .el')].filter(e=>e.scrollHeight>e.clientHeight+1||e.scrollWidth>e.clientWidth+1).map(e=>e.textContent)")
        ok(not cut, f'{w} IMPL 메뉴 강의 이름 잘림 없음 {cut}')
    ctx.close()

def learn(b):
    print('== 강의 학습')
    for tag, w, h, t in [('mac', 1280, 900, False), ('land', 1180, 820, True), ('port', 820, 1180, True)]:
        ctx, pg = new(b, w, h, t)
        go(pg, '#/CONS/WHT/learn', 1200)
        pg.keyboard.press('h'); pg.wait_for_timeout(100); pg.keyboard.press('t'); pg.wait_for_timeout(200)
        r = pg.evaluate("[__h.Kit.mode(),document.body.classList.contains('mode-h'),document.body.classList.contains('kit-off')]")
        ok(r == [None, False, True], f'{tag} H → T(막대 숨김) → 형광펜 모드 꺼짐 {r}')
        n0 = pg.evaluate("document.querySelectorAll('#stage [data-rk]').length")
        li = pg.evaluate("(()=>{const e=document.querySelectorAll('#stage .tc li')[3];e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return [r.left+20,r.top+8]})()")
        pg.wait_for_timeout(200); (pg.touchscreen.tap if t else pg.mouse.click)(li[0], li[1]); pg.wait_for_timeout(300)
        ok(pg.evaluate("document.querySelectorAll('#stage [data-rk]').length") == n0, f'{tag} 막대를 숨긴 채 누르면 표시가 생기지 않음')
        pg.keyboard.press('t'); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.querySelector('#k-h').getAttribute('aria-pressed')") == 'false', f'{tag} 다시 T → 형광펜 버튼 눌리지 않음')
        # [카드 ▾] 목록이 화면 안
        pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(400); pg.click('#lmcur'); pg.wait_for_timeout(300)
        pg.evaluate("(()=>{const p=document.querySelector('#lpop');p.scrollTop=p.scrollHeight})()"); pg.wait_for_timeout(150)
        r = pg.evaluate("(()=>{const L=[...document.querySelectorAll('#lpop .lpi')].pop().getBoundingClientRect(),p=document.querySelector('#lpop').getBoundingClientRect();return [Math.round(L.bottom),Math.round(p.bottom),innerHeight]})()")
        ok(r[0] <= r[2] and r[1] <= r[2], f'{tag} [카드 ▾] 끝까지 굴리면 마지막 카드가 화면 안 {r}')
        pg.click('#lmcur'); pg.wait_for_timeout(200)
        # C 뒤 지금 카드
        go(pg, '#/CONS/WHT/learn', 1200)
        for i in range(6): pg.keyboard.press('j'); pg.wait_for_timeout(350)
        pg.wait_for_timeout(900); c0 = pg.evaluate("__h.LCUR")
        pg.keyboard.press('c'); pg.wait_for_timeout(2200)
        r = pg.evaluate("[__h.LCUR,(()=>{const line=innerHeight*.3;let j=-1;for(const c of document.querySelectorAll('#stage .tc')){if(c.offsetParent===null)continue;if(c.getBoundingClientRect().top<=line)j=+c.id.split('-').pop();else break}return j})(),document.querySelector('#lmcur').textContent]")
        ok(r[0] == r[1] == c0, f'{tag} J×6 → C: 지금 카드 {c0} 그대로 · 표시 {r}')
        pg.keyboard.press('j'); pg.wait_for_timeout(900)
        ok(pg.evaluate("__h.LCUR") == c0 + 1, f'{tag} C 뒤 J → 다음 카드 {pg.evaluate("__h.LCUR")}')
        pg.keyboard.press('c'); pg.wait_for_timeout(1500)
        # / 뒤 Esc
        pg.keyboard.press('Slash'); pg.wait_for_timeout(150); pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        r = pg.evaluate("[document.activeElement.id,document.querySelector('#gsearch').value]")
        l0 = pg.evaluate("__h.LCUR"); pg.keyboard.press('j'); pg.wait_for_timeout(800)
        ok(r[0] != 'gsearch' and pg.evaluate("document.querySelector('#gsearch').value") == '' and pg.evaluate("__h.LCUR") != l0, f'{tag} / → Esc → 검색칸에서 나옴 · J = 다음 카드 {r}')
        pg.keyboard.press('v'); pg.wait_for_timeout(500); pg.keyboard.press('Slash'); pg.wait_for_timeout(150); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        ok(not pg.evaluate("document.body.classList.contains('topshow')"), f'{tag} 집중 모드 / → Esc → 상단 막대 다시 숨음')
        pg.keyboard.press('v'); pg.wait_for_timeout(500)
        # 🧹 이 카드 → Esc
        pg.evaluate("document.querySelectorAll('#stage .tc')[3].scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
        pg.click('#k-clear'); pg.wait_for_timeout(150); pg.click('#clearpop [data-csc=card]'); pg.wait_for_timeout(150)
        a = pg.evaluate("document.querySelectorAll('#stage .clrtgt').length"); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        ok(a == 1 and pg.evaluate("document.querySelectorAll('#stage .clrtgt').length") == 0, f'{tag} 🧹 이 카드 테두리 → Esc → 없음')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

def extra(b):
    print('== 그 밖(K·창 자리·서랍+V·예상·한눈표·전체정리표·가린 칸·⚡ 창·검색 머리)')
    for tag, w, h, t in [('mac', 1280, 900, False), ('port', 820, 1180, True)]:
        ctx, pg = new(b, w, h, t)
        go(pg, '#/CONS/WHT/learn', 1500); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(500)
        pg.keyboard.press('k'); pg.wait_for_timeout(900)
        ok(pg.evaluate("scrollY") < 5 and pg.evaluate("__h.LCUR") == -1, f'{tag} 맨 위(틀)에서 K → 그대로 {pg.evaluate("scrollY")}')
        pg.keyboard.press('j'); pg.wait_for_timeout(900); pg.keyboard.press('k'); pg.wait_for_timeout(1200)
        ok(pg.evaluate("__h.LCUR") == -1, f'{tag} 카드 1에서 K → 틀')
        pg.keyboard.press('v'); pg.wait_for_timeout(500); pg.click('#lmcur'); pg.wait_for_timeout(300)
        r = pg.evaluate("[document.querySelector('#lmcur').getBoundingClientRect().left,document.querySelector('#lpop').getBoundingClientRect().left,document.querySelector('#lpop').getBoundingClientRect().right,innerWidth]")
        ok(r[2] <= r[3] and (abs(r[1] - r[0]) < 2 or r[2] >= r[3] - 9), f'{tag} 집중 모드 [카드 ▾] 창이 버튼 아래 {r}')
        pg.click('#lmcur'); pg.keyboard.press('v'); pg.wait_for_timeout(500)
        if w <= 860:
            pg.keyboard.press('m'); pg.wait_for_timeout(300); pg.keyboard.press('v'); pg.wait_for_timeout(500)
            r = pg.evaluate("[document.body.classList.contains('navopen'),document.body.classList.contains('focus')]")
            ok(r == [False, True], f'{tag} 서랍이 열린 채 V → 서랍 닫고 집중 {r}')
            pg.keyboard.press('v'); pg.wait_for_timeout(400)
        # 예상문제 J/K — 필터 줄 아래 · K로 첫 문항까지
        go(pg, '#/CONS/WHT/pred', 1200)
        for k in 'jjj': pg.keyboard.press(k); pg.wait_for_timeout(700)
        r = pg.evaluate("[document.querySelector('#stage .pc.rcur').getBoundingClientRect().top,document.querySelector('#ppills').getBoundingClientRect().bottom]")
        ok(r[0] >= r[1] - 1, f'{tag} 예상 J → 카드 머리가 필터 줄 아래 {r}')
        for k in 'kk': pg.keyboard.press(k); pg.wait_for_timeout(700)
        idx = pg.evaluate("[...document.querySelectorAll('#stage .pc')].filter(e=>e.offsetParent).indexOf(document.querySelector('#stage .pc.rcur'))")
        ok(idx == 0, f'{tag} 예상 J×3 → K×2 → 첫 문항 {idx}')
        go(pg, '#/CONS/_pred/_pred', 1200)
        pg.click('#ppills [data-pf=ng]'); pg.wait_for_timeout(400)
        r = pg.evaluate("[...document.querySelectorAll('#stage h3.pgh')].filter(h=>!h.hidden).length")
        ok(r == 0, f'{tag} 예상 틀린 것(0) → 강의 머리 숨김 {r}')
        pg.click('#ppills [data-ptype=n]'); pg.click('#ppills [data-pf=ng]'); pg.wait_for_timeout(400)
        r = pg.evaluate("document.querySelector('#stage h3.pgh .pgn').textContent")
        ok('/' in r, f'{tag} 예상 미출제 → 머리 수 보이는 것 / 전체 {r!r}')
        # 한눈표 2회↑ 뒤 새로고침 칩 수
        go(pg, '#/CONS/_sum/_sum', 900); pg.click('#stage [data-filt=rep]'); pg.wait_for_timeout(500)
        a = pg.evaluate("[...document.querySelectorAll('#sumbar [data-sgo] b')].map(b=>b.textContent).join(',')")
        pg.reload(); pg.wait_for_function("window.__h&&__h.plStat().pend===0", timeout=60000); pg.wait_for_timeout(1500)
        bb = pg.evaluate("[...document.querySelectorAll('#sumbar [data-sgo] b')].map(b=>b.textContent).join(',')")
        ok(a == bb, f'{tag} 한눈표 2회↑ → 새로고침 칩 수 그대로 {a} / {bb}')
        pg.click('#stage [data-filt=rep]'); pg.wait_for_timeout(300)
        # 전체정리표 모두 펼치기 ↔ 접기
        go(pg, '#/CONS/WHT/sum', 1200)
        if pg.query_selector('#sumtop [data-sttab=all]'):
            pg.evaluate("document.querySelector('#sumtop [data-sttab=all]').click()"); pg.wait_for_timeout(300)
            ok(pg.evaluate("document.querySelector('#sumtop [data-sttab=all]').textContent") == '모두 접기', f'{tag} 전체정리표 모두 펼치기 → 모두 접기')
            pg.evaluate("document.querySelector('#sumtop [data-sttab=all]').click()"); pg.wait_for_timeout(300)
        # ⚡ 창 바깥 누르면 닫힘
        go(pg, '#/CONS/WHT/learn', 1200)
        pg.click('#k-auto'); pg.wait_for_timeout(300)
        a = pg.evaluate("document.querySelector('#autopop').classList.contains('on')")
        pg.mouse.click(w // 2, 200); pg.wait_for_timeout(300)
        ok(a and not pg.evaluate("document.querySelector('#autopop').classList.contains('on')"), f'{tag} ⚡ 창 바깥을 누르면 닫힘')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()
    # 가린 칸 가운데 탭 → 그 칸만(820 정리표 카드형)
    ctx, pg = new(b, 820, 1180, True)
    go(pg, '#/CONS/WHT/sum', 1500)
    lc = pg.evaluate("(()=>{const c=[...document.querySelectorAll('#stage .msum table.mtx td[data-col]')].find(x=>x.offsetParent);if(!c)return null;c.scrollIntoView({block:'center'});const r=c.getBoundingClientRect();return [r.x+10,r.y+8]})()")
    if lc:
        pg.wait_for_timeout(300); pg.touchscreen.tap(lc[0], lc[1]); pg.wait_for_timeout(400)
        n0 = pg.evaluate("document.querySelectorAll('#stage td.cov').length")
        c = pg.evaluate("(()=>{const c=[...document.querySelectorAll('#stage td.cov')].filter(x=>x.offsetParent)[2];c.scrollIntoView({block:'center'});const r=c.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()")
        pg.wait_for_timeout(300); pg.touchscreen.tap(c[0], c[1]); pg.wait_for_timeout(400)
        r = pg.evaluate("[document.querySelectorAll('#stage td.cov').length,document.querySelectorAll('#stage td.covo').length]")
        ok(n0 > 0 and r[0] == n0 and r[1] == 1, f'가린 칸 가운데 탭 → 그 칸만 열림(열 전체 풀리지 않음) {n0} → {r}')
        pg.evaluate("document.querySelector('#stage [data-covall]')&&document.querySelector('#stage [data-covall]').click()")
    ctx.close()
    ctx, pg = new(b, 820, 1180, True)
    go(pg, '#/CONS/_jb/_jb', 800); pg.keyboard.press('Slash'); pg.keyboard.type('bleaching'); pg.wait_for_timeout(1500)
    r = pg.evaluate("(e=>e?parseFloat(getComputedStyle(e).fontSize):0)(document.querySelector('.shead .swide'))")
    ok(0 < r < 16, f'검색 머리 전체로 넓히기 = 작은 링크 {r}px')
    ctx.close()

with sync_playwright() as p:
    b = p.chromium.launch()
    for f in (hub_rest, hub_home, subject, learn, extra):
        try: f(b)
        except Exception as e: ok(False, f'{f.__name__} 예외 {str(e)[:300]}')
    b.close()
print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
