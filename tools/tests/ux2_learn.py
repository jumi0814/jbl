"""ux2 묶음 4(트랙B) 회귀 — 정리본 학습 탭: 빠른 훑기·가독성·암기 (D01~D12). 맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)
D01 압축 보기: 🔑·.krest 보이는 글자 = 압축 전 · 연도 칩 보임·태그 칩 숨김 · 형광 친 .li만 남고 나머지 .li 숨김 · '내 표시만' 필터
D02 ⚡ 복습 보기(R): 1280 EXT 카드 평균 높이 ≤ 220 · 문서 ≤ 5000 · R 두 번 = 원래대로 · 몰라요 2장 → '몰라요 먼저'에서 앞 · 새로고침 유지 · 2회↑만 · 표시 복원 수 불변 · 머리 누르면 끄고 그 카드
D03 ⚡ 가리기(그 블록 .k만) · ⚡ 줄 키(data-fk) = 플래시카드 R: 키 — 줄마다 ○✕는 ux4에서 없앰 · 플래시카드 '몰라요만'에 나옴 · ann 불변
D04 ⭐ 구조화: 연도 머리 숨김·형식 칩·근거 접힘(누르면 펼침) · HM ⭐ 블록 높이(보고)
D05 '⭐ n ↓' → .c-exam이 탭 아래 ±20 · Shift+J 3번 = data-n>0 카드만 · ⭐ 먼저 → .c-exam이 첫 .li 위 · 목록 ⭐ 숫자 → ⭐ 블록
D06 기본 = 시험 핵심만 빨강(.k2는 빨강 아님) · '전부' = 빨간 span 수 = 전체 .k · 가리기 대상은 .k:not(.k2)
D07 EXT 카드 2: 보이는 글자에 '(필기)' 0 · ✍(.srcn) 수 = textContent의 '(필기)' 수
D08 ANAT MAND 카드 7 머리에 'p.'
D10 GRAFT 처음 열면 src 있는 그림 < 30 · 1장 그림 폭 ≥ 500 · I 순환 → LS figmode·새로고침 유지
D11 EXT 카드 1 ✓ 뒤 다시 열면 틀 접힘·첫 카드 top ≤ 450 · 6과목 ⭐ 많이 나온 순에 (탈)·(짤)·(복원 원문)·발문만 0 · 줄 누르면 그 카드
D12 HM ⭐ 칩 → 해시 그대로·.jbpeek·답 가림 · ✗ → mk.ng · [JB에서 풀기] → 기출 탭·↩ 알약"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1300):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
async def until(pg, js, t=4000):
    try: await pg.wait_for_function(js, timeout=t); return True
    except Exception: return False
VIS = "e=>!!e&&e.offsetParent!==null&&getComputedStyle(e).display!=='none'"
NRK = "document.querySelectorAll('#stage [data-rk]').length"
WORDXY = """(sel)=>{const e=document.querySelector(sel);e.scrollIntoView({block:'center'});const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){const m=/[A-Za-z가-힣]{3,}/.exec(x.nodeValue);if(m&&!x.parentElement.closest('button,.chip,.noann')){const r=document.createRange();r.setStart(x,m.index+1);r.setEnd(x,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2,m[0]];}}}"""
def packs():
    out = {}
    for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
        t = open(_os.path.join(J.DOCS, 'packs', s + '.js'), encoding='utf-8').read(); out[s] = json.loads(t[t.index('JBLHUB.register(') + 16:-2])
    return out

async def mac(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    # ---- D01 압축 보기
    await open_(pg, '#/PHARM/HM/learn')
    KT = "(()=>{const c=document.querySelector('#t-HM-4');return [...c.querySelectorAll('.c-key,.krest')].map(e=>e.innerText).join('').replace(/[\\s·]/g,'')})()"
    t0 = await pg.evaluate(KT); await pg.evaluate("document.querySelector('#lmcond').click()"); await pg.wait_for_timeout(200)
    t1 = await pg.evaluate(KT)
    ok(t0 == t1 and len(t0) > 20, f'D01 HM 카드 5 압축 전후 🔑·krest 보이는 글자 같음 ({len(t0)}자)')
    r = await pg.evaluate(f"(()=>{{const v={VIS};const y=[...document.querySelectorAll('#stage .tc .tchips .chip.yr')];const tg=[...document.querySelectorAll('#stage .tc .tchips .tagc')];return [y.length,y.filter(v).length,tg.filter(v).length]}})()")
    ok(r[0] > 0 and r[0] == r[1] and r[2] == 0, f'D01 압축: 연도 칩 {r[1]}/{r[0]} 보임 · 태그 칩 {r[2]} 보임')
    await pg.screenshot(path=J.TMP + '/ux2i_d01_cond_1280.png')
    await pg.evaluate("document.querySelector('#lmcond').click()")
    await open_(pg, '#/OMS1/EXT/learn')
    await pg.evaluate("document.querySelector('#k-h').click()")
    a = await pg.evaluate(WORDXY, '#t-EXT-2 .tbody > .li'); await pg.mouse.click(a[0], a[1]); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('#k-h').click()")
    await pg.evaluate("document.querySelector('#lmcond').click()"); await pg.wait_for_timeout(200)
    r = await pg.evaluate(f"(()=>{{const v={VIS};const L=[...document.querySelectorAll('#t-EXT-2 .tbody .li')].filter(l=>!l.closest('.krest'));const m=L.filter(l=>l.querySelector('[data-rk]'));return [m.length,m.filter(v).length,L.filter(l=>!l.querySelector('[data-rk]')&&v(l)).length]}})()")
    ok(r[0] == 1 and r[1] == 1 and r[2] == 0, f'D01 형광 친 줄만 압축에서 보임 ("{a[2]}") {r}')
    await pg.screenshot(path=J.TMP + '/ux2i_d01_mine_1280.png')
    await pg.evaluate("document.querySelector('#lmcond').click()")
    await pg.evaluate("document.querySelector('[data-filt=mine]').click()"); await pg.wait_for_timeout(200)
    r = await pg.evaluate(f"(()=>{{const v={VIS};return [...document.querySelectorAll('#stage .tc')].filter(v).map(c=>c.id)}})()")
    ok(r == ['t-EXT-2'], f'D01 내 표시만 → {r}')
    await pg.evaluate("document.querySelector('[data-filt=mine]').click()")
    await pg.evaluate("localStorage.removeItem('jblhub.v1.ann.OMS1')")
    # ---- D02 복습 보기
    await open_(pg, '#/OMS1/EXT/learn'); n0 = await pg.evaluate(NRK); h0 = await pg.evaluate('document.documentElement.scrollHeight')
    await pg.keyboard.press('r'); await pg.wait_for_timeout(500)
    r = await pg.evaluate(f"(()=>{{const v={VIS};const cs=[...document.querySelectorAll('#stage .tc')].filter(v);const hs=cs.map(c=>c.getBoundingClientRect().height);return [document.querySelector('#stage').classList.contains('review'),Math.round(hs.reduce((a,b)=>a+b,0)/hs.length),document.documentElement.scrollHeight,document.querySelectorAll('#stage .k.qzk:not(.show)').length]}})()")
    ok(r[0] and r[1] <= 220 and r[2] <= 5000, f'D02 EXT 복습 보기: 카드 평균 {r[1]}px ≤ 220 · 문서 {r[2]}px ≤ 5000')
    ok(r[3] > 0, f'D02 복습 보기 빨간 글씨 가림 {r[3]}개(가리기 보기 강의 전체)')
    await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(200); await pg.screenshot(path=J.TMP + '/ux2i_d02_review_1280.png')
    await pg.evaluate("document.querySelector('#t-EXT-4 .rvj [data-rv=x]').click();document.querySelector('#t-EXT-9 .rvj [data-rv=x]').click()")
    fc = await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.fc.OMS1')||'{}')")
    ok(sum(1 for k, v in fc.items() if k.startswith('V:') and v.get('s') == 'x') == 2, f'D02 몰라요 2장 → fc.OMS1 V: 키 2개')
    await pg.evaluate("document.querySelector('[data-rvs=x]').click()"); await pg.wait_for_timeout(300)
    r = await pg.evaluate(f"(()=>{{const v={VIS};return [...document.querySelectorAll('#stage .tc')].filter(v).sort((a,b)=>a.getBoundingClientRect().top-b.getBoundingClientRect().top).slice(0,3).map(c=>c.id)}})()")
    ok(r[:2] == ['t-EXT-4', 't-EXT-9'], f'D02 몰라요 먼저 → {r}')
    await open_(pg, '#/OMS1/EXT/learn')
    r = await pg.evaluate(f"(()=>{{const v={VIS};return [document.querySelector('#stage').classList.contains('review'),[...document.querySelectorAll('#stage .tc')].filter(v).sort((a,b)=>a.getBoundingClientRect().top-b.getBoundingClientRect().top)[0].id]}})()")
    ok(r == [True, 't-EXT-4'], f'D02 새로고침 뒤 복습 보기·정렬 유지 {r}')
    await pg.evaluate("document.querySelector('[data-rvs=\"\"]').click()")
    await pg.evaluate("document.querySelector('[data-filt=rep2]').click()"); await pg.wait_for_timeout(200)
    r = await pg.evaluate(f"(()=>{{const v={VIS};const cs=[...document.querySelectorAll('#stage .tc')].filter(v);return [cs.length,cs.filter(c=>+c.dataset.n<2).length,document.querySelector('#lmN').textContent,[...document.querySelectorAll('#stage .gdiv')].filter(g=>v(g)).length]}})()")
    ok(r[0] > 0 and r[1] == 0 and r[2] == str(r[0]), f'D02 2회↑만: 보이는 카드 {r[0]} · data-n<2 {r[1]} · 미니바 N {r[2]} · 그룹 제목 {r[3]}')
    await pg.evaluate("document.querySelector('[data-filt=rep2]').click()")
    await pg.evaluate("document.querySelector('[data-filt=jb]').click()"); await pg.wait_for_timeout(200)
    r = await pg.evaluate(f"(()=>{{const v={VIS};return [...document.querySelectorAll('#stage .tc')].filter(v).filter(c=>c.dataset.n==='0').length}})()")
    ok(r == 0, f'D02 ⭐ 기출 카드만: data-n=0 보임 {r}')
    await pg.evaluate("document.querySelector('[data-filt=jb]').click()")
    await pg.keyboard.press('r'); await pg.wait_for_timeout(400)
    r = await pg.evaluate(f"[document.querySelector('#stage').classList.contains('review'),{NRK},document.documentElement.scrollHeight,document.querySelectorAll('#stage .k.qzk').length]")
    ok(not r[0] and r[1] == n0 and abs(r[2] - h0) < 60 and r[3] == 0, f'D02 R 두 번 → 원래대로 (표시 {n0}→{r[1]} · 문서 {h0}→{r[2]} · 가림 {r[3]})')
    await pg.keyboard.press('r'); await pg.wait_for_timeout(300)
    await pg.evaluate("document.querySelector('#t-EXT-6 .thead .ko').click()"); await pg.wait_for_timeout(900)
    r = await pg.evaluate("[document.querySelector('#stage').classList.contains('review'),Math.round(document.querySelector('#t-EXT-6').getBoundingClientRect().top-document.querySelector('#dtabs').getBoundingClientRect().bottom)]")
    ok(not r[0] and 0 <= r[1] <= 30, f'D02 복습 머리 누르면 끄고 그 카드로 {r}')
    await pg.evaluate("localStorage.setItem('jblhub.v1.review','false')")
    # ---- D03 ⚡ 가리기·○✕
    await open_(pg, '#/OMS1/EXT/learn'); ann0 = await pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')")
    await pg.evaluate("document.querySelector('#t-EXT-0 .memqz').click()")
    r = await pg.evaluate("(()=>{const tr=k=>getComputedStyle(k).color==='rgba(0, 0, 0, 0)';const a=[...document.querySelectorAll('#t-EXT-0 .c-mem .k')],o=[...document.querySelectorAll('#t-EXT-0 .k:not(.c-mem .k)'),...document.querySelectorAll('#t-EXT-1 .c-mem .k')];return [a.length,a.filter(tr).length,o.filter(tr).length]})()")
    ok(r[0] > 0 and r[0] == r[1] and r[2] == 0, f'D03 ⚡ 가리기 = 그 블록 .k만 {r}')
    await pg.evaluate("document.querySelector('#t-EXT-0 .c-mem .k').click()")
    ok(await pg.evaluate("document.querySelector('#t-EXT-0 .c-mem .k').classList.contains('mshow')"), 'D03 가린 칸 누르면 열림')
    fk = await pg.evaluate("(()=>{const li=document.querySelector('#t-EXT-0 .c-mem li[data-fk]');return [li.dataset.fk,document.querySelectorAll('#stage .mj,#stage [data-mj]').length]})()")
    ok(fk[0].startswith('R:EXT:') and fk[1] == 0, f'D03 ⚡ 줄 키 data-fk = 플래시카드 키 · ux4 B1-5 줄마다 ○✕ 없음 {fk}')
    ok(ann0 == await pg.evaluate("localStorage.getItem('jblhub.v1.ann.OMS1')"), 'D03 ann 변화 0')
    await pg.screenshot(path=J.TMP + '/ux2i_d03_mem_1280.png')
    keys = await pg.evaluate("[...new Set([...document.querySelectorAll('#stage .c-mem li[data-fk]')].map(l=>l.dataset.fk))]")
    await pg.evaluate("ks=>{const o=JSON.parse(localStorage.getItem('jblhub.v1.fc.OMS1')||'{}');ks.forEach(k=>o[k]={s:'x',t:1});localStorage.setItem('jblhub.v1.fc.OMS1',JSON.stringify(o))}", keys)
    await open_(pg, '#/OMS1/EXT/flash')
    r = await pg.evaluate("(()=>{document.querySelector('[data-fk=\"암기\"]').click();return document.querySelector('[data-fst=x]').textContent})()")
    ok(r.strip() == f'몰라요만 {len(keys)}', f'D03 ⚡ 줄 키 {len(keys)}개 = 플래시카드 암기 키 (몰라요만 → "{r}")')
    await pg.evaluate("localStorage.removeItem('jblhub.v1.fc.OMS1')")
    # ---- D04 ⭐ 구조화
    await open_(pg, '#/PHARM/HM/learn')
    r = await pg.evaluate(f"(()=>{{const v={VIS};const x=document.querySelectorAll('#stage .exs').length;const yr=[...document.querySelectorAll('#stage .ex-yr')].filter(v).length;const src=[...document.querySelectorAll('#stage .ex-src')];return [x,yr,src.length,src.filter(v).length,document.querySelectorAll('#stage .exf').length]}})()")
    ok(r[0] > 20 and r[1] == 0 and r[2] > 0 and r[3] == 0 and r[4] > 0, f'D04 HM 구조화 {r[0]} · 연도 머리 보임 {r[1]} · 근거 {r[2]}개 접힘(보임 {r[3]}) · 형식 칩 {r[4]}')
    await pg.evaluate("(()=>{const b=document.querySelector('#stage .exsrcb');b.scrollIntoView({block:'center'});b.click()})()")
    ok(await pg.evaluate(f"({VIS})(document.querySelector('#stage .exs.srcopen .ex-src'))"), 'D04 근거 ▸ 누르면 펼침')
    hx = await pg.evaluate("[...document.querySelectorAll('#stage .c-exam')].reduce((a,e)=>a+e.getBoundingClientRect().height,0)|0")
    print(f'  INFO D04 HM ⭐ 블록 높이 합 {hx}px (2차 전 기준선 2767px)')
    await pg.evaluate("(()=>{const e=document.querySelector('#t-HM-20 .c-exam');e.scrollIntoView({block:'center'})})()"); await pg.screenshot(path=J.TMP + '/ux2i_d04_exam_1280.png')
    # ---- D05 ⭐ 바로 가기
    await open_(pg, '#/OMS1/EXT/learn')
    await pg.evaluate("document.querySelector('#t-EXT-0 [data-exjump]').click()"); await pg.wait_for_timeout(900)
    d = await pg.evaluate("Math.round(document.querySelector('#t-EXT-0 .c-exam').getBoundingClientRect().top-document.querySelector('#dtabs').getBoundingClientRect().bottom)")
    ok(abs(d - 12) <= 20, f'D05 ⭐ ↓ → .c-exam이 탭 아래 {d}px')
    await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(300); seen = []
    for _ in range(3):
        await pg.keyboard.press('Shift+J'); await pg.wait_for_timeout(1000); seen.append(await pg.evaluate("(()=>{const j=__h.LCUR;const c=document.querySelector('#t-EXT-'+j);return [j,c?+c.dataset.n:-1]})()"))
    ok(all(n > 0 for _, n in seen) and [j for j, _ in seen] == sorted({j for j, _ in seen}) and len(seen) == 3, f'D05 Shift+J 3번 = 기출 카드만 {seen}')
    await pg.evaluate("document.querySelector('#lexfirst').click()"); await pg.wait_for_timeout(200)
    r = await pg.evaluate("(()=>{const c=[...document.querySelectorAll('#stage .tc')].find(c=>c.querySelector('.c-exam')&&c.querySelector('.tbody>.li'));return [c.id,c.querySelector('.c-exam').getBoundingClientRect().top<c.querySelector('.tbody>.li').getBoundingClientRect().top,JSON.parse(localStorage.getItem('jblhub.v1.exfirst'))]})()")
    ok(r[1] and r[2] is True, f'D05 ⭐ 먼저 → .c-exam이 첫 .li 위 {r}')
    await pg.evaluate("document.querySelector('#lexfirst').click()")
    await pg.evaluate("window.scrollTo(0,0)"); await pg.evaluate("document.querySelector('#lmcur').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('#lpop .lpi[data-lj=\"7\"] i').click()"); await pg.wait_for_timeout(900)
    d = await pg.evaluate("Math.round(document.querySelector('#t-EXT-7 .c-exam').getBoundingClientRect().top-document.querySelector('#dtabs').getBoundingClientRect().bottom)")
    ok(abs(d - 12) <= 20, f'D05 목록 ⭐ 숫자 → 카드 8의 ⭐ 블록 {d}px')
    # ---- D06 빨강 두 단계
    await open_(pg, '#/OMS1/EXT/learn')
    RC = "(()=>{const red=k=>{const c=getComputedStyle(k).color.match(/\\d+/g).map(Number);return c[0]>=150&&c[1]<=90&&c[2]<=90};const ks=[...document.querySelectorAll('#stage .tc .k')];return [ks.length,ks.filter(red).length,document.querySelectorAll('#stage .tc .k.k2').length]})()"
    r0 = await pg.evaluate(RC)
    ok(r0[2] > 0 and r0[1] == r0[0] - r0[2], f'D06 시험 핵심만: 빨강 {r0[1]}/{r0[0]} (.k2 {r0[2]}는 굵은 검정)')
    await pg.evaluate("document.querySelector('[data-redm=all]').click()"); r1 = await pg.evaluate(RC)
    ok(r1[1] == r1[0] == 480, f'D06 전부 빨강: 빨간 span {r1[1]} = 전체 {r1[0]} (2차 전 480)')
    await pg.evaluate("document.querySelector('[data-redm=core]').click()")
    await pg.evaluate("document.querySelector('#t-EXT-2').scrollIntoView()"); await pg.keyboard.press('q'); await pg.wait_for_timeout(300)
    r = await pg.evaluate("[document.querySelectorAll('#stage .k.qzk').length,document.querySelectorAll('#stage .k.k2.qzk').length]")
    ok(r[0] > 0 and r[1] == 0, f'D06 가리기 대상 = .k:not(.k2) {r}')
    await pg.keyboard.press('q')
    # ---- D07 출처 메타
    r = await pg.evaluate("(()=>{const c=document.querySelector('#t-EXT-1');return [(c.innerText.match(/\\(필기\\)/g)||[]).length,c.querySelectorAll('.srcn:not(.srch)').length,(c.textContent.match(/\\((\\d{2}\\s)?필기\\)/g)||[]).length]})()")
    ok(r[0] == 0 and r[1] == r[2] and r[1] > 0, f'D07 EXT 카드 2: 보이는 (필기) {r[0]} · ✍ {r[1]} = 원문 (필기) {r[2]}')
    # ---- D08 쪽 범위
    await open_(pg, '#/ANAT/MAND/learn')
    r = await pg.evaluate("document.querySelector('#t-MAND-6 .thead .ko .pg')?.textContent||''")
    ok('p.' in r, f'D08 ANAT MAND 카드 7 머리 "{r}"')
    # ---- D10 그림
    await pg.goto('about:blank'); await pg.goto(U + '#/IMPL/GRAFT/learn'); await pg.wait_for_timeout(2000)
    r = await pg.evaluate("[document.querySelectorAll('#stage img[src]').length,document.querySelectorAll('#stage .tc .figs img').length,Math.round(document.querySelector('#stage .figs.one figure').getBoundingClientRect().width)]")
    ok(r[0] < 30 and r[1] > 60 and r[2] >= 500, f'D10 GRAFT 처음 src 있는 그림 {r[0]}/{r[1]} < 30 · 1장 그림 폭 {r[2]} ≥ 500')
    await pg.keyboard.press('i'); await pg.wait_for_timeout(200)
    r = await pg.evaluate("[JSON.parse(localStorage.getItem('jblhub.v1.figmode')),document.body.classList.contains('figsmall'),Math.round(document.querySelector('#stage .tc .figs figure img').getBoundingClientRect().height)]")
    ok(r[0] == 'small' and r[1] and r[2] <= 74, f'D10 I → 작게(72px 띠) {r}')
    await pg.evaluate("document.querySelector('#stage .tc .figs').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(300); await pg.screenshot(path=J.TMP + '/ux2i_d10_small_1280.png')
    await pg.keyboard.press('i'); await open_(pg, '#/IMPL/GRAFT/learn')
    r = await pg.evaluate(f"(()=>{{const v={VIS};const f=document.querySelector('#stage .tc .figs'),c=document.querySelector('#stage .tc .figchip');return [document.body.classList.contains('fighide'),v(f),v(c)]}})()")
    ok(r == [True, False, True], f'D10 숨김 → 새로고침 뒤 유지·🖼 칩 {r}')
    await pg.evaluate("document.querySelector('#stage .tc .figchip').click()"); await pg.wait_for_timeout(200)
    ok(await pg.evaluate(f"({VIS})(document.querySelector('#stage .tc .figs'))"), 'D10 🖼 칩 → 그 카드 그림 펼침')
    await pg.keyboard.press('i'); ok(await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.figmode'))") == 'big', 'D10 I 순환 → 크게')
    # ---- D11 이 강의의 틀
    await pg.evaluate("localStorage.clear()"); await open_(pg, '#/OMS1/EXT/learn')
    ok(not await pg.evaluate("document.querySelector('.frame').classList.contains('fold')"), 'D11 첫 방문(✓ 0) → 틀 펼침')
    await pg.evaluate("document.querySelector('#t-EXT-0 .dn').click()"); await open_(pg, '#/OMS1/EXT/learn'); await pg.evaluate('scrollTo(0,0)'); await pg.wait_for_timeout(200)
    r = await pg.evaluate("[document.querySelector('.frame').classList.contains('fold'),Math.round(document.querySelector('#t-EXT-0').getBoundingClientRect().top),Math.round(document.querySelector('.frame').getBoundingClientRect().top)]")
    ok(r[0] and r[1] - r[2] <= 280 and r[1] <= 560, f'D11 카드 1 ✓ 뒤 두 번째 방문: 틀 접힘 · 첫 카드 top {r[1]} — 틀 시작 {r[2]}부터 {r[1] - r[2]} ≤ 280(옛 450 − 틀 시작 170 · ux4 B3-4 머리 kicker·h1이 커져 틀 시작이 내려감)')
    await pg.screenshot(path=J.TMP + '/ux2i_d11_fold_1280.png')
    await pg.evaluate("document.querySelector('.frtog').click()"); await open_(pg, '#/OMS1/EXT/learn')
    ok(not await pg.evaluate("document.querySelector('.frame').classList.contains('fold')"), 'D11 틀 펼치기 → LS frameOpen 기억')
    cj = await pg.evaluate("(()=>{const li=document.querySelector('.ftop li[data-cj]');li.querySelector('.tq').click();return li.dataset.cj})()"); await pg.wait_for_timeout(900)
    d = await pg.evaluate(f"Math.round(document.querySelector('#t-EXT-{cj}').getBoundingClientRect().top-document.querySelector('#dtabs').getBoundingClientRect().bottom)")
    ok(0 <= d <= 30, f'D11 ⭐ 많이 나온 순 줄 → 카드 {int(cj) + 1} ({d}px)')
    # ---- D12 JB 미리보기
    await open_(pg, '#/PHARM/HM/learn'); h0 = await pg.evaluate('location.hash')
    qid = await pg.evaluate("(()=>{const c=document.querySelector('#t-HM-4 .c-exam .jbchip');c.scrollIntoView({block:'center'});c.click();return c.dataset.go})()"); await pg.wait_for_timeout(300)
    r = await pg.evaluate(f"(()=>{{const v={VIS};const p=document.querySelector('#jbpeek');return [location.hash,v(p),!v(p.querySelector('.jpa')),p.querySelectorAll('.jpq .ln').length]}})()")
    ok(r[0] == h0 and r[1] and r[2] and r[3] >= 1, f'D12 ⭐ 칩 {qid} → 해시 그대로 · 미리보기 · 답 가림 {r[1:]}')
    await pg.screenshot(path=J.TMP + '/ux2i_d12_peek_1280.png')
    await pg.evaluate("document.querySelector('#jbpeek .jpshow').click()"); ok(await pg.evaluate(f"({VIS})(document.querySelector('#jbpeek .jpa'))"), 'D12 답 핵심 보기 → 열림')
    await pg.evaluate("document.querySelector('#jbpeek [data-jpmk=ng]').click()")
    mk = await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.mk.PHARM')||'{}')")
    ok(qid in (mk.get('ng') or {}), f'D12 ✗ → mk.PHARM.ng[{qid}]')
    await pg.keyboard.press('Escape'); ok(not await pg.evaluate(f"({VIS})(document.querySelector('#jbpeek'))"), 'D12 Esc → 닫힘')
    await pg.evaluate("document.querySelector('#t-HM-4 .c-exam .jbchip').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('#jbpeek [data-jpgo]').click()"); await pg.wait_for_timeout(1000)
    r = await pg.evaluate(f"[location.hash,document.querySelector('#retpill').classList.contains('on'),!!document.querySelector('#c-{qid}')]")
    ok(r[0].startswith('#/PHARM/HM/jb') and r[1] and r[2], f'D12 JB에서 풀기 → 기출 탭·↩ 알약 {r}')
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()

async def tablet(b, W, H):
    ctx = await b.new_context(viewport={'width': W, 'height': H}, has_touch=True); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    await open_(pg, '#/OMS1/EXT/learn')
    r = await pg.evaluate("[document.documentElement.scrollWidth-innerWidth,document.querySelectorAll('.exs').length]")
    ok(r[0] <= 1, f'{W}: 학습 탭 가로 밀림 {r[0]}px')
    await pg.evaluate("document.querySelector('#lmrev').click()"); await pg.wait_for_timeout(400)
    r = await pg.evaluate("[document.querySelector('#stage').classList.contains('review'),document.documentElement.scrollWidth-innerWidth,Math.round(document.querySelector('#t-EXT-1 .rvj [data-rv=o]').getBoundingClientRect().height)]")
    ok(r[0] and r[1] <= 1 and r[2] >= 36, f'{W}: ⚡ 복습 버튼 → 복습 보기 · 가로 밀림 {r[1]} · 알아요 높이 {r[2]}')
    await pg.evaluate('scrollTo(0,0)'); await pg.wait_for_timeout(200); await pg.screenshot(path=J.TMP + f'/ux2i_d02_review_{W}.png')
    await pg.evaluate("document.querySelector('#lmrev').click()")
    await pg.evaluate("document.querySelector('#t-EXT-0 .c-exam').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(200)
    b_ = await pg.evaluate("(()=>{const c=document.querySelector('#t-EXT-0 .c-exam .jbchip');const r=c.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()")
    await pg.touchscreen.tap(b_[0], b_[1]); await pg.wait_for_timeout(300)
    r = await pg.evaluate("(()=>{const p=document.querySelector('#jbpeek');const r=p.getBoundingClientRect();return [p.classList.contains('on'),Math.round(r.left),Math.round(r.right)]})()")
    ok(r[0] and r[1] >= 0 and r[2] <= W, f'{W}: ⭐ 칩 탭 → 미리보기 화면 안 {r}')
    await pg.screenshot(path=J.TMP + f'/ux2i_d12_peek_{W}.png'); await pg.keyboard.press('Escape')
    m = await pg.evaluate("(()=>{const b=document.querySelector('#t-EXT-0 .c-mem .memqz');b.scrollIntoView({block:'center'});const r=b.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2,Math.round(r.height)]})()")
    await pg.touchscreen.tap(m[0], m[1]); await pg.wait_for_timeout(200)
    ok(m[2] >= 36 and await pg.evaluate("document.querySelector('#t-EXT-0 .c-mem').classList.contains('memhide')"), f'{W}: ⚡ 가리기 탭({m[2]}px) → 그 블록 가림(ux4 B1-5 ○✕ 대신)')
    await pg.touchscreen.tap(m[0], m[1]); await pg.wait_for_timeout(150)
    await pg.screenshot(path=J.TMP + f'/ux2i_d03_mem_{W}.png')
    await open_(pg, '#/PHARM/HM/learn'); await pg.evaluate("document.querySelector('#lmcond').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('#t-HM-4').scrollIntoView()"); await pg.wait_for_timeout(200); await pg.screenshot(path=J.TMP + f'/ux2i_d01_cond_{W}.png')
    await pg.evaluate("document.querySelector('#lmcond').click()")
    ok(not errs, f'{W}: pageerror 0 {errs[:2]}')
    await ctx.close()

async def main():
    P = packs(); bad = []
    for s, p in P.items():
        for L in p['lect']:
            for tq in re.findall(r'<span class="tq">(.*?)</span></li>', L['head']):
                t = re.sub(r'<[^>]+>', '', tq)
                if re.search(r'\(탈\)|\(짤\)|\(복원 원문\)', t) or re.fullmatch(r'\s*(다음 중 )?옳(은|지 않은) 것을 고르시오\.?\s*', t): bad.append(f'{s}/{L["k"]}: {t[:40]}')
    ok(not bad, f'D11 6과목 ⭐ 많이 나온 순 (탈)·(짤)·(복원 원문)·발문만 {len(bad)}건 {bad[:3]}')
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await mac(b)
        for W, H in [(820, 1180), (1180, 820)]: await tablet(b, W, H)
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
