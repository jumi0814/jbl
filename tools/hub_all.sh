#!/bin/sh
# 원본(강의자료·JB — work/jb)이 없는 환경(클라우드 세션)용: 공통 코드 동기화 → 허브만 다시(tools/rehub.py — 팩은 커밋된 그대로) → verify → audit_design → tests/ux_all.py
# 허브 코드(shell.html)만 고쳤을 때 쓴다. 원고·build4.py·lecparse.py·reflow.py·trend.py를 고쳤으면 원본이 있는 컴퓨터에서 sh tools/build_all.sh.
cd "$(dirname "$0")/.." && PY=.venv/bin/python && [ -x "$PY" ] || PY=python3
exec $PY tools/sync_common.py --rehub --all "$@"
