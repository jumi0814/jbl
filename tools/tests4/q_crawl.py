"""11-10 W0 전 화면 훑기 — 허브마다(미리 보기 사이트 뿌리 = 지금 쿼터 · 3q/ = 3Q · 시험용 사이트 fixture = 4Q 정체성 + 3Q 내용)
과목마다 모든 과목 문서(_home·_jb·_pred·_final·_fig·_sum·_led·_tbl·_cbm·_marks 중 메뉴에 있는 것) + 강의마다 모든 탭을 열어
① 화면 오류(pageerror)·콘솔 error·HTTP ≥400 0 ② 글·속성에 undefined / NaN / [object Object] 0 ③ 가로 넘침 0 ④ 빈 #stage 0 ⑤ 그 주소가 그 화면으로 열림(다른 곳으로 튕기지 않음)
컴퓨터 1280×900 = 전부 · 폰 393×852 = 허브 화면 + 과목마다 과목 홈·JB 문제·가장 큰 강의 첫 탭(시간 줄이기 — 폰 전부는 JBL_CRAWL_VW=393).
과목·강의·탭은 __h.PACKS·과목 메뉴에서 찾음(id를 박지 않음) — 빈 과목(자료 대기)도 같은 검사.
가로 넘침: body·html이 overflow-x:clip이라 scrollWidth로는 안 잡힘 → 보이는 요소의 오른쪽 끝을 직접 잼(11-11).
  .venv/bin/python tools/tests4/q_crawl.py                 # 전부
  JBL_CRAWL=quick …                                        # 과목마다 과목 문서 + 가장 큰 강의 하나만(약 3분)
  JBL_CRAWL=lite …                                         # 과목 문서 + 가장 큰 강의 2개는 모든 탭 · 나머지 강의는 첫 탭만
  JBL_CRAWL_SITE=fx|3q|root  JBL_CRAWL_SID=CONS,PHARM  JBL_CRAWL_VW=1280|393   # 좁혀서 · JBL_CRAWL_LOG=1 = 화면마다 한 줄"""
import json, time
from qsite import *
from playwright.sync_api import sync_playwright
VERB = bool(os.environ.get('JBL_CRAWL_LOG')); selfok = []
QUICK = os.environ.get('JBL_CRAWL') == 'quick'; LITE = os.environ.get('JBL_CRAWL') == 'lite'; ONLY = [x for x in os.environ.get('JBL_CRAWL_SID', '').split(',') if x]
OSITE = os.environ.get('JBL_CRAWL_SITE', ''); OVW = os.environ.get('JBL_CRAWL_VW', ''); FULLM = OVW == '393'
cur = QS.current(); rel = build(); fx = build_fixture(); b1 = serve(); b2 = serve(fx['dir'])
has = lambda q, d: [s for s in QS.sids(q) if os.path.exists(os.path.join(d, 'packs', s + '.js'))]
SITES = [('root', f'뿌리({cur})', url(b1, rel[cur]), has(cur, os.path.join(SITE, rel[cur])))]
SITES += [(q, f'{q}/', url(b1, rel[q]), has(q, os.path.join(SITE, rel[q]))) for q in rel if q != cur]
SITES += [('fx', f'fixture({fx["ident"]} 정체성 + {fx["content"]} 내용)', url(b2, ''), fx['sids'])]
VWS = [({'width': 1280, 'height': 900}, False), ({'width': 393, 'height': 852}, True)]
HUBV = ['#/', '#/_cal', '#/_time', '#/_bm', '#/_num', '#/_numr']
SDOCS = ['_home', '_jb', '_pred', '_final', '_fig', '_sum', '_led', '_tbl', '_cbm', '_marks']
# 화면 하나 검사 — 보이는 틀(위 막대·메뉴·머리·탭·본문 / 허브 홈)의 글과 속성 · 가로 넘침 · 빈 본문
CHECK = r"""(kind)=>{const $=s=>document.querySelector(s),sub=$('#subj'),doc=sub&&!sub.hidden,box=(doc?['#top','#nav','#hero','#dtabs','#stage']:['#top','#nav','#home']).map($).filter(Boolean),out={bad:[],over:'',empty:''};
 const RX=/\bundefined\b|\bNaN\b|\[object Object\]/;
 for(const b of box){const t=b.textContent||'',m=RX.exec(t);if(m)out.bad.push('#'+b.id+' 글 «'+t.slice(Math.max(0,m.index-40),m.index+50).replace(/\s+/g,' ')+'»');
  const a=b.querySelector('[href*="undefined"],[src*="undefined"],[title*="undefined"],[aria-label*="undefined"],[placeholder*="undefined"],[data-id="undefined"],[data-d="undefined"],[data-s="undefined"],[data-aid*="undefined"],[title*="NaN"],[style*="NaN"],[title*="[object Object]"],[href*="[object"]');
  if(a)out.bad.push('#'+b.id+' 속성 '+a.outerHTML.slice(0,140).replace(/\s+/g,' '));}
 /* 11-11 가로 넘침 — body·html이 overflow-x:clip이라 scrollWidth는 늘 창 폭(넘쳐도 안 늘어남) → 보이는 요소의 오른쪽 끝을 직접 잼:
    창 밖으로 나갔는데 자르는/스크롤하는 조상(표 가로 스크롤 상자 등)이 없는 것 = 넘침(붙박이·숨긴 것·접힌 details 안·창 밖에서 시작하는 것(밀어 둔 서랍)은 뺌) */
 const W=innerWidth,sw=document.documentElement.scrollWidth;let w=null,wr=0;
 for(const b of box)for(const e of b.querySelectorAll('*')){const r=e.getBoundingClientRect();if(!(r.width>0&&r.height>0)||r.right<=W+1||r.right<=wr||r.left>=W)continue;if(e.checkVisibility&&!e.checkVisibility())continue;   /* 접힌 <details> 안(25 → 26 바뀐 점 알약 등 — 안 그려지지만 크기는 잡힘)·display:none 조상 */
  let p=e,clip=false;while(p&&p!==document.body){const c=getComputedStyle(p);if((p!==e&&c.overflowX!=='visible')||c.position==='fixed'||c.visibility==='hidden'||+c.opacity===0){clip=true;break;}p=p.parentElement;}
  if(!clip){w=e;wr=r.right;}}
 if(sw>W+1||w)out.over=(w?Math.round(wr):sw)+'>'+W+(w?' ← '+w.tagName.toLowerCase()+(w.id?'#'+w.id:'')+(w.className&&w.className.baseVal==null?'.'+String(w.className).trim().split(/\s+/).join('.'):'')+' «'+(w.textContent||'').trim().slice(0,30).replace(/\s+/g,' ')+'»':'');
 const st=doc?$('#stage'):$('#home'),tx=st?(st.innerText||'').trim():'';
 if(!st||tx.length<(kind==='hub'?20:12)||!st.firstElementChild)out.empty='글 '+tx.length+'자';
 out.len=tx.length;return out;}"""
AT = "([s,d,t])=>{const c=window.__h&&__h.CUR;return !!(c&&c.s===s&&c.d===d&&(!t||c.t===t)&&!document.querySelector('#subj').hidden&&document.querySelector('#stage').firstElementChild);}"
SETTLE = "()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>setTimeout(r,60))))"
tot = {'views': 0}; t00 = time.time()
with sync_playwright() as p:
    br = p.chromium.launch()
    for sk, sname, U, sids in SITES:
        if OSITE and sk != OSITE: continue
        for vw, mob in VWS:
            if OVW and str(vw['width']) != OVW: continue
            tag = f'{sname} {vw["width"]}px'; t0 = time.time(); nv = 0; nf0 = len(fail)
            ctx = br.new_context(viewport=vw, is_mobile=mob, has_touch=mob); ctx.route('https://api.github.com/**', lambda r: r.fulfill(status=401, body='{}'))
            ev = []   # (종류, 글) — 화면마다 비움
            def page():
                pg = ctx.new_page()
                pg.on('pageerror', lambda x: ev.append(('오류', str(x)[:200])))
                pg.on('console', lambda m: m.type == 'error' and ev.append(('콘솔', m.text[:200])))
                pg.on('response', lambda r: r.status >= 400 and ev.append(('HTTP', f'{r.status} {r.url[-70:]}')))
                pg.on('requestfailed', lambda r: 'ERR_ABORTED' not in (r.failure or '') and ev.append(('요청 실패', f'{r.failure} {r.url[-70:]}')))
                pg.on('dialog', lambda d: d.dismiss())
                return pg
            def look(pg, name, kind='doc'):
                global_nv[0] += 1
                pg.evaluate(SETTLE); r = pg.evaluate(CHECK, kind); e = list(ev); ev.clear()
                if VERB: print(f'       {tag} {name} 글 {r["len"]}자')
                if e: ok(False, f'{tag} {name}: {e[0][0]} {len(e)}건 — {e[0][1]}')
                if r['bad']: ok(False, f'{tag} {name}: {r["bad"][0]}')
                if r['over']: ok(False, f'{tag} {name}: 가로 넘침 {r["over"]}')
                if r['empty']: ok(False, f'{tag} {name}: 빈 화면({r["empty"]})')
            global_nv = [0]
            # 허브 화면
            pg = page(); pg.goto(U); wait_hub(pg, len(sids))
            packs = pg.evaluate('Object.keys(__h.PACKS)')
            ok(sorted(packs) == sorted(sids), f'{tag} 과목 팩 {len(packs)}개 = 준비된 과목 {len(sids)}개')
            for h in HUBV:
                pg.evaluate('h=>{location.hash=h;}', h); pg.wait_for_timeout(350); look(pg, h, 'hub')
            if not selfok:   # 검사기 자체 검사(한 번) — 일부러 넣은 undefined 글·NaN 속성·넓은 칸·빈 본문을 잡는지
                pg.evaluate("()=>{location.hash='#/';}"); pg.wait_for_timeout(300)
                pg.evaluate("()=>{const h=document.querySelector('#home'),d=document.createElement('div');d.id='__qc';d.innerHTML='<p>값 undefined 줄</p><i title=\"NaN분\"></i><div style=\"width:'+(innerWidth+300)+'px;height:4px\"></div>';h.appendChild(d);}")
                r = pg.evaluate(CHECK, 'hub'); pg.evaluate("()=>{const d=document.querySelector('#__qc');if(d)d.remove();}")
                ok(len(r['bad']) == 2 and bool(r['over']), f'검사기 자체 검사 — 넣은 undefined 글·NaN 속성·가로 넘침을 잡음 {r["bad"][:2]} {r["over"][:60]}'); selfok.append(1)
            info = pg.evaluate(PACKINFO); pg.close()
            for s in packs:
                if ONLY and s not in ONLY: continue
                pg = page(); pg.goto(U + f'#/{s}/_home/_home')
                try: wait_hub(pg, 1); pg.wait_for_function(AT, arg=[s, '_home', ''], timeout=120000)
                except Exception as e: ok(False, f'{tag} #/{s}/_home 안 열림 {str(e)[:80]}'); pg.close(); continue
                nav = pg.evaluate(NAVDOCS); docs = [d for d in SDOCS if d in nav]
                lect = info[s]['lect']; big = sorted(lect, key=lambda L: -L['size']['learn'])
                if QUICK: lect = big[:1]
                if mob and not FULLM: views = [(d, d) for d in docs if d in ('_home', '_jb')] + [(L['k'], t) for L in big[:1] for t in L['tabs'][:1]]   # 폰은 과목마다 문서 2~3개만(시간 — 전부는 JBL_CRAWL_VW=393)
                elif LITE: views = [(d, d) for d in docs] + [(L['k'], t) for L in lect for t in (L['tabs'] if L in big[:2] else L['tabs'][:1])]   # 가장 큰 강의 2개는 모든 탭 · 나머지는 첫 탭(학습)만
                else: views = [(d, d) for d in docs] + [(L['k'], t) for L in lect for t in L['tabs']]
                for d, t in views:
                    h = f'#/{s}/{d}/{t}'
                    try:
                        pg.evaluate('h=>{location.hash=h;}', h); pg.wait_for_function(AT, arg=[s, d, t], timeout=30000)
                    except Exception:
                        c = pg.evaluate("JSON.stringify(window.__h&&__h.CUR)"); ok(False, f'{tag} {h}: 그 화면으로 안 열림(지금 {c} · {pg.evaluate("location.hash")})'); ev.clear(); continue
                    look(pg, h)
                pg.close()
            nv = global_nv[0]; tot['views'] += nv; nb = len(fail) - nf0
            if nb: print(f'  ---- {tag}: 화면 {nv}개 · 과목 {len(packs)} 가운데 걸린 것 {nb}건 ({time.time() - t0:.0f}초)')
            else: ok(True, f'{tag}: 화면 {nv}개 · 과목 {len(packs)} — 오류·undefined/NaN·가로 넘침·빈 화면 0 ({time.time() - t0:.0f}초)')
            ctx.close()
    br.close()
print(f'  훑은 화면 {tot["views"]}개 · {time.time() - t00:.0f}초')
done()
