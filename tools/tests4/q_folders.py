"""맥 원본 폴더 정리·JB 풀기 회귀(11-15 — tools/folders.py · tools/jbx.py · tools/matx.py 자리 찾기)
임시 폴더에 옛 맥 모양(3Q 자료 = materials/<과목> · JB = jb/ 바로 아래 · 한글 이름 NFD)을 만들고:
  ① folders.py --dry = 아무것도 안 바꿈 ② folders.py = 3Q는 3Q 칸으로 · 4Q 과목 자리 10+10 · 지우는 것 0 ③ 두 번째 = 바꿀 것 없음
  ④ jbx = jb/3Q 표준 이름 · jb/4Q/<과목>/<연도 든 이름> 풀기 · 연도 없음·모르는 자리는 '알아보지 못함' · 같은 판 두 파일은 하나만 ⑤ 다시 = 이미 푼 판 건너뜀
  ⑥ matx 자리 찾기 = 3Q는 materials/3Q/<과목>(NFD) → 옛 자리도 · 빈 4Q 과목 폴더에서 멈추지 않음"""
import os, sys, shutil, subprocess, tempfile, unicodedata, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
PY = os.path.join(ROOT, '.venv', 'bin', 'python'); PY = PY if os.path.exists(PY) else sys.executable
F = []
def ok(c, m): print(('  OK   ' if c else '  FAIL ') + m); c or F.append(m)
import pymupdf
def pdf(p, n=2):
    os.makedirs(os.path.dirname(p), exist_ok=True); d = pymupdf.open()
    for i in range(n): d.new_page().insert_text((50, 72), f'p{i + 1} ' + 'dental text ' * 20, fontsize=9)
    d.save(p)
def files(d):   # 원본 자리(materials·jb)만
    return sorted(unicodedata.normalize('NFC', os.path.relpath(os.path.join(a, f), d)) for t in ('materials', 'jb') for a, _, fs in os.walk(os.path.join(d, t)) for f in fs)
T = tempfile.mkdtemp(prefix='qfold_'); TL = os.path.join(T, 'tools'); os.makedirs(TL)
for f in ('quarters.py', 'quarters.json', 'folders.py', 'jbx.py', 'matx.py', 'jblpaths.py'): shutil.copy(os.path.join(ROOT, 'tools', f), TL)
NFD = lambda s: unicodedata.normalize('NFD', s)
pdf(os.path.join(T, 'materials', NFD('노인치과학'), '250901_옛자료.pdf')); pdf(os.path.join(T, 'materials', '임상치과보존학', '261002_이창하.pdf'))
pdf(os.path.join(T, 'jb', '2025 3Q 노인치과학 JB.pdf')); pdf(os.path.join(T, 'jb', NFD('2026 3Q 임상치과보존학 JB.pdf')), 3); pdf(os.path.join(T, 'jb', '2025 4Q 구강악안면외과학2 JB.pdf'))
before = files(T)
def run(*a): r = subprocess.run([PY, *a], cwd=T, capture_output=True, text=True); return r.returncode, r.stdout + r.stderr
rc, o = run('tools/folders.py', '--dry'); ok(rc == 0 and files(T) == before and '⇒' in o, f'① --dry = 바꾸지 않음(파일 {len(before)}개 그대로) · 할 일은 보임')
rc, o = run('tools/folders.py'); after = files(T)
ok(rc == 0, '② folders.py 종료 0')
ok('materials/3Q/노인치과학/250901_옛자료.pdf' in after and 'materials/3Q/임상치과보존학/261002_이창하.pdf' in after, '② 3Q 강의자료 → materials/3Q/<과목> (NFD 이름도)')
ok('jb/3Q/2025 3Q 노인치과학 JB.pdf' in after and 'jb/3Q/2026 3Q 임상치과보존학 JB.pdf' in after, '② 3Q JB → jb/3Q/')
ok('jb/4Q/구강악안면외과학/2025 4Q 구강악안면외과학2 JB.pdf' in after, '② 4Q 표준 이름 JB → jb/4Q/<과목>/')
sys.path.insert(0, os.path.join(ROOT, 'tools')); import quarters as QS
four = [v['mat'] for v in QS.SUBJ.values() if v['q'] == QS.current()]
ok(all(os.path.isdir(os.path.join(T, 'materials', '4Q', m)) and os.path.isdir(os.path.join(T, 'jb', '4Q', m)) for m in four), f'② 4Q 과목 자리 {len(four)}+{len(four)}')
ok(sum(f.endswith('.pdf') for f in after) == sum(f.endswith('.pdf') for f in before), '② PDF 수 그대로(지우는 것 0)')
rc, o = run('tools/folders.py'); ok(rc == 0 and '바꿀 것 없음' in o, '③ 두 번째 = 바꿀 것 없음')
pdf(os.path.join(T, 'jb', '4Q', '임상영상치의학', '영상치의학 기출 2024.pdf')); pdf(os.path.join(T, 'jb', '4Q', '임상영상치의학', '2025 영상 JB.pdf'))
pdf(os.path.join(T, 'jb', '4Q', '임상영상치의학', '2025 영상 답안.pdf')); pdf(os.path.join(T, 'jb', '4Q', '임상영상치의학', '연도없음.pdf')); pdf(os.path.join(T, 'jb', '아무데나.pdf'))
rc, o = run('tools/jbx.py')
got = sorted(os.listdir(os.path.join(T, 'work', 'jb')))
ok(rc == 0 and got == ['CONS_2026', 'GERI_2025', 'OMS2_2025', 'RAD_2024', 'RAD_2025'], f'④ 풀린 판 {got}')
ok(o.count('알아보지 못함') == 2 and '연도' in o, '④ 연도 없음·모르는 자리 = 알아보지 못함 2')
ok('두 파일' in o, '④ 같은 판 두 파일 = 하나만 풀고 알림')
m = json.load(open(os.path.join(T, 'work', 'jb', 'RAD_2024', 'manifest.json'), encoding='utf-8'))
ok(len(m['pages']) == 2 and os.path.exists(os.path.join(T, 'work', 'jb', 'RAD_2024', '1.txt')), '④ 판 폴더 꼴(N.txt·manifest)')
rc, o = run('tools/jbx.py'); ok(rc == 0 and '새로 푼 판 0' in o and '이미 푼 판 5' in o, '⑤ 다시 = 이미 푼 판 건너뜀')
code = ("import sys; sys.path.insert(0,'tools'); import matx, os\n"
        "class P:\n def map(self,f,j,chunksize=1): [f(x) for x in j]\n"
        "for s in ('GERI','RAD','HINS'): matx.run(s, P())\n"
        "print(sorted(os.listdir('work/GERI/mat')), os.path.isdir('work/HINS/mat'))")
B = os.path.join(T, 'bin'); os.makedirs(B); open(os.path.join(B, 'tesseract'), 'w').write('#!/bin/sh\nexit 0\n'); os.chmod(os.path.join(B, 'tesseract'), 0o755)   # OCR은 이 검사 밖(자리 찾기만)
r = subprocess.run([PY, '-c', code], cwd=T, capture_output=True, text=True, env={**os.environ, 'PATH': B + os.pathsep + os.environ.get('PATH', '')})
ok(r.returncode == 0 and '250901_옛자료' in r.stdout and 'False' in r.stdout, f'⑥ matx 자리 = materials/3Q/<과목>(NFD) · 빈 4Q 과목은 건너뜀 {r.stdout.strip()[-120:]}{r.stderr.strip()[-200:]}')
shutil.rmtree(T, ignore_errors=True)
print('RESULT ' + ('PASS' if not F else f'FAIL {len(F)}'))
sys.exit(1 if F else 0)
