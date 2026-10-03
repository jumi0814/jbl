"""ux4e 회귀 — 사용자 10-01 '과목명 및 강의자료 이름 등은 너 마음대로 줄이지 말고 원래 그대로로' · '퍼센트 이런건 필요 없어'.
화면 틀(상단 막대·메뉴·허브 홈·과목 머리·달력·통계·시계 창·과목 바꾸기·JB 📖 칩·한눈표 강의 칩·검색)의 보이는 글자에
  ① 짧은 과목 이름(SUBJECTS 셋째 값)·짧은 강의 이름(p.lecname 가운데 원래 제목에 없는 것) 0
  ② 과목·강의 이름 칸이 말줄임(…·text-overflow 잘림)으로 잘린 것 0 (카드 목차 제목은 2줄까지 — 참고만)
  ③ '%' 0 (정리표·원고 내용은 제외)
  ④ 가로 넘침 0 · 콘솔 오류 0
맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)"""
import os as _os, sys as _sys, re, json, datetime; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
td = J.study_today(); yd = td - datetime.timedelta(days=1); D = lambda d: d.isoformat()
SEED = {'time': {D(td): {'CONS': 5400000, 'PHARM': 2400000, 'OMS1': 900000}, D(yd): {'ANAT': 3600000, 'GERI': 1800000}},
        'timed': {D(td): {'CONS:DHS': 5400000, 'PHARM:XE': 2400000, 'OMS1:DD1': 900000}, D(yd): {'ANAT:NV': 3600000, 'GERI:SAL': 1800000}},
        'tgoal': 240, 'whatsNew.4': 1, 'tauto': False}
def new(b, w, h, touch=False):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch); pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); pg.on('console', lambda m: pg.errs.append('console ' + m.text[:160]) if m.type == 'error' else None)
    pg.on('dialog', lambda d: d.accept())
    pg.goto('about:blank'); pg.goto(U + '#/')
    pg.evaluate("S=>{localStorage.clear();sessionStorage.clear();for(const k in S)localStorage.setItem('jblhub.v1.'+k,JSON.stringify(S[k]));}", SEED)
    return ctx, pg
def go(pg, h, wait=700):
    pg.goto('about:blank'); pg.goto(U + h)
    pg.wait_for_function("window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')", timeout=60000); pg.wait_for_timeout(wait)
# 보이는 글자 모으기 + 말줄임으로 잘린 이름 칸 + 가로 넘침
COL = r"""(A)=>{const vis=e=>e&&e.checkVisibility&&e.checkVisibility({visibilityProperty:true,opacityProperty:false});
 const SKIPC='.tc .tbody,.qtext,.lines,.ans,table.sum,#sumtop .sttab,.tblwrap table,.frame .ol .og2,.pc,.trend .tlines,.hrep,.rp2,.tvlec td.r+td';
 const out=[],cut=[];for(const sel of A){document.querySelectorAll(sel).forEach(root=>{if(!vis(root))return;
  const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null);let n;while(n=w.nextNode()){const p=n.parentElement,t=n.nodeValue.trim();if(!t||!p||!vis(p)||p.closest('script,style,svg title')||p.closest(SKIPC))continue;out.push([sel,t]);}
  root.querySelectorAll('*').forEach(e=>{if(!vis(e)||e.closest(SKIPC))return;const cs=getComputedStyle(e);const clamp=cs.webkitLineClamp&&cs.webkitLineClamp!=='none';
   if((cs.textOverflow==='ellipsis'&&e.scrollWidth>e.clientWidth+1)||(clamp&&e.scrollHeight>e.clientHeight+2))cut.push([sel,(e.className||e.tagName)+'',e.textContent.trim().slice(0,60),clamp?'clamp':'ell',!!e.closest('.scard2')]);});});}
 return {out,cut,sw:document.documentElement.scrollWidth-innerWidth};}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    SUBJ = [('OMS1', '구강악안면외과학 1', '구강외과1'), ('CONS', '임상치과보존학', '보존'), ('IMPL', '치과임플란트학', '임플란트'), ('ANAT', '임상두경부해부학', '두경부해부'),
            ('GERI', '노인치과학', '노인치과'), ('PHARM', '임상치과약물치료학', '약물치료'), ('ESTH', '심미치과학', '심미')]
    # 짧은 강의 이름 = 팩 lecname(연도 괄호 뗌) 가운데 원래 제목에 들어 있지 않은 것
    SL = []; FULL = []
    for sid in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
        t = open(_os.path.join(J.DOCS, 'packs', sid + '.js'), encoding='utf-8').read(); i = t.index('JBLHUB.register(') + 16
        pk = json.JSONDecoder().raw_decode(t[i:])[0]
        for L in pk['lect']:
            FULL.append(L['title']); s = re.sub(r'\s*\([^)]*\)\s*$', '', pk['lecname'].get(L['k'], ''))
            if s and s not in L['title'] and len(s) >= 3: SL.append(s)
    HB = r'(?<![가-힣A-Za-z0-9])'; HA = r'(?![가-힣A-Za-z0-9])'
    RS = re.compile(HB + '(' + '|'.join(re.escape(x[2]) for x in SUBJ) + ')' + HA)
    RL = re.compile(HB + '(' + '|'.join(re.escape(x) for x in sorted(SL, key=len, reverse=True)) + ')' + HA)
    FULLJ = [x[1] for x in SUBJ]
    def check(tag, R, pct=True):
        bad_s = [t for s, t in R['out'] if RS.search(t) and not any(f in t for f in FULLJ + FULL)]
        bad_l = [t for s, t in R['out'] if RL.search(t) and not any(f in t for f in FULL)]
        bad_e = [t for s, t in R['out'] if t.endswith('…') and not re.search(r'(중|잠시|불러오는)…$', t)]
        cutn = [c for c in R['cut'] if not (c[4] and c[3] == 'clamp')]   # 카드 목차 제목(.scard2 안)만 2줄 자름 허용
        ok(not bad_s and not bad_l, f'{tag} 짧은 과목·강의 이름 0 {bad_s[:3]} {bad_l[:3]}')
        ok(not bad_e and not cutn, f'{tag} 말줄임으로 잘린 이름 0 {bad_e[:3]} {cutn[:3]}')
        if pct:
            bp = [t for s, t in R['out'] if '%' in t]
            ok(not bp, f'{tag} % 글자 0 {bp[:4]}')
        ok(R['sw'] <= 1, f'{tag} 가로 넘침 없음 {R["sw"]}')
    CH = ['#top', '#nav', '#home', '#hero', '.pop2:not([hidden])', '#ckpop', '.pop.on']
    for W, H, T in [(1280, 900, False), (820, 1180, True), (1180, 820, True)]:
        v = f'{W}'
        ctx, pg = new(b, W, H, touch=T)
        go(pg, '#/CONS/DHS/learn'); go(pg, '#/PHARM/_jb/_jb'); go(pg, '#/')
        drawer = lambda: pg.evaluate("(()=>{const b=document.querySelector('#navbtn');if(b&&b.offsetParent&&!document.body.classList.contains('navopen'))b.click();})()") or pg.wait_for_timeout(400)
        # 허브 홈 + 허브 메뉴
        drawer(); check(f'{v} 허브 홈', pg.evaluate(COL, CH))
        sj = pg.evaluate("[...document.querySelectorAll('#nav .nvsb .nvsn')].map(x=>x.textContent.trim())")
        ok(sj[:6] == FULLJ[:6], f'{v} 허브 메뉴 과목 7줄 = 정식 이름 {sj}')
        # 시계 창
        pg.evaluate("(()=>{const c=document.querySelector('#clock');if(c)c.click();})()"); pg.wait_for_timeout(500)
        check(f'{v} 시계 창', pg.evaluate(COL, ['#ckpop', '.pop.on', '#tpop', '.tpop']))
        pg.keyboard.press('Escape')
        # 과목 홈 + 과목 메뉴 + 과목 바꾸기
        go(pg, '#/GERI/_home/_home'); drawer()
        check(f'{v} 과목 홈', pg.evaluate(COL, ['#top', '#nav', '#hero', '#home']))
        hd = pg.evaluate("(document.querySelector('#nav .nvsjn')||{}).textContent")
        ok(hd == '노인치과학', f'{v} 과목 메뉴 머리 = 정식 이름 하나 {hd!r}')
        pg.evaluate("document.querySelector('#nav .nvsw').click()"); pg.wait_for_timeout(300)
        sw = pg.evaluate("[...document.querySelectorAll('#nav .nvswp .pi')].map(x=>x.textContent.trim())")
        ok(all(any(x.startswith(f) for f in FULLJ) for x in sw) and len(sw) == 7, f'{v} 과목 바꾸기 7과목 정식 이름 {sw}')
        check(f'{v} 과목 바꾸기', pg.evaluate(COL, ['#nav .nvswp']))
        pg.keyboard.press('Escape')
        # 강의(긴 제목) — 빵부스러기·메뉴 강의 줄·카드 목차
        for h_, full in [('#/CONS/DHS/learn', 'Dentin hypersensitivity — 시린 치아, 제대로 진단하고 효과적으로 진료하기'), ('#/CONS/ADH/learn', 'Dental Adhesive — 상아질 접착제의 올바른 사용과 복합레진 충전 시의 고려사항')]:
            go(pg, h_); drawer()
            cc = pg.evaluate("(()=>{const e=document.querySelector('#crumb .ccur');if(!e)return null;const r=e.getBoundingClientRect(),t=document.querySelector('#top').getBoundingClientRect();return {t:e.textContent,cut:e.scrollHeight>e.clientHeight+2,in:r.top>=t.top-1&&r.bottom<=t.bottom+1}})()")
            ok(cc and cc['t'] == full and cc['in'], f'{v} 빵부스러기 원래 강의 제목 {cc}')
            nl = pg.evaluate("[...document.querySelectorAll('#nav .nvl .el')].map(x=>x.textContent)")
            ok(full in nl, f'{v} 메뉴 강의 줄 원래 제목 {nl[:3]}')
            check(f'{v} 강의 {h_}', pg.evaluate(COL, ['#top', '#nav', '#hero']), pct=False)
        # JB 📖 칩 · 한눈표 강의 칩
        go(pg, '#/CONS/_jb/_jb')
        lc = pg.evaluate("[...document.querySelectorAll('#cards .qc .chip.lec')].map(x=>x.textContent.trim()).filter(Boolean).slice(0,400)")
        badc = [x for x in lc if RL.search(x)]
        ok(lc and not badc, f'{v} JB 📖 칩 원래 강의 제목 {lc[:2]} {badc[:2]}')
        go(pg, '#/CONS/_sum/_sum')
        sc = pg.evaluate("[...document.querySelectorAll('#sumbar [data-sgo]')].map(x=>x.textContent.trim())")
        ok(sc and not [x for x in sc if RL.search(x)] and any(x.startswith('Dentin hypersensitivity — 시린 치아') for x in sc), f'{v} 한눈표 강의 칩 {sc[:3]}')
        # 달력(오늘 날 패널) · 통계
        go(pg, '#/_cal/' + D(td))
        check(f'{v} 달력', pg.evaluate(COL, ['#top', '#nav', '#home']))
        rg = pg.evaluate("(document.querySelector('#cc-ring')||{}).textContent||''")
        ok('%' not in rg and '/ 4:00' in rg, f'{v} 달력 목표 고리 시간 {rg!r}')
        go(pg, '#/_time')
        check(f'{v} 통계', pg.evaluate(COL, ['#top', '#nav', '#home']))
        # 검색
        go(pg, '#/')
        pg.evaluate("(()=>{const g=document.querySelector('#gsearch');if(!g||!g.offsetParent)return;g.focus();})()")
        if pg.evaluate("!!document.querySelector('#gsearch')&&!!document.querySelector('#gsearch').offsetParent"):
            pg.fill('#gsearch', 'whitening'); pg.keyboard.press('Enter'); pg.wait_for_timeout(1200)
            r = pg.evaluate(COL, ['#top', '#nav', '.hres .hrchip', '#home .srh', '.sres .sh'])
            check(f'{v} 검색', r, pct=False)
        ok(not pg.errs, f'{v} 콘솔 오류 없음 {pg.errs[:2]}'); ctx.close()
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
