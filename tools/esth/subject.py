import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
# 과목별 설정 — ESTH 심미치과학 (강의 주제마다 가장 최신 연도 자료: 26 → 없으면 25)
SID, TITLE, EN, COLOR = 'ESTH', '심미치과학', 'Esthetic Dentistry', '#2F7A3E'
PROFS = '이창하 · 안진수'
BUILT = '2026-10-03'
LECMAP = {'INT': ('E01i', 'Introduction(26)'), 'FUN': ('E02i', 'Fundamentals of esthetic dentistry(26)'),
          'PLAN': ('E03i', '심미수복에서의 진단 및 치료계획(26)'), 'SPE': ('E04i', 'Special Effects(25)'),
          'COL': ('E05i', '색(25)'), 'MAT': ('E06i', '심미수복재료(25)'),
          'VEN': ('E07i', 'Direct veneer, Indirect composite resin inlay(25)'),
          'INT5': ('E08i', 'Introduction(25)'), 'FUN5': ('E09i', 'Fundamentals of esthetic dentistry(25)'),
          'PLAN5': ('E10i', '심미수복에서의 진단 및 치료계획(25)')}
LEC_ORDER = ['INT', 'FUN', 'PLAN', 'SPE', 'COL', 'MAT', 'VEN']
LEC_IMG_ROOT = J.work('ESTH', 'lec') + '/'     # 강의 쪽 이미지: work/ESTH/lec/<폴더>/<쪽>.jpg (tools/matx.py가 mat/<파일>/i로 연결)
def lec_img_path(k, p):
    d = LECMAP[k][0]
    return f'{LEC_IMG_ROOT}{d}/{p}.jpg' if d else None
FORCE_PAGES = {}
PAGE_LABEL = {}
IMG_ALIAS = {'INT5': 'INT', 'FUN5': 'FUN', 'PLAN5': 'PLAN'}
PROF_LEC = {'이창하': ['INT', 'FUN', 'PLAN', 'SPE', 'MAT', 'VEN'], '안진수': ['COL'], '서덕규': [], '여인성': []}
PROF_ORDER = ['이창하', '안진수']
COVER = {'이창하': 18, '안진수': 18, '서덕규': 18, '여인성': 18}   # JB 괄호 연도가 18년까지 → 2018년이 기준선
TIERS = {'A': '현 강의 담당 교수 파트(전임 서덕규 교수 퀴즈에서 이어진 문항 포함)',
         'B': '전임 여인성 교수(Resin-bonded restoration, 21~24년) 출제 — 지금 강의에는 일부만 겹침',
         'C': '참고용 — 서덕규 교수 Successful cervical restoration 강의 문항(JB: "23년도 시험범위 아닙니다")'}
PROF_NOTE = {'이창하': '22년부터 담당(전임 서덕규) — 서덕규 교수 수업 퀴즈가 "완짤 경향"으로 계속 출제(23·24 JB)',
             '안진수': '색 강의 — 짤 경향이 강함(25 JB)',
             '서덕규': '21년까지 담당 — 퀴즈 문항이 이창하 교수 시험에 계속 나옴',
             '여인성': 'Resin-bonded restoration(21~24년 3Q) — 25·26년 강의 목록에 없음, "작년 여인성 교수님 파트의 내용도 이창하 교수님께서 다루시는 것 같습니다(예정)"(25 JB)'}
MENT_PROF = {'이창하': '"원래 서덕규 교수님께서 맡았던 부분을 이창하 교수님께서 작년부터 강의 … 여전히 서덕규 교수님께서 수업시간에 알려주신 퀴즈들이 완짤 경향으로 나오는 것 같습니다 … 이창하 교수님 후반부 수업은 탈 경향이 큰 것 같습니다"(23년) · "이창하 교수님 수업 구성이 조금 바뀌었고 … 이창하 교수님 ppt는 꼼꼼히 보는 것을 추천"(25년)',
             '안진수': '"안진수 교수님의 경우 짤 경향이 강해"(25년 27번 해설) · SPD "올해에도 강조하셨습니다"(25년)'}
MENT_ALL = '25년 멘트: "짤 경향 높은 반짤반탈이지만 미복원 문항이 많습니다 … 탈의 경우 작년 여인성 교수님 ppt, 이창하 교수님 ppt 및 교과서에서 출제 … 교과서 문제의 경우 생각해보면 풀 수 있는 수준으로 출제되어 교과서는 선택적으로" / 24년 멘트: "반짤반탈 … 작년에 교과서 기반 탈 문제 출제를 예고하셨으나 복원된 탈 문항은 대부분 PPT를 출처로 합니다. 우선은 JBL을 추천드리고, 여유가 되신다면 PPT까지" / 23년 멘트: "반짤반탈 … 3단원도 잘 출제 안하시는 것 같습니다"'
