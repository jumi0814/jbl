"""⭐ 시험포인트(E:)·annot 🎯 요점(K:) 문구 속 연도 ↔ 사이트 연도 배지 대조 — E: 줄에 적힌 'NN·NN년'이 그 문항의 실제 출제연도와 맞는지.
사용: .venv/bin/python tools/check_eyears.py [SID ...]   (docs/packs 현재 빌드 기준)
E: 줄의 문항이 하나일 때만 검사: 문구에 쓴 해 중 배지에 없는 해(= 실리지 않은 해 — 금지) / 배지에 있는데 문구에 없는 해(누락, 참고)."""
import os, re, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J

def badges(sid):
    t = open(os.path.join(J.DOCS, 'packs', sid + '.js'), encoding='utf-8').read(); p = json.loads(t[t.index('{'):t.rindex('}') + 1]); out = {}
    for cid, h in p['cards'].items():
        yb = re.search(r'<span class="ybadge[^"]*"(?: title="([^"]*)")?[^>]*><b>([^<]*)</b>', h)
        out[cid] = {int(y) % 100 for y in re.findall(r'20\d\d', (yb.group(1) or yb.group(2)) if yb else '')}
    return out

def years_in(txt):
    ys = set()
    for m in re.finditer(r'((?:20)?\d\d(?:\s*[·,/]\s*(?:20)?\d\d)*)\s*년(?!도에도)', txt):
        ys |= {int(x) % 100 for x in re.findall(r'(?:20)?(\d\d)', m.group(1))}
    return {y for y in ys if 5 <= y <= 26}

def kyears(txt):
    """🎯 요점 줄: '23년 기출'·'24·23년 객관식'·'21년 3번'처럼 시험 말이 바로 붙은 해만(‘10년 폐암 사망률’ 같은 기간은 뺌)"""
    ys = set()
    for m in re.finditer(r'((?:20)?\d\d(?:\s*[·,/]\s*(?:20)?\d\d)*)\s*년\s*(?:도\s*)?(?=기출|출제|시험|객관식|서술|빈칸|단답|T/F|문항|함정|\d+\s*번|\d+\)|에\s|은|의\s|칸)', txt):
        ys |= {int(x) % 100 for x in re.findall(r'(?:20)?(\d\d)', m.group(1))}
    return {y for y in ys if 5 <= y <= 26}

def main(sids):
    bad = 0
    for sid in sids:
        B = badges(sid); n = 0
        for f in sorted(glob.glob(os.path.join(J.TOOLS, sid.lower(), 'lec_*.txt'))):
            for i, line in enumerate(open(f, encoding='utf-8'), 1):
                if not line.startswith('E:'): continue
                ids, _, txt = line[2:].partition('|'); ids = [x.strip() for x in ids.split(',') if x.strip()]
                if len(ids) != 1 or ids[0] not in B: continue
                head = re.split(r'→|—|JB 답|JB 해설', txt)[0]
                ys = years_in(re.sub(r'"[^"]*"|“[^”]*”', '', head))   # 따옴표 안 문제 원문('보존기간은 10년' 같은 숫자)은 출제연도가 아님
                if not ys: continue
                extra = sorted(ys - B[ids[0]], reverse=True)
                if extra:
                    n += 1; bad += 1
                    print(f'  ✗ {sid} {os.path.basename(f)}:{i} {ids[0]} 문구 연도 {sorted(ys, reverse=True)} 중 배지에 없는 해 {extra} (배지 {sorted(B[ids[0]], reverse=True)})')
        ap = os.path.join(J.TOOLS, sid.lower(), 'annot.txt'); cur = None   # 10-07 annot 🎯 요점(K:) 줄의 연도도(JBKEY — 배지에 없는 해 금지)
        if os.path.exists(ap):
            for i, line in enumerate(open(ap, encoding='utf-8'), 1):
                m = re.match(r'^@(\S+)', line)
                if m: cur = m.group(1); continue
                if not line.startswith('K:') or cur not in B: continue
                ys = kyears(re.sub(r'"[^"]*"|“[^”]*”', '', line[2:]))
                extra = sorted(ys - B[cur], reverse=True)
                if ys and extra:
                    n += 1; bad += 1
                    print(f'  ✗ {sid} annot.txt:{i} {cur} 🎯 요점 연도 {sorted(ys, reverse=True)} 중 배지에 없는 해 {extra} (배지 {sorted(B[cur], reverse=True)})')
        print(f'== {sid}: 배지에 없는 해를 쓴 ⭐·🎯 {n}건')
    return bad

if __name__ == '__main__':
    sys.exit(1 if main([a.upper() for a in sys.argv[1:]] or ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']) else 0)
