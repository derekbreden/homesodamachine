# Video workflow — Snapshot 2026-05-08

**This is a point-in-time snapshot, not a living document.** Captures the workflow that actually worked on the first end-to-end execution of the Mac edit pipeline — *I've Never Tapped — First NPT Threads in 316L Stainless*, shipped 2026-05-08 (https://youtu.be/MXtzmCHN1mw).

**Supersedes** [`2026-05-04-first-execution.md`](2026-05-04-first-execution.md), which captured the iPhone + iMovie workflow that shipped *First Weld*. The iMovie path is preserved as a fallback for very short single-angle clips; for everything else, the Mac pipeline wins on sync precision, cross-dissolves, captions, multi-source stitching, and iteration speed.

The narrative below (what shipped, what changed, what bit) is what's frozen here as historical record. The current procedure lives in [`../workflow.md`](../workflow.md).

## What shipped

- **Title:** *I've Never Tapped — First NPT Threads in 316L Stainless*
- **Duration:** 6:38
- **URL:** https://youtu.be/MXtzmCHN1mw
- **Source material:** 9:13 lav (DJI) + 9:02 GoPro for Part 1 (drilling the birch fixture, first c-clamp tap attempt failing); 28:48 lav + 28:49 GoPro for Part 2 (clamp re-orientation, successful first NPT tap, depth measurement, "result is inconclusive"). Two recordings, same day, separate sessions.
- **Final video structure:** 2 s title card → 5 cuts from Part 1 → 5 cuts from Part 2 → close. Cross-dissolves at every boundary (0.4 s xfade). Section labels ("Drilling," "Cleanup," "Part 2 — later that day," "Measuring depth") at the major narrative beats. One tool annotation ("WEN 8\" benchtop drill press") at the open. Burned-in subtitles throughout, ~3.5 s / 7-word chunks.

## Milestones

- **2026-05-08** — First Mac-pipeline video published. End of iMovie-only mode for narrative content. The pipeline is no longer hypothetical; the scripts in `marketing/video/` are exercised, debugged, and committed.

## What changed from 2026-05-04

- **iMovie → Mac edit pipeline.** Custom Python + ffmpeg scripts (sync, segment, cut, captions) in `marketing/video/` replaced iMovie. Driven from Claude Code; the Mac mostly idles during long-running steps from the user's perspective.
- **Sync went from manual to waveform cross-correlation.** [`sync.py`](../sync.py) finds the offset by cross-correlating the lav audio against the GoPro's own audio (clap as the shared transient). Confidence 5+ on both 2026-05-08 recordings. iMovie's by-ear sync is now strictly worse for this use case.
- **Whisper-driven scene clustering.** [`segment.py`](../segment.py) groups speech into candidate scenes by gap + pad. Eliminates the "where do the cuts go?" guesswork; the visual-analysis pass refines from a defensible starting point.
- **Cross-dissolves became cheap.** [`cut.py --fade 0.4`](../cut.py) applies a 0.4 s cross-fade at every cut boundary. Took some debugging — chained xfade is famously fragile in ffmpeg — but the gotchas are captured in cut.py's header now (TL;DR: `setpts=PTS-STARTPTS` poisons the rate metadata, and you need `format=yuv420p,fps={rate}` after every xfade).
- **Burned-in captions.** [`make-subtitles.py`](../make-subtitles.py) generates an ASS subtitle file aligned to the OUTPUT video — handles word-level truncation for cuts that fall mid-segment, filters Whisper hallucinations, and post-processes overlap removal at xfade boundaries. The cut.py `--captions` flag burns them in.
- **Working dir off iCloud.** `~/Desktop/soda-edit/<slug>/` was the first attempt; mid-run, iCloud started evicting multi-GB files and ffmpeg failed with "Operation timed out." Moved to `~/Developer/soda-edit/<slug>/` (non-iCloud on this machine) and the issue went away. Captured as a hard rule in workflow.md step 5.
- **Photos export bypassed FDA.** Granting Full Disk Access to the terminal would let osxphotos read the SQLite database directly, but is a sweeping permission grant. Instead, [`export-from-photos.sh`](../export-from-photos.sh) uses an `osascript` block that asks Photos.app to do the export — Photos.app already has access to its own library, so no FDA grant on the terminal is needed. Wrap in `with timeout of 1200 seconds` for big GoPro files.
- **Multi-source cut lists.** A single video can be assembled from multiple synced sources without pre-concatenating them. cut.py's "dict-with-sources" cut list format names each source's transcript and sync offset once at the top, then per-cut entries reference the source by path. make-subtitles.py reads the same file.
- **Title card.** [`cut.py --title "First Tap"`](../cut.py) generates a 2 s near-black card with centered text and prepends it to the xfade chain (so it dissolves into the first content frame, instead of hard-cutting). Resolution and fps are matched to the first content source — title-vs-content fps mismatch breaks xfade.
- **Section + tool overlays.** Per-cut `"section"` (lower-third banner, 3 s) and `"tool"` (upper-right small label, 3.5 s) fields in the cut list let scenes self-annotate. Used sparingly — four section labels and one tool callout for the whole 6:38 video.

## What bit (issues encountered, solutions captured)

- **DJI Mic Mini fell off mid-Part-2.** Lav audio for the 30-min recording was unusably distant. GoPro built-in mic was the fallback — re-rendered the cut with Part 2 sourced directly from the GoPro file (kept Part 1 with the lav). Captured as: keep the GoPro original around as fallback audio for any session; don't delete `video/<file>.mp4` until the muxed output has been reviewed.
- **iCloud eviction race.** First "Operation timed out" failures during ffmpeg encode were misdiagnosed (twice) as filesystem hiccups. Eventually traced to iCloud-managed `~/Desktop/`. The Apple `brctl` command silently lies ("client zone not found") about whether a file is in an iCloud sync zone — trust the user's eyes, not brctl.
- **Chained xfade fails on rate metadata.** ffmpeg 7.1's xfade output advertises rate `1/0` (undefined) when fed back into the next xfade. Fix: insert `format=yuv420p,fps={rate}` after every xfade. Discovered by binary-searching from a working 2-input xfade to a failing 3-input chain.
- **`setpts=PTS-STARTPTS` is a footgun on xfade chains.** Resets timestamps in a way that destroys frame-rate metadata downstream. Removed; replaced with explicit `fps={rate}` per-input.
- **NPT vs MPT.** Whisper consistently mistranscribed "NPT" as "MPT." Fix path: post-process the generated `.ass` file with `sed 's/MPT/NPT/g'`. Future improvement: add a per-video text-replacements dictionary to make-subtitles.py.
- **Time-elapsed chyrons on cumulative output.** First attempt computed each cut's chyron as that cut's start in its own source — which made Part 2's chyrons read as `+0:10` after Part 1 had reached `+7:35`, looking like time went backward. Easy fix (cumulative across sources), but the user dropped chyrons entirely in favor of cross-dissolves + section labels for the time-passing signal.
- **First-cut clap-in-frame.** The "broad" pad-before for the FIRST cut of a clip pulls in the clap (sync marker, not content). Caught on draft v1; rule added to workflow.md: first cut starts at speech, not scene_start. Broad-pad is mid-recording behavior only.

## What this snapshot is NOT

- Not a video-production manual. The live procedure is in [`../workflow.md`](../workflow.md). Detailed gotchas live in each script's header.
- Not a permanent statement about iMovie. The on-phone workflow still has its place for very short single-angle clips; this snapshot doesn't retire it, just deprioritizes it.
- Not a publish-cadence commitment. Two videos in, the rate is "when there's a story worth telling," not a schedule.
- Not a closure of the *Walk* commitment from the 2026-05-04 snapshot. Walk (live narration during shop work) is still untested. The 2026-05-08 video used the conventional model — capture quietly, narrate later — but the lav-mic-failure path also revealed that *post-recorded scripted voiceover* is workable, which weakens the case for live walking narration.
