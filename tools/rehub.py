"""허브만 다시 만들기 — 강의자료·JB 원본(materials/·jb/·work/)이 없는 환경(클라우드 세션 등)에서 허브 코드(shell.html)만 고쳤을 때 쓴다.
지금 docs/packs/<SID>.js(커밋된 팩)를 그대로 두고, 허브 코드 판(BUILD = shell.html의 md5 앞 8자)만 모든 팩에 다시 박은 뒤
docs/index.html을 build4와 똑같은 방법으로 다시 쓴다(READY·PV·PSZ). 결과는 6과목 build4를 모두 돌린 것과 글자까지 같다(tools/cons/build4.py 끝부분과 같은 식).
  python tools/rehub.py           # tools/cons/shell.html 기준(먼저 tools/sync_common.py로 6과목 사본을 맞출 것)
  python tools/rehub.py --check   # 지금 docs가 shell.html과 맞는지만 확인(다르면 종료 코드 1)
주의: 원고(lec_*.txt·annot·tables·pred)나 build4.py·lecparse.py·reflow.py·trend.py를 고친 것은 팩 내용이 바뀌어야 하므로 이 도구로는 반영되지 않는다 —
강의자료·JB 원본이 있는 컴퓨터에서 sh tools/build_all.sh로 다시 빌드해야 한다."""
import os, sys, re, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J
SIDS = ['OMS1', 'CONS', 'IMPL', 'ANAT', 'GERI', 'PHARM', 'ESTH']
_h8 = lambda t: hashlib.md5(t.encode('utf-8')).hexdigest()[:8]
js = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')      # build4.py와 같은 직렬화
HEAD = re.compile(r"^window\.JBLHUB&&!JBLHUB\.build&&location\.search\.indexOf\('v=([0-9a-f]{8}|dev)'\)<0&&/\^https\?:/\.test\(location\.protocol\)&&location\.replace\(location\.pathname\+'\?v=([0-9a-f]{8}|dev)'\+location\.hash\);JBLHUB\.register\(")

def main(check=False):
    shell = open(os.path.join(J.TOOLS, 'cons', 'shell.html'), encoding='utf-8').read()
    BUILD = _h8(shell); P = os.path.join(J.DOCS, 'packs'); bad = []
    for s in SIDS:
        f = os.path.join(P, s + '.js')
        if not os.path.exists(f): continue
        t = open(f, encoding='utf-8').read(); m = HEAD.match(t)
        if not m or m.group(1) != m.group(2): sys.exit(f'{s}.js 머리 형식이 build4 출력과 다름 — 원본이 있는 곳에서 build_all로 다시 빌드할 것')
        old = m.group(1)
        body = t[m.end():]
        nb = body.replace(f'"build": "{old}"', f'"build": "{BUILD}"', 1)
        if old != BUILD and nb == body: sys.exit(f'{s}.js 안에서 "build": "{old}"를 찾지 못함')
        new = t[:m.start(1)] + BUILD + t[m.end(1):m.start(2)] + BUILD + t[m.end(2):m.end()] + nb
        if new != t:
            bad.append(s)
            if not check: open(f, 'w', encoding='utf-8').write(new)
    READY = [x for x in SIDS if os.path.exists(os.path.join(P, x + '.js'))]
    PV = {x: _h8(open(os.path.join(P, x + '.js'), encoding='utf-8').read()) for x in READY}
    PSZ = {x: round(sum(os.path.getsize(os.path.join(P, f)) for f in os.listdir(P) if f == x + '.js') / 1e6, 1) for x in READY}
    idx = shell.replace('<!--INLINE_PACKS-->', '').replace('null/*READY*/', js(READY)).replace('null/*PV*/', js(PV)).replace('null/*PSZ*/', js(PSZ)).replace("'dev'/*BUILD*/", js(BUILD))
    fi = os.path.join(J.DOCS, 'index.html'); cur = open(fi, encoding='utf-8').read() if os.path.exists(fi) else ''
    if cur != idx:
        bad.append('index.html')
        if not check: open(fi, 'w', encoding='utf-8').write(idx)
    if check:
        print('rehub check:', 'OK — docs가 shell.html과 맞음' if not bad else '다름 ' + ', '.join(bad)); return not bad
    print(f'rehub: BUILD {BUILD} · 바꾼 파일 {", ".join(bad) or "없음"} · 팩 {", ".join(READY)}'); return True

if __name__ == '__main__':
    sys.exit(0 if main('--check' in sys.argv) else 1)
