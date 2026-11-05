import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
# 과목별 설정(4q 치과임플란트학 — tools/new_subject.py가 만든 빈 틀 · 강의를 넣으며 채움 · 필드 설명은 tools/cons/subject.py)
SID, TITLE, EN, COLOR = 'IMPL4', '치과임플란트학', '', '#93561A'
PROFS = ''
BUILT = '2026-11-05'
LECMAP = {'WAIT': (None, '강의자료 대기')}   # 키: (쪽 이미지 폴더 work/IMPL4/lec/<폴더> — tools/matx.py SRC, 강의 이름)
LEC_ORDER = ['WAIT']
LEC_IMG_ROOT = J.work('IMPL4', 'lec') + '/'
def lec_img_path(k, p):
    d = LECMAP[k][0]
    return f'{LEC_IMG_ROOT}{d}/{p}.jpg' if d else None
FORCE_PAGES = {}
PAGE_LABEL = {}
IMG_ALIAS = {}   # 25 보조 키 → 26 키(예 'INT5': 'INT') — 4Q는 25 쪽을 기출 근거 ⭐ 줄에서만(RULES 14)
PROF_LEC = {}
PROF_ORDER = []
COVER = {}   # 교수: JB 괄호 연도 기준선(그해까지는 짤/탈 판정 안 함)
TIERS = {'A': '현 교수 기출', 'B': '(해당 없음)', 'C': '참고용'}
PROF_NOTE = {}
MENT_PROF = {}
MENT_ALL = ''
YEAR_PROF = {}
YEAR_PROF_Q = {}
