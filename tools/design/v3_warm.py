"""디자인 v3.1 따뜻함 더하기(10-24 사용자 '지금은 너무 갑자기 냉한, 무채색 느낌인데 조금의 따듯함은 첨가').
v3의 차가운 중립색(v3_palette가 바꾼 색 + v3 묶음의 회색 토큰)만 골라 같은 밝기(L)의 **은은하게 따뜻한 회색**(색상 80°,
옛 베이지 채도의 약 58%)으로 바꾼다 — 명암비·레이아웃 그대로. 의미 색(빨강·초록·보라·금색·예상 파랑·형광펜·과목 색)은 그대로.
  .venv/bin/python tools/design/v3_warm.py <옛 shell 사본> <옛 num.js 사본> [--dry]   (한 번 — 대상: tools/cons/shell.html · tools/num/num.js · tools/cons/build4.py 매니페스트)"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oklch import hex2rgb, rgb2oklch, oklch2rgb, rgb2hex
import v3_palette as VP

def warm_chroma(L):
    """옛 종이 베이지(OKLCH 채도)의 약 58% — 차갑지 않되 누렇지 않게"""
    if L >= 0.97: return 0.0052
    if L >= 0.93: return 0.0070
    if L >= 0.85: return 0.0087
    if L >= 0.35: return 0.0110
    return 0.0070

def warm(rgb):
    L, C, h = rgb2oklch(*rgb)
    return oklch2rgb(L, warm_chroma(L), 80)

HEX = re.compile(r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b')
RGBA = re.compile(r'rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(,\s*[\d.]+\s*)?\)')
PROTECT = {'#EEF4FD', '#C4D6F2', '#1D4E9E', '#FFFFFF', '#000000', '#FFF', '#000'}   # 예상 파랑 토큰·흰·검정

def targets(old_files, cur_shell):
    """바꿀 색 = 옛 따뜻한 색을 v3_palette가 바꾼 결과(차가운 회색) ∪ v3 묶음 안의 차가운 저채도 회색"""
    T = set()
    for p in old_files:
        s = open(p, encoding='utf-8').read()
        for h in set(HEX.findall(s)):
            o = hex2rgb(h); r = VP.remap(o)
            if r and r != o: T.add(r)
        for m in RGBA.finditer(s):
            o = tuple(int(m.group(i)) for i in (1, 2, 3)); r = VP.remap(o)
            if r and r != o: T.add(r)
    k = cur_shell.find('/* ===== 10-24 디자인 v3')
    blk = cur_shell[k:cur_shell.find('</style>', k)]
    for h in set('#' + x for x in HEX.findall(blk)):
        if h.upper() in PROTECT: continue
        o = hex2rgb(h); L, C, hh = rgb2oklch(*o)
        if C < 0.003 or (C < 0.035 and 200 <= hh <= 290): T.add(o)
    for m in RGBA.finditer(blk):
        o = tuple(int(m.group(i)) for i in (1, 2, 3)); L, C, hh = rgb2oklch(*o)
        if o not in ((255, 255, 255), (0, 0, 0)) and (C < 0.003 or (C < 0.035 and 200 <= hh <= 290)): T.add(o)
    return T - {(255, 255, 255), (0, 0, 0)}

def apply(t, T, log):
    def fh(m):
        o = hex2rgb(m.group(0))
        if o not in T or m.group(0).upper() in PROTECT: return m.group(0)
        n = rgb2hex(warm(o)); log.append((m.group(0), n)); return n
    def fr(m):
        o = tuple(int(m.group(i)) for i in (1, 2, 3))
        if o not in T: return m.group(0)
        n = warm(o); a = (m.group(4) or '').replace(' ', ''); log.append((m.group(0), n))
        return f'rgba({n[0]},{n[1]},{n[2]}{a})' if a else f'rgb({n[0]},{n[1]},{n[2]})'
    def fu(m):
        o = hex2rgb(m.group(1))
        if o not in T: return m.group(0)
        return '%23' + rgb2hex(warm(o))[1:]
    t = HEX.sub(fh, t); t = re.sub(r'%23([0-9A-Fa-f]{6})\b', fu, t)
    return RGBA.sub(fr, t)

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]; dry = '--dry' in sys.argv
    J = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    shell = os.path.join(J, 'tools', 'cons', 'shell.html'); num = os.path.join(J, 'tools', 'num', 'num.js')
    cur = open(shell, encoding='utf-8').read()
    T = targets(a, cur); print('바꿀 차가운 회색', len(T))
    for p in (shell, num):
        s = open(p, encoding='utf-8').read(); log = []
        if p.endswith('.html'):
            out = re.sub(r'(<style>.*?</style>|<script>.*?</script>)', lambda m: apply(m.group(0), T, log), s, flags=re.S)
        else:
            out = apply(s, T, log)
        u = {}
        for x, y in log: u.setdefault(x.upper(), y)
        print(f'{p}: 바꾼 곳 {len(log)} · 서로 다른 색 {len(u)}'); [print('   ', x, '→', y) for x, y in list(u.items())[:14]]
        if not dry and out != s: open(p, 'w', encoding='utf-8').write(out)
