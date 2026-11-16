import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
"""HINS 의료전달체계와 건강보험(4Q) — JB 23·24·25판 → 정식 문항(Q)·같은 문제의 다른 판본(other)·대조표(LEDGER) (2026-11-16 JB 단계 · work/HINS/jb/R_JB_HINS.md)
id = 강의 글자 + 번호(강의 안에서 최근 해 먼저 · jb_lock.json이 잠금 — 번호 당기기 금지):
  S 보건의료체계(HSYS) · I 건강보험제도(INS) · M 의료법(MED) · L 보건의료기본법·지역보건법·국민건강증진법(BLAW) · P 건강보험과 치과진료의 실제(PRAC)
  B 혈액·응급·마약(BEM) · F 감염병(INF) · H 호스피스·연명의료(HOS) · A 후천성면역결핍증(AIDS) · Q 검역법(QUA — 24 자료 · 25 수업 안 함)
  X 외래교수 강의(EXT — 올해 강의 없음 · 참고) · O 구강보건법(OHL — 올해 강의 없음 · 참고)
묶음 G = (id, 강의 키, tier, [칸 토큰 …]) — 칸 토큰 '24|n' = 25판 2024 칸 n번 · '23S|n'·'23H|n'·'23X|n' = 2023 칸 송영하·한동헌·외래 n번(25판 → 24판) ·
  '22S|n'·'22H|n'·'22X|n' = 2022 칸(25판 → 24판 → 23판) · '21|n' = 2021 칸(24판 → 23판) · '20|n' = 2020 칸(23판)
  첫 토큰의 첫 블록 = 정식(가장 최신 판·가장 최근 칸) · 나머지 = 같은 문제의 다른 판본(OTHER)
  · 판 사이 같은 문제 = 같은 칸 같은 번호(판마다 글 같음 — 보고 1절 diff) + JB 괄호 연도 사슬로 이어진 다른 칸 문항
  · 괄호 사슬이 없고 문제 글·빈칸이 다른 것(예 2021 명찰 M16 ↔ 2020 명찰 M33)은 별개 — 관련 문항(annot rel=)은 다음 단계(짝 목록 보고 3절)
  · 괄호 사슬로 이어졌는데 학습부 답이 판·칸마다 다른 것(X05 사보험·X06 의료 시스템 문제·X07 활동치과의사 수·B05 채혈 금지)은 한 카드 — 앞면 = 가장 최근 칸, 옛 답 = 📜 이전 답(10-25c) · 보고 5절"""
import re, json, io, base64, os, html, sys
from PIL import Image
DIR = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, DIR)
import parse_hins as P, subject as S
BASE = J.JBX; SUB = 'HINS'
NPAGES = P.NPAGES
LECMAP = S.LECMAP

# ---------- 1. JB blocks ----------
blocks = {}
for ed, n in NPAGES.items():
    out = []
    for x in P.parse(ed, n):
        x['text'] = '\n'.join(x['lines']).strip(); out.append(x)
    blocks[ed] = out
ANSRE = re.compile(r'^\s*\[?답\]?\s*[:：)]|^\s*답\s*$')
def stem_of(t):
    out = []
    for l in t.split('\n'):
        if ANSRE.match(l): break
        out.append(l)
    return ' '.join(out)
NOISE = re.compile(r'(반짤반탈|짤 변형|짤|탈|년도|년|이전|이후|~|’|\')')
def tag_years(text):
    """문항 첫머리(답 이전)의 연도 괄호 전부 — (24,23,22,21) · (22, 21,18,14) · (21,20,19,18,12,10 이전) · (반짤반탈,23) · (탈)·(불완전복원)·( 1 )은 연도 아님"""
    ys, raw = set(), []
    for m in re.finditer(r'\(([^()]*)\)', stem_of(text)):
        g = m.group(1)
        g2 = NOISE.sub(' ', g).replace('，', ',').strip().strip(',').strip()
        if not re.fullmatch(r'(20\d\d|\d\d)(\s*[,、]\s*(20\d\d|\d\d))*', g2): continue
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
# 강의별 담당(25 담당 — 26 자료가 아직 없어 모든 강의가 25 임시본 · RULES 14 b)
LK_PROF = {'HSYS': '송영하', 'INS': '송영하', 'MED': '송영하', 'BLAW': '송영하', 'PRAC': '송영하',
           'NHI': '한동헌', 'BEM': '한동헌', 'INF': '한동헌', 'HOS': '한동헌', 'AIDS': '한동헌', 'QUA': '한동헌',
           'EXT': '외래교수', 'OHL': '김현덕'}
_SEC = {'S': '송영하', 'H': '한동헌', 'X': '외래'}
_EDS = {'24': ['25'], '23': ['25', '24'], '22': ['25', '24', '23'], '21': ['24', '23'], '20': ['23']}
def _exp(tok):
    """칸 토큰 → [(판, 칸, 번호) …] (가장 최신 판 먼저)"""
    c, num = tok.split('|'); y = c[:2]; who = _SEC.get(c[2:], '')
    sec = f'20{y}-4Q' + (f' · {who}' if who else '')
    return [(ed, sec, num) for ed in _EDS[y]]
G = [
    # ---- S 보건/구강보건의료체계(송영하 · 21·20 = 김현덕 '구강보건진료제도의 개념 및 총론')
    ('S01', 'HSYS', 'A', ['24|14', '23S|1']),   # 보건의료체계에 영향을 주는 요인이 아닌 것 (24,23)
    ('S02', 'HSYS', 'A', ['24|18']),            # 기대수명 연장 사회현상 아닌 것 (탈) — 답 참고 그림 Social medicine(p.1-4)
    ('S03', 'HSYS', 'A', ['24|19']),            # 구강 보건진료 자원 아닌 것 (탈)
    ('S04', 'HSYS', 'A', ['23S|2']),            # 구강보건의료체계 비교 모형 빈칸 (탈) — 그림 문항
    ('S05', 'HSYS', 'A', ['23S|3']),            # 일차 구강보건의료가 아닌 것 (탈)
    ('S06', 'HSYS', 'A', ['22S|1']),            # 치과의료의 특수성 옳지 않은 것
    ('S07', 'HSYS', 'A', ['22S|2']),            # WHO 정의 용어 — 일차 보건의료
    ('S08', 'HSYS', 'A', ['22S|3']),            # Health system dynamic framework 그림 context 빈칸 — 그림 문항
    ('S09', 'HSYS', 'A', ['21|22']),            # 보건의료체계 … 생산, 배분, ( ) (21,20) — 관련 S10
    ('S10', 'HSYS', 'A', ['21|40']),            # 보건의료체계 … ( )하는데 … 사회체계의 ( ) (21,20,19)
    ('S11', 'HSYS', 'A', ['21|23']),            # 보건의료체계의 3요소 (21,20)
    ('S12', 'HSYS', 'A', ['21|37']),            # 2,3차 병원은 중증질환의 ( )환자 — 입원
    ('S13', 'HSYS', 'A', ['21|54']),            # 구강보건전달체계 2차진료 조합
    ('S14', 'HSYS', 'A', ['20|1']),             # 1차진료는 경증질환의 ( )환자 — 외래
    ('S15', 'HSYS', 'A', ['20|29']),            # 국가의료체계의 일반원칙
    # ---- I 의료제공체계·건강보험제도(송영하 · 21·20 = 김현덕 '구강보건 전달체계'·'개념 및 총론')
    ('I01', 'INS', 'A', ['24|15', '23S|5']),    # 진료보수 지불제도 — 인두제 (24,23)
    ('I02', 'INS', 'A', ['24|20']),             # 사회보장 옳지 않은 것 — 공공부조 (탈)
    ('I03', 'INS', 'A', ['24|21']),             # 사회보장기본법 제3조 빈칸 (23)
    ('I04', 'INS', 'A', ['24|26']),             # 건강보험 운영 체계 빈칸 그림 (탈) — 그림 문항
    ('I05', 'INS', 'A', ['23S|4']),             # Safety net — 공공부조 (탈)
    ('I06', 'INS', 'A', ['22S|4']),             # 일차 진료의뢰 전 단계 옳지 않은 것
    ('I07', 'INS', 'A', ['22S|5']),             # 국민건강보험제도 보험자
    ('I08', 'INS', 'A', ['22S|7']),             # 건강보험제도 특성
    ('I09', 'INS', 'A', ['22S|14']),            # 재개정 연혁(복원 미흡)
    ('I10', 'INS', 'A', ['21|50']),             # 의료지역화 빈칸빵 (21,20)
    ('I11', 'INS', 'A', ['21|31']),             # 구강 진료 = ( )과 요양 — 검진
    ('I12', 'INS', 'A', ['21|55']),             # 요양 = 예방, 치료, 재활 (21,20)
    ('I13', 'INS', 'A', ['20|2']),              # 상대가치에 근거한 ( ) — 행위별 수가제
    ('I14', 'INS', 'A', ['20|3']),              # ( )를 기준으로 DRG — 진단명
    ('I15', 'INS', 'A', ['20|26']),             # 혼합구강보건진료제도
    ('I16', 'INS', 'A', ['20|27']),             # 2017 면허 치과의사 중 비활동 ( )명
    ('I17', 'INS', 'A', ['20|28']),             # 치과 진료 대부분 — 충치·잇몸치료
    ('I18', 'INS', 'A', ['20|30']),             # 건강보험제도 옳은 것(보기 미복원)
    ('I19', 'INS', 'A', ['20|32']),             # 2017 활동 치과의사 비율
    # ---- M 의료법(송영하 · 21·20 = 김현덕)
    ('M01', 'MED', 'A', ['24|22']),             # 시행규칙 — 보건복지부령 (탈)
    ('M02', 'MED', 'A', ['24|23']),             # 의료법상 의료기관 아닌 것 — 재활병원 (탈) · 관련 M03
    ('M03', 'MED', 'A', ['23S|6']),             # 의료법상 의료기관 아닌 것 — 보건소 (탈)
    ('M04', 'MED', 'A', ['23S|7', '22S|12']),   # 진단서 교부 방법 (23,22)
    ('M05', 'MED', 'A', ['22S|8']),             # 국시 보건의약관리법규 아닌 것 — 구강보건법
    ('M06', 'MED', 'A', ['22S|10']),            # 의료법상 의료인
    ('M07', 'MED', 'A', ['21|1', '20|31']),     # 2년 이내 재교부 불가 (21,18,15)·(18,15)
    ('M08', 'MED', 'A', ['21|5']),              # 실태보고(불완전복원) (21,20) — 해설 속 예상 문항 (18,14,11)(답 전이라 첫머리로 셈 = check_years와 같음 · 11-16 JBV: '아마 … 예상' 옛 JB 인용이라 사용자 확인 — V_JB_HINS 5절)
    ('M09', 'MED', 'A', ['21|7']),              # 진료기록부 보관·실태보고
    ('M10', 'MED', 'A', ['21|8']),              # 원격의료 책임 (21,20)
    ('M11', 'MED', 'A', ['21|20']),             # 진단서 허위 작성 ( )년간 면허 ( ) · 관련 M40
    ('M12', 'MED', 'A', ['21|21']),             # 전문병원
    ('M13', 'MED', 'A', ['21|27']),             # 상급병원 인증 주기
    ('M14', 'MED', 'A', ['21|29']),             # 국시합격 ( ) 이내 학위 (21,20,19)
    ('M15', 'MED', 'A', ['21|30']),             # 의료인은 ( ) 빌려주면 안 됨 · 관련 M32
    ('M16', 'MED', 'A', ['21|4']),              # 의료인 아닌 사람 의료행위 시 명찰 · 관련 M33
    ('M17', 'MED', 'A', ['21|32']),             # 진료 후 사망 ( )시간 이내 진단서 (21,20,19) · 관련 M35
    ('M18', 'MED', 'A', ['21|34']),             # 치과의사 법정 임무 — 구강 보건지도 · 관련 M29
    ('M19', 'MED', 'A', ['21|35']),             # 태아 성 고지 ( )주
    ('M20', 'MED', 'A', ['21|36']),             # 출생·사망·( ) 증명서
    ('M21', 'MED', 'A', ['21|38']),             # 치과( ) 개원 시도지사 허가 · 관련 M39
    ('M22', 'MED', 'A', ['21|42']),             # 의료법 17조 2항 조산사 빈칸
    ('M23', 'MED', 'A', ['21|44']),             # 치과병의원 공통 시설·외래환자·간호사 정원
    ('M24', 'MED', 'A', ['21|45']),             # 국가고시 부정행위 응시 제한 (21,20,19)
    ('M25', 'MED', 'A', ['21|47']),             # 치과병원 의과 진료과목 — 가정의학과
    ('M26', 'MED', 'A', ['21|52']),             # 종합병원 치과 필수 아닌 병상수 (21,20) · 관련 M30
    ('M27', 'MED', 'A', ['21|56']),             # 100-300 병상 종합병원 9개의 ( )
    ('M28', 'MED', 'A', ['20|4']),              # 의료인 — 간호사
    ('M29', 'MED', 'A', ['20|5']),              # 치과의사 역할 빈칸빵
    ('M30', 'MED', 'A', ['20|6']),              # 300병상 이상 종합병원 필수 진료과목 ( )개
    ('M31', 'MED', 'A', ['20|7']),              # 상급병원 진료과목 수
    ('M32', 'MED', 'A', ['20|8']),              # 발급받은 ( )를 빌려줘서는 — 면허증
    ('M33', 'MED', 'A', ['20|9']),              # 학생 진료 시 ( ) — 명찰
    ('M34', 'MED', 'A', ['20|10']),             # 자격 정지 몇 번 → 면허 취소
    ('M35', 'MED', 'A', ['20|11']),             # 48시간 이내 사망 — ( )나 증명서
    ('M36', 'MED', 'A', ['20|12']),             # 치과의사 중앙회 — 민법
    ('M37', 'MED', 'A', ['20|14']),             # 치과의원 의과진료과목(단답)
    ('M38', 'MED', 'A', ['20|15']),             # 한방내과, ( ) 개원(단답)
    ('M39', 'MED', 'A', ['20|16']),             # 치과병원 설립 ( )의 허가
    ('M40', 'MED', 'A', ['20|17']),             # 진단서 허위 작성 처벌
    # ---- L 보건의료기본법·지역보건법·국민건강증진법(송영하 · 21·20 = 김현덕 '보건관련법')
    ('L01', 'BLAW', 'A', ['24|16', '23S|8']),   # 지역보건의료계획 수립 주기 (24,23)
    ('L02', 'BLAW', 'A', ['24|24']),            # 지역보건의료계획 내용 (탈)
    ('L03', 'BLAW', 'A', ['24|25']),            # 보건의료발전계획 내용 아닌 것 (탈)
    ('L04', 'BLAW', 'A', ['23S|9']),            # 국민건강증진법 보건교육 내용 아닌 것 (탈)
    ('L05', 'BLAW', 'A', ['22S|9']),            # 평생국민건강관리체계 아닌 것
    ('L06', 'BLAW', 'A', ['22S|11']),           # 국민건강증진부담금 사업 아닌 것
    ('L07', 'BLAW', 'A', ['22S|13']),           # 방송광고 금지 주류 도수
    ('L08', 'BLAW', 'A', ['21|25']),            # 담배갑 경고 문구·그림 크기
    ('L09', 'BLAW', 'A', ['21|33']),            # 보건의료기관 … ( )이 정하는 기관 — 대통령령 · 관련 L13
    ('L10', 'BLAW', 'A', ['21|46']),            # 보건의료원 빈칸빵
    ('L11', 'BLAW', 'A', ['21|48']),            # 담배 발암물질(객관식)
    ('L12', 'BLAW', 'A', ['21|53']),            # 주요 시책 추진방안 매년 · 관련 L16
    ('L13', 'BLAW', 'A', ['20|18']),            # 보건의료기관 — 약국
    ('L14', 'BLAW', 'A', ['20|19']),            # 보건의료(발전)계획 ( )년마다
    ('L15', 'BLAW', 'A', ['20|20']),            # 보건의료발전계획 — 국무회의
    ('L16', 'BLAW', 'A', ['20|21']),            # 주요 정책 — 관계 중앙행정기관의 장 / 국회
    ('L17', 'BLAW', 'A', ['20|22']),            # 국민건강증진법 목적
    ('L18', 'BLAW', 'A', ['20|25']),            # (초록책 빈칸빵) 구강건강관리 위생사업(불완전 복원 — 국민건강증진법 관련 예상)
    ('L19', 'BLAW', 'A', ['20|38']),            # 국민건강증진법 행정 옳지 않은 것
    ('L20', 'BLAW', 'A', ['20|39']),            # 건강증진기금 사용 용도
    # ---- O 구강보건법(올해 강의 없음 — 20 김현덕 '보건관련법' · 22 송영하 "수업 중에 구강보건법이 빠져 있는 점을 강조")
    ('O01', 'OHL', 'C', ['20|13']),             # 구강보건사업 기본계획 ( )년마다
    ('O02', 'OHL', 'C', ['20|23']),             # 구강관리용품 — 예방
    ('O03', 'OHL', 'C', ['20|24']),             # 사업장 구강보건 — 보건교육 및 건강진단
    # ---- P 건강보험과 치과진료의 실제(송영하 — 23 칸 3문항 JB 참고 = 241113 같은 제목)
    ('P01', 'PRAC', 'A', ['23S|10']),           # 총 진료비에 포함되지 않는 것 (탈)
    ('P02', 'PRAC', 'A', ['23S|11']),           # 가산료 빈칸 — 가산율 (탈)
    ('P03', 'PRAC', 'A', ['23S|12']),           # 건강보험 청구 시 해야 할 일 아닌 것 (탈)
    ('P04', 'PRAC', 'C', ['23X|7']),            # 상대가치점수 (탈) — 외래(최희수 '치과건강보험의 실제') · 내용은 이 강의 p.2·3
    # ---- B 혈액·응급·마약(한동헌)
    ('B01', 'BEM', 'A', ['24|10', '23H|7', '21|39']),             # 응급의료법 재개정 (24,23,21)
    ('B02', 'BEM', 'A', ['23H|8', '22H|12', '21|16']),            # 응급의료 국가·지자체 책임 아닌 것 (23,22,21) — JB "선지가 약간 변형"
    ('B03', 'BEM', 'A', ['24|11', '23H|9', '22H|14', '21|3']),    # 마약 처방전 보관 기간 (24,23,22,21)·(22,21,18,14) · 관련 B13
    ('B04', 'BEM', 'A', ['24|11(두번째)', '23H|10', '22H|13']),   # 마약취급업자 틀린 것 (24,23,22) · 관련 B06
    ('B05', 'BEM', 'A', ['24|12', '22H|16', '21|43']),            # 채혈 금지 대상자 (24,22,21) — 답 25판 1번 / 23·24판 1,3,5번
    ('B06', 'BEM', 'A', ['23H|11']),                               # 투약 교부 마약 관리책임자 (탈)
    ('B07', 'BEM', 'A', ['22H|10', '21|17']),                      # 채혈관리대상자(불완전 복원) (22,21)
    ('B08', 'BEM', 'A', ['22H|11', '21|11']),                      # 응급 진료 틀린 것 (22,21)
    ('B09', 'BEM', 'A', ['22H|17', '21|13']),                      # 마약관리자 할 수 있는 사람 — 약사 (22,21,20)
    ('B10', 'BEM', 'A', ['20|40']),             # 마약류 관리 틀린 것
    ('B11', 'BEM', 'A', ['20|41']),             # 모르핀 저장 방법
    ('B12', 'BEM', 'A', ['20|42']),             # 마약류 관리자 치과의사 — 잡지 광고(짤 — 해설 속 예상 문항)
    ('B13', 'BEM', 'A', ['20|43']),             # 마약류 처방 내역 ( )년 보관
    ('B14', 'BEM', 'A', ['20|44']),             # 사고 마약류 발생 보고 기한
    ('B15', 'BEM', 'A', ['20|45']),             # 유효기간 지난 마약 폐기
    ('B16', 'BEM', 'A', ['20|46']),             # 마약 도난 고지 대상
    ('B17', 'BEM', 'A', ['20|47']),             # 마약 취급 허가 대상
    ('B18', 'BEM', 'A', ['20|48']),             # 모르핀 연구 신고 대상
    ('B19', 'BEM', 'A', ['20|49']),             # 한외마약
    ('B20', 'BEM', 'A', ['20|51']),             # 지역응급의료센터 비응급 환자 의뢰
    ('B21', 'BEM', 'A', ['20|52']),             # 응급의료 설명·동의(짤 — 해설 속 예상 문항)
    ('B22', 'BEM', 'A', ['20|53']),             # 구급차 사용
    ('B23', 'BEM', 'A', ['20|60']),             # 마약 투약 정보 보고 대상
    # ---- F 감염병의 예방 및 관리에 관한 법률(한동헌)
    ('F01', 'INF', 'A', ['24|8', '23H|3']),     # 감염병 정보 알 권리 — 국민 (23)
    ('F02', 'INF', 'A', ['24|9', '23H|1']),     # 감염병 환자 진단·검안 시 대처(24 칸은 괄호 없음 — 23 칸 1번과 보기·답 같음)
    ('F03', 'INF', 'A', ['23H|2', '22H|8', '21|9']),   # 고위험병원체 분리 신고 (23,22,21)
    ('F04', 'INF', 'A', ['22H|9', '21|28']),    # (감염병)관리위원회 (22,21)
    ('F05', 'INF', 'A', ['21|49']),             # 감염병 기본계획 ( )년마다 (21,20,19,18,12,10 이전)
    ('F06', 'INF', 'A', ['20|54']),             # 국가예방접종 대상 질병
    ('F07', 'INF', 'A', ['20|56']),             # 감염상태 — 보균자
    ('F08', 'INF', 'A', ['20|57']),             # 감염병환자·의사환자·보균자 옳지 않은 것
    ('F09', 'INF', 'A', ['20|58']),             # 감염병의심환자·역학조사 정의
    # ---- H 호스피스·완화의료 및 연명의료결정법(한동헌 — 22 새 강의)
    ('H01', 'HOS', 'A', ['24|13', '22H|15']),   # 연명의료행위 아닌 것 (24,22)
    ('H02', 'HOS', 'A', ['23H|12', '22H|18']),  # 연명의료중단등결정 환자 의사 확인 (23,22)
    ('H03', 'HOS', 'A', ['23H|13']),            # 연명의료중단 이행 시 계속할 것 — 물 공급 (탈)
    # ---- A 후천성면역결핍증 예방법(한동헌)
    ('A01', 'AIDS', 'A', ['24|2']),             # HIV 전문진료기관 설치·운영 기관장 (탈) · 관련 A05
    ('A02', 'AIDS', 'A', ['24|6', '22H|5', '21|6']),    # HIV 혈액 등 유통·판매 벌칙 (24,22,21)
    ('A03', 'AIDS', 'A', ['24|7', '22H|6', '21|10']),   # 정기검진 옳은 것 (24,22,21)
    ('A04', 'AIDS', 'A', ['24|17', '23H|4', '22H|1']),  # 감염인 사망 시 신고 (24,23,22)
    ('A05', 'AIDS', 'A', ['22H|4']),            # 전문기관·연구기관 설치 주체
    ('A06', 'AIDS', 'A', ['20|50']),            # 결핵·HIV 진단 사실을 가족에게 — 위반(비밀 누설)
    # ---- Q 검역법(한동헌 — 23·25 수업 안 함 · 24 자료 '(미수업)241002_한동헌_검역법')
    ('Q01', 'QUA', 'A', ['24|1', '23H|5', '22H|2', '21|26']),    # 검역법 옳은 것 (24,23,22,21)
    ('Q02', 'QUA', 'A', ['24|3', '23H|6', '22H|3', '21|41']),    # 검역 시간 옳은 것 (24,23,22,21)
    ('Q03', 'QUA', 'A', ['24|4', '21|18']),     # 검역사항이 아닌 것 (24,21)
    ('Q04', 'QUA', 'A', ['24|5', '22H|7', '21|14']),     # 검역감염병(사체 해부·검역비용·회항) (24,22,21)
    ('Q05', 'QUA', 'A', ['20|59']),             # 검역감염병인 것
    ('Q06', 'QUA', 'A', ['20|55']),             # 중증호흡기증후군 접촉자 격리 기간
    # ---- X 외래교수 강의(올해 강의 없음 — 참고 · 25판 "작년 기준 외래 교수님 강의는 시험에 출제되지 않은 것으로 보입니다")
    ('X01', 'EXT', 'C', ['23X|1', '22X|7', '20|33']),             # 공급자별 국민의료비 순서 (23,22,20)
    ('X02', 'EXT', 'C', ['23X|2', '22X|2', '21|12', '20|34']),    # Nudge effect (23,22,21,20,19)
    ('X03', 'EXT', 'C', ['23X|3', '22X|3', '21|19', '20|35']),    # SQL 빈칸 (23,22,21,20)
    ('X04', 'EXT', 'C', ['23X|4', '22X|5']),                      # 우리나라 건강보험 제도 (23,22) · 관련 X09
    ('X05', 'EXT', 'C', ['23X|5', '22S|6', '21|2', '21|51']),     # 사보험 특징이 아닌 것 (22,21,20)·(23,22,21) — 답 23 칸 4번 / 22·21 칸 1번(보기 순서 다름)
    ('X06', 'EXT', 'C', ['23X|6', '22X|4', '21|15']),             # 우리나라 의료 시스템의 문제 (23,22,21,19,18) — 답 23 칸 1번 / 22 칸 2,4(?) / 21 칸 ?
    ('X07', 'EXT', 'C', ['22X|1', '21|24']),                      # 인구 천명 당 활동치과의사 수 (22,21) — 답 0.31 / 21 칸 0.51(2018년 기준)
    ('X08', 'EXT', 'C', ['22X|6', '20|37']),                      # 문재인 케어 방향성 T/F (22,20)
    ('X09', 'EXT', 'C', ['20|36']),                               # 대한민국 의료보험
]
CANON = [(cid, *_exp(toks[0])[0]) for cid, lk, tier, toks in G]
OTHER = {}
for cid, lk, tier, toks in G:
    bl = [b for t in toks for b in _exp(t)][1:]
    if bl: OTHER[cid] = bl
LK = {cid: lk for cid, lk, tier, toks in G}
TIER = {cid: tier for cid, lk, tier, toks in G}
CROPS = {}   # JB 그림 조각(tools/jbfig.py → jb_crops.json)은 다음 단계 JF — 그림 문항 표 = 보고 3절
FIG = {'S04', 'S08', 'I04', 'I10'}   # 시험에 그림이 주어진 문항(JB 쪽에 그 그림이 있음) — S02 답 참고 그림·Q06 해설 표·X01 2022 칸 해설 그래프는 해설 쪽 그림(그림 문항 아님 · X01 시험 그래프는 JB에 없음)
Q = []
for cid, ed, sec, num in CANON:
    x = find(ed, sec, num); assert x, (cid, ed, sec, num)
    t = x['text']; ty, raw = tag_years(t)
    yrs = set(ty) | ({secyear(sec)} if secyear(sec) else set())
    for (e2, s2, n2) in OTHER.get(cid, []):
        x2 = find(e2, s2, n2); assert x2, (cid, e2, s2, n2)
        if secyear(s2): yrs.add(secyear(s2))
        yrs |= tag_years(x2['text'])[0]
    short = re.sub(r'^\s*\d{1,2}\s*[.．]\s*', '', t.split('\n')[0]).strip()
    Q.append({'id': cid, 'ed': ed, 'sec': sec, 'num': num, 'pg': x['pg'], 'pg2': x['pg2'], 'text': t, 'tier': TIER[cid], 'prof': '',
              'src': f'JB {ed}판 · {seclabel(sec)} {num}번', 'short': short[:52], 'jbtag': ' '.join(dict.fromkeys(raw)), 'base': sorted(yrs, reverse=True),
              'secy': secyear(sec), 'tal': bool(re.search(r'\(\s*탈\s*\)|\(\s*\d\d\s*,\s*탈\s*\)', stem_of(t))), 'pick': ''})

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
    q['fig'] = q['id'] in FIG

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
def ment(ed, pages, cut=None):
    """판 머리 멘트·수업 표 쪽 — cut = (쪽, 시작 글): 그 쪽은 그 글로 시작하는 줄부터 끝까지만(23판 3쪽 위 표가 글 순서에서 문항 뒤로 온 것 — parse_hins CUT)"""
    t = ''
    for p in pages:
        ls = [l for l in P.rd(f'{BASE}{SUB}_20{ed}/{p}.txt').split('\n') if '무단인쇄' not in l and l.strip()]
        if cut and p == cut[0]: ls = ls[next(i for i, l in enumerate(ls) if l.strip().startswith(cut[1])):]
        t += '\n'.join(ls) + '\n'
    return t.strip()
MENT = {'25': ment('25', [1, 2]), '24': ment('24', [1, 2]), '23': ment('23', [1, 2, 3], (3, P.CUT[('23', 3)]))}
if __name__ == '__main__':
    used = {}
    for cid, lk, tier, toks in G:
        for t in toks:
            for b in _exp(t): used.setdefault('|'.join(b), []).append(cid)
    allk = [f"{ed}|{x['sec']}|{x['num']}" for ed in NPAGES for x in blocks[ed]]
    print('Q', len(Q), '· 블록', len(allk), '· 묶음 안 블록', len(used), '· 못 쓴 블록', [k for k in allk if k not in used], '· 없는 블록', [k for k in used if k not in allk])
    print('두 카드 이상에 든 블록', {k: v for k, v in used.items() if len(v) > 1})
    print('ids 겹침', [c for c in LK if list(LK).count(c) > 1], '· 카드 수', len(G), len(set(LK)))
    print('ledger', {s_: sum(1 for r in LEDGER if r['st'] == s_) for s_ in ('card', 'dup', 'ref')}, [(r['ed'], r['sec'], r['num'], r['first'][:25]) for r in LEDGER if r['st'] == 'ref'])
    for ed in NPAGES: print(f' {ed}판', {s_: sum(1 for r in LEDGER if r['ed'] == ed and r['st'] == s_) for s_ in ('card', 'dup', 'ref')})
    if '-v' in sys.argv:
        for q in Q: print(f"{q['id']} {q['lk']:5} {q['tier']} {str(q['yrs']):30} {q['jbtag'][:34]:34} {q['short'][:44]}")
