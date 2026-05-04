# Video Workflow

Living procedure for the capture-to-publish loop. Updates in place when a step changes; if a step changes meaningfully (CapCut → iMovie, Quik cloud added, etc.), update here. Snapshots in [`snapshots/`](snapshots/) preserve the historical state at moments worth freezing.

## The on-phone workflow

End-to-end edit and publish, all on iPhone:

1. **Capture.** GoPro on cap mount, DJI Mic Mini live to iPhone Voice Memos. See [`equipment.md`](equipment.md) for camera and audio settings.
2. **Quik cloud (auto).** GoPro reconnects to home wifi → footage auto-syncs to Quik cloud. No per-clip action needed once the cloud subscription is on.
3. **Quik → Photos.** Share each desired clip from Quik cloud to Photos (per clip, manual selection).
4. **Voice Memos → Files.** Share each desired audio clip from Voice Memos to Files.
5. **iMovie.** Open, new project.
   - Import video from Photos.
   - Import audio from Files.
   - Manually sync. iMovie does not display audio waveforms in a useful way for visual sync — done by ear and timecode.
   - Find start point, split, delete the head trim.
   - Find stop point, split, delete the tail trim.
   - Export → save to Photos.
6. **YouTube → Create.** Upload from Photos.
7. **Title and description.** Title carries the thumbnail's hook into searchable form: `<hook> — <equipment or specifics>`. Sentence- or title-cased, not all caps (all caps is algorithmically flagged as spam in titles). Description is 2–3 sentences front-loading the hook and personal stakes, then equipment name on a final line for SEO. Reference example for *I've Never Welded — First Welds on the Xlaserlab X1 Pro*:
   > Round four or five of learning to weld. I'm building a stainless steel carbonation tank for a home soda machine, and the only way to get the size I want is to build it myself.
   >
   > Welder: Xlaserlab X1 Pro
8. **Thumbnail** (during YouTube's processing window):
   - Generate via [`../thumbnail/make.sh`](../thumbnail/make.sh) — see that script's header for the duration-pill gotcha and other thumbnail design notes.
   - Set the thumbnail in YouTube once processing finishes.
9. **(Optional) Caption fix.** If YouTube auto-captions have an error that crosses the brand-cringe threshold ("big butt" type misheard words), open Studio → Subtitles → click into the auto-caption editor → fix the text in the textarea → Publish. The textarea uses `\n\n` as caption-segment delimiters; edits *within* a segment preserve all timestamps. Only worth it for high-impact errors; auto-captions are otherwise good enough for Tier 2 build-in-public clips.
10. **Updates-feed post on homesodamachine.com.** Write a video-launch post at `posts/YYYY-MM-DD-HHMM.md` per the post format documented in [`../../posts/README.md`](../../posts/README.md) — specifically the *Video-launch posts* section, which deviates from the daily-window bullet format. Reuse the YouTube thumbnail PNG as the post image: copy the 1280×720 PNG to `public/post-images/YYYY-MM-DD-<slug>-thumbnail.png` and link to the YouTube watch URL. Example: `posts/2026-05-04-0240.md` accompanying *I've Never Welded*. Committing the post triggers an FCM push to subscribers — treat as a publish action.

Steady-state target: ~30–60 minutes per clip, faster as muscle memory builds.

## Open items

- **Walk** — DJI Mic Mini live during shop work, narrate as you go (the audio-first inversion). Not yet attempted as a habit. Remains the highest-leverage workflow change for unsticking the narration step specifically; the conventional shoot-then-narrate model has not produced narration as a reliable habit.
- **Welder unboxing footage** — captured but not edited; planned as B-roll for the welding story, not standalone content.

## Why this shape

The block keeping the project in capture-only mode for two months was not editing skill but device-and-app context switching. The default mental model said *edit happens on a Mac in a real editor* — six steps including Mac transfer, editor learning, project setup, render. Staying on the iPhone end-to-end collapses six steps into the procedure above. The Mac stays available for actual soda-machine work, which is the boundary that needs defending.

## Related

- [`principles.md`](principles.md) — durable production principles this workflow sits on top of (POV, voiceover, drafts vs. posts, etc.).
- [`equipment.md`](equipment.md) — gear list and HERO13 capture settings.
- [`concepts.md`](concepts.md) — video ideas and tier ranking.
- [`../thumbnail/make.sh`](../thumbnail/make.sh) — thumbnail builder script with duration-pill / aspect-ratio / font gotchas in its header.
- [`../../posts/README.md`](../../posts/README.md) — Updates-feed post format, including the video-launch post variant referenced in step 10.
- [`snapshots/2026-05-03-workflow-commitment.md`](snapshots/2026-05-03-workflow-commitment.md) — original 5-step plan before any execution.
- [`snapshots/2026-05-04-first-execution.md`](snapshots/2026-05-04-first-execution.md) — what changed when the plan met first execution.
