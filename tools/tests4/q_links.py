"""11-10 W1 이동·↩·자리 — 3q/ 허브(내용이 있는 쿼터)에서. 과목·강의·카드는 __h.PACKS에서 찾음(id를 박지 않음)
A 칩 종류마다 건너감 → ↩ → 같은 주소·같은 자리(누른 것의 화면 높이 ±2px)
  JB 카드 📖 정리본(data-golec)·예상 n ▸(data-gopred) · 학습 카드 기출 칩 → 미리보기 → JB에서 풀기(data-jpgo) · 예상 카드 관련 기출(.jbchip)·정리본(data-golec)
  과목 홈(기준 카드가 없는 화면 — scrollY): 강의 카드 본문 · 카드 아래 '기출 n' · 2회 이상 목록 · 기출 대장 → 문제 · 폰 393: 강의 바로가기 칩·강의 카드·JB 📖
B 검색: '더 보기' → 결과 → 뒤로(펼침·자리 그대로) · 결과에서 ↩ = 그 검색 · 종류 칩 뒤에도 펼침 · 검색만 해서는 ↩ 스택이 안 지워짐
C 내 표시 → 그 자리 → ↩ · ★ 북마크 카드 '강의로 →' → ↩ · 넘버링 화면 Ctrl+K → ↩ = 그 넘버링
D 학습 탭 거르기(묶음 알약·'… 카드만')가 탭 왕복·건너갔다 ↩·새로고침 뒤 그대로
E 없는 '_' 주소 · N제 없는 과목의 _final · 숨은 탭 주소(알림) · 정리본 칩이 없는 카드 번호를 가리킴(알림)
F 그림 묶음 받기 실패: 한 번 실패 = 저절로 다시 받음 · 두 번 실패 = 알림 [다시]·그림 창 스피너 닫힘 → [다시]로 받음 · JB 원본 없는 쪽 = 가까운 쪽 + 알림
G 고르기 칸(select)에 키보드 초점일 때 한 글자 단축키 끔 · 넘버링 편집 칸에서 Ctrl+K 안 열림"""
import json, re
from qsite import *
from playwright.sync_api import sync_playwright
rel = build(); base = serve()
if '3q' not in rel: print('SKIP 3q 허브 없음'); done()
U = url(base, rel['3q']); NS = QS.QS['3q']['ident']['ns']
READY = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('.hkick')"
PILL = "(()=>{const p=document.getElementById('retpill');return [p.classList.contains('on')&&getComputedStyle(p).display!=='none',p.textContent]})()"
TOASTS = "(ns)=>{try{return JSON.parse(sessionStorage.getItem(ns+'toasts')||'[]').map(x=>x.t)}catch(e){return []}}"
MARK = "(sel)=>{document.querySelectorAll('[data-qlk]').forEach(e=>e.removeAttribute('data-qlk'));const top=(parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--toph'))||52)+(parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--tabh'))||0)+70;const L=[...document.querySelectorAll(sel)].filter(e=>e.offsetParent!==null&&!e.closest('[hidden]'));if(!L.length)return null;const e=L[Math.min(L.length-1,Math.floor(L.length*0.6))];window.scrollTo(0,Math.max(0,e.getBoundingClientRect().top+scrollY-top-120));e.dataset.qlk='1';return L.length;}"
WHERE = "(()=>{const e=document.querySelector('[data-qlk]');const c=e&&(e.closest('[data-aid],.lcw,li,tr')||e);return {h:location.hash,y:Math.round(scrollY),t:e&&e.offsetParent!==null?Math.round(e.getBoundingClientRect().top):null,k:c?(c.dataset.aid||c.id||c.textContent.slice(0,30)):null};})()"
def hop(pg, name, sel, click=None, wait=1300, need_pill=True, away=None):
    """sel 가운데 하나를 표시하고 화면 가운데쯤 둠 → 누름 → 건너감 확인 → ↩ → 같은 주소·같은 자리"""
    n = pg.evaluate(MARK, sel)
    if not n: print(f'  SKIP {name} — 누를 것 없음({sel})'); return False
    pg.wait_for_timeout(700); a = pg.evaluate(WHERE)
    if click: click()
    else: pg.evaluate("document.querySelector('[data-qlk]').click()")
    pg.wait_for_timeout(wait); b = pg.evaluate('location.hash'); pl = pg.evaluate(PILL)
    ok(b != a['h'] if away is None else away(b), f'{name}: 건너감 ({a["h"]} → {b})')
    ok(pl[0] or not need_pill, f'{name}: ↩ 알약 ({pl[1][:40]!r})')
    if not pl[0]: return False
    pg.evaluate("document.getElementById('retpill').click()"); pg.wait_for_timeout(wait + 500)
    c = pg.evaluate("(a)=>{const k=a.k;let e=null;if(k){e=[...document.querySelectorAll('[data-aid]')].find(x=>x.dataset.aid===k)||document.getElementById(k);}return {h:location.hash,y:Math.round(scrollY),ct:e&&e.offsetParent!==null?Math.round(e.getBoundingClientRect().top):null};}", a)
    pg.evaluate(MARK.replace('const e=L[Math.min(L.length-1,Math.floor(L.length*0.6))];window.scrollTo(0,Math.max(0,e.getBoundingClientRect().top+scrollY-top-120));', 'const e=L[Math.min(L.length-1,Math.floor(L.length*0.6))];'), sel)
    d = pg.evaluate(WHERE)
    dy = None if (a['t'] is None or d['t'] is None) else d['t'] - a['t']
    ok(c['h'] == a['h'], f'{name}: ↩ = 같은 주소 ({c["h"]})')
    ok((dy is not None and abs(dy) <= 2) or abs(c['y'] - a['y']) <= 2, f'{name}: ↩ = 같은 자리(±2px) — 누른 것 높이 {a["t"]} → {d["t"]} · scrollY {a["y"]} → {c["y"]}')
    return True
with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={'width': 1280, 'height': 900}); ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, body='{}'))
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda x: errs.append(str(x)[:200])); pg.on('dialog', lambda d: d.dismiss())
    pg.goto(U); pg.wait_for_function(READY, timeout=240000); pg.wait_for_timeout(800)
    def fresh(h, w=1100):
        pg.goto('about:blank'); pg.goto(U + h); pg.wait_for_function("window.__h&&(__h.VIEW==='doc'||__h.VIEW==='home'||__h.VIEW==='search'||__h.VIEW==='num')&&__h.plStat().pend===0", timeout=240000); pg.wait_for_timeout(w)
    def go(h, w=1000): pg.goto(U + h); pg.wait_for_timeout(w)
    # 과목·강의 고르기 — 기출·예상·비교표·카드가 모두 넉넉한 강의
    PK = pg.evaluate("""(()=>{const o=[];for(const s in __h.PACKS){const p=__h.PACKS[s];(p.lect||[]).forEach(L=>{o.push({s,k:L.k,jb:L.jb.length,pred:L.pred.length,tbl:L.tbl.length,cards:(L.cards||[]).length,grp:new Set(((L.learn||'').match(/data-grp="[^"]+"/g)||[])).size,fig:/data-img=/.test(L.learn||'')});});}return o;})()""")
    best = sorted([x for x in PK if x['jb'] >= 4 and x['pred'] >= 4 and x['cards'] >= 8 and x['grp'] >= 2], key=lambda x: -(x['jb'] + x['cards']))
    ok(bool(best), f'시험할 강의 찾음({len(PK)}개 가운데)')
    if not best: br.close(); done()
    S, K = best[0]['s'], best[0]['k']; print(f'== 과목 {S} · 강의 {K} {best[0]}')
    pg.evaluate('localStorage.clear();sessionStorage.clear()'); fresh('#/')
    # ---------- A 칩 → ↩
    fresh(f'#/{S}/_jb/_jb'); pg.wait_for_selector('#cards .qc')
    hop(pg, 'A1 JB 카드 📖 정리본', '#cards .qc .qhead .chip.lec[data-golec]')
    fresh(f'#/{S}/_jb/_jb'); hop(pg, 'A2 JB 카드 예상 n ▸', '#cards .qc [data-gopred]')
    fresh(f'#/{S}/{K}/learn'); pg.wait_for_selector('#stage .tc')
    def peek_go():
        pg.evaluate("document.querySelector('[data-qlk]').click()"); pg.wait_for_timeout(500)
        ok(pg.evaluate("!!document.querySelector('#jbpeek.on [data-jpgo]')"), 'A3 학습 카드 기출 칩 → 그 자리 미리보기')
        pg.evaluate("document.querySelector('#jbpeek.on [data-jpgo]').click()")
    hop(pg, 'A3 학습 → 미리보기 → JB에서 풀기', '#stage .tc .c-exam .jbchip[data-go]', click=peek_go)
    fresh(f'#/{S}/{K}/pred'); pg.wait_for_selector('#stage .pc')
    hop(pg, 'A4 예상 카드 관련 기출 칩', '#stage .pc .jbchip[data-go]')
    fresh(f'#/{S}/{K}/pred'); hop(pg, 'A5 예상 카드 📖 정리본', '#stage .pc [data-golec]')
    fresh(f'#/{S}/_home/_home'); pg.wait_for_selector('#stage .lgrid')
    hop(pg, 'A6 과목 홈 강의 카드 본문', '#stage .lgrid .lcard', away=lambda h: '/learn' in h)
    fresh(f'#/{S}/_home/_home'); hop(pg, "A7 과목 홈 카드 아래 '기출 n'", '#stage .lgrid .lcl [data-lcs][data-t="jb"]', away=lambda h: h.endswith('/jb'))
    fresh(f'#/{S}/_home/_home'); hop(pg, 'A8 과목 홈 2회 이상 목록', '#htop .toplist .q[data-go]')
    fresh(f'#/{S}/_led/_led'); hop(pg, 'A10 기출 대장 → 문제', '#stage [data-go]')
    # ---------- B 검색
    fresh(f'#/{S}/{K}/learn'); pg.wait_for_function('__h.sxProg().ready', timeout=240000)
    Q = None
    for q in ('치료', '환자', '경우', '사용', '있다'):
        pg.evaluate("(q)=>{const s=document.querySelector('#gsearch');s.focus();s.value=q;s.dispatchEvent(new Event('input',{bubbles:true}));}", q); pg.wait_for_timeout(900)
        if pg.evaluate("__h.VIEW==='search'&&document.querySelectorAll('#home [data-smore]').length>0"): Q = q; break
    ok(bool(Q), f"검색 결과가 20건 넘는 낱말 찾음({Q})")
    if Q:
        g = pg.evaluate("(()=>{const b=document.querySelector('#home [data-smore]'),k=b.dataset.smore,grp=b.closest('.sgrp');b.click();return [k,grp.querySelectorAll('.sres').length,grp.classList.contains('all')];})()")
        ok(g[1] > 20 and g[2], f'B 더 보기 → {g[0]} 결과 {g[1]}건 펼침')
        st = pg.evaluate("[(__h.SQ.smo||[]).slice(),(history.state||{}).smo||null]"); ok(st[0] == [g[0]] and st[1] == [g[0]], f'B 펼친 과목을 SQ·history에 기억 {st}')
        pg.evaluate("(()=>{const r=[...document.querySelectorAll('#home .sgrp.all .sres')][24];r.dataset.qlk='1';window.scrollTo(0,r.getBoundingClientRect().top+scrollY-300);})()"); pg.wait_for_timeout(500)
        a = pg.evaluate("(()=>{const r=document.querySelector('#home [data-qlk]');return {y:Math.round(scrollY),t:Math.round(r.getBoundingClientRect().top),aid:r.dataset.aid,d:r.dataset.d};})()")
        pg.evaluate("document.querySelector('#home [data-qlk]').click()"); pg.wait_for_timeout(1500)
        pl = pg.evaluate(PILL); ok(pg.evaluate("__h.VIEW")== 'doc' and pl[0] and '검색' in pl[1], f'B 결과 25번째를 열면 ↩ = 그 검색 ({pl[1][:40]!r})')
        pg.go_back(); pg.wait_for_timeout(1500)
        b = pg.evaluate("(a)=>{const G=[...document.querySelectorAll('#home .sgrp')].find(x=>x.classList.contains('all'));const r=[...document.querySelectorAll('#home .sres')].find(x=>x.dataset.aid===a.aid&&x.dataset.d===a.d);return {v:__h.VIEW,n:G?G.querySelectorAll('.sres').length:0,y:Math.round(scrollY),t:r?Math.round(r.getBoundingClientRect().top):null};}", a)
        ok(b['v'] == 'search' and b['n'] == g[1], f'B 뒤로 = 검색 · 펼침 그대로 ({b["n"]}건)')
        ok(abs(b['y'] - a['y']) <= 2 and b['t'] is not None and abs(b['t'] - a['t']) <= 2, f'B 뒤로 = 보던 결과 그 자리(±2px) scrollY {a["y"]} → {b["y"]} · 높이 {a["t"]} → {b["t"]}')
        # 결과 → ↩ 알약 → 그 검색(펼침·자리)
        pg.evaluate("(a)=>{const r=[...document.querySelectorAll('#home .sres')].find(x=>x.dataset.aid===a.aid&&x.dataset.d===a.d);r.click();}", a); pg.wait_for_timeout(1500)
        pg.evaluate("document.getElementById('retpill').click()"); pg.wait_for_timeout(1700)
        b = pg.evaluate("(a)=>{const G=[...document.querySelectorAll('#home .sgrp')].find(x=>x.classList.contains('all'));const r=[...document.querySelectorAll('#home .sres')].find(x=>x.dataset.aid===a.aid&&x.dataset.d===a.d);return {v:__h.VIEW,n:G?G.querySelectorAll('.sres').length:0,y:Math.round(scrollY),t:r?Math.round(r.getBoundingClientRect().top):null};}", a)
        ok(b['v'] == 'search' and b['n'] == g[1] and abs(b['y'] - a['y']) <= 2, f'B ↩ 알약 = 그 검색 · 펼침·자리 그대로 ({b})')
        pg.evaluate("document.querySelector('#home [data-sk=\"\"]').click()"); pg.wait_for_timeout(700)
        ok(pg.evaluate("(k)=>{const G=[...document.querySelectorAll('#home .sgrp.all')];return G.length===1&&!document.querySelector('#home [data-smore=\"'+k+'\"]');}", g[0]), 'B 다시 그려도(종류 칩·색인 채움) 펼침 그대로')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(600)
    # 검색만 해서는 ↩ 스택이 안 지워짐
    fresh(f'#/{S}/_jb/_jb'); pg.wait_for_selector('#cards .qc')
    pg.evaluate(MARK, '#cards .qc .qhead .chip.lec[data-golec]'); pg.wait_for_timeout(500); pg.evaluate("document.querySelector('[data-qlk]').click()"); pg.wait_for_timeout(1300)
    p0 = pg.evaluate(PILL); h0 = pg.evaluate('location.hash')
    pg.evaluate("(q)=>{const s=document.querySelector('#gsearch');s.focus();s.value=q;s.dispatchEvent(new Event('input',{bubbles:true}));}", Q or '치료'); pg.wait_for_timeout(900)
    ok(pg.evaluate('__h.VIEW') == 'search' and pg.evaluate('__h.RSTK.length') == 1, '검색 화면으로 가도 ↩ 스택 그대로')
    pg.evaluate("document.querySelector('#gsearch').focus()"); pg.keyboard.press('Escape'); pg.wait_for_timeout(1200)
    p1 = pg.evaluate(PILL); ok(pg.evaluate('location.hash') == h0 and p0[0] and p1[0] and p1[1] == p0[1], f'검색을 닫고 돌아오면 ↩ 알약이 살아 있음 ({p1[1][:36]!r})')
    # ---------- C 내 표시 · ★ 북마크 카드 · 넘버링 Ctrl+K
    fresh(f'#/{S}/{K}/learn'); pg.wait_for_selector('#stage .tc')
    seed = pg.evaluate("""(()=>{const A={},B={};[...document.querySelectorAll('#stage .tc[data-aid]')].forEach(c=>{const txt=c.textContent;for(const e of c.querySelectorAll('.tbody li,.tbody div.li')){for(const w of e.textContent.split(/\\s+/)){const x=w.replace(/[^가-힣A-Za-z0-9]/g,'');if(x.length>=3&&txt.split(x).length===2){A[c.dataset.aid]=[{t:'h',x,i:0,c:'g'}];return;}}}});[...document.querySelectorAll('#stage .tc[data-aid]')].forEach(c=>{B[c.dataset.aid]=Date.now();});return [A,B];})()""")
    K2 = next((x['k'] for x in PK if x['s'] == S and x['k'] != K and x['cards'] >= 4), None)
    if K2:
        fresh(f'#/{S}/{K2}/learn'); pg.wait_for_selector('#stage .tc')
        s2 = pg.evaluate("""(()=>{const A={},B={};[...document.querySelectorAll('#stage .tc[data-aid]')].forEach(c=>{B[c.dataset.aid]=Date.now();const txt=c.textContent;for(const e of c.querySelectorAll('.tbody li,.tbody div.li')){for(const w of e.textContent.split(/\\s+/)){const x=w.replace(/[^가-힣A-Za-z0-9]/g,'');if(x.length>=3&&txt.split(x).length===2){A[c.dataset.aid]=[{t:'h',x,i:0,c:'y'}];return;}}}});return [A,B];})()""")
        seed[0].update(s2[0]); seed[1].update(s2[1])
    pg.evaluate("([ns,S,A,B])=>{localStorage.setItem(ns+'ann.'+S,JSON.stringify(A));localStorage.setItem(ns+'cbm.'+S,JSON.stringify(B));}", [NS, S, seed[0], seed[1]])
    ok(len(seed[0]) >= 6, f'표시·★ 카드 심음(표시 {len(seed[0])} · ★ {len(seed[1])})')
    fresh(f'#/{S}/_marks/_marks'); pg.wait_for_timeout(600)
    hop(pg, 'C1 내 표시 → 그 자리', '#stage button.mk[data-mkgo]')
    fresh(f'#/{S}/_cbm/_cbm'); pg.wait_for_timeout(600)
    hop(pg, "C2 ★ 북마크 카드 '강의로 →'", '#stage [data-cbmgo]', away=lambda h: '/learn' in h)
    fresh(f'#/_num/{S}', 2500)
    if pg.evaluate("__h.VIEW") == 'num':
        pg.keyboard.press('Control+k'); pg.wait_for_timeout(400); pg.fill('#qjq', 'JB 문제'); pg.wait_for_timeout(400)
        pg.evaluate("(sh)=>{const b=[...document.querySelectorAll('#qjl .qjo:not([data-qs])')].find(x=>/JB/.test(x.querySelector('.t').textContent)&&x.querySelector('small').textContent===sh);b.click();}", pg.evaluate(f"__h.sjShort('{S}')")); pg.wait_for_timeout(1500)
        pl = pg.evaluate(PILL); ok(pg.evaluate('location.hash').startswith(f'#/{S}/_jb') and pl[0] and '넘버링' in pl[1], f'C3 넘버링 화면 Ctrl+K → JB · ↩ 알약 ({pl[1][:36]!r})')
        pg.evaluate("document.getElementById('retpill').click()"); pg.wait_for_timeout(2000)
        ok(pg.evaluate('__h.VIEW') == 'num' and pg.evaluate('location.hash').startswith('#/_num'), f"C3 ↩ = 그 넘버링 ({pg.evaluate('location.hash')})")
        # G 넘버링 편집 칸에서 Ctrl+K 안 열림
        ed = pg.evaluate("(()=>{const v=document.querySelector('#numv');if(!v)return false;let e=v.querySelector('[contenteditable]');if(!e){e=document.createElement('div');e.contentEditable='true';e.textContent='스토리';e.dataset.qlkEd='1';v.appendChild(e);}e.focus();return document.activeElement===e;})()")
        if ed:
            pg.keyboard.press('Control+k'); pg.wait_for_timeout(300)
            ok(pg.evaluate("document.querySelector('#qj').hidden"), 'G 넘버링 편집 칸에 커서가 있으면 Ctrl+K가 바로 가기를 열지 않음')
            pg.evaluate("(()=>{const e=document.querySelector('[data-qlk-ed]');if(e)e.remove();if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();})()")
            pg.keyboard.press('Control+k'); pg.wait_for_timeout(300); ok(not pg.evaluate("document.querySelector('#qj').hidden"), 'G 편집 칸 밖에서는 Ctrl+K가 열림'); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        else: print('  SKIP G 넘버링 화면(#numv) 없음')
    else: ok(False, '넘버링 화면이 열림')
    # ---------- D 학습 탭 거르기 유지
    fresh(f'#/{S}/{K}/learn'); pg.wait_for_selector('#grppills')
    FS = "(()=>({g:(document.querySelector('#grppills [data-grp].on')||{dataset:{}}).dataset.grp||'',f:[...document.querySelectorAll('#grppills [data-filt].on')].map(b=>b.dataset.filt).sort().join(','),n:[...document.querySelectorAll('#stage .tc')].filter(c=>c.offsetParent!==null).length,N:(document.querySelector('#lmN')||{}).textContent||''}))()"
    f0 = pg.evaluate(FS)
    pg.evaluate("(()=>{const G=[...document.querySelectorAll('#grppills [data-grp]')].filter(b=>b.dataset.grp);const g=G.find(b=>[...document.querySelectorAll('#stage .tc')].filter(c=>c.dataset.grp===b.dataset.grp&&+c.dataset.n>0).length>0)||G[0];g.click();const f=document.querySelector('#grppills [data-filt=\"jb\"]');if(f)f.click();})()"); pg.wait_for_timeout(500)
    f1 = pg.evaluate(FS); ok(f1['g'] != '' and f1['n'] < f0['n'], f'D 거르기 켬 {f0} → {f1}')
    pg.evaluate("document.querySelector('#dtabs button[data-t=\"sum\"]').click()"); pg.wait_for_timeout(700); pg.evaluate("document.querySelector('#dtabs button[data-t=\"learn\"]').click()"); pg.wait_for_timeout(900)
    f2 = pg.evaluate(FS); ok(f2 == f1, f'D 정리표 탭에 다녀와도 그대로 {f2}')
    if pg.evaluate(MARK, '#stage .tc .c-exam .jbchip[data-go]'):
        pg.wait_for_timeout(400); pg.evaluate("document.querySelector('[data-qlk]').click()"); pg.wait_for_timeout(500)
        if pg.evaluate("!!document.querySelector('#jbpeek.on [data-jpgo]')"):
            pg.evaluate("document.querySelector('#jbpeek.on [data-jpgo]').click()"); pg.wait_for_timeout(1300); pg.evaluate("document.getElementById('retpill').click()"); pg.wait_for_timeout(1600)
            f3 = pg.evaluate(FS); ok(f3 == f1, f'D 기출로 건너갔다 ↩ 뒤에도 그대로 {f3}')
    pg.reload(); pg.wait_for_function("window.__h&&__h.VIEW==='doc'&&document.querySelector('#grppills')", timeout=240000); pg.wait_for_timeout(1200)
    f4 = pg.evaluate(FS); ok(f4 == f1, f'D 새로고침 뒤에도 그대로 {f4}')
    pg.evaluate("sessionStorage.clear()")
    # ---------- E 주소
    T = lambda: pg.evaluate(TOASTS, NS)
    fresh(f'#/{S}/_xyz/_xyz'); ok(pg.evaluate('location.hash') == f'#/{S}/_home/_home' and any('그 화면을 찾지 못해' in x for x in T()[:3]), f"E 모르는 '_' 주소 → 과목 홈 + 알림 ({pg.evaluate('location.hash')})")
    NF = pg.evaluate("Object.keys(__h.PACKS).find(s=>!(__h.PACKS[s].preds||[]).some(x=>x.fn&&!x.x))")
    if NF:
        fresh(f'#/{NF}/_final/_final'); ok(pg.evaluate('location.hash') == f'#/{NF}/_home/_home' and any('자료가 아직 없어' in x for x in T()[:3]), f'E N제 없는 과목({NF})의 _final → 과목 홈 + 알림')
    else: print('  SKIP E N제 없는 과목 없음')
    NT = pg.evaluate("(()=>{for(const s in __h.PACKS){const p=__h.PACKS[s];for(const L of p.lect){const have=__h.docTabs(p,L.k).map(x=>x[0]);const t=['tbl','jb','pred','fig'].find(x=>have.indexOf(x)<0);if(t)return [s,L.k,t];}}return null;})()")
    if NT:
        fresh(f"#/{NT[0]}/{NT[1]}/{NT[2]}"); ok(pg.evaluate('location.hash') == f"#/{NT[0]}/{NT[1]}/learn" and any('탭이 없어' in x for x in T()[:3]), f"E 숨은 탭 주소(#/{NT[0]}/{NT[1]}/{NT[2]}) → 학습 탭 + 알림 ({T()[:1]})")
    else: print('  SKIP E 탭이 빠진 강의 없음')
    fresh(f'#/{S}/_home/_home'); pg.evaluate("(()=>{const b=document.querySelector('#stage [data-golec]')||(()=>{const x=document.createElement('button');x.dataset.golec='';document.querySelector('#stage').appendChild(x);return x;})();b.dataset.golec='%s:999';b.click();})()" % K); pg.wait_for_timeout(1200)
    ok(pg.evaluate('location.hash') == f'#/{S}/{K}/learn' and pg.evaluate('scrollY') <= 2 and any('그 카드를 찾지 못해' in x for x in T()[:3]), f'E 정리본 칩의 카드 번호가 없으면 강의 처음 + 알림 ({T()[:1]})')
    ok(not errs, f'콘솔 오류 0 {errs[:3]}'); ctx.close()
    # ---------- F 그림 묶음
    FG = next((x for x in sorted(PK, key=lambda x: x['cards']) if x['fig']), None)
    if FG:
        s, k = FG['s'], FG['k']
        for nfail in (1, 2):
            ctx = br.new_context(viewport={'width': 1280, 'height': 900}); ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, body='{}'))
            cnt = {'n': 0, 'urls': [], 'fail': nfail}
            def mk(cnt):
                def img(route):
                    cnt['n'] += 1; cnt['urls'].append(route.request.url.rsplit('/', 1)[-1])
                    if cnt['n'] <= cnt['fail']: route.abort()
                    else: route.continue_()
                return img
            ctx.route(re.compile(r'/packs/[^/]*\.img\.[^/]*\.js'), mk(cnt))
            pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda x: errs.append(str(x)[:200])); pg.on('dialog', lambda d: d.dismiss())
            pg.goto(U + f'#/{s}/{k}/learn'); pg.wait_for_function("window.__h&&__h.VIEW==='doc'&&document.querySelector('#stage .tc')", timeout=240000); pg.wait_for_timeout(300)
            IM = "(()=>{const im=[...document.querySelectorAll('#stage img[data-img]')];return [im.length,im.filter(i=>i.getAttribute('src')).length];})()"
            if nfail == 1:
                pg.evaluate('__h.fillAll&&__h.fillAll()'); pg.wait_for_timeout(6000)
                im = pg.evaluate(IM); t = pg.evaluate(TOASTS, NS)
                ok(cnt['n'] >= 2 and 'r=' in cnt['urls'][1] and im[1] > 0 and not any('받지 못했어요' in x for x in t), f'F 한 번 실패 → 1.5초 뒤 저절로 다시 받음(요청 {cnt["n"]}번 · 그림 {im[1]}/{im[0]} · 알림 없음)')
            else:
                opened = pg.evaluate("(()=>{const f=document.querySelector('#stage figure[data-fig] img, #stage img[data-img]');if(!f)return false;f.click();return true;})()"); pg.wait_for_timeout(900)
                spin = pg.evaluate("document.querySelector('#imgmodal').classList.contains('on')&&!document.querySelector('#mspin').hidden")
                pg.wait_for_timeout(4500)
                r = pg.evaluate("(()=>{const t=document.querySelector('#toast');return {modal:document.querySelector('#imgmodal').classList.contains('on'),toast:t&&t.style.display!=='none'?t.innerText:'',btn:!!(t&&t.querySelector('.tact')),wait:Object.keys(__h.imgWait).filter(k=>(__h.imgWait[k]||[]).length).length,scr:document.querySelectorAll('script[data-imgk]').length};})()")
                ok(cnt['n'] == 2 and '받지 못했어요' in r['toast'] and r['btn'], f'F 두 번 실패 → 알림 [다시] (요청 {cnt["n"]}번 · {r["toast"][:30]!r})')
                ok(not r['modal'] and r['wait'] == 0 and r['scr'] == 0, f'F 그림 창 스피너 닫힘(열렸었음 {opened and spin}) · 대기열·script 지움 {r}')
                pg.evaluate("document.querySelector('#toast .tact').click()"); pg.wait_for_timeout(5000)
                im = pg.evaluate("(()=>{window.__h.fillAll&&__h.fillAll();const im=[...document.querySelectorAll('#stage img[data-img]')];return [im.length,im.filter(i=>i.getAttribute('src')).length,Object.keys(__h.LOADED).length];})()")
                ok(cnt['n'] >= 3 and im[2] >= 1, f'F [다시] → 다시 받음(요청 {cnt["n"]}번 · 받은 묶음 {im[2]})')
            ok(not errs, f'F 콘솔 오류 0 {errs[:3]}'); ctx.close()
    else: print('  SKIP F 그림 있는 강의 없음')
    ctx = br.new_context(viewport={'width': 1280, 'height': 900}); ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, body='{}'))
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda x: errs.append(str(x)[:200])); pg.on('dialog', lambda d: d.dismiss())
    pg.goto(U + f'#/{S}/_led/_led'); pg.wait_for_function("window.__h&&__h.VIEW==='doc'&&__h.plStat().pend===0", timeout=240000); pg.wait_for_timeout(800)
    if pg.evaluate("!!document.querySelector('#stage [data-jb]')"):
        ed = pg.evaluate("(()=>{const b=document.querySelector('#stage [data-jb]');const ed=b.dataset.jb.split('-')[0];b.dataset.jb=ed+'-9999';b.click();return ed;})()"); pg.wait_for_timeout(3500)
        r = pg.evaluate("[document.querySelector('#imgmodal').classList.contains('on'),document.querySelector('#mtitle').textContent,document.querySelector('#mspin').hidden]"); t = pg.evaluate(TOASTS, NS)
        ok(r[0] and r[2] and '원본' in r[1] and not r[1].endswith(' 1쪽') and any('원본이 없어' in x for x in t[:3]), f'F JB 원본 없는 쪽(9999) → 가장 가까운 쪽 + 알림 ({r[1]!r} · {t[:1]})')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
    else: print('  SKIP F JB 원본 쪽 단추 없음')
    # ---------- G select 초점
    pg.goto(U + f'#/{S}/_jb/_jb'); pg.wait_for_selector('#cards .qc'); pg.wait_for_timeout(600)
    if pg.evaluate("!!document.querySelector('#fprof,#fyr,#fsort')"):
        pg.evaluate("document.querySelector('#fprof,#fyr,#fsort').focus()"); pg.keyboard.press('h'); pg.keyboard.press('b'); pg.wait_for_timeout(200)
        ok(not pg.evaluate("__h.Kit.mode()||''") and pg.evaluate("document.activeElement.tagName") == 'SELECT', 'G 키보드로 초점 준 고르기 칸에서 H·B = 형광펜·빈칸 안 켜짐(초점 그대로)')
        pg.evaluate("(()=>{dispatchEvent(new Event('pointerdown'));const s=document.querySelector('#fprof,#fyr,#fsort');s.blur();s.focus();})()"); pg.keyboard.press('h'); pg.wait_for_timeout(200)
        ok(pg.evaluate("__h.Kit.mode()||''") == 'h' and pg.evaluate("document.activeElement.tagName") != 'SELECT', 'G 눌러서 고른 뒤 남은 초점이면 초점을 풀고 단축키(H = 형광펜)')
        pg.keyboard.press('h'); pg.wait_for_timeout(150)
    ok(not errs, f'G 콘솔 오류 0 {errs[:3]}'); ctx.close()
    # ---------- 폰 393 — 과목 홈(강의 바로가기 칩은 860px 이하에서만 보임) · JB 카드 📖 정리본
    ctx = br.new_context(viewport={'width': 393, 'height': 852}, is_mobile=True, has_touch=True); ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, body='{}'))
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda x: errs.append(str(x)[:200])); pg.on('dialog', lambda d: d.dismiss())
    fresh(f'#/{S}/_home/_home'); pg.wait_for_selector('#stage .lgrid')
    hop(pg, 'A9 (폰 393) 과목 홈 강의 바로가기 칩', '#stage .ljump .ljc', away=lambda h: '/learn' in h)
    fresh(f'#/{S}/_home/_home'); hop(pg, 'A6 (폰 393) 과목 홈 강의 카드 본문', '#stage .lgrid .lcard', away=lambda h: '/learn' in h)
    fresh(f'#/{S}/_jb/_jb'); pg.wait_for_selector('#cards .qc'); hop(pg, 'A1 (폰 393) JB 카드 📖 정리본', '#cards .qc .qhead .chip.lec[data-golec]')
    ok(not errs, f'폰 393 콘솔 오류 0 {errs[:3]}'); ctx.close()
    br.close()
done()
