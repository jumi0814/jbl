"""ux4f E 회귀 — 오류 재검 2회차(n 91~118): 정리표·한눈표·기출 대장·JB 문제·한 장씩·백업 복원·형광펜/빈칸·메모·터치 대상.
틀 접기 줄·더 보기·▣ 칩·⤢ 터치 크기 · 형광펜 모드에서 가린 칸 = 열기(보이지 않는 표시 없음) · 정리표 Q · 요약 줄 누르면 세부 펼침
· 그림 창 뒤로 = 창만 닫기 · 카드형 칸 이름 판정 · 답 가리기 과목마다·'모두 열기' 중복 없음 · 이름(자세히·2회↑만·안 푼 것) · E가 👁 칸도
· 과목 홈 바로가기 확인창 없음 · 🔁 복습 뒤 메뉴 JB = 원래대로 · 🔁 수 = 필터 범위 · 위에 붙은 막대 [필터 ▾] · 검색칸 Esc
· 한 장씩 시작 1/n · 회차 요약 키보드 · 펼친 답 유지 · 검색 색인 안내 글 제외 · 버튼 글자 세로 가운데 · 인쇄에 ↩ 알약 없음
· 한 장씩 끝 = 답 접기 · 복원 뒤 ↶ 목록 비움 · 형광펜↔빈칸 바꾸기 · 메모 바로 새로고침·뒤로 · 손가락 기기 :hover 바탕 없음
맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)   (JBL_URL로 다른 허브 파일을 시험할 수 있음)"""
import os as _os, sys as _sys, re; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = _os.environ.get('JBL_URL') or J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def new(b, w, h, touch=False):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch); pg = ctx.new_page(); pg.errs = []; pg.dlg = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    def _d(d): pg.dlg.append(d.message[:40]); d.accept()
    pg.on('dialog', _d)
    pg.goto('about:blank'); pg.goto(U + '#/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')")
    return ctx, pg
def go(pg, h, wait=600):
    pg.goto('about:blank'); pg.goto(U + h)
    pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')", timeout=60000); pg.wait_for_timeout(wait)
def ready(pg, wait=600):
    pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')", timeout=60000); pg.wait_for_timeout(wait)
TOAST = "(document.querySelector('#toast')||{}).textContent||''"
VIS = "e=>!!e&&e.offsetParent!==null&&e.getBoundingClientRect().height>0"
WORD = """(sel,w)=>{const root=document.querySelector(sel);const tw=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while(n=tw.nextNode()){const i=n.nodeValue.indexOf(w);if(i>=0&&n.parentElement.offsetParent){const r=document.createRange();r.setStart(n,i);r.setEnd(n,i+w.length);const q=r.getClientRects()[0];if(q&&q.width)return [q.left+q.width/2,q.top+q.height/2];}}return null;}"""

def touch_sizes(b):
    print('== 91·116·117 터치 누름 자리')
    for w, h in [(820, 1180), (1180, 820)]:
        for route in ['#/CONS/WHT/learn', '#/ANAT/TMJ/learn']:
            ctx, pg = new(b, w, h, True); go(pg, route, 900)
            m = pg.evaluate("""(()=>{const v=e=>e&&e.offsetParent!==null;const f=document.querySelector('#stage .frame');if(!f)return null;
              return [...f.querySelectorAll('summary,.tmorebtn,.btn.sm')].filter(v).map(e=>[e.tagName+'.'+e.className,(e.textContent||'').trim().slice(0,14),Math.round(e.getBoundingClientRect().height)])})()""")
            small = [x for x in (m or []) if x[2] < 40]
            ok(m is not None and not small, f'{w} {route} 틀 안 접기 줄·더 보기 높이 40px↑ {small or len(m or [])}')
            if route.startswith('#/CONS'):
                d = pg.evaluate("(e=>e&&e.offsetParent?[Math.round(e.getBoundingClientRect().width),Math.round(e.getBoundingClientRect().height)]:null)(document.querySelector('#dfocus'))")
                ok(d is None or (d[0] >= 44 and d[1] >= 40), f'{w} ⤢ 집중 누름 자리 44×40↑ {d}')
                pg.keyboard.press('q'); pg.wait_for_timeout(400)
                q = pg.evaluate("[...document.querySelectorAll('button.qzchip')].filter(e=>e.offsetParent).map(e=>Math.round(e.getBoundingClientRect().height))")
                ok(all(x >= 40 for x in q), f'{w} ▣ n/n 열림 칩 높이 40↑ {q[:4]}')
                hv = pg.evaluate("""(()=>{let n=0;const walk=L=>{for(const r of L){if(r.cssRules&&r.type!==1){walk(r.cssRules);continue;}if(r.type===1&&/:hover/.test(r.selectorText)&&/^(#kit button:hover|#stage #jbbar \\.tg:hover|#dtabs \\.lmini button:hover)/.test(r.selectorText))n++;}};[...document.styleSheets].forEach(s=>{try{walk(s.cssRules)}catch(e){}});return n})()""")
                ok(hv == 0, f'{w} 118 손가락 기기 — 도구 막대·필터·미니바 :hover 바탕 규칙 없음 {hv}')
            ok(not pg.errs, f'{w} {route} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/WHT/learn')
    hv = pg.evaluate("""(()=>{let n=0;const walk=L=>{for(const r of L){if(r.cssRules&&r.type!==1){walk(r.cssRules);continue;}if(r.type===1&&/^#kit button:hover/.test(r.selectorText))n++;}};[...document.styleSheets].forEach(s=>{try{walk(s.cssRules)}catch(e){}});return n})()""")
    ok(hv >= 1, f'118 맥(마우스)은 :hover 그대로 {hv}'); ctx.close()

def tables(b):
    print('== 92·99 가린 칸 · 93·94·96·98 정리표 · 97 답 가리기')
    for w, h, t in [(1280, 900, False), (820, 1180, True)]:
        for key in ['h', 'b']:
            ctx, pg = new(b, w, h, t); go(pg, '#/CONS/_tbl', 900)
            pg.evaluate("(()=>{const t=document.querySelector('#tb-2 table')||document.querySelector('#stage table');const th=t.tHead.rows[0].cells[1];th.querySelector('.coveye').click();t.scrollIntoView({block:'center'})})()"); pg.wait_for_timeout(500)
            pg.keyboard.press(key); pg.wait_for_timeout(300)
            pt = pg.evaluate("(()=>{const c=[...document.querySelectorAll('#stage td.cov:not(.covo)')].find(e=>{const r=e.getBoundingClientRect();return r.top>150&&r.bottom<innerHeight-60&&e.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2))});if(!c)return null;c.id=c.id||'zcov';const r=c.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2,c.id]})()")
            if pt:
                if t: pg.touchscreen.tap(pt[0], pt[1])
                else: pg.mouse.click(pt[0], pt[1])
                pg.wait_for_timeout(500)
                r = pg.evaluate(f"(c=>[c.classList.contains('covo'),c.querySelectorAll('[data-rk]').length,document.querySelectorAll('#stage td.cov [data-rk]').length])(document.getElementById('{pt[2]}'))")
                ok(r[0] and r[2] == 0, f'{w} {key.upper()} 모드에서 가린 칸 누름 = 칸 열림 · 가린 칸에 표시 0 {r}')
            else: ok(False, f'{w} 가린 칸을 못 찾음')
            ok(not pg.errs, f'{w} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/_tbl', 900)
    pg.evaluate("(()=>{const t=document.querySelector('#tb-2 table')||document.querySelector('#stage table');t.tHead.rows[0].cells[1].querySelector('.coveye').click()})()"); pg.wait_for_timeout(300)
    n0 = pg.evaluate("document.querySelectorAll('#stage td.cov:not(.covo)').length")
    pg.mouse.move(5, 500); pg.keyboard.press('e'); pg.wait_for_timeout(300)
    n1 = pg.evaluate("document.querySelectorAll('#stage td.cov:not(.covo)').length")
    pg.keyboard.press('e'); pg.wait_for_timeout(300)
    n2 = pg.evaluate("document.querySelectorAll('#stage td.cov:not(.covo)').length")
    ok(n0 > 0 and n1 == 0 and n2 == n0, f'99 E = 👁 가린 칸도 열림, 다시 E = 원래대로 {n0}→{n1}→{n2}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # 93 정리표 Q · 플래시카드 안내
    for w, h, t in [(1280, 900, False), (820, 1180, True)]:
        ctx, pg = new(b, w, h, t); go(pg, '#/CONS/WHT/sum', 900)
        pg.evaluate("scrollTo(0,400)"); pg.wait_for_timeout(400); pg.keyboard.press('q'); pg.wait_for_timeout(400)
        r = pg.evaluate("[document.querySelectorAll('#stage .k.qzk').length,__h.QZ.on," + TOAST + "]")
        ok(r[0] > 0 and r[1] and '가리기 보기' in r[2] and '이 카드' not in r[2], f'{w} 93 정리표에서 Q = 지금 행 빨간 핵심어 가림 {r}')
        ctx.close()
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/WHT/flash', 900); pg.keyboard.press('q'); pg.wait_for_timeout(300)
    ok('플래시카드' in pg.evaluate(TOAST), f'93 플래시카드에서 Q = 뒤집기 안내 {pg.evaluate(TOAST)[:40]}'); ctx.close()
    # 94 요약 줄 + 98 이름
    ctx, pg = new(b, 1600, 900); go(pg, '#/CONS/WHT/sum', 900)
    ok(pg.evaluate("[...document.querySelectorAll('#stage [data-mfilt=rep2]')].every(b=>b.textContent.trim()==='2회↑만')"), '98 정리표 주제 필터 이름 2회↑만')
    pg.evaluate("(e=>e&&e.scrollIntoView({block:'center',behavior:'instant'}))(document.querySelector('#stage .msum td.md .sline'))"); pg.wait_for_timeout(500)
    pg.keyboard.press('h'); pg.wait_for_timeout(200)
    pt = pg.evaluate("(()=>{const s=[...document.querySelectorAll('#stage .msum td.md .sline')].find(e=>{const r=e.getBoundingClientRect();return e.offsetParent&&r.top>200&&r.bottom<innerHeight-80});if(!s)return null;s.closest('td').id='zmd';const r=s.getBoundingClientRect();return [r.left+12,r.top+r.height/2]})()")
    if pt:
        pg.mouse.click(pt[0], pt[1]); pg.wait_for_timeout(400)
        r = pg.evaluate("[document.getElementById('zmd').classList.contains('dopen')," + TOAST + "]")
        ok(r[0] and '세부를 펼쳤어요' in r[1], f'94 형광펜 모드에서 요약 줄 누름 = 그 칸 세부 펼침·안내 {r}')
    else: ok(False, '94 요약 줄을 못 찾음')
    pg.keyboard.press('h'); pg.wait_for_timeout(200)
    pg.evaluate("document.querySelector('#stage [data-mdense=f]').click()"); pg.wait_for_timeout(300)
    ok('자세히' in pg.evaluate(TOAST), f'98 [자세히] 알림 = 자세히 {pg.evaluate(TOAST)[:30]}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # 96 카드형 칸 이름 판정
    for w, h, t in [(820, 1180, True)]:
        ctx, pg = new(b, w, h, t); go(pg, '#/CONS/WHT/sum', 900)
        pt = pg.evaluate("""(()=>{for(const td of document.querySelectorAll('#stage .msum tbody tr td[data-col=key]')){const r=td.getBoundingClientRect();if(r.top<200||r.bottom>innerHeight-100)continue;
          const tw=document.createTreeWalker(td,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.nodeValue.trim()?1:3});const n=tw.nextNode();if(!n)continue;const rg=document.createRange();rg.selectNodeContents(n);const q=rg.getClientRects()[0];
          for(let y=Math.ceil(q.bottom)+1;y<r.top+40;y++)for(let x=r.left+2;x<r.left+200;x+=3){if(document.elementFromPoint(x,y)===td)return {x,y,q:[q.left,q.top,q.bottom],top:r.top,left:r.left};}}return null})()""")
        if pt:
            pg.touchscreen.tap(pt['x'], pt['y']); pg.wait_for_timeout(400)
            n = pg.evaluate("document.querySelectorAll('#stage td.cov').length")
            ok(n == 0, f'{w} 96 🔑 칸 첫 글줄 아래 빈자리 누름 = 열 가리지 않음 {n} {pt}')
            pg.touchscreen.tap(pt['left'] + 12, pt['q'][1] + (pt['q'][2] - pt['q'][1]) / 2); pg.wait_for_timeout(400)
            n = pg.evaluate("document.querySelectorAll('#stage td.cov').length")
            ok(n > 0, f'{w} 96 칸 이름(첫 줄 앞) 누름 = 열 가림 {n}')
        else: ok(True, f'{w} 96 첫 글줄 아래 td 빈자리 없음(판정 대상 없음)')
        ok(not pg.errs, f'{w} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # 97 답 가리기 과목마다
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/_sum', 900)
    pg.evaluate("document.querySelector('#stage [data-sumhide]').click()"); pg.wait_for_timeout(400)
    r = pg.evaluate("[document.querySelector('#stage [data-sumhide]').classList.contains('on'),document.querySelectorAll('#stage td.cov:not(.covo)').length,[...document.querySelectorAll('#stage .covall')].filter(e=>e.offsetParent).length]")
    ok(r[0] and r[1] > 0 and r[2] == 0, f'97 CONS 답 가리기 켬 · 표마다 모두 열기 없음 {r}')
    go(pg, '#/PHARM/_sum', 900)
    r = pg.evaluate("[document.querySelector('#stage [data-sumhide]').classList.contains('on'),document.querySelectorAll('#stage td.cov:not(.covo)').length]")
    ok(not r[0] and r[1] == 0, f'97 PHARM은 그대로(과목마다) {r}')
    pg.evaluate("localStorage.setItem('jblhub.v1.sumhide','true')"); go(pg, '#/GERI/_sum', 900)
    ok(pg.evaluate("document.querySelector('#stage [data-sumhide]').classList.contains('on')"), '97 옛 공용 값(sumhide)은 과목 값이 없을 때 그대로 이어짐')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()

def ledger(b):
    print('== 95 그림 창 뒤로')
    for w, h, t in [(1280, 900, False), (820, 1180, True)]:
        ctx, pg = new(b, w, h, t); go(pg, '#/CONS/_led', 1800)
        pg.evaluate("(()=>{const e=[...document.querySelectorAll('#stage [data-jb]')].find(e=>e.offsetParent);scrollTo(0,e.getBoundingClientRect().top+scrollY-innerHeight/2)})()"); pg.wait_for_timeout(500)
        y0 = pg.evaluate("Math.round(scrollY)")
        pg.evaluate("[...document.querySelectorAll('#stage [data-jb]')].find(e=>{const r=e.getBoundingClientRect();return e.offsetParent&&r.top>100&&r.bottom<innerHeight}).click()"); pg.wait_for_timeout(1500)
        a = pg.evaluate("[document.querySelector('#imgmodal').classList.contains('on'),"+str(y0)+"]")
        pg.evaluate("history.back()"); pg.wait_for_timeout(1200)
        r = pg.evaluate("[document.querySelector('#imgmodal').classList.contains('on'),location.hash,Math.round(scrollY)]")
        ok(a[0] and a[1] > 300 and not r[0] and r[1].startswith('#/CONS/_led') and abs(r[2] - a[1]) < 60, f'{w} 뒤로 = 그림 창만 닫힘·대장 같은 자리 {a} → {r}')
        pg.evaluate("[...document.querySelectorAll('#stage [data-jb]')].find(e=>{const r=e.getBoundingClientRect();return e.offsetParent&&r.top>100&&r.bottom<innerHeight}).click()"); pg.wait_for_timeout(1200)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(800)
        r = pg.evaluate("[document.querySelector('#imgmodal').classList.contains('on'),location.hash,!!(history.state&&history.state.modal)]")
        ok(not r[0] and r[1].startswith('#/CONS/_led') and not r[2], f'{w} Esc로 닫으면 history 칸도 지움 {r}')
        ok(not pg.errs, f'{w} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()

def jb(b):
    print('== 100~112 JB 문제·한 장씩')
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/_jb', 900)
    pg.evaluate("document.querySelector('#fone').click()"); pg.wait_for_timeout(500); pg.keyboard.press('x'); pg.wait_for_timeout(500)
    go(pg, '#/CONS/_home', 900); pg.dlg.clear()
    has = pg.evaluate("(e=>{if(!e)return false;e.click();return true})(document.querySelector('#stage [data-jbf=ng]'))"); pg.wait_for_timeout(900)
    r = pg.evaluate("[(document.querySelector('#jbbar [data-qf].on')||{}).dataset?.qf,__h.JB.vis.length]")
    ok(has and not pg.dlg and r[0] == 'ng', f'100 과목 홈 틀린 것 다시 = 확인창 없이 틀린 것 {pg.dlg} {r}')
    ctx.close()
    # 101·102
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/_jb', 900)
    pg.keyboard.press('j'); pg.wait_for_timeout(300); pg.keyboard.press('x'); pg.wait_for_timeout(500)
    pg.evaluate("(()=>{const s=document.querySelector('#fyr');s.value='23';s.dispatchEvent(new Event('change',{bubbles:true}))})()"); pg.wait_for_timeout(500)
    r = pg.evaluate("[...document.querySelectorAll('#jbbar [data-qf=due] .rvc,#jbbar [data-qf=ever] .rvc')].map(e=>e.textContent)")
    ok(r == ['0', '0'], f'102 연도 23 필터에서 🔁 복습·한 번이라도 틀림 = 0 {r}')
    go(pg, '#/CONS/_home', 900)
    pg.evaluate("document.querySelector('#stage [data-revgo]').click()"); pg.wait_for_timeout(900)
    a = pg.evaluate("[__h.JB.one,__h.JB.F.mine]")
    pg.evaluate("(document.querySelector('#nav .nvd[data-d=_jb]')||document.querySelector('#nav [data-d=_jb]')).click()"); pg.wait_for_timeout(900)
    r = pg.evaluate("[__h.JB.one,__h.JB.F.mine,__h.JB.F.yr]")
    ok(a == [True, 'due'] and r[0] is False and r[1] == '' and r[2] == '23', f'101 🔁 복습 뒤 메뉴 JB = 원래(목록·전체·연도 23) {a} → {r}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # 103 위에 붙은 막대 [필터 ▾]
    for w, h, t in [(1280, 900, False), (820, 1180, True), (1180, 820, True)]:
        ctx, pg = new(b, w, h, t); go(pg, '#/CONS/_jb', 900)
        pg.evaluate("scrollTo(0,600)"); pg.wait_for_timeout(500)
        pg.evaluate("document.querySelector('#fexp').click()"); pg.wait_for_timeout(500)
        r = pg.evaluate("[document.querySelector('#jbbar').className,document.querySelector('#jbbar .b2').checkVisibility(),document.querySelector('#fq').checkVisibility()]")
        ok(r[1] and r[2], f'{w} 103 목록 위에 붙은 막대에서 [필터 ▾] = 검색·필터 줄 보임 {r}')
        # 109 글자 세로 가운데
        d = pg.evaluate("[...document.querySelectorAll('#fexp,#fone')].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect(),g=document.createRange();g.selectNodeContents(e);const q=g.getBoundingClientRect();return Math.round((q.top+q.bottom)/2-(r.top+r.bottom)/2)})")
        ok(all(abs(x) <= 2 for x in d), f'{w} 109 [필터 ▾] 글자 세로 가운데 {d}')
        ctx.close()
    # 104 검색칸 Esc
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/_jb', 900)
    pg.evaluate("document.querySelector('#fexp').click()"); pg.wait_for_timeout(300)
    pg.click('#fq'); pg.keyboard.type('bleaching'); pg.wait_for_timeout(500); pg.keyboard.press('Escape'); pg.wait_for_timeout(200); pg.keyboard.press('j'); pg.wait_for_timeout(300)
    r = pg.evaluate("[document.activeElement&&document.activeElement.id,document.querySelector('#fq').value]")
    ok(r[0] != 'fq' and r[1] == 'bleaching', f'104 검색칸 Esc = 칸에서 나옴 · j는 검색어로 안 들어감 {r}')
    ctx.close()
    # 105 새로고침 뒤 [한 장씩] = 1/n
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/_jb', 900)
    pg.evaluate("document.querySelector('#cards .qc[data-id=Q10]').scrollIntoView({block:'start'})"); pg.wait_for_timeout(900)
    pg.reload(); ready(pg, 1200); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(500)
    pg.evaluate("document.querySelector('#fone').click()"); pg.wait_for_timeout(600)
    r = pg.evaluate("(document.querySelector('#opos')||{}).textContent||''")
    ok(r.startswith('1/'), f'105 새로고침 뒤 맨 위에서 [한 장씩] = 1번부터 {r}')
    # 107 한 장씩 펼친 답 → 정리본 → ↩
    for i in range(6): pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(120)
    pg.keyboard.press(' '); pg.wait_for_timeout(300)
    cid = pg.evaluate("__h.JB.vis[__h.JB.cur].dataset.id")
    pg.evaluate("__h.JB.vis[__h.JB.cur].querySelector('.chip.lec').click()"); pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelector('#retpill').click()"); pg.wait_for_timeout(1500)
    r = pg.evaluate(f"[(document.querySelector('#opos')||{{}}).textContent,document.querySelector('#cards .qc[data-id={cid}]').classList.contains('open')]")
    ok(r[0].startswith('7/') and r[1], f'107 한 장씩 7번 답 펼침 → 📖 → ↩ = 7번 답 그대로 {r}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # 106 회차 요약 키보드 · 111 안 푼 것 · 112 한 장씩 끝 = 답 접기
    ctx, pg = new(b, 1280, 900); go(pg, '#/CONS/WHT/jb', 900)
    pg.evaluate("document.querySelector('#fone').click()"); pg.wait_for_timeout(500)
    n = pg.evaluate("__h.JB.vis.length"); pg.keyboard.press('x'); pg.wait_for_timeout(300)
    for i in range(n): pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(120)
    st = pg.evaluate("(document.querySelector('#onesum')||{}).innerText||''")
    ok('안 푼 것' in st and '안 채점' not in st, f'111 회차 요약 = 안 푼 것 {st[:60]!r}')
    pg.evaluate("document.querySelector('#onesum [data-onesum=sng]').focus()"); pg.keyboard.press('Enter'); pg.wait_for_timeout(600)
    r = pg.evaluate("[(document.querySelector('#opos')||{}).textContent,__h.JB.vis.length]")
    ok(r[1] == 1, f'106 키보드 Enter [이번 회차 틀린 것 다시] = 틀린 1문항 새 회차 {r} (전 {n})')
    c0 = pg.evaluate("(e=>e?e.checked:null)(document.querySelector('#oauto'))")
    pg.evaluate("document.querySelector('#oauto').focus()"); pg.keyboard.press(' '); pg.wait_for_timeout(300)
    c1 = pg.evaluate("document.querySelector('#oauto').checked")
    ok(c0 is not None and c1 != c0, f'106 키보드 Space = 자동 넘김 체크 바뀜 {c0}→{c1}')
    pg.mouse.click(5, 450); pg.keyboard.press(' '); pg.wait_for_timeout(200); pg.keyboard.press(' '); pg.wait_for_timeout(200)
    pg.evaluate("document.querySelector('#fone').click()"); pg.wait_for_timeout(500)
    ok(pg.evaluate("document.querySelectorAll('#cards .qc.open').length") == 0, '112 [한 장씩 끝] = 회차 중 펼친 답 접음')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    # 108 검색 색인 · 110 인쇄
    ctx, pg = new(b, 1280, 900); go(pg, '#/?q=' + '줄바꿈만', 2500)
    t = pg.evaluate("document.body.innerText.replace(/\\s+/g,' ')")
    go(pg, '#/?q=' + 'bleaching', 2500)
    t2 = pg.evaluate("document.body.innerText.replace(/\\s+/g,' ')")
    ok(not re.search(r'JB\s*4\d\d', t) and '491' not in t and re.search(r'JB\s*\d', t2), f'108 "줄바꿈만" 검색에 JB 안내 글 안 걸림(대조 bleaching은 JB 결과 있음) {re.findall(r"JB\s*\d+", t)[:2]} {re.findall(r"JB\s*\d+", t2)[:2]}')
    go(pg, '#/CONS/_jb', 900); pg.evaluate("document.querySelector('#cards .qc[data-id=Q01] .chip.lec').click()"); pg.wait_for_timeout(1500)
    a = pg.evaluate("getComputedStyle(document.querySelector('#retpill')).display"); pg.emulate_media(media='print')
    r = pg.evaluate("getComputedStyle(document.querySelector('#retpill')).display")
    ok(a != 'none' and r == 'none', f'110 ↩ 알약 화면 {a} · 인쇄 {r}'); ctx.close()

def data(b):
    print('== 113 복원 뒤 ↶ · 114 형광펜↔빈칸 · 115 메모')
    ctx, pg = new(b, 1180, 820, True); go(pg, '#/CONS/WHT/learn', 900)
    pg.evaluate("document.querySelector('#t-WHT-3').scrollIntoView({block:'start'});scrollBy(0,-120)"); pg.wait_for_timeout(500)
    pg.keyboard.press('h'); pg.wait_for_timeout(200)
    p1 = pg.evaluate("(" + WORD + ")('#t-WHT-3','Adequate')")
    pg.mouse.click(p1[0], p1[1]); pg.wait_for_timeout(400)
    pg.evaluate("__h.autoBak(true,'t')"); pg.wait_for_timeout(800)
    p2 = pg.evaluate("(" + WORD + ")('#t-WHT-3','Non-vital')")
    pg.mouse.click(p2[0], p2[1]); pg.wait_for_timeout(500)
    u0 = pg.evaluate("Object.keys(sessionStorage).filter(k=>k.indexOf('undo.')>=0).length")
    pg.evaluate("(async()=>{const L=await __h.bkList();const x=L.sort((a,b)=>(b.at||0)-(a.at||0))[0];const r=await __h.bkLoad(x.id);await __h.studyReplace(r.data,'t');})()")
    pg.wait_for_timeout(2500); ready(pg, 1200)
    r = pg.evaluate("[Object.keys(sessionStorage).filter(k=>k.indexOf('undo.')>=0).map(k=>sessionStorage.getItem(k)),[...document.querySelectorAll('#t-WHT-3 [data-rk]')].map(e=>e.textContent)]")
    st = [x for x in r[0] if x and '"p"' in x]
    ok(u0 >= 1 and not st and 'Adequate' in ''.join(r[1]) and 'Non-vital' not in ''.join(r[1]), f'113 백업 되돌리기 뒤 ↶ 목록 비움 · 복원한 표시 {u0} {r[0][:1]} {r[1]}')
    ctx.close()
    for tch in [False, True]:
        ctx, pg = new(b, 1180, 820, tch); go(pg, '#/CONS/WHT/learn', 900)
        pg.evaluate("document.querySelector('#t-WHT-3').scrollIntoView({block:'start'});scrollBy(0,-120)"); pg.wait_for_timeout(500)
        cnt = "(()=>{const c=document.querySelector('#t-WHT-3');return [c.querySelectorAll('[data-rk=h]').length,c.querySelectorAll('[data-rk=b]').length]})()"
        def tap(w):
            p = pg.evaluate("(" + WORD + ")('#t-WHT-3','" + w + "')")
            if tch: pg.touchscreen.tap(p[0], p[1])
            else: pg.mouse.click(p[0], p[1])
            pg.wait_for_timeout(400)
        pg.keyboard.press('h'); tap('Adequate'); a = pg.evaluate(cnt)
        pg.keyboard.press('b'); tap('Adequate'); r = pg.evaluate(cnt + ".concat([" + TOAST + "])")
        ok(a == [1, 0] and r[:2] == [0, 1] and '빈칸' in r[2], f'114 {"터치" if tch else "마우스"} 빈칸 모드에서 형광펜 누름 = 빈칸으로 바뀜 {a} → {r}')
        pg.keyboard.press('h'); tap('Adequate'); r = pg.evaluate(cnt)
        ok(r == [1, 0], f'114 형광펜 모드에서 빈칸 누름 = 형광펜으로(조용히 지우지 않음) {r}')
        pg.keyboard.press('Control+z'); pg.wait_for_timeout(300); r = pg.evaluate(cnt)
        ok(r == [0, 1], f'114 ↶ 한 번 = 바꾸기 전(빈칸) {r}')
        ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    ctx, pg = new(b, 820, 1180, True); go(pg, '#/CONS/WHT/learn', 900)
    pg.evaluate("document.querySelector('#k-memo').click()"); pg.wait_for_timeout(300)
    pg.click('#memota'); pg.keyboard.type('첫 줄 abc'); pg.wait_for_timeout(1000); pg.keyboard.type(' 마지막'); pg.reload(); ready(pg, 800)
    v = pg.evaluate("localStorage.getItem('jblhub.v1.memo.CONS.WHT')")
    ok(v and '마지막' in v, f'115 메모 바로 새로고침해도 저장 {v}')
    go(pg, '#/CONS/WHT/sum', 600); go(pg, '#/CONS/WHT/learn', 600)
    pg.evaluate("location.hash='#/CONS/WHT/sum'"); pg.wait_for_timeout(800)
    pg.evaluate("(()=>{const m=document.querySelector('#memo');if(!m.classList.contains('on'))document.querySelector('#k-memo').click()})()"); pg.wait_for_timeout(300)
    pg.click('#memota'); pg.keyboard.press('End'); pg.keyboard.type(' XYZ'); pg.evaluate("history.back()"); pg.wait_for_timeout(1000)
    v = pg.evaluate("localStorage.getItem('jblhub.v1.memo.CONS.WHT')")
    ok(v and 'XYZ' in v, f'115 메모 바로 뒤로 가도 저장 {v}')
    ok(not pg.errs, f'콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()

with sync_playwright() as p:
    b = p.chromium.launch()
    for fn in [touch_sizes, tables, ledger, jb, data]:
        try: fn(b)
        except Exception as e: ok(False, f'{fn.__name__} 예외 {str(e)[:300]}')
    b.close()
print(f'RESULT {"PASS" if not fails else "FAIL"} {len(fails)}')
if fails: _sys.exit(1)
