"""U23 검사: 정리본 카드(.tc)의 글자가 렌더 변경(🔑 분리·가로 흐름·형광 블록·나열 병합) 전후로 같은지.
  .venv/bin/python tools/tests/card_text.py --save <파일>   # 지금 docs/packs의 카드별 글자 저장(변경 전)
  .venv/bin/python tools/tests/card_text.py <파일>          # 저장본과 비교 — 공백·구분자(/ : ; · , — - = → | •)를 뺀 글자 다중집합
  --skip-mem: ⚡ 암기 머리의 안내문(small)은 빼고 비교(U27에서 첫 카드에만 남김)"""
import os, sys, re, json, html, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEP = re.compile(r'[\s/:：;·,—\-=→|•]')
def grab(skip_mem=False):
    out = {}
    for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']:
        t = open(f'{ROOT}/docs/packs/{s}.js', encoding='utf-8').read(); p = (lambda t__: json.loads(t__[t__.index('JBLHUB.register(')+16:-2]))(t)
        for L in p['lect']:
            for m in re.finditer(r'<article class="tc[^"]*"[^>]*data-aid="([^"]+)"(.*?)</article>', L['learn'], flags=re.S):
                h = m.group(2)
                h = re.sub(r'<div class="thead".*?<div class="tbody">', '', h, count=1, flags=re.S)   # 카드 머리(칩 표기)는 제외 — 본문만
                if skip_mem: h = re.sub(r'(<div class="ct">⚡ 암기) <small>.*?</small>', r'\1', h)
                out[f'{s}:{m.group(1)}'] = SEP.sub('', html.unescape(re.sub(r'<[^>]+>', '', h)))
    return out
if __name__ == '__main__':
    a = sys.argv[1:]; sk = '--skip-mem' in a; a = [x for x in a if x != '--skip-mem']
    if a and a[0] == '--save': json.dump(grab(sk), open(a[1], 'w'), ensure_ascii=False); print('saved', len(grab(sk))); sys.exit(0)
    if not a: print(__doc__.strip().splitlines()[0]); print('RESULT SKIP — 비교할 저장본 인자가 없음(구조화 전후 1회용 검사)'); sys.exit(0)
    old = json.load(open(a[0])); new = grab(sk); bad = []
    for k, v in old.items():
        w = new.get(k)
        if w is None or collections.Counter(v) != collections.Counter(w):
            d = (collections.Counter(v) - collections.Counter(w or '')) + (collections.Counter(w or '') - collections.Counter(v))
            bad.append((k, ''.join(sorted(d.elements()))[:30]))
    print('카드', len(old), '개 비교 · 글자 다른 카드', len(bad), bad[:8]); print('RESULT', 'PASS' if not bad else 'FAIL'); sys.exit(1 if bad else 0)
