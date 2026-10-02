"""ux4f 범위 A 회귀 — 허브 홈·시계·달력·과목 홈·과목 메뉴 오류 22건(bugs_A n1~22) 재검.
1 허브로 나와 쉬면 ☕ 휴식(알약·띠·tstate why hub) · 2 이번 주·오늘 막대·과목 표 시간 = 머리 · 3 키보드 포커스 Enter/Space
4 알약 폭 고정 · 5 좁은 폭 서랍 포커스·inert·Esc → ☰ · 6 버튼 이름 통일(■ 멈춤 · ▶ 다시 공부 · ☕ 쉬기) · 7 ⏱ 크게 상태 한 번·m:ss
8 시간 표기(내림 h:mm · 앞 0 없음) · 9 복원 창이 백업 창 자리(맥·아이패드 가로) · 10 맥에 '홈 화면에 추가' 없음 · 11 허브 화면에 % 글자 없음
12·21 과목 안 서랍 머리 = 과목 메뉴 · 13 바닥 '백업' 한 번·표 첫 머리 빈칸 · 14 바로가기 필터는 한 번만(틀린 것 0이면 꺼짐·한 장씩 뒤 메뉴 JB 목록)
15 비교표 수 머리 = 메뉴 = 화면 · 16 2회 이상 펼침 뒤로 기억 · 17 과목 홈 새로고침 스크롤 · 18 'JB에서 참고 n 보기 →' 이동 링크 글자
19 강의 바로가기 간격 · 20 바로 떠나도 읽던 자리 · 22 IMPL 메뉴 강의 이름 잘림 없음
맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)"""
import os as _os, sys as _sys, re; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
VP = [('mac', 1280, 900, False), ('port', 820, 1180, True), ('land', 1180, 820, True)]
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def new(b, w, h, touch=False, clock=False):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch); pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    pg.on('dialog', lambda d: d.accept())
    if clock: pg.clock.install()
    pg.goto('about:blank'); pg.goto(U + '#/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')")
    return ctx, pg
def go(pg, h, wait=500):
    pg.goto('about:blank'); pg.goto(U + h)
    pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')", timeout=60000); pg.wait_for_timeout(wait)
def mv(pg, i=0):
    pg.mouse.move(300 + i % 7, 300 + i % 5); pg.mouse.move(310, 320 + i % 3)
def tap(pg, sel, touch):
    if touch: pg.tap(sel)
    else: pg.click(sel)
CK = "(c=>({st:c.dataset.st,t:c.querySelector('.ckt').textContent,l:c.querySelector('.ckl').textContent}))(document.querySelector('#clock'))"
PCT = "(s=>[...document.querySelectorAll(s)].filter(e=>e.offsetParent!==null||e===document.body).map(e=>e.innerText).join(' '))"

def hub_rest(b):
    print('== 1·2·8 허브로 나와 쉬기 · 과목 표 시간 · 표기(가짜 시계)')
    for tag, w, h, t in VP:
        ctx, pg = new(b, w, h, t, clock=True)
        go(pg, '#/CONS/WHT/learn', 1500)
        for i in range(21): mv(pg, i); pg.clock.run_for(30000)
        mv(pg); pg.wait_for_timeout(200)
        c = pg.evaluate(CK); ok(c['st'] == 'run', f'{tag} 강의에서 10분 30초 → 공부 중 {c}')
        pg.evaluate("document.querySelector('#gohome').click()"); pg.wait_for_timeout(400)
        c = pg.evaluate(CK); ok(c['st'] == 'wait', f'{tag} 허브로 나오면 대기 {c}')
        # 2·8 머리 오늘 = 이번 주 합계 = 오늘 막대 = 과목 표 CONS 오늘 · 분 단위 내림(10:30 → 0:10) · 알약 앞 0 없음
        r = pg.evaluate("[document.querySelector('#home [data-hb=td]').textContent,document.querySelector('#home [data-hw=tot]').textContent,(document.querySelector('#home .hwb.today .hwv')||{}).textContent,(document.querySelector('#home .hsj[data-s=CONS] .hct')||{}).textContent,(document.querySelector('#home .hsj[data-s=CONS] .hctt')||{}).textContent]")
        ok(r[0] == r[1] == r[2] == r[3] == r[4] == '0:10', f'{tag} 머리 = 이번 주 = 오늘 막대 = 과목 표 오늘·전체 = 0:10(내림) {r}')
        ok(re.match(r'^0:10:\d\d$', c['t']) is not None, f'{tag} 알약 h:mm:ss 앞 0 없음 {c["t"]}')
        for i in range(22): pg.clock.run_for(60000)
        pg.wait_for_timeout(200); c = pg.evaluate(CK)
        ok(c['st'] == 'rest' and c['l'].startswith('휴식 2'), f'{tag} 허브에서 22분 입력 없음 → 알약 휴식 {c}')
        ts = pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.tstate')||'null')")
        ok(ts and ts.get('why') == 'hub', f'{tag} tstate why hub {ts and ts.get("why")}')
        go(pg, '#/CONS/WHT/learn', 800); mv(pg); pg.clock.run_for(2000); pg.wait_for_timeout(300)
        r = pg.evaluate("[!document.querySelector('#idleband').hidden,document.querySelector('#idleband').innerText,+Object.values(JSON.parse(localStorage.getItem('jblhub.v1.trest')||'{}'))[0]||0]")
        ok(r[0] and '쉬었어요' in r[1] and '공부했어요' in r[1] and r[2] >= 20 * 60000, f'{tag} 돌아오면 [☕ 쉬었어요][📖 공부했어요] 띠 · trest {r[2] // 60000}분')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

def hub_home(b):
    print('== 3~13 허브 홈·시계·달력·서랍·백업')
    for tag, w, h, t in VP:
        ctx, pg = new(b, w, h, t)
        go(pg, '#/', 800)
        # 3 키보드
        pg.focus('#clock'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.querySelector('#tpop').classList.contains('on')"), f'{tag} #clock 포커스 + Enter → 팝오버')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        pg.focus('#clock'); pg.keyboard.press('Space'); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.querySelector('#tpop').classList.contains('on')"), f'{tag} #clock 포커스 + Space → 팝오버')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        pg.evaluate("document.querySelector('#home .hrbig').focus()"); pg.keyboard.press('Enter'); pg.wait_for_timeout(700)
        ok(re.match(r'^#/[A-Z]', pg.evaluate("location.hash")) is not None, f'{tag} 계속하기 카드 포커스 + Enter → 과목 {pg.evaluate("location.hash")}')
        go(pg, '#/', 500)
        # 4·6 알약 폭 고정 · 팝오버 버튼 이름
        def box(): return pg.evaluate("[document.querySelector('#clock').getBoundingClientRect().width,document.querySelector('#gsearch').getBoundingClientRect().left]")
        b0 = box(); tap(pg, '#clock', t); pg.wait_for_timeout(150)
        p0 = pg.evaluate("document.querySelector('#tpop').innerText")
        tap(pg, '#tpop [data-tp=start]', t); pg.wait_for_timeout(300); b1 = box()
        tap(pg, '#clock', t); pg.wait_for_timeout(150); p1 = pg.evaluate("document.querySelector('#tpop').innerText")
        tap(pg, '#tpop [data-tp=rest]', t); pg.wait_for_timeout(300)
        tap(pg, '#clock', t); pg.wait_for_timeout(150); p2 = pg.evaluate("document.querySelector('#tpop').innerText"); pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        L = []
        for i in range(6): L.append(box()); pg.wait_for_timeout(1000)
        ws = [x[0] for x in L] + [b0[0], b1[0]]; ls = [x[1] for x in L] + [b0[1], b1[1]]
        ok(max(ws) - min(ws) <= 1 and max(ls) - min(ls) <= 1, f'{tag} 알약 폭·검색칸 자리 고정 폭 {min(ws):.1f}~{max(ws):.1f} · 검색 {min(ls):.1f}~{max(ls):.1f}')
        bad = [x for x in ('종료', '세션 끝내기', '공부 멈춤', '쉬기 시작', '▶ 다시\n') if x in p0 + p1 + p2]
        ok(not bad and '■ 멈춤' in p1 and '☕ 쉬기' in p1 and '▶ 다시 공부' in p2 and '■ 멈춤' in p2, f'{tag} 팝오버 이름 ■ 멈춤 · ☕ 쉬기 · ▶ 다시 공부 (다른 이름 {bad})')
        band = pg.evaluate("document.querySelector('#home .hband').innerText")
        ok('▶ 다시 공부' in band and '■ 멈춤' in band and '종료' not in band, f'{tag} 홈 띠 이름 {band[-40:]!r}')
        # 7·11 ⏱ 크게
        tap(pg, '#clock', t); pg.wait_for_timeout(150); tap(pg, '#tpop [data-tp=big]', t); pg.wait_for_timeout(1200)
        r = pg.evaluate("[document.querySelector('#bigclock').innerText,document.querySelector('#bct').textContent]")
        ok(r[0].count('쉬는 중') == 1 and re.match(r'^\d+:\d\d$', r[1]) and '%' not in r[0] and '다시 공부' in r[0] and '멈춤' in r[0] and '종료' not in r[0],
           f'{tag} ⏱ 크게(휴식): 제목 한 번 · {r[1]} m:ss · % 없음 ({r[0][:80]!r})')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        # 6·8·11 달력
        go(pg, '#/_cal', 700)
        r = pg.evaluate("[document.querySelector('#cc-td').textContent,document.querySelector('.ccard.cst').innerText,document.querySelector('#stage').innerText,document.querySelector('#cc-ring').textContent]")
        ok(re.match(r'^\d+:\d\d:\d\d$', r[0]) and not r[0].startswith('00'), f'{tag} 달력 오늘 공부 앞 0 없음 {r[0]}')
        ok('종료' not in r[1] and '멈춤' in r[1] and '다시 공부' in r[1], f'{tag} 달력 측정 카드 이름 {r[1][:40]!r}')
        ok('%' not in r[2] and '/' in r[3], f'{tag} 달력에 % 없음 · 달성 = 시간 / 목표 {r[3]!r}')
        pg.evaluate("document.querySelector('[data-caltab=stats]').click()"); pg.wait_for_timeout(600)
        ok('%' not in pg.evaluate("document.querySelector('#stage').innerText"), f'{tag} 통계 탭에 % 없음')
        pg.evaluate("__h.trStop&&__h.trStop()"); pg.wait_for_timeout(200)
        go(pg, '#/', 500)
        tap(pg, '#clock', t); pg.wait_for_timeout(150)
        ok('%' not in pg.evaluate("document.querySelector('#tpop').innerText") + pg.evaluate("document.querySelector('#home').innerText"), f'{tag} 허브 홈·시계 팝오버에 % 없음')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        # 13 바닥 문구 · 과목 표 머리
        r = pg.evaluate("[document.querySelector('#home .hbk summary').textContent,document.querySelector('#home .hsjh span').textContent]")
        ok(r[0].count('백업') == 1 and '기기 옮기기' in r[0] and r[1] == '', f'{tag} 바닥 한 줄 {r[0]!r} · 표 첫 머리 빈칸')
        if w <= 860:
            # 5 서랍
            tap(pg, '#navbtn', t); pg.wait_for_timeout(350)
            r = pg.evaluate("[!!document.activeElement.closest('#nav'),document.querySelector('#main').inert,document.querySelector('#top').inert]")
            ok(r == [True, True, True], f'{tag} 서랍 열면 포커스가 서랍 안 · 뒤 화면 inert {r}')
            seq = []
            for i in range(20): pg.keyboard.press('Tab'); seq.append(pg.evaluate("(a=>a.closest('#side')?'S':a===document.body?'B':'X')(document.activeElement)"))
            ok('X' not in seq, f'{tag} Tab 20번이 서랍 밖으로 새지 않음 {"".join(seq)}')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
            r = pg.evaluate("[document.activeElement.id,document.querySelector('#main').inert,document.body.classList.contains('navopen')]")
            ok(r == ['navbtn', False, False], f'{tag} Esc → 닫힘 · 포커스 ☰ · inert 풀림 {r}')
            # 12·21 과목 안 서랍 머리(과목 홈·강의)
            for hh in ('#/CONS/_home/_home', '#/CONS/WHT/learn'):
                go(pg, hh, 600); tap(pg, '#navbtn', t); pg.wait_for_timeout(300)
                hd = pg.evaluate("document.querySelector('#nav .nvbrand').textContent.trim()")
                ok('허브' not in hd and '임상치과보존학' in hd, f'{tag} {hh} 서랍 머리 {hd!r}')
                pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        else:
            # 9·10 복원 창 자리 · 맥에 '홈 화면에 추가' 없음
            tap(pg, '#bkup', t); pg.wait_for_timeout(300); a = pg.evaluate("(r=>[r.left,r.bottom])(document.querySelector('#bkpop').getBoundingClientRect())")
            tap(pg, '#rstr', t); pg.wait_for_timeout(600); r = pg.evaluate("(r=>[r.left,r.bottom,r.right<=innerWidth,r.top>=0])(document.querySelector('#rpop').getBoundingClientRect())")
            ok(abs(r[0] - a[0]) < 20 and abs(r[1] - a[1]) < 20 and r[2] and r[3], f'{tag} 복원 창이 백업 창 자리·화면 안 {a} → {r}')
            st = pg.evaluate("document.querySelector('#rpop .rstore').innerText")
            ok('%' not in st and '기록 ' in st and ' / ' in st, f'{tag} 11 복원 창 저장 공간 줄에 % 없음(크기로) {st[:60]!r}')
            if not t:
                t2 = pg.evaluate("(document.querySelector('#rstp')||{}).textContent||''")
                ok('홈 화면' not in t2, f'{tag} 맥 복원 창에 홈 화면 추가 안내 없음 {t2!r}')
            pg.keyboard.press('Escape')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

def subject(b):
    print('== 14~22 과목 홈·과목 메뉴')
    for tag, w, h, t in VP:
        ctx, pg = new(b, w, h, t)
        def menu_jb():
            if w <= 860: tap(pg, '#navbtn', t); pg.wait_for_timeout(300)
            pg.evaluate("document.querySelector('#nav .nvd[data-d=_jb]').click()"); pg.wait_for_timeout(700)
            return pg.evaluate("[__h.JB.F.mine,__h.JB.F.n,__h.JB.one,__h.JB.vis.length,+(document.querySelector('#nav .nvd[data-d=_jb] .r')||{textContent:0}).textContent]")
        go(pg, '#/CONS/_home/_home', 700)
        r = pg.evaluate("[document.querySelector('#hprog [data-jbf=ng]').disabled,document.querySelector('#hprog [data-jbf=ng]').title]")
        ok(r[0] is True and r[1], f'{tag} 14 틀린 것 0 → [틀린 것 다시] 꺼짐 {r}')
        pg.click('#hprog [data-jbf=todo]'); pg.wait_for_timeout(600)
        ok(pg.evaluate("__h.JB.F.mine") == 'todo', f'{tag} 14 안 푼 것 풀기 → JB 안 푼 것')
        go(pg, '#/CONS/_home/_home', 500); r = menu_jb()
        ok(r[0] == '' and r[1] == 0 and r[3] == r[4] > 0, f'{tag} 14 그 뒤 메뉴 JB 문제 → 필터 풀림 · 목록 {r[3]} = 메뉴 {r[4]}')
        go(pg, '#/CONS/_home/_home', 500)
        pg.evaluate("document.querySelector('#htop [data-one]').click()"); pg.wait_for_timeout(800)
        ok(pg.evaluate("__h.JB.one") is True, f'{tag} 14 2회 이상 한 장씩 → 한 장씩')
        go(pg, '#/CONS/_home/_home', 500); r = menu_jb()
        ok(r[1] == 0 and r[2] is False and r[3] == r[4], f'{tag} 14 한 장씩(2회 이상) 뒤 메뉴 JB 문제 → 전체 목록 {r}')
        # 15 비교표 수
        go(pg, '#/CONS/_home/_home', 500)
        a = pg.evaluate("+document.querySelector('#hero [data-hgo=_tbl]').textContent.replace(/\\D/g,'')")
        bnav = pg.evaluate("+(document.querySelector('#nav .nvd[data-d=_tbl] .r')||{textContent:0}).textContent")
        go(pg, '#/CONS/_tbl/_tbl', 800); c = pg.evaluate("document.querySelectorAll('#stage table.cmp').length")
        ok(a == bnav == c > 0, f'{tag} 15 비교표 머리 {a} = 메뉴 {bnav} = 화면 {c}')
        # 16 2회 이상 펼침 → 문항 → 뒤로
        go(pg, '#/CONS/_home/_home', 600)
        pg.click('#htop [data-topmore]'); pg.wait_for_timeout(200)
        pg.evaluate("document.querySelector('#htop li.tmr').scrollIntoView({block:'center'})"); pg.wait_for_timeout(1200)
        y0 = pg.evaluate("scrollY"); pg.evaluate("document.querySelector('#htop li.tmr .q').click()"); pg.wait_for_timeout(900)
        pg.go_back(); pg.wait_for_timeout(1800)
        r = pg.evaluate("[document.querySelector('#htop').classList.contains('all'),scrollY]")
        ok(r[0] and abs(r[1] - y0) < 40, f'{tag} 16 펼친 2회 이상 → 문항 → 뒤로: 펼친 그대로 · y {y0} → {r[1]}')
        # 17 새로고침 스크롤
        go(pg, '#/CONS/_home/_home', 600); pg.evaluate("scrollTo(0,900)"); pg.wait_for_timeout(1300)
        pg.reload(); pg.wait_for_function("window.__h&&__h.plStat().pend===0", timeout=60000); pg.wait_for_timeout(1800)
        y = pg.evaluate("scrollY"); ok(abs(y - 900) < 40, f'{tag} 17 과목 홈 새로고침 → 같은 위치 {y}')
        # 18 참고 링크 글자(이동 링크) — 켠 뒤에도 같은 말
        go(pg, '#/OMS1/_home/_home', 500)
        t1 = pg.evaluate("document.querySelector('#hprog [data-reftog]').textContent")
        pg.click('#hprog [data-reftog]'); pg.wait_for_timeout(700)
        h1 = pg.evaluate("location.hash")
        go(pg, '#/OMS1/_home/_home', 500); t2 = pg.evaluate("document.querySelector('#hprog [data-reftog]').textContent")
        ok(t1.startswith('JB에서 참고') and t1.endswith('→') and h1.startswith('#/OMS1/_jb') and t2 == t1, f'18 참고 링크 {t1!r} → {h1} · 다시 {t2!r}')
        # 19 강의 바로가기 간격
        if w <= 860:
            go(pg, '#/CONS/_home/_home', 500)
            r = pg.evaluate("(()=>{const o=document.querySelector('#hguide ol').getBoundingClientRect(),l=document.querySelector('#stage .ljump').getBoundingClientRect();return l.top-o.bottom})()")
            ok(r >= 8, f'{tag} 19 강의 바로가기가 공부 순서와 떨어짐 {r:.0f}px')
        # 20 창을 바로 닫아도 읽던 자리(새로고침)
        go(pg, '#/CONS/DHS/learn', 1500); pg.evaluate("scrollTo(0,3000)"); pg.wait_for_timeout(250)
        pg.reload(); pg.wait_for_function("window.__h&&__h.plStat().pend===0", timeout=60000); pg.wait_for_timeout(300)
        aid = pg.evaluate("(JSON.parse(localStorage.getItem('jblhub.v1.lastBy')||'{}').CONS||{}).aid||''")
        ok(aid and not aid.endswith(':frame'), f'{tag} 20 스크롤 0.25초 뒤 바로 새로고침해도 읽던 자리 {aid}')
        # 22 IMPL 메뉴 강의 이름
        if w > 860:
            go(pg, '#/IMPL/_home/_home', 500)
            cut = pg.evaluate("[...document.querySelectorAll('#nav .nvl .el')].filter(e=>e.scrollHeight>e.clientHeight+1||e.scrollWidth>e.clientWidth+1).map(e=>e.textContent)")
            ok(not cut, f'{tag} 22 IMPL 메뉴 강의 이름 잘림 없음 {cut}')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

with sync_playwright() as p:
    b = p.chromium.launch()
    for f in (hub_rest, hub_home, subject):
        try: f(b)
        except Exception as e: ok(False, f'{f.__name__} 예외 {str(e)[:300]}')
    b.close()
print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
_sys.exit(1 if fails else 0)
