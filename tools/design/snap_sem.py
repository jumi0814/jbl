"""W7 넓힘 ⓐ·ⓔ — 같은 뜻인데 조금씩 다른 의미 색 글자를 대표 값 하나로(빨강·금·초록·보라·파랑) + v2 남색(#2F5470 계열) 남은 글자·선 → 중립.
  snap_sem.py <파일…> [--dry] [--tests]   (shell.html = <style>·<script>만 · num.js = 전체 · 어두운 테마 묶음·--bk-*·형광펜 색은 건드리지 않음)"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAP = {}
def m(dst, *src):
    for s in src: MAP['#' + s] = '#' + dst
m('B3261E', 'B42318', 'A3231B', 'A3261E', '9B2C2C', '9A2019')                 # 빨강 글자(핵심어·틀림) = --red
m('7A5300', '7A5A00', '7C5E0E', '8A5A00')                                     # 금색 글자 = --exam-fg
m('5C3D00', '5A4300', '5C4200', '5C4300', '5A3B00', '5E3F00', '3F2E00')       # 진한 금색 글자(2회↑ 칩)
m('1E6B3F', '11643A', '1C5B33', '17663A', '1F6B43', '2E6B44')                 # 초록 글자(맞음·✓ 정답·NEW 26 알약 글자) — 대표 값 = ✓ 정답 색(ux2_fixB가 봄)
m('5B4B9A', '5B3FB0', '4B3A8C')                                               # 보라 글자 = --e26
m('1D4E9E', '1E4E8C')                                                         # 파랑 글자 = --pred-fg
m('393734', '3B5F78', '2F4F6E', '2C4A6E', '0E5A7A', '24466B')                 # v2 남색·청록 글자 남은 것 → 먹 2단
m('2A2723', '2B3440')                                                         # 표 메모 칸의 남빛 먹 → 본문 먹
m('1E6B3F', '1E6B3E')
m('F1EEEA', 'EDF2F6'); m('F4F1ED', 'F0F5FA'); m('D8D4CE', 'B9CAD8', 'C9D9E8')     # v2 옅은 남색 면·선(넘버링 fallback) → 중립
m('CCC8C1', '5A7D95')                                                         # v2 남색 선 → 중립 선
HEX = re.compile(r'(?<![%&\w])#([0-9A-Fa-f]{6})\b')
def transform(t, log):
    prot = []
    for mm in re.finditer(r'--bk-[a-z]+:#[0-9A-Fa-f]{3,6}', t): prot.append(mm.span())
    for mm in re.finditer(r':root\[data-theme="dark"\][^{]*\{[^}]*\}', t): prot.append(mm.span())
    for mm in re.finditer(r'\.rk[a-z-]*[^{}]*\{[^}]*\}', t): prot.append(mm.span())   # 형광펜·빈칸 표시 규칙
    def f(mm):
        if any(a <= mm.start() < b for a, b in prot): return mm.group(0)
        n = MAP.get(mm.group(0).upper())
        if not n: return mm.group(0)
        log.append((mm.group(0).upper(), n)); return n
    return HEX.sub(f, t)
if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; dry = '--dry' in sys.argv; allmap = {}
    for p in args:
        s = open(p, encoding='utf-8').read(); log = []
        if p.endswith('.html'): out = re.sub(r'(<style>.*?</style>|<script>.*?</script>)', lambda mm: transform(mm.group(0), log), s, flags=re.S)
        else: out = transform(s, log)
        u = {}
        for a, b in log: u[a] = b; allmap[a] = b
        print(f'{p}: 바꾼 곳 {len(log)} · 서로 다른 색 {len(u)} → {len(set(u.values()))}')
        if not dry and out != s: open(p, 'w', encoding='utf-8').write(out)
    if '--tests' in sys.argv:
        import subprocess
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from oklch import hex2rgb
        for a, b in sorted(allmap.items()):
            r, g, bl = hex2rgb(a)
            for pat in [a[1:], f'{r}, ?{g}, ?{bl}\\b']:
                o = subprocess.run(['grep', '-rlEi', pat, ROOT + '/tools/tests', ROOT + '/tools/tests4', ROOT + '/tools/audit_design.py', ROOT + '/tools/verify.py'], capture_output=True, text=True).stdout.split()
                o = [x for x in o if not x.endswith('.pyc')]
                if o: print(f'   PIN {a} → {b} ({pat}):', ' '.join(os.path.basename(x) for x in o)[:200])
