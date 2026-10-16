# R_MAND_MAX_TMJ — ANAT 예상문제 개선(PRED) 보고 · MAND·MAX·TMJ (10-15)

- 담당: PRED B(서병무 MAND·MAX — 26 자료 / 박주영 TMJ — 25 자료)
- 따른 것: guide/handoff/PRED26_BRIEF.md 0·2·3·4절 · work/ANAT/pred26/TREND_ANAT.md 5·6·7·9절 · RULES.md 0·9~13절 · guide/과목노트_ANAT.md
- 쓰는 곳: work/ANAT/pred26/pred_MAND_MAX_TMJ.txt(시작 = tools/anat/pred.txt의 MAND 18 · MAX 15 · TMJ 13 블록 그대로 = 46 — 옛 aid는 pred_before.json, MAX 마지막 2개(26 강조 Lymphatics·Figure 7.1)는 pred_before에 없음 → Q 글자를 바꾸지 않고 판정)
- tools/anat/pred.txt는 고치지 않음(메인이 tools/pred_merge.py로 합침)
- 판정 말: 유지(Q·A 그대로 + pr·why·b) · 개선(oid=옛 aid) · 보관(x=1 + why 사유) · 새
- 만드는 법: 시작 사본(46블록)의 Q·A 줄은 스크립트로 그대로 옮기고 머리만 바꿈(유지 31블록 + 보관 6블록 = Q·A 37개 글자 그대로 — 대조 확인) · 개선 블록만 Q/A를 다시 씀 · 새 블록은 강의 끝에 덧붙임. 최종 54블록.
- 화면 글자 규칙: why·Q·A에 내부 문항 id 안 씀("24년 5번" 꼴·연도만) · why 40자 이하 · why의 출제 연도는 b= 문항 배지에 있는 해만(직접 대조 — check_eyears는 pred를 안 읽음).

## MAND — 서병무 Mandible(26 자료 81쪽) · 활성 21 · 보관 1
교수 경향 근거(TREND 5절): 20~24년 18회 = 그림 7 · 단답 6 · 넘버링 5, 객관식·T/F 0 · **탈 강함**(21~24 짤 1/15 — 22·23 악하 A/B만) · 접근법 축이 20·22·23·24 매번(쪽은 매번 다름) · 그림은 해마다 새 그림(p.10·11·47·51·71) · 25년 MAND 복원 0 · 26 `{e:}` p.23 '중요한 가지들' 4신경 · 25 필기 별표는 '예고'로 쓰지 않음(기출 쪽 표시 가능성 — why에 별표를 근거로 쓰지 않음).
- **유지 13**: 하악지 덮개·상방 구조(p.5, 중) · 하악체 내면 5(p.22, 중) · mylohyoid groove vs line(p.14 슬라이드 빨간 상자 두 개, 중) · vestibular 합병증·술식 4(p.35·36, 중) · 악하 접근 marginal mandibular br. 보호(p.53·56·57, **상** — 22·23 짤 축) · 악하 vasoconstrictor만 쓰는 이유(p.54, 중) · sensory buccal n.(p.38, 중) · retromandibular 두 방법·구조·fistula(p.61·68·69, **상** — 접근법 축 목록) · preauricular frontal br. 보호·단점(p.75·77·79, **상** — 접근법 축 + TMJ temporal br. 축) · CNV3 분지 4(26 p.8 필기 — 21년 'V3의 가지' 문구, 중) · 구강저 lingual n.–duct 교차·disc 사고(p.18·19, 중) · mental foramen 위치·무치악·food management(p.20·23, 중) · 7.5 mm·SSO 기준점(p.23, 중).
- **개선 4(oid)**:
  - 폐구근 3과 붙는 곳(`…_87cf79`) — Q 그대로, A만: 'masseter = 바깥쪽' 같은 필기 말뿐이던 부착 부위를 p.22 그림 표지("Attachment of masseter m." · "Coronoid process — Attachment of temporalis m." · medial view "Attachment of medial pterygoid m." · "Attachment of Lateral pterygoid m.")로 근거를 붙이고 21년 개구근 답을 짝으로(중).
  - 26 강조 4신경(`…_929a40`) — '26 수업 필기에서 정리한 신경은?'(필기를 묻는 꼴)을 시험 꼴 "하악 신경 지배(V3)에서 꼭 기억해야 할 중요한 신경 가지 4가지"로 · ⚠ 26 p.8 'CNV3 분지 4'(mylohyoid n.)와 p.23 목록(mental n.) 혼동 함정 덧붙임(**상**).
  - extended vestibular 거리(`…_fd295f`) — '26 필기에서 구치부는 어떻게 하라고 했나'(필기를 묻는 꼴)를 빼고 24년 10-15 mm 문장의 나머지 수치까지 ① 견치 사이 10–15 mm ② 견치 후방 5 mm ③ ramus 쪽 약 5 mm로(p.43·37 — **상**, 24 수치 단답 꼴 + 접근법 축).
  - transfacial 6 + surgical anatomy(`…_8cf655`) — 20년 기출 그대로인 transfacial 6을 빼고 미출제 목록 p.29 Surgical anatomy 4 + 각 문제(p.31~34 필기)로(중).
- **보관 1**: 사랑니 세 신경 주행·따로 마취 이유(U12 축 — 답 전부 필기 · p.23 4신경·p.8 V3·p.12 그림빵과 같은 신경 중복).
- **새 4 = 그림빵 4(전부 중)** — 기출 그림 p.10(23 빈칸)·p.11(22)·p.47(23)·p.51(22·23)·p.71(22)은 다시 내지 않음:
  - p.4 B 내면 7(Lingula · Inferior Alveolar Canal · Pterygoid Tuberosity · Mylohyoid Line · Submandibular Fossa · Sublingual Fovea · Mental Spine) — 24 내면 목록·20 lingula 답을 그림으로(같은 쪽 A 외면은 23 p.10과 겹쳐 안 씀).
  - p.12 6(빨간 상자 3 = Sphenomandibular lig. · Stylomandibular lig. · Pterygoid fovea of neck of mandible + Inferior alveolar n. · Lingual n. · Superficial and deep heads of medial pterygoid m.) — 22년 p.11 답(articular disc·lateral pterygoid heads) 표지는 안 가림.
  - p.21 오른쪽 그림 7(Chorda tympani · Lingual nerve · Facial nerve · Greater superficial petrosal nerve · Mandibular nerve · Maxillary nerve · Opthalmic nerve — 슬라이드 철자 그대로) — 21년 chorda tympani·V3 문항 쪽.
  - p.20 번호 그림 1~5(이름만 가리고 번호는 보이게) — 22년 이공 문항 쪽 · 26 필기 "여기서 눈여겨봐야하는 것!".
- 그림 첨부(f=) 4 = 그림빵 4.
- 우선순위: 상 5(26 강조 1 · 22·23 짤 축 1 · 접근법 축 목록·수치 3) · 중 16 · 하 0. 탈 교수라 '같은 축의 다른 쪽'은 대부분 중으로 둠.
- 답 근거 쪽 확인(쪽 이미지 또는 26 텍스트층): p.4·5·8·10·12·14·16·18·20·21·22·23·28·29·30·35·36·37·38·39·43·44·48·50·53·54·55·56·57·61·63·68·69·71·75·77·79 — 21문항 전부.
- 안 쓴 후보(확인 필요에): p.18 악하선 그림 — 오른쪽 아래 작은 그림이 'Submandibular duct·Superficial part·Deep part'를 그대로 보여 주고 26 필기 상자도 같은 이름을 적어 가려도 답이 보임 → 그림빵 대신 기존 교차·disc 문항 유지 · p.8 세 신경 그림(20년 미복원 그림 — TREND '다른 각도로만').

## MAX — 서병무 Maxilla(26 자료 107쪽) · 활성 16 · 보관 3
교수 경향 근거(TREND 6절): 19~25년 18회 = 단답 8 · 그림 6 · 이유 서술 3 · 넘버링 1, 객관식·T/F 0 · **같은 축 반복**(Le Fort I 혈행 5회 · 5-6 mm 22·23·24 · No valve·CST 19·20·24 · cinch 22·24) · 25년 P12 = p.12 그림 표지 9개 전부 → p.12 그림빵 더 없음 · 26 `{e:}` p.14·18·24·105(p.105는 25년도에도 강조함).
- **유지 12**: 괴사 원인 5(p.97, **상**) · DPA 35.4 mm·medial wall 30/35 mm(p.106·107, **상** — 26 `{e:}` p.105) · Dodson·Bell 혈행 근거(p.98·99, 중) · Venous drainage 5줄(p.13, **상**) · cinch 이유·방법(p.36·37, **상**) · V-Y 방법(p.39, 중 — 23년 이유의 짝) · 상악 접근 3·pitfall(p.23·35, 중) · vestibular 5단계·3-5 mm(p.25·27, 중 — 24·22 'vestibular incision' 워딩과 헷갈릴 수치) · osteology·맞닿는 뼈(p.2, 중) · 5-6 mm + sinus·nasal 근거(p.101~104, **상**) · Le Fort I 술식 순서(p.63~65, 하) · pterygoid plexus·palatine n.(p.22 필기, 하).
- **개선 0**.
- **보관 3**: Le Fort I 역사(p.58 — 출제·강조 근거 없음) · Lymphatics node 6 글 문항 · Figure 7.1 근육 글 문항(둘 다 26 갱신 때 더해진 것 — pred_before에 aid 없음 · 같은 그림을 그림빵으로 옮겨 중복이 되어 보관, Q 글자는 그대로).
- **새 4**:
  - Le Fort I 혈행 이유(**상**) — "끊어지는 두 혈관(nasopalatine·descending palatine) + 괴사하지 않는 이유(ascending palatine branch of the facial artery · anterior branch of the ascending pharyngeal artery — Siebert 1997)" — 26 p.59 필기 '끊어지는 혈관은 크게 두 가지' · 25 필기 p.12 · 26 필기 p.12 '얘네마저 다 끊어지면 괴사'. TREND 6-7 '잘리는/살리는'을 이유 꼴로. b=혈행 3문항.
  - 그림빵 p.14 Lymphatics 6(중 — 26 `{e:}` p.14 · 그림 기출 없음).
  - 그림빵 p.18 Trigeminal Nerve의 V2 쪽 5(Infraorbital Nerve · Posterior/Middle/Anterior Superior Alveolar Nerve(s) · Sphenopalatine Ganglion — 중 · 26 `{e:}` p.18 "상악에서 중요한 가지는 maxillary branch").
  - 그림빵 p.24 Figure 7.1 근육 10 + main muscle of lip movement(중 — 26 `{e:}` p.24). 슬라이드 철자 'aleque' 그대로.
- 그림빵 3 · 그림 첨부 3. 기출 그림 p.12(20·25)·p.6(20·22)·cinch(22·24)는 다시 내지 않음.
- 우선순위: 상 6(혈행 2·5-6 mm·DPA·No valve·cinch) · 중 8 · 하 2.
- 답 근거 쪽 확인: p.2·12·13·14·18·19·23·24·25·27·35·36·39·59·60·97·98·99·100·101·102·103·104·106·107 — 16문항 전부(p.22·63~65는 lec·25 필기 대조).
- 안 쓴 후보: p.19 Maxillary nerve 그림 — 26 필기 상자가 가지 이름(meningeal br.·infraorbital n.·PSA·MSA·ASA·greater/lesser palatine n.)을 순서대로 적어 가려도 답이 보임 → 같은 강조(p.18)의 p.18 그림으로 대신 · p.2 frontal view(표지 대부분이 상악 아닌 구조 — 근거 약함).

## TMJ — 박주영 TMJ·SMAS(25 자료 47쪽 — 26 자료 없음) · 활성 11 · 보관 2
교수 경향 근거(TREND 7절): 20~25년 19회 = 객관식 12 · 빈칸+사진 4 · 서술 1 · 단답 1 · 그림→이름 1 · **완짤**(용어·SMAS 객관식 각 6년 같은 선지 · preauricular 5회 · 25년 = 세 문제 그대로 + temporal branch 변형) · 현 교수 중 객관식을 낸 건 박주영뿐 → 객관식 꼴 유지 · 그림 예고 p.6·7·17(6년 미출제 → 중) · p.16 필기 "다음 중에서 TMJ approach가 아닌 것은?라고 하면 고를 수 있어야".
- **유지 6**: endaural 특징 3(p.18 "!!중요!! 시험!!", **상**) · 상·중·하부 층 순서(p.20~22 — SMAS 객관식 선지 5) 층 축, **상**) · SMAS 풀네임·정의·위치·의미(p.31·32 "풀내임! 시험에 낼 거임 ★★" · QUIZ 4), **상**) · temporal branch 손상 증상 2·Stuzin(p.35 — 25년 신경·가지 문항의 짝, **상**) · triad·감각/운동신경(p.39~41 — QUIZ 2) · STA·STV 빈칸 5회, **상**) · CN7 5 branch(p.33 "외우세요!", 중).
- **개선 5(oid)**:
  - 턱관절 A~G(`…_06f4ed`) → 그림빵 p.7(답 목록 'A)…G)' 뒤 이름만 가림 · 중).
  - TMJ 접근법 5(`…_bcd938`) → 교수 예고 꼴 객관식 "TMJ로의 접근법이 아닌 것은?"(정답 vestibular approach — p.13 필기 "입 안으로 … 절대 볼 수 없습니다" · R도 TMJ 피부절개법 p.16 필기 · 옛 답의 E 최다·I 재건은 해설로 옮김 · 중).
  - 기본 preauricular 3(`…_9c5811`) → 그림빵 p.17 5(Blair's · Thoma's · Dingman's · Popowich & Crane · Posterior Auricular — 'Endaural Incision'은 같은 쪽 필기 상자가 이름을 적어 가리지 않음) + 기본 3 고르기(중).
  - 용어 4 정의 서술(`…_82417b`) → 객관식 "옳지 않은 것은?"(정의 문장 변형 — ③ Ligament가 '근육과 뼈를 연결' ✗ · 6년 선지와 다른 문장, **상**).
  - SMAS 역사·동의어 서술(`…_9812d7`) → 객관식 "옳지 않은 것을 모두"(③ Teisser가 1976년 정의 ✗ · ⑤ 정의가 명확해 논란 없음 ✗ — p.25·31·32 문장, **상**).
- **보관 2**: 개구 hinge/gliding·ADD(답 대부분 필기 · p.8·9 '스킵' · 완짤 교수 미출제 축) · gap arthroplasty(p.42~ "빠르게 진행, 읽어주심" · 출제 근거 없음).
- **새 0** — 객관식·그림빵은 옛 문항을 고쳐서(형식이 교수 경향과 안 맞던 것) 만들어 문항 수를 늘리지 않음.
- 그림빵 2 · 그림 첨부 2. 기출 사진 p.13(Q13)은 다시 내지 않음.
- 우선순위: 상 7(완짤 축 그대로 변형·QUIZ·'시험' 예고) · 중 4.
- 답 근거 쪽 확인: p.6·7·13·15·16·17·18·21·25·27·28·29·30·31·32·33·35·39·40·41(쪽 이미지·텍스트층) — 11문항 전부.
- 안 쓴 후보: p.40·41 triad 그림 — 슬라이드 제목 "Superficial temporal artery and vein (STA, STV)"과 필기 상자가 이름을 적어 가려도 답이 보임 → 그림빵 안 만듦(글 문항 유지).

## 검사
- `.venv/bin/python tools/pred_check.py ANAT --file work/ANAT/pred26/pred_MAND_MAX_TMJ.txt` → **✗ 0 · △ 0** (MAND 활성 21·보관 1·상 5·중 16·그림빵 4 / MAX 활성 16·보관 3·상 6·중 8·하 2·그림빵 3 / TMJ 활성 11·보관 2·상 7·중 4·그림빵 2).
- `.venv/bin/python tools/pred_merge.py ANAT work/ANAT/pred26/pred_MAND_MAX_TMJ.txt --dry` → 블록 104 → 112 · **옛 문항 보존 ✓(46)** (--dry만).
- 새 약어 0(check_abbr 같은 규칙·같은 자료 모음으로 조각 파일을 직접 검사 — STA·STV는 TMJ p.40 슬라이드).
- why 40자 이하 · why/t의 출제 연도 ⊂ b= 문항 배지(직접 대조 — '25 필기'처럼 자료 연도는 출제 연도가 아님).
- 그림빵 9개 모두 `tools/figmask.py ANAT <KEY> <쪽> --mask …` 미리보기(work/_tmp/figmask/ANAT_<KEY>_<쪽>_mask.png)를 Read로 보고 확대 조각까지 확인 — 고른 라벨 다 가림 · 답 = 쪽 이미지에 보이는 글자 그대로(철자 Opthalmic·aleque 포함). tesseract OCR이 이 기계에서 너무 느려(--version만 7초, 앞서 돌린 OCR은 시간 초과로 끊김) `--pick` 대신 쪽 좌표로 `--mask`를 직접 줌 — 섞인 OCR 결과는 쓰지 않음.

## 확인 필요
1. 그림빵 화면: 26 쪽 이미지의 학습부 필기 상자가 일부 낱말을 보여 줌(MAND p.12·21, TMJ p.7 아래 상자) — 위치 짝은 안 드러나 그대로 둠. 쪽마다 '번호 없는 덮개 상자'(답 없이 필기 상자만 가림)가 있으면 MAX p.19·MAND p.18·TMJ p.41도 그림빵으로 쓸 수 있음(메인 판단).
2. TMJ는 26 자료 없음(25 자료 기준) — 26 TMJ 자료·필기가 오면 예고 쪽·QUIZ가 바뀌었는지 다시 봐야 함.
3. TMJ 객관식 2개를 옛 서술 문항에서 바꿈(oid로 기록 이어짐) — 사용자가 서술형 암기용을 따로 원하면 보관본(옛 글)을 되살리는 대신 새 서술 문항을 더할 것.
4. MAX의 보관 2개(Lymphatics·Figure 7.1 글 문항)는 오늘 26 갱신 때 더해진 것이라 사용자 표시가 없을 가능성이 큼 — 메인이 지우는 쪽을 원하면 그때.
5. MAND 상은 '접근법 축의 목록·수치 쪽' 3개(retromandibular·preauricular·거리 수치)로 TREND 5-7을 따랐지만, 탈 교수라 다른 접근법 쪽(p.38·54)도 같은 정도로 나올 수 있음 — 상/중 경계가 근거상 뚜렷하지 않음.

