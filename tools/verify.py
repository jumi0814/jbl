"""허브 검증 (빌드 후 매번: .venv/bin/python tools/verify.py) — 홈 과목 목록 · 모든 문서/탭 렌더 · 강의/JB 이미지 로딩 · 형광펜·빈칸·실행취소·새로고침 복원 · 콘솔 오류 0"""
import sys, os, json, io, base64, threading, http.server, functools, socketserver
from PIL import Image
from playwright.sync_api import sync_playwright
DOCS = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs'))
fail = []
def ok(c, msg):
    print(('  OK  ' if c else '  FAIL') + ' ' + msg)
    if not c: fail.append(msg)
# ---- 1. 이미지 청크 데이터 자체가 전부 디코드되는지
for f in sorted(os.listdir(DOCS + '/packs')):
    if '.img.' not in f: continue
    t = open(f'{DOCS}/packs/{f}', encoding='utf-8').read(); o = json.loads(t[t.index('{'):t.rindex('}') + 1]); n = bad = 0
    for sect in o.values():
        for k, v in sect.items():
            n += 1
            try: Image.open(io.BytesIO(base64.b64decode(v.split(',', 1)[1]))).load()
            except Exception: bad += 1
    ok(bad == 0, f'{f}: 이미지 {n}개 디코드' + (f' — 실패 {bad}' if bad else ''))
# ---- 1b. JB 분해 검사: 답안 안에 다음 문항이 삼켜졌는지 (번호 n 줄이 문항형으로 끝나는데 바로 앞 번호 n-1 줄이 답안에 없음)
import re as _re, html as _html
for f in sorted(os.listdir(DOCS + '/packs')):
    if '.img.' in f or not f.endswith('.js'): continue
    t = open(f'{DOCS}/packs/{f}', encoding='utf-8').read(); pk = json.loads(t[t.index('{'):t.rindex('}') + 1]); hits = []
    for cid, h in pk.get('cards', {}).items():
        m = _re.search(r'<section class="ab jbans">(.*?)</section>', h)
        if not m: continue
        lines = [_html.unescape(_re.sub('<[^>]+>', '', x)) for x in _re.findall(r'<div class="ln[^"]*">(.*?)</div>', m.group(1))]
        nums = [int(mm.group(1)) for mm in (_re.match(r'^\s*(\d{1,2})\s*[.．]', l) for l in lines) if mm]
        for i, l in enumerate(lines):
            mm = _re.match(r'^\s*(\d{1,2})\s*[.．]\s+\S', l)
            if mm and _re.search(r'(\?|？|것은|시오)\s*\.?\s*$', l) and (int(mm.group(1)) - 1) not in nums: hits.append(f'{cid}: {l[:40]}')
    ok(not hits, f'{f}: 답안에 삼켜진 문항 {len(hits)}건 {hits[:3]}')
# ---- 2. 브라우저
class Q(http.server.SimpleHTTPRequestHandler):
    def __init__(s, *a, **k): super().__init__(*a, directory=DOCS, **k)
    def log_message(s, *a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address = True; daemon_threads = True
srv = S(('127.0.0.1', 0), Q); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{srv.server_address[1]}/index.html'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_context(viewport={'width': 1280, 'height': 900}).new_page()
    errs, r404 = [], []
    pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
    pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
    pg.on('response', lambda r: r.status >= 400 and r404.append(r.url.rsplit('/', 1)[-1]))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(URL); pg.wait_for_selector('.scard'); pg.wait_for_timeout(500)
    cards = pg.eval_on_selector_all('.scard', 'es=>es.length'); built = pg.eval_on_selector_all('.scard[data-s]', 'es=>es.map(e=>e.dataset.s)')
    ok(cards == 7, f'허브 홈 과목 카드 {cards}개 (7과목)'); print('       팩 있는 과목:', built)
    for s in built:
        pg.goto(URL); pg.wait_for_selector('.scard'); pg.click(f'.scard[data-s="{s}"]'); pg.wait_for_selector('#side .dbtn')
        docs = pg.eval_on_selector_all('#side .dbtn', 'es=>es.map(e=>e.dataset.d)'); nt = 0
        for d in docs:
            pg.click(f'#side .dbtn[data-d="{d}"]'); pg.wait_for_timeout(80)
            for t in pg.eval_on_selector_all('#dtabs button', 'es=>es.map(e=>e.dataset.t)'):
                pg.click(f'#dtabs button[data-t="{t}"]'); pg.wait_for_timeout(40); nt += 1
        ok(True, f'{s}: 문서 {len(docs)}개 · 탭 {nt}개 열어봄')
        # 강의 정리본 본문 그림(강의 이미지 청크에서 로딩)
        lk = [d for d in docs if not d.startswith('_')]
        for d in lk:
            pg.click(f'#side .dbtn[data-d="{d}"]'); pg.wait_for_timeout(150)
            inl = pg.evaluate('(async()=>{const im=[...document.querySelectorAll("#stage img")];im.forEach(i=>i.loading="eager");await Promise.all(im.map(i=>i.decode().catch(()=>0)));return [im.length,im.filter(i=>i.naturalWidth>0).length]})()')
            ok(inl[0] == inl[1], f'{s}/{d}: 본문 그림 {inl[1]}/{inl[0]} 표시')
        pg.click('#side .dbtn[data-d="_led"]'); pg.wait_for_timeout(200)
        for ed in pg.evaluate('[...new Set([...document.querySelectorAll("#stage [data-jb]")].map(e=>e.dataset.jb.split("-")[0]))]'):
            pg.evaluate(f'document.querySelector("#stage [data-jb^=\'{ed}-\']").click()'); pg.wait_for_timeout(300)
            titles, good = set(), 0
            for _ in range(200):
                tt = pg.inner_text('#mtitle')
                if tt in titles: break
                titles.add(tt); good += pg.evaluate('(async()=>{const i=document.querySelector("#mimg");try{await i.decode()}catch(e){};return i.naturalWidth>0?1:0})()'); pg.click('#mnext')
            ok(good == len(titles) > 0, f'{s} JB {ed}판: 원본 쪽 {good}/{len(titles)} 표시'); pg.click('#mclose')
    # ---- 3. 도구 (첫 과목 첫 강의)
    s = built[0]; pg.goto(URL); pg.evaluate('localStorage.clear()'); pg.goto(URL); pg.wait_for_selector('.scard'); pg.click(f'.scard[data-s="{s}"]'); pg.wait_for_selector('#side .dbtn')
    d = pg.eval_on_selector_all('#side .dbtn', 'es=>es.map(e=>e.dataset.d).filter(x=>!x.startsWith("_"))')[0]; pg.click(f'#side .dbtn[data-d="{d}"]'); pg.wait_for_timeout(300)
    PICK = '''(n=>{const lis=[...document.querySelectorAll('#stage [data-aid] li')].filter(l=>l.offsetParent&&!l.querySelector('[data-rk]')&&/[A-Za-z가-힣]{3}/.test(l.textContent));const li=lis[n];li.scrollIntoView({block:'center'});const w=document.createTreeWalker(li,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){const m=/[A-Za-z가-힣]{3,}/.exec(x.nodeValue);if(m&&!x.parentElement.closest('button,.chip,.noann,[data-rk]')){const r=document.createRange();r.setStart(x,m.index+1);r.setEnd(x,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2,m[0]];}}})'''
    cnt = lambda t: pg.eval_on_selector_all(f'#stage [data-rk={t}]', 'es=>es.length')
    pg.click('#k-h'); a = pg.evaluate(PICK + '(0)'); pg.mouse.click(a[0], a[1]); pg.wait_for_timeout(100); ok(cnt('h') == 1, f'형광펜 ("{a[2]}")')
    pg.click('#k-b'); a = pg.evaluate(PICK + '(1)'); pg.mouse.click(a[0], a[1]); pg.wait_for_timeout(100); ok(cnt('b') == 1, f'빈칸 ("{a[2]}")'); pg.click('#k-b')
    pg.click('#k-undo'); ok(cnt('b') == 0 and cnt('h') == 1, '실행 취소 → 빈칸만 사라짐'); pg.click('#k-redo'); ok(cnt('b') == 1, '다시 실행 → 빈칸 복귀')
    pg.reload(); pg.wait_for_selector('#stage [data-aid]'); pg.wait_for_timeout(500)
    ok(cnt('h') == 1 and cnt('b') == 1, '새로고침 후 형광펜·빈칸 복원')
    pg.evaluate('document.querySelector("#stage [data-rk=b]").click()'); ok(pg.evaluate('document.querySelector("#stage [data-rk=b]").classList.contains("show")'), '빈칸 누르면 열림')
    pg.click('#k-auto'); pg.click('#ago'); pg.wait_for_timeout(200); n = pg.eval_on_selector_all('#stage .rk-b', 'es=>es.length'); ok(n > 1, f'자동 빈칸 {n}개')
    pg.click('#k-undo'); ok(pg.eval_on_selector_all('#stage .rk-b', 'es=>es.length') == 1, '자동 빈칸 실행 취소')
    exp404 = {f'{x}.js' for x in ('OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH') if x not in built}
    ok(set(r404) <= exp404, f'404는 아직 없는 과목 팩뿐 {sorted(set(r404) - exp404)}')
    real = [e for e in errs if 'Failed to load resource' not in e]
    ok(not real, f'콘솔 오류 0 {real[:5]}')
    b.close()
print('RESULT', 'PASS' if not fail else f'FAIL {len(fail)}'); sys.exit(1 if fail else 0)
