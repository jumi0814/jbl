"""ux3 트랙3 묶음 N 회귀(빌드·브라우저 없이): lecparse.key_lines 🔑 줄 나누기 K1~K6 · 글자 불변 · 요지 .ksub
① 예시 6개가 결정 10의 '후' 모양(HTML 구조) — anat LIP:45 라벨 줄 · geri ENDO:252 ' / ' 줄 라벨 굵게+흐름 · cons WHT:117 머리 줄+사실 흐름 ·
  pharm CHR:406 단계 흐름 · cons WHT:424 ' — ' 둘째 줄 · anat NECK:295 '+ ' 줄
② 6과목 🔑 전부(719)·요지 전부: 새 렌더 글자(textContent) = 옛 렌더(render_block·inline) — 하나라도 다르면 FAIL · key_lines 되돌림 0
③ 80자 넘는 한 줄 덩어리(🔑 상자 + 정리표 🔑 칸) ≤ 150 (옛 렌더 548)"""
import os, sys, re, importlib, collections
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
class QM(dict):
    def get(self, k, d=None): return {'yrs': [24], 'short': ''}
def load(sid):
    d = os.path.join(T, sid)
    for m in ('lecparse', 'subject', 'emph'): sys.modules.pop(m, None)
    sys.path.insert(0, d); LP = importlib.import_module('lecparse'); sys.path.remove(d); return LP, d
def line(d, f, n):   # n = 원고 줄 머리(앞부분 글자) — 원고를 고치면 줄 번호가 밀리므로 번호 대신 글자로 찾음(10-02 정리본 검토로 ENDO·CHR 한 줄씩 밀림)
    L = [x for x in open(os.path.join(d, f), encoding='utf-8').read().split('\n') if x.startswith(n)]
    assert len(L) == 1, f'{f} 예시 줄 {n!r} {len(L)}개'
    return L[0][2:].strip()
tot_o = tot_n = nk = ng = 0; ctxs = {}
EX = {('anat', 'lec_LIP.txt', '= 인중 = {r:philtrum}'): lambda h: h.count('<div class="kl">') == 2 and '<b class="lbl">인중</b>' in h and '<b class="lbl">입술 경계</b>' in h and '<span class="ksep kh"> · </span>' in h,
      ('geri', 'lec_ENDO.txt', '= Negotiation = {r:Do 100 strokes}'): lambda h: h.count('<b class="lbl">') == 3 and '<ul class="klist">' in h and h.count('<li>') == 3,
      ('cons', 'lec_WHT.txt', '= 핵심 수치: gutta percha'): lambda h: '<div class="kl klh">핵심 수치:' in h and h.count('class="kfi') == 6,
      ('pharm', 'lec_CHR.txt', '= IV {r:morphine} → 수술'): lambda h: '<span class="kst">' in h and h.count('class="ksi') == 6 and h.count('class="ksep ka"') == 5,
      ('cons', 'lec_WHT.txt', '= ==10% carbamide peroxide in a custom-f'): lambda h: '<div class="ksub"><span class="ksep kh"> — </span>best ultimate results' in h,
      ('anat', 'lec_NECK.txt', '= Extended ND = {r:additional LN}'): lambda h: h.count('<div class="kl">') == 2 and '<span class="ksep kp"> + </span>' in h}
for sid in ['oms1', 'cons', 'impl', 'anat', 'geri', 'pharm']:
    LP, d = load(sid); ctx = {'QMAP': QM(), 'LECNAME': collections.defaultdict(lambda: 'L'), 'cited': set()}
    for (s2, f, n), chk in EX.items():
        if s2 != sid: continue
        v = line(d, f, n); ks = LP.key_split(v); k = ks[0] if ks else v; h = LP.render_keybox(k, ctx)
        ok(chk(h) and LP._txt(h) == LP._txt('<div class="kb">' + LP.render_block(k, ctx) + '</div>'), f'{sid} {f}:{n} 모양 {re.sub(r"<(?!/?(div|b|ul|li)\b)[^>]+>", "", h)[:150]}')
    bad = []
    for L in LP.load_all():
        for j, c in enumerate(L['cards']):
            for t, v in c['body']:
                if t != 'K': continue
                ks = LP.key_split(v); k = ks[0] if ks else v; o = LP.render_block(k, ctx); nw = LP.key_lines(k, ctx); nk += 1
                if LP._txt(o) != LP._txt(nw): bad.append(f'{L["k"]}:{j}')
                tot_o += sum(len(x) > 80 for x in LP.line_units(o)); tot_n += sum(len(x) > 80 for x in LP.line_units(nw))
            if c['gist']:
                ng += 1
                if LP._txt(LP.gist_html(c['gist'], ctx)) != LP._txt(LP.inline(c['gist'], ctx)): bad.append(f'{L["k"]}:{j} 요지')
    ok(not bad and LP.KL[2] == 0, f'{sid}: 🔑·요지 글자 = 옛 렌더 (다름 {bad[:5]} · 되돌림 {LP.KL[2]} · 새 구조 {LP.KL[1]}/{LP.KL[0]})')
ok(nk == 719 and ng == 719, f'🔑 {nk} · 요지 {ng} (719·719)')
ok(tot_n * 2 <= 150 and tot_n <= tot_o * 0.3, f'80자 넘는 한 줄 덩어리(상자+정리표 칸) {tot_o * 2} → {tot_n * 2} (≤150 · 70% 이상 줄임)')
print('RESULT', 'PASS' if not fails else f'FAIL {len(fails)}'); sys.exit(1 if fails else 0)
