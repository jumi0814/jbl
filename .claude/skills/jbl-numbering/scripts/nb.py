#!/usr/bin/env python3
"""JBL 넘버링 제작 세션 도구 — JBL '내 넘버링' ChatGPT 내보내기 JSON(format jbl-numbering, v1)을 그대로 받아
문제마다 제작·검수 기록을 남기고, 검수 통과 스토리만 JBL '결과 가져오기'에 넣을 JSON으로 돌려준다.

  원본 보존: source.json은 받은 그대로(읽기만) · 결과 JSON의 id·q·s0는 원본에서 그대로 복사(문제·답안·출처·연도는 JBL에 그대로 남음 — 가져오기는 스토리만 바꿈)
  스토리 보호: 원본에 스토리가 있던 문제(story가 있거나 s0 ≠ '0')는 'keep' — 사용자가 고치기를 부탁한 id(--revise)만 다시 씀
  보류 분리: hold = 결과 JSON에 넣지 않음(hold.md에 이유·최선안만)
  이어하기: state.json(원자적 저장) · checkpoint(한 파일 — 다른 세션·기기에서 start --from)

명령(저장소 루트에서, 받은 파일은 -I로):
  .venv/bin/python -I .claude/skills/jbl-numbering/scripts/nb.py start EXPORT.json [--name 이름] [--revise all|id,id]
  … next 이름 [--n 1]              다음 제작할 문제(문제·정답·관련 문제)
  … show 이름 ID                   한 문제 전부(시도 기록 포함)
  … save 이름 ID --status pass|hold|todo [--story-file F | --story S] [--review-file F | --review S] [--allow-kw 키워드]
  … status 이름                    상태별 수 · 보류 이유
  … blind 이름 [--ids a,b]         독립 검수용 — 문제 + 괄호를 뺀 스토리만(정답 없음)
  … export 이름 [--out 경로] [--print]   통과 스토리만 JBL 가져오기 JSON(+ hold.md)
  … verify 이름 결과.json          결과 JSON을 원본과 견주기
  … checkpoint 이름 [--out 경로]    이어하기용 한 파일
  … start --from 체크포인트.json [--name 이름]
  … feedback 이름 ID --verdict approve|reject --text "사용자 말 그대로"
세션 폴더: work/numbering/<이름>/ (커밋 안 함 · 환경변수 JBL_NB_HOME으로 바꿀 수 있음)"""
import argparse, copy, json, os, re, sys, tempfile, unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4] if len(Path(__file__).resolve().parents) > 4 else Path.cwd()
HOME = Path(os.environ.get('JBL_NB_HOME') or (ROOT / 'work' / 'numbering'))
FMT, V = 'jbl-numbering', 1
STATUSES = ('todo', 'pass', 'hold', 'keep')
NOW = lambda: datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


class Bad(Exception):
    pass


def uniq_pairs(pairs):
    o = {}
    for k, v in pairs:
        if k in o:
            raise Bad(f'JSON 안에 같은 키가 두 번: {k}')
        o[k] = v
    return o


def load_json_text(txt):
    s = txt.lstrip('﻿').strip()
    m = re.search(r'```(?:json)?\s*([\s\S]*?)```', s)   # 채팅에서 코드 블록째 붙여 넣은 것도
    if m and re.search(r'[{\[]', m.group(1)):
        s = m.group(1).strip()
    return json.loads(s, object_pairs_hook=uniq_pairs)


def load(path):
    with open(path, encoding='utf-8') as f:
        return load_json_text(f.read())


def atomic(path, value, text=False):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f'.{path.name}.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            if text:
                f.write(value)
            else:
                json.dump(value, f, ensure_ascii=False, indent=1); f.write('\n')
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def items_of(src):
    """원본(JBL 내보내기) 검사 → [(강의 이름, item)] — 형식이 다르면 멈춤(고치지 않음)"""
    if not isinstance(src, dict):
        raise Bad('JBL 내보내기 JSON이 아니에요(맨 위가 객체가 아님)')
    if src.get('format') != FMT:
        raise Bad(f"format이 '{FMT}'가 아니에요: {str(src.get('format'))[:40]}")
    if not isinstance(src.get('v'), int) or src['v'] > V:
        raise Bad(f"지원하지 않는 판(v={src.get('v')}) — 이 도구는 v{V}까지")
    for k in ('sid', 'batch', 'lecs'):
        if k not in src:
            raise Bad(f'맨 위에 {k}가 없어요')
    if not isinstance(src['lecs'], list):
        raise Bad('lecs가 배열이 아니에요')
    out, seen = [], set()
    for gi, g in enumerate(src['lecs']):
        if not isinstance(g, dict) or not isinstance(g.get('items'), list):
            raise Bad(f'lecs[{gi}].items가 배열이 아니에요')
        for it in g['items']:
            if not isinstance(it, dict):
                raise Bad(f'lecs[{gi}]: 문제가 객체가 아니에요')
            for k in ('id', 'q', 'a', 'story', 's0'):
                if k not in it:
                    raise Bad(f"lecs[{gi}] 문제 {it.get('id', '?')}: {k}가 없어요")
            if not isinstance(it['id'], str) or not it['id'].strip():
                raise Bad(f'lecs[{gi}]: id가 비었거나 글이 아니에요')
            for k in ('q', 'a', 'story', 's0'):
                if not isinstance(it[k], str):
                    raise Bad(f"{it['id']}: {k}가 글이 아니에요")
            if it['id'] in seen:
                raise Bad(f"같은 id가 두 번: {it['id']}")
            seen.add(it['id']); out.append((g.get('lec', ''), it))
    if not out:
        raise Bad('문제가 하나도 없어요')
    return out


def has_story(it):
    return bool(it['story'].strip()) or (it['s0'].strip() not in ('', '0'))   # 스토리를 빼고 내보내도 s0(지문)가 '0'이 아니면 JBL에 스토리가 있음


def sdir(name):
    if not re.fullmatch(r'[\w.\-가-힣]{1,60}', name or ''):
        raise Bad('세션 이름은 글자·숫자·._- 60자까지')
    return HOME / name


def read_state(name):
    d = sdir(name)
    if not (d / 'state.json').exists():
        raise Bad(f'세션이 없어요: {name} (start로 만드세요 — 폴더 {d})')
    return d, load(d / 'source.json'), load(d / 'state.json')


def write_state(d, st):
    st['u'] = NOW(); atomic(d / 'state.json', st)


# ---------- 글 ----------
PUNCT = re.compile(r"[\s \-–—_.,·:;!?'\"“”‘’/\\()\[\]{}<>~*=+|#%&^`$@]")
def norm(s):
    return PUNCT.sub('', unicodedata.normalize('NFKC', str(s or '')).lower())


PAREN = re.compile(r'[(（]([^()（）]{1,80})[)）]')
def kws(story):
    return [m.group(1).strip() for m in PAREN.finditer(story)]


def strip_paren(story):
    return re.sub(r'\s*[(（][^()（）]{1,80}[)）]', '', story)


ITEM = re.compile(r'(?m)^\s*(?:\(?\d{1,2}[.)]|[①-⑳]|[-•▪◦➢*]|[a-zA-Z][.)]|[가-하][.)])\s*\S')
def est_items(a):
    lines = [l for l in a.splitlines() if l.strip()]
    n = len(ITEM.findall(a))
    if n < 2:
        n = max(n, len(re.findall(r'(?:^|[\s,;])(?:\d{1,2}[.)]|[①-⑳])\s*\S', a)))
    return n or len(lines)


def check_story(story, it, allow=()):
    """저장(pass) 전 형식 검사 — 창작 품질은 여기서 판단하지 않음(사람·모델 검수 몫). 돌려주는 값: (오류 목록, 경고 목록)"""
    err, warn = [], []
    s = story.strip()
    if not s:
        err.append('스토리가 비었어요')
        return err, warn
    if re.search(r'<[a-zA-Z/][^>]*>', s):
        err.append('HTML 태그는 쓰지 않아요(줄바꿈·**굵게**만)')
    if len(s) > 700:
        err.append(f'너무 길어요({len(s)}자) — 짧은 장면으로 다시(승인 예시는 100~200자)')
    elif len(s) > 380:
        warn.append(f'길어요({len(s)}자) — 승인 예시(100~200자)보다 많이 김: 정말 필요한지 검토')
    A = norm(it['a']); allowN = {norm(x) for x in allow}
    K = kws(s)
    if not K:
        err.append('괄호 키워드가 없어요 — 단서 바로 뒤에 정답 원문 핵심어를 (괄호)로')
    for k in K:
        nk = norm(k)
        if not nk:
            err.append(f'빈 괄호: ({k})')
            continue
        if nk not in A and nk not in allowN:
            err.append(f"괄호 '{k}'가 정답 원문(a)에 없어요 — 원문 글자 그대로의 가장 짧은 핵심어로(번역·풀이 금지 · 정말 필요하면 --allow-kw)")
        words = len(k.split())
        if words > 5 or len(k) > 45:
            err.append(f"괄호 '{k}'가 길어요 — 답안 문장이 아니라 가장 짧은 핵심어만")
        elif words > 3:
            warn.append(f"괄호 '{k}'가 3단어보다 김 — 더 짧게 줄일 수 있는지")
    dup = {k for k in K if K.count(k) > 1}
    if dup:
        warn.append('같은 괄호가 여러 번: ' + ', '.join(sorted(dup)))
    n = est_items(it['a'])
    if K and n and len(K) < n:
        warn.append(f'정답 항목(추정 {n}개)보다 괄호({len(K)}개)가 적어요 — 빠진 항목이 없는지(묶음·해설 줄이면 괜찮음)')
    bare = strip_paren(s)
    if len(norm(bare)) < len(norm(s)) * 0.45:
        warn.append('괄호를 빼면 남는 글이 너무 적어요 — 괄호가 단서를 대신하고 있지 않은지')
    return err, warn


# ---------- 명령 ----------
def cmd_start(a):
    if a.frm:
        cp = load(a.frm)
        if not isinstance(cp, dict) or cp.get('format') != 'jbl-numbering-session':
            raise Bad('체크포인트 파일이 아니에요')
        src, st = cp['source'], cp['state']
        items_of(src)
        name = a.name or st.get('name')
    else:
        src = load(a.src); items_of(src)
        name = a.name or ('s' + datetime.now().strftime('%m%d_%H%M') + '_' + re.sub(r'[^\w]', '', str(src.get('sid')))[:12])
        st = None
    d = sdir(name)
    if (d / 'state.json').exists() and not a.force:
        raise Bad(f'이미 있는 세션이에요: {name} — 이어서 하려면 next/status, 새로 시작하려면 다른 --name')
    if st is None:
        rv = set() if not a.revise else ({'*'} if a.revise == 'all' else {x.strip() for x in a.revise.split(',') if x.strip()})
        st = {'format': 'jbl-numbering-state', 'v': 1, 'name': name, 'c': NOW(), 'sid': src.get('sid'), 'subject': src.get('subject', ''), 'batch': src.get('batch'), 'items': {}}
        ids = set()
        for lec, it in items_of(src):
            ids.add(it['id']); ex = has_story(it); rev = '*' in rv or it['id'] in rv
            st['items'][it['id']] = {'lec': lec, 'status': 'todo' if (not ex or rev) else 'keep', 'had': ex, 'revise': bool(ex and rev), 'story': '', 'review': '', 'attempts': [], 'user': []}
        miss = rv - ids - {'*'}
        if miss:
            raise Bad('--revise에 없는 id: ' + ', '.join(sorted(miss)))
    atomic(d / 'source.json', src); write_state(d, st)
    print(summary(src, st))


def summary(src, st):
    c = {k: 0 for k in STATUSES}
    for x in st['items'].values():
        c[x['status']] = c.get(x['status'], 0) + 1
    keep = [i for i, x in st['items'].items() if x['status'] == 'keep']
    rev = [i for i, x in st['items'].items() if x.get('revise')]
    lines = [f"세션 {st['name']} · 과목 {st.get('subject') or st.get('sid')} · 문제 {len(st['items'])}",
             f"  제작할 문제(todo) {c['todo']} · 통과(pass) {c['pass']} · 보류(hold) {c['hold']} · 보호(keep — 이미 스토리 있음) {c['keep']}"]
    if keep:
        lines.append('  보호(건드리지 않음): ' + ', '.join(keep[:12]) + (' …' if len(keep) > 12 else ''))
    if rev:
        lines.append('  고치기 허락받은 기존 스토리: ' + ', '.join(rev))
    lines.append(f'  폴더: {sdir(st["name"])}')
    return '\n'.join(lines)


def toks(s):
    return {w for w in re.findall(r'[a-z]{4,}|[가-힣]{2,}', unicodedata.normalize('NFKC', s).lower())} - {'다음', '대해', '쓰시오', '기술하시오', '서술하시오', '설명하시오', '무엇', '가지', 'with', 'from', 'that', 'this', 'which', 'what'}


def related(src_items, it, k=3):
    T = toks(it['q'] + ' ' + it['a'])
    sc = []
    for lec, o in src_items:
        if o['id'] == it['id']:
            continue
        U = toks(o['q'] + ' ' + o['a'])
        if T and U:
            j = len(T & U) / len(T | U)
            if j >= 0.12:
                sc.append((j, o))
    return [o for j, o in sorted(sc, key=lambda x: -x[0])[:k]]


def item_text(src_items, st, it, full=False):
    x = st['items'][it['id']]
    out = [f"■ {it['id']}  [{x['lec']}]  상태 {x['status']}" + (' · 기존 스토리 고치기 허락' if x.get('revise') else ''),
           '문제(q):', it['q'], '정답(a):', it['a'], f'(정답 항목 추정 {est_items(it["a"])}개)']
    if it['story'].strip():
        out += ['기존 스토리(사용자가 쓴 것 — 고치기 허락이 없으면 그대로):', it['story']]
    if x['story']:
        out += ['이 세션 최근 스토리:', x['story']]
    if x['user']:
        out += ['사용자 판정:'] + [f"  {u['at']} {u['verdict']}: {u['text']}" for u in x['user']]
    R = related(src_items, it)
    if R:
        out.append('관련 문제(연결·간섭 검토):')
        for o in R:
            y = st['items'][o['id']]
            out.append(f"  - {o['id']} [{y['status']}] {re.sub(r'\s+', ' ', o['q'])[:90]}" + (f" ⇒ {re.sub(r'\s+', ' ', y['story'])[:80]}" if y['story'] else ''))
    if full and x['attempts']:
        out.append('시도 기록:')
        for t in x['attempts']:
            out.append(f"  · {t['at']} {t['status']}: {re.sub(r'\s+', ' ', t.get('story', ''))[:160]}")
            if t.get('review'):
                out.append('    검수: ' + re.sub(r'\s+', ' ', t['review'])[:300])
    return '\n'.join(out)


def cmd_next(a):
    d, src, st = read_state(a.name); S = items_of(src)
    todo = [it for lec, it in S if st['items'][it['id']]['status'] == 'todo']
    if not todo:
        print('제작할 문제가 없어요 — status로 확인 · export로 결과 만들기'); return
    for it in todo[:a.n]:
        print(item_text(S, st, it)); print()
    print(f'남은 todo {len(todo)}')


def cmd_show(a):
    d, src, st = read_state(a.name); S = items_of(src)
    it = next((o for l, o in S if o['id'] == a.id), None)
    if not it:
        raise Bad(f'없는 id: {a.id}')
    print(item_text(S, st, it, full=True))


def read_arg(text, path):
    if path:
        return Path(path).read_text(encoding='utf-8')
    return text or ''


def cmd_save(a):
    d, src, st = read_state(a.name); S = items_of(src)
    it = next((o for l, o in S if o['id'] == a.id), None)
    if not it:
        raise Bad(f'없는 id: {a.id}')
    x = st['items'][a.id]
    if x['status'] == 'keep':
        raise Bad(f'{a.id}: 사용자가 쓴 스토리가 있는 문제(보호) — 사용자가 고치기를 부탁했을 때만 start --revise로 연 세션에서')
    story = read_arg(a.story, a.story_file).strip().replace('\r\n', '\n')
    review = read_arg(a.review, a.review_file).strip()
    if a.status == 'pass':
        err, warn = check_story(story, it, a.allow_kw or [])
        if err:
            raise Bad('통과로 저장하지 않았어요(형식 오류):\n  - ' + '\n  - '.join(err) + ('\n경고:\n  - ' + '\n  - '.join(warn) if warn else ''))
        if not review or 'G2' not in review:
            raise Bad('통과로 저장하려면 검수 기록(--review)이 필요해요 — REVIEW.md 틀(G1~G8 · 특히 G2 블라인드 복원 목록)')
        for w in warn:
            print('경고:', w)
    elif a.status == 'hold' and not review:
        raise Bad('보류에는 이유(--review)가 필요해요 — 어느 관문에서 왜 막혔는지')
    x['attempts'].append({'at': NOW(), 'status': a.status, 'story': story, 'review': review})
    x['status'] = a.status
    x['story'] = story if a.status == 'pass' else (story if a.status == 'hold' else '')
    x['review'] = review; x['allow'] = list(a.allow_kw or []) if a.status == 'pass' else []
    write_state(d, st)
    if a.status == 'pass':
        print(f'{a.id} 통과 저장 · 괄호 뺀 글(G1 확인용):\n  ' + strip_paren(story).replace('\n', '\n  '))
    else:
        print(f'{a.id} → {a.status} 저장')
    left = sum(1 for v in st['items'].values() if v['status'] == 'todo')
    print(f'남은 todo {left}')


def cmd_status(a):
    d, src, st = read_state(a.name)
    print(summary(src, st))
    H = [(i, x) for i, x in st['items'].items() if x['status'] == 'hold']
    if H:
        print('보류(결과 JSON에 안 넣음):')
        for i, x in H:
            print(f"  - {i}: {re.sub(r'\s+', ' ', x['review'])[:160]}")
    U = [(i, u) for i, x in st['items'].items() for u in x['user']]
    if U:
        print('사용자 판정 기록:')
        for i, u in U:
            print(f"  - {i} {u['verdict']}: {u['text'][:120]}")


def cmd_blind(a):
    d, src, st = read_state(a.name); S = items_of(src)
    want = {x.strip() for x in a.ids.split(',')} if a.ids else None
    n = 0
    for lec, it in S:
        x = st['items'][it['id']]
        if (want and it['id'] not in want) or (not want and x['status'] != 'pass'):
            continue
        if not x['story']:
            continue
        n += 1
        print(f"■ {it['id']}\n문제: {it['q']}\n스토리(괄호 뺌): {strip_paren(x['story'])}\n")
    if not n:
        print('보여 줄 통과 스토리가 없어요')


def build_out(src, st):
    S = items_of(src); groups, gm, n = [], {}, 0
    for lec, it in S:
        x = st['items'][it['id']]
        if x['status'] != 'pass' or not x['story'].strip():
            continue
        if x['had'] and not x.get('revise'):
            continue   # 이중 안전 — 보호 문제는 절대 넣지 않음
        g = gm.get(lec)
        if g is None:
            g = {'lec': lec, 'items': []}; gm[lec] = g; groups.append(g)
        g['items'].append({'id': it['id'], 'q': it['q'], 'story': x['story'], 's0': it['s0']}); n += 1
    out = {'format': FMT, 'v': V, 'sid': src['sid'], 'subject': src.get('subject', ''), 'batch': src['batch'], 'part': src.get('part', ''), 'n': n,
           'made_by': 'claude:jbl-numbering', 'session': st['name'],
           'note': '검수 통과 스토리만 · JBL 내 넘버링 → ChatGPT 결과 가져오기에 파일을 넣거나 이 글 전체를 붙여 넣기 → 미리 보기에서 고른 것만 적용',
           'lecs': groups}
    return out, n


def dump_compact(o):   # JBL 내보내기와 같은 꼴(문제 한 줄씩)
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    return s.replace('[{"id":', '[\n{"id":').replace('},{"id":', '},\n{"id":').replace(',"lecs":[', ',\n"lecs":[')


def cmd_export(a):
    d, src, st = read_state(a.name)
    out, n = build_out(src, st)
    if not n:
        raise Bad('통과한 스토리가 없어요 — 넣을 게 없음')
    txt = dump_compact(out)
    verify_obj(src, st, load_json_text(txt))
    p = Path(a.out) if a.out else d / 'out' / f"JBL_가져오기_{st['name']}_{n}문제.json"
    atomic(p, txt + '\n', text=True)
    H = [(i, x) for i, x in st['items'].items() if x['status'] == 'hold']
    hp = d / 'out' / 'hold.md'
    atomic(hp, '# 보류 — JBL에 넣지 않은 문제\n\n' + ('\n'.join(f"## {i}\n- 이유: {x['review']}\n- 최선안(검수 미통과 · 넣지 말 것): {x['story'] or '없음'}\n" for i, x in H) or '없음\n'), text=True)
    print(f'결과 {p} · 통과 {n}문제 · 보류 {len(H)} → {hp}')
    if a.print:
        print('----- 아래 JSON 전체를 JBL [ChatGPT 결과 가져오기]에 붙여 넣기 -----')
        print(txt)


def verify_obj(src, st, out):
    S = {it['id']: it for l, it in items_of(src)}
    if not isinstance(out, dict) or out.get('format') != FMT or out.get('v') != V:
        raise Bad('결과의 format·v가 JBL 형식이 아니에요')
    if out.get('sid') != src.get('sid') or out.get('batch') != src.get('batch'):
        raise Bad('결과의 sid·batch가 원본과 달라요')
    seen, n = set(), 0
    for g in out.get('lecs', []):
        for it in g.get('items', []):
            i = it.get('id')
            if i not in S:
                raise Bad(f'원본에 없는 id: {i}')
            if i in seen:
                raise Bad(f'결과에 같은 id가 두 번: {i}')
            seen.add(i); o = S[i]; x = st['items'][i]
            if it.get('q') != o['q'] or it.get('s0') != o['s0']:
                raise Bad(f'{i}: q 또는 s0가 원본과 달라요(문제 확인·충돌 방지용 — 한 글자도 바꾸면 안 됨)')
            if set(it) - {'id', 'q', 'story', 's0'}:
                raise Bad(f'{i}: 스토리 말고 다른 칸이 들어 있어요: {sorted(set(it) - {"id", "q", "story", "s0"})}')
            if x['status'] != 'pass' or it.get('story') != x['story']:
                raise Bad(f'{i}: 검수 통과(pass) 스토리가 아니에요')
            if x['had'] and not x.get('revise'):
                raise Bad(f'{i}: 사용자 스토리 보호 문제가 들어 있어요')
            err, _ = check_story(it['story'], o, x.get('allow', []))
            if err:
                raise Bad(f'{i}: ' + '; '.join(err))
            n += 1
    return n


def cmd_verify(a):
    d, src, st = read_state(a.name)
    n = verify_obj(src, st, load(a.file))
    print(f'확인 끝 — {n}문제 · id·q·s0 원본 그대로 · 통과 스토리만 · 보호 문제 없음')


def cmd_checkpoint(a):
    d, src, st = read_state(a.name)
    p = Path(a.out) if a.out else d / 'out' / f"이어하기_{st['name']}.json"
    atomic(p, {'format': 'jbl-numbering-session', 'v': 1, 'at': NOW(), 'source': src, 'state': st})
    print(f'체크포인트 {p} — 다른 세션에서: nb.py start --from {p.name} [--name 새이름]')


def cmd_feedback(a):
    d, src, st = read_state(a.name)
    if a.id not in st['items']:
        raise Bad(f'없는 id: {a.id}')
    x = st['items'][a.id]
    x['user'].append({'at': NOW(), 'verdict': a.verdict, 'text': a.text, 'story': x['story']})
    if a.verdict == 'reject':
        x['attempts'].append({'at': NOW(), 'status': 'user-rejected', 'story': x['story'], 'review': a.text})
        x['status'] = 'todo'; x['story'] = ''; x['review'] = ''
    write_state(d, st)
    print(f'{a.id} 사용자 판정 {a.verdict} 기록' + (' · 다시 todo(거절된 스토리는 다시 쓰지 않음)' if a.verdict == 'reject' else ''))
    print('다음: FEEDBACK.md에 한 줄(날짜·문제·판정·원인·규칙) · 승인 → EXEMPLARS 성공, 거절 → 실패 사례 · 남은 todo·통과본에 새 규칙 다시 적용')


def main():
    p = argparse.ArgumentParser(description='JBL 넘버링 제작 세션 도구')
    c = p.add_subparsers(dest='cmd', required=True)
    s = c.add_parser('start'); s.add_argument('src', nargs='?'); s.add_argument('--name'); s.add_argument('--revise'); s.add_argument('--from', dest='frm'); s.add_argument('--force', action='store_true')
    s = c.add_parser('next'); s.add_argument('name'); s.add_argument('--n', type=int, default=1)
    s = c.add_parser('show'); s.add_argument('name'); s.add_argument('id')
    s = c.add_parser('save'); s.add_argument('name'); s.add_argument('id'); s.add_argument('--status', required=True, choices=('pass', 'hold', 'todo'))
    s.add_argument('--story'); s.add_argument('--story-file'); s.add_argument('--review'); s.add_argument('--review-file'); s.add_argument('--allow-kw', action='append')
    s = c.add_parser('status'); s.add_argument('name')
    s = c.add_parser('blind'); s.add_argument('name'); s.add_argument('--ids')
    s = c.add_parser('export'); s.add_argument('name'); s.add_argument('--out'); s.add_argument('--print', action='store_true')
    s = c.add_parser('verify'); s.add_argument('name'); s.add_argument('file')
    s = c.add_parser('checkpoint'); s.add_argument('name'); s.add_argument('--out')
    s = c.add_parser('feedback'); s.add_argument('name'); s.add_argument('id'); s.add_argument('--verdict', required=True, choices=('approve', 'reject')); s.add_argument('--text', required=True)
    a = p.parse_args()
    if a.cmd == 'start' and not a.src and not a.frm:
        p.error('start에는 내보내기 JSON 경로나 --from 체크포인트가 필요해요')
    {'start': cmd_start, 'next': cmd_next, 'show': cmd_show, 'save': cmd_save, 'status': cmd_status, 'blind': cmd_blind,
     'export': cmd_export, 'verify': cmd_verify, 'checkpoint': cmd_checkpoint, 'feedback': cmd_feedback}[a.cmd](a)


if __name__ == '__main__':
    try:
        main()
    except (Bad, OSError, json.JSONDecodeError) as e:
        sys.exit(f'오류: {e}')
