#!/bin/sh
# 맥 전용 한 줄(11-15): 파일을 넣은 뒤 jbl 폴더 터미널에서  git pull && sh tools/push_materials.sh
#   0) 폴더 정리(tools/folders.py — 처음이면 자리를 만들고 옛 3Q 파일을 3Q 칸으로 옮김 · 지우는 것 없음)
#   1) 강의자료 추출(matx — materials/4Q/<과목>/의 PDF·PPTX → 쪽 이미지·글·필기·OCR · 이미 뽑은 쪽은 건너뜀)
#   2) JB 풀기(jbx — jb/ 아래 전부: jb/4Q/<과목>/<연도 든 이름>.pdf · jb/3Q/'20YY 3Q <과목> JB.pdf' · 이미 푼 판은 건너뜀)
#   3) cloud-materials 브랜치에 아직 없는 추출본만 올림 → 4) 끝에 '이 대화에 보낼 한 줄'을 보여 줌
#   sh tools/push_materials.sh               # 지금 쿼터 과목 강의자료 + 모든 JB
#   sh tools/push_materials.sh CONS4 RAD     # 고른 과목만(그 과목 JB도)
#   sh tools/push_materials.sh --dry         # 올릴 목록만 보기(올리지 않음 · 폴더 정리도 보기만)
# 원본 PDF(materials/·jb/)는 올리지 않는다 — 추출본(work/<SID>/mat/<파일id>/ · work/jb/<SID>_20YY/)만.
# 클라우드 세션은 sh tools/cloud_materials.sh 로 받아 작업한다(guide/handoff/4Q_자료_보내는_법.md).
set -e
cd "$(dirname "$0")/.."
ROOT=$(pwd)
DRY=0; SIDS=""; PICK=0
for a in "$@"; do case "$a" in --dry) DRY=1;; *) SIDS="$SIDS $a"; PICK=1;; esac; done
PY=.venv/bin/python; [ -x "$PY" ] || PY=python3
[ -n "$SIDS" ] || SIDS=$($PY tools/quarters.py sids)   # 기본 = 지금 쿼터 과목(tools/quarters.json current) · 3Q 과목은 이름을 주면 됨
if [ $DRY = 1 ]; then $PY tools/folders.py --dry; else $PY tools/folders.py; fi
[ -n "$NO_MATX" ] || [ -x .venv/bin/python ] || { echo '.venv 없음 — CLAUDE.md 「첫 세션에서 할 일」 2번으로 먼저 준비'; exit 1; }
if [ -z "$NO_MATX" ]; then
  command -v tesseract >/dev/null || { echo 'tesseract 없음 — brew install tesseract tesseract-lang'; exit 1; }
  echo "== 1) 강의자료 추출(이미 뽑은 쪽 이미지·OCR은 건너뜀):$SIDS"
  .venv/bin/python tools/matx.py $SIDS
  echo "== 1b) JB 풀기(이미 푼 판은 건너뜀)"
  if [ $PICK = 1 ]; then .venv/bin/python tools/jbx.py $SIDS; else .venv/bin/python tools/jbx.py; fi
fi
echo "== 2) cloud-materials 브랜치에 없는 새 파일 찾기"
git fetch -q origin cloud-materials
REV=$(git rev-parse FETCH_HEAD)
TMP=$(mktemp -d)
git worktree add -q --no-checkout --detach "$TMP" "$REV"
trap 'cd "$ROOT"; git worktree remove --force "$TMP" 2>/dev/null || true' EXIT
git -C "$TMP" read-tree "$REV"   # 파일은 풀지 않고 목록(index)만 — 이미 올린 추출본은 그대로 둠
N=0
for S in $SIDS; do
  [ -d "$ROOT/work/$S/mat" ] || continue
  for D in "$ROOT/work/$S/mat"/*/; do
    [ -d "$D" ] || continue
    F=$(basename "$D")
    if ! git -C "$TMP" cat-file -e "$REV:work/$S/mat/$F/t" 2>/dev/null; then
      echo "  + $S  $F ($(ls "$D/i" 2>/dev/null | wc -l | tr -d ' ')쪽)"; N=$((N+1))
      if [ $DRY = 0 ]; then mkdir -p "$TMP/work/$S/mat"; cp -R "${D%/}" "$TMP/work/$S/mat/$F"; NEW="$NEW $S"; ADD="$ADD work/$S/mat/$F"; fi
    fi
  done
done
JBS=$SIDS; [ $PICK = 1 ] || JBS=$($PY -c "import sys; sys.path.insert(0,'tools'); import quarters as Q; print(' '.join(Q.all_sids()))")   # 11-15 JB = 모든 쿼터(3Q 26판도 한 번에)
for S in $JBS; do   # 10-07 새 과목·새 JB 판본: work/jb/<SID>_20xx(jbx.py 추출본)도 cloud-materials에 없으면 올림
  for D in "$ROOT/work/jb/${S}_"[0-9]*/; do
    [ -d "$D" ] || continue
    F=$(basename "$D")
    if ! git -C "$TMP" cat-file -e "$REV:work/jb/$F/manifest.json" 2>/dev/null; then
      echo "  + JB  $F"; N=$((N+1))
      if [ $DRY = 0 ]; then mkdir -p "$TMP/work/jb"; cp -R "${D%/}" "$TMP/work/jb/$F"; NEW="$NEW $S"; ADD="$ADD work/jb/$F"; JBN=1; fi
    fi
  done
done
if [ $N = 0 ]; then echo '새로 올릴 것 없음 — 파일을 materials/4Q/<과목>/(강의자료)·jb/4Q/<과목>/(JB)에 넣었는지 위 "지금 들어 있는 파일"에서 확인'; exit 0; fi
if [ $DRY = 1 ]; then echo "(--dry: ${N}개 — 올리지 않음)"; exit 0; fi
echo "== 3) 올리기 (${N}개 파일)"
cd "$TMP"
for S in $(echo $NEW | tr ' ' '\n' | sort -u); do [ -f "$ROOT/work/$S/mat/index.json" ] || continue; mkdir -p "work/$S/mat"; cp "$ROOT/work/$S/mat/index.json" "work/$S/mat/index.json"; ADD="$ADD work/$S/mat/index.json"; done
git add -f -- $ADD   # 새 폴더와 index.json만(다른 경로는 손대지 않음 · work/는 main의 .gitignore 대상이라 -f)
git commit -q -m "새 강의자료 추출본: $(echo $NEW | tr ' ' '\n' | sort -u | tr '\n' ' ')($(date +%m-%d) · ${N}개)"
git push -q origin HEAD:cloud-materials
echo ""
echo "== 올림 (${N}개) — 이제 Claude 대화창에 아래 한 줄을 보내 주세요"
echo "   4Q 자료 올렸어:$(echo $NEW | tr ' ' '\n' | sort -u | tr '\n' ' ')"

