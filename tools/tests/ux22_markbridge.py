"""UX22 위치 잃은 표시 되찾기(10-20 사용자 "tmj smas 강의자료 업데이트하면서 기존의 메모가 날라간 것 같은데 확인해줄 수 있고 복구 가능한지 말해줘! 그리고 그렇게 다른 강의자료에서도 날라간 메모 있으면 복구 가능하면 복구해줘!")
- Kit.resolve 마지막 수단 bridge: 표시 글자가 블록에서 사라졌어도 저장된 앞뒤 글자(p·s)가 한 곳에서만 붙어 있으면 그 사이로('p.13' → 'p.10')
- 앞뒤가 두 곳 이상이면 안 붙임 · 사이 글자가 너무 길면(끼워 넣은 글) 안 붙임 · 표시 글자가 여러 곳에 있으면 사이 글자가 같을 때만
- 문맥이 맞는 보통 경우는 예전 그대로(exact 먼저)"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(J.HUB_URL + '#/'); pg.wait_for_timeout(2000)
    R = lambda t, o: pg.evaluate("([t,o])=>{const r=__h.Kit.resolve(t,o);return r?t.slice(r[0],r[1]):null}", [t, o])
    o = {'x': '13', 'i': 0, 'p': 'skin incision— p.', 's': ' 그림만 보고 이름 쓰기'}
    ok(R('Preauricular skin incision— p.10 그림만 보고 이름 쓰기 · 끝', o) == '10', "쪽 번호가 바뀐 자리(p.13 → p.10)로 되찾음")
    ok(R('Preauricular skin incision— p.13 그림만 보고 이름 쓰기', o) == '13', "글자가 그대로면 예전처럼 그 자리")
    ok(R('skin incision— p.10 그림만 보고 이름 쓰기 / skin incision— p.11 그림만 보고 이름 쓰기', o) is None, "앞뒤 문맥이 두 곳이면 붙이지 않음")
    ok(R('Preauricular skin incision— p.10 (25 자료 — 26에서 빠짐 · JB 짤 대비용) 그림만 보고 이름 쓰기', o) is None, "사이에 긴 글이 끼면 붙이지 않음")
    o2 = {'x': 'fascia상부', 'i': 0, 'p': 'deep masseteric ', 's': ' = temporoparietal'}
    ok(R('… deep masseteric fascia · 상부 = temporoparietal fascia', o2) == 'fascia · 상부', "띄어쓰기·구분 기호만 바뀐 자리")
    o3 = {'x': '슬라이드', 'i': 1, 'p': 'joint capsule(', 's': ' 답을 따름).'}
    ok(R('슬라이드 p.7 · 슬라이드 p.8 · joint capsule(슬라이드 답을 따름).', o3) == '슬라이드', "글자가 여러 곳 + 앞뒤 그대로 = 그 자리")
    ok(R('슬라이드 p.7 · 슬라이드 p.8 · joint capsule(그 답을 따름).', o3) is None, "글자가 여러 곳에 남아 있는데 그 자리 글자가 바뀌면 다른 곳에 붙이지 않음")
    ok(R('짧은 글', {'x': '없는말', 'i': 0}) is None, "문맥 없는 옛 표시는 그대로 위치 잃음")
    ok(not errs, f"pageerror 0 {errs[:2]}")
    b.close()
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
