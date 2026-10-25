"""10-25c 사용자 'jb 답안에 -> 등의 기호가 이상하게 깨지는 오류' 회귀.
원인: 브라우저가 '-' 뒤에서 줄을 바꿔 '-'는 줄 끝, '>'는 다음 줄 첫머리로 떨어짐(폭마다 다름 · 폰에서 잦음) + PDF 줄 끝에서 끊긴 '-' | '>'가 '- >'로 이어 붙음.
 ① 팩 정적: 모든 팩 HTML 글(태그 밖)의 -> · --> · <- · <-> 가 span.nwa 안 · '- &gt;'(띄운 화살표) 0
 ② 화면(390 폰 · 1100): JB 카드 답을 펼쳐 .nwa가 줄바꿈 없이 한 줄(getClientRects 1개 · white-space nowrap) — ANAT T16 · OMS1 Q08 · PHARM RX36
 ③ 넘버링: JB 카드 '✎ 넘버링'으로 넣은 문제 답안 화면에도 .nwa · 저장된 글에는 span 없음(글 그대로) · pageerror 0"""
import os, sys, re, json, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
TAGS = re.compile(r'(<[^>]*>)'); ARW = re.compile(r'(?:&lt;)?-{1,2}&gt;|&lt;-{1,2}')
bad = {}; sp = {}
for f in sorted(glob.glob(os.path.join(J.DOCS, 'packs', '*.js'))):
    if '.img.' in f or f.endswith('.lx.js'): continue
    t = open(f, encoding='utf-8').read().replace('<\\/', '</').replace('\\"', '"'); n = 0; b = 0; s = 0
    parts = TAGS.split(t)
    for i in range(0, len(parts), 2):
        for m in ARW.finditer(parts[i]):
            n += 1
            if not (i > 0 and parts[i - 1] == '<span class="nwa">' and m.start() == 0): b += 1
        s += len(re.findall(r'-\s+&gt;', parts[i]))
    bad[os.path.basename(f)] = b; sp[os.path.basename(f)] = s
ok(not any(bad.values()), f'① 팩 HTML 글의 화살표가 모두 span.nwa 안 {bad}')
ok(not any(sp.values()), f"① 띄운 화살표 '- &gt;' 0 {sp}")
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (390, 1100):
        pg = b.new_page(viewport={'width': w, 'height': 900}, is_mobile=w < 600, has_touch=w < 600); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for sid, cid in (('ANAT', 'T16'), ('OMS1', 'Q08'), ('PHARM', 'RX36')):
            pg.goto(J.HUB_URL + f'#/{sid}/_jb/_jb'); pg.wait_for_function(WAIT + f"&&document.querySelector('#c-{cid}')", timeout=90000); pg.wait_for_timeout(700)
            r = pg.evaluate("""q=>{const c=document.querySelector('#c-'+q);c.scrollIntoView();c.querySelector('[data-tog]').click();const d=c.querySelector('[data-deep]');if(d)d.click();c.querySelectorAll('details').forEach(x=>x.open=true);
              const L=[...c.querySelectorAll('.nwa')].filter(e=>e.offsetParent);return {n:L.length,multi:L.filter(e=>e.getClientRects().length>1).length,ws:L.length?getComputedStyle(L[0]).whiteSpace:''}}""", cid)
            ok(r['n'] >= 1 and r['multi'] == 0 and r['ws'] == 'nowrap', f'② {w} {sid} {cid} 화살표 {r["n"]}개 모두 한 줄(줄 끝 - · 다음 줄 > 없음) {r}')
        pg.close()
    pg = b.new_page(viewport={'width': 1280, 'height': 900}); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(J.HUB_URL + '#/ANAT/_jb/_jb'); pg.wait_for_function(WAIT + "&&document.querySelector('#c-T16')", timeout=90000); pg.wait_for_timeout(700)
    pg.evaluate("document.querySelector('#c-T16').scrollIntoView()"); pg.wait_for_timeout(300)
    btn = pg.evaluate("(()=>{const b=document.querySelector('#c-T16 .nmgo,#c-T16 [data-nmgo],#c-T16 [data-nmadd]');if(!b)return false;b.click();return true})()"); pg.wait_for_timeout(3500)
    if btn:
        v = pg.evaluate("""(()=>{const a=[...document.querySelectorAll('#numv .nm-it')].find(x=>/ascending pharyngeal/.test(x.textContent));if(!a)return null;
          const raw=Object.keys(localStorage).filter(k=>k.indexOf('jblhub.v1.num.i.ANAT.')===0).map(k=>localStorage.getItem(k)).join('');return {nwa:a.querySelectorAll('.nwa').length,stored:/nwa/.test(raw)}})()""")
        ok(v and v['nwa'] >= 1 and not v['stored'], f'③ 넘버링 답안 화면에도 화살표 묶음 · 저장 글엔 span 없음 {v}')
    else: ok(False, '③ ANAT T16 카드에 ✎ 넘버링 단추 없음')
    b.close()
ok(not errs, f'pageerror 0 {errs[:2]}')
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
sys.exit(1 if fails else 0)
