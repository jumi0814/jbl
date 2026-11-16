import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""ANAT4 임상두경부해부학(4Q) JB(23·24판) → 문항 블록 parse(ed, n) → [{'ed','sec','prof','num','pg','pg2','lines'}]
판 구조(2026-11-16 전 쪽 글·그림 확인 — 보고 work/ANAT4/jb/R_JB_ANAT4.md 1절):
  - 23판 = '2023 4Q JB'(쪽 머리 번호 45~70 — 큰 묶음의 일부 · 26쪽 = 빈 쪽) · 24판 = 파일 '2024_2025 4Q …' · 표지 '2025 4Q JB' · 멘트 '25년'(판 키 24는 jbx가 파일 이름 첫 연도로 붙임)
  - 1쪽 = 학습부 멘트 + 수업 표(문항 아님 · assemble MENT)
  - '[임상두경부해부학 4Q 문제 뱅크]' = 번호형 뱅크(23판 1~22 · 24판 1~23) — 연도 괄호·교수 칸·'답' 머리 없음(24판 7번 '답:'만)
  - '[2022년 기출문제]'(두 판)·'[2023년 기출문제]'(24판) = 그해 시험 문항 목록(뱅크 번호를 가리킴 — '뱅크 문제의 답은 중복되어 작성하지 않았습니다.')
  - 23판 24~25쪽 '명훈 교수님'(3Q Neck dissection — '2023 학습부) 2018 년도까지만 시험 출제 …') '[2018년 복원]' 1~3 · '[2017년 복원]' 1 — 답 머리 '답)'
  - 쪽 첫 줄 = 쪽 번호 · '※본 파일의 무단인쇄…※' 줄 뺌
  - 해설·표 안의 '1. …' 번호 줄은 번호가 이어지지 않으면 문항 아님(바로 앞 문항 번호 + 1만 새 문항 · RULES 0-1 — 5번 표 '1. 머리뼈 공간…'·7번 '1. Meningeal branch'·11번 '1. Body of Maxilla'·13·16번 표 칸 등)
  - 23판 11번 '11-1) Bony palate의 구성 뼈를 써라.'·'# 예전 족보에 있던 관련 자료' = 11번 블록 안(묻힌 하위 문항 — annot subq= 후보)
  - 24판 18쪽 맨 위 '23. 입꼬리를 위로 올릴 때 작용하는 근육들을 쓰시오.'(답 3줄 + 근육·기시·정지·작용 표) = 붙여 넣은 그림 — 글층(18.txt)에 없음 → IMGTXT(쪽 그림을 읽은 글 · 판독 확실 — 확대해 확인)를 그 쪽 글 맨 앞에"""
import re, json
BASE = J.JBX
NPAGES = {'24': 18, '23': 26}
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
# 글층에 없는 그림 글(쪽 그림에서 읽음 — 표는 pdfium이 표 칸을 읽는 차례처럼 한 칸 한 줄)
IMGTXT = {('24', 18): ['23. 입꼬리를 위로 올릴 때 작용하는 근육들을 쓰시오.',
                       'Levator anguli oris m.', 'Zygomaticus minor m.', 'Zygomaticus major m.',
                       '근육 기시 정지 작용',
                       'Levator anguli', 'oris m.', 'Maxilla의 canine fossa', 'Zygomaticus major m.의 안쪽에', '서 입꼬리 근처 위입술로 닿음', '입꼬리를 위로 올리고,', '안쪽으로 당김',
                       'Zygomaticus', 'minor m.', 'Zygomatic bone의 아래면', '입꼬리 안쪽의 위입술', '위입술을 위쪽으로 당기며,', '경멸하는 표정을 만듦.', '비순구를 만드는 주된 근육',
                       'Zygomaticus', 'major m.', 'Zygomatic bone의 바깥면', '입꼬리의 피부와 점막으로 닿고', '일부는 orbicularis oris m.,', 'levator anguli oris m. 및', 'depressor anguli oris m.과 섞임', '입꼬리를 뒤위쪽으로 당겨', '미소짓는 표정을 만듦']}
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        for l in IMGTXT.get((ed, i), []): lines.append((i, l))
        ls = rd(f'{BASE}ANAT4_20{ed}/{i}.txt').split('\n'); first = True
        for l in ls:
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
BANK = re.compile(r'^\s*\[\s*임상두경부해부학\s*4Q\s*문제\s*뱅크\s*\]\s*$')
YLIST = re.compile(r'^\s*\[\s*(20\d\d)\s*년\s*기출문제\s*\]\s*$')
MHHEAD = re.compile(r'^\s*명훈\s*교수님\s*$')
MHYEAR = re.compile(r'^\s*\[\s*(20\d\d)\s*년\s*복원\s*\]\s*$')
QRE = re.compile(r'^\s*(\d{1,2})\s*[.．](?!\d)\s*(\S.*)?$')
HEADNOTE = re.compile(r'^\s*뱅크\s*문제의\s*답은\s*중복되어\s*작성하지\s*않았습니다\.?\s*$')   # 목록 머리 멘트(문항 아님)
def parse(ed, n=None):
    L = load(ed, n or NPAGES[ed]); blocks = []; cur = None; sec = '머리말'; prof = ''; last = 0
    for pg, l in L:
        s = l.strip()
        if BANK.match(s): sec = '문제 뱅크'; prof = ''; last = 0; cur = None; continue
        m = YLIST.match(s)
        if m: sec = f'{m.group(1)}년 기출문제'; prof = ''; last = 0; cur = None; continue
        if MHHEAD.match(s): sec = '명훈 머리말'; prof = '명훈'; last = 0; cur = None; continue
        m = MHYEAR.match(s)
        if m and prof == '명훈': sec = f'{m.group(1)}년 복원 · 명훈'; last = 0; cur = None; continue
        if sec in ('머리말', '명훈 머리말'): continue
        if cur is None and HEADNOTE.match(s): continue
        mq = QRE.match(s)
        if mq and int(mq.group(1)) == last + 1:
            last += 1
            cur = {'ed': ed, 'sec': sec, 'prof': prof, 'num': str(last), 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur); continue
        if cur is not None: cur['lines'].append(l); cur['pg2'] = pg if s else cur['pg2']
    for x in blocks:   # 끝의 빈 줄 정리 · 끝 쪽 = 마지막 글줄의 쪽
        while x['lines'] and not x['lines'][-1].strip(): x['lines'].pop()
    return blocks
if __name__ == '__main__':
    for ed in NPAGES:
        bl = parse(ed); by = {}
        for x in bl: by.setdefault(x['sec'], []).append(x['num'])
        print(f'{ed}판 블록 {len(bl)} ·', ' · '.join(f'{k} {len(v)}개 [{",".join(v)}]' for k, v in by.items()))
        for x in bl: print(f"   {x['sec'][:12]:12} {x['num']:>2} p.{x['pg']}-{x['pg2']}  {x['lines'][0].strip()[:60]}")
