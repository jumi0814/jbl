"""회귀: 검증에서 나온 문제 수정(F3·F4·F5·F6·V01·V03) — .venv/bin/python tools/tests/ux_fix.py
F4 백업 합치기에서 맞음·틀림이 겹치면 채점 기록의 마지막 것 하나만(화면마다 수가 같음)
F3 자동 백업: 바뀌지 않으면 새로 쓰지 않음 · 원고 갱신 전 백업은 주기 백업이 밀어내지 못함
F5 팩 판 ≠ 허브 판이면 새로고침 안내 + 형광펜·채점 잠금 · 옛 index가 새 팩을 받으면 ?v=로 한 번만 다시 엶
F6 기출 대장이 아이패드 세로·가로에서 옆으로 밀리지 않음 · V01·V03 목록 점이 첫 글자를 가리지 않음"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, shutil, re, threading, http.server, functools, socketserver
from playwright.async_api import async_playwright
U = J.HUB_URL
fail = []
def ok(c, msg):
    print(('  OK  ' if c else '  FAIL') + ' ' + msg)
    if not c: fail.append(msg)
SUBJ = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']
OVERLAP = r"""()=>{const bad=[];document.querySelectorAll('#stage .ln.li, #stage .mtx .ci').forEach(el=>{if(!el.offsetParent)return;const b=getComputedStyle(el,'::before');if(b.content==='none'||b.display==='none'||b.content==='normal'||b.position!=='absolute')return;   /* 글 흐름 안의 칩(ux2 F01 '✓ 정답')은 겹칠 수 없음 — audit_design OVERLAP과 같음 */
 const cs=getComputedStyle(el);const pad=parseFloat(cs.paddingLeft)+parseFloat(cs.textIndent||0);const L=parseFloat(b.left)||0,W=parseFloat(b.width)||0;if(L+W>pad-1)bad.push(el.className+': '+el.textContent.trim().slice(0,20));});return bad.slice(0,5);}"""

def serve(d):
    class Q(http.server.SimpleHTTPRequestHandler):
        def __init__(s, *a, **k): super().__init__(*a, directory=d, **k)
        def log_message(s, *a): pass
    class S(socketserver.ThreadingTCPServer): allow_reuse_address = True; daemon_threads = True
    srv = S(('127.0.0.1', 0), Q); threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        pg = await (await b.new_context(viewport={'width': 1280, 'height': 900})).new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await pg.goto(U + '#/ANAT/_home'); await pg.wait_for_timeout(2000); await pg.evaluate('localStorage.clear()')
        # ---- F4
        await pg.evaluate("""()=>{localStorage.setItem('jblhub.v1.mk.ANAT',JSON.stringify({ok:{Q01:1,Q03:1},ng:{},log:{Q03:[{r:'ng',t:1000},{r:'ok',t:3000}]}}));}""")
        await pg.evaluate("""()=>__h.mergeInto({'jblhub.v1.mk.ANAT':JSON.stringify({ok:{},ng:{Q03:1,Q04:1,Q01:1},log:{Q03:[{r:'ng',t:2000}]}})})""")
        m = await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.mk.ANAT'))")
        ok('Q03' in m['ok'] and 'Q03' not in m['ng'], f"F4 합치기: 기록의 마지막(맞음)이 이김 ok={sorted(m['ok'])} ng={sorted(m['ng'])}")
        ok('Q01' in m['ok'] and 'Q01' not in m['ng'], 'F4 합치기: 기록이 없으면 지금 기기의 채점(맞음)을 따름')
        await pg.evaluate("""()=>localStorage.setItem('jblhub.v1.mk.ANAT',JSON.stringify({ok:{Q05:1},ng:{Q05:1},log:{Q05:[{r:'ok',t:1},{r:'ng',t:9}]}}))""")
        g = await pg.evaluate("(()=>{const m=__h.getMK('ANAT');return [!!m.ok.Q05,!!m.ng.Q05];})()")
        ok(g == [False, True], f'F4 옛 겹친 기록도 getMK에서 하나로 {g}')
        await pg.goto('about:blank'); await pg.goto(U + '#/ANAT/_home'); await pg.wait_for_timeout(1500)
        home = await pg.inner_text('#hprog .pline'); await pg.goto('about:blank'); await pg.goto(U + '#/ANAT/_jb'); await pg.wait_for_timeout(1500); jb = await pg.inner_text('#jbprog')
        num = lambda t, k: re.search(k + r'\s*(\d+)', t).group(1)
        ok(num(home, '맞음') == num(jb, '맞음') and num(home, '틀림') == num(jb, '틀림'), f"F4 과목 홈·JB 막대 수 같음 (홈 {num(home, '맞음')}/{num(home, '틀림')} · JB {num(jb, '맞음')}/{num(jb, '틀림')})")
        # ---- F3
        await pg.evaluate("__h.bkClear()")   # 자동 백업은 IndexedDB(C02) — 목록은 __h.bkList()
        await pg.evaluate("__h.autoBak(true,'원고 갱신 전')")
        for _ in range(7): await pg.evaluate("__h.autoBak(false)")
        await pg.goto('about:blank'); await pg.goto(U + '#/ANAT/_home'); await pg.wait_for_timeout(800)
        for _ in range(7): await pg.evaluate("__h.autoBak(false)")
        L = await pg.evaluate("__h.bkList()")
        ok(any(x['cat'] == 'upd' for x in L), f"F3 원고 갱신 전 백업이 따로 남음 {[x['cat'] for x in L]}")
        per = [x for x in L if x['cat'] == 'i']
        ok(len(per) <= 1, f'F3 바뀐 게 없으면 주기 백업을 또 쓰지 않음 (새로고침 뒤에도) — 주기 칸 {len(per)}')
        await pg.evaluate("localStorage.setItem('jblhub.v1.memo.ANAT._home',JSON.stringify('x'))"); await pg.evaluate("__h.autoBak(false)")
        L2 = await pg.evaluate("__h.bkList()")
        ok(len([x for x in L2 if x['cat'] == 'i']) == len(per) + 1, 'F3 바뀌면 새 주기 백업')
        await pg.click('#rstr'); await pg.wait_for_timeout(200)
        ok(await pg.locator('#rpop [data-snapdl]').count() >= 1, 'F3 복원 창에 원고 갱신 전 시점 + 파일로 받기')
        await pg.keyboard.press('Escape')
        # ---- F6·V01·V03 (아이패드 세로·가로)
        for vw, vh in [(820, 1180), (1180, 820)]:
            q = await (await b.new_context(viewport={'width': vw, 'height': vh}, has_touch=vw < 1000)).new_page()
            for s in SUBJ:
                for d in ['_led', '_sum', '_tbl', '_jb']:
                    await q.goto('about:blank'); await q.goto(f'{U}#/{s}/{d}'); await q.wait_for_timeout(700)
                    if d == '_jb': await q.evaluate("document.querySelector('#frev')&&document.querySelector('#frev').click()"); await q.wait_for_timeout(200)
                    ov = await q.evaluate('document.documentElement.scrollWidth-innerWidth')
                    ok(ov <= 1, f'F6 {vw}×{vh} {s}/{d} 가로 밀림 {ov}px')
                    if d in ('_jb', '_sum'):
                        bad = await q.evaluate(OVERLAP); ok(not bad, f'V01·V03 {vw} {s}/{d} 점이 첫 글자와 겹침 {bad}')
            await q.close()
        # ---- F5-a: 팩 판 ≠ 허브 판
        tmp = _os.path.join(J.TMP, 'stale_docs'); shutil.rmtree(tmp, ignore_errors=True); _os.makedirs(tmp + '/packs')
        shutil.copy(J.DOCS + '/index.html', tmp)
        for f in _os.listdir(J.DOCS + '/packs'):
            if '.img.' not in f and not f.endswith('.lx.js'): shutil.copy(J.DOCS + '/packs/' + f, tmp + '/packs/')
        t = open(tmp + '/packs/OMS1.js', encoding='utf-8').read(); open(tmp + '/packs/OMS1.js', 'w', encoding='utf-8').write(re.sub(r'"build": "[^"]+"', '"build": "old00000"', t))
        await pg.goto('about:blank'); await pg.goto('file://' + tmp + '/index.html#/OMS1/DD1/learn'); await pg.wait_for_timeout(1500)
        ok(await pg.locator('#stalebar').count() == 1, 'F5 판이 다르면 새로고침 안내')
        await pg.click('#k-h'); ok(not await pg.evaluate("__h.Kit.mode()"), 'F5 판이 다르면 형광펜 잠금')
        # ---- F5-b: 옛 index + 새 팩 → ?v=판 으로 한 번만 다시 엶(무한 반복 없음)
        old = _os.path.join(J.WORK, '_legacy', 'f2e99d3', 'docs')
        if _os.path.exists(old + '/index.html'):
            mix = _os.path.join(J.TMP, 'mix_docs'); shutil.rmtree(mix, ignore_errors=True); _os.makedirs(mix + '/packs')
            shutil.copy(old + '/index.html', mix)
            for f in _os.listdir(J.DOCS + '/packs'):
                if '.img.' not in f: shutil.copy(J.DOCS + '/packs/' + f, mix + '/packs/')
            srv = serve(mix); navs = []
            q = await b.new_page(); q.on('load', lambda: navs.append(q.url))
            await q.goto(f'http://127.0.0.1:{srv.server_address[1]}/index.html#/OMS1/_home'); await q.wait_for_timeout(2500)
            hb = re.search(r'const HUB_BUILD="([^"]+)"', open(J.DOCS + '/index.html', encoding='utf-8').read()).group(1)
            ok(('v=' + hb) in q.url and len(navs) == 1, f'F5 옛 index가 새 팩을 받으면 ?v={hb}로 한 번 다시 엶 (불러오기 {len(navs)}번)')
            await q.close(); srv.shutdown()
        else: print('  (건너뜀) 옛 배포본 없음 — tools/legacy_base.py 먼저')
        ok(not errs, f'콘솔 오류 0 {errs[:3]}'); await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fail else f'FAIL {len(fail)}'); _sys.exit(1 if fail else 0)
