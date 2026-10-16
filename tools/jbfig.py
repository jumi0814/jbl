"""JB 그림 조각 상자 — 과목 팩 문항마다 JB 원본 쪽 이미지에서 그 문항 구역 안의 그림(사진·도식·그림 표)을 찾아 tools/<sid>/jb_crops.json에 쓴다.
build4.py가 이 상자로 쪽 이미지를 잘라 문항 카드 문제 아래(q)·JB 답안 안(a)에 붙인다(SPEC.md 'JB 그림 조각').
사용:
  .venv/bin/python tools/jbfig.py SID…                 # 문항 전부 → tools/<sid>/jb_crops.json (fix 항목은 그대로 둠)
  .venv/bin/python tools/jbfig.py SID --dump           # + 검수용 조각 work/_tmp/jbfig/<SID>/<id>_q1.jpg … · 쪽 표시 work/_tmp/jbfig/<SID>/pages/<판>-<쪽>.jpg
  .venv/bin/python tools/jbfig.py SID --ids Q13,R05 --dump --dry   # 일부 문항만 · --dry = json 안 씀
  .venv/bin/python tools/jbfig.py --page SID 25 8      # 쪽 하나의 그림 상자만(문항 무관, 디버그) → work/_tmp/jbfig/page_<SID>_<판>-<쪽>.jpg
jb_crops.json = {문항id: {"q": [{"ed": "25", "pg": 14, "box": [x0, y0, x1, y1]}, …], "a": [...]}}  상자 = 924폭 쪽 이미지(work/jb/<SID>_20<판>/<쪽>.jpeg) 픽셀
  상자에 "fix": true → 다시 돌려도 그대로(같은 쪽에서 겹치는 자동 상자는 버림) · 문항에 "fix": true → 문항 항목 전체를 그대로
  문항 "nofig": "absent"(문제는 그림을 말하지만 JB에 그림이 실려 있지 않음 — 카드 안내를 그렇게 바꿈) | "text"(그림 문항이 아님 — 안내 숨김) · "note": 사람 메모
방법: 23~25판 = tesseract tsv(kor+eng) 글줄 상자 → 그 쪽 N.txt 줄과 순서 맞춤(DP) → 본문 글줄·얇은 곧은 선(글상자 테두리·밑줄)을 지운 잉크의
      세로 띠 = 그림 → 그림 안·가장자리 라벨 글자, 그림에 이어진 선(화살표·빈칸 밑줄)까지 넓힘 → 여백 10px(본문 글줄 앞에서 멈춤).
      26판 이후(원본 PDF jb/20xx 3Q <과목> JB.pdf가 있으면) = pymupdf 글줄 상자(정확) + 이미지 배치 상자도 그림 후보로.
      그림 바로 앞 글줄이 문제 쪽(첫 '답' 줄 앞 — build4 split_qa와 같은 규칙)이면 'q', 답 쪽이면 'a'.
      'q' 상자는 답 쪽 글줄과 겹치지 않게 자른다(답이 문제 조각에 보이지 않게). 본 판에서 문제 그림을 못 찾으면 같은 문제의 다른 판본에서.
assemble.py의 기존 CROPS(조각 파일)가 있는 문항은 자동 상자를 만들지 않음(같은 그림 두 번 금지 — 손으로 fix 항목을 넣으면 build4가 CROPS에 없는 종류에만 덧붙임)."""
import os, sys, re, json, subprocess, difflib, unicodedata, argparse, importlib
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageChops
TOOLS = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TOOLS)
import jblpaths as J
OUT = os.path.join(J.TMP, 'jbfig')
SUBJ = {'OMS1': '구강악안면외과학1', 'CONS': '임상치과보존학', 'IMPL': '치과임플란트학', 'ANAT': '임상두경부해부학',
        'GERI': '노인치과학', 'PHARM': '임상치과약물치료학', 'ESTH': '심미치과학'}
IMG_W = 924
# build4 split_qa와 같은 틀(문제 → 첫 '답' 줄부터 답 · '유사복원)' 등에서 다시 문제) — build4를 고치면 같이
ANS = re.compile(r'^\s*(\[답\]|답\s*[:：)]|답\s*$)')
LABEL = re.compile(r'^\s*(\[답\]|답\s*[:：)]?|해설\s*[:：)]?|참고\s*[:：)]?)(.*)$')   # build4 split_qa(reflow.LABEL)
REQ = re.compile(r'^\s*(유사복원\)|추가복원\)|\*?비슷한 복원|복원 원문)')
nfc = lambda s: unicodedata.normalize('NFC', s)
def norm(s): return re.sub(r'[^0-9a-z가-힣]', '', nfc(s).lower())
def onorm(t):
    """OCR 줄 정규화 — 짧은 '답)' 줄을 OCR이 '탑)'·'닫)'으로 읽는 것 바로잡음"""
    s = norm(t)
    return '답' + s[1:] if 0 < len(s) <= 4 and s[0] in '탑닫담' else s
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def jpeg(sid, ed, pg): return f'{J.JBX}{sid}_20{ed}/{pg}.jpeg'
def txtp(sid, ed, pg): return f'{J.JBX}{sid}_20{ed}/{pg}.txt'
def npages(sid, ed):
    d = f'{J.JBX}{sid}_20{ed}'
    return max([int(f[:-4]) for f in os.listdir(d) if re.fullmatch(r'\d+\.txt', f)] or [0]) if os.path.isdir(d) else 0
def page_lines(sid, ed, pg):
    """N.txt의 비지 않은 줄(파서 load와 같은 거름 — 무단인쇄 머리·첫 쪽 번호 줄 뺌)"""
    out, first = [], True
    for l in rd(txtp(sid, ed, pg)).split('\n'):
        if '무단인쇄' in l: continue
        if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue
        if l.strip(): first = False; out.append(l.rstrip())
    return out
# ---------------- 글줄 상자: OCR(23~25판) · PDF(원본이 있는 판)
_PDF = {}
def pdf_doc(sid, ed):
    if (sid, ed) not in _PDF:
        _PDF[(sid, ed)] = None; d = os.path.join(J.ROOT, 'jb')
        for f in (sorted(os.listdir(d)) if os.path.isdir(d) else []):
            if re.fullmatch(r'20%s[ _]3Q[ _]%s[ _]JB\.pdf' % (ed, re.escape(SUBJ[sid])), nfc(f), re.I):
                try:
                    import pymupdf; _PDF[(sid, ed)] = pymupdf.open(os.path.join(d, f))
                except Exception as e: print('PDF 열기 실패', f, e)
                break
    return _PDF[(sid, ed)]
def ocr_tsv(img, psm='3', tag=''):
    c = (img[:-4] if img.startswith(OUT) else os.path.join(OUT, 'ocr', re.sub(r'[^\w.-]+', '_', os.path.relpath(img, J.JBX)))) + tag + '.tsv'
    if not (os.path.exists(c) and os.path.getmtime(c) >= os.path.getmtime(img)):
        os.makedirs(os.path.dirname(c), exist_ok=True)
        r = subprocess.run(['tesseract', img, 'stdout', '-l', 'kor+eng', '--psm', psm, 'tsv'], capture_output=True, text=True,
                           env=dict(os.environ, OMP_THREAD_LIMIT='1'))
        open(c, 'w', encoding='utf-8').write(r.stdout)
    return open(c, encoding='utf-8').read()
def tsv_words(t, dx=0, dy=0, tag=0):
    ws = []
    for row in t.split('\n')[1:]:
        f = row.split('\t')
        if len(f) < 12 or f[0] != '5' or not f[11].strip(): continue
        x, y, w, h = map(int, f[6:10])
        ws.append({'x0': x + dx, 'y0': y + dy, 'x1': x + w + dx, 'y1': y + h + dy, 't': f[11].strip(), 'c': float(f[10]), 'ln': (tag, int(f[2]), int(f[3]), int(f[4]))})
    return ws
def words_of(sid, ed, pg):
    """[{x0,y0,x1,y1,t,c,ln}] + 이미지 배치 상자(PDF가 있을 때)"""
    doc = pdf_doc(sid, ed)
    if doc is not None and pg <= len(doc):
        p = doc[pg - 1]; z = IMG_W / p.rect.width; ws = []
        for x0, y0, x1, y1, t, b, l, _ in p.get_text('words'):
            if t.strip(): ws.append({'x0': x0 * z, 'y0': y0 * z, 'x1': x1 * z, 'y1': y1 * z, 't': t, 'c': 100.0, 'ln': (b, l)})
        ims = []   # 이미지 배치 상자(그림 후보)
        for info in p.get_image_info():
            x0, y0, x1, y1 = [v * z for v in info['bbox']]
            if x1 - x0 > 12 and y1 - y0 > 12: ims.append([x0, y0, x1, y1])
        return ws, ims, 'pdf'
    return tsv_words(ocr_tsv(jpeg(sid, ed, pg))), [], 'ocr'
def mklines(ws, W=IMG_W):
    G = {}
    for w in ws: G.setdefault(w['ln'], []).append(w)
    out = []
    for k, g in G.items():
        g.sort(key=lambda w: w['x0'])
        # 한 줄이 쪽 가운데(단 사이)를 큰 틈으로 건너면 나눔(양쪽 정렬 줄의 넓은 낱말 틈은 그대로 한 줄)
        parts = [[g[0]]]
        for w in g[1:]:
            a_, b_ = parts[-1][-1]['x1'], w['x0']
            if b_ - a_ > 30 and a_ < W / 2 + 25 and b_ > W / 2 - 25: parts.append([w])
            else: parts[-1].append(w)
        for p in parts:
            out.append({'x0': min(w['x0'] for w in p), 'y0': min(w['y0'] for w in p), 'x1': max(w['x1'] for w in p), 'y1': max(w['y1'] for w in p),
                        't': ' '.join(w['t'] for w in p), 'c': sum(w['c'] for w in p) / len(p), 'ws': p, 'ti': None})
    return out
def sim(a, b):
    if not a or not b: return 0.0
    if a == b: return 1.0
    m = difflib.SequenceMatcher(None, a, b, autojunk=False)
    if m.real_quick_ratio() < 0.5 or m.quick_ratio() < 0.5: return 0.0
    return m.ratio()
def contained(a, b, mn=4):
    """a(짧은 OCR 조각)가 b(txt 줄) 안에 이어진 채로 들어 있는 정도(가장 긴 공통 부분 / a 길이)"""
    if len(a) < mn or not b: return 0.0
    m = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return m.find_longest_match(0, len(a), 0, len(b)).size / len(a)
# ---------------- 쪽 분석
class Page:
    def __init__(self, sid, ed, pg):
        self.sid, self.ed, self.pg = sid, ed, pg
        self.im = Image.open(jpeg(sid, ed, pg)).convert('RGB'); self.W, self.H = self.im.size
        ws, self.pimgs, self.src = words_of(sid, ed, pg)
        if self.src == 'pdf' and abs(self.W - IMG_W) > 2:   # 쪽 이미지 폭이 다르면 PDF 좌표를 맞춤
            z = self.W / IMG_W
            for w in ws: w.update({k: w[k] * z for k in ('x0', 'y0', 'x1', 'y1')})
            self.pimgs = [[v * z for v in b] for b in self.pimgs]
        self.txt = page_lines(sid, ed, pg); self.setup(ws)
        if self.src == 'ocr' and self.quality() < 0.6:   # psm 3이 쪽 배치를 잘못 읽으면(글자가 낱자로 흩어짐) psm 4로 다시 — 맞춘 줄이 더 많은 쪽을 씀
            q0, keep = self.quality(), (self.words, self.lines, self.two, self.gut, self.body, self.marg)
            self.setup(tsv_words(ocr_tsv(jpeg(sid, ed, pg), '4', '_4')))
            if self.quality() <= q0: self.words, self.lines, self.two, self.gut, self.body, self.marg = keep
    def setup(self, ws):
        self.words = ws; self.lines = mklines(ws, self.W)
        self.layout(); self.lines.sort(key=self.key); self.align()
    def quality(self):
        return len({l['ti'] for l in self.body}) / max(1, len(self.txt))
    def layout(self):
        g = self.W / 2
        tx = lambda l: l['x1'] - l['x0'] > 110 and l['c'] > 50
        Lc = [l for l in self.lines if tx(l) and l['x1'] < g + 12]; Rc = [l for l in self.lines if tx(l) and l['x0'] > g - 12]
        self.two = len(Lc) >= 4 and len(Rc) >= 4
        if not self.two:   # OCR이 두 단을 한 줄로 읽은 쪽 — 가운데 세로 빈 띠(단 사이)가 있으면 두 단
            if not hasattr(self, '_gx'):
                m = self.im.convert('L').point(lambda v: 255 if v < 170 else 0); W, H = m.size; y0, y1 = 110, H - 90
                band = m.crop((int(g) - 30, y0, int(g) + 30, y1)).transpose(Image.Transpose.TRANSPOSE); bb = band.tobytes(); h = y1 - y0
                rows = m.crop((0, y0, W, y1)).resize((1, h)).tobytes()
                nrow = sum(1 for v in rows if v > 0) or 1
                cn = [bb[i * h:(i + 1) * h].count(255) for i in range(60)]; mn = min(cn); zs = [i for i, v in enumerate(cn) if v == mn]
                self._gx = (mn / nrow, int(g) - 30 + zs[len(zs) // 2])
            if self._gx[0] <= 0.02 and len(Lc) + len(Rc) >= 4: self.two = True; g = self._gx[1]
        if self.two and Lc and Rc:
            gl = max(l['x1'] for l in Lc); gr = min(l['x0'] for l in Rc)
            if gl < gr: g = (gl + gr) / 2
        self.gut = g
    def col(self, x0, x1):
        return 1 if self.two and (x0 + x1) / 2 > self.gut and x0 > self.gut - 40 else 0
    def key(self, l): return (self.col(l['x0'], l['x1']), (l['y0'] + l['y1']) / 2)
    def colx(self, c):
        if not self.two: return 0, self.W
        return (0, int(self.gut)) if c == 0 else (int(self.gut), self.W)
    def frag_ok(self, l, on, t):
        """txt 줄의 조각으로 볼 수 있나 — 충분히 길거나(txt 줄의 40% 이상) 단 가장자리에 붙은 조각만(그림 속 라벨이 본문으로 잡히지 않게)"""
        if len(on) >= 0.4 * len(t): return True
        L, R = self.marg.get(self.col(l['x0'], l['x1']), (0, self.W))
        return l['x0'] - L < 30 or R - l['x1'] < 30
    def align(self):
        T = [norm(t) for t in self.txt]; O = [onorm(l['t']) for l in self.lines]; n, m = len(T), len(O)
        S = [[0.0] * (m + 1) for _ in range(n + 1)]; B = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                best, b = S[i - 1][j], 1
                if S[i][j - 1] > best: best, b = S[i][j - 1], 2
                s = sim(T[i - 1], O[j - 1])
                if s >= 0.5 and S[i - 1][j - 1] + s > best: best, b = S[i - 1][j - 1] + s, 3
                S[i][j], B[i][j] = best, b
        i, j = n, m
        while i and j:
            b = B[i][j]
            if b == 3: self.lines[j - 1]['ti'] = i - 1; i -= 1; j -= 1
            elif b == 1: i -= 1
            else: j -= 1
        self.marg = {}
        for l in self.lines:
            if l['ti'] is None: continue
            c = self.col(l['x0'], l['x1']); L, R = self.marg.get(c, (1e9, -1e9)); self.marg[c] = (min(L, l['x0']), max(R, l['x1']))
        # 한 txt 줄이 OCR 두 줄로 갈린 것 — 맞춘 줄 사이의 txt 줄에 들어 있으면 본문
        for j, l in enumerate(self.lines):
            if l['ti'] is not None: continue
            pv = next((self.lines[k]['ti'] for k in range(j - 1, -1, -1) if self.lines[k]['ti'] is not None), 0)
            nx = next((self.lines[k]['ti'] for k in range(j + 1, m) if self.lines[k]['ti'] is not None), n - 1)
            best = max(((contained(O[j], T[i]), i) for i in range(pv, min(n, nx + 1)) if self.frag_ok(l, O[j], T[i])), default=(0, None))
            if best[0] >= 0.75: l['ti'] = best[1]; l['part'] = 1
        self.body = [l for l in self.lines if l['ti'] is not None]
        self.t2l = {}
        for l in self.body: self.t2l.setdefault(l['ti'], []).append(l)
    # ---- 그림 찾기
    def masks(self):
        g = self.im.convert('L').point(lambda v: 255 if v < 190 else 0)
        s = self.im.convert('HSV').split(); s = ImageChops.multiply(s[1].point(lambda v: 255 if v > 55 else 0), s[2].point(lambda v: 255 if v > 40 else 0))
        ink = ImageChops.lighter(g, s)
        m0 = ink.copy(); d = ImageDraw.Draw(m0)
        for l in self.body:
            cx0, cx1 = self.colx(self.col(l['x0'], l['x1']))
            if l['x1'] - l['x0'] >= 0.5 * (cx1 - cx0) and not l.get('v'): d.rectangle([cx0, l['y0'] - 2, cx1, l['y1'] + 2], fill=0)   # 긴 본문 줄은 단 폭 전체(양쪽 정렬 줄 끝 낱말을 OCR이 따로 떼어 읽은 것까지)
            else: d.rectangle([l['x0'] - 2, l['y0'] - 2, l['x1'] + 2, l['y1'] + 2], fill=0)
        self.m0 = m0                     # 본문 글줄만 지운 잉크(선·라벨 이어 넓히기용)
        self.m1 = drop_thin(m0)          # + 얇은 곧은 선(테두리·밑줄) 지움(그림 띠 찾기용)
    def cands(self, small=False):
        """그림 후보 상자 · small=True면 남은 잉크 띠 전부(작은 것까지 — 쪽 OCR이 놓친 글줄 찾기용)"""
        self.bodyw = {id(w) for l in self.body for w in l['ws']}
        self.masks(); cands = []
        for c in ((0, 1) if self.two else (0,)):
            x0, x1 = self.colx(c)
            for (ya, yb) in (row_bands(self.m1, x0, x1, 0, self.H, hmin=8, inkmin=60) if small else row_bands(self.m1, x0, x1, 0, self.H)):
                xr = col_range(self.m1, x0, x1, ya, yb)
                if xr: cands.append([xr[0], ya, xr[1], yb])
        if small: return cands
        for b in self.pimgs: cands.append([int(b[0]), int(b[1]), int(b[2]), int(b[3])])
        return merge_boxes(cands, self)
    def verify(self, boxes):
        """그림 후보를 다시 OCR(psm 6) — 그 쪽 N.txt 줄과 맞으면 본문(쪽 OCR이 놓친 글줄 · 회색 머리 상자 등)으로 넣음"""
        if self.src == 'pdf' or not boxes: return False
        T = [norm(t) for t in self.txt]; n = len(T); ch = False
        for b in boxes:
            x0, y0, x1, y1 = max(0, int(b[0]) - 4), max(0, int(b[1]) - 4), min(self.W, int(b[2]) + 4), min(self.H, int(b[3]) + 4)
            p = os.path.join(OUT, 'ocr', 'crop', f'{self.sid}_{self.ed}_{self.pg}_{x0}_{y0}_{x1}_{y1}.png')
            if not os.path.exists(p): os.makedirs(os.path.dirname(p), exist_ok=True); self.im.crop((x0, y0, x1, y1)).save(p)
            psm = '7' if y1 - y0 < 40 else '6'
            for l in mklines(tsv_words(ocr_tsv(p, psm, '_' + psm), x0, y0, ('v', x0, y0)), self.W):
                on = onorm(l['t'])
                if len(on) < 2: continue
                k = self.key(l)
                pv = max([x['ti'] for x in self.body if self.key(x) < k], default=0); nx = min([x['ti'] for x in self.body if self.key(x) > k], default=n - 1)
                small = y1 - y0 < 70   # 작은 띠 = 쪽 OCR이 놓친 본문 조각(들여쓴 줄 머리 등) — 조각 길이 조건 없이
                best = max(((max(sim(on, T[i]), contained(on, T[i], 3) * 0.75 if (small or self.frag_ok(l, on, T[i])) else 0), i) for i in range(max(0, pv), min(n, max(pv, nx) + 1))), default=(0, None))
                if best[0] >= 0.6: l['ti'] = best[1]; l['v'] = 1; self.lines.append(l); self.body.append(l); self.words += l['ws']; ch = True
        if ch: self.lines.sort(key=self.key)
        return ch
    def figures(self):
        if self.verify(self.cands(small=True)): pass
        cands = self.cands()
        out = []
        for b in cands:
            b = self.grow(b)
            if (b[2] - b[0]) < 36 or (b[3] - b[1]) < 36: continue   # 글줄 하나 높이의 찌꺼기는 그림 아님
            out.append(b)
        out = merge_boxes(out, self)
        out = [b for b in out if not self.textish(b)]
        out = [self.pad(b) for b in out]
        self.figs = [{'box': [int(v) for v in b], 'col': self.col(b[0], b[2])} for b in out]
        return self.figs
    def textish(self, b):
        """쪽 바탕(순백) 위의 글 덩어리(OCR이 본문으로 못 맞춘 글줄·글로 된 표 칸)인가 — 그림 바탕이 아닌 순백 비율 ≥ 0.9이고 OCR 낱말(신뢰 60↑)이 상자 넓이의 15%↑를 덮으면 그림 아님.
        PDF 이미지 배치 상자와 겹치면 그림으로 둠. 붙여 넣은 그림(슬라이드·표 사진)은 바탕이 순백이 아니라 남음"""
        if any(iou(b, p) > 0.1 for p in self.pimgs): return False
        x0, y0, x1, y1 = [int(v) for v in b]
        if x1 - x0 < 2 or y1 - y0 < 2: return True
        im = self.im.crop((x0, y0, x1, y1)); g = im.convert('L').tobytes(); px = im.tobytes(); n = w = 0
        for i in range(0, len(g), 3):
            if g[i] >= 190:
                n += 1
                if px[3 * i] >= 250 and px[3 * i + 1] >= 250 and px[3 * i + 2] >= 250: w += 1
        if not n or w / n < 0.9: return False
        cov = sum(max(0, min(x1, wd['x1']) - max(x0, wd['x0'])) * max(0, min(y1, wd['y1']) - max(y0, wd['y0'])) for wd in self.words if wd['c'] >= 60 and len(norm(wd['t'])) >= 2)
        if cov / ((x1 - x0) * (y1 - y0)) >= 0.15: return True
        # OCR이 글자를 못 읽은 글 덩어리: 잉크 줄이 글줄 높이(8~28px) 덩어리로만 되어 있으면 글
        m = im.convert('L').point(lambda v: 255 if v < 170 else 0); W_ = x1 - x0; bb = m.tobytes()
        prof = [bb[y * W_:(y + 1) * W_].count(255) for y in range(y1 - y0)]
        runs, cur = [], None
        for i, v in enumerate(prof + [0]):
            if v >= 2: cur = [i, i + 1] if cur is None else [cur[0], i + 1]
            elif cur is not None: runs.append(cur); cur = None
        ink = sum(b_ - a_ for a_, b_ in runs) or 1
        return len(runs) >= 2 and sum(b_ - a_ for a_, b_ in runs if 6 <= b_ - a_ <= 28) / ink >= 0.8
    def grow(self, b):
        b = list(b)
        for _ in range(3):   # 라벨 글자(본문이 아닌 글줄 낱말 · 본문 낱말이면 상자 안에 걸칠 때만)
            ch = False
            for w in self.words:
                isb = id(w) in self.bodyw
                e = 0 if isb else 8
                if w['x1'] >= b[0] - e and w['x0'] <= b[2] + e and w['y1'] >= b[1] - e and w['y0'] <= b[3] + e:
                    if isb and not inside_frac(w, b) > 0.5: continue
                    nb = [min(b[0], w['x0']), min(b[1], w['y0']), max(b[2], w['x1']), max(b[3], w['y1'])]
                    if nb != b: b = nb; ch = True
            if not ch: break
        m = self.m0; W, H = m.size; buf = m.tobytes()
        def cnt(x0, y0, x1, y1):
            x0, y0, x1, y1 = max(0, int(x0)), max(0, int(y0)), min(W, int(x1)), min(H, int(y1))
            if x1 <= x0 or y1 <= y0: return 0
            return sum(buf[y * W + x0:y * W + x1].count(255) for y in range(y0, y1))
        lim = [b[0] - 40, b[1] - 40, b[2] + 40, b[3] + 40]
        for _ in range(8):   # 그림에 이어진 선(화살표·빈칸 밑줄·테두리) — 바깥 6px 띠에 잉크가 있으면 넓힘(최대 40px)
            ch = False
            if b[0] > lim[0] and cnt(b[0] - 6, b[1], b[0], b[3]) >= 4: b[0] -= 6; ch = True
            if b[2] < lim[2] and cnt(b[2], b[1], b[2] + 6, b[3]) >= 4: b[2] += 6; ch = True
            if b[1] > lim[1] and cnt(b[0], b[1] - 6, b[2], b[1]) >= 4: b[1] -= 6; ch = True
            if b[3] < lim[3] and cnt(b[0], b[3], b[2], b[3] + 6) >= 4: b[3] += 6; ch = True
            if not ch: break
        return [max(0, b[0]), max(0, b[1]), min(W, b[2]), min(H, b[3])]
    def pad(self, b, p=10):
        x0, y0, x1, y1 = b; X0, Y0, X1, Y1 = x0 - p, y0 - p, x1 + p, y1 + p
        for l in self.body:
            if inside_frac(l, b) > 0.5: continue
            hov = min(x1, l['x1']) - max(x0, l['x0']) > 0; vov = min(y1, l['y1']) - max(y0, l['y0']) > 0
            if hov and l['y1'] <= y0 + 2: Y0 = max(Y0, min(y0, l['y1'] + 2))
            if hov and l['y0'] >= y1 - 2: Y1 = min(Y1, max(y1, l['y0'] - 2))
            if vov and l['x1'] <= x0 + 2: X0 = max(X0, min(x0, l['x1'] + 2))
            if vov and l['x0'] >= x1 - 2: X1 = min(X1, max(x1, l['x0'] - 2))
        return [max(0, X0), max(0, Y0), min(self.W, X1), min(self.H, Y1)]
    def pos(self, b):
        """그림 앞 본문 줄(읽는 순서)의 txt 줄 번호 — 없으면 -1(이 쪽 첫 줄보다 앞)"""
        k = (self.col(b[0], b[2]), b[1] + 4); best = -1
        for l in self.body:
            if self.key(l) < k and (best < 0 or l['ti'] > best): best = l['ti']
        return best
    def unread(self, b):
        """그림 앞 본문 줄과 뒤 본문 줄 사이에 OCR이 못 읽은 txt 줄 번호들(그림이 그 줄 앞인지 뒤인지 모름)"""
        p = self.pos(b); k = (self.col(b[0], b[2]), b[3] - 4)
        nx = min([l['ti'] for l in self.body if self.key(l) > k], default=len(self.txt))
        got = {l['ti'] for l in self.body}
        return [i for i in range(p + 1, nx) if i not in got]
def inside_frac(w, b):
    ix = min(w['x1'], b[2]) - max(w['x0'], b[0]); iy = min(w['y1'], b[3]) - max(w['y0'], b[1])
    a = max(1, (w['x1'] - w['x0']) * (w['y1'] - w['y0']))
    return max(0, ix) * max(0, iy) / a
def drop_thin(m, hmin=70, vmin=28):
    def h(img, minlen):
        W, H = img.size; buf = bytearray(img.tobytes()); pat = re.compile(rb'\xff{%d,}' % minlen); kill = []
        for y in range(H):
            row = bytes(buf[y * W:(y + 1) * W])
            for mm in pat.finditer(row):
                x0, x1 = mm.span(); L = x1 - x0
                up = buf[(y - 4) * W + x0:(y - 4) * W + x1].count(255) if y >= 4 else 0
                dn = buf[(y + 4) * W + x0:(y + 4) * W + x1].count(255) if y + 4 < H else 0
                if up < 0.3 * L and dn < 0.3 * L: kill.append((y, x0, x1))
        for y, x0, x1 in kill: buf[y * W + x0:y * W + x1] = bytes(x1 - x0)
        return Image.frombytes('L', (W, H), bytes(buf))
    T = Image.Transpose.TRANSPOSE
    return h(h(m, hmin).transpose(T), vmin).transpose(T)
def row_bands(m, x0, x1, y0, y1, gap=12, hmin=22, inkmin=350):
    W = m.size[0]; buf = m.tobytes()
    prof = [buf[y * W + x0:y * W + x1].count(255) for y in range(y0, y1)]
    runs, cur = [], None
    for i, v in enumerate(prof):
        if v >= 2:
            if cur and i - cur[1] <= gap: cur[1] = i + 1
            else:
                if cur: runs.append(cur)
                cur = [i, i + 1]
    if cur: runs.append(cur)
    return [(y0 + a, y0 + b) for a, b in runs if b - a >= hmin and sum(prof[a:b]) >= inkmin]
def col_range(m, x0, x1, ya, yb, gap=25):
    band = m.crop((x0, ya, x1, yb)).transpose(Image.Transpose.TRANSPOSE); bw = yb - ya; bb = band.tobytes()
    prof = [bb[x * bw:(x + 1) * bw].count(255) for x in range(x1 - x0)]
    cl, cur = [], None
    for i, v in enumerate(prof):
        if v >= 2:
            if cur and i - cur[1] <= gap: cur[1] = i + 1; cur[2] += v
            else:
                if cur: cl.append(cur)
                cur = [i, i + 1, v]
        elif cur and i - cur[1] <= gap: pass
    if cur: cl.append(cur)
    if not cl: return None
    mx = max(c[2] for c in cl); keep = [c for c in cl if c[2] >= 0.1 * mx and c[1] - c[0] >= 6]
    if not keep: return None
    return (x0 + min(c[0] for c in keep), x0 + max(c[1] for c in keep))
def merge_boxes(bs, P):
    bs = [list(b) for b in bs]; ch = True
    while ch:
        ch = False
        for i in range(len(bs)):
            for j in range(i + 1, len(bs)):
                a, b = bs[i], bs[j]
                hov = min(a[2], b[2]) - max(a[0], b[0]); vgap = max(a[1], b[1]) - min(a[3], b[3]); hgap = max(a[0], b[0]) - min(a[2], b[2])
                if (hov > 0 and vgap <= 14 and not body_between(P, a, b)) or (hgap <= 0 and vgap <= 0) or (vgap < -10 and hgap <= 14 and P.col(a[0], a[2]) == P.col(b[0], b[2])):
                    bs[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]; del bs[j]; ch = True; break
            if ch: break
    return bs
def body_between(P, a, b):
    lo, hi = sorted([a, b], key=lambda x: x[1])
    y0, y1 = lo[3], hi[1]; x0, x1 = max(a[0], b[0]), min(a[2], b[2])
    return any(l['y0'] >= y0 - 2 and l['y1'] <= y1 + 2 and min(x1, l['x1']) > max(x0, l['x0']) for l in P.body)
# ---------------- 문항 ↔ 쪽
_PG = {}
def page(sid, ed, pg):
    if (sid, ed, pg) not in _PG: _PG[(sid, ed, pg)] = Page(sid, ed, pg); _PG[(sid, ed, pg)].figures()
    return _PG[(sid, ed, pg)]
_GL = {}
def glines(sid, ed):
    """판 전체 비지 않은 줄 [(쪽, 쪽 안 txt 번호, 줄)]"""
    if (sid, ed) not in _GL:
        _GL[(sid, ed)] = [(p, i, l) for p in range(1, npages(sid, ed) + 1) for i, l in enumerate(page_lines(sid, ed, p))]
    return _GL[(sid, ed)]
def span(sid, ed, pg, text):
    G = glines(sid, ed); ql = [l for l in text.split('\n') if norm(l)]
    if not ql: return None
    eq = lambda a, b: norm(a) == norm(b) or sim(norm(a), norm(b)) >= 0.85
    st = [k for k, (p, _, l) in enumerate(G) if p == pg and norm(l) == norm(ql[0])] or [k for k, (p, _, l) in enumerate(G) if p == pg and eq(l, ql[0])]
    best = None
    for s in st:
        k, mt = s, [s]
        for x in ql[1:]:
            for k2 in range(k + 1, min(len(G), k + 6)):
                if eq(G[k2][2], x): k = k2; mt.append(k2); break
        if best is None or len(mt) > len(best): best = mt
    if not best: return None
    s, e = best[0], best[-1]; mode, modes = 'q', {}
    for k in range(s, e + 1):
        l = G[k][2]
        if REQ.match(l): mode = 'q'
        if ANS.match(l) or (LABEL.match(l) and '참고' not in l.split(':')[0] and re.match(r'^\s*(\[답\]|답)', l)): mode = 'a'   # build4 split_qa 규칙 ∪ '답) … 참고'도 답(답 쪽으로 보는 것이 안전)
        modes[k] = mode
    return s, e, modes
def gidx(sid, ed, pg, ti):
    """쪽 pg의 txt 줄 ti → 판 전체 번호(ti=-1이면 앞 쪽 마지막 줄)"""
    G = glines(sid, ed)
    for k, (p, i, _) in enumerate(G):
        if p == pg and i == max(ti, 0): return k if ti >= 0 else k - 1
    return None
def figs_for(sid, ed, pg, pg2, text):
    """한 블록(판·쪽 범위·원문) 안의 그림 [(kind, ed, pg, box, warn)]"""
    sp = span(sid, ed, pg, text)
    if not sp: return None
    s, e, modes = sp; G = glines(sid, ed); out = []
    for p in range(pg, (pg2 or pg) + 2):   # 다음 쪽 첫머리(블록 끝 줄 뒤 · 다음 블록 앞)에 실린 그림도
        if not os.path.exists(jpeg(sid, ed, p)): continue
        P = page(sid, ed, p)
        for f in P.figs:
            b = list(f['box']); gi = gidx(sid, ed, p, P.pos(b))
            if gi is None or not (s <= gi <= e): continue
            kind = modes[gi]; warn = ''
            un = [gidx(sid, ed, p, i) for i in P.unread(b)]
            if any(u is None or not (s <= u <= e) or modes.get(u) != kind for u in un): warn = 'OCR이 못 읽은 줄 옆 — 위치 확인'
            if kind == 'q' and any(u is not None and s <= u <= e and modes.get(u) == 'a' for u in un):
                # OCR이 못 읽은 줄 가운데 '답' 경계가 있음 — 그림 바로 아래(같은 단, 왼쪽 가장자리)에 짧은 못 읽은 줄('=)'·'탑)')이 있고 그림 위에는 없을 때만 문제 쪽, 아니면 답 쪽(안전)
                c_ = P.col(b[0], b[2]); L_ = P.marg.get(c_, (0, 0))[0]
                sh = [l for l in P.lines if l['ti'] is None and P.col(l['x0'], l['x1']) == c_ and 8 <= l['y1'] - l['y0'] <= 40 and l['x0'] - L_ < 40 and len(onorm(l['t'])) <= 6]
                below = any(b[3] - 8 <= l['y0'] <= b[3] + 60 for l in sh); above = any(b[1] - 60 <= l['y1'] and l['y0'] <= b[1] + 15 for l in sh)
                if below and not above: warn = (warn + ' · ' if warn else '') + '답 줄 OCR 못 읽음 — 그림 아래 짧은 줄을 답 줄로 봄'
                else: kind = 'a'; warn = (warn + ' · ' if warn else '') + '답 줄 위치 불확실 → 답 쪽(안전)'
            if kind == 'q':   # 답 경계(그림 뒤 첫 답 쪽 줄) 아래는 문제 조각에 넣지 않음 — 그림 속 라벨(상자 안 글줄)은 빼고 같은 단·같은 쪽의 답 쪽 본문 줄 위에서 자름
                ka = next((k for k in range(gi + 1, e + 1) if modes[k] == 'a'), None)
                if ka is not None:
                    ys = []
                    for l in P.body:
                        gl = gidx(sid, ed, p, l['ti'])
                        if gl is None or not (ka <= gl <= e) or P.col(l['x0'], l['x1']) != P.col(b[0], b[2]) or inside_frac(l, b) >= 0.5 or l['y1'] <= b[1] + 6: continue
                        ys.append(l['y0'])
                    if ys and min(ys) - 3 < b[3]: b[3] = int(min(ys)) - 3; warn = (warn + ' · ' if warn else '') + '답 줄 위에서 자름'
                    if G[ka][0] == p and not any(gidx(sid, ed, p, l['ti']) == ka for l in P.body): warn = (warn + ' · ' if warn else '') + '답 줄을 OCR이 못 읽음 — 확인'
                if b[3] - b[1] < 20: continue
            out.append((kind, ed, p, b, warn))
    return out
def load_assemble(sid):
    d = os.path.join(TOOLS, sid.lower())
    for k in [k for k in sys.modules if k in ('assemble', 'subject', 'emph', 'reflow', 'lecparse', 'trend') or k.startswith('parse_')]: del sys.modules[k]
    sys.path.insert(0, d)
    try:
        import assemble as A; importlib.reload(A)
    finally: sys.path.remove(d)
    return A
def thumb(sid, d):
    im = Image.open(jpeg(sid, d['ed'], d['pg'])).convert('L').crop(tuple(d['box']))
    return im.size, im.resize((24, 24)).tobytes()
def same_img(sid, a, b):
    try: (wa, ha), ta = thumb(sid, a); (wb, hb), tb = thumb(sid, b)
    except Exception: return False
    if abs(wa / ha - wb / hb) > 0.15 * (wa / ha): return False
    return sum(abs(x - y) for x, y in zip(ta, tb)) / len(ta) < 18
def iou(a, b):
    ix = min(a[2], b[2]) - max(a[0], b[0]); iy = min(a[3], b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0: return 0
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - ix * iy
    return ix * iy / u
def run(sid, ids=None, dump=False, dry=False):
    A = load_assemble(sid); Q = A.Q; CR = getattr(A, 'CROPS', {}) or {}
    eds = sorted({q['ed'] for q in Q} | {o['ed'] for q in Q for o in q.get('other', [])})
    todo = sorted({(e, p) for e in eds for p in range(1, npages(sid, e) + 1) if os.path.exists(jpeg(sid, e, p)) and pdf_doc(sid, e) is None})
    with ThreadPoolExecutor(4) as ex: list(ex.map(lambda x: ocr_tsv(jpeg(sid, *x)), todo))   # OCR 캐시 미리(병렬)
    jp = os.path.join(TOOLS, sid.lower(), 'jb_crops.json')
    old = json.load(open(jp, encoding='utf-8')) if os.path.exists(jp) else {}
    new, log = {}, []
    for q in Q:
        if ids and q['id'] not in ids:
            if q['id'] in old: new[q['id']] = old[q['id']]
            continue
        o = old.get(q['id'], {})
        if o.get('fix'): new[q['id']] = o; log.append((q['id'], 'fix(그대로)', o)); continue
        r = figs_for(sid, q['ed'], q['pg'], q['pg2'], q['text'])
        if r is None: log.append((q['id'], '⚠ 원문 위치 못 찾음', {})); r = []
        ent = {'q': [], 'a': []}
        for kind, ed, p, b, warn in r:
            d = {'ed': ed, 'pg': p, 'box': b}
            if warn: d['warn'] = warn
            ent[kind].append(d)
        if not ent['q']:   # 본 판에 문제 그림이 없으면 같은 문제의 다른 판본에서(문제 쪽 그림만)
            for ot in q.get('other', []):
                r2 = figs_for(sid, ot['ed'], ot['pg'], ot['pg2'], ot['text']) or []
                qq = [{'ed': ed, 'pg': p, 'box': b, 'via': '다른 판본', **({'warn': w} if w else {})} for kind, ed, p, b, w in r2 if kind == 'q']
                if qq: ent['q'] = qq; break
        if ent['q'] and ent['a']:   # 다른 판본에서 가져온 문제 그림과 같은 그림이 답 쪽에도 있으면 한 번만(문제 쪽)
            ent['a'] = [d for d in ent['a'] if not any(same_img(sid, d, x) for x in ent['q'])]
        for kind in ('q', 'a'):
            if any(CR.get(q['id'], {}).values()): ent[kind] = []   # assemble 기존 조각(CROPS)이 있는 문항은 자동 상자를 만들지 않음 — 기존 것 우선(종류가 달라도 같은 그림일 수 있음 · ESTH Q23)
            fx = [d for d in o.get(kind, []) if d.get('fix')]
            ent[kind] = fx + [d for d in ent[kind] if not any(f['ed'] == d['ed'] and f['pg'] == d['pg'] and iou(f['box'], d['box']) > 0.2 for f in fx)]
        for k in ('nofig', 'note'):
            if k in o: ent[k] = o[k]
        if ent['q'] or ent['a'] or 'nofig' in ent: new[q['id']] = ent
    for k, v in old.items():   # 지금 문항 목록에 없는 id의 검수 결정(fix)도 지우지 않음(문항 id가 잠시 빠진 빌드에서도 결정 보존)
        if k not in new and v.get('fix'): new[k] = v
    order = {q['id']: i for i, q in enumerate(Q)}
    new = {k: new[k] for k in sorted(new, key=lambda k: order.get(k, 1e9))}
    if not dry:
        with open(jp, 'w', encoding='utf-8') as f:
            f.write('{\n' + ',\n'.join(f' {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}' for k, v in new.items()) + '\n}\n')
    nq = sum(len(v.get('q', [])) for v in new.values()); na = sum(len(v.get('a', [])) for v in new.values())
    print(f'{sid}: 문항 {len(new)} · 조각 q {nq} · a {na}' + ('' if dry else f' → {os.path.relpath(jp, J.ROOT)}'))
    for x in log: print('  ', x[0], x[1])
    if dump: dump_review(sid, Q, new); audit(sid, Q, new)
    return new
def audit(sid, Q, new):
    """검수 도움: 본 판 문항이 있는 쪽에서 찾은 그림 중 어느 조각에도 안 쓰인 것(놓친 그림·표시 안 하는 블록의 그림)"""
    used = [(d['ed'], d['pg'], d['box']) for v in new.values() for k in ('q', 'a') for d in v.get(k, [])]
    pages = sorted({(q['ed'], p) for q in Q for p in range(q['pg'], (q['pg2'] or q['pg']) + 1) if os.path.exists(jpeg(sid, q['ed'], p))})
    out = []
    for ed, pg in pages:
        P = page(sid, ed, pg)
        for f in P.figs:
            if any(e == ed and p == pg and iou(b, f['box']) > 0.2 for e, p, b in used): continue
            ti = P.pos(f['box']); prev = P.txt[ti][:40] if 0 <= ti < len(P.txt) else '(앞 쪽)'
            out.append(f'{ed}-{pg} {f["box"]} 앞 줄: {prev}')
    print('  안 쓰인 그림', len(out)); [print('    ', x) for x in out]
def dump_review(sid, Q, new):
    d = os.path.join(OUT, sid); os.makedirs(os.path.join(d, 'pages'), exist_ok=True)
    for dd in (d, os.path.join(d, 'pages')):
        for f in os.listdir(dd):
            if f.endswith('.jpg'): os.remove(os.path.join(dd, f))
    marks = {}
    for qid, v in new.items():
        for kind in ('q', 'a'):
            for i, b in enumerate(v.get(kind, []), 1):
                p = jpeg(sid, b['ed'], b['pg'])
                if not os.path.exists(p): continue
                Image.open(p).convert('RGB').crop(tuple(b['box'])).save(os.path.join(d, f'{qid}_{kind}{i}.jpg'), quality=85)
                marks.setdefault((b['ed'], b['pg']), []).append((qid, kind, i, b['box']))
    for (ed, pg), ms in marks.items():
        im = Image.open(jpeg(sid, ed, pg)).convert('RGB'); dr = ImageDraw.Draw(im)
        for qid, kind, i, b in ms:
            col = (0, 90, 255) if kind == 'q' else (230, 0, 0)
            dr.rectangle(b, outline=col, width=3); dr.rectangle([b[0], b[1], b[0] + 70, b[1] + 16], fill=col); dr.text((b[0] + 3, b[1] + 2), f'{qid} {kind}{i}', fill=(255, 255, 255))
        im.save(os.path.join(d, 'pages', f'{ed}-{pg}.jpg'), quality=70)
    print('  검수용 →', os.path.relpath(d, J.ROOT))
def debug_page(sid, ed, pg):
    P = page(sid, ed, int(pg)); im = P.im.copy(); dr = ImageDraw.Draw(im)
    for l in P.lines: dr.rectangle([l['x0'], l['y0'], l['x1'], l['y1']], outline=(0, 160, 0) if l['ti'] is not None else (255, 150, 0))
    for f in P.figs: dr.rectangle(f['box'], outline=(230, 0, 0), width=3)
    if P.two: dr.line([P.gut, 0, P.gut, P.H], fill=(200, 200, 255))
    p = os.path.join(OUT, f'page_{sid}_{ed}-{pg}.jpg'); os.makedirs(OUT, exist_ok=True); im.save(p, quality=75)
    print(p, 'two' if P.two else 'one', 'gut', int(P.gut), 'figs', [f['box'] for f in P.figs], 'body', len(P.body), '/', len(P.lines), 'txt', len(P.txt))
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('sids', nargs='*'); ap.add_argument('--ids', default=''); ap.add_argument('--dump', action='store_true')
    ap.add_argument('--dry', action='store_true'); ap.add_argument('--page', nargs=3)
    a = ap.parse_args()
    if a.page: debug_page(*a.page); sys.exit(0)
    ids = set(x for x in a.ids.split(',') if x) or None
    for s in (a.sids or list(SUBJ)): run(s.upper(), ids, a.dump, a.dry)
