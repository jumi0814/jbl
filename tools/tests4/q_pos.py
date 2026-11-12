"""11-11 W0 자리 지킴이 — '렉' 묶음(표 맞춤 미루기·content-visibility 등)의 안전판: 보던 카드가 돌아왔을 때 같은 화면 높이에 있는지.
시험용 사이트(fixture = 4Q 정체성 + 3Q 내용 · JBL_POS_SITE=3q면 3q/ 허브)에서 가장 긴 문서 7개
  강의 탭 학습·정리표·비교표·기출·예상 + 과목 문서 JB 문제·비교표 (과목·강의는 __h.PACKS에서 가장 큰 것 — id를 박지 않음)
의 깊이 3곳(위·가운데·아래)마다
  ① 탭 전환 뒤 돌아옴(강의 = 다른 탭 단추 · 과목 문서 = 메뉴의 과목 홈) ② 브라우저 뒤로 ②' 앞으로 ③ 새로고침 ④ 칩으로 건너갔다 ↩
→ 같은 카드(data-aid)의 화면 높이가 떠나기 전과 ±2px인지 — 돌아와 그려진 뒤 100ms와 1.5초 두 번 잼(늦게 밀리는 것도 잡음).
지금 코드에서 통과해야 함. 지금 실패하는 경우(이미 있는 버그)는 아래 KNOWN에 적어 'KNOWN' 줄로 보이고 RESULT에는 안 셈 — KNOWN인데 통과하면 알려 줌(목록에서 빼기).
  .venv/bin/python tools/tests4/q_pos.py                      # 전부(약 6분)
  JBL_POS_DOC=learn,_tbl  JBL_POS_SC=tab,back,fwd,reload,chip  JBL_POS_SITE=3q   # 좁혀서
  .venv/bin/python tools/tests4/q_pos.py --perf               # 판정 없이 '여는 시간·LayoutCount' 표만(렉 묶음 전·후 견주기 — CDP Performance.getMetrics)"""
import json, time
from qsite import *
from playwright.sync_api import sync_playwright
PERF = '--perf' in sys.argv; TOL = 2
ODOC = [x for x in os.environ.get('JBL_POS_DOC', '').split(',') if x]; OSC = [x for x in os.environ.get('JBL_POS_SC', '').split(',') if x]
if os.environ.get('JBL_POS_SITE') == '3q':
    rel = build(); U = url(serve(), rel['3q']); SNAME = '3q/'
else:
    fx = build_fixture(); U = url(serve(fx['dir']), ''); SNAME = 'fixture'
DOCS = ['learn', 'sum', 'tbl', 'jb', 'pred', '_jb', '_tbl']; NAME = {'learn': '학습', 'sum': '정리표', 'tbl': '비교표', 'jb': '기출', 'pred': '예상', '_jb': '과목 JB', '_tbl': '과목 비교표'}
DEPTH = [('위', 0.0), ('가운데', 0.5), ('아래', 1.0)]
SCN = {'tab': '① 탭 전환', 'back': '② 뒤로', 'fwd': "②' 앞으로", 'reload': '③ 새로고침', 'chip': '④ 칩 → ↩'}
# 이미 있는 버그(지금 코드에서 실패) — (문서, 경우, 깊이) 또는 (문서, 경우, '*') → 재현·이유(DONE_W0.md 3번)
KNOWN = {}
CHIP = '.jbchip[data-go],[data-golec],[data-go]'
JS = r"""window.__qp={
 cards(){const seen=new Set();return [...document.querySelectorAll('#stage [data-aid]')].filter(b=>{if(b.classList.contains('res')||b.offsetParent===null||seen.has(b.dataset.aid))return false;seen.add(b.dataset.aid);return b.getBoundingClientRect().height>0;});},
 find(aid){return [...document.querySelectorAll('#stage [data-aid]')].find(b=>!b.classList.contains('res')&&b.dataset.aid===aid)||null;},
 /* 깊이 f(0~1)의 카드를 기준선 30px 아래에 둠 · sel을 주면 그 칩이 있는 카드 가운데서 골라 칩이 보이게 둠(칩에 data-qp) */
 place(f,sel){document.querySelectorAll('[data-qp]').forEach(e=>e.removeAttribute('data-qp'));let L=this.cards(),chip=null;
  if(sel){L=L.filter(b=>[...b.querySelectorAll(sel)].some(e=>e.offsetParent!==null));if(!L.length)return null;}
  const b=L[Math.min(L.length-1,Math.round((L.length-1)*f))];if(!b)return null;const line=__h.topOff();let y=b.getBoundingClientRect().top+scrollY-line-30;
  if(sel){chip=[...b.querySelectorAll(sel)].find(e=>e.offsetParent!==null);chip.dataset.qp='1';const cy=chip.getBoundingClientRect().top+scrollY;if(cy-y>innerHeight-160||cy-y<line+8)y=cy-line-140;}
  window.scrollTo(0,Math.max(0,Math.round(y)));return {aid:b.dataset.aid,n:L.length,chip:chip?(chip.className+' '+Object.keys(chip.dataset).filter(k=>k!=='qp').join(',')):''};},
 where(aid){const b=this.find(aid);return {h:location.hash,y:Math.round(scrollY),top:b&&b.offsetParent!==null?Math.round(b.getBoundingClientRect().top*10)/10:null,H:document.documentElement.scrollHeight};}
};"""
AT = "([s,d,t])=>{const c=window.__h&&__h.CUR;return !!(c&&c.s===s&&c.d===d&&c.t===t&&!document.querySelector('#subj').hidden&&document.querySelector('#stage').firstElementChild);}"
PILL = "()=>{const p=document.getElementById('retpill');return !!(p&&p.classList.contains('on')&&getComputedStyle(p).display!=='none');}"
RAF2 = "()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r(1))))"
known_hit = set(); skips = []; selfok = []; t00 = time.time()

def perf(p):
    """렉 묶음 전·후 견주기용 수치 — 판정 없음. 문서마다 새 탭에서(팩 다 받은 뒤 허브 홈 → 그 문서) 처음 열기·같은 문서 다시 열기"""
    br = p.chromium.launch(); ctx = br.new_context(viewport={'width': 1280, 'height': 900}); ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, body='{}'))
    pg = ctx.new_page(); pg.goto(U + '#/'); wait_hub(pg, 1); pg.wait_for_function("__h.plStat().pend===0", timeout=240000); info = pg.evaluate(PACKINFO); pg.close()
    rows = []
    for tab in (ODOC or ['_tbl', 'sum', 'learn', '_jb', 'pred']):
        bg = biggest(info, tab)
        if not bg: continue
        s, d, t, size = bg; pg = ctx.new_page(); pg.goto(U + '#/'); wait_hub(pg, 1); pg.wait_for_function("__h.plStat().pend===0", timeout=240000); pg.wait_for_timeout(1500)
        cdp = ctx.new_cdp_session(pg); cdp.send('Performance.enable')
        def met(): return {m['name']: m['value'] for m in cdp.send('Performance.getMetrics')['metrics']}
        def openit(h):
            m0 = met(); t0 = time.time()
            pg.evaluate('h=>{location.hash=h}', h); pg.wait_for_function(AT, arg=[s, d, t], timeout=120000); pg.evaluate(RAF2); ms = (time.time() - t0) * 1000
            pg.wait_for_timeout(1600); m1 = met()   # 그린 뒤 1.6초 — 뒤따르는 일(표 맞춤·자리 맞춤)까지 셈
            return [round(ms), round(m1['LayoutCount'] - m0['LayoutCount']), round(m1['RecalcStyleCount'] - m0['RecalcStyleCount']), round((m1['LayoutDuration'] - m0['LayoutDuration']) * 1000), round((m1['ScriptDuration'] - m0['ScriptDuration']) * 1000), round((m1['TaskDuration'] - m0['TaskDuration']) * 1000)]
        a = openit(f'#/{s}/{d}/{t}'); pg.evaluate("h=>{location.hash=h}", f'#/{s}/_home/_home'); pg.wait_for_function(AT, arg=[s, '_home', '_home']); pg.wait_for_timeout(600)
        b = openit(f'#/{s}/{d}/{t}'); heap = round(met()['JSHeapUsedSize'] / 1e6)
        rows.append((NAME[tab], f'{s}/{d}', size, a, b, heap)); pg.close()
    br.close()
    print(f'| 문서({SNAME} · 1280×900) | 크기(글자) | 처음 열기 ms | Layout 수 | Recalc 수 | Layout ms | Script ms | Task ms | 다시 열기 ms | Layout 수 | Task ms | JS 힙 MB |'); print('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for n, k, size, a, b, heap in rows: print(f'| {n} {k} | {size} | {a[0]} | {a[1]} | {a[2]} | {a[3]} | {a[4]} | {a[5]} | {b[0]} | {b[1]} | {b[5]} | {heap} |')
    print('RESULT PASS (수치만 — 판정 없음)'); sys.exit(0)

with sync_playwright() as p:
    if PERF: perf(p)
    br = p.chromium.launch(); ctx = br.new_context(viewport={'width': 1280, 'height': 900}); ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, body='{}'))
    ctx.add_init_script(JS); pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda x: errs.append(str(x)[:200])); pg.on('dialog', lambda d: d.dismiss())
    pg.goto(U + '#/'); wait_hub(pg, 1); pg.wait_for_function("__h.plStat().pend===0", timeout=240000)
    ok(SNAME != 'fixture' or pg.evaluate('__h.NS') == QS.QS[QS.current()]['ident']['ns'], f'{SNAME}: 지금 쿼터 저장 이름({pg.evaluate("__h.NS")})으로 내용 팩 {pg.evaluate("Object.keys(__h.PACKS).length")}개')
    info = pg.evaluate(PACKINFO)
    def at(s, d, t, timeout=90000): pg.wait_for_function(AT, arg=[s, d, t], timeout=timeout)
    def hgo(h): pg.evaluate('h=>{location.hash=h}', h)
    for tab in DOCS:
        if ODOC and tab not in ODOC: continue
        bg = biggest(info, tab)
        if not bg: print(f'  SKIP {NAME[tab]} — 이 사이트에 그 문서가 없음'); skips.append(NAME[tab]); continue
        s, d, t, size = bg; H = f'#/{s}/{d}/{t}'; lec = tab[0] != '_'; t0 = time.time(); nfail0 = len(fail)
        other = ([x for x in next(L for L in info[s]['lect'] if L['k'] == d)['tabs'] if x != t and x not in ('flash', 'fig')] or [None])[0] if lec else None
        hgo('#/'); pg.wait_for_timeout(300); hgo(H); at(s, d, t); pg.wait_for_timeout(1500)
        n = pg.evaluate('__qp.cards().length'); print(f'== {NAME[tab]} {H} (글자 {size} · 카드 {n} · 높이 {pg.evaluate("document.documentElement.scrollHeight")}px)')
        ok(n >= 3, f'{NAME[tab]}: 기준 카드(data-aid) {n}개')
        def place(f, sel=None):
            if pg.evaluate('location.hash') != H or not pg.evaluate(AT, [s, d, t]): hgo(H); at(s, d, t); pg.wait_for_timeout(600)
            r = pg.evaluate('([f,sel])=>__qp.place(f,sel)', [f, sel])
            if not r: return None
            pg.wait_for_timeout(1100)   # 스크롤 0.8초 뒤 자리 저장(posNow) + 느린 그림
            a = pg.evaluate('a=>__qp.where(a)', r['aid']); a['aid'] = r['aid']; a['chip'] = r['chip']; return a
        def judge(sc, dn, a):
            """돌아와 그려진 뒤 100ms·1.5초에 잼 → (통과?, 글)"""
            try: at(s, d, t, 60000)
            except Exception: return False, f'돌아오지 않음(지금 {pg.evaluate("location.hash")})'
            tm = time.time(); pg.wait_for_timeout(100); b1 = pg.evaluate('a=>__qp.where(a)', a['aid'])
            pg.wait_for_timeout(max(0, 1500 - (time.time() - tm) * 1000)); b2 = pg.evaluate('a=>__qp.where(a)', a['aid'])
            dd = [None if b['top'] is None or a['top'] is None else round(b['top'] - a['top'], 1) for b in (b1, b2)]
            good = b2['h'] == a['h'] and all(x is not None and abs(x) <= TOL for x in dd)
            return good, f'카드 {a["aid"]} 높이 {a["top"]} → 100ms {b1["top"]}({dd[0]:+} px) · 1.5초 {b2["top"]}({dd[1]:+} px) · scrollY {a["y"]} → {b2["y"]} · 문서 높이 {a["H"]} → {b2["H"]}' if None not in dd else f'카드 {a["aid"]}를 못 찾음/안 보임(주소 {b2["h"]} · scrollY {a["y"]} → {b2["y"]})'
        def report(sc, dn, good, msg):
            k = next((x for x in ((tab, sc, dn), (tab, sc, '*')) if x in KNOWN), None); name = f'{NAME[tab]} {SCN[sc]} · {dn}'
            if k and not good: known_hit.add(k); print(f'  KNOWN {name}: {msg} — 이미 있는 버그: {KNOWN[k]}')
            elif k: print(f'  OK   {name}: {msg} — KNOWN인데 통과(목록에서 빼도 됨)')
            else: ok(good, f'{name}: {msg}')
        if not selfok:   # 검사기 자체 검사(한 번) — 일부러 37px 밀어 두면 '어긋남'으로 잡는지
            a = place(0.5); pg.evaluate('window.scrollBy(0,37)'); good, msg = judge('tab', '가운데', a)
            ok(not good, f'검사기 자체 검사 — 일부러 37px 민 것을 어긋남으로 잡음({msg[:90]})'); selfok.append(1)
        for dn, f in DEPTH:
            a = None
            for sc in ('tab', 'back', 'fwd', 'reload', 'chip'):
                if OSC and sc not in OSC: continue
                try:
                    if sc == 'chip':
                        a = place(f, CHIP)
                        if not a: print(f'  SKIP {NAME[tab]} {SCN[sc]} · {dn} — 이 문서에 칩 없음'); skips.append(f'{NAME[tab]} 칩'); continue
                        pg.evaluate("document.querySelector('[data-qp]').click()"); pg.wait_for_timeout(450)
                        if pg.evaluate("!!document.querySelector('#jbpeek.on [data-jpgo]')"): pg.evaluate("document.querySelector('#jbpeek.on [data-jpgo]').click()")   # 학습·정리표 기출 칩 = 그 자리 미리보기 → JB에서 풀기
                        try: pg.wait_for_function("h=>location.hash!==h", arg=H, timeout=5000); pg.wait_for_timeout(900)
                        except Exception: pass
                        if pg.evaluate('location.hash') == H or not pg.evaluate(PILL):
                            print(f'  SKIP {NAME[tab]} {SCN[sc]} · {dn} — 칩({a["chip"]})이 다른 화면으로 안 감/↩ 없음(지금 {pg.evaluate("location.hash")})'); skips.append(f'{NAME[tab]} 칩 {dn}'); a = None; continue
                        pg.evaluate("document.getElementById('retpill').click()")
                    else:
                        if a is None: a = place(f)
                        if not a: ok(False, f'{NAME[tab]} · {dn}: 기준 카드를 못 잡음'); break
                        if sc == 'tab':
                            if lec and other:
                                pg.evaluate("t=>document.querySelector('#dtabs button[data-t=\"'+t+'\"]').click()", other); at(s, d, other); pg.wait_for_timeout(500)
                                pg.evaluate("t=>document.querySelector('#dtabs button[data-t=\"'+t+'\"]').click()", t)
                            else:
                                pg.evaluate("document.querySelector('#nav .nvd[data-d=\"_home\"]').click()"); at(s, '_home', '_home'); pg.wait_for_timeout(500)
                                pg.evaluate("d=>document.querySelector('#nav .nvd[data-d=\"'+d+'\"]').click()", d) if not lec else hgo(H)
                        elif sc == 'back':
                            hgo(f'#/{s}/_home/_home'); at(s, '_home', '_home'); pg.wait_for_timeout(500); pg.go_back()
                        elif sc == 'fwd':
                            pg.go_back(); pg.wait_for_function("h=>location.hash!==h", arg=H, timeout=20000); pg.wait_for_timeout(600); pg.go_forward()
                        elif sc == 'reload':
                            pg.reload()
                    good, msg = judge(sc, dn, a)
                except Exception as e:
                    good, msg = False, f'시험 중 오류 {str(e)[:160]}'
                report(sc, dn, good, msg)
                if not good or sc == 'chip': a = None   # 어긋났으면 다음 경우는 다시 자리 잡음
        print(f'   {NAME[tab]}: {time.time() - t0:.0f}초 · 걸린 것 {len(fail) - nfail0}')
    ok(not errs, f'화면 오류 0 {errs[:2]}')
    br.close()
stale = [k for k in KNOWN if k not in known_hit and not ODOC and not OSC]
print(f'  {SNAME} · {time.time() - t00:.0f}초 · KNOWN(이미 있는 버그) {len(known_hit)}건 · SKIP {len(skips)}건{" · KNOWN인데 이번엔 안 걸림: " + str(stale) if stale else ""}')
done()
