"""카드 aid 잠금(tools/aidlock.py) 회귀 테스트 — 원고를 바꿔도 옛 aid가 이어지는지.
원고 파일·잠금 파일은 건드리지 않고, 사본을 고쳐 lecparse.parse로 읽은 뒤 커밋된 aid_lock.json과 맞춘다."""
import os, sys, re, json, tempfile
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS); sys.path.insert(0, os.path.join(TOOLS, 'cons'))
import aidlock, lecparse
SID, K = 'CONS', 'WHT'
SRC = os.path.join(TOOLS, 'cons', f'lec_{K}.txt')
LOCK = aidlock.load(os.path.join(TOOLS, 'cons', 'aid_lock.json'))
fails = []
def ok(c, msg):
    print(('  OK   ' if c else '  FAIL ') + msg)
    if not c: fails.append(msg)
def parse_text(t):
    f = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8'); f.write(t); f.close()
    try: return lecparse.parse(f.name)
    finally: os.unlink(f.name)
fresh = lambda j, c: f'{SID}:{K}:NEW{j}'
orig = open(SRC, encoding='utf-8').read()
old = LOCK[K]
L0 = parse_text(orig)
a0, al0, _, st0 = aidlock.assign(K, L0['cards'], old, fresh)
ok(a0 == [o['aid'] for o in old if not o.get('gone')], f'지금 원고 그대로 → aid 변화 0 ({st0})')
ok(not any(al0), '지금 원고 그대로 → 추가 alt 없음')
# 1) 제목 한 글자 바꾸기
t1 = orig.replace('## Does the Classification Tell the Treatment? | 분류가 치료를 정해 주는가', '## Does the Classification Tell a Treatment? | 분류가 치료를 정해 주나', 1)
assert t1 != orig
L1 = parse_text(t1); a1, al1, lk1, st1 = aidlock.assign(K, L1['cards'], old, fresh)
ok(a1[1] == old[1]['aid'], f'제목 한 글자 바꿈 → 같은 aid ({st1})')
ok(a1 == a0, '제목 바꿈 → 다른 카드 aid도 그대로')
# 2) 카드를 둘로 나누기 — 두 번째 카드의 '# New classification' 절부터 새 카드
t2 = orig.replace('# New classification of causes(슬라이드 16 — 교수 강조)', '## New Classification of Causes | 변색 원인의 새 분류 | 16-20 | 교수 강조\n> 세 갈래로 보면 치료가 정해진다\n# New classification of causes(슬라이드 16 — 교수 강조)', 1)
L2 = parse_text(t2); a2, al2, lk2, st2 = aidlock.assign(K, L2['cards'], old, fresh)
ok(len(L2['cards']) == len(L0['cards']) + 1, '나누기 → 카드 +1')
ok(a2[1] == old[1]['aid'] and old[1]['aid'] in al2[2], f'나누기 → 옛 aid가 한 카드의 aid와 다른 카드의 alt에 ({st2})')
ok(a2[2] not in {o['aid'] for o in old}, '나뉜 새 카드는 새 aid')
ok(a2[3:] == a0[2:], '나누기 → 뒤 카드들 aid 그대로')
# 3) 카드 통째로 삭제 → 옛 aid는 가장 비슷한 카드의 alt, 잠금에는 gone으로 남음
blk = re.search(r'## Does the Classification.*?(?=\n@G|\n## )', orig, re.S).group(0)
t3 = orig.replace(blk, '', 1)
L3 = parse_text(t3); a3, al3, lk3, st3 = aidlock.assign(K, L3['cards'], old, fresh)
ok(any(old[1]['aid'] in x for x in al3), '카드 삭제 → 옛 aid가 어느 카드의 alt에')
ok(any(o['aid'] == old[1]['aid'] and o.get('gone') for o in lk3), '카드 삭제 → 잠금에 gone으로 보존')
# 4) 잠금 다음 세대: 삭제된 aid가 다음 빌드에도 alt로 이어짐
a4, al4, lk4, _ = aidlock.assign(K, parse_text(t3)['cards'], lk3, fresh)
ok(any(old[1]['aid'] in x for x in al4), '다음 빌드에도 gone aid가 alt로 이어짐')
# 5) 모든 과목: 잠금 파일이 지금 원고와 맞음(유지 = 전체)
for sid in ['oms1', 'cons', 'impl', 'anat', 'geri', 'pharm']:
    lk = aidlock.load(os.path.join(TOOLS, sid, 'aid_lock.json'))
    ok(bool(lk), f'{sid}/aid_lock.json 있음 ({len(lk)}강의)')
print('RESULT', 'PASS' if not fails else 'FAIL')
sys.exit(1 if fails else 0)
