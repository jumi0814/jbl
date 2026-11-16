import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
"""OPATH 임상구강악안면병리학(4Q) — JB 23·24·25판 → 정식 문항(Q)·같은 문제의 다른 판본(other)·대조표(LEDGER) (2026-11-16 JB 단계 · work/OPATH/jb/R_JB_OPATH.md)
id = 강의 글자 + 번호(강의 안에서 최근 해 먼저 · tier C는 강의 끝 · jb_lock.json이 잠금 — 번호 당기기 금지):
  B Biopsy(BX) · Q 구강병리검사의뢰서(REQ) · I Immune-mediated(IMM) · O OPMD · M 구강점막질환(1)(MUC1) · N 구강점막질환(2)(MUC2) · J Inflammation of Jaw(INF)
  T Benign Nonodontogenic Tumors(BNT) · G Giant cell lesion(GCL) · C Cystic lesions(CYS) · D Odontogenic tumor(ODT) · P Pigmented lesions(PIG)
  S 연조직 종창(SOFT — 올해 강의 없음) · X 구강 감염성 질환(INFX) · H 진단혈액(HEMA) · R 혈액형·헌혈과 수혈(TRF) · K 임상화학검사(CHEM)
묶음 G = (id, 강의 키, tier, [블록 '판|칸키|번호' …]) — 첫 블록 = 정식(가장 최신 판 · 같은 판이면 가장 최근 해 칸 · 가리킴 줄이 아닌 것), 나머지 = 같은 문제의 다른 판본(OTHER)
  · 판 사이 같은 문제 = 문제 글이 같거나(복원 낱말만 다름 · 답 같음) JB가 같은 문제라고 적은 것: 괄호 연도 사슬 · 25판 가리킴 줄('23 년도 2 번'·'24 년도 17 번'·'24 년도 5 번') ·
    25판이 2022·2023·2024 칸에 합치며 과거 통합에서 뺀 문항(조직고정·하얗게·OPMD 정의·leukoedema·cellulitis·actinomycosis·central hemangioma·Gardner·FD·tori) ·
    '짤 문항'·'[추정문항]'(2022 진단혈액 '보기에 루푸스 있는 짤 문항' · 2022 Giant cell matching) · 23·24판 2022 칸 덧문항('2-1. 드문 세균 감염증'·'2-1~2-3 Gardner'·'4-1 Cherubism' — 과거 기출 첨부)
  · 비슷하지만 묻는 것·답이 다른 것은 별개(관련 문항 rel=은 다음 단계 annot — 짝 목록은 보고 3절): D01 ↔ D02(파노라마 감별 — 옛 판은 조직 사진 2) 더 있음) ·
    B01 ↔ B03(특수염색) · M01 ↔ M05(WSN) · M02 ↔ M06(leukoedema) · O05 ↔ O04(백반증 발암 위험 조건) · R02 ↔ R04(RhD) · K03 ↔ K06(당뇨 진단 기준) · T07 ↔ T05·T09(FD·COD) · T03 ↔ S04(hemangioma) …"""
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_opath as P, subject as S
BASE = J.JBX; SUB = 'OPATH'
NPAGES = P.NPAGES
LECMAP = S.LECMAP

# ---------- 1. JB blocks ----------
blocks = {}
for ed, n in NPAGES.items():
    out = []
    for x in P.parse(ed, n):
        x['text'] = '\n'.join(x['lines']).strip(); out.append(x)
    blocks[ed] = out
BYKEY = {P.key(x): x for ed in blocks for x in blocks[ed]}
ANSRE = re.compile(r'^\s*\[?(정답|답)\]?\s*[:：)]|^\s*답\s*$')
def stem_of(t):
    out = []
    for l in t.split('\n'):
        if ANSRE.match(l): break
        out.append(l)
    return ' '.join(out)
def tag_years(text):
    """문항 첫머리(답 이전)의 연도 괄호 전부 — (24,23) · (20,22,23,24) · (주관식,19) · (객,20,19) · (불완전 복원, 20,19) · (21,19,18,17) ★★★"""
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = re.sub(r'(반짤반탈|짤|탈|년|~|객관식|주관식|객|불완전\s*복원)', ' ', g).replace('，', ',')
        if not re.fullmatch(r'\s*,?\s*(20\d\d|\d\d)(\s*[,、]\s*(20\d\d|\d\d)?)*\s*', g2): continue
        vs = [int(v) % 100 for v in re.findall(r'20\d\d|\d\d', g2)]
        if not vs or not all(8 <= v <= 26 for v in vs): continue
        ys |= set(vs); raw.append('(' + re.sub(r'\s+', '', g) + ')')
    return ys, raw
def find(ed, sec, num):
    for x in blocks[ed]:
        if x['sec'] == sec and str(x['num']) == str(num): return x
    return None
def secyear(sec): m = re.match(r'(20\d\d)', sec or ''); return int(m.group(1)) % 100 if m else None
def seclabel(sec): return f'{sec} 칸'

# ---------- 2. canonical questions ----------
# 강의별 담당(25 담당 — 26 자료 없음 · 올해 강의 없는 주제는 옛 담당)
LK_PROF = {'BX': '윤혜정', 'REQ': '이삭', 'IMM': '오규영', 'OPMD': '윤혜정', 'MUC1': '이재일', 'MUC2': '이재일', 'INF': '이재일', 'BNT': '이재일',
           'GCL': '홍성두', 'CYS': '홍성두', 'ODT': '이삭', 'PIG': '윤혜정', 'CC1': '윤혜정', 'CC2': '이삭', 'CC3': '윤혜정',
           'SOFT': '윤혜정', 'INFX': '오규영', 'HEMA': '황상미', 'TRF': '김형석', 'CHEM': '이경훈'}
G = [
    # ---- B Biopsy & Diagnostic Procedures(윤혜정)
    ('B01', 'BX', 'A', ['25|2024|1']),                                      # PAS·mucicarmine(2024 새 문항)
    ('B02', 'BX', 'A', ['25|2023|1', '24|2023|2', '25|2022.1|1', '24|2022.1|1', '23|2022.1|1', '23|과거.1|1']),   # 조직고정 (23,22,21,20) · 25판 2022 '1. 23 년도 2 번' 가리킴
    ('B03', 'BX', 'A', ['25|2023|2', '24|2023|10']),                        # 특수염색 하나 적고 목적
    ('B04', 'BX', 'A', ['25|2023|3', '24|2023|11']),                        # 면역형광 감별 질환 4가지
    # ---- Q 구강병리검사의뢰서(25 이삭 실습 — 25 필기 "오늘 강의는 시험에 안 나온다" · 2019 문항)
    ('Q01', 'REQ', 'C', ['23|과거.2|1']),                                   # 의뢰서 필수 정보 (19)
    # ---- I Immune-mediated oral mucosal diseases(오규영)
    ('I01', 'IMM', 'A', ['25|2024|2']),                                     # EM — 헤르페스 촉발인자(2024 새 문항)
    ('I02', 'IMM', 'A', ['25|2024|3', '24|2023|8', '24|2023|9', '24|2023|13']),   # 치과수복물 태선양 반응 (24,23) · 24판 8·9 = "두 복원 모두 같은 문제"
    #   · 24판 13 '탈 OLP와 비교되는 태선양반응의 임상과 조직학적 특징'(옛 I04 → jb_move I04→I02 · 11-16 JBV) = 같은 2023 서술형의 세 번째 복원: 답 글자 8·9와 같음 · 같은 해 같은 교수 서술형 칸 ·
    #     25판이 2023 칸에서 2024와 겹치지 않는 문항(B02·B03·B04·I05·I06·O03)은 남기고 8·9·13은 모두 빼 2024 3번 (24,23) 하나로 합침
    ('I03', 'IMM', 'A', ['25|2024|4', '24|2023|16']),                       # 항말라리아제 — chronic ulcerative stomatitis (24,23)
    ('I05', 'IMM', 'A', ['25|2023|4', '24|2023|14']),                       # 기저막 아래 자가항체 — MMP
    ('I06', 'IMM', 'A', ['25|2023|5', '24|2023|15']),                       # BMG 부전각화층 아래 ( ) — neutrophil
    # ---- O Oral Potentially Malignant Disorders(윤혜정)
    ('O01', 'OPMD', 'A', ['25|2024|5', '24|2023|12', '25|2022.3|1', '24|2022.3|1', '23|2022.3|1', '25|과거.1|4', '23|과거.3|5']),   # OPMD 정의 (20,22,23,24) · 25판 '24 년도 17 번'(2022)·'24 년도 5 번'(과거 = 23판 (21))
    ('O02', 'OPMD', 'A', ['25|2024|6', '23|과거.3|1']),                     # 하얗게 보이는 것 1~5 (24,21,20,19)
    ('O03', 'OPMD', 'A', ['25|2023|6', '24|2023|1']),                       # 홍반증 옳은 것 — 24판 답 '1, (2)' → 25판 '2, 4'
    ('O04', 'OPMD', 'A', ['25|과거.1|3', '23|과거.3|4']),                   # 특징 가지는 병소 설명 (21,20)
    ('O05', 'OPMD', 'A', ['25|과거.1|2', '23|과거.3|3']),                   # Malignancy disorder 될 가능성 높은 조건 (20)
    ('O06', 'OPMD', 'A', ['25|과거.1|1', '23|과거.3|2']),                   # Epithelial dysplasia 8가지 (주관식,19)
    # ---- M 구강점막질환(1)(이재일)
    ('M01', 'MUC1', 'A', ['25|2024|7']),                                    # WSN 틀린 것(2024)
    ('M02', 'MUC1', 'A', ['25|2024|8']),                                    # Leukoedema 옳은 것(2024)
    ('M03', 'MUC1', 'A', ['25|2024|9']),                                    # Peutz-Jeghers 옳지 않은 것
    ('M04', 'MUC1', 'A', ['25|2024|11']),                                   # Hypohidrotic ectodermal dysplasia
    ('M05', 'MUC1', 'A', ['25|2022.4|1', '24|2022.4|1', '23|2022.4|1']),    # Symmetric … corrugated plaque → WSN(2022)
    ('M06', 'MUC1', 'A', ['25|2022.4|2', '24|2022.4|2', '23|2022.4|2', '23|과거.5|1']),   # 극세포 … 정상소견 → leukoedema (22 · 과거 20,19)
    ('M07', 'MUC1', 'A', ['25|과거.2|2', '23|과거.5|3']),                   # pachyonychia congenita (21,18)
    # ---- N 구강점막질환(2)(이재일)
    ('N01', 'MUC2', 'A', ['25|2024|10']),                                   # 원발성 헤르페스 치은구내염(2024)
    ('N02', 'MUC2', 'A', ['25|2022.4|3', '24|2022.4|3', '23|2022.4|3']),    # 외상·마찰 수포 — epidermolysis bullosa(2022 · 25판 출처 (2) p34)
    ('N03', 'MUC2', 'A', ['25|과거.2|1', '23|과거.5|2']),                   # intermediate cell — pemphigus vulgaris (20,19)
    ('N04', 'MUC2', 'C', ['25|과거.2|3', '23|과거.5|4']),                   # 궤양 사진+경부 림프절 (20) — JB "출제자와 출처가 불분명한 문제"
    # ---- J Inflammation of Jaw(이재일)
    ('J01', 'INF', 'A', ['25|2024|12']),                                    # dentoalveolar infection → osteomyelitis 옳지 않은 것
    ('J02', 'INF', 'A', ['25|2024|13']),                                    # 급성 골수염 틀린 것
    ('J03', 'INF', 'A', ['25|2024|14']),                                    # BRONJ 옳지 않은 것
    ('J04', 'INF', 'A', ['25|2024|15']),                                    # Focal sclerosing osteomyelitis 틀린 것
    ('J05', 'INF', 'A', ['25|2022.5|1', '24|2022.5|1', '23|2022.5|1', '23|과거.6|1']),   # 근막 침범 급성 상태 — cellulitis (22 · 과거 21,20,19)
    ('J06', 'INF', 'A', ['25|2022.5|2', '24|2022.5|2', '23|2022.5|2', '24|2022.5|2-1', '23|2022.5|2-1', '23|과거.6|4']),   # 유황과립 — cervicofacial actinomycosis (22 · 과거 21,20,16)
    ('J07', 'INF', 'A', ['25|과거.3|1', '23|과거.6|2']),                    # 혈병 탈락 — alveolar osteitis (19,16)
    ('J08', 'INF', 'A', ['25|과거.3|2', '23|과거.6|3']),                    # 도식 빈칸 — condensing osteitis(연도 표기 없음)
    # ---- T Benign Nonodontogenic Tumors of the Jaws(이재일)
    ('T01', 'BNT', 'A', ['25|2022.6|1', '24|2022.6|1', '23|2022.6|1', '23|과거.7|7']),   # Exostoses and tori (22 · 과거 20,19)
    ('T02', 'BNT', 'A', ['25|2022.6|2', '24|2022.6|2', '23|2022.6|2', '24|2022.6|2-1', '23|2022.6|2-1', '23|과거.7|3']),   # Gardner syndrome (22 · 과거 21,20,19,18 + 4-1~4-3)
    ('T03', 'BNT', 'A', ['25|2022.6|3', '24|2022.6|3', '23|2022.6|3', '23|과거.7|2']),   # central hemangioma (22 · 과거 20,19,16)
    ('T04', 'BNT', 'A', ['25|2022.6|4', '24|2022.6|4', '23|2022.6|4', '24|2022.6|4-1', '23|2022.6|4-1']),   # Cherubism (22 · 덧문항 4-1 = 연도 모르는 과거 기출 — 25판은 한 블록)
    ('T05', 'BNT', 'A', ['25|2022.6|5', '24|2022.6|5', '23|2022.6|5', '23|과거.7|5']),   # Fibrous dysplasia (22 · 과거 20,19)
    ('T06', 'BNT', 'A', ['25|과거.4|3', '23|과거.7|8']),                    # ABC vs SBC (21)
    ('T07', 'BNT', 'A', ['25|과거.4|4', '23|과거.7|9']),                    # FD vs COD 비교 (21)
    ('T08', 'BNT', 'A', ['25|과거.4|1', '23|과거.7|1']),                    # osteoma (20,19,17)
    ('T09', 'BNT', 'A', ['25|과거.4|2', '23|과거.7|6']),                    # cemento-osseous dysplasia (20,19)
    ('T10', 'BNT', 'C', ['25|2022.10|1', '23|2022.13|1']),                  # 골 악성종양 — 'Osteosarcoma??'(2022 그 외 불완전 복원 — 강의 머리 없음)
    # ---- G Giant cell lesion(홍성두)
    ('G01', 'GCL', 'A', ['25|2022.7|1', '23|2022.10|1', '25|과거.5|1', '23|과거.11|1']),   # giant cell 종류 matching (22 [추정문항] · 과거 21,19,18,17 ★★★)
    ('G02', 'GCL', 'A', ['25|2022.7|2', '23|2022.10|2']),                   # Foreign body giant cell 연관 질환 (22)
    ('G03', 'GCL', 'A', ['25|과거.5|2', '23|과거.11|2']),                   # 조직슬라이드 → 질환명·giant cell [학습부 출제] (20)
    ('G04', 'GCL', 'A', ['25|과거.5|3', '23|과거.11|3']),                   # Sarcoidosis giant cell (18)
    # ---- C Cystic lesions in jaw and soft tissue(홍성두)
    ('C01', 'CYS', 'A', ['25|2022.8|1', '23|2022.11|1', '25|과거.6|3', '23|과거.12|3']),   # #48 치관 둘러싼 낭성 병소 2개 (22 · 과거 21,19)
    ('C02', 'CYS', 'A', ['25|과거.6|4', '23|과거.12|4']),                   # 생검 사진 → OKC (21,18)
    ('C03', 'CYS', 'A', ['25|과거.6|1', '23|과거.12|1']),                   # 진성·가성·치성·비치성 (20)
    ('C04', 'CYS', 'A', ['25|과거.6|2', '23|과거.12|2']),                   # 17/M Lt. Mn. anterior DDx 4 (20)
    ('C05', 'CYS', 'C', ['23|과거.범위외|1']),                              # 상악동 낭성병소 3가지·감별점 (19 — 윤혜정 상악동 질환 · 범위외)
    ('C06', 'CYS', 'C', ['23|과거.범위외|2']),                              # 상악동저 dome shaped mucin — mucous retention cyst (18 — 범위외)
    # ---- D Odontogenic tumor(25 이삭 · JB 기출은 홍성두 출제)
    ('D01', 'ODT', 'A', ['25|2024|16', '25|2022.9|1', '23|2022.12|1']),     # 파노라마 감별진단 3가지 (24 · 22)
    ('D02', 'ODT', 'A', ['25|과거.7|1', '23|과거.13|1']),                   # 파노라마 감별 3 + 조직 사진 감별 (21,19,17)
    ('D03', 'ODT', 'A', ['25|과거.7|2', '23|과거.13|2']),                   # 방사선 소견 가장 관련 없는 병소 (20)
    # ---- P Pigmented lesions(윤혜정)
    ('P01', 'PIG', 'A', ['25|2024|21']),                                    # (탈) amalgam tattoo
    ('P02', 'PIG', 'A', ['25|2022.3|2', '24|2022.3|2', '23|2022.3|2']),     # Oral melanocytic lesion 3개 (22)
    ('P03', 'PIG', 'A', ['25|2022.3|3', '24|2022.3|3', '23|2022.3|3']),     # 파란색·검은색 3 · 붉은 4 (22)
    ('P04', 'PIG', 'A', ['25|2022.3|4', '24|2022.3|4', '23|2022.3|4']),     # 혀 Blue·Purple 3 (22) — 23·24판 답 → 25판 '해설참조'
    ('P05', 'PIG', 'C', ['25|과거.8|2', '23|과거.14|2']),                   # melanoma ABCDE의 E (21,18,17) — 옛 연조직 종창 강의 · 25 pigmented lesions p.3 ABCDE
    # ---- S Intraoral soft tissue swelling(윤혜정 — 25 강의계획서에서 빠짐)
    ('S01', 'SOFT', 'C', ['25|2024|20']),                                   # (탈) 출혈성 치은 병소 감별진단(2024)
    ('S02', 'SOFT', 'C', ['25|과거.8|1', '23|과거.14|1']),                  # 국소적 치은 종창 5가지 (21,20,19,17)
    ('S03', 'SOFT', 'C', ['25|과거.8|3', '23|과거.14|3']),                  # 혀 신경기원 종양 3 (21,20)
    ('S04', 'SOFT', 'C', ['25|과거.8|4', '23|과거.14|4']),                  # Hemangioma 설명 고르기 (20)
    ('S05', 'SOFT', 'C', ['25|과거.8|5', '23|과거.14|5']),                  # 페니토인·니페디핀·사이클로스포린 — 치은비대 (20)
    # ---- X 구강 감염성 질환(오규영 2020 — 21년부터 강의 없음)
    ('X01', 'INFX', 'C', ['24|과거.4|1', '23|과거.4|1']),                   # 허치슨 절치·멀버리 몰러 → Treponema pallidum (20)
    ('X02', 'INFX', 'C', ['24|과거.4|2', '23|과거.4|2']),                   # 의치 PAS Candida → candidiasis 관련 질환 (20)
    ('X03', 'INFX', 'C', ['24|과거.4|3', '23|과거.4|3']),                   # HHV-3 원발·재발 (20)
    # ---- H 진단혈액(황상미 — 24·25 수업 없음)
    ('H01', 'HEMA', 'C', ['24|2023|7']),                                    # PT·aPTT 튜브 (23)
    ('H02', 'HEMA', 'C', ['23|2022.7|1', '23|과거.9|2']),                   # 2세 여아 선별검사 아닌 것 (22 '짤 문항' · 과거 20,18)
    ('H03', 'HEMA', 'C', ['23|과거.9|1']),                                  # 말초혈액 관찰 안 되는 세포 (20)
    # ---- R 혈액형, 헌혈과 수혈(김형석 — 24·25 수업 없음)
    ('R01', 'TRF', 'C', ['24|2023|3', '23|과거.10|3']),                     # cis-AB (23 · 과거 21,20,18)
    ('R02', 'TRF', 'C', ['24|2023|4', '23|과거.10|2']),                     # 한국인 RhD 비율 객관식 (23 · 과거 18)
    ('R03', 'TRF', 'C', ['24|2023|5']),                                     # 성분수혈 아닌 것 (23)
    ('R04', 'TRF', 'C', ['23|과거.10|1']),                                  # RhD 음성 비율 (20,19,17)
    ('R05', 'TRF', 'C', ['23|과거.10|4']),                                  # ABO 발견 시기(연도 표기 없음 — "강의자료에 없는 내용")
    ('R06', 'TRF', 'C', ['23|과거.10|5']),                                  # 헌혈 최소 몸무게(연도 표기 없음)
    ('R07', 'TRF', 'C', ['23|과거.10|6']),                                  # 헌혈 할 수 없는 상황(연도 표기 없음)
    ('R08', 'TRF', 'C', ['23|과거.10|7']),                                  # Duffy 혈액군(연도 표기 없음)
    ('R09', 'TRF', 'C', ['23|과거.10|8']),                                  # 수혈 전 검사 3(연도 표기 없음)
    # ---- K 임상화학검사(이경훈 23 · 송정한 22까지 — 24·25 수업 없음)
    ('K01', 'CHEM', 'C', ['24|2023|6']),                                    # 그래프 rule violation (23)
    ('K02', 'CHEM', 'C', ['23|2022.9|1', '23|과거.8|2']),                   # NCEP ATP III 틀린 것 (22 · 과거 객,20,19 — 보기 같음)
    ('K03', 'CHEM', 'C', ['23|과거.8|4']),                                  # 당화혈색소·공복혈당 틀린 것 (21)
    ('K04', 'CHEM', 'C', ['23|과거.8|5']),                                  # 암 표지자 (21)
    ('K05', 'CHEM', 'C', ['23|과거.8|1']),                                  # 간기능 잘못 짝 (20,19)
    ('K06', 'CHEM', 'C', ['23|과거.8|3']),                                  # 당뇨 검사 옳은 것 (18)
]
def _blk(b):
    x = BYKEY.get(b); assert x, b; return x
CANON = [(cid, _blk(bs[0])['ed'], _blk(bs[0])['sec'], _blk(bs[0])['num']) for cid, lk, tier, bs in G]
OTHER = {cid: [(_blk(b)['ed'], _blk(b)['sec'], _blk(b)['num']) for b in bs[1:]] for cid, lk, tier, bs in G if bs[1:]}
LK = {cid: lk for cid, lk, tier, bs in G}
TIER = {cid: tier for cid, lk, tier, bs in G}
CROPS = {}
FIG_NOT = {'T09'}   # '방사선 사진 상에서'(글 속 말 — 그림 문항 아님)
FIG_EXTRA = {'C04'}   # 문제 첫 줄에 '사진' 낱말이 없지만 JB 문제에 파노라마가 실림(25판 p.27 · 23판 p.32 — 그림 안 붉은 글씨 DDx = 답 글자)
TALRE = re.compile(r'\(\s*탈\s*\)|\(\s*\d\d\s*,\s*탈\s*\)|^\s*\d{1,2}\s+탈\s')   # (탈) · 24판 '13 탈 OLP …'
Q = []
for cid, ed, sec, num in CANON:
    x = find(ed, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t)
    yrs = set(ty) | ({secyear(sec)} if secyear(sec) else set())
    for (e2, s2, n2) in OTHER.get(cid, []):
        x2 = find(e2, s2, n2); assert x2, (cid, e2, s2, n2)
        if secyear(s2): yrs.add(secyear(s2))
        yrs |= tag_years(x2['text'])[0]
    short = re.sub(r'^\s*\d{1,2}(\s*-\s*\d{1,2})?\s*[.．]{0,2}\s*', '', t.split('\n')[0]).strip()
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': TIER[cid], 'prof': '',
              'src': f'JB {ed}판 · {seclabel(sec)} {num}번', 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True),
              'secy': secyear(sec), 'tal': bool(TALRE.search(stem_of(t))), 'pick': ''})

# ---------- 3. annotations ----------
import emph
EMPH = emph.apply
def cite_html(s, em=False):
    toks = re.split(r'(\[\[[A-Z0-9]+:[^\]]+\]\])', s)
    s = ''.join(t if t.startswith('[[') else (EMPH(html.escape(t, quote=False)) if (em and EMPH) else html.escape(t, quote=False)) for t in toks)
    def rep(m):
        k, p = m.group(1), m.group(2); name = LECMAP[k][1]
        if not LECMAP[k][0]: return f'<button class="cite t" data-k="{k}" data-p="">{name} ‘{p}’</button>'
        return f'<button class="cite" data-k="{k}" data-p="{p}">{name} p.{p}</button>'
    s = re.sub(r'\[\[([A-Z0-9]+):([^\]]+)\]\]', rep, s)
    return s.replace('⚠', '<b class="warn">⚠</b>').replace('💡', '<b class="bulb">💡</b>')
cited = set()
def collect(s):
    for m in re.finditer(r'\[\[([A-Z0-9]+):([^\]]+)\]\]', s):
        k, p = m.group(1), m.group(2)
        if LECMAP.get(k, (None,))[0] and p.isdigit(): cited.add((k, int(p)))
ANN = {}; cur = None
if os.path.exists(DIR + '/annot.txt'):
    for line in open(DIR + '/annot.txt', encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('@'):
            parts = [p.strip() for p in line[1:].split('|')]
            cur = {'v': '', 'yrs': [], 'yrsnote': '', 'lec': [], 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': [], 'K': []}; ANN[parts[0]] = cur
            for p in parts[1:]:
                k, _, v = p.partition('=')
                if k == 'yrs': cur['yrs'] = [int(y) for y in v.split(',') if y.strip()]
                elif k == 'lec': cur['lec'] = [v] if v else []
                else: cur[k] = v
        elif cur is not None and len(line) > 2 and line[1] == ':' and line[0] in 'AMNK':
            collect(line); cur[line[0]].append(cite_html(line[2:].strip()))
for q in Q:
    a = ANN.get(q['id'])
    if a:
        lk_ = a['lec'][0].split(':')[0] if a['lec'] else ''; lk_ = getattr(S, 'IMG_ALIAS', {}).get(lk_, lk_)
        lkp_ = a['lec'][0].split(':')[1] if a['lec'] and ':' in a['lec'][0] else ''
        q.update({'v': a['v'], 'yrsnote': a['yrsnote'], 'rel': a['rel'], 'pair': a['pair'], 'A': a['A'], 'M': a['M'], 'N': a['N'], 'K': a.get('K', []), 'lk': lk_ or LK[q['id']], 'lkp': int(lkp_) if lkp_.isdigit() else None})
        q['yrs'] = sorted(set(q['base']) | set(a['yrs']), reverse=True); q['xtra'] = sorted(set(a['yrs']) - set(q['base']), reverse=True)
    else:
        q.update({'v': 'na', 'yrsnote': '', 'rel': '', 'pair': '', 'A': [], 'M': [], 'N': [], 'K': [], 'lk': LK[q['id']], 'xtra': []}); q['yrs'] = sorted(q['base'], reverse=True)
    q['prof'] = LK_PROF.get(q['lk'], '')
    o = []
    for (e2, s2, n2) in OTHER.get(q['id'], []):
        x2 = find(e2, s2, n2)
        if x2: o.append({'ed': e2, 'sec': s2, 'num': n2, 'pg': x2['pg'], 'pg2': x2['pg2'], 'text': x2['text']})
    q['other'] = o; q['lab24'] = ''; q['crops'] = CROPS.get(q['id'], {})
    q['fig'] = bool(re.search(r'사진|그림|도식|슬라이드', ' '.join(q['text'].split('\n')[:4]))) and q['id'] not in FIG_NOT or q['id'] in FIG_EXTRA   # 그림 없음(K01·X02·N04 — JB에 사진이 실리지 않음)은 다음 단계 jb_crops nofig: absent

# 답 칸 시작(build4 split_qa는 '답'·'[답]' 줄만 답으로 봄) — JB 원문이 '정답 :'(25판)이거나 답 머리 없이 답만 적힌 카드 = annot ans=와 같은 지시를 기본으로(annot에 ans=를 적으면 그것이 이김 · 글자는 그대로)
ANS_DEFAULT = {**{cid: '정답' for cid in ('B01', 'I01', 'M01', 'M02', 'M03', 'N01', 'J01', 'J02', 'J04', 'P03', 'P04')},
               'K01': '1(3s)'}   # 24판 2023 6번 — 문제 아래 '1(3s) rule violation'(밑줄 없는 답 줄 · '답' 머리 없음)
for cid, v in ANS_DEFAULT.items():
    ANN.setdefault(cid, {}).setdefault('ans', v)

LECT = []; TABLES = []
# ---------- 5. predicted ----------
PRED = []; cur = None
for _pf, _fn in (('pred.txt', ''), ('final.txt', '1')):   # 10-29 사용자 '최종 N제라는 탭' — final.txt = 같은 문법(머리 fn=1)
  if not os.path.exists(DIR + '/' + _pf): continue
  for line in open(DIR + '/' + _pf, encoding='utf-8'):
    line = line.rstrip('\n')
    if line.startswith('@'):
        p = [x.strip() for x in (line[3:] if line.startswith('@P ') else line[1:]).split('|')]
        cur = {'k': p[0], 't': '', 'b': '', 'q': '', 'a': ''}
        for x in p[1:]:
            k, _, v = x.partition('='); cur[k] = v
        if _fn: cur['fn'] = _fn
        PRED.append(cur)
    elif line.startswith('Q:') and cur: cur['q'] = cite_html(line[2:].strip()); cur['q_raw'] = line[2:].strip()
    elif line.startswith('A:') and cur: collect(line); cur['a'] = cite_html(line[2:].strip()); cur['a_raw'] = line[2:].strip()
# ---------- 6. images ----------
def b64(im, q):
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
IMG = {'jb': {}, 'lec': {}, 'crop': {}}
for ed, n in NPAGES.items():
    man = json.load(open(f'{BASE}{SUB}_20{ed}/manifest.json'))
    vis = {p['page_number'] for p in man['pages'] if p.get('has_visual_content')}
    for i in range(1, n + 1):
        if not os.path.exists(f'{BASE}{SUB}_20{ed}/{i}.jpeg'):   # JB 쪽 이미지가 없는 환경(클라우드 세션) — 지금 docs/packs의 쪽 이미지를 그대로(tools/jblpaths.prev_jb_pages)
            IMG['jb'][f'{ed}-{i}'] = J.prev_jb_pages(SUB)[f'{ed}-{i}']; continue
        im = Image.open(f'{BASE}{SUB}_20{ed}/{i}.jpeg').convert('RGB')
        if i in vis: IMG['jb'][f'{ed}-{i}'] = b64(im, 50)
        else: IMG['jb'][f'{ed}-{i}'] = b64(im.convert('L').resize((860, int(im.size[1] * 860 / im.size[0]))), 32)
# ---------- 7. ledger ----------
LEDGER = []
idmap = {(q['ed'], q['sec'], str(q['num'])): q['id'] for q in Q}
rev = {}
for cid, lst in OTHER.items():
    for (e2, s2, n2) in lst: rev.setdefault((e2, s2, str(n2)), []).append(cid)
for ed in NPAGES:
    for x in blocks[ed]:
        key = (ed, x['sec'], str(x['num'])); first = x['text'].split('\n')[0][:70]
        if key in idmap: st, to = 'card', [idmap[key]]
        elif key in rev: st, to = 'dup', rev[key]
        else: st, to = 'ref', []
        LEDGER.append({'ed': ed, 'sec': x['sec'], 'num': x['num'], 'pg': x['pg'], 'first': first, 'st': st, 'to': to})
def ment(ed, pages):
    t = ''
    for p in pages:
        s = P.rd(f'{BASE}{SUB}_20{ed}/{p}.txt'); t += '\n'.join(l for l in s.split('\n') if '무단인쇄' not in l and l.strip()) + '\n'
    return t.strip()
MENT = {'25': ment('25', [1, 2]), '24': ment('24', [1, 2]), '23': ment('23', [1, 2])}   # 판 머리 멘트·수업 표 쪽
if __name__ == '__main__':
    used = {}
    for cid, lk, tier, bs in G:
        for b in bs: used.setdefault(b, []).append(cid)
    allk = [P.key(x) for ed in NPAGES for x in blocks[ed]]
    print('Q', len(Q), '· 블록', len(allk), '· 묶음 안 블록', len(used), '· 못 쓴 블록', [k for k in allk if k not in used], '· 없는 블록', [k for k in used if k not in allk])
    print('두 카드 이상에 든 블록', {k: v for k, v in used.items() if len(v) > 1})
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')})
    for q in Q: print(f"{q['id']} {q['tier']} {LK[q['id']]:5} {str(q['yrs']):22} {q['jbtag'][:28]:28} {'탈 ' if q['tal'] else ''}{q['short'][:46]}")
