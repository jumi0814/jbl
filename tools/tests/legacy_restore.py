"""회귀: 옛 허브(배포본 f2e99d3)에서 만든 형광펜·빈칸이 새 허브에서 '같은 자리'에 복원되고, 못 찾은 것은 지우지 않고 보관되는지 (F1·F2·F7)
  .venv/bin/python tools/tests/legacy_restore.py [--max-shift 3] [--max-lost 0.06]
1) 옛 허브(tools/legacy_base.py가 work/_legacy/<rev>/docs에 풀어 둔 것)의 모든 과목·문서·탭을 돌며
   블록마다 합성 표시(한 단어 · 3~5단어 범위 · 줄 경계를 넘는 범위)를 옛 저장 형식 {t,x,i,c}로 만든다.
2) 같은 브라우저 저장소로 새 허브(docs/)를 열어 모든 문서·탭을 돌며 실제로 그려진 표시와 블록 글자를 모은다.
분류(표시마다):
  OK          그려짐 + 옛 앞뒤 글자가 맞음
  REANCHORED  그려짐 + 앞뒤 글자는 다르지만, 새 블록 어디에도 옛 앞뒤 글자를 가진 같은 글자 자리가 없음
              = 원고를 고쳐 쓰며 이웃 글자가 바뀐 같은 글자(표본 검토 2026-09 원고 재작성: '→ 8주' → '식립 8주', ' / ' → '6. ' 번호,
                필기 문장 다듬기 등 — 같은 문장·같은 사실 자리). 정상 이관
  SHIFTED     그려짐 + 옛 앞뒤 글자를 그대로 가진 같은 글자 자리가 새 블록에 따로 있는데 다른 곳에 그림 = 잘못 복원
  MOVED       옛 카드가 없어졌고(aid 바뀜) 같은 강의의 다른 카드로 옮겨 그려짐(강의 안 한 곳뿐인 글자 — data-alt로 찾은 같은 카드는 위 문맥 판정)
  MERGED      옮긴 곳에 같은 표시(같은 글자·색)가 이미 있어 하나로 합쳐짐(migrateAids — 보이는 표시 손실 없음)
  OVERLAP     다른 표시와 겹쳐 겹치지 않은 부분만 이 표시로 그려짐(겹친 곳은 먼저 그린 색)
  (PARTIAL    글자·숫자만·지워진 ⚡ 안내문 조각을 떼고 찾아 지금 글자로 다시 닻 내린 것 — 위 분류와 겹쳐 셈)
  DELETED·NOTDRAWN  저장소에서 사라짐 · 잃음 표시도 없이 안 보임 = 결함(0이어야 함)
  LOST_GONE   못 그림 — 표시 글자가 새 원고의 그 블록에서 사라짐(또는 카드 자체가 없어지고 옮길 곳도 없음) → 잃는 것이 맞음
  LOST_AMBIG  못 그림 — 글자는 새 블록에 남아 있으나 후보가 여럿이거나 짧아 문맥이 안 맞아 보류(다른 자리에 몰래 붙이지 않음)
판정: SHIFTED ≤ --max-shift · LOST_AMBIG 비율 ≤ --max-lost(옛 원고 그대로일 때의 '위치 잃음' 한도 6%를 '글자가 남아 있는데 잃은 것'에 그대로 적용 —
원고를 다시 써서 글자가 사라진 LOST_GONE은 한도에서 빼되 아래 보존 검사를 반드시 통과) · 보존: 과목마다 🖍 내 표시 모아보기의
'표시' 수 = 심은 수(하나도 지워지지 않음), '위치 잃음' 수 ≥ 못 그린 수, 못 그린 표시 글자가 모두 ⚠ 위치 잃음 절에 보임 · 콘솔 오류 0 → RESULT PASS(종료 코드 0)"""
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
   if(b<=a)continue;out.push({aid,x:s.slice(a,b),a,pre:s.slice(Math.max(0,a-14),a),post:s.slice(b,b+14),t:gs[g][0].getAttribute('data-rk')});}
  out.push({__blk:aid,alt:B.dataset.alt||'',s});}
 return out;}"""
DOCS = """(S=>{__h.openDoc(S,'_home');const p=__h.PACKS[S];return ['_jb','_sum','_tbl','_pred','_led'].map(d=>[d,'']).concat(p.lect.flatMap(L=>__h.docTabs(p,L.k).map(t=>[L.k,t[0]])));})"""
sq = lambda s: re.sub(r'\s+', '', s or '')
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
                pend = []
                for x in r:
                    if '__ann' in x:   # 블록의 합성 표시(list)와 기대값(pend)은 같은 순서 — 표시마다 추적 번호 tid(허브는 모르는 칸이라 그대로 들고 다님)
                        assert len(x['list']) == len(pend)
                        for o, e in zip(x['list'], pend): o['tid'] = e['tid'] = len(exp); exp.append(e)
                        ann[x['__ann']] = x['list']; seen[x['__ann']] = 1; pend = []
                    else: pend.append(x)
            await crawl(pg, S, GEN, each, lambda: [S, seen])
            ALL[S] = ann
        await pg.goto('about:blank')
        await pg.goto('file://' + old + '/index.html#/'); await pg.evaluate("(A)=>{localStorage.clear();for(const S in A)localStorage.setItem('jblhub.v1.ann.'+S,JSON.stringify(A[S]));}", ALL)
        print('seeded', len(exp), 'marks on', sum(len(v) for v in ALL.values()), 'blocks', flush=True)
        # 2) 새 허브에서 복원
        pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'Failed to load' not in m.text and errs.append(m.text[:200]))
        await pg.goto('about:blank'); await pg.goto('file://' + new + '/index.html#/'); await pg.wait_for_timeout(2500)
        await pg.evaluate("window.__h||(window.__h=null)"); await pg.add_script_tag(content=IDX)
        recs = collections.defaultdict(list); blocks = {}; alt_rev = collections.defaultdict(list); seen_r = set()
        for S in SUBJ:
            for r in await crawl(pg, S, COL):
                for x in r:
                    if '__blk' in x:
                        if x['__blk'] not in blocks:
                            blocks[x['__blk']] = x['s']
                            for o in x['alt'].split():
                                if o != x['__blk']: alt_rev[o].append(x['__blk'])
                    else:
                        k = (x['aid'], x['t'], x['a'], x['x'])   # 같은 블록이 여러 문서(강의 기출 탭·JB)에 나오면 한 번만
                        if k not in seen_r: seen_r.add(k); recs[x['aid']].append(x)
        ls = await pg.evaluate("(()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k);}return o;})()")
        # 보존: 🖍 내 표시 모아보기(과목마다) — 표시 총수·위치 잃음 수·⚠ 절 글자
        MK = {}
        for S in SUBJ:
            await pg.evaluate(f"__h.openDoc('{S}','_marks','')"); await pg.wait_for_timeout(150)
            MK[S] = await pg.evaluate("(()=>{const t=document.querySelector('#stage .mk-sum'),L=document.querySelector('#mk-lost');return {sum:t?t.innerText.replace(/\\s+/g,' '):'',lost:L?L.textContent:''}})()")
        await ctx.close()
    cat = collections.Counter(); bad = collections.defaultdict(list)
    ctx_ok = lambda e, pre, x, post: (norm(pre)[-5:] == norm(e['pre'])[-5:] or norm(post)[:5] == norm(e['post'])[:5]
                                      or (fz(pre)[-4:] + fz(x)) in fz(e['pre'] + e['x']) or (fz(x) + fz(post)[:4]) in fz(e['x'] + e['post']))
    ANN = {k.split('.')[-1]: json.loads(v) for k, v in ls.items() if '.ann.' in k}
    seedo = {o['tid']: o for A in ALL.values() for L in A.values() for o in L}   # tid → 심은 표시(색 c 등)
    where = {}   # tid → (과목, 지금 키, 지금 표시)
    for S, A in ANN.items():
        for key, L in A.items():
            for o in L:
                if isinstance(o, dict) and 'tid' in o: where[o['tid']] = (S, key, o)
    lec = lambda aid: ':'.join(aid.split(':')[:2]) + ':' if aid.count(':') >= 2 else None
    known = lambda key: key in blocks or key in alt_rev   # 모아보기 aidMap과 같은 기준(지금 원고의 블록 또는 그 data-alt)
    for e in exp:
        w = where.get(e['tid'])
        if not w:
            # 원고 갱신 이관(migrateAids)은 옮긴 곳에 같은 표시(t·x·i 같음 = 같은 글자 같은 자리)가 이미 있으면 하나로 합침 — 합쳐진 짝이 남아 있으면 MERGED(보이는 표시 손실 없음)
            twin = [(S_, k_, o_) for S_, k_, o_ in where.values() if S_ == e['S'] and o_['t'] == e['t'] and fz(o_['x']) == fz(e['x']) and o_.get('c') == seedo[e['tid']].get('c') and k_ != exp[o_['tid']]['aid']]
            if twin: cat['MERGED'] += 1; bad['MERGED'].append((e, twin[0][1], twin[0][2]['x'])); continue
            cat['DELETED'] += 1; bad['DELETED'].append((e, None, None)); continue   # 저장소에서 사라짐 = 절대 안 됨
        S, key, o = w
        if o.get('lost') or not known(key):
            fx = fz(e['x'])
            if e['aid'] in blocks: present = bool(fx) and fx in fz(blocks[e['aid']])
            else:   # 카드가 없어짐: 강의 안 한 블록에만 글자가 있으면 옮겼어야 함(원고 갱신 이관 규칙)
                pre = lec(e['aid']); present = bool(pre) and len(fx) >= 4 and sum(1 for a_, t_ in blocks.items() if a_.startswith(pre) and e['x'] in t_) == 1
            k = 'LOST_AMBIG' if present else 'LOST_GONE'; cat[k] += 1; bad[k].append((e, key, o['x'])); continue
        # 복원됨 → 그 블록에 실제로 그려진 자리(지금 표시의 앞뒤 글자 p·s로 고름)
        rs = [r for r in recs.get(key, []) if r['t'] == o['t'] and (r['x'] == o['x'] or norm(r['x']) == norm(o['x']) or fz(r['x']) == fz(o['x']) or (o.get('xl') and len(r['x']) == o['xl'] and r['x'].startswith(o['x'])))]   # 긴 빈칸(C03)은 x = 앞 24자 + xl   # 허브 색인과 이 검사 색인(__index)의 건너뛰는 요소 차이 흡수
        rs.sort(key=lambda r: -(len(os.path.commonprefix([sq(r['pre'])[::-1], sq(o.get('p', ''))[::-1]])) + len(os.path.commonprefix([sq(r['post']), sq(o.get('s', ''))]))))
        if not rs:
            # 겹친 표시: 먼저 그린 다른 표시가 글자 일부를 차지하면 나머지만 이 표시 묶음으로 그려짐(겹친 곳은 먼저 것 색) — 보이는 표시
            part_ = [r for r in recs.get(key, []) if r['t'] == o['t'] and len(fz(r['x'])) >= 2 and fz(r['x']) in fz(o['x']) and fz(r['x']) != fz(o['x'])]
            if part_: cat['OVERLAP'] += 1; continue
            cat['NOTDRAWN'] += 1; bad['NOTDRAWN'].append((e, key, o['x'])); continue   # 잃음 표시도 없이 안 보임 = 결함
        r = rs[0]
        if o['x'] != e['x']: cat['PARTIAL'] += 1   # 글자·숫자만·⚡ 안내문 조각을 떼고 찾은 것(지금 글자로 다시 닻)
        if key != e['aid'] and key not in alt_rev.get(e['aid'], []):
            cat['MOVED'] += 1; bad['MOVED'].append((e, key, r)); continue   # 없어진 카드 → 같은 강의 다른 카드(한 곳뿐인 글자)
        if ctx_ok(e, r['pre'], r['x'], r['post']): cat['OK'] += 1; continue
        s_ = blocks.get(key, ''); x = r['x']; L = len(x)
        other = [q for q in (m.start() for m in re.finditer(re.escape(x), s_)) if q != r['a'] and ctx_ok(e, s_[max(0, q - 14):q], x, s_[q + L:q + L + 14])]
        if other: cat['SHIFTED'] += 1; bad['SHIFTED'].append((e, r, s_[max(0, other[0] - 14):other[0] + L + 14]))
        else: cat['REANCHORED'] += 1; bad['REANCHORED'].append((e, r))
    lost_flag = sum(1 for A in ANN.values() for L in A.values() for o in L if isinstance(o, dict) and o.get('lost'))
    n = len(exp); nl = cat['LOST_GONE'] + cat['LOST_AMBIG']
    print('result', dict(cat), '| lost flagged', lost_flag, f'| lost rate {nl / max(1, n):.3f} (글자 사라짐 {cat["LOST_GONE"] / max(1, n):.3f} · 글자 남음 {cat["LOST_AMBIG"] / max(1, n):.3f})')
    for e, r in bad['REANCHORED'][:10]: print('  REANCHORED', e['aid'][:48], repr(e['x'][:30]), '| was', repr(e['pre'][-10:]), '·', repr(e['post'][:10]), '→ now', repr(r['pre'][-10:]), '·', repr(r['post'][:10]))
    for e, key, r in bad['MOVED'][:5]: print('  MOVED', e['aid'][:40], '→', key[:40], repr(e['x'][:30]))
    for e, r, o in bad['SHIFTED'][:10]: print('  SHIFTED', e['aid'][:48], repr(e['x'][:30]), '| was', repr(e['pre'][-10:]), '→ drawn', repr(r['pre'][-10:]), '| 옛 자리 남음', repr(o))
    for k in ('MERGED', 'DELETED', 'NOTDRAWN'):
        for z in bad[k][:5]: print(' ', k, z[0]['aid'][:48], repr(z[0]['x'][:30]), '→', z[1])
    json.dump({'cat': cat, 'bad': bad, 'marks': MK, 'ls': {k: v for k, v in ls.items() if '.ann.' in k}}, open(os.path.join(J.TMP, 'legacy_restore.json'), 'w'), ensure_ascii=False, indent=1)
    fail = []
    if cat['SHIFTED'] > a.max_shift: fail.append(f"SHIFTED {cat['SHIFTED']} > {a.max_shift}")
    if cat['LOST_AMBIG'] / max(1, n) > a.max_lost: fail.append(f"LOST_AMBIG rate {cat['LOST_AMBIG'] / n:.3f} > {a.max_lost}")
    if cat['DELETED']: fail.append(f"DELETED {cat['DELETED']} (저장소에서 사라진 표시)")
    if cat['NOTDRAWN']: fail.append(f"NOTDRAWN {cat['NOTDRAWN']} (잃음 표시도 없이 안 보이는 표시)")
    # 보존 — 잃은 표시는 삭제되지 않고 🖍 모아보기 '⚠ 위치 잃음'에 모두 보여야 함
    seeded = {S: sum(len(L) for L in ALL[S].values()) for S in SUBJ}
    for S in SUBJ:
        m1 = re.search(r'표시 (\d+)', MK[S]['sum']); m2 = re.search(r'위치 잃음 (\d+)', MK[S]['sum'])
        tot, nls = int(m1.group(1)) if m1 else -1, int(m2.group(1)) if m2 else -1
        L_ = [(key, o) for key, L in ANN.get(S, {}).items() for o in L if isinstance(o, dict) and (o.get('lost') or not known(key))]
        miss = [o['x'] for key, o in L_ if o['x'] not in MK[S]['lost']]
        print(f'  보존 {S}: 모아보기 표시 {tot} / 심은 {seeded[S]}(합침 {sum(1 for z in bad["MERGED"] if z[0]["S"] == S)}) · 위치 잃음 {nls} = 저장소의 잃은 표시 {len(L_)} · ⚠ 절에 없는 글자 {len(miss)} {miss[:3]}')
        mg = sum(1 for z in bad['MERGED'] if z[0]['S'] == S)
        if tot != seeded[S] - mg: fail.append(f'{S} 표시 총수 {tot} ≠ 심은 {seeded[S]} − 합침 {mg}')
        if nls != len(L_): fail.append(f'{S} 위치 잃음 {nls} ≠ 저장소 {len(L_)}')
        if miss: fail.append(f'{S} ⚠ 위치 잃음 절에 없는 표시 {len(miss)}')
    if errs: fail.append(f'console errors {errs[:3]}')
    print('RESULT', 'PASS' if not fail else 'FAIL ' + '; '.join(fail)); return not fail

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--rev', default='f2e99d3'); ap.add_argument('--max-lost', type=float, default=0.06); ap.add_argument('--max-shift', type=int, default=3)
    sys.exit(0 if asyncio.run(main(ap.parse_args())) else 1)
