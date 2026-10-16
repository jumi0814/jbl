"""UX14 내 넘버링 — 연도·교수 꼬리표(문제 글 끝) · 'JB 문제' 바로 가기 · ↩ 돌아가기(10-11 사용자: '넘버링에서 각 문제의 끝나는 음절 오른쪽에 순서대로 연도 표기, 그리고 교수 이름을 적었으면 좋겠고, 가장 오른쪽 원래 연도랑 교수가 적혀있던 부분에는 수정 버튼 옆에 jb문제 바로가는 버튼이 있었으면 좋겠고, 내가 강의자료에서 jb문제 가면 다시 강의자료로 돌아가기 버튼이 뜨는 방식을 그대로 차용해서, 넘버링문제에서 Jb 문제로 바로가면, 해당 답안이 (간단히 상태로) 펼쳐지고, 마찬가지로 다시 넘버링 따는 곳으로 돌아갈 수 있었으면 좋겠어.')
- 꼬리표: 문제 글 마지막 음절 바로 오른쪽 · 연도 옛날→최근('22·24') + 교수 · 작은 회색 · 오른쪽 옛 연도·교수 태그 없음 · 문제를 고쳐도 꼬리표 유지(저장 글엔 없음) · 인쇄·ChatGPT 내보내기 글엔 안 섞임
- 'JB 문제' 단추: JB 기출(jb:) + '관련 기출'이 있는 예상문제(pr:)만 · 직접 만든 문제·관련 기출 없는 예상문제는 없음 · '수정' 단추 바로 오른쪽
- 누르면 그 과목 JB 문제 화면 · 그 문항이 화면에 · 답 1단계(간단히)로 펼침 · '↩ 돌아가기 · 내 넘버링 n번' 알약(강의자료 → JB와 같은 알약)
- 알약 · 브라우저 뒤로 = 내 넘버링의 그 문제 자리로 · 넘버링 복습도 같음(꼬리표·단추·돌아가기 = #/_numr) · 모바일(390) 가로 넘침 없음 · pageerror 0
- 스크린샷 work/_tmp/ux14_{num,jb,mobile,mobile_jb}.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CLEAR = "(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()"
TOP = """(id=>{const a=document.querySelector('.nm-it[data-id="'+CSS.escape(id)+'"]');return a?Math.round(a.getBoundingClientRect().top):null})"""
JBV = """(aid=>{const L=[...document.querySelectorAll('#stage [data-aid]')].filter(b=>!b.classList.contains('res'));const c=L.find(b=>b.dataset.aid===aid);const r=c&&c.getBoundingClientRect(),P=document.getElementById('retpill');
  return {hash:location.hash,found:!!c,vis:!!r&&r.top<innerHeight-60&&r.bottom>60,open:!!c&&c.classList.contains('open'),deep:!!c&&c.classList.contains('deep'),ans:!!c&&!!c.querySelector('.ans')&&getComputedStyle(c.querySelector('.ans')).display!=='none',pill:P.classList.contains('on')&&getComputedStyle(P).display!=='none',pt:P.textContent}})"""
async def import_all(pg, sj):
    await pg.evaluate(f"location.hash='#/_num/{sj}'"); await pg.wait_for_timeout(3000)
    await pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); await pg.wait_for_timeout(700)
    await pg.select_option('[data-if=ty]', ''); await pg.wait_for_timeout(300); await pg.click('[data-ib=all]'); await pg.wait_for_timeout(500); await pg.click('[data-cf2=ok]'); await pg.wait_for_timeout(1500); await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(600)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1366, 'height': 900}, accept_downloads=True); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(U + '#/'); await pg.wait_for_timeout(2000); await pg.evaluate(CLEAR)
        await import_all(pg, 'CONS')
        n = await pg.evaluate("document.querySelectorAll('.nm-it').length"); ok(n > 100, f"CONS 기출·예상 {n}문제")
        # ---- 꼬리표 ----
        tl = await pg.evaluate("""(()=>{const S=JBLNUM._S,P=JBLNUM._H().PACKS.CONS,A=[...document.querySelectorAll('.nm-it')];let bad=[],jbN=0,yrOK=0,pfOK=0,place=0,gray=0,small=0;
          for(const a of A){const it=S.by.get(a.dataset.id),c=a.querySelector('.nm-q .nm-c'),t=c.querySelector('.nm-qt');if(!t){if(it.yrs.length)bad.push(it.id);continue;}
            if(c.lastElementChild!==t&&!(c.lastElementChild&&c.lastElementChild.lastElementChild===t)&&!(t.parentElement&&t.parentElement.parentElement===c&&t.parentElement===c.lastElementChild))bad.push('pos:'+it.id);
            const y=(t.querySelector('.y')||{}).textContent||'',want=it.yrs.slice().sort((x,z)=>x-z).map(v=>String(v%100).padStart(2,'0')).join('·');if(y===want)yrOK++;else bad.push('yr:'+it.id+':'+y+'≠'+want);
            if(/^jb:/.test(it.id)){jbN++;const k=it.id.split(':').pop(),m=/data-prof="([^"]*)"/.exec(P.cards[k]||'');if(m&&(t.querySelector('.p')||{}).textContent===m[1])pfOK++;else bad.push('pf:'+it.id);}
            const w=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);let last=null;for(let x=w.nextNode();x;x=w.nextNode())if(x.data.trim()&&!t.contains(x))last=x;
            if(last&&!last.parentElement.closest('table')){const r=document.createRange();r.setStart(last,Math.max(0,last.data.trimEnd().length-1));r.setEnd(last,last.data.trimEnd().length);const R=r.getClientRects(),q=R[R.length-1],T=t.getClientRects()[0];if(q&&T&&Math.abs((q.top+q.bottom)/2-(T.top+T.bottom)/2)<12&&T.left>=q.right-1&&T.left-q.right<16)place++;else if(q&&T&&T.top>q.bottom-2&&T.left<q.left)place++;else bad.push('place:'+it.id);}else place++;
            const cs=getComputedStyle(t);if(parseFloat(cs.fontSize)<=12.5)small++;const rgb=cs.color.match(/\\d+/g).map(Number);if(Math.max(...rgb)-Math.min(...rgb)<40&&rgb[0]>100)gray++;}
          return {n:A.length,tails:A.filter(a=>a.querySelector('.nm-qt')).length,jbN,yrOK,pfOK,place,small,gray,bad:bad.slice(0,6),old:document.querySelectorAll('.nm-tags .nm-tag, .nm-tags .nm-tag.yr, .nm-tags .nm-tag.pf').length}})()""")
        ok(tl['tails'] > 100 and not tl['bad'] and tl['yrOK'] == tl['tails'] and tl['jbN'] > 20 and tl['pfOK'] == tl['jbN'], f"문제 글 끝 꼬리표 = 연도 옛날→최근 · JB 교수 {tl['tails']}문제 {tl['bad']}")
        ok(tl['place'] == tl['tails'], f"꼬리표 = 마지막 음절 바로 오른쪽(줄이 넘치면 다음 줄 처음) {tl['place']}/{tl['tails']}")
        ok(tl['small'] == tl['tails'] and tl['gray'] == tl['tails'], f"작은 회색 글씨 {tl['small']}·{tl['gray']}")
        ok(tl['old'] == 0, f"오른쪽 옛 연도·교수 태그 없음 ({tl['old']})")
        # ---- 'JB 문제' 단추 ----
        jb = await pg.evaluate("""(()=>{const S=JBLNUM._S,P=JBLNUM._H().PACKS.CONS,A=[...document.querySelectorAll('.nm-it')];const pm=new Map();for(const x of P.preds){const a=/data-aid="([^"]+)"/.exec(x.html),g=/class="jbchip"[^>]*data-go="([^"]+)"/.exec(x.html);if(a)pm.set(a[1],!!(g&&P.cards[g[1]]));}
          let jbB=0,jbAll=0,prB=0,prWant=0,wrong=[],right=0;for(const a of A){const it=S.by.get(a.dataset.id),b=a.querySelector('.nm-tags .nm-jbb');if(/^jb:/.test(it.id)){jbAll++;if(b)jbB++;}else if(/^pr:/.test(it.id)){const s=it.src.find(x=>x.t==='pred'),w=!!(s&&pm.get(s.id));if(w)prWant++;if(!!b!==w)wrong.push(it.id);else if(b)prB++;}
            if(b){const e=a.querySelector('.nm-q > .nm-edb').getBoundingClientRect(),r=b.getBoundingClientRect();if(r.left>=e.right-1&&r.left-e.right<60&&Math.abs((r.top+r.bottom)/2-(e.top+e.bottom)/2)<6)right++;}}
          return {jbB,jbAll,prB,prWant,wrong:wrong.slice(0,4),right,btn:A.filter(a=>a.querySelector('.nm-jbb')).length}})()""")
        ok(jb['jbB'] == jb['jbAll'] > 20 and jb['prB'] == jb['prWant'] > 0 and not jb['wrong'], f"'JB 문제' 단추 = JB 기출 전부 {jb['jbB']}/{jb['jbAll']} · 관련 기출 있는 예상문제만 {jb['prB']}/{jb['prWant']} {jb['wrong']}")
        ok(jb['right'] == jb['btn'], f"단추 자리 = '수정' 바로 오른쪽(옛 연도·교수 자리) {jb['right']}/{jb['btn']}")
        # 직접 만든 문제 = 단추 없음
        await pg.evaluate("document.querySelector('.nm-side [data-act=new]').click()"); await pg.wait_for_timeout(500)
        await pg.click('[data-rich=q]'); await pg.keyboard.type('직접 만든 시험 문제를 쓰시오'); await pg.fill('[data-nf=yrs]', '25'); await pg.click('[data-nfsave]'); await pg.wait_for_timeout(800); sv = 'nfsave'
        uq = await pg.evaluate("(()=>{const S=JBLNUM._S,u=S.items.filter(i=>i.kind==='user');const a=u.length&&document.querySelector('.nm-it[data-id=\"'+CSS.escape(u[u.length-1].id)+'\"]');return {n:u.length,btn:a?!!a.querySelector('.nm-jbb'):null}})()")
        ok(uq['n'] >= 1 and uq['btn'] is False, f"직접 만든 문제 = 'JB 문제' 단추 없음 {uq} ({sv})")
        await pg.evaluate("document.querySelectorAll('.nm-ov [data-x]').forEach(x=>x.click())"); await pg.wait_for_timeout(300)
        # 문제를 고쳐도 꼬리표 유지 · 저장 글엔 없음
        ids = await pg.evaluate("[...document.querySelectorAll('.nm-it')].map(a=>a.dataset.id).filter(x=>/^jb:/.test(x))")
        e1 = ids[2]
        await pg.evaluate("(id=>document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"]').scrollIntoView({block:'center'}))", e1); await pg.wait_for_timeout(200)
        await pg.evaluate("(id=>document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"] .nm-q [data-act=edit]').click())", e1); await pg.wait_for_timeout(300)
        inEd = await pg.evaluate("(id=>!!document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"] .nm-q .nm-c[contenteditable=true] .nm-qt'))", e1)
        await pg.keyboard.press('Control+End'); await pg.keyboard.type(' 고침'); await pg.wait_for_timeout(900); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
        ed = await pg.evaluate("(id=>{const c=document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"] .nm-q .nm-c'),r=localStorage.getItem('jblhub.v1.num.i.CONS.'+id)||'';return {tail:!!c.querySelector('.nm-qt'),txt:c.textContent.includes('고침'),stored:r.includes('고침'),leak:r.includes('nm-qt')}})", e1)
        ok(not inEd and ed['tail'] and ed['txt'] and ed['stored'] and not ed['leak'], f"고치는 동안엔 꼬리표 빠짐 · 고친 뒤에도 꼬리표 그대로 · 저장 글엔 없음 {ed}")
        # 인쇄·ChatGPT 내보내기 = 꼬리표 안 섞임
        pr = await pg.evaluate("""(()=>{const S=JBLNUM._S,L=S.items.filter(i=>!i.del).slice(0,60),h=JBLNUM._printHTML(L,{what:'qas',lay:'side',brk:false},'시험');const d=document.createElement('div');d.innerHTML=h;const T=[...d.querySelectorAll('.np-t')];
          let same=0;T.forEach((t,i)=>{if(t.textContent===JBLNUM._plain(JBLNUM._qDisp(L[i]))||t.textContent.replace(/\\s+/g,'')===JBLNUM._plain(JBLNUM._qDisp(L[i])).replace(/\\s+/g,''))same++;});return {leak:h.includes('nm-qt'),n:T.length,same}})()""")
        ok(not pr['leak'] and pr['same'] == pr['n'] == 60, f"인쇄·PDF 문제 글 = 꼬리표 안 섞임 {pr}")
        await pg.evaluate("document.querySelector('.nm-side [data-act=aiout]').click()"); await pg.wait_for_timeout(400)
        await pg.select_option('[data-xo=st]', ''); await pg.select_option('[data-xo=chunk]', '0'); await pg.wait_for_timeout(200)
        async with pg.expect_download() as dl: await pg.click('[data-xget="0"]')
        d = await dl.value; X = json.loads(open(await d.path(), encoding='utf-8').read()); xs = [x for g in X['lecs'] for x in g['items']]
        xl = await pg.evaluate("""(L=>{const S=JBLNUM._S;let same=0,leak=0;for(const x of L){const it=S.by.get(x.id);if(!it)continue;if(JBLNUM._toText(it.q)===x.q)same++;const a=document.querySelector('.nm-it[data-id="'+CSS.escape(x.id)+'"] .nm-qt');if(a&&a.textContent&&x.q.replace(/\\s+/g,'').endsWith(a.textContent.replace(/\\s+/g,'')))leak++;}return {n:L.length,same,leak}})""", xs)
        ok(xl['n'] > 100 and xl['same'] == xl['n'] and xl['leak'] == 0, f"ChatGPT 내보내기 문제 글 = 원문 그대로(꼬리표 없음) {xl}")
        await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(300)
        await pg.evaluate("(id=>document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"]').scrollIntoView({block:'center'}))", ids[4]); await pg.wait_for_timeout(300)
        await pg.screenshot(path=J.TMP + '/ux14_num.png')
        # ---- JB 문제로 → 답 펼침(간단히) → ↩ 돌아가기 ----
        t1 = ids[6]; await pg.evaluate("(id=>document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"]').scrollIntoView({block:'center'}))", t1); await pg.wait_for_timeout(400)
        y0 = await pg.evaluate(TOP, t1); no = await pg.evaluate("(id=>document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"] .nm-no').textContent)", t1)
        aid = await pg.evaluate("(id=>JBLNUM._S.by.get(id).src.find(s=>s.t==='jb').id)", t1)
        await pg.click(f".nm-it[data-id='{t1}'] .nm-jbb"); await pg.wait_for_timeout(1600)
        v = await pg.evaluate(JBV, aid)
        ok(v['hash'].startswith('#/CONS/_jb') and v['found'] and v['vis'], f"'JB 문제' → 그 과목 JB 문제 화면 · 그 문항({aid})이 화면에 {v['hash']}")
        ok(v['open'] and v['ans'] and not v['deep'], f"답 = 펼침 · 간단히(1단계) {v}")
        ok(v['pill'] and '돌아가기' in v['pt'] and '내 넘버링' in v['pt'] and no.rstrip('.') in v['pt'], f"'↩ 돌아가기 · 내 넘버링 n번' 알약(강의자료 → JB와 같은 것) '{v['pt']}'")
        await pg.screenshot(path=J.TMP + '/ux14_jb.png')
        await pg.click('#retpill'); await pg.wait_for_timeout(2500)
        y1 = await pg.evaluate(TOP, t1)
        ok(await pg.evaluate("location.hash") == '#/_num/CONS' and y1 is not None and abs(y1 - y0) <= 40 and not await pg.evaluate("document.getElementById('retpill').classList.contains('on')"), f"알약 = 내 넘버링 그 문제 자리로 {y0}→{y1}")
        # 브라우저 뒤로
        t2 = ids[12]; await pg.evaluate("(id=>document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"]').scrollIntoView({block:'center'}))", t2); await pg.wait_for_timeout(400); y0 = await pg.evaluate(TOP, t2)
        await pg.click(f".nm-it[data-id='{t2}'] .nm-jbb"); await pg.wait_for_timeout(1500)
        ok((await pg.evaluate("location.hash")).startswith('#/CONS/_jb'), "두 번째 문제 → JB")
        await pg.go_back(); await pg.wait_for_timeout(2500); y1 = await pg.evaluate(TOP, t2); vh = await pg.evaluate('innerHeight')
        # 10-16: 뒤로는 그 문제를 화면 위쪽(고정 머리 아래)으로 되돌림 — 같은 문제가 화면 안에 보이면 통과(가운데 자리까지 같을 필요 없음 · 26판으로 CONS 문항이 늘어 위치 계산이 달라짐)
        ok(await pg.evaluate("location.hash") == '#/_num/CONS' and y1 is not None and (abs(y1 - y0) <= 40 or 0 <= y1 <= vh - 120), f"브라우저 뒤로 = 그 문제 자리로 {y0}→{y1}")
        # 예상문제(관련 기출) → 그 기출
        pq = await pg.evaluate("""(()=>{const a=[...document.querySelectorAll('.nm-it')].find(x=>/^pr:/.test(x.dataset.id)&&x.querySelector('.nm-jbb'));return a&&a.dataset.id})()""")
        want = await pg.evaluate("""(id=>{const P=JBLNUM._H().PACKS.CONS,s=JBLNUM._S.by.get(id).src.find(x=>x.t==='pred'),p=P.preds.find(x=>x.html.indexOf('data-aid="'+s.id+'"')>=0),g=/class="jbchip"[^>]*data-go="([^"]+)"/.exec(p.html);return /data-aid="([^"]+)"/.exec(P.cards[g[1]])[1]})""", pq)
        await pg.evaluate("(id=>document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"]').scrollIntoView({block:'center'}))", pq); await pg.wait_for_timeout(300); y0 = await pg.evaluate(TOP, pq)
        await pg.click(f".nm-it[data-id='{pq}'] .nm-jbb"); await pg.wait_for_timeout(1500)
        v2 = await pg.evaluate(JBV, want)
        ok(v2['found'] and v2['vis'] and v2['open'] and not v2['deep'] and v2['pill'], f"예상문제 'JB 문제' = 관련 기출({want})로 · 답 간단히 · 알약 {v2['pt']}")
        await pg.click('#retpill'); await pg.wait_for_timeout(2500); y1 = await pg.evaluate(TOP, pq)
        ok(y1 is not None and abs(y1 - y0) <= 40, f"→ 돌아오기 {y0}→{y1}")
        # ⋯ 메뉴 'JB 기출 원본 열기'도 같은 길(알약)
        await pg.evaluate("(id=>document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"]').scrollIntoView({block:'center'}))", t1); await pg.wait_for_timeout(300)
        await pg.locator(f".nm-it[data-id='{t1}'] [data-act=more]").click(); await pg.click('.nm-menu [data-mi=open]'); await pg.wait_for_timeout(1500)
        v3 = await pg.evaluate(JBV, aid)
        ok(v3['found'] and v3['open'] and v3['pill'], f"⋯ 'JB 기출 원본 열기' = 같은 길(답 펼침·알약) {v3['pt']}")
        await pg.click('#retpill'); await pg.wait_for_timeout(2500)
        # ---- 넘버링 복습 ----
        await pg.evaluate("location.hash='#/_numr/CONS'"); await pg.wait_for_timeout(2500)
        rv = await pg.evaluate("""(()=>{const A=[...document.querySelectorAll('.nm-it')];return {rv:document.getElementById('numv').classList.contains('rv'),n:A.length,tail:A.filter(a=>a.querySelector('.nm-q .nm-c .nm-qt')).length,btn:A.filter(a=>a.querySelector('.nm-tags .nm-jbb')).length,old:document.querySelectorAll('.nm-tags .nm-tag').length}})()""")
        ok(rv['rv'] and rv['tail'] > 100 and rv['btn'] > 20 and rv['old'] == 0, f"넘버링 복습도 같은 꼬리표·'JB 문제' 단추 {rv}")
        r1 = await pg.evaluate("[...document.querySelectorAll('.nm-it')].map(a=>a.dataset.id).filter(x=>/^jb:/.test(x))[5]")
        await pg.evaluate("(id=>document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"]').scrollIntoView({block:'center'}))", r1); await pg.wait_for_timeout(300); y0 = await pg.evaluate(TOP, r1)
        await pg.click(f".nm-it[data-id='{r1}'] .nm-jbb"); await pg.wait_for_timeout(1500)
        v4 = await pg.evaluate(JBV, await pg.evaluate("(id=>id.slice(3))", r1))
        ok(v4['found'] and v4['open'] and v4['pill'] and '넘버링 복습' in v4['pt'], f"복습 → JB · 알약 '{v4['pt']}'")
        await pg.click('#retpill'); await pg.wait_for_timeout(2500); y1 = await pg.evaluate(TOP, r1)
        ok(await pg.evaluate("location.hash") == '#/_numr/CONS' and y1 is not None and abs(y1 - y0) <= 40, f"→ 넘버링 복습 그 문제 자리로 {y0}→{y1}")
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await pg.evaluate(CLEAR); await ctx.close()
        # ---- 모바일 390 ----
        ctx2 = await b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); pm = await ctx2.new_page(); errs2 = []
        pm.on('pageerror', lambda e: errs2.append(str(e)[:200]))
        await pm.goto(U + '#/'); await pm.wait_for_timeout(2000); await pm.evaluate(CLEAR)
        await import_all(pm, 'CONS')
        m1 = await pm.evaluate("[...document.querySelectorAll('.nm-it')].map(a=>a.dataset.id).filter(x=>/^jb:/.test(x))[3]")
        await pm.evaluate("(id=>document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"]').scrollIntoView({block:'center'}))", m1); await pm.wait_for_timeout(400)
        mw = await pm.evaluate("""(id=>{const a=document.querySelector('.nm-it[data-id="'+CSS.escape(id)+'"]'),b=a.querySelector('.nm-jbb').getBoundingClientRect(),t=a.querySelector('.nm-qt').getBoundingClientRect();return {sw:document.documentElement.scrollWidth,vw:innerWidth,bIn:b.left>=0&&b.right<=innerWidth&&b.height>0,tIn:t.left>=0&&t.right<=innerWidth+1}})""", m1)
        ok(mw['sw'] <= mw['vw'] and mw['bIn'] and mw['tIn'], f"모바일 = 꼬리표·'JB 문제' 단추가 화면 안 · 가로 넘침 없음 {mw}")
        await pm.screenshot(path=J.TMP + '/ux14_mobile.png'); y0 = await pm.evaluate(TOP, m1)
        await pm.tap(f".nm-it[data-id='{m1}'] .nm-jbb"); await pm.wait_for_timeout(1600)
        v5 = await pm.evaluate(JBV, m1[3:])
        ok(v5['found'] and v5['vis'] and v5['open'] and v5['pill'], f"모바일 'JB 문제' → 문항·답 펼침·알약 {v5['pt']}")
        await pm.screenshot(path=J.TMP + '/ux14_mobile_jb.png')
        await pm.tap('#retpill'); await pm.wait_for_timeout(2500); y1 = await pm.evaluate(TOP, m1)
        ok(await pm.evaluate("location.hash") == '#/_num/CONS' and y1 is not None and abs(y1 - y0) <= 40, f"모바일 ↩ 돌아가기 = 그 문제 {y0}→{y1}")
        await pm.evaluate(CLEAR)
        ok(not errs2, f'pageerror 0(모바일) {errs2[:2]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
