"""11-10 W1 빈 과목(강의자료 대기 — 강의가 WAIT뿐·문항 0 · build4 pack.stub) 화면 — 4Q 뿌리 허브(빈 과목 10개)에서 컴퓨터 1280·폰 393
① 허브 홈: 과목 줄 '자료 대기'(0 / 0 없음) · 준비 안내 · '시작하기 →'가 대기 강의로 안 감 · 오늘 할 일 글
② 과목 홈: '자료 대기' 한 줄 · '기출을 다 맞혔어요'·'- -'·빈 h1·끝 ' · '·'2회 이상 출제 0문항' 없음 · 가로 넘침 없음
③ Ctrl+K: 빈 과목 항목 = 과목 홈 + 넘버링 둘뿐(JB·한눈표·비교표·예상·대장·대기 강의 없음)
④ 과목 바꾸기: 빈 과목끼리 → 과목 홈 · (3q/ 허브) JB를 보다가 빈 과목으로 바꾸면 과목 홈, 보통 과목이면 JB 그대로
⑤ 없는 주소: 빈 과목의 _jb·_pred·_tbl·_final·_fig · 모르는 '_' 주소 · 없는 강의 → 과목 홈 + 알림
⑥ WAIT 카드: ✓·★·알아요/몰라요 단추 없음 · H·B·D·M 키로도 표시·메모가 안 남음 · 검색에 대기 카드가 안 뜸
⑦ build4가 곧 내는 꼴(stub:true · trends '' · top [] · tline·tstrat '')로 바꿔도 같은 화면·오류 0
과목·강의는 등록표·__h.PACKS에서(id를 박지 않음)."""
import json
from qsite import *
from playwright.sync_api import sync_playwright
rel = build(); base = serve()
Q4 = [q for q in QS.QS if q != '3q']
TOASTS = "(ns)=>{try{return JSON.parse(sessionStorage.getItem(ns+'toasts')||'[]').map(x=>x.t)}catch(e){return []}}"
def toasts(pg, ns): return pg.evaluate(TOASTS, ns)
def hash_(pg): return pg.evaluate('location.hash')
with sync_playwright() as p:
    br = p.chromium.launch()
    for vw, mob in (({'width': 1280, 'height': 900}, False), ({'width': 393, 'height': 852}, True)):
        W = vw['width']
        for q in Q4:
            ns = QS.QS[q]['ident']['ns']; U = url(base, rel[q])
            ctx = br.new_context(viewport=vw, is_mobile=mob, has_touch=mob); ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, body='{}'))
            pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda x: errs.append(str(x)[:200])); pg.on('dialog', lambda d: d.dismiss())
            pg.goto(U); pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('.hkick')", timeout=90000); pg.wait_for_timeout(600)
            ST = pg.evaluate("Object.keys(__h.PACKS).filter(s=>__h.isStub(__h.PACKS[s]))"); ALL = pg.evaluate("Object.keys(__h.PACKS)")
            if not ST: print(f'  SKIP {q} {W}px — 빈 과목 없음(자료가 다 들어옴)'); ctx.close(); continue
            allstub = len(ST) == len(ALL) == len(QS.sids(q))
            S = ST[0]; S2 = ST[1] if len(ST) > 1 else None
            # ① 허브 홈
            r = pg.evaluate("(ST)=>{const o={rows:0,wait:0,zero:0};ST.forEach(s=>{const e=document.querySelector('#home .hsj[data-s=\"'+s+'\"]');if(!e)return;o.rows++;if(e.classList.contains('stub')&&/자료 대기/.test(e.querySelector('.hcj').innerText))o.wait++;if(/\\d+\\s*\\/\\s*\\d+/.test(e.querySelector('.hcj').innerText))o.zero++;});o.qe=!!document.querySelector('#home .qempty');const hr=document.querySelector('#home .hres');o.res=hr?hr.innerText:'';o.go=hr?[...hr.querySelectorAll('.go-resume')].map(b=>b.dataset.d):[];o.todo=(document.querySelector('#home .htodo')||{}).innerText||'';o.ovf=document.documentElement.scrollWidth<=innerWidth+1;return o;}", ST)
            ok(r['rows'] == len(ST) and r['wait'] == len(ST) and r['zero'] == 0, f'{q} {W}px ① 허브 과목 표: 빈 과목 {len(ST)}줄 모두 「자료 대기」(0 / 0 없음) {r["rows"]}/{r["wait"]}/{r["zero"]}')
            ok('WAIT' not in r['go'], f'{q} {W}px ① 시작하기·이어서가 대기 강의로 안 감 {r["go"]}')
            if allstub:
                ok(r['qe'], f'{q} {W}px ① 과목이 전부 빈 과목 → 준비 안내(qEmpty)')
                ok('시작하기' not in r['res'] and '과목 자료가 오면' in r['res'], f'{q} {W}px ① 「시작하기 →」 대신 안내 ({r["res"][:40]!r})')
                ok('다 했어요' not in r['todo'] and '과목 자료가 오면' in r['todo'], f'{q} {W}px ① 오늘 할 일 = 자료 안내 ({r["todo"][:50]!r})')
            ok(r['ovf'], f'{q} {W}px ① 허브 홈 가로 넘침 없음')
            # ② 과목 홈
            def home_chk(tag):
                pg.goto(U + f'#/{S}/_home'); pg.wait_for_timeout(900)
                h = pg.evaluate("(()=>{const he=document.querySelector('#hero'),st=document.querySelector('#stage');return {hero:he.innerText,h1:(he.querySelector('h1')||{}).innerText||'',kick:(he.querySelector('.kick')||{}).innerText||'',lead:!!he.querySelector('.hlead .hwait'),btn:he.querySelectorAll('.hlead button').length,body:st.innerText,htop:!!document.querySelector('#htop'),side:(document.querySelector('#nav')||{}).innerText||'',ovf:document.documentElement.scrollWidth<=innerWidth+1,und:/undefined|NaN|\\[object/.test(he.innerText+st.innerText)};})()")
                ok(h['lead'] and h['btn'] == 0 and '자료 대기' in h['hero'], f'{q} {W}px ② {tag} 과목 머리 「자료 대기」 한 줄(개수 링크 없음)')
                ok(h['h1'].strip() != '' and not h['kick'].rstrip().endswith('·'), f'{q} {W}px ② {tag} 빈 h1·끝 구분점 없음 (h1={h["h1"]!r} kick={h["kick"]!r})')
                ok('기출을 다 맞혔어요' not in h['body'] and '- -' not in h['body'] and '- 교수' not in h['body'] and '- · ' not in h['body'], f'{q} {W}px ② {tag} 「기출을 다 맞혔어요」·「- -」 없음')
                ok('자료 대기' in h['body'], f'{q} {W}px ② {tag} 공부 순서·강의 칸 「자료 대기」')
                ok(not h['htop'], f'{q} {W}px ② {tag} 「2회 이상 출제」 0문항 절 없음')
                ok('- - ' not in h['side'] and '강의자료 대기' not in h['side'], f'{q} {W}px ② {tag} 과목 메뉴에 대기 강의 없음')
                ok(pg.evaluate("[...document.querySelectorAll('#nav .nvgrid .nvd')].map(b=>b.dataset.d).join(',')") == '_home', f'{q} {W}px ② {tag} 과목 메뉴 = 과목 홈(+ 넘버링)만')
                ok(h['ovf'] and not h['und'], f'{q} {W}px ② {tag} 가로 넘침·undefined 없음')
            home_chk('지금 팩')
            # ③ Ctrl+K
            ix = pg.evaluate("(ST)=>{const L=__h.qjIndex(),o={};ST.forEach(s=>{const sh=__h.sjShort(s);o[s]=L.filter(x=>x.g===sh).map(x=>(x.tab?x.tab+'|':'')+x.t);});return o;}", ST)
            bad = {s: v for s, v in ix.items() if len(v) != 3 or any(('대기' in t or 'JB' in t or '예상' in t or '비교표' in t or '한눈표' in t or '대장' in t) for t in v)}
            ok(not bad, f'{q} {W}px ③ Ctrl+K 색인: 빈 과목마다 과목 홈 + 넘버링 2 = 3개 {dict(list(bad.items())[:2])}')
            pg.keyboard.press('Control+k'); pg.wait_for_timeout(300); pg.fill('#qjq', S); pg.wait_for_timeout(300)
            n = pg.evaluate("(sh)=>[...document.querySelectorAll('#qjl .qjo:not([data-qs])')].filter(b=>(b.querySelector('small')||{}).textContent===sh).map(b=>b.innerText.replace(/\\s+/g,' ').trim())", pg.evaluate(f"__h.sjShort('{S}')"))
            ok(len(n) == 3 and not any('대기' in t for t in n), f'{q} {W}px ③ Ctrl+K 「{S}」 항목 {len(n)}개 {n}')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
            # ④ 과목 바꾸기(빈 과목끼리)
            if S2:
                pg.goto(U + f'#/{S}/_home'); pg.wait_for_timeout(600)
                pg.evaluate(f"document.querySelector('#side [data-nvsj=\"{S2}\"]').click()"); pg.wait_for_timeout(700)
                ok(hash_(pg) == f'#/{S2}/_home/_home', f'{q} {W}px ④ 과목 바꾸기 {S} → {S2} = 과목 홈 ({hash_(pg)})')
            # ⑤ 없는 주소
            for d, want in (('_jb', '자료가 아직 없어'), ('_pred', '자료가 아직 없어'), ('_tbl', '자료가 아직 없어'), ('_sum', '자료가 아직 없어'), ('_led', '자료가 아직 없어'), ('_final', '자료가 아직 없어'), ('_fig', '자료가 아직 없어'), ('_xyz', '그 화면을 찾지 못해'), ('NOPE', '그 강의를 찾지 못해')):
                pg.goto('about:blank'); pg.goto(U + f'#/{S}/{d}/{d if d[0] == "_" else "learn"}'); pg.wait_for_function("window.__h&&__h.VIEW==='doc'", timeout=60000); pg.wait_for_timeout(900)
                t = toasts(pg, ns)
                ok(hash_(pg) == f'#/{S}/_home/_home' and any(want in x for x in t[:3]) and pg.evaluate("document.querySelector('#stage').innerText.length>40"), f'{q} {W}px ⑤ #/{S}/{d} → 과목 홈 + 알림 ({hash_(pg)} · {t[:1]})')
            # ⑥ WAIT 카드
            pg.goto('about:blank'); pg.goto(U + f'#/{S}/WAIT/learn'); pg.wait_for_function("window.__h&&__h.VIEW==='doc'&&document.querySelector('#stage .tc')", timeout=60000); pg.wait_for_timeout(900)
            w = pg.evaluate("(()=>{const vis=q=>[...document.querySelectorAll(q)].some(e=>e.offsetParent!==null&&getComputedStyle(e).display!=='none');const he=document.querySelector('#hero');return {dn:vis('#stage .tc .dn'),cb:vis('#stage .tc .cbend'),rv:vis('#stage .tc .rvj'),lbm:!!he.querySelector('.hbm,.hrd'),kick:(he.querySelector('.kick')||{}).innerText||'',kit:getComputedStyle(document.querySelector('#kit')).display,tabs:[...document.querySelectorAll('#dtabs button[data-t]')].map(b=>b.dataset.t)};})()")
            ok(not w['dn'] and not w['cb'] and not w['rv'] and not w['lbm'], f'{q} {W}px ⑥ WAIT 카드 ✓·★·알아요/몰라요·강의 북마크 단추 없음 {w}')
            ok('- 교수' not in w['kick'] and '자료 대기' in w['kick'] and w['kit'] == 'none', f'{q} {W}px ⑥ WAIT 머리 「자료 대기」·도구 막대 없음 ({w["kick"]!r})')
            pg.evaluate("(()=>{const b=document.querySelector('#stage .tc .dn');if(b)b.click();})()")
            for k in ('h', 'b', 'd', 'm'): pg.keyboard.press(k); pg.wait_for_timeout(150)
            if not mob:
                bx = pg.evaluate("(()=>{const e=document.querySelector('#stage .tc .kb')||document.querySelector('#stage .tc .tbody');const r=e.getBoundingClientRect();return [r.left+6,r.top+r.height/2,r.left+Math.min(160,r.width-6)];})()")
                pg.mouse.move(bx[0], bx[1]); pg.mouse.down(); pg.mouse.move(bx[2], bx[1], steps=6); pg.mouse.up(); pg.wait_for_timeout(300)
            m = pg.evaluate("(ns)=>{const g=k=>{try{return JSON.parse(localStorage.getItem(ns+k)||'null')}catch(e){return null}};const S=__h.CUR.s;const n=o=>o&&typeof o==='object'?Object.keys(o).length:0;return {mode:__h.Kit.mode()||'',ann:n(__h.Kit.all()),done:n(g('done.'+S)),cbm:n(g('cbm.'+S)),memo:!!document.querySelector('#memo.on'),rk:document.querySelectorAll('#stage [data-rk]').length};}", ns)
            ok(not m['mode'] and m['ann'] == 0 and m['done'] == 0 and m['cbm'] == 0 and not m['memo'] and m['rk'] == 0, f'{q} {W}px ⑥ WAIT에서 ✓·H·B·D·M·끌기로 표시·메모가 안 남음 {m}')
            pg.goto(U + '#/'); pg.wait_for_timeout(500); pg.wait_for_function("__h.sxProg().ready||!__h.sidxN()", timeout=60000)
            pg.evaluate("(()=>{const s=document.querySelector('#gsearch');s.focus();s.value='강의자료';s.dispatchEvent(new Event('input',{bubbles:true}));})()"); pg.wait_for_timeout(1500)
            pg.wait_for_function("__h.sxProg().ready", timeout=60000); pg.wait_for_timeout(400)
            sr = pg.evaluate("[__h.VIEW,[...document.querySelectorAll('#home .sres')].filter(b=>b.dataset.d==='WAIT').length]")
            ok(sr[0] == 'search' and sr[1] == 0, f'{q} {W}px ⑥ 검색 색인에 대기 카드 없음 {sr}')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
            # ⑦ build4가 곧 내는 꼴
            pg.goto(U + '#/'); pg.wait_for_timeout(400)
            pg.evaluate("(ST)=>ST.forEach(s=>{const p=__h.PACKS[s];p.stub=true;p.trends='';p.top=[];(p.lect||[]).forEach(L=>{L.tline='';L.tstrat='';});})", ST)
            ok(pg.evaluate("(ST)=>ST.every(s=>__h.isStub(__h.PACKS[s]))", ST), f'{q} {W}px ⑦ pack.stub === true도 빈 과목')
            home_chk('stub:true 팩')
            ok(not errs, f'{q} {W}px 콘솔 오류 0 {errs[:3]}')
            ctx.close()
    # ④ (3q/ 허브) JB를 보다가 과목 바꾸기 — 빈 과목이면 과목 홈 · 보통 과목이면 JB 그대로
    if '3q' in rel:
        U = url(base, rel['3q']); ns = QS.QS['3q']['ident']['ns']
        ctx = br.new_context(viewport={'width': 1280, 'height': 900}); ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, body='{}'))
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda x: errs.append(str(x)[:200])); pg.on('dialog', lambda d: d.dismiss())
        pg.goto(U); pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('.hkick')", timeout=180000); pg.wait_for_timeout(600)
        J = pg.evaluate("Object.keys(__h.PACKS).filter(s=>(__h.PACKS[s].order||[]).length>0)")
        if len(J) >= 3:
            A, B, C = J[0], J[1], J[2]
            pg.goto(U + f'#/{A}/_jb/_jb'); pg.wait_for_function("__h.VIEW==='doc'&&document.querySelector('#cards')", timeout=60000); pg.wait_for_timeout(600)
            pg.evaluate(f"(()=>{{const p=__h.PACKS['{B}'];p.stub=true;p.order=[];}})()")   # 이 화면에서만 문항 0인 빈 과목으로(팩 파일은 그대로)
            pg.evaluate(f"document.querySelector('#side [data-nvsj=\"{B}\"]').click()"); pg.wait_for_timeout(900)
            ok(hash_(pg) == f'#/{B}/_home/_home', f'3q ④ JB에서 빈 과목({B})으로 바꾸면 과목 홈 ({hash_(pg)})')
            ok(pg.evaluate("!!document.querySelector('#hero .hlead .hwait')"), '3q ④ 그 과목 머리 「자료 대기」')
            pg.goto(U + f'#/{A}/_jb/_jb'); pg.wait_for_timeout(900)
            pg.evaluate(f"document.querySelector('#side [data-nvsj=\"{C}\"]').click()"); pg.wait_for_timeout(900)
            ok(hash_(pg) == f'#/{C}/_jb/_jb', f'3q ④ JB에서 보통 과목({C})으로 바꾸면 JB 그대로 ({hash_(pg)})')
            pg.goto('about:blank'); pg.goto(U + f'#/{B}/_pred/_pred'); pg.wait_for_function("window.__h&&__h.VIEW==='doc'", timeout=180000); pg.wait_for_timeout(900)
            ok(not errs, f'3q 콘솔 오류 0 {errs[:3]}')
        else: print('  SKIP 3q ④ — JB가 있는 과목이 3개 미만')
        ctx.close()
    br.close()
done()
