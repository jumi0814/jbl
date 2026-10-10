"""정리본 원고 검사기 — 빌드 없이 원고 하나(또는 과목 전체)를 점검한다. 여러 작업자가 동시에 써도 docs/를 건드리지 않음.
사용: .venv/bin/python tools/check_lec.py <SID> [강의키 ...]
검사: 문법 파싱 · jb=/E:/{jb:} 문항 id 존재 · 이 강의에 연결될 현 교수 기출이 ⭐(E:)에 다 있는지 · F:·[[키:쪽]] 쪽 이미지 존재 ·
      카드별 필수 줄(> 요지, = 핵심, M: 암기) · 🔑 줄 길이 · 소제목의 쪽 번호 표기 · 쪽 범위 커버리지(빠진 쪽) · 밀도 통계(DD1 기준과 비교)
기준(qids.json)은 tools/dump_review.py가 만든 현재 사이트 연결. 새로 연결할 문항은 --also Q01,Q02 로 추가 지정."""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J

def ranges(s):
    out = set()
    for part in re.split(r'[,·]', s):
        m = re.match(r'\s*(\d+)\s*(?:[-~–]\s*(\d+))?\s*$', part)
        if m:
            a = int(m.group(1)); b = int(m.group(2) or a)
            if b >= a and b - a < 300: out |= set(range(a, b + 1))
    return out

def main(sid, keys, also):
    d = os.path.join(J.TOOLS, sid.lower()); sys.path.insert(0, d); os.chdir(d)
    import subject as S, lecparse as LP
    qj = json.load(open(J.work(sid, 'review', 'qids.json'), encoding='utf-8'))
    Q = qj['q']; bylec = qj['bylec']
    keys = keys or [k for k in S.LEC_ORDER if os.path.exists(os.path.join(d, f'lec_{k}.txt'))]
    bad_total = 0
    # ux3 N2·N5 🔑·요지 렌더 글자 동일 검사 + 80자 넘는 한 줄 덩어리 수 — 빌드 없이 원고만으로(문항·강의 이름은 가짜 값: 두 렌더에 똑같이 들어감)
    import collections as _co
    class _QM(dict):
        def get(self, k, d=None): return {'yrs': [24], 'short': ''}
    kctx = {'QMAP': _QM(), 'LECNAME': _co.defaultdict(lambda: 'L'), 'cited': set()}
    ktot = [0, 0, 0, 0, 0]   # 🔑 상자 · 요지 · 글자 다름 · 옛 80자↑ · 새 80자↑
    for k in keys:
        path = os.path.join(d, f'lec_{k}.txt'); errs, warns = [], []
        try: L = LP.parse(path)
        except Exception as e: print(f'✗ {k}: 파싱 실패 — {e}'); bad_total += 1; continue
        if L['k'] != k: errs.append(f'#LEC 키 {L["k"]} ≠ 파일 키 {k}')
        linked, exam = set(), set()
        cites = []
        for ci, c in enumerate(L['cards'], 1):
            nm = f'카드{ci} "{c["en"][:30]}"'
            if hasattr(LP, 'key_lines'):
                for t_, v_ in c['body']:
                    if t_ != 'K': continue
                    ks_ = LP.key_split(v_); k_ = ks_[0] if ks_ else v_; o_ = LP.render_block(k_, kctx); n_ = LP.key_lines(k_, kctx); ktot[0] += 1
                    if LP._txt(o_) != LP._txt(n_): errs.append(f'{nm}: 🔑 렌더 글자가 옛 렌더와 다름'); ktot[2] += 1
                    ktot[3] += sum(len(x) > 80 for x in LP.line_units(o_)); ktot[4] += sum(len(x) > 80 for x in LP.line_units(n_))
                if c['gist']:
                    ktot[1] += 1
                    if LP._txt(LP.gist_html(c['gist'], kctx)) != LP._txt(LP.inline(c['gist'], kctx)): errs.append(f'{nm}: 요지(>) 렌더 글자가 옛 렌더와 다름'); ktot[2] += 1
            if not c['gist']: errs.append(f'{nm}: > 요지 없음')
            if not any(b[0] == 'K' for b in c['body']): errs.append(f'{nm}: = 🔑 핵심 없음')
            if not c['recall']: errs.append(f'{nm}: M: 암기 줄 없음')
            for b in c['body']:
                if b[0] == 'K' and len(re.sub(r'\{r:|\}|==|\*\*', '', b[1])) > 260: warns.append(f'{nm}: 🔑 핵심이 너무 김({len(b[1])}자) — 한 줄 공식으로 압축, 나머지는 # 소제목/- 항목으로')
                if b[0] == 'h' and re.search(r'\(p\.?\s*\d', b[1]): warns.append(f'{nm}: 소제목에 쪽 번호 "{b[1][:30]}" — 의미 단위로')
                if b[0] == 'E':
                    exam |= set(b[1][0])
                    d_ = LP.exam_parts(b[1][1])   # ux2 fixB VIS11 서술·빈칸 답에 말줄임(…)은 그대로 외울 답을 가림 — JB 답 전문으로
                    if d_ and re.search(r'…|\.\.\.', d_['a'].split(' — ')[0]) and re.search(r'서술|빈칸|단답', d_['mid'] + d_['q']): warns.append(f'{nm}: ⭐ 답에 말줄임(…) "{d_["a"][:50]}" — 서술·빈칸 답은 JB 답 전문으로')
                if b[0] == 'F':
                    for p_, cap, fk in b[1]:
                        cites.append((fk or k, p_, nm))
                        if ',' in cap: errs.append(f'{nm}: 그림 캡션에 쉼표')
                txt = b[1] if isinstance(b[1], str) else (b[1][1] if b[0] == 'E' else '')
                for m in re.finditer(r'\[\[([A-Z0-9]+):([^\]]+)\]\]', str(txt)): cites.append((m.group(1), m.group(2), nm))
                for m in re.finditer(r'\{jb:([^}]+)\}', str(txt)): linked.add(m.group(1))
            linked |= set(c['jb'])
            body_t = ' '.join(b[1] for b in c['body'] if b[0] in ('b', 'K') and isinstance(b[1], str))   # ux2 fixB VIS08 빨강 비율(원칙 7-1 — 빨강은 핵심어·수치만)
            kc_ = LP._kcls(LP.red_set([v for t_, v in c['body'] if t_ == 'K'] + [v[1] for t_, v in c['body'] if t_ == 'E'] + list(c['recall'])))   # 화면과 같게: 🔑·⭐·⚡와 겹치는 {r:}만 빨강(나머지는 굵은 검정)
            tot_ = len(re.sub(r'\s|\{r:|\{k:|\}|==|\*\*|\[\[[^\]]*\]\]', '', body_t)); red_ = sum(len(re.sub(r'\s', '', x)) for x in re.findall(r'\{r:([^{}]*)\}', body_t) if kc_(x) == 'k')
            if tot_ > 80 and red_ / tot_ > 0.30: warns.append(f'{nm}: 빨강 {round(red_ / tot_ * 100)}% (30% 넘음 — 🔑·⚡와 겹치는 본문 {{r:}}는 **굵게**로)')
            items = sum(1 for b in c['body'] if b[0] == 'b'); heads = sum(1 for b in c['body'] if b[0] == 'h')
            if heads == 0 and items == 0: warns.append(f'{nm}: # 소제목·- 항목이 하나도 없음(🔑 줄에 몰아씀?)')
        for i in sorted(linked | exam):
            if i not in Q: errs.append(f'없는 문항 id {i}')
        want = set(bylec.get(k, [])) | set(also)
        cur = {i for i in want if i in Q and Q[i]['tier'] != 'C'}
        miss = sorted(cur - exam)
        if miss: errs.append(f'이 강의 기출인데 ⭐(E:)에 없음: {",".join(miss)}')
        for ck, p_, nm in cites:
            if ck not in S.LECMAP: errs.append(f'{nm}: 없는 강의 키 {ck}'); continue
            if not S.LECMAP[ck][0]: continue
            ps = str(p_)
            if not ps.isdigit(): errs.append(f'{nm}: [[{ck}:{ps}]] 쪽 번호가 숫자가 아님'); continue
            f = S.lec_img_path(ck, int(ps))
            if not os.path.exists(f) and not os.path.exists(os.path.dirname(f)): warns.append(f'{nm}: {ck} 쪽 이미지 폴더 없음(옛 이미지만 있을 수 있음)')
            elif not os.path.exists(f): errs.append(f'{nm}: {ck} p.{ps} 쪽 이미지 없음(쪽수 초과?)')
        cov = set()
        for c in L['cards']: cov |= ranges(c['rng'])
        n = L['pages']
        if n:
            gap = sorted(set(range(1, n + 1)) - cov)
            if gap:
                runs, st = [], None
                for x in gap:
                    if st is None or x != prev + 1:
                        if st is not None: runs.append((st, prev))
                        st = x
                    prev = x
                runs.append((st, prev))
                warns.append('카드 쪽 범위에 빠진 쪽: ' + ', '.join(f'{a}' if a == b else f'{a}-{b}' for a, b in runs) + ' (표지·목차·참고문헌이면 무시)')
        # 26 바뀐 곳 표시(10-10): 25·26 둘 다 있는 강의(IMG_ALIAS 25 키 → 이 26 키)인데 @UPD가 없거나, @UPD 줄이 150자 넘음
        LM = getattr(S, 'LECMAP', {}); src25 = [a5 for a5, kk in getattr(S, 'IMG_ALIAS', {}).items() if kk == k and '25' in str(LM.get(a5, ('', ''))[1])]
        if src25 and '26' in str(LM.get(k, ('', ''))[1]) and not L.get('upd'):
            warns.append(f'26 갱신 강의(25 = {"·".join(src25)})인데 @UPD 없음 — 25 ↔ 26 바뀐 곳 표시(UPD26MARK_BRIEF · 대조표 없으면 끝 절 · AGENTS B3)')
        for u_ in L.get('upd', []):
            n_ = len(re.sub(r'\[\[[^\]]*\]\]|\{u:|\{e:|\{n:|\{r:|[{}]', '', u_).strip())
            if n_ > 150: warns.append(f'@UPD {n_}자(150자 넘음): "{u_[:40]}…"')
        C = len(L['cards']); B = sum(1 for c in L['cards'] for b in c['body'] if b[0] == 'b'); T = sum(1 for c in L['cards'] for b in c['body'] if b[0] == 'T')
        E = sum(1 for c in L['cards'] for b in c['body'] if b[0] == 'E'); F = sum(len(c['figs']) for c in L['cards']); M = sum(len(c['recall']) for c in L['cards'])
        print(f'{"✓" if not errs else "✗"} {sid}/{k}: 카드 {C} · 항목 {B} · 표 {T} · ⭐ {E} · 그림 {F} · 암기 {M} · 쪽 {n}   (승인 기준 DD1: 카드 19 · 항목 75 · 표 4 · ⭐ 19 · 그림 40 · 75쪽)')
        for e in errs: print('   ✗', e)
        for w in warns[:25]: print('   ·', w)
        bad_total += bool(errs)
    if ktot[0]:
        print(f'🔑 렌더(ux3 N): 🔑 {ktot[0]} · 요지 {ktot[1]} · 옛 렌더와 글자 다름 {ktot[2]} · key_lines 되돌림 {LP.KL[2]} · 80자 넘는 한 줄 덩어리 {ktot[3]} → {ktot[4]} (🔑 상자 기준 — 정리표 🔑 칸도 같은 수)')
        if LP.KL[2]: print('   · key_lines가 글자 차이로 옛 렌더로 되돌린 🔑이 있음(구조만 옛 모양)')
    return bad_total

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    also = []
    if '--also' in a: i = a.index('--also'); also = a[i + 1].split(','); a = a[:i] + a[i + 2:]
    sys.exit(1 if main(a[0].upper(), a[1:], also) else 0)
