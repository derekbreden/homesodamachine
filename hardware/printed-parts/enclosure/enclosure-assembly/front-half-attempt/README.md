# front-half-attempt

The enclosure's contents placed against `front_half.py`, made and reverted. The tag
`front-half-attempt` carries the whole tree; these are the files that read on their own.

Nothing here builds — it sits inside a `.retired` tree, so `deps.js` never walks it.

| File | What it holds |
|---|---|
| `_contents.py` | Every body's pose against the front-half pack, and the datum each was measured from. |
| `_lines.py` | The runs authored between their ports. |
| `front_half.py` | The study: shroud and condenser mated on the floor, the manifold on their crown, the core behind, the deck on its cap. |
| `manifold_layout.py` | The manifold as it stood under that placement. |
| `enclosure-assembly.{top,front,right}.png` | The three orthographic elevations. |
| `enclosure-assembly.scorecard.json` | 49 bodies, their ports, and the seventeen rows below. |

The box is 223 wide. Its ±X walls stand off the mated compressor shroud and condenser on
the floor. Both seams are stated numbers: `y 200` splits front from back, `z 160` splits
the front columns. `pieces-fit-bed` 4/4.

The sidecar's rows:

```
coverage         pass  49/49 placed declared      placed   warn  37% (18/49)
pack-closes      pass  0 clash                    located  warn  94% (46/49)
room-holds       fail  1 short                    shaped   warn  98% (48/49)
lines-clear      pass  0 clash                    routed   warn  33% (23/70)
port-leads       fail  71/91 clear                held     warn  22% (11/49)
clearance-floor  fail  0.87 mm                    mounted  warn  12% (6/49)
deck-mounts-land fail  0/2 columns landed
pieces-fit-bed   pass  4/4 fit
seams-mate       pass  0 interfering
bend-radius      pass  0/0 corners at spec
parts-sourced    pass  49/49
```

`LIMB_PITCH` is `min(BARB_PITCH, LIMB_PITCH_CEILING)`, the ceiling struck off
`_contents.CORE_EAST_FACE` — 52.305 against a `VALVE_PITCH` of 34.25. `MIRROR_X` is 90.5,
the cold core's centreline. `condenser+fan` is a placeholder box and its `AIRFLOW` axis is
a label in `condenser_block.py`, not a geometric feature of the solid.

`hardware/topology/` at this state names a `reservoir-b-fill` and a `Y-H` that this
`manifold_layout.py` does not carry: reservoir B takes one mouth and a junction, and
segments 24/25/26 mirror 14/15/16.
