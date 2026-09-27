"""U19 회귀: 기출 한눈표 — 번호만 있는 답에 '정답/틀린 보기' 줄(문제 원문 부분 문자열) 또는 '▸ 보기 펼치기', 연도 배지 줄바꿈 없음(820폭).
전 과목 · 맥 1280×900 · 아이패드 세로 820×1180. 스크린샷 work/_tmp/ux_u19_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CHECK = r"""()=>{const P=window.__P;const rows=[...document.querySelectorAll('table.sum tbody tr')];let num=0,has=0,bad=[],picks=0,wrap=0;
 const tmp=document.createElement('div');
 rows.forEach(r=>{const td=r.cells[2];if(!td)return;const ln=td.querySelector('.lines .ln');const t=ln?ln.textContent.trim():'';
  if(/^답\s*[:：]?\s*(?:[1-9①-⑨](?![0-9])\s*\)?\s*[,\/]?\s*)+$/.test(t)){num++;if(td.querySelector('.ln.pick,details.pickd'))has++;else bad.push(t);}
  const b=r.querySelector('.ybadge');if(b){const bb=b.querySelector('b');if(bb&&bb.getClientRects().length>1||b.getBoundingClientRect().height>30)wrap++;}
  td.querySelectorAll('.ln.pick').forEach(pk=>{picks++;const id=r.querySelector('[data-go]').dataset.go;return;});});
 return {rows:rows.length,num,has,bad:bad.slice(0,5),picks,wrap};}"""
SUBSTR = r"""(s)=>{const p=window.JBLHUB&&0;const rows=[...document.querySelectorAll('table.sum tbody tr')];let n=0,bad=[];const tmp=document.createElement('div');
 for(const r of rows){const g=r.querySelector('[data-go]');if(!g)continue;const pk=[...r.querySelectorAll('.ln.pick')];if(!pk.length)continue;
  const html=window.__cards[g.dataset.go];tmp.innerHTML=html;const qt=tmp.querySelector('.qtext').textContent;
  pk.forEach(x=>{n++;const t=x.textContent.replace(/^(정답 보기|틀린 보기)\s/,'');if(qt.indexOf(t)<0)bad.push(g.dataset.go+': '+t.slice(0,40));});}
 return {n,bad:bad.slice(0,5)};}"""
async def run(b, vp, touch, tag):
    ctx = await b.new_context(viewport=vp, has_touch=touch); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); print('==', tag)
    for s in ['PHARM', 'OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI']:
        await pg.goto('about:blank'); await pg.goto(U + f'#/{s}/_sum/_sum'); await pg.wait_for_timeout(1300)
        r = await pg.evaluate(CHECK)
        ok(r['num'] == r['has'], f"{s}: 번호만 있는 답 {r['num']}행 중 보기 줄/펼치기 {r['has']} {r['bad']}")
        ok(r['wrap'] == 0, f"{s}: 연도 배지 줄바꿈 {r['wrap']}")
        # 카드 원문 대조: 팩 파일을 다시 읽음
        import json
        t = open(_os.path.join(J.DOCS, 'packs', f'{s}.js'), encoding='utf-8').read(); pk = (lambda t__: json.loads(t__[t__.index('JBLHUB.register(')+16:-2]))(t)
        await pg.evaluate("c=>{window.__cards=c}", pk['cards'])
        r2 = await pg.evaluate(SUBSTR, s)
        ok(not r2['bad'], f"{s}: 보기 줄 {r2['n']}개 모두 문제 원문 부분 문자열 {r2['bad']}")
        ov = await pg.evaluate("document.documentElement.scrollWidth<=innerWidth")
        ok(ov, f'{s}: 가로 넘침 없음')
        if s == 'PHARM':
            ok(r['num'] >= 48, f"PHARM 번호만 있는 답 {r['num']}행(≥48)")
            await pg.screenshot(path=J.TMP + f'/ux_u19_{tag}.png')
            await pg.evaluate("document.querySelector('details.pickd')&&(document.querySelector('details.pickd').open=true,document.querySelector('details.pickd').scrollIntoView({block:'center'}))"); await pg.wait_for_timeout(200)
            await pg.screenshot(path=J.TMP + f'/ux_u19_pickd_{tag}.png')
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
