# Supco BPV31 Bullet piercing valve — reference solid

The sealed loop's one permanent service port ([`hardware/ledger/bom.md`](/hardware/ledger/bom.md)
§5). A saddle clamp bands the compressor's process tube and drives a needle through its
wall; the whole procedure it serves is [`assembly/refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md)
— vent at step 2, argon from step 3, vacuum at step 6, charge at step 7, then closed and
capped. It stays on for the life of the appliance.

`supco-bpv31.step` is a generated stand-in. The envelope is the catalogue's, not a
manufacturing drawing: **1-3/4"** height (Grainger, Global Industrial), a **1-1/8" × 7/8"**
saddle (Global Industrial), and a 1/4" male SAE flare port with its cap.

## Geometry

| | mm |
|---|---|
| Valve height off the tube | **44.45** (1-3/4") |
| Saddle, along the tube × across × round | **28.58 × 22.23 × 22.23** |
| Valve column | **Ø15.88** |
| Flare port | **Ø12.7**, reaching **25.4** off the valve's axis at z **31.75** |
| **Clearance the valve needs** | **50.8** (2") |

The needle, the two clamp screws and the gasket are inside the envelope and are not drawn.

## The clearance is the point

Supco: *requires only 2" clearance for installation and operation*. `SERVICE_CLEAR` is that
figure, measured out of the tube along the valve's own axis. The body spends 44.45 of it
standing up and the remaining 6.35 is the allen key on the needle and the flare nut on the
port.

A valve that fits is not a valve you can turn, and no clash check tells the two apart.
`enclosure_assembly.check_bpv_reach` casts the column and reports it as the **`bpv-reach`**
gate.

## Frame

- **X** = the tube's own axis, the line the saddle bands round.
- **Z** = the valve's own axis, out of the tube: the needle's direction, the body's, and
  the one `SERVICE_CLEAR` is measured along. **Z = 0 is the tube's axis**, so the saddle
  hangs half its depth below the origin and a placement seats the part on the line it
  pierces.
- **Y** carries the flare port. Supco's *non-positional mounting* means the valve is rolled
  about the tube to aim it.

| station | what |
|---|---|
| `saddle()` | the tube's axis at the clamp's mid-length — what a placement seats on |
| `flare()` | the 1/4" male SAE mouth the hose, the manifold and the argon rig land on |
| `stem()` | the needle screw's crown, the point the clearance is left above |

## Ratings

500 PSI max. Fits Ø6.35, Ø7.94 and Ø9.53 (1/4", 5/16", 3/8") line with the adapter sleeves
in the box; this appliance's process tube is the 1/4".

## Where it stands

[`compressor.process_tube()`](/hardware/reference/compressor/compressor.py) states where
the stub leaves the can and where along it the saddle bands, and
[`enclosure_assembly.build_bpv31`](/hardware/manifold-layout/enclosure_assembly.py) seats
the valve on that station.

## Regenerate

```
tools/cad-venv/bin/python hardware/reference/supco-bpv31/supco_bpv31.py
```
