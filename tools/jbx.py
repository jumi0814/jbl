"""JB PDF → work/jb/<SID>_20xx/ (N.txt · N.jpeg · manifest.json) — 파이프라인이 읽는 판본 폴더 형식.
사용: python3 tools/jbx.py [SID ...] [--force]   (인자 없으면 전 과목 · 이미 푼 판은 건너뜀 — --force면 다시)
jb/ 파일명: '2025 3Q <과목> JB.pdf' 또는 '2025_3Q_<과목>_JB.pdf' · 4Q 과목은 '2025 4Q <과목> JB.pdf'(과목 이름 = tools/quarters.json subjects의 jb). 실제 PDF든 ZIP(N.txt·N.jpeg·manifest.json)이든 처리."""
import os, re, sys, json, zipfile, unicodedata, pymupdf, pypdfium2
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import quarters as QS   # 11-04 분기 등록표 — (쿼터, JB 이름) → SID
SUBJQ = {}
for k, v in QS.SUBJ.items():   # 11-05 JB 파일 과목 이름 = 등록표 jb · 자료 폴더 이름(mat) · 정식 이름 띄어쓰기 없이 — 4Q JB 파일 이름을 아직 몰라서(예 '구강악안면외과학2'·'구강악안면외과학')
    for nm in (v['jb'], v['mat'], v['ko'].replace(' ', '')): SUBJQ.setdefault((v['q'], unicodedata.normalize('NFC', nm)), k)
SUBJ = {j: k for (q, j), k in SUBJQ.items() if q == '3q' and QS.SUBJ[k]['jb'] == j}   # 옛 호출(3Q 이름 → SID) 호환
IMG_W = 924
def nfc(s): return unicodedata.normalize('NFC', s)
UNKNOWN = []   # 알아보지 못한 파일(이름·자리) — main이 알림
def sources():
    """jb/ 아래 전부(11-15 — 하위 폴더도): ① 이름 '20YY 3Q|4Q <과목> JB.pdf|zip'(어느 폴더든) ② jb/<3Q|4Q>/<과목 폴더>/ 안의 PDF·ZIP — 이름에 연도 네 자리(20YY)만 있으면 됨(tools/folders.py가 만든 자리)"""
    d = os.path.join(ROOT, 'jb')
    if not os.path.isdir(d): return
    for dp, dirs, files in os.walk(d):
        dirs.sort(); parts = [nfc(x) for x in os.path.relpath(dp, d).split(os.sep) if x != '.']
        for f in sorted(files):
            n = nfc(f)
            if not n.lower().endswith(('.pdf', '.zip')): continue
            m = re.match(r'^(20\d\d)[ _]([34])Q[ _](.+?)[ _]JB\.(pdf|zip)$', n, re.I)   # 11-04 '20YY 3Q …' · '20YY 4Q …'(쿼터 = 그 과목 분기)
            k = m and SUBJQ.get((m.group(2) + 'q', m.group(3)))
            if k: yield k, m.group(1), os.path.join(dp, f); continue
            if len(parts) >= 2 and re.fullmatch(r'[34]Q', parts[0], re.I):   # jb/4Q/<과목>/<아무 이름 + 연도>.pdf
                k = SUBJQ.get((parts[0][0] + 'q', parts[1])) or SUBJQ.get((parts[0][0] + 'q', parts[1].replace(' ', '')))
                y = re.search(r'(?<!\d)(20\d\d)(?!\d)', n)
                if k and y: yield k, y.group(1), os.path.join(dp, f); continue
                UNKNOWN.append((os.path.relpath(os.path.join(dp, f), ROOT), '과목 폴더 이름을 모름' if not k else "이름에 연도(예 '2025')가 없음")); continue
            UNKNOWN.append((os.path.relpath(os.path.join(dp, f), ROOT), "이름이 '20YY 4Q <과목> JB.pdf' 꼴이 아님 — jb/4Q/<과목>/ 에 넣으면 연도만 있으면 됨"))
def done(src, out):
    """이미 풀었음 = manifest가 있고 원본보다 새것(PDF면 같은 원본 이름) — 다시 풀지 않음(--force면 다시)"""
    mf = os.path.join(out, 'manifest.json')
    if '--force' in sys.argv or not os.path.exists(mf) or os.path.getmtime(mf) < os.path.getmtime(src): return False
    if zipfile.is_zipfile(src): return True
    try: return nfc(json.load(open(mf, encoding='utf-8')).get('source', '')) == nfc(os.path.basename(src))
    except Exception: return False
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
    want = {a for a in sys.argv[1:] if not a.startswith('--')}; seen = {}; nnew = 0
    for sid, yr, src in sources():
        if want and sid not in want: continue
        if (sid, yr) in seen: print(f'  ! {sid} {yr}판이 두 파일: {os.path.relpath(seen[(sid, yr)], ROOT)} · {os.path.relpath(src, ROOT)} — 뒤 것은 건너뜀(하나만 두세요)'); continue
        seen[(sid, yr)] = src; out = os.path.join(ROOT, 'work', 'jb', f'{sid}_{yr}')
        if done(src, out): print(f'  = {sid} {yr}판 이미 풂'); continue
        extract(src, out); nnew += 1
        print(f'  + {sid} {yr}판 → {os.path.relpath(out, ROOT)} {len([f for f in os.listdir(out) if f.endswith(".txt")])}쪽')
    for f, why in UNKNOWN: print(f'  ? 알아보지 못함: {f} — {why}')
    print(f'JB 새로 푼 판 {nnew} · 이미 푼 판 {len(seen) - nnew} · 알아보지 못한 파일 {len(UNKNOWN)}')
