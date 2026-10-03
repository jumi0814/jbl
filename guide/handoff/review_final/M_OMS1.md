# OMS1 맥 확인 결과 (10-03)

대상: `R_OMS1_*.md` 7개 보고서의 '맥에서 확인할 것' 19건. 쪽 이미지(`work/OMS1/lec/L0xi/<쪽>.jpg`)와 JB 원본(`work/jb/OMS1_20xx/<쪽>.jpeg`)을 직접 봤다.
결과: **맞음 13 · 고침 5 · 판단 불가 1**. 빌드·docs 수정·커밋은 하지 않음.

| 보고서 | 항목 | 판정 | 근거(쪽·자료 원문) | 고친 곳(파일:줄 요지) |
|---|---|---|---|---|
| DD1 | 1. Treacher Collins 'Frenceschetti' 철자(p.64) | 맞음 | p.64 슬라이드 원문이 "(Frenceschetti-Zwahlen-Klein syndrome)". 슬라이드 철자 그대로 | — |
| DD1 | 2. Muenke·Saethre-Chotzen 치료 첫 줄(p.55·58) | 고침 | p.55(Muenke) "Craniosynostosis release (6-12 Ms old)" / p.58(Saethre-Chotzen) "Craniofacial synostosis release (6-12 Ms old)". 두 슬라이드 표기가 실제로 다름. 하나로 통일하면 한쪽이 틀리게 되므로 원고는 p.55 표기를 두고 p.58 표기를 덧붙임. annot 427행(p.58 인용)은 원문 그대로라 손대지 않음 | `lec_DD1.txt:378` 줄 끝에 "Saethre-Chotzen 슬라이드(p.58) 표기는 'Craniofacial synostosis release'." 추가 |
| DD1 | 3. Lambdoid vs Positional 뒤통수 행(p.35) | 맞음 | FIG 58-9(Right posterior plagiocephaly) "Contralateral occipital bossing" · FIG 58-10(Right-sided lambdoid synostosis) "Contralateral parietal bossing". 이마·귀·flattening 행도 그림 표지와 일치 | — |
| DD2 | 1. S21-4·S20-3 ⭐의 '그림' | 고침 | JB 24판 원본 14쪽(2021 4번)·15쪽(2020 3번)과 23판 10·12쪽의 같은 문항 모두 그림 없이 글 문제. **S20-4(15쪽 2020 4번)도 그림 없음**: 사이트의 🖼 표시는 `assemble.py:182`가 문제 첫머리의 '사진'(“방사선 사진 종류”)을 그림 문항으로 잘못 잡은 것 | `lec_DD2.txt:52`(S21-4)·`:53`(S20-3)·`:248`(S20-4) "단답/서술 그림" → "단답/서술" |
| DD2 | 2. N 행 "코의 기저부가 되는(연조직)"(p.6) | 맞음 | p.6 필기 상자 하나에 "미간 / 코의 기저부가 되는(연조직)" 두 줄이 G선과 N 사이에 있음. 필기 원문이 여기서 끝남(잘린 게 아님). 원고 그대로 | — |
| DD2 | 3. Tooth mass evaluation 뒷부분(p.50) | 판단 불가 | 쪽 이미지에는 "Tooth mass evaluation; p"까지만 보이고 나머지는 흰 상자로 덮여 있음. PDF를 열어 흰 상자(벡터 사각형)를 빼고 다시 그려 봐도 그 아래에 남은 글자 조각은 "pl … t … d … t"뿐(나머지 글자는 PDF에 없음). 복원할 수 없음. 원고의 '판독 불가' 표현 그대로 둠 | — |
| DD2 | 4. Cervicofacial 수치(p.17) | 맞음 | p.17 슬라이드 "cervicomental angle 100˚, neck-chin length 50 mm" · "4 mm behind SN perpendicular to FH plane". 필기 "~100도 · ~50mm (사람마다 다름)" | — |
| DD3 | 1. Q12·Q44 ⭐의 '그림' | 고침 | JB 25판 원본 5쪽(12번)·14쪽(44번), 24판 13쪽·23판 9쪽(같은 문제 '추가복원된 탈문항') 모두 그림 없는 글 문제 | `lec_DD3.txt:78`(Q12) "서술 그림" → "서술" · `:79`(Q44) "단답 그림" → "단답" |
| DD3 | 2. SN to FH "1년 5개월" vs "PO 1.5Y"(p.21·30) | 맞음 | p.30 필기 원문 "수술 1년 5개월 후 측정값이 바뀐 것을 볼 수 있음"(p.30 표 머리는 Gom Player 창에 가려 안 보임). p.21 측정표 머리 원문은 "PO 1.5Y", SN to FH 11.65. 원고 183행(필기 표현)·184행(p.21 표)이 각각 출처대로라 둘 다 유지 | — |
| DD3 | 3. '3-dimentional'(p.8) | 맞음 | p.8 슬라이드 원문 "Transfer of prescribed 3-dimentional movements of the maxilla…". 슬라이드 철자라 44행·58행·tables 510행 그대로 | — |
| DX | 1. 'Alminum oxide'(p.6) | 맞음 | p.6 재료 목록 원문 "Alminum oxide". 슬라이드 철자 | — |
| DX | 2. p.27 그림 설명 잘림 | 고침 | 오른쪽 아래 설명을 PDF에서 300dpi로 다시 뽑아 봄. ③ "…골소주+두꺼운"에서 끊김(더 읽히지 않음), ④는 "…골소주+얇은 피"까지 읽힘. ①②는 원고대로("두꺼운 치밀골 (" / "얇은 피질골 (" 뒤 괄호 안 잘림) | `lec_DX.txt:280` ④ "얇은 …" → "얇은 피…" |
| EXT | 1. 'Titanum mesh'(p.29) | 맞음 | p.29 표 원문 "Titanum mesh"(형광펜 칠해진 글자). 슬라이드 철자. lec 223·233행, tables 223행, annot 306행, pred 147행 그대로 | — |
| EXT | 2. 'Angiogenecity'(p.22) | 맞음 | p.22 상자 원문 "Angiogenecity". 슬라이드 철자 | — |
| LOAD | 1. "32~40N/cm2" 단위(p.16) | 맞음 | p.16 원문 "식립시의 회전력이 최소한 32~40N/cm²"(2는 위첨자). p.20은 "greater than 35 Ncm". 두 쪽 단위가 슬라이드에서부터 다름. tables 322행 N:의 설명("슬라이드 표기가 다름")도 맞음. 위첨자를 '2'로 적은 것만 차이(고치지 않음) | — |
| LOAD | 2. 'organized lamella bone'(p.22) | 맞음 | p.22 원문 "At 4 months: the bone is still only 60% mineralized, organized lamella bone." 같은 쪽 위 줄은 "mineralized lamellar bone". 슬라이드 철자 그대로 | — |
| REP | 1. 증례 나이 "10세" vs "9~10세"(p.24-25) | 고침 | 슬라이드끼리 다름: p.24 "Male/9" · p.25 "Male, 10yrs". 본문 표기 "9~10세"로 부제·정리표를 맞추고, 본문 줄 끝에 출처 쪽을 붙임 | `lec_REP.txt:300` 부제 "10세" → "9~10세" · `:304` 줄 끝에 "(나이: p.24 'Male/9' · p.25 'Male, 10yrs')" 추가 · `tables.txt:629` "10세 #11" → "9~10세 #11" |
| REP | 2. "재(?)위치에 이식"(p.8) | 맞음 | p.8 슬라이드 원문이 "전위된 매복상악견치나 매복중절치 혹은 소구치를 재(?)위치에 이식"('(?)'까지 슬라이드에 있음). p.10의 "정상위치로 이식"은 다른 문장이고 원고 221행에 따로 있음 | — |
| REP | 3. 7th visit 날짜(p.36) | 맞음 | p.36 원문 "2021.02.04 (21 weeks later) / 7th visit / Resin temporary setting". 앞뒤 날짜(6th 2022.01.25 · final 2022.03.10)로 보면 슬라이드 오타로 보이지만, 원고는 이미 "(슬라이드 표기 2021.02.04)"로 적고 있음 | — |

## 제안 절 메모(자료로 확인한 사실만)
- **DD1 제안1 (J2가 카드16·17에 중복)**: 자료상 FGFR2와 관련 없는 두 증후군은 카드17 범위에 있음. p.56 Saethre-Chotzen "TWIST1 gene mutation", p.62 Carpenter "RAB23"(필기 "FGFR이 아닌 다른 유전자의 변이인 점이 특징"). 카드16 쪽은 모두 FGFR 계열: p.44 Apert "FGFR2 mutations", p.47 Crouzon "FGFR2: 95%"와 "FGFR3 … A391E", p.51 Pfeiffer "FGFR1 and FGFR2". 카드16은 대비용 근거.
- **DD2 제안1 (Q08·Q07·Q40 두 곳)**: 이번에는 자료를 따로 보지 않음. 판단에 쓸 새 사실 없음.
- **DD3 제안1 ('완짤' 태그)**: JB 연도를 어떻게 정의하느냐의 문제라 강의자료로 정할 수 있는 사실이 없음.
- **DX 제안1 (Q30이 DX 골량 카드에도)**: JB 25판 해설에 "한정준 교수님 강의자료를 함께 참고했습니다 … (한정준, p.26)"라고 적혀 있고, 참고란에도 "0922_한정준 … p.26"이 있음. DX p.26 원문은 "초기 1년동안 치조골 흡수가 가장 심함 … 하악: 1년동안 4-5mm". EXT 강의(0929)에는 상악·하악 흡수량 비교가 없음.
- **DX 제안2 (Complete Edentulism 카드 jb=에 Q47 없음)**: 이 카드의 Q47 ⭐ 근거 문장은 DX p.28의 1) 완전 무치악 표 "상악: 골질이 떨어지므로 … 전악에 가능한 많은 임플란트"이고, 골량 카드의 Q47 근거는 p.26 필기 "상악 4형은 좋지 않다는 걸 기억". 두 카드 모두 자료 근거가 있음.
- **EXT 제안1 (증례 카드가 길다)**: 해당 쪽(p.32-48·61-64·72-76) 필기에 '넘어가심'·'생략' 같은 말은 없음. 거의 모든 쪽에 1~4줄짜리 증례 설명 필기가 있음(예: p.40 "1달 정도 지나니까 골이 다 흡수", p.41 "4개월 후 … 5mm 이상 되니까 임플란트 식립"). 필기가 없는 쪽은 p.43·45·47·64·72-75. 원칙 5-11의 '넘어가심 증례'에는 해당하지 않음.
- LOAD·REP: 제안 0건.

## 덧붙임 (이 작업 범위 밖이라 고치지 않음)
- `tools/oms1/assemble.py:182`의 그림 문항 판정 정규식 `그림|사진|도해`가 "방사선 사진 종류"(S20-4)를 그림 문항으로 잡아 사이트에 '🖼 그림 문항' 안내가 뜸. JB 원본에는 그림이 없음. 고치려면 판정에서 '방사선 사진' 같은 경우를 빼야 하는데, 팩 내용이 바뀌므로 사용자 결정 뒤 빌드할 때 함께 처리.

## check_lec·check_eyears 결과
- `.venv/bin/python tools/check_lec.py OMS1` → 7강의 모두 ✓, **✗ 0**(DD1 카드 20 · DD2 18 · DD3 15 · DX 14 · EXT 19 · LOAD 16 · REP 15). 🔑 렌더: 옛 렌더와 글자 다름 0.
- `.venv/bin/python tools/check_eyears.py OMS1` → **배지에 없는 해를 쓴 ⭐ 0건**.
