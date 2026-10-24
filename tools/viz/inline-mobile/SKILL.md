---
name: inline-mobile
description: Keep inline HTML visualizations readable on mobile and desktop when creating or editing them, including text, native controls, legends, SVG and canvas or WebGL colors. Complements the host visualization skill; does not apply to ordinary website or application styling.
---

# Mobile-compatible inline visuals

Follow the host visualization skill's output contract. This skill supplies the
color handling shared by inline fragments; it does not choose the visual's content,
layout, controls or publishing surface.

## Shared helper

Inline [assets/theme.js](assets/theme.js) inside the fragment's script, then use:

```js
const root = document.getElementById('unique-visual-root');
const theme = createInlineMobileTheme(root);
function draw() {
  const text = theme.cssColor('foreground');
  const series = theme.cssColor('viz-series-1');
  // Use these resolved colors for the existing SVG/canvas drawing.
}
theme.observe(draw);
draw();
```

Read the asset from disk when packaging the fragment. Do not fetch a local path
from inside the visualization or add another CDN dependency. Its source is usable
in either a classic script or a module.

The helper sets scoped CSS variables for text, surfaces, native controls and series
colors, preserves valid theme colors, and resets WebKit text fill. It accepts full
CSS colors and HSL/RGB channel values, rejects invisible colors, and resolves text
against the painted background. It does not paint or frame the fragment root.

`theme.cssColor(token)` returns a concrete CSS color including alpha.
`theme.rgba(token)` returns four sRGB bytes. For Three.js, convert RGB to the
renderer working space once, for example:

```js
const p = theme.rgba('viz-series-1');
const color = new THREE.Color(p[0] / 255, p[1] / 255, p[2] / 255)
  .convertSRGBToLinear();
```

Use the same resolved palette for geometry and legend swatches. Physical scene
lights retain neutral illumination; a missing UI color must not turn the lights
black. The helper does not depend on Three.js or add any renderer.

`theme.observe(draw)` refreshes the palette before calling `draw` when ancestor
theme attributes, stylesheets or the system appearance change. It returns a stop
function. If existing code already observes those events, call `theme.refresh()`
from that handler instead of adding a second observer.

## Diagnosing a mobile rendering failure

A narrow desktop viewport does not establish iOS rendering. When investigating a
reported failure, inspect the actual text fill as well as `color`, and check the
specific series that failed rather than only counting colored pixels somewhere
in the scene. Missing values, defined-but-invalid values, transparent text fill
and a monochrome first series are distinct cases. WebKit is useful reproduction
evidence; distinguish it from acceptance on the user's actual device.

This guidance adds no hook or check to commits, builds or ordinary edits. Reuse the
helper without rerunning its entire compatibility matrix for every new visual.

## Inline file location

Use the current chat's visualization directory, even when the workspace lists an
older chat's directory as writable. A path inherited from a parent/forked chat
can fail the inline reader. Keep the final fragment a regular file under the host
size limit and emit the host's visualization reference for that exact path.

Already-issued embeds retain their saved code. Regenerate and reissue an older
visualization when it needs this handling; shared instructions do not rewrite it.
