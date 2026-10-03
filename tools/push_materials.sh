#!/bin/sh
# 맥 전용: 새 강의자료(예: 26년도 PDF)를 materials/<과목>/에 넣은 뒤 한 줄로 → 쪽별 추출(matx) → **새로 넣은 파일의 추출본만** origin cloud-materials 브랜치에 올림.
#   sh tools/push_materials.sh               # 7과목 전부에서 새 파일 찾기
#   sh tools/push_materials.sh CONS GERI     # 고른 과목만
#   sh tools/push_materials.sh --dry         # 올릴 목록만 보기(올리지 않음)
# '새 파일' = cloud-materials 브랜치에 아직 없는 work/<SID>/mat/<파일id>/ 폴더(이미 올린 25·26 추출본은 건드리지 않음) + 그 과목 index.json(파일 목록).
# 원본 PDF(materials/)·JB(jb/)는 올리지 않는다. 정리본 키 연결(work/<SID>/lec)은 클라우드가 새 파일로 바꾼다.
# 클라우드 세션은 sh tools/cloud_materials.sh 로 받아 정리본을 26년도 자료에 맞춰 고친다(guide/handoff/26년도_업데이트_절차.md).
set -e
cd "$(dirname "$0")/.."
ROOT=$(pwd)
DRY=0; SIDS=""
for a in "$@"; do case "$a" in --dry) DRY=1;; *) SIDS="$SIDS $a";; esac; done
[ -n "$SIDS" ] || SIDS="OMS1 CONS IMPL ANAT GERI PHARM ESTH"
[ -n "$NO_MATX" ] || [ -x .venv/bin/python ] || { echo '.venv 없음 — CLAUDE.md 「첫 세션에서 할 일」 2번으로 먼저 준비'; exit 1; }
if [ -z "$NO_MATX" ]; then
  command -v tesseract >/dev/null || { echo 'tesseract 없음 — brew install tesseract tesseract-lang'; exit 1; }
  echo "== 1) 추출(이미 뽑은 쪽 이미지·OCR은 건너뜀):$SIDS"
  .venv/bin/python tools/matx.py $SIDS
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
if [ $N = 0 ]; then echo '새 파일 없음 — materials/<과목>/에 PDF를 넣었는지 확인'; exit 0; fi
if [ $DRY = 1 ]; then echo "(--dry: ${N}개 — 올리지 않음)"; exit 0; fi
echo "== 3) 올리기 (${N}개 파일)"
cd "$TMP"
for S in $(echo $NEW | tr ' ' '\n' | sort -u); do cp "$ROOT/work/$S/mat/index.json" "work/$S/mat/index.json"; ADD="$ADD work/$S/mat/index.json"; done
git add -f -- $ADD   # 새 폴더와 index.json만(다른 경로는 손대지 않음 · work/는 main의 .gitignore 대상이라 -f)
git commit -q -m "새 강의자료 추출본: $(echo $NEW | tr ' ' '\n' | sort -u | tr '\n' ' ')($(date +%m-%d) · ${N}개)"
git push -q origin HEAD:cloud-materials && echo "올림 — 클라우드 세션에 '26년도 자료 반영해 줘'라고 말하면 됨"
