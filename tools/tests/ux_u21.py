"""U21 회귀: 과목 홈 압축·실행 버튼 — 순서 유지(공부 순서 → 진행률 → 교수별 경향·📌 → 📣 → 강의 카드 → 2회 이상),
1280에서 강의 카드 시작 y ≤ 1800(6과목 · ux4 B3-3 시안 기준), 2회 이상 목록 항목 수 = 제목의 N(처음 5줄 + 더 보기 · 닫히지 않은 괄호 없음), 실행 버튼(이어서·안 푼 것·2회 이상·한눈표)이 맞는 문서·필터로 열림.
스크린샷 work/_tmp/ux_u21_*.png (맥 1280×900 · 아이패드 세로 820×1180)"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, re
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1000):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
ORDER = """()=>{const st=document.querySelector('#stage');const ids=['#hguide','#hprog','.ptrend','.hints','.lgrid','#htop'];const ys=ids.map(s=>{const e=st.querySelector(s);return e?Math.round(e.getBoundingClientRect().top+scrollY):null;});return ys;}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
            await open_(pg, f'#/{s}/_home/_home')
            ys = await pg.evaluate(ORDER)
            seq = [y for y in ys if y is not None]
            ok(seq == sorted(seq) and ys[0] is not None and ys[4] is not None, f'{s} 섹션 순서 {ys}')
            ok(ys[4] <= 1800, f'{s} 강의 카드 시작 y={ys[4]} ≤ 1800')   # ux4 B3-3 최종 시안(v2_subject_1280_full) 절 사이 48·경향 표·전략 4줄·예고 3 — 시안의 강의 절 시작 ≈1565
            n, t = await pg.evaluate("[document.querySelectorAll('#htop .toplist li').length, document.querySelector('#htop .bt').textContent]")
            N = int(re.search(r'(\d+)문항', t).group(1))
            ok(n == N, f'{s} 2회 이상 항목 {n} = 제목 N {N}')
            # 4차 최종: 처음 5줄만 보이고 [나머지 n문항 더 보기 ▾] → 누르면 전부 · 문항 글자에 닫히지 않은 괄호(잘린 연도 '(24,23') 없음
            v, bt, qs = await pg.evaluate("[[...document.querySelectorAll('#htop .toplist li')].filter(l=>l.offsetParent).length, (document.querySelector('#htop .topmore')||{}).textContent||'', [...document.querySelectorAll('#htop .toplist .q')].map(q=>q.textContent)]")
            ok(v == min(N, 5) and (N <= 5 or f'{N-5}문항' in bt), f'{s} 2회 이상 처음 {v}줄 · 버튼 {bt!r}')
            ok(not [q for q in qs if q.rfind('(') > q.rfind(')')], f'{s} 2회 이상 문항 글자 닫히지 않은 괄호 없음 {[q for q in qs if q.rfind("(") > q.rfind(")")][:2]}')
            if N > 5:
                await pg.click('#htop .topmore'); await pg.wait_for_timeout(200)
                ok(await pg.evaluate("[...document.querySelectorAll('#htop .toplist li')].every(l=>l.offsetParent) && !document.querySelector('#htop .topmore')"), f'{s} 더 보기 → {N}줄 모두')
            ok(await pg.evaluate("!!document.querySelector('#stage details.trd') && !document.querySelector('#stage details.trd').open"), f'{s} 연도별 세부 접힘')
        await open_(pg, '#/PHARM/_home/_home')
        g1 = await pg.inner_text('#hguide ol.steps li:first-child')
        ok('2회 이상' in g1, f'PHARM 1단계 2회 이상 우선 ({g1[:40]})')
        await pg.screenshot(path=J.TMP + '/ux_u21_pharm_1280.png')
        # 실행 버튼
        await pg.click('#hguide [data-sumrep]'); await pg.wait_for_timeout(600)
        ok(await pg.evaluate("location.hash.startsWith('#/PHARM/_sum') && document.querySelector('#stage').classList.contains('only-rep')"), '▶ 한눈표 2회 이상 → _sum + 2회 이상만')
        await open_(pg, '#/PHARM/_home/_home'); await pg.click('#hguide [data-jbn]'); await pg.wait_for_timeout(700)
        r = await pg.evaluate("[location.hash, document.querySelector('#fn').value, document.querySelectorAll('#cards .qc:not(.hid)').length]")
        ok(r[0].startswith('#/PHARM/_jb') and r[1] == '2', f'▶ 2회 이상만 풀기 → _jb 출제 2회↑ {r}')
        await open_(pg, '#/PHARM/_home/_home'); await pg.click('#hguide [data-jbf="todo"]'); await pg.wait_for_timeout(700)
        ok(await pg.evaluate("location.hash.startsWith('#/PHARM/_jb') && document.querySelector('#jbbar [data-qf=\"todo\"]').classList.contains('on')"), '▶ 안 푼 것 → _jb 안 푼 것 필터')
        await open_(pg, '#/PHARM/_home/_home'); t = await pg.inner_text('#hguide .go-resume'); await pg.click('#hguide .go-resume'); await pg.wait_for_timeout(700)
        ok(await pg.evaluate("/^#\\/PHARM\\/[A-Z]+\\/learn/.test(location.hash)"), f'{t} → 강의 학습 ({await pg.evaluate("location.hash")})')
        await open_(pg, '#/PHARM/_home/_home'); await pg.click('#htop [data-jbn][data-one]'); await pg.wait_for_timeout(700)
        ok(await pg.evaluate("document.querySelector('#stage').classList.contains('single') && document.querySelector('#fn').value==='2'"), '▶ n문항 한 장씩 풀기 → 한 장씩 + 2회↑')
        await open_(pg, '#/CONS/_home/_home')
        ok(await pg.evaluate("getComputedStyle(document.querySelector('#stage .ljump')).display") == 'none', '넓은 화면 과목 홈 강의 바로가기 숨김(ux3 G4 — 메뉴 강의 줄과 중복)')
        await pg.click('#side .nvl.dbtn >> nth=0'); await pg.wait_for_timeout(600)
        ok(await pg.evaluate("/\\/learn$/.test(location.hash)"), '메뉴 강의 줄 → 학습')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        ctx2 = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True); pg2 = await ctx2.new_page()
        await open_(pg2, '#/GERI/_home/_home'); await pg2.screenshot(path=J.TMP + '/ux_u21_geri_820.png')
        await pg2.click('.ljump .ljc'); await pg2.wait_for_timeout(600)
        ok(await pg2.evaluate("/\\/learn$/.test(location.hash)"), '서랍 폭(820) 강의 바로가기 칩 → 학습')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
