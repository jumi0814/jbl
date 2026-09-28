"""U06 회귀: 🖍 내 표시 모아보기 — ⚠ 위치 잃음 절(옛 카드 키·옛 제목·[이 과목에서 찾기]·[버리기]+자동 백업), 📝 메모 절, 칩 → 그 표시 묶음이 화면 가운데·깜빡임
(JB 답 안의 표시면 답을 열어 줌). 맥 1280×900 + 아이패드 세로 820×1180. 스크린샷 work/_tmp/ux_marks_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; KEY = 'jblhub.v1.ann.CONS'; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1100):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
UNIQ = """(sel)=>{const B=document.querySelector(sel);if(!B)return null;const txt=B.textContent;const L=[...B.querySelectorAll(%s)];for(const e of L){for(const w of e.textContent.split(/\\s+/)){const x=w.replace(/[^가-힣A-Za-z0-9]/g,'');if(x.length>=3&&txt.split(x).length===2)return [B.dataset.aid,x];}}return null;}"""
CENTER = """()=>{const e=document.querySelector('#stage .mkflash');if(!e)return null;const r=e.getBoundingClientRect();const c=Math.round((r.top+r.bottom)/2-innerHeight/2);
  const atEnd=Math.ceil(scrollY+innerHeight)>=document.documentElement.scrollHeight-1,vis=r.top>=0&&r.bottom<=innerHeight;return atEnd&&vis&&c>0?0:c;}"""   # 문서 바닥이라 더 못 내리면 화면 안에 보이는 것으로 충분
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
    print(f'== {tag}')
    await open_(pg, '#/CONS/CRK/learn'); await pg.evaluate('localStorage.clear();sessionStorage.clear()'); await open_(pg, '#/CONS/CRK/learn')
    # 픽스처: 강의 가운데쯤 카드(끝 카드는 문서 바닥이라 가운데로 못 옴)의 본문 줄(li·div.li)에서 문서 안 한 번뿐인 낱말
    nc = await pg.evaluate("document.querySelectorAll('#stage .tc').length"); a1 = None
    for k in sorted(range(1, nc + 1), key=lambda k: abs(k - (nc + 1) // 2)):
        a1 = await pg.evaluate(UNIQ % "'.tbody li,.tbody div.li'", f'#stage .tc:nth-of-type({k})')
        if a1: break
    await open_(pg, '#/CONS/_jb/_jb')
    a2 = None
    for n in range(8, 40):
        a2 = await pg.evaluate(UNIQ % "'.jbans .ln'", f'#cards .qc.tA:nth-of-type({n})')
        if a2: break
    ok(bool(a1 and a2), f'표시할 글자 준비 {a1} {a2}')
    await pg.evaluate("""([k,a1,a2])=>{const a={};a[a1[0]]=[{t:'h',x:a1[1],i:0,c:'g'}];a[a2[0]]=[{t:'b',x:a2[1],i:0}];a['CONS:CRK:oldcardtitle_abcdef']=[{t:'h',x:'옛 카드의 표시',i:0,c:'y'}];
      localStorage.setItem(k,JSON.stringify(a));localStorage.setItem('jblhub.v1.memo.CONS.WHT',JSON.stringify('미백 메모 — 과산화수소 농도 외우기'));}""", [KEY, a1, a2])
    await open_(pg, '#/CONS/_marks/_marks')
    head = await pg.inner_text('#stage .mk-sum'); ok('표시 3' in head.replace('\n', ' ') and '위치 잃음 1' in head.replace('\n', ' ') and '메모 1' in head.replace('\n', ' '), f'머리 문구 ({head!r})')
    lost = await pg.inner_text('#mk-lost'); ok('옛 카드의 표시' in lost and '이 과목에서 찾기' in lost and '버리기' in lost, '⚠ 위치 잃음 절: 표시 텍스트·버튼')
    memo = await pg.inner_text('#mk-memo'); ok('미백 메모' in memo and '열기' in memo, '📝 메모 절')
    await pg.screenshot(path=J.TMP + f'/ux_marks_page_{tag}.png', full_page=True)
    # 칩 → 정리본 카드 안 표시 가운데·깜빡임
    await pg.evaluate("(aid)=>document.querySelector('#stage button.mk[data-mkgo=\"'+aid+'\"]').click()", a1[0]); await pg.wait_for_timeout(500)
    c = await pg.evaluate(CENTER); ok(c is not None and abs(c) <= 60, f'칩 → 형광펜 표시 화면 가운데·깜빡임 ({c})')
    await pg.screenshot(path=J.TMP + f'/ux_marks_jump_{tag}.png')
    await pg.go_back(); await pg.wait_for_timeout(700)
    await pg.evaluate("(aid)=>document.querySelector('#stage button.mk[data-mkgo=\"'+aid+'\"]').click()", a2[0]); await pg.wait_for_timeout(500)
    c = await pg.evaluate(CENTER); op = await pg.evaluate("(aid)=>{const e=[...document.querySelectorAll('#stage [data-aid]')].find(x=>x.dataset.aid===aid);return !!(e&&e.classList.contains('open'))}", a2[0])
    ok(c is not None and abs(c) <= 60 and op, f'칩 → JB 답 안 빈칸: 답 열고 가운데 ({c}, open={op})')
    await pg.go_back(); await pg.wait_for_timeout(700)
    # [이 과목에서 찾기]
    await pg.evaluate("document.querySelector('#mk-lost [data-lostfind]').click()"); await pg.wait_for_timeout(700)
    ok((await pg.evaluate('location.hash')).startswith('#/?q=') and '&s=CONS' in await pg.evaluate('location.hash') and await pg.evaluate("!document.querySelector('#home').hidden"), '[이 과목에서 찾기] → 과목 한정 검색')
    await pg.go_back(); await pg.wait_for_timeout(700)
    # [버리기] — 자동 백업 한 건 뒤 삭제
    nb0 = await pg.evaluate("__h.bkList().then(L=>L.length)")
    await pg.evaluate("document.querySelector('#mk-lost [data-lostdrop]').click()"); await pg.wait_for_timeout(500)
    await pg.wait_for_timeout(300); nb1 = await pg.evaluate("__h.bkList().then(L=>L.length)")
    why = await pg.evaluate("__h.bkList().then(L=>{L.sort((a,b)=>b.at-a.at);return L[0]&&L[0].why})")   # 버리기 전 백업은 보호 칸(p0~2 — F3)
    ann = json.loads(await pg.evaluate(f"localStorage.getItem('{KEY}')"))
    ok(nb1 == nb0 + 1 and why == '위치 잃은 표시 버리기' and 'CONS:CRK:oldcardtitle_abcdef' not in ann and len(ann) == 2, f'[버리기] 자동 백업 {nb0}→{nb1} ({why}) 후 삭제')
    ok(await pg.evaluate("!document.querySelector('#mk-lost')") and '위치 잃음 0' in (await pg.inner_text('#stage .mk-sum')).replace('\n', ' '), '버린 뒤 위치 잃음 0')
    await pg.evaluate("document.querySelector('#mk-memo [data-memoopen]').click()"); await pg.wait_for_timeout(600)
    ok(await pg.evaluate("location.hash.startsWith('#/CONS/WHT/') && document.querySelector('#memo').classList.contains('on') && document.querySelector('#memota').value.includes('미백 메모')"), '메모 [열기] → 그 문서·메모 창')
    ok(not errs, f'pageerror 0 ({errs[:2]})')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 820, 'height': 1180}, True, 'ipp')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
