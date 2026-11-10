# One Less Errand

A 36-second Home Soda Machine film about a small wish that turns into a
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

`story.json` stores the source shot clock. `pacing-review.json` defines the
delivered edit; [`hsm-marketing studio-clock`](../../../../tools/hsm/marketing/src/film/clock.rs)
derives its picture and sound clock.

| Time | Picture | Spoken idea |
| --- | --- | --- |
| 0–2.833 | Cold soda macro | You wanted a glass of soda |
| 2.833–7.25 | One can opens into a twelve-can case and cart | Somehow, a trip to the store |
| 7.25–11.75 | The same case lands in the car, kitchen and shelf | Carrying it home |
| 11.75–17.917 | Cans leave; loaded cases replenish the shelf | Another trip. And another. And another. |
| 17.917–21.333 | The emptied shelf | What if the next glass was already waiting? |
| 21.333–24.375 | First Sculpted faucet reveal | Cold. Fully carbonated. |
| 24.375–26.5 | Established active pour | Straight from your faucet |
| 26.5–30.542 | Tighter soda macro | The soda you wanted, whenever you want it |
| 30.542–35.833 | Completed drink and brand | Home Soda Machine. One less errand. |

`hsm-marketing studio-stage` builds the standalone studio and evaluates each
pose from local shot time. The native
[beverage scene](../../../../tools/hsm/marketing/src/film/beverage.rs) reads
the faucet triangles and firmware display and supplies the studio lighting.
The pour uses distinct gravity-curved jets entering the glass, an animated
impact surface, a small change in liquid level and fine rising bubbles.
[Routine geometry](../../../../tools/hsm/marketing/src/film/routine.rs) builds
the can, carton and handling contexts; the
[picture clock](../../../../tools/hsm/marketing/src/film/clock.rs) evaluates
departures, transfers and restocks from each scene’s `can_actions`.
The static empty shelf is a held frame under the question. The
[native finisher](../../../../tools/hsm/marketing/src/film/finish.rs) adds
moving bubbles to the beverage photographs, timed type and the sound master.

## Sound

`narration.json` contains the script and recording direction.
`audio/narration.wav` is a connected Charon performance, placed at 0.55 seconds.
`narration-words.json` contains its word alignment. A contextual pickup supplies
the car and kitchen clauses. The edit preserves recorded word speed.

[`hsm-marketing studio-audio`](../../../../tools/hsm/marketing/src/film/sound.rs) supplies
an original repeating routine motif, an open harmony at the
reveal, pictured case contacts, fine carbonation and the close pour.
`story.json` records source contact frames; the delivered `audio-plan.json`
records the resulting sound clock. Water follows the established flow, then close fizz takes over at
the sensory macro. The final master is stereo 48 kHz, with English WebVTT and
SRT captions. The final spoken line ends at 32.952 seconds; the invitation and
musical decay complete the 860-frame edit.

## Timing and typography

`pacing-review.json` defines an 860-frame, 35.833-second edit. Each handling
context has 1.5 seconds for its arrival, contact and settled result. The repeat
sequence has short rests after replenishment, and its labels remain readable
until the following phrase. The final repetition lands before the question.

The 3.042-second faucet portrait follows the connected delivery of “Cold.
Fully carbonated.” The titles switch in the same position with the spoken
phrases, with “Carbonated” remaining visible for 2.167 seconds. The established
pour has 2.125 seconds of continuous liquid motion, including a half-second
handle before its camera move. The sensory macro has room between the satisfied wish and
“Whenever you want it,” then another breath before the brand.

`hsm-marketing studio-clock` derives this clock from `story.json`. Settled-frame
holds preserve the can motion and contact poses; extended product shots use the
source cadence. `hsm-marketing studio-finish` maps repeat type through the same
holds. The sound contacts follow the resulting picture frames.

The voice uses `audio/narration.wav` with added sentence-gap space and a
contextual Charon pickup for “Into the car” and “Into the kitchen.” The benefit
pair retains the original recorded cadence. The pickup recording and direction
are `audio/handling.wav` and `audio/handling.json`;
selected passages and placements are in the edit manifest. The words retain
their recorded speed. Captions follow the edited phrases, with separate cues
for “Cold” and “Fully carbonated.”

The routine score moves at 96 BPM. Its last harmony decays through the question
pause and into the answer. The benefit holds leave the revealed product in
view, with the answer chord, water and fine fizz providing continuity.

Build the delivered edit:

```sh
tools/run -- hsm-marketing studio-render \
  --timing marketing/video/one-less-errand/studio/pacing-review.json \
  --profile story-breathing \
  --chunk-frames 8 \
  --out marketing/video/one-less-errand/studio/out/connected-benefits-review
```

The player is `out/connected-benefits-review/index.html`; its movie, captions,
picture clock and sound report live beside it. The published master and its
publication record are listed in [`../README.md`](../README.md).

## Render and review

Use Blender, FFmpeg and the [native marketing tools](../../../../tools/hsm/marketing/README.md).
The current local faucet payload is
`hardware/faucet-layout/faucet-assembly.step.mesh`.

After rendering, `node marketing/video/one-less-errand/serve.mjs`
serves the output tree; open `/connected-benefits-review/` for the player.

The renderer uses Cycles denoising. Moving CG shots retain the source cadence,
preserving the can contacts, fine carbonation and moving liquid. Command help
and the native source define render defaults.
`--fps` and `--pour-fps` can select lower source cadences for draft work; the
finisher confines any interpolation to its individual shot. Each Blender process
renders a bounded source-frame batch of one shot; `--chunk-frames` selects its
size. Existing frames make the render resumable. `--fresh --shots pour` replaces
one source sequence. `--picture-only` and `--finish-only`
select rendering or finishing.

For art review, select stills from the repository root:

```sh
tools/run -- hsm-marketing studio-stage --stills --width 960 --samples 8 \
  --shots hero pour serve
tools/run -- hsm-marketing studio-stage --stills --width 960 --samples 8 \
  --shots case car kitchen shelf repeat question
```

A timed animatic uses one draft still in each source shot's frame directory:

```sh
tools/run -- hsm-marketing studio-finish \
  --animatic --frames /absolute/path/to/draft-frames \
  --audio /absolute/path/to/mix-master.wav --out /absolute/path/to/animatic
```

Generated frames, stems, intermediate encodes and the player are under ignored
`out/`. The delivered player files are `film.mp4`, `film.vtt`, `film.srt`,
`poster.jpg` and `contact-sheet.jpg` under `out/connected-benefits-review/`.
The approved upload and captions are copied to `out/one-less-errand-delivery.*`.
The player offers playback, captions and downloads.
