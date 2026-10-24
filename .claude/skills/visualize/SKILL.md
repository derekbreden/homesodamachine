---
name: visualize
description: Show it instead of describing it. Use proactively, without being asked, whenever a picture would carry the answer better than prose — options Derek chooses between, where a part sits or how it moves, what changes when a dimension or parameter changes, a sequence or timing, a display-screen mockup, measured data. Picks the surface each visual belongs on (an inline widget, a page built from the tree's own geometry and opened as an Artifact beside the conversation, the site's 3D viewer) and never hand-draws a real part.
---

# Visualize

A question about geometry, a choice between options, or a sequence is answered fastest with a
picture and a line or two of text. Derek wants these used often: reach for one without being
asked, and when in doubt, show it. Skip it when a sentence or a list already says it, when Derek
asks for a table (write a Markdown table), and when the ask is a change to a file in the tree (the
site, a drawing, a guide), which is that file's own work.

## Real geometry is never drawn by hand

A part, an assembly or a scene that exists in the tree is shown from its own triangles. A
hand-drawn outline of a real part is a claim nobody measured, and it is the picture this tree
trusts least. Hand-drawing is for what has no geometry: timing, flow, wiring, a parameter curve,
a screen layout.

## Where each visual goes

| Showing | Surface |
|---|---|
| A published part or assembly to turn around | The site viewer: `https://homesodamachine.com/3d#step:` and the path under `hardware/`, percent-encoded (`faucet-layout%2Ffaucet-assembly.step`). It draws what main published, not an edit on this disk. |
| A feature of a published part, on the part itself: where it is, lit and labelled | The same link closing on `?find=` and pick text, which the viewer's Find box runs once the part is drawn: `face:` lights the face a point lies on, `box:` exactly the surface inside a box, `view:` turns the camera to the side it is seen from, and quoted words closing any line are pinned to that pick. `link()` in `hardware/scripts/pick_text.py` composes it. |
| Options or states of real geometry, an unpublished candidate, a part among its neighbours | A page from `tools/viz/build.py`, one lettered panel per option, published and opened as an Artifact |
| A render the pipeline already made (`tools/look.sh`, `tools/render/render-step-posed.js`) | The PNG with SendUserFile `display: "render"`, or several side by side as `image` panels of a built page |
| What a slice commands: seams, speeds, the outer walls as emitted | A page from `tools/gcode/view.py` (`seams` or `speed`), published and opened as an Artifact; [its README](../../../tools/gcode/README.md) has the commands |
| Timing, flow, wiring, a what-if with a slider, a screen mockup | `show_widget`, inline; promoted to a built page and an Artifact when it should stay open, turn, or be kept |
| The before and after of an enclosure change, kept | An entry in `changes/`, drawn with `tools/changes/change.mjs`; [its README](../../../changes/README.md) has the steps, and the site shows it at `https://homesodamachine.com/changes` |

## Built pages

    python3 tools/viz/build.py --list-solids hardware/manifold-layout/enclosure-assembly.step
    python3 tools/viz/build.py SPEC.json --out <scratchpad>/viz/<name>.html
    node tools/viz/shot.mjs <scratchpad>/viz/<name>.html <scratchpad>/viz/<name>.png

The spec names the page and its panels; the docstring of `tools/viz/build.py` has the whole
format. `--step`, `--image` and `--fragment` build a page with no spec file.

    {"title": "Tee carrier states",
     "lede": "The carrier plate (amber) in the tee-carrier scenes, one camera for all of them.",
     "panels": [
       {"name": "Staged", "models": [{"step": "hardware/assembly/scenes/out/tee-carrier-staged.step",
                                      "highlight": ["carrier-plate"], "ghost": ["front-*"]}]},
       {"name": "Seated", "models": [{"step": "hardware/assembly/scenes/out/tee-carrier-seated.step",
                                      "highlight": ["carrier-plate"], "ghost": ["front-*"]}]}]}

- A panel draws the triangles the /3d viewer draws, in its colours, finishes and light: the
  payload the export wrote beside the STEP, or the STEP itself read with occt-import-js when that
  payload is stale or absent. The footer names the route each model took.
- `highlight` lights solids in the viewer's selection amber, and the page prints where they stand
  and how far their centre moved from the first panel, read off their triangles. That line is the
  caption. Type no caption the geometry does not back.
- `only` drops every other solid from the page, so nothing stands in front of what the question
  is about. `ghost` draws solids translucent and leaves them out of the framing (`enclosure-*`
  opens the whole machine), for context that has to stay in the picture.
- Every panel shares one camera, one target and one span, so a part that moved between panels is
  seen to move. `"frame": "each"` is for models that do not share a coordinate frame.
- A candidate that is in no assembly yet goes through a scene STEP: `export_assembly` from
  `hardware/scripts/_cadq_export.py` into `hardware/assembly/scenes/out/`, which is ignored, and the
  export writes the payload beside it.
- The whole enclosure is 1.08 million triangles and a 10.5 MB page. It opens, slowly on a phone.
  Narrow with `only` to what the question is about. An Artifact carries 16 MB and the builder
  refuses a page past that.
- Pages and specs go in the session scratchpad, never the tree.

## Sending it

1. Look once. `shot.mjs` captures the page at 960 px light and 390 px dark in one PNG, and
   prints every stage that did not draw, every console error and every failed request. Read the
   PNG, fix what it shows, then send.
2. Publish the page with the Artifact tool (`file_path` the page; `icon` "cube" on a first
   publish), then, in the same turn, call the Artifact tool again with `action: "open"` and the
   URL the publish returned. Published alone, the page waits behind a chip Derek has to click;
   opened, it stands in a tab beside the conversation, and the models turn. Open a page the first
   time it is shown. A republish reaches a tab that is already open by itself.
3. In the chat, a line or two: what to look at, and what is being asked of Derek.

## Inline widgets

Apply the shared [mobile compatibility skill](../../../tools/viz/inline-mobile/SKILL.md)
when creating or editing inline HTML. It supplies the common theme helper for
text, native controls, legends and canvas/WebGL colors; retain this skill's own
surface and publishing contract.

- Load `read_me` from the visualize tools with the module that fits before the first
  `show_widget` call. Its rules (680 px wide, the colour ramps, `sendPrompt`) are the widget's
  contract.
- The widget's code travels as output tokens, so keep a widget to what a person could draw by
  hand: tens of shapes, a slider or two, no embedded data. Anything larger, or anything read from
  the tree, is a built page.
- Write the fragment to the scratchpad first and pass that text, so a revision is an edit rather
  than a rewrite. `build.py --fragment <file> --title <name> --out <page>` turns it into a page to
  keep or share, drawn in the same classes.
- Options inline get one card each, and on each card a button that calls
  `sendPrompt("Build option B")`, marked ↗. It sends that text as Derek's next message.
- A widget cannot be looked at once it renders. Do the arithmetic its guide asks for (viewBox,
  text widths, overlaps) before sending, and when the layout is not simple, promote the fragment
  and run `shot.mjs` on the page first.

## Composition

- One dominant visual. No summary cards, KPI rows, legends for a single series, or controls
  nobody asked for.
- Opaque first. Hide what stands in front, or cut a section where the tool can, before drawing
  anything translucent: x-ray views and ghosts are the hardest pictures to read.
- Options are lettered A, B, C and drawn at one scale from one camera. At most one is marked as
  the pick, and the chat says why in a line.
- Values sit on the marks, with units: millimetres on the machine's axes for engineering (front is
  −Y, up is +Z); inches, pounds and PSI first on anything a buyer reads.
- The chat carries only what the picture does not: the question put to Derek, or the one number
  that decides it.
