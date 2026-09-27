"""U17 회귀: JB 카드 무게 — '답:' 줄 18px(.ans0) · 긴 해설 접기(.exw.clamp + '해설 전체 보기') · 📖 정리본 절 기본 접힘(lkopen 저장) + 🔑 5항목 '더 보기'
· '✓ 대조' 작은 칩 · 문제 집중(jbfocus) · PHARM RX01 펼친 높이(개선 전 1483px, 맥 1280폭) 40%↑ 감소. 스크린샷 work/_tmp/ux_u17_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []; BASE_RX01 = 1483
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h, w=1300):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(w)
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    await open_(pg, '#/PHARM/_jb/_jb')
    r = await pg.evaluate("""(()=>{const c=document.querySelector('#c-RX01');const h0=c.offsetHeight;c.classList.add('open');const a=c.querySelector('.ln.ans0');
      return {h0,h1:c.offsetHeight,fs:a&&getComputedStyle(a).fontSize,fw:a&&getComputedStyle(a).fontWeight,clamp:!!c.querySelector('.exw.clamp'),lk:!!c.querySelector('details.ab.lk:not([open])'),vchip:(c.querySelector('.qhead .chip.v-ok')||{}).textContent}})()""")
    ok(r['fs'] == '18px' and r['fw'] == '800', f"'답:' 줄 18px·800 {r['fs']} {r['fw']}")
    ok(r['clamp'] and r['lk'], '긴 해설 접힘·📖 절 기본 접힘')
    ok(r['vchip'] == '✓ 대조', f"대조 칩 '✓ 대조' ({r['vchip']})")
    if tag == 'mac': ok(r['h1'] <= BASE_RX01 * 0.6, f"RX01 펼친 높이 {BASE_RX01} → {r['h1']} ({round((1 - r['h1'] / BASE_RX01) * 100)}% 감소)")
    await pg.evaluate("(()=>{const c=document.querySelector('#c-RX01');scrollTo(0,c.getBoundingClientRect().top+scrollY-110)})()"); await pg.wait_for_timeout(200)
    await pg.screenshot(path=J.TMP + f'/ux_u17_rx01_{tag}.png')
    # 해설 전체 보기
    await pg.evaluate("document.querySelector('#c-RX01 .exmore').click()"); await pg.wait_for_timeout(100)
    r = await pg.evaluate("(()=>{const e=document.querySelector('#c-RX01 .exw');return [getComputedStyle(e).maxHeight,document.querySelector('#c-RX01 .exmore').textContent]})()")
    ok(r[0] == 'none' and '접기' in r[1], f'해설 전체 보기 → 펼침 {r}')
    # 📖 절 펼치기 → 🔑 5항목 + 더 보기, lkopen 저장
    await pg.evaluate("document.querySelector('#c-RX01 details.ab.lk>summary .lkt').click()"); await pg.wait_for_timeout(200)
    r = await pg.evaluate("""(()=>{const d=document.querySelector('#c-RX01 details.ab.lk');const kb=d.querySelector('.kb');const l=kb.querySelector(':scope>ul,:scope>ol');const vis=[...l.children].filter(x=>x.offsetParent).length;
      return {open:d.open,vis,all:l.children.length,more:!!d.querySelector('.lkmore'),rec:d.querySelectorAll('.lrec li').length,ls:localStorage.getItem('jblhub.v1.lkopen')}})()""")
    ok(r['open'] and r['vis'] == 5 and r['all'] > 5 and r['more'] and r['ls'] == 'true', f'📖 절 펼침: 🔑 앞 5항목·더 보기·lkopen 저장 {r}')
    await pg.evaluate("document.querySelector('#c-RX01 .lkmore').click()"); await pg.wait_for_timeout(100)
    r = await pg.evaluate("(()=>{const l=document.querySelector('#c-RX01 details.ab.lk .kb').querySelector(':scope>ul,:scope>ol');return [...l.children].filter(x=>x.offsetParent).length===l.children.length})()")
    ok(r, '더 보기 → 🔑 전부')
    await pg.screenshot(path=J.TMP + f'/ux_u17_lkopen_{tag}.png')
    await open_(pg, '#/PHARM/_jb/_jb')
    ok(await pg.evaluate("[...document.querySelectorAll('#cards details.ab.lk')].every(d=>d.open)"), '새로 열어도 📖 절 펼침 선호 유지(lkopen)')
    await pg.evaluate("document.querySelector('#c-RX01').classList.add('open');document.querySelector('#c-RX01 details.ab.lk>summary .lkt').click()"); await pg.wait_for_timeout(200)
    ok(await pg.evaluate("localStorage.getItem('jblhub.v1.lkopen')") == 'false', '접으면 lkopen=false')
    # 카드로 이동 버튼은 summary를 펼치지 않고 이동
    await open_(pg, '#/PHARM/_jb/_jb')
    await pg.evaluate("document.querySelector('#c-RX01').classList.add('open');document.querySelector('#c-RX01 details.ab.lk>summary .chip.lec').click()"); await pg.wait_for_timeout(800)
    ok((await pg.evaluate('location.hash')).startswith('#/PHARM/RX/learn') and await pg.evaluate("localStorage.getItem('jblhub.v1.lkopen')") == 'false', '📖 절 머리의 카드로 이동 → 정리본(선호 안 바뀜)')
    # 문제 집중
    await open_(pg, '#/PHARM/_jb/_jb')
    await pg.evaluate("document.querySelector('#ffocus').click()"); await pg.wait_for_timeout(200)
    r = await pg.evaluate("(()=>{const c=document.querySelector('#c-RX02');const lec=c.querySelector('.qhead .chip.lec'),sub=c.querySelector('.qsub');const a=[!!lec.offsetParent,!!sub.offsetParent];c.querySelector('[data-tog]').click();return a.concat([!!lec.offsetParent,!!sub.offsetParent])})()")
    ok(r == [False, False, True, True], f'문제 집중: 닫힌 카드 📖 칩·출처 줄 숨김 → 펼치면 보임 {r}')
    await pg.screenshot(path=J.TMP + f'/ux_u17_focus_{tag}.png')
    await open_(pg, '#/PHARM/RX/jb')
    ok(await pg.evaluate("document.querySelector('#stage').classList.contains('focus') && document.querySelector('#ffocus').classList.contains('on')"), '문제 집중 선호가 강의 기출 탭에도(jbfocus)')
    await pg.evaluate("document.querySelector('#ffocus').click()")
    ok(await pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), '가로 넘침 없음')
    ok(not errs, f'pageerror 0 {errs[:2]}')
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await run(b, {'width': 1280, 'height': 900}, False, 'mac')
        await run(b, {'width': 820, 'height': 1180}, True, 'ipad')
        await b.close()
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
