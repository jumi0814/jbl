import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""ESTH4 4Q 심미치과학 JB(23·24·25판) → 문항 블록 (2026-11-16 JB 단계 · 보고 work/ESTH4/jb/R_JB_ESTH4.md)
구조 = 연도 칸형(3Q ESTH와 같은 꼴): 쪽 1~2 = 학습부 멘트·수업 표 → '20YY-4Q' 칸 → 번호 문항('★2.' · '★ 7.' · '3. ★' · '10 ★'(점 없음) · '16-17. 미복원' 범위).
parse(ed, n) → 블록 [{'ed','sec','prof','num','pg','pg2','lines'}] — sec = JB 칸 머리 그대로('2024-4Q') · key(x) = '판|칸 해|번호'(예 '25|2024|3').
판본별 특이점(전 쪽 글·그림 확인 2026-11-16):
 - 23판 = 2022(13)·2021(19 — 13번 없음)·2020(8) 칸 · 24판 = 2023(14)·2022(10 — 23판 2022 칸의 이창하 4·11·12번 빠짐)·2021(19) 칸 · 25판 = 2024(17 — 12번·16-17번 '미복원')·2023(14)·2022(10) 칸
 - 25판 2024 칸 10번 머리 '10 ★ Staubi …'(번호 뒤 점 없음) → QRE가 '★' 앞 번호도 받음
 - 답·해설 안의 번호 줄(표·보기·나열)은 문항이 아님 → NOTQ(판마다 정확한 줄 글자) — 번호가 '지난 번호 + 1~6'이라 문항 머리처럼 보이는 것만
 - 24판 17쪽 = 2021 칸 20번(Miller Class III) 뒤 Miller 분류 그림만(글 없음) · 18쪽 = 빈 쪽 → PG2_FIX로 20번 블록 쪽 범위에 17쪽을 넣음(23판은 같은 그림이 13쪽 20번 옆)"""
import re, json
BASE = J.JBX
NPAGES = {'25': 16, '24': 18, '23': 15}
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def load(ed, n):
    lines = []
    for i in range(1, n + 1):
        t = rd(f'{BASE}ESTH4_20{ed}/{i}.txt'); first = True
        for l in t.split('\n'):
            if '무단인쇄' in l: continue
            if first and re.fullmatch(r'\s*\d{1,3}\s*', l): first = False; continue   # 쪽 머리 쪽 번호(23판 265~ · 24판 213~ · 25판 1~)
            if l.strip(): first = False
            lines.append((i, l.rstrip()))
    return lines
SEC = re.compile(r'^\s*(20\d\d)\s*-\s*4Q\s*$')
QRE = re.compile(r'^★?\s*(\d{1,2})(?:\s*-\s*(\d{1,2}))?\s*(?:[.．]|(?=\s+★))\s*★?\s*(\S.*)?$')
# 답·해설 안의 번호 줄 — 문항 아님(판 → 칸 → 줄 글자 strip)
NOTQ = {
    '25': {'2024': {'5. 치아삭제 금속은 1.5-2.0, 도재는 그거보다', '5. 설면: 금속 - 최대 치아 삭제량 0.7~1.0mm,',
                    '1. Gold standard', '2. Excellent mechanical properties', '3. Predictable structural performance',
                    '1. Limited esthetics', '2. Masking ability', '3. Porcelain chipping or fracture',
                    '1. porcelain chipping or fracture', '2. dark metal line visible at margin', '3. possible bluish appearance of the surrounding',
                    '4. wear on opposing teeth', '5. significant tooth reduction required', '6. time-consuming and labor-intensive laboratory',
                    '1. Esthetic', '2. A variety of products with a wide range', '3. Biocompatibility', '4. Monolithic/Bilayered',
                    '1. Low tensile strength', '2. Fracture risk', '3. Antagonist wear',
                    '1. MIP에서 교합 접촉점은 경계부에서 1.5-2.0mm', '2. eccentric movement에서 가능한 금속 도재', '3. 대합치 교합면보고 재료 결정', '4. 심미를 고려하면 전치 및 소구치의 근심',
                    '1. 금속-도재 경계부에서 1.5~2.0mm 까지 떨어진', '2. Eccentric movement 시에도 금속-도재 연결', '3. 동일 재료끼리 접촉: 금속과 금속, 도재와 도재', '4. 심미적 고려. 전치 및 소구치의 근심 접촉점은',
                    '1. Incisor & gingival display', '2. Upper lip curvature (Smile type)', '3. Smile symmetry', '4. Smile arc', '5. Buccal corridor',
                    '6. Occlusal frontal plane', '7. Dental components', '8. Gingival components'},
           '2023': {'1. Esthetic', '2. A variety of products with a wide range', '3. Biocompatibility', '4. Monolithic/Bilayered',
                    '1. Low tensile strength', '2. Fracture risk', '3. Antagonist wear',
                    '1. No light blocking material', '2. Wide range of translucency', '3. Better soft tissue health with', '4. Supragingival margin',
                    '5. Reduced overcontouring of the', '1. Predictable structural performance', '2. No special knowledge required',
                    '1. 보기와 같은 그림', '2. triangular #21', '3. ovoid #21', '4. triangular #11이었으며,'}},
    '24': {'2023': {'1. Esthetic (no light blocking material)', '2. A variety of products with a wide range', '3. Biocompatibilty', '4. Monolithic/veneered',
                    '1. Low tensile strength', '2. Fracture risk', '3. Antagonist wear',
                    '1. No light blocking material', '2. Wide range of translucency', '3. Better soft tissue health with', '4. Supragingival margin',
                    '5. Reduced overcontouring of the', '1. Predictable structural performance', '2. No special knowledge required',
                    '1. Incisor & gingival display', '2. Upper lip curvature (Smile type)', '3. Smile symmetry', '4. Smile arc', '5. Buccal corridor',
                    '6. Occlusal frontal plane', '7. Dental components', '8. Gingival components'}},
}
PG2_FIX = {('24', '2021', '20'): 17}   # 24판 17쪽 Miller 분류 그림(글 없음) = 2021 칸 20번 뒤 그림
def key(x): return f"{x['ed']}|{x['sec'][:4]}|{x['num']}"
def parse(ed, n=None):
    L = load(ed, n or NPAGES[ed]); blocks = []; cur = None; sec = '머리말'; last = 0
    for pg, l in L:
        s = l.strip()
        m = SEC.match(s)
        if m: sec = m.group(1) + '-4Q'; last = 0; cur = None; continue
        if sec == '머리말': continue
        mq = QRE.match(s)
        if mq and s not in NOTQ.get(ed, {}).get(sec[:4], ()):
            a = int(mq.group(1)); b = int(mq.group(2)) if mq.group(2) else None
            if last < a <= last + 6:
                num = f'{a}-{b}' if b else str(a)
                cur = {'ed': ed, 'sec': sec, 'prof': '', 'num': num, 'pg': pg, 'pg2': pg, 'lines': [l]}; blocks.append(cur)
                last = b or a
                continue
        if cur is not None: cur['lines'].append(l); cur['pg2'] = pg
    for x in blocks:   # 끝의 빈 줄 정리 · 그림만 있는 다음 쪽
        while x['lines'] and not x['lines'][-1].strip(): x['lines'].pop()
        x['pg2'] = max(x['pg2'], PG2_FIX.get((x['ed'], x['sec'][:4], x['num']), 0))
    return blocks
# 판마다 칸별 번호(전 쪽 확인 — __main__이 맞대어 봄)
EXPECT = {'25': {'2024': [str(i) for i in range(1, 12)] + ['12', '13', '14', '15', '16-17', '18'], '2023': [str(i) for i in range(1, 15)], '2022': [str(i) for i in range(1, 11)]},
          '24': {'2023': [str(i) for i in range(1, 15)], '2022': [str(i) for i in range(1, 11)], '2021': [str(i) for i in range(1, 13)] + [str(i) for i in range(14, 21)]},
          '23': {'2022': [str(i) for i in range(1, 14)], '2021': [str(i) for i in range(1, 13)] + [str(i) for i in range(14, 21)], '2020': [str(i) for i in range(1, 9)]}}
if __name__ == '__main__':
    allb = {}; bad = 0
    for ed in ('25', '24', '23'):
        b = parse(ed); allb[ed] = b
        print(f'=== {ed}판: {len(b)} blocks')
        for sec, nums in EXPECT[ed].items():
            got = [x['num'] for x in b if x['sec'][:4] == sec]
            ok = got == nums; bad += not ok
            print(f'  {sec}-4Q: {len(got)} {"✓" if ok else "✗ 기대 " + str(nums)} {got}')
        for x in b:
            txt = '\n'.join(x['lines']); stem = ' '.join(x['lines'][:2])[:62]
            print(f" {x['sec']:7}|{str(x['num']):>5}|p{x['pg']:<2}-{x['pg2']:<2}|{len(txt):5}|{'A' if '답' in txt else '-'}| {stem}")
    print('블록 합계', sum(len(v) for v in allb.values()), '· 번호 어긋남', bad)
    json.dump(allb, open(J.work('ESTH4', 'jb_blocks.json'), 'w'), ensure_ascii=False)
