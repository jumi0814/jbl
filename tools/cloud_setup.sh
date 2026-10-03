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
# claude.ai 클라우드 컨테이너: chromium이 /opt/pw-browsers에 미리 깔려 있고 CDN 내려받기는 막혀 있음 → 그 chromium 판에 맞는 playwright를 고름
#   (chromium-1194 = playwright 1.56.x). 다른 판이 깔려 있으면 PW_VER=1.xx.x sh tools/cloud_setup.sh 로 지정.
PW_VER=${PW_VER:-}
if [ -z "$PW_VER" ] && [ -d /opt/pw-browsers/chromium-1194 ]; then PW_VER=1.56.0; fi
.venv/bin/pip install -q pillow "playwright${PW_VER:+==$PW_VER}"
.venv/bin/python -c "from playwright.sync_api import sync_playwright as s
with s() as p: p.chromium.launch().close()" 2>/dev/null && echo "chromium OK" || \
 .venv/bin/python -m playwright install chromium || echo "!! chromium 실행·내려받기 실패 — /opt/pw-browsers 판에 맞게 PW_VER를 주거나, 환경의 네트워크 접근을 넓히거나 사용자에게 알릴 것"
# 리눅스: 브라우저 의존 라이브러리·한글 글꼴(없으면 화면 폭·줄바꿈 검사가 맥과 달라짐)
if [ "$(uname)" = Linux ]; then
  (.venv/bin/python -m playwright install-deps chromium >/dev/null 2>&1 || true)
  (command -v apt-get >/dev/null && (apt-get install -y -q fonts-noto-cjk >/dev/null 2>&1 || sudo apt-get install -y -q fonts-noto-cjk >/dev/null 2>&1) || true)
fi
mkdir -p work/_tmp
.venv/bin/python tools/sync_common.py --check
.venv/bin/python tools/rehub.py --check || echo "docs가 shell.html과 다름 → .venv/bin/python tools/rehub.py"
[ -d work/jb ] && echo "work/jb 있음 — 전체 빌드(sh tools/build_all.sh) 가능" || echo "work/jb 없음 — sh tools/cloud_materials.sh 로 작업용 추출본(cloud-materials 브랜치)을 받으면 전체 빌드 가능. 안 받으면 허브만 빌드(sh tools/hub_all.sh)."
echo "준비 끝"
