"""10-26 사용자 '연도별 정렬, 교수별 정렬을 했을 때 당연히 유형별 문제 수도 맞춰서 카운트해줘야지! … 모든 탭에서' · '답 펼칠 때 왜 자꾸 위로 펼쳐지냐고 ! 위로 스크롤해서 확인해야되고'
① 기출 유형 줄 숫자 합 = '전체 n'(교수·연도를 골라도) · 0인 칸은 흐림(.z)
② 예상 유형 줄 숫자 합 = 보이는 활성 예상 수(강의·우선순위를 골라도)
③ 답 보기(카드 하나) — 누른 단추가 같은 자리(±2px) → 답은 아래로
④ 답 모두 펼치기 — 화면 맨 위에 문제·답 단추가 걸친 카드는 그 카드가 그대로(±3px) → 그 카드 답이 위로 펼쳐지지 않음"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
SUMJ = "()=>{const q=s=>[...document.querySelectorAll(s)];const t=q('#jbfmt [data-jfmt] .qn').reduce((a,x)=>a+(+x.textContent||0),0);const al=document.querySelector('#jbbar [data-qf=\"\"] .qn');return [t,al?+al.textContent:-1,q('#jbfmt .tg.z').length]}"
SUMP = "()=>{const t=[...document.querySelectorAll('#pfmt [data-pfmt] .qn')].reduce((a,x)=>a+(+x.textContent||0),0);const v=[...document.querySelectorAll('#stage .pc:not(.px)')].filter(c=>getComputedStyle(c).display!=='none'&&c.offsetParent!==null).length;return [t,v]}"
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, mob in ((1440, 900, False), (390, 844, True)):
        pg = b.new_page(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for sid in ('GERI', 'PHARM'):
            pg.goto(J.HUB_URL + f'#/{sid}/_jb'); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1000)
            if not pg.evaluate("()=>!!document.querySelector('#jbfmt')"): ok(False, f'{w} {sid} ① 유형 줄 없음'); continue
            s0 = pg.evaluate(SUMJ); ok(s0[0] == s0[1], f'{w} {sid} ① 거르기 없음 유형 합 = 전체 {s0}')
            for yr, pf in (('__first', ''), ('__second', ''), ('', '__first'), ('__first', '__first')):
                pg.evaluate("([y,pf])=>{const set=(id,v)=>{const e=document.getElementById(id);if(!e)return;if(v==='__first'||v==='__second'){const os=[...e.options].filter(o=>o.value);const o=os[v==='__first'?0:1];v=o?o.value:'';}e.value=v;e.dispatchEvent(new Event('change',{bubbles:true}));};set('fprof',pf);set('fyr',y);}", [yr, pf]); pg.wait_for_timeout(600)
                s = pg.evaluate(SUMJ); ok(s[0] == s[1] and s[1] >= 0, f'{w} {sid} ① 연도 {yr or "-"} 교수 {pf or "-"}: 유형 합 = 전체 {s}')
            pg.evaluate("()=>{['fprof','fyr'].forEach(id=>{const e=document.getElementById(id);if(e){e.value='';e.dispatchEvent(new Event('change',{bubbles:true}));}})}"); pg.wait_for_timeout(300)
            pg.goto(J.HUB_URL + f'#/{sid}/_pred'); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1000)
            if pg.evaluate("()=>!!document.querySelector('#pfmt')"):
                s = pg.evaluate(SUMP); ok(s[0] == s[1], f'{w} {sid} ② 예상 유형 합 = 보이는 예상 {s}')
                pg.evaluate("()=>{const s=document.querySelector('#plec');if(s&&s.options.length>1){s.value=s.options[1].value;s.dispatchEvent(new Event('change',{bubbles:true}));}}"); pg.wait_for_timeout(600)
                s = pg.evaluate(SUMP); ok(s[0] == s[1], f'{w} {sid} ② 강의 고른 뒤 유형 합 = 보이는 예상 {s}')
                pg.evaluate("()=>{const b=document.querySelector('#ppills [data-ppr=\"상\"]');if(b)b.click()}"); pg.wait_for_timeout(600)
                s = pg.evaluate(SUMP); ok(s[0] == s[1], f'{w} {sid} ② 우선 상 고른 뒤 유형 합 = 보이는 예상 {s}')
        for route in ('#/GERI/_jb', '#/PHARM/HM/pred'):
            pg.goto(J.HUB_URL + route); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1000)
            for i in (2, 5):
                for pos in (160, h - 140):
                    r = pg.evaluate("([i,pos])=>{document.querySelectorAll('[data-rp]').forEach(x=>delete x.dataset.rp);const c=[...document.querySelectorAll('#stage .qc,#stage .pc')].filter(x=>x.offsetParent)[i];if(!c)return 0;const b=c.querySelector('.acts:not(.acts2) [data-tog]');if(!b)return 0;scrollTo(0,scrollY+b.getBoundingClientRect().top-pos);c.dataset.rp='1';return 1}", [i, pos])
                    if not r: continue
                    pg.wait_for_timeout(300); y0 = pg.evaluate("()=>Math.round(document.querySelector('[data-rp] .acts:not(.acts2) [data-tog]').getBoundingClientRect().top)")
                    if y0 < 130: continue   # 위 막대에 가린 자리(페이지 맨 위라 더 못 내림) — 사람이 못 누르는 자리
                    pg.evaluate("()=>document.querySelector('[data-rp] .acts:not(.acts2) [data-tog]').click()"); pg.wait_for_timeout(700)
                    y1 = pg.evaluate("()=>Math.round(document.querySelector('[data-rp] .acts:not(.acts2) [data-tog]').getBoundingClientRect().top)")
                    op = pg.evaluate("()=>document.querySelector('[data-rp]').classList.contains('open')")
                    pg.evaluate("()=>document.querySelector('[data-rp] .acts:not(.acts2) [data-tog]').click()"); pg.wait_for_timeout(500)
                    ok(op and abs(y1 - y0) <= 2, f'{w} ③ {route} {i + 1}번째 답 보기 — 단추 같은 자리 {y0} → {y1}')
            # ④ 맨 위 카드의 문제 아래쪽만 보이게 두고 답 모두 펼치기
            if pg.evaluate("()=>{const f=document.querySelector('#frev');return !!f&&f.offsetParent!==null}"):
                for i in (1, 3):
                    r = pg.evaluate("i=>{document.querySelectorAll('[data-rp]').forEach(x=>delete x.dataset.rp);const c=[...document.querySelectorAll('#stage .qc,#stage .pc')].filter(x=>x.offsetParent)[i];if(!c)return 0;const a=c.querySelector('.acts:not(.acts2)');const line=120;scrollTo(0,scrollY+a.getBoundingClientRect().bottom-line-60);c.dataset.rp='1';return 1}", i)
                    if not r: continue
                    pg.wait_for_timeout(400); t0 = pg.evaluate("()=>Math.round(document.querySelector('[data-rp]').getBoundingClientRect().top)")
                    pg.evaluate("()=>document.querySelector('#frev').click()"); pg.wait_for_timeout(1500); t1 = pg.evaluate("()=>Math.round(document.querySelector('[data-rp]').getBoundingClientRect().top)")
                    pg.evaluate("()=>document.querySelector('#frev').click()"); pg.wait_for_timeout(1500)
                    ok(abs(t1 - t0) <= 3, f'{w} ④ {route} 맨 위에 걸친 {i + 1}번째 카드 — 답 모두 펼치기 뒤 그 카드 그대로 {t0} → {t1}')
        pg.close()
    b.close()
ok(not errs, f'콘솔 오류 0 {errs[:3]}')
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
