"""회귀: 옛 허브(배포본 f2e99d3)에서 만든 형광펜·빈칸이 새 허브에서 '같은 자리'에 복원되는지 (F1·F2·F7)
  .venv/bin/python tools/tests/legacy_restore.py [--max-lost 0.06]
1) 옛 허브(tools/legacy_base.py가 work/_legacy/<rev>/docs에 풀어 둔 것)의 모든 과목·문서·탭을 돌며
   블록마다 합성 표시(한 단어 · 3~5단어 범위 · 줄 경계를 넘는 범위)를 옛 저장 형식 {t,x,i,c}로 만든다.
2) 같은 브라우저 저장소로 새 허브(docs/)를 열어 모든 문서·탭을 돌며 실제로 그려진 표시를 모은다.
판정: 다른 자리(SHIFTED) ≤ --max-shift(기본 3 — 검토한 3건은 라벨·원고 표기가 바뀌어 앞뒤 글자만 달라진 같은 자리:
IMPL:R02 '용어·설계·표면'(📖 정리본 카드 → 🔑 핵심), IMPL 인상채득 표('{jb:R11}' 누출 제거), ANAT:T14 '핵심Maxilla'(제목 뒤 '(25)') · 위치 잃음(MISSING+NOTRENDERED) 비율 ≤ --max-lost · 콘솔 오류 0 → RESULT PASS(종료 코드 0)"""
import os, sys, json, re, shutil, asyncio, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jblpaths as J
import legacy_base as LB
from playwright.async_api import async_playwright
SUBJ = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']
IDX = r"""
window.__SKIP='button,.noann,select,input,textarea,summary,.chip,.badge,.kbd,.ntag,.ybadge,[data-ttog]';
window.__blockOf=function(n){let p=n.nodeType===1?n:n.parentElement;while(p&&!/^(P|LI|TD|TH|DIV|SECTION|ARTICLE|H1|H2|H3|H4|H5|TR|UL|OL|TABLE|FIGCAPTION|SUMMARY|DETAILS)$/.test(p.nodeName))p=p.parentElement;return p;};
window.__index=function(B,nm){const w=document.createTreeWalker(B,NodeFilter.SHOW_TEXT,null);let s='',map=[],bs={},prev=null,n;
 while(n=w.nextNode()){if(!n.nodeValue)continue;const p=n.parentElement;if(!p||p.closest(__SKIP))continue;if(nm){const ab=p.closest('[data-aid]');if(ab&&ab!==B)continue;}const bl=__blockOf(n);if(bl!==prev){bs[s.length]=1;prev=bl;}map.push({n,start:s.length,len:n.nodeValue.length});s+=n.nodeValue;}return{s,map,bs};};
"""
GEN = r"""(args)=>{const [S,seen]=args;const out=[];const BND=/[\s\/()\[\]{},;:·•→"'“”‘’<>=|—–]/;
 for(const B of document.querySelectorAll('#stage [data-aid]')){const aid=B.dataset.aid;if(seen[aid])continue;const ix=__index(B,false);const s=ix.s;if(s.replace(/\s/g,'').length<6)continue;
  const toks=[];let i=0;while(i<s.length){if(BND.test(s[i])){i++;continue;}let j=i;while(j<s.length&&!BND.test(s[j])&&!(j>i&&ix.bs[j]))j++;if(j-i>=2)toks.push([i,j]);i=j;}
  if(!toks.length)continue;const picks=[],used=[];const ok=(a,b)=>used.every(u=>b<=u[0]||a>=u[1]);
  const h=[...aid].reduce((a,c)=>(a*31+c.charCodeAt(0))>>>0,7);
  let t=toks[h%toks.length];picks.push([t[0],t[1]]);used.push(t);
  if(toks.length>=6){const k=(h>>>3)%(toks.length-5);for(let tr=0;tr<toks.length;tr++){const kk=(k+tr)%(toks.length-5);const a=toks[kk][0],b=toks[kk+2+(h%3)][1];if(ok(a,b)&&b-a<120){picks.push([a,b]);used.push([a,b]);break;}}}
  const bks=Object.keys(ix.bs).map(Number).filter(x=>x>0);for(const bp of bks.slice((h>>>5)%Math.max(1,bks.length))){const L=toks.filter(t=>t[1]<=bp).pop(),R=toks.find(t=>t[0]>=bp);if(L&&R&&ok(L[0],R[1])&&R[1]-L[0]<160){picks.push([L[0],R[1]]);used.push([L[0],R[1]]);break;}}
  const cols=['y','g','p','u','o'];let ci=h;const list=[];
  for(const [a,b] of picks){const x=s.slice(a,b);let n=0,p=-1;while((p=s.indexOf(x,p+1))>=0&&p<a)n++;const tt=(ci++%4===3)?'b':'h';const o={t:tt,x,i:n};if(tt==='h')o.c=cols[ci%5];list.push(o);
   out.push({S,aid,t:tt,x,pre:s.slice(Math.max(0,a-14),a),post:s.slice(b,b+14)});}
  out.push({__ann:aid,list});}
 return out;}"""
COL = r"""()=>{const out=[];
 for(const B of document.querySelectorAll('#stage [data-aid]')){const aid=B.dataset.aid;const ix=__index(B,true);const s=ix.s;const gs={};
  B.querySelectorAll('[data-rk]').forEach(el=>{if(el.closest('[data-aid]')!==B)return;const g=el.getAttribute('data-g');(gs[g]=gs[g]||[]).push(el);});
  for(const g in gs){let a=1e9,b=-1;gs[g].forEach(e=>{const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT,null);let t;while(t=w.nextNode()){const m=ix.map.find(q=>q.n===t);if(m){a=Math.min(a,m.start);b=Math.max(b,m.start+m.len);}}});
   if(b<=a)continue;out.push({aid,x:s.slice(a,b),pre:s.slice(Math.max(0,a-14),a),post:s.slice(b,b+14),t:gs[g][0].getAttribute('data-rk')});}
  out.push({__blk:aid});}
 return out;}"""
DOCS = """(S=>{__h.openDoc(S,'_home');const p=__h.PACKS[S];return ['_jb','_sum','_tbl','_pred','_led'].map(d=>[d,'']).concat(p.lect.flatMap(L=>__h.docTabs(p,L.k).map(t=>[L.k,t[0]])));})"""
norm = lambda s: re.sub(r'[\s/·•→;,|\-—–:()\[\]]', '', s).lower()
fz = lambda s: ''.join(ch for ch in s.lower() if ch.isalnum())

async def crawl(pg, S, fn, each=None, arg=None):
    docs = await pg.evaluate(DOCS, S); await pg.wait_for_timeout(300); res = []
    for d, t in docs:
        if t == 'flash': continue
        await pg.evaluate(f"__h.openDoc('{S}','{d}','{t}')"); await pg.wait_for_timeout(60)
        r = await pg.evaluate(fn, arg() if arg else None) if arg else await pg.evaluate(fn)
        if each: each(r)
        res.append(r)
    return res

async def main(a):
    old = LB.old_docs(a.rev, None); new = J.DOCS
    prof = os.path.join(J.TMP, 'legacy_restore_profile'); shutil.rmtree(prof, ignore_errors=True)
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(prof, viewport={'width': 1280, 'height': 900})
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page(); errs = []
        pg.on('dialog', lambda d: asyncio.ensure_future(d.dismiss()))
        # 1) 옛 허브에서 합성 표시
        await pg.goto('file://' + old + '/index.html#/'); await pg.wait_for_timeout(1500); await pg.evaluate('localStorage.clear()')
        await pg.goto('about:blank'); await pg.goto('file://' + old + '/index.html#/'); await pg.wait_for_timeout(2000); await pg.add_script_tag(content=IDX)
        exp = []; ALL = {}
        for S in SUBJ:
            ann = {}; seen = {}
            def each(r):
                for x in r:
                    if '__ann' in x: ann[x['__ann']] = x['list']; seen[x['__ann']] = 1
                    else: exp.append(x)
            await crawl(pg, S, GEN, each, lambda: [S, seen])
            ALL[S] = ann
        await pg.goto('about:blank')
        await pg.goto('file://' + old + '/index.html#/'); await pg.evaluate("(A)=>{localStorage.clear();for(const S in A)localStorage.setItem('jblhub.v1.ann.'+S,JSON.stringify(A[S]));}", ALL)
        print('seeded', len(exp), 'marks on', sum(len(v) for v in ALL.values()), 'blocks', flush=True)
        # 2) 새 허브에서 복원
        pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'Failed to load' not in m.text and errs.append(m.text[:200]))
        await pg.goto('about:blank'); await pg.goto('file://' + new + '/index.html#/'); await pg.wait_for_timeout(2500)
        await pg.evaluate("window.__h||(window.__h=null)"); await pg.add_script_tag(content=IDX)
        recs = collections.defaultdict(list); blocks = set()
        for S in SUBJ:
            for r in await crawl(pg, S, COL):
                for x in r:
                    if '__blk' in x: blocks.add(x['__blk'])
                    else: recs[x['aid']].append(x)
        ls = await pg.evaluate("(()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k);}return o;})()")
        await ctx.close()
    cat = collections.Counter(); bad = collections.defaultdict(list)
    for e in exp:
        if e['aid'] not in blocks: cat['NOTRENDERED'] += 1; bad['NOTRENDERED'].append(e); continue
        rs = [r for r in recs[e['aid']] if r['t'] == e['t'] and (r['x'] == e['x'] or norm(r['x']) == norm(e['x']))]
        if not rs:   # 3단계(글자·숫자만·옛 ⚡ 안내문 조각 뗌)로 찾은 것 — 그려진 글자가 원래 표시 글자의 일부
            rs = [r for r in recs[e['aid']] if r['t'] == e['t'] and len(fz(r['x'])) >= 2 and fz(r['x']) in fz(e['x']) and len(fz(r['x'])) >= .3 * len(fz(e['x']))]
            if rs: cat['PARTIAL'] += 1
        if not rs: cat['MISSING'] += 1; bad['MISSING'].append(e); continue
        ctx_ok = lambda r: (fz(r['pre'])[-4:] + fz(r['x'])) in fz(e['pre'] + e['x']) or (fz(r['x']) + fz(r['post'])[:4]) in fz(e['x'] + e['post'])
        good = [r for r in rs if norm(r['pre'])[-5:] == norm(e['pre'])[-5:] or norm(r['post'])[:5] == norm(e['post'])[:5] or ctx_ok(r)]
        if good: cat['OK'] += 1
        else: cat['SHIFTED'] += 1; bad['SHIFTED'].append((e, rs[:2]))
    lost = sum(1 for k, v in ls.items() if '.ann.' in k for L in json.loads(v).values() for o in L if o.get('lost'))
    n = len(exp); nl = cat['MISSING'] + cat['NOTRENDERED']
    print('result', dict(cat), '| lost flagged', lost, f'| lost rate {nl / max(1, n):.3f}')
    for e, rs in bad['SHIFTED'][:10]: print('  SHIFTED', e['aid'], repr(e['x'][:30]), '| was', repr(e['pre'][-10:]), '→ now', repr(rs[0]['pre'][-10:]))
    json.dump({'cat': cat, 'bad': bad}, open(os.path.join(J.TMP, 'legacy_restore.json'), 'w'), ensure_ascii=False, indent=1)
    fail = []
    if cat['SHIFTED'] > a.max_shift: fail.append(f"SHIFTED {cat['SHIFTED']} > {a.max_shift}")
    if nl / max(1, n) > a.max_lost: fail.append(f'lost rate {nl / n:.3f} > {a.max_lost}')
    if errs: fail.append(f'console errors {errs[:3]}')
    print('RESULT', 'PASS' if not fail else 'FAIL ' + '; '.join(fail)); return not fail

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--rev', default='f2e99d3'); ap.add_argument('--max-lost', type=float, default=0.06); ap.add_argument('--max-shift', type=int, default=3)
    sys.exit(0 if asyncio.run(main(ap.parse_args())) else 1)
