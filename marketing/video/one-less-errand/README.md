# One Less Errand

A 100-second animated Home Soda Machine film, 1920 × 1080 at 30 fps.
One can becomes a case, a trip home, and a refrigerator shelf that empties
again. A quiet kitchen pour leads into Sculpted and Industrial faucets in
Black and White.

`story.json` holds the picture clock, narration placements, and caption phrases.
`composition.js` supplies type, brand artwork, transitions, captions, and the
poster. `errand-scenes.js` builds the opening objects and motion;
`product-scenes.js` renders the current faucet and machine assembly meshes.
Motion is deterministic and can be rendered at any timestamp.

The film uses the site's cobalt palette, Montserrat, warm neutral product
scenes, and orange accents. The faucet display and pour are illustrative CG.

## Audio

`narration.json` contains the Gemini recording direction and script.
`audio/narration.wav` is the Charon recording; `narration-words.json` contains
its 109 word timestamps. `prepare-audio.py` places its phrases on the picture
clock and writes `narration-timing.json` and the English captions.

`sound-design.py` synthesizes the original score and effects. Their timing and
levels are in `sound-manifest.json`. `mix-audio.py` ducks the score beneath the
narration and masters stereo 48 kHz audio at approximately −17 LUFS with a
−1.5 dBTP ceiling.

## Render

From the repository root, with the web and `tools/render` dependencies,
FFmpeg, and `tools/video-venv` installed:

```sh
tools/video-venv/bin/python marketing/video/one-less-errand/prepare-audio.py
tools/video-venv/bin/python marketing/video/one-less-errand/sound-design.py
tools/video-venv/bin/python marketing/video/one-less-errand/mix-audio.py
node marketing/video/one-less-errand/render.mjs
node marketing/video/one-less-errand/serve.mjs
```

The output is `out/film.mp4`, H.264 with BT.709 color and AAC audio.
`out/film.vtt` and `out/film.srt` are the caption sidecars; `out/poster.jpg`
is the player poster. The preview server prints its local URL and offers the
film, chapter navigation, and downloads.

`render.mjs --draft` writes a 720p, 15 fps review copy. `--stills --at 30,52.5,90`
renders selected frames; `--start 46 --end 63 --output detail.mp4` renders a
section. `errand-review.mjs` and `product-review.mjs` render the scene modules
independently.

## YouTube

Published as [One Less Errand — Cold Soda on Tap at Home](https://youtu.be/WHO-V2DPTcs)
on the Home Soda Machine channel, with English captions and 1080p playback.

`publication.json` holds the upload for the Home Soda Machine channel: title,
description with five chapter links, English captions, audience settings, and
the SHA-256 of the film it describes. `thumbnail.jpg` is the 3840 × 2160 custom
thumbnail, the film's mid-pour faucet on cobalt in the tour thumbnail's type and
layout. `draw(t, shot, { cobalt: true })` in `product-scenes.js` sets any shot on
the cobalt ground. Regenerate the thumbnail with:

```sh
node marketing/video/one-less-errand/render-thumbnail.mjs
```

## Record narration

The narration generator is shared with the tour film:

```sh
python3 marketing/video/tour/generate-narration.py \
  --config marketing/video/one-less-errand/narration.json \
  --output marketing/video/one-less-errand/audio/narration.wav
```

It reads `GEMINI_API_KEY` or `~/Developer/.gemini_key`. Each recording has its
own word timestamps. `check-audio.py` submits a WAV or MP3 to Gemini for an
independent audio assessment and writes the returned review to its second
argument.
