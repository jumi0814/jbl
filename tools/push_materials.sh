#!/bin/sh
# 맥 전용: 새 강의자료(예: 26년도 PDF)를 materials/<과목>/에 넣은 뒤 한 줄로 → 쪽별 추출(matx) → 작업용 추출본을 origin cloud-materials 브랜치에 올림.
#   sh tools/push_materials.sh               # 7과목 전부
#   sh tools/push_materials.sh CONS GERI     # 고른 과목만
# 올라가는 것 = work/<SID>/mat(쪽 이미지·텍스트층·필기 주석·OCR)과 work/<SID>/lec 연결뿐. 원본 PDF(materials/)·JB(jb/)는 올리지 않는다.
# 클라우드 세션은 sh tools/cloud_materials.sh 로 받아 정리본을 26년도 자료에 맞춰 고친다(guide/handoff/26년도_업데이트_절차.md).
set -e
cd "$(dirname "$0")/.."
ROOT=$(pwd)
[ -x .venv/bin/python ] || { echo '.venv 없음 — CLAUDE.md 「첫 세션에서 할 일」 2번으로 먼저 준비'; exit 1; }
command -v tesseract >/dev/null || { echo 'tesseract 없음 — brew install tesseract tesseract-lang'; exit 1; }
SIDS="$*"; [ -n "$SIDS" ] || SIDS="OMS1 CONS IMPL ANAT GERI PHARM ESTH"
echo "== 1) 추출: $SIDS"
.venv/bin/python tools/matx.py $SIDS
echo "== 2) cloud-materials 브랜치에 올리기"
TMP=$(mktemp -d)
git fetch -q origin cloud-materials
git worktree add -q --detach "$TMP" FETCH_HEAD
for S in $SIDS; do
  mkdir -p "$TMP/work/$S"
  rsync -a --delete "$ROOT/work/$S/mat/" "$TMP/work/$S/mat/"
  [ -d "$ROOT/work/$S/lec" ] && rsync -a --delete "$ROOT/work/$S/lec/" "$TMP/work/$S/lec/"
done
cd "$TMP"
git add -A work
if git diff --cached --quiet; then echo '바뀐 추출본 없음'; else
  git commit -q -m "추출본 갱신: $SIDS ($(date +%m-%d))"
  git push -q origin HEAD:cloud-materials && echo "올림 — 클라우드 세션에 '26년도 자료 반영해 줘'라고 말하면 됨"
fi
cd "$ROOT"; git worktree remove --force "$TMP"
