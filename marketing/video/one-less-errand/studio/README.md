# One Less Errand — studio film

A 64-second Home Soda Machine design film. A cold glass opens the film; one can
becomes twelve, a trip home, and an empty shelf. The kitchen reveal resolves the
chore into choosing a flavor and pouring a glass. Sculpted in Black and
Industrial in White close the product sequence.

The integrated appliance is in development. Cabinetry, glass, ice, carbonation
and the two separate liquid streams are illustrative animation. The faucet,
enclosure, regulator and display artwork use the current project geometry and
firmware assets, shared with the homepage's kitchen renderer.

## Picture

`story.json` is the 64-second edit. `stage.py` builds the scene, loads the current
hardware meshes, and evaluates every pose from shot-local time. `errands.py`
supplies the can, twelve-pack and carrying sequence. `lighting.py` supplies the
product lighting and studio backgrounds. The kitchen scene builder's
`--scene-only` option loads its CAD scene without rendering homepage stills.

`render.py` renders slow camera moves at 4 source fps, liquid and carrying action
at 8 source fps, and the cabinet, display and lever at native 24 fps.
`finish.py` assembles each shot separately, interpolates the lower cadences to 24 fps,
adds typography, and encodes the 1920 × 1080 H.264 / BT.709 / AAC master.
Interpolation is confined to each shot; picture cuts remain cuts. Render frames
and intermediate encodes are under the ignored `out/` directory. A render
resumes by retaining existing frames. Use `render.py --fresh --shots pour` to
replace one changed shot and finish the film with the other source sequences.
Changing source cadence, resolution or samples selects a separate frame set.

## Sound

`audio-plan.json` holds the source narration edits and their picture positions.
`audio.py` edits the existing Charon recording without changing its pace and
synthesizes the original score and tactile effects. A repeating chore rhythm
clears at the kitchen reveal; the pour, ice and fine carbonation have their own
space. The stereo master is 48 kHz / 16-bit, approximately −17 LUFS, with a
−1.5 dBTP ceiling. English WebVTT and SRT captions accompany the film.

## Render and review

From the repository root, using Blender 5.1, FFmpeg, the existing web/render
dependencies and `tools/video-venv`. The shared scene requires the current local
`.step.mesh` payloads for both faucet assemblies, the enclosure and the Taprite
regulator.

```sh
tools/video-venv/bin/python marketing/video/one-less-errand/studio/render.py
node marketing/video/one-less-errand/serve.mjs --studio
```

`render.py --fps 24 --action-fps 24` renders every shot at native 24 fps. The default
source render is 1920 × 1080 with 16 Cycles samples and denoising. `--samples`
and `--width` select other settings; `--mechanism-fps` selects the mechanism cadence.
`--picture-only` and `--finish-only` select
one side of the process.

Pass `--stills --shots kitchen pour fizz` to `stage.py` for selected art review frames.
`--start-frame` and `--end-frame` select a local frame interval. `--out` keeps
independent render sets. For native 24 fps frames, pass `--fps 24` to both
`stage.py` and `finish.py`; source rates can also be set per shot with the
finisher's `--source-fps pour=12` option.

The review player provides chapter navigation, captions, and downloads of
`out/film.mp4`, `out/film.vtt` and `out/film.srt`. `out/poster.jpg` is the player
poster and `out/contact-sheet.jpg` is the picture overview.
