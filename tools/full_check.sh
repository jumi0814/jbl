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
o=$($PY tools/num/build_num.py --check 2>&1 | tail -1); say "$o"; echo "$o" | grep -q OK || say "  ✗ 넘버링 모듈 사본(docs/num ↔ tools/num · NUMV) 다름 — tools/num/build_num.py"
say "== 빌드"
for s in $sids; do
  $PY tools/$s/build4.py > work/_tmp/b_$s.log 2>&1; rc=$?
  say "$s rc=$rc $(grep -E '연결 안 된|없는 문항|되돌림' work/_tmp/b_$s.log | tr '\n' ' ' | cut -c1-200)"
done
$PY tools/rehub.py 2>&1 | tail -1 | cut -c1-80 | tee -a $L
say "== verify";        $PY tools/verify.py 2>&1 | grep -E 'FAIL|RESULT' | tee -a $L
say "== check_lec";     for s in $SIDS; do o=$($PY tools/check_lec.py $s 2>&1); sl=$(echo $s | tr A-Z a-z); fn=$($PY tools/check_unote.py $s | tail -1 | awk '{print $NF}'); printf "%s ✗%s 경고 %s @UPD없음 %s 필기NEW26 %s " $s "$(echo "$o" | grep -c '✗')" "$(echo "$o" | grep -c '^   · ')" "$(echo "$o" | grep -c '@UPD 없음')" "$fn"; done | tee -a $L; echo | tee -a $L   # 경고 수는 정보(기준과 견줌) · @UPD없음 = 26 갱신 강의 표시 빠짐(10-10)
say "== check_years";   $PY tools/check_years.py 2>&1 | grep '^== ' | tee -a $L
say "== check_eyears";  $PY tools/check_eyears.py 2>&1 | grep -v ' 0건' | tail -3 | tee -a $L
say "== check_abbr";    for s in $SIDS; do $PY tools/check_abbr.py $s 2>&1 | grep '^== '; done | tee -a $L
say "== scan_render";   $PY tools/scan_render.py 2>&1 | tail -8 | tee -a $L
say "== check_links";   $PY tools/check_links.py 2>&1 | grep -v '^    ' | tail -8 | tee -a $L
say "== pred_check";    for S in $SIDS; do say "$S $($PY tools/pred_check.py $S 2>&1 | tail -1)"; done   # 10-16 예상문제 문법·사라진 옛 문항(pred_before) ✗
say "== link_audit";    $PY tools/link_audit.py --md work/_tmp/link_audit.md 2>&1 | grep -E "^[A-Z0-9]+:|  ✗|RESULT" | tee -a $L   # 10-16 JB ↔ 강의·⭐·표·예상 연결 전수
n=$(grep -c '예상 연결 없음' work/_tmp/link_audit.md 2>/dev/null); [ "${n:-0}" -gt 0 ] && say "  ✗ link_audit 최근 해 문항 예상 연결 없음 $n"   # QA 49 — △도 0이어야 함
say "== check_yearprof"; $PY tools/check_yearprof.py 2>&1 | grep -E "^[A-Z0-9]+:|  ✗|RESULT" | tee -a $L   # 10-16 출제 연도별 출제 교수 표(YEAR_PROF) 키·id·해
[ -f tools/fmt_audit.py ] && { say "== fmt_audit"; $PY tools/fmt_audit.py 2>&1 | grep -E "^[A-Z0-9]+:|RESULT" | tee -a $L; }   # 10-16 형식 판정 표·의심(정보) → work/_tmp/fmt<YY>/<SID>.md
[ -f tools/tests/fmt_cases.py ] && say "fmt_cases $($PY tools/tests/fmt_cases.py 2>&1 | grep -E 'RESULT' | tail -1)"   # 형식 판정 회귀(브라우저 없음)
say "== table_audit"; for S in $SIDS; do say "$S $($PY tools/table_audit.py $S --md work/review_final2/TA_$S.md 2>&1 | tail -1)"; done
say "== check_nred"; for S in $SIDS; do say "$($PY tools/check_nred.py $S 2>&1 | tail -1)"; done   # 10-09 필기 쪽 강조(정보 — 예외가 있어 0 목표 아님 · 기준값 SKILL G1)
say "== check_breaks_jb"; $PY tools/check_breaks_jb.py 2>&1 | tail -1 | tee -a $L
say "== check_numbering"; $PY tools/check_numbering.py 2>&1 | tail -1 | tee -a $L
say "== fc_carry";      $PY tools/fc_carry.py 2>&1 | tail -8 | tee -a $L
for s in $SIDS; do $PY tools/dump_jb.py $s >/dev/null 2>&1; $PY tools/dump_breaks2.py $s >/dev/null 2>&1; done   # QA(E)·D2b가 읽는 화면 덤프
if [ $UI = 1 ]; then
  say "== tests"
  # 표시·북마크 테스트는 file:// 대신 로컬 http로(JBL_HTTP=1 — file://은 Chromium이 가끔 localStorage를 비워 거짓 실패). ux3_compat만 file://
  for t in legacy_restore kt_migrate aidlock_test ux_u23 ux2_fixB ux4h_A ux4h_B ux4h_C ux_marks ux4f_P ux4g_A ux4g_C ux_u24 ux_u26 kt_sync ux5_sess ux5_hlm ux4f_C ux2_undo ux6_gap ux7_u26 ux8_num ux9_numai ux10_num5 ux11_fix ux12_numrev ux13_numdrag ux14_numjb ux15_storage ux16_pred ux17_fig ux18_numpred ux19_yearprof ux20_numdocx ux21_numyrs ux22_markbridge nb_numbering; do
    [ -f tools/tests/$t.py ] || continue
    say "$t $(JBL_HTTP=1 $PY tools/tests/$t.py 2>&1 | grep -E 'RESULT|FAIL|lost rate|LOST_GONE [0-9]' | tr '\n' ' ' | cut -c1-300)"
  done
  say "ux3_compat $($PY tools/tests/ux3_compat.py 2>&1 | grep -E 'RESULT' | tr '\n' ' ')"
  say "== audit_design"; $PY tools/audit_design.py 2>&1 | tail -1 | tee -a $L
fi
say "== 요약"; grep -nE 'FAIL|rc=[1-9]|✗[1-9]|✗ [1-9]|  ✗ |의심 [1-9]|약어 [1-9]|합계 [1-9]|되돌림 [1-9]|끊김 [1-9]|칩 없는 기출 [1-9]|없는 id [1-9]|표 꼴 [1-9]|@UPD없음 [1-9]|필기NEW26 [1-9]' $L | grep -vE '^[0-9]+:== [^:]*$' | grep -v ' · 형식 {' >> work/_tmp/full_check.fail || true
grep -E '^합계: 기록 이어짐' $L | awk -F'[(%]' '{ if ($2+0 < 95) print "  ✗ 플래시카드 기록 이어짐 95% 미만:", $0 }' >> work/_tmp/full_check.fail
cat work/_tmp/full_check.fail | tee -a $L   # 요약은 로그 끝에도(10-09 — 기준값은 SKILL G1)
say "ALLDONE"
