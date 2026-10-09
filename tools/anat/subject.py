import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
# 과목별 설정 — ANAT 임상두경부해부학
SID, TITLE, EN, COLOR = 'ANAT', '임상두경부해부학', 'Clinical Head & Neck Anatomy', '#2F5DA8'
PROFS = '명훈 · 권익재 · 양훈주 · 서병무 · 서미현 · 박주영'
BUILT = '2026-09-25'
LECMAP = {'NECK': ('A01i', 'Neck dissection(26)'), 'NV': ('A02i', '신경·혈관 해부학(26)'), 'NV5': ('A03i', '신경·혈관 해부학(25)'),
          'LIP': ('A04i', '구순열·구개열·비 해부학(26)'), 'LP5': ('A05i', 'Lip, Palate, Nose(25 한정준)'),
          'MAND': ('A11i', 'Mandible(26)'), 'MAND5': ('A06i', 'Mandible(25)'), 'PAR': ('A12i', 'Parotid gland and facial nerve(26 권익재)'), 'PAR5': ('A07i', 'Parotidectomy(25 서미현)'), 'MAX': ('A08i', 'Maxilla(25)'), 'NK5': ('A10i', 'Neck dissection(25)'), 'TMJ': ('A09i', 'TMJ·SMAS(25)')}
LEC_ORDER = ['NECK', 'NV', 'LIP', 'MAND', 'PAR', 'MAX', 'TMJ']
LEC_IMG_ROOT = J.work('ANAT', 'lec') + '/'     # 강의 쪽 이미지: work/ANAT/lec/<폴더>/<쪽>.jpg
def lec_img_path(k, p):
    d = LECMAP[k][0]
    return f'{LEC_IMG_ROOT}{d}/{p}.jpg' if d else None
FORCE_PAGES = {}
PAGE_LABEL = {}
IMG_ALIAS = {'NV5': 'NV', 'LP5': 'LIP', 'NK5': 'NECK', 'MAND5': 'MAND', 'PAR5': 'PAR'}
PROF_LEC = {'명훈': ['NECK'], '권익재': ['NV'], '이종호': ['NV'], '양훈주': ['LIP'], '최진영': ['LIP'], '한정준': ['LIP'], '서병무': ['MAND', 'MAX'], '서미현': ['PAR'], '김성민': ['PAR', 'TMJ'], '박주영': ['TMJ']}
PROF_ORDER = ['서병무', '권익재', '양훈주', '서미현', '박주영', '명훈']
COVER = {'서병무': 20, '권익재': 22, '이종호': 19, '양훈주': 20, '최진영': 20, '한정준': 20, '서미현': 20, '김성민': 19, '박주영': 20, '명훈': 17}
TIERS = {'A': '현 강의 담당 교수 파트(이전 담당 교수 출제분 포함)', 'B': '이전 담당 교수(이종호·김성민) 출제 — 현 강의와 겹치는 내용', 'C': '(해당 없음)'}
PROF_NOTE = {'양훈주': '26년 담당 — 24년까지는 최진영 교수님 PPT로 최진영(~23)·한정준(24) 출제', '서미현': '24년부터 담당 — 23년까지 양훈주, 20년 이전 김성민', '권익재': '22년부터 담당 — 21년 이전은 이종호(참고 B)', '명훈': '18년 이후 출제 없음 — JB는 혹시 몰라 유지'}
MENT_PROF = {'서병무': '"서병무 교수님은 짤 몇 문제 + 탈 경향이 강합니다"(23년) · "서병무 교수님은 탈 경향이 강하고"(24년)',
             '박주영': '"박주영 교수님은 완짤"(24년) — 22·23·24년 같은 세 문제',
             '권익재': '"권익재 교수님은 짤"(23년) · "나머지 교수님은 반짤반탈"(24년)',
             '양훈주': '"최진영 교수님도 짤 경향이 강하시고"(23년) · "25년 한정준 교수님이 최진영 PPT로 수업, 출제도 한정준"(25년) → 26년은 양훈주 교수님이 새 PPT로 수업',
             '서미현': '"양훈주 교수님은 짤"(23년) · "서미현 교수님 범위부터는 작년 PPT를 참고"(24년)',
             '명훈': '"명훈 교수님은 19년도부터 출제하지 않으신 것으로 되어있으나, 일단 수업은 하셨기에 절삭하지 않았습니다"(25년) — 26 수업에서 시험문제(level landmarks)를 공개'}
MENT_ALL = '25년 멘트: "이전 전반적으로 명훈, 이종호 교수님은 짤 경향" / 22년: "서병무 교수님을 제외한 교수님 파트는 짤 경향" / 24년: "박주영 완짤, 서병무 탈, 나머지 반짤반탈". 해부학 JB는 연도 칸 안에 교수별로 실림'
