import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""OMS2 구강악안면외과학 2(4Q) JB(23·24·25판) → 문항 블록 parse(ed, n) → [{'ed','sec','prof','num','pg','pg2','lines'}]
판 구조(2026-11-16 전 쪽 글·그림 확인 — 보고 work/OMS2/jb/R_JB_OMS2.md 1절):
  - 25판(2024년 시험까지): 교수 머리 '[최진영 교수님]'·'[박주영 교수님]'·'[서병무 교수님]' → 연도 칸 '2024-4Q'·'2023-4Q'·'2022-4Q'
      번호는 교수마다 칸을 넘어 이어짐(최진영 1~15 · 박주영 1~10 · 서병무 1·2 → 3·4) → 칸 이름 '2024-4Q · 최진영'
      최진영 1번 뒤 번호 없는 '(유사복원) 수면무호흡 진단기준 넘버링(24)' = 따로 블록 '1(유사복원)'(멘트 '최진영 9 문항' = 1~8 + 이 블록)
      서병무 '2023-4Q' 칸 ': 2024-4Q 에 모두 출제' = 칸 멘트(문항 아님)
  - 24판·23판: 교수 머리 '<I> 최진영 교수님 Part' → 강의 머리('[New Paradigm … POPA]'·'[Orthognathic Surgery and Facial Bone …]'·'[Surgical Treatment of OSA]'·
      '[211213 악교정수술 후 합병증]'·'[Loading Protocol]'·'[참고: 악안면영역 심미수술 …]' — 두 줄에 걸친 머리는 둘째 줄 버림 · 박주영은 강의 머리 없음)
      → 연도 칸 '★★2023 년 기출★★'(칸마다 1부터 · '★★2022, 2021 년 기출★★' = 두 해 한 칸 '2022·2021') → 칸 이름 '<교수> <강의> <연도>'(예 '최진영 POPA 2023')
      23판 박주영 끝 '★★황순정 교수님 기출 중 박주영 교수님과 내용이 겹치는 부분★★' → 칸 '박주영 황순정'
      '2-1.'·'2-2.'(박주영 2022) = 따로 블록 '2-1'·'2-2'(23판 멘트 '박주영 6 문항 (미복원 1)' = 1·2-1·2-2·3·4 + 미복원 1) · '3-1 …'(마침표 없음)은 3번 안
      23판 서병무 2022 3번 뒤 '추가복원:' = 따로 블록 '3(추가복원)'(멘트 '서병무 5 문항 (미복원 1)' = 1·2·3·추가복원 + 미복원 1)
      '1. 2023 1 번' = 가리킴 블록(그 해 칸에도 같은 문제 — assemble에서 그 카드의 다른 판본)
  - 문항 시작 판정(RULES 0-1 — 답·보기·해설 안 '1. …' 번호 줄은 문항 아님): 번호 = 바로 앞 번호 + 1 이고, 앞 블록이 닫힘('참고' 줄을 지남 · 가리킴 블록은 바로 닫힘)
      예외 FORCEQ(앞 블록에 '참고'가 없음) · NOTQ('참고' 뒤 해설의 '1. …' 목록)
  - 쪽 첫 줄 = 쪽 번호(24판 35~46 · 23판 5~20 — 큰 책의 일부) · '※본 파일의 무단인쇄…※' 줄 뺌 · 24판 12쪽은 빈 쪽"""
import re, json
BASE = J.JBX
NPAGES = {'25': 12, '24': 12, '23': 16}
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        ls = rd(f'{BASE}OMS2_20{ed}/{i}.txt').split('\n'); first = True
        for l in ls:
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
PROF25 = re.compile(r'^\s*\[\s*(최진영|박주영|서병무)\s*교수님\s*\]\s*$')
YEAR25 = re.compile(r'^\s*(20\d\d)\s*-\s*4Q\s*$')
PROFP = re.compile(r'^\s*<\s*(I|II|III|IV)\s*>\s*(\S+?)\s*교수님\s*Part')
LECH = [(re.compile(r'^\s*\[\s*New Paradigm'), 'POPA'), (re.compile(r'^\s*\[\s*Orthognathic Surgery and Facial Bone'), 'FACEGIDE'),
        (re.compile(r'^\s*\[\s*Surgical Treatment of OSA\s*\]'), 'OSA'), (re.compile(r'^\s*\[\s*\d{6}\s*악교정수술'), '합병증'),
        (re.compile(r'^\s*\[\s*Loading Protocol\s*\]'), 'Loading'), (re.compile(r'^\s*\[\s*참고\s*:\s*악안면영역\s*심미수술'), '심미수술')]
YEARH = re.compile(r'^\s*★+\s*(20\d\d)(?:\s*,\s*(20\d\d))?\s*년\s*기출\s*★+\s*$')
HWANG = re.compile(r'^\s*★★\s*황순정')
QRE = re.compile(r'^\s*(\d{1,2})\s*[.．](?!\d)\s*(\S.*)?$')
SUBQ = re.compile(r'^\s*(\d{1,2})-(\d)\s*[.．]\s*(\S.*)?$')
PTR = re.compile(r'^\s*\d{1,2}(?:-\d)?\s*[.．]\s*20\d\d\s*\d{1,2}\s*번\s*$')   # '1. 2023 1 번' 가리킴
REF = re.compile(r'^\s*(\[참고\]|참고\s*[:：])')
FORCEQ = {('23', '서병무 합병증 2022'): {'3. Aftermath routine 부작용(넘버링)'}}   # 23판 서병무 2022 2번에 '[참고]' 줄이 없음(답만) → 다음 3번이 새 문항
NOTQ = {('23', '한정준 Loading 2022'): {'2. Faster treatment', '3. More ideal soft tissue drape', '4. Immediate satisfaction and patient',
                                       '5. Greater bone-implant contact'}}   # 1번 '참고:' 뒤 '해설:' 속 <Advantages …> 1.~5. 목록(문항 아님 — 진짜 2번 = '2. 즉시하중을 …')
# (11-16 JBV) 가리킴 줄 뒤의 답·해설이 바로 앞 소문항의 것인 칸 — 24판 박주영 2022: 굵은 머리 '2-1. 피지샘 … 객관식 문항' · '2-2. 2023 2 번'(= 2023 2번 STSG 선 가리킴)
#   두 줄 아래 '[답] 해설참고 [참고] … p.8-11 [해설] 각 층의 특징 …'(피부 층 = 2-1의 답 — 25판 9번 S06과 같은 해설) → 그 줄들은 2-1 블록에, 2-2 = 가리킴만(→ S02)
PTR_ANS_PREV = {('24', '박주영 2022', '2-2')}
def parse(ed, n=None):
    L = load(ed, n or NPAGES[ed]); blocks = []; cur = None; closed = True
    prof = None; lec = ''; year = None; sec = None; last = 0; sublast = 0
    def new(num, pg, l):
        nonlocal cur, closed
        cur = {'ed': ed, 'sec': sec, 'prof': prof, 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur)
        closed = bool(PTR.match(l))
    for pg, l in L:
        s = l.strip()
        if ed == '25':
            m = PROF25.match(s)
            if m: prof = m.group(1); last = 0; cur = None; sec = None; continue
            m = YEAR25.match(s)
            if m and prof: year = m.group(1) + '-4Q'; sec = f'{year} · {prof}'; cur = None; closed = True; continue
        else:
            m = PROFP.match(s)
            if m: prof = m.group(2); lec = ''; sec = None; cur = None; continue
            hit = next((lab for rx, lab in LECH if rx.match(s)), None)
            if hit and prof: lec = hit; sec = None; cur = None; continue
            m = YEARH.match(s)
            if m and prof:
                year = m.group(1) + (('·' + m.group(2)) if m.group(2) else ''); sec = ' '.join(x for x in (prof, lec, year) if x)
                last = 0; sublast = 0; cur = None; closed = True; continue
            if HWANG.match(s) and prof:
                sec = f'{prof} 황순정'; last = 0; sublast = 0; cur = None; closed = True; continue
        if sec is None: continue
        if s.startswith('(유사복원)') and closed: new(f'{last}(유사복원)', pg, l); continue
        if s.startswith('추가복원') and closed: new(f'{last}(추가복원)', pg, l); continue
        ms = SUBQ.match(s)
        if ms:
            a, b = int(ms.group(1)), int(ms.group(2))
            if (b == 1 and a == last + 1 and closed) or (b == sublast + 1 and a == last and b > 1):
                last = a; sublast = b; new(f'{a}-{b}', pg, l); continue
        mq = QRE.match(s)
        if mq and s not in NOTQ.get((ed, sec), ()):
            a = int(mq.group(1))
            if a == last + 1 and (closed or s in FORCEQ.get((ed, sec), ())):
                last = a; sublast = 0; new(str(a), pg, l); continue
        if cur is not None:
            tgt = blocks[-2] if (ed, sec, str(cur['num'])) in PTR_ANS_PREV and len(blocks) > 1 else cur
            tgt['lines'].append(l); tgt['pg2'] = pg
            if REF.match(s): closed = True
    for x in blocks:   # 끝의 빈 줄 정리
        while x['lines'] and not x['lines'][-1].strip(): x['lines'].pop()
    return blocks
if __name__ == '__main__':
    allb = {}
    for ed in ('25', '24', '23'):
        b = parse(ed); allb[ed] = b
        secs = {}
        for x in b: secs.setdefault(x['sec'], []).append(x['num'])
        print(f'=== {ed}판: {len(b)} blocks')
        for k, v in secs.items(): print(f'   {k}: {" ".join(v)}')
        if '-v' in _sys.argv:
            for x in b:
                txt = '\n'.join(x['lines']); stem = ' '.join(x['lines'][:2])[:62]
                print(f" {x['sec']:22}|{str(x['num']):>12}|p{x['pg']:<2}-{x['pg2']:<2}|{len(txt):5}|{'A' if '답' in txt else '-'}| {stem}")
    json.dump(allb, open(J.work('OMS2', 'jb_blocks.json'), 'w'), ensure_ascii=False)
