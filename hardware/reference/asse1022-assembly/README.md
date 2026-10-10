# ASSE 1022 assembly

The Multiplex 19-0897 backflow preventer with its made-up inlet and outlet
water fittings — the water path's one non-negotiable component, plus the four
fittings that make it reachable from 1/4" tube on both sides.

```
1/4" LLDPE → PP010822E → GAGIRA coupling → [ASSE 1022] → PI4512F6S + PP061208W → 1/4" LLDPE
                                                 └ TPU sleeve → 4 mm OVER → faucet/bowl
```

That is the chain `hardware/assembly/internal-plumbing.md` step 2 builds, in the
order it builds it. Parts and prices are in `hardware/ledger/bom.md` §3.

| part | role | model |
|---|---|---|
| John Guest PP010822E | 1/4" PTC × 1/4" NPT M — the cabinet's water run pushes in here | [`../jg-pp010822e/`](../jg-pp010822e/) |
| GAGIRA reducing coupling | 3/8" NPT F × 1/4" NPT F, 316L SS — closes the 1/4"-to-3/8" gap | [`../gagira-reducing-coupling/`](../gagira-reducing-coupling/) |
| Multiplex 19-0897 | ASSE 1022 dual-check backflow preventer | [`../multiplex-asse1022/`](../multiplex-asse1022/) |
| PI4512F6S + PP061208W | 3/8" FFL swivel × 3/8" PTC carrying a 3/8"-stem × 1/4" PTC reducer — turns the ASSE outlet onto 1/4" LLDPE toward the water-split. Two fittings: no potable single-piece flare-to-1/4" adapter exists | [`../flare38-14ptc/`](../flare38-14ptc/) |

## The vent is the pose

The assembly has an orientation rather than just an envelope because the
atmospheric vent discharges through the separate 4 mm OVER circuit to its open faucet outlet over the sink bowl. [ASSE drain assembly](/hardware/assembly/asse-drain.md) specifies the direct
[TPU sleeve](/hardware/printed-parts/asse-drain-adapter/README.md) and its two
independent zip ties. The sleeve and return are placed by the appliance model.

The machine lays it fore and aft in the −X lane west of the G Ganen, on the panel
deck's own storey over the pump's casting
([`enclosure_assembly.build_asse`](/hardware/manifold-layout/enclosure_assembly.py),
`ASSE1022_YAW`) — a yaw about Z and a translation, since this frame is already the
cabinet's axes. The yaw turns the chain's flow onto the cabinet's −Y, its inlet aft
at the tap-water bulkhead and its 1/4" PTC collet forward onto the 1/4" LLDPE run to
the water-split; there is no roll, so the vent hangs as it is built, dropping its
TPU sleeve downward onto the 4 mm tube. The continuation is authored in [`_drain.py`](/hardware/manifold-layout/_drain.py) and checked against the installed appliance in [`drain-clearance-check.json`](/hardware/manifold-layout/drain-clearance-check.json).

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
| `port("vent-tip")` | `multiplex-asse1022.vent` | [(32.00, 0.00, 0.00)](ASSE_VENT_TIP) | −Z |

Overall [140.0 × 33.0 × 41.3 mm](ASSE_ENVELOPE) for the water-fitting chain.
The exposed vent tip is the actual reference barb datum, with no hose stub.
The installed TPU sleeve and the two-bend R25 return are separate appliance
members. The sleeve's printable sockets are trial fit dimensions; its expanded
installed representation is an occupancy approximation.

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
