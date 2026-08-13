# Scenes

One picture per finished sub-assembly, for the [`SA` unit cards](/hardware/assembly/cards/).
A scene is a **subset of the built machine**, posed: `enclosure-back-top` with everything bolted,
pressed and strapped to it is a real thing a person holds on the bench, and no STEP in this repo
contains exactly it.

| scene | what it shows |
|---|---|
| `back-top` | The back top piece and the 38 bodies it carries, seen in through its own open faces |
| `front-top` | The front top piece and its flavor manifold — eight valves, both pumps, two lever nuts, the display |
| `cap-lid-fill` | The top cap and its lid alone, poured, that face bare |
| `cap-lid` | The same pair with the pump, three valves, both chains and two runs on that face |
| `cold-core` | The whole core, its crown populated and a tube standing in each of its seven cap conduits |
| `back-half` | The two back quadrants mated, through the Y-seam mouth they hand the front half |
| `hopper-drain` | The basin inverted, its drain stub and clamp on the spout |

## Which bodies

Derived. [`_scorecard.MOUNTS`](/hardware/manifold-layout/_scorecard.py) is
`(body, the part that holds it, the joint)` and is gated at every build, so a scene names only
its **roots** — the printed pieces the unit is built on — and takes everything those roots hold,
transitively. The three anchor tables say the same for what a printed rib holds. A body that
moves to another parent moves scenes with it and no list goes stale.

Three things that table cannot say are stated in [`_scenes.py`](_scenes.py): **which piece a body
bears on** when nothing fastens it (`BEARS_ON` — a slab it lands on, a line it hangs off), **where
the camera goes**, and the four below. A body the fastening table leaves parentless and `BEARS_ON`
does not name is reported, not dropped.

**`parts` draws part of a root.** The cold core is one solid in the machine, and the unit a
person actually holds is its top cap and that cap's lid — they take their own foam pour, carry
everything on the crown, and meet the shell long afterwards. A scene names the sub-solids it
wants and they are carried through the root's own placement, recovered from the placed body
rather than restated.

**`flip` is the pose the unit is worked in**, not a camera trick. `enclosure-back-top` is open at
its ceiling, so on the bench it is turned over and both open faces look up. The scene is turned
with it and the camera stays a camera.

**`later` is what the piece holds and the unit has not got yet.** The drip tray rides channels
printed on `enclosure-back-top` and the funnel sits in an opening `enclosure-front-top` takes its
share of — the fastening table is right about both — and each arrives through a wall with the box
already standing ([EN-08](/hardware/assembly/cards/en-08-drip-tray.html), FS). So neither is on
its bench unit and neither is in its picture, and whatever stands on one goes with it: the
moisture plate lies in the tray. A name here the roots do not hold is reported.

**A run joins a unit by its ends** — the unit that holds both of its mouths, or the unit whose
rib closes on it. That second clause is how `fluid-14` is part of the cold core's finished state
with its far end still hanging, and how the pump's hose stubs come with the pump.

**`also` is the mirror of `later`** — what the unit carries and the tables hand to somebody else.
A length of tube is made up once, on the unit whose mouth it can reach, and leaves that bench
with its far end in the air: `fluid-18` goes into the nozzle-A union with the back top still
open, and the three reservoir lines go into the core's own cap conduits with the core still on
its own. Two mouths cannot say that — a run with one mouth in a unit is as often one the unit
*receives* — so those are named per scene. A name there the scene already derives is reported.

**The pictures are shaded solid.** The viewer ghosts an assembly by default, which is how a body
nested three deep is read through the ones over it; a unit card asks what the thing looks like
when it leaves the bench, and that answer is the silhouette — an opaque wall, and the inside seen
through the mouth the unit actually leaves open. `render-step-posed.js --solid`.

## Cost

```
tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py           # every one
tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py back-top  # one
tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py --stale   # only what moved
tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py --force   # anyway
```

The machine is built **once** for however many scenes are asked for, then cut one way each. The
scene STEPs land in `out/`, which `.gitignore` holds — a 22 MB intermediate that churns on every
move of any body it contains is exactly the commit cost these pictures must not add. What is
committed is the PNG in [`cards/img/`](/hardware/assembly/cards/img/) and a `.scene.json` beside
it naming what the picture is of — the scene, the geometry, the image, the bodies. The hash of
every file that decided it goes under `.cache/stamps/scenes/`.

Each render also writes `glb/<scene>.glb` — the artifact `/3d` opens, at a coarser tessellation
than the B-rep so the whole set comes to 9 MB rather than three times that. **That one is
committed**, the same bargain [the PCB carrier](/hardware/pcb/pcba/) already takes: the big
drawing stays out of the tree, the thing a browser opens goes in.

**Doubting a picture is cheap; drawing one is not.** So the two are split.
[`check_scenes.py`](/hardware/scripts/check_scenes.py) re-hashes the files the render stamped
— no import, no geometry, stdlib python3, a third of a second for all of them against 74 sources —
and says which scenes have moved since they were drawn. That runs on every commit; the render
runs when it says to.
