"""ux2 수정자 B 회귀 — 화면·터치·흐름(flow V01·V02·V03·V06·V08·V09·V12~V20 · VIS01~VIS14 · N1·N2). 맥 1280×900 · 아이패드 세로 820×1180(터치) · 가로 1180×820(터치)
V01 한 장씩: 애플펜슬(touchType stylus) 가로 긋기 → 카드 그대로 · 손가락 → 다음 카드
V02·V16 줄인 한 장씩 막대: 버튼 한 줄(글자 줄바꿈 0)·가로 넘침 0·'회차 n 고정 ↻'·'한 장씩 끝' 보임
V03 옛 사용자(1차 판 mk 기록) 허브 홈 '✨ 이번 업데이트' 카드 → [알겠어요] 사라짐 · 새 사용자 없음 · 도움말 '✨ 새로 생긴 것' → 그 줄
V06 JB 목록 맨 위: 첫 J = 1번 · 맨 위 O = 1번 채점 · V17 새 사용자 keyNotice 없음·요약 문구에 (mk) 없음
V08·V09 ⚡ ' / ' 줄 = 한 묶음(.mg)·○✕ 하나 · 복습 보기 줄 ○✕는 몰라요 카드만·범례 · V18 제목 탭 → [↩ 복습 보기로]
V12 위 막대 누름 자리 44px·👁 40px · V13 [요약|자세히]·[모든 주제…] · V14 카드형 칸 이름 👁 → 가림 + [되돌리기] · V15 세로 탭 줄 넘침 0·⤢ 하나
V19 한눈표 답 가리기 행 높이·✓✗★ 한 줄 · V20 한 장씩 답 열기 전 이전 채점 숨김
VIS01 ★ 칸 반쯤 잘린 줄 0·답 보임 · VIS02 820 전체정리표 넘침 0 · VIS03 ⚡ 줄임 없음 · VIS04 영어 낱말 중간 끊김 0(DD1) · VIS05 점 두 개 0 · VIS07 정답 라벨
VIS09 ✎가 본문을 가리지 않음·플래시카드 판정 버튼이 도구 막대 위 · VIS10 JB 표 답 행 · VIS12 강의 카드 2단·💬 따옴표 안 끊김 · VIS13 '해당 없음' → '—'(글자 그대로)
VIS14 미복원 문항 prof 칩 없음·안 푼 것·회차 제외 · N1 PHARM CHR 번호 나열 한 모양 · N2 첫 전체정리표 기본 펼침 · 스크린샷 work/_tmp/ux2f_*.png"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, re
from playwright.async_api import async_playwright
U = J.HUB_URL; NS = 'jblhub.v1.'; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def SHOT(n, tag): return J.TMP + f'/ux2f_{n}_{tag}.png'
async def open_(pg, h, sel='#stage'):
    await pg.goto('about:blank'); await pg.goto(U + h)
    try: await pg.wait_for_function(f"document.querySelector({json.dumps(sel)})&&window.__h", timeout=15000)
    except Exception: pass
    await pg.wait_for_timeout(500)
async def ls(pg, k): return json.loads(await pg.evaluate(f"localStorage.getItem('{NS}{k}')") or 'null')
async def clean(pg):
    await open_(pg, '#/'); await pg.evaluate("localStorage.clear();sessionStorage.clear()"); await open_(pg, '#/')
async def key(pg, k, w=250): await pg.keyboard.press(k); await pg.wait_for_timeout(w)
async def grade5(pg):
    for _ in range(5):
        await pg.evaluate("document.querySelector('#ong').click()"); await pg.wait_for_timeout(80)
        await pg.evaluate("document.querySelector('#onext').click()"); await pg.wait_for_timeout(80)
BAR = """(()=>{const b=document.querySelector('#jbbar .b1');const els=[...b.querySelectorAll('.tg,button,select')].filter(e=>e.offsetParent&&getComputedStyle(e).display!=='none');
 const multi=els.filter(e=>{if(e.tagName==='SELECT')return false;const r=document.createRange();r.selectNodeContents(e);const T=[...r.getClientRects()].filter(x=>x.width>1&&x.height>4).map(x=>x.top);return T.length&&Math.max(...T)-Math.min(...T)>8;}).map(e=>e.id||e.dataset.qf||e.textContent.trim().slice(0,8));
 const f=document.querySelector('#fone').getBoundingClientRect(),br=b.getBoundingClientRect(),rc=document.querySelector('#jbrec');
 return {sw:b.scrollWidth,cw:b.clientWidth,h:Math.round(b.offsetHeight),multi,fone:[Math.round(f.left),Math.round(f.right),Math.round(br.right)],fonet:document.querySelector('#fone').innerText.trim(),rec:rc&&rc.offsetParent?rc.innerText.trim():''};})()"""
STYLUS = """async ([type])=>{const c=__h.JB.vis[__h.JB.cur];const tw=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);let n,best=null;while(n=tw.nextNode()){if(n.nodeValue.trim().length>12&&!n.parentElement.closest('button,.chip,.noann')){best=n;break;}}
 const r=document.createRange();r.setStart(best,0);r.setEnd(best,1);const b=r.getBoundingClientRect();const x0=Math.min(innerWidth-60,b.left+220),y0=b.top+b.height/2;const tgt=best.parentElement;
 const mk=(x,y)=>{const T=new Touch({identifier:1,target:tgt,clientX:x,clientY:y,pageX:x,pageY:y+scrollY,touchType:type,radiusX:1,radiusY:1,force:0.5});if(T.touchType!==type)Object.defineProperty(T,'touchType',{value:type});return T;};   /* 크로미움 Touch에는 touchType이 없어 아이패드 사파리처럼 심음 */
 const fire=(t,x,y)=>{const T=mk(x,y);tgt.dispatchEvent(new TouchEvent(t,{bubbles:true,cancelable:true,touches:t==='touchend'?[]:[T],targetTouches:t==='touchend'?[]:[T],changedTouches:[T]}));};
 const before=__h.JB.cur;fire('touchstart',x0,y0);for(let i=1;i<=10;i++){await new Promise(r=>setTimeout(r,16));fire('touchmove',x0-i*16,y0+(i%2));}
 await new Promise(r=>setTimeout(r,20));fire('touchend',x0-160,y0+1);await new Promise(r=>setTimeout(r,500));return [before,__h.JB.cur];}"""
PARTIAL = """(()=>{let n=0;document.querySelectorAll('#stage .msum td.mt .mexb, #stage .msum td.mt .ex-q, #stage .msum td.mt .ex-a, #stage .msum td.mnote .ci').forEach(el=>{if(!el.offsetParent)return;const cs=getComputedStyle(el);if(cs.overflow!=='hidden'&&cs.overflowY!=='hidden')return;const b=el.getBoundingClientRect();const r=document.createRange();r.selectNodeContents(el);if([...r.getClientRects()].some(x=>x.height>4&&x.width>2&&x.top<b.bottom-2&&x.bottom>b.bottom+2))n++;});return n;})()"""
MIDW = """(()=>{let n=0;const ex=[];const w=document.createTreeWalker(document.querySelector('#stage'),NodeFilter.SHOW_TEXT);let t;const r=document.createRange();while(t=w.nextNode()){const v=t.nodeValue;if(!/[A-Za-z]{2}/.test(v)||!t.parentElement.offsetParent)continue;r.selectNodeContents(t);if(r.getClientRects().length<2)continue;let prev=null;
 for(let i=0;i<v.length;i++){r.setStart(t,i);r.setEnd(t,i+1);const b=r.getClientRects()[0];if(!b)continue;if(prev&&b.top>prev.top+4&&/[A-Za-z]/.test(prev.ch)&&/[A-Za-z]/.test(v[i])){n++;ex.push(v.slice(Math.max(0,i-8),i)+'|'+v.slice(i,i+5));}prev={top:b.top,ch:v[i]};}}return [n,ex.slice(0,3)];})()"""

async def mac(b):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); tag = 'mac'
    await clean(pg)
    # ---- V03 새 사용자 = 카드 없음 · V17 keyNotice 없음
    ok(not await pg.evaluate("document.querySelector('#wnew')") and await ls(pg, 'ux2old') == 0, "V03 새 사용자(기록 없음) → '이번 업데이트' 카드 없음 · ux2old=0")
    await open_(pg, '#/OMS1/_jb/_jb'); await pg.click('#fone'); await pg.wait_for_timeout(1500)
    t = await pg.evaluate("[...JSON.parse(sessionStorage.getItem('jblhub.v1.toasts')||'[]')].map(x=>x.t).join(' | ')")
    ok('★는 이제 S' not in t, f'V17 새 사용자 한 장씩 → keyNotice 없음 ({t[:60]!r})')
    await pg.evaluate("(()=>{let g=0;while(document.querySelector('#opos').textContent!=='요약'&&g++<400)document.querySelector('#onext').click();})()"); await pg.wait_for_timeout(300)
    t = await pg.inner_text('#onesum'); ok('(mk)' not in t and '채점 기록에도 저장' in t, f'V17 회차 요약 문구 {t[t.find("맞음·틀림"):][:40]!r}')
    await pg.click('#fone'); await pg.wait_for_timeout(300)
    # ---- V06 맨 위 첫 J = 1번 · 맨 위 O = 1번
    await pg.evaluate("localStorage.removeItem('jblhub.v1.mk.PHARM');sessionStorage.clear();localStorage.removeItem('jblhub.v1.jbst.PHARM._jb')")
    await open_(pg, '#/PHARM/_jb/_jb'); await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(300)
    lc0 = await pg.evaluate("__h.JB.lc?__h.JB.vis.indexOf(__h.JB.lc):-1")
    await key(pg, 'j', 400); r = await pg.evaluate("[__h.JB.vis.indexOf(__h.JB.lc),__h.JB.vis[0].dataset.id]")
    ok(r[0] == (0 if lc0 < 0 else lc0 + 1), f'V06 맨 위(지금 카드 {lc0}) 첫 J → {r[0]}번째(0 = 1번 {r[1]})')
    await open_(pg, '#/PHARM/_jb/_jb'); await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(300)
    lc0 = await pg.evaluate("__h.JB.lc?__h.JB.lc.dataset.id:null"); first = await pg.evaluate("__h.JB.vis[0].dataset.id")
    await key(pg, 'o', 300); m = await ls(pg, 'mk.PHARM') or {}
    ok((m.get('ok') or {}).get(lc0 or first) == 1, f'V06 맨 위에서 O → 그 카드({lc0 or first}) 맞음')
    # ---- V08·V09·V18 ⚡ 묶음·복습 보기
    await open_(pg, '#/OMS1/DD2/learn', '#stage .tc')
    r = await pg.evaluate("(()=>{const L=[...document.querySelectorAll('#t-DD2-0 .c-mem li.mg')];return [L.length,new Set(L.map(l=>l.dataset.fk)).size,L.filter(l=>l.querySelector('.mj')).length,L.length?L[L.length-1].classList.contains('mgz'):false]})()")
    ok(r[0] == 2 and r[1] == 1 and r[2] == 1 and r[3], f"V08 DD2 카드 1 ' / ' 줄 = 묶음 li {r[0]}·키 {r[1]}·○✕ {r[2]}(끝 줄)")
    await pg.evaluate("document.querySelector('#lmrev').click()"); await pg.wait_for_timeout(400)
    r = await pg.evaluate("[[...document.querySelectorAll('#stage .tc:not(.rv-x) .c-mem .mj')].filter(e=>e.offsetParent).length,!!document.querySelector('#stage .rvleg').offsetParent]")
    ok(r[0] == 0 and r[1], f'V09 복습 보기: 몰라요 아닌 카드 줄 ○✕ 보임 {r[0]} · 범례 {r[1]}')
    await pg.evaluate("document.querySelector('#t-DD2-1 .rvj [data-rv=x]').click()"); await pg.wait_for_timeout(200)
    r = await pg.evaluate("[...document.querySelectorAll('#t-DD2-1 .c-mem .mj')].filter(e=>e.offsetParent).length")
    ok(r > 0, f'V09 몰라요 카드 → 줄 ○✕ {r}개 보임')
    await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(150); await pg.screenshot(path=SHOT('v09_review', tag))
    await pg.evaluate("document.querySelector('#t-DD2-2 .thead .ko').click()"); await pg.wait_for_timeout(500)
    r = await pg.evaluate("[document.querySelector('#stage').classList.contains('review'),(document.querySelector('#toast .tact')||{}).textContent||'']")
    ok(not r[0] and '복습 보기로' in r[1], f'V18 제목 탭 → 복습 보기 꺼짐·[{r[1]}]')
    if r[1]: await pg.evaluate("document.querySelector('#toast .tact').click()"); await pg.wait_for_timeout(400)
    ok(await pg.evaluate("document.querySelector('#stage').classList.contains('review')"), 'V18 [↩ 복습 보기로] → 다시 켜짐')
    await pg.evaluate("document.querySelector('#lmrev').click()"); await pg.wait_for_timeout(200)
    # ---- V13 정리표 막대 라벨 · VIS03 ⚡ 줄임 없음 · VIS04 낱말 중간 끊김
    await open_(pg, '#/OMS1/DD1/sum', '#stage .msum')
    r = await pg.evaluate("[document.querySelector('[data-mdense=f]').textContent,document.querySelector('[data-mfilt=\"\"]').textContent,[...document.querySelectorAll('#msbar .pglab')].map(e=>e.textContent)]")
    ok(r[0] == '자세히' and r[1] == '모든 주제' and r[2] == ['보기', '주제'], f'V13 정리표 막대 {r}')
    r = await pg.evaluate("[...document.querySelectorAll('#stage .msum td.mnote .ci')].filter(c=>c.offsetParent&&c.scrollHeight>c.clientHeight+2).length")
    ok(r == 0, f'VIS03 요약 ⚡ 줄 잘림 {r}')
    r = await pg.evaluate(MIDW); ok(r[0] == 0, f'VIS04 1280 DD1 정리표 영어 낱말 중간 줄바꿈 {r}')
    ok(await pg.evaluate(PARTIAL) == 0, 'VIS01 1280 DD1 반쯤 잘린 줄 0')
    # ---- VIS07 부정 발문 정답 라벨
    await open_(pg, '#/PHARM/_jb/_jb')
    r = await pg.evaluate("""(()=>{const c=document.querySelector('#c-RX01'),a=c.querySelector('.qtext .ln.li[data-ans]');c.querySelector('.acts [data-tog]').click();return [getComputedStyle(a,'::before').content,getComputedStyle(a,'::before').color,(c.querySelector('.ln.pick')||{}).textContent||'']})()""")
    ok('정답 · 틀린 설명' in r[0] and r[1] == 'rgb(30, 107, 63)' and r[2].startswith('정답 · 틀린 설명'), f'VIS07 틀린 것 고르기 답 = 초록 ✓ 정답 · 틀린 설명 {r[0]} {r[1]} · 줄 {r[2][:20]!r}')
    # ---- VIS10 JB 표 답
    await open_(pg, '#/OMS1/_sum')
    r = await pg.evaluate("[...document.querySelectorAll('#stage tr[data-id=\"J4\"] td[data-col=ans] .ln')].map(e=>e.textContent.trim())")
    ok('Bicoronal Brachycephaly Short skull' in r and 'Lambdoid Plagiocephaly Asymmetric skull' in r and 'skull' not in r, f'VIS10 두개골 조기 유합증 표 행 {[x for x in r if "skull" in x][:5]}')
    # ---- VIS13 '해당 없음'
    await open_(pg, '#/CONS/ADH/sum', '#stage .msum')
    r = await pg.evaluate("(()=>{const e=document.querySelector('#stage .na');if(!e)return null;return [e.textContent,getComputedStyle(e,'::after').content,getComputedStyle(e).fontSize]})()")
    ok(r and r[0] == '해당 없음' and '—' in r[1] and r[2] == '0px', f"VIS13 '해당 없음' 칸 = 화면 '—'·글자 그대로 {r}")
    # ---- N1 PHARM CHR 번호 나열
    await open_(pg, '#/PHARM/CHR/learn', '#stage .tc')
    r = await pg.evaluate("[document.querySelectorAll('#t-CHR-0 .li.cont').length,[...document.querySelectorAll('#t-CHR-0 .li')].filter(l=>/^[①②③④]/.test(l.textContent.trim())).length]")
    ok(r[0] == 0 and r[1] == 4, f'N1 CHR 카드 1 ①~④ 같은 모양(.li {r[1]} · 이어 번호 목록 {r[0]})')
    # ---- N2 첫 전체정리표 펼침
    await open_(pg, '#/PHARM/CHR/sum', '#stage .msum')
    ok(await pg.evaluate("document.querySelector('#sumtop .stbl[data-sti=\"0\"]').offsetParent!==null"), 'N2 PHARM CHR 첫 전체정리표 기본 펼침')
    await pg.evaluate("document.querySelector('#sumtop [data-sttab=\"0\"]').click()"); await pg.wait_for_timeout(150)
    await open_(pg, '#/PHARM/CHR/sum', '#stage .msum')
    ok(await pg.evaluate("document.querySelector('#sumtop .stbl[data-sti=\"0\"]').offsetParent===null") and await ls(pg, 'sumtop.PHARM.CHR') == 'none', 'N2 접으면 기억(새로고침 뒤 접힘)')
    # ---- V03 옛 사용자 카드
    await pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('jblhub.v1.mk.OMS1',JSON.stringify({ok:{Q01:1},ng:{},bm:{},log:{}}))")
    await open_(pg, '#/'); await pg.wait_for_function("__h.plStat().pend===0", timeout=20000); await pg.wait_for_timeout(500)
    r = await pg.evaluate("[0,!!document.querySelector('#wnew'),(document.querySelector('#wnew')||{}).textContent||'']")
    ok(r[1] and '이번 업데이트' in r[2] and await ls(pg, 'ux2old') == 1, f"V03 옛 사용자 → 허브 홈 '✨ 이번 업데이트' 카드 {r[2][:50]!r}")
    await pg.screenshot(path=SHOT('v03_whatsnew', tag))
    await pg.evaluate("document.querySelector('#wnew [data-wnh]').click()"); await pg.wait_for_timeout(400)
    r = await pg.evaluate("[document.querySelector('#help').classList.contains('on'),(document.querySelector('#help tr.flash th')||{}).textContent||'']")
    ok(r[0] and r[1] == '왼쪽 메뉴 M', f'V03 카드 [도움말 ▸] → 도움말의 그 줄 {r}')   # ux3 P2: 카드 = 3차 안내(첫 줄 🧭 왼쪽 메뉴)
    await pg.evaluate("document.querySelector('#helpx').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('#wnew [data-wnx]').click()"); await pg.wait_for_timeout(200)
    await open_(pg, '#/')
    ok(not await pg.evaluate("document.querySelector('#wnew')") and await ls(pg, 'whatsNew.3') == 1, "V03 [알겠어요] → 다시 안 보임(LS whatsNew.3 — ux3 P2)")
    ok(not errs, f'{tag}: pageerror 0 {errs[:2]}')
    await ctx.close()

async def ipad(b, w, h):
    tag = 'ipp' if w < 1000 else 'ipl'
    ctx = await b.new_context(viewport={'width': w, 'height': h}, has_touch=True); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await clean(pg)
    # ---- V02·V16 줄인 막대
    await open_(pg, '#/OMS1/_jb/_jb'); await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(400); await grade5(pg); await pg.wait_for_timeout(300)
    r = await pg.evaluate(BAR)
    ok(not r['multi'] and r['sw'] <= r['cw'] + 1 and r['h'] <= 52, f"V02 {w} 한 장씩 막대 한 줄 — 두 줄 버튼 {r['multi']} · 넘침 {r['sw']}/{r['cw']} · 높이 {r['h']}")
    ok(r['fone'][1] <= r['fone'][2] + 1 and r['fonet'] == '한 장씩 끝' and r['rec'].startswith('회차 '), f"V02·V16 '한 장씩 끝' 보임 {r['fone']} · 칩 {r['rec']!r}")
    await pg.screenshot(path=SHOT('v02_bar', tag))
    # ---- V20 이전 채점 숨김(새 회차)
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(300)
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(500)
    await pg.evaluate("__h.JB.cur=0;__h.JB.show()"); await pg.wait_for_timeout(200)
    r = await pg.evaluate("(()=>{const c=__h.JB.vis[__h.JB.cur];return [c.dataset.id,c.classList.contains('mk-ng'),c.classList.contains('pvh'),document.querySelector('#ong').classList.contains('on'),getComputedStyle(c.querySelector('.qhead .chip.rec')||c).display]})()")
    ok(r[1] and r[2] and not r[3] and r[4] == 'none', f'V20 새 회차 첫 카드({r[0]}, 지난번 ✗): 답 열기 전 ✗ 채움·기록 칩 숨김 {r[1:]}')
    await pg.screenshot(path=SHOT('v20_front', tag))
    await pg.evaluate("document.querySelector('#otog').click()"); await pg.wait_for_timeout(300)
    r = await pg.evaluate("[document.querySelector('#ong').classList.contains('on'),__h.JB.vis[__h.JB.cur].classList.contains('pvh')]")
    ok(r[0] and not r[1], f'V20 답을 열면 이전 채점 보임 {r}')
    # ---- VIS09 ✎가 본문을 가리지 않음
    r = await pg.evaluate("(()=>{const c=__h.JB.vis[__h.JB.cur].getBoundingClientRect(),k=document.querySelector('#k-min').getBoundingClientRect();return [Math.round(c.right),Math.round(k.left),k.width>0]})()")
    ok(not r[2] or r[0] <= r[1] + 2 or w < 700, f'VIS09 {w} 한 장씩 카드 오른쪽 {r[0]} ≤ ✎ 왼쪽 {r[1]}')
    await pg.screenshot(path=SHOT('vis09_one', tag))
    # ---- V01 펜슬 가로 긋기
    if w < 1000:
        r = await pg.evaluate(STYLUS, ['stylus']); ok(r[0] == r[1], f'V01 애플펜슬 가로 긋기 → 카드 그대로 {r}')
        r = await pg.evaluate(STYLUS, ['direct']); ok(r[1] == r[0] + 1, f'V01 손가락 가로 쓸기 → 다음 카드 {r}')
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(300)
    # ---- VIS14 미복원
    await open_(pg, '#/IMPL/_jb/_jb')
    r = await pg.evaluate("[[...document.querySelectorAll('#cards .qc .chip.pf')].filter(c=>c.offsetParent&&!c.textContent.trim()).length,document.querySelectorAll('#cards .qc[data-unrec]').length,+document.querySelector('#jbbar [data-qf=todo] .qn').textContent,document.querySelectorAll('#cards .qc').length]")
    ok(r[0] == 0 and r[1] == 3 and r[2] == r[3] - 3, f'VIS14 IMPL 빈 교수 칩 {r[0]} · 미복원 {r[1]} · 안 푼 것 {r[2]} = 전체 {r[3]} − 3')
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(400)
    r = await pg.evaluate("__h.JB.vis.filter(c=>c.dataset.unrec).length"); ok(r == 0, f'VIS14 한 장씩 회차에 미복원 {r}')
    await pg.evaluate("document.querySelector('#fone').click()"); await pg.wait_for_timeout(300)
    # ---- VIS01 ★ 칸 · VIS02 전체정리표
    await open_(pg, '#/OMS1/DD1/sum', '#stage .msum')
    ok(await pg.evaluate(PARTIAL) == 0, f'VIS01 {w} DD1 정리표 반쯤 잘린 줄 0')
    r = await pg.evaluate("[...document.querySelectorAll('#stage .msum td.mt .mex:not(.mexx)')].filter(m=>m.offsetParent&&m.querySelector('.exh>.ex-a')&&!(m.querySelector('.exh>.ex-a').offsetHeight>0)).length")
    ok(r == 0, f'VIS01 {w} 구조화 ⭐의 답(→) 안 보이는 칸 {r}')
    await pg.evaluate("document.querySelector('#stage .msum').scrollIntoView()"); await pg.wait_for_timeout(200); await pg.screenshot(path=SHOT('vis01_sum', tag))
    if w < 1000:
        for h_ in ['#/GERI/SAL/sum', '#/IMPL/HIS/sum', '#/CONS/ADH/sum']:
            await open_(pg, h_, '#stage .msum')
            await pg.evaluate("document.querySelectorAll('#sumtop .stbl.stoff').forEach(t=>t.classList.remove('stoff'))"); await pg.wait_for_timeout(400)
            r = await pg.evaluate("[...document.querySelectorAll('#sumtop .tblwrap.stbl')].map(w=>{const x=w.querySelector('.tscroll')||w,t=w.querySelector('table');return t.scrollWidth-x.clientWidth})")
            ok(all(x <= 1 for x in r), f'VIS02 820 {h_} 전체정리표 가로 넘침 {r}')
        await open_(pg, '#/GERI/SAL/sum', '#stage .msum'); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(()=>{const w=document.querySelector('#sumtop .stcard');if(!w)return null;const tr=w.querySelector('tbody tr'),th=tr.querySelector('th'),k=tr.querySelector('td.keycell');if(!k)return 'nokey';const kt=k.getBoundingClientRect().top;return [th.getBoundingClientRect().top<kt,[...tr.querySelectorAll('td')].filter(x=>x!==k).every(x=>x.getBoundingClientRect().top>kt),getComputedStyle(tr.querySelector('td'),'::before').content]})()")
        if r is None:   # ux3 L4: 열 폭을 맞춰(twApply) 넘치지 않으면 표 그대로 — 카드형은 5열↑·폭 760 미만에서 열이 모자랄 때만
            r2 = await pg.evaluate("[...document.querySelectorAll('#sumtop .tblwrap.stbl:not(.stoff)')].map(w=>{const x=w.querySelector('.tscroll')||w,t=w.querySelector('table');return [t.classList.contains('tw'),Math.round(t.scrollWidth-x.clientWidth)]})")
            ok(r2 and all(a and o <= 1 for a, o in r2), f'VIS02 넘치는 표 없음(ux3 L4 열 폭 맞춤 — 카드형 대신 표) {r2}')
        else: ok(r != 'nokey' and r[0] and r[1] and r[2] not in ('none', 'normal'), f'VIS02 넘치는 표 = 카드형(항목 → ★ 시험 → 나머지 · 열 이름) {r}')
        await pg.screenshot(path=SHOT('vis02_sumtop', tag))
        # ---- V14 카드형 칸 이름 👁
        await open_(pg, '#/CONS/WHT/sum', '#stage .msum')
        a0 = await pg.evaluate("localStorage.getItem('jblhub.v1.ann.CONS')")
        p_ = await pg.evaluate("(()=>{const td=document.querySelector('#m-WHT-1 td[data-col=mem]');td.scrollIntoView({block:'center'});const r=td.getBoundingClientRect();return [r.left+30,r.top+14,getComputedStyle(td,'::before').content]})()")
        await pg.touchscreen.tap(p_[0], p_[1]); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[document.querySelectorAll('#stage .msum td.cov[data-col=mem]').length,(document.querySelector('#toast .tact')||{}).textContent||'']")
        ok(r[0] > 5 and r[1] == '되돌리기' and '👁' in p_[2], f"V14 카드형 '⚡ 암기 👁' 칩 탭 → 칸 {r[0]}개 가림 · 알림 [{r[1]}]")
        await pg.screenshot(path=SHOT('v14_cov', tag))
        if r[1]: await pg.evaluate("document.querySelector('#toast .tact').click()"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("document.querySelectorAll('#stage .msum td.cov').length") == 0 and a0 == await pg.evaluate("localStorage.getItem('jblhub.v1.ann.CONS')"), 'V14 [되돌리기] → 가림 풀림 · ann 불변')
        ok(await pg.evaluate("(()=>{const n=document.querySelector('.msum .mshn,#msbar .mshn'),w=document.querySelector('#msbar .mshw');return !!(n&&n.offsetParent&&w&&!w.offsetParent)})()"), 'V14 카드형 안내 문구(칸 이름의 👁)')
        # ---- V15 탭 줄
        await open_(pg, '#/OMS1/DD1/learn', '#stage .tc')
        r = await pg.evaluate("[document.querySelector('#dtabs').scrollWidth-document.querySelector('#dtabs').clientWidth,getComputedStyle(document.querySelector('#focusb')).display,[...document.querySelectorAll('#dtabs .dfoc')].filter(e=>e.offsetParent).length]")
        ok(r[0] <= 1 and r[1] == 'none' and r[2] == 1, f'V15 820 탭 줄 넘침 {r[0]} · 위 막대 ⤢ {r[1]} · 탭 줄 ⤢ {r[2]}')
        await pg.screenshot(path=SHOT('v15_tabs', tag))
        # ---- V12 누름 자리
        r = await pg.evaluate("[Math.round(document.querySelector('#helpb').getBoundingClientRect().height),Math.round(document.querySelector('#clock').getBoundingClientRect().height),Math.round(document.querySelector('#bkup').getBoundingClientRect().height)]")
        ok(min(r) >= 44, f'V12 위 막대 도움말·시계·백업 높이 {r} ≥ 44')
        await open_(pg, '#/OMS1/_sum')
        r = await pg.evaluate("(()=>{const e=[...document.querySelectorAll('#stage .coveye')].find(x=>x.offsetParent);const b=e.getBoundingClientRect();return [Math.round(b.width),Math.round(b.height)]})()")
        ok(min(r) >= 40, f'V12 👁 {r} ≥ 40')
        # ---- V19 한눈표 답 가리기
        await pg.evaluate("document.querySelector('[data-sumhide]').click()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(()=>{const hs=[...document.querySelectorAll('#stage table.sum>tbody>tr')].filter(r=>r.offsetParent).map(r=>r.offsetHeight).sort((a,b)=>a-b);const s=document.querySelector('#stage table.sum .smk');const tops=new Set([...s.querySelectorAll('button')].map(b=>Math.round(b.getBoundingClientRect().top)));return [hs[hs.length>>1],hs[hs.length-1],tops.size]})()")
        ok(r[0] <= 170 and r[2] == 1, f'V19 답 가리기 행 높이 중앙값 {r[0]}·최대 {r[1]} · ✓✗★ 한 줄 {r[2] == 1}')
        await pg.screenshot(path=SHOT('v19_sumhide', tag))
        # ---- VIS12 과목 홈 강의 카드
        await open_(pg, '#/OMS1/_home')
        r = await pg.evaluate("[getComputedStyle(document.querySelector('.lgrid')).gridTemplateColumns.split(' ').length,[...document.querySelectorAll('.lcard .lh')].filter(e=>(e.textContent.match(/\"/g)||[]).length%2).length]")
        ok(r[0] == 2 and r[1] == 0, f'VIS12 820 강의 카드 {r[0]}단 · 💬 따옴표 안에서 끊긴 카드 {r[1]}')
        await pg.evaluate("document.querySelector('.lgrid').scrollIntoView()"); await pg.wait_for_timeout(200); await pg.screenshot(path=SHOT('vis12_home', tag))
        # ---- VIS09 플래시카드 판정 버튼
        await open_(pg, '#/OMS1/DD1/flash')
        await pg.evaluate("(()=>{const b=[...document.querySelectorAll('#stage [data-fk],#stage .tg')].find(x=>/기출/.test(x.textContent));if(b)b.click();})()"); await pg.wait_for_timeout(300)
        await pg.evaluate("document.querySelector('#fcard').click()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(()=>{const j=document.querySelector('#fc .fcjudge').getBoundingClientRect(),k=document.querySelector('#kit');const kt=k&&k.offsetParent?k.getBoundingClientRect().top:innerHeight;return [Math.round(j.bottom),Math.round(kt)]})()")
        ok(r[0] <= r[1] + 1, f'VIS09 플래시카드 뒷면 판정 버튼 아래 {r[0]} ≤ 도구 막대 위 {r[1]}')
        await pg.screenshot(path=SHOT('vis09_flash', tag))
    else:
        r = await pg.evaluate(MIDW); ok(r[0] == 0, f'VIS04 1180 DD1 정리표 영어 낱말 중간 줄바꿈 {r}')
        # ---- VIS05 점 두 개
        await open_(pg, '#/ANAT/NV/sum', '#stage .msum'); await pg.evaluate("document.querySelector('[data-mdense=f]').click()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[...document.querySelectorAll('#stage .ci')].filter(el=>{if(!el.offsetParent)return false;const b=getComputedStyle(el,'::before');const f=el.firstElementChild;return b.display!=='none'&&b.content!=='none'&&f&&/^(UL|OL)$/.test(f.tagName)}).length")
        ok(r == 0, f'VIS05 ANAT NV 정리표(자세히) 점 두 개 {r}')
        await pg.screenshot(path=SHOT('vis05_nv', tag))
    ok(not errs, f'{tag}: pageerror 0 {errs[:2]}')
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await mac(b); await ipad(b, 820, 1180); await ipad(b, 1180, 820)
        await b.close()
    idx = open(J.DOCS + '/index.html', encoding='utf-8').read()
    ok(re.search(r'PSZ=\{"OMS1":\s*[\d.]+', idx) is not None, 'V11 허브에 팩 크기(PSZ) — 첫 방문 진행 막대 MB')
    print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); _sys.exit(1 if fails else 0)
asyncio.run(main())
