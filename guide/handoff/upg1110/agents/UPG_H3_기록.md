먼저 /home/user/jbl/guide/handoff/upg1110/BRIEF_공통.md 를 끝까지 읽고 그대로 따른다(메인 저장소에서 일하는 '허브 담당' — 커밋 금지).

묶음 **W5 기록 — 저장·백업·동기화·넘버링·형광펜**. 읽기: guide/handoff/upg1110/R_DATA…md(B1~B3 · C1·C2 · D1~D4 · E1~E4 · F1~F3 · (b)2~4) · R_DESIGN_설계.md §0·§1 W2·W6 · tools/SPEC.md '기기 자동 동기화'·저장 공간·백업·'내 넘버링' 절 · guide/넘버링_따기.md · tools/tests/ux_sync*.py·ux15_storage.py·ux12_numrev.py·ux2_jblock.py·ux22_markbridge.py·fakegist.py.
맡은 파일: tools/cons/shell.html · tools/num/num.js(→ tools/num/build_num.py) · tools/quarters.py(qcfg others에 bakApp만) · 새 tools/tests4/q_store.py·q_backup.py · tools/tests4/q_sync.py(확장) · tools/SPEC.md·guide/넘버링_따기.md · 보고 guide/handoff/upg1110/DONE_W5.md.
할 일(기록을 건드리는 고침은 먼저 autoBak · 지우지 않음 · 옛 판 기기가 읽어도 안 깨지는 꼴):
1. 저장 공간(D3·D4): 저장 공간 창·경고에 '다른 쿼터(3쿼터) 기록 n MB — 3Q 허브에서 정리하기'(3Q 허브 주소 + 정리 창 열림 해시) · lqReplay의 14일 버림 없앰(써질 때까지 둠 — 띠에 밀린 개수·가장 오래된 날) · 다른 쿼터 백업 파일을 넣으면 "3쿼터 백업 파일이에요 — 3Q 허브(⇄)에서 넣어 주세요"(QC.others의 bakApp으로 판별).
2. 백업(D1·D2): 되돌리기/교체 창에 선택 칸 '넘버링도 이 시점으로'(num.i·num.x·num.r·num.rl·num.rs·num.subj·exam. — 저장소 계층 stGet/stSet/stDel로 · 문제마다 u 견줘 미리 보기 수) · 동기화 충돌로 밀린 판(IndexedDB 'old' — xsOld)을 복원 창에 목록(문제 제목·때·기기) + [되살리기](지금 것을 old로 보내고 바꿈) · 30일·200줄 넘으면 정리 · 백업 파일에도 포함.
3. 동기화(C2·E3·E4): 넘버링 복습 채점(num.r/num.rl)의 지움·바꿈 — rMark가 줄을 빼는 대신 지움 표시 `{t,s,x:1}` · 합칠 때 회차 s마다 가장 최근 t가 이김(mergeData·syncApplyGrp의 SYNCLOG 길) · 읽는 쪽은 x 건너뜀 · 처음 한 번 중복 정리 — 옛 판 기기(지움 표시를 모름)와 섞여도 기록이 깨지지 않는지 q_sync에 · GitHub 403/429: x-ratelimit-remaining/reset·retry-after를 읽어 '요청 한도(언제 다시)'와 '토큰 권한 없음(Gist 권한 — 다시 연결)'을 구분, 권한 없음은 되풀이하지 않음 · Gist 목록은 짧은 쪽이 나올 때까지(상한 30쪽 · 상한이면 경고).
4. 넘버링(C1·F1~F3): jbMove가 넘버링 문제의 src[].id·ref.id도 `S:옛 → S:새`(같은 새 id 문제가 이미 있으면 둘 다 두고 최근 u에 표시 — 지우지 않음) · leave()가 열린 '새 문제' 칸·ChatGPT 미리 보기에 글이 있으면 초안으로 남김(다시 열면 이어 쓰기) 또는 한 번 물음 · Word 파일 이름 날짜 = 허브 day()(한국 날짜) · 가져오기 창 dupOf를 (후보, 대상 판)으로 기억.
5. 형광펜(B1·B3): pick — 블록 지문 o.v가 다르고 후보가 하나뿐이면 문맥 점수 ≥ need일 때만 붙임(글이 12자 이상이면 지금처럼) · 아니면 '위치 잃음'(🖍 복구 목록) · ★ 카드 수 = 지금 있는 카드만 · migrateAids가 cbm·lrd도 옮김.
6. (b)2 꽉 찼을 때 밀린 ann/mk 값이 다른 탭의 새 값을 덮는 것: lsFlush가 ann.·mk.는 저장된 값과 합쳐 씀(합치기 함수 재사용) — 재현되면 고침, 아니면 보고만.
하지 않는 것: ann.<SID>를 강의별 키로 쪼개기(B2 — 측정 뒤) · 넘버링 시계 어긋남(b3) · 붙여 넣은 큰 그림(b4 — 보고만).
테스트: 새 q_store.py(다른 쿼터 기록이 큰 상태 — 경고 글·링크 · 밀린 쓰기 15일 뒤에도 남음 · 3Q 백업 안내) · q_backup.py(넘버링을 고친 뒤 자동 백업 시점으로 되돌리기 — 선택 칸 켬/끔 · old 되살리기) · q_sync.py 확장(복습 채점 지움·바꿈이 두 기기에서 같음 · 옛 판 섞임 · 403 권한 없음 = 되풀이 0) · 회귀(전·후): ux_sync · ux_sync_num · ux_sync_all · ux_sync_real · ux15_storage · ux12_numrev · ux8_num · ux9_numai · ux10_num5 · ux20_numdocx · ux21_numyrs · ux2_jblock · ux22_markbridge · ux_marks · kt_sync · tests4 q_isolation·q_ident.
끝나면 마지막 메시지에: 항목별 고침/안 함 · 테스트 전·후 · 화면 글 · 메인이 정할 것.
