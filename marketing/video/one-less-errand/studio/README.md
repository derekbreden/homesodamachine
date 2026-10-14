# One Less Errand

An 18-second Home Soda Machine film about keeping the soda you love and losing
the routine of carrying cases home. Diet Mountain Dew introduces the drink;
the Sculpted faucet reveals its source. A brief graphic accumulation of cases
cuts directly to an active pour. The finished drink and “One less errand” close
the film, with an invitation to explore the machine.

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
| 0–2.125 | Cold soda macro | Diet Mountain Dew |
| 2.125–6.25 | Sculpted faucet and drink | Familiar soda, Pepsi's own concentrate, on tap |
| 6.25–8.333 | Three cases accumulate | Without the cases to carry home |
| 8.333–9.958 | Established active pour | Open the faucet |
| 9.958–12.708 | Tighter soda macro | Cold and fully carbonated, whenever you want it |
| 12.708–18 | Completed drink and brand | Home Soda Machine. One less errand. |

`stage.py` builds the standalone studio and evaluates each pose from local shot
time. `cad.py` reads the faucet triangles and firmware display; `lighting.py`
provides the studio. The pour uses two distinct gravity-curved jets entering
the glass, an animated impact surface, a small change in liquid level and fine
rising bubbles. `errands.py` draws the graphic passage at delivery cadence and
exposes its contact events to sound. `carbonation.py` gives the beverage
photographs fine moving bubbles. `finish.py` adds the timed type and assembles
the picture with the sound master.

## Sound

`narration.json` contains the script and recording direction.
`audio/narration.wav` is one connected Charon performance, placed at 0.55 seconds.
`narration-words.json` contains its word alignment. The edit preserves the spoken
sentences and natural breaths without time stretching.

`audio.py` supplies the original short score, fine carbonation, the three
pictured graphic contacts and the close pour. `audio-plan.json` records the
shared timings. Water follows the established flow, then close fizz takes over
at the sensory macro. There are no control or handling effects implying unseen
actions. The final
master is stereo 48 kHz, with English WebVTT and SRT captions.

## Render and review

Use Blender 5.1, FFmpeg, the existing `tools/render` Node dependencies and
`tools/video-venv`. The current local faucet payload is
`hardware/faucet-layout/faucet-assembly.step.mesh`.

```sh
tools/video-venv/bin/python marketing/video/one-less-errand/studio/render.py
node marketing/video/one-less-errand/serve.mjs --studio
```

The default render uses 1920 × 1080, 32 Cycles samples and denoising. All CG shots
render at native 24 fps, preserving the fine carbonation and moving liquid.
`--fps` and `--pour-fps` can select lower source cadences for draft work; the
finisher confines any interpolation to its individual shot. Each Blender process
renders at most 32 source frames of one shot; `--chunk-frames` selects that batch
size. Existing frames make the render resumable. `--fresh
--shots pour` replaces one source sequence. `--picture-only` and `--finish-only`
select rendering or finishing.

For art review, pass `--python
marketing/video/one-less-errand/studio/stage.py -- --stills --shots hero pour
serve --width 960 --samples 8` to Blender from the repository root.
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
