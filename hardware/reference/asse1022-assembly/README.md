# ASSE 1022 assembly

The Multiplex 19-0897 backflow preventer with everything that threads or clamps
directly onto it — the water path's one non-negotiable component, plus the four
fittings that make it reachable from 1/4" tube on both sides.

```
1/4" LLDPE → PP010822E → GAGIRA coupling → [ASSE 1022] → PI4512F6S + PP061208W → 1/4" LLDPE
                                                 └ vent stub ↓ drip pan
```

That is the chain `hardware/assembly/internal-plumbing.md` step 2 builds, in the
order it builds it. Parts and prices are in `hardware/ledger/bom.md` §3.

| part | role | model |
|---|---|---|
| John Guest PP010822E | 1/4" PTC × 1/4" NPT M — the cabinet's water run pushes in here | [`../jg-pp010822e/`](../jg-pp010822e/) |
| GAGIRA reducing coupling | 3/8" NPT F × 1/4" NPT F, 316L SS — closes the 1/4"-to-3/8" gap | [`../gagira-reducing-coupling/`](../gagira-reducing-coupling/) |
| Multiplex 19-0897 | ASSE 1022 dual-check backflow preventer | [`../multiplex-asse1022/`](../multiplex-asse1022/) |
| PI4512F6S + PP061208W | 3/8" FFL swivel × 3/8" PTC carrying a 3/8"-stem × 1/4" PTC reducer — turns the ASSE outlet onto 1/4" LLDPE toward the water-split. Two fittings: no potable single-piece flare-to-1/4" adapter exists | [`../flare38-14ptc/`](../flare38-14ptc/) |
| Sealproof clear PVC stub | 1/4" ID × 3/8" OD — the atmospheric vent's telltale run | built here |

## The vent is the pose

The assembly has an orientation rather than just an envelope because the
atmospheric vent weeps to atmosphere and the internal drip pan over the moisture
sensor has to be under it. That weeping is the mechanical telltale for a
cross-contamination event (`hardware/future.md` "Backflow vent monitoring"), and
it drips — never plumbed into a drain. `vent_tip()` is the datum the pan catches,
and the drip falls from there: the pan sits under the tip's column, wherever the
pose leaves it pointing.

The enclosure lays it along the service bay's aft strip, behind the SeaFlo and
over the foam cap (`enclosure-assembly/_contents.py` `ASSE1022_POS`,
`ASSE1022_YAW`, `ASSE1022_ROLL`) — a yaw about Z, a roll about X, and a
translation, since this frame is already the cabinet's axes. Both turns are zero
there: the chain runs the cabinet's +X with its inlet west at the tap-water
bulkhead and its 1/4" PTC collet east onto the 1/4" LLDPE run to the water-split, and the vent hangs as
it is built, dropping its column straight onto the cap the pan sits on. The
scorecard measures that fall (`fall vent-tip onto foam-assembly`). All three
terminals are carried to world coordinates from the stations below, so a length
changed in any of the five parts moves the enclosure's ports with it.

## Model

External envelopes only, composed. Each fitting's own module states how deep its
threads run, and this file stacks those reaches along the flow axis — change a
length in any of them and the chain closes on the new one. The two female
fittings are bored at the major Ø of the male they take, so a threaded joint
shares a surface and no volume; the assembly's parts do not interfere.

| terminal | position | out |
|---|---|---|
| `tube_in()` | (−36.00, 0, 27.00) | −X |
| `tube_out()` | (87.50, 0, 27.00) | +X |
| `vent_tip()` | (32.00, 0, −2.00) | −Z |

Overall 123.5 × 33.0 × 43.3 mm. The vent stub's reach past the barb tip is a cut
length, not a fixed dimension — it is trimmed at the bench, and `VENT_STUB_REACH`
holds the overhang the enclosure's placement leaves for it: the room in the
service bay's aft strip between the electronics shelf's back edge and the chain,
which is what stands the drip's fall clear of the shelf.

Frame: the Multiplex's own — **+X = flow**, its inlet at X = 0, vent along −Z.
The upstream fittings therefore sit at negative X.

## Regenerate

Builds its parts from their modules in-process, so only this one command:

```
tools/cad-venv/bin/python hardware/reference/asse1022-assembly/asse1022_assembly.py
```
