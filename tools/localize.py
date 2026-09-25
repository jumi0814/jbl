"""claude.ai 대화에서 만든 JBL_master.zip(도구·원고·지침 안전판)을 이 저장소에 반영한다.
사용: .venv/bin/python tools/localize.py ~/Downloads/JBL_master.zip   (또는 풀어 둔 JBL/ 폴더)

- tools/<과목>/ 전부: 받은 파일로 덮어쓰되 claude.ai 경로(/home/claude/…, /mnt/user-data/…)를 저장소 경로(tools/jblpaths.py)로 바꾼다.
  받은 zip에 없는 저장소 파일(예: cons/ocr.py)은 그대로 둔다.
- guide/, .claude/commands/: 그대로 복사.  CLAUDE.md·SPEC.md는 덮어쓰지 않고 차이만 보여준다(저장소판에 로컬 환경 설명이 있어서).
- 바꾼 뒤 claude.ai 경로가 하나라도 남으면 실패로 끝낸다 → 규칙을 추가할 것."""
import os, re, sys, shutil, zipfile, tempfile, difflib, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAD = re.compile(r"/home/claude|/mnt/user-data|TESSDATA_PREFIX|f'/tmp/")
PRE = "import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py\n"
HERE = "_os.path.dirname(_os.path.abspath(__file__))"

def unpack(src):
    if os.path.isdir(src): return src
    d = tempfile.mkdtemp(prefix='jblmaster_'); zf = zipfile.ZipFile(src)
    for i in zf.infolist():
        n = i.filename
        if not i.flag_bits & 0x800:
            try: n = n.encode('cp437').decode('utf-8')
            except Exception: pass
        n = unicodedata.normalize('NFC', n); p = os.path.join(d, n)
        if n.endswith('/'): os.makedirs(p, exist_ok=True); continue
        os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'wb').write(zf.read(i))
    return os.path.join(d, 'JBL') if os.path.isdir(os.path.join(d, 'JBL')) else d

def localize(s, sid, fn):
    o = s
    # 빌드 출력 → docs/ (허브 index.html + packs/), 단일 파일판 → work/, zip 없음
    s = s.replace("OUT = '/mnt/user-data/outputs/JBL_HUB'; os.makedirs(OUT + '/packs', exist_ok=True)\nopen(OUT + '/JBL_HUB.html', 'w'",
                  "OUT = J.DOCS; os.makedirs(OUT + '/packs', exist_ok=True)\nopen(OUT + '/index.html', 'w'")
    s = s.replace("""open(f'/mnt/user-data/outputs/{S.TITLE.replace(" ", "")}_JBL.html', 'w'""",
                  """SINGLE = _os.path.join(J.WORK, f'{S.TITLE.replace(" ", "")}_JBL.html')   # 단일 파일판 — work/에만, 커밋 안 함\nopen(SINGLE, 'w'""")
    s = re.sub(r"with zipfile\.ZipFile\('/mnt/user-data/outputs/JBL_HUB\.zip'.*\n(?:    .*\n)+", "", s)
    s = re.sub(r"\{f: round\(os\.path\.getsize\('/mnt/user-data/outputs/' \+ f\) / 1e6, 2\) for f in \[[^\]]*\]\}",
               "{_os.path.relpath(f, J.ROOT): round(_os.path.getsize(f) / 1e6, 2) for f in [OUT + f'/packs/{SID}.js', SINGLE]}", s)
    # 강의 쪽 이미지 원본이 없으면 지금 docs/에 있는 같은 쪽 이미지를 그대로 씀
    s = s.replace("""lecimg = {}
for (k, p) in sorted(ctx['cited'] | {(k_, p_) for k_, r_ in S.FORCE_PAGES.items() for p_ in r_}):
    f = S.lec_img_path(k, p)
    if not f or not os.path.exists(f): continue
""", """lecimg = {}; PREV = J.prev_images(SID)   # 강의 원본 이미지가 없으면 지금 docs/에 올라가 있는 이미지를 그대로 씀
for (k, p) in sorted(ctx['cited'] | {(k_, p_) for k_, r_ in S.FORCE_PAGES.items() for p_ in r_}):
    f = S.lec_img_path(k, p)
    if not f or not os.path.exists(f):
        if f and f'{k}-{p}' in PREV: lecimg[f'{k}-{p}'] = PREV[f'{k}-{p}']
        continue
""")
    s = re.sub(r"    os\.makedirs\('/mnt/user-data/outputs', exist_ok=True\)\n    open\('/mnt/user-data/outputs/[^']+'",
               f"    open(J.work('{sid}', 'build2_view.html')", s)
    # JB 추출 폴더·작업 폴더
    s = re.sub(r"'/home/claude/jb/x/'", "J.JBX", s)
    s = re.sub(r"sys\.path\.insert\(0, *'/home/claude/[^']*'\)", f"sys.path.insert(0, {HERE})", s)
    s = re.sub(r"open\('/home/claude/[^'/]+/jb_blocks\.json'", f"open(J.work('{sid}', 'jb_blocks.json')", s)
    s = re.sub(r"open\('jb_blocks\.json' *, *'w'\)", f"open(J.work('{sid}', 'jb_blocks.json'), 'w')", s)
    s = re.sub(r"LEC_IMG_ROOT = '/home/claude/[^']*'", f"LEC_IMG_ROOT = J.work('{sid}', 'lec') + '/'     # 강의 쪽 이미지: work/{sid}/lec/<폴더>/<쪽>.jpg", s)
    s = re.sub(r"^LEC = '/home/claude/[^']*'", f"LEC = J.work('{sid}', 'lec') + '/'", s, flags=re.M)
    # 옛 형식 lectures1/2.txt(OMS1 단일 파일판용)는 저장소에 없으면 건너뜀
    s = s.replace("    for line in open('/home/claude/build/' + fn, encoding='utf-8'):",
                  f"    if not _os.path.exists(_os.path.join({HERE}, fn)): continue\n    for line in open(_os.path.join({HERE}, fn), encoding='utf-8'):")
    # JB 그림 조각: work/<SID>/crops/ — 없으면 docs/ 팩에 박힌 조각을 그대로 씀
    s = re.sub(r"for f in os\.listdir\('/home/claude/[^']+/crops'\):\n    im = Image\.open\('/home/claude/[^']+/crops/' \+ f\)\.convert\('RGB'\)\n((?:    .*\n)*)",
               lambda m: f"CROP_DIR = J.work('{sid}', 'crops')\nfor f in (sorted(_os.listdir(CROP_DIR)) if _os.path.isdir(CROP_DIR) else []):\n    im = Image.open(_os.path.join(CROP_DIR, f)).convert('RGB')\n{m.group(1)}for k, v in J.prev_crops('{sid}', CROPS).items(): IMG['crop'].setdefault(k, v)\n", s)
    s = re.sub(r"open\('/home/claude/[^'/]+/([^'/]+)'", lambda m: f"open(_os.path.join({HERE}, '{m.group(1)}')", s)
    # OCR·idx: work/<SID>/에서 실행, tesseract는 Homebrew 기본 tessdata
    s = re.sub(r"os\.environ\['TESSDATA_PREFIX'\] *= *'[^']*'", f"_os.chdir(J.work('{sid}'))   # 강의 PDF·OCR 결과는 work/{sid}/, tesseract는 Homebrew 기본 tessdata", s)
    s = s.replace("tmp=f'/tmp/", "tmp=f'{k}o/_")
    if fn == 'idx.py' and 'J.work' not in s:
        s = s.replace("if __name__=='__main__':\n", f"if __name__=='__main__':\n    _os.chdir(J.work('{sid}'))\n", 1)
    if s != o or 'J.' in s: s = PRE + s
    return s

def main(src):
    M = unpack(src); rep = []
    for sub in sorted(os.listdir(os.path.join(M, 'tools'))):
        sd = os.path.join(M, 'tools', sub)
        if not os.path.isdir(sd): continue
        sid = sub.upper(); dst = os.path.join(ROOT, 'tools', sub); os.makedirs(dst, exist_ok=True)
        for fn in sorted(os.listdir(sd)):
            p = os.path.join(sd, fn)
            if not os.path.isfile(p) or fn.endswith('.pyc'): continue
            data = open(p, 'rb').read()
            if fn == 'SPEC.md': data = open(os.path.join(ROOT, 'tools', 'SPEC.md'), 'rb').read()   # 과목 폴더 사본은 저장소 tools/SPEC.md와 같게
            if fn.endswith('.py'):
                t = localize(data.decode('utf-8'), sid, fn)
                left = [f'{fn}:{i}: {l.strip()[:90]}' for i, l in enumerate(t.split('\n'), 1) if BAD.search(l)]
                if left: sys.exit(f'✗ tools/{sub}/{fn}: 바꾸지 못한 claude.ai 경로 — tools/localize.py에 규칙 추가 필요\n  ' + '\n  '.join(left))
                data = t.encode('utf-8')
            q = os.path.join(dst, fn); old = open(q, 'rb').read() if os.path.exists(q) else None
            if old != data: open(q, 'wb').write(data); rep.append(('새 파일' if old is None else '갱신', f'tools/{sub}/{fn}'))
    for sub in ('guide', '.claude/commands'):
        sd = os.path.join(M, sub)
        if not os.path.isdir(sd): continue
        for fn in sorted(os.listdir(sd)):
            p = os.path.join(sd, fn); q = os.path.join(ROOT, sub, unicodedata.normalize('NFC', fn))
            if not os.path.isfile(p): continue
            os.makedirs(os.path.dirname(q), exist_ok=True); data = open(p, 'rb').read(); old = open(q, 'rb').read() if os.path.exists(q) else None
            if old != data: open(q, 'wb').write(data); rep.append(('새 파일' if old is None else '갱신', f'{sub}/{fn}'))
    for k, v in rep: print(f'  {k:4} {v}')
    print(f'반영 {len(rep)}개')
    for doc in ('CLAUDE.md', 'tools/SPEC.md'):
        a, b = os.path.join(ROOT, doc), os.path.join(M, doc)
        if os.path.exists(b) and open(a, encoding='utf-8').read() != open(b, encoding='utf-8').read():
            print(f'\n--- {doc}: 받은 판과 다름(자동 덮어쓰기 안 함 — 확인 후 손으로 합칠 것)')
            sys.stdout.writelines(difflib.unified_diff(open(a, encoding='utf-8').readlines(), open(b, encoding='utf-8').readlines(), '저장소', '받은 판', n=0))

if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit(__doc__)
    main(os.path.expanduser(sys.argv[1]))
