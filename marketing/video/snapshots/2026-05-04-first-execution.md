# Video workflow — Snapshot 2026-05-04

**This is a point-in-time snapshot, not a living document.** Captures the workflow that actually worked on the first end-to-end execution — first edited and published video shipped 2026-05-04 (the welding first-weld clip). Originally lived as `marketing/video/video-workflow-2026-05-04.md`; relocated and trimmed in the 2026-05-04 refactor — durable HERO13 settings extracted to [`/marketing/video/equipment.md`](/marketing/video/equipment.md), the actual workflow steps extracted to [`/marketing/video/workflow.md`](/marketing/video/workflow.md) as the living procedure. The narrative below (milestones, what changed vs. plan, open items at the time) is what's frozen here as historical record.

**Supersedes** [`2026-05-03-workflow-commitment.md`](2026-05-03-workflow-commitment.md), which captured the planned workflow before any execution. iMovie replaced CapCut after CapCut's first-attempt friction (free tier put a watermark on the export, paid upgrade errored on purchase). GoPro Quik cloud subscription was added and is working as a transfer step.

## Open items at the time of this snapshot

- **Walk** — DJI Mic Mini live during shop work, narrate as you go (the audio-first inversion from the 2026-05-03 plan). Not yet attempted. Remained the highest-leverage workflow change for unsticking the narration step specifically; the conventional shoot-then-narrate model had not produced narration in the first published video.

(Open-items current state lives in [`/marketing/video/workflow.md`](/marketing/video/workflow.md) Open items section. This list is frozen as of 2026-05-04.)

## Milestones

- **2026-05-04** — First weld video published on YouTube. End of capture-only mode. The publishing pipeline is no longer hypothetical.

## What changed from 2026-05-03

- **CapCut → iMovie** as the editor. CapCut's free tier watermarked the export and paid-tier purchase errored. iMovie did the minimal cut sufficient for shipping. Revisit CapCut (or LumaFusion / Final Cut iPad) only if iMovie's missing features become real friction.
- **GoPro Quik cloud subscription enabled and working.** Auto-sync on home-wifi reconnect — removes the manual "open Quik, transfer footage" step that was the planned bullet in 2026-05-03. The transfer-on-capture commitment is satisfied passively now.
- **GoPro voice control enabled.** Hands-free trigger for tool-occupied moments.
- **Audio sync is manual, not waveform-assisted.** iMovie limitation. Tolerable for short clips; may become friction for longer ones — at that point the question of editor choice reopens.
- **Thumbnail process learned in flight** — screenshot a video frame, add big text, set after YouTube processes. Not a friction point, just a step that wasn't explicit in the prior plan. (Subsequently codified as a script: [`/marketing/thumbnail/make.sh`](/marketing/thumbnail/make.sh).)

## What this snapshot is NOT

- Not a video-production manual — it's the workflow that happened to work on the first execution. Live procedure is in [`/marketing/video/workflow.md`](/marketing/video/workflow.md).
- Not a permanent statement about tools — iMovie won the first round by default after CapCut's purchase errored. CapCut and other tools may earn back the slot later.
- Not a publish-cadence commitment. The first video is shipped; the second one will happen when it happens.
- Not a closure of the Walk commitment. Walk was still pending at this date, and is the only piece of the 2026-05-03 plan not yet executed.
