"""C11 회귀: 저장소 보호 확인과 홈 화면 앱 — docs/index.html head에 manifest 링크·apple 메타 · manifest.webmanifest 유효 JSON(name·display standalone·start_url·아이콘 192/512) ·
아이콘·manifest가 http 200 · 복원 창·도움말에 '저장소 보호' · persisted()가 false면 허브 홈 💾 패널에 홈 화면 앱 안내 한 줄([알겠어요] → LS a2hsNote)·백업 알림 기준 2일.
맥 1280×900 + 아이패드 세로 820×1180 · 가로 1180×820. 스크린샷 work/_tmp/ux2i_c11_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, re, threading, http.server, socketserver, urllib.request
from playwright.async_api import async_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
h = open(J.DOCS + '/index.html', encoding='utf-8').read(); head = h[:h.index('</head>')]
ok('<link rel="manifest" href="manifest.webmanifest">' in head and 'apple-mobile-web-app-capable' in head and 'rel="apple-touch-icon"' in head, 'head에 manifest 링크·apple 메타·apple-touch-icon')
m = json.load(open(J.DOCS + '/manifest.webmanifest', encoding='utf-8'))
ok(m['name'] == 'JBL 허브' and m['display'] == 'standalone' and m['start_url'] == './' and {i['sizes'] for i in m['icons']} == {'192x192', '512x512'}, f'manifest {m["name"]} · {m["display"]} · 아이콘 {[i["sizes"] for i in m["icons"]]}')
class Q(http.server.SimpleHTTPRequestHandler):
    def __init__(s, *a, **k): super().__init__(*a, directory=J.DOCS, **k)
    def log_message(s, *a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address = True; daemon_threads = True
srv = S(('127.0.0.1', 0), Q); threading.Thread(target=srv.serve_forever, daemon=True).start(); BASE = f'http://127.0.0.1:{srv.server_address[1]}/'
for f in ['manifest.webmanifest', 'icon-192.png', 'icon-512.png']:
    r = urllib.request.urlopen(BASE + f); b = r.read()
    ok(r.status == 200 and (f.endswith('webmanifest') or b[:8] == b'\x89PNG\r\n\x1a\n'), f'{f} → {r.status} ({len(b)} B)')
async def run(b, vp, touch, tag, persisted):
    ctx = await b.new_context(viewport=vp, has_touch=touch)
    if persisted is not None: await ctx.add_init_script(f"(()=>{{const v={str(persisted).lower()};try{{Object.defineProperty(navigator,'storage',{{value:{{persisted:()=>Promise.resolve(v),persist:()=>Promise.resolve(v),estimate:()=>Promise.resolve({{usage:1e6,quota:1e9}})}},configurable:true}});}}catch(e){{}}}})()")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await pg.goto(BASE + 'index.html#/'); await pg.wait_for_selector('.scard[data-s="OMS1"]'); await pg.wait_for_timeout(400)
    await pg.evaluate("document.querySelector('#bkup').click()"); await pg.click('#rstr'); await pg.wait_for_selector('#rpop .rstore'); t = await pg.inner_text('#rpop .rstore')
    want = {True: '허용됨', False: '안 됨', None: ''}[persisted]
    ok('저장소 보호' in t and want in t, f"복원 창 {re.search(r'저장소 보호[^\n]*', t).group(0) if '저장소 보호' in t else t[-60:]!r}")
    await pg.screenshot(path=J.TMP + f'/ux2i_c11_restore_{tag}.png'); await pg.keyboard.press('Escape')
    await pg.keyboard.press('?'); await pg.wait_for_timeout(150); ht = await pg.inner_text('#hpers'); ok('저장소 보호' in ht and want in ht, f'도움말 {ht!r}'); await pg.keyboard.press('Escape')
    if persisted is False:
        a = await pg.inner_text('#a2hs'); ok('홈 화면에 추가' in a, f'안 됨 → 허브 홈 안내 한 줄 {a[:40]!r}')
        await pg.screenshot(path=J.TMP + f'/ux2i_c11_a2hs_{tag}.png')
        ok(await pg.evaluate("__h.bkLimit()") == 2, '안 됨 → 백업 알림 기준 2일')
        await pg.click('#a2hs [data-a2hsx]'); await pg.reload(); await pg.wait_for_selector('.scard[data-s="OMS1"]'); await pg.wait_for_timeout(400)
        ok(await pg.inner_text('#a2hs') == '' and await pg.evaluate("localStorage.getItem('jblhub.v1.a2hsNote')") == '1', '[알겠어요] 뒤에는 안내 없음(한 번)')
    if persisted is True: ok(await pg.inner_text('#a2hs') == '', '허용됨 → 안내 없음')
    ok(not errs, f'pageerror 0 ({errs[:2]})'); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac', True)
        await run(b, {'width': 820, 'height': 1180}, True, 'ipp', False)
        await run(b, {'width': 1180, 'height': 820}, True, 'ipl', None)
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
_sys.exit(1 if fails else 0)
