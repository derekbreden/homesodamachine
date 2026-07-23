# ASSE 1022 assembly

The Multiplex 19-0897 backflow preventer with everything that threads or clamps
directly onto it — the water path's one non-negotiable component, plus the four
fittings that make it reachable from 1/4" tube on one side and 3/8" hose on the
other.

```
1/4" LLDPE → PP010822E → GAGIRA coupling → [ASSE 1022] → FFL38BARB38 → 3/8" hose
                                                 └ vent stub ↓ drip pan
```

That is the chain `hardware/assembly/internal-plumbing.md` step 2 builds, in the
order it builds it. Parts and prices are in `hardware/ledger/bom.md` §3.

| part | role | model |
|---|---|---|
| John Guest PP010822E | 1/4" PTC × 1/4" NPT M — the cabinet's water run pushes in here | [`../jg-pp010822e/`](../jg-pp010822e/) |
| GAGIRA reducing coupling | 3/8" NPT F × 1/4" NPT F, 316L SS — closes the 1/4"-to-3/8" gap | [`../gagira-reducing-coupling/`](../gagira-reducing-coupling/) |
| Multiplex 19-0897 | ASSE 1022 dual-check backflow preventer | [`../multiplex-asse1022/`](../multiplex-asse1022/) |
| brewhardware FFL38BARB38 | 3/8" FFL swivel × 3/8" hose barb — feeds the SeaFlo suction | [`../ffl38barb38/`](../ffl38barb38/) |
| Sealproof clear PVC stub | 1/4" ID × 3/8" OD — the atmospheric vent's telltale run | built here |

## The vent is the pose

The assembly has an orientation rather than just an envelope because the
atmospheric vent must point **down**, into the internal drip pan over the
moisture sensor. The vent weeping is the mechanical telltale for a
cross-contamination event (`hardware/future.md` "Backflow vent monitoring"), and
it must drip to atmosphere — never be plumbed into a drain. Whatever places this
assembly inherits that: `vent_tip()` is the datum the pan has to catch.

## Model

External envelopes only, composed. Each fitting's own module states how deep its
threads run, and this file stacks those reaches along the flow axis — change a
length in any of them and the chain closes on the new one. The two female
fittings are bored at the major Ø of the male they take, so a threaded joint
shares a surface and no volume; the assembly's parts do not interfere.

| terminal | position | out |
|---|---|---|
| `tube_in()` | (−36.00, 0, 27.00) | −X |
| `hose_out()` | (87.50, 0, 27.00) | +X |
| `vent_tip()` | (32.00, 0, −50.00) | −Z |

Overall 123.5 × 33.0 × 91.3 mm. The vent stub's reach below the barb is a cut
length, not a fixed dimension — it is trimmed at the bench to clear whatever it
passes on the way to the pan.

Frame: the Multiplex's own — **+X = flow**, its inlet at X = 0, vent along −Z.
The upstream fittings therefore sit at negative X.

## Regenerate

Builds its parts from their modules in-process, so only this one command:

```
tools/cad-venv/bin/python hardware/reference/asse1022-assembly/asse1022_assembly.py
```
