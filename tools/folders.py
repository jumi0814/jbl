"""맥 원본 폴더 정리(11-15 사용자 "4큐 jb 및 자료를 어디로 넣어야 하는지 … 기존 폴더를 최적으로 바꿔서 구조화") — 쿼터·과목별 자리를 만들고 옛 3Q 파일을 3Q 칸으로 옮김.
  python3 tools/folders.py          # 자리 만들기 + 옮기기 + 지금 들어 있는 파일 수 보이기(여러 번 돌려도 같음)
  python3 tools/folders.py --dry    # 무엇을 할지만 보이기
sh tools/push_materials.sh 가 맨 처음에 이것을 돌림(따로 돌릴 일 없음).

  materials/
    3Q/<과목>/        ← 3Q 강의자료(옛 materials/<과목>/ 을 여기로 옮김 — 보관)
    4Q/<과목>/        ← 4Q 강의자료(PDF·PPTX — 받은 이름 그대로)
  jb/
    3Q/               ← 3Q JB('20YY 3Q <과목> JB.pdf' — 옛 jb/ 바로 아래 파일을 여기로 옮김 · 26판도 여기)
    4Q/<과목>/        ← 4Q JB(아무 이름 + 연도 '2025' 같은 네 자리가 들어 있으면 됨 · '20YY 4Q <과목> JB.pdf'도 됨)

지우는 것 없음 · 옮길 자리에 같은 이름이 이미 있으면 옮기지 않고 알림. 과목 폴더 이름 = tools/quarters.json subjects의 mat.
도구는 옛 자리도 그대로 읽음(matx = materials/3Q/<과목> → materials/<과목> · jbx = jb/ 아래 전부) — 옮기지 않아도 깨지지 않음."""
import os, re, sys, shutil, unicodedata
TOOLS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS); import quarters as QS
DRY = '--dry' in sys.argv
JBPAT = re.compile(r'^(20\d\d)[ _]([34])Q[ _](.+?)[ _]JB\.(pdf|zip)$', re.I)
NOTE = {
    'materials': '4Q 강의자료는 4Q/<과목>/ 에 넣어 주세요(PDF·PPTX · 받은 이름 그대로 · 25·26 둘 다 있어도 됨).\n'
                 '3Q/ = 3Q 자료(보관 — 옛 자리에서 옮김).\n다 넣은 뒤 jbl 폴더 터미널에서:  git pull && sh tools/push_materials.sh\n',
    'jb': '4Q JB는 4Q/<과목>/ 에 넣어 주세요(이름에 연도 2025 같은 네 자리가 들어 있으면 됨 · 판본마다 한 파일).\n'
          '3Q JB(26판 포함)는 3Q/ 에 — 이름 \'2026 3Q <과목> JB.pdf\'.\n다 넣은 뒤 jbl 폴더 터미널에서:  git pull && sh tools/push_materials.sh\n',
}
def nfc(s): return unicodedata.normalize('NFC', s)
def find(d, name):
    """d 안에서 이름이 name(NFC 비교 — 맥 한글 이름은 NFD)인 것"""
    if not os.path.isdir(d): return None
    return next((os.path.join(d, x) for x in os.listdir(d) if nfc(x) == nfc(name)), None)
def mk(p, acts):
    if not os.path.isdir(p):
        acts.append(f'  + 폴더 {os.path.relpath(p, ROOT)}/')
        if not DRY: os.makedirs(p, exist_ok=True)
def mv(a, b, acts, warn):
    if os.path.exists(b) or find(os.path.dirname(b), os.path.basename(b)):
        warn.append(f'  ! 옮기지 않음(이미 있음): {os.path.relpath(a, ROOT)} → {os.path.relpath(b, ROOT)} — 둘을 손으로 합쳐 주세요'); return
    acts.append(f'  → {os.path.relpath(a, ROOT)}  ⇒  {os.path.relpath(b, ROOT)}')
    if not DRY: os.makedirs(os.path.dirname(b), exist_ok=True); shutil.move(a, b)
def count(d):
    n = 0
    for dp, _, fs in os.walk(d): n += sum(1 for f in fs if f.lower().endswith(('.pdf', '.pptx', '.zip')))
    return n
def main():
    acts, warn = [], []
    M, JB = os.path.join(ROOT, 'materials'), os.path.join(ROOT, 'jb')
    live = QS.live() if hasattr(QS, 'live') else [QS.current()]
    for q in QS.QS:
        Q = q.upper()
        subs = [(k, v) for k, v in QS.SUBJ.items() if v['q'] == q]
        if QS.QS[q].get('frozen'):
            # 옛 materials/<과목>/(3Q) → materials/3Q/<과목>/ · 옛 jb/<'20YY 3Q …'> → jb/3Q/
            for k, v in subs:
                old = find(M, v['mat'])
                if old and os.path.isdir(old): mv(old, os.path.join(M, Q, nfc(v['mat'])), acts, warn)
            if os.path.isdir(JB):
                for f in sorted(os.listdir(JB)):
                    m = JBPAT.match(nfc(f))
                    if m and m.group(2) + 'q' == q and os.path.isfile(os.path.join(JB, f)): mv(os.path.join(JB, f), os.path.join(JB, Q, nfc(f)), acts, warn)
            mk(os.path.join(JB, Q), acts)
        else:
            # 지금 쿼터: 과목마다 빈 자리 · 옛 jb/ 바로 아래 '20YY 4Q …' 파일은 jb/4Q/<과목>/로
            for k, v in subs:
                mk(os.path.join(M, Q, nfc(v['mat'])), acts); mk(os.path.join(JB, Q, nfc(v['mat'])), acts)
            if os.path.isdir(JB):
                for f in sorted(os.listdir(JB)):
                    m = JBPAT.match(nfc(f))
                    if not (m and m.group(2) + 'q' == q and os.path.isfile(os.path.join(JB, f))): continue
                    sid = next((k for k, v in subs if nfc(m.group(3)) in {nfc(v['jb']), nfc(v['mat']), nfc(v['ko'].replace(' ', ''))}), None)
                    if sid: mv(os.path.join(JB, f), os.path.join(JB, Q, nfc(QS.SUBJ[sid]['mat']), nfc(f)), acts, warn)
    for top, txt in NOTE.items():
        p = os.path.join(ROOT, top, '여기에_넣는_법.txt')
        if os.path.isdir(os.path.dirname(p)) and not os.path.exists(p):
            acts.append(f'  + 안내 {os.path.relpath(p, ROOT)}')
            if not DRY: open(p, 'w', encoding='utf-8').write(txt)
    print('== 폴더 정리' + (' (--dry: 하지 않음)' if DRY else ''))
    print('\n'.join(acts) if acts else '  (바꿀 것 없음 — 이미 정리됨)')
    for w in warn: print(w)
    # 지금 들어 있는 것
    print('== 지금 들어 있는 파일(PDF·PPTX·ZIP)')
    for q in QS.QS:
        Q = q.upper(); subs = [(k, v) for k, v in QS.SUBJ.items() if v['q'] == q]
        if QS.QS[q].get('frozen'):
            print(f'  {Q}  강의자료 {count(os.path.join(M, Q))} · JB {count(os.path.join(JB, Q))}  (보관)')
            continue
        for k, v in subs:
            a = find(os.path.join(M, Q), v['mat']); b = find(os.path.join(JB, Q), v['mat'])
            print(f'  {Q} {k:6} {nfc(v["mat"])}: 강의자료 {count(a) if a else 0} · JB {count(b) if b else 0}')
    return 0
if __name__ == '__main__':
    sys.exit(main())
