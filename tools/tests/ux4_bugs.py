"""ux4 B1-7 오류 재현 → 수정 확인(work/ux4_bugs.json 51건 중 묶음 1 몫) — 1280×900 · 820×1180(터치)
B04 허브 홈에서 H·B·V·T·E·N은 상태를 바꾸지 않음 · 도움말 열린 동안 H·C 무시 · 홈에서 Esc = 집중 모드 끔
B07 필터 1문항 → 압축 인쇄 미디어에서 보이는 문항 1 · B08 정리표 '자세히' 작은 표가 칸 밖으로 0 · B09 예상 J 3번 = 셋째 카드
B10 정리표 [기출 나온 주제]·예상 [짤 변형] → 다른 화면 → 뒤로 = 필터 그대로 · B11 820 CONS CRK 비교표 5열↑ = 카드형·기출 대장 표 가로 넘침 0
B12 한눈표 답 가리기 × 👁: 표 하나 '모두 열기' = 그 표만 · 답 열 👁 한 번에 풀림 · 끌 때 개인 답 가림 보존
B15 집중 모드에서 / → 검색칸 포커스(글자가 단축키가 되지 않음) · B16 그림 확대 중 뒤로 → 모달 닫힘·스크롤 잠김 없음
B17 한 장씩 회차 중 문항 id로 이동 = 확인창 0 · B18 형광펜 모드 중 ⭐ 연도 칩 = 미리보기(해시 그대로) · B19·B37 한 장씩 끝 = 필터 목록 그대로·안내
B20 교수 줄 합산 표시 · B21 달력 + 시간 → 메뉴 오늘 숫자 바로 · B23 검색 결과로 가면 검색칸 비움 · 한 글자 안내
B24 [2회↑] 빈 묶음 머리 숨김 · B25 예상 [틀린 것] 0개 안내·답 모두 접기 글자 · B27 비교표 목차 목록 = 휠로 닫힘 · B28 카드형 라벨로 열 가림 풀기
B29 내 표시 전체 수 = 표시 수 · B30 압축 목록 Space = 펼침 · B35 ⋯ 메뉴 Esc · B36 미리보기 z-index < 탭 줄 · B38 다른 화면 반대 판정 = 새 기록
B43 맥(아이패드 아님) 홈 화면 추가 안내 없음 · B46 전체정리표 칩 이름 짧게·J가 펼친 전체정리표 행도 · B47 [기출 연결 표만] 빈 강의 칩 → 필터 풀고 이동
B49 한눈표 [✗] 뒤 강의 칩 숫자 = 보이는 행 · B50 형광펜 모드 중 플래시카드 누르면 안 뒤집힘 · 콘솔 오류 0"""
import os as _os, sys as _sys, re, json, datetime; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def go(pg, h, sel=None, wait=700):
    await pg.goto('about:blank'); await pg.goto(U + h)
    await pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0", timeout=30000)
    if sel: await pg.wait_for_selector(sel, timeout=30000)
    await pg.wait_for_timeout(wait)
async def jbm(pg, k):
    for _ in range(3):
        if not await pg.evaluate("!!document.querySelector('#jbmenu')"): await pg.evaluate("document.querySelector('#fmenu').click()")
        try: await pg.wait_for_selector(f'#jbmenu [data-jbm={k}]', timeout=1500); break
        except Exception: pass
    await pg.evaluate(f"document.querySelector('#jbmenu [data-jbm={k}]').click()")
def kd(key, code): return f"document.dispatchEvent(new KeyboardEvent('keydown',{{key:'{key}',code:'{code}',bubbles:true}}))"
async def mac(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []; dlg = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
    pg.on('dialog', lambda d: (dlg.append(d.message), asyncio.ensure_future(d.accept())))
    await go(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('jblhub.v1.tauto','false');localStorage.setItem('jblhub.v1.whatsNew.3','1')")
    # ---- B04
    await go(pg, '#/', '#home .hsj')
    for k, c in [('ㅗ', 'KeyH'), ('ㅠ', 'KeyB'), ('ㅍ', 'KeyV'), ('ㅅ', 'KeyT'), ('ㄷ', 'KeyE')]: await pg.evaluate(kd(k, c))
    await pg.wait_for_timeout(200)
    r = await pg.evaluate("[document.body.className,localStorage.getItem('jblhub.v1.focus'),localStorage.getItem('jblhub.v1.kitoff'),__h.Kit.mode()]")
    ok('mode-h' not in r[0] and 'mode-b' not in r[0] and 'focus' not in r[0] and 'rk-reveal' not in r[0] and 'kit-off' not in r[0] and r[1] is None and r[2] is None and r[3] is None, f'B04 허브 홈 H·B·V·T·E 무시 {r}')
    await go(pg, '#/CONS/WHT/learn', '#stage .tc')
    await pg.keyboard.press('?'); await pg.wait_for_timeout(150); await pg.evaluate(kd('ㅗ', 'KeyH')); await pg.evaluate(kd('ㅊ', 'KeyC')); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(150)
    r = await pg.evaluate("[__h.Kit.mode(),document.querySelector('#stage').classList.contains('cond'),document.querySelector('#help').classList.contains('on')]")
    ok(r == [None, False, False], f'B04 도움말 열린 동안 H·C 무시 · Esc = 도움말 닫기 {r}')
    await pg.evaluate("localStorage.setItem('jblhub.v1.focus','true')"); await go(pg, '#/', '#home .hsj')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(150)
    ok(await pg.evaluate("localStorage.getItem('jblhub.v1.focus')") == 'false', 'B04 허브 홈에서 Esc = 집중 모드 꺼짐(저장)')
    # ---- B07 인쇄 = 필터 그대로
    await go(pg, '#/CONS/_jb/_jb', '#cards .qc')
    id0 = await pg.evaluate("__h.JB.vis[0].dataset.id"); await pg.evaluate(f"__h.mark('{id0}','ng','set')")
    await pg.evaluate("document.querySelector('#jbbar [data-qf=ng]').click()"); await pg.wait_for_timeout(300)
    await pg.evaluate("document.body.classList.add('prc')"); await pg.emulate_media(media='print')
    n = await pg.evaluate("[...document.querySelectorAll('#cards .qc')].filter(c=>getComputedStyle(c).display!=='none').length")
    await pg.emulate_media(media='screen'); await pg.evaluate("document.body.classList.remove('prc')")
    ok(n == 1, f'B07 틀린 것 1문항 → 압축 인쇄에 보이는 문항 {n}')
    # ---- B30 압축 목록 Space · B35 ⋯ Esc
    await pg.evaluate("document.querySelector('#jbbar [data-qf=\"\"]').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('#fmenu').click()"); await pg.wait_for_timeout(150)
    ok(await pg.evaluate("!!document.querySelector('#jbmenu')"), 'B35 ⋯ 메뉴 열림'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)
    ok(await pg.evaluate("!document.querySelector('#jbmenu')"), 'B35 Esc → ⋯ 메뉴 닫힘')
    await jbm(pg, 'list'); await pg.wait_for_timeout(300)
    await pg.keyboard.press('j'); await pg.wait_for_timeout(300); await pg.keyboard.press('Space'); await pg.wait_for_timeout(200)
    r = await pg.evaluate("(()=>{const c=[...document.querySelectorAll('#cards .qc')].find(x=>x.classList.contains('lx'));return c?[c.classList.contains('open'),getComputedStyle(c.querySelector('.ans')).display]:null})()")
    ok(r and r[0] and r[1] != 'none', f'B30 압축 목록 J → Space = 그 카드 펼치고 답 보임 {r}')
    await jbm(pg, 'list'); await pg.wait_for_timeout(200)
    # ---- B17·B19·B37 한 장씩
    await pg.evaluate("document.querySelector('#jbbar [data-qf=ng]').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(300)
    j1 = await pg.evaluate("document.querySelector('#jbprog').innerText")
    d0 = len(dlg); other = await pg.evaluate(f"__h.PACKS.CONS.order.find(i=>i!=='{id0}'&&!(__h.PACKS.CONS.refids||[]).includes(i))")
    await pg.evaluate(f"__h.openDoc('CONS','_jb','_jb',null,{{qid:'{other}'}})"); await pg.wait_for_timeout(600)
    r = await pg.evaluate("[__h.JB.one,(__h.JB.vis[__h.JB.cur]||{dataset:{}}).dataset.id]")
    ok(len(dlg) == d0 and r[1] == other, f'B17 회차 중 다른 문항으로 이동 → 확인창 {len(dlg) - d0}번 · 그 문항 {r}')
    ok('J/K' not in j1, f'B37 한 장씩 진행 줄에 J/K 안내 없음')
    await pg.evaluate("__h.JB.F.mine='ng';__h.JB.sync();__h.JB._free=true;__h.JB.apply(true);__h.JB._free=false"); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(300)
    r = await pg.evaluate("[__h.JB.one,[...document.querySelectorAll('#cards .qc')].filter(c=>!c.classList.contains('hid')).length,__h.JB.vis.length,document.querySelector('#jbprog').innerText.includes('J/K')]")
    ok(not r[0] and r[1] == r[2] == 1 and r[3], f'B19 한 장씩 끝 = 필터(틀린 것) 목록 그대로 · J/K 안내 다시 {r}')
    await pg.evaluate("document.querySelector('#jbbar [data-qf=\"\"]').click()"); await pg.wait_for_timeout(200)
    # ---- B38 다른 화면 반대 판정은 새 기록
    await go(pg, '#/CONS/_jb/_jb', '#cards .qc')
    id1 = await pg.evaluate("__h.JB.vis[1].dataset.id")
    await pg.evaluate(f"__h.mark('{id1}','ng','set')"); await go(pg, '#/CONS/WHT/jb', '#cards .qc')
    await pg.evaluate(f"__h.mark('{id1}','ok','set')")
    lg = await pg.evaluate(f"JSON.parse(localStorage.getItem('jblhub.v1.mk.CONS')).log['{id1}'].map(x=>x.r)")
    ok(lg == ['ng', 'ok'], f'B38 다른 화면의 반대 판정(20초 안) = 새 기록 {lg}')
    await pg.evaluate(f"__h.mark('{id1}','ng','set')")
    lg = await pg.evaluate(f"JSON.parse(localStorage.getItem('jblhub.v1.mk.CONS')).log['{id1}'].map(x=>x.r)")
    ok(lg == ['ng', 'ng'], f'B38 같은 화면 20초 안 다시 매김 = 고침 {lg}')
    # ---- B18 형광펜 모드 중 ⭐ 연도 칩
    await go(pg, '#/CONS/WHT/learn', '#stage .tc')
    await pg.keyboard.press('h'); await pg.evaluate("(()=>{const c=document.querySelector('#stage .c-exam .jbchip[data-go]');c.scrollIntoView({block:'center'});c.id='ux4jc';})()")
    await pg.click('#ux4jc'); await pg.wait_for_timeout(300)
    r = await pg.evaluate("[location.hash,!!document.querySelector('#jbpeek.on')]"); await pg.keyboard.press('Escape'); await pg.keyboard.press('Escape')
    ok(r[0].endswith('/WHT/learn') and r[1], f'B18 형광펜 모드 중 연도 칩 → 미리보기(기출 탭으로 안 감) {r}')
    ok(await pg.evaluate("parseInt(getComputedStyle(document.querySelector('.jbpeek')||document.body).zIndex)||0") < await pg.evaluate("parseInt(getComputedStyle(document.querySelector('#dtabs')).zIndex)"), 'B36 미리보기 z-index < 탭 줄')
    # ---- B15 집중 모드 / 검색
    await pg.keyboard.press('v'); await pg.wait_for_timeout(300); await pg.keyboard.press('/'); await pg.keyboard.type('ab'); await pg.wait_for_timeout(200)
    r = await pg.evaluate("[document.activeElement&&document.activeElement.id,document.querySelector('#gsearch').value,__h.Kit.mode(),getComputedStyle(document.querySelector('#top')).display]")
    ok(r[0] == 'gsearch' and r[1] == 'ab' and r[2] is None and r[3] != 'none', f'B15 집중 모드 / → 검색칸에 글자(단축키 아님) {r}')
    await pg.keyboard.press('Escape'); await pg.evaluate("document.activeElement.blur()"); await pg.wait_for_timeout(200); await pg.keyboard.press('v'); await pg.wait_for_timeout(300)
    # ---- B16 그림 확대 중 뒤로
    await go(pg, '#/CONS/_home/_home', '#stage .lcard'); await pg.evaluate("__h.openDoc('CONS','WHT','learn')"); await pg.wait_for_timeout(900)
    await pg.evaluate("(()=>{const f=document.querySelector('#stage figure[data-fig],#stage img.fig');f.scrollIntoView({block:'center'});f.click();})()"); await pg.wait_for_timeout(800)
    m1 = await pg.evaluate("document.querySelector('#imgmodal').classList.contains('on')"); await pg.go_back(); await pg.wait_for_timeout(700)
    r = await pg.evaluate("[document.querySelector('#imgmodal').classList.contains('on'),document.body.classList.contains('modal-on'),location.hash]")
    ok(m1 and not r[0] and not r[1], f'B16 그림 확대 → 뒤로 = 모달 닫힘·스크롤 잠김 없음 {r}')
    # ---- B09 예상 J · B25
    await go(pg, '#/OMS1/DD1/pred', '#stage .pc')
    for _ in range(3): await pg.keyboard.press('j'); await pg.wait_for_timeout(450)
    r = await pg.evaluate("[...document.querySelectorAll('#stage .pc')].findIndex(c=>c.classList.contains('rcur'))")
    ok(r == 2, f'B09 예상 J 3번 → 셋째 카드(.rcur {r})')
    await pg.evaluate("document.querySelector('#ppills [data-pf=ng]').click()"); await pg.wait_for_timeout(200)
    ok(await pg.evaluate("!!document.querySelector('#predempty')&&document.querySelector('#predempty').offsetParent!==null"), 'B25 [틀린 것] 0개 → 안내')
    await pg.evaluate("document.querySelector('#predempty [data-predall]').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('#ppills #frev').click()"); await pg.wait_for_timeout(100)
    ok(await pg.evaluate("document.querySelector('#ppills #frev').textContent") == '답 모두 접기', 'B25 [답 모두 펼치기] → 글자 접기')
    await pg.evaluate("document.querySelector('#ppills [data-ptype=v]').click()"); await pg.wait_for_timeout(200)
    # ---- B10 필터 기억(예상 짤 변형) → 다른 화면 → 뒤로
    await pg.evaluate("__h.openDoc('OMS1','_home')"); await pg.wait_for_timeout(500); await pg.go_back(); await pg.wait_for_timeout(900)
    r = await pg.evaluate("[location.hash,(document.querySelector('#ppills [data-ptype].on')||{dataset:{}}).dataset.ptype,[...document.querySelectorAll('#stage .pc')].filter(c=>getComputedStyle(c).display!=='none').every(c=>c.dataset.ptype==='v')]")
    ok(r[0].endswith('/DD1/pred') and r[1] == 'v' and r[2], f'B10 예상 [짤 변형] → 다른 화면 → 뒤로 = 필터 그대로 {r}')
    # ---- B10·B24 정리표
    await go(pg, '#/OMS1/DD1/sum', '#stage .msum')
    await pg.evaluate("document.querySelector('#stage [data-mfilt=rep2]').click()"); await pg.wait_for_timeout(300)
    r = await pg.evaluate("(()=>{const R=[...document.querySelectorAll('#stage .msum table.mtx>tbody>tr')];let bad=0,h=null,any=false;R.forEach(r=>{if(r.classList.contains('grow')){if(h&&!any&&getComputedStyle(h).display!=='none')bad++;h=r;any=false;}else if(getComputedStyle(r).display!=='none')any=true;});if(h&&!any&&getComputedStyle(h).display!=='none')bad++;return bad})()")
    ok(r == 0, f'B24 [2회↑] 뒤 보이는 행 없는 묶음 머리 {r}')
    await pg.evaluate("__h.openDoc('OMS1','DD1','learn')"); await pg.wait_for_timeout(500); await pg.go_back(); await pg.wait_for_timeout(900)
    ok(await pg.evaluate("document.querySelector('#stage').classList.contains('mf-rep2')&&document.querySelector('#stage [data-mfilt=rep2]').classList.contains('on')"), 'B10 정리표 [2회↑] → 학습 → 뒤로 = 필터 그대로')
    # ---- B46 칩 이름·J가 전체정리표 행
    lab = await pg.evaluate("[...document.querySelectorAll('#sumtop [data-sttab]')].map(b=>b.textContent)")
    ok(all(len(x) <= 20 and '전체정리표' not in x for x in lab), f'B46 전체정리표 칩 이름 짧게 {lab}')
    await go(pg, '#/CONS/WHT/sum', '#stage .msum'); await pg.evaluate("scrollTo(0,0)"); await pg.keyboard.press('j'); await pg.wait_for_timeout(450)
    ok(await pg.evaluate("!!document.querySelector('#sumtop tr.rcur')"), 'B46 펼친 전체정리표가 있으면 J는 그 행부터')
    # ---- B08
    await go(pg, '#/GERI/PAIN/sum', '#stage .msum'); await pg.evaluate("document.querySelector('#stage [data-mdense=f]').click()"); await pg.wait_for_timeout(600)
    r = await pg.evaluate("(()=>{let n=0;document.querySelectorAll('#stage .msum td').forEach(td=>td.querySelectorAll('table.mini').forEach(t=>{if(t.getBoundingClientRect().right>td.getBoundingClientRect().right+1)n++;}));return [n,document.documentElement.scrollWidth-innerWidth]})()")
    ok(r == [0, 0], f'B08 자세히: 칸 밖 작은 표 {r[0]} · 문서 가로 넘침 {r[1]}')
    await pg.evaluate("document.querySelector('#stage [data-mdense=s]').click()")
    # ---- B12 답 가리기 × 👁
    await go(pg, '#/OMS1/_sum/_sum', '#stage table.sum')
    await pg.evaluate("document.querySelector('[data-sumhide]').click()"); await pg.wait_for_timeout(300)
    W = "[...document.querySelectorAll('#stage .tblwrap')].filter(w=>w.querySelector('table.sum'))"
    n0 = await pg.evaluate(f"{W}.map(w=>w.querySelectorAll('td.cov').length>0)")
    await pg.evaluate(f"{W}[0].querySelector('[data-covall]').click()"); await pg.wait_for_timeout(200)
    n1 = await pg.evaluate(f"{W}.map(w=>w.querySelectorAll('td.cov').length>0)")
    ok(all(n0) and not n1[0] and all(n1[1:]) and await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.sumhide'))") is True, f'B12 한 표 [모두 열기] = 그 표만(답 가리기는 켜진 채) {n1[:4]}')
    await pg.evaluate(f"(()=>{{const w={W}[1],th=[...w.querySelectorAll('thead th')].find(h=>h.dataset.col==='ans');th.querySelector('[data-cov]').click();}})()"); await pg.wait_for_timeout(200)
    ok(await pg.evaluate(f"{W}[1].querySelectorAll('td.cov').length") == 0, 'B12 답 가리기가 덮은 답 열 👁 → 한 번에 풀림')
    await pg.evaluate(f"(()=>{{const w={W}[2],th=[...w.querySelectorAll('thead th')].find(h=>h.dataset.col==='ans');th.querySelector('[data-cov]').click();}})()"); await pg.wait_for_timeout(100)
    await pg.evaluate("document.querySelector('[data-sumhide]').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('[data-sumhide]').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('[data-sumhide]').click()"); await pg.wait_for_timeout(200)
    ok(await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.sumhide'))") is False, 'B12 답 가리기 끔')
    # ---- B49 한눈표 칩 숫자
    await pg.evaluate("document.querySelector('#stage [data-sf=ng]').click()"); await pg.wait_for_timeout(300)
    r = await pg.evaluate("[...document.querySelectorAll('#sumbar [data-sgo]')].map(b=>{const w=document.getElementById(b.dataset.sgo);const n=[...w.querySelector('table.sum').tBodies[0].rows].filter(r=>getComputedStyle(r).display!=='none').length;return [+b.querySelector('b').textContent,n]})")
    ok(r and all(a == c for a, c in r), f'B49 [✗ 틀린 것만] 뒤 칩 숫자 = 보이는 행 {r[:4]}')
    await pg.evaluate("document.querySelector('#stage [data-sf=ng]').click()")
    # ---- B47 과목 비교표
    await go(pg, '#/IMPL/_tbl/_tbl', '#stage .tblwrap')
    await pg.evaluate("document.querySelector('#stage [data-tjb]').click()"); await pg.wait_for_timeout(300)
    e = await pg.evaluate("(()=>{const h=document.querySelector('#stage .tgh.tgempty');return h?h.dataset.k:null})()")
    if e:
        z = await pg.evaluate(f"document.querySelector('#tbltoc [data-tgk=\"{e}\"]').classList.contains('z')")
        await pg.evaluate(f"document.querySelector('#tbltoc [data-tgk=\"{e}\"]').click()"); await pg.wait_for_timeout(600)
        r = await pg.evaluate(f"[document.querySelector('#stage').classList.contains('only-tjb'),document.querySelectorAll('#stage .tgh.tgempty').length,Math.round(document.querySelector('#tg-{e}').getBoundingClientRect().top)]")
        ok(z and not r[0] and r[1] == 0 and 0 <= r[2] < 400, f'B47 기출 연결 표 없는 강의 칩({e}, 흐림 {z}) → 필터 풀고 이동 {r}')
    else: ok(True, 'B47 (빈 강의 없음 — 건너뜀)')
    # B27 목차 목록 휠로 닫힘
    await pg.evaluate("document.querySelector('#tbltoc [data-tgk]').click()"); await pg.wait_for_timeout(400)
    o1 = await pg.evaluate("!document.querySelector('#tbllist').hidden"); await pg.mouse.move(640, 600); await pg.mouse.wheel(0, 300); await pg.wait_for_timeout(300)
    ok(o1 and await pg.evaluate("document.querySelector('#tbllist').hidden"), 'B27 강의 칩 목록 → 스크롤하면 닫힘')
    # ---- B11 기출 대장
    await go(pg, '#/OMS1/_led/_led', '#stage table.led')
    r = await pg.evaluate("(()=>{const t=document.querySelector('#stage table.led'),x=t.closest('.tscroll')||t.parentElement;return [t.scrollWidth-x.clientWidth,document.querySelector('#stage').classList.contains('wide'),[...t.tBodies[0].rows].map(r=>r.cells[0].textContent)]})()")
    ok(r[0] <= 1 and r[1] and any('참고' in x for x in r[2]), f'B11·B48 기출 대장 교수×연도 표 넘침 {r[0]} · 넓게 · 참고 교수 행 {r[2]}')
    # ---- B20 교수 줄
    await go(pg, '#/OMS1/_home/_home', '#stage .lcard')
    t = await pg.evaluate("[...document.querySelectorAll('#stage .tsl')].map(e=>e.textContent)")
    ok(any('표본이 적어 누적' in x for x in t) and not any(re.search(r'짤 1/탈 0 → 탈형', x) for x in t), f'B20 합산이면 문구에 드러냄 {t[:3]}')
    # ---- B21 달력 + 시간 → 메뉴 숫자
    await go(pg, '#/_cal', '#calg')
    before = await pg.evaluate("(document.querySelector('#nav [data-nb=td]')||{}).textContent")
    await pg.evaluate("__h.addTime({d:new Date(Date.now()-864e5*0).toISOString().slice(0,10)&&(()=>{const d=new Date();return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2)})(),S:'CONS',D:'',min:60});__h.calView({push:false})"); await pg.wait_for_timeout(400)
    after = await pg.evaluate("(document.querySelector('#nav [data-nb=td]')||{}).textContent")
    ok(before != after or after is None, f'B21 달력에서 시간 추가 → 메뉴 오늘 숫자 {before} → {after}')
    # ---- B23 검색
    await go(pg, '#/', '#home .hsj'); await pg.fill('#gsearch', '미백'); await pg.wait_for_timeout(900)
    await pg.click('#home .res'); await pg.wait_for_timeout(800)   # 실제 누르기(검색칸에서 포커스가 빠짐)
    ok(await pg.evaluate("document.querySelector('#gsearch').value") == '', 'B23 검색 결과로 가면 검색칸 비움')
    await go(pg, '#/', '#home .hsj'); await pg.fill('#gsearch', '미백'); await pg.wait_for_timeout(900)
    ok('지금 과목 먼저' not in await pg.inner_text('#home .lead'), 'B23 홈에서 검색 = "지금 과목 먼저" 없음')
    await pg.fill('#gsearch', ''); await pg.wait_for_timeout(300); await pg.fill('#gsearch', '미'); await pg.wait_for_timeout(1100)
    ok('2글자부터' in await pg.evaluate("(document.querySelector('#toast')||{}).textContent||''"), 'B23 한 글자 → 2글자부터 안내')
    await pg.fill('#gsearch', ''); await pg.wait_for_timeout(300)
    # ---- B29 내 표시 전체 수
    await go(pg, '#/CONS/WHT/learn', '#stage .tc')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.ann.CONS')"); await go(pg, '#/CONS/WHT/learn', '#stage .tc')
    PICK = "(n=>{const L=[...document.querySelectorAll('#stage .tc li')].filter(l=>l.offsetParent&&!l.querySelector('[data-rk]')&&/[A-Za-z가-힣]{4}/.test(l.textContent));const li=L[n];li.scrollIntoView({block:'center'});const w=document.createTreeWalker(li,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){const m=/[A-Za-z가-힣]{4,}/.exec(x.nodeValue);if(m&&!x.parentElement.closest('button,.noann,[data-rk]')){const r=document.createRange();r.setStart(x,m.index+1);r.setEnd(x,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2];}}})"
    await pg.keyboard.press('h')
    for i in range(3): xy = await pg.evaluate(PICK + f'({i})'); await pg.mouse.click(xy[0], xy[1]); await pg.wait_for_timeout(120)
    await pg.keyboard.press('b'); xy = await pg.evaluate(PICK + '(4)'); await pg.mouse.click(xy[0], xy[1]); await pg.wait_for_timeout(120); await pg.keyboard.press('Escape')
    await go(pg, '#/CONS/_marks/_marks', '#stage .mkfbar')
    t = await pg.evaluate("document.querySelector('#stage .mkf[data-mkcol=\"\"] b').textContent")
    ok(t == '4', f'B29 내 표시 전체 = 4(형광 3 + 빈칸 1) · {t}')
    # ---- B50 플래시카드 × 모드
    await go(pg, '#/CONS/WHT/flash', '#fc .fcard'); await pg.keyboard.press('h')
    b0 = await pg.evaluate("document.querySelector('#fc .fcard').classList.contains('back')")
    await pg.evaluate("document.querySelector('#fcard').click()"); await pg.wait_for_timeout(200)
    r = await pg.evaluate("[document.querySelector('#fc .fcard').classList.contains('back'),(document.querySelector('#toast')||{}).textContent||'']")
    ok(r[0] == b0 and '플래시카드' in r[1], f'B50 형광펜 모드 중 카드 누름 = 안 뒤집힘·안내 {r}'); await pg.keyboard.press('Escape')
    # ---- B43 맥 = 홈 화면 추가 안내 없음(저장소 보호 안 됨이어도)
    await pg.evaluate("localStorage.removeItem('jblhub.v1.a2hsNote')"); await go(pg, '#/', '#home .hsj')
    ok(await pg.evaluate("(document.querySelector('#a2hs')||{}).textContent||''") == '', 'B43 맥 브라우저 = 아이패드 홈 화면 추가 안내 없음')
    ok(not errs, f'1280 콘솔 오류 0 {errs[:3]}')
    await ctx.close()
async def ipad(b):
    ctx = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
    await go(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('jblhub.v1.tauto','false')")
    # B11 ① 아이패드 세로 비교표 5열↑ = 카드형(가로로 잘리지 않음)
    await go(pg, '#/CONS/CRK/tbl', '#stage .tblwrap'); await pg.wait_for_timeout(600)
    r = await pg.evaluate("[...document.querySelectorAll('#stage .tblwrap')].map(w=>{const t=w.querySelector('table'),x=w.querySelector('.tscroll')||w;return [w.classList.contains('stcard'),t?Math.round(t.scrollWidth-x.clientWidth):0]})")
    ok(all(c or o <= 1 for c, o in r), f'B11 820 CRK 비교표: 넘치는 표는 카드형 {r}')
    # B28 카드형 정리표: 칸 이름으로 가린 열을 다시 풂
    await go(pg, '#/OMS1/DD1/sum', '#stage .msum'); await pg.wait_for_timeout(400)
    LAB = "(()=>{const td=[...document.querySelectorAll('#stage .msum table.mtx td[data-col=mem]')].find(x=>x.offsetParent);td.scrollIntoView({block:'center'});const r=td.getBoundingClientRect();return [r.left+30,r.top+14]})()"
    p1 = await pg.evaluate(LAB); await pg.touchscreen.tap(p1[0], p1[1]); await pg.wait_for_timeout(300)
    n1 = await pg.evaluate("document.querySelectorAll('#stage .msum td.cov[data-col=mem]').length")
    p2 = await pg.evaluate(LAB); await pg.touchscreen.tap(p2[0], p2[1]); await pg.wait_for_timeout(300)
    n2 = await pg.evaluate("document.querySelectorAll('#stage .msum td.cov[data-col=mem]').length")
    ok(n1 > 3 and n2 == 0, f'B28 카드형: 칸 이름 탭 → 열 가림 {n1} → 같은 이름 탭 → 풀림 {n2}')
    ok(not errs, f'820 콘솔 오류 0 {errs[:3]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        try:
            await mac(b); await ipad(b)
        finally:
            await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
