# R_NAV_이동·연동·빈과목 — 11-10 읽기 전용 점검 보고(담당 원문 · 줄 번호는 커밋 b714aca8의 tools/cons/shell.html)

I found 24 defects confirmed from the code and 8 that need a browser or device check. None of them repeats an item already marked fixed. Nothing in the repo was changed: every probe was a read-only grep, awk or Python read of `tools/cons/shell.html` and the packs.

Line numbers are for `/home/user/jbl/tools/cons/shell.html` at HEAD b714aca8, unless another file is named.

## (a) Confirmed from code

### Navigation, ↩ and keeping the user's place

**A1. P1 — After one failed figure download, that figure chunk never loads again until a full reload.**
- Evidence: `needImages` (2659):
  ```
  (imgWait[key]=imgWait[key]||[]).push(cb);if(imgWait[key].length>1)return; … s.onerror=()=>toast(…)
  ```
  On error the waiting callbacks are not cleared and the script tag is not removed. Every later call adds a callback, sees length > 1, and returns without asking again.
- What the user sees: lecture thumbnails (`fillThumbs` 4079) stay blank. `openImg` (4067) opens the viewer with a spinner that never ends (`mloading(true)`).
- How to hit it: one network drop while a lecture's figures load (phone on the subway), then keep studying that lecture.
- Fix: in `onerror`, run `delete imgWait[key]; s.remove();` and close the spinner (`mclose()` if it is open). The next call then retries.

**A2. P2 — ↩ back to 과목 홈, 기출 대장 or 내 표시 often lands at the top of the page.**
- Evidence: `retFrom` (3569–3571) stores only `pos` from `probePos()`, which needs `[data-aid]`. The subject home has none, so `r.pos=null`, and no scroll `y` is stored.
- `goRet` (3573) only uses history (which does carry `y`) when `history.state.ret===r.id`. Otherwise it calls `openDoc(r.s,r.d,r.t,null,{pos:r.pos})`. `savePos` (5466) skips `_home|_marks|_led`, so nothing restores the spot.
- How to hit it: 과목 홈, scrolled to a lecture card → footer "기출 n" (that creates a ↩ entry) → switch to the 학습 tab → ↩ → the subject home opens at y = 0.
- Fix: in `retFrom`, set `r.y=Math.round(scrollY)`. In `goRet`, pass `{pos:r.pos,y:r.y}` (`restoreAt` already falls back to `y`).

**A3. P2 — Search results expanded with "더 보기" collapse on browser back, and also whenever the search index fills in.**
- Evidence: `SMORE` (4726–4727) renders 20 results per subject. The click handler (4741) inserts the rest, but that expansion is never saved.
- `route` (3525) calls `search(st.q,{push:false,y:st.y…})`, which re-renders only 20 per subject and then scrolls to the saved y. That y can be past the shorter page, so the user lands on a different result.
- `sxDone` (4710) re-runs `search()` each time one subject's index finishes. For the first seconds after boot (10 subjects in 4Q) it collapses the list while the user is reading it.
- How to hit it: search a common word → 더 보기 → open result #35 → browser back.
- Fix: keep the expanded groups in `SQ` and in the history state (for example `smo:[gi…]`) and expand them again in `search()`. Also make `sxDone` append to the list, or keep the expanded groups when it redraws.

**A4. P2 — Typing in the search box wipes the whole ↩ stack.**
- Evidence: `search()` (4729) calls `retClear();retPill();` on every search. Closing the search returns through `history.back()`, and then `route` → `openDoc` has nothing to push back.
- How to hit it: JB card → 📖 정리본 chip (the pill appears) → type a term in the search box → Esc → back on the 정리본, but the pill to the JB card is gone.
- Fix: in `search()`, only clear the stack when the user opens a result. Keep it while the search view is just layered on top of the doc.

**A5. P2 — Jumps from "내 표시 모아보기", "★ 북마크 카드 → 강의로" and search results create no ↩ entry.**
- Evidence:
  - `marksGo` (5549): `openDoc(CUR.s,loc.d,loc.t,aid,{mark:o})` sets no `PENDRET`.
  - `data-cbmgo` (6355): `openDoc(CUR.s,t.dataset.cbmgo,'learn')` sets none either.
  - `resClick` (3618) sets none; this was audit #6's "search-result clicks" part, which the progress line does not mark as fixed.
- This goes against 7-2b ("칩·카드·…·바로 가기로 건너간 모든 이동에서"). These three are list → item jumps, not menu moves, so the "사이드바 이동에는 알약 없음" decision does not cover them.
- Fix: put `PENDRET=retFrom(b)` before each of these `openDoc` calls. For search, push a `{q:SQ.q,s:SQ.s,y}` return entry and teach `goRet` to call `search()`.

**A6. P2 — Ctrl/⌘+K from the numbering screen gives no ↩ back to the numbering.**
- Evidence: `qjPick` (3610) only sets the pill when the current screen is a document: `if(VIEW==='doc'&&!PENDRET)PENDRET=retFrom();`. `retFrom` (3569) also returns null outside documents.
- Meanwhile `numJB`/`numLEC`/`numDOC` (3575, 3616–3617) do give a numbering ↩ (`{num:1,…}`), so the same trip back is available one way and not the other.
- How to hit it: in 내 넘버링 → Ctrl+K → "JB 문제" → no pill back to the problem you were on.
- Fix: when on the numbering screen, use `PENDRET=Object.assign({num:1},JBLNUM.state(),{label:'넘버링'})`. Ideally reuse whatever `numJB` receives as `r`.

**A7. P2 — Learn-tab filters are lost on ↩ return, browser back and tab round-trips.**
- Evidence: the learn-tab group pills (`d.grp`, 4121) and `data-filt` "only-*" filters (4120: ⭐ 기출 카드만, 2회↑만, 내 표시만, 안 본 카드만) only toggle DOM classes.
- `fltRead`/`fltRestore` (6369–6384) save the 정리표, 한눈표, 비교표, 예상 and 그림빵 filters, but nothing from the 학습 tab. `mount()` rebuilds the page, so the filters reset after any trip away.
- Fix: add an `o.lg` (group) and `o.lf` (list of only-* classes) branch for `CUR.t==='learn'` in `fltRead`/`fltRestore`. Call `fltSave` from the 4120/4121 handlers.

**A8. P2 — Document hashes starting with `_` are never checked, so missing or unknown screens open empty or blank.**
- Evidence: `openDoc` (3626) only checks lecture keys: `if(d&&d[0]!=='_'&&!p.lect.find(…))`.
  - `#/PHARM/_final` opens an empty "🎯 최종 N제 0문항" page. The 11-04 fix only covered Ctrl+K and the subject switch.
  - `#/ANAT/_fig` opens an empty 그림빵 page.
  - `#/CONS/_xyz` falls through every branch of `mount()` (3719–3725) with `L` undefined and paints a blank page with no message.
- How to hit it: old bookmarks, a pasted link, or `lastBy`/"이어서" entries saved before a subject lost its N제.
- Fix: in `openDoc`, if `d[0]==='_'` and (`!SUBJDOCS.some(x=>x[0]===d)`, or `_final` with `!finN(p)`, or `_fig` with `!gbHas(p)`), switch to `_home` with the same toast already used for missing lectures.

**A9. P3 — Hidden tabs reached by hash switch silently, and number keys mean different tabs in different lectures.**
- Evidence: `docTabs` (3621) drops empty 비교표, 기출 and 예상 tabs. `openDoc` (3627) then falls back to `tabs[0]` without telling the user.
- Keys 1–9 index the visible tabs (4591: `bs[n-1].click()`). So "3" is 비교표 in one lecture and 기출 in another, and in a 4Q stub lecture (학습/정리표/플래시카드) "3" is 플래시카드.
- The help says "1~6 탭 바꾸기" (2561), but 31 of the 50 3Q lectures have 7 tabs, so key 7 (그림빵) works without being documented.
- Fix: say "1~7" in the help. Either keep fixed key slots (learn 1, sum 2, tbl 3, jb 4, pred 5, flash 6, fig 7) and skip missing ones with a toast, or put the key number on each tab label.

**A10. P3 — The same link behaves differently depending on where you press it.**
- Lecture card on the 과목 홈: tapping the card body (4116) creates no ↩. The footer "📖 정리본" button (3804, `data-lcs`) does create one. Both open the same place.
- A `.jbchip` inside 학습 cards and tables opens the in-place JB preview (5650). The identical chip in 예상/N제 cards (329 of them in CONS) navigates away (4141 `go()`).
- Labels for the same action vary in the pack HTML. CONS JB cards have "JB 원본 n쪽" (96) next to "원본 n쪽" (102). Chips to a lecture's 정리본 say "카드로 이동 →" (67), the bare lecture title, or "<title> 정리본 →". `nmDeco` (3579) only rewrites them inside a lecture's 기출 tab.
- Fix: pick one behavior per link type in the shell, and settle the labels in build4 before 4Q packs are built.

### 4Q stub subjects (10 packs with one `WAIT` placeholder lecture and 0 cards)

Checked against `docs/packs/OMS2.js`.

**A11. P2 — The subject home says "기출을 다 맞혔어요" (you got every past question right) for subjects with zero questions.**
- Evidence: in `actBtn` 'todo' (3671), `C.todo?…:C.ng?…:'<span class="small">기출을 다 맞혔어요</span>'`. `jbCount` (2655) gives `main=0` → `todo=0`.
- Shows on all 10 4Q subject homes right now.
- Fix: `if(!C.main)return '<span class="small">기출 자료 대기</span>'`.

**A12. P2 — The hub's main "시작하기 →" button opens a placeholder.**
- Evidence: `homeResume` (3394–3395) uses `resumeTarget` (3668) → `p.lect[0]`, which is `WAIT` "강의자료 대기 · 학습".
- The hub also shows every stub as a normal subject. `qEmpty()` (3379) only appears when there are no subjects at all. The subject table shows "0 / 0", and 오늘 할 일 says "오늘 할 일을 다 했어요" (3428).
- Fix: add an `isStub(p)` helper (`!p.stats.cards && p.lect.every(L=>L.k==='WAIT')`). Skip stubs in resume and "시작", gray their rows with the label "자료 대기", and show the `qEmpty` message when every subject is a stub.

**A13. P2 — "과목 바꾸기" from JB, 예상, 비교표, 한눈표 or 대장 lands on an empty page when the target is a stub.**
- Evidence: `sjKeepDoc` (6018) only falls back for `_fig` and `_final`.
- The empty pages say the wrong thing:
  - JB page: "조건에 맞는 문항이 없습니다." (3713), which implies a filter is on.
  - 예상: `predEmpty` (6394) "해당 문제가 없어요 — 전체 보기".
  - 비교표: `tblAllHTML` (5724–5728) has no empty message at all; only a lone "기출 연결 표만" button.
- 4Q will run for weeks with some real subjects and some stubs, so this will come up.
- Fix: in `sjKeepDoc`, return `_home` when the target doc's count is 0 (stats.main, predN, tblN). Give each subject-level doc a "아직 자료가 없어요" panel when its source array is empty.

**A14. P3 — The stub header, menu labels and lecture card text look broken.**
- `lpn` (3511) turns prof `'-'` into "- - 강의자료 대기". This shows in the side menu, 강의 바로가기 chips, Ctrl+K and the `#plec` dropdown.
- The subject-home hero (3640) renders `"${sjName} · ${p.profs}"` with empty profs (trailing " · ") and an empty `<h1>` (`p.en=""`).
- The lecture hero and lecture card say "- 교수" and "- · 26년도 자료".
- Fix: treat `'-'` as no professor in `lpn` and the hero. Omit the separator when `profs` is empty, and use `p.title` when `p.en` is empty.

**A15. P3 — Ctrl+K and the subject menu list dead screens for stubs.**
- `qjIndex` (3590) filters only `_fig` and `_final`. Each stub gets JB 문제, 기출 한눈표, 비교표, 예상문제 and 기출 대장, plus WAIT × (정리표, 플래시카드, ✎ 넘버링): about 80 dead entries.
- `navSubj` (5987) renders 비교표 and 예상문제 with blank counts.
- The Ctrl+K lecture items (3593) cover sum/jb/pred/flash but never 비교표 or 그림빵, although the docs say "강의(탭까지)".
- Fix: use the same count filter in both places (hide docs with 0), and add the `tbl` and `fig` tab items.

**A16. P3 — The placeholder card can be marked.**
- The `WAIT` card accepts ✓ done, ★ bookmark (D), highlights and blanks. When the real lecture replaces it, those marks become "위치 잃음" entries in 🖍 내 표시.
- Fix: add `kitnone` for `d==='WAIT'`, or hide `.acts` on that card.

**A17. P3 — Build-side text in the stub packs is wrong.**
- This lives in build4, not the shell.
- The learn tab says "📌 공부 전략 기출은 전부 풀되 … 이 문항들이 다음 해의 짤 후보" with zero 기출.
- The ledger says "카드 0개 = ." (an empty clause).
- The subject home shows an empty "2회 이상 출제 완짤 후보 0문항" section (3695).
- Fix: build4 should skip these lines when there are 0 cards, and the shell should hide `#htop` when `T.length===0`.

### Links pointing at things that do not exist

**A18. P2 — "JB 원본 n쪽" for a page missing from the image chunk silently shows page 1.**
- Evidence: in `openImg` (4077), `MI=Math.max(0,ks.indexOf(key))` turns −1 into 0.
- Real case: the 3Q PHARM 기출 대장 has buttons for `23q4-17…20`, but `docs/3q/packs/PHARM.img.jb23q4.js` has no pages 17–20.
- If a chunk had no pages at all, `SEQ` would be empty and `mshow` would throw on `x[0]`.
- Fix: if `ks.indexOf(key)<0`, call `mclose()` and show a toast "이 쪽 원본 이미지가 없어요". Add this check to link_audit.

**A19. P3 — One GERI cite chip points at a page that does not exist.**
- `tools/geri/lec_OHQ.txt:3` contains a literal `[[OHQ:쪽]]` inside a note, which builds a cite with `data-p="쪽"`.
- Pressing it shows the misleading toast "용량 때문에 넣지 않았습니다" (4069).
- Fix: the cite parser should only accept page numbers; check_links should flag non-numeric pages.

**A20. P3 — A 정리본 chip whose card number is out of range lands silently on the last reading spot.**
- `data-golec` → `openDoc(...,{id:'t-K-n'})` (4119). If card n no longer exists (cards renumbered when 26 material arrives), `el` is null. The code falls through to the saved tab position with no toast.
- None are broken in 3Q today (checked all 7 packs), but 4Q rebuilds will renumber cards.
- Fix: toast "그 카드를 찾지 못해 강의 처음으로 왔어요" and scroll to the top.

### Keyboard

**A21. P3 — Single-letter shortcuts fire while a `<select>` has keyboard focus.**
- `isTextField` (4554) excludes SELECT, and 4560 only guards Enter and Space.
- Tabbing to the JB 교수/연도 selects or `#plec` and typing a letter to jump within the list also triggers H, B, N, Q, C and so on.
- Fix: add `t.tagName==='SELECT'` to the early return for letter keys.

**A22. P3 — Ctrl/⌘+K opens quick jump in the middle of editing a numbering story.**
- The 3615 handler only exempts `#memo`. Leaving does save (`JBLNUM.leave`), so no text is lost, but the editor closes unexpectedly.
- Fix: also exempt `#numv [contenteditable]`, or require the editor to be closed.

### Phone and touch

**A23. P3 — The "답 바로 보기 ▸" target in search results is 28 px tall and not focusable.**
- `.sres .sans{min-height:28px}` (625) is below the 32 px rule.
- It is a `<span role=button>` inside the result `<button>`, so keyboard users cannot reach it.
- Fix: `@media (pointer:coarse){.sres .sans{min-height:36px}}`. Better, move it out of the button as a sibling `<button>`.

**A24. P3 — A deep link to a subject that is still loading replaces the URL with `#/`.**
- `route` (3526) → `home({push:false})` → `histSet(…,'#/',false)`. If the pack fails to load, or the user reloads, the link is gone.
- Fix: keep `location.hash` when `PL.lost` is set (do not replace it), or put the hash back on failure.

## (b) Probable issues, needing a browser or device check

1. **P1 (iPad home-screen app).** The manifest says `display:standalone`, and there is no in-app Back button besides ↩. A5 (search, 내 표시, 북마크 카드) and the reverted menu ↩ then leave no way back on iPad, unless an edge swipe works in standalone mode. The code comment 3525 assumes it does. Test on the actual iPad home-screen app.
2. **P3.** `PL.lost` (3526, 6220) is not cleared when the user navigates away. If the user returns to the hub before the pack arrives, they get pulled to the old deep link. Only happens on a slow network.
3. **P3.** `#jbpeek` is placed with absolute coordinates (5640) and stays open while J/K or scrolling moves the page. The popup can float away from its chip.
4. **P3.** For a stub, 예상 shows the predBar note "실제 기출이 아닙니다" plus filter chips on an empty page, and probably the "해당 문제가 없어요 — 전체 보기" panel. Check how `_pred` and `_sum` render with 0 items.
5. **P3.** Searching "자료" or "대기" in 4Q returns 10 placeholder hits (the WAIT cards are indexed). `sxUnits` could skip lectures with key `WAIT`.
6. **P3.** The 23q4 missing pages may be on purpose (blank pages). Even so, the buttons should not exist.
7. **P3.** On the 학습 tab on phone, tab row and mini bar both scroll sideways with the scrollbars hidden. The fade mask (`.dtrow.ovr`, 2193) exists, but check that it actually appears on 393 px for 4Q lectures with 7 tabs.
8. **P3.** Subject-switch buttons for packs that have not loaded do nothing when tapped (6022, `if(!PACKS[S])return;`). There is no toast like the hub's "불러오는 중".

## Deferred items, with a view on each

| Deferred item | Still worth doing? |
|---|---|
| Fit 비교표/정리표 column widths for visible tables first | Yes, before PHARM4 and GERI4 content lands. Test it together with position restore. |
| 4Q figures as webp files plus URLs | Yes, and the most valuable of these: it also covers A1 (no retry) and audit #10 (memory). Do it before the first 4Q figures are built so packs never carry base64 again. |
| Don't render all search results | Mostly done already (`SMORE`, 20 per subject). What remains is A3: the expansion is lost on back and on index updates. The matching loop over the whole index still runs on every keystroke, but it is debounced at 250 ms, so that part is fine. |
| Content ★ (4Q content rule) | Yes, as a `check_*` lint on the 4Q source text, not a display-time replacement. |
| Menu ↩ (reverted) | Fine to keep reverted. A5 is a different category (list → item) and should get the ↩. |
| content-visibility (reverted) | Only together with a virtual list. Not before 4Q. |

Items from the 11-04 audit that appear in neither the fixed nor the deferred list:
- #11 (all packs loaded on every start): trivial now (10 × 14 KB) but about 60 MB once 4Q content lands. Load the current and most recent subjects first.
- #19 (phone hero pushes the tab row down).
- #20 (no offline use).

## Top 15 by priority

1. **A1 P1** — Images never retry after one failed load. Fix: `onerror` clears `imgWait`, removes the script and closes the spinner.
2. **A11 P2** — Stub subject home says "기출을 다 맞혔어요" (all 10 4Q subjects now).
3. **A12 P2** — Hub "시작하기 →" opens the placeholder; stubs look like real subjects. Add `isStub`.
4. **A13 P2** — Subject switch lands on empty JB/예상/비교표 pages with "filter" wording. Fix in `sjKeepDoc` and add real empty-state panels.
5. **A2 P2** — ↩ to subject home, 대장 or 내 표시 loses the scroll spot. Store `y` in `retFrom`.
6. **A3 P2** — Search "더 보기" collapses on back and on index refresh.
7. **A5 P2** — No ↩ from 내 표시, 북마크 카드 or search results. Check (b)1 on the iPad home-screen app first.
8. **A4 P2** — Searching wipes the ↩ stack.
9. **A8 P2** — Unchecked `_` hashes (`_final`, `_fig`, unknown names) open empty or blank pages.
10. **A18 P2** — Missing JB original page shows page 1. Guard in `openImg` and add to link_audit.
11. **A7 P2** — Learn-tab filters lost on return. Extend `fltRead`/`fltRestore`.
12. **A6 P2** — Ctrl+K from numbering has no ↩ back.
13. **A14 + A15 P3** — "- - 강의자료 대기", empty hero, about 80 dead Ctrl+K entries for stubs.
14. **A9 P3** — Help says 1~6 but there are 7 tabs; key numbers shift between lectures.
15. **A10 + A17 P3** — One behavior and one label per link type, and build4 stub texts. Fix in build4 before 4Q packs are built.