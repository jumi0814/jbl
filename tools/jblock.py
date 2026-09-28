"""JB 문항 id 잠금(C09) — 채점·형광펜·플래시카드 기록이 다른 문제에 붙지 않게.
tools/<sid>/jb_lock.json = {id: md5(공백 뺀 문제 글자 앞 80자)[:12]} — build4가 새 id만 추가(있는 항목은 바꾸지 않음, 커밋 대상).
있던 id의 해시가 바뀌거나 id가 사라지면 verify.py가 실패하고 옮김 표 tools/<sid>/jb_move.json({옛 id: 새 id})를 요구 —
옮김 표가 있으면 build4가 팩에 p.jbmove·p.jbmovev(표 지문)를 넣고, 허브가 과목을 열 때 한 번 mk·log·fc J:·ann 키를 옮김(LS jbmoved.<S>.<jbmovev>).
같은 id인데 문제 글자만 고친 것이면 {id: id}로 적어 확인만 함(옮길 것 없음)."""
import os, re, json, hashlib
TOOLS = os.path.dirname(os.path.abspath(__file__))
def qhash(qt): return hashlib.md5(re.sub(r'\s+', '', qt or '')[:80].encode('utf-8')).hexdigest()[:12]
def paths(sid):
    d = os.path.join(TOOLS, sid.lower()); return os.path.join(d, 'jb_lock.json'), os.path.join(d, 'jb_move.json')
def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return {} if d is None else d
def update(sid, cur):
    """cur = {id: 해시}(이번 빌드) → 잠금에 새 id만 더해 저장. 돌려줌: (잠금, 옮김 표, 새로 더한 id)"""
    lp, mp = paths(sid); lock = load(lp); added = [i for i in cur if i not in lock]
    for i in added: lock[i] = cur[i]
    if added or not os.path.exists(lp):
        json.dump(dict(sorted(lock.items())), open(lp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    return lock, load(mp), added
def check(sid, cur, lock, move):
    """잠금과 이번 빌드 비교 — 옮김 표에 있는 옛 id는 새 id가 팩에 있는지만. 돌려줌: 오류 목록"""
    err = []
    for i, h in lock.items():
        if i in move:
            if move[i] not in cur: err.append(f'{i}→{move[i]}: 새 id가 팩에 없음')
            continue
        if i not in cur: err.append(f'{i}: id가 사라짐')
        elif cur[i] != h: err.append(f'{i}: 문제 글자가 바뀜')
    return err
def need_msg(sid): return f'옮김 표 tools/{sid.lower()}/jb_move.json(old→new) 필요'
def lock_errors(docs):
    """docs/packs/<SID>.js마다 팩의 jbhash를 잠금·옮김 표와 비교 → [(파일, 잠금 수, 오류 목록)] (verify.py·회귀용)"""
    out = []; d = os.path.join(docs, 'packs')
    for f in sorted(os.listdir(d)):
        if '.img.' in f or not f.endswith('.js') or f.endswith('.lx.js'): continue
        t = open(os.path.join(d, f), encoding='utf-8').read(); pk = json.loads(t[t.index('{'):t.rindex('}') + 1])
        if 'jbhash' not in pk: out.append((f, 0, ['팩에 jbhash 없음 — 다시 빌드'])); continue
        lp, mp = paths(pk['id']); lock = load(lp); out.append((f, len(lock), check(pk['id'], pk['jbhash'], lock, load(mp)) + ([] if lock else ['잠금 파일 없음'])))
    return out
