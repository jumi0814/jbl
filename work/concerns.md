
## ANAT/LIP — needs_human · 확인 72 · 수정 7
- Year lists in Korean subtitles: 7 card subtitles still carry exam years, e.g. '(24·23·22·21·20·19·18)' and '(24·22·20·23)'. The review rule says Korean subtitles should not list years, but the card's saved-highlight key is built from the English title plus Korean subtitle (build4.py card_aid/slug), and the index fallback (data-alt) no longer lines up because the lecture went from 10 to 18 cards. Renaming would detach the user's saved highlights and blanks on those cards, so I kept the titles; the user should decide. Other ANAT, GERI and PHARM lectures also still have years in their subtitles.
- Where levator veli palatini sits relative to the hamulus, the 26 p.17 note ('it hangs over the hamulus') and the 25 p.24 note ('it does not hang on the hamulus') contradict each other. The draft keeps a ⚠ line and follows the slides (tensor veli palatini goes around the hamulus). The user may want to check with the lecture recording.
- Q02: the header of questions.md shows '출제 24,23,22,21,18' but also '7회 출제' and a year note that adds 19 and 18 to the JB bracket (24,23,22,21,20). The draft uses 24·23·22·21·20·19·18, which matches the yrs= value in annot.txt; the header line looks abbreviated. Worth confirming after the build.
- S07 (angle between the FH plane and the occlusal plane) has no source in either lecture file. It stays as v=na with the JB answer unchanged. Its ⭐ exam point sits in the Nose Surface Landmarks card only because there is nowhere else to attach it.
- In annot_LIP.txt the v= verdicts and lec= links changed from the existing annot.txt: R14 ok→part, U06 ok→part, Q04 lec LIP:27→LP5:29, R14 lec NV:8→LP5:54. I judged the changes reasonable because the slides do not contain 'main' or 'nasolabial fold/commissure', and the JB answer for Q04 is on p.29. yrs=, yrsnote=, rel= and pair= are the same as before.

## ANAT/MAND — pass · 확인 74 · 수정 9
- Parotid duct 개구 위치가 필기끼리 다름. p.9·10은 '상악 제1·2 대구치 협측', p.7은 '하악의 제1,2 대구치 사이 buccal(caruncle)', p.5는 '제2대구치 협부'. 원고는 p.10을 따라 상악으로 적었으니 사용자 확인이 필요함.
- p.13 필기 원문은 'inferior anterior artery'인데 원고는 'inferior alveolar a.'로 적혀 있음. 받아 적을 때 생긴 오타로 보여 그대로 두었음.
- p.39 텍스트층에 '2-3 mm 정도로'라는 이전 해 필기가 있지만 2025 필기에 가려져 이미지에서는 보이지 않음. 그래서 원고에 넣지 않았음.
- 다른 강의에 연결된 문항 U09(PAR)·Q13·T13(TMJ)도 이 강의 카드에 E: 줄로 참고용으로 들어가 있음. 연도는 questions.md와 같음.
- T23: 문제 문구는 'V3의 가지'인데 JB 답은 삼차신경 3분지임. S03은 JB 스스로 '그림 추측'이라 적었고 박주영 Q13 복원일 가능성도 있음. 두 문항 모두 E:·annot에 경고로 남겨 두었음.
- 빌드(build4.py)는 지시대로 실행하지 않았음. 화면 렌더링 확인은 빌드 후에 필요함.

## ANAT/MAX — pass · 확인 68 · 수정 11
- U13의 판정이 기존 tools/anat/annot.txt(v=part)와 달리 파트에서 v=ok로 바뀜. 답 4개가 모두 p.6 medial view 그림의 명칭이라 ok로 둘 근거는 있지만, 실제 출제 그림은 JB도 '그림 예상'이고 문제에는 '측면그림'이라고 되어 있음. part로 되돌릴지 사용자가 정해야 함(yrs·rel 등 나머지 값은 기존과 같음)
- T17(foramen rotundum)은 JB에서는 서병무 17번이지만 사이트에서는 권익재 NV 강의에 연결된 문항. MAX V2 카드에도 jb=T17과 E: T17이 있고, ! 출제 경향의 '21년 탈 4'에 포함됨. 두 강의에 동시에 연결해도 되는지 빌드 로그에서 확인 필요
- p.12 필기 마지막 줄 'ascending pharyngeal a.는 facial a.의 또 다른 가지'는 같은 쪽의 앞 문장('external carotid a.에서 바로')과 모순됨. 원고는 슬라이드 p.102(Siebert)와 앞 문장을 따랐고, 대조 주석의 N:에 이 내용을 적어 둠
- T14 JB 답의 vomer와 cranial/facial 분류는 자료에 없음(필기에는 'septal bone'). sphenoid는 필기에 있지만 JB 답에는 없음. 원고와 대조 주석에 ⚠·v=part로 표시해 둠

## ANAT/NECK — pass · 확인 64 · 수정 12
- The 26 public exam question (p.4) is marked as ==형광==, but it is a question announced for the upcoming exam, not a past JB sentence. Please decide whether that counts as 'a sentence that appeared on the exam'.
- The MRND-1 row ('제거: 나머지 SCM·IJV') in the lec card and the SAN·IJV·SCM table is inferred. The slide says only 'accessory nerve 보존'; the inference rests on the 25 p.67 notes ('2개 없앨거냐, 1개만…').
- The F:8 caption ('구강에서 아래로 흘러내리는 전이 방향') interprets red arrows drawn on the slide. There is no written note on p.8; the concept comes from the 25 p.7 notes.
- The header claims the complications section (p.53–56) was not covered in the 26 lecture. That is inferred from the p.52 note '(여기까지 끝!)'. It still needs studying because M03 (18) asks about it.
- M03 lec pointer changed from NECK:40 (existing annot.txt) to NECK:56 (the shoulder syndrome slide). There are no yrs/rel/pair fields to compare, but this is a change from the existing value.

## ANAT/NV — pass · 확인 64 · 수정 11
- annot_NV의 T01 판정이 tools/anat/annot.txt 기존 값 v=ok에서 v=part로 바뀌었음(작업자가 바꿈). JB 답 8개 중 ascending pharyngeal a.가 권익재 자료에 없어서 part가 맞다고 봄. yrs=·rel=·pair=는 기존과 같고 R11 lec=는 NV:18에서 NV:19로 바뀌었음
- p.27 26 필기에는 'IAN이 mental foramen으로 들어가기 직전 mylohyoid branch', 25 필기에는 'mandibular foramen'으로 되어 있음. 원고는 그냥 'foramen'이라고만 적었으니 필요하면 사용자가 정리해야 함
- p.13 필기 '근육과 코를 알아야 안전한 보톡스'는 텍스트층 글자 그대로 옮김(OCR은 깨짐). 혹시 '혈관'을 잘못 적은 건지는 원본을 보고 판단해야 함
- Q20은 복원 문제가 '상악'인지 '하악'인지 불분명함(JB도 답을 두 가지 다 적음). R12도 복원이 불완전함(Foramen(?)·Maxillary artery). 두 문항 모두 E:와 annot에 ⚠로 표시해 둠
- T17은 JB 원본에 2021 칸 '서병무 17번'으로 실려 있는데 권익재 문항으로 분류되어 있음. 출제 경향 연도 범위(21~24)는 이 분류를 따름
- p.34 그래프(A~E 중 2nd premolar 63%)는 슬라이드에 'mental foramen 위치'라는 설명이 없어서, Mental foramen 슬라이드 안의 그래프로 해석해 적은 것임

## ANAT/PAR — pass · 확인 56 · 수정 7
- 국문 부제에 연도가 남은 카드 제목 4개: '이하선의 경계·엽·도관 (24·23·21년)', '저작근 4 — 기시·정지·기능 (23·22·21년 + 20년)', 'main trunk 찾는 4 landmark (22·21년)', '이하선 절제술 순서 (24·23년 그림)'. 정리본 원칙 체크리스트('국문 부제에 연도 나열 없음') 위반이다. 작업자는 사용자 형광펜을 지키려고 그대로 뒀다(카드 aid가 영문|국문 제목의 해시라, 고치면 해당 카드의 형광펜·빈칸·'이해함' 표시가 사라짐). 특히 저작근 카드의 '+ 20년'은 U09가 pterygoid 카드로 옮겨진 뒤라 이제 이 카드의 jb=와 맞지 않는다. 제목을 고칠지는 사용자가 정해야 한다
- U09 대조 판정이 기존 annot.txt의 v=ok에서 parts의 v=part로 바뀜. JB 답 '하악지: medial pterygoid'와 슬라이드 'Medial angle of the mandible'이 다르고, JB 해설도 '정확히는 angle'이라고 한다. 근거가 있다고 보고 유지했다. yrs·rel·pair 값은 기존과 같다
- Q17(24년 탈 그림)은 JB 스스로 복원이 불명확하다고 적었다. 정리본·주석은 p.20 기준 JB 답을 따르고, p.27 그림일 가능성은 '확인 안 됨'으로 표시해 뒀다. 실제 출제 그림은 사용자가 JB 원본으로 확인해야 한다
- 머리말의 '앞부분(gland·근육·facial n.)이 핵심'에서 괄호 안 풀이는 p.35 필기 '앞부분'을 작업자가 해석한 것이다(자료에 적힌 말은 아님)

## ANAT/TMJ — pass · 확인 96 · 수정 12
- Skin Incisions·SMAS 두 카드의 국문 부제를 바꿔서 카드 aid(slug)가 바뀜. 사용자가 이 두 카드에 해 둔 형광펜·빈칸·'이해함' 표시는 새 빌드 뒤 복원되지 않을 수 있음(카드 본문이 전면 재작성돼 텍스트 기반 복원도 이미 어려운 상태). 제목을 되돌릴지 사용자 확인 필요
- p.7 텍스트층에 이미지에는 보이지 않는 두 번째 A~G 목록('B. External ear canal' 등, 슬라이드 답과 다름)이 숨어 있음. 원고는 이미지의 슬라이드 답(B = joint capsule)을 따름
- p.37 필기의 거리 표기가 '1.7cm(7mm)'와 '0.7cm(7mm)'로 섞여 있음. 원고는 두 표기를 그대로 적었고, 어느 쪽이 맞는지는 원본 필기로 확인 필요(교수님이 '알 필요 없음'이라고 한 쪽이라 비중은 낮음)
- Q15 20년 선지 3) '근육과 피부 연결'의 정오는 JB 학습부 스스로 논란이라고 적어 둠. 정리본·주석은 두 해석을 함께 제시함
- U23·U24(김성민 전임)는 김성민 PPT가 없어 v=part로 둠. '턱관절 내시경'이라는 술식은 박주영 자료에 없음
- 빌드(build4.py)와 merge_parts 병합은 지시대로 실행하지 않음. 빌드 후 JB 카드의 📖 정리본 칩 제목이 새 부제로 바뀌는지 확인 필요

## CONS/ADH — pass · 확인 62 · 수정 8
- p.20 application mode 표의 필기 배치는 제 해석입니다. '많이 사용하지는 않음·특수한 경우에만 사용·결합력이 잘 안나와서'는 빨간 필기가 2-step etch and rinse 줄 높이에 있어서 그 줄에 붙였습니다. 사용자가 이 배치를 확인해 주면 좋겠습니다
- FRC p.1 학습부 필기 '시험은 저번 시간, 이번 시간 강의에서 2~3문제'의 '저번 시간'을 Dental adhesive(251014)로 해석했습니다. 강의 날짜로 추정한 것입니다
- p.42 필기 '얘도 앞서 얘기한 내용'을 p.39 'Simple-step adhesive – water permeability'와 연결한 것은 원고 작성자의 해석입니다
- check_lec 경고로 빠진 쪽 1-2·46이 남아 있습니다. 표지·목차·Q&A라서 정상입니다

## CONS/ANT — pass · 확인 52 · 수정 9
- p.40 노란 메모와 p.65·p.83의 빨간 글씨 필기가 몇 년도 필기인지 쪽 이미지로는 알 수 없음. 예전 텍스트본 annot에는 '25 필기'로 적혀 있었는데, 이번엔 '연도 미표기'로 바꿈. 사용자가 원본 필기 연도를 알면 확인이 필요함.
- p.83 enamel shade 두께가 필기마다 다름: 초록 상자(25 학습부 양식)는 '1/3', 빨간 필기는 '2/3'. 원고에는 ⚠로 둘 다 적어 둠. 어느 쪽이 맞는지는 교수님 설명으로 확인해야 함.
- JB Q13 답의 'yellowish·whitish·dark'·'opacity'라는 단어는 강의자료에 글자로는 없음(annot N에 적어 둠). JB 답 문장은 바꾸지 않음.

## CONS/CRK — pass · 확인 64 · 수정 9
- Q07 years: the manuscript and annot use the full JB bracket (23,22,21,20,19,18,17,16,14,13 — 10 times). The questions.md header and qids.json list only 23,22,21,20,13, but that is because tools/dump_review.py reads the shortened badge '2023 · 2022 · 2021 · 2020 … 2013'. All 10 years are in the JB bracket, so nothing was added. Please confirm that 10 is the intended count
- The Five Categories card subtitle '5가지 분류 (매년 출제)' was left unchanged on purpose. Changing it would change the card's saved-marks key (build4 card_aid is built from the English and Korean titles), and the user's highlights on that card would be lost. '매년' is loose, since 15 and 24 are missing. If you want it accurate, change it to '(10회 출제)' and accept that marks on that card will reset
- VRF direction may be a multiple-choice trap. The professor (25 notes, 26 p.34) and both Summary tables say VRF runs mainly B-L. But the 26 p.27 Table 3 counts VRF as M-D 8, B-L 4, both 2. The manuscript follows the professor's statement, so the numbers may need a check if a question asks for them
- The 26 text-layer summary boxes sometimes seem shifted by a page from the slide they sit on (for example p.52/53). Captions were checked against the slide images, but the few note sentences taken from those boxes are cited by the box's page

## CONS/DHS — pass · 확인 64 · 수정 9
- Q08 years: the questions.md header and qids.json say '출제 24,23,22,21,17'. This is an artifact of tools/dump_review.py. It parses the compressed badge text '2024 · 2023 · 2022 · 2021 … 2017', so the '…' drops 20 and 18. The JB bracket (24,23,22,21,20,18,17), the badge count '7회' and the current docs pack (yrs [24,23,22,21,20,18,17]) all give 7 years. The manuscript, annot and tables keep all 7. Other questions with elided badges will have the same header problem in questions.md (e.g. Q02, Q04, Q07). Please confirm.
- The Hydrodynamic card's Korean subtitle says '(매년 출제)', but the JB years are not every year (2019 is missing). I left it because card titles are the keys for saved highlights. If you want it changed to something like '7회 출제', saved highlights on that card may need migrating.
- tables_DHS rows about SDF ('침전물로 tubule 폐쇄') and the Desensitizers text rely on 25 notes that exist only inside the page image (DH5 p.22 black box). I confirmed them in the image, but they are not in the t/ text layer, so text-only checks will not find them.
- The 26 'notes' (t/ text layer, red boxes) read like summary notes rather than verbatim professor remarks. They are cited as '26 필기' throughout, consistent with the other CONS lectures.

## CONS/FRC — pass · 확인 78 · 수정 6
- questions.md 머리줄에는 Q26 '출제 21,20,19,18,13', Q28 '출제 20,16,15,14,11'로 적혀 있다. 이는 화면 연도 배지가 '2021 · 2020 · 2019 · 2018 … 2013'처럼 가운데를 '…'로 줄인 것을 덤프한 값이다. JB 괄호와 배지 횟수(8회·7회)로 보면 실제 출제연도는 21,20,19,18,17,15,14,13과 20,16,15,14,13,12,11이다. 원고 E:와 annot N:은 괄호 전체 연도를 쓰고 있어 정확하다고 보고 그대로 두었다. dump_review.py가 연도를 줄여 출력하는지 확인이 필요하다
- ! 머리말의 '저번 시간(Dental adhesive)'에서 괄호 안 강의명은 추론이다. p.49 필기 '지난 강의에서 universal까지'와 학습부 멘트('두 강의 모두 반짤반탈')로 뒷받침되지만, p.1 필기 원문은 '저번 시간'뿐이다
- Q24(FRC post '목적' → 슬라이드 제목은 Concepts)는 v=part를 유지했다. JB 해설도 '목적'이라 명시된 내용이 없다고 적고 있다

## CONS/INL — pass · 확인 124 · 수정 17
- The p.21 note says 'direct filling을 하는게 indirect 보다 해부학적 형태를 만드는데 유리', which contradicts the p.22 slide and note (anatomy favors the inlay). The draft follows the p.22 slide. The user should decide whether to mention the contradiction
- The p.48 red note says 'the other four faces are diamond-coated', which contradicts the slide note and JB (3 of 4 faces coated). The draft uses the slide and JB wording (3 faces)
- The last card (Anti-Aging) also has a 'Q09 (link)' ⭐ line, so Q09 is linked from two cards. This is intentional but should be checked after the build
- The worker's lec= and [[INL:page]] citations switched from the old labels ('시험문제 p.7' etc.) to page numbers in the new PDF. The annot, tables and pred blocks in tools/cons/annot.txt, tables.txt and pred.txt still hold the old labels until the parts are merged. The v=, yrsnote= and rel/pair values match the existing ones
- Density is well above DD1 (157 items, 13 tables vs 75 items, 4 tables). The format matches DD1, but the user should confirm the density is not excessive

## CONS/WHT — pass · 확인 62 · 수정 12
- The 출제 value in the questions.md header is shortened, because tools/dump_review.py parses the badge text 'A · B · C · D … Z'. For Q02 it shows 24,23,21,20,10 and for Q04 22,21,20,17,14. The real values are 11 years for Q02 and 7 years for Q04, as in the JB brackets and the yrs array in docs/packs/CONS.js. The E: lines follow the full values, and qids.json has the same shortened lists, so any automatic year check must not rely on it
- The originally approved WHT manuscript already used ==highlight== for slide sentences that were never exam questions (for example Safest, efficient method; Immediate; Use of lights did not lighten…; 반드시 한쪽 악부터 시행). This does not match the SPEC definition (== = sentence that appeared on the exam as written). Since the user approved that version, I left those as they are. The user should decide whether to remove them
- tables_WHT row 'Vital 적응증: 변색이 chemical dye에 의한 것일 때' is an application of the slide 26 principle. The slides have no explicit list of vital bleaching indications
- The captions on the 25 handout images (old WHT images) were only partly checked against their notes: 7, 30, 31, 34, 69, 83, 102, 128 and 163 were opened, and the rest were not

## GERI/BLE — pass · 확인 62 · 수정 8
- 원고 머리말의 'JB 참고 쪽(24 강의 p.33·37 / p.44·45·46) = 이 25 PDF p.32·36 / p.43·44·45'는 1쪽씩 밀렸다고 보고 맞춘 추정임. 내용(splotchy·종료·relapse·dingy·touch-up)은 전부 맞지만, 24 PDF를 직접 대조한 것은 아님
- Splotchy 정의 문장(==형광==)은 JB 답을 글자 그대로 옮긴 것이 아니고 p.32 필기 문장임. 기출에서 묻는 정의와 뜻은 같아 형광을 그대로 둠. 엄격하게 JB 원문 문장에만 형광을 쓰려면 사용자가 판단해야 함
- p.98·99 transfer barrier probing 항목('치관 밖 x / 근관 안 x + 2-3 mm')은 필기 설명이 없는 그림을 읽고 쓴 설명임. 수치와 라벨은 이미지와 일치함
- p.1 표지만 카드 쪽 범위에서 빠짐(정상). p.2 목차(Lecture Outlines)는 원인 카드 범위에 넣었고 따로 항목으로 만들지는 않음

## GERI/ENDO — pass · 확인 56 · 수정 11
- annot 판정이 이번 작업에서 두 문항 바뀜: E11 ok→part(JB 답의 원인 '근관 주위 상아질의 방사선투과성이 낮다면'이 26 슬라이드 p.26에 없음 — 이 판정은 맞다고 확인), E13 ok→part(핵심 방법은 일치, 'RC prep 윤활작용'만 26 자료에 없음). 판정 바꾼 것을 사용자가 받아들일지 확인 필요. E09의 lec 연결 쪽도 ENDO:14→ENDO:61로 바뀜. yrs=·rel=·pair= 값은 기존 annot.txt와 같음
- p.27 필기 'radiopaque하게 보이기 때문에'는 슬라이드 'Radiodensity tertiary < primary dentin'과 방향이 반대 — 원고에 ⚠로 표시만 해 둠. p.70 슬라이드 조건은 'non-surgical endo treatment'인데 필기·JB는 '치료할 수 없는 경우'로 읽음 — 이것도 ⚠ 표시만 해 둠
- 그림 캡션 여러 개(예: 3·9·11·21·33·45·56·57·68·71 등)가 필기가 아니라 슬라이드 제목 문구에서 옴. 원칙 9번('필기에 설명이 있을 때만, 없으면 쪽 번호만')을 엄격하게 적용하려면 쪽 번호만 남겨야 함 — 사용자 판단 필요
- 필기 상자의 색(초록=과거 필기, 빨강·파랑 상자=26 필기로 보임)만 보고 원고가 일부를 '26 필기'로 표기함. 색으로 출처를 정확히 가를 근거는 자료에 없음
- 빌드(build4)와 playwright 화면 확인은 지시대로 하지 않음 — 다음 빌드 때 ENDO 카드 렌더링, 특히 ① 목록과 표 확인 필요

## GERI/HARD — pass · 확인 62 · 수정 6
- Y02(22년 백악질) JB 답의 'tertiary dentin과 달리 새 cementum은 기존 것과 방향성 동일' 문장이 25 유연지 슬라이드와 필기 어디에도 없음. p.12 '배열은 층상'과 p.10 반응성 상아질로만 대응할 수 있어 v=part로 둠(기존 annot.txt는 ok였음). 24 유연지 강의 p.10에 있던 문장일 가능성이 있으니 24 자료가 있으면 확인해 주세요
- Y06(erosion intrinsic source 6개)은 25 자료에 목록이 없고 p.42에 'Erosion' 단어만 있음. 그래서 v=none으로 둠(기존 part). JB 답으로만 외워야 함
- Chemomechanical 카드의 '짝 맞추기' 항목(위험요인 ↔ 예방 3)은 자료의 두 슬라이드를 작업자가 묶어 놓은 정리임. 새 사실을 더한 것은 아니지만 교수님 필기에 있는 연결은 아님
- 마지막 카드의 영문 제목 'Signs of Time — Age-related Conditions'는 슬라이드 제목('노화에 따른 치아 경조직의 변화')을 영어로 옮겨 만든 이름임. 사실을 주장하는 문장은 아니어서 그대로 둠
- annot의 JB 참고 쪽 대응(예: '240905 p.10 = 25 PDF p.12')은 주제가 같다는 것에서 추정한 것임. 24 자료로 직접 확인하지 않았음

## GERI/OHQ — pass · 확인 68 · 수정 13
- All 11 H items (한동헌 24) have no matching material (v=na), and the JB note says the exam was not based on the ppt. The E: lines are only loosely linked to the card topics. The user should know these are common-knowledge questions.
- The 26 slide 14 notes '주로 노인에게 사용 / 일반 성인에게 사용' are appended to the end of the slide text. The reading that they mean GOHAI = elderly and OHIP-14 = general adults is inferred from their order.
- The OHIP-14 memory line '(1994)' comes from the C14 JB question text, not the slides.
- The 26 pptx images (slides 6·7·15·20·22~25) are not wired into F:. Figures use the same graphs and tables from the 25 PDF (OHQ5). Using the 26 originals would need an image key registered in subject.py.
- 25 p.25-27 (result tables of the sex-difference study) are not cited as figures. Only the conclusion p.28 is shown.
- questions.md shows C02 as '(학습부 예상 — 선지 미복원)', but it actually has options made by the student study group. This is a display matter, so it was left as is.

## GERI/PAIN — pass · 확인 68 · 수정 9
- Card count is 27, above principle 5-1's 'about 7-19 cards per lecture'. Pages covered, density and format are at or above DD1 level, and 96 pages is proportionate (DD1 is 19 cards for 75 pages). If the user wants fewer cards, merge candidates are 'Age Differences in Pain Presentation' into 'Pain Perception' and 'PAINAD' into 'Nonverbal'. Merging changes card ids, so it was left for the user to decide.
- J11's verdict is back to part (the worker had raised it to ok). If the user considers 'the JB answer matches p.18 exactly' enough, ok also works.
- The 2023 'vocalization blank' in J01 is based only on the JB commentary; no 2023-column copy of the question exists. The year value itself is correct as it is in questions.md.
- The p.83 slide spells it 'amytriptyline'; the draft uses 'amitriptyline'. The spelling difference was left as is.
- No build (build4.py) was run, so on-screen rendering is unchecked. The J11 v=part change also needs to reach tools/geri/annot.txt through merge_parts.

## GERI/PSY — pass · 확인 68 · 수정 9
- Question years: the header line in questions.md and yrs in qids.json show only 5 years for P01 (21,20,18,16,11) and P02 (21,20,18,17,11). The live pack docs/packs/GERI.js has the full lists: P01 [21,20,18,16,14,12,11] (7 times) and P02 [21,20,18,17,16,14,13,11] (8 times). These match the JB brackets converted from 학번. The manuscript and annot use the 7- and 8-year lists and I left them as they are. The header in the review file looks truncated for display ('…'). The user may want to confirm this.
- Four card 국문 부제 lines still list years: '(24·23)', '(23)', '(22·21·20·18·16…)' and '(21·20·18·17…)'. The years are correct. The writer kept these titles on purpose so existing highlights stay attached (the aid is built from the title). Other subjects (ANAT, SAL) keep the same style. They clash with the rule of no year lists in 부제, so the user needs to decide.
- P04 was changed from v=ok to v=part. Option 5 ('알츠하이머 등의 전구반응') has no support in the 25 material, and option 3 was never restored. If a 21-year 박지은 file turns up, this can be settled.
- Page 44 (감사합니다) is not in any card's page range. This is expected.
- p.41: the 필기 '그리고 남에게 더 의존하게 된다' sits next to 조심성 증가 on the slide. The manuscript attaches it to ④ 의존성 증가 because of what it says. This is my reading of the page, not a confirmed placement.

## GERI/SAL — pass · 확인 64 · 수정 6
- For G04, the 출제 value in qids.json and in the questions.md header is '24,23,22,21,9', while the page display shows '2024·2023·2022·2021 … 2009, 14회'. The list looks shortened, and the full 14 years (including converted class-year brackets) are not written out anywhere. The card's E: follows the display text ('24·23·22·21 … 09년(14회)'); the full year list for G04 needs checking by the user.
- Renaming card 4 changes its content-based card ID, so any highlights or '이해함' marks the user made on that card before may not carry over. The earlier rewrite probably changed it already.
- A few small spelling and wording differences were left as they are. The notes say 'lysosyme'; the card writes 'lysozyme'. The 🔑 line of the connective-tissue card uses '치주인대 폭', a Korean gloss of the slide's 'Width of periodontal ligament'; that exact phrase is not in the material.
- Figure p.7 is shown only in card 3 and p.8 only in card 4, so card 4 (노인병·노인증후군, p.7) and card 5 (구강건조증 유병률·구조, p.8) have no figure right under that content. This does not break the rules, but a second copy could be placed there.

## IMPL/BIO — pass · 확인 68 · 수정 4
- 7 card Korean subtitles still list years or exam formats, which the rule 'no year list in the Korean subtitle' forbids: 'PDL의 장점 4 (22 T/F → 24 나열)', '(20·21년)', '(21·22·24)', '(23년 빈칸)', '(23년 넘버링)', '하악의 굴절 (20·22·23·24 — 4회)', and '무치악 상악의 임플란트 개수 — arch form별 6·7·8, 이상적 9'. They are identical to the committed version, and a card's aid is slug(en,ko), so editing them would drop the user's saved highlights and blanks on those cards. The user must decide whether to remove them.
- JB answers for Q18/S01 say '5~10배' where the slide says 10X. The Q06 answer adds '설측', which is not on the slide (only the figure). Both are marked ⚠. Whether to follow the JB wording or the slide in an exam answer is the user's call.
- U09's 2.5배 comes only from the 25 note, and the maxillary vs mandibular cantilever table (뷰머·루이스, 20 mm) is a slide the professor added during the 25 class, not in the PDF. Neither is in the 26 material.
- The T01 and T02 23년 학습부답 (3급 악간관계·입술지지, fixed maxilla 8 / mandible 6, occlusal scheme) is textbook-sourced and absent from the lecture materials, so both stay v=part.
- The Korean glosses in the three-force table (압축·인장·전단, 누르는/당기는/옆으로 미는 힘) are translations, not slide text. The '2 piece' split line in the p.44 figure is hard to read, so that description is my reading of the image.
- The build step (build4.py) was not run, as instructed, so rendering and figure loading on the site have not been checked.

## IMPL/GRAFT — pass · 확인 68 · 수정 9
- 머리말의 '24 필기 별표: 18·57·94' — p.1 필기 원문은 '1 8, 57, 94'(띄어 씀)임. 옛 원고와 과목노트_IMPL은 16으로 적었고, JB 참고 쪽(24 슬라이드 p.16)과 쪽수 차이(+3~4)로 보면 16이 맞을 수도 있음. 작업자는 원문 그대로 18로 두었고 나는 바꾸지 않음 — 사용자 확인 필요
- p.19 형광 ==새로운 골이 형성하고 발달하는 과정==은 슬라이드 문장이고, JB 문제 문장('새로운 골을 형성하고 발달시키는')과 조사가 조금 다름. 출제 문장의 출처로 보고 그대로 둠
- p.73 비교표의 큰 글씨 줄(공간유지 우수·반드시 제거·창상이 잘 벌어짐·조작이 불편 / 공간유지 효과 저하·제거 불필요 등)은 이미지상 '장점' 칸에 들어 있음. 원고는 내용에 따라 장점과 단점으로 나눠 적었는데, 해석이 맞는지 사용자 확인 권장
- tools/impl/annot.txt(원본)에는 아직 옛 [[GRAFT:p.N]] 표기와 '25 텍스트본' 문구가 남아 있음 — merge_parts로 파트를 합칠 때 새 파트 값으로 바뀌는지 확인 필요(이번 범위에서는 원본을 건드리지 않음)

## IMPL/HIS — pass · 확인 52 · 수정 11
- Q14 판정을 작업자가 v=ok → v=part로 바꿈(annot.txt의 기존 값은 ok). 'external' 판정은 슬라이드 문장에 근거가 없고 사진만 보고 내린 JB 답이라 part가 맞다고 보고 그대로 둠. 사용자가 이 판정에 동의하는지 확인이 필요함
- 25 필기 p.24에 '과거 대부분 internal 사용'과 '과거에는 대부분 external 사용'이 함께 적혀 있어 서로 모순됨. 정리본에서는 26 필기('internal은 과거에 잘 안 썼음')만 썼음
- 25 필기가 p.43 Shaping drill을 '= Tapping drill'이라고 적었는데 학생 필기의 해석일 수 있음. 25 필기라고 밝혀 두고 옮김
- 카드 12장·항목 53개로 DD1(19장·75항목)보다 적음. 다만 p.39-47은 키트 그림 위주이고 표가 15개라서 밀도가 떨어진다고 보지는 않았음
- HIS 외 강의(BIO:13·OSS:36·PART:3)를 가리키는 annot M: 인용은 해당 텍스트 쪽을 확인했음. 원문은 수정하지 않음

## IMPL/OSS — needs_human · 확인 64 · 수정 17
- Q16 annot: the worker changed v=ok to v=part. This differs from the current value in tools/impl/annot.txt (ok) and from the site label ('강의자료와 일치'). I kept part: the JB answer to option 2 relies on another subject's lecture (구강악안면외과학 Loading protocol p.7) and this lecture has no basis for it, which matches principle 7-3. The user should confirm.
- Three Korean card subtitles still carry exam years: '(23·24 연속 출제)' ×2 and '(23·24 연속)'. Card 2's subtitle also says '뼈의 세포 3가지' although the slide lists 4 cells. The worker left these unchanged on purpose: the card's saved-highlight ID is built from the English and Korean titles, so editing them would drop the user's existing highlights. The user must choose between the rule (no years in subtitles) and keeping highlights. The table title '뼈의 세포 3가지' was left for the same reason.
- p.26 Figure 8-1: the week for stage C is hidden by a head in the photo and cannot be read. The notes say the last picture is about 6 weeks, but the caption says D = 12 weeks. The material itself is inconsistent here.
- p.27, 31, 33 and 36 contain only a transcript of the lecture, with no slide. p.33 in particular is a garbled speech-to-text transcript, so the regional bone-quality items (general mandible D2, maxillary anterior/premolar D3) rest on how that transcript is read.
- The p.1 black-box note is not labelled with a year. It is only certain that it came after 22, probably 23, so which year counts as 'last year' in 'last year's exam' is still an inference.

## IMPL/PART — pass · 확인 64 · 수정 11
- Abutments — Types card: the Osstem-vs-Dentium mapping table pairs Dentium parts to categories by name only (Dual Abutment = ready-made, Direct-/Metal-Casting = UCLA type, Milling = custom). The only note on the slide is '덴티움도 똑같아요', and the card says the pairing is by name. The user should decide whether to keep this table or drop the Dentium column.
- Scan body E: line ends with a study-trap hint ('전통 인상의 impression coping·healing abutment와 헷갈리지 말 것'). This is study advice, not a sourced fact. Kept.
- The in-lecture cross-links to HIS ({jb:Q10} external vs internal, cited as '역사·용어·설계·표면 강의 p.24-25'; {jb:Q13} healing-abutment definition, cited as '조영단 강의 p.22') rely on annot.txt / lec_HIS page numbers for the 26 HIS material. I did not reopen the HIS PDF.
- annot_PART.txt R11 header now has lec=PART:16; the existing tools/impl/annot.txt has lec=PART:14. v= and the absence of yrs=/rel=/pair= match. p.16 (the open-tray procedure) is a reasonable anchor, so I left it; revert to 14 if the base value must match exactly.
- Q08 and R11 are listed under 조준호 in questions.md, but the JB 참고 lines name 이재현 (the 23·24 exams). The manuscript says so explicitly. No year was added or removed (Q08 = 24,23 · R11 = 23).

## IMPL/PATH — pass · 확인 72 · 수정 11
- 26 p.2 slide (old national-exam question): the slide circles answer ① 가나다, but the note says aspirin should be kept, not stopped. The manuscript's key line follows the note (아스피린 → 복용 유지) and the card points out the conflict. The user should decide which answer to trust.
- 25 p.12 has two notes that say opposite things: 'aggressive하고 invasive한 치료를 시도하라' (before the drug is started) and '침습적인 치료는 … 미루어야' (while on it). The manuscript keeps both as they are.
- R13 and R14 are the professor's announced questions (추1·추2 in the JB). The JB does not say whether they were actually on the exam. The year stays 23, as questions.md gives it.
- Sibling IMPL manuscripts (OSS, PRO, BIO and others) also put == on many non-exam slide sentences. I only fixed PATH, so highlight use is now inconsistent across lectures in this subject.
- The Zavyalov line ends with '임플란트 대신 보철', which is my reading of the slide text. If even that is too much interpretation, the user may want it removed.

## IMPL/PRO — pass · 확인 68 · 수정 8
- 국문 부제 4곳에 연도가 들어 있어 원칙('국문 부제에 연도 나열 없음')과 어긋납니다: '(23년 서술)', '(22·23)', '(20·21·22)', '(23년)'. 부제 글자가 카드 aid(형광펜·빈칸 저장 키)를 만들기 때문에 작업자가 일부러 그대로 두었고, 저도 바꾸지 않았습니다. 연도 자체는 questions.md와 맞습니다. 기존 표시를 잃더라도 부제를 바꿀지 사용자가 정해야 합니다.
- micromotion 카드 부제 '150 → 100 → 50 μm'(그대로 둔 기존 부제)는 슬라이드 순서(Sobelle 150 → Vandamme 50 → Tettamanti 100~150 → 결론 50~150)와 맞지 않습니다. 바꾸면 aid가 달라집니다.
- Dynamic Equilibrium 표의 dip 값 '약 4주·약 80 / 약 2주·약 30'은 그래프에서 읽은 값입니다. 슬라이드나 필기에 글자로 적힌 수치가 아닙니다.
- 빨간 테두리에 검정 글씨인 필기 상자는 어느 해 필기인지 자료에 표시가 없습니다. 원고에서는 해당 상자를 모두 '(필기)'로만 적었습니다.

## OMS1/DD1 — pass · 확인 68 · 수정 14
- The Korean subtitle of the card '## Treacher Collins Syndrome | TCS | 64-69' is still 'TCS', an abbreviation that appears in neither the slides nor the JB. It is part of the card id (slug of the English and Korean titles), so changing it could detach the user's existing highlights. The user should decide whether to rename it, for example to '트리처 콜린스 증후군'.
- The approved manuscript highlighted four slide sentences with ==…== even though they were never exam sentences (Premature fusion…, perpendicular…, Skull osteotomy…, growth potential…scarring). I changed them to {r:}, which follows the ==exam sentence== rule but changes markup the user had approved. The text itself is unchanged.
- '==Accommodate head expansion==' stays highlighted. The S21-3 JB answer reads 'head position', so the highlight is the slide version of an exam sentence. The ⚠ warning is in the E: line.
- The worker's disputed change is correct: the approved Treacher Collins summary used 'bilateral', which no slide (p.64-69) supports, and removing it was right. The user should still be told that an approved sentence changed.
- J8 is listed in the jb= of the Muenke·Saethre-Chotzen card but has no E: line there; its E: is in the Genetics card. The checks pass, but the user may want this confirmed.
- Verified without problems: all 21 linked questions have E: lines and their years match questions.md; annot yrs= match tools/oms1/annot.txt and none of these blocks has rel/pair/yrsnote; verdicts changed for Q38 (ok→part, Psychological vs Psychosocial) and J6 (ok→part, JB treatment is from the textbook), and both changes are justified; I spot-checked more than 20 A: quotes against page images; pages 1-75 are all covered.

## OMS1/DD2 — pass · 확인 58 · 수정 6
- 작업 지시에 적힌 연결 문항 목록(S20-1, S20-2, S20-8, S21-2, S21-3, S21-5~7, J8, J10, J12, J13)이 실제 데이터와 맞지 않음. work/OMS1/review/qids.json의 DD2 연결 문항은 Q07, Q08, Q09, Q10, Q26, Q27, Q40, Q41, Q42, Q43, S21-4, S20-3, S20-4, S20-5이고, 검토도 이 14개로 함. 14개 모두 E:와 annot 블록이 있고, 연도는 questions.md 머리줄과 같음(Q07·Q08 23·24 / Q09·Q10 24 / Q26·Q27 23 / Q40~Q43 22 / S21-4 21 / S20-3~5 20). 지시에 있던 S20-2, S21-6, S21-7, J10, J12, J13은 qids.json에 아예 없음. 목록을 만든 스크립트를 확인할 필요가 있음
- S20-4의 대조 판정이 기존 annot.txt의 v=ok에서 작업자가 v=part로 바꿨음. 근거는 JB 답의 '보조적으로 PA, transcranial, panorama'라는 묶음이 자료에 없다는 것(필기에서 '보조적 수단'이라고 한 것은 CT)이고, 타당하다고 봐서 그대로 둠. 반영 전에 사용자가 확인하면 좋음
- 형광펜 보존: 예전 카드 'Regional Evaluation'(Q40)과 'Cephalometric Analysis — Norms'(Q08·S20-5 포함 36-49쪽)를 여러 카드로 나눴음. 예전 카드 안에서 옮겨 간 문장에 칠해 둔 형광펜·빈칸은 복원되지 않을 수 있음
- p.6 필기를 N에 붙인 것은 필기 칸의 위치를 보고 판단한 것임. 필기 칸이 G와 N 사이에 걸쳐 있고 Sn 옆에는 필기가 없음
- 빌드(build4.py)는 지시대로 실행하지 않았음. 화면 렌더링과 형광펜 복원은 다음 빌드 때 확인해야 함

## OMS1/DD3 — pass · 확인 78 · 수정 11
- Q12: 22년 칸의 JB 복원 답('ear rod … external auditory meatus가 전하방으로')은 26 슬라이드와 필기에 문장으로 없음. p.6 그림에 Ear Rod 표지만 있음. ⭐ 줄과 대조 주석에 ⚠·부분으로 표시해 두었으니, 두 복원 답 가운데 어느 쪽을 외울지는 사용자가 정하면 됨
- Q44: JB 해설의 '7°를 이루어야 한다'는 규범식 표현은 슬라이드에 없음. 슬라이드는 '7° off FH'라는 사실 서술임. 대조 주석에 참고로 적었고 v=ok는 그대로 둠(답 7°는 슬라이드와 같음)
- STO 비교표에서 Initial STO의 '시기(치료계획 단계, 술전 교정 목표를 세울 때)'는 슬라이드에 없고 p.11-12의 흐름과 필기에서 추론한 것임. 문장 자체는 필기 표현이라 지우지는 않음
- p.7 그림 캡션 'Frankfort horizontal plane vs axis-orbital plane'은 필기 설명이 아니라 슬라이드 표지를 옮긴 것임. 원칙(캡션은 필기에 설명이 있을 때만)을 엄격히 적용하면 쪽 번호만 남겨야 함
- 빌드(build4.py)를 돌리지 않았으므로 화면 렌더링(구조화·그림 로딩)은 다음 빌드 때 확인해야 함. check_lec(✗ 0)과 merge_parts --check(검사 통과)는 수정 뒤 다시 돌려 둘 다 통과함

## OMS1/DX — pass · 확인 64 · 수정 11
- Q30(서미현 EXT 문항)이 DX 골량 카드의 E:에 Q47과 함께 연결되어 있음. 검사는 통과했고 p.26이 JB 해설 근거이긴 하지만, 빌드에서 Q30이 DX 카드에도 연결되어 보이는 것이 사용자 의도와 맞는지 확인이 필요함
- p.27 오른쪽 그림 설명은 슬라이드 오른쪽이 잘려 있어 끝부분을 '…'로 남김. 원본 PDF에서 잘리지 않은 판이 있으면 채울 수 있음
- Q47 선지 1~4의 판정 근거(방강미 22년 자료 p.21)는 받은 25년도 자료에 없음. annot에 '근거 없음(이 강의)', v=part로 표시되어 있음

## OMS1/EXT — pass · 확인 68 · 수정 9
- Density: this manuscript has 187 items against DD1's 75. The case cards (p.32-48, 61-64, 72-76) have many items, while principle 5-11 says to group 'passed-over' cases briefly. Everything checks out against the slides and notes, but the user should decide whether the cases feel too long
- Q17 (23·24 short answer, 5 stages of socket healing) is not in the lecture material. The JB itself says the source is a textbook, pp.105-106. The card carries the JB answer's 5 lines verbatim, marked '강의자료 없음', with v=none. The user may want to get the textbook pages
- Q17's lec= was empty in the original annot.txt and the worker's part sets lec=EXT:8. That is a link to the p.8 card (1 and 2 months after extraction), not a change to years. yrs=23,24 is unchanged
- ==highlight== is used on some slide sentences that the JB explanations quote as the basis for an answer (p.25 'does not provide evidence…', p.4 'more pronounced at buccal side', etc.), not only on sentences that appeared word for word in an exam. DD1 uses it the same way for sentences in JB answers, so I left it, but the user should confirm this reading
- The 'professor emphasis' header lists the red slide text on p.25 and p.53. That red is the slide's own design, not a handwritten note like '시험' or '외워라'. It will show up in the subject home's '📣 교수님이 예고·강조한 것' panel

## OMS1/LOAD — pass · 확인 58 · 수정 11
- Q20 (on the Loading Timing card as a cross-reference E:, linked to the DX lecture): the JB answer ends in '(?)' and the JB itself flags that '수평력' may have been restored as '수직력'. The card's E: carries this warning, but the user should confirm whether the reconstructed question is right.
- Image p.11 is cited in both the Loading Concepts card (early loading, Korean text at top) and the Other Definitions card (Misch definitions at bottom). The page holds both topics, so both are kept, but the same image appears twice.
- p.19: the highlight on '하악의 이공 사이 부위가 가장 유리' is kept even though the 24-year T/F turned it into the opposite statement ('가장 불리' → F). This follows the rule that tested sentences are highlighted, but the user may want to decide.
- The 🔑 line on the Pros/Cons card lists 5 advantages and 3 disadvantages in English. It is somewhat long, but it is exactly the exam answer, so it was left as is.
- Checked the annot part: the 3 blocks Q21, Q22 and Q48 are all present. Their yrs= and lec= values match tools/oms1/annot.txt; the part has no yrsnote=, rel= or pair= fields. 16 A:/M: quotations were compared with the t/ pages and match. Q48's N: note on the wording difference 'mastication' vs 'masticatory' was also confirmed in questions.md.
- Checked the tables (5) and the predicted questions (10) against the slide text: they match apart from the A-P spread wording fixed above. The predicted-question answers are slide sentences.

## OMS1/REP — pass · 확인 64 · 수정 8
- The 3D printing case on p.12 (allogenic transplantation, daughter's #8 → mother's #6) sits in the Transplantation Procedure·Progress card (9-12). It could fit better in the Allogenic card; it was left where it is because that card's page range covers p.12.
- p.36 shows the date '2021.02.04' but '21 weeks later'. This looks like a typo for 2022 on the slide itself; the case table keeps it as '슬라이드 표기 2021.02.04'.
- The JB 22년 칸 for Q24 only preserved the format ('정의 주고 빈칸빵'), not the question text. Calling it 단답형 for 22년 is an inference from that description.
- A few links between the textbook and the 보존과 교수님 slides are my interpretation, not written in the materials. Example: '기능적 자극 → p.5 예후 고려사항 ②' cross-reference. The user may want to confirm these.
- annot_REP.txt, tables_REP.txt and pred_REP.txt were checked and not changed. All three questions have annot blocks, and the header fields (v/yrs/yrsnote/pair/lec) match tools/oms1/annot.txt exactly. 16 A:/M: quotes were checked against p.2, 4, 5, 6, 14 and REP2:20. Table and prediction answers match the slide text. build4 was not run (as instructed), so the merged output has not been rendered.

## PHARM/ACU — pass · 확인 68 · 수정 10
- PN21(20년 Neuropathic vs Nociceptive 표 빈칸)은 CHR 강의에 배정됐고 사이트에 '대조 na · 대응 강의자료 없음'으로 나옴. 하지만 표가 이 자료 p.18에 글자 그대로 있음 → CHR 담당 쪽 annot에서 v=ok, [[ACU:18]]로 고쳐야 함(이번 작업 범위 밖이라 손대지 않음)
- PN13(21년 영문)과 PN24(20년 한국어 복원)는 같은 만성통증 p.18 문장인데 사이트에서는 따로 떨어진 문항. 연결(OTHER)할지는 사용자가 판단해야 함. 출제연도는 규칙대로 건드리지 않음
- PN09 JB 답 (2) 'somatic, visceral' 중 visceral은 p.17 정의에 없고 p.3에만 있음(v=part). 문제 복원이 불완전해 (4)에 해당하는 답이 없음
- PN16 '가장 낮은 dose에서 나타나는 효과'는 25 자료 슬라이드·필기 어디에도 없음(JB 해설도 인정). 근거가 22 자료 필기뿐이라 v=part
- check_abbr에 걸린 약어(TRPV1·TRPV2·PKA·PGE·PGE2·NOS·ASIC·P2X·NGF·NK1·TTX·VR1)는 모두 쪽 이미지 속 그림 라벨로 직접 확인함. SNRI는 이 자료 p.21에는 풀어 쓴 형태로만 있고, 약어는 같은 교수의 만성통증 자료에 나옴
- annot의 lec= 쪽 번호가 기존 annot.txt와 다름(PN10 12→20, PN14 25→20). 둘 다 문장이 실제 있는 쪽이라 더 정확함. yrs·rel·pair 값은 기존 파일에도 없어서 달라진 것 없음

## PHARM/BT — pass · 확인 58 · 수정 13
- The JB answer for BT04 option 4) and BT18 option 2) ('활성화 기간 4-6개월 ✗', based on '2주 시작·6주 최대') comes from an old edition's p.47. The 26 material has no matching slide, and the 26 p.29 note says '15-20U로 3-6개월 효과'. The draft flags this with ⚠, but the user should know the exam answer and the current material differ here.
- The BT02 exam option (BoNT 위장관계 효소에 저항) contradicts the 26 notes on p.7 and p.9 ('대부분 소화계에서 분해'). The note keeps the slide wording as the grading basis and marks it ⚠.
- BT15: the JB answer is 1),3), but the 21학번 학습부 and the p.14 step 2 slide support 1) only. BT03 option ③ ('독성은 약하나') is also wrong by the slides, yet the JB answer is 4) only. Both are left as v=part with ⚠ — worth the user's judgement.
- BT07 and BT13 have JB-correct options '20-50U 양쪽', and BT17 has '20-60 U' (not treated as wrong by JB). Both numbers differ from the slide value (25~50 U/side), probably a recall error in the reconstructed questions.
- tools/pharm/annot.txt has no existing @BT blocks, so there were no stored yrs=/yrsnote=/rel=/pair= values to compare against. The part file adds none either. All years match the '출제' values in questions.md.

## PHARM/CHR — pass · 확인 68 · 수정 19
- Card titles changed. The earlier worker already split the note into 18 new cards, and I renamed the homework card again to 'Homework Case — Burn → Chronic Pain'. Highlights or blanks the user put on the old cards may not carry over.
- PN21 (neuropathic vs nociceptive table) and PN17 (ketorolac) are judged ok, but the supporting slides are in the 급성통증 lecture (ACU p.18 and p.27). The site header for PN21 still shows '대조 na'. The earlier worker raised PN21 from na to ok because the answer matches ACU p.18 word for word. The user should confirm that call.
- PN07's lec= changed from CHR:11 in tools/pharm/annot.txt to CHR:24 in the part file, which puts it on the dialysis-paper card. That is intended, but it will differ from the main annot until merge_parts is run.
- The dialysis card (PN05, PN06, PN07) cites page 24, but its content comes from the paper the professor assigned. Only the JB explanation's quotes are on hand, not the paper itself, so the quotes cannot be checked against the original.
- The p.24 slide spells 'ibuprophen', but the note uses the standard spelling ibuprofen. Left unchanged.
- The build (build4.py) was not run, as instructed, so rendering has not been checked.

## PHARM/DS — pass · 확인 96 · 수정 16
- '포타딘 볼 = povidone-iodine' (Antiseptics card and its recall line) is an inference. The notes say '히비탄 볼, 포타딘 볼' on p.2 and '포비돈' on p.7, but no page states that the two are the same product. Needs the user to confirm.
- annot DS20 N reads the JB explanation 'Volatile and powerful, 4)' as a numbering slip, since option 4) actually comes from the mercury sentence. This is an interpretation.
- DS14 (iodine, 22) exists only as the recovery memo, and the correct option of DS17 (phenol, 21) was never recovered. Both are v=part and cannot be judged from the material.
- The p.43 FYI textbook table disagrees with the slide text in places (CHX HIV +, Oxidizing agents all +). The notes flag this, but the user should know exam answers follow the slide text.
- The lecture itself flags gaps in two JB answers: DS26 counts 'Denature protein' as correct, and DS19 says moisture accelerates 'the effect'. The slides say something different in both places (the mercury mechanism is 'Reversible interaction with sulfhydryl group'; for ZOE the setting reaction is what speeds up). Both are marked ⚠, and the JB answer text was not changed.

## PHARM/HM — needs_human · 확인 64 · 수정 12
- JB split errors, which cannot be fixed in the lecture files. (1) The 2021 Q14 'types, standards and calculation of pre-operative tests' (answer INR(PT), aPTT) is glued to the other-edition text of HM04 and is not its own question. (2) The 2021 Q12 Mr. J case is glued to HM18's text; HM10 may also have been set in 2021. (3) HM24 (2020 Q15) contains 15-1, which is the same question as HM07, so HM07 may also have been set in 2020. (4) HM03 (24·23·22) and HM11 (22·20) are the same question; HM16 and HM21 are also duplicates. Merging questions or adding years is for the user to decide. I kept the years exactly as questions.md gives them.
- HM09: the JB bracket in the 2021 column reads (21’, 20’, 19’, 18’, 17’이전), but questions.md lists only 22·21·20. Under the year rule, 19 and 18 may need adding. The user needs to confirm this in assemble.
- HM01 (physiological anticoagulants recognize thrombin) and HM23 (GP Ib–vWF) have no supporting slide in the 25 material (v=none). HM06's TFPI and thrombomodulin and HM05's '9-12' count are also only in the 22/23 material. These can only be memorized from the JB answer. When the 26 or older material arrives, it should be checked again.
- HM20's v changed from part (current value in annot.txt) to ok. This should be reflected when merging. HM22's first JB answer 'II, V, VII, X' differs from the slides; the lecture file marks this with ⚠ and gives the corrected answer II, VII, IX, X.
- check_lec counts 24 cards, more than the 7~19 cards per lecture in principle 5.1 (DD1 has 19–20). Each card is one topic over 59 pages, so I did not merge any. If the user wants fewer cards, the small ones can be merged: Gelfoam + FloSeal, and PT·INR + screening tests.
- 25 JB says this lecture was not covered yet and the explanations are the old ones. If the 26 material for Woo Kyung-mi arrives, it replaces this, as the subject note says.

## PHARM/RX — needs_human · 확인 64 · 수정 14
- RX18 (20, T/F '처방전 발급 주체는 의사·치과의사·한의사'): the JB answer is F, but 의료법 17조의2 on 26 p.4, 18조 ④ and the 25 note (25 p.6) all include 한의사, which points to T. Annot marks it v=diff. You should decide which answer to memorize.
- RX05 (23): the JB answer is 'NRT or 바레니클린', but only NRT is explicitly '주의 깊게 사용' (p.79). The materials also conflict with each other: p.70 lists 청소년 as an NRT contraindication.
- RX11, RX24 and RX29 ask who may counsel, join the program or prescribe (한의사, 간호사, 군의관). None of the 26 or 25 materials has such a list, so the JB answers come from 2020–2023 materials and are marked v=part.
- RX27 (ACE2 and COVID-19) has no basis in the 26 or 25 materials (v=none). RX20's 2-year retention period is also not in the 26 slides; the answer is kept as the JB value.
- Card 2 got a new Korean subtitle, so its content-based card id changes. Any existing user highlights on that card may not restore; this applies generally because the whole manuscript was rewritten.
- Build (build4.py) was not run, per the instructions. Rendering and the audit_design check should be confirmed after the orchestrator builds.

## PHARM/XE — pass · 확인 68 · 수정 10
- XE05 (23, cevimeline, which patient has no adverse effect): the JB answer 4 (low CYP2D6 activity) has no basis in the lecture material, and the JB explanation says so itself. Option 5 is also incompletely reconstructed. The note flags this with ⚠ and v=part; please decide whether to trust the answer.
- XE07 and XE21 (BMS): the JB answer's mechanism of action ('Increases opening frequency of gaba channel' / 'GABA A receptor potentiation') is not on the slides (p.49 has no clonazepam mechanism). It is kept with ⚠ as a JB answer.
- XE02 (24): answer 3) is the only option with a value outside the normal range. It does not meet the dry mouth criterion (<0.1), and the other options' values (0.8, 0.05, 0.2) do not match the table exactly either, so the option numbers may have been changed during reconstruction (v=part). XE15 (21, fill-in-the-blank table): it is unclear whether the table was p.40 or p.55, and there is no JB answer.
- Asthma contraindication mechanism differs by slide: p.45 says 'Beta2 receptor activation', while p.32 (professor's emphasis) and p.42 say 'M3 → bronchial smooth muscle contraction'. The note keeps both with ⚠.
- Glaucoma type differs by slide: p.43 says pilocarpine treats 'open-angle glaucoma', p.35 says 'Glaucoma (acute angle-closure)', and p.31 and p.45 list narrow-angle (angle-closure) glaucoma as a contraindication. This is flagged with ⚠ in a U: line.
- Build (build4.py) and playwright checks were not run, per instructions. I did not verify the rendered result, including display of the cross-lecture [[BT:14]] link.
