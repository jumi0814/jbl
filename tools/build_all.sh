#!/bin/sh
# 공통 코드 동기화 → 7과목 빌드 → verify → audit_design → (있으면) tests/ux_all.py
cd "$(dirname "$0")/.." && exec .venv/bin/python tools/sync_common.py --build --all "$@"
