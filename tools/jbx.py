"""JB PDF → work/jb/<SID>_20xx/ (N.txt · N.jpeg · manifest.json) — 파이프라인이 읽는 판본 폴더 형식.
사용: python3 tools/jbx.py [SID ...]   (인자 없으면 전 과목)
jb/ 파일명: '2025 3Q <과목> JB.pdf' 또는 '2025_3Q_<과목>_JB.pdf'. 실제 PDF든 ZIP(N.txt·N.jpeg·manifest.json)이든 처리."""
import os, re, sys, json, zipfile, unicodedata, pymupdf, pypdfium2
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBJ = {'구강악안면외과학1': 'OMS1', '임상치과보존학': 'CONS', '치과임플란트학': 'IMPL', '임상두경부해부학': 'ANAT',
        '노인치과학': 'GERI', '임상치과약물치료학': 'PHARM', '심미치과학': 'ESTH'}
IMG_W = 924
def nfc(s): return unicodedata.normalize('NFC', s)
def sources():
    d = os.path.join(ROOT, 'jb')
    for f in sorted(os.listdir(d)):
        m = re.match(r'^(20\d\d)[ _]3Q[ _](.+?)[ _]JB\.(pdf|zip)$', nfc(f), re.I)
        if m and m.group(2) in SUBJ: yield SUBJ[m.group(2)], m.group(1), os.path.join(d, f)
def extract(src, out):
    os.makedirs(out, exist_ok=True)
    if zipfile.is_zipfile(src):
        zipfile.ZipFile(src).extractall(out); return
    # 텍스트 = pdfium(기존 팩을 만든 변환과 같은 줄·띄어쓰기·\r\n, 줄끝 하이픈은 \x02 → 파서 rd()가 지움), 쪽 이미지 = pymupdf
    doc = pymupdf.open(src); txt = pypdfium2.PdfDocument(src); pages = []
    for i, pg in enumerate(doc, 1):
        open(f'{out}/{i}.txt', 'w', encoding='utf-8', newline='').write(txt[i - 1].get_textpage().get_text_range().replace('\ufffe', '\x02'))
        z = IMG_W / pg.rect.width
        pg.get_pixmap(matrix=pymupdf.Matrix(z, z)).pil_save(f'{out}/{i}.jpeg', quality=90)
        pages.append({'page_number': i, 'has_visual_content': bool(pg.get_images())})
    json.dump({'source': os.path.basename(src), 'pages': pages}, open(f'{out}/manifest.json', 'w'), ensure_ascii=False, indent=1)
if __name__ == '__main__':
    want = set(sys.argv[1:])
    for sid, yr, src in sources():
        if want and sid not in want: continue
        out = os.path.join(ROOT, 'work', 'jb', f'{sid}_{yr}'); extract(src, out)
        print(sid, yr, '→', os.path.relpath(out, ROOT), len([f for f in os.listdir(out) if f.endswith('.txt')]), 'pages')
