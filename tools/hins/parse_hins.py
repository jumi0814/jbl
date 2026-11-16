import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""HINS 의료전달체계와 건강보험(4Q) JB(23·24·25판) → 문항 블록 parse(ed, n) → [{'ed','sec','prof','num','pg','pg2','lines'}]
판 구조(2026-11-16 전 쪽 확인 — 보고 work/HINS/jb/R_JB_HINS.md 1절):
  - 연도 칸형 · 판마다 최근 3해 칸 — 25판 '2024-4Q'·'2023-4Q'·'2022-4Q' / 24판 '[23년도 문제]'·'[22년도 문제]'·'[21 년도 문제]' / 23판 '[22년도 문제]'·'[ 21년도 문제 ]'·'[ 20년도 문제 ]'
    → 칸 이름은 모두 'YYYY-4Q'(+ 교수 머리가 있으면 ' · <교수>')
  - 칸 안 교수 머리 '[송영하 교수님]'·'[한동헌 교수님]'·'[외래교수님]'·'[외래 교수님]'(25판 2023·2022 칸 · 24판 2023·2022 칸 · 23판 2022 칸) — 교수마다 번호가 1부터
    교수 머리가 없는 칸(25판 2024 · 24판·23판 2021 · 23판 2020)은 번호가 칸 끝까지 이어짐
  - 쪽 첫 줄 = 쪽 번호(23판은 71~112 — 큰 책의 일부) · '※본 파일의 무단인쇄…※' 줄 뺌
  - 23판 3쪽: 쪽 위 표(멘트 끝 + 2023 수업 표)가 pdfium 글에서는 2022 칸 1번 해설 뒤로 옴 → 그 쪽 '제작 시점에서는'부터 쪽 끝까지 = 멘트(문항 아님 · MENT)
  - 25판 2024 칸 '11.'이 두 번(마약 처방전 보관 / 마약취급업자) → 두 번째 = num '11(두번째)'(ESTH DUP 꼴)
  - 25판 2024 칸 4번 보기 '1. 승무원 소지품 … 5. 마약소지여부'의 '5.' = 보기(NOTQ — 진짜 5번은 바로 뒤 '5. 검역전염병에 관하여')
  - 해설·보기 안의 '1. …' 번호 줄은 번호가 이어지지 않으면 문항 아님(바로 앞 문항 번호 + 1만 새 문항 · RULES 0-1)
  - 칸 머리 바로 아래 '총 주관식 3(…), 객관식 48문제 출제'(23판·24판 2022 칸) = 칸 멘트(문항 아님)"""
import re, json
BASE = J.JBX
NPAGES = {'25': 32, '24': 34, '23': 42}
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
CUT = {('23', 3): '제작 시점에서는'}   # 그 쪽에서 이 글로 시작하는 줄부터 쪽 끝까지 = 멘트(쪽 위 표가 글 순서에서 뒤로 온 것)
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        ls = rd(f'{BASE}HINS_20{ed}/{i}.txt').split('\n'); first = True
        for l in ls:
            if '무단인쇄' in l: continue
            if (ed, i) in CUT and l.strip().startswith(CUT[(ed, i)]): break
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
SEC25 = re.compile(r'^\s*(20\d\d)\s*-\s*4Q\s*$')
SEC23 = re.compile(r'^\s*\[\s*(\d\d)\s*년도\s*문제\s*\]\s*$')
PROF = re.compile(r'^\s*\[\s*(송영하|한동헌|외래)\s*교수님\s*\]\s*$')
QRE = re.compile(r'^\s*(\d{1,2})\s*[.．](?!\d)\s*(\S.*)?$')
DUP = {('25', '2024-4Q', 11): '11(두번째)'}
NOTQ = {('25', '2024-4Q'): {'5. 마약소지여부'}}   # 보기 줄이 '번호. '꼴이고 번호가 문항 번호 + 1인 것(25판 2024 칸 4번 보기 5 — 진짜 5번은 바로 뒤 '5. 검역전염병에 관하여')
def parse(ed, n=None):
    L = load(ed, n or NPAGES[ed]); blocks = []; cur = None; sec = '머리말'; year = None; last = 0; seen = set()
    for pg, l in L:
        s = l.strip()
        m = SEC25.match(s) or SEC23.match(s)
        if m:
            y = m.group(1); year = (y if len(y) == 4 else '20' + y) + '-4Q'; sec = year; last = 0; cur = None; continue
        mp = PROF.match(s)
        if mp and year:
            sec = f'{year} · {mp.group(1)}'; last = 0; cur = None; continue
        if sec == '머리말': continue
        mq = QRE.match(s)
        if mq and s not in NOTQ.get((ed, sec), ()):
            a = int(mq.group(1)); num = None
            if a == last + 1: num = str(a)
            elif a == last and (ed, sec, a) in DUP and (ed, sec, a) not in seen: num = DUP[(ed, sec, a)]; seen.add((ed, sec, a))
            if num:
                prof = sec.split(' · ')[1] if ' · ' in sec else ''
                cur = {'ed': ed, 'sec': sec, 'prof': prof, 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur)
                last = a; continue
        if cur is not None: cur['lines'].append(l); cur['pg2'] = pg
    for x in blocks:   # 끝의 빈 줄 정리
        while x['lines'] and not x['lines'][-1].strip(): x['lines'].pop()
    return blocks
if __name__ == '__main__':
    allb = {}
    for ed in ('25', '24', '23'):
        b = parse(ed); allb[ed] = b
        secs = {}
        for x in b: secs.setdefault(x['sec'], []).append(x['num'])
        print(f'=== {ed}판: {len(b)} blocks · ' + ' · '.join(f"{k} {len(v)}" for k, v in secs.items()))
        for k, v in secs.items(): print(f'   {k}: {" ".join(v)}')
        if '-v' in _sys.argv:
            for x in b:
                txt = '\n'.join(x['lines']); stem = ' '.join(x['lines'][:2])[:62]
                print(f" {x['sec']:14}|{str(x['num']):>9}|p{x['pg']:<2}-{x['pg2']:<2}|{len(txt):5}|{'A' if '답' in txt else '-'}| {stem}")
    json.dump(allb, open(J.work('HINS', 'jb_blocks.json'), 'w'), ensure_ascii=False)
