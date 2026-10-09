"""U24 회귀: '이 강의의 틀' 압축 — 820×1180에서 틀 높이(목차 제외 — 900px 이하 한 단, 항목은 두 줄 이내) ≤ 아이패드 세로 한 화면(고정 상단 막대·탭 줄·아래 도구 막대를 뺀
보이는 높이 — 틀 머리를 위로 맞추면 목차 앞까지가 한 화면에 다 보임; 옛 원고 때의 고정 800px은 📣 예고·강조 줄 수가 늘어난 새 원고에 맞지 않아 화면 기준으로 바꿈),
출제 경향은 접힘(summary = 한 줄)·📌 전략 줄은 보임, ⭐ 많이 나온 순 항목 수 = min(8, 강의 기출 수)(숨김 포함)·5개만 보임, 모든 ! 줄 글자가 틀 안 어딘가(📣 블록 또는 출처 줄)에 남음."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, re, html
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
TOOLS = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
SEP = re.compile(r'[\s/:：;·,—\-=→|•"“”\'‘’()]')
def notes_ok():
    for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
        p = (lambda t__: json.loads(t__[t__.index('JBLHUB.register(')+16:-2]))(open(J.DOCS + f'/packs/{s}.js', encoding='utf-8').read())
        for L in p['lect']:
            src = open(f'{TOOLS}/{s.lower()}/lec_{L["k"]}.txt', encoding='utf-8').read()
            ft = SEP.sub('', html.unescape(re.sub(r'<[^>]+>', '', L['head'])))
            for n0 in [l[1:].strip() for l in src.splitlines() if l.startswith('!')]:
              for n in re.split(r'(?<=\.) ', n0):   # 문장 단위(📣·출처 줄로 나뉘어 들어감)
                for chunk in re.split(r'\[\[[^\]]+\]\]|\{jb:[^}]+\}', re.sub(r'\*\*|==|\{r:|\{k:|\{n:|\{u:|\}', '', n)):
                    c = SEP.sub('', chunk)
                    if c and c not in ft: ok(False, f'{s}/{L["k"]} ! 줄 글자 누락: {chunk[:40]}'); break
    ok(True, '! 줄 글자 검사 끝')
JS = """()=>{const f=document.querySelector('#stage .frame');const t=f.querySelector('details.trend');const top=f.querySelectorAll('.ftop li');
const ol=f.querySelector('.outline');const olh=ol?ol.getBoundingClientRect().height:0;const ols=ol?[...ol.querySelectorAll('.ol')].filter(e=>e.getBoundingClientRect().height>72).length:0;   /* 목차는 900px 이하 한 단(V09) — 높이 예산에서 빼고, 항목 하나가 제목 한 줄 + 요지 두 줄(ux2 D11 line-clamp 2)을 넘지 않는지 따로 */
const cs=getComputedStyle(document.documentElement),kit=document.querySelector('#kit'),kr=kit&&kit.getBoundingClientRect(),kb=kr&&getComputedStyle(kit).position==='fixed'&&getComputedStyle(kit).visibility!=='hidden'&&kr.height>0?innerHeight-kr.top:0;
return {lim:Math.round(innerHeight-parseFloat(cs.getPropertyValue('--toph'))-parseFloat(cs.getPropertyValue('--tabh'))-kb),h:Math.round(f.getBoundingClientRect().height-olh),ol2:ols,trend:!!t&&!t.open&&t.querySelector('summary').innerText.length>10,strat:!!f.querySelector('.tstr')&&f.querySelector('.tstr').offsetHeight>0,
top:top.length,vis:[...top].filter(l=>l.offsetParent!==null).length,jb:(PACKS_J=null,0)}}"""
async def main():
    notes_ok()
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
            P = (lambda t__: json.loads(t__[t__.index('JBLHUB.register(')+16:-2]))(open(J.DOCS + f'/packs/{s}.js', encoding='utf-8').read())
            mx = 0; lim = 0
            for L in P['lect']:
                await pg.goto('about:blank'); await pg.goto(U + f'#/{s}/{L["k"]}/learn'); await pg.wait_for_timeout(450)
                r = await pg.evaluate(JS); mx = max(mx, r['h']); lim = r['lim']
                want = min(8, len(L['jb']))
                if r['h'] > r['lim'] or r['ol2'] or not r['trend'] or not r['strat'] or r['top'] != want or r['vis'] != min(5, want): ok(False, f'{s}/{L["k"]} {r} (⭐ 기대 {want})')
            ok(lim >= 900 and mx <= lim, f'{s} 틀 최대 높이 {mx}px ≤ 한 화면 {lim}px · 경향 접힘 · 📌 보임 · ⭐ 개수')
        await pg.goto('about:blank'); await pg.goto(U + '#/OMS1/DD1/learn'); await pg.wait_for_timeout(600)
        await pg.click('#stage .ftop [data-tmore]'); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("[...document.querySelectorAll('#stage .ftop li')].every(l=>l.offsetParent!==null)"), '⭐ 더 보기 → 전부 보임')
        await pg.screenshot(path=J.TMP + '/ux_u24_dd1_820.png')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
