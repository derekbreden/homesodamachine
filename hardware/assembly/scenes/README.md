# Scenes

One picture per finished sub-assembly, for the [`SA` unit cards](/hardware/assembly/cards/).
A scene is a **subset of the built machine**, posed: `enclosure-back-top` with everything bolted,
pressed and strapped to it is a real thing a person holds on the bench, and no STEP in this repo
contains exactly it.

| scene | what it shows |
|---|---|
| `back-top` | The back top piece and all 35 bodies it carries, seen in through its own open faces |
| `cap-lid-fill` | The cold core closed and poured, its lid's outer face bare |
| `cap-lid` | The same core with the pump, three valves, both chains and two runs on that face |
| `back-half` | The two back quadrants mated, through the Y-seam mouth they hand the front half |

## Which bodies

Derived. [`_scorecard.MOUNTS`](/hardware/manifold-layout/_scorecard.py) is
`(body, the part that holds it, the joint)` and is gated at every build, so a scene names only
its **roots** — the printed pieces the unit is built on — and takes everything those roots hold,
transitively. The three anchor tables say the same for what a printed rib holds. A body that
moves to another parent moves scenes with it and no list goes stale.

Two things that table cannot say are stated in [`_scenes.py`](_scenes.py): **which piece a body
bears on** when nothing fastens it (`BEARS_ON` — a slab it lands on, a wall its own nut clamps it
to), and **where the camera goes**. A body the fastening table leaves parentless and `BEARS_ON`
does not name is reported, not dropped.

**A run joins a unit by its ends** — the unit that holds both of its mouths, or the unit whose
rib closes on it. That second clause is how `fluid-14` is part of the cold core's finished state
with its far end still hanging, and how the pump's hose stubs come with the pump.

## Cost

```
tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py           # all four
tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py back-top  # one
tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py --stale   # only what moved
```

The machine is built **once** for however many scenes are asked for, then cut four ways. The
scene STEPs land in `out/`, which `.gitignore` holds — a 20 MB intermediate that churns on every
move of any body it contains is exactly the commit cost these pictures must not add. What is
committed is the PNG in [`cards/img/`](/hardware/assembly/cards/img/) and a `.scene.json` beside
it naming everything that drew it.

**Doubting a picture is cheap; drawing one is not.** So the two are split.
[`check_scenes.py`](/hardware/scripts/check_scenes.py) re-hashes the files the render wrote down
— no import, no geometry, stdlib python3, ~40 ms for all four against 71 sources — and says which
scenes have moved since they were drawn. That runs on every commit; the render runs when it says
to.
