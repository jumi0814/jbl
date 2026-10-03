# 허브 기능 점검 — 오류 찾기 담당 안내 (10-03 클라우드)

저장소 `/home/user/jbl`. 허브 = `docs/index.html`(코드 원본 `tools/cons/shell.html` — **고치지 말 것, 보고만**). 파이썬 `.venv/bin/python`, Playwright 1.56(chromium 설치됨). URL은 `tools/jblpaths.py`의 `HUB_URL`(file://…/docs/index.html). 기존 테스트 예시: `tools/tests/ux4f_P.py`·`ux4f_Q.py`(boot·WAIT·clock 쓰는 법). 내부 함수는 `window.__h`.
사용자 요청(10-03): "자잘자잘한 기능에서 크고작은 오류들이 계속 생기는데 더이상 없게끔 검토" · "가장 최고의 jbl 프로그램".

## 하는 법
- 스크래치 스크립트는 `/tmp/claude-0/-home-user-jbl/a0af02c5-0dbc-52ee-b82b-13be879fb1dd/scratchpad/hub_<영역>/`에 쓴다(저장소에 파일 만들지 말 것).
- 세 화면: 1280×900 마우스 · 820×1180 터치(has_touch) · 1180×820 터치. 새 context마다 `localStorage.clear()` 후 `jblhub.v1.whatsNew.4='1'`.
- **실제 사용자처럼** 키보드·클릭·탭·스크롤로 조작하고, 결과를 DOM·localStorage·콘솔 오류로 확인한다. 같은 동작을 다른 화면·다른 과목(OMS1·PHARM·ESTH 등)·다른 탭(학습·정리표·비교표·기출·예상·플래시카드·JB)에서도.
- 경계 상황을 일부러: 빠른 연속 입력, 모드 켠 채 화면 이동, 새로고침, 뒤로가기, 창 크기 바꾸기, 다른 탭 갔다 오기(visibilitychange), 빈 상태, 아주 긴 글, 같은 동작 두 번.
- 시각 확인이 필요하면 스크린샷을 찍어 Read로 본다(겹침·잘림·가로 넘침·안 보이는 버튼).

## 보고
`/home/user/jbl/work/review_final2/HUB_<영역>.md`:
```
# 허브 점검 — <영역>
## 오류 (n건) — 심각도(상/중/하) · 화면·경로 · 재현 순서 · 기대 · 실제 · (가능하면) 원인 코드 위치(tools/cons/shell.html 줄)·고칠 방향
## 어색함·개선 제안 (n건) — 사용자에게 득이 분명한 것만
## 확인했는데 정상 (목록 한 줄씩)
```
추측 말고 재현된 것만 '오류'로. 최종 답은 5줄 이내.
