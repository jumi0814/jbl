#!/bin/sh
# 클라우드 세션(또는 새 컴퓨터) 환경 준비 — 파이썬 가상환경·playwright·한글 글꼴. 한 번만.
#   sh tools/cloud_setup.sh
# 스크립트는 Python 3.12+ 문법 — 더 낮으면 uv/pyenv로 3.12 이상을 먼저 준비.
set -e
cd "$(dirname "$0")/.."
PYBIN=$(command -v python3.14 || command -v python3.13 || command -v python3.12 || command -v python3)
$PYBIN -c 'import sys; assert sys.version_info >= (3, 12), "Python 3.12+ 필요: " + sys.version'
[ -d .venv ] || $PYBIN -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q pillow playwright
.venv/bin/python -m playwright install chromium || echo "!! chromium 내려받기 실패 — 환경의 네트워크 접근을 넓히거나(playwright CDN 허용) 사용자에게 알릴 것"
# 리눅스: 브라우저 의존 라이브러리·한글 글꼴(없으면 화면 폭·줄바꿈 검사가 맥과 달라짐)
if [ "$(uname)" = Linux ]; then
  (.venv/bin/python -m playwright install-deps chromium >/dev/null 2>&1 || true)
  (command -v apt-get >/dev/null && (apt-get install -y -q fonts-noto-cjk >/dev/null 2>&1 || sudo apt-get install -y -q fonts-noto-cjk >/dev/null 2>&1) || true)
fi
mkdir -p work/_tmp
.venv/bin/python tools/sync_common.py --check
.venv/bin/python tools/rehub.py --check || echo "docs가 shell.html과 다름 → .venv/bin/python tools/rehub.py"
[ -d work/jb ] && echo "work/jb 있음 — 전체 빌드(sh tools/build_all.sh) 가능" || echo "work/jb 없음 — 허브만 빌드(sh tools/hub_all.sh). 팩 내용(원고·build4·lecparse)을 바꾸는 작업은 원본이 있는 컴퓨터에서."
echo "준비 끝"
