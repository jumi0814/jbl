"""옛 허브(배포본 f2e99d3 = 8793033)의 표시 단위 글자 기준선 — 한 번만 만들면 됨.
  .venv/bin/python tools/legacy_base.py [--rev f2e99d3] [--old <옛 docs 폴더>]
옛 허브는 표시를 {x, i(같은 글자 몇 번째)}로만 저장했다. 원고·화면 구조가 바뀌면 i가 다른 자리를 가리키므로,
옛 허브가 실제로 보여 주던 블록 글자(옛 Kit.index 규칙 — 안쪽 data-aid도 셈)를 aid별로 모아
tools/<sid>/legacy_txt.json에 둔다. build4가 docs/packs/<SID>.lx.js로 내보내고, 허브는 옛 표시가 남은 과목만
그 파일을 받아 표시마다 앞뒤 글자(p·s)와 블록 지문(v)을 한 번 붙인다(Kit.enrich). 그 뒤로는 i를 믿지 않고 문맥으로 찾는다."""
import os, sys, json, asyncio, subprocess, argparse
TOOLS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
from jblpaths import WORK
SUBJ = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']   # ESTH는 옛 허브(f2e99d3)에 없던 과목 — 이관할 옛 표시 없음

IDX = r"""(()=>{const SKIP='button,.noann,select,input,textarea,summary,.chip,.badge,.kbd,.ntag,.ybadge,[data-ttog]';
 const blockOf=n=>{let p=n.nodeType===1?n:n.parentElement;while(p&&!/^(P|LI|TD|TH|DIV|SECTION|ARTICLE|H1|H2|H3|H4|H5|TR|UL|OL|TABLE|FIGCAPTION|SUMMARY|DETAILS)$/.test(p.nodeName))p=p.parentElement;return p;};
 const out={};for(const B of document.querySelectorAll('#stage [data-aid]')){if(B.closest(SKIP))continue;const w=document.createTreeWalker(B,NodeFilter.SHOW_TEXT,null);let s='',n;
  while(n=w.nextNode()){if(!n.nodeValue)continue;const p=n.parentElement;if(!p||p.closest(SKIP))continue;s+=n.nodeValue;}
  if(!(B.dataset.aid in out))out[B.dataset.aid]=s;}return out;})()"""

def old_docs(rev, given):
    if given: return given
    d = os.path.join(WORK, '_legacy', rev)
    if not os.path.exists(os.path.join(d, 'docs', 'index.html')):
        os.makedirs(d, exist_ok=True)
        tar = subprocess.run(['git', 'archive', rev, 'docs'], cwd=ROOT, capture_output=True, check=True).stdout
        subprocess.run(['tar', '-x', '-C', d], input=tar, check=True)
    ix = os.path.join(d, 'docs', 'index.html'); h = open(ix, encoding='utf-8').read()
    if 'window.__h=' not in h:   # 옛 허브 안을 들여다보는 고리(이 복사본에만)
        k = h.rindex('})();\n</script>')
        h = h[:k] + 'window.__h={openDoc,PACKS,docTabs,get CUR(){return CUR;}};\n' + h[k:]
        open(ix, 'w', encoding='utf-8').write(h)
    return os.path.join(d, 'docs')

async def crawl(docs):
    from playwright.async_api import async_playwright
    res = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        await pg.goto('file://' + os.path.join(docs, 'index.html') + '#/'); await pg.wait_for_timeout(2000)
        for S in SUBJ:
            if not await pg.evaluate(f"!!(window.__h&&__h.PACKS['{S}'])"): continue
            docs_ = await pg.evaluate(f"""(()=>{{__h.openDoc('{S}','_home');const p=__h.PACKS['{S}'];return [['_home','']].concat(['_jb','_sum','_tbl','_pred','_led'].map(d=>[d,''])).concat(p.lect.flatMap(L=>__h.docTabs(p,L.k).map(t=>[L.k,t[0]])));}})()""")
            T = {}
            for d, t in docs_:
                if t == 'flash': continue
                await pg.evaluate(f"__h.openDoc('{S}','{d}','{t}')"); await pg.wait_for_timeout(60)
                for k, v in (await pg.evaluate(IDX)).items(): T.setdefault(k, v)
            res[S] = T; print(S, 'aids', len(T), 'chars', sum(len(v) for v in T.values()), flush=True)
        await b.close()
    return res

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--rev', default='f2e99d3'); ap.add_argument('--old'); a = ap.parse_args()
    res = asyncio.run(crawl(old_docs(a.rev, a.old)))
    for S, T in res.items():
        json.dump({'rev': a.rev, 'txt': T}, open(os.path.join(TOOLS, S.lower(), 'legacy_txt.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('wrote', ', '.join(f'tools/{S.lower()}/legacy_txt.json' for S in res))
