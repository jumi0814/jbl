"""넘버링 따기 — 첨부 Word(넘버링 자료)를 사이트 기본 자료(docs/num/seed*.js · docs/num/img/)로 (10-10)
읽는 방법은 허브 '파일 가져오기'와 같은 tools/num/docx.js를 크롬(playwright)에서 그대로 돌린다(따로 만든 파서 없음).
  .venv/bin/python -I tools/num/build_seed.py          # tools/num/seed_src.json의 Word 전부
원본 Word는 work/num/src/(커밋 안 함). 결과:
  docs/num/seed.js            과목 목록·개수(작음 — 넘버링 화면을 열 때만 읽음)
  docs/num/seed.<ID>.js       과목 문제(그 과목을 열 때만)
  docs/num/img/<해시>.webp    그림(화면에 보일 때만 받음)
  work/num/review_<ID>.md     검토 목록(사람이 볼 것)
고칠 것이 있으면 tools/num/seed_fix.json(줄 위치 → 고침, 이유)에 적는다 — 글자는 바꾸지 않고 칸만 옮김."""
import os, sys, json, base64, re, asyncio, hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jblpaths as J
from playwright.async_api import async_playwright

NUM = os.path.join(J.TOOLS, 'num'); OUT = os.path.join(J.DOCS, 'num'); IMG = os.path.join(OUT, 'img'); WK = os.path.join(J.WORK, 'num')
js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
TXT = lambda h: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h or '')).strip()

def apply_fix(items, fixes, sid):
    by = {it['pos']: it for it in items}; used = []
    for f in fixes:
        if f.get('doc') != sid: continue
        it = by.get(f['pos'])
        if not it: sys.exit(f'seed_fix: {sid} {f["pos"]} 줄이 없음')
        op = f['op']
        if op == 'shift':   # 정답 칸에 문제 · 암기법 칸에 답 → 문제 = 문제+정답 칸, 답 = 암기법 칸, 스토리 비움
            it['q'] = it['q'] + it['a']; it['a'] = it['st']; it['st'] = ''
            it['yrs'] = sorted(set(it['yrs']) | set(f.get('yrs', [])), reverse=True)
        elif op == 'years':
            it['yrs'] = sorted(set(it['yrs']) | set(f['yrs']), reverse=True)
        else: sys.exit('seed_fix: 모르는 op ' + op)
        it['rv'] = [r for r in it['rv'] if r['k'] != 'shift'] + [{'k': 'fix', 'm': f['why']}]
        used.append(f['pos'])
    return used

async def main():
    src = json.load(open(os.path.join(NUM, 'seed_src.json'), encoding='utf-8'))
    fixes = json.load(open(os.path.join(NUM, 'seed_fix.json'), encoding='utf-8'))
    os.makedirs(IMG, exist_ok=True); os.makedirs(WK, exist_ok=True)
    keep_img = set(); index = []
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.set_content('<!doctype html><meta charset="utf-8"><body></body>')
        await pg.add_script_tag(path=os.path.join(NUM, 'docx.js'))
        for S in src:
            f = os.path.join(J.ROOT, S['file'])
            if not os.path.exists(f): sys.exit(f'{S["id"]}: Word 원본이 없음 {f} — 맥/첨부에서 work/num/src/로 복사')
            b64 = base64.b64encode(open(f, 'rb').read()).decode()
            r = await pg.evaluate("""async b64 => { const s = atob(b64), u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i);
                return await JBLDOCX.parse(u.buffer, {img: 'id', maxW: 1100, q: 0.8}); }""", b64)
            sid = S['id']; items = r['items']
            used = apply_fix(items, fixes, sid)
            for h, im in r['images'].items():
                m = re.match(r'data:image/(\w+);base64,(.*)', im['d'])
                ext = {'jpeg': 'jpg'}.get(m.group(1), m.group(1)); fn = f'{h}.{ext}'
                open(os.path.join(IMG, fn), 'wb').write(base64.b64decode(m.group(2))); keep_img.add(fn)
                for it in items:
                    for k in ('q', 'a', 'st'): it[k] = it[k].replace(f'data-nimg="{h}"', f'data-nimg="{h}.{ext}"')
            lk = {}   # 강의 키 = 강의 이름 해시(문서에 강의가 끼어들어도 '강의 옮기기' 기록이 엉뚱한 강의로 가지 않게)
            for s_ in r['sections']:
                k0 = 'L' + hashlib.md5(re.sub(r'\s+', '', s_['title']).encode()).hexdigest()[:6]; k1 = k0; n = 2
                while k1 in lk.values(): k1 = f'{k0}-{n}'; n += 1
                lk[s_['k']] = k1
            for it in items: it['lec'] = lk.get(it['lec'], it['lec'])
            for s_ in r['sections']: s_['k'] = lk[s_['k']]
            lecs = [{'k': s['k'], 't': s['title'], 'raw': s['raw'], 'lab': s['lab'], 'prof': s['prof'], 'date': s['date']} for s in r['sections'] if s['n']]
            out = []; used_id = {}
            for i, it in enumerate(items):
                # id = 강의 이름 + 문제 글(띄어쓰기·꾸밈 빼고)의 해시 — Word를 다시 만들어 문제가 끼어들어도 작업본이 엉뚱한 문제에 붙지 않음(같은 글이 두 번이면 -2)
                lt = next((s['title'] for s in r['sections'] if s['k'] == it['lec']), '')
                h = hashlib.md5((re.sub(r'\s+', '', lt) + '|' + re.sub(r'\s+', '', TXT(it['q']))).encode()).hexdigest()[:8]
                n = used_id.get(h, 0) + 1; used_id[h] = n; sid8 = h if n == 1 else f'{h}-{n}'
                o = {'id': f'sd:{sid}:{sid8}', 'lec': it['lec'], 'q': it['q'], 'a': it['a'], 'st': it['st'], 'yrs': it['yrs'], 'tags': it['tags'], 'lab': it['lab'], 'pos': it['pos']}
                if it.get('note'): o['note'] = it['note']
                if it['rv']: o['rv'] = it['rv']
                out.append(o)
            meta = {'id': sid, 't': S['t'], 'short': S.get('short', S['t']), 'src': r['title'] or (r['sections'][0]['raw'] if r['sections'] else S['t']), 'file': S.get('label', ''), 'legend': r['legend'], 'layout': r['layout'], 'n': len(out)}
            body = {'meta': meta, 'lecs': lecs, 'items': out}
            open(os.path.join(OUT, f'seed.{sid}.js'), 'w', encoding='utf-8').write('window.JBLNUM_SEED=window.JBLNUM_SEED||{};JBLNUM_SEED[' + js(sid) + ']=' + js(body) + ';\n')
            index.append(dict(meta, v=hashlib.md5(js(body).encode()).hexdigest()[:8], lecs=len(lecs)))
            # 검토 목록
            L = [f'# {S["t"]} — Word 반영 검토 목록 ({r["title"]})', '', f'- 형식: {r["layout"]} · 강의 {len(lecs)} · 문제 {len(out)} · 그림 {len(r["images"])} · 고친 줄 {len(used)} · 문서 전체 알림 {len(r["flags"])}', '']
            for fl in r['flags']: L.append(f'- 문서: {fl["m"]}')
            L.append(''); L.append('| # | 강의 | 위치 | 문제(앞부분) | 연도 | 꼬리표 | 검토 |'); L.append('|---|---|---|---|---|---|---|')
            ln = {l['k']: l['t'] for l in lecs}
            for i, o in enumerate(out):
                rv = '; '.join(x['m'] + (' ⟨' + x['d'].replace('\n', ' / ') + '⟩' if x.get('d') else '') for x in o.get('rv', []))
                L.append(f'| {i + 1} | {ln.get(o["lec"], o["lec"])} | {o["pos"]} | {TXT(o["q"])[:70].replace("|", "/")} | {",".join(str(y) for y in o["yrs"])} | {",".join(o["tags"])} | {rv.replace("|", "/")} |')
            open(os.path.join(WK, f'review_{sid}.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
            print(f'{sid}: 강의 {len(lecs)} · 문제 {len(out)} · 그림 {len(r["images"])} · 검토 {sum(1 for o in out if o.get("rv"))} · 고침 {used} · 문서 알림 {[x["m"] for x in r["flags"]]}')
        await b.close()
        if errs: sys.exit('pageerror ' + '; '.join(errs[:3]))
    for fn in os.listdir(IMG):
        if fn not in keep_img: os.remove(os.path.join(IMG, fn))
    open(os.path.join(OUT, 'seed.js'), 'w', encoding='utf-8').write('window.JBLNUM_INDEX=' + js(index) + ';\n')
    print('seed.js:', [(x['id'], x['n']) for x in index], '그림', len(keep_img), '개', round(sum(os.path.getsize(os.path.join(IMG, f)) for f in keep_img) / 1e6, 2), 'MB')

asyncio.run(main())
