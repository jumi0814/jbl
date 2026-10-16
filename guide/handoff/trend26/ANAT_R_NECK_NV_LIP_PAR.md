# ANAT 예상문제 개선(PRED) — NECK · NV · LIP · PAR 보고

- 담당: PRED(강의 묶음 NECK 명훈 · NV 권익재 · LIP 양훈주(26 새 PPT) · PAR 권익재(26 새 PPT)) · 브리프 guide/handoff/PRED26_BRIEF.md 0·2·3·4절 · 경향 work/ANAT/pred26/TREND_ANAT.md 1·2·3·4·8·9절
- 쓰는 곳: work/ANAT/pred26/pred_NECK_NV_LIP_PAR.txt(조각 — tools/anat/pred.txt는 손대지 않음, 메인이 tools/pred_merge.py로 합침)
- 시작(10-15): pred.txt의 NECK 13 · NV 13 · LIP 14 · PAR 18 = 58블록을 그대로 조각으로 옮김 → `pred_merge --dry` 옛 문항 보존 ✓(58) · 58블록 모두 pred_before.json에 aid 있음
- 판정 기준(TREND 요지): 명훈 19~25 출제 0 → 공개 문제 외 상 없음 · 권익재 NV 그림 빈칸 8 · 단답 6(서술·객관식 0), 빨간 상자 = 빈칸 자리 · PAR = 권익재 형식 기준(불확실) + 옛 축 duct·trunk·술식 그림 · LIP = 양훈주 본인 기출(PAR 서술 7·그림 1) 형식 + 옛 축 unilateral·framework·CP 차이 · 이 네 강의에 객관식 새로 늘리지 않음 · JB 칸 교수 ≠ 사이트 연결(T17 서병무 · U09 최진영 · R14 권익재 칸)은 형식 근거로 안 씀
- 표기: 유지 = Q·A 글자 그대로 + pr·why·b(t는 필요하면 고침) · 개선 = Q/A 고침 + oid · 보관 = x=1 + why(사유) · 새 = 새 블록

(강의별 결과는 아래에 강의 하나 끝날 때마다 덧붙임)

---

## NECK — Neck dissection (명훈 · 26 자료 56쪽) — 활성 14 · 보관 1 (상 5 · 중 8 · 하 1)
**교수 경향 근거(TREND 1절)**: 명훈 기출 4문항(17·18년) — 단답·넘버링 3 + 서술·도해 1, 19~25년 출제 0(26판 2025 칸에도 없음). 소재는 슬라이드 표·목록 그대로(M01 p.27 · M02 p.35 · M03 p.56 · M04 p.34·4~6). 26 신호 = p.4~6 공개 시험문제(표·Figure 2 — "이게 시험 문제다", 25년도에도 강조함) · p.15·32·12 강조(25에도). 공개 문제가 25년에도 있었는데 25년 시험에 명훈 문항이 없었으므로 '공개 = 출제'로 단정하지 않음 → **공개 문제 표·그림만 상**, 나머지는 중 이하(과장 금지). 그림빵 = 공개 문제 그림(p.6 Figure 2)만.

| 판정 | 수 | 문항(요지) · pr · 근거 |
|---|---|---|
| 유지 | 11 | IA·IB 경계(상 — 공개 표) · III·IV 경계(상 — 공개 표, M01 같은 축) · VA·VB·VI 경계(상) · landmark 틀·칼선(상 — 공개 문제 '구분하는 구조물 명명') · Crile RND 6(중 — p.15 '외워야 한다'·25 ★) · MRND Type 1·2·3(중 — M02 짝) · ND 4분류 정의(중 — p.32 강조, t '교수 강조'로) · SND 암종별 level·구강암 경계(중 — p.37-38 표) · Extended ND(중 — M04 'RND 미포함 node' 축) · 비림프 3 제거 결과·보존 순서(중 — M03·M02 축) · 예후 인자 6(하 — 필기 별표만) |
| 개선 | 1 | N staging(oid=…clinicalnstagingajccuicc_6de1fe) → **크기 주고 stage 맞추기**(① 2 cm ~ ⑤ 7 cm → N1·N2a·N2b·N2c·N3 + 기준 3·6 cm) — p.12 필기 "크기 주면서 stage 맞추라는 문제를 내기도 한다"(25년도에도 강조함)의 꼴 그대로, 답은 슬라이드 원문(중) |
| 보관 | 1 | incision 8가지 + MacFee(p.44 "외우지 않아도 된다" · 25 필기 "incision 관련 문제는 안 낼 거지만" — 교수가 안 낸다고 한 축) |
| 새 | 2 | ① **그림빵 p.6 Figure 2 — level 구분 구조물 13 표지**(상 — 공개 시험문제 그대로의 꼴) ② **그림빵 p.6 — level 칸 9(IA~VI)**(중 — 25 p.67 필기 출제 예시 "그 level에 포함되는 구조물") |
- 그림 첨부(f=) 2 · 그림빵 2(둘 다 p.6 — 표지 13 / level 칸 9, 서로 다른 것을 가림). 미리보기 확인: /tmp/claude-0/-home-user-jbl/a0af02c5-0dbc-52ee-b82b-13be879fb1dd/scratchpad/ANAT_PRED_A_M_NECK6A_mask.png · /tmp/claude-0/-home-user-jbl/a0af02c5-0dbc-52ee-b82b-13be879fb1dd/scratchpad/ANAT_PRED_A_M_NECK6B_mask.png(같은 쪽이라 work/_tmp/figmask/ANAT_NECK_6_mask.png에는 마지막 것만 남음 · 가린 상자 13·9 모두 라벨 전부 덮음 — 답 = 쪽 이미지 글자 그대로, 'digatsric'은 슬라이드 표기라고 답에 적음).
- 답 근거 쪽 확인(쪽 이미지): p.4·5·6·12·15·35·40 · 텍스트층·OCR: p.13·33·37·38 · 필기 쪽은 lec 원고 대조(p.23·34 · 25 p.2·13·67).
- 확인 필요: 공개 문제가 25년에도 있었으나 25년 시험에 명훈 문항 없음 — 26에도 낼지 근거 없음(그래서 상은 공개 표·그림 5개에만).

---

## NV — 구강악안면 영역의 신경과 혈관 해부학 (권익재 · 26 자료 45쪽 = 25와 같은 슬라이드) — 활성 14 · 보관 1 (상 4 · 중 9 · 하 1)
**교수 경향 근거(TREND 2절)**: 권익재 22~25년 9문항·14회 = 그림 빈칸 8 · 단답 6(서술·객관식·넘버링 0), 짤 강함(24년 2/3 · 25년 3/4). 3회 축 = p.7 Maxillary a. 그림(Q19 22·24·25) · p.19 3 foramen(S08·R11 22·23·25) · 필러 → ophthalmic a.(Q18 23·24·25). **슬라이드 빨간 상자 = 빈칸 자리**(Q19·R11). 26 슬라이드·강조 변화 없음(`{u:}`·`{e:}` 0). → 그림빵 = 아직 빈칸으로 안 나온 빨간 상자(p.9 정맥 4 · p.7 남은 상자) · 기출 그림 그대로(p.7 PSA a.·IA a. 자리 · p.19 3 foramen · p.12 ophthalmic)는 다시 내지 않음 · 객관식·서술 장문 새로 안 냄. T17(서병무 칸)은 b=로만 두고 권익재 형식 근거로 안 씀.

| 판정 | 수 | 문항(요지) · pr · 근거 |
|---|---|---|
| 유지 | 11 | lingual a. 천공 5단계·지혈(상 — R10 23 + U05 20 이종호 같은 p.6) · maxillary a. 분지 짝·sphenopalatine(상 — Q19 3회 축) · 필러 실명 기전(상 — Q18 3회 완짤 축) · ECA 5분지·촉진(중 — R13 1회) · trigeminal 특징 3·V2 구멍(중 — p.18 목록 + p.19 축) · IAN block landmark·needle 4원칙(중 — **b=U11→P04**·t 미출제→짤 변형: 25 '기준 구조물' 단답 축 + 25 필기 "계속 강조") · 임플란트 신경 손상 5·anterior loop(중) · 사랑니 LN vs IAN·Cautions 4(중 — Q20 '하악이었다면' 답) · LN 주행·chorda tympani(중) · V2 가지·infraorbital 담당(중 — p.23 목록·26 필기 "중요한 가지를 보자면") · IAN 특징 3·V3 3가지(하) |
| 개선 | 1 | 정맥 원칙·중요 2 서술(oid=…정맥을공부할때의원칙과…_9203f9) → **임상 상황 → 정맥 이름 단답 2**(brain abscess = cavernous sinus · Le Fort I 출혈 = pterygoid plexus of veins) — 권익재 단답 꼴(R10·Q18)로, 답은 26 필기 p.9 문장 그대로(중) |
| 보관 | 1 | 신경 손상 증례 3 서술(권익재 형식 아님 · 강조·기출 없음 — TREND 하) |
| 새 | 2 | ① **그림빵 p.7 남은 빨간 상자**(sphenopalatine a. ×2 · dental and alveolar branches 3 — Q19 같은 그림, 기출 빈칸 PSA a.·IA a.는 가리지 않음, 상 — 3회 축 변형) ② **그림빵 p.9 Venous Drainage 빨간 상자 4**(cavernous sinus · pterygoid plexus of veins · retromandibular v. · facial v. — 미출제 빨간 상자 + 26 필기 "여기서 중요한 두 가지 구조물" + Summary 정맥, 중) |
- 그림 첨부(f=) 2 · 그림빵 2. p.9는 왼쪽 26 필기 상자에 답(cavernous sinus·pterygopalatine plexus)이 적혀 있어 ⑤로 함께 가림(답 줄 "⑤ (필기 상자 — 가림)"). 미리보기: work/_tmp/figmask/ANAT_NV_9_mask.png · ANAT_NV_7_mask.png — 라벨 모두 덮임 확인.
- p.5 ECA 남은 2분지 그림빵은 기존 ECA 5분지 문항과 같은 축이라 안 만듦 · p.21 V2 가지 그림은 강조 근거 약하고 V2 가지 문항과 겹쳐 안 만듦 · p.31 IAN block 그림은 표지가 약어(CN·PTD·PMF…)뿐이라 자료 밖 풀이가 필요해 안 만듦.
- 답 근거 쪽 확인(쪽 이미지): p.5·6·7·9·12·19·20·21·23·31·32·35 · 텍스트층: p.8·18·26·28·29·33·34.
- 확인 필요: 없음.

---

## LIP — 구순열·구개열 해부학, 비(코) 외과적 해부학 (양훈주 · 26 새 PPT 28쪽 · 옛 기출 최진영·한정준) — 활성 15 · 보관 3 (상 5 · 중 7 · 하 3)
**교수 경향 근거(TREND 4절)**: 형식 = 새 교수 양훈주 본인 기출(PAR 21~23년 8회: 별표 슬라이드 목록 서술 7 · 술식 그림 표지 빈칸 1, 객관식 0, 짤 강함) — 한 강의 8회뿐이라 **불확실**. 내용 축 = 옛 교수 unilateral(18~25 8회) · framework(20·22·24·25) · complete CP vs 정상(22·23·24) · LVP·bilateral·keystone·Kiesselbach(각 2회). 26 신호 = 새 PPT 목록(p.12 일측성 14 · p.13 양측성 9 · p.14 구륜근 · p.24 VP closure 표 · p.27 구개열 5) + `{e:}` p.24 "제일 중요한 근육은 levator veli palatini" · p.28 "용어를 알자! … 정상과 비정상이 어떻게 다른지". 코(framework·keystone·Kiesselbach)는 26 PPT에서 빠짐 → 'JB 대비'로만 하. 25년 객관식(P05·P06)은 한정준 출제라 객관식은 새로 안 냄.

| 판정 | 수 | 문항(요지) · pr · 근거 |
|---|---|---|
| 유지 | 9 | 구륜근 주행 편측 vs 양측(중 — 26 p.14 새 표, S05·P07 축) · LVP 기시·정지·기능·구개열 차이(상 — U07·P08 2회 + p.24 26 강조) · VP closure 주된/이관/옆벽 근육(상 — 26 p.24 새 표 + 26 강조) · tensor vs LVP 비교(중 — **b에 P08**: 25 빈칸 축, 신경은 26에서 빠짐) · internal valve·keystone component(하 — t '26에서 빠짐 · JB 대비') · 발생 6·7주(하 — 26 새 쪽이나 기출·강조 없음) · 26 p.15 그림 치조골·비익연골 변형 3(중) · 입술 올림근 4 origin(하 — T06 축, 26에서 빠짐 · JB 대비) · 26 양측성 코 변형 9(중 — S05·P07 축의 26판) |
| 개선 | 2 | ① 26 일측성 비주·비공 6항목(oid=…26년양훈주교수님자료에서일측성…_dc47bf) → **26 p.12 14항목 전부를 부위별로**(Q02 8회 축의 26판 · 25 답이 10+4=14항목이었던 꼴 그대로 · 25년 객관식 함정 '내측·둔각' 병기, 상) ② Veau's cleft muscle·경구개(oid=…구개열에서veauscleftmuscle이란무_a0a587) → **26 p.27 구개열 5항목 전부 + Veau's cleft muscle**(Q04 3회 축의 26판 · p.28 26 강조 "정상과 비정상 차이", 상) — 둘 다 양훈주 '목록 서술' 꼴 |
| 보관 | 3 | 일측성 Non-cleft side 4(Q02 기출 답 그대로 · 26에서 빠짐) · 코의 층·rhinion(26에서 빠짐 · rhinion은 25 객관식 선지 그대로) · Kiesselbach 3·prolabium 동맥(R02 기출 답 그대로 · 26에서 빠짐) |
| 새 | 4 | ① **그림빵 p.26 정상 vs 구개열 구개 표지 10**(Aponeurosis·Hamulus·Tensor·Levator·Uvulus / Accessory muscle — Q04 3회 축 + p.28 26 강조, 상) ② **그림빵 p.17 구개인두의 근육 7**(S06 축 + "용어를 알자!", 중) ③ **그림빵 p.15 A 정상 비부의 골/연골 9**(framework 4회 축의 다른 그림 · 기출 framework·crus 그림(25 자료)은 다시 안 냄, 중) ④ **그림빵 p.9 입술·코 표면 명칭 11**(U06 인중·입술산 축 + "용어를 알자!", 중) |
- 그림 첨부(f=) 4 · 그림빵 4(전부 26 PPT 그림 — 26에서 빠진 25 그림으로 낸 그림빵 0). 미리보기: work/_tmp/figmask/ANAT_LIP_26/17/15/9_mask.png — 라벨 모두 덮임(p.9 'Philtrum' 첫 글자 비침 → 상자 넓혀 다시 확인).
- p.25(정상 vs 구개열 측면 — 표지 3개 반복)는 p.26과 같은 축이라 안 만듦.
- 답 근거 쪽 확인(쪽 이미지): p.9·12·15·17·25·26·27 · 텍스트층: p.5·6·13·14·18·19·24 · 25 LP5 p.24·26·48.
- 확인 필요: 양훈주가 LIP를 낸 기록 0 — '목록 서술' 우선은 PAR 기출 8회에서 옮긴 추정(불확실).

---

## PAR — Parotid gland and facial nerve (권익재 · 26 새 PPT 29쪽 · 옛 기출 양훈주 21~23·서미현 24·25) — 활성 15 · 보관 8 (상 4 · 중 8 · 하 3)
**교수 경향 근거(TREND 3절)**: 형식 = 새 교수 권익재의 NV 기출(22~25년 14회: 그림 빈칸 8 · 단답 6, 서술·객관식·넘버링 0) 기준 — 이 강의를 권익재가 낸 기록 0이라 **불확실**. 내용 축(옛 교수) = Stensen's duct 4회(21·23·24·25) · trunk landmark 3회(21·22·25) · 술식 그림 3년 연속(23·24·25) · 저작근 기능 3회 완짤(21·22·23 — **26에서 빠짐**) · 이하선 개요 객관식 1회(25). 26 신호 = 새 쪽 21(`{u:}`) + `{e:}` p.13 "이 구조를 반드시 알아야" · "facial nerve는 stylomastoid foramen으로 나온다!" · p.17 "제일 중요한 건 mastoid process다!!" · 술식(p.21~29)은 26 수업에서 영상으로 대체("정확히 알아야 할 필요는 없다"). → 26 해부 그림 표지 빈칸·한 낱말 단답 우선, 26에서 빠진 25 내용은 'JB 대비' 하 또는 보관, 객관식·장문 서술 새로 안 냄.

| 판정 | 수 | 문항(요지) · pr · 근거 |
|---|---|---|
| 유지 | 9 | FN 출구·main trunk 두 division(상 — 26 강조 p.13 ×2) · 26 landmark 7·mastoid(상 — 3회 축 + p.17 26 강조) · 26 duct anatomy p.6 5항목(상 — duct 4회 축 + 26 새 수치) · pes anserinus(중 — R08 술식 그림 축 + 26 p.27 새 문장) · parotidectomy 4종·적응증(중 — 26 p.19-20 새 목록) · 측두지 8-35 mm·0.8 cm(중 — 26 p.11 새 수치) · FN exit 1 cm·digastric(하 — 25 문장, 'JB 대비') · masseter O/I·기능(하 — 저작근 3회 완짤 축, 26 슬라이드 없음 · 'JB 대비') · 타액선 종양 통계(하 — 26 p.18, 기출·강조 없음) |
| 개선 | 1 | border 6방향(oid=…parotidgland의border를6방향으_27d93f) → **26 p.5 이하선 전체 경계(첨부·기저부·전방·후방·내측) + p.4 superficial·deep lobe** 중심으로(25 6방향은 '26에서 빠짐'으로 뒤에 둠 · 25년 객관식 선지 '상부 = zygomatic arch' 축, 중) |
| 보관 | 8 | lobe 비율·lymph·accessory(21 R07 답 그대로 · 26에서 빠짐) · medial·lateral pterygoid 기시·정지(26에서 빠짐 · 기출 축은 '기능'이지 기시·정지가 아님) · 표층 걷은 그림 '5개 이상'(그림 없이 못 풂 · 답 대부분 25 필기 표지 · 복원 불확실) · buccal·marginal mandibular 주행(25 p.15 — 26에서 빠짐 · 기출·강조 없음) · branch 회복과 anastomosis(25 필기만 · 26에서 빠짐) · working in a hole·hemovac(술식 세부 — 26 수업 영상 대체) · buccinator O/I/F(26에서 빠짐 · 기능은 R09 답 그대로) · 두 신경 층 순서(25 p.5 — 26에서 빠짐 · 답 대부분 필기) |
| 새 | 5 | ① **그림빵 p.13 trunk 주변 5**(cartilaginous auditory canal · facial nerve · styloid · mastoid · digastric post. belly — p.13 26 강조 + landmark 3회 축, 상) ② **그림빵 p.12 Horizontal section 6**(26 새 단면 · 25년 객관식 선지 '천층과 심층 사이' 축, 중) ③ **그림빵 p.11 5 branch + upper·lower division**(25 사진 빈칸 두 division 축 · 26 p.12 '상부 3·하부 2' 문장을 답에, 중) ④ **그림빵 p.9 혈관 5**(transverse facial a.·v. · STA·STV 분지 · posterior auricular · retromandibular v. · ECA — 25 RV 빈칸 축 + 26 필기 "massive bleeding에 주의", 중) ⑤ **단답 5칸 — 26 Overview·분비 지배**(serous · glossopharyngeal n. · papilla around upper 2nd molar · parotid-masseteric fascia · facial n.의 분비 gland 3 — 25년 객관식(정답 = 설인 신경) 축, 중) |
- 그림 첨부(f=) 4 · 그림빵 4(전부 26 PPT 해부 그림 — 기출 그림 p.24·25·27 Mayo 그림·25 p.11 사진은 다시 안 냄). p.9는 아래 슬라이드 글·26 필기에 답이 적혀 있어 ⑥으로 한 상자로 가림. 미리보기: work/_tmp/figmask/ANAT_PAR_13/12/11/9_mask.png — 라벨 모두 덮임.
- 보관이 많은 이유: 26 권익재 PPT에 없는 25 서미현(양훈주 판) 슬라이드·필기만 근거인 문항이고, 그 축의 기출 답은 JB 카드에 그대로 있음(각 축의 'JB 대비' 대표 1문항씩은 활성으로 남김 — trunk landmark·저작근).
- 답 근거 쪽 확인(쪽 이미지): p.3·4·5·9·10·11·12·13·17·29 · 텍스트층: p.2·6·10·18·19·20·27 · 25 PAR5 p.6·17.
- 확인 필요: 권익재가 PAR 형식으로 NV와 같은 '그림 빈칸·단답'을 낼지는 다른 강의 근거뿐(불확실) — 옛 축 서술(duct 경로)을 그대로 낼 가능성도 배제 못 함(duct 4회 축은 상으로 둠).

---

## 합계·검사 (10-16)
- 블록 58 → 71: 유지 40(Q·A 그대로, 머리줄 pr·why·b·t만) · 개선 5(oid — NECK 1 · NV 1 · LIP 2 · PAR 1) · 보관 13(x=1 — NECK 1 · NV 1 · LIP 3 · PAR 8) · 새 13(그림빵 12 + 단답 1) → **활성 58**(NECK 14 · NV 14 · LIP 15 · PAR 15) · 상 18 · 중 32 · 하 8.
- 그림빵 12(NECK 2 · NV 2 · LIP 4 · PAR 4) — 모두 26 자료 그림, 기출 빈칸 자리·기출 그림은 다시 안 냄. 상자는 쪽 이미지에서 직접 잡고(동시 실행 OCR이 느려 테두리 미리보기로 맞춤) `tools/figmask.py --mask` 미리보기를 Read로 모두 확인(라벨 전부 덮임 · 답 = 쪽 이미지 글자 그대로). 답이 같은 쪽 글·필기에 적힌 2장(NV p.9 · PAR p.9)은 그 글을 마지막 상자로 함께 가리고 답 줄에 '(가림)'으로 적음.
- `pred_check ANAT --file …` ✗ 0 · △ 0 / `pred_merge --dry` 옛 문항 보존 ✓(58) · 블록 104 → 117 / 새 약어 0(자료·JB 말뭉치 대조 — 남은 'LVP' 1회는 원래 문항 답, 과목노트 '자료에 있어 유지') / why 40자 이내 · why·t의 연도는 모두 그 b 문항 배지에 있는 해.
- 맡은 파일 밖 수정 없음(tools/anat/pred.txt 손대지 않음 · 빌드·커밋 안 함). 작업 스크립트·미리보기 사본은 scratchpad(ANAT_PRED_A_*).
