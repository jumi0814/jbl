"""fmt_cases — 문제 형식 분류기 trend.fmt_of 회귀(브라우저 없음 · 1초 안)
손으로 쓴 문항(assemble Q와 같은 꼴 — text = 문제 줄 + JB 답 줄, lab24)으로 10-16 고친 판정을 고정한다.
- '다음 중 옳지 않은 것은?' + 보기 줄 5개(①~⑤ · 1)~5) · 줄바꿈으로 끊긴 보기) → 객관식 · '[객]'·'(객관식)' 라벨 → 객관식
- 같은 줄에 이어 쓴 보기 '(1) … (2) … (3) …' → 객관식 · 띄어쓰기 없는 '아닌것은'·'5 지 선다'·'가장 적절한 것' → 객관식
- 번호 빈칸 '( 1 ) 돌출'·'(2)가'·'[1]' → 빈칸 · 글자 빈칸 '(ㄱ)mm'·'A는 … B, C 등' → 빈칸(그림 A·B '설명하시오'는 서술형)
- 'T/F'·'O/X' → T/F · T/F 묶음의 평서문 한 문장('…한다.' · 끝 연도 괄호 '(20’, 19’)' 붙어도) → T/F
- '…비교하시오'·'비교하여 쓰시오' → 서술형 · 긴 증례의 5번째 줄 '…설명하시오' → 서술형 · 하위 질문 (1)(2)(3)은 보기 아님
- '…2개를 쓰시오' → 단답형 · '주관식' → 단답형 · 라벨 '[서술형]'은 보기 줄보다 먼저
- JB 답(답:·[답]·답)·정답 :·해설:) 안의 '설명'·'비교'·'T/F'·보기꼴 줄은 판정에 영향 없음
- 7과목 tools/<sid>/trend.py 사본이 모두 같음(빌드마다 같은 분류기)
사용: .venv/bin/python tools/tests/fmt_cases.py   (끝 줄 'fmt_cases RESULT PASS' · 실패면 'fmt_cases RESULT FAIL n' + exit 1)"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J
import hashlib, importlib.util
TP = _os.path.join(J.TOOLS, 'cons', 'trend.py')
_sp = importlib.util.spec_from_file_location('_fmt_cases_trend', TP); T = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(T)
fails = []
def ok(c, m):
    print(('  OK   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
def q(*lines, lab=''):
    return {'id': 'X', 'text': '\n'.join(lines), 'lab24': lab}

CASES = [
    # (이름, 기대 형식, 문항)
    ("'다음 중 옳지 않은 것은?' + ①~⑤ 보기 5줄", '객관식',
     q('1. 다음 중 Tooth whitening 에 대하여 옳지 않은 것은?', '① Carbamide peroxide 는 분해되어 H2O2 를 낸다', '② Walking bleaching 은 실활치에 쓴다',
       '③ 미백 직후에는 접착 강도가 떨어진다', '④ 10% CP 는 약 3.5% HP 에 해당한다', '⑤ 미백 효과는 영구적이다', '답: ⑤')),
    ("'다음 중 옳지 않은 것은?' + 1)~5) 보기(줄바꿈으로 끊긴 보기 포함)", '객관식',
     q('2. 다음 중 OHRQoL 에 관해 옳지 않은 것은?', '1) OHRQoL 은 구강건강관련 삶의 질을 일컫는다.', '2) 기능적 제한, 통증과 불편감, 심리사회적', '영향 3 가지를 측정한다.',
       '3) GOHAI 는 주로 노인 측정시 사용한다.', '4) OHIP-14 는 주로 일반 성인 측정시 사용한다.', '5) GOHAI 의 문항 수가 OHIP-14 보다 많다.', '답: 5')),
    ("'[객]' 라벨(보기 미복원)", '객관식', q('6. [객] Crack 의 정의 (25)', '답: 장기간에 걸친 수직방향 균열')),
    ("'(객관식)' 라벨", '객관식', q('7. (객관식) 그림 나오고 올바른 보기 고르시오. (2016, 2019)', '답: 3')),
    ("같은 줄 보기 '(1) … (2) … (3) … (4) …'", '객관식',
     q('31. Hypersensitivity 줄이는 치약 성분 (1) Potassium nitrate (2) Sodium bicarbonate (3) Calcium carbonate (4) Silica', '답: (1)')),
    ("띄어쓰기 없는 '아닌것은?' + 번호 없는 보기", '객관식',
     q('32. 상아세관을 물리적으로 막는 성분이 아닌것은?', 'Potassium nitrate', 'Fluoride', 'Ferric oxalate', 'Strontium chloride', '답: Potassium nitrate')),
    ("'가장 적절한 것은?'", '객관식', q('5. 이 환자에게 가장 적절한 처치는?', '답: 2')),
    ("번호 빈칸 '( 1 ) 돌출'", '빈칸', q('3. Class II div 1 에서 상악 전치는 ( 1 ) 돌출되어 있고 하악은 ( 2 ) 후퇴되어 있다.', '답: (1) 순측 (2) 후방')),
    ("번호 빈칸 '(2)가 있고'", '빈칸', q('4. 성공적인 골유착을 위해 (1)과 (2)가 있어야 한다.', '답: (1) 초기 고정 (2) 혈액 공급')),
    ("글자 빈칸 '(ㄱ)mm · (ㄴ)mm'", '빈칸', q('8. 임플란트와 자연치 사이는 (ㄱ)mm, 임플란트 사이는 (ㄴ)mm 이상 띄운다.', '답: ㄱ 1.5 ㄴ 3')),
    ("글자 빈칸 'A는 … B, C 등'", '빈칸', q('12. Dopamine의 재흡수를 차단하는 금연치료제인 A는 대표적인 부작용으로 B, C 등이 있다.', '답: A bupropion B 불면 C 구강건조')),
    ("그림 A·B를 '설명하시오'(빈칸 아님)", '서술형', q('10. 사진의 A와 B가 의미하는 바를 설명하시오.', '답: A 는 … B 는 …')),
    ("'T/F' 표시", 'T/F', q('4. Pilocarpine 은 M3 agonist 이다. (T/F)', '답: T')),
    ("'O/X' 표시", 'T/F', q('5. 다음 문장이 맞으면 O, 틀리면 X (O/X)', '1) Warfarin 은 vitamin K 길항제이다.', '답: O')),
    ("T/F 묶음의 평서문 한 문장 '…해야 한다.'", 'T/F', q('17. 모든 금연치료의약품은 금연 시작부터 복용해야 한다.', '답: F')),
    ("평서문 + 끝 연도 괄호 '(20’, 19’)'", 'T/F', q('9. 악하선이나 이하선 주변에 고농도 botulinum toxin 을 투여하면 타액량이 증가한다. (20’, 19’)', '답: F', '해설: 감소한다.')),
    ("'…비교하시오'", '서술형', q('5. Etch-and-rinse 와 self-etch 접착 시스템을 비교하시오.', '답: …')),
    ("'비교하여 쓰시오'(쓰시오여도 서술형)", '서술형', q('6. Inlay 와 direct filling 을 비교하여 쓰시오.', '답: …')),
    ("긴 증례 5번째 줄 '…설명하시오'", '서술형',
     q('11. 65 세 남성 환자가 내원하였다.', '상악 좌측 제 1 대구치 부위 통증을 주소로', '최근 6 개월간 체중 감소가 있었으며', '고혈압 약을 복용 중이다.', '이 환자의 진단과 치료 계획을 설명하시오.', '답: …')),
    ("하위 질문 (1)(2)(3)(보기 아님)", '서술형',
     q('3. 다음 증례에 대해 답하시오.', '(1) 진단명은?', '(2) 치료법을 쓰시오.', '(3) 예후를 설명하시오.', '답: (1) … (2) … (3) …')),
    ("'…2개를 쓰시오'", '단답형', q('3. Vital bleaching 의 비적응증 2개를 쓰시오. (24, 탈)', '답: 임산부, 심한 변색')),
    ("'주관식'(보기 중 고르는 주관식)", '단답형', q('4. 보기 12 개 중 하나 고르는 주관식 — 하악 관절원판의 위치 이상은?', '답: ADDwR')),
    ("'[서술형]' 라벨이 보기 줄보다 먼저", '서술형',
     q('2. [서술형] 다음 중 옳지 않은 것을 고르고 이유를 쓰시오.', '1) A', '2) B', '3) C', '4) D', '답: 3')),
    # ---- JB 답 안의 글자는 판정에 영향 없음 ----
    ("'답:' 뒤 '설명·비교·이유' + 보기꼴 줄 4개", '단답형',
     q('3. Vital bleaching 의 비적응증 2개를 쓰시오.', '답: 1) 임산부 — 설명: 안전성이 확립되지 않음', '2) 심한 변색 — 비교하면 효과 낮음', '3) 이유: 과민', '4) 균열치')),
    ("'[답]' 뒤 '서술·설명'", '단답형', q('8. 치은에서 가장 cervical 한 점의 이름은?', '[답] zenith — 서술형으로 설명하면 …')),
    ("'답)' 뒤 'T/F'·'옳지 않은'", '서술형', q('1. Non-vital bleaching 적응증과 금기증에 대해 서술하시오.', '답) T/F 가 아니라 서술 — 옳지 않은 것: …')),
    ("'정답 :'·'해설:' 뒤 번호 빈칸꼴 '(1)은'·'( 2 )'", '객관식',
     q('2. 다음 중 옳은 것은?', '① a', '② b', '③ c', '정답 : ②', '해설: (1)은 틀림 · ( 2 ) 가 맞음')),
    ("평서문 T/F + '답:'·'해설:'에 '설명하시오'", 'T/F', q('10. 국내 현행법상 처방전은 세 번까지 사용할 수 있다.', '답: F', '해설: 설명하시오 — 한 번만 사용할 수 있다.')),
]
VALID = {'객관식', 'T/F', '빈칸', '단답형', '서술형'}
for name, want, case in CASES:
    try: got = T.fmt_of(case)
    except Exception as e: got = f'오류 {type(e).__name__}: {e}'
    ok(got == want, f"{name} → {got}" + ('' if got == want else f"  (기대 {want} · 문제 부분 {' / '.join(T.q_lines(case))[:120]})"))
got_all = {T.fmt_of(c) for _, _, c in CASES}
ok(got_all <= VALID, f"fmt_of 값은 {sorted(VALID)} 안 — 나온 값 {sorted(got_all)}")
# 7과목 사본이 같음(build4가 tools/<sid>/trend.py를 씀)
H = {}
for sid in ('oms1', 'cons', 'impl', 'anat', 'geri', 'pharm', 'esth'):
    p = _os.path.join(J.TOOLS, sid, 'trend.py')
    if _os.path.exists(p): H[sid] = hashlib.md5(open(p, 'rb').read()).hexdigest()[:10]
ok(len(set(H.values())) == 1 and len(H) == 7, f"7과목 trend.py 사본 같음 {H if len(set(H.values())) != 1 else len(H)}")
print('fmt_cases RESULT', 'PASS' if not fails else f'FAIL {len(fails)}')
_sys.exit(1 if fails else 0)
