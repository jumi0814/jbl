"""UX21 넘버링 JB 문제 출제 연도 = 지금 JB(10-18 사용자 "내가 넘버링 문제가져올 때 25년도 연도 표기가 누락되고 빠지는데, 원본 jb문제 가면 또 연도 표시는 잘 되어있거든")
- 가져온 뒤 사이트에 새 해가 붙은 문제(옛 사본에 2025 없음)를 열면 → 연도·꼬리표에 2025가 다시 · 저장에도 들어감(새로고침 뒤 그대로)
- 내가 넣은 연도(JB에 없던 해)는 그대로 · 고쳐 쓴 시각(u)은 그대로
- 새로 가져온 JB 문제의 연도 = 그 카드 data-yrs 전부(7과목 중 CONS·ESTH)
- pageerror 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CLEAR = "(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()"
CMP = """(sj=>{const S=JBLNUM._S,L=JBLNUM._jbList(sj).filter(x=>x.t==='jb'),bad=[];let n=0;
  for(const it of S.items.filter(i=>!i.del&&i.kind==='jb')){const s=it.src.find(z=>z.t==='jb'),x=s&&L.find(z=>z.id===s.id);if(!x)continue;n++;if(x.yrs.some(y=>!it.yrs.includes(y)))bad.push(it.id+' '+it.yrs+' / '+x.yrs);}
  return [n,bad.slice(0,4)];})"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1300, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(U + '#/'); pg.wait_for_timeout(1500); pg.evaluate(CLEAR)
    for sj in ('CONS', 'ESTH'):
        pg.evaluate(f"location.hash='#/_num/{sj}'"); pg.wait_for_timeout(3000)
        pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); pg.wait_for_timeout(700)
        pg.select_option('[data-if=src]', 'jb'); pg.select_option('[data-if=ty]', ''); pg.wait_for_timeout(300)
        pg.click('[data-ib=all]'); pg.wait_for_timeout(500); pg.click('[data-cf2=ok]'); pg.wait_for_timeout(1500); pg.click('.nm-ov [data-x]'); pg.wait_for_timeout(700)
        n, bad = pg.evaluate(CMP, sj); ok(n > 30 and not bad, f"{sj} 새로 가져온 JB {n}문제 연도 = JB 카드 연도 전부 {bad}")
    # 옛 사본 흉내: 2025가 든 CONS JB 문제 3개에서 2025를 빼고(src.yrs도) · 하나엔 내가 넣은 해 2019
    pg.evaluate("location.hash='#/_num/CONS'"); pg.wait_for_timeout(2500)
    ids = pg.evaluate("""(()=>{const S=JBLNUM._S,L=S.items.filter(i=>!i.del&&i.kind==='jb'&&i.yrs.includes(2025)&&i.yrs.length>1).slice(0,3);
      L.forEach((it,k)=>{it.yrs=it.yrs.filter(y=>y!==2025).concat(k===0?[2019]:[]);it.src.forEach(s=>{if(s.t==='jb')s.yrs=(s.yrs||[]).filter(y=>y!==2025);});it.u=12345;JBLNUM._put(it);});return L.map(i=>i.id);})()""")
    ok(len(ids) == 3, f"2025가 빠진 옛 사본 3개 만듦 {ids}")
    pg.evaluate("location.hash='#/'"); pg.wait_for_timeout(800); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("location.hash='#/_num/CONS'"); pg.wait_for_timeout(3000)
    r = pg.evaluate("""(ids=>ids.map(id=>{const it=JBLNUM._S.by.get(id),el=document.querySelector('.nm-it[data-id="'+CSS.escape(id)+'"] .nm-qt');return [it.yrs.join(','),it.u,el?el.textContent:'',(it.src.find(s=>s.t==='jb')||{}).yrs.join(',')];}))""", ids)
    ok(all('2025' in x[0] and '2025' in x[3] for x in r), f"다시 열면 2025 돌아옴(연도·출처) {[x[0] for x in r]}")
    ok(all('25' in x[2] for x in r), f"꼬리표에 25 {[x[2] for x in r]}")
    ok('2019' in r[0][0], f"내가 넣은 해 2019는 그대로 {r[0][0]}")
    ok(all(x[1] == 12345 for x in r), "고쳐 쓴 시각(u) 그대로")
    pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("location.hash='#/_num/CONS'"); pg.wait_for_timeout(3000)
    st = pg.evaluate("""(ids=>ids.map(id=>{let v=null;for(const k of Object.keys(localStorage))if(k.indexOf('num.i.CONS.')>=0&&k.endsWith(id))v=localStorage.getItem(k);const it=JBLNUM._S.by.get(id);return it.yrs.includes(2025);}))""", ids)
    ok(all(st), f"새로고침 뒤에도 2025 {st}")
    ok(not errs, f"pageerror 0 {errs[:3]}")
    pg.evaluate(CLEAR); b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
