# Build Time — One Generator Run

Seconds somebody waits for a generator to finish. The fourth ledger beside [bom.md](/hardware/ledger/bom.md) (what a unit costs in parts), [labor.md](/hardware/ledger/labor.md) (what it costs in attended minutes) and [machine-time.md](/hardware/ledger/machine-time.md) (hours a machine is occupied). Those three price one appliance. This one prices a change to this repo.

**Counted from `_cadq_export`'s import to process exit.** Every generator imports that module before it cuts anything. The interpreter's own start and CadQuery's import stand ahead of that line.

**The figure is the smallest reading in a window of [5](BT_WINDOW),** and it moves when it moves [10](BT_BAND) %. Four runs of the enclosure's canonicalization on an idle machine spread 2.6 %; the same four with six cores busy spread 14.4 %, every one of them above the idle floor.

**The readings are the measuring machine's.** [`_build_time.py`](/hardware/scripts/_build_time.py) files one per run that cut something, into an untracked window beside this file. What this file carries is the figure those readings settle on, so a checkout that has run nothing moves nothing here and a row nobody has run yet reads `—`.

## Generators

| Generator | Cuts | Seconds |
|---|---|---:|
| [`assembly/cards/_build.py`](/hardware/assembly/cards/_build.py) | every build card, and the deck they print as | [136](BT_BUILD) |
| [`assembly/scenes/render_scenes.py`](/hardware/assembly/scenes/render_scenes.py) | every card's picture, off the placed machine | [68](BT_RENDER_SCENES) |
| [`manifold-layout/enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py) | the placed machine — every body in the box | [84](BT_ENCLOSURE_ASSEMBLY) |
| [`printed-parts/enclosure/enclosure/enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py) | the box, in its printable pieces | [50](BT_ENCLOSURE) |
| [`faucet-layout/faucet_assembly.py`](/hardware/faucet-layout/faucet_assembly.py) | the faucet on its counter | [8.3](BT_FAUCET_ASSEMBLY) |
| [`manifold-layout/manifold_layout.py`](/hardware/manifold-layout/manifold_layout.py) | the fittings and the runs between them | [7.2](BT_MANIFOLD_LAYOUT) |
| [`printed-parts/cold-core/reservoir/reservoir.py`](/hardware/printed-parts/cold-core/reservoir/reservoir.py) | both flavor reservoirs and their caps | [2.8](BT_RESERVOIR) |
| [`printed-parts/cold-core/foam-assembly/foam_assembly.py`](/hardware/printed-parts/cold-core/foam-assembly/foam_assembly.py) | the foam shell and its four cap pieces | [1.7](BT_FOAM_ASSEMBLY) |
| [`printed-parts/refrigeration/fuse-clamp/fuse_clamp.py`](/hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.py) | the thermal fuse's clamp | [0.1](BT_FUSE_CLAMP) |

Sixty-two generators cut solids, and two more draw what the rest of them made — the cards and their pictures, which is why those two head the table. The rows here are hand-kept, as bom.md's are. `_build_time.py --check` names a generator whose readings come in slower than every row on this page.

## What rides the machine and what stands one

The enclosure assembly's row is one Bazel action, and every artifact of the appliance comes out of it: the STEP, the `.step.mesh` the viewer reads instead of parsing it, the collet plate's cut file, eleven scene GLBs, the scorecard, the facts, and sixty `check_*` called inline. The 296-solid machine is stood once and all of them read that one.

**Eleven GLBs come off it in 1.4 s.** That is what a scene costs where it rides the machine that made it. What it costs anywhere else is the row above, because an action of its own has to stand the appliance before it can pose a picture — and the same arithmetic prices every other reader here, a check included. What they read is the built machine; the machine is the expense. The box these are measured on has 8 GB, and `.bazelrc` records a full build already sitting in 3.4–4.2 GB of swap, so a second action standing the same 296 solids is a second OpenCASCADE process on it as well as a second derivation.

The seconds inside one run are not a figure this file carries, because a single reading on a shared box is not one — five sessions build this tree at once, and the spread quoted above is what that does to a number.

## What a figure moves

A generator's seconds are its own code plus everything it imports, so a change to the shared machinery moves every row at once. `_cadq_export`'s STEP canonicalization renumbers the styling records on every `.step` written — the chain a colour hangs on, which is the only part of a file OpenCASCADE seats differently between runs. On the enclosure assembly that is 2,408 records of 858,725, found by reading the file once.

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_build_time.py`
