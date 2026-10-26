"""10-26 사용자 '예상문제도 횟수, 대조, 문제 집중 이런 기능 다 필요없고, 기출문제, 예상문제 정렬 칸을 심플하게 … 문제 유형,(넘버링 문제 따올떄 필터 정렬 기준처럼)
서술형, 단답형, 객관식, tf 이런걸 선택할 수 있게 … multiple 선택' + '문제의 줄바꿈 및 답이 줄바꿈이 잘 안 이루어진 경우가 너무 많은데, 특히 예상문제란에서' 회귀.
 ① 막대 정돈: JB(과목·강의 기출)·예상 화면에 문제 집중(#ffocus)·출제 횟수(#fn)·대조(#fver)·상세 필터 단추(#fmore) 없음 · 옛 '문제 집중' 선호가 남아도 숨김 없음
 ② 유형 여러 개: JB 과목 문제 — 서술형+단답형을 켜면 보이는 카드 = 그 두 유형뿐(수 = 칸 숫자 합) · 하나 끄면 그것만 · [전체] = 풀림 · 새로고침해도 유지
    예상 — 객관식+단답형 켜면 그 둘만 · 새로고침해도 유지 · [전체 보기]로 풀림
 ③ 예상 문제 줄: 보기(①… · 1) … · (1) … · 1. …)가 차례로 2개 넘게 있는 발문은 보기마다 줄(.ln.li) — 한 줄 안에 차례 보기 둘 이상 0(7과목)
 ④ 예상 답 줄: 한 줄 안에 ' · '로 이은 보기 풀이(… · ③ = … · ④ ✗ …) 0 · PHARM '①②③은 12조 ②, ① 단서, ③ 그대로'는 한 줄(엉뚱한 끊김 없음)
 ⑤ 폰 393: 유형 줄 한 줄(가로 밀기) · 화면 가로 넘침 0 · pageerror 0
실행: JBL_HTTP=1 .venv/bin/python tools/tests/ux_predfmt.py"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m, flush=True)
    if not c: fails.append(m)
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
SIDS = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
VIS = "[...document.querySelectorAll('%s')].filter(c=>c.offsetParent!==null)"
def go(pg, h, sel):
    pg.goto(J.HUB_URL + h); pg.wait_for_function(WAIT + f"&&!!document.querySelector({sel!r})", timeout=90000); pg.wait_for_timeout(900)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    # ① 막대
    go(pg, '#/PHARM/_jb/_jb', '#jbbar'); pg.evaluate("localStorage.setItem('jblhub.v1.jbfocus','true')"); pg.reload(); pg.wait_for_function(WAIT + "&&!!document.querySelector('#jbbar')", timeout=90000); pg.wait_for_timeout(800)
    for h, sel in (('#/PHARM/_jb/_jb', '#jbbar'), ('#/PHARM/HM/jb', '#jbbar'), ('#/PHARM/_pred/_pred', '#ppills')):
        go(pg, h, sel)
        r = pg.evaluate("['#ffocus','#fn','#fver','#fmore'].filter(s=>document.querySelector(s))")
        ok(not r and not pg.evaluate("document.querySelector('#stage').classList.contains('focus')"), f'① {h}: 문제 집중·출제 횟수·대조·상세 필터 단추 없음 {r}')
    # ② JB 유형
    go(pg, '#/PHARM/_jb/_jb', '#jbfmt [data-jfmt]')
    chips = pg.evaluate("[...document.querySelectorAll('#jbfmt [data-jfmt]')].filter(b=>b.dataset.jfmt).map(b=>[b.dataset.jfmt,+(b.querySelector('.qn')||{}).textContent||0])")
    ok(len(chips) >= 3, f'② JB 유형 칸 {chips}')
    n0 = pg.evaluate(VIS % '#cards .qc' + ".length")
    W = dict(chips); pick = [k for k in ('es', 'sh', 'mc', 'tf', 'bl') if k in W][:2]
    for k in pick: pg.click(f'#jbfmt [data-jfmt="{k}"]'); pg.wait_for_timeout(400)
    v = pg.evaluate(VIS % '#cards .qc' + ".map(c=>c.dataset.fmt)")
    ok(v and set(v) <= set(pick) and len(v) <= sum(W[k] for k in pick), f'② JB {pick} 켬 → 보이는 {len(v)}(칸 합 {sum(W[k] for k in pick)} · 전체 {n0}) 유형 {sorted(set(v))}')
    pg.reload(); pg.wait_for_function(WAIT + "&&!!document.querySelector('#jbfmt')", timeout=90000); pg.wait_for_timeout(900)
    on = pg.evaluate("[...document.querySelectorAll('#jbfmt .tg.on')].map(b=>b.dataset.jfmt)")
    v2 = pg.evaluate(VIS % '#cards .qc' + ".map(c=>c.dataset.fmt)")
    ok(sorted(on) == sorted(pick) and set(v2) <= set(pick), f'② 새로고침 뒤에도 {on}')
    pg.click(f'#jbfmt [data-jfmt="{pick[0]}"]'); pg.wait_for_timeout(400)
    v3 = pg.evaluate(VIS % '#cards .qc' + ".map(c=>c.dataset.fmt)")
    ok(v3 and set(v3) == {pick[1]}, f'② 하나 끄면 {pick[1]}만 {sorted(set(v3))}')
    pg.click('#jbfmt .fmtall'); pg.wait_for_timeout(400)
    ok(pg.evaluate(VIS % '#cards .qc' + ".length") == n0 and pg.evaluate("document.querySelector('#jbfmt .fmtall').hidden"), '② [전체] = 풀림')
    # ② 예상 유형
    go(pg, '#/PHARM/_pred/_pred', '#pfmt [data-pfmt]')
    pch = dict(pg.evaluate("[...document.querySelectorAll('#pfmt [data-pfmt]')].filter(b=>b.dataset.pfmt).map(b=>[b.dataset.pfmt,+(b.querySelector('.qn')||{}).textContent||0])"))
    pk = [k for k in ('mc', 'sh', 'nu', 'es') if k in pch][:2]
    for k in pk: pg.click(f'#pfmt [data-pfmt="{k}"]'); pg.wait_for_timeout(400)
    pv = pg.evaluate(VIS % '#stage .pc:not(.px)' + ".map(c=>c.dataset.fmt)")
    ok(pv and set(pv) <= set(pk) and len(pv) == sum(pch[k] for k in pk), f'② 예상 {pk} 켬 → {len(pv)}(칸 합 {sum(pch[k] for k in pk)}) {sorted(set(pv))}')
    pg.reload(); pg.wait_for_function(WAIT + "&&!!document.querySelector('#pfmt')", timeout=90000); pg.wait_for_timeout(1200)
    pv2 = pg.evaluate(VIS % '#stage .pc:not(.px)' + ".map(c=>c.dataset.fmt)")
    ok(set(pv2) <= set(pk) and len(pv2) == len(pv), f'② 예상 새로고침 뒤에도 {len(pv2)}')
    pg.evaluate("document.querySelector('#pfmt .fmtall').click()"); pg.wait_for_timeout(400)
    ok(not pg.evaluate("document.querySelectorAll('#pfmt .tg.on').length"), '② 예상 [전체] = 풀림')
    # ③④ 7과목 예상 줄
    QB = []; AB = []; tot = 0
    for sid in SIDS:
        go(pg, f'#/{sid}/_pred/_pred', '#stage .pc')
        r = pg.evaluate(r"""(()=>{const C='①②③④⑤⑥⑦⑧⑨⑩',qb=[],ab=[];let n=0;
          const seq=t=>{let best=0;for(const rx of [/(?:^|\s)([①-⑩])/g,/(?:^|\s)(\d{1,2})\)\s/g,/(?:^|\s)\((\d{1,2})\)\s/g,/(?:^|\s)(\d{1,2})\.\s/g]){const v=[...t.matchAll(rx)].map(m=>C.indexOf(m[1])>=0?C.indexOf(m[1])+1:+m[1]);let run=1,b=1;for(let i=1;i<v.length;i++){run=v[i]===v[i-1]+1?run+1:1;b=Math.max(b,run);}best=Math.max(best,b);}return best;};
          document.querySelectorAll('#stage .pc:not(.px)').forEach(c=>{n++;const q=c.querySelector('.pq');if(q){const L=q.querySelectorAll('.ln');(L.length?[...L]:[q]).forEach(l=>{const t=l.textContent;if(seq(t)>=3&&!/빈칸|\(\s*\)/.test(t))qb.push(c.dataset.id+' | '+t.slice(0,90));});}
           const a=c.querySelector('.ans .pre2');if(a){const L=a.querySelectorAll(':scope>ul>li,:scope>ol>li');(L.length?[...L]:[a]).forEach(l=>{const t=l.innerText;if(/\s·\s(?:[①-⑩](?:[·,]?[①-⑩])*|\d{1,2}\))\s*(?:=|✗|×|○|✓)/.test(t)&&t.length>70)ab.push(c.dataset.id+' | '+t.slice(0,90));});}});return {n,qb,ab};})()""")
        tot += r['n']; QB += [sid + ' ' + x for x in r['qb']]; AB += [sid + ' ' + x for x in r['ab']]
    ok(not QB, f'③ 예상 {tot}문제 — 한 줄 안에 차례 보기 3개↑ 0 {len(QB)} {QB[:4]}')
    ok(not AB, f'④ 예상 답 — 한 줄 안에 · 로 이은 보기 풀이 0 {len(AB)} {AB[:4]}')
    go(pg, '#/PHARM/_pred/_pred', '#stage .pc')
    t = pg.evaluate("(()=>{const c=[...document.querySelectorAll('#stage .pc')].find(x=>/처방전 발급 원칙/.test(x.textContent));if(!c)return null;const a=c.querySelector('.ans .pre2');return [a.querySelectorAll('li').length,a.textContent.replace(/\\s+/g,' ').indexOf('①②③은 12조 ②, ① 단서, ③ 그대로')>=0]})()")
    ok(t and t[0] == 0 and t[1], f'④ PHARM 처방전 발급 원칙 답 = 한 줄(12조 ②, ① 단서 … 끊김 없음) {t}')
    pg.close()
    # ⑤ 폰
    pg = b.new_page(viewport={'width': 393, 'height': 852}, is_mobile=True, has_touch=True); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    for h, sel, row in (('#/PHARM/_jb/_jb', '#jbfmt', '#jbfmt'), ('#/PHARM/_pred/_pred', '#pfmt', '#pfmt')):
        go(pg, h, sel)
        r = pg.evaluate(f"(()=>{{const r=document.querySelector('{row}');const bs=[...r.querySelectorAll('.tg')].filter(b=>!b.hidden);const tops=new Set(bs.map(b=>Math.round(b.getBoundingClientRect().top)));return [tops.size,document.documentElement.scrollWidth<=innerWidth+1]}})()")
        ok(r[0] == 1 and r[1], f'⑤ 폰 {h}: 유형 줄 한 줄 · 가로 넘침 0 {r}')
        pg.screenshot(path=J.TMP + f'/ux_predfmt_{"jb" if "jb" in h else "pred"}_393.png')
    b.close()
ok(not errs, f'pageerror 0 {errs[:2]}')
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
sys.exit(1 if fails else 0)
