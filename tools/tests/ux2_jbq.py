"""ux2 묶음 6 회귀(F01~F12): JB 문제 화면 — 떠올리기·암기 최적
F01 정답 보기 강조(답을 연 뒤에만 #E6F4EA)·.ln.pick 수 ≥ 한눈표 · F02 답 두 단계(1단계 높이·Space 1→2→닫기·jbdeep) ·
F03 한 장씩 넓히기(820×1180 카드 시작 y ≤ 130·도구 막대 겹침 0·끄면 원래 도구 막대·위로 쓸기 = 답) · F04 앞면은 문제만(연도 근거는 답 뒤 details·.qsub '판' 0·켜진 ✓ 채움) ·
F05 목록 키보드(맨 위에서 J×3 → 세 번째 카드 — fixB flow V06: 첫 J = 1번·O → mk.ok·순번 칩 1,2,3…·'지금 n/N' 입력 이동) · F06 필터 개수·회차 요약 '이번 회차 틀린 것 다시' ·
F07 ✗면 머묾·✓면 넘김·한 장씩 켜면 답 모두 펼치기 해제 · F08 플래시카드 기출 그림·뒷면 · F09 빈 글머리 0 · F10 예상 보기 줄·번호 나열·채점 ·
F11 인쇄(해설 안 잘림·압축 인쇄 ≤ 1/4)·압축 목록 카드 ≤ 80px · F12 보기 줄 끊김 이어 붙임.
맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치). 스크린샷 work/_tmp/ux2i_f*_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
MK = lambda s: f"JSON.parse(localStorage.getItem('jblhub.v1.mk.{s}')||'{{}}')"
SHOT = lambda n, tag: J.TMP + f'/ux2i_{n}_{tag}.png'
async def go(pg, h):
    await pg.goto('about:blank'); await pg.goto(U + h)
    await pg.wait_for_function("document.querySelector('#stage') && document.querySelector('#stage').children.length>0 && window.__h && __h.CUR && __h.CUR.s"); await pg.wait_for_timeout(400)
async def key(pg, k, w=120):
    await pg.keyboard.press(k); await pg.wait_for_timeout(w)
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: asyncio.ensure_future(d.accept())); print('==', tag)
    await pg.goto(U + '#/'); await pg.wait_for_selector('.hsj[data-s="PHARM"]'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    mac = tag == 'mac'
    # ---------- F01 정답 보기 강조 ----------
    await go(pg, '#/PHARM/_jb/_jb')
    r = await pg.evaluate("""(()=>{const c=document.querySelector('#c-RX01'),a=c.querySelector('.qtext .ln.li[data-ans]');const b0=getComputedStyle(a).backgroundColor,p0=getComputedStyle(a,'::before').content;
      c.querySelector('.acts [data-tog]').click();return {b0,p0,b1:getComputedStyle(a).backgroundColor,p1:getComputedStyle(a,'::before').content,dv:a.dataset.ans,pick:(c.querySelector('.jbans .ln.pick')||{}).textContent||''}})()""")
    ok(r['b0'] != 'rgb(230, 244, 234)' and r['b1'] == 'rgb(230, 244, 234)' and '정답 · 틀린 설명' in r['p1'] and r['dv'] == 'wrong', f"F01 RX01 열기 전 강조 없음 {r['b0']} → 연 뒤 #E6F4EA·'✗ 틀린 보기' {r['b1']} {r['p1']}")
    ok(r['pick'].startswith('정답 · 틀린 설명') and '환자에게' in r['pick'], f"F01 .ans0 아래 정답 보기 줄 {r['pick'][:40]!r}")
    if mac:
        await pg.wait_for_function("__h.plStat().pend===0&&['OMS1','CONS','IMPL','ANAT','GERI','PHARM'].every(s=>__h.PACKS[s]&&__h.PACKS[s].cards&&__h.PACKS[s].sumall!=null)", timeout=60000)   # 주소 과목(PHARM) 먼저 · 나머지 팩은 쉬는 틈에 — 모두 온 뒤에 여섯 과목을 셈(경합 없앰 · 부하가 크면 늦게 옴)
        r = await pg.evaluate("""['OMS1','CONS','IMPL','ANAT','GERI','PHARM'].map(s=>{const p=__h.PACKS[s];const c=Object.values(p.cards).filter(h=>h.indexOf('class="ln pick noann"')>=0).length,t=(p.sumall.match(/<tr[^>]*data-id="[^"]+"(?:(?!<\\/tr>).)*?class="ln pick"/g)||[]).length;return [s,c,t]})""")
        ok(all(c >= t for s, c, t in r), f"F01 카드의 .ln.pick 문항 수 ≥ 한눈표 {r}")
        # ---------- F02 1단계 높이·F04 판 0 ----------
        r = await pg.evaluate("""(()=>{const c=document.querySelector('#c-RX01');c.classList.remove('open','deep');const h0=c.offsetHeight;c.classList.add('open');const h1=c.offsetHeight;c.classList.add('deep');c.querySelectorAll('details.ab').forEach(d=>d.open=true);const h2=c.offsetHeight;c.classList.remove('open','deep');return {h0,h1,h2}})()""")
        ok(r['h1'] - r['h0'] <= 350 and r['h2'] > r['h1'] + 200, f"F02 RX01 1단계로 늘어난 높이 {r['h1'] - r['h0']} ≤ 350 · 2단계 {r['h2'] - r['h0']}")
        r = await pg.evaluate("""['OMS1','CONS','IMPL','ANAT','GERI','PHARM'].map(s=>{const d=document.createElement('div');let n=0;Object.values(__h.PACKS[s].cards).forEach(h=>{d.innerHTML=h;const q=d.querySelector('.qsub');if(q&&q.textContent.indexOf('판')>=0)n++;});return n}).reduce((a,b)=>a+b,0)""")
        ok(r == 0, f"F04 6과목 .qsub 글자에 '판' {r}건")
        # F09 빈 글머리 0(2단계로 모두 펼침)
        for s in ['PHARM', 'OMS1']:
            if s != 'PHARM': await go(pg, f'#/{s}/_jb/_jb')
            r = await pg.evaluate("""(()=>{document.querySelectorAll('#cards .qc').forEach(c=>c.classList.add('open','deep'));document.querySelectorAll('#cards details.ab').forEach(d=>d.open=true);let n=0;
              document.querySelectorAll('#cards .ans li').forEach(li=>{if(!li.offsetParent)return;const f=[...li.childNodes].find(x=>x.nodeType===1||(x.nodeType===3&&x.textContent.trim()));if(!f||f.nodeType!==1||!/^(UL|OL)$/.test(f.tagName)||f.classList.contains('kflow'))return;const cs=getComputedStyle(li);if(cs.display==='list-item'&&cs.listStyleType!=='none')n++;});
              document.querySelectorAll('#cards .qc').forEach(c=>c.classList.remove('open','deep'));return n})()""")
            ok(r == 0, f"F09 {s} 답 모두 펼친 뒤 빈 글머리 {r}")
        await go(pg, '#/PHARM/_jb/_jb')
    # ---------- F02 Space 단계(한 장씩) · F03 화면 · F07 ----------
    await pg.evaluate("document.querySelector('#frev').click()"); await pg.wait_for_timeout(100)
    ok(await pg.evaluate("document.querySelectorAll('#cards .qc.open').length>100"), 'F07 준비: 답 모두 펼치기 켬')
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(300)
    r = await pg.evaluate("(()=>{const c=__h.JB.vis[__h.JB.cur];return {open:c.classList.contains('open'),any:document.querySelectorAll('#cards .qc.open').length,frev:document.querySelector('#frev').classList.contains('on'),frevVis:!!document.querySelector('#frev').offsetParent}})()")
    ok(not r['open'] and r['any'] == 0 and not r['frev'] and not r['frevVis'], f"F07 한 장씩을 켜면 답 모두 펼치기 해제·열린 답 0·버튼 숨김 {r}")
    r = await pg.evaluate("""(()=>{const c=__h.JB.vis[__h.JB.cur],j=document.querySelector('#jbbar'),k=document.querySelector('#kit'),hero=document.querySelector('#hero');
      return {top:Math.round(c.getBoundingClientRect().top),mini:j.classList.contains('mini'),jh:j.offsetHeight,hero:!!hero.offsetParent,kitN:[...k.children].filter(x=>x.offsetParent).map(x=>x.id),acts:!!c.querySelector('.acts [data-tog]').offsetParent,keys:(document.querySelector('.onebar .okeys')||{}).textContent}})()""")
    lim = 130
    ok(r['top'] <= lim and r['mini'] and not r['hero'], f"F03 한 장씩 카드 시작 y {r['top']} ≤ {lim} · 막대 압축 {r['jh']}px · hero 숨김")
    ok('k-h' in r['kitN'] and 'k-min' not in r['kitN'] and not r['acts'], f"F03(ux4 B1-1) 도구 막대 = LS kitoff 하나(한 장씩도 그대로 보임·✎ 접힘 없음) {r['kitN']} · 카드 안 중복 버튼 숨김")
    ok('H 형광펜' in (r['keys'] or '') and 'B 빈칸' in (r['keys'] or ''), 'F03 키 안내에 H 형광펜 · B 빈칸')
    await pg.screenshot(path=SHOT('f03_one', tag))
    id0 = await pg.evaluate("__h.JB.vis[__h.JB.cur].dataset.id")
    st = "(()=>{const c=__h.JB.vis[__h.JB.cur];return (c.classList.contains('open')?1:0)+(c.classList.contains('deep')?1:0)})()"
    s = []
    for _ in range(3): await key(pg, 'Space'); s.append(await pg.evaluate(st))
    ok(s == [1, 2, 0], f"F02 Space 세 번 → 1단계 → 2단계 → 닫힘 {s}")
    await key(pg, 'Space'); await pg.wait_for_timeout(200)
    await pg.screenshot(path=SHOT('f02_stage1', tag))
    r = await pg.evaluate("""(async()=>{scrollTo(0,1e6);await new Promise(r=>setTimeout(r,250));const c=__h.JB.vis[__h.JB.cur].getBoundingClientRect(),k=document.querySelector('#kit').getBoundingClientRect(),o=document.querySelector('#onebar').getBoundingClientRect();
      return {ov:!(c.bottom<=k.top||c.top>=k.bottom||c.right<=k.left||c.left>=k.right),kb:Math.round(k.bottom),ot:Math.round(o.top)}})()""")
    ok(not r['ov'] and r['kb'] <= r['ot'], f"F03 답을 연 카드 아래가 도구 막대에 가리지 않음·도구 막대는 풀이 막대 위 {r}")
    await key(pg, 'Space'); await key(pg, 'Space')
    await pg.evaluate("localStorage.setItem('jblhub.v1.jbdeep','1')"); await key(pg, 'Space')
    ok(await pg.evaluate(st) == 2, 'F02 jbdeep=1이면 한 번에 2단계'); await key(pg, 'Space'); await pg.evaluate("localStorage.removeItem('jblhub.v1.jbdeep')")
    # 자세히 버튼 = 선호 저장
    await pg.evaluate("(()=>{const c=__h.JB.vis[__h.JB.cur];c.querySelector('.acts [data-tog]').click();c.querySelector('[data-deep]').click()})()")
    ok(await pg.evaluate("localStorage.getItem('jblhub.v1.jbdeep')") == '1' and await pg.evaluate(st) == 2, 'F02 [자세히 ▾] → 2단계·jbdeep=1 저장')
    await pg.evaluate("(()=>{const c=__h.JB.vis[__h.JB.cur];c.querySelector('[data-deep]').click();c.querySelector('.acts [data-tog]').click()})()")
    ok(await pg.evaluate("localStorage.getItem('jblhub.v1.jbdeep')") == '0', 'F02 [간단히 ▴] → jbdeep=0')
    # F07 자동 넘김: ✗ 머묾·열림 / ✓ 넘김
    await pg.evaluate("localStorage.setItem('jblhub.v1.jbauto','true')")
    await key(pg, 'x', 600)
    r = await pg.evaluate("(()=>{const c=__h.JB.vis[__h.JB.cur];return [c.dataset.id,c.classList.contains('open')]})()")
    ok(r == [id0, True], f"F07 ✗ → 0.6초 뒤에도 같은 카드·답 열림 {r}")
    await key(pg, 'o', 600)
    ok(await pg.evaluate("__h.JB.vis[__h.JB.cur].dataset.id") != id0, 'F07 ✓ → 다음 카드')
    # F03 위로 쓸기 = 답 보기(터치)
    if touch:
        c1 = await pg.evaluate("__h.JB.vis[__h.JB.cur].dataset.id")
        box = await pg.evaluate("(()=>{const r=__h.JB.vis[__h.JB.cur].querySelector('.qtext').getBoundingClientRect();return [r.left+r.width/2,r.top+Math.min(r.height-10,120)]})()")
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': box[0], 'y': box[1]}]})
        for i in range(1, 6): await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': box[0], 'y': box[1] - 100 * i / 5}]}); await pg.wait_for_timeout(16)
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); await pg.wait_for_timeout(250)
        r = await pg.evaluate("(()=>{const c=__h.JB.vis[__h.JB.cur];return [c.dataset.id,c.classList.contains('open')]})()")
        ok(r == [c1, True], f"F03 카드 위로 쓸기 → 답 보기 {r}")
    # F03 → ux4 B1-1: 풀이 막대의 [✎ 도구]로 도구 막대를 끄고 켬(LS kitoff 하나 — 한 장씩을 끄면 그 상태 그대로)
    await pg.evaluate("document.querySelector('#onebar [data-kitt]').click()"); await pg.wait_for_timeout(150)
    ok(await pg.evaluate("getComputedStyle(document.querySelector('#kit')).display==='none' && localStorage.getItem('jblhub.v1.kitoff')==='true' && document.querySelector('#onebar [data-kitt]').getAttribute('aria-pressed')==='false'"), 'F03 풀이 막대 [✎ 도구] → 도구 막대 숨김(LS kitoff)')
    await pg.evaluate("document.querySelector('#onebar [data-kitt]').click()"); await pg.wait_for_timeout(150)
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(250)
    r = await pg.evaluate("({one:document.body.classList.contains('jbone'),kit:[...document.querySelector('#kit').children].filter(x=>x.offsetParent).length,koff:localStorage.getItem('jblhub.v1.kitoff')})")
    ok(not r['one'] and r['kit'] > 3 and r['koff'] == 'false', f"F03 한 장씩 끄면 도구 막대 그대로(LS kitoff) {r}")
    # ---------- F06 개수·회차 요약 ----------
    await pg.evaluate("localStorage.removeItem('jblhub.v1.mk.PHARM');sessionStorage.clear();localStorage.removeItem('jblhub.v1.jbst.PHARM._jb')")
    await go(pg, '#/PHARM/_jb/_jb')
    QN = "(()=>Object.fromEntries([...document.querySelectorAll('#jbbar [data-qf]')].map(b=>[b.dataset.qf,+(b.querySelector('.qn')||{textContent:'-1'}).textContent])))()"
    q0 = await pg.evaluate(QN)
    await pg.evaluate("document.querySelector('#c-RX02 .acts [data-mk=\"ng\"]').click()"); await pg.wait_for_timeout(100)
    q1 = await pg.evaluate(QN)
    ok(q1['ng'] == q0['ng'] + 1 and q1['todo'] == q0['todo'] - 1 and q0[''] == 157, f"F06 ✗ 하나 → '틀린 것' {q0['ng']}→{q1['ng']} · 안 푼 것 {q0['todo']}→{q1['todo']}")
    await pg.select_option('#fprof', index=1); await pg.wait_for_timeout(150)
    q2 = await pg.evaluate(QN); ok(q2[''] < 157 and q2['todo'] <= q2[''], f"F06 교수를 고르면 그 범위 안에서 셈 {q2}")
    await pg.select_option('#fprof', index=0); await pg.wait_for_timeout(150)
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(250)
    for k in ['x', 'ArrowRight', 'o', 'x', 'ArrowRight', 'o']: await key(pg, k, 350)
    await pg.evaluate("(()=>{__h.JB.cur=__h.JB.vis.length;__h.JB.show();})()"); await pg.wait_for_timeout(150)
    r = await pg.evaluate("(()=>{const S=__h.JB.sess;return {ng:S.ids.filter(i=>S[i]==='ng'),t:document.querySelector('#onesum').innerText}})()")
    nall = await pg.evaluate("(()=>{const m=__h.getMK('PHARM');return Object.keys(m.ng).filter(i=>__h.PACKS.PHARM.cards[i]).length})()")
    ok(len(r['ng']) == 2 and '이번 회차 틀린 것 2 다시' in r['t'] and f'전체 틀린 것 {nall}' in r['t'] and '안 채점 153' in r['t'] and '처음부터' in r['t'], f"F06 회차 요약 버튼 {r['t'][-80:]!r}")
    await pg.screenshot(path=SHOT('f06_sum', tag))
    await pg.evaluate("document.querySelector('[data-onesum=\"sng\"]').click()"); await pg.wait_for_timeout(200)
    r2 = await pg.evaluate("__h.JB.sess.ids")
    ok(r2 == r['ng'] and await pg.inner_text('#opos') == '1/2', f"F06 이번 회차 틀린 것 다시 → 새 회차 = 이번 회차 ✗ {r2}")
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(200)
    # ---------- F05 목록 키보드·순번·지금 n/N ----------
    await pg.evaluate("localStorage.removeItem('jblhub.v1.mk.PHARM');sessionStorage.clear();localStorage.removeItem('jblhub.v1.jbst.PHARM._jb')")
    await go(pg, '#/PHARM/_jb/_jb')
    i0 = await pg.evaluate("__h.JB.lc?__h.JB.vis.indexOf(__h.JB.lc):-1")   # 화면 위 30% 선에 걸친 카드가 이미 '지금 카드'면(세로 화면) 거기서부터
    for _ in range(3): await key(pg, 'j', 350)
    r = await pg.evaluate("(()=>{const v=__h.JB.vis,c=v[%d]," % (i0 + 3 if i0 >= 0 else 2) + "t=c.getBoundingClientRect().top;return {id:c.dataset.id,t:Math.round(t),line:Math.round(parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--toph'))+parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--tabh'))),cur:c.classList.contains('cur2'),lc:__h.JB.lc===c}})()")
    ok(r['cur'] and r['lc'] and r['line'] < r['t'] < r['line'] + 200, f"F05 맨 위에서 j 세 번 → 세 번째 카드({r['id']})가 탭 아래 y {r['t']}")
    await key(pg, 'o', 150)
    ok((await pg.evaluate(MK('PHARM'))).get('ok', {}).get(r['id']) == 1, f"F05 o → 그 카드 mk.ok[{r['id']}]")
    await key(pg, 'Space', 200)
    ok(await pg.evaluate("__h.JB.lc.classList.contains('open')"), 'F05 Space → 지금 카드 답 1단계')
    await key(pg, 'k', 350); ok(await pg.evaluate("__h.JB.lc===__h.JB.vis[%d]" % (i0 + 2 if i0 >= 0 else 1)), 'F05 k → 이전 카드')
    await pg.screenshot(path=SHOT('f05_list', tag))
    # 지금 n/N 입력 이동
    await pg.evaluate("scrollBy(0,400)"); await pg.wait_for_function("document.querySelector('#jbbar').classList.contains('mini')")
    await pg.click('#fnow'); await pg.fill('#fnowi', '40'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(400)
    r = await pg.evaluate("(()=>{const c=__h.JB.vis[39];return {t:Math.round(c.getBoundingClientRect().top),now:document.querySelector('#fnow').textContent,h:document.querySelector('#fnow').hidden}})()")
    ok(0 < r['t'] < 300 and r['now'].startswith('지금 40') and not r['h'], f"F05 '지금 n/157' 입력 40 → 40번째 카드로 {r}")
    await pg.screenshot(path=SHOT('f05_mini', tag))
    # 강의 기출 탭(많이 나온 순) 순번 칩
    await go(pg, '#/PHARM/RX/jb')
    r = await pg.evaluate("[...document.querySelectorAll('#cards .qc:not(.hid)')].sort((a,b)=>a.getBoundingClientRect().top-b.getBoundingClientRect().top).map(c=>c.querySelector('.chip.seq').textContent)")
    ok(all(x == f'{i + 1}/{len(r)}' for i, x in enumerate(r)) and len(r) > 5, f"F05 강의 기출 탭 순번 칩 {r[:4]}…")
    # ---------- F04 앞면·버튼 ----------
    await go(pg, '#/OMS1/DD1/jb')
    r = await pg.evaluate("""(()=>{const cs=__h.JB.vis;const c=cs.find(x=>x.querySelector('.srcd .note'))||cs[0];const v0=c.innerText.indexOf('연도 표기 근거')>=0,n=c.querySelector('.srcd .note');const f0=c===cs[0];
      c.querySelector('.acts [data-tog]').click();const s=c.querySelector('.srcd>summary');return {f0,id:c.dataset.id,v0,inD:!!(n&&n.closest('details.srcd')),sum:!!(s&&s.offsetParent),vchip:[...c.querySelectorAll('.qhead .chip[class*=v-]')].map(x=>!!x.offsetParent)}})()""")
    ok(not r['v0'] and r['inD'] and r['sum'], f"F04 OMS1 DD1 기출 탭 {'첫 ' if r['f0'] else ''}카드 {r['id']}: 답을 열기 전 '연도 표기 근거' 안 보임 → 연 뒤 details '출처·연도 근거' 안")
    await pg.screenshot(path=SHOT('f04_front', tag))
    r = await pg.evaluate("(()=>{const c=__h.JB.vis[1];const b=c.querySelector('.acts [data-mk=ok]'),cs=()=>getComputedStyle(b);const before=[cs().borderTopColor,cs().fontWeight];b.click();return [before,[cs().borderTopColor,cs().fontWeight,cs().backgroundColor,cs().color],cs().borderTopStyle,Math.round(b.getBoundingClientRect().height)]})()")
    ok(r[0] != r[1][:2] and r[1] == ['rgb(35, 33, 29)', '700', 'rgb(255, 255, 255)', 'rgb(35, 33, 29)'] and r[2] == 'solid' and (not touch or r[3] >= 44), f"F04(ux4 B3-6) ✓ 맞음 테두리 버튼 → 켜지면 ink 테두리·굵게(채움 없음) {r}")
    # ---------- F08 플래시카드 기출 그림·뒷면 ----------
    await go(pg, '#/OMS1/DX/flash')
    r = await pg.evaluate("""(async()=>{const F=__h.Flash;F.filter('기출');const i=F.deck.findIndex(c=>c.key==='J:Q35');F.i=i;F.back=false;F.draw();const im=document.querySelector('#fcard img');if(!im)return {i,img:0};try{await im.decode()}catch(e){};return {i,img:im.naturalWidth,mh:getComputedStyle(im).maxHeight}})()""")
    ok(r['i'] >= 0 and r['img'] > 0, f"F08 OMS1 DX 플래시카드 기출 Q35 앞면 그림 naturalWidth {r}")
    await pg.screenshot(path=SHOT('f08_front', tag))
    await pg.evaluate("__h.Flash.flip()"); await pg.wait_for_timeout(100)
    r = await pg.evaluate("({a0:document.querySelectorAll('#fcard .fca .ln').length,go:(document.querySelector('#fcard [data-go]')||{}).textContent||''})")
    ok(r['a0'] and '문제 카드로' in r['go'], f"F08 뒷면 JB 답 줄·'📝 문제 카드로' {r}")
    await pg.screenshot(path=SHOT('f08_back', tag))
    await pg.evaluate("document.querySelector('#fcard [data-go]').click()"); await pg.wait_for_timeout(600)
    ok(await pg.evaluate("location.hash.indexOf('/OMS1/DX/jb')>=0 && !!document.querySelector('#c-Q35')"), 'F08 문제 카드로 → 강의 기출 탭 그 문항')
    # ---------- F10 예상문제 ----------
    HUB = "[...document.querySelectorAll('.hsj[data-s=\"PHARM\"] .hcr,.hsj[data-s=\"PHARM\"] .hcj')].map(x=>x.title+' '+x.textContent).join(' | ')"   # ux3 H4 과목 표
    await pg.goto('about:blank'); await pg.goto(U + '#/'); await pg.wait_for_selector('.hsj[data-s="PHARM"] .hcj'); hub0 = await pg.evaluate(HUB)
    await go(pg, '#/PHARM/_pred')
    r = await pg.evaluate("""(()=>{const p=document.querySelectorAll('#stage .pc')[1];const d=document.createElement('div');d.innerHTML=__h.PACKS.PHARM.preds[1].html;
      return {li:p.querySelectorAll('.pq .ln.li').length,q1:!!p.querySelector('.pq .ln.q1'),lone:[...d.querySelectorAll('.pre2 li')].filter(l=>/^[①-⑩]$/.test(l.textContent.trim())).length}})()""")
    ok(r['li'] == 4 and r['q1'] and r['lone'] == 0, f"F10 PHARM 예상 두 번째 카드 보기 4줄·발문 .q1 · 답 목록 '②' 단독 li {r['lone']}")
    pid = await pg.evaluate("document.querySelectorAll('#stage .pc')[1].dataset.id")
    await pg.evaluate("document.querySelectorAll('#stage .pc')[1].querySelector('.acts [data-mk=ng]').click()"); await pg.wait_for_timeout(100)
    m = await pg.evaluate(MK('PHARM'))
    ok(pid.startswith('P:') and m.get('ng', {}).get(pid) == 1, f"F10 예상 카드 ✗ → mk.ng['{pid[:24]}…']")
    await pg.evaluate("document.querySelector('#ppills [data-pf=ng]').click()"); await pg.wait_for_timeout(100)
    ok(await pg.evaluate("[...document.querySelectorAll('#stage .pc')].filter(p=>p.offsetParent).map(p=>p.dataset.id)") == [pid], "F10 예상 '틀린 것' 필터 = 그 카드만")
    await pg.evaluate("document.querySelector('#ppills [data-pf=todo]').click()"); await pg.wait_for_timeout(100)
    ok(await pg.evaluate("[...document.querySelectorAll('#stage .pc')].filter(p=>p.offsetParent).length") == await pg.evaluate("document.querySelectorAll('#stage .pc').length-1"), "F10 예상 '안 푼 것' 필터")
    await pg.screenshot(path=SHOT('f10_pred', tag))
    await pg.goto('about:blank'); await pg.goto(U + '#/'); await pg.wait_for_selector('.hsj[data-s="PHARM"] .hcj'); hub1 = await pg.evaluate(HUB)
    ok(hub0 == hub1, f"F10 예상 채점 뒤 허브 과목 카드 기출 개수 그대로 {hub1!r}")
    # ---------- F11 인쇄·압축 목록 ----------
    await go(pg, '#/PHARM/_jb/_jb')
    await pg.emulate_media(media='print')
    r = await pg.evaluate("""(()=>{const c=document.querySelector('#c-RX01'),e=c.querySelector('.exw');return {mh:getComputedStyle(e).maxHeight,more:getComputedStyle(c.querySelector('.exmore')).display,disp:getComputedStyle(e).display,h:document.documentElement.scrollHeight}})()""")
    ok(r['mh'] == 'none' and r['more'] == 'none' and r['disp'] != 'none', f"F11 인쇄: 첫 카드 해설 안 잘림·'해설 전체 보기' 없음 {r}")
    hc = await pg.evaluate("(()=>{document.body.classList.add('prc');const h=document.documentElement.scrollHeight;document.body.classList.remove('prc');document.body.classList.add('prq');const q=document.documentElement.scrollHeight;document.body.classList.remove('prq');return [h,q]})()")
    ok(hc[0] * 4 <= r['h'] and hc[1] < hc[0], f"F11 압축 인쇄 높이 {hc[0]} ≤ 일반 인쇄 {r['h']}의 1/4 · 시험지 {hc[1]}")
    if mac:
        await pg.evaluate("document.body.classList.add('prc')"); await pg.screenshot(path=SHOT('f11_print_prc', tag)); await pg.evaluate("document.body.classList.remove('prc')")
    await pg.emulate_media(media='screen')
    await pg.evaluate("document.querySelector('#fmenu').click()"); await pg.wait_for_selector('#jbmenu')
    await pg.screenshot(path=SHOT('f11_menu', tag))
    await pg.evaluate("document.querySelector('#jbmenu [data-jbm=list]').click()"); await pg.wait_for_timeout(250)
    r = await pg.evaluate("(()=>{const v=__h.JB.vis;const hs=v.slice(0,12).map(c=>c.offsetHeight);const a=v[0].querySelector('.lxa');return {on:document.querySelector('#stage').classList.contains('jblist'),ls:localStorage.getItem('jblhub.v1.jblist'),max:Math.max(...hs),a:a&&a.textContent.slice(0,30)}})()")
    ok(r['on'] and r['ls'] == '1' and (not mac or r['max'] <= 80) and r['a'], f"F11 압축 목록: 카드 높이 최대 {r['max']}px{' ≤ 80' if mac else ''} · 답 한 줄 {r['a']!r}")
    await pg.screenshot(path=SHOT('f11_list', tag))
    await pg.evaluate("__h.JB.vis[2].querySelector('.qtext').click()"); await pg.wait_for_timeout(150)
    ok(await pg.evaluate("__h.JB.vis[2].classList.contains('lx') && __h.JB.vis[2].offsetHeight>120"), 'F11 압축 목록에서 누르면 카드 펼침')
    await go(pg, '#/PHARM/_jb/_jb')
    ok(await pg.evaluate("document.querySelector('#stage').classList.contains('jblist')"), 'F11 압축 목록 선호 유지(LS jblist)')
    await pg.evaluate("document.querySelector('#fmenu').click()"); await pg.evaluate("document.querySelector('#jbmenu [data-jbm=list]').click()"); await pg.wait_for_timeout(150)
    ok(not await pg.evaluate("document.querySelector('#stage').classList.contains('jblist')"), 'F11 압축 목록 끄기')
    # ---------- F12 보기 줄 이어 붙임 ----------
    r = await pg.evaluate("[...document.querySelectorAll('#c-XE02 .qtext .ln')].map(l=>l.textContent)")
    ok(any(x.startswith('5)') and x.endswith('0.2ml/min 이면 정상이다.') for x in r) and len(r) == 6, f"F12 XE02 보기 5)가 한 줄 {r[-1]!r}")
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), '가로 넘침 없음')
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 820, 'height': 1180}, True, 'ipadp')
        await run(b, {'width': 1180, 'height': 820}, True, 'ipadl')
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
