"""UX17 그림빵(S3 4 — guide/handoff/S3_BRIEF.md)
- 강의 탭 '그림빵' = 근거 있는 강의만(그림 조각이 있는 JB 기출 L.gbj 또는 t=그림빵 예상 L.gbp) — 없는 강의는 탭 없음 · 탭은 맨 끝(앞 탭 단축키 그대로)
- 예상 그림빵: 쪽 그림 위 번호 가림막(m 상자 수) · 하나 누르면 그것만 열림 · '전체 보기/가리기' · '답 목록' 펼침 · 채점 = 그 예상문제 기록('P:<aid>' — 예상 탭 카드와 같은 기록)
- 기출 그림빵: JB 그림 조각 + 원래 문제 글 + 답 줄 가림(하나씩 · '답 모두 펼치기') · 채점 = JB 문항 id(기출 카드와 같은 기록 — 새 키 없음) · 'JB 문제'·'📖 정리본' 칩
- 과목 메뉴 '그림빵 모아 풀기'(#/<S>/_fig) — 그림빵이 없는 과목은 메뉴 없음 · 모아 풀기 = 그 과목 전부(강의·종류 필터)
- 옛 교수·26에서 빠진 그림 = '과거 JB 대비용' 칩(있을 때) · 표시(형광펜) 대상 아님(data-aid 없음)
- 일반 빈칸빵: 학습 탭 가리기(Q)·빈칸 도구(B)를 켜도 카드 그림(F:)이 보임
- pageerror 0 · 스크린샷 work/_tmp/s3/ux17_*.png(없으면 work/_tmp/)"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import json
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
OUT = _os.path.join(J.TMP, 's3') if _os.path.isdir(_os.path.join(J.TMP, 's3')) else J.TMP
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def go(pg, h, w=1800): pg.evaluate(f"location.hash={json.dumps(h, ensure_ascii=False)}"); pg.wait_for_timeout(w)
MK = lambda s: f"JSON.parse(localStorage.getItem('jblhub.v1.mk.{s}')||'{{}}')"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(U + '#/'); pg.wait_for_timeout(2500)
    for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']: pg.evaluate(f"localStorage.removeItem('jblhub.v1.mk.{s}')")
    I = pg.evaluate("""(()=>{const o={};for(const s of Object.keys(__h.PACKS)){const P=__h.PACKS[s];o[s]=P.lect.map(L=>({k:L.k,j:(L.gbj||[]).length,p:(L.gbp||[]).length,tabs:__h.docTabs(P,L.k).map(t=>t[0])}));}return o})()""")
    bad = [(s, L['k']) for s, LL in I.items() for L in LL if ('fig' in L['tabs']) != bool(L['j'] + L['p'])]
    last = [(s, L['k']) for s, LL in I.items() for L in LL if 'fig' in L['tabs'] and L['tabs'][-1] != 'fig']
    nfig = sum(1 for LL in I.values() for L in LL if 'fig' in L['tabs']); nall = sum(len(LL) for LL in I.values())
    ok(not bad and not last and 0 < nfig < nall, f"'그림빵' 탭 = 근거 있는 강의만 {nfig}/{nall} · 맨 끝 · 어긋남 {bad[:3]}{last[:3]}")
    SP = next(((s, L['k']) for s, LL in I.items() for L in LL if L['p']), None)
    SJ = next(((s, L['k']) for s, LL in I.items() for L in LL if L['j']), None)
    NO = next((s for s, LL in I.items() if not any(L['j'] + L['p'] for L in LL)), None)
    ok(bool(SP), f"예상 그림빵 강의 {SP} · 기출 그림빵 강의 {SJ} · 그림빵 없는 과목 {NO}")
    # ---- 예상 그림빵 ----
    if SP:
        s, k = SP; go(pg, f'#/{s}/{k}/fig', 2500)
        pg.evaluate("document.querySelector('#stage .gbx.gbp').scrollIntoView({block:'start'})"); pg.wait_for_timeout(2000)
        r = pg.evaluate(f"""(()=>{{const P=__h.PACKS.{s},c=document.querySelector('#stage .gbx.gbp'),x=P.preds.find(z=>'P:'+z.aid===c.dataset.id),im=c.querySelector('.gbfig img');
          return {{id:c.dataset.id,m:x.m.length,n:c.querySelectorAll('.gbm').length,open:c.querySelectorAll('.gbm.open').length,src:/^data:image/.test(im.src||''),aid:!!c.closest('[data-aid]'),ans:c.querySelector('.gbans').hidden}}}})()""")
        ok(r['n'] == r['m'] > 0 and r['open'] == 0 and r['src'] and not r['aid'] and r['ans'], f"예상 그림빵 = 쪽 그림 + 번호 가림막 {r['n']}/{r['m']} 닫힘 · 그림 로드 · 표시 대상 아님 · 답 접힘")
        pg.evaluate("document.querySelector('#stage .gbx.gbp .gbm').click()"); pg.wait_for_timeout(200)
        r1 = pg.evaluate("[...document.querySelector('#stage .gbx.gbp').querySelectorAll('.gbm')].map(m=>m.classList.contains('open')?1:0)")
        ok(r1[0] == 1 and sum(r1) == 1, f"가림막 하나 누르면 그것만 열림 {r1[:6]}")
        pg.evaluate("document.querySelector('#stage .gbx.gbp [data-gbshow]').click()"); pg.wait_for_timeout(200)
        r2 = pg.evaluate("(()=>{const c=document.querySelector('#stage .gbx.gbp');return [c.querySelectorAll('.gbm:not(.open)').length,c.querySelector('[data-gbshow]').textContent]})()")
        pg.evaluate("document.querySelector('#stage .gbx.gbp [data-gbshow]').click()"); pg.wait_for_timeout(200)
        r3 = pg.evaluate("document.querySelector('#stage .gbx.gbp').querySelectorAll('.gbm.open').length")
        ok(r2[0] == 0 and r2[1] == '전체 가리기' and r3 == 0, f"'전체 보기' → 모두 열림 · '전체 가리기' → 모두 닫힘 {r2} {r3}")
        pg.evaluate("document.querySelector('#stage .gbx.gbp [data-gbans]').click()"); pg.wait_for_timeout(200)
        ok(pg.evaluate("!document.querySelector('#stage .gbx.gbp .gbans').hidden && document.querySelector('#stage .gbx.gbp .gbans').textContent.trim().length>3"), "'답 목록' 펼침")
        pg.screenshot(path=_os.path.join(OUT, 'ux17_pred.png'))
        pg.evaluate("document.querySelector('#stage .gbx.gbp [data-mk=ok]').click()"); pg.wait_for_timeout(300)
        m = pg.evaluate(MK(s)); pid = r['id']
        ok((m.get('ok') or {}).get(pid) == 1 and pg.evaluate("document.querySelector('#stage .gbx.gbp').classList.contains('mk-ok')"), f"예상 그림빵 ✓ = 그 예상문제 기록 mk.ok['{pid[:30]}…']")
        go(pg, f'#/{s}/{k}/pred', 2000)
        ok(pg.evaluate(f"(()=>{{const c=document.querySelector('#stage .pc[data-id={json.dumps(pid, ensure_ascii=False)}]');return !!c&&c.classList.contains('mk-ok')}})()"), "예상 탭 같은 문제에도 ✓ (같은 기록)")
        tg = pg.evaluate(f"__h.PACKS.{s}.preds.filter(x=>x.m&&!x.x).filter(x=>/26에서 빠|JB 대비/.test((x.t||'')+(x.why||''))).length")
        if tg:
            go(pg, f'#/{s}/_fig', 2500)
            ok(pg.evaluate("document.querySelectorAll('#stage .gbx.gbp .chip.gbpast').length") >= tg, f"26에서 빠진 예상 그림 = '과거 JB 대비용' {tg}")
    # ---- 기출 그림빵 ----
    if SJ:
        s, k = SJ; go(pg, f'#/{s}/{k}/fig', 2500)
        r = pg.evaluate("""(()=>{const c=document.querySelector('#stage .gbx.gbj');const L=[...c.querySelectorAll('.gbl')];return {id:c.dataset.id,img:c.querySelectorAll('.gbfigs img.fig').length,ln:L.length,hid:L.filter(l=>!l.classList.contains('show')&&getComputedStyle(l).color==='rgba(0, 0, 0, 0)').length,q:c.querySelector('.gbq').textContent.trim().length,jb:!!c.querySelector('[data-go]'),aid:!!c.closest('[data-aid]')}})()""")
        ok(r['img'] > 0 and r['ln'] > 0 and r['hid'] == r['ln'] and r['q'] > 3 and r['jb'] and not r['aid'], f"기출 그림빵 = JB 그림 {r['img']} + 문제 글 + 답 줄 {r['ln']}줄 가림 · 'JB 문제' 칩 {r}")
        pg.evaluate("document.querySelector('#stage .gbx.gbj .gbl').click()"); pg.wait_for_timeout(150)
        r1 = pg.evaluate("[...document.querySelector('#stage .gbx.gbj').querySelectorAll('.gbl')].map(l=>l.classList.contains('show')?1:0)")
        ok(r1[0] == 1 and sum(r1) == 1, f"답 줄 하나씩 {r1[:5]}")
        pg.evaluate("document.querySelector('#stage .gbx.gbj [data-gball]').click()"); pg.wait_for_timeout(150)
        ok(pg.evaluate("document.querySelector('#stage .gbx.gbj').querySelectorAll('.gbl:not(.show)').length") == 0, "'답 모두 펼치기'")
        pg.screenshot(path=_os.path.join(OUT, 'ux17_jb.png'))
        pg.evaluate("document.querySelector('#stage .gbx.gbj [data-mk=ng]').click()"); pg.wait_for_timeout(300)
        m = pg.evaluate(MK(s))
        ok((m.get('ng') or {}).get(r['id']) == 1, f"기출 그림빵 ✗ = JB 문항 기록 mk.ng['{r['id']}'] (새 키 없음 · 키 {[x for x in (m.get('ng') or {})]})")
        pg.evaluate("document.querySelector('#stage .gbx.gbj [data-go]').click()"); pg.wait_for_timeout(2000)
        r2 = pg.evaluate(f"(()=>{{const c=document.getElementById('c-{r['id']}');return {{h:location.hash,ng:!!c&&c.classList.contains('mk-ng'),pill:document.getElementById('retpill').classList.contains('on')}}}})()")
        ok(r2['ng'] and r2['pill'], f"'JB 문제' → 그 기출 카드(같은 ✗) · ↩ 알약 {r2}")
        go(pg, f'#/{s}/{k}/fig', 2000)
        lc = pg.evaluate("(()=>{const b=document.querySelector('#stage .gbx [data-golec]');if(!b)return null;const v=b.dataset.golec;b.click();return v})()"); pg.wait_for_timeout(1800)
        if lc: ok(pg.evaluate("location.hash").endswith('/learn'), f"'📖 정리본' → 학습 카드 {lc}")
    # ---- 모아 풀기 · 메뉴 ----
    s = (SP or SJ)[0]; go(pg, f'#/{s}/_home', 2000)
    has = pg.evaluate("!!document.querySelector('[data-d=\"_fig\"]')")
    ok(has, f"{s} 과목 메뉴 '그림빵 모아 풀기'")
    if NO:
        go(pg, f'#/{NO}/_home', 2000); ok(not pg.evaluate("!!document.querySelector('[data-d=\"_fig\"]')"), f"그림빵 없는 과목({NO}) = 메뉴 없음")
    go(pg, f'#/{s}/_fig', 2500)
    tot = sum(L['j'] + L['p'] for L in I[s])
    r = pg.evaluate("[document.querySelectorAll('#stage .gbx').length,document.querySelectorAll('#stage .gbx.gbj').length,document.querySelectorAll('#stage .gbx.gbp').length]")
    ok(r[0] == tot, f"모아 풀기 = 과목 그림빵 전부 {r[0]}/{tot} (기출 {r[1]} · 예상 {r[2]})")
    pg.evaluate("document.querySelector('#gbpills [data-gbkind=p]').click()"); pg.wait_for_timeout(200)
    v = pg.evaluate("[...document.querySelectorAll('#stage .gbx')].filter(c=>getComputedStyle(c).display!=='none').map(c=>c.dataset.gk)")
    ok(len(v) == r[2] and all(x == 'p' for x in v), f"종류 '예상' 필터 {len(v)}")
    pg.evaluate("document.querySelector('#gbpills [data-gbkind=\"\"]').click()"); pg.wait_for_timeout(100)
    k2 = next(L['k'] for L in I[s] if L['j'] + L['p'])
    pg.select_option('#gbpills [data-gbf=k]', k2); pg.wait_for_timeout(200)
    v = pg.evaluate("[...document.querySelectorAll('#stage .gbx')].filter(c=>getComputedStyle(c).display!=='none').map(c=>c.dataset.k)")
    want = next(L['j'] + L['p'] for L in I[s] if L['k'] == k2)
    ok(len(v) == want and all(x == k2 for x in v), f"강의 필터 {k2} {len(v)}/{want}")
    pg.screenshot(path=_os.path.join(OUT, 'ux17_all.png'))
    # ---- 일반 빈칸빵에서 카드 그림 ----
    fl = pg.evaluate("""(()=>{for(const s of Object.keys(__h.PACKS)){const L=__h.PACKS[s].lect.find(L=>/<figure data-fig=/.test(L.learn));if(L)return [s,L.k];}return null})()""")
    if fl:
        go(pg, f'#/{fl[0]}/{fl[1]}/learn', 2500)
        pg.evaluate("document.querySelector('#stage .tc .figs figure').scrollIntoView({block:'center'})"); pg.wait_for_timeout(1500)
        pg.keyboard.press('q'); pg.wait_for_timeout(500)
        q = pg.evaluate("(()=>{const f=document.querySelector('#stage .tc .figs figure');const r=f.getBoundingClientRect();return {qz:__h.QZ.on,vis:getComputedStyle(f.parentElement).display!=='none'&&r.height>40}})()")
        pg.keyboard.press('q'); pg.wait_for_timeout(300); pg.keyboard.press('b'); pg.wait_for_timeout(400)
        k = pg.evaluate("(()=>{const f=document.querySelector('#stage .tc .figs figure');return {mode:__h.Kit.mode(),vis:f.getBoundingClientRect().height>40&&getComputedStyle(f.parentElement).display!=='none'}})()")
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        ok(q['qz'] and q['vis'] and k['vis'], f"일반 빈칸빵(가리기 Q {q} · 빈칸 도구 B {k})에서 카드 그림 보임")
    ok(not errs, f"pageerror 0 {errs[:3]}")
    for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']: pg.evaluate(f"localStorage.removeItem('jblhub.v1.mk.{s}')")
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
