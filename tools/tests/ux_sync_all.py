"""10-25c 사용자 '핸드폰에서 접속한 화면이랑 … 넘버링 내역, 예상문제 별표 등 모든 내역들, 기록들이 똑같이 실시간 연동 … 각 화면에서의 입력이 바로 반영되면서 다른 화면에서
접속해서 들어가보면 반영되어있게끔 … 충돌이나 누락 오류 없게끔 … 넘버링이랑 jb문제 및 예상문제 별표 표시 등등 이런 내역들 실시간 연동되는건지 제발 확인' 회귀.
가짜 GitHub Gist(fakegist.py)와 두 창(컴퓨터 1280 · 아이폰 393 터치) — 값을 저장소에 직접 넣지 않고 **실제 화면 단추**로, 받는 쪽은 **새로고침 없이 화면에** 보이는지:
 ① JB 문제 ★·✓ 맞음(컴퓨터) → 휴대폰 JB 화면에 저절로(보내기 2.5~12초 · 받기 15초 확인)
 ② 예상문제 ★·✗ 틀림(휴대폰) → 컴퓨터 예상 화면에
 ③ 동시 입력 = 충돌·누락 없음: 연결된 채 서로 모르게 컴퓨터 ★ A · 휴대폰 ★ B·✗ C → 주고받은 뒤 양쪽 모두 A·B·C(+①②) 그대로
 ④ 지우기 전파: 컴퓨터에서 ★를 끄면 휴대폰에서도 꺼짐(다른 ★는 그대로)
 ⑤ 정리본 카드 ★(북마크 카드 cbm) 컴퓨터 → 휴대폰 학습 화면 카드에 ★ 북마크됨
 ⑥ 과목 홈 강의 북마크 ★(lbm) 휴대폰 → 컴퓨터 과목 홈 강의 카드에
 ⑦ 두 창 다 새로고침 없음 · 컴퓨터 기록(★·채점) 수가 줄지 않음 · 페이지 오류 0
넘버링(문제·스토리·복습·진행 중 회차·내 답안 낙서장)은 ux_sync_num.py · 키별 합치기 규칙은 ux_sync.py.
실행: JBL_HTTP=1 .venv/bin/python tools/tests/ux_sync_all.py"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import jblpaths as J, asyncio, json
from playwright.async_api import async_playwright
from fakegist import gist_data, getv, settle, tick, poll, two, connect, NS
U = J.HUB_URL; SJ = 'PHARM'; LK = 'HM'; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m, flush=True)
    if not c: fails.append(m)
    return c
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
async def go(pg, h, sel):
    await pg.evaluate(f"location.hash={h!r}"); await pg.wait_for_function(WAIT + f"&&!!document.querySelector({sel!r})", timeout=60000); await pg.wait_for_timeout(900)
JBC = "#stage article.qc[data-id]"; PDC = "#stage article.pc[data-id]"
async def ids(pg, sel, n): return await pg.evaluate(f"[...document.querySelectorAll({sel!r})].slice(0,{n}).map(e=>e.dataset.id)")
async def press(pg, sel, cid, k):   # 그 카드의 위 단추(✓ 맞음 · ✗ 틀림 · ★) — 사람이 누르듯 화면에 보이게 한 뒤 click
    await pg.evaluate("([s,i,k])=>{const c=document.querySelector(s+'[data-id=\"'+CSS.escape(i)+'\"]');c.scrollIntoView({block:'center'});c.querySelector('.acts:not(.acts2) [data-mk=\"'+k+'\"]').click()}", [sel, cid, k]); await pg.wait_for_timeout(350)
async def cls(pg, sel, cid): return await pg.evaluate("([s,i])=>{const c=document.querySelector(s+'[data-id=\"'+CSS.escape(i)+'\"]');return c?['ok','ng','bm'].filter(k=>c.classList.contains('mk-'+k)):null}", [sel, cid])
async def mkn(pg): m = await getv(pg, 'mk.' + SJ) or {}; return sum(len(m.get(k) or {}) for k in ('ok', 'ng', 'bm'))
async def main():
    async with async_playwright() as p:
        b, dk, ph = await two(p, U); errs = []
        for pg in (dk, ph): pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        dev_d, dev_p = await connect(dk, ph)
        ok(dev_d and dev_p and dev_d != dev_p, f'연결 — 컴퓨터 {dev_d} · 휴대폰 {dev_p}')
        await go(dk, f'#/{SJ}/{LK}/jb', JBC); await go(ph, f'#/{SJ}/{LK}/jb', JBC)
        for pg in (dk, ph): await pg.evaluate("window.__keep=1")
        J5 = await ids(dk, JBC, 6)
        # ① 컴퓨터 JB ★·맞음 → 휴대폰(저절로)
        await press(dk, JBC, J5[0], 'bm'); await press(dk, JBC, J5[1], 'ok')
        ok(await cls(dk, JBC, J5[0]) == ['bm'] and await cls(dk, JBC, J5[1]) == ['ok'], f'① 컴퓨터 화면: {J5[0]} ★ · {J5[1]} ✓')
        push = None
        for i in range(60):
            m = gist_data(dev_d, SJ).get(NS + 'mk.' + SJ)
            if m and J5[0] in json.loads(m).get('bm', {}) and J5[1] in json.loads(m).get('ok', {}): push = i / 2; break
            await dk.wait_for_timeout(500)
        ok(push is not None, f'① 컴퓨터가 저절로 보냄(바뀌면 2.5초 뒤 · 최소 12초 간격) {push}s')
        t1 = await poll(ph, f"(()=>{{const c=document.querySelector('{JBC}[data-id=\"{J5[0]}\"]'),d=document.querySelector('{JBC}[data-id=\"{J5[1]}\"]');return c&&d&&c.classList.contains('mk-bm')&&d.classList.contains('mk-ok')}})()", 40)
        ok(t1 is not None, f'① 휴대폰 JB 화면에 저절로(15초 확인 · 새로고침 없이) {t1}s · 오류 {await ph.evaluate("JBLSYNC.err()")!r}')
        if t1 is None: await tick(ph)
        # ② 휴대폰 예상 ★·틀림 → 컴퓨터
        await go(dk, f'#/{SJ}/{LK}/pred', PDC); await go(ph, f'#/{SJ}/{LK}/pred', PDC)
        P3 = await ids(ph, PDC, 3)
        await press(ph, PDC, P3[0], 'bm'); await press(ph, PDC, P3[1], 'ng')
        ok(await cls(ph, PDC, P3[0]) == ['bm'] and await cls(ph, PDC, P3[1]) == ['ng'], f'② 휴대폰 예상 화면: ★ · ✗ ({P3[0][:30]}…)')
        await tick(ph, '{pull:false,force:true}'); await tick(dk)
        v = [await cls(dk, PDC, P3[0]), await cls(dk, PDC, P3[1])]
        ok(v == [['bm'], ['ng']], f'② 컴퓨터 예상 화면에 휴대폰 ★·✗(새로고침 없이) {v}')
        # ③ 동시 입력 — 서로 모르게(보내기 전) 양쪽에서
        await go(dk, f'#/{SJ}/{LK}/jb', JBC); await go(ph, f'#/{SJ}/{LK}/jb', JBC)
        await press(dk, JBC, J5[2], 'bm'); await press(ph, JBC, J5[3], 'bm'); await press(ph, JBC, J5[4], 'ng')
        await press(dk, JBC, J5[5], 'ok')   # 컴퓨터 JB 하나 더(같은 mk 키를 양쪽이 같은 때 고침)
        await tick(dk, '{pull:false,force:true}'); await tick(ph, '{force:true}'); await tick(dk)
        want = {J5[0]: ['bm'], J5[1]: ['ok'], J5[2]: ['bm'], J5[3]: ['bm'], J5[4]: ['ng'], J5[5]: ['ok']}
        got_d = {i: await cls(dk, JBC, i) for i in want}; got_p = {i: await cls(ph, JBC, i) for i in want}
        ok(got_d == want, f'③ 컴퓨터 화면: 양쪽에서 같은 때 한 ★·✓·✗ 모두 남음(충돌·누락 0) {got_d}')
        ok(got_p == want, f'③ 휴대폰 화면: 양쪽 기록 모두 {got_p}')
        md, mp = await getv(dk, 'mk.' + SJ), await getv(ph, 'mk.' + SJ)
        ok(md == mp, '③ 두 기기 저장소의 채점·★ 기록이 글자까지 같음(합친 결과가 같음 — 서로 되풀이해 보내지 않음)')
        ok(P3[0] in (md or {}).get('bm', {}) and P3[1] in (md or {}).get('ng', {}), '③ 예상문제 ★·✗(②)도 그대로')
        n_before = await mkn(dk)
        # ④ 지우기 전파
        await press(dk, JBC, J5[0], 'bm')
        ok(await cls(dk, JBC, J5[0]) == [], f'④ 컴퓨터: {J5[0]} ★ 끔')
        await tick(dk, '{pull:false,force:true}'); await tick(ph)
        ok(await cls(ph, JBC, J5[0]) == [] and await cls(ph, JBC, J5[2]) == ['bm'] and await cls(ph, JBC, J5[3]) == ['bm'], f'④ 휴대폰: 끈 ★만 꺼지고 다른 ★는 그대로')
        # ⑤ 정리본 카드 ★(cbm) 컴퓨터 → 휴대폰 학습 화면
        await go(dk, f'#/{SJ}/{LK}/learn', '#stage .tc .cbend'); await go(ph, f'#/{SJ}/{LK}/learn', '#stage .tc .cbend')
        aid = await dk.evaluate("(()=>{const c=[...document.querySelectorAll('#stage .tc')].find(x=>x.querySelector(':scope>.cbend'));c.scrollIntoView({block:'center'});c.querySelector(':scope>.cbend').click();return c.dataset.aid})()"); await dk.wait_for_timeout(400)
        ok(await dk.evaluate(f"document.querySelector('#stage .tc[data-aid=\"{aid}\"]').classList.contains('cbm')"), f'⑤ 컴퓨터 학습 화면: 카드 ★ 북마크 {aid}')
        await tick(dk, '{pull:false,force:true}'); await tick(ph)
        v = await ph.evaluate(f"(()=>{{const c=document.querySelector('#stage .tc[data-aid=\"{aid}\"]');return c?[c.classList.contains('cbm'),(c.querySelector(':scope>.cbend')||{{}}).textContent]:null}})()")
        ok(v and v[0] and '★' in (v[1] or ''), f'⑤ 휴대폰 학습 화면(새로고침 없이): 같은 카드 ★ 북마크됨 {v}')
        # ⑥ 과목 홈 강의 북마크 ★(lbm) 휴대폰 → 컴퓨터
        await go(dk, f'#/{SJ}/_home', '#hlec [data-lbm]'); await go(ph, f'#/{SJ}/_home', '#hlec [data-lbm]')
        lb = await ph.evaluate("(()=>{const b=document.querySelector('#hlec [data-lbm]');b.scrollIntoView({block:'center'});b.click();return b.dataset.lbm})()"); await ph.wait_for_timeout(500)
        await tick(ph, '{pull:false,force:true}'); await tick(dk)
        v = await dk.evaluate(f"(()=>{{const b=document.querySelector('#hlec [data-lbm=\"{lb}\"]');return b?[b.classList.contains('on'),b.textContent.trim().slice(0,2)]:null}})()")
        ok(v and v[0], f'⑥ 컴퓨터 과목 홈(새로고침 없이): 휴대폰이 북마크한 강의 ★ {lb} {v}')
        # ⑦
        ok(await dk.evaluate("window.__keep===1") and await ph.evaluate("window.__keep===1"), '⑦ 두 창 모두 새로고침 없음')
        n_after = await mkn(dk)
        ok(n_after == n_before - 1, f'⑦ 컴퓨터 채점·★ 수 = 끈 1개만 줄어듦 {n_before} → {n_after}')
        ok(not errs, f'⑦ 페이지 오류 0 {errs[:3]}')
        await dk.screenshot(path=J.TMP + '/ux_sync_all_desk.png'); await ph.screenshot(path=J.TMP + '/ux_sync_all_phone.png')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
