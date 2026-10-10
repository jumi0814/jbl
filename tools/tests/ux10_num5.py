"""UX10 내 넘버링 5차(10-10) — 흰 미니 도구 막대 · 사이드바(과목·강의가 맨 위 · 강의 목록 접기 · 접은 아이콘 줄에서 과목 바꾸기) · 마지막 위치 기억(과목마다 · 거르기 바꿔도 근처 · 맨 위로) · 전체 목록 섞기(화면에서만 — 저장 순서 그대로) · 사이드바 백업 · '내 강의목록' 이름.
- 도구 막대: 흰 반투명 · 기본 단추 = 굵게·밑줄·글자색·⋯·✓ · 형광펜·번호·글머리표·표·그림은 ⋯ 안
- 사이드바: 과목 칸이 '새 문제'보다 위 · 강의 바로 가기 접기(기억) · 접으면 과목 칩 → 과목 메뉴 → 바꾸기
- 위치: 스크롤 → 새로고침 = 그 문제부터(알림 '맨 위로') · 과목 바꿨다 돌아와도 · 상태 거르기를 바꿔도 보던 자리 근처 · 맨 위로 단추
- 섞기: 전체 목록에서만 · 순서 바뀜·번호 1…n · 다시 섞기 = 또 다름 · 원래대로 = 처음 순서 · 거르기와 함께 · 저장된 o 그대로 · 강의별로 가면 꺼짐 · 섞은 채 '위로 옮기기' 막음
- 사이드바 [백업] = 백업 창 · 허브 메뉴 '내 강의목록' · pageerror 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
ORD = "[...document.querySelectorAll('.nm-it:not([hidden])')].map(a=>a.dataset.id)"
OS = """(()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.indexOf('jblhub.v1.num.i.CONS.')===0){const r=JSON.parse(localStorage.getItem(k));o[r.id]=r.o;}}return o})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1366, 'height': 900}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(U + '#/'); await pg.wait_for_timeout(2500)
        nv = await pg.evaluate("document.querySelector('[data-nv=bm] .el')?.textContent")
        ok(nv == '내 강의목록', f"허브 메뉴 이름 '내 강의목록' ({nv})")
        await pg.evaluate("location.hash='#/_bm'"); await pg.wait_for_timeout(1200)
        ok(await pg.evaluate("document.title.startsWith('내 강의목록') && document.querySelector('#crumb').textContent.includes('내 강의목록')"), "내 강의목록 화면 제목·위치 표시")
        await pg.evaluate("(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()")
        await pg.evaluate("location.hash='#/_num/CONS'"); await pg.wait_for_timeout(3500)
        await pg.click('.nm-side [data-act=imp]'); await pg.wait_for_timeout(700); await pg.click('[data-ib=flt]'); await pg.wait_for_timeout(400); await pg.click('[data-cf2=ok]'); await pg.wait_for_timeout(1200); await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(500)
        n = await pg.evaluate("document.querySelectorAll('.nm-it').length"); ok(n > 50, f"CONS {n}문제")
        # ---- 도구 막대 ----
        await pg.evaluate("document.querySelectorAll('.nm-it')[2].querySelector('.nm-s .nm-c').scrollIntoView({block:'center'})")
        await pg.locator('.nm-it').nth(2).locator('.nm-s .nm-c').click(); await pg.wait_for_timeout(250)
        tb = await pg.evaluate("(()=>{const t=document.querySelector('.nm-tb'),cs=getComputedStyle(t);return {btn:[...t.querySelectorAll('button')].map(b=>b.dataset.cmd||b.dataset.pal),bg:cs.backgroundColor,h:Math.round(t.getBoundingClientRect().height)}})()")
        ok(tb['btn'] == ['bold', 'underline', 'fc', 'more', 'done'] and 'rgba(255, 255, 255' in tb['bg'] and tb['h'] <= 32, f"흰 반투명 미니 막대 — 굵게·밑줄·글자색·⋯·✓ {tb}")
        await pg.click('.nm-tb [data-pal=more]'); await pg.wait_for_timeout(150)
        mo = await pg.evaluate("[...document.querySelectorAll('.nm-pal [data-hl],.nm-pal [data-cmd],.nm-pal [data-tb]')].map(b=>b.dataset.hl!=null?'hl':(b.dataset.cmd||b.dataset.tb))")
        ok('hl' in mo and 'insertOrderedList' in mo and 'insertUnorderedList' in mo and 'ins2' in mo and 'img' in mo and 'undo' in mo, f"⋯ = 형광펜·번호·글머리표·표·그림·실행 취소 {sorted(set(mo))}")
        await pg.click('.nm-pal [data-hl="#FFFF00"]'); await pg.keyboard.type('형광 글'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
        # ---- 사이드바 ----
        sd = await pg.evaluate("(()=>{const S=document.querySelector('.nm-side'),a=S.querySelector('.nm-sjd'),b=S.querySelector('[data-act=new]'),c=S.querySelector('.nm-ljl'),g=S.querySelector('[data-act=aiout]'),F=(x,y)=>!!(x.compareDocumentPosition(y)&Node.DOCUMENT_POSITION_FOLLOWING);return {sjFirst:F(a,b),ljFirst:F(c,b),gptMid:F(a,g)&&F(c,g)&&F(g,b),note:document.querySelectorAll('.nm-note').length}})()")
        ok(sd['sjFirst'] and sd['ljFirst'] and sd['gptMid'] and sd['note'] == 0, f"사이드바 = 과목·강의 → ChatGPT·인쇄 → 문제(맨 아래) · 문제 아래 '참고:' 줄 없음 {sd}")
        await pg.click('.nm-side [data-act=imp]'); await pg.wait_for_timeout(600)
        await pg.click('.nm-irow >> nth=0 >> .t'); await pg.wait_for_timeout(200)
        ia = await pg.evaluate("(()=>{const a=document.querySelector('.nm-ians');return a?{t:a.textContent.slice(0,40),open:document.querySelector('.nm-irow').classList.contains('open')}:null})()")
        await pg.click('.nm-irow >> nth=0 >> .nm-ivb'); await pg.wait_for_timeout(150)
        ok(ia and len(ia['t']) > 4 and ia['open'] and not await pg.evaluate("!!document.querySelector('.nm-ians')"), f"불러오기 목록: 문제를 누르면 답안 · 다시 누르면 접힘 {ia}")
        await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(200)
        await pg.click('.nm-side [data-act=ljt]'); await pg.wait_for_timeout(150)
        h1 = await pg.evaluate("document.querySelector('.nm-ljl').hidden"); await pg.reload(); await pg.wait_for_timeout(3000)
        h2 = await pg.evaluate("document.querySelector('.nm-ljl').hidden"); await pg.click('.nm-side [data-act=ljt]'); await pg.wait_for_timeout(150)
        ok(h1 and h2 and not await pg.evaluate("document.querySelector('.nm-ljl').hidden"), "강의 목록 접기·펼치기(새로고침 뒤에도 기억)")
        await pg.click('[data-sact=fold]'); await pg.wait_for_timeout(300)
        await pg.click('.nm-side [data-act=sjm]'); await pg.wait_for_timeout(200)
        mi = await pg.evaluate("[...document.querySelectorAll('.nm-menu [data-mi]')].map(b=>b.dataset.mi)")
        ok('OMS1' in mi and 'CONS' in mi and '__new' in mi, f"접은 사이드바 과목 칩 → 과목 메뉴 {mi[:4]}…")
        await pg.click('.nm-menu [data-mi=OMS1]'); await pg.wait_for_timeout(1500)
        ok(await pg.evaluate("location.hash") == '#/_num/OMS1', "→ 과목 바뀜")
        await pg.click('.nm-ctx [data-act=sjm]'); await pg.wait_for_timeout(200); await pg.click('.nm-menu [data-mi=CONS]'); await pg.wait_for_timeout(1800)
        ok(await pg.evaluate("location.hash") == '#/_num/CONS', "위 막대 과목 이름 → 과목 메뉴로 돌아옴")
        await pg.click('[data-sact=fold]'); await pg.wait_for_timeout(300)
        # ---- 마지막 위치 ----
        tgt = await pg.evaluate("document.querySelectorAll('.nm-it')[30].dataset.id")
        await pg.evaluate("(id=>{const a=document.querySelector('.nm-it[data-id=\"'+id+'\"]');window.scrollTo(0,a.getBoundingClientRect().top+scrollY-150);})", tgt); await pg.wait_for_timeout(1500)
        saved = await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.num.pos.CONS')||'null')")
        await pg.reload(); await pg.wait_for_timeout(3500)
        top = await pg.evaluate("(()=>{const s=document.querySelector('.nm-stick').getBoundingClientRect().bottom;const a=[...document.querySelectorAll('.nm-it:not([hidden])')].find(x=>x.getBoundingClientRect().bottom>s+6);return a&&a.dataset.id})()")
        toastT = await pg.evaluate("document.body.innerText.includes('이어서 보여 드려요')")
        ok(saved and saved.get('id') in (tgt, None) and top == saved['id'] and toastT, f"스크롤이 멈추면 위치 저장 → 새로고침 = 그 문제부터 · '이어서' 알림 {saved} → {top}")
        await pg.evaluate("location.hash='#/_num/OMS1'"); await pg.wait_for_timeout(2000); await pg.evaluate("location.hash='#/_num/CONS'"); await pg.wait_for_timeout(2500)
        top2 = await pg.evaluate("(()=>{const s=document.querySelector('.nm-stick').getBoundingClientRect().bottom;const a=[...document.querySelectorAll('.nm-it:not([hidden])')].find(x=>x.getBoundingClientRect().bottom>s+6);return a&&a.dataset.id})()")
        ok(top2 == saved['id'], f"다른 과목에 갔다 와도 그 자리 {top2}")
        # 거르기 바꿔도 근처
        await pg.click('[data-act=flt]'); await pg.click('[data-stf="0"]'); await pg.wait_for_timeout(300); await pg.keyboard.press('Escape')
        near = await pg.evaluate("""(t=>{const s=document.querySelector('.nm-stick').getBoundingClientRect().bottom;const V=[...document.querySelectorAll('.nm-it:not([hidden])')];const a=V.find(x=>x.getBoundingClientRect().bottom>s+6);const all=[...document.querySelectorAll('.nm-it')].map(x=>x.dataset.id);return {i:all.indexOf(a&&a.dataset.id),t:all.indexOf(t),y:scrollY}})""", saved['id'])
        ok(near['i'] >= near['t'] and near['i'] - near['t'] < 6 and near['y'] > 500, f"상태 거르기를 바꿔도 보던 자리 근처 {near}")
        await pg.click('.nm-fchip[data-fx=st]'); await pg.wait_for_timeout(300)   # 칩은 문서 맨 위에 있어 누르면 맨 위
        await pg.evaluate("scrollTo(0,4000)"); await pg.wait_for_timeout(500)
        ok(await pg.evaluate("!document.querySelector('.nm-top').hidden"), "맨 위로 단추 보임(내려왔을 때)")
        await pg.click('.nm-top'); await pg.wait_for_timeout(900)
        ok(await pg.evaluate("scrollY") < 10, "맨 위로")
        # ---- 섞기 ----
        o0 = await pg.evaluate(OS)
        ok(not await pg.evaluate("!!document.querySelector('[data-act=shuf]')"), "강의별 보기에는 섞기 단추 없음")
        await pg.click('[data-mode=all]'); await pg.wait_for_timeout(700)
        base = await pg.evaluate(ORD)
        await pg.click('[data-act=shuf]'); await pg.wait_for_timeout(700)
        s1 = await pg.evaluate(ORD); nums = await pg.evaluate("[...document.querySelectorAll('.nm-it:not([hidden]) .nm-no')].map(x=>x.textContent)")
        ok(s1 != base and sorted(s1) == sorted(base) and nums == [f'{i + 1}.' for i in range(len(s1))] and await pg.evaluate("!!document.querySelector('.nm-fchip[data-act=unshuf]')"), f"섞기 = 순서 바뀜·같은 문제들·번호 1…{len(s1)} · '순서: 무작위' 칩")
        await pg.click('[data-act=shuf]'); await pg.wait_for_timeout(700); s2 = await pg.evaluate(ORD)
        ok(s2 != s1 and sorted(s2) == sorted(base), "다시 섞기 = 또 다른 순서")
        await pg.click('[data-act=flt]'); await pg.select_option('[data-cf=type]', 'num'); await pg.wait_for_timeout(300); await pg.keyboard.press('Escape')
        sf = await pg.evaluate(ORD)
        ok(0 < len(sf) < len(s2) and sf == [x for x in s2 if x in set(sf)], f"거르기와 함께 = 섞은 순서에서 걸러진 {len(sf)}문제")
        await pg.click('.nm-fchip[data-fx=type]'); await pg.wait_for_timeout(300)
        await pg.locator('.nm-it').nth(3).locator('[data-act=more]').click(); await pg.click('.nm-menu [data-mi=up]'); await pg.wait_for_timeout(300)
        ok(await pg.evaluate(ORD) == s2 and await pg.evaluate("document.body.innerText.includes('섞은 순서에서는 옮길 수 없어요')"), "섞은 채 '위로 옮기기' = 막음(순서 저장 안 바뀜)")
        await pg.click('.nm-shf [data-act=unshuf]'); await pg.wait_for_timeout(700)
        ok(await pg.evaluate(ORD) == base and await pg.evaluate(OS) == o0, "원래대로 = 처음 순서 · 저장된 순서(o) 그대로")
        await pg.click('[data-act=shuf]'); await pg.wait_for_timeout(500); await pg.click('[data-mode=grp]'); await pg.wait_for_timeout(600)
        ok(not await pg.evaluate("JBLNUM._S.shuf") and await pg.evaluate(OS) == o0, "강의별로 가면 섞기 꺼짐 · 저장 데이터 안 바뀜")
        # ---- 사이드바 백업 ----
        await pg.click('.nm-side [data-bkpop]'); await pg.wait_for_timeout(400)
        ok(await pg.evaluate("document.getElementById('bkpop').classList.contains('on')"), "사이드바 [백업] → 백업 창")
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await pg.evaluate("(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()")
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
