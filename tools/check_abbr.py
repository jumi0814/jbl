"""자료에 없는 약어 검사 — 원칙 "자료에 없는 약어·사실 금지"(예: 슬라이드에 없는 'ITP')를 기계적으로 점검.
사용: .venv/bin/python tools/check_abbr.py [SID ...]
원고(lec_*.txt·annot.txt·tables.txt·pred.txt)의 대문자 약어(2~7자, 숫자 포함 가능)가 그 과목 강의자료 추출본(work/<SID>/mat/*/t·o)이나
JB 원문(work/jb/<SID>_20xx/*.txt)에 한 번이라도 나오는지 본다. 없으면 파일:줄과 함께 보고(판단은 사람이 — 필기 이미지에만 있는 약어일 수 있음)."""
import os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J
ABBR = re.compile(r'(?<![A-Za-z0-9])([A-Z][A-Z0-9]{1,6}s?)(?![A-Za-z0-9])')
SKIP = {'JB', 'OX', 'OK', 'TF', 'PDF', 'OCR', 'NB', 'VS', 'EX', 'CF', 'TBL', 'LEC', 'MAP', 'FIG', 'ALL', 'YES', 'NOT', 'BOX', 'AND', 'OR', 'NO', 'THE', 'FOR'}   # 사이트 자체 용어·영어 단어
import importlib.util
def keys(sid):
    sp = importlib.util.spec_from_file_location('s_' + sid, os.path.join(J.TOOLS, sid.lower(), 'subject.py')); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return set(m.LECMAP)

def corpus(sid):
    txt = []
    for f in glob.glob(os.path.join(J.WORK, sid, 'mat', '*', '[to]', '*.txt')) + glob.glob(os.path.join(J.WORK, 'jb', f'{sid}_20*', '*.txt')):
        try: txt.append(open(f, encoding='utf-8', errors='replace').read())
        except Exception: pass
    return '\n'.join(txt)

def main(sids):
    for sid in sids:
        d = os.path.join(J.TOOLS, sid.lower()); C = corpus(sid); Cn = re.sub(r'[\s\-.]', '', C)
        miss = {}; K = keys(sid)
        try: K |= set(__import__('json').load(open(J.work(sid, 'review', 'qids.json'), encoding='utf-8'))['q'])   # 문항 id(BT04 등)
        except Exception: pass
        for f in sorted(glob.glob(os.path.join(d, 'lec_*.txt'))) + [os.path.join(d, x) for x in ('annot.txt', 'tables.txt', 'pred.txt')]:
            if not os.path.exists(f): continue
            for i, line in enumerate(open(f, encoding='utf-8'), 1):
                body = re.sub(r'\[\[[^\]]+\]\]|\{jb:[^}]+\}|^@[^\n|]*|jb=[^|\n]*|k=[A-Z0-9]+|b=[A-Z0-9_-]+|lec=[^|\s]+', ' ', line)
                for m in ABBR.finditer(body):
                    a = m.group(1); base = a[:-1] if a.endswith('s') and len(a) > 2 else a
                    if base in SKIP or base in K or (len(base) >= 5 and base.isalpha()) or re.fullmatch(r'[A-Z]\d+|\d+', base) or re.fullmatch(r'[QRSTUVCJMHPYEKGB]\d{2}(_\d)?', base): continue
                    if re.search(r'(?<![A-Za-z])' + re.escape(base) + r'(?![a-z])', C) or base in Cn: continue
                    miss.setdefault(base, []).append(f'{os.path.basename(f)}:{i}')
        print(f'== {sid}: 자료·JB에 없는 약어 {len(miss)}개')
        for a, locs in sorted(miss.items(), key=lambda x: -len(x[1])):
            print(f'   {a:8} {len(locs):3}회  {", ".join(locs[:6])}')

if __name__ == '__main__':
    main([a.upper() for a in sys.argv[1:]] or ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM'])
