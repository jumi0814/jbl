# R_CONS — 예상문제·그림빵 수 보완(PRED_MORE, 10-16) · 임상치과보존학

> 담당: PRED_MORE(CONS). 쓴 파일 = `tools/cons/pred.txt` 하나(기존 블록 글자 수정·삭제 0 — 새 블록은 그 강의 마지막 블록 바로 뒤) + 이 보고. 빌드·커밋 0.
> 기준: `guide/handoff/PRED_MORE_BRIEF.md` · CLAUDE.md 절대 규칙 · RULES.md 11절 · PRED26_BRIEF 2-2~2-4 · `guide/handoff/trend26/TREND_CONS.md` · `work/_tmp/fmt26/CONS.md` · `work/CONS/review/questions.md`·`materials.md` · `tools/cons/lec_*.txt`.
> 요청(메인): INL(6)·ANT(5) 활성이 적음 — 김선영은 예고 쪽 위주지만 26 자료·필기 근거가 있는 고가치 문항을 더 찾기 · ANT는 26 자료가 없어 25 자료 · 예고 밖이라 보관한 문항도 근거를 다시 보고 되살릴 만하면 보고(블록은 안 고침).
> 시작 수(pred_check CONS): WHT 18·그림빵 1 / CRK 19 / DHS 18 / INL 6 / ANT 5 / ADH 18 / FRC 17 — 보관 WHT 1·DHS 1·INL 7·ANT 7·ADH 2·FRC 1.

## 강의별 전 → 후 (pred_check CONS · ✗ 0 · △ 0)
| 강의 | 교수 | 활성 전→후 | 그림빵 전→후 | 새 문항(상/중) | 보관 |
|---|---|---|---|---|---|
| WHT | 이인복 | 18 → 19 | 1 → 2 | 1 (0/1) | 1 그대로 |
| CRK | 서덕규 | 19 → 21 | 0 → 1 | 2 (1/1) | 0 |
| DHS | 서덕규 | 18 → 18 | 0 → 0 | 0 | 1 그대로 |
| **INL** | 김선영 | **6 → 9** | 0 → 1 | 3 (1/2) | 7 그대로 |
| **ANT** | 김선영 | **5 → 8** | 0 → 1 | 3 (0/3) | 7 그대로 |
| ADH | 이창하 | 18 → 20 | 0 → 1 | 2 (0/2) | 2 그대로 |
| FRC | 이창하 | 17 → 18 | 0 → 1 | 1 (0/1) | 1 그대로 |
| 계 | | **101 → 113 (+12)** | **1 → 7 (+6)** | 12 (상 2 · 중 10 · 하 0) | 19 그대로 |

- 기존 블록 글자 수정·삭제·x= 변경 0(`git diff` = 추가 줄만, 39줄) · 새 블록은 각 강의 마지막 블록 바로 뒤 · pred_before 옛 aid 모두 남음(pred_check 전체 모드 ✗ 0).
- 쪽 확인: 7강의 26 자료(ANT는 25) **전 쪽을 접촉 시트(쪽 번호 붙임)로 처음부터 끝까지** 넘김 — INL 105 · ANT 135 · WHT 183 · CRK·DHS 109 · ADH 46 · FRC 84. 새 문항 답 근거 쪽은 쪽 이미지를 다시 확대해 보고(WHT 41 · CRK 54·55·60 · INL 36 · ANT 39·56 · ADH 19 · FRC 44) 글자층 t/·OCR o/로 문장을 대조(CRK 29·34·44·46·48·49·54·55·56·60 · INL 7·25·26·36·76·103·104 + INL5 25·36·104 · ANT 1·39·44·55·56·66·68·70·88·89 · ADH 29·31 · FRC 44 · WHT 41).
- 그림빵 미리보기 확인 **6/6**(`work/_tmp/figmask/CONS_{WHT_41,CRK_60,INL_36,ANT_56,ADH_19,FRC_44}_mask.png` — 라벨 전부 가려짐 · 답이 적힌 26 필기 상자도 덮개 상자로 · 답 = 쪽 이미지 글자 그대로, 오타도 슬라이드 표기대로 'Resevoir'·'Pulp involement'·'Possibley'·'cotact'). 만들었다가 뺀 것 2: INL p.47(라벨이 제목 하나뿐 · 답이 JB 11번 ③과 같음) · CRK p.13(AAE 표 — 기존 활성 4문항이 같은 표).

## INL — 김선영 Inlay vs Fillings (26 PDF · 26 '시험 출제 예고' 도장 p.7·25·36-41·44-48 + p.43 ★)
- 근거: 기출 4/4 예고 쪽 목록 서술 · 25 학습부 "시험은 시험문제 페이지(p.7, 25)에서만" · 26 필기 도장(t/ 검색 — 도장 쪽 = p.7·25·36-41·44-48, p.43 "★ 시험 가능"). 예고 밖은 이번에도 새로 내지 않음.
- **발견: 25년 42번(Q10, 25·23·20 3회)에 걸린 활성 예상 0** — b=Q10 두 블록이 모두 x=1(보관). RULES 11 '최신 해 기출마다 활성 예상 ≥1' 위반이었는데 link_audit가 못 잡음(아래 '확인 필요' 1).
- 새 3:
  1. `짤 변형 · 26 강조` **상** b=Q10 — "'와동이 넓으면 inlay, 좁으면 filling' 기준에 대한 강의 입장 + 결정 고려사항 5 + 상대적 적응증"(p.25 26 필기 "둘 사이에 절대적인 경계는 없다" · 25 필기 "이게 시험문제!" · p.26 · p.76) — 25 필기가 '시험문제'라 적은 발문 꼴 그대로.
  2. `짤 변형 · 26 강조` 중 b=Q09 — p.7 성공 요소 + p.103-104 결론판(Reasonable longevity) 대응 · 26 필기 두 쪽의 공통 메시지(술자·case selection).
  3. `그림빵 · 26 강조` 중 b=Q12 f=INL:36 — 26 예고 p.36 수치 6칸(1.5-2.0 mm occlusal clearance · Otherwise… · 1.0 mm for e.max · No bevel · Width ≥ 1.5 mm · ≥ 1.0 mm for e.max) + 26 필기 덮개. TREND는 INL 그림빵 '안 함'이지만 브리프 2의 '그림 라벨이 곧 암기 대상 + 26 예고 쪽' 조건 — 기존 #42(원리 5가지)·gold vs tooth-colored 비교와 같은 쪽이라 그림은 이것 하나만.
- 보관 7 재검토(블록은 안 고침): 되살릴 만한 것 **없음**. #39(상대적 적응증·접착 p.21·26) → 상대적 적응증은 새 1에 들어감 · #47(수명·reasonable longevity p.87·103-104) → 후반은 새 2에 들어감 · #45(bonding 3요소 p.49 — 26 필기 "가장 critical한 procedure … 중요")가 가장 가까운 후보지만 도장 쪽 아님 → 보관 유지 권장 · #40·#44·#46 예고 밖(26 필기는 일반 설명) · #48 #42와 중복.

## ANT — 김선영 전치부 레진 심미수복 (26 자료 없음 → 25 PDF 135쪽 · 25 예고 p.40-43·65)
- 근거: 기출 2/2 예고 쪽(Q13 p.40-43 4회 · Q66 p.65-66 25년 10점) · 25 학습부 "올해 시험문제 예고 페이지는 p.40-43, 65" · 25 PDF 전 쪽 '시험'·'중요' 검색 + 전 쪽 이미지.
- 새 3(모두 중 — 26 예고를 몰라 상 없음):
  1. `짤 변형` b=Q13 — p.39 "제일 중요한 2가지 1) 모양 2) shade · 모양 70% 색 30%"(예고 p.40 바로 앞 필기 '중요') + shade 3방법 + 결정 뒤(p.44).
  2. `짤 변형` b=Q66 — Direct putty index technique 과정(p.66 필기 · p.88-89 증례 · p.68 explorer) + 스캐너 index 2가지(p.66) — 25년 43번 답 ⑤만 따로 설명하는 꼴(기존 'customized shade tab 설명'이 Q13의 한 방법인 것과 같은 꼴).
  3. `그림빵 · 교수 강조` f=ANT:56 — 'Morphological characteristcs' 사진의 1·2·3 = vertical transitional line angle · gingival embrasure · cotact의 형태 + 필기 상자 5개 덮개 · 필기 "이 3가지 요소가 중요"(p.56)·p.70 "앞에서 언급한 중요한 3가지" · 24 필기 p.55 "56-60pg까지 치아의 중요한 여러 형태". **예고 밖 · 김선영 그림 기출 0 · TREND '안 함'** → 사용자 확인 2.
- 보관 7 재검토: 되살릴 만한 것 **없음(26 예고가 오기 전까지)**. #56(분석 3요소 p.56)은 새 3과 같은 축 — 글 문제로 보고 싶으면 #56 x=1을 벗기고 새 3을 x=1(둘 중 하나만) · #57 slip technique(p.75 필기 "교수님이 애용하고 효과적이라 생각하시는 방식")이 다음 후보 · #52는 25년 43번과 같은 문제(보관 유지) · #55·#58·#59·#61 예고 밖.
- **26 ANT 수업(261013) 자료·예고가 들어오면** 예고 쪽 다시 보고 #57·#56·#59 등 되살리기 · 새 3(그림빵)의 근거도 다시.

## WHT — 이인복 (26 = 25 같은 183장)
- 새 1: `그림빵 · 짤 변형` 중 b=Q02 f=WHT:41 — Inside-Outside bleaching 모식도 라벨 5(Bleaching tray · Resevoir · Gutta percha · Gutta percha seal · Open access) + 표백법 이름 칸 + 26 필기 덮개. TREND '함(제한)' — 기출 그림인 슬라이드 38은 피하고 NVB 술식의 다른 모식도. 26 강조는 없음(why에 '강조 없음').
- 나머지 26 강조(2·16·26·134)·T/F·빈칸·목록 축은 기존 18이 이미 덮음 → 새 글 문제 0.

## CRK — 서덕규 (26 시험 예고 p.66: 검사법 · 분류 5가지 · cracked tooth 특징 2~3)
- 새 2:
  1. `26 강조 · 26 새 내용 · 교수 형식(객관식)` **상** b=Q38 — 검사·보조 장비 '옳지 않은 것'(여러 방향 transillumination p.46 · dye 병용 p.49 · QLF 405nm p.48 · microscope p.55 · VRF diagnostic surgery p.56·34·29) — 예고 1축인데 26 새 쪽 p.41-57 중 기존 문항이 안 쓴 칸(기존: p.29 목록·p.30 plot·CT/X-ray/probing/transillumination).
  2. `그림빵 · 26 강조` 중 b=Q49,Q52,Q36 f=CRK:60 — Clinical Treatment flow 10칸 + 26 필기 덮개. 25년 24번(증례 RCT + Cr)·27번(split 발치)·11번(CEJ 하방 발치) 답이 모두 이 flow. TREND '안 함'(그림 기출 0)이지만 '표 그림 라벨 = 암기 대상' 조건 — 기존 #79(flow·예후 짝 객관식)·#82(분류 5 + 치료)와 같은 내용의 그림판 → 사용자 확인 2.

## DHS — 서덕규
- 새 0 — 26 강조(p.73·87 감별 · p.90 · p.91 · p.95 · p.96-97 SDF · p.100)와 25 37블록 축이 기존 18에 모두 있음. 그림 라벨 슬라이드(p.91)는 25에 수치 객관식으로 나옴 → 그림빵 안 함.

## ADH — 이창하
- 새 2:
  1. `짤 변형` 중 b=Q67 — Self-etch primer pH 4단계(p.29 Strong <1 · Intermediately strong 1-2 · Mild ≈2 · Ultra-mild >2.5) + protocol의 mild primer·rubbing(p.31 + 26 필기 p.29·31) — 목록·수치 미출제(기존 예상에 pH 0).
  2. `그림빵 · 짤 변형 · 26 강조` 중 b=Q15,Q16,Q68 f=ADH:19 — Functional Monomers 표의 약어 칸 6(4-META · MDP · GPDM · HEMA · PENTA · Phenyl-P) + 26 필기 덮개 — 23 full name → 24 숫자 빈칸 → 25 phosphate 2개로 3년 연속 같은 표(기존 2문항은 full name 쪽 · 이번은 반대 방향).

## FRC — 이창하
- 새 1: `그림빵 · 26 강조` 중 b=Q24 f=FRC:44 — Failure Mode 그림 라벨 6(Complete debonding of post/core · Partial · Fracture of Post/Core/Tooth complex / Crack below the bone level · Below the bone level · Root fracture) + 26 필기 덮개 · 26 p.84 키워드 'favorable failure'. 기존 #82(favorable vs unfavorable 글 문제 — 답에 같은 라벨)와 같은 축의 그림판 → 사용자 확인 2.

## 검사
- `tools/pred_check.py CONS` ✗ 0 · △ 0(전체 모드 — 옛 aid 사라짐 0).
- `tools/check_abbr.py CONS` 새 약어 0(걸린 11개는 모두 기존 줄 — pred.txt는 옛 179·380줄 'BACK'·'IEJ'뿐).
- `tools/check_eyears.py CONS` 0건 · 새 why·t의 연도 = b 문항 배지 해만(Q10 25·23·20 · Q13 24·23·21·20 · Q15·Q16·Q68 23·24·25 · Q66 25 · Q02 11회 · CRK 25) — '26'은 26 자료·필기 표기, ANT 둘째 why의 '10점'은 배점.
- 새 블록 문장 = 슬라이드·필기(t/·o/)·JB 원문만 · `{u:}`는 26 새 슬라이드(CRK p.48·55)에만 · `{e:}`는 원고가 `{e:}`로 둔 26 강조·예고(CRK p.66 · INL p.7·25·36·43 · ADH p.19 · FRC p.84)에만 · 빌드·커밋 0(git status = tools/cons/pred.txt만 M).

## 사용자 확인 필요
1. **link_audit 누락(메인)**: Q10(25년 42번)은 활성 예상 0이었는데 △가 안 떴음 — 카드의 첫 `.qtext` 줄이 '2025 년 교수님 강조' 표시라 `weak`(글자 < 12)로 건너뜀(tools/link_audit.py `weak = … len(NORM(qt)) < 12`). Q09·Q11·Q13도 같은 표시 → 다른 과목에도 같은 꼴이 있으면 놓침. 이번 INL 새 1로 Q10 연결은 채움.
2. **TREND '안 함' 강의의 그림빵 4(CRK 60 · ANT 56 · ADH 19 · FRC 44)** — 그 교수 그림 기출 0, 브리프 2의 '그림 라벨 = 암기 대상(표·분류·모식도)' 조건으로 냄. 넷 다 같은 축의 글 문제가 이미 있어(CRK #79·#82 · ANT 보관 #56 · ADH full name 2 · FRC #82) 그림판 성격 — 원하지 않으면 x=1만.
3. 기존 블록에서 본 것(고치지 않음): link_audit △ 5 'b=가 있는데 t=미출제'(WHT #16 · INL #61 · ANT #74 · ADH #88 · FRC #109) — t를 '짤 변형'으로 바꾸거나 b=를 빼는 정리 후보.
4. ANT 26 자료·26 예고 미수령 — 들어오면 ANT 보관 #57·#56·#59와 새 그림빵 근거를 다시.

### 최종 답(5줄)
- CONS 활성 예상 101 → 113(+12 · 상 2 · 중 10 · 하 0) · 그림빵 1 → 7(+6) — 기존 블록 수정·삭제 0, `tools/cons/pred.txt`만 씀.
- INL 6 → 9: 25년 42번(Q10)에 활성 예상이 하나도 없던 구멍을 '넓으면 inlay?' 발문(25 필기 '이게 시험문제!')으로 채움(상) + p.7·결론판 대응 + 26 예고 p.36 수치 그림빵.
- ANT 5 → 8(26 자료 없음 · 25 예고 p.40-43·65 기준): p.39 모양/shade·shade 3방법, Direct putty index 과정(25 10점 답 ⑤), p.56 '3가지 요소' 그림빵 — 보관 14(INL 7·ANT 7)는 되살릴 것 없음(ANT #57 slip은 26 예고가 오면 후보).
- 다른 강의는 빠진 고가치만: CRK 검사 보조장비 객관식(26 예고 '검사법', 상)·치료 flow 그림빵 · WHT inside-outside 모식도 · ADH pH 4단계·monomer 약어 그림빵 · FRC failure mode 그림빵 · DHS 0.
- pred_check ✗0 △0 · 새 약어 0 · 연도 배지 해만 · 그림빵 미리보기 6/6 확인 · 확인 필요: link_audit가 '교수님 강조' 표시 문항을 건너뜀(Q10) · TREND '안 함' 강의 그림빵 4 유지 여부.
