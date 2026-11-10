먼저 /home/user/jbl/guide/handoff/upg1110/BRIEF_공통.md 를 끝까지 읽고 그대로 따른다(메인 저장소에서 일하는 '허브 담당' — 커밋 금지).

묶음 **W3 허브 쪽 — 4Q 그림을 파일로 읽기**. 읽기: guide/handoff/upg1110/R_DESIGN_설계.md §3(허브 절) · guide/handoff/upg1110/DONE_빌드.md(빌드 담당이 정한 주소 규칙·imgf 꼴 — 이것이 기준) · tools/SPEC.md 이미지 절 · shell.html의 needImages·fillThumbs·openImg·chunkOf·imgSet·JBLHUB.images·host.img(넘버링에 주는 그림)·gbCompose(그림빵)·인쇄 길.
맡은 파일: tools/cons/shell.html · tools/num/num.js(sanitize — 붙여 넣은 packs/img 주소 그림을 data-lecimg 자리 표시로) · 새 tools/tests4/q_img.py · tools/tests4/qsite.py(fixture에 '한 과목을 파일 방식으로 바꾼 사본' 변형만 — 다른 함수는 건드리지 않음) · tools/SPEC.md · 보고 guide/handoff/upg1110/DONE_W3_허브.md.
할 일:
1. 그림 주소 한 곳(resolver): 그림 키 → ① 이미 메모리에 있으면 그것(IMGS — 단일 파일판·묶음) ② 팩에 `imgf`가 있으면 파일 주소(빌드 담당 규칙) ③ 아니면 지금 묶음 길(needImages). fillThumbs·openImg(쪽 넘김 SEQ도 imgf 키에서)·host.img·그림빵 합성·미리 보기(peek)·플래시카드가 전부 이 함수로.
2. 파일 방식: 묶음을 기다리지 않고 바로 주소 · 실패(error)면 한 번 다시(캐시 피해서) → 또 실패면 같은 크기 자리 표시 + [다시](폭·높이는 HTML에 있어 화면이 안 밀림) · 목록에 없는 키는 지금처럼 그림 빼기 · 인쇄 전(beforeprint) 아직 안 받은 그림 받기.
3. 묶음 방식(3Q 팩): 강의를 떠나면 그 강의 그림 묶음을 메모리에서 비움(최근 2개만 — LOADED·IMGS[s]에서 그 묶음 키 삭제, 다시 가면 다시 받음 · 열린 그림 창·미리 보기·넘버링이 쓰는 중이면 두기) — 11-04 측정 '강의 15개 뒤 129 → 254MB'가 늘지 않게.
4. q_img.py: fixture의 한 과목을 파일 방식으로 바꾼 사본(qsite — 묶음 js에서 그림을 파일로 풀고 팩 사본에 imgf 넣기)에서 학습 그림·그림 창 쪽 넘김·JB 원본 쪽·미리 보기·그림빵·넘버링에 강의 그림 넣기·Word 내보내기(그림 포함) · 파일 하나 404 → 다시·자리 표시 · 묶음 방식 과목에서 강의 15개 뒤 힙이 기준 + 여유 안 · 인쇄 준비.
회귀(전·후): tools/verify.py(4Q·3Q 스테이징) · ux_gbclick · ux20_numdocx · ux8_num · ux_final(교과서 쪽 그림) · ux_u29 또는 JB 원본 쪽을 보는 테스트(grep data-jb) · ux2_load · tests4 q_crawl·q_pos·q_perf·q_perf2(있으면).
끝나면 마지막 메시지에: 항목별 고침/안 함 · 테스트 전·후 · 힙 수치 · 메인이 정할 것.
