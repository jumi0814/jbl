"""C09 회귀: JB 문항 id 잠금 — 6과목 빌드 뒤 tools/<sid>/jb_lock.json이 있고 팩 해시(jbhash)와 같음(verify 통과) ·
한 문항 글자를 인위로 바꾼 팩 → verify의 잠금 검사(jblock.lock_errors)가 '문제 글자가 바뀜 … 옮김 표 tools/<sid>/jb_move.json(old→new) 필요' ·
팩 p.jbmove {RX01: RX01a} → 과목을 열면 합성 mk·log·fc J:·ann이 새 id로(한 번만 — jbmoved.<S>.<판>) · 옮기기 전 자동 백업."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, shutil, tempfile
import jblock
from playwright.async_api import async_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
# 1. 잠금 = 팩
R = jblock.lock_errors(J.DOCS)
ok(len(R) >= 6 and all(n > 0 and not e for f, n, e in R), f"6과목 잠금 {[(f, n, e[:1]) for f, n, e in R]}")
ok(all(_os.path.exists(jblock.paths(s)[0]) for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']), 'tools/<sid>/jb_lock.json 7개')
# 2. 글자를 바꾼 팩 → 실패 메시지
tmp = tempfile.mkdtemp(); _os.makedirs(tmp + '/packs')
t = open(J.DOCS + '/packs/PHARM.js', encoding='utf-8').read(); i = t.index('{'); pk = json.loads(t[i:t.rindex('}') + 1])
qid = pk['order'][0]; pk['jbhash'][qid] = jblock.qhash('인위로 바꾼 문제 글자')
open(tmp + '/packs/PHARM.js', 'w', encoding='utf-8').write(t[:i] + json.dumps(pk, ensure_ascii=False) + t[t.rindex('}') + 1:])
R2 = jblock.lock_errors(tmp); e = R2[0][2]
msg = f"{R2[0][0]}: JB id 잠금 {R2[0][1]}개 — ⚠ {' · '.join(e)} → {jblock.need_msg('PHARM')}"
ok(e == [f'{qid}: 문제 글자가 바뀜'], f'verify 실패 메시지: {msg}')
ok(jblock.check('PHARM', pk['jbhash'], jblock.load(jblock.paths('PHARM')[0]), {qid: qid}) == [], '옮김 표 {id:id}(확인만)이면 통과')
shutil.rmtree(tmp)
# 3. 허브: 옮김 표 → 합성 기록 이관
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(J.HUB_URL + '#/'); await pg.wait_for_selector('.hsj[data-s="PHARM"]')
        await pg.evaluate("localStorage.clear()"); await pg.evaluate("__h.bkClear()")
        await pg.evaluate("""(()=>{const ns='jblhub.v1.';localStorage.setItem(ns+'mk.PHARM',JSON.stringify({ok:{RX01:1,RX02:1},ng:{},bm:{RX01:1},log:{RX01:[{r:'ng',t:1},{r:'ok',t:2}]}}));
          localStorage.setItem(ns+'fc.PHARM',JSON.stringify({'J:RX01':{s:'o',t:5}}));localStorage.setItem(ns+'fcMerged.PHARM','1');
          localStorage.setItem(ns+'ann.PHARM',JSON.stringify({'PHARM:RX01':[{t:'h',x:'처방전',i:0,c:'y'}]}));})()""")
        await pg.reload(); await pg.wait_for_selector('.hsj[data-s="PHARM"]')
        await pg.evaluate("__h.PACKS.PHARM.jbmove={RX01:'RX01a'};__h.PACKS.PHARM.jbmovev='t1'")
        await pg.click('.hsj[data-s="PHARM"] .hsjn'); await pg.wait_for_function("location.hash.indexOf('PHARM')>0"); await pg.wait_for_timeout(500)
        mk = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.mk.PHARM')")); fc = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.fc.PHARM')")); an = json.loads(await pg.evaluate("localStorage.getItem('jblhub.v1.ann.PHARM')"))
        ok(mk['ok'].get('RX01a') == 1 and 'RX01' not in mk['ok'] and mk['bm'].get('RX01a') == 1 and len(mk['log'].get('RX01a', [])) == 2 and mk['ok'].get('RX02') == 1, f"mk 이관 {mk}")
        ok('J:RX01a' in fc and 'J:RX01' not in fc and 'PHARM:RX01a' in an and 'PHARM:RX01' not in an, 'fc J:·ann 키 이관')
        ok(await pg.evaluate("localStorage.getItem('jblhub.v1.jbmoved.PHARM.t1')") == '1', '한 번만(jbmoved.PHARM.t1)')
        await pg.wait_for_timeout(300); ok(any(x['cat'] == 'upd' for x in await pg.evaluate("__h.bkList()")), "옮기기 전 자동 백업(원고 갱신·이관 전 — ux2 fixA V04)")
        ok(not errs, f'pageerror 0 ({errs[:2]})'); await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
_sys.exit(1 if fails else 0)
