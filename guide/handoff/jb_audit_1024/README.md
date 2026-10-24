# JB 전수 검토 (10-24) — 찾기만, 아직 안 고침

사용자 10-24: "각 과목에 대해서 jb 문제 누락 없는지 … 모조리 다 찾아낸 다음에 나한테 정리해서 알려주면, 내가 뭘 넣고 뭐는 이미 겹치거나 나온건지 정할게."

- `<SID>_review.md` — 과목마다 독립 검토(JB 전 쪽 + 그림 쪽 이미지 ↔ 사이트 카드). 0표·A 누락·B 합치기·C 교수·D 연도·짤탈·E 내용·F 그 밖·G 확인됨.
- `<SID>_auto.md` — `tools/jb_cover.py <SID>` 자동 대조(교수·그림 칸은 거짓 양성이 대부분).
- `결정표.html` — 사용자 결정 화면(142항목 + 확인만 43). 게시본: https://claude.ai/artifact/4M65i8qqaJjWv8t7EP9HWp
  - 사용자가 고른 것은 그 artifact의 db `state/picks` 문서 `items[<SID>-<번호>] = {i, p(고른 안 글), n(메모), at}` (공통은 `X-n`).
  - 읽기: ArtifactData get collection `state` doc_id `picks`. 사용자가 '결정 복사'로 붙여 넣을 수도 있음.
- 결정을 받으면: 항목별로 assemble.py(OTHER·CANON)·annot.txt(rel·yrs·lec)·parse_<sid>.py(분해 경계·\x02 하이픈)·trend(짤탈 기준선)·build4(양방향 링크·최근 출제 꼴) 순으로 고치고 build_all → check_years·check_eyears·link_audit·check_lec → 테스트 → 배포.

요약(빠진 문항): GERI 24판 2023 장지희 20번 1 · PHARM 2021 4번(Iodine)·8-1·8-2(답 칸에 묻힘) + 23q4 2020 구강건조증 6(카드 없음 4 · 연도만 2) + 연결만 빠짐(24판 XE 2023 4번·23판 HM 2020 15-1·23q4 구강건조증 사본 16) · 나머지 5과목 0.
