"""UX16 예상문제 화면(S3 1·2 — guide/handoff/S3_BRIEF.md · PRED26_BRIEF 2-3)
- 카드 머리: 우선순위 칩('우선 상/중/하' — data-pr) · 유형(배지) · 관련 기출(b — 여럿이면 연도 칩) · '근거' 버튼(기본 접힘 → 누르면 why 한 줄 · 다시 누르면 접힘)
- 좁은 화면(820)에서 태그 줄 한 줄 · 필터 막대 한 줄(우선순위 칸이 있어도 줄이 늘지 않음)
- 필터: 우선순위 '상' → 상만 · '상+중' → 상·중 · 다시 누르면 전체 · 새로고침 뒤 복원 · 보관 접힘 안은 거르지 않음
- 보관(x=1): 강의 예상 탭 맨 아래 details#parch(접힘) '보관된 예상문제 n개' · 탭 '예상 n'·플래시카드·과목 모아보기(_pred)·과목 머리 개수에서 빠짐 · 보관 카드도 채점 기록이 보임
- oid 기록 이어짐: 옛 aid로 ✓·★를 저장해 두고(사이트 갱신 전 기록) 새 빌드에서 그 문항(고쳐 쓴 문제)에 ✓·★가 보이고, 플래시카드 키도 같은 'P:<옛 aid>'
- f 그림: 문제 아래 강의 쪽 그림(img[data-img] 지연 로드 → src) · 누르면 그림 창
- pageerror 0 · 스크린샷 work/_tmp/s3/ux16_*.png(없으면 work/_tmp/)"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import re, json
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
OUT = _os.path.join(J.TMP, 's3') if _os.path.isdir(_os.path.join(J.TMP, 's3')) else J.TMP
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def pred_blocks(sid):
    """pred.txt 머리줄 → [{k, oid, x, f, pr}] (팩 preds 순서와 같음)"""
    out = []
    for line in open(_os.path.join(J.TOOLS, sid.lower(), 'pred.txt'), encoding='utf-8'):
        if not line.startswith('@'): continue
        p = [x.strip() for x in (line[3:] if line.startswith('@P ') else line[1:]).split('|')]
        d = {'k': p[0]}
        for x in p[1:]: k, _, v = x.partition('='); d[k.strip()] = v.strip()
        out.append(d)
    return out
def pick():
    """oid·보관·그림·우선순위가 다 있는 과목(없으면 가장 많은 과목)"""
    best = None
    for s in ['CONS', 'ANAT', 'OMS1', 'IMPL', 'GERI', 'PHARM', 'ESTH']:
        if not _os.path.exists(_os.path.join(J.DOCS, 'packs', s + '.js')): continue
        B = pred_blocks(s); sc = (any(b.get('oid') for b in B), any(b.get('x') == '1' for b in B), any(b.get('f') for b in B), any(b.get('pr') for b in B))
        if all(sc): return s, B
        if best is None or sum(sc) > sum(best[2]): best = (s, B, sc)
    return best[0], best[1]
SID, BL = pick(); print('과목', SID)
MK = f"JSON.parse(localStorage.getItem('jblhub.v1.mk.{SID}')||'{{}}')"
def go(pg, h, wait=1800):
    pg.evaluate(f"location.hash='{h}'"); pg.wait_for_timeout(wait)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1280, 'height': 900}); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(U + '#/'); pg.wait_for_timeout(2500)
    P = pg.evaluate(f"(()=>{{const P=__h.PACKS.{SID};return {{preds:P.preds.map(x=>({{k:x.k,aid:x.aid,x:x.x||0,pr:x.pr||'',f:x.f||[],why:x.why||'',b:x.b||[],m:x.m||null}})),lect:P.lect.map(L=>({{k:L.k,pred:L.pred,parch:L.parch||[]}}))}}}})()")
    PR = P['preds']; ok(len(PR) == len(BL), f"팩 예상 {len(PR)} = pred.txt 블록 {len(BL)}")
    # ---- oid: 옛 aid로 기록을 먼저 저장(사이트 갱신 전 ✓·★) ----
    oids = [(i, b_['oid']) for i, b_ in enumerate(BL) if b_.get('oid')]
    ok(bool(oids) and all(PR[i]['aid'] == o for i, o in oids), f"oid 있는 {len(oids)}문항 = 팩 aid가 옛 aid 그대로 {[o for i, o in oids if PR[i]['aid'] != o][:3]}")
    oi, oid = oids[0] if oids else (None, None)
    if oid:
        pg.evaluate(f"localStorage.setItem('jblhub.v1.mk.{SID}',JSON.stringify({{ok:{{{json.dumps('P:' + oid, ensure_ascii=False)}:1}},ng:{{}},bm:{{{json.dumps('P:' + oid, ensure_ascii=False)}:1}}}}))")
        pg.reload(); pg.wait_for_timeout(2500)
        K = PR[oi]['k']; go(pg, f'#/{SID}/{K}/pred')
        r = pg.evaluate(f"(()=>{{const c=document.querySelector('#stage .pc[data-aid={json.dumps(oid, ensure_ascii=False)}]');return c?{{id:c.dataset.id,ok:c.classList.contains('mk-ok'),bm:c.classList.contains('mk-bm'),arch:!!c.closest('#parch')}}:null}})()")
        ok(bool(r) and r['id'] == 'P:' + oid and r['ok'] and r['bm'], f"oid 기록 이어짐 — 옛 aid ✓·★가 고쳐 쓴 문제 카드에 그대로 {r}")
        if r and not r['arch']:
            pg.evaluate("document.querySelector('#dtabs [data-t=flash]').click()"); pg.wait_for_timeout(1200)
            fk = pg.evaluate("__h.Flash.all.filter(c=>/^P:/.test(c.key)).map(c=>c.key)")
            ok(('P:' + oid) in fk, f"플래시카드 예상 키 = 'P:<옛 aid>' ({len(fk)}장)")
    # ---- 우선순위·근거·필터·보관 — 보관이 있는 강의(없으면 우선순위가 있는 첫 강의) ----
    LA = next((L for L in P['lect'] if L['parch'] and any(PR[i]['pr'] for i in L['pred'])), None) or next(L for L in P['lect'] if any(PR[i]['pr'] for i in L['pred']))
    K = LA['k']; go(pg, f'#/{SID}/{K}/pred')
    r = pg.evaluate("""(()=>{const A=[...document.querySelectorAll('#stage .pc:not(.px)')],X=[...document.querySelectorAll('#stage .pc.px')];const tab=(document.querySelector('#dtabs [data-t=pred]')||{}).textContent||'';
      const chip=A.filter(c=>c.dataset.pr).map(c=>{const e=c.querySelector('.qhead .chip.ppr');return e?e.textContent.trim()==='우선 '+c.dataset.pr:false});
      const d=document.querySelector('#parch');return {n:A.length,x:X.length,tab,chipOK:chip.filter(Boolean).length,chipN:chip.length,inArch:X.every(c=>c.closest('#parch')),open:d?d.open:null,sum:d?d.querySelector('summary').textContent.trim():''}})()""")
    ok(r['n'] == len(LA['pred']) and r['tab'].endswith(str(len(LA['pred']))), f"강의 {K} 활성 예상 {r['n']} = L.pred {len(LA['pred'])} · 탭 '{r['tab']}'")
    ok(r['chipN'] > 0 and r['chipOK'] == r['chipN'], f"우선순위 칩 '우선 상/중/하' {r['chipOK']}/{r['chipN']}")
    if LA['parch']:
        ok(r['x'] == len(LA['parch']) and r['inArch'] and r['open'] is False and r['sum'] == f"보관된 예상문제 {len(LA['parch'])}개", f"보관 {r['x']}개 = 맨 아래 접힘 '{r['sum']}'")
    # 근거
    r = pg.evaluate("""(()=>{const c=[...document.querySelectorAll('#stage .pc:not(.px)')].find(c=>c.querySelector('[data-pwhy]'));if(!c)return null;const b=c.querySelector('[data-pwhy]'),w=c.querySelector('.pwhyt');const h0=w.hidden||getComputedStyle(w).display==='none';b.click();const h1=getComputedStyle(w).display!=='none'&&w.offsetHeight>0,ae=b.getAttribute('aria-expanded'),t=w.textContent;b.click();const h2=w.hidden;return {h0,h1,ae,h2,t:t.slice(0,60)}})()""")
    ok(bool(r) and r['h0'] and r['h1'] and r['ae'] == 'true' and r['h2'], f"'근거' 기본 접힘 → 누르면 한 줄({r and r['t']}) → 다시 접힘")
    # 필터
    VIS = "[...document.querySelectorAll('#stage .pc:not(.px)')].filter(c=>getComputedStyle(c).display!=='none').map(c=>c.dataset.pr||'')"
    want = lambda s_: [PR[i]['pr'] for i in LA['pred'] if PR[i]['pr'] and PR[i]['pr'] in s_]
    pg.click('#ppills [data-ppr="상"]'); pg.wait_for_timeout(300); v1 = pg.evaluate(VIS)
    ok(v1 == want('상'), f"우선순위 '상' → 상만 {len(v1)}문항")
    pg.click('#ppills [data-ppr="상중"]'); pg.wait_for_timeout(300); v2 = pg.evaluate(VIS)
    ok(v2 == want('상중') and len(v2) >= len(v1), f"'상+중' → 상·중 {len(v2)}문항")
    if LA['parch']:
        xv = pg.evaluate("(()=>{document.querySelector('#parch').open=true;return [...document.querySelectorAll('#parch .pc')].filter(c=>getComputedStyle(c).display!=='none').length})()")
        ok(xv == len(LA['parch']), f"보관 접힘 안은 우선순위로 거르지 않음 {xv}/{len(LA['parch'])}")
        pg.evaluate("document.querySelector('#parch').open=false")
    pg.reload(); pg.wait_for_timeout(2500); v3 = pg.evaluate(VIS)
    ok(v3 == v2 and pg.evaluate("!!document.querySelector('#ppills [data-ppr=\"상중\"].on')"), f"새로고침 뒤 우선순위 필터 복원 {len(v3)}")
    pg.click('#ppills [data-ppr="상중"]'); pg.wait_for_timeout(300); v4 = pg.evaluate(VIS)
    ok(len(v4) == len(LA['pred']), f"다시 누르면 전체 {len(v4)}")
    # 보관 카드 채점 기록도 보임
    if LA['parch']:
        xa = PR[LA['parch'][0]]['aid']
        pg.evaluate(f"(()=>{{const m={MK};m.ng=m.ng||{{}};m.ng[{json.dumps('P:' + xa, ensure_ascii=False)}]=1;m.ok=m.ok||{{}};m.bm=m.bm||{{}};localStorage.setItem('jblhub.v1.mk.{SID}',JSON.stringify(m))}})()")
        pg.reload(); pg.wait_for_timeout(2500)
        r = pg.evaluate(f"(()=>{{const c=document.querySelector('#parch .pc[data-aid={json.dumps(xa, ensure_ascii=False)}]');return c?c.classList.contains('mk-ng'):null}})()")
        ok(r is True, "보관 카드에도 채점 기록(✗)이 그대로 보임")
        pg.evaluate("document.querySelector('#dtabs [data-t=flash]').click()"); pg.wait_for_timeout(1200)
        fk = pg.evaluate("__h.Flash.all.filter(c=>/^P:/.test(c.key)).map(c=>c.key)")
        arch = {'P:' + PR[i]['aid'] for i in LA['parch']}
        ok(not (set(fk) & arch) and len(fk) <= len(LA['pred']), f"플래시카드에 보관 문항 없음 (예상 {len(fk)}장 ≤ 활성 {len(LA['pred'])})")
    # 모아보기·과목 머리 개수
    act = sum(1 for x in PR if not x['x'])
    go(pg, f'#/{SID}/_pred', 2500)
    r = pg.evaluate("[document.querySelectorAll('#stage .pc').length,document.querySelectorAll('#stage .pc.px,#stage #parch').length]")
    ok(r[0] == act and r[1] == 0, f"과목 예상 모아보기 = 활성 {r[0]}/{act} · 보관 없음")
    go(pg, f'#/{SID}/_home', 2000)
    hn = pg.evaluate("(document.querySelector('#hero [data-hgo=_pred]')||{}).textContent||''")
    ok(hn == f'예상 {act}', f"과목 머리 '{hn}' = 활성 {act}")
    # ---- f 그림 ----
    fi = next((i for i, x in enumerate(PR) if x['f'] and not x['x'] and not x.get('m')), None)   # 10-16 그림빵(m)은 아래 따로 — 예상 탭에서도 번호 가림막
    if fi is not None:
        go(pg, f"#/{SID}/{PR[fi]['k']}/pred", 2500)
        sel = f"#stage .pc[data-aid={json.dumps(PR[fi]['aid'], ensure_ascii=False)}]"
        pg.evaluate(f"document.querySelector({json.dumps(sel, ensure_ascii=False)}).scrollIntoView({{block:'center'}})"); pg.wait_for_timeout(2500)
        r = pg.evaluate(f"(()=>{{const c=document.querySelector({json.dumps(sel, ensure_ascii=False)});const im=[...c.querySelectorAll('.figs figure img[data-img]')];return {{n:im.length,keys:im.map(i=>i.dataset.img),src:im.filter(i=>/^data:image/.test(i.src||'')).length,after:!!c.querySelector('.pq+.figs, .pq+.figchip+.figs')}}}})()")
        ok(r['n'] == len(PR[fi]['f']) and r['keys'] == PR[fi]['f'] and r['src'] == r['n'] and r['after'], f"f 그림 {r['keys']} 문제 아래 · 지연 로드 {r['src']}/{r['n']}")
        pg.evaluate(f"document.querySelector({json.dumps(sel + ' .figs figure', ensure_ascii=False)}).click()"); pg.wait_for_timeout(1500)
        r = pg.evaluate("[document.querySelector('#imgmodal').classList.contains('on'),(document.querySelector('#mtitle')||{}).textContent]")
        ok(r[0], f"그림 누르면 그림 창 '{r[1]}'")
        pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
        pg.screenshot(path=_os.path.join(OUT, 'ux16_fig.png'))
    # ---- 그림빵 예상 = 예상 탭 카드에서도 라벨을 번호 가림막으로(10-16 — 그림을 그대로 보이면 답이 보임) ----
    gi = next((i for i, x in enumerate(PR) if x.get('m') and x['f'] and not x['x']), None)
    if gi is not None:
        go(pg, f"#/{SID}/{PR[gi]['k']}/pred", 2500)
        sel = f"#stage .pc[data-aid={json.dumps(PR[gi]['aid'], ensure_ascii=False)}]"
        pg.evaluate(f"document.querySelector({json.dumps(sel, ensure_ascii=False)}).scrollIntoView({{block:'center'}})"); pg.wait_for_timeout(2500)
        r = pg.evaluate(f"(()=>{{const c=document.querySelector({json.dumps(sel, ensure_ascii=False)});const im=c.querySelector('.gbfig img[data-img]');return {{m:c.querySelectorAll('.gbfig .gbm').length,plain:c.querySelectorAll('.figs figure img[data-img=\"'+(im&&im.dataset.img)+'\"]').length,src:!!(im&&/^data:image/.test(im.src||''))}}}})()")
        ok(r['m'] == len(PR[gi]['m']) and r['plain'] == 0 and r['src'], f"그림빵 예상(예상 탭) = 가림막 {r['m']}/{len(PR[gi]['m'])} · 맨 그림 없음 · 지연 로드 {r['src']}")
        pg.evaluate(f"document.querySelector({json.dumps(sel + ' .gbm', ensure_ascii=False)}).click()"); pg.wait_for_timeout(300)
        ok(pg.evaluate(f"document.querySelectorAll({json.dumps(sel + ' .gbm.open', ensure_ascii=False)}).length") == 1, "가림막 누르면 하나만 열림")
    # ---- 좁은 화면 820 — 태그 줄·필터 막대 한 줄 ----
    pg.set_viewport_size({'width': 820, 'height': 900}); go(pg, f'#/{SID}/{K}/pred', 2000)
    r = pg.evaluate("""(()=>{const one=e=>{const k=[...e.children].filter(x=>getComputedStyle(x).display!=='none'&&x.offsetWidth);if(!k.length)return true;const t=k.map(x=>x.getBoundingClientRect().top);return Math.max(...t)-Math.min(...t)<8;};
      const A=[...document.querySelectorAll('#stage .pc:not(.px) .qhead')];const bad=A.filter(h=>!one(h)).map(h=>h.closest('.pc').dataset.aid.slice(-10));const P=document.querySelector('#ppills');return {n:A.length,bad,pp:one(P),ph:Math.round(P.getBoundingClientRect().height),over:document.documentElement.scrollWidth>innerWidth+1}})()""")
    ok(not r['bad'] and r['pp'] and not r['over'], f"820: 태그 줄 한 줄 {r['n'] - len(r['bad'])}/{r['n']} {r['bad'][:4]} · 필터 막대 한 줄 {r['pp']}({r['ph']}px) · 가로 넘침 없음")
    pg.screenshot(path=_os.path.join(OUT, 'ux16_820.png'))
    # ---- JB 카드 → 관련 예상문제 칩 '예상 n ▸'(10-16 — 사용자 '기출에는 반영 … 예상문제에는 반영이 안된') ----
    pg.set_viewport_size({'width': 1280, 'height': 900}); go(pg, f'#/{SID}/_jb', 3000)
    r = pg.evaluate("(()=>{const c=document.querySelector('#stage .qc .chip.pgo');if(!c)return null;const [k,a]=c.dataset.gopred.split('|');return {k,a,t:c.textContent,n:document.querySelectorAll('#stage .qc .chip.pgo').length}})()")
    ok(bool(r) and r['t'].startswith('예상 '), f"JB 카드에 '예상 n ▸' 칩 {r and r['n']}개")
    if r:
        pg.evaluate("document.querySelector('#stage .qc .chip.pgo').click()"); pg.wait_for_timeout(2500)
        h = pg.evaluate("location.hash"); v = pg.evaluate(f"(()=>{{const c=document.querySelector('#stage .pc[data-aid={json.dumps(r['a'], ensure_ascii=False)}]');if(!c)return null;const b=c.getBoundingClientRect();return {{top:Math.round(b.top),vis:b.bottom>0&&b.top<innerHeight}}}})()")
        ok(h == f"#/{SID}/{r['k']}/pred" and v and v['vis'] and pg.evaluate("!!document.querySelector('#retpill')"), f"누르면 그 강의 예상 탭의 그 문제로 {h} {v} · ↩ 알약")
    ok(not errs, f"pageerror 0 {errs[:3]}")
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
