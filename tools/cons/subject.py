import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
# 과목별 설정 — 새 과목은 이 파일과 assemble.py(JB·강의 매핑)만 바꾸면 된다
SID, TITLE, EN, COLOR = 'CONS', '임상치과보존학', 'Clinical Conservative Dentistry', '#5B2A86'
PROFS = '이인복 · 서덕규 · 김선영 · 이창하'
BUILT = '2026-09-23'
LECMAP = {'WHT': ('C01c', 'Tooth whitening(26·25)'), 'CRK': ('C09i', 'Cracked tooth(26)'), 'DHS': ('C09i', '시린 치아·DH(26)'), 'CR5': ('C02i', 'Cracked tooth(25)'), 'DH5': ('C03i', 'Dentin hypersensitivity(25)'),
          'INL': (None, 'Inlay vs Fillings(25·필기본)'), 'ANT': (None, '전치부 레진 심미수복(25·필기본)'),
          'ADH': ('C06i', 'Dental adhesive(25)'), 'FRC': ('C07i', 'FRC post(25)')}
LEC_ORDER = ['WHT', 'CRK', 'DHS', 'INL', 'ANT', 'ADH', 'FRC']
LEC_IMG_ROOT = J.work('CONS', 'lec') + '/'     # 강의 쪽 이미지: work/CONS/lec/<폴더>/<쪽>.jpg
def lec_img_path(k, p):
    d = LECMAP[k][0]
    return f'{LEC_IMG_ROOT}{d}/{p}.jpg' if d else None
FORCE_PAGES = {}
PAGE_LABEL = {'WHT': '슬라이드 '}          # 이미지 전부 넣을 강의 {키: range}
IMG_ALIAS = {'CR5': 'CRK', 'DH5': 'DHS'}
PROF_LEC = {'이인복': ['WHT'], '서덕규': ['CRK', 'DHS'], '김선영': ['INL', 'ANT'], '이창하': ['ADH', 'FRC'], '손호현': []}
PROF_ORDER = ['이인복', '서덕규', '김선영', '이창하']
COVER = {'이인복': 10, '서덕규': 10, '김선영': 10, '이창하': 10, '손호현': 10}   # 괄호 연도가 10년까지 → 2010년이 기준선
TIERS = {'A': '현 교수 기출', 'B': '(해당 없음)', 'C': '참고용 — 손호현 교수님 기출(25판에서 절삭)'}
PROF_NOTE = {'손호현': '16년 이후 출제 없음 · 25판에서 절삭 — 참고'}
MENT_PROF = {'이인복': '"짤 단답형·서술형 1문제씩과 탈 서술형 1문제"(25년, 24년 시험) · "짤 2(서술형), 탈 1(T/F)"(24년) · "전반적으로 반짤"(23년)',
             '서덕규': '"완짤"(25·24년) · "올해는 객관식으로 출제하겠다 하셨습니다"(25년)',
             '김선영': '"완짤"(25·24년) · "시험 출제 예고하신 내용 중 기출된 문제에 강조 표시"(25년) · "수업시간에 시험문제라고 강조하신 부분이 있으니 필기 참고"(23년)',
             '이창하': '"두 강의 모두 반짤반탈"(25년, 24년 시험: 짤 객관식 2·서술형 1 / 탈 단답형 1·서술형 2) · "FRC post 파트는 완짤, 새로 수업한 Dental adhesive 파트는 완탈"(24년)'}
MENT_ALL = '25년 멘트: 24년 시험 = 서술형 8·단답형 2·객관식 2, 총 12문제 복원 / 24년 멘트: 23년 시험 = 서술형 7·단답형 4·객관식 1·T/F 1, 총 13문제 / 23년 멘트: 22년 시험 = 서술형 9·단답형·빈칸빵 2·객관식 1, 총 12문제'
