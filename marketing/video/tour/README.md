# Inside the soda machine

The full film is 3 minutes 18 seconds at 1920 × 1080, 30 fps. It covers all
19 tour scenes with Gemini narration, animated reveals, numbered component
labels, captions, and seven chapter markers. It uses the machine model and
reveal motions from `/tour` in the current checkout.

`narration.json` contains the spoken script, Charon voice, Gemini model, and delivery
direction. `audio/narration.wav` is the recorded take. `edit.json` places pauses
and captions against that take for the 41.63-second opening.

`narration-full.json` contains the continuation's recording script and direction;
`audio/continuation.wav` is its recorded take. `film.json` holds the shots, narration,
caption phrases, and breathing room around each scene. `film-timing.json` aligns
the words to the recording. `composition.js` draws the opening, and
`film-scenes.js` draws the remaining chapters from their timestamps.

## Render

From the repository root, with the web and `tools/render` dependencies installed:

```sh
python3 marketing/video/tour/prepare-audio.py
python3 marketing/video/tour/prepare-film.py
node marketing/video/tour/render.mjs --full --stills
node marketing/video/tour/render.mjs --full
node marketing/video/tour/serve.mjs
```

FFmpeg encodes `out/film.mp4`, with chapter metadata. The caption sidecars are
`out/film.vtt` and `out/film.srt`. The opening's mastered audio is preserved exactly;
the continuation is matched to its loudness. Review frames, chapter timings, and
the edited narration also live in `out/`.
The browser uses the site's Montserrat fonts, brand artwork, and
`brand/palette.json`. Cobalt frames the model; numbered markers identify the
internal systems. The 3D viewport renders at twice its output size for
smooth enclosure flutes and edges.
The preview server prints its local URL and supports seeking through the MP4.
`out/index.html` plays the full film, provides chapter navigation, and offers the
MP4 and caption downloads. `out/film.html` opens the same player.

Omit `--full` to render `out/opening.mp4` and its player, `out/opening.html`.
`--stills --at 46.65,121.66` reviews particular timestamps without encoding a film.

## YouTube

Published as [Cold Soda on Tap — Inside a Home Soda Machine](https://youtu.be/aYyjj8i9WS8)
on the Home Soda Machine channel. The public video includes English captions
and seven timestamp links; 1080p playback is available.

`publication.json` contains the upload title, description, chapter links, and
audience settings, plus the video URL and verification record.
`thumbnail.jpg` is the 3840 × 2160 custom thumbnail, composed
from the same exploded machine model, Montserrat type, and cobalt palette as
the film. Regenerate it with:

```sh
node marketing/video/tour/render-thumbnail.mjs
```

## Record narration

```sh
python3 marketing/video/tour/generate-narration.py
python3 marketing/video/tour/generate-narration.py \
  --config marketing/video/tour/narration-full.json \
  --output marketing/video/tour/audio/continuation.wav
```

The generator reads `GEMINI_API_KEY` or `~/Developer/.gemini_key`; `--key-file`,
`--voice`, and `--output` select a different local credential, voice, or output.
A new take has its own timing; `edit.json` refers to the committed recording.
To align a new continuation, transcribe it with Whisper word timestamps into
`out/continuation.json`, then run `align-narration.py`. Review its reported word
differences and the recording before rebuilding the film.
