"""QA 스크린샷(10-07 jbl-update 스킬 F단계): 강의마다 ⭐ 많은 카드 1장(학습 화면 + ⚡ 블록) + 그 카드 기출 1문항(답·🎯 요점·대조 펼침).
  JBL_HTTP=1 .venv/bin/python tools/qa_shots.py <SID> <KEY> [<KEY> …] [--w 1100]
→ work/_tmp/qa_<SID>_<KEY>_card.png · _mem.png · _jb.png (Read로 본다)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import jblpaths as J
from playwright.sync_api import sync_playwright
a = sys.argv[1:]; W = 1100
if '--w' in a: i = a.index('--w'); W = int(a[i + 1]); del a[i:i + 2]
S, KEYS = a[0].upper(), a[1:]
WAIT = "window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': W, 'height': 900})
    for K in KEYS:
        pg.goto(J.HUB_URL + f'#/{S}/{K}/learn'); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1500)
        r = pg.evaluate("""(()=>{const cs=[...document.querySelectorAll('#stage .tc')];let best=null,n=-1;
          cs.forEach(c=>{const k=c.querySelectorAll('.c-exam li, .c-exam .exh').length;if(k>n){n=k;best=c;}});
          if(!best)return null;best.scrollIntoView({block:'start'});const id=(best.querySelector('[data-jbq],[data-jbp],[data-go]')||{}).dataset||{};
          best.id=best.id||'qa_card';return [best.id, id.jbq||id.jbp||id.go||'']})()""")
        if not r: print(K, '카드 없음'); continue
        pg.wait_for_timeout(600); out = os.path.join(J.TMP, f'qa_{S}_{K}')
        pg.locator('#' + r[0]).screenshot(path=out + '_card.png')
        m = pg.locator('#' + r[0] + ' .c-mem')
        if m.count(): m.first.screenshot(path=out + '_mem.png')
        q = (r[1] or '').split(',')[0].split(':')[-1]
        if q:
            pg.goto(J.HUB_URL + f'#/{S}/_jb/_jb'); pg.wait_for_function(WAIT, timeout=60000); pg.wait_for_timeout(1500)
            ok = pg.evaluate("q=>{const c=document.querySelector('#c-'+q);if(!c)return false;c.querySelector('[data-tog]').click();const d=c.querySelector('[data-deep]');if(d)d.click();c.querySelectorAll('details').forEach(x=>x.open=true);c.scrollIntoView();return true}", q)
            if ok: pg.wait_for_timeout(600); pg.locator('#c-' + q).screenshot(path=out + '_jb.png')
        print(K, '→', out + '_{card,mem,jb}.png', q)
    b.close()
