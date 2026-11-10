"""10-05 기능 연동 검사 — 빌드된 팩에서
  ① 인용 칩(cite data-k·data-p·data-pp)이 가리키는 쪽 이미지가 그림 묶음(<SID>.img.<강의>.js) 또는 그림 파일 목록(11-10 팩 imgf — packs/img/<SID>/…)에 있는지(imgalias 반영)
  ② JB 카드 '📖 정리본' 칩(data-golec K:j)이 실제 카드를 가리키고 그 카드 ⭐/jb=에 이 문항이 있는지
  ③ 정리본·표·예상의 기출 칩(data-go / {jb:})이 있는 문항인지
  ④ 11-10 인용 칩의 쪽이 숫자인지(A19 — 원고의 설명 글 '[[OHQ:쪽]]'이 없는 쪽 칩이 됨 · build4가 이제 글자 그대로 둠)
  ⑤ 11-10 JB 원본 쪽 단추(data-jb 판-쪽)가 팩의 JB 원본 쪽 그림(묶음 <SID>.img.jb<판>.js 또는 imgf.jb)에 있는지(A18 — 없는 쪽을 누르면 다른 쪽·빈 창)
  ⑥ 11-10 그림 파일 방식: imgf에 적힌 파일이 실제로 있는지
  보관(frozen) 분기 팩은 다시 빌드할 수 없어 못 고침 → 아래 KNOWN에 적힌 것은 '알려진 것 n'으로 따로 세고 FAIL로 치지 않음(새 ✗가 생기면 FAIL · 다시 빌드해 사라지면 KNOWN에서 뺌)
  .venv/bin/python tools/check_links.py [SID…]      # 과목 = $JBL_Q 분기(없으면 지금 분기) · 팩 자리 = 그 과목 분기의 docs(J.docs_of — $JBL_DOCS면 그 폴더)"""
import os, sys, re, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools')); import jblpaths as J
QS = J.QS
# 보관 분기의 알려진 것(11-10 메인 결정) — 'cite <키>:<쪽>'(숫자 아닌 쪽) · 'jb <판>-<쪽>'(팩에 없는 JB 원본 쪽)
#   GERI: tools/geri/lec_OHQ.txt 머리말의 설명 글 [[OHQ:쪽]] · PHARM: 23q4판 17~20쪽은 대장의 쪽 단추(NPAGES 20)만 있고 쪽 그림이 묶음에 없음 — 3Q를 다시 빌드할 때(2026 출제 반영) 고침
KNOWN = {'GERI': {'cite OHQ:쪽'}, 'PHARM': {'jb 23q4-17', 'jb 23q4-18', 'jb 23q4-19', 'jb 23q4-20'}}
SIDS = [a.upper() for a in sys.argv[1:]] or J.sids()
def walk(o, w=''):
    """팩 안의 모든 글(어디 있는지 이름과 함께) — 카드·강의·예상·표·한눈표·대장·경향…"""
    if isinstance(o, str): yield w, o
    elif isinstance(o, list):
        for i, x in enumerate(o): yield from walk(x, f'{w} {x["k"]}' if isinstance(x, dict) and isinstance(x.get('k'), str) and w == 'lect' else f'{w} {i}')
    elif isinstance(o, dict):
        for k, v in o.items(): yield from walk(v, f'{w} {k}'.strip())
bad_all = known_all = 0
for SID in SIDS:
    D = J.docs_of(SID); pf = os.path.join(D, 'packs', SID + '.js')
    if not os.path.exists(pf): print(f'{SID}: 팩 없음({os.path.relpath(pf, ROOT)}) — 건너뜀'); continue
    P = J._load_js(pf); have = set(); havejb = set(); nofile = []
    for f in sorted(glob.glob(os.path.join(D, 'packs', SID + '.img.*.js'))):
        if f.endswith('.img.jb.js'): continue   # 옛 index 호환 심(데이터 없음)
        t = open(f, encoding='utf-8').read(); i = t.index('{'); j = t.rindex('}')
        try: o = json.loads(t[i:j + 1]); have |= set((o.get('lec') or {}).keys()); havejb |= set((o.get('jb') or {}).keys())
        except Exception as e: print('  ? 청크 읽기 실패', f, e)
    for kind, got in (('lec', have), ('jb', havejb)):   # 11-10 그림 파일 방식 — 목록(imgf)에 있고 파일도 있는 것만 '있음'
        for key, h8 in ((P.get('imgf') or {}).get(kind) or {}).items():
            fp = os.path.join(J.img_dir(SID, D), J.img_name(kind, key, h8))
            if os.path.exists(fp): got.add(key)
            else: nofile.append(f'imgf.{kind} {key} → {os.path.relpath(fp, D)}')
    alias = P.get('imgalias') or {}
    htmls = [(f'{L["k"]}/{k}', L.get(k) or '') for L in P['lect'] for k in ('learn', 'sum', 'tbl')] + [(f'JB {q}', h) for q, h in P['cards'].items()] + [(f'예상 {i}', p.get('html', '')) for i, p in enumerate(P.get('preds') or [])] + [('비교표', t.get('html', '') if isinstance(t, dict) else t) for t in P.get('tables') or []] + [('한눈표', P.get('sumall') or '')]
    miss, gobad, lecbad, numbad, jbbad, known = [], [], [], [], [], []
    KN = KNOWN.get(SID, set()) if QS.frozen(QS.quarter_of(SID)) else set(); seen_kn = set()
    def img_ok(k, p):
        for kk in [k] + ([alias[k]] if isinstance(alias.get(k), str) else list(alias.get(k) or [])):
            if f'{kk}-{p}' in have: return True
        return any(x.endswith(f'-{p}') and x.split('-')[0] in (alias.get(k) if isinstance(alias.get(k), list) else [alias.get(k)]) for x in have)
    def put(lst, key, msg):
        if key in KN: seen_kn.add(key); known.append(msg)
        else: lst.append(msg)
    for w, h in walk(P):   # ①④⑤ = 팩 전체 글에서(대장·경향·머리말 포함)
        if 'class="cite' in h:
            for m in re.finditer(r'<button class="cite[^"]*" data-k="([^"]*)" data-p="([^"]*)"(?: data-pp="([^"]*)")?', h):
                k, p, pp = m.groups()
                for pg in (pp.split(',') if pp else [p]):
                    if not pg: continue   # 쪽 그림 폴더가 없는 강의의 글 인용(cite t · data-p="")
                    if not (pg.isascii() and pg.isdigit()): put(numbad, f'cite {k}:{pg}', f'{w} → {k}:{pg}')
                    elif not img_ok(k, pg): miss.append(f'{w} → {k}:{pg}')
        if 'data-jb="' in h:
            for key in dict.fromkeys(re.findall(r'data-jb="([^"]+)"', h)):
                if key not in havejb: put(jbbad, f'jb {key}', f'{w} → JB 원본 {key}')
    for w, h in htmls:
        if not isinstance(h, str): continue
        for m in re.finditer(r'data-go="([^"]+)"', h):
            if m.group(1) not in P['cards']: gobad.append(f'{w} → {m.group(1)}')
    lmap = {L['k']: L for L in P['lect']}
    for q, h in P['cards'].items():
        for m in re.finditer(r'data-golec="([A-Z0-9]+):(\d+)"', h):
            L = lmap.get(m.group(1))
            if not L: lecbad.append(f'JB {q} → 없는 강의 {m.group(1)}'); continue
            arts = re.findall(r'<article class="tc[^"]*" id="t-%s-(\d+)"' % m.group(1), L['learn'])
            if m.group(2) not in arts: lecbad.append(f'JB {q} → 없는 카드 {m.group(1)}:{m.group(2)}'); continue
            seg = L['learn'][L['learn'].index(f'id="t-{m.group(1)}-{m.group(2)}"'):]
            seg = seg[:seg.find('<article', 10) if seg.find('<article', 10) > 0 else len(seg)]
            if f'data-go="{q}"' not in seg: lecbad.append(f'JB {q} → 카드 {m.group(1)}:{m.group(2)}에 이 문항 칩 없음')
    n = len(miss) + len(gobad) + len(lecbad) + len(numbad) + len(jbbad) + len(nofile); bad_all += n; known_all += len(known)
    print(f'{SID}: 쪽 이미지 없는 인용 {len(miss)} · 없는 문항 칩 {len(gobad)} · 📖 연결 어긋남 {len(lecbad)} · 숫자 아닌 쪽 {len(numbad)} · 팩에 없는 JB 원본 쪽 {len(jbbad)} · 없는 그림 파일 {len(nofile)}'
          + (f' · 알려진 것 {len(known)}(보관 분기 — FAIL 아님)' if known else '') + (f' · KNOWN에서 뺄 것 {sorted(KN - seen_kn)}' if KN - seen_kn else ''))
    for x in (miss[:8] + gobad[:8] + lecbad[:12] + numbad[:8] + jbbad[:8] + nofile[:8]): print('    ✗', x)
    for x in known[:8]: print('    (알려진 것)', x)
print('RESULT', 'PASS' if not bad_all else f'FAIL {bad_all}', f'· 알려진 것 {known_all}(보관 분기)' if known_all else '')
sys.exit(1 if bad_all else 0)
