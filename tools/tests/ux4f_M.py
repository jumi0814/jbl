"""ux4f M 회귀 — 사용자 10-02 '이미 하이라이트한 곳에서 추가 하이라이트 포함해서 드래그하면 기존 하이라이트 일부가 사라지는 오류'
무작위 드래그(고정 씨앗 — 기존 형광펜 안에서 시작·끝나는 드래그 70%, 여러 줄에 걸침) 뒤 기존에 칠한 글자가 하나도 빠지지 않음(합집합) · 새로고침 뒤에도 같음.
(4차 중간본 e001e1b에서는 27번 중 15번 일부가 사라졌음 — ux4f C56 clearOverlap이 겹친 부분만 다룸)"""
import os as _os, sys, random; sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
U=J.HUB_URL;W="window.__h&&__h.plStat&&__h.plStat().pend===0&&document.querySelector('#nav .ni')"
# 블록(카드 본문) 전체 글자 기준 좌표·덮임
PICK="""(k)=>{const L=[...document.querySelectorAll('#stage .tc.open .tbody')].filter(b=>b.offsetParent&&b.textContent.length>300);window.__b=L[k%L.length].closest('.tc');const li=window.__b.querySelectorAll('.tbody li');const t=li[Math.min(2,li.length-1)];(t||window.__b).scrollIntoView({block:'center'});return window.__b.id}"""
TXT="""()=>__h.Kit.textOf(window.__b)"""
XY="""(i)=>{const B=window.__b;const w=document.createTreeWalker(B,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement.closest('.noann,.thead')?2:1});let n,k=i;while(n=w.nextNode()){if(k<n.nodeValue.length)break;k-=n.nodeValue.length;}if(!n)return null;const r=document.createRange();r.setStart(n,k);r.setEnd(n,Math.min(n.nodeValue.length,k+1));const q=r.getClientRects()[0];return q&&q.top>60&&q.bottom<innerHeight-90?[q.left+1,q.top+q.height/2]:null}"""
COV="""()=>{const B=window.__b;const out=[];let pos=0;const w=document.createTreeWalker(B,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement.closest('.noann,.thead')?2:1});let n;while(n=w.nextNode()){const h=n.parentElement.closest('[data-rk=h]');for(let j=0;j<n.nodeValue.length;j++)if(h)out.push(pos+j);pos+=n.nodeValue.length;}return [out,pos]}"""
random.seed(3);bad=0;tot=0
with sync_playwright() as p:
  b=p.chromium.launch();c=b.new_context(viewport={'width':1280,'height':900});pg=c.new_page();E=[]
  pg.on('pageerror',lambda e:E.append(str(e)))
  pg.goto(U+'#/');pg.evaluate("localStorage.clear();localStorage.setItem('jblhub.v1.whatsNew.4','1')")
  for lec in ['CONS/WHT','OMS1/DD1','GERI/PAIN','ANAT/MAND']:
    pg.goto('about:blank');pg.goto(U+'#/'+lec+'/learn');pg.wait_for_function(W,timeout=60000);pg.wait_for_timeout(800);pg.keyboard.press('h')
    for k in range(4):
      bid=pg.evaluate(PICK,random.randint(0,50));pg.wait_for_timeout(300)
      for step in range(5):
        before,N=pg.evaluate(COV)
        if before and random.random()<.7:
          x=random.choice(before);d=random.randint(30,160);i,j=(x,min(N-1,x+d)) if random.random()<.5 else (max(0,x-d),x)
        else: i=random.randint(0,N-200);j=i+random.randint(30,160)
        a=pg.evaluate(XY,i);z=pg.evaluate(XY,j)
        if not a or not z or abs(a[1]-z[1])+abs(a[0]-z[0])<20: continue
        tot+=1;pg.mouse.move(a[0],a[1]);pg.mouse.down();pg.mouse.move(z[0]+4,z[1],steps=10);pg.mouse.up();pg.wait_for_timeout(400)
        after,_=pg.evaluate(COV);lost=sorted(set(before)-set(after))
        if lost:
          bad+=1;print('LOST',lec,bid,'drag',i,j,'lost',len(lost),lost[:6])
      cv,_=pg.evaluate(COV);pg.wait_for_timeout(900);pg.reload();pg.wait_for_function(W,timeout=60000);pg.wait_for_timeout(900)
      pg.evaluate("(id)=>{window.__b=document.getElementById(id)}",bid);cv2,_=pg.evaluate(COV)
      if set(cv)!=set(cv2): bad+=1;print('RELOAD DIFF',lec,bid,len(cv),len(cv2),sorted(set(cv)-set(cv2))[:8],sorted(set(cv2)-set(cv))[:8])
      pg.keyboard.press('h')
  print('drags',tot,'bad',bad,'errs',E[:2])
ok=bad==0 and tot>=15 and not E
print(('  OK   ' if ok else '  FAIL ')+f'M1 드래그 {tot}번 · 기존 형광펜 사라짐 {bad}번 · 오류 {E[:1]}')
print('RESULT', 'PASS' if ok else 'FAIL 1');sys.exit(0 if ok else 1)
