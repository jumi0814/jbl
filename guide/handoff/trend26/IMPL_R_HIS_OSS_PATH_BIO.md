# IMPL 예상문제 개선(PRED) — HIS · OSS · PATH · BIO 보고

- 담당: PRED(강의 묶음 HIS 조영단 · OSS 한정준 · PATH 명훈 · BIO 임영준) · 브리프 guide/handoff/PRED26_BRIEF.md 0·2·3·4절 · 경향 work/IMPL/pred26/TREND_IMPL.md 2~5·9절
- 쓰는 곳: work/IMPL/pred26/pred_HIS_OSS_PATH_BIO.txt(조각 — tools/impl/pred.txt는 손대지 않음, 메인이 tools/pred_merge.py로 합침)
- 시작(10-15): pred.txt의 HIS 12 · OSS 11 · PATH 12 · BIO 12 = 47블록을 그대로 조각으로 옮김 → `pred_merge --dry` 옛 문항 보존 ✓(47)
- 표기: 유지 = Q·A 글자 그대로 + pr·why·b(t는 필요하면 고침) · 개선 = Q/A 고침 + oid(pred_before aid) · 보관 = x=1 + why(사유) · 새 = 새 블록.
- 형식 기준(TREND 9절): HIS 객관식(5지 옳은 것·4지 모두) + 그림 이름 · OSS 객관식/서술/그림 빈칸 회전 · PATH 객관식 정답 1 · BIO 원문 서술·나열·표 빈칸(객관식 금지). 그림빵 = HIS·OSS 함(기출 그림 p.38·p.23·p.17·p.14 반복 금지) · BIO p.23 한 장 · PATH 안 함.

(강의별 결과는 아래에 강의 하나 끝날 때마다 덧붙임)

## HIS — 조영단(역사·용어·설계·표면) · 활성 16 · 보관 1
- **교수 경향 근거(TREND 2절)**: 24·25 출현 9 중 객관식 8(5지 '옳은 것' 답 1 · 4지 '모두 고르시오' 답 2~3) · 선지 = p.25 External/Internal 표·p.21 One/Two stage 표의 반대 칸, p.22↔23·p.30↔31 짝 쪽 주어 바꾸기, p.35 Type 행 바꾸기 · 25년 4문항 = 완짤 1·변형 3(새 축 0) · 그림 기출 p.38 드릴(23·24)·p.23 two-stage 사진(24·25) → 그림빵 함(기출 그림 반복 금지) · 25 필기 "별표는 p.38 (과거: p.25, 42, 48)" · p.42 "그림보고 이름을 쓸 수 있게 하자".
- **유지 1**: 드릴 사용 순서 배열(pr=중 — 25 필기 p.42 예시 문제 그대로).
- **개선 10(oid — 서술 → 교수 객관식 꼴로, 옛 답 내용은 선지 해설에 모두 남김)**:
  - `…internalconnection과exter_8f6170` → Internal type 옳은 것 모두(25 P11의 반대편 · 감싸는 쪽 필기 + 교합조정) 상
  - `…healingabutment와coverscr_a99b9f` → healing abutment/cover screw 옳은 것 모두(24·25 바꿔치기 축) 상
  - `…onestage와twostage임플란트수술의_02cbe8` → One/Two stage 5지(p.21 표 단점 칸 — 25 P15의 다른 칸) 상
  - `…lekholm과zarb…_403951` → Type 1~4 5지(행 바꾸기) 상
  - `…straightbody와taperedbody_b5ae85` → '임플란트 수술과 관련하여 옳은 것' 5지(24 Q13·25 P14 같은 머리 다섯 주제 · 정답 = straight) 상
  - `…자연치와임플란트의가장큰차이…_db3645` → 가)~라) 옳은 것 모두(Q12 꼴 · p.4 필기 짝 바꾸기) 상
  - `…골유착osseointegration의정의…_c32918` → timeline 옳은 것 모두 중 · `…발전사…_953d57` → 4종 짝 문장 5지 중 · `…치료기간…표면처리sa_39c542` → SA·CA·HA + 단축 짝 모두 중 · `…isq의기준값…_2e7e10` → 해부·ISQ·환자 4축 표 모두 중
- **보관 1**: 수술 키트 역할 서술(`…수술키트implantsurgicalkit에서_25f7c3`) — 답이 필기뿐 · 키트 그림은 새 그림빵 p.42로.
- **새 5(상 4 · 중 1)**: 드릴 A~E 역할 객관식(p.38 — 기출 그림을 다시 쓰지 않고 글 선지로, 상) · 그림빵 4 — p.24 연결 방식 이름·말풍선 4칸(상) · p.42 Lance/Long Pilot/Long Countersink(25 필기 별표, 상) · p.4 자연치 vs 임플란트 섬유·PDL 라벨 5(상) · p.31 Tapered/Straight + 유리한 문장(중).
- **상/중/하**: 상 10 · 중 6 · 하 0. 그림 첨부(f=) 4 = 그림빵 4(객관식은 그림 없이 풀림 → f 없음).
- **그림빵 확인**: 미리보기 work/_tmp/figmask/IMPL_HIS_{4,24,31,42}_mask.png Read — 라벨 전부 가림 · p.31 ②는 옆 26 필기('tapered body가 더 선호됨' — 답 힌트)까지 한 상자 · p.42는 라벨 + 바로 아래 26 필기(=initial drill 등)를 한 상자(④⑤⑥ 동그라미 번호도 가려짐 — 답엔 이름만). OCR(figmask 자동)은 2분 넘게 걸려 중단 → 쪽 이미지 격자 확대로 상자를 직접 잡음(--mask).
- **답 근거 쪽 확인(쪽 이미지 Read)**: p.4·5·6·20·21·22·23·24·25·27·30·31·35·36·38·40·41·42·48·52 + 텍스트층 p.7-10·14-15·33·53 → 17문항 모두 확인.
- **확인 필요**: p.35·38·53 26 PDF 빨간 상자(슬라이드/필기 구분 불가)는 강조 근거로 쓰지 않음 · Type 2·3 '적절'의 근거는 JB 해설("D2, D3 가 가장 적절")·25 필기.

## OSS — 한정준(Osseointegration·bone physiology, 25 자료) · 활성 12 · 보관 2
- **교수 경향 근거(TREND 3절)**: 23·24·25 해마다 같은 3축 × 1문항 — ① 층판골 vs 망상골 객관식(23 R06 → 24 Q15 그림+객관식 → 25 R06 완짤) ② 골유착 3단계(23 서술 → 24 객관식 → 25 서술 세 단계) ③ osteon 그림 빈칸(Q17 3년 완짤) · 함정 = 숫자(99%·1년·3~4개월)·주어(woven↔lamellar)·단계(친화↔전도↔적응) · 그림 기출 p.17·p.14 → 그림빵 함(이 두 그림은 반복 안 함) · 25 학습부 "강의자료에 포함된 텍스트는 모두 공부".
- **유지 6**: 층판골 옳은 것 모두(이미 객관식, 상) · osteon 구성 3 + interstitial lamellae(상) · Haversian vs Volkmann 방향(중) · 골전도기·골적응기 서술(25 서술의 뒤 두 단계, 상) · 연골내 vs 막성(중) · Misch D1~D4(중 — 필기 '쭉 읽어주셨습니다').
- **개선 3(oid — 서술 → 객관식)**: `…wovenbone망상골의특징…_e6e6fe` → 망상골 5지(층판골 문장 주어 바꾸기, 상) · `…spongybone과immaturebone의_5c9f83` → 옳은 것 모두(필기 '잘 구분해야 한다', 중) · `…골막periosteum의기능2가지…_3d84df` → periosteum/endosteum 옳은 것 모두(필기 '두 가지 기능은 중요', 중).
- **보관 2**: osteoblast vs osteoclast 기원(`…osteoblast와osteoclast의기원_073e8a` — 세포 각론, 3축 밖) · rigid fixation vs osseointegration(`…임상용어rigidfixation과…_790789` — 동요도 용어, TREND '하').
- **새 3(상 2 · 중 1)**: 골유착 단계 5지(24 골친화기 객관식의 다른 단계 — 방향·주차·단계 바꾸기, 상) · 그림빵 p.19 spongy/compact bone·Volkmann/Haversian canals(osteon 같은 구조 다른 그림, 상) · 그림빵 p.16 long bone spongy·compact·marrow cavity·periosteum(중 — p.16 오른쪽 osteon 그림은 기출 p.17과 같은 그림이라 가리지 않음).
- **상/중/하**: 상 6 · 중 6 · 하 0 · 그림 첨부 2 = 그림빵 2.
- **그림빵 확인**: work/_tmp/figmask/IMPL_OSS_{19,16}_mask.png Read — 라벨 전부 가림(필기 상자 안 Haversian/Volkmann 설명은 이해 근거라 남김). p.18 조직 사진(O·HC·CL·IL·VC)은 라벨이 약어뿐이고 CL·IL의 풀이가 자료에 없어 뺌.
- **답 근거 쪽 확인(쪽 이미지 Read)**: p.12·13·15·16·17·18·19·20·21·22·23·24·25·26·30 → 활성 12문항 모두 확인.
- **확인 필요**: OSS 26 자료 미수령(26 수업 261013) — 받으면 3축 쪽(p.13·15·17·25-26)이 바뀌었는지 다시 볼 것.

## PATH — 명훈(Implant in pathologic bone, 26 = 23 자료) · 활성 9 · 보관 3
- **교수 경향 근거(TREND 4절)**: IMPL 명훈 기출 = 23 한 해 3문항, 모두 객관식 정답 1(R12 potency 가장 강한 것 · R13 절대 금기 ORN · R14 undersized drilling — R13·R14는 수업 공개 문항) · 24·25 출제 0(26 멘트 "출제조차 하지 않으셨고") · 26 멘트 "23 년도 복원본 참고" · 26 PDF p.1에 공개 문항 2개와 답이 23년도 필기로 남음 · 그림 기출 0 → 그림빵 안 함. **출제 자체가 불확실** — 상은 공개 문항 두 축에만, why에 '이후 출제 없음'을 적음.
- **유지 0**.
- **개선 9(oid — 서술 12개가 모두 교수 형식과 어긋남 → 정답 1개 객관식으로)**: `…골방사선괴사orn…_8b4c4a` → ORN 5지(3 hypo · 절대 금기, 상) · `…lowbonequalityd4opoope에서_d3935b` → low bone quality 5지(undersized · tapping 함정 — 근거 쪽 25 ONJ5 p.36 '26에서 빠짐 · JB 대비', 상) · `…병적골pathologicstate…_f8fb66` → '심어도 성공할 수 있는 것' 4지(R13의 반대 방향, 중) · `…골수염osteomyelitis…_2333ae` 중 · `…bisphosphonate의기능4가지…_017a4f` 중 · `…다음bisphosphonate를relativ_aa68fa` → 약·상품명·potency 연결 5지(26에서 빠짐 · JB 대비, 중) · `…과거에임플란트의contraindication_e5dc1f` 중 · `…우식치주질환파절로…_de33a1` 중 · `…chemotherapyinducedonj증례_ef4891` → '1기만 되어도 손대면 안 됨' 정답(필기 '브론즈 기준 알아야', 중).
- **보관 3**: oral vs IV bisphosphonate(`…oralbisphosphonate복용환자의임_6af4cc` — 25 각론·26에서 빠짐) · Misch 골질 기준(`…misch골밀도분류에서…_e21a3e` — 26에서 빠짐, OSS Misch 표와 겹침) · ONJ 문제점·3H(`…onj의문제점…_233a7e` — 26에서 빠짐, ORN 3 hypo와 겹침).
- **새 0** — OI·Paget·FD 각론은 '심어도 성공할 수 있는 것' 문항과 R13 오답 보기로 대비되고, 출제가 불확실한 강의라 더 늘리지 않음.
- **상/중/하**: 상 2 · 중 7 · 하 0 · 그림 0(그림 없이 풀림).
- **답 근거 쪽 확인**: 26 PDF 쪽 이미지 p.1·35·44·55 + 텍스트층 p.3·9·16·23·34·37·38·39·40·41·53·54 · 25 ONJ5 쪽 이미지 p.14·36·38 → 활성 9문항 모두 확인.
- **확인 필요**: 26 수업 새 강조·시험 예고 없음(@UPD) — 26 출제 여부 자체 불명. R13 공개 문항 보기 1)은 26 p.1 필기에 'cemento ossifying dyslplasia'(JB 'COD(Cemento-Osseous dysplasia)')로 적혀 있음 — 개선 문항 해설엔 필기 표기 그대로.

## BIO — 임영준(진단과 치료계획·biomechanics, 26) · 활성 15 · 보관 1
- **교수 경향 근거(TREND 5절)**: 출현 19 = 서술 10 · 나열·넘버링 5 · 빈칸 3 · T/F 1 · 객관식 0 · 그림 0 · 24·25 = 완짤만(25 완짤 3) · 반복 축 flexure 5회 · 자연치 vs 임플란트 7문장 4회 · 피로실패 4 3회 · PDL 장점 2회(22 T/F → 24 나열) · 26 수업 강조 p.23 "그림을 잘 기억하세요. 어떤 힘이 작용하는지"·p.36 flexure "3번 반복" → 그림빵은 p.23 한 장만, 객관식 꼴은 쓰지 않음.
- **유지 11(Q·A 글자 그대로, 머리에 pr·why만)**: flexure 설계·상악은 묶어도 되는 이유(상 — 26 강조) · PDL 표 오른쪽 열 restorative modification(상) · 과부하 전구증상 vs 무경고 + WHY(상) · 부하 시 비교표 다른 행(중) · offset(중 — JB 해설 '깊게 설명한 건 offset') · AP distance(중) · 무치악 상악 arch form(중) · 모멘트 암 3·정의(중) · 힘의 3유형·crestal(중) · overdenture 움직임 허용(하 — 필기 위주) · biomechanics 정의(하).
- **개선 0** — 기존 문항이 교수 형식(서술·나열)과 맞고 답이 슬라이드·필기와 일치.
- **보관 1**: loads applied + passive fit(`…임플란트에가해지는하중loadsappliedt_d98745` — 근거 약함, passive fit 필기는 새 Richter 문항에 담음).
- **새 4(상 3 · 중 1)**: 그림빵 p.23 B~E 힘 4·모멘트 4(26 강조, 상) · p.25 7문장 빈칸 9칸(4회 축 — 형식만 빈칸, JB 답 오기 ⚠ 병기, 상) · PDL 표 두 열 섞은 T/F 4(22 T/F·24 나열 축, 상) · Richter(1998) absolute axial loading 거의 없음 + 필기 이상적 조건 3(필기 '해당 슬라이드 텍스트 모두 읽으심', 중).
- **상/중/하**: 상 6 · 중 7 · 하 2 · 그림 첨부 1 = 그림빵 1.
- **그림빵 확인**: work/_tmp/figmask/IMPL_BIO_23_mask.png Read — 힘·모멘트 라벨 8개 가림(⑦ Occlusal force는 넓혀 다시 확인) · moment arm 라벨(Occlusal height·Cantilever length)·축 이름은 남김.
- **답 근거 쪽 확인(쪽 이미지 Read)**: p.14·17·23·25·26 + 유지 문항은 원고(쪽 이미지 대조본) 표·필기와 대조 → 활성 15문항.
- **확인 필요**: 피로실패 4(T04 3회)는 기출 그대로가 가장 유력해 변형 문항을 따로 만들지 않음(JB 문항으로 대비).

## 합계 · 검사
- 블록 47 → 59(새 12) · 활성 52 · 보관 7 · 개선(oid) 22 · 유지 18 · 상 24 · 중 26 · 하 2 · 그림빵 7(HIS 4 · OSS 2 · BIO 1) — 그림 첨부는 모두 그림빵(f=).
- `pred_check IMPL --file …` ✗ 0 · △ 0 / `pred_merge … --dry` 블록 82 → 94, 옛 문항 보존 ✓(47) / 새 약어 0(check_abbr 같은 규칙으로 조각 점검 — 처음 'TTFF'가 걸려 '1) T 2) T 3) F 4) F'로 바꿈) / why·t의 'NN년' 표기 없음(연도는 기출 배지에 있는 해만 'NN·NN' 꼴로).
- 맡은 파일 밖 수정 없음(tools/impl/pred.txt·원고·빌드 손대지 않음). 상자 잡기 보조 스크립트·격자 이미지는 scratchpad(IMPL_PRED_A_*)에만.
