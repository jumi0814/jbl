# JBL 과목 팩 제작 스펙 (구강악안면외과학1 → 임상치과보존학에서 확정)

## 폴더 구조 (과목당 한 폴더 — 모든 과목이 같은 스크립트를 쓰고 `subject.py`·`assemble.py`·`parse_<과목>.py`만 다름)
- claude.ai 대화에서 받은 `JBL_master.zip` 반영: `python tools/localize.py <zip>` (경로 변환 + guide/·.claude/commands/ 복사, CLAUDE.md·SPEC.md는 차이만 출력)
- 공통: `tools/jblpaths.py`(저장소 기준 경로 — 스크립트는 여기서만 경로를 얻음) · `tools/jbx.py`(JB PDF → `work/jb/<SID>_20xx/`) · `tools/verify.py`(playwright 허브 검증)
- 경로: 과목 작업 폴더 `work/<SID>/`(jb_blocks.json·강의 쪽 이미지 `lec/`·OCR) · JB 추출 `work/jb/<SID>_20xx/` · 출력 `docs/`(허브 `docs/index.html` + `docs/packs/`) · 단일 파일판 `work/<과목>_JBL.html`(커밋 안 함)
- 파이썬은 3.12 이상(저장소 `.venv/`, f-string 문법 때문에 3.11 불가)
- `subject.py` 과목 설정 — SID·제목·색·교수, LECMAP(강의키 → 이미지 폴더·표시명), LEC_ORDER, PROF_LEC, COVER(기준선 연도), TIERS, MENT_PROF/MENT_ALL(학습부 멘트), PAGE_LABEL, IMG_ALIAS
- `parse_<과목>.py` JB(23·24·25판 ZIP 텍스트) → 문항 블록 (`jb_blocks.json`). JB 구조가 과목마다 달라 여기만 새로 씀
- `assemble.py` 문항 정규화·연도 괄호 파싱·OTHER(판본 간 같은 문제)·주석 병합·JB 쪽 이미지·대장·멘트·예상문제 파싱
- `reflow.py` JB 원문 줄바꿈 정리(글자 불변) · `emph.py` 빨간 핵심어 · `lecparse.py` 정리본 원고 파서 · `trend.py` 짤/탈·형식·전략
- `build2.py` 기출 대장 렌더러 · `build4.py` 팩 조립(정리본·비교표·예상·경향) + 허브·단일 파일판 출력 ← 실행 진입점
- `shell.html` 허브 템플릿(모든 과목 공통) · `annot.txt` 문항 주석 · `lec_<키>.txt` 정리본 원고 · `tables.txt` 비교표 · `pred.txt` 예상문제

## 한 과목 작업 순서
1. `python tools/jbx.py <SID>`로 JB 3판본을 `work/jb/<SID>_20xx/`에 풀고(N.txt + N.jpeg + manifest.json — 텍스트는 pdfium, 쪽 이미지는 폭 924) 전문을 읽어 구조(연도 칸형 / 교수별 괄호형)를 파악 → `parse_<과목>.py` 작성, 블록 수·번호 검증
2. 강의자료: `pymupdf`로 쪽 텍스트·이미지(폭 1100), 텍스트가 부족하면 `tesseract -l kor+eng` OCR. 6슬라이드 핸드아웃은 셀 단위로 잘라 슬라이드 번호로(보존학 WHT). 강의실 촬영본은 슬라이드 사진 영역만 OCR. 텍스트만 온 파일은 그대로 필기본(그림 없음)
3. `subject.py` 채우기 → `assemble.py`의 OTHER·tier·연도 규칙 조정 → `annot.txt`(문항마다 v= / lec= / A: M: N:, 출처 [[키:쪽]])
4. `lec_<키>.txt` 7개 내외(형식은 아래) → `tables.txt`·`pred.txt` → `python3 build4.py` → 검증 출력(연결 누락 0, 없는 문항 0) → playwright로 화면·도구·이미지 확인
5. 출력: `docs/index.html`(허브) + `docs/packs/<SID>.js` + `docs/packs/<SID>.img.<강의>.js`, 단일 파일판 `work/<과목>_JBL.html` → `python tools/verify.py`
   - 강의 쪽 이미지 원본(`work/<SID>/lec/`)이 없으면 지금 `docs/packs/`에 있는 같은 쪽 이미지를 그대로 씀(재빌드해도 그림이 빠지지 않음)

## 공통 코드 동기화·전 과목 빌드 (tools/sync_common.py · tools/build_all.sh)
- 공통 생성 코드(shell.html·build4.py·lecparse.py·trend.py·reflow.py·emph.py·template2.html)는 **tools/cons/에서만 고친다**. SPEC.md는 tools/SPEC.md가 원본
- `.venv/bin/python tools/sync_common.py` — cons → oms1·impl·anat·geri·pharm 복사(SPEC.md 사본 포함) · `--check` 사본끼리 다르면 종료 코드 1 · `--build` 복사 후 6과목 build4 → verify.py → audit_design.py
- `tools/build_all.sh` = `sync_common.py --build --all`(tests/ux_all.py가 있으면 그것까지)
- build2.py는 과목마다 마지막 출력 줄(`J.work('<SID>', 'build2_view.html')`)이 달라 복사하지 않는다 — 고칠 때는 과목별로
- 과목별로 달라야 하는 설정은 subject.py의 선택 항목(`getattr(S, '이름', 기본값)`)으로 — 없으면 기존 동작
- 기준선: work/는 메인 저장소와 공유되어 강의 이미지·강의 이름이 바뀔 수 있으므로, 코드 변경 전후 비교는 "지금 work/로 HEAD 코드를 빌드한 docs/"를 기준으로 한다(빌드는 결정적 — 같은 입력이면 같은 출력)

## lec_<키>.txt 문법
```
#LEC 키 | 제목 | 교수 | 연도 | 파일 설명 | 쪽수
! 머리말(자료 출처·강조 쪽·주의)
@MAP 흐름 → 흐름 → 흐름
@G ① 분류 이름
## 영문 제목 | 국문 부제 | 쪽범위 | 태그 | jb=Q01,Q02
> 한 줄 요지
= 🔑 핵심 한 줄  ({r:빨강} ==형광(시험에 나온 문장)== **굵게**)
# 소제목                                 - 항목 (① ② ③, 영어 뒤 한글 풀이)
| 표 머리 | ... |   | 행 | ... |
E: Q01,Q02 | ⭐ 시험포인트 — 몇 년에 어떻게, 함정 (한 줄에 하나)
P: 💬 교수님 강조      U: ✍ 이해(필기 한 줄)
F: 19=캡션, 20=캡션, 21   (캡션 안에 쉼표 금지; 보조 자료의 쪽은 `DH5:13=캡션`처럼 키를 앞에 — subject.py의 LECMAP에 보조 키와 IMG_ALIAS를 등록)
M: ⚡ 암기 줄({r:} 포함)
```

## 규칙
- 답·해설·정리본은 강의자료와 JB에서만. 근거 없으면 "근거 없음". 자료에 없는 약어·사실 금지. 그림 캡션은 필기에 설명이 있을 때만
- 출제연도 = 괄호 ∪ 문항이 실린 연도 칸 ∪ 다른 연도 칸의 같은 문제. 괄호 파싱은 `(24, 탈)` `(14~)` `(…,13,)` 변형 처리. 실리지 않은 해 금지
- JB 답안 글자 불변(줄바꿈만 정리). 강의자료 26 > 25, 둘 다 있으면 26 본문 + 25 그림/보조 키
- 검증: 현 교수 기출 전부 ⭐ 시험포인트 연결, 문항 id 존재, 이미지 로딩, 형광펜·빈칸·실행취소·새로고침 복원
- JB 분해 검사(verify.py): 답안(.jbans) 안에 '번호. …?/것은/시오'로 끝나는 줄이 있고 바로 앞 번호가 답안에 없으면 '삼켜진 문항' — 6과목 0건이어야 함. 파서가 답안 모드에서 직전 번호+1 문항형 줄을 만나면 블록을 끊고(split), 새 카드 id는 기존 번호 뒤에 붙여 기존 id(채점·표시 키)를 바꾸지 않음(PHARM DS30)

## 렌더링 규칙 (v6, lecparse.render_block — render_key / render_item / render_recall가 호출)
- `split_top(s, ' / ')`: 괄호 밖의 ' / '에서만 분리. 조각 최소 길이 14자 미만이면 분리하지 않음
- `split_circ`: 괄호 밖 ①②③…이 3개 이상이면 (앞머리, 항목들)로 분리 → `<ol class="circ">`
- 🔑(=)·⭐(E:)·💬(P:)는 render_key, 항목(-)은 render_item(80자 초과 시만 ① 분리, 120자 초과·3조각 이상일 때만 ' / ' 분리), ⚡(M:)는 render_recall
- 연속된 E: 줄은 한 `.c-exam` 블록 안의 `<ul class="exlist">`로 합침
- CSS는 shell.html 끝의 `/* ===== v5 가독성·디자인 통일 ===== */` 블록이 이전 규칙을 덮어씀 — 디자인 변경은 이 블록에서

- v6: render_block = split_enum(①·1.·A)) → 라벨 목록('라벨: 내용 / 라벨: 내용') → split_lead+segments → segments(' / ', '; ', ' · ', 문장, '→' 5단계↑는 번호 단계). _rebalance로 ==·{r:} 짝 맞춤. 예상문제 답(a_raw)·정리표 세부·✍ 이해·⭐ 목록에도 적용. CSS는 shell.html의 'v6 가독성' 블록
- 디자인 감사: tools/audit_design.py(명암 대비 3.0 미만·230자 넘는 덩어리·가로 넘침) — 빌드 후 매번 실행

## 허브 도구 v2 (2026-09-26, shell.html)
- 형광펜·빈칸(Kit): 저장 단위 = 카드(data-aid). 기록 {t,x,i,c}. 탭 = 어절(공백·/·()·,;:·→=| 경계, 끝 문장부호 정리), 드래그 = 어절 단위로 넓힌 한 묶음(data-g) — 조각이 여러 개여도 한 번에 열림/지움. 마우스=누른 채 끌기, 펜=바로 끌기, 손가락=0.28초 길게 누른 뒤 끌기(짧은 스와이프는 스크롤). 칠한 곳을 다시 누르면 지움, 다른 색이면 색만 변경. 좌표→글자 위치는 직접 판정(hit)
- 색 키: y 노랑 · g 초록 · p 분홍 · **u 파랑**(#C9DDF7) · o 주황(#FFC98C). 'b'는 빈칸 클래스(.rk-b)와 겹쳐 쓰지 않음 — 옛 기록 {t:'h',c:'b'}는 과목을 열 때 전 과목 c:'u'로 이관(직전 autoBak '파랑 색 키 이관'). 색 CSS는 v6 블록 한 곳(.rk-y/g/p/u/o/n), 빈칸 .rk-b도 v6 블록 한 곳
- 복원: 정확 일치 → 공백·구분기호 무시 느슨한 일치. **찾지 못한 표시는 버리지 않음**: restore가 카드의 B._lost에 모으고 기록에 lost:1을 붙임 → commit = snap(B) + _lost(lost:1). 🧹·되돌리기·색 변경도 lost 항목을 건드리지 않고, 다음 복원에서 찾으면 lost를 뗌. 도구 막대 오른쪽 '⚠ 위치 잃음 N'(0이면 숨김) → 🖍 모아보기의 ⚠ 절(#mk-lost). 버튼·.res 같은 링크의 data-aid는 복원 대상이 아님
- 카드 aid 고정(tools/aidlock.py, tools/<sid>/aid_lock.json — 커밋 대상): build4가 새 카드를 옛 잠금 항목과 맞춤(제목 유사도 0.4 + 문장 Jaccard 0.6 ≥ 0.5면 옛 aid 유지). 카드가 나뉘면 옛 aid는 한 카드의 data-aid + 다른 카드의 data-alt(점수 0.5↑ 또는 새 카드 문장의 절반↑이 그 옛 카드에서 옴), 짝 없는 옛 aid는 가장 비슷한 카드의 data-alt(공백 구분 여러 개). 잠금 항목은 지우지 않고 gone:1로 남김. 빌드 로그 '카드 aid 잠금: 강의 유지·이관·신규'. 원고 파일은 건드리지 않음
- 원고 갱신 이관(허브, 과목을 연 첫 번째에 한 번 — migrateAids): 지금 카드의 aid가 아닌 ann 키와, 다른 카드의 data-alt에도 걸린 aid의 표시를 글자로 찾아 옮김(후보 = 그 aid·alt 카드 → 같은 강의(SID:K:) 카드 중 한 곳에서만 찾히면 그리로 → 아니면 lost:1로 보존, 합집합·중복 제거). ✓ 이해함은 옛 aid가 aid가 아니고 alt에만 있으면 그 카드로. 옮기기 전 autoBak '원고 갱신 전' + 토스트 '표시 N개 중 M개를 옮겼어요 · 못 찾은 K개는 🖍 내 표시 모아보기에'
- 다른 창 동기화: storage 이벤트 — ann.<S>(표시 다시 칠함) · mk.<S>·done.<S>(채점·✓ 다시 칠하고 JB 진행률·사이드바·과목 홈 갱신) · memo(입력칸에 포커스가 없을 때만 새 값) · time/timed. 쓰기는 모두 '직전에 다시 읽고 그 항목만 바꿈': 채점 버튼·O/X·✓, 공부 시간(증가분 ms만 더함), 메모(입력 중 다른 창이 바꿨으면 '— 다른 창의 메모와 합침 —' 구분선으로 합침)
- 채점 기록 mk.<S>는 getMK로 읽음: {ok,ng,bm} 중 없거나 객체가 아닌 칸은 {}(옛 형식 {ok,ng}·깨진 값에서도 ★ 필터·O/X 오류 없음). 복원 합치기도 같은 정규화
- 공부 시간: 자동 측정(기본 켬, 과목을 연 동안만) · 8분 무활동/다른 창이면 멈춤 · 과목·강의별 기록(time, timed) · 시계 누르면 오늘·7일 팝업. 20초마다 저장하되 마지막 입력 뒤 1분까지만 미리 계상(tFlush가 now=min(now, 마지막 입력+60초)) — 무활동이 8분 안에 끝나면 그 사이도 활동이 돌아올 때 더해지고, 8분을 넘기면 마지막 입력+1분까지만
- 그림: 바깥 누르면 닫힘, 그림 누르면 그 자리 확대/맞추기, 드래그 이동, Ctrl+휠, ←/→·스와이프, 아래로 쓸어 닫기, +/- 키
- 안전: 5분마다 자동 백업(최근 5개, autobak.* = {at, why?, data} — 이관 직전 백업은 why가 붙어 복원 창에 표시) · 복원 = 합치기(기본)/덮어쓰기/자동 백업 시점 · navigator.storage.persist · 홈에 백업 경과일 알림
- 편의: 이어서 보기(과목별 마지막 위치), 🖍 내 표시 모아보기(_marks), ? 도움말
- 테스트: tools/tests/kt*.py(도구 — kt_orphan 위치 잃음 보존 · kt_sync 두 창·옛 mk·무활동 · kt_color 파랑/주황 · kt_migrate 원고 갱신 이관), aidlock_test.py(카드 aid 잠금), reg.py·ct.py·gt.py(회귀), audit_design.py(디자인) — 모두 docs/index.html(J.HUB_URL)을 열고 스크린샷은 work/_tmp/

## 허브 화면 골격·이동 v3 (2026-09-27, shell.html)
- 상단 오프셋: ResizeObserver가 #top·#dtabs 높이를 재어 `--toph`·`--tabh`에 넣음 → #side·#dtabs는 `top:var(--toph)`로 고정. (html scroll-padding-top은 U13에서 뺌 — 위에 붙은 막대 안 입력칸을 누르면 페이지가 끌려 올라갔음) 화면 안 이동은 모두 `goEl(el, off)`(요소 윗변을 상단 막대+탭 바로 아래 12px에 둠, off = 요소 안에서 더 내려갈 거리) — openDoc aid·목차(data-scroll)·정리표(data-scroll2)·📖 칩(data-golec)·go()·⚠ 배지
- 아이패드 세로(≤860px): 사이드바 = ☰ 서랍(#side fixed, top:var(--toph)~bottom:0, 폭 min(320px,86vw), translateX 슬라이드) + 반투명 배경 #navbg. 배경·항목 선택·Esc·문서 이동이면 닫힘. 서랍 안은 데스크톱과 같은 세로 목록(읽음·기출 small 유지, .dbtn 44px↑). ☰(#navbtn)는 어두운 바탕(#3F3830)·밝은 글자, 44×40↑, 허브 홈·검색(body.at-home)에서는 숨김. #dtabs는 sticky 유지(탭 글자 13px) + 오른쪽 강의명(.dtname, 최대 30vw 줄임표). 터치 기기(pointer:coarse)는 탭의 숫자키 배지(.kbd) 숨김
- 도구 막대(#kit): `left:0;right:0;margin:0 auto;width:max-content;max-width:calc(100vw - 20px)`로 가운데 한 줄(nowrap). 높이는 ResizeObserver로 `--kith`(막대 높이+14px, 숨기면 ✎ 버튼 몫 56px)에 넣고 `#stage{padding-bottom:calc(var(--kith)+24px)}`·자동 빈칸 창·메모 창이 그 위에 뜸. 860px 이하는 색 견본을 '지금 색 1개 + ▾'(#k-swc)로 줄이고 ▾를 누르면 5색 팝오버(#k-swl), 고르면 닫히고 형광펜이 켜짐. 허브 홈·검색 화면(body.at-home)에서는 #kit·✎·자동 빈칸·메모 창 숨김
- 터치 대상(pointer:coarse): 강의·JB 칩(.chip.lec·.jbchip·.xjb·.cite) 높이 32↑, 읽음 ✓(.dn) 40×40, .tg·.btn 38↑, 도구 막대 버튼 40×40·견본 28×28, 칩 사이 8px. 테스트: tools/tests/ux_u12.py
- 주소·뒤로가기(history): 화면 = VIEW('home'|'search'|'doc'). openDoc(s,d,t,aid,opt)는 문서·탭이 바뀌면 `pushState({s,d,t,aid},'','#/S/문서/탭')`, 같은 화면이거나 opt.push===false면 replaceState. 떠나기 직전 지금 항목에 `{y, pos:{aid,off}}`를 적어 둠(stampHist). popstate·hashchange → route(state||parseHash()) — 뒤로가기·앞으로 가기·해시 직접 수정 모두 화면이 따라옴. 허브 홈 = `#/`(home()도 push), 전체 검색 = `#/?q=…`(과목 한정이면 `&s=SID`, 처음 들어갈 때만 push·입력 중엔 replace). 새로고침은 같은 항목의 state로 스크롤까지 복원(history.scrollRestoration='manual')
- 위치 맞춤(settle): 목표 위치로 옮긴 뒤 1.4초 동안 그림이 늦게 떠서 밀리면 다시 맞춤(그동안 overflow-anchor:none). 휠·터치·키·마우스를 쓰거나 스크롤이 다른 곳에서 바뀌면 즉시 멈춤
- 탭별 읽던 위치: `pos.<S>` = {'문서/탭': {aid, off}} — 기준 = 상단 막대+탭 아래 첫 [data-aid], off = 그 카드 윗변이 기준선에서 올라간 거리. openDoc에 목표가 없으면 (뒤로가기 state → JB 풀이 상태 → pos) 순으로 복원, 없을 때만 맨 위. 과목 홈·내 표시·기출 대장·검색 화면에서는 저장 안 함. 선택된 탭을 한 번 더 누르면 맨 위
- 이어서 보기: lastBy(과목별 1개 — 옛 형식 {s,d,t,aid,at}에 off·ti 추가) + `lastList.<S>`(과목별 최근 3곳, 과목 홈에 표시). 문구 '↪ DD I · 학습 · 7. Two Categories (9/27 13:50)'(강의 약칭 = lecname에서 (26) 같은 괄호 뗀 것)
- JB 풀이 상태: sessionStorage `jbst.<S>.<문서>` = {F, one, curId, shuf(셔플 순서), y, pos} — JB.apply·show·스크롤(800ms)마다 저장, JB.init이 복원하고 필터 버튼·select·검색어·한 장씩·상세 필터 펼침을 되돌림(JB.sync). 사이드바로 다시 들어가도 유지
- ↩ 돌아가기 알약(#retpill): 📖 칩·⭐ 연도칩·기출 칩(xjb)·인용(cite)·go로 다른 화면에 가면 출발점 {s,d,t,curId|pos,label}을 기억('↩ JB 5/68로 돌아가기', '↩ DD I 카드 7로 돌아가기'). 오른쪽 아래 도구 막대 위(bottom: calc(var(--kith)+16px)), 높이 44·과목색 바탕·흰 글자. 누르면 지금 항목이 그 이동으로 생긴 것이면 history.back(), 아니면 openDoc(출발점). 도착 문서를 벗어나거나 출발점으로 돌아오면 사라짐
- 숨은 카드 드러내기 revealCard(el,{open,mark}): JB 카드 = tier 켜기 → 그래도 숨으면 내 필터·검색어 → 교수·강의·횟수·대조 필터 순으로 풀고 한 장씩이면 그 카드로. 정리본 카드 = 그룹 필터·압축 보기·only- 필터 해제 후 펼침. 그다음 goEl·깜빡임. 답은 한눈표(data-src="sum")에서 온 것만 열고, 나머지(정리본·홈·검색)는 가린 채 카드 머리에 '답 바로 보기'(.ansnow)를 3초간 강조
- 🖍 내 표시 모아보기(_marks): 머리 '표시 N · 위치 잃음 M · 메모 K' → ⚠ 위치를 잃은 표시(aidMap에 없는 키 + lost, 강의별, 옛 제목 = 팩의 L.oldTitles(aid_lock의 지금 없는 aid) · [이 과목에서 찾기] = 과목 한정 검색 · [버리기] = 확인 → autoBak('위치 잃은 표시 버리기') → 삭제) → 강의별 표시(칩 = 그 표시 묶음(data-g)을 화면 가운데로·깜빡임(.mkflash), JB 답 안이면 답을 열어 줌) → 📝 메모(memo.<S>.<문서> 앞 120자·[열기] = 그 문서+메모 창). 테스트: tools/tests/ux_nav.py(U07~U10)·ux_marks.py(U06)

## JB 풀이·진행률·학습 위치 v4 (2026-09-27, shell.html·build4.py)
- 진행률 분모(U16): pack.stats = {cards, main(tier A+B), ref(tier C), rep} + pack.refids(tier C id). 허브 과목 카드·과목 홈 진행률·JB 진행 줄(JB.prog)·과목 hero는 main을 분모로 쓰고('현 교수 기출 68문항 — 맞음 n · 틀림 n · 안 푼 것 n'), ref가 있으면 회색 점선 칩 '참고 42 숨김 [보이기]'(.chip.refc, data-reftog = tier C 토글 — 과목 홈에서는 JB 문제로 가서 켬). tier C 카드 채점은 참고 칩에 '· 맞음 a · 틀림 b'로 따로 셈. ref가 0인 과목은 '기출 N문항'(참고 칩 없음). 옛 팩(main 없음)은 cards를 씀(jbCount). 기출 대장 '수록 현황'은 개수 0인 등급을 생략(build2 view_led). 테스트: tools/tests/ux_u16.py
- 기출 한눈표(U19, build4 ans_core·pick_choices): 답 핵심 첫 줄이 보기 번호뿐이면(ANS_NUM — '답: 2)', '답 ③', '답: 2), 4)') 문제 원문(reflow된 qt, 첫 줄=발문 제외)에서 그 번호의 보기 줄('n)'·'(n)'·원문자, 한 줄에 여러 보기면 다음 번호 앞까지, 없으면 'n. ')을 찾아 답 칸 아래 `.ln.pick` '정답 보기 5) …'(발문에 옳지 않은·틀린 것·잘못된·바르지 않은이 있으면 '틀린 보기')로 붙임 — 글자는 원문 그대로(부분 문자열), 번호가 여럿이면 모두. 못 찾으면 `details.pickd` '▸ 보기 펼치기'(문제의 목록 줄 전체). 연도 배지는 nowrap·칸 폭 96px, 연도 5개↑는 '24·23·22 +2'(title에 전체). 테스트: tools/tests/ux_u19.py
- 대조·주변부 자동 구조화(U18, build4 struct_item·astruct·auto_item): annot의 A:·M:·N: 항목(이미 cite_html된 HTML)이 150자를 넘거나 ' / '가 3개 이상이면 인용 칩을 떼어 항목 끝 `.cites` 줄로 모으고 글을 나눔 — 190자 이하는 lecparse.render_block, 넘으면 astruct: ① 깊이 0(괄호·따옴표 밖) 문장('. ', p.·vs.·e.g. 제외) ② ' — '(대시는 뒤 줄 첫머리) ③ ①·1.·A) 나열(split_enum) → ' / '(2↑)·' · '(3↑)·'; '·' → '(3↑) 나열(앞머리 '…:'는 .klead) ④ 괄호·따옴표 안의 나열(가장 긴 묶음, 여는 글자까지 .klead · 닫는 글자는 마지막 항목 끝 · 뒤는 .ktail) ⑤ 가장 긴 묶음 안으로 들어가 다시 나눔(.kin) ⑥ ', '로 140자 안팎씩. 문장·대시·쉼표 조각은 점 없는 줄(.kp), 나열은 점 목록(.klist/.circ). 글자는 그대로이고 나눈 자리의 구분자만 빠짐(검사: tools/tests/annot_text.py --save 전/후 비교 — 공백·/ : ; · , — - = → 제외 글자 다중집합). annot가 없는 문항의 자동 채움은 '✓ 정리본 «카드» 일치'(.agree) + ⭐ 시험포인트 원문(.aex, astruct) + 인용 칩 3개까지(li.auto). audit_design.py가 _jb에서 모든 카드 답을 펼쳐 .ab.chk·.ab.more의 li·div 덩어리(안의 목록·블록·칩 제외한 직접 글)가 230자를 넘는지 셈(CHUNK 줄). 테스트: tools/tests/ux_u18.py
- JB 필터 막대(U15, shell jbBar(p,{lec})): 과목 JB 문제(_jb)와 강의 기출 탭이 같은 막대를 씀 — 강의 탭은 강의 필터를 숨기고(카드가 이미 그 강의뿐) 기본 정렬이 '많이 나온 순'. 첫 줄 = 전체/안 푼 것/틀린 것/★ · 교수(2명↑일 때) · 연도(fyr) · 짤/탈(data-stf) · 정렬(JB 수록 순서/많이 나온 순/최근 출제 순/섞기) · 한 장씩 풀기 · 답 모두 펼치기. 둘째 줄 = 검색(#fq) + 범위 [문제만(기본)·문제+답·전체](data-qs) + 결과 수(#fqn) + 상세 필터(등급 tier·출제 횟수·강의·대조). 카드에는 build4가 data-yrs="24 22"(두 자리 연도)·data-st=jj|tt|base(최근 출제 해의 짤/탈, st_kind) · pack에 jbprofs·jbyears·tcount. 연도를 고르면 정렬을 JB 수록 순서로(섞기 중이면 유지). 검색은 띄어쓰기를 뺀 글자끼리, 영문 낱말 뒤 조사(과·와·을·를·이·가·은·는·의·에·로·으로·도·만)는 뗌('warfarin과' → warfarin). 필터 F = {tiers, prof, lec, n, ver, mine, sort, q, yr, st, qs} — U08 풀이 상태(jbst)에 함께 저장. #jbbar는 `position:sticky; top:calc(var(--toph)+var(--tabh))`, 앞의 #jbsent가 위로 지나가면 .mini(첫 줄 + 3px 진행 막대만, 검색 중이면 검색 줄 유지). 붙은 막대 높이(첫 줄+34px)는 `--jbh`(LAY.jbh)로 재어 goEl·probePos가 그 아래로 맞춤. 860px 이하는 '한 장씩'·'답 펼치기'로 줄이고 select 폭 6.8em. 강의 hero의 '✓12 ✗4'(#hstat, hstat()). 테스트: tools/tests/ux_u15.py
- JB 카드 무게(U17 — 카드 순서는 그대로): reflow.render(at, ans=True)가 첫 '답' 라벨 줄에 `.ans0`(18px·800·흰 칸), 첫 '해설' 라벨부터 끝까지를 `.exw`로 감싸고 해설이 6줄 또는 400자를 넘으면 `.exw.clamp`(max-height 9.5em + 아래 그라데이션) + '해설 전체 보기 ▾'(data-exmore, 섹션 .full). '참고:' 줄은 13px·var(--sub). 글자는 그대로(reflow의 same_chars 단언). 답 칸의 '📖 정리본 카드' 절은 `<details class="ab lk">`(기본 접힘) — 머리 '📖 «카드 제목» · ⚡ 암기 첫 줄 · [카드로 이동 →]'(넓은 화면 1줄·좁은 화면 2줄 말줄임), 펼치면 🔑 앞 5항목 + '더 보기 (+N)'(lkCut)·⚡ 전부. 펼침 선호는 머리를 직접 누를 때만 LS 'lkopen'에 저장(카드로 이동 버튼은 펼치지 않음). 카드 머리 대조 칩(vchip): 일치 = 11.5px 테두리 칩 '✓ 대조', 부분 일치·불일치 = 글자 그대로, 근거 없음·자료 없음 = 짧게(title에 전체). '문제 집중'(#ffocus, LS 'jbfocus', 기본 끔)을 켜면 답을 펼치기 전까지 📖 칩과 출처 줄(.qsub)을 숨김. revealCard로 표시를 찾아가면 접힌 해설·🔑를 펼침. 테스트: tools/tests/ux_u17.py(PHARM RX01 펼친 높이 1483 → 861px, 42% 감소)
- 한 장씩 풀기(U14): 풀이 막대(#onebar)는 `position:fixed; bottom:0; padding-bottom:env(safe-area-inset-bottom)`(넓은 화면은 사이드바 오른쪽부터) — [◀][답 보기/답 가리기 ▲][✗ 틀림][✓ 맞음][★][▶] '12/155' + '자동 넘김'(LS 'jbauto', 기본 켬) + 키 안내(hover:hover·pointer:fine 기기만). 버튼 48×56↑. 켜져 있는 동안 body.jbone(`--oneh:72px`) → 도구 막대·✎·↩ 알약·자동 빈칸·메모 창이 그만큼 위로, `#stage.single` 아래 여백 = --kith + 140px. 막대의 ✓/✗와 O/X는 '설정'(누르면 항상 그 상태, 해제는 카드의 맞음/틀림 버튼 = 토글) → 자동 넘김이면 0.25초 뒤 다음. 채점할 때마다 mark(id,k,how)가 mk.<S>.log[id]에 {r:'ok'|'ng', t}를 최근 10개까지(ok·ng·bm 형식은 그대로 — 옛 기록 호환, 복원 합치기는 log도 t 기준 합집합) → 카드 머리 기록 칩 '✗2 ✓1'(.chip.rec, paintQ). 카드 영역 좌우 스와이프(|dx|>70·|dy|<50, 형광펜·빈칸 모드 꺼짐, 표·그림 제외)로 넘김. cur = 0…n-1 문제, n = 회차 요약(#onesum: '이번 회차 n — ✓ · ✗ · 안 채점' + [틀린 것만 다시](F.mine='ng') [안 채점만](todo) [처음부터]) — 회차 기록 JB.sess는 풀이 상태(jbst)의 sess. 섞기 순서는 정렬에서 '섞기'를 고를 때만 만들고 jbst.shuf에 저장. 목록 모드는 답 끝(다른 판본 앞)에 .acts2 [✓ 맞음][✗ 틀림][★][답 접기 ▲](답 접기 = 닫고 카드 머리로). 답 토글 글자는 펼치면 '답 가리기 ▲'(togLabel). '답 모두 펼치기'는 모든 카드에 .open을 더하고 빼는 방식(개별 토글 유지). 긴 해설의 '해설 전체 보기'는 접힌 해설 아래쪽에 겹쳐 띄움. 테스트: tools/tests/ux_u14.py
- 강의 안 위치(U13): 학습 탭에서만 #dtabs 오른쪽 끝(sticky right:0)에 미니바 #lmini = '카드 7/19 ▾'(#lmcur) · 압축(#lmcond, 정리본의 '압축 보기'와 같은 상태 — condSet) · '↑ 틀'(이 강의의 틀로). 미니바가 있으면 .dtname(강의명)은 숨김. 지금 카드 = 화면 위 30% 선에 걸친 .tc(IntersectionObserver rootMargin '-30% 0px -70% 0px', learnSpy/setLCur) — 목록·J/K로 옮긴 직후 0.9초는 관찰 무시(LHOLD). ▾ = #lpop(.pop 재사용): 번호·국문 제목·✓읽음·⭐기출 수, 지금 카드 강조, 누르면 goCard(j)(숨은 카드면 revealCard, 아니면 펼치고 탭 아래로). 넓은 화면(>860)은 사이드바의 지금 강의 아래 접이식 카드 목록(details.scards, LS 'sidecards' 기본 펼침 · 스크롤 스파이로 .on 굵게 · 다른 탭에서 누르면 학습 탭 그 카드). 키보드 J/K = 다음/이전 카드(입력칸 포커스면 무시). 데이터: pack.lect[].cards = [[aid, 번호, 국문 제목, 기출 수]](build4). 테스트: tools/tests/ux_u13.py
