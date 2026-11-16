import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""OPATH 임상구강악안면병리학(4Q) JB 23·24·25판 → 문항 블록 (2026-11-16 JB 단계 · 보고 work/OPATH/jb/R_JB_OPATH.md)
parse(ed, n) → 블록 [{'ed','sec','prof','num','pg','pg2','lines','skey','yr'}]
판 구조(세 판 모든 쪽 글·그림 확인 — 두 단 편집, pdfium 글 = 왼 단 → 오른 단):
  - 연도 칸 '2024-4Q'·'2023-4Q'·'2022-4Q' + '과거 통합 기출'(괄호 연도 16~21)
  - 강의 머리: 24·25판 '[5. Inflammation of Jaw : 이재일]'(대괄호 · 두 줄로 끊김도) · 23판 2022 칸 '5. Inflammation of Jaw : 이재일'(대괄호 없음 — 번호 머리)
    과거 통합 머리 '[6] Inflammatory lesions of the jaw' · '[범위외] Antral opacities' · 24판 2023 칸 '[객관식]'·'[서술형]'·'[단답형]'
  - 번호 매김: 2022 칸·과거 통합 = 강의 머리마다 1부터(skey '2022.5'·'과거.6') · 25판 2024·2023 칸, 24판 2023 칸 = 칸 전체 한 줄(skey '2024')
  - 'N-M.' 덧문항: 앞 블록에 이미 답 줄이 있으면 새 블록(23·24판 2022 '2-1. 드문 세균 감염증'·'4-1. 양측성' — 과거 기출을 덧붙인 것) · 아니면 앞 블록의 일부(25판 2022 '2-1'·23판 과거 [7] 3번 안 '4-1~4-3')
  - 24판 p16 = 머리 없는 조각(왼 단 = 23판 과거 통합 [4] 구강 감염성 질환 1~3번과 같은 글 · 오른 단 끝 '[Histopathologic feature]…' = 2022 FD 5번 해설 끝) → 칸 '과거 통합 · 구강 감염성 질환(24판 p16 — 머리 없음)'
    · FD 해설 조각(4줄)은 24판 2022 [6] 5번 블록 끝으로 옮김(글자 그대로 — 23판 2022 FD 블록과 같은 차례)
  - 해설·답 안의 번호 줄(답 목록 '3. GMS'·'4. AFB' · 해설 '3. Keratocystic …' 등)은 문항 아님(NOTQ) · 수 = 블록 수 검증(__main__)"""
import re, json, os
BASE = J.JBX
NPAGES = {'25': 32, '24': 16, '23': 39}
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
FOOT = {'임상구강악안면병리학', '-2025 4Q JB-', '-2024 4Q JB-', '-2023 4Q JB-'}
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        first = True
        for l in rd(f'{BASE}OPATH_20{ed}/{i}.txt').split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue   # 쪽 번호(원본 합본 쪽 번호 포함)
            if l.strip(): first = False
            if l.strip() in FOOT: continue
            lines.append((i, l.rstrip()))
    return lines
PROFS = '윤혜정|안동기|이재일|황상미|김형석|이경훈|홍성두|오규영|이삭'
YSEC = re.compile(r'^\s*(20\d\d)\s*-\s*4Q\s*$')
PSEC = re.compile(r'^\s*과거 통합 기출\s*$')
LHB = re.compile(r'^\[(\d{1,2})\s*\.\s*(.+?)\s*(?::\s*(' + PROFS + r'))?\s*\]$')   # [5. Inflammation of Jaw : 이재일] · [10. 그 외 불완전 복원]
LHN = re.compile(r'^(\d{1,2})\s*\.\s+(.+?)\s*:\s*(' + PROFS + r')(\s*\([^)]*\))?\s*$')   # 23판 2022 칸 '9. 임상화학검사 : 이경훈 (작년 송정한)'
PHB = re.compile(r'^\[(\d{1,2}|범위외)\]\s*(.+)$')                                      # 과거 통합 '[6] Inflammatory lesions of the jaw'
FHB = re.compile(r'^\[(객관식|서술형|단답형)\]$')
QRE = re.compile(r'^(\d{1,2})(?:-(\d{1,2}))?\s*[.．]{1,2}\s*(\S.*)?$')
NODOT = re.compile(r'^(1|13) (?:홍반증|탈 OLP)')                                     # 24판 2023 칸 점 없는 번호
ANS = re.compile(r'^\s*(정답|답)\s*[:：]|^\s*답\s*$')
GLOBAL = {('25', '2024'), ('25', '2023'), ('24', '2023')}                                  # 칸 전체가 번호 하나로 이어짐
JUMP = {('25', '2024', 21), ('25', '2024', 20), ('23', '과거.7', 5)}                          # 25판 2024 칸 16 → 21(탈) → 20(탈) — JB 번호 그대로 · 23판 과거 [7] 3번 다음 5번(4-1~4-3은 3번 안)
# 답·해설 안의 번호 줄(문항 아님) — (판, 줄 앞부분)
NOTQ = {('25', '3. GMS'), ('25', '4. AFB'), ('24', '3. GMS'), ('24', '4. AFB'), ('23', '3. GMS'), ('23', '4. AFB'),
        ('25', '3. Keratocystic odontogenic tumor'), ('25', '4. Others'), ('23', '3. Keratocystic odontogenic tumor'), ('23', '4. Others'),
        ('24', '10. 231201_홍성두_Giant cell lesions'), ('23', '10. 231201_홍성두_Giant cell lesions'),
        ('23', '2. FBS >= 126 mg/dL'), ('23', '3. 2hr >200 mg/dL during OGTT'),
        ('23', '2. Mucocele'), ('23', '3. POMC'),
        ('25', '2. Odontogenic myxoma'), ('23', '2. Odontogenic myxoma'),
        ('24', '5. 12-25%'),                                               # 24판 2023 4번 보기
        ('23', '2. 수술명'), ('23', '3. 수술소견'), ('23', '4. 병력 및 임상소견'), ('23', '5. 임상진단'),   # 23판 과거 [2] 1번 답 목록
        }
def _notq(ed, s): return any(e == ed and s.startswith(p) for e, p in NOTQ)
FORCE_SEC = {('24', 16): ('과거', '4', '구강 감염성 질환(24판 p16 — 머리 없음)', '')}   # 24판 p16 머리 없는 조각
def parse(ed, n=None):
    L = load(ed, n or NPAGES[ed]); blocks = []; cur = None
    yr = None; skey = None; sec = None; prof = ''; last = 0; glob = False; i = 0; page_forced = set()
    def newsec(y, k, title, pf, reset=True):
        nonlocal yr, skey, sec, prof, last, cur
        yr = y; prof = pf; cur = None
        skey = y if (ed, y) in GLOBAL else f'{y}.{k}'
        sec = (f'{y}-4Q · {title}' if y != '과거' else f'과거 통합 · {title}')
        if reset and (ed, y) not in GLOBAL: last = 0
    while i < len(L):
        pg, l = L[i]; s = l.strip(); i += 1
        if (ed, pg) in FORCE_SEC and pg not in page_forced:
            page_forced.add(pg); y, k, t, pf = FORCE_SEC[(ed, pg)]; newsec(y, k, t, pf); last = 0
        m = YSEC.match(s)
        if m: yr = m.group(1); skey = yr; sec = f'{yr}-4Q'; prof = ''; last = 0; cur = None; continue
        if PSEC.match(s): yr = '과거'; skey = '과거'; sec = '과거 통합'; prof = ''; last = 0; cur = None; continue
        if yr is None: continue                       # 머리말(멘트·수업 표)
        # 대괄호 머리 — 두 줄로 끊긴 것도
        cand = s
        if s.startswith('[') and not s.endswith(']') and i < len(L): cand = s + ' ' + L[i][1].strip()
        mh = LHB.match(s) or LHB.match(cand)
        if mh and yr != '과거':
            if mh.string is cand and cand != s: i += 1
            newsec(yr, mh.group(1), mh.group(2).strip(), mh.group(3) or ''); continue
        mp = PHB.match(s)
        if mp and yr == '과거':
            title = mp.group(2).strip()
            if title.endswith(' with') and i < len(L): title += ' ' + L[i][1].strip(); i += 1   # '[13] Common odontogenic tumors in jaws with' + 다음 줄(쪽 넘김)
            newsec('과거', mp.group(1), title, ''); continue
        mf = FHB.match(s)
        if mf: newsec(yr, mf.group(1), mf.group(1), '', reset=False); continue
        if ed == '23' and yr == '2022':
            mn = LHN.match(s)
            if mn: newsec(yr, mn.group(1), mn.group(2).strip(), mn.group(3)); continue
            if re.fullmatch(r'6\.\s*Benign Nonodontogenic tumors of the Jaws', s) and i < len(L) and re.fullmatch(r':\s*이재일', L[i][1].strip()):
                i += 1; newsec(yr, '6', 'Benign Nonodontogenic tumors of the Jaws', '이재일'); continue
            if re.fullmatch(r'13\.\s*그 외 불완전 복원', s): newsec(yr, '13', '그 외 불완전 복원', ''); continue
        mq = QRE.match(s); nd = NODOT.match(s) if ed == '24' else None
        if (mq or nd) and not _notq(ed, s):
            a = int((mq or nd).group(1)); b = int(mq.group(2)) if (mq and mq.group(2)) else None
            num = None
            if b is None:
                if a == last + 1 or (ed, skey, a) in JUMP: num = str(a)
            elif a == last and cur is not None and any(ANS.match(x) for x in cur['lines']):
                num = f'{a}-{b}'
            if num:
                cur = {'ed': ed, 'sec': sec, 'prof': prof, 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l], 'skey': skey, 'yr': yr}
                blocks.append(cur)
                if b is None: last = a
                continue
        if cur is not None: cur['lines'].append(l); cur['pg2'] = pg
    for x in blocks:
        while x['lines'] and not x['lines'][-1].strip(): x['lines'].pop()
    if ed == '24':   # p16 오른 단 끝 FD 해설 조각 → 2022 [6] 5번(FD) 블록 끝(글자 그대로)
        src = next((x for x in blocks if x['skey'] == '과거.4' and any(l.strip() == '[Histopathologic feature]' for l in x['lines'])), None)
        dst = next((x for x in blocks if x['skey'] == '2022.6' and x['num'] == '5'), None)
        if src and dst:
            k = next(j for j, l in enumerate(src['lines']) if l.strip() == '[Histopathologic feature]')
            dst['lines'] += src['lines'][k:]; src['lines'] = src['lines'][:k]; dst['pg2'] = 16
            while src['lines'] and not src['lines'][-1].strip(): src['lines'].pop()
    return blocks
def key(x): return f"{x['ed']}|{x['skey']}|{x['num']}"
if __name__ == '__main__':
    allb = {}
    for ed in NPAGES:
        b = parse(ed); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks')
        for x in b:
            txt = '\n'.join(x['lines']); stem = ' '.join(l.strip() for l in x['lines'][:2])[:60]
            print(f" {key(x):18}|{x['prof']:3}|p{x['pg']:<2}-{x['pg2']:<2}|{len(txt):5}|{'A' if any(ANS.match(l) for l in x['lines']) else '-'}| {stem}")
    os.makedirs(J.work('OPATH'), exist_ok=True)
    json.dump(allb, open(J.work('OPATH', 'jb_blocks.json'), 'w'), ensure_ascii=False)
