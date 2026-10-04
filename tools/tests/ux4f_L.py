"""ux4f L 회귀 — 공부 시간 기록 오류 9건(새 오류 찾기 2회차)
L1 달력 ✎로 구간을 옆 공부 구간과 겹치게 고치면 되물음([그래도 고치기]/[겹친 만큼 빼고]) · 휴식과 겹친 부분은 휴식에서 뺌 — 합계·줄·카드·알약·허브 홈 숫자가 같음 · 되돌리기
L2 ▶ 세션 중 ☕ 쉬는 동안 다른 과목으로 옮기거나 다른 창에서 다른 과목을 공부하면 그 뒤 세션 시간은 새 과목에
L3 ✎를 열고 아무것도 안 바꾸고 저장 = 기록 그대로(자정에 끝나는 줄 24:00 포함 · ✎ 표시 없음 · tedit 그대로)
L4 '+ 시간 추가'로 휴식 시간대에 공부를 넣으면 그 휴식은 공부로(휴식 줄·합계에서 빠짐) · 되돌리기
L5 같은 휴식은 띠·알림·달력 모두 내림(같은 분)   L6 측정 구간 있는 날 시간대 없이 5분 = '시간대 없음 0:05'
L7 ☕ 쉬기 뒤 계속 입력하면 '쉬는 중이에요' 띠   L8 ⏱ 크게도 알약처럼 '자리 비움'   L9 아이패드 달력 ±·고치기 줄 버튼 44px"""
import os as _os, sys as _sys, datetime, json, re; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
W = "!!(window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni'))"
D0 = J.study_today(); td = D0.isoformat()
DH = 0 if td <= '2026-10-03' else 6   # dayRows/daySegs의 s·e = 그 공부 날 시작(DCUT 뒤 06:00)부터 초 — 벽시계로 바꿀 때 더함
def fmtH(ms): m = int(max(0, ms) // 60000); return f'{m // 60}:{m % 60:02d}'
class P:
    def __init__(s, b, w=1280, h=900, touch=False, start=None, ctx=None):
        s.ctx = ctx or b.new_context(viewport={'width': w, 'height': h}, has_touch=touch)
        s.pg = s.ctx.new_page(); s.E = []
        s.pg.on('pageerror', lambda e: s.E.append(str(e)[:200])); s.pg.on('dialog', lambda d: d.accept())
        if not ctx: s.pg.clock.install(time=start or datetime.datetime.combine(D0, datetime.time(9, 0, 0)))
    def go(s, h, hard=True):
        pg = s.pg
        if hard: pg.goto('about:blank'); pg.goto(U + h)
        else: pg.evaluate(f"location.hash='{h}'")
        pg.clock.run_for(1500)
        for _ in range(150):
            if pg.evaluate(W): break
            pg.wait_for_timeout(100); pg.clock.run_for(100)
        pg.clock.run_for(500)
    def clear(s): s.go('#/'); s.pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')")
    def ev(s, js): return s.pg.evaluate(js)
    def run(s, ms): s.pg.clock.run_for(ms)
    def st(s): return s.ev("__h.trState()")
    def move(s, n=4, step=20000):
        for i in range(n): s.pg.mouse.move(300 + i * 20 + (n % 7), 420 + i); s.pg.mouse.wheel(0, 1); s.pg.clock.run_for(step)
    def pop(s, rx):
        s.ev("document.querySelector('#clock').click()"); s.run(300)
        r = s.ev(f"(b=>b?(b.click(),b.textContent.trim()):null)([...document.querySelectorAll('#tpop [data-tp],#tpop [data-trb]')].find(b=>/{rx}/.test(b.textContent)))")
        s.run(300); return r
    def clk(s, sel): r = s.ev(f"(b=>b?(b.click(),1):0)(document.querySelector('{sel}'))"); s.run(600); return r
    def tday(s): return s.ev(f"(()=>{{const x=__h.tDay('{td}');return Object.values(x).reduce((a,b)=>a+b,0)}})()")
    def rest(s): return s.ev(f"__h.restDay('{td}')")
    def rows(s): return s.ev("[...document.querySelectorAll('#calday .crow')].map(e=>e.textContent.replace(/\\s+/g,' ').trim())")
    def undo(s): r = s.ev("(b=>b?(b.click(),1):0)([...document.querySelectorAll('#toast button')].find(b=>/되돌리기/.test(b.textContent)))"); s.run(800); return r
    def view(s):
        """같은 날 숫자를 화면마다 — 합계(ms)·구간 합(초)·달력 카드·알약·휴식"""
        segs = s.ev(f"__h.daySegs('{td}')")
        st = sum(x['e'] - x['s'] for x in segs if not x['f'].startswith('r')); rs = sum(x['e'] - x['s'] for x in segs if x['f'].startswith('r'))
        s.run(1200)   # 알약은 1초마다 다시 그림
        return dict(t=s.tday(), seg=st, rseg=rs, rest=s.rest(), card=s.ev("[...document.querySelectorAll('.ccard')].slice(0,2).map(e=>e.textContent.replace(/\\s+/g,' '))"),
                    pill=s.ev("document.querySelector('#clock').dataset.today+' '+document.querySelector('#clock').dataset.lab"))
def same_nums(x, v, tag):
    t = v['t']; okc = fmtH(t) in v['card'][0] and fmtH(v['rest']) in v['card'][1]
    ok(abs(v['seg'] - t / 1000) <= 3 and abs(v['rseg'] - v['rest'] / 1000) <= 3 and okc and v['pill'].startswith(fmtH(t)),
       f"{tag} 숫자 일치 — 합계 {fmtH(t)}({t/1000:.0f}s) · 공부 구간 {v['seg']}s · 휴식 {fmtH(v['rest'])}/구간 {v['rseg']}s · 카드 {v['card']} · 알약 {v['pill'][:12]}")
def home_has(x, ms, tag):
    x.go('#/', False); x.run(800)
    h = x.ev("(document.querySelector('#home .hband')||document.querySelector('#home')).innerText.replace(/\\s+/g,' ')")
    ok(fmtH(ms) in h, f'{tag} 허브 홈 오늘 {fmtH(ms)} — {h[:80]}')
def setup3(x):
    """09:00–09:10 공부 → 자동 휴식 → 09:22–09:32 공부 → ■ 멈춤 → 달력"""
    x.clear(); x.go('#/CONS/WHT/learn'); x.move(30); x.run(12 * 60000); x.move(30); x.pop('멈춤'); x.run(1000)
    x.go('#/_cal/' + td, False); x.run(800)
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---- L1 ✎ 겹침
    x = P(b); setup3(x); v0 = x.view(); r0 = x.rows()
    ok(len(r0) == 3 and '휴식' in r0[1], f'L1 준비 줄 {r0}')
    x.clk('[data-cre="2"]'); x.ev("ceA.value='09:00'"); x.clk('[data-cesave="2"]')
    w = x.ev("(w=>w&&!w.hidden?w.textContent:'')(document.querySelector('#cewarn'))")
    ok('겹쳐요' in w and x.ev("document.querySelectorAll('#cewarn [data-cef]').length") == 2 and abs(x.tday() - v0['t']) < 2000,
       f'L1 ✎ 시작을 앞 공부 구간에 겹치게 → 되물음 [{w[:60]}] · 합계 그대로 {fmtH(x.tday())}')
    R0 = x.ev(f"__h.dayRows('{td}').map(r=>[r.s,r.e])")
    x.clk('#cewarn [data-cef="cut"]'); v1 = x.view(); r1 = x.rows()
    exp = (R0[2][1] + DH * 3600 - 9 * 3600) * 1000   # 앞 구간 겹친 몫은 빼고 휴식 시간대는 공부로 = 09:00–셋째 줄 끝 벽시계(넘지 않음)
    ok(abs(v1['t'] - exp) <= 3000 and v1['rest'] < 60000 and not any('휴식' in r for r in r1),
       f"L1 [겹친 만큼 빼고] 합계 {fmtH(v0['t'])}→{fmtH(v1['t'])}({v1['t']/1000:.0f}s, 기대 {exp/1000:.0f}s) · 휴식 {fmtH(v0['rest'])}→{fmtH(v1['rest'])} · 줄 {r1}")
    same_nums(x, v1, 'L1 고친 뒤')
    ok(sum(1 for r in r1 if '✎' in r) >= 1, 'L1 고친 줄 ✎ 표시')
    x.undo(); v2 = x.view()
    ok(abs(v2['t'] - v0['t']) < 2000 and abs(v2['rest'] - v0['rest']) < 2000 and len(x.rows()) == 3, f"L1 되돌리기 → {fmtH(v2['t'])} · 휴식 {fmtH(v2['rest'])} · 줄 {len(x.rows())}")
    # 휴식하고만 겹침(앞 공부 줄 끝을 휴식 안으로) — 되묻지 않고 그 부분을 휴식에서 뺌
    e0 = x.ev(f"__h.dayRows('{td}')[0].e") + DH * 3600; x.clk('[data-cre="0"]')
    x.ev(f"ceB.value=('0'+Math.floor({e0 + 300}/3600)).slice(-2)+':'+('0'+Math.floor({e0 + 300}/60)%60).slice(-2)"); x.clk('[data-cesave="0"]'); v3 = x.view()
    ok(not x.ev("(w=>w&&!w.hidden)(document.querySelector('#cewarn'))") and 4 * 60000 <= v3['t'] - v0['t'] <= 6 * 60000 and 4 * 60000 <= v0['rest'] - v3['rest'] <= 6 * 60000,
       f"L1 끝을 휴식 안으로 5분 → 공부 +{(v3['t']-v0['t'])/60000:.1f}분 · 휴식 −{(v0['rest']-v3['rest'])/60000:.1f}분")
    same_nums(x, v3, 'L1 휴식 겹침 뒤')
    x.undo(); v4 = x.view(); ok(abs(v4['t'] - v0['t']) < 2000 and abs(v4['rest'] - v0['rest']) < 2000 and x.ev(f"__h.daySegs('{td}').filter(s=>s.f[0]==='r').length") == 1,
                                f"L1 되돌리기 → 공부 {fmtH(v4['t'])} · 휴식 {fmtH(v4['rest'])}(휴식 구간 하나로)")
    # [그래도 고치기]
    x.clk('[data-cre="2"]'); x.ev("ceA.value='09:00'"); x.clk('[data-cesave="2"]'); x.clk('#cewarn [data-cef="all"]'); v5 = x.view()
    ok(v5['t'] > v0['t'] + 15 * 60000 and v5['rest'] < 60000, f"L1 [그래도 고치기] = 겹친 채 고침(사용자 선택) {fmtH(v5['t'])} · 휴식은 공부로 {fmtH(v5['rest'])}")
    x.undo(); ok(not x.E, f'L1 콘솔 오류 없음 {x.E[:2]}'); x.ctx.close()
    # ---- L4 + 시간 추가가 휴식 시간대
    x = P(b); setup3(x); v0 = x.view()
    x.ev("document.querySelector('#cadd').open=true"); x.run(200)
    rs = x.ev(f"__h.daySegs('{td}').find(s=>s.f[0]==='r')"); ws = rs['s'] + DH * 3600; hm = f"{ws // 3600 % 24:02d}:{ws // 60 % 60:02d}"
    x.ev(f"caH.value=0;caM.value=5;caT.value='{hm}'"); x.ev("document.querySelector('[data-cago]').click()"); x.run(800); v1 = x.view()
    ok(4.9 * 60000 <= v1['t'] - v0['t'] <= 5.1 * 60000 and 4 * 60000 <= v0['rest'] - v1['rest'] <= 6 * 60000 and '휴식' in x.ev("document.querySelector('#toast').textContent"),
       f"L4 휴식 시간대 {hm}에 +5분 → 공부 +{(v1['t']-v0['t'])/60000:.1f}분 · 휴식 {fmtH(v0['rest'])}→{fmtH(v1['rest'])}")
    same_nums(x, v1, 'L4 더한 뒤')
    home_has(x, v1['t'], 'L4')
    x.go('#/_cal/' + td, False); x.run(500)
    x.ev("document.querySelector('#cadd').open=true"); x.run(200); x.ev("caH.value=0;caM.value=12;caT.value='09:10'"); x.ev("document.querySelector('[data-cago]').click()"); x.run(800)
    wa = x.ev("(w=>w.hidden?'':w.textContent)(document.querySelector('#cawarn'))"); x.clk('#cawarn [data-cago="cut"]')
    ok('이미' in wa and x.rest() < 60000 and not any('휴식' in r for r in x.rows()), f'L4 휴식 전부 덮으면 휴식 줄 없음 · 휴식 {fmtH(x.rest())}')
    x.undo(); v2 = x.view(); ok(abs(v2['t'] - v1['t']) < 2000 and abs(v2['rest'] - v1['rest']) < 2000, f"L4 되돌리기 → {fmtH(v2['t'])} · 휴식 {fmtH(v2['rest'])}")
    ok(not x.E, f'L4 콘솔 오류 없음 {x.E[:2]}'); x.ctx.close()
    # ---- L3 바꾸지 않고 저장
    for t0 in [datetime.time(23, 40, 30), datetime.time(9, 0, 30)]:
        x = P(b, start=datetime.datetime.combine(D0, t0)); x.clear(); x.go('#/CONS/WHT/learn')
        x.move(3); x.move(60); x.pop('멈춤'); x.run(60000)
        b0 = x.tday(); x.go('#/_cal/' + td, False); x.run(800); te0 = x.ev("(JSON.parse(localStorage.getItem('jblhub.v1.tedit'))||[]).length")
        row = x.rows()[0]; x.clk('[data-cre="0"]'); x.clk('[data-cesave="0"]'); row2 = x.rows()[0]
        ok(x.tday() == b0 and row2 == row and x.ev("(JSON.parse(localStorage.getItem('jblhub.v1.tedit'))||[]).length") == te0,
           f'L3 {t0} 그대로 저장 → 합계 차 {(x.tday()-b0)/1000:.0f}s · 줄 {row[:24]} → {row2[:24]}')
        x.ctx.close()
    # ---- L2 쉬는 동안 다른 과목으로 · 다른 창
    x = P(b); x.clear(); x.go('#/')
    x.ev("[...document.querySelectorAll('[data-trb=start]')].find(e=>e.offsetParent).click()"); x.run(500)
    x.go('#/CONS/WHT/learn', False); x.move(15); x.pop('쉬기'); x.run(60000)
    x.go('#/ANAT/TMJ/learn', False); x.run(1000); x.pop('다시'); x.move(15)
    tm = json.loads(x.ev("localStorage.getItem('jblhub.v1.timed')"))[td]; ts = x.ev("(t=>[t.S,t.D])(__h.tsRead())")
    ok(ts == ['ANAT', 'TMJ'] and tm.get('ANAT:TMJ', 0) >= 4.5 * 60000 and tm.get('CONS:WHT', 0) <= 5.5 * 60000, f'L2 쉬는 동안 ANAT로 → 다시 공부 5분: 세션 {ts} · {tm}')
    x.pop('멈춤'); x.run(1000); x.go('#/_cal/' + td, False); x.run(800); same_nums(x, x.view(), 'L2 멈춘 뒤')
    x.ctx.close()
    a = P(b); a.clear(); a.go('#/'); a.ev("[...document.querySelectorAll('[data-trb=start]')].find(e=>e.offsetParent).click()"); a.run(500)
    a.go('#/CONS/WHT/learn', False); a.move(6)
    c = P(b, ctx=a.ctx); c.pg.bring_to_front(); c.go('#/ANAT/TMJ/learn'); c.move(30)
    tm = json.loads(a.ev("localStorage.getItem('jblhub.v1.timed')"))[td]
    ok(tm.get('ANAT:TMJ', 0) >= 9 * 60000 and tm.get('CONS:WHT', 0) <= 3 * 60000, f'L2 세션 중 다른 창에서 ANAT 10분 → {tm}')
    ok(not a.E and not c.E, f'L2 콘솔 오류 없음 {(a.E + c.E)[:2]}'); a.ctx.close()
    # ---- L5 반올림
    x = P(b); x.clear(); x.go('#/CONS/WHT/learn'); x.move(15); x.run(int(12.2 * 60000)); x.pg.mouse.move(500, 500); x.pg.mouse.wheel(0, 1); x.run(1000)
    band = x.ev("document.querySelector('#idleband').textContent"); x.run(11000); toast = x.ev("document.querySelector('#toast').textContent")
    x.go('#/_cal/' + td, False); x.run(800); card = x.ev("[...document.querySelectorAll('.ccard')][1].textContent")
    m = int(x.rest() // 60000)
    ok(f'쉬었어요 {m}분' in band and f'휴식 {m}분' in toast and fmtH(x.rest()) in card, f'L5 같은 휴식 {m}분 — 띠 [{band[:40]}] · 알림 [{toast[:20]}] · 카드 [{card[:16]}]')
    x.ctx.close()
    # ---- L6 시간대 없음
    x = P(b); x.clear(); x.go('#/CONS/WHT/learn'); x.move(30); x.pop('멈춤'); x.run(1000)
    x.go('#/_cal/' + td, False); x.run(800)
    x.ev("document.querySelector('#cadd').open=true;caH.value=0;caM.value=5"); x.ev("document.querySelector('[data-cago]').click()"); x.run(800)
    nr = [r for r in x.rows() if '시간대 없음' in r]
    ok(nr and '0:05' in nr[0] and x.ev(f"__h.ntsAmt('{td}','CONS')") == 300000, f"L6 시간대 없이 5분 → {nr} · ± 한도 {x.ev(f'__h.ntsAmt(\"{td}\",\"CONS\")')}")
    x.ctx.close()
    # ---- L7 쉬기 뒤 계속 입력
    # 10-04 사용자: 자동 측정이 켜져 있으면 쉬는 중 움직임 = 공부 시작(띠 없이) — 띠는 자동 측정 끔일 때만
    x = P(b); x.clear(); x.go('#/CONS/WHT/learn'); x.move(6); x.pop('쉬기'); x.move(30)
    ok(x.st() in ('run', 'sess'), f'L7 자동 측정 켬 · ☕ 쉬기 뒤 계속 입력 → 공부로 ({x.st()})')
    x.ctx.close()
    x = P(b); x.clear(); x.go('#/CONS/WHT/learn'); x.ev("__h.T.auto=false;localStorage.setItem('jblhub.v1.tauto','false')"); x.pop('공부 시작'); x.move(6); x.pop('쉬기'); x.move(30)
    bd = x.ev("(t=>[t.hidden,t.dataset.k])(document.querySelector('#trband'))")
    ok(x.st() == 'rest' and bd == [False, 'rest'], f'L7 자동 측정 끔 · ☕ 쉬기 뒤 10분 계속 입력 → 띠 {bd}')
    x.ctx.close()
    # ---- L8 ⏱ 크게 자리 비움
    x = P(b); x.clear(); x.go('#/CONS/WHT/learn'); x.move(6)
    x.ev("document.querySelector('#clock').click()"); x.run(300)
    x.ev("[...document.querySelectorAll('#tpop [data-tp],#tpop [data-trb]')].find(b=>/크게/.test(b.textContent)).click()"); x.run(1000)
    l0 = x.ev("document.querySelector('#bcl').textContent"); x.run(150000)
    l1 = x.ev("document.querySelector('#bcl').textContent"); ck = x.ev("document.querySelector('#clock').innerText.replace(/\\s+/g,' ')")
    sec = lambda t: (lambda m: int(m.group(1)) * 60 + int(m.group(2)) if m else -99)(re.search(r'자리 비움 (\d+):(\d\d)', t))
    ok(x.st() == 'run' and '집중' in l0 and l1.startswith('자리 비움') and abs(sec(l1) - sec(ck)) <= 1, f'L8 ⏱ 크게 {l0} → 2분 30초 입력 없음 {l1} · 알약 {ck}')
    x.ctx.close()
    # ---- L9 아이패드 44px
    SZ = "(sel=>[...document.querySelectorAll(sel)].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return [(e.textContent.trim()||e.tagName).slice(0,6),Math.round(r.width),Math.round(r.height)]}))"
    for wv, hv in [(820, 1180), (1180, 820)]:
        x = P(b, wv, hv, True); x.clear(); x.go('#/CONS/WHT/learn'); x.move(15); x.pop('멈춤'); x.run(1000)
        x.go('#/_cal/' + td, False); x.run(800)
        x.ev("document.querySelector('#cadd').open=true;caH.value=0;caM.value=5"); x.ev("document.querySelector('[data-cago]').click()"); x.run(800)
        rb = x.ev(SZ + "('#calday .crow button')"); x.ev("document.querySelector('#calday [data-cnts]').click()"); x.run(300)
        ne = x.ev(SZ + "('#calday .cedit button')"); x.clk('[data-cre="0"]'); ed = x.ev(SZ + "('#calday .cedit button')")
        small = [z for z in rb + ne + ed if z[1] < 44 or z[2] < 44]
        ok(rb and ne and ed and not small, f'L9 {wv} 달력 줄·± 줄·✎ 줄 버튼 44px — 작은 것 {small}')
        x.ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
