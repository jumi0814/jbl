# ESTH 예상문제 개선(PRED) — INT · FUN · PLAN · SPE (이창하) 보고

- 담당: PRED(강의 묶음 INT·FUN·PLAN·SPE) · 브리프 guide/handoff/PRED26_BRIEF.md 0·2·3·4절 · 경향 work/ESTH/pred26/TREND_ESTH.md 1절(이창하)
- 쓰는 곳: work/ESTH/pred26/pred_INT_FUN_PLAN_SPE.txt(조각 — tools/esth/pred.txt는 손대지 않음, 메인이 tools/pred_merge.py로 합침)
- 시작(10-15): pred.txt의 FUN 20 · INT 14 · PLAN 14 · SPE 16 = 64블록을 그대로 조각으로 옮김 → `pred_merge --dry` 옛 문항 보존 ✓(64) · `pred_check --loose` ✗0
- 판정 기준(TREND 1-1·1-7 요지): 이창하 22~25년 복원 64문항 = 객관식 5지(단답 3회뿐 · 서술·넘버링·빈칸·T/F 0) · 25 마지막 수업 '시험 관련 사항'(VEN p.1·33) "이창하 교수님 부분 전부 객관식! 넘버링, 단답형 등 안나옴" · 26 FUN p.10 `{e:}` 넘버링으로 내지 않음 · 26 SPE p.21 `{e:}` "큰 원리만 알면 다 이해된다. 하나하나 외우는 건 시험 문제에도 안 나올 거다" · 기출 50% = 슬라이드 목록 줄 그대로/한 낱말·짝·방향 바꾸기 · '모두/전부 ○' 함정 · 그림빵 안 함(네 강의 이창하 그림 기출 0).
- 형식 방침: '쓰시오'·빈칸·O/X·T/F형 옛 문항 → 같은 축이면 객관식 5지('옳은 것/옳지 않은 것/모두 고르시오/잘못 짝지어진 것')로 고쳐 씀(oid) — 선지 = 슬라이드 원문 줄 그대로, 오답 선지 = 슬라이드의 짝·반대·숫자·한 낱말 바꾸기(답에 바꾼 근거) · 축이 겹치거나 근거 약하면 보관(x=1 + why) · 객관식 옛 문항 중 근거 정확한 것은 글자 그대로 유지.
- 표기: 유지 = Q·A 글자 그대로 + pr·why·b(t는 필요하면 고침) · 개선 = Q/A 고침 + oid · 보관 = x=1 + why(사유) · 새 = 새 블록. 보기 번호 = ①~⑤(화면이 보기마다 줄을 바꿈).

(강의별 결과는 아래에 강의 하나 끝날 때마다 덧붙임)

## INT (Introduction · 이창하) — 14 → 활성 5 · 보관 9
- 유지 2: 목표에 들어 있지 않은 것(R04·Q02 축, pr=상) · 아름다움을 이루는 것으로 제시되지 않은 것(Q01·P01 축, pr=상) — 이미 객관식 · 근거 p.4·6·8 정확.
- 개선 3(oid): 세부구성 다섯 가지 쓰기 → '세부구성 모두 고르기'(보기에 목표·재정상태 섞음, 상 · oid …e4f3e2) · 정의 쓰기 → '심미치과학 설명 옳지 않은 것'(정의 '예술적 요소'→'객관적 기준' 한 낱말 바꿈 + p.7 영문 정의·審美 보기, 상 · …641590) · p.4 빈칸 → '(가)(나)(다) 짝 고르기'(personal taste/social norms 뒤바꿈·objective 반대말·p.6 깔때기 섞기, 중 · …f07d01).
- 보관 9(x=1): T/F 세부구성(같은 축 · T/F 꼴) · p.6 세 요소·p.7 영문 정의·審美(개선 문항 보기로 들어감) · Wikipedia 정의(근거 약함) · smile line·problem list·26 필기 본질(필기 사례 · 쓰기 꼴) · 상악 전치부 shape 3(FUN 중절치 형태 문항과 겹침).
- 새 0 · 그림 첨부 0 · 그림빵 0(TREND 1-6 '안 함').
- 경향 근거: Q02(25·24·23·22·21·20) · Q01(24·23·22)/P01(25) · R04(23·22·21·20) — 해마다 시험지 1~4번 객관식 · 답 근거는 p.4·p.8 두 쪽뿐 → 활성 5로 충분(작은 강의).
- 답 근거 쪽 확인(쪽 이미지): INT 4·6·7·8 — 활성 5문항 모두.

## FUN (Fundamentals of esthetic dentistry · 이창하) — 20 → 활성 14 · 보관 7 · 새 1
- 유지 0(20개 모두 '쓰시오'·O/X였음).
- 개선 13(oid): 인접치 모두 고르기(p.3·5 항목 섞기, 상 · …03965c) · zenith 옳지 않은 것(distal→mesial, 상 · …c90fec) · 상악 전치 배열 틀린 것(Class I Coronal↔Apical 짝 바꿈, 상 · …b4b5ff) · black triangle 옳지 않은 것(필기 '무한정 내리면' 반대, 중 · …4358b4) · 폭/높이 비 옳지 않은 것(Lighter>darker 뒤집기, 상 · …696c0f) · Golden proportion 옳지 않은 것('stable reference'는 width/height ratio, 중 · …59cea4) · 중절치·측절치 형태 옳지 않은 것(p.21 ⭐ · Distal outline convex→straight, 상 · …b69a42) · Incisal edge configuration 옳지 않은 것(thick → look young 반대, 상 · …b3a236) · Surface texture 옳은 것 모두(Vertical shorter or wider ✗ · 구조 짝 바꿈 ✗, 상 · …f11fa1) · Color 옳지 않은 것(Middle→Cervical third, 상 · …6999ba) · Lower lipline·Smile symmetry 옳지 않은 것(13·14 섞기, 상 · …4e395d) · Objective criteria에 해당하지 않는 것(Negative space = subjective, 중 · …c12225) · 용어 설명 옳지 않은 것(Transparency 반투명 ✗, 상 · …802703).
- 새 1: 상악 중절치 세 형태 '옳게 짝지어진 것'(Q10 반대 방향 — 상).
- 보관 7: Class I·II 해결법(배열 문항 보기로) · 견치 형태(26 '크게 중요하지는 않다') · 측절치 차이(중절치 형태 문항 보기로) · Gingival health(미출제 · 강조 없음) · Subjective integration(criteria 섞기 문항과 같은 축) · Magne & Belser 묶음(미출제) · Value·Chroma·Hue 한글·순서(Color 문항과 겹침 · 필기).
- 상 11 · 중 3 · 하 0 — 상은 모두 2회↑ 축(Q06 6회·Q10 5회·R03/P03·R07·Q12·R09·S04/R06/P05·Q08·Q11/P11)이나 p.21 ⭐("이것만 기억해도 좋다")의 다른 줄. 중 = 전임 교수 축(T03·T08) · 교과서 근거 1회(P14).
- 그림 첨부 0 · 그림빵 0(TREND '안 함').
- 경향 근거: 22~25 해마다 5~8문항 객관식 — 슬라이드 ✓ 줄을 반대말·짝·수치로 바꾼 '틀린 것/잘못 짝지어진 것'·'모두 고르시오' · FUN p.10 25·26 "넘버링으로 내지 않습니다" → 14 기준 번호 쓰기는 이름·범주 고르기로만.
- 답 근거 쪽 확인: FUN 3·4·5·10·11·12·13·14·15·16·17·18·19·20·21·22·23·25·26·27·28·29·30·31 + COL 80·92 — 활성 14문항 모두(용어 문항의 COL p.89 정의는 lec_COL 원고로만 확인).

## PLAN (심미수복에서의 진단 및 치료계획 · 이창하) — 14 → 활성 8 · 보관 6
- 유지 1: diagnostic wax-up·orthodontic setup이 속한 단계(R20 축, 상 — 9단계 도표 ↔ p.24 차트 함정 해설 정확).
- 개선 7(oid): Initial therapy에 해당하지 않는 것(Preventive modality = Diagnostic phase, 중 · …a7b4e6) · Restorative phase에 해당하지 않는 것(Tooth preparation ↔ Finishing preparation, 중 · …789388) · 진단 과정의 목적 모두 고르기(p.23 ★ · 답 전부 ○, 상 · …caab22) · 심미 추가 Present illness가 아닌 것(Pulp vitality test = 일반 항목, 중 · …e47672) · Initial Patient Management 단계·내용 짝(Informed consent = Final phase, 중 · …add607) · Diagnostic stage 옳지 않은 것(Short-term→Long-term provisionals, 중 · …cd2e44) · 54세 남성 증례 옵션 장단점 짝(옵션 2·3 단점 바꿈, 하 · …7a5c9a).
- 보관 6: wax-up 용도·Mock-up technique(진단 단계 객관식 보기로) · 18세 여성 증례(21년 기출 JB 답 없음 · 서술) · forced eruption(필기만) · 23세 여성 증례(20·18 서술은 전임 교수 꼴) · Systemic Patient Management(p.3 개요 · 강조 없음).
- 상 2 · 중 5 · 하 1 — TREND '근거 1축이라 상은 2~3개만' 그대로(R20 25·23 + p.23 ★). 증례 문항은 하로 두고 활성 1개만(22~25 증례 기출 0).
- 그림 첨부 0 · 그림빵 0(도표는 글 보기로만 나옴).
- 경향 근거: R20(25·23) = p.8 9단계 도표 칸 고르기 객관식, 25 보기는 p.24 차트 5단계 이름 · 서덕규 서술(T16·U02)은 형식 근거로 쓰지 않음(내용 축만).
- 답 근거 쪽 확인: PLAN 3·4·6·7·8·11·12·13·14·15·17·18·19·20·23·24·25·26·27·28 — 활성 8문항 모두.

## SPE (Special Effects · 이창하) — 16 → 활성 7 · 보관 9
- 유지 2: 환영 옳은 것 모두 고르기(R19 축 — staining 짝, 자료 기준 판정, 상) · 환영 옳지 않은 것(Q21 꼴 — CEJ·길이 보기, 중).
- 개선 5(oid): Narrower space Shaping 옳지 않은 것(Rounded incisal edge는 Wider, 중 · …c96e68) · S12 변형 '환영 옳지 않은 것'(견치 labial ridge distally → 좁아 보임 ✗ · 발육구 closer together ○ 등 같은 보기 묶음 방향 바꾸기, 상 · …6ce7ff) · 길이 조절 원리 옳지 않은 것(26 p.21 `{e:}` '큰 원리' + p.20·21 필기 'Shorter ≈ Wider 수정·Longer ≈ Narrower 수정', 상 · …ee7d9f) · Principle of Illusion 옳지 않은 것(Combination of lines = edge line, 중 · …2a756a) · 환영과 치료 단계 옳지 않은 것(p.7 필기 '진단단계에 다 끝내야 함!! 기억할것' · 26 필기 '진단·치료계획·상담이 핵심', 중 · …b1b5e6).
- 보관 9: 견치 방향 쓰기·Shaping and Contouring 4(S12 변형 보기로) · Longer teeth 기법 쓰기(길이 원리 문항과 같은 축 · 26 p.21 "하나하나 외우는 건 시험 문제에도 안 나올 거다") · Lombardi('참고만') · Staining 목적·기법(세부 목록) · Surface Characterization(미출제) · 가장 많이 조정하는 부위·'기억해둬야 할것들'(필기만) · 심미 수복 6요소·환영 정의(필기 정의뿐).
- 상 3 · 중 4 · 하 0 — 시험엔 해마다 1문항(환영 옳지 않은 것)이라 상은 S12 변형·R19·26 강조 원리 셋만.
- 그림 첨부 0 · 그림빵 0.
- 경향 근거: S12(25·22) · R19(23) · Q21(24) = 22~25 4년 연속 '환영 옳지 않은 것' 객관식, 보기 = p.11 staining 필기·p.13-19 Wider/Narrower·FUN p.26 · 서덕규 서술(T15 18·20·21)은 객관식으로만 · 26 p.13 필기 "2가지씩 대비 되는 효과라 큰 법칙만 알고 있으면" · p.21 `{e:}`.
- 답 근거 쪽 확인: SPE(26 E11i) 5·6·7·11·13·14·15·16·18·19·20·21 — 활성 7문항 모두.

## 검사(10-16)
- `pred_check ESTH --file …pred_INT_FUN_PLAN_SPE.txt` ✗ 0 · △ 0 (FUN 활성 14·보관 7 / INT 5·9 / PLAN 8·6 / SPE 7·9)
- `pred_merge ESTH … --dry` 블록 118 → 119 · 옛 문항 보존 ✓(64) — 보관·유지 36블록 Q·A 글자 그대로(대조 72줄 일치)
- 새 약어 0(check_abbr 같은 규칙으로 조각 점검) · why·t·A에 쓴 해 = b= 문항의 배지 해 안(26은 '26 필기' 표기뿐)
- 보기 번호 ①~⑤(화면 줄바꿈) · 답 = 정답 + 선지마다 판정·근거 쪽 · 바꾼 선지는 '(…를 …로 바꿈)'으로 근거 · 필기 조각 `{n:}`.

## 확인 필요(메인·사용자)
1. build4의 ESTH 예상문제 파서가 새 머리 필드(pr·why·oid·x)와 쉼표 b=(최대 3)를 읽는지 — 지금 build4는 b를 문항 하나로 찾음(메인 담당).
2. 26 '시험 관련 사항'(26 마지막 수업 261023 예정)이 25처럼 "전부 객관식"이 아니면 형식 판정 다시 — 지금은 25 공지 + 25년 시험(이창하 칸 21/21 객관) 기준.
3. 23년 환영 문항(R19) JB 답은 자료와 어긋남 — 예상 답은 모두 자료 기준(밝게 → 커 보임 ○)으로 씀.
4. black triangle·용어 문항 일부 보기는 필기·색 강의(안진수) 정의가 근거 — 이창하 슬라이드 원문만으로는 판정이 안 되는 보기임을 답에 적어 둠.
