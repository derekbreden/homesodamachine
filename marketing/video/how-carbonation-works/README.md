# How Carbonation Works

[Watch the film on YouTube](https://youtu.be/fEWwkrJh5J4).

A 1 minute 42 second narrated explainer, 1920 × 1080 at 30 fps. The film moves
from the Sculpted faucet into the enclosure and cold core, then spends most of
its running time on the carbonator's gas admission, water jet, entrainment,
refill control and copper evaporator. Two separate streams meet in the glass
at the close.

The enclosure reveal and animated cutaway share the actual STEP pressure
vessel, fittings, drilled jet cap and guide geometry. A moving section plane
opens the hardware at fixed datums. The movable cylindrical ASA Aero float
and its enclosed RC62 ring come from their assembly STEP. Fluid motion,
bubble populations, thermal tracers, glass and drink are illustrative.
The integrated appliance is in development. The coil carries refrigerant;
heat tracers terminate on its submerged turns.

Open [the film player](watch.html) or the rendered master at
`out/how-carbonation-works.mp4`. [publication.json](publication.json) and
[youtube-description.txt](youtube-description.txt) contain the channel metadata
and six chapter markers. [thumbnail.jpg](thumbnail.jpg) is the 1280 × 720 cover.
The output directory contains matching English SRT and WebVTT captions.

## Picture and voice

[story.json](story.json) defines the ten scenes. The final picture clock is
[audio/timing.json](audio/timing.json): 3,061 frames, 102.033 seconds. The sound
master uses Gemini Charon narration, an original ambient score, and original
scene-following sound effects. The saved source performance and its service,
model, script hash and recording hash are recorded in
[audio/provenance.json](audio/provenance.json).

The connected voice retains its recorded word speed. Editorial breaths and
picture handles are defined in [audio/edit-plan.json](audio/edit-plan.json).
[audio/audio-report.json](audio/audio-report.json) records the 48 kHz stereo
24-bit mix at −16.00 LUFS, with −2.61 dBTP peak and linear final normalization.
The picture includes readable captions; the sidecars carry the same spoken text.

`carbonator.js` evaluates fluid behavior at the CAD inlet and outlet datums
from explicit simulation time. `scene.js` maps that behavior onto the narration
clock. Its continuous camera track moves from the drilled cap directly to the
impact, then widens through the float and evaporator views. Soft dissolves join
the faucet and appliance locations. The studio uses the pale ice, cobalt and
orange palette of *One Less Errand*, with a matte faucet and clear thin-rimmed
glass. `studio.html` provides the fixed video composition.
[assets/README.md](assets/README.md) describes the mesh snapshots, real coil
path, datums, fonts and provenance.

## Render

Use Node, FFmpeg, the existing `tools/render` Node dependencies, Chrome and
`tools/video-venv`. The renderer restores local JSON working copies from the
committed gzip assets and caches pinned Three.js 0.160.1 in the ignored output
directory. It does not rebuild the hardware.

From the repository root:

```sh
tools/video-venv/bin/python marketing/video/how-carbonation-works/edit-audio.py
tools/video-venv/bin/python marketing/video/how-carbonation-works/make-audio.py
node marketing/video/how-carbonation-works/render.mjs --stills
node marketing/video/how-carbonation-works/render.mjs --render
```

The full render creates resumable H.264 scene clips in `out/segments`, joins
them, and muxes the stereo AAC sound master. A matching scene signature reuses
an existing clip. `--shots gas,jet` selects scenes and `--fresh` replaces selected
clips. `--stills` writes the review frames and thumbnail source. Render outputs,
intermediate audio, and local CAD working copies are ignored.

`--stills --times 4.2,20.2,36.7,65.1` selects specific review frames. The
fixed hardware and closed half-section sources can be extracted from the
existing STEP files with `prepare-carbonator-assets.py` in `tools/cad-venv`.
That export does not change or rebuild the hardware.

For the local player and the animated scene preview:

```sh
node marketing/video/how-carbonation-works/render.mjs --serve
```

Open `http://127.0.0.1:8794/watch.html` for the finished movie, or
`http://127.0.0.1:8794/studio.html?play` for the source picture. The source preview
has no sound. `studio.html?t=47.2` selects an explicit picture time.

To record a new Gemini performance, edit `narration.json` and run
`generate-narration.py` with the video Python environment. It reads the local
Gemini credential or its environment variable, records the source WAV, and
aligns the words with local Whisper. Recording is separate from a normal render.
The original WAV, script, alignment and audio recipes are sufficient to rebuild
this film without another voice-generation request.

## Review

The production review covered the full narration and mix, each scene's still
frames, the port/coil/faucet datums, upright font metadata, caption timing,
the finite gas train, jet entrainment, refill stop and thermal contact. The
delivery report in `out/verification.json` records the encoded movie's streams,
duration, frame count, loudness and final audiovisual review. No repository
build or commit check is added by this workflow.
