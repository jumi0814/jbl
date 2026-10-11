"""넘버링 제작 스킬(.claude/skills/jbl-numbering) 시스템 검증 — 이야기 품질이 아니라 주고받기·보존·보호·이어하기.
A. 도구(nb.py) 단독: 시작(보호 판정: story 있음·s0≠0) · 보호 문제 저장 거부 · 괄호 원문 검사·검수 기록 필수 · 보류 분리 · 새 프로세스로 이어하기 · 체크포인트 → 다른 세션 복원 · 결과 = 통과만·id/q/s0 원본 그대로 · 고친 결과 거부 · 사용자 거절 → 다시 todo · --revise
B. 실제 JBL 왕복: 내 넘버링에서 내보내기(파일 받기) → 도구 → 채팅 코드 블록째 붙여 넣기 → 미리 보기(새 스토리 미리 고름 · 내보낸 뒤 JBL에서 쓴 스토리 = 충돌로 안 고름 · 기존 사용자 스토리 문제는 결과에 없음) → 적용 → 문제·답안·출처·연도 그대로, 사용자 스토리 그대로
글은 모두 '[테스트]' 표시 — 실제 넘버링이 아님."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import asyncio, json, os, re, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(J.ROOT) if hasattr(J, 'ROOT') else Path(__file__).resolve().parents[2]
NB = ROOT / '.claude' / 'skills' / 'jbl-numbering' / 'scripts' / 'nb.py'
PY = str(ROOT / '.venv' / 'bin' / 'python')
TMP = Path(tempfile.mkdtemp(prefix='nbtest_'))
ENV = dict(os.environ, JBL_NB_HOME=str(TMP / 'home'))
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def nb(*args, expect=0):
    r = subprocess.run([PY, '-I', str(NB), *args], capture_output=True, text=True, env=ENV)
    out = r.stdout + r.stderr
    if expect == 0 and r.returncode != 0: print(out[-800:])
    return r.returncode, out
def wr(name, txt):
    p = TMP / name; p.write_text(txt, encoding='utf-8'); return str(p)
REV = 'G1 자연성: 통과\nG2 복원: 1 단서→항목 · 2 단서→항목 · 3 단서→항목 (테스트)\nG3~G8: 통과(테스트)'
REV1 = 'G1 자연성: 통과\nG2 복원: 단서→항목 (테스트)\nG3~G8: 통과(테스트)'

def part_a():
    print('A. 도구 단독')
    src = {"format": "jbl-numbering", "v": 1, "sid": "TEST", "subject": "시험과목", "batch": "b1", "part": "1/1", "n": 4, "rules": ["x"],
           "lecs": [{"lec": "강의1", "items": [
               {"id": "q1", "q": "1. 두개골 조기 유합 증후군을 쓰시오", "a": "1. Crouzon\n2. Apert", "story": "", "s0": "0"},
               {"id": "q2", "q": "2. 다른 문제", "a": "1) Alpha\n2) Beta\n3) Gamma", "story": "", "s0": "0"},
               {"id": "q3", "q": "3. 내가 쓴 스토리가 있는 문제", "a": "Delta", "story": "내 스토리", "s0": "abc12"},
               {"id": "q4", "q": "4. 스토리를 빼고 내보낸 문제", "a": "Epsilon", "story": "", "s0": "zz9"}]}]}
    sp = wr('src.json', json.dumps(src, ensure_ascii=False))
    rc, o = nb('start', sp, '--name', 't1'); ok(rc == 0 and 'todo) 2' in o and 'keep — 이미 스토리 있음) 2' in o, '시작 — todo 2 · 보호 2(story 있음 + s0≠0)')
    rc, o = nb('save', 't1', 'q3', '--status', 'pass', '--story', '[테스트] 장면(Delta)', '--review', REV, expect=1); ok(rc != 0 and '보호' in o, '보호 문제 저장 거부')
    rc, o = nb('save', 't1', 'q1', '--status', 'pass', '--story', '[테스트] 크루즈(Crouzon) 타고 갔어', '--review', 'G1만', expect=1); ok(rc != 0 and 'G2' in o, '검수 기록(G2) 없으면 통과 저장 거부')
    rc, o = nb('save', 't1', 'q1', '--status', 'pass', '--story', '[테스트] 크루즈(Crouzon) 타고 가다 앞에(Apert) 멈췄어', '--review', REV1, expect=1); ok(rc != 0 and '짝' in o, 'G2 줄의 단서→항목 짝이 괄호 수보다 적으면 거부')
    rc, o = nb('save', 't1', 'q1', '--status', 'pass', '--story', '[테스트] 크루즈(크루존 증후군) 타고 앞에(Apert)', '--review', REV, expect=1); ok(rc != 0 and '정답 원문' in o, '괄호가 정답 원문에 없으면 거부(번역 금지)')
    rc, o = nb('save', 't1', 'q1', '--status', 'pass', '--story', '[테스트] 크루즈(Crouzon) 타고 가다 앞에(Apert) 멈췄어', '--review', REV); ok(rc == 0 and '통과 저장' in o and '크루즈 타고 가다 앞에 멈췄어' in o, '통과 저장 + 괄호 뺀 글 보여 줌')
    rc, o = nb('save', 't1', 'q2', '--status', 'hold', '--story', '[테스트] 최선안(Alpha)', expect=1); ok(rc != 0, '보류는 이유 필수')
    rc, o = nb('save', 't1', 'q2', '--status', 'hold', '--story', '[테스트] 최선안(Alpha)', '--review', 'G2 — Gamma 단서 없음'); ok(rc == 0, '보류 저장')
    rc, o = nb('status', 't1'); ok('통과(pass) 1' in o and '보류(hold) 1' in o and 'Gamma 단서 없음' in o, '새 프로세스로 이어하기 — 상태 그대로')
    rc, o = nb('next', 't1'); ok('제작할 문제가 없어요' in o, '남은 todo 0(보호 문제는 내지 않음)')
    rc, o = nb('checkpoint', 't1', '--out', str(TMP / 'cp.json')); rc2, o2 = nb('start', '--from', str(TMP / 'cp.json'), '--name', 't1b'); rc3, o3 = nb('status', 't1b')
    ok(rc == 0 and rc2 == 0 and '통과(pass) 1' in o3 and '보류(hold) 1' in o3, '체크포인트 → 다른 세션 복원')
    rc, o = nb('export', 't1', expect=1); ok(rc != 0 and '블라인드' in o, '독립 블라인드 검수 전 통과본은 내지 않음')
    rc, o = nb('blind', 't1'); ok('크루즈 타고 가다 앞에 멈췄어' in o and 'Crouzon' not in o and 'Apert' not in o, 'blind 출력 = 문제 + 괄호 뺀 이야기(정답 없음)')
    rc, o = nb('blindres', 't1', 'q1', '--ok', '--note', '[테스트] 2/2'); rc2, o2 = nb('blind', 't1'); ok(rc == 0 and '보여 줄 통과 스토리가 없어요' in o2, '블라인드 통과 기록 · 같은 이야기를 다시 보이지 않음')
    outp = TMP / 'out.json'; rc, o = nb('export', 't1', '--out', str(outp), '--print')
    out = json.loads(outp.read_text(encoding='utf-8')); its = [it for g in out['lecs'] for it in g['items']]
    ok(rc == 0 and [it['id'] for it in its] == ['q1'] and its[0]['q'] == src['lecs'][0]['items'][0]['q'] and its[0]['s0'] == '0' and 'a' not in its[0] and out['format'] == 'jbl-numbering' and out['sid'] == 'TEST', '결과 = 통과만 · id/q/s0 원본 그대로 · 답안 칸 없음')
    ok('```' not in o and '{"format":"jbl-numbering"' in o, '채팅 붙여 넣기용 JSON 출력')
    rc, o = nb('verify', 't1', str(outp)); ok(rc == 0, '결과 확인 통과')
    bad = json.loads(outp.read_text(encoding='utf-8')); bad['lecs'][0]['items'][0]['q'] += ' '; bp = wr('bad.json', json.dumps(bad, ensure_ascii=False))
    rc, o = nb('verify', 't1', bp, expect=1); ok(rc != 0 and 'q 또는 s0' in o, '원본 q를 바꾼 결과는 거부')
    rc, o = nb('feedback', 't1', 'q1', '--verdict', 'reject', '--text', '[테스트] 별로야'); rc2, o2 = nb('export', 't1', expect=1)
    ok(rc == 0 and rc2 != 0, '사용자 거절 → 다시 todo · 결과에서 빠짐')
    rc, o = nb('start', sp, '--name', 't2', '--revise', 'q3'); ok(rc == 0 and 'todo) 3' in o and '고치기 허락받은 기존 스토리: q3' in o, '--revise로 허락한 기존 스토리만 다시 엶')
    rc, o = nb('start', sp, '--name', 't1', expect=1); ok(rc != 0 and '이미 있는 세션' in o, '같은 이름 세션 덮어쓰기 막음')
    rc, o = nb('start', sp, '--name', 't1', '--force'); ok(rc == 0 and '덮기 전 기록을 남겼어요' in o and list((TMP / 'home' / 't1').glob('state.bak.*.json')), '--force는 덮기 전 기록을 남김')
    rc, o = nb('save', 't2', 'q2', '--status', 'pass', '--story', '[테스트] 알파(Alpha) 베타(Beta) 감마(Gamma) 끝', '--review', REV); ok('목록꼴' in o, '괄호만 늘어놓은 목록꼴 경고')
    rc, o = nb('blindres', 't2', 'q2', '--fail', '--note', '[테스트] 감마 안 떠오름'); rc2, o2 = nb('save', 't2', 'q2', '--status', 'pass', '--story', '[테스트] 알파(Alpha) 베타(Beta) 감마(Gamma) 끝', '--review', REV, expect=1)
    ok(rc == 0 and rc2 != 0 and '전제부터 새로' in o2, '블라인드 실패 → 다시 todo · 같은 글은 다시 통과 저장 안 됨')

async def part_b():
    print('B. 실제 JBL 왕복')
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1366, 'height': 900}, accept_downloads=True); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(J.HUB_URL + '#/'); await pg.wait_for_timeout(2500)
        await pg.evaluate("(()=>{for(const k of Object.keys(localStorage))if(k.indexOf('jblhub.v1.num.')===0)localStorage.removeItem(k);})()")
        await pg.evaluate("location.hash='#/_num/CONS'"); await pg.wait_for_timeout(3500)
        await pg.click('.nm-side [data-act=imp]'); await pg.wait_for_timeout(700); await pg.click('[data-ib=flt]'); await pg.wait_for_timeout(400); await pg.click('[data-cf2=ok]'); await pg.wait_for_timeout(1200); await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(500)
        ids = await pg.evaluate("[...document.querySelectorAll('.nm-it')].slice(0,4).map(a=>a.dataset.id)")
        # 사용자 스토리(내보내기 전) — ids[1]
        await pg.evaluate("document.querySelectorAll('.nm-it')[1].querySelector('.nm-s .nm-c').scrollIntoView({block:'center'})")
        await pg.locator('.nm-it').nth(1).locator('.nm-s .nm-c').click(); await pg.wait_for_timeout(200); await pg.keyboard.type('[테스트] 사용자가 쓴 스토리'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(900)
        LS = "(k=>JSON.parse(localStorage.getItem('jblhub.v1.'+k)))"
        before = {i: await pg.evaluate(f"{LS}('num.i.CONS.{i}')") for i in ids}
        # 내보내기: 모든 상태 · 나누지 않음 → 파일 받기
        await pg.click('.nm-side [data-act=aiout]'); await pg.wait_for_timeout(500)
        await pg.select_option('[data-xo=st]', ''); await pg.select_option('[data-xo=chunk]', '0'); await pg.wait_for_timeout(300)
        async with pg.expect_download() as dl:
            await pg.click('[data-xget="0"]')
        d = await dl.value; ep = TMP / 'export.json'; await d.save_as(str(ep)); await pg.click('.nm-ov [data-x]'); await pg.wait_for_timeout(300)
        rc, o = nb('start', str(ep), '--name', 'web'); ok(rc == 0 and 'keep — 이미 스토리 있음) 1' in o, f'JBL 내보내기 파일 그대로 시작 · 사용자 스토리 문제 1개 보호 ({o.splitlines()[1] if len(o.splitlines()) > 1 else o[:80]})')
        src = json.loads(ep.read_text(encoding='utf-8')); S = {it['id']: it for g in src['lecs'] for it in g['items']}
        def kw(a):
            m = re.search(r'[A-Za-z][A-Za-z\-]{3,}', a) or re.search(r'[가-힣]{2,}', a); return m.group(0)
        for i in (ids[0], ids[2], ids[3]):
            k = kw(S[i]['a']); rc, o = nb('save', 'web', i, '--status', 'pass', '--story', f'[테스트] 그 장면에서 떠오른 말({k})이 이어졌어', '--review', REV)
            ok(rc == 0, f'{i} 테스트 통과 저장(괄호 {k})')
        rc, o = nb('blindres', 'web', ','.join((ids[0], ids[2], ids[3])), '--ok', '--note', '[테스트]')
        rc, o = nb('export', 'web', '--print'); txt = o.split('-----\n', 1)[1] if '-----\n' in o else ''
        ok(rc == 0 and txt.strip().startswith('{'), '결과 JSON(붙여 넣기용) 만듦')
        # 내보낸 뒤 JBL에서 ids[2]에 스토리를 씀 → 가져오기 때 충돌이어야
        await pg.evaluate("document.querySelectorAll('.nm-it')[2].querySelector('.nm-s .nm-c').scrollIntoView({block:'center'})")
        await pg.locator('.nm-it').nth(2).locator('.nm-s .nm-c').click(); await pg.wait_for_timeout(200); await pg.keyboard.type('[테스트] 내보낸 뒤 쓴 스토리'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(900)
        mid2 = await pg.evaluate(f"{LS}('num.i.CONS.{ids[2]}')")
        # 채팅에서 코드 블록째 복사해 붙여 넣기
        await pg.click('.nm-side [data-act=aiin]'); await pg.wait_for_timeout(400)
        await pg.fill('[data-ai=txt]', '```json\n' + txt.strip() + '\n```'); await pg.click('[data-ai=go]'); await pg.wait_for_timeout(800)
        rows = await pg.evaluate("[...document.querySelectorAll('.nm-airow')].map(r=>({k:r.dataset.k,on:r.querySelector('[data-ack]').checked,q:r.querySelector('.q').textContent.slice(0,30)}))")
        ks = [r['k'] for r in rows]
        ok(len(rows) == 3 and ks.count('new') == 2 and ks.count('cf') == 1 and all(r['on'] == (r['k'] == 'new') for r in rows), f"미리 보기 — 새 스토리 2(미리 고름) · 충돌 1(안 고름) · 사용자 스토리 문제는 결과에 없음 {ks}")
        await pg.click('[data-aapply=new]'); await pg.wait_for_timeout(900)
        after = {i: await pg.evaluate(f"{LS}('num.i.CONS.{i}')") for i in ids}
        keep = lambda r: {k: v for k, v in (r or {}).items() if k not in ('st', 'prev', 'u')}
        ok(all('[테스트] 그 장면' in (after[i] or {}).get('st', '') for i in (ids[0], ids[3])), '새 스토리 2개 적용')
        ok(all(keep(after[i]) == keep(before[i]) for i in (ids[0], ids[3])) and after[ids[0]].get('q') == before[ids[0]].get('q'), '문제·답안·출처·연도 등 원본 칸은 그대로(스토리만 바뀜)')
        ok(after[ids[1]] == before[ids[1]], '내보내기 전 사용자 스토리 문제 그대로')
        ok(after[ids[2]] == mid2 and '내보낸 뒤 쓴 스토리' in after[ids[2]]['st'], '내보낸 뒤 쓴 사용자 스토리는 덮어쓰지 않음(충돌)')
        await ctx.close(); await b.close()
        ok(not errs, f'pageerror 0 {errs[:2]}')

part_a()
asyncio.run(part_b())
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
