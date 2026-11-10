# R_DESIGN_설계 — 11-10 읽기 전용 점검 보고(담당 원문 · 줄 번호는 커밋 b714aca8의 tools/cons/shell.html)

I could not write a plan file: this agent has no file-editing tool, so the full plan is below for you to merge. Nothing in the repo was modified and no tests were run; everything here comes from reading code.

## 0. What I verified, and where the brief needs correcting

| Claim | Verdict | Evidence (`/home/user/jbl/tools/cons/shell.html` unless noted) |
|---|---|---|
| T1 sleep overcount | Confirmed | `trTick` 2969 checks the 12 h cap before anything else. `sessFlush(now)` 2972 records the whole gap before `trAsk` 2958-2960 runs, and the `visibilitychange` handler 2982 also flushes on becoming visible. If input resumes, the band closes at +30 min and the gap stays. |
| T1 constraint | New | `tools/tests/ux3_timer.py` line 125 asserts that with `sessAsk=0` a 12 h sleep is counted in full ("되묻기 끔 → 12시간 상한"). The fix must leave 끄기 alone or change that test on purpose. |
| V1 chunk never retries | Confirmed | `needImages` 2659: `onerror` only toasts. `imgWait[key]` keeps length ≥ 1, so every later call returns early; the script tag stays and `openImg`'s spinner never closes. |
| N2 review grades | Confirmed | `tools/num/num.js` 2262-2263: un-mark splices `r.h`, re-grade replaces the entry with a new `t`. `mergeData` 4784 unions by `t\|s`, and `syncApplyGrp` 5083 always unions `SYNCLOG` keys. |
| S1 shared quota | Partly | `lsScan` counts other-quarter keys (`oq`) in `used`, so 4Q's own numbering auto-moves to IndexedDB early. Nothing in 4Q can free 3Q data, and non-numbering keys cannot move. `lqReplay` 5348 drops rows older than 14 days; `at` is refreshed on each `lqWrite`, so this only bites after 14 days without opening the hub. |
| S2, S4, M1, N1 | Confirmed | `STUDY` 5274 has no `num.`/`exam.`; 5304 gives a generic message; `pick` 4224 accepts one candidate at ≥ 4 chars; `jbMove` 4896-4901 never touches `num.i.*`. |
| "Word export must fetch" | Not needed | `dxImages` (`num.js` 2104-2112) draws already-loaded `<img>` elements to a canvas, and the export waits for `img.complete` (2055, 2136). Same-origin file URLs work unchanged. |
| Who reads `IMGS` | Only 4 places | `JBLHUB.images` 2657, numbering `host.img` 3363, `openImg` 4067-4077, `fillThumbs` 4079. `fillThumbs` has 5 callers (mount, peek ×2, 4033, 4117). |
| Pack size | Correction | Main packs are HTML text; inline data-URIs are only 1–11% (PHARM 3%, ANAT 11%). File images will not shrink main packs or boot memory. |
| Table lag | Root cause found | `tblFit` 5733 → `twApply` reads `clientWidth`/`getComputedStyle` then writes a colgroup, per table, so there is one forced layout per table. `TWT` and `CF.stats` are WeakMaps keyed by DOM node, lost on every `mount`, which is why repeat opens are not cached. |
| Repo size | Measured | Shallow clone; blobs reachable from `origin/main` pack to 612 MB, of which image chunks are 297 MB (243 versions of 88 current chunks). `docs/` is 281 MB. |
| Pack budget | Risk | `tools/tests4/q_perf.py` fails any 4Q pack over 6.0 MB; 3Q PHARM is 8.7 MB. A PHARM4-sized subject will trip it. |

## 1. Workstreams (each group deploys on its own)

Every hub change follows the same path: edit `tools/cons/shell.html`, run `tools/sync_common.py`, `tools/rehub.py`, then tests. First log the user's request verbatim in `guide/피드백기록.md`.

### W0. Safety net (tools only, no deploy)
1. Fixture site in `tools/tests4/qsite.py`: 4Q identity serving 3Q packs (design in §5).
2. Triage the 37 baseline failures into a status manifest (§5). Investigate `ux_u18`, `ux4e_names`, `ux4f_O` first.
3. S6: extend the `q_ident` lint to flag `const|let|var` or parameter names `T|QC|NS|LS|SYNC|XS|PACKS|CUR` inside the hub closure.
4. Capture a perf baseline on the fixture: CDP `Performance.getMetrics` (LayoutCount, RecalcStyleCount) per open, and heap after 15 lectures.

### W1. Study time (deploy 1)
| Item | Where | Minimal change |
|---|---|---|
| T1 | `sessFlush` 2899, `trTick` 2964, `trAsk` 2958, boot 3283, 2982 | See §2. |
| T2 | `tFlush` 2699, `sessFlush` | If `Date.now() < T.t0 − 2 s`, rebase `T.t0` and `T.last` to now. If `ts.seg > now + 2 s`, set `ts.seg = now` and clamp `ts.li`. |
| T6 | `trTake` 2902 | Delete `ts.cls`; delete `ts.hid` when the document is visible. |
| T4 | `tUnrec` 2893, `teLog` 3012, `teMerge` 3035 | Trim entries get a deterministic id per (device, day, subject, doc, kind) and accumulate `ms`. `teMerge`: for the same id with `agg`, the later `at` wins. Old entries stay untouched. |
| T5 | import block 2618 | Second pass under a new flag `qimport2` (the first flag is already set on devices). Import only global keys, never overwrite. Needs your decision (§6). |
| T3 | BroadcastChannel 2837 | A cross-quarter channel name from the registry (`quarters.json` top level, emitted by `qcfg`). Auto timing yields to the other quarter's window. It only works in 3Q once the 3Q index is regenerated. |

Tests: new `q_timer.py`; regress `ux3_timer`, `ux3_rest`, `ux3_fixes`, `ux3_tedit`, `ux4g_A`, `ux5_sess` on 3Q staging.

### W2. Records: storage, sync, backup, numbering, marks (deploy 2)
- **S1**:
  - 4Q storage warning shows "다른 쿼터 허브 기록 n MB" with a link to the 3Q hub. The 3Q hub's own `xsAuto` then moves its numbering, because usage is counted origin-wide.
  - `lqReplay` 5348: remove the 14-day drop; keep rows until written, and show the count and oldest date in the error band.
- **S2**: `studyPlan`/`studyReplace` 5275-5292 gain an opt-in "넘버링도 되돌리기" set (`num.i|x|r|rl|rs`, `num.subj`, `exam.`). These keys must go through `stGet/stSet/stDel`; the current raw `localStorage` calls would bypass the IndexedDB tier.
- **S3**: list the IndexedDB `old` store (`xsOld` 5381) in the restore dialog with "되살리기"; prune beyond 30 days or 200 rows.
- **S4**: `fileRestore` 5304: when `j.app` matches another quarter (add `bakApp` to `qcfg` `others`), say which quarter and offer its hub.
- **S5**:
  - `gh()` errors carry `retry-after` and `x-ratelimit-*`. At 5065 and 5131, treat 403-with-zero-remaining and 429 as back-off, and only 401 as a token problem.
  - `syncList` 5044: page until a short page (cap 30) and warn at the cap.
- **N2**: `rMark` writes a tombstone `{t, s, x:1}` instead of splicing. Merge key becomes `s` with latest `t` winning (4784 and the 5083 path). Readers skip `x`. One-time dedupe on load.
- **N1**: `jbMove` also rewrites `src`/`ref` ids in `num.i.<S>.*`. On collision keep the newer `u` and mark the other as duplicate, never delete. Run `autoBak(true,'misc')` first.
- **M1**: `pick` 4224: a single candidate needs matching context unless the text is long (≥ 12 normalised chars). Otherwise the mark goes to the existing lost-marks list. This is user-visible, so it is a decision (§6).
- **M3**: ★ count 6327 filters by existing cards; `migrateAids` 5492 also maps `cbm`/`lrd`.

Tests: new `q_store.py`, `q_backup.py`; extend `q_sync.py`; regress `ux_sync*`, `ux15_storage`, `ux2_backup`, `ux2_merge`, `ux12_numrev`, `kt*`, `legacy_restore`.

### W3. Stubs and navigation (deploy 3, the only group visible today)
- **Stubs**:
  - `tools/cons/build4.py` emits `pack['stub']=True` when `LEC_ORDER==['WAIT']` and there are no questions, and drops the empty strategy and "2회 이상" texts.
  - Hub adds `isStub(p)` (flag, or `!p.order.length && p.lect.every(L=>L.k==='WAIT')`).
  - Apply it in `homeResume` 3394, `resumeTarget` 3668, `actBtn` 3671, `sjKeepDoc` 6018 (go to `_home`), `mount` 3713, `predEmpty` 6394, `tblAllHTML` 5724, `lpn` 3511, hero 3640, `qjIndex` 3590 (subject home only), `navSubj` 5987. Make the WAIT card unmarkable.
- **V1**: `needImages` `onerror` retries once after 1.5 s with a cache-bust. On the second failure it clears `imgWait[key]`, removes the script, closes the spinner and toasts with [다시].
- **V2–V14**:
  - V2: `retFrom` also stores `scrollY`; `goRet` passes `{pos, y}`.
  - V3/V4: keep the "더 보기" state in `SQ`/history state, and do not `retClear()` in `search()`.
  - V5/V6: set `PENDRET=retFrom()` in `marksGo`, `data-cbmgo`, `resClick`, and for Ctrl+K from numbering.
  - V7: add learn filters to `fltRead`/`fltRestore`.
  - V8: one `docOk(p,d)` check in `openDoc` 3626, shared with `sjKeepDoc`.
  - V9: fix the help text.
  - V10: one behaviour and one label per link type.
  - V11: `openImg` opens the nearest existing page with a toast, not page 1.
  - V12: ignore single-letter keys when a `SELECT` is focused; no Ctrl+K while the numbering editor has focus.
  - V13: 32 px target.
  - V14: `route` 3526 keeps the deep-link URL while the pack loads.

Tests: new `q_stub.py`, `q_links.py`, `q_crawl.py`; regress `ux_nav`, `ux26_links`, `ux_srchkeep`, `ux4_nav`.

### W4. Images as files for 4Q (deploy 4, dormant until a pack carries the flag)
See §3.

### W5. Lag (deploy 5)
See §4.

### W6. Small numbering fixes and design leftovers (deploy 6)
- N3: `leave()` (`num.js` 2776) saves or asks about open dialogs.
- N4: local date in the export filename (`num.js` 2169).
- N5: memoise `dupOf` per redraw (`num.js` 1610-1660).
- The four 10-24 leftovers: one-line focus tab row, quieter secondary buttons, lighter sidebar badges, tool pill at 1280.
- After `num.js` edits run `tools/num/build_num.py`.

Tests: `ux8_num`, `ux20_numdocx`, `ux_v3phone`, `ux_align`, `ux_fbar`, `audit_design`.

### W7. Process and docs (commits only, can run in parallel)
- Fix old-layout paths in `.claude/skills/jbl-update/{SKILL,RULES,QA,AGENTS}.md`.
- Resolve RULES 11 against 14 c⑥ (decision, §6).
- Carry the ~20 HIT lessons into RULES.
- Reference 14 c⑥ from AGENTS T/P/FN and `guide/handoff/Q4_RULES_BRIEF.md`.
- Add a content-★ check to `tools/check_lec.py` for 4Q manuscripts.
- Update `tools/SPEC.md` and `guide/정리본_원칙.md` for each hub change.

## 2. T1 design: sleep- and idle-safe sessions

**Kept as is:** 06:00 day boundary (`tSplit`/`nextMid`), auto timing (already capped at last input + 1 min), auto and manual rest (capped by `restMax`), the 5-second switch rule, the "closed session" question, and wall-clock counting of no-input study up to the ask threshold.

**Where the last tick lives**
- Persisted: reuse `tstate.at`. `sessFlush` already writes it every ≤ 20 s, on state changes, and on hide/pagehide. No new key, no extra writes, device-only (`MSKIP`).
- In memory: `T.tk = Date.now()` at the end of every `trTick`, for 1 s resolution inside a live page.
- Gap `g = now − max(ts.at, T.tk)`.

**Classification** (owner window, `st==='sess'`), with `li = max(ts.li, T.inp, ts.t0)`, `idle = now − li`, `A = sessAskMin()` in ms:

| Case | Condition | Result |
|---|---|---|
| Clock went back | `g < −2 s` | Rebase (T2); record nothing for the negative span. |
| Live | `g < 90 s` | As today. |
| Suspended, short idle | `g ≥ 90 s`, `idle < A` | Count it. This is the off-screen paper study the user asked for (iPad locked beside the notes). |
| Ask window | `A ≤ idle < A+30 min` | Show the ask band with `T.askAt = li + A`, not wake time, so the 30 minutes run on the real clock. |
| Expired | `A > 0`, `idle ≥ A+30 min` | End the session at `li + 1 min`, exactly what a live page would have done, without recording the gap first. |
| 끄기 | `A = 0` | Unchanged: 12 h cap (decision D1). |

**Changes**
1. Helpers `sessLi(ts)` and `sessDead(ts,now)` (`st==='sess' && A>0 && now−li ≥ A+30 min`).
2. `sessFlush`: when dead, `lim = min(lim, max(ts.seg, li+60000))`. This protects every caller, including the `visibilitychange` flush at 2982.
3. `sessFlush`: while `idle ≥ A`, record only up to `li + A`. The rest stays pending: still shown live through `ts.seg`, recorded when the user presses 계속 or gives input. This shrinks later trims, which also helps T4.
4. `trTick`: check `sessDead` first, before the H12 check at 2969. Call `trStop(li+60000, …)`, then show a new band: "마지막 입력(23:10) 뒤 7시간 40분 동안 입력이 없어 23:11에 끝냈어요 [그대로] [📖 공부했어요 — 시간 넣기]". The second button opens the calendar's existing "+ 시간 추가".
5. Boot 3283: if `sessDead`, take the same path instead of the closed-session question, so "지금까지로" cannot add up to 12 h by a mis-click.
6. On `visibilitychange` to visible and on `pageshow`, call `trTick()` at once. Apply the same clamp in `sessLiveFor` 2876, `trSessMs` 2857 and `trFocusMs` 2861 so the clock never flashes an inflated number.

**Test compatibility** (traced by hand, not run)
- `ux3_timer` 104-121: 30 min counted, band at 90, stop gives +1 min, 121 min auto-ends at +1 min. All hold.
- `ux3_timer` 125 (끄기, 12 h): unchanged.
- `ux3_fixes` and `part_closed` seed `li` 50 min old, so they are not dead and keep the existing band.
- Before coding, grep the tests for seeded `'st': 'sess'` states with `li` older than 120 min.

## 3. Images as files (4Q only)

**Recommendation: do it now, and also add retry and eviction for chunk packs.** 4Q has zero images published today, so switching now costs no migration. Switching after content ships would republish every image (~300 MB of extra git history).

| | Chunks + evict + retry | Files |
|---|---|---|
| Memory growth (129 → 254 MB) | Fixed (LRU of 2 lecture chunks) | Fixed (no strings in JS heap) |
| First figure at 20 Mbps | Still 2–4 s (whole 4.5–8.3 MB chunk) | About one ~47 KB request |
| Published size | Same | About 25% smaller (binary instead of base64) |
| Git churn | A one-figure change rewrites a 5–8 MB blob | Only changed images are new blobs |
| Code | ~30 lines in the hub | build4 + hub + 3 tools |

**build4 (`/home/user/jbl/tools/cons/build4.py` 1649-1669, 1718-1724, 1786-1797)**
- Switch per quarter: `quarters.json` `4q.img = "files"`; 3Q has no key and keeps chunks even if rebuilt.
- Format unchanged from the 10-04 approval: WebP q72, width 1100, method 6. JB original pages stay JPEG without recompression.
- Path: `docs/packs/img/<SID>/<KEY>-<page>.<h8>.webp`, and `jb<ed>-<page>.<h8>.jpg`. `h8` is the md5 of the file bytes, so URLs are immutable and need no `?v=`.
- Pack manifest: `pack['imgf'] = {'lec': {'CRK-30': 'a1b2c3d4', …}, 'jb': {…}}` (about 20 KB per subject). The existing `PV` busts the manifest. `imgv` stays empty.
- `tools/<sid>/img_lock.json` maps key → (source md5, output hash). Unchanged sources are not re-encoded, which avoids churn between Mac and cloud Pillow versions.
- Deletion keeps the previous generation of files, so a client holding a cached old pack does not hit 404s.
- No-source rebuilds (`prev_images`, `img_dims` in `/home/user/jbl/tools/jblpaths.py`) read the previous manifest and file headers.
- The single-file edition in `work/` still inlines `JBLHUB.images` data from the same bytes.
- JB crops inside cards stay inline for now. Move them to files only if a pack breaks the size budget (RAD is the likely one).

**Hub**
- One resolver: `IMGS[s]` entry if loaded, else `p.imgf` URL, else the chunk path. The first rule covers the single-file edition.
- `fillThumbs` 4079: for `imgf` packs set the URL through `imgSet`; skip `needImages`; a key missing from the manifest removes the figure, as today.
- `openImg` 4067: build `SEQ` from manifest keys; no spinner wait.
- `host.img` 3363 returns the URL. `gbCompose` and Word export work on same-origin URLs.
- `chunkOf`/`imgalias` are used only for chunk packs.
- Missing file: one capturing `error` listener retries once with a cache-bust, then shows a same-size placeholder with [다시]. Width and height are already in the HTML, so nothing shifts.
- Print: on `beforeprint`, set `loading='eager'` and flush `imgSet`'s deferred sources.
- `num.js` `sanitize` (74, 243): a pasted `packs/img/<SID>/<KEY>-<p>…` source becomes a `data-lecimg` placeholder instead of being stripped.
- Chunk packs: V1 retry plus an LRU eviction of lecture chunks on leaving a lecture.

**Tools:** `tools/verify.py` (every manifest file exists; every `data-img` and cite key resolves), `tools/check_links.py`, `q_perf.py` (per-file budget replaces the chunk budget).

**Size outlook (estimate from 3Q):** ten subjects would add roughly 350 MB as base64 or 265 MB as files, so `docs/` lands near 600–680 MB against the 1 GB Pages limit. `.nojekyll` is already present; about 12k small files is fine.

## 4. Cutting heavy-tab lag without breaking position restore

| Option | Verdict | Expected gain | Why |
|---|---|---|---|
| (a) Visible-first table fit with caches | Now | Table tabs 0.6–1.2 s → roughly 0.15–0.3 s (estimate) | Removes one forced layout per table. |
| (b) Defer post-mount readers | Now, small | 5–15% | On learn/JB/pred the cost is one unavoidable layout of 4–54k nodes; deferring only changes who pays. |
| (c) Chunked mounting | Not now | – | JB filters and counts, one-at-a-time, find-in-page, print and highlights all assume the full DOM. |
| content-visibility with exact heights | Stage 2, behind a flag | 40–80% on repeat opens (measured 11-04) | The only large lever for learn/JB/pred. |
| (d) On-demand packs | Scheduling tweak now; "lite packs" later | Boot heap | 138 `PACKS` references; too wide before content. |

**(a) in detail**
- Split `twApply` 6187 into measure (reads only) and apply (writes only). `tblFit` runs all reads, then all writes.
- Fit synchronously every table at or above the restore target (known in `openDoc` 3650-3655), or the first two screens when opening at the top. Tables below the anchor cannot move it.
- Fit the rest in idle slices of about 8, with an IntersectionObserver (1500 px margin) pulling tables forward as they approach.
- Any `goEl` jump flushes the queue first. If a late fit lands above the viewport, wrap it in the existing `keepAt` 6259.
- Cache the `twSolve` result per (pack fingerprint, table index, width bucket, font scale, mode) in a Map. Persist `colFit`'s `CF.cache` in a device-only key (add to `MSKIP`).

**(b)**: create `learnSpy`'s observer and do `navRender`'s scroll-into-view in a frame after restore. Leave `Kit.restore` synchronous.

**Stage 2 (content-visibility)**
- The first open of a doc lays out fully, then records every card's height per (doc, tab, width bucket, view state) in a device-only cache.
- Later opens set `contain-intrinsic-size` to the recorded height and enable `content-visibility:auto`, so placeholders are exact and `goEl` lands correctly.
- Bulk operations (expand all, 압축, print) switch it off, run, re-measure and switch it back on.
- Ship it only if `ux_nav`, `ux_kitfrev`, `ux_marks`, `ux2_jbq` and the new `q_pos` pass with the flag on.

**(d)**
- Now: in `plEnd` 6218, start the next pack only after 1.5 s without input and while visible.
- Hub home reads far more than a summary (`jbCount` needs `p.cards`, `resumeTarget` needs `p.lect`, plus the review queue).
- A later design that fits: `fill_index` embeds a "lite pack" per subject (stats, lecture list, ids), which `openDoc` upgrades on demand. Guard it with a differential crawl (lite on vs off, same text on every screen).
- Decide after measuring with real 4Q content.

## 5. Test strategy

**Fixture (feasible with no registry change)**
- `qsite.py` gains `build_fixture()`. It calls `rehub.one('4q', out=work/_tmp/fx, src=docs/3q)` with an in-process override of the subject list, so 3Q packs load under 4Q identity next to the real stubs. That exercises 4Q storage names, first-run import and sync against rich content.
- A second variant converts one subject's chunks to files and injects `imgf` into the pack copy, to test the file path before any build4 output exists.
- Later, for build4 itself: a tiny synthetic subject built with `JBL_DOCS=<scratch>`. It needs a `"test": true` quarter that `quarters.py` excludes from `live()`, `others` and `--site`. Only worth doing when W4's build side lands.

**New `tools/tests4/` tests** (discover subjects, lectures and cards from `__h.PACKS`; pass with zero work on a stub-only hub)
- `q_timer` – T1/T2/T6 with the fake clock: sleep at 100 min and at 8 h, the 12 h case, clock moved back.
- `q_stub` – every stub: wording, no "시작하기" into WAIT, Ctrl+K entries, subject switch.
- `q_pos` – at 3 depths on the richest learn/sum/tbl/jb/pred/`_tbl`/`_jb` docs, check same card within ±2 px after tab switch, back/forward, reload, ↩ and "이어서". Check at 100 ms and at 1.5 s.
- `q_links` – every chip type lands on an existing target and ↩ returns.
- `q_img` – file images load, the modal pages, missing-file placeholder, chunk retry.
- `q_crawl` – every doc × tab: no errors, blanks, `undefined`/`NaN`, or sideways overflow.
- `q_store`, `q_backup` – W2.
- `q_perf` (extended) – LayoutCount budgets, heap after 15 lectures, 4× CPU opens.

**3Q staging** stays the regression corpus (`JBL_Q=3q rehub.py --q 3q --stage`). Each group runs its named tests plus a full `ux_all` in the background.

**The 37 baseline failures**
- Add `tools/tests/STATUS.json`, read by `ux_all.py` and `full_check.sh`.
- ~12 local-only: marked `local`, reported as SKIP when `work/jb` or materials are absent.
- ~20 stale: retire to `tools/tests/retired/` with a one-line reason and the superseding test. Repair instead when the test guards records (`legacy_restore*`, `ux2_sum_mig`, `ux3_compat`).
- 2 harness: exclude `fakegist` (a helper) from the glob; fix `fmt_cases`.
- 3 possible real bugs: investigate in W0, fix in W3/W6.
- Target: `ux_all` on staging reports PASS plus a SKIP list.

## 6. Risks, rollback, decisions, and what not to do

| Group | Main risk | Guard and rollback |
|---|---|---|
| W1 | Under-counting real paper study | Suspended gaps under the ask threshold still count; one click adds time back. Revert the hub commit; no format change except aggregated trims, which old code reads as normal entries. |
| W2 | Touching stored records | `autoBak` before the N1 rewrite; tombstones and new fields are ignored by old code; nothing is deleted. |
| W3 | Wrong stub detection hides a real subject | Explicit `stub` flag, with a heuristic only for today's packs. |
| W4 | 404 during cache mix; encoder churn | Two-generation retention; lock file; chunk mode remains as fallback. |
| W5 | Position drift | The four guard tests plus `q_pos`; Stage 2 behind a flag. |

Every deploy is one commit; rollback is `git revert` plus push.

**Not before content arrives:** splitting `ann.<SID>` per lecture (M2: measure highlight cost on a 3,000-mark fixture first), chunked mounting, lite packs, a service worker, rebuilding 3Q packs, wholesale rewriting of 3Q tests.

**Decisions to batch for the user**
- D1. With 되묻기 = 끄기, should a script-suspended gap over 3 h be dropped? Default: leave as is, relabel the option.
- D2. T5 extra settings to carry into 4Q (`tauto`, `tgoal`, `sessAsk`, JB auto-advance, and so on).
- D3. Regenerate the 3Q index from the current shell (needs `JBL_UNFREEZE=1`) so 3Q gets T3, S1 and V1; bundle it with the "2026 출제" update.
- D4. M1 stricter relocation: some marks will show as lost instead of silently moving.
- D5. S2: let 되돌리기/교체 include numbering.
- D6. The 6.0 MB pack budget against a PHARM-sized 4Q subject: raise it, or split packs.
- D7. RULES 11 against 14 c⑥ for "상" share.

### Critical Files for Implementation
- /home/user/jbl/tools/cons/shell.html
- /home/user/jbl/tools/cons/build4.py
- /home/user/jbl/tools/num/num.js
- /home/user/jbl/tools/tests4/qsite.py
- /home/user/jbl/tools/quarters.py