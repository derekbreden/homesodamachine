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
7. **Thumbnail** (during YouTube's processing window):
   - Generate via [`../thumbnail/make.sh`](../thumbnail/make.sh) — see that script's header for the duration-pill gotcha and other thumbnail design notes.
   - Set the thumbnail in YouTube once processing finishes.
8. **(Optional) Caption fix.** If YouTube auto-captions have an error that crosses the brand-cringe threshold ("big butt" type misheard words), open Studio → Subtitles → click into the auto-caption editor → fix the text in the textarea → Publish. The textarea uses `\n\n` as caption-segment delimiters; edits *within* a segment preserve all timestamps. Only worth it for high-impact errors; auto-captions are otherwise good enough for Tier 2 build-in-public clips.

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
- [`snapshots/2026-05-03-workflow-commitment.md`](snapshots/2026-05-03-workflow-commitment.md) — original 5-step plan before any execution.
- [`snapshots/2026-05-04-first-execution.md`](snapshots/2026-05-04-first-execution.md) — what changed when the plan met first execution.
