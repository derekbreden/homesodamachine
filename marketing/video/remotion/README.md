# Channel style — Remotion foundation

The Home Soda Machine series has a house style, built as code so every episode
inherits it. This is the sibling to the footage pipeline in
[`../`](../workflow.md): that one **edits captured reality** (GoPro POV + lav
narration); this one **builds video from the engineering** — the board, the CAD,
the faucet — staged inside a designed world.

## The look

Two worlds, one system (the direction chosen from the
[channel look book](../../../marketing/video/) pitch):

- **Shop Notes** — the primary language. An engineering drawing brought to life:
  a blueprint ground, the part drawing itself on, dimension lines, leader
  callouts, a revision stamp, and one weld-glow accent. Built to *explain* — the
  thing every episode actually does.
- **Cold Press** — reserved for cold opens and hero reveals. A chilled cinematic
  void: rising carbonation, a single teal under-light, the part materialising as
  a glowing specimen.

The demo composition **`ByHand`** shows the hybrid end to end: a Cold Press cold
open cross-dissolving into the Shop Notes drawing of the board.

## Run it

```bash
npm install
npm run studio          # live editor at localhost:3000 — scrub, tweak, preview
npm run still ByHand out/frame.png --frame=300   # one frame (fast)
npm run render ByHand out/by-hand.mp4            # the whole thing
```

The render outputs to `out/` (git-ignored — regenerable). First render downloads
Remotion's headless Chromium once.

## How it's organised

```
src/
  style/
    tokens.ts     palette (Shop Notes + Cold Press), type scale, grid — the
                  single source of truth. Change the look here.
    fonts.ts      typefaces via @remotion/google-fonts (Archivo / IBM Plex Mono
                  / Caveat). Swap for licensed brand faces in one file.
    layout.ts     shared board geometry, so the board, its dimensions, and its
                  leader callouts all reference the same coordinates.
  motion/
    easings.ts    the small, fixed set of channel eases.
    draw.ts       frame-deterministic helpers: drawOn (SVG stroke draws itself
                  on via the pathLength=1 trick), fadeIn/fadeInOut, countTo.
  components/
    shop/         BlueprintGrid, BoardDrawing, DimensionLine, LeaderCallout,
                  RevisionStamp, Title, HandNote — the Shop Notes kit.
    cold/         ColdField, Bubbles — the Cold Press kit.
  scenes/         ColdOpen, ShopNotesScene — reusable scene templates.
  compositions/   ByHand — one file per episode; composes scenes + sound cues.
  sound/
    cues.ts       the sound kit, pointing at ../sfx via public/sfx (symlink).
  Root.tsx        registers compositions.
```

Every animation is a pure function of the frame — Remotion's rule, and the
reason the render is deterministic.

## Authoring a new episode

1. Add a composition in `src/compositions/`, composing the scene templates.
2. Register it in `src/Root.tsx`.
3. Reach for the shared components; when a beat needs a move the kit doesn't
   have, add the component to `components/` so the next episode gets it too. The
   system grows with the channel.

## Roadmap — bringing the real engineering in

The board here is a hand-authored stand-in ([`style/layout.ts`](src/style/layout.ts)).
The asset bridges that replace it with the real thing:

- **Board (2D)** — parse [`hardware/pcb/pcba/out/pcba.circuit.json`](../../../hardware/pcb/pcba/out/)
  and drive `BoardDrawing` from real pads/traces, in the authored routing order
  (see [`hand-routing.md`](../../../hardware/pcb/pcba/hand-routing.md)) — the
  traces draw on in the sequence they were reasoned about.
- **Board / faucet (3D)** — `@remotion/three` loading
  [`out/pcba.glb`](../../../hardware/pcb/pcba/out/) and the faucet STEP→glTF for
  exploded-assembly reveals and cross-sections. (Not yet added — v1 is 2D.)
- **Interop with footage** — a Remotion clip drops into
  [`cut.py`](../cut.py) as B-roll; `<OffthreadVideo>` embeds real footage inside
  a composition; `@remotion/captions` ingests the existing Whisper JSON.

## Notes

- SVGs inside a scene must be wrapped in `<AbsoluteFill>` — `AbsoluteFill` is a
  flexbox, and a bare `<svg>` flex-child collapses.
- `feGaussianBlur` does not render in Remotion's headless Chromium; fake glow
  with a wide, low-opacity halo stroke under a sharp core (see `ColdOpen`).
