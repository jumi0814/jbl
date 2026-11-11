"""11-11 W3 허브가 4Q 그림을 파일로 읽음 — 그림 주소 한 곳(imgUrl: 메모리 → 팩 imgf 파일 주소 → 묶음).
시험 사이트 = qsite.filesite: 3q/ 허브의 사본(3qf/)에서 한 과목(IMPL)만 파일 방식(묶음 js를 packs/img/<SID>/<키>.<h8>.webp|jpg로 풀고 팩에 imgf · 묶음 파일은 사본에 없음),
다른 과목은 묶음 방식 그대로 → 두 방식이 한 허브에서 함께 돎(정체성은 3q 그대로 — 그림 길만 시험).
① 학습 그림(묶음 요청 0 · 주소 = 규칙 · 자리 안 밀림 · 목록에 없는 키는 그림 빼기) ② 그림 창 쪽 넘김·범위 전환·인용 칩 ③ JB 원본 쪽 ④ 미리 보기 ⑤ 그림빵·예상 탭
⑥ 넘버링에 강의 그림(자리표 → 파일 주소 · 그림빵 합성 canvas) · 붙여 넣은 packs/img 주소 → 자리표(sanitize) ⑦ Word 내보내기에 그림 ⑧ 파일 하나 404 → 한 번 다시 → 같은 크기 자리 표시 → 누르면 다시
⑨ 묶음 방식 과목: 강의 15개 뒤 힙이 '2강 뒤 + 여유' 안 · 받은 강의 묶음 ≤ 2 · 다시 가면 다시 받음 · 그림 창이 열려 있으면 안 비움 ⑩ 인쇄 준비(beforeprint·print 매체 → 안 받은 그림 받기)."""
import json, re, zipfile, tempfile
from qsite import *
from playwright.sync_api import sync_playwright
rel = build(); fr, IMGF = filesite(rel); base = serve(); U = url(base, fr); SID = 'IMPL'; HEAP_ROOM = 30   # MB — 2강 뒤 대비 여유(측정: 고친 뒤 +4 · 고치기 전 +119)
FURL = lambda kind, k: f"packs/img/{SID}/{'jb' if kind == 'jb' else ''}{k}.{IMGF[kind][k]}.{'jpg' if kind == 'jb' else 'webp'}"

def wait(pg, js, arg=None, n=100, ms=100):
    for _ in range(n):
        try:
            if pg.evaluate(js, arg): return True
        except Exception: pass
        pg.wait_for_timeout(ms)
    return False
LOADED1 = "s=>{const i=document.querySelector(s);return !!(i&&i.complete&&i.naturalWidth>0)}"
MODAL = "(()=>{const i=document.querySelector('#mimg');return {on:document.querySelector('#imgmodal').classList.contains('on'),src:i.getAttribute('src')||'',nw:i.naturalWidth,vis:i.style.visibility,spin:!document.querySelector('#mspin').hidden,title:document.querySelector('#mtitle').textContent,err:i.classList.contains('imgerr')}})()"

with sync_playwright() as p:
    b = p.chromium.launch(args=['--enable-precise-memory-info'])
    ctx = b.new_context(viewport={'width': 1280, 'height': 900}, accept_downloads=True); pg = ctx.new_page(); errs = []; reqs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('request', lambda r: reqs.append(r.url.split('/packs/', 1)[1]) if '/packs/' in r.url else None)
    print(f'== 파일 방식 사본 {U} (그림 파일 강의 쪽 {len(IMGF["lec"])} · JB 원본 쪽 {len(IMGF["jb"])})')
    pg.goto(U + '#/'); pg.wait_for_timeout(1200); pg.evaluate("localStorage.clear();sessionStorage.clear()"); pg.goto('about:blank'); pg.goto(U + f'#/{SID}/_home')
    ok(wait(pg, f"()=>!!(window.__h&&__h.PACKS['{SID}'])"), f'{SID} 팩 도착')
    ok(pg.evaluate(f"!!__h.imgF('{SID}')&&!Object.keys(__h.PACKS['{SID}'].imgv||{{}}).length&&!__h.imgF('PHARM')"), f'{SID} = 파일 방식(imgf · imgv 빈 값) · PHARM = 묶음 방식 — 한 허브에 함께')
    LEC = pg.evaluate(f"__h.PACKS['{SID}'].lect.map(L=>[L.k,(L.learn.match(/data-img=\"[^\"]+\"/g)||[]).map(x=>x.slice(10,-1)),__h.docTabs(__h.PACKS['{SID}'],L.k).map(x=>x[0])])")
    LEC = [x for x in LEC if len(x[1]) >= 5]; K, FIGS, TABS = LEC[0]; K2 = LEC[1][0]; K3 = LEC[2][0]

    # ---- ① 학습 그림
    pg.evaluate(f"location.hash='#/{SID}/{K}/learn'"); ok(wait(pg, "()=>document.querySelectorAll('#stage img[data-img]').length>0"), f'① 학습 탭({K}) 그림 자리')
    k0 = pg.evaluate("document.querySelector('#stage img[data-img]').dataset.img"); ok(wait(pg, LOADED1, '#stage img[data-img]'), f'① 첫 그림 받음({k0})')
    s0 = pg.evaluate("document.querySelector('#stage img[data-img]').getAttribute('src')")
    ok(s0 == FURL('lec', k0), f'① 주소 = packs/img/<SID>/<키>.<h8>.webp ({s0})')
    ok(not [r for r in reqs if r.startswith(SID + '.img.')] and any(r.startswith(f'img/{SID}/') for r in reqs), f'① 묶음 요청 0 · 그림 파일 요청 {len([r for r in reqs if r.startswith("img/" + SID + "/")])}번(화면 가까운 것만)')
    nfig = pg.evaluate("document.querySelectorAll('#stage img[data-img]').length"); want = len([k for k in FIGS if k in IMGF['lec']])
    ok(nfig == want, f'① 목록에 있는 그림은 다 자리 있음({nfig}/{want})')
    far = pg.evaluate("(()=>{const L=[...document.querySelectorAll('#stage .tc .figs img[data-img]')].filter(i=>!i.getAttribute('src')&&i.offsetParent!==null);const i=L[L.length-1];if(!i)return null;const r=i.getBoundingClientRect();return {k:i.dataset.img,w:+i.getAttribute('width'),h:+i.getAttribute('height'),cw:r.width,ch:r.height}})()")
    ok(bool(far) and far['w'] > 0 and abs(far['ch'] - far['cw'] * far['h'] / far['w']) <= 2, f"① 아직 안 받은 그림도 자리(폭·높이)가 잡혀 있음 {far and (far['k'], round(far['cw']), round(far['ch']))}")
    if far:
        pg.evaluate("k=>document.querySelector('#stage img[data-img=\"'+k+'\"]').scrollIntoView({block:'center'})", far['k'])
        ok(wait(pg, LOADED1, f'#stage img[data-img="{far["k"]}"]'), '① 스크롤해 가면 받음')
        ch2 = pg.evaluate("k=>document.querySelector('#stage img[data-img=\"'+k+'\"]').getBoundingClientRect().height", far['k'])
        ok(abs(ch2 - far['ch']) <= 2, f"① 받은 뒤 높이 그대로(화면 안 밀림 {round(far['ch'])} → {round(ch2)})")
    gone = FIGS[1]; h8 = IMGF['lec'][gone]
    pg.evaluate(f"k=>{{delete __h.PACKS['{SID}'].imgf.lec[k];location.hash='#/{SID}/_home'}}", gone); pg.wait_for_timeout(600); pg.evaluate(f"location.hash='#/{SID}/{K}/learn'"); wait(pg, "()=>document.querySelectorAll('#stage img[data-img]').length>0"); pg.wait_for_timeout(400)
    r = pg.evaluate("k=>[!!document.querySelector('#stage figure[data-fig=\"'+k+'\"]'),document.querySelectorAll('#stage img[data-img]').length]", gone)
    ok(r[0] is False and r[1] == want - FIGS.count(gone), f'① 목록에 없는 키({gone}) = 지금처럼 그림 빼기({r[1]}/{want})')
    pg.evaluate(f"([k,h])=>{{__h.PACKS['{SID}'].imgf.lec[k]=h;location.hash='#/{SID}/_home'}}", [gone, h8]); pg.wait_for_timeout(500)

    # ---- ② 그림 창: 카드 그림 → 쪽 넘김 → 강의 전체 · 인용 칩
    pg.evaluate(f"location.hash='#/{SID}/{K}/learn'"); wait(pg, LOADED1, '#stage img[data-img]'); reqs.clear()
    pg.evaluate("document.querySelector('#stage figure[data-fig] img').click()"); ok(wait(pg, "()=>{const i=document.querySelector('#mimg');return document.querySelector('#imgmodal').classList.contains('on')&&i.complete&&i.naturalWidth>0&&i.style.visibility!=='hidden'}"), '② 그림을 누르면 그림 창(바로 — 묶음을 기다리지 않음)')
    m = pg.evaluate(MODAL); ok(m['src'] == FURL('lec', k0) and not m['spin'] and '(1/' in m['title'], f"② 그림 창 주소·제목 {m['src'][-28:]} · {m['title']!r}")
    allk = sorted([k for k in IMGF['lec'] if k.split('-')[0] == k0.split('-')[0]], key=lambda x: int(x.split('-')[1]))
    if pg.evaluate("!document.querySelector('#mscope').hidden"): pg.click('#mscope'); pg.wait_for_timeout(300)
    m = pg.evaluate(MODAL); n_all = int(re.search(r'/(\d+)\)', m['title']).group(1)); ok(n_all == len(allk), f'② 범위 전환 → 강의 전체 쪽 수 = 파일 목록({n_all}/{len(allk)})')
    i0 = allk.index(k0); pg.click('#mnext'); ok(wait(pg, "u=>{const i=document.querySelector('#mimg');return i.getAttribute('src')===u&&i.complete&&i.naturalWidth>0&&i.style.visibility!=='hidden'}", FURL('lec', allk[(i0 + 1) % len(allk)])), f'② ▶ 다음 쪽({allk[(i0 + 1) % len(allk)]}) 받아서 보임')
    pg.click('#mprev'); pg.click('#mprev'); ok(wait(pg, "u=>{const i=document.querySelector('#mimg');return i.getAttribute('src')===u&&i.complete&&i.naturalWidth>0}", FURL('lec', allk[i0 - 1])), '② ◀ 이전 쪽')
    pg.click('#mclose'); pg.wait_for_timeout(300)
    ck = pg.evaluate("K=>{const c=[...document.querySelectorAll('#stage button.cite[data-p]')].find(c=>c.dataset.p&&K[c.dataset.k+'-'+c.dataset.p]);if(!c)return null;c.click();return c.dataset.k+'-'+c.dataset.p}", IMGF['lec'])
    ok(bool(ck) and wait(pg, "u=>{const i=document.querySelector('#mimg');return document.querySelector('#imgmodal').classList.contains('on')&&i.getAttribute('src')===u&&i.naturalWidth>0}", FURL('lec', ck) if ck else ''), f'② 인용 칩 [[{ck}]] → 그 쪽 그림 창')
    pg.click('#mclose'); pg.wait_for_timeout(300)
    ok(not [r for r in reqs if r.startswith(SID + '.img.')], '② 그림 창도 묶음 요청 0')

    # ---- ③ JB 원본 쪽(기출 대장 단추 · JB 카드 단추)
    reqs.clear(); pg.evaluate(f"location.hash='#/{SID}/_led'"); ok(wait(pg, "()=>!!document.querySelector('#stage [data-jb]')"), '③ 기출 대장 JB 원본 쪽 단추')
    jk = pg.evaluate("K=>{const b=[...document.querySelectorAll('#stage [data-jb]')].find(b=>K[b.dataset.jb]);b.click();return b.dataset.jb}", IMGF['jb'])
    ok(wait(pg, "u=>{const i=document.querySelector('#mimg');return document.querySelector('#imgmodal').classList.contains('on')&&i.getAttribute('src')===u&&i.complete&&i.naturalWidth>0&&i.style.visibility!=='hidden'}", FURL('jb', jk)), f'③ JB 원본 {jk} → {FURL("jb", jk)}')
    m = pg.evaluate(MODAL); ed = jk.split('-')[0]; nj = len([k for k in IMGF['jb'] if k.split('-')[0] == ed])
    ok(m['title'].startswith(f'JB {ed}판 원본 {jk.split("-")[1]}쪽') and f'/{nj})' in m['title'], f"③ 제목·쪽 수 {m['title']!r}")
    pg.click('#mnext'); ok(wait(pg, "()=>{const i=document.querySelector('#mimg');return i.complete&&i.naturalWidth>0&&i.style.visibility!=='hidden'}"), '③ ▶ 다음 원본 쪽'); pg.click('#mclose'); pg.wait_for_timeout(300)
    pg.evaluate(f"location.hash='#/{SID}/_jb/_jb'"); wait(pg, "()=>!!document.querySelector('#cards .qc [data-jb]')")
    jk2 = pg.evaluate("(()=>{const b=document.querySelector('#cards .qc [data-jb]');b.click();return b.dataset.jb})()")
    ok(wait(pg, "u=>{const i=document.querySelector('#mimg');return document.querySelector('#imgmodal').classList.contains('on')&&i.getAttribute('src')===u&&i.naturalWidth>0}", FURL('jb', jk2)), f'③ JB 카드 [JB 원본 n쪽] {jk2}')
    pg.click('#mclose'); pg.wait_for_timeout(300); ok(not [r for r in reqs if '.img.' in r and r.startswith(SID)], '③ JB 원본도 묶음 요청 0')

    # ---- ④ 미리 보기(⭐ 연도 칩 → JB 미리보기 → 답 보기 = fillThumbs)
    pg.evaluate(f"location.hash='#/{SID}/{K}/learn'"); wait(pg, "()=>!!document.querySelector('#stage .tc')"); pg.wait_for_timeout(500)
    pk = pg.evaluate("(()=>{const c=document.querySelector('#stage .c-exam .jbchip[data-go], #stage .tchips .chip.yr[data-go]');if(!c)return false;c.scrollIntoView({block:'center'});c.click();return true})()")
    ok(pk and wait(pg, "()=>!!document.querySelector('#jbpeek.on .jpshow')"), '④ 미리 보기 열림')
    if pk:
        pg.evaluate("(k=>{const p=document.querySelector('#jbpeek'),a=p.querySelector('.jpa');const f=document.createElement('figure');f.dataset.fig=k;f.innerHTML='<img data-img=\"'+k+'\" alt=\"\" width=\"740\" height=\"524\">';a.appendChild(f);p.querySelector('.jpshow').click()})", FIGS[2])
        ok(wait(pg, "u=>{const i=document.querySelector('#jbpeek img[data-img]');return !!i&&i.getAttribute('src')===u&&i.complete&&i.naturalWidth>0}", FURL('lec', FIGS[2])), '④ 미리 보기 [답 보기] → 그 안의 강의 그림도 파일 주소로')
        pg.evaluate("document.querySelector('#jbpeek .jpx').click()")

    # ---- ⑤ 그림빵 탭 · 예상 탭
    for t, nm in (('fig', '그림빵'), ('pred', '예상')):
        kk = next((x[0] for x in LEC if t in x[2]), None)
        if not kk: print(f'  --   ⑤ {nm} 탭이 있는 강의 없음 — 건너뜀'); continue
        pg.evaluate(f"location.hash='#/{SID}/{kk}/{t}'"); wait(pg, "()=>document.querySelectorAll('#stage img[data-img]').length>0"); pg.wait_for_timeout(300)
        pg.evaluate("document.querySelectorAll('#stage img[data-img]').forEach(i=>{i.loading='eager'})")
        r = pg.evaluate("(async()=>{const L=[...document.querySelectorAll('#stage img[data-img]')];await Promise.all(L.map(i=>i.decode().catch(()=>0)));return [L.length,L.filter(i=>/^packs\\/img\\//.test(i.getAttribute('src')||'')&&i.naturalWidth>0).length,document.querySelectorAll('#stage .gbm').length]})()")
        ok(r[0] > 0 and r[0] == r[1] and (t != 'fig' or r[2] > 0), f'⑤ {nm} 탭({kk}) 그림 {r[1]}/{r[0]}' + (f' · 가림 상자 {r[2]}' if t == 'fig' else ''))

    # ---- ⑥ 넘버링에 강의 그림(예상문제 그림·그림빵 자리표) · 붙여 넣은 packs/img 주소 → 자리표
    pg.evaluate("__h.xsReady()"); pg.wait_for_timeout(300); kp = FIGS[3]   # 가림 상자 없는 강의 쪽 그림 자리표가 든 문제 하나(붙여 넣기·옛 가져오기와 같은 꼴)
    pg.evaluate("([k,v])=>__h.stSet(k,JSON.stringify(v))", [f'num.i.{SID}.zimg', {'id': 'zimg', 's': SID, 'kind': 'user', 'lec': '', 'q': f'<p>그림 문제</p><p><img data-lecimg="{SID}|{kp}" width="740" height="524" alt=""></p>', 'a': '답', 'st': '', 'note': '', 'tags': [], 'yrs': [], 'src': [], 'ref': None, 'done': False, 'o': 1, 'c': 1000, 'u': 1000, 'del': False, 'rv': [], 'rvok': False, 'prev': None, 'pm': None}])
    reqs.clear(); pg.evaluate(f"location.hash='#/_num/{SID}'"); ok(wait(pg, "()=>!!document.querySelector('.nm-side [data-act=imp]')", n=150), '⑥ 내 넘버링 열림')
    pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); pg.wait_for_timeout(700)
    pg.select_option('[data-if=src]', 'pred'); pg.select_option('[data-if=ty]', ''); pg.wait_for_timeout(300)
    pg.click('[data-ib=all]'); pg.wait_for_timeout(500); pg.click('[data-cf2=ok]'); pg.wait_for_timeout(1500); pg.click('.nm-ov [data-x]'); pg.wait_for_timeout(700)
    ok(wait(pg, "()=>{const L=[...document.querySelectorAll('#numv img[data-lecimg]')];return L.length>0&&L.every(i=>i.getAttribute('src'))}", n=200), '⑥ 예상문제를 넣으면 강의 그림 자리표가 그림으로')
    r = pg.evaluate("(async()=>{const L=[...document.querySelectorAll('#numv img[data-lecimg]')];await Promise.all(L.map(i=>i.decode().catch(()=>0)));const P=L.filter(i=>!i.dataset.gbm),G=L.filter(i=>i.dataset.gbm);return {n:L.length,plain:P.length,pf:P.filter(i=>/^packs\\/img\\//.test(i.getAttribute('src'))&&i.naturalWidth>0).length,gb:G.length,gd:G.filter(i=>/^data:image\\/jpeg/.test(i.getAttribute('src'))&&i.naturalWidth>0).length}})()")
    ok(r['plain'] > 0 and r['plain'] == r['pf'] and pg.evaluate("k=>(document.querySelector('#numv img[data-lecimg=\"'+k+'\"]')||{getAttribute(){}}).getAttribute('src')", f'{SID}|{kp}') == FURL('lec', kp), f"⑥ 강의 쪽 그림 = 파일 주소 그대로({r['pf']}/{r['plain']} · {FURL('lec', kp)})")
    ok(r['gb'] > 0 and r['gb'] == r['gd'], f"⑥ 그림빵(가림 상자) = 파일에서 canvas로 합성({r['gd']}/{r['gb']} — 나눠 그리는 뒤쪽 문제까지)")
    ok(not [x for x in reqs if x.startswith(SID + '.img.')], '⑥ 넘버링도 묶음 요청 0')
    saved = pg.evaluate("__h.stKeys('num.i.').map(k=>__h.stGet(k)).filter(v=>/data-lecimg/.test(v))"); ok(saved and not any('packs/img' in v or 'data:image' in v for v in saved), f'⑥ 저장된 문제에는 자리표만(그림 주소·글자 없음 — {len(saved)}문제)')
    here = U.rsplit('/', 1)[0] + '/'; kq = FIGS[0]
    S = lambda h: pg.evaluate("h=>JBLNUM._sanitize(h,{paste:true})", h)
    o1 = S(f'<p>글<img src="{here}{FURL("lec", kq)}" width="740" height="524" data-img="{kq}" loading="lazy"></p>')
    ok(f'data-lecimg="{SID}|{kq}"' in o1 and 'src=' not in o1 and 'width="740"' in o1 and 'height="524"' in o1, f'⑥ 붙여 넣은 강의 쪽 그림(packs/img 주소) → 자리표 {o1[:90]!r}')
    o2 = S(f'<img src="{here}{FURL("jb", jk)}">'); ok(f'data-lecimg="{SID}|jb{jk}"' in o2 and 'src=' not in o2, f'⑥ 붙여 넣은 JB 원본 쪽 → 자리표 {o2!r}')
    o3 = S(f'<img src="https://example.com/packs/img/{SID}/{kq}.{IMGF["lec"][kq]}.webp"><img src="{here}packs/img/{SID}/ZZZ-999.00000000.webp"><img src="data:image/png;base64,iVBORw0KGgo=">')
    ok('data-lecimg' not in o3 and 'example.com' not in o3 and 'data:image/png' in o3, f'⑥ 다른 곳 주소·목록에 없는 키는 전처럼 버림 · dataURI 그림은 전처럼 둠 {o3[:60]!r}')
    hj = pg.evaluate(f"__h.hostImg('{SID}','jb{jk}')"); ok(hj == FURL('jb', jk), f'⑥ 자리표 JB 원본 쪽 → 그림 주소 {hj}')

    # ---- ⑦ Word 내보내기에 그림
    pg.evaluate("document.querySelector('.nm-side [data-act=print]').click()"); pg.wait_for_timeout(600)
    TMP = tempfile.mkdtemp(prefix='q_img_')
    with pg.expect_download(timeout=60000) as dl: pg.click('.nm-ov [data-po=docx]')
    f = os.path.join(TMP, 'out.docx'); dl.value.save_as(f); z = zipfile.ZipFile(f); med = [n for n in z.namelist() if n.startswith('word/media/')]
    big = [n for n in med if len(z.read(n)) > 5000]
    ok(len(big) >= r['n'], f"⑦ Word(.docx)에 강의 그림 포함(그림 파일 {len(big)}개 ≥ 화면의 강의 그림 {r['n']}개)")
    pg.evaluate("(()=>{const x=document.querySelector('.nm-ov [data-x]');if(x)x.click()})()"); pg.wait_for_timeout(300)

    # ---- ⑧ 파일 하나 404 → 0.8초 뒤 한 번 다시(?r=) → 같은 크기 자리 표시 → 누르면 다시
    bad = pg.evaluate(f"__h.PACKS['{SID}'].lect.find(L=>L.k==='{K2}').learn.match(/data-img=\"([^\"]+)\"/)[1]"); cnt = {'n': 0, 'urls': [], 'on': True}; name = FURL('lec', bad).rsplit('/', 1)[1]
    def h404(route):
        cnt['n'] += 1; cnt['urls'].append(route.request.url)
        if cnt['on']: route.fulfill(status=404, body='')
        else: route.continue_()
    pg.route(re.compile(r'.*/packs/img/' + SID + '/' + re.escape(name) + r'(\?.*)?$'), h404)
    pg.evaluate(f"location.hash='#/{SID}/{K2}/learn'"); wait(pg, "()=>document.querySelectorAll('#stage img[data-img]').length>0")
    ok(wait(pg, "k=>document.querySelector('#stage img[data-img=\"'+k+'\"]').classList.contains('imgerr')", bad, n=80), f'⑧ 못 받은 그림({bad}) → 자리 표시')
    e = pg.evaluate("k=>{const i=document.querySelector('#stage img[data-img=\"'+k+'\"]'),r=i.getBoundingClientRect(),t=document.querySelector('#toast');return {src:(i.getAttribute('src')||'').slice(0,26),w:+i.getAttribute('width'),h:+i.getAttribute('height'),cw:r.width,ch:r.height,nw:i.naturalWidth,nh:i.naturalHeight,title:i.title,toast:t&&t.style.display!=='none'?t.innerText:''}}", bad)
    pg.evaluate("__h.fillAll();document.querySelectorAll('#stage img[data-img]').forEach(i=>{i.loading='eager'})"); wait(pg, "()=>[...document.querySelectorAll('#stage .tc .figs img[data-img]')].filter(x=>x.offsetParent!==null).every(x=>x.complete)", n=150)
    e['others'] = pg.evaluate("[...document.querySelectorAll('#stage img[data-img]')].filter(x=>x.complete&&x.naturalWidth>0&&!x.classList.contains('imgerr')&&/^packs\\/img\\//.test(x.getAttribute('src'))).length"); e['errs'] = pg.evaluate("document.querySelectorAll('#stage img.imgerr').length")
    ok(cnt['n'] == 2 and '?r=' in cnt['urls'][1] and '?' not in cnt['urls'][0], f"⑧ 한 번 다시 받음(요청 {cnt['n']}번 · 둘째는 캐시를 피해 ?r=)")
    ok(e['src'].startswith('data:image/svg+xml') and e['nw'] == e['w'] and e['nh'] == e['h'] and abs(e['ch'] - e['cw'] * e['h'] / e['w']) <= 2, f"⑧ 자리 표시 = 같은 크기({e['nw']}×{e['nh']} · 화면 {round(e['cw'])}×{round(e['ch'])})")
    ok('받지 못했어요' in e['toast'] and '다시' in e['toast'] and '다시' in e['title'] and e['others'] > 0 and e['errs'] == 1, f"⑧ 알림 [다시] · 다른 그림은 그대로 받음({e['others']}장 · 자리 표시 {e['errs']}) {e['toast'][:40]!r}")
    cnt['on'] = False; pg.evaluate("k=>document.querySelector('#stage img[data-img=\"'+k+'\"]').click()", bad)
    ok(wait(pg, "k=>{const i=document.querySelector('#stage img[data-img=\"'+k+'\"]');return !i.classList.contains('imgerr')&&i.complete&&i.naturalWidth>0&&/^packs\\/img\\//.test(i.getAttribute('src'))}", bad), '⑧ 자리 표시를 누르면 다시 받아 그림으로')
    ok(not pg.evaluate("document.querySelector('#imgmodal').classList.contains('on')"), '⑧ 자리 표시를 누를 때 그림 창은 안 열림')
    pg.unroute(re.compile(r'.*/packs/img/' + SID + '/' + re.escape(name) + r'(\?.*)?$'))
    jb3 = sorted(IMGF['jb'])[-1]; pat = re.compile(r'.*/packs/img/' + SID + '/' + re.escape(FURL('jb', jb3).rsplit('/', 1)[1]) + r'(\?.*)?$'); pg.route(pat, lambda route: route.fulfill(status=404, body=''))
    pg.evaluate(f"__h.openImg('jb','{jb3}')"); ok(wait(pg, "()=>{const i=document.querySelector('#mimg');return i.classList.contains('imgerr')&&i.style.visibility!=='hidden'&&document.querySelector('#mspin').hidden}", n=80), f'⑧ 그림 창에서 못 받은 쪽({jb3}) → 자리 표시(스피너가 남지 않음)')
    pg.unroute(pat); pg.evaluate("document.querySelector('#mimg').click()"); ok(wait(pg, "u=>{const i=document.querySelector('#mimg');return !i.classList.contains('imgerr')&&i.naturalWidth>0&&(i.getAttribute('src')||'').split('?')[0]===u}", FURL('jb', jb3)), '⑧ 그림 창 자리 표시를 누르면 다시 받음')
    pg.click('#mclose'); pg.wait_for_timeout(300)

    # ---- ⑩ 인쇄 준비(파일 방식): beforeprint → 아직 안 받은 그림을 모두 받음 · print 매체로 바뀔 때도
    pg.evaluate(f"location.hash='#/{SID}/{K3}/learn'"); wait(pg, "()=>document.querySelectorAll('#stage img[data-img]').length>0"); pg.wait_for_timeout(500)
    b4 = pg.evaluate("[document.querySelectorAll('#stage img[data-img]').length,[...document.querySelectorAll('#stage img[data-img]')].filter(i=>i.getAttribute('src')).length]")
    pg.evaluate("window.dispatchEvent(new Event('beforeprint'))"); n = pg.evaluate("__h.imgsReady(15000)")
    a4 = pg.evaluate("(()=>{const L=[...document.querySelectorAll('#stage img[data-img]')];return [L.length,L.filter(i=>i.getAttribute('src')).length,L.filter(i=>i.loading==='lazy').length,L.filter(i=>i.offsetParent!==null).length,L.filter(i=>i.offsetParent!==null&&i.complete&&i.naturalWidth>0).length]})()")
    ok(b4[1] < b4[0] and a4[1] == a4[0] and a4[2] == 0 and a4[3] == a4[4], f'⑩ 인쇄 전: 받은 그림 {b4[1]}/{b4[0]} → {a4[1]}/{a4[0]} · 늦게 받기 0 · 보이는 그림 {a4[4]}/{a4[3]} 다 옴(기다린 그림 {n})')
    pg.evaluate("window.dispatchEvent(new Event('afterprint'))")
    pg.evaluate(f"location.hash='#/{SID}/{K}/learn'"); wait(pg, "()=>document.querySelectorAll('#stage img[data-img]').length>0"); pg.wait_for_timeout(400); pg.emulate_media(media='print'); pg.wait_for_timeout(400)
    a5 = pg.evaluate("(()=>{const L=[...document.querySelectorAll('#stage img[data-img]')];return [L.length,L.filter(i=>i.getAttribute('src')).length]})()"); pg.emulate_media(media='screen')
    ok(a5[0] == a5[1], f'⑩ print 매체로 바뀔 때도 모두 받기 시작({a5[1]}/{a5[0]})')

    # ---- ⑨ 묶음 방식 과목(같은 허브): 강의 15개 뒤 힙 · 받은 강의 묶음 ≤ 2 · 다시 가면 다시 받음 · 그림 창이 열려 있으면 안 비움
    cdp = ctx.new_cdp_session(pg)
    def heap():
        for _ in range(3): cdp.send('HeapProfiler.collectGarbage'); pg.wait_for_timeout(150)
        return round(pg.evaluate('performance.memory.usedJSHeapSize') / 1e6)
    FILLED = "h=>{const L=[...document.querySelectorAll('#stage img[data-img]')];if(location.hash!==h||!L.length||!L.every(i=>i.getAttribute('src')||i._src))return false;__h.fillAll();return L.every(i=>/^data:image/.test(i.getAttribute('src')||''))&&L.some(i=>i.complete&&i.naturalWidth>0)}"
    CH = [s for s in ('PHARM', 'ANAT', 'CONS') if s in QS.sids('3q')]; L15 = pg.evaluate("S=>S.flatMap(s=>__h.PACKS[s].lect.filter(L=>/data-img=/.test(L.learn)).map(L=>[s,L.k]))", CH)[:15]
    ok(len(L15) == 15, f'⑨ 묶음 방식 과목({", ".join(CH[:2])}) 강의 15개'); reqs.clear(); hs = {}
    for i, (s, k) in enumerate(L15):
        pg.evaluate(f"location.hash='#/{s}/{k}/learn'"); wait(pg, FILLED, f'#/{s}/{k}/learn', n=200); pg.wait_for_timeout(1500)   # 묶음이 와서 그림 글자(dataURI)가 모두 화면에 걸림(멀리 있는 것은 loading=lazy라 아직 안 그림) + 비우기(1.2초) 기다림
        if i == 0:
            pg.evaluate("document.querySelector('#stage figure[data-fig] img').click()"); wait(pg, "()=>document.querySelector('#imgmodal').classList.contains('on')&&document.querySelector('#mimg').naturalWidth>0")
            ev = pg.evaluate("(()=>{const u=__h.IMGUSE.slice();__h.IMGUSE.length=0;const n=__h.imgEvict();u.forEach(x=>__h.IMGUSE.push(x));return [n,Object.keys(__h.LOADED).length]})()")
            ok(ev[0] == 0 and ev[1] >= 1, f'⑨ 그림 창이 열려 있으면 묶음을 안 비움({ev})'); pg.click('#mclose'); pg.wait_for_timeout(300)
        if i in (1, 14): hs[i + 1] = heap()
    st = pg.evaluate("[Object.keys(__h.IMGNET).filter(k=>__h.IMGNET[k]==='lec'&&__h.LOADED[k]),Object.keys(__h.IMGS).map(s=>s+':'+Object.keys(__h.IMGS[s].lec).length).join(' ')]")
    ok(len(st[0]) <= 2, f'⑨ 강의 15개 뒤 메모리에 있는 강의 묶음 {st[0]} (≤ 2 · 과목별 그림 수 {st[1]})')
    ok(hs[15] <= hs[2] + HEAP_ROOM, f'⑨ 힙(GC 뒤 usedJSHeapSize): 2강 뒤 {hs[2]}MB → 15강 뒤 {hs[15]}MB (기준 + 여유 {HEAP_ROOM}MB 안 — 고치기 전 147 → 266)')
    ok(len([r for r in reqs if '.img.' in r and not r.startswith(SID)]) >= 15 and not [r for r in reqs if r.startswith(SID + '.img.')], f'⑨ 묶음 방식 과목은 묶음으로 받음({len([r for r in reqs if ".img." in r])}번)')
    s, k = L15[0]; n0 = len([r for r in reqs if r.startswith(f'{s}.img.')])
    pg.evaluate(f"location.hash='#/{s}/{k}/learn'")
    back = wait(pg, FILLED, f'#/{s}/{k}/learn', n=200); n1 = len([r for r in reqs if r.startswith(f'{s}.img.')])
    ok(back and n1 > n0, f'⑨ 비운 강의({s} {k})에 다시 가면 다시 받아 그림이 나옴(묶음 요청 {n0} → {n1})')
    ok(not errs, f'콘솔 오류 0 {errs[:3]}'); ctx.close(); b.close()
done()
