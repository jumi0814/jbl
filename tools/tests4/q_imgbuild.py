"""11-10 그림 파일 방식(W3) 빌드 시험 — 진짜 build4를 시험 과목으로 돌려 봄(브라우저·work/jb 없이)
tools/new_subject.py로 시험 과목 TST9(4q)를 만들고 → PIL 가짜 강의 쪽 그림 3장 + F: 그림 줄이 든 작은 원고 → build4를 JBL_DOCS=<시험 폴더>로:
 ① 파일 3개(packs/img/TST9/<키>-<쪽>.<h8>.webp · h8 = 파일 md5 앞 8자)·팩 imgf·tools/tst9/img_lock.json · 묶음 파일(TST9.img.*.js) 없음 · HTML에 폭·높이
 ② 다시 빌드 = 파일·해시·팩 글자 그대로(다시 인코딩 0 · 파일을 다시 쓰지 않음)
 ③ 그림 하나를 바꾸면 그 파일만 새 해시 + 옛 파일은 한 세대 남음 → 한 번 더 빌드하면 옛 파일 지워짐
 ④ 원본 그림 없이 다시 빌드(클라우드) = 지난 목록·파일 그대로 · 팩 글자까지 같음
 ④b JB 원본 쪽 — 가짜 JB 2쪽(사본 work/jb/TST9_2026 · 진짜 work/jb는 쓰지 않음): packs/img/TST9/jb26-<쪽>.<h8>.jpg(assemble이 준 JPEG 바이트 그대로)·imgf.jb·img_lock · 다시 빌드 = 그대로 · 쪽 그림 없이(클라우드) = 그대로
 ⑤ 스위치 끔(분기에 img 키 없음 = 3Q 방식) = 묶음 TST9.img.<강의>.js·imgv 그대로(imgf·packs/img 없음) · 묶음 속 그림 바이트 = 파일 방식의 파일 바이트
 ⑥ new_subject.py --remove TST9 → 등록표·tools/tst9 지워짐
 (+ ① 쪽이 숫자가 아닌 인용 [[키:쪽]]은 칩을 만들지 않고 글자 그대로 — A19)
등록표(tools/quarters.json)·tools/를 건드리지 않게 도구 사본(work/_tmp/q_imgbuild/repo/tools — *.py·quarters.json·cons 공통 파일)에서 돌림: new_subject·build4는 제 파일 자리로 저장소 뿌리를 정하므로
사본 안의 등록표·tools/tst9·work/만 바뀜(시험이 중간에 죽어도 진짜 등록표에 TST9가 남지 않고, 같은 때 도는 rehub·다른 시험이 TST9를 보지 않음)."""
import os, sys, re, json, glob, shutil, base64, hashlib, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)
from PIL import Image, ImageDraw
SB = os.path.join(ROOT, 'work', '_tmp', 'q_imgbuild'); REPO = os.path.join(SB, 'repo'); T2 = os.path.join(REPO, 'tools')
SID = 'TST9'; KEY = 'IMG'; FOLD = 'IMGi'
fail = []
def ok(c, m):
    print(('  OK  ' if c else '  FAIL') + ' ' + m)
    if not c: fail.append(m)
def done():
    print('RESULT', 'FAIL' if fail else 'PASS'); sys.exit(1 if fail else 0)
ENV = {k: v for k, v in os.environ.items() if not k.startswith('JBL_')}   # 바깥의 JBL_Q·JBL_HTTP·JBL_DOCS가 시험 빌드에 새지 않게
def run(args, docs=None, expect=0):
    e = dict(ENV);
    if docs: e['JBL_DOCS'] = docs
    r = subprocess.run([sys.executable] + args, cwd=REPO, env=e, capture_output=True, text=True)
    if r.returncode != expect: print(r.stdout[-3000:], r.stderr[-3000:]); ok(False, f'{" ".join(os.path.basename(a) for a in args[:2])} 종료 코드 {r.returncode}'); done()
    return r.stdout + r.stderr
def pack(docs):
    t = open(os.path.join(docs, 'packs', SID + '.js'), encoding='utf-8').read(); return t, json.loads(t[t.index('{'):t.rindex('}') + 1])
def files(docs):
    d = os.path.join(docs, 'packs', 'img', SID); return sorted(os.listdir(d)) if os.path.isdir(d) else []
def md8(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()[:8]
def dk(Pa, Pb):
    """두 팩에서 값이 다른 곳(실패 줄에 보일 것) — 맨 위 키 · 강의 안 키"""
    o = [k for k in sorted(set(Pa) | set(Pb)) if Pa.get(k) != Pb.get(k) and k != 'lect']
    for La, Lb in zip(Pa.get('lect') or [], Pb.get('lect') or []): o += [f'lect.{La.get("k")}.{k}' for k in sorted(set(La) | set(Lb)) if La.get(k) != Lb.get(k)]
    return o
def fake(n, tint=0):
    """가짜 강의 쪽 그림(1400×900 — 폭 1100으로 줄어드는 길) · 쪽마다 다른 무늬"""
    im = Image.new('RGB', (1400, 900), (250, 250 - tint, 245)); d = ImageDraw.Draw(im)
    for i in range(12): d.rectangle([40 + i * 110, 60 + (i * n * 37) % 600, 120 + i * 110, 140 + (i * n * 37) % 600], fill=((i * 20 + n * 40) % 255, (90 + tint) % 255, (200 - i * 12) % 255))
    d.text((60, 820), f'page {n} tint {tint}', fill=(20, 20, 20))
    p = os.path.join(REPO, 'work', SID, 'lec', FOLD); os.makedirs(p, exist_ok=True); im.save(os.path.join(p, f'{n}.jpg'), 'JPEG', quality=90)

# ---- 사본 만들기(도구만 — 과목 폴더·원고·docs는 복사하지 않음)
shutil.rmtree(SB, ignore_errors=True); os.makedirs(os.path.join(T2, 'cons')); os.makedirs(os.path.join(REPO, 'guide'))
for f in glob.glob(os.path.join(TOOLS, '*.py')) + [os.path.join(TOOLS, 'quarters.json'), os.path.join(TOOLS, 'SPEC.md')]: shutil.copy(f, T2)
for f in ('shell.html', 'build4.py', 'lecparse.py', 'trend.py', 'reflow.py', 'emph.py', 'template2.html', 'assemble.py', 'build2.py'): shutil.copy(os.path.join(TOOLS, 'cons', f), os.path.join(T2, 'cons'))
REG = os.path.join(T2, 'quarters.json'); reg0 = json.load(open(REG, encoding='utf-8'))
Q4 = next((q for q, v in reg0['quarters'].items() if v.get('img') == 'files' and not v.get('frozen')), None)
ok(Q4 is not None, f'등록표에 그림 파일 방식 분기가 있음("img": "files") — {Q4}')
if not Q4: done()
real0 = open(os.path.join(TOOLS, 'quarters.json'), encoding='utf-8').read()

# ---- 시험 과목: new_subject → 그림 강의 하나
run([os.path.join(T2, 'new_subject.py'), '--sid', SID, '--q', Q4, '--ko', '그림 시험 과목', '--short', '그림시험', '--color', '#336699'])
D = os.path.join(T2, SID.lower())
ok(os.path.isdir(D) and SID in json.load(open(REG, encoding='utf-8'))['subjects'], 'new_subject: 사본 등록표·tools/tst9 생김')
s = open(os.path.join(D, 'subject.py'), encoding='utf-8').read()
s = s.replace("LECMAP = {'WAIT': (None, '강의자료 대기')}", f"LECMAP = {{'{KEY}': ('{FOLD}', '그림 시험 강의')}}").replace("LEC_ORDER = ['WAIT']", f"LEC_ORDER = ['{KEY}']")
assert f"'{FOLD}'" in s and f"['{KEY}']" in s; open(os.path.join(D, 'subject.py'), 'w', encoding='utf-8').write(s)
os.remove(os.path.join(D, 'lec_WAIT.txt'))
open(os.path.join(D, f'lec_{KEY}.txt'), 'w', encoding='utf-8').write(
    f'#LEC {KEY} | 그림 시험 강의 | 시험교수 | 26 | 시험용 자료(26년도 슬라이드, 3쪽) | 3\n@MAP 하나 → 둘\n@G ① 묶음\n'
    f'## Alpha panel | 첫째 무늬 판 | 1-2 | 무늬\n= 빨간 네모가 왼쪽 위에서 시작합니다.\n- 가로 줄 열두 칸 [[{KEY}:1]]\nF: 1=첫 쪽, 2\n'
    f'## Omega ledger | 둘째 장부 끝 | 3 | 장부\n= 파란 동그라미는 오른쪽 아래에서 끝납니다.\n- 세로 기둥 일곱 개 [[{KEY}:쪽]]\nF: 3\n')   # 두 카드는 제목·글이 서로 달라야 함 — 비슷하면 tools/aidlock.py가 두 번째 빌드부터 서로를 옛 이름(alt)으로 붙여 첫 빌드 ≠ 둘째 빌드(그림과 무관한 차이)
for n in (1, 2, 3): fake(n)
B4 = os.path.join(D, 'build4.py'); LOCK = os.path.join(D, 'img_lock.json'); OUT = os.path.join(SB, 'docs_files'); KS = [f'{KEY}-{n}' for n in (1, 2, 3)]

# ---- ① 첫 빌드
o = run([B4], OUT); t1, P1 = pack(OUT); F1 = files(OUT)
ok(len(F1) == 3 and all(re.fullmatch(re.escape(KEY) + r'-[123]\.[0-9a-f]{8}\.webp', f) for f in F1), f'① 그림 파일 3개 packs/img/{SID}/<키>-<쪽>.<h8>.webp {F1}')
ok(all(md8(os.path.join(OUT, 'packs', 'img', SID, f)) == f.split('.')[1] for f in F1), '① 파일 이름의 h8 = 파일 바이트 md5 앞 8자')
imgf = P1.get('imgf') or {}
ok(sorted(imgf.get('lec') or {}) == KS and imgf.get('jb') == {} and all(f'{k}.{h}.webp' in F1 for k, h in imgf['lec'].items()), f'① 팩 imgf.lec = 키 → h8(파일과 맞음) · imgf.jb 빈 목록 {imgf}')
ok(P1.get('imgv') == {} and not glob.glob(os.path.join(OUT, 'packs', SID + '.img.*')), '① 묶음 파일(TST9.img.*.js) 없음 · imgv 빈 값')
ok(not P1.get('stub'), '① 강의가 있는 과목은 stub 아님')
L1 = json.load(open(LOCK, encoding='utf-8')) if os.path.exists(LOCK) else {}
ok(sorted(L1.get('lec') or {}) == KS and all(L1['lec'][k][1] == imgf['lec'][k] and len(L1['lec'][k][0]) == 32 for k in KS) and L1.get('enc'), f'① img_lock.json: 키 → [원본 md5, h8, 폭, 높이] · enc {L1.get("enc")}')
im = Image.open(os.path.join(OUT, 'packs', 'img', SID, F1[0])); ok(im.format == 'WEBP' and im.size == (1100, 707), f'① 그림 = WebP 폭 1100(원본 1400×900 → {im.size})')
learn = P1['lect'][0]['learn']
ok(all(re.search(r'<img data-img="%s" alt="" width="740" height="\d+"' % re.escape(k), learn) for k in KS), '① 팩 HTML: img[data-img]에 width·height(자리 미리 잡기)')
ok('새로 인코딩 3' in o, '① 빌드 출력: 새로 인코딩 3')
ok(f'[[{KEY}:쪽]]' in learn and 'data-p="쪽"' not in json.dumps(P1, ensure_ascii=False).replace('\\"', '"') and '쪽이 숫자가 아닌 인용' in o and f'data-k="{KEY}" data-p="1"' in learn, f'① 쪽이 숫자가 아닌 인용 [[{KEY}:쪽]] = 칩 없이 원고 글자 그대로(A19) · 숫자 쪽 [[{KEY}:1]]은 칩')
single = glob.glob(os.path.join(REPO, 'work', '*_JBL.html'))
ok(len(single) == 1 and open(single[0], encoding='utf-8').read().count('data:image/webp;base64,') >= 3, '① work/ 단일 파일판에는 그림이 들어 있음(지금처럼)')
mt1 = {f: os.stat(os.path.join(OUT, 'packs', 'img', SID, f)).st_mtime_ns for f in F1}; lock1 = open(LOCK, encoding='utf-8').read()

# ---- ② 다시 빌드 = 그대로
o = run([B4], OUT); t2, P2 = pack(OUT); F2 = files(OUT)
ok(F2 == F1 and t2 == t1, f'② 다시 빌드: 파일 이름·팩 글자 그대로 {dk(P1, P2) or ""}')
ok({f: os.stat(os.path.join(OUT, 'packs', 'img', SID, f)).st_mtime_ns for f in F2} == mt1, '② 그림 파일을 다시 쓰지 않음(수정 시각 그대로)')
ok('새로 인코딩 0' in o and '원본 같음 3' in o and open(LOCK, encoding='utf-8').read() == lock1, '② 다시 인코딩 0 · 원본 같음 3 · img_lock 그대로')

# ---- ③ 그림 하나 바꿈 → 그 파일만 새 해시 · 옛 파일 한 세대 남음 → 다음 빌드 때 지움
fake(2, tint=60); o = run([B4], OUT); t3, P3 = pack(OUT); F3 = files(OUT); h1, h3 = P1['imgf']['lec'], P3['imgf']['lec']
ok(h3[KS[0]] == h1[KS[0]] and h3[KS[2]] == h1[KS[2]] and h3[KS[1]] != h1[KS[1]], f'③ 바꾼 쪽만 새 해시({KS[1]} {h1[KS[1]]} → {h3[KS[1]]})')
ok(len(F3) == 4 and f'{KS[1]}.{h1[KS[1]]}.webp' in F3 and f'{KS[1]}.{h3[KS[1]]}.webp' in F3, f'③ 옛 파일 한 세대 남음(파일 {len(F3)}개)')
ok('새로 인코딩 1' in o and '지난 세대 남김 1' in o, '③ 빌드 출력: 새로 인코딩 1 · 지난 세대 남김 1')
ok({f: os.stat(os.path.join(OUT, 'packs', 'img', SID, f)).st_mtime_ns for f in F1 if f in F3} == {f: v for f, v in mt1.items() if f in F3}, '③ 안 바뀐 파일은 다시 쓰지 않음')
o = run([B4], OUT); F4 = files(OUT); t4, P4 = pack(OUT)
ok(len(F4) == 3 and f'{KS[1]}.{h1[KS[1]]}.webp' not in F4 and '지움 1' in o and t4 == t3, '③ 한 번 더 빌드 → 옛 파일 지움(파일 3개) · 팩 그대로')

# ---- ④ 원본 그림 없이 다시 빌드(클라우드) = 지난 목록·파일에서
shutil.move(os.path.join(REPO, 'work', SID, 'lec'), os.path.join(REPO, 'work', SID, 'lec_off'))
o = run([B4], OUT); t5, P5 = pack(OUT)
ok(t5 == t4 and files(OUT) == F4, '④ 원본 없이 다시 빌드: 팩 글자(그림 폭·높이 포함)·파일 그대로')
ok('원본 없이 지난 파일 3' in o and '새로 인코딩 0' in o, '④ 빌드 출력: 원본 없이 지난 파일 3')
OUT2 = os.path.join(SB, 'docs_nosrc'); os.makedirs(os.path.join(OUT2, 'packs')); os.remove(LOCK)   # 잠금도 없고 출력 자리도 빈 곳 — 지난 것이 없으니 그림 없이(오류 없이) 빌드
o = run([B4], OUT2); t6, P6 = pack(OUT2)
ok(P6['imgf'] == {'lec': {}, 'jb': {}} and files(OUT2) == [], '④ 원본도 지난 파일도 없으면 그림 0장(오류 없이)')
shutil.move(os.path.join(REPO, 'work', SID, 'lec_off'), os.path.join(REPO, 'work', SID, 'lec'))
o = run([B4], OUT); t7, P7 = pack(OUT)
ok(P7['imgf'] == P4['imgf'] and t7 == t4 and files(OUT) == F4, '④ 원본이 돌아오면(잠금 없음 → 다시 인코딩) 같은 해시·같은 팩')

# ---- ④b JB 원본 쪽(가짜 JB 2쪽 — 1쪽 = 그림 있는 쪽(색 그대로) · 2쪽 = 글만(회색 860폭))
JD = os.path.join(REPO, 'work', 'jb', f'{SID}_2026'); os.makedirs(JD)
for n in (1, 2):
    im = Image.new('RGB', (924, 1300), (255, 255, 250)); d = ImageDraw.Draw(im)
    for i in range(9): d.rectangle([60, 80 + i * 130, 60 + 90 * (i + n), 150 + i * 130], fill=((40 * i + 70 * n) % 255, 80, (200 - 20 * i) % 255))
    im.save(os.path.join(JD, f'{n}.jpeg'), 'JPEG', quality=85); open(os.path.join(JD, f'{n}.txt'), 'w', encoding='utf-8').write(f'시험 JB {n}쪽\n')
json.dump({'pages': [{'page_number': 1, 'has_visual_content': True}, {'page_number': 2, 'has_visual_content': False}]}, open(os.path.join(JD, 'manifest.json'), 'w', encoding='utf-8'))
AS = os.path.join(D, 'assemble.py'); s = open(AS, encoding='utf-8').read(); s2 = re.sub(r'^NPAGES = \{\}', "NPAGES = {'26': 2}", s, count=1, flags=re.M); assert s2 != s; open(AS, 'w', encoding='utf-8').write(s2)
o = run([B4], OUT); tj, PJ = pack(OUT); FJ = files(OUT); JK = ['26-1', '26-2']; jf = PJ['imgf'].get('jb') or {}
ok(sorted(jf) == JK and all(f'jb{k}.{h}.jpg' in FJ and md8(os.path.join(OUT, 'packs', 'img', SID, f'jb{k}.{h}.jpg')) == h for k, h in jf.items()), f'④b JB 원본 쪽 파일 packs/img/{SID}/jb<판>-<쪽>.<h8>.jpg · imgf.jb {jf}')
ok(PJ['imgf']['lec'] == P7['imgf']['lec'] and len(FJ) == 5 and PJ.get('imgv') == {} and not glob.glob(os.path.join(OUT, 'packs', SID + '.img.*')), '④b 강의 쪽 파일은 그대로 · 묶음 파일(TST9.img.jb*.js) 없음')
if sorted(jf) == JK:
    i1, i2 = (Image.open(os.path.join(OUT, 'packs', 'img', SID, f'jb{k}.{jf[k]}.jpg')) for k in JK)
    ok(i1.format == i2.format == 'JPEG' and i1.mode == 'RGB' and i2.mode == 'L' and i2.size[0] == 860, f'④b JPEG 그대로(그림 쪽 = 색 {i1.size} · 글 쪽 = 회색 {i2.size} — assemble이 만든 그대로, 다시 압축 없음)')
ok(all(f'data-jb="{k}"' in PJ['ledger'] for k in JK), '④b 기출 대장의 JB 원본 쪽 단추 키 = imgf.jb 키')
LJ = json.load(open(LOCK, encoding='utf-8'))
ok(sorted(LJ.get('jb') or {}) == JK and all(LJ['jb'][k][1] == jf[k] and '|' in LJ['jb'][k][0] for k in JK), '④b img_lock.json jb: 키 → [원본 md5|꼴, h8]')
mtj = {f: os.stat(os.path.join(OUT, 'packs', 'img', SID, f)).st_mtime_ns for f in FJ}; lockj = open(LOCK, encoding='utf-8').read()
o = run([B4], OUT); tj2, PJ2 = pack(OUT)
ok(tj2 == tj and files(OUT) == FJ and {f: os.stat(os.path.join(OUT, 'packs', 'img', SID, f)).st_mtime_ns for f in FJ} == mtj and open(LOCK, encoding='utf-8').read() == lockj and '지난 파일 유지 2' in o, f'④b 다시 빌드: 팩·파일·잠금 그대로(지난 파일 유지 2) {dk(PJ, PJ2) or ""}')
for n in (1, 2): os.rename(os.path.join(JD, f'{n}.jpeg'), os.path.join(JD, f'{n}.jpeg.off'))   # 쪽 그림이 없는 곳(클라우드 — 글만 풀어 둠) → assemble이 J.prev_jb_pages(지난 목록의 파일)로
o = run([B4], OUT); tj3, PJ3 = pack(OUT)
ok(tj3 == tj and files(OUT) == FJ and open(LOCK, encoding='utf-8').read() == lockj, f'④b JB 쪽 그림 없이 다시 빌드: 팩·파일·잠금 그대로 {dk(PJ, PJ3) or ""}')
for n in (1, 2): os.rename(os.path.join(JD, f'{n}.jpeg.off'), os.path.join(JD, f'{n}.jpeg'))
single = glob.glob(os.path.join(REPO, 'work', '*_JBL.html'))
ok(len(single) == 1 and open(single[0], encoding='utf-8').read().count('data:image/jpeg;base64,') >= 2, '④b work/ 단일 파일판에는 JB 원본 쪽도 들어 있음')
t7, P7 = tj, PJ

# ---- ⑤ 스위치 끔 = 묶음 방식 그대로(3Q 방식)
reg = json.load(open(REG, encoding='utf-8')); reg['quarters'][Q4].pop('img'); json.dump(reg, open(REG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
OUT3 = os.path.join(SB, 'docs_chunks'); lock7 = open(LOCK, encoding='utf-8').read()
o = run([B4], OUT3); t8, P8 = pack(OUT3); CF = os.path.join(OUT3, 'packs', f'{SID}.img.{KEY}.js')
ok(os.path.exists(CF) and 'imgf' not in P8 and sorted(P8.get('imgv') or {}) == sorted([KEY, 'jb26']) and not os.path.isdir(os.path.join(OUT3, 'packs', 'img')), '⑤ 스위치 끔: 묶음 TST9.img.IMG.js·TST9.img.jb26.js·imgv 있음 · imgf·packs/img 없음')
JF = os.path.join(OUT3, 'packs', f'{SID}.img.jb26.js')
if os.path.exists(JF):
    jt = open(JF, encoding='utf-8').read(); JC = json.loads(jt[jt.index('{'):jt.rindex('}') + 1])
    ok(sorted(JC.get('jb') or {}) == JK and all(base64.b64decode(JC['jb'][k].split(',', 1)[1]) == open(os.path.join(OUT, 'packs', 'img', SID, f'jb{k}.{P7["imgf"]["jb"][k]}.jpg'), 'rb').read() for k in JK) and os.path.exists(os.path.join(OUT3, 'packs', f'{SID}.img.jb.js')), '⑤ JB 묶음 속 쪽 바이트 = 파일 방식의 jpg 바이트 · 옛 index 호환 TST9.img.jb.js 있음')
else: ok(False, '⑤ 스위치 끔: TST9.img.jb26.js 없음')
ok(open(LOCK, encoding='utf-8').read() == lock7 and '그림 파일(' not in o, '⑤ 스위치 끔: img_lock을 건드리지 않음 · 그림 파일 길이 돌지 않음')
if os.path.exists(CF):
    ct = open(CF, encoding='utf-8').read(); C = json.loads(ct[ct.index('{'):ct.rindex('}') + 1])
    same = all(base64.b64decode(C['lec'][k].split(',', 1)[1]) == open(os.path.join(OUT, 'packs', 'img', SID, f'{k}.{P7["imgf"]["lec"][k]}.webp'), 'rb').read() for k in KS)
    ok(sorted(C.get('lec') or {}) == KS and same, '⑤ 묶음 속 그림 바이트 = 파일 방식의 파일 바이트(화질·폭·method 같은 값)')
    strip = lambda P: {k: v for k, v in P.items() if k not in ('imgf', 'imgv')}
    ok(strip(P8) == strip(P7), '⑤ 두 방식의 팩은 imgf·imgv 말고 글자까지 같음')

# ---- ⑥ 지우기
run([os.path.join(T2, 'new_subject.py'), '--remove', SID])
ok(not os.path.isdir(D) and SID not in json.load(open(REG, encoding='utf-8'))['subjects'], '⑥ new_subject --remove: 사본 등록표·tools/tst9 지워짐')
ok(open(os.path.join(TOOLS, 'quarters.json'), encoding='utf-8').read() == real0 and not os.path.isdir(os.path.join(TOOLS, SID.lower())) and SID not in real0, '⑥ 진짜 등록표·tools/에는 TST9가 생긴 적 없음')
if not fail: shutil.rmtree(SB, ignore_errors=True)
done()
