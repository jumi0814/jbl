#!/bin/sh
# 빌드 + 전 검사 + 브라우저 테스트 한 번에(10-07 — jbl-update 스킬 F단계). 로그 work/_tmp/full_check.log, 끝에 '== 요약'.
#   sh tools/full_check.sh            → 7과목 빌드·검사·테스트·감사
#   sh tools/full_check.sh --no-ui    → 브라우저 테스트·디자인 감사 빼고(빠른 확인)
# 오래 걸린다(전체 약 40분) — Claude는 Bash run_in_background로 돌린다('&'로 띄우면 호출이 끝날 때 같이 죽음).
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python; L=work/_tmp/full_check.log; mkdir -p work/_tmp; : > $L; : > work/_tmp/full_check.fail
UI=1; [ "$1" = "--no-ui" ] && UI=0
# 과목 목록(새 과목은 여기 두 줄에 더함)
SIDS="OMS1 CONS IMPL ANAT GERI PHARM ESTH"; sids=$(echo $SIDS | tr A-Z a-z)
say() { echo "$@" | tee -a $L; }
say "== 동기화"; $PY tools/sync_common.py 2>&1 | tail -1 | tee -a $L
say "== 빌드"
for s in $sids; do
  $PY tools/$s/build4.py > work/_tmp/b_$s.log 2>&1; rc=$?
  say "$s rc=$rc $(grep -E '연결 안 된|없는 문항|되돌림' work/_tmp/b_$s.log | tr '\n' ' ' | cut -c1-200)"
done
$PY tools/rehub.py 2>&1 | tail -1 | cut -c1-80 | tee -a $L
say "== verify";        $PY tools/verify.py 2>&1 | grep -E 'FAIL|RESULT' | tee -a $L
say "== check_lec";     for s in $SIDS; do printf "%s ✗%s " $s "$($PY tools/check_lec.py $s 2>&1 | grep -c '✗')"; done | tee -a $L; echo | tee -a $L
say "== check_years";   $PY tools/check_years.py 2>&1 | tail -2 | tee -a $L
say "== check_eyears";  $PY tools/check_eyears.py 2>&1 | grep -v ' 0건' | tail -3 | tee -a $L
say "== check_abbr";    for s in $SIDS; do $PY tools/check_abbr.py $s 2>&1 | tail -1; done | tee -a $L
say "== scan_render";   $PY tools/scan_render.py 2>&1 | tail -8 | tee -a $L
say "== check_links";   $PY tools/check_links.py 2>&1 | grep -v '^    ' | tail -8 | tee -a $L
say "== table_audit"; for S in $SIDS; do say "$S $($PY tools/table_audit.py $S --md work/review_final2/TA_$S.md 2>&1 | tail -1)"; done
say "== check_nred"; for S in $SIDS; do say "$($PY tools/check_nred.py $S 2>&1 | tail -1)"; done   # 10-09 필기 쪽 강조(정보 — 예외가 있어 0 목표 아님)   # 10-09 표 빠짐(칩 없는 기출·없는 id·표 꼴)
say "== check_breaks_jb"; $PY tools/check_breaks_jb.py 2>&1 | tail -1 | tee -a $L
say "== check_numbering"; $PY tools/check_numbering.py 2>&1 | tail -1 | tee -a $L
say "== fc_carry";      $PY tools/fc_carry.py 2>&1 | tail -8 | tee -a $L
for s in $SIDS; do $PY tools/dump_jb.py $s >/dev/null 2>&1; done
if [ $UI = 1 ]; then
  say "== tests"
  # 표시·북마크 테스트는 file:// 대신 로컬 http로(JBL_HTTP=1 — file://은 Chromium이 가끔 localStorage를 비워 거짓 실패). ux3_compat만 file://
  for t in legacy_restore kt_migrate aidlock_test ux_u23 ux2_fixB ux4h_A ux4h_B ux4h_C ux_marks ux4f_P ux4g_A ux4g_C ux_u24 ux_u26 kt_sync ux5_sess ux5_hlm ux4f_C ux2_undo ux6_gap; do
    [ -f tools/tests/$t.py ] || continue
    say "$t $(JBL_HTTP=1 $PY tools/tests/$t.py 2>&1 | grep -E 'RESULT|FAIL' | tr '\n' ' ' | cut -c1-300)"
  done
  say "ux3_compat $($PY tools/tests/ux3_compat.py 2>&1 | grep -E 'RESULT' | tr '\n' ' ')"
  say "== audit_design"; $PY tools/audit_design.py 2>&1 | tail -1 | tee -a $L
fi
say "== 요약"; grep -nE 'FAIL|rc=[1-9]|✗[1-9]|  ✗ |의심 [1-9]|약어 [1-9]|합계 [1-9]|되돌림 [1-9]|끊김 [1-9]|칩 없는 기출 [1-9]|없는 id [1-9]|표 꼴 [1-9]' $L | grep -v '== ' | tee -a work/_tmp/full_check.fail || true
grep -E '^합계: 기록 이어짐' $L | awk -F'[(%]' '{ if ($2+0 < 95) print "  ✗ 플래시카드 기록 이어짐 95% 미만:", $0 }' | tee -a $L
say "ALLDONE"
