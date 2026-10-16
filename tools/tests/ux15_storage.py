"""UX15 저장 공간 2단(10-15 사용자 '저장 공간 및 기기 간 기록 이전 개선' · '사용자 데이터는 어떤 업데이트에서도 소실되지 않아야') —
넘버링 문제(num.i.*)·복습 기록(num.r.*)이 이 브라우저(localStorage)를 채우면 기기 저장소(IndexedDB 'jblhub-xs')로 옮김(키·값 글 그대로).
A 맥 1280: 옛 형식 기록으로 localStorage를 약 4.8M자까지 채움(형광펜·빈칸 = 화면에서 직접 + 열지 않는 과목 4천 개 · 채점·✓·북마크·메모·공부 시간 · 넘버링 300문제 + 복습 기록 300 · 같은 주소 다른 페이지 몫)
  → 허브 열기 → 자동 옮김(먼저 자동 백업 '저장 공간 정리 전' · 다시 읽어 같을 때만 지움) → 모든 기록 글자까지 같음(지문) · localStorage 넘버링 0 · 자리 비움
  → 새로고침 뒤 형광펜·빈칸 그대로 · 새 표시 저장 성공(빨간 띠 없음) · 넘버링 화면 300문제 · 스토리 고침 → 기기 저장소에 저장 · 새로고침 뒤 그대로 · 다른 창에 바로 보임
B 빈 브라우저: 자기 표시·넘버링 1개 → A의 백업 파일 합치기(미리 보기 확인 창: 더해지는 것·겹칠 때) → A 기록 전부 같음 + 자기 것도 남음 → B 파일을 A에 합치기 → A에도 둘 다
C IndexedDB 없음(사생활 보호 모드 흉내): 옛 방식 그대로 — 넘버링 열기·고치기·표시·백업 파일에 넘버링 · 공간 정리 '쓸 수 없어요'
D 꽉 찬 브라우저(자동 옮김 끔 xs.no): 저장 실패 → 넘버링을 옮겨 자리를 만들고 다시 씀 → 띠 없이 표시 저장
E 아이패드 사파리(UA·820 세로): 크기를 바이트로(한글 2) · 복원 창 저장 공간 줄 · 가로 넘침 0
A 끝: 이 브라우저로 되돌리기(xsBack) → 글자 같음 · pageerror 0. 스크린샷 work/_tmp/ux15_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json
from playwright.async_api import async_playwright
U = J.HUB_URL; BASE = U.rsplit('/', 1)[0] + '/'; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
LEC = '#/OMS1/DD1/learn'
PICK = '''(n=>{const lis=[...document.querySelectorAll('#stage [data-aid] li')].filter(l=>l.offsetParent&&!l.closest('details:not([open])')&&!l.querySelector('[data-rk]')&&/[A-Za-z가-힣]{3}/.test(l.textContent));const li=lis[n];li.scrollIntoView({block:'center'});const w=document.createTreeWalker(li,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){const m=/[A-Za-z가-힣]{3,}/.exec(x.nodeValue);if(m&&!x.parentElement.closest('button,.chip,.noann,[data-rk]')){const r=document.createRange();r.setStart(x,m.index+1);r.setEnd(x,m.index+2);const b=r.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2,m[0]];}}})'''
FNV = "const FNV=s=>{if(s==null)return null;let h=0x811c9dc5;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0).toString(36)+':'+s.length;};"
# 옛 형식 기록(허브가 쓰는 그대로의 키·값) — n문제 · target(글자)까지 같은 주소 다른 페이지 몫으로 채움 · keys = 지문을 볼 공부 기록 키
SEED = """(o=>{const NS='jblhub.v1.',W=(k,v)=>localStorage.setItem(NS+k,typeof v==='string'?v:JSON.stringify(v)),keys=[];
 const kor='넘버링 스토리 — 상악골 골절 분류와 치료 원칙을 떠올리는 문장 ',sj=o.sj||'CONS';
 for(let i=0;i<o.n;i++){const id='u:p'+i;W('num.i.'+sj+'.'+id,{id,k:'user',lec:'',q:'<p>'+(i+1)+'. 시험 문제 '+kor.repeat(6)+'</p>',a:'<p>'+'답안 줄 '.repeat(40)+'</p><table><tbody><tr><td>칸</td><td>'+'x'.repeat(300)+'</td></tr></tbody></table>',st:'<p>스토리 '+i+' '+kor.repeat(o.st||30)+'</p>',note:'해설 '.repeat(80),tags:[],yrs:[2025-(i%5)],src:[{t:'user',s:sj,lab:'시험'}],o:i,c:1,u:1000+i,prev:{f:'st',h:'<p>옛 스토리 '+kor.repeat(20)+'</p>',at:1}});keys.push('num.i.'+sj+'.'+id);
  if(o.r){W('num.r.'+sj+'.'+id,{id,m:i%3,d:2000,h:[{t:2000,m:i%3,s:'s1'}],w:[{t:2000,s:'s1',x:'내 답안 '.repeat(120)}],u:2000});keys.push('num.r.'+sj+'.'+id);}}
 if(o.n){W('num.x.'+sj,{v:1,ul:[],lt:{},u:1});keys.push('num.x.'+sj);}
 if(o.more){const A={};for(let c=0;c<200;c++){const L=[];for(let j=0;j<20;j++){const m={t:j%4?'h':'b',x:'핵심어 '+c+'-'+j+' 상악동',i:0,p:'앞 문맥 열두 글자다',s:'뒤 문맥 열두 글자다',v:'abc123'};if(j%4)m.c='y';L.push(m);}A['GERI:BLE:c'+c]=L;}W('ann.GERI',A);
  W('mk.GERI',{ok:{Q1:1,Q2:1},ng:{Q3:1},bm:{Q2:1},log:{Q1:[{r:'ok',t:1760000000000}]}});W('done.GERI',{'GERI:BLE:c1':1760000000000});W('cbm.GERI',{'GERI:BLE:c2':1760000000000});W('lbm.GERI',{BLE:1760000000000});W('memo.GERI.BLE',JSON.stringify('메모 — 지우면 안 되는 글 '.repeat(20)));
  ['ann.GERI','mk.GERI','done.GERI','cbm.GERI','lbm.GERI','memo.GERI.BLE'].forEach(k=>keys.push(k));
  W('tseg',{'2026-10-02':[[3600,7200,'GERI','BLE','a']]});W('time',{'2026-10-02':{GERI:3600000}});W('timed',{'2026-10-02':{'GERI:BLE':3600000}});}
 if(o.no)W('xs.no',1);
 const used=()=>{let n=0;for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);n+=k.length+(localStorage.getItem(k)||'').length;}return n;};
 let i=0;if(o.target){const big='z'.repeat(100000);while(used()<o.target-100000){localStorage.setItem('zz.other.'+(i++),big);}}
 if(o.brim){for(const sz of [100000,10000,1000,100,10]){const s='z'.repeat(sz);try{for(;;)localStorage.setItem('zz.brim.'+(i++),s);}catch(e){}}}
 let nc=0;for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(/^jblhub[.]v1[.]num[.][ir][.]/.test(k))nc+=k.length+localStorage.getItem(k).length;}
 return {keys,used:used(),nc};})"""
DIG = "(keys=>{" + FNV + "const o={};keys.forEach(k=>{o[k]=FNV(__h.stGet(k));});return o;})"
DIGLS = "(keys=>{" + FNV + "const o={};keys.forEach(k=>{o[k]=FNV(localStorage.getItem('jblhub.v1.'+k));});return o;})"
NANN = "(s=>{const v=__h.stGet('ann.'+s);if(!v)return 0;const a=JSON.parse(v);let n=0;for(const k in a)n+=a[k].length;return n;})"
LSNUM = "Object.keys(localStorage).filter(k=>/^jblhub\\.v1\\.num\\.[ir]\\./.test(k)).length"
async def lec(pg):
    await pg.goto(U + LEC); await pg.wait_for_function("document.querySelectorAll('#stage .tc').length>3", timeout=60000); await pg.wait_for_timeout(500)
async def mark(pg, n, key='h'):
    await pg.keyboard.press(key); a = await pg.evaluate(PICK + f'({n})'); await pg.mouse.click(a[0], a[1]); await pg.wait_for_timeout(250); await pg.keyboard.press(key); return a[2]
def ctxerr(pg, errs, tag):
    pg.on('pageerror', lambda e: errs.append(tag + ' ' + str(e)[:200]))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []; DLG = []
        def dlg(d): DLG.append(d.message); asyncio.ensure_future(d.accept())
        # ===== A: 옛 형식 4.8M자 → 열기 → 자동 옮김 =====
        print('== A 맥 1280 — 옛 형식 4.8M자')
        A = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await A.new_page(); ctxerr(pg, errs, 'A'); pg.on('dialog', dlg)
        await lec(pg); await pg.evaluate("localStorage.clear()"); await lec(pg)
        w1 = await mark(pg, 0); w2 = await mark(pg, 2); w3 = await mark(pg, 4, 'b')
        nh0, nb0 = await pg.evaluate("document.querySelectorAll('#stage [data-rk=h]').length"), await pg.evaluate("document.querySelectorAll('#stage [data-rk=b]').length")
        ok(await pg.evaluate(NANN + "('OMS1')") == 3 and nh0 >= 2 and nb0 >= 1, f'화면에서 형광펜 2·빈칸 1 ({w1}·{w2}·{w3})')
        await pg.goto(BASE + 'icon-192.png'); sd = await pg.evaluate(SEED + "({n:300,r:1,more:1,target:4800000})"); keys = sd['keys'] + ['ann.OMS1']
        d0 = await pg.evaluate(DIGLS, keys); ok(sd['used'] >= 4700000 and all(d0.values()), f"옛 형식으로 채움 {sd['used']:,}자 · 지문 볼 기록 {len(keys)}개")
        num0 = sum(1 for k in keys if k.startswith('num.'))
        await lec(pg)
        await pg.wait_for_function("__h.XS.ready&&__h.XS.on&&__h.lsScan().xsN===0", timeout=30000, polling=300)
        ok(await pg.evaluate(LSNUM) == 0, '자동 옮김 — localStorage 넘버링 키 0')
        ok(await pg.evaluate("__h.XS.M.size") == num0 - 1, f"기기 저장소 {await pg.evaluate('__h.XS.M.size')}개(num.i·num.r — num.x는 그대로)")
        d1 = await pg.evaluate(DIG, keys); bad = [k for k in keys if d1[k] != d0[k] and k != 'ann.OMS1']
        ok(not bad, f'옮긴 뒤 기록 {len(keys)}개 글자까지 같음(지문) — 다름 {bad[:3]}')
        u1 = await pg.evaluate("__h.lsUsed()"); ok(u1 <= sd['used'] - sd['nc'] * 0.95, f'이 브라우저 기록 {sd["used"]:,} → {u1:,}자(넘버링 {sd["nc"]:,}자만큼 비움)')
        L = await pg.evaluate("__h.bkList().then(L=>L.filter(x=>x.cat==='xs').map(x=>({id:x.id,why:x.why})))"); ok(len(L) == 1 and '저장 공간 정리 전' in L[0]['why'], f'옮기기 전 자동 백업 {L}')
        bk = await pg.evaluate("(id=>__h.bkLoad(id).then(j=>{" + FNV + "const o={};Object.keys(j.data).forEach(k=>{if(/\\.num\\.[ir]\\./.test(k))o[k.slice(10)]=FNV(j.data[k]);});return o;}))", L[0]['id'] if L else '0')
        ok(len(bk) == num0 - 1 and all(bk[k] == d0[k] for k in bk), f'그 백업에 옮기기 전 넘버링 {len(bk)}개(글자 같음)')
        lg = await pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.xs.log')||'null')"); ok(bool(lg) and lg['n'] == num0 - 1, f"옮김 기록 xs.log n={lg and lg['n']} sig={lg and lg['sig']}")
        ok('저장 공간을 정리했어요' in (await pg.evaluate("sessionStorage.getItem('jblhub.v1.toasts')") or ''), "알림 '저장 공간을 정리했어요 — 넘버링 기록 n개…'")
        # 새로고침 뒤 그대로 · 새 표시 저장
        await lec(pg); await pg.wait_for_function("__h.XS.ready", timeout=10000)
        nh1, nb1 = await pg.evaluate("document.querySelectorAll('#stage [data-rk=h]').length"), await pg.evaluate("document.querySelectorAll('#stage [data-rk=b]').length")
        ok((nh1, nb1) == (nh0, nb0), f'새로고침 뒤 형광펜·빈칸 그대로 {nh1}·{nb1}')
        d2 = await pg.evaluate(DIG, keys); ok(all(d2[k] == d0[k] for k in keys if k != 'ann.OMS1'), '새로고침 뒤 모든 기록 같음')
        ok(await pg.evaluate(f"JSON.parse(__h.stGet('tseg'))['2026-10-02'][0][1]") == 7200 and await pg.evaluate("JSON.parse(__h.stGet('time'))['2026-10-02'].GERI") == 3600000, '공부 시간(지난 날) 그대로')
        w4 = await mark(pg, 6); await pg.wait_for_timeout(400)
        ok(await pg.locator('#lserr').count() == 0 and await pg.evaluate(NANN + "('OMS1')") == 4, f'새 표시 저장 성공({w4}) · 빨간 띠 없음')
        await pg.screenshot(path=J.TMP + '/ux15_A_lec.png')
        # 넘버링 화면 — 300문제 · 스토리 고침 → 기기 저장소
        await pg.goto(U + '#/_num/CONS'); await pg.wait_for_function("document.querySelectorAll('.nm-it').length>=300", timeout=30000)
        ok(await pg.evaluate("document.querySelectorAll('.nm-it').length") == 300, '넘버링 화면 300문제(기기 저장소에서)')
        iid = await pg.evaluate("document.querySelectorAll('.nm-it')[0].dataset.id"); loc = pg.locator('.nm-it').nth(0).locator('.nm-s .nm-c'); await loc.scroll_into_view_if_needed(); bx = await loc.bounding_box()
        await pg.mouse.click(bx['x'] + 30, bx['y'] + 8); await pg.wait_for_timeout(250); await pg.keyboard.press('Control+End'); await pg.keyboard.type(' 새로 쓴 글'); await pg.wait_for_timeout(1200); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
        ik = 'num.i.CONS.' + iid
        ok('새로 쓴 글' in (await pg.evaluate(f"__h.stGet('{ik}')") or '') and await pg.evaluate(f"localStorage.getItem('jblhub.v1.{ik}')") is None, '스토리 고침 → 기기 저장소에 저장(이 브라우저에는 없음)')
        p2 = await A.new_page(); ctxerr(p2, errs, 'A2'); await p2.goto(U + '#/'); await p2.wait_for_function("window.__h&&__h.XS.ready", timeout=30000)
        await pg.evaluate(f"(()=>{{const r=JSON.parse(__h.stGet('{ik}'));r.note='다른 창 시험';r.u=Date.now();__h.stSet('{ik}',JSON.stringify(r));}})()"); await p2.wait_for_timeout(600)
        ok('다른 창 시험' in (await p2.evaluate(f"__h.stGet('{ik}')") or ''), '다른 창에 바로 보임(BroadcastChannel)'); await p2.close()
        await pg.reload(); await pg.wait_for_function("document.querySelectorAll('.nm-it').length>=300", timeout=30000)
        ok('새로 쓴 글' in await pg.inner_text(f'.nm-it[data-id="{iid}"] .nm-s'), '새로고침 뒤 넘버링 스토리 그대로')
        await pg.screenshot(path=J.TMP + '/ux15_A_num.png')
        dA = await pg.evaluate(DIG, keys)
        # 백업 파일 내보내기
        await pg.goto(U + '#/'); await pg.wait_for_selector('.hsj[data-s="OMS1"]', timeout=30000)
        fa = J.TMP + '/ux15_A.json'; ja = await pg.evaluate("__h.xsReady().then(()=>JSON.stringify(__h.bakFile()))"); open(fa, 'w', encoding='utf-8').write(ja)
        dd = json.loads(ja)['data']; ok(sum(1 for k in dd if '.num.i.' in k) == 300 and sum(1 for k in dd if '.num.r.' in k) == 300, '백업 파일에 넘버링 문제 300·복습 기록 300(기기 저장소 몫 포함)')
        await pg.evaluate("document.querySelector('#bkup').click()"); await pg.wait_for_timeout(200); bt = await pg.inner_text('#bkstore'); ok('이 브라우저' in bt and '기기 저장소 넘버링' in bt, f'백업 창 저장 공간 줄 {bt!r}')
        await pg.click('#rstr'); await pg.wait_for_selector('#rpop .rstore'); st = await pg.inner_text('#rpop .rstore')
        ok('이 브라우저 기록' in st and '기기 저장소(IndexedDB) 넘버링' in st and '종류:' in st and '같은 주소의 다른 페이지' in st and '%' not in st, f'복원 창 저장 공간·종류별 {st[:160]!r}')
        await pg.evaluate("document.querySelector('#rclean').open=true"); await pg.wait_for_timeout(200); ok('기기 저장소(IndexedDB)에 있어요' in await pg.inner_text('#rclean'), '공간 정리 — 넘버링은 기기 저장소에 있어요')
        await pg.screenshot(path=J.TMP + '/ux15_A_rst.png'); await pg.keyboard.press('Escape')
        # ===== B: 빈 브라우저 — 자기 기록 + A 합치기 =====
        print('== B 빈 브라우저 — 합치기')
        B = await b.new_context(viewport={'width': 1280, 'height': 900}); pb = await B.new_page(); ctxerr(pb, errs, 'B'); pb.on('dialog', dlg)
        await lec(pb); wb = await mark(pb, 8)
        await pb.evaluate("localStorage.setItem('jblhub.v1.num.i.CONS.u:b1',JSON.stringify({id:'u:b1',k:'user',lec:'',q:'<p>B 기기 문제</p>',a:'<p>B 답</p>',st:'<p>B 스토리</p>',src:[{t:'user',s:'CONS',lab:'B'}],yrs:[],o:999,c:1,u:5}))")
        DLG.clear(); await pb.evaluate("window.__mark=1;document.querySelector('#rfile').dataset.how='merge'"); await pb.set_input_files('#rfile', fa)
        await pb.wait_for_function("!window.__mark", timeout=30000); await pb.wait_for_function("window.__h&&__h.XS&&__h.XS.ready", timeout=30000); await pb.wait_for_timeout(800)
        msg = DLG[0] if DLG else ''
        ok('더해지는 것' in msg and '형광펜·빈칸 +' in msg and '넘버링 새 문제 +300' in msg and '겹칠 때' in msg and '지우지 않아요' in msg, f'합치기 미리 보기 확인 창 {msg[:120]!r}')
        dB = await pb.evaluate(DIG, keys); bad = [k for k in keys if k != 'ann.OMS1' and dB[k] != dA[k]]
        ok(not bad, f'B에 A 기록 {len(keys) - 1}개 글자까지 같음 — 다름 {bad[:3]}')
        ok(await pb.evaluate(NANN + "('OMS1')") == 5 and bool(await pb.evaluate("__h.stGet('num.i.CONS.u:b1')")), 'B 자기 표시·넘버링도 남음(표시 4 + 1)')
        ok(await pb.locator('#rpop .mres').count() == 1 and '두 기기를 같게' in await pb.inner_text('#rpop .mres'), '합치기 결과 + 두 기기를 같게 안내')
        await pb.screenshot(path=J.TMP + '/ux15_B_merge.png')
        fb = J.TMP + '/ux15_B.json'; open(fb, 'w', encoding='utf-8').write(await pb.evaluate("__h.xsReady().then(()=>JSON.stringify(__h.bakFile()))"))
        await pg.goto(U + '#/'); await pg.wait_for_selector('.hsj[data-s="OMS1"]', timeout=30000)
        await pg.evaluate("window.__mark=1;document.querySelector('#rfile').dataset.how='merge'"); await pg.set_input_files('#rfile', fb)
        await pg.wait_for_function("!window.__mark", timeout=30000); await pg.wait_for_function("window.__h&&__h.XS&&__h.XS.ready", timeout=30000); await pg.wait_for_timeout(500)
        dA2 = await pg.evaluate(DIG, keys)
        ok(all(dA2[k] == dA[k] for k in keys if k != 'ann.OMS1') and await pg.evaluate(NANN + "('OMS1')") == 5 and bool(await pg.evaluate("__h.stGet('num.i.CONS.u:b1')")), 'B 파일을 A에 합침 → A에도 둘 다(A 기록 그대로)')
        await B.close()
        # ===== C: IndexedDB 없음 =====
        print('== C IndexedDB 없음(사생활 보호 모드 흉내)')
        C = await b.new_context(viewport={'width': 1280, 'height': 900}); await C.add_init_script("try{Object.defineProperty(window,'indexedDB',{value:undefined,configurable:true});}catch(e){}")
        pc = await C.new_page(); ctxerr(pc, errs, 'C'); pc.on('dialog', dlg)
        await pc.goto(BASE + 'icon-192.png'); sc = await pc.evaluate(SEED + "({n:20,st:5,target:3500000})")
        await lec(pc); await pc.wait_for_function("__h.XS.ready", timeout=15000); await pc.wait_for_timeout(5000)
        ok(await pc.evaluate("__h.XS.ok") is False and await pc.evaluate(LSNUM) == 20, '기기 저장소 없음 → 넘버링은 이 브라우저 그대로(옮기지 않음)')
        wc = await mark(pc, 0); ok(await pc.evaluate(NANN + "('OMS1')") == 1 and await pc.locator('#lserr').count() == 0, f'표시 저장({wc})')
        await pc.goto(U + '#/_num/CONS'); await pc.wait_for_function("document.querySelectorAll('.nm-it').length>=20", timeout=30000)
        cid = await pc.evaluate("document.querySelectorAll('.nm-it')[1].dataset.id"); loc = pc.locator('.nm-it').nth(1).locator('.nm-s .nm-c'); await loc.scroll_into_view_if_needed(); bx = await loc.bounding_box()
        await pc.mouse.click(bx['x'] + 30, bx['y'] + 8); await pc.wait_for_timeout(250); await pc.keyboard.press('Control+End'); await pc.keyboard.type(' C 글'); await pc.wait_for_timeout(1200); await pc.keyboard.press('Escape'); await pc.wait_for_timeout(400)
        ok('C 글' in (await pc.evaluate(f"localStorage.getItem('jblhub.v1.num.i.CONS.{cid}')") or ''), '넘버링 고침 → 이 브라우저(localStorage)에 저장(옛 방식)')
        jc = json.loads(await pc.evaluate("__h.xsReady().then(()=>JSON.stringify(__h.bakFile()))"))['data']; ok(sum(1 for k in jc if '.num.i.' in k) == 20, '백업 파일에 넘버링 20')
        await pc.goto(U + '#/'); await pc.wait_for_selector('.hsj[data-s="OMS1"]', timeout=30000); await pc.evaluate("document.querySelector('#bkup').click()"); await pc.click('#rstr'); await pc.wait_for_selector('#rpop .rstore')
        await pc.evaluate("document.querySelector('#rclean').open=true"); await pc.wait_for_timeout(200); ok('쓸 수 없어' in await pc.inner_text('#rclean'), '공간 정리 — 기기 저장소를 쓸 수 없어요(안내)')
        await C.close()
        # ===== D: 꽉 참 — 저장 실패 → 옮겨서 자리 만들기 =====
        print('== D 꽉 찬 브라우저(자동 옮김 끔)')
        D = await b.new_context(viewport={'width': 1280, 'height': 900}); pd = await D.new_page(); ctxerr(pd, errs, 'D'); pd.on('dialog', dlg)
        await pd.goto(BASE + 'icon-192.png'); sdd = await pd.evaluate(SEED + "({n:200,no:1,brim:1})"); dd0 = await pd.evaluate(DIGLS, sdd['keys'])
        ok(await pd.evaluate("(()=>{try{localStorage.setItem('zz.t','x'.repeat(2000));localStorage.removeItem('zz.t');return false;}catch(e){return true;}})()"), f"한도까지 채움 {sdd['used']:,}자")
        await lec(pd); wd = await mark(pd, 0)
        await pd.wait_for_function("__h.XS.on&&__h.LSQ.size===0", timeout=30000, polling=300); await pd.wait_for_timeout(500)
        ok(await pd.locator('#lserr').count() == 0 and await pd.evaluate("(()=>{const v=localStorage.getItem('jblhub.v1.ann.OMS1');return v?Object.values(JSON.parse(v)).flat().length:0})()") == 1, f'저장 실패 → 넘버링을 옮겨 자리 만듦 → 표시 저장({wd}) · 빨간 띠 없음')
        dd1 = await pd.evaluate(DIG, sdd['keys']); ok(all(dd1[k] == dd0[k] for k in sdd['keys']) and await pd.evaluate(LSNUM) == 0, '넘버링 200문제 글자 같음 · localStorage 넘버링 0')
        await D.close()
        # ===== E: 아이패드 사파리 — 바이트로 셈 =====
        print('== E 아이패드 사파리(UA) 820 세로')
        E = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True, user_agent='Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1')
        pe = await E.new_page(); ctxerr(pe, errs, 'E')
        await pe.goto(U + '#/'); await pe.wait_for_selector('.hsj[data-s="OMS1"]', timeout=60000)
        ok(await pe.evaluate("__h.WKS") is True and await pe.evaluate("__h.lsW('가나')") == 4 and await pe.evaluate("__h.lsW('ab')") == 2, '사파리: 한글이 든 값은 글자당 2바이트 · 라틴 글은 1')
        await pe.evaluate("localStorage.setItem('jblhub.v1.memo.OMS1.DD1','가'.repeat(100000))")
        ok(abs(await pe.evaluate("__h.lsScan().kind.memo") - 200000 - len('jblhub.v1.memo.OMS1.DD1')) < 5, '메모 10만 자 = 20만 바이트로 셈')
        await pe.evaluate("document.querySelector('#bkup').click()"); await pe.click('#rstr'); await pe.wait_for_selector('#rpop .rstore'); ste = await pe.inner_text('#rpop .rstore')
        ov = await pe.evaluate("(()=>{const p=document.querySelector('#rpop');return [document.documentElement.scrollWidth-innerWidth,p.scrollWidth-p.clientWidth];})()")
        ok('이 브라우저 기록' in ste and '메모' in ste and max(ov) <= 1, f'복원 창 저장 공간 줄 · 가로 넘침 {ov}'); await pe.screenshot(path=J.TMP + '/ux15_E_rst.png')
        await E.close()
        # ===== A 끝: 되돌리기 =====
        print('== A 되돌리기(기기 저장소 → 이 브라우저)')
        await pg.evaluate("(()=>{for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(k.indexOf('zz.')===0)localStorage.removeItem(k);}})()")
        r = await pg.evaluate("__h.xsBack().then(r=>JSON.stringify(r))"); r = json.loads(r)
        ok(r['ok'] and r['n'] == 601, f'되돌리기 {r}')
        dA3 = await pg.evaluate(DIGLS, keys); bad = [k for k in keys if k != 'ann.OMS1' and dA3[k] != dA2[k]]
        ok(not bad and await pg.evaluate("__h.XS.M.size") == 0 and await pg.evaluate("__h.XS.on") is False, f'되돌린 뒤 이 브라우저에 글자 같음 · 기기 저장소 비움 — 다름 {bad[:3]}')
        await pg.reload(); await pg.wait_for_function("window.__h&&__h.XS.ready", timeout=30000); await pg.wait_for_timeout(5000)
        ok(await pg.evaluate("__h.XS.on") is False and await pg.evaluate(LSNUM) == 601, '되돌린 뒤 다시 옮기지 않음(xs.no) · 새로고침 뒤 그대로')
        ok(not errs, f'pageerror 0 ({errs[:3]})')
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
    _sys.exit(1 if fails else 0)
asyncio.run(main())
