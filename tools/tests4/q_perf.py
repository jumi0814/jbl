"""11-04 사용자 '용량커지거나 해서 렉 절대 안 생기게끔' — 성능 예산
① 크기: 허브 index ≤ 1.6MB · 과목 본문 팩 ≤ 6.0MB · 강의 그림 묶음 하나 ≤ 9.5MB (4Q는 넘으면 실패, 3Q는 보고만 — 이미 배포된 보관 쿼터)
② 시간(로컬): 홈이 그려질 때까지 · 과목 팩 받기 · 강의 학습·기출·예상 탭 열기 · 그동안 긴 작업(longtask) 합계 — tools/tests4/perf_base.json(기준)보다 2배+0.5초 넘게 느리면 실패
  기준을 새로 잡기: JBL_PERF_SAVE=1 .venv/bin/python tools/tests4/q_perf.py"""
import json, time
from qsite import *
from playwright.sync_api import sync_playwright
BUD = {'index': 1.6e6, 'pack': 6.0e6, 'img': 9.5e6}
BASE = os.path.join(HERE, 'perf_base.json'); base0 = json.load(open(BASE, encoding='utf-8')) if os.path.exists(BASE) else {}
rel = build(); base = serve(); got = {}
for q, r in rel.items():
    D = os.path.join(SITE, r) if r else SITE; strict = q != '3q'
    sz = os.path.getsize(os.path.join(D, 'index.html'))
    (ok if strict else (lambda c, m: print(('  OK  ' if c else '  INFO') + ' ' + m)))(sz <= BUD['index'], f'{q} 허브 index {sz / 1e6:.2f}MB ≤ {BUD["index"] / 1e6}')
    P = os.path.join(D, 'packs')
    for f in sorted(os.listdir(P)) if os.path.isdir(P) else []:
        n = os.path.getsize(os.path.realpath(os.path.join(P, f))); lim = BUD['img'] if '.img.' in f else BUD['pack'] if f.count('.') == 1 else None
        if lim and n > lim: (ok if strict else (lambda c, m: print('  INFO ' + m)))(False, f'{q} {f} {n / 1e6:.1f}MB > {lim / 1e6}MB')
LT = "(()=>{window.__lt=0;try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lt+=e.duration;}).observe({type:'longtask',buffered:true});}catch(e){}})()"
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(viewport={'width': 1280, 'height': 900}); ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, body='{}'))
    for q, r in rel.items():
        U = url(base, r); pg = ctx.new_page(); pg.add_init_script(LT)
        t = time.time(); pg.goto(U); pg.wait_for_selector('.hkick', timeout=60000); got[f'{q}.home'] = round(time.time() - t, 2)
        sub = [s for s in QS.sids(q) if s in ('PHARM', 'CONS')] or QS.sids(q)[:2]
        for s in sub:
            t = time.time(); pg.wait_for_function(f"window.__h&&__h.PACKS&&__h.PACKS['{s}']", timeout=120000); got[f'{q}.{s}.pack'] = round(time.time() - t, 2)
            L = pg.evaluate(f"(__h.PACKS['{s}'].lect||[])[0]&&__h.PACKS['{s}'].lect[0].k")
            if not pg.evaluate(f"(__h.PACKS['{s}'].order||[]).length"): continue   # 11-05 JB·정리본이 아직 없는 과목(자료 대기) — 탭 시간은 잴 것이 없음
            for tab, h in (('learn', f'#/{s}/{L}'), ('jb', f'#/{s}/_jb/_jb'), ('pred', f'#/{s}/_pred/_pred')):
                if not L and tab == 'learn': continue
                pg.evaluate('window.__lt=0'); t = time.time(); pg.goto(U + h)
                pg.wait_for_function("(document.querySelector('#stage')||{innerText:''}).innerText.length>300", timeout=60000)
                got[f'{q}.{s}.{tab}'] = round(time.time() - t, 2); got[f'{q}.{s}.{tab}.lt'] = round(pg.evaluate('window.__lt') / 1000, 2)
        pg.close()
    br.close()
print('  측정(초):', json.dumps(got, ensure_ascii=False))
if os.environ.get('JBL_PERF_SAVE'): json.dump(got, open(BASE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('  기준 저장', BASE)
for k, v in got.items():
    b = base0.get(k)
    if b is not None: ok(v <= 2 * b + 0.5, f'{k} {v}s (기준 {b}s)')
ok(True, f'측정 {len(got)}개 · 기준 {len(base0)}개')
done()
