"""과목명만 받았을 때: 사이트(docs/)의 JB 문제로 JBL '내 넘버링' 내보내기와 같은 JSON을 만든다.
빈 브라우저에서 내 넘버링 → 'JB에서 가져오기'(기본 '서술형·넘버링형만') → 'ChatGPT로 내보내기'(모든 상태 · 나누지 않음) → 파일.
사용자 브라우저의 스토리는 안 보이므로 전부 s0 "0" — 가져올 때 JBL이 이미 스토리 있는 문제를 '충돌'로 빼서 덮어쓰지 않는다.
쓰기: .venv/bin/python -I .claude/skills/jbl-numbering/scripts/site_export.py OMS1 [--out 파일] [--lec 강의이름 일부]"""
import argparse, asyncio, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'tools')); os.environ.setdefault('JBL_HTTP', '1')
import jblpaths as J


async def grab(sid, out):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1366, 'height': 900}, accept_downloads=True); pg = await ctx.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(J.HUB_URL + '#/'); await pg.wait_for_timeout(2500)
        await pg.evaluate(f"location.hash='#/_num/{sid}'"); await pg.wait_for_timeout(3500)
        await pg.click('.nm-side [data-act=imp]'); await pg.wait_for_timeout(700)
        await pg.click('[data-ib=flt]'); await pg.wait_for_timeout(400); await pg.click('[data-cf2=ok]'); await pg.wait_for_timeout(1500); await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(500)
        await pg.click('.nm-side [data-act=aiout]'); await pg.wait_for_timeout(500)
        await pg.select_option('[data-xo=st]', ''); await pg.select_option('[data-xo=chunk]', '0'); await pg.wait_for_timeout(300)
        async with pg.expect_download() as dl:
            await pg.click('[data-xget="0"]')
        d = await dl.value; await d.save_as(str(out)); await b.close()
        if errs: print('페이지 오류:', errs)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('sid'); ap.add_argument('--out'); ap.add_argument('--lec', help='강의 이름 일부(이 강의만 남김)')
    a = ap.parse_args(); sid = a.sid.upper()
    out = Path(a.out or ROOT / 'work' / 'numbering' / '_in' / f'{sid}_site.json'); out.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(grab(sid, out))
    d = json.loads(out.read_text(encoding='utf-8'))
    if a.lec:
        d['lecs'] = [g for g in d['lecs'] if a.lec in g['lec']]; d['n'] = sum(len(g['items']) for g in d['lecs'])
        out.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"{out} · {d.get('subject')} · 문제 {d['n']}")
    for g in d['lecs']: print(f"  {len(g['items']):3d}  {g['lec']}")


if __name__ == '__main__':
    main()
