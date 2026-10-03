import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
SID, TITLE, EN, COLOR = 'PHARM', '임상치과약물치료학', 'Clinical Dental Pharmacotherapeutics', '#8E3B78'
PROFS = '백정화 · 이윤실 · 김우진 · 우경미 · 조영단'
BUILT = '2026-09-27'
LECMAP = {'RX': ('P01i', '처방전과 금연요법(26)'), 'RX5': ('P02i', '처방전과 금연요법(25)'), 'XE': ('P03i', '구강건조증 치료제(26)'), 'XE5': ('P04i', '구강건조증 치료제(25)'),
          'BT': ('P05i', '보톡스(26)'), 'ACU': ('P11i', '급성통증 치료제(26 김우진)'), 'ACU5': ('P06i', '급성통증 치료제(25 우경미)'), 'CHR': ('P07i', '만성통증 치료제(25)'), 'HM': ('P08i', '지혈제와 수렴제(25)'), 'DS': ('P09i', '살균제와 소독제(25)'), 'BT5': ('P10i', '보톡스(25)')}
LEC_ORDER = ['RX', 'XE', 'BT', 'ACU', 'CHR', 'HM', 'DS']
LEC_IMG_ROOT = J.work('PHARM', 'lec') + '/'     # 강의 쪽 이미지: work/PHARM/lec/<폴더>/<쪽>.jpg
def lec_img_path(k, p):
    d = LECMAP[k][0]
    return f'{LEC_IMG_ROOT}{d}/{p}.jpg' if d else None
FORCE_PAGES = {}
PAGE_LABEL = {}
IMG_ALIAS = {'RX5': 'RX', 'XE5': 'XE', 'BT5': 'BT', 'ACU5': 'ACU'}
PROF_LEC = {'백정화': ['RX'], '이윤실': ['XE'], '김우진': ['BT'], '우경미': ['ACU', 'CHR', 'HM'], '조영단': ['DS']}
PROF_ORDER = ['백정화', '이윤실', '김우진', '우경미', '조영단']
COVER = {'백정화': 19, '이윤실': 20, '김우진': 20, '우경미': 20, '조영단': 20}
TIERS = {'A': '현 강의 담당 교수 파트', 'B': '(해당 없음)', 'C': '(해당 없음)'}
PROF_NOTE = {'백정화': '금연요법·처방전(23년부터 3Q). 22년엔 구강건조증도 백정화 출제', '이윤실': '구강건조증(24년 4Q→3Q 이동). 20년엔 처방전 파트도 이윤실 출제', '김우진': '보톡스 — 25·26 자료 동일 · 26년부터 급성통증 치료제도 담당(25년까지 우경미 교수님)', '우경미': '급성(25년까지)·만성통증 + 지혈제(25년 JB: 지혈·살균은 진도 전이라 이전 해설 그대로)', '조영단': '살균제·소독제 — "빨간 글씨 위주로 읽어보라"(23년)'}
MENT_PROF = {'백정화': '"대체적으로 짤 비율이 높고 선지 변형 정도의 탈"(25년) — 처방전 확인사항·약어·NRT 금기가 반복', '이윤실': '"짤"(25년) — pilocarpine 적응 2(구강건조·녹내장)·진단 기준 표·BMS clonazepam 처방', '김우진': '"짤"(25년) — 균 특성·독소 구조·진료 영역·금기·교근 주입이 24·23·22 같은 문제', '우경미': '"짤"(25년) — carbamazepine·sensitization·gabapentin·NSAID vs opioid 매년 / 지혈: thrombin·target 표·warfarin vs dabigatran·aspirin', '조영단': '"짤"(25년) — 각 제제의 general features 한 문장 선지(iodine·hypochlorite·oxygenating·bis-biguanide) 반복'}
MENT_ALL = '25년 멘트: "작년과 수업 순서만 바뀌었을 뿐 같은 구성. 대체적으로 짤 비율이 높고 선지 변형 정도의 탈. 짤 문항은 가장 최근 출제 연도에만 수록". 23판 멘트: "괄호 숫자는 ’가 붙으면 연도, 없으면 학번". 성호르몬(노상호)은 4Q로 이전되어 제외'
