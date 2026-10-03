"""C02·C05 회귀: 자동 백업 IndexedDB·저장 공간·복원 안전
C02 옛 localStorage autobak.0~4·p0 → IDB 6개·localStorage autobak 0개 · 복원 창 목록 6개·'저장 공간' 줄 · 되돌리기가 IDB에서 동작 · indexedDB가 없으면 localStorage 방식·오류 0
C05 되돌리기는 공부 기록만(time 오늘 120분 → 되돌린 뒤에도 ≥120분, ann은 백업 값) · 확인창 '바뀐 표시 N개·채점 M개' · 쓰기 중 QuotaExceeded → 원래 값·새로고침 안 함·오류 띠 ·
    같은 파일을 다시 골라도 change · 깨진 ann이 든 백업 합치기 → 다른 키는 합쳐지고 결과 창 '건너뜀 1' · 6과목 연속 이관 → '원고 갱신 전' 스냅숏 1개에 6과목
맥 1280×900 + 아이패드 세로 820×1180 · 가로 1180×820(복원 창). 스크린샷 work/_tmp/ux2i_c02_*.png·ux2i_c05_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, time, datetime
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []; NS = 'jblhub.v1.'
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
TODAY = J.study_today().isoformat()
async def home(pg, h=''):
    await pg.goto(U + h); await pg.wait_for_function("window.__h&&document.querySelector('#home .hsj[data-s]')||document.querySelector('#stage [data-aid]')")
async def c02(b, vp, touch, tag, full):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []; dlg = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    async def on_dialog(d): dlg.append(d.message); await d.accept()
    pg.on('dialog', on_dialog); print('== C02', tag)
    await home(pg); await pg.evaluate("localStorage.clear()"); await pg.evaluate("__h.bkClear()")
    await pg.evaluate("""()=>{const ns='jblhub.v1.';const A=n=>JSON.stringify({'OMS1:DD1:x':[{t:'h',x:'snap'+n,i:0,c:'y'}]});
      for(let i=0;i<5;i++)localStorage.setItem(ns+'autobak.'+i,JSON.stringify({at:1700000000000+i*60000,data:{[ns+'ann.OMS1']:A(i),[ns+'mk.OMS1']:JSON.stringify({ok:{RX0:1},ng:{},bm:{}})}}));
      localStorage.setItem(ns+'autobak.p0',JSON.stringify({at:1690000000000,why:'원고 갱신 전',data:{[ns+'ann.OMS1']:A(9)}}));localStorage.setItem(ns+'autobak.i','4');localStorage.setItem(ns+'autobak.pi','0');
      localStorage.setItem(ns+'ann.OMS1',JSON.stringify({'OMS1:DD1:x':[{t:'h',x:'now',i:0,c:'y'}]}));}""")
    t0 = time.time(); await home(pg)
    await pg.wait_for_function("__h.bkList().then(L=>L.length>=6)", timeout=8000)
    n_idb = await pg.evaluate("__h.bkList().then(L=>L.length)"); n_ls = await pg.evaluate("Object.keys(localStorage).filter(k=>k.indexOf('jblhub.v1.autobak')===0).length")
    ok(n_idb == 6 and n_ls == 0 and await pg.evaluate("__h.BK.ok"), f'옛 autobak 6개 → IDB {n_idb}개 · localStorage autobak {n_ls}개')
    await pg.evaluate("document.querySelector('#bkup').click()"); await pg.click('#rstr'); await pg.wait_for_selector('#rpop .rstore')
    ns = await pg.locator('#rpop [data-snap]').count(); ok(ns == 6, f'복원 창 목록 {ns}개 ({time.time() - t0:.0f}초 안)')
    st = await pg.inner_text('#rpop .rstore'); ok('저장 공간' in st and '백업' in st and 'MB' in st and '마지막 자동 백업' in st, f'저장 공간 줄 {st[:80]!r}')
    await pg.wait_for_timeout(300); await pg.screenshot(path=J.TMP + f'/ux2i_c02_restore_{tag}.png')
    if full:
        # 되돌리기(IDB) — 가장 최근 주기 백업(snap4)
        await pg.evaluate("window.__mark=1")
        await pg.evaluate("document.querySelectorAll('#rpop [data-snap]')[document.querySelectorAll('#rpop [data-snap]').length-5].click()")   # 주기 줄의 첫 번째(최신)
        await pg.wait_for_function("!window.__mark", timeout=8000); await pg.wait_for_function("window.__h", timeout=8000); await pg.wait_for_timeout(300)
        a = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')"))
        ok(a['OMS1:DD1:x'][0]['x'] == 'snap4', f"되돌리기(IDB) → ann {a['OMS1:DD1:x'][0]['x']}")
        ok(any('바뀐 표시' in m and '채점' in m for m in dlg), f'확인창 문구 {dlg[-1][:80] if dlg else ""!r}')
        L = await pg.evaluate("__h.bkList()"); ok(any(x['why'] == '되돌리기 전' for x in L), "되돌리기 전 상태를 '되돌리기 전'으로 보관")
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()
async def c02_noidb(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); await ctx.add_init_script("Object.defineProperty(window,'indexedDB',{value:undefined,configurable:true})")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:200])); print('== C02 indexedDB 없음')
    await home(pg); await pg.evaluate("localStorage.clear()"); await home(pg)
    r = await pg.evaluate("__h.autoBak(true,'파랑 색 키 이관')"); r2 = await pg.evaluate("(localStorage.setItem('jblhub.v1.memo.OMS1.DD1','\"a\"'),__h.autoBak(false))")
    ks = await pg.evaluate("Object.keys(localStorage).filter(k=>/autobak\\.p?\\d$/.test(k)).sort()")
    ok(r and r2 and 'jblhub.v1.autobak.p0' in ks and any(k.endswith('autobak.0') for k in ks) and not await pg.evaluate("__h.BK.ok"), f'localStorage 방식 유지 {ks}')
    await pg.evaluate("document.querySelector('#bkup').click()"); await pg.click('#rstr'); await pg.wait_for_selector('#rpop .rstore'); ok(await pg.locator('#rpop [data-snap]').count() == 2, '복원 창 목록 2개(localStorage)')
    ok(not errs, f'오류 0 ({errs[:2]})'); await ctx.close()
async def c05(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []; dlg = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    async def on_dialog(d): dlg.append(d.message); await d.accept()
    pg.on('dialog', on_dialog); print('== C05')
    await home(pg); await pg.evaluate("localStorage.clear()"); await pg.evaluate("__h.bkClear()"); await home(pg)
    A1 = {'OMS1:DD1:x': [{'t': 'h', 'x': 'old', 'i': 0, 'c': 'y'}]}; A2 = {'OMS1:DD1:x': [{'t': 'h', 'x': 'old', 'i': 0, 'c': 'y'}, {'t': 'h', 'x': 'new1', 'i': 0, 'c': 'y'}, {'t': 'b', 'x': 'new2', 'i': 0}]}
    await pg.evaluate("([a,d])=>{const ns='jblhub.v1.';localStorage.setItem(ns+'ann.OMS1',JSON.stringify(a));localStorage.setItem(ns+'mk.OMS1',JSON.stringify({ok:{Q01:1},ng:{},bm:{}}));localStorage.setItem(ns+'time',JSON.stringify({[d]:{OMS1:600000}}));localStorage.setItem(ns+'pos.OMS1',JSON.stringify({'DD1/learn':{aid:'A',off:5}}));}", [A1, TODAY])
    await pg.evaluate("__h.autoBak(true)")
    await pg.evaluate("([a,d])=>{const ns='jblhub.v1.';localStorage.setItem(ns+'ann.OMS1',JSON.stringify(a));localStorage.setItem(ns+'mk.OMS1',JSON.stringify({ok:{Q01:1},ng:{Q02:1,Q03:1},bm:{}}));localStorage.setItem(ns+'time',JSON.stringify({[d]:{OMS1:7200000}}));localStorage.setItem(ns+'pos.OMS1',JSON.stringify({'DD1/learn':{aid:'B',off:9}}));}", [A2, TODAY])
    # 쓰기 중 QuotaExceeded 주입 → 원래 값·새로고침 안 함
    await pg.evaluate("(()=>{window.__mark=1;const o=Storage.prototype.setItem;let n=0;window.__o=o;Storage.prototype.setItem=function(k,v){if(/\\.(ann|mk)\\./.test(k)&&++n===2){const e=new Error('quota');e.name='QuotaExceededError';throw e;}return o.call(this,k,v);};})()")
    await pg.evaluate("document.querySelector('#bkup').click()"); await pg.click('#rstr'); await pg.wait_for_selector('#rpop [data-snap]'); await pg.click('#rpop [data-snap]'); await pg.wait_for_timeout(1500)
    ann = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')")); mk = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.mk.OMS1')"))
    ok(await pg.evaluate("window.__mark") == 1 and len(ann['OMS1:DD1:x']) == 3 and len(mk['ng']) == 2, '쓰기 중 QuotaExceeded → 원래 값 그대로·새로고침 안 함')
    ok(await pg.locator('#rsterr').count() == 1, '오류 띠')
    await pg.screenshot(path=J.TMP + '/ux2i_c05_quota.png')
    ok(any('바뀐 표시 2개·채점 2개' in m for m in dlg), f"확인창 '바뀐 표시 2개·채점 2개' {dlg[-1][:90] if dlg else ''!r}")
    await pg.evaluate("(()=>{Storage.prototype.setItem=window.__o;})()")
    # 되돌리기: 공부 기록만 · 시간은 큰 값
    await pg.evaluate("document.querySelector('#bkup').click()"); await pg.click('#rstr'); await pg.wait_for_timeout(100)
    if not await pg.is_visible('#rpop'): await pg.evaluate("document.querySelector('#bkup').click()"); await pg.click('#rstr')
    await pg.wait_for_selector('#rpop [data-snap]'); await pg.evaluate("document.querySelectorAll('#rpop [data-snap]')[document.querySelectorAll('#rpop [data-snap]').length-1].click()")
    await pg.wait_for_function("!window.__mark", timeout=8000); await pg.wait_for_function("window.__h", timeout=8000); await pg.wait_for_timeout(300)
    ann = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')")); tm = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.time')")); pos = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.pos.OMS1')"))
    ok(ann == A1, f'ann은 백업 값 {ann}')
    ok(tm[TODAY]['OMS1'] >= 7200000, f"time 오늘 {tm[TODAY]['OMS1'] / 60000:.0f}분 (≥120)")
    ok(pos['DD1/learn']['aid'] == 'B', '읽던 위치(pos)는 지금 값')
    # 같은 파일 다시 고르기 → change · value 비움
    f1 = J.TMP + '/ux2_bad.json'; open(f1, 'w').write('{"app":"other"}')
    await pg.evaluate("window.__ch=0;document.querySelector('#rfile').addEventListener('change',()=>window.__ch++)")
    await pg.set_input_files('#rfile', f1); await pg.wait_for_timeout(200); v1 = await pg.evaluate("document.querySelector('#rfile').value")
    await pg.set_input_files('#rfile', f1); await pg.wait_for_timeout(200)
    ok(await pg.evaluate("window.__ch") == 2 and v1 == '', f"같은 파일을 다시 골라도 change ({await pg.evaluate('window.__ch')}) · value 비움")
    # 깨진 ann 백업 합치기
    f2 = J.TMP + '/ux2_broken.json'
    json.dump({'app': 'jblhub', 'v': 2, 'at': '2026-09-01', 'data': {NS + 'ann.CONS': '{broken', NS + 'memo.OMS1.DD1': json.dumps('백업 메모'), NS + 'done.OMS1': json.dumps({'OMS1:DD1:q': 1})}}, open(f2, 'w'))
    await pg.evaluate("document.querySelector('#rfile').dataset.how='merge'"); await pg.evaluate("window.__mark=1")
    await pg.set_input_files('#rfile', f2); await pg.wait_for_function("!window.__mark", timeout=8000); await pg.wait_for_function("window.__h", timeout=8000)
    await pg.wait_for_selector('#rpop .mres', timeout=5000); mr = await pg.inner_text('#rpop .mres')
    ok('건너뜀 1' in mr and 'ann.CONS' in mr, f'결과 창 {mr[:80]!r}')
    ok(json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.memo.OMS1.DD1')")) == '백업 메모' and await pg.evaluate("localStorage.getItem('jblhub.v1.ann.CONS')") is None, '다른 키는 합쳐지고 깨진 ann은 안 들어옴')
    await pg.screenshot(path=J.TMP + '/ux2i_c05_merge.png')
    # 6과목 연속 이관 → '원고 갱신 전' 스냅숏 1개
    await pg.evaluate("__h.bkClear()")
    S6 = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']
    for s in S6:
        await pg.evaluate("s=>{localStorage.setItem('jblhub.v1.ann.'+s,JSON.stringify({[s+':A:x']:[{t:'h',x:'pre-'+s,i:0,c:'y'}]}));return __h.autoBak(true,'원고 갱신 전',s)}", s)
        await pg.evaluate("s=>localStorage.setItem('jblhub.v1.ann.'+s,JSON.stringify({[s+':A:x']:[{t:'h',x:'post-'+s,i:0,c:'y'}]}))", s)
    L = await pg.evaluate("__h.bkList()"); up = [x for x in L if x['cat'] == 'upd']
    d = await pg.evaluate("id=>__h.bkLoad(id).then(r=>r.data)", up[0]['id']) if up else {}
    pre = [s for s in S6 if ('pre-' + s) in d.get(NS + 'ann.' + s, '')]
    ok(len(up) == 1 and sorted(up[0]['subs']) == sorted(S6) and len(pre) == 6, f"'원고 갱신 전' 스냅숏 {len(up)}개 · 과목 {up[0]['subs'] if up else []} · 이관 직전 값 {len(pre)}/6")
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await c02(b, {'width': 1280, 'height': 900}, False, 'mac', True)
        await c02(b, {'width': 820, 'height': 1180}, True, 'ipp', False)
        await c02(b, {'width': 1180, 'height': 820}, True, 'ipl', False)
        await c02_noidb(b)
        await c05(b)
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
