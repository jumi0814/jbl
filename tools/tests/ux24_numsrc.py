"""UX24 넘버링 가져오기·인쇄·정리본 바로가기(10-22 사용자 "넘버링 따기에서 내가 기출 문제 가져올 떄는 기본적으로는 각 교수님별로 출제연도 순으로 정렬해주면 좋겠고, 프린트할 때 제목은 과목 이름 넘버링 - madeby쭘 … 오른쪽 위에는 총 문제수 및 (기출은 모조리 다 연도표기 함 / 연도 표기 X = 예상문제) … 넘버링 스토리랑 답안이라고 상자 안에 표시 없애주면 … 예상문제 가져올 때 … 어디 피피티 몇페이지 이런 표시는 완전 필요없어! … 예상문제도 해당 예상문제를 출제한 강의자료 정리본 카드로 바로가는 버튼이 있고, 다시 돌아올 수 있었으면 … 각 강의자료정리본의 예상문제란에서도")
- 불러오기 기본 정렬 = 교수별 · 최근 출제 순(같은 교수 JB가 이어지고, 그 안에서 최근 출제 해가 내려감) · 넣는 순서도 같음
- 예상문제 문제·답에 강의자료 쪽 표시(p.N · 슬라이드 N · 인용 칩) 없음 · 이미 가져온 예상문제도 다시 열면 지워짐('26 필기' 같은 말은 남음)
- 예상문제 '정리본' 단추 → 그 정리본 카드(학습 탭) + ↩ 알약 → 내 넘버링 그 문제로 · 예상 탭 카드 '📖 정리본' → 카드 + ↩ 알약 → 예상 탭
- 인쇄 머리 '<과목> 넘버링 - madeby쭘' · '총 n문제 (기출은 모조리 다 연도표기 함 / 연도 표기 X = 예상문제)' · 상자 안 '답안'·'넘버링 스토리' 없음 · pageerror 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CLEAR = "(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()"
PAGE = r"/(?<![A-Za-z])p\.\s*\d|슬라이드\s*\d/"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1300, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(J.HUB_URL + '#/'); pg.wait_for_timeout(2500); pg.evaluate(CLEAR)
    pg.evaluate("location.hash='#/_num/CONS'"); pg.wait_for_timeout(3000)
    pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); pg.wait_for_timeout(800)
    so = pg.evaluate("document.querySelector('[data-if=so]').value"); ok(so == 'prof', f"불러오기 기본 정렬 = 교수별 · 최근 출제 순 ({so})")
    pg.select_option('[data-if=ty]', ''); pg.select_option('[data-if=src]', 'jb'); pg.wait_for_timeout(400)
    seq = pg.evaluate("""(()=>{const L=JBLNUM._jbList('CONS'),m=new Map(L.map(x=>[x.id,x]));return [...document.querySelectorAll('.nm-irow')].map(r=>{const x=m.get(r.dataset.ix);return [x.prof,Math.max(0,...x.yrs)]})})()""")
    seen, bad, prev = [], 0, None
    for pr, y in seq:
        if not seen or seen[-1] != pr:
            if pr in seen: bad += 1
            seen.append(pr); prev = None
        if prev is not None and y > prev: bad += 1
        prev = y
    ok(len(seq) > 30 and bad == 0, f"JB {len(seq)}문제 — 교수별로 이어짐 · 그 안에서 최근 출제 해 내림차순(어긋남 {bad}) · 교수 순 {seen}")
    pg.select_option('[data-if=src]', ''); pg.wait_for_timeout(300)
    pg.click('[data-ib=all]'); pg.wait_for_timeout(500); pg.click('[data-cf2=ok]'); pg.wait_for_timeout(1500); pg.click('.nm-ov [data-x]'); pg.wait_for_timeout(800)
    pr = pg.evaluate(f"""(()=>{{const S=JBLNUM._S,P=S.items.filter(i=>!i.del&&i.kind==='pred');return [P.length,P.filter(i=>{PAGE}.test(JBLNUM._plain(i.q)+' '+JBLNUM._plain(i.a))).map(i=>JBLNUM._plain(i.a).match(/.{{0,20}}(p\\.\\s*\\d|슬라이드\\s*\\d).{{0,10}}/)[0]).slice(0,4),P.filter(i=>/필기/.test(JBLNUM._plain(i.a))).length]}})()""")
    ok(pr[0] > 50 and not pr[1], f"예상문제 {pr[0]}개 — 문제·답에 쪽 표시 없음 {pr[1]} · '필기' 말은 남음 {pr[2]}")
    o = pg.evaluate("(()=>{const S=JBLNUM._S;const L=S.items.filter(i=>!i.del&&i.kind==='jb').sort((a,b)=>a.o-b.o);return L.slice(0,6).map(i=>[(i.src[0]||{}).lab,Math.max(0,...i.yrs)])})()")
    ok(len(o) == 6 and all(o[i][1] >= o[i + 1][1] for i in range(5) if o[i][0] == o[i + 1][0]), f"넣은 순서도 교수별 · 최근 출제 순 {o[:4]}")
    # 이미 가져온 예상문제(옛 글자) → 다시 열면 지워짐
    pid = pg.evaluate("""(()=>{const S=JBLNUM._S,it=S.items.find(i=>!i.del&&i.kind==='pred');it.a=it.a+'<p>옛 꼬리 Tooth whitening(26·25) p.31 · (슬라이드 36) · 26 필기(p.12): 남는 말</p>';JBLNUM._put(it);return it.id;})()""")
    pg.evaluate("location.hash='#/'"); pg.wait_for_timeout(600); pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("location.hash='#/_num/CONS'"); pg.wait_for_timeout(3000)
    a2 = pg.evaluate(f"JBLNUM._plain(JBLNUM._S.by.get({pid!r}).a)")
    ok('p.31' not in a2 and '슬라이드 36' not in a2 and 'p.12' not in a2 and '26 필기' in a2 and '남는 말' in a2, f"이미 가져온 예상문제도 다시 열면 쪽 표시만 지워짐 — '…{a2[-40:]}'")
    # 예상문제 '정리본' 단추
    btn = pg.evaluate("(()=>{const a=[...document.querySelectorAll('.nm-it')].find(x=>x.querySelector('[data-act=lecgo]'));if(!a)return null;a.scrollIntoView({block:'center'});return [a.dataset.id,(a.querySelector('.nm-no')||{}).textContent];})()")
    ok(btn is not None, f"예상문제 머리에 '정리본' 단추 {btn}")
    if btn:
        y0 = pg.evaluate(f"Math.round(document.querySelector('.nm-it[data-id=\"{btn[0]}\"]').getBoundingClientRect().top)")
        pg.click(f'.nm-it[data-id="{btn[0]}"] [data-act=lecgo]'); pg.wait_for_timeout(2500)
        v = pg.evaluate("(()=>{const P=document.getElementById('retpill');const m=/^#\\/CONS\\/([A-Z0-9]+)\\/learn/.exec(location.hash);const c=[...document.querySelectorAll('#stage [id^=\"t-\"]')].find(e=>{const r=e.getBoundingClientRect();return r.top<innerHeight*0.6&&r.bottom>60;});return {h:location.hash,lec:!!m,card:c?c.id:null,pill:P.classList.contains('on'),pt:P.textContent}})()")
        ok(v['lec'] and v['card'] and v['pill'] and '내 넘버링' in v['pt'], f"정리본 단추 → 학습 탭 그 카드 {v['h']} {v['card']} · 알약 '{v['pt'].strip()[:30]}'")
        pg.click('#retpill'); pg.wait_for_timeout(2500)
        y1 = pg.evaluate(f"(()=>{{const a=document.querySelector('.nm-it[data-id=\"{btn[0]}\"]');return a?Math.round(a.getBoundingClientRect().top):null}})()")
        ok(pg.evaluate("location.hash") == '#/_num/CONS' and y1 is not None and abs(y1 - y0) <= 40, f"↩ 알약 = 내 넘버링 그 문제 자리로({y0}→{y1})")
    # 인쇄 머리
    ph = pg.evaluate("(()=>{const S=JBLNUM._S,L=S.items.filter(i=>!i.del).slice(0,5);return JBLNUM._printHTML(L,{what:'qas',lay:'side'},'전체')})()")
    ok('임상치과보존학 넘버링 - madeby쭘' in ph and '총 5문제 (기출은 모조리 다 연도표기 함 / 연도 표기 X = 예상문제)' in ph and 'np-l' not in ph, "인쇄 머리 '임상치과보존학 넘버링 - madeby쭘' · '총 5문제 (…)' · 상자 안 라벨 없음")
    # 예상 탭 '📖 정리본'
    pg.evaluate("location.hash='#/CONS/WHT/pred'"); pg.wait_for_timeout(2500)
    n = pg.evaluate("[document.querySelectorAll('#stage .pc').length,document.querySelectorAll('#stage .pc .chip.plc').length]")
    ok(n[0] > 0 and n[0] == n[1], f"예상 탭 카드마다 '📖 정리본' {n[1]}/{n[0]}")
    pg.evaluate("document.querySelector('#stage .pc .chip.plc').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
    pg.click('#stage .pc .chip.plc'); pg.wait_for_timeout(2500)
    v2 = pg.evaluate("(()=>{const P=document.getElementById('retpill');return {h:location.hash,pill:P.classList.contains('on')}})()")
    ok('/learn' in v2['h'] and v2['pill'], f"예상 탭 '📖 정리본' → 학습 탭 · 알약 {v2}")
    pg.click('#retpill'); pg.wait_for_timeout(2000)
    ok(pg.evaluate("location.hash").endswith('/pred'), f"↩ 알약 = 예상 탭으로 {pg.evaluate('location.hash')}")
    ok(not errs, f"pageerror 0 {errs[:3]}")
    pg.evaluate(CLEAR); b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
