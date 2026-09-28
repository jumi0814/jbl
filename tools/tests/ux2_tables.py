"""ux2 묶음 5(트랙B) 회귀 — 정리표·비교표·기출 한눈표 (E02~E12). 맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)
E02 정리표 요약(기본)·전체: 1280 WHT 문서 높이 ≤ 4,500 · 요약 행 높이 400 초과 0 · 요약↔전체 표시 수 같음·lost 0 · 820 WHT 카드 250~400
E03 WHT 행에 'Intrinsic'·'Extrinsic' · 세부 칸에 ' — ○' 같은 빈 기호 0(6과목)
E04 GERI OHQ .mn 배경 h0 ≠ h2 · '2회↑' → h0·h1 행 0개 보임 · 미출제 행 td 수 = 기출 행 td 수 − 1
E05 ★ 칸 문항 높이 ≤ 5줄 · ★ 칸 innerText가 '23년'처럼 연도로 시작 0 · 전체정리표(sum=1)가 정리표 탭 첫 요소 · 비교표에 중복 없음
E06 1280(사이드바 접힘)·1180 .men 영문 단어 중간 줄바꿈 0 · 긴 행 중간에서도 주제 div가 화면 안 · 강의 비교표 탭 끝 .nextl
(E07~E12는 아래에 이어 붙임) 스크린샷 work/_tmp/ux2i_e*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, re
from playwright.async_api import async_playwright
U = J.HUB_URL; NS = 'jblhub.v1.'; fails = []
SUBJ = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, sel='#stage'):
    await pg.goto('about:blank'); await pg.goto(U + h)
    try: await pg.wait_for_function(f"document.querySelector({json.dumps(sel)})&&window.__h", timeout=15000)
    except Exception: pass
    await pg.wait_for_timeout(350)
async def ls(pg, k): return json.loads(await pg.evaluate(f"localStorage.getItem('{NS}{k}')") or 'null')
VIS = "e=>!!e&&e.offsetParent!==null&&getComputedStyle(e).display!=='none'"
ROWS = "[...document.querySelectorAll('#stage table.mtx>tbody>tr:not(.grow)')]"
MIDBREAK = r"""(()=>{const bad=[];document.querySelectorAll('#stage .msum .men').forEach(m=>{const w=document.createTreeWalker(m,NodeFilter.SHOW_TEXT);let n,prev=null;const r=document.createRange();
 while(n=w.nextNode()){for(let i=0;i<n.nodeValue.length;i++){r.setStart(n,i);r.setEnd(n,i+1);const b=r.getClientRects()[0];if(!b)continue;const ch=n.nodeValue[i];
  if(prev&&b.top>prev.top+4&&/[a-z]/.test(prev.ch)&&/[a-z]/.test(ch))bad.push(m.textContent.slice(0,40));prev={top:b.top,ch};}}});return bad;})()"""
async def mark_words(pg, sel, n):
    """sel 안에서 낱말 n개에 형광펜(도구 막대 H 모드로 누르기)"""
    await pg.evaluate("document.querySelector('#k-h').click()")
    got = 0
    for i in range(n * 3):
        a = await pg.evaluate("""([sel,i])=>{const es=[...document.querySelectorAll(sel)].filter(e=>e.offsetParent!==null);let k=0;for(const e of es){const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){if(x.parentElement.closest('button,.noann,[data-rk]'))continue;const m=/[A-Za-z가-힣]{4,}/.exec(x.nodeValue);if(!m)continue;if(k++<i)continue;
          x.parentElement.scrollIntoView({block:'center'});const r=document.createRange();r.setStart(x,m.index+1);r.setEnd(x,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2];}}return null}""", [sel, i * 3])
        if not a: break
        await pg.mouse.click(a[0], a[1]); await pg.wait_for_timeout(60); got = await pg.evaluate("new Set([...document.querySelectorAll('#stage [data-rk]')].map(e=>e.dataset.g)).size")
        if got >= n: break
    await pg.evaluate("document.querySelector('#k-h').click()")
    return got

async def mac(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    # ---- E02
    await open_(pg, '#/CONS/WHT/sum', '#stage .msum')
    r = await pg.evaluate(f"[document.documentElement.scrollHeight,document.querySelector('#stage').classList.contains('sdfull'),Math.max(...{ROWS}.map(r=>r.offsetHeight)),document.body.classList.contains('sidefold')]")
    ok(r[0] <= 4500 and not r[1], f'E02 1280 WHT 정리표(요약) 문서 높이 {r[0]} ≤ 4500 (사이드바 자동 접힘 {r[3]})')
    ok(r[2] <= 400, f'E02 요약 모드 행 최대 높이 {r[2]} ≤ 400')
    await pg.screenshot(path=J.TMP + '/ux2i_e02_sum_1280.png')
    n0 = await mark_words(pg, '#stage .msum td.mk, #stage .msum .mfull, #stage .msum td.mnote', 4)
    # 세부 전체(.mfull) 안 낱말은 요약에서 숨으므로 전체 모드에서 칠함
    await pg.evaluate("document.querySelector('[data-mdense=f]').click()"); await pg.wait_for_timeout(150)
    n0 = await mark_words(pg, '#stage .msum .mfull', 6)
    a0 = await ls(pg, 'ann.CONS'); tot0 = sum(len(v) for v in a0.values())
    rows_marked = [k for k in a0 if k.endswith('~s')]
    ok(n0 >= 6 and rows_marked and all(k.endswith('~s') for k in a0), f'E01 정리표 표시 {n0}개는 행 aid(~s)에 저장 ({len(rows_marked)}행)')
    await pg.evaluate("document.querySelector('[data-mdense=s]').click()"); await pg.wait_for_timeout(150)
    ns = await pg.evaluate("new Set([...document.querySelectorAll('#stage [data-rk]')].map(e=>e.dataset.g)).size")
    await pg.evaluate("document.querySelector('[data-mdense=f]').click()"); await pg.wait_for_timeout(150)
    nf = await pg.evaluate("new Set([...document.querySelectorAll('#stage [data-rk]')].map(e=>e.dataset.g)).size")
    await open_(pg, '#/CONS/WHT/sum', '#stage .msum')
    a1 = await ls(pg, 'ann.CONS'); lost = sum(1 for v in a1.values() for o in v if o.get('lost'))
    ok(ns == nf == n0 and lost == 0 and sum(len(v) for v in a1.values()) == tot0, f'E02 요약↔전체 표시 수 {ns}={nf}={n0} · 새로고침 뒤 lost {lost}')
    ok(await ls(pg, 'sumdense') == 'f' and await pg.evaluate("document.querySelector('#stage').classList.contains('sdfull')"), 'E02 [전체] LS sumdense 유지')
    await pg.evaluate("document.querySelector('[data-mdense=s]').click()")
    b0 = await pg.evaluate("(()=>{const td=document.querySelector('#m-WHT-1 td.md');const f=td.querySelector('.mfull');const v0=f.offsetParent!==null;td.querySelector('.mdmore').click();return [v0,f.offsetParent!==null,td.querySelector('.sline').offsetParent!==null]})()")
    ok(b0 == [False, True, False], f'E02 요약에서 세부 ▸ → 그 자리 전체 펼침 {b0}')
    # ---- E03
    t = await pg.evaluate("document.querySelector('#m-WHT-1').textContent")
    ok('Intrinsic' in t and 'Extrinsic ○' in t, "E03 WHT 행 2 세부에 'Extrinsic ○'(열 이름)")
    bad = await pg.evaluate("""(()=>{const o=[];for(const s in __h.PACKS){__h.PACKS[s].lect.forEach(L=>{const d=document.createElement('div');d.innerHTML=L.sum;d.querySelectorAll('.msum .mfull .ci').forEach(c=>{const x=c.cloneNode(true);x.querySelectorAll('.csx').forEach(e=>e.remove());const t=x.textContent,i=t.indexOf(' — ');if(i>0&&/^(—|○|×)\\s*(\\/|$)/.test(t.slice(i+3)))o.push(s+'/'+L.k+': '+t.slice(0,60));});});}return o})()""")
    ok(not bad, f'E03 6과목 세부 칸 빈 기호 줄 {len(bad)} {bad[:2]}')
    # ---- E04
    await open_(pg, '#/GERI/OHQ/sum', '#stage .msum')
    r = await pg.evaluate("(()=>{const bg=s=>{const e=document.querySelector('#stage .msum tr.'+s+' .mn');return e?getComputedStyle(e).backgroundColor:null};return [bg('h0'),bg('h2')]})()")
    ok(r[0] and r[1] and r[0] != r[1], f'E04 OHQ .mn 배경 h0 {r[0]} ≠ h2 {r[1]}')
    tdc = await pg.evaluate("(()=>{const h0=document.querySelector('#stage .msum tr.h0[data-aid]'),h2=document.querySelector('#stage .msum tr.h2[data-aid]');return [h0&&h0.querySelectorAll(':scope>td').length,h2&&h2.querySelectorAll(':scope>td').length]})()")
    ok(tdc[0] == tdc[1] - 1, f'E04 미출제 행 td {tdc[0]} = 기출 행 td {tdc[1]} − 1')
    await pg.evaluate("document.querySelector('[data-mfilt=rep2]').click()"); await pg.wait_for_timeout(100)
    r = await pg.evaluate(f"(()=>{{const v={VIS};return [[...document.querySelectorAll('#stage .msum tr.h0,#stage .msum tr.h1')].filter(v).length,[...document.querySelectorAll('#stage .msum tr.h2')].filter(v).length,[...document.querySelectorAll('#stage .msum tr.grow')].filter(v).length]}})()")
    ok(r[0] == 0 and r[1] > 0, f"E04 '2회↑' → h0·h1 보임 {r[0]} · h2 {r[1]} · 묶음 줄 {r[2]}")
    await pg.screenshot(path=J.TMP + '/ux2i_e04_rep2_1280.png')
    await pg.evaluate("document.querySelector('[data-mfilt=hit]').click()"); await pg.wait_for_timeout(100)
    r = await pg.evaluate(f"(()=>{{const v={VIS};return [[...document.querySelectorAll('#stage .msum tr.h0')].filter(v).length,[...document.querySelectorAll('#stage .msum tr.h1,#stage .msum tr.h2')].filter(v).length]}})()")
    ok(r[0] == 0 and r[1] > 0, f"E04 '기출 나온 주제만' → h0 {r[0]} · 기출 {r[1]}")
    # ---- E05
    bad, tall, n = [], [], 0
    for s in SUBJ:
        for k in await pg.evaluate(f"__h.PACKS['{s}'].lect.map(L=>L.k)"):
            await pg.evaluate(f"__h.openDoc('{s}','{k}','sum')"); await pg.wait_for_timeout(60)
            r = await pg.evaluate("(()=>{const o=[],t=[];let n=0;document.querySelectorAll('#stage .msum td.mt').forEach(td=>{n++;const x=td.innerText.trim();if(/^\\d{2}(·\\d{2})*년/.test(x))o.push(x.slice(0,30));td.querySelectorAll('.mex').forEach(m=>{if(m.offsetParent===null)return;const lh=parseFloat(getComputedStyle(m.querySelector('.mexb')).lineHeight)||20;if(m.offsetHeight>lh*5+2)t.push(td.closest('tr').id+':'+m.offsetHeight);});});return [o,t,n]})()")
            bad += [f'{s}/{k} {x}' for x in r[0]]; tall += [f'{s}/{x}' for x in r[1]]; n += r[2]
    ok(not bad, f'E05 ★ 칸 {n}개 중 innerText가 연도로 시작 {len(bad)} {bad[:2]}')
    ok(not tall, f'E05 ★ 문항 높이 5줄 초과 {len(tall)} {tall[:3]}')
    await open_(pg, '#/CONS/WHT/sum', '#stage .msum')
    r = await pg.evaluate("(()=>{const f=document.querySelector('#stage').firstElementChild;const aids=[...document.querySelectorAll('#sumtop [data-aid]')].map(e=>e.dataset.aid);return [f&&f.id,aids]})()")
    ok(r[0] == 'sumtop' and len(r[1]) == 3, f'E05 WHT 정리표 탭 첫 요소 = 전체정리표({r[0]}, 표 {len(r[1])}개)')
    await pg.evaluate("document.querySelector('#sumtop [data-sttab=\"0\"]').click()"); await pg.wait_for_timeout(200)
    ok(await pg.evaluate("document.querySelector('#sumtop .stbl[data-sti=\"0\"]').offsetParent!==null&&document.querySelector('#sumtop .stbl[data-sti=\"1\"]').offsetParent===null"), 'E05 전체정리표 칩 ① → 그 표만 펼침')
    await pg.screenshot(path=J.TMP + '/ux2i_e05_sumtop_1280.png')
    dup = await pg.evaluate("""(a=>{__h.openDoc('CONS','_tbl');const t=[...document.querySelectorAll('#stage [data-aid]')].map(e=>e.dataset.aid);__h.openDoc('CONS','WHT','tbl');const l=[...document.querySelectorAll('#stage [data-aid]')].map(e=>e.dataset.aid);return a.filter(x=>t.includes(x)||l.includes(x))})""" + f"({json.dumps(r[1])})")
    ok(not dup, f'E05 전체정리표는 비교표(과목·강의)에 없음 {dup}')
    # ---- E06 (1280 사이드바 접힘)
    await open_(pg, '#/CONS/WHT/sum', '#stage .msum')
    br = []
    for s in SUBJ:
        for k in await pg.evaluate(f"__h.PACKS['{s}'].lect.map(L=>L.k)"):
            await pg.evaluate(f"__h.openDoc('{s}','{k}','sum')"); await pg.wait_for_timeout(50)
            br += await pg.evaluate(MIDBREAK)
    ok(not br and await pg.evaluate("document.body.classList.contains('sidefold')"), f'E06 1280 .men 영문 단어 중간 줄바꿈 {len(br)} {br[:3]}')
    await open_(pg, '#/CONS/WHT/sum', '#stage .msum')
    await pg.evaluate("document.querySelector('[data-mdense=f]').click()"); await pg.wait_for_timeout(150)
    r = await pg.evaluate("(async()=>{const tr=[...document.querySelectorAll('#stage table.mtx>tbody>tr:not(.grow)')].sort((a,b)=>b.offsetHeight-a.offsetHeight)[0];const R=tr.getBoundingClientRect();window.scrollTo(0,scrollY+R.top+R.height*.6-450);await new Promise(r=>setTimeout(r,150));const d=tr.querySelector('.mtw').getBoundingClientRect(),t=tr.getBoundingClientRect();return [Math.round(d.top),Math.round(d.bottom),innerHeight,Math.round(t.top),Math.round(t.height)]})()")
    ok(r[3] < 0 and r[0] >= 0 and r[1] <= r[2], f'E06 전체 모드 긴 행({r[4]}px) 중간(행 top {r[3]})에서 주제 div 화면 안 (top {r[0]}·bottom {r[1]})')
    await pg.evaluate("document.querySelector('[data-mdense=s]').click()")
    await pg.screenshot(path=J.TMP + '/ux2i_e06_sticky_1280.png')
    await open_(pg, '#/CONS/WHT/tbl', '#stage .tblwrap')
    ok(await pg.evaluate("!!document.querySelector('#stage .nextl')"), 'E06 강의 비교표 탭 끝 .nextl')
    ok(not errs, f'맥 pageerror 0 {errs[:2]}')
    await ctx.close()

async def ipad(b, w, h):
    tag = 'ipad' if w < 1000 else 'ipadl'
    ctx = await b.new_context(viewport={'width': w, 'height': h}, has_touch=True); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    await open_(pg, '#/CONS/WHT/sum', '#stage .msum')
    if w < 1000:
        hs = await pg.evaluate(f"{ROWS}.map(r=>r.offsetHeight)")
        ok(min(hs) >= 250 and max(hs) <= 400, f'E02 820 WHT 카드 높이 {min(hs)}~{max(hs)} (250~400)')
        r = await pg.evaluate("(()=>{const td=document.querySelector('#m-WHT-1 td.md');const v0=[td.querySelector('.sline'),td.querySelector('.mfull')].map(e=>e.offsetParent!==null);td.querySelector('.mdmore').click();return [v0,td.querySelector('.mfull').offsetParent!==null,td.querySelector('.mdmore').textContent]})()")
        ok(r[0] == [False, False] and r[1], f"E02 820 카드형: 세부 접힘 → '세부 n줄 ▸' 누르면 펼침 {r}")
    else:
        br = await pg.evaluate(MIDBREAK)
        ok(not br, f'E06 1180 .men 영문 단어 중간 줄바꿈 {len(br)} {br[:3]}')
    await pg.screenshot(path=J.TMP + f'/ux2i_e02_sum_{tag}.png')
    ok(await pg.evaluate('document.documentElement.scrollWidth-innerWidth') <= 1, f'{tag} 정리표 가로 밀림 0')
    ok(not errs, f'{tag} pageerror 0 {errs[:2]}')
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await mac(b); await ipad(b, 820, 1180); await ipad(b, 1180, 820)
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else 'FAIL'); _sys.exit(1 if fails else 0)
