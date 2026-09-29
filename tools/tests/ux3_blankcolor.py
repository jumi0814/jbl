"""ux3 트랙3 묶음 K2~K6 회귀: 빈칸 5색(n 회색·u 파랑·g 초록·p 분홍·v 보라)
저장·복원(초록 빈칸 → 새로고침 → rkb-g) · 회색 빈칸 JSON에 c 없음(1차 배포본 snap과 같은 글자 {t,x,i,p,s,v}) · 1차 배포본 허브로 열어도 오류 없이 빈칸(회색) ·
빈칸 모드에서 다른 색 빈칸 = 색만 바꿈 → ⌘Z 되돌림 · 같은 색 = 지움 · Shift+B 4번 → 보라(알림 4번) · 견본 색 기억(bcol)·형광펜 색 기억(hcol) ·
라벨(blabel — 견본 우클릭) = title·모드 칩 · 모드 칩 색 · 빈칸 모드 밖 우클릭(길게 누르기) 팝업으로 색 바꾸기 · ⚡ 자동 빈칸 창 색 칩(규칙·카드) ·
내 표시 모아보기 빈칸 색 필터 · 가린 빈칸 밑줄 대비 3.0↑(5색) · 인쇄 에뮬레이션 색 없음 · 좁은 화면 ▾ 팝업 빈칸 줄 · 콘솔 오류 0
맥 1280×900 · 아이패드 세로 820×1180·가로 1180×820(터치). 스크린샷 work/_tmp/ux3i_blank_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
OLD = 'file://' + _os.path.join(J.WORK, '_legacy', '7095e56', 'docs', 'index.html')
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1300, url=None):
    await pg.goto('about:blank'); await pg.goto((url or U) + h); await pg.wait_for_timeout(w)
NS = 'jblhub.v1.'
ANN = "JSON.parse(localStorage.getItem('jblhub.v1.ann.OMS1')||'{}')"
# n번째 카드 본문에서 블록 안에 한 번만 나오는 4글자↑ 낱말의 화면 좌표(스크롤해 보이게)
WORD = """([cid,k])=>{const c=document.querySelector('#'+cid);c.classList.add('open');const B=c;const T=__h.Kit.textOf(B);
 const els=[...c.querySelectorAll('.tbody .li, .tbody .und')].filter(e=>e.offsetParent&&!e.closest('.c-key'));let seen=0;
 for(const li of els){const w=document.createTreeWalker(li,NodeFilter.SHOW_TEXT);let t;while(t=w.nextNode()){if(t.parentElement.closest('button,.noann,[data-rk],.srt'))continue;const re=/[A-Za-z가-힣]{4,}/g;let m;
  while(m=re.exec(t.nodeValue)){if(T.split(m[0]).length!==2)continue;if(seen++<k)continue;li.scrollIntoView({block:'center'});const r=document.createRange();r.setStart(t,m.index+1);r.setEnd(t,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2,m[0]];}}}return null;}"""
BAT = "(w)=>{const e=[...document.querySelectorAll('#stage [data-rk=b]')].find(x=>x.textContent===w);return e?[e.className,e.dataset.bc]:null}"
BXY = "(w)=>{const e=[...document.querySelectorAll('#stage [data-rk=b]')].find(x=>x.textContent===w);e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}"
def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]; f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])
def cr(a, b): L1, L2 = lum(a), lum(b); return (max(L1, L2) + 0.05) / (min(L1, L2) + 0.05)
async def mac(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('dialog', lambda d: asyncio.ensure_future(d.accept('수치')))
    await open_(pg, '#/OMS1/DD1/learn'); await pg.evaluate("['ann.OMS1','bcol','hcol','blabel','autoRule.OMS1','mkcol'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k));sessionStorage.clear()")
    await open_(pg, '#/OMS1/DD1/learn')
    ok(await pg.evaluate("__h.Kit.bcolor()") == 'n', '처음 빈칸 색 = 회색(n)')
    # 1) 회색 빈칸 — JSON에 c 없음, 1차 배포본 snap과 같은 글자
    xy = await pg.evaluate(WORD, ['t-DD1-2', 0]); await pg.keyboard.press('b'); await pg.mouse.click(xy[0], xy[1]); await pg.wait_for_timeout(200)
    r = await pg.evaluate("""(w)=>{const A=JSON.parse(localStorage.getItem('jblhub.v1.ann.OMS1')||'{}');const B=document.querySelector('#t-DD1-2');const o=(A[B.dataset.aid]||[]).find(o=>o.x===w);if(!o)return null;
      const s=__h.Kit.textOf(B),a=s.indexOf(w),b=a+w.length,CTX=12;const old={t:'b',x:w,i:0,p:s.slice(Math.max(0,a-CTX),a),s:s.slice(b,b+CTX),v:__h.Kit.fnv(s)};return [JSON.stringify(o),JSON.stringify(old)]}""", xy[2])
    ok(r and r[0] == r[1] and '"c"' not in r[0], f'회색 빈칸 저장 JSON = 1차 배포본 snap 글자 그대로(c 없음) {r[0][:90] if r else r}')
    gw = xy[2]
    # 2) 견본에서 초록 → 빈칸 모드 · 새 빈칸 rkb-g · 저장 c:'g' · 새로고침 복원
    await pg.keyboard.press('Escape'); await pg.click('#k-bswc'); await pg.click('#k-bswl .bsw[data-bc="g"]'); await pg.wait_for_timeout(150)
    mb = await pg.evaluate("[__h.Kit.bcolor(),document.body.classList.contains('mode-b'),localStorage.getItem('jblhub.v1.bcol')]")
    ok(mb == ['g', True, '"g"'], f'견본 초록 → 빈칸 모드·bcol 저장 {mb}')
    chip = await pg.evaluate("[document.querySelectorAll('#modechip').length,document.querySelector('#k-b').classList.contains('on'),getComputedStyle(document.querySelector('#k-b')).getPropertyValue('--bcb').trim()]"); ok(chip[0] == 0 and chip[1] and chip[2].upper() == '#D3EBD9', f'ux4 B1-4 모드 칩 없이 ▣ 버튼 눌림 + 점 색 = 초록 {chip}')
    xy2 = await pg.evaluate(WORD, ['t-DD1-3', 0]); await pg.mouse.click(xy2[0], xy2[1]); await pg.wait_for_timeout(200)
    a = await pg.evaluate(BAT, xy2[2]); sv = await pg.evaluate(f"(w)=>Object.values({ANN}).flat().find(o=>o.x===w)", xy2[2])
    ok(a and 'rkb-g' in a[0] and a[1] == 'g' and sv and sv.get('c') == 'g', f'초록 빈칸 만들기 → {a} · 저장 {sv and {k: sv[k] for k in ("t", "c")}}')
    await pg.keyboard.press('Escape'); await pg.reload(); await pg.wait_for_timeout(1500)
    a2 = await pg.evaluate(BAT, xy2[2]); a3 = await pg.evaluate(BAT, gw)
    ok(a2 and 'rkb-g' in a2[0] and a3 and 'rkb-' not in a3[0] and a3[1] == 'n', f'새로고침 → 초록 복원 {a2} · 회색 그대로 {a3}')
    ok(await pg.evaluate("__h.Kit.bcolor()") == 'g', '새로고침 뒤 빈칸 색 기억(bcol)')
    await pg.screenshot(path=J.TMP + '/ux3i_blank_mac.png')
    # 3) 파랑 모드로 초록 빈칸 누르기 → 색만 바꿈 → ⌘Z 되돌림 → 같은 색 누르기 = 지움
    await pg.evaluate("__h.Kit.setBColor('u')"); await pg.keyboard.press('b')
    p_ = await pg.evaluate(BXY, xy2[2]); await pg.mouse.click(p_[0], p_[1]); await pg.wait_for_timeout(200)
    a4 = await pg.evaluate(BAT, xy2[2]); s4 = await pg.evaluate(f"(w)=>Object.values({ANN}).flat().find(o=>o.x===w)", xy2[2])
    ok(a4 and 'rkb-u' in a4[0] and s4 and s4.get('c') == 'u', f'파랑 모드로 초록 빈칸 → 파랑 {a4}')
    await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(250); a5 = await pg.evaluate(BAT, xy2[2])
    ok(a5 and 'rkb-g' in a5[0], f'Ctrl+Z → 다시 초록 {a5}')
    await pg.evaluate("__h.Kit.setBColor('g')"); p_ = await pg.evaluate(BXY, xy2[2]); await pg.mouse.click(p_[0], p_[1]); await pg.wait_for_timeout(200)
    ok(await pg.evaluate(BAT, xy2[2]) is None, '같은 색 빈칸 누르기 = 지움(지금 동작)')
    await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(250); await pg.keyboard.press('Escape')
    ok((await pg.evaluate(BAT, xy2[2]) or [''])[0].find('rkb-g') >= 0, '지운 것 되돌리기')
    # 4) Shift+B 4번 → 보라, 알림 4번
    await pg.evaluate("__h.Kit.setBColor('n');sessionStorage.removeItem('jblhub.v1.toasts')")
    for _ in range(4): await pg.keyboard.press('Shift+B'); await pg.wait_for_timeout(60)
    T = await pg.evaluate("JSON.parse(sessionStorage.getItem('jblhub.v1.toasts')||'[]').map(x=>x.t).filter(t=>t.startsWith('빈칸 색:'))")
    ok(await pg.evaluate("__h.Kit.bcolor()") == 'v' and len(T) == 4 and '보라' in T[0], f'Shift+B 4번 → 보라 · 알림 {T}')
    ok(not await pg.evaluate("document.body.classList.contains('mode-b')"), 'Shift+B는 모드를 켜지 않음(색만)')
    # 5) 라벨(견본 우클릭 → prompt '수치') → title·모드 칩
    await pg.click('#k-bswc'); await pg.click('#k-bswl .bsw[data-bc="g"]', button='right'); await pg.wait_for_timeout(300)
    bl = await pg.evaluate("localStorage.getItem('jblhub.v1.blabel')"); await pg.keyboard.press('Escape')
    await pg.evaluate("__h.Kit.setBColor('g')"); await pg.keyboard.press('b'); await pg.wait_for_timeout(100)
    chip = await pg.evaluate("document.querySelectorAll('#modechip').length"); ttl = await pg.evaluate("document.querySelector('#k-b').title+' | '+document.querySelector('#k-bswc').title")
    ok(bl == '{"g":"수치"}' and chip == 0 and '수치' in ttl, f'라벨 수치 → LS {bl} · 모드 칩 없음(ux4 B1-4) {chip} · title {ttl[-40:]!r}')
    await pg.keyboard.press('Escape')
    # 6) 형광펜 색 기억(hcol)
    await pg.click('#k-swc'); await pg.click('#k-swl .sw[data-c="g"]'); await pg.keyboard.press('Escape'); await pg.reload(); await pg.wait_for_timeout(1500)
    hc = await pg.evaluate("[__h.Kit.color(),document.querySelector('#k-swl .sw.sel').dataset.c,localStorage.getItem('jblhub.v1.hcol')]")
    ok(hc == ['g', 'g', '"g"'], f'형광펜 초록 → 새로고침 뒤에도 초록 {hc}')
    # 7) 빈칸 모드 밖 우클릭 → 색 바꾸기 팝업 → 보라
    p_ = await pg.evaluate(BXY, xy2[2]); await pg.mouse.click(p_[0], p_[1], button='right'); await pg.wait_for_timeout(200)
    pop = await pg.evaluate("!!document.querySelector('#bcpop.on')"); await pg.screenshot(path=J.TMP + '/ux3i_blank_pop_mac.png')
    await pg.click('#bcpop [data-pbc="v"]'); await pg.wait_for_timeout(200); a6 = await pg.evaluate(BAT, xy2[2])
    ok(pop and a6 and 'rkb-v' in a6[0] and not await pg.evaluate("document.querySelector('#bcpop').classList.contains('on')"), f'모드 밖 우클릭 팝업 → 보라 {a6}')
    op = await pg.evaluate("(w)=>{const e=[...document.querySelectorAll('#stage [data-rk=b]')].find(x=>x.textContent===w);return e.classList.contains('show')}", xy2[2])
    ok(not op, '팝업으로 색 바꿀 때 빈칸이 열리지 않음')
    # 8) 대비 3.0↑ · 연 상태 노랑 바탕 · 인쇄 색 없음
    C = await pg.evaluate("""()=>{const o={};const box=document.querySelector('#t-DD1-3 .tbody');for(const c of ['n','u','g','p','v']){const s=document.createElement('span');s.className='rk-b'+(c!=='n'?' rkb-'+c:'');s.textContent='가나다';box.appendChild(s);const cs=getComputedStyle(s);o[c]=[cs.backgroundColor,cs.borderBottomColor];s.classList.add('show');const c2=getComputedStyle(s);o[c].push(c2.backgroundColor,c2.borderBottomColor);s.remove();}return o;}""")
    def hx(rgb): v = [int(x) for x in rgb[rgb.index('(') + 1:rgb.index(')')].split(',')[:3]]; return '#%02X%02X%02X' % tuple(v)
    crs = {c: round(cr(hx(v[0]), hx(v[1])), 2) for c, v in C.items()}
    ok(all(x >= 3.0 for x in crs.values()) and len(set(v[0] for v in C.values())) == 5, f'가린 빈칸 밑줄 대 바탕 대비 {crs}')
    ok(all(hx(v[2]) == '#FFF3C8' for v in C.values()) and len(set(v[3] for v in C.values())) == 5, f'연 빈칸 = 노랑 바탕 + 제 색 밑줄 {[v[3] for v in C.values()]}')
    await pg.emulate_media(media='print')
    P = await pg.evaluate("[...document.querySelectorAll('#stage .rk-b')].slice(0,4).map(e=>getComputedStyle(e).backgroundColor+'|'+getComputedStyle(e).borderBottomColor)")
    await pg.emulate_media(media='screen')
    ok(P and all(x.startswith('rgba(0, 0, 0, 0)') and x.endswith('rgb(0, 0, 0)') for x in P), f'인쇄 = 색 없이 검은 밑줄 {P}')
    # 9) ⚡ 자동 빈칸 창 색 칩 — 이 탭 전체 규칙을 분홍으로
    await pg.click('#k-auto'); await pg.check('input[name=am][value=red]'); await pg.select_option('#asc', 'all')
    ab0 = await pg.evaluate("document.querySelector('#abc .bsw.sel').dataset.abc"); await pg.click('#abc [data-abc="p"]'); await pg.screenshot(path=J.TMP + '/ux3i_blank_auto_mac.png'); await pg.click('#ago'); await pg.wait_for_timeout(400)
    ar = await pg.evaluate("[JSON.parse(localStorage.getItem('jblhub.v1.autoRule.OMS1')||'{}')['DD1/learn'],document.querySelectorAll('#stage .rk-b[data-auto].rkb-p').length,document.querySelectorAll('#stage .rk-b[data-auto]').length,getComputedStyle(document.querySelector('#stage .rk-b[data-auto]')).borderBottomStyle]")
    ok(ab0 == 'g' and ar[0] and ar[0].get('c') == 'p' and ar[1] > 5 and ar[1] == ar[2] and ar[3] == 'dotted', f'⚡ 자동 빈칸 분홍 저장 → 규칙 c:p · 규칙 빈칸 {ar[1]}/{ar[2]} 분홍 · 점선 (창 기본 색 {ab0})')
    await pg.reload(); await pg.wait_for_timeout(1500)
    ok(await pg.evaluate("document.querySelectorAll('#stage .rk-b[data-auto].rkb-p').length") == ar[1], '새로고침 뒤에도 규칙 빈칸 분홍')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.autoRule.OMS1')")
    # 10) 내 표시 모아보기 — 초록 빈칸만
    await pg.evaluate("__h.Kit.setBColor('g')"); await open_(pg, '#/OMS1/DD1/learn')
    xy3 = await pg.evaluate(WORD, ['t-DD1-4', 0]); await pg.keyboard.press('b'); await pg.mouse.click(xy3[0], xy3[1]); await pg.keyboard.press('Escape')
    await open_(pg, '#/OMS1/_marks/_marks', 1800)
    chips = await pg.evaluate("[...document.querySelectorAll('.mkfbar .mkf')].map(b=>b.dataset.mkcol+':'+b.textContent.trim())")
    await pg.click('.mkf[data-mkcol="bg"]'); await pg.wait_for_timeout(200)
    vis = await pg.evaluate("[...document.querySelectorAll('.mkview .mk-line')].filter(e=>e.offsetParent).map(e=>e.dataset.bk||e.dataset.c)")
    ok(any(c.startswith('bg:') and '수치' in c for c in chips) and vis and all(v == 'bg' for v in vis), f'모아보기 빈칸 색 칩 {chips} → 초록만 {vis}')
    await pg.screenshot(path=J.TMP + '/ux3i_blank_marks_mac.png'); await pg.click('.mkf[data-mkcol="bg"]')
    ok(not errs, f'콘솔 오류 0 {errs[:3]}')
    # 11) 1차 배포본 허브로 열기 — 색 빈칸도 오류 없이 빈칸(회색)
    if _os.path.exists(OLD[7:]):
        pg2 = await ctx.new_page(); e2 = []; pg2.on('pageerror', lambda e: e2.append(str(e)))
        await open_(pg2, '#/OMS1/DD1/learn', 2500, OLD)
        n2 = await pg2.evaluate("document.querySelectorAll('#stage [data-rk=b]').length")
        ok(n2 >= 2 and not e2, f'1차 배포본(7095e56) 허브로 열기 — 빈칸 {n2}개 그려짐 · 오류 {e2[:2]}'); await pg2.close()
    else: print('  (1차 배포본 허브 없음 — tools/legacy_base.py --rev 7095e56로 풀면 검사)')
    await ctx.close()
async def touch(b, W, H):
    ctx = await b.new_context(viewport={'width': W, 'height': H}, has_touch=True); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    await open_(pg, '#/OMS1/DD1/learn'); await pg.evaluate("['bcol','hcol','blabel'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))"); await open_(pg, '#/OMS1/DD1/learn')
    if True:   # ux4 B1-4 모든 폭 = [● 빈칸 ▾] 팝오버(좁은 화면도 형광펜 ▾와 따로)
        await pg.tap('#k-bswc'); await pg.wait_for_timeout(150); await pg.screenshot(path=J.TMP + f'/ux3i_blank_pop_{W}.png')
        r = await pg.evaluate("[...document.querySelectorAll('#k-bswl .bsw')].map(e=>{const r=e.getBoundingClientRect();return Math.round(r.width)})")
        await pg.tap('#k-bswl .bsw[data-bc="p"]'); await pg.wait_for_timeout(150)
        ok(len(r) == 5 and min(r) >= 30 and await pg.evaluate("__h.Kit.bcolor()") == 'p', f'{W} 견본 5색(누름 자리 {r}) → 분홍')
    await pg.keyboard.press('Escape')
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth") and not errs, f'{W} 가로 넘침 없음 · 오류 {errs[:2]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await mac(b); await touch(b, 820, 1180); await touch(b, 1180, 820)
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
