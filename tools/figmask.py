"""그림빵(그림 빈칸) 상자 도우미 — 강의 쪽 이미지의 라벨 글자 상자를 OCR(tesseract)로 찾아 가릴 상자(m=)를 만든다.
사용:
  .venv/bin/python tools/figmask.py <SID> <KEY> <쪽>                 → 글줄 목록(번호·글자·상자 %) + 미리보기 work/_tmp/figmask/<SID>_<KEY>_<쪽>_ocr.png
  .venv/bin/python tools/figmask.py <SID> <KEY> <쪽> --pick 3,5,7+8   → 고른 글줄(+ = 한 상자로 합침)의 m= 문자열 + 가린 미리보기 _mask.png
  .venv/bin/python tools/figmask.py <SID> <KEY> <쪽> --mask "x0,y0,x1,y1;…" → 손으로 준 상자 미리보기(_mask.png)
상자 = 쪽 이미지 너비·높이 대비 %(소수 1자리) · 순서 = 화면 번호 ①②③. pred.txt 그림빵 문법은 guide/handoff/PRED26_BRIEF.md.
OCR이 못 잡은 라벨은 미리보기를 보고 --mask로 직접(그림 속 글자를 추측해 답으로 쓰지 않음 — 답은 쪽 이미지에서 읽히는 글자 그대로)."""
import os, sys, re, subprocess, importlib.util, argparse
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J

def subject(sid):
    p = os.path.join(J.TOOLS, sid.lower(), 'subject.py')
    sp = importlib.util.spec_from_file_location('subject_' + sid, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def page_img(sid, key, pg):
    S = subject(sid); f = S.lec_img_path(key, pg)   # 과목마다 폴더 규칙이 다름(OMS1은 끝에 i)
    if not f: raise SystemExit(f'{key}: 쪽 이미지 폴더 없음')
    if not os.path.exists(f): raise SystemExit(f'없음: {f}')
    return f
def ocr_lines(f, z=3):
    """작은 라벨도 잡게 z배 키워 흑백으로 OCR(psm 11 = 흩어진 글자) — 상자는 원래 크기로 되돌림"""
    im = Image.open(f).convert('L'); im = im.resize((im.width * z, im.height * z), Image.LANCZOS)
    tmp = os.path.join(J.WORK, '_tmp', 'figmask', f'_ocr_in_{os.getpid()}.png')   # 담당 여럿이 동시에 돌려도 섞이지 않게; os.makedirs(os.path.dirname(tmp), exist_ok=True); im.save(tmp)
    out = subprocess.run(['tesseract', tmp, '-', '-l', 'eng+kor', '--psm', '11', 'tsv'], capture_output=True, text=True).stdout
    try: os.remove(tmp)
    except OSError: pass
    rows = [r.split('\t') for r in out.splitlines()[1:]]
    for r in rows:
        if len(r) >= 12: r[6:10] = [str(int(v) // z) for v in r[6:10]]
    L = {}
    for r in rows:
        if len(r) < 12 or not r[11].strip(): continue
        try: conf = float(r[10])
        except ValueError: continue
        if conf < 30: continue
        k = (r[2], r[3], r[4]); x, y, w, h = map(int, r[6:10])
        g = L.setdefault(k, {'t': [], 'b': [x, y, x + w, y + h], 'c': []})
        g['t'].append(r[11]); g['c'].append(conf)
        b = g['b']; g['b'] = [min(b[0], x), min(b[1], y), max(b[2], x + w), max(b[3], y + h)]
    lines = sorted(L.values(), key=lambda g: (g['b'][1], g['b'][0]))
    return [{'t': ' '.join(g['t']), 'b': g['b'], 'c': round(sum(g['c']) / len(g['c']))} for g in lines]
def pct(b, W, H, pad=0.4):
    x0, y0, x1, y1 = b
    return [round(max(0, x0 / W * 100 - pad), 1), round(max(0, y0 / H * 100 - pad), 1), round(min(100, x1 / W * 100 + pad), 1), round(min(100, y1 / H * 100 + pad), 1)]
def draw(f, boxes, out, label=True, fill=None):
    im = Image.open(f).convert('RGB'); W, H = im.size; d = ImageDraw.Draw(im)
    try: font = ImageFont.load_default(size=16)
    except TypeError: font = ImageFont.load_default()
    for i, b in enumerate(boxes, 1):
        r = [b[0] * W / 100, b[1] * H / 100, b[2] * W / 100, b[3] * H / 100]
        d.rectangle(r, outline='#D0021B', width=2, fill=fill)
        if label: d.text((r[0] + 2, r[1] + 1), str(i), fill='#D0021B' if not fill else '#FFFFFF', font=font)
    os.makedirs(os.path.dirname(out), exist_ok=True); im.save(out); return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('sid'); ap.add_argument('key'); ap.add_argument('pg', type=int)
    ap.add_argument('--pick'); ap.add_argument('--mask'); a = ap.parse_args()
    sid = a.sid.upper(); f = page_img(sid, a.key, a.pg); W, H = Image.open(f).size
    base = os.path.join(J.WORK, '_tmp', 'figmask', f'{sid}_{a.key}_{a.pg}')
    if a.mask:
        boxes = [[float(v) for v in m.split(',')] for m in a.mask.split(';') if m.strip()]
        print('m=' + ';'.join(','.join(str(v) for v in b) for b in boxes)); print(draw(f, boxes, base + '_mask.png', fill='#F5E6B8')); return
    L = ocr_lines(f)
    if a.pick:
        boxes = []
        for grp in a.pick.split(','):
            idx = [int(x) for x in grp.split('+')]; bs = [L[i - 1]['b'] for i in idx]
            boxes.append(pct([min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)], W, H))
            print(f"{len(boxes)}. {' / '.join(L[i - 1]['t'] for i in idx)}")
        print('m=' + ';'.join(','.join(str(v) for v in b) for b in boxes)); print(draw(f, boxes, base + '_mask.png', fill='#F5E6B8')); return
    for i, g in enumerate(L, 1): print(f"{i:3}. [{g['c']:3}] {g['t'][:60]}  ({','.join(str(v) for v in pct(g['b'], W, H))})")
    print(draw(f, [pct(g['b'], W, H) for g in L], base + '_ocr.png'))
if __name__ == '__main__': main()
