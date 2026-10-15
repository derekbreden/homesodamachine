# One Less Errand

[Watch the film on YouTube](https://youtu.be/o3l6Vcl-nLU).

A 30-second Home Soda Machine film, 1920 × 1080 at 24 fps, with English captions.
A glass of soda leads to a case in a cart, then the car, kitchen and refrigerator
shelf. The cans disappear and another trip follows. Cold soda from the Sculpted
faucet gives the next glass a different ending.

The film is a product visualization. The integrated appliance is in development.
The faucet uses current CAD; the drink imagery is illustrative. The script keeps
one connected narration performance, with an original score and synchronized
case contacts, pouring and carbonation.

## Source and rendering

[`studio/README.md`](studio/README.md) describes the picture clock, sound,
artwork provenance and resumable render workflow. The source and recording live
in [`studio/`](studio/).

From the repository root, with Blender, FFmpeg, the existing `tools/render`
Node dependencies and `tools/video-venv` installed:

```sh
tools/video-venv/bin/python marketing/video/one-less-errand/studio/render.py
node marketing/video/one-less-errand/serve.mjs --studio
```

The delivered master is `studio/out/one-less-errand-story.mp4`, with matching
`.srt` and `.vtt` captions. The player uses `studio/out/film.mp4` and offers
playback, captions and downloads.

## Publication

`publication.json` records the public upload, description, disclosure and audience
settings, English caption file and SHA-256 of the approved master. `thumbnail.jpg`
is the film’s closing composition at 1280 × 720. The homepage uses the same
composition in `web/public/landing/film-poster.webp` and opens the published film.
