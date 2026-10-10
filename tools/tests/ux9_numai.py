"""UX9 내 넘버링 ↔ ChatGPT 주고받기 · 인쇄(10-10).
- 내보내기: 범위(과목 전체·강의·지금 보이는 문제·고른 문제) · 제작 상태(기본 = 스토리 없는 문제만) · 기존 스토리 넣기(기본 끔) · 나눠 받기 · JSON(format·v·sid·batch·lecs→items{id,q,a,story,s0}) · 문제·답안 글 원문 그대로 · id 고유
- 가져오기(가짜 ChatGPT 답 — 코드 블록·설명 글 섞음): 새 스토리 = 기본 선택 · 이미 있는 스토리 = 보호(바꿈) · 내보낸 뒤 JBL에서 고친 스토리 = 충돌 · 없는 ID·중복 ID·문제 글 다름·빈 스토리 = 적용 안 됨
  → '고른 것 적용' = 새 스토리만 · 문제·답안·출처·연도 그대로(스토리만 바뀜) · 새로고침 뒤 그대로 · 보호된 것은 직접 골라야 바뀜(확인 창) · 잘못된 파일 = 오류 문구·변경 없음
- 인쇄: 범위·내용(문제만/문제+답안/문제+답안+스토리) · A4 PDF로 그려짐 · 인쇄 때 메뉴·막대 숨김 · 끝나면 치움 · ⌘/Ctrl P = 인쇄 창 · pageerror 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
NIT = lambda pg: pg.evaluate("document.querySelectorAll('.nm-it').length")
RECS = """(()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.indexOf('jblhub.v1.num.i.CONS.')===0){const r=JSON.parse(localStorage.getItem(k));o[r.id]=r;}}return o})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1366, 'height': 900}, accept_downloads=True); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(U + '#/_num/CONS'); await pg.wait_for_timeout(3500)
        await pg.evaluate("(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()")
        await pg.reload(); await pg.wait_for_timeout(3000)
        await pg.click('.nm-side [data-act=imp]'); await pg.wait_for_timeout(700); await pg.click('[data-ib=flt]'); await pg.wait_for_timeout(400); await pg.click('[data-cf2=ok]'); await pg.wait_for_timeout(1200); await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(500)
        n = await NIT(pg); ok(n > 30, f"CONS 서술형 {n}문제 넣음")
        ids = await pg.evaluate("[...document.querySelectorAll('.nm-it')].map(a=>a.dataset.id)")
        A, F, G, Hq = ids[0], ids[5], ids[10], ids[11]
        # A에 스토리(내보내기 전)
        await pg.evaluate("document.querySelectorAll('.nm-it')[0].querySelector('.nm-s .nm-c').scrollIntoView({block:'center'})")
        await pg.locator('.nm-it').nth(0).locator('.nm-s .nm-c').click(); await pg.keyboard.type('내가 쓴 A 스토리'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
        # G에 번호 목록 스토리(도구 막대 '1.')
        await pg.evaluate("document.querySelectorAll('.nm-it')[10].querySelector('.nm-s .nm-c').scrollIntoView({block:'center'})")
        await pg.locator('.nm-it').nth(10).locator('.nm-s .nm-c').click(); await pg.click('.nm-tb [data-cmd=insertOrderedList]'); await pg.keyboard.type('alpha'); await pg.keyboard.press('Enter'); await pg.keyboard.type('beta'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
        # ---- 내보내기 ----
        await pg.click('.nm-side [data-act=aiout]'); await pg.wait_for_timeout(400)
        s1 = await pg.evaluate("document.querySelector('[data-xsum]').textContent")
        ok(f'내보낼 문제 {n - 2}개' in s1, f"기본 = 과목 전체 · 스토리 없는 문제만(A 빠짐) — {s1[:60]}")
        await pg.select_option('[data-xo=st]', ''); await pg.check('[data-xo=inc]'); await pg.select_option('[data-xo=chunk]', '30'); await pg.wait_for_timeout(200)
        np_ = await pg.evaluate("document.querySelectorAll('[data-xget]').length"); ok(np_ == -(-n // 30), f"나눠 받기 30문제씩 → 파일 {np_}개")
        await pg.select_option('[data-xo=chunk]', '0'); await pg.wait_for_timeout(200)
        async with pg.expect_download() as dl: await pg.click('[data-xget="0"]')
        d = await dl.value; txt = open(await d.path(), encoding='utf-8').read(); fn = d.suggested_filename
        J0 = json.loads(txt); items = [x for g in J0['lecs'] for x in g['items']]
        chk = await pg.evaluate("(L=>{const S=JBLNUM._S;return L.map(x=>{const it=S.by.get(x.id);return it?[JBLNUM._toText(it.q)===x.q,JBLNUM._toText(it.a)===x.a,JBLNUM._hsh(it.st)===x.s0]:[false,false,false]})})", items)
        ok(J0['format'] == 'jbl-numbering' and J0['v'] == 1 and J0['sid'] == 'CONS' and J0['batch'] and len(items) == n and len({x['id'] for x in items}) == n and fn.endswith('.json'), f"JSON 파일 {fn} · format·v·sid·batch · 문제 {len(items)} · id 고유")
        ok(all(all(c) for c in chk) and any(x['id'] == A and x['story'] == '내가 쓴 A 스토리' for x in items) and all(set(x) <= {'id', 'q', 'a', 'story', 's0'} for x in items), "문제·답안 글 원문 그대로 · 스토리 지문 s0 · 기존 스토리 넣기 · 불필요한 정보 없음")
        qa = await pg.evaluate("(L=>{const S=JBLNUM._S;let pl=0;for(const x of L){const it=S.by.get(x.id);const a=JBLNUM._plain(it.q).replace(/\\s+/g,''),b=x.q.replace(/\\s+/g,'');if(a===b)pl++;}return pl})", items)
        ok(qa >= len(items) * 0.9, f"문제 글 = 저장된 글자 그대로(공백 빼고 같음 {qa}/{len(items)})")
        await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(200)
        # 내보낸 뒤 F 스토리를 JBL에서 씀 → 충돌이어야
        await pg.evaluate("document.querySelectorAll('.nm-it')[5].querySelector('.nm-s .nm-c').scrollIntoView({block:'center'})")
        await pg.locator('.nm-it').nth(5).locator('.nm-s .nm-c').click(); await pg.keyboard.type('내보낸 뒤 쓴 F'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
        before = await pg.evaluate(RECS)
        # ---- 가짜 ChatGPT 답 ----
        R = json.loads(txt); L = [x for g in R['lecs'] for x in g['items']]
        for x in L: x['story'] = 'ChatGPT 스토리 ' + x['id'][-6:] + '\n**굵은 앞글자** 둘째 줄'
        byid = {x['id']: x for x in L}
        byid[A]['story'] = 'AI가 다듬은 A'
        B, C, D, E = ids[1], ids[2], ids[3], ids[4]
        byid[C]['q'] = byid[D]['q']   # ID 엉킴
        byid[E]['story'] = ''
        g0 = [x for x in items if x['id'] == G][0]['story']; byid[G]['story'] = g0   # 번호 목록 스토리를 그대로 돌려줌 → 변경 없음
        del byid[Hq]['q']   # 문제 글 없이 돌아옴 → 미리 고르지 않음
        R['lecs'][0]['items'].append(dict(byid[B]))   # 중복 ID
        R['lecs'][0]['items'].append({'id': 'jb:CONS:없는번호', 'q': '?', 'a': '', 'story': '없는 문제', 's0': '0'})
        reply = '물론이죠! 아래가 결과예요.\n```json\n' + json.dumps(R, ensure_ascii=False, indent=1) + '\n```\n더 필요하면 말해 주세요.'
        # 잘못된 입력
        await pg.click('.nm-side [data-act=aiin]'); await pg.wait_for_timeout(300)
        await pg.fill('[data-ai=txt]', '이건 JSON이 아니에요'); await pg.click('[data-ai=go]'); await pg.wait_for_timeout(300)
        m1 = await pg.evaluate("document.querySelector('[data-ai-msg]').textContent")
        await pg.fill('[data-ai=txt]', '{"format":"other","items":[{"id":"x"}]}'); await pg.click('[data-ai=go]'); await pg.wait_for_timeout(300)
        m2 = await pg.evaluate("document.querySelector('[data-ai-msg]').textContent")
        ok('JSON으로 읽지 못했어요' in m1 and 'JBL 넘버링 파일이 아니에요' in m2 and await pg.evaluate(RECS) == before, f"잘못된 파일 = 오류 문구 · 아무것도 안 바뀜 ({m1[:30]} / {m2[:30]})")
        # 미리 보기
        await pg.fill('[data-ai=txt]', reply); await pg.click('[data-ai=go]'); await pg.wait_for_timeout(600)
        pv = await pg.evaluate("""(()=>{const o={};document.querySelectorAll('[data-ar]').forEach(r=>{const k=r.dataset.k;o[k]=(o[k]||0)+1;});const on=[...document.querySelectorAll('[data-ar]')].filter(r=>r.querySelector('[data-ack]').checked).map(r=>r.dataset.k);return {k:o,on:[...new Set(on)],non:on.length,cmp:document.querySelectorAll('[data-cmp]').length}})()""")
        NEW = n - 6   # 빼는 것: A(바꿈)·F(충돌)·B(중복)·C(문제 다름)·E(빈 스토리)·G(변경 없음) — D는 정상(새 스토리) · Hq는 새 스토리지만 문제 글이 없어 미리 안 고름
        ok(pv['k'].get('upd') == 1 and pv['k'].get('cf') == 1 and pv['k'].get('dup') == 2 and pv['k'].get('miss') == 1 and pv['k'].get('qdiff') == 1 and pv['k'].get('empty') == 1 and pv['k'].get('same') == 1 and pv['k'].get('new') == NEW, f"미리 보기 분류: 새 스토리·바꿈 1·충돌 1·중복 2·없는 ID 1·문제 글 다름 1·빈 스토리 1·변경 없음 1(번호 목록 스토리를 그대로 돌려받음) {pv['k']}")
        ok(pv['on'] == ['new'] and pv['non'] == NEW - 1 and pv['cmp'] == 2, f"기본 선택 = 새 스토리만(문제 글 없이 온 것은 빼고) · 바꿈·충돌은 나란히 비교로 펼침 {pv}")
        await pg.click('[data-aapply=sel]'); await pg.wait_for_timeout(700)
        after = await pg.evaluate(RECS)
        changedOther = [i for i in before if {k: v for k, v in before[i].items() if k not in ('st', 'prev', 'u')} != {k: v for k, v in after.get(i, {}).items() if k not in ('st', 'prev', 'u')}]
        newOK = [i for i in ids if i not in (A, F, B, C, E, G, Hq) and after[i].get('st', '').startswith('<p>ChatGPT 스토리')]
        ok(not changedOther and len(newOK) == NEW - 1 and not after[Hq].get('st') and '<ol>' in after[G]['st'] and '<b>굵은 앞글자</b>' in after[D]['st'], f"적용 = 새 스토리만 · 문제·답안·출처·연도 그대로(바뀐 다른 칸 {len(changedOther)}) · **굵게** → 굵게")
        ok('내가 쓴 A 스토리' in after[A]['st'] and '내보낸 뒤 쓴 F' in after[F]['st'] and not after[B].get('st') and not after[C].get('st') and not after[E].get('st'), "이미 있는 스토리(A)·내보낸 뒤 고친 스토리(F)·중복·엉킨 ID·빈 스토리는 그대로")
        await pg.reload(); await pg.wait_for_timeout(3000)
        st5 = await pg.evaluate("(id=>document.querySelector('.nm-it[data-id=\"'+id+'\"] .nm-s .nm-c').textContent)", D)
        ok('ChatGPT 스토리' in st5, "새로고침 뒤 그대로")
        # 보호된 것은 직접 골라야(확인 창)
        await pg.click('.nm-side [data-act=aiin]'); await pg.wait_for_timeout(300); await pg.fill('[data-ai=txt]', reply); await pg.click('[data-ai=go]'); await pg.wait_for_timeout(600)
        k2 = await pg.evaluate("(()=>{const o={};document.querySelectorAll('[data-ar]').forEach(r=>{o[r.dataset.k]=(o[r.dataset.k]||0)+1});return o})()")
        ok(k2.get('same', 0) >= NEW and k2.get('new') == 1 and await pg.evaluate("document.querySelector('[data-aapply=new]').disabled"), f"같은 파일 두 번째 = 이미 넣은 것은 '변경 없음' · 안 고른 새 스토리는 '새 스토리만 적용'에도 안 들어감 {k2}")
        await pg.click(f"[data-ar][data-k=upd] [data-ack]"); await pg.click('[data-aapply=sel]'); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("!!document.querySelector('[data-ask]')"), "이미 있는 스토리 바꾸기 = 확인 창")
        await pg.focus('[data-ask="0"]'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(400)
        ok('내가 쓴 A 스토리' in (await pg.evaluate(RECS))[A]['st'] and not await pg.evaluate("!!document.querySelector('[data-ask]')"), "확인 창 '취소'에서 Enter = 취소(바뀌지 않음)")
        await pg.click('[data-aapply=sel]'); await pg.wait_for_timeout(300); await pg.click('[data-ask="1"]'); await pg.wait_for_timeout(600)
        a2 = await pg.evaluate(RECS)
        ok('AI가 다듬은 A' in a2[A]['st'] and a2[A].get('prev', {}).get('f') == 'st' and '내가 쓴 A' in a2[A]['prev']['h'], "직접 고른 것만 바뀜 · 바뀌기 전 스토리는 '마지막 수정 전으로'에 남음")
        # 다른 과목 파일 → 그 과목으로 옮겨 맞춤(없는 과목이면 오류)
        R2 = dict(R); R2['sid'] = 'NOPE'
        await pg.click('.nm-side [data-act=aiin]'); await pg.wait_for_timeout(300); await pg.fill('[data-ai=txt]', json.dumps(R2, ensure_ascii=False)); await pg.click('[data-ai=go]'); await pg.wait_for_timeout(300)
        ok('과목(NOPE)' in await pg.evaluate("document.querySelector('[data-ai-msg]').textContent"), "이 기기에 없는 과목 파일 = 오류 문구"); await pg.click('.nm-ov [data-x]')
        # 고른 문제 → 내보내기
        await pg.click('[data-act=selm]'); await pg.wait_for_timeout(500)
        for i in (7, 8, 9): await pg.locator('.nm-it').nth(i).locator('[data-ck]').check()
        await pg.click('.nm-batch [data-act=aiout]'); await pg.wait_for_timeout(300)
        sx = await pg.evaluate("[document.querySelector('input[name=xsc]:checked').value, document.querySelector('[data-xsum]').textContent, document.querySelector('[data-xo=st]').value]")
        ok(sx[0] == 'sel' and '3개' in sx[1] and sx[2] == '', f"여러 개 선택 → ChatGPT로 내보내기 = 고른 3문제 전부(제작 상태 '모든 상태') {sx}")
        await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(200)
        # ---- 인쇄 ----
        await pg.evaluate("(()=>{window.print=()=>{window.__printed=(window.__printed||0)+1};})()")
        await pg.click('.nm-batch [data-act=print]'); await pg.wait_for_timeout(300)
        await pg.select_option('[data-po=what]', 'qa'); await pg.click('[data-po=go]'); await pg.wait_for_timeout(600)
        pr = await pg.evaluate("(()=>{const d=document.getElementById('nm-print');return d?{n:d.querySelectorAll('.np-i').length,ps:d.querySelectorAll('.np-s').length,pb:d.querySelectorAll('.np-b').length,printed:window.__printed||0,cls:document.body.classList.contains('nm-printing')}:null})()")
        ok(pr and pr['n'] == 3 and pr['ps'] == 0 and pr['pb'] == 3 and pr['printed'] == 1 and pr['cls'], f"인쇄: 고른 3문제 · 문제+답안(스토리 칸 없음) · 브라우저 인쇄 호출 {pr}")
        await pg.evaluate("dispatchEvent(new Event('afterprint'))"); await pg.wait_for_timeout(100)
        ok(await pg.evaluate("!document.getElementById('nm-print')&&!document.body.classList.contains('nm-printing')"), "인쇄 뒤 치움")
        await pg.click('[data-act=selm]'); await pg.wait_for_timeout(400)
        await pg.keyboard.press('Control+p'); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("!!document.querySelector('[data-po=go]')"), "⌘/Ctrl P = 인쇄 범위·내용 고르기 창")
        await pg.click('.nm-ov input[name=psc][value=lec]'); await pg.click('[data-po=go]'); await pg.wait_for_timeout(600)
        pr2 = await pg.evaluate("(()=>{const d=document.getElementById('nm-print');return {n:d.querySelectorAll('.np-i').length,ps:d.querySelectorAll('.np-s').length,h2:d.querySelectorAll('h2').length,story:d.textContent.indexOf('ChatGPT 스토리')>=0}})()")
        ok(pr2['n'] > 0 and pr2['ps'] == pr2['n'] and pr2['h2'] == 1 and pr2['story'], f"인쇄: 강의 하나 · 문제+답안+스토리 · 강의 머리 {pr2}")
        await pg.emulate_media(media='print')
        vis = await pg.evaluate("[getComputedStyle(document.getElementById('app')).display,getComputedStyle(document.getElementById('top')).display,getComputedStyle(document.getElementById('nm-print')).display,getComputedStyle(document.getElementById('nm-print')).visibility]")
        pdf = await pg.pdf(format='A4', print_background=True, prefer_css_page_size=True)
        npg = len(re.findall(rb'/Type\s*/Page[^s]', pdf))
        ok(vis[0] == 'none' and vis[1] == 'none' and vis[2] == 'block' and vis[3] == 'visible' and len(pdf) > 5000 and npg >= 1, f"PDF(A4) {npg}쪽 · {len(pdf)//1024}KB · 인쇄 때 메뉴·막대 숨김 {vis}")
        open(J.TMP + '/nm_print_test.pdf', 'wb').write(pdf)
        await pg.emulate_media(media='screen'); await pg.evaluate("dispatchEvent(new Event('afterprint'))")
        # 모바일 대화창
        await pg.set_viewport_size({'width': 390, 'height': 844}); await pg.wait_for_timeout(300)
        await pg.click('#navbtn'); await pg.wait_for_timeout(300); await pg.click('.nm-side [data-act=aiout]'); await pg.wait_for_timeout(400)
        mo = await pg.evaluate("(()=>{const d=document.querySelector('.nm-dlg').getBoundingClientRect();return {w:Math.round(d.width),hs:document.documentElement.scrollWidth-innerWidth,drawer:document.getElementById('numv').classList.contains('sideo')}})()")
        ok(mo['w'] <= 390 and mo['hs'] <= 0 and not mo['drawer'], f"모바일: 서랍에서 내보내기 → 대화창 화면 안 · 서랍 닫힘 {mo}")
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await pg.evaluate("(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()")
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
