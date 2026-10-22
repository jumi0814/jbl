"""UX26 탭 간 연계(10-22 사용자 "강의 자료를 보다가 기출을 보다가 기출에 해당하는 넘버링으로 가고 싶으면 다 홈페이지로 나가서 다시 넘버링으로 가야 되고 … 각종 탭들의 구조도 마음에 안 들고 탭 간의 연계도 잘 안 돼 있는 것 같아")
- JB 카드마다 '✎ 넘버링'(한 카드에 하나 — 답 아래 채점 줄엔 없음) → 내 넘버링 그 문제(없으면 하나 넣고) · 그 문제가 보이고 반짝 · ↩ 알약 → JB 그 자리
- 예상 카드 '✎ 넘버링' → 예상문제가 넘버링에 들어감
- 강의 탭 막대 '✎ 넘버링' → 내 넘버링(문제가 없으면 '이 강의 문제 불러오기' 알림) · ↩ 알약 = 강의
- 과목 메뉴 '✎ 넘버링' → 이 과목 넘버링 · 넘버링 사이드바 'JBL 이 과목' JB 문제·강의 ▾ → JBL(↩ = 넘버링)
- 넘버링 JB 문제에도 '정리본' 단추 · 바로 가기(Ctrl+K): '접착 예상' → 강의 예상 탭 · Esc 닫기 · pageerror 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CLEAR = "(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()"
PILL = "(()=>{const p=document.getElementById('retpill');return [p.classList.contains('on'),getComputedStyle(p).display,p.textContent]})()"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1300, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(J.HUB_URL + '#/'); pg.wait_for_timeout(2500); pg.evaluate(CLEAR)
    # JB 카드 → 넘버링
    pg.evaluate("location.hash='#/CONS/_jb'"); pg.wait_for_timeout(2500)
    n = pg.evaluate("[document.querySelectorAll('#stage article.qc').length,document.querySelectorAll('#stage article.qc .nmgo').length,document.querySelectorAll('#stage .acts2 .nmgo').length]")
    ok(n[0] > 30 and n[0] == n[1] and n[2] == 0, f"JB 카드마다 '✎ 넘버링' 하나 {n}")
    pg.evaluate("document.querySelectorAll('#stage article.qc')[2].scrollIntoView({block:'center'})"); pg.wait_for_timeout(400)
    aid = pg.evaluate("document.querySelectorAll('#stage article.qc')[2].dataset.aid")
    y0 = pg.evaluate("Math.round(document.querySelectorAll('#stage article.qc')[2].getBoundingClientRect().top)")
    pg.evaluate("document.querySelectorAll('#stage article.qc')[2].querySelector('.nmgo').click()"); pg.wait_for_timeout(3500)
    it = pg.evaluate(f"(()=>{{const S=JBLNUM._S;const it=S.items.find(i=>!i.del&&(i.src||[]).some(s=>s.t==='jb'&&s.id==={aid!r}));if(!it)return null;const a=document.querySelector('.nm-it[data-id=\"'+CSS.escape(it.id)+'\"]');if(!a)return [it.id,null];const r=a.getBoundingClientRect();return [it.id,Math.round(r.top),r.top>=0&&r.top<innerHeight-100]}})()")
    pl = pg.evaluate(PILL)
    ok(pg.evaluate('location.hash') == '#/_num/CONS' and it and it[2], f"JB '✎ 넘버링' → 내 넘버링 그 문제(넣고 · 보임) {it}")
    ok(pl[0] and pl[1] != 'none' and 'JB' in pl[2], f"넘버링 화면에 ↩ 알약 {pl}")
    pg.click('#retpill'); pg.wait_for_timeout(2500)
    y1 = pg.evaluate(f"(()=>{{const c=[...document.querySelectorAll('#stage article.qc')].find(x=>x.dataset.aid==={aid!r});return c?Math.round(c.getBoundingClientRect().top):null}})()")
    ok(pg.evaluate('location.hash').startswith('#/CONS/_jb') and y1 is not None and 0 <= y1 < 900, f"↩ 알약 → JB 그 문제 자리({y0}→{y1})")
    # 다시 누르면 같은 문제(새로 넣지 않음)
    pg.evaluate(f"[...document.querySelectorAll('#stage article.qc')].find(x=>x.dataset.aid==={aid!r}).querySelector('.nmgo').click()"); pg.wait_for_timeout(3000)
    c2 = pg.evaluate(f"JBLNUM._S.items.filter(i=>!i.del&&(i.src||[]).some(s=>s.id==={aid!r})).length")
    ok(c2 == 1, f"두 번 눌러도 넘버링에 하나 {c2}")
    jl = pg.evaluate("[...document.querySelectorAll('.nm-it')].filter(a=>a.dataset.id.startsWith('jb:')).map(a=>!!a.querySelector('[data-act=lecgo]'))")
    ok(jl and all(jl), f"넘버링 JB 문제에도 '정리본' 단추 {jl}")
    # 넘버링 사이드바 'JBL 이 과목'
    pg.click('.nm-jbl [data-jbl=_jb]'); pg.wait_for_timeout(2500)
    ok(pg.evaluate('location.hash').startswith('#/CONS/_jb') and '넘버링' in pg.evaluate(PILL)[2], f"넘버링 'JBL 이 과목' JB 문제 → JB · ↩ 넘버링 {pg.evaluate(PILL)[2]}")
    pg.click('#retpill'); pg.wait_for_timeout(2500)
    pg.click('.nm-jbl [data-jbl=lec]'); pg.wait_for_timeout(400)
    lm = pg.evaluate("[...document.querySelectorAll('.nm-menu [data-mi]')].map(b=>b.textContent)")
    ok(len(lm) >= 7 and all(' - ' in x for x in lm), f"'강의 ▾' = 교수 - 강의 제목 {lm[:2]}")
    pg.click('.nm-menu [data-mi]'); pg.wait_for_timeout(2500)
    ok(pg.evaluate('location.hash').endswith('/learn'), f"강의 고르기 → 학습 탭 {pg.evaluate('location.hash')}")
    # 강의 탭 막대 '✎ 넘버링'
    pg.evaluate("location.hash='#/CONS/ADH/learn'"); pg.wait_for_timeout(2500)
    ok(pg.evaluate("!!document.querySelector('#dtabs .dtnm')"), "강의 탭 막대에 '✎ 넘버링'")
    pg.click('#dtabs .dtnm'); pg.wait_for_timeout(3000)
    ok(pg.evaluate('location.hash') == '#/_num/CONS' and 'Dental Adhesive' in pg.evaluate(PILL)[2], f"강의 탭 '✎ 넘버링' → 넘버링 · ↩ 강의 {pg.evaluate(PILL)[2][:40]}")
    pg.click('#retpill'); pg.wait_for_timeout(2500)
    ok(pg.evaluate('location.hash').startswith('#/CONS/ADH/learn'), f"↩ → 강의 {pg.evaluate('location.hash')}")
    # 예상 카드
    pg.evaluate("location.hash='#/CONS/ADH/pred'"); pg.wait_for_timeout(2500)
    pa = pg.evaluate("document.querySelector('#stage article.pc').dataset.aid")
    pg.evaluate("document.querySelector('#stage article.pc .nmgo').click()"); pg.wait_for_timeout(3000)
    ok(pg.evaluate(f"JBLNUM._S.items.some(i=>!i.del&&(i.src||[]).some(s=>s.t==='pred'&&s.id==={pa!r}))"), "예상 '✎ 넘버링' → 예상문제가 넘버링에")
    # 과목 메뉴 '✎ 넘버링'
    pg.evaluate("location.hash='#/CONS/_home'"); pg.wait_for_timeout(2500)
    ok(pg.evaluate("document.querySelectorAll('#nav .nvgrid .nvd').length>=8&&!!document.querySelector('#nav [data-nvnum]')"), "과목 메뉴에 '✎ 넘버링'")
    pg.click('#nav [data-nvnum]'); pg.wait_for_timeout(3000)
    ok(pg.evaluate('location.hash') == '#/_num/CONS', f"과목 메뉴 '✎ 넘버링' → 이 과목 넘버링 {pg.evaluate('location.hash')}")
    # 바로 가기
    pg.evaluate("location.hash='#/CONS/ADH/learn'"); pg.wait_for_timeout(2500)
    pg.keyboard.press('Control+k'); pg.wait_for_timeout(300)
    ok(pg.evaluate("!document.getElementById('qj').hidden && document.activeElement.id==='qjq'"), "Ctrl+K → 바로 가기 창(입력칸에 커서)")
    pg.keyboard.type('접착 예상'); pg.wait_for_timeout(300)
    first = pg.evaluate("(document.querySelector('#qjl .qjo.on .t')||{}).textContent||''")
    pg.keyboard.press('Enter'); pg.wait_for_timeout(2000)
    ok(pg.evaluate('location.hash').startswith('#/CONS/ADH/pred'), f"'접착 예상' Enter → 강의 예상 탭 ({first[:40]})")
    pg.keyboard.press('Control+k'); pg.wait_for_timeout(200); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(pg.evaluate("document.getElementById('qj').hidden"), "Esc → 닫힘")
    pg.click('#qjb'); pg.wait_for_timeout(200)
    ok(pg.evaluate("!document.getElementById('qj').hidden"), "위 막대 '바로 가기' 단추 → 창")
    pg.keyboard.press('Escape')
    ok(not errs, f"pageerror 0 {errs[:3]}")
    pg.evaluate(CLEAR); b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
