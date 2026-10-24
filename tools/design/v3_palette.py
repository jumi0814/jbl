"""디자인 v3 색 바꾸기(10-24 사용자 '밤티 · old fashioned — 색감·탭·배치 전면 개편, 내용은 그대로').
따뜻한 저채도 색(종이 베이지·갈색 글자·크림 바탕)을 같은 밝기의 차가운 회색으로 바꾼다 — 명암비는 그대로 유지(밝기 L 보존).
의미 색(빨강 핵심 · 초록 NEW 26 · 보라 26 강조 · 금색 ⭐ 기출 · 파랑 예상 · 형광펜·과목 색)은 채도가 높아 건드리지 않음.
  .venv/bin/python tools/design/v3_palette.py <파일…> [--dry]   (한 번만 — shell.html은 '10-24 디자인 v3' 묶음을 건너뜀)"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oklch import hex2rgb, rgb2oklch, oklch2rgb, rgb2hex

def cool_chroma(L):
    if L >= 0.95: return 0.004
    if L >= 0.85: return 0.004 + (0.95 - L) / 0.10 * 0.008
    if L >= 0.55: return 0.012 + (0.85 - L) / 0.30 * 0.014
    return max(0.016, 0.026 - (0.55 - L) / 0.35 * 0.010)

def is_warm_neutral(L, C, h):
    if C < 0.003: return True                       # 순수 회색(채도 0)도 같은 차가운 회색 줄로
    lim = 0.018 if L > 0.94 else 0.030              # 아주 밝은 색은 복숭아·크림 바탕(의미 바탕)과 종이 베이지를 가름
    return C < lim and 45 <= h <= 110

def remap(rgb):
    if rgb in ((255, 255, 255), (0, 0, 0)): return None
    L, C, h = rgb2oklch(*rgb)
    if not is_warm_neutral(L, C, h): return None
    if L >= 0.985: return (255, 255, 255)          # 크림 흰 바탕 → 흰색
    return oklch2rgb(L, cool_chroma(L), 255)

HEX = re.compile(r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b')
RGB = re.compile(r'rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(,\s*[\d.]+\s*)?\)')

def transform(t, log):
    def fh(m):
        h = m.group(0)
        # '#1a', '#fff' 같은 3자 — 흰·검정·회색만 (따뜻한 3자 색 거의 없음)
        o = hex2rgb(h); nr = remap(o)
        if nr is None or nr == o: return h
        out = rgb2hex(nr); log.append((h, out)); return out
    def fr(m):
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        nr = remap((r, g, b))
        if nr is None: return m.group(0)
        a = m.group(4) or ''
        out = (f'rgba({nr[0]},{nr[1]},{nr[2]}{a.replace(" ", "")})' if a else f'rgb({nr[0]},{nr[1]},{nr[2]})')
        if (r, g, b) != nr: log.append((m.group(0), out))
        return out if (r, g, b) != nr else m.group(0)
    t = HEX.sub(fh, t)
    def fu(m):   # data: URI 안의 %23RRGGBB(검색 돋보기 선 색 등 — 10-24 검토 8)
        o = hex2rgb(m.group(1)); nr = remap(o)
        if nr is None or nr == o: return m.group(0)
        out = '%23' + rgb2hex(nr)[1:]; log.append((m.group(0), out)); return out
    t = re.sub(r'%23([0-9A-Fa-f]{6})\b', fu, t)
    return RGB.sub(fr, t)

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; dry = '--dry' in sys.argv
    if '--check' in sys.argv:   # 검사만: 파일 전체(v3 묶음 포함)의 따뜻한 저채도 색 — 0이어야 함(QA 70 · full_check)
        bad = 0
        for p in args:
            s = open(p, encoding='utf-8').read(); log = []
            seg = ''.join(re.findall(r'<style>.*?</style>', s, flags=re.S)) if p.endswith('.html') else s
            u = set()   # 순수 회색(채도 ~0)·차가운 회색은 v3 색 — 따뜻한 쪽(색상 45~110°)으로 기운 저채도만 셈
            for h in re.findall(r'#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b', seg):
                L, C, H = rgb2oklch(*hex2rgb(h))
                # 10-24 v3.1: 은은한 따뜻함(v3_warm.warm_chroma — 옛 베이지의 약 58%)까지는 허용 · 그보다 누런 옛 베이지·갈색만 셈
                from v3_warm import warm_chroma
                if 1.3 * warm_chroma(L) < C < (0.018 if L > 0.94 else 0.030) and 45 <= H <= 110: u.add(h.upper())
            u = sorted(u); bad += len(u)
            print(f'{p}: 따뜻한 색 {len(u)}', ' '.join(u[:10]))
        print('RESULT', 'PASS' if not bad else f'FAIL {bad}'); sys.exit(1 if bad else 0)
    for p in args:
        s = open(p, encoding='utf-8').read(); log = []
        # HTML이면 <style>…</style>와 <script>…</script>만(본문 글자는 손대지 않음) — js는 파일 전체
        if p.endswith('.html'):
            # '10-24 디자인 v3' 묶음부터 </style>까지는 이미 v3 색 — 건너뜀(다시 돌려도 v3 색이 바뀌지 않게)
            def fs(m):
                t = m.group(0); k = t.find('/* ===== 10-24 디자인 v3')
                return transform(t, log) if k < 0 else transform(t[:k], log) + t[k:]
            out = re.sub(r'(<style>.*?</style>|<script>.*?</script>)', fs, s, flags=re.S)
        else:
            out = transform(s, log)
        uniq = {}
        for a, b in log: uniq.setdefault(a.upper(), b)
        print(f'{p}: 바꾼 곳 {len(log)} · 서로 다른 색 {len(uniq)}')
        for a, b in list(uniq.items())[:12]: print('   ', a, '→', b)
        if not dry and out != s: open(p, 'w', encoding='utf-8').write(out)
