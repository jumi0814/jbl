export const meta = {
  name: 'jbl-ux4-design-bugs',
  description: '허브 4차 — 설계 시안 3개(과목 전용 메뉴·깔끔하게·없앨 것) ∥ 오류 전수 조사 4영역 → 종합(최선안·구현 계획) ∥ 오류 목록 정리',
  phases: [
    { title: 'Explore', detail: '시안 3 ∥ 오류 조사 4' },
    { title: 'Synthesize', detail: '설계 종합 ∥ 오류 정리' },
  ],
}
const SPEC = {
  type: 'object',
  properties: {
    direction: { type: 'string' },
    clutter_audit: { type: 'array', items: { type: 'string' } },
    menus: { type: 'string' }, home: { type: 'string' }, subject_pages: { type: 'string' }, visual_system: { type: 'string' },
    remove_merge: { type: 'array', items: { type: 'string' } },
    mockups: { type: 'array', items: { type: 'string' } },
    risks: { type: 'array', items: { type: 'string' } },
  },
  required: ['direction', 'clutter_audit', 'menus', 'home', 'subject_pages', 'visual_system', 'mockups'],
}
const BUGS = {
  type: 'object',
  properties: { bugs: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, area: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] },
    problem: { type: 'string' }, repro: { type: 'string' }, evidence: { type: 'string' }, cause: { type: 'string' }, fix: { type: 'string' },
  }, required: ['id', 'area', 'severity', 'problem', 'repro', 'fix'] } } },
  required: ['bugs'],
}
const PLAN = {
  type: 'object',
  properties: {
    scores: { type: 'array', items: { type: 'string' } },
    decisions: { type: 'array', items: { type: 'string' } },
    visual_system: { type: 'string' }, menus: { type: 'string' }, screens: { type: 'string' },
    final_mockups: { type: 'array', items: { type: 'string' } },
    batches: { type: 'array', items: { type: 'object', properties: {
      name: { type: 'string' },
      items: { type: 'array', items: { type: 'object', properties: {
        id: { type: 'string' }, title: { type: 'string' }, what: { type: 'string' }, acceptance: { type: 'string' }, files: { type: 'string' },
      }, required: ['id', 'title', 'what', 'acceptance'] } },
    }, required: ['name', 'items'] } },
    data_compat: { type: 'array', items: { type: 'string' } },
    user_facing_summary: { type: 'string' },
  },
  required: ['decisions', 'visual_system', 'menus', 'screens', 'final_mockups', 'batches', 'user_facing_summary'],
}
const TRI = {
  type: 'object',
  properties: { bugs: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, area: { type: 'string' }, severity: { type: 'string' }, problem: { type: 'string' }, repro: { type: 'string' }, cause: { type: 'string' }, fix: { type: 'string' }, merged_from: { type: 'string' }, redesign_overlap: { type: 'string' },
  }, required: ['id', 'severity', 'problem', 'fix'] } }, summary: { type: 'string' } },
  required: ['bugs', 'summary'],
}
const REQ = `사용자 요청(원문, 최근 두 개): ① "내가 한 과목에 들어가면 메뉴탭이 허브 홈페이지의 메뉴탭이랑 달라지게, 해당 과목의 메뉴탭에 대한 메뉴탭으로 specify되게끔 해주고, 전반적으로 좀 난잡한데, 가독성 좋고 조금 더 깔끔하게 가장 최적 효과적 효율적으로 홈페이지, 과목별 페이지 및 메뉴탭 등등을 전면적 개선해줘!" ② "집중모드는 너무 좋지만 집중모드와 별개로 하이라이트, 빈칸빵 등의 도구창 토글 버튼은 따로 있었으면 좋겠고, 형광펜 및 빈칸빵 켜짐 이라는 안내탭은 없어도 될 것 같아. 그리고 암기에서 각각 모든 줄에 Ox이건 필요 없을 것 같아서 없애줘. 그리고 집중모드로 토글되면서 화면이 중앙에서 치우쳐진 상태가 되는 오류, 표시 지우기에 이 카드만 이 탭만 이게 클릭되더라도 안지워지는 오류 등등 크고 작은 오류들이 많은데 면밀히 검토하면서 홈페이지, 과목탭, 각 강의자료 정리본, 정리표 등 모든 것에서 모든 오류들을 찾고 최적으로 효과적 효율적으로 개선해줬으면 좋겠어. 더불어서 시험일 표시는 안해도 되고, 정리본 읽음, 퍼센트 이런건 필요 없어. 그냥 가장 최적으로 가독성 좋고 깔끔하게 허브 홈페이지 및 과목별 탭페이지를 정리해줬으면 좋겠어." (앞서: "너가 최적으로 판단해서 알아서 가장 최고의 내게 최적의 jbl을 만들어주면 돼")`
const CTX = `저장소 /Users/jumisong/JBL (읽기 전용 — tools/·docs/는 고치지 말 것. 내 파일은 work/_tmp/ux4_<내 이름>/ 에만). JBL 허브 = 치의학대학원 3학년 3쿼터 시험 대비 학습 사이트(6과목 OMS1 구강외과1·CONS 보존·IMPL 임플란트·ANAT 두경부해부·GERI 노인치과·PHARM 약물치료, 곧 ESTH 심미). 사용자는 아이패드(세로 820·가로 1180, 펜슬·손가락, 하드웨어 키보드 — 한글 입력 상태일 수 있음)와 맥(1280)에서 공부한다.
지금 빌드: docs/index.html(허브 원본 tools/cons/shell.html, 팩 docs/packs/*.js) — 3차 배포본 + 쉬는 시간 타이머 보완·과목 색 통일(9816dc9·80c55e8). playwright(/Users/jumisong/JBL/.venv/bin/python)로 file:///Users/jumisong/JBL/docs/index.html 을 세 뷰포트(1280x900 · 820x1180 has_touch · 1180x820 has_touch)로 열어 직접 본다(해시만 바꾸면 안 바뀔 수 있으니 about:blank → URL, localStorage 키 접두 jblhub.v1.). 지금 구조: 모든 화면에 같은 전역 왼쪽 메뉴(트래커·🏠 오늘·📅 공부 달력·🖍 내 표시·↪ 이어서·과목 7줄 — 펼치면 문서 칩·강의 줄·카드 목차) + 상단 막대 + 허브 홈 '오늘' 대시보드(오늘 띠·이어서·오늘 할 일·과목 한눈표(시험일·읽음 %·기출 맞/틀·시간)·이번 주) + 과목 화면(과목 홈, 강의 탭 학습/정리표/비교표/기출/예상/플래시카드, 미니바, 도구 막대 #kit — 형광펜·빈칸·자동·되돌리기·메모·전체 보기·🧹 지우기, 모드 칩, V 집중 모드, Q 가리기, R 복습 보기 ⚡ 줄마다 ○✕, M 메뉴 숨기기). 기능·단축키: tools/SPEC.md, 도움말(?). 과목 홈·강의 탭·JB 내부 구성 원칙: CLAUDE.md '페이지 구성'(단, 이번 요청대로 시험일·정리본 읽음 %는 화면에서 뺀다). 디자인 원칙: guide/정리본_원칙.md 7-1(색 절제·대비·줄간격 — 과거 지적 "가독성 떨어짐·색 눈아픔·규칙 없는 나열"). 사용자가 쓰던 허브: reference/HUB_지난학기.html·materials/HUB.html(차분하고 깔끔한 톤·왼쪽 메뉴·오늘 공부·달력·트래커 — 참고).
${REQ}
기능은 없애지 않는 것이 기본(요청으로 뺄 것만 뺌 — 시험일 표시·읽음 %·모드 칩·⚡ 줄마다 ○✕). 저장 데이터(exam.<S>·done·fc 등)는 지우지 않고 화면에서만 뺀다.`
const DIRS = [
  ['calm', '차분한 편집 디자인', '여백·글자 위계·선 최소화로 조용한 화면. 색은 과목색 한 점과 강조 하나만. 참고 HUB 톤.'],
  ['task', '공부 흐름·정보 밀도', '지금 할 일과 다음 행동이 가장 먼저. 크롬(버튼·칩·배지) 수를 절반 이하로, 한 화면에 한 가지 주 행동.'],
  ['touch', '아이패드 우선', '세로 820·가로 1180 손가락/펜슬 기준. 메뉴는 서랍·레일, 버튼은 크고 적게.'],
]
const AREAS = [
  ['hub', '허브 홈·왼쪽 메뉴·상단 막대·검색·📅 공부 달력·통계·트래커(▶/☕/■·자동 측정·자동 휴식·되묻기 띠·⏱ 크게)·백업/복원/기기 옮기기·도움말'],
  ['learn', '과목 홈·강의 학습 탭(틀·카드·🔑·⭐·⚡·그림 확대)·보기 모드(압축 C·⚡ 복습 R·가리기 Q·집중 모드 V — 화면이 가운데에서 치우치는 사용자 신고 오류 포함)·도구 막대 #kit(형광펜·빈칸 5색·자동 빈칸·되돌리기/다시·메모·전체 보기·🧹 지우기 — "이 카드만·이 탭만 눌러도 안 지워짐" 사용자 신고 오류 포함)·M 메뉴 숨기기·펜슬/손가락 칠하기'],
  ['tables', '정리표(요약/자세히·맨 위 전체정리표·👁 열 가리기·필터·colFit 열 폭·메뉴 숨김 때 확장)·과목 비교표·기출 한눈표(답 가리기·채점)·기출 대장·예상문제'],
  ['jb', 'JB 문제(목록·한 장씩·답 1·2단계·채점 O/X·★·필터·회차 요약·복습 대기열·압축 목록·인쇄)·플래시카드·🖍 내 표시 모아보기·연도 칩 JB 미리보기'],
]
phase('Explore')
const tasks = [
  ...DIRS.map(([k, t, body]) => () => agent(`${CTX}

## 역할: 설계자 — 방향 '${t}': ${body}
1) 지금 빌드를 세 뷰포트로 찍어 보고 '난잡함'의 원인을 구체적으로(화면·요소·개수) 적는다.
2) 설계: 허브 메뉴(허브 단계 — 🏠 홈·📅 달력·검색·전체 내 표시·과목 목록) vs 과목 메뉴(과목에 들어가면 메뉴가 그 과목 전용으로 바뀜 — ← 허브로, 과목 이름, 과목 문서(과목 홈·JB 문제·한눈표·비교표·예상·대장·내 표시), 강의 목록, 지금 강의의 카드 목차, 과목 바꾸기) 구성과 전환 규칙·서랍·M, 허브 홈(시험일·읽음 % 없이), 과목 홈·강의 화면(머리·탭·미니바·도구 막대 — 도구 막대 켜기/끄기 버튼 따로, 모드 칩 없음, ⚡ 줄마다 ○✕ 없음), 시각 체계(색 토큰·글자 단계·간격·테두리·칩/버튼 종류 수를 수치로).
3) 정적 시안: work/_tmp/ux4_${k}/ 에 home.html · subject.html(과목 홈) · lecture.html(강의 학습 탭 첫 화면 — 🔑·⭐ 카드 두세 장, 도구 막대 토글 버튼 포함) 을 실제 내용(과목·강의 이름·카드 제목은 docs/packs/CONS.js 등에서)으로 만들고 각각 1280x900과 820x1180(서랍 닫힘/열림)으로 찍어 Read로 직접 보며 다듬는다(최소 2회). 지금 shell.html 구조로 구현 가능한 CSS로.
결과(JSON): 방향, 난잡함 원인, 메뉴·홈·과목 화면·시각 체계, 없애거나 합칠 것, 시안 스크린샷 경로, 위험.`, { label: `mock:${k}`, phase: 'Explore', schema: SPEC, effort: 'high' })),
  ...AREAS.map(([k, body]) => () => agent(`${CTX}

## 역할: 오류 조사자 — 영역: ${body}
이 영역을 세 뷰포트(맥 마우스·아이패드 손가락/펜슬 터치 이벤트)에서 실제 공부하듯 모든 버튼·키·흐름을 눌러 보며 오류를 빠짐없이 찾는다: 동작 안 함·반대로 동작·화면 치우침/겹침/잘림/가로 넘침·새로고침·뒤로가기 뒤 상태 잃음·다른 화면과 값 불일치·콘솔 오류·저장 안 됨/날아감·키 충돌(한글 입력 상태 keydown {key:'ㅗ',code:'KeyH'} 포함). 사용자 신고 오류는 반드시 재현하고 원인(코드 줄)까지. 코드도 읽어 논리 오류를 찾는다(tools/cons/shell.html 해당 함수). 파일은 고치지 말 것 — 스크린샷·스크립트는 work/_tmp/ux4_bug_${k}/.
각 오류: id, 영역, 심각도(high=공부 방해·데이터·오작동 / medium=불편·어긋남 / low=다듬기), 문제, 재현 절차, 근거(스크린샷·출력), 원인(코드 위치), 수정안. 중요한 것부터 최대 30개.`, { label: `bug:${k}`, phase: 'Explore', schema: BUGS, effort: 'high' })),
]
const res = await parallel(tasks)
const designs = res.slice(0, 3), bugs = res.slice(3)
phase('Synthesize')
const [plan, tri] = await Promise.all([
  agent(`${CTX}

## 역할: 설계 종합자 — 세 시안을 직접 보고(스크린샷 전부 Read) 최선안을 골라 합치고 구현 계획을 만든다
설계안(JSON): ${JSON.stringify(designs.filter(Boolean)).slice(0, 45000)}
평가(각 10점): ① 과목에 들어가면 메뉴가 그 과목 전용으로 분명히 바뀌는가 ② 깔끔함·가독성(요소 수·여백·위계·색 절제) ③ 공부 흐름 효율 ④ 아이패드 세로·가로 ⑤ 구현 위험(지금 코드·저장 데이터·테스트 호환). 점수표를 남긴다.
최종 시안 work/_tmp/ux4_final/{home,subject,lecture}.html을 만들어 1280x900·820x1180으로 찍고(Read로 확인, 최소 2회 다듬기) final_mockups에 경로.
구현 계획: 결정 사항, 시각 체계(토큰·수치), 메뉴(허브/과목 두 모드·전환·서랍·M), 화면별 구성(홈·과목 홈·강의·정리표·JB·달력 크롬), 사용자 요청의 뺄 것(시험일 표시·읽음 %·모드 칩·⚡ 줄마다 ○✕)과 더할 것(도구 막대 토글 버튼) 반영, 구현 묶음 3개(순서대로 한 사람씩 — 묶음당 항목 5~10, 항목마다 what·acceptance(playwright)·files), 데이터 호환, 사용자에게 보여줄 한국어 요약 6~10줄.`, { label: 'judge', phase: 'Synthesize', schema: PLAN, effort: 'high' }),
  agent(`${CTX}

## 역할: 오류 정리자 — 네 조사자의 오류 목록을 합쳐 중복을 없애고 우선순위를 매긴다
오류(JSON): ${JSON.stringify(bugs.filter(Boolean)).slice(0, 60000)}
같은 원인은 하나로(merged_from에 원래 id), 심각도 재확인(의심스러우면 직접 재현해 확인 — 재현 안 되면 빼고 summary에 적음), 이번 4차 개편(메뉴를 허브/과목 두 모드로 바꾸고 홈·과목 화면 정리, 시험일·읽음 %·모드 칩·⚡ ○✕ 제거)으로 없어질 오류는 redesign_overlap에 표시. 사용자 신고 두 건(집중 모드 치우침·🧹 이 카드만/이 탭만 안 지워짐)은 원인과 수정안을 가장 구체적으로. 결과(JSON): 정리된 오류 목록(high → low), 요약.`, { label: 'triage', phase: 'Synthesize', schema: TRI, effort: 'high' }),
])
return { designs, bugs, plan, tri }
