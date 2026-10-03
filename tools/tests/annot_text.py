"""U18 검사: JB 카드의 '강의자료 대조'(.ab.chk)·'주변부 확장'(.ab.more) 절의 annot 문구 글자가 자동 구조화 전후로 같은지.
  .venv/bin/python tools/tests/annot_text.py --save <파일>   # 지금 docs/packs의 글자 집합 저장(구조화 전)
  .venv/bin/python tools/tests/annot_text.py <파일>          # 저장본과 비교 — 공백·구분자(/ : ; · , — - = →)를 뺀 글자 다중집합
정리본 ⭐ 자동 채움 항목(annot에 없는 문항 — '정리본 «' 로 시작하거나 li.auto)은 제외"""
import os, sys, re, json, html, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEP = re.compile(r'[\s/:：;·,—\-=→]')
def grab():
    out = {}
    for s in ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']:
        t = open(f'{ROOT}/docs/packs/{s}.js', encoding='utf-8').read(); p = (lambda t__: json.loads(t__[t__.index('JBLHUB.register(')+16:-2]))(t)
        for qid, h in p['cards'].items():
            txt = []
            for _t, sec in re.findall(r'<(section|details) class="ab (?:chk v-\w+|more)">(.*?)</\1>', h, flags=re.S):   # ux2 F02 대조·주변부 = details(머리 summary)
                sec = re.sub(r'<h5>.*?</h5>|<summary[^>]*>.*?</summary>', '', sec, flags=re.S)
                if re.search(r'<li class="auto"', sec) or re.sub(r'<[^>]+>', '', sec).strip().startswith('정리본 «'): continue
                txt.append(html.unescape(re.sub(r'<[^>]+>', '', sec)))
            if txt: out[f'{s}:{qid}'] = SEP.sub('', ''.join(txt))
    return out
if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--save': json.dump(grab(), open(a[1], 'w'), ensure_ascii=False); print('saved'); sys.exit(0)
    if not a: print(__doc__.strip().splitlines()[0]); print('RESULT SKIP — 비교할 저장본 인자가 없음(구조화 전후 1회용 검사)'); sys.exit(0)
    old = json.load(open(a[0])); new = grab(); bad = []
    for k, v in old.items():
        w = new.get(k)
        if w is None or collections.Counter(v) != collections.Counter(w): bad.append(k)
    print('annot 절', len(old), '개 비교 · 글자 다른 절', len(bad), bad[:8]); print('RESULT', 'PASS' if not bad else 'FAIL'); sys.exit(1 if bad else 0)
