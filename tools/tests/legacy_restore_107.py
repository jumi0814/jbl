"""회귀(ux2 fixA V06): 1차 배포본 7095e56 — 사용자가 지금 쓰는 판 — 에서 만든 형광펜·빈칸(실제 저장 형식 {t,x,i,c,p,s,v})이 새 허브에서 같은 자리에 복원되는지.
legacy_restore.py --rev 7095e56 과 같음(양쪽 Kit 글자로 판정 · 원고를 다시 써서 글자가 사라진 LOST_GONE은 강의별로 보고하고 비율 한도 --max-gone).
  .venv/bin/python tools/tests/legacy_restore_107.py"""
import os, sys, asyncio, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import legacy_restore as LR
a = argparse.Namespace(rev='7095e56', max_lost=0.06, max_shift=3, max_gone=0.04)   # 2026-09-28 측정: LOST_GONE 262/7754 = 3.38% (원고를 다시 써서 글자가 사라진 것 — 강의별 수는 출력)
sys.exit(0 if asyncio.run(LR.main(a)) else 1)
