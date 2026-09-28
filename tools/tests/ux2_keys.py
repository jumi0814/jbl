"""2차 묶음 1 회귀: 새 단축키 배치(A02) — H·Shift+H·B(A 별칭)·E·N·Shift+N·T·D·F·C·G·/ · 한 장씩 S ★(B는 빈칸)·keyNotice · ? 도움말 키 표.
맥 1280×900 · 아이패드 세로 820×1180(터치)·가로 1180×820(터치). 스크린샷 work/_tmp/ux2_keys_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1200):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
BODY = "(c)=>document.body.classList.contains(c)"
async def a02(pg, tag):
    await open_(pg, '#/OMS1/DD1/learn')
    await pg.keyboard.press('b'); m1 = await pg.evaluate(BODY, 'mode-b'); await pg.keyboard.press('b'); m2 = await pg.evaluate(BODY, 'mode-b')
    ok(m1 and not m2, f'B → 빈칸 모드 켜기·끄기 ({m1},{m2})')
    await pg.keyboard.press('h'); h1 = await pg.evaluate(BODY, 'mode-h'); await pg.keyboard.press('h'); h2 = await pg.evaluate(BODY, 'mode-h')
    ok(h1 and not h2, f'H 두 번 → 켜졌다 꺼짐 ({h1},{h2})')
    await pg.keyboard.press('a'); a1 = await pg.evaluate(BODY, 'mode-b'); await pg.keyboard.press('Escape')
    ok(a1 and not await pg.evaluate(BODY, 'mode-b'), '옛 A 키도 빈칸 모드 · Esc 끄기')
    c0 = await pg.evaluate("[__h.Kit.color(),document.querySelector('#k-swc .swcur').style.background,document.querySelector('#k-swl .sw.sel').dataset.c]")
    await pg.keyboard.press('Shift+H'); await pg.wait_for_timeout(100)
    try: await pg.wait_for_function("t=>(document.querySelector('#toast').textContent||'').includes(t)", arg='초록', timeout=4000)   # B11 알림 대기열 — 앞 알림 뒤 차례로
    except Exception: pass
    c1 = await pg.evaluate("[__h.Kit.color(),document.querySelector('#k-swc .swcur').style.background,document.querySelector('#k-swl .sw.sel').dataset.c]")
    toast = await pg.inner_text('#toast')
    ok(c0[0] == 'y' and c1[0] == 'g' and c1[1] != c0[1] and c1[2] == 'g' and '초록' in toast, f'Shift+H → 색 칩 {c0} → {c1} · 토스트 {toast!r}')
    await pg.keyboard.press('Shift+H'); await pg.keyboard.press('Shift+H'); await pg.keyboard.press('Shift+H'); await pg.keyboard.press('Shift+H')
    ok(await pg.evaluate("__h.Kit.color()") == 'y', 'Shift+H 다섯 번 → 한 바퀴(y→g→p→u→o→y)')
    # D: 지금 카드 ✓ / F: 접기 / C: 압축
    await pg.evaluate("(()=>{const c=document.querySelector('#t-DD1-2');window.scrollTo(0,c.getBoundingClientRect().top+scrollY-120)})()"); await pg.wait_for_timeout(1200)
    cur = await pg.evaluate("(()=>{const n=document.querySelector('#lmn').textContent;return n})()")
    await pg.keyboard.press('d'); await pg.wait_for_timeout(300)
    dn = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.done.OMS1')") or '{}')
    aid = await pg.evaluate(f"document.querySelector('#t-DD1-{int(cur)-1}').dataset.aid") if cur.isdigit() else None
    ok(cur.isdigit() and dn.get(aid) == 1, f'D → 지금 카드({cur}) ✓ 이해함 {list(dn)[:2]}')
    await pg.keyboard.press('d'); await pg.wait_for_timeout(300)
    c = await pg.evaluate("(()=>{const n=+document.querySelector('#lmn').textContent;const c=document.querySelector('#t-DD1-'+(n-1));return c?[n,c.classList.contains('open')]:null})()")
    await pg.keyboard.press('f'); await pg.wait_for_timeout(150)
    c2 = await pg.evaluate(f"document.querySelector('#t-DD1-{c[0]-1}').classList.contains('open')") if c else None
    ok(c and c[1] != c2, f'F → 지금 카드 접기/펼치기 {c} → {c2}')
    await pg.keyboard.press('c'); cd = await pg.evaluate("document.querySelector('#stage').classList.contains('cond')"); await pg.keyboard.press('c')
    ok(cd and not await pg.evaluate("document.querySelector('#stage').classList.contains('cond')"), 'C → 압축 보기 켜고 끄기')
    await pg.keyboard.press('/'); ok(await pg.evaluate("document.activeElement.id") == 'gsearch', '/ → 검색창')
    await pg.keyboard.press('Escape'); await pg.evaluate("document.activeElement.blur()")
    await pg.keyboard.press('t'); t1 = await pg.evaluate(BODY, 'kit-off'); await pg.keyboard.press('t')
    ok(t1 and not await pg.evaluate(BODY, 'kit-off'), 'T → 도구 막대 숨기기·다시')
    await pg.keyboard.press('g'); await pg.wait_for_timeout(400); ok('/_home/' in await pg.evaluate('location.hash'), 'G → 과목 홈')
    # E·N·Shift+N — 저장형 빈칸 3개(한 카드)
    await open_(pg, '#/OMS1/DD1/learn')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.fold.OMS1.DD1');localStorage.removeItem('jblhub.v1.done.OMS1')"); await open_(pg, '#/OMS1/DD1/learn')   # D(✓하면 접기)로 접힌 카드는 N 대상이 아님
    await pg.evaluate("""()=>{const B=document.querySelector('#t-DD1-3');const T=__h.Kit.textOf(B);const ws=[...new Set((T.match(/[A-Za-z가-힣]{3,}/g)||[]))].filter(w=>T.split(w).length===2).slice(0,3);
      const k='jblhub.v1.ann.OMS1';const a=JSON.parse(localStorage.getItem(k)||'{}');a[B.dataset.aid]=ws.map(x=>({t:'b',x,i:0}));localStorage.setItem(k,JSON.stringify(a));}""")
    await open_(pg, '#/OMS1/DD1/learn'); await pg.evaluate("document.querySelector('#t-DD1-3').scrollIntoView({block:'start'})"); await pg.wait_for_timeout(1000)
    NB = "[...new Set([...document.querySelectorAll('#t-DD1-3 [data-rk=b].show')].map(e=>e.dataset.g))].length"
    await pg.keyboard.press('n'); n1 = await pg.evaluate(NB); await pg.keyboard.press('n'); n2 = await pg.evaluate(NB)
    ok(n1 == 1 and n2 == 2, f'N → 가린 칸 하나씩 열기 ({n1},{n2})')
    await pg.keyboard.press('Shift+N'); ok(await pg.evaluate(NB) == 0, 'Shift+N → 이 카드 다시 가리기')
    await pg.keyboard.press('e'); e1 = await pg.evaluate("getComputedStyle(document.querySelector('#t-DD1-3 [data-rk=b]')).color")
    await pg.keyboard.press('e'); e2 = await pg.evaluate("getComputedStyle(document.querySelector('#t-DD1-3 [data-rk=b]')).color")
    ok(e1 != 'rgba(0, 0, 0, 0)' and e2 == 'rgba(0, 0, 0, 0)', f'E → 전부 열기·가리기 ({e1},{e2})')
    # 한 장씩: S = ★, B = 빈칸 모드(★ 그대로)
    await open_(pg, '#/OMS1/_jb/_jb'); await pg.evaluate("localStorage.removeItem('jblhub.v1.keyNotice');localStorage.setItem('jblhub.v1.ux2old','1')")   # fixB flow V17: 안내는 옛 사용자(1차 판 기록이 있던 기기)에게만
    await open_(pg, '#/OMS1/_jb/_jb'); await pg.click('#fone'); await pg.wait_for_timeout(300)
    try: await pg.wait_for_function("t=>(document.querySelector('#toast').textContent||'').includes(t)", arg='★는 이제 S', timeout=4000)   # B11 알림 대기열 — 앞 알림 뒤 차례로
    except Exception: pass
    t = await pg.inner_text('#toast'); ok('★는 이제 S' in t, f'처음 한 번 안내 토스트 {t!r}')
    cid = await pg.evaluate("document.querySelector('#cards .qc.cur').dataset.id")
    BM = f"!!(JSON.parse(localStorage.getItem('jblhub.v1.mk.OMS1')||'{{}}').bm||{{}})['{cid}']"
    b0 = await pg.evaluate(BM); await pg.keyboard.press('s'); b1 = await pg.evaluate(BM)
    await pg.keyboard.press('b'); b2 = await pg.evaluate(BM); mb = await pg.evaluate(BODY, 'mode-b'); await pg.keyboard.press('Escape')
    ok(b1 != b0 and b2 == b1 and mb, f'한 장씩 S → ★ 토글({b0}→{b1}) · B는 ★ 그대로({b2})·빈칸 모드({mb})')
    okeys = await pg.evaluate("document.querySelector('.okeys').textContent+' | '+document.querySelector('#obm').title")
    ok('S ★' in okeys and '(S)' in okeys, f'풀이 막대 안내 {okeys!r}')
    await pg.click('#fone')
    await pg.keyboard.press('?'); ht = await pg.inner_text('#help')
    ok('빈칸 B' in ht and 'S ★' in ht and '한/영 상관없이' in ht and 'Shift+H' in ht, '? 도움말 키 표(B 빈칸·S ★·한/영·Shift+H)')
    await pg.screenshot(path=J.TMP + f'/ux2_keys_help_{tag}.png'); await pg.keyboard.press('Escape')
    titles = await pg.evaluate("['#k-h','#k-b','#k-eye'].map(x=>document.querySelector(x).title).join(' | ')")
    ok('(H)' in titles and '(B)' in titles and '(E)' in titles, f'도구 막대 제목 {titles[:80]}')
async def a03(pg, tag, vp):
    """A03 집중 모드(V)·글자 크기(A−/A+)"""
    await open_(pg, '#/OMS1/DD1/learn'); await pg.evaluate("localStorage.removeItem('jblhub.v1.focus');localStorage.removeItem('jblhub.v1.fontScale')"); await open_(pg, '#/OMS1/DD1/learn')
    await pg.keyboard.press('v'); await pg.wait_for_timeout(300)
    r = await pg.evaluate("(()=>({f:document.body.classList.contains('focus'),side:getComputedStyle(document.querySelector('#side')).display,hero:getComputedStyle(document.querySelector('#hero')).display,w:Math.round(document.querySelector('#stage').getBoundingClientRect().width),top:document.querySelector('#top').offsetHeight}))()")
    ok(r['f'] and r['hero'] == 'none' and (r['side'] == 'none' or vp['width'] <= 860) and (vp['width'] != 1180 or r['w'] >= 900) and r['top'] <= 26, f'V → 집중: 사이드바·hero 숨김·본문 폭·얇은 상단 {r}')
    await pg.screenshot(path=J.TMP + f'/ux2_keys_focus_{tag}.png')
    DT = "(()=>{const d=document.querySelector('#dtabs').getBoundingClientRect();return [Math.round(d.top),Math.round(d.bottom)]})()"
    await pg.evaluate("scrollBy(0,600)"); await pg.wait_for_timeout(450); d1 = await pg.evaluate(DT)
    await pg.evaluate("scrollBy(0,-60)"); await pg.wait_for_timeout(450); d2 = await pg.evaluate(DT)
    ok(d1[1] <= 0 and d2[0] >= 0 and d2[1] > 20, f'아래로 600 → 탭 줄 화면 밖 {d1} · 위로 60 → 다시 보임 {d2}')
    await pg.evaluate("document.querySelector('#t-DD1-3').scrollIntoView({block:'start'})"); await pg.evaluate("scrollBy(0,-40)"); await pg.wait_for_timeout(900)
    pt = await pg.inner_text('#fpill'); ok('카드 ' in pt and '/20' in pt or '/' in pt and '카드' in pt, f'알약에 카드 n/N ({pt})')
    await pg.reload(); await pg.wait_for_timeout(1500)
    ok(await pg.evaluate("document.body.classList.contains('focus')"), '새로고침 뒤에도 집중 모드 유지')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
    ok(not await pg.evaluate("document.body.classList.contains('focus')"), 'Esc → 집중 모드 나가기')
    FS = "parseFloat(getComputedStyle(document.querySelector('#stage .tbody .li')).fontSize)"
    f0 = await pg.evaluate(FS); await pg.evaluate("document.querySelector('details.pmore').open=true")
    await pg.click('#fsup'); await pg.click('#fsup'); f1 = await pg.evaluate(FS); await pg.reload(); await pg.wait_for_timeout(1500); f2 = await pg.evaluate(FS)
    ok(abs(f1 / f0 - 1.1) < 0.02 and f2 == f1, f'A+ 두 번 → 글자 {f0}→{f1} (새로고침 뒤 {f2})')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.fontScale')")
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), '가로 넘침 없음')
async def a04(pg, tag, vp):
    """A04 사이드바 접기(\\ · ‹ ›) · 정리표·비교표·한눈표 1440 이하 자동 접기(wideSide)"""
    await open_(pg, '#/CONS/WHT/learn'); await pg.evaluate("['sidefold','wideSide','focus'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))")
    await open_(pg, '#/CONS/WHT/sum', 1500)
    S = "(()=>({fold:document.body.classList.contains('sidefold'),tw:Math.round((document.querySelector('.msum table.mtx')||document.querySelector('table.cmp')).getBoundingClientRect().width),side:Math.round(document.querySelector('#side').getBoundingClientRect().width),over:document.documentElement.scrollWidth>innerWidth}))()"
    r0 = await pg.evaluate(S)
    if vp['width'] <= 860:
        ok(not r0['fold'] and not r0['over'], f'세로 화면은 접기 없음(서랍) {r0}')
        await pg.keyboard.press('Backslash'); ok(await pg.evaluate("document.body.classList.contains('navopen')"), '\\ → 좁은 화면은 서랍 열기'); await pg.keyboard.press('Escape'); return
    ok(r0['fold'] and r0['side'] == 0 and (vp['width'] != 1280 or r0['tw'] >= 1180) and not r0['over'], f'정리표 들어가면 자동 접기 · 표 폭 {r0}')
    await pg.screenshot(path=J.TMP + f'/ux2_keys_sidefold_{tag}.png')
    await pg.keyboard.press('Backslash'); await pg.wait_for_timeout(450); r1 = await pg.evaluate(S)
    ws = await pg.evaluate("localStorage.getItem('jblhub.v1.wideSide')")
    await pg.keyboard.press('Backslash'); await pg.wait_for_timeout(450); r2 = await pg.evaluate(S)
    ok(not r1['fold'] and r1['side'] > 200 and ws == '1' and r2['fold'], f'\\ → 펼침(wideSide={ws}) → 다시 접힘 {r1["side"]}/{r2["side"]}')
    await pg.click('#dtabs button[data-t="learn"]'); await pg.wait_for_timeout(700)
    ok(await pg.evaluate("document.body.classList.contains('sidefold')"), '학습 탭으로 돌아가도 접은 설정 그대로')
    await pg.click('#sideopen'); await pg.wait_for_timeout(450)
    ok(not await pg.evaluate("document.body.classList.contains('sidefold')"), '왼쪽 가장자리 › → 펼침')
    await open_(pg, '#/CONS/_tbl/_tbl'); r3 = await pg.evaluate(S)
    ok(not r3['fold'] and not r3['over'], f'펼친 뒤(wideSide)에는 비교표도 자동으로 안 접음 {r3}')
    await pg.click('#side .nvhead [data-nvfold]'); await pg.wait_for_timeout(450)
    vis = await pg.evaluate("getComputedStyle(document.querySelector('#sideopen')).display")
    ok(await pg.evaluate("document.body.classList.contains('sidefold')") and vis == 'flex', f'메뉴 머리 ‹ → 접힘 · 왼쪽 가장자리 › ({vis})')
    await pg.click('#sideopen'); await pg.evaluate("['sidefold','wideSide'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))")
async def a05(pg, tag, vp):
    """A05 가리기 보기(Q — 저장 안 함)·N·Shift+N·카드 머리 칩·⚡ 창 첫 선택지·강의 전체 200ms"""
    await open_(pg, '#/OMS1/EXT/learn'); await pg.evaluate("localStorage.removeItem('jblhub.v1.ann.OMS1');sessionStorage.clear();['qzscope','qzfix','focus','sidefold'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))")
    await open_(pg, '#/OMS1/EXT/learn')
    ANN = "(localStorage.getItem('jblhub.v1.ann.OMS1')||'').length"
    a0 = await pg.evaluate(ANN)
    # 빨간 핵심어가 4개 이상인 카드 머리를 탭 아래로(지금 카드)
    j = await pg.evaluate("(()=>{const c=[...document.querySelectorAll('#stage .tc')].find(c=>c.querySelectorAll('.tbody .k').length>=5);c.scrollIntoView({block:'start'});scrollBy(0,-130);return c.id})()")
    await pg.wait_for_timeout(1100)
    await pg.keyboard.press('q'); await pg.wait_for_timeout(200)
    r = await pg.evaluate(f"(()=>{{const c=document.querySelector('#{j}');const ks=[...c.querySelectorAll('.k.qzk')];return {{n:ks.length,col:ks.length?getComputedStyle(ks[0]).color:'',other:document.querySelectorAll('#stage .k.qzk').length}}}})()")
    ok(r['n'] >= 4 and r['col'] == 'rgba(0, 0, 0, 0)' and r['other'] == r['n'] and await pg.evaluate(ANN) == a0, f'Q → 지금 카드({j}) 빨간 핵심어만 가림 · ann 변화 0 {r}')
    await pg.screenshot(path=J.TMP + f'/ux2_keys_quiz_{tag}.png')
    await pg.evaluate(f"document.querySelector('#{j} .k.qzk').click()")
    sh = await pg.evaluate(f"[...document.querySelectorAll('#{j} .k.qzk')].map(k=>k.classList.contains('show'))")
    ok(sh[0] and not any(sh[1:]), f'한 칸 누르면 그 칸만 {sh[:5]}')
    chip = await pg.evaluate(f"document.querySelector('#{j} .thead .qzchip')?.textContent")
    ok(chip == f'▣ 1/{len(sh)} 열림', f'카드 머리 칩 {chip}')
    y0 = await pg.evaluate('scrollY')
    for _ in range(3): await pg.keyboard.press('n'); await pg.wait_for_timeout(120)
    n3 = await pg.evaluate(f"document.querySelectorAll('#{j} .k.qzk.show').length"); y1 = await pg.evaluate('scrollY')
    ok(n3 == 4 and y1 != y0, f'N 세 번 → 3개 더 열림({n3}) · 스크롤 이동 {y0}→{y1}')
    await pg.keyboard.press('Shift+N'); await pg.wait_for_timeout(100)
    ok(await pg.evaluate(f"document.querySelectorAll('#{j} .k.qzk.show').length") == 0, 'Shift+N → 다시 가림')
    await pg.evaluate(f"document.querySelector('#{j} .thead .qzchip').click()")
    ok(await pg.evaluate(f"[...document.querySelectorAll('#{j} .k.qzk')].every(k=>k.classList.contains('show'))"), '카드 머리 칩 → 이 카드 전체 열기')
    # 탭을 옮겼다 와도 연 칸 유지
    await pg.click('#dtabs button[data-t="sum"]'); await pg.wait_for_timeout(500); await pg.click('#dtabs button[data-t="learn"]'); await pg.wait_for_timeout(1200)
    ok(await pg.evaluate(f"document.querySelectorAll('#{j} .k.qzk.show').length") == r['n'], '탭을 옮겼다 와도 가리기·연 칸 유지(sessionStorage)')
    await pg.keyboard.press('q')
    # 강의 전체 — 200ms 이하·쓰기 없음
    await pg.click('#k-auto'); v = await pg.evaluate("document.querySelector('input[name=am]:checked').value")
    await pg.select_option('#qzsc', 'all')
    t = await pg.evaluate("(()=>{const t0=performance.now();document.querySelector('#ago').click();return performance.now()-t0})()")
    na = await pg.evaluate("[document.querySelectorAll('#stage .k.qzk').length,document.querySelectorAll('#stage .k').length]")
    ok(v == 'quiz' and t <= 200 and na[0] > 20 and await pg.evaluate(ANN) == a0, f'⚡ 첫 선택지 = 가리기(기본) · 강의 전체 {na} {t:.0f}ms · ann 변화 0')
    await pg.screenshot(path=J.TMP + f'/ux2_keys_quizall_{tag}.png')
    await pg.reload(); await pg.wait_for_timeout(1500)
    ok(not await pg.evaluate("document.querySelector('#stage').classList.contains('quiz')") and await pg.evaluate(ANN) == a0, '새로고침 → 가리기 보기 꺼짐 · ann 변화 0')
    # 저장형 빈칸: 연 상태 세션 유지
    await pg.evaluate("""()=>{const B=document.querySelector('#stage .tc');const T=__h.Kit.textOf(B);const ws=[...new Set((T.match(/[A-Za-z가-힣]{4,}/g)||[]))].filter(w=>T.split(w).length===2).slice(0,2);
      localStorage.setItem('jblhub.v1.ann.OMS1',JSON.stringify({[B.dataset.aid]:ws.map(x=>({t:'b',x,i:0}))}));}""")
    await pg.reload(); await pg.wait_for_timeout(1500)
    await pg.evaluate("document.querySelector('#stage .tc [data-rk=b]').click()")
    await pg.click('#dtabs button[data-t="jb"]'); await pg.wait_for_timeout(500); await pg.click('#dtabs button[data-t="learn"]'); await pg.wait_for_timeout(1200)
    ok(await pg.evaluate("document.querySelector('#stage .tc [data-rk=b]').classList.contains('show')") and await pg.evaluate("document.querySelector('#stage .tc .qzchip')?.textContent") == '▣ 1/2 열림', '연 저장형 빈칸도 탭을 옮겼다 와도 열림 · 칩 1/2')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.ann.OMS1')")
async def a06(pg, tag, vp):
    """A06 모드 칩·모드 중 카드 점선·스크롤하는 동안 도구 막대 ✎·↶ 배지·kit-off 저장"""
    await open_(pg, '#/OMS1/DD2/learn'); await pg.evaluate("['kitoff','focus','sidefold'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))"); await open_(pg, '#/OMS1/DD2/learn')
    await pg.keyboard.press('h'); await pg.wait_for_timeout(100)
    c = await pg.evaluate("(()=>{const c=document.querySelector('.modechip');return [getComputedStyle(c).display,c.textContent,document.querySelector('#stage').classList.contains('modeon'),getComputedStyle(document.querySelector('#stage .tc')).outlineStyle]})()")
    ok(c[0] != 'none' and c[1] == '🖍 형광펜 켜짐 · 노랑 — 누르면 끄기 (H·Esc)' and c[2] and c[3] == 'dashed', f'H → 모드 칩·카드 점선 {c}')
    await pg.screenshot(path=J.TMP + f'/ux2_keys_modechip_{tag}.png')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)
    ok(await pg.evaluate("getComputedStyle(document.querySelector('.modechip')).display") == 'none' and not await pg.evaluate("document.querySelector('#stage').classList.contains('modeon')"), 'Esc → 모드 칩 사라짐')
    await pg.keyboard.press('b'); t = await pg.inner_text('.modechip'); await pg.click('.modechip')
    ok(t == '▣ 빈칸 만들기 켜짐 · 회색 — 빈칸을 누르면 지워져요 (B·Esc)' and not await pg.evaluate("document.body.classList.contains('mode-b')"), f'B → 빈칸 칩 문구 · 칩 누르면 끄기 ({t})')
    # ↶ 배지 = 되돌리기 스택 길이
    await pg.keyboard.press('h')
    for k in (1, 2):
        xy = await pg.evaluate(f"""(()=>{{const li=[...document.querySelectorAll('#t-DD2-{k} .tbody li, #t-DD2-{k} .tbody div.li')].find(e=>e.offsetParent&&/[A-Za-z가-힣]{{4}}/.test(e.textContent));li.scrollIntoView({{block:'center'}});const w=document.createTreeWalker(li,NodeFilter.SHOW_TEXT);let t;while(t=w.nextNode()){{const m=/[A-Za-z가-힣]{{4,}}/.exec(t.nodeValue);if(m&&!t.parentElement.closest('button,.noann')){{const r=document.createRange();r.setStart(t,m.index+1);r.setEnd(t,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2];}}}}}})()""")
        await pg.mouse.click(xy[0], xy[1]); await pg.wait_for_timeout(120)
    u = await pg.evaluate("[document.querySelector('#k-undo .ubn').textContent,__h.Kit.undoN()]"); await pg.keyboard.press('Escape')
    ok(u[0] == str(u[1]) and u[1] == 2, f'↶ 배지 = 되돌리기 스택 길이 {u}')
    await pg.keyboard.press('Control+z'); await pg.keyboard.press('Control+z')
    ok(await pg.evaluate("document.querySelector('#k-undo .ubn').textContent") == '' and await pg.evaluate("document.querySelector('#k-undo').disabled"), '되돌릴 것 없으면 배지 숨김·비활성')
    # 스크롤하는 동안 ✎ 하나
    await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(300); h0 = await pg.evaluate("document.querySelector('#kit').offsetHeight")
    await pg.mouse.move(vp['width'] / 2, vp['height'] / 2)
    for _ in range(4): await pg.mouse.wheel(0, 250); await pg.wait_for_timeout(90)
    h1 = await pg.evaluate("document.querySelector('#kit').offsetHeight"); await pg.screenshot(path=J.TMP + f'/ux2_keys_kitmin_{tag}.png')
    await pg.wait_for_timeout(1500); h2 = await pg.evaluate("document.querySelector('#kit').offsetHeight")
    ok(h1 <= 48 and h2 == h0, f'스크롤하는 동안 도구 막대 {h0}→{h1}px(≤48) · 1.5초 뒤 {h2}')
    await pg.keyboard.press('t'); await pg.reload(); await pg.wait_for_timeout(1300)
    ok(await pg.evaluate("document.body.classList.contains('kit-off')"), 'T → 새로고침 뒤에도 도구 막대 숨김 유지(LS kitoff)')
    await pg.keyboard.press('t'); ok(not await pg.evaluate("document.body.classList.contains('kit-off')"), 'T → 다시 보임')
    if vp['width'] <= 860:
        lb = await pg.evaluate("[...document.querySelectorAll('#kit .lb2')].map(e=>getComputedStyle(e).display+':'+e.textContent)")
        ok(all(x.startswith('block') for x in lb) and len(lb) == 4, f'860 이하 아이콘 아래 라벨 {lb}')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.ann.OMS1')")
async def a08(pg, tag, vp):
    """A08 드래그가 다른 카드에서 끝나면 시작 카드 끝까지(토스트) · 화면 가장자리 자동 스크롤(초당 400px)"""
    await open_(pg, '#/OMS1/DD1/learn'); await pg.evaluate("['ann.OMS1','fold.OMS1.DD1','done.OMS1','focus'].forEach(k=>localStorage.removeItem('jblhub.v1.'+k))"); await open_(pg, '#/OMS1/DD1/learn')
    P = """(sel)=>{const L=[...document.querySelectorAll(sel)].filter(e=>e.offsetParent&&/[A-Za-z가-힣]{4}/.test(e.textContent));const e=L[Math.floor(L.length/2)]||L[0];return e?e:null}"""
    await pg.evaluate("document.querySelector('#t-DD1-3 .tbody').scrollIntoView({block:'start'})"); await pg.evaluate("scrollBy(0,-160)"); await pg.wait_for_timeout(600)
    p1 = await pg.evaluate("""(()=>{const L=[...document.querySelectorAll('#t-DD1-3 .tbody li,#t-DD1-3 .tbody div.li')].filter(e=>e.offsetParent&&!e.closest('.noann')&&/[A-Za-z가-힣]{4}/.test(e.textContent));const e=L[L.length-1];e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return [r.left+30,r.top+r.height/2]})()""")
    p2 = await pg.evaluate("""(()=>{const e=document.querySelector('#t-DD1-4 .thead');const r=e.getBoundingClientRect();return [r.left+140,r.top+14]})()""")
    await pg.keyboard.press('h'); await pg.mouse.move(p1[0], p1[1]); await pg.mouse.down(); await pg.mouse.move(p2[0], p2[1], steps=8); await pg.mouse.up(); await pg.wait_for_timeout(150)
    try: await pg.wait_for_function("t=>(document.querySelector('#toast').textContent||'').includes(t)", arg='카드 경계까지', timeout=4000)   # B11 알림 대기열 — 앞 알림 뒤 차례로
    except Exception: pass
    ann = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')") or '{}'); a3 = await pg.evaluate("document.querySelector('#t-DD1-3').dataset.aid"); a4 = await pg.evaluate("document.querySelector('#t-DD1-4').dataset.aid")
    t = await pg.inner_text('#toast')
    ok(len(ann.get(a3, [])) == 1 and not ann.get(a4) and not ann.get(a4 + '~h') and '카드 경계까지' in t, f'카드 3 → 카드 4로 끌기 = 카드 3 끝까지 표시 1 · 토스트 {t!r} ({[(k[-10:], len(v)) for k, v in ann.items()]})')
    await pg.keyboard.press('Control+z')
    # 자동 스크롤: 아래 가장자리 60px 안에 1초 머묾
    await pg.evaluate("document.querySelector('#t-DD1-5').scrollIntoView({block:'start'})"); await pg.evaluate("scrollBy(0,-150)"); await pg.wait_for_timeout(500)
    q = await pg.evaluate("""(()=>{const L=[...document.querySelectorAll('#stage .tc.open .tbody li,#stage .tc.open .tbody div.li,#stage .tc.open .tbody td')].filter(e=>e.offsetParent&&!e.closest('.noann,.c-exam')&&/[A-Za-z가-힣]{4}/.test(e.textContent)&&e.getBoundingClientRect().top>150&&e.getBoundingClientRect().bottom<innerHeight-250);const r=L[0].getBoundingClientRect();return [r.left+30,r.top+Math.min(r.height/2,12)]})()""")
    await pg.mouse.move(q[0], q[1]); await pg.mouse.down(); await pg.mouse.move(q[0] + 40, vp['height'] - 25, steps=6); y0 = await pg.evaluate('scrollY')
    await pg.wait_for_timeout(1000); y1 = await pg.evaluate('scrollY'); await pg.mouse.up(); await pg.wait_for_timeout(200); y2 = await pg.evaluate('scrollY')
    ok(300 <= y1 - y0 <= 520 and y2 - y1 < 40, f'아래 가장자리 1초 → 자동 스크롤 +{y1 - y0:.0f}px · 떼면 멈춤(+{y2 - y1:.0f})')
    await pg.keyboard.press('Control+z'); await pg.keyboard.press('Escape'); await pg.evaluate("localStorage.removeItem('jblhub.v1.ann.OMS1')")
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    await a02(pg, tag)
    await a03(pg, tag, vp)
    await a04(pg, tag, vp)
    await a05(pg, tag, vp)
    await a06(pg, tag, vp)
    if not touch: await a08(pg, tag, vp)
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 820, 'height': 1180}, True, 'ipad')
        await run(b, {'width': 1180, 'height': 820}, True, 'ipadl')
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
