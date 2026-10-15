# One Less Errand

A 30-second Home Soda Machine film about a small wish that turns into a
repeating errand. A glass of soda leads to a case in a cart, then the car,
kitchen and refrigerator shelf. The cans disappear and the trip returns.
The next glass gets a different ending: cold soda from the Sculpted faucet.
The completed drink and “One less errand” close the story, with an invitation
to explore the machine.

The film is a product visualization. The integrated appliance is in development.
The faucet uses the current Sculpted CAD, and its selected display uses the
current green factory flavor artwork. The glass, liquid, carbonation,
condensation and studio are illustrative. The opening beverage photograph is
built-in imagegen artwork in [`assets/cold-soda-macro.png`](assets/cold-soda-macro.png);
its full prompt and generator are in [`assets/cold-soda-macro.json`](assets/cold-soda-macro.json).

## Edit

`story.json` is the shared picture clock, at 1920 × 1080 and 24 fps.

| Time | Picture | Spoken idea |
| --- | --- | --- |
| 0–2.5 | Cold soda macro | You wanted a glass of soda |
| 2.5–6.917 | One can opens into a twelve-can case and cart | Somehow, a trip to the store |
| 6.917–9.583 | The same case lands in the car, kitchen and shelf | Carrying it home |
| 9.583–14.75 | Cans leave; loaded cases replenish the shelf | Another trip. And another. And another. |
| 14.75–17.5 | The emptied shelf | What if the next glass was already waiting? |
| 17.5–19.583 | First Sculpted faucet reveal | Cold. Fully carbonated. |
| 19.583–21.208 | Established active pour | Straight from your faucet |
| 21.208–24.5 | Tighter soda macro | The soda you wanted, whenever you want it |
| 24.5–29.792 | Completed drink and brand | Home Soda Machine. One less errand. |

`stage.py` builds the standalone studio and evaluates each pose from local shot
time. `cad.py` reads the faucet triangles and firmware display; `lighting.py`
provides the studio. The pour uses two distinct gravity-curved jets entering
the glass, an animated impact surface, a small change in liquid level and fine
rising bubbles. `can_stage.py` builds the can, carton and cropped handling
contexts. `can_motion.py` evaluates the full-size can departures, case transfers
and restocks from each scene's `can_actions`. The static empty shelf is one
held frame under the question. `carbonation.py` gives the beverage photographs
fine moving bubbles. `finish.py` adds the timed type and assembles the picture
with the sound master.

## Sound

`narration.json` contains the script and recording direction.
`audio/narration.wav` is one connected Charon performance, placed at 0.55 seconds.
`narration-words.json` contains its word alignment. The edit preserves the spoken
sentences and natural breaths without time stretching.

`audio.py` supplies an original repeating routine motif, an open harmony at the
reveal, pictured case contacts, fine carbonation and the close pour.
`story.json` records the contact frames; `audio-plan.json` records the resulting
sound clock. Water follows the established flow, then close fizz takes over at
the sensory macro. The final master is stereo 48 kHz, with English WebVTT and
SRT captions. The final spoken line ends at 26.91 seconds; the invitation and
musical decay complete the 715-frame edit.

## Processing-beat review

`pacing-review.json` defines a 739-frame, 30.792-second review cut. The moving
opening macro has eight extra frames (333 ms) after the wish for a glass of
soda. The empty-shelf question has sixteen extra frames (667 ms) before the faucet
answer. The case, transport, repeat, pour and closing shots retain their local
motion and duration. The store text enters with “a trip to the store.”
The faucet reveal displays “Cold” from local frame 2 through the shot while
the narrator delivers “Cold. Fully carbonated.”

`timing.py` derives the review clock from `story.json`, including the shifted
contact frames. The narration receives silence at two quiet sample boundaries
in the existing recording, with 3 ms fades in the noise floor. All spoken
material and its original speed remain intact. The final routine harmony rings
with a soft decay through the question pause and overlaps the answer by 350 ms.
The pulse releases before the answer chord and faucet arrive together.

Build the review from the native source frames:

```sh
tools/video-venv/bin/python marketing/video/one-less-errand/studio/audio.py \
  --timing marketing/video/one-less-errand/studio/pacing-review.json \
  --out marketing/video/one-less-errand/studio/out/pacing-review-cold
tools/video-venv/bin/python marketing/video/one-less-errand/studio/finish.py \
  --timing marketing/video/one-less-errand/studio/pacing-review.json \
  --frames marketing/video/one-less-errand/studio/out/frames/story-loop-24-24fps-1920px-32spp \
  --audio marketing/video/one-less-errand/studio/out/pacing-review-cold/mix-master.wav \
  --out marketing/video/one-less-errand/studio/out/pacing-review-cold
```

The review player is `out/pacing-review-cold/index.html`; its movie, captions,
picture clock and sound report live beside it. The published master and its
publication record are listed in [`../README.md`](../README.md).

## Render and review

Use Blender 5.1, FFmpeg, the existing `tools/render` Node dependencies and
`tools/video-venv`. The current local faucet payload is
`hardware/faucet-layout/faucet-assembly.step.mesh`.

```sh
tools/video-venv/bin/python marketing/video/one-less-errand/studio/render.py
node marketing/video/one-less-errand/serve.mjs --studio
```

The default render uses 1920 × 1080, 32 Cycles samples and denoising. Moving CG
shots render at native 24 fps, preserving the can contacts, fine carbonation
and moving liquid.
`--fps` and `--pour-fps` can select lower source cadences for draft work; the
finisher confines any interpolation to its individual shot. Each Blender process
renders at most 32 source frames of one shot; `--chunk-frames` selects that batch
size. Existing frames make the render resumable. `--fresh
--shots pour` replaces one source sequence. `--picture-only` and `--finish-only`
select rendering or finishing.

For art review, pass `--python
marketing/video/one-less-errand/studio/stage.py -- --stills --shots hero pour
serve --width 960 --samples 8` to Blender from the repository root.
The can routine uses `can_stage.py -- --stills --shots case car kitchen shelf
repeat question --width 960 --samples 8` with the same Blender invocation.
A timed animatic uses one draft still in each source shot's frame directory:

```sh
tools/video-venv/bin/python marketing/video/one-less-errand/studio/finish.py \
  --animatic --frames /absolute/path/to/draft-frames \
  --audio /absolute/path/to/mix-master.wav --out /absolute/path/to/animatic
```

Generated frames, stems, intermediate encodes and the player are under ignored
`out/`. The delivered files are `out/film.mp4`, `out/film.vtt`, `out/film.srt`,
`out/poster.jpg` and `out/contact-sheet.jpg`. The player offers playback,
captions and downloads.
