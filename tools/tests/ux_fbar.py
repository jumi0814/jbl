"""10-24 상단 막대 정리 회귀(사용자 '그림빵 풀기 상단메뉴처럼 예상문제·jb문제 탭 상단 메뉴 구조화 · jb는 연도별·순서 정렬은 남기고 짤 탈은 정렬 필터나 그런곳에서 합치기 · 예상문제는 강의별로').
① JB 막대 첫 줄 = 교수·연도 │ 상태 │ 정렬·필터 ▾ │ 한 장씩·답 펼치기 — 짤·탈은 첫 줄에 없고 [필터 ▾] 안 · 짤 켜면 '필터 1' · 탈로 거른 카드는 모두 탈
② 예상(과목) 막대 맨 앞 = 강의 ▾ · 고르면 그 강의 문제만(다른 강의 머리 숨김) · 새로고침 뒤에도 그대로 · '전체 보기'로 풀림
③ 1440에서 JB·예상·그림빵 막대 모두 한 줄 · 393 폰에서 고르기 칸이 쪼그라들지 않음(≥80px) · 페이지 오류 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
LINES = """(sel=>{const b=document.querySelector(sel);if(!b)return -1;const K=[...b.children].filter(e=>e.offsetParent&&!e.matches('.sp,.bdv'));const L=[];K.forEach(e=>{const r=e.getBoundingClientRect(),m=(r.top+r.bottom)/2;if(!L.some(x=>Math.abs(x-m)<12))L.push(m);});return L.length;})"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1440, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(U + '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
        # ① JB
        await pg.goto(U + '#/PHARM/_jb/_jb'); await pg.wait_for_timeout(1500)
        b1 = await pg.evaluate("[...document.querySelectorAll('#jbbar .b1 > *')].filter(e=>e.offsetParent).map(e=>e.id||e.className)")
        ok(b1[:2] == ['fprof', 'fyr'] and 'fsort' in b1 and 'fexp' in b1 and b1[-2:] == ['fone', 'frev'], f'① JB 첫 줄 순서 {b1}')
        ok(not await pg.evaluate("[...document.querySelectorAll('#jbbar .b1 [data-stf]')].length"), '① 짤·탈은 첫 줄에 없음')
        await pg.click('#fexp'); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("!!document.querySelector('#jbmore [data-stf=tt]').offsetParent"), '① [필터 ▾] 안에 짤·탈')
        await pg.click('#jbmore [data-stf=tt]'); await pg.wait_for_timeout(400)
        lab = await pg.inner_text('#fexp'); vis = await pg.evaluate("[...document.querySelectorAll('#cards .qc')].filter(c=>c.offsetParent)")
        ok('1' in lab, f'① 짤·탈을 켜면 필터 수 표시 {lab!r}')
        tt = await pg.evaluate("(()=>{const V=[...document.querySelectorAll('#cards .qc')].filter(c=>c.offsetParent);return [V.length,V.filter(c=>c.querySelector('.chip.tt')).length]})()")
        ok(tt[0] > 0 and tt[0] == tt[1], f'① 탈로 거른 카드 = 모두 탈 {tt}')
        await pg.click('#jbmore [data-stf=tt]'); await pg.wait_for_timeout(300)
        ok('1' not in await pg.inner_text('#fexp'), '① 다시 누르면 풀림')
        # ② 예상 강의
        await pg.goto('about:blank'); await pg.goto(U + '#/PHARM/_pred/_pred'); await pg.wait_for_timeout(1500)
        first = await pg.evaluate("(document.querySelector('#ppills').firstElementChild||{}).id")
        ok(first == 'plec', f'② 예상 막대 맨 앞 = 강의 고르기 ({first})')
        opts = await pg.evaluate("[...document.querySelectorAll('#plec option')].map(o=>o.value).filter(Boolean)")
        k = opts[1] if len(opts) > 1 else opts[0]
        await pg.select_option('#plec', k); await pg.wait_for_timeout(500)
        r = await pg.evaluate(f"(()=>{{const V=[...document.querySelectorAll('#stage .pc:not(.px)')].filter(c=>c.offsetParent);const H=[...document.querySelectorAll('#stage h3.pgh')].filter(h=>!h.hidden);return [V.length,V.every(c=>c.dataset.lk==='{k}'),H.length]}})()")
        ok(r[0] > 0 and r[1] and r[2] == 1, f'② 고른 강의 문제만 · 머리 1개 {r}')
        await pg.reload(); await pg.wait_for_timeout(1800)
        r2 = await pg.evaluate(f"[document.querySelector('#plec').value,[...document.querySelectorAll('#stage .pc:not(.px)')].filter(c=>c.offsetParent).every(c=>c.dataset.lk==='{k}')]")
        ok(r2 == [k, True], f'② 새로고침 뒤에도 그대로 {r2}')
        await pg.select_option('#plec', ''); await pg.wait_for_timeout(400)
        ok(await pg.evaluate("[...document.querySelectorAll('#stage h3.pgh')].filter(h=>!h.hidden).length") > 1, '② 모든 강의로 돌아감')
        # ③ 한 줄
        for h, sel in (('#/PHARM/_jb/_jb', '#jbbar .b1'), ('#/PHARM/_pred/_pred', '#ppills'), ('#/PHARM/_fig/_fig', '#gbpills'), ('#/PHARM/ANX/jb', '#jbbar .b1'), ('#/PHARM/ANX/pred', '#ppills')):
            await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(1200)
            n = await pg.evaluate(LINES, sel); ok(n == 1, f'③ 1440 한 줄 {h} ({n})')
        ph = await b.new_page(viewport={'width': 393, 'height': 852}, is_mobile=True, has_touch=True); ph.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for h in ('#/PHARM/_pred/_pred', '#/PHARM/_fig/_fig', '#/PHARM/_jb/_jb'):
            await ph.goto('about:blank'); await ph.goto(U + h); await ph.wait_for_timeout(1200)
            w = await ph.evaluate("[...document.querySelectorAll('#ppills select,#gbpills select,#jbbar .b1 select')].map(s=>Math.round(s.getBoundingClientRect().width))")
            ok(w and min(w) >= 80, f'③ 폰 고르기 칸 폭 {h} {w}')
        ok(not errs, f'페이지 오류 0 {errs[:2]}')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
