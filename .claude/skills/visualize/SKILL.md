---
name: visualize
description: Show geometry through the published model, existing native payload renders and kept enclosure changes. Use inline visualizations for timing, flow, wiring and interactive explanations.
---

# Visualize

Use a picture when it answers the current question more clearly than prose. A repository change to the site, a drawing or a guide belongs in that deliverable.

## Machine geometry

Show a part or a spot in the machine with its published model link. A link closing on `?find=` lights and labels the subject and turns the camera to it. [Part search](../../../tools/find-part.mjs) returns model links; the [geometry tools](../../../tools/hsm/README.md) measure the checkout's current payloads.

Use the existing triangles for real geometry. The native `hsm render` command and [look.sh](../../../tools/look.sh) draw payloads with the viewer's materials and lighting. Run rendering through `tools/run`. Show the resulting PNG directly when a still image answers the question. Keep comparisons at one camera and scale, and base their captions on the measured geometry. Current work stays in the shared checkout.

An enclosure change keeps its before and after in [changes/](../../../changes/README.md), using the existing snapshot and publication flow. A new concept starts in the [Rust sandbox](../../../tools/hsm/sandbox/README.md). Reuse its payload for native rendering and publish the completed part through the normal producer flow when it is ready to show on the site.

## Inline explanations

Use the host visualization workflow for timing, flow, wiring, parameter curves and screen mockups. Apply the [mobile compatibility skill](../../../tools/viz/inline-mobile/SKILL.md), including its shared theme helper for text, controls, legends and canvas or WebGL colours. Save the fragment in the current chat's visualization directory.

Keep one dominant visual and controls that help answer the question. Label measured values with units. Review the layout at mobile and desktop widths when the host workflow supports it. [shot.mjs](../../../tools/viz/shot.mjs) remains available for a requested HTML capture.
