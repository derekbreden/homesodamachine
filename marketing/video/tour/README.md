# Inside the soda machine — opening

The 41.63-second opening is a 1920 × 1080, 30 fps video with Gemini narration,
animated enclosure reveals, component labels, and captions. It uses the machine
model and reveal motions from `/tour` in the current checkout.

`narration.json` contains the spoken script, Charon voice, Gemini model, and delivery
direction. `audio/narration.wav` is the recorded take. `edit.json` places pauses
and captions against that take. `composition.js` draws each frame from its time.

## Render

From the repository root, with the web and `tools/render` dependencies installed:

```sh
python3 marketing/video/tour/prepare-audio.py
node marketing/video/tour/render.mjs --stills
node marketing/video/tour/render.mjs
node marketing/video/tour/serve.mjs
```

FFmpeg encodes `out/opening.mp4`. The caption sidecars are `out/opening.vtt` and
`out/opening.srt`. Review frames and the edited narration also live in `out/`.
The browser uses the site's Montserrat fonts and brand artwork.
The preview server prints its local URL and supports seeking through the MP4.
`out/index.html` plays the video and provides the MP4 download.

## Record narration

```sh
python3 marketing/video/tour/generate-narration.py
```

The generator reads `GEMINI_API_KEY` or `~/Developer/.gemini_key`; `--key-file`,
`--voice`, and `--output` select a different local credential, voice, or output.
A new take has its own timing; `edit.json` refers to the committed recording.
