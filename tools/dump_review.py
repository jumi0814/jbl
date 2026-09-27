"""검토·개선 작업용 덤프: docs/packs/<SID>.js(현재 빌드) → work/<SID>/review/
- questions.md : 문항마다 id·교수·연도·짤탈·연결 강의 + 화면에 보이는 그대로의 문제·JB 답·대조·주변부·다른 판본(텍스트)
- qids.json    : {id: {tier, prof, yrs, lk, v}} + 강의별 기출 목록 {강의키: [id…]}  (tools/check_lec.py가 씀)
- materials.md : 강의 키 → 쪽 이미지 폴더 → 강의자료 파일·쪽수, 추출 위치(t/ 텍스트층, o/ OCR, i/ 쪽 이미지)
사용: .venv/bin/python tools/dump_review.py [SID ...]"""
import os, sys, re, json, html, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J

def load_pack(sid):
    t = open(os.path.join(J.DOCS, 'packs', sid + '.js'), encoding='utf-8').read()
    return json.loads(t[t.index('{'):t.rindex('}') + 1])
def text(h):
    h = re.sub(r'<img[^>]*>', '[그림]', h)
    h = re.sub(r'</(div|li|h5|section|summary|tr|p)>', '\n', h); h = re.sub(r'<br\s*/?>', '\n', h)
    h = re.sub(r'<(td|th)[^>]*>', ' | ', h)
    h = html.unescape(re.sub(r'<[^>]+>', '', h))
    return re.sub(r'\n\s*\n+', '\n', h).strip()
def subject(sid):
    p = os.path.join(J.TOOLS, sid.lower(), 'subject.py')
    sp = importlib.util.spec_from_file_location('subject_' + sid, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

def run(sid):
    p = load_pack(sid); out = J.work(sid, 'review'); os.makedirs(out, exist_ok=True); S = subject(sid)
    q = {}
    for cid, h in p['cards'].items():
        m = re.search(r'<article[^>]*>', h).group(0); a = dict(re.findall(r'data-([a-z0-9]+)="([^"]*)"', m))
        yb = re.search(r'<span class="ybadge[^"]*"[^>]*><b>([^<]*)</b>', h)
        q[cid] = {'tier': a.get('tier'), 'prof': html.unescape(a.get('prof', '')), 'lk': a.get('lec', ''), 'v': a.get('v', ''),
                  'yrs': [int(y) % 100 for y in re.findall(r'20\d\d', yb.group(1))] if yb else []}
    bylec = {L['k']: L['jb'] for L in p['lect']}
    json.dump({'q': q, 'bylec': bylec, 'order': p['order']}, open(f'{out}/qids.json', 'w'), ensure_ascii=False, indent=0)
    with open(f'{out}/questions.md', 'w', encoding='utf-8') as f:
        f.write(f'# {sid} JB 문항 {len(p["order"])}개 — 현재 사이트에 보이는 그대로(텍스트)\n')
        f.write('강의별 연결: ' + ' / '.join(f'{k}: {",".join(v)}' for k, v in bylec.items()) + '\n\n')
        for cid in p['order']:
            x = q[cid]
            f.write(f'\n=== {cid} | tier {x["tier"]} | {x["prof"]} | 출제 {",".join(str(y) for y in x["yrs"])} | 연결 강의 {x["lk"] or "-"} | 대조 {x["v"]}\n')
            f.write(text(p['cards'][cid]) + '\n')
    idx = json.load(open(J.work(sid, 'mat', 'index.json'), encoding='utf-8')) if os.path.exists(J.work(sid, 'mat', 'index.json')) else {}
    lecdir = J.work(sid, 'lec')
    with open(f'{out}/materials.md', 'w', encoding='utf-8') as f:
        f.write(f'# {sid} 강의자료 추출 위치 (work/{sid}/mat/<파일id>/)\n- t/<쪽>.txt 텍스트층(+[주석] PDF 필기 주석) · o/<쪽>.txt OCR(텍스트층 150자 미만 쪽만) · i/<쪽>.jpg 쪽 이미지(폭 1100, Read 도구로 직접 볼 것)\n\n## 강의 키 → 쪽 이미지 폴더 → 파일\n')
        for k, (d, name) in S.LECMAP.items():
            path = S.lec_img_path(k, 1) if d else None; tgt = ''
            if path:
                dd = os.path.dirname(path)
                tgt = os.path.basename(os.path.dirname(os.path.realpath(dd))) if os.path.islink(dd) else '(폴더 없음 — 옛 이미지만 docs/에)'
            f.write(f'- {k}: {name} → 폴더 {d or "없음(텍스트 인용)"} → {tgt}\n')
        f.write('\n## 파일 목록\n')
        for fid_, v in idx.items(): f.write(f'- {fid_}/ : {v["file"]} — {v["pages"]}쪽 ({v["kind"]}, OCR {v.get("ocr", 0)}쪽)\n')
    print(sid, len(p['order']), '문항 →', os.path.relpath(out, J.ROOT))

if __name__ == '__main__':
    for sid in [a.upper() for a in sys.argv[1:]] or ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM']: run(sid)
