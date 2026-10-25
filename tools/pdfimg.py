"""PDF 한 개 → 강의 쪽 이미지(클라우드용 — pymupdf·tesseract 없이 pypdfium2만). 10-25 GERI OHQ: pptx로 먼저 받은 26 강의에 필기 포함 PDF가 따로 왔을 때.
사용: .venv/bin/python -I tools/pdfimg.py <SID> <파일id> <PDF 경로> [--force]     (pypdfium2가 없으면 .venv/bin/pip install pypdfium2)
- 먼저 tools/matx.py SRC에 그 파일 앞머리 폴더를 넣어 둔다(예 'G12i': '260910_') — 그래야 work/<SID>/lec/<폴더> 연결까지 함
- work/<SID>/mat/<파일id>/i/<쪽>.jpg (폭 1100, JPEG q82 — matx.py와 같은 꼴) · t/<쪽>.txt는 없을 때만(pptx 글이 있으면 그대로 두고 PDF 글과 쪽마다 대조해 순서가 같은지 출력)
- work/<SID>/mat/index.json 그 항목을 kind=pdf로 · PDF 주석(필기) 글은 t/에 넣지 않음 — 필기는 i/ 이미지를 Read로 본다
- 그 뒤: subject.py LECMAP 그 키 폴더 · F: 26 쪽 그림 · build4 (RULES 1절 'PDF가 오면')"""
import os, sys, json, re, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J
import pypdfium2 as P

nfc = lambda s: unicodedata.normalize('NFC', s)
a = [x for x in sys.argv[1:] if not x.startswith('--')]; force = '--force' in sys.argv
if len(a) != 3: sys.exit(__doc__)
sid, fid, src = a[0].upper(), nfc(a[1]), a[2]
out = os.path.join(J.work(sid, 'mat'), fid)
for s in ('t', 'i'): os.makedirs(os.path.join(out, s), exist_ok=True)
sq = lambda t: re.sub(r'\s+', '', t)
d = P.PdfDocument(src); n = len(d); same = []; diff = []
for i in range(n):
    pg = d[i]; f = os.path.join(out, 'i', f'{i + 1}.jpg')
    if force or not os.path.exists(f):
        w, _ = pg.get_size()
        pg.render(scale=1100 / w, draw_annots=True).to_pil().convert('RGB').save(f, quality=82)
    pt = pg.get_textpage().get_text_range().replace('\r', '')
    t = os.path.join(out, 't', f'{i + 1}.txt')
    if not os.path.exists(t): open(t, 'w', encoding='utf-8').write(pt)
    else:
        head = sq(pt)[:20]; old = sq(open(t, encoding='utf-8').read())
        (same if head and head in old else diff).append(i + 1)
ix = os.path.join(J.work(sid, 'mat'), 'index.json')
idx = json.load(open(ix, encoding='utf-8')) if os.path.exists(ix) else {}
e = idx.setdefault(fid, {}); e.update({'file': nfc(e['file']).rsplit('.', 1)[0] + '.pdf' if e.get('file') else fid + '.pdf', 'pages': n, 'kind': 'pdf'})
json.dump(idx, open(ix, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# 폴더 연결 — matx.py와 같은 판정(index의 원래 파일명이 SRC 앞머리로 시작하는 항목이 하나일 때만)
m = re.search(r"'%s':\s*\{([^}]*)\}" % sid, open(os.path.join(J.ROOT, 'tools', 'matx.py'), encoding='utf-8').read())
lec = J.work(sid, 'lec'); os.makedirs(lec, exist_ok=True); done = []
for k, pre in re.findall(r"'(\w+)':\s*'([^']*)'", m.group(1) if m else ''):
    hit = [x for x, v in idx.items() if nfc(v.get('file', '')).startswith(pre)]
    if fid not in hit: continue
    if len(hit) != 1: print(f'  ✗ {k}: 앞머리 {pre} → 파일 {len(hit)}개 {hit} — 하나만 남기기'); continue
    link = os.path.join(lec, k)
    if os.path.islink(link): os.remove(link)
    if os.path.exists(link): print(f'  ✗ {link}가 링크가 아닌 진짜 폴더 — 손으로 확인'); continue
    os.symlink(os.path.join('..', 'mat', fid, 'i'), link); done.append(k)
print(f'{sid} {fid}: {n}쪽 → {out}/i · 연결 {done or "없음(matx.py SRC에 앞머리를 넣고 다시)"}'
      + (f' · 기존 t/와 쪽 순서 대조: 같음 {len(same)} · 다름 {diff}' if same or diff else ''))
