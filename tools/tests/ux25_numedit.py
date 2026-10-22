"""UX25 강의 이름·넘버링 편집(10-22 사용자 "나의 넘버링 따기 및 강의자료 정리본에서 왼쪽 메뉴탭, 넘버링 따기에서 기존 문제 가져오기할 때 강의자료 선택 버튼 등등에 강의자료 이름이 아니라 교수님 이름 - 강의 제목 … 넘버링 따기에서 문제랑 답안도 굳이 수정 안 눌러도 클릭만 해도 바로 수정 … 갑자기 글머리 기호 붙는 경우 … 글머리 기호 사용 시 갑자기 줄바꿈 되어서 줄간격 생기는 현상 … 글씨 조그만 서식창에 글머리 기호랑 숫자 기호 … 사진 크기 비율 유지되돼 그냥 크기만 조정")
- JBL 왼쪽 메뉴 강의 줄 = '교수 - 강의 제목' · 내 넘버링 사이드바 강의 · 불러오기 강의 고르기 = '교수 - 강의 제목'
- 문제·답 칸을 누르면 바로 편집(수정 단추 없이) · 미니 서식창에 글머리 기호·번호 목록 단추 → 누르면 목록
- 목록 줄(li) 줄바꿈 글자로 줄 간격이 생기지 않음(white-space normal · li 안 문단 여백 0) · JBL ' · ' 한 줄 목록(kflow)은 문단으로(글머리 기호 안 붙음)
- 편집 중 그림을 누르면 크기 손잡이 → 끌면 너비만 바뀌고 비율 그대로 · 저장 · pageerror 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CLEAR = "(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()"
PNG = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAABkCAIAAABM5OhcAAAAh0lEQVR4nO3BAQ0AAADCoPdPbQ8HFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPwGCMQAAa0X4YIAAAAASUVORK5CYII='
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1300, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(J.HUB_URL + '#/IMPL/_home'); pg.wait_for_timeout(3500); pg.evaluate(CLEAR)
    nav = pg.evaluate("[...document.querySelectorAll('#nav .ni.nvl .el')].map(e=>e.textContent.trim())")
    want = pg.evaluate("__h.PACKS.IMPL.lect.map(L=>String(L.prof||'').split('(')[0].trim()+' - ')")
    ok(len(nav) >= 7 and all(n.replace('★', '').startswith(w) for n, w in zip(nav, want)), f"JBL 왼쪽 메뉴 강의 = '교수 - 제목' {nav[:3]}")
    pg.evaluate("location.hash='#/_num/IMPL'"); pg.wait_for_timeout(3000)
    pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); pg.wait_for_timeout(800)
    opts = pg.evaluate("[...document.querySelectorAll('[data-if=lec] option')].slice(1).map(o=>o.textContent)")
    ok(opts and all(' - ' in o for o in opts), f"불러오기 강의 고르기 = '교수 - 제목' {opts[:2]}")
    pg.select_option('[data-if=ty]', ''); pg.wait_for_timeout(300)
    pg.click('[data-ib=all]'); pg.wait_for_timeout(500); pg.click('[data-cf2=ok]'); pg.wait_for_timeout(1500); pg.click('.nm-ov [data-x]'); pg.wait_for_timeout(800)
    side = pg.evaluate("[...document.querySelectorAll('.nm-lj .l')].map(e=>e.textContent)")
    ok(side and sum(' - ' in x for x in side) >= len(side) - 1, f"내 넘버링 사이드바 강의 = '교수 - 제목' {side[:2]}")
    # 클릭 바로 편집 — 답
    aid = pg.evaluate("(()=>{const a=[...document.querySelectorAll('.nm-it')].find(x=>{const c=x.querySelector('.nm-a .nm-c');return c&&c.textContent.trim().length>20});a.scrollIntoView({block:'center'});return a.dataset.id})()")
    pg.wait_for_timeout(300); pg.click(f'.nm-it[data-id="{aid}"] .nm-a .nm-c[data-f=a]', position={'x': 20, 'y': 8}); pg.wait_for_timeout(400)
    ed = pg.evaluate(f"(()=>{{const c=document.querySelector('.nm-it[data-id=\"{aid}\"] .nm-a .nm-c[data-f=a]');return [c.getAttribute('contenteditable'),!!document.querySelector('.nm-tb [data-cmd=insertUnorderedList]'),!!document.querySelector('.nm-tb [data-cmd=insertOrderedList]')]}})()")
    ok(ed[0] == 'true', f"답 칸 누르기 = 바로 편집 ({ed[0]})")
    ok(ed[1] and ed[2], f"미니 서식창에 글머리 기호·번호 목록 단추 {ed[1:]}")
    pg.keyboard.press('End'); pg.keyboard.press('Enter'); pg.keyboard.type('새 줄 하나')
    pg.click('.nm-tb [data-cmd=insertUnorderedList]'); pg.wait_for_timeout(300)
    li = pg.evaluate(f"(()=>{{const c=document.querySelector('.nm-it[data-id=\"{aid}\"] .nm-a .nm-c[data-f=a]'),l=[...c.querySelectorAll('li')].pop();if(!l)return null;const cs=getComputedStyle(l),lh=parseFloat(getComputedStyle(c).lineHeight)||20;return [cs.whiteSpace,Math.round(l.getBoundingClientRect().height),Math.round(lh)]}})()")
    ok(li and li[0] == 'normal' and li[1] <= li[2] * 1.6, f"글머리 기호 누르면 목록 · 줄 간격 안 생김(white-space {li and li[0]} · 높이 {li and li[1]} ≤ 줄 {li and li[2]}×1.6)")
    # 그림 크기 조절
    pg.evaluate(f"document.execCommand('insertHTML',false,'<img src=\"{PNG}\" width=\"200\" height=\"100\" alt=\"\">')"); pg.wait_for_timeout(400)
    box = pg.evaluate(f"(()=>{{const im=[...document.querySelectorAll('.nm-it[data-id=\"{aid}\"] .nm-a .nm-c img')].pop();im.scrollIntoView({{block:'center'}});const r=im.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2,r.width]}})()")
    pg.mouse.click(box[0], box[1]); pg.wait_for_timeout(300)
    h = pg.evaluate("(()=>{const h=document.querySelector('.nm-irh');if(!h)return null;const r=h.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()")
    ok(h is not None, "편집 중 그림 누르기 = 크기 손잡이")
    if h:
        pg.mouse.move(h[0], h[1]); pg.mouse.down(); pg.mouse.move(h[0] - 80, h[1] + 30, steps=6); pg.mouse.up(); pg.wait_for_timeout(300)
        wh = pg.evaluate(f"(()=>{{const im=[...document.querySelectorAll('.nm-it[data-id=\"{aid}\"] .nm-a .nm-c img')].pop();const r=im.getBoundingClientRect();return [+im.getAttribute('width'),+im.getAttribute('height'),Math.round(r.width),Math.round(r.height)]}})()")
        ok(wh[0] < 200 and abs(wh[1] / wh[0] - 0.5) < 0.03 and abs(wh[3] / wh[2] - 0.5) < 0.05, f"끌면 너비만 줄고 비율 그대로(1:2) {wh}")
    pg.keyboard.press('Escape'); pg.wait_for_timeout(1200)
    st = pg.evaluate(f"(()=>{{const it=JBLNUM._S.by.get('{aid}');const m=/<img[^>]*width=\"(\\d+)\"[^>]*height=\"(\\d+)\"/.exec(it.a);return [/<ul>/.test(it.a),m?[+m[1],+m[2]]:null]}})()")
    ok(st[0] and st[1] and st[1][0] < 200 and abs(st[1][1] / st[1][0] - 0.5) < 0.03, f"저장 — 목록·그림 크기(비율 그대로) {st}")
    # 문제 칸도 누르면 바로 편집
    q = pg.evaluate("(()=>{const a=document.querySelectorAll('.nm-it')[2];a.scrollIntoView({block:'center'});return a.dataset.id})()"); pg.wait_for_timeout(300)
    pg.click(f'.nm-it[data-id="{q}"] .nm-q .nm-c[data-f=q]', position={'x': 30, 'y': 8}); pg.wait_for_timeout(400)
    ok(pg.evaluate(f"document.querySelector('.nm-it[data-id=\"{q}\"] .nm-q .nm-c[data-f=q]').getAttribute('contenteditable')") == 'true', "문제 칸 누르기 = 바로 편집")
    pg.keyboard.press('Escape'); pg.wait_for_timeout(600)
    kf = pg.evaluate("JBLNUM._sanitize('<ul class=\"kflow\"><li>Prevention</li><li>Intervention</li></ul><ul class=\"klist\"><li>가</li></ul>')")
    ok(kf.startswith('<p>Prevention · Intervention</p>') and '<ul><li>가</li></ul>' in kf, f"JBL 한 줄 목록(kflow) = 문단 · 원래 글머리 기호 목록은 그대로 {kf[:80]}")
    ok(not errs, f"pageerror 0 {errs[:3]}")
    pg.evaluate(CLEAR); b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
