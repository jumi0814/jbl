export const meta = {
  name: 'jbl-ux4-impl',
  description: '허브 4차 구현 — 묶음 1(오류 55건·도구 토글·뺄 것, main) ∥ 묶음 2(허브/과목 두 단계 메뉴·상단 시계, worktree) → 병합 → 묶음 3(토큰·전체 화면 정리)',
  phases: [
    { title: 'Tracks', detail: '묶음 1 ∥ 묶음 2' },
    { title: 'Merge', detail: 'ux4m → main' },
    { title: 'Screens', detail: '묶음 3' },
  ],
}
const DONE = {
  type: 'object',
  properties: {
    implemented: { type: 'array', items: { type: 'string' } }, skipped: { type: 'array', items: { type: 'string' } },
    tests: { type: 'string' }, commit: { type: 'string' }, notes: { type: 'array', items: { type: 'string' } },
  },
  required: ['implemented', 'tests'],
}
const MAIN = '/Users/jumisong/JBL', WM = '/Users/jumisong/JBL-ux4m'
const REQ = `사용자 요청(원문): ① "내가 한 과목에 들어가면 메뉴탭이 허브 홈페이지의 메뉴탭이랑 달라지게, 해당 과목의 메뉴탭에 대한 메뉴탭으로 specify되게끔 해주고, 전반적으로 좀 난잡한데, 가독성 좋고 조금 더 깔끔하게 가장 최적 효과적 효율적으로 홈페이지, 과목별 페이지 및 메뉴탭 등등을 전면적 개선해줘!" ② "집중모드는 너무 좋지만 집중모드와 별개로 하이라이트, 빈칸빵 등의 도구창 토글 버튼은 따로 있었으면 좋겠고, 형광펜 및 빈칸빵 켜짐 이라는 안내탭은 없어도 될 것 같아. 그리고 암기에서 각각 모든 줄에 Ox이건 필요 없을 것 같아서 없애줘. 그리고 집중모드로 토글되면서 화면이 중앙에서 치우쳐진 상태가 되는 오류, 표시 지우기에 이 카드만 이 탭만 이게 클릭되더라도 안지워지는 오류 등등 크고 작은 오류들이 많은데 면밀히 검토하면서 홈페이지, 과목탭, 각 강의자료 정리본, 정리표 등 모든 것에서 모든 오류들을 찾고 최적으로 효과적 효율적으로 개선해줬으면 좋겠어. 더불어서 시험일 표시는 안해도 되고, 정리본 읽음, 퍼센트 이런건 필요 없어. 그냥 가장 최적으로 가독성 좋고 깔끔하게 허브 홈페이지 및 과목별 탭페이지를 정리해줬으면 좋겠어." ③ (재강조) "위 지시사항을 모두 잘 수행하도록 하고 오류 또한 면밀히 빠짐없이 검토" ④ 쉬는 시간: "내가 공부하다가 멈추고 쉬면 쉬는시간 타이머도 함께 기능하게끔 hub html 참고해서 보완" — 상단 시계 하나로 모으더라도 쉬는 중에는 휴식 타이머가 흘러가며 보여야 한다.`
const BASE = (root) => `JBL 허브 = 치의학대학원 3학년 3쿼터 시험 대비 학습 사이트(6과목, 곧 ESTH). 사용자는 아이패드(세로 820·가로 1180, 펜슬·손가락, 하드웨어 키보드 — 한글 입력 상태일 수 있음)와 맥(1280)에서 GitHub Pages로 공부한다. 사용자의 실제 저장 데이터(형광펜·빈칸·채점·공부 시간·메모)가 있다.
${REQ}
4차 설계·계획: work/ux4_plan.json(decisions·visual_system·menus·screens·batches — 묶음 1·2·3 항목마다 what·acceptance·files), 최종 시안: work/_tmp/ux4_final/{home,subject,lecture}.html·final.css·shots/v2_*.png(직접 열어 보고 그대로 구현 — 1280·820), 오류 목록: work/ux4_bugs.json(정리된 51건 — high 10·medium 21·low 20, 각 repro·cause·fix·redesign_overlap). 반드시 이 세 가지를 모두 읽고 시작.
파이썬 ${root}/.venv/bin/python, playwright. 코드 원본 ${root}/tools/cons/{shell.html, build4.py, lecparse.py, trend.py} → .venv/bin/python tools/sync_common.py 로 6과목 복사. 빌드·검증: sh tools/build_all.sh(6과목 빌드 → verify → audit_design → tests/ux_all.py, 약 50분 — 개발 중에는 6과목 build4 뒤 관련 테스트만, 묶음 끝에 build_all). 한 과목만 다시 빌드하면 stale — 테스트 전 6과목 모두 빌드. 허브 문서 tools/SPEC.md, 원칙 guide/정리본_원칙.md 7-1, CLAUDE.md '페이지 구성'(과목 홈 순서·강의 탭·JB 내부 순서 유지 — 단 시험일·읽음 %는 화면에서 뺌).
지킬 것: ① localStorage 키·형식 하위 호환(새 키·이관만, 삭제·덮어쓰기 금지 — exam.<S>·done·fc 등 값은 두고 화면에서만 뺌). ② 원고(lec_*.txt·annot·tables·pred) 수정 금지. ③ 카드 textContent 보존(숨김은 CSS — legacy_restore·legacy_restore_107 통과 유지). ④ 기능은 없애지 않음(요청으로 뺄 것만 — 시험일 표시·읽음 %·모드 칩·켜짐 안내·⚡ 줄마다 ○✕). ⑤ 항목마다 수용 기준을 playwright로 직접 확인(스크린샷 ${root}/work/_tmp/ux4i_*.png를 Read로, 1280x900·820x1180·1180x820 has_touch). ⑥ 회귀 테스트 추가·갱신(기존 테스트가 지운 요소를 찾으면 새 구조로 갱신 — 테스트를 약하게 만들지 말 것). ⑦ SPEC·도움말 갱신. ⑧ 고친 단위로 git add tools && git commit(한국어, 항목 id로 시작, 끝에 "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"). docs/ 커밋·push 금지. ⑨ 기계가 CPU 8·메모리 8GB이고 다른 구현자가 동시에 브라우저 테스트를 돌릴 수 있다 — 브라우저는 쓰고 바로 닫고, 시간 초과로 보이는 실패는 한 번 더.`
phase('Tracks')
const [b1, b2] = await Promise.all([
  agent(`작업 위치: 본 저장소 ${MAIN} (main). ${BASE(MAIN)}

## 역할: 구현자 — ux4_plan.json '묶음 1'(B1-1~B1-8) 전 항목 + ux4_bugs.json의 오류 전부(redesign_overlap이 묶음 2·3 몫인 메뉴·홈 구조 항목은 그 묶음에 맡기고 notes에 목록)
특히: B1-1 도구 막대 토글 버튼(✎ 도구 · T — 집중 모드와 따로, LS kitoff 하나) · B1-2 집중 모드 가운데 정렬(오른쪽 58px 여백 원인) · B1-3 🧹 지우기 '이 카드/이 탭' 실제로 지워지게(2단계 팝오버) · B1-4 모드 칩·켜짐 안내 삭제 · B1-5 ⚡ 암기 줄마다 ○✕ 삭제(학습·복습 보기 모두) · B1-6 시험일·정리본 읽음 % 화면에서 빼기 · 오류 high 10·medium 21·low 20.
동시 작업: 다른 구현자가 worktree ${WM}(브랜치 ux4m)에서 묶음 2(허브/과목 두 단계 메뉴 navRender·상단 막대 밝게·빵부스러기·검색 범위·공부 시계 하나로·서랍·M)를 한다 — 그 영역(navRender·#nav·#top·시계 알약·tPop)은 건드리지 말 것. 새 CSS는 shell.html <style> 끝의 새 블록 '/* ux4 묶음1 */'에, 새 JS는 '// ux4 묶음1' 구역에(기존 함수는 필요한 줄만).
먼저 git log --oneline -6 · git status. 끝나면 sh tools/build_all.sh RESULT PASS. 결과(JSON): 구현한 것(항목·오류 id별), 건너뛴 것과 이유, 테스트, 마지막 커밋, 병합자·다음 묶음에 넘길 메모.`, { label: 'ux4:묶음 1', phase: 'Tracks', schema: DONE, effort: 'high' }),
  agent(`작업 위치: git worktree ${WM} (브랜치 ux4m) — 모든 셸 명령은 'cd ${WM} && …'로, 파일 읽기·수정은 ${WM}/… 절대 경로로만. ${MAIN}(main)은 다른 구현자가 묶음 1(오류 55건·도구 토글·뺄 것)을 동시에 작업 중이니 절대 고치지 말 것(git 명령도 ${WM}에서만). work/의 하위 폴더는 공유(심볼릭 링크) — 거기에 쓰지 말고 스크린샷·임시 파일은 ${WM}/work/_tmp/에. ${BASE(WM)}

## 역할: 구현자 — ux4_plan.json '묶음 2'(B2-1~B2-7) 전 항목: navRender 허브/과목 분기(VIEW==='doc'&&CUR.s → 과목 메뉴: ‹ 허브 홈·과목 머리·[과목 바꾸기]·이 과목 문서 7개(글자 2열)·강의 7(교수명 흐리게, 읽음 없음)·지금 강의 카드 목차(기출 노란 점)·바닥 백업·도움말·M) / 허브 메뉴(오늘·공부 달력·내 표시·과목 7줄 — 읽음 %·시험일·▸ 없음), 상단 막대 밝게·빵부스러기(JBL / 과목 / 강의)·과목 안 검색 범위, 공부 시계 하나로(상단 알약 — 상태 점 회색 대기·과목색 측정·금색 휴식 + 시간 + '공부 중/휴식 3:10/대기', 쉬는 중에는 휴식 구간 타이머가 흘러감, 누르면 팝오버 멈춤·쉬기·크게 보기·달력·목표 — 메뉴 트래커·상단 자동 대기 칩·홈 ⏱ 크게는 이리로), 서랍(≤860)·M 숨기기(>860) 정리, 전환 규칙·스크롤 기억, 도움말·SPEC·회귀.
과목 홈·강의 화면 본문·도구 막대·지우기·집중 모드·시험일/읽음 % 제거(묶음 1)와 색·글자 토큰·홈 본문 재구성(묶음 3)은 건드리지 말 것. 새 CSS는 '/* ux4 묶음2 */' 블록에, 새 JS는 '// ux4 묶음2' 구역에.
먼저 cd ${WM} && git log --oneline -6 · git status. 끝나면 sh tools/build_all.sh RESULT PASS. 결과(JSON): 구현한 것, 건너뛴 것과 이유, 테스트, 마지막 커밋, 병합자에게 넘길 메모(바꾼 함수·새 LS 키·계약).`, { label: 'ux4:묶음 2', phase: 'Tracks', schema: DONE, effort: 'high' }),
])
phase('Merge')
const merge = await agent(`작업 위치: 본 저장소 ${MAIN} (main). ${BASE(MAIN)}
## 역할: 병합자 — 브랜치 ux4m(worktree ${WM}, 묶음 2 메뉴·상단 시계)를 main(묶음 1 오류·도구 토글·뺄 것)에 병합
1) 두 작업 트리 모두 docs/ 외 미커밋 변경이 없는지 확인(있으면 그 작업 트리에서 알맞게 커밋). 2) cd ${MAIN} && git merge --no-ff ux4m -m "병합: 묶음 2(허브/과목 두 단계 메뉴·상단 시계 하나로)" — 두 쪽 기능을 모두 살려 충돌 해결, 다른 과목 사본은 sync_common.py로. 도움말·SPEC은 두 쪽 모두. 겹치는 동작(도구 토글 버튼 위치·집중 모드와 메뉴·M·서랍) 계약 확인. 3) sh tools/build_all.sh RESULT PASS까지.
묶음 1 보고: ${JSON.stringify(b1).slice(0, 9000)}
묶음 2 보고: ${JSON.stringify(b2).slice(0, 9000)}
결과(JSON): 해결한 충돌, 병합 후 고친 것, 테스트, 병합 커밋.`, { label: 'ux4:merge', phase: 'Merge', schema: DONE, effort: 'high' })
phase('Screens')
const b3 = await agent(`작업 위치: 본 저장소 ${MAIN} (main). ${BASE(MAIN)}

## 역할: 구현자 — ux4_plan.json '묶음 3'(B3-1~B3-7) 전 항목: 색·글자·간격 토큰 교체(최종 시안 final.css 수치), 허브 홈 재구성(날짜·오늘 시간 막대·멈춤/쉬기·휴식 0:12 → '계속하기 →' 주 버튼 → 오늘 할 일·최근 → 과목 표(기출 푼 것·틀림·오늘·전체 시간) → 이번 주 → 바닥 한 줄, 시험일·읽음 % 없음), 과목 홈 재구성(순서 유지, 시험일 줄·읽음 % 없음, 교수별 출제 경향 표), 강의 머리·탭 줄(글자 탭·개수 흐리게·이모지/번호 배지 없음)·미니바 4개([카드 n/19 ▾][보기 ▾][✎ 도구][⤢ 집중]), 이 강의의 틀·카드 머리(⭐ 기출 칩 하나·✓ 다 봄은 카드 끝)·블록 스타일, JB·정리표·비교표·예상·달력 크롬 통일, 전 과목 재빌드·세 뷰포트 최종 확인. 최종 시안 스크린샷(work/_tmp/ux4_final/shots/v2_*.png)과 나란히 비교하며 맞춘다.
먼저 git log --oneline -15 · git status. 앞 보고: ${JSON.stringify({ b1, b2, merge }).slice(0, 14000)}
끝나면 sh tools/build_all.sh RESULT PASS. 결과(JSON): 구현한 것, 건너뛴 것과 이유, 테스트, 마지막 커밋, 오류 조사자에게 넘길 메모(바뀐 화면·선택자·새 LS 키).`, { label: 'ux4:묶음 3', phase: 'Screens', schema: DONE, effort: 'high' })
return { b1, b2, merge, b3 }
