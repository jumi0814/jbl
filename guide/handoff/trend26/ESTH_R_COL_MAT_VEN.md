# R_COL_MAT_VEN — ESTH 예상문제 개선(PRED26 2절) · COL·MAT·VEN 담당 (10-15)

> 조각 파일: `work/ESTH/pred26/pred_COL_MAT_VEN.txt`(tools/esth/pred.txt의 COL 22 · MAT 15 · VEN 17 = 54블록을 그대로 옮긴 뒤 고침 — pred.txt 직접 수정 없음).
> 근거: `guide/handoff/PRED26_BRIEF.md` · `work/ESTH/pred26/TREND_ESTH.md`(2절 안진수 · 1절 이창하 · 1-7 MAT·VEN 줄 · 2-7 COL) · `work/ESTH/review/questions.md` · `tools/esth/lec_COL·MAT·VEN.txt`(모두 25 자료 — 26 수업 '색(예정)'·'복합레진을 이용한 심미수복 1·2(예정)' 아직 안 열림) · 쪽 이미지 `work/ESTH/lec/`.
> 형식 원칙: COL(안진수) = 단답·서술·그림 그리기(객관식 0 · 끝 3문항) → '쓰시오'형 유지 · MAT·VEN(이창하) = 전부 객관식 5지(25 VEN p.1·33 공지 "전부 객관식! 넘버링, 단답형 등 안나옴") → '쓰시오'·T/F는 5지로 고쳐 쓰기(oid).
> 시작: 54블록 복사 → `pred_merge.py --dry` 옛 문항 보존 ✓(54).

## 결과 요약 (검사)
- `pred_check.py ESTH --file work/ESTH/pred26/pred_COL_MAT_VEN.txt` → **✗ 0 · △ 0** · COL 활성 19/보관 6 · MAT 활성 11/보관 5 · VEN 활성 14/보관 5.
- `pred_merge.py ESTH … --dry` → 블록 118 → 124 · **옛 문항 보존 ✓(54)** (지운 옛 문항 0 — 보관은 x=1).
- 유지·보관 41블록은 Q·A 글자 그대로(원본 복사본과 기계 대조 41/41) · 개선 13(oid) · 새 6.
- 새 약어 0(조각 전체 약어 검사에서 걸린 'TSR'은 유지한 옛 COL 문항 글자 — 슬라이드 p.73·74 "Spectroradiometer ; (TSR)" 쪽 이미지에 있음, OCR 글자층에만 없음).
- 연도: why·t에 쓴 해는 모두 b 문항 배지 안(직접 대조 — 어긋난 1곳(VEN 보관 블록)은 b=P23,T12로 바로잡음).
- 답 근거 쪽 이미지 Read **48쪽**: COL 5·6·8·11·13·17·19·40·47·49·51·59·60·69·70·72·74·81·82·83·84·89·103·105 · MAT 4·6·7·8·9·11·12·16·19·20·23·24 · VEN 3·5·6·7·8·9·10·16·17·18·19·23 (개선·새 문항의 보기·답은 전부 이 쪽들에서 확인. 그대로 둔 옛 문항 중 COL p.45·62·68·92-95·100·104·106 · MAT p.10·13·14는 정리본 원고(쪽 이미지에서 옮긴 것)로만 대조).
- 그림빵 미리보기 4장 Read(work/_tmp/figmask/ESTH_COL_11·17·47_mask.png · ESTH_VEN_23_mask.png) — 라벨 전부 가려짐. 상자는 figmask OCR이 서버 부하로 멈춰 쪽 이미지 격자 확대로 좌표를 재고 `--mask`로 만듦.

## COL — 색 (안진수 · 25 자료 · 26 수업 261016 예정)
- 경향 근거: 안진수 칸 = 해마다 끝 3문항, **객관식 0**(22~25 단답 6·서술 6) · CIELAB 그림 7회·SPD x축 5회 완짤 · 나머지 1문항이 산란 → 3요소 → 반투명도 → 하늘·유백광으로 바뀜 · 필기 p.1 "시험문제 항상 같은 것 냄" → **'쓰시오'형 그대로 유지**(TREND 2절). 교과서 근거 객관식(24·25년 13번·24년 20번·25년 20번)은 교수 불확실이라 형식 근거로 쓰지 않고 b=와 why '교수 불확실'로만.
- **유지 15**(Q·A 그대로, pr·why·b만): 상 6 = SPD x·y축+650 nm(Q28) · CIELAB ±a·±b·C*ab·hab(Q26) · 3요소(R22) · opalescence 정의(P27·S14) · 색차계·조건등색(T20) · 하늘·노을·치아 유백광(S14·P27) / 중 9 = CIELAB vs CIELUV·ΔE · 측색 장비 4·TSR cross-media · 정반사/난반사 · 간상체/추상체(Q13) · binocular·successive(P20) · 형광·인광(P27 같은 표 다른 행) · '제일 헷갈리는 것'·3D master · Munsell · 가시광선 nm(Q13).
- **개선 1**(oid=ESTH:P:opacitytranslucencytrans_aa7127): Opacity·Translucency·Transparency 문항에 24년 27번 축(반투명도에 관여하는 두 요소 = Reflectance · Thickness, p.82 · 나이가 들수록 투명도↓ p.84)을 더함 — 24년 27번이 안진수 칸 자리(TREND 0-2)라 이 강의에도 대비, JB 답 두 교수 병기 그대로 인용.
- **보관 6**(x=1): 흰색 LED SPD(p.8 필기만) · CIE 3요소·표준광원(p.49·51 표시 없음) · Gloss·GU(긴 정의문·표시 없음) · Viewer effects·약물(강조 없음·24년 20번 답 미상) · Color constancy(표시 없음) · 투과도 두 과정·큐브(p.13 필기 위주) — 모두 '하'(근거 약함).
- **새 3 = 그림빵 3**(전부 중 · 기출 그림 CIELAB p.59-60·SPD p.6은 반복하지 않음): p.11 반사 그림(① Specular reflection ② Diffuse reflection ③ Incident light ④ Reflecting surface — 필기 "정반사는 색상이 아님! 중요**") · p.17 추상체 감도 그래프(① S ② M ③ L ④ Relative sensitivity ⑤ Wavelength (nm) — 별표 · SPD 축 문항과 같은 '그래프 축' 꼴) · p.47 Munsell(① Hue circle ② Weak chroma ③ Strong chroma ④ Value — 필기 "꼭 알기!! cielab 시험에 나온다"). TREND 후보 p.70(metamerism)은 필기 상자 4곳이 답(조건등색·Metamerism)을 그대로 보여 줘 빈칸이 성립하지 않아 뺌.
- 활성 19 = 상 6 · 중 13 · 하 0 · 그림 첨부 3(그림빵) · 그림빵 3.
- 확인 필요: 26 COL 자료(261016) 오면 p.쪽·필기 강조 다시 대조 · 24년 27번(반투명도) 출제 교수.

## MAT — 심미수복재료 (이창하 · 25 자료 · 26 '복합레진을 이용한 심미수복 1·2 (예정)')
- 경향 근거: 이창하 = 22~25 복원 64문항 서술·넘버링·빈칸·T/F 0 · 25 공지(VEN p.1·33) "전부 객관식! 넘버링, 단답형 등 안나옴" · MAT 기출 = 표 한 칸 5지(열팽창계수 4회 · 2급 와동 재료 4회 · 3층 순서 4회 · special enamel shade 3회) → 옛 '쓰시오' 15개 중 가치 있는 10개를 **같은 축 5지 객관식**으로 고쳐 씀(표 다른 행·짝 바꾸기·'아닌 것' 뒤집기).
- **개선 10**(oid 전부 pred_before aid): 직접수복재 표 다른 행 ⑤(상, Q15) · 간접수복재 표 Ceramic만 열팽창 O(상, Q15) · GI 필기 '중요!!'(중, Q15) · Applicable Range 잘못 짝(상, Q19) · Special enamel shade 'no alteration of value'(상, Q18) · shade 약자 XL·OA 뒤집기(중, Q18) · 3층 More Opaque = Dentin(상, Q17) · Thickness·saturation ↓ → Translucency ↑ + bulk-fill(중, Q27) · shade wheel A1 → A2D + A1E(중, p.23 'a2를 쓴다는 걸 알아두기') · 재료 선택 흐름도 Compomer 분홍 약점(중, p.6).
- **보관 5**: Patient Factors 6(넘버링형) · Opacity/Translucency 층·bulk-fill(Direct veneer 강의 같은 표 문항과 중복 — bulk-fill은 반투명도 개선 문항 보기 ⑤로) · shade guide 단점·극복(필기 위주) · single-shade(p.17 "등장했다 정도만") · 성질 7·판단 요소 6(넘버링형).
- **새 1**(중): p.16 Composite for dentin vs enamel — Microfilled는 enamel 쪽에만(필기 "덴틴 쪽에 해당하는 게 색상과 관련된 것!") · why '26 자료 대기'.
- 활성 11 = 상 5 · 중 6 · 하 0 · 그림 0 · 그림빵 0(이 강의 이창하 그림 기출 0 — TREND 1-6 '안 함').
- 확인 필요: 26 MAT 자료(261021 예정)가 25와 같은지 · porcelain 5종(24·22년 16번)은 25 자료에 표가 없어 새 문항 안 만듦(JB 카드로 대비).

## VEN — Direct veneer, Indirect composite resin inlay (이창하 · 25 자료 · 26 '복합레진을 이용한 심미수복 1·2 (예정)')
- 경향 근거: 24년 2·25년 4문항 모두 탈(새 자료 슬라이드 목록·비교표 5지) · p.23 필기 "임상과정 : 주의해야 할 것 한두가지!"·"붙이고 나서 광조사 충분히 해줘야 함!!" · 그림 기출은 25년 23번 1문항뿐(VEN:11) → 그림빵 1개만(불확실).
- **유지 10**: 상 6 = inlay 내면 처리 순서(Q23·T23) · 내면 에칭 불가(T23) · dual-cured 광조사(Q25) · DCV 삭제 — 변색 치아(P24 축) · 인레이 금기 상대 금기(P25 축) · 직접 대비 장점 아닌 것(P25 축) / 중 4 = Rationale(p.3) · DCV 장점 아닌 것(p.6-7 함정) · Clinical considerations 7(p.9) · Selection of composite(p.10 '복습'). (4지 객관은 그대로 둠 — 글자를 바꾸면 기록이 끊김.)
- **개선 2**: 치아 쪽 priming·bonding box 코너(서술 → 5지, 중, oid=ESTH:P:치아쪽primingbonding때inlayb_99353d) · Porcelain vs composite T/F(→ 5지, 중, b=P16, oid=ESTH:P:tf1porcelain은enamellikes_8d363d).
- **보관 5**: Masking effect 층 순서 쓰기(25년 23번 그림·축 그대로 반복 · 쓰기형) · 고2 증례 · 10세 미만 외상 증례 · 21번 증례(증례 세부·쓰기형 — 필기 "케이스 몇개 보고 마칠 것") · 전통적 인레이 제작(p.20 필기 세부).
- **새 2**(중): Adhesive Cementation 시멘트 고르기(24년 25번 축 — 보기·해설은 JB 해설의 retentive type 시멘트·임시접착용 그대로) · **그림빵 1** p.23 Clinical Procedures(① Roughening ② Silanization ③ Bonding ④ Etching → Priming → Bonding ⑤ Dual-cured resin cement ⑥ 충분한 광조사! — 기출 그림 VEN:11과 다른 그림, why '그림 기출 1문항뿐·불확실'; 아랫줄 세 라벨은 바로 아래 필기 상자 "치아에도 priming bonding"과 붙어 있어 한 상자로 가림).
- 활성 14 = 상 6 · 중 8 · 하 0 · 그림 첨부 1(그림빵) · 그림빵 1.
- 확인 필요: 26 VEN 자료(261023 예정)·26 '시험 관련 사항' 공지가 나오면 형식(전부 객관식)·그림빵 여부 다시 · 그림빵(빈칸 쓰기)은 객관식 교수에겐 형식이 다름 — 남길지 사용자 판단 · 25년 23번 정답(2)만인지 2)·5)인지).

## 공통 확인 필요 (메인·사용자)
1. 출제 교수 엇갈림(TREND 0-2): 24·25년 13번 · 24년 20번 · 25년 20번(색·교과서 객관) · 24년 27번(반투명도) — 관련 예상은 why에 '교수 불확실'만 적고 형식 근거로 쓰지 않음.
2. 26 COL(261016)·MAT·VEN(261021·261023 '복합레진을 이용한 심미수복 1·2') 자료가 오면 이 조각의 쪽 번호·근거·그림빵을 다시 대조.
3. 그림빵 화면 렌더러는 아직 없음(메인) — m= 상자는 쪽 이미지 대비 %, 순서 = ①②③.
- 수정한 파일: 이 조각 `work/ESTH/pred26/pred_COL_MAT_VEN.txt`와 이 보고만(빌드·커밋·tools/esth/pred.txt 수정 없음).
