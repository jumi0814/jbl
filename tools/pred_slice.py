"""예상문제 조각 만들기(pred_merge의 짝): tools/<sid>/pred.txt에서 강의 키들의 블록만 뽑아 work/<SID>/pred26/<이름>.txt로(지금 글 그대로 — 담당이 고친 뒤 pred_merge로 되돌림)
사용: .venv/bin/python tools/pred_slice.py <SID> <이름> <KEY> [<KEY>…]   (10-27 예상 전면 정돈 — guide/handoff/PRED_REV1027_BRIEF.md)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jblpaths as J
from pred_merge import split
sid, name, keys = sys.argv[1].upper(), sys.argv[2], set(a.upper() for a in sys.argv[3:])
src = open(os.path.join(J.TOOLS, sid.lower(), 'pred.txt'), encoding='utf-8').read()
bl = [b for k, b in split(src) if k in keys]
os.makedirs(J.work(sid, 'pred26'), exist_ok=True); out = J.work(sid, 'pred26', name + '.txt')
open(out, 'w', encoding='utf-8').write('\n'.join(b.rstrip('\n') for b in bl).rstrip('\n') + '\n')
print(sid, name, len(bl), '블록 →', out)
