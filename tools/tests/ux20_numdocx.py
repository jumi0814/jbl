"""UX20 넘버링 Word(.docx) 저장(10-17 사용자 "넘버링 파트에서 내가 pdf말고도 독스 파일로 추출할 수 있게 해줘!")
- 인쇄 창(인쇄 · PDF · Word 저장)의 [Word(.docx) 저장] → .docx 내려받기 · 인쇄와 같은 범위·내용·배치
- 압축(zip)·XML이 올바름(document·styles·rels·Content_Types) · 문제 수 = 번호 문단 수 · 문제 글·답안·스토리 글자 들어감 · 스토리 빨간 글씨 = w:color · 굵게 = w:b
- 그림이 있는 문제면 word/media/*.jpeg + rels 짝 · LibreOffice가 있으면 PDF로 변환해 열리는지
- pageerror 0"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import zipfile, re, shutil, subprocess, tempfile
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright
U = J.HUB_URL; fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
CLEAR = "(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()"
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
TMP = tempfile.mkdtemp(prefix='ux20_')
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1300, 'height': 900}, accept_downloads=True); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(U + '#/'); pg.wait_for_timeout(1500); pg.evaluate(CLEAR)
    pg.evaluate("location.hash='#/_num/ESTH'"); pg.wait_for_timeout(3000)
    pg.evaluate("document.querySelector('.nm-side [data-act=imp]').click()"); pg.wait_for_timeout(700)
    pg.select_option('[data-if=src]', 'jb'); pg.select_option('[data-if=ty]', ''); pg.wait_for_timeout(300)
    pg.click('[data-ib=all]'); pg.wait_for_timeout(500); pg.click('[data-cf2=ok]'); pg.wait_for_timeout(1500); pg.click('.nm-ov [data-x]'); pg.wait_for_timeout(700)
    n = pg.evaluate("document.querySelectorAll('.nm-it').length"); ok(n > 20, f"ESTH JB 문제 {n}개 가져옴")
    # 첫 문제에 빨간 스토리를 넣어 둠(색이 Word로 가는지)
    pg.evaluate("""(()=>{const S=JBLNUM._S,it=S.items.filter(i=>!i.del)[0];it.st='<p><span style="color:#C00000;">빨강 스토리 확인</span> 그리고 <b>굵게</b></p>';})()""")   # 메모리의 문제(인쇄·Word는 S.items에서 읽음)
    pg.evaluate("document.querySelector('.nm-side [data-act=print]').click()"); pg.wait_for_timeout(600)
    ttl = pg.evaluate("(document.querySelector('.nm-ov h3, .nm-ov .hd, .nm-ov [class*=tt]')||{}).textContent||''")
    has = pg.evaluate("!!document.querySelector('.nm-ov [data-po=docx]')"); ok(has, f"인쇄 창에 [Word(.docx) 저장] 단추 ({ttl.strip()[:30]})")
    want = pg.evaluate("(()=>{const t=document.querySelector('[data-psum]');return t?+((t.textContent.match(/\\d+/)||[0])[0]):0})()")
    sel = pg.evaluate("[!!document.querySelector('.nm-ov [data-po=fs]'),!!document.querySelector('.nm-ov [data-po=mg]')]"); ok(all(sel), f"인쇄 창에 글씨 크기·페이지 여백 칸 {sel}")
    pg.select_option('.nm-ov [data-po=fs]', 'l'); pg.select_option('.nm-ov [data-po=mg]', 'n')
    with pg.expect_download(timeout=30000) as dl:
        pg.click('.nm-ov [data-po=docx]')
    d = dl.value; f = _os.path.join(TMP, 'out.docx'); d.save_as(f)
    ok(d.suggested_filename.endswith('.docx'), f"파일 이름 {d.suggested_filename}")
    pg.wait_for_timeout(500)
    ok(pg.evaluate("JSON.parse(localStorage.getItem('jblhub.v1.num.pcfg')||'{}').fs") == 'l', "고른 글씨 크기·여백 기억")
    ok(not errs, f"pageerror 0 {errs[:3]}")
    pg.evaluate(CLEAR); b.close()
z = zipfile.ZipFile(f); names = z.namelist()
ok({'[Content_Types].xml', '_rels/.rels', 'word/document.xml', 'word/styles.xml', 'word/_rels/document.xml.rels'} <= set(names), f"docx 부품 {names[:6]}")
bad = []
for nm in names:
    if nm.endswith('.xml') or nm.endswith('.rels'):
        try: ET.fromstring(z.read(nm))
        except Exception as e: bad.append(f'{nm}: {e}')
ok(not bad, f"XML 올바름 {bad[:2]}")
doc = ET.fromstring(z.read('word/document.xml'))
paras = doc.iter(W + 'p'); txt = lambda e: ''.join(t.text or '' for t in e.iter(W + 't'))
qn = []   # 문제 문단 = keepNext + 위 간격 160(답안·스토리 문단과 구별)
for p_ in doc.iter(W + 'p'):
    pp = p_.find(W + 'pPr'); sp = pp.find(W + 'spacing') if pp is not None else None
    if pp is not None and pp.find(W + 'keepNext') is not None and sp is not None and sp.get(W + 'before') == '160':
        m = re.match(r'^(\d+)\. ', txt(p_))
        if m: qn.append(int(m.group(1)))
ok(want > 0 and sorted(set(qn)) == list(range(1, want + 1)), f"문제 번호 1~{want} 모두(문제 문단 {len(set(qn))})")
# Word가 '손상된 파일'로 보는 구조 — 칸 끝은 문단 · rPr/pPr/tblPr 자식 순서(스키마 순)
RO = ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike', 'dstrike', 'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid', 'vanish', 'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz', 'szCs', 'highlight', 'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign']
PO = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl', 'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind', 'contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc']
TO = ['tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize', 'tblStyleColBandSize', 'tblW', 'jc', 'tblCellSpacing', 'tblInd', 'tblBorders', 'shd', 'tblLayout', 'tblCellMar', 'tblLook']
def order_bad(tag, ref):
    out = []
    for e in doc.iter(W + tag):
        ix = [ref.index(c.tag.replace(W, '')) if c.tag.replace(W, '') in ref else -1 for c in e]
        if -1 in ix or ix != sorted(ix): out.append([c.tag.replace(W, '') for c in e])
    return out
tc_bad = [1 for tc in doc.iter(W + 'tc') if not len(tc) or tc[-1].tag != W + 'p']
ob = order_bad('rPr', RO) + order_bad('pPr', PO) + order_bad('tblPr', TO)
ok(not tc_bad and not ob, f"Word 구조(칸 끝 문단 · 꾸밈 순서) 문제 {len(tc_bad)} · {ob[:2]}")
body = doc.find(W + 'body'); ok(body is not None and body[-1].tag == W + 'sectPr', "본문 끝 = 쪽 설정(sectPr)")
xml = z.read('word/document.xml').decode('utf-8')
ok('빨강 스토리 확인' in xml and 'w:val="C00000"' in xml, "스토리 빨간 글씨 → w:color C00000")
ok('<w:b/>' in xml, "굵게 → w:b")
sty = z.read('word/styles.xml').decode('utf-8'); ok('w:sz w:val="23"' in sty and 'w:top="340"' in xml, "글씨 크게(115% → 11.5pt) · 여백 좁게(6 mm) 반영")
ok('빨강 스토리 확인' in xml and '>넘버링 스토리<' not in xml and '>답안<' not in xml, "답안 | 스토리 칸 — 상자 안 '답안'·'넘버링 스토리' 표시 없음(10-22)")
ok('넘버링 - madeby쭘' in xml and '총 ' in xml and '연도 표기 X = 예상문제' in xml and 'w:jc w:val="right"' in xml, "제목 '<과목> 넘버링 - madeby쭘' · 오른쪽 '총 n문제 (기출은 … / 연도 표기 X = 예상문제)'(10-22)")
media = [x for x in names if x.startswith('word/media/')]
rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
ok(all(_os.path.basename(m) in rels for m in media) and len(re.findall(r'r:embed="rIdI\d+"', xml)) >= len(media), f"그림 {len(media)}개 · rels 짝")
def lo_ok():   # 이 환경의 LibreOffice가 글자 파일도 못 열면(샌드박스) 열림 검사는 건너뜀
    t = _os.path.join(TMP, 'lo.txt'); open(t, 'w').write('x')
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', TMP, t], capture_output=True, timeout=120)
    return _os.path.exists(_os.path.join(TMP, 'lo.pdf'))
if shutil.which('soffice') and lo_ok():
    r = subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', TMP, f], capture_output=True, timeout=180)
    pdf = _os.path.join(TMP, 'out.pdf'); ok(_os.path.exists(pdf) and _os.path.getsize(pdf) > 2000, f"LibreOffice로 열림(PDF 변환 {(_os.path.getsize(pdf) if _os.path.exists(pdf) else 0)} B)")
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
