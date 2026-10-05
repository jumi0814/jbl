"""10-05 사용자 묶음: 메모 v2(한 줄 머리·크기 조절·서식 B/U/형광/크기·단축키는 메모 안에서만·초록 점) · 강조 카드 보기(⭐ 기출 ∪ ★ 북마크, 토글) · 그림 창 화면 맞춤 · 되돌리기 기록 정리 · 5초 안 모드 전환 기록 안 함
  .venv/bin/python tools/tests/ux4h_A.py"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
MOD = 'Meta' if _sys.platform == 'darwin' else 'Control'
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, touch in ((1280, 860, False), (820, 1180, True)):
        ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch); pg = ctx.new_page(); errs = []; tag = str(w)
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto(U); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1');localStorage.setItem('jblhub.v1.memo.CONS.WHT',JSON.stringify('옛 메모\\n둘째 줄'))")
        pg.goto('about:blank'); pg.goto(U + '#/CONS/WHT/learn'); pg.wait_for_timeout(3500)
        # 초록 점
        ok(pg.evaluate("document.querySelector('#k-memo').classList.contains('hasmemo')"), f'{tag} 메모가 있으면 초록 점')
        pg.keyboard.press('m'); pg.wait_for_timeout(300)
        ok(pg.evaluate("document.querySelector('#memota').value") == '옛 메모\n둘째 줄', f'{tag} 옛 메모(글자) 그대로 불러옴')
        hh = pg.evaluate("[document.querySelector('#memo .mt').getBoundingClientRect().height,getComputedStyle(document.querySelector('#memot')).whiteSpace]")
        ok(hh[0] <= 30 and hh[1] == 'nowrap', f'{tag} 메모 머리 한 줄 {hh}')
        ok(pg.evaluate("document.querySelectorAll('#memotb [data-mf]').length") == 5, f'{tag} 서식 막대 5버튼')
        # 굵게: 전체 선택 후 단축키
        pg.click('#memota'); pg.keyboard.press(MOD + '+a'); pg.keyboard.press(MOD + '+b'); pg.wait_for_timeout(500)
        st = pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.memoh.CONS.WHT')||'null')")
        ok(st and st['t'] == '옛 메모\n둘째 줄' and ('bold' in st['h'] or '<b' in st['h']), f'{tag} ⌘B 굵게 → memoh 저장 {st and st["h"][:80]}')
        ok(pg.evaluate("localStorage.getItem('jblhub.v1.memo.CONS.WHT')") == '"옛 메모\\n둘째 줄"', f'{tag} memo 글자 키는 글자 그대로')
        # 글자 크기: 선택 없음 → 전체
        pg.keyboard.press('End'); pg.keyboard.press(MOD + '+Equal'); pg.wait_for_timeout(300)
        ok(pg.evaluate("localStorage.getItem('jblhub.v1.memofs')") == '15' and pg.evaluate("document.querySelector('#memota').style.fontSize") == '15px', f'{tag} ⌘+ (선택 없음) → 메모 글자 15')
        # 메모 밖에서 ⌘B는 메모 서식 아님
        pg.evaluate("document.querySelector('#memota').blur()"); z0 = pg.evaluate("localStorage.getItem('jblhub.v1.memoh.CONS.WHT')")
        pg.keyboard.press(MOD + '+u'); pg.wait_for_timeout(200)
        ok(pg.evaluate("localStorage.getItem('jblhub.v1.memoh.CONS.WHT')") == z0, f'{tag} 메모 밖 ⌘U = 메모 그대로')
        # 새로고침 뒤 서식 유지
        pg.reload(); pg.wait_for_timeout(3000); pg.keyboard.press('m'); pg.wait_for_timeout(300)
        ok(pg.evaluate("!!document.querySelector('#memota b, #memota span[style*=bold]')") and pg.evaluate("document.querySelector('#memota').value") == '옛 메모\n둘째 줄', f'{tag} 새로고침 뒤 굵게·글자 그대로')
        # 크기 조절
        r0 = pg.evaluate("document.querySelector('#memo').getBoundingClientRect().toJSON()")
        hb = pg.evaluate("document.querySelector('#memors').getBoundingClientRect().toJSON()")
        pg.mouse.move(hb['x'] + 5, hb['y'] + 5); pg.mouse.down(); pg.mouse.move(hb['x'] - 95, hb['y'] - 75, steps=6); pg.mouse.up(); pg.wait_for_timeout(200)
        r1 = pg.evaluate("document.querySelector('#memo').getBoundingClientRect().toJSON()"); sz = pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.memosz')||'null')")
        ok(r1['width'] > r0['width'] + 60 and r1['height'] > r0['height'] + 40 and sz, f'{tag} 왼쪽 위 모서리 끌기 = 크기 조절 {round(r0["width"])}→{round(r1["width"])} · 저장 {sz}')
        # 메모 지우면 점 꺼짐
        pg.click('#memota'); pg.keyboard.press(MOD + '+a'); pg.keyboard.press('Backspace'); pg.wait_for_timeout(500)
        ok(not pg.evaluate("document.querySelector('#k-memo').classList.contains('hasmemo')") and pg.evaluate("localStorage.getItem('jblhub.v1.memoh.CONS.WHT')") is None, f'{tag} 메모 비우면 점·서식 키 없음')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        # 강조 카드 보기
        pg.evaluate("localStorage.setItem('jblhub.v1.cbm.CONS',JSON.stringify({[document.querySelectorAll('#stage .tc')[0].dataset.aid]:1}))"); pg.reload(); pg.wait_for_timeout(3000)
        tot = pg.evaluate("[document.querySelectorAll('#stage .tc').length,[...document.querySelectorAll('#stage .tc')].filter(c=>+c.dataset.n>0).length]")
        pg.evaluate("document.querySelector('#lmview').click()"); pg.wait_for_timeout(250); pg.evaluate("document.querySelector('#lmcbm').click()"); pg.wait_for_timeout(500)
        vis = lambda: pg.evaluate("[...document.querySelectorAll('#stage .tc')].filter(c=>c.offsetParent).length")
        v_all = vis(); exp = tot[1] + (0 if pg.evaluate("+document.querySelectorAll('#stage .tc')[0].dataset.n>0") else 1)
        ok(v_all == exp and pg.evaluate("!!document.querySelector('#stage>.hlbar')"), f'{tag} 강조 카드 = ⭐ {tot[1]} ∪ ★ 1 → {v_all} (기대 {exp})')
        pg.evaluate("document.querySelector('.hlbar [data-hlf=bm]').click()"); pg.wait_for_timeout(300)
        ok(vis() == 1, f'{tag} 토글 ★ 북마크만 = 1')
        pg.evaluate("document.querySelector('.hlbar [data-hlf=ex]').click()"); pg.wait_for_timeout(300)
        ok(vis() == tot[1], f'{tag} 토글 ⭐ 기출만 = {tot[1]}')
        pg.evaluate("document.querySelector('.hlbar [data-hlf=off]').click()"); pg.wait_for_timeout(300)
        ok(vis() == tot[0] and not pg.evaluate("!!document.querySelector('#stage>.hlbar')"), f'{tag} 모든 카드 ✕ → 전체')
        # 그림 창 맞춤
        pg.evaluate("document.querySelector('#stage .figs figure img, #stage figure img').click()"); pg.wait_for_timeout(1500)
        m = pg.evaluate("(()=>{const w=document.querySelector('#mwrap'),i=document.querySelector('#mimg').getBoundingClientRect(),r=w.getBoundingClientRect();return [w.scrollHeight-w.clientHeight,Math.round(i.width),Math.round(i.height),Math.round(r.width),Math.round(r.height)];})()")
        ok(m[0] <= 1 and (m[1] >= m[3] - 40 or m[2] >= m[4] - 40), f'{tag} 그림 창 처음 = 화면에 꽉(세로 스크롤 없음) {m}')
        ib = pg.evaluate("document.querySelector('#mimg').getBoundingClientRect().toJSON()")
        pg.mouse.click(ib['x'] + ib['width'] * .3, ib['y'] + ib['height'] * .3); pg.wait_for_timeout(500)
        ok(pg.evaluate("document.querySelector('#mimg').classList.contains('zoom')") and pg.evaluate("(()=>{const w=document.querySelector('#mwrap');return w.scrollHeight>w.clientHeight||w.scrollWidth>w.clientWidth;})()"), f'{tag} 그림 누르면 확대 + 스크롤')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
        ok(not errs, f'{tag} pageerror 0 {errs[:2]}'); ctx.close()
    # 5초 규칙 (시계 고정)
    ctx = b.new_context(viewport={'width': 1280, 'height': 860}); pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.clock.install(); pg.goto(U); pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')"); pg.goto('about:blank'); pg.goto(U + '#/CONS/WHT/learn'); pg.clock.run_for(4000)
    segs = "(()=>{const s=JSON.parse(localStorage.getItem('jblhub.v1.tseg')||'{}');return Object.values(s).flat().filter(q=>q[1]>q[0]).map(q=>q[4]+':'+(q[1]-q[0]));})()"
    pg.evaluate("__h.trStart()"); pg.clock.run_for(60000); pg.evaluate("__h.trRest()"); pg.clock.run_for(3000); pg.evaluate("__h.trResume()"); pg.clock.run_for(60000); pg.evaluate("__h.trStop()"); pg.clock.run_for(1000)
    sg = pg.evaluate(segs); rs = pg.evaluate("Object.values(JSON.parse(localStorage.getItem('jblhub.v1.trest')||'{}')).reduce((a,b)=>a+b,0)")
    ok(not any(x.startswith('r') for x in sg) and rs == 0 and len([x for x in sg if x.startswith('s')]) == 1, f'5초 규칙: 공부 → 3초 쉬기 → 다시 공부 = 휴식 기록 없음·공부 한 구간 {sg} trest {rs}')
    pg.evaluate("__h.trStart()"); pg.clock.run_for(3000); pg.evaluate("__h.trStop()"); pg.clock.run_for(1000)
    sg2 = pg.evaluate(segs)
    ok(sg2 == sg, f'5초 규칙: ▶ 뒤 3초 안 ■ = 기록 없음 {sg2}')
    pg.evaluate("__h.trStart()"); pg.clock.run_for(30000); pg.evaluate("__h.trRest()"); pg.clock.run_for(20000); pg.evaluate("__h.trResume()"); pg.clock.run_for(20000); pg.evaluate("__h.trStop()"); pg.clock.run_for(1000)
    sg3 = pg.evaluate(segs)
    ok(len([x for x in sg3 if x.startswith('r')]) == 1, f'5초 넘은 쉬기는 그대로 기록 {sg3}')
    ok(not errs, f'5초 pageerror 0 {errs[:2]}'); ctx.close(); b.close()
print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
