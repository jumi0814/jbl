"""카드 식별자(aid) 고정 — tools/<sid>/aid_lock.json 관리 (build4가 호출, 모든 과목 공통).

사용자의 형광펜·빈칸(ann.<SID>)과 '이해함'(done.<SID>)은 카드 aid에 저장된다. aid는 원래 강의키 + slug(영문 제목, 국문 부제)라서
원고를 다시 쓰며 제목 한 글자만 바뀌어도 새 aid가 되어 표시가 떨어져 나갔다. 이 모듈은 빌드마다 새 카드를 옛 카드와 맞춰
옛 aid를 이어받게 한다.

aid_lock.json = {강의키: [{aid, en, ko, sig:[정규화 문장 앞 20개의 md5 8자리], gone?:1}]}
- 점수 = 제목 유사도(SequenceMatcher, 'en | ko') × 0.4 + 문장 Jaccard(sig 집합) × 0.6
- 점수 0.5 이상인 쌍을 높은 순으로: 옛 aid가 아직 안 쓰였으면 그 카드의 aid로
- 카드가 나뉨: 이미 다른 카드가 가져간 옛 aid는, 점수 0.5 이상이거나 새 카드 문장의 절반 이상(2문장↑)이 그 옛 카드에서 왔으면 이 카드의 alt로
- 짝을 못 찾은 옛 aid는 가장 비슷한 카드의 alt에 이어 붙임(→ 허브가 표시·✓를 그 카드로 옮기고, 못 찾으면 '위치 잃음'으로 보존)
- 한 번 잠긴 aid는 lock에서 지우지 않음(gone=1로 남겨 다음 빌드에도 alt로 계속 이어짐)
- 원고 파일은 건드리지 않음. 잠금이 없는 강의는 기존 규칙(card_aid)으로 만들고 잠금에 추가
"""
import os, re, json, hashlib, difflib

W_TITLE, W_SENT, TH = 0.4, 0.6, 0.5
NSIG = 20


def _norm(s):
    s = re.sub(r'\{[a-z]:', '', s)
    s = s.replace('==', '').replace('**', '')
    return re.sub(r'[^0-9a-z가-힣]+', '', s.lower())


def sentences(c):
    """카드의 문장(한 줄 = 한 사실) 목록 — 요지·🔑·소제목·항목·표 행·⭐·💬·✍·⚡ 순서"""
    out = [c.get('gist', '')]
    for t, v in c.get('body', []):
        if t in ('K', 'h', 'b', 'P', 'U'): out.append(v)
        elif t == 'T': out += [' '.join(r) for r in v]
        elif t == 'E': out.append(v[1])
    out += c.get('recall', [])
    return [n for n in (_norm(x) for x in out) if n]


def sig(c):
    return [hashlib.md5(x.encode('utf-8')).hexdigest()[:8] for x in sentences(c)[:NSIG]]


def title(c):
    return (c.get('en', '') + ' | ' + c.get('ko', '')).lower()


def tokens(c):
    """카드 전체 글의 단어 집합(영문·한글 2자 이상, 숫자 포함 단어) — 문장이 다시 쓰여도 같은 주제면 많이 겹침"""
    txt = ' '.join([c.get('en', ''), c.get('ko', ''), c.get('gist', '')] + [v if isinstance(v, str) else (' '.join(' '.join(r) for r in v) if t == 'T' else (v[1] if t == 'E' else '')) for t, v in c.get('body', []) if t != 'F'] + c.get('recall', []))
    txt = re.sub(r'\{[a-z]:|\}|==|\*\*|\[\[[^\]]*\]\]|\{jb:[^}]*\}', ' ', txt.lower())
    return {w for w in re.findall(r'[a-z][a-z0-9\-]{1,}|[가-힣]{2,}|\d+[a-z%]+', txt)}


def score(new, old):
    """제목이 같으면 1.0(우선). 아니면 제목 유사도 × 0.4 + 내용 유사도 × 0.6.
    내용 유사도 = 옛 항목에 단어 집합(tok, tools/aidlock_enrich.py)이 있으면 단어 겹침 비율(작은 쪽 기준), 없으면 문장 해시 Jaccard."""
    if new.get('en') == old.get('en') and new.get('ko') == old.get('ko'): return 1.0
    t = difflib.SequenceMatcher(None, title(new), (old.get('en', '') + ' | ' + old.get('ko', '')).lower()).ratio()
    if old.get('tok'):
        a, b = new.setdefault('_tok', tokens(new)), set(old['tok'])
        j = len(a & b) / min(len(a), len(b)) if a and b else 0.0
    else:
        a, b = set(new['_sig']), set(old.get('sig', []))
        j = len(a & b) / len(a | b) if (a or b) else 0.0
    return W_TITLE * t + W_SENT * j


def assign(k, cards, old, fresh):
    """k: 강의키, cards: lecparse 카드 목록, old: 잠금 항목 목록(없으면 []), fresh(j, c) → 기존 규칙 aid.
    반환 (aids[j], alts[j] = [옛 aid...], 새 잠금 목록, 통계 {keep, moved, new})"""
    for c in cards: c['_sig'] = sig(c)
    n = len(cards)
    aids, alts = [None] * n, [[] for _ in range(n)]
    st = {'keep': 0, 'moved': 0, 'new': 0}
    if not old:
        used = set()
        for j, c in enumerate(cards):
            a = fresh(j, c); base, q = a, 2
            while a in used: a = f'{base}~{q}'; q += 1
            used.add(a); aids[j] = a; st['new'] += 1
    else:
        S = [[score(c, o) for o in old] for c in cards]
        pairs = sorted(((S[j][i], j, i) for j in range(n) for i in range(len(old)) if S[j][i] >= TH), key=lambda x: (-x[0], x[1], x[2]))
        taken = {}                                     # 옛 항목 i → 카드 j
        for s_, j, i in pairs:
            if i not in taken and aids[j] is None: taken[i] = j; aids[j] = old[i]['aid']
        # 나뉜 카드: 옛 aid를 다른 카드의 alt로 — 점수 0.5 이상이거나, 새 카드 문장의 절반 이상(2문장 이상)이 그 옛 카드에서 온 경우
        for j, c in enumerate(cards):
            a = set(c['_sig'])
            for i, o in enumerate(old):
                if taken.get(i) is None or taken[i] == j or o['aid'] in alts[j]: continue
                sh = len(a & set(o.get('sig', [])))
                if S[j][i] >= TH or (a and sh >= 2 and sh / len(a) >= 0.5): alts[j].append(o['aid'])
        used = {a for a in aids if a} | {o['aid'] for o in old}
        for j, c in enumerate(cards):
            if aids[j] is None:
                a = fresh(j, c); base, q = a, 2
                while a in used: a = f'{base}~{q}'; q += 1
                used.add(a); aids[j] = a; st['new'] += 1
            elif any(old[i]['aid'] == aids[j] and _same_title(c, old[i]) for i in range(len(old))): st['keep'] += 1
            else: st['moved'] += 1
        for i, o in enumerate(old):                     # 짝 없는 옛 aid → 가장 비슷한 카드의 alt
            if i in taken or not n: continue
            j = max(range(n), key=lambda j_: (S[j_][i], -j_))
            if o['aid'] not in alts[j] and o['aid'] != aids[j]: alts[j].append(o['aid'])
    lock = [{'aid': aids[j], 'en': c['en'], 'ko': c['ko'], 'sig': c['_sig'], 'tok': sorted(c.get('_tok') or tokens(c))} for j, c in enumerate(cards)]
    cur = {x['aid'] for x in lock}
    lock += [dict(o, gone=1) for o in (old or []) if o['aid'] not in cur]
    for c in cards: c.pop('_sig', None); c.pop('_tok', None)
    return aids, alts, lock, st


def _same_title(c, o):
    return c.get('en') == o.get('en') and c.get('ko') == o.get('ko')


def load(path):
    try: return json.load(open(path, encoding='utf-8'))
    except FileNotFoundError: return {}


def save(path, lock):
    t = json.dumps(lock, ensure_ascii=False, indent=0, sort_keys=True)
    if not os.path.exists(path) or open(path, encoding='utf-8').read() != t:
        open(path, 'w', encoding='utf-8').write(t)
