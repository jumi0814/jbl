# 화면 줄바꿈 자리 전수 검토 — 과목 하나 담당 (10-04 클라우드)

사용자(10-04 원문): "* Pilocarpine = tertiary alkaloid · 점안 → Glaucoma * 경구 → Xerostomia · Cevimeline = M1·M3 · 경구 → Xerostomia 이런식으로 원래는 * Pilocarpine = tertiary alkaloid · 점안 → Glaucoma 경구 → Xerostomia · * Cevimeline = M1·M3 · 경구 → Xerostomia 아래처럼 되어야 하는데 상단처럼 줄바꿈이 이상한 곳이 군데군데 존재하거든. 모든 강의자료 정리본 전수조사하면서 효율적이면서 효과적인 줄바꿈, 이해 및 암기에 최적인 줄바꿈이 이루어졌는지, 누락이나 오류 없는지 검토 개선해줘!"

## 화면이 줄을 나누는 규칙(tools/cons/lecparse.py — 코드는 고치지 않음, 원고만 고침)
- 맨 먼저 **` / `(앞뒤 띄운 빗금)** 자리에서 나눔 → 조각마다 한 줄(•). 괄호·`{r:…}` 안의 ` / `는 안 나눔.
- ①②③(또는 `1. 2. 3.`·`A) B) C)`)가 3개 이상이면 '머리말 + 번호 목록'.
- 길면(110자↑ 항목, 🔑 줄 등) ` · `·`; `·` → ` 자리에서 더 나눔, 190자↑는 문장 단위.
- 그래서 **` / ` = 큰 단위(서로 다른 대상·주제) 경계, ` · ` = 한 대상 안의 작은 나열**로 써야 의미대로 끊긴다.
- 사용자 예: `= Pilocarpine = tertiary {r:alkaloid} · 점안 → {r:Glaucoma} / 경구 → {r:Xerostomia} · Cevimeline = {r:M1·M3} · 경구 → {r:Xerostomia}` → 약 둘의 경계가 ` · `, 한 약 안이 ` / `라 거꾸로 끊김.
  ✓ `= Pilocarpine = tertiary {r:alkaloid} · 점안 → {r:Glaucoma} · 경구 → {r:Xerostomia} / Cevimeline = {r:M1·M3} · 경구 → {r:Xerostomia}`

## 할 일 (맡은 과목 `<SID>`)
1. `work/review_breaks/<SID>.md`(화면 조각 덤프 — `.venv/bin/python tools/dump_breaks.py <SID>`로 다시 만들 수 있음)를 **처음부터 끝까지 전부** 본다. 줄마다: 조각 하나하나가 의미 단위로 끊겼는가? (대상 하나가 두 줄로 찢어짐 · 서로 다른 대상이 한 줄에 붙음 · 조각이 '→ …'·'· …'·'경구 → …'처럼 앞 말 없이 시작 · 한 글자/한 낱말짜리 조각 · 괄호 설명이 떨어져 나감 → 오류)
2. 덤프 끝 '나뉘지 않은 긴 줄'도 본다 — 서로 다른 대상 셋 이상이 ` · `로만 이어져 한 덩어리로 보이면 대상 경계를 ` / `로.
3. 고치는 법(원고 `tools/<sid>/lec_*.txt`만): **구분 기호만 바꾼다**(` / ` ↔ ` · `, 필요하면 ` / ` 추가·삭제). 낱말·`{r:}`·`==`·순서는 그대로(사용자 형광펜·빈칸이 글자에 붙어 있음). 기호만으로 안 되면 그 줄은 고치지 말고 보고에 '수동 필요'로.
4. 고친 뒤 `.venv/bin/python tools/dump_breaks.py <SID>`로 다시 덤프해 그 줄이 의도대로 끊기는지 확인.
- 이미 의미대로 끊긴 줄은 건드리지 않는다. 카드 머리·E:(⭐)·M:(⚡ — ` / `가 플래시카드 줄 나눔이라 특히 조심, 보지 않음)·`|` 표·@ 줄은 대상 아님.

## 검사
`.venv/bin/python tools/check_lec.py <SID>` ✗ 0. 빌드·커밋·브라우저 금지. 다른 과목 파일 금지.

## 보고 `work/review_breaks/B_<SID>.md`
고친 줄마다: 파일:줄 · 전(화면 조각) → 후(화면 조각). 끝에 건수·'수동 필요' 목록. 최종 답 5줄.
