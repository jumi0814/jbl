#!/bin/sh
# 클라우드 세션(또는 원본이 없는 컴퓨터): 작업용 추출본(origin의 cloud-materials 브랜치) → 저장소 work/ 로 풀기.
#   sh tools/cloud_materials.sh        # 약 470MB — 7과목 강의자료 쪽 이미지·텍스트·OCR, JB 3판본, ESTH 작업 조각
# work/는 .gitignore — 여기서 고친 것(특히 work/<SID>/parts·notes)은 커밋되지 않는다. 남겨야 할 것은 tools/·guide/에.
# 다시 돌리면 같은 이름의 파일을 덮어쓴다(클라우드에서 고친 parts가 있으면 먼저 다른 곳에 복사).
set -e
cd "$(dirname "$0")/.."
git fetch --depth 1 origin cloud-materials
mkdir -p work
git archive FETCH_HEAD work | tar -x -C .
mkdir -p work/_tmp
echo "풀림: $(ls work | tr '\n' ' ')"
du -sh work 2>/dev/null | cut -f1
[ -d work/jb ] && echo "work/jb 있음 — 전체 빌드(sh tools/build_all.sh) 가능"
