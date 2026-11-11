# DONE_W3_허브 — 4Q 그림을 파일로 읽기(허브 쪽) + 0번(W5 메인 결정 5) (11-11 · 허브 담당 H4 · 커밋은 메인)

지시: `guide/handoff/upg1110/agents/UPG_H4_그림파일.md` + 메인 머리말(0번 = 되돌린 넘버링이 동기화에서 이기게 · fixture 변형은 qsite.py에 직접) · 기준 HEAD e24335e9
맡은 파일: `tools/cons/shell.html` · `tools/num/num.js`(sanitize) · 새 `tools/tests4/q_img.py` · `tools/tests4/qsite.py`(파일 방식 변형 함수만) · `tools/tests4/q_backup.py`(0번 한 경우) · `tools/SPEC.md` · 이 보고 · `DONE_W5.md` 끝 한 줄.
그림 주소 규칙 = `DONE_빌드.md` '그림 주소 규칙'(기준).

## 진행(항목 하나 끝낼 때마다 갱신 — 멈추면 여기서 이어 감)
- [x] 0 되돌린 넘버링 u = 지금(numApply) + q_backup ②b — PASS(3q·4q)
- [x] 1 그림 주소 한 곳(resolver) — q_img ①~⑦ PASS
- [x] 2 파일 방식(바로 주소 · 실패 → 한 번 다시 → 자리 표시 + [다시] · 인쇄 전 받기) — q_img ①·⑧·⑩ PASS
- [x] 3 묶음 방식 — 강의를 떠나면 그림 묶음 비움(최근 2개) + 묶음을 fetch·JSON으로 읽기 — q_img ⑨ PASS · 힙 측정함
- [x] num.js sanitize(packs/img 주소 → data-lecimg 자리 표시) + 넘버링 강의 그림 두 군데(lecFill·lecWait — 아래) — q_img ⑥⑦ PASS
- [x] 4 qsite 파일 방식 변형(`qsite.filesite`) + q_img.py — **RESULT PASS(OK 56줄 · 약 1분)**
- [x] 회귀(전·후) · SPEC('11-11 W3' 절 — 문서 끝 + 묶음 받기·imgf 줄에 한 줄씩) · 보고 — 끝

## 항목별
(아래에 끝낸 순서대로)

### 0 되돌린 넘버링이 동기화에서 이김(W5 메인 결정 5) — 고침(shell.html `numBump`·`numApply` · 회귀 고리에 numApply·syncMerge3·xsWin)
- 복원 창 '넘버링도 이 시점으로'를 켜고 되돌리기·교체를 하면, 백업 것으로 바뀌는 넘버링 문제(`num.i.*` — 그때 글로 돌아가는 것 + 다시 생기는 것)를 쓸 때 **u = 지금**으로 올려 씀(`numBump` — oldRevive [되살리기]와 같은 규칙 · 만든 때 c·글은 백업 그대로).
  - 옛: 백업의 옛 u 그대로 → 다른 기기에 더 최근에 고친 판이 있으면 '둘 다 바뀜 = 더 최근 u'(`syncMerge3` num.i 가지)에서 그 판이 이겨 되돌린 것이 조용히 원래대로.
  - 밀려난 쪽(다른 기기의 판)은 지금처럼 그 기기의 밀린 판 목록에('다른 기기 동기화로 바뀌기 전' — syncApplyGrp 그대로).
- 안 바꾼 것: 복습 기록(num.r — 늘 합집합 규칙)·회차·과목 정보·시험 날짜는 백업 글자 그대로 · '뒤에 새로 만든 문제가 사라짐'은 지금처럼 키를 지움(다른 기기가 그 문제를 그사이 **고쳤으면** 동기화의 '한쪽은 지우고 한쪽은 고침 = 고친 것' 규칙으로 다시 옴 — 안 고쳤으면 그 기기에서도 지워지고 밀린 판 목록에 남음).
- 테스트: `tools/tests4/q_backup.py` ②b(3q·4q) — 되돌린 문제·다시 생긴 문제 u ≥ 되돌리기 직전 시각 · `syncMerge3(바탕 = 고친 뒤, 이 기기 = 되돌린 판, 그 기기 = 되돌리기 1분 전에 고친 판)` = 되돌린 판(양쪽 어느 기기에서 합쳐도) · 견줌: u를 안 올리면 그 기기 판이 이김 · 다른 창 쓰기(xsWin)도 되돌린 판 · 복습 기록 u는 그대로. **RESULT PASS(OK 68줄 — 옛 58 + 새 10)**.

### 1~3 허브 코드(shell.html — '11-11 W3' 주석) — 고침
- **그림 주소 한 곳**: `imgF(s)`(파일 방식 팩인지 = 팩 imgf) · `imgUrl(s,kind,key)`(① IMGS 메모리 ② imgf 파일 주소 `packs/img/<SID>/<키>.<h8>.webp` · JB `jb<판>-<쪽>.<h8>.jpg` ③ '') · `imgKeys(s,kind)`(메모리 ∪ imgf — 그림 창 쪽 넘김 SEQ) · `chunkOfS(s,kind,key)`(묶음 이름 — 옛 chunkOf는 없앰 · 과목을 인자로) · `imgNeed(s,kind,key,cb,fail)`(파일 방식·메모리에 있으면 바로 · 아니면 needImages).
  - 쓰는 곳: `fillThumbs`(학습·기출·예상·플래시카드·그림빵 탭·미리 보기·JB 카드 쪽 그림) · `openImg`(강의 쪽·JB 원본 쪽 — 파일 방식은 스피너 없이 바로) · `hostImg`(넘버링 host.img — 그림빵 합성·Word) · `mshow`(파일이면 받는 동안 옛 쪽 가림 + 300ms 넘으면 스피너 + 앞뒤 쪽 미리 받기).
- **파일 방식**: `imgSet` — 파일 주소는 `loading=lazy`(카드 그림은 전처럼 FIO 1200px) · 목록에 없는 키 = 지금처럼 그림 빼기 · 실패: 문서에 capture `error` 하나 — 0.8초 뒤 한 번 다시(`?r=`) → 또 실패면 **같은 크기 자리 표시**(SVG — HTML의 width·height 그대로 · '그림을 받지 못했어요 · ↻ 다시' · 새 DOM 없음 = 형광펜 위치 영향 없음) + 알림 `그림을 받지 못했어요 — 인터넷 연결을 확인해 주세요 [다시]`(못 받은 그림 전부) · 자리 표시를 누르면 그 그림만 다시(`imgRetry` — 그림 창을 열지 않음) · 인쇄: `imgEager`(beforeprint·print 매체 — FIO 밀린 것 + lazy 전부 받기 시작) · [인쇄] 단추(jbPrint)는 `imgsReady`(보이는 그림이 다 올 때까지 최대 4초) 뒤 인쇄 창.
- **묶음 방식(3Q 팩)**: `imgEvict`(leaveView 1.2초 뒤) — 최근에 쓴 강의 묶음 2개(`IMGUSE`) + 지금 화면(`img[data-img]`)에 걸린 묶음만 남기고 IMGS·LOADED에서 그 묶음 키 삭제(다른 과목의 JB 원본 묶음도) · 네트워크로 받은 묶음만(`IMGNET` — 단일 파일판은 그대로) · 그림 창이 열려 있거나 넘버링 화면이면 미룸 · 닫힌 그림 창의 SEQ도 비움.
  - **묶음을 fetch로 받아 JSON으로 읽음**(`imgLoad` — 실패 때 1.5초 뒤 한 번 다시·알림은 전과 같음 · 글 꼴이 다르거나 file://이면 전처럼 `<script>`): 측정해 보니 `<script>`로 실행한 묶음은 Chromium이 그 스크립트 원문(묶음 크기 4~8MB)을 페이지가 닫힐 때까지 붙듦(heap snapshot — `V8LocalCompileHintsProducer` → Script → source) → 비우기만으로는 절반만 줄었음.
- 힙(11-04와 같은 길 — 3q 허브에서 PHARM·ANAT 강의 15개 · 학습 탭 그림 다 채움 · GC 뒤 `performance.memory.usedJSHeapSize`): **전(e24335e9) 시작 166 → 15강 뒤 266MB(+100) · 후 166 → 147MB(2강 뒤 143 · 받은 묶음 2개)**. (그림을 다 채우지 않은 흐름: 후 2강 뒤 176 → 15강 뒤 180.)

### num.js(넘버링) — 고침(`lecOfUrl`·sanitize · `lecFill` · `lecWait`) → build_num
- **sanitize**(지시): 붙여 넣은 그림의 src가 이 허브의 `…/packs/img/<SID>/<키>.<h8>.webp|jpg`이고 그 과목 팩 imgf 목록에 있으면 버리지 않고 자리표 `data-lecimg="SID|키"`로(폭·높이 유지 · 그림 글자·주소를 저장하지 않음 · JB 원본 쪽은 키 `jb<판>-<쪽>` → 허브 `hostImg`가 풀어 줌). 다른 곳 주소·목록에 없는 키는 전처럼 버림 · dataURI 그림은 전처럼 둠.
- **지시 밖이지만 q_img가 잡아 고친 것 둘(넘버링의 강의 그림 — 메인 확인)**:
  1. `lecFill` — 넘버링은 문제 HTML을 미리 만들어 조금씩 넣는데(step), 그림이 그보다 먼저 오면 뒤에 들어온 자리표에 그림이 안 붙음(파일 방식은 한 장씩이라 빨라 IMPL 예상 22문제 중 뒤 7문제가 빈 칸 · 묶음 방식도 그 묶음이 이미 받아져 있으면 같은 일) → 넣을 때마다 받아 둔 그림으로 채움(step 두 곳 — 내 넘버링·복습).
  2. `lecWait` — **인쇄·Word에 강의 그림(예상문제 그림·그림빵)이 원래 안 나갔음**(기준 e24335e9 · 묶음 방식 3q 허브에서도 Word에 `[그림]` 22개 · 그림 0): 문제 글 HTML을 처음 그릴 때 것으로 기억(`it._qd`)하는데 그때는 그림이 없어 src가 없음 → 화면은 나중에 채워지지만 인쇄·Word 묶음은 빈 채. → 인쇄·Word 전에 받아 둔 그림을 그 묶음에 넣고 뜰 때까지 기다림(두 곳). 고친 뒤 Word 그림 10 → 32개(`[그림]` 0).
- 3Q 허브(보관)는 넘버링 모듈이 옛 판이라 위 셋은 4Q 허브에만(3Q는 index·num을 다시 낼 때부터 — DONE_W5 메인이 정할 것 1과 같음).

### 4 qsite.filesite · q_img.py
- `tools/tests4/qsite.py` `filesite(rel, sid='IMPL', q='3q')`(끝에 덧붙임 — 다른 함수 그대로): 3q/ 허브 사본 `work/_tmp/qsite/3qf/` · IMPL만 파일 방식(묶음 12개 → `packs/img/IMPL/` 강의 쪽 480장 + JB 원본 쪽 50장 = 22MB · 가장 큰 파일 127KB · 팩 사본에 imgf·imgv 빈 값 · 그 과목 묶음 파일은 사본에 없음) · 다른 6과목은 묶음 링크 · 넘버링 모듈 = 지금 것(docs/num) · 다시 부르면 0.0초(묶음이 그대로면 안 풂).
- `tools/tests4/q_img.py`(새 · full_check의 `tools/tests4/q_*.py`에 저절로 들어감):
  ① 학습 그림(묶음 요청 0 · 주소 = 규칙 · 안 받은 그림도 자리 잡힘·받은 뒤 높이 그대로 · 목록에 없는 키 = 그림 빼기) ② 그림 창(바로 열림 · 범위 전환 쪽 수 = 파일 목록 · ▶◀ · 인용 칩) ③ JB 원본 쪽(대장 단추·JB 카드 단추 · 제목·쪽 수) ④ 미리 보기 [답 보기] ⑤ 그림빵 탭·예상 탭
  ⑥ 넘버링(예상문제 넣기 → 자리표 → 그림 · 그림빵 합성 22/22 · 저장에는 자리표만 · 붙여 넣기 sanitize 3가지 · hostImg JB) ⑦ Word(.docx) 그림 32개 ⑧ 404(요청 2번·둘째 `?r=` → 같은 크기 자리 표시 740×426 → 누르면 다시 · 그림 창도) ⑩ 인쇄 준비(beforeprint 1/113 → 113/113 · print 매체)
  ⑨ 묶음 방식 과목(같은 허브 — PHARM·ANAT 15강): 그림 창이 열려 있으면 안 비움 · 15강 뒤 강의 묶음 2개 · **힙 2강 뒤 154 → 15강 뒤 151MB**(기준 + 여유 30MB 안) · 비운 강의에 다시 가면 다시 받음.

## 빌드
`sync_common` → `num/build_num.py`(docs/num/num.js + NUMV) → `rehub.py`(4Q docs/ — index.html + 4Q 팩 10개 BUILD 글자) → `rehub.py --q 3q --stage`(work/_tmp/hub3q). 확인: `sync_common --check`·`build_num --check`·`rehub --check`·`quarters.py check` 모두 OK · BUILD 007d154b. docs/3q(frozen)는 안 건드림.

## 테스트(하나씩 돌림 · '전' = e24335e9 worktree — 실패한 것만 다시)
| 테스트 | 전(e24335e9) | 후 | 비고 |
|---|---|---|---|
| tests4/q_img(새) | (새 시험 — 옛 허브는 imgf를 모름) | **PASS**(OK 56) | 두 번 돌림(같음) |
| tests4/q_backup(②b 추가) | (새 기대) | PASS(OK 68) | 0번 |
| `JBL_HTTP=1 tools/verify.py`(4Q) | (안 돌림) | PASS | |
| `JBL_Q=3q JBL_HTTP=1 tools/verify.py`(3Q 스테이징) | (안 돌림) | PASS(OK 288) | 7과목 모든 강의·JB 그림 = fetch로 받은 묶음 |
| verify를 파일 방식 사본에(`JBL_Q=3q JBL_HUB_DIR=work/_tmp/qsite/3qf`) | — | PASS | 1a 'IMPL 그림 파일 530개·이름 지문·디코드'(+ 시험 사본의 `_stamp.json`이 '지난 세대 파일 1개' 알림으로 뜸) |
| tests/ux_gbclick · ux_final · ux_u29 · ux2_load | (안 돌림) | PASS(15·20·14·51) | ux_u29 = JB 원본 쪽 묶음·스피너·쪽 넘김 |
| tests/ux20_numdocx · ux8_num · ux9_numai · ux12_numrev · ux21_numyrs | (안 돌림) | PASS(18·65·25·44·9) | 스테이징의 넘버링 모듈을 새 num.js로 바꿔 돌림(끝나고 되돌림) |
| tests/ux10_num5 | FAIL 1(DONE_W5 표) | FAIL 1(같은 줄 '맨 위로') | 원래 실패 |
| tests/ux4_bugs · ux4f_S · ux16_pred · ux17_fig · ux4f_D · ux4f_E | (안 돌림) | PASS(46·32·25·24·65·78) | 그림 창·인쇄·예상 그림·그림빵 |
| tests/kt | FAIL 2 + Timeout | FAIL 2 + Timeout(같은 줄 — 9c·9d·#clock) | 원래 실패 |
| tests/ux2_jbq | FAIL 14 | FAIL 14(같은 줄 — diff 0) | 원래 실패 |
| tests4/q_links · q_stub · q_perf · q_empty · q_ident · q_isolation · q_store · q_sync · q_timer · q_imgbuild | (안 돌림) | PASS(93·84·19·38·14·17·42·38·122·40) | q_links F = 묶음 한 번·두 번 실패(다시 받기·알림) 그대로 |
- q_crawl·q_pos·q_perf2는 아직 없음(테스트 담당 몫) · `ux_all`·audit은 안 돌림(메인).
- 3Q 묶음 81개 전부 fetch가 읽는 글 꼴(`JBLHUB.images('<SID>',{…},'<묶음>');`)임을 따로 확인(꼴 다름 0 — `<script>` 대체 길로 안 감).

## 힙 수치(GC 뒤 `performance.memory.usedJSHeapSize` — 11-04 측정 '129 → 254MB'와 같은 길: 3q 허브 · PHARM·ANAT 강의 15개 차례로 · 학습 탭)
| | 시작 | 2강 뒤 | 5강 | 10강 | 15강 뒤 | 15강 뒤 메모리의 묶음 |
|---|---|---|---|---|---|---|
| 전(e24335e9 · 그림 다 채움) | 166 | 147 | 167 | 211 | **266** | 15 |
| 비우기만(중간 판 · `<script>` 그대로) | 166 | 147 | 156 | 180 | 210 | 2 |
| **후(비우기 + fetch·JSON)** | 166 | 143 | 141 | 144 | **147** | 2 |
- q_img ⑨(파일 방식 사본 허브 안의 묶음 과목): 2강 뒤 154 → 15강 뒤 151~152MB(기준 + 여유 30MB).
- 파일 방식 과목은 그림 글자가 JS에 들어오지 않음(그림 한 장 ≈ 47KB 요청 — IMPL 530장 22MB · 가장 큰 파일 127KB).

## 화면 글(새로 생긴 것)
- 못 받은 그림 자리(그림 안 글): **그림을 받지 못했어요 · ↻ 다시** · 도움말 풍선 '그림을 받지 못했어요 — 누르면 다시 받아요' · 알림 '그림을 받지 못했어요 — 인터넷 연결을 확인해 주세요 [다시]'(묶음 방식의 있던 알림과 같은 글).

## 메인이 정할 것
1. **묶음을 fetch·JSON으로 읽기**(지시문에는 '비우기'만) — 비우기만으로는 절반만 줄어(위 표 둘째 줄 — Chromium이 `<script>` 원문을 붙듦) 받는 길을 바꿈. 실패 처리·알림·주소는 그대로이고 꼴이 다르면 `<script>`로 돌아감. 이대로 둘지(되돌리려면 `imgLoad`의 fetch 가지 한 줄).
2. **3Q 허브 다시 내기**: 비우기·fetch는 묶음 방식(3Q 팩)에만 효과가 있는데 3Q 허브(docs/3q)는 frozen — index를 다시 내야 실제로 듦(사용자 허락 뒤 `JBL_UNFREEZE=1` · DONE_W5 '메인이 정할 것 1'과 한 번에). 4Q는 파일 방식이라 비울 것이 없음.
3. **num.js 지시 밖 고침 둘**(`lecFill`·`lecWait` — 위 num.js 절): 넘버링 인쇄·Word에 강의 그림(예상문제 그림·그림빵)이 원래 안 나가던 것까지 고쳐짐. `guide/넘버링_따기.md`에는 안 적음(맡은 파일 밖 — 한 줄 필요하면 메인).
4. **못 받은 그림 자리 표시 꼴**: 따로 단추를 만들지 않고 자리 표시 그림 안에 글 + 누르면 다시(새 DOM·새 단추 꼴을 안 만들려고 — 형광펜 글자 위치에도 영향 없음) + 알림의 [다시]. 진짜 단추가 낫다면 한 줄.
5. **0번 범위**: u를 올리는 것은 '백업 것으로 바뀌는 문제'(글이 돌아가는 것·다시 생기는 것)뿐. '뒤에 새로 만든 문제가 사라짐'은 키를 지우는 그대로라, 다른 기기가 그사이 그 문제를 **고쳤으면** 동기화 뒤 다시 생김('한쪽은 지우고 한쪽은 고침 = 고친 것' 규칙) · 복습 기록(num.r)은 합집합 규칙이라 다른 기기에 이력이 더 있으면 다시 합쳐짐. 여기까지 '되돌린 쪽이 이기게' 하려면 지움 표시(del + u = 지금 — 휴지통에 보임)·복습 기록 규칙을 따로 정해야 함.
6. **남기는 묶음 수** `IMG_KEEP = 2`(지시대로) · JB 원본 묶음은 '지금 과목 것은 둠 · 다른 과목 것은 비움'으로 함(지시문에 없던 부분).

## 남은 위험
- **파일 방식은 진짜 4Q 그림으로는 못 돌려 봄**(4Q 그림 0장) — 3Q IMPL 묶음을 푼 사본으로만. 첫 4Q 그림 과목을 빌드한 날 `q_img`(사본)와 함께 진짜 허브에서 verify 1a·학습 그림·그림 창·JB 원본 쪽을 볼 것.
- **브라우저 메뉴 인쇄(Ctrl·⌘ P)**: beforeprint에서 받기 '시작'만 함 — 브라우저가 기다려 주지 않으면 아직 안 받은 그림이 빈 칸으로 찍힐 수 있음(자리는 잡힘). JB [인쇄] 단추는 다 올 때까지(최대 4초) 기다림. 묶음 방식은 전과 같음(그림 글자가 이미 메모리에).
- **Chromium에서만 잼**(힙·스크립트 원문 붙듦·자리 표시) — 사파리(아이패드·맥)에서는 못 봄. fetch·JSON 길은 표준 기능만 씀.
- 팩 HTML의 `loading="lazy"` + 파일 주소 → 접힌 곳·가려진 곳의 그림은 보일 때 받음(인쇄 전 `imgEager`가 모두 받게 함).
- 넘버링 모듈이 받아 둔 강의 그림·그림빵 합성 그림(`LECC`)은 넘버링 메모리에 계속 남음(이번 범위 밖 · 파일 방식에서는 주소 글자뿐이라 작음).
- 자리 표시 글은 '그림 작게(72px 띠)'에서는 읽기 어려움 → 도움말 풍선·알림으로 보완.
- 비운 묶음을 다시 받는 것은 브라우저 캐시에 기댐(GitHub Pages `max-age=600` — 10분 뒤에는 다시 확인 요청).
- 단일 파일판(work/)은 손대지 않음(그림이 메모리에 있어 ①로 감 · 비우지 않음) — 이번에 다시 만들어 보지는 않음.
- 비교용 worktree `scratchpad/base_w3`는 끝에 지움.
