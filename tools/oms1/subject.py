import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
# 과목별 설정 — OMS1 구강악안면외과학 1
SID, TITLE, EN, COLOR = 'OMS1', '구강악안면외과학 1', 'Oral & Maxillofacial Surgery I', '#0F4B4A'
PROFS = '서병무 · 한정준 · 서미현 · 윤필영'
BUILT = '2026-09-24'
LECMAP = {'DD1': ('L08', 'DD I(26)'), 'DD2': ('L09', 'DD II(26)'), 'DD3': ('L10', 'DD III(26)'), 'DX': ('L03', '진단·치료계획(25)'),
          'EXT': ('L04', '발치와·식립시기(25)'), 'LOAD': ('L05', 'Loading(25)'), 'REP': ('L06', '재식론(25)'), 'REP2': ('L07', '보존과 ppt(25)')}
LEC_ORDER = ['DD1', 'DD2', 'DD3', 'DX', 'EXT', 'LOAD', 'REP']
LEC_IMG_ROOT = J.work('OMS1', 'lec') + '/'     # 강의 쪽 이미지: work/OMS1/lec/<폴더>/<쪽>.jpg
def lec_img_path(k, p):
    d = LECMAP[k][0]
    return f'{LEC_IMG_ROOT}{d}i/{p}.jpg' if d else None
FORCE_PAGES = {'DX': range(1, 46)}
PAGE_LABEL = {}
ALT_KEY = {'REP': 'REP2'}
IMG_ALIAS = {'REP2': 'REP'}
PROF_LEC = {'서병무': ['DD1', 'DD2', 'DD3'], '정필훈': ['DD1', 'DD2', 'DD3'], '한정준': ['DX', 'LOAD'], '방강미': ['DX', 'LOAD'], '서미현': ['EXT'], '윤필영': ['REP']}
PROF_ORDER = ['서병무', '서미현', '한정준', '윤필영', '방강미']
COVER = {'서병무': 20, '한정준': 22, '서미현': 22, '윤필영': 22, '방강미': 22, '정필훈': 13}
TIERS = {'A': '현 교수 기출', 'B': '정필훈 중 서병무 내용과 겹침', 'C': '참고용 과거 교수 파트'}
PROF_NOTE = {'방강미': '22년 출제 · 지금은 한정준 파트', '정필훈': '은퇴 · 2020년부터 서병무 담당 — 참고'}
MENT_PROF = {'서병무': '"탈 경향이 강하신 분이므로 JB 문제들과 함께 ppt도 보시는 것을 추천"(23년) · "복원된 문제는 전부 서술형 혹은 넘버링 형태였고 큼직하게 물어보시는 것 같습니다"(22년)'}
MENT_ALL = '24년 멘트: "2023 기출 대부분 탈이고 짤인 문제도 문제 유형이 조금씩 바뀐 듯" / 25년 멘트: "2022년 진단 및 치료계획 파트는 방강미 교수님 출제(참고로만)"'
