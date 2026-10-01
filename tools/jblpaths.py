"""저장소 기준 경로 — 모든 과목 파이프라인 공통.
과목 작업 폴더 = work/<SID>/ · JB 추출 = work/jb/<SID>_20xx/ (tools/jbx.py) · 출력 = docs/ (허브 docs/index.html, 팩 docs/packs/)"""
import os, re, json
TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
WORK = os.path.join(ROOT, 'work')
DOCS = os.path.join(ROOT, 'docs')
JBX = os.path.join(WORK, 'jb') + '/'          # f'{JBX}{SID}_20{ed}/{i}.txt'
HUB_URL = 'file://' + os.path.join(DOCS, 'index.html')   # 테스트·감사 스크립트가 여는 허브
TMP = os.path.join(WORK, '_tmp'); os.makedirs(TMP, exist_ok=True)   # 스크린샷 등 임시 파일
def work(sid, *p):
    d = os.path.join(WORK, sid); os.makedirs(d, exist_ok=True)
    return os.path.join(d, *p)
def _load_js(path):
    t = open(path, encoding='utf-8').read()
    return json.loads(t[t.index('{'):t.rindex('}') + 1])
def prev_images(sid):
    """지금 docs/packs/에 올라가 있는 <SID>.img.*.js의 강의 이미지 {키-쪽: dataURI}.
    강의자료 원본(materials/, work/)이 없는 환경에서 재빌드해도 이미지가 빠지지 않게 하는 대체용."""
    out = {}; d = os.path.join(DOCS, 'packs')
    if not os.path.isdir(d): return out
    for f in os.listdir(d):
        if f.startswith(sid + '.img.') and f.endswith('.js') and not f.startswith(sid + '.img.jb'):   # JB 원본 청크(jb·jb23·jb24·jb25)는 제외
            out.update(_load_js(os.path.join(d, f)).get('lec', {}))
    return out
def prev_crops(sid, crops):
    """지금 docs/packs/<SID>.js 문항 카드에 박힌 JB 그림 조각 {조각키: dataURI} (crops 폴더가 없을 때 대체용)."""
    p = os.path.join(DOCS, 'packs', sid + '.js')
    if not os.path.exists(p): return {}
    cards = _load_js(p).get('cards', {}); out = {}
    for cid, kinds in crops.items():
        h = cards.get(cid, '')
        for kind, alt in (('q', 'JB 그림'), ('a', 'JB 그림(답)')):
            srcs = re.findall(r'<img class="fig" loading="lazy" src="([^"]+)" alt="%s">' % re.escape(alt), h)
            for k, s in zip(kinds.get(kind, []), srcs): out[k] = s
    return out
def prev_jb(sid):
    """지금 docs/packs/<SID>.img.jb.js의 JB 원본 쪽 이미지 {판-쪽: dataURI} — 같은 JB PDF를 다시 렌더해 파일만 바뀌는 것을 막는 용도."""
    p = os.path.join(DOCS, 'packs', sid + '.img.jb.js')
    return _load_js(p).get('jb', {}) if os.path.exists(p) else {}

_PJ = {}
def prev_jb_pages(sid):
    """지금 docs/packs/<SID>.img.jb23·jb24·jb25.js에 든 JB 원본 쪽 이미지 {판-쪽: dataURI}.
    JB 쪽 이미지 파일(work/jb/<SID>_20xx/N.jpeg)이 없는 환경(클라우드 세션 — 텍스트만 풀어 둠)에서 assemble.py가 그대로 다시 쓰는 대체용."""
    if sid not in _PJ:
        out = {}; d = os.path.join(DOCS, 'packs')
        for f in (sorted(os.listdir(d)) if os.path.isdir(d) else []):
            if re.fullmatch(re.escape(sid) + r'\.img\.jb\d+\.js', f): out.update(_load_js(os.path.join(d, f)).get('jb', {}))
        _PJ[sid] = out
    return _PJ[sid]
