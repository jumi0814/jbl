"""ux4 묶음 3(B3-1~B3-6) 수용 기준 — '차분한 편집' 최종 시안(work/_tmp/ux4_final) · 1280×900 · 1180×820(터치) · 820×1180(터치)
B3-2 허브 홈: 절 순서(머리 → 이어서 → 오늘 할 일|최근 → 과목 표 → 이번 주 → 바닥) · 보이는 주 버튼(.btn.pri) 1개 · 시험·D-n·읽음·% 없음 · 과목 표 5열(오늘 열은 ≤860 숨김) ·
  과목 행 → 과목 홈 + 과목 메뉴 · 계속하기 → LS last 위치(카드 aid까지) · 휴식 중에는 머리에 '☕ 쉬는 중 m:ss'가 흐르고 [▶ 다시 공부]
B3-3 과목 홈: 절 제목 순서 = 공부 순서 · 진행률 · 교수별 출제 경향 · 교수님이 예고·강조한 것 · 강의 · 2회 이상 출제(6과목) · 경향 표 행 수 = 교수 수(세부 표 행 − 예전 담당) · 지금 단계 채운 원 하나 ·
  머리 hchip 없음·밑줄 링크 줄 · 강의 카드에 읽음 없음 · 가로 넘침 0
B3-4 강의: 탭 글자에 이모지·번호 배지 없음 · 개수는 흐린 .tn · 탭 줄 한 줄(높이 ≤48 · 가로로 밀리지 않음) · [보기 ▾] → 복습/가리기/압축/전체(버튼 글자·눌림·#stage 클래스) · R·Q·C 키도 같은 표시 ·
  [카드 ▾] 첫 줄 '이 강의의 틀' · 학습 외 탭에는 카드▾·보기▾ 없음
B3-5 틀·카드: 흐름 = 글자(알약 바탕 없음) · 틀 머리 '카드 n · m묶음' · 📌 전략 N개 → 펼침 · 카드 머리 칩 = ⭐ 기출 하나 · ✓ 원 없음 · 끝 '✓ 다 봄' · 카드 textContent 불변(표시 글자 밖 noann만 더함)
B3-6 JB: 채운 색 버튼 0(맞음·틀림·★·답 해설 — 눌러도 채움 없음) · 필터 한 줄 + [필터 ▾]로 검색 줄 · 문항 머리 ⭐ 연도 칩 1 + 글자 메타 · 달력 제목·탭 이모지 없음 · 콘솔 오류 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def go(pg, h, sel, w=500):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_selector(sel, timeout=30000); await pg.wait_for_timeout(w)
EMO = r"(t=>(t.match(/\p{Extended_Pictographic}/gu)||[]).filter(c=>!/[🔑⭐💬✍⚡📌⚠☕▶]/u.test(c)))"
FILLED = """(sel=>[...document.querySelectorAll(sel)].filter(e=>e.offsetParent).filter(e=>{const bg=getComputedStyle(e).backgroundColor,sc=/^color\\(/.test(bg)?255:1,m=(bg.replace(/^color\\(srgb/,'').match(/[\\d.]+/g)||[]).map(Number);if(m.length<3||(m.length>3&&m[3]<.5))return false;m[0]*=sc;m[1]*=sc;m[2]*=sc;const [r,g,b]=m,mx=Math.max(r,g,b),mn=Math.min(r,g,b);return mx<200||(mx-mn)>60;}).map(e=>e.tagName+'.'+e.className+':'+e.textContent.trim().slice(0,12)))"""
async def run(b, tag, vp, touch):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
    W = vp['width']; narrow = W <= 860; print('==', tag)
    await pg.goto(U + '#/'); await pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.tauto','false');localStorage.setItem('jblhub.v1.whatsNew.4','1')")
    # ---- B3-2 허브 홈
    await go(pg, '#/', '#home .hub .hsj[data-s]')
    r = await pg.evaluate("""(()=>({secs:[...document.querySelectorAll('#home .hub>.hsec')].map(e=>e.classList[1]),pri:[...document.querySelectorAll('#home .btn.pri')].filter(e=>e.checkVisibility()).length,
      tx:document.querySelector('#home').innerText,hd:[...document.querySelectorAll('#home .hsjh span')].filter(e=>e.offsetParent).map(e=>e.textContent),sw:document.documentElement.scrollWidth-innerWidth,
      today:getComputedStyle(document.querySelector('#home .hsj[data-s=CONS] .hct')).display}))()""")
    ok(r['secs'] == ['hband', 'hres', 'hduo', 'hsubj', 'hweek', 'hxtra'], f'{tag} B3-2 절 순서 {r["secs"]}')
    ok(r['pri'] == 1, f'{tag} B3-2 보이는 주 버튼 1개 ({r["pri"]})')
    ok(not re.search(r'D-\d|시험일|읽음|\d+%', r['tx']), f'{tag} B3-2 시험·D-n·읽음·% 없음')
    ok(r['hd'][:3] == ['과목', '기출 푼 것', '틀림'] and ('오늘' in r['hd']) != narrow and r['today'] == ('none' if narrow else 'block'), f'{tag} B3-2 과목 표 열 {r["hd"]} · 오늘 열 {r["today"]}')
    ok(r['sw'] <= 0, f'{tag} B3-2 가로 넘침 0 ({r["sw"]})')
    await pg.screenshot(path=J.TMP + f'/ux4i_b3_home_{tag}.png')
    await pg.evaluate("document.querySelector('#home .hsj[data-s=PHARM] .hcn').click()"); await pg.wait_for_timeout(700)
    ok(await pg.evaluate("location.hash.startsWith('#/PHARM/_home')&&document.querySelector('#nav').dataset.mode==='subj'"), f'{tag} B3-2 과목 행 → 과목 홈 + 과목 메뉴')
    # 계속하기 = LS last(카드 aid까지)
    await go(pg, '#/CONS/WHT/learn', '#stage .tc')
    aid = await pg.evaluate("document.querySelector('#t-WHT-5').dataset.aid")
    await pg.evaluate("a=>{const o={s:'CONS',d:'WHT',t:'learn',aid:a,off:0,at:Date.now(),ti:'카드 6'};localStorage.setItem('jblhub.v1.last',JSON.stringify(o));const l=JSON.parse(localStorage.getItem('jblhub.v1.lastBy')||'{}');l.CONS=o;localStorage.setItem('jblhub.v1.lastBy',JSON.stringify(l));}", aid)
    await go(pg, '#/', '#home .hrbig')
    t = await pg.inner_text('#home .hrbig'); await pg.evaluate("document.querySelector('#home .hrbig').click()"); await pg.wait_for_timeout(1600)
    d = await pg.evaluate("a=>{const e=document.querySelector('#stage .tc[data-aid=\"'+a+'\"]'),t=document.querySelector('#dtabs').getBoundingClientRect().bottom;return e?Math.round(e.getBoundingClientRect().top-t):null}", aid)
    ok('계속하기' in t and 'Tooth whitening' in t and (await pg.evaluate('location.hash')).startswith('#/CONS/WHT/learn') and d is not None and -8 <= d <= 80, f'{tag} B3-2 계속하기 → 카드 6 자리 복원 (탭 아래 {d}px · {t[:40]!r})')
    # 휴식 중 머리 — '☕ 쉬는 중 m:ss' 흐름 · [▶ 다시 공부]
    await go(pg, '#/', '#home .hband [data-trk]')
    await pg.evaluate("__h.trStart()"); await pg.wait_for_timeout(300); await pg.evaluate("document.querySelector('#home .hband [data-trb=rest]').click()"); await pg.wait_for_timeout(1300)
    a1 = await pg.evaluate("[(document.querySelector('#home .hband .trs')||{}).textContent,!!document.querySelector('#home .hband [data-trb=resume]'),document.querySelector('#home .hband .trs')&&getComputedStyle(document.querySelector('#home .hband .trs')).display]")
    await pg.wait_for_timeout(2100); a2 = await pg.evaluate("(document.querySelector('#home .hband .trt')||{}).textContent")
    ok(a1[0] and '쉬는 중' in a1[0] and a1[1] and a1[2] != 'none' and a2 and a2 != (a1[0] or '').split(' ')[-1], f'{tag} B3-2 쉬는 중 머리 휴식 시간 흐름·[▶ 다시 공부] {a1} → {a2}')
    await pg.evaluate("document.querySelector('#home .hband [data-trb=stop]').click()"); await pg.wait_for_timeout(300)
    # ---- B3-3 과목 홈(6과목)
    for S in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
        await go(pg, f'#/{S}/_home/_home', '#stage .lcard', 300)
        r = await pg.evaluate("""(()=>{const h=[...document.querySelectorAll('#stage h2.hh')].map(e=>(e.childNodes[0].textContent||'').trim());const tr=document.querySelectorAll('#stage table.ttab tbody tr').length,dt=document.querySelectorAll('#stage table.trendtbl tbody tr').length,
          sm=(document.querySelector('#stage details.trd>summary')||{}).textContent||'',old=(sm.split('예전 담당 ')[1]||'').split('·').filter(Boolean).length;
          return {h,tr,dt,old,now:document.querySelectorAll('#hguide li.now').length,chip:document.querySelectorAll('#hero .hchip').length,lead:document.querySelectorAll('#hero .hlead [data-hgo]').length,lc:[...document.querySelectorAll('#stage .lcard')].map(e=>e.innerText).join(' '),sw:document.documentElement.scrollWidth-innerWidth}})()""")
        want = ['공부 순서', '진행률', '교수별 출제 경향', '교수님이 예고·강조한 것', '강의', '2회 이상 출제']
        seq = [x for x in r['h'] if x in want]
        ok(seq == [x for x in want if x in seq] and seq[:3] == want[:3] and '강의' in seq and '2회 이상 출제' in seq, f'{tag} B3-3 {S} 절 순서 {seq}')
        ok(r['tr'] >= 1 and r['tr'] + r['old'] == r['dt'], f'{tag} B3-3 {S} 경향 표 행 {r["tr"]} = 교수 {r["dt"]} − 예전 담당 {r["old"]}')
        ok(r['now'] == 1 and r['chip'] == 0 and r['lead'] == 5 and '읽음' not in r['lc'] and '%' not in r['lc'] and r['sw'] <= 0, f'{tag} B3-3 {S} 지금 단계 1 · hchip 0 · 링크 줄 5 · 강의 카드 읽음 없음 · 넘침 {r["sw"]}')
        if S == 'CONS': await pg.screenshot(path=J.TMP + f'/ux4i_b3_subject_{tag}.png')
    await pg.evaluate("document.querySelector('#hero [data-hgo=_jb]').click()"); await pg.wait_for_timeout(600)
    ok((await pg.evaluate('location.hash')).startswith('#/PHARM/_jb'), f'{tag} B3-3 머리 링크 → JB 문제')
    # ---- B3-4 강의 탭 줄·미니바
    await go(pg, '#/CONS/WHT/learn', '#stage .tc')
    r = await pg.evaluate(f"""(()=>{{const d=document.querySelector('#dtabs'),tabs=[...d.querySelectorAll('button[data-t]')];return {{emo:tabs.flatMap(b=>{EMO}(b.textContent)),kbd:d.querySelectorAll('.kbd').length,h:d.clientHeight,
      ov:d.scrollWidth-d.clientWidth,tn:getComputedStyle(d.querySelector('.tn')).color,lab:tabs.map(b=>b.textContent),btn:[...d.querySelectorAll('#lmini>button,#lmini .ktog,#lmini .dfoc')].map(b=>b.id||b.className)}}}})()""")
    ok(not r['emo'] and r['kbd'] == 0 and r['lab'][0] == '학습', f'{tag} B3-4 글자 탭(이모지·번호 배지 없음) {r["lab"]}')
    ok(r['h'] <= 48 and r['ov'] <= 1, f'{tag} B3-4 탭 6 + 미니바 한 줄(높이 {r["h"]} ≤48 · 밀림 {r["ov"]})')
    ok(r['btn'][:2] == ['lmcur', 'lmview'] and len(r['btn']) == 4, f'{tag} B3-4 미니바 4개 {r["btn"]}')
    await pg.screenshot(path=J.TMP + f'/ux4i_b3_lecture_{tag}.png')
    VS = "[document.querySelector('#lmview').textContent,document.querySelector('#lmview').getAttribute('aria-pressed'),['review','cond','quiz'].filter(c=>document.querySelector('#stage').classList.contains(c)).join(','),document.querySelector('#lvpop').classList.contains('on')]"
    async def pick(i):
        if touch: await pg.tap('#lmview')
        else: await pg.click('#lmview')
        await pg.wait_for_timeout(250); o = await pg.evaluate("document.querySelector('#lvpop').classList.contains('on')")
        if touch: await pg.tap('#' + i)
        else: await pg.click('#' + i)
        await pg.wait_for_timeout(450); return o, await pg.evaluate(VS)
    o, v = await pick('lmrev'); ok(o and v[0] == '복습' and v[1] == 'true' and 'review' in v[2] and not v[3], f'{tag} B3-4 보기 ▾ → 복습 {v}')
    await pg.screenshot(path=J.TMP + f'/ux4i_b3_view_{tag}.png')
    o, v = await pick('lmall'); ok(v[0] == '보기' and v[1] == 'false' and v[2] == '', f'{tag} B3-4 보기 ▾ → 전체 {v}')
    o, v = await pick('lmqz'); ok(v[0] == '가리기' and 'quiz' in v[2], f'{tag} B3-4 보기 ▾ → 가리기 {v}')
    await pg.evaluate("document.dispatchEvent(new KeyboardEvent('keydown',{key:'ㅂ',code:'KeyQ',bubbles:true}))"); await pg.wait_for_timeout(300)
    await pg.evaluate("document.dispatchEvent(new KeyboardEvent('keydown',{key:'ㄱ',code:'KeyR',bubbles:true}))"); await pg.wait_for_timeout(400)
    v = await pg.evaluate(VS); ok(v[0] == '복습' and 'review' in v[2], f'{tag} B3-4 Q(끔)·R(켬) 키 → 버튼 글자 따라감 {v}')
    await pg.evaluate("document.dispatchEvent(new KeyboardEvent('keydown',{key:'ㄱ',code:'KeyR',bubbles:true}))"); await pg.wait_for_timeout(400)
    await pg.evaluate("document.dispatchEvent(new KeyboardEvent('keydown',{key:'ㅊ',code:'KeyC',bubbles:true}))"); await pg.wait_for_timeout(400)
    v = await pg.evaluate(VS); ok(v[0] == '압축' and 'cond' in v[2], f'{tag} B3-4 C 키 → 압축 {v}')
    o, v = await pick('lmall'); ok(v[2] == '' and v[0] == '보기', f'{tag} B3-4 전체로 되돌림 {v}')
    if touch: await pg.tap('#lmcur')
    else: await pg.click('#lmcur')
    await pg.wait_for_timeout(300)
    ok(await pg.evaluate("document.querySelector('#lpop .lpi:first-child').textContent.includes('이 강의의 틀')"), f'{tag} B3-4 카드 ▾ 첫 줄 이 강의의 틀')
    await pg.keyboard.press('Escape'); await pg.evaluate("document.querySelector('#lpop').classList.remove('on')")
    # ---- B3-5 틀·카드
    r = await pg.evaluate("""(()=>{const f=document.querySelector('#stage .frame'),fl=f.querySelector('.flow .fl'),c=document.querySelector('#t-WHT-3');
      return {flbg:getComputedStyle(fl).backgroundColor,frn:(f.querySelector('.frn')||{}).textContent,chips:[...c.querySelectorAll('.tchips .chip')].filter(e=>e.offsetParent).map(e=>e.className),
        dn:getComputedStyle(c.querySelector('.thead>.dn')).display,end:c.lastElementChild.className,tsh:(f.querySelector('.tstr .tsh')||{dataset:{}}).dataset.n}})()""")
    ok(r['flbg'] in ('rgba(0, 0, 0, 0)', 'transparent') and re.match(r'카드 \d+ · \d+묶음', r['frn'] or ''), f'{tag} B3-5 흐름 글자·틀 머리 {r["frn"]}')
    ok(r['chips'] == ['chip yr n2'] and r['dn'] == 'none' and 'dnend' in r['end'], f'{tag} B3-5 카드 머리 칩 ⭐ 하나 {r["chips"]} · ✓ 원 {r["dn"]} · 끝 {r["end"]}')
    if r['tsh']:
        await pg.evaluate("document.querySelector('#stage .frame').classList.remove('fold');document.querySelector('#stage .frame .tstr .tsh').click()"); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("document.querySelector('#stage .frame .tstr').classList.contains('open')&&getComputedStyle(document.querySelector('#stage .frame .tstr .tsl2')).display!=='none'"), f'{tag} B3-5 📌 전략 {r["tsh"]}개 → 펼침')
    await pg.evaluate("document.querySelector('#t-WHT-3').scrollIntoView()"); await pg.wait_for_timeout(300)
    await pg.screenshot(path=J.TMP + f'/ux4i_b3_card4_{tag}.png')
    # 학습 외 탭 — 카드▾·보기▾ 없음 · 도구·집중만
    await pg.evaluate("document.querySelector('#dtabs button[data-t=sum]').click()"); await pg.wait_for_timeout(500)
    ok(await pg.evaluate("!document.querySelector('#dtabs #lmcur,#dtabs #lmview')&&!!document.querySelector('#dtabs [data-kitt]')&&!!document.querySelector('#dtabs .dfoc')"), f'{tag} B3-4 정리표 탭: 카드▾·보기▾ 없음 · 도구·집중')
    # ---- B3-6 JB
    await go(pg, '#/CONS/_jb/_jb', '#cards .qc')
    await pg.evaluate("(()=>{const c=document.querySelector('#cards .qc');c.querySelector('[data-mk=ok]').click();document.querySelectorAll('#cards .qc')[1].querySelector('[data-mk=ng]').click();document.querySelectorAll('#cards .qc')[2].querySelector('[data-mk=bm]').click();c.querySelector('[data-tog]').click();})()"); await pg.wait_for_timeout(400)
    fl = await pg.evaluate(FILLED + "('#stage #jbbar button,#stage .qc .acts .btn,#stage .qc .qhead *')")
    ok(not fl, f'{tag} B3-6 채운 색 버튼 0 {fl[:4]}')
    r = await pg.evaluate("""(()=>{const q=document.querySelectorAll('#cards .qc'),cs=e=>getComputedStyle(e);const ok_=q[0].querySelector('[data-mk=ok]'),ng=q[1].querySelector('[data-mk=ng]'),bm=q[2].querySelector('[data-mk=bm]');
      return {ok:[cs(ok_).fontWeight,cs(ok_).color],ng:cs(ng).color,bm:cs(bm).borderTopColor,b2:getComputedStyle(document.querySelector('#jbbar .b2')).display,yb:[...q[0].querySelectorAll('.qhead .ybadge')].length,lec:(q[0].querySelector('.qhead .chip.lec')||{}).textContent||''}})()""")
    ok(r['ok'][0] == '700' and r['ok'][1] == 'rgb(35, 33, 29)' and r['ng'] == 'rgb(179, 38, 30)' and r['bm'] == 'rgb(212, 167, 44)', f'{tag} B3-6 맞음 ink 굵게 · 틀림 빨강 글자 · ★ 노란 선 {r}')
    ok(r['b2'] == 'none' and r['yb'] == 1 and '📖' not in r['lec'] and '정리본' in r['lec'], f'{tag} B3-6 검색 줄 접힘 · ⭐ 연도 칩 1 · 정리본 글자 링크 {r["lec"]!r}')
    await pg.evaluate("document.querySelector('#fexp').click()"); await pg.wait_for_timeout(250)
    ok(await pg.evaluate("getComputedStyle(document.querySelector('#jbbar .b2')).display!=='none'&&document.querySelector('#fq').offsetParent!==null"), f'{tag} B3-6 [필터 ▾] → 검색·상세 줄')
    await pg.screenshot(path=J.TMP + f'/ux4i_b3_jb_{tag}.png')
    await go(pg, '#/_cal', '#calg')
    e = await pg.evaluate(f"{EMO}(document.querySelector('.calhd').innerText)")
    ok(not e, f'{tag} B3-6 달력 제목·탭 이모지 없음 {e}')
    await pg.screenshot(path=J.TMP + f'/ux4i_b3_cal_{tag}.png')
    ok(not errs, f'{tag} 콘솔 오류 0 {errs[:3]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for tag, vp, t in [('1280', {'width': 1280, 'height': 900}, False), ('1180', {'width': 1180, 'height': 820}, True), ('820', {'width': 820, 'height': 1180}, True)]:
            await run(b, tag, vp, t)
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
    for f in fails: print('  -', f)
    _sys.exit(1 if fails else 0)
asyncio.run(main())
