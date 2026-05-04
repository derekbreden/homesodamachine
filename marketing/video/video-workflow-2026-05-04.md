# Video workflow — Snapshot 2026-05-04

**This is a point-in-time snapshot, not a living document.** Captures the workflow that actually worked on the first end-to-end execution — first edited and published video shipped 2026-05-04 (the welding first-weld clip). Recipe and rationale recorded here for posterity. Will go stale; treat as a reference point, not the canonical pipeline doc.

**Supersedes** [video-workflow-2026-05-03.md](video-workflow-2026-05-03.md), which captured the planned workflow before any execution. iMovie replaced CapCut after CapCut's first-attempt friction (free tier put a watermark on the export, paid upgrade errored on purchase). GoPro Quik cloud subscription was added and is working as a transfer step.

## GoPro HERO13 capture settings

| Setting | Pick | Why |
|---|---|---|
| Resolution + Aspect Ratio | **2.7K 8:7** at 30 fps | 8:7 is the full HERO13 sensor — the most pixels GoPro can capture. 2.7K gives headroom to crop to 16:9 horizontal *or* 9:16 vertical without quality loss, while keeping file sizes sane. 5.3K 8:7 also works but eats storage 2–3× faster — overkill for talking-head and table-work content. |
| Frame rate | **30 fps** | Baseline. Bump to 60 fps only on clips where slow-mo might matter (welding sparks, fluid splash). |
| Digital Lens | **Linear** | HERO13 lens menu offers HyperView / Wide / Linear / Linear + Horizon Lock / Narrow. Avoid HyperView and Wide — both heavily distort the frame and make hands at the table look like sausages. Linear digitally undistorts so a soldering iron looks like a soldering iron. Skip "Linear + Horizon Lock" — it crops more aggressively and adds rotation correction that misbehaves on head tilt. Plain Linear is right. |
| HyperSmooth | **On** (or AutoBoost) | HERO13 options are Off / On / AutoBoost / Boost. Cap mount is body-stabilized; On is enough. AutoBoost uses available pixels for slightly better stabilization on bumpier moments. Avoid Boost in this mode — it crops ~30% and defeats the 8:7 capture cushion. Switch to Boost when you take the camera off the cap and handhold for a close-up (weld-joint inspection, settings screen of the welder, etc.) — handheld shake is meaningfully worse than head-mounted. |
| HDR | **Off** | Wasted bitrate at this content type. |
| Audio | Default (Stereo) | Fine for ambient (tool clicks, welder hum). Real audio comes from the DJI Mic via the iPhone. |
| Orientation | **Auto** | Settings → Preferences → General → Orientation. Auto handles minor head tilt. "Locked Landscape" is for special use cases — not these. |
| Voice Control | **On** | Preferences → Voice Control. "GoPro start recording" / "GoPro stop recording" works hands-free for solder/weld/torch moments. |

**To check or change on the camera:** From the capture screen, tap the bottom strip showing current settings (e.g. "5.3K | 30 | W") to access Resolution, Aspect Ratio, Framerate, and Digital Lens. For Orientation and Voice Control: swipe down from the top → gear icon → Preferences → General.

## The actual on-phone workflow

End-to-end edit and publish, all on iPhone:

1. **Quik cloud (auto)** — GoPro reconnects to home wifi → footage auto-syncs to Quik cloud. No per-clip action needed once the cloud subscription is on.
2. **Quik → Photos** — share each desired clip from Quik cloud to Photos (per clip, manual selection).
3. **Voice Memos → Files** — share each desired audio clip from Voice Memos to Files.
4. **iMovie** — open, new project.
   - Import video from Photos.
   - Import audio from Files.
   - Manually sync. iMovie does not display audio waveforms in a useful way for visual sync — done by ear and timecode.
   - Find start point, split, delete the head trim.
   - Find stop point, split, delete the tail trim.
   - Export → save to Photos.
5. **YouTube → Create** — upload from Photos.
6. **Thumbnail** (during YouTube's processing window):
   - Screenshot a frame from the video in Photos.
   - Add big text on top in Photos / a thumbnail tool.
   - Save.
7. **Set thumbnail** once YouTube finishes processing the upload.

That's the loop. ~30–60 minutes for a first clip; steady state will be faster as muscle memory builds.

## Open items still on the commitment

- **Walk** — DJI Mic Mini live during shop work, narrate as you go (the audio-first inversion from the 2026-05-03 plan). Not yet attempted. Remains the highest-leverage workflow change for unsticking the narration step specifically; the conventional shoot-then-narrate model has not produced narration in the first published video and is unlikely to in subsequent ones either.

## Milestones

- **2026-05-04** — First weld video published on YouTube. End of capture-only mode. The publishing pipeline is no longer hypothetical.

## What changed from 2026-05-03

- **CapCut → iMovie** as the editor. CapCut's free tier watermarked the export and paid-tier purchase errored. iMovie did the minimal cut sufficient for shipping. Revisit CapCut (or LumaFusion / Final Cut iPad) only if iMovie's missing features become real friction.
- **GoPro Quik cloud subscription enabled and working.** Auto-sync on home-wifi reconnect — removes the manual "open Quik, transfer footage" step that was the planned bullet in 2026-05-03. The transfer-on-capture commitment is satisfied passively now.
- **GoPro voice control enabled.** Hands-free trigger for tool-occupied moments.
- **Audio sync is manual, not waveform-assisted.** iMovie limitation. Tolerable for short clips; may become friction for longer ones — at that point the question of editor choice reopens.
- **Thumbnail process learned in flight** — screenshot a video frame, add big text, set after YouTube processes. Not a friction point, just a step that wasn't explicit in the prior plan.

## What this snapshot is NOT

- Not a video-production manual — it's the workflow that happened to work on the first execution, and will evolve.
- Not a permanent statement about tools — iMovie won the first round by default after CapCut's purchase errored. CapCut and other tools may earn back the slot later.
- Not a publish-cadence commitment. The first video is shipped; the second one will happen when it happens.
- Not a closure of the Walk commitment. Walk is still pending and is the only piece of the 2026-05-03 plan not yet executed.
