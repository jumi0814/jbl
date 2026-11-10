# R_DATA_시간·형광펜·동기화·넘버링 — 11-10 읽기 전용 점검 보고(담당 원문 · 줄 번호는 커밋 b714aca8의 tools/cons/shell.html)

I found 30 issues across the six areas. Four of them can lose user data or miscount study time (P1). All file:line references are to `/home/user/jbl/tools/cons/shell.html` unless marked `num.js`.

# (a) Confirmed from code

## Study time

**A1. A session left running through device sleep is counted in full (up to 12 h). The "no input" reminder band doesn't stop this. — P1**
- Evidence: `trTick` 2969 checks the 12-hour cap before anything else and stops at the cap time, not at the last input: `if(ts.t0+H12<=now){trStop(ts.t0+H12,'세션이 12시간을 넘어 끝냈어요');return;}`.
- For gaps under 12 h, 2972 `sessFlush(now)` records the whole gap first. `trAsk` (2958–2960) then shows the band. If the user is active again, after 30 min the band is dismissed and the gap is kept: `if(li>T.askLi){T.askAt=0;trBand();}`.
- Nothing detects a gap between ticks (no `lastTick` anywhere). The page-start check at 3283 only asks when `ts.cls || !ts.hid`, so a tab that iOS discarded comes back silently.
- Scenario: start ▶ 공부 시작 at 23:00, close the laptop lid. Next morning the toast says "세션 끝 — 공부 12:00", or with a 7 h sleep you scroll past the band and 7 h stays.
- Fix:
  - Record the time of every tick. If more than 2 min passed since the last tick, flush only up to `li+60s` and show the existing "closed session" question with default "마지막 입력 때".
  - At the 12 h cap, end at `min(t0+12h, li+60s)` when the last input is older than `sessAsk`.
  - In `trAsk`, if no button was pressed, default to `stopli` when the gap included a device sleep.
- Test: none. `ux3_timer.py:122-127` asserts 12 h is recorded only with `sessAsk=0`.

**A2. Moving the clock backwards freezes auto timing. — P3**
- Evidence: 2699 `tFlush`: `if(now<=T.t0)return;`. `T.t0` stays in the future, so nothing is recorded until the clock passes the old value. A forward jump inside a session is counted as session time (wall clock).
- Fix: if `now < T.t0 - 5s`, reset `T.t0 = now`.

**A3. The 3Q and 4Q hubs can both count time at once. — P3**
- Evidence: each hub has its own BroadcastChannel (`QC.bc.t`, 2837) and its own `tstate`. A session left running in a 3Q tab keeps its wall clock while 4Q auto-measures.
- Within each quarter the totals are fine. "Total study" would be double-counted if both calendars are added. 4Q goals ignore time spent studying in the 3Q tab.
- Fix: share a cross-quarter "who is measuring" channel (e.g. `jbl-timer`), or at least block 4Q auto-measuring while a 3Q session is running.

**A4. The time-edit log `tedit` grows forever and is synced every 3 min. — P2 (probable size impact)**
- Evidence: `teLog` 3012 only appends. Trim entries are written by `tUnrec` (2894), called from `trAutoRest` (3242 — almost every app/tab switch within a minute of input) and from `restBack` <60 s (3258). The only list-rewrite (`undoEdit`, 3019) just marks entries `x=1`; nothing ever deletes old ones.
- It is part of `SYNCT`, so the 'T' group is re-sent every 3 min, and `teIdx` rebuilds the whole list.
- Fix: fold trims older than ~60 days into a per-day/subject total, e.g. one `k:'trimsum'` entry with a stable id.

**A5. 4Q's first-run import leaves out the timer settings. — P3**
- Evidence: the import list at 2618 has no `tauto`, `tgoal`, `sessAsk` (nor `jbauto`, `jbautoNg`, `jbhidePrev`, `qz*`, `ascope`, `sumhide`, `cond`, `autofold`, `exfirst`).
- Scenario: a user who turned auto-measuring off in 3Q gets it silently on in 4Q, and the goal resets to 4:00.
- Fix: add these to the list `A`.

The statistics math looked correct. Day keys use the local 6 am boundary (`day`/`calKey`, 2666–2667). No `toISOString` is used in time code. Week and streak loops use noon dates (`tD0`), and every divide-by-goal or divide-by-`main` is guarded. The only rounding issue is that `fmtH` floors each day, so the week total can differ from the sum of the daily figures by a few minutes (P3).

## Highlights / blanks / memos

**B1. A mark can silently move to a different place after the lecture text is rewritten. — P2**
- Evidence: `pick` 4224 accepts a single candidate with no context check when the text is 4+ characters: `if(L.length===1)return (fz(String(o.x)).t.length>=4||ctxScore(...)>=need)?L[0]:null;`.
- Scenario: the 26 rewrite deletes the sentence where you highlighted "치근단 병소", but the same words appear once elsewhere in that block. The mark jumps there and is not flagged as lost.
- Fix: when the block fingerprint `o.v` differs, require `ctxScore ≥ need` even for a single candidate. Otherwise mark it lost (the existing 🖍 recovery handles that).

**B2. All marks of a subject live in one key `ann.<SID>`. — P3 (scaling)**
- Evidence: `persist` 4175 rewrites the whole subject on every stroke. The sync group for that subject is re-sent (min 12 s), and every merge parses the whole object.
- At a few thousand marks this is noticeable on iPad.
- Fix (later): shard by lecture, e.g. `ann.<SID>.<lec>`.

**B3. ★ card-bookmark count includes bookmarks of removed cards. — P3**
- Evidence: 6327 `cbmN = Object.keys(cbmGet(S)).length`, with no existence check. `migrateAids` (5492) migrates `ann` and `done` but not `cbm`/`lrd`.
- After the 26 rewrite deletes cards, the menu shows e.g. "★ 12" while the view shows 10.
- Fix: count only keys that match a live card aid or alias.

## Grading / bookmarks / numbering links

**C1. A JB card renumbering (`jb_move`) is not applied to numbering items. — P2**
- Evidence: `jbMove` 4896–4901 moves `mk`, `fc 'J:'` and `ann '<S>:old'` only. Numbering items keep `src[].id` / `ref.id = 'OMS1:Q49'`. `tools/oms1/jb_move.json` already has `"Q49": "Q37"`.
- Effects (`num.js` 790–808, 1629–1636):
  - `jbRef`, `jbYrsSync` and `bmOn` can't find the card, so there is no "JB 문제" link, the year doesn't follow the JB, and ★ disappears.
  - '✎ 넘버링' on Q37 doesn't find the existing item and adds a duplicate (or auto-links one that is ≥0.75 similar).
- Fix: in `jbMove`, also rewrite `num.i.<S>.*` `src`/`ref` ids `S:old → S:new` (the key id can stay).
- Test: `ux2_jblock` covers mk/fc/ann only.

**C2. Un-marking a review grade (모름/애매함/암기 완료) never sticks across devices, and changed grades leave duplicates. — P2**
- Evidence: in `syncApplyGrp` 5083, for `num.r`/`num.rl` keys, even when only the other device changed, it runs `mergeData({[K]:r})` (union) instead of taking the remote value.
- `mergeData` 4784 merges `h` as a union keyed `t|s`. `markSet` (`num.js` ~2259) deletes or replaces the entry for the current round.
- Result:
  - A removed entry is re-added by the other device's copy.
  - A changed grade (new `t`) keeps the old one too, and the next "tap again to clear" leaves the old grade as current `m`.
- Effect: wrong 'weak'/'m0'/'m2' review scopes.
- Fix: take the remote value when only the remote changed, and union only when both changed. Or add tombstones: `{s, del:1}` per round.

## Backup / restore / storage

**D1. Neither auto-backup restore nor "교체" can bring back numbering, and a snapshot file merge always loses. — P2 (amplifies every numbering loss)**
- Evidence:
  - `STUDY` 5274 = `ann|mk|done|memo|memoh|fc|autoRule|lbm|lrd|cbm`, with no `num.`/`exam.`. `studyPlan` (5275) only uses those keys.
  - "⬇ 파일" of a snapshot plus 합치기 goes through `mergeData` 4782: `(+b.u||0)>(+a.u||0)`, so an older snapshot never wins.
- The only rollback is one step per item (`prev`) or the toast undo after a ChatGPT import.
- Fix: add "이 과목 넘버링을 이 시점으로" (per-item compare of `u`, with a preview) to the restore dialog.

**D2. Versions displaced by sync conflicts go to a store nobody can see. — P2**
- Evidence: `xsOld` 5381 writes to IndexedDB store `'old'`. It is skipped when `!XS.db`, capped at 300, not in `dumpAll`, and no UI reads it.
- Sync rule `num.i` = newer `u` wins, whole record (5033).
- Scenario: you edit a story on the phone in the subway while the Mac edits the answer of the same item. One edit vanishes from every UI.
- Fix: list "다른 기기에 밀린 판" per item in the ⋯ menu, and include `old` in the backup file.

**D3. The two quarters share one storage quota, and 4Q's 공간 정리 can't touch 3Q data. — P1 (probable, depends on the size of 3Q data)**
- Evidence: `lsScan`/`lsKind` 5246–5248 count `oq` in `used`, and the warnings and the 70% cap use the whole origin. `cleanHTML` 5458 offers only this quarter's old backup copies, moving this quarter's `num.*`, and old auto blanks. `xsAuto` (5434) moves only this quarter's `num.*`.
- Scenario: on iPad Safari (cap ≈2.6 M characters; Korean counts double) 3Q holds most of it. 4Q highlights and grades start failing into `LSQ` (red band), and the clean-up offers nothing useful.
- `lqReplay` (5348) drops queued rows older than 14 days, so if the app isn't opened for 14 days while full, queued marks are lost.
- Fix:
  - Show "다른 쿼터 n MB" with a button that opens `/3q/` with the clean dialog.
  - In 3Q, run `xsAuto` (move 3Q numbering to IndexedDB) whenever the origin is above 50%.
  - Don't expire queued rows while `LSQ.err` is set.
- Test: none.

**D4. A 3Q backup in 4Q is refused, but with a generic message. — P3**
- Evidence: 5304 `j.app!==QC.bakApp → '백업 파일을 읽지 못했어요'`.
- Fix: if `j.app` matches another quarter in `QC.others`, say "3Q 백업 파일이에요 — 3Q 허브(⇄)에서 받으세요" with a link. The refusal itself is tested (`tests4/q_isolation.py:45`).

## Device sync

**E1. Other shadowing or typo bugs like the Q→QC one: none found.**
- I checked every global-name redeclaration (`T` at 3600/3685/3823/5310/5493/5510/5647/5699/5724, plus `G`, `D`, `H`, `F`). Each is a local in a function that doesn't read the global, and the `const F` blocks in `syncPull` are separate scopes.
- `q_ident` only lints `Q.`. A broader lint (no local redeclaring `T`/`QC`/`NS`/`LS`/`SYNC`/`XS`) would be cheap insurance.

**E2. Coverage of the synced key list (`SYNCK`). — mostly OK**
- Unsynced data keys:
  - `annAt.*`: only the backup reminder uses it, so the reminder is slightly off. P3.
  - `num.rd.*`: by design.
  - `jbst.*`: device-local.
- `exam.*`, `tgoal`, `tgoalDay`, `hlabel` and `blabel` sync, as intended.
- Group 'M' risk: with all 10 4Q subjects registered, `SYNC_SJ` (4963) already covers them. If a subject is added later while an old-build device still sends its keys in 'M', `syncApplyGrp` 5077 skips them (`syncGrp(k)!==q.g`) until both devices update. P3.

**E3. GitHub 403 / rate-limit handling is coarse. — P3**
- Evidence:
  - 5065: any 403/429 aborts the whole pull.
  - 5131: every 403 shows "요청 한도"; the back-off is max(60 s, Retry-After). A primary limit (`x-ratelimit-reset`, no Retry-After) is retried every minute.
  - A fine-grained token without gist permission (also 403) gets a misleading message and retries forever.
- Fix: read `x-ratelimit-remaining`/`-reset`, and tell "no permission" apart from "limit".
- The 1 MB truncation path (`truncated → raw_url`, 5062) is fine and is tested by `fakegist` REAL.

**E4. The full gist listing stops at 10 pages × 100. — P3 (probable)**
- Evidence: 5044. Both quarters' gists share the account: per context, 4Q needs up to ~102 groups and 3Q ~72, plus old v2 gists. With several Safari/home-screen/in-app-browser contexts this approaches 1000.
- Fix: stop on `Link` without `next`, raise the cap, or delete superseded v2 gists.

## Numbering (`num.js`)

**F1. Leaving the numbering screen throws away open dialogs without asking. — P3**
- Evidence: `num.js:2776` `leave()` calls `dlgClose()`, which discards a half-filled "새 문제" form or a ChatGPT preview. Editor text is safe: `endEdit` saves it (1248), and `flush` runs on `pagehide`/`visibilitychange` (2726).
- Fix: ask (or keep a draft) when the form has text.

**F2. The Word export file name uses the UTC date. — P3**
- Evidence: `num.js:2169` `new Date().toISOString().slice(0,10)`. Between 00:00 and 09:00 KST the file is named with yesterday's date.
- Fix: use the hub's `day()`.

**F3. The import dialog compares every candidate with every item on each redraw. — P3 (probable perf)**
- Evidence: `num.js:1660` calls `dupOf` for every candidate on each filter change or keystroke. `dupOf` (1610–1616) runs a bigram `dice` against every item: about 300 × 500 comparisons per redraw.
- Fix: cache `dupOf` per (candidate, target version).

ChatGPT import edge cases are already handled: malformed JSON, wrong format/version, duplicate ids (`dup`), more than 5000 items, files over 20 MB, a subject this hub doesn't have, and stories edited after export (`cf`) (`aiParse`/`aiPlan` 1903–1939). Ids can't collide between quarters (separate storage namespace) or between subjects (the key includes the subject; JB ids are `'jb:'+aid`, and the aid has a subject prefix). Nothing is hardcoded to 3Q subject ids (only comments mention them).

# (b) Probable — needs a browser check

1. **Stale "closed" flag ends a healthy session. — P3**
   - `tstate.cls` set by a closed owner tab is not cleared when another tab takes over (`trTake` 2902; cleared only on that tab's next visible event, 2982).
   - If the new owner is then reloaded or discarded more than 2 min later, the start check at 3283 asks "켜진 채 닫힌 세션" and after 60 s ends the session at the last record.
   - Fix: `delete ts.cls` in `trTake`.
2. **Old queued value can overwrite another tab's newer marks. — P3**
   - While storage is full, `ann` sits in `LSQ` (no storage event reaches other tabs). Another tab writes its own `ANN`; the later `lsFlush` writes the older queued copy over it.
   - Fix: on flush, merge the queued value with the stored one for `ann.`/`mk.` instead of overwriting.
3. **Wrong winner on numbering conflicts with clock skew. — P3**
   - `num.i` conflicts are decided by the device's own `u` timestamp, so a phone clock a few minutes off picks the wrong winner.
4. **Pasted base64 images in numbering stories are copied many times. — P3**
   - They are allowed by `sanitize` (61ff).
   - They bloat `num.i`, the 8-way numbering sync groups, and every IndexedDB snapshot (5 periodic + 3 per reason), all within the same origin quota as D3.

# Existing tests vs. these risks
- Covered:
  - session ask without input: `ux3_timer`
  - 12 h cap only with ask off: `ux3_timer`
  - two windows: `kt_sync`
  - `jbMove` for mk/fc/ann: `ux2_jblock`
  - 1 MB truncation: `fakegist`, `ux_sync_real`
  - 3Q backup refused, quarter isolation: `q_isolation`
  - quarter sync: `q_sync`
  - storage tiers / IndexedDB move: `ux15_storage`
  - ChatGPT import: `ux9_numai`
  - JB year follow: `ux21_numyrs`
  - lost-mark recovery: `ux22_markbridge`, `legacy_restore`
- No test:
  - A1 (sleep or input after the ask band, 12 h cap with default settings)
  - A2, A3, A4, A5
  - B1 (single candidate without context)
  - C1 (`jb_move` vs numbering)
  - C2 (review un-mark across devices)
  - D1 (restoring numbering), D2 (`old` store)
  - D3 (`oq` quota / origin full / 14-day expiry)
  - E3 (403/429 back-off)
  - (b)1 stale `cls`

# Prioritised top 15
1. A1 — sleep / 12 h / ask-band overcount (P1)
2. D3 — shared quota, no remedy in 4Q, 14-day expiry of queued writes (P1, probable)
3. D1 — no way to restore numbering from auto backups (P2)
4. D2 — invisible `old` store for sync-conflict losers (P2)
5. C2 — review un-mark resurrects across devices (P2)
6. C1 — `jb_move` not applied to numbering (P2)
7. B1 — mark moves silently after a rewrite (P2)
8. A4 — `tedit` grows forever and syncs every 3 min (P2)
9. A5 — 4Q import misses `tauto`/`tgoal`/`sessAsk` (P3)
10. (b)1 — stale `cls` ends a session (P3)
11. E3 — 403/429 handling (P3)
12. A3 — 3Q and 4Q timers both run at once (P3)
13. D4 — unclear message for a 3Q backup in 4Q (P3)
14. B3 — ★ card count includes removed cards (P3)
15. F2 + F1 — UTC date in the Word file name; `leave()` discards open dialogs (P3)