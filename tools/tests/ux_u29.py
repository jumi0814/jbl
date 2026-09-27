"""U29 회귀: 그림 확대창 — 카드 그림을 열면 캡션(#mcap)이 보이고 ◀▶는 그 카드 그림 안에서만 돎(범위 전환 '강의 전체' 가능), 버튼 44×44,
JB 원본은 판본별 청크(<SID>.img.jb23/24/25.js) — PHARM 'JB 원본' 첫 클릭 때 받는 파일은 그 판본 청크 하나, 300ms 넘게 걸리면 스피너,
6과목 모든 JB 원본 쪽 버튼(data-jb)의 이미지가 청크에 있음(깨짐 0). http 서버로 열고 청크 응답을 0.8초 늦춰 스피너 확인."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, threading, http.server, functools, json, re
from playwright.async_api import async_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
H = functools.partial(Q, directory=J.DOCS)
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
U = f'http://127.0.0.1:{srv.server_address[1]}/index.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []; got = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('request', lambda r: got.append(r.url.rsplit('/', 1)[-1].split('?')[0]))   # ?v= 캐시 무효화 꼬리 뗌(F5)
        async def slow(route):
            await asyncio.sleep(0.8); await route.continue_()
        await pg.route(re.compile(r'.*\.img\.jb\d\d\.js(\?.*)?$'), slow)
        await pg.goto(U + '#/OMS1/DD1/learn'); await pg.wait_for_timeout(1500)
        fig = await pg.evaluate("(()=>{const t=[...document.querySelectorAll('#stage .tc')].find(c=>c.querySelectorAll('figure[data-fig]').length>=2);const f=t.querySelector('figure[data-fig]');f.scrollIntoView({block:'center'});return [t.id,t.querySelectorAll('figure[data-fig]').length,f.querySelector('figcaption').textContent]})()")
        await pg.click(f'#{fig[0]} figure[data-fig]'); await pg.wait_for_timeout(600)
        r = await pg.evaluate("[document.querySelector('#mcap').textContent, document.querySelector('#mtitle').textContent, document.querySelector('#mscope').hidden]")
        ok(r[0].strip() and r[0].strip()[:6] in fig[2].replace('\n', ' ') and f'/{fig[1]})' in r[1] and not r[2], f'카드 그림 → 캡션·그 카드 그림 {fig[1]}장 안에서 {r}')
        ts = []
        for _ in range(fig[1] + 1):
            ts.append(await pg.inner_text('#mtitle')); await pg.click('#mnext'); await pg.wait_for_timeout(120)
        ok(ts[0] == ts[-1], f'▶ 넘기기가 카드 그림 안에서 한 바퀴 ({len(set(ts))}장)')
        await pg.click('#mscope'); await pg.wait_for_timeout(200)
        t2 = await pg.inner_text('#mtitle'); ok(int(re.search(r'/(\d+)\)', t2).group(1)) > fig[1], f'범위 전환 → 강의 전체 ({t2})')
        wh = await pg.evaluate("[...document.querySelectorAll('#mbar .btn')].filter(b=>!b.hidden).map(b=>[b.offsetWidth,b.offsetHeight])")
        ok(all(w >= 44 and h >= 44 for w, h in wh), f'확대창 버튼 44×44 {wh}')
        await pg.screenshot(path=J.TMP + '/ux_u29_modal.png'); await pg.click('#mclose')
        # PHARM JB 원본 — 판본 청크 하나 + 스피너
        await pg.goto(U + '#/PHARM/_jb/_jb'); await pg.wait_for_timeout(1500); got.clear()
        key = await pg.evaluate("(()=>{const b=document.querySelector('#cards .qc [data-jb]');b.scrollIntoView();return b.dataset.jb})()")
        await pg.evaluate("document.querySelector('#cards .qc [data-jb]').click()"); await pg.wait_for_timeout(450)
        spin = await pg.evaluate("document.querySelector('#imgmodal').classList.contains('on') && !document.querySelector('#mspin').hidden")
        await pg.wait_for_timeout(900)
        jb = [u for u in got if '.img.jb' in u]
        ok(jb == [f'PHARM.img.jb{key.split("-")[0]}.js'], f'JB 원본 {key} → 받은 청크 {jb}')
        ok(spin, '300ms 넘으면 스피너 먼저')
        ok(await pg.evaluate("(async()=>{const i=document.querySelector('#mimg');try{await i.decode()}catch(e){};return i.naturalWidth>0})()"), '불러온 뒤 원본 쪽 표시')
        await pg.click('#mclose'); await pg.unroute(re.compile(r'.*\.img\.jb\d\d\.js(\?.*)?$'))
        # 6과목 모든 data-jb
        for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
            P = (lambda t__: json.loads(t__[t__.index('JBLHUB.register(')+16:-2]))(open(J.DOCS + f'/packs/{s}.js', encoding='utf-8').read())
            keys = set(re.findall(r'data-jb="([0-9]+-[0-9]+)"', json.dumps(P, ensure_ascii=False).replace('\\"', '"')))
            # 이미지 디코드: 청크 파일 내용으로 직접 확인
            bad = 0; tot = 0
            for ed in {k.split('-')[0] for k in keys}:
                t = open(J.DOCS + f'/packs/{s}.img.jb{ed}.js', encoding='utf-8').read(); o = json.loads(t[t.index(',') + 1:t.rindex(",'")])
                for k in keys:
                    if k.startswith(ed + '-'):
                        tot += 1; bad += 0 if o['jb'].get(k, '').startswith('data:image/') else 1
            ok(bad == 0 and tot == len(keys), f'{s} JB 원본 쪽 버튼 {tot}개 — 청크에 이미지 없음 {bad}')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
    srv.shutdown()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
