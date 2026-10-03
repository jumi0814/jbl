"""ux4f Q 회귀 — 사용자 10-03 추가 요청
Q1 '공부시간 리셋 타임은 매일 아침 6시 … 새벽12~아침 6시 전까지는 전날의 공부시간에' — 공부 날 경계 06:00(DCUT 2026-10-04부터 — 그 전 날은 자정 그대로 · DCUT 날은 자정~다음 날 6시)
   · 새벽 3시 공부 = 전날 · 아침 7시 공부 = 그날 · 달력 구간 시각은 실제 시각(03:00대) · 옛 날(09-28)은 자정 기준 그대로
Q2 '자동측정에서 공부 시간측정 재개는 내가 스크롤 또는 클릭을 하면서 시작' — 마우스만 움직이면 시작·재개 안 함 · 휠(스크롤)·클릭이면 시작 · 자동 휴식도 마우스 움직임으로는 안 끝남
Q3 '각 카드 상단에 기출문제 연도 클릭하면 jb창으로 바로 가는게 아니라 Jb 미리보기 … 문제 및 선지는 생략 없이 … 답도 … 생략없이' — 카드 머리 연도 칩 = 미리보기(화면 그대로) · 문제 줄 전부·'이하 JB에서' 없음 · 답 줄 전부(해설·참고 줄 없음) · [JB에서 풀기] = 그 문항"""
import os as _os, sys as _sys, json, datetime, re; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []; MIN = 60000
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
def boot(pg, h, ms=1500):
    pg.goto('about:blank'); pg.goto(U + h); pg.clock.run_for(ms)
    for _ in range(150):
        if pg.evaluate("!!(window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni'))"): break
        pg.wait_for_timeout(100); pg.clock.run_for(100)
def study(pg, minutes):
    for i in range(minutes * 2):
        pg.mouse.wheel(0, 120 if i % 2 else -120); pg.clock.run_for(30000)
def tday(pg, d): return sum(pg.evaluate(f"__h.tDay('{d}')").values())
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------- Q1 ----------
    for start, want, other, hm in [((2026, 10, 10, 3, 0), '2026-10-09', '2026-10-10', '03:0'), ((2026, 10, 10, 7, 0), '2026-10-10', '2026-10-09', '07:0'),
                                   ((2026, 10, 5, 3, 0), '2026-10-04', '2026-10-05', '03:0'), ((2026, 9, 28, 3, 0), '2026-09-28', '2026-09-27', '03:0')]:
        ctx = b.new_context(viewport={'width': 1280, 'height': 900}); pg = ctx.new_page(); E = []
        pg.on('pageerror', lambda e: E.append(str(e)[:200]))
        pg.clock.install(time=datetime.datetime(*start))
        boot(pg, '#/'); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); boot(pg, '#/CONS/WHT/learn')
        pg.mouse.move(500, 400); study(pg, 10)
        a, o = tday(pg, want), tday(pg, other)
        ok(9 * MIN <= a <= 11.5 * MIN and o == 0, f"Q1 {start[1]:02d}-{start[2]:02d} {start[3]:02d}:00 공부 10분 → {want} {a / MIN:.1f}분 · {other} {o / MIN:.1f}분")
        pg.evaluate("__h.trStop&&__h.trStop()"); pg.clock.run_for(1500)
        boot(pg, '#/_cal/' + want, 1500)
        rows = pg.evaluate("[...document.querySelectorAll('.crows .crow .ctm')].map(e=>e.textContent)")
        ok(any(r.startswith(hm) for r in rows), f'Q1 {want} 달력 구간 시각 = 실제 시각 {rows[:3]}')
        ok(not E, f'Q1 콘솔 오류 없음 {E[:2]}'); ctx.close()
    # ---------- Q2 ----------
    for W, H, T in [(1280, 900, False), (820, 1180, True)]:
        ctx = b.new_context(viewport={'width': W, 'height': H}, has_touch=T); pg = ctx.new_page(); E = []
        pg.on('pageerror', lambda e: E.append(str(e)[:200]))
        pg.clock.install(time=datetime.datetime(2026, 10, 12, 14, 0))
        boot(pg, '#/'); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); boot(pg, '#/CONS/WHT/learn')
        for i in range(6): pg.mouse.move(300 + i * 40, 400 + i * 5); pg.clock.run_for(500)
        s0 = pg.evaluate("__h.trState()")
        if T: pg.touchscreen.tap(W // 2, H // 2 + 100)
        else: pg.mouse.wheel(0, 200)
        pg.clock.run_for(500); s1 = pg.evaluate("__h.trState()")
        ok(s0 == 'wait' and s1 == 'run', f'Q2 {W} 마우스만 움직임 → {s0} · {"손가락" if T else "휠"} → {s1}')
        pg.clock.run_for(10 * MIN); ts = pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.tstate')||'null')")
        ok(ts and ts.get('st') == 'rest', f'Q2 {W} 무입력 10분 → 자동 휴식 {ts and ts.get("st")}')
        for i in range(5): pg.mouse.move(600 + i * 30, 300); pg.clock.run_for(400)
        ok(pg.evaluate("__h.trState()") == 'rest', f'Q2 {W} 자동 휴식 중 마우스만 움직임 → 휴식 그대로')
        if T: pg.touchscreen.tap(W // 2, H // 2 + 150)
        else: pg.mouse.click(W // 2, 300)
        pg.clock.run_for(600)
        ok(pg.evaluate("__h.trState()") == 'run', f'Q2 {W} {"손가락" if T else "클릭"} → 다시 잼 {pg.evaluate("__h.trState()")}')
        ok(not E, f'Q2 {W} 콘솔 오류 없음 {E[:2]}'); ctx.close()
    # ---------- Q3 ----------
    for W, H, T in [(1280, 900, False), (820, 1180, True)]:
        ctx = b.new_context(viewport={'width': W, 'height': H}, has_touch=T); pg = ctx.new_page(); E = []
        pg.on('pageerror', lambda e: E.append(str(e)[:200]))
        pg.goto(U + '#/'); pg.wait_for_function(WAIT, timeout=60000); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')")
        for route in ['#/ESTH/COL/learn', '#/OMS1/DD1/learn', '#/PHARM/HM/learn']:
            pg.goto('about:blank'); pg.goto(U + route); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1200)
            # 문제 줄이 가장 많은 카드의 연도 칩
            info = pg.evaluate("""(()=>{const P=__h.PACKS[__h.CUR.s];let best=null;for(const b of document.querySelectorAll('#stage .tchips .chip.yr[data-go]')){const h=P.cards[b.dataset.go];if(!h)continue;const d=document.createElement('div');d.innerHTML=h;const n=d.querySelectorAll('.qtext .ln').length;
              const a=d.querySelector('.jbans .lines');let na=0,tx='';if(a)for(const ln of a.children){if(ln.matches('.lab-e,.lab-r'))break;if(ln.matches('.exw')){if(/해설\s*참고|해설 ?참조/.test(tx))na++;break;}tx+=ln.textContent;na++;}if(!best||n>best[1])best=[b,n,na,b.dataset.go];}if(!best)return null;best[0].id='qchip';best[0].scrollIntoView({block:'center'});return best.slice(1)})()""")
            if not info: ok(False, f'Q3 {W} {route} 연도 칩 없음'); continue
            h0 = pg.evaluate("location.hash"); pg.wait_for_timeout(300)
            box = pg.evaluate("(e=>{const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})(document.querySelector('#qchip'))")
            (pg.touchscreen.tap if T else pg.mouse.click)(box[0], box[1]); pg.wait_for_timeout(500)
            r = pg.evaluate("(p=>p?[p.classList.contains('on'),p.querySelectorAll('.jpq .ln').length,!!p.querySelector('.jpmore'),location.hash]:null)(document.querySelector('#jbpeek'))")
            ok(r and r[0] and r[1] == info[0] and not r[2] and r[3] == h0, f'Q3 {W} {route} 연도 칩 → 미리보기 · 문제 줄 {r and r[1]}/{info[0]} 전부 · 화면 그대로')
            pg.evaluate("document.querySelector('#jbpeek .jpshow').click()"); pg.wait_for_timeout(200)
            a = pg.evaluate("(p=>[!p.hidden,p.querySelectorAll(':scope>.ln,:scope>.exw').length,p.querySelectorAll(':scope>.lab-r,:scope>.ln.lab-e').length,p.querySelectorAll('.clamp').length])(document.querySelector('#jbpeek .jpa'))")
            ok(a[0] and a[1] == info[1] and a[2] == 0 and a[3] == 0, f'Q3 {W} {route} 답 보기 → 답 줄 {a[1]}/{info[1]} 전부(답이 \'해설 참고\'면 해설 펼쳐서) · 참고 줄 없음 · 접힘 없음')
            pg.evaluate("document.querySelector('#jbpeek [data-jpgo]').click()"); pg.wait_for_timeout(900)
            ok(pg.evaluate(f"location.hash.indexOf('/_jb')>0||location.hash.indexOf('/jb')>0") and pg.evaluate(f"!!document.querySelector('#c-{info[2]}')"), f'Q3 {W} {route} [JB에서 풀기] → 그 문항 {info[2]}')
        ok(not E, f'Q3 {W} 콘솔 오류 없음 {E[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
