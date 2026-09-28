"""U05 회귀: 원고가 바뀌어 aid가 달라져도 표시·✓가 새 카드로 옮겨지고, 못 찾은 것은 '위치 잃음'으로 보존(표시 총수 불변).
① data-alt(옛 aid)에 있던 표시·✓ → 새 카드  ② 어느 카드에도 없는 옛 aid → 같은 강의에서 글자가 한 곳에만 있으면 그리로, 아니면 lost
docs/index.html(J.HUB_URL)을 열고 스크린샷은 work/_tmp/ux_kt_migrate*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; NS = 'jblhub.v1.'
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
async def open_(pg, h):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(1300)
async def ls(pg, k): return json.loads(await pg.evaluate(f"localStorage.getItem('{NS}{k}')") or 'null')
def total(a): return sum(len(v) for v in (a or {}).values())
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []; toasts = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await open_(pg, '#/CONS/CRK/learn'); await pg.evaluate('localStorage.clear()'); await open_(pg, '#/CONS/CRK/learn')
        info = await pg.evaluate("""(()=>{const C=[...document.querySelectorAll('#stage .tc')];const words=c=>c.querySelector('.tbody').textContent.split(/\\s+/).filter(w=>/^[A-Za-z]{6,}$/.test(w));
          const nz=t=>t.toLowerCase().replace(/[\\s\\/·•→;,|]/g,'');const all=C.map(c=>nz(c.textContent));const uniq=(c,i)=>words(c).find(w=>all.filter(t=>t.includes(nz(w))).length===1);
          const once=c=>{const T=__h.Kit.textOf(c);return words(c).find(w=>T.split(w).length===2);};   /* 카드 안 한 번뿐인 낱말 — 문맥 없는 옛 기록은 후보가 하나일 때만 복원(v3) */
          return C.slice(0,4).map((c,i)=>({aid:c.dataset.aid,alt:c.dataset.alt,w:once(c),u:uniq(c,i)}));})()""")
        c0, c3 = info[0], info[3]
        ok(bool(c0['w'] and c3['u']), f"픽스처: 카드 안 한 번뿐인 낱말 {c0['w']} · 강의 전체에서 한 번뿐인 낱말 {c3['u']}")
        ok(c0['alt'].split(' ')[0] == 'CONS:CRK:c0', f"카드 data-alt에 옛 index aid ({c0['alt']})")
        ann = {c0['alt'].split(' ')[0]: [{'t': 'h', 'x': c0['w'], 'i': 0, 'c': 'g'}],
               'CONS:CRK:oldcard_abc123': [{'t': 'h', 'x': c3['u'], 'i': 0, 'c': 'y'}, {'t': 'b', 'x': '원고에서사라진글자', 'i': 0}]}
        await pg.evaluate("async ([ns,a,d])=>{localStorage.setItem(ns+'ann.CONS',JSON.stringify(a));localStorage.setItem(ns+'done.CONS',JSON.stringify(d));await __h.bkClear();}",
                          [NS, ann, {c0['alt'].split(' ')[0]: 1}])
        n0 = total(ann)
        await pg.goto('about:blank'); await pg.goto(U + '#/CONS/CRK/learn'); await pg.wait_for_timeout(250); await pg.evaluate("__h.migWait()")
        toast = await pg.evaluate("document.querySelector('#toast').textContent"); await pg.wait_for_timeout(1000)
        a = await ls(pg, 'ann.CONS'); dn = await ls(pg, 'done.CONS')
        ok([o['x'] for o in a.get(c0['aid'], [])] == [c0['w']], f"옛 index aid의 표시 → 새 카드 {c0['aid']}")
        ok(dn.get(c0['aid']) == 1 and 'CONS:CRK:c0' not in dn, '옛 aid의 ✓ 이해함 → 새 카드')
        ok(await pg.evaluate(f"document.querySelector('[data-aid=\"{c0['aid']}\"]').classList.contains('done') && !!document.querySelector('[data-aid=\"{c0['aid']}\"] .rk-g')"), '새로고침 뒤 새 카드에 표시와 ✓가 보임')
        ok([o['x'] for o in a.get(c3['aid'], [])] == [c3['u']], f"없는 aid의 표시 → 같은 강의에서 글자가 한 곳뿐인 카드로 ({c3['u']})")
        lost = a.get('CONS:CRK:oldcard_abc123', [])
        ok(len(lost) == 1 and lost[0].get('lost') == 1, '못 찾은 표시는 옛 키에 lost:1로 보존')
        ok(total(a) == n0, f'localStorage 표시 총수 불변 ({n0} → {total(a)})')
        ok('옮겼어요' in toast and '못 찾은 1개' in toast, f'토스트: {toast}')
        why = await pg.evaluate("__h.bkList().then(L=>{const x=L.find(x=>x.cat==='upd');return x?x.why:''})")   # ux2 fixA V04: 이관 전 전 과목 백업 한 칸(upd)
        ok('원고 갱신' in why, f'이관 전 자동 백업 ({why})')
        ok(await pg.evaluate("document.querySelector('#k-lost b').textContent") == '1', '⚠ 위치 잃음 1')
        await pg.screenshot(path=J.TMP + '/ux_kt_migrate.png')
        await open_(pg, '#/CONS/_marks/')
        ok(await pg.evaluate("document.querySelector('#mk-lost').textContent.includes('원고에서사라진글자')"), '모아보기에 옛 카드 표시')
        # 두 번째 열기: 다시 옮길 것 없음(토스트 없음·총수 불변)
        await open_(pg, '#/CONS/CRK/learn'); a2 = await ls(pg, 'ann.CONS')
        ok(a2 == a, '다시 열어도 변화 없음')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else 'FAIL'); _sys.exit(1 if fails else 0)
