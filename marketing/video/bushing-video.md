# *"Bushing" Doesn't Mean Bushing* — production plan

Companion plan for the X1 Pro wire-stick explainer. Substantive technical content already lives in [`../../hardware/welding-progress-2026-05-09.md`](../../hardware/welding-progress-2026-05-09.md) — this file captures production division of labor only.

- **Working title:** *"Bushing" Doesn't Mean Bushing — Fixing X1 Pro Wire Stick*
- **Target length:** ~3 minutes
- **Audience:** X1 Pro owners hitting the wire-stick problem (search-relevance, not virality)

## User: capture raw footage

Three shots, one session. Wire feed pointed away from any plate, laser firing into a fire-resistant pad. No real welding on shots 1 and 2 — wire never touches the surface, can't stick.

1. **Default 400 ms Bushing delay, wire out of fire path.** Trigger fire 2–3 seconds, release, hold camera on the wire. The retract-then-immediate-pushback is barely visible — that's the pedagogical point. 4–6 takes for one clean read.
2. **Bushing delay 2000 ms, same setup.** Trigger fire, release, hold long enough for the 2-second pause + forward push to play out fully. 3–4 takes.
3. **Real weld with corrected parameters.** Cap-mount POV welding on test material. 2–3 clean trigger releases showing no stick.

Slow-mo on shots 1 and 2 if the GoPro supports it at the chosen frame rate.

## User: record narration

After the agent delivers the finalized script (below). Standard post-record narration per [`workflow.md`](workflow.md) — DJI Mic Mini → Voice Memos. Read time ~2 minutes.

## Agent: pre-narration work

- Pull the three source clips from Photos via [`export-from-photos.sh`](export-from-photos.sh).
- Pull the wire-stuck-to-plate cold-open clip from the *Stuck Less That Time* working dir or re-export from Photos.
- Download the X1 Pro Operator's Manual PDF from the source URL in [`../../hardware/welding-progress-2026-05-09.md`](../../hardware/welding-progress-2026-05-09.md), screenshot Figure 17 (the wire-feeding parameters page), crop to the three definitions.
- Build an annotated translation-table PNG, 1920×1080, sans-serif, dark background:
  - Three rows: 回抽 / 补丝 / 补丝延迟.
  - Three columns: Chinese term, English (as printed in manual), Actual meaning.
  - Highlight the "Bushing delay" row to emphasize the broken translation.
- Confirm the script below still reads cleanly against the actual footage. Tighten if anything mis-aligns. Record any phrasing changes inline.

## Agent: post-narration work

Standard Mac edit pipeline per [`workflow.md`](workflow.md):

- [`sync.py`](sync.py) — narration ↔ raw footage cross-correlation.
- [`segment.py`](segment.py) — scene clustering on the narration.
- Visual analysis pass against the cut list.
- [`make-subtitles.py`](make-subtitles.py) — burned-in captions, with `MPT → NPT`-style replacements if Whisper misreads "Bushing" or the Chinese pinyin.
- [`cut.py`](cut.py) — assembly:
  - Title card.
  - Cold open (wire-stuck clip → clean-release clip from shot 3).
  - Shot 1 (default 400 ms).
  - Manual screenshot (Figure 17).
  - Translation-table PNG.
  - Shot 2 (Bushing delay 2000 ms).
  - Shot 3 (real weld).
  - Close.
  - Cross-dissolves at every boundary; captions burned in.
- [`../thumbnail/make.sh`](../thumbnail/make.sh) — 1280×720. Candidate text: **BUSHING ≠ BUSHING** over a frame from shot 2 with the wire visibly retracting.
- Updates-feed post at `posts/YYYY-MM-DD-HHMM.md` per the video-launch format in [`../../posts/README.md`](../../posts/README.md). Reuse the thumbnail PNG.
- After upload, edit the *Stuck Less That Time* YouTube description to add: *Update: the actual fix was Bushing delay, not the laser timing — see [URL].*
- Optional: reply to the @Xlaserlab "Looking good!" comment on the welded video with a link to this one.

## Script (draft, ~270 words / ~2 min spoken)

Each block names the visual it sits over. Narration in blockquotes is what the user reads.

**Cold open** — wire-stuck-to-plate clip from *Stuck Less That Time*, hard cut to clean release from shot 3.

> Wire keeps sticking on the X1 Pro? It's not the laser timing. There's a parameter the English manual mistranslates, and once you change it, the wire stops sticking.

**Shot 1** — default 400 ms, wire out of fire path.

> Watch this. Wire feed pointed away from any plate. Laser firing into nothing. Default Bushing delay — 400 milliseconds. On trigger release, the wire retracts, barely visible, then immediately pushes back. The retract is happening. You just can't see it through laser goggles when there's a puddle and sparks in front of your face.

**Manual screenshot** — Figure 17, the three definitions.

> Here's the X1 Pro manual. Pullback length — *wire retracts after releasing the trigger*. Patch length — *wire retracts after releasing the trigger*. They can't both retract, or the wire would disappear after one cycle. So I went to the Chinese source.

**Translation-table animation.**

> 回抽 means retract. That's Pullback, correctly translated. 补丝 means compensating feed — forward push to restore wire stickout. Not retract. 补丝延迟 is the wait between them. The English translator rendered 补丝 as "bushing," which has nothing to do with the actual concept. The parameter has been doing what it's designed to do. The label was wrong.

**Shot 2** — Bushing delay 2000 ms, same setup.

> Same setup, Bushing delay set to 2000 milliseconds. Now you can see what the welder has been doing all along. Retract. Two-second pause. Then forward push. The pause is where the puddle solidifies. The forward push hits solid metal instead of liquid metal. That's why the wire stops sticking.

**Shot 3** — real weld with the corrected parameters.

> In practice. Real weld. No stick on release. Three sessions of trimming wire by hand for what turned out to be a one-parameter fix.

**Close** — black, then end card.

> If you have an X1 Pro and the wire keeps sticking, it's almost certainly Bushing delay. The English manual won't tell you that. Now you know.

---

## Additional suggestions (not folded into the core plan)

Captured for a later pass — fold in selectively when revisiting. Don't pollute the core above.

1. **Honest caveats half-beat.** A ~15-second insert between Shot 3 and the Close, naming the bound: *"This delay is for 0.065-inch 304L stainless. Thicker plate holds heat longer — push the delay up. Thinner sheet, the default 400 ms is probably right. Your number will be different than mine."* The "Open questions" list in [`../../hardware/welding-progress-2026-05-09.md`](../../hardware/welding-progress-2026-05-09.md) (1200–1500 ms might suffice, wire-feed-stop timing untested, Pulse mode untested) is the source. Prevents misuse, earns durable credibility.
2. **Pinyin in the script as pronunciation guidance.** Pull the pinyin from the welding-progress translation table (*huí chōu*, *bǔ sī*, *bǔ sī yán chí*) into the inline script. The video's whole differentiator is "I went to the Chinese source" — pronouncing the terms badly weakens that signal. The user doesn't need perfect tones, just deliberate ones.
3. **Thumbnail follows the existing channel convention.** Use [`../thumbnail/make.sh`](../thumbnail/make.sh) with white-on-black-outline text at the top of the frame, matching *First Weld* / *First Tap* / *Stuck Less*. Avoid one-off styling for visual consistency on the channel grid.
4. **Capture frame rate for slow-mo.** GoPro baseline per [`equipment.md`](equipment.md) is 30 fps. For slow-mo on shots 1 and 2, bump to 60 or 120 fps before the session — easy to miss at capture time and forces a reshoot if forgotten.
