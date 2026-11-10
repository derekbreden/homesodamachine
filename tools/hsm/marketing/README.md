# Native marketing tools

`hsm-marketing` prepares display and brand artwork, edits footage and rebuilds
the saved marketing films. Run it from the repository root through
[`tools/run`](../../run). Artwork regeneration, media rendering and kitchen
illustrations run on demand, outside the normal print build.

```sh
tools/run -- hsm-marketing COMMAND --help
```

| Command | Output or purpose |
| --- | --- |
| `make-art enclosure` | Packages the display animation headers into the firmware art blob; `-o` selects its destination. |
| `make-logos` | Packages flavor portrait headers; `--store` selects the store format and `-o` names the blob. |
| `brand-assets` | Writes web, PWA, mobile and PCB brand exports from the source mark and palette; `--preview` adds the reference sheet. |
| `animation-frames` | Writes the display animation headers and browser motion review artwork. |
| `flavor-placeholders` | Draws the flavor portraits; `--preview` adds their reference sheet. |
| `sync`, `segment`, `make-subtitles` | Align external sound, propose speech scenes and generate output-timed captions. |
| `cut`, `overlays` | Assemble ranges and freezes, then apply captions, graphics and sound cues. |
| `kitchen-scene` | Renders the kitchen, faucet and cabinet illustrations from current CAD payloads. |
| `studio-stage` | Writes source frames or selected stills for *One Less Errand*. |
| `studio-render` | Runs the resumable studio picture, saved narration, sound and finishing workflow. |
| `studio-clock`, `studio-audio`, `studio-finish` | Write the picture clock, rebuild saved sound and captions, or finish existing frames into the film and player. |
| `explainer-edit`, `explainer-audio` | Rebuild the saved narration edit, timing, captions and sound for *How Carbonation Works*. |
| `explainer-assets` | Refreshes selected current CAD bundles and animation datums for the explainer when requested. |
| `film-narration` | Records or aligns an explicitly requested new performance; regular film rebuilds use the saved recording. |

The [cut and caption contract](../../../marketing/video/cuts.md) and
[overlay schema](../../../marketing/video/overlays.md) describe authored footage
inputs. Command help and the [native source](src/main.rs) own flags and defaults.
Brand, animation and flavor generators accept `--out-root DIR` for isolated exports.

```sh
tools/run -- hsm-marketing brand-assets --preview
tools/run -- hsm-marketing kitchen-scene --preview --shots kitchen faucet cabinet
tools/run -- hsm-marketing studio-stage --stills --shots hero pour
tools/run -- hsm-marketing studio-render \
  --timing marketing/video/one-less-errand/studio/pacing-review.json
```

Kitchen renders print their output directory. `--out DIR` selects one;
`--shots kitchen faucet cabinet` selects views, and `--preview` makes drafts.
`--width` and `--samples` narrow an explicit review render. The
[website instructions](../../../web/README.md#refreshing-the-illustrations)
cover final PNG-to-WebP publication.

FFmpeg supplies media decoding and encoding. Blender supplies the kitchen and
studio renderer. The native [scene descriptors](src/scene.rs),
[kitchen scene](src/kitchen.rs) and [film modules](src/film) own geometry,
materials, cameras, motion and orchestration. They launch the generic
[Blender adapter](../../render/blender_adapter.py), whose Python boundary
applies those descriptors through the application API. `--describe-only` on
the scene commands writes descriptors for inspection without starting Blender.

The explainer's browser picture renderer remains
[`render.mjs`](../../../marketing/video/how-carbonation-works/render.mjs);
its saved sound and manual CAD exports use the native commands above.
Optional narration recording and local Whisper alignment are separate manual steps.

