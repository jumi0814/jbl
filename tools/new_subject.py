"""새 과목 만들기(11-04 4Q) — 등록표(tools/quarters.json)에 넣고 tools/<sid>/를 첫 build4가 도는 최소 모양으로 만든다.
  .venv/bin/python tools/new_subject.py --sid OMS2 --q 4q --ko '구강악안면외과학 2' --short 구강외과2 --color '#0F6E6C' [--jb 구강악안면외과학2] [--mat 구강악안면외과학2] [--en '…'] [--profs '교수 · 교수'] [--dry]
  .venv/bin/python tools/new_subject.py --remove TST9     # 시험용 SID 지우기(등록표·tools/<sid>/·matx SRC — 배포한 과목에는 쓰지 말 것)
만드는 것: subject.py(빈 강의표) · build2.py(cons 사본 — build4가 씀) · assemble.py(tools/cons/assemble.py의 기계 부분 + 비운 JB 자료 절 — JB 분해 뒤 2절을 채움) · parse_<sid>.py(빈 parse — 판본 구조를 읽고 씀)
  · lec_WAIT.txt(자리 표시 강의 — 실제 강의를 넣으면 지움) · annot.txt·tables.txt·pred.txt(빈) · jb_lock.json·jb_move.json({}) · 공통 파일(sync_common) · tools/matx.py SRC 빈 항목 · guide/과목노트_<SID>.md
그다음: JB → parse_<sid>.py·assemble 2절(OTHER·add) → subject.py(LECMAP·LEC_ORDER·PROF_*·YEAR_PROF) → 원고 — .claude/skills/jbl-update/SKILL.md B 모드 4 · RULES 14(4Q 판)"""
import os, re, sys, json, shutil, argparse, subprocess
TOOLS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
REGF = os.path.join(TOOLS, 'quarters.json')
COMMON = ['shell.html', 'build4.py', 'lecparse.py', 'trend.py', 'reflow.py', 'emph.py', 'template2.html', 'SPEC.md']

def reg_write(R):
    """등록표를 원래 꼴(과목 한 줄씩)로 다시 씀"""
    head = {k: v for k, v in R.items() if k != 'subjects'}
    t = json.dumps(head, ensure_ascii=False, indent=1)[:-2] + ',\n "subjects": {\n'
    t += ',\n'.join(f'  {json.dumps(s, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}' for s, v in R['subjects'].items()) + '\n }\n}\n'
    json.loads(t); open(REGF, 'w', encoding='utf-8').write(t)

def assemble_src(sid):
    """tools/cons/assemble.py → 새 과목판: 판본·문항 자료(2절)·CONS 전용 꼼수를 비움(나머지 기계 부분은 그대로)"""
    s = open(os.path.join(TOOLS, 'cons', 'assemble.py'), encoding='utf-8').read()
    def R(a, b):
        nonlocal s
        assert s.count(a) == 1, a[:60]; s = s.replace(a, b)
    R('import parse_cons as P, subject as S', f'import parse_{sid.lower()} as P, subject as S')
    R("SUB = 'CONS'", f"SUB = '{sid}'")
    s = re.sub(r"^NPAGES = \{[^\n]*\}$", "NPAGES = {}   # JB 판본 {'26': 쪽수, '25': …} — parse_%s.py를 쓴 뒤 채움" % sid.lower(), s, count=1, flags=re.M)
    i = s.index('# ---------- 2. canonical questions ----------'); j = s.index('# ---------- 3. annotations ----------')
    k = s.index('def add(', i); e = s.index('\nfor x in blocks', k)
    s = s[:i] + ('# ---------- 2. canonical questions ----------\n'
                 '# (새 과목 — JB 분해 뒤 채움) OTHER = {id: [(판, 번호), …]} 같은 문제의 다른 판본 · 문항 = add(id, 판, 블록, tier, 교수, 출처 글) · 판본마다 for x in blocks[판]: add(…)\n'
                 '#   본보기: tools/cons/assemble.py 2절(새 판 문항 NEW26·놓을 자리) · tools/esth/assemble.py(연도 칸형) — 판본 사이 같은 문제는 OTHER로(대조표 연결 안 된 블록 0)\n'
                 'OTHER = {}\nCROPS = {}\nQ = []\n') + s[k:e] + '\n\n' + s[j:]
    R('{"슬라이드" if k == "WHT" else "p."}', 'p.')
    s = re.sub(r"^MENT = \{[^\n]*\}$", "MENT = {ed: ment(ed, [1]) for ed in NPAGES}   # JB 판 머리 멘트 쪽 — 판마다 맞게", s, count=1, flags=re.M)
    s = s.replace('# 정식 문항은 26판 앞쪽 블록뿐(뒷부분 key P…는 모두 다른 판본)', '')
    return s

PARSE = '''import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""{sid} JB 분해 — 판본 구조(연도 칸형 / 교수별 괄호형)를 읽고 쓴다: parse(ed, n) → 블록 [{{'ed','sec','prof','num','pg','pg2','lines'}}](+ 'key' 겹치는 번호)
본보기: tools/cons/parse_cons.py(교수별 괄호형·26판 앞뒤) · tools/esth/parse_esth.py(연도 칸형) — 블록 수·번호 검증(RULES 0-1)"""
import re, json
BASE = J.JBX
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\\r', '').replace('\\x02', '')
def parse(ed, n):
    return []   # 아직 JB 없음 — work/jb/{sid}_20<ed>/<쪽>.txt를 읽어 블록으로
'''

SUBJECT = '''import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
# 과목별 설정({q} {ko} — tools/new_subject.py가 만든 빈 틀 · 강의를 넣으며 채움 · 필드 설명은 tools/cons/subject.py)
SID, TITLE, EN, COLOR = {sid!r}, {ko!r}, {en!r}, {color!r}
PROFS = {profs!r}
BUILT = {built!r}
LECMAP = {{'WAIT': (None, '강의자료 대기')}}   # 키: (쪽 이미지 폴더 work/{sid}/lec/<폴더> — tools/matx.py SRC, 강의 이름)
LEC_ORDER = ['WAIT']
LEC_IMG_ROOT = J.work({sid!r}, 'lec') + '/'
def lec_img_path(k, p):
    d = LECMAP[k][0]
    return f'{{LEC_IMG_ROOT}}{{d}}/{{p}}.jpg' if d else None
FORCE_PAGES = {{}}
PAGE_LABEL = {{}}
IMG_ALIAS = {{}}   # 25 보조 키 → 26 키(예 'INT5': 'INT') — 4Q는 25 쪽을 기출 근거 ⭐ 줄에서만(RULES 14)
PROF_LEC = {{}}
PROF_ORDER = []
COVER = {{}}   # 교수: JB 괄호 연도 기준선(그해까지는 짤/탈 판정 안 함)
TIERS = {{'A': '현 교수 기출', 'B': '(해당 없음)', 'C': '참고용'}}
PROF_NOTE = {{}}
MENT_PROF = {{}}
MENT_ALL = ''
YEAR_PROF = {{}}
YEAR_PROF_Q = {{}}
'''

LEC = '''#LEC WAIT | 강의자료 대기 | - | 26 | (강의자료·JB를 받으면 실제 강의로 바꾸고 이 파일은 지움) | 0
@MAP 자료 대기
@G ① 자료 대기
## Materials pending | 강의자료 대기 | 1 | 자리 표시
= 이 과목은 강의자료·JB를 받는 대로 정리본이 채워집니다.
'''

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sid'); ap.add_argument('--q'); ap.add_argument('--ko'); ap.add_argument('--short'); ap.add_argument('--color')
    ap.add_argument('--jb'); ap.add_argument('--mat'); ap.add_argument('--en', default=''); ap.add_argument('--profs', default=''); ap.add_argument('--dry', action='store_true'); ap.add_argument('--remove')
    a = ap.parse_args(); R = json.load(open(REGF, encoding='utf-8'))
    if a.remove:
        sid = a.remove.upper(); R['subjects'].pop(sid, None); reg_write(R)
        d = os.path.join(TOOLS, sid.lower())
        if os.path.isdir(d): shutil.rmtree(d)
        m = os.path.join(TOOLS, 'matx.py'); t = open(m, encoding='utf-8').read(); t2 = re.sub(r"\n    '%s': \{\},   # new_subject[^\n]*" % sid, '', t)
        if t2 != t: open(m, 'w', encoding='utf-8').write(t2)
        nf = os.path.join(ROOT, 'guide', f'과목노트_{sid}.md')
        if os.path.exists(nf) and '(new_subject 빈 틀)' in open(nf, encoding='utf-8').read(): os.remove(nf)
        print('지움', sid); return
    for k in ('sid', 'q', 'ko', 'short', 'color'):
        if not getattr(a, k): sys.exit(f'--{k} 필요')
    sid = a.sid.upper(); d = os.path.join(TOOLS, sid.lower())
    if sid in R['subjects'] or os.path.exists(d): sys.exit(f'{sid}: 이미 있음')
    if a.q not in R['quarters']: sys.exit(f'분기 {a.q} 없음')
    if not re.fullmatch(r'#[0-9A-Fa-f]{6}', a.color): sys.exit('--color는 #RRGGBB')
    R['subjects'][sid] = {'q': a.q, 'ko': a.ko, 'short': a.short, 'color': a.color, 'jb': a.jb or a.ko.replace(' ', ''), 'mat': a.mat or a.ko.replace(' ', '')}
    import quarters as QS
    QS.SUBJ = R['subjects']; QS.REG = R; QS.QS = R['quarters']; err = QS.check()
    if err: sys.exit('등록표 검사 실패:\n  ' + '\n  '.join(err))
    if a.dry: print('검사 통과(--dry — 아무것도 쓰지 않음)', R['subjects'][sid]); return
    reg_write(R); os.makedirs(d)
    import datetime
    files = {'subject.py': SUBJECT.format(sid=sid, q=a.q, ko=a.ko, en=a.en, color=a.color, profs=a.profs, built=datetime.date.today().isoformat()),
             'assemble.py': assemble_src(sid), f'parse_{sid.lower()}.py': PARSE.format(sid=sid), 'lec_WAIT.txt': LEC,
             'annot.txt': '', 'tables.txt': '', 'pred.txt': '', 'jb_lock.json': '{}\n', 'jb_move.json': '{}\n'}
    for f, t in files.items(): open(os.path.join(d, f), 'w', encoding='utf-8').write(t)
    b2 = open(os.path.join(TOOLS, 'cons', 'build2.py'), encoding='utf-8').read().replace("J.work('CONS', 'build2_view.html')", f"J.work('{sid}', 'build2_view.html')")   # build4가 JB 막대·대장(PINL·YPF·view_led)에 씀
    open(os.path.join(d, 'build2.py'), 'w', encoding='utf-8').write(b2)
    for f in COMMON: shutil.copyfile(os.path.join(TOOLS, 'SPEC.md') if f == 'SPEC.md' else os.path.join(TOOLS, 'cons', f), os.path.join(d, f))
    m = os.path.join(TOOLS, 'matx.py'); t = open(m, encoding='utf-8').read()
    if f"'{sid}':" not in t: open(m, 'w', encoding='utf-8').write(t.replace('SRC = {\n', "SRC = {\n    '%s': {},   # new_subject — 정리본 키 폴더 → 강의자료 파일 앞머리(예 'X01i': '261103_')\n" % sid, 1))
    nf = os.path.join(ROOT, 'guide', f'과목노트_{sid}.md')
    if not os.path.exists(nf): open(nf, 'w', encoding='utf-8').write(f'# 과목노트 {sid} — {a.ko} ({a.q}) (new_subject 빈 틀)\n\n- 교수: {a.profs or "(자료 받는 대로)"}\n- 강의·JB 판본·결정은 여기에 덧붙임\n')
    print(f'만듦: {sid} ({a.q} · {a.ko}) → tools/{sid.lower()}/ · 등록표 · matx SRC · 과목노트')
    print('다음: 빌드 시험 = .venv/bin/python tools/%s/build4.py' % sid.lower())

if __name__ == '__main__':
    main()
