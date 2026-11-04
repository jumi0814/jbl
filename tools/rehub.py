"""허브만 다시 만들기 — 강의자료·JB 원본(materials/·jb/·work/)이 없는 환경(클라우드 세션 등)에서 허브 코드(shell.html)만 고쳤을 때 쓴다.
지금 <분기 docs>/packs/<SID>.js(커밋된 팩)를 그대로 두고, 허브 코드 판(BUILD = shell.html의 md5 앞 8자)만 모든 팩에 다시 박은 뒤
<분기 docs>/index.html을 build4와 똑같은 방법으로 다시 쓴다(READY·PV·PSZ·QCFG — tools/quarters.fill_index). 결과는 그 분기 과목 build4를 모두 돌린 것과 글자까지 같다.
11-04 분기: 기본 = 보관(frozen)이 아닌 분기 전부(tools/quarters.json).
  python tools/rehub.py                  # 살아 있는 분기 전부
  python tools/rehub.py --q 4q           # 그 분기만
  python tools/rehub.py --check          # 지금 docs가 shell.html과 맞는지만 확인(다르면 종료 코드 1)
  python tools/rehub.py --site work/_tmp/qsite   # 전환 뒤 모양(4q = 뿌리, 3q = 3q/) 미리 보기 사이트 — 분리 시험(tests4/q_isolation)용
  python tools/rehub.py --q 3q --stage   # 보관 분기를 지금 shell로 스테이징(<stage>: 팩 본문은 복사·BUILD 다시 박음, 그림·lx·넘버링은 링크) — 3Q 회귀 테스트용(배포 안 함)
주의: 원고(lec_*.txt·annot·tables·pred)나 build4.py·lecparse.py·reflow.py·trend.py를 고친 것은 팩 내용이 바뀌어야 하므로 이 도구로는 반영되지 않는다 —
강의자료·JB 원본이 있는 컴퓨터에서 sh tools/build_all.sh로 다시 빌드해야 한다."""
import os, sys, re, json, hashlib, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J, quarters as QS
_h8 = lambda t: hashlib.md5(t.encode('utf-8')).hexdigest()[:8]
js = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')      # build4.py와 같은 직렬화
HEAD = re.compile(r"^window\.JBLHUB&&!JBLHUB\.build&&location\.search\.indexOf\('v=([0-9a-f]{8}|dev)'\)<0&&/\^https\?:/\.test\(location\.protocol\)&&location\.replace\(location\.pathname\+'\?v=([0-9a-f]{8}|dev)'\+location\.hash\);JBLHUB\.register\(")

def restamp(t, BUILD, s):
    m = HEAD.match(t)
    if not m or m.group(1) != m.group(2): sys.exit(f'{s}.js 머리 형식이 build4 출력과 다름 — 원본이 있는 곳에서 build_all로 다시 빌드할 것')
    old = m.group(1); body = t[m.end():]
    nb = body.replace(f'"build": "{old}"', f'"build": "{BUILD}"', 1)
    if old != BUILD and nb == body: sys.exit(f'{s}.js 안에서 "build": "{old}"를 찾지 못함')
    return t[:m.start(1)] + BUILD + t[m.end(1):m.start(2)] + BUILD + t[m.end(2):m.end()] + nb

def _link(src, dst):
    """스테이징 링크 — 없거나 다른 곳(전환 전 docs/packs 등 옛 자리)을 가리키면 새로(11-04 전환 뒤 옛 링크가 남아 그림 404)"""
    if os.path.islink(dst):
        if os.readlink(dst) == src: return
        os.remove(dst)
    elif os.path.lexists(dst): return
    os.symlink(src, dst)

def one(q, check=False, out=None, src=None, layout=None):
    """분기 q의 허브를 out(기본 = 그 분기 docs)에 — src = 팩을 읽을 곳(스테이징이면 원래 docs)"""
    shell = open(os.path.join(J.TOOLS, 'cons', 'shell.html'), encoding='utf-8').read()
    BUILD = _h8(shell); D = out or QS.docs_dir(q); S0 = src or D; bad = []
    P = os.path.join(D, 'packs'); P0 = os.path.join(S0, 'packs'); os.makedirs(P, exist_ok=True)
    if S0 != D:   # 스테이징 — 원래 팩 폴더의 그림·lx·호환 파일은 링크, 본문 팩은 복사해 BUILD만 바꿈 · 넘버링 모듈·앱 아이콘도 링크
        for f in os.listdir(P0):
            dst = os.path.join(P, f)
            if re.fullmatch(r'[A-Z0-9]+\.js', f): continue
            _link(os.path.join(P0, f), dst)
        for f in ('num', 'icon-192.png', 'icon-512.png'):
            if os.path.exists(os.path.join(S0, f)): _link(os.path.join(S0, f), os.path.join(D, f))
    for s in QS.sids(q):
        f0 = os.path.join(P0, s + '.js'); f = os.path.join(P, s + '.js')
        if not os.path.exists(f0): continue
        t = open(f0, encoding='utf-8').read(); new = restamp(t, BUILD, s)
        cur = open(f, encoding='utf-8').read() if os.path.exists(f) else ''
        if new != cur:
            bad.append(s)
            if not check: open(f, 'w', encoding='utf-8').write(new)
    READY = [x for x in QS.sids(q) if os.path.exists(os.path.join(P, x + '.js'))]
    PV = {x: _h8(open(os.path.join(P, x + '.js'), encoding='utf-8').read()) for x in READY}
    PSZ = {x: round(os.path.getsize(os.path.join(P, x + '.js')) / 1e6, 1) for x in READY}
    idx = QS.fill_index(shell, q, READY, PV, PSZ, BUILD, docs=(D if layout else QS.docs_dir(q) if S0 != D else D), jsf=js, layout=layout)
    fi = os.path.join(D, 'index.html'); cur = open(fi, encoding='utf-8').read() if os.path.exists(fi) else ''
    if cur != idx:
        bad.append('index.html')
        if not check: open(fi, 'w', encoding='utf-8').write(idx)
    for n in (192, 512):   # 앱 아이콘(없거나 다를 때만 — 링크면 그대로)
        fp = os.path.join(D, f'icon-{n}.png')
        if os.path.islink(fp): continue
        b = QS.icon_png(n)
        if not os.path.exists(fp) or open(fp, 'rb').read() != b:
            bad.append(f'icon-{n}')
            if not check: open(fp, 'wb').write(b)
    man = QS.manifest(q); fm = os.path.join(D, 'manifest.webmanifest')
    if not os.path.exists(fm) or open(fm, 'rb').read() != man:
        bad.append('manifest')
        if not check: open(fm, 'wb').write(man)
    return BUILD, bad, READY

def main(a):
    check = '--check' in a; stage = '--stage' in a
    qs = [a[a.index('--q') + 1]] if '--q' in a else QS.live()
    ok = True
    if '--site' in a:   # 전환 뒤 모양 미리 보기(배포 안 함) — 분기마다 cutover 자리에, 팩은 지금 자리에서(본문 복사·그림 링크)
        site = os.path.abspath(a[a.index('--site') + 1]); L = {q: QS.cutover_dir(q, site) for q in QS.QS}
        for q in QS.QS:
            B, bad, R = one(q, out=L[q], src=QS.docs_dir(q), layout=L); print(f'rehub --site {q} → {os.path.relpath(L[q], J.ROOT)}: 팩 {", ".join(R) or "없음"}')
        return True
    for q in qs:
        if stage:
            B, bad, R = one(q, check, out=QS.stage_dir(q), src=QS.docs_dir(q))
        else:
            if QS.frozen(q): print(f'rehub {q}: 보관(frozen) — 건너뜀(스테이징은 --stage)'); continue
            if not os.path.isdir(QS.docs_dir(q)) and QS.sids(q): print(f'rehub {q}: docs 폴더 없음 — 건너뜀'); continue
            B, bad, R = one(q, check)
        if check:
            print(f'rehub check {q}:', 'OK — docs가 shell.html과 맞음' if not bad else '다름 ' + ', '.join(bad)); ok = ok and not bad
        else:
            print(f'rehub {q}{" (스테이징 " + os.path.relpath(QS.stage_dir(q), J.ROOT) + ")" if stage else ""}: BUILD {B} · 바꾼 파일 {", ".join(bad) or "없음"} · 팩 {", ".join(R) or "없음"}')
    return ok

if __name__ == '__main__':
    sys.exit(0 if main(sys.argv[1:]) else 1)
