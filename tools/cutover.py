"""쿼터 전환(11-04 사용자 결정 1 — 'jumi0814.github.io/jbl/ = 4Q, 3Q는 /jbl/3q/ 보관') — 한 번만.
  .venv/bin/python tools/cutover.py --dry   # 할 일만 보기
  .venv/bin/python tools/cutover.py         # 실행(커밋은 따로 — 커밋 전 git diff -M --stat으로 이름 바꿈만인지 확인)
하는 일: ① docs/{index.html,manifest.webmanifest,icon-*.png,num,packs} → docs/3q/ (git mv — 파일 내용 그대로 = 저장소가 커지지 않음 · 3Q 기록은 같은 주소라 그대로 보임)
② 등록표: current = 새 쿼터 · 옛 쿼터 docs = docs/3q·frozen · 새 쿼터 docs = docs ③ 새 쿼터 허브를 docs/에(rehub — 앱 아이콘·manifest·넘버링 모듈 포함)
④ 옛 쿼터 index를 링크 들어간 판으로 한 번 다시(팩 BUILD가 같으면 팩은 그대로) — 그 뒤 옛 쿼터는 보관(build4·rehub가 쓰지 않음)"""
import os, sys, json, subprocess, shutil
TOOLS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(TOOLS); sys.path.insert(0, TOOLS)
REGF = os.path.join(TOOLS, 'quarters.json')
MOVE = ['index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'num', 'packs']
def main(dry):
    R = json.load(open(REGF, encoding='utf-8')); old = R['current']; new = [q for q in R['cutover'] if q != '_doc' and R['cutover'][q] == 'docs'][0]
    if old == new: sys.exit(f'이미 전환됨(current = {old})')
    dst = os.path.join(ROOT, R['cutover'][old])
    if os.path.exists(dst): sys.exit(f'{os.path.relpath(dst, ROOT)} 이미 있음')
    if subprocess.run(['git', '-C', ROOT, 'status', '--porcelain', 'docs'], capture_output=True, text=True).stdout.strip(): sys.exit('docs/에 커밋 안 된 변경이 있음 — 먼저 커밋')
    print(f'전환: {old} → {os.path.relpath(dst, ROOT)}/ (보관) · {new} → docs/ (지금 쿼터)')
    for f in MOVE: print('  git mv docs/%s %s/%s' % (f, os.path.relpath(dst, ROOT), f))
    if dry: return
    os.makedirs(dst)
    for f in MOVE:
        if os.path.exists(os.path.join(ROOT, 'docs', f)): subprocess.run(['git', '-C', ROOT, 'mv', f'docs/{f}', f'{os.path.relpath(dst, ROOT)}/{f}'], check=True)
    R['current'] = new; R['quarters'][old]['docs'] = R['cutover'][old]; R['quarters'][old]['frozen'] = True; R['quarters'][new]['docs'] = 'docs'
    import new_subject as NS; NS.reg_write(R)
    import importlib, quarters as QS; importlib.reload(QS)
    import rehub as RH; importlib.reload(RH)
    B, bad, rd = RH.one(old); print(f'  {old} 보관 허브 링크 넣어 다시: {", ".join(bad) or "바뀐 것 없음"}')
    B, bad, rd = RH.one(new); print(f'  {new} 허브: {", ".join(bad)} · 팩 {", ".join(rd) or "없음(자료 대기)"}')
    py = os.path.join(ROOT, '.venv', 'bin', 'python')
    src = os.path.join(dst, 'num')   # 넘버링 모듈·기본 자료(seed)는 보관 쿼터 것을 새 쿼터에도 복사(build_num이 이후 살아 있는 쿼터만 맞춤)
    if os.path.isdir(src) and not os.path.exists(os.path.join(ROOT, 'docs', 'num')): shutil.copytree(src, os.path.join(ROOT, 'docs', 'num'))
    subprocess.run([py if os.path.exists(py) else sys.executable, os.path.join(TOOLS, 'num', 'build_num.py'), '--check'])
    print('끝 — 확인: git diff -M --stat HEAD -- docs (3Q는 이름 바꿈 + index 한 줄) · tools/tests4 · verify')
if __name__ == '__main__':
    main('--dry' in sys.argv)
