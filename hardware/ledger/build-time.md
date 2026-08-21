# Build Time — One Generator Run

Seconds somebody waits for a generator to finish. The fourth ledger beside [bom.md](/hardware/ledger/bom.md) (what a unit costs in parts), [labor.md](/hardware/ledger/labor.md) (what it costs in attended minutes) and [machine-time.md](/hardware/ledger/machine-time.md) (hours a machine is occupied). Those three price one appliance. This one prices a change to this repo.

**Counted from `_cadq_export`'s import to process exit.** Every generator imports that module before it cuts anything. The interpreter's own start and CadQuery's import stand ahead of that line.

**The figure is the smallest reading in a window of [5](BT_WINDOW),** and it moves when it moves [10](BT_BAND) %. Four runs of the enclosure's canonicalization on an idle machine spread 2.6 %; the same four with six cores busy spread 14.4 %, every one of them above the idle floor.

**The readings are the measuring machine's.** [`_build_time.py`](/hardware/scripts/_build_time.py) files one per run that cut something, into an untracked window beside this file. What this file carries is the figure those readings settle on, so a checkout that has run nothing moves nothing here and a row nobody has run yet reads `—`.

## Generators

| Generator | Cuts | Seconds |
|---|---|---:|
| [`assembly/cards/_build.py`](/hardware/assembly/cards/_build.py) | every build card, and the deck they print as | [120](BT_BUILD) |
| [`assembly/scenes/render_scenes.py`](/hardware/assembly/scenes/render_scenes.py) | every card's picture, off the placed machine | [49](BT_RENDER_SCENES) |
| [`manifold-layout/enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py) | the placed machine — every body in the box | [63](BT_ENCLOSURE_ASSEMBLY) |
| [`printed-parts/enclosure/enclosure/enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py) | the box, in its printable pieces | [95](BT_ENCLOSURE) |
| [`faucet-layout/faucet_assembly.py`](/hardware/faucet-layout/faucet_assembly.py) | the faucet stack on its counter | [12](BT_FAUCET_ASSEMBLY) |
| [`manifold-layout/manifold_layout.py`](/hardware/manifold-layout/manifold_layout.py) | the fittings and the runs between them | [8.1](BT_MANIFOLD_LAYOUT) |
| [`printed-parts/cold-core/reservoir/reservoir.py`](/hardware/printed-parts/cold-core/reservoir/reservoir.py) | both flavor reservoirs and their caps | [2.8](BT_RESERVOIR) |
| [`printed-parts/cold-core/foam-assembly/foam_assembly.py`](/hardware/printed-parts/cold-core/foam-assembly/foam_assembly.py) | the foam shell and its four cap pieces | [2.8](BT_FOAM_ASSEMBLY) |
| [`printed-parts/refrigeration/fuse-clamp/fuse_clamp.py`](/hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.py) | the thermal fuse's clamp | [0.1](BT_FUSE_CLAMP) |

Sixty-two generators cut solids, and two more draw what the rest of them made — the cards and their pictures, which is why those two head the table. The rows here are hand-kept, as bom.md's are. `_build_time.py --check` names a generator whose readings come in slower than every row on this page.

## What a figure moves

A generator's seconds are its own code plus everything it imports, so a change to the shared machinery moves every row at once. `_cadq_export`'s STEP canonicalization is the largest single piece of that: it renumbers entity IDs into a content-derived order on every `.step` written, and on the enclosure assembly's 382,000 entities it is most of the run.

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_build_time.py`
