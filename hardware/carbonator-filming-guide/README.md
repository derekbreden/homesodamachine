# Carbonator weld filming guide

Thirty-three Letter pages with a separate illustrated instruction page for each
of 25 shots. The cameras record hands and work below shoulder level. Setup pages
cover the overall and detail positions, lights, settings, sound and the separate
active-process camera arrangement. Each shot gives the camera, recording time,
action, useful finished view and purpose in the edit.

Camera A is the GoPro HERO13 Black on the SmallRig CT-10 at the overall
position; camera B is the Canon EOS R50 V with its 14-30 mm kit lens on the
SmallRig CT25 at the detail position. The NEEWER NL-192AI two-light kit lights
the closeups, and the iPhone records the DJI Mic Mini. The framing sketches show composition, not actual weld
results or measured camera positions.

The PDF is published on [the drawings shelf](https://homesodamachine.com/drawings).
Its sidebar has page bookmarks, and the footer's Contents link returns to page 2.
The identical delivery copy is `output/pdf/carbonator-filming-guide.pdf`.

## Manual regeneration

```bash
tools/cad-venv/bin/python tools/carbonator-filming-guide/build.py
```

The script writes the numbered HTML leaves and vector framing sketches, renders
them through the existing Letter guide renderer, binds the PDF and writes the
cover, document sidecar and delivery receipt. Sources and final artifacts are
committed. The local `out/` directory is ignored. No hook, watcher, build target
or recurring verification invokes this script.

The [filming plan](../../marketing/video/carbonator-weld-shooting-plan.md) holds
the preparation notes. The [rotator procedure](../assembly/weld-rotation-rig.md)
and [pressure-vessel procedure](../assembly/pressure-vessel.md) govern fabrication.
