"""UX18 넘버링 가져오기 ← 예상문제(S3 3 — guide/handoff/S3_BRIEF.md)
- 불러오기 목록 예상문제 행: 짧은 태그('우선 상/중/하'·유형·'기출 25·24'·그림/그림빵) · '근거'는 눌러서 펼침(다시 누르면 접힘) · 태그 글자가 짧음(문제보다 길지 않게)
- 필터 '우선 상만'·'우선 상+중'(예상문제만) · 정렬 '우선순위 높은 순' · 보관(x=1)된 예상문제는 목록에 없음
- 가져오면 출처 메타(it.pm — 우선순위·유형·근거·관련 기출)를 사용자 글과 따로 저장 · 문제 머리에 작은 우선순위 표 · 넘버링 필터 '우선순위'·정렬 '우선순위 높은 순'
- 그림: 예상 f= 쪽 그림 = 강의 이미지 자리표(data-lecimg)로 넣고 화면에서 실제 그림으로 · 그림빵 = 번호 가림 상자를 그려 넣은 그림(data-gbm) · JB 그림 = 기존 data-jbfig 그대로 · 저장 글에 그림 글자(dataURI) 없음
- 다시 가져오기: 사용자가 고친 문제·답안·스토리와 복습 기록은 그대로, 메타만 새로(확인 창 '우선순위·근거만 새로 n') · 사이트 값이 바뀌면 화면 태그는 지금 팩 값
- pageerror 0 · 스크린샷 work/_tmp/s3/ux18_*.png(없으면 work/_tmp/)"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import json
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
OUT = _os.path.join(J.TMP, 's3') if _os.path.isdir(_os.path.join(J.TMP, 's3')) else J.TMP
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CLEAR = "(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()"
ROWS = """(()=>[...document.querySelectorAll('.nm-ov [data-ix]')].map(r=>({id:r.dataset.ix,pred:!!r.querySelector('.nm-chip.k-pred'),pr:((r.querySelector('.nm-chip.pr')||{}).textContent||'').replace('우선 ',''),tags:[...r.querySelectorAll('.nm-chip.pr,.nm-chip.yr,.nm-chip.fig')].map(c=>c.textContent).join(' '),q:(r.querySelector('.t')||{}).textContent||'',why:!!r.querySelector('[data-iwhy]')})))()"""
def pick(pg):
    """우선순위·그림빵·f 그림이 다 있는 과목·강의"""
    return pg.evaluate("""(()=>{for(const s of ['ANAT','IMPL','OMS1','CONS','GERI','ESTH','PHARM']){const P=JBLNUM._H().PACKS[s];if(!P)continue;
      for(const L of P.lect){const A=L.pred.map(i=>P.preds[i]);if(A.some(x=>x.m)&&A.some(x=>x.pr)&&A.some(x=>x.why))return {s,k:L.k,n:A.length,gb:A.filter(x=>x.m).length,f:A.filter(x=>x.f).length,x:(L.parch||[]).length};}}return null})()""")
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1366, 'height': 900}); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(U + '#/'); pg.wait_for_timeout(2500); pg.evaluate(CLEAR)
    pg.evaluate("location.hash='#/_num/ANAT'"); pg.wait_for_timeout(3500)
    T = pick(pg); ok(bool(T), f"고를 과목·강의 {T}"); SID, K = T['s'], T['k']
    if SID != 'ANAT': pg.evaluate(f"location.hash='#/_num/{SID}'"); pg.wait_for_timeout(3000)
    pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); pg.wait_for_timeout(800)
    pg.select_option('[data-if=ty]', ''); pg.select_option('[data-if=src]', 'pred'); pg.wait_for_timeout(400)
    R = pg.evaluate(ROWS)
    act = pg.evaluate(f"(()=>{{const P=JBLNUM._H().PACKS.{SID};return {{act:P.preds.filter(x=>!x.x).length,x:P.preds.filter(x=>x.x).map(x=>x.aid),pr:P.preds.filter(x=>!x.x&&x.pr).length,s3:P.preds.filter(x=>!x.x&&x.pr==='상').length,s2:P.preds.filter(x=>!x.x&&(x.pr==='상'||x.pr==='중')).length}}}})()")
    ok(len(R) == act['act'] and not ({r['id'] for r in R} & set(act['x'])), f"예상문제 목록 = 활성 {len(R)}/{act['act']} · 보관 {len(act['x'])}개 없음")
    ok(sum(1 for r in R if r['pr']) == act['pr'] and all(r['pr'] in ('상', '중', '하', '') for r in R), f"행 우선순위 태그 {sum(1 for r in R if r['pr'])}/{act['pr']}")
    lng = [r for r in R if len(r['tags']) > 30]
    ok(not lng, f"태그 글자 짧음(≤30자) — 넘는 행 {len(lng)} {[r['tags'] for r in lng[:2]]}")
    # 근거 펼침
    w = pg.evaluate("""(()=>{const r=[...document.querySelectorAll('.nm-ov [data-ix]')].find(x=>x.querySelector('[data-iwhy]'));const b=r.querySelector('[data-iwhy]');const h0=!r.querySelector('.nm-iwhy');b.click();const e=r.querySelector('.nm-iwhy'),t=e&&e.textContent,ae=b.getAttribute('aria-expanded');b.click();return {h0,t,ae,h2:!r.querySelector('.nm-iwhy')}})()""")
    ok(w['h0'] and w['t'] and w['t'].startswith('근거') and w['ae'] == 'true' and w['h2'], f"'근거' 기본 접힘 → 펼침 '{(w['t'] or '')[:50]}' → 접힘")
    # 우선순위 필터·정렬
    pg.select_option('[data-if=src]', ''); pg.select_option('[data-if=pr]', '상'); pg.wait_for_timeout(300); R1 = pg.evaluate(ROWS)
    ok(len(R1) == act['s3'] and all(r['pred'] and r['pr'] == '상' for r in R1), f"'우선 상만' = 예상 상 {len(R1)}/{act['s3']}(JB 기출 빠짐)")
    pg.select_option('[data-if=pr]', '상중'); pg.wait_for_timeout(300); R2 = pg.evaluate(ROWS)
    ok(len(R2) == act['s2'] and all(r['pr'] in ('상', '중') for r in R2), f"'우선 상+중' {len(R2)}/{act['s2']}")
    pg.select_option('[data-if=pr]', ''); pg.select_option('[data-if=so]', 'pr'); pg.wait_for_timeout(300); R3 = pg.evaluate(ROWS)
    V = {'상': 3, '중': 2, '하': 1, '': 0}; seq = [V[r['pr']] for r in R3]
    ok(seq == sorted(seq, reverse=True) and seq[0] == 3, f"정렬 '우선순위 높은 순' (처음 {seq[:3]} … 끝 {seq[-3:]})")
    pg.select_option('[data-if=so]', ''); pg.screenshot(path=_os.path.join(OUT, 'ux18_import.png'))
    # 강의 하나 전체 넣기
    pg.select_option('[data-if=lec]', K); pg.wait_for_timeout(300); pg.click('[data-ib=lec]'); pg.wait_for_timeout(600); pg.click('[data-cf2=ok]'); pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelectorAll('.nm-ov [data-x]').forEach(x=>x.click())"); pg.wait_for_timeout(800)
    r = pg.evaluate(f"""(()=>{{const S=JBLNUM._S,P=JBLNUM._H().PACKS.{SID},L=P.lect.find(l=>l.k==='{K}'),pr=S.items.filter(i=>/^pr:/.test(i.id)&&i.lec==='{K}');
      const raw=id=>JSON.parse(localStorage.getItem('jblhub.v1.num.i.{SID}.'+id)||'null');const want=L.pred.length;let pm=0,pmOK=0,tag=0;
      pr.forEach(i=>{{const x=P.preds.find(z=>'pr:'+z.aid===i.id),r=raw(i.id);if(r&&r.pm)pm++;if(x&&r&&r.pm&&(r.pm.pr||'')===(x.pr||'')&&(r.pm.why||'')===(x.why||''))pmOK++;const a=document.querySelector('.nm-it[data-id="'+CSS.escape(i.id)+'"]');if(a&&(!x.pr||(a.querySelector('.nm-prt')||{{}}).textContent===x.pr))tag++;}});
      const big=pr.filter(i=>/data:image/.test((raw(i.id)||{{}}).q||'')).length;return {{n:pr.length,want,pm,pmOK,tag,big}}}})()""")
    ok(r['n'] >= r['want'] - 2 and r['pm'] == r['n'] and r['pmOK'] == r['n'], f"넣은 예상문제 {r['n']}(강의 {r['want']}) · 출처 메타 저장 {r['pm']} · 팩 값과 같음 {r['pmOK']}")
    ok(r['tag'] == r['n'], f"문제 머리 작은 우선순위 표 {r['tag']}/{r['n']}")
    ok(r['big'] == 0, "저장 글에 그림 글자(dataURI) 없음 — 자리표만")
    # 그림 · 그림빵
    pg.wait_for_timeout(2500)
    g = pg.evaluate(f"""(async()=>{{const S=JBLNUM._S,P=JBLNUM._H().PACKS.{SID};const fi=S.items.find(i=>{{const x=P.preds.find(z=>'pr:'+z.aid===i.id);return x&&x.f&&!x.m;}}),gi=S.items.find(i=>{{const x=P.preds.find(z=>'pr:'+z.aid===i.id);return x&&x.m;}});
      const one=async it=>{{if(!it)return null;const a=document.querySelector('.nm-it[data-id="'+CSS.escape(it.id)+'"]');a.scrollIntoView({{block:'center'}});await new Promise(r=>setTimeout(r,2500));const im=a.querySelector('.nm-q img[data-lecimg]');if(!im)return {{img:0}};try{{await im.decode()}}catch(e){{}};return {{img:1,gbm:im.getAttribute('data-gbm')||'',src:(im.getAttribute('src')||'').slice(0,22),w:im.naturalWidth,key:im.getAttribute('data-lecimg')}};}};
      return {{f:await one(fi),gb:await one(gi)}}}})()""")
    ok(g['gb'] and g['gb']['img'] and g['gb']['gbm'] and g['gb']['src'].startswith('data:image/jpeg') and g['gb']['w'] > 300, f"그림빵 = 번호 가림 상자 그림(문제 쪽) {g['gb']}")
    if g['f']: ok(g['f']['img'] and not g['f']['gbm'] and g['f']['src'].startswith('data:image') and g['f']['w'] > 300, f"예상 f= 쪽 그림 = 실제 그림으로 {g['f']}")
    pg.screenshot(path=_os.path.join(OUT, 'ux18_gb.png'))
    gid = pg.evaluate(f"(()=>{{const S=JBLNUM._S,P=JBLNUM._H().PACKS.{SID};const i=S.items.find(i=>{{const x=P.preds.find(z=>'pr:'+z.aid===i.id);return x&&x.m;}});return i.id}})()")
    # JB 그림(기존 꼴)도 같이: 같은 강의 JB 기출 넣기 → data-jbfig 그림
    pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); pg.wait_for_timeout(800)
    KJ = pg.evaluate(f"(()=>{{const P=JBLNUM._H().PACKS.{SID};const L=P.lect.find(L=>L.jb.some(i=>/<img class=\"fig\"/.test(P.cards[i]||'')));return L?L.k:'{K}'}})()")
    pg.select_option('[data-if=ty]', ''); pg.select_option('[data-if=src]', 'jb'); pg.select_option('[data-if=lec]', KJ); pg.wait_for_timeout(300)
    if pg.evaluate("document.querySelectorAll('.nm-ov [data-ix]').length"):
        pg.click('[data-ib=lec]'); pg.wait_for_timeout(800)
        if pg.evaluate("(()=>{const b=document.querySelector('[data-cf2=ok]');return !!b&&!b.disabled})()"): pg.click('[data-cf2=ok]'); pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelectorAll('.nm-ov [data-x]').forEach(x=>x.click())"); pg.wait_for_timeout(800)
    jf = pg.evaluate("(()=>{const im=[...document.querySelectorAll('.nm-it .nm-q img[data-jbfig]')];return {n:im.length,src:im.filter(i=>/^data:image/.test(i.getAttribute('src')||'')).length}})()")
    ok(jf['n'] == 0 or jf['src'] == jf['n'], f"JB 그림(data-jbfig) 그대로 {jf}")
    # 넘버링 필터·정렬 '우선순위'
    pg.evaluate("document.querySelector('.nm-tbtn[data-act=flt]').click()"); pg.wait_for_timeout(300)
    has = pg.evaluate("!!document.querySelector('.nm-fpan select[data-cf=pr]') && !!document.querySelector('.nm-fpan select[data-cf=sort] option[value=pr]')")
    ok(has, "넘버링 필터 패널 '우선순위' · 정렬 '우선순위 높은 순'")
    if has:
        pg.select_option('.nm-fpan select[data-cf=pr]', '상'); pg.wait_for_timeout(500)
        v = pg.evaluate(f"(()=>{{const S=JBLNUM._S,P=JBLNUM._H().PACKS.{SID};const A=[...document.querySelectorAll('.nm-it:not([hidden])')];return {{n:A.length,ok:A.every(a=>{{const x=P.preds.find(z=>'pr:'+z.aid===a.dataset.id);return x&&x.pr==='상';}}),chip:[...document.querySelectorAll('.nm-fchip')].map(c=>c.textContent).join(' ')}}}})()")
        ok(v['n'] > 0 and v['ok'] and '우선순위' in v['chip'], f"넘버링 '우선순위 상' = 예상 상만 {v['n']} · 조건 칩 '{v['chip']}'")
        pg.evaluate("document.querySelector('.nm-fchip[data-fx=pr]').click()"); pg.wait_for_timeout(400)
    pg.evaluate("document.querySelector('.nm-tbtn[data-act=flt]').click()") if pg.evaluate("!!document.querySelector('.nm-fpan:not([hidden])')") else None
    # ---- 사용자 글 보호 · 메타만 새로 ----
    pg.evaluate(f"""(id=>{{const S=JBLNUM._S,it=S.by.get(id);const k='jblhub.v1.num.i.{SID}.'+id,r=JSON.parse(localStorage.getItem(k));r.st='<p>내 스토리 — 바꾸지 마</p>';r.q0=r.q;r.q=r.q+'<p>(내가 고친 문제)</p>';r.a0=r.a;r.a='<p>내가 고친 답</p>';r.pm=Object.assign({{}},r.pm,{{pr:'하',why:'옛 근거'}});r.u=Date.now();localStorage.setItem(k,JSON.stringify(r));
      localStorage.setItem('jblhub.v1.num.r.{SID}.'+id,JSON.stringify({{m:2,d:'2026-10-15',h:[{{m:2,t:Date.now()}}],w:[]}}));}})""", gid)
    pg.reload(); pg.wait_for_timeout(3500)
    live = pg.evaluate(f"""(id=>{{const P=JBLNUM._H().PACKS.{SID},x=P.preds.find(z=>'pr:'+z.aid===id),a=document.querySelector('.nm-it[data-id="'+CSS.escape(id)+'"]');return {{want:x.pr,tag:a&&(a.querySelector('.nm-prt')||{{}}).textContent}}}})""", gid)
    ok(live['tag'] == live['want'], f"사이트 값이 바뀌면(저장 메타 '하') 화면 태그는 지금 팩 값 {live}")
    pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); pg.wait_for_timeout(800)
    pg.select_option('[data-if=ty]', ''); pg.select_option('[data-if=src]', 'pred'); pg.select_option('[data-if=lec]', K); pg.wait_for_timeout(300)
    pg.click('[data-ib=lec]'); pg.wait_for_timeout(700)
    ct = pg.evaluate("(()=>{const b=document.querySelector('[data-cf2=ok]');const o=b&&b.closest('.nm-dlg');return o?(o.querySelector('.bd')||{}).textContent||'':''})()")
    ok('우선순위·근거만 새로' in ct, f"다시 가져오기 확인 창 '{ct[:120]}'")
    pg.click('[data-cf2=ok]'); pg.wait_for_timeout(1500); pg.evaluate("document.querySelectorAll('.nm-ov [data-x]').forEach(x=>x.click())"); pg.wait_for_timeout(600)
    r2 = pg.evaluate(f"""(id=>{{const P=JBLNUM._H().PACKS.{SID},x=P.preds.find(z=>'pr:'+z.aid===id),r=JSON.parse(localStorage.getItem('jblhub.v1.num.i.{SID}.'+id)),rv=JSON.parse(localStorage.getItem('jblhub.v1.num.r.{SID}.'+id)||'null');
      return {{st:r.st,q:r.q.includes('(내가 고친 문제)'),a:r.a,pr:r.pm&&r.pm.pr,want:x.pr,why:r.pm&&r.pm.why===(x.why||undefined),rv:rv&&rv.m}}}})""", gid)
    ok(r2['st'] == '<p>내 스토리 — 바꾸지 마</p>' and r2['q'] and r2['a'] == '<p>내가 고친 답</p>' and r2['rv'] == 2, f"다시 가져오기 = 문제·답안·스토리·복습 기록 그대로 {r2}")
    ok(r2['pr'] == r2['want'] and r2['why'], f"메타만 새로(우선순위 '하' → '{r2['pr']}')")
    ok(not errs, f"pageerror 0 {errs[:3]}")
    pg.evaluate(CLEAR); b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
