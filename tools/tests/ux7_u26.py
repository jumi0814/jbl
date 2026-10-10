"""U26 회귀(10-10): 25 → 26 바뀐 곳 표시({u:}·@UPD·'26에서 빠짐')가 화면에 그대로 나오는지 — 팩 lect[].upd > 0 인 강의 전부.
- 학습 화면: article.tc.u26c 수 = lect.upd · 그 카드마다 머리 칩 '🆕 26 바뀜' 보임 · NEW 26 배지(span.u26/u26p ::before)가 있음
- 강의 틀 제목 줄 알약(details.c-upd): 처음엔 접힘 → 누르면 펼침 · 안의 카드 바로가기(button.ucj) 수 = lect.upd · 하나 누르면 그 카드로 감
- '🆕 26 바뀐 카드만' 거르기: 보이는 카드 수 = lect.upd
- 원고에 '26에서 빠짐'이 있으면 span.gone26 이 있고 글자색이 본문과 다름(회색)
- 과목 홈 강의 카드 '🆕 26 바뀐 카드 n' = lect.upd · pageerror 0
- 10-10 26 수업 강조 {e:…}: article.tc.e26c 수 = lect.emp · 머리 칩 '26 강조' 보임 · 배지 글자 '26 강조'(NEW 26과 다름 — 색도 다름) · '26 강조 카드만' 거르기 · 알약 안 강조 카드 바로가기(button.ecj) 수 = emp · 과목 홈 '26 강조 카드 n' · 26 새 강의(lect.new26)는 과목 홈 'NEW 26 강의' 칩"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
TOOLS = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
SIDS = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def pack(s):
    t = open(J.DOCS + f'/packs/{s}.js', encoding='utf-8').read()
    return json.loads(t[t.index('JBLHUB.register(') + 16:-2])
LEARN = """()=>{const st=document.querySelector('#stage');const U=[...st.querySelectorAll('article.tc.u26c')];
const vis=e=>!!e&&e.offsetParent!==null&&getComputedStyle(e).display!=='none';
const bad=U.filter(c=>!vis(c.querySelector('.chip.u26chip'))).map(c=>c.id);
const badge=[...st.querySelectorAll('.u26,.u26p')].filter(e=>!e.classList.contains('demo')).map(e=>getComputedStyle(e,'::before').content).filter(x=>/26/.test(x)).length;
const E=[...st.querySelectorAll('article.tc.e26c')],ebad=E.filter(c=>!vis(c.querySelector('.chip.e26chip'))).map(c=>c.id);
const eb=[...st.querySelectorAll('.u26.e26,.u26p.e26p')].filter(e=>!e.classList.contains('demo')),ebadge=eb.map(e=>getComputedStyle(e,'::before').content).filter(x=>/강조/.test(x)).length;
const ub=[...st.querySelectorAll('.u26:not(.e26),.u26p:not(.e26p)')].filter(e=>!e.classList.contains('demo'))[0];
const ecol=eb[0]?getComputedStyle(eb[0],'::before').backgroundColor:'',ucol=ub?getComputedStyle(ub,'::before').backgroundColor:'';
const pill=st.querySelector('.frt details.c-upd'),g=[...st.querySelectorAll('.gone26')].filter(e=>!e.closest('.fun'));
const body=getComputedStyle(st.querySelector('article.tc .li, article.tc li')||st).color;
return {u:U.length,bad,badge,pill:!!pill,open:pill?pill.open:null,ucj:pill?pill.querySelectorAll('button.ucj:not(.ecj)').length:0,ecj:pill?pill.querySelectorAll('button.ecj').length:0,e:E.length,ebad,ebadge,ecol,ucol,gone:g.length,goneGray:g.every(e=>getComputedStyle(e).color!==body)}}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        nlec = 0
        for s in SIDS:
            P = pack(s); ups = [L for L in P['lect'] if L.get('upd') or L.get('emp')]
            for L in ups:
                k = L['k']; nlec += 1
                src = open(f'{TOOLS}/{s.lower()}/lec_{k}.txt', encoding='utf-8').read()
                await pg.goto('about:blank'); await pg.goto(U + f'#/{s}/{k}/learn'); await pg.wait_for_timeout(500)
                r = await pg.evaluate(LEARN)
                await pg.evaluate("(()=>{const c=document.querySelector('#stage article.tc');if(c)c.scrollIntoView();})()"); await pg.wait_for_timeout(300)
                await pg.evaluate("(()=>{const b=document.getElementById('lmcur');if(b)b.click();})()"); await pg.wait_for_timeout(250)   # 10-10 카드 목록 메뉴 ⭐ 옆 NEW 26·26 강조(QA 40)
                mb = await pg.evaluate("({u:document.querySelectorAll('#lpop small.lpu').length,e:document.querySelectorAll('#lpop small.lpe').length,a25:document.querySelectorAll('#stage .also25').length})")
                await pg.evaluate("document.querySelector('#lpop')&&document.querySelector('#lpop').classList.remove('on')")
                ok(mb['u'] == (L.get('upd') or 0) and mb['e'] == (L.get('emp') or 0), f"{s}/{k} 카드 목록 메뉴 NEW 26 {mb['u']} = upd {L.get('upd')} · 26 강조 {mb['e']} = emp {L.get('emp')}")
                if re.search(r'\(25(?:년도)?에도 (?:같이 )?강조', src): ok(mb['a25'] > 0, f"{s}/{k} '(25년도에도 강조함)' 회색 덧말 {mb['a25']}")
                if L.get('emp'): ok(r['e'] == L['emp'] and not r['ebad'] and r['ebadge'] > 0 and r['ecj'] == L['emp'] and (not r['ucol'] or r['ecol'] != r['ucol']), f"{s}/{k} 26 강조 카드 {r['e']} = emp {L['emp']} · 칩 안 보임 {r['ebad'][:3]} · '26 강조' 배지 {r['ebadge']} · 바로가기 {r['ecj']} · 색 {r['ecol']} ≠ {r['ucol']}")
                if not L.get('upd'): continue
                ok(r['u'] == L['upd'] and not r['bad'] and r['badge'] > 0, f"{s}/{k} 26 바뀐 카드 {r['u']} = upd {L['upd']} · 칩 안 보임 {r['bad'][:3]} · NEW 26 배지 {r['badge']}")
                ok(r['pill'] and r['open'] is False and r['ucj'] == L['upd'], f"{s}/{k} 알약 있음·처음 접힘 {r['open'] is False} · 바로가기 {r['ucj']}")
                if '26에서 빠' in src: ok(r['gone'] > 0 and r['goneGray'], f"{s}/{k} 회색 '26에서 빠짐' {r['gone']}")
                if not r['pill']: continue
                await pg.click('#stage .frt details.c-upd > summary'); await pg.wait_for_timeout(150)
                op = await pg.evaluate("document.querySelector('#stage .frt details.c-upd').open")
                tgt = await pg.evaluate("(()=>{const b=document.querySelector('#stage .frt details.c-upd button.ucj:not(.ecj)');return b?b.dataset.scroll:''})()")
                if tgt:
                    await pg.click('#stage .frt details.c-upd button.ucj:not(.ecj)'); await pg.wait_for_timeout(500)
                    y = await pg.evaluate(f"(()=>{{const e=document.getElementById('{tgt}');return e?Math.round(e.getBoundingClientRect().top):-9999}})()")
                else: y = -9999
                ok(op and -50 <= y <= 600, f"{s}/{k} 알약 펼침 {op} · 바로가기 → 카드 위치 {y}px")
                await pg.goto('about:blank'); await pg.goto(U + f'#/{s}/{k}/learn'); await pg.wait_for_timeout(450)
                await pg.click('#stage [data-filt="u26"]'); await pg.wait_for_timeout(200)
                nv = await pg.evaluate("[...document.querySelectorAll('#stage article.tc')].filter(c=>getComputedStyle(c).display!=='none').length")
                ok(nv == L['upd'], f"{s}/{k} '🆕 26 바뀐 카드만' 보이는 카드 {nv} = {L['upd']}")
                await pg.click('#stage [data-filt="u26"]'); await pg.wait_for_timeout(100)   # 거르기 끔(다음 강의에 남지 않게)
            if ups:
                await pg.goto('about:blank'); await pg.goto(U + f'#/{s}/_home/_home'); await pg.wait_for_timeout(700)
                h = await pg.evaluate("Object.fromEntries([...document.querySelectorAll('.lcard[data-d]')].map(c=>[c.dataset.d,c.textContent]))")
                miss = [L['k'] for L in ups if L.get('upd') and f"🆕 26 바뀐 카드 {L['upd']}" not in h.get(L['k'], '') or L.get('emp') and f"26 강조 카드 {L['emp']}" not in h.get(L['k'], '')]
                ok(not miss, f"{s} 과목 홈 '🆕 26 바뀐 카드 n'·'26 강조 카드 n' — 틀린 강의 {miss}")
            nw = [L['k'] for L in P['lect'] if L.get('new26')]
            if nw:
                await pg.goto('about:blank'); await pg.goto(U + f'#/{s}/_home/_home'); await pg.wait_for_timeout(700)
                hn = await pg.evaluate("[...document.querySelectorAll('.lcard[data-d]')].filter(c=>c.querySelector('.lnew26')).map(c=>c.dataset.d)")
                ok(sorted(hn) == sorted(nw), f"{s} 과목 홈 'NEW 26 강의' 칩 {hn} = {nw}")
        ok(nlec > 0, f'26 바뀐 강의 {nlec}개 확인')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
