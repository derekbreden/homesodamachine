# Scenes

One picture per finished sub-assembly, for the [`SA` unit cards](/hardware/assembly/cards/).
A scene is a **subset of the built machine**, posed: `enclosure-back-top` with everything bolted,
pressed and strapped to it is a real thing a person holds on the bench, and no STEP in this repo
contains exactly it.

Beside them, a **part shot** is one STEP posed — the card that names a single part, or a
sub-assembly the tree already keeps a file for. Same renderer, same sidecar, same `geometry`
digest; its subject is a file rather than a set of bodies, and it costs no appliance to draw.
`_scenes.PARTS` is that table and `img/<id>.png` is the card's own file name.

| scene | what it shows |
|---|---|
| `back-top` | The back top piece and the 38 bodies it carries, seen in through its own open faces |
| `front-top` | The front top piece and its flavor manifold — eight valves, both pumps, two lever nuts, the display |
| `cap-lid-fill` | The top cap and its lid alone, poured, that face bare |
| `cap-lid` | The same pair with the pump, three valves, both chains and one run on that face |
| `cold-core-open` | The core closed underneath and open at the top, every line standing out of the mouth, ready for its body pour |
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
the camera goes**, and the five below. A body the fastening table leaves parentless and `BEARS_ON`
does not name is reported, not dropped.

**`inner` draws a root at the depth its own model has.** Two models draw the cold core, and each
owns one thing. [`printed-parts/cold-core/foam-assembly`](/hardware/printed-parts/cold-core/foam-assembly/)
owns the six printed pieces and the port table on their faces; it is the **interface**, and both
larger models load it. [`cold-core-layout`](/hardware/cold-core-layout/) owns what stands inside
the shell — the vessel, the coil, both reservoirs, the sensing, the eight internal lines — in the
shell's own frame. [`manifold-layout`](/hardware/manifold-layout/) owns the machine, and imports
the interface as **one solid** with that port table.

So a picture of the machine wants the solid, and a picture of the core wants the inside. `inner`
names bodies from the core's model, drawn instead of the one solid `roots` puts there;
`INNER_ALL` takes every one, so no list of 63 names lives in the scene table. `one-core` gates
that the two models agree about what they share.

**The seating is the bridge between the two frames.** The core's model builds in
`foam-assembly`'s own frame, and the machine seats that body: `seat_body` hands the placement
back as `carry.where`, and the core's own solids stand under it.

**`flip` is the pose the unit is worked in**, not a camera trick. `enclosure-back-top` is open at
its ceiling, so on the bench it is turned over and both open faces look up. The scene is turned
with it and the camera stays a camera.

**`later` is what the piece holds and the unit has not got yet.** The drip tray rides channels
printed on `enclosure-back-top` and the funnel sits in an opening `enclosure-front-top` takes its
share of — the fastening table is right about both — and each arrives through a wall with the box
already standing ([EN-08](/hardware/assembly/cards/en-08-drip-tray.html), FS). So neither is on
its bench unit and neither is in its picture, and whatever stands on one goes with it: the
moisture plate lies in the tray. A name here the roots do not hold is reported.

A run can be late too. The cap's lid prints a rib for `fluid-14`, so the anchor table hands that
run to the cold core and every unit built on the core takes it — `cap-lid` among them, where the
run's far end is a valve on a piece nobody has brought. That rib leaves the bench empty, and the
run is made up when the core is plumbed.

**A run joins a unit by its ends** — the unit that holds both of its mouths, or the unit whose
rib closes on it. That second clause is how `fluid-14` is part of the cold core's finished state
with its far end still hanging, and how the pump's hose stubs come with the pump.

**`also` is the mirror of `later`** — what the unit carries and the tables hand to somebody else.
A length of tube is made up once, on the unit whose mouth it can reach, and leaves that bench
with its far end in the air: `fluid-18` goes into the nozzle-A union with the back top still
open, and the three reservoir lines go into the core's own cap conduits with the core still on
its own. Those are named per scene. A name there the scene already derives is reported.

**`without` is one unit stated as another, less a third.** `cold-core-open` is `cold-core` without
everything `cap-lid` carries — the pump, the three valves, both chains and every run between them
stand on a plate that is not down yet. It names the other scene and takes its members out, less
the roots they share, so a body that moves onto the crown leaves this picture with it.

**The pictures are shaded solid** — opaque walls, and the inside seen through the mouth the unit
leaves open. `render-step-posed.js --solid`; the viewer's own default is x-ray, which every part
draws through.

## Cost

```
tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py           # every one
tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py back-top  # one
tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py --force   # anyway
```

The machine is built **once** for however many scenes are asked for, then cut one way each. The
scene STEPs land in `out/`, which `.gitignore` holds — a 22 MB intermediate that churns on every
move of any body it contains is exactly the commit cost these pictures must not add. What is
committed is the PNG in [`cards/img/`](/hardware/assembly/cards/img/) and a `.scene.json` beside
it naming what the picture is of — the scene, the geometry, the image, the bodies.

Each render also writes `glb/<scene>.glb` — the artifact `/3d` opens, at a coarser tessellation
than the B-rep so the whole set comes to 9 MB rather than three times that. **That one is
committed**, the same bargain [the PCB carrier](/hardware/pcb/pcba/) already takes: the big
drawing stays out of the tree, the thing a browser opens goes in.

**`//:render-scenes` is what runs it.** The target names the assembly's STEP and this
directory's own modules as its inputs, so the render happens when one of those moves and not
otherwise. It carries `local` rather than running sandboxed: the renderer stands the viewer on
loopback and photographs it, and that page loads `occt-import-js` off a CDN, so drawing a scene
reaches the network for a library this tree does not carry.
