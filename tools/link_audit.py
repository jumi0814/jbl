"""JB 문항 ↔ 강의 ↔ 정리본 ⭐ ↔ 표 ↔ 예상문제 연결 전수 점검(10-16 사용자 '모든 과목 모든 강의자료의 jb 문제 및 각 강의자료와의 연동 … 어떠한 오류가 없게끔')
빌드된 팩(docs/packs/<SID>.js)만 읽음.
  .venv/bin/python tools/link_audit.py [SID…] [--md work/_tmp/link_audit.md] [--year 25]
✗ = 고쳐야 함(종료 코드 1):
  강의 없음 — 복원된(미복원 아님) 현 자료 문항(tier A·B)인데 data-lec 빈칸
  기출 탭 빠짐 — data-lec 강의의 기출 목록(L.jb)에 없음
  ⭐ 없음 — 현 교수 문항인데 그 강의 정리본(학습)에 ⭐ 연결(칩) 없음
  예상 = 기출 — 예상문제 문제 글이 JB 문항과 거의 같은데(이미 출제됨) 관련 기출(b=)에 그 문항이 없음
△ = 확인:
  예상 연결 없음 — 최근 해(--year, 기본 = 팩의 최신 해) 문항인데 그 문항을 관련 기출(b=)로 건 예상문제 0
  표 없음 — 현 교수 문항인데 정리표·비교표 어디에도 칩 없음
  '미출제' 모순 — 예상 t=에 '미출제'인데 b=에 기출이 있음
  정리본 칩 없음 — 강의가 있는 문항 카드에 '📖 정리본' 단추 없음"""
import os, sys, re, json, difflib, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J
from bs4 import BeautifulSoup
SIDS = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
TXT = lambda h: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h or '')).strip()
NORM = lambda s: re.sub(r'[^0-9a-z가-힣]+', '', (s or '').lower())
def refs(h, q):
    return bool(re.search(r'data-(?:go|jb|id|jbgo)="' + re.escape(q) + r'"', h or '')) or bool(re.search(r'(?<![A-Za-z0-9_])' + re.escape(q) + r'(?![A-Za-z0-9_])', h or ''))
def S_(v): return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
def audit(SID, year=None):
    P = J._load_js(os.path.join(J.DOCS, 'packs', SID + '.js')); out = {'x': [], 'w': []}
    LK = {L['k']: L for L in P['lect']}
    ymax = year or max((y for y in P.get('jbyears') or [0]), default=0)
    cur_prof = {}
    for L in P['lect']:
        for p_ in re.split(r'[·,/]\s*', L.get('prof') or ''):
            if p_.strip(): cur_prof.setdefault(L['k'], set()).add(p_.strip().split('(')[0])
    tbl_all = ' '.join(S_(L.get('tbl')) + S_(L.get('sum')) for L in P['lect']) + S_(P.get('tables')) + S_(P.get('sumall'))
    predb = {}
    for i, x in enumerate(P['preds']):
        if x.get('x') or x.get('fn'): continue   # 10-29 최종 N제(fn)는 '예상 연결'로 세지 않음(강의 예상 탭 기준)
        for b in x.get('b') or []: predb.setdefault(b, []).append(i)
    qtext = {}
    for q, h in P['cards'].items():
        a = re.search(r'<article[^>]*>', h); A = a.group(0) if a else ''
        g = lambda k: (re.search(k + r'="([^"]*)"', A) or [None, ''])[1]
        # 10-16 data-prof = 최근 출제 해 교수(YEAR_PROF) → '현 교수' 판정은 강의 연결 교수 data-lprof
        tier, lec, prof = g('data-tier'), g('data-lec'), (g('data-lprof') or g('data-prof')).split('(')[0]
        yrs, unrec = [int(y) for y in g('data-yrs').split() if y.isdigit()], 'data-unrec' in A
        _qe = BeautifulSoup(h, 'html.parser').select_one('.qtext'); qt = re.sub(r'\s+', ' ', _qe.get_text(' ', strip=True)) if _qe else ''   # 10-16 문제 글 전체(첫 줄이 '2025 년 교수님 강조' 같은 머리면 첫 div만 보고 '짧은 문제'로 빠지던 것 — CONS INL 25년 42번)
        qt = re.sub(r'^\s*20\d\d\s*년\s*교수님\s*강조\s*', '', qt)
        qtext[q] = qt
        weak = unrec or re.search(r'복원\s*불충분|복원부실|미복원', qt) or len(NORM(qt)) < 12
        if tier == 'C' or weak: continue
        if not lec: out['x'].append((q, '강의 없음', qt[:60])); continue
        L = LK.get(lec)
        if not L: out['x'].append((q, f'없는 강의 {lec}', qt[:60])); continue
        if q not in (L.get('jb') or []): out['x'].append((q, f'{lec} 기출 탭 빠짐', qt[:60]))
        curp = prof and any(prof == c or prof in c or c in prof for c in cur_prof.get(lec, set()))
        if curp and not refs(S_(L.get('learn')), q): out['x'].append((q, f'{lec} 정리본 ⭐ 없음', qt[:60]))
        if curp and not refs(tbl_all, q): out['w'].append((q, f'{lec} 표 없음', qt[:60]))
        if 'data-golec' not in h: out['w'].append((q, f'{lec} 정리본 칩 없음', qt[:60]))
        if ymax and ymax in yrs and not predb.get(q): out['w'].append((q, f'{lec} {ymax}년 문항 예상 연결 없음', qt[:60]))   # 최신 해 문항은 교수와 상관없이(RULES 11)
    # 예상 = 기출(이미 나온 문제)인데 b=에 없음 · '미출제' 모순
    jbn = {q: NORM(t)[:90] for q, t in qtext.items() if len(NORM(t)) >= 16}
    for i, x in enumerate(P['preds']):
        if x.get('x'): continue
        m = re.search(r'class="pq"[^>]*>(.*?)</div>', x['html'], re.S); pq = NORM(TXT(m.group(1)) if m else '')[:90]
        if len(pq) >= 16:
            for q, t in jbn.items():
                if difflib.SequenceMatcher(None, pq, t).ratio() >= 0.86 and q not in (x.get('b') or []):
                    out['x'].append((f'예상 {x["k"]} #{i}', f'예상 = 기출 {q} 인데 관련 기출(b=)에 없음', TXT(m.group(1))[:60]))
        if '미출제' in (x.get('t') or '') and x.get('b'): out['w'].append((f'예상 {x["k"]} #{i}', f"t '미출제'인데 b={','.join(x['b'])}", ''))
    return out, ymax
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('sids', nargs='*'); ap.add_argument('--md'); ap.add_argument('--year', type=int); a = ap.parse_args()
    tot = 0; md = []
    for SID in [s.upper() for s in a.sids] or SIDS:
        o, ym = audit(SID, a.year); tot += len(o['x'])
        print(f'{SID}: ✗ {len(o["x"])} · △ {len(o["w"])} (최근 해 {ym})')
        for q, k, t in o['x']: print(f'  ✗ {q} {k} — {t}')
        md.append(f'## {SID} ✗ {len(o["x"])} · △ {len(o["w"])}')
        md += [f'- ✗ {q} · {k} · {t}' for q, k, t in o['x']] + [f'- △ {q} · {k} · {t}' for q, k, t in o['w']]
    if a.md: os.makedirs(os.path.dirname(a.md), exist_ok=True); open(a.md, 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('RESULT', 'PASS' if not tot else f'FAIL {tot}'); return 1 if tot else 0
if __name__ == '__main__': sys.exit(main())
