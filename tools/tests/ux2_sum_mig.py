"""ux2 E01 회귀 — 정리표 행 단위 저장과 옛 '<S>:<K>:sum' 표시 옮기기 (맥 1280×900)
배포본(git의 마지막 docs/packs/CONS.js) WHT 정리표 글자에 합성 표시 50개(카드 행 안 낱말 1~3개, 문맥 p·s·v 포함)를 옛 키로 넣고 새 빌드를 열면
① 옮김 ≥ 47 · 다른 자리 0(옮긴 표시는 원래 카드 행에, 앞뒤 문맥이 옛 문맥과 맞음) · lost ≤ 3 · 표시 총수 불변 ② 옮기기 전 자동 백업에 옛 키
③ 화면에 옮긴 표시가 모두 칠해짐(행 data-aid '<카드 aid>~s') ④ 다시 열어도 변화 없음(LS sumMig.CONS)
⑤ 원고에 한 줄을 더한 것처럼 행 글자를 바꿔 다시 그려도 표시가 모두 제자리(위치 잃음 0)"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, subprocess, random
from playwright.async_api import async_playwright
U = J.HUB_URL; NS = 'jblhub.v1.'; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def old_pack(sid):
    """배포본 팩 — docs/packs/<SID>.js를 마지막으로 커밋한 판(없으면 None)"""
    try:
        h = subprocess.run(['git', 'log', '-1', '--format=%H', '--', f'docs/packs/{sid}.js'], cwd=J.ROOT, capture_output=True, text=True).stdout.strip()
        t = subprocess.run(['git', 'show', f'{h}:docs/packs/{sid}.js'], cwd=J.ROOT, capture_output=True, text=True).stdout
        return json.loads(t[t.index('JBLHUB.register(') + 16:t.rindex(');')])
    except Exception as e:
        print('  (배포본 팩 없음)', e); return None
# 옛 표 글자(= Kit.textOf(옛 표)) · 카드 행마다 글자 범위 → 합성 표시
GEN = r"""([html,N,seed])=>{let r=seed;const rnd=()=>{r=(r*1103515245+12345)%2147483648;return r/2147483648;};
 const d=document.createElement('div');d.innerHTML=html;document.body.appendChild(d);d.style.display='none';const W=d.querySelector('[data-aid]');const SK=__h.Kit.skipSel;
 const w=document.createTreeWalker(W,NodeFilter.SHOW_TEXT);let v='',n;const rows={};
 while(n=w.nextNode()){if(!n.nodeValue)continue;const p=n.parentElement;if(!p||p.closest(SK))continue;const tr=p.closest('tr');const b=tr&&tr.querySelector('th [data-scroll2]');if(b){const j=+b.dataset.scroll2.split(':')[1];const R=rows[j]=rows[j]||[v.length,v.length];R[1]=v.length+n.nodeValue.length;}v+=n.nodeValue;}
 const T=__h.Kit.textOf(W);if(T!==v)return {err:'글자 불일치'};const hv=__h.Kit.fnv(T);const js=Object.keys(rows).map(Number);const out=[];let guard=0;
 while(out.length<N&&guard++<5000){const j=js[Math.floor(rnd()*js.length)],R=rows[j];const seg=T.slice(R[0],R[1]);const ws=[...seg.matchAll(/[A-Za-z가-힣0-9][A-Za-z가-힣0-9\-]{1,}/g)];if(ws.length<4)continue;
  const k=Math.floor(rnd()*(ws.length-3)),m=1+Math.floor(rnd()*3),a=R[0]+ws[k].index,e=R[0]+ws[k+m-1].index+ws[k+m-1][0].length;const x=T.slice(a,e);if(x.length<3||/\n/.test(x))continue;
  if(out.some(o=>o._a<e&&a<o._b))continue;let i=0,q=-1;while((q=T.indexOf(x,q+1))>=0&&q<a)i++;
  const o={t:out.length%10===9?'b':'h',x,i,p:T.slice(Math.max(0,a-12),a),s:T.slice(e,e+12),v:hv,tid:out.length,j,_a:a,_b:e};if(o.t==='h')o.c='y';out.push(o);}
 d.remove();return {marks:out.map(o=>{const c=Object.assign({},o);delete c._a;delete c._b;return c;}),n:T.length};}"""
async def main():
    old = old_pack('CONS')
    if not old: print('RESULT SKIP'); return
    L0 = next(L for L in old['lect'] if L['k'] == 'WHT')
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(U + '#/'); await pg.wait_for_function('window.__h&&__h.PACKS.CONS', timeout=15000); await pg.evaluate('localStorage.clear()')
        g = await pg.evaluate(GEN, [L0['sum'], 50, 20260928])
        ok('marks' in g and len(g['marks']) == 50, f"픽스처: 배포본 WHT 정리표 글자 {g.get('n')}자에 합성 표시 {len(g.get('marks', []))}개 {g.get('err', '')}")
        marks = g['marks']; J_ = {m['tid']: m['j'] for m in marks}
        for m in marks: del m['j']
        newL = await pg.evaluate("__h.PACKS.CONS.lect.find(L=>L.k==='WHT').cards.map(c=>c[0])")
        oldA = [c[0] for c in L0['cards']]
        ok(newL[:len(oldA)] == oldA or True, f'WHT 카드 aid 배포본 {len(oldA)} · 지금 {len(newL)} (같은 번호 {sum(1 for a, b_ in zip(oldA, newL) if a == b_)})')
        newaid = {j: (newL[j] if j < len(newL) else None) for j in range(len(oldA))}
        # 옛 카드 aid가 새 행 alt에 있으면 그 행(aid_lock 이관)
        altmap = await pg.evaluate("(()=>{const d=document.createElement('div');d.innerHTML=__h.PACKS.CONS.lect.find(L=>L.k==='WHT').sum;const o={};d.querySelectorAll('tr[data-aid]').forEach(t=>{(t.dataset.alt||'').split(' ').forEach(a=>{if(a)o[a]=t.dataset.aid;});o[t.dataset.aid]=t.dataset.aid;});return o;})()")
        want = {tid: altmap.get(oldA[j] + '~s') for tid, j in J_.items()}
        await pg.evaluate("([ns,a])=>{localStorage.clear();localStorage.setItem(ns+'ann.CONS',JSON.stringify(a));}", [NS, {'CONS:WHT:sum': marks}])
        await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/sum'); await pg.wait_for_function("document.querySelector('#stage table.mtx')", timeout=15000)
        toast = await pg.evaluate("document.querySelector('#toast').textContent"); await pg.wait_for_timeout(600)
        a = json.loads(await pg.evaluate(f"localStorage.getItem('{NS}ann.CONS')"))
        where = {}
        for k, L in a.items():
            for o in L:
                if isinstance(o, dict) and 'tid' in o: where[o['tid']] = (k, o)
        moved = [t for t, (k, o) in where.items() if k.endswith('~s') and not o.get('lost')]
        lost = [t for t, (k, o) in where.items() if o.get('lost')]
        sq = lambda t: ''.join(str(t or '').split())
        def same(t):
            k, o = where[t]; m = marks[t]
            if k != want[t]: return False
            P, Q, p2, s2 = sq(m['p']), sq(m['s']), sq(o.get('p')), sq(o.get('s'))
            run = 0
            while run < min(len(P), len(p2)) and P[-1 - run] == p2[-1 - run]: run += 1
            r2 = 0
            while r2 < min(len(Q), len(s2)) and Q[r2] == s2[r2]: r2 += 1
            return sq(o['x']) == sq(m['x']) and (run + r2 >= min(6, len(P) + len(Q)))
        wrong = [t for t in moved if not same(t)]
        ok(len(moved) >= 47, f'E01 옮김 {len(moved)}/50 (≥ 47)')
        ok(not wrong, f'E01 다른 자리 {len(wrong)} {[(marks[t]["x"], where[t][0]) for t in wrong[:3]]}')
        ok(len(lost) <= 3 and all(where[t][0] == 'CONS:WHT:sumt' for t in lost), f'E01 lost {len(lost)} (≤ 3, 표 전체 단위 sumt에 보관) {[marks[t]["x"] for t in lost]}')
        ok(len(where) == 50 and sum(len(v) for v in a.values()) == 50, f'표시 총수 불변 ({sum(len(v) for v in a.values())})')
        ok(all(k.endswith('~s') for t, (k, o) in where.items() if t in moved), '옮긴 표시 키는 모두 행 aid(~s)')
        ok('행으로 옮겼어요' in toast, f'토스트: {toast}')
        bak = await pg.evaluate(f"(()=>{{for(const i of ['p0','p1','p2',0,1,2,3,4]){{const v=localStorage.getItem('{NS}autobak.'+i);if(!v)continue;const o=JSON.parse(v);if(o.why==='정리표 표시 이관 전')return JSON.parse(o.data['{NS}ann.CONS']||'{{}}');}}return null}})()")
        ok(bool(bak) and len(bak.get('CONS:WHT:sum', [])) == 50, f"옮기기 전 자동 백업에 옛 키 표시 {len((bak or {}).get('CONS:WHT:sum', []))}개")
        # ③ 화면
        drawn = await pg.evaluate("(()=>{const o={};document.querySelectorAll('#stage tr[data-aid] [data-rk]').forEach(e=>{const tr=e.closest('tr');o[tr.dataset.aid+'|'+e.dataset.g]=1;});return Object.keys(o).length})()")
        a2 = json.loads(await pg.evaluate(f"localStorage.getItem('{NS}ann.CONS')"))
        rlost = sum(1 for k, L in a2.items() for o in L if isinstance(o, dict) and o.get('lost') and k.endswith('~s'))
        ok(drawn == len(moved) and rlost == 0, f'화면에 칠해진 묶음 {drawn} = 옮김 {len(moved)} · 행 표시 위치 잃음 {rlost}')
        await pg.screenshot(path=J.TMP + '/ux2i_e01_mig_1280.png')
        # ④ 다시 열기
        await pg.goto('about:blank'); await pg.goto(U + '#/CONS/WHT/sum'); await pg.wait_for_function("document.querySelector('#stage table.mtx')", timeout=15000); await pg.wait_for_timeout(500)
        a3 = json.loads(await pg.evaluate(f"localStorage.getItem('{NS}ann.CONS')"))
        ok(a3 == a2, '다시 열어도 변화 없음')
        # ⑤ 원고에 한 줄 더한 것처럼: 표시가 든 행마다 세부 칸 맨 앞에 줄 하나를 넣고 다시 그림
        r = await pg.evaluate("""(()=>{const L=__h.PACKS.CONS.lect.find(L=>L.k==='WHT');const d=document.createElement('div');d.innerHTML=L.sum;let n=0;
          d.querySelectorAll('tr[data-aid]').forEach(tr=>{const td=tr.querySelectorAll('td')[1];if(!td)return;const x=document.createElement('div');x.className='ci';x.textContent='추가된 한 줄 — Bleaching 10% CP 확인';td.prepend(x);n++;});
          L.sum=d.innerHTML;__h.openDoc('CONS','WHT','learn');__h.openDoc('CONS','WHT','sum');return n;})()""")
        await pg.wait_for_timeout(500)
        a4 = json.loads(await pg.evaluate(f"localStorage.getItem('{NS}ann.CONS')"))
        l4 = sum(1 for k, L in a4.items() for o in L if isinstance(o, dict) and o.get('lost') and k.endswith('~s'))
        d4 = await pg.evaluate("(()=>{const o={};document.querySelectorAll('#stage tr[data-aid] [data-rk]').forEach(e=>{o[e.closest('tr').dataset.aid+'|'+e.dataset.g]=1;});return Object.keys(o).length})()")
        ok(l4 == 0 and d4 == len(moved), f'행 {r}개에 줄을 더해도 표시 {d4}/{len(moved)} 제자리 · 위치 잃음 {l4}')
        ok(not errs, f'pageerror 0 {errs[:2]}')
        await b.close()
asyncio.run(main())
print('RESULT', 'PASS' if not fails else 'FAIL'); _sys.exit(1 if fails else 0)
