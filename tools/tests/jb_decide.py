"""10-25 JB 결정 반영 회귀(사용자 10-24 결정표 — guide/handoff/jb_audit_1024) — 팩 정적 검사(브라우저 없음).
① 미복원·복원 불충분 자리 카드 0(공통-5 — 기출 대장에만)
② '다른 해의 관련 문항'·'같은 내용이 … 다른 연도 칸' 링크가 양쪽 카드에 다 있음(공통-2)
③ 이전 출제 꼴(.qprev)은 문제(.qtext) 뒤 · 글이 있음(공통-3)
④ 예고·예상 배지(.ybadge.kd) 카드는 출제 연도(data-yrs)가 비어 있음
⑤ 팩 어디서든 data-go가 가리키는 JB id가 실제 카드로 있음(합치기·숨김 뒤 끊긴 링크 0)
⑥ JB id 잠금·옮김 표 오류 0(tools/jblock.lock_errors)
⑦ 10-25c 앞면 = 가장 최신 판 — '다른 판본'에 앞면보다 새 판 사본(가리킴 아님)이 있는 카드는 팩 frontskip(자동 건너뜀·front=0)뿐 · 'JB 원본' 단추 = 앞면 판
⑧ 10-25c '📜 이전 답'(details.ab.pans)은 JB 답안 바로 뒤 · 원본 쪽 단추·글이 있음 · 과목마다 1장 이상"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import re, json, html, jblock
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
txt = lambda h: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()
HIDE = re.compile(r'^\s*\d+(\s*-\s*\d+)?\s*[.)]?\s*\(?\s*(미복원|복원\s*불충분)\s*\)?\s*\.?\s*$')
SIDS = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
for s in SIDS:
    P = J._load_js(_os.path.join(J.ROOT, 'docs', 'packs', s + '.js')); C = P['cards']
    unrec = [i for i, h in C.items() if (m := re.search(r'<div class="qtext">(.*?)</div></div>', h, re.S)) and HIDE.match(txt(m.group(1)))]
    ok(not unrec, f'{s} ① 미복원 자리 카드 0 {unrec[:5]}')
    links = {}
    for i, h in C.items():
        for kind, rx in (('rel', r'(?:다른 해|같은 해)의 관련 문항\([^)]*\): (.*?)</div>'), ('pair', r'같은 내용이 JB의 다른 연도 칸에도 실려 있음: (.*?)</div>')):
            for m in re.finditer(rx, h, re.S):
                for t in re.findall(r'data-go="([^"]+)"', m.group(1)): links.setdefault((kind, i), set()).add(t)
    oneway = [f'{a}→{b}' for (k, a), bs in links.items() for b in bs if a not in links.get((k, b), set())]
    ok(not oneway, f'{s} ② 관련 링크 양방향 {len(links)}카드 · 한쪽만 {oneway[:6]}')
    badprev = [i for i, h in C.items() if 'class="qprev"' in h and (h.index('class="qprev"') < h.index('class="qtext"') or not txt(re.search(r'<div class="qprev">.*?<div class="lines">(.*?)</div></div>', h, re.S).group(1)))]
    nprev = sum(1 for h in C.values() if 'class="qprev"' in h)
    ok(not badprev, f'{s} ③ 이전 출제 꼴 {nprev}카드 · 자리·글 오류 {badprev[:5]}')
    skip = set(P.get('frontskip') or []); newer = []; npans = 0; badp = []
    for i, h in C.items():
        acts = re.search(r'<div class="acts">(.*?)</div>', h, re.S); fe = re.findall(r'data-jb="([0-9a-z]+)-\d+"', acts.group(1)) if acts else []
        oth = re.search(r'<details class="oth">(.*?)</details>', h, re.S)
        if fe and oth:
            for m in re.finditer(r'<div class="oh">JB ([0-9a-z]+)판[^<]*<button[^>]*>[^<]*</button></div><div class="lines box0">(.*?)</div></div>(?=<div class="oh">|$)', oth.group(1), re.S):
                t = re.sub(r'\s+', '', txt(m.group(2)))
                if m.group(1) > fe[0] and len(t) >= 30 and not (len(t) < 80 and re.search(r'\d+\s*번\s*(?:문제\s*)?(?:와\s*|과\s*)?(?:중복|동일|같음)|미복원|복원\s*불충분', t)) and i not in skip: newer.append(f'{i}({fe[0]}<{m.group(1)})'); break
        if 'class="ab pans"' in h:
            npans += 1; k = h.index('class="ab pans"'); j = h.find('class="ab jbans')
            seg = h[k:h.find('</details>', k)]
            if j < 0 or j > k or 'data-jb=' not in seg or not txt(seg): badp.append(i)
    ok(not newer, f'{s} ⑦ 앞면 = 가장 최신 판(frontskip {len(skip)}) · 새 판 사본이 남은 카드 {newer[:6]}')
    ok(npans > 0 and not badp, f'{s} ⑧ 📜 이전 답 {npans}카드 · 자리·단추·글 오류 {badp[:5]}')
    badk = [i for i, h in C.items() if 'ybadge n0 kd' in h and not re.search(r'data-yrs=""', h)]
    ok(not badk, f'{s} ④ 예고·예상 배지 {sum(1 for h in C.values() if "ybadge n0 kd" in h)}카드 · 연도 남음 {badk}')
    blob = json.dumps(P, ensure_ascii=False)
    gos = set(re.findall(r'data-go=\\"([A-Za-z]{1,3}\d[\w-]*)\\"', blob)) | set(re.findall(r'data-go="([A-Za-z]{1,3}\d[\w-]*)"', blob))
    dang = sorted(g for g in gos if g not in C)
    ok(not dang, f'{s} ⑤ 끊긴 JB 링크 0 (링크 대상 {len(gos)}개) {dang[:8]}')
errs = [(f, e) for f, n, e in jblock.lock_errors(_os.path.join(J.ROOT, 'docs')) if e]
ok(not errs, f'⑥ JB id 잠금·옮김 표 {errs[:3]}')
print('RESULT', 'PASS' if not fails else 'FAIL ' + str(len(fails)))
