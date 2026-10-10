"""UX8 넘버링 따기(10-10) — 홈 탭·Word형 연속 화면·편집/자동 저장·불러오기·새 문제·파일 가져오기·검색/정렬/상태·가리기·성능(300문제+).
기본 자료(Word)는 없음(10-10 사용자: 첨부 Word는 참고용 예시 — 사이트에서 뺌) → 시험은 JB 기출·예상문제 불러오기와, 이 시험이 직접 만드는 작은 Word(.docx)로.
- 홈: '넘버링' 칸(과목 표 위) · ① 넘버링 따기 → #/_num · ② 넘버링 복습 = 비활성(추후 업데이트 예정) · 홈에서는 넘버링 파일을 받지 않음 · 예시 Word 과목·그림 없음
- 기존 문제 불러오기(CONS): 서술형·넘버링형만/전체 · 고른 것·이 강의 전체·과목 전체 · 중복 다시 안 만듦 · 새로고침 뒤 그대로 · 예상문제 문제 글
- 연속 문서: 모두 펼침(문제 + 왼쪽 답안 | 오른쪽 스토리) · 강의별/전체 목록 · 새로고침 뒤 기억
- 스토리 누르면 그 자리 편집(도구 막대는 편집 중에만 · 취소선 없음) → 0.7초 뒤 그 문제 키 하나만 저장 → 새로고침 뒤 그대로 · 서식(굵게·밑줄·글자색·형광펜·표·그림) · Word 붙여넣기
- 문제 '수정' = 작업본만(팩 원본 그대로) → '원본으로'(화면 안 확인 창) · 열었다 닫기만 = '고침' 없음 · 완성·상태 개수 · 빼기/다시 넣기 · 위로 · 복사
- 검색·연도·정렬 · 답안/스토리 가리기(누르면 그 문제만 보임) · 새 문제(스토리 없이) · 파일 가져오기(미리 보기 → 새 과목)
- 백업: dumpAll에 num 키 · mergeData는 문제마다 더 최근(u) 것 · 성능: 320문제(긴 답·표·그림) 첫 표시·전체·빠른 스크롤·편집기·타이핑 중 저장·보기/과목 전환·대량 추가(PHARM 전체·묶음 안 중복 0) · 모바일 · pageerror 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, time, struct, zlib, zipfile
from playwright.async_api import async_playwright
U = J.HUB_URL; fails = []; PERF = {}
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def png(w=60, h=40):   # 작은 PNG(그림 넣기 시험용)
    raw = b''.join(b'\x00' + bytes([200, 80, 60] * w) for _ in range(h))
    ch = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw)) + ch(b'IEND', b'')
def docx(path):   # 3칸 표('문제|정답|암기법') 시험용 Word — 강의 머리 줄 하나, 문제 둘(연도 괄호·번호 글·빨간 스토리)
    W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    def P(t, col=''):
        rp = '<w:rPr><w:color w:val="' + col + '"/></w:rPr>' if col else ''
        return '<w:p><w:r>' + rp + '<w:t xml:space="preserve">' + t + '</w:t></w:r></w:p>'
    def C(*ps, span=1):
        gs = '<w:gridSpan w:val="' + str(span) + '"/>' if span > 1 else ''
        return '<w:tc><w:tcPr>' + gs + '</w:tcPr>' + (''.join(ps) or P('')) + '</w:tc>'
    R = lambda *cs: '<w:tr>' + ''.join(cs) + '</w:tr>'
    body = P('시험 넘버링 자료') + '<w:tbl><w:tblGrid><w:gridCol/><w:gridCol/><w:gridCol/></w:tblGrid>' + R(C(P('홍길동_시험 강의'), span=3)) + R(C(P('문제')), C(P('정답')), C(P('암기법'))) \
        + R(C(P('시험용 원인을 3가지 쓰시오 (24,22)')), C(P('1. 첫째 원인'), P('2. 둘째 원인'), P('3. 셋째 원인')), C(P('첫둘셋 스토리 한 줄', 'C00000'))) \
        + R(C(P('시험용 기전을 서술하시오 (25탈)')), C(P('기전 답 문장')), C()) + '</w:tbl>'
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/document.xml', '<?xml version="1.0" encoding="UTF-8"?><w:document ' + W + '><w:body>' + body + '</w:body></w:document>')
NIT = lambda pg: pg.evaluate("document.querySelectorAll('.nm-it').length")
async def goto(pg, h, wait=2500):
    await pg.goto('about:blank'); await pg.goto(U + h); await pg.wait_for_timeout(wait)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1366, 'height': 900}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        reqs = []; pg.on('request', lambda r: reqs.append(r.url))
        # ---- 홈 ----
        await goto(pg, '#/', 2500)
        h = await pg.evaluate("""(()=>{const s=document.querySelector('.hnum'),t=document.querySelector('.hsj'),b2=document.querySelector('.hnumb.off');return {s:!!s,above:!!(s&&t&&s.compareDocumentPosition(t)&Node.DOCUMENT_POSITION_FOLLOWING),dis:!!(b2&&b2.disabled),txt:b2?b2.textContent:''}})()""")
        ok(h['s'] and h['above'], f"홈 '넘버링' 칸이 과목 표 위 {h}")
        ok(h['dis'] and '추후 업데이트 예정' in h['txt'], "② 넘버링 복습 = 비활성·'추후 업데이트 예정'")
        ok(not any('/num/' in r for r in reqs), f"홈에서는 넘버링 파일을 받지 않음 {[r for r in reqs if '/num/' in r][:2]}")
        await pg.click('[data-hnum=take]'); await pg.wait_for_timeout(2500)
        ok((await pg.evaluate('location.hash')).startswith('#/_num'), f"① 넘버링 따기 → {await pg.evaluate('location.hash')}")
        sj = await pg.evaluate("[...document.querySelectorAll('[data-cf=sj] option')].map(o=>o.value)")
        ok(not any(x in sj for x in ('OMED', 'ORTH')) and await pg.evaluate("(window.JBLNUM_INDEX||[]).length") == 0 and not any('/num/img/' in r for r in reqs), f"예시 Word 과목·그림 없음(과목 {sj[:9]})")
        # ---- 빈 과목 → 기존 문제 불러오기 ----
        await goto(pg, '#/_num/CONS', 3500)
        ok(await NIT(pg) == 0 and await pg.evaluate("!!document.querySelector('.nm-empty')"), "문제가 없는 과목 = 안내(기존 문제 불러오기·새 문제)")
        await pg.click('[data-act=imp]'); await pg.wait_for_timeout(800)
        ne = await pg.evaluate("document.querySelectorAll('.nm-irow').length"); await pg.select_option('[data-if=ty]', ''); await pg.wait_for_timeout(300); na = await pg.evaluate("document.querySelectorAll('.nm-irow').length")
        ok(0 < ne <= na, f"불러오기: 서술형·넘버링형만 {ne} ≤ 전체 {na}")
        await pg.select_option('[data-if=ty]', 'ess'); await pg.wait_for_timeout(300)
        for i in range(3): await pg.locator('.nm-irow [data-ick]').nth(i).check()
        await pg.click('[data-ib=sel]'); await pg.wait_for_timeout(300)
        ok('새로 넣을 문제 3' in await pg.evaluate("document.querySelector('.nm-ov .nm-ov .bd').innerText"), "고른 3개 → 미리 '새로 넣을 문제 3'")
        await pg.click('[data-cf2=ok]'); await pg.wait_for_timeout(600)
        await pg.select_option('[data-if=lec]', index=1); await pg.wait_for_timeout(300); await pg.select_option('[data-if=ty]', ''); await pg.wait_for_timeout(300)
        await pg.click('[data-ib=lec]'); await pg.wait_for_timeout(300)
        t2 = await pg.evaluate("document.querySelector('.nm-ov .nm-ov .bd').innerText"); ok('이미 있음(건너뜀)' in t2, f"이 강의 전체: {t2.splitlines()[0][:90]}")
        await pg.click('[data-cf2=ok]'); await pg.wait_for_timeout(600)
        await pg.click('[data-ib=all]'); await pg.wait_for_timeout(500); await pg.click('[data-cf2=ok]'); await pg.wait_for_timeout(1200); await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(600)
        nc = await NIT(pg); await pg.click('[data-act=imp]'); await pg.wait_for_timeout(600); await pg.select_option('[data-if=ty]', ''); await pg.wait_for_timeout(300)
        await pg.click('[data-ib=all]'); await pg.wait_for_timeout(500)
        t3 = await pg.evaluate("document.querySelector('.nm-ov .nm-ov .bd').innerText")
        ok('새로 넣을 문제 0' in t3, f"과목 전체를 한 번 더 → 새로 넣을 문제 0(중복 안 만듦) {t3.splitlines()[0][:90]}")
        await pg.click('[data-cf2=no]'); await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(300)
        await pg.reload(); await pg.wait_for_timeout(3000)
        ok(await NIT(pg) == nc and nc > 100, f"CONS 과목 전체 {nc}문제 · 새로고침 뒤 그대로")
        ok(await pg.evaluate("[...document.querySelectorAll('.nm-it')].filter(a=>a.querySelector('.nm-chip.k-pred')).every(a=>a.querySelector('.nm-q .nm-c').textContent.trim().length>3)"), "예상문제 문제 글이 비지 않음")
        r = await pg.evaluate("""(()=>{const A=[...document.querySelectorAll('.nm-it')];const bad=A.filter(a=>!a.querySelector('.nm-q .nm-c')||!a.querySelector('.nm-a .nm-c')||!a.querySelector('.nm-s .nm-c')).length;
          const a=A[0],q=a.querySelector('.nm-q').getBoundingClientRect(),c1=a.querySelector('.nm-a').getBoundingClientRect(),c2=a.querySelector('.nm-s').getBoundingClientRect();
          return {n:A.length,bad,hidden:A.filter(x=>x.hidden).length,side:c2.left>c1.left+100&&Math.abs(c2.top-c1.top)<2&&c1.top>q.top,lec:document.querySelectorAll('.nm-lec').length,tb:document.querySelectorAll('.nm-tb').length}})()""")
        ok(not r['bad'] and not r['hidden'] and r['side'] and r['lec'] > 1 and r['tb'] == 0, f"모두 펼침 · 문제 아래 왼쪽 답안 | 오른쪽 스토리 · 강의 머리 {r['lec']} · 읽기 상태엔 편집 막대 없음 {r}")
        await pg.click('[data-mode=all]'); await pg.wait_for_timeout(800)
        ok(await pg.evaluate("document.querySelectorAll('.nm-lec').length") == 0 and await NIT(pg) == nc, "전체 목록 보기 = 강의 머리 없이 연속")
        await pg.reload(); await pg.wait_for_timeout(2500)
        ok(await pg.evaluate("document.querySelector('[data-mode=all]').classList.contains('on')") and await pg.evaluate("location.hash") == '#/_num/CONS', "새로고침 뒤에도 과목·보기(전체 목록) 기억")
        await pg.click('[data-mode=grp]'); await pg.wait_for_timeout(600)
        # ---- 편집·자동 저장 ----
        it3 = await pg.evaluate("document.querySelectorAll('.nm-it')[2].dataset.id")
        loc = pg.locator('.nm-it').nth(2).locator('.nm-s .nm-c'); await loc.scroll_into_view_if_needed(); bx = await loc.bounding_box()
        await pg.evaluate("""(()=>{window.__w=0;window.__ww=1;const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(String(k).indexOf('jblhub.v1.num.')===0)window.__w++;return o.call(this,k,v);};})()""")
        await pg.mouse.click(bx['x'] + 30, bx['y'] + 8); await pg.wait_for_timeout(250)
        e = await pg.evaluate("(()=>{const S=JBLNUM._S;return {ed:!!S.ed,tb:document.querySelectorAll('.nm-tb').length,strike:!!document.querySelector('.nm-tb [data-cmd*=strike i]'),btn:[...document.querySelectorAll('.nm-tb button')].map(b=>b.title.split(' ')[0])}})()")
        ok(e['ed'] and e['tb'] == 1 and not e['strike'], f"스토리 누르면 그 자리 편집 · 도구 막대 1개 · 취소선 없음 {e['btn']}")
        await pg.keyboard.type('스토리 첫 줄'); await pg.keyboard.down('Shift'); await pg.keyboard.press('Home'); await pg.keyboard.up('Shift')
        await pg.click('.nm-tb [data-cmd=bold]'); await pg.click('.nm-tb [data-cmd=underline]')
        await pg.click('.nm-tb [data-pal=fc]'); await pg.click('.nm-pal [data-fc="#C00000"]')
        await pg.click('.nm-tb [data-pal=hl]'); await pg.click('.nm-pal [data-hl="#FFFF00"]')
        await pg.keyboard.press('End'); await pg.keyboard.press('Enter'); await pg.keyboard.type('둘째 줄 표 아래')
        await pg.click('.nm-tb [data-pal=tbl]'); await pg.click('.nm-pal [data-tb=ins2]'); await pg.keyboard.type('칸1')
        async with pg.expect_file_chooser() as fci: await pg.click('.nm-tb [data-cmd=img]')
        fc = await fci.value; pth = J.TMP + '/nm_test.png'; open(pth, 'wb').write(png()); await fc.set_files(pth); await pg.wait_for_timeout(800)
        w0 = await pg.evaluate('window.__w'); await pg.wait_for_timeout(1200)
        rec = await pg.evaluate(f"localStorage.getItem('jblhub.v1.num.i.CONS.{it3}')") or ''
        ok('<b>' in rec and '<u>' in rec and 'color:#C00000' in rec and 'background-color:#FFFF00' in rec and '<table>' in rec and 'data:image/' in rec, f"서식 저장(굵게·밑줄·글자색·형광펜·표·그림) {len(rec)}자")
        ok((await pg.evaluate("document.querySelector('.nm-save').textContent")).startswith('저장됨'), "저장 상태 '저장됨 ✓'")
        ok(await pg.evaluate("!!JBLNUM._S.ed") and await pg.evaluate('window.__w') <= w0 + 2, f"자동 저장 = 입력 멈춘 뒤 그 문제 키만(쓰기 {await pg.evaluate('window.__w')}번)")
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        ok(not await pg.evaluate("!!JBLNUM._S.ed") and await pg.evaluate("document.querySelectorAll('.nm-tb').length") == 0, "Esc = 편집 끝·도구 막대 사라짐")
        await pg.reload(); await pg.wait_for_timeout(3000)
        st = await pg.evaluate("document.querySelectorAll('.nm-it')[2].querySelector('.nm-s .nm-c').innerHTML")
        ok('스토리 첫 줄' in st and '<table>' in st and '<img' in st, "새로고침 뒤 스토리·표·그림 그대로")
        # 열었다 닫기만 = '고침' 없음
        await pg.evaluate("(()=>{const a=document.querySelectorAll('.nm-it')[5];a.scrollIntoView({block:'center'});a.querySelector('.nm-a [data-act=edit]').click();})()"); await pg.wait_for_timeout(900)
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("document.querySelectorAll('.nm-it')[5].querySelector('.nm-chip.ed')") is None, "답안 칸을 열었다 닫기만 = '고침' 표시·작업본 안 생김")
        # Word에서 복사한 글 붙여넣기
        it4 = await pg.evaluate("document.querySelectorAll('.nm-it')[3].dataset.id")
        await pg.evaluate("document.querySelectorAll('.nm-it')[3].querySelector('.nm-s .nm-c').scrollIntoView({block:'center'})")
        await pg.evaluate("document.querySelectorAll('.nm-it')[3].querySelector('.nm-s .nm-c').click()"); await pg.wait_for_timeout(200); await pg.keyboard.press('Control+End')
        await pg.evaluate("""(()=>{const dt=new DataTransfer();dt.setData('text/html','<html><body><!--StartFragment--><p class=MsoNormal><b>워드굵게</b> <span style="color:#C00000;mso-highlight:yellow">빨강노랑</span> <s>취소선글자</s><o:p></o:p></p><table class=MsoTableGrid><tr><td><p>칸A</p></td><td><p>칸B</p></td></tr></table><!--EndFragment--></body></html>');dt.setData('text/plain','워드굵게');document.activeElement.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));})()""")
        await pg.wait_for_timeout(1200); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        r4 = await pg.evaluate(f"localStorage.getItem('jblhub.v1.num.i.CONS.{it4}')") or ''
        ok('<b>워드굵게</b>' in r4 and 'color:#C00000' in r4 and 'background-color:#FFFF00' in r4 and '칸A' in r4 and '<table>' in r4 and '취소선글자' in r4 and '<s>' not in r4 and 'line-through' not in r4 and 'Mso' not in r4, "Word 붙여넣기: 서식·표 유지 · 취소선은 글자만 · Word 꾸밈(class) 없음")
        # 문제 수정 → 원본(팩 원본은 그대로)
        aid0 = await pg.evaluate("document.querySelectorAll('.nm-it')[0].dataset.id")
        await pg.locator('.nm-it').nth(0).locator('.nm-q [data-act=edit]').click(); await pg.wait_for_timeout(200)
        await pg.keyboard.press('Control+End'); await pg.keyboard.type(' (내 메모)'); await pg.wait_for_timeout(1000); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        packq = await pg.evaluate("(a=>{const P=JBLNUM._H().PACKS.CONS,id=a.replace(/^jb:CONS:/,''),pr=P.preds.find(x=>x.html.indexOf(a.slice(3))>=0);return (P.cards[id]||'')+(pr?pr.html:'')})", aid0)
        ok(await pg.evaluate("document.querySelectorAll('.nm-it')[0].querySelector('.nm-chip.ed')?.textContent") == '문제 고침' and '(내 메모)' not in (packq or ''), "문제 '수정' = 작업본만(JB 팩 원본 그대로) · '문제 고침' 표시")
        await pg.locator('.nm-it').nth(0).locator('[data-act=more]').click(); await pg.click('.nm-menu [data-mi=orig]'); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("!!document.querySelector('[data-ask]')"), "'원본으로' = 화면 안 확인 창(브라우저 confirm 안 씀)")
        await pg.click('[data-ask="1"]'); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("document.querySelectorAll('.nm-it')[0].querySelector('.nm-chip.ed')") is None and '(내 메모)' not in await pg.evaluate("document.querySelectorAll('.nm-it')[0].querySelector('.nm-q').textContent"), "'원본으로' 되돌리기")
        # 완성·상태
        c0 = await pg.evaluate("document.querySelector('[data-stf=\"2\"] b').textContent")
        await pg.locator('.nm-it').nth(1).locator('[data-act=more]').click(); await pg.click('.nm-menu [data-mi=done]'); await pg.wait_for_timeout(300)
        ok(int(await pg.evaluate("document.querySelector('[data-stf=\"2\"] b').textContent")) == int(c0) + 1, "완성 표시 → 완성 개수 +1")
        await pg.click('[data-stf="0"]'); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("[...document.querySelectorAll('.nm-it:not([hidden])')].every(a=>a.querySelector('.nm-chip.s0'))"), "상태 '미작성'만 보기"); await pg.click('[data-stf=""]'); await pg.wait_for_timeout(200)
        # 빼기/다시 넣기 · 옮기기 · 복사
        id5 = await pg.evaluate("document.querySelectorAll('.nm-it')[4].dataset.id")
        await pg.locator('.nm-it').nth(4).locator('[data-act=more]').click(); await pg.click('.nm-menu [data-mi=del]'); await pg.wait_for_timeout(400)
        ok(await NIT(pg) == nc - 1 and await pg.evaluate("!!document.querySelector('.nm-hid')"), "목록에서 빼기 → '뺀 문제'에 남음")
        await pg.evaluate("document.querySelector('.nm-hid').open=true"); await pg.click(f".nm-hid [data-id='{id5}'] [data-act=undel]"); await pg.wait_for_timeout(400)
        ok(await NIT(pg) == nc, "다시 넣기")
        id2 = await pg.evaluate("document.querySelectorAll('.nm-it')[1].dataset.id")
        await pg.locator('.nm-it').nth(1).locator('[data-act=more]').click(); await pg.click('.nm-menu [data-mi=up]'); await pg.wait_for_timeout(500)
        ok(await pg.evaluate("document.querySelectorAll('.nm-it')[0].dataset.id") == id2, "위로 옮기기(사용자 지정 순서)")
        await pg.locator('.nm-it').nth(0).locator('[data-act=more]').click(); await pg.click('.nm-menu [data-mi=copy]'); await pg.wait_for_timeout(500)
        ok(await NIT(pg) == nc + 1, "복사해서 새 문제")
        # 검색·연도·정렬
        await pg.fill('[data-cf=q]', 'bleaching'); await pg.wait_for_timeout(450)
        nv = await pg.evaluate("document.querySelectorAll('.nm-it:not([hidden])').length"); ok(1 <= nv < nc, f"검색 'bleaching' → {nv}문제"); await pg.fill('[data-cf=q]', ''); await pg.wait_for_timeout(400)
        yr = await pg.evaluate("[...document.querySelectorAll('[data-cf=yr] option')].map(o=>o.value).find(v=>/^20/.test(v))")
        await pg.select_option('[data-cf=yr]', yr); await pg.wait_for_timeout(250)
        ok(await pg.evaluate("(y=>[...document.querySelectorAll('.nm-it:not([hidden])')].every(a=>(a.querySelector('.nm-chip.yr')?.textContent||'').indexOf(y)>=0))", yr), f"연도 {yr}만")
        await pg.select_option('[data-cf=yr]', ''); await pg.select_option('[data-cf=sort]', 'freq'); await pg.wait_for_timeout(600)
        f = await pg.evaluate("""(()=>{const G=[];let cur=null;for(const x of document.querySelector('.nm-doc').children){if(x.classList.contains('nm-lec')){cur=[];G.push(cur);}else if(x.classList.contains('nm-it')&&!x.hidden&&cur)cur.push((x.querySelector('.nm-chip.yr')?.textContent||'').split('·').filter(s=>s.trim()).length);}return G;})()""")
        ok(all(g[i] >= g[i + 1] for g in f for i in range(len(g) - 1)), f"정렬 '기출 빈도' = 강의마다 출제 횟수 많은 순 {[g[:6] for g in f[:2]]}")
        await pg.select_option('[data-cf=sort]', 'lec'); await pg.wait_for_timeout(400)
        # 가리기(연습·암기)
        await pg.click('[data-hide=a]'); await pg.wait_for_timeout(200)
        hb = await pg.evaluate("getComputedStyle(document.querySelectorAll('.nm-it')[1].querySelector('.nm-a .nm-c')).filter")
        await pg.evaluate("document.querySelectorAll('.nm-it')[1].scrollIntoView({block:'center'})")
        await pg.locator('.nm-it').nth(1).locator('.nm-a .nm-c').click(); await pg.wait_for_timeout(200)
        ha = await pg.evaluate("[getComputedStyle(document.querySelectorAll('.nm-it')[1].querySelector('.nm-a .nm-c')).filter,getComputedStyle(document.querySelectorAll('.nm-it')[2].querySelector('.nm-a .nm-c')).filter,!!JBLNUM._S.ed]")
        ok('blur' in hb and ha[0] == 'none' and 'blur' in ha[1] and not ha[2], f"답안 가리기: 모두 가림 → 누른 문제만 보임(편집은 안 켜짐) {hb} → {ha}")
        await pg.reload(); await pg.wait_for_timeout(2500)
        ok(await pg.evaluate("document.getElementById('numv').classList.contains('hideA')"), "가리기 설정 기억")
        await pg.click('[data-hide=a]'); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("getComputedStyle(document.querySelector('.nm-it .nm-a .nm-c')).filter") == 'none', "가리기 끄기")
        # 새 문제(스토리 없이)
        n0 = await NIT(pg)
        await pg.click('[data-act=new]'); await pg.wait_for_timeout(300); await pg.click('[data-rich=q]'); await pg.keyboard.type('직접 만든 문제 4가지를 쓰시오.'); await pg.fill('[data-nf=yrs]', '25'); await pg.click('[data-nfsave]'); await pg.wait_for_timeout(700)
        ok(await NIT(pg) == n0 + 1 and await pg.evaluate("document.querySelector('.nm-it.flash .nm-chip.s0')!==null"), "새 문제(스토리 없이) 저장 → 바로 문서에 · 미작성")
        # 파일 가져오기(시험용 Word) → 미리 보기 → 새 과목
        dp = J.TMP + '/nm_test.docx'; docx(dp)
        async with pg.expect_file_chooser() as fci: await pg.click('[data-act=file]')
        fc = await fci.value; await fc.set_files(dp); await pg.wait_for_timeout(2500)
        pv = await pg.evaluate("document.querySelector('.nm-ov .bd')?.innerText||''")
        ok('문제 2' in pv and '강의 1' in pv and '문제|정답|암기법' in pv, f"파일 미리 보기 {pv[:160]!r}")
        await pg.select_option('[data-fp=s]', '__new'); await pg.click('[data-fpgo]'); await pg.wait_for_timeout(2500)
        fi = await pg.evaluate("[...document.querySelectorAll('.nm-it')].map(a=>[a.querySelector('.nm-q').textContent,a.querySelector('.nm-a .nm-c').textContent,a.querySelector('.nm-s .nm-c').innerHTML,a.querySelector('.nm-chip.yr')?.textContent||''])")
        lh = await pg.evaluate("document.querySelector('.nm-lec')?.textContent||''")
        ok(len(fi) == 2 and '1. 첫째 원인' in fi[0][1] and '첫둘셋 스토리' in fi[0][2] and 'C00000' in fi[0][2] and fi[0][3] == '2024 · 2022' and fi[1][3] == '2025' and '시험 강의' in lh, f"Word 가져오기 → 새 과목 2문제(답·빨간 스토리·연도·강의) {fi} · {lh}")
        # 백업·합치기
        bk = await pg.evaluate("(()=>{const d=window.__h&&window.__h.dumpAll?window.__h.dumpAll():null;return d?Object.keys(d).filter(k=>k.indexOf('jblhub.v1.num.i.')===0).length:-1})()")
        ok(bk > 100, f"백업 파일(dumpAll)에 넘버링 문제 키 {bk}개")
        mg = await pg.evaluate("""(()=>{const k='jblhub.v1.num.i.CONS.zz:test';localStorage.setItem(k,JSON.stringify({id:'zz:test',k:'user',q:'<p>새</p>',u:200}));window.__h.mergeData({[k]:JSON.stringify({id:'zz:test',k:'user',q:'<p>옛</p>',u:100})});const a=JSON.parse(localStorage.getItem(k)).q;window.__h.mergeData({[k]:JSON.stringify({id:'zz:test',k:'user',q:'<p>더 새</p>',u:300})});const b=JSON.parse(localStorage.getItem(k)).q;localStorage.removeItem(k);
          const x='jblhub.v1.num.x.CONS';const x0=localStorage.getItem(x);localStorage.setItem(x,JSON.stringify({v:1,ul:[{k:'UA',t:'A'}],u:5}));window.__h.mergeData({[x]:JSON.stringify({v:1,ul:[{k:'UB',t:'B'}],u:9})});const ul=JSON.parse(localStorage.getItem(x)).ul.map(l=>l.k).join(',');if(x0==null)localStorage.removeItem(x);else localStorage.setItem(x,x0);return [a,b,ul]})()""")
        ok(mg == ['<p>새</p>', '<p>더 새</p>', 'UA,UB'], f"백업 합치기 = 문제마다 더 최근(u) 것 · 내가 만든 강의는 두 기기 것을 합침 {mg}")
        # ---- 성능 ----
        await pg.evaluate("""(()=>{const NS='jblhub.v1.',L=JSON.parse(localStorage.getItem(NS+'num.subj')||'[]');L.push({id:'PERF',t:'성능 시험'});localStorage.setItem(NS+'num.subj',JSON.stringify(L));
          const img='data:image/png;base64,'+btoa(String.fromCharCode(...new Uint8Array(64)));
          for(let i=0;i<320;i++){const a=Array.from({length:8},(_,j)=>'<p>'+(j+1)+') '+'Long answer line about periodontal ligament remodeling and hyalinization zone 치주인대 '+(i*8+j)+'</p>').join('')+(i%5===0?'<table><tr><td><p>표</p></td><td><p>값 '+i+'</p></td></tr><tr><td><p>A</p></td><td><p>B</p></td></tr></table>':'')+(i%7===0?'<p><img src="'+img+'" width="200" height="120" alt=""></p>':'');
            localStorage.setItem(NS+'num.i.PERF.u:p'+i,JSON.stringify({id:'u:p'+i,k:'user',lec:'',q:'<p>'+(i+1)+'. 성능 시험 문제 — 서술하시오 '+'x'.repeat(i%40)+'</p>',a,st:i%3?'<p>스토리 '+i+' '+'넘버링 기억법 '.repeat(4)+'</p>':'',src:[{t:'user',s:'PERF',lab:'시험'}],yrs:[2025-(i%6)],o:i,c:1,u:1}));}})()""")
        await pg.goto('about:blank'); await pg.goto(U + '#/'); await pg.wait_for_timeout(2500)
        t = await pg.evaluate("""new Promise(res=>{const t0=performance.now();let first=0;location.hash='#/_num/PERF';const iv=setInterval(()=>{const n=document.querySelectorAll('.nm-it').length;if(n&&!first)first=performance.now()-t0;if(n>=320){clearInterval(iv);res({first:Math.round(first),all:Math.round(performance.now()-t0)});}},5);setTimeout(()=>{clearInterval(iv);res({first,all:-1});},15000);})""")
        PERF['open320'] = t; ok(0 < t['first'] < 1500 and 0 < t['all'] < 5000, f"320문제 열기: 첫 문제 {t['first']}ms · 전체 {t['all']}ms")
        await pg.wait_for_timeout(500)
        sc = await pg.evaluate("""new Promise(async res=>{const L=[];const po=new PerformanceObserver(l=>l.getEntries().forEach(e=>L.push(e.duration)));try{po.observe({type:'longtask',buffered:false});}catch(e){}
          const H=document.documentElement.scrollHeight;const fr=[];let last=performance.now();for(let i=0;i<=60;i++){window.scrollTo(0,H*i/60);await new Promise(r=>requestAnimationFrame(()=>r()));const n=performance.now();fr.push(n-last);last=n;}
          for(let i=60;i>=0;i-=2){window.scrollTo(0,H*i/60);await new Promise(r=>requestAnimationFrame(()=>r()));const n=performance.now();fr.push(n-last);last=n;}
          await new Promise(r=>setTimeout(r,300));po.disconnect();fr.sort((a,b)=>b-a);res({maxLong:Math.round(Math.max(0,...L)),nLong:L.length,p95:Math.round(fr[Math.floor(fr.length*0.05)]),max:Math.round(fr[0]),H});})""")
        PERF['scroll'] = sc; ok(sc['p95'] < 120 and sc['maxLong'] < 400, f"빠른 스크롤(위↔아래 90단계): 프레임 p95 {sc['p95']}ms · 최대 {sc['max']}ms · 긴 작업 {sc['nLong']}개 최대 {sc['maxLong']}ms · 문서 높이 {sc['H']}px")
        await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(200)
        ea = await pg.evaluate("""(()=>{const el=document.querySelectorAll('.nm-it')[150].querySelector('.nm-s .nm-c');el.scrollIntoView({block:'center'});const t0=performance.now();el.click();const t1=performance.now();return {ms:Math.round((t1-t0)*10)/10,ed:!!JBLNUM._S.ed,n:document.querySelectorAll('[contenteditable=true]').length}})()""")
        PERF['editOn'] = ea; ok(ea['ed'] and ea['ms'] < 150 and ea['n'] <= 2, f"편집기 켜기 {ea['ms']}ms · 켜진 편집 칸 {ea['n']}개(넘버링 1 + 허브 메모장)")
        await pg.evaluate("""(()=>{if(!window.__ww){window.__ww=1;const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(String(k).indexOf('jblhub.v1.num.')===0)window.__w++;return o.call(this,k,v);};}window.__w=0;window.__lt=[];const po=new PerformanceObserver(l=>l.getEntries().forEach(e=>__lt.push(e.duration)));try{po.observe({type:'longtask'});}catch(e){}window.__po=po;})()""")
        t0 = time.time(); await pg.keyboard.type('타이핑 중 렉 시험 ' * 6, delay=15); typ = time.time() - t0
        wt = await pg.evaluate('window.__w'); await pg.wait_for_timeout(1200); wt2 = await pg.evaluate('window.__w')
        lt = await pg.evaluate("(()=>{__po.disconnect();return __lt.length?Math.round(Math.max(...__lt)):0})()")
        PERF['typing'] = {'chars': 66, 'sec': round(typ, 2), 'writesDuring': wt, 'writesAfter': wt2, 'maxLong': lt}
        ok(wt <= 3 and wt2 >= 1 and lt < 100, f"타이핑 66자: 입력 중 저장 {wt}번 · 멈춘 뒤 {wt2}번 · 긴 작업 최대 {lt}ms")
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
        ms = await pg.evaluate("""new Promise(res=>{const t0=performance.now();document.querySelector('[data-mode=all]').click();const iv=setInterval(()=>{if(document.querySelectorAll('.nm-it').length>=320&&!document.querySelector('.nm-lec')){clearInterval(iv);res(Math.round(performance.now()-t0));}},5);setTimeout(()=>{clearInterval(iv);res(-1)},8000);})""")
        PERF['mode'] = ms; ok(0 <= ms < 3000, f"강의별 → 전체 목록 전환(320문제) {ms}ms")
        await pg.click('[data-mode=grp]'); await pg.wait_for_timeout(600)
        ss = await pg.evaluate("""new Promise(res=>{const t0=performance.now();const s=document.querySelector('[data-cf=sj]');s.value='CONS';s.dispatchEvent(new Event('change',{bubbles:true}));const iv=setInterval(()=>{if(location.hash==='#/_num/CONS'&&document.querySelectorAll('.nm-it').length>=100){clearInterval(iv);res(Math.round(performance.now()-t0));}},5);setTimeout(()=>{clearInterval(iv);res(-1)},8000);})""")
        PERF['switch'] = ss; ok(0 <= ss < 2000, f"과목 바꾸기(PERF → 보존) {ss}ms")
        fi2 = await pg.evaluate("""new Promise(res=>{const i=document.querySelector('[data-cf=q]');i.value='post';i.dispatchEvent(new Event('input',{bubbles:true}));setTimeout(()=>res(document.querySelectorAll('.nm-it:not([hidden])').length),260);})""")
        ok(fi2 >= 1, f"검색 거르기(0.2초 기다린 뒤) 보이는 {fi2}문제")
        await goto(pg, '#/_num/PHARM', 3500)
        await pg.click('[data-act=imp]'); await pg.wait_for_timeout(600); await pg.select_option('[data-if=ty]', ''); await pg.wait_for_timeout(300)
        await pg.click('[data-ib=all]'); await pg.wait_for_timeout(500)
        bt = await pg.evaluate("""new Promise(res=>{const t0=performance.now();document.querySelector('[data-cf2=ok]').click();const iv=setInterval(()=>{const n=document.querySelectorAll('.nm-it').length;if(n>200){clearInterval(iv);res({ms:Math.round(performance.now()-t0),n});}},5);setTimeout(()=>{clearInterval(iv);res({ms:-1,n:document.querySelectorAll('.nm-it').length})},10000);})""")
        dq = await pg.evaluate("(()=>{const c={};JBLNUM._S.items.filter(i=>!i.del).forEach(i=>{const k=JBLNUM._qKey(i.q);if(k.length>=8&&!/미복원|복원불충분/.test(k))c[k]=(c[k]||0)+1;});return Object.values(c).filter(n=>n>1).length})()")
        ok(dq == 0, f"과목 전체를 한 번에 넣어도 같은 문제 글이 두 번 생기지 않음(묶음 안 중복 {dq})")
        PERF['bulk'] = bt; ok(bt['n'] > 200 and 0 <= bt['ms'] < 4000, f"대량 추가(PHARM 과목 전체 {bt['n']}문제) {bt['ms']}ms")
        await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(300)
        # 모바일
        await pg.set_viewport_size({'width': 390, 'height': 844}); await goto(pg, '#/_num/CONS')
        mb = await pg.evaluate("(()=>{const a=document.querySelector('.nm-it'),c1=a.querySelector('.nm-a').getBoundingClientRect(),c2=a.querySelector('.nm-s').getBoundingClientRect();return {stack:c2.top>=c1.bottom-1,hs:document.documentElement.scrollWidth-innerWidth}})()")
        ok(mb['stack'] and mb['hs'] <= 0, f"모바일: 답안 위·스토리 아래로 쌓임 · 가로 넘침 {mb['hs']}px")
        ok(not errs, f'pageerror 0 {errs[:2]}')
        print('PERF', json.dumps(PERF, ensure_ascii=False))
        await b.close()
    print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
asyncio.run(main())
