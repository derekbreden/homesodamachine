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
it drips — never plumbed into a drain. `port("vent-tip")` is the datum the pan
catches, and the drip falls from there: the pan sits under the tip's column,
wherever the pose leaves it pointing.

The machine lays it fore and aft in the −X lane west of the SeaFlo, over the foam
cap ([`front_half.build_asse`](/hardware/manifold-layout/front_half.py),
`ASSE1022_YAW`) — a yaw about Z and a translation, since this frame is already the
cabinet's axes. The yaw turns the chain's flow onto the cabinet's −Y, its inlet aft
at the tap-water bulkhead and its 1/4" PTC collet forward onto the 1/4" LLDPE run to
the water-split; there is no roll, so the vent hangs as it is built, dropping its
column straight into the drip tray under it. `front_half.check_vent_lands` is where
that landing is made: the tray's floor, rim and the chain's underside are struck on
one set of numbers, so the drip falls exactly the gap the basin was drawn for, and a
pose that put the tip outside the coves reds the `vent-lands` gate. The pack seats the chain and
reads all three terminals off that seat, so a length changed in any of the five parts
moves the machine's ports with it.

## Model

External envelopes only, composed. Each fitting's own module states how deep its
threads run, and this file stacks those reaches along the flow axis — change a
length in any of them and the chain closes on the new one. The two female
fittings are bored at the major Ø of the male they take, so a threaded joint
shares a surface and no volume; the assembly's parts do not interfere.

`STATIONS` seats each fitting; `TERMINALS` names which of their ports are this
assembly's own, and `port(name)` reads one off its station's seat:

| terminal | station port | position | out |
|---|---|---|---|
| `port("tube-in")` | `jg-pp010822e.tube_port` | [(-36.00, 0.00, 27.00)](ASSE_TUBE_IN) | −X |
| `port("tube-out")` | `flare38-14ptc.tube_port` | [(104.00, 0.00, 27.00)](ASSE_TUBE_OUT) | +X |
| `port("vent-tip")` | `vent-stub.tip` | [(32.00, 0.00, -2.00)](ASSE_VENT_TIP) | −Z |

Overall [140.0 × 33.0 × 43.3 mm](ASSE_ENVELOPE). The vent stub's reach past the barb tip is a cut
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

## Sources
[value](NAME) texts are updated by:
- `/hardware/reference/asse1022-assembly/asse1022_assembly.py`
