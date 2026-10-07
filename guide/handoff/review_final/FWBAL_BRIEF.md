# ⚡·🎯 번호 항목 — 풀 워딩 ↔ 압축 균형 다시 잡기(과목 하나 담당, 10-07 사용자 정정)

사용자(10-07 정정 원문): "내가 넘버링 축약을 다 풀워딩으로 써달라고 한게 암기 정리에서 Epidermis 6 ① rete pegs 소실 ② abnormal stratum corneum ③ vertical polarity 소실 ④ UV DNA damage ⑤ keratinocyte proliferative potential↓ ⑥ melanocytes → dyschromia 이렇게 나와있는건 딱 좋아. 너무 긴 문장들을 그대로 쓰면 이건 암기가 아니라 그냥 그대로 복붙인거니까! 내가 원하는건 ① Soft tissue ② Skeletal and dental structures ③ Interrelationship between static and functioning positions ④ Growth and aging process 요런 예시처럼 넘버링 자체가 길지도 않은데, 이걸 또 굳이 줄이지 않았으면 좋겠다는 말이야! 너가 진짜 최적으로 적절히 판단해서 너무 길다 싶은건 기존대로 압축한거 그대로 유지해주고, 다만 이건 넘버링 시험에도 나올 것 같은데, 길이도 적당하다? 그러면 풀워딩 또는 분량이 좀 길다 싶으면 완벽히 풀워딩은 아니더라도 키워드는 들어가게끔! … 암기파트을 보고도 내가 키워드를 이해 암기하면서 넘어갈 수 있게끔"

오늘 앞선 작업(FULLWORD_BRIEF)이 번호 항목을 원문 그대로 풀어 썼는데, 일부는 **긴 문장을 그대로 붙여** 암기용이 아니게 됐다. 그 줄들을 다시 판단한다.

## 대상 — 오늘 풀 워딩으로 바뀐 줄만
- `git show <과목 커밋> -- tools/<sid>/` = 바뀐 M:·K: 줄의 전(압축)·후(풀 워딩). 과목 커밋: IMPL 2318be0 · ANAT 5abd309 · ESTH 7e8dc90 · CONS dc12a97 · OMS1 c0997fd · GERI b792591 · PHARM 810792d. 보고 `work/review_final2/FW_<SID>.md`도 참고.
- 지금 파일(`tools/<sid>/lec_*.txt` M: 줄 · `tools/<sid>/annot.txt` K: 줄)에서 그 줄을 찾아 항목(①②③)마다 판단:
  1. **원문 항목이 짧다**(대략 한 항목 영어 8낱말·50자 이하, 이름·구) → **풀 워딩 그대로**(사용자 ✓ 예: Interrelationship between static and functioning positions).
  2. **원문 항목이 문장처럼 길다**(한 항목 50~60자를 넘는 문장·절) → **압축으로 되돌리되 키워드는 꼭**: 옛 압축이 원문 핵심어를 빠뜨렸으면 그 핵심어를 넣어 다시 압축(사용자 ✓ 예: `① rete pegs 소실 ② abnormal stratum corneum ③ vertical polarity 소실 ④ UV DNA damage ⑤ keratinocyte proliferative potential↓ ⑥ melanocytes → dyschromia` — 원문 용어 + 짧은 한국어/기호).
  3. 그 사이(조금 길지만 서술형 번호로 나올 것) → 원문 낱말을 살린 **키워드 압축**(관사·전치사·군더더기만 빼고 핵심 명사·형용사·동사는 원문 그대로).
- 한 줄 안에서 항목마다 따로 판단해도 됨(①은 풀 워딩, ④는 키워드 압축). 기출 서술 답(JB 답이 그 문장인 것)은 시험 답이니 키워드가 다 들어가게.
- 화면에서 한 ⚡ 줄이 너무 길면(대략 300자↑) 압축 쪽으로.

## 하지 않을 것
- 오늘 바뀌지 않은 줄·번호 없는 줄은 손대지 않음. 라벨·번호 개수·순서·`{r:}`(핵심어에)·카드 순서 그대로. 본문 `-` 줄의 `{n:…}` 필기 표시는 건드리지 않음.
- 자료에 없는 말 금지(압축은 원문 낱말을 줄이는 것만, 한국어 풀이는 원래 있던 것·자료의 것).
- 플래시카드: 옛 압축으로 되돌리면 옛 기록이 그대로 이어짐(좋음). 키워드 압축은 옛 압축과 비슷하게(라벨·번호 그대로).

## 검사
- `.venv/bin/python tools/check_lec.py <SID>` ✗ 0 · `.venv/bin/python tools/check_abbr.py <SID>` 새 약어 0 · ⚡는 `tools/<sid>/lecparse.py` render_recall로 렌더해 번호 목록 그대로.
- annot를 고치면 `.venv/bin/python tools/annot_diff.py <SID>`로 A·M·N 빠진 글자 0(K는 예외).
- 빌드·커밋·stash·브라우저 금지 · 맡은 과목 lec·annot 밖 수정 금지 · scratchpad 이름 `<SID>_FB_`.

## 보고 `work/review_final2/FB_<SID>.md`
줄마다: 파일:줄 · 판단(풀 워딩 유지 / 압축 되돌림 / 키워드 압축) · 후 문구. 끝에 건수. 최종 답 5줄.
