"""10-07 사용자 회귀: ① 세션 공부시간 = 오늘(06시 경계) 이 세션 몫만 · 시간:분:초 ② 정리표·비교표·전체정리표·과목 비교표의 기출 칩 = 그 자리 JB 미리보기(기출 탭으로 튀지 않음)
  JBL_HTTP=1 .venv/bin/python tools/tests/ux5_sess.py"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(J.HUB_URL + '#/CONS/ADH/learn'); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1000)
    r = pg.evaluate("""(()=>{const now=Date.now(),dk=__h.day(),H=36e5,f=__h.trSessTxt;return [
      f({st:'sess',t0:now-2*H,seg:now-60000,sum:H,sdd:dk,sdv:30*60000},now),
      f({st:'sess',t0:now-3*H,seg:now-60000,sum:5*H,sdd:'2000-01-01',sdv:5*H},now),
      f({st:'rest',t0:now-2*H,seg:now-60000,sum:H,sdd:dk,sdv:45*60000},now)]})()""")
    ok(r[0] == '0:31:00', f'세션 = 오늘 몫(30분) + 지금 구간(1분) h:mm:ss {r[0]}')
    ok(r[1] == '0:01:00', f'어제 몫(5시간)은 빼고 오늘 지금 구간만 {r[1]}')
    ok(r[2] == '0:45:00', f'쉬는 중에도 오늘 세션 공부 몫 {r[2]}')
    for h, sel in (('#/CONS/ADH/sum', '.msum td.mt [data-go]'), ('#/CONS/ADH/sum', '.tblwrap .xjb[data-go]'), ('#/CONS/ADH/tbl', '.tblwrap .xjb[data-go]'), ('#/CONS/_tbl/_tbl', '.tblwrap .xjb[data-go]')):
        pg.goto('about:blank'); pg.goto(J.HUB_URL + h); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1200)
        c = pg.evaluate(f"""(()=>{{const c=[...document.querySelectorAll('#stage {sel}')].find(x=>x.offsetParent);if(!c)return false;c.scrollIntoView({{block:'center'}});c.click();return true}})()""")
        pg.wait_for_timeout(600)
        ok(c and pg.evaluate("!!document.querySelector('#jbpeek.on')") and pg.evaluate('location.hash') == h, f'{h} {sel} → 미리보기 · 화면 그대로')
    ok(not errs, f'콘솔 오류 0 {errs[:2]}')
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
