# Video Workflow

Living procedure for the capture-to-publish loop. Updates in place when a step changes; if a step changes meaningfully (CapCut → iMovie → Mac edit pipeline), update here. Snapshots in [`snapshots/`](snapshots/) preserve the historical state at moments worth freezing.

## The Mac edit pipeline

Capture on GoPro + DJI Mic Mini as before. Edit on the Mac with custom scripts in this directory, driven from Claude Code. Lossless waveform-based sync, Whisper transcription, segment-clustered cut decisions, scripted cross-dissolves, burned-in captions, generated title cards.

1. **Capture.** GoPro on cap mount, DJI Mic Mini live to iPhone Voice Memos. See [`equipment.md`](equipment.md) for camera and audio settings. *DJI Mic Mini failure mode: clip can fall off mid-session. The GoPro's built-in mic is a usable fallback for narration; keep it as plan B.*
2. **Quik cloud (auto).** GoPro reconnects to home wifi → footage auto-syncs to Quik cloud. No per-clip action needed once the cloud subscription is on.
3. **Quik → Photos (manual).** Share each desired clip from Quik cloud to Photos. Once the file lands in Photos.app the rest of the pipeline can pull it via AppleScript (no Full Disk Access grant required).
4. **Voice Memos → Files (manual).** Share each desired audio clip from Voice Memos to iCloud Drive Downloads.
5. **Working dir.** `~/Developer/soda-edit/<YYYY-MM-DD-slug>/`. **Not** `~/Desktop/` — Desktop is iCloud-synced and aggressively evicts large files mid-encode, breaking ffmpeg with opaque "Operation timed out" errors. `~/Developer/` is non-iCloud on this machine; verify on yours before committing to a path.
6. **Pull video from Photos.** [`export-from-photos.sh`](export-from-photos.sh) wraps an `osascript` block that asks Photos.app to export the latest media item as the unmodified original. Photos.app does the file copy; we never touch the SQLite database, so no FDA grant is required. Use `with timeout of 1200 seconds` for big GoPro files (6 GB+ on 30-min clips).
7. **Sync external audio to video.** [`sync.py`](sync.py) cross-correlates the lav audio against the GoPro's own audio (within the first 120 s — we use a clap as the shared transient). Outputs the offset, writes a `.sync.json` sidecar next to both source and muxed output, and (with `-o`) muxes the lav onto the video, replacing the GoPro audio. Confidence > ~3 means a clean clap; below that, listen to a synced sample before trusting.
8. **Transcribe.** Run Whisper on the lav audio: `whisper <audio>.m4a --model medium.en --language en --word_timestamps True --output_format json`. Word timestamps are required for caption truncation in step 11. Use the project's `tools/video-venv/` for everything Python.
9. **Cluster speech into scenes.** [`segment.py`](segment.py) groups Whisper segments into clusters with gap ≤ `--gap` seconds, pads each cluster by `--pad-before` / `--pad-after`, and merges any scenes that overlap after padding. Default `gap=10 pad=30/30` is too broad for sparse-narration footage; for the 2026-05-08 first-tap recording, `--gap 15 --pad-before 10 --pad-after 10` produced the right shape. Tune per video.
10. **Visual analysis (interactive, with Claude).** Spend the tokens here. For each candidate scene, extract a frame every ~5 s within the scene window, plus a few from the gaps before/after that look interesting. Read them, decide refined cut points based on what's visible (the spoken word is rarely the whole story — interesting visual moments often start before or end after the speech). Output: a cut list JSON.
11. **Generate captions.** [`make-subtitles.py`](make-subtitles.py) reads the cut list + per-source whisper transcripts + sync offsets and emits an ASS subtitle file timed to the OUTPUT video. Word-level truncation handles cuts that fall mid-segment so the caption doesn't show words that aren't audible. Whisper "so / um / uh" hallucinations during silence are filtered. Output is chunked at ~3.5 s / 7-word max for modern burned-in-caption pacing.
12. **Render.** [`cut.py`](cut.py) extracts each cut, generates a title card (still color background + centered text, resolution + fps matched to source), prepends it to the chain, applies cross-dissolves between every cut, draws section / tool overlays per cut, then burns the captions in. Use `--preset fast --crf 23` for review drafts, `--preset medium --crf 18` for final lock. See cut.py's header for the chained-xfade gotchas (TL;DR: don't use `setpts`; do re-pin `format=yuv420p,fps={rate}` after every xfade).
13. **Iterate on the cut list.** Drafts are cheap. Watch each draft, send adjustments back to Claude, re-render. Auto-delete the rejected draft to keep the working dir small (multi-GB H.264 files add up fast).
14. **Thumbnail.** [`../thumbnail/make.sh`](../thumbnail/make.sh) takes a source image + headline text and produces a 1280×720 PNG with white-on-black-outline text at the **top** of the frame. Top-positioned text avoids YouTube's bottom-right duration pill — particularly aggressive on mobile, where the pill takes a larger proportion of the cropped preview. Pre-crop the source frame in ImageMagick if the action isn't already centered or if the top portion is too busy for legible text — make.sh's center-crop assumes the action is in frame.
15. **Title and description (per workflow.md established convention).** Title carries the thumbnail's hook into searchable form: `<hook> — <equipment or specifics>`. Sentence- or title-cased, not all caps (all caps is algorithmically flagged as spam in titles). Description is 2–3 sentences front-loading the hook and personal stakes, then equipment names on final lines for SEO. Reference example for *I've Never Tapped — First NPT Threads in 316L Stainless*:
    > First time tapping NPT threads by hand. The plates are 1/4" 316 stainless from Send Cut Send — they'll be welded into a carbonation tank for a home soda machine I'm building. Forty threads to cut by hand. This is the first one.
    >
    > Tap: Drill America 1/4"-18 NPT
    > Drill press: WEN 4208T 8" benchtop
    > Cutting fluid: Tap Magic EP-Xtra
16. **Upload.** YouTube Studio. Click upload, select the rendered MP4, paste title + description, upload custom thumbnail (the same 1280×720 PNG), set audience to "not made for kids," skip subtitles (we burn them in), set Public, publish.
17. **Verify the published video.** Open the public watch URL (`https://youtu.be/<id>`, copyable from the upload dialog) and confirm title, description, thumbnail, duration, and visibility all match. Studio's "Video published" confirmation dialog is not ground truth — the public watch URL is. HD transcoding runs in the background after publish, so the player may sit at 0:00 buffering for several minutes; that is not a verification failure, the upload is committed once the URL resolves. This step is mandatory: at least one prior agent skipped it and shipped a broken state.
18. **(Optional) Caption fix.** YouTube auto-captions still run in parallel to the burned-in captions; if YouTube's version has an error that crosses the brand-cringe threshold, fix it in Studio → Subtitles → click into the auto-caption editor. Burned-in captions are unaffected.
19. **Updates-feed post on homesodamachine.com.** Write a video-launch post at `posts/YYYY-MM-DD-HHMM.md` per the post format documented in [`../../posts/README.md`](../../posts/README.md) — specifically the *Video-launch posts* section. Reuse the YouTube thumbnail PNG: copy the 1280×720 PNG to `public/post-images/YYYY-MM-DD-<slug>-thumbnail.png` and link to the YouTube watch URL. Example: `posts/2026-05-08-1145.md` accompanying *I've Never Tapped*.

Steady-state target: ~60–90 minutes per clip including the visual-analysis pass. Render time scales with clip length; the 2026-05-08 first-tap clip rendered in ~10 min on M-series with `--preset fast`. Iteration cycle: ~5 min per draft once cut list is stable.

## On the iPhone + iMovie path

The on-phone workflow that shipped *First Weld* (2026-05-04) is preserved in [`snapshots/2026-05-04-first-execution.md`](snapshots/2026-05-04-first-execution.md). It still works for very short clips that don't need cross-dissolves, captions, or precise sync. Below ~3 minutes of source material with one camera angle, it's still faster than the Mac pipeline. Anything past that, the Mac pipeline wins on every axis except setup cost.

## Open items

- **Walk** — DJI Mic Mini live during shop work, narrate as you go (the audio-first inversion). The first-tap session validated *post-recorded narration* over the on-camera ad-libbing; walking with live narration remains untested.
- **Welder unboxing footage** — captured but not edited; planned as B-roll for the welding story, not standalone content.
- **Voiceover-from-script** — the v3 script in `~/Developer/soda-edit/2026-05-08-first-tap/script-v3.md` is what we'd use if recording on-camera audio fails entirely. Not yet exercised end-to-end (the GoPro audio for the 2026-05-08 first-tap was usable, narrowly).

## Why this shape

The original block was device-and-app context switching. Phone-only kept the Mac free for soda-machine work. But two videos in, the iMovie limitations bit hard: no waveform-based sync, no cross-dissolves, no caption tooling, no programmatic precision when iterating cut points. The Mac pipeline takes a one-time cost (write the scripts, learn them, set up the venv) and amortizes it across every future video. Claude Code does the orchestration, so the Mac stays mostly idle from the user's perspective during the heavy lifts (whisper transcription, ffmpeg encode passes).

The principles in [`principles.md`](principles.md) didn't change. POV > talking head, voiceover > on-camera, build-in-public > tutorial. The Mac pipeline just makes it easier to honor those — especially voiceover-friendly editing.

## Related

- [`principles.md`](principles.md) — durable production principles this workflow sits on top of (POV, voiceover, drafts vs. posts, etc.).
- [`equipment.md`](equipment.md) — gear list and HERO13 capture settings.
- [`concepts.md`](concepts.md) — video ideas and tier ranking.
- [`sync.py`](sync.py), [`segment.py`](segment.py), [`make-subtitles.py`](make-subtitles.py), [`cut.py`](cut.py), [`export-from-photos.sh`](export-from-photos.sh) — the pipeline scripts. Each script's header has the gotchas + design rationale.
- [`../thumbnail/make.sh`](../thumbnail/make.sh) — thumbnail builder.
- [`../../tools/video-venv/`](../../tools/video-venv/) — Python venv for the pipeline (numpy, scipy). Self-ignoring per the `tools/cad-venv/` convention.
- [`../../posts/README.md`](../../posts/README.md) — Updates-feed post format, including the video-launch post variant.
- [`snapshots/2026-05-04-first-execution.md`](snapshots/2026-05-04-first-execution.md) — what changed when the on-phone plan met first execution (First Weld).
- [`snapshots/2026-05-08-mac-pipeline-first-execution.md`](snapshots/2026-05-08-mac-pipeline-first-execution.md) — what changed when the Mac pipeline met first execution (First Tap).
