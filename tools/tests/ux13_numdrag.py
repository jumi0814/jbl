"""UX13 내 넘버링 — 문제 끌어서 순서 바꾸기 · 편집 도구 막대 더 작게(10-11 사용자: '문제별 순서 바꿀 때 메뉴 눌러서 위로 옮기기 누르지 않아도 되게끔, 각 문제 번호 앞에 커서 올리면 내가 문제 직접 드래그해서 옮길 수 있게끔 해줘! 더불어 편집창 툴바 크기는 더 줄여주고!!')
- 손잡이: 번호 앞(왼쪽)에 숨어 있다가 문제에 마우스를 올리면 보임 · cursor grab · 번호 칸을 밀지 않음
- 끌기: 셋째 문제를 첫째 위로 → 순서 바뀜 · 놓일 자리 선 · 번호 1·2·3 다시 · 새로고침 뒤 그대로 · 알림 '되돌리기' = 처음 순서
- 같은 저장: 새 저장 키 없음(num.i.<과목>.<id>의 o만) · ⋯ 메뉴 '아래로 옮기기' 두 번으로 되돌리면 o가 처음과 똑같음(같은 한 칸씩 바꾸기)
- 막기·안내: 섞은 순서 = 막음(메뉴와 같은 안내) · 강의 순서 정렬 = 같은 강의 안에서만(다른 강의 쪽 = 안내·그대로) · 다른 정렬(출제 연도) = '사용자 지정 순서'로 바꿔 그 문제 바로 위에 · Esc = 취소
- 자동 스크롤: 화면 아래 끝 근처에서 잡고 있으면 내려감 · 편집 중 칸·글 선택은 그대로(손잡이를 눌렀다 떼도 편집 계속 · 칸 안에서 끌면 글 선택만)
- 손가락: 길게 누른 뒤 끌기 = 옮김 · 그냥 쓸기 = 안 옮김 · 넘버링 복습 화면엔 손잡이 없음
- 도구 막대: 단추 높이 ≤ 22px · 글자 ≤ 12px · 기능 그대로(굵게·밑줄·글자색·⋯·✓) · pageerror 0 · 스크린샷 work/_tmp/ux13_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, time
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
SJ = 'UZDRAG'
ORD = "[...document.querySelectorAll('.nm-it:not([hidden])')].map(a=>a.dataset.id)"
NOS = "[...document.querySelectorAll('.nm-it:not([hidden]) .nm-no')].map(x=>x.textContent)"
OS = """(sj=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.indexOf('jblhub.v1.num.i.'+sj+'.')===0){const r=JSON.parse(localStorage.getItem(k));o[r.id]=r.o;}}return o})"""
KEYS = "Object.keys(localStorage).filter(k=>k.indexOf('jblhub.v1.num.')===0).sort()"
CLEAR = "(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()"
SEED = """(sj=>{const ns='jblhub.v1.',t=Date.now();localStorage.setItem(ns+'num.subj',JSON.stringify([{id:sj,t:'끌기 시험'}]));
  localStorage.setItem(ns+'num.x.'+sj,JSON.stringify({v:1,ul:[{k:'UL1',t:'시험 강의 1'},{k:'UL2',t:'시험 강의 2'}],lt:{},u:t}));
  const L=[['d1','UL1','첫째 문제 — 원인 3가지를 쓰시오'],['d2','UL1','둘째 문제 — 분류를 쓰시오'],['d3','UL1','셋째 문제 — 기전을 서술하시오'],['d4','UL1','넷째 문제 — 순서를 쓰시오'],['d5','UL2','다섯째 문제 — 다른 강의 첫 문제'],['d6','UL2','여섯째 문제 — 다른 강의 둘째 문제']];
  L.forEach(([id,lec,q],i)=>localStorage.setItem(ns+'num.i.'+sj+'.'+id,JSON.stringify({id,k:'user',lec,q:'<p>'+q+'</p>',a:'<p>1. 답 하나</p><p>2. 답 둘</p>',st:i===1?'<p>스토리 한 줄</p>':'',note:'',tags:[],yrs:[],src:[{t:'user',s:sj,lab:'직접 추가'}],o:i,c:t,u:t})));})"""
HRECT = """(id=>{const a=document.querySelector('.nm-it[data-id="'+CSS.escape(id)+'"]');const r=a.querySelector('.nm-drag').getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2}})"""
ARECT = """(id=>{const r=document.querySelector('.nm-it[data-id="'+CSS.escape(id)+'"]').getBoundingClientRect();return {top:r.top,bottom:r.bottom,mid:r.top+r.height/2,left:r.left}})"""
async def to_view(pg, id_, block='center'):
    await pg.evaluate("([id,b])=>document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"]').scrollIntoView({block:b})", [id_, block]); await pg.wait_for_timeout(150)
FIT = """([a,b])=>{const A=document.querySelector('.nm-it[data-id="'+CSS.escape(a)+'"]').getBoundingClientRect(),B=document.querySelector('.nm-it[data-id="'+CSS.escape(b)+'"]').getBoundingClientRect(),s=document.querySelector('.nm-stick').getBoundingClientRect().bottom,top=Math.min(A.top,B.top),bot=Math.max(A.top+60,B.bottom);scrollBy(0,(top+bot)/2-(s+innerHeight)/2);}"""
async def drag(pg, src, dst, where='top', release=True, peek=None):
    """src 손잡이를 잡아 dst 문제 위쪽(where=top)·아래쪽(bottom)으로 끌어 놓기 — 마우스(둘 다 화면에 들어오게 먼저 스크롤)"""
    await pg.evaluate(FIT, [src, dst]); await pg.wait_for_timeout(150)
    h = await pg.evaluate(HRECT, src)
    await pg.mouse.move(h['x'], h['y']); await pg.mouse.down(); await pg.mouse.move(h['x'], h['y'] + 7, steps=2)
    t = await pg.evaluate(ARECT, dst); y = t['top'] + 8 if where == 'top' else t['bottom'] - 8
    await pg.mouse.move(h['x'] + 60, y, steps=10); await pg.wait_for_timeout(120)
    seen = await pg.evaluate("(()=>{const l=document.querySelector('#numv .nm-dline'),g=document.querySelector('#numv .nm-dghost');return {line:!!l&&!l.hidden,ly:l&&!l.hidden?l.getBoundingClientRect().top:null,ghost:!!g,dg:document.getElementById('numv').classList.contains('nm-dg'),src:!!document.querySelector('.nm-it.nm-dsrc')}})()")
    if peek: await peek()
    if release: await pg.mouse.up(); await pg.wait_for_timeout(600)
    return seen
async def undo(pg):
    await pg.wait_for_selector('#toast button.tact:has-text("되돌리기")', state='visible', timeout=6000); await pg.click('#toast button.tact:has-text("되돌리기")'); await pg.wait_for_timeout(600)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1366, 'height': 1000}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(U + '#/'); await pg.wait_for_timeout(2000)
        await pg.evaluate(CLEAR); await pg.evaluate(SEED, SJ)
        await pg.evaluate(f"location.hash='#/_num/{SJ}'"); await pg.wait_for_timeout(2500)
        o0 = await pg.evaluate(ORD); ok(o0 == ['d1', 'd2', 'd3', 'd4', 'd5', 'd6'], f"시험 과목 6문제(강의 2개) {o0}")
        # ---- 손잡이 ----
        hv = await pg.evaluate("""(()=>{const a=document.querySelector('.nm-it'),h=a.querySelector('.nm-drag'),n=a.querySelector('.nm-no'),hr=h.getBoundingClientRect(),nr=n.getBoundingClientRect(),br=a.querySelector('.nm-body').getBoundingClientRect(),qr=a.querySelector('.nm-q').getBoundingClientRect();return {n:document.querySelectorAll('.nm-it .nm-drag').length,op:getComputedStyle(h).opacity,cur:getComputedStyle(h).cursor,left:hr.right<=nr.left+1,mid:Math.abs((hr.top+hr.bottom)/2-(nr.top+nr.bottom)/2)<6,w:Math.round(hr.width),noL:Math.round(nr.left),bodyL:Math.round(br.left),qL:Math.round(qr.left)}})()""")
        ok(hv['n'] == 6 and hv['op'] == '0' and hv['cur'] == 'grab' and hv['left'] and hv['mid'], f"손잡이 = 문제마다 번호 바로 앞(왼쪽)·번호 줄 가운데 · 평소 숨김 · cursor grab {hv}")
        ok(abs(hv['bodyL'] - hv['qL']) <= 2, f"번호 칸·답안 칸 정렬 그대로(답안 칸 왼쪽 = 문제 글 왼쪽) {hv['bodyL']}·{hv['qL']}")
        nr = await pg.evaluate("(()=>{const r=document.querySelector('.nm-it .nm-no').getBoundingClientRect();return {x:r.left+6,y:r.top+r.height/2}})()")
        await pg.mouse.move(nr['x'], nr['y']); await pg.wait_for_timeout(250)
        op1 = await pg.evaluate("getComputedStyle(document.querySelector('.nm-it .nm-drag')).opacity")
        h1 = await pg.evaluate(HRECT, 'd1'); await pg.mouse.move(h1['x'], h1['y']); await pg.wait_for_timeout(250)
        op2 = await pg.evaluate("getComputedStyle(document.querySelector('.nm-it .nm-drag')).opacity")
        ok(op1 == '1' and op2 == '1', f"번호(앞)에 마우스를 올리면 손잡이가 보임 {op1}·{op2}")
        await pg.mouse.move(700, 120); await pg.wait_for_timeout(100)
        # ---- 셋째를 첫째 위로 ----
        k0 = await pg.evaluate(KEYS); s0 = await pg.evaluate(OS, SJ)
        await pg.evaluate("(()=>{window.__nw={};const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(String(k).indexOf('jblhub.v1.num.')===0)window.__nw[k]=(window.__nw[k]||0)+1;return o.call(this,k,v);};})()")
        shot = J.TMP + '/ux13_drag.png'
        seen = await drag(pg, 'd3', 'd1', 'top', peek=lambda: pg.screenshot(path=shot))
        o1 = await pg.evaluate(ORD); n1 = await pg.evaluate(NOS); s1 = await pg.evaluate(OS, SJ)
        ok(seen['line'] and seen['ghost'] and seen['dg'] and seen['src'], f"끄는 동안 = 놓일 자리 선·끄는 문제 표시 {seen}")
        ok(o1 == ['d3', 'd1', 'd2', 'd4', 'd5', 'd6'] and n1[:4] == ['1.', '2.', '3.', '4.'], f"셋째를 첫째 위로 끌기 → 순서 {o1} · 번호 {n1[:4]}")
        ok(s1['d3'] < s1['d1'] < s1['d2'] < s1['d4'], f"저장 순서(o) {s1}")
        nw = await pg.evaluate("window.__nw")
        ok(set(nw) <= {f'jblhub.v1.num.i.{SJ}.d1', f'jblhub.v1.num.i.{SJ}.d2', f'jblhub.v1.num.i.{SJ}.d3', 'jblhub.v1.num.cfg', f'jblhub.v1.num.pos.{SJ}'} and all(f'jblhub.v1.num.i.{SJ}.{x}' in nw for x in ('d1', 'd2', 'd3')), f"같은 저장 = 바뀐 문제 키(num.i.{SJ}.d1~d3)만 · 새 키 없음 {sorted(nw)}")
        ok(set(await pg.evaluate(KEYS)) - set(k0) <= {f'jblhub.v1.num.pos.{SJ}'}, "저장 키 종류 그대로(새 저장 키 0)")
        ok(await pg.evaluate("document.body.innerText.includes('순서를 옮겼어요')"), "알림 '순서를 옮겼어요' + 되돌리기")
        await pg.reload(); await pg.wait_for_timeout(2500)
        ok(await pg.evaluate(ORD) == o1, "새로고침 뒤에도 옮긴 순서 그대로")
        # ⋯ 메뉴 '아래로 옮기기' 두 번 = 처음 o 그대로(같은 한 칸씩 바꾸기)
        for _ in range(2):
            await pg.locator('.nm-it[data-id=d3] [data-act=more]').click(); await pg.click('.nm-menu [data-mi=down]'); await pg.wait_for_timeout(450)
        ok(await pg.evaluate(ORD) == o0 and await pg.evaluate(OS, SJ) == s0, f"⋯ 메뉴 '아래로 옮기기' ×2 = 처음 순서·처음 o 그대로(끌기와 같은 저장) {await pg.evaluate(OS, SJ)}")
        # 아래로 끌기(둘째를 넷째 아래로) → 알림 되돌리기
        await drag(pg, 'd2', 'd4', 'bottom')
        o2 = await pg.evaluate(ORD)
        ok(o2[:4] == ['d1', 'd3', 'd4', 'd2'], f"둘째를 넷째 아래로 끌기 → {o2[:4]}")
        await undo(pg)
        ok(await pg.evaluate(ORD) == o0 and await pg.evaluate(OS, SJ) == s0, "알림 '되돌리기' = 처음 순서·o")
        # Esc = 취소
        await drag(pg, 'd4', 'd1', 'top', release=False); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100); await pg.mouse.up(); await pg.wait_for_timeout(400)
        ok(await pg.evaluate(ORD) == o0 and not await pg.evaluate("!!document.querySelector('#numv .nm-dline')"), "끄는 중 Esc = 취소(순서 그대로·선 사라짐)")
        # 제자리에 놓기 = 바뀜 없음
        k1 = await pg.evaluate(OS, SJ); await drag(pg, 'd2', 'd2', 'top')
        ok(await pg.evaluate(ORD) == o0 and await pg.evaluate(OS, SJ) == k1, "제자리에 놓기 = 아무것도 안 바뀜")
        # 강의 순서 정렬 = 같은 강의 안에서만
        await to_view(pg, 'd5'); seen = await drag(pg, 'd5', 'd2', 'top')
        ok(await pg.evaluate(ORD) == o0 and not seen['line'] and await pg.evaluate("document.body.innerText.includes('같은 강의 안에서만')"), f"다른 강의 쪽으로 끌기 = 그대로 · 안내 {seen}")
        await to_view(pg, 'd6'); await drag(pg, 'd6', 'd5', 'top')
        ok(await pg.evaluate(ORD) == ['d1', 'd2', 'd3', 'd4', 'd6', 'd5'], "같은 강의 안 = 옮김(둘째 강의)")
        await drag(pg, 'd5', 'd6', 'top'); await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(200)
        # 다른 정렬(출제 연도) → '사용자 지정 순서'로 바꿔 그 문제 바로 위에
        await pg.click('[data-act=flt].nm-tbtn'); await pg.select_option('[data-cf=sort]', 'yr'); await pg.wait_for_timeout(500); await pg.keyboard.press('Escape')
        await drag(pg, 'd4', 'd2', 'top')
        o3 = await pg.evaluate(ORD); srt = await pg.evaluate("JBLNUM._S.cfg.sort")
        ok(srt == 'own' and o3.index('d4') == o3.index('d2') - 1 and await pg.evaluate("document.body.innerText.includes('사용자 지정 순서')"), f"정렬 '출제 연도'에서 끌기 = '사용자 지정 순서'로 바꿔 놓은 문제 바로 위에 {srt} {o3}")
        await undo(pg)
        ok(await pg.evaluate("JBLNUM._S.cfg.sort") == 'yr' and await pg.evaluate(OS, SJ) == s0, "되돌리기 = 정렬·순서 처음대로")
        await pg.click('[data-act=flt].nm-tbtn'); await pg.select_option('[data-cf=sort]', 'lec'); await pg.wait_for_timeout(500); await pg.keyboard.press('Escape')
        # 섞은 순서 = 막음
        await pg.click('[data-mode=all]'); await pg.wait_for_timeout(500); await pg.click('[data-act=shuf]'); await pg.wait_for_timeout(500)
        sh = await pg.evaluate(ORD); await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(200)
        await drag(pg, sh[2], sh[0], 'top')
        ok(await pg.evaluate(ORD) == sh and await pg.evaluate(OS, SJ) == s0 and await pg.evaluate("document.body.innerText.includes('섞은 순서에서는 옮길 수 없어요')"), "섞은 순서에서 끌기 = 막음(메뉴와 같은 안내 · 저장 그대로)")
        await pg.click('.nm-shf [data-act=unshuf]'); await pg.wait_for_timeout(400); await pg.click('[data-mode=grp]'); await pg.wait_for_timeout(500)
        # 검색 중 = 보이는 문제끼리(메뉴와 같음)
        await pg.fill('[data-cf=q]', '쓰시오'); await pg.wait_for_timeout(450)
        vq = await pg.evaluate(ORD); await drag(pg, vq[-1], vq[0], 'top')
        vq2 = await pg.evaluate(ORD)
        ok(vq == ['d1', 'd2', 'd4'] and vq2 == ['d4', 'd1', 'd2'], f"검색 중 = 보이는 문제끼리 옮김 {vq} → {vq2}")
        await pg.fill('[data-cf=q]', ''); await pg.wait_for_timeout(450)
        vq3 = await pg.evaluate(ORD)
        ok(vq3[:4] == ['d4', 'd1', 'd3', 'd2'], f"검색을 풀면 숨었던 문제는 제 칸 그대로(메뉴 '위로 옮기기' 두 번과 같음) {vq3[:4]}")
        await undo(pg)
        ok(await pg.evaluate(OS, SJ) == s0, "되돌리기 = 처음 o")
        # ---- 편집 중 칸·글 선택은 그대로 ----
        await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(200)
        ord_e = await pg.evaluate(ORD)
        await pg.locator('.nm-it[data-id=d2] .nm-s .nm-c').click(); await pg.wait_for_timeout(250)
        await pg.keyboard.type(' 덧붙임')
        tb = await pg.evaluate("(()=>{const t=document.querySelector('.nm-tb'),B=[...t.querySelectorAll('button')];return {btn:B.map(b=>b.dataset.cmd||b.dataset.pal),h:Math.max(...B.map(b=>b.getBoundingClientRect().height)),fs:Math.max(...B.map(b=>parseFloat(getComputedStyle(b).fontSize))),bar:Math.round(t.getBoundingClientRect().height),w:Math.round(t.getBoundingClientRect().width)}})()")
        ok(tb['btn'] == ['bold', 'underline', 'insertUnorderedList', 'insertOrderedList', 'fc', 'more', 'done'] and tb['h'] <= 22 and tb['fs'] <= 12 and tb['bar'] <= 26, f"편집 도구 막대 더 작게 — 단추 높이 {tb['h']}px · 글자 {tb['fs']}px · 막대 {tb['bar']}×{tb['w']} · 기능 그대로 {tb['btn']}")
        h3 = await pg.evaluate(HRECT, 'd3'); await pg.mouse.move(h3['x'], h3['y']); await pg.wait_for_timeout(200)
        await pg.screenshot(path=J.TMP + '/ux13_toolbar.png')
        await pg.mouse.down(); await pg.mouse.up(); await pg.wait_for_timeout(400)
        ed = await pg.evaluate("(()=>{const S=JBLNUM._S;return {ed:!!S.ed&&S.ed.it.id,ce:!!document.querySelector('.nm-it[data-id=d2] .nm-s .nm-c[contenteditable=true]'),tb:document.querySelectorAll('.nm-tb').length}})()")
        ok(ed['ed'] == 'd2' and ed['ce'] and ed['tb'] == 1 and await pg.evaluate(ORD) == ord_e, f"편집 중에 다른 문제 손잡이를 눌렀다 떼기 = 편집 그대로·순서 그대로 {ed}")
        await pg.click('.nm-tb [data-cmd=bold]'); await pg.keyboard.type('굵게'); await pg.wait_for_timeout(100)
        ok(await pg.evaluate("!!document.querySelector('.nm-it[data-id=d2] .nm-s .nm-c b, .nm-it[data-id=d2] .nm-s .nm-c [style*=\"font-weight\"]')"), "작아진 도구 막대 굵게 단추 동작")
        c = await pg.evaluate("(()=>{const r=document.querySelector('.nm-it[data-id=d2] .nm-s .nm-c').getBoundingClientRect();return {x:r.left+4,y:r.top+10,x2:r.left+80}})()")
        await pg.mouse.move(c['x'], c['y']); await pg.mouse.down(); await pg.mouse.move(c['x2'], c['y'], steps=5); await pg.mouse.move(c['x2'], c['y'] + 300, steps=5); await pg.mouse.up(); await pg.wait_for_timeout(300)
        sel = await pg.evaluate("String(getSelection()).length")
        ok(sel > 0 and await pg.evaluate(ORD) == ord_e and not await pg.evaluate("!!document.querySelector('#numv .nm-dline')") and await pg.evaluate("!!JBLNUM._S.ed"), f"편집 칸 안에서 끌기 = 글 선택만(순서 그대로·끌기 없음) 선택 {sel}자")
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(900)
        ok('덧붙임' in (await pg.evaluate(f"localStorage.getItem('jblhub.v1.num.i.{SJ}.d2')") or ''), "편집한 글 저장 그대로")
        # 읽기 화면 글 선택(문제 글을 끌어 선택) = 끌기 아님
        q = await pg.evaluate("(()=>{const r=document.querySelector('.nm-it[data-id=d1] .nm-q .nm-c').getBoundingClientRect();return {x:r.left+2,y:r.top+r.height/2}})()")
        await pg.mouse.move(q['x'], q['y']); await pg.mouse.down(); await pg.mouse.move(q['x'] + 120, q['y'] + 90, steps=6); await pg.mouse.up(); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("String(getSelection()).length") > 0 and await pg.evaluate(ORD) == ord_e, "문제 글을 끌면 글 선택만(순서 그대로)")
        # ---- 넘버링 복습 = 손잡이 없음 ----
        await pg.evaluate(f"location.hash='#/_numr/{SJ}'"); await pg.wait_for_timeout(2000)
        rv = await pg.evaluate("({rv:document.getElementById('numv').classList.contains('rv'),n:document.querySelectorAll('.nm-it').length,h:document.querySelectorAll('.nm-drag').length})")
        ok(rv['rv'] and rv['n'] >= 6 and rv['h'] == 0, f"넘버링 복습 화면엔 끌기 손잡이 없음 {rv}")
        # ---- 자동 스크롤(CONS 실제 문제 · 긴 문서) ----
        await pg.evaluate(f"location.hash='#/_num/CONS'"); await pg.wait_for_timeout(3000)
        await pg.click('.nm-side [data-act=imp]'); await pg.wait_for_timeout(700); await pg.click('[data-ib=flt]'); await pg.wait_for_timeout(400); await pg.click('[data-cf2=ok]'); await pg.wait_for_timeout(1200); await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(500)
        oc = await pg.evaluate(ORD); ok(len(oc) > 50, f"CONS {len(oc)}문제")
        await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(200)
        hc = await pg.evaluate(HRECT, oc[0]); y0 = await pg.evaluate("scrollY")
        await pg.mouse.move(hc['x'], hc['y']); await pg.mouse.down(); await pg.mouse.move(hc['x'], hc['y'] + 10, steps=2); await pg.mouse.move(hc['x'] + 40, 985, steps=8); await pg.wait_for_timeout(900)
        y1 = await pg.evaluate("scrollY"); ln = await pg.evaluate("!!document.querySelector('#numv .nm-dline')&&!document.querySelector('#numv .nm-dline').hidden")
        await pg.mouse.move(hc['x'] + 40, 500, steps=4); await pg.wait_for_timeout(150); y2 = await pg.evaluate("scrollY"); await pg.wait_for_timeout(300)
        ok(y1 > y0 + 300 and ln and abs(await pg.evaluate("scrollY") - y2) < 2, f"화면 아래 끝 근처에서 잡고 있으면 자동 스크롤(멈추면 그침) {y0}→{y1}")
        await pg.mouse.up(); await pg.wait_for_timeout(1500)
        oc2 = await pg.evaluate(ORD); L1 = await pg.evaluate("(id=>{const S=JBLNUM._S,l=S.by.get(id).lec;return [...document.querySelectorAll('.nm-it')].map(a=>a.dataset.id).filter(x=>S.by.get(x).lec===l)})", oc[0])
        ok(oc2 != oc and sorted(oc2) == sorted(oc) and oc2[0] != oc[0] and oc[0] in L1 and L1[0] != oc[0], f"멀리 끌어 놓기 = 같은 강의 안 아래쪽으로 옮김(첫 문제 → {L1.index(oc[0]) + 1}번째)")
        rb = await pg.evaluate("(id=>{const a=document.querySelector('.nm-it[data-id=\"'+CSS.escape(id)+'\"]').getBoundingClientRect();return {t:a.top,b:a.bottom,vh:innerHeight}})", oc[0])
        ok(rb['b'] > 60 and rb['t'] < rb['vh'], f"놓은 뒤 옮긴 문제가 화면 안(놓은 자리 근처) {rb}")
        await pg.evaluate(CLEAR)
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await ctx.close()
        # ---- 손가락(모바일 폭 · 길게 누른 뒤 끌기) ----
        ctx2 = await b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); pm = await ctx2.new_page(); errs2 = []
        pm.on('pageerror', lambda e: errs2.append(str(e)[:200]))
        await pm.goto(U + '#/'); await pm.wait_for_timeout(1800); await pm.evaluate(CLEAR); await pm.evaluate(SEED, SJ)
        await pm.evaluate(f"location.hash='#/_num/{SJ}'"); await pm.wait_for_timeout(2500)
        cdp = await ctx2.new_cdp_session(pm)
        async def touch(pts, kind): await cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y} for x, y in pts]})
        mw = await pm.evaluate("(()=>{const h=document.querySelector('.nm-it .nm-drag').getBoundingClientRect();return {w:Math.round(h.width),x:Math.round(h.left),sw:document.documentElement.scrollWidth,vw:innerWidth}})()")
        ok(mw['w'] >= 12 and mw['x'] >= 0 and mw['sw'] <= mw['vw'], f"모바일 폭 = 손잡이 {mw['w']}px · 가로 넘침 없음 {mw}")
        await to_view(pm, 'd1', 'start'); await pm.evaluate("scrollBy(0,-120)"); await pm.wait_for_timeout(200)
        h = await pm.evaluate(HRECT, 'd2'); t = await pm.evaluate(ARECT, 'd1')
        await touch([(h['x'], h['y'])], 'touchStart'); await touch([(h['x'], h['y'] - 60)], 'touchMove'); await touch([], 'touchEnd'); await pm.wait_for_timeout(500)
        ok(await pm.evaluate(ORD) == o0, "손가락으로 그냥 쓸기 = 안 옮김")
        await touch([(h['x'], h['y'])], 'touchStart'); await pm.wait_for_timeout(450)
        for i in range(1, 7): await touch([(h['x'] + 4, h['y'] + (t['top'] + 8 - h['y']) * i / 6)], 'touchMove'); await pm.wait_for_timeout(30)
        lm = await pm.evaluate("!!document.querySelector('#numv .nm-dline')&&!document.querySelector('#numv .nm-dline').hidden")
        await touch([], 'touchEnd'); await pm.wait_for_timeout(700)
        om = await pm.evaluate(ORD)
        ok(lm and om[:2] == ['d2', 'd1'], f"손가락 길게 누른 뒤 끌기 = 옮김 {om[:3]}")
        ok(not await pm.evaluate("!!JBLNUM._S.ed"), "손가락 끌기 뒤 편집기가 열리지 않음")
        await pm.evaluate(CLEAR)
        ok(not errs2, f'pageerror 0(모바일) {errs2[:2]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
