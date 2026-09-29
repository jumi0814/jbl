"""ux3 묶음 H 회귀 — 허브 홈 '오늘' 대시보드.
H1 섹션 5개 순서(띠 → 이어서|할 일 → 과목 표 → 이번 주 → 더보기)·.scard 없음 · H2 오늘 띠(ux4 B1-6: 시험일이 있어도 D-n·시험일 넣기 없음 · 막대 폭 = 오늘/목표) ·
H3 todayTasks 규칙·순서(🔁 복습 → 📝 최근 과목 안 푼 기출 → ✗ 틀린 기출(복습과 겹치면 뺌) → 💾 백업 — 시험 하루 분량 줄 없음)·각 ▶ 라우트·메뉴 🏠 배지·시계 팝업 ·
H4 과목 표 7행·ESTH·시험 칸·✎·기본/시험순 없음(LS exam.<S>·homeSort는 그대로)·행 → 과목 홈 · H5 이번 주 합계 = 시계 팝업 주 합계·막대 → 그날 달력·더보기 details ·
H6 과목 홈 시험일 줄 없음·순서 유지·'📅 이 과목 달력' · 세 폭 가로 넘침 0 · 1180 메뉴 펼침에서 띠·이어서·할 일이 첫 화면.
맥 1280×900 + 아이패드 가로 1180×820·세로 820×1180(터치). 스크린샷 work/_tmp/ux3h_{1280,1180,820}.png · ux3i_h_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, datetime, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, wait=300):
    await pg.goto('about:blank'); await pg.goto(U + h)
    await pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&(document.querySelector('#home .hub .hsj[data-s]')||document.querySelector('#stage [data-aid],#stage .guide,#stage #cards,.cal'))", timeout=30000)
    await pg.wait_for_timeout(wait)
def dd(n): return (datetime.date.today() + datetime.timedelta(days=n)).isoformat()
SEED = """(a)=>{const NS='jblhub.v1.',S=(k,v)=>localStorage.setItem(NS+k,JSON.stringify(v)),P=__h.PACKS,now=Date.now(),D=864e5;
 S('exam.CONS',a.c);S('exam.ANAT',a.a);
 const ids=s=>P[s].order.filter(id=>(P[s].refids||[]).indexOf(id)<0);
 const m={ok:{},ng:{},bm:{},log:{}};ids('CONS').slice(0,3).forEach((id,i)=>{m.ng[id]=1;m.log[id]=[{r:'ng',t:now-(i+1)*60e3}];});S('mk.CONS',m);
 const lb={CONS:{s:'CONS',d:P.CONS.lect[0].k,t:'sum',aid:'',off:0,at:now-3600e3,ti:'카드 제목'},ANAT:{s:'ANAT',d:P.ANAT.lect[1].k,t:'learn',aid:'',off:0,at:now-2*3600e3},PHARM:{s:'PHARM',d:P.PHARM.lect[0].k,t:'jb',aid:'',off:0,at:now-3*3600e3}};
 S('lastBy',lb);S('last',lb.CONS);S('lastBackup',now-10*D);
 const t={};t[a.t0]={CONS:3600e3,ANAT:1800e3};S('time',t);}"""
TASKS = "__h.todayTasks().map(x=>x.k+':'+(x.S||''))"
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    print('==', tag); W = vp['width']; narrow = W <= 860
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await open_(pg, '#/')
    # ---- H1 구성
    secs = await pg.evaluate("[...document.querySelectorAll('#home .hub>.hsec')].map(e=>e.classList[1])")
    ok(secs == ['hband', 'hduo', 'hsubj', 'hweek', 'hxtra'], f'{tag} H1 섹션 순서 {secs}')
    ok(await pg.evaluate("!document.querySelector('#home .scard,#home .sgrid,#home .lead,#home .todayb,#home .htime')"), f'{tag} H1 옛 과목 카드·lead·옛 띠·최근 시간 표 없음')
    # ---- H2 띠: 시험일 넣기·D-n 없음(ux4 B1-6) · 첫 과목 안 푼 기출 · 시험일 안내 줄 없음
    bt = await pg.inner_text('#home .hband')
    ok('시험' not in bt and not re.search(r'D-\d', bt), f'{tag} H2 띠에 시험·D-n 없음 ({bt[:40]!r})')
    tk0 = await pg.evaluate(TASKS)
    ok(tk0 == ['jb:OMS1'] and '시험일' not in await pg.inner_text('#home .htodo'), f'{tag} H3 빈 기록: 첫 과목 안 푼 기출 · 시험일 안내 없음 {tk0}')
    # ---- 시드: 복습 3(CONS) · 시험 CONS D-2·ANAT D-6 · 백업 10일 전 · 이어서 3 · 오늘 시간
    await pg.evaluate(SEED, {'c': dd(2), 'a': dd(6), 't0': dd(0)}); await open_(pg, '#/')
    tk = await pg.evaluate(TASKS)
    ok(tk == ['rev:CONS', 'jb:CONS', 'bk:'], f'{tag} H3 할 일 순서(시험일이 있어도 시험 줄 없음) {tk}')
    li = await pg.evaluate("[...document.querySelectorAll('#home .htodo .htk')].map(b=>b.dataset.todo+':'+b.dataset.ts)")
    ok(li == tk, f'{tag} H3 홈 ✅ 목록 = todayTasks {li}')
    tx = await pg.inner_text('#home .htodo')
    ok('복습 3문항' in tx and 'D-' not in tx and '보존 안 푼 기출' in tx and '최근 공부한 과목' in tx and '백업 10일 전' in tx, f'{tag} H3 문구 ({tx[:160]!r})')
    ok(await pg.evaluate("__h.examPlan('CONS')") is None, f'{tag} H3 하루 분량 계산 없음(examPlan null)')
    nb = await pg.evaluate("(document.querySelector('#nav [data-nb=tk]')||{}).textContent")
    ok(nb == '3', f'{tag} H3 메뉴 🏠 오늘 배지 = 할 일 수 {nb!r}')
    bt = await pg.inner_text('#home .hband')
    ok('D-2' not in bt and '가장 가까운 시험' not in bt, f'{tag} H2 시험일이 있어도 띠에 D-n 없음 ({bt[:60]!r})')
    pc = await pg.evaluate("d=>{const td=Object.values(__h.tDay(d)).reduce((a,b)=>a+b,0);return [Math.min(100,Math.round(td/(__h.tGoal(d)*60000)*100))+'%',document.querySelector('#home [data-hbw]').style.width,!document.querySelector('#home [data-hb=pct]')]}", dd(0))
    ok(pc[0] == pc[1] and pc[2], f'{tag} H2 막대 폭 = 오늘/목표 · % 글자 없음 {pc}')
    await pg.screenshot(path=J.TMP + f'/ux3h_{W}.png'); await pg.screenshot(path=J.TMP + f'/ux3i_h_{tag}_full.png', full_page=True)
    # 1180 메뉴 펼침·1280: 띠·이어서·할 일이 첫 화면에(스크롤 없이)
    if not narrow:
        bot = await pg.evaluate("Math.max(...['.hband','.hres','.htodo'].map(q=>document.querySelector('#home '+q).getBoundingClientRect().bottom))")
        ok(bot <= vp['height'], f'{tag} H3 띠·이어서·할 일 바닥 {bot:.0f} ≤ {vp["height"]} (메뉴 펼침 {await pg.evaluate("!document.body.classList.contains(\'sidefold\')")})')
    # 가로 넘침 0 · 칸 넘침 0
    ov = await pg.evaluate("(()=>{const r=[document.documentElement.scrollWidth-innerWidth];document.querySelectorAll('#home .hsj,#home .hband,#home .htodo,#home .hres,#home .hweek').forEach(e=>{if(e.scrollWidth>e.clientWidth+1)r.push(e.className+':'+(e.scrollWidth-e.clientWidth));});return r})()")
    ok(ov[0] <= 0 and len(ov) == 1, f'{tag} H4 가로 넘침 0 {ov}')
    # 시계 팝업 — 같은 목록 앞 3
    await pg.evaluate("document.querySelector('#clock').click()"); await pg.wait_for_timeout(250)
    pt = await pg.evaluate("[...document.querySelectorAll('#tpop .tptodo [data-todo]')].map(b=>b.dataset.todo+':'+b.dataset.ts)")
    ok(pt == tk[:3], f'{tag} H3 시계 팝업 할 일 3 {pt}')
    await pg.evaluate("document.querySelector('#tpop .tptodo [data-todo=jb]').click()"); await pg.wait_for_timeout(700)
    ok((await pg.evaluate('location.hash')).startswith('#/CONS/_jb') and not await pg.evaluate("document.querySelector('#tpop').classList.contains('on')"), f'{tag} H3 팝업 📝 → JB·팝업 닫힘')
    # 각 ▶ 라우트
    async def todo(k, S=''):
        await open_(pg, '#/'); await pg.evaluate("([k,S])=>document.querySelector(`#home .htodo [data-todo=${k}]`+(S?`[data-ts=${S}]`:'')).click()", [k, S]); await pg.wait_for_timeout(900)
        return await pg.evaluate("[location.hash,document.body.classList.contains('jbone'),__h.JB&&__h.JB.F?__h.JB.F.mine:'',document.querySelector('#bkpop').classList.contains('on')]")
    r = await todo('rev'); ok(r[0].startswith('#/CONS/_jb') and r[1] and r[2] == 'due', f'{tag} H3 🔁 → CONS 복습 한 장씩 {r}')
    r = await todo('jb'); ok(r[0].startswith('#/CONS/_jb') and r[2] == 'todo', f'{tag} H3 📝 → CONS 안 푼 것 필터 {r}')
    r = await todo('bk'); ok(r[0] in ('#/', '') and r[3], f'{tag} H3 💾 → 백업 창 {r}')
    # ④ 틀린 기출 — 복습에 없는 틀림(틀림 표시 + 맞음 기록만: 옛 판 재채점)이 있을 때만 · 복습과 겹치면 뺌
    await pg.evaluate("(()=>{const P=__h.PACKS.PHARM,id=P.order.filter(i=>(P.refids||[]).indexOf(i)<0)[0],m={ok:{},ng:{},bm:{},log:{}};m.ng[id]=1;m.log[id]=[{r:'ok',t:Date.now()-5*864e5}];localStorage.setItem('jblhub.v1.mk.PHARM',JSON.stringify(m));localStorage.setItem('jblhub.v1.lastBackup',JSON.stringify(Date.now()));})()")
    await open_(pg, '#/'); tk2 = await pg.evaluate(TASKS)
    ok('ng:PHARM' in tk2 and 'bk:' not in tk2, f'{tag} H3 ✗ 틀린 기출(복습 밖 틀림 PHARM) · 백업 오늘 → 백업 줄 없음 {tk2}')
    r = await todo('ng'); ok(r[0].startswith('#/PHARM/_jb') and r[1] and r[2] == 'ng', f'{tag} H3 ✗ → 틀린 것 한 장씩 {r}')
    # ---- H4 과목 표
    await open_(pg, '#/')
    rows = await pg.evaluate("[...document.querySelectorAll('#home .hsj')].map(r=>r.dataset.s||('off:'+r.dataset.off))")
    ok(len(rows) == 7 and rows[-1] == 'off:ESTH' and '자료 준비 중' in await pg.inner_text('#home .hsj.off[data-off=ESTH]'), f'{tag} H4 7행·ESTH 흐린 행 {rows}')
    rh = await pg.evaluate("Math.min(...[...document.querySelectorAll('#home .hsj[data-s]')].map(r=>r.getBoundingClientRect().height))")
    ok(rh >= 50, f'{tag} H4 행 높이 ≥ 52(카드는 두 줄) {rh:.0f}')
    cols = await pg.evaluate("(()=>{const r=document.querySelector('#home .hsj[data-s=CONS]');return {t:getComputedStyle(r.querySelector('.hct')).display,h:getComputedStyle(document.querySelector('#home .hsjh')).display,w:document.querySelector('#home .hsjw').clientWidth,tx:r.innerText}})()")
    wantT = 'none' if cols['w'] < 940 else 'block'
    ok(cols['t'] == wantT and (cols['h'] == 'none') == (cols['w'] < 780), f'{tag} H4 폭 {cols["w"]}: 시간 열 {cols["t"]} · 머리 {cols["h"]}')
    ok('D-2' not in cols['tx'] and '읽음' not in cols['tx'] and '%' not in cols['tx'] and '🔁3' in cols['tx'], f'{tag} H4 CONS 행 시험·읽음 없음·🔁3 ({cols["tx"][:80]!r})')
    # ux4 B1-6 시험 칸 ✎·기본/시험순 없음 · 시험일(LS)이 있어도 순서 = 기본 · 과목 홈 시험일 줄 없음
    st = await pg.evaluate("[document.querySelectorAll('#home [data-exed],#home [data-hsort],#home .hce,#home .hcr,#home input[data-exam]').length,[...document.querySelectorAll('#home .hsj[data-s]')].map(r=>r.dataset.s).slice(0,3),JSON.parse(localStorage.getItem('jblhub.v1.exam.CONS'))]")
    ok(st[0] == 0 and st[1] == ['OMS1', 'CONS', 'IMPL'] and st[2] == dd(2), f'{tag} H4 시험 칸·✎·정렬 없음 · 순서 기본 · LS exam.CONS 그대로 {st}')
    await open_(pg, '#/CONS/_home/_home')
    ok(await pg.evaluate("!document.querySelector('#stage .exline,#stage input[data-exam]')"), f'{tag} H6 과목 홈 시험일 줄 없음')
    await open_(pg, '#/')
    # 행 → 과목 홈 · ↪
    await pg.evaluate("document.querySelector('#home .hsj[data-s=OMS1] .hcj').click()"); await pg.wait_for_timeout(600)
    ok((await pg.evaluate('location.hash')).startswith('#/OMS1/_home'), f'{tag} H4 행 누르면 과목 홈')
    await open_(pg, '#/'); await pg.evaluate("document.querySelector('#home .hsj[data-s=ANAT] .hgo').click()"); await pg.wait_for_timeout(900)
    lb = await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.lastBy')).ANAT.d")
    ok((await pg.evaluate('location.hash')).startswith('#/ANAT/' + lb), f'{tag} H4 ↪ → 이어서(lastBy {lb})')
    # 이어서 큰 버튼 = LS last · 칩 2
    await open_(pg, '#/')
    rs = await pg.evaluate("[document.querySelector('#home .hrbig').dataset.s,document.querySelector('#home .hrbig').innerText,[...document.querySelectorAll('#home .hrchip')].map(b=>b.dataset.s)]")
    ok(rs[0] == 'CONS' and '정리표' in rs[1] and '카드 제목' in rs[1] and rs[2] == ['ANAT', 'PHARM'], f'{tag} H3 ↪ 큰 버튼 = last · 칩 = lastBy 다음 2 {rs}')
    # ---- H5 이번 주 · 더보기
    wk = await pg.evaluate("(()=>{const W=__h.tWeek((()=>{const x=new Date();x.setHours(12,0,0,0);x.setDate(x.getDate()-((x.getDay()+6)%7));return x})());const s=W.reduce((a,x)=>a+x.sum,0);const m=Math.round(s/60000);return [Math.floor(m/60)+':'+('0'+m%60).slice(-2),document.querySelector('#home [data-hw=tot]').textContent,document.querySelectorAll('#home .hwb').length,document.querySelectorAll('#home .hwb.today').length]})()")
    ok(wk[0] == wk[1] and wk[2] == 7 and wk[3] == 1, f'{tag} H5 주 합계 = tWeek 합 · 막대 7 · 오늘 1 {wk}')
    await pg.evaluate("document.querySelector('#clock').click()"); await pg.wait_for_timeout(200)
    ok(wk[1] in await pg.inner_text('#tpop .tph'), f'{tag} H5 주 합계 = 시계 팝업 주 합계')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(150)
    await pg.evaluate(f"document.querySelector('#home .hwb[data-hwd=\"{dd(0)}\"]').click()"); await pg.wait_for_timeout(500)
    h = await pg.evaluate('location.hash'); ok(h.startswith('#/_cal') and await pg.evaluate("__h.CAL.sel") == dd(0), f'{tag} H5 막대 → 그날 달력 {h}')
    await open_(pg, '#/')
    dt = await pg.evaluate("[...document.querySelectorAll('#home details.hxm')].map(d=>d.open)")
    ok(dt == [False, False], f'{tag} H5 더보기 접힘 {dt}')
    await pg.click('#home details.hxm[data-hmd=bk] > summary'); await pg.wait_for_timeout(200)
    ok(await pg.evaluate("document.querySelector('#home .bkp [data-bksend]').offsetParent!==null"), f'{tag} H5 💾 펼침 → 보내기 버튼')
    await pg.evaluate("__h.home({push:false})"); await pg.wait_for_timeout(150)
    ok(await pg.evaluate("document.querySelector('#home details.hxm[data-hmd=bk]').open"), f'{tag} H5 다시 그려도 펼침 유지(이 창)')
    await pg.screenshot(path=J.TMP + f'/ux3i_h_{tag}_more.png', full_page=True)
    # ---- H6 과목 홈: 시험일 넣기 칸 없음 · 순서 유지 · 이 과목 달력
    await open_(pg, '#/IMPL/_home/_home')
    ok(await pg.evaluate("!document.querySelector('#stage .exline')"), f'{tag} H6 시험일 없음 → 넣기 칸도 없음(ux4)')
    order = await pg.evaluate("(()=>{const q=['#hguide','#hprog','#hlec','#htop'].map(s=>document.querySelector('#stage '+s));return q.every(Boolean)&&q.every((e,i)=>!i||(q[i-1].compareDocumentPosition(e)&4))})()")
    ok(order, f'{tag} H6 과목 홈 순서 유지(공부 순서 → 진행률 → 강의 → 2회↑)')
    await pg.evaluate("document.querySelector('#hprog [data-tvgo2]').click()"); await pg.wait_for_timeout(500)
    h = await pg.evaluate('location.hash'); ok(h == '#/_cal?s=IMPL', f'{tag} H6 📅 이 과목 달력 → {h}')
    ok(not errs, f'{tag} 콘솔 오류 0 {errs[:3]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for vp, touch, tag in [({'width': 1280, 'height': 900}, False, 'mac'), ({'width': 1180, 'height': 820}, True, 'land'), ({'width': 820, 'height': 1180}, True, 'port')]:
            await run(b, vp, touch, tag)
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
    for f in fails: print('  -', f)
    _sys.exit(1 if fails else 0)
asyncio.run(main())
