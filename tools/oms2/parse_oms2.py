import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
"""OMS2 JB 분해 — 판본 구조(연도 칸형 / 교수별 괄호형)를 읽고 쓴다: parse(ed, n) → 블록 [{'ed','sec','prof','num','pg','pg2','lines'}](+ 'key' 겹치는 번호)
본보기: tools/cons/parse_cons.py(교수별 괄호형·26판 앞뒤) · tools/esth/parse_esth.py(연도 칸형) — 블록 수·번호 검증(RULES 0-1)"""
import re, json
BASE = J.JBX
def rd(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '').replace('\x02', '')
def parse(ed, n):
    return []   # 아직 JB 없음 — work/jb/OMS2_20<ed>/<쪽>.txt를 읽어 블록으로
