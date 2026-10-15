"""예상문제 덤프(개선 작업 전 기준본): docs/packs/<SID>.js의 예상문제 → work/<SID>/pred26/pred_before.{json,md}
- 문항마다 순번 i · 강의 k · data-aid(사용자 ✓·✗·★·넘버링 연결 키 — 문제를 고쳐 쓰면 pred.txt 머리에 `oid=<이 값>`) · 유형 · 관련 기출 · 문제·답(화면 글자)
- tools/<sid>/pred.txt 블록 순서와 같음(i = 파일 안 블록 순번, 0부터)
사용: .venv/bin/python tools/pred_dump.py <SID ...>"""
import os, sys, re, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J

def load_pack(sid):
    t = open(os.path.join(J.DOCS, 'packs', sid + '.js'), encoding='utf-8').read()
    return json.loads(t[t.index('{'):t.rindex('}') + 1])
def text(h):
    h = re.sub(r'<img[^>]*>', '[그림]', h); h = re.sub(r'</(div|li|h5|section|p)>', '\n', h); h = re.sub(r'<br\s*/?>', '\n', h)
    return re.sub(r'\n\s*\n+', '\n', html.unescape(re.sub(r'<[^>]+>', '', h))).strip()
def run(sid):
    p = load_pack(sid); out = []
    for i, x in enumerate(p.get('preds', [])):
        h = x['html']; a = re.search(r'data-aid="([^"]+)"', h).group(1)
        t = re.search(r'<span class="ybadge pr"><b>예상</b><i>([^<]*)</i>', h)
        rel = re.findall(r'data-go="([^"]+)"', h)
        q = re.search(r'<div class="pq">(.*?)</div><div class="acts">', h, re.S)
        an = re.search(r'<div class="pre2">(.*)</div></section>', h, re.S)
        out.append({'i': i, 'k': x['k'], 'aid': a, 't': html.unescape(t.group(1)) if t else '', 'b': rel, 'q': text(q.group(1)) if q else '', 'a': text(an.group(1)) if an else ''})
    d = J.work(sid, 'pred26'); os.makedirs(d, exist_ok=True)
    json.dump(out, open(os.path.join(d, 'pred_before.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(os.path.join(d, 'pred_before.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {sid} 예상문제 {len(out)}개 — 개선 전(사이트 그대로)\n')
        for r in out: f.write(f"\n=== #{r['i']} | {r['k']} | {r['t']} | 관련 {','.join(r['b']) or '-'} | aid={r['aid']}\nQ: {r['q']}\nA: {r['a']}\n")
    print(sid, len(out), '→', os.path.relpath(d, J.ROOT))
if __name__ == '__main__':
    for s in (sys.argv[1:] or ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']): run(s.upper())
