"""ux4c 2회차 회귀 — 4차 개편 뒤 오류 찾기 2회차에서 재현된 것.
허브: 허브(홈·달력·검색)에서 쉬는 중에는 움직여도 휴식이 이어지고 과목 문서를 열 때 끝남 · 이어서·최근 제목에 배지 글자 없음
     · '지금 휴식 m:ss'·'오늘 휴식 h:mm' 이름 구분(시계 창 '지금 구간' 중복 없음) · 📖 공부로 바꾸면 머리·메뉴 숫자가 곧바로
     · 과목 안 검색은 과목 메뉴·빵부스러기 · ■ 멈춤 알림에 % 없음 · 오늘 할 일 '달력에서 고치기' 없음 · 자리 비움 → 휴식 숫자가 이어짐
     · 백업 경고 기준 하나(bkDue) · 시계 창·⏱ 크게 포커스(열면 안 · Tab 안에서 · Esc 뒤 알약) · 달력 보던 달 ?m= · 지난달 요약에 연속 없음 · 달력 '취소' 버튼
과목: 공부 순서 '이어서'가 JB·표·예상을 열어도 마지막 강의 · '안 푼 것 n →'은 n문항 전부 · 과목이 바뀌거나 과목 홈이면 형광펜·빈칸 모드 끔
     · 과목 홈은 집중 모드를 적용하지 않음 · 과목 바꾸기 ↑↓ · 메뉴 '내 표시' 숫자 곧바로 · 정리표 탭 카드 목차 표시 · 강의 바로가기 칩 이름 안 잘림
학습: 복습 보기(R) 뒤 Esc = 복습 끔 · 가리기(이 카드)를 켠 채 R = 강의 전체 가림(끄면 되돌림) · 막대를 숨긴 채 H·B = 막대 다시 보임 · 메모 Esc = 저장·닫기
맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)"""
import os as _os, sys as _sys, re, datetime; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def new(b, w, h, touch=False, clock=None):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch); pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    pg.on('dialog', lambda d: d.accept())
    if clock: pg.clock.install(time=clock)
    pg.goto('about:blank'); pg.goto(U + '#/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')")
    return ctx, pg
def go(pg, h, wait=500):
    pg.goto('about:blank'); pg.goto(U + h)
    pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')", timeout=60000); pg.wait_for_timeout(wait)
def mv(pg, i=0):
    pg.mouse.move(300 + i % 7, 300 + i % 5); pg.mouse.move(310, 320 + i % 3)
def key(pg, k, code=None, shift=False):
    pg.evaluate("([k,c,s])=>document.dispatchEvent(new KeyboardEvent('keydown',{key:k,code:c,shiftKey:s,bubbles:true}))", [k, code or '', shift]); pg.wait_for_timeout(250)
CK = "(c=>({st:c.dataset.st,t:c.querySelector('.ckt').textContent,l:c.querySelector('.ckl').textContent}))(document.querySelector('#clock'))"
TREST = "Object.values(JSON.parse(localStorage.getItem('jblhub.v1.trest')||'{}')).reduce((a,v)=>a+(+v||0),0)"
T0 = datetime.datetime(2026, 9, 30, 10, 0, 0)
TOASTS = "(JSON.parse(sessionStorage.getItem('jblhub.v1.toasts')||'[]')).map(x=>x&&(x.t||x[1]||'')).join(' | ')"
def ms_of(t):
    p = [int(x) for x in t.split(':')]; return p[0] * 60 + p[1]

def hub_rest(b):
    print('== 허브에서 쉬는 중: 움직여도 휴식 이어짐 · 문서를 열면 끝 · 이름(지금 휴식/오늘 휴식) · 📖 공부로 바꾸면 숫자 곧바로')
    for tag, w, h, t in [('mac', 1280, 900, False), ('port', 820, 1180, True)]:
        ctx, pg = new(b, w, h, t, clock=T0)
        go(pg, '#/CONS/WHT/learn', 1200)
        for i in range(10): mv(pg, i); pg.clock.run_for(30000)
        pg.evaluate("__h.home()"); pg.wait_for_timeout(200)
        pg.clock.run_for(130000); pg.clock.run_for(180000); pg.wait_for_timeout(200)
        ok(pg.evaluate(CK)['st'] == 'rest', f'{tag} 허브 홈 5분 → 휴식 {pg.evaluate(CK)}')
        # 허브에서 입력(맥 마우스 · 아이패드 톡)
        if t: pg.evaluate("(()=>{const t=new Touch({identifier:1,target:document.body,clientX:5,clientY:400});document.body.dispatchEvent(new TouchEvent('touchstart',{bubbles:true,touches:[t],targetTouches:[t],changedTouches:[t]}));document.body.dispatchEvent(new TouchEvent('touchend',{bubbles:true,touches:[],targetTouches:[],changedTouches:[t]}));})()")
        else: mv(pg, 3)
        pg.clock.run_for(2000); pg.wait_for_timeout(200)
        r = pg.evaluate("[document.querySelector('#clock').dataset.st,document.querySelector('#idleband').hidden]")
        ok(r == ['rest', True], f'{tag} 허브에서 움직여도 휴식 그대로 · 띠 없음 {r}')
        tr0 = pg.evaluate(TREST)
        for i in range(10):
            if i % 3 == 0: mv(pg, i)
            pg.clock.run_for(60000)
        pg.wait_for_timeout(200); tr1 = pg.evaluate(TREST)
        ok(pg.evaluate(CK)['st'] == 'rest' and tr1 - tr0 >= 9 * 60000, f'{tag} 허브에서 10분 더 → 휴식 기록 +{(tr1 - tr0) // 60000}분')
        # 이름: 머리 띠 '오늘 휴식' · 시계 창 '지금 휴식' 한 번 · '지금 구간' 없음 · 머리 '오늘 휴식'
        band = pg.inner_text('#home [data-trk="band"]') if pg.query_selector('#home [data-trk="band"]') else pg.inner_text('#home .hband')
        ok('오늘 휴식' in band and not re.search(r'(?<!오늘 )휴식 \d', band), f'{tag} 머리 띠 합계는 "오늘 휴식" {band!r}')
        pg.click('#clock'); pg.wait_for_timeout(200)
        tp = pg.inner_text('#tpop')
        ok(tp.count('지금 휴식') == 1 and '지금 구간' not in tp and '오늘 휴식' in tp, f'{tag} 시계 창 지금 휴식 한 번 · 지금 구간 없음 {tp!r}')
        ok(pg.evaluate("document.querySelector('#tpop').contains(document.activeElement)"), f'{tag} 시계 창을 열면 포커스가 창 안')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.activeElement&&document.activeElement.id") == 'clock', f'{tag} Esc → 포커스 시계 알약')
        # 과목 문서를 열면 휴식 끝 + 띠
        pg.evaluate("__h.openDoc('CONS','WHT','learn')"); pg.wait_for_timeout(400)
        r = pg.evaluate("[document.querySelector('#clock').dataset.st,!document.querySelector('#idleband').hidden,document.querySelector('#idleband').dataset.k]")
        ok(r[0] != 'rest' and r[1] and r[2] == 'rest', f'{tag} 과목 문서를 열면 휴식 끝 · [☕ 쉬었어요][📖 공부했어요] 띠 {r}')
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()
    print('== 📖 공부했어요 → 머리·이번 주·메뉴 숫자가 곧바로')
    ctx, pg = new(b, 1280, 900, clock=T0)
    go(pg, '#/CONS/WHT/learn', 1200)
    for i in range(20): mv(pg, i); pg.clock.run_for(30000)
    pg.evaluate("__h.home()"); pg.wait_for_timeout(200)
    for i in range(7): pg.clock.run_for(60000)
    pg.evaluate("__h.restBack(Date.now(),'x')"); pg.wait_for_timeout(200)
    pg.click('#idleband [data-rb=study]'); pg.wait_for_timeout(300)
    r = pg.evaluate("[document.querySelector('#clock .ckt').textContent,document.querySelector('#home [data-hb=td]').textContent,document.querySelector('#home [data-hw=tot]').textContent,document.querySelector('#nav [data-nb=wk]').textContent]")
    ok(r[0].rsplit(':', 1)[0] == r[1] == r[2] and r[3].endswith(r[1]) and ms_of(r[1]) >= 16, f'알약 = 머리 = 이번 주 = 메뉴 곧바로 {r}')
    ok(not pg.errs, f'오류 0 {pg.errs[:3]}')
    ctx.close()

def hub_misc(b):
    print('== 제목 배지 · 과목 검색 메뉴 · ■ 알림 % · 할 일 버튼 · 백업 경고 · ⏱ 크게 포커스')
    ctx, pg = new(b, 1180, 820, True)
    for h in ['#/CONS/WHT/learn', '#/CONS/WHT/sum', '#/OMS1/_tbl']:
        go(pg, h, 800); pg.evaluate("window.scrollBy(0,60)"); pg.wait_for_timeout(1500)
        ti = pg.evaluate("(JSON.parse(localStorage.getItem('jblhub.v1.last')||'{}')).ti||''")
        ok(ti and not re.search(r'(카드 \d+ · \d+묶음|기출 \d+)$', ti), f'{h} 저장 제목에 배지 글자 없음 {ti!r}')
    go(pg, '#/', 400)
    pg.evaluate("(()=>{const o={s:'CONS',d:'WHT',t:'learn',aid:'',off:0,at:Date.now()+1000,ti:'이 강의의 틀카드 19 · 7묶음'};localStorage.setItem('jblhub.v1.last',JSON.stringify(o));const a=JSON.parse(localStorage.getItem('jblhub.v1.lastBy')||'{}');a.CONS=o;localStorage.setItem('jblhub.v1.lastBy',JSON.stringify(a));})()")
    pg.evaluate("__h.home({push:false})"); pg.wait_for_timeout(400)
    tx = pg.inner_text('#home .hres') if pg.query_selector('#home .hres') else ''
    ok('이 강의의 틀' in tx and '묶음' not in tx, f'이미 저장된 제목도 배지를 떼고 보임 {tx!r}')
    ok(not pg.query_selector('#home .htodo [data-tvgo2]'), "오늘 할 일에 '달력에서 고치기' 없음")
    # 과목 안 검색
    go(pg, '#/CONS/WHT/learn', 800)
    pg.fill('#gsearch', '미백'); pg.press('#gsearch', 'Enter'); pg.wait_for_timeout(800)
    r = pg.evaluate("[location.hash,document.querySelector('#nav').dataset.mode,document.querySelector('#crumb').innerText.replace(/\\s+/g,'')]")
    ok('&s=CONS' in r[0] and r[1] == 'subj' and '보존' in r[2] and r[2].endswith('검색'), f'과목 안 검색 → 과목 메뉴·빵부스러기 {r}')
    pg.evaluate("document.querySelector('[data-swide]').click()"); pg.wait_for_timeout(600)
    ok(pg.evaluate("document.querySelector('#nav').dataset.mode") == 'hub', '전체로 넓히기 → 허브 메뉴')
    ok(not pg.errs, f'오류 0 {pg.errs[:3]}')
    ctx.close()
    ctx, pg = new(b, 1280, 900)
    go(pg, '#/', 600)
    pg.click('#clock'); pg.wait_for_timeout(150); pg.click('#tpop [data-tp=start]'); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelector('#home [data-trb=stop]').click()"); pg.wait_for_timeout(300)
    tx = pg.evaluate(TOASTS)
    ok('%' not in tx and '/ 목표' in tx, f'■ 멈춤 알림에 % 없음 {tx!r}')
    ok('(92%)' not in pg.evaluate("document.querySelector('#help').textContent") and '[📊 통계]' not in pg.evaluate("document.querySelector('#help').textContent"), '도움말 % 예시·옛 [📊 통계] 없음')
    # ⏱ 크게 포커스
    go(pg, '#/', 500)
    pg.focus('#clock'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    pg.evaluate("document.querySelector('#tpop [data-tp=big]').click()"); pg.wait_for_timeout(300)
    ok(pg.evaluate("document.querySelector('#bigclock').contains(document.activeElement)"), '⏱ 크게를 열면 포커스가 창 안')
    ins = []
    for i in range(4): pg.keyboard.press('Tab'); ins.append(pg.evaluate("document.querySelector('#bigclock').contains(document.activeElement)"))
    ok(all(ins), f'⏱ 크게 Tab은 창 안에서만 {ins}')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(pg.evaluate("[!document.querySelector('#bigclock').classList.contains('on'),document.activeElement.id]") == [True, 'clock'], 'Esc → ⏱ 크게 닫힘 · 포커스 시계 알약')
    # 백업 경고 기준 하나
    for tag, setup, want in [('보낸 적 없음·기록 없음', "", False), ('10일 전·그 뒤 바뀐 것 없음', "localStorage.setItem('jblhub.v1.lastBackup',String(Date.now()-10*864e5))", False),
                             ('10일 전·그 뒤 형광펜', "localStorage.setItem('jblhub.v1.lastBackup',String(Date.now()-10*864e5));localStorage.setItem('jblhub.v1.annAt.CONS',String(Date.now()-864e5))", True)]:
        pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1');" + setup); go(pg, '#/', 600)
        r = pg.evaluate("[document.querySelector('#bkup').classList.contains('warn'),!!document.querySelector('#home .hbk.warn'),/백업/.test((document.querySelector('#home .htodo')||{}).innerText||'')]")
        ok(r == [want, want, want], f'백업 {tag} → 메뉴·홈 바닥·할 일 모두 {want} {r}')
    ok(not pg.errs, f'오류 0 {pg.errs[:3]}')
    ctx.close()

def away_rest(b):
    print('== 자리 비움 → 휴식 숫자가 이어짐')
    ctx, pg = new(b, 1280, 900, clock=T0)
    go(pg, '#/CONS/WHT/learn', 1200)
    for i in range(6): mv(pg, i); pg.clock.run_for(30000)
    pg.clock.run_for(6 * 60000 + 30000); pg.wait_for_timeout(200); a = pg.evaluate(CK)
    pg.clock.run_for(90000); pg.wait_for_timeout(200); c = pg.evaluate(CK)
    ok(a['l'].startswith('자리 비움') and c['st'] == 'rest' and c['l'].startswith('휴식'), f'자리 비움 → 휴식 {a["l"]} → {c["l"]}')
    if a['l'].startswith('자리 비움') and c['l'].startswith('휴식'):
        x, y = ms_of(a['l'].split()[-1]), ms_of(c['l'].split()[-1])
        ok(abs((y - x) - 90) <= 5, f'90초 뒤 휴식 숫자가 자리 비움에서 이어짐(거꾸로 뛰지 않음) {x}s → {y}s')
    ctx.close()

def cal(b):
    print('== 달력 보던 달 · 지난달 연속 없음 · 취소 버튼')
    ctx, pg = new(b, 1280, 900, clock=T0)
    pg.evaluate("localStorage.setItem('jblhub.v1.time',JSON.stringify({'2026-08-15':{CONS:3*3600e3},'2026-09-28':{CONS:3*3600e3},'2026-09-29':{CONS:3*3600e3},'2026-09-30':{CONS:3*3600e3}}))")
    go(pg, '#/_cal', 800)
    s9 = pg.inner_text('#home .calsum')
    pg.click('[data-calm="-1"]'); pg.wait_for_timeout(400)
    s8 = pg.inner_text('#home .calsum'); h8 = pg.evaluate('location.hash')
    ok('연속' in s9 and '연속' not in s8 and s8.startswith('8월'), f'연속은 이번 달만 {s9!r} / {s8!r}')
    ok('m=2026-08' in h8, f'주소에 보던 달 {h8}')
    pg.reload(); pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0", timeout=60000); pg.wait_for_timeout(600)
    ok(pg.inner_text('#home .calsum').startswith('8월'), '새로고침해도 8월')
    pg.click('[data-calm="0"]'); pg.wait_for_timeout(300)
    ok('m=' not in pg.evaluate('location.hash'), f'오늘 달로 오면 ?m 없음 {pg.evaluate("location.hash")}')
    src = open(J.os.path.join(J.DOCS, 'index.html'), encoding='utf-8').read()
    ok('class="btn sm" data-cex="1">취소' in src, "기록 고치기 '취소'는 버튼 크기(.btn sm)")
    ok(not pg.errs, f'오류 0 {pg.errs[:3]}')
    ctx.close()

def subj(b):
    print('== 과목: 이어서 · 안 푼 것 n · 모드 · 집중 · 과목 바꾸기 ↑↓ · 내 표시 · 정리표 목차 · 칩')
    ctx, pg = new(b, 1280, 900)
    pg.evaluate("localStorage.setItem('jblhub.v1.tauto','false')")
    go(pg, '#/CONS/CRK/learn', 800)
    pg.evaluate("__h.goCard(6)"); pg.wait_for_timeout(1500)
    for d in ['_jb', '_sum', '_tbl', '_pred']:
        go(pg, '#/CONS/' + d, 600); pg.evaluate("window.scrollBy(0,200)"); pg.wait_for_timeout(1300)
    go(pg, '#/CONS/_home', 600)
    lk = pg.evaluate("(document.querySelector('#hguide .go-resume')||{}).textContent||''")
    ok('이어서' in lk and 'Cracked' in lk, f'JB·한눈표·비교표·예상을 열어도 공부 순서 이어서 = 마지막 강의 {lk!r}')
    ok('Cracked' in pg.inner_text('#stage'), "과목 홈 '최근 읽던 곳'에 마지막 강의가 남음")
    pg.click('#hguide .go-resume'); pg.wait_for_timeout(1200)
    ok(pg.evaluate("location.hash").startswith('#/CONS/CRK/learn') and pg.evaluate("scrollY") > 200, f'누르면 그 강의 그 자리 {pg.evaluate("[location.hash,scrollY]")}')
    # 2회 이상 → 안 푼 것 n
    go(pg, '#/CONS/_home', 600)
    pg.click('#hguide [data-jbn="2"]'); pg.wait_for_timeout(800)
    go(pg, '#/CONS/_home', 600)
    n = int(re.search(r'\d+', pg.inner_text('#hguide [data-jbf="todo"]')).group())
    pg.click('#hguide [data-jbf="todo"]'); pg.wait_for_timeout(900)
    q = pg.evaluate("[...document.querySelectorAll('#cards .qc')].filter(x=>x.offsetParent).length")
    ok(q == n, f"'2회 이상' 뒤 '안 푼 것 {n} →' = {q}문항")
    pg.reload(); pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0", timeout=60000); pg.wait_for_timeout(900)
    q2 = pg.evaluate("[...document.querySelectorAll('#cards .qc')].filter(x=>x.offsetParent).length")
    ok(q2 == n, f'새로고침 뒤에도 {q2}')
    # 형광펜 모드 — 과목이 바뀌면 끔 · 과목 홈에서 H는 켜지지 않음
    go(pg, '#/CONS/WHT/learn', 800); key(pg, 'ㅗ', 'KeyH')
    ok(pg.evaluate("document.body.classList.contains('mode-h')"), 'H → 형광펜 켜짐')
    pg.evaluate("__h.openDoc('OMS1','_home')"); pg.wait_for_timeout(400)
    ok(not pg.evaluate("document.body.classList.contains('mode-h')"), '과목을 바꾸면 형광펜 모드 꺼짐')
    key(pg, 'ㅗ', 'KeyH')
    ok(not pg.evaluate("document.body.classList.contains('mode-h')"), '과목 홈에서 H → 켜지지 않음(알림)')
    pg.evaluate("__h.openDoc('OMS1',__h.PACKS.OMS1.lect[0].k,'learn')"); pg.wait_for_timeout(600)
    ok(not pg.evaluate("document.body.classList.contains('mode-h')"), '다른 과목 강의에서 모드 꺼져 있음')
    # 집중 모드 — 과목 홈은 머리·메뉴·상단 막대 그대로
    key(pg, 'ㅍ', 'KeyV')
    ok(pg.evaluate("document.body.classList.contains('focus')"), 'V → 집중')
    pg.evaluate("__h.openDoc('OMS1','_home')"); pg.wait_for_timeout(500)
    r = pg.evaluate("[getComputedStyle(document.querySelector('#top')).display,document.querySelector('#hero').getBoundingClientRect().height>0,getComputedStyle(document.querySelector('#side')).display,[...document.querySelectorAll('.dfoc')].filter(x=>x.offsetParent).length]")
    ok(r[0] != 'none' and r[1] and r[2] != 'none' and r[3] == 0, f'집중 중 과목 홈 → 상단 막대·머리·메뉴 보임 · 집중 버튼 없음 {r}')
    pg.evaluate("__h.openDoc('OMS1',__h.PACKS.OMS1.lect[0].k,'learn')"); pg.wait_for_timeout(500)
    ok(pg.evaluate("document.body.classList.contains('focus')&&getComputedStyle(document.querySelector('#top')).display==='none'"), '강의로 돌아가면 집중 그대로')
    key(pg, 'ㅍ', 'KeyV')
    # 과목 바꾸기 ↑↓
    go(pg, '#/CONS/_home', 500)
    pg.focus('#nav [data-nvsw]'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    a0 = pg.evaluate("document.activeElement.dataset.nvsj")
    pg.keyboard.press('ArrowDown'); a1 = pg.evaluate("document.activeElement.dataset.nvsj")
    pg.keyboard.press('Home'); a2 = pg.evaluate("document.activeElement.dataset.nvsj")
    ok(a0 == 'CONS' and a1 and a1 != 'CONS' and a2 == 'OMS1', f'과목 바꾸기: 열면 지금 과목 · ↓ 다음 · Home 처음 {[a0, a1, a2]}')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
    # 내 표시 숫자 곧바로
    go(pg, '#/CONS/WHT/learn', 800)
    ok(pg.evaluate("!!document.querySelector('#nav [data-nb=\"mk.CONS\"]')"), "표시 0이어도 '내 표시' 숫자 칸이 있음")
    key(pg, 'ㅗ', 'KeyH')
    r = pg.evaluate("""(()=>{const el=[...document.querySelectorAll('#stage .tc li')].find(e=>e.textContent.trim().length>30&&e.getClientRects().length&&e.getBoundingClientRect().top>150);if(!el)return null;el.scrollIntoView({block:'center'});const r=el.getBoundingClientRect();return [r.left+4,r.top+Math.min(10,r.height/2),Math.min(r.right-4,r.left+160)]})()""")
    if r: pg.mouse.move(r[0], r[1]); pg.mouse.down(); pg.mouse.move(r[2], r[1], steps=6); pg.mouse.up(); pg.wait_for_timeout(500)
    mk = pg.evaluate("(document.querySelector('#nav [data-nb=\"mk.CONS\"]')||{}).textContent")
    ok(mk == '1', f"칠하면 메뉴 '내 표시 1' 곧바로 {mk!r}")
    key(pg, 'ㅗ', 'KeyH')
    # 정리표 목차
    go(pg, '#/CONS/WHT/sum', 800)
    for f in [0.35, 0.7]:
        pg.evaluate(f"window.scrollTo(0,document.documentElement.scrollHeight*{f})"); pg.wait_for_timeout(500)
        r = pg.evaluate("""(()=>{const on=document.querySelector('#nav .scard2.on');const line=innerHeight*.3;const rows=[...document.querySelectorAll('#stage [id^="m-WHT-"]')].filter(x=>x.offsetParent&&x.getBoundingClientRect().top<=line+2);const last=rows.length?+rows[rows.length-1].id.split('-').pop():null;return [on?+on.dataset.lj:null,last];})()""")
        ok(r[0] is not None and r[0] == r[1], f'정리표 {int(f * 100)}% → 카드 목차 표시 = 보는 행 {r}')
    ok(not pg.errs, f'오류 0 {pg.errs[:3]}')
    ctx.close()
    ctx, pg = new(b, 820, 1180, True)
    go(pg, '#/IMPL/_home', 700)
    cut = pg.evaluate("[...document.querySelectorAll('#stage .ljump .ljc span')].filter(s=>s.scrollWidth>s.clientWidth+1).map(s=>s.textContent)")
    ok(not cut, f'아이패드 세로 강의 바로가기 칩 이름 안 잘림 {cut}')
    ctx.close()

def learn(b):
    print('== 학습: 복습 Esc · 가리기+R · 숨긴 막대+H · 메모 Esc')
    for tag, w, h, t in [('mac', 1280, 900, False), ('port', 820, 1180, True)]:
        ctx, pg = new(b, w, h, t)
        pg.evaluate("localStorage.setItem('jblhub.v1.tauto','false')")
        go(pg, '#/CONS/WHT/learn', 800)
        RV = "[document.querySelector('#stage').classList.contains('review'),__h.QZ.on,__h.QZ.scope,document.querySelectorAll('#stage .k.qzk').length]"
        key(pg, 'ㄱ', 'KeyR'); a = pg.evaluate(RV)
        key(pg, 'Escape', 'Escape'); c = pg.evaluate(RV)
        tx = pg.evaluate(TOASTS)
        ok(a[0] and a[1] and a[3] > 50 and not c[0] and not c[1] and '가리기 보기를 껐어요' not in tx, f'{tag} R → Esc = 복습 끔(가리기만 풀리지 않음) {a} → {c}')
        pg.evaluate("__h.goCard(3)"); pg.wait_for_timeout(500)
        key(pg, 'ㅂ', 'KeyQ'); q = pg.evaluate(RV)
        key(pg, 'ㄱ', 'KeyR'); r = pg.evaluate(RV)
        key(pg, 'ㄱ', 'KeyR'); z = pg.evaluate(RV)
        ok(q[1] and q[2] == 'card' and r[0] and r[2] == 'all' and r[3] > q[3] and not z[0] and z[1] and z[2] == 'card' and z[3] == q[3], f'{tag} 가리기(이 카드) → R = 강의 전체 → R 끄면 이 카드로 {q} {r} {z}')
        key(pg, 'Escape', 'Escape')
        # 숨긴 막대 + H
        key(pg, 'ㅅ', 'KeyT')
        ok(pg.evaluate("document.body.classList.contains('kit-off')"), f'{tag} T → 막대 숨김')
        key(pg, 'ㅗ', 'KeyH')
        r = pg.evaluate("[document.body.classList.contains('kit-off'),document.body.classList.contains('mode-h'),getComputedStyle(document.querySelector('#kit')).display]")
        ok(r[0] is False and r[1] and r[2] != 'none', f'{tag} 숨긴 채 H → 막대 다시 보임·형광펜 {r}')
        key(pg, 'ㅗ', 'KeyH')
        # 메모 Esc
        key(pg, 'M', 'KeyM', True)
        ok(pg.evaluate("document.activeElement.id") == 'memota', f'{tag} Shift+M → 메모 입력')
        pg.keyboard.type('ab'); pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        r = pg.evaluate("[document.querySelector('#memo').classList.contains('on'),document.activeElement.id]")
        ok(r[0] is False and r[1] != 'memota', f'{tag} 메모에서 Esc → 닫힘·커서 빠짐 {r}')
        pg.keyboard.press('j'); pg.wait_for_timeout(200)
        mm = pg.evaluate("localStorage.getItem('jblhub.v1.memo.CONS.WHT')")
        ok(mm == '"ab"', f"{tag} 메모 'ab' 저장 · 뒤 단축키가 메모에 안 들어감 {mm}")
        ok(not pg.errs, f'{tag} 오류 0 {pg.errs[:3]}')
        ctx.close()

if __name__ == '__main__':
    only = _sys.argv[1:]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for f in [hub_rest, hub_misc, away_rest, cal, subj, learn]:
            if not only or f.__name__ in only: f(b)
        b.close()
    print('\n' + ('ALL OK' if not fails else f'FAIL {len(fails)}\n  ' + '\n  '.join(fails)))
    _sys.exit(1 if fails else 0)
