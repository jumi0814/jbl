"""ux2 수정자 A 회귀(데이터·시간·기록 — work/ux2_verify_prev.json func V01~V13 · flow V04·V05·V07·V10).
시간(V02·V07·V10)은 ux2_time.py(part_multi·part_twoidle). 여기서는:
 채점 — flow V04 ✗→✓ 1초 안 = 기록 하나·복습 없음 · func V03 ✗ ✗(끔) = 복습·'한 번이라도 틀림'에서 빠짐 · V11 같은 날 맞음 여러 번 = 하루 · flow V05 첫 ✗ 뒤 '🔁 복습 1' 칩이 새로고침 없이
 이관 — flow V10 옛 fc J: 판정이 과목을 열기 전 허브 홈 개수에 · func V04 과목 셋을 열어도 '원고 갱신·이관 전' 한 칸(subs *)·합치기 전은 rst 칸 · V09 되돌린 뒤 fcMerged 다시 · V13 예상 플래시카드 = mk
 저장 — V05 devCut 전 날짜는 큰 값 · V08 저장 실패 큐가 새로고침 뒤 다시 저장 · V12 한도 재기(lscap)
 표시 — V01 정리표 세부(.mfull)에 든 표시가 요약·아이패드 세로에서도 보임 · V07 숨긴 출처 글자('(필기)'·'슬라이드 NN: ')에 든 표시가 보임
맥 1280×900 + 아이패드 세로 820×1180 + 가로 1180×820(표시 보임). 스크린샷 work/_tmp/ux2f_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; NS = 'jblhub.v1.'; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def go(pg, h, ms=900):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_function('window.__h&&__h.PACKS.CONS&&__h.PACKS.OMS1', timeout=20000)
    await pg.wait_for_timeout(ms); await pg.evaluate('__h.migWait()')
async def ls(pg, k):
    v = await pg.evaluate(f"localStorage.getItem('{NS}{k}')"); return json.loads(v) if v else None
async def clean(pg):
    await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await pg.evaluate("__h.bkClear()")

async def part_grade(b):
    print('== 채점 기록(flow V04·V05 · func V03·V11)')
    ctx = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await go(pg, '#/'); await clean(pg); await go(pg, '#/CONS/_jb')
    ids = await pg.evaluate("[...document.querySelectorAll('#cards .qc')].slice(0,4).map(c=>c.id.slice(2))")
    q1, q2, q3 = ids[0], ids[1], ids[2]
    hid = await pg.evaluate("(()=>{const b=document.querySelector('#jbbar [data-qf=due]');return b?b.hidden:null})()")
    ok(hid is True, f"깨끗한 기록: '🔁 복습' 칩은 만들어 두되 숨김 ({hid})")
    # flow V05: 첫 ✗ → 칩이 바로
    await pg.evaluate(f"document.querySelector('#c-{q1} [data-mk=\"ng\"]').click()"); await pg.wait_for_timeout(200)
    st = await pg.evaluate("(()=>{const b=document.querySelector('#jbbar [data-qf=due]'),e=document.querySelector('#jbbar [data-qf=ever]');return [b.hidden,b.textContent,e.hidden,e.textContent]})()")
    ok(st[0] is False and '복습 1' in st[1] and st[2] is False and '틀림 1' in st[3], f'첫 ✗ 뒤 새로고침 없이 칩 {st}')
    await pg.screenshot(path=J.TMP + '/ux2f_v05_chip_ipp.png', clip={'x': 0, 'y': 0, 'width': 820, 'height': 420})
    # flow V04: ✗ → 0.5초 → ✓ (카드 버튼 = toggle)
    await pg.evaluate(f"document.querySelector('#c-{q2} [data-mk=\"ng\"]').click()"); await pg.wait_for_timeout(500)
    await pg.evaluate(f"document.querySelector('#c-{q2} [data-mk=\"ok\"]').click()"); await pg.wait_for_timeout(200)
    mk = await ls(pg, 'mk.CONS'); L = mk['log'].get(q2, [])
    R = await pg.evaluate(f"(()=>{{const R=__h.revInfo('CONS');return [R.due.has('{q2}'),R.ever.has('{q2}')]}})()")
    ok(len(L) == 1 and L[0]['r'] == 'ok' and R == [False, False], f'✗→✓ 0.5초 = 기록 하나 {[(x["r"]) for x in L]} · 복습 대기열·한 번이라도 틀림 아님 {R}')
    # func V03: ✗ ✗ (끔)
    await pg.evaluate(f"document.querySelector('#c-{q3} [data-mk=\"ng\"]').click()"); await pg.wait_for_timeout(300)
    await pg.evaluate(f"document.querySelector('#c-{q3} [data-mk=\"ng\"]').click()"); await pg.wait_for_timeout(200)
    mk = await ls(pg, 'mk.CONS'); R = await pg.evaluate(f"(()=>{{const R=__h.revInfo('CONS');return [R.due.has('{q3}'),R.ever.has('{q3}')]}})()")
    ok(q3 not in mk['ng'] and not mk['log'].get(q3) and R == [False, False], f'✗ 다시 눌러 끔 → 기록·복습에서 빠짐 {mk["log"].get(q3)} {R}')
    # 옛 기록(끈 ✗가 log에 남은 1·2차 판): 지금 채점 없음 + 마지막 ng → 복습 아님
    r = await pg.evaluate(f"__h.revNext({{ok:{{}},ng:{{}},bm:{{}},log:{{'{q3}':[{{r:'ng',t:Date.now()-5000}}]}}}},'{q3}')")
    ok(r is None, f'옛 기록(끈 ✗만 log에) → 복습 아님 ({r})')
    # func V11: 같은 날 맞음 세 번 = 하루 → 1일 뒤 · 이틀에 걸쳐 = 3일 뒤
    one = await pg.evaluate("(()=>{const d0=new Date(2026,8,20,9).getTime(),H=36e5;const m={ok:{X:1},ng:{},bm:{},log:{X:[{r:'ng',t:d0},{r:'ok',t:d0+H},{r:'ok',t:d0+2*H},{r:'ok',t:d0+3*H}]}};return __h.revNext(m,'X')})()")
    two = await pg.evaluate("(()=>{const d0=new Date(2026,8,20,9).getTime(),H=36e5;const m={ok:{X:1},ng:{},bm:{},log:{X:[{r:'ng',t:d0},{r:'ok',t:d0+H},{r:'ok',t:d0+24*H}]}};return __h.revNext(m,'X')})()")
    ok(one == '2026-09-21' and two == '2026-09-24', f'같은 날 맞음 3번 → 다음 복습 {one}(1일 뒤) · 이틀 → {two}(3일 뒤)')
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()

async def part_mig(b):
    print('== 이관(flow V10 · func V04·V09·V13)')
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await go(pg, '#/'); await clean(pg)
    q = await pg.evaluate("__h.PACKS.OMS1.order.slice(0,5)")
    pid = await pg.evaluate("(()=>{const p=__h.PACKS.OMS1;const L=p.lect.find(L=>L.pred&&L.pred.length);const m=/data-id=\"(P:[^\"]+)\"/.exec(p.preds[L.pred[0]].html);return [L.k,m[1]]})()")
    fc = {'J:' + q[0]: {'s': 'x', 't': 1700000000000}, 'J:' + q[1]: {'s': 'x', 't': 1700000000001}, 'J:' + q[2]: {'s': 'o', 't': 1700000000002}, pid[1]: {'s': 'x', 't': 1700000000003}}
    await pg.evaluate("([ns,f])=>{localStorage.setItem(ns+'fc.OMS1',JSON.stringify(f));localStorage.setItem(ns+'fc.CONS',JSON.stringify({['J:'+__h.PACKS.CONS.order[0]]:{s:'x',t:1700000000000}}));}", [NS, fc])
    await pg.evaluate("__h.bkClear()")
    await go(pg, '#/', 1500)
    card = await pg.evaluate("document.querySelector('.hsj[data-s=OMS1] .hcj').title")   # ux3 H4 과목 표 기출 칸(title = '기출 n문항 — 맞음 · 틀림 · 안 푼 것')
    ok('맞음 1' in card and '틀림 2' in card, f'과목을 열기 전 허브 홈 = 합친 개수 ({card.strip()})')
    mk = await ls(pg, 'mk.OMS1')
    ok(mk['ng'].get(q[0]) == 1 and mk['ng'].get(pid[1]) == 1, f"옛 fc J:·P: 판정 → mk ({list(mk['ng'])})")
    L = await pg.evaluate("__h.bkList()"); up = [x for x in L if x['cat'] == 'upd']; mi = [x for x in L if x['cat'] == 'misc']
    ok(len(up) == 1 and up[0]['subs'] == ['*'] and not mi, f"이관 전 백업 = 'upd' 한 칸(subs *) {[(x['cat'], x['why'], x['subs']) for x in L]}")
    pre = await pg.evaluate("__h.bkList().then(L=>__h.bkLoad(L.find(x=>x.cat==='upd').id)).then(r=>[r.data['jblhub.v1.mk.OMS1']||null,r.data['jblhub.v1.fc.CONS']||null])")
    ok(pre[0] is None and pre[1] is not None, f'그 백업은 이관 직전 전 과목 상태(mk.OMS1 없음·fc.CONS 있음)')
    await go(pg, '#/OMS1/_home'); t2 = await pg.evaluate("document.querySelector('#stage').textContent")
    ok('맞음 1' in t2 and '틀림 2' in t2, '과목 홈 개수 = 허브 홈 개수')
    await go(pg, '#/CONS/_home'); await go(pg, '#/IMPL/_home')
    L = await pg.evaluate("__h.bkList()")
    ok(len([x for x in L if x['cat'] == 'upd']) == 1 and not [x for x in L if x['cat'] == 'misc'], f"과목 셋을 열어도 이관 백업 한 칸 {[(x['cat'], x['why']) for x in L]}")
    ok(await pg.evaluate("__h.autoBak(true,'합치기 전').then(()=>__h.bkList()).then(L=>L.some(x=>x.cat==='rst'&&x.why==='합치기 전'))"), "'합치기 전'은 따로(rst) 칸")
    # V13: 예상 탭 · 플래시카드
    await go(pg, f'#/OMS1/{pid[0]}/pred')
    ok(await pg.evaluate(f"document.querySelector('.pc[data-id=\"{pid[1]}\"]').classList.contains('mk-ng')"), '옛 예상 플래시카드 몰라요 → 예상 탭 ✗')
    await go(pg, f'#/OMS1/{pid[0]}/flash'); await pg.click('#fc [data-fk="예상"]'); await pg.wait_for_timeout(150)
    st = await pg.evaluate(f"(()=>{{const F=__h.Flash;const j=F.deck.findIndex(c=>c.key==='{pid[1]}');F.i=j;F.draw();return document.querySelector('#fcard .fcm')?document.querySelector('#fcard .fcm').textContent:''}})()")
    ok(st == '몰라요', f'플래시카드 예상 카드 상태 = mk ({st})')
    await pg.click('#fo'); await pg.wait_for_timeout(200); mk = await ls(pg, 'mk.OMS1')
    ok(mk['ok'].get(pid[1]) == 1 and pid[1] not in mk['ng'] and mk['log'][pid[1]][-1].get('how') == 'fc', '예상 카드 알아요 → mk.ok (how:fc)')
    fcm = await ls(pg, 'fc.OMS1'); ok(fcm[pid[1]]['s'] == 'x', '예상 카드 판정은 fc에 새로 쓰지 않음(옛 값 그대로)')
    # V09: 이관 전 백업으로 되돌리기 → fcMerged 지워지고 다시 합침
    snap = await pg.evaluate("__h.bkList().then(L=>L.find(x=>x.cat==='upd').id)")
    pg.once('dialog', lambda d: asyncio.ensure_future(d.accept()))
    await pg.evaluate("document.querySelector('#bkup').click();document.querySelector('#rstr').click()"); await pg.wait_for_timeout(400)
    await pg.evaluate(f"document.querySelector('#rpop [data-snap=\"{snap}\"]').click()")
    await pg.wait_for_timeout(2500); await pg.wait_for_function('window.__h&&__h.PACKS.OMS1', timeout=20000); await pg.wait_for_timeout(800); await pg.evaluate('__h.migWait()')
    mk = await ls(pg, 'mk.OMS1')
    ok(bool(mk) and mk['ng'].get(q[0]) == 1 and mk['ng'].get(pid[1]) == 1, f"이관 전으로 되돌린 뒤 옛 판정을 다시 합침 ({(mk or {}).get('ng')})")
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()

async def part_store(b):
    print('== 저장(func V05·V08·V12)')
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await go(pg, '#/'); await clean(pg); await go(pg, '#/')
    cut = await pg.evaluate("__h.devCut()"); ok(bool(cut) and await ls(pg, 'devCut') == cut, f'devCut = 처음 연 날 ({cut})')
    # V05: 합산 시작 전 날짜 = 큰 값, 그 뒤 = 합
    pre, post = '2026-01-10', cut
    M = 60000
    await pg.evaluate("([ns,a,b,M])=>{localStorage.setItem(ns+'time',JSON.stringify({[a]:{OMS1:60*M},[b]:{OMS1:10*M}}));localStorage.setItem(ns+'timeDev',JSON.stringify({dmac:{name:'맥',time:{[a]:{OMS1:60*M},[b]:{OMS1:5*M}}}}));}", [NS, pre, post, M])
    await go(pg, '#/')
    d1 = await pg.evaluate(f"__h.tDay('{pre}').OMS1"); d2 = await pg.evaluate(f"__h.tDay('{post}').OMS1")
    ok(d1 == 60 * M, f'합산 시작 전({pre}) 이 기기 60분 + 맥 60분(1차 판 max 합침) → {d1 / M:.0f}분(큰 값)')
    ok(d2 >= 15 * M, f'합산 시작일부터는 더함 → {d2 / M:.0f}분(≥ 15)')
    # V12: 한도 재기
    await pg.evaluate("__h.lsCapProbe()"); cap = await ls(pg, 'lscap')
    ok(bool(cap) and 1e6 <= cap <= 2e7 and await pg.evaluate("__h.lsCap()") == cap, f'lscap 잼 = {cap} 글자 · lsCap()이 씀')
    # V08: 저장 실패 → LSQ → IDB → 새로고침 뒤 다시 저장
    await go(pg, '#/OMS1/_jb')
    qid = await pg.evaluate("document.querySelector('#cards .qc').id.slice(2)")
    await pg.evaluate("""(()=>{const o=Storage.prototype.setItem;window.__o=o;Storage.prototype.setItem=function(k,v){if(this===localStorage&&String(k).indexOf('jblhub.v1.mk.')===0){const e=new Error('full');e.name='QuotaExceededError';throw e;}return o.call(this,k,v);};})()""")
    await pg.evaluate(f"document.querySelector('#c-{qid} [data-mk=\"ng\"]').click()"); await pg.wait_for_timeout(600)
    band = await pg.evaluate("(document.getElementById('lserr')||{}).textContent||''")
    ok('저장되지 않았어요' in band and '임시 보관 중' in band, f'오류 띠 = 임시 보관 n건 ({band[:60]!r})')
    await pg.screenshot(path=J.TMP + '/ux2f_v08_band.png', clip={'x': 0, 'y': 700, 'width': 1280, 'height': 200})
    ok(await ls(pg, 'mk.OMS1') is None, '그동안 localStorage에는 없음')
    await pg.goto('about:blank'); await pg.goto(U + '#/OMS1/_jb'); await pg.wait_for_function('window.__h&&__h.PACKS.OMS1', timeout=20000); await pg.wait_for_timeout(1200)
    mk = await ls(pg, 'mk.OMS1')
    ok(bool(mk) and mk['ng'].get(qid) == 1, f'새로고침 뒤 임시 보관을 다시 저장 → mk.OMS1.ng.{qid}')
    ok(await pg.evaluate(f"document.querySelector('#c-{qid}').classList.contains('mk-ng')"), '그 채점이 화면에도')
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()

GEN_MFULL = r"""(()=>{const K=__h.Kit;const trs=[...document.querySelectorAll('#stage .msum tr[data-aid]')];for(const tr of trs){const f=tr.querySelector('td.md .mfull');if(!f)continue;const T=K.textOf(tr);
 const ws=(f.textContent.match(/[A-Za-z가-힣]{4,}/g)||[]);for(const w of ws){if(T.indexOf(w)>=0&&T.indexOf(w)===T.lastIndexOf(w)&&(tr.querySelector('.sline')||{textContent:''}).textContent.indexOf(w)<0)return [tr.dataset.aid,w];}}return null;})()"""
GEN_SRT = r"""(()=>{const K=__h.Kit,SK=K.skipSel;const s=[...document.querySelectorAll('#stage .srcn .srt,#stage .srcp .srt')].find(e=>e.textContent.trim().length>=3);if(!s)return null;const B=s.closest('[data-aid]');
 const w=document.createTreeWalker(B,NodeFilter.SHOW_TEXT);let n,v='';while(n=w.nextNode()){const pe=n.parentElement;if(!pe||pe.closest(SK))continue;if(s.contains(n))break;v+=n.nodeValue;}
 const x=s.textContent.trim().replace(/[:\s]+$/,'');const T=K.textOf(B);let i=0,q=-1;const at=T.indexOf(x,v.length);while((q=T.indexOf(x,q+1))>=0&&q<at)i++;return [B.dataset.aid,x,i];})()"""
async def part_vis(b, vp, touch, tag):
    print('== 표시 보임(func V01·V07)', tag)
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await go(pg, '#/'); await clean(pg)
    await go(pg, '#/OMS1/DD1/sum'); g = await pg.evaluate(GEN_MFULL)
    await go(pg, '#/OMS1/DD1/learn'); s = await pg.evaluate(GEN_SRT)
    ok(bool(g) and bool(s), f'픽스처: 세부 칸 낱말 {g} · 출처 글자 {s}')
    ann = {g[0]: [{'t': 'h', 'x': g[1], 'i': 0, 'c': 'y'}], s[0]: [{'t': 'h', 'x': s[1], 'i': s[2], 'c': 'p'}]}
    await pg.evaluate("([ns,a])=>localStorage.setItem(ns+'ann.OMS1',JSON.stringify(a))", [NS, ann])
    await pg.evaluate("localStorage.removeItem('jblhub.v1.sumdense')")
    await go(pg, '#/OMS1/DD1/sum', 1200)
    v = await pg.evaluate(f"(()=>{{const tr=document.querySelector('#stage tr[data-aid=\"{g[0]}\"]');const m=[...tr.querySelectorAll('[data-rk]')];const b=tr.querySelector('.mdmore .rkn');return [m.length,m.some(e=>e.getClientRects().length>0),b?b.textContent:'']}})()")
    ok(v[0] > 0 and v[1], f'정리표 요약: 세부(.mfull)에 든 형광펜이 보임 {v}')
    await pg.evaluate(f"document.querySelector('#stage tr[data-aid=\"{g[0]}\"]').scrollIntoView({{block:'center'}})"); await pg.wait_for_timeout(200)
    await pg.screenshot(path=J.TMP + f'/ux2f_v01_sum_{tag}.png')
    await go(pg, '#/OMS1/DD1/learn', 1200)
    v2 = await pg.evaluate(f"(()=>{{const B=document.querySelector('#stage [data-aid=\"{s[0]}\"]');const m=[...B.querySelectorAll('[data-rk]')];return [m.length,m.some(e=>e.getClientRects().length>0),!!B.querySelector('.srt.rkshow')]}})()")
    ok(v2[0] > 0 and v2[1] and v2[2], f"학습: 숨긴 출처 글자('{s[1]}')에 든 형광펜이 보임 {v2}")
    await pg.evaluate(f"document.querySelector('#stage .srt.rkshow').scrollIntoView({{block:'center'}})"); await pg.wait_for_timeout(200)
    await pg.screenshot(path=J.TMP + f'/ux2f_v07_srt_{tag}.png')
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await part_grade(b)
        await part_mig(b)
        await part_store(b)
        await part_vis(b, {'width': 1280, 'height': 900}, False, 'mac')
        await part_vis(b, {'width': 820, 'height': 1180}, True, 'ipp')
        await part_vis(b, {'width': 1180, 'height': 820}, True, 'ipl')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
