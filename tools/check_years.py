"""출제연도 규칙 전수 검사 — "JB 괄호 연도(문항 첫머리 전체에서, 변형 포함) ∪ 실린 연도 칸 ∪ 같은 문제의 다른 칸"이 사이트 연도 배지에 다 있는지.
사용: .venv/bin/python tools/check_years.py [SID ...]   (docs/packs/<SID>.js = 현재 빌드 기준)
문항 첫머리(답 이전)의 괄호를 느슨하게 읽어(’ ' ~ 이전 이후 년 년도 짤 탈 학번 … 제거) 두 자리 연도 목록으로 보이는 것만 뽑고,
배지 연도에 없는 해가 있으면 보고한다. 학번 표기(노인치과학 24·23판)는 자동 판단하지 않고 '학번?'으로 표시만 — 사람이 확인."""
import os, re, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J
NOISE = r"(반짤반탈|짤 변형|완짤|짤|탈|년도|년|NEW|new|이전|이후|’|‘|'|`|~|\.|번과 유사|유사|학번|추가|기출|출제|복원|최근|연속|회)"

def cand(g):
    g2 = re.sub(NOISE, ' ', g).replace('，', ',').replace('·', ',').replace('/', ',')
    if not re.fullmatch(r'\s*(20\d\d|\d\d)(\s*[,、\-\s]\s*(20\d\d|\d\d)?)*\s*', g2): return None
    vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
    if not vs or not all(5 <= v <= 26 for v in vs): return None
    if re.search(r'\d\s*-\s*\d', g2) and len(vs) == 2: vs = list(range(min(vs), max(vs) + 1))
    return vs

def main(sids):
    bad = 0
    for sid in sids:
        t = open(os.path.join(J.DOCS, 'packs', sid + '.js'), encoding='utf-8').read(); p = json.loads(t[t.index('{'):t.rindex('}') + 1])
        n = 0
        for cid in p['order']:
            h = p['cards'][cid]
            yb = re.search(r'<span class="ybadge[^"]*"(?: title="([^"]*)")?[^>]*><b>([^<]*)</b>', h)
            yrs = {int(y) % 100 for y in re.findall(r'20\d\d', (yb.group(1) or yb.group(2)) if yb else '')}
            q = re.search(r'<div class="qtext">(.*?)</div>\s*(?:<img|<div class="small"|<div class="qsub")', h, re.S)
            stem = html.unescape(re.sub(r'<[^>]+>', '\n', q.group(1) if q else ''))
            heads = [('본문', stem)]
            for o in re.findall(r'<div class="lines box0">(.*?)</div></div>', h, re.S):   # 다른 판본에 실린 같은 문제(첫 3줄)
                heads.append(('다른 판본', '\n'.join(html.unescape(re.sub(r'<[^>]+>', '\n', o)).split('\n')[:6])))
            for where, txt in heads:
              for m in re.finditer(r'\(([^()]{1,60})\)', txt):
                vs = cand(m.group(1))
                if not vs: continue
                miss = sorted(set(vs) - yrs, reverse=True)
                if miss:
                    n += 1; bad += 1
                    flag = ' 학번?' if ('학번' in m.group(1) or (sid == 'GERI')) else ''
                    print(f'  {sid} {cid} [{where}]: 괄호 ({m.group(1).strip()}) → 배지에 없는 해 {miss}  (배지 {sorted(yrs, reverse=True)}){flag}')
        print(f'== {sid}: 의심 {n}건')
    return bad

if __name__ == '__main__':
    sys.exit(1 if main([a.upper() for a in sys.argv[1:]] or ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']) else 0)
