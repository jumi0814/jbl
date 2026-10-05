"""U23 회귀: 정리본 렌더 — 🔑 상자 평균 높이 ≤ 140px(과목별, 1280), 첫 자식이 목록인 li 0, 조각별 형광 3개↑ 연속 목록 0,
짧은 나열 가로 흐름(ul.kflow)·형광 블록(.hlblock) 존재, ux2 D09 중앙값 22자 이하 세로 목록 0. 글자 불변은 tools/tests/card_text.py(--save 전/후)로."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
JS = """()=>{const st=document.querySelector('#stage');const k=[...st.querySelectorAll('.c-key')].map(e=>e.getBoundingClientRect().height);
const orphan=[...st.querySelectorAll('li')].filter(l=>l.firstElementChild&&/^(UL|OL)$/.test(l.firstElementChild.tagName)&&l.firstChild===l.firstElementChild).length;
let run3=0;st.querySelectorAll('ul,ol').forEach(u=>{let r=0;for(const li of u.children){const h=li.querySelector(':scope>.hl');if(h&&h.textContent.trim()===li.textContent.trim())r++;else r=0;if(r>=3){run3++;break;}}});
let vshort=0;const vs=[];st.querySelectorAll('.tc ul,.tc ol').forEach(u=>{if(u.closest('.c-mem')||u.classList.contains('exlist')||!u.offsetParent)return;const lis=[...u.children].filter(x=>x.tagName==='LI'&&x.offsetParent);if(lis.length<3)return;
 const ls=lis.map(x=>x.innerText.replace(/\\s+/g,' ').trim().length).sort((a,b)=>a-b);if(ls[ls.length>>1]>22)return;if(lis.filter(x=>/ = | → |: /.test(x.innerText)).length*2>=lis.length)return;   /* 10-04 사용자 줄바꿈 전수: '사실 문장'(=·→·:) 조각은 짧아도 한 줄씩 — 세로가 맞음 */const L=lis.map(x=>Math.round(x.getBoundingClientRect().left));if(L.every(x=>x===L[0])&&getComputedStyle(lis[0]).display!=='inline'){vshort++;vs.push(u.textContent.slice(0,40));}});   /* ux2 D09 중앙값 22자 이하 세로 목록 */
return {n:k.length,sum:k.reduce((a,b)=>a+b,0),orphan,run3,flow:st.querySelectorAll('ul.kflow').length,blk:st.querySelectorAll('.hlblock,li.hlb').length,vshort,vs};}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        tot = {'flow': 0, 'blk': 0}; vtot = 0
        for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
            await pg.goto('about:blank'); await pg.goto(U + f'#/{s}/_home/_home'); await pg.wait_for_timeout(700)
            ks = await pg.evaluate("PACKS_KEYS=[...document.querySelectorAll('.lcard')].map(b=>b.dataset.d)")
            n = sm = 0
            for k in ks:
                await pg.goto('about:blank'); await pg.goto(U + f'#/{s}/{k}/learn'); await pg.wait_for_timeout(450)
                r = await pg.evaluate(JS); n += r['n']; sm += r['sum']; tot['flow'] += r['flow']; tot['blk'] += r['blk']
                if r['orphan'] or r['run3']: ok(False, f'{s}/{k} 목록만 든 li {r["orphan"]} · 형광 3연속 {r["run3"]}')
                if r['vshort']: ok(False, f'{s}/{k} 중앙값 22자 이하 세로 목록 {r["vshort"]}개 {r["vs"][:2]}')   # ux2 D09
                vtot += r['vshort']
            ok(n and sm / n <= 140, f'{s} 🔑 상자 평균 높이 {round(sm / max(n, 1))}px ≤ 140')
        ok(vtot == 0, f'중앙값 22자 이하 세로 목록 {vtot}개 (ux2 D09 — 격자·가로 흐름)')
        ok(tot['flow'] > 0 and tot['blk'] > 0, f'가로 흐름 {tot["flow"]} · 형광 블록 {tot["blk"]}')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
