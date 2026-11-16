import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
# 과목별 설정 — ANAT4 임상두경부해부학(4Q) · 필드 설명은 tools/cons/subject.py · 11-16 JB 단계(work/ANAT4/jb/R_JB_ANAT4.md · guide/과목노트_ANAT4.md)
SID, TITLE, EN, COLOR = 'ANAT4', '임상두경부해부학', '', '#2F5DA8'
PROFS = '방강미 · 장미숙 · 이승표'
BUILT = '2026-11-16'
# 강의자료 = 교과서 2권뿐(26·25 PPT 없음): '치의학도를 위한 사람해부학(1판)'(458쪽 · 전 쪽 OCR · PDF 쪽 = 책 쪽 + 6) · '머리 및 목 해부학(7판)_2021 교정 및 보완판'(1081쪽 · PDF 쪽 = 책 쪽 + 23)
# 강의 나누기(11-16 무인 결정 — 보고 2절 안 3 · 사용자가 다르게 원하면 바꿈 — 문항 id는 강의와 무관해 그대로):
#   수업 표 1~3강(Lower limb·Upper limb·Splanchnology) = 사람해부학 해당 PART(기출 0 — 멘트 '두경부 위주로 출제')
#   수업 표 4~7강(Face·Infratemporal region·Maxillary sinus·Neck) = 두경부 문제 뱅크 한 강의 HN(머리 및 목 해부학 · 뱅크 문항 전부 — 문항 ↔ 4~7강 연결 근거가 JB에 없음:
#     24판 14번 '25년도 수업시간에 출제 예고한 슬라이드'(Submandibular triangle — 교과서로는 목)가 12/10 전 강의(Face·Infratemporal region)에서 나옴 → 강의 이름으로 나누면 어긋날 수 있음)
#   3Q 명훈 Neck dissection 기출(23판 끝 첨부) = MH(4Q 강의·교과서에 없음 — 폴더 None · 기출 참고)
# 쪽 이미지 폴더(work/ANAT4/lec/<폴더> → ../mat/<파일id>/i) — 키마다 폴더 하나(같은 책을 여러 키가 씀) · 카드 쪽 번호 = PDF 쪽(책 쪽 + 오프셋 — 보고 2절 장 → 쪽 범위 표)
LECMAP = {'LL': ('LLi', 'Lower limb — 교과서(치의학도를 위한 사람해부학)'),
          'UL': ('ULi', 'Upper limb — 교과서(치의학도를 위한 사람해부학)'),
          'SPL': ('SPLi', 'Splanchnology — 교과서(치의학도를 위한 사람해부학)'),
          'HN': ('HNi', '두경부 문제 뱅크(Face·Infratemporal region·Maxillary sinus·Neck) — 교과서(머리 및 목 해부학 7판)'),
          'MH': (None, 'Neck dissection(3Q 명훈) — 4Q 강의 없음(기출 참고)')}
LEC_ORDER = ['LL', 'UL', 'SPL', 'HN', 'MH']   # 25 수업 차례(26 수업 표 없음) · HN = 4~7강 · 다른 쿼터 참고 기출은 끝
LEC_IMG_ROOT = J.work('ANAT4', 'lec') + '/'
def lec_img_path(k, p):
    d = LECMAP[k][0]
    return f'{LEC_IMG_ROOT}{d}/{p}.jpg' if d else None
FORCE_PAGES = {}
PAGE_LABEL = {}   # 교과서 쪽 표시(PDF 쪽 ≠ 책 쪽)는 작성 단계에서 정함 — 보고 2절 '쪽 표시'
IMG_ALIAS = {}   # 25·26 판 나눔 없음(교과서)
XREF_LECS = []   # HN이 뱅크 문항을 직접 가짐(참고 강의 아님)
FIG_ONLY_LECS = []   # 교과서 쪽 칩도 눌러서 쪽 그림(10-30 사용자 — ESTH BOOK 선례)
PROF_LEC = {'방강미': ['LL', 'SPL', 'HN'], '장미숙': ['UL'], '이승표': ['HN'], '박영석': [], '명훈': ['MH']}   # 25 수업 표(24판 1쪽) 담당 · 박영석 = 23 Splanchnology·Face(25 수업 없음) · 26 담당 미정
PROF_ORDER = ['방강미', '장미숙', '이승표', '명훈']
COVER = {'': 22, '명훈': 17}   # 뱅크 문항(출제 교수 근거 없음 — 강의 연결 교수 '') 기준선 = 2022(JB에 남은 첫 시험 해 · 23판 '[2022년 기출문제]') · 명훈 = 2017(23판 '[2017년 복원]')
TIERS = {'A': '문제 뱅크(JB 23·24판 — 4Q 시험은 뱅크에서 출제 · 2022·2023 기출 목록 포함)', 'B': '(해당 없음)',
         'C': '3Q 명훈 교수님 Neck dissection 기출(2018·2017 복원 · 23판 끝 첨부 "2 년동안 출제된 적 없으나 혹시 몰라 3Q 명훈 pf 부분도 첨부")'}
PROF_NOTE = {'방강미': '25 수업 표(24판 1쪽): Lower limb·Splanchnology·Face·Infratemporal region·Maxillary sinus(예정) — 23 수업 표에는 없음 · 시험 출제 교수 근거 없음(뱅크 출제)',
             '장미숙': '25: Upper limb · 23: Lower limb·Upper limb·Infratemporal region·Maxillary sinus(23판 1쪽 수업 표) — 시험 출제 교수 근거 없음(뱅크 출제)',
             '이승표': '25: Neck(예정 — 24판 1쪽 수업 표) · 23 Neck 교수 칸은 빈칸',
             '박영석': '23: Splanchnology·Face(23판 1쪽 수업 표) — 25 수업 표에 없음',
             '명훈': '3Q 교수(230830 Neck dissection) — 4Q JB 23판 끝에 3Q 기출 첨부: "2023 학습부) 2018 년도까지만 시험 출제 하셨고 그 이후로는 출제된 적이 없으나 혹시 몰라 이전 JB 추가했습니다." · 24판(25년)에는 없음'}
MENT_PROF = {'명훈': '"2 년동안 출제된 적 없으나 혹시 몰라 3Q 명훈 pf 부분도 첨부는 해두었습니다"(23년) · "2018 년도까지만 시험 출제 하셨고 그 이후로는 출제된 적이 없으나 혹시 몰라 이전 JB 추가했습니다"(23판 명훈 칸)'}
MENT_ALL = ('25년 멘트(24판 — 표지 "2025 4Q JB"): "매년 강의 교수님이나 내용이 조금씩 달라지지만 시험은 뱅크에서 꾸준히 출제됩니다. 따라서 5 년째 이전 기출문제 첨부 없이 뱅크로만 JB 가 제작되어 왔습니다. 실제 이론 강의 시간에는 전신을 다루었지만 실제 시험에는 두경부 위주로 출제되는 것으로 보이므로 해당 범위 위주로 공부하시면 좋을 것 같습니다. 24 년에는 복원 자체를 하지 않았으나 참고를 위해 22 년, 23 년에 출제된 문제는 맨 뒤에 첨부했습니다." · 14번 "[참고] 25년도 수업시간에 출제 예고한 슬라이드"(Submandibular triangle) / '
            '23년 멘트(23판): "수업시간 강의는 전신을 다루었고 매년 강의의 교수님이나 내용이 조금씩 달라졌지만 시험은 문제 Bank 에서 꾸준히 출제되는 것으로 보입니다. 두경부 위주로 출제되는 듯 하니 문제뱅크 위주로 암기해가시고, 더 공부하고 싶으신 분들은 강의자료 참고하시면 될 것 같습니다. 4 년째 이전 기출문제 첨부 없이 Bank 로만 JB 가 이루어져 있으나 문제가 거의 전부 Bank 에서 출제되어서 그런 것 같습니다. 참고를 위해 작년에 복원된 총 5 문제는 맨 아래에 첨부해두었습니다."')
NOIMG_PAGES = {}   # 교수님 본인 연락처 쪽 없음(11-16 교과서 글층·OCR 검색 — @·010·Tel: 머리 및 목 해부학 1081쪽 출판사 TEL·FAX만 · 저자 약력 1079쪽은 경력뿐)
# 11-16 출제 연도별 출제 교수(guide/handoff/YEARPROF_BRIEF.md · 보고 work/ANAT4/jb/R_JB_ANAT4.md 2절)
#   HN 2023·2022 = '-'(근거 없음): 판에 교수 칸·문항별 교수 표기가 없고 멘트가 "시험은 문제 Bank 에서 꾸준히 출제"(23년)·"시험은 뱅크에서 꾸준히 출제"(25년) — 2023 수업 표(23판 1쪽 장미숙·박영석)는 있으나 뱅크 문항 ↔ 강의 연결 근거가 없음 · 2022 수업 표 없음
#   MH 2018·2017 = 명훈: 23판 24쪽 칸 머리 '명훈 교수님' [2018년 복원]·[2017년 복원] (3Q ANAT YEAR_PROF NECK과 같은 값)
YEAR_PROF = {'HN': {2023: '-', 2022: '-'}, 'MH': {2018: '명훈', 2017: '명훈'}}
YEAR_PROF_Q = {}
# 11-16 JBV(Q4_JBV — work/ANAT4/jb/V_JB_ANAT4.md 4절) — JB 답 줄바꿈만 정리(공통-8 뭉친 나열·표 행이 앞 줄에 붙음 · build4 JBFIX):
#   그 줄 앞에 강제 줄바꿈 표시(U+2063 — reflow가 앞 줄에 잇지 않고 지움)만 넣거나 줄바꿈 ↔ 띄어쓰기만 바꿈 — JB 글자·차례는 그대로(아래 assert)
#   카드 id 열쇠 = 그 카드의 모든 사본(24판 앞면 · 23판 '📜 이전 답'·'다른 판본')에 · 표 칸 경계가 글로는 안 살아나는 표(B02·B05·B08·B13·B14·B15·B16·B17·B18·B20·B23 —
#   특히 B05는 글층이 [maxillary a.] 표를 [참고] 뒤로 보냄 · B15는 '절단 ↔ 보존' 두 열 경계가 없음)는 다음 단계 JF 그림 조각(표 그림) 후보
_H = '\u2063'
def _nl(*heads):
    """heads로 시작하는 줄을 새 줄로(앞 줄에 잇지 않게) → [('\\n<head>', '\\n\\u2063<head>')] · '앞 글|뒤 글' = 한 줄 안 빈칸 하나를 줄바꿈으로(뒤 글부터 새 줄)"""
    out = []
    for h in heads:
        if '|' in h:
            a, b = h.split('|', 1); out.append((f'{a} {b}', f'{a}\n{_H}{b}'))
        else: out.append((f'\n{h}', f'\n{_H}{h}'))
    return out
JBFIX = {
    'B02': _nl('Temporal\nm.', 'Masseter\nm.', 'Medial\npterygoi', '하악지 안쪽면의 pterygoid'),   # 표 행 머리(근육 이름)가 앞 행 끝에 붙음
    'B03': _nl('Articular fibrous covering', 'Articular disc', 'Discal ligament', 'Retrodiscal tissues', 'Articular capsule', 'Articular cavity'),   # 구조물 9가지 중 7개가 한 줄로 뭉침
    'B05': _nl('Middle meningeal\nbranch', 'Pterygopalatine nerve Anterior superior alveolar', 'Posterior superior\nalveolar nerve', '제1부분 (mandibular', 'Deep auricular a.', 'Infraorbital a.', 'Pharyngeal br.',
               'Nasal branch ->', 'Nasopalatine nerve', 'Pharyngeal nerve') + [('1. 머리뼈\n공간에서\n나오는 가지', '1. 머리뼈 공간에서 나오는 가지'), ('2. 날개입천장\n오목에서 나오는\n가지', '2. 날개입천장 오목에서 나오는 가지'),
               ('3.눈확아래관에서 나오는\n가지', '3.눈확아래관에서 나오는 가지'), ('4. 얼굴에 분포하는\n가지', '4. 얼굴에 분포하는 가지')],   # 표 행·'[참고]' 뒤 표 머리 · 표 머리 칸 안 줄바꿈 · 23판 '2.의 내용을 첨언하자면' 나열
    'B08': [('\n특수감각신\n경\n맛감각\n', f'\n{_H}특수감각신경 맛감각\n{_H}')],   # 셋째 행(특수감각신경·맛감각)이 둘째 행 칸 끝에 붙음
    'B10': _nl(' Minor duct - submandibular duct', '도관 :', '위치 :'),   # 24판 Major/Minor duct 두 줄 · 23판 위치/도관 줄
    'B11': _nl('뒷면: infrazygomatic crest는', '위면: 안쪽 모서리', '안쪽면: 후외측에'),   # 23판 '예전 족보' 앞면/뒷면/위면/안쪽면
    'B12': _nl('외측 ramus of mandible', '내측 sphenoid bone', '앞쪽 1) body of maxilla', '근육 medial pterygoid', '신경 1) mandibular n.', '동맥 maxillary a.', '정맥 pterygoid plexus'),   # 경계 외측·내측·앞쪽 · 내용물 신경이 앞 줄에 붙음
    'B13': _nl('앞쪽 omohyoid m.', '뒤쪽 sternocleidomastoid m.', 'Common carotid a.의'),
    'B14': _nl('앞쪽 digastric m.의 anterior belly', '뒤쪽 digastric m.의 posterior belly', 'Suprahyoid m. (4):', 'submandibular\nnodes', 'submandibular\ngland') + [('\nsublingual gland\n및 duct', f'\n{_H}sublingual gland 및 duct')],
    'B15': _nl('Sternocleidomastoid m.', 'Omohyoid m.', 'External jugular v.', 'Internal jugular v.', 'Posterior branch of retromandibular v.', 'Superior thyroid v.', 'Facial a.', 'Submandibular gland',
               'Lower part of parotid gland', 'Fat & Lymph node', 'Ansa cervicalis', 'Branches of cervical plexus', 'Cervical branch of facial n.', 'Accessory n.', 'Lingual n.', 'Hypoglossal n.', 'Common carotid a.',
               'Vagus n.', 'Phrenic n.', 'Brachial plexus', 'Superior laryngeal n.', 'Recurrent laryngeal n.', 'Thoracic duct', 'Cupula of pleura', 'Sympathetic trunk', '출처를 찾지 못해'),
    'B16': _nl('뒤쪽 Trapezius m.', '아래쪽 Clavicle', '천장 피부,', '바닥 Deep cervical fascia', '3~8 cervical nerves의', 'superficial cervical\nnodes', 'deep cervical nodes'),
    'B17': _nl('신경 앞쪽부위:', '뒤쪽부위: Greater palatine n.', 'Lesser palatine n.', 'Lesser palatine a.', 'Ascending palatine a.의 palatine'),
    'B18': _nl('혀의 앞쪽 2/3부분'),
    'B20': _nl('5. superior oblique m.|6. Lateral rectus m.'),   # 한 줄 안 두 칸(Trochlear·Abducent)
    'B21': _nl('뒤쪽벽 –', '안쪽벽 –', '천장 –', '바닥 –', '바깥벽 –', 'Pterygopalatine fossa로는', '날개관신경오목으로는') + [('지나간\n다.', '지나간다.')],
    'B23': _nl('Levator anguli\noris m.', 'Maxilla의 canine fossa', 'Zygomaticus major m.의 안쪽에', '입꼬리를 위로 올리고,', 'Zygomaticus\nminor m.', 'Zygomatic bone의 아래면', '입꼬리 안쪽의 위입술',
               '위입술을 위쪽으로 당기며,', 'Zygomaticus\nmajor m.', 'Zygomatic bone의 바깥면', '입꼬리의 피부와 점막으로 닿고', '입꼬리를 뒤위쪽으로 당겨') + [('안쪽에\n서 입꼬리', '안쪽에서 입꼬리')],   # 그림 글(parse IMGTXT) 표 칸마다 한 줄
    'M01': _nl('inferior: inferior body', 'anterior: stylohyoid', 'posterior: spinal accessory'),
    'M04': _nl('periparotid nodes', 'buccinator nodes', 'retropharyngeal nodes', 'midline visceral nodes', 'level 1과 level 2 경계', 'level 3,4,5 경계', 'level 2,3 경계', 'level 2 경계'),   # (1) 림프절 5 · (2) 'level … 경계' 줄마다(값은 그 줄에 붙음)
}
import re as _re
for _k, _ps in JBFIX.items():
    for _o, _n in _ps: assert _re.sub(r'[\s\u2063]+', '', _o) == _re.sub(r'[\s\u2063]+', '', _n), f'JBFIX 글자가 바뀜: {_k} {_o[:30]!r}'
