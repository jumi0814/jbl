"""허브 검증 (빌드 후 매번: .venv/bin/python tools/verify.py) — 홈 과목 목록 · 모든 문서/탭 렌더 · 강의/JB 이미지 로딩(묶음 디코드 · 11-10 그림 파일 목록 imgf의 파일·본문 그림·인용 쪽 키) · 형광펜·빈칸·실행취소·새로고침 복원 · 콘솔 오류 0"""
import sys, os, json, io, base64, threading, http.server, functools, socketserver
NOMAT = {'PHARM': ('ANX',)}   # 강의자료 없이 JB 답으로만 만든 강의(26 자료가 오면 빼기)
from PIL import Image
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import jblpaths as J   # 11-04 분기: 기본 = 그 분기 허브 폴더(J.HUB_DIR — $JBL_Q·$JBL_HUB_DIR)
DOCS = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else J.HUB_DIR)
NSUB = len(J.sids())
fail = []
def ok(c, msg):
    print(('  OK  ' if c else '  FAIL') + ' ' + msg)
    if not c: fail.append(msg)
# ---- 1. 이미지 청크 데이터 자체가 전부 디코드되는지
CHK = {}   # 과목 → 그림 묶음에 든 강의 쪽 키(1a에서 씀)
for f in sorted(os.listdir(DOCS + '/packs')):
    if '.img.' not in f or f.endswith('.img.jb.js'): continue   # .img.jb.js = 옛 index 호환 심(데이터 없음)
    t = open(f'{DOCS}/packs/{f}', encoding='utf-8').read(); o = json.loads(t[t.index('{'):t.rindex('}') + 1]); n = bad = 0
    CHK.setdefault(f.split('.')[0], set()).update((o.get('lec') or {}).keys())
    for sect in o.values():
        for k, v in sect.items():
            n += 1
            try: Image.open(io.BytesIO(base64.b64decode(v.split(',', 1)[1]))).load()
            except Exception: bad += 1
    ok(bad == 0, f'{f}: 이미지 {n}개 디코드' + (f' — 실패 {bad}' if bad else ''))
# ---- 1a. 11-10 그림 파일 방식(팩 imgf — tools/quarters.json 분기 "img": "files") — 목록의 파일이 다 있고(이름의 h8 = 파일 md5 앞 8자 · 디코드)
#      + 모든 팩: 본문 그림(img[data-img])·인용 칩 쪽이 그림 파일 목록이나 그림 묶음에 있음(없으면 허브에서 빈 그림·빈 창 — imgalias 반영)
import re as _re, hashlib as _hl
STUBS = set()   # 자료 대기 과목(강의가 WAIT뿐·문항 0 — 팩 stub) — 3절 도구 시험은 강의가 있는 과목에서
def _walk(o):
    if isinstance(o, str): yield o
    elif isinstance(o, list):
        for x in o: yield from _walk(x)
    elif isinstance(o, dict):
        for x in o.values(): yield from _walk(x)
for f in sorted(os.listdir(DOCS + '/packs')):
    if '.img.' in f or not f.endswith('.js') or f.endswith('.lx.js'): continue
    sid = f[:-3]; t = open(f'{DOCS}/packs/{f}', encoding='utf-8').read(); pk = json.loads(t[t.index('{'):t.rindex('}') + 1])
    if pk.get('stub') or (not (pk.get('stats') or {}).get('cards') and [L.get('k') for L in pk.get('lect') or []] == ['WAIT']): STUBS.add(sid)
    have = set(CHK.get(sid, ())); F = pk.get('imgf')
    if F is not None:
        n = 0; nofile = []; badf = []; idir = os.path.join(DOCS, 'packs', 'img', sid)
        for kind in ('lec', 'jb'):
            for key, h8 in (F.get(kind) or {}).items():
                n += 1; fn = J.img_name(kind, key, h8); fp = os.path.join(idir, fn)
                if not os.path.exists(fp): nofile.append(fn); continue
                b_ = open(fp, 'rb').read()
                try: Image.open(io.BytesIO(b_)).load(); good = _hl.md5(b_).hexdigest()[:8] == h8
                except Exception: good = False
                if not good: badf.append(fn)
                elif kind == 'lec': have.add(key)
        old = [x for x in (os.listdir(idir) if os.path.isdir(idir) else []) if x not in {J.img_name(kd, k_, h_) for kd in ('lec', 'jb') for k_, h_ in (F.get(kd) or {}).items()}]
        ok(not nofile and not badf, f'{f}: 그림 파일 {n}개(packs/img/{sid}/) 있음·이름 지문·디코드' + (f' — 없음 {len(nofile)} {nofile[:3]}' if nofile else '') + (f' — 깨짐 {len(badf)} {badf[:3]}' if badf else '') + (f' · 지난 세대 파일 {len(old)}개(다음 빌드 때 지움)' if old else ''))
    alias = pk.get('imgalias') or {}; need = set()
    for h in _walk(pk):
        if 'data-img="' in h: need.update(_re.findall(r'data-img="([^"]+)"', h))
        if 'class="cite' in h:
            for k_, p_, pp_ in _re.findall(r'<button class="cite[^"]*" data-k="([^"]*)" data-p="([^"]*)"(?: data-pp="([^"]*)")?', h):
                need.update(f'{k_}-{x}' for x in (pp_.split(',') if pp_ else [p_]) if x and x.isascii() and x.isdigit())
    def _has(key):
        k_, p_ = key.rsplit('-', 1); al = alias.get(k_); al = [al] if isinstance(al, str) else list(al or [])
        return any(f'{kk}-{p_}' in have for kk in [k_] + al)
    lost = sorted(x for x in need if not _has(x))
    ok(not lost, f'{f}: 본문 그림·인용 칩 쪽 {len(need)}개가 그림 {"파일 목록" if F is not None else "묶음"}에 있음' + (f' — 없음 {len(lost)} {lost[:5]}' if lost else ''))
# ---- 1b. JB 분해 검사: 답안 안에 다음 문항이 삼켜졌는지 (번호 n 줄이 문항형으로 끝나는데 바로 앞 번호 n-1 줄이 답안에 없음)
import re as _re, html as _html
for f in sorted(os.listdir(DOCS + '/packs')):
    if '.img.' in f or not f.endswith('.js') or f.endswith('.lx.js'): continue
    t = open(f'{DOCS}/packs/{f}', encoding='utf-8').read(); pk = json.loads(t[t.index('{'):t.rindex('}') + 1]); hits = []
    _hb = _re.search(r"const HUB_BUILD=\"([^\"]+)\"", open(f'{DOCS}/index.html', encoding='utf-8').read())
    ok(_hb and pk.get('build') == _hb.group(1), f"{f}: 팩 판 {pk.get('build')} = 허브 판 {_hb and _hb.group(1)} (다르면 6과목 모두 다시 빌드)")
    for cid, h in pk.get('cards', {}).items():
        m = _re.search(r'<section class="ab jbans">(.*?)</section>', h)
        if not m: continue
        lines = [_html.unescape(_re.sub('<[^>]+>', '', x)) for x in _re.findall(r'<div class="ln[^"]*">(.*?)</div>', m.group(1))]
        nums = [int(mm.group(1)) for mm in (_re.match(r'^\s*(\d{1,2})\s*[.．]', l) for l in lines) if mm]
        for i, l in enumerate(lines):
            mm = _re.match(r'^\s*(\d{1,2})\s*[.．]\s+\S', l)
            if mm and _re.search(r'(\?|？|것은|시오)\s*\.?\s*$', l) and (int(mm.group(1)) - 1) not in nums: hits.append(f'{cid}: {l[:40]}')
    ok(not hits, f'{f}: 답안에 삼켜진 문항 {len(hits)}건 {hits[:3]}')
# ---- 1b2. ux2 F12 문제 보기 줄 중간 끊김 — 보기(번호 줄) 사이·끝에 번호 없는 짧은 줄이 끼인 곳(tools/cons/reflow.py stray와 같은 규칙) 0
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cons')); import reflow as _RF
# 10-25 확인한 예외(보기가 아닌 줄): ANAT Q13 앞면(26판 2025 19번) '( 1 )'은 빈칸이고 다음 줄은 새 물음 · GERI C16(23판 2020 5번) 끝 줄은 JB 복원자 메모('그 외 선지는 완전히 벗어난 값들')
STRAY_OK = {('ANAT.js', 'Q13'), ('GERI.js', 'C16')}
for f in sorted(os.listdir(DOCS + '/packs')):
    if '.img.' in f or not f.endswith('.js') or f.endswith('.lx.js'): continue
    t = open(f'{DOCS}/packs/{f}', encoding='utf-8').read(); pk = json.loads(t[t.index('{'):t.rindex('}') + 1]); hits = []
    for cid, h in pk.get('cards', {}).items():
        m = _re.search(r'<div class="qtext">((?:<div class="ln[^>]*>.*?</div>)*)</div>', h)
        if not m: continue
        L = [_html.unescape(_re.sub('<[^>]+>', '', x)) for x in _re.findall(r'<div class="ln[^>]*>(.*?)</div>', m.group(1))]
        for i in range(1, len(L)):
            if (f, cid) in STRAY_OK: continue
            if _RF.stray(L[i - 1], L[i], 10 ** 6) and (i == len(L) - 1 or _RF.CHOICE.match(L[i + 1])): hits.append(f'{cid}: {L[i][:30]}')
    ok(not hits, f'{f}: 보기 사이에 끼인 번호 없는 짧은 줄 {len(hits)}건 {hits[:3]}')
# ---- 1c. JB 문항 id 잠금(C09) — 있던 id의 문제 글자가 바뀌거나 id가 사라지면 실패(옮김 표 tools/<sid>/jb_move.json 필요)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import jblock as _JL
for f, n, e in _JL.lock_errors(DOCS):
    sid = f.split('.')[0]; ok((n is None or n > 0) and not e, f"{f}: JB id 잠금 {'— JB 아직 없음' if n is None else str(n) + '개'}" + (f" — ⚠ {' · '.join(e[:4])}{' …' if len(e) > 4 else ''} → {_JL.need_msg(sid)}" if e else ''))
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
    pg.goto(URL); pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&(document.querySelector('#home .hsj[data-s]')||(%d===0&&document.querySelector('.hkick')))" % NSUB); pg.wait_for_timeout(500)   # 11-04 과목 0인 쿼터(4Q 시작)도
    cards = pg.eval_on_selector_all('#home .hsj', 'es=>es.length'); built = pg.eval_on_selector_all('#home .hsj[data-s]', 'es=>es.map(e=>e.dataset.s)')
    ok(cards == NSUB, f'허브 홈 과목 표 {cards}행 ({NSUB}과목)'); print('       팩 있는 과목:', built)
    if not built:   # 11-04 팩이 아직 없는 쿼터 — 홈·콘솔만 보고 끝
        ok(not errs, f'콘솔 오류 0 {errs[:3]}'); b.close(); print('RESULT', 'FAIL' if fail else 'PASS'); sys.exit(1 if fail else 0)
    # 원고 문법 표기가 화면 글자로 새어 나온 곳(U25) — 숨은 답·접힌 절 포함(textContent). JB 원문(문제·답안·다른 판본·한눈표 답)은 글자 불변이라 제외
    LEAK = r"(()=>{const c=document.querySelector('#stage').cloneNode(true);c.querySelectorAll('.qtext,.jbans,.box0,table.sum .lines,.pickd,.qbody,.pans,.qprev').forEach(e=>e.remove());const t=c.textContent;const o=[];const re=/\*\*|\{r:|\{jb:|==/g;let m;while((m=re.exec(t))&&o.length<3)o.push(t.slice(Math.max(0,m.index-25),m.index+25).replace(/\s+/g,' '));return o;})()"
    leaks = []
    for s in built:
        pg.goto(URL); pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#home .hsj[data-s]')"); pg.click(f'#home .hsj[data-s="{s}"] .hsjn'); pg.wait_for_selector('#side .dbtn')
        docs = pg.eval_on_selector_all('#side .dbtn', 'es=>es.map(e=>e.dataset.d)'); nt = 0
        for d in docs:
            pg.evaluate("d=>document.querySelector('#side .dbtn[data-d=\"'+d+'\"]').click()", d); pg.wait_for_timeout(80)
            for t in pg.eval_on_selector_all('#dtabs button[data-t]', 'es=>es.map(e=>e.dataset.t)'):
                pg.click(f'#dtabs button[data-t="{t}"]'); pg.wait_for_timeout(40); nt += 1
                lk_ = pg.evaluate(LEAK)
                if lk_: leaks.append(f'{d}/{t}: {lk_[0]}')
            if d.startswith('_') and d not in ('_home', '_marks'):
                lk_ = pg.evaluate(LEAK)
                if lk_: leaks.append(f'{d}: {lk_[0]}')
        ok(True, f'{s}: 문서 {len(docs)}개 · 탭 {nt}개 열어봄')
        ok(not leaks, f'{s}: 렌더된 글자에 원고 표기(** {{r: {{jb: ==) 0건 {leaks[:3]}'); leaks.clear()
        # ux2 E03 정리표 세부 칸에 뜻 없는 '행 머리 — ○/×/—'(작은 표를 펼칠 때 열 이름 빠짐) 0 · E10 한눈표 답 핵심이 '해설 참조'뿐인 행 0
        e3 = pg.evaluate("""(s=>{const P=__h.PACKS[s],o=[],e=[];P.lect.forEach(L=>{const d=document.createElement('div');d.innerHTML=L.sum;d.querySelectorAll('.msum .mfull .ci').forEach(c=>{const x=c.cloneNode(true);x.querySelectorAll('.csx').forEach(z=>z.remove());const t=x.textContent,i=t.indexOf(' — ');if(i>0&&/^(—|○|×)\\s*(\\/|$)/.test(t.slice(i+3)))o.push(L.k+': '+t.slice(0,50));});});
          const d=document.createElement('div');d.innerHTML=P.sumall;d.querySelectorAll('table.sum tbody tr').forEach(r=>{const L=r.querySelector('.lines');if(!L)return;const c=L.cloneNode(true);c.querySelectorAll('.alab').forEach(z=>z.remove());const t=c.textContent.replace(/\\s+/g,' ').trim();if(/^\\(?\\s*(해설|해답|아래|위)?\\s*(참조|참고)\\s*\\)?\\s*\\.?$/.test(t))e.push(r.dataset.id);});return [o,e];})""", s)
        ok(not e3[0], f'{s}: 정리표 세부 칸 빈 기호 줄(행 머리 — ○) 0 {e3[0][:2]}')
        ok(not e3[1], f'{s}: 한눈표 답 핵심이 참조뿐인 행 0 {e3[1][:3]}')
        # 강의 정리본 본문 그림(강의 이미지 청크에서 로딩)
        lk = [d for d in docs if not d.startswith('_')]
        for d in lk:
            pg.evaluate("d=>document.querySelector('#side .dbtn[data-d=\"'+d+'\"]').click()", d); pg.wait_for_timeout(150)
            pgb = pg.evaluate('[...document.querySelectorAll("#stage .tc .thead .ko")].filter(k=>{const g=k.querySelector(".pg");return !g||!g.textContent.replace(/[·\\s]/g,"")||/·\\s*$/.test(g.textContent);}).map(k=>k.textContent.trim().slice(0,30))')
            ncard = pg.evaluate('document.querySelectorAll("#stage .tc .thead .ko").length')
            if pgb and len(pgb) == ncard and d in NOMAT.get(s, ()): pgb = []   # 강의자료가 아직 없는 강의(카드 전부 JB 답 기반 — PHARM ANX 10-16)는 쪽 번호 없음이 정상
            ok(not pgb, f'{s}/{d}: 카드 머리 쪽 번호 빈 카드 {len(pgb)} {pgb[:2]}')   # ux2 D08
            inl = pg.evaluate('(async()=>{window.__h&&__h.fillAll&&__h.fillAll();const im=[...document.querySelectorAll("#stage img")];im.forEach(i=>i.loading="eager");await Promise.all(im.map(i=>i.decode().catch(()=>0)));return [im.length,im.filter(i=>i.naturalWidth>0).length]})()')
            ok(inl[0] == inl[1], f'{s}/{d}: 본문 그림 {inl[1]}/{inl[0]} 표시')
        if not pg.evaluate("!!document.querySelector('#side .dbtn[data-d=\"_led\"]')"): continue   # 11-10 빈 과목(자료 대기)은 메뉴에 기출 대장이 없음
        pg.evaluate("document.querySelector('#side .dbtn[data-d=\"_led\"]').click()"); pg.wait_for_timeout(200)
        for ed in pg.evaluate('[...new Set([...document.querySelectorAll("#stage [data-jb]")].map(e=>e.dataset.jb.split("-")[0]))]'):
            pg.evaluate(f'document.querySelector("#stage [data-jb^=\'{ed}-\']").click()'); pg.wait_for_timeout(300)
            titles, good = set(), 0
            for _ in range(200):
                tt = pg.inner_text('#mtitle')
                if tt in titles: break
                titles.add(tt); good += pg.evaluate('(async()=>{const i=document.querySelector("#mimg");try{await i.decode()}catch(e){};return i.naturalWidth>0?1:0})()'); pg.click('#mnext')
            ok(good == len(titles) > 0, f'{s} JB {ed}판: 원본 쪽 {good}/{len(titles)} 표시'); pg.click('#mclose')
    # ---- 3. 도구 (강의가 있는 첫 과목의 첫 강의 — 11-10 자료 대기(stub) 과목은 표시할 글이 없어 건너뜀: 전에는 4Q가 빈 과목뿐일 때 여기서 죽었음)
    real_s = [x for x in built if x not in STUBS]
    if not real_s:
        print('       도구 시험(형광펜·빈칸·실행 취소) 건너뜀 — 강의가 있는 과목이 아직 없음(전부 자료 대기)')
        exp404 = {f'{x}.js' for x in J.sids() if x not in built}
        ok(set(r404) <= exp404, f'404는 아직 없는 과목 팩뿐 {sorted(set(r404) - exp404)}')
        real = [e for e in errs if 'Failed to load resource' not in e]
        ok(not real, f'콘솔 오류 0 {real[:5]}')
        b.close(); print('RESULT', 'PASS' if not fail else f'FAIL {len(fail)}'); sys.exit(1 if fail else 0)
    s = real_s[0]; pg.goto(URL); pg.evaluate('localStorage.clear()'); pg.goto(URL); pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#home .hsj[data-s]')"); pg.click(f'#home .hsj[data-s="{s}"] .hsjn'); pg.wait_for_selector('#side .dbtn')
    d = pg.eval_on_selector_all('#side .dbtn', 'es=>es.map(e=>e.dataset.d).filter(x=>!x.startsWith("_"))')[0]; pg.evaluate("d=>document.querySelector('#side .dbtn[data-d=\"'+d+'\"]').click()", d); pg.wait_for_timeout(300)
    PICK = '''(n=>{const lis=[...document.querySelectorAll('#stage [data-aid] li')].filter(l=>l.offsetParent&&!l.closest('details:not([open])')&&!l.querySelector('[data-rk]')&&/[A-Za-z가-힣]{3}/.test(l.textContent));const li=lis[n];li.scrollIntoView({block:'center'});const w=document.createTreeWalker(li,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){const m=/[A-Za-z가-힣]{3,}/.exec(x.nodeValue);if(m&&!x.parentElement.closest('button,.chip,.noann,[data-rk]')){const r=document.createRange();r.setStart(x,m.index+1);r.setEnd(x,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2,m[0]];}}})'''
    cnt = lambda t: pg.eval_on_selector_all(f'#stage [data-rk={t}]', 'es=>es.length')
    pg.click('#k-h'); a = pg.evaluate(PICK + '(0)'); pg.mouse.click(a[0], a[1]); pg.wait_for_timeout(100); ok(cnt('h') == 1, f'형광펜 ("{a[2]}")')
    pg.click('#k-b'); a = pg.evaluate(PICK + '(1)'); pg.mouse.click(a[0], a[1]); pg.wait_for_timeout(100); ok(cnt('b') == 1, f'빈칸 ("{a[2]}")'); pg.click('#k-b')
    pg.click('#k-undo'); ok(cnt('b') == 0 and cnt('h') == 1, '실행 취소 → 빈칸만 사라짐'); pg.click('#k-redo'); ok(cnt('b') == 1, '다시 실행 → 빈칸 복귀')
    pg.reload(); pg.wait_for_selector('#stage [data-aid]'); pg.wait_for_timeout(500)
    ok(cnt('h') == 1 and cnt('b') == 1, '새로고침 후 형광펜·빈칸 복원')
    pg.evaluate('document.querySelector("#stage [data-rk=b]").click()'); ok(pg.evaluate('document.querySelector("#stage [data-rk=b]").classList.contains("show")'), '빈칸 누르면 열림')
    pg.click('#k-auto'); pg.check('input[value="red"]'); pg.click('#ago'); pg.wait_for_timeout(200); n = pg.eval_on_selector_all('#stage .rk-b', 'es=>es.length'); ok(n > 1, f'자동 빈칸 {n}개')
    pg.click('#k-undo'); ok(pg.eval_on_selector_all('#stage .rk-b', 'es=>es.length') == 1, '자동 빈칸 실행 취소')
    exp404 = {f'{x}.js' for x in J.sids() if x not in built}
    ok(set(r404) <= exp404, f'404는 아직 없는 과목 팩뿐 {sorted(set(r404) - exp404)}')
    real = [e for e in errs if 'Failed to load resource' not in e]
    ok(not real, f'콘솔 오류 0 {real[:5]}')
    b.close()
print('RESULT', 'PASS' if not fail else f'FAIL {len(fail)}'); sys.exit(1 if fail else 0)
