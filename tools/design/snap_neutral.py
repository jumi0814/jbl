"""W7 넓힘 ⓐ — 중립 회색을 사다리 16단으로 모음(같은 색상·비슷한 밝기의 '비슷한데 다른 회색' → 토큰 값).
  snap_neutral.py <파일…> [--dry] [--tests]   (shell.html = <style>·<script>만 · num.js = 전체)
건드리지 않는 것: 흰색·검정 · 채도 있는 색(의미 색·형광펜·과목 색) · 빈칸 색 변수(--bk-*) · 어두운 테마 묶음(:root[data-theme="dark"] …) · data URI(%23…) · rgb()/rgba()"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oklch import hex2rgb, rgb2oklch
LADDER = ['#1A1815', '#2A2723', '#393734', '#57534D', '#706C65', '#89857F', '#B5B1AA', '#CCC8C1', '#D8D4CE', '#E0DCD7', '#E9E5DF', '#F1EEEA', '#F4F1ED', '#F7F4EF', '#FAF8F4', '#FDFBF7']
LL = [rgb2oklch(*hex2rgb(h))[0] for h in LADDER]
# 경계(밝기) — 글자 쪽(어두운 단)은 더 진한 단으로 기울임(명암 유지), 밝은 단은 가운데
CUT = [0.2425, 0.3065, 0.4016, 0.497, 0.600, 0.700, 0.798, 0.850, 0.8835, 0.9095, 0.9365, 0.9545, 0.9635, 0.9735, 0.9845]
def snap(h):
    h = h.upper()
    if len(h) == 4: h = '#' + ''.join(c * 2 for c in h[1:])
    if h in ('#FFFFFF', '#000000', '#E6E2DC', '#6E6A64'): return None   # 빈칸 중립색(바탕·밑줄 — 사용자 표시 색 · ux_hlpre)
    L, C, H = rgb2oklch(*hex2rgb(h))
    if not (C < 0.004 or (C < (0.0125 if L > 0.9 else 0.02) and 40 <= H <= 110)): return None   # 밝은 쪽은 0.0125 — 복숭아·크림 '의미 바탕'(26 빠짐 #FCEDE6 · 기출 줄 #FDF1E6 · #FBF6E8)은 회색이 아님(첫 판에서 이 셋이 잘못 모였다가 되돌림 — ux_u27이 잡음)
    if L > 0.9945: return None
    i = sum(1 for c in CUT if L >= c)
    return LADDER[i] if LADDER[i] != h else None
HEX = re.compile(r'(?<![%&\w])#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b')
def transform(t, log):
    # 보호 구간: --bk-*: 값 · 어두운 테마 규칙
    prot = []
    for m in re.finditer(r'--bk-[a-z]+:#[0-9A-Fa-f]{3,6}', t): prot.append(m.span())
    for m in re.finditer(r':root\[data-theme="dark"\][^{]*\{[^}]*\}', t): prot.append(m.span())
    def f(m):
        if any(a <= m.start() < b for a, b in prot): return m.group(0)
        n = snap(m.group(0))
        if not n: return m.group(0)
        log.append((m.group(0).upper(), n)); return n
    return HEX.sub(f, t)
if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; dry = '--dry' in sys.argv; allmap = {}
    for p in args:
        s = open(p, encoding='utf-8').read(); log = []
        if p.endswith('.html'): out = re.sub(r'(<style>.*?</style>|<script>.*?</script>)', lambda m: transform(m.group(0), log), s, flags=re.S)
        else: out = transform(s, log)
        u = {}
        for a, b in log: u[a] = b; allmap[a] = b
        print(f'{p}: 바꾼 곳 {len(log)} · 서로 다른 색 {len(u)} → {len(set(u.values()))}')
        if not dry and out != s: open(p, 'w', encoding='utf-8').write(out)
    if '--map' in sys.argv:
        for a, b in sorted(allmap.items(), key=lambda x: rgb2oklch(*hex2rgb(x[0]))[0]):
            print(f'   {a} L{rgb2oklch(*hex2rgb(a))[0]:.3f} → {b} L{rgb2oklch(*hex2rgb(b))[0]:.3f}')
    if '--tests' in sys.argv:   # 테스트·도구가 옛 값을 박아 둔 곳
        import subprocess
        for a, b in sorted(allmap.items()):
            r, g, bl = hex2rgb(a); pats = [a[1:], f'{r}, ?{g}, ?{bl}\\b']
            for pat in pats:
                o = subprocess.run(['grep', '-rlEi', pat, ROOT + '/tools/tests', ROOT + '/tools/tests4', ROOT + '/tools/audit_design.py', ROOT + '/tools/verify.py'], capture_output=True, text=True).stdout.split()
                o = [x for x in o if not x.endswith('.pyc')]
                if o: print(f'   PIN {a} → {b} ({pat}):', ' '.join(os.path.basename(x) for x in o)[:200])
